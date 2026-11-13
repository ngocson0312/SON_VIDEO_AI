# -*- coding: utf-8 -*-
"""ban_do_that.py — nền BẢN ĐỒ THẬT cho đồ hoạ hành trình (nen "that"; khách chốt 13/11/2026: "di chuyển máy bay hay ô tô thì
kiểu bản đồ map thực").

- Ảnh vệ tinh Esri World Imagery (cache dùng chung D:\\…\\SON_AI_VIDEO\\_cache_tiles\\esri với các skill bản đồ khác).
- Đường đi THẬT: ô tô / xe máy / xe buýt → OSRM driving; đi bộ → OSRM foot; xe đạp → OSRM bike; máy bay → cung bay
  (đường tròn lớn + phồng nhẹ như bản đồ chuyến bay); tàu thuỷ / tàu hoả → cung thấp.
- Camera bay: cận điểm đi → lùi ra toàn tuyến (điểm đi trượt mượt về chỗ của nó) → giữ toàn tuyến lúc xe chạy → sà vào điểm đến.
  Camera tính sẵn TỪNG KHUNG ở đây → biết đúng ô ảnh cần tải trước khi dựng.
Toạ độ trong KH: chuẩn hoá Web Mercator [0..1] (x Đông, y Nam). Trang dựng đặt điểm (fx, fy) của camera tại màn (540, FOC_Y).
"""
import concurrent.futures as cf
import json
import math
import os
import time
from pathlib import Path

from chung import FPS, SKILL, H, W, bam, loi, url

UA = {'User-Agent': 'SonAIVideo-dulich/1.0'}
ESRI = 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}'
TILE_CACHE = Path(os.environ.get('NNS_TILE_CACHE') or (SKILL.parent.parent.parent / '_cache_tiles' / 'esri'))
OSRM = {'o_to': 'https://router.project-osrm.org/route/v1/driving/{a};{b}',
        'di_bo': 'https://routing.openstreetmap.de/routed-foot/route/v1/driving/{a};{b}',
        'xe_dap': 'https://routing.openstreetmap.de/routed-bike/route/v1/driving/{a};{b}'}
NOMINATIM = 'https://nominatim.openstreetmap.org/search'

FOC_Y = 945                      # điểm nhìn của camera trên màn (thẻ tuyến gọn chiếm y 200–570, sub ở y ~1340–1470)
VUNG = (860, 600)                # khung chứa toàn tuyến lúc lùi xa: x 110–970, y 645–1245
Z_MAX, Z_MIN = 17.4, 2.0
DUONG_PT = {'may_bay': 'cung', 'o_to': 'o_to', 'xe_may': 'o_to', 'xe_buyt': 'o_to', 'xe_dap': 'xe_dap', 'di_bo': 'di_bo',
            'khong': 'di_bo', 'tau_hoa': 'cung_thap', 'tau_thuy': 'cung_thap'}
DUONG_HL = ('cung', 'cung_thap', 'thang', 'o_to', 'di_bo', 'xe_dap')


def merc(lat, lon):
    lat = max(-85.0, min(85.0, float(lat)))
    return ((float(lon) + 180) / 360, (1 - math.asinh(math.tan(math.radians(lat))) / math.pi) / 2)


def merc_nguoc(x, y):
    return math.degrees(math.atan(math.sinh(math.pi * (1 - 2 * y)))), x * 360 - 180


def km_giua(a, b):
    la1, lo1, la2, lo2 = map(math.radians, (a[0], a[1], b[0], b[1]))
    h = math.sin((la2 - la1) / 2) ** 2 + math.cos(la1) * math.cos(la2) * math.sin((lo2 - lo1) / 2) ** 2
    return 2 * 6371.0 * math.asin(math.sqrt(min(1, h)))


# ---------------- tìm toạ độ (Claude dùng khi viết kế hoạch) ----------------
def tim(ten, n=6):
    import requests
    r = requests.get(NOMINATIM, params={'q': ten, 'format': 'json', 'limit': n, 'accept-language': 'vi,en'}, headers=UA, timeout=30)
    r.raise_for_status()
    ds = r.json()
    if not ds:
        loi(f'không tìm thấy «{ten}» — thử tên khác (tiếng Anh / địa chỉ) hoặc lấy toạ độ từ Google Maps')
    for x in ds:
        loi(f"  [{float(x['lat']):.5f}, {float(x['lon']):.5f}]  {x.get('type', '')} · {x.get('display_name', '')[:110]}")
    return ds


