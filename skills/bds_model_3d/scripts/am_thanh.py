# -*- coding: utf-8 -*-
"""am_thanh.py — trộn giọng + nhạc (né lời, dâng ở khoảng lặng) + SFX, chuẩn hoá −14 LUFS / −1 dBTP (2 lượt loudnorm)."""
import json
import re
import subprocess
from pathlib import Path

import numpy as np

from chung import LUFS, NHAC_DANG, NHAC_MUC, SFX_DIR, TP, run

SR = 48000


def doc(p, sr=SR):
    r = subprocess.run(['ffmpeg', '-v', 'error', '-i', str(p), '-vn', '-f', 'f32le', '-ac', '2', '-ar', str(sr), '-'], capture_output=True)
    if r.returncode != 0:
        raise SystemExit(f'⛔ Không đọc được âm thanh {p}: {r.stderr.decode("utf-8", "replace")[-400:]}')
    return np.frombuffer(r.stdout, np.float32).reshape(-1, 2).copy()


def ghi(p, a, sr=SR):
    a = np.clip(a, -1, 1).astype(np.float32)
    pr = subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'f32le', '-ac', '2', '-ar', str(sr), '-i', '-', '-c:a', 'pcm_s24le', str(p)],
                        input=a.tobytes(), capture_output=True)
    if pr.returncode != 0:
        raise SystemExit('⛔ ghi wav lỗi: ' + pr.stderr.decode('utf-8', 'replace')[-400:])


def do_lufs(p, loc=''):
    """→ dict loudnorm (input_i, input_tp, input_lra, input_thresh, target_offset)."""
    af = (loc + ',' if loc else '') + f'loudnorm=I={LUFS}:TP={TP}:LRA=11:print_format=json'
    r = run(['ffmpeg', '-hide_banner', '-nostats', '-i', p, '-af', af, '-f', 'null', '-'], capture=True)
    m = re.findall(r'\{[^{}]*"input_i"[^{}]*\}', r.stderr or '')
    if not m:
        raise SystemExit('⛔ không đo được độ to: ' + (r.stderr or '')[-300:])
    return json.loads(m[-1])


def _lufs_mang(a, tmp):
    ghi(tmp, a)
    v = float(do_lufs(tmp)['input_i'])
    return v if v > -70 else -70.0


