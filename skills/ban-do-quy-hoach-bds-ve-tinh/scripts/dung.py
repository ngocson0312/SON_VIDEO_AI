# -*- coding: utf-8 -*-
"""Bước dựng: ke_hoach.json + dia_ly/*.json → video 1080x1920 30 fps: nền vệ tinh Esri theo camera từng cảnh,
hành lang / tuyến / vùng / ghim / thước đo, thẻ hook, thẻ đầu đề, thẻ tài liệu, logo, nguồn, CTA, SUB KARAOKE nguyên văn,
giọng −14 LUFS, mã hoá hình ĐÚNG 1 lần.

    python -I scripts/dung.py --work <dir> [--out <mp4>] [--preset medium] [--crf 18]
    python -I scripts/dung.py --work <dir> --xem-truoc 1,20.5,45     # chỉ ra ảnh work/xem_truoc_*.jpg (soát camera)
    python -I scripts/dung.py --work <dir> --khong-mang               # chỉ dùng ô ảnh đã cache
"""
import argparse
import io
import math
import os
import re
import shutil
import subprocess
import sys
import time

import cv2
import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import am_thanh as A
import ban_do as B
import chung as C
import cta as CT
import dia_ly as G
import diem_nhan as DN
import do_hoa as D
from chung import W, H, FPS, clamp, ramp, smooth

LOAI_CANH = ("bay_tuyen", "ban_do_tong", "to_vung", "diem", "thuoc_do", "tinh", "cta")


def tien_do(t, dur, ease=0.6):
    """0→1 đều, mềm 2 đầu (ease giây)"""
    if dur <= 0:
        return 1.0
    e = min(ease, dur / 2)
    if t <= 0:
        return 0.0
    if t >= dur:
        return 1.0
    # quãng đường theo vận tốc hình thang: tăng tốc e, đều, giảm tốc e
    tong = dur - e            # diện tích vận tốc chuẩn hoá
    if t < e:
        s = t * t / (2 * e)
    elif t < dur - e:
        s = e / 2 + (t - e)
    else:
        u = dur - t
        s = tong - u * u / (2 * e)
    return clamp(s / tong)


