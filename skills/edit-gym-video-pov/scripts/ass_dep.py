"""Lớp chữ / bubble đẹp cho edit-gym-video-pov, vẽ bằng ASS (libass) — viên thuốc kính tối + huy hiệu vàng + bóng mờ,
thẻ tiêu đề kính, HUD REC, sub karaoke. Rộng chữ đo bằng PIL (hệ số K đã hiệu chuẩn với libass)."""
import os
from PIL import ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
FONT_FILE = os.path.join(os.path.dirname(HERE), "assets", "fonts", "BeVietnamPro-Black.ttf")
FN = "Be Vietnam Pro Black"   # tên đầy đủ — "Be Vietnam Pro" sẽ rơi về Arial (libass+DirectWrite)
K = 0.644               # libass: rộng thật = PIL(size) * K (đo 18/11/2026 trên font Black)
W, H = 1080, 1920
YEL = "&H0000D8FF"
WHITE = "&H00FFFFFF"
BLACK = "&H00000000"
NAVY = "&H0024160E"     # #0E1624
RED = "&H003030FF"

_font = ImageFont.truetype(FONT_FILE, 100)


def tw(text, size, spacing=0):
    return _font.getlength(text) * size / 100 * K + spacing * len(text)


def ts(t):
    t = max(0, t)
    return f"{int(t // 3600)}:{int(t % 3600 // 60):02d}:{t % 60:05.2f}"


def rr(w, h, r):
    """Hình chữ nhật bo góc (lệnh vẽ ASS), toạ độ tương đối góc trên-trái."""
    w, h, r = int(w), int(h), int(min(r, w / 2, h / 2))
    return (f"m {r} 0 l {w - r} 0 b {w} 0 {w} 0 {w} {r} l {w} {h - r} b {w} {h} {w} {h} {w - r} {h} "
            f"l {r} {h} b 0 {h} 0 {h} 0 {h - r} l 0 {r} b 0 0 0 0 {r} 0")


def shape(x, y, w, h, r, color, alpha=0x00, border=None, blur=0.6, layer=2, t0=0, t1=1, anim="", z=None):
    """1 dòng Dialogue vẽ hình bo góc."""
    p = "" if "\\move" in anim else f"\\pos({int(x)},{int(y)})"
    tag = (f"{{\\an7{p}{anim}\\1c{color}\\1a&H{alpha:02X}&\\bord0\\shad0\\blur{blur}")
    if border:
        bc, ba, bw = border
        tag += f"\\3c{bc}\\3a&H{ba:02X}&\\bord{bw}"
    tag += "\\p1}"
    return f"Dialogue: {layer},{ts(t0)},{ts(t1)},Sub,,0,0,0,,{tag}{rr(w, h, r)}{{\\p0}}"


def slide(x, y, dx=520, ms=260, fo=160):
    return f"\\move({int(x - dx)},{int(y)},{int(x)},{int(y)},0,{ms})\\fad(0,{fo})"


def pill(x, y, text, t0, t1, size=74, badge=True, color=YEL, txtcol=WHITE):
    """Bubble nhãn: kính tối bo tròn, huy hiệu vàng, chữ trắng, bóng mềm. Trả về list Dialogue."""
    h = int(size * 1.6)
    bd = int(h * 0.56) if badge else 0
    padL = int(h * 0.28) + (bd + 20 if badge else 10)
    padR = int(h * 0.42)
    tx = tw(text, size, 1.5)
    w = int(padL + tx + padR)
    out = []
    def pos(xc, yc):
        return slide(xc, yc)
    out.append(shape(x, y + 12, w, h, h / 2, BLACK, 0x70, blur=16, layer=1, t0=t0, t1=t1, anim=pos(x, y + 12)))
    out.append(shape(x, y, w, h, h / 2, NAVY, 0x30, border=(WHITE, 0x90, 2), blur=0.4, layer=2, t0=t0, t1=t1, anim=pos(x, y)))
    if badge:
        bx, by = x + int(h * 0.2), y + (h - bd) // 2
        out.append(shape(bx, by, bd, bd, bd / 2, color, 0x00, blur=0.5, layer=3, t0=t0, t1=t1, anim=pos(bx, by)))
        d = int(bd * 0.38)
        dx, dy = bx + (bd - d) // 2, by + (bd - d) // 2
        out.append(shape(dx, dy, d, d, d / 2, NAVY, 0x00, blur=0.3, layer=4, t0=t0, t1=t1, anim=pos(dx, dy)))
    cx, cy = x + padL, y + h // 2 - 2
    out.append(f"Dialogue: 5,{ts(t0)},{ts(t1)},Pill,,0,0,0,,{{\\an4{slide(cx, cy)}\\fs{size}\\1c{txtcol}}}{text}")
    return out, w, h


