# -*- coding: utf-8 -*-
"""CTA KÊU GỌI FOLLOW cuối video — chủ dự án chốt 2026-10-20 (lượt Dũng Tỏi): *"đoạn cuối mỗi video
lúc nào cũng kêu gọi follow nhé, bỏ cái chữ CÒN TIẾP đi"*. Thay thẻ kết `CÒN TIẾP...` của reference.

    python cta_follow.py --t0 67.30 --dur-video 71.20 --kenh "DŨNG TỎI" --out cta.mov \
        [--dong2 "ĐỂ XEM QUÁN TIẾP THEO"] [--y 930] [--emit-box avoid.json --shift 0.1] [--still soi.png]

Bố cục (khung 1080x1920, canh giữa x 540):
  dòng 1  "FOLLOW <KÊNH>"          BVP Black, cap 70 px, chữ FOLLOW trắng + tên kênh vàng #FFD800,
                                   viền đen 0,10×cap, nén ngang 77% (cùng họ chữ với sub)
  dòng 2  "<dong2>"                BVP Black, cap 46 px, trắng
  nút     viên đỏ TikTok (254,44,85) 470×118, logo TikTok trắng (từ resources/brand-logos/tiktok.svg,
          KHÔNG tự vẽ logo) + "FOLLOW"; bấm xong đổi sang viên xám đậm "✓ ĐÃ FOLLOW"
  tay     bàn tay vector trắng viền tối (cùng hình với cta_overlay.hand của lượt KB3)
Thời gian (giây, tính từ --t0):
  0,00  dòng 1 bật 0,6→1,08→1 (8 khung) · 0,10 dòng 2 · 0,25 nút bật back-out 0→1 (12 khung)
  0,70  tay trượt vào từ dưới-phải (10 khung) · 1,30 BẤM: nút nén 0,94 (7 khung), vòng sóng 0,7 s,
  1,40  nút đổi sang ĐÃ FOLLOW · 2,00 tay trượt ra · giữ tới hết video (fade đen cuối video lo)
SFX gợi ý (đưa vào cue nns-add-sfx, mức "nghe rõ" đã duyệt): t0 quick-swoosh −7 · t0+0,32 pop-2 −3
· t0+1,30 click-button −3.
"""
import argparse, io, json, os, re, subprocess, sys
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import svgpath  # noqa: E402

ASSETS = os.path.join(os.path.dirname(HERE), "assets")          # dung-toi-edit: mọi thứ nằm trong skill
FONT = os.path.join(ASSETS, "fonts", "BeVietnamPro-Black.ttf")
W, H, FPS = 1080, 1920, 30
YEL, WHITE, INK = (255, 216, 0, 255), (255, 255, 255, 255), (0, 0, 0, 255)
RED, GRAY = (254, 44, 85, 255), (58, 58, 64, 255)
SQ = 0.77


def font_cap(cap):
    """cỡ font sao cho chữ hoa 'H' cao đúng cap px."""
    f = ImageFont.truetype(FONT, 100)
    b = f.getbbox("H")
    return ImageFont.truetype(FONT, int(round(100 * cap / (b[3] - b[1]))))


