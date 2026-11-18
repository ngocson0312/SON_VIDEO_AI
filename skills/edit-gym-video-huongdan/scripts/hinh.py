# -*- coding: utf-8 -*-
"""hinh.py — hình minh hoạ giải phẫu / người que vẽ tay (cột sống, xương chậu, cơ gập hông, tư thế nằm / quỳ)."""
import math
import numpy as np, cv2
from ve import *
from ve import _cum, _r


# ------------------------------------------------------------------ nền bảng (giấy ô li tối)
def board_bg(w, h, t=0.0):
    img = np.empty((h, w, 3), np.uint8)
    top = np.array(COL['ink2'], np.float32); bot = np.array(COL['ink'], np.float32)
    k = np.linspace(0, 1, h, dtype=np.float32)[:, None, None]
    img[:] = (top * (1 - k) + bot * k).astype(np.uint8)
    g = COL['grid']
    for x in range(0, w, 54): cv2.line(img, (x, 0), (x, h), g, 1)
    for y in range(0, h, 54): cv2.line(img, (0, y), (w, y), g, 1)
    return img


# ------------------------------------------------------------------ cột sống nhìn nghiêng (mặt trước = bên phải)
_BASE = [(0.00, .02), (0.05, .045), (0.10, .04), (0.17, .0), (0.25, -.04), (0.34, -.065), (0.43, -.07), (0.50, -.05),
         (0.57, -.01), (0.64, .03), (0.71, .055), (0.78, .045), (0.84, .0), (0.90, -.045), (0.96, -.08)]


def spine_curve(ox, oy, hg, lord=1.0):
    pts = []
    for s, dx in _BASE:
        k = lord if 0.6 <= s <= 0.82 else (1 + (lord - 1) * 0.5 if 0.5 < s < 0.9 else 1)
        d = dx * (k if s >= 0.57 and s <= 0.84 else 1)
        # lord lớn làm cung thắt lưng cong ra trước + kéo thân trên về sau
        if s > 0.5: d += (lord - 1) * 0.05 * math.sin(math.pi * (s - 0.5) / 0.5)
        if s < 0.5: d -= (lord - 1) * 0.025 * (1 - s / 0.5)
        pts.append((ox + d * hg, oy + s * hg))
    return catmull(pts, 12)


def spine(cv, ox, oy, hg, lord=1.0, f=1.0, hl=0.0, pulse=0.0, lab=True, tilt=None):
    """ox,oy = đỉnh; hg = chiều cao. hl = mức tô sáng vùng thắt lưng (0..1). tilt = độ nghiêng xương chậu (độ)."""
    C = spine_curve(ox, oy, hg, lord)
    cum = _cum(C); L = cum[-1]
    nver = 24
    sc = hg / 640.0
    # vùng thắt lưng ~ đốt 13..17
    for i in range(nver):
        u = (i + .5) / nver
        if u > f: break
        a = prog(f, u, u + 0.05)
        d = u * L
        k = int(np.searchsorted(cum, d)); k = min(max(k, 1), len(C) - 1)
        p = C[k]; tg = C[min(k + 2, len(C) - 1)] - C[max(k - 2, 0)]; tg = tg / (np.linalg.norm(tg) + 1e-6)
        nm = np.array([tg[1], -tg[0]])        # hướng ra trước (phải)
        if nm[0] < 0: nm = -nm
        size = (16 + 26 * u) * sc * 1.15
        wv = size * 1.25; hv = size * .72
        lum = 0.52 <= u <= 0.80
        col = COL['bone']
        if lum and hl > 0: col = mix(COL['bone'], COL['coral'], 0.75 * hl * (0.75 + 0.25 * math.sin(pulse * 6.0 + i)))
        cb = p + nm * wv * .12
        pts = [cb - tg * hv / 2 - nm * wv / 2, cb - tg * hv / 2 + nm * wv / 2, cb + tg * hv / 2 + nm * wv / 2, cb + tg * hv / 2 - nm * wv / 2]
        # đốt thân
        rp = rr_poly(pts)
        lay_alpha(cv, a, lambda c: (poly(c, rp, COL['ink'], True), poly(c, shrink(rp, p, .88), col, True)))
        # gai sau
        sp0 = cb - nm * wv * .5; sp1 = sp0 - nm * wv * .42 + tg * hv * .45
        lay_alpha(cv, a, lambda c: (line(c, sp0, sp1, COL['ink'], int(9 * sc * 1.2) + 2), line(c, sp0, sp1, col, max(2, int(5.5 * sc * 1.2)))))
        # đĩa đệm
        if i < nver - 1:
            dc = cb + tg * (hv / 2 + 2.2 * sc)
            dcol = COL['disc'] if (lum and hl > 0) else (150, 200, 235)
            lay_alpha(cv, a * 0.95, lambda c: cv2.ellipse(c, (_r(dc[0]), _r(dc[1])), (_r(wv * .46), _r(2.6 * sc * 1.2 + 1)), math.degrees(math.atan2(tg[0], -tg[1])) + 0 if False else 0, 0, 360, dcol, -1, cv2.LINE_AA, 4))
    # xương chậu + xương đùi
    if f > 0.86:
        a = prog(f, .86, 1.0)
        pelvis(cv, C[-1], hg, tilt if tilt is not None else (lord - 1) * 14, a, hl, pulse)
    return C


