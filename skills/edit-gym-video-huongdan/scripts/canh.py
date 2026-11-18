# -*- coding: utf-8 -*-
"""canh.py — các cảnh minh hoạ vẽ tay trên bảng (BW x BH). Mỗi cảnh: f(cv, t) với t = giây GỐC của video thô."""
import math
import numpy as np, cv2
from ve import *
from ve import _cum, _r
from hinh import *

BW, BH = 1008, 736
C_ = COL
FS = 1.18                      # phóng cỡ chữ trên bảng (bảng hiển thị thu nhỏ nên chữ phải to hơn)
_text0 = text
def text(cv, t, x, y, fname=F_XB, size=60, *a, **k):
    return _text0(cv, t, x, y, fname, int(size * FS), *a, **k)


# ------------------------------------------------------------------ tiện ích
def pill(cv, txt, cx, cy, fill, tcol=C_['ink'], size=34, a=1.0, sc=1.0, padx=34, h=None, font=F_XB, outline=None):
    sp = sprite(txt, font, int(size * FS), tcol)
    w = sp.shape[1] + padx * 2; h = h or int(size * FS * 1.9)
    w2, h2 = w * sc, h * sc
    rrect(cv, cx - w2 / 2, cy - h2 / 2, cx + w2 / 2, cy + h2 / 2, h2 / 2, fill, outline, 3, a)
    blit(cv, sp, cx, cy + 1, a, sc)


def pop(t, t0, dur=0.35):
    """hệ số bật (có nảy) của phần tử xuất hiện tại t0."""
    return back(prog(t, t0, t0 + dur))


def fade(t, t0, t1, d=0.25):
    """1 trong [t0,t1], mờ vào/ra."""
    return min(prog(t, t0, t0 + d), 1 - prog(t, t1 - d, t1))


def spine_pt(C, s):
    cum = _cum(C); i = int(np.searchsorted(cum, cum[-1] * s)); i = min(max(i, 0), len(C) - 1)
    return C[i]


def note(cv, txt, x, y, col=C_['amber'], size=40, a=1.0, sc=1.0, rot=-3, anchor='c'):
    text(cv, txt, x, y, F_HAND, size, col, a, sc, anchor, rot=rot)


def tag(cv, txt, x, y, col, a=1.0, sc=1.0, size=44, anchor='c', sub=None, subcol=None):
    text(cv, txt, x, y, F_BLACK, size, col, a, sc, anchor, stroke=0)
    if sub: text(cv, sub, x, y + size * FS * .95, F_M, int(size * .55), subcol or C_['dim'], a, sc, anchor)


def glow_pulse(cv, c, r, col, t, a=0.5, spd=5.0):
    glow(cv, c, r * (1 + .08 * math.sin(t * spd)), col, a * (0.75 + .25 * math.sin(t * spd)))


def sparkle_pain(cv, c, t, col=C_['coral'], a=1.0, n=3, r=70):
    """tia nhói quanh điểm đau."""
    for i in range(n):
        ang = i * 2 * math.pi / n + 0.6
        ph = (t * 2.2 + i * .33) % 1.0
        d0 = r * (0.7 + 0.5 * ph); d1 = r * (1.0 + 0.5 * ph)
        p0 = (c[0] + d0 * math.cos(ang), c[1] + d0 * math.sin(ang)); p1 = (c[0] + d1 * math.cos(ang), c[1] + d1 * math.sin(ang))
        mid = ((p0[0] + p1[0]) / 2 + 10 * math.cos(ang + 1.57), (p0[1] + p1[1]) / 2 + 10 * math.sin(ang + 1.57))
        stroke(cv, [p0, mid, p1], col, 7, 1, i, 0, a=a * (1 - ph * .6))


def stamp_title(cv, txt, cx, cy, col, size, a=1.0, sc=1.0, ext=C_['ink'], rot=0):
    text(cv, txt, cx, cy, F_BLACK, size, col, a, sc, 'c', ext=(ext, 9), rot=rot)


