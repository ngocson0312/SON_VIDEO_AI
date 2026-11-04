# -*- coding: utf-8 -*-
"""Bộ ĐỘNG TÁC CHUẨN của template bản đồ. Mỗi động tác = 1 lớp, vẽ ở mặt đất (ve_dat) và/hoặc màn hình (ve_man).

Mốc thời gian trong kịch bản đều là GIÂY TUYỆT ĐỐI của audio.
"""
import math
import os
import random

import numpy as np
from PIL import Image

from . import ve
from . import dia_ly as DL
from .camera import ease, ease_in_out_cubic

VANG = (255, 212, 0)
TRANG = (255, 255, 255)
CAM = (255, 120, 20)
XANH_NEON = (70, 200, 255)


def _ramp(t, t0, dur):
    if dur <= 0:
        return 1.0 if t >= t0 else 0.0
    return max(0.0, min(1.0, (t - t0) / dur))


class DongTac:
    LOAI = "?"
    BEN_VUNG = True      # tồn tại tới `den` (mặc định hết video)
    LOP_DAT = False      # vẽ ở mặt đất
    LOP_MAN = False      # vẽ ở màn hình
    VAO, RA = 0.4, 0.3   # thời gian hiện / tan

    def __init__(self, d, t_end):
        self.d = d
        self.id = d.get("id") or ("%s_%s" % (self.LOAI, id(self)))
        self.t0 = float(d.get("luc", 0.0))
        self.t1 = float(d["den"]) if d.get("den") is not None else (t_end if self.BEN_VUNG else self.t0 + self.thoi_luong())
        self.t_end = t_end
        self.loi = None

    def thoi_luong(self):
        return 1.5

    def hoat_dong(self, t):
        return self.t0 <= t <= self.t1 + self.RA

    def alpha(self, t):
        a = _ramp(t, self.t0, self.VAO)
        if t > self.t1:
            a *= 1 - _ramp(t, self.t1, self.RA)
        return a

    def sfx(self):
        return []

    def ve_dat(self, c):
        pass

    def ve_man(self, c):
        pass

    def diem(self, c, ref):
        return c.diem(ref)


# ---------- tô nước / bang ----------
class ToNuoc(DongTac):
    LOAI = "to_nuoc"
    LOP_DAT = True
    VAO = 0.6

    def __init__(self, d, t_end):
        super().__init__(d, t_end)
        self.ref = d.get("nuoc") or d.get("tai")
        self.co_flag = bool(d.get("co"))
        self.mau = ve_mau(d.get("mau"), (255, 74, 31))
        self._co_img = None

    def ve_dat(self, c):
        rec = c.vung(self.ref)
        if not rec:
            return
        vong = DL.vong_den_px(rec["vong"], c.z, c.x0, c.y0, c.rong, c.cao)
        if not vong:
            return
        co = None
        if self.co_flag:
            if self._co_img is None:
                p = c.co_nuoc(self.ref)
                self._co_img = Image.open(p).convert("RGBA") if p and os.path.exists(p) else False
            co = self._co_img or None
        allp = np.concatenate(vong, 0)
        bw = float(allp[:, 0].max() - allp[:, 0].min())
        khoi = int(max(2, min(16, bw * 0.012)))
        img, (ox, oy) = ve.to_vung(vong, c.rong, c.cao, mau=None if co is not None else self.mau, co=co,
                                   day_khoi=khoi, day_vien=max(1, int(bw * 0.004)), alpha=self.alpha(c.t))
        if img is not None:
            ve.dan_lop(c.ground, img, ox, oy)


