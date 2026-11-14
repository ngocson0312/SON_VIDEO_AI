# -*- coding: utf-8 -*-
"""mo_hinh_3d.py — CẢNH 3D công trình đặt trên ảnh vệ tinh thật (kiểu đoạn 0–9 s của video mẫu Khánh Nguyễn).

Claude đọc ảnh phối cảnh dự án → tả công trình bằng tham số (tháp / khối đế / khối tự do) trong ke_hoach.json:
  "mo_hinh_3d": {vi_tri:{lat,lon,ten}, xoay, thap:[…], de:[…], khoi:[…], khu:{rong,sau}, cay_quanh, mau:{…}}
  "canh_3d": {"<id>": {cam:[{luc,nhin,goc,nghieng,xa,fov}], chu:[…], chu_thich:[…], logo:{…}, vong:[…], dia_danh:[…], tia:[…], duong_vien:[…]}}
Cảnh nào lấy footage {"nguon": "3d:<id>"} thì khung 3D được dựng (Three.js trong Chrome headless) thành chuỗi ảnh
rồi dùng như 1 clip: thẻ nổi / tràn màn / nền nhoè, chữ ngoài, SFX… y như footage thường.
Toạ độ: gốc = vi_tri, x = Đông, z = Nam, y = cao (mét thật). Xem references/mo_hinh_3d.md.
"""
import hashlib
import re
import shutil
from pathlib import Path

from chung import FPS, H, KHUNG, W, doc_json, ghi_json, loi, node, run, url
import ve_tinh

SCRIPTS = Path(__file__).resolve().parent
CAP3D_TOP = 1290           # mép trên chữ 2 tầng BÊN TRONG cảnh 3D (mẫu: "chỉ vỏn vẹn / 602 căn hộ" ở thấp, giữa khung)
MAX_CAO = 120 * 3.3 + 40


def _f(x, d=None):
    try:
        return float(x)
    except (TypeError, ValueError):
        return d


def _cao(loai, o):
    nen = _f(o.get('cao_nen'), 0) or 0
    if loai == 'thap':
        return nen + (o.get('chan') or 0) + int(o.get('tang') or 0) * (o.get('cao_tang') or 3.3) + (o.get('mai_cao') if o.get('mai_cao') is not None else 2.4 * (o.get('cao_tang') or 3.3))
    if loai == 'de':
        return nen + (o.get('cao') or 4.5 * (o.get('tang') or 3))
    return nen + (o.get('cao') or 3.6 * (o.get('tang') or 3))


def _kich(o):
    """(rộng, sâu) mặt bằng — tháp đa giác lấy theo khung bao các điểm."""
    if o.get('hinh') == 'da_giac' and isinstance(o.get('diem'), list) and len(o['diem']) >= 3:
        try:
            xs, zs = [float(p[0]) for p in o['diem']], [float(p[1]) for p in o['diem']]
            return max(xs) - min(xs), max(zs) - min(zs)
        except (TypeError, ValueError, IndexError):
            pass
    return _f(o.get('rong'), 0) or 0, _f(o.get('sau'), 0) or 0


def diem(spec, mh, bao, ten):
    """[x,y,z] hoặc "thap1@0.7" (tâm tháp 1 ở 70 % chiều cao) / "de1" / "khoi2@0.5" → [x,y,z] toạ độ mô hình."""
    if isinstance(spec, (list, tuple)) and len(spec) == 3 and all(_f(v) is not None for v in spec):
        return [float(v) for v in spec]
    if isinstance(spec, str):
        m = re.fullmatch(r'\s*(thap|de|khoi)(\d+)(?:@([\d.]+))?\s*', spec)
        if m:
            loai, i = m.group(1), int(m.group(2)) - 1
            k = float(m.group(3)) if m.group(3) else (.7 if loai == 'thap' else 1.0)
            ds = mh.get(loai) or []
            if 0 <= i < len(ds):
                o = ds[i]
                return [_f(o.get('x'), 0), round(_cao(loai, o) * k, 2), _f(o.get('z'), 0)]
    bao.L(f'{ten}: diem "{spec}" không hiểu — dùng [x,y,z] (m) hoặc "thap1@0.7" / "de1" / "khoi1@0.5"')
    return [0.0, 50.0, 0.0]


def pham_vi(mh):
    """(nửa cạnh mô hình theo mặt bằng, cao nhất) — để tự đặt vùng bóng, camera xem trước."""
    r, h = 30.0, 20.0
    for loai in ('thap', 'de', 'khoi'):
        for o in mh.get(loai) or []:
            w, d = _kich(o)
            r = max(r, abs(_f(o.get('x'), 0)) + (w + d) / 2)
            r = max(r, abs(_f(o.get('z'), 0)) + (w + d) / 2)
            h = max(h, _cao(loai, o))
    K = mh.get('khu') or {}
    r = max(r, (_f(K.get('rong'), 0) + _f(K.get('sau'), 0)) / 2 * .75)
    return r, h


