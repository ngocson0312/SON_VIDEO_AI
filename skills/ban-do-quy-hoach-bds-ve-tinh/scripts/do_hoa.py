# -*- coding: utf-8 -*-
"""Lớp đồ hoạ trên nền bản đồ (toạ độ khung 1080x1920, đo từ video mẫu ho_dan.mp4):
thẻ hook đầu video, thẻ đầu đề bản đồ tổng, thẻ tài liệu navy, logo kênh, chữ nguồn, SUB KARAOKE nguyên văn.
CTA cuối ở cta.py, điểm nhấn bản đồ ở diem_nhan.py."""
import math
import os

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

import chung as C
from chung import W, H, FPS, clamp, ramp, ease_out

NAVY_A = tuple(C.NAVY) + (238,)
VIEN_A = tuple(C.NAVY_VIEN) + (255,)


def _hop_navy(w, h, r=19):
    box = C.hop_bo((w, h), r, NAVY_A, vien=VIEN_A, vien_w=2)
    sh, p = C.bong_do(box, blur=18, alpha=0.5)
    out = Image.new("RGBA", (w + 2 * p, h + 2 * p), (0, 0, 0, 0))
    out.alpha_composite(sh, (0, 8))
    out.alpha_composite(box, (p, p))
    return out, p


# ---------------------------------------------------------------- thẻ hook (đầu video, như mẫu 0–3,8 s)

