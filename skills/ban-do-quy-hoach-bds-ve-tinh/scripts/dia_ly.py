# -*- coding: utf-8 -*-
"""Địa lý: tìm toạ độ (Photon) + lấy hình học thật từ OSM API (tim sông/đường, ranh xã/huyện, điểm) + cắt đoạn A→B.

Cần mạng (chạy ngoài sandbox trong Claude Code). Overpass công cộng hay 502 (04/11/2026) nên KHÔNG dùng —
Photon trả osm_type/osm_id, rồi api.openstreetmap.org/api/0.6/<type>/<id>/full.json cho toàn bộ node/way.
Mọi kết quả cache ở ~/.cache/ban-do-quy-hoach-bds-ve-tinh/osm.

    python -I scripts/dia_ly.py tim "Đập Đáy" [--gan 21.0,105.7]
    python -I scripts/dia_ly.py lay R2155608            # in tóm tắt hình học
"""
import argparse
import json
import math
import os
import re
import sys
import time

import numpy as np
import requests

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import chung as C

PHOTON = "https://photon.komoot.io/api/"
PHOTON_REV = "https://photon.komoot.io/reverse"
LOAI_DIA_DANH = ("city", "town", "suburb", "quarter", "village", "neighbourhood", "hamlet")
OSM_API = "https://api.openstreetmap.org/api/0.6/%s/%s%s.json"
LOAI_TUYEN = {"river", "stream", "canal", "drain", "ditch", "motorway", "trunk", "primary", "secondary", "tertiary",
              "residential", "unclassified", "road", "track", "path", "living_street", "railway", "rail", "light_rail",
              "subway", "tram", "dike", "dyke", "levee"}
LOAI_VUNG = {"administrative", "historic", "political"}


def _get(url, params=None, timeout=60, lan=4):
    last = None
    for k in range(lan):
        try:
            r = requests.get(url, params=params, headers=C.UA, timeout=timeout)
            if r.status_code == 200:
                return r
            last = "HTTP %d" % r.status_code
            if r.status_code in (404, 410):
                break
        except Exception as e:
            last = type(e).__name__
        time.sleep(1.5 * (k + 1))
    raise RuntimeError("không gọi được %s (%s) — kiểm mạng / chạy ngoài sandbox" % (url, last))


# ---------------------------------------------------------------- Photon

def tim(q, gan=None, n=8, osm_tag=None):
    """→ [{osm: 'R2155608', ten, key, value, mo_ta, lat, lon, extent}]"""
    p = {"q": q, "limit": n, "lang": "default"}
    if gan:
        p["lat"], p["lon"] = gan[0], gan[1]
    if osm_tag:
        p["osm_tag"] = osm_tag
    r = _get(PHOTON, p, timeout=30)
    out = []
    for f in r.json().get("features", []):
        pr = f["properties"]
        lon, lat = f["geometry"]["coordinates"]
        mo = ", ".join(str(pr[k]) for k in ("street", "district", "city", "state") if pr.get(k))
        out.append({"osm": "%s%d" % (pr.get("osm_type", "N"), int(pr.get("osm_id", 0))),
                    "ten": C.nfc(pr.get("name") or pr.get("street") or q), "key": pr.get("osm_key"),
                    "value": pr.get("osm_value"), "kieu": pr.get("type"), "mo_ta": mo, "lat": lat, "lon": lon,
                    "extent": pr.get("extent")})
    return out


def chon(ung_vien, ten, loai):
    """chấm điểm ứng viên Photon theo loại mong muốn + tên: → (ứng viên tốt nhất, điểm)"""
    key = C.ten_khong_dau(ten)
    best, best_s = None, -1
    for u in ung_vien:
        s = 0
        tn = C.ten_khong_dau(u["ten"])
        if tn == key:
            s += 6
        elif key in tn or tn in key:
            s += 3
        v = (u.get("value") or "").lower()
        k = (u.get("key") or "").lower()
        if loai == "tuyen" and (v in LOAI_TUYEN or k in ("waterway", "highway", "railway")):
            s += 5
            if u["osm"].startswith("R"):
                s += 2            # relation = cả tuyến, way = 1 mẩu
        if loai == "vung":
            if k == "boundary" and v == "administrative":
                s += 5
            elif k == "boundary" and v == "historic":
                s += 3
            elif k == "place":
                s += 1
        if loai == "diem" and k not in ("boundary",):
            s += 2
            if v in ("dam", "weir", "bridge", "town", "village", "suburb", "locality", "neighbourhood", "quarter"):
                s += 2
        if s > best_s:
            best, best_s = u, s
    return best, best_s