class NguonDiaLy:
    def __init__(self, work):
        self.work = work
        self.cache = {}

    def lay(self, key):
        if key not in self.cache:
            p = os.path.join(self.work, "dia_ly", key + ".json")
            if not os.path.isfile(p):
                C.die("thiếu dia_ly/%s.json — chạy `run.py dia-diem --work …` trước (hoặc địa điểm chưa khai trong ke_hoach.dia_diem)" % key)
            self.cache[key] = C.jload(p)
        return self.cache[key]

    def diem(self, x):
        """key hoặc [lat, lon] → [lat, lon]"""
        if isinstance(x, (list, tuple)) and len(x) == 2:
            return [float(x[0]), float(x[1])]
        g = self.lay(x)
        if g.get("diem"):
            return g["diem"]
        if g.get("tuyen"):
            return g["tuyen"][len(g["tuyen"]) // 2]
        C.die("địa điểm %s không có toạ độ" % x)

    def ten(self, x, mac_dinh=""):
        if isinstance(x, str):
            g = self.lay(x)
            return g.get("ten_ke_hoach") or g.get("ten") or mac_dinh
        return mac_dinh


# ---------------------------------------------------------------- các cảnh

class Canh:
    loai = "tinh"
    hard_cut = False

    def __init__(self, it, ctx):
        self.it = it
        self.ctx = ctx
        self.t0, self.t1 = float(it["tu"]), float(it["den"])
        self.dur = self.t1 - self.t0
        self.loi = it.get("_loi", "")
        dd = it.get("dau_de")
        if dd is None and it.get("tieu_de") and self.loai != "ban_do_tong":
            dd = [{"t": self.t0, "tieu_de": it["tieu_de"], "phu": it.get("phu")}]
        self.dd = [(float(x.get("t", self.t0)), D.TheDauDe(x["tieu_de"], x.get("phu"))) for x in (dd or [])
                   if x.get("tieu_de")]
        self.dd.sort(key=lambda x: x[0])
        # C10: điểm nhấn khai tay + tên địa danh OSM quanh camera + bản đồ định vị nhỏ
        self.nm = DN.NhanManh(it.get("nhan_manh"), ctx["dl"], self.t0, self.t1)
        self.dia_danh = None
        self.dinh_vi = None
        self.chiem = DN.Chiem()

    def tao_dia_danh(self, pts, buoc_km, r_km, the=("place",), loai=None, bo_ten=(), mac_dinh=True, **kw):
        """tên làng/xã/thị trấn THẬT quanh đường camera (OSM place); tắt: canh.dia_danh=false / cai_dat.dia_danh=false"""
        it, cd = self.it, self.ctx["cai_dat"]
        if not it.get("dia_danh", mac_dinh) or not cd.get("dia_danh", True):
            return None
        ds = G.dia_danh_doc(pts, buoc_km, r_km, 50, the, loai, chi_cache=not self.ctx.get("mang", True))
        bo = list(bo_ten) + list(it.get("dia_danh_bo", []) or []) + list(cd.get("dia_danh_bo", []) or [])
        return DN.DiaDanh(ds, bo, **kw) if ds else None

    def tao_dinh_vi(self, mac_dinh):
        """bản đồ định vị nhỏ góc dưới trái: canh.dinh_vi = true (tuyến của cảnh) | "<key tuyến>" | false"""
        it, cd = self.it, self.ctx["cai_dat"]
        v = it.get("dinh_vi", mac_dinh)
        if not v or not cd.get("dinh_vi", True):
            return None
        key = v if isinstance(v, str) else it.get("tuyen")
        if not key:
            return None
        doan = it.get("dinh_vi_doan") or cd.get("dinh_vi_doan")
        ck = (key, tuple(doan) if doan else None)
        cache = self.ctx.setdefault("_dinh_vi", {})
        if ck not in cache:
            dl = self.ctx["dl"]
            full = dl.lay(key)["tuyen"]
            if doan:
                full = G.cat_doan(full, dl.diem(doan[0]), dl.diem(doan[1]))
            cache[ck] = DN.DinhVi(full, it.get("dinh_vi_ten") or cd.get("dinh_vi_ten") or dl.ten(key, "Vị trí"))
        return cache[ck]

    def vi_tri(self, t, cam):
        return cam.lat, cam.lon

    def a_dia_danh(self, t):
        return 1.0 - 0.6 * self.nm.dang_ngam(t)

    def ve_lop(self, frame, t, nen):
        """thứ tự lớp: bản đồ của cảnh → nhấn mạnh khai tay → tên địa danh phụ (né chữ đã đặt) → định vị → đầu đề"""
        cam = self.cam(t)
        vc = self.ctx.get("vung_cam")
        self.chiem = DN.Chiem(vc(t, self) if vc else [DN.DAI_SUB])
        if self.dinh_vi is not None and t >= self.t0 + 0.3:
            self.chiem.dat(self.dinh_vi.rect())
        self.lop(frame, t, cam)
        self.nm.ve(frame, t, cam, self.chiem)
        if self.dia_danh is not None:
            self.dia_danh.ve(frame, t, cam, self.chiem, self.a_dia_danh(t))
        if self.dinh_vi is not None:
            la, lo = self.vi_tri(t, cam)
            self.dinh_vi.ve(frame, nen, t - self.t0 - 0.3, la, lo)
        self.ve_dau_de(frame, t)

    def ve_dau_de(self, frame, t):
        """thẻ đầu đề navy trên cùng: hiện mờ 0,2 s ở mốc t, đổi thẻ hoà 0,2 s"""
        k = -1
        for i, (ti, _) in enumerate(self.dd):
            if t >= ti:
                k = i
        if k < 0:
            return
        a = ramp(t, self.dd[k][0], 0.2)
        if k > 0 and a < 1:
            self.dd[k - 1][1].ve(frame, 1 - a)
        self.dd[k][1].ve(frame, a)

    def cam(self, t):
        raise NotImplementedError

    def nen(self, t, nen):
        return self.cam(t).render(nen)

    def lop(self, frame, t, cam):
        pass

    def sfx(self):
        return []

    def o_can(self, nen):
        ks = set()
        n = max(2, int(self.dur / 0.25) + 1)
        for i in range(n):
            t = self.t0 + self.dur * i / (n - 1)
            ks |= self.cam(t).o_can(nen)
        if self.dinh_vi is not None:
            ks |= self.dinh_vi.o_can(nen)
        return ks


class Tinh(Canh):
    loai = "tinh"

    def __init__(self, it, ctx):
        super().__init__(it, ctx)
        p = ctx["dl"].diem(it.get("diem") or [it["lat"], it["lon"]])
        self.p, self.zf = p, float(it.get("zoom", 16.0))
        self.them = float(it.get("zoom_them", 0.06))

    def cam(self, t):
        return B.Camera(self.p[0], self.p[1], self.zf + self.them * smooth((t - self.t0) / max(self.dur, 0.1)))


class BayTuyen(Canh):
    """trượt dọc tuyến (sông/đường) ở zoom gần; hành lang ±N m vàng; tuỳ chọn vẽ tim tuyến"""
    loai = "bay_tuyen"

    def __init__(self, it, ctx):
        super().__init__(it, ctx)
        dl = ctx["dl"]
        g = dl.lay(it["tuyen"])
        self.g = g
        full = g.get("tuyen_deu") or g["tuyen"]
        seg = full
        if it.get("tu_diem") is not None and it.get("den_diem") is not None:
            seg = G.cat_doan(full, dl.diem(it["tu_diem"]), dl.diem(it["den_diem"]))
        elif it.get("tu_diem") is not None:
            a = dl.diem(it["tu_diem"])
            i = G.chieu_len_tuyen(full, a)[0]
            seg = full[i:] if not it.get("nguoc") else full[:i + 1][::-1]
        if it.get("nguoc") and it.get("den_diem") is not None:
            seg = seg[::-1]
        L = C.dai_tuyen_m(seg)
        toc = float(it.get("toc_do", 45.0))
        can = toc * self.dur
        if L > can + 1:
            # chỉ bay quãng vừa thời lượng (từ đầu đoạn; 'giua': lấy khúc giữa)
            dau = (L - can) / 2 if it.get("giua") else 0.0
            pts = [G.diem_tai(seg, dau + can * k / 120) for k in range(121)]
            seg = pts
        self.zf = float(it.get("zoom", 16.4))
        self.bay = B.DuongBay(seg, self.zf, lam_muot=int(it.get("lam_muot", 10)))
        self.hanh_lang = it.get("hanh_lang_m")
        self.t_hl = float(it.get("hanh_lang_tu", self.t0))
        self.ve_tuyen = bool(it.get("ve_tuyen", False))
        self.thuoc = it.get("thuoc")
        self.tuyen_np = np.asarray(g["tuyen"], dtype=np.float64)
        self.nhan = []
        for n in it.get("nhan", []) or []:
            self.nhan.append((dl.diem(n.get("diem") or [n["lat"], n["lon"]]), n.get("text") or dl.ten(n.get("diem"))))
        r_km = clamp(960 * C.m_per_px(self.bay.pts[0][0], self.zf) / 1000 * 1.15, 1.5, 6.0)
        self.dia_danh = self.tao_dia_danh(self.bay.pts.tolist(), max(0.8, r_km * 0.8), r_km,
                                          bo_ten=[x for _, x in self.nhan])
        self.dinh_vi = self.tao_dinh_vi((g.get("dai_m") or C.dai_tuyen_m(g["tuyen"])) > 8000)
        tt = it.get("ten_tuyen", True)
        self.ten_tuyen = (tt if isinstance(tt, str) else dl.ten(it["tuyen"], "")) if tt else ""

    def cam(self, t):
        return self.bay.tai(tien_do(t - self.t0, self.dur, float(self.it.get("em", 0.8))))

    def sfx(self):
        if self.thuoc:
            return [{"t": float(self.thuoc.get("t", self.t0)) + 0.7, "file": "pop.mp3", "muc": "nhe"}]
        return []

    def lop(self, frame, t, cam):
        P = cam.chieu_mang(self.tuyen_np)
        # chỉ giữ điểm quanh màn hình (tránh vẽ cả 245 km mỗi khung)
        m = (P[:, 0] > -800) & (P[:, 0] < W + 800) & (P[:, 1] > -800) & (P[:, 1] < H + 800)
        if m.any():
            idx = np.where(m)[0]
            a, b = max(0, idx[0] - 2), min(len(P), idx[-1] + 3)
            Pv = P[a:b]
            if self.ve_tuyen:
                B.ve_duong(frame, Pv, C.XANH_LO, 5, vien=(10, 30, 50), day_vien=1, alpha=0.55)
                if self.it.get("dong_chay", True):
                    DN.ve_dong_chay(frame, Pv, t - self.t0, toc=80, dash=20, gap=58, mau_=(236, 248, 255), day=3)
            if self.hanh_lang:
                d_px = float(self.hanh_lang) / 2 / cam.m_per_px()
                a_hl = ramp(t, self.t_hl, 0.5)
                if a_hl > 0:
                    B.ve_hanh_lang(frame, Pv, d_px, C.VANG, 3, 0.10, a_hl)
        for p, text in self.nhan:
            x, y = cam.chieu(p[0], p[1])
            if -100 < x < W + 100 and -100 < y < H + 100:
                DN.ve_song(frame, x, y, t - self.t0 - 0.3, C.TRANG, r0=8, r1=62, chu_ky=1.6, day=3, alpha=0.9)
                self.chiem.dat(B.nhan_diem(frame, x, y, text, 28))
        if self.thuoc and m.any():
            u = smooth(ramp(t, float(self.thuoc.get("t", self.t0)), 0.7))
            rong = float(self.thuoc.get("rong_m", self.hanh_lang or 300))
            ab = B.thuoc_ngang(Pv, rong / 2 / cam.m_per_px())
            if u > 0 and ab:
                (x0, y0), (x1, y1) = ab
                cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
                nh = self.thuoc.get("nhan") if u >= 0.999 else None
                dy = -46
                if nh:
                    w_ = B.nhan_pill(nh, "xbold", 40, C.VANG, C.NAVY).shape[1] / 2
                    hop = lambda d: (cx - w_, cy + d - 40, cx + w_, cy + d + 40)
                    for p_ in (self.nhan or []):
                        xp, yp = cam.chieu(p_[0][0], p_[0][1])
                        self.chiem.dat((xp - 66, yp - 66, xp + 66, yp + 66))
                    if getattr(self, "_dy_thuoc", -46) == 52 or (self.chiem.trung(hop(-46), 4)
                                                                 and not self.chiem.trung(hop(52), 4)):
                        dy = 52
                        self._dy_thuoc = 52          # đã xuống dưới thì giữ, không nhảy lên xuống giữa cảnh
                    self.chiem.dat(hop(dy))
                B.ve_thuoc(frame, (cx + (x0 - cx) * u, cy + (y0 - cy) * u), (cx + (x1 - cx) * u, cy + (y1 - cy) * u),
                           nh, dy_nhan=dy)
        if self.ten_tuyen and m.any():
            DN.ve_ten_tuyen(frame, Pv, self.ten_tuyen, C.XANH_LO, self.chiem, t - self.t0 - 0.2)


class BanDoTong(Canh):
    """bản đồ tổng: nền tối, tuyến xanh lơ, từng đoạn A→B vẽ vàng chạy 2 s + nhãn 2 đầu + thẻ đầu đề đổi theo đoạn"""
    loai = "ban_do_tong"

    def __init__(self, it, ctx):
        super().__init__(it, ctx)
        dl = ctx["dl"]
        g = dl.lay(it["tuyen"])
        self.tuyen = g["tuyen"]
        self.tuyen_np = np.asarray(self.tuyen, dtype=np.float64)
        bb = g["bbox"]
        if it.get("bbox_doan"):
            a_, b_ = it["bbox_doan"]
            sd = G.cat_doan(self.tuyen, dl.diem(a_), dl.diem(b_))
            bb = [min(p[0] for p in sd), min(p[1] for p in sd), max(p[0] for p in sd), max(p[1] for p in sd)]
        if it.get("bbox"):
            bb = it["bbox"]
        vy = tuple(it.get("vung_y", (0.10, 0.70)))
        self.cam_full = B.Camera.vua_bbox(bb, le=float(it.get("le", 0.10)), vung_y=vy)
        self.doan = []
        for i_d, d in enumerate(it.get("doan", [])):
            a, b = dl.diem(d["tu_diem"]), dl.diem(d["den_diem"])
            seg = G.cat_doan(self.tuyen, a, b)
            lats, lons = [p[0] for p in seg], [p[1] for p in seg]
            bbd = [min(lats), min(lons), max(lats), max(lons)]
            cam = B.Camera.vua_bbox(bbd, le=float(d.get("le", 0.28)), vung_y=tuple(d.get("vung_y", (0.14, 0.68))))
            if d.get("zoom_toi_da") is not None:
                cam = B.Camera(cam.lat, cam.lon, min(cam.zf, float(d["zoom_toi_da"])))
            self.doan.append({"t": float(d["t"]), "seg": np.asarray(seg, dtype=np.float64), "a": a, "b": b,
                              "nhan": d.get("nhan", ""), "phu": d.get("phu", it.get("phu")),
                              "nhan_dau": d.get("nhan_dau") if d.get("nhan_dau") is not None else dl.ten(d["tu_diem"], "A"),
                              "nhan_cuoi": d.get("nhan_cuoi") if d.get("nhan_cuoi") is not None else dl.ten(d["den_diem"], "B"),
                              "nhan_dau_tren": d.get("nhan_dau_tren", True), "nhan_cuoi_tren": d.get("nhan_cuoi_tren", False),
                              "cam": cam,
                              "dai_ve": float(d.get("dai_ve", 2.0)), "zoom_vao": bool(d.get("zoom_vao", True)),
                              "mau": DN.mau(d.get("mau", it.get("mau")), i_d),
                              "t_xong": float(d["t"]) + 0.3 + float(d.get("dai_ve", 2.0)),
                              "huy_hieu": d.get("huy_hieu"),
                              "huy_hieu_tu": float(d["huy_hieu_tu"]) if d.get("huy_hieu_tu") is not None else
                              float(d["t"]) + 0.3 + float(d.get("dai_ve", 2.0))})
        self.diem_nhan = []
        for n in it.get("nhan", []) or []:
            self.diem_nhan.append((dl.diem(n.get("diem") or [n["lat"], n["lon"]]), n.get("text") or dl.ten(n.get("diem"))))
        self.toi = float(it.get("toi", 0.62))
        lat0, lon0, lat1, lon1 = bb
        doc = [p for p in self.tuyen if lat0 - 0.02 <= p[0] <= lat1 + 0.02 and lon0 - 0.02 <= p[1] <= lon1 + 0.02]
        bo = [x["nhan_dau"] for x in self.doan] + [x["nhan_cuoi"] for x in self.doan] + [t_ for _, t_ in self.diem_nhan]
        self.dia_danh = self.tao_dia_danh(doc or self.tuyen, 6.0, 8.0, the=("place:city", "place:town"),
                                          bo_ten=bo, toi_da=7, co=24, cach=200, a_max=0.85)
        # thẻ đầu đề: thẻ chung từ đầu cảnh, mỗi đoạn đổi thẻ ở mốc t; 'phu_tu' = dòng phụ (số liệu) hiện đúng lúc đọc
        dd = []
        if it.get("tieu_de"):
            dd.append((self.t0, D.TheDauDe(it["tieu_de"], it.get("phu"))))
        for d, raw in zip(self.doan, it.get("doan", [])):
            if not d["nhan"]:
                continue
            if raw.get("phu_tu") is not None and d["phu"]:
                dd.append((d["t"], D.TheDauDe(d["nhan"], None)))
                dd.append((float(raw["phu_tu"]), D.TheDauDe(d["nhan"], d["phu"])))
            else:
                dd.append((d["t"], D.TheDauDe(d["nhan"], d["phu"])))
        self.dd = sorted(dd, key=lambda x: x[0])

    def _active(self, t):
        k = -1
        for i, d in enumerate(self.doan):
            if t >= d["t"]:
                k = i
        return k

    def cam(self, t):
        k = self._active(t)
        if k < 0 or not self.doan[k]["zoom_vao"]:
            return self.cam_full
        d = self.doan[k]
        prev = self.cam_full if k == 0 or not self.doan[k - 1]["zoom_vao"] else self.doan[k - 1]["cam"]
        return B.noi_suy(prev, d["cam"], smooth(ramp(t, d["t"], 0.6)))

    def nen(self, t, nen):
        return B.lam_toi(self.cam(t).render(nen), self.toi, 0.7)

    def lop(self, frame, t, cam):
        P = cam.chieu_mang(self.tuyen_np)
        B.ve_duong(frame, P, C.XANH_LO, 4, vien=(10, 40, 60), day_vien=1, glow=0)
        k = self._active(t)
        for i, d in enumerate(self.doan):
            if i > k:
                break
            u = ramp(t, d["t"] + 0.3, d["dai_ve"])
            if u <= 0:
                continue
            S = cam.chieu_mang(d["seg"])
            part, head = B.doan_theo_tien_do(S, u)
            if i < k:
                B.ve_duong(frame, part, d["mau"], 7, vien=(40, 30, 0), day_vien=1, alpha=0.55)
                if d["huy_hieu"] and t >= d["huy_hieu_tu"]:
                    _, mid = B.doan_theo_tien_do(S, 0.5)
                    if mid is not None and not self.chiem.trung(DN.hop_huy_hieu(mid[0], mid[1], d["huy_hieu"]), 4):
                        self.chiem.dat(DN.ve_huy_hieu(frame, mid[0], mid[1], 9.0, d["huy_hieu"], alpha=0.8))
                continue
            B.ve_duong(frame, part, d["mau"], 9, vien=(40, 30, 0), day_vien=1, glow=10)
            xa, ya = S[0]
            DN.ve_song(frame, xa, ya, t - d["t"] - 0.3, d["mau"], r0=10, r1=72, chu_ky=1.4, day=3)
            if u >= 0.999:
                DN.ve_dong_chay(frame, S, t - d["t_xong"], toc=110, dash=18, gap=46, mau_=(255, 255, 255), day=3)
            if d["nhan_dau"]:
                self.chiem.dat(B.nhan_diem(frame, xa, ya, d["nhan_dau"], 26, tren=d["nhan_dau_tren"]))
            if head is not None and u < 0.999:
                B.ve_cham(frame, head[0], head[1], 9)
            if u >= 0.999:
                xb, yb = S[-1]
                tx = t - d["t_xong"]
                DN.ve_song(frame, xb, yb, tx, d["mau"], r0=10, r1=80, chu_ky=1.4, day=3)
                self.chiem.dat(DN.ve_ghim_roi(frame, xb, yb, tx, d["mau"], 0.9))
                if d["nhan_cuoi"]:
                    tren = d["nhan_cuoi_tren"]
                    self.chiem.dat(B.nhan_diem(frame, xb, yb - (58 if tren else 0), d["nhan_cuoi"], 26, tren=tren))
            if d["huy_hieu"] and t >= d["huy_hieu_tu"]:
                _, mid = B.doan_theo_tien_do(S, 0.5)
                if mid is not None:
                    self.chiem.dat(DN.ve_huy_hieu(frame, mid[0], mid[1], t - d["huy_hieu_tu"], d["huy_hieu"]))
        if k < 0:
            for p, text in self.diem_nhan:
                x, y = cam.chieu(p[0], p[1])
                self.chiem.dat(B.nhan_diem(frame, x, y, text, 24))

    def sfx(self):
        ev = [{"t": self.t0, "file": "ding.mp3", "muc": "nhe", "chot": True}]
        for d in self.doan:
            ev.append({"t": d["t"] + 0.3, "file": "quick-swoosh.mp3", "muc": "nhe"})
        return ev


class ToVung(Canh):
    """tô ranh xã/huyện (vàng mờ + viền) + nhãn pill ở tâm; camera vừa hộp bao, đẩy vào chậm"""
    loai = "to_vung"

    def __init__(self, it, ctx):
        super().__init__(it, ctx)
        dl = ctx["dl"]
        self.vung = []
        lats, lons = [], []
        nhan = it.get("nhan") or {}
        for key in it["vung"]:
            g = dl.lay(key)
            rings = [np.asarray(v, dtype=np.float64) for v in g["vong"]]
            for v in g["vong"]:
                lats += [p[0] for p in v]
                lons += [p[1] for p in v]
            txt = nhan.get(key) if isinstance(nhan, dict) else None
            if txt is None:
                txt = re.sub(r"^(Huyện|Xã|Phường|Thị xã|Quận|Thị trấn)\s+", "", g.get("ten_ke_hoach") or g.get("ten") or key, flags=re.I)
            self.vung.append({"rings": rings, "tam": g.get("diem"), "nhan": txt,
                              "mau": DN.mau(it.get("mau"), len(self.vung))})
        bb = [min(lats), min(lons), max(lats), max(lons)]
        self.cam0 = B.Camera.vua_bbox(bb, le=float(it.get("le", 0.14)), vung_y=tuple(it.get("vung_y", (0.10, 0.72))))
        self.them = float(it.get("zoom_them", 0.06))
        self.mau = tuple(it.get("mau", C.VANG))
        self.co_nhan = it.get("co_nhan", True)
        hien = it.get("hien") or {}
        for i, (key, v) in enumerate(zip(it["vung"], self.vung)):
            v["t"] = float(hien.get(key, self.t0 + 0.12 * i))
        self.tuyen_np = np.asarray(dl.lay(it["tuyen"])["tuyen"], dtype=np.float64) if it.get("tuyen") else None

    def cam(self, t):
        return B.Camera(self.cam0.lat, self.cam0.lon, self.cam0.zf + self.them * smooth((t - self.t0) / max(self.dur, 0.1)))

    def lop(self, frame, t, cam):
        for i, v in enumerate(self.vung):
            if t <= v["t"]:
                continue
            px = [cam.chieu_mang(r) for r in v["rings"]]
            af = smooth(ramp(t, v["t"] + 0.25, 0.45))
            if af > 0:
                B.ve_vung(frame, px, v["mau"], alpha_to=0.24, vien=None, day_vien=0, alpha=af)
            uo = smooth(ramp(t, v["t"], 0.7))
            for r_ in px:
                DN.ve_vien_chay(frame, r_, uo, v["mau"], 4)
        if self.tuyen_np is not None:
            B.ve_duong(frame, cam.chieu_mang(self.tuyen_np), C.XANH_LO, 5, vien=(10, 40, 60), day_vien=1)
        for i, v in enumerate(self.vung):
            if t <= v["t"] or not v["tam"]:
                continue
            x, y = cam.chieu(v["tam"][0], v["tam"][1])
            DN.ve_song(frame, x, y, t - v["t"] - 0.1, v["mau"], r0=14, r1=110, chu_ky=1.5, lap=False)
            if self.co_nhan:
                self.chiem.dat(DN.ve_pop(frame, DN.pill_cham(v["nhan"], v["mau"], 30), x, y, t - v["t"] - 0.25))

    def sfx(self):
        return [{"t": v["t"], "file": "pop.mp3", "muc": "nhe"} for v in self.vung]


class Diem(Canh):
    """đẩy vào 1 điểm (cầu, đập, công trình): zoom_tu → zoom trong t_zoom giây, ghim + nhãn"""
    loai = "diem"

    def __init__(self, it, ctx):
        super().__init__(it, ctx)
        dl = ctx["dl"]
        self.p = dl.diem(it.get("diem") or [it["lat"], it["lon"]])
        self.zf, self.z0 = float(it.get("zoom", 17.2)), float(it.get("zoom_tu", 15.4))
        self.t_zoom = float(it.get("t_zoom", 1.6))
        self.text = it.get("nhan") if it.get("nhan") is not None else dl.ten(it.get("diem"), "")
        self.phu = it.get("phu_nhan")
        self.mau = DN.mau(it.get("mau"), 0)
        self.t_ghim = self.t0 + max(0.25, self.t_zoom * 0.55)
        self.ngam = bool(it.get("ngam", True))
        r_km = clamp(960 * C.m_per_px(self.p[0], self.zf) / 1000 * 1.25, 1.0, 4.0)
        self.dia_danh = self.tao_dia_danh([self.p], 1.0, r_km, bo_ten=[self.text])
        self.dinh_vi = self.tao_dinh_vi(False)

    def cam(self, t):
        u = smooth(ramp(t, self.t0, self.t_zoom))
        return B.Camera(self.p[0], self.p[1], self.z0 + (self.zf - self.z0) * u)

    def vi_tri(self, t, cam):
        return self.p

    def a_dia_danh(self, t):
        return 1.0 - 0.55 * smooth(ramp(t, self.t0 + 0.15, 0.45)) if self.ngam else 1.0

    def lop(self, frame, t, cam):
        x, y = cam.chieu(self.p[0], self.p[1])
        if self.ngam:
            DN.ve_ngam(frame, x, y, t - self.t0 - 0.15, float(self.it.get("ban_kinh_ngam", 190)), self.mau)
        tg = t - self.t_ghim
        DN.ve_song(frame, x, y, tg, self.mau, r0=12, r1=105, chu_ky=1.5)
        self.chiem.dat(DN.ve_ghim_roi(frame, x, y, tg, self.mau, 1.15))
        if self.text:
            self.chiem.dat(DN.ve_chu_thich(frame, x, y - 58, tg - 0.35, self.text, self.phu, self.mau,
                                           self.it.get("huong_nhan")))

    def sfx(self):
        return [{"t": self.t0 + 0.25, "file": "pop.mp3", "muc": "chinh"}]


class ThuocDo(Canh):
    """thước đo giữa 2 điểm: vạch trắng vẽ 0,8 s + nhãn '≈ N M'"""
    loai = "thuoc_do"

    def __init__(self, it, ctx):
        super().__init__(it, ctx)
        dl = ctx["dl"]
        self.a, self.b = dl.diem(it["a"]), dl.diem(it["b"])
        lats, lons = sorted([self.a[0], self.b[0]]), sorted([self.a[1], self.b[1]])
        self.cam0 = B.Camera.vua_bbox([lats[0], lons[0], lats[1], lons[1]], le=float(it.get("le", 0.45)),
                                      vung_y=tuple(it.get("vung_y", (0.15, 0.70))), z_max=float(it.get("zoom_toi_da", 17.6)))
        self.them = float(it.get("zoom_them", 0.05))
        met = C.khoang_cach_m(self.a, self.b)
        self.text = it.get("nhan") or ("≈ %d M" % int(round(met / 10.0) * 10))

    def cam(self, t):
        return B.Camera(self.cam0.lat, self.cam0.lon, self.cam0.zf + self.them * smooth((t - self.t0) / max(self.dur, 0.1)))

    def lop(self, frame, t, cam):
        u = smooth(ramp(t, self.t0 + 0.2, 0.8))
        if u <= 0:
            return
        ax, ay = cam.chieu(self.a[0], self.a[1])
        bx, by = cam.chieu(self.b[0], self.b[1])
        ex, ey = ax + (bx - ax) * u, ay + (by - ay) * u
        B.ve_thuoc(frame, (ax, ay), (ex, ey), self.text if u >= 0.999 else None)


class Cta(Canh):
    """CTA cuối: clip/ảnh của kênh (kenh.cta) phủ kín khung, hoặc thẻ NÚT + ICON tự dựng (cta.CtaNut, C11) trên khung
    cuối cảnh trước làm mờ. Vào cắt cứng. KHÔNG SFX (C6)."""
    loai = "cta"
    hard_cut = True

    def __init__(self, it, ctx):
        super().__init__(it, ctx)
        kenh = ctx["kenh"]
        self.frames, self.img, self.tinh = None, None, None
        src = it.get("file") or kenh.get("cta")
        if src:
            p = ctx["tim_file"](src)
            if os.path.splitext(p)[1].lower() in (".mp4", ".mov", ".m4v", ".mkv", ".webm"):
                n = int(self.dur * FPS) + 1
                vf = "fps=%d,scale=%d:%d:force_original_aspect_ratio=increase,crop=%d:%d" % (FPS, W, H, W, H)
                r = subprocess.run([C.ffbin("ffmpeg"), "-v", "error", "-i", p, "-an", "-vf", vf, "-frames:v", str(n),
                                    "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True)
                k = len(r.stdout) // (W * H * 3)
                self.frames = np.frombuffer(r.stdout[:k * W * H * 3], np.uint8).reshape(k, H, W, 3)
            else:
                self.img = np.asarray(C.cover(Image.open(p).convert("RGB"), W, H))
        if self.frames is None and self.img is None:
            self.tinh = CT.CtaNut(kenh, self.dur, it, ctx.get("tim_file"))

    def _khung_truoc(self, nen):
        ds = [c for c in (self.ctx.get("canh") or []) if c is not self and c.t0 < self.t0]
        if not ds:
            return None
        p = ds[-1]
        t = self.t0 - 1.0 / FPS
        fr = p.nen(t, nen)
        p.ve_lop(fr, t, nen)
        return fr

    def cam(self, t):
        return None

    def o_can(self, nen):
        return set()

    def nen(self, t, nen):
        fr = np.zeros((H, W, 3), np.uint8)
        tl = t - self.t0
        if self.frames is not None:
            i = min(len(self.frames) - 1, max(0, int(tl * FPS)))
            fr[:] = self.frames[i]
        elif self.img is not None:
            fr[:] = self.img
        else:
            if self.tinh.bg is None:
                self.tinh.dat_nen(self._khung_truoc(nen))
            self.tinh.ve(fr, tl)
        return fr

    def sfx(self):
        return []          # góp ý 04/11/2026: chime cuối nghe chói ⇒ CTA KHÔNG có SFX


LOAI = {"bay_tuyen": BayTuyen, "ban_do_tong": BanDoTong, "to_vung": ToVung, "diem": Diem, "thuoc_do": ThuocDo,
        "tinh": Tinh, "cta": Cta}


# ---------------------------------------------------------------- sub nguyên văn (gom cụm bằng nns-auto-sub)

def gop_so(words):
    """Whisper tách '6.000' thành '6' + '.000' ⇒ gộp lại; cũng gộp '3' + '.002'"""
    out = []
    for w in words:
        t = w["w"]
        if out and re.fullmatch(r"\.\d{3}[.,;:!?]*", t) and re.fullmatch(r"\d{1,3}", out[-1]["w"]):
            out[-1]["w"] = out[-1]["w"] + t
            out[-1]["end"] = max(out[-1]["end"], w["end"])
            continue
        out.append(dict(w))
    return out


def thay_cum(words, sua):
    """sua_chu {"cụm sai": "cụm đúng"} — khớp chuỗi từ liên tiếp (bỏ dấu câu 2 đầu, không phân biệt hoa thường)"""
    if not sua:
        return words
    P = ".,!?;:…\"'()"

    def n(s):
        return s.strip(P).lower()
    for sai, dung in sua.items():
        key = [n(x) for x in sai.split()]
        rep = dung.split()
        i = 0
        while i <= len(words) - len(key):
            if [n(w["w"]) for w in words[i:i + len(key)]] == key:
                st, en = words[i]["start"], words[i + len(key) - 1]["end"]
                tail = words[i + len(key) - 1]["w"]
                punct = tail[len(tail.rstrip(P)):] if tail.rstrip(P) != tail else ""
                span = (en - st) / max(1, len(rep))
                new = [{"w": r + (punct if j == len(rep) - 1 else ""), "start": round(st + j * span, 3),
                        "end": round(st + (j + 1) * span, 3), "p": 1.0} for j, r in enumerate(rep)]
                words[i:i + len(key)] = new
                i += len(new)
            else:
                i += 1
    return words


def lam_sub(plan, work, dur_out, an):
    src = C.jload(os.path.join(work, "loi_doc.json"))
    cd = plan["cai_dat"]
    sd = os.path.join(work, "sub")
    shutil.rmtree(sd, ignore_errors=True)
    os.makedirs(os.path.join(sd, "fonts"), exist_ok=True)
    for f in os.listdir(C.SUB_FONT_DIR):
        shutil.copy(os.path.join(C.SUB_FONT_DIR, f), os.path.join(sd, "fonts", f))
    proxy = os.path.join(sd, "ra.mp4")
    C.run([C.ffbin("ffmpeg"), "-v", "error", "-y", "-f", "lavfi", "-i", "color=c=black:s=%dx%d:r=%d:d=%.3f" % (W, H, FPS, dur_out),
           "-f", "lavfi", "-i", "anullsrc=r=48000:cl=mono", "-t", "%.3f" % dur_out, "-c:v", "libx264", "-preset", "ultrafast",
           "-crf", "40", "-c:a", "aac", "-shortest", proxy])
    words = gop_so([dict(w) for w in src["words"] if w.get("w")])
    words = thay_cum(words, plan.get("sua_chu") or {})
    words = [w for w in words if not any(w["start"] < s1 and w["end"] > s0 for s0, s1 in an)]
    segs = []
    starts = [float(sg["start"]) for sg in src.get("segments", [])]
    nhom = [[] for _ in starts]
    for x in words:
        k = 0
        for i, st in enumerate(starts):
            if x["start"] >= st - 0.01:
                k = i
        if nhom:
            nhom[k].append(x)
    for mids in nhom:
        if mids:
            segs.append({"start": mids[0]["start"], "end": mids[-1]["end"], "text": " ".join(x["w"] for x in mids), "words": mids})
    out = {"cache_version": 2, "video": proxy, "video_mtime": os.path.getmtime(proxy), "video_frames": int(round(dur_out * FPS)),
           "video_fps": float(FPS), "video_w": W, "video_h": H, "model": src.get("model", "large-v3"), "language": "vi",
           "words": words, "segments": segs}
    C.jsave(os.path.join(sd, "ra.words.json"), out)
    ba = ["--y", str(int(cd.get("sub_y", 1545))), "--max-words", str(int(cd.get("sub_max_chu", 6))),
          "--max-chars", str(int(cd.get("sub_max_ky_tu", 30))), "--font-size", str(int(cd.get("sub_co", 56)))]
    cap = [ln.strip() for ln in io.open(os.path.join(C.ASSETS, "cap_tu_quy_hoach.txt"), encoding="utf-8")
           if ln.strip() and not ln.startswith("#")]
    cap += [x.strip().lower() for x in cd.get("cap_tu", []) if x.strip()]
    p_cap = os.path.join(sd, "cap_tu.txt")
    C.ghi_text(p_cap, "\n".join(C.nfc(x) for x in cap) + "\n")
    ba += ["--keep-pairs", p_cap]

    def chay(scr, extra):
        return subprocess.run([sys.executable, "-X", "utf8", os.path.join(C.SUB_SCRIPTS, scr), "--video", proxy, "--out", proxy]
                              + extra, capture_output=True, text=True, encoding="utf-8", errors="replace")
    r = chay("fix_tokens.py", [])
    if r.returncode != 0:
        print(r.stdout[-2500:], r.stderr[-1500:])
        C.die("bước sub fix_tokens.py lỗi")
    r = chay("build_ass.py", ba)
    if r.returncode != 0:
        # build_ass đo 1 dòng; lớp SubKaraoke tự xếp ≤ 2 dòng nên cụm dài vẫn vẽ được ⇒ chạy lại không đo
        print("⚠ build_ass báo cụm rộng hơn 1 dòng — gom lại không đo (sub tự xuống 2 dòng)")
        r = chay("build_ass.py", ba + ["--no-measure"])
        if r.returncode != 0:
            print(r.stdout[-2500:], r.stderr[-1500:])
            C.die("bước sub build_ass.py lỗi")
    chunks = C.jload(os.path.join(sd, "ra.plan.json"))["chunks"]
    return chunks, words


# ---------------------------------------------------------------- dựng

def dung_canh(plan, ctx, dur_out):
    canh = sorted(plan.get("canh", []), key=lambda x: float(x["tu"]))
    if not canh:
        C.die("ke_hoach.canh rỗng — chưa có cảnh nào")
    out = []
    for i, it in enumerate(canh):
        it = dict(it)
        if it.get("den") is None:
            it["den"] = float(canh[i + 1]["tu"]) if i + 1 < len(canh) else dur_out
        it["den"] = min(float(it["den"]), dur_out)
        if float(it["den"]) - float(it["tu"]) < 0.3:
            C.canh_bao("cảnh %d (%s) ngắn < 0,3 s — bỏ" % (i, it.get("loai")))
            continue
        loai = it.get("loai")
        if loai not in LOAI:
            C.die("loại cảnh lạ: %s (có: %s)" % (loai, ", ".join(LOAI)))
        out.append(LOAI[loai](it, ctx))
    if out and out[0].t0 > 0.01:
        C.canh_bao("cảnh đầu bắt đầu ở %.2f s — %.2f s đầu sẽ lấy cảnh đầu" % (out[0].t0, out[0].t0))
    return out


def main(a):
    t_bd = time.time()
    plan = C.doc_ke_hoach(a.work)
    work = plan["work"]
    cd = plan.setdefault("cai_dat", {})
    audio = plan["audio"]
    res = plan.get("res")
    info = C.probe(audio)
    dur_voice = info["duration"]
    dur_out = dur_voice + float(cd.get("duoi", C.DUOI_SAU_TIENG_CUOI))
    nout = int(round(dur_out * FPS))
    dur_out = nout / FPS

    def tim_file(p):
        for base in ([res] if res else []) + [work, os.path.dirname(audio), C.ASSETS]:
            q = p if os.path.isabs(p) else os.path.join(base, p)
            if os.path.isfile(q):
                return q
        C.die("không thấy file: %s (tìm trong Resources / work / cạnh audio)" % p)

    kenh = plan.get("kenh") or {}
    ctx = {"dl": NguonDiaLy(work), "kenh": kenh, "tim_file": tim_file, "cai_dat": cd, "mang": not a.khong_mang}
    canh = dung_canh(plan, ctx, dur_out)
    ctx["canh"] = canh
    print("▶ %d cảnh · %.2f s (giọng %.2f s)" % (len(canh), dur_out, dur_voice))
    for c in canh:
        print("   %6.2f–%6.2f  %-12s %s" % (c.t0, c.t1, c.loai, (c.loi or "")[:60]))

    # ô ảnh: tải trước
    nen = B.Nen(mang=not a.khong_mang)
    xem = [float(x) for x in a.xem_truoc.split(",")] if a.xem_truoc else None
    ks = set()
    for c in canh:
        if xem and not any(c.t0 - 0.3 <= t <= c.t1 + 0.3 for t in xem):
            continue
        ks |= c.o_can(nen)
    if not a.khong_mang:
        n_, loi = nen.tai_truoc(ks, luong=8)
        print("▶ ô ảnh vệ tinh: cần %d, tải mới %d, lỗi %d" % (len(ks), n_, loi))

    # lớp chung
    hook = D.TheHook(plan["hook"]) if plan.get("hook") else None
    the = [D.TheTaiLieu(it, tim_file) for it in plan.get("the_tai_lieu", []) if it.get("tu") is not None]
    logo = D.Logo(kenh, tim_file)
    credit = D.ChuNguon(B.CREDIT) if cd.get("nguon_anh", True) else None
    an = [[c.t0, c.t1] for c in canh if c.loai == "cta"] + [list(x) for x in cd.get("sub_an", [])]

    def vung_cam(t, c):
        """chỗ không được đặt chữ bản đồ phụ: dải sub, thẻ đầu đề (đang hiện), thẻ hook (đang hiện), logo"""
        r = [DN.DAI_SUB]
        if c.dd and t >= c.dd[0][0] - 0.25:
            r.append((0, 36, W, 184))
        if hook is not None and hook.t0 - 0.1 <= t <= hook.t1:
            r.append(hook.rect())
        if logo.img is not None:
            r.append(logo.rect())
        return r
    ctx["vung_cam"] = vung_cam
    sub = None
    if cd.get("sub", True) and not xem:
        chunks, words = lam_sub(plan, work, dur_out, an)
        sub = D.SubKaraoke(chunks, sub_y=int(cd.get("sub_y", 1545)), co=int(cd.get("sub_co", 56)), an=an)
        print("▶ sub karaoke: %d cụm" % len(sub.cum))
    elif xem:
        try:
            chunks, words = lam_sub(plan, work, dur_out, an)
            sub = D.SubKaraoke(chunks, sub_y=int(cd.get("sub_y", 1545)), co=int(cd.get("sub_co", 56)), an=an)
        except SystemExit:
            sub = None

    d_hoa = float(cd.get("hoa_tan", 0.25))

    def canh_tai(t):
        k = 0
        for i, c in enumerate(canh):
            if t >= c.t0:
                k = i
        return k

    def khung(t):
        k = canh_tai(t)
        c = canh[k]
        fr = c.nen(t, nen)
        if c.loai != "cta":
            c.ve_lop(fr, t, nen)
        # hoà tan sang cảnh kế (không áp dụng cho CTA: cắt cứng như mẫu)
        if k + 1 < len(canh):
            n_ = canh[k + 1]
            if not n_.hard_cut and not c.hard_cut and n_.t0 - d_hoa <= t < n_.t0:
                w = smooth((t - (n_.t0 - d_hoa)) / d_hoa)
                f2 = n_.nen(t, nen)
                if n_.loai != "cta":
                    n_.ve_lop(f2, t, nen)
                C.tron(fr, f2, w)
        if c.loai == "cta":
            logo.ve(fr)
            return fr
        if hook is not None:
            hook.ve(fr, t)
        for th in the:
            th.ve(fr, t)
        logo.ve(fr)
        if credit is not None:
            credit.ve(fr)
        if sub is not None:
            sub.ve(fr, t)
        return fr

    if xem:
        for t in xem:
            fr = khung(min(max(0.0, t), dur_out - 1 / FPS))
            p = os.path.join(work, "xem_truoc_%06.2f.jpg" % t)
            Image.fromarray(fr).save(p, quality=90)
            print("   → %s" % p)
        print("✅ xem trước xong (%.0f s)" % (time.time() - t_bd))
        return None

    # tiếng
    voice = A.doc(audio)
    n_sr = int(dur_out * A.SR)
    voice = np.concatenate([voice, np.zeros(max(0, n_sr - len(voice)), np.float32)])[:n_sr]
    ev = []
    if cd.get("sfx", True):
        for c in canh:
            for e in c.sfx():
                if e["t"] < dur_out - 0.05 and (e.get("chot") or cd.get("sfx_them", False)):
                    ev.append(e)
        if cd.get("sfx_them", False):
            for th in the:
                ev += th.sfx()
    sfx, bc = A.tron_sfx(voice, ev)
    mix = voice + sfx[:len(voice)]
    if cd.get("nhac") and cd.get("nhac") != "khong":
        mix = mix + A.nhac_nen(tim_file(cd["nhac"]), len(mix), voice, duoi_db=float(cd.get("nhac_duoi_giong_db", 20)))
    A.ghi(os.path.join(work, "tron.wav"), mix)
    am_ra = os.path.join(work, "tieng_ra.wav")
    A.master(os.path.join(work, "tron.wav"), am_ra, float(cd.get("lufs", -14.0)), float(cd.get("tp", -1.0)))

    out_path = os.path.abspath(a.out) if a.out else C.ten_khong_trung(os.path.join(
        os.path.dirname(audio), os.path.splitext(os.path.basename(audio))[0] + "_BDQH.mp4"))
    if a.chi_tieng:
        src = os.path.abspath(a.chi_tieng)
        C.run([C.ffbin("ffmpeg"), "-v", "error", "-y", "-i", src, "-i", am_ra, "-map", "0:v", "-map", "1:a", "-c:v", "copy",
               "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", out_path])
        bcp = os.path.join(work, "dung_bao_cao.json")
        rp = C.jload(bcp) if os.path.isfile(bcp) else {}
        rp.update({"ra": out_path, "sfx": bc, "chi_tieng_tu": src})
        C.jsave(bcp, rp)
        print("✅ trộn lại tiếng, giữ nguyên hình của %s → %s" % (src, out_path))
        return out_path
    vf = "scale=out_color_matrix=bt709:out_range=tv,format=yuv420p"
    enc_cmd = [C.ffbin("ffmpeg"), "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", "%dx%d" % (W, H),
               "-r", str(FPS), "-i", "-", "-i", am_ra, "-map", "0:v", "-map", "1:a", "-vf", vf,
               "-c:v", "libx264", "-preset", a.preset, "-crf", str(a.crf), "-colorspace", "bt709", "-color_primaries", "bt709",
               "-color_trc", "bt709", "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", out_path]
    enc = subprocess.Popen(enc_cmd, stdin=subprocess.PIPE)
    print("▶ dựng %d khung …" % nout)
    for f in range(nout):
        fr = khung(f / FPS)
        enc.stdin.write(np.ascontiguousarray(fr).tobytes())
        if f % 300 == 0:
            print("   %4d / %d  (%.0f s)" % (f, nout, time.time() - t_bd))
    enc.stdin.close()
    enc.wait()
    if enc.returncode != 0 or not os.path.isfile(out_path):
        C.die("mã hoá lỗi")
    C.jsave(os.path.join(work, "dung_bao_cao.json"), {
        "ra": out_path, "giay": dur_out, "giong": dur_voice,
        "canh": [{"loai": c.loai, "t0": round(c.t0, 3), "t1": round(c.t1, 3), "loi": c.loi} for c in canh],
        "the_tai_lieu": [{"t0": t.t0, "t1": t.t1} for t in the],
        "sub_cum": [[round(c["t0"], 3), round(c["t_het"], 3), " ".join(c["chu"])] for c in (sub.cum if sub else [])],
        "sfx": bc, "o_thieu": sorted(list(nen.thieu))[:50]})
    print("✅ dựng xong %.0f s → %s" % (time.time() - t_bd, out_path))
    return out_path


def cli():
    ap = argparse.ArgumentParser()
    ap.add_argument("--work", required=True)
    ap.add_argument("--out")
    ap.add_argument("--preset", default="medium")
    ap.add_argument("--crf", type=int, default=18)
    ap.add_argument("--xem-truoc", dest="xem_truoc", help="các giây, vd 1,20.5,45 → chỉ ra ảnh xem trước")
    ap.add_argument("--khong-mang", dest="khong_mang", action="store_true")
    ap.add_argument("--chi-tieng", dest="chi_tieng", help="video đã dựng: chỉ trộn lại tiếng (SFX/nhạc), chép nguyên hình")
    a = ap.parse_args()
    main(a)


if __name__ == "__main__":
    cli()