# ---------------- kiểm ----------------
def anh_mat_file(work, spec):
    """thap.anh_mat: \"<id>\" (texture do run.py mat-anh nắn) → W/mat_anh/<id>.jpg"""
    mid = spec.get('id') if isinstance(spec, dict) else spec
    return Path(work) / 'mat_anh' / f'{mid}.jpg'


def kiem_mo_hinh(mh, bao, nhap_la_loi=True, work=None):
    if not isinstance(mh, dict):
        bao.L('thiếu khối "mo_hinh_3d": {vi_tri, thap/de/khoi, …} (cảnh có footage 3d:…)'); return False
    if nhap_la_loi and str(mh.get('_GHI_CHU', '')).startswith('NHÁP'):
        bao.L('mo_hinh_3d còn là NHÁP (2 tháp mẫu) — Claude phải MỞ ảnh dự án, dựng lại tháp / tầng / vườn treo / đế / hồ bơi theo ảnh, '
              'xoá "_GHI_CHU", chạy xem-3d so mo_hinh_3d.jpg với ảnh')
    if work is not None and not (Path(work) / 'mo_hinh_3d.jpg').exists():
        bao.C('chưa chạy xem-3d — chưa so mô hình với ảnh dự án (run.py xem-3d --work …, mở mo_hinh_3d.jpg)')
    vt = mh.get('vi_tri') or {}
    lat, lon = _f(vt.get('lat')), _f(vt.get('lon'))
    if lat is None or lon is None or not (-85 < lat < 85 and -180 <= lon <= 180):
        bao.L('mo_hinh_3d.vi_tri cần lat, lon (số) — tìm bằng run.py tim "<tên dự án / địa chỉ>"')
    if not vt.get('chac', True):
        bao.C(f"vị trí công trình là ĐOÁN ({vt.get('ten', '')}) — hỏi người dùng link Google Maps / toạ độ ở cổng duyệt")
    n = 0
    if mh.get('buoi', 'ngay') not in ('ngay', 'hoang_hon', 'chang_vang', 'dem'):
        bao.L(f"mo_hinh_3d.buoi '{mh.get('buoi')}' (ngay | hoang_hon | chang_vang | dem)")
    for loai, can in (('thap', ('rong', 'sau', 'tang')), ('de', ('rong', 'sau')), ('khoi', ('rong', 'sau'))):
        for i, o in enumerate(mh.get(loai) or []):
            n += 1
            hinh = o.get('hinh', 'chu_nhat')
            if loai == 'thap' and hinh not in ('chu_nhat', 'tron', 'bo_goc', 'da_giac'):
                bao.L(f"mo_hinh_3d.thap[{i + 1}].hinh '{hinh}' (chu_nhat | tron | bo_goc | da_giac)")
            for ka in ('anh_mat', 'anh_hoi'):
                if loai == 'thap' and o.get(ka):
                    if hinh != 'chu_nhat' or o.get('lui'):
                        bao.L(f"mo_hinh_3d.thap[{i + 1}].{ka} chỉ dán được lên tháp hộp chữ nhật không lùi tầng (đang hinh '{hinh}'{' + lui' if o.get('lui') else ''})")
                    elif work is not None and not anh_mat_file(work, o[ka]).exists():
                        bao.L(f"mo_hinh_3d.thap[{i + 1}].{ka} '{o[ka]}': chưa có {anh_mat_file(work, o[ka])} — chạy run.py mat-anh --id … trước")
            if loai == 'thap' and hinh == 'da_giac':
                P = o.get('diem')
                if not isinstance(P, list) or len(P) < 3 or any(not (isinstance(p, list) and len(p) >= 2 and _f(p[0]) is not None and _f(p[1]) is not None) for p in P):
                    bao.L(f'mo_hinh_3d.thap[{i + 1}] hinh da_giac cần "diem": ≥ 3 điểm [x, z] (m, quanh tâm tháp)')
                can = ('tang',)
            for k in can:
                if _f(o.get(k)) is None:
                    bao.L(f'mo_hinh_3d.{loai}[{i + 1}] thiếu {k}')
            for j, L in enumerate(o.get('lui') or []):
                co = _f((L or {}).get('co'))
                if not isinstance(L, dict) or _f(L.get('tu')) is None or co is None or not .3 <= co <= 1.0:
                    bao.L(f'mo_hinh_3d.{loai}[{i + 1}].lui[{j + 1}] cần {{"tu": tầng, "co": 0.3–1.0}}')
            if loai == 'thap':
                t = int(_f(o.get('tang'), 0))
                if not 1 <= t <= 120:
                    bao.L(f'mo_hinh_3d.thap[{i + 1}].tang = {t} (1–120)')
                for v in o.get('vuon') or []:
                    if not 1 <= int(v) <= t - 3:
                        bao.C(f'mo_hinh_3d.thap[{i + 1}].vuon {v} nằm ngoài thân tháp (1–{t - 3}) — bỏ qua')
            for k in ('rong', 'sau'):
                v = _f(o.get(k), 0)
                if v and not 3 <= v <= 400:
                    bao.L(f'mo_hinh_3d.{loai}[{i + 1}].{k} = {v} m (3–400)')
            if loai == 'de' and o.get('ho_boi'):
                B = o['ho_boi']
                if abs(_f(B.get('x'), 0)) + _f(B.get('rong'), 0) / 2 > _f(o.get('rong'), 0) / 2 + .1 or \
                   abs(_f(B.get('z'), 0)) + _f(B.get('sau'), 0) / 2 > _f(o.get('sau'), 0) / 2 + .1:
                    bao.L(f'mo_hinh_3d.de[{i + 1}].ho_boi tràn ra ngoài mặt đế')
            if loai == 'khoi' and o.get('kieu', 'tuong') not in ('kinh', 'de', 'tuong'):
                bao.L(f"mo_hinh_3d.khoi[{i + 1}].kieu '{o.get('kieu')}' (kinh | de | tuong)")
    for i, o in enumerate(mh.get('mat_dat') or []):
        loai = (o or {}).get('loai')
        if loai not in ('ho', 'san_tt', 'san', 'duong', 'cau_tren_cao'):
            bao.L(f"mo_hinh_3d.mat_dat[{i + 1}].loai '{loai}' (ho | san_tt | san | duong | cau_tren_cao)"); continue
        if loai in ('duong', 'cau_tren_cao') and (not isinstance(o.get('diem'), list) or len(o['diem']) < 2):
            bao.L(f'mo_hinh_3d.mat_dat[{i + 1}] ({loai}) cần "diem": ≥ 2 điểm [x, z] (toạ độ mô hình)')
        if loai in ('ho', 'san_tt', 'san') and o.get('diem') is None and (_f(o.get('x')) is None or _f(o.get('z')) is None):
            bao.L(f'mo_hinh_3d.mat_dat[{i + 1}] ({loai}) cần x, z (+ rong, sau, xoay) hoặc "diem" đa giác')
    for i, V in enumerate(mh.get('san_vuon') or []):
        P = V.get('diem') if isinstance(V, dict) else None
        if not isinstance(P, list) or len(P) < 3 or any(not (isinstance(p, list) and len(p) >= 2 and _f(p[0]) is not None and _f(p[1]) is not None) for p in P):
            bao.L(f'mo_hinh_3d.san_vuon[{i + 1}].diem cần ≥ 3 điểm [x, z] (m, gốc vi_tri, x Đông z Nam — không xoay theo công trình)')
    if not n:
        bao.L('mo_hinh_3d chưa có tháp / khối đế / khối nào')
    return True


