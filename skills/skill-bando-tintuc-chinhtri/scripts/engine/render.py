# -*- coding: utf-8 -*-
"""Dựng khung hình: camera theo nhịp, nền ô vệ tinh, động tác mặt đất -> warp phối cảnh -> động tác màn hình."""
import math
import os
import sys

import cv2
import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import chung as C
from . import camera as CAM
from . import dong_tac as DT
from . import nen as NEN
from . import ve
from . import dia_ly as DL

NGHIENG_MAC_DINH = 35.0


# ---------------- camera theo nhịp ----------------
class LoTrinh:
    """Chuỗi trạng thái camera theo thời gian, dựng từ kịch bản."""

    TOC_DO = 0.35   # "đơn vị dịch chuyển" mỗi giây (1 đơn vị = 1 bề rộng màn hình hoặc e^2 lần đổi zoom)

    def __init__(self, kb, tt, t_end, W, H):
        self.W, self.H = W, H
        self.doan = []   # (t_bat_dau, t_toi, trang_thai_truoc, trang_thai_dich, kieu, t_het, ro_gio)
        self.van_de = []
        nhip = sorted(kb.get("nhip", []), key=lambda n: float(n.get("t", 0)))
        truoc = None
        # mỗi nhịp: camera là 1 dict, hoặc DANH SÁCH các điểm dừng {luc: giây camera ĐẾN NƠI, toi, rong_km, ...}
        muc = []
        for i, n in enumerate(nhip):
            t0 = float(n.get("t", 0))
            t_n = float(nhip[i + 1]["t"]) if i + 1 < len(nhip) else t_end
            cam = n.get("camera")
            if not cam:
                continue
            ds = cam if isinstance(cam, list) else [cam]
            ds = sorted(ds, key=lambda d: float(d.get("luc", t0)))
            for k, d in enumerate(ds):
                den = float(ds[k + 1].get("luc", t0)) if k + 1 < len(ds) else t_n
                muc.append((t0 if k == 0 and d.get("luc") is None else float(d.get("luc", t0)), d, d.get("luc") is not None, den))
        for (t0, cam, ro, t_het) in muc:
            dich = self._trang_thai(cam, tt, truoc)
            if dich is None:
                continue
            if truoc is None:
                self.doan.append((t0, t0, dich, dich, "giu", t_het, False))
                truoc = dich
                continue
            kieu = cam.get("kieu") or "bay"
            if ro:
                bay = 0.0   # ĐẾN NƠI đúng t0 (mốc giây tuyệt đối); chỗ bắt đầu bay = mốc trước
            else:
                bay = cam.get("bay_trong")
                if bay is None:
                    bay = min(2.4, max(0.8, 0.65 * (t_het - t0)))
            if kieu == "giu":
                dich = truoc
                bay = 0.0
            self.doan.append((t0, t0 + float(bay), truoc, dich, kieu, t_het, ro))
            truoc = dich
        if not self.doan:
            st = CAM.TrangThai(0.5, 0.45, 0.4, NGHIENG_MAC_DINH)
            self.doan.append((0.0, 0.0, st, st, "giu", t_end, False))
        self._dung_quy_dao(t_end)
        self._kiem_toc_do()

    def _kiem_toc_do(self):
        mo = self.mo
        for (ta, a, _), (tb, b, kieu) in zip(mo[:-1], mo[1:]):
            dx = abs(b.x - a.x)
            dx = min(dx, 1 - dx)
            dist = math.hypot(dx, b.y - a.y) / ((a.w + b.w) / 2)
            can = dist + 0.5 * abs(math.log(b.w / a.w))
            dt = tb - ta
            if can > 0.15 and dt < can / self.TOC_DO * 0.8:
                self.van_de.append("camera %.1f s → %.1f s: dịch chuyển %.2f bề rộng màn hình trong %.1f s quá nhanh "
                                   "(cần ≥ %.1f s) — lia gắt gây chóng mặt: nới thời gian, bớt 1 điểm dừng hoặc tăng rong_km"
                                   % (ta, tb, can, dt, can / self.TOC_DO))

    @staticmethod
    def _trang_thai(cam, tt, truoc):
        toi = cam.get("toi")
        p = tt.diem(toi) if toi is not None else None
        if p is None:
            if truoc is None:
                return None
            x, y = truoc.x, truoc.y
            lat = C.don_vi_den_lonlat(x, y)[1]
        else:
            x, y = C.lonlat_den_don_vi(*p)
            lat = p[1]
        rong_km = cam.get("rong_km")
        if rong_km is None:
            w = truoc.w if truoc is not None else C.km_den_don_vi(3000, lat)
        else:
            w = C.km_den_don_vi(float(rong_km), lat)
        w = max(C.km_den_don_vi(30, lat), min(0.95, w))
        y = max(0.03, min(0.97, y))
        ng = float(cam.get("nghieng", NGHIENG_MAC_DINH))
        return CAM.TrangThai(x, y, w, max(0.0, min(50.0, ng)), float(cam.get("xoay", 0.0)))

    def _dung_quy_dao(self, t_end):
        """Quỹ đạo LIÊN TỤC: camera không dừng-rồi-chạy ở mỗi nhịp. Mốc = trạng thái đích của từng nhịp, đạt
        giữa lúc bay; nội suy PCHIP (vận tốc liên tục, không vọt quá mốc) cho x, y, log w, nghiêng, xoay."""
        mo = []   # (t, trang_thai, kieu_cua_doan_toi_mo_nay)
        for (t0, t1, a, b, kieu, t_het, ro) in self.doan:
            if kieu == "giu" and mo:
                continue
            tm = t0 if (not mo or ro) else (t0 + 0.5 * (t1 - t0) if t1 > t0 else t0)
            if mo and tm <= mo[-1][0] + 0.3:
                tm = mo[-1][0] + 0.3
            mo.append((tm, b, kieu))
        if not mo:
            mo = [(0.0, CAM.TrangThai(0.5, 0.45, 0.4, NGHIENG_MAC_DINH), "giu")]
        if mo[0][0] > 0:
            mo.insert(0, (0.0, mo[0][1], "giu"))
        if mo[-1][0] < t_end:
            mo.append((t_end, mo[-1][1], "giu"))
        self.mo = mo
        T = np.array([m[0] for m in mo], np.float64)
        xs = [mo[0][1].x]
        for m in mo[1:]:
            d = m[1].x - (xs[-1] % 1.0)
            d -= round(d)
            xs.append(xs[-1] + d)
        kenh = [np.array(xs), np.array([m[1].y for m in mo]), np.array([math.log(m[1].w) for m in mo]),
                np.array([m[1].nghieng for m in mo]), np.array([m[1].xoay for m in mo])]
        self._T = T
        self._V = kenh
        self._M = [self._pchip(T, v) for v in kenh]

    @staticmethod
    def _pchip(T, v):
        n = len(T)
        m = np.zeros(n)
        if n < 3:
            return m
        h = np.diff(T)
        d = np.diff(v) / h
        for k in range(1, n - 1):
            if d[k - 1] * d[k] > 0:
                w1, w2 = 2 * h[k] + h[k - 1], h[k] + 2 * h[k - 1]
                m[k] = (w1 + w2) / (w1 / d[k - 1] + w2 / d[k])
        return m

    def tai(self, t):
        T = self._T
        t = min(max(t, T[0]), T[-1])
        i = int(np.searchsorted(T, t, side="right") - 1)
        i = max(0, min(len(T) - 2, i))
        h = T[i + 1] - T[i]
        p = (t - T[i]) / h
        h00, h10 = 2 * p ** 3 - 3 * p ** 2 + 1, p ** 3 - 2 * p ** 2 + p
        h01, h11 = -2 * p ** 3 + 3 * p ** 2, p ** 3 - p ** 2
        val = [h00 * V[i] + h10 * h * M[i] + h01 * V[i + 1] + h11 * h * M[i + 1] for V, M in zip(self._V, self._M)]
        x, y, lw, ng, xo = val
        if self.mo[i + 1][2] == "vong":
            wa, wb = math.exp(self._V[2][i]), math.exp(self._V[2][i + 1])
            kc = math.hypot(self._V[0][i + 1] - self._V[0][i], self._V[1][i + 1] - self._V[1][i])
            dinh = max(max(wa, wb) * 1.6, kc * 1.3)
            lw += max(0.0, math.log(dinh) - lw) * math.sin(math.pi * p) ** 2
        return CAM.TrangThai(x % 1.0, y, math.exp(lw), ng, xo)


