# -*- coding: utf-8 -*-
"""ve.py — bộ vẽ tay (cv2 + PIL): nét phác có tiến độ vẽ, chữ có sprite, mũi tên, người que, cột sống…
Mọi màu là RGB (canvas RGB uint8)."""
import os, math
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
FONTS = os.path.abspath(os.path.join(HERE, '..', 'assets', 'fonts'))
W, H = 1080, 1920

COL = dict(ink=(11, 23, 40), ink2=(18, 36, 60), grid=(24, 44, 70), chalk=(242, 246, 250), coral=(255, 92, 96),
           mint=(48, 226, 168), amber=(255, 201, 64), ice=(112, 196, 255), violet=(170, 140, 255),
           dim=(110, 134, 165), white=(255, 255, 255), black=(0, 0, 0), bone=(238, 226, 200), disc=(255, 170, 70))


# ------------------------------------------------------------------ easing
def c01(x): return 0.0 if x < 0 else (1.0 if x > 1 else x)
def prog(t, a, b): return c01((t - a) / max(1e-6, (b - a)))
def eo(x): x = c01(x); return 1 - (1 - x) ** 3
def eio(x): x = c01(x); return 3 * x * x - 2 * x ** 3
def back(x):
    x = c01(x); c1 = 1.70158; c3 = c1 + 1
    return 1 + c3 * (x - 1) ** 3 + c1 * (x - 1) ** 2
def lerp(a, b, k): return a + (b - a) * k
def lerp2(a, b, k): return (a[0] + (b[0] - a[0]) * k, a[1] + (b[1] - a[1]) * k)
def mix(c1, c2, k): return tuple(int(lerp(c1[i], c2[i], k)) for i in range(3))


# ------------------------------------------------------------------ chữ
_fc = {}; _sc = {}
def font(name, size):
    k = (name, size)
    if k not in _fc:
        _fc[k] = ImageFont.truetype(os.path.join(FONTS, name), int(size))
    return _fc[k]

F_ANTON = 'Anton-Regular.ttf'; F_BLACK = 'BeVietnamPro-Black.ttf'; F_XB = 'BeVietnamPro-ExtraBold.ttf'
F_B = 'BeVietnamPro-Bold.ttf'; F_SB = 'BeVietnamPro-SemiBold.ttf'; F_M = 'BeVietnamPro-Medium.ttf'
F_HAND = 'Pacifico.ttf'; F_SCRIPT = 'DancingScript.ttf'


def sprite(text, fname=F_XB, size=60, fill=COL['chalk'], stroke=0, sfill=COL['ink'], ext=None, line_gap=1.12, align='center'):
    """Sprite RGBA (ndarray H,W,4). ext=(màu, độ sâu) -> chữ nổi khối 3D."""
    key = (text, fname, size, fill, stroke, sfill, ext, align)
    if key in _sc: return _sc[key]
    f = font(fname, size)
    lines = text.split('\n')
    asc = int(size * line_gap)
    d = (ext[1] if ext else 0)
    pad = stroke + d + 6
    wl = [f.getlength(l) for l in lines]
    w = int(max(wl)) + 2 * pad; h = asc * len(lines) + 2 * pad + int(size * .2)
    im = Image.new('RGBA', (w, h), (0, 0, 0, 0)); dr = ImageDraw.Draw(im)
    for i, l in enumerate(lines):
        x = pad + ((max(wl) - wl[i]) / 2 if align == 'center' else 0)
        y = pad + i * asc
        if ext:
            for k in range(d, 0, -1):
                dr.text((x + k * .7, y + k), l, font=f, fill=ext[0] + (255,), stroke_width=stroke, stroke_fill=ext[0] + (255,))
        dr.text((x, y), l, font=f, fill=fill + (255,), stroke_width=stroke, stroke_fill=sfill + (255,))
    a = np.array(im)
    _sc[key] = a
    return a


