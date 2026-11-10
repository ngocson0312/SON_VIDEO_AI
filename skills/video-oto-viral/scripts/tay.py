# -*- coding: utf-8 -*-
"""Dò 2 BÀN TAY người dẫn trong clip mở đầu → toạ độ tay trái / tay phải / mặt theo GIÂY NGUỒN.

Dùng cho hiệu ứng 'manh_tay' (mẫu 3,3–4,9 s): mảnh cảnh sau căng GIỮA 2 bàn tay, to ra khi tay dang,
ngón tay đè lên mép mảnh, mặt luôn lộ.
Cách dò: tách người (u2net) ∧ màu da (YCrCb) − mặt (Haar) − cổ → 2 khối da lớn nhất = 2 tay
(chỉ 1 khối rộng = 2 tay chụm → tách đôi). Mất dấu → nội suy. Làm mượt theo thời gian.
Kết quả: work/tay/<clip>_<ss>_<dai>.json + tờ soát work/tay_<id cảnh>.jpg (chấm xanh = tay trái,
đỏ = tay phải, khung vàng = mặt, khung xanh lơ = mảnh sẽ vẽ) — Claude PHẢI mở tờ này soi."""
import os, math, subprocess, hashlib
import numpy as np, cv2
import chung as C
import nguoi as NG

DAI_NHAT = 1920     # cạnh dài khung phân tích (px) — 960 làm ngón (~6 px) quá mảnh, đầu ngón dò hụt
MT = C.MANH_TAY
NGON = ('Li', 'Lt', 'Ri', 'Rt', 'Lg', 'Rg', 'Lc', 'Rc')  # đầu ngón phía trong (ngón cái) + đầu ngón trên cùng (trỏ)
#                                               + chỗ gấp trỏ–cái (góc dưới khung chữ L) + chỗ chụm cầm dải, mỗi tay

_CASCADE = None


def _mat_dt():
    global _CASCADE
    if _CASCADE is None:
        p = os.path.join(cv2.data.haarcascades, 'haarcascade_frontalface_default.xml')
        _CASCADE = cv2.CascadeClassifier(p)
    return _CASCADE


def _vf(info, xoay):
    vf = ''
    if info.get('hdr'):
        vf = ('zscale=t=linear:npl=100,format=gbrpf32le,zscale=p=bt709,tonemap=hable:desat=0,'
              'zscale=t=bt709:m=bt709:r=tv,format=yuv420p,')
    vf += {90: 'transpose=1,', -90: 'transpose=2,', 270: 'transpose=2,', 180: 'hflip,vflip,'}.get(int(xoay or 0), '')
    return vf


def doc_khung(path, info, ss, dai, xoay=0):
    """→ (danh sách (giây nguồn, khung BGR)), cạnh dài = DAI_NHAT, đúng fps gốc."""
    w, h = info['w'], info['h']
    if int(xoay or 0) in (90, -90, 270):
        w, h = h, w
    if w >= h:
        rw, rh = DAI_NHAT, int(round(DAI_NHAT * h / w / 2) * 2)
    else:
        rw, rh = int(round(DAI_NHAT * w / h / 2) * 2), DAI_NHAT
    fps = float(info.get('fps') or 30)
    vf = _vf(info, xoay) + f'scale={rw}:{rh}:flags=area'
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-ss', f'{ss:.3f}', '-i', path, '-t', f'{dai:.3f}', '-an', '-vf', vf,
                          '-pix_fmt', 'bgr24', '-f', 'rawvideo', '-'], capture_output=True).stdout
    n = rw * rh * 3
    k = len(raw) // n
    a = np.frombuffer(raw[:k * n], np.uint8).reshape(k, rh, rw, 3)
    return [(ss + i / fps, a[i]) for i in range(k)]


def _da(fr):
    ycc = cv2.cvtColor(fr, cv2.COLOR_BGR2YCrCb)
    Y, Cr, Cb = ycc[..., 0], ycc[..., 1], ycc[..., 2]
    m = (Cr >= MT['cr'][0]) & (Cr <= MT['cr'][1]) & (Cb >= MT['cb'][0]) & (Cb <= MT['cb'][1]) & (Y >= 50)
    return m.astype(np.uint8)