# ------------------------------------------------------------------ A. vùng đau + võng lưng (0 – 11.3)
def sA(cv, t):
    f = eo(prog(t, 0.2, 2.2))
    lord = 1.0 + 0.95 * eio(prog(t, 5.1, 6.3))
    hl = eo(prog(t, 1.7, 2.7))
    ox, oy, hg = 250, 66, 560
    if lord > 1.03:
        dashed(cv, spine_curve(ox, oy, hg, 1.0), C_['ice'], 4, 1.0, 14, 11, a=eo(prog(t, 5.2, 6.0)) * .9)
    C = spine(cv, ox, oy, hg, lord, f, hl, pulse=t, tilt=(lord - 1) * 14)
    P = spine_pt(C, 0.68)
    # nhãn vùng đau
    if t > 2.1:
        a = pop(t, 2.2)
        stroke(cv, [P + (50, -10), (P[0] + 190, P[1] - 150), (600, 170)], C_['coral'], 6, eo(prog(t, 2.2, 2.9)), 3, 1.2)
        tag(cv, 'VÙNG LƯNG DƯỚI', 745, 120, C_['coral'], a, size=44, sub='thắt lưng L1 – L5', subcol=C_['amber'])
    # võng lưng
    if t > 5.3:
        a = pop(t, 5.4)
        text(cv, 'VÕNG LƯNG', 735, 300, F_BLACK, 56, C_['amber'], a, 1.0, 'c', ext=(C_['ink'], 8))
        note(cv, 'cong quá mức!', 735, 365, C_['chalk'], 40, a)
        arrow(cv, (650, 400), (P[0] + 70, P[1] - 20), C_['amber'], 6, eo(prog(t, 5.8, 6.6)), 26)
        if t > 6.4:
            dashed(cv, [(560, 690), (610, 690)], C_['ice'], 4, 1.0, 10, 8, a=pop(t, 6.4))
            text(cv, 'đường cong bình thường', 625, 690, F_M, 26, C_['ice'], pop(t, 6.4), 1.0, 'l')
    # áp lực + nhói
    if t > 9.3:
        a = fade(t, 9.3, 99, .3)
        s2 = eo(prog(t, 9.4, 10.0))
        for sgn in (-1, 1):
            p0 = (P[0] + sgn * (170 - 30 * s2), P[1] + 10); p1 = (P[0] + sgn * 55, P[1] + 10)
            arrow(cv, p0, p1, C_['coral'], 9, 1.0, 34, a=a)
        sparkle_pain(cv, (P[0] + 4, P[1] + 8), t, C_['coral'], a, 4, 105)
        pill(cv, 'ÁP LỰC · TỨC', 735, 560, C_['coral'], C_['white'], 38, pop(t, 9.5), 1.0)
    return cv


# ------------------------------------------------------------------ B. hai bài tập (11.3 – 27.7)
def card(cv, x, y, w, h, num, title, subt, icon, t, t0, col):
    k = back(prog(t, t0, t0 + 0.5))
    if k <= 0: return
    yy = y + (1 - k) * 160; a = c01(k * 1.4)
    rrect(cv, x, yy, x + w, yy + h, 34, (22, 46, 78), col, 4, a)
    lay_alpha(cv, a, lambda c: circle(c, (x + 62, yy + 62), 40, col))
    text(cv, str(num), x + 62, yy + 64, F_BLACK, 52, C_['ink'], a)
    text(cv, title, x + 112, yy + 62, F_BLACK, 28, C_['chalk'], a, 1.0, 'l')
    text(cv, subt, x + w / 2, yy + h - 40, F_M, 25, C_['dim'], a)
    if k < 0.8: return
    if icon == 'ly':
        lying(cv, (x + 30, yy + 130, w - 60, 150), LY['lift'], 0, 1, C_['chalk'], C_['dim'], 11)
    else:
        kneeling(cv, (x + 90, yy + 100, w - 180, 215), KN['up'], 1, C_['chalk'], C_['dim'], 11)


def sB(cv, t):
    card(cv, 24, 30, 470, 400, 1, 'ÉP LƯNG SÁT SÀN', 'giải phóng cơ thắt lưng', 'ly', t, 12.9, C_['mint'])
    card(cv, 514, 30, 470, 400, 2, 'GIÃN CƠ GẬP HÔNG', 'giảm căng vùng thắt lưng', 'kn', t, 17.4, C_['amber'])
    # kết quả
    for i, (tx, t0) in enumerate((('Giải phóng lưng', 22.6), ('Bớt áp lực', 24.2), ('Giảm nhói', 26.4))):
        if t < t0: continue
        k = pop(t, t0)
        cx = 24 + 160 + i * 332
        rrect(cv, cx - 150 * k, 530, cx + 150 * k, 590, 30, C_['mint'], None, 0, c01(k * 1.5))
        text(cv, tx, cx + 8, 561, F_XB, 28, C_['ink'], c01(k * 1.5), k)
        check(cv, (cx - 112, 561), 11 * k, C_['ink'], 1.0, 5)
    if t > 22.3:
        text(cv, 'KẾT QUẢ', 504, 480, F_HAND, 36, C_['amber'], pop(t, 22.3), 1.0, 'c', rot=-2)
    return cv


