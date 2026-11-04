# -*- coding: utf-8 -*-
"""Chuẩn bị 1 lần (cần mạng): tải ranh giới nước (Natural Earth), font, model cắt nền u2net;
sinh sẵn sprite nổ, SFX, nhạc nền dự phòng, icon vật thể dự phòng.

python -I scripts/chuan_bi.py [--khong-u2net] [--lam-lai]
Các bước khác tự gọi hàm bao_dam() nếu thiếu.
"""
import argparse
import math
import os
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import chung as C

NE_URL = "https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/"
TAI = {
    "ne_10m_admin_0_countries.geojson": NE_URL + "ne_10m_admin_0_countries.geojson",
    "ne_50m_admin_1_states_provinces.geojson": NE_URL + "ne_50m_admin_1_states_provinces.geojson",
}
FONT_URL = {
    "PaytoneOne-Regular.ttf": "https://raw.githubusercontent.com/google/fonts/main/ofl/paytoneone/PaytoneOne-Regular.ttf",
    "LilitaOne-Regular.ttf": "https://raw.githubusercontent.com/google/fonts/main/ofl/lilitaone/LilitaOne-Regular.ttf",
    "Caveat.ttf": "https://raw.githubusercontent.com/google/fonts/main/ofl/caveat/Caveat%5Bwght%5D.ttf",
    "CaveatBrush-Regular.ttf": "https://raw.githubusercontent.com/google/fonts/main/ofl/caveatbrush/CaveatBrush-Regular.ttf",
}
U2NET_URL = "https://github.com/danielgatis/rembg/releases/download/v0.0.0/u2net.onnx"
FONT_MINH_TAM = os.path.join(os.path.dirname(C.SKILL), "minh-tam-edit", "assets", "fonts")


def duong_dan_du_lieu():
    return {
        "nuoc": os.path.join(C.CACHE, "du_lieu", "ne_10m_admin_0_countries.geojson"),
        "bang": os.path.join(C.CACHE, "du_lieu", "ne_50m_admin_1_states_provinces.geojson"),
        "u2net": os.path.join(C.CACHE, "models", "u2net.onnx"),
        "font_sub": os.path.join(C.FONTS, "PaytoneOne-Regular.ttf"),
        "font_tay": os.path.join(C.FONTS, "Caveat.ttf"),
        "font_co": os.path.join(C.FONTS, "CaveatBrush-Regular.ttf"),
        "font_dam": os.path.join(C.FONTS, "Montserrat-Black.ttf"),
        "no": os.path.join(C.CACHE, "sprite", "no"),
        "sfx": os.path.join(C.CACHE, "sfx"),
        "nhac": os.path.join(C.CACHE, "nhac_drone.wav"),
        "icon": os.path.join(C.CACHE, "thu_vien_mac_dinh"),
    }


# ---------------- tải ----------------
def tai_du_lieu(lam_lai=False):
    d = duong_dan_du_lieu()
    for ten, url in TAI.items():
        p = os.path.join(C.CACHE, "du_lieu", ten)
        if lam_lai and os.path.exists(p):
            os.remove(p)
        if os.path.exists(p):
            print("   đã có " + ten)
            continue
        print("   tải " + ten + " …")
        if not C.tai_file(url, p, timeout=300):
            C.canh_bao("không tải được %s (cần mạng). Nước/bang sẽ không tô được." % ten)
    return d


def tai_font():
    C.mkdir(C.FONTS)
    for ten, url in FONT_URL.items():
        p = os.path.join(C.FONTS, ten)
        if os.path.exists(p):
            continue
        print("   tải font " + ten)
        if not C.tai_file(url, p, timeout=120):
            C.canh_bao("không tải được font " + ten)
    for ten in ("Montserrat-Black.ttf", "Pacifico.ttf", "Montserrat-ExtraBold.ttf"):
        src = os.path.join(FONT_MINH_TAM, ten)
        dst = os.path.join(C.FONTS, ten)
        if os.path.exists(src) and not os.path.exists(dst):
            shutil.copy2(src, dst)