def tron(giong, dur, out, tu=None, nhac=None, sfx=(), nhac_muc=NHAC_MUC, nhac_dang=NHAC_DANG, bao=print):
    """giong: file giọng (video/audio). tu: [{w,s,e}] để biết chỗ lặng. sfx: [{luc,file,db,dai?}]."""
    out = Path(out)
    tmp = out.with_name('_do_tam.wav')
    n = int(round(dur * SR))
    v = doc(giong)[:n]
    v = np.pad(v, ((0, n - len(v)), (0, 0)))
    g = 10 ** ((-16.0 - _lufs_mang(v, tmp)) / 20)
    v *= g
    mix = v.copy()
    # ---- nhạc ----
    if nhac:
        m = doc(nhac)
        if len(m) < n:
            rep = int(np.ceil(n / max(1, len(m))))
            m = np.concatenate([m] * rep)
        m = m[:n].copy()
        lm = _lufs_mang(m, tmp)
        m *= 10 ** ((-16.0 + nhac_muc - lm) / 20)
        env = np.zeros(n, np.float32)              # dB thêm theo thời gian
        if tu:
            ds = [(0.0, tu[0]['s'])] + [(a['e'], b['s']) for a, b in zip(tu, tu[1:])] + [(tu[-1]['e'], dur)]
            for a, b in ds:
                if b - a < 1.0:
                    continue
                a2, b2 = a + .12, b - .25      # dâng sau tiếng cuối một chút, hạ trước tiếng đầu
                if b2 - a2 < .5:
                    continue
                i0, i1 = int(a2 * SR), int(b2 * SR)
                r = int(.35 * SR)
                seg = np.full(max(0, i1 - i0), nhac_dang, np.float32)
                k = min(r, len(seg) // 2)
                if k > 0:
                    seg[:k] *= np.linspace(0, 1, k)
                    seg[-k:] *= np.linspace(1, 0, k)
                L = max(0, min(len(seg), n - i0))
                env[i0:i0 + L] = np.maximum(env[i0:i0 + L], seg[:L])
        gain = 10 ** (env / 20)
        f_in, f_out = int(.4 * SR), int(min(2.0, dur * .1) * SR)
        gain[:f_in] *= np.linspace(0, 1, f_in)
        gain[-f_out:] *= np.linspace(1, 0, f_out)
        mix += m * gain[:, None]
    # ---- SFX ----
    cache = {}
    for e in sfx:
        f = Path(e['file'])
        if not f.is_absolute():
            f = SFX_DIR / f
        if not f.exists():
            bao(f'⚠ thiếu SFX {f.name} — bỏ qua'); continue
        if f not in cache:
            s = doc(f)
            pk = float(np.abs(s).max()) or 1.0
            cache[f] = s * (10 ** (-1 / 20) / pk)
        s = cache[f] * 10 ** (float(e['db']) / 20)
        if e.get('dai'):
            L = int(float(e['dai']) * SR) + int(.12 * SR)
            s = s[:L].copy()
            k = min(len(s), int(.12 * SR))
            s[-k:] *= np.linspace(1, 0, k)[:, None]
        i0 = int(float(e['luc']) * SR)
        if i0 >= n:
            continue
        L = min(len(s), n - i0)
        mix[i0:i0 + L] += s[:L]
    # đuôi êm
    k = int(.25 * SR)
    mix[-k:] *= np.linspace(1, 0, k)[:, None]
    ghi(tmp, mix)
    # ---- 2 lượt loudnorm ----
    d = do_lufs(tmp)
    af = (f"loudnorm=I={LUFS}:TP={TP - .5}:LRA=11:measured_I={d['input_i']}:measured_TP={d['input_tp']}:measured_LRA={d['input_lra']}"
          f":measured_thresh={d['input_thresh']}:offset={d['target_offset']}:linear=true:print_format=summary,aresample={SR}")
    run(['ffmpeg', '-v', 'error', '-y', '-i', tmp, '-af', af, '-ar', str(SR), '-c:a', 'pcm_s24le', out])
    try:
        tmp.unlink()
    except Exception:
        pass
    return out


def gioi_han(vao, ra, tran_db):
    """chặn đỉnh mẫu ở tran_db (dBFS) — dùng khi mã hoá AAC làm đỉnh thật vượt −1 dBTP."""
    run(['ffmpeg', '-v', 'error', '-y', '-i', vao, '-af', f'alimiter=limit={10 ** (tran_db / 20):.4f}:attack=1:release=60:level=false',
         '-ar', str(SR), '-c:a', 'pcm_s24le', ra])
    return ra


def ghep(hinh, tieng, dur, out, bao=print):
    """ghép hình + tiếng (AAC 192k); AAC hay vọt đỉnh trên tiếng click → đo lại, hạ trần, ghép lại (≤ 3 lần)."""
    tran = TP - .8                                  # đo 12/11/2026: trần −1,8 dBFS → AAC ra ≈ −1,45 dBTP
    src = gioi_han(tieng, Path(tieng).with_name('_tieng_gh.wav'), tran)
    for lan in range(4):
        run(['ffmpeg', '-v', 'error', '-y', '-i', hinh, '-i', src, '-map', '0:v', '-map', '1:a', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k',
             '-t', f'{dur:.3f}', '-movflags', '+faststart', out])
        tp = float(do_lufs(out)['input_tp'])
        if tp <= TP or lan == 3:
            return tp
        tran -= .3 + .1 * (tp - TP)
        bao(f'  đỉnh sau AAC {tp:+.1f} dBTP → hạ trần giới hạn về {tran:.1f} dBFS, ghép lại')
        src = gioi_han(tieng, Path(tieng).with_name('_tieng_gh.wav'), tran)

