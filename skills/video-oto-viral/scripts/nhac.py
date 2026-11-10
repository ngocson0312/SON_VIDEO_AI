# -*- coding: utf-8 -*-
"""Phân tích nhạc: BPM, lưới phách, phách mạnh (đầu nhịp), DROP (bass vào mạnh nhất), đề xuất đoạn cắt
để drop rơi đúng nhịp 6 của khuôn (như mẫu 13,76 s). Ra nhac.json + nhac.png (phổ + lưới + drop)."""
import os, subprocess
import numpy as np, cv2
import chung as C

SRA = 22050
HOP = 256


def doc_mono(path, sr=SRA):
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', path, '-vn', '-ac', '1', '-ar', str(sr), '-f', 'f32le', '-'],
                         capture_output=True).stdout
    return np.frombuffer(raw, np.float32).copy()


def _stft(x, win=2048, hop=HOP):
    n = 1 + max(0, (len(x) - win)) // hop
    idx = np.arange(win)[None, :] + hop * np.arange(n)[:, None]
    return np.abs(np.fft.rfft(x[idx] * np.hanning(win).astype(np.float32), axis=1)), np.fft.rfftfreq(win, 1 / SRA)


def phan_tich(path, drop_tay=None):
    x = doc_mono(path)
    if len(x) < SRA * 4:
        raise RuntimeError('Nhạc quá ngắn (< 4 s)')
    S, fq = _stft(x)
    fr = SRA / HOP
    t = np.arange(S.shape[0]) / fr
    L = np.log1p(S)
    flux = np.r_[0, np.maximum(0, np.diff(L, axis=0)).sum(1)]
    o = flux - np.convolve(flux, np.ones(17) / 17, 'same'); o = np.maximum(o, 0)
    low = S[:, fq < 150].sum(1)
    lowflux = np.r_[0, np.maximum(0, np.diff(np.log1p(low)))]
    # --- tempo thô bằng tự tương quan (có điều hoà bậc 2, 4)
    ac = np.correlate(o, o, 'full')[len(o) - 1:]
    best = None
    for bpm in np.arange(70, 181, 0.25):
        lag = 60 / bpm * fr
        v = sum(np.interp(lag * k, np.arange(len(ac)), ac) / k ** 0.3 for k in (1, 2, 4))
        if best is None or v > best[0]:
            best = (v, bpm)
    bpm = best[1]
    while bpm < 80: bpm *= 2
    while bpm > 165: bpm /= 2
    # --- tinh chỉnh chu kỳ + pha trên toàn bài (bước 0,5 ms)
    oc = o + 0.5 * lowflux / (lowflux.max() + 1e-9) * o.max()
    best = None
    dur = len(x) / SRA
    for p in np.linspace(60 / bpm * 0.985, 60 / bpm * 1.015, 61):
        for ph in np.arange(0, p, 0.004):
            g = np.arange(ph, dur, p)
            v = np.interp(g * fr, np.arange(len(oc)), oc).sum()
            if best is None or v > best[0]:
                best = (v, p, ph)
    _, P, PH = best
    # tinh pha mịn
    best = None
    for ph in np.arange(PH - 0.006, PH + 0.006, 0.0005):
        g = np.arange(ph, dur, P)
        v = np.interp(g * fr, np.arange(len(oc)), oc).sum()
        if best is None or v > best[0]:
            best = (v, ph)
    PH = best[1] % P
    # khung STFT i phủ [i·hop, i·hop + 2048) → onset thật ở TÂM cửa sổ: cộng nửa cửa sổ (≈ 0,046 s). Thiếu bước này
    # lưới phách sớm hơn tiếng trống ~1,5 khung → mọi cú cắt rơi TRƯỚC trống (bản 2 VF7 10/11/2026 lệch so với mẫu).
    PH = (PH + 2048 / 2 / SRA) % P
    phach = np.arange(PH, dur - 0.05, P)
    # --- năng lượng trầm + toàn dải theo từng phách
    rms_full = np.sqrt(np.convolve(x ** 2, np.ones(HOP) / HOP, 'same')[::HOP][:len(t)] + 1e-12)
    def db_doan(env, a, b):
        i, j = int(a * fr), max(int(a * fr) + 1, int(b * fr))
        return 20 * np.log10(env[i:j].mean() + 1e-9)
    lo_b = np.array([db_doan(low, a, a + P) for a in phach])
    fu_b = np.array([db_doan(rms_full, a, a + P) for a in phach])
    # --- ứng viên drop: trầm 8 phách sau − 8 phách trước (cộng toàn dải)
    ung = []
    for i in range(8, len(phach) - 8):
        d = 0.7 * (lo_b[i:i + 8].mean() - lo_b[i - 8:i].mean()) + 0.3 * (fu_b[i:i + 8].mean() - fu_b[i - 8:i].mean())
        ung.append((float(d), i))
    ung.sort(reverse=True)
    chon = []
    for d, i in ung:
        if all(abs(i - j) >= 8 for _, j in chon):
            chon.append((d, i))
        if len(chon) >= 4:
            break
    if drop_tay is not None:
        i_drop = int(np.argmin(np.abs(phach - drop_tay)))
    elif chon:
        i_drop = chon[0][1]
    else:
        i_drop = min(len(phach) - 1, 24)
    # phách mạnh: cùng pha (mod 4) với drop
    nhip = phach[i_drop % 4::4]
    kq = dict(file=os.path.abspath(path), dur=round(dur, 3), bpm=round(60 / P, 2), phach_s=round(float(P), 5),
              nhip_s=round(float(4 * P), 5), phach=[round(float(v), 4) for v in phach], nhip=[round(float(v), 4) for v in nhip],
              drop=round(float(phach[i_drop]), 4),
              drop_ung_vien=[dict(t=round(float(phach[i]), 3), diem_db=round(d, 1)) for d, i in chon])
    return kq, (S, fq, t)


