# -*- coding: utf-8 -*-
"""nhip.py — dò NHỊP nhạc nền (BPM, phách, phách mạnh đầu ô nhịp, độ to theo thời gian) để TEASER mở màn cắt đúng beat
và chọn đoạn nhạc CAO TRÀO cho 20 s đầu (khách 14/11/2026: "đầu video để đoạn cao trào giật gân giữ người xem tầm 30 s").
Chỉ dùng numpy (không cần librosa). Kết quả cache theo file nhạc: <work>/nhac_nhip.json."""
import json
import subprocess
from pathlib import Path

import numpy as np

from chung import bam

SR = 22050
HOP = 512


def _doc_mono(p):
    r = subprocess.run(['ffmpeg', '-v', 'error', '-i', str(p), '-vn', '-f', 'f32le', '-ac', '1', '-ar', str(SR), '-'], capture_output=True)
    if r.returncode != 0:
        raise SystemExit(f'⛔ Không đọc được nhạc {p}')
    return np.frombuffer(r.stdout, np.float32).copy()


def _onset(x):
    n = 2048
    if len(x) < n * 4:
        return np.zeros(1), np.zeros(1)
    k = 1 + (len(x) - n) // HOP
    idx = np.arange(n)[None, :] + HOP * np.arange(k)[:, None]
    fr = x[idx] * np.hanning(n)[None, :].astype(np.float32)
    mag = np.abs(np.fft.rfft(fr, axis=1)).astype(np.float32)
    lg = np.log1p(100 * mag)
    flux = np.maximum(0, np.diff(lg, axis=0)).sum(1)
    flux = np.concatenate([[0], flux])
    flux -= np.convolve(flux, np.ones(16) / 16, mode='same')        # bỏ nền chậm
    flux = np.maximum(0, flux)
    rms = np.sqrt(np.mean(fr ** 2, axis=1) + 1e-12)
    return flux / (flux.max() or 1), 20 * np.log10(rms + 1e-9)


def phan_tich(file, work=None, bao=print):
    file = Path(file)
    st = file.stat()
    khoa = bam(str(file), st.st_size, int(st.st_mtime), 'nhip2')
    cache = Path(work) / 'nhac_nhip.json' if work else None
    if cache and cache.exists():
        d = json.loads(cache.read_text(encoding='utf-8'))
        if d.get('khoa') == khoa:
            return d
    x = _doc_mono(file)
    nz = np.where(np.abs(x) > 10 ** (-50 / 20))[0]          # giống am_thanh.chuan_bi_nhac: bỏ lặng đầu → giờ nhạc tính từ đây
    lech = nz[0] / SR if len(nz) else 0.0
    x = x[nz[0]:nz[-1] + 1] if len(nz) else x
    on, db = _onset(x)
    fps = SR / HOP
    # ---- tempo: tự tương quan trên 60–180 BPM, ưu tiên quanh 120 ----
    o = on - on.mean()
    ac = np.correlate(o, o, mode='full')[len(o) - 1:]
    best, bpm = -1e9, 120.0
    for b in np.arange(60, 180.5, .5):
        lag = 60 * fps / b
        i = int(lag)
        f = lag - i
        if i + 1 >= len(ac):
            continue
        v = ac[i] * (1 - f) + ac[i + 1] * f
        v *= np.exp(-.5 * (np.log2(b / 120) / .9) ** 2)
        if v > best:
            best, bpm = v, b
    p = 60 * fps / bpm
    # ---- pha phách: lưới cố định khớp đỉnh onset nhất ----
    tg = np.arange(len(on))
    best, phi = -1, 0.0
    for ph in np.arange(0, p, .25):
        ks = np.arange(ph, len(on) - 1, p)
        v = np.interp(ks, tg, on).sum()
        if v > best:
            best, phi = v, ph
    nhip = np.arange(phi, len(on) - 1, p) / fps
    # ---- phách mạnh (đầu ô 4 phách): phách nào trong 4 có onset trung bình lớn nhất ----
    vals = np.interp(nhip * fps, tg, on)
    m4 = [vals[k::4].mean() if len(vals[k::4]) else 0 for k in range(4)]
    k0 = int(np.argmax(m4))
    o_nhip = nhip[k0::4]
    # ---- độ to theo 0,5 s ----
    b = int(fps / 2)
    nb = len(db) // b
    to = db[:nb * b].reshape(nb, b).mean(1) if nb else np.array([-60.0])
    d = {'khoa': khoa, 'file': str(file), 'lech_dau': round(float(lech), 3), 'dai': round(len(x) / SR, 3), 'bpm': round(float(bpm), 1),
         'nhip': [round(float(t), 3) for t in nhip], 'o_nhip': [round(float(t), 3) for t in o_nhip],
         'to_05': [round(float(v), 1) for v in to]}
    if cache:
        cache.write_text(json.dumps(d), encoding='utf-8')
    bao(f'  nhạc: ≈ {bpm:.0f} BPM, {len(nhip)} phách, ô nhịp {4 * 60 / bpm:.2f}s')
    return d


def chon_dau(d, dai):
    """giờ (trong nhạc đã bỏ lặng đầu) bắt đầu teaser: đầu ô nhịp mà `dai` giây sau đó TO nhất + có cú dâng (drop) ngay đầu."""
    to = np.array(d['to_05'])
    if len(to) < 4:
        return 0.0
    best, t0 = -1e9, 0.0
    for t in d['o_nhip']:
        i = int(t * 2)
        j = i + int(dai * 2)
        if j > len(to):
            break
        sau = to[i:j].mean()
        dau = to[i:i + 8].mean() - (to[max(0, i - 8):i].mean() if i >= 4 else to[i:i + 8].mean() - 3)
        v = sau + .6 * max(0.0, dau)
        if v > best:
            best, t0 = v, t
    return float(t0)


def bat_nhip(t, ds, toi_da=.35):
    """đưa giờ t về phách gần nhất trong ds (nếu lệch ≤ toi_da)."""
    if not ds:
        return t
    k = min(ds, key=lambda x: abs(x - t))
    return k if abs(k - t) <= toi_da else t
