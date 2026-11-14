# -*- coding: utf-8 -*-
"""ke_hoach.py — đọc ke_hoach.json, kiểm (⛔ / ⚠ / 🔧), giải giờ → KH cho trang dựng + danh sách chuẩn bị footage + SFX."""
import math
import re
import unicodedata
from pathlib import Path

from chung import (BAN_DO_MIN, BINH_LUAN_CACH, BINH_LUAN_DUNG, BO_CUC, BO_CUC_CHO, CANH_MIN, CANH_TEASER_MIN, CAO_TRAO_DAI, CAO_TRAO_DAP, CAT_Y_DOC,
                   CHUYEN, CHUYEN_DONG, KY_XAO, KY_XAO_DROP,
                   CTA_MIN, DUOI, FPS, GHEP_KHE, H, HIEN_ANH, HIEN_MIN, ICON, KHONG_CACH, LOAI_DH, MO_MAN_DAI, MO_MAN_MAX, MO_MAN_MIN, NGON_NGU, NHO,
                   SFX, SFX_TREN, SUB_MAX_KY_TU, SUB_MAX_TU, SUB_NGAT, THE_DOC_CAO, THE_DOC_X, W, XUAT_PHAT_MAC_DINH, ASSETS, doc_json, gio_phut, loi,
                   so_km, TONG_HOP_CAT, TONG_HOP_NHIP, TONG_HOP_TOC, CHUYEN_LECH, CHUYEN_DAI, CHUYEN_NHIP, NAC_XONG, TONG_HOP_CD,
                   CAT_MIN_PHACH, CAT_MIN_S, CAT_MIN_THAN, DUNG_RO_MIN, DAY_S, CHU_LOE_MIN)

BAT_BUOC = {'mo_dau': ('chinh',), 'hook_tu': ('chu',), 'chuong': ('ten',), 'dia_danh': ('ten',), 'tu_khoa': ('muc',), 'tieu_de': ('khoa',), 'chip': ('muc',),
            'so_lon': ('so',), 'liet_ke': ('muc',), 'trich': ('noi',), 'ban_do': ('diem',), 'hanh_trinh': ('xuat_phat', 'diem_den'), 'binh_luan': ()}
VI_TRI_DH = ('giua', 'trai', 'phai')
BAN_DO_LOAI = ('hanh_trinh',)          # + chuong có toa_do → bản đồ A → B toàn màn

# ---- TEASER: phần thân viết theo giờ trong loi_doc.txt; có mo_man thì mọi giờ phần thân dời thêm `dai` giây ----
KHOA_GIO = {'tu', 'den', 'luc', 'dem_tu', 'luc_di', 'luc_den', 'luc_tg', 'luc_kc', 'luc_ten_di', 'luc_ten_den', 'luc_anh', 'luc_o', 'luc_cam_on', 'luc_binh_luan'}


