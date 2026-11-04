# -*- coding: utf-8 -*-
"""CTA cuối có NÚT + ICON (góp ý chủ dự án 04/11/2026: "cta nên có button, icon thay vì text đơn giản", bỏ SFX chói).

Nền = khung cuối của cảnh trước, làm mờ + tối (không cắt sang màn đen). Trên đó, giữa khung:
  avatar tròn (logo kênh, không có thì icon ghim bản đồ trên nền vàng) + vòng sóng
  tên kênh (chỉ khi có kenh.ten — không bịa) · dòng chính "THEO DÕI KÊNH" · dòng phụ (theo lời đọc)
  hàng 3 chip icon (ghim · tài liệu · chuông) — tắt bằng "bieu_tuong": false
  nút đỏ có chuông "THEO DÕI" (chuông rung) → bàn tay trượt vào, bấm (nút lún + sóng trắng)
  → nút xám "✓ ĐÃ THEO DÕI"; tay rút ra. KHÔNG có SFX.
Mọi hình vẽ vector bằng PIL (siêu lấy mẫu 4x), không tải ảnh ngoài.
"""
import math

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

import chung as C
import diem_nhan as DN
from chung import W, H, clamp, ramp, smooth, ease_out

DO_NUT = (229, 38, 44)
DO_SANG = (255, 92, 92)
XAM_NUT = (86, 95, 112)
SS = 4


def _o(size):
    S = size * SS
    return Image.new("RGBA", (S, S), (0, 0, 0, 0)), S


def _thu(im, size):
    return im.resize((size, size), Image.LANCZOS)


def icon_chuong(size, mau=C.TRANG):
    im, S = _o(size)
    d = ImageDraw.Draw(im)
    c = tuple(mau) + (255,)
    cx = S / 2
    d.ellipse((cx - 0.07 * S, 0.04 * S, cx + 0.07 * S, 0.18 * S), fill=c)
    d.pieslice((cx - 0.30 * S, 0.13 * S, cx + 0.30 * S, 0.73 * S), 180, 360, fill=c)
    d.polygon([(cx - 0.30 * S, 0.42 * S), (cx + 0.30 * S, 0.42 * S), (cx + 0.40 * S, 0.74 * S), (cx - 0.40 * S, 0.74 * S)],
              fill=c)
    d.rounded_rectangle((cx - 0.45 * S, 0.70 * S, cx + 0.45 * S, 0.80 * S), radius=0.05 * S, fill=c)
    d.ellipse((cx - 0.10 * S, 0.78 * S, cx + 0.10 * S, 0.96 * S), fill=c)
    return _thu(im, size)


def icon_tick(size, mau=C.TRANG):
    im, S = _o(size)
    d = ImageDraw.Draw(im)
    c = tuple(mau) + (255,)
    pts = [(0.16 * S, 0.53 * S), (0.41 * S, 0.77 * S), (0.86 * S, 0.27 * S)]
    wd = int(0.14 * S)
    d.line(pts, fill=c, width=wd, joint="curve")
    for x, y in (pts[0], pts[-1]):
        d.ellipse((x - wd / 2, y - wd / 2, x + wd / 2, y + wd / 2), fill=c)
    return _thu(im, size)


def icon_ghim(size, mau=C.NAVY, lo=C.VANG):
    im, S = _o(size)
    d = ImageDraw.Draw(im)
    c = tuple(mau) + (255,)
    cx, cy, r = S / 2, 0.38 * S, 0.30 * S
    d.polygon([(cx - r * 0.86, cy + r * 0.5), (cx + r * 0.86, cy + r * 0.5), (cx, 0.96 * S)], fill=c)
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=c)
    d.ellipse((cx - r * 0.42, cy - r * 0.42, cx + r * 0.42, cy + r * 0.42), fill=tuple(lo) + (255,))
    return _thu(im, size)