# ---------------- đường đi ----------------
def _cung(a, b, phong):
    """cung bay: đường tròn lớn chiếu Mercator + phồng (tỉ lệ độ dài) về phía bắc."""
    la1, lo1, la2, lo2 = map(math.radians, (a[0], a[1], b[0], b[1]))
    v1 = (math.cos(la1) * math.cos(lo1), math.cos(la1) * math.sin(lo1), math.sin(la1))
    v2 = (math.cos(la2) * math.cos(lo2), math.cos(la2) * math.sin(lo2), math.sin(la2))
    om = math.acos(max(-1, min(1, sum(p * q for p, q in zip(v1, v2))))) or 1e-9
    P = []
    for i in range(121):
        f = i / 120
        s1, s2 = math.sin((1 - f) * om) / math.sin(om), math.sin(f * om) / math.sin(om)
        v = [s1 * p + s2 * q for p, q in zip(v1, v2)]
        P.append(merc(math.degrees(math.atan2(v[2], math.hypot(v[0], v[1]))), math.degrees(math.atan2(v[1], v[0]))))
    (x0, y0), (x1, y1) = P[0], P[-1]
    L = math.hypot(x1 - x0, y1 - y0)
    nx, ny = -(y1 - y0) / L, (x1 - x0) / L                      # pháp tuyến; chọn phía bắc (y nhỏ)
    if ny > 0:
        nx, ny = -nx, -ny
    out = []
    for i, (x, y) in enumerate(P):
        f = i / 120
        k = 4 * f * (1 - f) * phong * L
        out.append((x + nx * k, y + ny * k))
    return out


def duong_di(a, b, kieu, cache_dir, bao=loi):
    """a, b = [lat, lon] → (điểm chuẩn hoá [[x, y]…], km thật | None)."""
    if kieu == 'cung':
        return _cung(a, b, .16), km_giua(a, b)
    if kieu == 'cung_thap':
        return _cung(a, b, .07), km_giua(a, b)
    if kieu == 'thang':
        return [merc(*a), merc(*b)], km_giua(a, b)
    cache_dir.mkdir(parents=True, exist_ok=True)
    p = cache_dir / f"duong_{kieu}_{bam(a, b, kieu)}.json"
    if p.exists():
        d = json.loads(p.read_text(encoding='utf-8'))
        return [tuple(x) for x in d['diem']], d['km']
    import requests
    u = OSRM[kieu].format(a=f'{a[1]:.6f},{a[0]:.6f}', b=f'{b[1]:.6f},{b[0]:.6f}')
    for k in range(3):
        try:
            r = requests.get(u, params={'overview': 'full', 'geometries': 'geojson'}, headers=UA, timeout=40)
            r.raise_for_status()
            rt = r.json()['routes'][0]
            pts = [merc(la, lo) for lo, la in rt['geometry']['coordinates']]
            pts = [merc(*a)] + pts + [merc(*b)]                    # nối 2 đầu về đúng điểm (OSRM bám đường gần nhất)
            km = rt['distance'] / 1000
            p.write_text(json.dumps({'diem': pts, 'km': km}), encoding='utf-8')
            return pts, km
        except Exception as e:
            last = e
            time.sleep(2 * (k + 1))
    bao(f'⚠ không lấy được đường đi thật ({kieu}) {a} → {b}: {last} — vẽ đường cong thấp thay thế')
    return _cung(a, b, .07), None


def _gon(pts, toi_da=420):
    if len(pts) <= toi_da:
        return pts
    b = len(pts) / toi_da
    return [pts[int(i * b)] for i in range(toi_da)] + [pts[-1]]


# ---------------- camera ----------------
def _ease(k):
    k = max(0.0, min(1.0, k))
    return k * k * (3 - 2 * k)


def _g(z, z0, z1):
    """tỉ lệ trượt tâm khi đổi zoom: điểm neo trượt đều trên màn (không vụt mất khi lùi / sà nhanh)."""
    d = 2 ** -z1 - 2 ** -z0
    return 0.0 if abs(d) < 1e-15 else (2 ** -z - 2 ** -z0) / d