# ------------------------------------------------------------------ C. cơ gập hông (27.7 – 32.6)
def sC(cv, t):
    f = eo(prog(t, 27.9, 29.3))
    ox, oy, hg = 250, 70, 520
    C = spine(cv, ox, oy, hg, 1.0, f, 0.0)
    base = C[-1]
    path = psoas_path(base, hg, 0)
    pf = eio(prog(t, 29.7, 31.2))
    if pf > 0:
        q = partial(path, pf)
        glow_pulse(cv, q[-1], 90, C_['coral'], t, .6)
        stroke(cv, q, C_['coral'], 30, 1, 9, 1.0, out=(C_['ink'], 8))
        stroke(cv, q, (255, 150, 150), 10, 1, 9, 1.0)
    if t > 30.7:
        a = pop(t, 30.8)
        tag(cv, 'CƠ GẬP HÔNG', 735, 190, C_['coral'], a, size=56, sub='(cơ thắt lưng chậu)', subcol=C_['amber'])
        stroke(cv, [(600, 300), (500, 330), (path[14][0] + 30, path[14][1])], C_['coral'], 5, eo(prog(t, 30.9, 31.5)), 2, 1)
    if t > 31.1:
        note(cv, 'phía trước của hông', 760, 400, C_['chalk'], 36, pop(t, 31.2))
        arrow(cv, (700, 450), (520, 500), C_['amber'], 6, eo(prog(t, 31.4, 32.0)), 28)
    pill(cv, 'BÀI 1 · MỞ CƠ GẬP HÔNG', 740, 80, C_['amber'], C_['ink'], 28, pop(t, 28.4), 1, 60)
    return cv


# ------------------------------------------------------------------ D. nằm áp lưng xuống sàn (32.6 – 47.4)
def _arch_d(t):
    a = 64.0
    k = a * (1 - eio(prog(t, 35.1, 36.0)))
    k += 58.0 * eio(prog(t, 42.7, 43.6)) * (1 - eio(prog(t, 44.6, 45.4)))
    return k


def sD(cv, t):
    box = (24, 70, 960, 340)
    arch = _arch_d(t)
    fw = eo(prog(t, 32.7, 33.8))
    gap_col = C_['coral'] if arch > 0.5 else C_['mint']
    P = lying(cv, box, LY['bent'], max(arch, 0), fw, gap_col=C_['coral'])
    hip = np.array(P['hip']); sh = np.array(P['sh'])
    wrong1 = 32.8 <= t < 35.4
    wrong2 = 42.7 <= t < 45.1
    right = (35.5 <= t < 42.7) or t >= 45.1
    spot = (hip[0] - 70, hip[1] - 28)
    if wrong1 or wrong2:
        glow_pulse(cv, (hip[0] - 90, hip[1] - arch * .6), 120, C_['coral'], t, .45, 7)
    # nhãn trạng thái
    if wrong1:
        k = pop(t, 32.9)
        rrect(cv, 70, 470, 940, 600, 36, (60, 24, 36), C_['coral'], 4, c01(k * 1.4))
        cross(cv, (150, 535), 54 * k, C_['coral'], eo(prog(t, 33.0, 33.6)), 11)
        text(cv, 'HỞ LƯNG · VÕNG LƯNG', 540, 520, F_BLACK, 44, C_['coral'], c01(k * 1.4))
        text(cv, 'lưng bị cong lên khỏi mặt sàn', 540, 570, F_M, 28, C_['chalk'], c01(k * 1.4))
    if t >= 35.4 and t < 42.7 or t >= 45.1:
        k = pop(t, 35.5 if t < 42.7 else 45.2)
        rrect(cv, 70, 470, 940, 600, 36, (14, 64, 56), C_['mint'], 4, c01(k * 1.4))
        check(cv, (150, 535), 50 * k, C_['mint'], eo(prog(t, 35.6, 36.2)) if t < 42.7 else 1, 12)
        text(cv, 'LƯNG ÁP SÁT MẶT SÀN', 540, 520, F_BLACK, 44, C_['mint'], c01(k * 1.4))
        text(cv, 'thắt lưng dính xuống sàn, không để hở', 540, 570, F_M, 28, C_['chalk'], c01(k * 1.4))
        # mũi tên ép xuống
        if 35.8 <= t < 42.7 or t > 45.3:
            ph = (t * 1.6) % 1.0
            for dx in (-120, -60, 0):
                arrow(cv, (hip[0] + dx - 40, hip[1] - 120 + ph * 30), (hip[0] + dx - 40, hip[1] - 40), C_['mint'], 7, 1.0, 26, a=0.9)
    if wrong2:
        k = pop(t, 42.8)
        rrect(cv, 70, 470, 940, 600, 36, (60, 24, 36), C_['coral'], 4, c01(k * 1.4))
        cross(cv, (150, 535), 54 * k, C_['coral'], eo(prog(t, 42.9, 43.5)), 11)
        text(cv, 'KHÔNG ƯỠN · KHÔNG VÕNG LÊN', 540, 520, F_BLACK, 40, C_['coral'], c01(k * 1.4))
        text(cv, 'sẽ ảnh hưởng ngay vùng thắt lưng', 540, 570, F_M, 28, C_['chalk'], c01(k * 1.4))
    # cảnh báo thoát vị đĩa đệm
    if 37.6 <= t < 41.6:
        k = pop(t, 37.7) * fade(t, 37.6, 41.6, .3)
        pill(cv, 'THOÁT VỊ ĐĨA ĐỆM · CÀNG PHẢI CHÚ Ý', 504, 665, C_['amber'], C_['ink'], 27, k, 1.0, 54)
        circle(cv, spot, 22 + 5 * math.sin(t * 8), C_['amber'], False, 5)
    return cv