def mo_rong_mau(lab, hat, bo=None, xa_px=None):
    """Bắt TRỌN bàn tay theo MÀU RIÊNG của nó (u2net hay cụt đầu ngón mảnh giơ ra ngoài người — bản 3a đầu ngón
    trỏ dò thấp hơn thật ~0,4 cỡ tay): mô hình (a, b) Lab lấy từ lõi 'hat' (khối da chắc chắn) → điểm ảnh gần màu
    (Mahalanobis < mau_nguong, đủ sáng) NỐI với hat. Nền xe đỏ / áo trắng / kính đen lệch màu xa nên không lan.
    lab: float32 ROI · hat: uint8 ROI · bo: uint8 ROI vùng cấm (mặt, cổ…). → uint8 ROI."""
    core = cv2.erode(hat, np.ones((3, 3), np.uint8))
    if core.sum() < 30:
        core = hat
    X = lab[core > 0][:, 1:3]
    if len(X) < 20:
        return hat
    mu = X.mean(0)
    Si = np.linalg.inv(np.cov(X.T) + np.eye(2) * 4)
    D = lab[..., 1:3] - mu
    md = np.einsum('...i,ij,...j->...', D, Si, D)
    # độ đậm màu tối thiểu: áo trắng ám hồng (phản chiếu xe đỏ) lọt Mahalanobis → bản 3 đầu ngón 'chụm' tụt xuống áo
    sac = np.hypot(lab[..., 1] - 128, lab[..., 2] - 128)
    sac_tay = float(np.hypot(mu[0] - 128, mu[1] - 128))
    hop = ((md < MT['mau_nguong'] ** 2) & (lab[..., 0] > 40) & (sac >= MT['mau_dam'] * sac_tay)).astype(np.uint8)
    # chỉ lan quanh khối chắc chắn (đầu ngón hụt ≤ ~0,5 cỡ tay), không lan xa
    if xa_px is not None:
        r = max(3, int(xa_px))
        hop &= cv2.dilate(hat, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * r + 1, 2 * r + 1)))
    if bo is not None:
        hop[bo > 0] = 0
    hop = cv2.morphologyEx(hop, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
    _, lb = cv2.connectedComponents(hop)
    ids = np.unique(lb[(hat > 0) & (hop > 0)])
    ids = ids[ids > 0]
    return (np.isin(lb, ids) | (hat > 0)).astype(np.uint8)


def do_1(fr, mat_cu=None, soi=None):
    """1 khung → dict(L, R, s, mat) toạ độ chuẩn hoá 0..1 (None nếu không thấy). soi: dict nhận mặt nạ trung gian (soi lỗi)."""
    H, W = fr.shape[:2]
    pm = NG.mat_na(fr)
    if pm is None:
        return None
    nguoi = cv2.dilate((pm > 0.3).astype(np.uint8), np.ones((11, 11), np.uint8))
    gray = cv2.equalizeHist(cv2.cvtColor(fr, cv2.COLOR_BGR2GRAY))
    fs = _mat_dt().detectMultiScale(gray, 1.1, 5, minSize=(int(0.03 * max(W, H)),) * 2)
    mat = None
    best = 0
    for (x, y, w, h) in fs:
        cx, cy = int(x + w / 2), int(y + h / 2)
        if nguoi[min(H - 1, cy), min(W - 1, cx)] and w * h > best:
            best = w * h; mat = [x, y, w, h]
    if mat is None and mat_cu is not None:
        mat = [mat_cu[0] * W, mat_cu[1] * H, mat_cu[2] * W, mat_cu[3] * H]
    da = _da(fr) & nguoi
    da = cv2.morphologyEx(da, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
    da = cv2.morphologyEx(da, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))
    bo = np.zeros((H, W), np.uint8)
    if mat is not None:
        x, y, w, h = [int(round(v)) for v in mat]
        # bỏ mặt (+ tóc, tai) và cổ / cổ áo hở ngay dưới cằm
        bo[max(0, y - int(0.35 * h)):y + int(1.08 * h), max(0, x - int(0.06 * w)):x + int(1.06 * w)] = 1
        # CỔ: chỉ bỏ da trong hộp cổ NỐI LIỀN với mặt. Bản 3 bỏ trắng cả hộp → 2 đầu ngón CHỤM trước ngực (nằm
        # trong hộp) bị xoá, chỗ chụm dò ra = mép hộp cách nhau ~1,1 cỡ tay → dải 'đưa từ dưới lên', không kéo từ tay
        hc = np.zeros((H, W), np.uint8)
        hc[y + h:y + int(h * (1 + MT['co'])), x + int(0.12 * w):x + int(0.88 * w)] = 1
        dk = (da & (hc | bo)).astype(np.uint8)
        _, lk = cv2.connectedComponents(dk)
        ids = np.unique(lk[(bo > 0) & (dk > 0)])
        co_da = (np.isin(lk, ids[ids > 0]) & (hc > 0)).astype(np.uint8)
        # Đầu ngón chụm hay CHẠM MŨI CHỮ V cổ áo → dính vào khối cổ. Cổ thon dần xuống mũi V rồi ngón tay nở bề ngang
        # → cắt ở HÀNG HẸP NHẤT nếu phía dưới nở rộng hẳn (≥ co_no ×); không nở = cổ thuần, bỏ hết
        yc0, yc1 = y + h, min(H, y + int(h * (1 + MT['co'])))
        rong = np.convolve(co_da[yc0:yc1].sum(1).astype(np.float64), np.ones(3) / 3, 'same')
        co_hang = np.nonzero(rong > 0)[0]
        if len(co_hang) > 3:
            r0 = co_hang[0] + int(0.1 * h)
            cand = [r for r in co_hang if r >= r0 and rong[r:].max() >= MT['co_no'] * rong[r] + 3]
            if cand:
                rc = min(cand, key=lambda r: rong[r])
                co_da[yc0 + rc:yc1] = 0
        bo |= cv2.dilate(co_da, np.ones((5, 5), np.uint8)) & hc
        da[bo > 0] = 0
        dt_mat = w * h
    else:
        dt_mat = (0.06 * H) ** 2
    n, lab, st, ce = cv2.connectedComponentsWithStats(da)
    kh = [(st[i, cv2.CC_STAT_AREA], i) for i in range(1, n) if st[i, cv2.CC_STAT_AREA] >= MT['dt_min'] * dt_mat]
    kh.sort(reverse=True)
    mat_n = [mat[0] / W, mat[1] / H, mat[2] / W, mat[3] / H] if mat is not None else None
    if not kh:
        return dict(L=None, R=None, s=None, mat=mat_n)
    def tron(ids, s):
        """Khối da (theo nhãn) → điểm ảnh bàn tay ĐỦ NGÓN (mở rộng theo màu riêng trong hộp nới mau_noi·cỡ tay)."""
        m = np.isin(lab, ids).astype(np.uint8)
        ys, xs = np.nonzero(m)
        r = int(MT['mau_noi'] * s) + 2
        x0, x1 = max(0, xs.min() - r), min(W, xs.max() + r + 1)
        y0, y1 = max(0, ys.min() - r), min(H, ys.max() + r + 1)
        roi = cv2.cvtColor(fr[y0:y1, x0:x1], cv2.COLOR_BGR2Lab).astype(np.float32)
        mm = mo_rong_mau(roi, m[y0:y1, x0:x1], bo[y0:y1, x0:x1], MT['mau_xa'] * s)
        yy, xx = np.nonzero(mm)
        return yy + y0, xx + x0

    chum = None
    if len(kh) >= 2 and kh[1][0] >= 0.25 * kh[0][0]:
        a, b = kh[0][1], kh[1][1]
        pa, pb = ce[a], ce[b]
        if pa[0] > pb[0]:
            a, b, pa, pb = b, a, pb, pa
        L, R = pa, pb
        s = math.sqrt((kh[0][0] + kh[1][0]) / 2)
        ya, xa = tron([a], s); yb, xb = tron([b], s)
        # 2 khối CHẠM SÁT (đầu ngón chạm nhau nhưng tách 1 khe da tối): chỗ chụm = cụm điểm CAO NHẤT trong số điểm của
        # tay trái cách tay phải ≤ cham·cỡ tay (thấp hơn thường là ngón cong / lòng tay chạm nhau)
        gx0, gy0 = min(xa.min(), xb.min()) - 2, min(ya.min(), yb.min()) - 2
        mb = np.ones((max(ya.max(), yb.max()) - gy0 + 3, max(xa.max(), xb.max()) - gx0 + 3), np.uint8)
        mb[yb - gy0, xb - gx0] = 0
        kc = cv2.distanceTransform(mb, cv2.DIST_L2, 3)[ya - gy0, xa - gx0] <= MT['cham'] * s
        if kc.any():
            yy, xx = ya[kc], xa[kc]
            tren = yy <= yy.min() + 0.15 * s
            chum = [float(xx[tren].mean() + 0.5 * MT['cham'] * s) / W, float(yy[tren].mean()) / H]
    else:
        a = kh[0][1]
        x0, w0 = st[a, cv2.CC_STAT_LEFT], st[a, cv2.CC_STAT_WIDTH]
        if mat is None or w0 < MT['chum_rong'] * mat[2]:
            return dict(L=None, R=None, s=None, mat=mat_n)
        ys, xs = np.nonzero(lab == a)
        # đường chia 2 tay = cột MẢNH NHẤT (chỗ 2 đầu ngón chạm) giữa 25–75 % bề ngang khối — trung vị lệch về tay
        # to hơn (bản 3a chỗ chụm rơi lên giữa ngón trỏ tay trái)
        xs0 = xs.min()
        day_cot = np.convolve(np.bincount(xs - xs0).astype(np.float64), np.ones(5) / 5, 'same')
        c0, c1 = [int(round(q)) - xs0 for q in np.percentile(xs, (25, 75))]
        xm = float(xs0 + c0 + int(np.argmin(day_cot[c0:c1 + 1]))) if c1 > c0 else float(np.median(xs))
        L = np.array([xs[xs < xm].mean(), ys[xs < xm].mean()]); R = np.array([xs[xs >= xm].mean(), ys[xs >= xm].mean()])
        s = math.sqrt(kh[0][0] / 2)
        ys, xs = tron([a], s)
        ya, xa = ys[xs < xm], xs[xs < xm]; yb, xb = ys[xs >= xm], xs[xs >= xm]
        # 2 tay CHỤM (dính 1 khối): chỗ chụm = cụm điểm ảnh cao nhất sát đường chia — KHÔNG lấy mép trong của nửa khối
        # (cột sát đường chia gồm cả lòng bàn tay bên dưới → bản 3 điểm chụm tụt xuống, dải 'đưa từ dưới lên')
        cot = np.abs(xs - xm) <= max(2.0, MT['dau_ngon'] * s)
        if cot.any():
            yy, xx = ys[cot], xs[cot]
            tren = yy <= yy.min() + 0.35 * s
            chum = [float(xx[tren].mean()) / W, float(yy[tren].mean()) / H]
    # ĐẦU NGÓN: 'trong' = điểm sát giữa nhất (tay trái: x lớn nhất) = chỗ chụm / đầu ngón cái khi làm khung chữ L;
    # 'tren' = điểm cao nhất = đầu ngón trỏ. Lấy trung bình dải 10 % cỡ tay ở mép cho đỡ nhiễu.
    e = MT['dau_ngon'] * s

    def mep(xx, yy, vx, vy):
        p = xx * vx + yy * vy
        k = p >= p.max() - e
        return [float(xx[k].mean()) / W, float(yy[k].mean()) / H]
    ngon = dict(Li=mep(xa, ya, 1, 0), Lt=mep(xa, ya, 0, -1), Ri=mep(xb, yb, -1, 0), Rt=mep(xb, yb, 0, -1))
    # CHỖ CHỤM (đầu ngón cái + trỏ cầm dải) = điểm xa nhất theo hướng VÀO TRONG + HƠI LÊN: lúc chụm, các ngón cong
    # phía dưới mới là điểm 'trong cùng' → bản 3 dải mọc từ dưới lên thay vì kéo ra từ chỗ 2 đầu ngón chạm nhau
    cg, sg = math.cos(math.radians(MT['chum_goc'])), math.sin(math.radians(MT['chum_goc']))
    ngon['Lc'] = mep(xa, ya, cg, -sg)
    ngon['Rc'] = mep(xb, yb, -cg, -sg)
    if chum is not None:
        ngon['Lc'] = ngon['Rc'] = chum          # khoảng cách 0 → dải chưa hiện, kéo ra từ đúng chỗ chụm

    def gap(xx, yy, trong, tren, huong):
        """CHỖ GẤP ngón trỏ–ngón cái (góc khung chữ L) = khuyết lồi sâu nhất của bàn tay nằm dưới đầu ngón trỏ và
        phía ngoài đầu ngón cái. Không có (tay chụm) → điểm chiếu đầu ngón trỏ xuống ngang đầu ngón cái."""
        tr = np.array(trong) * (W, H); tp = np.array(tren) * (W, H)
        mac = np.array([tp[0], tr[1]])
        x0, y0 = xx.min() - 2, yy.min() - 2
        m = np.zeros((yy.max() - y0 + 3, xx.max() - x0 + 3), np.uint8)
        m[yy - y0, xx - x0] = 1
        cs, _ = cv2.findContours(m, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        if not cs:
            return [mac[0] / W, mac[1] / H]
        ct = max(cs, key=cv2.contourArea)
        try:
            hull = cv2.convexHull(ct, returnPoints=False)
            df = cv2.convexityDefects(ct, hull)
        except cv2.error:
            df = None
        best, bd = None, MT['gap_sau'] * s * 256
        if df is not None:
            for s0, e0, f0, dd in df[:, 0]:
                p = ct[f0, 0] + (x0, y0)
                if dd > bd and p[1] > tp[1] + 0.15 * s and (p[0] - tr[0]) * huong < 0:
                    best, bd = p, dd
        if best is None:
            return [mac[0] / W, mac[1] / H]
        return [float(best[0]) / W, float(best[1]) / H]
    if soi is not None:
        soi.update(da=da, bo=bo, ya=ya, xa=xa, yb=yb, xb=xb, hai=len(kh) >= 2 and kh[1][0] >= 0.25 * kh[0][0], kh=kh[:4])
    ngon['Lg'] = gap(xa, ya, ngon['Li'], ngon['Lt'], 1)
    ngon['Rg'] = gap(xb, yb, ngon['Ri'], ngon['Rt'], -1)
    return dict(L=[L[0] / W, L[1] / H], R=[R[0] / W, R[1] / H], s=s / max(W, H), mat=mat_n, **ngon)


def _muot(t, v, ok):
    """Nội suy chỗ mất dấu + trung vị 5 + Gauss σ=1 khung."""
    v = np.array(v, np.float64)
    if ok.sum() == 0:
        return v
    for j in range(v.shape[1]):
        v[:, j] = np.interp(t, t[ok], v[ok, j])
    if len(v) >= 5:
        p = np.pad(v, ((2, 2), (0, 0)), mode='edge')
        v = np.median(np.stack([p[i:i + len(v)] for i in range(5)]), axis=0)
    k = np.array([0.24, 0.52, 0.24])
    p = np.pad(v, ((1, 1), (0, 0)), mode='edge')
    return k[0] * p[:-2] + k[1] * p[1:-1] + k[2] * p[2:]


def do_clip(path, info, ss, dai, xoay, work):
    """Dò cả đoạn [ss, ss+dai] (giây nguồn), có bộ nhớ đệm. → dict(t=[...], L, R, s, mat, ok)."""
    tham = [MT[k] for k in ('cr', 'cb', 'co', 'dt_min', 'chum_rong', 'dau_ngon', 'mau_nguong', 'mau_noi')] + [DAI_NHAT, MT['gap_sau'], MT['mau_dam'], MT['mau_xa'], MT['chum_goc'], MT['cham'], MT['co_no'], 'v7_co']
    key = hashlib.md5(f'{os.path.abspath(path)}|{ss:.3f}|{dai:.3f}|{xoay}|{tham}'.encode('utf-8')).hexdigest()[:10]
    p = os.path.join(work, 'tay', f'{os.path.splitext(os.path.basename(path))[0]}_{key}.json')
    if os.path.exists(p):
        return C.doc_json(p)
    C.in_ra(f'  dò 2 bàn tay + đầu ngón: {os.path.basename(path)} {ss:.2f}→{ss + dai:.2f} s …')
    kh = doc_khung(path, info, ss, dai, xoay)
    ts, Ss, Ms, ok, okm = [], [], [], [], []
    D = {k: [] for k in ('L', 'R') + NGON}
    mat_cu = None
    for t, fr in kh:
        d = do_1(fr, mat_cu)
        ts.append(t)
        if d and d['mat'] is not None:
            mat_cu = d['mat']
        g = d is not None and d['L'] is not None
        ok.append(g); okm.append(d is not None and d['mat'] is not None)
        for k in D:
            D[k].append(d[k] if g else [0, 0])
        Ss.append([d['s'] if g else 0])
        Ms.append(d['mat'] if d is not None and d['mat'] is not None else [0, 0, 0, 0])
    t = np.array(ts); ok = np.array(ok); okm = np.array(okm)
    kq = dict(t=ts, ok=ok.tolist(), s=_muot(t, Ss, ok)[:, 0].tolist(),
              mat=_muot(t, Ms, okm).tolist() if okm.any() else None,
              ty_le=[kh[0][1].shape[1], kh[0][1].shape[0]] if kh else [1, 1])
    for k in D:
        kq[k] = _muot(t, D[k], ok).tolist()
    C.ghi_json(p, kq)
    C.in_ra(f'    thấy 2 tay ở {int(ok.sum())}/{len(ok)} khung')
    return kq


def tai(kq, t_nguon):
    """Toạ độ chuẩn hoá tại giây nguồn (nội suy) → dict(L, R, Li, Lt, Ri, Rt, s, mat, tc) hoặc None."""
    t = np.array(kq['t'])
    if len(t) == 0 or t_nguon < t[0] - 0.2 or t_nguon > t[-1] + 0.2:
        return None
    f = lambda arr: np.array([np.interp(t_nguon, t, np.array(arr)[:, j]) for j in range(np.array(arr).shape[1])])
    v = {k: f(kq[k]) for k in ('L', 'R') + NGON if k in kq}
    v['s'] = float(np.interp(t_nguon, t, kq['s']))
    v['mat'] = f(kq['mat']) if kq.get('mat') else None
    ok = np.array(kq['ok'], np.float64)
    # tin cậy = tỉ lệ khung thấy tay trong ±0,15 s
    w = np.abs(t - t_nguon) <= 0.15
    v['tc'] = float(ok[w].mean()) if w.any() else 0.0
    return v


# ---------------------------------------------------------------- hình mảnh giữa 2 tay
def _truc(A, B):
    v = B - A
    d = max(1e-3, float(np.hypot(*v)))
    u = v / d
    n = np.array([u[1], -u[0]])          # pháp tuyến hướng LÊN (y âm)
    if n[1] > 0:
        n = -n
    return u, n, d


def the_tay(Li, Lt, Ri, Rt, s, ban=1.0, Lg=None, Rg=None, Lc=None, Rc=None):
    """Mảnh cảnh sau GHIM VÀO ĐẦU NGÓN (px khung ra) → 4 đỉnh TL, TR, BR, BL float32.
    • Tay CHỤM / KÉO DÃN: DẢI căng đúng giữa 2 CHỖ CHỤM (Lc, Rc) — dài đúng bằng khoảng cách 2 đầu ngón (chụm sát =
      dài 0 → kéo ra từ tay). ban = 0: SỢI mảnh 'day'·cỡ tay (mẫu 2,7–3,07 s) → 1: dải bản 'soi'·khoảng cách (3,13–3,3 s).
    • Tay KHUNG CHỮ L (ngón trỏ dựng cao hơn ngón cái): 4 góc = đầu ngón trỏ (trên) + chỗ gấp trỏ–cái (dưới) mỗi tay —
      mảnh nằm đúng TRONG khung tay (mẫu 3,4–4,4 s). Chuyển mượt giữa 2 kiểu theo độ dựng của ngón trỏ.
    Mép mảnh lấn ra ngoài 'lan'·s để đầu ngón ĐÈ lên mép (ngón vẽ lại phía trên)."""
    Li, Lt, Ri, Rt = [np.asarray(p, np.float64) for p in (Li, Lt, Ri, Rt)]
    A = np.asarray(Lc, np.float64) if Lc is not None else Li
    B = np.asarray(Rc, np.float64) if Rc is not None else Ri
    # khung chữ L
    u, n, d = _truc(Li, Ri)
    a0, a1 = MT['dung_l']
    b0, b1 = MT['tach']
    dung = (float((Lt - Li) @ n) + float((Rt - Ri) @ n)) / 2 / s      # ngón trỏ dựng cao hơn đầu ngón trong (×cỡ tay)
    o = min(1.0, max(0.0, (dung - a0) / (a1 - a0)))
    o *= min(1.0, max(0.0, (d / s - b0) / (b1 - b0)))                # 2 tay còn chụm sát nhau → vẫn là dải
    o = C.ease_io(o)
    # góc dưới khung L = CHỖ GẤP ngón trỏ–ngón cái (dọc ngón trỏ xuống tới ngang ngón cái), không phải đầu ngón cái:
    # mép bên chạy dọc ngón trỏ, mép dưới dọc ngón cái như mẫu 3,7 s (bản 3a lấy đầu ngón cái → hình thang hụt vào)
    gL = np.asarray(Lg, np.float64) if Lg is not None else Li + u * float((Lt - Li) @ u)
    gR = np.asarray(Rg, np.float64) if Rg is not None else Ri + u * float((Rt - Ri) @ u)
    e = MT['lan'] * s
    F = [Lt - u * e + n * MT['lan_tren'] * s, Rt + u * e + n * MT['lan_tren'] * s,
         gR + u * e - n * MT['lan_duoi'] * s, gL - u * e - n * MT['lan_duoi'] * s]
    # dải kéo giữa 2 chỗ chụm
    us, ns, ds = _truc(A, B)
    day = MT['day'] * s
    ban = min(1.0, max(0.0, ban))
    hs = day + (max(MT['soi'] * ds, MT['soi_min'] * s) - day) * C.ease_io(ban)
    es = MT['lan'] * s * min(1.0, ds / s)            # đầu dải luồn dưới ngón, chụm sát thì gần như không lố
    S = [A + ns * hs / 2 - us * es, B + ns * hs / 2 + us * es, B - ns * hs / 2 + us * es, A - ns * hs / 2 - us * es]
    return np.array([(1 - o) * p + o * q for p, q in zip(S, F)], np.float32)


def do_keo(v, s=None):
    """Khoảng cách 2 chỗ chụm / cỡ tay (dict điểm px hoặc chuẩn hoá cùng hệ)."""
    A = np.asarray(v.get('Lc', v['Li']), np.float64); B = np.asarray(v.get('Rc', v['Ri']), np.float64)
    return float(np.hypot(*(B - A))) / (s if s is not None else v['s'])


def mat_na_che(img, nguoi, mat, vung, s, dau=True, diem=None):
    """Mặt nạ 0..1 những gì của NGƯỜI phải nằm TRƯỚC mảnh: ngón / bàn tay (da) [+ cả đầu nếu dau=True].
    Áo KHÔNG che (mảnh nằm trước áo). Mép SẮC: không nở (dilate) — bản 2 nở + nhoè 1,3 px làm dán cả nền áo trắng
    quanh ngón → viền trắng. Chỉ đóng lỗ (close) rồi nhoè 0,7 px.
    diem = dict px {L, Li, Lt, R, Ri, Rt}: chỉ giữ da nằm trong 'ống' lòng bàn tay → đầu ngón (bàn tay THẬT),
    nên da mặt / cổ sát ngón cái không bị coi là tay (mảnh nằm TRƯỚC mặt như vật cầm trên tay)."""
    H, W = img.shape[:2]
    r = int(0.6 * s) + 4
    x0, y0 = np.floor(vung.min(0)).astype(int) - r; x1, y1 = np.ceil(vung.max(0)).astype(int) + r
    x0, y0, x1, y1 = max(0, x0), max(0, y0), min(W, x1), min(H, y1)
    m = np.zeros((H, W), np.float32)
    if x1 - x0 < 4 or y1 - y0 < 4:
        return m
    roi = img[y0:y1, x0:x1]
    da = _da(roi)
    ng = nguoi[y0:y1, x0:x1] if nguoi is not None else np.ones(da.shape, np.float32)
    da = da & (ng > 0.5).astype(np.uint8)
    if diem is not None:
        ong = np.zeros(da.shape, np.uint8)
        pt = lambda p: (int(round(p[0] - x0)), int(round(p[1] - y0)))
        for h in ('L', 'R'):
            if h not in diem:
                continue
            c0 = np.asarray(diem[h], np.float64)
            cv2.circle(ong, pt(c0), int(MT['ong_long'] * s), 1, -1)
            for f in (h + 'i', h + 't'):
                if f in diem:
                    c1 = np.asarray(diem[f], np.float64)
                    dv = c1 - c0
                    c2 = c1 + dv / max(1e-3, float(np.hypot(*dv))) * MT['ong_qua'] * s     # vượt đầu ngón chút
                    cv2.line(ong, pt(c0), pt(c2), 1, max(3, int(2 * MT['ong_ngon'] * s)))
                    cv2.circle(ong, pt(c1), int(MT['ong_ngon'] * s * 1.2), 1, -1)
        da = da & ong
        # u2net cụt đầu ngón → mở rộng theo màu riêng của bàn tay, chỉ trong ống
        if da.sum() >= 30:
            da = mo_rong_mau(cv2.cvtColor(roi, cv2.COLOR_BGR2Lab).astype(np.float32), da, 1 - ong, MT['mau_xa'] * s) & ong
    da = cv2.morphologyEx(da, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))
    da = cv2.morphologyEx(da, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
    n, lab, st, _ = cv2.connectedComponentsWithStats(da)
    keep = np.zeros_like(da)
    for i in range(1, n):          # bỏ đốm da lẻ (nhiễu trên nền đỏ)
        if st[i, cv2.CC_STAT_AREA] >= 0.04 * s * s:
            keep[lab == i] = 1
    da = cv2.GaussianBlur(keep.astype(np.float32), (0, 0), 0.7)
    if mat is not None and mat[2] > 0:
        fx, fy, fw, fh = mat
        hx0, hx1 = int(fx - 0.32 * fw) - x0, int(fx + 1.32 * fw) - x0
        hy0, hy1 = int(fy - 0.75 * fh) - y0, int(fy + fh * (1 + MT['co_che'])) - y0
        hx0, hy0 = max(0, hx0), max(0, hy0)
        if hx1 > hx0 and hy1 > hy0:
            if dau:
                d2 = np.zeros_like(da)
                d2[hy0:hy1, hx0:hx1] = ng[hy0:hy1, hx0:hx1]
                da = np.maximum(da, d2)
            elif diem is None:
                # chỉ lấy BÀN TAY: bỏ da mặt / cổ (nhưng giữ khối da chạm mép hộp = ngón đưa sát mặt)
                fx0, fx1 = max(0, int(fx + 0.08 * fw) - x0), int(fx + 0.92 * fw) - x0
                da[hy0:hy1, fx0:max(fx0, fx1)] = 0
    m[y0:y1, x0:x1] = da
    return m


def to_soat(kq, path, info, xoay, ra, buoc=0.1, cot=10, rong=300, t_tu=None, t_den=None):
    """Tờ soát: khung nguồn mỗi 'buoc' giây, chấm tay + khung mặt + khung mảnh."""
    t = kq['t']
    if not t:
        return None
    kh = doc_khung(path, info, t[0], t[-1] - t[0] + 0.05, xoay)
    # cắt quanh người (hộp bao mọi tay + mặt, nới rộng) cho dễ soi
    Hh, Ww = kh[0][1].shape[:2]
    pts = np.concatenate([np.array(kq['L']), np.array(kq['R'])])
    if kq.get('mat'):
        M = np.array(kq['mat']); M = M[M[:, 2] > 0]
        if len(M):
            pts = np.concatenate([pts, M[:, :2], M[:, :2] + M[:, 2:4]])
    lo, hi = pts.min(0), pts.max(0)
    sz = max(hi[0] - lo[0], (hi[1] - lo[1]) * Hh / Ww)
    cx0 = int(max(0, (lo[0] - 0.35 * sz) * Ww)); cx1 = int(min(Ww, (hi[0] + 0.35 * sz) * Ww))
    cy0 = int(max(0, lo[1] * Hh - 0.35 * sz * Ww)); cy1 = int(min(Hh, hi[1] * Hh + 0.6 * sz * Ww))
    o = []
    nx = t[0]
    for tt, fr in kh:
        if tt + 1e-6 < nx or (t_tu is not None and tt < t_tu - 1e-6) or (t_den is not None and tt > t_den + 1e-6):
            continue
        nx = max(nx, tt) + buoc - 1e-3
        f = fr.copy(); H, W = f.shape[:2]
        v = tai(kq, tt)
        if v:
            px = lambda p: np.asarray(p) * [W, H]
            sp = v['s'] * max(W, H)
            mat = v['mat']
            mp = mat * [W, H, W, H] if mat is not None and mat[2] > 0 else None
            if mp is not None:
                cv2.rectangle(f, (int(mp[0]), int(mp[1])), (int(mp[0] + mp[2]), int(mp[1] + mp[3])), (0, 220, 255), 1)
            if 'Li' in v:
                q = {k: (px(v[k]) if k in v else None) for k in ('Lg', 'Rg', 'Lc', 'Rc')}
                P = the_tay(px(v['Li']), px(v['Lt']), px(v['Ri']), px(v['Rt']), sp, 1.0, q['Lg'], q['Rg'], q['Lc'], q['Rc'])
                cv2.polylines(f, [P.astype(np.int32)], True, (255, 255, 0), 1, cv2.LINE_AA)
                for k, col in (('Li', (0, 255, 0)), ('Lt', (0, 160, 0)), ('Ri', (0, 0, 255)), ('Rt', (0, 0, 160)),
                               ('Lg', (255, 0, 255)), ('Rg', (255, 0, 255)), ('Lc', (0, 255, 255)), ('Rc', (0, 255, 255))):
                    if k in v:
                        q = px(v[k]); cv2.circle(f, (int(q[0]), int(q[1])), 4, col, -1)
        f = np.ascontiguousarray(f[cy0:cy1, cx0:cx1])
        sc = float(rong) / max(1, f.shape[1])
        f = cv2.resize(f, (rong, int(round(f.shape[0] * sc))), interpolation=cv2.INTER_AREA)
        nhan = f'{tt:.2f}s' + (f' tin {v["tc"]:.1f}' if v else ' --')
        cv2.putText(f, nhan, (4, 18), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 3)
        cv2.putText(f, nhan, (4, 18), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)
        o.append(f)
    if not o:
        return None
    h, w = o[0].shape[:2]
    hang = (len(o) + cot - 1) // cot
    tam = np.zeros((hang * h, cot * w, 3), np.uint8)
    for i, f in enumerate(o):
        r, c = divmod(i, cot)
        tam[r * h:(r + 1) * h, c * w:(c + 1) * w] = f
    cv2.imencode('.jpg', tam, [cv2.IMWRITE_JPEG_QUALITY, 82])[1].tofile(ra)
    return ra
