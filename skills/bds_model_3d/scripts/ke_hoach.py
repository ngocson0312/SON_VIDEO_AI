# -*- coding: utf-8 -*-
"""ke_hoach.py — lập kế hoạch nháp, kiểm kế hoạch, GIẢI GIỜ (chữ từng từ, footage, SFX) cho bds_model_3d."""
import hashlib
from pathlib import Path

from chung import (CAP_TOP, CAP_TOP_PHONE, FPS, H, IMG_EXT, KIEU_CHU, KIEU_NGUYEN_CUM, LEAD, MAU_GIAO_DIEN, MODE,
                   PILL_Y, SFX, TILE_Y, W, bo_dau, ghi_json, giong_nhau, probe, run, url)

CTA_TU = ('comment', 'binhluan', 'inbox', 'nhantin', 'ib', 'lienhe', 'goingay', 'theodoi', 'follow')


# ---------------- nháp ----------------
def cum_loi(tu, max_tu=7, nghi=0.35):
    out, cur = [], []
    for i, w in enumerate(tu):
        cur.append(w)
        het = w['w'].endswith(('.', ',', '!', '?', ';', ':')) or (i + 1 < len(tu) and tu[i + 1]['s'] - w['e'] > nghi) or len(cur) >= max_tu
        if het:
            out.append(cur); cur = []
    if cur:
        out.append(cur)
    return out


