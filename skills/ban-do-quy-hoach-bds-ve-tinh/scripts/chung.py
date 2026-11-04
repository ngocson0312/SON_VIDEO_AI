# -*- coding: utf-8 -*-
"""Phần dùng chung của ban-do-quy-hoach-bds-ve-tinh: đường dẫn, ffmpeg, font, vẽ chữ, dán lớp, toán Mercator, cache."""
import io
import json
import math
import os
import re
import shutil
import subprocess
import sys
import unicodedata

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H, FPS = 1080, 1920, 30
DUOI_SAU_TIENG_CUOI = 0.9          # video kéo thêm 0,9 s sau tiếng cuối

SCRIPTS = os.path.dirname(os.path.abspath(__file__))
SKILL = os.path.dirname(SCRIPTS)
ASSETS = os.path.join(SKILL, "assets")
FONT_DIR = os.path.join(ASSETS, "fonts")
SFX_DIR = os.path.join(ASSETS, "sfx")
SUB_SCRIPTS = os.path.join(SKILL, "sub", "scripts")
SUB_FONT_DIR = os.path.join(SKILL, "sub", "assets", "fonts")
CACHE = os.path.join(os.path.expanduser("~"), ".cache", "ban-do-quy-hoach-bds-ve-tinh")
UA = {"User-Agent": "ban-do-quy-hoach-bds-ve-tinh/1.0 (personal video tool)"}

FONTS = {
    "black": "Montserrat-Black.ttf",
    "xbold": "Montserrat-ExtraBold.ttf",
    "bold": "Montserrat-Bold.ttf",
    "semi": "Montserrat-SemiBold.ttf",
    "sub": "Montserrat-ExtraBold.ttf",
    "sub_bvp": "BeVietnamPro-ExtraBold.ttf",
}

# bảng màu đo từ video mẫu ho_dan.mp4 (references/phan-tich-mau-ho-dan.md mục 8)
NAVY = (15, 44, 82)            # #0F2C52 hộp thẻ
NAVY_VIEN = (62, 98, 150)
NAVY_TOI = (8, 22, 44)
VANG = (255, 210, 77)          # #FFD24D
TRANG = (255, 255, 255)
XAM = (190, 200, 215)
XANH_LO = (79, 195, 247)       # #4FC3F7 tim sông
XANH_LA = (120, 230, 120)
DO_CAM = (255, 120, 50)
DEN = (0, 0, 0)


def utf8():
    for s in (sys.stdout, sys.stderr):
        try:
            s.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass


utf8()


def die(msg, code=1):
    print("⛔ " + msg)
    sys.exit(code)


def canh_bao(msg):
    print("⚠ " + msg)


def ok(msg):
    print("✅ " + msg)


def ffbin(name):
    p = shutil.which(name) or shutil.which(name + ".exe")
    if not p:
        die("không thấy %s trong PATH — cài ffmpeg bản full (https://www.gyan.dev/ffmpeg/builds/)" % name)
    return p


def run(cmd, check=True):
    r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if check and r.returncode != 0:
        print(r.stderr[-3000:])
        die("lệnh lỗi: " + " ".join(str(c) for c in cmd[:6]) + " …")
    return r


def probe(path):
    r = run([ffbin("ffprobe"), "-v", "error", "-show_entries",
             "format=duration:stream=codec_type,width,height,avg_frame_rate", "-of", "json", path])
    d = json.loads(r.stdout)
    info = {"duration": float(d["format"].get("duration", 0) or 0), "w": 0, "h": 0, "fps": 0.0, "audio": False,
            "video": False}
    for s in d.get("streams", []):
        if s.get("codec_type") == "video" and not info["video"]:
            info["video"] = True
            info["w"], info["h"] = int(s.get("width", 0)), int(s.get("height", 0))
            a, b = (s.get("avg_frame_rate") or "0/1").split("/")
            info["fps"] = float(a) / float(b) if float(b) else 0.0
        elif s.get("codec_type") == "audio":
            info["audio"] = True
    return info


def jload(path):
    with io.open(path, encoding="utf-8") as f:
        return json.load(f)