def ranh_diem(mh, spec):
    """đường cho duong_vien → [[x,z],…] toạ độ cảnh. "ranh" = mo_hinh_3d.ranh (ranh lô) hoặc san_vuon 1;
    "san_vuon<k>" / "mat_dat<k>" = đa giác / tuyến đó (mat_dat theo toạ độ mô hình, đã xoay về cảnh); [[x,z],…] dùng thẳng."""
    import math
    def sach(P):
        try:
            P = [[float(p[0]), float(p[1])] for p in P]
        except (TypeError, ValueError, IndexError):
            return None
        return P if len(P) >= 2 else None
    if isinstance(spec, list):
        return sach(spec)
    if not isinstance(spec, str):
        return None
    m = re.fullmatch(r'\s*(ranh|san_vuon|mat_dat)(\d*)\s*', spec)
    if not m:
        return None
    loai, k = m.group(1), int(m.group(2) or 1) - 1
    if loai == 'ranh':
        if mh.get('ranh'):
            return sach(mh['ranh'])
        loai, k = 'san_vuon', 0
    ds = mh.get(loai) or []
    if not 0 <= k < len(ds) or not isinstance(ds[k], dict):
        return None
    P = sach(ds[k].get('diem') or [])
    if P and loai == 'mat_dat':                       # toạ độ mô hình (G0 xoay -xoay, dời x/z) → cảnh
        a = -(_f(mh.get('xoay'), 0) or 0) * math.pi / 180
        ox, oz = _f(mh.get('x'), 0) or 0, _f(mh.get('z'), 0) or 0
        P = [[round(ox + x * math.cos(a) + z * math.sin(a), 2), round(oz - x * math.sin(a) + z * math.cos(a), 2)] for x, z in P]
    return P


