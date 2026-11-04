# -*- coding: utf-8 -*-
"""Bố cục cảnh + hiệu ứng: phủ kín/Ken Burns, thẻ bo góc trên nền nhoè, ghép 3 thẻ + bướm, tấm kính 3D,
loé cam (light leak), loé trắng + rung, phóng-lùi, phóng nhanh, nhân bản loé. Số đo ở chung.py."""
import math
import numpy as np
import cv2
import chung as C

W, H = C.W, C.H


def ease_out(u):
    u = min(1.0, max(0.0, u)); return 1 - (1 - u) ** 3


def ease_io(u):
    u = min(1.0, max(0.0, u)); return u * u * (3 - 2 * u)


# ---------------------------------------------------------------- phủ kín / Ken Burns
def cover(img, w, h):
    ih, iw = img.shape[:2]
    s = max(w / iw, h / ih)
    r = cv2.resize(img, (int(math.ceil(iw * s)), int(math.ceil(ih * s))), interpolation=cv2.INTER_AREA if s < 1 else cv2.INTER_CUBIC)
    y = (r.shape[0] - h) // 2; x = (r.shape[1] - w) // 2
    return r[y:y + h, x:x + w]


def ken_burns(src, w, h, z, px=0.0, py=0.0):
    """src đã phủ kín đúng w×h; phóng z ≥ 1 quanh tâm, lệch (px,py) px (bị giới hạn để không lộ mép)."""
    if z <= 1.0005 and px == 0 and py == 0: return src.copy()   # KHÔNG trả bộ đệm gốc (ảnh cache / buffer chỉ đọc)
    mx, my = (z - 1) * w / 2, (z - 1) * h / 2
    px, py = float(np.clip(px, -mx, mx)), float(np.clip(py, -my, my))
    M = np.float32([[z, 0, -(z - 1) * w / 2 - px], [0, z, -(z - 1) * h / 2 - py]])
    return cv2.warpAffine(src, M, (w, h), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)


def phong(frame, z, cx=W / 2, cy=H / 2):
    if abs(z - 1) < 1e-3: return frame.copy()
    M = np.float32([[z, 0, cx - z * cx], [0, z, cy - z * cy]])
    return cv2.warpAffine(frame, M, (W, H), flags=cv2.INTER_CUBIC if z > 1.15 else cv2.INTER_LINEAR,
                          borderMode=cv2.BORDER_REFLECT)


_TOI = {}


def toi_tren(frame, manh):
    """tối dần nửa trên khung (0 ở y TOI_TREN['y'] → manh ở đỉnh) để chữ màu nổi trên nền sáng."""
    k = (manh,)
    if k not in _TOI:
        y = C.TOI_TREN['y']
        _TOI[k] = (1 - np.clip((y - np.arange(H)) / y, 0, 1) * manh).astype(np.float32)[:, None, None]
    return (frame.astype(np.float32) * _TOI[k]).astype(np.uint8)


