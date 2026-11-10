# -*- coding: utf-8 -*-
"""Lớp HUD công nghệ đè mờ (mẫu từ 9,8 s tới hết): số rỗng viền to kiểu 7 đoạn, chuỗi dữ liệu <35468>,
mũi tên '>' trắng nhấp nháy theo móc đơn, vạch dọc mảnh, ngoặc vuông nhỏ. Đổi trạng thái theo nửa nhịp,
xuất hiện / tắt đúng móc đơn. Chỉ ở MÉP khung (né giữa = xe, né dải chữ tiêu đề)."""
import math
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont
import chung as C

# 7 đoạn: a trên, b phải-trên, c phải-dưới, d dưới, e trái-dưới, f trái-trên, g giữa
SEG = {'0': 'abcdef', '1': 'bc', '2': 'abged', '3': 'abgcd', '4': 'fgbc', '5': 'afgcd', '6': 'afgedc', '7': 'abc',
       '8': 'abcdefg', '9': 'abcdfg'}


def ve_so_rong(h, so, net):
    """Trả mặt nạ L (uint8) của chữ số rỗng viền vuông bo (như số '3', '4', '8' trong mẫu)."""
    w = int(h * 0.56)
    pad = net * 3
    m = Image.new('L', (w + 2 * pad, h + 2 * pad), 0)
    d = ImageDraw.Draw(m)
    x0, y0, x1, y1 = pad, pad, pad + w, pad + h
    ym = (y0 + y1) // 2
    P = {'a': [(x0, y0), (x1, y0)], 'b': [(x1, y0), (x1, ym)], 'c': [(x1, ym), (x1, y1)], 'd': [(x0, y1), (x1, y1)],
         'e': [(x0, ym), (x0, y1)], 'f': [(x0, y0), (x0, ym)], 'g': [(x0, ym), (x1, ym)]}
    day = max(4, int(h * 0.075))
    for s in SEG.get(so, '8'):
        d.line(P[s], fill=255, width=day)
        for p in P[s]:
            d.ellipse([p[0] - day / 2, p[1] - day / 2, p[0] + day / 2, p[1] + day / 2], fill=255)
    rong = day - 2 * net
    if rong > 0:
        for s in SEG.get(so, '8'):
            d.line(P[s], fill=0, width=rong)
            for p in P[s]:
                d.ellipse([p[0] - rong / 2, p[1] - rong / 2, p[0] + rong / 2, p[1] + rong / 2], fill=0)
    return np.array(m)