def rr_poly(pts):
    pts = [np.array(p, float) for p in pts]; out = []
    for i in range(4):
        a = pts[i]; b = pts[(i + 1) % 4]; c = pts[(i - 1) % 4]
        out += [a + (c - a) * .22, a + (b - a) * .22]
    return out


def shrink(pts, c, k):
    return [np.array(c) * 0 + (np.mean(pts, 0) + (np.array(p) - np.mean(pts, 0)) * k) for p in pts]


def pelvis(cv, base, hg, tilt_deg, a=1.0, hl=0.0, pulse=0.0):
    """vẽ xương chậu quanh điểm cuối cột sống (base). tilt_deg>0: nghiêng ra trước."""
    s = hg / 640.0 * 0.62
    ang = math.radians(tilt_deg)
    def R(p):
        x, y = p; return (base[0] + (x * math.cos(ang) - y * math.sin(ang)) * s, base[1] + (x * math.sin(ang) + y * math.cos(ang)) * s)
    ilium = [(-30, -20), (10, -46), (58, -34), (92, -6), (100, 40), (84, 86), (46, 112), (6, 104), (-22, 70), (-34, 20)]
    P = [R(p) for p in ilium]
    hip = R((62, 98))
    fem = [hip, (hip[0] + 8 * s, hip[1] + 120 * s), (hip[0] + 16 * s, hip[1] + 250 * s)]
    def d(c):
        stroke(c, fem, COL['ink'], 44 * s, 1, 1, 0, out=None)
        stroke(c, fem, COL['bone'], 32 * s, 1, 1, 0)
        poly(c, P, COL['ink'], True)
        poly(c, shrink(P, base, .94), COL['bone'], True)
        circle(c, hip, 26 * s, COL['ink']); circle(c, hip, 20 * s, (250, 244, 230))
        # lỗ bịt
        circle(c, R((38, 60)), 13 * s, COL['ink2'])
    lay_alpha(cv, a, d)
    return hip


def psoas_path(base, hg, tilt_deg):
    """đường cơ gập hông từ mặt trước thắt lưng xuống mấu chuyển nhỏ xương đùi."""
    s = hg / 640.0; ang = math.radians(tilt_deg)
    def R(p):
        x, y = p; return (base[0] + (x * math.cos(ang) - y * math.sin(ang)) * s, base[1] + (x * math.sin(ang) + y * math.cos(ang)) * s)
    top = (base[0] + 52 * s, base[1] - 190 * s)
    return np.array(bez3(top, (top[0] + 40 * s, top[1] + 80 * s), R((98, 20)), R((78, 150)), 40))


# ------------------------------------------------------------------ người que
def _box(P, box):
    x0, y0, w, h = box
    return {k: (x0 + v[0] * w, y0 + v[1] * h) for k, v in P.items()}


def blend_pose(A, B, k):
    return {n: lerp2(A[n], B[n], k) for n in A}


FLOOR_Y = 0.88
LY_BASE = dict(head=(.075, .77), neck=(.13, .815), sh=(.19, .83), hip=(.52, .83), el=(.30, .86), wr=(.40, .86))
LY = {
    'bent': dict(LY_BASE, kn=(.66, .50), an=(.79, .83), kn2=(.68, .52), an2=(.80, .83)),
    'lift': dict(LY_BASE, kn=(.60, .50), an=(.80, .52), kn2=(.68, .52), an2=(.80, .83)),
    'ext':  dict(LY_BASE, kn=(.74, .68), an=(.95, .80), kn2=(.68, .52), an2=(.80, .83)),
}
KN_BASE = dict(el=(.30, .42), wr=(.40, .58))
KN = {
    'up':    dict(head=(.40, .085), neck=(.40, .15), sh=(.40, .19), hip=(.38, .58), kn=(.66, .64), an=(.66, .90), ft=(.78, .915),
                  kb=(.37, .90), ab=(.10, .90), el=(.33, .40), wr=(.38, .56)),
    'shift': dict(head=(.49, .11), neck=(.49, .17), sh=(.49, .21), hip=(.48, .59), kn=(.72, .64), an=(.66, .90), ft=(.78, .915),
                  kb=(.44, .90), ab=(.16, .90), el=(.42, .42), wr=(.48, .57)),
    'arch':  dict(head=(.34, .115), neck=(.375, .17), sh=(.39, .21), hip=(.50, .59), kn=(.74, .64), an=(.66, .90), ft=(.78, .915),
                  kb=(.46, .90), ab=(.18, .90), el=(.31, .40), wr=(.50, .56)),
}


def limb(cv, pts, col, w, f=1.0, seed=1):
    stroke(cv, pts, col, w, f, seed, 0.0, out=(COL['ink'], 9))