def text_sprite(parts, cap, stroke_k=0.10):
    """parts = [(chuỗi, màu)] trên MỘT dòng, viền đen đều, nén ngang SQ. Trả về RGBA."""
    f = font_cap(cap)
    sw = max(2, int(round(stroke_k * cap)))
    full = "".join(p for p, _ in parts)
    bb = f.getbbox(full, stroke_width=sw)
    im = Image.new("RGBA", (bb[2] - bb[0] + 8, bb[3] - bb[1] + 8), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    x = 4 - bb[0]
    for s, col in parts:
        d.text((x, 4 - bb[1]), s, font=f, fill=col, stroke_width=sw, stroke_fill=INK)
        x += f.getlength(s)
    return im.resize((int(im.width * SQ), im.height), Image.LANCZOS)


def tiktok_logo(px):
    src = io.open(os.path.join(ASSETS, "logos", "tiktok.svg"), encoding="utf-8").read()
    dpath = re.search(r'\sd="([^"]+)"', src).group(1)
    vb = [float(v) for v in re.search(r'viewBox="([^"]+)"', src).group(1).split()]
    m = svgpath.mask(dpath, vb, px * 2)
    m = m.crop(m.getbbox()).resize((int(px * m.width / m.height), px), Image.LANCZOS)
    im = Image.new("RGBA", m.size, (255, 255, 255, 0)); im.putalpha(m)
    return im


def button(done):
    S = 3
    w, h = 470 * S, 118 * S
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, w - 1, h - 1), radius=h // 2, fill=GRAY if done else RED)
    f = ImageFont.truetype(FONT, 50 * S)
    if done:
        lab = "ĐÃ FOLLOW"
        tw = f.getlength(lab); ck = 44 * S; gap = 18 * S
        x0 = (w - (ck + gap + tw)) / 2
        cy = h / 2
        d.line([(x0, cy), (x0 + ck * 0.38, cy + ck * 0.36), (x0 + ck, cy - ck * 0.40)],
               fill=WHITE, width=10 * S, joint="curve")
        d.text((x0 + ck + gap, cy), lab, font=f, fill=WHITE, anchor="lm")
    else:
        logo = tiktok_logo(64 * S)
        lab = "FOLLOW"
        tw = f.getlength(lab); gap = 22 * S
        x0 = (w - (logo.width + gap + tw)) / 2
        im.alpha_composite(logo, (int(x0), int((h - logo.height) / 2)))
        d.text((x0 + logo.width + gap, h / 2), lab, font=f, fill=WHITE, anchor="lm")
    im = im.resize((w // S, h // S), Image.LANCZOS)
    # bóng đổ nhẹ cho nút tách khỏi áo kẻ sọc
    pad = 24
    out = Image.new("RGBA", (im.width + 2 * pad, im.height + 2 * pad), (0, 0, 0, 0))
    sh = Image.new("RGBA", out.size, (0, 0, 0, 0))
    sh.putalpha(Image.new("L", out.size, 0))
    a = Image.new("L", out.size, 0); a.paste(im.split()[3], (pad, pad + 8))
    sh.putalpha(a.filter(ImageFilter.GaussianBlur(10)).point(lambda v: int(v * 0.55)))
    out.alpha_composite(sh); out.alpha_composite(im, (pad, pad))
    return out


def hand():
    """Bàn tay chỉ vector trắng viền tối, ngón trỏ chỉ lên-trái (giống cta_overlay.hand lượt KB3)."""
    S = 4; U = 150 * S
    im = Image.new("RGBA", (int(U * 1.3), int(U * 1.5)), (0, 0, 0, 0))

    def shapes(dr, g, col):
        dr.rounded_rectangle((0.42 * U - g, 0.05 * U - g, 0.64 * U + g, 0.80 * U + g), radius=0.11 * U + g, fill=col)
        dr.rounded_rectangle((0.36 * U - g, 0.58 * U - g, 1.12 * U + g, 1.32 * U + g), radius=0.22 * U + g, fill=col)
        for i, x in enumerate((0.62, 0.80, 0.98)):
            dr.rounded_rectangle((x * U - 0.02 * U - g, 0.55 * U + i * 0.02 * U - g, x * U + 0.17 * U + g,
                                  0.86 * U + g), radius=0.09 * U + g, fill=col)
        dr.rounded_rectangle((0.16 * U - g, 0.78 * U - g, 0.50 * U + g, 1.00 * U + g), radius=0.11 * U + g, fill=col)

    dr = ImageDraw.Draw(im)
    shapes(dr, 0.045 * U, (26, 15, 8, 255)); shapes(dr, 0, (255, 255, 255, 255))
    for x in (0.80, 0.98):
        dr.line((x * U - 0.01 * U, 0.66 * U, x * U - 0.01 * U, 0.84 * U), fill=(26, 15, 8, 255), width=int(0.025 * U))
    im = im.rotate(24, resample=Image.BICUBIC, expand=True)
    sh = im.split()[3].filter(ImageFilter.GaussianBlur(10))
    shadow = Image.new("RGBA", im.size, (0, 0, 0, 0)); shadow.putalpha(sh.point(lambda v: int(v * 0.45)))
    out = Image.alpha_composite(shadow, im)
    return out.resize((out.width // S, out.height // S), Image.LANCZOS)


def ease_out3(p):
    p = min(max(p, 0.0), 1.0); return 1 - (1 - p) ** 3


def back_out(p, s=1.9):
    p = min(max(p, 0.0), 1.0); p -= 1
    return p * p * ((s + 1) * p + s) + 1


def put(canvas, spr, cx, cy, sc=1.0, al=1.0):
    """dán sprite (RGBA float, màu ĐÃ NHÂN alpha) tâm (cx,cy), phóng sc, độ đục al — dưới-pixel.
    Làm trong không gian premultiplied: nội suy + chồng lớp màu thẳng sẽ ra viền đen quanh chữ."""
    if al <= 0.003 or sc <= 0.01:
        return
    h, w = spr.shape[:2]
    M = np.float32([[sc, 0, cx - sc * w / 2], [0, sc, cy - sc * h / 2]])
    lay = cv2.warpAffine(spr, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=0)
    lay *= al
    a = lay[..., 3:4]
    canvas[..., :3] = lay[..., :3] + canvas[..., :3] * (1 - a)
    canvas[..., 3:4] = a + canvas[..., 3:4] * (1 - a)


def f01(im):
    a = np.asarray(im).astype(np.float32) / 255.0
    a[..., :3] *= a[..., 3:4]          # nhân alpha trước
    return a


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--t0", type=float, required=True, help="mốc CTA bắt đầu (timeline file cuối)")
    ap.add_argument("--dur-video", type=float, required=True)
    ap.add_argument("--kenh", required=True)
    ap.add_argument("--dong2", default="ĐỂ XEM QUÁN TIẾP THEO")
    ap.add_argument("--y", type=int, default=930, help="tâm dòng 1")
    ap.add_argument("--out", default="")
    ap.add_argument("--still", default="")
    ap.add_argument("--emit-box", default="", help="ghi thêm hộp CTA vào json vật cản của captions.py")
    ap.add_argument("--shift", type=float, default=0.100, help="timeline cuối − timeline bản cắt")
    a = ap.parse_args()

    L1 = f01(text_sprite([("FOLLOW ", WHITE), (a.kenh.upper(), YEL)], 70))
    L2 = f01(text_sprite([(a.dong2.upper(), WHITE)], 46))
    B0, B1 = f01(button(False)), f01(button(True))
    HD = f01(hand())
    y1 = a.y; y2 = y1 + 96; yb = y2 + 124            # dấu "Ể" của dòng 2 chạm dòng 1 khi chỉ cách 84
    bx = 540
    tip = (bx + 70, yb + 18)                  # chỗ ngón trỏ chạm nút (lệch phải tâm nút)
    # đầu ngón trỏ trong sprite tay sau khi xoay 24°: ~ (0.30 W, 0.06 H) của sprite
    hx_off, hy_off = HD.shape[1] * (0.5 - 0.30), HD.shape[0] * (0.5 - 0.06)
    n = int(round((a.dur_video - a.t0) * FPS))
    # Vật cản cho captions.py: HAI hộp. Chữ + nút thì suốt CTA; bàn tay chỉ trong lúc tay có mặt.
    # Gộp làm một hộp (y tới 1410 suốt 4 s) thì nửa dưới còn 180 px ⇒ 6 khối sub rơi về FORCE.
    hw, hh = HD.shape[1], HD.shape[0]
    hand_c = (tip[0] + hx_off, tip[1] + hy_off)
    boxes = [("cta_follow", 0.0, 9.0, dict(x0=bx - 300, y0=y1 - 70, x1=min(W, bx + 300), y1=yb + 75)),
             ("cta_tay", 0.70, 2.35, dict(x0=int(hand_c[0] - hw / 2 - 10), y0=int(hand_c[1] - hh / 2 - 10),
                                          x1=int(min(W, hand_c[0] + hw / 2 + 10)), y1=int(hand_c[1] + hh / 2 + 10)))]
    if a.emit_box:
        J = json.load(open(a.emit_box, encoding="utf-8")) if os.path.exists(a.emit_box) else {"W": W, "H": H, "avoid": []}
        J["avoid"] = [r for r in J["avoid"] if r.get("ten") not in ("cta_follow", "cta_tay")]
        for ten, d0, d1, bxx in boxes:
            J["avoid"].append({"ten": ten, "t0": round(a.t0 + d0 - a.shift, 3),
                               "t1": round(min(a.t0 + d1, a.dur_video + 1) - a.shift, 3), **bxx})
            print("vật cản %-10s → %s  x %d..%d y %d..%d" % (ten, a.emit_box, bxx["x0"], bxx["x1"], bxx["y0"], bxx["y1"]))
        json.dump(J, open(a.emit_box, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
        if not (a.out or a.still):
            return

    def frame(k):
        t = k / FPS
        c = np.zeros((H, W, 4), np.float32)
        # dòng 1 / dòng 2
        for spr, yy, d0 in ((L1, y1, 0.0), (L2, y2, 0.10)):
            p = (t - d0) * FPS / 8.0
            if p <= 0:
                continue
            sc = 0.6 + 0.48 * ease_out3(min(p / 0.6, 1)) if p < 0.6 else 1.08 - 0.08 * ease_out3((p - 0.6) / 0.4)
            put(c, spr, 540, yy, sc, min(1.0, p * 2.5))
        # nút
        pb = (t - 0.25) * FPS / 12.0
        if pb > 0:
            sc = back_out(pb)
            tp = (t - 1.30) * FPS / 7.0
            if 0 <= tp <= 1:
                sc *= 1 - 0.06 * np.sin(np.pi * tp)
            spr = B1 if t >= 1.40 else B0
            put(c, spr, bx, yb, sc, min(1.0, pb * 3))
            # vòng sóng trắng khi bấm
            rp = (t - 1.30) / 0.7
            if 0 <= rp <= 1:
                ring = np.zeros((H, W), np.float32)
                cv2.ellipse(ring, (int(tip[0]), int(tip[1])), (int(40 + 150 * ease_out3(rp)),) * 2, 0, 0, 360,
                            1.0, int(10 - 6 * rp), lineType=cv2.LINE_AA)
                al = (1 - rp) * 0.9 * ring[..., None]
                c[..., :3] = al + c[..., :3] * (1 - al)          # trắng, premultiplied
                c[..., 3:4] = al + c[..., 3:4] * (1 - al)
        # tay
        if 0.70 <= t <= 2.35:
            pin = ease_out3((t - 0.70) * FPS / 10.0)
            pout = ease_out3((t - 2.00) * FPS / 10.0) if t > 2.00 else 0.0
            press = 0.0
            tp = (t - 1.22) * FPS / 9.0
            if 0 <= tp <= 1:
                press = np.sin(np.pi * tp)
            dx = (1 - pin) * 260 + pout * 300 - press * 10
            dy = (1 - pin) * 300 + pout * 320 - press * 12
            put(c, HD, tip[0] + hx_off + dx, tip[1] + hy_off + dy, 1.0 - 0.05 * press, min(pin * 1.5, 1 - pout))
        al_ = np.maximum(c[..., 3:4], 1e-6)
        c[..., :3] = np.where(c[..., 3:4] > 1e-6, c[..., :3] / al_, 0)   # về màu thẳng cho qtrle argb
        return (np.clip(c, 0, 1) * 255 + 0.5).astype(np.uint8)

    if a.still:
        Image.fromarray(frame(int(1.0 * FPS)), "RGBA").save(a.still.replace(".png", "_a.png"))
        Image.fromarray(frame(int(1.32 * FPS)), "RGBA").save(a.still.replace(".png", "_b.png"))
        Image.fromarray(frame(int(2.6 * FPS)), "RGBA").save(a.still.replace(".png", "_c.png"))
        print("-> %s _a/_b/_c" % a.still)
        return
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgba", "-s", "%dx%d" % (W, H),
                          "-r", str(FPS), "-i", "-", "-c:v", "qtrle", "-pix_fmt", "argb", a.out], stdin=subprocess.PIPE)
    for k in range(n):
        p.stdin.write(frame(k).tobytes())
    p.stdin.close()
    if p.wait():
        raise SystemExit("⛔ ffmpeg lỗi")
    print("-> %s  %d khung = %.2fs (từ %.2fs tới hết video)" % (a.out, n, n / FPS, a.t0))


if __name__ == "__main__":
    main()
