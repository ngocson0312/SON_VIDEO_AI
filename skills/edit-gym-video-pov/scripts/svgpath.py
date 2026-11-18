# -*- coding: utf-8 -*-
"""Doc thuoc tinh d cua SVG path -> matplotlib Path (cung -> bezier bac 3), ve mask fill nonzero."""
import math, re
import numpy as np
from matplotlib.path import Path

TOK = re.compile(r"[MmLlHhVvCcSsQqTtAaZz]|[-+]?(?:\d*\.\d+|\d+\.?)(?:[eE][-+]?\d+)?")


def _arc(x1, y1, rx, ry, phi, fa, fs, x2, y2):
    """SVG F.6.5 -> list cubic segments [(c1, c2, p)]"""
    if rx == 0 or ry == 0:
        return [((x1, y1), (x2, y2), (x2, y2))]
    rx, ry = abs(rx), abs(ry)
    cp, sp = math.cos(math.radians(phi)), math.sin(math.radians(phi))
    dx, dy = (x1 - x2) / 2, (y1 - y2) / 2
    x1p, y1p = cp * dx + sp * dy, -sp * dx + cp * dy
    lam = x1p ** 2 / rx ** 2 + y1p ** 2 / ry ** 2
    if lam > 1:
        rx, ry = rx * math.sqrt(lam), ry * math.sqrt(lam)
    num = rx * rx * ry * ry - rx * rx * y1p * y1p - ry * ry * x1p * x1p
    den = rx * rx * y1p * y1p + ry * ry * x1p * x1p
    co = math.sqrt(max(0.0, num / den)) if den else 0.0
    if fa == fs:
        co = -co
    cxp, cyp = co * rx * y1p / ry, -co * ry * x1p / rx
    cx = cp * cxp - sp * cyp + (x1 + x2) / 2
    cy = sp * cxp + cp * cyp + (y1 + y2) / 2

    def ang(ux, uy, vx, vy):
        a = math.atan2(ux * vy - uy * vx, ux * vx + uy * vy)
        return a
    t1 = ang(1, 0, (x1p - cxp) / rx, (y1p - cyp) / ry)
    dt = ang((x1p - cxp) / rx, (y1p - cyp) / ry, (-x1p - cxp) / rx, (-y1p - cyp) / ry)
    if not fs and dt > 0:
        dt -= 2 * math.pi
    elif fs and dt < 0:
        dt += 2 * math.pi
    n = max(1, int(math.ceil(abs(dt) / (math.pi / 2))))
    d = dt / n
    k = 4 / 3 * math.tan(d / 4)
    out = []

    def pt(t):
        return (cx + rx * math.cos(t) * cp - ry * math.sin(t) * sp, cy + rx * math.cos(t) * sp + ry * math.sin(t) * cp)

    def dpt(t):
        return (-rx * math.sin(t) * cp - ry * math.cos(t) * sp, -rx * math.sin(t) * sp + ry * math.cos(t) * cp)
    t = t1
    for _ in range(n):
        p0, p3 = pt(t), pt(t + d)
        d0, d3 = dpt(t), dpt(t + d)
        out.append(((p0[0] + k * d0[0], p0[1] + k * d0[1]), (p3[0] - k * d3[0], p3[1] - k * d3[1]), p3))
        t += d
    return out


def parse(d):
    toks = TOK.findall(d)
    verts, codes = [], []
    i = 0
    cmd = None
    x = y = sx = sy = 0.0
    lc = None  # last control (for S/T)
    lcmd = None

    def num():
        nonlocal i
        v = float(toks[i]); i += 1
        return v

    def flag():
        # co (flag) trong 'a' co the dinh lien: "00.744" -> 0, 0, .744
        nonlocal i
        t = toks[i]
        if t[0] in "01" and len(t) > 1 and t[1] != ".":
            toks[i] = t[1:]
            return int(t[0])
        if t.startswith("0.") or t.startswith("1."):
            toks[i] = t[1:]
            return int(t[0])
        i += 1
        return int(float(t))
    while i < len(toks):
        t = toks[i]
        if re.match(r"[A-Za-z]", t):
            cmd = t; i += 1
            if cmd in "Zz":
                codes.append(Path.CLOSEPOLY); verts.append((sx, sy))
                x, y = sx, sy
                lcmd = cmd
                continue
        rel = cmd.islower()
        C = cmd.upper()
        ox, oy = (x, y) if rel else (0.0, 0.0)
        if C == "M":
            x, y = ox + num(), oy + num()
            sx, sy = x, y
            verts.append((x, y)); codes.append(Path.MOVETO)
            cmd = "l" if rel else "L"
            lc = None
        elif C == "L":
            x, y = ox + num(), oy + num()
            verts.append((x, y)); codes.append(Path.LINETO); lc = None
        elif C == "H":
            x = ox + num() if rel else num()
            verts.append((x, y)); codes.append(Path.LINETO); lc = None
        elif C == "V":
            y = (y + num()) if rel else num()
            verts.append((x, y)); codes.append(Path.LINETO); lc = None
        elif C == "C":
            c1 = (ox + num(), oy + num()); c2 = (ox + num(), oy + num()); p = (ox + num(), oy + num())
            verts += [c1, c2, p]; codes += [Path.CURVE4] * 3
            lc = c2; x, y = p
        elif C == "S":
            c1 = (2 * x - lc[0], 2 * y - lc[1]) if (lc and lcmd and lcmd.upper() in "CS") else (x, y)
            c2 = (ox + num(), oy + num()); p = (ox + num(), oy + num())
            verts += [c1, c2, p]; codes += [Path.CURVE4] * 3
            lc = c2; x, y = p
        elif C == "Q":
            c1 = (ox + num(), oy + num()); p = (ox + num(), oy + num())
            verts += [c1, p]; codes += [Path.CURVE3] * 2
            lc = c1; x, y = p
        elif C == "T":
            c1 = (2 * x - lc[0], 2 * y - lc[1]) if (lc and lcmd and lcmd.upper() in "QT") else (x, y)
            p = (ox + num(), oy + num())
            verts += [c1, p]; codes += [Path.CURVE3] * 2
            lc = c1; x, y = p
        elif C == "A":
            rx, ry, phi = num(), num(), num()
            fa = flag(); fs = flag()
            p = (ox + num(), oy + num())
            for c1, c2, q in _arc(x, y, rx, ry, phi, fa, fs, p[0], p[1]):
                verts += [c1, c2, q]; codes += [Path.CURVE4] * 3
            x, y = p; lc = None
        lcmd = cmd
    return Path(np.array(verts), codes)


def mask(d, viewbox, size):
    """Mask L (PIL) size x size, fill trang nonzero."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import PathPatch
    from PIL import Image
    vx, vy, vw, vh = viewbox
    fig = plt.figure(figsize=(1, 1), dpi=size)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(vx, vx + vw); ax.set_ylim(vy + vh, vy)
    ax.axis("off")
    fig.patch.set_facecolor("black")
    ax.add_patch(PathPatch(parse(d), facecolor="white", edgecolor="none", antialiased=True))
    fig.canvas.draw()
    a = np.asarray(fig.canvas.buffer_rgba())[..., 0].copy()
    plt.close(fig)
    return Image.fromarray(a, "L")
