# -*- coding: utf-8 -*-
"""Hàm vẽ: chữ có viền/bóng, chữ neon, dán sprite (màn hình & mặt đất), vạch sáng, bong bóng ghim, thẻ ảnh."""
import math
import os
from functools import lru_cache

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont


FONT_THAY = {"caveat": "Pacifico.ttf", "caveatbrush": "Pacifico.ttf", "lilitaone": "PaytoneOne-Regular.ttf"}
_GLYPH = {}


def _co_glyph(path, ch):
    k = (path, ch)
    if k not in _GLYPH:
        try:
            f = ImageFont.truetype(path, 40)

            def mask(c):
                im = Image.new("L", (80, 80), 0)
                ImageDraw.Draw(im).text((10, 10), c, font=f, fill=255)
                return im.tobytes()
            _GLYPH[k] = mask(ch) != mask("ມ")
        except Exception:
            _GLYPH[k] = True
    return _GLYPH[k]


def chon_font(path, text):
    """Font không có dấu tiếng Việt (Caveat, Lilita) -> đổi sang font cùng thư mục có dấu (Pacifico, Paytone One)."""
    if not path or not text:
        return path
    ten = os.path.splitext(os.path.basename(path))[0].lower().replace("-regular", "").replace("[wght]", "")
    thay = FONT_THAY.get(ten)
    if not thay:
        return path
    for ch in set(text):
        if ord(ch) > 0x7F and not _co_glyph(path, ch):
            p2 = os.path.join(os.path.dirname(path), thay)
            return p2 if os.path.exists(p2) else path
    return path


@lru_cache(maxsize=256)
def font(path, size, dam=False):
    size = max(6, int(size))
    try:
        f = ImageFont.truetype(path, size)
    except Exception:
        f = ImageFont.load_default()
        return f
    if dam:
        try:
            f.set_variation_by_axes([700])
        except Exception:
            pass
    return f