# ------------------------------------------------------------------ E. các bước bài 1 (47.4 – 75.0)
STEPS = [('Co gối · thả lỏng người', 55.4, 61.3), ('Đưa chân lên · dán lưng dưới xuống sàn', 61.3, 66.7),
         ('Gồng nhẹ cơ lõi (bụng trước)', 66.7, 70.2), ('Duỗi chân xuống · co lên', 70.2, 74.4)]


def _pose_E(t):
    A, B, Cx = LY['bent'], LY['lift'], LY['ext']
    if t < 61.3: return A
    if t < 62.3: return blend_pose(A, B, eio(prog(t, 61.3, 62.3)))
    if t < 70.5: return B
    if t < 72.0: return blend_pose(B, Cx, eio(prog(t, 70.5, 72.0)))
    if t < 72.4: return Cx
    if t < 73.5: return blend_pose(Cx, B, eio(prog(t, 72.4, 73.5)))
    if t < 74.6: return B
    # lặp minh hoạ
    ph = ((t - 74.6) / 1.8) % 1.0
    return blend_pose(B, Cx, 0.5 - 0.5 * math.cos(ph * 2 * math.pi))


def sE(cv, t):
    box = (24, 40, 960, 330)
    P = lying(cv, box, _pose_E(t), 0, eo(prog(t, 47.5, 48.4)))
    hip = np.array(P['hip']); sh = np.array(P['sh']); kn = np.array(P['kn']); an = np.array(P['an'])
    # nhấn chân đang tập
    if 47.4 <= t < 55.6:
        a = fade(t, 47.6, 55.6)
        pill(cv, 'MỖI LẦN MỘT CHÂN', 504, 440, C_['amber'], C_['ink'], 40, pop(t, 49.0) * a, 1, 70)
        glow_pulse(cv, ((hip[0] + kn[0]) / 2, (hip[1] + kn[1]) / 2), 100, C_['mint'], t, .55)
        note(cv, 'đau nặng → từng chân một thôi', 504, 520, C_['chalk'], 36, pop(t, 51.6) * a)
    # mũi tên dán lưng dưới xuống sàn
    if 62.4 <= t < 66.0:
        ph = (t * 1.4) % 1.0
        arrow(cv, (hip[0] - 90, hip[1] - 150 + ph * 25), (hip[0] - 90, hip[1] - 38), C_['mint'], 8, 1.0, 30)
        glow_pulse(cv, (hip[0] - 90, hip[1] + 2), 70, C_['mint'], t, .5)
        text(cv, 'ép lưng dưới xuống sàn', hip[0] - 90, hip[1] - 185, F_B, 26, C_['mint'], 1.0)
    # gồng cơ lõi
    if 66.8 <= t < 70.0:
        c = (lerp(sh[0], hip[0], .55), sh[1] - 4)
        glow_pulse(cv, c, 95, C_['amber'], t, .85, 9)
        circle(cv, c, 36 + 8 * math.sin(t * 9), C_['amber'], False, 5)
        text(cv, 'CƠ LÕI', c[0], c[1] - 92, F_BLACK, 34, C_['amber'], 1.0, 1.0, 'c', ext=(C_['ink'], 5))
    # duỗi / co
    if 70.4 <= t < 74.4:
        e = eio(prog(t, 70.5, 72.0)) if t < 72.2 else 1 - eio(prog(t, 72.4, 73.5))
        arrow(cv, (an[0] - 10, an[1] - 70), (an[0] + 40, an[1] + (30 if t < 72.3 else -30)), C_['mint'], 8, 1.0, 28, curve=.25)
    # thanh các bước
    for i, (st, a0, a1) in enumerate(STEPS):
        k = pop(t, 55.0 + i * .18)
        if t < 55.0: break
        y = 450 + i * 68
        act = a0 <= t < a1; done = t >= a1
        fill = (16, 38, 62) if not act else (30, 62, 98)
        out = C_['amber'] if act else (C_['mint'] if done else (40, 66, 100))
        xx = 40 + (1 - k) * 700
        rrect(cv, xx, y, xx + 928, y + 58, 29, fill, out, 4 if act else 2, 1.0)
        circle(cv, (xx + 34, y + 29), 22, C_['mint'] if done else (C_['amber'] if act else (60, 86, 120)))
        if done: check(cv, (xx + 34, y + 30), 14, C_['ink'], 1.0, 5)
        else: text(cv, str(i + 1), xx + 34, y + 31, F_BLACK, 28, C_['ink'] if act else C_['chalk'], 1.0)
        text(cv, st, xx + 72, y + 30, F_B if act else F_M, 29, C_['white'] if act else (C_['chalk'] if done else C_['dim']), 1.0, 1.0, 'l')
    if t >= 74.4:
        k = pop(t, 74.5)
        circle(cv, (880, 150), 60 * k, C_['mint'])
        check(cv, (880, 154), 40 * k, C_['ink'], 1.0, 12)
    return cv


