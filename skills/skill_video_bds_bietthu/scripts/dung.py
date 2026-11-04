# -*- coding: utf-8 -*-
"""Bước 3 — dựng hình theo plan.json (đã duyệt) → hinh.mp4; xuất sfx.json + hop_chu.json cho bước tiếng/kiểm.
Có chế độ XEM: dựng vài khung tại các mốc giây ra PNG để soát bố cục trước khi dựng cả bài."""
import os, re, math, subprocess, time
import numpy as np
import cv2
from PIL import Image
import chung as C
import chu
import hieu_ung as HU

W, H, FPS = C.W, C.H, C.FPS


# ---------------------------------------------------------------- đọc video có tua
class Doc:
    def __init__(self, path, mode='cover', loop=False):
        self.path, self.mode, self.loop = path, mode, loop
        pr = C.probe(path)
        self.dur = pr['dur']
        if mode == 'cover': self.w, self.h = W, H
        else:   # 'fitw': giữ tỉ lệ, rộng 1080
            self.w = W; self.h = int(round(W * pr['h'] / pr['w'] / 2)) * 2
        self.p = None; self.cur = -1; self.start = 0.0; self.last = None

    def _mo(self, ts):
        if self.p: self.p.kill()
        self.start = max(0.0, ts)
        if self.mode == 'cover':
            sc = f'scale={self.w}:{self.h}:force_original_aspect_ratio=increase:in_color_matrix=auto,crop={self.w}:{self.h}'
        else:
            sc = f'scale={self.w}:{self.h}:in_color_matrix=auto'
        self.p = subprocess.Popen(['ffmpeg', '-v', 'error', '-ss', f'{self.start:.3f}', '-i', self.path, '-an',
                                   '-vf', f'fps={FPS},{sc}', '-pix_fmt', 'bgr24', '-f', 'rawvideo', '-'],
                                  stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, bufsize=self.w * self.h * 3 * 2)
        self.cur = -1

    def get(self, ts):
        if self.loop and self.dur > 0.5: ts = ts % (self.dur - 0.1)
        ts = min(ts, max(0.0, self.dur - 0.05))
        want = int(round((ts - self.start) * FPS))
        if self.p is None or want < self.cur - 1 or want > self.cur + 90:
            self._mo(ts); want = 0
        n = self.w * self.h * 3
        while self.cur < want:
            buf = self.p.stdout.read(n)
            if len(buf) < n: break
            self.last = np.frombuffer(buf, np.uint8).reshape(self.h, self.w, 3); self.cur += 1
        if self.last is None:
            self.last = np.zeros((self.h, self.w, 3), np.uint8)
        return self.last

    def dong(self):
        if self.p: self.p.kill(); self.p = None


def doc_anh(path):
    im = Image.open(path).convert('RGB')
    return np.ascontiguousarray(np.asarray(im)[..., ::-1])