def icon_tai_lieu(size, mau=C.TRANG):
    im, S = _o(size)
    d = ImageDraw.Draw(im)
    c = tuple(mau) + (255,)
    x0, y0, x1, y1, g = 0.18 * S, 0.06 * S, 0.82 * S, 0.94 * S, 0.22 * S
    d.polygon([(x0, y0), (x1 - g, y0), (x1, y0 + g), (x1, y1), (x0, y1)], fill=c)
    d.polygon([(x1 - g, y0), (x1 - g, y0 + g), (x1, y0 + g)], fill=(150, 165, 190, 255))
    for k in range(4):
        y = 0.40 * S + k * 0.13 * S
        d.rounded_rectangle((0.28 * S, y, (0.72 if k < 3 else 0.55) * S, y + 0.055 * S), radius=0.02 * S,
                            fill=(120, 135, 165, 255))
    return _thu(im, size)


def ban_tay(size=240):
    """bàn tay trỏ vector (trắng viền tối, tay áo xanh) → (ảnh RGBA 2size x 2size, ĐẦU NGÓN TRỎ ở tâm ảnh), nghiêng 18°"""
    S = size * SS
    m = Image.new("L", (S, S), 0)
    d = ImageDraw.Draw(m)
    d.rounded_rectangle((0.31 * S, 0.02 * S, 0.49 * S, 0.62 * S), radius=0.09 * S, fill=255)
    d.rounded_rectangle((0.46 * S, 0.33 * S, 0.63 * S, 0.62 * S), radius=0.085 * S, fill=255)
    d.rounded_rectangle((0.60 * S, 0.38 * S, 0.76 * S, 0.65 * S), radius=0.08 * S, fill=255)
    d.rounded_rectangle((0.73 * S, 0.44 * S, 0.87 * S, 0.68 * S), radius=0.07 * S, fill=255)
    d.rounded_rectangle((0.25 * S, 0.46 * S, 0.87 * S, 0.90 * S), radius=0.17 * S, fill=255)
    th = Image.new("L", (S, S), 0)
    ImageDraw.Draw(th).rounded_rectangle((0.10 * S, 0.50 * S, 0.40 * S, 0.66 * S), radius=0.08 * S, fill=255)
    th = th.rotate(-28, center=(0.36 * S, 0.62 * S), resample=Image.BICUBIC)
    m = Image.fromarray(np.maximum(np.asarray(m), np.asarray(th)))
    ao = Image.new("L", (S, S), 0)
    ImageDraw.Draw(ao).rounded_rectangle((0.27 * S, 0.84 * S, 0.85 * S, 1.0 * S), radius=0.04 * S, fill=255)
    tong = Image.fromarray(np.maximum(np.asarray(m), np.asarray(ao)))
    vien = tong.filter(ImageFilter.MaxFilter(int(0.035 * S) | 1))
    im = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    im.paste((24, 30, 44, 255), (0, 0), vien)
    im.paste((255, 255, 255, 255), (0, 0), m)
    im.paste((44, 96, 210, 255), (0, 0), ao)
    dd = ImageDraw.Draw(im)
    for x in (0.475, 0.615, 0.745):
        dd.line([(x * S, 0.42 * S), (x * S, 0.60 * S)], fill=(196, 204, 218, 255), width=int(0.012 * S))
    dd.arc((0.33 * S, 0.06 * S, 0.47 * S, 0.20 * S), 200, 340, fill=(206, 214, 226, 255), width=int(0.012 * S))
    im = im.resize((size, size), Image.LANCZOS)
    can = Image.new("RGBA", (2 * size, 2 * size), (0, 0, 0, 0))
    can.alpha_composite(im, (int(size - 0.40 * size), int(size - 0.03 * size)))
    sh = can.copy()
    sh.paste((0, 0, 0, 255), (0, 0), can.getchannel("A"))
    sh.putalpha(can.getchannel("A").point(lambda v: int(v * 0.45)))
    sh = sh.filter(ImageFilter.GaussianBlur(9))
    out = Image.new("RGBA", can.size, (0, 0, 0, 0))
    out.alpha_composite(sh, (10, 14))
    out.alpha_composite(can)
    return out.rotate(18, center=(size, size), resample=Image.BICUBIC)