def tai_u2net():
    p = duong_dan_du_lieu()["u2net"]
    if os.path.exists(p):
        print("   đã có u2net.onnx")
        return True
    print("   tải u2net.onnx (~176 MB, 1 lần) …")
    if not C.tai_file(U2NET_URL, p, timeout=900):
        C.canh_bao("không tải được u2net.onnx — ảnh người/vật sẽ không cắt nền được")
        return False
    return True


# ---------------- sprite nổ ----------------
def _nhieu(h, w, o, rng):
    import cv2
    import numpy as np
    out = np.zeros((h, w), np.float32)
    amp, tong = 1.0, 0.0
    for i in range(o):
        n = 4 * (2 ** i)
        base = rng.random((n, n)).astype(np.float32)
        out += amp * cv2.resize(base, (w, h), interpolation=cv2.INTER_CUBIC)
        tong += amp
        amp *= 0.55
    return out / tong


def sinh_sprite_no(thu_muc, so_khung=36, kich=384):
    import cv2
    import numpy as np
    if os.path.exists(os.path.join(thu_muc, "%02d.png" % (so_khung - 1))):
        return
    C.mkdir(thu_muc)
    rng = np.random.default_rng(7)
    yy, xx = np.mgrid[0:kich, 0:kich].astype(np.float32)
    cx = cy = kich / 2
    n1, n2, n3 = (_nhieu(kich, kich, 4, rng) for _ in range(3))
    for i in range(so_khung):
        p = i / (so_khung - 1)
        r = 0.48 * kich * (1 - (1 - p) ** 2.4)
        # lửa nổ: nhanh rồi tan; khói: lên trên, mờ dần
        lua = max(0.0, 1 - max(0.0, p - 0.35) / 0.5)
        khoi = max(0.0, min(1.0, (p - 0.15) / 0.5)) * (1 - p) ** 0.8
        nn = n1 * (1 - p) + n2 * p
        d = np.sqrt((xx - cx) ** 2 + (yy - cy - r * 0.15 * p) ** 2)
        fall = np.clip(1 - d / max(r, 1), 0, 1)
        f = fall ** 0.8 * (0.35 + 1.25 * nn)
        f = np.clip(f, 0, 1)
        img = np.zeros((kich, kich, 4), np.float32)
        # lõi trắng-vàng, giữa cam, ngoài đỏ sẫm
        v = f
        rr = np.clip(v * 2.2, 0, 1)
        gg = np.clip((v - 0.25) * 1.9, 0, 1)
        bb = np.clip((v - 0.7) * 2.5, 0, 1)
        a_lua = np.clip(v * 1.6, 0, 1) * lua
        # khói
        dk = np.sqrt((xx - cx) ** 2 + (yy - cy + r * 0.35 * p) ** 2)
        fk = np.clip(1 - dk / max(r * 1.15, 1), 0, 1) ** 0.7 * (0.3 + 1.2 * n3)
        a_khoi = np.clip(fk, 0, 1) * khoi * 0.85
        xam = 0.28 + 0.25 * n3
        # trộn: lửa trên khói
        a = a_lua + a_khoi * (1 - a_lua)
        col = np.stack([rr, gg, bb], -1) * a_lua[..., None] + \
            np.stack([xam, xam, xam], -1) * (a_khoi * (1 - a_lua))[..., None]
        col = np.where(a[..., None] > 1e-4, col / np.maximum(a[..., None], 1e-4), 0)
        img[..., :3] = np.clip(col, 0, 1)
        img[..., 3] = np.clip(a, 0, 1)
        out = (img * 255).astype(np.uint8)
        out = cv2.cvtColor(out, cv2.COLOR_RGBA2BGRA)
        cv2.imwrite(os.path.join(thu_muc, "%02d.png" % i), out)
    print("   đã sinh %d khung sprite nổ" % so_khung)


# ---------------- SFX & nhạc dự phòng ----------------
def _ghi_wav(path, x, sr=44100):
    import numpy as np
    import wave
    x = np.clip(x, -1, 1)
    if x.ndim == 1:
        x = np.stack([x, x], -1)
    C.mkdir(os.path.dirname(path))
    with wave.open(path, "wb") as f:
        f.setnchannels(2)
        f.setsampwidth(2)
        f.setframerate(sr)
        f.writeframes((x * 32767).astype("<i2").tobytes())