def _tong_hop(mm, phach, N, by, E, Wn, TS):
    """MONTAGE TỔNG HỢP ≤ 10 s (khách 14/11/2026 vòng 3) + 5 KỸ XẢO MẪU người dùng gửi (ba cột, khung bung, dải trượt, khớp hình, hai nửa):
    xếp cảnh Claude liệt kê (theo thứ tự) lên lưới PHÁCH 0…N.
    Vai: 3 cảnh đầu = 'cot' (BA CỘT bật theo phách, cột 3 bung tràn) khi có ≥ 5 cảnh tên đầu, không thì cảnh đầu = 'mo';
    cuối = 'dinh' (DẢI TRƯỢT các điểm đến → phóng ra; cảnh trước đỉnh quá ngắn thì VỠ KÍNH); mọi cảnh tới cảnh có `chu` cuối = 'ten'
    (1 phách; kỹ xảo dài KHUNG BUNG / HAI NỬA → 2 phách); sau đó = 'nhanh' (1 phách — vòng 5: ½ phách "nhanh quá, khó chịu"). `nhip` (bước 0,5) / `vai` / `chuyen` ghi rõ thì giữ.
    → (cảnh teaser có tu / chuyen / _vt / _vs / _nhom / _dai, đồ hoạ teaser: tên đập theo phách + tít đỉnh)"""
    sh = [dict(c) for c in mm.get('canh') or [] if c.get('nguon')]
    if len(sh) < 3:
        E('mo_man tong_hop: cần ≥ 3 cảnh (mở → tên điểm đến / dồn → đỉnh)')
        return [], []
    if any('tu' in c for c in sh):
        TS('mo_man tong_hop: bỏ qua `tu` của cảnh — giờ cảnh do lưới phách tính')
    dd = sorted(b - a for a, b in zip(phach, phach[1:]) if b - a > .2)
    P = dd[len(dd) // 2] if dd else .6                 # 1 phách (giây) — mọi nấc kỹ xảo montage bám bội số ½ phách
    cuoi_chu = max([i for i, c in enumerate(sh) if c.get('chu')] or [-1])
    for i, c in enumerate(sh):
        c['_vai'] = c.get('vai') or ('mo' if i == 0 else 'dinh' if i == len(sh) - 1 else 'ten' if i <= cuoi_chu else 'nhanh')
    if mm.get('ba_cot', True) is not False and len(sh) >= 5 and all(c['_vai'] in ('mo', 'ten', 'cot') for c in sh[:3]) \
            and not any(c.get('chuyen') for c in sh[:3]):
        for c in sh[:3]:
            c['_vai'] = 'cot'
    # ---- kiểu cắt theo vai (trước khi chia phách: kỹ xảo dài cần cảnh vào ≥ 1,5 phách) ----
    k_ten = 0
    for i, c in enumerate(sh):
        v = c['_vai']
        if i == 0:
            c['chuyen'] = 'ba_cot' if v == 'cot' else 'cat'
            continue
        if c.get('chuyen'):
            continue
        if v == 'cot':
            c['chuyen'] = 'cat'                      # cột 2, 3: nhóm ba_cot điều khiển
        elif v == 'ten':
            q = TONG_HOP_CAT['ten']
            for _ in range(len(q)):
                ch = q[k_ten % len(q)]; k_ten += 1
                if ch not in CHUYEN_DAI or float(c.get('nhip', 2)) >= 1.5:
                    break
            c['chuyen'] = ch
        elif v == 'nhanh':
            q = TONG_HOP_CAT['nhanh']
            c['chuyen'] = q[sum(1 for x in sh[:i] if x['_vai'] == 'nhanh') % len(q)]
        elif v == 'dinh':
            c['chuyen'] = TONG_HOP_CAT['dinh']
    nb = []
    for i, c in enumerate(sh):
        v = c['_vai']
        mac = (2.0 if i == 2 else 1.0) if v == 'cot' else (2.0 if v == 'ten' and c['chuyen'] in CHUYEN_DAI else TONG_HOP_NHIP[v if v in TONG_HOP_NHIP else 'ten'])
        nb.append(round(float(c.get('nhip', mac)) * 2) / 2)
    nb_min = max(CAT_MIN_PHACH, math.ceil(CAT_MIN_S / P * 2 - 1e-6) / 2)   # LUẬT NHỊP CẮT: không cảnh nào < 1 phách / 0,55 s
    for i, c in enumerate(sh):
        if nb[i] < nb_min:
            if 'nhip' in c:
                TS(f"mo_man: cảnh {c.get('nguon')} nhip {nb[i]:g} → {nb_min:g} phách (luật nhịp cắt: cảnh ≥ {nb_min:g} phách / {CAT_MIN_S} s ở mọi chỗ)")
            nb[i] = nb_min
    if sh[-1]['chuyen'] == 'dai_truot' and len(sh) > 1 and nb[-2] < 1.5:   # dải trượt chạy trên cảnh trước đỉnh → cần ≥ 1,5 phách
        if 'nhip' in sh[-2]:
            sh[-1]['chuyen'] = TONG_HOP_CAT['dinh_ngan']
        else:
            nb[-2] = 2.0
    bo = []
    while N - sum(nb[:-1]) < TONG_HOP_NHIP['dinh']:   # cảnh đỉnh cần đủ 3 phách → bỏ bớt cảnh dồn (không bỏ cảnh trước đỉnh có dải trượt)
        cho = [i for i in range(1, len(sh) - 1) if sh[i]['_vai'] == 'nhanh' and not (i == len(sh) - 2 and nb[i] >= 1.5)]
        if cho:
            k = cho[-1]
            bo.append(sh[k].get('nguon')); del sh[k]; del nb[k]
            continue
        if N - sum(nb[:-1]) >= 2:                   # hết cảnh dồn để bỏ: đỉnh 2 phách vẫn chạy được
            break
        dai = [i for i in range(len(sh) - 1) if sh[i]['_vai'] == 'ten' and sh[i]['chuyen'] in CHUYEN_DAI and 'nhip' not in sh[i]]
        if dai:                                      # còn thiếu → đổi kỹ xảo dài thành cắt đập 1 phách
            sh[dai[-1]]['chuyen'], nb[dai[-1]] = 'dap', 1.0
            continue
        E(f'mo_man tong_hop: {sum(nb[:-1]):.1f} phách trước cảnh đỉnh > {N - 2} — bớt cảnh / nhịp (teaser {N} phách ≤ 10 s)')
        return [], []
    if bo:
        Wn(f"mo_man tong_hop: thừa cảnh, bỏ {', '.join(bo)} (teaser {N} phách)")
    k = 0
    while N - sum(nb[:-1]) > 4:                     # thừa phách → kéo dài cảnh tên / mở (không ghi nhip) tối đa 2 phách
        cho = [i for i in range(len(sh) - 1) if 'nhip' not in sh[i] and sh[i]['_vai'] in ('ten', 'mo') and nb[i] < 2]
        if not cho:
            break
        nb[cho[k % len(cho)]] += .5; k += 1
    nb[-1] = N - sum(nb[:-1])

    def tb(x):                                      # giờ của phách thứ x (x có thể lẻ nửa)
        i = int(math.floor(x + 1e-6))
        return phach[min(i, len(phach) - 1)] if x - i < .25 or i + 1 >= len(phach) else (phach[i] + phach[i + 1]) / 2
    pos = 0.0
    for i, c in enumerate(sh):
        c['tu'] = round(tb(pos), 3)
        c['_den_tm'] = round(tb(pos + nb[i]), 3)
        c['_nb'] = nb[i]
        pos += nb[i]
        v = c['_vai']
        c['id'] = c.get('id') or f't{i + 1}'
        c['_teaser'] = c['_tong_hop'] = c['giu_chuyen'] = True
        r = by.get(c['nguon']) or {}
        if r.get('loai') == 'clip' and v in TONG_HOP_TOC:
            c.setdefault('toc_do', TONG_HOP_TOC[v])
        c['_p'] = round(P, 4)
        c.setdefault('chuyen_dong', TONG_HOP_CD.get(v) or ('zoom_vao' if i % 2 == 0 else 'lia_phai'))
    for i in range(1, len(sh)):                     # cửa sổ chuyển: trước / sau cú cắt (CHUYEN_LECH), không nuốt quá nửa cảnh kề
        c, dt0, dt1 = sh[i], sh[i]['tu'] - sh[i - 1]['tu'], sh[i]['_den_tm'] - sh[i]['tu']
        if c['_vai'] == 'cot':
            c['_vt'] = c['_vs'] = 0.0
            continue
        if c['chuyen'] in CHUYEN_NHIP:              # nấc theo PHÁCH (vòng 4): cửa sổ = bội số phách, nấc cuối + 0,18 s chạy
            b0, b1 = CHUYEN_NHIP[c['chuyen']]
            c['_vt'] = round(min(b0 * P, .95 * dt0), 3)
            c['_vs'] = round(min(b1 * P + (NAC_XONG if b1 >= 1 else 0), dt1 - .02), 3)
            if c['chuyen'] == 'day_nhanh':          # cú đẩy cả khung ≥ 0,34 s (êm) nhưng chừa cảnh đứng rõ ≥ 0,25 s
                c['_vs'] = round(max(c['_vs'], min(DAY_S, dt1 - DUNG_RO_MIN)), 3)
            continue
        d = CHUYEN.get(c['chuyen'], (0,))[0]
        f0, f1 = CHUYEN_LECH.get(c['chuyen'], (.5, .5))
        lim = .6 if c['chuyen'] in CHUYEN_DAI else .5
        c['_vt'], c['_vs'] = round(min(d * f0, lim * dt0), 3), round(min(d * f1, lim * dt1), 3)
    sh[0]['_vt'] = sh[0]['_vs'] = 0.0
    # ---- A: nhóm BA CỘT — cột bật đúng phách, cột 3 bung tràn sau 1 phách, tên nhỏ dưới mỗi cột (tên cột 3 lớn dần ra giữa) ----
    if sh[0]['_vai'] == 'cot':
        c0, c1, c2 = sh[:3]
        bung = round(c2['tu'] + (P if c2['_den_tm'] - c2['tu'] >= 1.4 * P else max(.3, .5 * (c2['_den_tm'] - c2['tu']))), 3)  # cột 3 đứng 1 phách rồi bung ĐÚNG phách
        het = round(c2['_den_tm'] - (sh[3]['_vt'] if len(sh) > 3 else 0), 3)
        bung_dai = round(max(.2, min(.5 * P, .38, het - bung - .04)), 3)          # bung (outExpo) xong trong ½ phách, TRƯỚC kỹ xảo kế
        c0['_nhom'] = {'kieu': 'ba_cot', 'ids': [c0['id'], c1['id'], c2['id']], 'moc': [c0['tu'], c1['tu'], c2['tu']],
                       'bung': bung, 'bung_dai': bung_dai, 'het': het,
                       'nhan': [{'chu': x.get('chu') or '', 'nhan': x.get('nhan') or ''} for x in (c0, c1, c2)]}
        for x in (c0, c1):
            x['_b_min'] = round(min(bung + bung_dai + .05, het - .01), 3)   # cột 1, 2 còn hiện tới khi cột 3 phủ kín
    # ---- D: dải trượt → ảnh trong dải = các cảnh có tên (điểm đến), thiếu thì cảnh trước ----
    for i, c in enumerate(sh):
        if c['chuyen'] == 'dai_truot' and not c.get('dai'):
            ds_ = [x['id'] for x in sh if x is not c and x.get('chu')]
            ds_ += [x['id'] for x in sh[:i][::-1] if x is not c and x['id'] not in ds_]
            c['_dai'] = ds_[:3]
    # ---- chữ: tên điểm đến đập lúc cảnh LỘ HẾT (cắt thường = đúng cú cắt; khung bung / hai nửa = lúc tràn màn), đứng tới tên kế ----
    dh = []
    for i, c in enumerate(sh):
        if not c.get('chu') or c['_vai'] == 'cot':
            continue
        if c['chuyen'] in ('hai_nua', 'hai_nua_doc'):   # F — cú ĐẨY: chữ chạy theo mép chia (không đập giữa) + người tách nền nhô qua mép
            c['_day_chu'] = {'chu': c['chu'], 'nhan': c.get('nhan') or ''}
            c['_nv'] = c['chuyen'] == 'hai_nua' and c.get('nhan_vat', True) is not False   # người tách nền: chỉ chia trái / phải
            continue
        j = i + 1
        while j < len(sh) and not sh[j].get('chu') and sh[j]['_vai'] in ('ten', 'mo'):
            j += 1
        den = sh[j]['tu'] - (sh[j].get('_vt') or 0) if j < len(sh) else sh[-1]['_den_tm']
        tu = c['tu'] + (P if c['chuyen'] in CHUYEN_NHIP and CHUYEN_NHIP[c['chuyen']][1] >= 1 else
                        .62 * c['_vs'] if c['chuyen'] in CHUYEN_DAI else 0)   # khung bung: tên đập đúng NẤC CHỐT (tràn màn, phách sau)
        if den - .02 - tu < .62:
            tu = max(c['tu'], den - .64)
        dh.append({'id': f'tn{len(dh) + 1}', 'loai': 'hook_tu', 'chu': c['chu'], 'tu': round(tu, 3), 'den': round(den - .02, 3),
                   'vi_tri': c.get('vi_tri_chu', 'giua'), 'co': c.get('co_chu', 210), 'dap': True, '_teaser': True, '_tong_hop': True,
                   **{k: c[k] for k in ('nhan', 'icon', 'y') if c.get(k)}})
    dn = mm.get('dinh') or {}
    if dn.get('khoa'):
        h = sh[-1]
        tu_d = h['tu'] + (P if h['chuyen'] == 'dai_truot' and h['_den_tm'] - h['tu'] >= 2.2 * P else .7 * h['_vs'] if h['chuyen'] in CHUYEN_DAI else .06)
        dh.append({'id': 'tn_dinh', 'loai': 'tieu_de', 'tu': round(tu_d, 3), 'den': round(h['_den_tm'] - .04, 3),   # tít đập PHÁCH sau ảnh đỉnh dừng
                   'vi_tri': dn.get('vi_tri', 'giua'), 'dap': True, 'sfx': False, '_teaser': True, '_tong_hop': True,
                   'co': dn.get('co', 210), **{k: dn[k] for k in ('dan', 'khoa', 'viet_tay', 'y', 'mau') if dn.get(k)}})
    else:
        Wn('mo_man tong_hop: chưa có `dinh.khoa` (tít đập cùng cảnh đỉnh — vd "4 điểm đến")')
    TS('montage tổng hợp: ' + ' | '.join(f"{c['nguon']} {c['_vai']} {c['tu']:.2f}s {c['chuyen']}" + (f" «{c['chu']}»" if c.get('chu') else '')
                                          for c in sh))
    return sh, dh


def _dich(o, off):
    """dời mọi khoá giờ (tu, den, luc…) trong cảnh / đồ hoạ / cta (lồng nhau) thêm off giây."""
    if isinstance(o, dict):
        for k, v in list(o.items()):
            if k in KHOA_GIO and isinstance(v, (int, float)) and not isinstance(v, bool):
                o[k] = round(float(v) + off, 3)
            elif k in KHOA_GIO and isinstance(v, list) and all(isinstance(z, (int, float)) for z in v):
                o[k] = [round(float(z) + off, 3) for z in v]
            elif isinstance(v, (dict, list)) and k not in ('toa_do', 'bd'):
                _dich(v, off)
    elif isinstance(o, list):
        for z in o:
            _dich(z, off)


def _nhac_file(kh, work):
    nh = kh.get('nhac')
    if nh is False:
        return None
    nh = nh or doc_json(Path(work) / 'tai_nguyen.json').get('nhac')
    return nh if nh and Path(nh).exists() else None


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
    # ---- TEASER mở màn (mo_man): ~20 s nhạc + cảnh đẹp nhất cắt theo nhịp + chữ lớn, rồi giọng mới vào ----
    import copy
    kh = copy.deepcopy(kh)
    mm = kh.get('mo_man') or {}
    nhac_f = _nhac_file(kh, work)
    OFF, nhip_d, nhac_dau, phach = 0.0, None, None, []
    if mm and mm.get('bat', True) is not False and mm.get('canh'):
        if not nhac_f:
            Wn('mo_man: teaser cần NHẠC NỀN (Resources không có nhạc) → bỏ teaser, video mở thẳng bằng hook lời')
            mm = {}
        else:
            import nhip as NH
            nhip_d = NH.phan_tich(nhac_f, work, bao=lambda m: None)
            kieu_mm = mm.get('kieu', 'tong_hop')
            if kieu_mm not in ('tong_hop', 'nhip'):
                E(f'mo_man.kieu «{kieu_mm}» (tong_hop / nhip)')
                kieu_mm = 'tong_hop'
            if kieu_mm == 'nhip':
                Wn('mo_man kieu "nhip" (1 cảnh / ô nhịp) — khách chê "tuần tự, chưa cao trào"; mặc định là "tong_hop"')
            dai = float(mm.get('dai', MO_MAN_DAI))
            if not MO_MAN_MIN <= dai <= MO_MAN_MAX:
                Wn(f'mo_man.dai {dai:.1f}s ngoài {MO_MAN_MIN:.0f}–{MO_MAN_MAX:.0f}s (khách chốt: giới thiệu 5–10 s, giọng vào trước giây 10)')
                dai = min(max(dai, MO_MAN_MIN), MO_MAN_MAX)
            nhac_dau = mm.get('nhac_tu')
            if nhac_dau is None:
                nhac_dau = NH.chon_dau(nhip_d, dai)
                TS(f'mo_man: nhạc teaser bắt đầu từ {nhac_dau:.2f}s của bài (đoạn cao trào, đầu ô nhịp ≈ {nhip_d["bpm"]:.0f} BPM)')
            if kieu_mm == 'tong_hop':
                # khớp độ dài về PHÁCH gần nhất ≤ 10 s → giọng vào đúng phách, trước giây thứ 10
                pa = [x - nhac_dau for x in nhip_d['nhip'] if -.01 <= x - nhac_dau <= MO_MAN_MAX + .01]
                on = [x for x in pa if x >= MO_MAN_MIN - .01]
            else:
                on = [x - nhac_dau for x in nhip_d['o_nhip'] if MO_MAN_MIN - .01 <= x - nhac_dau <= MO_MAN_MAX + .01]
            if on:
                k = min(on, key=lambda x: abs(x - dai))
                if abs(k - dai) > .02:
                    TS(f'mo_man: dài {dai:.2f}s → {k:.2f}s (đúng {"phách" if kieu_mm == "tong_hop" else "đầu ô nhịp"})')
                dai = round(k, 3)
            OFF = dai
            phach = [round(x - nhac_dau, 3) for x in nhip_d['nhip'] if -.01 <= x - nhac_dau <= OFF + .01]
            if phach and phach[0] > .05:
                phach = [0.0] + phach
            # phần thân: mọi giờ dời OFF
            for c in kh.get('canh') or []:
                _dich(c, OFF)
            for d in kh.get('do_hoa') or []:
                _dich(d, OFF)
            if kh.get('cta'):
                _dich(kh['cta'], OFF)
            kh['bo_di_chuyen'] = [float(x) + OFF for x in kh.get('bo_di_chuyen') or []]
            tu = [dict(w, s=round(w['s'] + OFF, 3), e=round(w['e'] + OFF, 3)) for w in tu]
            body = kh.get('canh') or []
            if body and float(min(c['tu'] for c in body)) > OFF + .01:
                Wn(f'cảnh đầu phần thân không bắt đầu đúng lúc giọng vào — kéo về {OFF:.2f}s')
                min(body, key=lambda c: c['tu'])['tu'] = OFF
            if kieu_mm == 'tong_hop':
                N = len(phach) - 1
                tc, td0 = _tong_hop(mm, phach, N, by, E, Wn, TS)
                if tc:
                    tc[0]['tu'] = 0.0
                    # giọng vào: cú cắt đầu phần thân = TIA SÁNG quét (Claude ghi kỹ xảo khác thì giữ)
                    b0 = min(body, key=lambda c: c['tu']) if body else None
                    if b0 is not None and b0.get('chuyen') not in KY_XAO:
                        b0['chuyen'] = TONG_HOP_CAT['giong']
                        b0['giu_chuyen'] = True
                    if b0 is not None:
                        b0['_giong'] = True           # cú CHỐT vào lời: riser dồn + kỹ xảo + boom (khách vòng 4: "như đổ vỡ ở demo 3")
            else:
                # cảnh teaser kiểu cũ: giờ riêng 0…dai, bắt về phách gần nhất
                tc = sorted([dict(c) for c in mm['canh']], key=lambda c: float(c['tu']))
                for i, c in enumerate(tc):
                    c['tu'] = 0.0 if i == 0 else NH.bat_nhip(float(c['tu']), phach)
                    c.setdefault('id', f't{i + 1}')
                    c.setdefault('chuyen', 'phong' if i else 'cat')
                    c['_teaser'] = True
                if tc and tc[-1]['tu'] > OFF - CANH_TEASER_MIN:
                    E(f"mo_man: cảnh teaser cuối bắt đầu {tc[-1]['tu']:.2f}s — quá sát lúc giọng vào ({OFF:.2f}s)")
                td0 = []
            kh['canh'] = tc + [c for c in body]
            td = td0 + [dict(d, _teaser=True) for d in mm.get('do_hoa') or []]
            for d in td:
                if 'tu' in d and float(d['tu']) > .01 and not d.get('_tong_hop'):
                    d['tu'] = NH.bat_nhip(float(d['tu']), phach, .25)
            kh['do_hoa'] = td + list(kh.get('do_hoa') or [])
            loi_teaser = [d for d in td if float(d.get('den', 0)) > OFF + .05]
            for d in loi_teaser:
                E(f"{d.get('id', d.get('loai'))}: chữ teaser kéo quá lúc giọng vào ({OFF:.2f}s)")
    elif not mm:
        Wn('chưa có mo_man (TEASER ~20 s đầu: cảnh đẹp nhất cắt theo nhịp nhạc + chữ lớn — khách 14/11/2026 chốt "đầu video cao trào giữ người xem")')
    het_loi = tu[-1]['e'] if tu else lj.get('dai', 10) + OFF
    cta = dict(kh.get('cta') or {})
    co_cta = cta.get('bat', True)
    dur = max(het_loi + DUOI, lj.get('dai', 0) + OFF + .2)
    if co_cta:
        cta.setdefault('tu', max(0, het_loi - 4))
        dur = max(dur, cta['tu'] + CTA_MIN)
        # màn KẾT CẢM ƠN: câu hỏi (nếu có) → "Cảm ơn bạn đã xem" khi giọng đọc xong → tay bấm Đăng ký → chuông → Thích
        if cta.get('luc_cam_on'):
            cta['luc_cam_on'] = round(float(cta['luc_cam_on']), 2)
        elif cta.get('cau_hoi'):
            cta['luc_cam_on'] = round(max(cta['tu'] + 1.4, min(het_loi + .15, cta['tu'] + 3.5)), 2)
        else:
            cta['luc_cam_on'] = round(cta['tu'] + .5, 2)
        cta['luc_bam'] = round(cta['luc_cam_on'] + 1.8, 2)
        cta['luc_chuong'] = round(cta['luc_bam'] + .55, 2)
        cta['luc_thich'] = round(cta['luc_bam'] + 1.3, 2)
        dur = max(dur, cta['luc_thich'] + 1.5)
    dur = math.ceil(dur * FPS) / FPS
    # ---- cảnh ----
    canh = sorted(kh.get('canh') or [], key=lambda c: c['tu'])
    if not canh:
        E('chưa có cảnh nào')
        return None, [], [], L
    if canh[0]['tu'] > .01:
        Wn(f"cảnh đầu bắt đầu {canh[0]['tu']}s → kéo về 0")
        canh[0]['tu'] = 0
    # ---- CAO TRÀO ~30 s đầu (khách 14/11/2026: "những cảnh đầu làm xịn xò, hiệu ứng chuyển cảnh xịn xò liên tục, kỹ xảo điện ảnh…
    # 5 s đầu kỹ xảo xịn vào… những cái hay tinh tuý ở 30 s đầu, sau 30 giây đầu như bình thường"): MỌI cú cắt từ 0 tới cú DROP
    # (mo_dau đầu tiên; không có thì 30 s) tự thành 1 KỸ XẢO ĐIỆN ẢNH xoay vòng (KY_XAO), cú cắt trùng DROP = xuyên cảnh; kỹ xảo Claude
    # ghi rõ thì giữ; `man` (mở chương) / `giu_chuyen: true` giữ nguyên. Teaser: cú đập theo phách giữa 2 cú cắt. Sau đoạn này: chuyển êm.
    ct = kh.get('cao_trao', {})
    ct = {'bat': False} if ct is False else (ct if isinstance(ct, dict) else {})
    moc_drop = min([float(d['tu']) for d in kh.get('do_hoa') or [] if d.get('loai') == 'mo_dau'] or [-1.0])
    het_ct = float(ct.get('het') or (moc_drop if 8 <= moc_drop <= 45 else CAO_TRAO_DAI))
    cao_trao = None
    if ct.get('bat', True) is not False:
        seq = [x for x in (ct.get('fx') or KY_XAO) if x in CHUYEN] or list(KY_XAO)
        # montage đã dùng kỹ xảo nào → phần hook sau đó ưu tiên kiểu CHƯA dùng; vỡ kính (cảnh đỉnh) không lặp lại
        da = [c.get('chuyen') for c in canh if c.get('_tong_hop') or c.get('giu_chuyen')]
        if da and not ct.get('fx'):
            seq = [x for x in seq if x not in da] + [x for x in seq if x in da and x != 'vo_kinh'] or seq
        lay = lambda k: seq[k] if k < len(seq) else seq[1 + (k - len(seq)) % max(1, len(seq) - 1)] if len(seq) > 1 else seq[0]
        k, truoc, doi = 0, None, []
        for i in range(1, len(canh)):
            c = canh[i]
            if float(c['tu']) > het_ct + .01:
                break
            ch0 = c.get('chuyen')
            if ch0 in KY_XAO or ch0 == 'man' or c.get('giu_chuyen'):
                truoc = ch0
                continue
            if moc_drop > 0 and abs(float(c['tu']) - moc_drop) < .06:
                ch = KY_XAO_DROP if truoc != KY_XAO_DROP else 'xoay'
            else:
                ch = lay(k); k += 1
                sau_drop = i + 1 < len(canh) and moc_drop > 0 and abs(float(canh[i + 1]['tu']) - moc_drop) < .06
                if ch == truoc or (sau_drop and ch == KY_XAO_DROP):
                    ch = lay(k); k += 1
            c['chuyen'] = ch
            truoc = ch
            doi.append(f"{c.get('id', i)} {ch}")
        # cửa sổ kỹ xảo không nuốt quá nửa cảnh kề (cảnh 2 s → mỗi cú ≤ 1 s, còn ≥ 1 s đứng yên cho người xem kịp nhìn)
        for i in range(1, len(canh)):
            c = canh[i]
            if float(c['tu']) > het_ct + .01:
                break
            if c.get('chuyen') in KY_XAO and '_vt' not in c:
                dai_truoc = float(c['tu']) - float(canh[i - 1]['tu'])
                dai_nay = (float(canh[i + 1]['tu']) if i + 1 < len(canh) else dur) - float(c['tu'])
                if c['chuyen'] in CHUYEN_DAI and not c.get('giu_chuyen') and min(dai_truoc, dai_nay) < 1.8:
                    c['chuyen'] = 'xoay'                 # kỹ xảo dài (khung bung / hai nửa / dải trượt) cần 2 cảnh ≥ 1,8 s
                d0 = CHUYEN[c['chuyen']][0]
                f0, f1 = CHUYEN_LECH.get(c['chuyen'], (.5, .5))
                lim = .6 if c['chuyen'] in CHUYEN_DAI else .5
                c['_vt'], c['_vs'] = round(min(d0 * f0, lim * dai_truoc), 3), round(min(d0 * f1, lim * dai_nay), 3)
                c['_d'] = round(c['_vt'] + c['_vs'], 3)
        dap = []
        if phach:                                   # teaser: đập theo phách ở GIỮA 2 cú cắt (cú cắt đã nằm đầu ô nhịp)
            cat = [float(c['tu']) for c in canh if float(c['tu']) <= OFF + .01]
            for j, b in enumerate(phach):
                if j % 2 or b < .45 or b > OFF - .3 or any(abs(b - x) < .45 for x in cat):
                    continue
                dap.append({'t': round(b, 3), 'm': CAO_TRAO_DAP[0] if b < 5.2 else CAO_TRAO_DAP[1]})
        cao_trao = {'het': round(het_ct, 3), 'mo': bool(OFF) and ct.get('mo', True) is not False, 'dap': dap}
        if doi:
            TS(f"cao trào 0–{het_ct:.1f}s: kỹ xảo {', '.join(doi)}" + (f'; {len(dap)} cú đập theo phách' if dap else ''))
    for c in canh:                       # ô ghép không ghi luc_o → trượt vào so le 0,12 s ngay đầu cảnh
        if c.get('bo_cuc') == 'ghep' and not c.get('luc_o') and isinstance(c.get('nguon'), list):
            c['luc_o'] = [round(float(c['tu']) + k * .12, 3) for k in range(len(c['nguon']))]
    for i, c in enumerate(canh):
        c.setdefault('id', f'c{i + 1}')
    for i, c in enumerate(canh):
        if c.get('chuyen') == 'dai_truot' and not c.get('_dai'):
            c['_dai'] = [x['id'] for x in (canh[i + 1:i + 4] if i + 4 <= len(canh) else canh[max(0, i - 3):i])]
        if c.get('chuyen') == 'khop_hinh' and not c.get('khop'):
            TS(f"{c['id']}: cắt nối theo hình chưa ghi `khop` → lúc dựng tự dò hình tròn / vùng sáng ở 2 khung cắt")
    CB, CS = [], []
    for i, c in enumerate(canh):
        cid = c.get('id') or f'c{i + 1}'
        tu0 = float(c['tu'])
        den = float(canh[i + 1]['tu']) if i + 1 < len(canh) else dur
        ch = c.get('chuyen', 'hoa_tan') if i > 0 else c.get('chuyen', 'loe')
        if ch not in CHUYEN:
            E(f'{cid}: chuyển cảnh lạ «{ch}» (có: {", ".join(CHUYEN)})')
            ch = 'hoa_tan'
        d_in = float(c.get('_d', CHUYEN[ch][0])) if i > 0 else 0
        ch_ra = canh[i + 1].get('chuyen', 'hoa_tan') if i + 1 < len(canh) else 'cat'
        d_out = float(canh[i + 1].get('_d', CHUYEN.get(ch_ra, (0,))[0])) if i + 1 < len(canh) else 0
        # cửa sổ chuyển cảnh LỆCH được (montage): d_t trước cú cắt, d_s sau cú cắt; mặc định chia đôi
        d_t = float(c.get('_vt', d_in / 2)) if i > 0 else 0
        d_s = float(c.get('_vs', d_in / 2)) if i > 0 else 0
        d_in = d_t + d_s
        d_out_s = float(canh[i + 1].get('_vs', d_out / 2)) if i + 1 < len(canh) else 0
        moc_hook = min([float(d['tu']) for d in kh.get('do_hoa') or [] if d.get('loai') == 'mo_dau'] or [0])
        truoc = canh[i - 1] if i > 0 else None
        montage = bool(truoc and c.get('bo_cuc') == 'the_doc' and truoc.get('bo_cuc') == 'the_doc'
                       and c.get('vi_tri', 'giua') == truoc.get('vi_tri', 'giua') and ch in ('hoa_tan', 'nhoe'))
        dai_c = den - tu0
        if c.get('_tong_hop'):                     # montage tổng hợp: cắt theo phách là CỐ Ý, nhưng LUẬT NHỊP CẮT: ≥ 1 phách / 0,55 s
            if dai_c < CAT_MIN_S - .01:
                E(f'{cid} @ {tu0:.2f}s chỉ {dai_c:.2f}s — cắt dồn dập (luật nhịp cắt: mọi cảnh ≥ 1 phách / {CAT_MIN_S} s, ở MỌI chỗ trong video)')
        elif ch == 'phong' and dai_c < .8 or ch != 'phong' and dai_c < CAT_MIN_THAN:
            E(f'{cid} @ {tu0:.2f}s chỉ {dai_c:.2f}s — quá gấp, người xem chưa kịp nhìn')
        else:
            nguong = CANH_TEASER_MIN if c.get('_teaser') else (1.8 if tu0 < moc_hook else (2.0 if montage else CANH_MIN))
            if dai_c < nguong - .01:
                Wn(f'{cid} @ {tu0:.2f}s đứng {dai_c:.2f}s (< {nguong:.1f} s) — gộp với cảnh kề / kéo dài cho kịp nhìn')
        a, b = max(0, tu0 - d_t), min(dur, max(den + d_out_s, float(c.get('_b_min', 0))))
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
        # LUÔN TRÀN MÀN (khách 14/11/2026: "không làm ảnh kiểu chia màn hình… giống màn dọc quá, lúc nào cũng full màn hình")
        bc = c.get('bo_cuc') or 'tran'
        if bc not in BO_CUC_CHO:
            E(f'{cid}: bo_cuc «{bc}» — đã chốt LUÔN TRÀN MÀN (không chia ô / thẻ dọc / thẻ ảnh) → bỏ bo_cuc hoặc ghi "tran"')
            bc = 'tran'
        if len(rs) > 1:
            E(f'{cid}: 1 cảnh chỉ 1 nguồn (không ghép ô) — tách thành nhiều cảnh nối tiếp')
            rs, ds_vao = rs[:1], ds_vao[:1]
        r0 = rs[0]
        phong = max(W / max(1, r0['w']), H / max(1, r0['h']))
        if r0['doc']:
            if 'cat_y' not in c:
                TS(f"{cid}: {r0['ma']} DỌC → tràn khung ngang, lấy dải 16:9 neo cao {CAT_Y_DOC:.2f} (đổi bằng cat_y 0–1)")
            if phong > 1.9:
                Wn(f"{cid}: {r0['ma']} dọc chỉ {r0['w']} px ngang — phóng {phong:.1f}× hơi mềm (đã làm nét bù); có cảnh ngang / 4K thì nên thay")
        elif phong > 1.6:
            Wn(f"{cid}: {r0['ma']} chỉ {r0['w']}×{r0['h']} — tràn khung phóng {phong:.1f}× sẽ mờ; nên thay nguồn to hơn")
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
                 'cat_x': float(theo('cat_x', k, .5)), 'cat_y': float(theo('cat_y', k, CAT_Y_DOC if r['doc'] else .5)),
                 'vung': theo('vung', k, None)}
            if p['vung'] is not None and (len(p['vung']) != 4 or not all(0 <= float(z) <= 1 for z in p['vung'])):
                E(f"{cid}: vung phải là [x0, y0, x1, y1] trong 0–1")
                p['vung'] = None
            CB.append(p)
            lop.append(p['id'])
            if k == 0 and bc in ('the_doc', 'the_anh'):
                q = dict(p, id=f'{cid}_nen', kieu='nen')
                CB.append(q)
        CS.append({'id': cid, 'tu': round(tu0, 3), 'den': round(den, 3), 'a': round(a, 3), 'b': round(b, 3), 'n': n, 'bo_cuc': bc,
                   'chuyen': ch if i > 0 else 'mo', 'd_in': d_in, 'd_t': d_t, 'd_s': d_s, 'chuyen_dong': cd, 'vi_tri': vt, 'toc': toc, 'lop': lop,
                   'nen': f'{cid}_nen' if bc in ('the_doc', 'the_anh') else None, 'nghieng': float(c.get('nghieng', 0)),
                   'loai_nguon': [r['loai'] for r in rs], 'nhan': c.get('nhan'), 'luc_o': c.get('luc_o'), 'pw': 0,
                   'teaser': bool(c.get('_teaser')), 'vai': c.get('_vai'), 'nhom': c.get('_nhom'), 'dai': c.get('_dai'),
                   'khop': c.get('khop'), 'p': c.get('_p'), 'day_chu': c.get('_day_chu'), 'nv': bool(c.get('_nv')),
                   'giong': bool(c.get('_giong'))})
    for a_, b_ in zip(CS, CS[1:]):                  # LUẬT NHỊP CẮT: mỗi cảnh ĐỨNG YÊN RÕ ≥ 0,25 s giữa 2 cú chuyển (mọi chỗ trong video)
        ro = (b_['tu'] - b_['d_t']) - (a_['tu'] + a_['d_s'])
        if ro < DUNG_RO_MIN - .01:
            E(f"{a_['id']} @ {a_['tu']:.2f}s chỉ đứng rõ {max(0, ro):.2f}s giữa 2 cú chuyển (< {DUNG_RO_MIN} s) — cảnh lướt qua, "
              f"khó chịu: kéo dài cảnh / bỏ bớt cảnh / chuyển ngắn hơn")
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
        if lo == 'binh_luan' and 'tu' in d:
            d.setdefault('den', float(d['tu']) + BINH_LUAN_DUNG)
            d.setdefault('vi_tri', 'phai')
        if 'tu' not in d or 'den' not in d:
            E(f'{did}: thiếu tu / den')
            continue
        d['tu'], d['den'] = float(d['tu']), float(d['den'])
        toi_thieu = (.5 if d.get('dap') else .9) if lo == 'hook_tu' else (1.0 if d.get('dap') else 1.2)
        if d['den'] - d['tu'] < toi_thieu - .005:
            E(f"{did} ({lo}) chỉ {d['den'] - d['tu']:.2f}s (< {toi_thieu:.1f} s)")
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
        if d['loai'] != 'hook_tu' or d.get('_tong_hop'):      # montage: tên đập ĐÚNG cú cắt là cố ý
            continue
        for c in CS:
            xong = c['tu'] + c['d_s']
            if c['bo_cuc'] == 'ghep' and c.get('luc_o'):
                xong = max(float(x) for x in c['luc_o']) + .45
            if c['tu'] - c['d_t'] - .05 <= d['tu'] < xong - .02:
                if d.get('_teaser') and phach:            # teaser: kỹ xảo xong → tên đập vào ĐÚNG PHÁCH kế tiếp (vẫn bám nhạc)
                    sau = [b for b in phach if xong - .02 <= b <= xong + .45]
                    xong = sau[0] if sau else xong
                TS(f"{d['id']}: chữ «{d.get('chu')}» chờ cảnh {c['id']} vào xong {d['tu']:.2f}→{xong:.2f}s")
                d['tu'] = round(xong, 2)
                con = float(d.get('den', xong + 9)) - d['tu']
                if con < CHU_LOE_MIN:                     # LUẬT NHỊP: chữ không được loé qua (< 1 s) ở bất kỳ đâu
                    TS(f"{d['id']}: chữ «{d.get('chu') or d.get('cau') or ''}» chỉ còn {max(0, con):.2f}s sau khi chờ cảnh — loé qua khó chịu "
                       f"(< {CHU_LOE_MIN} s) → BỎ chữ (sub vẫn có lời)")
                    d['_bo'] = True
                break
    DH = [d for d in DH if not d.get('_bo')]
    # ---- BẢN ĐỒ A → B kiểu Google Maps (khách 14/11/2026): mỗi `chuong` có toa_do + mọi `hanh_trinh` ----
    import ban_do_that as BDT
    truoc = dict(kh.get('xuat_phat') or XUAT_PHAT_MAC_DINH)
    so_ch = 0
    for d in sorted(DH, key=lambda d: d['tu']):
        lo, did = d['loai'], d['id']
        if lo == 'chuong':
            so_ch += 1
            d.setdefault('so', f'{so_ch:02d}')
        la_bd = lo == 'hanh_trinh' or (lo == 'chuong' and d.get('toa_do') and d.get('ban_do', True) is not False)
        if lo == 'chuong' and not d.get('toa_do') and d.get('ban_do', True) is not False:
            Wn(f"{did}: chương «{d.get('ten')}» chưa có toa_do → không có bản đồ A → B (run.py tim \"<tên>\" lấy toạ độ)")
        if not la_bd:
            continue
        if lo == 'chuong':
            d['diem_den'] = {'ten': d.get('ten_ban_do') or d['ten'], 'toa_do': d['toa_do']}
            if not d.get('xuat_phat'):
                d['xuat_phat'] = dict(truoc)
        hong = False
        for f in ('xuat_phat', 'diem_den'):
            p = d.get(f)
            if isinstance(p, str):
                p = d[f] = {'ten': p}
            td = (p or {}).get('toa_do')
            if not (isinstance(td, list) and len(td) == 2 and -90 <= float(td[0]) <= 90 and -180 <= float(td[1]) <= 180):
                E(f'{did}: {f}.toa_do phải là [lat, lon] (run.py tim "<tên>")')
                hong = True
        if hong:
            continue
        a, b = d['xuat_phat']['toa_do'], d['diem_den']['toa_do']
        if BDT.km_giua(a, b) < .3:
            E(f"{did}: điểm đi và điểm đến trùng nhau ({d['xuat_phat'].get('ten')} → {d['diem_den'].get('ten')})")
            continue
        if lo == 'chuong':
            truoc = {'ten': d['diem_den']['ten'], 'toa_do': b}
        pt = d.setdefault('phuong_tien', 'o_to')
        if pt not in T.get('xe', {}):
            E(f"{did}: phuong_tien «{pt}» (có: {', '.join(T.get('xe', {}))})")
            continue
        if d['den'] - d['tu'] < BAN_DO_MIN - .01:
            E(f"{did}: bản đồ chỉ {d['den'] - d['tu']:.2f}s (< {BAN_DO_MIN}s — bay ra, chạy tuyến, sà vào điểm đến)")
        dai_bd = d['den'] - d['tu']
        d['luc_di'] = round(float(d.get('luc_di', d['tu'] + .35)), 3)
        d['luc_den'] = round(float(d.get('luc_den') or max(d['luc_di'] + 1.6, min(d['den'] - 1.4, d['tu'] + .55 * dai_bd))), 3)
        if not d['tu'] <= d['luc_di'] < d['luc_den'] <= d['den'] - .6:
            E(f"{did}: cần tu ≤ luc_di < luc_den ≤ den − 0,6 (đang {d['tu']:.2f} / {d['luc_di']:.2f} / {d['luc_den']:.2f} / {d['den']:.2f})")
        # số giờ / km: lời nói có thì theo lời (thoi_gian / khoang_cach); không có thì ước tính OSRM, luôn "≈"
        try:
            _r, km, giay, kieu = BDT.tuyen(work, a, b, pt, bao=lambda m: None)
        except Exception as e:                                # noqa: BLE001
            km, giay, kieu = None, None, '?'
            Wn(f'{did}: không tính được tuyến ({e}) — cần mạng lần đầu')
        tg, kc = d.get('thoi_gian'), d.get('khoang_cach')
        d['chu_gio'] = str(tg) if tg else (gio_phut(giay, nn) if giay else None)
        if isinstance(kc, (int, float)) and not isinstance(kc, bool):
            d['km_so'], d['chu_km'] = float(kc), so_km(float(kc), nn)
        elif kc:
            d['km_so'], d['chu_km'] = None, str(kc)
        elif km:
            d['km_so'], d['chu_km'] = round(km), '≈ ' + so_km(km, nn)
        d['chu_ghi'] = d.get('chu_ghi') or (T['xe'].get(pt, '') + (' · ' + T['uoc'] if not tg and giay else ''))
        nguon_so = 'lời' if tg or kc else f'ước tính OSRM {kieu}'
        d['_so'] = f"{d['xuat_phat'].get('ten')} → {d['diem_den'].get('ten')}: {d.get('chu_km') or '—'} · {d.get('chu_gio') or '—'} ({nguon_so})"
        TS(f"{did}: bản đồ {d['_so']} — xác nhận số ở cổng duyệt")
        if not d['chu_gio'] and not d.get('chu_km'):
            Wn(f'{did}: bản đồ không có giờ / km (mạng?) — thẻ chỉ ghi tên')
    # ---- BÌNH LUẬN ẢO tiếng Anh / Hàn (khách 14/11/2026): mỗi chương 1 đợt 3 thẻ khen / chê nhẹ, tự đặt chỗ trống ----
    import binh_luan as BL
    bl_nn = tuple(kh.get('binh_luan_nn') or BINH_LUAN_NN)
    seed = kh.get('binh_luan_seed') or 'dln'
    da_dung = set()
    chs = sorted([d for d in DH if d['loai'] == 'chuong'], key=lambda d: d['tu'])
    het_than = cta['tu'] if co_cta else dur
    for d in [x for x in DH if x['loai'] == 'binh_luan']:          # bình luận Claude viết: điền phần thiếu
        ch = max([c for c in chs if c['tu'] <= d['tu']] or [None], key=lambda c: c['tu'] if c else 0)
        ten = d.get('ten') or (ch or {}).get('ten') or ''
        loai = d.get('loai_canh') or BL.loai_canh(ten, (ch or {}).get('phu'))
        if d.get('muc'):
            d['muc'] = [BL.dien(m if isinstance(m, dict) else {'chu': str(m)}, seed, ten, loai, k, d['tu'] + k * BINH_LUAN_CACH, da_dung)
                        for k, m in enumerate(d['muc'])]
        else:
            d['muc'] = BL.tao(seed, ten, loai, int(d.get('so', 3)), bl_nn, d['tu'], da_dung=da_dung)
        d['ten'] = ten
    if kh.get('binh_luan', True) is not False:
        for i, ch in enumerate(chs):
            if ch.get('binh_luan') is False:
                continue
            ket = chs[i + 1]['tu'] if i + 1 < len(chs) else het_than
            if any(x['loai'] == 'binh_luan' and ch['tu'] <= x['tu'] < ket for x in DH):
                continue
            so = int(ch.get('so_binh_luan', 3))
            dai_bl = max(BINH_LUAN_DUNG, (so - 1) * BINH_LUAN_CACH + 3.5)
            chon = None
            for vt in ('phai', 'trai'):
                # tránh MỌI đồ hoạ lớn (chữ 2 bên cùng lúc rối mắt); chỉ chung khung với nhãn nhỏ dia_danh / chip
                cam = [(x['tu'], x['den']) for x in DH if x['loai'] not in ('dia_danh', 'chip', 'binh_luan')]
                cam += [(x['tu'], x['den']) for x in DH if x['loai'] == 'binh_luan']
                t = round(float(ch.get('luc_binh_luan', ch['den'] + 2.5)), 2)
                while t + dai_bl <= ket - .3:
                    va = [(a_, b_) for a_, b_ in cam if a_ < t + dai_bl + .2 and b_ > t - .2]
                    if not va:
                        break
                    t = round(max(b_ for _a, b_ in va) + .3, 2)
                if t + dai_bl <= ket - .3 and (chon is None or t < chon[0] - 1.5):
                    chon = (t, vt)
            if not chon:
                Wn(f"{ch['id']}: chương «{ch.get('ten')}» không còn chỗ trống {dai_bl:.0f}s cho bình luận ảo → thêm tay (loai binh_luan) hoặc binh_luan: false")
                continue
            t, vt = chon
            ten = ch.get('ten_binh_luan') or ch.get('ten')
            loai = ch.get('loai_canh') or BL.loai_canh(ten, ch.get('phu'))
            bl = {'id': f"bl_{ch['id']}", 'loai': 'binh_luan', 'tu': t, 'den': round(t + dai_bl, 2), 'vi_tri': vt, 'ten': ten,
                  'muc': BL.tao(seed, ten, loai, so, bl_nn, t, da_dung=da_dung), '_tu_dong': True}
            DH.append(bl)
            TS(f"{bl['id']}: {so} bình luận ảo ({'/'.join(bl_nn)}, loại {loai}) cho «{ten}» {t:.1f}–{bl['den']:.1f}s, cột {vt}")
    # chồng nhau: tối đa 1 đồ hoạ LỚN 1 lúc
    lon = sorted([d for d in DH if d['loai'] not in NHO], key=lambda d: d['tu'])
    for x, y in zip(lon, lon[1:]):
        if y['tu'] < x['den'] - .25:
            E(f"{x['id']} ({x['loai']}) và {y['id']} ({y['loai']}) chồng nhau {x['den'] - y['tu']:.2f}s — 1 lúc chỉ 1 đồ hoạ lớn")
    # ---- sub ----
    sub_cfg = kh.get('sub') or {}
    giu = list(sub_cfg.get('giu_lien') or []) + list((kh.get('sua_loi') or {}).values())
    SUB = gom_sub(tu, nn, giu) if sub_cfg.get('bat', True) else []
    # ---- màn kết ----
    if co_cta:
        cta['den'] = dur
        cta.setdefault('tieu_de', T['tieu_de'])
        cta.setdefault('viet_tay', T['viet_tay'])
        cta['nut'] = cta.get('nut') or T['nut']
        cta['nut_da'] = cta.get('nut_da') or T['nut_da']
        cta['thich'] = cta.get('thich') or T['thich']
        cta['chia_se'] = cta.get('chia_se') or T['chia_se']
        cta['chuong_nhan'] = cta.get('chuong_nhan') or T.get('chuong_nhan') or ''
        # màn KẾT CẢM ƠN (khách 14/11/2026: "cuối video cảm ơn mọi người xem và hãy like và đăng ký")
        cta['cam_on'] = cta.get('cam_on') or T.get('cam_on') or T['tieu_de']
        cta['loi_moi'] = cta.get('loi_moi') or T.get('loi_moi') or T['viet_tay']
        if cta.get('lua_chon') and not cta.get('cau_hoi'):
            E('cta.lua_chon cần cta.cau_hoi (câu hỏi trong lời, vd "Bạn muốn đặt chân đến đâu đầu tiên?")')
        if len(cta.get('lua_chon') or []) > 5:
            Wn('cta.lua_chon > 5 lựa chọn — hàng nút quá dài')
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
    if cao_trao and cao_trao['mo']:
        S('fx_mo', 0.0)                          # khung 0 teaser: cú đập mở màn
    for i, c in enumerate(CS):
        if c.get('nhom'):                        # A — ba cột: 1 tiếng mỗi cột bật (cột 1 = cú đập mở màn) + 1 tiếng lúc cột 3 bung
            for m in c['nhom']['moc'][1:]:
                S('fx_cot', m)
            S('fx_cot_bung', c['nhom']['bung'])
        if i == 0:
            continue
        sf = CHUYEN[c['chuyen']][1]
        if c.get('vai'):                         # montage tổng hợp: nhạc là xương sống — tiếng THEO NẤC kỹ xảo, nấc nào cũng đúng phách
            p_ = c.get('p') or 0
            if c['chuyen'] == 'dai_truot':       # dải vào (1 phách trước) → khựng ½ phách → ảnh đỉnh dừng + phóng: thịch
                S('fx_buoc', c['tu'] - c['d_t'])
                if p_ and c['d_t'] >= .9 * p_:
                    S('fx_buoc', c['tu'] - .5 * p_)
                S('fx_cham', c['tu'])
            elif c['chuyen'] in CHUYEN_NHIP and p_ and CHUYEN_NHIP[c['chuyen']][1] >= 1:
                S('fx_buoc', c['tu'])            # khung bung / hai nửa: bật (phách) → nấc giữa (½) → CHỐT tràn màn (phách sau)
                S('fx_buoc', c['tu'] + .5 * p_)
                S('fx_cham', c['tu'] + p_)
            elif c['vai'] == 'dinh':
                if sf:
                    S(sf, c['tu'])
                S('fx_cham', c['tu'])
            elif sf and (c['chuyen'] in CHUYEN_DAI or c['chuyen'] == 'day_nhanh'):
                S(sf, c['tu'])
            continue
        if c['chuyen'] in KY_XAO:                # kỹ xảo cao trào: đỉnh tiếng đúng CÚ CẮT (cả trong teaser)
            if c.get('giong'):                   # GIỌNG VÀO: riser dồn từ cảnh đỉnh → vỡ / kỹ xảo + boom CHỐT đúng phách
                S('riser', c['tu'] - 1.85)
                S(sf, c['tu'])
                S('boom', c['tu'])
            elif c['chuyen'] == 'dai_truot':
                S(sf, c['tu'] - c['d_t'])
            else:
                S(sf, c['tu'])
            continue
        if c.get('teaser'):                      # teaser: nhạc là xương sống — cắt thường không kèm whoosh
            continue
        if sf:
            S(sf, c['tu'] - c['d_t'])
    for d in DH:
        lo = d['loai']
        if d.get('_teaser'):                    # chữ lớn đập vào trong teaser: 1 whoosh ngắn (không phải mọi chữ)
            if lo in ('mo_dau', 'tieu_de', 'tu_khoa', 'hook_tu', 'so_lon') and d.get('sfx', True):
                S('teaser_dap', d['tu'])
            continue
        if lo == 'binh_luan':
            for m in d.get('muc') or []:
                S('binh_luan', float(m.get('luc', d['tu'])))
            continue
        if lo == 'hanh_trinh' or (lo == 'chuong' and d.get('diem_den')):
            S('ban_do_vao', d['tu'])
            if d.get('phuong_tien') in ('o_to', 'xe_may', 'xe_buyt'):
                S('xe_chay', d['luc_di'], dai=round(d['luc_den'] - d['luc_di'], 2))
            S('toi_noi', d['luc_den'])
            continue
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
        S('lap_lanh', cta['luc_cam_on'])
        S('bam', cta['luc_bam'])
        S('chuong_bell', cta['luc_chuong'])
        S('thich', cta['luc_thich'])
    cue.sort(key=lambda x: x['luc'])
    # chữ teaser hiện cùng / ngay sau kỹ xảo → bỏ whoosh chữ (1 cú chuyển = 1 tiếng; khách chê "chuyển hình xong có sfx")
    moc_fx = [x['luc'] - SFX[x['ten']][2] for x in cue if x['ten'].startswith('fx_')]
    cue = [x for x in cue if not (x['ten'] == 'teaser_dap' and any(-.45 < x['luc'] - SFX['teaser_dap'][2] - m < 1.0 for m in moc_fx))]
    gon = []
    UU = ('boom', 'riser')
    for x in cue:
        if gon and x['luc'] - gon[-1]['luc'] < .22 and x['ten'] not in UU:
            continue
        gon.append(x)
    KH = {'W': W, 'H': H, 'fps': FPS, 'dur': dur, 'ngon_ngu': nn, 'canh': CS, 'do_hoa': DH, 'sub': SUB, 'cta': cta if co_cta else None,
          'kenh': kenh, 'T': T, 'khe': GHEP_KHE, 'the_doc_cao': THE_DOC_CAO, 'the_doc_x': THE_DOC_X,
          'mau': kh.get('mau', {}), 'dien_anh': kh.get('dien_anh', True),
          # teaser: giọng / sub / phần thân lùi `lech` giây; nhạc teaser lấy từ `teaser_dau` của bài, phần thân theo nhac_bat_dau
          'lech': round(OFF, 3), 'teaser_dau': round(nhac_dau, 3) if OFF and nhac_dau is not None else None,
          'nhac_bat_dau': kh.get('nhac_bat_dau'), 'bpm': nhip_d['bpm'] if nhip_d else None,
          'cao_trao': cao_trao}
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