def kiem_canh(kh, cid, t0, t1, bao):
    """kiểm 1 cảnh 3D cho đoạn [t0, t1] (giây tuyệt đối) mà nó được dùng làm footage."""
    c3 = (kh.get('canh_3d') or {}).get(cid)
    if not isinstance(c3, dict):
        bao.L(f"không có canh_3d['{cid}'] (có: {', '.join(kh.get('canh_3d') or {}) or 'không'})"); return
    cam = c3.get('cam') or []
    if len(cam) < 2:
        bao.L(f'canh_3d.{cid}: cần ≥ 2 khoá camera'); return
    ls = [_f(k.get('luc')) for k in cam]
    if any(x is None for x in ls) or ls != sorted(ls) or len(set(ls)) != len(ls):
        bao.L(f'canh_3d.{cid}: mọi khoá camera cần "luc" (giây tuyệt đối) tăng dần, không trùng')
    else:
        if ls[0] > t0 + .05 or ls[-1] < t1 - .05:
            bao.C(f'canh_3d.{cid}: camera chỉ có khoá {ls[0]}–{ls[-1]} s nhưng cảnh dùng {t0:.2f}–{t1:.2f} s — ngoài khoảng camera đứng yên')
        for a, b in zip(ls, ls[1:]):
            if b - a < .6:
                bao.C(f'canh_3d.{cid}: 2 khoá camera cách {b - a:.2f} s — bay giật')
    for i, k in enumerate(cam):
        for ten, lo, hi in (('goc', -3600, 3600), ('nghieng', 3, 89.5), ('xa', 30, 30000), ('fov', 15, 90)):
            v = _f(k.get(ten), 55 if ten == 'fov' else None)
            if v is None or not lo <= v <= hi:
                bao.L(f'canh_3d.{cid}.cam[{i + 1}].{ten} = {k.get(ten)} ({lo}–{hi})')
        nh = k.get('nhin', [0, 40, 0])
        if not (isinstance(nh, list) and len(nh) == 3):
            bao.L(f'canh_3d.{cid}.cam[{i + 1}].nhin cần [x,y,z]')
    for ten in ('chu_thich', 'vong', 'dia_danh', 'tia', 'chu', 'duong_vien'):
        for i, o in enumerate(c3.get(ten) or []):
            a, b = _f(o.get('tu')), _f(o.get('den'))
            if a is None or b is None or b <= a:
                bao.L(f'canh_3d.{cid}.{ten}[{i + 1}]: tu/den sai'); continue
            if b < t0 - .1 or a > t1 + .1:
                bao.C(f'canh_3d.{cid}.{ten}[{i + 1}] ({a}–{b} s) nằm ngoài đoạn cảnh dùng {t0:.2f}–{t1:.2f} s — không ai thấy')
    for i, o in enumerate(c3.get('chu_thich') or []):
        if not str(o.get('chu', '')).strip():
            bao.L(f'canh_3d.{cid}.chu_thich[{i + 1}] thiếu chu')
        if o.get('ben', 'trai') not in ('trai', 'phai'):
            bao.L(f'canh_3d.{cid}.chu_thich[{i + 1}].ben = trai | phai')
    for i, o in enumerate(c3.get('duong_vien') or []):
        if ranh_diem(kh.get('mo_hinh_3d') or {}, o.get('diem', 'ranh')) is None:
            bao.L(f"canh_3d.{cid}.duong_vien[{i + 1}].diem = {str(o.get('diem', 'ranh'))[:60]} — cần \"ranh\" (mo_hinh_3d.ranh hoặc san_vuon 1), \"san_vuon<k>\", \"mat_dat<k>\" hoặc [[x,z],…] ≥ 2 điểm (toạ độ cảnh)")
    for i, o in enumerate(c3.get('dia_danh') or []):
        if o.get('diem') is None and (_f(o.get('lat')) is None or _f(o.get('lon')) is None):
            bao.L(f'canh_3d.{cid}.dia_danh[{i + 1}] cần lat/lon (hoặc diem [x,y,z])')


def so_trong_loi(kh, tu, bao):
    """số in trên cảnh 3D (chú thích, logo, chữ trong) phải có trong lời — không thì là ĐOÁN, ghi vào doan."""
    loi_so = set(re.findall(r'\d+', ''.join(w['w'] for w in tu).replace('.', '').replace(',', '')))
    doan = ' '.join(kh.get('doan') or [])
    for cid, c3 in (kh.get('canh_3d') or {}).items():
        chu = [str(o.get('chu', '')) + ' ' + str(o.get('phu', '')) for o in c3.get('chu_thich') or []]
        lg = c3.get('logo') or {}
        chu.append(str(lg.get('chu', '')) + ' ' + str(lg.get('phu', '')))
        for g in c3.get('chu') or []:
            chu += [str(ch.get('t', '')) for d in g.get('dong') or [] for ch in d]
        for s in chu:
            for so in re.findall(r'\d[\d.,]*', s):
                k = so.replace('.', '').replace(',', '')
                if k and k not in loi_so and so not in doan:
                    bao.C(f"canh_3d.{cid}: số '{so}' ('{s.strip()}') không có trong lời — chỉ giữ nếu người dùng đưa, ghi vào doan")