def _lowpass(x, cutoff, sr=44100):
    """Lọc thấp 1 cực (cutoff có thể là mảng theo thời gian)."""
    import numpy as np
    y = np.zeros_like(x)
    if np.isscalar(cutoff):
        a = math.exp(-2 * math.pi * cutoff / sr)
        prev = 0.0
        for i in range(len(x)):
            prev = (1 - a) * x[i] + a * prev
            y[i] = prev
    else:
        a = np.exp(-2 * np.pi * cutoff / sr)
        prev = 0.0
        for i in range(len(x)):
            prev = (1 - a[i]) * x[i] + a[i] * prev
            y[i] = prev
    return y


def _env(n, attack, decay, sr=44100, cong=1.5):
    import numpy as np
    t = np.arange(n) / sr
    e = np.minimum(t / max(attack, 1e-4), 1.0)
    e = e * np.exp(-np.maximum(t - attack, 0) / max(decay, 1e-4) * cong)
    return e.astype(np.float32)


def sinh_sfx(thu_muc):
    import numpy as np
    sr = 44100
    C.mkdir(thu_muc)
    rng = np.random.default_rng(3)

    def ton(ten, x, gain=0.8):
        p = os.path.join(thu_muc, ten + ".wav")
        if os.path.exists(p):
            return
        x = x / (np.max(np.abs(x)) + 1e-6) * gain
        _ghi_wav(p, x.astype(np.float32), sr)

    n = int(1.8 * sr)
    noise = rng.standard_normal(n).astype(np.float32)
    boom = _lowpass(noise, 180) * _env(n, 0.01, 0.55, sr) * 6
    t = np.arange(n) / sr
    boom += 0.9 * np.sin(2 * np.pi * (48 + 20 * np.exp(-t * 6)) * t) * _env(n, 0.005, 0.5, sr)
    crack = _lowpass(noise, 3500) * _env(n, 0.002, 0.12, sr) * 1.2
    ton("no", boom + crack)

    n = int(1.3 * sr)
    noise = rng.standard_normal(n).astype(np.float32)
    cut = 300 + 5000 * (np.arange(n) / n) ** 1.6
    ton("phong", _lowpass(noise, cut) * _env(n, 0.25, 0.6, sr, 1.1) * 3)

    n = int(0.7 * sr)
    t = np.arange(n) / sr
    ping = (np.sin(2 * np.pi * 1320 * t) + 0.4 * np.sin(2 * np.pi * 2640 * t)) * np.exp(-t * 7)
    ton("ping", ping, 0.5)

    n = int(1.4 * sr)
    noise = rng.standard_normal(n).astype(np.float32)
    imp = np.zeros(n, np.float32)
    for k in rng.integers(0, int(0.5 * sr), 60):
        imp[k:k + 40] += rng.standard_normal(40) * (1 - k / (0.5 * sr))
    vo = _lowpass(imp, 5000) * 2 + _lowpass(noise, 140) * _env(n, 0.01, 0.5, sr) * 4
    ton("vo", vo)

    n = int(0.45 * sr)
    noise = rng.standard_normal(n).astype(np.float32)
    ton("hien", _lowpass(noise, 2500) * _env(n, 0.08, 0.15, sr) * 2.5, 0.45)

    n = int(1.2 * sr)
    noise = rng.standard_normal(n).astype(np.float32)
    x = np.zeros(n, np.float32)
    for k in range(3):
        s = int(k * 0.22 * sr)
        seg = _lowpass(noise[s:s + int(0.5 * sr)], 2000 + 3000 * k) * _env(int(0.5 * sr), 0.05, 0.18, sr)
        x[s:s + len(seg)] += seg
    ton("tach", x * 2, 0.6)

    n = int(1.1 * sr)
    noise = rng.standard_normal(n).astype(np.float32)
    ton("luot", _lowpass(noise, 1200) * _env(n, 0.4, 0.5, sr, 1.0) * 3, 0.45)

    n = int(1.6 * sr)
    noise = rng.standard_normal(n).astype(np.float32)
    cut = 200 + 2500 * (np.arange(n) / n) ** 2
    ton("lan", _lowpass(noise, cut) * _env(n, 1.2, 0.35, sr, 1.0) * 3, 0.5)

    n = int(0.9 * sr)
    x = np.zeros(n, np.float32)
    for k in range(8):
        s = int(k * 0.1 * sr)
        x[s:s + 300] += rng.standard_normal(300) * np.exp(-np.arange(300) / 60)
    ton("dem", _lowpass(x, 4000), 0.4)
    print("   SFX dự phòng sẵn sàng")


