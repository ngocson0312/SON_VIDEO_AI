"""Bubble / tiêu đề vẽ bằng PIL (gradient, bóng mềm, viền sáng, icon) → PNG trong suốt, ffmpeg phủ lên có hiệu ứng.
Đẹp hơn nhiều so với vẽ bằng ASS. Siêu lấy mẫu x2 để mép mịn."""
import math, os
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
FONT = os.path.join(os.path.dirname(HERE), "assets", "fonts", "BeVietnamPro-Black.ttf")
SS = 2
NAVY = (14, 22, 40)
Y1, Y2 = (255, 232, 96), (255, 170, 0)       # vàng gradient
R1, R2 = (255, 110, 110), (214, 32, 60)      # đỏ gradient
WHITE = (255, 255, 255)


def F(sz):
    return ImageFont.truetype(FONT, int(sz * SS))


def vgrad(w, h, c1, c2):
    t = np.linspace(0, 1, h)[:, None, None]
    a = np.array(c1)[None, None, :] * (1 - t) + np.array(c2)[None, None, :] * t
    return Image.fromarray(np.repeat(a, w, axis=1).astype("uint8"), "RGB")


def rmask(w, h, r):
    m = Image.new("L", (w, h), 0)
    ImageDraw.Draw(m).rounded_rectangle((0, 0, w - 1, h - 1), radius=r, fill=255)
    return m


def drop_shadow(canvas_size, mask, xy, blur=14, dy=10, opacity=130):
    sh = Image.new("L", canvas_size, 0)
    sh.paste(mask, (xy[0], xy[1] + dy * SS))
    sh = sh.filter(ImageFilter.GaussianBlur(blur * SS))
    out = Image.new("RGBA", canvas_size, (0, 0, 0, 0))
    out.putalpha(sh.point(lambda v: int(v * opacity / 255)))
    return out


def sparkle(d, cx, cy, r, fill=WHITE):
    pts = []
    for i in range(8):
        a = math.pi / 4 * i - math.pi / 2
        rr = r if i % 2 == 0 else r * 0.28
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    d.polygon(pts, fill=fill)


def pin_icon(d, cx, cy, r, fill=WHITE, hole=NAVY):
    d.ellipse((cx - r, cy - r * 1.15, cx + r, cy + r * 0.85), fill=fill)
    d.polygon([(cx - r * 0.78, cy + r * 0.35), (cx + r * 0.78, cy + r * 0.35), (cx, cy + r * 1.75)], fill=fill)
    d.ellipse((cx - r * 0.38, cy - r * 0.55, cx + r * 0.38, cy + r * 0.21), fill=hole)


def ff_icon(d, cx, cy, r, fill=WHITE):
    for off in (-r * 0.55, r * 0.55):
        d.polygon([(cx + off - r * 0.5, cy - r * 0.7), (cx + off - r * 0.5, cy + r * 0.7), (cx + off + r * 0.5, cy)], fill=fill)


