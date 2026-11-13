# -*- coding: utf-8 -*-
"""goi_y.py — GỢI Ý ghép TÀI NGUYÊN ↔ LỜI: tên file Resources / chú thích ảnh bài báo khớp cụm nào trong lời đọc, lúc mấy giây.

- So không dấu, không phân biệt hoa thường; tên viết liền / camelCase cũng khớp ('bunbo.jpg', 'PhoBo.jpg' ↔ 'bún bò', 'phở bò').
- Khớp GẦN theo âm (Whisper hay nghe lẫn ch/tr, s/x, d/gi/r, k/c…): 'Bún chả.jpg' ↔ lời 'bún trà' → gợi ý luôn sua_loi.
- Cụm nhắc quá nhiều lần trong lời (vd 'Hà Nội') = khớp CHUNG → hợp cảnh mở / cảnh chung, bị phạt khi so với cụm riêng.
- Chú thích ảnh bài báo chỉ tính cụm có TÊN RIÊNG (chữ hoa giữa câu) hoặc ≥ 3 từ thực — bỏ từ thường ('địa điểm', 'lưu giữ').
Chỉ là GỢI Ý — Claude vẫn phải mở ảnh / tờ khung để chọn theo NGHĨA.
"""
import re
from pathlib import Path

from chung import bo_dau, cau_di_chuyen, ghi_json

# chữ vô nghĩa hay gặp trong tên file điện thoại / máy ảnh / tải về
RAC = {'img', 'image', 'images', 'dsc', 'dscf', 'dscn', 'dji', 'vid', 'video', 'clip', 'photo', 'photos', 'pic', 'picture', 'anh', 'hinh',
       'final', 'copy', 'edit', 'edited', 'ban', 'mau', 'res', 'resource', 'resources', 'screenshot', 'untitled', 'new', 'pxl', 'mvimg',
       'gopr', 'mov', 'mp4', 'jpg', 'jpeg', 'png', 'fullsize', 'large', 'small', 'thumb', 'hd', 'fhd', 'uhd', '4k', '1080p', '720p',
       'stock', 'pexels', 'pixabay', 'unsplash', 'shutterstock', 'getty', 'freepik', 'canva', 'capcut', 'export', 'output', 'raw',
       'flycam', 'drone', 'broll', 'roll', 'slowmo', 'timelapse', 'hyperlapse', 'cut', 'part', 'phan', 'scene', 'shot'}
CHUNG_LAN = 4          # cụm có trong lời ≥ chừng này lần → khớp CHUNG
_AM = (('ngh', 'ng'), ('gh', 'g'), ('tr', 'ch'), ('gi', 'd'), ('r', 'd'), ('z', 'd'), ('x', 's'), ('k', 'c'), ('q', 'c'))


def _am(w):
    """dạng 'nghe giống' của 1 âm tiết không dấu (Whisper hay lẫn các phụ âm đầu này)."""
    for a, b in _AM:
        if w.startswith(a):
            w = b + w[len(a):]
            break
    return w[:-1] + 'i' if w.endswith('y') and len(w) > 1 else w


def _tach_hoa(s):
    o = []
    for i, ch in enumerate(s):
        if i and ch.isupper() and s[i - 1].islower():
            o.append(' ')
        o.append(ch)
    return ''.join(o)


_CAT = r'[\s_\-.,;:()\[\]{}+&/|!?"\'“”‘’–—…]+'


def _tu(s):
    """chuỗi → [(không dấu, nguyên gốc, viết hoa?)] (tách cả camelCase, gạch dưới, gạch ngang, chấm)."""
    out = []
    for x in re.split(_CAT, _tach_hoa(str(s))):
        b = bo_dau(x)
        if b:
            out.append((b, x, x[:1].isupper()))
    return out


def _tu_ten_file(ten):
    return [t for t in _tu(Path(ten).stem)
            if t[0] not in RAC and not t[0].isdigit() and not re.fullmatch(r'[a-z]{0,4}\d{2,}[a-z]?', t[0])]


