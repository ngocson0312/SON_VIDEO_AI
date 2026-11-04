# -*- coding: utf-8 -*-
"""Vẽ CỤM CHỮ kiểu mẫu: dẫn trắng nhỏ + KHOÁ to (số vàng / chữ hẹp đậm) + viết tay; gõ chữ, nhấp nháy,
rơi, xoá ngược, trôi chậm. Mọi số đo trong chung.py (CHU, VAI, CHONG)."""
import math, unicodedata
import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import chung as C

_FONT = {}


def _f(ten, co):
    k = (ten, co)
    if k not in _FONT: _FONT[k] = ImageFont.truetype(C.font(ten), co)
    return _FONT[k]


def _sang_toi(rgb, k):
    """k>0 sáng hơn, k<0 tối hơn."""
    r = np.array(rgb, np.float32)
    return tuple(np.clip(r + (255 - r) * k if k > 0 else r * (1 + k), 0, 255).astype(int))


LE_MAC_DINH = {'dan': 'trai', 'so': 'trai', 'khoa': 'trai', 'nhan': 'trai', 'viet_tay': 'phai',
               'chu_thich': 'phai', 'cau_hoi': 'giua', 'tu_lon': 'giua', 'ten': 'giua', 'sub': 'giua', 'nhan_the': 'trai'}