def build_ass(plan, sc, S, B, total, words, path, out_time):
    hdr = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {W}
PlayResY: {H}
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name,Fontname,Fontsize,PrimaryColour,SecondaryColour,OutlineColour,BackColour,Bold,Italic,Underline,StrikeOut,ScaleX,ScaleY,Spacing,Angle,BorderStyle,Outline,Shadow,Alignment,MarginL,MarginR,MarginV,Encoding
Style: Sub,{FN},104,{YEL},{WHITE},{BLACK},&H96000000,0,0,0,0,100,100,0,0,1,8,3,2,60,60,330,1
Style: Pill,{FN},56,{WHITE},{WHITE},{BLACK},&H00000000,0,0,0,0,100,100,1.5,0,1,0,0,4,0,0,0,1
Style: Ti,{FN},104,{WHITE},{WHITE},{BLACK},&H96000000,0,0,0,0,100,100,1,0,1,7,3,8,40,40,0,1
Style: Hud,{FN},54,{WHITE},{WHITE},{BLACK},&H00000000,0,0,0,0,100,100,2,0,1,0,0,4,0,0,0,1
Style: Big,{FN},110,{WHITE},{WHITE},{BLACK},&H96000000,0,0,0,0,100,100,1,0,1,9,3,5,40,40,0,1

