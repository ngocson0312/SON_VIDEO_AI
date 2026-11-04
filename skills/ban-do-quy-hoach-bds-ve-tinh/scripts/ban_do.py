# -*- coding: utf-8 -*-
"""Nền vệ tinh dựng bằng code: ô ảnh Esri World Imagery (cache đĩa + RAM), camera 2D hướng Bắc có zoom lẻ,
đường bay dọc tuyến, chiếu kinh vĩ → màn hình, vẽ tuyến / hành lang / vùng / ghim / thước đo.

Ghi nguồn bắt buộc trên video: "Ảnh: Esri World Imagery · Dữ liệu: © OpenStreetMap" (chung.CREDIT).
"""
import math
import os
import threading
import time
from collections import OrderedDict
from concurrent.futures import ThreadPoolExecutor

import cv2
import numpy as np
import requests
from PIL import Image

import chung as C
from chung import W, H, TS

TILE_URL = "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"
Z_MAX = 18
MAU_TRONG = (14, 22, 34)
CREDIT = "Ảnh: Esri World Imagery · Dữ liệu: © OpenStreetMap"


class Nen:
    """ô ảnh vệ tinh: cache đĩa ~/.cache/…/esri_imagery/z/x/y.jpg + LRU RAM; thiếu ô ⇒ phóng ô mức dưới"""

    def __init__(self, mang=True):
        self.dir = C.cache_dir("esri_imagery")
        self.mang = mang
        self.lru = OrderedDict()
        self.lock = threading.Lock()
        self.thieu = set()

    def duong_dan(self, z, x, y):
        return os.path.join(self.dir, str(z), str(x), "%d.jpg" % y)

    def tai_o(self, z, x, y):
        p = self.duong_dan(z, x, y)
        if os.path.isfile(p) and os.path.getsize(p) > 200:
            return True
        if not self.mang:
            return False
        os.makedirs(os.path.dirname(p), exist_ok=True)
        for k in range(4):
            try:
                r = requests.get(TILE_URL.format(z=z, x=x, y=y), headers=C.UA, timeout=25)
                if r.status_code == 200 and len(r.content) > 200 and r.headers.get("content-type", "").startswith("image"):
                    tmp = p + ".part"
                    with open(tmp, "wb") as f:
                        f.write(r.content)
                    os.replace(tmp, p)
                    return True
                if r.status_code == 404:
                    return False
            except Exception:
                pass
            time.sleep(0.8 * (k + 1))
        return False

    def lay_o(self, z, x, y):
        n = 1 << z
        if y < 0 or y >= n:
            return None
        x %= n
        k = (z, x, y)
        with self.lock:
            if k in self.lru:
                self.lru.move_to_end(k)
                return self.lru[k]
        img = None
        if self.tai_o(z, x, y):
            img = cv2.imread(self.duong_dan(z, x, y), cv2.IMREAD_COLOR)
            if img is not None:
                img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        if img is None and z > 0:
            cha = self.lay_o(z - 1, x // 2, y // 2)
            if cha is not None:
                ox, oy = (x % 2) * (TS // 2), (y % 2) * (TS // 2)
                img = cv2.resize(cha[oy:oy + TS // 2, ox:ox + TS // 2], (TS, TS), interpolation=cv2.INTER_LINEAR)
            self.thieu.add(k)
        if img is None:
            img = np.full((TS, TS, 3), MAU_TRONG, np.uint8)
        with self.lock:
            self.lru[k] = img
            if len(self.lru) > 1200:
                self.lru.popitem(last=False)
        return img

    def ghep(self, z, x0, y0, x1, y1):
        """vùng điểm ảnh thế giới [x0,x1)×[y0,y1) ở mức z → RGB"""
        x0, y0, x1, y1 = int(x0), int(y0), int(x1), int(y1)
        w, h = x1 - x0, y1 - y0
        out = np.full((h, w, 3), MAU_TRONG, np.uint8)
        for ty in range(y0 // TS, (y1 - 1) // TS + 1):
            for tx in range(x0 // TS, (x1 - 1) // TS + 1):
                im = self.lay_o(z, tx, ty)
                if im is None:
                    continue
                px, py = tx * TS - x0, ty * TS - y0
                sx0, sy0 = max(0, -px), max(0, -py)
                sx1, sy1 = min(TS, w - px), min(TS, h - py)
                if sx1 <= sx0 or sy1 <= sy0:
                    continue
                out[py + sy0:py + sy1, px + sx0:px + sx1] = im[sy0:sy1, sx0:sx1]
        return out

    def o_can(self, z, x0, y0, x1, y1):
        n = 1 << z
        ks = set()
        for ty in range(int(y0) // TS, (int(y1) - 1) // TS + 1):
            if 0 <= ty < n:
                for tx in range(int(x0) // TS, (int(x1) - 1) // TS + 1):
                    ks.add((z, tx % n, ty))
        return ks

    def tai_truoc(self, keys, luong=8):
        thieu = [k for k in keys if not os.path.isfile(self.duong_dan(*k))]
        if not thieu:
            return 0, 0
        loi = 0
        with ThreadPoolExecutor(max_workers=luong) as ex:
            for okk in ex.map(lambda k: self.tai_o(*k), thieu):
                if not okk:
                    loi += 1
        return len(thieu), loi


# ---------------------------------------------------------------- camera 2D hướng Bắc

class Camera:
    """tâm (lat, lon) + zoom lẻ zf. Ảnh lấy ở mức nguyên z = ceil(zf) (≤ Z_MAX) rồi thu nhỏ — nét hơn phóng to."""

    def __init__(self, lat, lon, zf):
        self.dat(lat, lon, zf)

    def dat(self, lat, lon, zf):
        self.lat, self.lon, self.zf = float(lat), float(lon), float(zf)
        self.z = int(min(Z_MAX, max(3, math.ceil(self.zf - 1e-6))))
        self.k = 2.0 ** (self.zf - self.z)          # màn hình px / điểm ảnh thế giới ở mức z (≤ 1)
        cx, cy = C.ll2px(self.lat, self.lon, self.z)
        self.x0, self.y0 = cx - (W / 2) / self.k, cy - (H / 2) / self.k
        return self

    def copy(self):
        return Camera(self.lat, self.lon, self.zf)

    def vung(self):
        return self.x0, self.y0, self.x0 + W / self.k, self.y0 + H / self.k

    def render(self, nen):
        x0, y0, x1, y1 = self.vung()
        fx0, fy0 = math.floor(x0) - 1, math.floor(y0) - 1
        roi = nen.ghep(self.z, fx0, fy0, math.ceil(x1) + 2, math.ceil(y1) + 2)
        M = np.float32([[self.k, 0, -(x0 - fx0) * self.k], [0, self.k, -(y0 - fy0) * self.k]])
        return cv2.warpAffine(roi, M, (W, H), flags=cv2.INTER_AREA if self.k < 0.999 else cv2.INTER_LINEAR,
                              borderMode=cv2.BORDER_CONSTANT, borderValue=MAU_TRONG)

    def o_can(self, nen):
        x0, y0, x1, y1 = self.vung()
        return nen.o_can(self.z, math.floor(x0) - 1, math.floor(y0) - 1, math.ceil(x1) + 2, math.ceil(y1) + 2)

    def chieu(self, lat, lon):
        x, y = C.ll2px(lat, lon, self.z)
        return (x - self.x0) * self.k, (y - self.y0) * self.k

    def chieu_mang(self, pts):
        if not len(pts):
            return np.zeros((0, 2), np.float64)
        n = TS * (2.0 ** self.z)
        a = np.asarray(pts, dtype=np.float64)
        lat = np.clip(a[:, 0], -85.05, 85.05)
        x = (a[:, 1] + 180.0) / 360.0 * n
        s = np.sin(np.radians(lat))
        y = (0.5 - np.log((1 + s) / (1 - s)) / (4 * np.pi)) * n
        return np.stack([(x - self.x0) * self.k, (y - self.y0) * self.k], 1)

    def m_per_px(self):
        return C.m_per_px(self.lat, self.zf)

    @staticmethod
    def vua_bbox(bbox, le=0.12, vung_y=(0.0, 1.0), z_max=Z_MAX):
        """camera cho hộp bao [minlat, minlon, maxlat, maxlon] nằm trong khung (lề tỉ lệ), chỉ dùng dải dọc vung_y"""
        lat0, lon0, lat1, lon1 = bbox
        if abs(lat1 - lat0) < 1e-6 and abs(lon1 - lon0) < 1e-6:
            return Camera((lat0 + lat1) / 2, (lon0 + lon1) / 2, 17.0)
        clat, clon = (lat0 + lat1) / 2, (lon0 + lon1) / 2
        hy = (vung_y[1] - vung_y[0]) * H
        best = None
        for zf in np.arange(z_max, 2.0, -0.05):
            ax, ay = C.ll2px(lat1, lon0, zf)
            bx, by = C.ll2px(lat0, lon1, zf)
            bw, bh = (bx - ax) * (1 + 2 * le), (by - ay) * (1 + 2 * le)
            if bw <= W and bh <= hy:
                best = float(zf)
                break
        zf = best if best is not None else 3.0
        cam = Camera(clat, clon, zf)
        # dời tâm cho hộp nằm giữa dải dọc vung_y
        off = ((vung_y[0] + vung_y[1]) / 2 - 0.5) * H
        cy = C.ll2px(clat, clon, cam.z)[1] - off / cam.k
        lat2 = C.px2ll(C.ll2px(clat, clon, cam.z)[0], cy, cam.z)[0]
        return Camera(lat2, clon, zf)


def noi_suy(a, b, u):
    """camera a→b theo u∈[0,1] (zoom nội suy theo log, tâm theo điểm ảnh thế giới)"""
    u = C.clamp(u)
    zf = a.zf + (b.zf - a.zf) * u
    ax, ay = C.ll2px(a.lat, a.lon, 18)
    bx, by = C.ll2px(b.lat, b.lon, 18)
    lat, lon = C.px2ll(ax + (bx - ax) * u, ay + (by - ay) * u, 18)
    return Camera(lat, lon, zf)


# ---------------------------------------------------------------- đường bay dọc tuyến

class DuongBay:
    """camera trượt đều theo mét dọc tuyến (đã lấy mẫu đều), tâm được làm mượt để không giật ở khúc cong"""

    def __init__(self, tuyen_deu, zf, lam_muot=14):
        pts = np.asarray(tuyen_deu, dtype=np.float64)
        if len(pts) >= 3 and lam_muot > 0:
            k = int(lam_muot)
            ker = np.ones(2 * k + 1) / (2 * k + 1)
            pad = np.concatenate([np.repeat(pts[:1], k, 0), pts, np.repeat(pts[-1:], k, 0)])
            lat = np.convolve(pad[:, 0], ker, mode="valid")
            lon = np.convolve(pad[:, 1], ker, mode="valid")
            pts = np.stack([lat, lon], 1)
        self.pts = pts
        seg = [C.khoang_cach_m(pts[i], pts[i + 1]) for i in range(len(pts) - 1)]
        self.cum = np.concatenate([[0.0], np.cumsum(seg)]) if seg else np.array([0.0])
        self.L = float(self.cum[-1])
        self.zf = zf

    def tai(self, u):
        """u ∈ [0,1] theo quãng đường → Camera"""
        s = C.clamp(u) * self.L
        i = int(np.searchsorted(self.cum, s, side="right") - 1)
        i = max(0, min(i, len(self.pts) - 2))
        d = self.cum[i + 1] - self.cum[i]
        t = (s - self.cum[i]) / d if d > 0 else 0.0
        p = self.pts[i] + (self.pts[i + 1] - self.pts[i]) * t
        return Camera(p[0], p[1], self.zf)


# ---------------------------------------------------------------- vẽ lớp trên khung (màn hình)

def lop_rgba():
    return np.zeros((H, W, 4), np.uint8)


def ve_duong(frame, pts_px, mau, day, vien=None, day_vien=0, alpha=1.0, glow=0):
    """polyline anti-alias lên frame RGB. vien = màu viền ngoài (vẽ trước, dày day+day_vien)"""
    if pts_px is None or len(pts_px) < 2:
        return
    p = np.round(np.asarray(pts_px)).astype(np.int32).reshape(-1, 1, 2)
    if alpha >= 0.999 and glow <= 0:
        if vien is not None:
            cv2.polylines(frame, [p], False, vien, int(day + 2 * day_vien), cv2.LINE_AA)
        cv2.polylines(frame, [p], False, mau, int(day), cv2.LINE_AA)
        return
    lay = lop_rgba()
    if glow > 0:
        g = lop_rgba()
        cv2.polylines(g, [p], False, tuple(mau) + (255,), int(day + glow), cv2.LINE_AA)
        g = cv2.GaussianBlur(g, (0, 0), glow * 0.8)
        g[..., 3] = (g[..., 3].astype(np.float32) * 0.9).astype(np.uint8)
        C.dan(frame, g, 0, 0, alpha)
    if vien is not None:
        cv2.polylines(lay, [p], False, tuple(vien) + (255,), int(day + 2 * day_vien), cv2.LINE_AA)
    cv2.polylines(lay, [p], False, tuple(mau) + (255,), int(day), cv2.LINE_AA)
    C.dan(frame, lay, 0, 0, alpha)


def ve_vung(frame, vong_px, mau, alpha_to=0.22, vien=None, day_vien=4, alpha=1.0):
    lay = lop_rgba()
    polys = [np.round(np.asarray(v)).astype(np.int32).reshape(-1, 1, 2) for v in vong_px if len(v) >= 3]
    if not polys:
        return
    cv2.fillPoly(lay, polys, tuple(mau) + (int(255 * alpha_to),), cv2.LINE_AA)
    if vien is not None and day_vien > 0:
        cv2.polylines(lay, polys, True, tuple(vien) + (255,), int(day_vien), cv2.LINE_AA)
    C.dan(frame, lay, 0, 0, alpha)


def ve_cham(frame, x, y, r=9, mau=C.TRANG, vien=(20, 30, 50), alpha=1.0):
    lay = np.zeros((2 * r + 8, 2 * r + 8, 4), np.uint8)
    c = (r + 4, r + 4)
    cv2.circle(lay, c, r + 2, tuple(vien) + (255,), -1, cv2.LINE_AA)
    cv2.circle(lay, c, r, tuple(mau) + (255,), -1, cv2.LINE_AA)
    C.dan(frame, lay, x - r - 4, y - r - 4, alpha)


def ve_ghim(frame, x, y, mau=C.VANG, co=1.0, alpha=1.0):
    """ghim giọt nước, mũi ở (x, y)"""
    s = 44 * co
    lay = np.zeros((int(s * 1.6) + 8, int(s) + 8, 4), np.uint8)
    cx, cy = lay.shape[1] // 2, int(s * 0.5) + 4
    r = int(s * 0.42)
    pts = np.array([[cx - r * 0.72, cy + r * 0.55], [cx + r * 0.72, cy + r * 0.55], [cx, lay.shape[0] - 4]], np.int32)
    cv2.fillPoly(lay, [pts.reshape(-1, 1, 2)], tuple(mau) + (255,), cv2.LINE_AA)
    cv2.circle(lay, (cx, cy), r, tuple(mau) + (255,), -1, cv2.LINE_AA)
    cv2.circle(lay, (cx, cy), int(r * 0.42), (20, 30, 50, 255), -1, cv2.LINE_AA)
    C.dan(frame, lay, x - cx, y - lay.shape[0] + 4, alpha)


def ve_thuoc(frame, a_px, b_px, nhan, alpha=1.0, dy_nhan=-46):
    """thước đo: vạch trắng 2 đầu có ngạnh + nhãn pill navy ở giữa"""
    (x0, y0), (x1, y1) = a_px, b_px
    lay = lop_rgba()
    cv2.line(lay, (int(x0), int(y0)), (int(x1), int(y1)), (0, 0, 0, 200), 7, cv2.LINE_AA)
    cv2.line(lay, (int(x0), int(y0)), (int(x1), int(y1)), (255, 255, 255, 255), 3, cv2.LINE_AA)
    dx, dy = x1 - x0, y1 - y0
    L = math.hypot(dx, dy) or 1.0
    nx, ny = -dy / L * 16, dx / L * 16
    for (x, y) in ((x0, y0), (x1, y1)):
        cv2.line(lay, (int(x - nx), int(y - ny)), (int(x + nx), int(y + ny)), (0, 0, 0, 200), 7, cv2.LINE_AA)
        cv2.line(lay, (int(x - nx), int(y - ny)), (int(x + nx), int(y + ny)), (255, 255, 255, 255), 3, cv2.LINE_AA)
    C.dan(frame, lay, 0, 0, alpha)
    if nhan:
        pill = nhan_pill(nhan, "xbold", 40, C.VANG, C.NAVY)
        C.dan_giua(frame, pill, (x0 + x1) / 2, (y0 + y1) / 2 + dy_nhan, alpha)


_pill_cache = {}


def nhan_pill(text, key="xbold", size=30, mau=C.TRANG, nen=C.NAVY, pad=(22, 12), r=None):
    k = (text, key, size, mau, nen, pad)
    if k in _pill_cache:
        return _pill_cache[k]
    t = C.chu(text, key, size, fill=mau)
    w, h = t.width + 2 * pad[0], t.height + 2 * pad[1]
    box = C.hop_bo((w, h), r or h // 2, tuple(nen) + (235,), vien=tuple(C.NAVY_VIEN) + (255,), vien_w=2)
    sh, p = C.bong_do(box, blur=10, alpha=0.5)
    out = Image.new("RGBA", (w + 2 * p, h + 2 * p), (0, 0, 0, 0))
    out.alpha_composite(sh, (0, 4))
    out.alpha_composite(box, (p, p))
    out.alpha_composite(t, (p + pad[0], p + pad[1]))
    arr = np.asarray(out)
    _pill_cache[k] = arr
    return arr


def nhan_diem(frame, x, y, text, size=30, alpha=1.0, tren=True):
    """nhãn địa danh IN HOA trắng viền tối + chấm trắng"""
    ve_cham(frame, x, y, 8, alpha=alpha)
    sp = _nhan_cache.get((text, size))
    if sp is None:
        sp = np.asarray(C.chu(text.upper(), "xbold", size, fill=C.TRANG, stroke=3, stroke_fill=(10, 18, 30),
                              shadow=(0, 3, 4, 0.7), track=1))
        _nhan_cache[(text, size)] = sp
    y0 = (y - 16 - sp.shape[0]) if tren else (y + 14)
    C.dan(frame, sp, x - sp.shape[1] / 2, y0, alpha)
    return (x - sp.shape[1] / 2, min(y0, y - 10), x + sp.shape[1] / 2, max(y0 + sp.shape[0], y + 10))


_nhan_cache = {}


def hanh_lang_px(pts_px, d_px):
    """2 đường song song cách tuyến ±d_px (pháp tuyến theo tiếp tuyến trung bình)"""
    P = np.asarray(pts_px, dtype=np.float64)
    if len(P) < 2:
        return None, None
    T = np.zeros_like(P)
    T[1:-1] = P[2:] - P[:-2]
    T[0] = P[1] - P[0]
    T[-1] = P[-1] - P[-2]
    n = np.linalg.norm(T, axis=1, keepdims=True)
    T = T / np.maximum(n, 1e-9)
    N = np.stack([-T[:, 1], T[:, 0]], 1)
    return P + N * d_px, P - N * d_px


def lam_toi(frame, sang=0.62, bao_hoa=0.7):
    """nền tối + bớt màu cho bản đồ tổng (vạch nổi)"""
    hsv = cv2.cvtColor(frame, cv2.COLOR_RGB2HSV).astype(np.float32)
    hsv[..., 1] *= bao_hoa
    hsv[..., 2] *= sang
    return cv2.cvtColor(hsv.clip(0, 255).astype(np.uint8), cv2.COLOR_HSV2RGB)


def doan_theo_tien_do(pts_px, u):
    """phần đầu polyline theo tỉ lệ chiều dài u∈[0,1] → (mảng điểm, điểm đầu vạch)"""
    P = np.asarray(pts_px, dtype=np.float64)
    if len(P) < 2:
        return P, (P[-1] if len(P) else None)
    seg = np.linalg.norm(P[1:] - P[:-1], axis=1)
    cum = np.concatenate([[0.0], np.cumsum(seg)])
    s = C.clamp(u) * cum[-1]
    i = int(np.searchsorted(cum, s, side="right") - 1)
    i = max(0, min(i, len(P) - 2))
    t = (s - cum[i]) / seg[i] if seg[i] > 0 else 0.0
    end = P[i] + (P[i + 1] - P[i]) * t
    return np.concatenate([P[:i + 1], end[None]]), end


def ve_hanh_lang(frame, pts_px, d_px, mau=C.VANG, day=3, alpha_to=0.10, alpha=1.0):
    """hành lang ±d_px quanh tuyến dạng VÙNG ĐỆM (nét dày → đường viền), không xoắn ở khúc sông uốn"""
    P = np.asarray(pts_px, dtype=np.float64)
    if len(P) < 2 or d_px < 1:
        return
    M = 600
    mask = np.zeros((H + 2 * M, W + 2 * M), np.uint8)
    q = np.round(P + M).astype(np.int32).reshape(-1, 1, 2)
    cv2.polylines(mask, [q], False, 255, max(2, int(round(2 * d_px))), cv2.LINE_8)
    cs, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not cs:
        return
    lay = lop_rgba()
    cs2 = [c - M for c in cs]
    if alpha_to > 0:
        cv2.fillPoly(lay, cs2, tuple(mau) + (int(255 * alpha_to),), cv2.LINE_AA)
    cv2.polylines(lay, cs2, True, (30, 24, 0, 230), day + 2, cv2.LINE_AA)
    cv2.polylines(lay, cs2, True, tuple(mau) + (255,), day, cv2.LINE_AA)
    C.dan(frame, lay, 0, 0, alpha)


def thuoc_ngang(P, d_px):
    """điểm tuyến gần tâm màn hình + 2 đầu thước vuông góc ±d_px → ((x0,y0),(x1,y1)) | None"""
    P = np.asarray(P, dtype=np.float64)
    if len(P) < 3:
        return None
    c = np.array([W / 2, H / 2])
    i = int(np.argmin(((P - c) ** 2).sum(1)))
    a, b = P[max(0, i - 3)], P[min(len(P) - 1, i + 3)]
    t = b - a
    n = np.linalg.norm(t)
    if n < 1e-6:
        return None
    t /= n
    nv = np.array([-t[1], t[0]])
    return tuple(P[i] - nv * d_px), tuple(P[i] + nv * d_px)