# ---------------------------------------------------------------- OSM API

def _osm_full(osm):
    typ = {"N": "node", "W": "way", "R": "relation"}[osm[0].upper()]
    oid = osm[1:]
    p = os.path.join(C.cache_dir("osm"), "%s_%s.json" % (typ, oid))
    if os.path.isfile(p):
        return C.jload(p)
    url = OSM_API % (typ, oid, "" if typ == "node" else "/full")
    r = _get(url, timeout=120)
    d = r.json()
    C.jsave(p, d)
    return d


def _osm_map(bbox):
    """mọi node/way trong hộp nhỏ [minlat, minlon, maxlat, maxlon] (OSM API /map, ≤ 0,25 độ², cache)"""
    la0, lo0, la1, lo1 = [round(float(x), 4) for x in bbox]
    p = os.path.join(C.cache_dir("osm"), "map_%s_%s_%s_%s.json" % (la0, lo0, la1, lo1))
    if os.path.isfile(p):
        return C.jload(p)
    r = _get("https://api.openstreetmap.org/api/0.6/map.json", params={"bbox": "%s,%s,%s,%s" % (lo0, la0, lo1, la1)},
             timeout=120)
    d = r.json()
    C.jsave(p, d)
    return d


def _cat_nhau(a0, a1, b0, b1):
    """giao 2 đoạn thẳng (toạ độ phẳng) → (u trên a) hoặc None"""
    d = (a1[0] - a0[0]) * (b1[1] - b0[1]) - (a1[1] - a0[1]) * (b1[0] - b0[0])
    if abs(d) < 1e-15:
        return None
    u = ((b0[0] - a0[0]) * (b1[1] - b0[1]) - (b0[1] - a0[1]) * (b1[0] - b0[0])) / d
    v = ((b0[0] - a0[0]) * (a1[1] - a0[1]) - (b0[1] - a0[1]) * (a1[0] - a0[0])) / d
    if 0 <= u <= 1 and 0 <= v <= 1:
        return u
    return None


def giao_duong(tuyen, ten_duong, quanh, ban_kinh=0.012):
    """chỗ tuyến (sông) cắt con đường tên ten_duong gần điểm quanh [lat,lon]: lấy mọi way trong hộp quanh điểm
    (OSM API /map), giữ way có name/ref chứa ten_duong (không dấu) → giao điểm đoạn-đoạn với tuyến. → [lat,lon] | None"""
    la, lo = quanh
    d = _osm_map([la - ban_kinh, lo - ban_kinh, la + ban_kinh, lo + ban_kinh])
    els = d.get("elements", [])
    nodes = {e["id"]: (e["lat"], e["lon"]) for e in els if e["type"] == "node"}
    key = C.ten_khong_dau(ten_duong)
    cands = []
    for e in els:
        if e["type"] != "way":
            continue
        tg = e.get("tags", {})
        if not tg.get("highway") and not tg.get("railway"):
            continue
        nm = " ".join(C.ten_khong_dau(tg.get(k, "")) for k in ("name", "ref", "official_name", "alt_name", "old_name"))
        if key and key in nm:
            cands.append([nodes[i] for i in e["nodes"] if i in nodes])
    T = [(p[1], p[0]) for p in tuyen]
    hits = []
    for pts in cands:
        for j in range(len(pts) - 1):
            b0, b1 = (pts[j][1], pts[j][0]), (pts[j + 1][1], pts[j + 1][0])
            for i in range(len(T) - 1):
                a0, a1 = T[i], T[i + 1]
                if max(a0[0], a1[0]) < min(b0[0], b1[0]) or min(a0[0], a1[0]) > max(b0[0], b1[0]):
                    continue
                if max(a0[1], a1[1]) < min(b0[1], b1[1]) or min(a0[1], a1[1]) > max(b0[1], b1[1]):
                    continue
                u = _cat_nhau(a0, a1, b0, b1)
                if u is not None:
                    hits.append([a0[1] + (a1[1] - a0[1]) * u, a0[0] + (a1[0] - a0[0]) * u])
    if not hits:
        return None, len(cands)
    hits.sort(key=lambda p: C.khoang_cach_m(p, quanh))
    return hits[0], len(cands)