def jsave(path, obj):
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with io.open(path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)


def ghi_text(path, text):
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with io.open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)


def ten_khong_trung(path):
    """file đã có ⇒ _ban2, _ban3… (không bao giờ ghi đè bản dựng cũ)"""
    if not os.path.exists(path):
        return path
    goc, duoi = os.path.splitext(path)
    k = 2
    while os.path.exists("%s_ban%d%s" % (goc, k, duoi)):
        k += 1
    return "%s_ban%d%s" % (goc, k, duoi)


def ten_khong_dau(s):
    s = unicodedata.normalize("NFD", str(s))
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    s = s.replace("đ", "d").replace("Đ", "D")
    s = re.sub(r"[^A-Za-z0-9 ]+", " ", s)
    return re.sub(r"\s+", " ", s).strip().lower()


def slug(s):
    return ten_khong_dau(s).replace(" ", "_")[:48] or "x"


def nfc(s):
    return unicodedata.normalize("NFC", s)


def doc_ke_hoach(work):
    work = os.path.abspath(work)
    plan = jload(os.path.join(work, "ke_hoach.json"))
    for k in ("audio", "res"):
        v = plan.get(k)
        if v and not os.path.isabs(v):
            plan[k] = os.path.normpath(os.path.join(work, v))
    if not plan.get("audio") or not os.path.isfile(plan["audio"]):
        die("ke_hoach.json trỏ tới audio không có: %s" % plan.get("audio"))
    plan["work"] = work
    return plan


def cache_dir(*p):
    d = os.path.join(CACHE, *p)
    os.makedirs(d, exist_ok=True)
    return d


# ---------------------------------------------------------------- nhịp

def clamp(x, a=0.0, b=1.0):
    return a if x < a else b if x > b else x


def ease_out(x):
    x = clamp(x)
    return 1 - (1 - x) ** 3


def ease_in_out(x):
    x = clamp(x)
    return 4 * x ** 3 if x < 0.5 else 1 - (-2 * x + 2) ** 3 / 2


def smooth(x):
    x = clamp(x)
    return x * x * (3 - 2 * x)


def ramp(t, t0, dur):
    if dur <= 0:
        return 1.0 if t >= t0 else 0.0
    return clamp((t - t0) / dur)


def vao_ra(t, dur, fin=0.2, fout=0.2):
    if t < 0 or t > dur:
        return 0.0
    a = 1.0
    if fin > 0:
        a = min(a, clamp(t / fin))
    if fout > 0:
        a = min(a, clamp((dur - t) / fout))
    return a


# ---------------------------------------------------------------- Mercator (ô 256 px)

TS = 256


def ll2px(lat, lon, z):
    """kinh vĩ → điểm ảnh thế giới ở zoom z (có thể z lẻ)"""
    n = TS * (2.0 ** z)
    x = (lon + 180.0) / 360.0 * n
    lat = max(-85.05, min(85.05, lat))
    s = math.sin(math.radians(lat))
    y = (0.5 - math.log((1 + s) / (1 - s)) / (4 * math.pi)) * n
    return x, y


def px2ll(x, y, z):
    n = TS * (2.0 ** z)
    lon = x / n * 360.0 - 180.0
    lat = math.degrees(2 * math.atan(math.exp((0.5 - y / n) * 2 * math.pi)) - math.pi / 2)
    return lat, lon


def m_per_px(lat, z):
    return 156543.03392 * math.cos(math.radians(lat)) / (2.0 ** z)


def khoang_cach_m(a, b):
    R = 6371000.0
    p1, p2 = math.radians(a[0]), math.radians(b[0])
    dp, dl = p2 - p1, math.radians(b[1] - a[1])
    h = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * R * math.asin(math.sqrt(h))


def dai_tuyen_m(pts):
    return sum(khoang_cach_m(pts[i], pts[i + 1]) for i in range(len(pts) - 1))


# ---------------------------------------------------------------- font + chữ

_font_cache = {}


def font(key, size):
    k = (key, int(size))
    if k not in _font_cache:
        path = key if os.path.isfile(key) else os.path.join(FONT_DIR, FONTS[key])
        _font_cache[k] = ImageFont.truetype(path, int(size))
    return _font_cache[k]