def chu_anh(text, font_path, size, mau=(255, 255, 255), vien=0, mau_vien=(0, 0, 0), bong=0,
            mau_bong=(0, 0, 0, 160), dam=False, pad=None):
    """Chữ -> ảnh RGBA (PIL) có viền + bóng mềm."""
    font_path = chon_font(font_path, text)
    f = font(font_path, size, dam)
    pad = pad if pad is not None else int(size * 0.5 + vien + bong + 4)
    tmp = ImageDraw.Draw(Image.new("RGBA", (4, 4)))
    try:
        l, t, r, b = tmp.textbbox((0, 0), text, font=f, stroke_width=vien)
    except Exception:
        l, t, r, b = 0, 0, int(len(text) * size * 0.6), size
    w, h = r - l + 2 * pad, b - t + 2 * pad
    img = Image.new("RGBA", (max(2, w), max(2, h)), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    ox, oy = pad - l, pad - t
    if bong > 0:
        sh = Image.new("RGBA", img.size, (0, 0, 0, 0))
        ds = ImageDraw.Draw(sh)
        ds.text((ox + bong * 0.6, oy + bong * 0.8), text, font=f, fill=mau_bong, stroke_width=vien,
                stroke_fill=mau_bong)
        sh = sh.filter(ImageFilter.GaussianBlur(max(1, bong * 0.5)))
        img.alpha_composite(sh)
    d.text((ox, oy), text, font=f, fill=tuple(mau) + (255,), stroke_width=vien, stroke_fill=tuple(mau_vien) + (255,))
    return img


def chu_neon(text, font_path, size, mau=(60, 200, 255), dam=False):
    font_path = chon_font(font_path, text)
    f = font(font_path, size, dam)
    pad = int(size * 0.8)
    tmp = ImageDraw.Draw(Image.new("RGBA", (4, 4)))
    l, t, r, b = tmp.textbbox((0, 0), text, font=f)
    w, h = r - l + 2 * pad, b - t + 2 * pad
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    glow = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    dg = ImageDraw.Draw(glow)
    dg.text((pad - l, pad - t), text, font=f, fill=tuple(mau) + (255,), stroke_width=max(2, size // 12),
            stroke_fill=tuple(mau) + (255,))
    g1 = glow.filter(ImageFilter.GaussianBlur(size * 0.22))
    g2 = glow.filter(ImageFilter.GaussianBlur(size * 0.07))
    img.alpha_composite(g1)
    img.alpha_composite(g1)
    img.alpha_composite(g2)
    d = ImageDraw.Draw(img)
    sang = tuple(min(255, int(c * 0.35 + 255 * 0.65)) for c in mau)
    d.text((pad - l, pad - t), text, font=f, fill=sang + (255,))
    return img


def pil_sang_np(img):
    """PIL RGBA -> np RGBA uint8."""
    return np.asarray(img.convert("RGBA"))


def np_sang_pil(arr):
    return Image.fromarray(arr, "RGBA")


def dan_lop(dest, src, x, y, alpha=1.0):
    """Dán ảnh RGBA src lên ảnh RGBA dest tại (x,y) (có thể âm / tràn), alpha toàn cục."""
    x, y = int(round(x)), int(round(y))
    W, H = dest.size
    w, h = src.size
    x0, y0, x1, y1 = max(0, x), max(0, y), min(W, x + w), min(H, y + h)
    if x1 <= x0 or y1 <= y0:
        return
    part = src.crop((x0 - x, y0 - y, x1 - x, y1 - y))
    if alpha < 0.999:
        a = part.split()[3].point(lambda v: int(v * alpha))
        part = part.copy()
        part.putalpha(a)
    region = dest.crop((x0, y0, x1, y1))
    region.alpha_composite(part)
    dest.paste(region, (x0, y0))


def bien_hinh(rgba, cao, goc=0.0, rong=None):
    """Co giãn sprite RGBA (np) về chiều cao `cao` px (giữ tỉ lệ) rồi xoay `goc` độ (dương = thuận chiều kim đồng hồ)."""
    h, w = rgba.shape[:2]
    cao = max(2, int(round(cao)))
    rong = max(2, int(round(rong))) if rong else max(2, int(round(w * cao / h)))
    interp = cv2.INTER_AREA if cao < h else cv2.INTER_LINEAR
    img = cv2.resize(rgba, (rong, cao), interpolation=interp)
    if abs(goc) < 0.01:
        return img
    c, s = abs(math.cos(math.radians(goc))), abs(math.sin(math.radians(goc)))
    nw, nh = int(rong * c + cao * s) + 2, int(rong * s + cao * c) + 2
    M = cv2.getRotationMatrix2D((rong / 2, cao / 2), -goc, 1.0)
    M[0, 2] += nw / 2 - rong / 2
    M[1, 2] += nh / 2 - cao / 2
    return cv2.warpAffine(img, M, (nw, nh), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT,
                          borderValue=(0, 0, 0, 0))


def dan_np(frame, rgba, cx, cy, neo=(0.5, 0.5), alpha=1.0):
    """Dán sprite RGBA (np, kênh màu theo thứ tự của frame) lên frame (np BGR/RGB uint8) tại tâm (cx,cy).
    neo: điểm neo trong sprite (0..1). Sửa frame tại chỗ."""
    h, w = rgba.shape[:2]
    x = int(round(cx - neo[0] * w))
    y = int(round(cy - neo[1] * h))
    H, W = frame.shape[:2]
    x0, y0, x1, y1 = max(0, x), max(0, y), min(W, x + w), min(H, y + h)
    if x1 <= x0 or y1 <= y0:
        return
    sp = rgba[y0 - y:y1 - y, x0 - x:x1 - x]
    a = sp[..., 3:4].astype(np.float32) / 255.0 * alpha
    reg = frame[y0:y1, x0:x1].astype(np.float32)
    frame[y0:y1, x0:x1] = (reg * (1 - a) + sp[..., :3].astype(np.float32) * a).astype(np.uint8)


def rgba_pil_sang_bgra(img):
    arr = np.asarray(img.convert("RGBA"))
    return np.ascontiguousarray(arr[..., [2, 1, 0, 3]])


def cat_duong(pts, rong, cao, le):
    """Bỏ các điểm nằm xa ngoài hộp [-le, rong+le]×[-le, cao+le] (giữ điểm kề để nét không gãy)."""
    pts = np.asarray(pts, dtype=np.float32)
    trong = (pts[:, 0] >= -le) & (pts[:, 0] <= rong + le) & (pts[:, 1] >= -le) & (pts[:, 1] <= cao + le)
    if not trong.any():
        return pts[:0]
    giu = trong.copy()
    giu[1:] |= trong[:-1]
    giu[:-1] |= trong[1:]
    out = pts[giu]
    out[:, 0] = np.clip(out[:, 0], -3 * le, rong + 3 * le)
    out[:, 1] = np.clip(out[:, 1], -3 * le, cao + 3 * le)
    return out


def dia_sang(duong_kinh, mau=(255, 140, 30), alpha=1.0):
    """Đĩa sáng mờ dần ra rìa (dùng cho vệt nổ trên đất)."""
    d = max(4, int(duong_kinh))
    n = 96
    yy, xx = np.mgrid[0:n, 0:n].astype(np.float32)
    r = np.sqrt((xx - n / 2) ** 2 + (yy - n / 2) ** 2) / (n / 2)
    a = np.clip(1 - r, 0, 1) ** 1.6 * 255 * alpha
    arr = np.zeros((n, n, 4), np.uint8)
    arr[..., 0], arr[..., 1], arr[..., 2] = mau
    arr[..., 3] = a.astype(np.uint8)
    return Image.fromarray(arr, "RGBA").resize((d, d), Image.BILINEAR)


def vach_sang(pts, mau=(255, 212, 0), day=3, glow=10, alpha=1.0, net_dut=0, gioi_han=None):
    """Vẽ đường gấp khúc phát sáng. pts: (N,2) px. gioi_han=(rong,cao) để cắt phần ngoài vùng vẽ.
    Trả (ảnh RGBA PIL, (ox, oy))."""
    pts = np.asarray(pts, dtype=np.float32)
    if gioi_han is not None:
        pts = cat_duong(pts, gioi_han[0], gioi_han[1], glow * 3 + day + 8)
    if len(pts) < 2:
        return None, (0, 0)
    pad = int(glow * 3 + day + 4)
    x0, y0 = int(np.floor(pts[:, 0].min())) - pad, int(np.floor(pts[:, 1].min())) - pad
    x1, y1 = int(np.ceil(pts[:, 0].max())) + pad, int(np.ceil(pts[:, 1].max())) + pad
    w, h = max(2, x1 - x0), max(2, y1 - y0)
    if w * h > 16_000_000:
        return None, (0, 0)
    p = (pts - [x0, y0]).astype(np.int32).reshape(-1, 1, 2)
    lop = np.zeros((h, w, 4), np.uint8)
    col = (mau[0], mau[1], mau[2], 255)
    if net_dut > 0:
        # nét đứt: vẽ từng đoạn
        seg = pts - [x0, y0]
        acc, on = 0.0, True
        for i in range(len(seg) - 1):
            a, b = seg[i], seg[i + 1]
            L = float(np.hypot(*(b - a)))
            if L < 1e-3:
                continue
            s = 0.0
            while s < L:
                e = min(L, s + net_dut)
                if on:
                    pa, pb = a + (b - a) * (s / L), a + (b - a) * (e / L)
                    cv2.line(lop, tuple(np.int32(pa)), tuple(np.int32(pb)), col, day, cv2.LINE_AA)
                on = not on
                s = e
    else:
        cv2.polylines(lop, [p], False, col, day, cv2.LINE_AA)
    if glow > 0:
        k = int(glow) | 1
        gl = cv2.GaussianBlur(lop, (k * 2 + 1, k * 2 + 1), glow * 0.6)
        gl[..., 3] = np.clip(gl[..., 3].astype(np.float32) * 1.6, 0, 255).astype(np.uint8)
        out = gl.astype(np.float32)
        a = lop[..., 3:4].astype(np.float32) / 255
        out = out * (1 - a) + lop.astype(np.float32) * a
        lop = out.astype(np.uint8)
    if alpha < 0.999:
        lop[..., 3] = (lop[..., 3] * alpha).astype(np.uint8)
    return Image.fromarray(lop, "RGBA"), (x0, y0)


def vong_tron(cx, cy, r, mau=(255, 255, 255), day=3, alpha=1.0, to=None):
    """Vòng tròn (hoặc đĩa nếu to=(r,g,b,a)) -> (ảnh RGBA, (ox,oy))."""
    pad = day + 3
    R = int(math.ceil(r)) + pad
    w = h = 2 * R
    lop = np.zeros((h, w, 4), np.uint8)
    if to is not None:
        cv2.circle(lop, (R, R), int(r), tuple(int(v) for v in to), -1, cv2.LINE_AA)
    cv2.circle(lop, (R, R), int(r), (mau[0], mau[1], mau[2], int(255 * alpha)), day, cv2.LINE_AA)
    return Image.fromarray(lop, "RGBA"), (int(round(cx)) - R, int(round(cy)) - R)


def bong_bong(text, font_path, size=40, mau_chu=(20, 20, 20), nen=(255, 255, 255)):
    """Bong bóng ghim trắng có mũi nhọn chỉ xuống, chữ viết tay. Trả ảnh RGBA; mũi ở giữa cạnh dưới."""
    font_path = chon_font(font_path, text)
    f = font(font_path, size, True)
    tmp = ImageDraw.Draw(Image.new("RGBA", (4, 4)))
    l, t, r, b = tmp.textbbox((0, 0), text, font=f)
    tw, th = r - l, b - t
    px, py = int(size * 0.55), int(size * 0.3)
    w, h = tw + 2 * px, th + 2 * py
    mui = int(size * 0.45)
    img = Image.new("RGBA", (w + 16, h + mui + 16), (0, 0, 0, 0))
    sh = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ds = ImageDraw.Draw(sh)
    ds.rounded_rectangle([8 + 4, 8 + 6, 8 + w + 4, 8 + h + 6], radius=int(size * 0.25), fill=(0, 0, 0, 120))
    sh = sh.filter(ImageFilter.GaussianBlur(5))
    img.alpha_composite(sh)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([8, 8, 8 + w, 8 + h], radius=int(size * 0.25), fill=nen + (255,))
    cx = 8 + w // 2
    d.polygon([(cx - mui // 2, 8 + h - 2), (cx + mui // 2, 8 + h - 2), (cx, 8 + h + mui)], fill=nen + (255,))
    d.text((8 + px - l, 8 + py - t), text, font=f, fill=mau_chu + (255,))
    return img


def the_anh(img_rgba, rong, vien=8, bo=28, mau_vien=(255, 255, 255)):
    """Thẻ ảnh bo góc viền trắng có bóng. img_rgba: PIL. Trả PIL RGBA."""
    w0, h0 = img_rgba.size
    cao = int(rong * h0 / max(w0, 1))
    cao = min(cao, int(rong * 1.25))
    im = img_rgba.convert("RGBA").resize((rong, max(2, int(rong * h0 / max(w0, 1)))), Image.LANCZOS)
    if im.size[1] > cao:
        y = (im.size[1] - cao) // 2
        im = im.crop((0, y, rong, y + cao))
    pad = 24
    out = Image.new("RGBA", (rong + 2 * vien + 2 * pad, cao + 2 * vien + 2 * pad), (0, 0, 0, 0))
    sh = Image.new("RGBA", out.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle([pad + 6, pad + 10, pad + rong + 2 * vien + 6, pad + cao + 2 * vien + 10],
                                         radius=bo, fill=(0, 0, 0, 150))
    out.alpha_composite(sh.filter(ImageFilter.GaussianBlur(10)))
    ImageDraw.Draw(out).rounded_rectangle([pad, pad, pad + rong + 2 * vien, pad + cao + 2 * vien], radius=bo,
                                          fill=mau_vien + (255,))
    mask = Image.new("L", im.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, rong - 1, cao - 1], radius=max(2, bo - vien), fill=255)
    out.paste(im, (pad + vien, pad + vien), mask)
    return out


def to_vung(vong_px, rong, cao, mau=None, co=None, vien=(40, 20, 10), day_vien=2, day_khoi=0, alpha=1.0):
    """Tô các đa giác (danh sách mảng (N,2) px trong ROI rộng×cao).
    mau: (r,g,b) tô phẳng; co: ảnh RGBA PIL cờ sẽ kéo giãn theo hộp bao đa giác.
    Trả (ảnh RGBA PIL, (ox,oy)) hoặc (None, _)."""
    allp = np.concatenate([v for v in vong_px if len(v) >= 3], 0) if vong_px else None
    if allp is None or len(allp) == 0:
        return None, (0, 0)
    bx0, by0 = allp[:, 0].min(), allp[:, 1].min()
    bx1, by1 = allp[:, 0].max(), allp[:, 1].max()
    # vùng vẽ = hộp bao ∩ ROI (nới thêm khối)
    x0, y0 = int(max(-4, math.floor(bx0)) - 2), int(max(-4, math.floor(by0)) - 2)
    x1, y1 = int(min(rong + 4, math.ceil(bx1)) + 2), int(min(cao + 4, math.ceil(by1)) + day_khoi + 2)
    if x1 - x0 < 2 or y1 - y0 < 2:
        return None, (0, 0)
    w, h = x1 - x0, y1 - y0
    if w * h > 30_000_000:
        return None, (0, 0)
    mask = Image.new("L", (w, h), 0)
    dm = ImageDraw.Draw(mask)
    for v in vong_px:
        if len(v) >= 3:
            dm.polygon([(float(p[0] - x0), float(p[1] - y0)) for p in v], fill=255)
    m = np.asarray(mask)
    out_np = np.zeros((h, w, 4), np.uint8)
    if day_khoi > 0:
        # khối dày: mặt bên tối, là mặt nạ dịch xuống 1..day_khoi px
        mk = m.copy()
        for k in range(1, day_khoi + 1):
            mk[k:] |= m[:-k]
        toi = tuple(int(c * 0.45) for c in (mau or (200, 60, 30)))
        out_np[..., 0], out_np[..., 1], out_np[..., 2] = toi
        out_np[..., 3] = mk
    out = Image.fromarray(out_np, "RGBA")
    if co is not None:
        fw, fh = max(2, int(bx1 - bx0)), max(2, int(by1 - by0))
        # chỉ resize phần cờ ứng với vùng vẽ (tránh ảnh khổng lồ khi zoom sâu)
        cw, ch = co.size
        sx0, sy0 = (x0 - bx0) / fw * cw, (y0 - by0) / fh * ch
        sx1, sy1 = (x1 - bx0) / fw * cw, (y1 - by0) / fh * ch
        l_, t_ = min(int(max(0, sx0)), cw - 1), min(int(max(0, sy0)), ch - 1)
        r_, b_ = max(l_ + 1, int(min(cw, max(sx0 + 1, sx1)))), max(t_ + 1, int(min(ch, max(sy0 + 1, sy1))))
        crop = co.crop((l_, t_, r_, b_))
        dx = int(max(0, -sx0) / cw * fw)
        dy = int(max(0, -sy0) / ch * fh)
        cw2 = max(2, int(round(crop.size[0] / cw * fw)))
        ch2 = max(2, int(round(crop.size[1] / ch * fh)))
        if cw2 * ch2 > 40_000_000:
            cw2, ch2 = w, h
        fill = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        fill.paste(crop.convert("RGBA").resize((cw2, ch2), Image.BILINEAR), (dx, dy))
        fill_np = np.asarray(fill).astype(np.float32)
        fill_np[..., :3] = fill_np[..., :3] * 0.92 + 10
        fill = Image.fromarray(np.clip(fill_np, 0, 255).astype(np.uint8), "RGBA")
        out.paste(fill, (0, 0), mask)
    else:
        arr = np.asarray(out).copy()
        sel = m > 0
        arr[sel, 0], arr[sel, 1], arr[sel, 2] = mau
        arr[sel, 3] = 255
        out = Image.fromarray(arr, "RGBA")
    if day_vien > 0:
        d = ImageDraw.Draw(out)
        for v in vong_px:
            if len(v) >= 3:
                pts = [(float(p[0] - x0), float(p[1] - y0)) for p in v]
                d.line(pts + [pts[0]], fill=tuple(vien) + (255,), width=day_vien)
    if alpha < 0.999:
        a = out.split()[3].point(lambda v: int(v * alpha))
        out.putalpha(a)
    return out, (x0, y0)


def mat_na_vung(vong_px, w, h, ox, oy):
    mask = Image.new("L", (w, h), 0)
    dm = ImageDraw.Draw(mask)
    for v in vong_px:
        if len(v) >= 3:
            dm.polygon([(float(p[0] - ox), float(p[1] - oy)) for p in v], fill=255)
    return mask


def manh_vo(img_rgba, so_manh=26, seed=1):
    """Cắt ảnh RGBA thành mảnh Voronoi. Trả list (ảnh mảnh PIL, (ox,oy), (cx,cy) tâm mảnh)."""
    arr = np.asarray(img_rgba.convert("RGBA"))
    h, w = arr.shape[:2]
    rng = np.random.default_rng(seed)
    ys, xs = np.nonzero(arr[..., 3] > 10)
    if len(xs) < 10:
        return []
    idx = rng.choice(len(xs), size=min(so_manh, len(xs)), replace=False)
    seeds = np.stack([xs[idx], ys[idx]], 1).astype(np.float32)
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    # nhãn Voronoi (tính theo khối để tiết kiệm RAM)
    lab = np.zeros((h, w), np.int32)
    best = np.full((h, w), np.inf, np.float32)
    for i, (sx, sy) in enumerate(seeds):
        d = (xx - sx) ** 2 + (yy - sy) ** 2
        m = d < best
        best[m] = d[m]
        lab[m] = i
    out = []
    for i in range(len(seeds)):
        m = (lab == i) & (arr[..., 3] > 10)
        if not m.any():
            continue
        ys2, xs2 = np.nonzero(m)
        x0, x1, y0, y1 = xs2.min(), xs2.max() + 1, ys2.min(), ys2.max() + 1
        piece = arr[y0:y1, x0:x1].copy()
        piece[..., 3] = piece[..., 3] * m[y0:y1, x0:x1]
        out.append((Image.fromarray(piece, "RGBA"), (int(x0), int(y0)),
                    (float(xs2.mean()), float(ys2.mean()))))
    return out


def nap_sprite(path):
    """Đọc PNG RGBA -> np RGBA (kênh RGB) hoặc None."""
    if not path or not os.path.exists(path):
        return None
    img = cv2.imread(path, cv2.IMREAD_UNCHANGED)
    if img is None:
        return None
    if img.ndim == 2:
        img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGRA)
    elif img.shape[2] == 3:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2BGRA)
    return np.ascontiguousarray(img[..., [2, 1, 0, 3]])


def rgba_sang_bgra(rgba):
    return np.ascontiguousarray(rgba[..., [2, 1, 0, 3]])
