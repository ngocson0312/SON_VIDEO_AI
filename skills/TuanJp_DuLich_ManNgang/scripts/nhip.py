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


def _tinh_chinh(x, nhip, bpm, bao=print):
    """Lưới phách thô (BPM bước 0,5, khung 23 ms) TRÔI so với tiếng trống thật (Music_Bg: lệch 0 → +40 ms sau 15 phách — người dùng
    14/11/2026: "hiệu ứng chèn không khớp nhịp") → khớp lại: onset độ phân giải 6 ms, mỗi phách lấy đỉnh onset trong ±70 ms, hồi quy
    có trọng số t = a + b·k (2 vòng, vòng 2 chỉ ±40 ms) → lưới đều, đúng nhịp thật suốt bài."""
    hop, n = 128, 1024
    if len(x) < n * 8 or len(nhip) < 8:
        return nhip, bpm
    k = 1 + (len(x) - n) // hop
    on = np.zeros(k, np.float32)
    w = np.hanning(n).astype(np.float32)
    lg0 = None
    for i0 in range(0, k, 4096):                      # theo khối cho đỡ tốn RAM
        i1 = min(k, i0 + 4096)
        idx = np.arange(n)[None, :] + hop * np.arange(i0, i1)[:, None]
        lg = np.log1p(100 * np.abs(np.fft.rfft(x[idx] * w[None, :], axis=1))).astype(np.float32)
        prev = np.concatenate([lg0[None] if lg0 is not None else lg[:1], lg[:-1]])
        on[i0:i1] = np.maximum(0, lg - prev).sum(1)
        lg0 = lg[-1]
    dt = hop / SR
    t = np.asarray(nhip, np.float64)
    n_ = len(t)

    def _dinh(t, cua):
        pk, wt = np.full(n_, np.nan), np.zeros(n_)
        for j, g in enumerate(t):
            a, b = int((g - cua) / dt), int((g + cua) / dt) + 1
            if a < 0 or b >= len(on):
                continue
            seg = on[a:b]
            m = int(np.argmax(seg))
            if seg[m] > 0:
                pk[j], wt[j] = (a + m) * dt, float(seg[m])
        return pk, wt

    # nhịp bài có thể nhích dần (thu phòng / người chơi) → khớp CỤC BỘ: mỗi phách hồi quy trên ±R phách kề, trọng số = độ mạnh đỉnh × Gauss
    for cua, R in ((.08, 8), (.05, 6), (.035, 5)):
        pk, wt = _dinh(t, cua)
        ok = ~np.isnan(pk)
        if ok.sum() < 8:
            return nhip, bpm
        wv = np.sqrt(np.where(ok, wt, 0) / max(wt.max(), 1e-9))
        moi = t.copy()
        for j in range(n_):
            lo, hi = max(0, j - R), min(n_, j + R + 1)
            ks = np.arange(lo, hi)
            ks = ks[ok[lo:hi]]
            if len(ks) < 4:
                continue
            w = wv[ks] * np.exp(-.5 * ((ks - j) / (.6 * R)) ** 2)
            A = np.vstack([np.ones(len(ks)), ks - j]).T * w[:, None]
            (a0, _b), *_ = np.linalg.lstsq(A, pk[ks] * w, rcond=None)
            moi[j] = a0
        t = moi
    t = np.maximum.accumulate(t)
    pk, wt = _dinh(t, .05)
    ok = ~np.isnan(pk)
    lech = np.abs(pk[ok] - t[ok])
    bpm2 = 60.0 / float(np.median(np.diff(t)))
    bao(f'  nhạc: lưới phách bám trống thật {bpm:.1f} → {bpm2:.2f} BPM (lệch trung vị {1000 * np.median(lech):.0f} ms)')
    return t, float(round(bpm2, 2))