# ------------------------------------------------------------------ F. bài 2 tựa đề (75 – 85.9)
def sF(cv, t):
    k = pop(t, 75.1, .5)
    stamp_title(cv, 'BÀI 2', 300, 92, C_['amber'], 78, c01(k * 1.5), k, C_['coral'])
    stamp_title(cv, 'GIÃN CƠ GẬP HÔNG', 540, 190, C_['chalk'], 58, c01(pop(t, 75.5) * 1.5), pop(t, 75.5), (30, 60, 96))
    P = kneeling(cv, (150, 245, 700, 470), KN['up'], eo(prog(t, 76.0, 79.0)))
    if 79.6 <= t < 83.2:
        a = fade(t, 79.6, 83.2)
        pill(cv, 'LƯNG ĐƯỢC GIẢI PHÓNG · THOÁNG RA', 504, 650, C_['mint'], C_['ink'], 29, a * pop(t, 79.7), 1, 60)
        for dx in (-1, 1):
            arrow(cv, (P['sh'][0] + dx * 40, P['sh'][1] + 50), (P['sh'][0] + dx * 150, P['sh'][1] + 50), C_['mint'], 6, eo(prog(t, 80.5, 81.5)), 24, a=a)
    if 84.6 <= t:
        k = pop(t, 84.7)
        hipf = (P['hip'][0] + 26, P['hip'][1] - 8)
        glow_pulse(cv, hipf, 90, C_['coral'], t, .7)
        glow_pulse(cv, (P['hip'][0] - 26, P['hip'][1] + 20), 60, C_['coral'], t, .45)
        pill(cv, 'VÙNG CƠ HÔNG · 2 CHỖ NÀY', 790, 330, C_['coral'], C_['white'], 28, c01(k * 1.4), k, 58)
        stroke(cv, [(660, 365), hipf + np.array([40, 0])], C_['coral'], 5, eo(prog(t, 84.8, 85.4)), 3, 1)
    return cv


# ------------------------------------------------------------------ G1. thảm / giường (85.7 – 94.4)
def _mat(cv, cx, cy, s, a=1.0):
    pts = [(cx - 190 * s, cy + 40 * s), (cx - 90 * s, cy - 60 * s), (cx + 200 * s, cy - 60 * s), (cx + 100 * s, cy + 40 * s)]
    lay_alpha(cv, a, lambda c: (poly(c, pts, C_['ink'], True), poly(c, [(p[0] + 0, p[1] - 6) for p in pts], (60, 150, 230), True), poly(c, pts, (150, 205, 255), False, 3)))


def _bed(cv, cx, cy, s, a=1.0):
    def d(c):
        rrect(c, cx - 190 * s, cy - 110 * s, cx - 160 * s, cy + 70 * s, 10, (150, 110, 80), None)
        rrect(c, cx - 190 * s, cy - 10 * s, cx + 190 * s, cy + 40 * s, 16, (225, 232, 245), (150, 170, 200), 3)
        rrect(c, cx - 180 * s, cy - 50 * s, cx - 60 * s, cy - 8 * s, 18, (250, 250, 255), (150, 170, 200), 3)
        rrect(c, cx + 150 * s, cy - 10 * s, cx + 190 * s, cy + 70 * s, 10, (150, 110, 80), None)
        rrect(c, cx - 190 * s, cy + 30 * s, cx - 165 * s, cy + 70 * s, 8, (150, 110, 80), None)
    lay_alpha(cv, a, d)


