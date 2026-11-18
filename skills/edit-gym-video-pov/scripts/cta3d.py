# -*- coding: utf-8 -*-
"""CTA cuối video kiểu 3D (khách chốt 18/11/2026): CHỈ nút FOLLOW 3D (khối đỏ có độ dày, bóng, viền sáng) + BÀN TAY 3D
trượt lên rồi bấm LIÊN TỤC (nút lún xuống, vòng sóng, tia lấp lánh), lặp suốt đoạn cuối. Không chữ phụ.

    python cta3d.py --dur 4.6 --out ov_cta.mov [--y 930] [--taps 1.3,2.3,3.3,4.3] [--still s.png]
Taps mặc định mỗi 1,0 s kể từ 1,3 s. Ra .mov qtrle có alpha 1080x1920 30 fps."""
import argparse, os, subprocess, sys
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import cta_follow as cf  # noqa: E402

W, H, FPS = 1080, 1920, 30
FONT = cf.FONT
BW, BH, DEPTH = 640, 168, 26
S = 3


def f01(im):
    a = np.asarray(im).astype(np.float32) / 255.0
    a[..., :3] *= a[..., 3:4]
    return a


def vgrad(w, h, c1, c2):
    t = np.linspace(0, 1, h)[:, None, None]
    a = np.array(c1)[None, None, :] * (1 - t) + np.array(c2)[None, None, :] * t
    return Image.fromarray(np.repeat(a, w, axis=1).astype("uint8"), "RGB")


