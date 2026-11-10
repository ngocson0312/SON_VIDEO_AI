# -*- coding: utf-8 -*-
"""Thư viện hiệu ứng hình (numpy + OpenCV) — mọi hằng số lấy từ chung.py.
Khung = uint8 BGR (H, W, 3)."""
import math
import numpy as np, cv2
import chung as C


# ---------------------------------------------------------------- cơ bản
def cham_mau(img, m=C.MAU):
    """Look xe 'HDR': nét + rõ khối (clarity) + tương phản + bão hoà + tối góc nhẹ."""
    H, W = img.shape[:2]
    s = W / 1920.0
    f = img.astype(np.float32)
    b = cv2.GaussianBlur(f, (0, 0), m['net_sigma'] * s)
    f = cv2.addWeighted(f, 1 + m['net'], b, -m['net'], 0)                      # nét
    l = cv2.cvtColor(f, cv2.COLOR_BGR2GRAY)
    sm = cv2.resize(l, (W // 8, H // 8), interpolation=cv2.INTER_AREA)
    sm = cv2.GaussianBlur(sm, (0, 0), m['ro_sigma'] * s / 8)
    lb = cv2.resize(sm, (W, H), interpolation=cv2.INTER_LINEAR)
    d = cv2.addWeighted(l, m['ro'], lb, -m['ro'], 0)                             # rõ khối
    tp = m['tuong_phan']
    f = cv2.addWeighted(f + cv2.merge([d, d, d]), tp, f, 0, 127.5 * (1 - tp))   # tương phản
    l = cv2.cvtColor(f, cv2.COLOR_BGR2GRAY)
    f = cv2.addWeighted(f, m['bao_hoa'], cv2.merge([l, l, l]), 1 - m['bao_hoa'], 0)   # bão hoà
    if m.get('toi_goc'):
        f = cv2.multiply(f, _toi_goc(W, H, m['toi_goc']))
    np.clip(f, 0, 255, out=f)
    return f.astype(np.uint8)


_VG = {}


def _toi_goc(W, H, k):
    key = (W, H, k)
    if key not in _VG:
        y, x = np.mgrid[0:H, 0:W].astype(np.float32)
        r = np.sqrt(((x - W / 2) / (W / 2)) ** 2 + ((y - H / 2) / (H / 2)) ** 2) / math.sqrt(2)
        v = (1 - k * np.clip(r - 0.35, 0, 1) ** 1.5 / 0.65 ** 1.5).astype(np.float32)
        _VG[key] = cv2.merge([v, v, v])
    return _VG[key]


def nhoe(img, sigma):
    if sigma < 0.4:
        return img
    if sigma > 6:
        H, W = img.shape[:2]
        f = 4 if sigma > 18 else 2
        sm = cv2.resize(img, (W // f, H // f), interpolation=cv2.INTER_AREA)
        sm = cv2.GaussianBlur(sm, (0, 0), sigma / f)
        return cv2.resize(sm, (W, H), interpolation=cv2.INTER_LINEAR)
    return cv2.GaussianBlur(img, (0, 0), sigma)


def tron_trang(img, a, khu_mau=0.0):
    if a <= 0.001 and khu_mau <= 0:
        return img
    f = img.astype(np.float32)
    if khu_mau > 0:
        l = f.mean(2, keepdims=True); f = f + (l - f) * khu_mau
    f = f + (255 - f) * a
    return np.clip(f, 0, 255).astype(np.uint8)


def nhoe_huong(img, dai, goc_do):
    """Nhoè chuyển động theo hướng (độ). dai = px tổng chiều dài vệt."""
    if dai < 2:
        return img
    H, W = img.shape[:2]
    f = 2
    sm = cv2.resize(img, (W // f, H // f), interpolation=cv2.INTER_AREA).astype(np.float32)
    n = int(min(15, max(5, dai / f / 3)))
    ca, sa = math.cos(math.radians(goc_do)), math.sin(math.radians(goc_do))
    acc = np.zeros_like(sm)
    for i in range(n):
        d = (i / (n - 1) - 0.5) * dai / f
        M = np.float32([[1, 0, d * ca], [0, 1, d * sa]])
        acc += cv2.warpAffine(sm, M, (W // f, H // f), borderMode=cv2.BORDER_REFLECT)
    acc /= n
    return cv2.resize(np.clip(acc, 0, 255).astype(np.uint8), (W, H), interpolation=cv2.INTER_LINEAR)


def nhoe_ngang(img, dai):
    if dai < 2:
        return img
    k = int(dai) | 1
    return cv2.blur(img, (k, 1))


# ---------------------------------------------------------------- méo hình
_LUOI = {}


def _luoi(W, H):
    if (W, H) not in _LUOI:
        y, x = np.mgrid[0:H, 0:W].astype(np.float32)
        _LUOI[(W, H)] = (x, y)
    return _LUOI[(W, H)]


def song(img, bien, buoc, pha, xoay_do=0.0):
    """Gợn sóng lỏng (DROP 13,6 s mẫu): dịch ngang theo sin(y), dọc theo sin(x)."""
    if bien < 0.5 and abs(xoay_do) < 0.05:
        return img
    H, W = img.shape[:2]
    x, y = _luoi(W, H)
    # mẫu 13,57–13,90 s: uốn "chất lỏng" mềm, bước dài (~0,15–0,25 W), không đều như sin → sin dài + nhiễu thô
    n = _nhieu(W, H, 21, o=72)
    c, s = math.cos(pha * 0.5), math.sin(pha * 0.5)
    nx = n[0] * c + n[2] * s
    ny = n[1] * c + n[3] * s
    mx = x + bien * (0.7 * np.sin(2 * np.pi * y / buoc + pha) + 0.9 * nx)
    my = y + bien * (0.3 * np.sin(2 * np.pi * x / (buoc * 1.5) + pha * 1.4) + 0.6 * ny)
    if abs(xoay_do) > 0.05:
        a = math.radians(xoay_do); cx, cy = W / 2, H / 2
        dx, dy = mx - cx, my - cy
        mx, my = cx + dx * math.cos(a) - dy * math.sin(a), cy + dx * math.sin(a) + dy * math.cos(a)
    return cv2.remap(img, mx.astype(np.float32), my.astype(np.float32), cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)


_NHIEU = {}


def _nhieu(W, H, seed, o=24):
    """4 trường nhiễu mịn −1..1; o = cỡ ô lưới (px) — to thì nhiễu thô, uốn dài."""
    key = (W, H, seed, o)
    if key not in _NHIEU:
        rng = np.random.default_rng(seed)
        ds = []
        for _ in range(4):
            n = rng.standard_normal((H // o + 2, W // o + 2)).astype(np.float32)
            n = cv2.GaussianBlur(n, (0, 0), 2.2)
            n = cv2.resize(n, (W, H), interpolation=cv2.INTER_CUBIC)
            n /= (np.abs(n).max() + 1e-6)
            ds.append(n)
        _NHIEU[key] = ds
    return _NHIEU[key]


def khoi(img, bien, k, nhat=0.0, seed=3):
    """Tan khói (15,5–15,8 s mẫu): gợn dọc bước ngắn mạnh dần + trường nhiễu mịn + BÓNG MỜ kéo vệt (2 lớp lệch pha),
    nhạt + khử màu."""
    H, W = img.shape[:2]
    if bien >= 0.5:
        x, y = _luoi(W, H)
        n = _nhieu(W, H, seed)
        a = (k % 8) / 8.0
        nx = n[0] * (1 - a) + n[2] * a
        ny = n[1] * (1 - a) + n[3] * a
        # gợn mạnh hơn ở nửa phải (mẫu: khói cuộn từ mép phải)
        lech = (0.55 + 0.9 * np.clip(x / W - 0.25, 0, 1)).astype(np.float32)
        gx = np.sin(y / (H * 0.014) + k * 0.9) * lech
        mx = x + bien * (0.45 * nx + 0.8 * gx)
        my = y + bien * 0.45 * ny
        a1 = cv2.remap(img, mx.astype(np.float32), my.astype(np.float32), cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
        mx2 = x + bien * (0.6 * nx - 0.8 * gx) * 1.6
        my2 = y + bien * 0.8 * ny - bien * 0.6
        a2 = cv2.remap(img, mx2.astype(np.float32), my2.astype(np.float32), cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
        img = cv2.addWeighted(a1, 0.62, a2, 0.38, 0)
    if nhat > 0:
        img = tron_trang(img, nhat * 0.5, khu_mau=nhat * 2)
    return img


# ---------------------------------------------------------------- rung
def rung(k, W, bien=C.LIA['rung_bien'], tau=C.LIA['rung_tau'], seed=0):
    """Rung tắt dần sau cú cắt (đoạn dồn nhanh 18–22 s mẫu): ~1,6 % bề rộng, xen trục x / y."""
    if k >= C.LIA['rung_khung']:
        return 0.0, 0.0
    a = bien * W * math.exp(-k / tau)
    ph = seed * 1.7
    return a * math.sin(2 * math.pi * k / 3.2 + ph), 0.6 * a * math.cos(2 * math.pi * k / 2.7 + ph)


# ---------------------------------------------------------------- halftone
_HT = {}


def halftone(img, buoc_px):
    """Chấm bi kiểu truyện tranh trên mảnh vỡ: bi to ở chỗ sáng, nền tối."""
    H, W = img.shape[:2]
    b = max(4, int(buoc_px))
    key = (W, H, b)
    if key not in _HT:
        x, y = _luoi(W, H)
        u = ((x % b) - b / 2) / (b / 2); v = ((y % b) - b / 2) / (b / 2)
        _HT[key] = np.sqrt(u * u + v * v).astype(np.float32) / math.sqrt(2)
    d = _HT[key]
    l = img.astype(np.float32).mean(2) / 255.0
    on = (d < np.sqrt(np.clip(l, 0, 1)) * 0.78).astype(np.float32)[..., None]
    f = img.astype(np.float32)
    return np.clip(f * (0.28 + 0.62 * on), 0, 255).astype(np.uint8)


# ---------------------------------------------------------------- glitch
def glitch(img, s, k, seed=11):
    """Glitch kéo dọc (23,97–24,25 s mẫu, đo từng khung): các CỘT ảnh bị kéo dọc (1 đoạn ngắn giãn hết chiều cao →
    vệt dọc mang màu ảnh), phủ tới ~80 % bề ngang lúc mạnh nhất · ám XANH LƠ / HỒNG xen kẽ · lệch kênh màu ngang ·
    cháy trắng mạnh 2 khung đầu · nhoè nhẹ. s = 0..1 độ mạnh."""
    if s <= 0.01:
        return img
    H, W = img.shape[:2]
    rng = np.random.default_rng(seed * 100 + k)
    f = img.astype(np.float32)
    # 1) kéo dọc theo dải cột
    out = f.copy()
    phu = 0.85 * s
    x = 0
    while x < W:
        w = int(rng.uniform(0.008, 0.07) * W) + 1
        if rng.random() < phu:
            y0 = int(rng.uniform(0.05, 0.9) * H); h0 = max(2, int(rng.uniform(0.01, 0.08) * H))
            seg = f[y0:min(H, y0 + h0), x:x + w]
            if seg.shape[0] >= 2 and seg.shape[1] >= 1:
                st = cv2.resize(seg, (seg.shape[1], H), interpolation=cv2.INTER_LINEAR)
                a = min(1.0, s * rng.uniform(0.75, 1.15))
                out[:, x:x + w] = out[:, x:x + w] * (1 - a) + st * a
        x += w
    f = out
    # 2) lệch kênh màu
    d = int(C.GLITCH['lech_rgb'] * W * s * (1 if k % 2 == 0 else -1))
    if d:
        f[..., 2] = np.roll(f[..., 2], d, axis=1)
        f[..., 0] = np.roll(f[..., 0], -d, axis=1)
    # 3) ám xanh lơ / hồng xen kẽ
    tint = np.array([1.25, 1.12, 0.62] if k % 2 == 0 else [1.15, 0.7, 1.22], np.float32)
    f = f * (1 + (tint - 1) * s)
    # 4) cháy trắng (mạnh nhất 2 khung đầu)
    f = f + (255 - f) * C.GLITCH['trang'] * s ** 1.4
    if s > 0.4:
        f = cv2.GaussianBlur(f, (0, 0), 0.0025 * W * s)
    return np.clip(f, 0, 255).astype(np.uint8)


# ---------------------------------------------------------------- mảnh vỡ 3D
def _xoay(a):
    c, s = math.cos(a), math.sin(a)
    return np.array([[c, -s], [s, c]], np.float32)


def _bo_goc(w, h, r):
    m = np.zeros((h, w), np.uint8)
    cv2.rectangle(m, (r, 0), (w - r, h), 255, -1); cv2.rectangle(m, (0, r), (w, h - r), 255, -1)
    for cx, cy in ((r, r), (w - r, r), (r, h - r), (w - r, h - r)):
        cv2.circle(m, (cx, cy), r, 255, -1, cv2.LINE_AA)
    return m


def _dan_hm(out, tex, mask_full, Hm, vung, a=1.0, vien=0.0, bong=0.0, toi=0.0):
    """Dán tex (theo mặt nạ uint8 cùng cỡ khung) qua phép chiếu Hm, chỉ tính trong hộp bao đích của đa giác 'vung'.
    vien = viền kính sáng · bong = bóng tối mềm phía dưới-phải · toi = làm tối mảnh."""
    H, W = out.shape[:2]
    pts = cv2.perspectiveTransform(np.asarray(vung, np.float32).reshape(-1, 1, 2), Hm).reshape(-1, 2)
    pad = int(0.02 * W) if bong > 0 else 1
    bx0, by0 = np.floor(pts.min(0)).astype(int) - pad; bx1, by1 = np.ceil(pts.max(0)).astype(int) + pad
    bx0, by0 = max(0, bx0), max(0, by0); bx1, by1 = min(W, bx1), min(H, by1)
    if bx1 - bx0 < 2 or by1 - by0 < 2:
        return
    T = np.array([[1, 0, -bx0], [0, 1, -by0], [0, 0, 1]], np.float64) @ Hm
    sz = (bx1 - bx0, by1 - by0)
    t = cv2.warpPerspective(tex, T, sz, flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT).astype(np.float32)
    m = cv2.warpPerspective(mask_full, T, sz, flags=cv2.INTER_LINEAR).astype(np.float32) / 255.0
    if m.max() <= 0:
        return
    roi = out[by0:by1, bx0:bx1].astype(np.float32)
    if bong > 0:
        sh = cv2.GaussianBlur(m, (0, 0), 0.01 * W)
        sh = np.roll(np.roll(sh, int(0.008 * W), 0), int(0.006 * W), 1)
        roi = roi * (1 - bong * sh[..., None])
    if toi > 0:
        t = t * (1 - toi)
    if vien > 0:
        e = cv2.morphologyEx((m * 255).astype(np.uint8), cv2.MORPH_GRADIENT, np.ones((3, 3), np.uint8)).astype(np.float32) / 255
        t = t + (255 - t) * (e * vien)[..., None]
    al = (m * a)[..., None]
    out[by0:by1, bx0:bx1] = np.clip(roi * (1 - al) + t * al, 0, 255).astype(np.uint8)


def _quad_bien(box, d, rot, sc, nghieng):
    """4 đỉnh box (TL, TR, BR, BL) → dời d, xoay rot (rad) quanh tâm, co sc, nghiêng 3D (cạnh trái/phải co ±nghieng)."""
    c = box.mean(0)
    rel = (box - c) * sc
    k = np.array([[1, 1 - nghieng], [1, 1 + nghieng], [1, 1 + nghieng], [1, 1 - nghieng]], np.float32)
    rel = rel * k
    return (rel @ _xoay(rot).T + c + d).astype(np.float32)


def _ve_do(out, dd, p):
    """Vệt nhọn: mũi đỏ tươi → đuôi tối gần đen (như mẫu 8,9 s), có 3 bóng mờ chuyển động."""
    H, W = out.shape[:2]
    L, T = dd['L'], dd['T']
    x_tam = (-0.6 + 2.2 * C.ease_in(p, 1.6)) * W if dd['trai'] else (1.6 - 2.2 * C.ease_in(p, 1.6)) * W
    c, s = math.cos(dd['ang']), math.sin(dd['ang'])
    sg = 1 if dd['trai'] else -1
    x0 = int(max(0, x_tam - L / 2 - T - 0.12 * W)); x1 = int(min(W, x_tam + L / 2 + T + 0.12 * W))
    y0 = int(max(0, dd['y'] - L / 2 * abs(s) - T * 2)); y1 = int(min(H, dd['y'] + L / 2 * abs(s) + T * 2))
    if x1 - x0 < 2 or y1 - y0 < 2:
        return
    layer = np.zeros((y1 - y0, x1 - x0), np.float32)
    for j in range(3):
        xo = x_tam - sg * j * 0.035 * W
        tip = (xo + sg * L / 2 * c, dd['y'] + sg * L / 2 * s)
        b1 = (xo - sg * L / 2 * c - T / 2 * s, dd['y'] - sg * L / 2 * s + T / 2 * c)
        b2 = (xo - sg * L / 2 * c + T / 2 * s, dd['y'] - sg * L / 2 * s - T / 2 * c)
        tmp = np.zeros_like(layer, np.uint8)
        cv2.fillPoly(tmp, [(np.array([tip, b1, b2], np.float32) - [x0, y0]).astype(np.int32)], 255, cv2.LINE_AA)
        layer = np.maximum(layer, tmp.astype(np.float32) / 255 * (1 - j * 0.3))
    xs = np.arange(x0, x1, dtype=np.float32)
    g = np.clip(((xs - x_tam) * sg * c) / L + 0.5, 0, 1)[None, :, None]
    c_duoi = np.array(C.MANH['mau_do'][2], np.float32); c_mui = np.array(C.MANH['mau_do'][1], np.float32)
    col = c_duoi * (1 - g) + c_mui * g
    a = layer[..., None]
    roi = out[y0:y1, x0:x1].astype(np.float32)
    out[y0:y1, x0:x1] = np.clip(roi * (1 - a) + col * a, 0, 255).astype(np.uint8)


def _tao_do(rng, W, H, so, u_tu, u_buoc):
    doc = H > W
    do = []
    for k in range(so):
        L = rng.uniform(0.75, 1.2) * W * (1.4 if doc else 1.0); T = rng.uniform(0.05, 0.11) * H * (0.75 if doc else 1.0)
        do.append(dict(L=L, T=T, y=rng.uniform(0.08, 0.62) * H, ang=math.radians(rng.uniform(-16, 16)),
                       u0=u_tu + u_buoc * k + rng.uniform(-0.03, 0.03), dai=rng.uniform(0.22, 0.32), trai=bool(rng.random() < 0.5)))
    return do


def _luoi_o(W, H, nx, ny):
    """Lưới ô chữ nhật (x0, y0, x1, y1) phủ kín khung."""
    o = []
    for j in range(ny):
        for i in range(nx):
            o.append((int(round(i * W / nx)), int(round(j * H / ny)), int(round((i + 1) * W / nx)), int(round((j + 1) * H / ny))))
    return o


class MangVo:
    """Chuyển cảnh MẢNH VỠ giữa 2 cảnh xe (mẫu 6,45–7,70 / 8,45–9,77 s, đo từng khung):
    cảnh cũ phủ CHẤM BI rõ dần + VỠ thành 2 tấm dài chéo trượt dọc trục · 2 vệt NHOÈ NGANG quét · vệt đỏ nhọn ·
    TẤM KÍNH bo góc mang cảnh mới ĐÚNG CHỖ (bật ra, lệch nhẹ) · cảnh mới về thành Ô bo góc lớn lệch nhẹ rồi khớp dần.
    u = 0 → 1 trong cửa sổ 'truoc'."""

    def __init__(self, W, H, seed=1, huong=0):
        self.W, self.H = W, H
        rng = np.random.default_rng(seed)
        m = C.MANH
        doc = H > W
        S = min(W, H)
        # (a) cảnh cũ vỡ thành tấm dài chéo, trượt dọc trục
        self.dai = []
        for k in range(m['so_dai']):
            ang = math.radians(rng.uniform(-30, -14) if (k + huong) % 2 == 0 else rng.uniform(10, 24))
            T = rng.uniform(0.15, 0.24) * H * (0.8 if doc else 1.0)
            yc = rng.uniform(0.2, 0.42) * H if k == 0 else rng.uniform(0.55, 0.78) * H
            u0 = 0.08 + 0.14 * k + rng.uniform(-0.02, 0.02)
            self.dai.append(dict(ang=ang, T=T, yc=yc, u0=u0, u1=u0 + rng.uniform(0.5, 0.62),
                                 dich=rng.uniform(0.22, 0.4) * W * (1 if rng.random() < 0.5 else -1)))
        # (b) vệt nhoè ngang (dải ảnh kéo nhoè rất dài)
        self.nhoe = []
        for k in range(m['so_nhoe']):
            h = rng.uniform(0.045, 0.09) * H
            self.nhoe.append(dict(y=rng.uniform(0.15, 0.85) * H, h=h, u0=0.12 + 0.14 * k + rng.uniform(-0.02, 0.02),
                                  dai=rng.uniform(0.16, 0.24), trai=bool(rng.random() < 0.5), moi=bool(k % 2)))
        # (c) vệt đỏ
        self.do = _tao_do(rng, W, H, m['so_do'], 0.16, 0.15)
        # (d) tấm kính cảnh mới đúng chỗ
        self.kinh = []
        for k in range(m['so_kinh']):
            w = int(rng.uniform(0.5, 0.72) * W) if doc else int(rng.uniform(0.3, 0.42) * W)
            h = int(w * (rng.uniform(0.62, 0.85) if doc else rng.uniform(0.6, 0.8)))
            x = int(rng.uniform(0.0, 1.0) * (W - w)); y = int(rng.uniform(0.04, 0.96) * (H - h))
            u0 = 0.15 + 0.13 * k + rng.uniform(-0.02, 0.02)
            self.kinh.append(dict(box=np.array([[x, y], [x + w, y], [x + w, y + h], [x, y + h]], np.float32), u0=u0,
                                  d0=np.array([rng.uniform(-0.1, 0.1) * W, rng.uniform(-0.06, 0.06) * H], np.float32),
                                  rot=math.radians(rng.uniform(-9, 9)), ng=rng.uniform(-0.12, 0.12),
                                  mk=_bo_goc(w, h, max(4, int(m['bo_goc'] * S))), x=x, y=y, w=w, h=h))
        # (e) ô cảnh mới (lưới lớn) lệch nhẹ → khớp
        nx, ny = (2, 3) if doc else (3, 2)
        o = _luoi_o(W, H, nx, ny)
        rng.shuffle(o)
        r = max(4, int(m['bo_goc'] * S))
        a0, a1 = m['o_tu']
        self.o = []
        for k, (x0, y0, x1, y1) in enumerate(o):
            mk = np.zeros((H, W), np.uint8)
            mk[y0:y1, x0:x1] = _bo_goc(x1 - x0, y1 - y0, r)
            u0 = a0 + (a1 - a0) * k / max(1, len(o) - 1)
            self.o.append(dict(box=np.array([[x0, y0], [x1, y0], [x1, y1], [x0, y1]], np.float32), mk=mk, u0=u0,
                               d=np.array([rng.uniform(0.05, 0.12) * W * rng.choice([-1, 1]), rng.uniform(-0.05, 0.05) * H], np.float32),
                               sc=rng.uniform(0.86, 0.95), rot=math.radians(rng.uniform(-4, 4)), ht=bool(rng.random() < 0.35)))

    def _poly_dai(self, dd):
        W, H = self.W, self.H
        c, s = math.cos(dd['ang']), math.sin(dd['ang'])
        L = 2.2 * max(W, H)
        cx, cy = W / 2, dd['yc']
        n = np.array([-s, c]) * dd['T'] / 2
        u = np.array([c, s]) * L / 2
        p = np.array([[cx, cy], [cx, cy], [cx, cy], [cx, cy]], np.float64) + np.array([-u - n, u - n, u + n, -u + n])
        return p.astype(np.float32), np.array([c, s])

    def ve(self, cu, moi, u, nguoi=None):
        W, H = self.W, self.H
        m = C.MANH
        if u >= m['lap_day'][1]:
            return moi
        ht_cu = halftone(cu, m['halftone_buoc'] * max(W, H))
        ah = m['cham_cu'] * C.ease_out(min(1.0, u / m['cham_vao']), 2)
        out = cv2.addWeighted(cu, 1 - ah, ht_cu, ah, 0) if ah > 0.01 else cu.copy()
        nen = out.copy()
        # (a) tấm dài cảnh cũ trượt
        for dd in self.dai:
            if not (dd['u0'] <= u <= dd['u1']):
                continue
            p = (u - dd['u0']) / (dd['u1'] - dd['u0'])
            poly, ax = self._poly_dai(dd)
            dich = dd['dich'] * C.ease_in(p, 1.7)
            mk = np.zeros((H, W), np.uint8)
            cv2.fillPoly(mk, [poly.astype(np.int32)], 255, cv2.LINE_AA)
            Hm = np.array([[1, 0, ax[0] * dich], [0, 1, ax[1] * dich], [0, 0, 1]], np.float64)
            fade = 1 - C.ease_io((p - 0.8) / 0.2)
            _dan_hm(out, nen, mk, Hm, poly, a=fade, vien=0.5, bong=0.45, toi=0.12 * p)
        # (b) vệt nhoè ngang
        for nn in self.nhoe:
            if not (nn['u0'] <= u <= nn['u0'] + nn['dai']):
                continue
            p = (u - nn['u0']) / nn['dai']
            y0 = int(max(0, nn['y'] - nn['h'] / 2)); y1 = int(min(H, nn['y'] + nn['h'] / 2))
            if y1 - y0 < 2:
                continue
            src = (moi if nn['moi'] else cu)[y0:y1]
            k = int(0.35 * W) | 1
            bl = cv2.blur(src, (k, 1))
            dx = int(((-1 + 2.2 * p) if nn['trai'] else (1 - 2.2 * p)) * W)
            bl = np.roll(bl, dx, axis=1)
            al = math.sin(math.pi * p) * 0.9
            out[y0:y1] = cv2.addWeighted(out[y0:y1], 1 - al, bl, al, 0)
        # (c) vệt đỏ
        for dd in self.do:
            if dd['u0'] <= u <= dd['u0'] + dd['dai']:
                _ve_do(out, dd, (u - dd['u0']) / dd['dai'])
        # (d) tấm kính cảnh mới đúng chỗ, bật ra
        for kn in self.kinh:
            if u < kn['u0']:
                continue
            p = C.ease_out((u - kn['u0']) / 0.12, 3)
            q = 1 - C.ease_io((u - kn['u0']) / (0.9 - kn['u0']))       # lệch dư → 0
            dst = _quad_bien(kn['box'], kn['d0'] * (0.35 + 0.65 * (1 - p)) * q, kn['rot'] * q, 0.8 + 0.2 * p, kn['ng'] * q)
            Hm = cv2.getPerspectiveTransform(kn['box'], dst)
            mk = np.zeros((H, W), np.uint8)
            mk[kn['y']:kn['y'] + kn['h'], kn['x']:kn['x'] + kn['w']] = kn['mk']
            _dan_hm(out, moi, mk, Hm, kn['box'], a=min(1.0, p * 1.6), vien=0.7 * q, bong=0.35 * q, toi=0.15 * q)
        # (e) ô cảnh mới
        ht_moi = None
        for o in self.o:
            if u < o['u0']:
                continue
            p = C.ease_out((u - o['u0']) / m['o_dai'], 2.6)
            q = 1 - C.ease_io((u - o['u0']) / (m['o_xong'] - o['u0']))
            dst = _quad_bien(o['box'], o['d'] * (0.4 * q + 0.6 * (1 - p)), o['rot'] * q, o['sc'] + (1 - o['sc']) * (1 - q), 0.0)
            Hm = cv2.getPerspectiveTransform(o['box'], dst)
            tex = moi
            if o['ht'] and q > 0.4:
                if ht_moi is None:
                    ht_moi = halftone(moi, m['halftone_buoc'] * max(W, H))
                k = min(1.0, (q - 0.4) / 0.3)
                tex = cv2.addWeighted(moi, 1 - k, ht_moi, k, 0)
            _dan_hm(out, tex, o['mk'], Hm, o['box'], a=min(1.0, p * 2.0), vien=0.45 * q, bong=0.3 * q, toi=0.25 * q)
        a0, a1 = m['lap_day']
        if u > a0:
            k = C.ease_io((u - a0) / (a1 - a0))
            out = cv2.addWeighted(out, 1 - k, moi, k, 0)
        return out


class MangMo:
    """Mảnh vỡ MỞ ĐẦU khi người dẫn cầm mảnh giữa 2 tay (mẫu 4,45–5,67 s):
    • lớp 'khung tay + mảnh' LAO VỀ MÁY (phóng nhanh dần quanh tâm mảnh, 2 tay văng ra 2 mép rồi mất ở u≈0,5);
    • cảnh mới vỡ thành 5–6 MẢNH LỚN (lưới méo) bay vào từ ngoài, xoay + nghiêng 3D, đáp chỗ ở u 0,12–0,46;
    • nền cảnh cũ đổi sang cảnh mới khi mảnh đã phủ (u 0,40–0,52); mảnh còn lệch nhẹ rồi khớp dần tới 0,95."""

    def __init__(self, W, H, seed=1):
        self.W, self.H = W, H
        rng = np.random.default_rng(seed)
        M = C.MANH_MO
        doc = H > W
        nx, ny = M['luoi']['doc' if doc else 'ngang']
        # lưới đỉnh méo (đỉnh trong rung ± rung_dinh ô)
        gx = np.linspace(0, W, nx + 1); gy = np.linspace(0, H, ny + 1)
        V = np.zeros((ny + 1, nx + 1, 2), np.float32)
        for j in range(ny + 1):
            for i in range(nx + 1):
                x, y = gx[i], gy[j]
                if 0 < i < nx:
                    x += rng.uniform(-1, 1) * M['rung_dinh'] * W / nx
                if 0 < j < ny:
                    y += rng.uniform(-1, 1) * M['rung_dinh'] * H / ny
                V[j, i] = (x, y)
        manh = []
        for j in range(ny):
            for i in range(nx):
                q = np.array([V[j, i], V[j, i + 1], V[j + 1, i + 1], V[j + 1, i]], np.float32)
                manh.append(q)
        rng.shuffle(manh)
        d0, d1 = M['dap']
        self.manh = []
        tam = np.array([W / 2, H / 2], np.float32)
        for k, q in enumerate(manh):
            c = q.mean(0)
            v = c - tam
            v = v / (np.hypot(*v) + 1e-6) if np.hypot(*v) > 1 else np.array([1.0, 0.0])
            ud = d0 + (d1 - d0) * k / max(1, len(manh) - 1) + rng.uniform(-0.02, 0.02)
            mk = np.zeros((H, W), np.uint8)
            cv2.fillPoly(mk, [q.astype(np.int32)], 255, cv2.LINE_AA)
            self.manh.append(dict(q=q, mk=mk, ud=ud, bay=M['bay'] * rng.uniform(0.85, 1.15),
                                  xa=(v * rng.uniform(0.75, 1.1) * max(W, H)).astype(np.float32),
                                  rot=math.radians(rng.uniform(25, 50) * rng.choice([-1, 1])), sc=rng.uniform(0.55, 0.75),
                                  ng=rng.uniform(0.2, 0.35) * rng.choice([-1, 1]),
                                  du=np.array([rng.uniform(-1, 1), rng.uniform(-1, 1)], np.float32) * M['lech_du'] * W,
                                  rot_du=math.radians(rng.uniform(-3, 3))))
        self.do = _tao_do(rng, W, H, M['so_do'], 0.08, 0.16)

    def ve(self, cu, moi, u, lop=None, tam=None):
        """cu = cảnh cũ SẠCH (không mảnh), lop = (ảnh có mảnh + tay, mặt nạ float 'mảnh ∪ tay'), tam = tâm mảnh px."""
        W, H = self.W, self.H
        M = C.MANH_MO
        if u >= 0.985:
            return moi
        n0, n1 = M['nen_doi']
        k = C.ease_io((u - n0) / (n1 - n0))
        out = cu.copy() if k <= 0 else (moi.copy() if k >= 1 else cv2.addWeighted(cu, 1 - k, moi, k, 0))
        for dd in self.do:
            if dd['u0'] <= u <= dd['u0'] + dd['dai']:
                _ve_do(out, dd, (u - dd['u0']) / dd['dai'])
        for mm in sorted(self.manh, key=lambda z: z['ud']):
            ub = mm['ud'] - mm['bay']
            if u < ub:
                continue
            p = C.ease_out((u - ub) / mm['bay'], 3)              # 0 → 1 lúc đáp
            q = 1 - C.ease_io((u - mm['ud']) / (0.95 - mm['ud'])) if u > mm['ud'] else 1.0   # lệch dư → 0
            d = mm['xa'] * (1 - p) + mm['du'] * q
            dst = _quad_bien(mm['q'], d, mm['rot'] * (1 - p) + mm['rot_du'] * q, mm['sc'] + (1 - mm['sc']) * p, mm['ng'] * (1 - p))
            Hm = cv2.getPerspectiveTransform(mm['q'], dst)
            _dan_hm(out, moi, mm['mk'], Hm, mm['q'], a=min(1.0, 0.25 + p), vien=0.8 * (0.3 + 0.7 * q) if q > 0.02 else 0.0,
                    bong=0.5 * (1 - p) + 0.2 * q)
        if lop is not None and tam is not None:
            h0, h1 = M['lop_het']
            a = 1 - C.ease_io((u - h0) / (h1 - h0))
            if a > 0.01:
                g = 1 + M['lop_zoom'] * u ** M['lop_mu']
                A = np.float32([[g, 0, (1 - g) * tam[0]], [0, g, (1 - g) * tam[1]]])
                img, mk = lop
                li = cv2.warpAffine(img, A, (W, H), flags=cv2.INTER_LINEAR)
                lm = cv2.warpAffine(mk, A, (W, H), flags=cv2.INTER_LINEAR)
                # nhoè chuyển động theo độ phóng (lao nhanh về máy)
                if g > 1.3:
                    li = nhoe(li, min(6.0, (g - 1.3) * 1.6) * W / 1080)
                tron_mat_na(out, li, lm, a)
        return out


def tron_mat_na(out, img, mask, k=1.0):
    """out ← img theo mặt nạ float 0..1 (chỉ tính trong hộp bao của mặt nạ). Sửa out tại chỗ."""
    ys, xs = np.nonzero(mask[::8, ::8] > 0.01)
    if len(ys) == 0:
        return out
    H, W = mask.shape
    y0, y1 = max(0, ys.min() * 8 - 8), min(H, ys.max() * 8 + 16)
    x0, x1 = max(0, xs.min() * 8 - 8), min(W, xs.max() * 8 + 16)
    a = (mask[y0:y1, x0:x1] * k)[..., None]
    out[y0:y1, x0:x1] = np.clip(out[y0:y1, x0:x1].astype(np.float32) * (1 - a) + img[y0:y1, x0:x1].astype(np.float32) * a,
                                0, 255).astype(np.uint8)
    return out


def manh_cho(out, moi, t_u, x, y, rong, seed=5):
    """Mảnh nhỏ của cảnh sau hiện giữa 2 tay người (3,2–4,3 s mẫu)."""
    H, W = out.shape[:2]
    rng = np.random.default_rng(seed)
    w = rong * W * (0.5 + 0.5 * C.ease_out(t_u)); h = w * 0.42
    a = math.radians(-8 + 6 * math.sin(t_u * 5))
    cx, cy = x * W, y * H
    pts = np.array([[-w / 2, -h / 2], [w / 2, -h / 2 * 0.8], [w / 2 * 0.95, h / 2], [-w / 2, h / 2 * 0.85]], np.float32)
    R = _xoay(a)
    dst = pts @ R.T + np.array([cx, cy], np.float32)
    src = np.array([[cx - w / 2, cy - h / 2], [cx + w / 2, cy - h / 2], [cx + w / 2, cy + h / 2], [cx - w / 2, cy + h / 2]], np.float32)
    Hm = cv2.getPerspectiveTransform(src, dst)
    tex = cv2.warpPerspective(moi, Hm, (W, H))
    mk = np.zeros((H, W), np.uint8)
    cv2.fillPoly(mk, [dst.astype(np.int32)], 255, cv2.LINE_AA)
    al = (mk.astype(np.float32) / 255 * min(1, t_u * 4))[..., None]
    return np.clip(out.astype(np.float32) * (1 - al) + tex.astype(np.float32) * 0.85 * al, 0, 255).astype(np.uint8)


def manh_tay(out, moi, P, a=1.0, vien=0.55, tay=None, sach=None):
    """Mảnh cảnh sau (tứ giác P = TL, TR, BR, BL px) căng giữa 2 bàn tay; tay = mặt nạ ngón tay 0..1 vẽ đè lại từ 'sach'."""
    H, W = out.shape[:2]
    P = np.asarray(P, np.float32)
    wq = (np.hypot(*(P[1] - P[0])) + np.hypot(*(P[2] - P[3]))) / 2
    hq = (np.hypot(*(P[3] - P[0])) + np.hypot(*(P[2] - P[1]))) / 2
    if wq < 3 or hq < 3 or a <= 0.01:
        return out
    ar = hq / wq
    sw = 0.9 * W; sh = sw * ar
    if sh > 0.9 * H:
        sh = 0.9 * H; sw = sh / ar
    cx, cy = W / 2, H * 0.5
    src = np.array([[cx - sw / 2, cy - sh / 2], [cx + sw / 2, cy - sh / 2], [cx + sw / 2, cy + sh / 2], [cx - sw / 2, cy + sh / 2]], np.float32)
    x0, y0 = np.floor(P.min(0)).astype(int) - 2; x1, y1 = np.ceil(P.max(0)).astype(int) + 3
    x0, y0, x1, y1 = max(0, x0), max(0, y0), min(W, x1), min(H, y1)
    if x1 - x0 < 3 or y1 - y0 < 3:
        return out
    Hm = cv2.getPerspectiveTransform(src, P - np.array([x0, y0], np.float32))
    tex = cv2.warpPerspective(moi, Hm, (x1 - x0, y1 - y0), flags=cv2.INTER_LINEAR).astype(np.float32)
    mk = np.zeros((y1 - y0, x1 - x0), np.uint8)
    cv2.fillPoly(mk, [(P - [x0, y0]).astype(np.int32)], 255, cv2.LINE_AA)
    al = mk.astype(np.float32)[..., None] / 255.0
    if vien > 0:   # viền kính sáng mảnh
        e = cv2.morphologyEx(mk, cv2.MORPH_GRADIENT, np.ones((3, 3), np.uint8)).astype(np.float32)[..., None] / 255
        tex = tex + (255 - tex) * e * vien
    roi = out[y0:y1, x0:x1].astype(np.float32)
    res = roi * (1 - al * a) + tex * al * a
    if tay is not None and sach is not None:
        t = tay[y0:y1, x0:x1][..., None]
        res = res * (1 - t) + sach[y0:y1, x0:x1].astype(np.float32) * t
    out = out.copy()
    out[y0:y1, x0:x1] = np.clip(res, 0, 255).astype(np.uint8)
    return out


def khung_dien_anh(img, ty_le, nguoi=None):
    """Dải điện ảnh: 2 thanh đen trên/dưới, người (nếu có mặt nạ) nổi ra ngoài thanh (0–1 s mẫu)."""
    H, W = img.shape[:2]
    if ty_le >= 0.999:
        return img
    bh = int(round(H * (1 - ty_le) / 2))
    out = img.copy()
    out[:bh] = 0; out[H - bh:] = 0
    if nguoi is not None and bh > 0:
        nm = nguoi.copy()
        nm[bh:H - bh] = 0
        tron_mat_na(out, img, nm)
    return out
