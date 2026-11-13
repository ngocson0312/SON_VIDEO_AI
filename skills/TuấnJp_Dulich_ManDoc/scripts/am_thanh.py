# -*- coding: utf-8 -*-
"""am_thanh.py — trộn giọng + nhạc (né lời, dâng ở khoảng lặng) + SFX, chuẩn hoá −14 LUFS / −1 dBTP (2 lượt loudnorm)."""
import json
import re
import subprocess
from pathlib import Path

import numpy as np

from chung import LUFS, NHAC_DANG, NHAC_LUI_MAX, NHAC_MUC, NHAC_SAN, SFX_DIR, TP, run

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


def chuan_bi_nhac(m, n, n_day_du=None, bat_dau=None, khop_cuoi=True, bao=print):
    """nhạc thô → đúng n mẫu.
    - bỏ lặng đầu / cuối của file nhạc;
    - bat_dau (giây trong nhạc) nếu kế hoạch ghi rõ;
    - không thì nhạc dài hơn video ≤ NHAC_LUI_MAX s → bỏ bớt ĐẦU để nốt kết trùng cuối video (biên tập viên gọi là
      'lùi nhạc' — kết bài hát rơi đúng CTA, không bị cắt ngang); dài hơn nữa → giữ đầu, mờ dần ở cuối;
    - nhạc ngắn hơn video → lặp, nối hoà tan 1,5 s (không cắt cứng).
    → (mảng, giây fade vào, giây fade ra)"""
    x = np.abs(m).max(1)
    nz = np.where(x > 10 ** (-50 / 20))[0]
    if len(nz):
        m = m[nz[0]:nz[-1] + 1]
    nd = n_day_du or n
    f_in, f_out = .4, min(2.5, nd / SR * .1)
    if bat_dau is not None:
        b0 = int(float(bat_dau) * SR)
        m = m[b0:]
        f_in = .4 if b0 == 0 else 1.2
        bao(f'  nhạc: bắt đầu từ {float(bat_dau):.1f}s (kế hoạch)')
    elif khop_cuoi and 0 < len(m) - nd <= int(NHAC_LUI_MAX * SR):
        du = len(m) - nd
        m = m[du:]
        f_in, f_out = 1.2, .6
        bao(f'  nhạc: bỏ {du / SR:.1f}s đầu → nốt kết của nhạc trùng cuối video')
    if len(m) < n:
        xf = min(int(1.5 * SR), len(m) // 3)
        o = m.copy()
        while len(o) < n:
            r = np.linspace(0, 1, xf, dtype=np.float32)[:, None]
            o = np.concatenate([o[:-xf], o[-xf:] * (1 - r) + m[:xf] * r, m[xf:]])
        m = o
        bao(f'  nhạc ngắn hơn video → lặp, nối hoà tan 1,5s')
    return m[:n].copy(), f_in, f_out


def san_bang(m, toi_da=NHAC_SAN, giu_cuoi=4.0):
    """nâng đoạn nhạc NHỎ (intro / outro / bridge) lên gần mức đoạn chính, tối đa `toi_da` dB, mượt 3 s.
    Không nâng chỗ gần như lặng (tránh kéo ồn), không đụng `giu_cuoi` giây cuối (giữ nốt kết tự nhiên của bài)."""
    if toi_da <= 0 or len(m) < SR * 4:
        return m
    b = SR // 4
    mono = m.mean(1)
    nb = len(mono) // b
    lv = 10 * np.log10(np.mean(mono[:nb * b].reshape(nb, b) ** 2, axis=1) + 1e-12)
    chuan = np.percentile(lv, 80)
    nang = np.clip(chuan - 2 - lv, 0, toi_da)
    nang[lv < chuan - 30] = 0
    k = 12                                         # 12 khối × 0,25 s = 3 s
    nang = np.convolve(np.pad(nang, (k // 2, k - k // 2 - 1), mode='edge'), np.ones(k) / k, mode='valid')
    g = np.interp(np.arange(len(m)), np.arange(nb) * b + b / 2, nang)
    L = min(len(g), int(giu_cuoi * SR))
    g[-L:] *= np.linspace(1, 0, L)
    return m * (10 ** (g / 20))[:, None].astype(np.float32)


def tron(giong, dur, out, tu=None, nhac=None, sfx=(), nhac_muc=NHAC_MUC, nhac_dang=NHAC_DANG, bao=print,
         nhac_bat_dau=None, nhac_khop_cuoi=True, dai_video=None):
    """giong: file giọng (video/audio). tu: [{w,s,e}] để biết chỗ lặng. sfx: [{luc,file,db,dai?}].
    dai_video: độ dài video đầy đủ (bản xem trước 20 s vẫn căn nhạc theo video thật)."""
    out = Path(out)
    tmp = out.with_name('_do_tam.wav')
    try:
        (out.parent / 'tron_bao_cao.json').unlink()
    except Exception:
        pass
    n = int(round(dur * SR))
    v = doc(giong)[:n]
    v = np.pad(v, ((0, n - len(v)), (0, 0)))
    g = 10 ** ((-16.0 - _lufs_mang(v, tmp)) / 20)
    v *= g
    mix = v.copy()
    # ---- nhạc ----
    if nhac:
        m, fi, fo = chuan_bi_nhac(doc(nhac), n, int(round((dai_video or dur) * SR)), nhac_bat_dau, nhac_khop_cuoi, bao)
        m = san_bang(m)
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
        f_in, f_out = int(fi * SR), int(fo * SR)
        gain[:f_in] *= np.linspace(0, 1, f_in)
        gain[-f_out:] *= np.linspace(1, 0, f_out)
        mt = m * gain[:, None]
        mix += mt
        rel = _lufs_mang(mt, tmp) - _lufs_mang(v, tmp)
        bao(f'  nhạc nền ≈ {rel:.1f} dB dưới giọng (cả bài)')
        (out.parent / 'tron_bao_cao.json').write_text(json.dumps({'nhac': str(nhac), 'nhac_so_giong_db': round(rel, 1)}, ensure_ascii=False),
                                                     encoding='utf-8')
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