# ---------------- ngữ cảnh cho động tác ----------------
class ThucThe:
    """Tra cứu thực thể từ work/thuc_the.json + Natural Earth."""

    def __init__(self, thuc_the, dia_ly):
        self.tt = thuc_the or {}
        self.dl = dia_ly

    def rec(self, ref):
        if ref is None:
            return None
        if isinstance(ref, (list, tuple)) and len(ref) == 2:
            return {"loai": "diem", "lon": float(ref[0]), "lat": float(ref[1])}
        key = str(ref)
        if key in self.tt:
            return self.tt[key]
        k2 = C.ten_khong_dau(key)
        for k, v in self.tt.items():
            if C.ten_khong_dau(k) == k2:
                return v
        rec = self.dl.tim(key) if self.dl else None
        if rec:
            return {"loai": rec["loai"], "lon": rec["lon"], "lat": rec["lat"], "ten": rec["ten"], "iso": rec["iso"]}
        b = C.tim_bien(key)
        if b:
            return {"loai": "bien", "lon": b[1], "lat": b[2], "ten": b[0]}
        return None

    def diem(self, ref):
        r = self.rec(ref)
        if not r or r.get("lon") is None:
            return None
        return float(r["lon"]), float(r["lat"])

    def vung(self, ref):
        r = self.rec(ref)
        if not r:
            return None
        ten = r.get("ten_ne") or r.get("iso") or r.get("ten") or str(ref)
        rec = self.dl.tim(ten) if self.dl else None
        if rec is None and isinstance(ref, str):
            rec = self.dl.tim(ref)
        return rec

    def co_nuoc(self, ref):
        r = self.rec(ref)
        return r.get("co") if r else None