def _chip(icon, nhan):
    t = C.chu(nhan, "semi", 28, fill=C.TRANG)
    w, h = 26 + icon.width + 12 + t.width + 28, 84
    box = C.hop_bo((w, h), h // 2, (255, 255, 255, 34), vien=(255, 255, 255, 110), vien_w=2)
    box.alpha_composite(icon, (26, (h - icon.height) // 2))
    box.alpha_composite(t, (26 + icon.width + 12, (h - t.height) // 2))
    return box


def _nut(mau, chu, rong=560, cao=128, icon=None, cho_icon=0):
    box = Image.new("RGBA", (rong, cao), (0, 0, 0, 0))
    d = ImageDraw.Draw(box)
    d.rounded_rectangle((0, 0, rong - 1, cao - 1), radius=cao // 2, fill=tuple(mau) + (255,))
    bong = Image.new("RGBA", (rong, cao), (0, 0, 0, 0))
    ImageDraw.Draw(bong).rounded_rectangle((10, 6, rong - 11, cao // 2), radius=cao // 3, fill=(255, 255, 255, 46))
    box.alpha_composite(bong)
    t = C.chu(chu, "black", 52, fill=C.TRANG, shadow=(0, 3, 4, 0.35), track=2)
    iw = icon.width if icon is not None else cho_icon
    gap = 22 if iw else 0
    x = (rong - (iw + gap + t.width)) // 2
    if icon is not None:
        box.alpha_composite(icon, (x, (cao - icon.height) // 2))
    box.alpha_composite(t, (x + iw + gap, (cao - t.height) // 2))
    return box, x + iw / 2


class CtaNut:
    def __init__(self, kenh, dur, it=None, tim_file=None):
        it = it or {}
        kenh = kenh or {}
        self.dur = dur
        self.bg = None
        dong = it.get("dong") or ["Theo dõi kênh", "để cập nhật thông tin mới nhất"]
        ten = (kenh.get("ten") or "").strip()
        # avatar
        D_ = 196
        av = Image.new("RGBA", (D_ + 16, D_ + 16), (0, 0, 0, 0))
        dv = ImageDraw.Draw(av)
        dv.ellipse((0, 0, D_ + 15, D_ + 15), fill=(255, 255, 255, 255))
        logo = None
        if kenh.get("logo") and tim_file:
            try:
                logo = C.cover(Image.open(tim_file(kenh["logo"])).convert("RGBA"), D_, D_)
            except SystemExit:
                logo = None
            except Exception:
                logo = None
        if logo is None:
            nen = Image.new("RGBA", (D_, D_), tuple(C.VANG) + (255,))
            ic = icon_ghim(118, C.NAVY, C.VANG)
            nen.alpha_composite(ic, ((D_ - 118) // 2, (D_ - 118) // 2 - 4))
            logo = nen
        mk = Image.new("L", (D_, D_), 0)
        ImageDraw.Draw(mk).ellipse((0, 0, D_ - 1, D_ - 1), fill=255)
        logo.putalpha(mk)
        av.alpha_composite(logo, (8, 8))
        sh, p = C.bong_do(av, blur=14, alpha=0.55)
        a2 = Image.new("RGBA", (av.width + 2 * p, av.height + 2 * p), (0, 0, 0, 0))
        a2.alpha_composite(sh, (0, 8))
        a2.alpha_composite(av, (p, p))
        self.avatar = a2
        # chữ
        self.ten = np.asarray(C.chu(ten.upper(), "black", 46, fill=C.VANG, shadow=(0, 3, 5, 0.5), track=2)) if ten else None
        self.tit = np.asarray(C.chu(dong[0].upper(), "black", 70, fill=C.TRANG, shadow=(0, 4, 6, 0.5), track=1))
        self.phu = np.asarray(C.chu(dong[1], "semi", 36, fill=(214, 224, 240))) if len(dong) > 1 and dong[1] else None
        # chip icon
        self.chips = []
        if it.get("bieu_tuong", True):
            nhan = it.get("nhan_bieu_tuong") or ["Bản đồ", "Quy hoạch", "Tin mới"]
            icons = [icon_ghim(46, C.VANG, C.NAVY), icon_tai_lieu(46), icon_chuong(44, C.VANG)]
            self.chips = [_chip(ic, n) for ic, n in zip(icons, nhan)]
        # nút
        self.chuong = icon_chuong(62)
        self.nut_do, self.x_chuong = _nut(DO_NUT, "THEO DÕI", cho_icon=62)
        self.nut_xam, _ = _nut(XAM_NUT, "ĐÃ THEO DÕI", icon=icon_tick(54))
        glow = Image.new("RGBA", (560 + 80, 128 + 80), (0, 0, 0, 0))
        ImageDraw.Draw(glow).rounded_rectangle((40, 40, 599, 167), radius=64, fill=tuple(DO_SANG) + (255,))
        self.glow = np.asarray(glow.filter(ImageFilter.GaussianBlur(18)))
        self.tay = ban_tay(250)
        # bố cục (y tâm)
        self.y_av = 640
        y = 760
        self.y_ten = None
        if self.ten is not None:
            self.y_ten = y + self.ten.shape[0] / 2
            y += self.ten.shape[0] + 16
        self.y_tit = y + self.tit.shape[0] / 2
        y += self.tit.shape[0] + 10
        self.y_phu = None
        if self.phu is not None:
            self.y_phu = y + self.phu.shape[0] / 2
            y += self.phu.shape[0] + 34
        self.y_chip = None
        if self.chips:
            self.y_chip = y + 42
            y += 84 + 40
        self.y_nut = y + 64
        y_cuoi = y + 128 + 52
        # thẻ nền
        ch = int(y_cuoi - self.y_av)
        the = C.hop_bo((940, ch), 36, tuple(C.NAVY) + (232,), vien=tuple(C.NAVY_VIEN) + (255,), vien_w=3)
        ImageDraw.Draw(the).rounded_rectangle((40, 0, 900, 8), radius=4, fill=tuple(C.VANG) + (255,))
        sh, p = C.bong_do(the, blur=26, alpha=0.6)
        t2 = Image.new("RGBA", (the.width + 2 * p, the.height + 2 * p), (0, 0, 0, 0))
        t2.alpha_composite(sh, (0, 12))
        t2.alpha_composite(the, (p, p))
        self.the, self.p_the = np.asarray(t2), p

    def dat_nen(self, fr):
        if fr is None:
            g = np.zeros((H, W, 3), np.uint8)
            g[:] = C.NAVY_TOI
            self.bg = g
            return
        b = cv2.GaussianBlur(fr, (0, 0), 22)
        navy = np.array(C.NAVY_TOI, np.float32)
        self.bg = (b.astype(np.float32) * 0.42 + navy * 0.35).clip(0, 255).astype(np.uint8)

    def _giua(self, frame, arr, cy, a, dy=0.0):
        if arr is None or a <= 0.003:
            return
        C.dan(frame, arr, (W - arr.shape[1]) / 2, cy - arr.shape[0] / 2 + dy, a)

    def ve(self, frame, tl):
        if self.bg is None:
            self.dat_nen(None)
        frame[:] = self.bg
        # thẻ
        a = ease_out(ramp(tl, 0.0, 0.35))
        dy = 70 * (1 - a)
        C.dan(frame, self.the, (W - self.the.shape[1]) / 2, self.y_av - self.p_the + dy, a)
        # avatar + sóng
        u = ramp(tl, 0.12, 0.4)
        if u > 0:
            DN.ve_song(frame, W / 2, self.y_av + dy, tl - 0.6, C.TRANG, r0=104, r1=150, chu_ky=1.6, so_vong=2, day=3,
                       alpha=0.6)
            s = max(0.05, DN.back_out(u))
            C.dan_giua(frame, self.avatar, W / 2, self.y_av + dy, clamp(u * 3), s)
        # chữ
        if self.y_ten is not None:
            v = ease_out(ramp(tl, 0.24, 0.3))
            self._giua(frame, self.ten, self.y_ten, v, dy + 18 * (1 - v))
        v = ease_out(ramp(tl, 0.30, 0.3))
        self._giua(frame, self.tit, self.y_tit, v, dy + 18 * (1 - v))
        if self.y_phu is not None:
            v = ease_out(ramp(tl, 0.38, 0.3))
            self._giua(frame, self.phu, self.y_phu, v, dy + 18 * (1 - v))
        # chip icon
        if self.chips:
            gap = 18
            tong = sum(c.width for c in self.chips) + gap * (len(self.chips) - 1)
            x = (W - tong) / 2
            for i, c in enumerate(self.chips):
                v = ramp(tl, 0.46 + 0.08 * i, 0.3)
                if v > 0:
                    C.dan_giua(frame, c, x + c.width / 2, self.y_chip + dy, clamp(v * 3), max(0.05, DN.back_out(v)))
                x += c.width + gap
        # nút + chuông + tay
        T_BAM, T_DOI = 1.30, 1.40
        v = ramp(tl, 0.58, 0.35)
        if v <= 0:
            return
        cy = self.y_nut + dy
        nhan = 1.0
        if T_BAM <= tl < T_BAM + 0.2:
            nhan = 1 - 0.06 * math.sin(math.pi * (tl - T_BAM) / 0.2)
        s = max(0.05, DN.back_out(v)) * nhan
        if tl < T_DOI:
            nhip = 0.5 + 0.5 * math.sin(2 * math.pi * tl / 0.8)
            C.dan_giua(frame, self.glow, W / 2, cy, clamp(v) * (0.35 + 0.35 * nhip))
            C.dan_giua(frame, self.nut_do, W / 2, cy, clamp(v * 3), s)
            goc = 0.0
            if 0.9 <= tl < T_BAM:
                k = tl - 0.9
                goc = 22 * math.sin(2 * math.pi * k / 0.16) * math.exp(-k * 3.0)
            ch = self.chuong.rotate(goc, center=(31, 6), resample=Image.BICUBIC) if goc else self.chuong
            xc = W / 2 + (self.x_chuong - self.nut_do.width / 2) * s
            C.dan_giua(frame, ch, xc, cy, clamp(v * 3), s)
        else:
            w2 = clamp((tl - T_DOI) / 0.12)
            C.dan_giua(frame, self.nut_do, W / 2, cy, 1 - w2, s)
            C.dan_giua(frame, self.nut_xam, W / 2, cy, w2, s * (0.92 + 0.08 * DN.back_out(w2)))
        # bàn tay: trượt vào 0,85–1,25 · bấm 1,30 · rút ra 1,75–2,15
        if 0.85 <= tl <= 2.2:
            dx, dy_t = W / 2 + 120, cy + 34
            if tl < 1.25:
                k = ease_out((tl - 0.85) / 0.4)
                ox, oy, at = 300 * (1 - k), 440 * (1 - k), clamp((tl - 0.85) / 0.15)
            elif tl < 1.75:
                ox, oy, at = 0.0, 0.0, 1.0
            else:
                k = smooth((tl - 1.75) / 0.4)
                ox, oy, at = 170 * k, 280 * k, 1 - k
            sc = 1.0
            if T_BAM - 0.05 <= tl < T_BAM + 0.2:
                sc = 1 - 0.08 * math.sin(math.pi * (tl - T_BAM + 0.05) / 0.25)
            if T_BAM <= tl < T_BAM + 0.6:
                DN.ve_song(frame, dx, dy_t, tl - T_BAM, C.TRANG, r0=18, r1=150, chu_ky=0.6, so_vong=1, day=5, lap=False)
            C.dan_giua(frame, self.tay, dx + ox, dy_t + oy, at, sc)