# ---------------- lập trang 3D ----------------
def lap(kh, cid, tu, work, bao, co_nen=True):
    """→ (M3 cho bds3d_3d.js, KH3 cho bds3d.js — chỉ chữ 2 tầng bên trong cảnh 3D)."""
    import ke_hoach as KHM
    mh, c3 = kh['mo_hinh_3d'], kh['canh_3d'][cid]
    vt = mh.get('vi_tri') or {}
    lat, lon = _f(vt.get('lat'), 0), _f(vt.get('lon'), 0)
    nen = ve_tinh.chuan_bi(lat, lon, Path(work) / 've_tinh', bao=loi) if co_nen else []
    r, hmax = pham_vi(mh)
    ct = {k: mh[k] for k in ('xoay', 'thap', 'de', 'khoi', 'khu', 'cay_quanh', 'mau', 'seed', 'x', 'z', 'san_vuon', 'mat_dat') if k in mh}
    if any(t.get('anh_mat') or t.get('anh_hoi') for t in ct.get('thap') or []):     # mặt đứng / tường hồi ảnh thật → url texture
        def _u(t):
            t = dict(t)
            for k in ('anh_mat', 'anh_hoi'):
                if t.get(k) and anh_mat_file(work, t[k]).exists():
                    f_ = anh_mat_file(work, t[k])          # ?v=<md5 nội dung>: cắt lại ảnh → HTML đổi → khung cache dựng lại
                    t[k + '_url'] = url(f_) + '?v=' + hashlib.md5(f_.read_bytes()).hexdigest()[:8]
            return t
        ct['thap'] = [_u(t) for t in ct['thap']]
    ct.setdefault('khu', {'rong': round(2 * r + 20), 'sau': round(2 * r + 20)})
    M3 = {
        'nen': [{'url': url(x['file']), 'nua_m': x['nua_m']} for x in nen],
        'ct': ct, 'bong_r': round(min(700, max(140, r + hmax * .95))),
        'cam': [{'t': _f(k['luc']), 'nhin': [_f(v, 0) for v in (k.get('nhin') or [0, 40, 0])], 'goc': _f(k.get('goc'), 0),
                 'nghieng': _f(k.get('nghieng'), 30), 'xa': _f(k.get('xa'), 500), 'fov': _f(k.get('fov'), 55)} for k in c3.get('cam') or []],
        'vong': [{'tu': _f(v['tu']), 'den': _f(v['den']), 'x': _f(v.get('x'), 0), 'z': _f(v.get('z'), 0), 'r': _f(v.get('r'), round(r * 1.5)),
                  **({'mau': v['mau']} if v.get('mau') else {})} for v in c3.get('vong') or []],
        'chu_thich': [{'tu': _f(o['tu']), 'den': _f(o['den']), 'diem': diem(o.get('diem', 'thap1'), mh, bao, f'canh_3d.{cid}.chu_thich'),
                       'chu': o.get('chu', ''), 'phu': o.get('phu', ''), 'ben': o.get('ben', 'trai'), **({'dai': o['dai']} if o.get('dai') else {})}
                      for o in c3.get('chu_thich') or []],
        'dia_danh': [], 'tia': [{'tu': _f(o['tu']), 'den': _f(o['den'])} for o in c3.get('tia') or []],
        'duong_vien': [dict({k: o[k] for k in ('mau', 'rong', 'cao', 've', 'chay', 'buoc', 'kin') if o.get(k) is not None},
                            tu=_f(o['tu']), den=_f(o['den']), diem=ranh_diem(mh, o.get('diem', 'ranh')))
                       for o in c3.get('duong_vien') or [] if ranh_diem(mh, o.get('diem', 'ranh'))],
    }
    for k in ('nang', 'troi', 'loc', 'mau_dat', 'buoi', 'hau_ky', 'ssaa'):
        if mh.get(k) is not None:
            M3[k] = mh[k]
    for o in c3.get('dia_danh') or []:
        if o.get('diem') is not None:
            p = diem(o['diem'], mh, bao, f'canh_3d.{cid}.dia_danh')
        else:
            x, z = ve_tinh.ll_sang_m(lat, lon, _f(o['lat']), _f(o['lon'])); p = [round(x, 1), _f(o.get('cao'), 0), round(z, 1)]
        M3['dia_danh'].append({'tu': _f(o['tu']), 'den': _f(o['den']), 'chu': o.get('chu', ''), 'diem': p})
    lg = c3.get('logo')
    if lg:
        L = {'tu': _f(lg.get('tu'), 0), 'den': _f(lg.get('den'), 3), 'diem': diem(lg.get('diem') or [0, round(hmax * 1.12), 0], mh, bao, f'canh_3d.{cid}.logo'),
             'chu': lg.get('chu', ''), 'phu': lg.get('phu', '')}
        if lg.get('file'):
            if Path(lg['file']).exists():
                L['url'] = url(lg['file'])
            else:
                bao.L(f"canh_3d.{cid}.logo: không thấy file {lg['file']}")
        M3['logo'] = L
    chu = []
    for g in c3.get('chu') or []:
        g = dict(g); g.setdefault('vi_tri', CAP3D_TOP); chu.append(g)
    caps = KHM._giai_chu(chu, tu, [], 1e4, bao)
    KH3 = {'fps': FPS, 'dur': 1e4, 'shots': [], 'scenes': [{'id': '3d', 'loai': 'nen_toi', 'tu': 0, 'den': 1e4, 'mode': 'none', 'shot': None}],
           'caps': caps, 'pills': [], 'tiles': []}
    return M3, KH3