class NguCanh:
    def __init__(self, cam, thuc_the, fonts, sprites, no_frames, W, H):
        self.cam = cam
        self.tt = thuc_the
        self.font_sub = fonts["sub"]
        self.font_tay = fonts["tay"]
        self.font_co = fonts["co"]
        self.font_dam = fonts["dam"]
        self._sprites = sprites
        self._no = no_frames
        self.W, self.H = W, H
        self.t = 0.0
        self.z = 0
        self.x0 = self.y0 = 0
        self.rong = self.cao = 0
        self.s = 256
        self.ground = None
        self.frame = None
        self.to_nuoc_map = {}

    # thực thể
    def diem(self, ref):
        return self.tt.diem(ref)

    def vung(self, ref):
        return self.tt.vung(ref)

    def co_nuoc(self, ref):
        return self.tt.co_nuoc(ref)

    def to_nuoc_cua(self, ref):
        k = C.ten_khong_dau(str(ref))
        return self.to_nuoc_map.get(k)

    def sprite(self, ten):
        return self._sprites(ten)

    def sprite_no(self, q):
        if not self._no:
            return None
        i = min(len(self._no) - 1, int(q * len(self._no)))
        return self._no[i]

    def anh_nguoi(self, ten):
        r = self.tt.rec(ten)
        return r.get("anh") if r else None

    def anh_minh_hoa(self, file, tim):
        if file and os.path.exists(file):
            return file
        r = self.tt.rec(file or tim)
        return r.get("anh") if r else None

    # toạ độ
    def don_vi(self, lon, lat):
        return C.lonlat_den_don_vi(lon, lat)

    def lonlat_don_vi(self, x, y):
        return C.don_vi_den_lonlat(x % 1.0, y)

    def px_don_vi(self, x, y):
        """đơn vị -> px trong ROI (có quấn vòng về gần ROI)."""
        px = x * self.s - self.x0
        cx = self.rong / 2.0
        for k in (-1, 1):
            if abs(px + k * self.s - cx) < abs(px - cx):
                px += k * self.s
        return px, y * self.s - self.y0

    def px_dat(self, lon, lat):
        return DL.diem_den_px(lon, lat, self.z, self.x0, self.y0, self.rong)

    def man(self, lon, lat):
        x, y = C.lonlat_den_don_vi(lon, lat)
        return self.man_don_vi(x, y)

    def man_don_vi(self, x, y):
        # chọn bản sao quấn gần camera
        cx = self.cam.tt.x
        for k in (-1, 1):
            if abs(x + k - cx) < abs(x - cx):
                x += k
        return self.cam.chieu_diem(x, y)

    def km_px_dat(self, km, lat):
        return C.km_den_don_vi(km, lat) * self.s

    def km_px_man(self, km, lon, lat):
        x, y = C.lonlat_den_don_vi(lon, lat)
        return C.km_den_don_vi(km, lat) * self.cam.ti_le_tai(x, y)

    def km_den_don_vi(self, km, lat):
        return C.km_den_don_vi(km, lat)

    def rong_km_hien(self):
        tt = self.cam.tt
        lat = C.don_vi_den_lonlat(tt.x, tt.y)[1]
        return tt.w * C.km_moi_don_vi(lat)

    def px_day(self, px_man_hinh):
        """Bề dày nét vẽ ở mặt đất tương đương px_man_hinh px trên màn hình (tại điểm nhìn)."""
        tt = self.cam.tt
        return max(1, int(round(px_man_hinh * (tt.w * self.s) / self.W)))


