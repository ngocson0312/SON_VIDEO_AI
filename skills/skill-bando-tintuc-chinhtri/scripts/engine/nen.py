# -*- coding: utf-8 -*-
"""Nền bản đồ: ô ảnh vệ tinh XYZ (Esri World Imagery) cache trên đĩa, ghép thành vùng đất (ROI) cho mỗi khung."""
import math
import os
import threading
from collections import OrderedDict
from concurrent.futures import ThreadPoolExecutor

import numpy as np

TILE_URL = "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"
TILE = 256
MAU_KHONG_GIAN = (30, 14, 8)  # BGR: navy sẫm cho vùng ngoài bản đồ
ROI_MAX = 2560


class Nen:
    def __init__(self, cache_dir, mang=False, z_max=12):
        self.cache = cache_dir
        self.mang = mang
        self.z_max = z_max
        self.lru = OrderedDict()
        self.lock = threading.Lock()
        self.thieu = set()

    def duong_dan(self, z, x, y):
        return os.path.join(self.cache, str(z), "%d_%d.jpg" % (x, y))

    def tai_o(self, z, x, y):
        p = self.duong_dan(z, x, y)
        if os.path.exists(p) and os.path.getsize(p) > 0:
            return True
        if not self.mang:
            return False
        import requests
        os.makedirs(os.path.dirname(p), exist_ok=True)
        for i in range(3):
            try:
                r = requests.get(TILE_URL.format(z=z, x=x, y=y), timeout=30,
                                 headers={"User-Agent": "skill-bando-tintuc-chinhtri/1.0"})
                if r.status_code == 200 and len(r.content) > 200:
                    tmp = p + ".part"
                    with open(tmp, "wb") as f:
                        f.write(r.content)
                    os.replace(tmp, p)
                    return True
            except Exception:
                pass
        return False

    def lay_o(self, z, x, y):
        import cv2
        n = 1 << z
        x = x % n
        if y < 0 or y >= n:
            return None
        k = (z, x, y)
        with self.lock:
            if k in self.lru:
                self.lru.move_to_end(k)
                return self.lru[k]
        img = None
        if self.tai_o(z, x, y):
            img = cv2.imread(self.duong_dan(z, x, y), cv2.IMREAD_COLOR)
        if img is None:
            # thiếu ô: thử lấy ô mức thấp hơn phóng to
            if z > 0:
                cha = self.lay_o(z - 1, x // 2, y // 2)
                if cha is not None:
                    ox, oy = (x % 2) * (TILE // 2), (y % 2) * (TILE // 2)
                    img = cv2.resize(cha[oy:oy + TILE // 2, ox:ox + TILE // 2], (TILE, TILE),
                                     interpolation=cv2.INTER_LINEAR)
            if img is None:
                self.thieu.add(k)
                img = np.full((TILE, TILE, 3), MAU_KHONG_GIAN, np.uint8)
        with self.lock:
            self.lru[k] = img
            if len(self.lru) > 900:
                self.lru.popitem(last=False)
        return img

    def ghep(self, z, x0, y0, x1, y1):
        """Ghép vùng px [x0,x1)×[y0,y1) ở mức z (x có thể vượt biên, quấn vòng)."""
        w, h = int(x1 - x0), int(y1 - y0)
        out = np.full((h, w, 3), MAU_KHONG_GIAN, np.uint8)
        n = 1 << z
        world = n * TILE
        tx0, tx1 = math.floor(x0 / TILE), math.floor((x1 - 1) / TILE)
        ty0, ty1 = math.floor(y0 / TILE), math.floor((y1 - 1) / TILE)
        for ty in range(ty0, ty1 + 1):
            if ty < 0 or ty >= n:
                continue
            for tx in range(tx0, tx1 + 1):
                img = self.lay_o(z, tx % n, ty)
                if img is None:
                    continue
                px, py = tx * TILE - x0, ty * TILE - y0
                sx0, sy0 = max(0, -px), max(0, -py)
                sx1, sy1 = min(TILE, w - px), min(TILE, h - py)
                if sx1 <= sx0 or sy1 <= sy0:
                    continue
                out[py + sy0:py + sy1, px + sx0:px + sx1] = img[sy0:sy1, sx0:sx1]
        return out

    def o_can(self, z, x0, y0, x1, y1):
        n = 1 << z
        ks = set()
        for ty in range(math.floor(y0 / TILE), math.floor((y1 - 1) / TILE) + 1):
            if 0 <= ty < n:
                for tx in range(math.floor(x0 / TILE), math.floor((x1 - 1) / TILE) + 1):
                    ks.add((z, tx % n, ty))
        return ks

    def tai_truoc(self, keys, luong=8):
        thieu = [k for k in keys if not os.path.exists(self.duong_dan(*k))]
        if not thieu:
            return 0, 0
        loi = 0
        with ThreadPoolExecutor(max_workers=luong) as ex:
            for okk in ex.map(lambda k: self.tai_o(*k), thieu):
                if not okk:
                    loi += 1
        return len(thieu), loi


def chon_vung(cam, z_max=12, roi_max=ROI_MAX, he_so=0.9):
    """Chọn mức zoom + hộp px của vùng đất cho khung hiện tại.
    Trả (z, x0, y0, x1, y1) px ở mức z (x0 có thể âm hoặc > world: quấn vòng)."""
    tt = cam.tt
    # px mặt đất trên 1 đơn vị tại điểm nhìn ≈ W / w; muốn 256*2^z ≈ he_so * W / w
    z = int(round(math.log2(he_so * cam.W / (TILE * tt.w))))
    z = max(1, min(z_max, z))
    while True:
        ux0, uy0, ux1, uy1 = cam.vung_dat(xa_nhat=cam.d * 5.0)
        s = TILE * (1 << z)
        uy0, uy1 = max(0.0, uy0), min(1.0, uy1)
        x0, x1 = math.floor(ux0 * s), math.ceil(ux1 * s)
        y0, y1 = math.floor(uy0 * s), math.ceil(uy1 * s)
        if (x1 - x0) <= roi_max and (y1 - y0) <= roi_max:
            break
        if z <= 1:
            # vẫn quá to: cắt bớt vùng xa (giữ tâm)
            cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
            x0, x1 = int(cx - roi_max / 2), int(cx + roi_max / 2)
            y0, y1 = int(cy - roi_max / 2), int(cy + roi_max / 2)
            break
        z -= 1
    return z, x0, y0, x1, y1