def _noi_way(ways):
    """ways: [[node id…]] → các chuỗi nối tiếp (theo id node 2 đầu), dài nhất trước"""
    rem = sorted([list(w) for w in ways if len(w) >= 2], key=len, reverse=True)
    chains = []
    while rem:
        cur = rem.pop(0)
        ext = True
        while ext and rem:
            ext = False
            for i, w in enumerate(rem):
                if w[0] == cur[-1]:
                    cur = cur + w[1:]
                elif w[-1] == cur[-1]:
                    cur = cur + w[::-1][1:]
                elif w[-1] == cur[0]:
                    cur = w[:-1] + cur
                elif w[0] == cur[0]:
                    cur = w[::-1][:-1] + cur
                else:
                    continue
                rem.pop(i)
                ext = True
                break
        chains.append(cur)
    return chains


def hinh_hoc(osm):
    """→ {loai: diem|tuyen|vung, ten, tags, diem [lat,lon], tuyen [[lat,lon]…] (chuỗi dài nhất), cac_tuyen, vong [[…]], bbox}"""
    d = _osm_full(osm)
    els = d.get("elements", [])
    nodes = {e["id"]: (e["lat"], e["lon"]) for e in els if e["type"] == "node"}
    ways = {e["id"]: e for e in els if e["type"] == "way"}
    rels = [e for e in els if e["type"] == "relation"]
    typ = osm[0].upper()
    out = {"osm": osm, "loai": None, "ten": "", "tags": {}, "diem": None, "tuyen": None, "cac_tuyen": [], "vong": [],
           "bbox": None}

    def coords(ids):
        return [[nodes[i][0], nodes[i][1]] for i in ids if i in nodes]

    if typ == "N":
        e = [x for x in els if x["type"] == "node"][0]
        out.update({"loai": "diem", "tags": e.get("tags", {}), "diem": [e["lat"], e["lon"]]})
    elif typ == "W":
        w = ways[int(osm[1:])]
        out["tags"] = w.get("tags", {})
        pts = coords(w["nodes"])
        kin = len(w["nodes"]) > 3 and w["nodes"][0] == w["nodes"][-1]
        if kin and (out["tags"].get("building") or out["tags"].get("landuse") or out["tags"].get("amenity")
                    or out["tags"].get("leisure") or out["tags"].get("natural")):
            out.update({"loai": "diem", "vong": [pts], "diem": _trong_tam(pts)})
        elif out["tags"].get("waterway") in ("dam", "weir") or out["tags"].get("man_made") or len(pts) <= 3:
            out.update({"loai": "diem", "tuyen": pts, "cac_tuyen": [pts], "diem": _trong_tam(pts)})
        else:
            out.update({"loai": "tuyen", "tuyen": pts, "cac_tuyen": [pts]})
    else:
        # full.json kèm cả relation con (vd thị trấn trong huyện) ⇒ phải chọn đúng id, KHÔNG lấy rels[0]
        r = next((e for e in rels if e["id"] == int(osm[1:])), {"members": [], "tags": {}})
        out["tags"] = r.get("tags", {})
        mem = r.get("members", [])
        if out["tags"].get("type") == "boundary" or out["tags"].get("boundary"):
            ids = [m["ref"] for m in mem if m["type"] == "way" and m.get("role", "outer") in ("outer", "")]
            chains = _noi_way([ways[i]["nodes"] for i in ids if i in ways])
            out["vong"] = [coords(c) for c in chains if len(c) >= 4]
            out["loai"] = "vung"
            allp = [p for v in out["vong"] for p in v]
            out["diem"] = _trong_tam(max(out["vong"], key=len)) if out["vong"] else None
            for m in mem:
                if m["type"] == "node" and m.get("role") in ("label", "admin_centre") and m["ref"] in nodes:
                    out["diem"] = list(nodes[m["ref"]])
        else:
            main = [m["ref"] for m in mem if m["type"] == "way" and m.get("role") == "main_stream"]
            ids = main or [m["ref"] for m in mem if m["type"] == "way"]
            chains = _noi_way([ways[i]["nodes"] for i in ids if i in ways])
            out["cac_tuyen"] = [coords(c) for c in chains]
            out["cac_tuyen"].sort(key=lambda c: -C.dai_tuyen_m(c) if len(c) > 1 else 0)
            out["tuyen"] = out["cac_tuyen"][0] if out["cac_tuyen"] else None
            out["loai"] = "tuyen"
    out["ten"] = C.nfc(out["tags"].get("name", ""))
    pts = []
    for key in ("tuyen",):
        if out.get(key):
            pts += out[key]
    for v in out["vong"]:
        pts += v
    if out["diem"]:
        pts.append(out["diem"])
    if pts:
        lats, lons = [p[0] for p in pts], [p[1] for p in pts]
        out["bbox"] = [min(lats), min(lons), max(lats), max(lons)]
    return out