[Events]
Format: Layer,Start,End,Style,Name,MarginL,MarginR,MarginV,Effect,Text
"""
    ev = []
    # ───── tiêu đề POV: thẻ kính + viên vàng "POV" + dòng trắng, từ khoá vàng
    ti = plan.get("title") if plan.get("lop_ass") else None
    if ti:
        t0, t1 = plan.get("title_t", [0.12, 3.9])
        y0 = plan.get("title_y", 860)
        hi = plan.get("title_hi", [])
        lines = ti[1:]
        pw = int(tw(ti[0], 150, 3) + 120); ph = 176
        lw = max(tw(l, 104, 1) for l in lines) if lines else 0
        cw = int(max(pw, lw) + 150)
        ch = 40 + ph + 30 + 130 * len(lines) + 24
        cx0 = (W - cw) // 2
        a = f"\\fad(80,300)"
        ev.append(shape(cx0, y0 + 14, cw, ch, 56, BLACK, 0x78, blur=22, layer=1, t0=t0, t1=t1, anim=a))
        ev.append(shape(cx0, y0, cw, ch, 56, NAVY, 0x38, border=(WHITE, 0xA0, 2), blur=0.4, layer=2, t0=t0, t1=t1, anim=a))
        px = (W - pw) // 2
        ev.append(shape(px, y0 + 40, pw, ph, ph / 2, YEL, 0x00, blur=0.5, layer=3, t0=t0 + 0.0, t1=t1,
                        anim=f"\\fad(60,300)"))
        ev.append(f"Dialogue: 5,{ts(t0)},{ts(t1)},Ti,,0,0,0,,{{\\an5\\pos(540,{y0 + 40 + ph // 2 + 4})\\fs150\\1c{NAVY}\\bord0\\shad0"
                  f"\\fad(60,300)\\fscx50\\fscy50\\t(0,180,\\fscx108\\fscy108)\\t(180,280,\\fscx100\\fscy100)}}{ti[0]}")
        y = y0 + 40 + ph + 30
        for j, line in enumerate(lines):
            d = int(140 * (j + 1))
            txt = line
            for hw in hi:
                txt = txt.replace(hw, "{\\1c" + YEL + "}" + hw + "{\\1c" + WHITE + "}")
            ev.append(f"Dialogue: 5,{ts(t0)},{ts(t1)},Ti,,0,0,0,,{{\\an8\\pos(540,{y})\\fad(60,300)\\alpha&HFF&"
                      f"\\t({d},{d + 1},\\alpha&H00&)\\fscx70\\fscy70\\t({d},{d + 220},\\fscx100\\fscy100)}}{txt}")
            y += 130
    # ───── nhãn khu vực / huy hiệu (bubble)
    for i, s in enumerate(sc):
        lb = s.get("label") if plan.get("lop_ass") else None
        if lb:
            a0 = s["_out0"] + s["_lo"] + s.get("label_dt", 0.12)
            a1 = s["_out0"] + s["_d"] - s["_hi"] - 0.05
            if s.get("label_dur"):
                a1 = min(a1, a0 + s["label_dur"])
            lines, _, _ = pill(64, 250, lb, a0, a1)
            ev += lines
        bg = s.get("badge") if plan.get("lop_ass") else None
        if bg:
            a0 = s["_out0"] + s["_lo"] + 0.1
            a1 = s["_out0"] + s["_d"] - s["_hi"] - 0.05
            lines, _, _ = pill(64, 250 if not lb else 410, bg, a0, a1, size=60, color=RED)
            ev += lines
        big = s.get("chu_lon")
        if big:
            a0 = s["_out0"] + s["_lo"] + 0.1
            a1 = a0 + s.get("chu_lon_dur", 1.3)
            ev.append(f"Dialogue: 4,{ts(a0)},{ts(a1)},Big,,0,0,0,,{{\\an5\\pos(540,860)\\fad(40,200)\\fscx60\\fscy60"
                      f"\\t(0,160,\\fscx112\\fscy112)\\t(160,260,\\fscx100\\fscy100)}}{big}")
    # ───── HUD REC (thẻ kính nhỏ + chấm đỏ nháy + đồng hồ)
    if plan.get("rec_hud", False):
        hx, hy, hw_, hh = 700, 92, 332, 80
        ev.append(shape(hx, hy + 8, hw_, hh, hh / 2, BLACK, 0x80, blur=10, layer=1, t0=0, t1=total))
        ev.append(shape(hx, hy, hw_, hh, hh / 2, NAVY, 0x40, border=(WHITE, 0xB0, 2), blur=0.3, layer=2, t0=0, t1=total))
        t = 0.0
        while t < total - 0.05:
            sec = int(t)
            on = int(t * 2) % 2 == 0
            if on:
                ev.append(shape(hx + 28, hy + 28, 24, 24, 12, RED, 0x00, blur=0.6, layer=3, t0=t, t1=min(total, t + 0.5)))
            ev.append(f"Dialogue: 5,{ts(t)},{ts(min(total, t + 0.5))},Hud,,0,0,0,,{{\\an4\\pos({hx + 70},{hy + hh // 2 - 2})}}"
                      f"REC  {sec // 60:02d}:{sec % 60:02d}")
            t += 0.5
    # ───── sub karaoke
    for (r0, r1) in plan.get("sub", []):
        ws = [w for w in words if w[1] >= r0 - 0.05 and w[2] <= r1 + 0.15]
        chunks, chunk = [], []
        for w in ws:
            if chunk and (len(chunk) >= 3 or w[1] - chunk[-1][2] > 0.6):
                chunks.append(chunk); chunk = []
            chunk.append(w)
        if chunk:
            chunks.append(chunk)
        for ci, ch in enumerate(chunks):
            o0 = out_time(sc, ch[0][1]); o1 = out_time(sc, ch[-1][2])
            if o0 is None or o1 is None:
                continue
            o1 = max(o1, o0 + 0.5) + 0.12
            if ci + 1 < len(chunks):
                nx = out_time(sc, chunks[ci + 1][0][1])
                if nx is not None:
                    o1 = min(o1, nx - 0.02)
            txt = ""
            for w in ch:
                ow0 = out_time(sc, w[1]) or o0
                ow1 = out_time(sc, w[2]) or o1
                txt += "{\\k%d}%s " % (max(5, int((ow1 - ow0) * 100)), w[0].upper())
            pre = "{\\fad(40,60)\\fscx85\\fscy85\\t(0,110,\\fscx100\\fscy100)}"
            ev.append(f"Dialogue: 6,{ts(o0)},{ts(o1)},Sub,,0,0,0,,{pre}{txt.strip()}")
    open(path, "w", encoding="utf-8-sig").write(hdr + "\n".join(ev) + "\n")