def thieu_glyph(key, text):
    f = font(key, 60)
    bad = []
    for ch in set(text):
        if ch.isspace():
            continue
        m = f.getmask(ch)
        if m.size[0] == 0 or m.size[1] == 0:
            bad.append(ch)
    return bad


def chu(text, key, size, fill=TRANG, stroke=0, stroke_fill=(0, 0, 0), shadow=None, track=0):
    """1 dòng chữ → ảnh RGBA cắt sát. shadow = (dx, dy, blur, alpha)"""
    f = font(key, size)
    pad = int(size * 0.5) + stroke * 2 + 30
    if track:
        widths = [f.getlength(ch) for ch in text]
        tw = int(sum(widths) + track * max(0, len(text) - 1))
    else:
        tw = int(f.getlength(text))
    asc, desc = f.getmetrics()
    th = asc + desc
    Wc, Hc = tw + 2 * pad, th + 2 * pad
    mask = Image.new("L", (Wc, Hc), 0)
    smask = Image.new("L", (Wc, Hc), 0)
    d, ds = ImageDraw.Draw(mask), ImageDraw.Draw(smask)

    def draw_text(dr, x, y, sw):
        if track:
            cx = x
            for ch_, wch in zip(text, widths):
                dr.text((cx, y), ch_, font=f, fill=255, stroke_width=sw, stroke_fill=255)
                cx += wch + track
        else:
            dr.text((x, y), text, font=f, fill=255, stroke_width=sw, stroke_fill=255)

    draw_text(d, pad, pad, 0)
    if stroke:
        draw_text(ds, pad, pad, stroke)
    out = Image.new("RGBA", (Wc, Hc), (0, 0, 0, 0))
    if shadow:
        dx, dy, blur, al = shadow
        base = smask if stroke else mask
        sh = Image.new("RGBA", (Wc, Hc), (0, 0, 0, 0))
        sh.putalpha(base.point(lambda v: int(v * al)))
        if blur > 0:
            sh = sh.filter(ImageFilter.GaussianBlur(blur))
        out.alpha_composite(sh, (int(dx), int(dy)))
    if stroke:
        sl = Image.new("RGBA", (Wc, Hc), tuple(stroke_fill) + (0,))
        sl.putalpha(smask)
        out.alpha_composite(sl)
    fl = Image.new("RGBA", (Wc, Hc), tuple(fill) + (0,))
    fl.putalpha(mask)
    out.alpha_composite(fl)
    bb = out.getbbox()
    if bb:
        out = out.crop((max(0, bb[0] - 2), max(0, bb[1] - 2), min(out.width, bb[2] + 2), min(out.height, bb[3] + 2)))
    return out


def bo_dong(text, key, size, max_w):
    f = font(key, size)
    words = text.split()
    lines, cur = [], ""
    for w_ in words:
        t = (cur + " " + w_).strip()
        if f.getlength(t) <= max_w or not cur:
            cur = t
        else:
            lines.append(cur)
            cur = w_
    if cur:
        lines.append(cur)
    return lines


def xep_doc(imgs, gap=0, align="center"):
    wmax = max(i.width for i in imgs)
    htot = sum(i.height for i in imgs) + gap * (len(imgs) - 1)
    out = Image.new("RGBA", (wmax, htot), (0, 0, 0, 0))
    y = 0
    for i in imgs:
        x = (wmax - i.width) // 2 if align == "center" else 0 if align == "left" else wmax - i.width
        out.alpha_composite(i, (x, y))
        y += i.height + gap
    return out


def hop_bo(size, r, fill, vien=None, vien_w=0):
    w, h = size
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    ImageDraw.Draw(im).rounded_rectangle((0, 0, w - 1, h - 1), radius=r, fill=fill, outline=vien,
                                         width=vien_w if vien else 0)
    return im


def bong_do(im, blur=24, alpha=0.55, grow=0):
    pad = blur * 2 + grow
    a = im.getchannel("A")
    base = Image.new("L", (im.width + 2 * pad, im.height + 2 * pad), 0)
    base.paste(a, (pad, pad))
    base = base.filter(ImageFilter.GaussianBlur(blur)).point(lambda v: int(v * alpha))
    sh = Image.new("RGBA", base.size, (0, 0, 0, 0))
    sh.putalpha(base)
    return sh, pad


