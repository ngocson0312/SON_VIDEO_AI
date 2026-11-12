# -*- coding: utf-8 -*-
"""Bước 3 — DỰNG HÌNH từng khung theo ke_hoach.json (đúng phong cách video mẫu Hết Hồn Real).

Mỗi khung:  nền (zoom nhảy bám mặt + trôi chậm, màu ấm, tối mép dưới/trên, chuyển cảnh zoom-nhoè / tách màu)
          → LỚP SAU NGƯỜI (logo, tiêu đề 3 tầng — nhân (1 − mặt nạ người) nên đầu che chữ)
          → LỚP TRƯỚC (thẻ ảnh bay ra từ tay, icon 3D, ô tìm kiếm gõ chữ, số tiền + vệt tốc độ, liệt kê, sub ngực)
          → chuyển cảnh phủ (tia sáng dọc, cháy phim)  → ffmpeg (mã hoá 1 lần, ghép tiếng đã master).
Mọi số phong cách lấy từ chung.py."""
import os, math, time, subprocess
from functools import lru_cache
import numpy as np
import cv2
from PIL import Image, ImageDraw
import chung as C
import ve
import nguoi
import tay

W, H, FPS = C.W, C.H, C.FPS
GRADE = (f"eq=contrast={C.MAU_SAC['tuong_phan']}:saturation={C.MAU_SAC['bao_hoa']},"
         f"colorbalance=rm={C.MAU_SAC['am']}:bm={-C.MAU_SAC['am']}")
MAT_MAC_DINH = [W * 0.42, H * 0.20, W * 0.58, H * 0.20 + W * 0.16]


# ------------------------------------------------------------------ ghép lớp (ảnh nhân trước alpha, float32)
_PM = {}


def pm(anh):
    k = id(anh.img)
    v = _PM.get(k)
    if v is None or v[1] is not anh.img:
        a = np.asarray(anh.img.convert('RGBA'), dtype=np.float32) / 255.0
        a = a.copy(); a[..., :3] *= a[..., 3:4]
        v = (a, anh.img); _PM[k] = v
    return v[0]


def _dau_tren(K, c0, c1):
    """Khoảng (px) từ đỉnh hộp nội dung chữ khoá tới mực DẤU nằm trên đỉnh chữ hoa (sắc / huyền / hỏi / ngã / mũ)
    trong các cột [c0, c1) của hộp nội dung; None nếu dưới đó không có dấu."""
    if not K.meta or 'cap' not in K.meta: return None
    a = np.asarray(K.img.convert('RGBA'))[..., 3]
    ct = int(K.meta['cap'][0] - 0.03 * K.meta['co'])
    x0, x1 = int(max(0, K.ox + c0)), int(min(a.shape[1], K.ox + c1))
    if ct <= 0 or x1 <= x0: return None
    rows = np.where((a[:ct, x0:x1] > 150).sum(1) >= 2)[0]
    return None if len(rows) < 3 else float(rows.min() - K.oy)


def _ghep(F, P, x0, y0, al=1.0, mask=None):
    h, w = P.shape[:2]
    a0, b0, a1, b1 = max(0, x0), max(0, y0), min(W, x0 + w), min(H, y0 + h)
    if a1 <= a0 or b1 <= b0: return
    Q = P[b0 - y0:b1 - y0, a0 - x0:a1 - x0]
    rgb, a = Q[..., :3], Q[..., 3]
    if mask is not None:
        k = (1.0 - mask[b0:b1, a0:a1]) * al
        rgb = rgb * k[..., None]; a = a * k
    elif al < 0.999:
        rgb = rgb * al; a = a * al
    R = F[b0:b1, a0:a1]
    R *= (1.0 - a)[..., None]
    R += rgb


def dat_P(F, P, px, py, X, Y, sc=1.0, al=1.0, mo=0.0, nx=0.0, ny=0.0, trang=0.0, goc=0.0, mask=None):
    """đặt điểm neo (px, py) của ảnh P vào (X, Y) khung; phóng sc, mờ al, nhoè Gauss mo, nhoè chuyển động nx/ny,
    loé trắng trang (0..1), xoay goc (độ)."""
    if al <= 0.004 or sc <= 0.02: return
    h, w = P.shape[:2]
    if abs(sc - 1) > 1e-3:
        nw, nh = max(1, int(round(w * sc))), max(1, int(round(h * sc)))
        P = cv2.resize(P, (nw, nh), interpolation=cv2.INTER_AREA if sc < 1 else cv2.INTER_LINEAR)
        px, py = px * nw / w, py * nh / h
    if trang > 0.004:
        Wt = P.copy(); Wt[..., :3] = Wt[..., 3:4]
        P = P * (1 - trang) + Wt * trang
    nx, ny = int(round(abs(nx))), int(round(abs(ny)))
    if nx or ny or mo > 0.3 or goc:
        pad = nx + ny + int(3 * mo) + 2 + (int(0.3 * max(P.shape[:2])) if goc else 0)
        P = cv2.copyMakeBorder(P, pad, pad, pad, pad, cv2.BORDER_CONSTANT, value=(0, 0, 0, 0))
        px += pad; py += pad
        if goc:
            R = cv2.getRotationMatrix2D((float(px), float(py)), float(goc), 1.0)
            P = cv2.warpAffine(P, R, (P.shape[1], P.shape[0]), flags=cv2.INTER_LINEAR, borderValue=(0, 0, 0, 0))
        if nx: P = cv2.blur(P, (2 * nx + 1, 1))
        if ny: P = cv2.blur(P, (1, 2 * ny + 1))
        if mo > 0.3: P = cv2.GaussianBlur(P, (0, 0), mo)
    _ghep(F, P, int(round(X - px)), int(round(Y - py)), al, mask)


def dat(F, anh, X, Y, ax=0.5, ay=0.5, **kw):
    """đặt điểm (ax, ay) của HỘP NỘI DUNG anh vào (X, Y)."""
    dat_P(F, pm(anh), anh.ox + ax * anh.w, anh.oy + ay * anh.h, X, Y, **kw)


@lru_cache(maxsize=64)
def _vong(w, h, q):
    return ve.vong_ve(w, h, q / 24.0)


@lru_cache(maxsize=48)
def _vet(w, h, q):
    return ve.vet_toc_do(w, h, q / 12.0)


@lru_cache(maxsize=96)
def _o_tim(text, con_tro):
    return ve.o_tim_kiem(text, con_tro)


def _lerp(a, b, e):
    return a + (b - a) * e