def _trong_tam(pts):
    if not pts:
        return None
    if len(pts) > 3 and pts[0] == pts[-1]:
        a = cx = cy = 0.0
        for i in range(len(pts) - 1):
            x0, y0 = pts[i][1], pts[i][0]
            x1, y1 = pts[i + 1][1], pts[i + 1][0]
            f = x0 * y1 - x1 * y0
            a += f
            cx += (x0 + x1) * f
            cy += (y0 + y1) * f
        if abs(a) > 1e-12:
            return [cy / (3 * a), cx / (3 * a)]
    return [sum(p[0] for p in pts) / len(pts), sum(p[1] for p in pts) / len(pts)]


# ---------------------------------------------------------------- tuyến: chiếu điểm, cắt đoạn, đo

def _xy(pts, z=18):
    return np.array([C.ll2px(p[0], p[1], z) for p in pts], dtype=np.float64)


def chieu_len_tuyen(tuyen, diem):
    """điểm gần nhất trên tuyến: → (chỉ số đoạn i, t∈[0,1], [lat,lon], cách (m))"""
    P = _xy(tuyen)
    q = np.array(C.ll2px(diem[0], diem[1], 18))
    A, B = P[:-1], P[1:]
    AB = B - A
    L2 = (AB ** 2).sum(1)
    t = np.clip(((q - A) * AB).sum(1) / np.maximum(L2, 1e-9), 0, 1)
    Pq = A + AB * t[:, None]
    d = ((Pq - q) ** 2).sum(1)
    i = int(np.argmin(d))
    ll = C.px2ll(Pq[i][0], Pq[i][1], 18)
    return i, float(t[i]), [ll[0], ll[1]], C.khoang_cach_m(diem, ll)


def cat_doan(tuyen, a, b):
    """đoạn tuyến giữa 2 điểm (lat,lon) — chiếu rồi lấy phần giữa, luôn theo hướng a → b"""
    ia, ta, pa, _ = chieu_len_tuyen(tuyen, a)
    ib, tb, pb, _ = chieu_len_tuyen(tuyen, b)
    if (ia, ta) <= (ib, tb):
        mid = tuyen[ia + 1:ib + 1]
        return [pa] + [list(p) for p in mid] + [pb]
    mid = tuyen[ib + 1:ia + 1]
    return ([pb] + [list(p) for p in mid] + [pa])[::-1]


def diem_tai(tuyen, s_m):
    """điểm cách đầu tuyến s_m mét"""
    acc = 0.0
    for i in range(len(tuyen) - 1):
        d = C.khoang_cach_m(tuyen[i], tuyen[i + 1])
        if acc + d >= s_m:
            u = (s_m - acc) / d if d > 0 else 0
            return [tuyen[i][0] + (tuyen[i + 1][0] - tuyen[i][0]) * u, tuyen[i][1] + (tuyen[i + 1][1] - tuyen[i][1]) * u]
        acc += d
    return list(tuyen[-1])


def trong_vung(diem, vong):
    """điểm (lat,lon) nằm trong 1 trong các vòng (even-odd)"""
    x, y = diem[1], diem[0]
    for v in vong:
        inside = False
        n = len(v)
        for i in range(n):
            y0, x0 = v[i]
            y1, x1 = v[(i + 1) % n]
            if (y0 > y) != (y1 > y):
                xi = x0 + (y - y0) * (x1 - x0) / (y1 - y0)
                if x < xi:
                    inside = not inside
        if inside:
            return True
    return False