def mat_na_bo(w, h, r):
    m = Image.new("L", (w, h), 0)
    ImageDraw.Draw(m).rounded_rectangle((0, 0, w - 1, h - 1), radius=r, fill=255)
    return m


# ---------------------------------------------------------------- dán lớp lên khung numpy RGB

def dan(frame, rgba, x, y, alpha=1.0):
    if alpha <= 0.002:
        return
    a = rgba if isinstance(rgba, np.ndarray) else np.asarray(rgba)
    h, w = a.shape[:2]
    x, y = int(round(x)), int(round(y))
    x0, y0 = max(0, x), max(0, y)
    x1, y1 = min(frame.shape[1], x + w), min(frame.shape[0], y + h)
    if x1 <= x0 or y1 <= y0:
        return
    src = a[y0 - y:y1 - y, x0 - x:x1 - x]
    al = src[:, :, 3:4].astype(np.float32) * (alpha / 255.0)
    dst = frame[y0:y1, x0:x1].astype(np.float32)
    frame[y0:y1, x0:x1] = (dst * (1 - al) + src[:, :, :3].astype(np.float32) * al).astype(np.uint8)


def dan_giua(frame, rgba, cx, cy, alpha=1.0, scale=1.0):
    im = rgba
    if scale != 1.0:
        if isinstance(im, np.ndarray):
            im = Image.fromarray(im)
        nw, nh = max(1, int(im.width * scale)), max(1, int(im.height * scale))
        im = im.resize((nw, nh), Image.BICUBIC)
    a = im if isinstance(im, np.ndarray) else np.asarray(im)
    dan(frame, a, cx - a.shape[1] / 2, cy - a.shape[0] / 2, alpha)


def tron(frame, other, alpha):
    if alpha <= 0.002:
        return frame
    if alpha >= 0.998:
        frame[:] = other
        return frame
    import cv2
    cv2.addWeighted(frame, 1 - alpha, other, alpha, 0, dst=frame)
    return frame


def cover(img, w, h):
    s = max(w / img.width, h / img.height)
    nw, nh = int(math.ceil(img.width * s)), int(math.ceil(img.height * s))
    im = img.resize((nw, nh), Image.LANCZOS)
    x, y = (nw - w) // 2, (nh - h) // 2
    return im.crop((x, y, x + w, y + h))


def fit_in(img, w, h):
    s = min(w / img.width, h / img.height)
    return img.resize((max(1, int(img.width * s)), max(1, int(img.height * s))), Image.LANCZOS)


# ---------------------------------------------------------------- số liệu trong lời

DON_VI = r"(km2|km²|m2|m²|ha|km|m|hộ|người|tỷ|tỉ|triệu|nghìn|%|xã|phường|huyện|tầng|phòng|lô|căn)"
_SO = re.compile(r"(\d{1,3}(?:[.,]\d{3})+|\d+(?:[.,]\d+)?)\s*(" + DON_VI[1:-1] + r")?", re.I)


def chuan_hoa_so(s):
    """'6.068' / '6,068' / '6068' → '6068'; '3,5' / '3.5' → '3.5' (dấu thập phân khi phần sau < 3 chữ số)"""
    s = s.strip()
    if re.fullmatch(r"\d{1,3}(?:[.,]\d{3})+", s):
        return re.sub(r"[.,]", "", s)
    m = re.fullmatch(r"(\d+)[.,](\d{1,2})", s)
    if m:
        return m.group(1) + "." + m.group(2)
    return s


def tim_so_lieu(text):
    """mọi (số chuẩn hoá, đơn vị, chuỗi gốc) trong 1 đoạn chữ"""
    out = []
    for m in _SO.finditer(text):
        so = chuan_hoa_so(m.group(1))
        dv = (m.group(2) or "").lower()
        if not dv and len(so) < 3:
            continue
        out.append((so, dv, m.group(0).strip()))
    return out