def sinh_nhac_drone(path, giay=150):
    import numpy as np
    if os.path.exists(path):
        return
    sr = 44100
    n = giay * sr
    t = np.arange(n) / sr
    rng = np.random.default_rng(11)
    x = np.zeros(n, np.float32)
    for f, g in ((55.0, 0.5), (55.3, 0.3), (82.4, 0.25), (110.0, 0.18), (164.8, 0.08)):
        lfo = 0.75 + 0.25 * np.sin(2 * np.pi * (0.05 + f / 2000) * t + rng.random() * 6)
        x += g * np.sin(2 * np.pi * f * t + rng.random() * 6) * lfo
    pad = _lowpass(rng.standard_normal(n).astype(np.float32), 420) * 0.9
    pad *= 0.6 + 0.4 * np.sin(2 * np.pi * 0.07 * t)
    x += pad
    # nhịp trống trầm mỗi 2 s
    nhip = np.zeros(n, np.float32)
    k = int(sr * 2.0)
    for s in range(0, n - sr, k):
        tt = np.arange(int(0.6 * sr)) / sr
        nhip[s:s + len(tt)] += np.sin(2 * np.pi * (60 + 30 * np.exp(-tt * 10)) * tt) * np.exp(-tt * 5) * 0.8
    x += nhip
    x = x / (np.max(np.abs(x)) + 1e-6)
    rms = float(np.sqrt(np.mean(x ** 2)))
    x = x * (10 ** (-20 / 20) / max(rms, 1e-6))
    _ghi_wav(path, x, sr)
    print("   nhạc nền dự phòng (drone) sẵn sàng")


# ---------------- icon vật thể dự phòng ----------------
def _grad_rect(draw, box, c1, c2, ngang=True):
    x0, y0, x1, y1 = box
    n = (x1 - x0) if ngang else (y1 - y0)
    for i in range(int(n)):
        f = i / max(n - 1, 1)
        c = tuple(int(c1[k] + (c2[k] - c1[k]) * f) for k in range(3)) + (255,)
        if ngang:
            draw.line([(x0 + i, y0), (x0 + i, y1)], fill=c)
        else:
            draw.line([(x0, y0 + i), (x1, y0 + i)], fill=c)