# ---------- nhãn chữ trên mặt đất ----------
class Nhan(DongTac):
    LOAI = "nhan"
    LOP_DAT = True

    def __init__(self, d, t_end):
        super().__init__(d, t_end)
        self.ref = d.get("tai") or d.get("nuoc")
        self.chu = str(d.get("chu") or "")
        self.kieu = d.get("kieu") or "viet_tay"
        self.mau = ve_mau(d.get("mau"), XANH_NEON if self.kieu == "neon" else (VANG if self.kieu == "doc" else TRANG))
        self.co_km = d.get("co_km")
        self.lech = d.get("lech_km") or [0, 0]
        self._cache = {}

    def _anh(self, c, px):
        px = max(10, int(round(px / 4.0)) * 4)
        if px not in self._cache:
            if self.kieu == "neon":
                img = ve.chu_neon(self.chu, c.font_tay, px, self.mau, dam=True)
            elif self.kieu == "doc":
                img = ve.chu_anh(self.chu, c.font_sub, px, self.mau, vien=max(1, px // 14), bong=px // 8)
                img = img.rotate(90, expand=True)
            else:
                img = ve.chu_anh(self.chu, c.font_tay, px, self.mau, vien=0, bong=max(2, px // 9),
                                 mau_bong=(0, 0, 0, 200), dam=True)
            if len(self._cache) > 12:
                self._cache.clear()
            self._cache[px] = img
        return self._cache[px]

    def ve_dat(self, c):
        p = self.diem(c, self.ref)
        if not p:
            return
        lon, lat = p
        if self.co_km is None:
            self.co_km = c.rong_km_hien() * (0.085 if self.kieu != "doc" else 0.07)
        px = c.km_px_dat(self.co_km, lat)
        if px < 6:
            return
        img = self._anh(c, px)
        x, y = c.px_dat(lon + self.lech[0] / max(1e-6, (111.0 * math.cos(math.radians(lat)))),
                        lat + self.lech[1] / 111.0)
        a = self.alpha(c.t)
        if self.kieu == "doc":
            # chữ dọc đặt bên trái điểm, chân chữ ngang điểm
            ve.dan_lop(c.ground, img, x - img.size[0] * 1.15, y - img.size[1] * 0.9, a)
        else:
            # hiện lên có co giãn nhẹ
            s = 0.92 + 0.08 * ease(_ramp(c.t, self.t0, self.VAO))
            if s < 0.999:
                img = img.resize((max(2, int(img.size[0] * s)), max(2, int(img.size[1] * s))), Image.BILINEAR)
            ve.dan_lop(c.ground, img, x - img.size[0] / 2, y - img.size[1] / 2, a)


class ChuNeon(Nhan):
    LOAI = "chu_neon"

    def __init__(self, d, t_end):
        d = dict(d)
        d.setdefault("kieu", "neon")
        super().__init__(d, t_end)


# ---------- ghim thành phố (màn hình) ----------
class Ghim(DongTac):
    LOAI = "ghim"
    LOP_MAN = True
    VAO = 0.35

    def __init__(self, d, t_end):
        super().__init__(d, t_end)
        self.ref = d.get("tai")
        self.chu = str(d.get("chu") or c_ten(d.get("tai")))
        self._img = None

    def sfx(self):
        return [("hien", self.t0)]

    def ve_man(self, c):
        p = self.diem(c, self.ref)
        if not p:
            return
        sx, sy, zc = c.man(*p)
        if zc <= 0:
            return
        if self._img is None:
            self._img = ve.rgba_pil_sang_bgra(ve.bong_bong(self.chu, c.font_co, int(c.H * 0.026)))
        s = 0.6 + 0.4 * ease(_ramp(c.t, self.t0, self.VAO))
        img = ve.bien_hinh(self._img, self._img.shape[0] * s) if s < 0.999 else self._img
        ve.dan_np(c.frame, img, sx, sy, neo=(0.5, 1.0), alpha=self.alpha(c.t))


# ---------- vật thể ----------
class VatThe(DongTac):
    LOAI = "vat_the"
    LOP_MAN = True
    VAO = 0.45

    def __init__(self, d, t_end):
        super().__init__(d, t_end)
        self.ref = d.get("tai")
        self.vat = d.get("vat") or "ten_lua"
        self.co = d.get("co")              # tỉ lệ chiều cao màn hình nếu co_dinh, hoặc km
        self.co_dinh = bool(d.get("co_dinh", False))
        self.co_km = d.get("co_km")
        self.hieu_ung = d.get("hieu_ung") or "noi_len"
        self.lech = d.get("lech") or [0.0, 0.0]   # phần của chiều cao màn hình
        self.goc = float(d.get("goc", 0.0))
        self.nam_dat = bool(d.get("nam_dat", False))
        self.neo = tuple(d.get("neo") or ((0.5, 0.5) if self.nam_dat else (0.5, 0.85)))
        self.huong_vao = d.get("tu_huong") or "tren"
        self._sp = None
        if self.nam_dat:
            self.LOP_DAT, self.LOP_MAN = True, False

    def sfx(self):
        return [("hien", self.t0)]

    def _sprite(self, c):
        if self._sp is None:
            sp = c.sprite(self.vat)
            self._sp = sp if isinstance(sp, np.ndarray) else False
        return self._sp if isinstance(self._sp, np.ndarray) else None

    def ve_dat(self, c):
        sp = self._sprite(c)
        p = self.diem(c, self.ref)
        if sp is None or not p:
            return
        lon, lat = p
        if self.co_km is None:
            self.co_km = (self.co or 0.09) * c.rong_km_hien() if not self.co_dinh else 0.09 * c.rong_km_hien()
        px = c.km_px_dat(self.co_km, lat)
        if px < 4:
            return
        x, y = c.px_dat(lon, lat)
        a = self.alpha(c.t)
        s = 0.8 + 0.2 * ease(_ramp(c.t, self.t0, self.VAO))
        img = ve.bien_hinh(sp, px * s, self.goc)
        pil = Image.fromarray(img, "RGBA")
        ve.dan_lop(c.ground, pil, x - img.shape[1] * self.neo[0], y - img.shape[0] * self.neo[1], a)

    def ve_man(self, c):
        sp = self._sprite(c)
        p = self.diem(c, self.ref)
        if sp is None or not p:
            return
        lon, lat = p
        sx, sy, zc = c.man(lon, lat)
        if zc <= 0:
            return
        if self.co_dinh:
            px = (self.co or 0.28) * c.H
        else:
            if self.co_km is None:
                self.co_km = (self.co or 0.16) * c.rong_km_hien()
            px = c.km_px_man(self.co_km, lon, lat)
        if px < 4:
            return
        a = self.alpha(c.t)
        pin = ease_in_out_cubic(_ramp(c.t, self.t0, self.VAO + 0.15))
        dx, dy = self.lech[0] * c.H, self.lech[1] * c.H
        if self.hieu_ung == "noi_len":
            dy += (1 - pin) * px * 0.35
        elif self.hieu_ung == "truot_vao":
            kc = (1 - pin)
            if self.huong_vao == "tren":
                dy -= kc * (sy + px)
            elif self.huong_vao == "trai":
                dx -= kc * (sx + px)
            elif self.huong_vao == "phai":
                dx += kc * (c.W - sx + px)
            else:
                dy += kc * (c.H - sy + px)
        elif self.hieu_ung == "hien":
            px = px * (0.85 + 0.15 * pin)
        img = ve.bien_hinh(ve.rgba_sang_bgra(sp), px, self.goc)
        ve.dan_np(c.frame, img, sx + dx, sy + dy, neo=self.neo, alpha=a)


# ---------- người (ảnh cắt nền) ----------
class Nguoi(DongTac):
    LOAI = "nguoi"
    LOP_MAN = True
    VAO = 0.4

    def __init__(self, d, t_end):
        super().__init__(d, t_end)
        self.ref = d.get("tai")
        self.ten = d.get("ten") or ""
        self.co = float(d.get("co", 0.42))
        self.lech = d.get("lech") or [0.0, 0.0]
        self.vi_tri = d.get("vi_tri")  # "giua" | "trai" | "phai" | None (neo theo điểm)
        self._sp = None

    def sfx(self):
        return [("hien", self.t0)]

    def ve_man(self, c):
        if self._sp is None:
            p = c.anh_nguoi(self.ten)
            sp0 = ve.nap_sprite(p) if p else None
            self._sp = sp0 if isinstance(sp0, np.ndarray) else False
        if not isinstance(self._sp, np.ndarray):
            return
        sp = self._sp
        if self.vi_tri in ("giua", "trai", "phai"):
            sx = {"giua": 0.5, "trai": 0.28, "phai": 0.72}[self.vi_tri] * c.W
            sy = 0.5 * c.H
        else:
            p = self.diem(c, self.ref)
            if not p:
                return
            sx, sy, zc = c.man(*p)
            if zc <= 0:
                return
        px = self.co * c.H
        pin = ease_in_out_cubic(_ramp(c.t, self.t0, self.VAO))
        img = ve.bien_hinh(ve.rgba_sang_bgra(sp), px * (0.86 + 0.14 * pin))
        h, w = img.shape[:2]
        cx = sx + self.lech[0] * c.H
        cy = sy + self.lech[1] * c.H
        cx = min(max(cx, w * 0.5 + 10), c.W - w * 0.5 - 10)
        cy = min(max(cy, h * 0.5 + 10), c.H * 0.86 - h * 0.5)
        ve.dan_np(c.frame, img, cx, cy, neo=(0.5, 0.5), alpha=self.alpha(c.t))


# ---------- thẻ ảnh minh hoạ ----------
class Anh(DongTac):
    LOAI = "anh"
    LOP_MAN = True
    VAO = 0.5

    def __init__(self, d, t_end):
        super().__init__(d, t_end)
        self.file = d.get("file")
        self.tim = d.get("tim")
        self.rong = float(d.get("rong", 0.76))
        self.vi_tri = d.get("vi_tri") or [0.5, 0.36]
        self.tieu_de = d.get("tieu_de")
        self._img = None

    def sfx(self):
        return [("hien", self.t0)]

    def ve_man(self, c):
        if self._img is None:
            p = c.anh_minh_hoa(self.file, self.tim)
            if p and os.path.exists(p):
                card = ve.the_anh(Image.open(p), int(self.rong * c.W))
                if self.tieu_de:
                    tt = ve.chu_anh(self.tieu_de, c.font_sub, int(c.H * 0.03), VANG, vien=4, bong=4)
                    big = Image.new("RGBA", (max(card.size[0], tt.size[0]), card.size[1] + tt.size[1] - 10),
                                    (0, 0, 0, 0))
                    big.alpha_composite(card, ((big.size[0] - card.size[0]) // 2, 0))
                    big.alpha_composite(tt, ((big.size[0] - tt.size[0]) // 2, card.size[1] - 24))
                    card = big
                self._img = ve.rgba_pil_sang_bgra(card)
            else:
                self._img = False
        if not isinstance(self._img, np.ndarray):
            return
        pin = ease_in_out_cubic(_ramp(c.t, self.t0, self.VAO))
        cx = self.vi_tri[0] * c.W + (1 - pin) * c.W
        cy = self.vi_tri[1] * c.H
        ve.dan_np(c.frame, self._img, cx, cy, neo=(0.5, 0.5), alpha=self.alpha(c.t))


# ---------- con số ----------
class So(DongTac):
    LOAI = "so"
    LOP_MAN = True

    def __init__(self, d, t_end):
        super().__init__(d, t_end)
        self.chu = str(d.get("chu") or "0")
        self.phu = d.get("phu") or ""
        self.vi_tri = d.get("vi_tri") or [0.5, 0.30]
        self.mau = ve_mau(d.get("mau"), VANG)
        self._cache = {}

    def sfx(self):
        return [("dem", self.t0)]

    def _so_hien(self, t):
        import re
        m = re.match(r"^([^\d]*)([\d.,]+)(.*)$", self.chu)
        if not m:
            return self.chu
        pre, num, post = m.groups()
        digits = num.replace(",", "").replace(".", "")
        try:
            val = int(digits)
        except ValueError:
            return self.chu
        p = ease(_ramp(t, self.t0, 1.0))
        v = int(round(val * p))
        s = "{:,}".format(v).replace(",", ".") if len(digits) > 3 else str(v)
        return pre + s + post

    def ve_man(self, c):
        s = self._so_hien(c.t)
        key = s
        if key not in self._cache:
            if len(self._cache) > 40:
                self._cache.clear()
            img = ve.chu_anh(s, c.font_sub, int(c.H * 0.11), self.mau, vien=int(c.H * 0.008), bong=int(c.H * 0.008))
            if self.phu:
                ph = ve.chu_anh(self.phu, c.font_sub, int(c.H * 0.034), TRANG, vien=int(c.H * 0.004), bong=6)
                big = Image.new("RGBA", (max(img.size[0], ph.size[0]), img.size[1] + ph.size[1] - 20), (0, 0, 0, 0))
                big.alpha_composite(img, ((big.size[0] - img.size[0]) // 2, 0))
                big.alpha_composite(ph, ((big.size[0] - ph.size[0]) // 2, img.size[1] - 20))
                img = big
            if img.size[0] > c.W * 0.92:
                k = c.W * 0.92 / img.size[0]
                img = img.resize((int(img.size[0] * k), int(img.size[1] * k)), Image.LANCZOS)
            self._cache[key] = ve.rgba_pil_sang_bgra(img)
        pin = 0.85 + 0.15 * ease(_ramp(c.t, self.t0, 0.3))
        img = self._cache[key]
        if pin < 0.999:
            img = ve.bien_hinh(img, img.shape[0] * pin)
        ve.dan_np(c.frame, img, self.vi_tri[0] * c.W, self.vi_tri[1] * c.H, alpha=self.alpha(c.t))


# ---------- CTA: nút kêu gọi theo dõi (cuối video) ----------
class Cta(DongTac):
    """Nút đỏ bo tròn có chuông, bật lên (nảy), con trỏ bay tới bấm, sóng loé, chuông rung — thay cho chữ trơn."""
    LOAI = "cta"
    LOP_MAN = True
    VAO = 0.35
    T_BAM = 1.45   # giây sau `luc` con trỏ bấm

    def __init__(self, d, t_end):
        super().__init__(d, t_end)
        self.chu = str(d.get("chu") or "THEO DÕI KÊNH")
        self.phu = d.get("phu") or ""
        self.vi_tri = d.get("vi_tri") or [0.5, 0.42]
        self.mau = ve_mau(d.get("mau"), (254, 44, 85))
        self._nen = None

    def sfx(self):
        return [("hien", self.t0), ("dem", self.t0 + self.T_BAM)]

    @staticmethod
    def _chuong(S, goc):
        """Chuông trắng kích thước S (px), xoay quanh điểm treo."""
        from PIL import ImageDraw
        k = 4
        im = Image.new("RGBA", (100 * k, 112 * k), (0, 0, 0, 0))
        g = ImageDraw.Draw(im)
        w = (255, 255, 255, 255)
        g.ellipse((46 * k, 4 * k, 54 * k + 2 * k, 14 * k), fill=w)
        g.ellipse((22 * k, 12 * k, 78 * k, 72 * k), fill=w)
        g.polygon([(22 * k, 44 * k), (78 * k, 44 * k), (90 * k, 80 * k), (10 * k, 80 * k)], fill=w)
        g.rounded_rectangle((8 * k, 76 * k, 92 * k, 90 * k), radius=7 * k, fill=w)
        g.ellipse((40 * k, 86 * k, 60 * k, 106 * k), fill=w)
        im = im.resize((S, int(S * 1.12)), Image.LANCZOS)
        if abs(goc) > 0.3:
            im = im.rotate(goc, resample=Image.BICUBIC, center=(S // 2, 4))
        return im

    def _ve(self, c, dt):
        from PIL import ImageDraw
        bw, bh = int(c.W * 0.78), int(c.H * 0.088)
        CW, CH = int(c.W * 0.98), int(bh * 3.4)
        k = 2
        im = Image.new("RGBA", (CW * k, CH * k), (0, 0, 0, 0))
        g = ImageDraw.Draw(im)
        cx, cy = CW * k // 2, int(CH * k * 0.40)
        press = 0.0
        if self.T_BAM <= dt < self.T_BAM + 0.18:
            press = 1 - abs((dt - self.T_BAM) / 0.18 * 2 - 1)
        s = 1.0 - 0.05 * press
        x0, y0, x1, y1 = cx - bw * k * s / 2, cy - bh * k * s / 2, cx + bw * k * s / 2, cy + bh * k * s / 2
        # bóng
        sh = Image.new("RGBA", im.size, (0, 0, 0, 0))
        ImageDraw.Draw(sh).rounded_rectangle((x0, y0 + 10 * k, x1, y1 + 10 * k), radius=bh * k // 2, fill=(0, 0, 0, 110))
        from PIL import ImageFilter
        im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(9 * k)))
        g = ImageDraw.Draw(im)
        mau = tuple(int(v * (0.86 if press else 1.0)) for v in self.mau)
        g.rounded_rectangle((x0, y0, x1, y1), radius=bh * k // 2, fill=mau + (255,), outline=(255, 255, 255, 255),
                            width=4 * k)
        # chuông (rung sau khi bấm)
        S = int(bh * 0.56 * k * s)
        goc = 0.0
        if dt >= self.T_BAM:
            u = dt - self.T_BAM
            goc = 22 * math.exp(-2.6 * u) * math.sin(2 * math.pi * 4.2 * u)
        else:
            goc = 4 * math.sin(2 * math.pi * 1.5 * dt)
        ch = self._chuong(S, goc)
        im.alpha_composite(ch, (int(x0 + bh * k * 0.34 * s), int(cy - ch.size[1] * 0.46)))
        # chữ
        f = ve.font(ve.chon_font(c.font_dam, self.chu), int(bh * 0.40 * k * s))
        tw = g.textlength(self.chu, font=f)
        tx = x0 + bh * k * 0.34 * s + S + bh * k * 0.22
        tx = tx + max(0.0, (x1 - bh * k * 0.30 - tx - tw) / 2)
        g.text((tx, cy), self.chu, font=f, fill=(255, 255, 255, 255), anchor="lm")
        # sóng loé khi bấm
        if dt >= self.T_BAM:
            u = (dt - self.T_BAM) / 0.55
            if u < 1:
                rr = bh * k * (0.3 + 1.2 * u)
                px, py = cx + bw * k * 0.18, cy + bh * k * 0.08
                rg = Image.new("RGBA", im.size, (0, 0, 0, 0))
                ImageDraw.Draw(rg).ellipse((px - rr, py - rr, px + rr, py + rr), outline=(255, 255, 255, int(220 * (1 - u))),
                                           width=int(6 * k * (1 - u)) + 1)
                im.alpha_composite(rg)
        # con trỏ bay tới bấm
        if 0.6 <= dt <= self.T_BAM + 1.6:
            tx0, ty0 = cx + bw * k * 0.46, cy + bh * k * 1.9
            tx1, ty1 = cx + bw * k * 0.18, cy + bh * k * 0.10
            q = ease(_ramp(dt, 0.6, self.T_BAM - 0.6))
            px, py = tx0 + (tx1 - tx0) * q, ty0 + (ty1 - ty0) * q
            if dt > self.T_BAM + 1.0:
                q2 = _ramp(dt, self.T_BAM + 1.0, 0.6)
                py += bh * k * 0.6 * q2
            a = 255 if dt < self.T_BAM + 1.0 else int(255 * (1 - _ramp(dt, self.T_BAM + 1.0, 0.6)))
            u2 = bh * k * 0.0145
            pts = [(0, 0), (0, 38), (9, 29), (16, 44), (24, 40), (17, 26), (30, 26)]
            poly = [(px + x * u2 * 2.2, py + y * u2 * 2.2) for x, y in pts]
            cur = Image.new("RGBA", im.size, (0, 0, 0, 0))
            cg = ImageDraw.Draw(cur)
            cg.polygon(poly, fill=(255, 255, 255, a), outline=(0, 0, 0, a))
            cg.line(poly + [poly[0]], fill=(0, 0, 0, a), width=3 * k)
            im.alpha_composite(cur)
        if self.phu:
            f2 = ve.font(ve.chon_font(c.font_dam, self.phu), int(bh * 0.26 * k))
            g.text((CW * k // 2, int(cy + bh * k * 1.0)), self.phu, font=f2, fill=(255, 255, 255, 255), anchor="mm",
                   stroke_width=3 * k, stroke_fill=(0, 0, 0, 255))
        return im.resize((CW, CH), Image.LANCZOS), (cx / k, cy / k)

    def ve_man(self, c):
        dt = c.t - self.t0
        p = _ramp(dt, 0, 0.5)
        c1 = 1.70158
        sc = 1 + (c1 + 1) * (p - 1) ** 3 + c1 * (p - 1) ** 2 if p < 1 else 1.0
        if dt > 0.5:
            sc *= 1 + 0.03 * math.sin(2 * math.pi * 1.4 * (dt - 0.5))
        img, (ox, oy) = self._ve(c, dt)
        arr = ve.rgba_pil_sang_bgra(img)
        if abs(sc - 1) > 0.004:
            arr = ve.bien_hinh(arr, arr.shape[0] * sc)
            ox, oy = ox * sc, oy * sc
        h, w = arr.shape[:2]
        ve.dan_np(c.frame, arr, self.vi_tri[0] * c.W, self.vi_tri[1] * c.H, neo=(ox / w, oy / h),
                  alpha=self.alpha(c.t))


# ---------- phóng + bay ----------
def _bezier(a, b, cong=0.22, n=60, huong=1.0):
    a, b = np.asarray(a, float), np.asarray(b, float)
    m = (a + b) / 2
    v = b - a
    perp = np.array([-v[1], v[0]])
    nrm = np.linalg.norm(perp)
    if nrm < 1e-12:
        return np.stack([a, b])
    perp = perp / nrm
    # cong về phía "bắc" (y nhỏ) trừ khi huong<0
    if perp[1] > 0:
        perp = -perp
    ctrl = m + perp * np.linalg.norm(v) * cong * huong
    ts = np.linspace(0, 1, n)[:, None]
    return (1 - ts) ** 2 * a + 2 * (1 - ts) * ts * ctrl + ts ** 2 * b


class Phong(DongTac):
    LOAI = "phong"
    LOP_DAT = True
    LOP_MAN = True
    BEN_VUNG = False
    RISE = 0.6

    def __init__(self, d, t_end):
        self.bay_trong = float(d.get("bay_trong", 3.0))
        self.so_luong = int(d.get("so_luong", 1))
        super().__init__(d, t_end)
        self.tu, self.den = d.get("tu"), d.get("den_diem") or d.get("toi") or d.get("den_ref")
        if self.den is None and isinstance(d.get("den"), (str, list)):
            self.den = d.get("den")
            self.t1 = self.t0 + self.thoi_luong()
        self.vat = d.get("vat") or "ten_lua"
        self.du_kien = bool(d.get("du_kien", False))
        self.mau = ve_mau(d.get("mau"), VANG)
        self.cong = float(d.get("cong", 0.22))
        self.co_km = d.get("co_km")
        self._sp = None

    def thoi_luong(self):
        return self.RISE + self.bay_trong + 0.25 * (self.so_luong - 1) + 1.6

    def sfx(self):
        return [("phong", self.t0 + i * 0.25) for i in range(self.so_luong)]

    def _duong(self, c):
        a, b = self.diem(c, self.tu), self.diem(c, self.den)
        if not a or not b:
            return None
        ua, ub = c.don_vi(*a), c.don_vi(*b)
        # quấn vòng: chọn bản sao gần
        dx = ub[0] - ua[0]
        if dx > 0.5:
            ub = (ub[0] - 1, ub[1])
        elif dx < -0.5:
            ub = (ub[0] + 1, ub[1])
        return _bezier(ua, ub, self.cong, 80)

    def _tien_do(self, c, k):
        t = c.t - self.t0 - k * 0.25
        if t < self.RISE:
            return "rise", max(0.0, t / self.RISE)
        p = (t - self.RISE) / self.bay_trong
        if p < 1:
            return "bay", ease_in_out_cubic(p) if self.bay_trong > 2.5 else ease(p)
        return "xong", min(1.0, (t - self.RISE - self.bay_trong) / 1.6)

    def ve_dat(self, c):
        duong = self._duong(c)
        if duong is None:
            return
        px = np.stack([c.px_don_vi(x, y) for x, y in duong])
        if self.du_kien:
            img, o = ve.vach_sang(px, self.mau, day=max(2, c.px_day(2)), glow=0, alpha=0.55,
                                  net_dut=max(8, c.px_day(14)), gioi_han=(c.rong, c.cao))
            if img is not None:
                ve.dan_lop(c.ground, img, *o)
        for k in range(self.so_luong):
            pha, p = self._tien_do(c, k)
            if pha == "rise":
                continue
            n = max(2, int(len(px) * (p if pha == "bay" else 1.0)))
            a = 1.0 if pha != "xong" else 1 - p
            lech = (k - (self.so_luong - 1) / 2) * c.px_day(12)
            pts = px[:n] + [lech, 0]
            img, o = ve.vach_sang(pts, self.mau, day=max(2, c.px_day(3)), glow=max(4, c.px_day(10)), alpha=a,
                                  gioi_han=(c.rong, c.cao))
            if img is not None:
                ve.dan_lop(c.ground, img, *o)

    def ve_man(self, c):
        duong = self._duong(c)
        if duong is None:
            return
        if self._sp is None:
            sp0 = c.sprite(self.vat)
            self._sp = sp0 if isinstance(sp0, np.ndarray) else False
        if not isinstance(self._sp, np.ndarray):
            return
        sp = ve.rgba_sang_bgra(self._sp)
        lon0, lat0 = self.diem(c, self.tu)
        if self.co_km is None:
            self.co_km = 0.11 * c.rong_km_hien()
        for k in range(self.so_luong):
            pha, p = self._tien_do(c, k)
            if pha == "xong":
                continue
            lech_dv = (k - (self.so_luong - 1) / 2) * 0.0006 * c.cam.tt.w / 0.02
            if pha == "rise":
                sx, sy, zc = c.man_don_vi(duong[0][0] + lech_dv, duong[0][1])
                if zc <= 0:
                    continue
                h = max(c.km_px_man(self.co_km, lon0, lat0), c.H * 0.045)
                yy = sy - ease(p) * h * 0.9
                # vệt lửa đứng
                tr = ve.vach_sang(np.array([[sx, sy], [sx, yy + h * 0.1]]), self.mau, day=3, glow=10, alpha=0.9)
                if tr[0] is not None:
                    ve.dan_np(c.frame, ve.rgba_pil_sang_bgra(tr[0]), tr[1][0], tr[1][1], neo=(0, 0))
                img = ve.bien_hinh(sp, h, 0)
                ve.dan_np(c.frame, img, sx, yy, neo=(0.5, 0.85), alpha=min(1.0, 0.3 + p))
            else:
                i = min(len(duong) - 1, int(p * (len(duong) - 1)))
                j = max(0, i - 2)
                x, y = duong[i]
                sx, sy, zc = c.man_don_vi(x + lech_dv, y)
                if zc <= 0:
                    continue
                sx2, sy2, _ = c.man_don_vi(duong[j][0] + lech_dv, duong[j][1])
                goc = math.degrees(math.atan2(sy - sy2, sx - sx2)) + 90
                lon, lat = c.lonlat_don_vi(x, y)
                h = max(c.km_px_man(self.co_km * 0.8, lon, lat), c.H * 0.035)
                img = ve.bien_hinh(sp, h, goc)
                ve.dan_np(c.frame, img, sx, sy, neo=(0.5, 0.5))


# ---------- nổ ----------
class No(DongTac):
    LOAI = "no"
    LOP_DAT = True
    LOP_MAN = True
    BEN_VUNG = False

    def __init__(self, d, t_end):
        super().__init__(d, t_end)
        self.ref = d.get("tai")
        self.co_km = d.get("co_km")
        self.dai = float(d.get("keo_dai", 1.5))
        self.t1 = self.t0 + self.dai

    def thoi_luong(self):
        return 1.5

    def hoat_dong(self, t):
        return self.t0 <= t <= self.t1

    def sfx(self):
        return [("no", self.t0)]

    def ve_dat(self, c):
        p = self.diem(c, self.ref)
        if not p:
            return
        if self.co_km is None:
            self.co_km = 0.22 * c.rong_km_hien()
        q = _ramp(c.t, self.t0, self.dai)
        r = c.km_px_dat(self.co_km, p[1]) * 0.5 * (0.3 + 0.7 * ease(q))
        a = (1 - q) ** 1.5 * 0.75
        if r < 2 or a <= 0.01:
            return
        x, y = c.px_dat(*p)
        img = ve.dia_sang(int(r * 2), (255, 140, 30), a)
        ve.dan_lop(c.ground, img, x - img.size[0] / 2, y - img.size[1] / 2)

    def ve_man(self, c):
        p = self.diem(c, self.ref)
        if not p:
            return
        sx, sy, zc = c.man(*p)
        if zc <= 0:
            return
        q = _ramp(c.t, self.t0, self.dai)
        fr = c.sprite_no(q)
        if fr is None:
            return
        h = c.km_px_man(self.co_km, *p) * (0.6 + 0.4 * q)
        img = ve.bien_hinh(ve.rgba_sang_bgra(fr), h)
        ve.dan_np(c.frame, img, sx, sy - h * 0.18, neo=(0.5, 0.5))
        if q < 0.12:
            # loé trắng
            a = (1 - q / 0.12) * 0.35
            c.frame[:] = (c.frame.astype(np.float32) * (1 - a) + 255 * a).astype(np.uint8)


# ---------- vỡ vụn ----------
class VoVun(DongTac):
    LOAI = "vo_vun"
    LOP_DAT = True
    BEN_VUNG = False

    def __init__(self, d, t_end):
        super().__init__(d, t_end)
        self.ref = d.get("nuoc") or d.get("tai")
        self.dai = float(d.get("keo_dai", 1.6))
        self.t1 = self.t0 + self.dai
        self.manh = None
        self.z_ev = None
        self.goc_ev = None
        self.tam = None
        self.nhan = []   # các Nhan gắn với nước này (render gán)

    def thoi_luong(self):
        return 1.6

    def hoat_dong(self, t):
        return self.t0 <= t <= self.t1

    def sfx(self):
        return [("vo", self.t0)]

    def _tao_manh(self, c, rec, to_nuoc):
        vong = DL.vong_den_px(rec["vong"], c.z, c.x0, c.y0, c.rong, c.cao)
        if not vong:
            return False
        co = None
        if to_nuoc is not None and to_nuoc.co_flag:
            p = c.co_nuoc(self.ref)
            if p and os.path.exists(p):
                co = Image.open(p).convert("RGBA")
        mau = to_nuoc.mau if to_nuoc is not None else (255, 74, 31)
        allp = np.concatenate(vong, 0)
        bw = float(allp[:, 0].max() - allp[:, 0].min())
        img, (ox, oy) = ve.to_vung(vong, c.rong, c.cao, mau=None if co is not None else mau, co=co,
                                   day_khoi=int(max(2, min(16, bw * 0.012))), day_vien=max(1, int(bw * 0.004)))
        if img is None:
            return False
        # dán nhãn vào canvas trước khi cắt
        for nh in self.nhan:
            p = c.diem(nh.ref)
            if not p or nh.co_km is None:
                continue
            px = c.km_px_dat(nh.co_km, p[1])
            if px < 6:
                continue
            ti = nh._anh(c, px)
            x, y = c.px_dat(*p)
            ve.dan_lop(img, ti, x - ox - ti.size[0] / 2, y - oy - ti.size[1] / 2)
        if img.size[0] * img.size[1] > 6_000_000:
            k = math.sqrt(6_000_000 / (img.size[0] * img.size[1]))
            img = img.resize((max(2, int(img.size[0] * k)), max(2, int(img.size[1] * k))), Image.BILINEAR)
            self.ti_le_canvas = k
        else:
            self.ti_le_canvas = 1.0
        self.manh = ve.manh_vo(img, 28, seed=3)
        self.z_ev = c.z
        self.goc_ev = (c.x0 + ox, c.y0 + oy)   # gốc canvas theo px thế giới mức z_ev
        self.tam = (img.size[0] / 2, img.size[1] / 2)
        rng = random.Random(5)
        self.van_toc = []
        for _, (px0, py0), (cx, cy) in self.manh:
            vx, vy = cx - self.tam[0], cy - self.tam[1]
            n = math.hypot(vx, vy) + 1e-6
            sp = (0.9 + rng.random() * 0.8) * max(img.size) * 0.35
            self.van_toc.append((vx / n * sp + rng.uniform(-40, 40), vy / n * sp + rng.uniform(-40, 40),
                                 rng.uniform(-60, 60)))
        return True

    def ve_dat(self, c):
        rec = c.vung(self.ref)
        if not rec:
            return
        if self.manh is None:
            if not self._tao_manh(c, rec, c.to_nuoc_cua(self.ref)):
                self.manh = []
                return
        if not self.manh:
            return
        q = _ramp(c.t, self.t0, self.dai)
        scale = (2 ** (c.z - self.z_ev)) / self.ti_le_canvas
        gx = (self.goc_ev[0]) * (2 ** (c.z - self.z_ev)) - c.x0
        gy = (self.goc_ev[1]) * (2 ** (c.z - self.z_ev)) - c.y0
        a = (1 - q) ** 1.2
        for (img, (px0, py0), (cx, cy)), (vx, vy, vr) in zip(self.manh, self.van_toc):
            dx = vx * q * 1.2 * (1 + q)
            dy = vy * q * 1.2 * (1 + q) + 0.6 * (q * q) * self.tam[1]
            s = scale * (1 + 0.25 * q)
            w, h = max(2, int(img.size[0] * s)), max(2, int(img.size[1] * s))
            im = img.resize((w, h), Image.BILINEAR)
            if abs(vr) > 1:
                im = im.rotate(vr * q, expand=True, resample=Image.BILINEAR)
            cxn = gx + (cx + dx) * scale
            cyn = gy + (cy + dy) * scale
            ve.dan_lop(c.ground, im, cxn - im.size[0] / 2, cyn - im.size[1] / 2, a)


# ---------- radar ----------
class Radar(DongTac):
    LOAI = "radar"
    LOP_DAT = True
    BEN_VUNG = False

    def __init__(self, d, t_end):
        super().__init__(d, t_end)
        self.ref = d.get("tai")
        self.ban_kinh_km = d.get("ban_kinh_km")
        self.so_vong = int(d.get("so_vong", 3))
        self.chu_ky = float(d.get("chu_ky", 1.8))
        self.mau = ve_mau(d.get("mau"), (210, 240, 255))
        if d.get("den") is None:
            self.t1 = self.t0 + 3.6

    def thoi_luong(self):
        return 3.6

    def hoat_dong(self, t):
        return self.t0 <= t <= self.t1

    def sfx(self):
        return [("ping", self.t0)]   # 1 tiếng cho cả cụm sóng (3 tiếng liên tiếp nghe "tạch tạch tạch" rất khó chịu)

    def ve_dat(self, c):
        p = self.diem(c, self.ref)
        if not p:
            return
        if self.ban_kinh_km is None:
            self.ban_kinh_km = 0.4 * c.rong_km_hien()
        R = c.km_px_dat(self.ban_kinh_km, p[1])
        x, y = c.px_dat(*p)
        tt = c.t - self.t0
        for i in range(self.so_vong):
            ph = (tt / self.chu_ky - i / self.so_vong)
            if ph < 0:
                continue
            fr = ph % 1.0
            r = R * fr
            a = (1 - fr) * 0.9
            if c.t > self.t1 - 0.5:
                a *= max(0.0, (self.t1 - c.t) / 0.5)
            if r < 2:
                continue
            img, o = ve.vong_tron(x, y, r, self.mau, day=max(2, c.px_day(2)), alpha=a)
            ve.dan_lop(c.ground, img, *o)


# ---------- tách đầu đạn ----------
class Tach(DongTac):
    LOAI = "tach"
    LOP_DAT = True
    LOP_MAN = True
    BEN_VUNG = False

    def __init__(self, d, t_end):
        super().__init__(d, t_end)
        self.ref = d.get("tai")
        self.so_vet = int(d.get("so_vet", 4))
        self.huong = d.get("huong")   # độ: 0 = đông, 90 = nam (mặt đất)
        self.toi = d.get("toi")
        self.dai_km = d.get("dai_km")
        self.dai = float(d.get("keo_dai", 1.4))
        self.t1 = self.t0 + self.dai + 0.6
        self.mau = ve_mau(d.get("mau"), (255, 255, 255))

    def thoi_luong(self):
        return 2.0

    def hoat_dong(self, t):
        return self.t0 <= t <= self.t1

    def sfx(self):
        return [("tach", self.t0)]

    def _vet(self, c):
        p = self.diem(c, self.ref)
        if not p:
            return None
        if self.dai_km is None:
            self.dai_km = 0.18 * c.rong_km_hien()
        ux, uy = c.don_vi(*p)
        if self.huong is None:
            if self.toi:
                q = self.diem(c, self.toi)
                if q:
                    vx, vy = c.don_vi(*q)
                    self.huong = math.degrees(math.atan2(vy - uy, vx - ux))
            if self.huong is None:
                self.huong = 90.0
        L = c.km_den_don_vi(self.dai_km, p[1])
        out = []
        for i in range(self.so_vet):
            g = self.huong + (i - (self.so_vet - 1) / 2) * 16.0
            out.append((ux, uy, ux + L * math.cos(math.radians(g)), uy + L * math.sin(math.radians(g))))
        return out

    def ve_dat(self, c):
        vets = self._vet(c)
        if not vets:
            return
        q = ease(_ramp(c.t, self.t0, self.dai))
        a = 1.0 if c.t < self.t1 - 0.6 else max(0.0, (self.t1 - c.t) / 0.6)
        for (x0, y0, x1, y1) in vets:
            pts = np.array([c.px_don_vi(x0, y0), c.px_don_vi(x0 + (x1 - x0) * q, y0 + (y1 - y0) * q)])
            img, o = ve.vach_sang(pts, self.mau, day=max(2, c.px_day(2)), glow=max(3, c.px_day(6)), alpha=a,
                                  gioi_han=(c.rong, c.cao))
            if img is not None:
                ve.dan_lop(c.ground, img, *o)

    def ve_man(self, c):
        vets = self._vet(c)
        if not vets or c.t > self.t1 - 0.6:
            return
        q = ease(_ramp(c.t, self.t0, self.dai))
        for (x0, y0, x1, y1) in vets:
            sx, sy, zc = c.man_don_vi(x0 + (x1 - x0) * q, y0 + (y1 - y0) * q)
            if zc <= 0:
                continue
            r = max(3, int(c.H * 0.004))
            img, o = ve.vong_tron(0, 0, r, self.mau, day=1, alpha=1.0, to=(255, 255, 255, 255))
            ve.dan_np(c.frame, ve.rgba_pil_sang_bgra(img), sx, sy)


# ---------- tuyến đường ----------
class Tuyen(DongTac):
    LOAI = "tuyen"
    LOP_DAT = True

    def __init__(self, d, t_end):
        super().__init__(d, t_end)
        self.tu, self.toi = d.get("tu"), d.get("toi") or d.get("den_diem")
        self.keo_dai = float(d.get("keo_dai", 2.0))
        self.vat = d.get("vat")
        self.mau = ve_mau(d.get("mau"), (255, 140, 0))
        self.net_dut = bool(d.get("net_dut", True))
        self.cong = float(d.get("cong", 0.12))
        self.co_km = d.get("co_km")
        self.qua = d.get("qua") or []
        # tuyến TÀU / dầu / hàng hải đi theo biển (tránh đất liền); tên lửa, máy bay đi cung cong. "bien": false để ép cung.
        tau = str(self.vat or "").lower() in ("tau_dau", "tau_san_bay", "tau_chien", "tau", "tau_hang")
        self.bien = bool(d.get("bien", tau or bool(self.qua)))
        self._sp = None
        self._duong = None

    def sfx(self):
        return [("luot", self.t0)]

    def _duong_don_vi(self, c, a, b):
        """Đường đi (np.array đơn vị Mercator, liên tục qua kinh tuyến 180)."""
        if self._duong is not None:
            return self._duong
        ua, ub = c.don_vi(*a), c.don_vi(*b)
        if self.bien:
            from . import duong_bien as DB
            dl = getattr(c.tt, "dl", None)
            if dl is not None:
                diem = [tuple(a)] + [self.diem(c, q) or tuple(q) for q in self.qua] + [tuple(b)]
                ll = DB.tim_duong_qua(dl, diem)
                if ll and len(ll) >= 2:
                    pts = [c.don_vi(lo, la) for lo, la in ll]
                    out = [pts[0]]
                    for x, y in pts[1:]:
                        d = x - out[-1][0]
                        x -= round(d)
                        out.append((x, y))
                    # làm đều theo chiều dài cung
                    arr = np.array(out, float)
                    seg = np.hypot(*np.diff(arr, axis=0).T)
                    cum = np.concatenate([[0], np.cumsum(seg)])
                    ts = np.linspace(0, cum[-1], 140)
                    self._duong = np.stack([np.interp(ts, cum, arr[:, 0]), np.interp(ts, cum, arr[:, 1])], 1)
                    return self._duong
        dx = ub[0] - ua[0]
        if dx > 0.5:
            ub = (ub[0] - 1, ub[1])
        elif dx < -0.5:
            ub = (ub[0] + 1, ub[1])
        self._duong = _bezier(ua, ub, self.cong, 70)
        return self._duong

    def ve_dat(self, c):
        a, b = self.diem(c, self.tu), self.diem(c, self.toi)
        if not a or not b:
            return
        duong = self._duong_don_vi(c, a, b)
        px = np.stack([c.px_don_vi(x, y) for x, y in duong])
        q = ease(_ramp(c.t, self.t0, self.keo_dai))
        n = max(2, int(len(px) * q))
        al = self.alpha(c.t)
        img, o = ve.vach_sang(px[:n], self.mau, day=max(3, c.px_day(4)), glow=max(3, c.px_day(6)), alpha=al,
                              net_dut=max(10, c.px_day(16)) if self.net_dut else 0, gioi_han=(c.rong, c.cao))
        if img is not None:
            ve.dan_lop(c.ground, img, *o)
        # mũi tên ở đầu
        if n >= 3:
            p1, p0 = px[n - 1], px[max(0, n - 4)]
            v = p1 - p0
            L = np.linalg.norm(v) + 1e-6
            v = v / L
            w = max(8, c.px_day(14))
            tri = np.array([p1 + v * w * 1.2, p1 - v * w * 0.6 + np.array([-v[1], v[0]]) * w * 0.8,
                            p1 - v * w * 0.6 - np.array([-v[1], v[0]]) * w * 0.8])
            img2, o2 = ve.vach_sang(np.vstack([tri, tri[:1]]), self.mau, day=max(2, c.px_day(3)), glow=0, alpha=al)
            if img2 is not None:
                ve.dan_lop(c.ground, img2, *o2)
        if self.vat:
            if self._sp is None:
                sp0 = c.sprite(self.vat)
                self._sp = sp0 if isinstance(sp0, np.ndarray) else False
            if isinstance(self._sp, np.ndarray) and n >= 2:
                if self.co_km is None:
                    self.co_km = 0.07 * c.rong_km_hien()
                i = n - 1
                x, y = px[i]
                x0, y0 = px[max(0, i - 2)]
                goc = math.degrees(math.atan2(y - y0, x - x0)) + 90
                lon, lat = c.lonlat_don_vi(*duong[i])
                h = c.km_px_dat(self.co_km, lat)
                im = ve.bien_hinh(self._sp, h, goc)
                ve.dan_lop(c.ground, Image.fromarray(im, "RGBA"), x - im.shape[1] / 2, y - im.shape[0] / 2, al)


# ---------- lan rộng ----------
class Lan(DongTac):
    LOAI = "lan"
    LOP_DAT = True

    def __init__(self, d, t_end):
        super().__init__(d, t_end)
        self.ref = d.get("tai")
        self.keo_dai = float(d.get("keo_dai", 2.0))
        self.ban_kinh_km = d.get("ban_kinh_km")
        self.mau = ve_mau(d.get("mau"), (255, 60, 60))

    def ve_dat(self, c):
        p = self.diem(c, self.ref)
        if not p:
            return
        if self.ban_kinh_km is None:
            self.ban_kinh_km = 0.3 * c.rong_km_hien()
        q = ease(_ramp(c.t, self.t0, self.keo_dai))
        r = c.km_px_dat(self.ban_kinh_km, p[1]) * q
        if r < 2:
            return
        x, y = c.px_dat(*p)
        al = self.alpha(c.t)
        img, o = ve.vong_tron(x, y, r, self.mau, day=max(2, c.px_day(3)), alpha=al,
                              to=tuple(self.mau) + (int(90 * al),))
        ve.dan_lop(c.ground, img, *o)

    def sfx(self):
        return [("lan", self.t0)]


# ---------- tiện ích ----------
def ve_mau(s, mac_dinh):
    if not s:
        return mac_dinh
    if isinstance(s, (list, tuple)) and len(s) == 3:
        return tuple(int(v) for v in s)
    s = str(s).strip().lstrip("#")
    if len(s) == 6:
        return tuple(int(s[i:i + 2], 16) for i in (0, 2, 4))
    return mac_dinh


def c_ten(ref):
    if isinstance(ref, str):
        return ref
    return ""


LOP = {k.LOAI: k for k in (ToNuoc, Nhan, ChuNeon, Ghim, VatThe, Nguoi, Anh, So, Phong, No, VoVun, Radar, Tach,
                           Tuyen, Lan, Cta)}


CHU_TOI_DA = 3.5   # giây


def tao(d, t_end):
    loai = d.get("loai")
    if loai not in LOP:
        raise ValueError("động tác không có trong bộ chuẩn: %r" % loai)
    # chữ (nhãn / neon / ghim) chỉ ở lại ~3,5 s sau khi được nhắc; muốn giữ lâu phải ghi "giu_lau": true
    if loai in ("nhan", "chu_neon", "ghim") and not d.get("giu_lau") and d.get("luc") is not None:
        gioi_han = float(d["luc"]) + CHU_TOI_DA
        if d.get("den") is None or float(d["den"]) > gioi_han:
            d = dict(d, den=gioi_han)
    return LOP[loai](d, t_end)