def blit(cv, spr, x, y, a=1.0, sc=1.0, anchor='c', rot=0.0):
    """Dán sprite RGBA (alpha) vào cv. (x,y) theo anchor c/l/r/t/b hoặc 'tl'."""
    if a <= 0.003 or sc <= 0.01: return
    s = spr
    if sc != 1.0 or rot:
        h0, w0 = s.shape[:2]
        if rot:
            M = cv2.getRotationMatrix2D((w0 / 2, h0 / 2), rot, sc)
            cs, sn = abs(M[0, 0]), abs(M[0, 1])
            nw = int(h0 * sn + w0 * cs); nh = int(h0 * cs + w0 * sn)
            M[0, 2] += nw / 2 - w0 / 2; M[1, 2] += nh / 2 - h0 / 2
            s = cv2.warpAffine(s, M, (nw, nh), flags=cv2.INTER_LINEAR, borderValue=(0, 0, 0, 0))
        else:
            s = cv2.resize(s, (max(1, int(w0 * sc)), max(1, int(h0 * sc))), interpolation=cv2.INTER_AREA if sc < 1 else cv2.INTER_LINEAR)
    h, w = s.shape[:2]
    ax = {'c': (.5, .5), 'l': (0, .5), 'r': (1, .5), 't': (.5, 0), 'b': (.5, 1), 'tl': (0, 0), 'tr': (1, 0), 'bl': (0, 1), 'br': (1, 1)}[anchor]
    x0 = int(round(x - w * ax[0])); y0 = int(round(y - h * ax[1]))
    X0 = max(0, x0); Y0 = max(0, y0); X1 = min(cv.shape[1], x0 + w); Y1 = min(cv.shape[0], y0 + h)
    if X1 <= X0 or Y1 <= Y0: return
    sub = s[Y0 - y0:Y1 - y0, X0 - x0:X1 - x0]
    al = (sub[:, :, 3:4].astype(np.float32) / 255.0) * a
    roi = cv[Y0:Y1, X0:X1]
    roi[:] = (roi * (1 - al) + sub[:, :, :3] * al).astype(np.uint8)


def text(cv, t, x, y, fname=F_XB, size=60, fill=COL['chalk'], a=1.0, sc=1.0, anchor='c', stroke=0, sfill=COL['ink'], ext=None, rot=0.0):
    blit(cv, sprite(t, fname, size, fill, stroke, sfill, ext), x, y, a, sc, anchor, rot)


# ------------------------------------------------------------------ hình cơ bản
def _p(pts): return np.round(np.asarray(pts, float) * 16).astype(np.int32)
def _r(v): return int(round(v * 16))


def line(cv, p0, p1, col, w=4, a=1.0):
    if a < 1:
        lay = cv.copy(); line(lay, p0, p1, col, w); cv[:] = cv2.addWeighted(lay, a, cv, 1 - a, 0); return
    cv2.line(cv, (_r(p0[0]), _r(p0[1])), (_r(p1[0]), _r(p1[1])), col, int(w), cv2.LINE_AA, 4)


def circle(cv, c, r, col, fill=True, w=3):
    cv2.circle(cv, (_r(c[0]), _r(c[1])), _r(r), col, -1 if fill else int(w), cv2.LINE_AA, 4)


def poly(cv, pts, col, fill=True, w=3):
    if fill: cv2.fillPoly(cv, [_p(pts)], col, cv2.LINE_AA, 4)
    else: cv2.polylines(cv, [_p(pts)], True, col, int(w), cv2.LINE_AA, 4)


def lay_alpha(cv, a, fn):
    """vẽ fn(layer) rồi trộn độ mờ a."""
    if a <= 0.003: return
    if a >= 0.997: fn(cv); return
    lay = cv.copy(); fn(lay); cv[:] = cv2.addWeighted(lay, a, cv, 1 - a, 0)


def rr_pts(x0, y0, x1, y1, r, n=8):
    r = min(r, (x1 - x0) / 2, (y1 - y0) / 2)
    pts = []
    for cx, cy, a0 in ((x1 - r, y0 + r, -90), (x1 - r, y1 - r, 0), (x0 + r, y1 - r, 90), (x0 + r, y0 + r, 180)):
        for i in range(n + 1):
            a = math.radians(a0 + 90 * i / n)
            pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts


def rrect(cv, x0, y0, x1, y1, r, fill=None, outline=None, w=3, a=1.0):
    pts = rr_pts(x0, y0, x1, y1, r)
    def f(c):
        if fill is not None: poly(c, pts, fill, True)
        if outline is not None: poly(c, pts, outline, False, w)
    lay_alpha(cv, a, f)


