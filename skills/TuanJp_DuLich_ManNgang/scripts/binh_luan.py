# -*- coding: utf-8 -*-
"""binh_luan.py — BÌNH LUẬN ẢO tiếng Anh / tiếng Hàn (khen + chê nhẹ) cho từng điểm đến / món ăn (khách 14/11/2026).
Câu lấy từ assets/binh_luan.json theo LOẠI cảnh (núi, vịnh, thác, sông nước, biển, chùa, thành phố, ẩm thực…), chọn tất định theo id
→ dựng lại ra đúng y như bản duyệt. Tên người dùng là tên tự đặt (không phải người thật)."""
import hashlib
import re
from functools import lru_cache

from chung import ASSETS, BINH_LUAN_CACH, BINH_LUAN_NN, bo_dau, doc_json


@lru_cache(1)
def kho():
    return doc_json(ASSETS / 'binh_luan.json')


def _h(*xs):
    return int(hashlib.md5('|'.join(map(str, xs)).encode('utf-8')).hexdigest()[:8], 16)


def _khong_dau(s):
    return re.sub(r'\s+', ' ', re.sub(r'[^a-z0-9 ]+', ' ', bo_dau(str(s)).lower())).strip()


def loai_canh(*chu):
    """đoán loại cảnh từ tên / mô tả (không dấu) → khoá trong kho['loai']. Xét TỪNG chữ theo thứ tự (tên trước, mô tả sau):
    "Ninh Bình" + phụ "Hạ Long trên cạn" → sông nước (theo tên), không phải vịnh."""
    tk = kho()['tu_khoa_loai']
    for c in chu:
        if not c:
            continue
        s = ' ' + _khong_dau(c) + ' '
        for loai in ('cap_treo', 'thac', 'vinh', 'song_nuoc', 'am_thuc', 'nui', 'bien', 'chua', 'thanh_pho'):
            if any(f' {k} ' in s for k in tk.get(loai, [])):
                return loai
    return 'chung'


def ten_theo_tieng(ten, nn):
    """tên địa danh theo tiếng của bình luận ('Thác Bản Giốc' → 'Ban Gioc Falls' / '반지옥 폭포'); không có trong bảng → None."""
    bang = kho()['ten']
    s = _khong_dau(ten)
    if s in bang:
        return bang[s].get(nn)
    for k in sorted(bang, key=len, reverse=True):
        if re.search(rf'(^| ){re.escape(k)}( |$)', s):
            return bang[k].get(nn)
    return None


def _so_thich(x, nn):
    if x < 1000:
        return str(x)
    v = f'{x / 1000:.1f}'.rstrip('0').rstrip('.')
    return v + ('천' if nn == 'ko' else 'K')


def tao(seed, ten, loai=None, so=3, nn_ds=BINH_LUAN_NN, tu=0.0, cach=BINH_LUAN_CACH, da_dung=None):
    """→ danh sách mục bình luận [{nn, ten, co, tg, chu, thich, tra_loi, luc}] — 2 khen + 1 chê nhẹ (xen tiếng)."""
    K = kho()
    loai = loai or loai_canh(ten)
    L = K['loai'].get(loai) or K['loai']['chung']
    h = _h(seed, ten)
    nn_ds = [n for n in nn_ds if n in L] or ['en']
    thu_tu = nn_ds if h % 2 == 0 or len(nn_ds) < 2 else list(reversed(nn_ds))
    kieu = [(thu_tu[0], 'khen'), (thu_tu[1 % len(thu_tu)], 'khen'), (thu_tu[(h // 3) % len(thu_tu)], 'che')][:so]
    while len(kieu) < so:
        kieu.append((thu_tu[len(kieu) % len(thu_tu)], 'khen'))
    da_dung = da_dung if da_dung is not None else set()
    out = []
    for k, (nn, kc) in enumerate(kieu):
        tn = ten_theo_tieng(ten, nn) if ten else None
        cau = [c for c in L[nn][kc] if tn or '{ten}' not in c]
        if not cau:
            cau = [c for c in K['loai']['chung'][nn][kc] if tn or '{ten}' not in c]
        moi = [c for c in cau if c not in da_dung] or cau
        chu = moi[_h(seed, ten, k, kc) % len(moi)]
        da_dung.add(chu)
        ng = K['nguoi'][nn]
        ten_ng, co = ng[(_h(seed, ten, 'ng', k) + k * 3) % len(ng)]
        for _ in range(len(ng)):           # không trùng người trong đợt; cả video: dùng hết người mới lặp lại
            if not any(x['ten'] == ten_ng for x in out) and ('@@' + ten_ng not in da_dung or all('@@' + n in da_dung for n, _c in ng)):
                break
            ten_ng, co = ng[(ng.index([ten_ng, co]) + 1) % len(ng)]
        da_dung.add('@@' + ten_ng)
        out.append({'nn': nn, 'ten': ten_ng, 'co': co, 'tg': K['tg'][nn][_h(seed, ten, 'tg', k) % len(K['tg'][nn])],
                    'chu': chu.replace('{ten}', tn or ''), 'thich': _so_thich(K['thich'][_h(seed, ten, 'th', k) % len(K['thich'])], nn),
                    'tra_loi': K['tra_loi'][nn], 'luc': round(tu + k * cach, 2)})
    return out


def dien(m, seed, ten, loai, k, tu, da_dung):
    """mục bình luận Claude viết thiếu chữ / tên → điền từ kho (giữ chữ Claude viết nếu có)."""
    K = kho()
    nn = m.get('nn') or BINH_LUAN_NN[k % len(BINH_LUAN_NN)]
    goc = tao(f'{seed}_{k}', ten, loai, 1, (nn,), tu, da_dung=da_dung)[0]
    if m.get('khen') is False and not m.get('chu'):
        L = K['loai'].get(loai or loai_canh(ten)) or K['loai']['chung']
        tn = ten_theo_tieng(ten, nn) if ten else None
        cau = [c for c in L[nn]['che'] if tn or '{ten}' not in c] or L[nn]['che']
        goc['chu'] = cau[_h(seed, k, 'che') % len(cau)].replace('{ten}', tn or '')
    out = dict(goc)
    out.update({kk: v for kk, v in m.items() if v not in (None, '')})
    out.setdefault('luc', round(tu + k * BINH_LUAN_CACH, 2))
    return out