def sG1(cv, t):
    k1 = pop(t, 85.9, .5); k2 = pop(t, 88.5, .5)
    _mat(cv, 270, 300, 1.1 * k1, c01(k1 * 1.5))
    text(cv, 'THẢM', 270, 400, F_BLACK, 52, C_['ice'], c01(k1 * 1.5), k1)
    note(cv, 'hoặc', 504, 300, C_['amber'], 46, pop(t, 88.2))
    _bed(cv, 750, 310, 1.0 * k2, c01(k2 * 1.5))
    text(cv, 'GIƯỜNG', 750, 400, F_BLACK, 52, C_['ice'], c01(k2 * 1.5), k2)
    if t > 90.8:
        k = pop(t, 90.9)
        pill(cv, 'QUỲ GỐI XUỐNG THOẢI MÁI', 504, 560, C_['mint'], C_['ink'], 38, c01(k * 1.4), k, 80)
        for cx in (270, 750):
            circle(cv, (cx, 480), 26 * k, C_['mint']); check(cv, (cx, 482), 16 * k, C_['ink'], 1.0, 6)
    return cv


# ------------------------------------------------------------------ G2. quỳ 1 gối: 90°, ánh mắt, tịnh tiến, sai/đúng, căng, 15 lần (94.4 – 137.8)
def _pose_K(t):
    U, S, A = KN['up'], KN['shift'], KN['arch']
    if t < 111.4: return U, 0.0
    if t < 113.8: return blend_pose(U, S, eio(prog(t, 111.4, 113.8)) * .35), 0.0
    if t < 116.2: return blend_pose(U, S, eio(prog(t, 113.8, 116.2))), 0.0
    if t < 119.3: return S, 0.0
    if t < 120.3: k = eio(prog(t, 119.3, 120.3)); return blend_pose(S, A, k), 46 * k
    if t < 124.5: return A, 46 + 6 * math.sin(t * 4)
    if t < 125.8: k = eio(prog(t, 124.5, 125.8)); return blend_pose(A, S, k), 46 * (1 - k)
    if t < 128.6: return S, 0.0
    ph = 0.5 - 0.5 * math.cos((t - 128.6) * 1.9)
    return blend_pose(KN['up'], S, 0.7 + 0.3 * ph), 0.0


def _right_angle(cv, c, v1, v2, col, a=1.0, size=44):
    v1 = np.array(v1, float); v2 = np.array(v2, float)
    v1 /= np.linalg.norm(v1) + 1e-6; v2 /= np.linalg.norm(v2) + 1e-6
    p = [c + v1 * size, c + v1 * size + v2 * size, c + v2 * size]
    stroke(cv, p, col, 6, 1, 4, 0, a=a)