def glow(cv, c, r, col, a=0.5):
    """vầng sáng mềm (radial)."""
    x, y = int(c[0]), int(c[1]); R = int(r * 1.0)
    x0, y0, x1, y1 = max(0, x - R), max(0, y - R), min(cv.shape[1], x + R), min(cv.shape[0], y + R)
    if x1 <= x0 or y1 <= y0: return
    yy, xx = np.mgrid[y0:y1, x0:x1]
    d = np.sqrt((xx - c[0]) ** 2 + (yy - c[1]) ** 2) / max(r, 1)
    k = np.clip(1 - d, 0, 1) ** 2 * a
    roi = cv[y0:y1, x0:x1].astype(np.float32)
    roi += (np.array(col, np.float32) - roi) * k[..., None]
    cv[y0:y1, x0:x1] = np.clip(roi, 0, 255).astype(np.uint8)


# ------------------------------------------------------------------ đường cong
def catmull(pts, n=10):
    P = [np.array(p, float) for p in pts]
    P = [P[0]] + P + [P[-1]]
    out = []
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
        for k in range(n):
            t = k / n
            out.append(0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t * t + (-p0 + 3 * p1 - 3 * p2 + p3) * t ** 3))
    out.append(P[-2])
    return np.array(out)


def bez3(p0, p1, p2, p3, n=36):
    t = np.linspace(0, 1, n)[:, None]
    p0, p1, p2, p3 = [np.array(p, float) for p in (p0, p1, p2, p3)]
    return (1 - t) ** 3 * p0 + 3 * (1 - t) ** 2 * t * p1 + 3 * (1 - t) * t * t * p2 + t ** 3 * p3


def bez2(p0, p1, p2, n=30):
    t = np.linspace(0, 1, n)[:, None]
    p0, p1, p2 = [np.array(p, float) for p in (p0, p1, p2)]
    return (1 - t) ** 2 * p0 + 2 * (1 - t) * t * p1 + t * t * p2


def arc_pts(c, r, a0, a1, n=30):
    return np.array([(c[0] + r * math.cos(math.radians(a)), c[1] + r * math.sin(math.radians(a))) for a in np.linspace(a0, a1, n)])


def _cum(p):
    d = np.sqrt(((p[1:] - p[:-1]) ** 2).sum(1)); return np.concatenate([[0], np.cumsum(d)])


def partial(pts, f):
    p = np.asarray(pts, float)
    if f >= 0.999 or len(p) < 2: return p
    if f <= 0: return p[:1]
    c = _cum(p); L = c[-1] * f
    i = int(np.searchsorted(c, L)); i = min(max(i, 1), len(p) - 1)
    seg = c[i] - c[i - 1]; k = (L - c[i - 1]) / seg if seg > 0 else 0
    return np.vstack([p[:i], p[i - 1] + (p[i] - p[i - 1]) * k])


def wob(pts, seed, amp=1.6):
    """nét phác: rung nhẹ cố định theo seed (không nhảy theo thời gian)."""
    p = np.asarray(pts, float)
    if amp <= 0: return p
    rs = np.random.RandomState(seed)
    n = np.cumsum(rs.randn(len(p), 2), 0)
    n = n - np.linspace(n[0], n[-1], len(p))
    n = n / (np.abs(n).max() + 1e-6) * amp
    return p + n


def stroke(cv, pts, col, w=6, f=1.0, seed=1, amp=1.4, cap=True, a=1.0, out=None):
    """vẽ 1 nét với tiến độ f (0..1) — cảm giác tay đang vẽ. out=(màu,độ dày thêm) viền tối."""
    p = wob(pts, seed, amp) if amp else np.asarray(pts, float)
    q = partial(p, f)
    if len(q) < 2: return
    def d(c):
        if out:
            cv2.polylines(c, [_p(q)], False, out[0], int(w + out[1]), cv2.LINE_AA, 4)
            if cap: circle(c, q[0], (w + out[1]) / 2, out[0]); circle(c, q[-1], (w + out[1]) / 2, out[0])
        cv2.polylines(c, [_p(q)], False, col, int(w), cv2.LINE_AA, 4)
        if cap and w > 3: circle(c, q[0], w / 2, col); circle(c, q[-1], w / 2, col)
    lay_alpha(cv, a, d)
    return q[-1]


def dashed(cv, pts, col, w=4, f=1.0, dash=16, gap=12, a=1.0):
    p = partial(np.asarray(pts, float), f)
    if len(p) < 2: return
    c = _cum(p); L = c[-1]; s = 0.0
    def d(cc):
        t = 0.0
        while t < L:
            t2 = min(L, t + dash)
            i0 = np.searchsorted(c, t); i1 = np.searchsorted(c, t2)
            seg = [np.interp(t, c, p[:, 0]), np.interp(t, c, p[:, 1])]
            pp = [seg] + [p[i] for i in range(i0, i1)] + [[np.interp(t2, c, p[:, 0]), np.interp(t2, c, p[:, 1])]]
            cv2.polylines(cc, [_p(pp)], False, col, int(w), cv2.LINE_AA, 4)
            t += dash + gap
    lay_alpha(cv, a, d)