def de_xuat_doan(kq, so_nhip_truoc=C.DROP_NHIP, F=C.F_MAU):
    """Chọn giây bắt đầu trong file nhạc để drop rơi vào F + so_nhip_truoc·nhịp ở video."""
    B = kq['nhip_s']; D = kq['drop']
    n = so_nhip_truoc
    while n > 3 and D - n * B < 0.3:
        n -= 1
    bd = D - n * B - F
    Fv = F
    if bd < 0:
        Fv = F + bd; bd = 0.0
        if Fv < 0.3:
            Fv = D - n * B; bd = 0.0
    sau = 5.67 * B  # cần sau drop: 2 nhịp + 4 nửa nhịp + 1 nhịp chữ + kết 2,67 phách
    du = kq['dur'] - D >= sau
    return dict(bat_dau=round(bd, 3), F=round(Fv, 3), so_nhip_truoc_drop=n, du_dai_sau_drop=bool(du),
                can_sau_drop=round(sau, 2), con_sau_drop=round(kq['dur'] - D, 2))


def ve(kq, spec, out, bat_dau=None, F=None):
    S, fq, t = spec
    H, W = 420, 1800
    lf = np.logspace(np.log10(30), np.log10(10000), H)
    rows = np.interp(lf, fq, np.arange(len(fq))).astype(int)
    img = 20 * np.log10(S[:, rows].T + 1e-6)
    img = np.clip((img - img.max() + 75) / 75, 0, 1)[::-1]
    img = cv2.resize(img.astype(np.float32), (W, H), interpolation=cv2.INTER_AREA)
    img = cv2.applyColorMap((img * 255).astype(np.uint8), cv2.COLORMAP_MAGMA)
    cv = np.zeros((H + 60, W, 3), np.uint8); cv[:H] = img
    dur = kq['dur']
    X = lambda s: int(s / dur * (W - 1))
    for p in kq['phach']:
        cv2.line(cv, (X(p), H), (X(p), H + 8), (150, 150, 150), 1)
    for n in kq['nhip']:
        cv2.line(cv, (X(n), H), (X(n), H + 18), (255, 255, 255), 1)
    for u in kq['drop_ung_vien']:
        cv2.line(cv, (X(u['t']), 0), (X(u['t']), H), (0, 200, 255), 1)
        cv2.putText(cv, f"{u['t']:.1f}s {u['diem_db']}dB", (X(u['t']) + 3, 16), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 220, 255), 1)
    cv2.line(cv, (X(kq['drop']), 0), (X(kq['drop']), H), (0, 0, 255), 2)
    cv2.putText(cv, 'DROP', (X(kq['drop']) + 4, 36), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
    if bat_dau is not None:
        cv2.rectangle(cv, (X(bat_dau), 2), (X(min(dur, bat_dau + 40)), H - 2), (0, 255, 0), 1)
    for s in range(0, int(dur) + 1, 5 if dur > 60 else 2):
        cv2.putText(cv, str(s), (X(s) + 2, H + 52), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 255, 0), 1)
    cv2.putText(cv, f"{kq['bpm']} BPM  nhip {kq['nhip_s']:.3f}s", (6, H + 34), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
    cv2.imwrite(out, cv)


def chay(path, work, drop_tay=None):
    kq, spec = phan_tich(path, drop_tay)
    dx = de_xuat_doan(kq)
    kq['de_xuat'] = dx
    ve(kq, spec, os.path.join(work, 'nhac.png'), dx['bat_dau'], dx['F'])
    C.ghi_json(os.path.join(work, 'nhac.json'), kq)
    C.in_ra(f"Nhạc: {os.path.basename(path)} · {kq['dur']:.1f} s · {kq['bpm']} BPM · nhịp {kq['nhip_s']:.3f} s · DROP {kq['drop']:.2f} s "
            f"(ứng viên: {', '.join(str(u['t']) for u in kq['drop_ung_vien'])})")
    C.in_ra(f"  Đề xuất: cắt nhạc từ {dx['bat_dau']:.2f} s → phách mạnh đầu ở {dx['F']:.2f} s video, drop ở nhịp {dx['so_nhip_truoc_drop']}"
            + ('' if dx['du_dai_sau_drop'] else f"  ⛔ sau drop chỉ còn {dx['con_sau_drop']} s, cần {dx['can_sau_drop']} s"))
    return kq