def _pha_o_nhip(x, nhip):
    """Pha phách mạnh (0–3). Onset TOÀN DẢI hay rơi vào phách 2 / 4 (trống snare, hi-hat) → sai pha: Music_Bg chọn đầu ô 21,44 s thay vì
    cú drop 19,55 s. Đầu ô nhịp thật = tiếng TRẦM (kick / bass) mạnh + ĐỔI HỢP ÂM → cộng 2 tiêu chí đó (chuẩn hoá)."""
    n, hop = 2048, 256
    if len(x) < n * 8 or len(nhip) < 8:
        return 0
    fq = np.fft.rfftfreq(n, 1 / SR)
    lo = fq < 150
    m = (fq > 60) & (fq < 2000)
    nn = np.round(12 * np.log2(fq[m] / 440) + 69).astype(int) % 12
    k = 1 + (len(x) - n) // hop
    fl = np.zeros(k, np.float32)
    pc = np.zeros((k, 12), np.float32)
    w = np.hanning(n).astype(np.float32)
    lg0 = None
    for i0 in range(0, k, 2048):
        i1 = min(k, i0 + 2048)
        idx = np.arange(n)[None, :] + hop * np.arange(i0, i1)[:, None]
        mag = np.abs(np.fft.rfft(x[idx] * w[None, :], axis=1)).astype(np.float32)
        lg = np.log1p(100 * mag[:, lo])
        prev = np.concatenate([lg0[None] if lg0 is not None else lg[:1], lg[:-1]])
        fl[i0:i1] = np.maximum(0, lg - prev).sum(1)
        lg0 = lg[-1]
        e = mag[:, m] ** 2
        for c in range(12):
            pc[i0:i1, c] = e[:, nn == c].sum(1)
    pc /= pc.sum(1, keepdims=True) + 1e-9
    dt = hop / SR
    P = float(np.median(np.diff(nhip)))

    def dinh(t):
        a, b = int((t - .05) / dt), int((t + .05) / dt) + 1
        return float(fl[max(0, a):min(k, b)].max()) if min(k, b) > max(0, a) else 0.0

    def tb(t0, t1):
        a, b = max(0, int(t0 / dt)), min(k, int(t1 / dt))
        return pc[a:max(a + 1, b)].mean(0)

    tram = np.array([dinh(t) for t in nhip])
    hop_am = np.array([np.abs(tb(t, t + P) - tb(t - P, t)).sum() if t > P else 0.0 for t in nhip])
    s = []
    for j in range(4):
        a, b = tram[j::4], hop_am[j::4]
        s.append((a.mean() if len(a) else 0) / (tram.mean() or 1) + (b.mean() if len(b) else 0) / (hop_am.mean() or 1))
    return int(np.argmax(s))


def _drop(x, nhip, w=2.0):
    """phách có độ to [t, t+2 s] trừ [t−2 s, t] lớn nhất (dB) → (chỉ số phách, độ nhảy). Music_Bg: 19,55 s (+7 dB, trầm 20 → 44 dB)."""
    L = len(x) / SR

    def db(a, b):
        seg = x[max(0, int(a * SR)):int(b * SR)]
        return 20 * np.log10(np.sqrt(np.mean(seg ** 2)) + 1e-9) if len(seg) else -90.0
    best, jb = -99.0, None
    for j, t in enumerate(nhip):
        if t < w or t + w > L:
            continue
        v = db(t, t + w) - db(t - w, t)
        if v > best:
            best, jb = v, j
    return jb, best


def phan_tich(file, work=None, bao=print):
    file = Path(file)
    st = file.stat()
    khoa = bam(str(file), st.st_size, int(st.st_mtime), 'nhip6')
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
    nhip, bpm = _tinh_chinh(x, nhip, bpm, bao)
    # ---- phách mạnh (đầu ô 4 phách): cú DROP (độ to nhảy mạnh nhất) luôn là đầu ô; bài không có drop rõ → trầm + đổi hợp âm ----
    jd, nhay = _drop(x, nhip)
    k0 = jd % 4 if jd is not None and nhay >= 4 else _pha_o_nhip(x, nhip)
    o_nhip = nhip[k0::4]
    # ---- độ to theo ĐÚNG 0,5 s (trước: khối 21 khung = 0,4876 s → tới giây 20 lệch 0,5 s, chon_dau đọc nhầm khối) ----
    b = SR // 2
    nb = len(x) // b
    to = 20 * np.log10(np.sqrt((x[:nb * b].reshape(nb, b) ** 2).mean(1)) + 1e-9) if nb else np.array([-60.0])
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
