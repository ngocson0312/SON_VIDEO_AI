# -*- coding: utf-8 -*-
"""ke_hoach.py — đọc ke_hoach.json, kiểm (⛔ / ⚠ / 🔧), giải giờ → KH cho trang dựng + danh sách chuẩn bị footage + SFX."""
import math
import re
import unicodedata
from pathlib import Path

from chung import (BO_CUC, CANH_MIN, CHUYEN, CHUYEN_DONG, CTA_MIN, DUOI, FPS, GHEP_KHE, H, HIEN_ANH, HIEN_MIN, ICON, KHONG_CACH, LOAI_DH, NGON_NGU,
                   NHO, SFX, SFX_TREN, SUB_MAX_KY_TU, SUB_MAX_TU, SUB_NGAT, THE_DOC_CAO, THE_DOC_X, W, ASSETS, doc_json, loi)

BAT_BUOC = {'mo_dau': ('chinh',), 'hook_tu': ('chu',), 'chuong': ('ten',), 'dia_danh': ('ten',), 'tu_khoa': ('muc',), 'tieu_de': ('khoa',), 'chip': ('muc',),
            'so_lon': ('so',), 'liet_ke': ('muc',), 'trich': ('noi',), 'ban_do': ('diem',)}
VI_TRI_DH = ('giua', 'trai', 'phai')


# ---------------- sửa lỗi nhận lời ----------------
def _chuan(w):
    return re.sub(r'[^\w]+', '', unicodedata.normalize('NFC', w).lower())


def sua_tu(tu, bang):
    """bang {"sai": "đúng"} — khớp chuỗi từ liên tiếp (bỏ dấu câu, không phân biệt hoa thường), giữ dấu câu cuối.
    → (từ mới, [cụm không tìm thấy])."""
    tu = [dict(w) for w in tu]
    khong_thay = []
    for sai, dung in (bang or {}).items():
        a = [_chuan(x) for x in sai.split()]
        b = dung.split()
        n, thay, i = len(a), 0, 0
        while i + n <= len(tu):
            if [_chuan(tu[i + k]['w']) for k in range(n)] != a:
                i += 1
                continue
            duoi = re.search(r'[^\w]+$', tu[i + n - 1]['w'])
            duoi = duoi.group(0) if duoi else ''
            dau = re.match(r'^[^\w]+', tu[i]['w'])
            dau = dau.group(0) if dau else ''
            s0, e0 = tu[i]['s'], tu[i + n - 1]['e']
            if len(b) == n:
                for k in range(n):
                    tu[i + k]['w'] = b[k]
                m = n
            else:
                tu[i:i + n] = [{'w': x, 's': round(s0 + (e0 - s0) * k / len(b), 2), 'e': round(s0 + (e0 - s0) * (k + 1) / len(b), 2)}
                               for k, x in enumerate(b)]
                m = len(b)
            tu[i + m - 1]['w'] += duoi
            tu[i]['w'] = dau + tu[i]['w']
            thay += 1
            i += m
        if not thay:
            khong_thay.append(sai)
    return tu, khong_thay


# ---------------- gom sub (quy hoạch động, ưu tiên 1 dòng cho khung ngang) ----------------
_TU_GHEP = {}
TU_DAN = {'vi': {'một', 'những', 'các', 'của', 'và', 'với', 'là', 'có', 'được', 'cho', 'để', 'mà', 'thì', 'hay', 'hoặc', 'rất', 'trong',
                 'ở', 'tại', 'từ', 'đến', 'vào', 'ra', 'lên', 'xuống', 'khi', 'nơi', 'này', 'bạn', 'hãy', 'đừng', 'sẽ', 'đã', 'đang',
                 'cũng', 'vẫn', 'còn', 'nhiều', 'mọi', 'mỗi', 'từng', 'bao', 'nét', 'con', 'ngôi', 'chiếc', 'món', 'cái', 'người', 'nhất'},
          'en': {'the', 'a', 'an', 'of', 'and', 'to', 'in', 'on', 'with', 'for', 'at', 'by', 'from', 'my', 'your', 'our', 'their', 'this',
                 'that', 'is', 'are', 'was', 'be', 'will', 'can', 'very', 'most', 'more'}}