class Hud:
    def __init__(self, W, H, phach_s, t_goc, seed=7, vung_cam=None):
        self.W, self.H = W, H
        self.P = phach_s            # 1 phách
        self.t_goc = t_goc          # mốc lưới nửa nhịp
        self.seed = seed
        self.font = ImageFont.truetype(C.font_hud(), max(12, int(C.HUD['chu_cao'] * min(W, H) * 1.25)))
        self.font_mt = ImageFont.truetype(C.font('BarlowCondensed-ExtraBold.ttf'), max(14, int(0.05 * min(W, H))))
        self.vung_cam = vung_cam or []   # [(x0,y0,x1,y1)] tỉ lệ — không đặt HUD vào
        self.cache = {}

    def _vi_tri(self, rng, w, h, vung):
        W, H = self.W, self.H
        for _ in range(30):
            if vung == 'day':
                x = rng.uniform(0.04, 0.96) * W - w / 2; y = rng.uniform(0.80, 0.93) * H - h / 2
            elif vung == 'phai':
                x = rng.uniform(0.74, 0.93) * W - w / 2; y = rng.uniform(0.35, 0.85) * H - h / 2
            else:
                x = rng.uniform(0.04, 0.24) * W - w / 2; y = rng.uniform(0.35, 0.85) * H - h / 2
            x = min(max(4, x), W - w - 4); y = min(max(4, y), H - h - 4)
            ok = True
            for (a, b, c, d) in self.vung_cam:
                if not (x + w < a * W or x > c * W or y + h < b * H or y > d * H):
                    ok = False; break
            if ok:
                return int(x), int(y)
        return int(x), int(y)

    def _trang_thai(self, o, m):
        """o = chỉ số nửa nhịp, m = móc đơn trong nửa nhịp (0..3)."""
        key = (o, m)
        if key in self.cache:
            return self.cache[key]
        if len(self.cache) > 24:
            self.cache.clear()
        W, H = self.W, self.H
        rng = np.random.default_rng(self.seed * 1000 + o)
        lay = Image.new('L', (W, H), 0)
        d = ImageDraw.Draw(lay)
        bong = Image.new('L', (W, H), 0)
        db = ImageDraw.Draw(bong)
        doc = H > W
        # 1) số rỗng to — đổi mỗi nhịp, bên trái / phải xen kẽ
        nhip = o // 2
        r2 = np.random.default_rng(self.seed * 77 + nhip)
        if r2.random() < 0.85:
            h = int(C.HUD['so_lon_cao']['9:16' if doc else '16:9'] * H)
            so = str(r2.integers(0, 10))
            mk = ve_so_rong(h, so, max(2, int(h * C.HUD['so_net'])))
            ben = 'trai' if nhip % 2 == 0 else 'phai'
            if doc:
                x = int((r2.uniform(0.02, 0.08) if ben == 'trai' else r2.uniform(0.62, 0.70)) * W)
                y = int(r2.uniform(0.22, 0.48) * H)
            else:
                x = int((r2.uniform(0.04, 0.16) if ben == 'trai' else r2.uniform(0.70, 0.84)) * W)
                y = int(r2.uniform(0.2, 0.42) * H)
            hh, ww = mk.shape
            xa, ya = max(0, x), max(0, y)
            xb, yb = min(W, x + ww), min(H, y + hh)
            sub = np.array(lay)
            sub[ya:yb, xa:xb] = np.maximum(sub[ya:yb, xa:xb], (mk[ya - y:yb - y, xa - x:xb - x].astype(np.float32) * C.HUD['so_lon_alpha']).astype(np.uint8))
            lay = Image.fromarray(sub); d = ImageDraw.Draw(lay)
        # 2) chuỗi dữ liệu — 2–3 chuỗi, mỗi chuỗi hiện từ móc đơn riêng
        for j in range(int(rng.integers(2, 4))):
            m_vao = int(rng.integers(0, 3))
            if m < m_vao:
                continue
            s = C.HUD['chuoi'][int(rng.integers(0, len(C.HUD['chuoi'])))]
            bb = d.textbbox((0, 0), s, font=self.font)
            w, h = bb[2] - bb[0], bb[3] - bb[1]
            x, y = self._vi_tri(rng, w, h, ['day', 'phai', 'trai'][j % 3])
            x += int((m - m_vao) * 0.006 * W) * (1 if j % 2 else -1)
            db.text((x + 2, y + 2), s, font=self.font, fill=255)
            d.text((x, y), s, font=self.font, fill=int(255 * C.HUD['chu_alpha']))
            if rng.random() < 0.5:   # vạch tiến độ nhỏ dưới chuỗi
                d.line([(x, y + h + 8), (x + int(w * rng.uniform(0.3, 0.9)), y + h + 8)], fill=int(255 * C.HUD['chu_alpha']), width=2)
            if rng.random() < 0.4:   # ngoặc vuông
                q = max(8, int(0.012 * H))
                d.rectangle([x - 3 * q, y, x - 2 * q, y + h], outline=int(255 * C.HUD['chu_alpha']), width=2)
        # 3) mũi tên '>' nhấp nháy theo móc đơn
        for j in range(2):
            if (m + j) % 2:
                continue
            x, y = self._vi_tri(rng, 30, 40, ['phai', 'day'][j])
            db.text((x + 2, y + 2), '>', font=self.font_mt, fill=255)
            d.text((x, y), '>', font=self.font_mt, fill=int(255 * C.HUD['mui_ten_alpha']))
        # 4) vạch dọc mảnh
        if rng.random() < 0.7:
            x = int(rng.uniform(0.78, 0.92) * W)
            y0 = int(rng.uniform(0, 0.3) * H); y1 = int(rng.uniform(0.7, 1.0) * H)
            d.line([(x, y0), (x, y1)], fill=int(255 * C.HUD['vach_alpha']), width=2)
        a = np.array(lay).astype(np.float32) / 255.0
        b = cv2.GaussianBlur(np.array(bong).astype(np.float32) / 255.0, (0, 0), 2.0) * C.HUD['bong']
        self.cache[key] = (a, b)
        return self.cache[key]

    def ve(self, img, t, muc=1.0):
        if muc <= 0.01:
            return img
        nua = self.P * 2
        o = int(math.floor((t - self.t_goc) / nua))
        m = int(math.floor(((t - self.t_goc) % nua) / (self.P / 2)))
        a, b = self._trang_thai(o, m)
        a = a * muc; b = b * muc
        f = img.astype(np.float32)
        f = f * (1 - b[..., None])
        f = f + (255 - f) * a[..., None]
        return np.clip(f, 0, 255).astype(np.uint8)