# ------------------------------------------------------------------ bộ dựng
class Dung:
    def __init__(self, plan, work, dung_mask=True):
        self.plan, self.work = plan, work
        self.src = os.path.join(work, 'nguon.mp4')
        self.n = int(round(float(plan.get('dur') or C.probe(self.src)['dur']) * FPS))
        self.mats = nguoi.mat_theo_khung(work, self.n)
        self.kho = nguoi.Kho(work) if dung_mask else None
        y = np.arange(H, dtype=np.float32)
        T = C.TOI
        d = np.zeros(H, np.float32)
        y0 = T['duoi_tu'] * H
        d = np.where(y > y0, T['duoi_max'] * np.clip((y - y0) / (H - y0), 0, None) ** 1.6, d)
        yt = T['tren_den'] * H
        d = np.maximum(d, np.where(y < yt, T['tren_max'] * np.clip(1 - y / yt, 0, None) ** 1.5, 0))
        self.vig = (1 - d)[:, None, None].astype(np.float32)
        self._cam_init()
        self._tieu_de_init()
        self._sub_init()
        self._phu_init()
        self.su_kien = []          # mốc sự kiện thật (để kiểm)

    # ---------------- camera
    def _tam_mat(self, m):
        m = m or MAT_MAC_DINH
        return ((m[0] + m[2]) / 2, (m[1] + m[3]) / 2)

    def _cam_init(self):
        ks = sorted(self.plan.get('zoom') or [{'t': 0.0, 'z': 1.0}], key=lambda k: k['t'])
        if ks[0]['t'] > 0.001: ks.insert(0, {'t': 0.0, 'z': 1.0})
        self.zk = []
        for j, k in enumerate(ks):
            i0 = C.khung(k['t']); i1 = C.khung(ks[j + 1]['t']) if j + 1 < len(ks) else self.n
            cs = [self._tam_mat(self.mats[q]) for q in range(i0, max(i0 + 1, i1), 3) if q < self.n]
            cx, cy = (np.median(np.array(cs), 0) if cs else (W / 2, H * 0.3))
            self.zk.append((i0, float(k['z']), float(cx), float(cy)))
        self.chuyen = sorted((C.khung(c['t']), c['kieu']) for c in self.plan.get('chuyen', []))

    def cam(self, i):
        seg = self.zk[0]
        for s in self.zk:
            if s[0] <= i: seg = s
            else: break
        i0, z, cx, cy = seg
        z = z * (1 + min(C.ZOOM['troi'] * (i - i0) / FPS, 0.06))
        wc, hc = W / z, H / z
        x0 = C.clamp(cx - wc / 2, 0, W - wc); y0 = C.clamp(cy - C.ZOOM['neo_mat_y'] * hc, 0, H - hc)
        return np.array([[z, 0, -z * x0], [0, z, -z * y0]], np.float32)

    @staticmethod
    def _phong_tam(M, e):
        M2 = M * e
        M2[0, 2] = M[0, 2] * e + (1 - e) * W / 2; M2[1, 2] = M[1, 2] * e + (1 - e) * H / 2
        return M2

    def mat_ra(self, i, M=None):
        i = int(min(max(i, 0), self.n - 1))
        M = self.cam(i) if M is None else M
        m = self.mats[i] or MAT_MAC_DINH
        s = float(M[0, 0])
        return [m[0] * s + M[0, 2], m[1] * s + M[1, 2], m[2] * s + M[0, 2], m[3] * s + M[1, 2]]

    def dinh_dau(self, i, M=None):
        """đỉnh đầu (y toạ độ RA): hàng trên cùng của mặt nạ người trong cột mặt; chưa có mặt nạ thì ước từ hộp mặt."""
        i = int(min(max(i, 0), self.n - 1))
        M = self.cam(i) if M is None else M
        m = self.mats[i] or MAT_MAC_DINH
        fh = m[3] - m[1]
        y_src = m[1] - C.TIEU_DE['dau_tren_mat'] * fh
        k = self.kho
        if k is not None and k.ok:
            j = min(i // k.buoc, len(k.arr) - 1)
            a = k.arr[j]; s = nguoi.M / W
            c0 = int(max(0, (m[0] + 0.15 * (m[2] - m[0])) * s))
            c1 = int(min(nguoi.M, (m[2] - 0.15 * (m[2] - m[0])) * s + 1))
            ya = k.js['ya'][j]
            r1 = int(min(nguoi.M, max(1, (m[1] + 0.5 * fh - ya) * s)))
            if c1 > c0 and r1 > 0:
                rows = np.where(a[:r1, c0:c1].max(1) > 128)[0]
                if len(rows):
                    y = ya + rows[0] / s
                    if m[1] - 0.8 * fh < y < m[1] + 0.3 * fh: y_src = y
        return y_src * float(M[0, 0]) + float(M[1, 2])

    def mat_tb(self, i0, i1):
        bs = [self.mat_ra(q) for q in range(max(0, i0), min(self.n, max(i0 + 1, i1)), 3)]
        return np.median(np.array(bs), 0) if bs else np.array(self.mat_ra(i0))

    def _chuyen_tai(self, i):
        for ic, kieu in self.chuyen:
            cf = C.CHUYEN.get(kieu, C.CHUYEN['zoom_nhoe'])
            if ic - cf['truoc'] <= i < ic + cf['sau']:
                u = (i - (ic - cf['truoc']) + 1) / cf['truoc'] if i < ic else 1 - (i - ic) / cf['sau']
                return kieu, i - ic, C.clamp(u)
        return None

    def nen(self, i, src):
        M = self.cam(i)
        ch = self._chuyen_tai(i)
        rad = 0.0
        if ch:
            kieu, d, u = ch
            if kieu == 'zoom_nhoe':
                M = self._phong_tam(M, 1 + C.CHUYEN['zoom_nhoe']['phong'] * C.ease_in(u)); rad = 0.11 * u
            elif kieu == 'tach_mau':
                rng = np.random.default_rng(i)
                M = M.copy(); M[0, 2] += rng.uniform(-1, 1) * 24 * u; M[1, 2] += rng.uniform(-1, 1) * 24 * u
        if rad > 0.01:
            acc = np.zeros((H, W, 3), np.float32); N = 7
            for k in range(N):
                acc += cv2.warpAffine(src, self._phong_tam(M, 1 + rad * k / (N - 1)), (W, H), flags=cv2.INTER_LINEAR,
                                      borderMode=cv2.BORDER_REFLECT)
            F = acc / (N * 255.0)
        elif abs(M[0, 0] - 1) < 1e-4 and abs(M[0, 2]) < 0.5 and abs(M[1, 2]) < 0.5:
            F = src.astype(np.float32) / 255.0
        else:
            F = cv2.warpAffine(src, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT).astype(np.float32) / 255.0
        if ch and ch[0] == 'tach_mau':
            u = ch[2]; L = int(C.CHUYEN['tach_mau']['lech'] * u)
            if L:
                F[..., 0] = np.roll(F[..., 0], -L, 1); F[..., 2] = np.roll(F[..., 2], L, 1)
            if u > 0.25: F = cv2.GaussianBlur(F, (0, 0), 5 * u)
        F *= self.vig
        return F, M

    def mask(self, i, M, src=None):
        """mặt nạ người (H, W) ở toạ độ RA (đã zoom) — từ bộ nhớ đệm, hoặc tính tại chỗ (xem trước)."""
        a = ya = None
        k = self.kho
        if k is not None and k.ok:
            j, r = divmod(i, k.buoc); j = min(j, len(k.arr) - 1); j2 = min(j + 1, len(k.arr) - 1)
            a = k.arr[j].astype(np.float32)
            if r and j2 != j:
                f = r / k.buoc; a = a * (1 - f) + k.arr[j2].astype(np.float32) * f
            ya = k.js['ya'][j]
        elif src is not None and nguoi.san_sang():
            a, ya = nguoi._chay(np.ascontiguousarray(src), self.mats[min(i, self.n - 1)])
            a = a.astype(np.float32)
        if a is None: return None
        a = cv2.GaussianBlur(a / 255.0, (0, 0), 0.7)
        s = W / nguoi.M
        A = np.array([[s, 0, 0], [0, s, ya], [0, 0, 1]], np.float32)
        Mf = (np.vstack([M, [0, 0, 1]]).astype(np.float32) @ A)[:2]
        return cv2.warpAffine(a, Mf, (W, H), flags=cv2.INTER_LINEAR, borderValue=0)

    # ---------------- TIÊU ĐỀ 3 TẦNG
    def _tieu_de_init(self):
        T = C.TIEU_DE
        self.tds = []
        for td in self.plan.get('tieu_de', []):
            if not td.get('khoa'): continue
            i0, i1 = C.khung(td['t0']), min(self.n - 1, C.khung(td['t1']))
            if i1 - i0 < 8: continue
            kieu = td.get('kieu', 'cam')
            I = ve.icon_net(td['icon'], 150) if td.get('icon') else None
            rong = T['khoa_rong'] - (I.w + 16 if I else 0)
            K = ve.chu_khoa(td['khoa'], kieu, None, rong, tuple(td['mau']) if td.get('mau') else None)
            D = None
            if td.get('dan'):
                D = ve.viet_tay(td['dan'], 'Pacifico.ttf') if td.get('dan_kieu') == 'viet_tay' else ve.dan(td['dan'])
            V = ve.viet_tay(td['viet_tay'], td.get('font_viet_tay')) if td.get('viet_tay') else None
            qs = list(range(i0, i1 + 1, 4)) or [i0]
            bs = np.array([self.mat_ra(q) for q in qs])
            m = np.median(bs, 0)
            fh = m[3] - m[1]
            hx, hy = (m[0] + m[2]) / 2, (m[1] + m[3]) / 2 - 0.15 * fh
            # đáy khoá = đỉnh đầu + 0,30 × cao mặt (đầu che phần dưới chữ), lấy lúc đầu CAO nhất trong suốt tiêu đề
            # người đứng xa (mặt nhỏ) thì 0,30 × cao mặt quá ít ⇒ đầu vẫn phải che ≥ de_khoa_min × cao khoá
            kbs = [self.dinh_dau(q) + max(T['day_tren_dau'] * (b[3] - b[1]), T['de_khoa_min'] * K.h) for q, b in zip(qs, bs)]
            kb_min = float(np.percentile(kbs, 10))
            tong = K.w + (I.w + 16 if I else 0)
            kx = W / 2 - tong / 2 + K.w / 2
            giua = td.get('vi_tri') == 'giua'
            # dòng dẫn đè 22 % đỉnh khoá — nhưng KHÔNG được đè DẤU trên chữ hoa (Ả, Ở, Ồ…): ONE ERA 12/11 "Trưng bày"
            # che dấu hỏi ⇒ khoá đọc thành "GIAI THƯỞNG" ⇒ có dấu dưới dòng dẫn thì nâng dòng dẫn lên ngay trên dấu
            de = T['dan_de'] * K.h
            if D:
                dd = _dau_tren(K, 0.03 * K.w, 0.03 * K.w + D.w)
                if dd is not None: de = min(de, dd - 4)
            if giua:
                ky = H * 0.50
            else:
                kb = kb_min
                top_min = T['y_min'] + (D.h - de if D else 0)
                ky = max(top_min, kb - K.h) + K.h / 2
            kt, kbot, kl, kr = ky - K.h / 2, ky + K.h / 2, kx - K.w / 2, kx + K.w / 2
            dpos = vpos = ipos = None
            if D:
                dl = C.clamp(kl + 0.03 * K.w, C.AN_TOAN['x0'], C.AN_TOAN['x1'] - D.w)
                dd = _dau_tren(K, dl - kl, dl - kl + D.w)
                de2 = min(T['dan_de'] * K.h, dd - 4) if dd is not None else T['dan_de'] * K.h
                dpos = (dl + D.w / 2, max(T['y_min'] + D.h / 2, kt + de2 - D.h / 2))
            if V:
                vr = C.clamp(kr - 0.02 * K.w, C.AN_TOAN['x0'] + V.w, C.AN_TOAN['x1'])
                vpos = (vr - V.w / 2, kbot - T['viet_tay_de'] * V.h + V.h / 2)
            if I:
                ipos = (kr + 16 + I.w / 2, ky - 0.08 * K.h)
            ra = td.get('ra', 'chui_dau')
            P = pm(K)
            chu = []
            if ra == 'vo_chu':
                xs = ve.ranh_chu(K, K.meta['text'])
                for a, b in zip(xs[:-1], xs[1:]):
                    if b - a < 4: continue
                    xa, xb = int(max(0, a - 6)), int(min(P.shape[1], b + 6))
                    chu.append((P[:, xa:xb].copy(), (xa + xb) / 2))
            top = min(kt, dpos[1] - D.h / 2 if D else kt)
            bot = max(kbot, vpos[1] + V.h / 2 if V else kbot)
            self.tds.append(dict(i0=i0, i1=i1, K=K, D=D, V=V, I=I, kpos=(kx, ky), dpos=dpos, vpos=vpos, ipos=ipos, top=top, bot=bot,
                                 head=(hx, hy), vao=td.get('vao', 'roi'), ra=ra, sau=not giua, chu=chu))

    def ve_tieu_de(self, F, i, td, mask):
        T = C.TIEU_DE
        i0, i1 = td['i0'], td['i1']
        if i < i0 or i > i1: return
        f = i - i0; n = max(1, i1 - i0)
        mk = mask if td['sau'] else None
        s_tho = 1 + T['tho'] * f / n
        Gx, Gy = td['kpos']
        hx, hy = td['head']
        ra = td['ra']; RK = T['ra_khung'] if ra != 'vo_chu' else 14
        q = C.clamp((i - (i1 - RK)) / RK) if i > i1 - RK else 0.0

        def tho(x, y):
            return Gx + (x - Gx) * s_tho, Gy + (y - Gy) * s_tho

        # --- dẫn + viết tay: hiện mờ-nét trước khoá
        dv = T['dan_vao_khung']
        for A, pos, tre in ((td['D'], td['dpos'], 0), (td['V'], td['vpos'], 2)):
            if not A: continue
            a = C.clamp((f - tre) / dv)
            if a <= 0: continue
            x, y = pos; mo = 8 * (1 - a); al = a
            if q > 0:
                if ra == 'troi_xuong': y += 90 * C.ease_in(q)
                al *= 1 - q; mo += 7 * q
            x, y = tho(x, y)
            # vẽ sau khoá (dẫn/viết tay đè lên khoá)
            td.setdefault('_tam', []).append((A, x, y, al, mo, s_tho))
        # --- KHOÁ
        K = td['K']; vk = T['vao_khung']
        p = C.clamp((f - 2) / vk)
        kx, ky = td['kpos']; sc = 1.0; al = 1.0 if f >= 2 else 0.0; nx = ny = 0.0; trang = 0.0; mo = 0.0
        vao = td['vao']
        if p < 1:
            if vao == 'roi':
                e = C.ease_out(p); ky = _lerp(-K.h * 0.9, ky, e); sc = 1 + 0.28 * (1 - e); ny = 34 * (1 - p)
            elif vao == 'phong':
                sc = 0.15 + 0.85 * C.ease_back(p); al *= C.clamp(p * 3)
            elif vao == 'truot':
                e = C.ease_out(p); kx = _lerp(-K.w * 0.6, kx, e); nx = 80 * (1 - p)
            elif vao == 'tu_dau':
                e = C.ease_out(p); kx, ky = _lerp(hx, kx, e), _lerp(hy, ky, e); sc = 0.1 + 0.9 * C.ease_back(p, 1.2)
        if vao == 'truot':
            trang = 0.9 * (1 - C.clamp((f - 2 - vk * 0.7) / 6))
        if q > 0 and ra != 'vo_chu':
            if ra == 'chui_dau':
                e = C.ease_in(q); kx, ky = _lerp(kx, hx, e), _lerp(ky, hy, e); sc *= 1 - 0.88 * e
                al *= 1 - C.clamp((q - 0.65) / 0.35)
            else:  # troi_xuong
                ky += 90 * C.ease_in(q); al *= 1 - q; mo = 7 * q
        kx2, ky2 = tho(kx, ky)
        if q > 0 and ra == 'vo_chu':
            P = pm(K); cx0 = K.ox + K.w / 2
            for k, (S, xc) in enumerate(td['chu']):
                qk = C.clamp(q * 1.5 - k * 0.06)
                rng = np.random.default_rng(1000 + k)
                vx, rot = rng.uniform(-90, 90), rng.uniform(-50, 50)
                X = kx2 + (xc - cx0) * sc * s_tho + vx * qk
                Y = ky2 + 1100 * qk * qk - 60 * qk
                dat_P(F, S, S.shape[1] / 2, K.oy + K.h / 2, X, Y, sc=sc * s_tho, al=al * (1 - C.clamp((qk - 0.55) / 0.45)),
                      goc=rot * qk, mask=mk)
        else:
            dat(F, K, kx2, ky2, sc=sc * s_tho, al=al, nx=nx, ny=ny, trang=trang, mo=mo, mask=mk)
        if td['I'] and f >= 2:
            ix, iy = td['ipos']
            a = C.clamp((f - 2 - vk) / 5)
            if a > 0:
                ia = a * (1 - q)
                dat(F, td['I'], *tho(ix, iy), sc=(0.6 + 0.4 * C.ease_back(a)) * s_tho, al=ia, mask=mk)
        # dẫn + viết tay luôn TRƯỚC người (mẫu: đầu chỉ che khoá, không che chữ phụ)
        for A, x, y, al2, mo2, s in td.pop('_tam', []):
            dat(F, A, x, y, sc=s, al=al2, mo=mo2)

    # ---------------- SUB NGỰC
    def _sub_init(self):
        S = C.SUB
        an = [(C.khung(x['t0']), C.khung(x['t1'])) for x in self.plan.get('so_tien', []) + self.plan.get('liet_ke', [])]
        es = []
        for s in sorted(self.plan.get('sub', []), key=lambda s: s['t0']):
            i0, i1 = C.khung(s['t0']), min(self.n - 1, C.khung(s['t1']))
            if i1 <= i0 or any(a <= i0 < b for a, b in an): continue
            dong = []
            for j, d in enumerate(s.get('dong', [])):
                if not d.get('text'): continue
                kieu = d.get('kieu') or ('chinh' if j == 0 else 'phu')
                il = max(i0, C.khung(d['t'])) if d.get('t') is not None else i0
                dong.append(dict(A=ve.sub_dong(d['text'], kieu), kieu=kieu, text=d['text'], il=il, vong=bool(d.get('vong'))))
            if dong: es.append(dict(i0=i0, i1=i1, dong=dong, vao=s.get('vao')))
        # chuỗi liền nhau dùng chung vị trí
        runs, cur = [], []
        for e in es:
            if cur and e['i0'] - cur[-1]['i1'] > 3: runs.append(cur); cur = []
            cur.append(e)
        if cur: runs.append(cur)
        self.dongs = []
        for run in runs:
            m = self.mat_tb(run[0]['i0'], run[-1]['i1'])
            fh = m[3] - m[1]
            cx = C.clamp((m[0] + m[2]) / 2, S['x_min'], S['x_max'])
            cy = C.clamp((m[1] + m[3]) / 2 + S['y_mat'] * fh, S['y_min'], S['y_max'])
            for e in run: e['c'] = (cx, cy)
            truoc = None
            for k, e in enumerate(run):
                huong = 1 if k % 2 == 0 else -1      # +1: vào từ phải; −1: vào từ trái
                y = cy; prev_h = None
                for j, d in enumerate(e['dong']):
                    if prev_h is not None: y += (prev_h + d['A'].h) / 2 * S['gian_dong']
                    prev_h = d['A'].h
                    giu = truoc is not None and j < len(truoc['dong']) and truoc['dong'][j]['text'] == d['text']
                    if giu:
                        o = truoc['dong'][j]['_obj']; o['io'] = e['i1']; d['_obj'] = o; o['ra'] = None
                        continue
                    if d['kieu'] == 'to': vao = 'bat'
                    elif k == 0: vao = e.get('vao') or 'nhoe'
                    else: vao = e.get('vao') or 'day'
                    # tâm bám người, nhưng cả dòng phải nằm trong vùng an toàn (người đi sát mép — ONE ERA 63,8 s
                    # "Ngay tại Hồng Kông" tràn mép phải)
                    xd = C.clamp(cx, C.AN_TOAN['x0'] + d['A'].w / 2, C.AN_TOAN['x1'] - d['A'].w / 2)
                    o = dict(A=d['A'], x=xd, y=y, ii=d['il'], io=e['i1'], vao=vao, hv=huong, ra=None, hr=0, vong=d['vong'])
                    d['_obj'] = o; self.dongs.append(o)
                # dòng của chuỗi trước không được giữ → đẩy ra
                if truoc is not None:
                    for j, d in enumerate(truoc['dong']):
                        o = d['_obj']
                        if o['io'] == truoc['i1'] and o['ra'] is None:
                            o['ra'] = 'day'; o['hr'] = -huong; o['io'] = e['i0']
                truoc = e
            for d in run[-1]['dong']:
                if d['_obj']['ra'] is None: d['_obj']['ra'] = 'mo'
        for o in self.dongs:
            if o['ra'] is None: o['ra'] = 'mo'

    def ve_sub(self, F, i):
        S = C.SUB
        for o in self.dongs:
            if i < o['ii'] or i >= o['io'] + 4: continue
            A = o['A']; x, y = o['x'], o['y']; f = i - o['ii']
            sc, al, mo, nx, dx = 1.0, 1.0, 0.0, 0.0, 0.0
            if o['vao'] == 'day':
                p = C.clamp(f / S['day_khung']); dx = o['hv'] * S['day_px'] * (1 - C.ease_out(p)); nx = 34 * (1 - p)
                al = C.clamp(p * 2 + 0.2)
            elif o['vao'] == 'bat':
                p = C.clamp(f / S['bat_khung']); sc = 0.55 + 0.45 * C.ease_back(p, 2.2); al = C.clamp(p * 3)
            else:
                p = C.clamp(f / S['nhoe_khung']); mo = 9 * (1 - p); sc = 1.12 - 0.12 * C.ease_out(p); al = C.clamp(p * 1.6)
            if i >= o['io']:
                q = (i - o['io'] + 1) / 4.0
                if o['ra'] == 'day':
                    dx += o['hr'] * S['day_px'] * C.ease_in(q); nx = max(nx, 34 * q)
                else:
                    mo = max(mo, 6 * q)
                al *= 1 - q
            dat(F, A, x + dx, y, sc=sc, al=al, mo=mo, nx=nx)
            if o['vong'] and f >= 3:
                pv = C.clamp((f - 3) / C.VONG_VE['khung'])
                Vg = _vong(int(A.w), int(A.h), int(round(pv * 24)))
                dat(F, Vg, x + dx, y, al=al)

    # ---------------- ĐỒ HOẠ PHỤ
    def _diem_tay(self, i, tu):
        m = self.mat_ra(i); fh = m[3] - m[1]; fx, fy = (m[0] + m[2]) / 2, (m[1] + m[3]) / 2
        if isinstance(tu, (list, tuple)): return float(tu[0]), float(tu[1])
        if tu in ('tay_trai', 'tay_phai'):   # lòng bàn tay THẬT (tay.json) nếu tay đang mở, không thì ước từ mặt
            p = tay.diem(self.tay, i, tu[4:])
            if p:
                M = self.cam(i)
                return float(p[0] * M[0, 0] + M[0, 2]), float(p[1] * M[1, 1] + M[1, 2])
        if tu == 'tay_phai': x, y = fx + 1.5 * fh, fy + 3.0 * fh
        elif tu == 'giua': x, y = fx, fy + 2.4 * fh
        else: x, y = fx - 1.5 * fh, fy + 3.0 * fh
        return C.clamp(x, 60, W - 60), C.clamp(y, 200, H - 200)

    def _vet_tay(self, ben, i0, i1):
        """lòng bàn tay (toạ độ RA) từng khung i0..i1: bám tay theo tỉ lệ ICON['tay_bam'] quanh điểm mở tay đầu tiên,
        tay hạ / mất dấu thì đứng yên ở chỗ cuối; làm mượt ±3 khung. None nếu không thấy tay."""
        pts = []
        for i in range(i0, i1 + 1):
            p = tay.diem(self.tay, i, ben)
            if p:
                M = self.cam(i); p = (p[0] * M[0, 0] + M[0, 2], p[1] * M[1, 1] + M[1, 2])
            pts.append(p)
        dau = [p for p in pts[:8] if p]
        if not dau: return None
        neo = np.median(np.array(dau, np.float32), 0)
        if not (40 <= neo[0] <= W - 40 and 150 <= neo[1] <= H - 60): return None   # zoom cắt mất tay
        cuoi, ra = neo, []
        for p in pts:
            if p: cuoi = np.array(p, np.float32)
            ra.append(cuoi)
        a = np.array(ra, np.float32)
        if len(a) >= 3:
            pad = np.pad(a, ((3, 3), (0, 0)), mode='edge')
            a = np.mean(np.stack([pad[j:j + len(a)] for j in range(7)]), 0)
        return neo + C.ICON['tay_bam'] * (a - neo)

    def _lech_tay(self, vet, A, ben, i0, i1):
        """độ lệch (dx, dy) từ lòng bàn tay tới tâm đồ hoạ: ưu tiên ngay TRÊN tay (như mẫu); đè mặt / sub / tiêu đề thì
        lách ra phía NGOÀI (xa người), lên trên hoặc ngang tay — giữ trong vùng an toàn. Tính 1 lần cho cả đoạn (không giật)."""
        a = C.AN_TOAN; I = C.ICON
        cam = []
        for q in range(i0, i1 + 1, 4):
            m = self.mat_ra(q); e = 0.22 * (m[3] - m[1])
            cam.append((m[0] - e, m[1] - e, m[2] + e, m[3] + 0.6 * e, 6.0))
        for o in self.dongs:
            if o['ii'] <= i1 and o['io'] >= i0:
                cam.append((o['x'] - o['A'].w / 2 - 12, o['y'] - o['A'].h / 2 - 8, o['x'] + o['A'].w / 2 + 12,
                            o['y'] + o['A'].h / 2 + 8, 3.0))
        for td in self.tds:
            if td['i0'] <= i1 and td['i1'] >= i0: cam.append((0, td['top'], W, td['bot'], 1.0))
        # khối chữ ở dải sub: liệt kê, số tiền, ô tìm kiếm (dựng sau icon nên ước từ kế hoạch)
        for key, tren, duoi in (('liet_ke', 130, 260), ('so_tien', 90, 260), ('tim_kiem', -60, 190)):
            for x in self.plan.get(key, []):
                a0, a1 = C.khung(x['t0']), C.khung(x['t1'])
                if a0 <= i1 and a1 >= i0:
                    cy = self._y_sub(a0, a1)
                    cam.append((W * 0.04, cy - tren, W * 0.96, cy + duoi, 1.5))
        pts = [tuple(v) for v in vet[::3]] or [tuple(vet[0])]
        s = -1 if ben == 'trai' else 1

        def xau(dx, dy):
            pen = 0.0
            for px, py in pts:
                x0 = px + dx - A.w / 2; y0 = py + dy - A.h / 2; x1 = x0 + A.w; y1 = y0 + A.h
                pen += 4 * (max(0, a['x0'] - x0) + max(0, x1 - a['x1']) + max(0, a['y0'] - y0) + max(0, y1 - a['y1']))
                for r in cam:
                    ox = min(x1, r[2]) - max(x0, r[0]); oy = min(y1, r[3]) - max(y0, r[1])
                    if ox > 0 and oy > 0: pen += r[4] * ox * oy / 300.0
            return pen / len(pts)

        dy0 = -I['tay_tren'] - A.h / 2
        best = None
        for dy in (dy0, dy0 - 80, dy0 + 0.45 * A.h, dy0 - 160):
            for k in range(0, 10):
                dx = s * 60 * k
                pnl = xau(dx, dy) + abs(dx) * 0.03 + abs(dy - dy0) * 0.05
                if best is None or pnl < best[0]: best = (pnl, dx, dy)
        return best[1], best[2]

    def _tai_tay(self, px, py, lech, A):
        a = C.AN_TOAN
        return (C.clamp(px + lech[0], a['x0'] + A.w / 2, a['x1'] - A.w / 2),
                C.clamp(py + lech[1], a['y0'] + A.h / 2, a['y1'] - A.h / 2))

    def _phu_init(self):
        T = C.THE_ANH
        self.tay = tay.doc(self.work)
        self.tay_xep = tay.xep(self.plan, self.tay)     # icon / thẻ ảnh nào mọc ra từ tay nào, lúc nào
        self.thes = []
        for kth, th in enumerate(self.plan.get('the_anh', [])):
            i0, i1 = C.khung(th['t0']), min(self.n - 1, C.khung(th['t1']))
            r = self.tay_xep.get(('the_anh', kth))
            vet, tu = None, th.get('tu', 'tay_trai')
            if r:
                i0 = max(i0, C.khung(r['t0'])); tu = 'tay_' + r['ben']
                vet = self._vet_tay(r['ben'], i0, i1)
            kieu = th.get('kieu', 'phang')
            srcs = [p for p in th.get('nguon', []) if os.path.exists(p)]
            if not srcs: continue
            if kieu != 'nho': srcs = srcs[:3]
            dat_ = th.get('dat', 'duoi')
            for k, p in enumerate(srcs):
                rong = int(th.get('rong') or (T['rong_nho'] if kieu == 'nho' else T['rong_tay'] if dat_ == 'tay' else T['rong']))
                tl = T['nho_ty_le'] if kieu == 'nho' else None
                A = ve.the_anh(p, rong, t=th.get('giay'), ty_le=tl)
                if A.h > 0.42 * H:
                    A = ve.the_anh(p, int(rong * 0.42 * H / A.h), t=th.get('giay'), ty_le=tl)
                if kieu in ('nghieng', 'xep'): A = ve.phoi_canh(A, T['nghieng_do'], 8)
                if kieu == 'nho':
                    goc = dat_ if dat_ in ('tren_trai', 'tren_phai') and len(srcs) == 1 else ('tren_trai' if k % 2 == 0 else 'tren_phai')
                    # dải trên cùng; có tiêu đề cùng lúc thì đáy thẻ phải nằm trên đỉnh tiêu đề
                    tran = min([td['top'] for td in self.tds if td['i0'] <= i1 and td['i1'] >= i0] or [H]) - 18
                    cao = min(A.h, tran - C.AN_TOAN['y0'] - 10)
                    if cao < A.h:
                        A = ve.the_anh(p, max(160, int(rong * cao / A.h)), t=th.get('giay'), ty_le=tl)
                    X = C.AN_TOAN['x0'] + 8 + A.w / 2 if goc == 'tren_trai' else C.AN_TOAN['x1'] - 8 - A.w / 2
                    Y = C.AN_TOAN['y0'] + 10 + A.h / 2 + (k // 2) * (A.h + 24)
                else:
                    if dat_ == 'tay': X, Y = W / 2, H * 0.55        # nằm TRÊN lòng bàn tay — vị trí thật tính lúc vẽ
                    elif dat_ == 'giua': X, Y = W / 2, H * 0.45
                    elif dat_ == 'tren_trai': X, Y = W * 0.34, H * 0.24
                    elif dat_ == 'tren_phai': X, Y = W * 0.66, H * 0.24
                    elif dat_ == 'trai_duoi': X, Y = W * 0.38, C.AN_TOAN['y1'] - 60 - A.h / 2
                    else: X, Y = W / 2, C.AN_TOAN['y1'] - 40 - A.h / 2
                    if kieu == 'xep':
                        X += T['xep_lech'][0] * k; Y += T['xep_lech'][1] * k
                    elif len(srcs) > 1:
                        X += (k - (len(srcs) - 1) / 2) * 40
                tre = k * (3 if kieu == 'xep' else 4)
                tren = dat_ == 'tay' and vet is not None
                self.thes.append(dict(A=A, i0=i0 + tre, i1=i1, X=X, Y=Y, tu=tu, vet=vet, tre=tre, tren_tay=tren,
                                      lech=self._lech_tay(vet, A, r['ben'], i0, i1) if tren else None))
        self.icons = []
        for k, ic in enumerate(self.plan.get('icon', [])):
            i0, i1 = C.khung(ic['t0']), min(self.n - 1, C.khung(ic['t1']))
            A = ve.icon_3d(ic.get('loai', 'vi_tri'), C.ICON['co'], ic.get('nhan'), tuple(ic['mau']) if ic.get('mau') else None)
            r = self.tay_xep.get(('icon', k))
            if r:   # MỌC RA TỪ LÒNG BÀN TAY (như mẫu): vị trí thật tính lúc vẽ theo vet
                i0 = max(i0, C.khung(r['t0']))
                vet = self._vet_tay(r['ben'], i0, i1)
                if vet is not None:
                    self.icons.append(dict(A=A, i0=i0, i1=i1, X=0, Y=0, ben=r['ben'], vet=vet,
                                           lech=self._lech_tay(vet, A, r['ben'], i0, i1)))
                    continue
            m = self.mat_tb(i0, i1); fh = m[3] - m[1]
            ben = ic.get('ben', 'trai')
            X = W * (0.17 if ben == 'trai' else 0.83)
            Y = ic.get('y') * H if ic.get('y') else C.clamp((m[1] + m[3]) / 2 + 0.3 * fh, H * 0.20, H * 0.50)
            if not ic.get('y'):   # né tiêu đề đang hiện: icon xuống dưới đáy tiêu đề
                bots = [td['bot'] for td in self.tds if td['i0'] <= i1 and td['i1'] >= i0]
                if bots and Y - A.h / 2 < max(bots) + 12:
                    Y = max(bots) + 12 + A.h / 2
            self.icons.append(dict(A=A, i0=i0, i1=i1, X=X, Y=Y, ben=ben, vet=None))
        self.tims = []
        for tk in self.plan.get('tim_kiem', []):
            i0, i1 = C.khung(tk['t0']), min(self.n - 1, C.khung(tk['t1']))
            Y = tk['y'] * H if tk.get('y') else self._y_sub(i0, i1) + 120
            self.tims.append(dict(i0=i0, i1=i1, ig=C.khung(tk.get('t_go', tk['t0'] + 0.3)), chu=tk.get('chu', ''), Y=Y))
        self.tiens = []
        for st in self.plan.get('so_tien', []):
            i0, i1 = C.khung(st['t0']), min(self.n - 1, C.khung(st['t1']))
            cy = self._y_sub(i0, i1)
            tren = ve.sub_dong(st['tren'], 'chinh') if st.get('tren') else None
            so = []
            for s in st.get('so', []):
                K = ve.chu_khoa(s['text'], 'vang', C.SO_TIEN['co'], C.SO_TIEN['rong_max'])
                Dd = ve.sub_dong(s['duoi'], 'phu') if s.get('duoi') else None
                so.append(dict(K=K, D=Dd, i=max(i0, C.khung(s.get('t', st['t0'])))))
            I = ve.icon_net(st['icon'], 96) if st.get('icon') else None
            self.tiens.append(dict(i0=i0, i1=i1, cy=cy, tren=tren, so=so, I=I))
        self.logos = []
        for lg in self.plan.get('logo', []):
            if not lg.get('nguon') or not os.path.exists(lg['nguon']): continue
            A = ve.logo(lg['nguon'], int(lg.get('rong', C.LOGO['rong'])))
            self.logos.append(dict(A=A, i0=C.khung(lg['t0']), i1=min(self.n - 1, C.khung(lg['t1'])),
                                   Y=C.LOGO['y'] + A.h / 2, sau=lg.get('sau_nguoi', True)))
        self.lks = []
        for lk in self.plan.get('liet_ke', []):
            i0, i1 = C.khung(lk['t0']), min(self.n - 1, C.khung(lk['t1']))
            K = ve.chu_khoa(lk.get('khoa', 'Là'), lk.get('kieu', 'tim'), C.LIET_KE['khoa_co'], W * C.LIET_KE['khoa_rong'])
            cy = self._y_sub(i0, i1)
            ds = [dict(A=ve.sub_dong(d['text'], d.get('kieu', 'list')), i=max(i0, C.khung(d.get('t', lk['t0']))))
                  for d in lk.get('dong', []) if d.get('text')]
            self.lks.append(dict(i0=i0, i1=i1, K=K, cy=cy, ds=ds))

    def _y_sub(self, i0, i1):
        m = self.mat_tb(i0, i1); fh = m[3] - m[1]
        return C.clamp((m[1] + m[3]) / 2 + C.SUB['y_mat'] * fh, C.SUB['y_min'], C.SUB['y_max'])

    def ve_the(self, F, i):
        T = C.THE_ANH
        for th in self.thes:
            if i < th['i0'] or i > th['i1']: continue
            f = i - th['i0']; g = th['i1'] - i
            A = th['A']
            if th['vet'] is not None:
                hx, hy = (float(v) for v in th['vet'][min(f + th['tre'], len(th['vet']) - 1)])
            else:
                hx, hy = self._diem_tay(th['i0'], th['tu'])
            X1, Y1 = th['X'], th['Y']
            if th['tren_tay']:
                X1, Y1 = self._tai_tay(hx, hy, th['lech'], A)
            p = C.clamp(f / T['vao_khung'])
            X = _lerp(hx, X1, C.ease_out(p)); Y = _lerp(hy, Y1, C.ease_out(p))
            sc = 0.12 + 0.88 * C.ease_back(p, 1.3); al = C.clamp(p * 3)
            if g < T['ra_khung']:
                q = 1 - g / T['ra_khung']
                X, Y = _lerp(X, hx, C.ease_in(q)), _lerp(Y, hy, C.ease_in(q)); sc *= 1 - 0.85 * C.ease_in(q)
                al *= 1 - C.clamp((q - 0.6) / 0.4)
            Y += 5 * math.sin(2 * math.pi * i / FPS / 2.2)
            dat(F, A, X, Y, sc=sc, al=al)

    def ve_icon(self, F, i):
        I = C.ICON
        for ic in self.icons:
            if i < ic['i0'] or i > ic['i1']: continue
            f = i - ic['i0']; g = ic['i1'] - i
            if ic['vet'] is not None:
                # mẫu: icon nhỏ xíu NGAY lòng bàn tay → lớn + nảy lên nằm trên tay trong 6 khung, nhún nhẹ, ra thì thu về tay
                px, py = (float(v) for v in ic['vet'][min(f, len(ic['vet']) - 1)])
                X1, Y1 = self._tai_tay(px, py, ic['lech'], ic['A'])
                p = C.clamp(f / I['tay_vao_khung']); e = C.ease_out(p)
                X, Y = _lerp(px, X1, e), _lerp(py, Y1, e)
                sc = I['tay_tu'] + (1 - I['tay_tu']) * C.ease_back(p, 1.5); al = C.clamp(p * 3)
                Y += I['tay_nhun'] * math.sin(2 * math.pi * f / FPS / 1.6) * p
                if g < 6:
                    q = C.ease_in(1 - g / 6)
                    X, Y = _lerp(X, px, q), _lerp(Y, py, q); sc *= 1 - 0.88 * q; al *= 1 - C.clamp((q - 0.5) / 0.5)
                dat(F, ic['A'], X, Y, sc=sc, al=al)
                continue
            p = C.clamp(f / I['vao_khung'])
            s = -1 if ic['ben'] == 'trai' else 1
            X = ic['X'] + s * 300 * (1 - C.ease_out(p)); sc = 0.3 + 0.7 * C.ease_back(p, 1.6); al = C.clamp(p * 2.5)
            Y = ic['Y'] + I['nhun'] * math.sin(2 * math.pi * f / FPS / 1.6)
            if g < 6:
                q = 1 - g / 6; sc *= 1 - 0.9 * C.ease_in(q); al *= 1 - C.clamp((q - 0.5) / 0.5)
            dat(F, ic['A'], X, Y, sc=sc, al=al, nx=20 * (1 - p))

    def ve_tim(self, F, i):
        T = C.TIM_KIEM
        for tk in self.tims:
            if i < tk['i0'] or i > tk['i1']: continue
            f = i - tk['i0']; g = tk['i1'] - i
            k = int(max(0, i - tk['ig']) * T['ky_tu_khung'])
            go_xong = k >= len(tk['chu'])
            con = (not go_xong) or ((i // 8) % 2 == 0)
            A = _o_tim(tk['chu'][:k], con if i >= tk['ig'] - 6 else False)
            p = C.clamp(f / T['vao_khung'])
            X = _lerp(-W * 0.2, W / 2, C.ease_out(p)); sc = 1.35 - 0.35 * C.ease_out(p)
            al, mo = 1.0, 0.0
            if g < T['ra_khung']:
                q = 1 - g / T['ra_khung']; al = 1 - q; mo = 8 * q
            dat(F, A, X, tk['Y'], sc=sc, al=al, mo=mo, nx=60 * (1 - p))

    def ve_tien(self, F, i):
        S = C.SO_TIEN
        for st in self.tiens:
            if i < st['i0'] or i > st['i1']: continue
            f = i - st['i0']; g = st['i1'] - st['i0'] - f
            alo = 1.0 if g >= 5 else g / 5.0
            cy = st['cy']
            if st['tren']:
                p = C.clamp(f / 5)
                dat(F, st['tren'], W / 2, cy, al=C.clamp(p * 2) * alo, mo=6 * (1 - p), sc=1.1 - 0.1 * C.ease_out(p))
            for k, s in enumerate(st['so']):
                nxt = st['so'][k + 1]['i'] if k + 1 < len(st['so']) else None
                if i < s['i'] - S['vet_khung'] or (nxt is not None and i >= nxt + 5): continue
                K = s['K']
                ky = cy + ((st['tren'].h / 2 if st['tren'] else 0) + K.h / 2) * 0.86
                if i < s['i']:      # vệt tốc độ chạy trước số
                    pv = (i - (s['i'] - S['vet_khung']) + 1) / (S['vet_khung'] + 2)
                    Vt = _vet(int(K.w), int(K.h), int(round(pv * 12)))
                    dat(F, Vt, W / 2, ky)
                    continue
                p = C.clamp((i - s['i']) / S['vao_khung'])
                dx = -W * 0.6 * (1 - C.ease_out(p)); nx = 70 * (1 - p); al = C.clamp(p * 2.5) * alo
                if p < 1:
                    pv = (S['vet_khung'] + 1 + (i - s['i'])) / (S['vet_khung'] + 2)
                    if pv <= 1.2:
                        Vt = _vet(int(K.w), int(K.h), int(round(min(1, pv) * 12)))
                        dat(F, Vt, W / 2, ky, al=1 - p)
                if nxt is not None and i >= nxt:
                    q = (i - nxt + 1) / 5.0; dx += W * 0.6 * C.ease_in(q); nx = 70 * q; al *= 1 - q
                dat(F, K, W / 2 + dx, ky, al=al, nx=nx)
                if s['D']:
                    a2 = C.clamp((i - s['i'] - 2) / 4) * al
                    dx2 = W / 2 + K.w / 2 - s['D'].w / 2 - (st['I'].w * 0.8 if st['I'] else 0) + dx * 0.6
                    yd = ky + K.h / 2 - s['D'].h * 0.25
                    dat(F, s['D'], dx2, yd, al=a2, mo=5 * (1 - C.clamp((i - s['i'] - 2) / 4)))
                    if st['I']:
                        dat(F, st['I'], dx2 + s['D'].w / 2 + st['I'].w * 0.45, yd - 6, al=a2,
                            sc=0.6 + 0.4 * C.ease_back(C.clamp((i - s['i'] - 2) / 5)))

    def ve_logo(self, F, i, mask):
        for lg in self.logos:
            if i < lg['i0'] or i > lg['i1']: continue
            f = i - lg['i0']; g = lg['i1'] - i
            p = C.clamp(f / C.LOGO['vao_khung'])
            Y = _lerp(-lg['A'].h * 0.6, lg['Y'], C.ease_back(p, 1.1)); al = C.clamp(p * 2)
            mo = 0.0
            if g < 6: q = 1 - g / 6; al *= 1 - q; mo = 6 * q
            dat(F, lg['A'], W / 2, Y, al=al, mo=mo, ny=26 * (1 - p), mask=mask if lg['sau'] else None)

    def ve_liet_ke(self, F, i):
        L = C.LIET_KE
        for lk in self.lks:
            if i < lk['i0'] or i > lk['i1']: continue
            f = i - lk['i0']; g = lk['i1'] - i
            alo = 1.0 if g >= 5 else g / 5.0
            K = lk['K']
            p = C.clamp(f / 8)
            kx = C.AN_TOAN['x0'] + 20 + K.w / 2; ky = lk['cy']
            dat(F, K, kx, ky, sc=0.2 + 0.8 * C.ease_back(p, 1.6), al=C.clamp(p * 3) * alo)
            hien = [d for d in lk['ds'] if d['i'] <= i][-L['toi_da']:]
            x0 = kx + K.w / 2 + 28
            gd = L['gian_dong']
            tong = sum(d['A'].h for d in hien) * gd
            y = ky - tong / 2
            for d in hien:
                pd = C.clamp((i - d['i']) / L['vao_khung'])
                A = d['A']
                y += A.h * gd / 2
                dat(F, A, x0 + A.w / 2 + 300 * (1 - C.ease_out(pd)), y, al=C.clamp(pd * 2.5) * alo, nx=40 * (1 - pd))
                y += A.h * gd / 2

    # ---------------- chuyển cảnh phủ
    def phu_chuyen(self, F, i):
        ch = self._chuyen_tai(i)
        if not ch or ch[0] not in ('loe_doc', 'chay_phim'): return F
        kieu, d, u = ch
        xs = np.arange(W, dtype=np.float32)[None, :]; ys = np.arange(H, dtype=np.float32)[:, None]
        cf = C.CHUYEN[kieu]
        tong = cf['truoc'] + cf['sau']
        ph = (d + cf['truoc'] + 0.5) / tong          # 0 → 1 suốt hiệu ứng
        if kieu == 'loe_doc':
            xc = W * (-0.15 + 1.3 * ph)
            core = np.exp(-((xs - xc) / 70.0) ** 2); glow = np.exp(-((xs - xc) / 330.0) ** 2)
            L = (core * 1.0 + glow * 0.55) * u + 0.45 * u ** 3
            L = np.broadcast_to(np.clip(L, 0, 1), (H, W))[..., None] * np.array([1.0, 0.95, 0.86], np.float32)
        else:
            if ph < 0.45:     # cam ấm bốc từ đáy + đốm nóng
                k = ph / 0.45
                g = np.clip(1.15 - (H - ys) / (H * (0.35 + 0.9 * k)), 0, 1) ** 1.3
                spot = np.exp(-(((xs - W * 0.55) / 260) ** 2 + ((ys - H * 0.72) / 360) ** 2))
                L = (g * 0.85 + spot * 0.9) * (0.4 + 0.6 * k)
                L = np.clip(L, 0, 1)[..., None] * np.array([1.0, 0.62, 0.16], np.float32)
                L = L + (spot * k)[..., None] * np.array([0.3, 0.35, 0.3], np.float32)
            elif ph < 0.62:   # loé trắng gần như toàn khung
                L = np.full((H, W, 1), 0.92, np.float32) * np.array([1.0, 0.97, 0.92], np.float32)
            else:             # đỏ quét từ mép trái rồi tắt
                k = (ph - 0.62) / 0.38
                g = np.clip(1 - xs / (W * (1.1 - 0.7 * k)), 0, 1) ** 0.8 * (1 - k)
                L = np.broadcast_to(g, (H, W))[..., None] * np.array([0.95, 0.12, 0.08], np.float32)
            L = np.clip(L, 0, 1)
        return 1 - (1 - F) * (1 - L)

    # ---------------- 1 khung
    def khung(self, i, src):
        F, M = self.nen(i, src)
        can_mask = any(td['sau'] and td['i0'] <= i <= td['i1'] for td in self.tds) or \
            any(lg['sau'] and lg['i0'] <= i <= lg['i1'] for lg in self.logos)
        mask = self.mask(i, M, src) if can_mask else None
        self.ve_logo(F, i, mask)
        for td in self.tds: self.ve_tieu_de(F, i, td, mask)
        self.ve_the(F, i)
        self.ve_icon(F, i)
        self.ve_liet_ke(F, i)
        self.ve_tien(F, i)
        self.ve_sub(F, i)
        self.ve_tim(F, i)
        F = self.phu_chuyen(F, i)
        return (np.clip(F, 0, 1) * 255 + 0.5).astype(np.uint8)


# ------------------------------------------------------------------ chạy
def ten_ra(video_goc, duoi='_BSV'):
    d, b = os.path.dirname(os.path.abspath(video_goc)), os.path.splitext(os.path.basename(video_goc))[0]
    p = os.path.join(d, b + duoi + '.mp4'); k = 2
    while os.path.exists(p):
        p = os.path.join(d, f'{b}{duoi}_ban{k}.mp4'); k += 1
    return p


def dung_video(plan, work, tieng, out):
    D = Dung(plan, work)
    if D.kho is None or not D.kho.ok:
        print('  ⚠ chưa có mặt nạ người → tiêu đề nằm TRÊN người (chạy run.py nguoi trước)')
    sz = W * H * 3
    dec = subprocess.Popen(['ffmpeg', '-v', 'error', '-i', D.src, '-vf', GRADE, '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'],
                           stdout=subprocess.PIPE)
    enc = subprocess.Popen(['ffmpeg', '-y', '-v', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS),
                            '-i', '-', '-i', tieng, '-map', '0:v', '-map', '1:a', '-c:v', 'libx264', '-preset', 'medium',
                            '-crf', '18', '-pix_fmt', 'yuv420p', '-color_primaries', 'bt709', '-color_trc', 'bt709',
                            '-colorspace', 'bt709', '-c:a', 'aac', '-b:a', '192k', '-shortest', '-movflags', '+faststart', out],
                           stdin=subprocess.PIPE)
    t0 = time.time(); i = 0
    try:
        while i < D.n:
            buf = dec.stdout.read(sz)
            if len(buf) < sz: break
            src = np.frombuffer(buf, np.uint8).reshape(H, W, 3)
            enc.stdin.write(D.khung(i, src).tobytes())
            i += 1
            if i % 150 == 0:
                el = time.time() - t0
                print(f'  dựng {i}/{D.n} khung · {el:.0f} s · còn ~{el / i * (D.n - i):.0f} s', flush=True)
    finally:
        dec.stdout.close(); dec.wait()
        enc.stdin.close(); enc.wait()
    print(f'  dựng xong {i} khung trong {time.time() - t0:.0f} s → {out}')
    return out


def doc_khung(src, t):
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-ss', f'{max(0, t):.3f}', '-i', src, '-frames:v', '1', '-vf', GRADE,
                          '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], capture_output=True).stdout
    if len(raw) < W * H * 3: return None
    return np.frombuffer(raw[:W * H * 3], np.uint8).reshape(H, W, 3)


def xem_truoc(plan, work, moc, out_jpg, cot=6, rong_o=300):
    """dựng các khung ở mốc [(giây, nhãn)] → 1 tờ ảnh (soi trước khi dựng thật)."""
    D = Dung(plan, work)
    oh = int(rong_o * H / W)
    tiles = []
    fo = C.font('BeVietnamPro-Bold.ttf', 18)
    for t, nhan in moc:
        i = min(D.n - 1, C.khung(t))
        src = doc_khung(D.src, i / FPS)
        if src is None: continue
        im = Image.fromarray(D.khung(i, src)).resize((rong_o, oh), Image.LANCZOS)
        o = Image.new('RGB', (rong_o, oh + 46), (18, 18, 18)); o.paste(im, (0, 46))
        d = ImageDraw.Draw(o)
        d.text((5, 3), f'{t:.2f}s', font=fo, fill=(255, 220, 80))
        d.text((5, 23), nhan[:30], font=fo, fill=(235, 235, 235))
        tiles.append(o)
    if not tiles: return None
    r = (len(tiles) + cot - 1) // cot
    sh = Image.new('RGB', (cot * (rong_o + 6), r * (oh + 52)), (8, 8, 8))
    for k, o in enumerate(tiles):
        sh.paste(o, ((k % cot) * (rong_o + 6), (k // cot) * (oh + 52)))
    sh.save(out_jpg, quality=88)
    return out_jpg