# ---------------- bộ dựng ----------------
class BoDung:
    def __init__(self, kb, thuc_the, du_lieu, cache_tiles, mang=False, W=None, H=None, fps=None):
        kh = kb.get("khung") or {}
        self.W = int(W or kh.get("rong") or C.KHUNG_MAC_DINH["rong"])
        self.H = int(H or kh.get("cao") or C.KHUNG_MAC_DINH["cao"])
        self.fps = int(fps or kh.get("fps") or C.KHUNG_MAC_DINH["fps"])
        self.kb = kb
        self.t_end = float(kb.get("thoi_luong") or 10.0)
        self.dl = DL.DiaLy(du_lieu.get("nuoc"), du_lieu.get("bang"))
        for r in (thuc_the or {}).values():
            if isinstance(r, dict):
                for k in ("co", "anh"):
                    if r.get(k):
                        r[k] = C.sua_duong_dan(r[k])
        self.tt = ThucThe(thuc_the, self.dl)
        self.lo_trinh = LoTrinh(kb, self.tt, self.t_end, self.W, self.H)
        self.cam = CAM.Camera(self.W, self.H, hfov=float(kb.get("hfov", 38.0)))
        self.nen = NEN.Nen(cache_tiles, mang=mang)
        self.du_lieu = du_lieu
        fonts = {"sub": du_lieu["font_sub"], "tay": du_lieu["font_tay"], "co": du_lieu["font_co"],
                 "dam": du_lieu.get("font_dam") or du_lieu["font_sub"]}
        for k, v in fonts.items():
            if not os.path.exists(v):
                fonts[k] = "C:/Windows/Fonts/arialbd.ttf"
        self._sprite_cache = {}
        self.thu_vien = [C.THU_VIEN, os.path.join(C.CACHE, "thu_vien_tai"), du_lieu["icon"]]
        no_dir = du_lieu["no"]
        self.no_frames = []
        if os.path.isdir(no_dir):
            for f in sorted(os.listdir(no_dir)):
                if f.endswith(".png"):
                    sp = ve.nap_sprite(os.path.join(no_dir, f))
                    if sp is not None:
                        self.no_frames.append(sp)
        self.ctx = NguCanh(self.cam, self.tt, fonts, self.sprite, self.no_frames, self.W, self.H)
        self.dong_tac = []
        self._tao_dong_tac()

    def sprite(self, ten):
        if ten in self._sprite_cache:
            return self._sprite_cache[ten]
        sp = None
        if ten and os.path.exists(str(ten)):
            sp = ve.nap_sprite(ten)
        else:
            k = C.tim_vat_the(ten) or ten
            for d in self.thu_vien:
                for cand in (os.path.join(d, "%s.png" % k), os.path.join(d, "%s.png" % ten)):
                    if os.path.exists(cand):
                        sp = ve.nap_sprite(cand)
                        break
                if sp is not None:
                    break
            if sp is None:
                r = self.tt.rec(ten)
                if r and r.get("anh"):
                    sp = ve.nap_sprite(r["anh"])
        self._sprite_cache[ten] = sp
        return sp

    def _tao_dong_tac(self):
        for n in self.kb.get("nhip", []):
            for d in n.get("dong_tac", []) or []:
                try:
                    dt = DT.tao(d, self.t_end)
                except Exception as exc:
                    C.canh_bao("bỏ động tác lỗi: %s (%s)" % (d, exc))
                    continue
                dt.nhip_id = n.get("id")
                self.dong_tac.append(dt)
        # vỡ vụn tắt tô nước + nhãn của nước đó
        for vo in [d for d in self.dong_tac if isinstance(d, DT.VoVun)]:
            k = C.ten_khong_dau(str(vo.ref))
            for d in self.dong_tac:
                if isinstance(d, DT.ToNuoc) and C.ten_khong_dau(str(d.ref)) == k and d.t0 <= vo.t0 < d.t1:
                    d.t1 = vo.t0
                    d.RA = 0.0
                if isinstance(d, DT.Nhan) and d.ref and C.ten_khong_dau(str(d.ref)) == k and d.t0 <= vo.t0 < d.t1:
                    d.t1 = vo.t0
                    d.RA = 0.0
                    vo.nhan.append(d)
        for d in self.dong_tac:
            if isinstance(d, DT.ToNuoc):
                self.ctx.to_nuoc_map[C.ten_khong_dau(str(d.ref))] = d
        thu_tu = {"to_nuoc": 0, "lan": 1, "tuyen": 2, "radar": 3, "phong": 4, "tach": 5, "vo_vun": 6,
                  "vat_the": 7, "nhan": 8, "chu_neon": 9, "no": 10, "ghim": 11, "nguoi": 12, "anh": 13, "so": 14}
        self.dong_tac.sort(key=lambda d: (thu_tu.get(d.LOAI, 20), d.t0))

    def sfx_cues(self):
        out = []
        for d in self.dong_tac:
            out.extend(d.sfx())
        return out

    def rang_buoc(self, st):
        """Không để camera nhìn ra ngoài mép trên/dưới bản đồ: hạ dần góc nghiêng, rồi thu hẹp tầm nhìn."""
        st = st.copy()

        def ok(s):
            self.cam.dat(s)
            x0, y0, x1, y1 = self.cam.vung_dat(xa_nhat=self.cam.d * 5.0)
            return y0 >= -0.002 and y1 <= 1.002

        if ok(st):
            return st
        # hạ góc nghiêng LIÊN TỤC (chia đôi) tới mức vừa đủ, tối thiểu 10°; còn vi phạm thì thu hẹp tầm nhìn
        lo = min(st.nghieng, 10.0)
        s2 = st.copy()
        s2.nghieng = lo
        if ok(s2):
            a, b = lo, st.nghieng
            for _ in range(18):
                mid = (a + b) / 2
                s2.nghieng = mid
                if ok(s2):
                    a = mid
                else:
                    b = mid
            s2.nghieng = a
            return s2
        st.nghieng = lo
        a, b = st.w * 0.3, st.w
        for _ in range(18):
            mid = (a + b) / 2
            st.w = mid
            if ok(st):
                a = mid
            else:
                b = mid
        st.w = a
        return st

    def cam_tai(self, t):
        """Camera cuối cùng tại t: quỹ đạo → ràng buộc mép bản đồ → làm mượt góc nghiêng + tầm nhìn theo thời gian
        (ràng buộc bật/tắt đột ngột sẽ làm hình giật) → ràng buộc lại cho chắc."""
        if getattr(self, "_cam_luoi", None) is None:
            fps = self.fps
            n = int(self.t_end * fps) + 3
            ng = np.zeros(n)
            lw = np.zeros(n)
            goc = []
            for i in range(n):
                st = self.rang_buoc(self.lo_trinh.tai(i / fps))
                goc.append(st)
                ng[i], lw[i] = st.nghieng, math.log(st.w)
            k = np.exp(-0.5 * (np.arange(-int(1.5 * fps), int(1.5 * fps) + 1) / (0.35 * fps)) ** 2)
            k /= k.sum()
            r = len(k) // 2

            def lam_muot(v):
                vp = np.concatenate([np.full(r, v[0]), v, np.full(r, v[-1])])
                return np.convolve(vp, k, mode="valid")

            ng2, lw2 = lam_muot(ng), lam_muot(lw)
            # chỉ làm mượt phần do ràng buộc gây ra: lấy giá trị đã mượt nhưng không nghiêng hơn / rộng hơn bản gốc
            self._cam_luoi = (goc, ng2, lw2)
        goc, ng2, lw2 = self._cam_luoi
        f = min(max(t * self.fps, 0.0), len(goc) - 1.001)
        i = int(f)
        a = f - i
        st = self.lo_trinh.tai(t)
        st.nghieng = ng2[i] * (1 - a) + ng2[i + 1] * a
        st.w = math.exp(lw2[i] * (1 - a) + lw2[i + 1] * a)
        return self.rang_buoc(st)

    # ---- 1 khung ----
    def khung(self, t):
        c = self.ctx
        c.t = t
        st = self.cam_tai(t)
        self.cam.dat(st)
        z, x0, y0, x1, y1 = NEN.chon_vung(self.cam)
        c.z, c.x0, c.y0 = z, x0, y0
        c.rong, c.cao = x1 - x0, y1 - y0
        c.s = 256 * (1 << z)
        base = self.nen.ghep(z, x0, y0, x1, y1)
        c.ground = Image.fromarray(cv2.cvtColor(base, cv2.COLOR_BGR2RGBA))
        for d in self.dong_tac:
            if d.LOP_DAT and d.hoat_dong(t):
                try:
                    d.ve_dat(c)
                except Exception as exc:
                    if not getattr(d, "loi", None):
                        d.loi = str(exc)
                        C.canh_bao("động tác %s lỗi khi vẽ mặt đất: %s" % (d.LOAI, exc))
        # warp phối cảnh
        s = c.s
        goc = np.float32([[0, 0], [c.rong, 0], [c.rong, c.cao], [0, c.cao]])
        dv = [((x0 + gx) / s, (y0 + gy) / s) for gx, gy in goc]
        dv = [(x - round(x - self.cam.tt.x), y) for x, y in dv]
        man = self.cam.chieu(dv)[:, :2].astype(np.float32)
        Hm = cv2.getPerspectiveTransform(goc, man)
        src = cv2.cvtColor(np.asarray(c.ground), cv2.COLOR_RGBA2BGR)
        frame = cv2.warpPerspective(src, Hm, (self.W, self.H), flags=cv2.INTER_LINEAR,
                                    borderMode=cv2.BORDER_CONSTANT, borderValue=NEN.MAU_KHONG_GIAN)
        c.frame = frame
        man_hinh = [d for d in self.dong_tac if d.LOP_MAN and d.hoat_dong(t)]

        def khoa(d):
            if d.LOAI in ("no",):
                return (3, 0)
            if d.LOAI in ("anh", "so"):
                return (2, 0)
            if d.LOAI == "ghim":
                return (1, 0)
            p = d.diem(c, getattr(d, "ref", None) or getattr(d, "tu", None)) if hasattr(d, "diem") else None
            y = c.man(*p)[1] if p else 0
            return (0, y)

        for d in sorted(man_hinh, key=khoa):
            try:
                d.ve_man(c)
            except Exception as exc:
                if not getattr(d, "loi", None):
                    d.loi = str(exc)
                    C.canh_bao("động tác %s lỗi khi vẽ màn hình: %s" % (d.LOAI, exc))
        return frame

    def o_can_toan_bo(self, buoc=0.25):
        """Tập ô bản đồ cần cho cả video (để tải trước)."""
        ks = set()
        t = 0.0
        while t <= self.t_end + 0.01:
            self.cam.dat(self.cam_tai(t))
            z, x0, y0, x1, y1 = NEN.chon_vung(self.cam)
            ks |= self.nen.o_can(z, x0, y0, x1, y1)
            t += buoc
        return ks