def trang(work, M3, KH3, ten):
    import json
    js = lambda o: json.dumps(o, ensure_ascii=False).replace('</', '<\\/')
    p = Path(work) / ten
    p.write_text(f'''<!doctype html><html><head><meta charset="utf-8"><link rel="stylesheet" href="{url(KHUNG / 'bds3d.css')}"></head>
<body><div id="stage"></div><script>window.KH={js(KH3)};window.M3={js(M3)};</script>
<script src="{url(KHUNG / 'lib' / 'three.min.js')}"></script><script src="{url(KHUNG / 'bds3d.js')}"></script><script src="{url(KHUNG / 'bds3d_3d.js')}"></script></body></html>''',
                 encoding='utf-8')
    return p


def _render(args_):
    return run([node(), SCRIPTS / 'render.mjs'] + [str(x) for x in args_])


def _khoa_may():
    h = hashlib.md5()
    for f in ('bds3d.js', 'bds3d_3d.js', 'bds3d.css'):
        h.update((KHUNG / f).read_bytes())
    return h.hexdigest()[:8]


def khung(kh, cid, t0, t1, tu, work, bao, trich, luong=3):
    """dựng chuỗi ảnh 30 fps cho đoạn [t0-0.1, t1+0.45] → {'dir','ext0','n'} như _trich_khung (có cache)."""
    ext0 = t0 - .1
    n = max(1, round((t1 + .45 - ext0) * FPS))
    out = Path(work) / 'khung' / f'3d_{cid}_{t0:.2f}'
    if trich:
        M3, KH3 = lap(kh, cid, tu, work, bao)
        hp = trang(work, M3, KH3, f'_3d_{cid}.html')
        key = hashlib.md5(f'{hp.read_text(encoding="utf-8")}|{ext0:.4f}|{n}|{_khoa_may()}'.encode()).hexdigest()[:12]
        if not (out / f'xong_{key}').exists():
            shutil.rmtree(out, ignore_errors=True); out.mkdir(parents=True)
            loi(f'▶ dựng cảnh 3D "{cid}" {t0:.2f}–{t1:.2f} s ({n} khung)…')
            _render(['--html', hp, '--khung', out, '--tu', f'{ext0:.4f}', '--n', n, '--fps', FPS, '--luong', luong])
            (out / f'xong_{key}').write_text('ok')
    return {'dir': url(out, True), 'ext0': round(ext0, 4), 'n': n}