# ---------------------------------------------------------------- dựng
class Dung:
    def __init__(self, plan, work):
        self.plan, self.work = plan, work
        self.res = plan.get('resources') or ''
        self.dur = float(plan['dur'])
        self.canh = sorted(plan['canh'], key=lambda c: c['t0'])
        self.nguon = Doc(os.path.join(work, 'nguon.mp4'))
        self.doc, self.anh, self.bg = {}, {}, {}
        mat = C.doc_json(os.path.join(work, 'mat.json')) if os.path.exists(os.path.join(work, 'mat.json')) else []
        self.mat = mat
        # gom mọi khối chữ (khối được phép vắt qua cú cắt)
        self.khoi = []
        for c in self.canh:
            for b in c.get('chu', []):
                self.khoi.append({'cum': b, 'canh': c, 'lay': None})
        self.sub = self._sub_nho() if plan.get('sub_nho', True) else []
        self.mask_nb = {}
        self.buom = {}
        self.kinh = {}
        self.hop_chu = []

    # -- nguồn
    def _path(self, f):
        return f if os.path.isabs(f) else os.path.join(self.res, f)

    def _video(self, key, path, mode):
        k = (key, mode)
        if k not in self.doc: self.doc[k] = Doc(path, mode)
        return self.doc[k]

    def _anh(self, f):
        if f not in self.anh: self.anh[f] = doc_anh(self._path(f))
        return self.anh[f]

    def neo(self, c):
        """neo phóng CỐ ĐỊNH cho cả cảnh (04/11: bám mặt từng 0,2 s làm khung giật khi người di chuyển)."""
        if c.get('tam'): return tuple(c['tam'])
        k = ('neo', c['id'])
        if k not in self.bg:
            ms = [m['mat'] for m in self.mat if m['mat'] and c['t0'] <= m['t'] < c['t1']]
            self.bg[k] = (float(np.median([(m[0] + m[2]) / 2 for m in ms])), float(np.median([(m[1] + m[3]) / 2 for m in ms])))                 if ms else (W / 2, H / 2)
        return self.bg[k]

    def truoc(self, c):
        """cảnh người nói liền trước (cùng nguồn) có zoom/neo khác → cần zoom mượt; None nếu không."""
        i = self.canh.index(c)
        if i == 0 or c['loai'] != 'noi': return None
        p = self.canh[i - 1]
        if p['loai'] != 'noi' or abs(p['t1'] - c['t0']) > 0.02: return None
        if any(h['kieu'] == 'phong_lui' and abs(h['t'] - c['t0']) < 0.05 for h in c.get('hieu_ung', [])): return None
        if abs(p.get('zoom', 1.0) - c.get('zoom', 1.0)) < 0.02: return None
        return p

    def mat_tai(self, t):
        if not self.mat: return None
        i = min(len(self.mat) - 1, max(0, int(round(t / 0.2))))
        return self.mat[i]['mat']

    # -- sub nhỏ: cụm 2–4 chữ đang nói
    def _sub_nho(self):
        p = os.path.join(self.work, 'words.json')
        if not os.path.exists(p): return []
        ws = [dict(w, cham=bool(re.search(r'[.,?!]$', w['w'])), w=re.sub(r'[.,?!]+$', '', w['w'])) for w in C.doc_json(p)]
        # sửa lỗi nghe theo CỤM từ (khoá nhiều chữ khớp các chữ liền nhau): "hòa hôn"→"hoàng hôn" không đụng "hòa nhịp"
        for a, b in sorted(self.plan.get('sua_loi', {}).items(), key=lambda kv: -len(kv[0].split())):
            toks = a.lower().split(); n = len(toks); i = 0
            while i <= len(ws) - n:
                if [x['w'].lower() for x in ws[i:i + n]] == toks:
                    ws[i] = dict(ws[i], w=b, e=ws[i + n - 1]['e'], cham=ws[i + n - 1]['cham']); del ws[i + 1:i + n]
                i += 1
        out, cur = [], []
        for i, w in enumerate(ws):
            t = w['w']
            gap = ws[i]['s'] - cur[-1]['e'] if cur else 0
            if cur and (len(cur) >= 4 or gap > 0.25 or w['e'] - cur[0]['s'] > 1.3):
                out.append(cur); cur = []
            cur.append(dict(w, w=t))
            if w['cham']: out.append(cur); cur = []
        if cur: out.append(cur)
        subs = []
        for k, c in enumerate(out):
            t1 = out[k + 1][0]['s'] if k + 1 < len(out) else c[-1]['e'] + 0.4
            subs.append({'cum': {'t1': t1 - 0.01, 'ra': 'tat', 'y': self.plan.get('sub_y', 1240),
                                 'dong': [{'text': ' '.join(w['w'] for w in c), 'vai': 'sub', 't': c[0]['s']}]}, 'lay': None})
        return subs

    # -- 1 cảnh tại t
    def nen(self, c, t):
        u = t - c['t0']
        loai = c['loai']
        if loai == 'noi':
            f = self.nguon.get(t).copy()
            z = c.get('zoom', 1.0) + c.get('day_vao', 0.0) * u
            cx, cy = self.neo(c)
            tr = self.truoc(c)
            n = C.ZOOM_MUOT['khung']
            if tr is not None and u * FPS < n:      # đổi khung giữa 2 cảnh người nói = ZOOM MƯỢT, không nhảy cứng
                e = HU.ease_io((u * FPS + 1) / n)
                z0 = tr.get('zoom', 1.0); (ax, ay) = self.neo(tr)
                z = z0 + (z - z0) * e; cx, cy = ax + (cx - ax) * e, ay + (cy - ay) * e
            if z > 1.001:
                f = HU.phong(f, z, cx, cy)
            if c.get('toi_tren'):
                f = HU.toi_tren(f, c['toi_tren'] if c['toi_tren'] is not True else C.TOI_TREN['manh'])
            return f
        if loai == 'ghep3':
            return self._ghep3(c, t)
        src_is_video = os.path.splitext(c['nguon'])[1].lower() in C.VID_EXT
        day = c.get('day', 'vao')
        sp = C.KEN_BURNS['day_vao_s'] * c.get('toc_do_day', 1.0)
        if src_is_video: sp *= 0.4      # video đã có chuyển động thật
        z = 1 + sp * u if day in ('vao', 'trai', 'phai') else (1 + sp * (c['t1'] - c['t0']) - sp * u if day == 'ra' else 1.0)
        z = max(1.0, z) + (0.03 if day in ('trai', 'phai') else 0)
        px = {'trai': 1, 'phai': -1}.get(day, 0) * C.KEN_BURNS['lia_px_s'] * u
        if loai == 'the_mo':
            if src_is_video:
                src = self._video(c['nguon'], self._path(c['nguon']), 'fitw').get(c.get('ss', 0) + u * c.get('speed', 1.0))
            else:
                src = self._anh(c['nguon'])
            key = (c['id'], 'bg')
            if not src_is_video and key in self.bg:
                bg = self.bg[key].copy()
                cfg = C.THE_MO; ih, iw = src.shape[:2]; cw = cfg['rong']; ch = int(round(cw * min(ih / iw, 0.75)))
                card = HU.ken_burns(self.bg[(c['id'], 'card')], cw, ch, z)
                HU.dan_the(bg, card, (W - cw) // 2, cfg['tam_y'] - ch // 2, cfg['bo_goc'], bong=0.55)
                return bg
            if not src_is_video:
                cfg = C.THE_MO
                b = HU.nhoe_nhanh(HU.cover(src, W, H), 8)
                self.bg[key] = (b.astype(np.float32) * cfg['toi']).astype(np.uint8)
                ih, iw = src.shape[:2]; cw = cfg['rong']; ch = int(round(cw * min(ih / iw, 0.75)))
                self.bg[(c['id'], 'card')] = HU.cover(src, cw, ch)
                return self.nen(c, t)
            return HU.canh_the_mo(src, z)
        if src_is_video:
            src = self._video(c['nguon'], self._path(c['nguon']), 'cover').get(c.get('ss', 0) + u * c.get('speed', 1.0))
        else:
            k = ('cover', c['nguon'])
            if k not in self.anh: self.anh[k] = HU.cover(self._anh(c['nguon']), W, H)
            src = self.anh[k]
        return HU.ken_burns(src, W, H, z, px, 0)

    def _ghep3(self, c, t):
        cfg = C.GHEP3
        k = ('g3', c['id'])
        if k not in self.bg: self.bg[k] = HU.nen_ghep3(c.get('nen', cfg['nen']))
        f = self.bg[k].copy()
        cw, ch, gap = cfg['rong'], cfg['cao'], cfg['khe']
        y0 = c.get('y0', cfg['y0'])
        for i, th in enumerate(c['the'][:3]):
            ti = th.get('t', c['t0'] + i * cfg['cach_the'])
            if t < ti: continue
            kf = (t - ti) * FPS
            e = HU.ease_out((kf + 1) / cfg['truot_khung'])
            x = (W - cw) // 2 - (1 - e) * (W + 60)
            y = y0 + i * (ch + gap)
            img = self._the_img(th['nguon'], cw, ch, th.get('ss', 0) + t - ti, ('g3', c['id'], i))
            for j, d in enumerate(th.get('doi', [])):          # đổi ảnh trong thẻ (hoà tan) đúng lúc đọc tên
                if t >= d['t']:
                    nimg = self._the_img(d['nguon'], cw, ch, d.get('ss', 0) + t - d['t'], ('g3', c['id'], i, j))
                    a = min(1.0, (t - d['t']) / cfg['hoa_tan'])
                    img = cv2.addWeighted(img, 1 - a, nimg, a, 0)
            HU.dan_the(f, img, x, y, cfg['bo_goc'], bong=0.45)
            if th.get('nhan'):
                lk = ('nhan', c['id'], i)
                cum = {'y': 0, 'dong': [{'text': th['nhan'], 'vai': 'nhan_the', 't': ti + 0.15}]}
                if lk not in self.bg: self.bg[lk] = chu.bo_cuc(cum)
                lay = [[d, x + 34 - d.ox, y + ch - 36 - d.gy1] for d, _, _ in self.bg[lk]]   # góc dưới-trái thẻ
                chu.ve_khoi(f, lay, {'t1': 1e9, 'troi': 0}, t)
        if c.get('buom', True):
            if c['id'] not in self.buom: self.buom[c['id']] = HU.DanBuom(c['t0'])
            self.buom[c['id']].ve(f, t)
        return f

    def _the_img(self, nguon, cw, ch, u, key):
        if os.path.splitext(nguon)[1].lower() in C.VID_EXT:
            src = self._video(key, self._path(nguon), 'fitw').get(u)   # mỗi thẻ 1 bộ đọc riêng (không tua qua lại)
            return HU.cover(src, cw, ch)
        k = ('the', nguon, cw, ch)
        if k not in self.anh: self.anh[k] = HU.cover(self._anh(nguon), cw, ch)
        return HU.ken_burns(self.anh[k], cw, ch, 1 + 0.015 * u)

    # -- hiệu ứng của cảnh
    def hieu_ung(self, f, c, t):
        rung = (0, 0)
        for h in c.get('hieu_ung', []):
            te, kieu = h['t'], h['kieu']
            k = int(round((t - te) * FPS))
            if kieu == 'phong_lui':
                n = C.HU['phong_lui']['khung']
                if 0 <= k < n:
                    z = C.HU['phong_lui']['tu'] - (C.HU['phong_lui']['tu'] - 1) * HU.ease_out((k + 1) / n)
                    cx, cy = self.neo(c)
                    f = HU.phong(f, z, cx, cy)
            elif kieu == 'loe':
                cfg = C.HU['loe']
                if 0 <= k < cfg['khung']:
                    env = (k + 1) / (cfg['dinh'] + 1) if k <= cfg['dinh'] else 1 - (k - cfg['dinh']) / (cfg['khung'] - cfg['dinh'])
                    f = HU.loe_trang(HU.phong(f, 1 + 0.035 * env), env, cfg['sang'])
                    rung = (0, cfg['rung_px'] * env * (1 if k % 2 == 0 else -0.6))
            elif kieu == 'phong_nhanh':
                if self.plan.get('nhoe'):
                    n = C.HU['nhoe_zoom']['khung']
                    if 0 <= k < n: f = HU.nhoe_zoom(f, k, n)
                else:
                    cfg = C.HU['phong_nhanh']; n = cfg['khung']
                    if 0 <= k < n:
                        u = (k + 1) / n
                        f = HU.phong(f, 1 + (cfg['toi'] - 1) * u * u)
                        if k == n - 1: f = HU.loe_trang(f, cfg['loe'])
                    elif k == n: f = HU.loe_trang(f, cfg['loe'] * 0.5)
            elif kieu == 'nhan_ban':
                n = C.HU['nhan_ban']['khung']
                if 0 <= k < n:
                    key = (c['id'], te)
                    if key not in self.mask_nb: self.mask_nb[key] = HU.mat_na_nguoi(f)
                    f = HU.nhan_ban(f, self.mask_nb[key], k)
            elif kieu == 'loe_cam_troi':     # loé cam nhẹ trôi suốt một quãng (mẫu 22,7–25,6 s)
                d = h.get('dai', 2.5)
                if 0 <= t - te < d: f = HU.loe_cam(f, (t - te) / d, h.get('manh', 0.45))
        k3 = c.get('the3d')
        if k3 and k3['t0'] <= t < k3.get('t1', c['t1']):
            if c['id'] not in self.kinh:
                anhs = [self._anh(x) if os.path.splitext(x)[1].lower() not in C.VID_EXT
                        else self._video(x, self._path(x), 'fitw').get(1.0).copy() for x in k3['nguon']]
                self.kinh[c['id']] = anhs
            anhs = self.kinh[c['id']]
            u = t - k3['t0']; cfg = C.HU['the3d']
            sh = int(u / cfg['doi_anh']) % max(1, len(anhs))
            panel = HU.tam_kinh(anhs[sh:] + anhs[:sh])
            g0, g1 = cfg['goc']
            yaw = g0 + (g1 - g0) * (0.5 - 0.5 * math.cos(u * 1.6))
            e = HU.ease_out(u / cfg['vao'])
            HU.ve_kinh3d(f, panel, yaw, k3.get('x', 300), k3.get('y', 980), 0.6 + 0.4 * e, e)
        return f, rung

    def chuyen(self, f, t):
        for x in self.plan.get('chuyen', []):
            if x['kieu'] == 'loe_cam':
                cfg = C.HU['loe_cam']
                a, b = x['t'] - cfg['truoc'], x['t'] + cfg['sau']
                if a <= t < b: f = HU.loe_cam(f, (t - a) / (b - a), x.get('manh', cfg['manh']))
        return f

    def canh_tai(self, t):
        for c in self.canh:
            if c['t0'] <= t < c['t1']: return c
        return self.canh[-1]

    def frame(self, t):
        c = self.canh_tai(t)
        f = self.nen(c, t)
        if not f.flags.writeable: f = f.copy()
        f, rung = self.hieu_ung(f, c, t)
        f = self.chuyen(f, t)
        co_chu = False
        for kb in self.khoi:
            cum = kb['cum']
            t_dau = min(d['t'] for d in cum['dong']) if cum['dong'] else 1e9
            if t < t_dau or t > cum.get('t1', 1e9) + 0.5: continue
            if kb['lay'] is None:
                for d in cum['dong']:
                    if d.get('mau') == 'tu_dong':
                        lay0 = chu.bo_cuc(cum)
                        d['mau'] = chu.mau_theo_canh(f, chu.hop(lay0))
                kb['lay'] = chu.bo_cuc(cum)
                x0, y0, x1, y1 = chu.hop(kb['lay'])
                self.hop_chu.append({'canh': kb['canh']['id'], 't0': t_dau, 't1': cum.get('t1'), 'hop': [x0, y0, x1, y1],
                                     'text': ' / '.join(d['text'] for d in cum['dong'])})
            if chu.ve_khoi(f, kb['lay'], cum, t, rung): co_chu = True
        sap_co = any(0 < min(d['t'] for d in kb['cum']['dong']) - t < 0.5 for kb in self.khoi if kb['cum']['dong'])
        if not co_chu and not sap_co and c['loai'] != 'ghep3':     # sub nhỏ không lặp chữ của khối sắp hiện
            for sb in self.sub:
                cum = sb['cum']
                if cum['dong'][0]['t'] <= t < cum['t1']:
                    if sb['lay'] is None:
                        sb['lay'] = chu.bo_cuc(cum)
                        m = self.mat_tai(t) if c['loai'] == 'noi' else None
                        if m:
                            x0, y0, x1, y1 = chu.hop(sb['lay'])
                            if y0 < m[3] + 30 and y1 > m[1] - 30:
                                for o in sb['lay']: o[2] += (m[3] + 60 - y0)
                    chu.ve_khoi(f, sb['lay'], cum, t)
                    break
        return f

    def sfx(self):
        cues = []
        for c in self.canh:
            for h in c.get('hieu_ung', []):
                k = h['kieu']
                if k == 'phong_nhanh' and self.plan.get('nhoe'): k = 'nhoe_zoom'
                if C.SFX_MAP.get(k) and h.get('sfx', True):
                    canh_dinh = k in ('phong_nhanh', 'nhoe_zoom')
                    t = h['t'] + (C.HU['phong_nhanh']['khung'] / FPS if canh_dinh else 0)
                    cues.append({'t': round(t, 3), 'file': h.get('file', C.SFX_MAP[k]), 'canh': 'dinh' if canh_dinh else 'dau', 'kieu': k})
            if c.get('the3d') and c['the3d'].get('sfx', True):
                cues.append({'t': c['the3d']['t0'], 'file': C.SFX_MAP['the3d'], 'canh': 'dau', 'kieu': 'the3d'})
            if self.truoc(c) is not None and c.get('sfx_zoom', True):   # 04/11: "zoom in/out không có SFX"
                cues.append({'t': c['t0'], 'file': C.SFX_MAP['zoom_muot'], 'canh': 'dinh_giua', 'kieu': 'zoom_muot'})
            if c['loai'] == 'ghep3' and c.get('sfx', True):
                cues.append({'t': c['t0'], 'file': C.SFX_MAP['ghep3'], 'canh': 'dau', 'kieu': 'ghep3'})
        xoay = {}
        for x in sorted(self.plan.get('chuyen', []), key=lambda q: q['t']):
            if not x.get('sfx', True): continue
            ds = C.SFX_XOAY.get(x['kieu'])
            if ds:                               # xoay vòng tiếng để các cú chuyển chương không lặp y hệt
                f = ds[xoay.get(x['kieu'], 0) % len(ds)]; xoay[x['kieu']] = xoay.get(x['kieu'], 0) + 1
            else:
                f = C.SFX_MAP[x['kieu']]
            cues.append({'t': x['t'], 'file': x.get('file', f), 'canh': 'dinh', 'kieu': x['kieu']})
        for x in self.plan.get('sfx_them', []): cues.append(dict({'canh': 'dau', 'kieu': 'them'}, **x))
        # mỗi cửa sổ SFX_CUA_SO giây tối đa 1 tiếng: giữ cái ưu tiên cao
        uu = {k: i for i, k in enumerate(C.SFX_UU_TIEN)}
        giu = []
        for q in sorted(cues, key=lambda q: uu.get(q['kieu'], 99)):
            if all(abs(q['t'] - g['t']) >= C.SFX_CUA_SO for g in giu): giu.append(q)
        giu = sorted(giu, key=lambda q: q['t'])
        for i, q in enumerate(giu):              # không lặp y hệt 1 tiếng trong SFX_KHONG_LAP_S giây
            gan = {g['file'] for g in giu[:i] if q['t'] - g['t'] < C.SFX_KHONG_LAP_S}
            if q['file'] in gan:
                ho = next((h for h in C.SFX_HO if q['file'] in h), [])
                khac = [f for f in ho if f not in gan]
                if khac: q['file'] = khac[0]
        return giu

    def dong(self):
        self.nguon.dong()
        for d in self.doc.values(): d.dong()


def xem(plan, work, moc, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    d = Dung(plan, work)
    outs = []
    for t in moc:
        # chạy đà 0,4 s trước mốc để hiệu ứng/khối chữ ở đúng trạng thái
        for tt in np.arange(max(0, t - 0.4), t, 1 / FPS): d.frame(float(tt))
        f = d.frame(t)
        p = os.path.join(out_dir, f'xem_{t:06.2f}.png'); cv2.imwrite(p, f); outs.append(p)
    d.dong()
    return outs


def dung_hinh(plan, work, out_mp4):
    d = Dung(plan, work)
    N = int(round(float(plan['dur']) * FPS))
    enc = subprocess.Popen(['ffmpeg', '-y', '-v', 'error', '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-s', f'{W}x{H}', '-r', str(FPS),
                            '-i', '-', '-vf', 'scale=out_color_matrix=bt709:out_range=tv,format=yuv420p',
                            '-c:v', 'libx264', '-preset', 'medium', '-crf', '17',
                            '-colorspace', 'bt709', '-color_primaries', 'bt709', '-color_trc', 'bt709', out_mp4],
                           stdin=subprocess.PIPE)
    t0 = time.time()
    for i in range(N):
        f = d.frame(i / FPS)
        enc.stdin.write(np.ascontiguousarray(f).tobytes())
        if i % 150 == 0: print(f'  khung {i}/{N}  ({time.time() - t0:.0f}s)', flush=True)
    enc.stdin.close(); enc.wait()
    d.dong()
    C.ghi_json(os.path.join(work, 'hop_chu.json'), d.hop_chu)
    C.ghi_json(os.path.join(work, 'sfx.json'), d.sfx())
    print(f'Hình xong: {out_mp4}  ({time.time() - t0:.0f}s)')