def lying(cv, box, pose, arch=0.0, f=1.0, col=COL['chalk'], far=COL['dim'], w=None, gap_col=None, head_r=None):
    """Người que nằm ngửa nhìn nghiêng. pose: dict toạ độ chuẩn hoá. arch>0: thắt lưng võng (hở khỏi sàn)."""
    P = _box(pose, box); s = box[2] / 900.0; w = w or 17 * s * 1.1
    fy = box[1] + FLOOR_Y * box[3]
    # sàn
    stroke(cv, [(box[0], fy), (box[0] + box[2], fy)], COL['dim'], 5, 1, 4, 1.0)
    # khe hở lưng-sàn
    hip = np.array(P['hip']); sh = np.array(P['sh'])
    if arch > 0:
        gp = bez3(sh + (30 * s, 0), (sh[0] + (hip[0] - sh[0]) * .35, hip[1] - arch * .2), (hip[0] - (hip[0] - sh[0]) * .30, hip[1] - arch), hip - (20 * s, 0), 30)
        floor_pts = np.vstack([gp, [[gp[-1][0], fy - 9], [gp[0][0], fy - 9]]])
        gc = gap_col or COL['coral']
        lay_alpha(cv, 0.28, lambda c: poly(c, floor_pts, gc, True))
    # chân xa
    limb(cv, [P['hip'], P['kn2'], P['an2']], far, w * .95, f, 11)
    # thân
    if arch > 0:
        tors = bez3(sh, (sh[0] + (hip[0] - sh[0]) * .35, sh[1] - arch * .12), (hip[0] - (hip[0] - sh[0]) * .30, hip[1] - arch), hip, 36)
    else:
        tors = np.array([sh, hip])
    limb(cv, tors, col, w * 1.7, f, 12)
    # chân gần
    limb(cv, [P['hip'], P['kn'], P['an']], col, w, f, 13)
    # bàn chân
    an = np.array(P['an']); kn = np.array(P['kn'])
    d = an - kn; d = d / (np.linalg.norm(d) + 1e-6)
    ft = an + np.array([abs(d[1]) * 26 * s + 6 * s, 0]) if abs(d[0]) < 0.8 else an + d * 24 * s
    limb(cv, [an, ft], col, w * .85, f, 14)
    # tay
    limb(cv, [P['sh'], P['el'], P['wr']], col, w * .8, f, 15)
    # đầu
    hr = head_r or 32 * s * 1.15
    circle(cv, P['head'], hr + 5, COL['ink']); circle(cv, P['head'], hr, col)
    line(cv, (P['neck'][0] - 4 * s, P['neck'][1]), P['sh'], COL['ink'], int(w * 1.4)); limb(cv, [P['neck'], P['sh']], col, w * 1.1, 1, 16)
    return P


def kneeling(cv, box, pose, f=1.0, col=COL['chalk'], far=COL['dim'], w=None, torso_arch=0.0, head_r=None):
    """Người que quỳ 1 gối (tư thế xuất kích) nhìn nghiêng, mặt quay sang phải."""
    P = _box(pose, box); s = box[2] / 800.0; w = w or 17 * s * 1.1
    fy = box[1] + 0.925 * box[3]
    stroke(cv, [(box[0], fy), (box[0] + box[2], fy)], COL['dim'], 5, 1, 4, 1.0)
    # chân sau (xa) = gối sau trên sàn
    limb(cv, [P['hip'], P['kb'], P['ab']], far, w * .98, f, 21)
    # thân
    sh = np.array(P['sh']); hip = np.array(P['hip'])
    if torso_arch:
        tors = bez3(sh, (sh[0] - torso_arch * .15, sh[1] + (hip[1] - sh[1]) * .35), (hip[0] + torso_arch, hip[1] - (hip[1] - sh[1]) * .30), hip, 36)
    else:
        tors = np.array([sh, hip])
    limb(cv, tors, col, w * 1.3, f, 22)
    # chân trước
    limb(cv, [P['hip'], P['kn'], P['an'], P['ft']], col, w, f, 23)
    # tay
    limb(cv, [P['sh'], P['el'], P['wr']], col, w * .8, f, 24)
    hr = head_r or 34 * s * 1.15
    circle(cv, P['head'], hr + 5, COL['ink']); circle(cv, P['head'], hr, col)
    limb(cv, [P['neck'], P['sh']], col, w * 1.1, 1, 25)
    return P


def person_icon(cv, c, size, col=COL['chalk'], kind='ly', w=None):
    """icon nhỏ cho thẻ (nằm / quỳ)."""
    box = (c[0] - size / 2, c[1] - size * .4, size, size * .8)
    if kind == 'ly':
        lying(cv, (c[0] - size / 2, c[1] - size * .35, size, size * .5), LY['lift'], 0, 1, col, COL['dim'], size * .028)
    else:
        kneeling(cv, (c[0] - size / 2, c[1] - size * .45, size, size * .9), KN['up'], 1, col, COL['dim'], size * .028)