# ---------------- tự kiểm bố cục trong cảnh 3D ----------------
def kiem_bo_cuc(kh, dung, tu, work, bao):
    """dung: [(cid, t0, t1)]. Dựng trang 3D KHÔNG nền (nhanh), đo hộp chú thích / logo / địa danh / chữ trong ở giữa lúc hiện."""
    for cid, t0, t1 in dung:
        c3 = kh['canh_3d'][cid]
        ts = set()
        for ten in ('chu_thich', 'dia_danh'):
            for o in c3.get(ten) or []:
                a, b = max(_f(o['tu']), t0), min(_f(o['den']), t1)
                if b > a:
                    ts |= {round(a + .7 * (b - a), 2), round(min(b - .05, a + .6), 2)}
        lg = c3.get('logo')
        if lg:
            a, b = max(_f(lg.get('tu'), 0), t0), min(_f(lg.get('den'), 3), t1)
            if b > a:
                ts.add(round((a + b) / 2, 2))
        for g in c3.get('chu') or []:
            a, b = max(_f(g['tu']), t0), min(_f(g['den']), t1)
            if b > a:
                ts.add(round(b - .1, 2))
        if not ts:
            continue
        M3, KH3 = lap(kh, cid, tu, work, bao, co_nen=False)
        hp = trang(work, M3, KH3, f'_kiem_3d_{cid}.html')
        rp = Path(work) / f'_bo_cuc_3d_{cid}.json'
        _render(['--html', hp, '--report', rp, '--times', ','.join(f'{t:.2f}' for t in sorted(ts))])
        thay = {}
        da = set()
        for fr in doc_json(rp):
            hop = fr['hop']
            for h in hop:
                thay.setdefault((h['loai'], h['chu']), []).append(fr['t'])
                if h['x0'] < 24 or h['x1'] > W - 24 or h['y0'] < 30 or h['y1'] > H - 40:
                    k = ('le', h['chu'])
                    if k not in da:
                        da.add(k); bao.L(f"canh_3d.{cid} {fr['t']:.2f}s: '{h['chu']}' ({h['loai']}) ra ngoài khung ({h['x0']},{h['y0']})–({h['x1']},{h['y1']}) → đổi camera / ben / diem")
            for i in range(len(hop)):
                for j in range(i + 1, len(hop)):
                    a, b = hop[i], hop[j]
                    ar = max(0, min(a['x1'], b['x1']) - max(a['x0'], b['x0'])) * max(0, min(a['y1'], b['y1']) - max(a['y0'], b['y0']))
                    if ar > 400 and not (a['loai'] == b['loai'] == 'chu'):
                        k = ('de', a['chu'], b['chu'])
                        if k not in da:
                            da.add(k); bao.L(f"canh_3d.{cid} {fr['t']:.2f}s: '{a['chu']}' đè '{b['chu']}' ({ar} px²) → đổi ben / diem / camera / thời gian")
        for o in c3.get('chu_thich') or []:
            a, b = max(_f(o['tu']), t0), min(_f(o['den']), t1)
            if b > a and ('chu_thich_3d', o.get('chu', '')) not in thay:
                bao.L(f"canh_3d.{cid}: chú thích '{o.get('chu')}' không hiện trong khung lúc {a:.2f}–{b:.2f} s (điểm sau lưng camera / ngoài khung)")
        for o in c3.get('dia_danh') or []:
            a, b = max(_f(o['tu']), t0), min(_f(o['den']), t1)
            if b > a and not any(k[0] == 'dia_danh_3d' and k[1].lower() == str(o.get('chu', '')).lower() for k in thay):
                bao.L(f"canh_3d.{cid}: địa danh '{o.get('chu')}' không nằm trong khung lúc {a:.2f}–{b:.2f} s → quay camera về phía nó (goc) hoặc bỏ")


# ---------------- ảnh xem mô hình (so với ảnh phối cảnh) ----------------
def xem(kh, tu, work, bao):
    """4 góc nhìn mô hình (không chữ) → work/_xem_3d/k_*.jpg để Claude so với ảnh dự án."""
    mh = kh['mo_hinh_3d']
    r, hm = pham_vi(mh)
    xa = max(260, 2.3 * max(hm, r))
    kh2 = dict(kh)
    kh2['canh_3d'] = {'_xem': {'cam': [
        {'luc': 0, 'nhin': [0, hm * .45, 0], 'goc': 25, 'nghieng': 18, 'xa': xa, 'fov': 45},
        {'luc': 1, 'nhin': [0, hm * .45, 0], 'goc': 115, 'nghieng': 18, 'xa': xa, 'fov': 45},
        {'luc': 2, 'nhin': [0, hm * .45, 0], 'goc': 205, 'nghieng': 18, 'xa': xa, 'fov': 45},
        {'luc': 3, 'nhin': [0, hm * .45, 0], 'goc': 295, 'nghieng': 18, 'xa': xa, 'fov': 45},
        {'luc': 4, 'nhin': [0, 0, 0], 'goc': 0, 'nghieng': 89, 'xa': xa * 1.2, 'fov': 45},
        {'luc': 5, 'nhin': [0, hm * .35, 0], 'goc': 40, 'nghieng': 42, 'xa': xa * 1.15, 'fov': 45},
    ]}}
    # góc GIỐNG ẢNH: mo_hinh_3d.goc_anh = [{anh: số thứ tự ảnh dự án (1…), goc, nghieng, xa, fov, nhin}] — Claude ước camera
    # của từng ảnh phối cảnh → dựng mô hình đúng góc đó, đặt CẠNH ảnh để so mặt đứng / màu / tỉ lệ (không so lệch góc)
    ga = [g for g in (mh.get('goc_anh') or []) if isinstance(g, dict)]
    for j, g in enumerate(ga):
        kh2['canh_3d']['_xem']['cam'].append({'luc': 6 + j, 'nhin': g.get('nhin') or [0, hm * .4, 0], 'goc': _f(g.get('goc'), 25),
                                              'nghieng': _f(g.get('nghieng'), 30), 'xa': _f(g.get('xa'), xa), 'fov': _f(g.get('fov'), 40)})
    M3, KH3 = lap(kh2, '_xem', tu, work, bao)
    # khoá đứng: mỗi giây 1 góc (bỏ nội suy giữa)
    M3['cam'] = [dict(k, t=k['t'] + d) for k in M3['cam'] for d in (0, .9)]
    hp = trang(work, M3, KH3, '_xem_3d.html')
    od = Path(work) / '_xem_3d'
    shutil.rmtree(od, ignore_errors=True)
    ts = [.5, 1.5, 2.5, 3.5, 4.5, 5.5] + [6.5 + j for j in range(len(ga))]
    _render(['--html', hp, '--anh', od, '--times', ','.join(f'{t:.2f}' for t in ts)])
    nhan = ['góc 25° (Nam-Đông Nam)', 'góc 115° (Đông)', 'góc 205° (Bắc)', 'góc 295° (Tây)', 'nhìn thẳng xuống (Bắc ở trên)', 'chéo cao 42°']
    nhan += [f"MÔ HÌNH cùng góc ảnh {g.get('anh', j + 1)}" for j, g in enumerate(ga)]
    return [(od / f'k_{t:.2f}.jpg', n) for t, n in zip(ts, nhan)]