class TheHook:
    """hộp navy x 60–1020, y ~202: dòng 1 vàng, dòng 2 trắng, dòng 3 xám nhỏ. Ra: cắt cứng như mẫu (hoặc fade)."""

    def __init__(self, it):
        self.t0, self.t1 = float(it.get("tu", 0.0)), float(it["den"])
        lines = []
        if it.get("dong1"):
            lines.append(C.chu(it["dong1"].upper(), "semi", 32, fill=C.VANG, track=1))
        if it.get("dong2"):
            lines.append(C.chu(it["dong2"].upper(), "xbold", 32, fill=C.TRANG, track=1))
        if it.get("dong3"):
            lines.append(C.chu(it["dong3"].upper(), "semi", 17, fill=C.XAM, track=1))
        txt = C.xep_doc(lines, gap=10)
        w, h = 960, txt.height + 56
        box, p = _hop_navy(w, h, 15)
        box.alpha_composite(txt, (p + (w - txt.width) // 2, p + 28))
        self.img = np.asarray(box)
        self.x, self.y = 60 - p, 202 - p
        self.fade = bool(it.get("fade", False))

    def rect(self):
        return (self.x, self.y, self.x + self.img.shape[1], self.y + self.img.shape[0])

    def ve(self, frame, t):
        if t < self.t0 or t > self.t1:
            return
        a = ramp(t, self.t0, 0.15)
        if self.fade:
            a = min(a, clamp((self.t1 - t) / 0.2))
        C.dan(frame, self.img, self.x, self.y, a)


# ---------------------------------------------------------------- thẻ đầu đề (bản đồ tổng)

class TheDauDe:
    def __init__(self, tieu_de, phu=None, y=56):
        co = 34
        t1 = C.chu(tieu_de.upper(), "xbold", co, fill=C.VANG, track=1)
        while t1.width > 950 and co > 22:
            co -= 2
            t1 = C.chu(tieu_de.upper(), "xbold", co, fill=C.VANG, track=1)
        lines = [t1]
        if phu:
            cp = 24
            t2 = C.chu(phu, "semi", cp, fill=C.TRANG)
            while t2.width > 950 and cp > 16:
                cp -= 1
                t2 = C.chu(phu, "semi", cp, fill=C.TRANG)
            lines.append(t2)
        txt = C.xep_doc(lines, gap=6)
        w, h = 1004, txt.height + 36
        box, p = _hop_navy(w, h, 14)
        box.alpha_composite(txt, (p + (w - txt.width) // 2, p + 18))
        self.img = np.asarray(box)
        self.x, self.y = 38 - p, y - p

    def ve(self, frame, alpha=1.0):
        C.dan(frame, self.img, self.x, self.y, alpha)


# ---------------------------------------------------------------- thẻ tài liệu (ảnh công văn / bảng / sơ đồ)

class TheTaiLieu:
    """x 112–968, y 300–825 (cao theo ảnh, ≤ 560): tiêu đề vàng · ảnh viền trắng · 'Nguồn: …'. Vào: mờ + trượt xuống 20 px 0,18 s."""

    def __init__(self, it, tim_file):
        self.t0, self.t1 = float(it["tu"]), float(it["den"])
        w = 856
        tit = C.chu(it.get("tieu_de", "").upper(), "xbold", 32, fill=C.VANG, track=1) if it.get("tieu_de") else None
        if tit is not None and tit.width > w - 60:
            tit = C.chu(it["tieu_de"].upper(), "xbold", int(32 * (w - 60) / tit.width), fill=C.VANG, track=1)
        im = Image.open(tim_file(it["anh"])).convert("RGB")
        if it.get("cat"):
            x0, y0, x1, y1 = it["cat"]
            im = im.crop((int(x0), int(y0), int(x1), int(y1)))
        max_h = int(it.get("anh_cao", 380))
        im = C.fit_in(im, w - 56, max_h)
        vien = 3
        khung = Image.new("RGBA", (im.width + 2 * vien, im.height + 2 * vien), (255, 255, 255, 255))
        khung.paste(im, (vien, vien))
        nguon = C.chu("Nguồn: " + it["nguon"], "semi", 22, fill=C.TRANG) if it.get("nguon") else None
        parts = [p for p in (tit, khung, nguon) if p is not None]
        txt = C.xep_doc(parts, gap=14)
        h = txt.height + 48
        box, p = _hop_navy(w, h, 19)
        box.alpha_composite(txt, (p + (w - txt.width) // 2, p + 24))
        self.img = np.asarray(box)
        self.x, self.y = 112 - p, int(it.get("y", 300)) - p
        self.h = h

    def ve(self, frame, t):
        if t < self.t0 - 0.02 or t > self.t1:
            return
        a_in = ease_out(ramp(t, self.t0, 0.18))
        a = min(ramp(t, self.t0, 0.18), clamp((self.t1 - t) / 0.15))
        C.dan(frame, self.img, self.x, self.y - 20 * (1 - a_in), a)

    def sfx(self):
        return [{"t": self.t0, "file": "quick-swoosh.mp3", "muc": "nhe"}]


# ---------------------------------------------------------------- logo + nguồn

class Logo:
    """logo kênh góc phải trên: ảnh (cao 70) hoặc tên kênh chữ Montserrat Black 54 trắng bóng"""

    def __init__(self, kenh, tim_file=None):
        self.img = None
        logo = (kenh or {}).get("logo")
        ten = (kenh or {}).get("ten") or ""
        if logo and tim_file:
            try:
                im = Image.open(tim_file(logo)).convert("RGBA")
                s = 70 / im.height
                im = im.resize((max(1, int(im.width * s)), 70), Image.LANCZOS)
                self.img = np.asarray(im)
            except Exception:
                self.img = None
        if self.img is None and ten:
            self.img = np.asarray(C.chu(ten.upper(), "black", 54, fill=C.TRANG, shadow=(0, 3, 6, 0.75), track=2))
        self.x = 1012 - (self.img.shape[1] if self.img is not None else 0)
        self.y = 95 - (self.img.shape[0] // 2 if self.img is not None else 0)

    def rect(self):
        return (self.x, self.y, self.x + self.img.shape[1], self.y + self.img.shape[0]) if self.img is not None else None

    def ve(self, frame, alpha=1.0):
        if self.img is not None:
            C.dan(frame, self.img, self.x, self.y, alpha)


class ChuNguon:
    def __init__(self, text, y=1830):
        self.img = np.asarray(C.chu(text, "semi", 17, fill=(235, 238, 245), shadow=(0, 2, 3, 0.8)))
        self.x, self.y = (W - self.img.shape[1]) // 2, y

    def ve(self, frame, alpha=0.9):
        C.dan(frame, self.img, self.x, self.y, alpha)


# CTA cuối: xem cta.py (CtaNut — nút + icon, C11)


# ---------------------------------------------------------------- SUB KARAOKE nguyên văn (chốt 04/11/2026)

SUB_VIEN = (8, 14, 26)


def sprite_chu(text, key, size, fill, stroke=4, stroke_fill=SUB_VIEN, shadow=(0, 4, 6, 0.55)):
    """chữ có viền + bóng, giữ đường chân chữ (oy) để các chữ 1 dòng thẳng hàng"""
    f = C.font(key, size)
    pad = int(size * 0.6) + stroke + 8
    adv = f.getlength(text)
    asc, desc = f.getmetrics()
    Wm, Hm = int(adv) + 2 * pad, asc + desc + 2 * pad
    im = Image.new("RGBA", (Wm, Hm), (0, 0, 0, 0))
    oy = pad + asc
    if shadow:
        dx, dy, bl, al = shadow
        sh = Image.new("RGBA", (Wm, Hm), (0, 0, 0, 0))
        ImageDraw.Draw(sh).text((pad + dx, oy + dy), text, font=f, fill=(0, 0, 0, int(255 * al)), stroke_width=stroke,
                                stroke_fill=(0, 0, 0, int(255 * al)), anchor="ls")
        if bl > 0:
            sh = sh.filter(ImageFilter.GaussianBlur(bl))
        im.alpha_composite(sh)
    ImageDraw.Draw(im).text((pad, oy), text, font=f, fill=tuple(fill) + (255,), stroke_width=stroke,
                            stroke_fill=tuple(stroke_fill) + (255,), anchor="ls")
    return {"rgba": np.asarray(im), "oy": oy, "ox": pad, "adv": adv}


def _disp(w):
    t = w.rstrip(".,;:…!")
    return t if t else w


class SubKaraoke:
    """Cả cụm hiện cùng lúc (Montserrat ExtraBold trắng viền navy + bóng), chữ ĐANG ĐỌC vàng + phồng 6 %;
    ≤ 2 dòng, rộng ≤ 960 px, chân dòng cuối ở sub_y. Cụm lấy từ build_ass (nns-auto-sub) để giữ cặp từ/ranh câu."""

    PHONG = 0.06

    def __init__(self, chunks, sub_y=1545, co=56, max_w=960, key="sub", an=None):
        self.key = key
        f = C.font(key, co)
        self.cum = []
        an = an or []
        for c in chunks:
            ws = [dict(w, t=_disp(w["w"])) for w in c["words"] if w.get("w")]
            ws = [w for w in ws if w["t"]]
            if not ws:
                continue
            co_ = co
            lines = None
            for _ in range(6):
                lines = self._xep_dong(ws, C.font(key, co_), max_w, c.get("breaks"))
                if len(lines) <= 2:
                    break
                co_ = int(co_ * 0.9)
            lh = int(co_ * 1.28)
            items = []
            sp_w = C.font(key, co_).getlength(" ")
            for li, line in enumerate(lines):
                tot = sum(w["_adv"] for w in line) + sp_w * (len(line) - 1)
                x = W / 2 - tot / 2
                base = sub_y - (len(lines) - 1 - li) * lh
                for w in line:
                    items.append({"trang": sprite_chu(w["t"], key, co_, C.TRANG),
                                  "vang": sprite_chu(w["t"], key, co_, C.VANG), "x": x, "base": base,
                                  "adv": w["_adv"], "t": float(w["start"])})
                    x += w["_adv"] + sp_w
            self.cum.append({"t0": float(c["start"]), "t1": float(c["end"]), "items": items, "chu": [w["t"] for w in ws]})
        for i, c in enumerate(self.cum):
            nxt = self.cum[i + 1]["t0"] if i + 1 < len(self.cum) else 1e9
            c["t_het"] = min(nxt, c["t1"] + 0.35)
            for s0, s1 in an:
                if c["t0"] < s0 < c["t_het"]:
                    c["t_het"] = s0

    def _xep_dong(self, ws, f, max_w, breaks):
        sp = f.getlength(" ")
        for w in ws:
            w["_adv"] = f.getlength(w["t"])
        if breaks:
            lines, cur = [], []
            for i, w in enumerate(ws):
                cur.append(w)
                if i in set(breaks):
                    lines.append(cur)
                    cur = []
            if cur:
                lines.append(cur)
            if all(sum(w["_adv"] for w in l) + sp * (len(l) - 1) <= max_w for l in lines):
                return lines
        tot = sum(w["_adv"] for w in ws) + sp * (len(ws) - 1)
        if tot <= max_w:
            return [ws]
        # 2 dòng cân nhau
        best = None
        for k in range(1, len(ws)):
            a = sum(w["_adv"] for w in ws[:k]) + sp * (k - 1)
            b = sum(w["_adv"] for w in ws[k:]) + sp * (len(ws) - k - 1)
            if a <= max_w and b <= max_w:
                sc = abs(a - b)
                if best is None or sc < best[0]:
                    best = (sc, k)
        if best:
            return [ws[:best[1]], ws[best[1]:]]
        lines, cur, wcur = [], [], 0.0
        for w in ws:
            add = w["_adv"] + (sp if cur else 0)
            if cur and wcur + add > max_w:
                lines.append(cur)
                cur, wcur = [w], w["_adv"]
            else:
                cur.append(w)
                wcur += add
        if cur:
            lines.append(cur)
        return lines

    def ve(self, frame, t):
        f = 1 / FPS
        for c in self.cum:
            if t < c["t0"] - 0.05 or t > c["t_het"]:
                continue
            dt0 = t - c["t0"] + f
            if dt0 <= 0:
                continue
            k = clamp(dt0 / (3 * f)) * clamp((c["t_het"] - t) / (4 * f))
            dy = 12 * (1 - ease_out(dt0 / (5 * f)))
            items = c["items"]
            sau = []
            for i, it in enumerate(items):
                t_tat = items[i + 1]["t"] if i + 1 < len(items) else 1e9
                h = clamp((t - it["t"] + f) / (2 * f)) * clamp(1 - (t - t_tat + f) / (2 * f))
                if h <= 0:
                    self._dan(frame, it["trang"], it, k, dy)
                else:
                    sau.append((it, h))
            for it, h in sau:
                sc = 1 + self.PHONG * (0.5 - 0.5 * math.cos(math.pi * h))
                self._dan(frame, it["trang"], it, k, dy, sc)
                self._dan(frame, it["vang"], it, k * h, dy, sc)

    @staticmethod
    def _dan(frame, sp, it, alpha, dy, scale=1.0):
        if alpha <= 0.003:
            return
        r = sp["rgba"]
        x = it["x"] - sp["ox"]
        y = it["base"] - sp["oy"] + dy
        if scale != 1.0:
            cx, cy = it["x"] + it["adv"] / 2, it["base"] - sp["oy"] * 0 - 0.35 * (sp["oy"])
            im = Image.fromarray(r)
            nw, nh = int(r.shape[1] * scale), int(r.shape[0] * scale)
            r = np.asarray(im.resize((nw, nh), Image.BILINEAR))
            x = cx - (cx - x) * scale
            y = (it["base"] + dy - 0.35 * sp["oy"]) - ((it["base"] + dy - 0.35 * sp["oy"]) - y) * scale
        C.dan(frame, r, x, y, alpha)