def sG2(cv, t):
    box = (70, 70, 860, 640)
    pose, arch = _pose_K(t)
    P = kneeling(cv, box, pose, eo(prog(t, 94.5, 96.6)), torso_arch=arch)
    s = box[2] / 800.0
    sh = np.array(P['sh']); hip = np.array(P['hip']); head = np.array(P['head']); kn = np.array(P['kn']); an = np.array(P['an'])
    kb = np.array(P['kb']); ab = np.array(P['ab'])
    text(cv, 'BÀI 2 · GIÃN CƠ GẬP HÔNG', 504, 44, F_B, 26, C_['dim'], 1.0)
    # bước chân trước
    if 96.8 <= t < 98.8:
        a = fade(t, 96.8, 98.8)
        arrow(cv, (an[0] - 150, an[1] + 12), (an[0] - 20, an[1] + 12), C_['amber'], 8, eo(prog(t, 96.9, 97.7)), 30, a=a)
        text(cv, 'BƯỚC CHÂN TRƯỚC', an[0] - 30, an[1] + 62, F_B, 28, C_['amber'], a)
    # góc vuông 90° gối trước
    if t >= 98.8:
        k = pop(t, 98.9)
        v_th = hip - kn; v_sh = an - kn
        _right_angle(cv, kn, v_th, v_sh, C_['amber'], c01(k), 46)
        text(cv, '90°', kn[0] + 95, kn[1] + 78, F_BLACK, 52, C_['amber'], c01(k * 1.4), k, 'c', ext=(C_['ink'], 6))
        if 98.8 <= t < 102.0:
            pill(cv, 'CẲNG CHÂN & XƯƠNG ĐÙI', 690, 120, C_['amber'], C_['ink'], 26, pop(t, 99.0) * fade(t, 98.8, 102.2), 1, 54)
    if t >= 102.2:
        k = pop(t, 102.3)
        v_th = hip - kb; v_sh = ab - kb
        _right_angle(cv, kb, v_th, v_sh, C_['amber'], c01(k), 40)
        text(cv, '90°', kb[0] - 60, kb[1] - 60, F_BLACK, 46, C_['amber'], c01(k * 1.4), k, 'c', ext=(C_['ink'], 6))
        if t < 104.2:
            pill(cv, 'MẶT SAU CŨNG VẬY', 330, 120, C_['amber'], C_['ink'], 26, pop(t, 102.4) * fade(t, 102.2, 104.2), 1, 54)
    # ánh mắt + trọng tâm
    if 104.4 <= t < 110.2:
        a = fade(t, 104.4, 110.2, .35)
        gz = head + (30, 0)
        arrow(cv, gz, gz + (170, 0), C_['ice'], 7, eo(prog(t, 105.8, 106.8)), 28, a=a)
        text(cv, 'ÁNH MẮT', head[0] + 290, head[1] - 22, F_B, 28, C_['ice'], a)
        com = np.array([hip[0] + 8, (hip[1] + sh[1]) / 2])
        glow_pulse(cv, com, 55, C_['amber'], t, .8)
        circle(cv, com, 13, C_['amber'])
        arrow(cv, com + (20, 0), com + (200, 0), C_['amber'], 7, eo(prog(t, 107.0, 108.4)), 28, a=a)
        text(cv, 'TRỌNG TÂM', com[0] + 330, com[1] - 4, F_B, 28, C_['amber'], a)
        pill(cv, 'NHÌN THẲNG · DỒN VỀ PHÍA TRƯỚC', 504, 668, C_['ice'], C_['ink'], 28, pop(t, 108.6) * a, 1, 56)
    # tịnh tiến về trước
    if 113.9 <= t < 119.0:
        a = fade(t, 113.9, 119.0, .35)
        y0 = hip[1] + 120
        arrow(cv, (hip[0] - 150, y0), (hip[0] + 150, y0), C_['mint'], 10, eo(prog(t, 114.0, 115.4)), 36, a=a)
        text(cv, 'TỊNH TIẾN VỀ PHÍA TRƯỚC', 504, 84, F_BLACK, 34, C_['mint'], a * pop(t, 114.1))
    # sai
    if 119.4 <= t < 124.4:
        a = fade(t, 119.4, 124.4, .3)
        pill(cv, 'SAI · ƯỠN LƯNG', 760, 100, C_['coral'], C_['white'], 38, a * pop(t, 119.5), 1, 70)
        cross(cv, (470, 100), 32, C_['coral'], eo(prog(t, 119.6, 120.2)), 9)
        lum = (lerp(hip[0], sh[0], .30) + 14, lerp(hip[1], sh[1], .30))
        glow_pulse(cv, lum, 100, C_['coral'], t, .75, 8)
        if t > 121.8:
            sparkle_pain(cv, lum, t, C_['coral'], a, 4, 85)
            text(cv, 'mỏi · căng lưng', lum[0] - 190, lum[1] - 60, F_HAND, 34, C_['coral'], pop(t, 121.9), 1.0, 'c', rot=-4)
    # đúng
    if 124.7 <= t < 128.6:
        a = fade(t, 124.7, 128.6, .3)
        pill(cv, 'ĐÚNG · LƯNG THẲNG', 650, 100, C_['mint'], C_['ink'], 30, a * pop(t, 124.8), 1, 60)
        check(cv, (150, 100), 32, C_['mint'], eo(prog(t, 124.9, 125.5)), 10)
        dashed(cv, [sh + (0, -70), hip + (0, 20)], C_['mint'], 4, eo(prog(t, 125.2, 126.0)), 14, 10, a=a)
        arrow(cv, (hip[0] - 150, hip[1] + 120), (hip[0] + 150, hip[1] + 120), C_['mint'], 9, eo(prog(t, 126.4, 127.6)), 34, a=a)
    # căng cơ gập hông chân sau
    if 128.7 <= t < 137.8:
        a = pop(t, 128.8)
        hz = (hip[0] + 30 * s, hip[1] - 6 * s)
        glow_pulse(cv, hz, 105, C_['coral'], t, .85, 6)
        for i in range(3):
            ph = (t * 1.2 + i / 3) % 1.0
            circle(cv, hz, 30 + ph * 90, C_['coral'], False, 4) if False else None
        arrow(cv, (hz[0] - 220 * 0 + 150, hz[1] - 150), (hz[0] + 30, hz[1] - 20), C_['coral'], 6, eo(prog(t, 129.8, 130.6)), 26)
        pill(cv, 'CĂNG CƠ GẬP HÔNG CHÂN SAU', 640, 110 if t < 135.0 else -999, C_['coral'], C_['white'], 29, c01(a * 1.4) * fade(t, 128.7, 135.0, .3), 1, 58)
    # 15 lần
    if t >= 135.0:
        k = pop(t, 135.0, .5)
        n = int(round(15 * eio(prog(t, 135.2, 137.2))))
        c = (810, 225)
        circle(cv, c, 118 * k, (14, 40, 70)); circle(cv, c, 118 * k, C_['amber'], False, 5)
        ring = arc_pts(c, 104 * k, -90, -90 + 360 * (n / 15.0), 60)
        if len(ring) > 1: stroke(cv, ring, C_['amber'], 12, 1, 3, 0)
        text(cv, str(n), c[0], c[1] - 6, F_BLACK, 92, C_['white'], c01(k * 1.4), 1.0)
        text(cv, 'LẦN', c[0], c[1] + 66, F_B, 30, C_['amber'], c01(k * 1.4))
        text(cv, 'KHOẢNG', c[0], c[1] - 110 * k - 20, F_HAND, 32, C_['chalk'], c01(k * 1.4), 1, 'c', rot=-3)
    return cv


