# -*- coding: utf-8 -*-
"""Ranh giới nước / bang từ Natural Earth (GeoJSON) -> đa giác đơn vị Mercator."""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import chung as C


def _rings(geom):
    t = geom.get("type")
    if t == "Polygon":
        return [geom["coordinates"][0]] + [r for r in geom["coordinates"][1:]]
    if t == "MultiPolygon":
        out = []
        for poly in geom["coordinates"]:
            out.extend(poly)
        return out
    return []


def _vong_ngoai(geom):
    """Chỉ lấy vòng ngoài của từng đa giác (bỏ lỗ)."""
    t = geom.get("type")
    if t == "Polygon":
        return [geom["coordinates"][0]]
    if t == "MultiPolygon":
        return [poly[0] for poly in geom["coordinates"]]
    return []


class DiaLy:
    def __init__(self, f_nuoc, f_bang):
        self.nuoc = {}
        self.bang = {}
        self._nap_nuoc(f_nuoc)
        self._nap_bang(f_bang)

    def _nap_nuoc(self, f):
        if not f or not os.path.exists(f):
            return
        with open(f, "r", encoding="utf-8") as fh:
            gj = json.load(fh)
        for ft in gj.get("features", []):
            p = ft.get("properties", {})
            iso = p.get("ISO_A2_EH") or p.get("ISO_A2") or ""
            if not iso or iso == "-99":
                iso = (p.get("WB_A2") or p.get("FIPS_10") or p.get("ADM0_A3") or "")[:2]
            iso = iso.upper()
            if p.get("NAME") == "Kosovo":
                iso = "XK"
            ten = p.get("NAME_LONG") or p.get("NAME") or iso
            rec = {"iso": iso, "ten": ten, "vong": _vong_ngoai(ft["geometry"]),
                   "lon": p.get("LABEL_X"), "lat": p.get("LABEL_Y")}
            if rec["lon"] is None:
                rec["lon"], rec["lat"] = _trong_tam(rec["vong"])
            if iso in self.nuoc:
                # ghép thêm đa giác (vài nước có nhiều feature)
                self.nuoc[iso]["vong"].extend(rec["vong"])
            else:
                self.nuoc[iso] = rec
            for k in ("NAME", "NAME_LONG", "ADMIN", "FORMAL_EN", "NAME_VI", "SOVEREIGNT"):
                v = p.get(k)
                if v:
                    self.nuoc.setdefault("@" + C.ten_khong_dau(v), self.nuoc[iso])

    def _nap_bang(self, f):
        if not f or not os.path.exists(f):
            return
        with open(f, "r", encoding="utf-8") as fh:
            gj = json.load(fh)
        for ft in gj.get("features", []):
            p = ft.get("properties", {})
            ten = p.get("name") or p.get("name_en") or ""
            if not ten:
                continue
            iso = (p.get("iso_a2") or "").upper()
            rec = {"iso": iso, "ten": ten, "vong": _vong_ngoai(ft["geometry"]),
                   "lon": p.get("longitude"), "lat": p.get("latitude")}
            if rec["lon"] is None:
                rec["lon"], rec["lat"] = _trong_tam(rec["vong"])
            self.bang[C.ten_khong_dau(ten)] = rec
            for k in ("name_en", "name_alt", "name_vi", "gn_name"):
                v = p.get(k)
                if v:
                    self.bang.setdefault(C.ten_khong_dau(v), rec)

    def tim(self, ten):
        """Tìm nước (ưu tiên) rồi bang. Trả record hoặc None."""
        if not ten:
            return None
        iso = C.tim_ma_nuoc(ten)
        if iso and iso in self.nuoc:
            return dict(self.nuoc[iso], loai="nuoc")
        k = "@" + C.ten_khong_dau(ten)
        if k in self.nuoc:
            return dict(self.nuoc[k], loai="nuoc")
        kb = C.ten_khong_dau(ten)
        if kb in self.bang:
            return dict(self.bang[kb], loai="bang")
        if kb.startswith("bang "):
            kb2 = kb[5:]
            if kb2 in self.bang:
                return dict(self.bang[kb2], loai="bang")
        return None


def _trong_tam(vong):
    """Trọng tâm xấp xỉ: vòng có diện tích lớn nhất, lấy trung bình đỉnh."""
    best, best_a = None, -1
    for r in vong:
        if len(r) < 3:
            continue
        a = 0.0
        for i in range(len(r) - 1):
            a += r[i][0] * r[i + 1][1] - r[i + 1][0] * r[i][1]
        a = abs(a)
        if a > best_a:
            best, best_a = r, a
    if not best:
        return 0.0, 0.0
    xs = [p[0] for p in best]
    ys = [p[1] for p in best]
    return sum(xs) / len(xs), sum(ys) / len(ys)


def vong_den_px(vong, z, x0, y0, rong=0, cao=0):
    """Các vòng lon/lat -> danh sách mảng (N,2) px trong ROI mức z gốc (x0,y0), ROI rộng×cao px.
    Xử lý quấn vòng quanh kinh tuyến 180; bỏ vòng nằm hẳn ngoài ROI (nếu biết cao)."""
    import numpy as np
    s = 256 * (1 << z)
    cx = x0 + rong / 2.0
    le = 64
    out = []
    for r in vong:
        if len(r) < 3:
            continue
        arr = np.asarray(r, dtype=np.float64)
        lon, lat = arr[:, 0], arr[:, 1]
        lat = np.clip(lat, -85.05, 85.05)
        x = (lon + 180.0) / 360.0 * s
        sl = np.sin(np.radians(lat))
        y = (0.5 - np.log((1 + sl) / (1 - sl)) / (4 * np.pi)) * s
        xm = float(x[0])
        best_k, best_d = 0, abs(xm - cx)
        for k in (-1, 1):
            dk = abs(xm + k * s - cx)
            if dk < best_d:
                best_k, best_d = k, dk
        x = x + best_k * s - x0
        y = y - y0
        if cao > 0:
            if x.max() < -le or x.min() > rong + le or y.max() < -le or y.min() > cao + le:
                continue
        out.append(np.stack([x, y], 1))
    return out


def diem_den_px(lon, lat, z, x0, y0, rong=0):
    import math
    s = 256 * (1 << z)
    lat = max(-85.05, min(85.05, lat))
    x = (lon + 180.0) / 360.0 * s
    sl = math.sin(math.radians(lat))
    y = (0.5 - math.log((1 + sl) / (1 - sl)) / (4 * math.pi)) * s
    cx = x0 + rong / 2.0
    for k in (-1, 1):
        if abs(x + k * s - cx) < abs(x - cx):
            x += k * s
    return x - x0, y - y0
