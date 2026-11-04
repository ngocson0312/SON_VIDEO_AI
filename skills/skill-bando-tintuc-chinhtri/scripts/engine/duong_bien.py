# -*- coding: utf-8 -*-
"""Đường đi TRÊN BIỂN: tránh đất liền (Natural Earth 10m), dùng cho tàu / tuyến hàng hải / dòng chảy dầu.

Dựng mặt nạ đất liền 0,1° từ polygon các nước, nở ra ~0,4° để đường cách bờ, rồi A* tám hướng, nắn thẳng
(line-of-sight) và làm mượt (Chaikin). Điểm đầu / cuối nằm trên đất (cảng) được dời ra mặt biển gần nhất.
"""
import heapq
import math

import cv2
import numpy as np

RES = 0.1          # độ / ô
NO_RA = 4          # số ô nở ra quanh bờ (≈ 0,4°)
_CACHE = {}


def _mat_na_dat(dia_ly):
    key = id(dia_ly)
    if key in _CACHE:
        return _CACHE[key]
    w, h = int(360 / RES), int(180 / RES)
    m = np.zeros((h, w), np.uint8)
    seen = set()
    for k, r in dia_ly.nuoc.items():
        if id(r) in seen:
            continue
        seen.add(id(r))
        for vong in r.get("vong", []):
            pts = np.array(vong, dtype=np.float64)
            if len(pts) < 3:
                continue
            xs = (pts[:, 0] + 180) / RES
            ys = (90 - pts[:, 1]) / RES
            # polygon vắt qua kinh tuyến 180 (nhảy > 180°) → bỏ qua để không kẻ vệt ngang
            if (pts[:, 0].max() - pts[:, 0].min()) > 300:
                continue
            cv2.fillPoly(m, [np.stack([xs, ys], 1).astype(np.int32)], 1)
    muc = {}
    for k in (NO_RA, 2, 1):
        ker = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * k + 1, 2 * k + 1))
        d = cv2.dilate(m, ker)
        # vùng nước rời rạc quá nhỏ (hồ, vịnh kín) coi như không đi được
        n, lab, st, _ = cv2.connectedComponentsWithStats((d == 0).astype(np.uint8), connectivity=8)
        nho_ = np.ones(len(st), bool)
        nho_[1:] = st[1:, cv2.CC_STAT_AREA] < 3200
        nho_[0] = False
        muc[k] = (d > 0) | nho_[lab]
    _CACHE[key] = (m.astype(bool), muc)
    return _CACHE[key]


def _o(lon, lat):
    return int((90 - lat) / RES), int((lon + 180) / RES)


def _lonlat(r, c):
    return (c + 0.5) * RES - 180, 90 - (r + 0.5) * RES


def la_dat(dia_ly, lon, lat):
    dat, _ = _mat_na_dat(dia_ly)
    r, c = _o(lon, lat)
    return bool(dat[min(max(r, 0), dat.shape[0] - 1), min(max(c, 0), dat.shape[1] - 1)])


def _ra_bien(nho, r, c, toi_da=12):
    """Ô biển (ngoài vùng nở) gần nhất theo vòng tròn mở rộng dần."""
    H, W = nho.shape
    if not nho[r, c]:
        return r, c
    for d in range(1, int(toi_da / RES) + 1):
        best = None
        for dr in range(-d, d + 1):
            for dc in (-d, d) if abs(dr) != d else range(-d, d + 1):
                rr, cc = r + dr, c + dc
                if 0 <= rr < H and 0 <= cc < W and not nho[rr, cc]:
                    dd = dr * dr + dc * dc
                    if best is None or dd < best[0]:
                        best = (dd, rr, cc)
        if best:
            return best[1], best[2]
    return r, c


def _thang_qua(nho, a, b):
    n = int(max(abs(a[0] - b[0]), abs(a[1] - b[1])) * 1.5) + 2
    rs = np.linspace(a[0], b[0], n).round().astype(int)
    cs = np.linspace(a[1], b[1], n).round().astype(int)
    return not nho[rs, cs].any()


def _dai(r):
    return sum(math.hypot(x1 - x0, y1 - y0) for (x0, y0), (x1, y1) in zip(r[:-1], r[1:]))


def tim_duong(dia_ly, a, b):
    """Thử lề rộng → hẹp; lấy lề rộng nhất mà không dài hơn 1,25× đường ngắn nhất (tránh vòng cả quần đảo)."""
    ds = []
    for k in (NO_RA, 2, 1):
        r = _tim(dia_ly, a, b, k)
        if r is not None:
            ds.append((k, r, _dai(r)))
    if not ds:
        return None
    ngan = min(d[2] for d in ds)
    for k, r, d in ds:
        if d <= ngan * 1.25:
            return r
    return ds[-1][1]