def sinh_icon_mac_dinh(thu_muc):
    from PIL import Image, ImageDraw, ImageFilter
    C.mkdir(thu_muc)
    S = 512

    def luu(ten, img):
        p = os.path.join(thu_muc, ten + ".png")
        if not os.path.exists(p):
            # bóng mềm
            sh = Image.new("RGBA", img.size, (0, 0, 0, 0))
            a = img.split()[3].filter(ImageFilter.GaussianBlur(6))
            sh.putalpha(a.point(lambda v: int(v * 0.45)))
            out = Image.new("RGBA", img.size, (0, 0, 0, 0))
            out.alpha_composite(sh, (6, 8))
            out.alpha_composite(img)
            out.save(p)

    # tên lửa
    im = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    bx = (216, 150, 296, 470)
    _grad_rect(d, bx, (70, 70, 74), (215, 215, 220))
    _grad_rect(d, (296, 150, 330, 470), (215, 215, 220), (90, 90, 95))
    d.polygon([(216, 150), (330, 150), (273, 40)], fill=(240, 240, 240, 255))
    # mũi kẻ ô
    for r in range(6):
        for c in range(4):
            if (r + c) % 2 == 0:
                y0 = 40 + r * 18
                w = (y0 - 40) / 110 * 57
                x0 = 273 - w + c * (2 * w / 4)
                d.rectangle([x0, y0, x0 + 2 * w / 4, y0 + 18], fill=(20, 20, 20, 255))
    d.polygon([(216, 470), (330, 470), (273, 40)], outline=None)
    d.polygon([(216, 420), (170, 490), (216, 470)], fill=(60, 60, 64, 255))
    d.polygon([(330, 420), (376, 490), (330, 470)], fill=(60, 60, 64, 255))
    d.rectangle([216, 470, 330, 486], fill=(40, 40, 44, 255))
    luu("ten_lua", im)

    # vệ tinh
    im = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    for x0 in (30, 330):
        d.rectangle([x0, 200, x0 + 150, 310], fill=(25, 50, 120, 255), outline=(200, 210, 230, 255), width=3)
        for i in range(1, 5):
            d.line([(x0 + i * 30, 200), (x0 + i * 30, 310)], fill=(140, 170, 230, 255), width=2)
        d.line([(x0, 255), (x0 + 150, 255)], fill=(140, 170, 230, 255), width=2)
    d.rectangle([180, 240, 330, 270], fill=(170, 170, 175, 255))
    _grad_rect(d, (205, 180, 305, 330), (120, 110, 90), (230, 220, 190))
    d.ellipse([200, 90, 310, 170], fill=(225, 225, 230, 255), outline=(120, 120, 125, 255), width=3)
    d.line([(255, 170), (255, 185)], fill=(90, 90, 90, 255), width=6)
    luu("ve_tinh", im)

    # tàu chiến (nhìn từ trên)
    im = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.polygon([(256, 30), (300, 120), (300, 470), (256, 500), (212, 470), (212, 120)], fill=(120, 125, 130, 255),
              outline=(60, 62, 66, 255), width=3)
    d.rectangle([232, 190, 280, 330], fill=(150, 155, 160, 255), outline=(70, 70, 75, 255), width=2)
    d.rectangle([244, 200, 268, 250], fill=(95, 100, 105, 255))
    d.ellipse([246, 130, 266, 150], fill=(80, 84, 90, 255))
    d.ellipse([246, 380, 266, 400], fill=(80, 84, 90, 255))
    d.rectangle([240, 420, 272, 460], fill=(100, 104, 110, 255))
    luu("tau_chien", im)

    # tàu sân bay (nhìn từ trên: boong phẳng, đường băng chéo)
    im = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.polygon([(256, 20), (330, 90), (335, 470), (300, 500), (212, 500), (177, 470), (182, 90)],
              fill=(105, 110, 118, 255), outline=(50, 52, 58, 255), width=3)
    d.polygon([(200, 120), (240, 120), (300, 470), (260, 470)], fill=(80, 84, 92, 255))
    for y0 in range(140, 460, 40):
        d.line([(214 + (y0 - 140) * 0.17, y0), (226 + (y0 - 140) * 0.17, y0 + 18)], fill=(230, 230, 230, 255), width=3)
    d.rectangle([300, 200, 334, 290], fill=(150, 155, 165, 255), outline=(60, 62, 68, 255), width=2)
    d.rectangle([308, 212, 326, 230], fill=(90, 95, 105, 255))
    luu("tau_san_bay", im)

    # tàu chở dầu (nhìn từ trên: thân dài, ống dẫn giữa, buồng lái phía đuôi)
    im = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.polygon([(256, 30), (318, 110), (318, 460), (300, 500), (212, 500), (194, 460), (194, 110)],
              fill=(150, 60, 50, 255), outline=(70, 25, 20, 255), width=3)
    d.rectangle([205, 120, 307, 400], fill=(170, 75, 60, 255))
    d.rectangle([250, 125, 262, 395], fill=(230, 220, 200, 255))
    for y0 in range(140, 390, 36):
        d.rectangle([212, y0, 300, y0 + 6], fill=(120, 45, 38, 255))
    d.rectangle([222, 410, 290, 470], fill=(235, 235, 240, 255), outline=(90, 90, 95, 255), width=2)
    d.rectangle([246, 455, 266, 480], fill=(60, 60, 65, 255))
    luu("tau_dau", im)

    # giàn phóng đánh chặn
    im = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rectangle([60, 330, 460, 420], fill=(80, 95, 70, 255), outline=(40, 50, 35, 255), width=3)
    for x0 in (90, 180, 300, 390):
        d.ellipse([x0, 400, x0 + 60, 460], fill=(30, 30, 30, 255), outline=(90, 90, 90, 255), width=4)
    d.rectangle([60, 270, 150, 330], fill=(95, 110, 85, 255), outline=(40, 50, 35, 255), width=3)
    for k in range(4):
        x0 = 190 + k * 48
        d.polygon([(x0, 330), (x0 + 36, 330), (x0 + 36 + 120, 110), (x0 + 120, 110)], fill=(70, 75, 70, 255),
                  outline=(30, 32, 30, 255))
        d.polygon([(x0 + 120, 110), (x0 + 156, 110), (x0 + 150, 96), (x0 + 126, 96)], fill=(200, 200, 200, 255))
    luu("gian_phong", im)

    # máy bay
    im = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.polygon([(256, 30), (280, 120), (290, 300), (275, 460), (256, 480), (237, 460), (222, 300), (232, 120)],
              fill=(120, 130, 140, 255), outline=(50, 55, 60, 255), width=3)
    d.polygon([(232, 180), (40, 330), (40, 350), (232, 300)], fill=(110, 120, 130, 255), outline=(50, 55, 60, 255))
    d.polygon([(280, 180), (472, 330), (472, 350), (280, 300)], fill=(110, 120, 130, 255), outline=(50, 55, 60, 255))
    d.polygon([(237, 400), (150, 470), (150, 482), (237, 450)], fill=(100, 110, 120, 255))
    d.polygon([(275, 400), (362, 470), (362, 482), (275, 450)], fill=(100, 110, 120, 255))
    d.ellipse([244, 60, 268, 130], fill=(40, 60, 90, 255))
    luu("may_bay", im)
    luu("may_bay_nem_bom", im)
    luu("drone", im)

    # xe tăng
    im = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([90, 260, 430, 400], 30, fill=(90, 100, 70, 255), outline=(40, 45, 30, 255), width=4)
    d.rounded_rectangle([60, 330, 460, 420], 40, fill=(50, 52, 48, 255), outline=(25, 25, 25, 255), width=4)
    for x0 in range(80, 440, 48):
        d.ellipse([x0, 350, x0 + 36, 400], fill=(85, 85, 85, 255))
    d.rounded_rectangle([170, 190, 340, 275], 20, fill=(100, 112, 80, 255), outline=(40, 45, 30, 255), width=4)
    d.rectangle([330, 215, 500, 235], fill=(70, 75, 60, 255), outline=(30, 32, 28, 255), width=2)
    luu("xe_tang", im)

    # thùng dầu
    im = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    _grad_rect(d, (150, 100, 362, 440), (40, 40, 44), (120, 120, 126))
    d.ellipse([150, 70, 362, 130], fill=(90, 90, 96, 255), outline=(30, 30, 30, 255), width=3)
    for y0 in (190, 300):
        d.rectangle([150, y0, 362, y0 + 16], fill=(60, 60, 66, 255))
    d.ellipse([150, 410, 362, 470], fill=(60, 60, 66, 255))
    luu("thung_dau", im)

    # đồng tiền / tiền
    im = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    for k in range(5):
        y0 = 360 - k * 38
        d.rounded_rectangle([90, y0, 420, y0 + 60], 10, fill=(60, 140, 80, 255), outline=(20, 70, 35, 255), width=3)
        d.rounded_rectangle([110, y0 + 10, 400, y0 + 50], 8, outline=(170, 220, 180, 255), width=2)
    d.ellipse([215, 160, 295, 240], fill=(210, 240, 215, 255), outline=(20, 70, 35, 255), width=3)
    d.text((238, 172), "$", fill=(20, 70, 35, 255))
    luu("tien", im)

    # toà nhà
    im = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    for x0, h, c in ((70, 300, (90, 100, 120)), (190, 420, (120, 130, 150)), (330, 240, (100, 110, 130))):
        d.rectangle([x0, 500 - h, x0 + 110, 500], fill=c + (255,), outline=(40, 45, 55, 255), width=3)
        for yy in range(500 - h + 20, 490, 30):
            for xx in range(x0 + 14, x0 + 100, 26):
                d.rectangle([xx, yy, xx + 14, yy + 16], fill=(250, 240, 180, 255))
    luu("toa_nha", im)
    luu("nha_may", im)
    luu("can_cu", im)

    # virus
    im = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.ellipse([150, 150, 362, 362], fill=(200, 60, 60, 255), outline=(120, 20, 20, 255), width=4)
    for k in range(14):
        a = k / 14 * 2 * math.pi
        x1, y1 = 256 + 106 * math.cos(a), 256 + 106 * math.sin(a)
        x2, y2 = 256 + 160 * math.cos(a), 256 + 160 * math.sin(a)
        d.line([(x1, y1), (x2, y2)], fill=(160, 40, 40, 255), width=10)
        d.ellipse([x2 - 18, y2 - 18, x2 + 18, y2 + 18], fill=(230, 90, 90, 255))
    luu("virus", im)

    # binh lính (bóng người)
    im = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    for x0 in (120, 256, 392):
        d.ellipse([x0 - 40, 60, x0 + 40, 140], fill=(60, 70, 50, 255))
        d.rounded_rectangle([x0 - 60, 150, x0 + 60, 360], 30, fill=(75, 90, 60, 255))
        d.rectangle([x0 - 50, 360, x0 - 10, 480], fill=(50, 60, 40, 255))
        d.rectangle([x0 + 10, 360, x0 + 50, 480], fill=(50, 60, 40, 255))
    luu("binh_linh", im)
    luu("nguoi_ti_nan", im)
    luu("bieu_tinh", im)

    # bom hạt nhân
    im = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.ellipse([150, 60, 362, 272], fill=(70, 70, 60, 255), outline=(30, 30, 25, 255), width=4)
    d.rectangle([180, 240, 332, 400], fill=(80, 80, 70, 255), outline=(30, 30, 25, 255), width=4)
    d.polygon([(180, 400), (332, 400), (360, 470), (152, 470)], fill=(60, 60, 55, 255))
    d.ellipse([216, 126, 296, 206], fill=(250, 210, 40, 255))
    for k in range(3):
        a = k * 2 * math.pi / 3 - math.pi / 2
        d.pieslice([226, 136, 286, 196], math.degrees(a) - 30, math.degrees(a) + 30, fill=(20, 20, 20, 255))
    luu("bom_hat_nhan", im)
    print("   icon dự phòng sẵn sàng")


