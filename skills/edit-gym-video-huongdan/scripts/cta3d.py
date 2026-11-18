# -*- coding: utf-8 -*-
"""cta3d.py — CTA cuối video: nút FOLLOW 3D (khối đỏ bóng, lún khi bấm) + bàn tay 3D chỉ ngón bấm liên tục (loop)."""
import math
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFilter, ImageFont
from ve import *

_cache = {}
BTN_W, BTN_H, BTN_D = 600, 160, 18     # kích thước mặt nút + độ dày khối


def _grad(h, w, top, bot):
    k = np.linspace(0, 1, h, dtype=np.float32)[:, None, None]
    return (np.array(top, np.float32) * (1 - k) + np.array(bot, np.float32) * k) * np.ones((1, w, 1), np.float32)


def _pill_mask(w, h, r, S):
    m = Image.new('L', (w * S, h * S), 0)
    ImageDraw.Draw(m).rounded_rectangle((0, 0, w * S - 1, h * S - 1), radius=r * S, fill=255)
    return np.array(m).astype(np.float32) / 255.0


def build_button():
    if 'btn' in _cache: return _cache['btn']
    S = 3; w, h = BTN_W, BTN_H; r = h // 2
    m = _pill_mask(w, h, r, S)
    W2, H2 = w * S, h * S
    face = _grad(H2, W2, (255, 112, 122), (206, 28, 58))
    # vành sáng mép trên + tối mép dưới
    er1 = cv2.erode(m, np.ones((9, 9), np.uint8))
    rim = np.clip(m - er1, 0, 1)[..., None]
    yy = np.linspace(0, 1, H2, dtype=np.float32)[:, None, None]
    face = face * (1 - rim * 0.55 * (1 - yy)) + np.array((255, 190, 196), np.float32) * rim * 0.55 * (1 - yy)
    face = face * (1 - rim * 0.35 * yy)
    # gloss nửa trên
    g = np.zeros((H2, W2), np.float32)
    cv2.ellipse(g, (W2 // 2, int(H2 * 0.02)), (int(W2 * 0.46), int(H2 * 0.50)), 0, 0, 360, 1.0, -1, cv2.LINE_AA)
    g = cv2.GaussianBlur(g, (0, 0), 6 * S / 3) * m
    face = face + (255 - face) * (g[..., None] * 0.34)
    img = Image.fromarray(np.clip(face, 0, 255).astype(np.uint8)).convert('RGBA')
    # nội dung: icon người + dấu cộng, chữ FOLLOW
    d = ImageDraw.Draw(img)
    f = ImageFont.truetype(os.path.join(FONTS, F_BLACK), int(70 * S))
    txt = 'FOLLOW'
    tw = d.textlength(txt, font=f)
    ix = 78 * S; iy = H2 // 2
    # icon user + plus
    d.ellipse((ix - 22 * S, iy - 36 * S, ix + 22 * S, iy + 8 * S), fill=(255, 255, 255, 255))
    d.pieslice((ix - 40 * S, iy + 4 * S, ix + 40 * S, iy + 84 * S), 180, 360, fill=(255, 255, 255, 255))
    px, py = ix + 44 * S, iy - 6 * S
    d.rounded_rectangle((px - 5 * S, py - 20 * S, px + 5 * S, py + 20 * S), 3 * S, fill=(255, 255, 255, 255))
    d.rounded_rectangle((px - 20 * S, py - 5 * S, px + 20 * S, py + 5 * S), 3 * S, fill=(255, 255, 255, 255))
    tx = 150 * S + (W2 - 150 * S - 40 * S - tw) / 2
    ty = H2 // 2 - 3 * S
    d.text((tx + 3 * S, ty + 5 * S), txt, font=f, fill=(140, 10, 34, 200), anchor='lm')
    d.text((tx, ty), txt, font=f, fill=(255, 255, 255, 255), anchor='lm')
    a = (np.array(img)[..., :3]); alpha = (m * 255).astype(np.uint8)
    face_rgba = np.dstack([a, alpha])
    face_rgba = cv2.resize(face_rgba, (w, h), interpolation=cv2.INTER_AREA)
    # khối (mặt bên) tối hơn
    side = np.dstack([_grad(H2, W2, (150, 14, 40), (110, 8, 30)).astype(np.uint8), alpha])
    side = cv2.resize(side, (w, h), interpolation=cv2.INTER_AREA)
    # bóng
    sh = np.zeros((h + 160, w + 220), np.uint8)
    cv2.ellipse(sh, ((w + 220) // 2, h // 2 + 100), (w // 2 + 30, 46), 0, 0, 360, 255, -1, cv2.LINE_AA)
    sh = cv2.GaussianBlur(sh, (0, 0), 26)
    shadow = np.dstack([np.zeros((*sh.shape, 3), np.uint8), (sh * 0.62).astype(np.uint8)])
    _cache['btn'] = (face_rgba, side, shadow)
    return _cache['btn']


def build_hand():
    """Bàn tay kiểu CON TRỎ BẤM (như ảnh mẫu nút FOLLOW): găng trắng, viền đen đậm, ngón trỏ chếch lên trái,
    3 ngón gập, ngón cái bên trái, cổ tay áo. Trả (sprite RGBA, bóng RGBA, tip=(x,y))."""
    if 'hand' in _cache: return _cache['hand']
    S = 3; CW, CH = 440, 560
    W2, H2 = CW * S, CH * S
    OX, OY = 90, 50

    def newm(): return Image.new('L', (W2, H2), 0)

    def cap(d, p0, p1, w):
        P0 = ((p0[0] + OX) * S, (p0[1] + OY) * S); P1 = ((p1[0] + OX) * S, (p1[1] + OY) * S)
        d.line([P0, P1], fill=255, width=int(w * S))
        for P in (P0, P1): d.ellipse((P[0] - w * S / 2, P[1] - w * S / 2, P[0] + w * S / 2, P[1] + w * S / 2), fill=255)

    m = newm(); d = ImageDraw.Draw(m)
    cap(d, (125, 70), (125, 270), 54)                                               # ngón trỏ
    cap(d, (178, 152), (178, 290), 50)                                              # ngón giữa
    cap(d, (227, 172), (227, 296), 48)                                              # ngón áp út
    cap(d, (272, 198), (272, 300), 44)                                              # ngón út
    d.rounded_rectangle(((99 + OX) * S, (232 + OY) * S, (294 + OX) * S, (392 + OY) * S), 46 * S, fill=255)   # lòng bàn tay
    cap(d, (116, 336), (58, 270), 48)                                               # ngón cái
    body = np.array(m).astype(np.float32) / 255.0
    mc = newm(); dc = ImageDraw.Draw(mc)
    dc.rounded_rectangle(((120 + OX) * S, (380 + OY) * S, (284 + OX) * S, (452 + OY) * S), 16 * S, fill=255)  # tay áo
    cuff = np.array(mc).astype(np.float32) / 255.0

    def puffy(mask, hi, lo, light=(-0.45, -0.6)):
        mm = (mask > 0.5).astype(np.uint8)
        dtf = cv2.distanceTransform(mm, cv2.DIST_L2, 5).astype(np.float32)
        h = np.clip(dtf / (np.percentile(dtf[mm > 0], 97) + 1e-6), 0, 1) ** 0.5
        gy, gx = np.gradient(cv2.GaussianBlur(dtf, (0, 0), 8 * S / 3))
        nl = np.clip(-(gx * light[0] + gy * light[1]), -1, 1)
        nl = nl / (np.abs(nl).max() + 1e-6)
        k = np.clip(0.72 + 0.18 * h + 0.22 * nl, 0, 1)[..., None]
        col = np.array(lo, np.float32) + (np.array(hi, np.float32) - np.array(lo, np.float32)) * k
        return col, mm

    c_body, m_body = puffy(body, (255, 255, 255), (196, 204, 220))
    c_cuff, m_cuff = puffy(cuff, (222, 230, 246), (150, 164, 196))
    ink = np.array((22, 24, 34), np.float32)
    out = np.zeros((H2, W2, 3), np.float32)
    k_ink = np.ones((int(8 * S), int(8 * S)), np.uint8)
    union = np.maximum(m_body, m_cuff)
    ring_all = cv2.dilate(union, k_ink)
    out[ring_all > 0] = ink
    al = ring_all.astype(np.float32)
    for c, mm in ((c_cuff, m_cuff), (c_body, m_body)):
        ring = cv2.dilate(mm, np.ones((int(5 * S), int(5 * S)), np.uint8)) - mm
        out = out * (1 - ring[..., None]) + ink * ring[..., None]
        out = out * (1 - mm[..., None]) + c * mm[..., None]
    img = Image.fromarray(np.clip(out, 0, 255).astype(np.uint8)); dd = ImageDraw.Draw(img)
    ik = tuple(int(v) for v in ink)

    def ln(p0, p1, w=4):
        dd.line([((p0[0] + OX) * S, (p0[1] + OY) * S), ((p1[0] + OX) * S, (p1[1] + OY) * S)], fill=ik, width=int(w * S))

    ln((152, 150), (152, 232))          # ngón trỏ | giữa
    ln((203, 170), (203, 238))          # giữa | áp út
    ln((251, 196), (251, 244))          # áp út | út
    # vết gập ngón cái
    dd.arc(((100 + OX) * S, (270 + OY) * S, (150 + OX) * S, (330 + OY) * S), 20, 110, fill=ik, width=int(4 * S))
    # đường may tay áo
    dd.line([((120 + OX) * S, (396 + OY) * S), ((284 + OX) * S, (396 + OY) * S)], fill=(120, 132, 168), width=int(3 * S))
    sp = np.zeros((H2, W2), np.float32)
    cv2.ellipse(sp, ((112 + OX) * S, (120 + OY) * S), (7 * S, 40 * S), 0, 0, 360, 1.0, -1, cv2.LINE_AA)
    sp = cv2.GaussianBlur(sp, (0, 0), 6 * S / 3) * m_body
    rgb = np.array(img).astype(np.float32); rgb = rgb + (255 - rgb) * sp[..., None] * 0.5
    rgba = np.dstack([np.clip(rgb, 0, 255).astype(np.uint8), (np.clip(al, 0, 1) * 255).astype(np.uint8)])
    rgba = cv2.resize(rgba, (CW, CH), interpolation=cv2.INTER_AREA)
    tip = (125.0 + OX, 44.0 + OY)
    M = cv2.getRotationMatrix2D(tip, 16.0, 1.0)                                     # ngón chếch lên trái
    rgba = cv2.warpAffine(rgba, M, (CW, CH), flags=cv2.INTER_LINEAR, borderValue=(0, 0, 0, 0))
    sh = cv2.GaussianBlur(rgba[..., 3], (0, 0), 12)
    sh = cv2.warpAffine(sh, np.float32([[1, 0, 12], [0, 1, 20]]), (CW, CH))
    shadow = np.dstack([np.zeros((CH, CW, 3), np.uint8), (sh * 0.45).astype(np.uint8)])
    _cache['hand'] = (rgba, shadow, tip)
    return _cache['hand']


# ------------------------------------------------------------------ hoạt cảnh
BTN_C = (540, 1330)              # tâm nút (trong vùng an toàn)
T_BTN = 152.5                    # nút hiện
T_HAND = 153.2                   # bàn tay vào, bắt đầu loop
LOOP = 1.2                       # chu kỳ 1 lần bấm
TAP_PH = 0.60                    # pha bấm trong chu kỳ


def config(t_btn, t_hand):
    """Đặt giờ hiện nút + giờ tay vào (giây GỐC). Tay bấm lúc t_hand + TAP_PH * LOOP."""
    global T_BTN, T_HAND
    T_BTN, T_HAND = float(t_btn), float(t_hand)


def tap_times(t_end):
    """CHỈ 1 lần bấm (khách chốt 18/11/2026: nhấn 1 cái là đủ)."""
    t = round(T_HAND + TAP_PH * LOOP, 3)
    return [t] if t < t_end else []


def _hand_state(ts, tgt):
    """-> (tip xy, press 0..1, alpha). Tay trượt vào từ dưới-phải, bấm ĐÚNG 1 lần, rồi lùi nhẹ và đứng yên cạnh nút."""
    rest = (tgt[0] + 90, tgt[1] + 130)
    u = (ts - T_HAND) / LOOP
    if u >= 1.0: return rest, 0.0, 1.0
    ph = u
    if ph < 0.5:
        e = eo(ph / 0.5)
        st = (tgt[0] + 320, tgt[1] + 460)
        return lerp2(st, tgt, e), 0.0, c01(ph / 0.2)
    if ph < 0.72:
        pr = math.sin(math.pi * (ph - 0.5) / 0.22)
        return (tgt[0] - 4 * pr, tgt[1] + 10 * pr), pr, 1.0
    e = eio((ph - 0.72) / 0.28)
    return lerp2(tgt, rest, e), 0.0, 1.0


def draw(canvas, ts):
    if ts < T_BTN: return
    face, side, shadow = build_button()
    cx, cy = BTN_C
    k = back(prog(ts, T_BTN, T_BTN + 0.55))
    # vầng sáng nhịp thở
    glow(canvas, (cx, cy + 20), 330, COL['coral'], 0.22 + 0.08 * math.sin(ts * 5))
    # bấm
    tgt = (cx + 110, cy + 20)
    press = 0.0
    if ts >= T_HAND:
        _, press, _ = _hand_state(ts, tgt)
    sc = max(0.01, k)
    blit(canvas, shadow, cx, cy + 4 + BTN_D * .5, 0.9 * c01(k), sc, 'c')
    blit(canvas, side, cx, cy + BTN_D * sc, 1.0, sc, 'c')
    blit(canvas, face, cx, cy + BTN_D * sc * press, 1.0, sc * (1 - 0.015 * press), 'c')
    if ts < T_HAND: return
    # hiệu ứng mỗi lần bấm: vòng sóng + tia
    for tt in tap_times(ts + 0.01):
        d = ts - tt
        if 0 <= d < 0.5:
            p = d / 0.5
            circle(canvas, tgt, 24 + 120 * eo(p), COL['white'], False, max(2, int(9 * (1 - p))))
            for i in range(8):
                an = i * math.pi / 4 + .35; r0 = 90 + 70 * eo(p); r1 = r0 + 26 * (1 - p)
                line(canvas, (tgt[0] + r0 * math.cos(an), tgt[1] + r0 * math.sin(an)), (tgt[0] + r1 * math.cos(an), tgt[1] + r1 * math.sin(an)), COL['amber'], 7, 1 - p)
    # bàn tay 3D
    hand, hsh, tipl = build_hand()
    tip, pr, al = _hand_state(ts, tgt)
    s = 0.62 - 0.02 * pr
    ox, oy = tip[0] - tipl[0] * s, tip[1] - tipl[1] * s
    blit(canvas, hsh, ox, oy, al, s, 'tl')
    blit(canvas, hand, ox, oy, al, s, 'tl')