def _tim(dia_ly, a, b, k):
    """a, b = (lon, lat). Trả (list [(lon,lat)…], da_doi_diem) — đường trên biển, điểm đầu/cuối đã dời ra biển."""
    dat, muc = _mat_na_dat(dia_ly)
    nho = muc[k]
    H, W = nho.shape
    ra, ca = _o(*a)
    rb, cb = _o(*b)
    ra, ca = min(max(ra, 0), H - 1), min(max(ca, 0), W - 1)
    rb, cb = min(max(rb, 0), H - 1), min(max(cb, 0), W - 1)
    s = _ra_bien(nho, ra, ca)
    g = _ra_bien(nho, rb, cb)
    # khung tìm kiếm: hộp bao + 20°
    pad = int(20 / RES)
    r0, r1 = max(0, min(s[0], g[0]) - pad), min(H, max(s[0], g[0]) + pad)
    c0, c1 = max(0, min(s[1], g[1]) - pad), min(W, max(s[1], g[1]) + pad)
    hs = lambda p: math.hypot(p[0] - g[0], p[1] - g[1])
    dq = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]
    best = {s: 0.0}
    cha = {}
    pq = [(hs(s), 0.0, s)]
    xong = False
    while pq:
        f, gc, u = heapq.heappop(pq)
        if u == g:
            xong = True
            break
        if gc > best.get(u, 1e18):
            continue
        for dr, dc in dq:
            v = (u[0] + dr, u[1] + dc)
            if not (r0 <= v[0] < r1 and c0 <= v[1] < c1) or nho[v]:
                continue
            ng = gc + (1.4142 if dr and dc else 1.0)
            if ng < best.get(v, 1e18):
                best[v] = ng
                cha[v] = u
                heapq.heappush(pq, (ng + hs(v), ng, v))
    if not xong:
        return None
    p = [g]
    while p[-1] != s:
        p.append(cha[p[-1]])
    p.reverse()
    # nắn thẳng: giữ điểm xa nhất còn nhìn thấy nhau
    out = [p[0]]
    i = 0
    while i < len(p) - 1:
        j = len(p) - 1
        while j > i + 1 and not _thang_qua(nho, p[i], p[j]):
            j -= 1
        out.append(p[j])
        i = j
    pts = [_lonlat(*q) for q in out]
    # nối đúng điểm đầu / cuối thật nếu đã dời (đoạn ngắn sát cảng)
    if (ra, ca) != s:
        pts.insert(0, tuple(a))
    if (rb, cb) != g:
        pts.append(tuple(b))
    # Chaikin 3 vòng cho cong mềm (giữ đầu cuối)
    arr = np.array(pts, float)
    for _ in range(3):
        if len(arr) < 3:
            break
        q = 0.75 * arr[:-1] + 0.25 * arr[1:]
        r = 0.25 * arr[:-1] + 0.75 * arr[1:]
        nxt = np.empty((len(q) * 2, 2))
        nxt[0::2], nxt[1::2] = q, r
        arr = np.vstack([arr[:1], nxt[1:-1], arr[-1:]])
    return [tuple(x) for x in arr.tolist()]


def do_dat_lien(dia_ly, pts, buoc=0.2):
    """Tỉ lệ (0–1) chiều dài đường đi qua đất liền (không nở). pts: [(lon,lat)…]."""
    dat, _ = _mat_na_dat(dia_ly)
    H, W = dat.shape
    tong = 0
    tren = 0
    for (x0, y0), (x1, y1) in zip(pts[:-1], pts[1:]):
        n = max(2, int(max(abs(x1 - x0), abs(y1 - y0)) / buoc))
        for k in range(n):
            f = k / n
            r, c = _o(x0 + (x1 - x0) * f, y0 + (y1 - y0) * f)
            tong += 1
            if 0 <= r < H and 0 <= c < W and dat[r, c]:
                tren += 1
    return tren / max(tong, 1)


def tim_duong_qua(dia_ly, diem):
    """diem: [(lon,lat), …] gồm đầu, các điểm dẫn `qua` (eo biển, mũi), cuối. Mỗi đoạn dò đường biển;
    đoạn nào dò không ra (eo hẹp hơn độ phân giải) thì nối thẳng — nên đặt điểm dẫn sát hai đầu eo."""
    out = []
    for a, b in zip(diem[:-1], diem[1:]):
        r = tim_duong(dia_ly, a, b) or [tuple(a), tuple(b)]
        out.extend(r if not out else r[1:])
    return out