def tao_nhap(tu, footage, thoi_luong, mo3d=None):
    """Kế hoạch NHÁP để Claude sửa theo nghĩa (CAN_CLAUDE_SUA=true). mo3d = {'lat','lon','ten','chac'} → nháp cảnh 3D."""
    cums = cum_loi(tu)
    chu = []
    for g in cums:
        ws = [x['w'].strip(',.!?;:') for x in g]
        dong = []
        if len(ws) >= 3:
            dong.append([{'t': ' '.join(ws[:-2]), 'k': 'dan'}])
            dong.append([{'t': ' '.join(ws[-2:]), 'k': 'vang'}])
        else:
            dong.append([{'t': ' '.join(ws), 'k': 'vang'}])
        chu.append({'tu': round(max(0, g[0]['s'] - .3), 2), 'den': round(g[-1]['e'] + .25, 2), 'vi_tri': 'tren', 'dong': dong})
    for a, b in zip(chu, chu[1:]):
        a['den'] = round(min(a['den'], b['tu'] - .02), 2)
    # cảnh
    keys = list(footage)
    cta_t = None
    for w in tu:
        if w['s'] > thoi_luong - 14 and bo_dau(w['w']) in CTA_TU:
            cta_t = w['s']; break
    het = cta_t - .4 if cta_t else thoi_luong
    canh = []
    mo = min(6.0, max(2.5, het * .2))
    if mo3d is not None:                       # cảnh 3D: thẻ nổi mở đầu → tràn màn, cùng 1 lượt bay camera
        canh.append({'loai': 'the_noi', 'tu': 0.0, 'den': round(mo, 2), 'footage': {'nguon': '3d:bay1'}})
        canh.append({'loai': 'tran_man', 'tu': round(mo, 2), 'den': round(het, 2)})
    elif 'video' in footage:
        canh.append({'loai': 'the_noi', 'tu': 0.0, 'den': round(mo, 2)})
        canh.append({'loai': 'tran_man', 'tu': round(mo, 2), 'den': round(het, 2)})
    else:
        t, i = 0.0, 0
        while t < het - .5:
            d = mo if i == 0 else 3.5
            canh.append({'loai': 'the_noi' if i == 0 else 'tran_man', 'tu': round(t, 2), 'den': round(min(het, t + d), 2),
                         'footage': {'nguon': keys[i % len(keys)], 'tu_giay': 0.0}})
            t += d; i += 1
        canh[-1]['den'] = round(het, 2)
    if cta_t:
        canh.append({'loai': 'dien_thoai', 'tu': round(het, 2), 'den': round(thoi_luong, 2),
                     'dien_thoai': {'ten': 'Khách hàng', 'trang_thai': 'Vừa mới truy cập',
                                    'tin': [{'luc': round(cta_t + .9, 2), 'ben': 'khach', 'chu': 'TỪ KHOÁ?', 'gio': '21:14'}]}})
    kh = {'CAN_CLAUDE_SUA': True, 'thoi_luong': round(thoi_luong, 2), 'canh': canh, 'chu': chu,
          'vien_kinh': [], 'o_kinh': [], 'nhac': {'file': None, 'muc': -23, 'dang': 16}, 'sfx': {'tat': False, 'bo': [], 'them': []}}
    if mo3d is not None:
        kh['mo_hinh_3d'] = {
            '_GHI_CHU': 'NHÁP — Claude mở ảnh phối cảnh, sửa số tháp / tầng / kích thước / màu theo ảnh (references/mo_hinh_3d.md), rồi run.py xem-3d',
            'vi_tri': {'lat': mo3d.get('lat'), 'lon': mo3d.get('lon'), 'ten': mo3d.get('ten', ''), 'chac': bool(mo3d.get('chac'))},
            'xoay': 0,
            'thap': [{'x': -16, 'z': -18, 'rong': 26, 'sau': 30, 'tang': 30, 'chan': 6, 'vuon': [12, 19], 'mai': 'song'},
                     {'x': 14, 'z': 4, 'rong': 40, 'sau': 24, 'tang': 30, 'chan': 6, 'vuon': [12, 19], 'mai': 'song'}],
            'de': [{'x': -14, 'z': 14, 'rong': 46, 'sau': 34, 'tang': 3, 'ho_boi': {'x': -2, 'z': -2, 'rong': 28, 'sau': 16}}],
            'khoi': [], 'khu': {'rong': 110, 'sau': 95}, 'cay_quanh': 70,
        }
        n = max(2, int(het // 3.2) + 1)
        cam = []
        for i in range(n):
            u = i / (n - 1)
            cam.append({'luc': round(u * het, 2), 'nhin': [0, round(20 + 40 * min(1, u * 1.6)), 0], 'goc': round(10 + 60 * u),
                        'nghieng': round(70 - 54 * min(1, u * 1.5)), 'xa': round(1050 - 660 * min(1, u * 1.5)), 'fov': 55})
        kh['canh_3d'] = {'bay1': {'cam': cam, 'chu': [], 'chu_thich': [],
                                  'vong': [{'tu': .3, 'den': round(min(het, mo), 2), 'r': 150}],
                                  'logo': {'tu': .6, 'den': round(min(het, mo) - .3, 2), 'chu': mo3d.get('ten', '') or 'TÊN DỰ ÁN', 'phu': ''},
                                  'dia_danh': [], 'tia': []}}
        kh['doan'] = ['mô hình 3D dựng theo ảnh phối cảnh: số tháp / tầng / kích thước là ƯỚC LƯỢNG']
    return kh


# ---------------- kiểm + giải ----------------
class Bao:
    def __init__(self):
        self.loi, self.canh_bao = [], []

    def L(self, m): self.loi.append('⛔ ' + m)
    def C(self, m): self.canh_bao.append('⚠ ' + m)


def _f(x, d=None):
    try:
        return float(x)
    except Exception:
        return d


def giai(kh, tu, footage, work, bao, trich=True):
    """Trả về dict KH cho bds3d.js + danh sách sự kiện SFX. trich=True thì cắt khung footage / ảnh tĩnh."""
    work = Path(work)
    D = _f(kh.get('thoi_luong'))
    if kh.get('CAN_CLAUDE_SUA'):
        bao.L('ke_hoach.json còn CAN_CLAUDE_SUA=true — Claude phải sửa theo nghĩa lời rồi đặt false.')
    sc = kh.get('canh') or []
    if not sc:
        bao.L('chưa có cảnh nào'); return None, []
    # ---- cảnh ----
    for i, s in enumerate(sc):
        s.setdefault('id', f'c{i + 1}')
        if s.get('loai') not in MODE:
            bao.L(f"cảnh {s['id']}: loai '{s.get('loai')}' không hợp lệ (the_noi|tran_man|nen_nhoe|nen_toi|giao_dien|dien_thoai)")
        s['tu'], s['den'] = _f(s.get('tu'), 0), _f(s.get('den'), 0)
    if abs(sc[0]['tu']) > .01:
        bao.L(f"cảnh đầu phải bắt đầu ở 0 (đang {sc[0]['tu']})")
    for a, b in zip(sc, sc[1:]):
        if abs(a['den'] - b['tu']) > .02:
            bao.L(f"cảnh {a['id']} hết {a['den']} nhưng {b['id']} bắt đầu {b['tu']} — các cảnh phải nối liền")
    if abs(sc[-1]['den'] - D) > .3:
        bao.C(f"cảnh cuối hết {sc[-1]['den']} ≠ thời lượng {D} — tự kéo về {D}")
    sc[-1]['den'] = D
    for s in sc:
        d = s['den'] - s['tu']
        if d < .8:
            bao.L(f"cảnh {s['id']} chỉ {d:.2f} s (< 0,8 s)")
        elif d < 1.5:
            bao.C(f"cảnh {s['id']} ngắn {d:.2f} s")
        if s.get('loai') == 'giao_dien':
            if s.get('mau') not in MAU_GIAO_DIEN:
                bao.L(f"cảnh {s['id']}: giao_dien cần mau = ban_do | chat_ai | anh")
            elif not isinstance(s.get(s['mau']), dict):
                bao.L(f"cảnh {s['id']}: thiếu khối \"{s['mau']}\": {{…}}")
    # ---- footage (shot) ----
    shots, prev, last_ng = [], None, None
    for s in sc:
        mode = MODE.get(s.get('loai'), 'none'); s['mode'] = mode
        if mode == 'none':
            s['shot'] = None; prev = None; continue
        f = s.get('footage')
        if prev is not None and not f:
            prev['t1'] = s['den']; s['shot'] = prev['id']; continue
        f = f or {}
        ng = f.get('nguon') or last_ng or ('video' if 'video' in footage else (next(iter(footage), None)))
        if isinstance(ng, str) and ng.startswith('3d:'):          # cảnh 3D dựng bằng mô hình (mo_hinh_3d.py)
            sh = {'id': f's{len(shots)}', 'layer': len(shots) % 2, 'nguon': ng, 'is3d': ng[3:], 't0': s['tu'], 't1': s['den']}
            shots.append(sh); s['shot'] = sh['id']; prev = sh; last_ng = ng
            continue
        if ng not in footage:
            bao.L(f"cảnh {s['id']}: footage nguon '{ng}' không có (có: {', '.join(footage) or 'không'})"); s['shot'] = None; continue
        tg = _f(f.get('tu_giay'))
        if tg is None:
            tg = s['tu'] if ng == 'video' else 0.0
        sh = {'id': f's{len(shots)}', 'layer': len(shots) % 2, 'nguon': ng, 'src': footage[ng], 'src_t0': tg, 't0': s['tu'], 't1': s['den'],
              'toc_do': _f(f.get('toc_do'), 1.0), 'tam': f.get('tam') or [.5, .5]}
        shots.append(sh); s['shot'] = sh['id']; prev = sh; last_ng = ng
    dung3d = [(sh['is3d'], sh['t0'], sh['t1']) for sh in shots if sh.get('is3d')]
    if dung3d:
        import mo_hinh_3d as M3D
        if M3D.kiem_mo_hinh(kh.get('mo_hinh_3d'), bao, work=work):
            for cid, a, b in dung3d:
                M3D.kiem_canh(kh, cid, a, b, bao)
            M3D.so_trong_loi(kh, tu, bao)
        if bao.loi:
            trich = False                  # kế hoạch 3D còn lỗi: không dựng khung
    for sh in shots:
        if sh.get('is3d'):
            continue
        info = probe(sh['src'])
        sh['anh'] = Path(sh['src']).suffix.lower() in IMG_EXT
        if not sh['anh']:
            het = sh['src_t0'] + (sh['t1'] - sh['t0']) * sh['toc_do']
            if het > info['duration'] + .05:
                bao.C(f"footage {sh['nguon']} chỉ dài {info['duration']:.1f} s nhưng shot {sh['id']} cần tới {het:.1f} s — khung cuối sẽ đứng")
    # ---- dữ liệu giao diện / điện thoại ----
    anh_dir = work / 'anh'; anh_dir.mkdir(exist_ok=True)
    for s in sc:
        if s.get('loai') == 'giao_dien' and s.get('mau') in MAU_GIAO_DIEN:
            s['data'] = dict(s.get(s['mau']) or {})
            _kiem_gio_trong(s, s['data'], bao)
            if s['mau'] == 'chat_ai':
                for j, a in enumerate(s['data'].get('viec') or []):
                    if a.get('lam') == 'video':
                        a['anh_url'] = _anh_tinh(a.get('anh') or {}, footage, anh_dir / f"{s['id']}_v{j}.jpg", 760, 1352, bao, trich)
            if s['mau'] == 'anh':
                d = s['data']
                if d.get('clip'):
                    c = d['clip']; ng = c.get('nguon')
                    if ng not in footage:
                        bao.L(f"cảnh {s['id']}: anh.clip nguon '{ng}' không có")
                    else:
                        d['khung'] = _trich_khung(footage[ng], _f(c.get('tu_giay'), 0), s['tu'], s['den'], _f(c.get('toc_do'), 1), [.5, .5],
                                                  work / 'khung' / f"{s['id']}_clip", 880, 1400, trich)
                else:
                    d['anh_url'] = _anh_tinh(d, footage, anh_dir / f"{s['id']}.jpg", 880, 1400, bao, trich)
        elif s.get('loai') == 'dien_thoai':
            s['data'] = dict(s.get('dien_thoai') or {})
            _kiem_gio_trong(s, s['data'], bao)
    # ---- trích khung footage ----
    js_shots = []
    for sh in shots:
        o = {'id': sh['id'], 'layer': sh['layer'], 't0': sh['t0'], 't1': sh['t1']}
        if sh.get('is3d'):
            if sh['is3d'] in (kh.get('canh_3d') or {}) and isinstance(kh.get('mo_hinh_3d'), dict):
                o.update(M3D.khung(kh, sh['is3d'], sh['t0'], sh['t1'], tu, work, bao, trich))
            else:
                o.update({'dir': '', 'ext0': sh['t0'], 'n': 1})
        elif sh['anh']:
            p = work / 'anh' / f"{sh['id']}.jpg"
            if trich:
                run(['ffmpeg', '-v', 'error', '-y', '-i', sh['src'], '-vf', _vf_cover(W, H, sh['tam']), '-frames:v', '1', '-q:v', '2', p])
            o.update(image=url(p), kb=[1.0, 1.08])
        else:
            o.update(_trich_khung(sh['src'], sh['src_t0'], sh['t0'], sh['t1'], sh['toc_do'], sh['tam'], work / 'khung' / sh['id'], W, H, trich))
        js_shots.append(o)
    # ---- chữ ----
    caps = _giai_chu(kh.get('chu') or [], tu, sc, D, bao)
    # ---- viên kính / ô kính ----
    pills = []
    for p in kh.get('vien_kinh') or []:
        a, b, g = _f(p.get('tu')), _f(p.get('den')), _f(p.get('gach'))
        if a is None or b is None or b <= a:
            bao.L(f"vien_kinh '{p.get('chu')}': tu/den sai"); continue
        if g is not None and not (a < g < b):
            bao.L(f"vien_kinh '{p.get('chu')}': gach {g} phải nằm trong ({a}, {b})")
        pills.append({'tu': a, 'den': b, 'gach': g, 'dan': p.get('dan', ''), 'icon': p.get('icon', 'check'), 'chu': p.get('chu', ''), 'y': _f(p.get('y'), PILL_Y)})
    tiles = []
    for T in kh.get('o_kinh') or []:
        a, b = _f(T.get('tu')), _f(T.get('den'))
        muc = T.get('muc') or []
        if a is None or b is None or b <= a or not muc:
            bao.L('o_kinh: thiếu tu/den/muc'); continue
        if len(muc) > 5:
            bao.L(f'o_kinh: tối đa 5 ô (đang {len(muc)})')
        mm = [{'icon': m.get('icon', 'check'), 'nhan': m.get('nhan', ''), 'luc': _f(m.get('luc'), a + .1 * i), **({'so': m['so']} if 'so' in m else {})} for i, m in enumerate(muc)]
        tiles.append({'tu': a, 'den': b, 'y': _f(T.get('y'), TILE_Y), 'so': T.get('so', True), 'muc': mm})
    js_sc = [{k: s.get(k) for k in ('id', 'loai', 'tu', 'den', 'mode', 'shot', 'vao', 'mau', 'data')} for s in sc]
    KH = {'fps': FPS, 'dur': D, 'shots': js_shots, 'scenes': js_sc, 'caps': caps, 'pills': pills, 'tiles': tiles,
          'canh3d': [{'id': c, 't0': a, 't1': b} for c, a, b in dung3d]}
    return KH, _sfx(kh, sc, pills, tiles, D, dung3d)


def _kiem_gio_trong(s, d, bao):
    """mọi 'luc' trong khối giao diện phải nằm trong cảnh."""
    def duyet(x, path):
        if isinstance(x, dict):
            for k, v in x.items():
                if k in ('luc', 'den') and isinstance(v, (int, float)) and not (s['tu'] - .05 <= v <= s['den'] + .3):
                    bao.C(f"cảnh {s['id']}: {path}.{k}={v} nằm ngoài cảnh [{s['tu']}, {s['den']}]")
                duyet(v, f'{path}.{k}')
        elif isinstance(x, list):
            for i, v in enumerate(x):
                duyet(v, f'{path}[{i}]')
    duyet(d, s.get('mau') or s.get('loai'))


def _vf_cover(w, h, tam=(.5, .5)):
    tx, ty = (tam or [.5, .5])[:2]
    return f"scale={w}:{h}:force_original_aspect_ratio=increase,crop={w}:{h}:(iw-{w})*{tx}:(ih-{h})*{ty},setsar=1"


def _trich_khung(src, src_t0, t0, t1, toc, tam, out, w, h, trich):
    """Cắt khung 30 fps cho đoạn footage [t0-0.1, t1+0.45] (giây ra) → thư mục ảnh. Có cache theo thông số."""
    out = Path(out)
    ext0 = t0 - .1
    a = src_t0 - .1 * toc
    if a < 0:
        ext0 += -a / toc; a = 0.0
    dur = (t1 + .45 - ext0) * toc
    key = hashlib.md5(f'{src}|{a:.3f}|{dur:.3f}|{toc}|{tam}|{w}x{h}'.encode()).hexdigest()[:12]
    n = 0
    if trich:
        if not (out / f'xong_{key}').exists():
            if out.exists():
                for f in out.glob('*'):
                    f.unlink()
            out.mkdir(parents=True, exist_ok=True)
            vf = (f'setpts=PTS/{toc},' if abs(toc - 1) > 1e-3 else '') + f'fps={FPS},' + _vf_cover(w, h, tam)
            run(['ffmpeg', '-v', 'error', '-y', '-ss', f'{a:.3f}', '-i', src, '-t', f'{dur:.3f}', '-vf', vf, '-q:v', '3', out / '%05d.jpg'])
            (out / f'xong_{key}').write_text('ok')
        n = len(list(out.glob('*.jpg')))
    return {'dir': url(out, True), 'ext0': round(ext0, 4), 'n': max(1, n)}


def _anh_tinh(d, footage, out, w, h, bao, trich):
    """ảnh tĩnh: {'file': path} hoặc {'nguon': key, 'tu_giay': s}."""
    src, ss = None, None
    if d.get('file'):
        src = d['file']
        if not Path(src).exists():
            bao.L(f'không thấy ảnh {src}'); return ''
    elif d.get('nguon') in footage:
        src, ss = footage[d['nguon']], _f(d.get('tu_giay'), 0)
    else:
        bao.L(f"thiếu ảnh (file hoặc nguon+tu_giay): {d}"); return ''
    if trich:
        cmd = ['ffmpeg', '-v', 'error', '-y'] + (['-ss', f'{ss:.3f}'] if ss is not None and Path(src).suffix.lower() not in IMG_EXT else []) + \
              ['-i', src, '-frames:v', '1', '-vf', _vf_cover(w, h, d.get('tam')), '-q:v', '2', out]
        run(cmd)
    return url(out)


def _giai_chu(chu, tu, sc, D, bao):
    Wd = tu
    phone = [(s['tu'], s['den']) for s in sc if s.get('loai') == 'dien_thoai']
    caps = []
    chu = sorted(chu, key=lambda g: _f(g.get('tu'), 0))
    for gi, g in enumerate(chu):
        a, b = _f(g.get('tu')), _f(g.get('den'))
        if a is None or b is None or b <= a:
            bao.L(f'chu #{gi + 1}: tu/den sai'); continue
        vt = g.get('vi_tri', 'tren')
        if isinstance(vt, (int, float)):
            top = float(vt)
        else:
            top = CAP_TOP.get(vt, CAP_TOP['tren'])
            if vt == 'tren' and any(p0 - .1 < (a + b) / 2 < p1 for p0, p1 in phone):
                top = CAP_TOP_PHONE
        ptr = 0
        while ptr < len(Wd) and Wd[ptr]['s'] < a - .6:
            ptr += 1
        dong_out, last = [], None
        for dong in g.get('dong') or []:
            row = []
            for ch in dong:
                k = ch.get('k', 'dan')
                if k not in KIEU_CHU:
                    bao.L(f"chu '{ch.get('t')}': k '{k}' không hợp lệ ({'|'.join(KIEU_CHU)})"); k = 'dan'
                text = str(ch.get('t', '')).strip()
                if not text:
                    continue
                whole = (k in KIEU_NGUYEN_CUM and ch.get('tung_tu') is not True) or ch.get('tung_tu') is False
                toks = text.split()
                times = []
                luc = _f(ch.get('luc'))
                if luc is not None:
                    while ptr < len(Wd) and Wd[ptr]['s'] < luc + LEAD - .08:
                        ptr += 1
                for j, tok in enumerate(toks):
                    t = None
                    if j == 0 and luc is not None:
                        t = luc
                    else:
                        truoc = times[j - 1] if j else last
                        for q in range(ptr, min(len(Wd), ptr + 7)):
                            if Wd[q]['s'] > b + .25 or (truoc is not None and Wd[q]['s'] - LEAD > truoc + 1.2):
                                break
                            if giong_nhau(tok, Wd[q]['w']) >= .62:
                                t = Wd[q]['s'] - LEAD; ptr = q + 1; break
                    times.append(t)
                for j in range(len(times)):
                    if times[j] is None:
                        prev = times[j - 1] if j else last
                        times[j] = (prev + .12) if prev is not None else a
                for j in range(1, len(times)):
                    times[j] = max(times[j], times[j - 1])
                times = [max(x, a) for x in times]       # cụm chưa hiện thì từ chưa hiện
                last = times[-1]
                row.append({'k': k, 'whole': whole, 'text': text, 't': round(times[0], 3),
                            'words': [{'w': w_, 't': round(t_, 3)} for w_, t_ in zip(toks, times)]})
            if row:
                dong_out.append(row)
        if not dong_out:
            continue
        t_min = min(c['t'] for r in dong_out for c in r)
        t_max = max(w['t'] for r in dong_out for c in r for w in c['words'])
        if b < t_max + .35:
            bao.C(f"chu '{_txt(dong_out)}': den {b} quá sát chữ cuối ({t_max + LEAD:.2f}) — chữ chưa kịp đọc")
        caps.append({'tu': round(t_min, 3), 'den': b, 'top': top, 'vi_tri': vt, 'dong': dong_out})
    for x, y in zip(caps, caps[1:]):
        if x['den'] > y['tu'] + .03 and x['vi_tri'] == y['vi_tri']:
            bao.L(f"2 cụm chữ chồng nhau: '{_txt(x['dong'])}' (hết {x['den']}) và '{_txt(y['dong'])}' (hiện {y['tu']:.2f})")
    return caps


def _txt(dong):
    return ' / '.join(' '.join(c['text'] for c in r) for r in dong)


def _sfx(kh, sc, pills, tiles, D, dung3d=()):
    cfg = kh.get('sfx') or {}
    if cfg.get('tat'):
        return []
    ev = []

    def add(ten, luc, dai=None):
        f, db, lech = SFX[ten]
        if luc is None:
            return
        e = {'luc': round(luc + lech, 3), 'file': f, 'db': db, 'ten': ten}
        if dai:
            e['dai'] = round(dai, 3)
        ev.append(e)
    for i, s in enumerate(sc):
        p = sc[i - 1] if i else None
        if s['mode'] != 'none':
            same = p is not None and p.get('mode') != 'none' and p.get('shot') == s.get('shot')
            if same and p['mode'] != s['mode']:
                add('phong_the' if (p['mode'], s['mode']) in (('card', 'full'), ('card', 'blur')) else 'nhoe_nen', s['tu'])
            elif not same:
                if s['mode'] == 'card':
                    add('the_vao', s['tu'])
                elif s['mode'] == 'full' and p is not None and p.get('loai') == 'giao_dien' and s.get('vao') != 'hoa_tan':
                    add('ket_qua_vao', s['tu'])
                elif p is not None:
                    add('nhoe_nen', s['tu'])
        if s.get('loai') == 'giao_dien':
            add('giao_dien_vao', s['tu'])
            d = s.get('data') or {}
            if s.get('mau') == 'ban_do':
                ot = d.get('o_tim') or {}
                if ot.get('luc') is not None:
                    add('go_phim', ot['luc'], (ot.get('den') or ot['luc'] + len(ot.get('chu', '')) / 16) - ot['luc'])
                for k, ten in (('ghim', 'ghim'), ('bang', 'bang_truot'), ('cham', 'cham'), ('thong_bao', 'thong_bao')):
                    if (d.get(k) or {}).get('luc') is not None:
                        add(ten, d[k]['luc'])
            elif s.get('mau') == 'chat_ai':
                for a in d.get('viec') or []:
                    l = a.get('lam')
                    if l in ('dan', 'tep'):
                        add('chip', a.get('luc'))
                    elif l == 'go':
                        add('go_phim', a.get('luc'), (a.get('den') or a['luc'] + len(a.get('chu', '')) / 16) - a['luc'])
                    elif l == 'gui':
                        add('gui', a.get('luc'))
                    elif l == 'xoa':
                        add('xoa', a.get('luc'))
                    elif l == 'video':
                        add('video_tha', a.get('luc'))
                    elif l == 'video_vao_o':
                        add('video_vao_o', a.get('luc'))
            elif s.get('mau') == 'anh':
                for c in d.get('cham') or []:
                    add('cham', c.get('luc'))
        if s.get('loai') == 'dien_thoai':
            add('dien_thoai_vao', s['tu'])
            for m in (s.get('data') or {}).get('tin') or []:
                if m.get('lam') == 'dang_go':
                    continue
                add('tai_lieu' if m.get('loai') == 'tai_lieu' else 'tin_nhan', m.get('luc'))
    for cid, a, b in dung3d:                     # sự kiện trong cảnh 3D (chỉ phần nằm trong đoạn được dùng)
        c3 = (kh.get('canh_3d') or {}).get(cid) or {}
        trong = lambda x: x is not None and a - .05 <= x < b
        for ten, ds in (('vong_3d', c3.get('vong')), ('chu_thich_3d', c3.get('chu_thich')), ('dia_danh_3d', c3.get('dia_danh'))):
            for o in ds or []:
                if trong(_f(o.get('tu'))):
                    add(ten, _f(o.get('tu')))
        lg = c3.get('logo') or {}
        if lg and trong(_f(lg.get('tu'), 0)):
            add('logo_3d', _f(lg.get('tu'), 0))
    for p in pills:
        add('vien_kinh', p['tu'])
        if p['gach'] is not None:
            add('gach', p['gach'])
    for T in tiles:
        for m in T['muc']:
            add('o_kinh', m['luc'])
    ev.sort(key=lambda e: e['luc'])
    out = []
    for e in ev:
        if out and 'dai' not in e and 'dai' not in out[-1] and e['luc'] - out[-1]['luc'] < .07:
            if e['db'] > out[-1]['db']:
                out[-1] = e
            continue
        out.append(e)
    bo = [_f(x) for x in cfg.get('bo') or []]
    out = [e for e in out if not any(abs(e['luc'] - x) < .12 for x in bo if x is not None)]
    for e in cfg.get('them') or []:
        out.append({'luc': _f(e.get('luc'), 0), 'file': e.get('file', 'pop.mp3'), 'db': _f(e.get('db'), -9), 'ten': 'them'})
    out = [e for e in out if 0 <= e['luc'] < D]
    out.sort(key=lambda e: e['luc'])
    return out