TU_TRUOC = {'vi': {'và', 'với', 'nhưng', 'mà', 'khi', 'nơi', 'để', 'thì', 'hay', 'hoặc', 'nếu', 'vì', 'bởi', 'rồi'},
            'en': {'and', 'but', 'or', 'with', 'of', 'for', 'to', 'in', 'at', 'on', 'from', 'where', 'when', 'which', 'who', 'that',
                   'as', 'like', 'into', 'through', 'while', 'because', 'so', 'if', 'than', 'around', 'along', 'near', 'by'}}


def tu_ghep(nn):
    if nn not in _TU_GHEP:
        f = ASSETS / f'tu_ghep_{nn}.txt'
        ds = set()
        if f.exists():
            for d in f.read_text(encoding='utf-8').splitlines():
                d = d.strip()
                if d and not d.startswith('#'):
                    ds.add(tuple(_chuan(x) for x in d.split()))
        _TU_GHEP[nn] = ds
    return _TU_GHEP[nn]


def gom_sub(tu, nn, giu_lien=()):
    """gom từ thành cụm sub (1 dòng, dài thì 2 dòng): ngắt ở dấu câu / chỗ ngừng, KHÔNG tách từ ghép / tên riêng."""
    kc = nn in KHONG_CACH
    max_ky = SUB_MAX_KY_TU if not kc else 22
    max_tu = SUB_MAX_TU if not kc else 40
    n = len(tu)
    if not n:
        return []
    dd = lambda ws: sum(len(w['w']) for w in ws) + (0 if kc else max(0, len(ws) - 1))
    ghep = set(tu_ghep(nn)) if not kc else set()
    for g in giu_lien or ():
        k = tuple(_chuan(x) for x in str(g).split() if _chuan(x))
        if 2 <= len(k) <= 5:
            ghep.add(k)
    c = [_chuan(w['w']) for w in tu]
    dinh = [False] * n
    dmax = max([len(g) for g in ghep] + [2])
    for i in range(n):
        for L in range(2, dmax + 1):
            if i + L <= n and tuple(c[i:i + L]) in ghep:
                for k in range(i, i + L - 1):
                    dinh[k] = True
    hoa = lambda x: (re.sub(r'^[^\w]+', '', x)[:1] or 'a').isupper()
    for i in range(n - 1):
        if hoa(tu[i]['w']) and hoa(tu[i + 1]['w']) and not re.search(r'[.!?,;:…]$', tu[i]['w']):
            dinh[i] = True
    dan, truoc = TU_DAN.get(nn, set()), TU_TRUOC.get(nn, set())
    P_CAU = r'[,;:、，.!?…。！？]["”’»)]?$'

    def gia_ngat(i):
        if i >= n - 1:
            return 0.0
        w = tu[i]['w']
        g = tu[i + 1]['s'] - tu[i]['e']
        cc = 10.0
        if re.search(r'[.!?…。！？]["”’»)]?$', w):
            cc -= 11
        elif re.search(r'[,;:、，–—-]["”’»)]?$', w):
            cc -= 7
        cc -= min(7.0, max(0.0, g) * 16)
        if dinh[i]:
            cc += 40
        elif _chuan(w) in dan and not re.search(r'[^\w]$', w):
            cc += 12
        if not re.search(r'[^\w]$', w):
            if _chuan(tu[i + 1]['w']) in truoc:
                cc -= 4
            if re.search(P_CAU, tu[i + 1]['w']):
                cc += 7
            if i >= 1 and re.search(P_CAU, tu[i - 1]['w']):
                cc += 7
        return cc

    def chia_dong(a, b):
        ws = tu[a:b]
        L = dd(ws)
        if L <= max_ky or len(ws) == 1:
            return (0.0 if L <= max_ky * 1.05 else 30.0), [ws]
        best = None
        for j in range(1, len(ws)):
            l1, l2 = dd(ws[:j]), dd(ws[j:])
            if l1 > max_ky or l2 > max_ky:
                continue
            gc = 6 + gia_ngat(a + j - 1) * .85 + abs(l1 - l2) * .3          # +6: khung ngang ưu tiên 1 dòng
            if min(j, len(ws) - j) == 1 and len(ws) >= 4:
                gc += 5
            if best is None or gc < best[0]:
                best = (gc, [ws[:j], ws[j:]])
        return best

    INF = float('inf')
    tot, vet = [INF] * (n + 1), [None] * (n + 1)
    tot[0] = 0.0
    for b in range(1, n + 1):
        for a in range(max(0, b - max_tu * 2), b):
            if tot[a] == INF:
                continue
            cd = chia_dong(a, b)
            if cd is None:
                continue
            ws = tu[a:b]
            dai = ws[-1]['e'] - ws[0]['s']
            giua = 0.0
            for k in range(a, b - 1):
                if tu[k + 1]['s'] - tu[k]['e'] >= SUB_NGAT * 1.6:
                    giua += 25
                if re.search(r'[.!?…。！？]["”’»)]?$', tu[k]['w']):
                    giua += 18
            ngan = 0.0
            if dd(ws) < max_ky * .35 and b < n:
                ngan += 7
            if dai < .7 and b < n:
                ngan += 6
            if dai > 3.8:
                ngan += (dai - 3.8) * 6
            cst = tot[a] + cd[0] + gia_ngat(b - 1) + giua + ngan + 4
            if cst < tot[b]:
                tot[b], vet[b] = cst, (a, cd[1])
    cum, b = [], n
    while b > 0:
        a, dong = vet[b]
        cum.append(dong)
        b = a
    cum.reverse()
    out = []
    for k, dong in enumerate(cum):
        c0, c1 = dong[0][0], dong[-1][-1]
        nxt = cum[k + 1][0][0]['s'] - .08 if k + 1 < len(cum) else None
        den = c1['e'] + .35
        if nxt is not None and nxt - c1['e'] < .6:
            den = nxt
        out.append({'tu': round(max(0, c0['s'] - .08), 3), 'den': round(den, 3),
                    'dong': [[{'w': w['w'], 's': w['s'], 'e': w['e']} for w in d] for d in dong]})
    for a, b in zip(out, out[1:]):
        a['den'] = min(a['den'], b['tu'])
    return out