def arrow(cv, p0, p1, col, w=6, f=1.0, head=26, seed=3, amp=0.8, curve=0.0, a=1.0):
    p0 = np.array(p0, float); p1 = np.array(p1, float)
    v = p1 - p0; L = np.linalg.norm(v) + 1e-6; n = np.array([-v[1], v[0]]) / L
    if curve: path = bez2(p0, (p0 + p1) / 2 + n * curve * L, p1, 28)
    else: path = np.array([p0 + (p1 - p0) * k for k in np.linspace(0, 1, 30)])
    body = partial(path, min(1, f))
    stroke(cv, path[:-1] if False else path, col, w, min(1, f) * 0.92 if f >= 1 else f, seed, amp, a=a)
    if f >= 0.92:
        k = eo((f - 0.92) / 0.08)
        d = path[-1] - path[-4]; d = d / (np.linalg.norm(d) + 1e-6); nn = np.array([-d[1], d[0]])
        tip = path[-1] + d * head * 0.2
        h = head * k
        lay_alpha(cv, a, lambda c: poly(c, [tip, tip - d * h + nn * h * .55, tip - d * h - nn * h * .55], col, True))


def check(cv, c, s, col, f=1.0, w=9):
    pts = [(c[0] - s * .55, c[1] + s * .0), (c[0] - s * .15, c[1] + s * .45), (c[0] + s * .6, c[1] - s * .5)]
    stroke(cv, catmull(pts, 8) if False else np.array(pts), col, w, f, seed=5, amp=0.4)


def cross(cv, c, s, col, f=1.0, w=9):
    stroke(cv, [(c[0] - s * .5, c[1] - s * .5), (c[0] + s * .5, c[1] + s * .5)], col, w, min(1, f * 2), 7, .3)
    if f > .5: stroke(cv, [(c[0] + s * .5, c[1] - s * .5), (c[0] - s * .5, c[1] + s * .5)], col, w, min(1, (f - .5) * 2), 8, .3)


# ------------------------------------------------------------------ cửa sổ bo góc (dán video)
_mask = {}
def rmask(w, h, r):
    k = (w, h, r)
    if k not in _mask:
        S = 4
        m = np.zeros((h * S, w * S), np.uint8)
        cv2.fillPoly(m, [np.round(np.array(rr_pts(0, 0, w * S - 1, h * S - 1, r * S, 10))).astype(np.int32)], 255, cv2.LINE_AA)
        _mask[k] = cv2.resize(m, (w, h), interpolation=cv2.INTER_AREA).astype(np.float32)[..., None] / 255.0
    return _mask[k]


def paste_round(cv, img, x, y, r=40, a=1.0):
    h, w = img.shape[:2]
    X0 = max(0, x); Y0 = max(0, y); X1 = min(cv.shape[1], x + w); Y1 = min(cv.shape[0], y + h)
    if X1 <= X0 or Y1 <= Y0: return
    m = rmask(w, h, r)[Y0 - y:Y1 - y, X0 - x:X1 - x] * a
    roi = cv[Y0:Y1, X0:X1]
    roi[:] = (roi * (1 - m) + img[Y0 - y:Y1 - y, X0 - x:X1 - x] * m).astype(np.uint8)


_bc = {}
def badge(txt, fill, tcol=COL['ink'], size=50, fname=F_BLACK, padx=30, pady=16):
    """tem chữ bo tròn (RGBA)."""
    k = (txt, fill, tcol, size, fname)
    if k in _bc: return _bc[k]
    f = font(fname, size); w = int(f.getlength(txt)) + padx * 2; h = int(size * 1.25) + pady
    im = Image.new('RGBA', (w + 16, h + 16), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((12, 12, w + 8, h + 8), radius=h // 2 - 4, fill=(8, 14, 26, 120))
    d.rounded_rectangle((8, 6, w + 4, h + 2), radius=h // 2 - 4, fill=fill + (255,))
    d.text(((w + 12) / 2, (h + 8) / 2 + 1), txt, font=f, fill=tcol + (255,), anchor='mm')
    a = np.array(im); _bc[k] = a
    return a