class Dong:
    """1 dòng chữ đã vẽ sẵn thành RGBA (float, premultiplied) + mốc x từng ký tự để gõ/xoá."""

    def __init__(self, d, mau=None):
        self.d = d
        self.text = unicodedata.normalize('NFC', d['text'])
        self.vai = d.get('vai', 'dan')
        cfg = C.VAI[self.vai]
        co = int(d.get('co', cfg['co']))
        fnt = _f(cfg['font'], co)
        rmax = d.get('rong_max', cfg.get('rong_max'))
        while rmax and fnt.getlength(self.text) > rmax and co > 30:
            co = int(co * 0.94); fnt = _f(cfg['font'], co)
        self.co = co
        mau = mau or d.get('mau') or cfg['mau']
        if mau == 'tu_dong': mau = cfg['mau']
        self.mau = C.BANG_MAU.get(mau, mau)
        P = max(40, int(co * 0.2))                 # đủ chỗ cho quầng
        l, t, r, b = fnt.getbbox(self.text, anchor='ls')
        w, h = int(r - l + 2 * P), int(b - t + 2 * P)
        ox, oy = P - l, P - t                      # gốc (baseline-left) trong ảnh
        m = Image.new('L', (w, h), 0)
        ImageDraw.Draw(m).text((ox, oy), self.text, font=fnt, fill=255, anchor='ls')
        a = np.asarray(m, np.float32) / 255.0
        col = self._to_mau(a, h, oy, fnt)
        base = np.array(C.hex2rgb(self.mau), np.float32) / 255.0
        blur = lambda x, s: cv2.GaussianBlur(x, (0, 0), s)
        # xếp lớp từ dưới lên (premultiplied): bóng tối → quầng cùng màu → viền tối màu → mặt chữ
        rgb = np.zeros((h, w, 3), np.float32); A = np.zeros((h, w), np.float32)

        def over(c, al):
            nonlocal rgb, A
            rgb = c * al[..., None] + rgb * (1 - al[..., None]); A = al + A * (1 - al)

        dx, dy, bl, ba = C.CHU['bong']
        if self.vai in C.CHU_A:      # KIỂU A (user chọn 04/11): quầng cùng màu + bóng đậm + viền tối màu + mặt gradient vân
            cfg_a = C.KIEU_A
            over(np.zeros(3, np.float32), np.roll(blur(a, cfg_a['bong_nhoe']), cfg_a['bong_dy'], 0) * cfg_a['bong_a'])
            over(base, np.clip(blur(a, co * cfg_a['quang_k']), 0, 1) * cfg_a['quang_a'])
            k = np.asarray(Image.fromarray((a * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(cfg_a['vien'])), np.float32) / 255
            over(base * cfg_a['vien_toi'], k)
        else:
            sh = np.roll(np.roll(blur(a, bl), dy, 0), dx, 1) * (ba / 255.0)
            if self.vai in ('dan', 'sub', 'chu_thich', 'viet_tay', 'nhan_the', 'cau_hoi', 'ten'):
                qb, qa = C.CHU['quang_nho']
                sh = np.maximum(sh, np.clip(blur(a, qb) * 2.2, 0, 1) * (qa / 255.0))
            over(np.zeros(3, np.float32), sh)
        over(col, a * float(d.get('do_dac', 1.0)))
        self.rgba = np.dstack([rgb, A]).astype(np.float32)
        ys, xs = np.where(A > 0.02)
        self.y0, self.y1 = int(ys.min()), int(ys.max()) + 1
        self.x0, self.x1 = int(xs.min()), int(xs.max()) + 1
        gy, gx = np.where(a > 0.3)
        self.gy0, self.gy1 = (int(gy.min()), int(gy.max()) + 1) if len(gy) else (self.y0, self.y1)
        self.ox = ox
        self.cut = [ox + fnt.getlength(self.text[:i]) for i in range(len(self.text) + 1)]
        self.n = len(self.text)

    def _to_mau(self, a, h, oy, fnt):
        base = C.hex2rgb(self.mau)
        H_, W_ = a.shape
        yy = np.linspace(0, 1, H_, dtype=np.float32)[:, None]
        if self.vai in ('so', 'nhan', 'khoa', 'tu_lon'):
            # gradient dọc theo phần chữ: sáng trên → màu gốc → tối dưới (mẫu: chữ khoá có độ khối)
            ys = np.where(a.max(1) > 0.3)[0]
            g0, g1 = (ys.min(), ys.max()) if len(ys) else (0, H_ - 1)
            u = np.clip((np.arange(H_) - g0) / max(1, g1 - g0), 0, 1)[:, None]
            top = _sang_toi(base, C.KIEU_A['mat_tren'])
            bot = _sang_toi(base, C.KIEU_A['mat_duoi'])
            col = np.empty((H_, W_, 3), np.float32)
            for c in range(3):
                col[..., c] = np.where(u < 0.5, top[c] + (base[c] - top[c]) * (u / 0.5),
                                       base[c] + (bot[c] - base[c]) * ((u - 0.5) / 0.5))
            if self.vai in ('khoa', 'tu_lon'):   # vân nhẹ như mẫu "TẦNG HẦM"
                rng = np.random.default_rng(len(self.text))
                nz = cv2.resize(rng.random((max(2, H_ // 5), max(2, W_ // 5))).astype(np.float32), (W_, H_))
                col *= (0.93 + 0.12 * nz)[..., None]
            return np.clip(col, 0, 255) / 255.0
        return np.broadcast_to(np.array(base, np.float32) / 255.0, (H_, W_, 3)).copy()

    @property
    def cao(self):
        return self.gy1 - self.gy0

    @property
    def rong(self):
        return self.cut[-1] - self.ox


def bo_cuc(cum):
    """xếp các dòng thành khối; trả về list (Dong, x_goc, y_goc) toạ độ khung 1080x1920."""
    dongs = [Dong(d) for d in cum['dong']]
    if not dongs: return []
    bw = max(d.rong for d in dongs)
    xc = cum.get('x', C.W / 2)
    left = xc - bw / 2
    y = cum.get('y', 300)
    out, prev_bot, prev_vai = [], None, None
    for d in dongs:
        le = d.d.get('le', LE_MAC_DINH.get(d.vai, 'trai'))
        if le == 'trai': gx = left
        elif le == 'phai': gx = left + bw - d.rong
        else: gx = xc - d.rong / 2
        gx += d.d.get('dx', 0)
        if prev_bot is None: top = y
        else:
            ov = C.CHONG.get(d.vai, C.CHONG['default']) if prev_vai in C.CHU_TO else C.CHONG['default']
            top = prev_bot - ov * d.cao + cum.get('gian', 0)
        top += d.d.get('dy', 0)
        x0 = gx - d.ox                     # góc trái ảnh dòng
        y0 = top - d.gy0
        out.append([d, x0, y0])
        prev_bot, prev_vai = top + d.cao, d.vai
    # giữ trong vùng an toàn
    xs0 = min(x0 + d.x0 for d, x0, _ in out); xs1 = max(x0 + d.x1 for d, x0, _ in out)
    ys0 = min(y0 + d.gy0 for d, _, y0 in out); ys1 = max(y0 + d.gy1 for d, _, y0 in out)
    sx = max(0, C.SAFE['x0'] - xs0) - max(0, xs1 - C.SAFE['x1'])
    sy = max(0, C.SAFE['y0'] - ys0) - max(0, ys1 - C.SAFE['y1'])
    for o in out: o[1] += sx; o[2] += sy
    return out


def hop(lay):
    """hộp bao (x0,y0,x1,y1) phần chữ thật của khối đã xếp."""
    return (min(x0 + d.x0 for d, x0, _ in lay), min(y0 + d.gy0 for d, _, y0 in lay),
            max(x0 + d.x1 for d, x0, _ in lay), max(y0 + d.gy1 for d, _, y0 in lay))


def dan(frame, rgba, x, y, alpha_k=1.0):
    """dán RGBA premultiplied (float 0..1) lên frame BGR uint8 tại (x,y) góc trái trên."""
    H_, W_ = frame.shape[:2]
    h, w = rgba.shape[:2]
    x, y = int(round(x)), int(round(y))
    xa, ya, xb, yb = max(0, x), max(0, y), min(W_, x + w), min(H_, y + h)
    if xa >= xb or ya >= yb: return
    src = rgba[ya - y:yb - y, xa - x:xb - x]
    roi = frame[ya:yb, xa:xb].astype(np.float32) / 255.0
    a = src[..., 3:4] * alpha_k
    rgb = src[..., :3][..., ::-1] * alpha_k            # RGB → BGR
    frame[ya:yb, xa:xb] = np.clip((rgb + roi * (1 - a)) * 255.0, 0, 255).astype(np.uint8)


def ve_khoi(frame, lay, cum, t, rung=(0, 0)):
    """vẽ 1 khối chữ tại thời điểm t (giây timeline). Trả True nếu có vẽ gì."""
    fps = C.FPS
    t_ra = cum.get('t1', 1e9)
    ra = cum.get('ra', 'xoa')
    if ra == 'tat' and t >= t_ra: return False
    k_ra = (t - t_ra) * fps if (ra == 'xoa' and t >= t_ra) else -1
    if k_ra >= C.CHU['xoa_khung']: return False
    t_dau = min(d.d['t'] for d, _, _ in lay)
    if t < t_dau: return False
    troi = C.CHU['troi_px_s'] * (t - t_dau) * cum.get('troi', 1)
    if k_ra >= 0: troi += C.CHU['xoa_troi_px'] * (k_ra + 1) / C.CHU['xoa_khung']
    ve = False
    for d, x0, y0 in lay:
        tt = d.d['t']
        if t < tt: continue
        k = int(round((t - tt) * fps))
        vao = d.d.get('vao', 'go' if d.vai not in ('so', 'khoa') else 'go')
        n = d.n
        dy, sy, ak = 0.0, 1.0, 1.0
        if vao == 'go':
            n = min(d.n, int(k * C.CHU['ky_tu_moi_khung']) + 1)
        elif vao == 'nhay':
            if k < C.CHU['nhay_khung'] and k % 2 == 1: continue
        elif vao == 'roi':
            if k < C.CHU['roi_khung']:
                u = (k + 1) / C.CHU['roi_khung']; e = 1 - (1 - u) ** 3
                dy = -C.CHU['roi_px'] * (1 - e); sy = 1 + 0.45 * (1 - e); ak = 0.35 + 0.65 * e
        if k_ra >= 0:
            n = int(math.ceil(n * (1 - (k_ra + 1) / C.CHU['xoa_khung'])))
        if n <= 0: continue
        img = d.rgba
        if n < d.n:
            xc = int(math.ceil(d.cut[n])) + 2
            img = img[:, :max(1, xc)]
        if sy != 1.0:
            h2 = int(img.shape[0] * sy)
            img = cv2.resize(img, (img.shape[1], h2), interpolation=cv2.INTER_LINEAR)
            dy -= (h2 - d.rgba.shape[0]) * 0.5
        dan(frame, img, x0 + troi + rung[0], y0 + dy + rung[1], ak)
        ve = True
    return ve


# ---------------------------------------------------------------- màu khoá ăn theo cảnh
def mau_theo_canh(frame_bgr, box):
    """chọn màu nhấn của chính cảnh, chỉnh sáng/tối cho đủ tương phản với nền sau chữ."""
    small = cv2.resize(frame_bgr, (90, 160), interpolation=cv2.INTER_AREA)
    lab = cv2.cvtColor(small, cv2.COLOR_BGR2LAB).reshape(-1, 3).astype(np.float32)
    crit = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 20, 1.0)
    _, lbl, cen = cv2.kmeans(lab, 6, None, crit, 3, cv2.KMEANS_PP_CENTERS)
    cnt = np.bincount(lbl.ravel(), minlength=6)
    x0, y0, x1, y1 = [int(v) for v in box]
    x0, y0 = max(0, x0), max(0, y0); x1, y1 = min(frame_bgr.shape[1], max(x0 + 2, x1)), min(frame_bgr.shape[0], max(y0 + 2, y1))
    bg = cv2.cvtColor(frame_bgr[y0:y1, x0:x1], cv2.COLOR_BGR2LAB).reshape(-1, 3).astype(np.float32).mean(0)
    best, bs = None, -1
    for c, n in zip(cen, cnt):
        chroma = math.hypot(c[1] - 128, c[2] - 128)
        if chroma < 14 or n < 0.04 * len(lbl): continue
        s = chroma * 1.5 + n / len(lbl) * 60
        if s > bs: best, bs = c.copy(), s
    # chọn trong BẢNG MÀU đo từ mẫu: gần sắc màu nhấn của cảnh nhất mà vẫn tương phản sáng ≥ 60 (L 0..255)
    # (mẫu: navy trên tường be, bạc hà trên tường xanh rêu, xanh rừng trong phòng sofa xanh, cam đào trong phòng gỗ)
    hue_c = math.atan2(best[2] - 128, best[1] - 128) if best is not None else None
    chon, cs = C.BANG_MAU['vang'], -1e9
    for ten, hx in C.BANG_MAU.items():
        if ten == 'bac': continue
        r, g, b = C.hex2rgb(hx)
        L = cv2.cvtColor(np.uint8([[[b, g, r]]]), cv2.COLOR_BGR2LAB)[0, 0].astype(np.float32)
        dl = abs(L[0] - bg[0])
        if dl < 60: continue
        s = dl * 0.3
        if hue_c is not None:
            hh = math.atan2(L[2] - 128, L[1] - 128)
            s += 100 * math.cos(hh - hue_c)
        if s > cs: chon, cs = hx, s
    return chon