# ------------------------------------------------------------------ H. câu hỏi / comment (137.8 – 147.7)
def bubble(cv, x, y, w, h, txt, sub, t, t0, col, tail='l'):
    k = pop(t, t0, .45)
    if k <= 0: return
    cx, cy = x + w / 2, y + h / 2
    x0, y0, x1, y1 = cx - w / 2 * k, cy - h / 2 * k, cx + w / 2 * k, cy + h / 2 * k
    rrect(cv, x0, y0, x1, y1, 36 * k, (236, 244, 252), None, 0, c01(k * 1.5))
    tx = (x0 + 70 * k) if tail == 'l' else (x1 - 70 * k)
    poly(cv, [(tx, y1 - 2), (tx + 40 * k, y1 - 2), (tx + (-10 if tail == 'l' else 50) * k, y1 + 42 * k)], (236, 244, 252), True)
    circle(cv, (x0 + 56, cy), 30 * k, col); text(cv, '?', x0 + 56, cy + 2, F_BLACK, 42, C_['white'], c01(k * 1.4))
    text(cv, txt, x0 + 110, cy - 14, F_XB, 31, C_['ink'], c01(k * 1.4), 1, 'l')
    text(cv, sub, x0 + 110, cy + 28, F_M, 25, (90, 110, 140), c01(k * 1.4), 1, 'l')


def sH(cv, t):
    bubble(cv, 30, 50, 700, 150, 'Cơn đau nào trên cơ thể?', 'lưng · hông · thắt lưng…', t, 138.0, C_['coral'], 'l')
    bubble(cv, 270, 250, 710, 150, 'Câu hỏi về bài tập / giãn cơ?', 'cứ hỏi, em giải đáp', t, 139.8, C_['amber'], 'r')
    # ô comment
    if t > 143.0:
        k = pop(t, 143.0, .5)
        yy = 470
        rrect(cv, 30, yy, 950, yy + 110, 55, (22, 46, 78), C_['ice'], 4, c01(k * 1.4))
        circle(cv, (92, yy + 55), 32, C_['violet'])
        text(cv, 'B', 92, yy + 57, F_BLACK, 36, C_['white'])
        msg = 'Em bị đau lưng dưới, nên tập sao ạ?'
        n = int(len(msg) * eio(prog(t, 143.5, 145.2)))
        text(cv, msg[:n] + ('|' if int(t * 2.5) % 2 == 0 and t < 145.6 else ''), 140, yy + 56, F_M, 29, C_['chalk'], 1.0, 1.0, 'l')
        pill(cv, 'Gửi', 880, yy + 55, C_['ice'], C_['ink'], 28, 1.0, 1.0, 46, 56)
    if t > 145.4:
        k = pop(t, 145.5, .5)
        yy = 610
        rrect(cv, 130 + (1 - k) * 100, yy, 978, yy + 100, 50, (14, 64, 56), C_['mint'], 4, c01(k * 1.4))
        circle(cv, (190 + (1 - k) * 100, yy + 50), 32, C_['amber']); text(cv, 'V', 190 + (1 - k) * 100, yy + 52, F_BLACK, 36, C_['ink'], c01(k * 1.4))
        text(cv, 'HLV Vinh: Em sẽ hướng dẫn nhà mình!', 240 + (1 - k) * 100, yy + 52, F_B, 29, C_['white'], c01(k * 1.4), 1, 'l')
    return cv


SCENES = [  # (t0, t1, hàm)  — theo giây GỐC
    (0.0, 11.4, sA), (11.4, 27.7, sB), (27.7, 32.64, sC), (32.64, 47.43, sD), (47.43, 75.0, sE), (75.0, 85.7, sF),
    (85.7, 94.4, sG1), (94.4, 137.8, sG2), (137.8, 147.7, sH),
]