def diem_ra_khoi_vung(tuyen, vong, tu_diem=None):
    """đi dọc tuyến từ tu_diem (mặc định đầu tuyến), điểm đầu tiên tuyến rời khỏi vùng → [lat, lon] (hoặc None)"""
    i0 = chieu_len_tuyen(tuyen, tu_diem)[0] if tu_diem else 0
    truoc = trong_vung(tuyen[i0], vong)
    for i in range(i0 + 1, len(tuyen)):
        nay = trong_vung(tuyen[i], vong)
        if truoc and not nay:
            a, b = tuyen[i - 1], tuyen[i]
            return [(a[0] + b[0]) / 2, (a[1] + b[1]) / 2]
        truoc = nay
    return None


def rut_gon(tuyen, buoc_m=25.0):
    """lấy mẫu đều theo mét (camera trượt đều, không giật ở chỗ node dày/thưa)"""
    L = C.dai_tuyen_m(tuyen)
    n = max(2, int(L / buoc_m) + 1)
    return [diem_tai(tuyen, L * k / (n - 1)) for k in range(n)]


# ---------------------------------------------------------------- giải quyết mục dia_diem của kế hoạch

def giai_quyet(plan, work, in_ra=True):
    """plan['dia_diem'] = {key: {ten, loai (diem|tuyen|vung), osm?, lat?, lon?, cap? ('huyen_cu' = ranh huyện cũ)}}
    → work/dia_ly/<key>.json; ghi lại osm đã chọn + ứng viên vào plan"""
    gan = None
    kv = plan.get("khu_vuc") or {}
    if kv.get("lat") and kv.get("lon"):
        gan = (float(kv["lat"]), float(kv["lon"]))
    dd = os.path.join(work, "dia_ly")
    os.makedirs(dd, exist_ok=True)
    bao = []
    muc = list((plan.get("dia_diem") or {}).items())
    # mục "giao" (điểm tuyến rời khỏi vùng) tính SAU các mục khác
    muc.sort(key=lambda kv: 1 if (kv[1].get("giao") or kv[1].get("dau_tuyen") or kv[1].get("cuoi_tuyen")) else 0)
    for key, it in muc:
        loai = it.get("loai", "diem")
        ten = it.get("ten") or key
        out_p = os.path.join(dd, key + ".json")
        if it.get("giao"):
            gi = it["giao"]
            try:
                gt = C.jload(os.path.join(dd, gi["tuyen"] + ".json"))
                if gi.get("duong"):
                    p, n_way = giao_duong(gt["tuyen"], gi["duong"], gi["quanh"], float(gi.get("ban_kinh", 0.012)))
                    loi = "không thấy '%s' cắt %s quanh %s (%d way trùng tên)" % (gi["duong"], gi["tuyen"], gi["quanh"], n_way)
                else:
                    gv = C.jload(os.path.join(dd, gi["ra_khoi"] + ".json"))
                    tu = None
                    if gi.get("sau"):
                        tu = C.jload(os.path.join(dd, gi["sau"] + ".json"))["diem"]
                    p = diem_ra_khoi_vung(gt["tuyen"], gv["vong"], tu)
                    loi = "tuyến %s không rời khỏi %s" % (gi["tuyen"], gi["ra_khoi"])
            except Exception as e:
                bao.append((key, ten, "⛔ giao lỗi", str(e)[:100]))
                continue
            if not p:
                bao.append((key, ten, "⛔ không giao", loi))
                continue
            g = {"osm": None, "loai": "diem", "ten": ten, "tags": {}, "diem": p, "tuyen": None, "cac_tuyen": [],
                 "vong": [], "bbox": p + p, "ten_ke_hoach": ten, "loai_ke_hoach": "diem"}
            C.jsave(out_p, g)
            bao.append((key, ten, "giao tuyến/ranh", "%.5f, %.5f" % (p[0], p[1])))
            continue
        if it.get("dau_tuyen") or it.get("cuoi_tuyen"):
            src = it.get("dau_tuyen") or it.get("cuoi_tuyen")
            try:
                tt = C.jload(os.path.join(dd, src + ".json"))["tuyen"]
            except Exception as e:
                bao.append((key, ten, "⛔ thiếu tuyến", "%s: %s" % (src, str(e)[:80])))
                continue
            p = list(tt[0] if it.get("dau_tuyen") else tt[-1])
            C.jsave(out_p, {"osm": None, "loai": "diem", "ten": ten, "tags": {}, "diem": p, "tuyen": None, "cac_tuyen": [],
                            "vong": [], "bbox": p + p, "ten_ke_hoach": ten, "loai_ke_hoach": "diem"})
            bao.append((key, ten, ("đầu" if it.get("dau_tuyen") else "cuối") + " tuyến " + src, "%.5f, %.5f" % (p[0], p[1])))
            continue
        if it.get("lat") is not None and it.get("lon") is not None and not it.get("osm"):
            g = {"osm": None, "loai": "diem", "ten": ten, "tags": {}, "diem": [float(it["lat"]), float(it["lon"])],
                 "tuyen": None, "cac_tuyen": [], "vong": [], "bbox": [float(it["lat"]), float(it["lon"])] * 2}
            C.jsave(out_p, g)
            bao.append((key, ten, "toạ độ tay", "%.5f, %.5f" % (g["diem"][0], g["diem"][1])))
            continue
        osm = it.get("osm")
        if not osm:
            q = ten
            uv = tim(q, gan, n=8)
            if loai == "vung" and it.get("cap") == "huyen_cu":
                uv2 = [u for u in uv if (u.get("value") == "historic")]
                uv = uv2 or uv
            best, s = chon(uv, ten, loai)
            it["_ung_vien"] = [{k: u[k] for k in ("osm", "ten", "key", "value", "mo_ta")} for u in uv[:6]]
            if not best or s < 3:
                bao.append((key, ten, "⛔ KHÔNG TÌM THẤY", "Photon không ra ứng viên hợp — hỏi người dùng toạ độ / tên khác"))
                continue
            osm = best["osm"]
            it["osm"] = osm
            it["_chon"] = "%s · %s=%s · %s" % (best["ten"], best.get("key"), best.get("value"), best.get("mo_ta"))
        try:
            g = hinh_hoc(osm)
        except Exception as e:
            bao.append((key, ten, "⛔ lỗi OSM", str(e)[:120]))
            continue
        if loai == "tuyen" and not g.get("tuyen"):
            bao.append((key, ten, "⛔ không có tuyến", "%s là %s" % (osm, g["loai"])))
            continue
        if loai == "vung" and not g.get("vong"):
            bao.append((key, ten, "⛔ không có ranh", "%s là %s" % (osm, g["loai"])))
            continue
        if loai == "diem" and not g.get("diem") and g.get("tuyen"):
            g["diem"] = _trong_tam(g["tuyen"])
        if loai == "diem" and not g.get("diem"):
            bao.append((key, ten, "⛔ không có điểm", osm))
            continue
        if loai == "tuyen":
            g["tuyen_deu"] = rut_gon(g["tuyen"], 25.0)
            g["dai_m"] = round(C.dai_tuyen_m(g["tuyen"]), 1)
        g["ten_ke_hoach"] = ten
        g["loai_ke_hoach"] = loai
        C.jsave(out_p, g)
        mo = ""
        if loai == "tuyen":
            mo = "tuyến %.1f km, %d điểm, %d nhánh" % (g["dai_m"] / 1000, len(g["tuyen"]), len(g["cac_tuyen"]))
        elif loai == "vung":
            mo = "%d vòng ranh, %s" % (len(g["vong"]), g["tags"].get("boundary", "") + " " + g["tags"].get("admin_level", "")
                                      + (" (ĐỊA GIỚI CŨ, hết hiệu lực %s)" % g["tags"]["end_date"] if g["tags"].get("end_date") else ""))
        else:
            mo = "%.5f, %.5f" % (g["diem"][0], g["diem"][1])
        bao.append((key, ten, osm + " · " + (g["ten"] or "?"), mo))
    if in_ra:
        print("▶ địa điểm:")
        for key, ten, osm, mo in bao:
            print("   %-16s %-28s %-40s %s" % (key, ten[:28], osm[:40], mo))
    return bao