def _dem(X, cum):
    n, L = 0, len(cum)
    for i in range(len(X) - L + 1):
        if all(X[i + q][0] == cum[q] for q in range(L)):
            n += 1
    return n


def _khop_lien(T, X, dan):
    """tên file ↔ lời: ghép từ liên tiếp của lời thành chuỗi liền, phải nằm trong tên viết liền ('bunbo' ↔ 'bún bò')."""
    N = ''.join(t[0] for t in T)
    if len(N) < 3:
        return []
    tok = {t[0] for t in T}
    kq = []
    for i in range(len(X)):
        cat = ''
        for j in range(i, min(i + 7, len(X))):
            cat += X[j][0]
            if cat not in N:
                break
            so = j - i + 1
            # 1 âm tiết chỉ tính khi tên file chỉ có đúng 1 từ ('pho.jpg') — tên nhiều từ mà khớp 1 âm tiết dễ nhầm
            # ('Đường_Hà Nội về đêm' ↔ 'thiên đường')
            if so == 1 and (len(T) > 1 or cat not in tok or len(cat) < 3 or cat in dan):
                continue
            if so > 1 and len(cat) < 5:
                continue
            if all(X[k][0] in dan for k in range(i, j + 1)):
                continue
            kq.append({'diem': len(cat) + 2 * (so - 1) + 6 * len(cat) / len(N), 'i': i, 'j': j, 'sua': None})
    return kq


def _khop_chuoi(C, X, dan, chung_cap=(), can_ten_rieng=False):
    """chuỗi từ (tên file nhiều từ / chú thích) ↔ lời: dãy từ liên tiếp NGHE GIỐNG nhau dài nhất (≥ 2 từ, ≥ 1 từ giống hệt).
    Có từ chỉ giống theo âm → kèm gợi ý sửa lời (sua_loi)."""
    Xa = [_am(x[0]) for x in X]
    Ca = [_am(c[0]) for c in C]
    N = sum(len(c[0]) for c in C) or 1
    kq = []
    for i in range(len(X)):
        for k in range(len(C)):
            if Xa[i] != Ca[k] or (i and k and Xa[i - 1] == Ca[k - 1]):
                continue
            L = 0
            while i + L < len(X) and k + L < len(C) and Xa[i + L] == Ca[k + L]:
                L += 1
            if L < 2:
                continue
            dung = sum(X[i + q][0] == C[k + q][0] for q in range(L))
            nd = [X[i + q][0] for q in range(L) if X[i + q][0] not in dan]
            if dung == 0 or len(nd) < 2:
                continue
            if can_ten_rieng and not any(C[k + q][2] and k + q > 0 for q in range(L)) and len(nd) < 3:
                continue                                    # chú thích: phải có tên riêng (chữ hoa giữa câu) hoặc ≥ 3 từ thực
            cum = tuple(X[i + q][0] for q in range(L))
            if cum in chung_cap and L < 4:
                continue
            sua = None
            if dung < L:
                sua = (' '.join(C[k + q][1] for q in range(L)), )
            dai = sum(len(C[k + q][0]) for q in range(L))       # cùng thang điểm với _khop_lien → phủ cả tên thì thắng
            kq.append({'diem': dai + 2 * (L - 1) + 6 * dai / N - 1.5 * (L - dung), 'i': i, 'j': i + L - 1, 'sua': sua})
    return kq


def _co_loi_rieng(X, d, dan):
    """chú thích ảnh ↔ lời: bỏ khớp mà mọi từ thực đều thuộc cụm 2 từ nhắc ≥ CHUNG_LAN lần trong lời
    ('của Thủ đô' / 'thủ đô Hà Nội' khi lời nói 'thủ đô' 4 lần, 'Hà Nội' 8 lần) — chỉ còn tên chung của cả bài, không chỉ ra ảnh nào."""
    toks = [X[q][0] for q in range(d['i'], d['j'] + 1)]
    phu = [False] * len(toks)
    for q in range(len(toks) - 1):
        if _dem(X, toks[q:q + 2]) >= CHUNG_LAN:
            phu[q] = phu[q + 1] = True
    return any(not phu[q] and toks[q] not in dan for q in range(len(toks)))


