# -*- coding: utf-8 -*-
"""Sub karaoke kiểu video mẫu: cụm 2–3 từ IN HOA, cả cụm trắng viền đen, chữ đang đọc sáng vàng, y ≈ 75 % khung."""
import re


def _mau_ass(rgb):
    return "&H00%02X%02X%02X" % (rgb[2], rgb[1], rgb[0])


def gom_cum(tu, toi_da=3):
    """tu: list {w,s,e}. Cắt cụm 3 từ, ngắt ở dấu câu; cụm lẻ 1 từ gộp vào cụm trước (≤4)."""
    cum, hien = [], []
    for w in tu:
        hien.append(w)
        ket = bool(re.search(r"[.!?…:;]$", w["w"])) or (len(hien) >= toi_da and re.search(r"[,]$", w["w"]))
        if len(hien) >= toi_da or ket:
            cum.append(hien)
            hien = []
    if hien:
        cum.append(hien)
    # gộp cụm 1 từ vào cụm trước nếu cụm trước ngắn
    out = []
    for c in cum:
        if len(c) == 1 and out and len(out[-1]) <= toi_da:
            out[-1] = out[-1] + c
        else:
            out.append(c)
    return out


def _sach(w):
    return re.sub(r"[\"“”‘’()\[\]]", "", w).upper()


def _t(s):
    s = max(0.0, s)
    h = int(s // 3600)
    m = int((s % 3600) // 60)
    return "%d:%02d:%05.2f" % (h, m, s % 60)


def _do_font(font_file):
    """Tỉ lệ chữ hoa / Fontsize của libass và hệ số đổi Fontsize → cỡ PIL (để đo bề ngang).
    libass đặt Fontsize = ascender − descender của font, nên font có khoảng trống dấu lớn (Paytone One)
    ra chữ hoa chỉ ≈ 0,45 × Fontsize — phải tính ngược từ chiều cao chữ hoa mong muốn."""
    try:
        from PIL import ImageFont
        S = 200
        f = ImageFont.truetype(font_file, S)
        a, d = f.getmetrics()
        b = f.getbbox("H")
        return (b[3] - b[1]) / float(a + d), S / float(a + d)
    except Exception:
        return 0.455, None


def tao_ass(tu, W, H, font_ten="Paytone One", co=None, y_ti_le=0.75, vang=(255, 255, 0), toi_da=3,
            keo_them=0.12, font_file=None, cao_hoa=0.027, rong_toi_da=0.9):
    """cao_hoa: chiều cao chữ HOA / chiều cao khung (mẫu beo.mp4 ≈ 2,7 % ≈ 52 px ở 1920)."""
    ti_le, doi_pil = _do_font(font_file) if font_file else (0.455, None)
    cap = H * cao_hoa
    co = co or int(round(cap / ti_le))
    vien = max(2, int(round(cap * 0.15)))
    bong = max(1, int(round(cap * 0.08)))
    marginv = int(H * (1 - y_ti_le) - co * 0.5)
    do_rong = None
    if font_file and doi_pil:
        try:
            from PIL import ImageFont
            _f = ImageFont.truetype(font_file, max(8, int(co * doi_pil)))
            do_rong = lambda txt: _f.getlength(txt) + 2 * vien
        except Exception:
            do_rong = None
    hdr = ["[Script Info]", "ScriptType: v4.00+", "PlayResX: %d" % W, "PlayResY: %d" % H, "WrapStyle: 2",
           "ScaledBorderAndShadow: yes", "", "[V4+ Styles]",
           "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, "
           "Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, "
           "MarginR, MarginV, Encoding",
           "Style: Sub,%s,%d,&H00FFFFFF,&H0000FFFF,&H00000000,&H90000000,0,-1,0,0,100,100,1,0,1,%d,%d,2,60,60,%d,1"
           % (font_ten, co, vien, bong, marginv),
           "", "[Events]", "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text"]
    lines = []
    cum = gom_cum(tu, toi_da)
    mv = _mau_ass(vang)
    for ci, c in enumerate(cum):
        # cụm quá rộng → thu nhỏ riêng cụm đó (WrapStyle 2 không xuống dòng)
        fs = ""
        if do_rong:
            r = do_rong(" ".join(_sach(x["w"]) for x in c))
            if r > W * rong_toi_da:
                fs = "{\\fs%d}" % int(co * W * rong_toi_da / r)
        t_cum_end = c[-1]["e"] + keo_them
        if ci + 1 < len(cum):
            t_cum_end = min(t_cum_end, cum[ci + 1][0]["s"])
        for i, w in enumerate(c):
            t0 = w["s"] if i > 0 else c[0]["s"]
            t1 = c[i + 1]["s"] if i + 1 < len(c) else t_cum_end
            if t1 <= t0:
                continue
            parts = []
            for j, x in enumerate(c):
                s = _sach(x["w"])
                if j == i:
                    parts.append("{\\c%s&}%s{\\c&H00FFFFFF&}" % (mv, s))
                else:
                    parts.append(s)
            lines.append("Dialogue: 0,%s,%s,Sub,,0,0,0,,%s%s" % (_t(t0), _t(t1), fs, " ".join(parts)))
    return "\n".join(hdr + lines) + "\n", cum