def camera(d, route, bao=loi):
    xs, ys = [p[0] for p in route], [p[1] for p in route]
    bw, bh = max(1e-9, max(xs) - min(xs)), max(1e-9, max(ys) - min(ys))
    C = ((max(xs) + min(xs)) / 2, (max(ys) + min(ys)) / 2)
    zO = min(math.log2(VUNG[0] / (256 * bw)), math.log2(VUNG[1] / (256 * bh)))
    zO = max(Z_MIN, min(Z_MAX - 1.2, zO))
    A, B = route[0], route[-1]
    pt = d.get('phuong_tien', 'khong')
    dz = 6.6 if pt == 'may_bay' else 2.2 if pt in ('o_to', 'xe_may', 'xe_buyt', 'tau_hoa', 'tau_thuy') else 1.3
    zA = min(Z_MAX, float(d.get('zoom_gan') or (zO + dz)), 12.8 if pt == 'may_bay' else Z_MAX)
    tu, den, di, toi = d['tu'], d['den'], d['luc_di'], d['luc_den']
    t0 = max(tu + .6, di - .7)                                  # bắt đầu lùi ra trước lúc rời bến
    t1 = t0 + max(1.0, min(2.0, .45 * (toi - di)))
    t2 = max(t1 + .3, toi - .15)
    con = max(.5, den - t2 - .1)
    t3 = t2 + min(2.0, con)
    zO2 = zO + .12
    zB = min(zA, zO2 + 2.6 * (t3 - t2))
    cam = []
    n = int(round((den - tu) * FPS)) + 1
    for i in range(n):
        t = tu + i / FPS
        if t <= t0:
            z, c = zA + .35 * (1 - _ease((t - tu) / max(.01, t0 - tu))), A
        elif t <= t1:
            z = zA + (zO - zA) * _ease((t - t0) / (t1 - t0))
            g = _g(z, zA, zO)
            c = (A[0] + (C[0] - A[0]) * g, A[1] + (C[1] - A[1]) * g)
        elif t <= t2:
            z, c = zO + .12 * (t - t1) / max(.01, t2 - t1), C
        elif t <= t3:
            z = zO2 + (zB - zO2) * _ease((t - t2) / max(.01, t3 - t2))
            g = _g(z, zO2, zB)
            c = (C[0] + (B[0] - C[0]) * g, C[1] + (B[1] - C[1]) * g)
        else:
            z, c = zB + .08 * (t - t3) / max(.01, den - t3), B
        cam.append((round(c[0], 10), round(c[1], 10), round(z, 4)))
    return cam, {'zO': zO, 'zA': zA, 'zB': zB}


def muc_tile(z):
    return int(max(1, min(18, math.floor(z + .5))))


def tile_can(cam):
    """mọi ô ảnh (z, x, y) cần cho các khung camera (mức chính + mức lót thấp hơn 2 bậc)."""
    S = set()
    for fx, fy, z in cam:
        sc = 256 * 2 ** z
        x0, x1 = fx + (0 - W / 2) / sc, fx + (W - W / 2) / sc
        y0, y1 = fy + (0 - FOC_Y) / sc, fy + (H - FOC_Y) / sc
        L = muc_tile(z)
        for LL in (L, max(1, L - 2)):
            n = 2 ** LL
            for tx in range(int(math.floor(x0 * n)), int(math.floor(x1 * n)) + 1):
                for ty in range(max(0, int(math.floor(y0 * n))), min(n - 1, int(math.floor(y1 * n))) + 1):
                    S.add((LL, tx % n, ty))
    return S


def tai_tile(z, x, y):
    import requests
    p = TILE_CACHE / f'{z}_{x}_{y}.jpg'
    if p.exists() and p.stat().st_size > 200:
        return True
    for k in range(4):
        try:
            r = requests.get(ESRI.format(z=z, x=x, y=y), headers=UA, timeout=30)
            r.raise_for_status()
            p.write_bytes(r.content)
            return True
        except Exception:
            time.sleep(1.2 * (k + 1))
    return False


def chuan_bi(work, d, bao=loi):
    """→ dict 'bd' gắn vào đồ hoạ hành trình cho trang dựng (đường, camera từng khung, gốc URL ô ảnh)."""
    work = Path(work)
    a, b = d['xuat_phat']['toa_do'], d['diem_den']['toa_do']
    kieu = d.get('duong') or DUONG_PT.get(d.get('phuong_tien', 'khong'), 'di_bo')
    route, km = duong_di(a, b, kieu, work / 'ban_do_that', bao)
    route = _gon(route)
    cam, z = camera(d, route, bao)
    can = tile_can(cam)
    TILE_CACHE.mkdir(parents=True, exist_ok=True)
    thieu = [k for k in can if not (TILE_CACHE / f'{k[0]}_{k[1]}_{k[2]}.jpg').exists()]
    t0 = time.time()
    hong = 0
    if thieu:
        bao(f"  {d['id']}: tải {len(thieu)}/{len(can)} ô ảnh vệ tinh (cần mạng) …")
        with cf.ThreadPoolExecutor(8) as ex:
            for ok in ex.map(lambda k: tai_tile(*k), thieu):
                hong += not ok
    if hong:
        bao(f"⚠ {d['id']}: {hong} ô ảnh vệ tinh không tải được — chỗ đó lấy ô mức thấp hơn (mờ hơn)")
    kc = f'đường thật ≈ {km:.1f} km' if km else 'đường thẳng (không lấy được đường thật)'
    bao(f"  {d['id']}: bản đồ thật {kieu} · {kc} · zoom {z['zA']:.1f} → {z['zO']:.1f} → {z['zB']:.1f} · "
        f"{len(can)} ô ({time.time() - t0:.0f}s)")
    phu = []
    for o in d.get('diem_phu') or []:
        x, y = merc(*o['toa_do'])
        phu.append([x, y, o['ten']])
    return {'tile': url(TILE_CACHE, thu_muc=True), 'duong': [[round(x, 10), round(y, 10)] for x, y in route],
            'cam': cam, 'foc_y': FOC_Y, 'phu': phu, 'kieu': kieu, 'km': km, 'zO': round(z['zO'], 3)}