def _chu_loi(tu, X, i, j):
    """chữ Whisper (nguyên văn) của đoạn X[i..j]."""
    ks = sorted({X[q][3] for q in range(i, j + 1)})
    return ' '.join(re.sub(r'^[^\w]+|[^\w]+$', '', tu[k]['w']) for k in ks)


def goi_y(tu, cau, tn, bai, nn, work):
    """→ dict {id: {...}} + ghi goi_y.json / goi_y.txt trong work."""
    from ke_hoach import TU_DAN
    dan = {bo_dau(w) for w in TU_DAN.get(nn, set())}
    X = []                                                   # (không dấu, giây đầu, giây cuối, chỉ số trong tu)
    for k, w in enumerate(tu):
        for b, _, _ in _tu(w['w']):
            X.append((b, w['s'], w['e'], k))
    nguon = []
    for a in tn:
        nguon.append((a['id'], a['ten'], 'ten', _tu_ten_file(a['ten'])))
    for a in (bai or {}).get('anh', []):
        cap = ' '.join(x for x in (a.get('chu_thich'), a.get('alt')) if x)
        nguon.append((a['id'], cap[:80] or '(ảnh bài báo không chú thích)', 'cau', _tu(cap)))
    # cụm 2–3 từ có trong ≥ nửa số chú thích → chung, bỏ
    caps = [{tuple(t[0] for t in T[q:q + L]) for L in (2, 3) for q in range(len(T) - L + 1)} for _, _, kieu, T in nguon if kieu == 'cau']
    dem = {}
    for s in caps:
        for c in s:
            dem[c] = dem.get(c, 0) + 1
    chung_cap = {c for c, n in dem.items() if len(caps) >= 3 and n >= max(2, len(caps) / 2)}

    def cau_cua(t):
        for c in cau:
            if c['s'] - .05 <= t <= c['e'] + .05:
                return c
        return None

    KQ = {}
    for nid, ten, kieu, T in nguon:
        ds = []
        if T:
            if kieu == 'ten':
                ds = _khop_lien(T, X, dan) + (_khop_chuoi(T, X, dan) if len(T) >= 2 else [])
            else:
                ds = [d for d in _khop_chuoi(T, X, dan, chung_cap, can_ten_rieng=True) if _co_loi_rieng(X, d, dan)]
        if not ds:
            KQ[nid] = {'ten': ten, 'khop': None}
            continue
        for d in ds:                                         # phạt cụm chung (nhắc nhiều lần) để cụm riêng thắng
            d['lan'] = _dem(X, [X[q][0] for q in range(d['i'], d['j'] + 1)])
            d['xep'] = d['diem'] - 1.5 * min(d['lan'] - 1, 6)
        best = max(ds, key=lambda d: (d['xep'], d['diem']))
        cung = sorted([d for d in ds if abs(d['xep'] - best['xep']) < 1e-6 and
                       [X[q][0] for q in range(d['i'], d['j'] + 1)] == [X[q][0] for q in range(best['i'], best['j'] + 1)]],
                      key=lambda d: d['i'])
        luc = []
        for d in cung or [best]:
            if not luc or X[d['i']][1] - luc[-1] > 1.0:
                luc.append(round(X[d['i']][1], 2))
        c0 = cau_cua(luc[0])
        o = {'ten': ten, 'khop': _chu_loi(tu, X, best['i'], best['j']), 'luc': luc[:6], 'lan': best['lan'],
             'chung': best['lan'] >= CHUNG_LAN, 'diem': round(best['xep'], 1), 'cau': c0['text'] if c0 else ''}
        if best['sua']:
            moi = best['sua'][0]
            a, b = o['khop'].split(), moi.split()
            if kieu == 'ten' and len(a) == len(b):          # tên file viết hoa tuỳ tiện → hoa / thường theo chữ Whisper
                moi = ' '.join(y if x[:1].isupper() else y[:1].lower() + y[1:] for x, y in zip(a, b))
            o['sua_loi'] = {o['khop']: moi}
        KQ[nid] = o
    # ---- ghi ----
    dong = ['GỢI Ý GHÉP TÀI NGUYÊN ↔ LỜI (so tên file / chú thích ảnh với lời, không dấu, gần đúng theo âm). CHỈ LÀ GỢI Ý — vẫn mở ảnh / tờ khung.',
            'riêng = cụm hiếm → dùng ĐÚNG lúc đọc tới; chung = cụm nhắc nhiều lần → hợp cảnh mở / cảnh chung.', '']
    rieng = sorted([(k, v) for k, v in KQ.items() if v['khop'] and not v['chung']], key=lambda x: x[1]['luc'][0])
    chung = [(k, v) for k, v in KQ.items() if v['khop'] and v['chung']]
    khong = [(k, v) for k, v in KQ.items() if not v['khop']]
    for nhom, ds in (('KHỚP RIÊNG', rieng), ('KHỚP CHUNG', chung)):
        if not ds:
            continue
        dong.append(f'--- {nhom} ---')
        for k, v in ds:
            dong.append(f"{k:8s} {v['ten'][:46]:46s} ↔ «{v['khop']}» lúc {', '.join(f'{t:.1f}s' for t in v['luc'])}"
                        + (f" (nhắc {v['lan']} lần)" if v['chung'] else ''))
            if v['cau'] and not v['chung']:
                dong.append(f"{'':9s}câu: {v['cau'][:110]}")
        dong.append('')
    sl = {a: b for v in KQ.values() for a, b in (v.get('sua_loi') or {}).items()}
    if sl:
        dong.append('--- GỢI Ý SỬA LỜI (Whisper nghe gần giống tên tài nguyên → kiểm rồi đưa vào sua_loi, viết hoa tên riêng cho đúng) ---')
        for a, b in sl.items():
            dong.append(f'  «{a}» → «{b}»')
        dong.append('')
    if khong:
        dong.append('--- KHÔNG KHỚP TÊN (tự soi hình để chọn chỗ dùng) ---')
        for k, v in khong:
            dong.append(f"{k:8s} {v['ten'][:60]}")
        dong.append('')
    dc = cau_di_chuyen(cau, nn)
    if dc:
        dong.append('--- CÂU DI CHUYỂN A → B (BẮT BUỘC 1 đồ hoạ hanh_trinh phủ trọn câu — SKILL mục 13; câu thời gian / km nối tiếp '
                    'cùng 1 chuyến thì gộp 1 đồ hoạ; điểm đi thường ở câu TRƯỚC; tự dò, câu nào không phải đi lại thì bỏ qua) ---')
        for r in dc:
            k = next((i for i, c in enumerate(cau) if abs(c['s'] - r['s']) < 1e-6), None)
            truoc = cau[k - 1]['text'] if k else ''
            pt = r['pt'] or '? (lời không nói phương tiện → khong / ban_do, hoặc theo câu trước)'
            dong.append(f"  [{r['s']:.2f}–{r['e']:.2f}] phương tiện đoán: {pt} · số: {', '.join(r['cum'])}")
            dong.append(f"{'':9s}câu: {r['text'][:120]}")
            if truoc:
                dong.append(f"{'':9s}câu trước: {truoc[:110]}")
    (Path(work) / 'goi_y.txt').write_text('\n'.join(dong), encoding='utf-8')
    ghi_json(Path(work) / 'goi_y.json', KQ)
    return KQ