# ---------------- giải kế hoạch ----------------
def _co_dau_viet(s):
    return bool(re.search(r'[àáạảãâầấậẩẫăằắặẳẵèéẹẻẽêềếệểễìíịỉĩòóọỏõôồốộổỗơờớợởỡùúụủũưừứựửữỳýỵỷỹđ]', str(s).lower()))


def giai(work, bao=loi):
    """→ (KH cho trang, CB danh sách footage cần chuẩn bị, SFX cue, nhật ký [(mức, thông báo)])."""
    work = Path(work)
    L = []
    E = lambda m: L.append(('⛔', m))
    Wn = lambda m: L.append(('⚠', m))
    TS = lambda m: L.append(('🔧', m))
    kh = doc_json(work / 'ke_hoach.json')
    lj = doc_json(work / 'loi.json')
    tn = doc_json(work / 'tai_nguyen.json')
    by = {r['ma']: r for r in tn.get('ds', [])}
    nn = kh.get('ngon_ngu') or lj.get('ngon_ngu') or 'vi'
    if nn != lj.get('ngon_ngu', nn):
        E(f"ngon_ngu {nn} khác tiếng của audio ({lj.get('ngon_ngu')}) — chữ trên hình phải đúng tiếng audio")
    T = NGON_NGU.get(nn, NGON_NGU['en'])
    if kh.get('CAN_CLAUDE_SUA', False):
        E('ke_hoach.json còn CAN_CLAUDE_SUA: true — Claude đọc lời + soi tài nguyên, viết lại theo nghĩa rồi đặt false')
    tu, khong = sua_tu(lj['tu'], kh.get('sua_loi'))
    for k in khong:
        Wn(f'sua_loi: không thấy cụm «{k}» trong lời (khoá phải đúng chữ Whisper trong loi_doc.txt)')
    het_loi = tu[-1]['e'] if tu else lj.get('dai', 10)
    cta = dict(kh.get('cta') or {})
    co_cta = cta.get('bat', True)
    dur = max(het_loi + DUOI, lj.get('dai', 0) + .2)
    if co_cta:
        cta.setdefault('tu', max(0, het_loi - 4))
        dur = max(dur, cta['tu'] + CTA_MIN)
    dur = math.ceil(dur * FPS) / FPS
    # ---- cảnh ----
    canh = sorted(kh.get('canh') or [], key=lambda c: c['tu'])
    if not canh:
        E('chưa có cảnh nào')
        return None, [], [], L
    if canh[0]['tu'] > .01:
        Wn(f"cảnh đầu bắt đầu {canh[0]['tu']}s → kéo về 0")
        canh[0]['tu'] = 0
    for c in canh:                       # ô ghép không ghi luc_o → trượt vào so le 0,12 s ngay đầu cảnh
        if c.get('bo_cuc') == 'ghep' and not c.get('luc_o') and isinstance(c.get('nguon'), list):
            c['luc_o'] = [round(float(c['tu']) + k * .12, 3) for k in range(len(c['nguon']))]
    CB, CS = [], []
    for i, c in enumerate(canh):
        cid = c.get('id') or f'c{i + 1}'
        tu0 = float(c['tu'])
        den = float(canh[i + 1]['tu']) if i + 1 < len(canh) else dur
        ch = c.get('chuyen', 'hoa_tan') if i > 0 else c.get('chuyen', 'loe')
        if ch not in CHUYEN:
            E(f'{cid}: chuyển cảnh lạ «{ch}» (có: {", ".join(CHUYEN)})')
            ch = 'hoa_tan'
        d_in = CHUYEN[ch][0] if i > 0 else 0
        ch_ra = canh[i + 1].get('chuyen', 'hoa_tan') if i + 1 < len(canh) else 'cat'
        d_out = CHUYEN.get(ch_ra, (0,))[0] if i + 1 < len(canh) else 0
        moc_hook = min([float(d['tu']) for d in kh.get('do_hoa') or [] if d.get('loai') == 'mo_dau'] or [0])
        truoc = canh[i - 1] if i > 0 else None
        montage = bool(truoc and c.get('bo_cuc') == 'the_doc' and truoc.get('bo_cuc') == 'the_doc'
                       and c.get('vi_tri', 'giua') == truoc.get('vi_tri', 'giua') and ch in ('hoa_tan', 'nhoe'))
        dai_c = den - tu0
        if ch == 'phong' and dai_c < .8 or ch != 'phong' and dai_c < 1.5:
            E(f'{cid} @ {tu0:.2f}s chỉ {dai_c:.2f}s — quá gấp, người xem chưa kịp nhìn')
        else:
            nguong = 1.8 if tu0 < moc_hook else (2.0 if montage else CANH_MIN)
            if dai_c < nguong - .01:
                Wn(f'{cid} @ {tu0:.2f}s đứng {dai_c:.2f}s (< {nguong:.1f} s) — gộp với cảnh kề / kéo dài cho kịp nhìn')
        a, b = max(0, tu0 - d_in / 2), min(dur, den + d_out / 2)
        sau = canh[i + 1] if i + 1 < len(canh) else None
        if sau and sau.get('bo_cuc') == 'ghep' and sau.get('luc_o'):      # ô ghép trượt vào lần lượt → cảnh này nằm dưới tới khi phủ kín
            b = min(dur, max(b, max(float(x) for x in sau['luc_o']) + .8))
        if c.get('bo_cuc') == 'ghep' and c.get('luc_o'):
            lo = [float(x) for x in c['luc_o']]
            if min(lo) < tu0 - .01 or lo != sorted(lo):
                E(f'{cid}: luc_o phải tăng dần và ≥ tu cảnh')
        nguon = c.get('nguon')
        ds_ng = nguon if isinstance(nguon, list) else [nguon]
        vao = c.get('vao', 0)
        ds_vao = vao if isinstance(vao, list) else [vao] * len(ds_ng)
        rs = []
        for m in ds_ng:
            if m not in by:
                E(f'{cid}: không có tài nguyên «{m}» (xem tai_nguyen.json)')
            else:
                rs.append(by[m])
        if not rs:
            continue
        bc = c.get('bo_cuc') or ('ghep' if len(rs) > 1 else ('the_doc' if rs[0]['doc'] else
                                                             ('the_anh' if rs[0]['loai'] == 'anh' and rs[0]['w'] < 1500 else 'tran')))
        if bc not in BO_CUC:
            E(f'{cid}: bo_cuc lạ «{bc}» (có: {", ".join(BO_CUC)})')
            bc = 'tran'
        if bc == 'ghep' and not 2 <= len(rs) <= 4:
            E(f'{cid}: ghep cần 2–4 nguồn')
        if bc == 'tran' and rs[0]['doc']:
            Wn(f"{cid}: {rs[0]['ma']} là clip DỌC mà để tràn khung ngang → phóng {W / rs[0]['w']:.1f}× sẽ mờ; dùng the_doc / ghep")
        if bc == 'tran' and rs[0]['loai'] == 'anh' and rs[0]['w'] < 1500:
            Wn(f"{cid}: ảnh {rs[0]['ma']} chỉ {rs[0]['w']} px ngang — tràn khung sẽ mờ, nên dùng the_anh")
        toc = float(c.get('toc_do', 1.0))
        cd = c.get('chuyen_dong', 'zoom_vao')
        if cd not in CHUYEN_DONG:
            E(f'{cid}: chuyen_dong lạ «{cd}»')
            cd = 'zoom_vao'
        vt = c.get('vi_tri', 'giua')
        if vt not in THE_DOC_X:
            E(f'{cid}: vi_tri «{vt}» (giua / trai / phai)')
            vt = 'giua'
        n = int(math.ceil((b - a) * FPS)) + 1
        lop = []
        def theo(f, k, mac):            # giá trị riêng từng nguồn (ô ghép): danh sách → phần tử k; 1 giá trị → dùng chung
            v = c.get(f, mac)
            if f == 'vung':
                return v[k] if isinstance(v, list) and v and isinstance(v[0], list) and k < len(v) else v
            return v[k] if isinstance(v, list) and k < len(v) else (v[-1] if isinstance(v, list) and v else v)
        for k, r in enumerate(rs):
            v0 = float(ds_vao[k] if k < len(ds_vao) else ds_vao[-1])
            if r['loai'] == 'clip':
                can = (b - a) * toc
                if v0 + can > r['dai'] + .05:
                    Wn(f"{cid}: {r['ma']} vào {v0:.1f}s + cần {can:.1f}s > clip {r['dai']:.1f}s → lùi điểm vào")
                    v0 = max(0, r['dai'] - can - .05)
            if bc == 'tran':
                kieu = 'full'
            elif bc == 'the_doc':
                kieu = 'card_doc'
            elif bc == 'ghep':
                kieu = 'panel'
            else:
                kieu = 'card_anh'
            pw = (W - GHEP_KHE * (len(rs) - 1)) // len(rs) if bc == 'ghep' else 0
            p = {'id': f'{cid}_{k}', 'ma': r['ma'], 'loai': r['loai'], 'file': r['file'], 'w': r['w'], 'h': r['h'], 'hdr': r.get('hdr'),
                 'kieu': kieu, 'vao': round(v0, 3), 'toc': toc, 'n': n, 'pw': pw,
                 'cat_x': float(theo('cat_x', k, .5)), 'cat_y': float(theo('cat_y', k, .5)), 'vung': theo('vung', k, None)}
            if p['vung'] is not None and (len(p['vung']) != 4 or not all(0 <= float(z) <= 1 for z in p['vung'])):
                E(f"{cid}: vung phải là [x0, y0, x1, y1] trong 0–1")
                p['vung'] = None
            CB.append(p)
            lop.append(p['id'])
            if k == 0 and bc in ('the_doc', 'the_anh'):
                q = dict(p, id=f'{cid}_nen', kieu='nen')
                CB.append(q)
        CS.append({'id': cid, 'tu': round(tu0, 3), 'den': round(den, 3), 'a': round(a, 3), 'b': round(b, 3), 'n': n, 'bo_cuc': bc,
                   'chuyen': ch if i > 0 else 'mo', 'd_in': d_in, 'chuyen_dong': cd, 'vi_tri': vt, 'toc': toc, 'lop': lop,
                   'nen': f'{cid}_nen' if bc in ('the_doc', 'the_anh') else None, 'nghieng': float(c.get('nghieng', 0)),
                   'loai_nguon': [r['loai'] for r in rs], 'nhan': c.get('nhan'), 'luc_o': c.get('luc_o'), 'pw': (W - GHEP_KHE * (len(rs) - 1)) // len(rs) if bc == 'ghep' else 0})
    # ---- đồ hoạ ----
    DH = []
    for k, d in enumerate(kh.get('do_hoa') or []):
        d = dict(d)
        did = d.setdefault('id', f'g{k + 1}')
        lo = d.get('loai')
        if lo not in LOAI_DH:
            E(f'{did}: loại đồ hoạ lạ «{lo}» (có: {", ".join(LOAI_DH)})')
            continue
        for f in BAT_BUOC.get(lo, ()):
            if not d.get(f):
                E(f'{did} ({lo}): thiếu «{f}»')
        if 'tu' not in d or 'den' not in d:
            E(f'{did}: thiếu tu / den')
            continue
        d['tu'], d['den'] = float(d['tu']), float(d['den'])
        if d['den'] - d['tu'] < (.9 if lo == 'hook_tu' else 1.2):
            E(f"{did} ({lo}) chỉ {d['den'] - d['tu']:.2f}s (< {'0,9' if lo == 'hook_tu' else '1,2'} s)")
        if d['den'] > dur + .01:
            Wn(f'{did}: den > hết video → cắt')
            d['den'] = dur
        if co_cta and d['den'] > cta['tu'] + .3:
            Wn(f"{did} ({lo}) chồng màn kết ({d['den']:.1f} > {cta['tu']:.1f}) → cắt về đầu màn kết")
            d['den'] = cta['tu'] + .3
        vt = d.get('vi_tri', 'giua' if lo in ('mo_dau', 'hook_tu', 'tieu_de', 'tu_khoa', 'so_lon', 'trich') else 'trai')
        if vt not in VI_TRI_DH:
            E(f'{did}: vi_tri «{vt}» (giua / trai / phai)')
        d['vi_tri'] = vt
        for m in d.get('muc') or []:
            if isinstance(m, dict):
                m.setdefault('luc', d['tu'])
                if m.get('icon') and m['icon'] not in ICON:
                    Wn(f"{did}: icon «{m['icon']}» chưa có → dùng sao")
                    m['icon'] = 'sao'
        if d.get('icon') and d['icon'] not in ICON:
            Wn(f"{did}: icon «{d['icon']}» chưa có → dùng ghim")
            d['icon'] = 'ghim'
        if nn == 'vi':
            for f in ('chinh', 'ten', 'khoa', 'dan', 'viet_tay', 'phu', 'nhan', 'noi'):
                s = d.get(f)
                if isinstance(s, str) and len(s.split()) >= 3 and not _co_dau_viet(s) and re.search(r'[a-z]', s.lower()):
                    Wn(f'{did}.{f}: «{s}» không có dấu tiếng Việt — kiểm lại')
        # KỊP NHÌN: mục cuối của chip / tu_khoa / liet_ke đứng ≥ HIEN_MIN
        if lo in ('chip', 'tu_khoa', 'liet_ke') and d.get('muc'):
            ms = [m for m in d['muc'] if isinstance(m, dict)]
            for m in ms:
                if d['den'] - float(m['luc']) < HIEN_MIN:
                    moi = round(d['den'] - HIEN_MIN, 2)
                    if moi < d['tu']:
                        Wn(f"{did}: mục «{m.get('chu')}» đứng < {HIEN_MIN}s — kéo den")
                    else:
                        TS(f"{did}: mục «{m.get('chu')}» hiện sớm {float(m['luc']):.2f}→{moi:.2f}s cho đủ {HIEN_MIN}s")
                        m['luc'] = moi
            luc = [float(m['luc']) for m in ms]
            for x in range(1, len(luc)):
                if luc[x] < luc[x - 1]:
                    ms[x]['luc'] = luc[x - 1] + .25
        DH.append(d)
    # chữ hook CHỜ cảnh mới vào xong (không hiện trên cảnh cũ / giữa cú chuyển) — vòng 3: "ĐẢO ĐÁ VÔI" hiện khi hình còn là biển mây
    for d in DH:
        if d['loai'] != 'hook_tu':
            continue
        for c in CS:
            xong = c['tu'] + c['d_in'] / 2
            if c['bo_cuc'] == 'ghep' and c.get('luc_o'):
                xong = max(float(x) for x in c['luc_o']) + .45
            if c['tu'] - c['d_in'] / 2 - .05 <= d['tu'] < xong - .02:
                TS(f"{d['id']}: chữ «{d.get('chu')}» chờ cảnh {c['id']} vào xong {d['tu']:.2f}→{xong:.2f}s")
                d['tu'] = round(xong, 2)
                break
    # chồng nhau: tối đa 1 đồ hoạ LỚN 1 lúc
    lon = sorted([d for d in DH if d['loai'] not in NHO], key=lambda d: d['tu'])
    for x, y in zip(lon, lon[1:]):
        if y['tu'] < x['den'] - .25:
            E(f"{x['id']} ({x['loai']}) và {y['id']} ({y['loai']}) chồng nhau {x['den'] - y['tu']:.2f}s — 1 lúc chỉ 1 đồ hoạ lớn")
    # ---- sub ----
    sub_cfg = kh.get('sub') or {}
    giu = list(sub_cfg.get('giu_lien') or []) + list((kh.get('sua_loi') or {}).values())
    SUB = gom_sub(tu, nn, giu) if sub_cfg.get('bat', True) else []
    if co_cta:
        for s in SUB:
            pass
    # ---- màn kết ----
    if co_cta:
        cta['den'] = dur
        cta.setdefault('tieu_de', T['tieu_de'])
        cta.setdefault('viet_tay', T['viet_tay'])
        cta['nut'] = cta.get('nut') or T['nut']
        cta['nut_da'] = cta.get('nut_da') or T['nut_da']
        cta['thich'] = cta.get('thich') or T['thich']
        cta['chia_se'] = cta.get('chia_se') or T['chia_se']
        cta['luc_bam'] = round(cta['tu'] + 1.9, 2)
        cta['luc_chuong'] = round(cta['luc_bam'] + .55, 2)
        cta['luc_thich'] = round(cta['luc_bam'] + 1.25, 2)
        if dur - cta['tu'] < CTA_MIN - .05:
            Wn(f"màn kết chỉ {dur - cta['tu']:.1f}s (< {CTA_MIN}s)")
    kenh = kh.get('kenh') or {}
    # ---- khoảng trống chữ ----
    moc = sorted([(d['tu'], d['den']) for d in DH] + ([(cta['tu'], dur)] if co_cta else []))
    t0 = 0.0
    for a_, b_ in moc:
        if a_ - t0 > 12:
            Wn(f'{t0:.1f}–{a_:.1f}s: {a_ - t0:.0f}s không có đồ hoạ chữ nào (nên ≤ 10 s)')
        t0 = max(t0, b_)
    # ---- SFX ----
    cue = []

    def S(ten, luc, dai=None):
        if ten not in SFX:
            return
        f, db, lech = SFX[ten]
        cue.append({'luc': round(max(0, luc + lech), 3), 'file': f, 'db': db, 'ten': ten, **({'dai': dai} if dai else {}),
                    **({'tren': SFX_TREN[ten]} if ten in SFX_TREN else {})})
    for i, c in enumerate(CS):
        if i == 0:
            continue
        sf = CHUYEN[c['chuyen']][1]
        if sf:
            S(sf, c['tu'] - c['d_in'] / 2)
    for d in DH:
        lo = d['loai']
        if lo == 'mo_dau':
            if d.get('drop', True):              # cú DROP: dồn → nổ trầm đúng lúc chữ đập vào
                S('riser', d['tu'] - 1.85)
                S('boom', d['tu'])
                S('lap_lanh', d['tu'] + .35)
            else:
                S('mo_dau', d['tu'])
                S('lap_lanh', d['tu'] + .9)
        elif lo == 'chuong':                    # whoosh đã có ở màn quét; chỉ thêm ding nhẹ lúc số tô xong
            S('chuong_so', d['tu'])
        elif lo in ('dia_danh', 'tieu_de', 'trich', 'tu_khoa', 'hook_tu'):
            pass                                 # chữ hiện KHÔNG kèm tiếng (người dùng chê "chuyển hình xong có sfx")
        elif lo == 'so_lon':
            dem = float(d.get('dem_tu', d['tu'] + .3))
            S('so_lon', dem - .2, dai=1.4)
            S('so_xong', dem + 1.3)
        elif lo == 'ban_do':
            S('ban_do', d['tu'])
            for p in d.get('diem') or []:
                S('ghim', float(p.get('luc', d['tu'])))
        elif lo in ('chip', 'liet_ke'):           # pop NHỎ (−4 dB dưới giọng tại chỗ)
            for m in d.get('muc') or []:
                if isinstance(m, dict):
                    S(lo, float(m['luc']))
    if co_cta and kh.get('sfx_cta', True):
        S('cta_vao', cta['tu'])
        if cta.get('lua_chon'):
            S('chip', cta['tu'] + .95)
        S('bam', cta['luc_bam'])
        S('chuong_bell', cta['luc_chuong'])
        S('thich', cta['luc_thich'])
    cue.sort(key=lambda x: x['luc'])
    gon = []
    UU = ('boom', 'riser')
    for x in cue:
        if gon and x['luc'] - gon[-1]['luc'] < .22 and x['ten'] not in UU:
            continue
        gon.append(x)
    KH = {'W': W, 'H': H, 'fps': FPS, 'dur': dur, 'ngon_ngu': nn, 'canh': CS, 'do_hoa': DH, 'sub': SUB, 'cta': cta if co_cta else None,
          'kenh': kenh, 'T': T, 'khe': GHEP_KHE, 'the_doc_cao': THE_DOC_CAO, 'the_doc_x': THE_DOC_X,
          'mau': kh.get('mau', {}), 'dien_anh': kh.get('dien_anh', True)}
    return KH, CB, gon, L


def kiem_kh(work, in_ra=True):
    KH, CB, cue, L = giai(work)
    if in_ra:
        for m, s in L:
            loi(f'{m} {s}')
        if KH:
            loi(f"→ {len(KH['canh'])} cảnh, {len(KH['do_hoa'])} đồ hoạ, {len(KH['sub'])} cụm sub, {len(cue)} SFX, dài {KH['dur']:.2f}s")
    so = sum(1 for m, _ in L if m == '⛔')
    loi('KIỂM KẾ HOẠCH: ' + ('ĐẠT' if not so and KH else f'{so} ⛔ — sửa rồi chạy lại'))
    return not so and KH is not None