# ---------------- bay thử: mô hình trong video, chưa cần giọng ----------------
def bay_thu(kh, work, bao, out, giay=12.0, luong=3):
    """camera hạ từ cao xuống rồi bay vòng quanh mô hình → mp4 câm (xem trước cho người dùng / khách).
    Có canh_3d['bay_thu'] trong kế hoạch thì dùng camera đó, không thì tự đặt."""
    mh = kh['mo_hinh_3d']
    r, hm = pham_vi(mh)
    R = max(hm, r)
    c3 = (kh.get('canh_3d') or {}).get('bay_thu')
    if c3:
        giay = max(_f(k.get('luc'), 0) for k in c3.get('cam') or [{'luc': giay}])
    else:
        c3 = {'cam': [
            {'luc': 0, 'nhin': [0, round(hm * .3), 0], 'goc': -25, 'nghieng': 58, 'xa': round(R * 4.4), 'fov': 55},
            {'luc': round(giay * .35, 2), 'nhin': [0, round(hm * .42), 0], 'goc': 8, 'nghieng': 36, 'xa': round(R * 3.1), 'fov': 55},
            {'luc': round(giay * .7, 2), 'nhin': [0, round(hm * .5), 0], 'goc': 42, 'nghieng': 22, 'xa': round(R * 2.5), 'fov': 55},
            {'luc': round(giay, 2), 'nhin': [0, round(hm * .5), 0], 'goc': 75, 'nghieng': 17, 'xa': round(R * 2.35), 'fov': 55},
        ], 'tia': [{'tu': round(giay * .45, 2), 'den': round(giay + 1, 2)}] if mh.get('buoi', 'ngay') in ('ngay', 'hoang_hon') else []}
        if ranh_diem(mh, 'ranh'):           # đường line sáng chạy quanh khu (mẫu: viền vàng bám mép khu / đế)
            c3['duong_vien'] = [{'tu': round(giay * .12, 2), 'den': round(giay + 1, 2), 'diem': 'ranh', 've': 2.6}]
        c3['vong'] = [{'tu': round(giay * .05, 2), 'den': round(giay * .5, 2), 'r': round(r * 1.25)}]
    kh2 = dict(kh)
    kh2['canh_3d'] = {'_bay_thu': c3}
    kiem_canh(kh2, '_bay_thu', 0, giay, bao)
    if bao.loi:
        return None
    k = khung(kh2, '_bay_thu', 0, giay, [], work, bao, True, luong)
    d = Path(work) / 'khung' / f'3d__bay_thu_{0:.2f}'
    run(['ffmpeg', '-v', 'error', '-y', '-framerate', FPS, '-i', d / '%05d.jpg', '-ss', '0.1', '-t', f'{giay:.2f}',
         '-c:v', 'libx264', '-crf', '17', '-preset', 'medium', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', out])
    return out


# ---------------- tìm toạ độ ----------------
def tim(q, n=8):
    import requests
    r = requests.get('https://nominatim.openstreetmap.org/search', params={'q': q, 'format': 'jsonv2', 'limit': n, 'countrycodes': 'vn', 'accept-language': 'vi'},
                     headers=ve_tinh.UA, timeout=30)
    r.raise_for_status()
    return [{'ten': x.get('display_name', ''), 'lat': float(x['lat']), 'lon': float(x['lon']), 'osm': f"{x.get('osm_type', '')[:1].upper()}{x.get('osm_id', '')}",
             'loai': f"{x.get('category', '')}/{x.get('type', '')}"} for x in r.json()]