# ---------------------------------------------------------------- tên địa danh quanh camera (C10)

def dia_danh_quanh(lat, lon, r_km=3.0, n=50, the=("place",), chi_cache=False):
    """tên địa danh OSM quanh 1 điểm (Photon reverse): place=city/town/suburb/quarter/village/neighbourhood/hamlet
    (node = toạ độ làng; relation/way = điểm đại diện của phường/xã), tên không chứa chữ số (tránh "Xóm 7" — số trên
    hình phải có trong lời). → [{id, ten, loai, lat, lon}]"""
    key = "v2_%.3f_%.3f_%.1f_%d_%s" % (lat, lon, r_km, n, "-".join(t.replace(":", "") for t in the))
    p = os.path.join(C.cache_dir("dia_danh"), key + ".json")
    if os.path.isfile(p):
        return C.jload(p)
    if chi_cache:
        return []
    params = [("lat", round(lat, 5)), ("lon", round(lon, 5)), ("radius", r_km), ("limit", n)]
    params += [("osm_tag", t) for t in the]
    r = _get(PHOTON_REV, params, timeout=30, lan=3)
    out = []
    for f in r.json().get("features", []):
        pr = f["properties"]
        v = pr.get("osm_value")
        ten = C.nfc((pr.get("name") or "").strip())
        if v not in LOAI_DIA_DANH or not ten or re.search(r"\d", ten):
            continue
        lo, la = f["geometry"]["coordinates"]
        out.append({"id": "%s%d" % (pr.get("osm_type", "N"), int(pr["osm_id"])), "ten": ten, "loai": v,
                    "lat": float(la), "lon": float(lo)})
    C.jsave(p, out)
    time.sleep(0.2)
    return out