def pill(text, size=64, c1=Y1, c2=Y2, txt=NAVY, icon="pin", path="pill.png"):
    """Nhãn: viên thuốc gradient + viền trắng + bóng + huy hiệu tròn có icon. Trả (path, w, h, pad)."""
    f = F(size)
    h = int(size * 1.9 * SS)
    bd = int(h * 0.68)
    tw = int(f.getlength(text))
    w = int(h * 0.16 + bd + 26 * SS + tw + h * 0.5)
    pad = 46 * SS
    CW, CH = w + 2 * pad, h + 2 * pad + 8 * SS
    img = Image.new("RGBA", (CW, CH), (0, 0, 0, 0))
    m = rmask(w, h, h // 2)
    img.alpha_composite(drop_shadow((CW, CH), m, (pad, pad), blur=12, dy=9, opacity=120))
    body = vgrad(w, h, c1, c2).convert("RGBA")
    body.putalpha(m)
    d = ImageDraw.Draw(body)
    # gloss: dải sáng nửa trên
    gl = Image.new("L", (w, h), 0)
    ImageDraw.Draw(gl).rounded_rectangle((int(h * 0.12), int(h * 0.07), w - int(h * 0.12), int(h * 0.5)), radius=h // 4, fill=70)
    body.alpha_composite(Image.merge("RGBA", (Image.new("L", (w, h), 255),) * 3 + (gl,)))
    d.rounded_rectangle((0, 0, w - 1, h - 1), radius=h // 2, outline=(255, 255, 255, 235), width=3 * SS)
    # huy hiệu
    bx, by = int(h * 0.16), (h - bd) // 2
    d.ellipse((bx, by, bx + bd, by + bd), fill=NAVY + (255,))
    d.ellipse((bx + 3 * SS, by + 3 * SS, bx + bd - 3 * SS, by + bd - 3 * SS), outline=(255, 255, 255, 60), width=2 * SS)
    if icon == "pin":
        pin_icon(d, bx + bd / 2, by + bd / 2 - bd * 0.04, bd * 0.2)
    elif icon == "ff":
        ff_icon(d, bx + bd / 2, by + bd / 2, bd * 0.2)
    d.text((bx + bd + 26 * SS, h / 2 + size * 0.04 * SS), text, font=f, fill=txt + (255,), anchor="lm")
    img.alpha_composite(body, (pad, pad))
    img = img.resize((CW // SS, CH // SS), Image.LANCZOS)
    img.save(path)
    return path, img.width, img.height, pad // SS


def _text_run(parts, size):
    """parts: [(chữ, is_hi)] → độ rộng tổng"""
    f = F(size)
    return sum(f.getlength(t) for t, _ in parts)


def title_card(lines, hi, y_pad=0, pov="POV:", path="title.png", W=1080):
    """Tiêu đề: viên vàng nghiêng 'POV:' + các dòng trắng viền navy dày, từ khoá vàng gradient, lấp lánh. Canvas rộng 1080."""
    CW = W * SS
    sizeP, sizeL = 150, 108
    while max(F(sizeL).getlength(l) for l in lines) > (W - 150) * SS and sizeL > 50:
        sizeL -= 2
    fP, fL = F(sizeP), F(sizeL)
    ph = int(sizeP * 1.55 * SS)
    pw = int(fP.getlength(pov) + 130 * SS)
    lh = int(sizeL * 1.28 * SS)
    CH = ph + 60 * SS + lh * len(lines) + 110 * SS
    img = Image.new("RGBA", (CW, CH), (0, 0, 0, 0))
    # --- viên POV (xoay -3°)
    badge = Image.new("RGBA", (pw + 80 * SS, ph + 80 * SS), (0, 0, 0, 0))
    m = rmask(pw, ph, ph // 2)
    bm = Image.new("L", badge.size, 0); bm.paste(m, (40 * SS, 40 * SS))
    badge.alpha_composite(drop_shadow(badge.size, m, (40 * SS, 40 * SS), blur=12, dy=10, opacity=140))
    body = vgrad(pw, ph, Y1, Y2).convert("RGBA"); body.putalpha(m)
    d = ImageDraw.Draw(body)
    gl = Image.new("L", (pw, ph), 0)
    ImageDraw.Draw(gl).rounded_rectangle((int(ph * 0.1), int(ph * 0.06), pw - int(ph * 0.1), int(ph * 0.48)), radius=ph // 4, fill=75)
    body.alpha_composite(Image.merge("RGBA", (Image.new("L", (pw, ph), 255),) * 3 + (gl,)))
    d.rounded_rectangle((0, 0, pw - 1, ph - 1), radius=ph // 2, outline=(255, 255, 255, 240), width=4 * SS)
    d.text((pw / 2, ph / 2 + 6 * SS), pov, font=fP, fill=NAVY + (255,), anchor="mm")
    badge.alpha_composite(body, (40 * SS, 40 * SS))
    badge = badge.rotate(3, resample=Image.BICUBIC, expand=False)
    img.alpha_composite(badge, ((CW - badge.width) // 2, 0))
    # --- các dòng
    y = ph + 50 * SS
    for line in lines:
        # tách theo từ khoá
        parts, rest = [], line
        marks = []
        for w_ in hi:
            i = rest.find(w_)
            while i >= 0:
                marks.append((i, i + len(w_)))
                i = rest.find(w_, i + 1)
        marks.sort()
        pos = 0
        for a, b in marks:
            if a > pos:
                parts.append((rest[pos:a], False))
            parts.append((rest[a:b], True)); pos = b
        if pos < len(rest):
            parts.append((rest[pos:], False))
        total = _text_run(parts, sizeL)
        x = (CW - total) / 2
        layer = Image.new("RGBA", (CW, lh + 70 * SS), (0, 0, 0, 0))
        stroke = Image.new("L", layer.size, 0)
        ds = ImageDraw.Draw(stroke)
        fill_mask_w = Image.new("L", layer.size, 0); dw = ImageDraw.Draw(fill_mask_w)
        fill_mask_y = Image.new("L", layer.size, 0); dy_ = ImageDraw.Draw(fill_mask_y)
        cx = x
        for t, ish in parts:
            ds.text((cx, lh * 0.92), t, font=fL, fill=255, anchor="ls", stroke_width=13 * SS, stroke_fill=255)
            (dy_ if ish else dw).text((cx, lh * 0.92), t, font=fL, fill=255, anchor="ls")
            cx += fL.getlength(t)
        # bóng
        sh = stroke.filter(ImageFilter.GaussianBlur(9 * SS))
        shl = Image.new("RGBA", layer.size, (0, 0, 0, 0)); shl.putalpha(sh.point(lambda v: int(v * 0.55)))
        sl2 = Image.new("RGBA", layer.size, (0, 0, 0, 0)); sl2.paste(shl, (0, 9 * SS))
        layer.alpha_composite(sl2)
        navy = Image.new("RGBA", layer.size, NAVY + (255,)); navy.putalpha(stroke)
        layer.alpha_composite(navy)
        wh = Image.new("RGBA", layer.size, WHITE + (255,)); wh.putalpha(fill_mask_w)
        layer.alpha_composite(wh)
        yl = vgrad(layer.width, layer.height, Y1, Y2).convert("RGBA"); yl.putalpha(fill_mask_y)
        layer.alpha_composite(yl)
        img.alpha_composite(layer, (0, int(y)))
        y += lh
    # lấp lánh
    d = ImageDraw.Draw(img)
    sparkle(d, CW * 0.2, ph * 0.35, 30 * SS)
    sparkle(d, CW * 0.84, ph * 0.18, 22 * SS)
    sparkle(d, CW * 0.9, ph + 10 * SS, 18 * SS)
    img = img.resize((CW // SS, CH // SS), Image.LANCZOS)
    img.save(path)
    return path, img.width, img.height


def title_flat(lines, hi, pov="POV:", path="title.png", W=1080):
    """Tiêu đề kiểu phẳng (theo ảnh khách gửi 18/11): ô 'POV:' vàng phẳng chữ tối + dòng trắng đậm đổ bóng mềm, từ khoá vàng."""
    CW = W * SS
    sizeP, sizeL = 56, 72
    while max(F(sizeL).getlength(l) for l in lines) > (W - 140) * SS and sizeL > 40:
        sizeL -= 2
    fP, fL = F(sizeP), F(sizeL)
    pw = int(fP.getlength(pov) + 44 * SS); ph = int(sizeP * 1.45 * SS)
    lh = int(sizeL * 1.3 * SS)
    CH = ph + 24 * SS + lh * len(lines) + 40 * SS
    img = Image.new("RGBA", (CW, CH), (0, 0, 0, 0))
    # ô POV: vàng phẳng, hơi nghiêng
    bd = Image.new("RGBA", (pw + 40 * SS, ph + 40 * SS), (0, 0, 0, 0))
    ImageDraw.Draw(bd).rounded_rectangle((20 * SS, 20 * SS, 20 * SS + pw, 20 * SS + ph), radius=8 * SS, fill=(255, 216, 0, 255))
    ImageDraw.Draw(bd).text((20 * SS + pw / 2, 20 * SS + ph / 2 + 3 * SS), pov, font=fP, fill=(20, 20, 20, 255), anchor="mm")
    bd = bd.transform(bd.size, Image.AFFINE, (1, 0.12, -0.12 * bd.height / 2, 0, 1, 0), resample=Image.BICUBIC)
    sh = bd.split()[3].filter(ImageFilter.GaussianBlur(6 * SS))
    shl = Image.new("RGBA", bd.size, (0, 0, 0, 0)); shl.putalpha(sh.point(lambda v: int(v * 0.5)))
    bx = (CW - bd.width) // 2
    img.alpha_composite(shl, (bx, 4 * SS)); img.alpha_composite(bd, (bx, 0))
    y = ph + 22 * SS
    for line in lines:
        marks = []
        for w_ in hi:
            i = line.find(w_)
            while i >= 0:
                marks.append((i, i + len(w_))); i = line.find(w_, i + 1)
        marks.sort(); parts, pos = [], 0
        for a, b in marks:
            if a > pos: parts.append((line[pos:a], False))
            parts.append((line[a:b], True)); pos = b
        if pos < len(line): parts.append((line[pos:], False))
        total = sum(fL.getlength(t) for t, _ in parts)
        layer = Image.new("RGBA", (CW, lh + 30 * SS), (0, 0, 0, 0))
        mw = Image.new("L", layer.size, 0); my = Image.new("L", layer.size, 0)
        dw, dy_ = ImageDraw.Draw(mw), ImageDraw.Draw(my)
        cx = (CW - total) / 2
        for t, ish in parts:
            (dy_ if ish else dw).text((cx, lh * 0.9), t, font=fL, fill=255, anchor="ls"); cx += fL.getlength(t)
        allm = Image.composite(Image.new("L", layer.size, 255), Image.new("L", layer.size, 0), Image.eval(Image.merge("L", (mw,)), lambda v: 255 if v else 0))
        union = Image.eval(Image.blend(mw, my, 0.5), lambda v: 255 if v else 0)
        shd = union.filter(ImageFilter.GaussianBlur(5 * SS))
        shl = Image.new("RGBA", layer.size, (0, 0, 0, 0)); shl.putalpha(shd.point(lambda v: min(255, int(v * 0.9))))
        l2 = Image.new("RGBA", layer.size, (0, 0, 0, 0)); l2.paste(shl, (0, 4 * SS)); layer.alpha_composite(l2)
        wh = Image.new("RGBA", layer.size, (255, 255, 255, 255)); wh.putalpha(mw); layer.alpha_composite(wh)
        yl = Image.new("RGBA", layer.size, (255, 216, 0, 255)); yl.putalpha(my); layer.alpha_composite(yl)
        img.alpha_composite(layer, (0, int(y))); y += lh
    img = img.resize((CW // SS, CH // SS), Image.LANCZOS)
    img.save(path)
    return path, img.width, img.height


if __name__ == "__main__":
    pill("KHU TẬP GYM", path="t_pill.png")
    pill("TUA NHANH x2", c1=R1, c2=R2, txt=WHITE, icon="ff", size=52, path="t_badge.png")
    title_card(["BẠN LÀ HLV ĐÓN KHÁCH", "VÀO PHÒNG TẬP"], ["HLV"], path="t_title.png")
    title_flat(["BẠN LÀ HLV ĐÓN KHÁCH", "VÀO PHÒNG TẬP"], ["HLV"], path="t_flat.png")