def nhoe_nhanh(img, k=8):
    h, w = img.shape[:2]
    s = cv2.resize(img, (max(2, w // k), max(2, h // k)), interpolation=cv2.INTER_AREA)
    s = cv2.GaussianBlur(s, (0, 0), C.THE_MO['nhoe'] / k)
    return cv2.resize(s, (w, h), interpolation=cv2.INTER_LINEAR)


# ---------------------------------------------------------------- thẻ bo góc
_MASK = {}


def mask_bo_goc(w, h, r):
    k = (w, h, r)
    if k not in _MASK:
        m = np.zeros((h * 2, w * 2), np.uint8)
        R = r * 2
        cv2.rectangle(m, (R, 0), (w * 2 - R, h * 2), 255, -1)
        cv2.rectangle(m, (0, R), (w * 2, h * 2 - R), 255, -1)
        for cx, cy in ((R, R), (w * 2 - R, R), (R, h * 2 - R), (w * 2 - R, h * 2 - R)):
            cv2.circle(m, (cx, cy), R, 255, -1, lineType=cv2.LINE_AA)
        _MASK[k] = cv2.resize(m, (w, h), interpolation=cv2.INTER_AREA).astype(np.float32) / 255.0
    return _MASK[k]


def dan_the(frame, img, x, y, r, bong=0.5, vien=None, vien_px=0):
    """dán ảnh img (BGR) bo góc r tại (x,y) góc trái trên, có bóng mềm."""
    h, w = img.shape[:2]
    m = mask_bo_goc(w, h, r)
    if bong > 0:
        pad = 40
        sm = np.zeros((h + 2 * pad, w + 2 * pad), np.float32); sm[pad:pad + h, pad:pad + w] = m
        sm = cv2.GaussianBlur(sm, (0, 0), 16) * bong
        _blend_mask(frame, None, sm, int(x) - pad, int(y) - pad + 14)
    if vien is not None and vien_px > 0:
        hv, wv = h + 2 * vien_px, w + 2 * vien_px
        mv = mask_bo_goc(wv, hv, r + vien_px)
        col = np.empty((hv, wv, 3), np.float32); col[:] = vien
        _blend_mask(frame, col, mv, int(x) - vien_px, int(y) - vien_px)
    _blend_mask(frame, img.astype(np.float32), m, int(x), int(y))


def _blend_mask(frame, col, m, x, y):
    """col=None → phủ đen theo m (bóng)."""
    h, w = m.shape
    H_, W_ = frame.shape[:2]
    xa, ya, xb, yb = max(0, x), max(0, y), min(W_, x + w), min(H_, y + h)
    if xa >= xb or ya >= yb: return
    mm = m[ya - y:yb - y, xa - x:xb - x][..., None]
    roi = frame[ya:yb, xa:xb].astype(np.float32)
    src = 0 if col is None else col[ya - y:yb - y, xa - x:xb - x]
    frame[ya:yb, xa:xb] = np.clip(roi * (1 - mm) + src * mm, 0, 255).astype(np.uint8)


def canh_the_mo(src_frame, z):
    """bố cục 'thẻ trên nền nhoè': nền = chính ảnh phủ kín + nhoè + tối; thẻ ảnh ngang bo góc ở giữa."""
    cfg = C.THE_MO
    bg = nhoe_nhanh(cover(src_frame, W, H), 8)
    bg = (bg.astype(np.float32) * cfg['toi']).astype(np.uint8)
    ih, iw = src_frame.shape[:2]
    cw = cfg['rong']; ch = int(round(cw * min(ih / iw, 0.75)))
    card = cover(src_frame, cw, ch)
    card = ken_burns(card, cw, ch, z)
    dan_the(bg, card, (W - cw) // 2, cfg['tam_y'] - ch // 2, cfg['bo_goc'], bong=0.55)
    return bg


# ---------------------------------------------------------------- ghép 3 thẻ + bướm
def nen_ghep3(mau_hex):
    b, g, r = C.hex2rgb(mau_hex)[::-1]
    yy = np.linspace(0, 1, H, dtype=np.float32)[:, None, None]
    base = np.array([b, g, r], np.float32)[None, None]
    top = base + (255 - base) * 0.10; bot = base * 0.80
    img = top * (1 - yy) + bot * yy
    rng = np.random.default_rng(7)
    nz = cv2.resize(rng.random((48, 27)).astype(np.float32), (W, H), interpolation=cv2.INTER_CUBIC)
    img = img * (0.94 + 0.12 * nz[..., None])
    return np.clip(np.broadcast_to(img, (H, W, 3)), 0, 255).astype(np.uint8)


def _buom_sprite(sz, mo, mau=(245, 170, 60)):
    """1 con bướm vẽ tay → BGR premultiplied + alpha (float 0..1); mo = độ mở cánh 0.2..1."""
    s = sz * 2
    col = np.zeros((s, s, 3), np.float32); A = np.zeros((s, s), np.float32)
    c = s // 2
    for sx in (-1, 1):
        for (ax, ay, rx, ry, k) in ((0.30, -0.12, 0.30, 0.24, 1.0), (0.22, 0.20, 0.20, 0.17, 0.8)):
            cx = int(c + sx * ax * s * mo); cy = int(c + ay * s)
            m = np.zeros((s, s), np.uint8)
            cv2.ellipse(m, (cx, cy), (max(1, int(rx * s * mo)), int(ry * s)), 0, 0, 360, 255, -1, cv2.LINE_AA)
            a = (m.astype(np.float32) / 255)[..., None]
            col = col * (1 - a) + (np.array(mau, np.float32) / 255 * k) * a
            A = np.maximum(A, a[..., 0])
    m = np.zeros((s, s), np.uint8)
    cv2.ellipse(m, (c, c), (max(1, s // 28), s // 4), 0, 0, 360, 255, -1, cv2.LINE_AA)
    a = (m.astype(np.float32) / 255)[..., None]
    col = col * (1 - a) + np.array((0.24, 0.12, 0.08), np.float32) * a
    A = np.maximum(A, a[..., 0])
    return cv2.resize(np.dstack([col, A]), (sz, sz), interpolation=cv2.INTER_AREA)


class DanBuom:
    def __init__(self, t0, n=14, seed=3):
        rng = np.random.default_rng(seed)
        self.t0 = t0
        self.b = []
        for i in range(n):
            self.b.append({'d': rng.uniform(0, 0.9), 'x': rng.uniform(-150, 500), 'y': rng.uniform(900, 1700),
                           'vx': rng.uniform(380, 650), 'vy': rng.uniform(-620, -320), 'sz': int(rng.uniform(46, 84)),
                           'f': rng.uniform(7, 10), 'ph': rng.uniform(0, 6.28), 'rot': rng.uniform(-30, 30),
                           'mau': (float(rng.uniform(220, 255)), float(rng.uniform(140, 190)), float(rng.uniform(40, 80)))})

    def ve(self, frame, t):
        import chu
        for b in self.b:
            u = t - self.t0 - b['d']
            if u < 0 or u > 2.6: continue
            x = b['x'] + b['vx'] * u + 40 * math.sin(u * 5 + b['ph'])
            y = b['y'] + b['vy'] * u + 30 * math.sin(u * 7 + b['ph'])
            if x > W + 100 or y < -100: continue
            mo = 0.25 + 0.75 * abs(math.cos(math.pi * b['f'] * u + b['ph']))
            sp = _buom_sprite(b['sz'], mo, b['mau'])
            M = cv2.getRotationMatrix2D((b['sz'] / 2, b['sz'] / 2), b['rot'] - 25, 1.0)
            sp = cv2.warpAffine(sp, M, (b['sz'], b['sz']))
            rgba = np.dstack([sp[..., :3][..., ::-1], sp[..., 3]])   # chu.dan nhận RGB premultiplied (tự đảo sang BGR)
            chu.dan(frame, rgba.astype(np.float32), x, y)


# ---------------------------------------------------------------- tấm kính 3D
def tam_kinh(anhs, w=400, h=720):
    """ghép ảnh xếp dọc trong 1 tấm kính bo góc viền xanh ngọc phát sáng → BGRA float 0..1."""
    pad = 18
    panel = np.zeros((h, w, 3), np.float32); panel[:] = (70, 60, 20)
    n = max(1, len(anhs)); ch = (h - pad * (n + 1)) // n
    for i, a in enumerate(anhs[:n]):
        c = cover(a, w - 2 * pad, ch).astype(np.float32)
        m = mask_bo_goc(w - 2 * pad, ch, 18)[..., None]
        y = pad + i * (ch + pad)
        panel[y:y + ch, pad:w - pad] = panel[y:y + ch, pad:w - pad] * (1 - m) + c * m
    m = mask_bo_goc(w, h, 36)
    edge = cv2.Canny((m * 255).astype(np.uint8), 50, 150).astype(np.float32) / 255
    glow = cv2.GaussianBlur(cv2.dilate(edge, np.ones((5, 5))), (0, 0), 6)
    glow = np.clip(glow * 2.2, 0, 1)
    cyan = np.array((224, 232, 52), np.float32)
    panel = panel * (1 - glow[..., None]) + cyan * glow[..., None]
    a = np.clip(m * 0.92 + glow * 0.3, 0, 1)
    return np.dstack([panel / 255.0, a]).astype(np.float32)


def ve_kinh3d(frame, panel, yaw_deg, cx, cy, scale=1.0, alpha=1.0):
    h, w = panel.shape[:2]
    f = 1400.0
    yaw = math.radians(yaw_deg)
    pts3 = np.array([[-w / 2, -h / 2], [w / 2, -h / 2], [w / 2, h / 2], [-w / 2, h / 2]], np.float32) * scale
    dst = []
    for X, Y in pts3:
        x = X * math.cos(yaw); z = X * math.sin(yaw) + f
        dst.append([cx + x * f / z, cy + Y * f / z])
    src = np.float32([[0, 0], [w, 0], [w, h], [0, h]])
    M = cv2.getPerspectiveTransform(src, np.float32(dst))
    x0, y0 = int(max(0, min(p[0] for p in dst))), int(max(0, min(p[1] for p in dst)))
    x1, y1 = int(min(W, max(p[0] for p in dst) + 1)), int(min(H, max(p[1] for p in dst) + 1))
    if x1 <= x0 or y1 <= y0: return
    T = np.float32([[1, 0, -x0], [0, 1, -y0], [0, 0, 1]]) @ M
    wp = cv2.warpPerspective(panel, T, (x1 - x0, y1 - y0), flags=cv2.INTER_LINEAR)
    a = wp[..., 3:4] * alpha
    roi = frame[y0:y1, x0:x1].astype(np.float32) / 255
    frame[y0:y1, x0:x1] = np.clip((wp[..., :3] * a + roi * (1 - a)) * 255, 0, 255).astype(np.uint8)


# ---------------------------------------------------------------- loé ánh cam (light leak)
_LEAK = {}


def loe_cam(frame, u, manh=0.85, seed=0):
    """u = tiến trình 0..1 của cú loé; lớp cam/đỏ/vàng từ góc dưới-trái trôi sang phải, hoà kiểu screen."""
    env = math.sin(math.pi * min(1, max(0, u))) ** 0.8 * manh
    if env <= 0.01: return frame
    w, h = 135, 240
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    lay = np.zeros((h, w, 3), np.float32)
    blobs = [((0.05 + 0.55 * u, 0.85 - 0.10 * u), 0.55, (30, 110, 255)),     # cam (BGR)
             ((0.20 + 0.45 * u, 0.62), 0.40, (40, 40, 255)),                  # đỏ
             ((0.0 + 0.30 * u, 0.98), 0.35, (90, 200, 255))]                  # vàng
    for (bx, by), r, col in blobs:
        d = ((xx / w - bx) ** 2 + ((yy / h - by) * 0.75) ** 2) / (r * r)
        g = np.exp(-d * 2.2)
        lay += g[..., None] * np.array(col, np.float32) / 255
    lay = np.clip(lay, 0, 1) * env
    lay = cv2.resize(lay, (W, H), interpolation=cv2.INTER_CUBIC)
    f = frame.astype(np.float32) / 255
    return np.clip((1 - (1 - f) * (1 - lay)) * 255, 0, 255).astype(np.uint8)


def loe_trang(frame, env, sang=0.55):
    if env <= 0.01: return frame
    f = frame.astype(np.float32)
    return np.clip(f * (1 + sang * env) + 40 * env, 0, 255).astype(np.uint8)


# ---------------------------------------------------------------- nhân bản loé (cần tách người)
_REMBG = {}


def mat_na_nguoi(frame_bgr):
    try:
        from rembg import remove, new_session
    except Exception:
        return None
    if 's' not in _REMBG: _REMBG['s'] = new_session('u2net_human_seg')
    small = cv2.resize(frame_bgr, (540, 960))
    from PIL import Image
    m = remove(Image.fromarray(small[..., ::-1]), session=_REMBG['s'], only_mask=True)
    m = cv2.resize(np.asarray(m, np.float32) / 255, (W, H))
    return np.clip((m - 0.3) / 0.4, 0, 1)


def nhan_ban(frame, mask, k):
    """k = số khung kể từ lúc bắt đầu (0..5): chẵn = bóng trắng, lẻ = âm bản xám."""
    if mask is None: return frame
    f = frame.astype(np.float32)
    m = mask[..., None]
    if k % 2 == 0:
        g = np.linspace(255, 205, H, dtype=np.float32)[:, None, None]
        out = f * (1 - m * 0.92) + g * m * 0.92
    else:
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY).astype(np.float32)[..., None]
        neg = 255 - gray * 0.85
        out = f * (1 - m) + np.repeat(neg, 3, 2) * 0.55 * m
    return np.clip(out, 0, 255).astype(np.uint8)


def nhoe_zoom(frame, k, n=5):
    """CHỈ dùng khi plan bật "nhoe": true (đúng mẫu 4,43 s). Nhoè chuyển động dọc."""
    s = 1 - abs(k - n / 2) / (n / 2)
    L = int(10 + 70 * s) | 1
    ker = np.zeros((L, 1), np.float32); ker[:] = 1 / L
    return cv2.filter2D(frame, -1, ker)