def dia_danh_doc(pts, buoc_km=2.0, r_km=3.0, n=50, the=("place",), loai=None, chi_cache=False):
    """lấy mẫu dọc chuỗi [lat, lon] mỗi buoc_km (cả 2 đầu) → gộp, bỏ trùng; lỗi mạng ⇒ bỏ qua (không bịa)"""
    pts = [list(map(float, p)) for p in pts]
    if not pts:
        return []
    mau_ = [pts[0]]
    acc = 0.0
    for i in range(1, len(pts)):
        acc += C.khoang_cach_m(pts[i - 1], pts[i])
        if acc >= buoc_km * 1000:
            mau_.append(pts[i])
            acc = 0.0
    if mau_[-1] is not pts[-1]:
        mau_.append(pts[-1])
    gap = {}
    loi = 0
    for la, lo in mau_:
        try:
            ds = dia_danh_quanh(round(la, 3), round(lo, 3), r_km, n, the, chi_cache)
        except Exception:
            loi += 1
            continue
        for d in ds:
            if loai and d["loai"] not in loai:
                continue
            gap.setdefault(d["id"], d)
    if loi:
        C.canh_bao("tên địa danh: %d/%d lần gọi Photon lỗi — bỏ qua chỗ đó (không bịa tên)" % (loi, len(mau_)))
    return list(gap.values())


def nap(work, key):
    return C.jload(os.path.join(work, "dia_ly", key + ".json"))


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd")
    t = sub.add_parser("tim")
    t.add_argument("q")
    t.add_argument("--gan", default="21.03,105.80", help="lat,lon ưu tiên (mặc định Hà Nội)")
    t.add_argument("--n", type=int, default=8)
    l = sub.add_parser("lay")
    l.add_argument("osm")
    a = ap.parse_args()
    if a.cmd == "tim":
        gan = tuple(float(x) for x in a.gan.split(","))
        for u in tim(a.q, gan, a.n):
            print("%-12s %-32s %s=%s  %s  (%.5f, %.5f)" % (u["osm"], u["ten"][:32], u["key"], u["value"], u["mo_ta"],
                                                          u["lat"], u["lon"]))
    elif a.cmd == "lay":
        g = hinh_hoc(a.osm)
        def tom(k, v):
            if k == "tuyen":
                return "%d điểm" % len(v) if v else None
            if k in ("cac_tuyen", "vong"):
                return "%d nhánh/vòng, %s điểm" % (len(v), [len(x) for x in v]) if v else None
            return v
        print(json.dumps({k: tom(k, v) for k, v in g.items()}, ensure_ascii=False, indent=1))
        if g.get("tuyen"):
            print("dài %.1f km" % (C.dai_tuyen_m(g["tuyen"]) / 1000))
    else:
        ap.print_help()


if __name__ == "__main__":
    main()
