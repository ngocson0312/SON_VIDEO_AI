# -*- coding: utf-8 -*-
"""Bộ dựng: đọc ke_hoach.json → từng khung (máy quay ảo + chuyển cảnh + HUD + chữ + glitch + khung điện ảnh)
→ x264 → trộn nhạc (đoạn đã chọn, vào dần, dừng cứng) → −14 LUFS → mp4. Dùng chung cho xem / duyệt."""
import os, math, subprocess, time
import numpy as np, cv2
import chung as C
import hieu_ung as E
import hud as HUDM
import chu as CHU
import nguoi as NG
import tay as TAY
import hashlib

FPS = C.FPS


def cham_muot(p, info, ss, dai, work):
    """Clip 24/30 fps phải làm chậm (toc < 0,95): nội suy chuyển động (minterpolate mci) lên 60 fps 1 lần, lưu
    work/cham/ — trộn khung (framerate) để lại bóng ma ở tay / vật chạy nhanh. → (đường dẫn, info mới)."""
    key = hashlib.md5(f'{os.path.abspath(p)}|{ss:.3f}|{dai:.3f}'.encode('utf-8')).hexdigest()[:10]
    ra = os.path.join(work, 'cham', f'{os.path.splitext(os.path.basename(p))[0]}_{key}.mp4')
    if not os.path.exists(ra):
        os.makedirs(os.path.dirname(ra), exist_ok=True)
        C.in_ra(f'  làm chậm mượt (nội suy chuyển động) {os.path.basename(p)} {ss:.2f}→{ss + dai:.2f} s … (1 lần, ~1–2 phút)')
        vf = ''
        if info.get('hdr'):
            vf = ('zscale=t=linear:npl=100,format=gbrpf32le,zscale=p=bt709,tonemap=hable:desat=0,'
                  'zscale=t=bt709:m=bt709:r=tv,format=yuv420p,')
        vf += 'minterpolate=fps=60:mi_mode=mci:mc_mode=aobmc:me_mode=bidir:vsbmc=1'
        tam = ra + '.tmp.mp4'
        C.run(['ffmpeg', '-y', '-v', 'error', '-ss', f'{ss:.3f}', '-i', p, '-t', f'{dai:.3f}', '-an', '-vf', vf,
               '-c:v', 'libx264', '-crf', '14', '-preset', 'veryfast', '-pix_fmt', 'yuv420p', tam])
        os.replace(tam, ra)
    return ra, dict(info, fps=60.0, hdr=False, dur=dai)


def _g(arr, i, mac_dinh=0.0):
    return arr[i] if 0 <= i < len(arr) else mac_dinh


class Nguon:
    """Đọc clip đã thu về cỡ 'phủ kín' khung ra × q, đúng 30 fps, có tua nhanh/chậm (toc)."""

    def __init__(self, path, info, W, H, ss, toc, la_anh=False, xoay=0):
        self.path, self.info, self.toc, self.la_anh = path, info, max(0.1, float(toc)), la_anh
        self.xoay = int(xoay or 0)
        w, h = info['w'], info['h']
        if self.xoay in (90, -90, 270):
            w, h = h, w
        c = max(W / w, H / h)
        q = min(1.25, max(1.0, 1.0 / c)) if c < 1 else 1.0
        self.dw = int(round(w * c * q / 2) * 2); self.dh = int(round(h * c * q / 2) * 2)
        self.q = q
        self.ss = max(0.0, ss)
        self.p = None; self.cur = -1; self.last = None; self.het = 0
        if la_anh:
            im = cv2.imdecode(np.fromfile(path, np.uint8), cv2.IMREAD_COLOR)
            if self.xoay:
                im = cv2.rotate(im, {90: cv2.ROTATE_90_CLOCKWISE, -90: cv2.ROTATE_90_COUNTERCLOCKWISE,
                                     270: cv2.ROTATE_90_COUNTERCLOCKWISE, 180: cv2.ROTATE_180}[self.xoay])
            self.last = cv2.resize(im, (self.dw, self.dh), interpolation=cv2.INTER_AREA)

    def _mo(self, k):
        self.dong()
        st = self.ss + k * self.toc / FPS
        vf = f'setpts=(PTS-STARTPTS)/{self.toc:.5f},fps={FPS}'
        fps0 = float(self.info.get('fps') or 30)
        if self.toc < 0.95 and fps0 < 45:
            # clip 24/30 fps làm chậm: nội suy trộn khung cho đỡ giật (khung lặp)
            vf = f'framerate=fps={min(120.0, fps0 / self.toc):.3f},' + vf
        if self.info.get('hdr'):
            vf = ('zscale=t=linear:npl=100,format=gbrpf32le,zscale=p=bt709,tonemap=hable:desat=0,'
                  'zscale=t=bt709:m=bt709:r=tv,format=yuv420p,') + vf
        # xoay thêm (clip quay nghiêng điện thoại): -90 = xoay trái (ngược kim đồng hồ), 90 = xoay phải
        vf += {90: ',transpose=1', -90: ',transpose=2', 270: ',transpose=2', 180: ',hflip,vflip'}.get(self.xoay, '')
        vf += f',scale={self.dw}:{self.dh}:flags=bicubic'
        self.p = subprocess.Popen(['ffmpeg', '-v', 'error', '-ss', f'{st:.3f}', '-i', self.path, '-an', '-vf', vf,
                                   '-pix_fmt', 'bgr24', '-f', 'rawvideo', '-'], stdout=subprocess.PIPE,
                                  stderr=subprocess.DEVNULL, bufsize=self.dw * self.dh * 3 * 2)
        self.cur = k - 1

    def get(self, k):
        if self.la_anh:
            return self.last
        k = max(0, k)
        if self.p is None or k < self.cur or k > self.cur + 45:
            self._mo(k)
        n = self.dw * self.dh * 3
        while self.cur < k:
            raw = self.p.stdout.read(n) if self.p else b''
            if len(raw) < n:
                self.het += 1
                if self.last is None:
                    self.last = np.zeros((self.dh, self.dw, 3), np.uint8)
                self.cur = k
                return self.last
            self.last = np.frombuffer(raw, np.uint8).reshape(self.dh, self.dw, 3)
            self.cur += 1
        return self.last

    def dong(self):
        if self.p:
            try:
                self.p.stdout.close(); self.p.kill(); self.p.wait()
            except Exception:
                pass
        self.p = None


