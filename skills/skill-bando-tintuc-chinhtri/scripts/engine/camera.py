# -*- coding: utf-8 -*-
"""Camera 3D nhìn xuống mặt phẳng bản đồ Mercator (đơn vị [0,1], y xuống nam).

Trạng thái camera: x, y (đơn vị, điểm nhìn trên mặt đất), w (bề rộng mặt đất nhìn thấy tại điểm nhìn,
đơn vị), nghieng (độ, 0 = nhìn thẳng xuống), xoay (độ, 0 = bắc ở trên).
"""
import math

import numpy as np


def ease(p):
    p = max(0.0, min(1.0, p))
    return p * p * (3 - 2 * p)


def ease_in_out_cubic(p):
    p = max(0.0, min(1.0, p))
    return 4 * p ** 3 if p < 0.5 else 1 - (-2 * p + 2) ** 3 / 2


class TrangThai:
    __slots__ = ("x", "y", "w", "nghieng", "xoay")

    def __init__(self, x, y, w, nghieng=35.0, xoay=0.0):
        self.x, self.y, self.w, self.nghieng, self.xoay = float(x), float(y), float(w), float(nghieng), float(xoay)

    def copy(self):
        return TrangThai(self.x, self.y, self.w, self.nghieng, self.xoay)

    def __repr__(self):
        return "TrangThai(x=%.4f y=%.4f w=%.5f nghieng=%.1f xoay=%.1f)" % (
            self.x, self.y, self.w, self.nghieng, self.xoay)


def noi_suy(a, b, p, kieu="bay"):
    """Nội suy camera a->b. kieu 'vong' = bay vòng: phóng xa ra giữa chừng."""
    e = ease_in_out_cubic(p)
    dx = b.x - a.x
    if dx > 0.5:
        dx -= 1.0
    elif dx < -0.5:
        dx += 1.0
    x = (a.x + dx * e) % 1.0
    y = a.y + (b.y - a.y) * e
    lw = math.log(a.w) + (math.log(b.w) - math.log(a.w)) * e
    if kieu == "vong":
        xa = max(a.w, b.w)
        kc = math.hypot(dx, b.y - a.y)
        dinh = max(xa * 1.6, kc * 1.3)
        bump = math.sin(math.pi * p) ** 1.2
        lw = lw + (math.log(dinh) - lw) * bump * (1 if dinh > math.exp(lw) else 0)
    w = math.exp(lw)
    ng = a.nghieng + (b.nghieng - a.nghieng) * e
    xo = a.xoay + (b.xoay - a.xoay) * e
    return TrangThai(x, y, w, ng, xo)


class Camera:
    def __init__(self, W, H, hfov=38.0):
        self.W, self.H = W, H
        self.hfov = hfov
        self.fx = (W / 2.0) / math.tan(math.radians(hfov / 2))
        self.tt = None

    def dat(self, tt):
        self.tt = tt
        t = math.radians(tt.nghieng)
        h = math.radians(tt.xoay)
        self.d = tt.w / (2 * math.tan(math.radians(self.hfov / 2)))
        T = np.array([tt.x, -tt.y, 0.0])
        off = np.array([math.sin(h) * math.sin(t), -math.cos(h) * math.sin(t), math.cos(t)])
        self.C = T + self.d * off
        f = (T - self.C)
        f /= np.linalg.norm(f)
        up = np.array([0.0, 0.0, 1.0])
        r = np.cross(f, up)
        if np.linalg.norm(r) < 1e-9:
            r = np.array([math.cos(h), math.sin(h), 0.0])
        r /= np.linalg.norm(r)
        u = np.cross(r, f)
        self.f, self.r, self.u = f, r, u
        return self

    # ---- chiếu ----
    def chieu(self, pts):
        """pts: (N,2) đơn vị Mercator -> (N,3): sx, sy, zc (zc<=0 là sau camera)."""
        pts = np.asarray(pts, dtype=np.float64).reshape(-1, 2)
        P = np.stack([pts[:, 0], -pts[:, 1], np.zeros(len(pts))], 1)
        v = P - self.C
        xc = v @ self.r
        yc = v @ self.u
        zc = v @ self.f
        zs = np.where(zc > 1e-9, zc, 1e-9)
        sx = self.W / 2 + self.fx * xc / zs
        sy = self.H / 2 - self.fx * yc / zs
        return np.stack([sx, sy, zc], 1)

    def chieu_diem(self, x, y):
        s = self.chieu([[x, y]])[0]
        return float(s[0]), float(s[1]), float(s[2])

    def ti_le_tai(self, x, y):
        """px màn hình trên 1 đơn vị Mercator tại điểm (x,y) trên mặt đất."""
        s = self.chieu([[x, y]])[0]
        z = max(float(s[2]), 1e-6)
        return self.fx / z

    def bo_chieu(self, sx, sy, xa_nhat=None):
        """Điểm màn hình -> điểm mặt đất (đơn vị). Tia không chạm đất thì lấy điểm xa xa_nhat."""
        d = self.f + ((sx - self.W / 2) / self.fx) * self.r - ((sy - self.H / 2) / self.fx) * self.u
        if xa_nhat is None:
            xa_nhat = self.d * 6.0
        if d[2] < -1e-6:
            t = -self.C[2] / d[2]
            t = min(t, xa_nhat)
        else:
            t = xa_nhat
        P = self.C + d * t
        return float(P[0]), float(-P[1])

    def vung_dat(self, xa_nhat=None):
        """Hộp bao (x0,y0,x1,y1) đơn vị của phần mặt đất camera nhìn thấy."""
        pts = []
        for sx in (0, self.W / 2, self.W):
            for sy in (0, self.H / 2, self.H):
                pts.append(self.bo_chieu(sx, sy, xa_nhat))
        xs = [p[0] for p in pts]
        ys = [p[1] for p in pts]
        return min(xs), min(ys), max(xs), max(ys)

    def huong_man_hinh(self, x, y, dx, dy):
        """Góc (độ) trên màn hình của hướng (dx,dy) đơn vị tại điểm (x,y). 0 = sang phải, dương = xuống."""
        a = self.chieu([[x, y], [x + dx * 1e-3, y + dy * 1e-3]])
        return math.degrees(math.atan2(a[1, 1] - a[0, 1], a[1, 0] - a[0, 0]))
