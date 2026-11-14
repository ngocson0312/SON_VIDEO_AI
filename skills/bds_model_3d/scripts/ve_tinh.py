# -*- coding: utf-8 -*-
"""ve_tinh.py — ảnh vệ tinh Esri World Imagery làm MẶT ĐẤT cho cảnh 3D (cache dùng chung _cache_tiles/esri với các skill bản đồ).

Toạ độ cảnh 3D: gốc = vị trí công trình, trục x = Đông (m thật), trục z = Nam (m thật), y = cao.
Mỗi lớp nền là 1 ảnh vuông phủ [-R, R] m quanh gốc (cắt chính xác từ tile Web Mercator).
"""
import math
import os
import time
from pathlib import Path

from chung import SKILL

UA = {'User-Agent': 'SonAIVideo-bds3d/1.0'}
ESRI = 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}'
_DU_AN = SKILL.parent.parent.parent      # SON_AI_VIDEO (qua junction hay thư mục thật đều ra cùng chỗ)
TILE_CACHE = Path(os.environ.get('NNS_TILE_CACHE') or (_DU_AN / '_cache_tiles' / 'esri'))
R_TD = 6378137.0

# lớp nền: (zoom, nửa cạnh m, cạnh ảnh px tối đa) — gần nét, xa mờ dần tới chân trời (px = độ phân giải gốc, chặn ở trần)
LOP = [(19, 260, 4096), (17, 1300, 4096), (15, 5200, 4096), (13, 20000, 4096), (11, 60000, 2048)]


def tile_xy(lat, lon, z):
    n = 2 ** z
    return (lon + 180) / 360 * n, (1 - math.asinh(math.tan(math.radians(lat))) / math.pi) / 2 * n


def tai_tile(z, x, y):
    import requests
    TILE_CACHE.mkdir(parents=True, exist_ok=True)
    p = TILE_CACHE / f'{z}_{x}_{y}.jpg'
    if p.exists() and p.stat().st_size > 200:
        return p
    last = None
    for k in range(5):
        try:
            r = requests.get(ESRI.format(z=z, x=x, y=y), headers=UA, timeout=30)
            r.raise_for_status()
            p.write_bytes(r.content)
            return p
        except Exception as e:
            last = e
            time.sleep(1.5 * (k + 1))
    raise SystemExit(f'⛔ không tải được ảnh vệ tinh {z}/{x}/{y}: {last} (lệnh này cần mạng)')


def lop_nen(lat, lon, z, nua_m, px, out):
    """ảnh vuông px×px phủ [-nua_m, nua_m] m quanh (lat, lon), bắc ở trên."""
    import concurrent.futures as cf
    from PIL import Image
    out = Path(out)
    if out.exists():
        return out
    k = 1 / math.cos(math.radians(lat))                    # 1 m thật = k m Mercator
    m_tile = 2 * math.pi * R_TD / 2 ** z
    cx, cy = tile_xy(lat, lon, z)
    nua_t = nua_m * k / m_tile                               # nửa cạnh tính bằng tile
    x0, x1 = int(math.floor(cx - nua_t)), int(math.floor(cx + nua_t))
    y0, y1 = int(math.floor(cy - nua_t)), int(math.floor(cy + nua_t))
    big = Image.new('RGB', ((x1 - x0 + 1) * 256, (y1 - y0 + 1) * 256), (40, 45, 40))
    jobs = [(x, y) for x in range(x0, x1 + 1) for y in range(y0, y1 + 1)]
    with cf.ThreadPoolExecutor(8) as ex:
        for (x, y), p in zip(jobs, ex.map(lambda q: tai_tile(z, *q), jobs)):
            try:
                big.paste(Image.open(p).convert('RGB').resize((256, 256)), ((x - x0) * 256, (y - y0) * 256))
            except Exception:
                pass
    l, t = (cx - nua_t - x0) * 256, (cy - nua_t - y0) * 256
    s = 2 * nua_t * 256
    px = min(px, int(round(s)))
    img = big.crop((round(l), round(t), round(l + s), round(t + s))).resize((px, px), Image.LANCZOS)
    img.save(out, quality=90)
    return out


def chuan_bi(lat, lon, thu_muc, bao=print):
    """tải + cắt các lớp nền → [{'file', 'nua_m'}] (gần → xa)."""
    thu_muc = Path(thu_muc); thu_muc.mkdir(parents=True, exist_ok=True)
    ds = []
    for z, nua, px in LOP:
        p = thu_muc / f'nen_z{z}_{lat:.5f}_{lon:.5f}.jpg'
        if not p.exists():
            bao(f'  tải ảnh vệ tinh z{z} ±{nua} m…')
        lop_nen(lat, lon, z, nua, px, p)
        ds.append({'file': str(p), 'nua_m': nua, 'z': z})
    return ds


def ll_sang_m(lat0, lon0, lat, lon):
    """độ → (x Đông, z Nam) m thật quanh gốc."""
    x = math.radians(lon - lon0) * R_TD * math.cos(math.radians(lat0))
    z = -math.radians(lat - lat0) * R_TD
    return x, z