class Dung:
    def __init__(self, plan, work):
        self.plan, self.work = plan, work
        self.kho = plan.get('kho', '16:9')
        self.W, self.H = C.KHO[self.kho]
        nh = plan['nhac']
        self.P = nh['phach_s']; self.B = nh['nhip_s']
        self.t_ket_nhac = nh['ket_nhac']
        self.t_den = self.t_ket_nhac + C.AM['giu_hinh']
        self.T = self.t_den + C.AM['den']
        self.canh = plan['canh']
        self.s = [(-1e9 if i == 0 else C.moc_cat(c)) for i, c in enumerate(self.canh)]
        res = plan.get('res')
        tn = C.doc_json(os.path.join(work, 'tai_nguyen.json')) if os.path.exists(os.path.join(work, 'tai_nguyen.json')) else {}
        infos = {v['file']: v for v in tn.get('video', [])}
        for i, c in enumerate(self.canh):
            p = C.tim_file(res, c['nguon'])
            if not p:
                raise FileNotFoundError(f'Cảnh {c["id"]}: không thấy nguồn {c["nguon"]}')
            la_anh = os.path.splitext(p)[1].lower() in C.ANH_EXT
            if la_anh:
                im = cv2.imdecode(np.fromfile(p, np.uint8), cv2.IMREAD_COLOR)
                info = dict(w=im.shape[1], h=im.shape[0], fps=0, dur=1e9, hdr=False)
            else:
                info = infos.get(c['nguon']) or C.probe(p)
            kieu = (c.get('chuyen') or {}).get('kieu', 'cat') if i else 'cat'
            lead = C.CHUYEN[kieu]['truoc'] + 0.1
            toc = float(c.get('toc', 1.0))
            ss = float(c.get('tu_giay', 0)) - lead * toc
            c['_info'] = info
            ss = max(0.0, ss)
            c['_tref'] = c['t0'] - (float(c.get('tu_giay', 0)) - ss) / max(0.1, toc)
            c['_ss_goc'] = ss
            dai = (c['t1'] - c['t0'] + lead + 0.4) * toc
            if not la_anh and toc < 0.95 and float(info.get('fps') or 30) < 45:
                p2, info2 = cham_muot(p, info, ss, dai, work)
                c['_nguon'] = Nguon(p2, info2, self.W, self.H, 0.0, toc, False, c.get('xoay', 0))
            else:
                c['_nguon'] = Nguon(p, info, self.W, self.H, ss, toc, la_anh, c.get('xoay', 0))
            if not la_anh and any(e['kieu'] == 'manh_tay' for e in c.get('hieu_ung', [])):
                c['_tay'] = TAY.do_clip(p, info, ss, dai, c.get('xoay', 0), work)
        ch = plan.get('chu', {})
        self.tieu_de = CHU.TieuDe(ch['tieu_de'], self.W, self.H, self.kho) if ch.get('tieu_de') else None
        self.dong_xe = CHU.DongXe(ch['dong_xe'], self.W, self.H, self.kho) if ch.get('dong_xe') else None
        hd = plan.get('hud', {})
        cam = []
        if self.tieu_de: cam.append(self.tieu_de.hop())
        self.hud = HUDM.Hud(self.W, self.H, self.P, nh['F'], seed=hd.get('seed', 7), vung_cam=cam) if hd.get('bat', True) else None
        self.mau = plan.get('mau', {}).get('bat', True)
        self.manh = {}
        self._mn = {}
        self._Mlast = {}

    # ------------------------------------------------------------ máy quay ảo của 1 cảnh
    def _zoom_canh(self, c, t):
        z = float(c.get('zoom', 1.0))
        d = float(c.get('dong', 0.0))
        if d:
            r = math.log(1 + abs(d))
            z *= math.exp(r * (t - c['t0'])) if d > 0 else math.exp(r * (c['t1'] - t))
        for e in c.get('hieu_ung', []):
            if e['kieu'] == 'dap_zoom':
                te = e['t']; dai = e.get('dai', C.DAP_ZOOM['dai']); ln = e.get('len', C.DAP_ZOOM['len'])
                if t >= te - dai:
                    z *= 1 + (ln - 1) * C.ease_io((t - (te - dai)) / dai)
            elif e['kieu'] == 'nay':
                k = int(round((t - (e['t'] - len(C.NAY) / FPS)) * FPS))
                if 0 <= k < len(C.NAY):
                    z *= C.NAY[k]
        return z

    def _bien(self, i, t, zoom=1.0, dx=0.0, dy=0.0):
        """→ (khung nguồn, ma trận 2×3 nguồn → khung ra, k)."""
        c = self.canh[i]
        ng = c['_nguon']
        k = int(round((t - c['_tref']) * FPS))
        src = ng.get(k)
        sh, sw = src.shape[:2]
        z = max(1.0, min(C.ZOOM_TOI_DA * 1.6, self._zoom_canh(c, t) * zoom))
        S = z / ng.q
        tam = c.get('tam', [0.5, 0.5])
        fx, fy = tam[0] * sw, tam[1] * sh
        hw, hh = self.W / (2 * S), self.H / (2 * S)
        fx = min(max(fx, hw), sw - hw) if sw >= 2 * hw else sw / 2
        fy = min(max(fy, hh), sh - hh) if sh >= 2 * hh else sh / 2
        M = np.float64([[S, 0, self.W / 2 - S * fx + dx], [0, S, self.H / 2 - S * fy + dy]])
        return src, M, k

    def khung_canh(self, i, t, zoom=1.0, dx=0.0, dy=0.0, them=None):
        """them = phép phóng 2×3 thêm sau cùng (vd đẩy sát vào 2 bàn tay khi chuyển cảnh)."""
        src, M, k = self._bien(i, t, zoom, dx, dy)
        if them is not None:
            M = (np.vstack([them, [0, 0, 1]]) @ np.vstack([M, [0, 0, 1]]))[:2]
        self._Mlast[i] = (t, M, src.shape[1], src.shape[0], k)
        out = cv2.warpAffine(src, M.astype(np.float32), (self.W, self.H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
        if self.mau:
            out = E.cham_mau(out)
        return out

    def _tay_px(self, i, t):
        """Tay / đầu ngón / mặt theo PIXEL khung ra của cảnh i tại t (dùng ma trận vừa vẽ) → dict hoặc None."""
        c = self.canh[i]
        if not c.get('_tay') or i not in self._Mlast:
            return None
        _, M, sw, sh, k = self._Mlast[i]
        s_goc = c['_ss_goc'] + k * c['_nguon'].toc / FPS
        v = TAY.tai(c['_tay'], s_goc)
        if v is None:
            return None
        ap = lambda p: M @ np.array([p[0] * sw, p[1] * sh, 1.0])
        sc = M[0, 0]
        o = {kk: ap(v[kk]) for kk in ('L', 'R') + TAY.NGON if kk in v}
        o['s'] = v['s'] * max(sw, sh) * sc
        o['tc'] = v['tc']
        o['mat'] = None
        mat = v['mat']
        if mat is not None and mat[2] > 0:
            q = ap(mat[:2]); o['mat'] = [q[0], q[1], mat[2] * sw * sc, mat[3] * sh * sc]
        return o

    def _ve_manh_tay(self, j, t, img, e):
        """Mảnh cảnh sau ghim vào đầu ngón (dải chụm → khung chữ L), ngón + đầu người vẽ lại phía trước.
        → (ảnh, tứ giác mảnh, mặt nạ 'tay + mảnh' cho lớp lao về máy khi chuyển cảnh) hoặc (ảnh, None, None)."""
        MT = C.MANH_TAY
        v = self._tay_px(j, t)
        if v is None or 'Li' not in v:
            return img, None, None
        tuoi = t - e['t0']
        # dải chỉ hiện khi 2 đầu ngón đã TÁCH ra (kéo ra từ chỗ chụm, không mọc sẵn giữa 2 tay)
        h0, h1 = MT['hien_keo']
        a = min(1.0, tuoi / 0.07) * min(1.0, v['tc'] * 1.5) * min(1.0, max(0.0, (TAY.do_keo(v) - h0) / (h1 - h0)))
        if a <= 0.01:
            return img, None, None
        # sợi mảnh → dải bản to theo NHỊP (mẫu: sợi tới phách 3 sau F, nở bản tới phách 3,5)
        P_ = float(self.plan['nhac'].get('phach_s', 0.5125))
        b0, b1 = e.get('ban_phach', MT['ban_phach'])
        ban = (tuoi - b0 * P_) / max(1e-3, (b1 - b0) * P_)
        P = TAY.the_tay(v['Li'], v['Lt'], v['Ri'], v['Rt'], v['s'], ban, v.get('Lg'), v.get('Rg'), v.get('Lc'), v.get('Rc'))
        moi = self.khung_canh(j + 1, t)
        nguoi = self._mat_na(j, t, img)
        diem = {kk: v[kk] for kk in ('L', 'R') + TAY.NGON if kk in v}
        tay = TAY.mat_na_che(img, nguoi, v['mat'], P, v['s'], dau=False, diem=diem)
        che = TAY.mat_na_che(img, nguoi, v['mat'], P, v['s']) if MT.get('che_dau') else tay
        out = E.manh_tay(img, moi, P, a, MT['vien'], che, img)
        # lớp lao về máy = mảnh ∪ bàn tay (KHÔNG gồm đầu — mặt người không phóng to theo)
        mk = np.zeros(img.shape[:2], np.uint8)
        cv2.fillPoly(mk, [P.astype(np.int32)], 255, cv2.LINE_AA)
        lop = mk.astype(np.float32) / 255 * a
        lop = np.maximum(lop, tay)
        return out, P, lop

    # ------------------------------------------------------------ chuyển cảnh
    def _huong(self, i):
        c = self.canh[i]
        h = (c.get('chuyen') or {}).get('huong')
        if h is None:
            h = [90, 35, 0, 145, 90, 0][i % 6]
        return float(h)

    def _hinh_hoc(self, kieu, pha, i, idx, m=None):
        """Phần biến đổi hình học (zoom, dịch) của chuyển cảnh cho cảnh i."""
        W = self.W
        z, dx, dy = 1.0, 0.0, 0.0
        sc = W / 1920.0
        if kieu == 'luot_trang':
            L = C.LUOT
            if pha == 'truoc':
                dx = sum(L['toc_truoc'][:idx + 1]) * sc
            else:
                dx = -sum(L['toc_sau'][idx:]) * sc
        elif kieu == 'lia_nhoe':
            L = C.LIA
            a = math.radians(self._huong(i if pha == 'sau' else i + 1))
            if pha == 'truoc':
                d = _g(L['dich_truoc'], idx) * W
                dx, dy = d * math.cos(a), d * math.sin(a)
            else:
                d = -_g(L['dich_sau'], idx) * W
                rx, ry = E.rung(idx, W, seed=i)
                dx, dy = d * math.cos(a) + rx, d * math.sin(a) + ry
                z = _g(L['zoom_sau'], idx, 1.0)
        elif kieu == 'gon_song' and pha == 'sau':
            z = 1.0 + 0.02 * _g(C.SONG['bien_sau'], idx) / 0.03
        return z, dx, dy

    def _diem_anh_sau(self, kieu, img, i, t, k):
        W = self.W
        if kieu == 'nhoe_loe' or kieu == 'manh_vo':
            if kieu == 'manh_vo':
                fb = 0 if self.canh[i - 1].get('_tay') else C.MANH['flashback']    # mở đầu (người cầm mảnh): không loé lại
                if k < fb:
                    return self._loe_vo(i, t, img)
                k -= fb
            N = C.NHOE_LOE
            img = E.nhoe(img, _g(N['sigma'], k) * W)
            if k < N['loe_khung']:
                img = E.tron_trang(img, N['loe'] * math.exp(-k / N['loe_tau']), khu_mau=0.3 * math.exp(-k / 3))
        elif kieu == 'luot_trang':
            L = C.LUOT
            img = E.nhoe_ngang(img, _g(L['toc_sau'], k) * W / 1920 * 1.6)
            img = E.tron_trang(img, _g(L['trang_sau'], k), khu_mau=_g(L['trang_sau'], k))
        elif kieu == 'gon_song':
            S = C.SONG
            img = E.nhoe(img, _g(S['nhoe_sau'], k) * W / 1920)
            img = E.song(img, _g(S['bien_sau'], k) * W, S['buoc_song'] * W, k * 0.9, xoay_do=-3 * _g(S['bien_sau'], k) / 0.03)
        elif kieu == 'khoi':
            img = E.khoi(img, _g(C.KHOI['bien_sau'], k) * W, k + 9, 0.0, seed=i)
        elif kieu == 'lia_nhoe':
            img = E.nhoe_huong(img, _g(C.LIA['nhoe_sau'], k) * W, self._huong(i))
        return img

    def _diem_anh_truoc(self, kieu, img, i, t, idx, m):
        """Cảnh i sắp hết, cảnh i+1 sắp vào (idx = 0..m-1 trong cửa sổ trước)."""
        W = self.W
        if kieu == 'manh_vo':
            ch = self.canh[i + 1].get('chuyen') or {}
            u = (idx + 1) / m
            ztt = 1.0
            if u >= C.MANH['tang_toc_tu']:
                kk = int(round((u - C.MANH['tang_toc_tu']) * m))
                if ch.get('ket') == 'nay':
                    ztt = C.NAY[min(len(C.NAY) - 1, int(kk * len(C.NAY) / max(1, round((1 - C.MANH['tang_toc_tu']) * m))))]
                else:
                    ztt = C.MANH['tang_toc'] ** kk
            moi = self.khung_canh(i + 1, t, zoom=ztt)
            if self.canh[i].get('_tay'):
                # mở đầu: người cầm mảnh → khung tay + mảnh lao về máy, cảnh mới về thành mảnh lớn
                key = ('mo', i + 1)
                if key not in self.manh:
                    self.manh[key] = E.MangMo(self.W, self.H, seed=int(ch.get('seed', 5 + i)))
                if self._lop is not None:
                    sach, co_manh, lop, tam = self._lop
                    return self.manh[key].ve(sach, moi, u, (co_manh, lop), tam)
                return self.manh[key].ve(img, moi, u)
            if i + 1 not in self.manh:
                self.manh[i + 1] = E.MangVo(self.W, self.H, seed=int(ch.get('seed', 3 + i)), huong=i)
            if idx >= m - C.MANH['fb_truoc']:
                return self._loe_vo(i + 1, t, moi, img)
            return self.manh[i + 1].ve(img, moi, u)
        if kieu == 'luot_trang':
            L = C.LUOT
            img = E.nhoe_ngang(img, _g(L['toc_truoc'], idx) * W / 1920 * 1.6)
            a = _g(L['trang_truoc'], idx)
            return E.tron_trang(img, a, khu_mau=a)
        if kieu == 'gon_song':
            S = C.SONG
            img = E.nhoe(img, _g(S['nhoe_truoc'], idx) * W / 1920)
            return E.song(img, _g(S['bien_truoc'], idx) * W, S['buoc_song'] * W, idx * 0.9, xoay_do=-2 * idx / 3)
        if kieu == 'khoi':
            K = C.KHOI
            return E.khoi(img, _g(K['bien_truoc'], idx) * W, idx, K['nhat'] * (idx + 1) / m, seed=i + 1)
        if kieu == 'lia_nhoe':
            return E.nhoe_huong(img, _g(C.LIA['nhoe_truoc'], idx) * W, self._huong(i + 1))
        return img

    def _loe_vo(self, i, t, moi, cu=None):
        """Khung LOÉ quanh mốc cắt mảnh vỡ vào cảnh i: cảnh cũ ĐANG VỠ (chấm bi + tấm chéo, pha fb_u) — mẫu 7,667–7,70 s."""
        if cu is None:
            cu = self.khung_canh(i - 1, t)
        mv = self.manh.get(i)
        if mv is None:
            return cu
        return mv.ve(cu, moi, C.MANH['fb_u'])

    def _mat_na(self, i, t, img):
        key = (i, int(round(t * FPS)))
        if key not in self._mn:
            if len(self._mn) > 8:
                self._mn.clear()
            self._mn[key] = NG.mat_na(img)
        return self._mn[key]

    # ------------------------------------------------------------ 1 khung hoàn chỉnh
    def khung(self, t):
        W, H = self.W, self.H
        if t >= self.t_den:
            return np.zeros((H, W, 3), np.uint8)
        cs = self.canh
        j = 0
        while j + 1 < len(cs) and t >= self.s[j + 1]:
            j += 1
        c = cs[j]
        # đóng bộ đọc của cảnh đã qua (mỗi bộ = 1 ffmpeg giải mã 4K, giữ hết sẽ tràn RAM); giữ cảnh trước để loé lại
        for q in range(len(cs)):
            if (q < j - 1 or q > j + 1) and cs[q]['_nguon'].p is not None:
                cs[q]['_nguon'].dong()
        kc = (c.get('chuyen') or {}).get('kieu', 'cat') if j else 'cat'
        k = int(math.floor((t - self.s[j]) * FPS + 1e-6)) if j else 0
        in_sau = j > 0 and t < self.s[j] + C.CHUYEN[kc]['sau']
        nx = cs[j + 1] if j + 1 < len(cs) else None
        kn = (nx.get('chuyen') or {}).get('kieu', 'cat') if nx else None
        m = int(round(C.CHUYEN[kn]['truoc'] * FPS)) if nx else 0
        in_truoc = nx is not None and m > 0 and t >= self.s[j + 1] - m / FPS - 1e-6
        idx = 0
        if in_truoc:
            r = int(math.ceil((self.s[j + 1] - t) * FPS - 1e-6))
            idx = max(0, min(m - 1, m - r))
        z, dx, dy = 1.0, 0.0, 0.0
        if in_sau:
            a = self._hinh_hoc(kc, 'sau', j, k); z *= a[0]; dx += a[1]; dy += a[2]
        if in_truoc:
            a = self._hinh_hoc(kn, 'truoc', j, idx, m); z *= a[0]; dx += a[1]; dy += a[2]
        et = next((e for e in c.get('hieu_ung', []) if e['kieu'] == 'manh_tay'), None) if c.get('_tay') else None
        u_mv = (idx + 1) / m if (in_truoc and kn == 'manh_vo') else None
        them = None
        self._lop = None
        if et is not None and u_mv is not None:
            # nền cảnh cũ chỉ đẩy nhẹ vào giữa 2 tay; lớp 'tay + mảnh' lao về máy do MangMo vẽ (mẫu 4,5–4,9 s)
            zc = float((nx.get('chuyen') or {}).get('zoom_cu', C.MANH_TAY['zoom_cu']))
            if zc > 1.001:
                self.khung_canh(j, t, z, dx, dy)
                v = self._tay_px(j, t)
                P = (v['Li'] + v['Ri']) / 2 if v and 'Li' in v else np.array([self.W / 2, self.H / 2])
                zz = 1 + (zc - 1) * C.ease_io(u_mv)
                them = np.float64([[zz, 0, (1 - zz) * P[0]], [0, zz, (1 - zz) * P[1]]])
        img = self.khung_canh(j, t, z, dx, dy, them=them)
        # mảnh cảnh sau ghim vào đầu ngón (bám tay thật)
        if et is not None and t >= et['t0'] and nx is not None:
            sach = img
            img, P, lop = self._ve_manh_tay(j, t, img, et)
            if P is not None:
                self._lop = (sach, img, lop, P.mean(0))
        # mảnh nhỏ cố định (kiểu cũ, khi không dò được tay)
        for e in c.get('hieu_ung', []):
            if e['kieu'] == 'manh_cho' and e['t0'] <= t < e['t1'] and nx is not None:
                moi = self.khung_canh(j + 1, t)
                img = E.manh_cho(img, moi, (t - e['t0']) / (e['t1'] - e['t0']), e['x'], e['y'], e.get('rong', 0.18))
        if in_sau:
            img = self._diem_anh_sau(kc, img, j, t, k)
        if in_truoc:
            img = self._diem_anh_truoc(kn, img, j, t, idx, m)
        # HUD
        hd = self.plan.get('hud', {})
        if self.hud and t >= hd.get('tu', 1e9):
            img = self.hud.ve(img, t)
        # chữ
        ch = self.plan.get('chu', {})
        if self.tieu_de and t >= ch.get('go_tu', 1e9):
            n = 1 + int(math.floor((t - ch['go_tu']) / (self.P / 2) + 1e-6))
            img = self.tieu_de.ve(img, n)
        if self.dong_xe and t >= ch.get('dong_xe_tu', 1e9):
            img = self.dong_xe.ve(img)
        # glitch (cả chữ)
        if in_sau and kc == 'glitch':
            img = E.glitch(img, _g(C.GLITCH['manh'], k), k)
        elif in_truoc and kn == 'glitch':
            img = E.glitch(img, _g(C.GLITCH['truoc'], idx, 1.0), idx + 50)
        # khung điện ảnh mở đầu (+ người nổi)
        for e in c.get('hieu_ung', []):
            if e['kieu'] == 'khung_dien_anh':
                r0 = e.get('ty_le', C.KHUNG_DIEN_ANH[self.kho])
                mo = e.get('mo', C.KHUNG_MO['tu'])
                uu = min(1.0, max(0.0, (t - mo) / e.get('dai', C.KHUNG_MO['dai'])))
                av = C.KHUNG_MO['vao']
                f = uu * uu / (2 * av) if uu < av else uu - av / 2
                tl = r0 + (1 - r0) * f / (1 - av / 2)
                if tl < 0.999:
                    mk = self._mat_na(j, t, img) if e.get('nguoi', False) else None
                    img = E.khung_dien_anh(img, tl, mk)
        return img

    def dong(self):
        for c in self.canh:
            if '_nguon' in c:
                c['_nguon'].dong()


# ================================================================ tiếng
def doc_am(path, ss=0.0, dur=None):
    cmd = ['ffmpeg', '-v', 'error', '-ss', f'{ss:.3f}', '-i', path, '-vn', '-ac', '2', '-ar', str(C.SR), '-f', 'f32le', '-']
    if dur:
        cmd[5:5] = ['-t', f'{dur:.3f}']
    raw = subprocess.run(cmd, capture_output=True).stdout
    return np.frombuffer(raw, np.float32).reshape(-1, 2).copy()


def lufs(path):
    r = subprocess.run(['ffmpeg', '-hide_banner', '-i', path, '-af', 'ebur128=peak=true', '-f', 'null', '-'],
                       capture_output=True, text=True, encoding='utf-8', errors='replace')
    s = r.stderr[r.stderr.rfind('Summary'):]
    import re
    I = float(re.search(r'I:\s*(-?[\d.]+) LUFS', s).group(1))
    tp = re.search(r'Peak:\s*(-?[\d.]+|-inf) dBFS', s)
    return I, (float(tp.group(1)) if tp and tp.group(1) != '-inf' else -99.0)


def tieng(plan, work, T):
    import json
    nh = plan['nhac']
    N = int(round(T * C.SR))
    ket = nh['ket_nhac']
    x = doc_am(nh['file'], nh['bat_dau'], ket + 0.05)
    out = np.zeros((N, 2), np.float32)
    n = min(len(x), int(ket * C.SR), N)
    out[:n] = x[:n]
    # vào dần trước phách mạnh đầu (mẫu: nhạc dạo nhỏ → bùng ở 1,46 s)
    if nh['bat_dau'] > 0.3:
        fv = max(0.05, C.AM['vao_cong'] * nh['F'])
        k = int(fv * C.SR)
        out[:k] *= (np.linspace(0, 1, k, dtype=np.float32) ** 2)[:, None]
    fo = int(C.AM['fade_cuoi'] * C.SR)
    out[max(0, n - fo):n] *= np.linspace(1, 0, n - max(0, n - fo), dtype=np.float32)[:, None]
    # SFX tuỳ chọn (mẫu KHÔNG có — chỉ nhạc)
    if plan.get('sfx'):
        rms_nhac = np.sqrt(np.mean(out[:n] ** 2) + 1e-12)
        for i, c in enumerate(plan['canh'][1:], 1):
            kieu = (c.get('chuyen') or {}).get('kieu')
            f = C.SFX.get(kieu)
            if not f:
                continue
            s = doc_am(os.path.join(C.SFX_DIR, f))
            if len(s) == 0:
                continue
            s = s[:int(1.2 * C.SR)]
            pk = int(np.argmax(np.abs(s).max(1)))
            st = int(C.moc_cat(c) * C.SR) - pk
            g = rms_nhac / (np.sqrt(np.mean(s ** 2)) + 1e-9) * 10 ** (-C.SFX_DUOI_NHAC_DB / 20)
            a0, b0 = max(0, st), min(N, st + len(s))
            if b0 > a0:
                out[a0:b0] += s[a0 - st:b0 - st] * g
    tho = os.path.join(work, 'tieng_tho.wav')
    _ghi_wav(tho, out)
    r1 = subprocess.run(['ffmpeg', '-hide_banner', '-i', tho, '-af', f'loudnorm=I={C.AM["lufs"]}:TP={C.AM["tp"]}:LRA=11:print_format=json',
                         '-f', 'null', '-'], capture_output=True, text=True, encoding='utf-8', errors='replace')
    js = json.loads(r1.stderr[r1.stderr.rfind('{'):r1.stderr.rfind('}') + 1])
    af = (f'loudnorm=I={C.AM["lufs"]}:TP={C.AM["tp"]}:LRA=11:measured_I={js["input_i"]}:measured_TP={js["input_tp"]}'
          f':measured_LRA={js["input_lra"]}:measured_thresh={js["input_thresh"]}:offset={js["target_offset"]}:linear=true')
    master = os.path.join(work, 'tieng.wav')
    C.run(['ffmpeg', '-y', '-v', 'error', '-i', tho, '-af', af + f',aresample={C.SR}', '-t', f'{T:.3f}', '-c:a', 'pcm_s16le', master])
    return master


def _ghi_wav(path, x):
    p = subprocess.Popen(['ffmpeg', '-y', '-v', 'error', '-f', 'f32le', '-ar', str(C.SR), '-ac', '2', '-i', '-', '-c:a', 'pcm_f32le', path],
                         stdin=subprocess.PIPE)
    p.stdin.write(np.ascontiguousarray(x, np.float32).tobytes()); p.stdin.close(); p.wait()


def ten_moi(path):
    if not os.path.exists(path):
        return path
    b, e = os.path.splitext(path)
    k = 2
    while os.path.exists(f'{b}_ban{k}{e}'):
        k += 1
    return f'{b}_ban{k}{e}'


def dung(plan, work, ra, nhap=False):
    d = Dung(plan, work)
    if nhap:
        d.W, d.H = d.W // 2, d.H // 2
        # dựng lại chữ / HUD ở cỡ nháp
        ch = plan.get('chu', {})
        d.tieu_de = CHU.TieuDe(ch['tieu_de'], d.W, d.H, d.kho) if ch.get('tieu_de') else None
        d.dong_xe = CHU.DongXe(ch['dong_xe'], d.W, d.H, d.kho) if ch.get('dong_xe') else None
        if d.hud:
            d.hud = HUDM.Hud(d.W, d.H, d.P, plan['nhac']['F'], seed=plan.get('hud', {}).get('seed', 7),
                             vung_cam=[d.tieu_de.hop()] if d.tieu_de else [])
        for c in d.canh:
            ng = c['_nguon']
            c['_nguon'] = Nguon(ng.path, ng.info, d.W, d.H, ng.ss, ng.toc, ng.la_anh, ng.xoay)
    N = int(round(d.T * FPS))
    hinh = os.path.join(work, 'hinh_nhap.mp4' if nhap else 'hinh.mp4')
    enc = subprocess.Popen(['ffmpeg', '-y', '-v', 'error', '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-s', f'{d.W}x{d.H}', '-r', str(FPS),
                            '-i', '-', '-c:v', 'libx264', '-preset', 'veryfast' if nhap else 'medium', '-crf', '23' if nhap else '17',
                            '-pix_fmt', 'yuv420p', '-colorspace', 'bt709', '-color_primaries', 'bt709', '-color_trc', 'bt709',
                            '-movflags', '+faststart', hinh], stdin=subprocess.PIPE)
    t0 = time.time()
    try:
        for n in range(N):
            t = n / FPS
            f = d.khung(t)
            enc.stdin.write(np.ascontiguousarray(f).tobytes())
            if n % (FPS * 3) == 0:
                C.in_ra(f'  hình {t:5.1f}/{d.T:.1f} s · {time.time() - t0:5.0f} s')
    finally:
        enc.stdin.close(); enc.wait(); d.dong()
    het = [(c['id'], c['_nguon'].het) for c in d.canh if c['_nguon'].het > 3]
    am = tieng(plan, work, d.T)
    ra = ten_moi(ra)
    C.run(['ffmpeg', '-y', '-v', 'error', '-i', hinh, '-i', am, '-map', '0:v', '-map', '1:a', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '256k',
           '-t', f'{d.T:.3f}', '-movflags', '+faststart', ra])
    C.in_ra(f'Dựng xong ({time.time() - t0:.0f} s): {ra}')
    if het:
        C.in_ra('  ⚠ clip hết nguồn → đứng hình ở cảnh: ' + ', '.join(f'{i} ({n} khung)' for i, n in het))
    return ra, het


def xem(plan, work, moc, thu_muc):
    os.makedirs(thu_muc, exist_ok=True)
    d = Dung(plan, work)
    ra = []
    try:
        for t in moc:
            f = d.khung(t)
            p = os.path.join(thu_muc, f'xem_{t:06.2f}.jpg')
            cv2.imencode('.jpg', f, [cv2.IMWRITE_JPEG_QUALITY, 90])[1].tofile(p)
            ra.append((t, p, f))
    finally:
        d.dong()
    return ra