# ---------------- gom ----------------
def bao_dam(can_mang=True, u2net=True, im=True):
    """Đảm bảo mọi thứ cần cho render có sẵn. Trả dict đường dẫn."""
    d = duong_dan_du_lieu()
    thieu = [k for k in ("nuoc", "bang") if not os.path.exists(d[k])]
    thieu_font = [k for k in ("font_sub", "font_tay") if not os.path.exists(d[k])]
    if (thieu or thieu_font) and can_mang:
        tai_du_lieu()
        tai_font()
    if u2net and can_mang and not os.path.exists(d["u2net"]):
        tai_u2net()
    sinh_sprite_no(d["no"])
    sinh_sfx(d["sfx"])
    sinh_nhac_drone(d["nhac"])
    sinh_icon_mac_dinh(d["icon"])
    return d


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--khong-u2net", action="store_true")
    ap.add_argument("--lam-lai", action="store_true", help="tải lại dữ liệu, sinh lại sprite/SFX")
    a = ap.parse_args()
    C.buoc("Chuẩn bị dữ liệu skill skill-bando-tintuc-chinhtri")
    if a.lam_lai:
        for p in (duong_dan_du_lieu()["no"], duong_dan_du_lieu()["sfx"], duong_dan_du_lieu()["icon"]):
            shutil.rmtree(p, ignore_errors=True)
        try:
            os.remove(duong_dan_du_lieu()["nhac"])
        except Exception:
            pass
    tai_du_lieu(a.lam_lai)
    tai_font()
    if not a.khong_u2net:
        tai_u2net()
    d = duong_dan_du_lieu()
    sinh_sprite_no(d["no"])
    sinh_sfx(d["sfx"])
    sinh_nhac_drone(d["nhac"])
    sinh_icon_mac_dinh(d["icon"])
    C.ok("xong. Dữ liệu ở " + C.CACHE)


if __name__ == "__main__":
    main()