def button3d(p):
    """p = độ lún 0..1. Trả sprite RGBA (có bóng) — khối: thân sẫm + mặt đỏ gradient + bóng sáng + logo + chữ."""
    w, h, d = BW * S, BH * S, DEPTH * S
    pad = 60 * S
    CW, CH = w + 2 * pad, h + d + 2 * pad
    img = Image.new("RGBA", (CW, CH), (0, 0, 0, 0))
    r = h // 2
    off = int(p * (d - 6 * S))                     # mặt lún xuống
    # bóng đổ mềm dưới sàn
    sh = Image.new("L", (CW, CH), 0)
    ImageDraw.Draw(sh).rounded_rectangle((pad + 10 * S, pad + d + 14 * S, pad + w - 10 * S, pad + h + d + 14 * S), radius=r, fill=255)
    sh = sh.filter(ImageFilter.GaussianBlur(18 * S))
    shl = Image.new("RGBA", (CW, CH), (0, 0, 0, 0)); shl.putalpha(sh.point(lambda v: int(v * 0.6)))
    img.alpha_composite(shl)
    # thân (độ dày): đỏ sẫm
    side = Image.new("RGBA", (CW, CH), (0, 0, 0, 0))
    ds = ImageDraw.Draw(side)
    ds.rounded_rectangle((pad, pad + d, pad + w, pad + h + d), radius=r, fill=(150, 14, 44, 255))
    ds.rounded_rectangle((pad, pad + d, pad + w, pad + h + d), radius=r, outline=(110, 8, 32, 255), width=3 * S)
    img.alpha_composite(side)
    # mặt
    fw, fh = w, h
    face = vgrad(fw, fh, (255, 96, 128), (240, 30, 78)).convert("RGBA")
    m = Image.new("L", (fw, fh), 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, fw - 1, fh - 1), radius=r, fill=255)
    face.putalpha(m)
    gl = Image.new("L", (fw, fh), 0)
    ImageDraw.Draw(gl).rounded_rectangle((int(fh * 0.10), int(fh * 0.07), fw - int(fh * 0.10), int(fh * 0.50)), radius=int(fh * 0.25), fill=85)
    gl = gl.filter(ImageFilter.GaussianBlur(2 * S))
    face.alpha_composite(Image.merge("RGBA", (Image.new("L", (fw, fh), 255),) * 3 + (gl,)))
    dr = ImageDraw.Draw(face)
    dr.rounded_rectangle((0, 0, fw - 1, fh - 1), radius=r, outline=(255, 210, 220, 255), width=4 * S)
    # logo + chữ
    f = ImageFont.truetype(FONT, int(fh * 0.44))
    lab = "FOLLOW"
    cx_, cy_ = fw / 2, fh / 2
    dr.text((cx_, cy_ + 5 * S), lab, font=f, fill=(120, 8, 36, 200), anchor="mm")   # bóng chữ
    dr.text((cx_, cy_), lab, font=f, fill=(255, 255, 255, 255), anchor="mm")
    img.alpha_composite(face, (pad, pad + off))
    return img.resize((CW // S, CH // S), Image.LANCZOS), (pad // S, pad // S)


def hand3d():
    """Bàn tay con trỏ 3D kiểu icon 'hand cursor' (mẫu khách gửi 18/11): mặt trắng-xám bóng, viền đen mảnh, 4 ngón có rãnh,
    khối dày màu đen nhô ra phía dưới-trái, nghiêng ~22° về trái. Trả (sprite, (tx, ty)) = đầu ngón trỏ."""
    SSx = 4
    U = 600 * SSx
    pad = int(0.18 * U)
    CW, CH = int(0.95 * U) + 2 * pad, int(1.02 * U) + 2 * pad

    def sil(dx=0.0, dy=0.0, grow=0):
        m = Image.new("L", (CW, CH), 0); d = ImageDraw.Draw(m)
        def cap(p1, p2, w):
            r = w * U / 2 + grow
            q1 = (p1[0] * U + pad + dx, p1[1] * U + pad + dy); q2 = (p2[0] * U + pad + dx, p2[1] * U + pad + dy)
            d.line([q1, q2], fill=255, width=int(2 * r))
            for q in (q1, q2):
                d.ellipse((q[0] - r, q[1] - r, q[0] + r, q[1] + r), fill=255)
        cap((0.25, 0.00), (0.27, 0.58), 0.17)        # ngón trỏ (cao nhất)
        cap((0.445, 0.32), (0.445, 0.58), 0.155)      # giữa
        cap((0.61, 0.36), (0.61, 0.60), 0.150)        # áp út
        cap((0.765, 0.43), (0.765, 0.62), 0.145)      # út
        cap((0.27, 0.74), (0.06, 0.62), 0.165)        # ngón cái (bướu dưới-trái)
        pal = [(0.19, 0.50), (0.84, 0.50), (0.865, 0.74), (0.76, 0.90), (0.66, 1.00), (0.32, 1.00), (0.20, 0.78)]
        d.polygon([(x * U + pad + dx, y * U + pad + dy) for x, y in pal], fill=255)
        if grow:
            pass
        return m
    flat = sil()
    # khối dày: nhiều lớp dịch xuống-trái, tối dần
    depth = int(0.065 * U); steps = 26
    img = Image.new("RGBA", (CW, CH), (0, 0, 0, 0))
    for i in range(steps, 0, -1):
        t = i / steps
        m = sil(-t * depth * 0.95, t * depth * 0.55)
        g = int(18 + 40 * (1 - t))
        lay = Image.new("RGBA", (CW, CH), (g, g, g + 4, 255)); lay.putalpha(m)
        img.alpha_composite(lay)
    # viền đen quanh mặt
    edge = flat.filter(ImageFilter.MaxFilter(2 * int(0.014 * U) + 1))
    ed = Image.new("RGBA", (CW, CH), (8, 8, 10, 255)); ed.putalpha(edge); img.alpha_composite(ed)
    # mặt: trắng → xám nhạt (gradient dọc) + dải bóng trên mặt bàn tay
    fh = np.asarray(flat).astype(np.float32) / 255.0
    yy = np.linspace(0, 1, CH)[:, None]
    base = 255 - 38 * np.clip((yy - 0.45) / 0.55, 0, 1)
    face = np.dstack([np.repeat(base, CW, 1)] * 3)
    gloss = np.clip(1 - np.abs((yy - 0.64) / 0.05), 0, 1) * 0.0
    fimg = Image.fromarray(np.clip(face, 0, 255).astype("uint8"), "RGB").convert("RGBA")
    inner = flat.filter(ImageFilter.MinFilter(2 * int(0.006 * U) + 1))
    fimg.putalpha(inner)
    img.alpha_composite(fimg)
    d = ImageDraw.Draw(img)
    lw = int(0.014 * U)
    for x in (0.355, 0.527, 0.688):                  # rãnh giữa các ngón
        d.line([(x * U + pad, 0.40 * U + pad), (x * U + pad, 0.60 * U + pad)], fill=(8, 8, 10, 255), width=lw)
    # vệt sáng cong ở mu bàn tay
    hl = Image.new("L", (CW, CH), 0); dh = ImageDraw.Draw(hl)
    dh.ellipse((0.22 * U + pad, 0.60 * U + pad, 0.92 * U + pad, 0.78 * U + pad), fill=70)
    hl = Image.fromarray(np.minimum(np.asarray(hl), np.asarray(inner)).astype("uint8")).filter(ImageFilter.GaussianBlur(12))
    hli = Image.new("RGBA", (CW, CH), (255, 255, 255, 255)); hli.putalpha(hl); img.alpha_composite(hli)
    out = img.rotate(24, resample=Image.BICUBIC, expand=True)
    m = np.asarray(out)[..., 3] > 200
    ys, xs = np.nonzero(m)
    k = np.argmin(ys + 0.0 * xs)
    tip = (xs[k], ys[k] + int(0.01 * U))
    sh = Image.new("L", out.size, 0); sh.paste(out.split()[3], (20, 36)); sh = sh.filter(ImageFilter.GaussianBlur(26))
    shl = Image.new("RGBA", out.size, (0, 0, 0, 0)); shl.putalpha(sh.point(lambda v: int(v * 0.42)))
    res = Image.alpha_composite(shl, out)
    tgt = 400 / res.width
    res = res.resize((int(res.width * tgt), int(res.height * tgt)), Image.LANCZOS)
    return res, (tip[0] * tgt, tip[1] * tgt)


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--dur", type=float, default=4.6)
    ap.add_argument("--out", default="")
    ap.add_argument("--still", default="")
    ap.add_argument("--y", type=int, default=930)
    ap.add_argument("--taps", default="")
    a = ap.parse_args()
    taps = [float(x) for x in a.taps.split(",")] if a.taps else [1.3]  # CHỈ BẤM 1 LẦN
    n = int(round(a.dur * FPS))
    levels = 9
    B = [f01(button3d(i / (levels - 1))[0]) for i in range(levels)]
    pad = button3d(0)[1][0]
    hsp, htip = hand3d()
    HD = f01(hsp)
    bx, by = 540, a.y
    # đầu ngón trỏ chạm mặt nút (lệch phải tâm nút)
    tip = (bx + 120, by + 10)
    HS = 1.0
    hx_off, hy_off = HS * (HD.shape[1] / 2 - htip[0]), HS * (HD.shape[0] / 2 - htip[1])
    rng = np.random.RandomState(7)
    spark = [(rng.uniform(0, 2 * np.pi), rng.uniform(70, 190), rng.uniform(5, 11)) for _ in range(10)]

    def press_of(t):
        for tk in taps:
            u = (t - tk)
            if -0.18 <= u < 0:        # tay hạ xuống
                return 0.0, (u + 0.18) / 0.18
            if 0 <= u < 0.34:         # lún rồi bật lại
                return float(np.sin(np.pi * min(u / 0.34, 1.0)) ** 0.7), 1.0
        return 0.0, 0.0

    def frame(k):
        t = k / FPS
        c = np.zeros((H, W, 4), np.float32)
        # nút: nảy vào + nhấp nhô nhẹ
        pb = (t - 0.05) / 0.45
        if pb > 0:
            sc = cf.back_out(pb)
            bob = 6 * np.sin(2 * np.pi * (t - 0.5) / 1.6) if t > 0.5 else 0
            pr, _ = press_of(t)
            li = int(round(pr * (levels - 1)))
            sc *= 1 - 0.035 * pr
            cf.put(c, B[li], bx, by + bob + pr * 8, sc, min(1.0, pb * 3))
        # vòng sóng + tia lấp lánh mỗi lần bấm
        for tk in taps:
            rp = (t - tk) / 0.6
            if 0 <= rp <= 1:
                ring = np.zeros((H, W), np.float32)
                cv2.ellipse(ring, (int(tip[0] - 10), int(tip[1])), (int(46 + 170 * cf.ease_out3(rp)),) * 2, 0, 0, 360,
                            1.0, max(2, int(11 - 8 * rp)), lineType=cv2.LINE_AA)
                al = (1 - rp) * 0.85 * ring[..., None]
                c[..., :3] = al + c[..., :3] * (1 - al)
                c[..., 3:4] = al + c[..., 3:4] * (1 - al)
                for ang, dist, rad in spark:
                    px_, py_ = tip[0] - 10 + np.cos(ang) * dist * cf.ease_out3(rp), tip[1] + np.sin(ang) * dist * cf.ease_out3(rp)
                    sp = np.zeros((H, W), np.float32)
                    cv2.circle(sp, (int(px_), int(py_)), int(max(1, rad * (1 - rp))), 1.0, -1, lineType=cv2.LINE_AA)
                    al2 = (1 - rp) * sp[..., None]
                    col = np.array([1.0, 0.85, 0.2], np.float32)
                    c[..., :3] = al2 * col + c[..., :3] * (1 - al2)
                    c[..., 3:4] = al2 + c[..., 3:4] * (1 - al2)
        # tay: trượt lên (0.5-1.1 s), lơ lửng nhấp nhô, hạ xuống bấm theo nhịp, giữ tới hết
        if t >= 0.5:
            pin = cf.ease_out3((t - 0.5) / 0.6)
            hover = 14 * np.sin(2 * np.pi * (t - 0.9) / 1.0)
            pr, appr = press_of(t)
            near = 70 * (1 - appr) if appr > 0 else 70
            # tiến sát nút khi sắp bấm
            ddx = (1 - pin) * 300 + near * 0.55
            ddy = (1 - pin) * 520 + near + hover * (1 - appr) - pr * 6
            sc = HS * (1.0 - 0.04 * pr)
            cf.put(c, HD, tip[0] + hx_off + ddx, tip[1] + hy_off + ddy, sc, min(pin * 1.6, 1.0))
        al_ = np.maximum(c[..., 3:4], 1e-6)
        c[..., :3] = np.where(c[..., 3:4] > 1e-6, c[..., :3] / al_, 0)
        return (np.clip(c, 0, 1) * 255 + 0.5).astype(np.uint8)

    if a.still:
        for nm, tt in (("a", 1.0), ("b", taps[0] + 0.12), ("c", 2.0)):
            Image.fromarray(frame(int(tt * FPS)), "RGBA").save(a.still.replace(".png", f"_{nm}.png"))
        print("still ok"); return
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{W}x{H}", "-r", str(FPS),
                          "-i", "-", "-c:v", "qtrle", "-pix_fmt", "argb", a.out], stdin=subprocess.PIPE)
    for k in range(n):
        p.stdin.write(frame(k).tobytes())
    p.stdin.close()
    if p.wait():
        raise SystemExit("⛔ ffmpeg lỗi")
    print(f"-> {a.out}  {n} khung = {a.dur:.2f}s, bấm lúc {taps}")


if __name__ == "__main__":
    main()
