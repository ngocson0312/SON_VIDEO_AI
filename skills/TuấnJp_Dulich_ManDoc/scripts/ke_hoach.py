# -*- coding: utf-8 -*-
"""ke_hoach.py — đọc ke_hoach.json, kiểm (⛔ / ⚠), giải giờ → KH cho trang dựng + danh sách SFX."""
import math
import re
import unicodedata
from pathlib import Path

from chung import (AN_TOAN, CHUYEN, DUOI, FPS, H, KHONG_CACH, NEN_HT, NEN_PT, NGON_NGU, PHUONG_TIEN, SFX, SUB_MAX_KY_TU, SUB_MAX_TU,
                   SUB_NGAT, SUB_Y, W, cau_di_chuyen, doc_json, giong_nhau, kiem_ngon_ngu, loi, nhan_ht)

LOAI = ('mo_dau', 'tu_khoa', 'chuong', 'tieu_de', 'ghim', 'chip', 'so_lon', 'the_anh', 'liet_ke', 'trich', 'hanh_trinh')
NHO = ('ghim', 'chip')                      # đồ hoạ nhỏ, được chồng thời gian với 1 đồ hoạ lớn
CHUYEN_DONG = ('zoom_vao', 'zoom_ra', 'lia_trai', 'lia_phai', 'lia_len', 'lia_xuong', 'dung')
TRUONG_CHU = {
    'mo_dau': ('tren', 'chinh', 'viet_tay', 'duoi'), 'chuong': ('nhan', 'ten', 'phu'), 'tieu_de': ('dan', 'khoa', 'viet_tay'),
    'ghim': ('ten', 'phu'), 'so_lon': ('tien_to', 'hau_to', 'nhan'), 'the_anh': ('chu_thich',), 'liet_ke': ('dan', 'tieu'),
    'trich': ('noi',), 'hanh_trinh': ('dan', 'thoi_gian', 'nhan_tg', 'khoang_cach', 'nhan_pt'),
}
BAT_BUOC = {'mo_dau': ('chinh',), 'tu_khoa': ('muc',), 'chuong': ('ten',), 'tieu_de': ('khoa',), 'ghim': ('ten',), 'chip': ('muc',),
            'so_lon': ('so',), 'the_anh': ('anh',), 'liet_ke': ('muc',), 'trich': ('noi',),
            'hanh_trinh': ('xuat_phat', 'diem_den')}
ICON_HOP_LE = {'ghim', 'dong_ho', 'lich_su', 'sao', 'may_anh', 'bat_pho', 'ca_phe', 'chua', 'ho', 'thanh_pho', 'la', 'trang', 'mat_troi',
               've', 'ban_do', 'di_bo', 'may_bay', 'tich', 'cong', 'sach', 'vuong_mien', 'co', 'di_tich', 'cay', 'tim', 'binh_luan',
               'chia_se', 'luu', 'chuong', 'nhac', 'lap_lanh', 'cau', 'den_long', 'xe_may', 'nguoi', 'tau', 'nui', 'qua_tang',
               'ca', 'cuon', 'lua', 'hoa', 'gio',
               # chủ đề du lịch đa dạng (biển, núi, mùa, phương tiện, lưu trú, ẩm thực, chi phí)
               'bien', 'dao', 'thac', 'song_nuoc', 'suoi_nong', 'hang', 'ruong', 'leu', 'khach_san', 'nha', 'lau_dai', 'cho', 'an_uong', 'do_uong', 'gia', 'tien', 'tuyet', 'may', 'mua', 'nhiet_do', 'o_to', 'xe_dap', 'tau_hoa', 'xe_buyt', 'cap_treo', 'balo', 'vali', 'la_ban', 'ong_nhom', 'phao_hoa', 'non_la'}


# ---------------- sửa lỗi nhận lời ----------------
def _chuan(w):
    return re.sub(r'[^\w]+', '', unicodedata.normalize('NFC', w).lower())


def sua_tu(tu, bang):
    """bang: {"xôi động": "sôi động", "cầu thê hút": "cầu Thê Húc"} — khớp chuỗi từ liên tiếp (bỏ dấu câu, không phân biệt hoa thường),
    thay chữ, giữ dấu câu cuối của từ cuối. Trả (từ mới, [cụm không tìm thấy])."""
    tu = [dict(w) for w in tu]
    khong_thay = []
    for sai, dung in (bang or {}).items():
        a = [_chuan(x) for x in sai.split()]
        b = dung.split()
        n, thay = len(a), 0
        i = 0
        while i + n <= len(tu):
            if [_chuan(tu[i + k]['w']) for k in range(n)] == a:
                duoi = re.search(r'[^\w]+$', tu[i + n - 1]['w'])
                duoi = duoi.group(0) if duoi else ''
                dau = re.match(r'^[^\w]+', tu[i]['w'])
                dau = dau.group(0) if dau else ''
                s0, e0 = tu[i]['s'], tu[i + n - 1]['e']
                if len(b) == n:
                    for k in range(n):
                        tu[i + k]['w'] = b[k]
                else:                                   # khác số từ → chia đều thời gian
                    moi = []
                    for k, x in enumerate(b):
                        moi.append({'w': x, 's': round(s0 + (e0 - s0) * k / len(b), 2), 'e': round(s0 + (e0 - s0) * (k + 1) / len(b), 2)})
                    tu[i:i + n] = moi
                    n2 = len(b)
                    tu[i + n2 - 1]['w'] += duoi
                    tu[i]['w'] = dau + tu[i]['w']
                    i += n2
                    thay += 1
                    continue
                tu[i + n - 1]['w'] += duoi
                tu[i]['w'] = dau + tu[i]['w']
                thay += 1
                i += n
            else:
                i += 1
        if not thay:
            khong_thay.append(sai)
    return tu, khong_thay


# ---------------- gom sub ----------------
def _do_dai(ws):
    return sum(len(w['w']) for w in ws) + (0 if KHONG_CACH_NN[0] else max(0, len(ws) - 1))


KHONG_CACH_NN = [False]


_TU_GHEP = {}
# hư từ: ngắt NGAY SAU chúng thì dòng / cụm cụt ("một / vẻ đẹp", "những / ngôi nhà") → phạt
TU_DAN = {
    'vi': {'một', 'những', 'các', 'của', 'và', 'với', 'là', 'có', 'được', 'cho', 'để', 'mà', 'thì', 'hay', 'hoặc', 'rất', 'trong',
           'ở', 'tại', 'từ', 'đến', 'vào', 'ra', 'lên', 'xuống', 'khi', 'nơi', 'này', 'bạn', 'hãy', 'đừng', 'sẽ', 'đã', 'đang', 'cũng',
           'vẫn', 'còn', 'nhiều', 'mọi', 'mỗi', 'từng', 'bao', 'nét', 'con', 'ngôi', 'chiếc', 'bát', 'món', 'cái', 'người', 'nhất'},
    'en': {'the', 'a', 'an', 'of', 'and', 'to', 'in', 'on', 'with', 'for', 'at', 'by', 'from', 'my', 'your', 'our', 'their', 'his',
           'her', 'its', 'this', 'that', 'these', 'those', 'is', 'are', 'was', 'be', 'will', 'can', 'very', 'most', 'more'},
    'fr': {'le', 'la', 'les', 'un', 'une', 'des', 'de', 'du', 'et', 'à', 'au', 'aux', 'en', 'dans', 'sur', 'pour', 'avec', 'par'},
    'de': {'der', 'die', 'das', 'ein', 'eine', 'und', 'mit', 'von', 'zu', 'im', 'in', 'am', 'auf', 'für'},
    'es': {'el', 'la', 'los', 'las', 'un', 'una', 'de', 'del', 'y', 'en', 'con', 'por', 'para', 'a', 'al'},
}


# giới từ / liên từ / từ nối: ngắt NGAY TRƯỚC chúng là chỗ ngắt tự nhiên (luật phụ đề kinh điển) → thưởng
TU_TRUOC = {
    'vi': {'và', 'với', 'nhưng', 'mà', 'khi', 'nơi', 'để', 'thì', 'hay', 'hoặc', 'nếu', 'vì', 'bởi', 'rồi'},
    'en': {'and', 'but', 'or', 'with', 'of', 'for', 'to', 'in', 'at', 'on', 'from', 'where', 'when', 'which', 'who', 'that', 'as',
           'like', 'into', 'through', 'while', 'because', 'so', 'if', 'than', 'around', 'along', 'across', 'near', 'by'},
    'fr': {'et', 'mais', 'ou', 'avec', 'de', 'pour', 'dans', 'sur', 'où', 'quand', 'qui', 'que', 'comme', 'par', 'à'},
    'de': {'und', 'aber', 'oder', 'mit', 'von', 'für', 'in', 'auf', 'wo', 'wenn', 'die', 'der', 'das', 'als', 'wie', 'durch'},
    'es': {'y', 'pero', 'o', 'con', 'de', 'para', 'en', 'donde', 'cuando', 'que', 'como', 'por', 'a'},
    'it': {'e', 'ma', 'o', 'con', 'di', 'per', 'in', 'dove', 'quando', 'che', 'come', 'da', 'a'},
    'pt': {'e', 'mas', 'ou', 'com', 'de', 'para', 'em', 'onde', 'quando', 'que', 'como', 'por', 'a'},
    'id': {'dan', 'tetapi', 'atau', 'dengan', 'untuk', 'di', 'ke', 'dari', 'yang', 'saat', 'ketika', 'seperti'},
}


def tu_ghep(nn):
    """từ điển từ ghép (assets/tu_ghep_<nn>.txt) → tập chuỗi âm tiết chữ thường."""
    if nn not in _TU_GHEP:
        from chung import ASSETS
        f = ASSETS / f'tu_ghep_{nn}.txt'
        ds = set()
        if f.exists():
            for d in f.read_text(encoding='utf-8').splitlines():
                d = d.strip()
                if d and not d.startswith('#'):
                    ds.add(tuple(_chuan(x) for x in d.split()))
        _TU_GHEP[nn] = ds
    return _TU_GHEP[nn]


def _keo_dinh(tu, ghep):
    """dinh[i] = True nếu KHÔNG nên ngắt giữa tu[i] và tu[i+1] (cùng 1 từ ghép / tên riêng)."""
    n = len(tu)
    dinh = [False] * n
    c = [_chuan(w['w']) for w in tu]
    dai_max = max([len(g) for g in ghep] + [2])
    for i in range(n):
        for L in range(2, dai_max + 1):
            if i + L <= n and tuple(c[i:i + L]) in ghep:
                for k in range(i, i + L - 1):
                    dinh[k] = True
    hoa = lambda x: (re.sub(r'^[^\w]+', '', x)[:1] or 'a').isupper()
    for i in range(n - 1):            # tên riêng: 2 âm tiết viết hoa liền nhau, không cách bởi dấu câu
        if hoa(tu[i]['w']) and hoa(tu[i + 1]['w']) and not re.search(r'[.!?,;:…]$', tu[i]['w']):
            dinh[i] = True
    return dinh


def gom_sub(tu, nn, giu_lien=()):
    """Gom từ thành cụm sub (≤ 2 dòng) bằng quy hoạch động: ngắt ở dấu câu / chỗ ngừng, KHÔNG ngắt giữa từ ghép / tên riêng,
    dòng cân, cụm không quá ngắn / quá dài. giu_lien: các cụm chữ thêm cần giữ liền (chữ đồ hoạ, tên sửa lỗi)."""
    KHONG_CACH_NN[0] = nn in KHONG_CACH
    max_ky = SUB_MAX_KY_TU if not KHONG_CACH_NN[0] else 16
    max_tu = SUB_MAX_TU if not KHONG_CACH_NN[0] else 40
    n = len(tu)
    if not n:
        return []
    ghep = set(tu_ghep(nn)) if not KHONG_CACH_NN[0] else set()
    for g in giu_lien or ():
        k = tuple(_chuan(x) for x in str(g).split() if _chuan(x))
        if 2 <= len(k) <= 4:
            ghep.add(k)
    dinh = _keo_dinh(tu, ghep) if not KHONG_CACH_NN[0] else [False] * n
    dan = TU_DAN.get(nn, set())
    truoc = TU_TRUOC.get(nn, set())
    P_CAU = r'[,;:、，.!?…。！？]["”’»)]?$'

    def gia_ngat(i):                   # giá ngắt SAU từ i (giữa i và i+1); i = n-1 → 0
        if i >= n - 1:
            return 0.0
        w = tu[i]['w']
        g = tu[i + 1]['s'] - tu[i]['e']
        c = 10.0
        if re.search(r'[.!?…。！？]["”’»)]?$', w):
            c -= 11
        elif re.search(r'[,;:、，–—-]["”’»)]?$', w):
            c -= 7
        c -= min(7.0, max(0.0, g) * 16)
        if dinh[i]:
            c += 40
        elif _chuan(w) in dan and not re.search(r'[^\w]$', w):
            c += 12
        if not re.search(r'[^\w]$', w):            # ngắt giữa vế (không có dấu câu)
            if _chuan(tu[i + 1]['w']) in truoc:      # ngắt TRƯỚC giới từ / liên từ = chỗ ngắt tự nhiên
                c -= 4
            if re.search(P_CAU, tu[i + 1]['w']):      # đầu cụt: vế sắp hết ngay sau chỗ ngắt ("old / quarter,")
                c += 7
            elif i + 2 < n and re.search(P_CAU, tu[i + 2]['w']):
                c += 3
            if i >= 1 and re.search(P_CAU, tu[i - 1]['w']):   # đuôi cụt: vừa qua dấu câu 1 chữ đã ngắt ("pho, grilled /")
                c += 7
            elif i >= 2 and re.search(P_CAU, tu[i - 2]['w']):
                c += 3
        return c

    def chia_dong(a, b):               # chia tu[a:b] thành 1–2 dòng → (giá, [dòng…]) hoặc None
        ws = tu[a:b]
        L = _do_dai(ws)
        if L <= max_ky * .78 or len(ws) == 1:
            return (0.0 if L <= max_ky * 1.05 else 30.0), [ws]
        best = None
        for j in range(1, len(ws)):
            l1, l2 = _do_dai(ws[:j]), _do_dai(ws[j:])
            if l1 > max_ky or l2 > max_ky:
                continue
            gc = gia_ngat(a + j - 1) * .85 + abs(l1 - l2) * .3 + (4 if l1 < l2 * .45 else 0)
            if min(j, len(ws) - j) == 1 and len(ws) >= 4:      # dòng chỉ 1 chữ ("stories.") → xấu
                gc += 5
            if best is None or gc < best[0]:
                best = (gc, [ws[:j], ws[j:]])
        if best is None and L <= max_ky:
            return 0.0, [ws]
        return best

    INF = float('inf')
    tot = [INF] * (n + 1)
    vet = [None] * (n + 1)
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
            # không vắt qua chỗ ngừng dài / hết câu ở GIỮA cụm
            giua = 0.0
            for k in range(a, b - 1):
                g = tu[k + 1]['s'] - tu[k]['e']
                if g >= SUB_NGAT * 1.6:
                    giua += 25
                if re.search(r'[.!?…。！？]["”’»)]?$', tu[k]['w']):
                    giua += 18
            ngan = 0.0
            L = _do_dai(ws)
            if L < max_ky * .42 and b < n:
                ngan += 7
            if dai < .7 and b < n:
                ngan += 6
            if dai > 3.6:
                ngan += (dai - 3.6) * 6
            c = tot[a] + cd[0] + gia_ngat(b - 1) + giua + ngan + 4     # +4 mỗi cụm: không băm vụn
            if c < tot[b]:
                tot[b], vet[b] = c, (a, cd[1])
    cum, b = [], n
    while b > 0:
        a, dong = vet[b]
        cum.append(dong)
        b = a
    cum.reverse()
    out = []
    for k, dong in enumerate(cum):
        c0, c1 = dong[0][0], dong[-1][-1]
        tu0 = c0['s'] - .08
        nxt = cum[k + 1][0][0]['s'] - .08 if k + 1 < len(cum) else None
        den = c1['e'] + .35
        mo_ra = True
        if nxt is not None and nxt - c1['e'] < .6:
            den, mo_ra = nxt, False
        out.append({'tu': round(max(0, tu0), 3), 'den': round(den, 3), 'mo_ra': mo_ra,
                    'dong': [[{'w': w['w'], 's': w['s'], 'e': w['e']} for w in d] for d in dong]})
    for a, b in zip(out, out[1:]):
        if a['den'] > b['tu']:
            a['den'] = b['tu']
    return out


# ---------------- sub DỊCH (chữ trên hình khác tiếng giọng — người dùng yêu cầu, vd giọng Việt + sub Hàn) ----------------
SUB_DICH_EM = 14.6          # 1 dòng sub dịch ≤ ~14,6 em (≈ 900 px ở cỡ 60 px; dài hơn → khung tự co chữ)


def _rong_em(s):
    """bề rộng ước lượng (em) của chuỗi ở phông sub: Hàn / Nhật / Trung ~0,95 em, chữ Latin / số ~0,58, khoảng trắng 0,3."""
    r = 0.0
    for c in str(s):
        o = ord(c)
        if c == ' ':
            r += .3
        elif 0x1100 <= o <= 0x11FF or 0x2E80 <= o <= 0x9FFF or 0xAC00 <= o <= 0xD7AF or 0xF900 <= o <= 0xFFEF:
            r += .95
        elif 0x0E00 <= o <= 0x0E7F:
            r += .5
        elif c.isalnum():
            r += .58
        else:
            r += .35
    return r


def _chia_dich(chu, nn):
    """chữ 1 cụm sub dịch → 1–2 dòng: theo chỗ Claude ngắt (xuống dòng hoặc ' / '), không có thì tự chia ở khoảng trắng cân nhất,
    ưu tiên ngắt sau dấu câu."""
    p = [x.strip() for x in re.split(r'\s*\n\s*|\s+/\s+', str(chu)) if x.strip()]
    if len(p) != 1:
        return p
    s = p[0]
    if _rong_em(s) <= SUB_DICH_EM:
        return [s]
    if nn in KHONG_CACH:                                  # không cách chữ → chia theo ký tự, cân 2 dòng
        k = len(s) // 2
        for d in range(0, len(s) // 3):                   # ưu tiên ngắt sau dấu câu gần giữa
            for j in (k + d, k - d):
                if 0 < j < len(s) and re.match(r'[、，,。！？!?]', s[j - 1]):
                    return [s[:j], s[j:]]
        return [s[:k], s[k:]]
    ws = s.split(' ')
    best = None
    for j in range(1, len(ws)):
        a, b = ' '.join(ws[:j]), ' '.join(ws[j:])
        g = abs(_rong_em(a) - _rong_em(b)) - (3 if re.search(r'[,.!?…、，。]$', a) else 0)
        g += 50 * (max(0, _rong_em(a) - SUB_DICH_EM) + max(0, _rong_em(b) - SUB_DICH_EM))
        if best is None or g < best[0]:
            best = (g, [a, b])
    return best[1] if best else [s]


def _tach_chu(dong, nn):
    """1 dòng → các 'từ' để tô karaoke: tiếng có cách chữ → theo khoảng trắng; ja / zh / th → nhóm 2 ký tự."""
    if nn in KHONG_CACH:
        return [dong[i:i + 2] for i in range(0, len(dong), 2)]
    return [w for w in dong.split(' ') if w]


def sub_dich(kh, tu, dur, nn, E, Wn, kiem_chu):
    """kh['sub_dich'] = [{tu, den, chu}] (chữ đã dịch, đặt theo giây của lời gốc) → cụm sub cùng khuôn gom_sub.
    Karaoke: chữ vàng chạy dần theo nhịp lời gốc trong cụm (ước lượng theo bề rộng chữ); 'sub.karaoke_dich': false → tắt."""
    ds = [x for x in (kh.get('sub_dich') or []) if isinstance(x, dict)]
    if not ds:
        E(f'chu_ngon_ngu = {nn} khác tiếng giọng → cần sub_dich (chạy run.py sub-dich --work <dir> --ngon-ngu {nn} rồi điền chữ dịch)')
        return []
    karaoke = (kh.get('sub') or {}).get('karaoke_dich', True) is not False
    ds = sorted(ds, key=lambda x: float(x.get('tu', 0)))
    out = []
    for k, x in enumerate(ds):
        t0, t1 = float(x.get('tu', 0)), float(x.get('den', 0))
        chu = str(x.get('chu') or '').strip()
        noi = f'sub_dich {t0:.2f}s'
        if not chu:
            E(f'{noi}: chưa có chữ dịch (goc: «{str(x.get("goc", ""))[:50]}»)')
            continue
        if t1 - t0 < .6:
            E(f'{noi}: cụm chỉ {t1 - t0:.2f}s (< 0,6 s) — gộp với cụm bên cạnh')
            continue
        if t0 < 0 or t1 > dur + .05:
            E(f'{noi}: ngoài video (0–{dur:.2f}s)')
            continue
        kiem_chu(chu, noi)
        dong = _chia_dich(chu, nn)
        if len(dong) > 2:
            E(f'{noi}: {len(dong)} dòng — sub tối đa 2 dòng, tách thành 2 cụm')
            continue
        for d in dong:
            r = _rong_em(d)
            if r > SUB_DICH_EM * 1.15:
                E(f'{noi}: dòng «{d}» quá dài ({r:.1f} em > {SUB_DICH_EM}) — rút gọn hoặc tách cụm')
            elif r > SUB_DICH_EM:
                Wn(f'{noi}: dòng «{d}» hơi dài ({r:.1f} em) — khung tự co chữ nhỏ lại')
        # nhịp karaoke: trải các từ dịch lên khoảng lời gốc đọc trong cụm
        trong = [w for w in tu if w['s'] >= t0 - .1 and w['s'] < t1]
        s0 = trong[0]['s'] if trong else t0 + .1
        e0 = max(s0 + .3, min(t1, trong[-1]['e'])) if trong else t1 - .1
        toks = [[c for c in _tach_chu(d, nn)] for d in dong]
        tong = sum(_rong_em(c) + .15 for dd in toks for c in dd) or 1
        luc, dong_out = s0, []
        for dd in toks:
            hang = []
            for c in dd:
                dai = (e0 - s0) * (_rong_em(c) + .15) / tong
                if karaoke:
                    hang.append({'w': c, 's': round(luc, 3), 'e': round(luc + dai, 3)})
                else:
                    hang.append({'w': c, 's': -9.0, 'e': -9.0})
                luc += dai
            dong_out.append(hang)
        out.append({'tu': round(t0, 3), 'den': round(t1, 3), 'mo_ra': True, 'dong': dong_out})
    for a, b in zip(out, out[1:]):
        if a['den'] > b['tu'] + .05:
            E(f"sub_dich {a['tu']:.2f}s chồng cụm sau ({b['tu']:.2f}s) — den phải ≤ tu của cụm sau")
        if b['tu'] - a['den'] < .6:
            a['den'], a['mo_ra'] = min(a['den'], b['tu']), False
    # lời gốc chưa có sub dịch
    ho, cu = [], None
    for w in tu:
        co = any(c['tu'] - .15 <= w['s'] <= c['den'] for c in out)
        if not co:
            cu = [w['s'], w['e']] if cu is None or w['s'] - cu[1] > 1.0 else [cu[0], w['e']]
            if not ho or ho[-1] is not cu:
                ho.append(cu)
        else:
            cu = None
    for a, b in ho:
        Wn(f'lời {a:.1f}–{b:.1f}s chưa có sub dịch')
    return out


def khung_sub_dich(work, nn):
    """khung sub_dich NHÁP: cụm sub lời gốc (giây, chữ gốc) + chữ dịch trống → ghi vào ke_hoach.json để Claude dịch từng cụm."""
    work = Path(work)
    kh = doc_json(work / 'ke_hoach.json')
    lj = doc_json(work / 'loi.json')
    if nn not in NGON_NGU:
        raise SystemExit(f'⛔ --ngon-ngu {nn} chưa hỗ trợ (có: {", ".join(NGON_NGU)})')
    if kh.get('sub_dich'):
        raise SystemExit('⛔ ke_hoach.json đã có sub_dich — sửa trực tiếp (xoá sub_dich nếu muốn tạo lại khung)')
    goc = lj.get('ngon_ngu') or 'vi'
    tu, _ = sua_tu(lj['tu'], kh.get('sua_loi'))
    giu = list((kh.get('sub') or {}).get('giu_lien') or []) + list((kh.get('sua_loi') or {}).values())
    cum = gom_sub(tu, goc, giu)
    kh['chu_ngon_ngu'] = nn
    kh['sub_dich'] = [{'tu': c['tu'], 'den': c['den'], 'goc': ' '.join(w['w'] for d in c['dong'] for w in d), 'chu': ''}
                      for c in cum]
    from chung import ghi_json
    ghi_json(work / 'ke_hoach.json', kh)
    loi(f'Đã thêm chu_ngon_ngu = {nn} + {len(cum)} cụm sub_dich (chữ dịch TRỐNG) vào {work / "ke_hoach.json"}')
    loi(f'→ dịch từng «goc» sang {NGON_NGU[nn]["ten"]} vào «chu» (1–2 dòng, ≤ ~{SUB_DICH_EM:.0f} em / dòng; ngắt dòng bằng " / "), '
        f'rồi đổi MỌI chữ đồ hoạ / CTA / hành trình sang {NGON_NGU[nn]["ten"]} → run.py kiem-kh')


# ---------------- giải kế hoạch ----------------
_CHU_SO = {}


def _chu_so_nguon(work, lj):
    """lời + bài báo → tập số (float) xuất hiện dạng chữ số ('1.000' / '1,000' / '1 000' → 1000; '2,5' → 2.5),
    để soát số trên hình không bịa."""
    k = str(work)
    if k not in _CHU_SO:
        t = ' '.join(w['w'] for w in lj.get('tu', []))
        t = re.sub(r'(?<=\d) (?=[.,]\d)', '', t)        # Whisper tách '2 ,5' / '1 .000' → ghép lại
        bb = Path(work) / 'bai_bao' / 'bai_bao.txt'
        if bb.exists():
            t += ' ' + bb.read_text(encoding='utf-8', errors='replace')
        tap = set()
        for x in (t, re.sub(r'(?<=\d)[.,   ](?=\d{3}(?!\d))', '', t)):
            for s in re.findall(r'\d+(?:[.,]\d+)?', x):
                for v in {s.replace(',', '.'), re.sub(r'[.,]', '', s)}:
                    try:
                        tap.add(round(float(v), 6))
                    except ValueError:
                        pass
        tl = t.lower()
        for bac, chu in _BAC_SO.items():               # 'một nghìn năm' / 'a thousand years' → chấp nhận bội của 1000
            if any(c in tl for c in chu):
                tap.add(('bac', bac))
        if any(c in tl for c in _NUA):                 # 'bốn tiếng rưỡi' / 'four and a half hours' → '4h30' / '4,5 giờ' hợp lệ
            tap.update({30.0, 0.5})
        _CHU_SO[k] = tap
    return _CHU_SO[k]


_BAC_SO = {
    100: ('hundred', 'trăm', 'cent', 'hundert', 'cien', 'ciento', 'cento', 'ratus', 'сто', 'сот', '百', '백', 'ร้อย'),
    1000: ('thousand', 'nghìn', 'ngàn', 'mille', 'mil ', 'tausend', 'ribu', 'тысяч', '千', '천', 'พัน'),
    10**6: ('million', 'triệu', 'millón', 'milione', 'milhão', 'juta', 'миллион', '百万', '백만', 'ล้าน'),
    10**9: ('billion', 'tỷ', 'tỉ', 'milliard', 'mil millones', 'miliardo', 'bilhão', 'miliar', 'миллиард', '十亿', '억'),
}


_NUA = ('rưỡi', 'half', '半', 'demi', 'halb', 'media hora', 'mezz', 'meia', 'setengah', '반', 'ครึ่ง')


def _so_co_trong_nguon(so, tap):
    if round(so, 6) in tap:
        return True
    return any(so >= b and so % b == 0 and ('bac', b) in tap for b in _BAC_SO)


CANH_XA = ('doi', 'thanh_pho', 'nui')    # cảnh xa sau đường (nen duong): đồi thoải / đường chân trời thành phố / núi đá vôi
XE_CUA_NEN = {'troi': {'may_bay'}, 'bien': {'tau_thuy'}, 'duong': {'o_to', 'xe_may', 'xe_buyt', 'xe_dap', 'tau_hoa'}}


def _hanh_trinh(d, did, nn, E, Wn, kiem_chu, work, lj):
    """kiểm + điền mặc định cho đồ hoạ hành trình (điểm đi → điểm đến, phương tiện, thời gian / khoảng cách).
    → False nếu hỏng tới mức không dựng được."""
    pt = d.setdefault('phuong_tien', 'khong')
    if pt not in PHUONG_TIEN:
        E(f"{did}: phuong_tien lạ «{pt}» (có: {', '.join(PHUONG_TIEN)})")
        d['phuong_tien'] = pt = 'khong'
    nen = d.setdefault('nen', NEN_PT[pt])
    if nen not in NEN_HT:
        E(f"{did}: nen lạ «{nen}» (có: {', '.join(NEN_HT)})")
        d['nen'] = nen = NEN_PT[pt]
    if nen in ('troi', 'bien') and pt not in XE_CUA_NEN[nen]:
        E(f"{did}: nền «{nen}» chỉ vẽ {'máy bay' if nen == 'troi' else 'du thuyền'} — phương tiện «{pt}» dùng nen "
          f"«{NEN_PT[pt]}»")
    elif nen == 'duong' and pt not in XE_CUA_NEN['duong']:
        Wn(f"{did}: nền đường không có xe cho «{pt}» (chỉ cảnh đường chạy) — đi bộ / không rõ phương tiện nên dùng nen ban_do")
    for k in ('xuat_phat', 'diem_den'):
        o = d.get(k)
        if isinstance(o, str):
            d[k] = o = {'ten': o}
        if not isinstance(o, dict) or not o.get('ten'):
            E(f'{did}: {k} phải là {{"ten": …, "phu": …}}')
            return False
        kiem_chu(o['ten'], f'{did}.{k}.ten')
        kiem_chu(o.get('phu'), f'{did}.{k}.phu')
        if len(o['ten']) > 26:
            Wn(f"{did}: {k}.ten «{o['ten']}» dài — rút gọn tên (≤ 26 ký tự), phần phụ đưa vào «phu»")
    if nen == 'duong':
        xa = d.setdefault('canh_xa', 'doi')
        if xa not in CANH_XA:
            E(f"{did}: canh_xa lạ «{xa}» (có: {', '.join(CANH_XA)} — phố cho sân bay → trung tâm, núi cho Hạ Long / Hà Giang…)")
            d['canh_xa'] = 'doi'
    if nen == 'ban_do' and 'ho_tai' not in d:          # điểm đi / đến là hồ → vẽ hồ ngay tại điểm đó
        la_ho = lambda o: bool(re.search(r'(?i)^(hồ|lake|lac|lago|danau|see\b|озеро)|湖|호수|ทะเลสาบ|\b(lake|see)$', o.get('ten', '')))
        d['ho_tai'] = 'di' if la_ho(d['xuat_phat']) else 'den' if la_ho(d['diem_den']) else 'khong'
    if not d.get('thoi_gian') and not d.get('khoang_cach'):
        E(f'{did}: cần ít nhất thoi_gian hoặc khoang_cach (đúng như lời đọc)')
    nh = nhan_ht(nn)
    if nh:
        d.setdefault('dan', nh[0])
        if 'nhan_pt' not in d:
            d['nhan_pt'] = nh[2].get(pt) or (nh[1] if d.get('khoang_cach') and not d.get('thoi_gian') else '')
    elif not d.get('dan') or ('nhan_pt' not in d and pt != 'khong'):
        E(f'{did}: ngôn ngữ «{nn}» chưa có chữ mặc định cho hành trình — tự ghi dan + nhan_pt đúng tiếng audio')
    # số trên hình phải có trong lời / bài báo ('rưỡi' / 'half' = 30 phút)
    tap = _chu_so_nguon(work, lj)
    for f in ('thoi_gian', 'khoang_cach'):
        for s in re.findall(r'\d+(?:[.,]\d+)?', str(d.get(f) or '')):
            if not _so_co_trong_nguon(float(s.replace(',', '.')), tap):
                Wn(f"{did}.{f}: số {s} không có trong lời / bài báo — đừng bịa thời gian / khoảng cách")
    # giờ
    try:
        d['luc_di'] = float(d.get('luc_di', d['tu'] + .8))
        d['luc_den'] = float(d.get('luc_den', max(d['luc_di'] + 1.5, d['den'] - 1.0)))
        d['luc_tg'] = float(d.get('luc_tg', d['luc_di'] + .4))
        for f in ('luc_ten_di', 'luc_ten_den'):
            if d.get(f) is not None:
                d[f] = float(d[f])
    except (TypeError, ValueError):
        E(f'{did}: luc_di / luc_den / luc_tg phải là số giây')
        return False
    if d['den'] - d['tu'] < 3:
        Wn(f"{did}: hành trình chỉ {d['den'] - d['tu']:.1f}s — nên ≥ 3s để kịp thấy xe chạy + đọc thời gian")
    if not d['tu'] <= d['luc_di'] < d['luc_den'] <= d['den'] - .4:
        E(f"{did}: cần tu ≤ luc_di < luc_den ≤ den − 0,4 (đang {d['tu']} / {d['luc_di']} / {d['luc_den']} / {d['den']})")
    elif d['luc_den'] - d['luc_di'] < 1.2:
        Wn(f"{did}: phương tiện chạy {d['luc_den'] - d['luc_di']:.1f}s — quá nhanh, nên ≥ 1,2s")
    if not d['tu'] <= d['luc_tg'] <= d['den'] - .8:
        E(f"{did}: luc_tg {d['luc_tg']} phải trong {d['tu']}–{d['den'] - .8} (thời gian / khoảng cách hiện ≥ 0,8s)")
    d['kc_tren'] = d['nen'] != 'ban_do' and bool(d.get('thoi_gian')) and bool(d.get('khoang_cach'))
    if d.get('luc_kc') is not None:
        d['luc_kc'] = float(d['luc_kc'])
    for f in ('luc_ten_di', 'luc_ten_den', 'luc_kc'):
        if d.get(f) is not None and not d['tu'] <= d[f] <= d['den'] - .8:
            E(f"{did}: {f} {d[f]} ngoài {d['tu']}–{d['den'] - .8}")
    return True


def giai(work, bao=loi):
    """→ (KH, SFX[], chuan_bi[], loi[(muc, msg)])"""
    work = Path(work)
    kh = doc_json(work / 'ke_hoach.json')
    lj = doc_json(work / 'loi.json')
    tn = doc_json(work / 'tai_nguyen.json')
    L = []
    def E(m): L.append(('⛔', m))
    def Wn(m): L.append(('⚠', m))
    if kh.get('CAN_CLAUDE_SUA', True):
        E('CAN_CLAUDE_SUA vẫn = true — Claude chưa sửa kế hoạch theo nghĩa lời')
    nn = kh.get('ngon_ngu') or lj.get('ngon_ngu') or 'vi'
    if lj.get('ngon_ngu') and nn != lj['ngon_ngu']:
        E(f"ke_hoach.ngon_ngu = {nn} nhưng audio là {lj['ngon_ngu']} — chữ trên hình PHẢI theo ngôn ngữ audio")
    nn_giong = nn
    nn = kh.get('chu_ngon_ngu') or nn_giong      # tiếng CHỮ trên hình: mặc định = tiếng giọng; người dùng yêu cầu tiếng khác → sub dịch
    if nn not in NGON_NGU:
        E(f'chu_ngon_ngu «{nn}» chưa hỗ trợ (có: {", ".join(NGON_NGU)})')
        nn = nn_giong
    dich = nn != nn_giong
    LN = NGON_NGU.get(nn, NGON_NGU['en'])

    def kiem_chu(chu, noi):
        if not chu:
            return
        m, msg = kiem_ngon_ngu(chu, nn)
        if m == '⛔':
            E(f'{noi}: «{chu}» — {msg}')
        elif m == '⚠':
            Wn(f'{noi}: «{chu}» — {msg}')

    tu, khong_thay = sua_tu(lj['tu'], kh.get('sua_loi'))
    for s in khong_thay:
        Wn(f'sua_loi: không thấy cụm «{s}» trong lời — kiểm chính tả cụm sai')
    if not tu:
        E('lời rỗng')
        return None, [], [], L
    het_loi = tu[-1]['e']
    cta = kh.get('cta')
    if cta:
        luc_bam = float(cta.get('luc_bam') or (float(cta['tu']) + 1.9))
        luc_tim = float(cta.get('luc_tim') or (luc_bam + 1.35))
        dur = max(het_loi + DUOI + float(cta.get('them_giay', 1.6)), luc_tim + 1.3)
    else:
        dur = het_loi + DUOI
        Wn('không có CTA cuối video (cta) — skill yêu cầu CTA theo dõi + bàn tay bấm')
    dur = round(math.ceil(dur * FPS) / FPS, 4)

    # ---- nguồn ----
    NG = {a['id']: a for a in tn.get('ds', [])}
    for a in tn.get('bai', []):
        NG[a['id']] = dict(a, loai='anh', bai=True)
    dung_nguon = {}

    # ---- cảnh ----
    canh = sorted(kh.get('canh', []), key=lambda c: float(c.get('tu', 0)))
    if not canh:
        E('không có cảnh nào')
        return None, [], [], L
    if abs(float(canh[0]['tu'])) > 1e-6:
        E(f"cảnh đầu phải bắt đầu ở 0 (đang {canh[0]['tu']})")
    KC, CB, nguon_anh = [], [], []
    for i, c in enumerate(canh):
        cid = c.get('id') or f'c{i + 1:02d}'
        tu0 = float(c['tu'])
        den = float(canh[i + 1]['tu']) if i + 1 < len(canh) else dur
        dai = den - tu0
        kieu = c.get('chuyen', 'cat') if i > 0 else c.get('chuyen', 'cat')
        if kieu not in CHUYEN:
            E(f'{cid}: chuyển cảnh lạ «{kieu}» (có: {", ".join(CHUYEN)})')
            kieu = 'hoa_tan'
        vd = CHUYEN[kieu][0]
        if i == 0 and kieu not in ('cat', 'loe'):
            kieu, vd = 'cat', 0
        if dai < 1.2 and i + 1 < len(canh):
            E(f'{cid}: cảnh dài {dai:.2f}s < 1,2s — đổi cảnh quá dồn')
        elif dai > 9 and i + 1 < len(canh):
            Wn(f'{cid}: cảnh dài {dai:.1f}s > 9s — dễ nhàm, cân nhắc tách')
        if vd > dai * .6:
            E(f'{cid}: chuyển «{kieu}» {vd}s quá dài so với cảnh {dai:.2f}s')
        cd = c.get('chuyen_dong', 'zoom_vao')
        if cd not in CHUYEN_DONG:
            E(f'{cid}: chuyen_dong lạ «{cd}» (có: {", ".join(CHUYEN_DONG)})')
            cd = 'zoom_vao'
        nid = c.get('nguon')
        a = NG.get(nid)
        if not a:
            E(f'{cid}: nguồn «{nid}» không có (xem tai_nguyen.jpg: clip_XX / res_XX / bai_XX)')
            continue
        khung = c.get('khung', 'tran')
        tail = (CHUYEN.get(canh[i + 1].get('chuyen', 'cat'), (0,))[0] if i + 1 < len(canh) else 0) + .15
        o = {'id': cid, 'tu': round(tu0, 4), 'den': round(den, 4), 'vao': {'kieu': kieu, 'dai': vd}, 'chuyen_dong': cd, 'khung': khung,
             'nguon': nid}
        if a['loai'] == 'clip':
            if khung != 'tran':
                E(f'{cid}: clip chỉ dùng khung "tran"')
                o['khung'] = khung = 'tran'
            vg = float(c.get('vao_giay', 0))
            toc = float(c.get('toc_do', 1.0))
            if not .5 <= toc <= 1.5:
                E(f'{cid}: toc_do {toc} ngoài 0,5–1,5')
                toc = 1.0
            n = int(math.ceil((dai + tail) * FPS)) + 1
            can = n / FPS * toc
            if vg < 0 or vg + dai * toc > a['dai'] + .05:
                E(f"{cid}: {nid} chỉ dài {a['dai']:.1f}s — vao_giay {vg} + {dai * toc:.1f}s vượt quá (chọn vao_giay ≤ {max(0, a['dai'] - dai * toc):.1f})")
            elif vg + can > a['dai']:
                Wn(f'{cid}: đuôi chuyển cảnh vượt cuối clip {nid} — khung cuối sẽ đứng yên vài khung')
            for (x0, x1, cc) in dung_nguon.get(nid, []):
                if vg < x1 - .3 and vg + dai * toc > x0 + .3:
                    Wn(f'{cid}: dùng lại đoạn {nid} {vg:.1f}–{vg + dai * toc:.1f}s trùng cảnh {cc} — khán giả thấy lặp')
            dung_nguon.setdefault(nid, []).append((vg, vg + dai * toc, cid))
            o.update({'loai': 'clip', 'n': n})
            CB.append({'id': cid, 'loai': 'clip', 'file': a['file'], 'vao': vg, 'toc': toc, 'n': n, 'w': a['w'], 'h': a['h'],
                       'hdr': a.get('hdr', False), 'cat_x': float(c.get('cat_x', .5)), 'cat_y': float(c.get('cat_y', .5))})
        else:
            if khung not in ('tran', 'the'):
                E(f'{cid}: khung lạ «{khung}» (tran / the)')
                o['khung'] = khung = 'tran'
            s0 = max(W / a['w'], H / a['h'])
            if khung == 'tran' and s0 > 2.3:
                Wn(f"{cid}: ảnh {nid} {a['w']}x{a['h']} phóng ×{s0:.1f} để tràn màn sẽ vỡ nét → nên khung \"the\"")
            ty = int(c.get('the_y', 820))
            # không ghi the_rong → tự co cho ảnh DỌC / vuông: đáy thẻ ≤ 1295, rộng tối đa 960
            # (sub 2 dòng cao tới y ≈ 1330, thẻ còn lắc / nghiêng nhẹ ±20 px → chừa 30 px)
            tr = int(c['the_rong']) if c.get('the_rong') else int(min(960, 2 * (1295 - ty) * a['w'] / a['h']))
            o.update({'loai': 'anh', 'aw': a['w'], 'ah': a['h'], 'the_y': ty, 'the_rong': tr, 'lech_x': c.get('lech_x')})
            if khung == 'the':
                hh = min(1100, o['the_rong'] * a['h'] / a['w'])
                if o['the_y'] + hh / 2 > 1300:
                    E(f"{cid}: thẻ ảnh đáy {o['the_y'] + hh / 2:.0f}px sát / đè sub 2 dòng (≤ 1300) — giảm the_y / the_rong "
                      f"(bỏ the_rong là tự co)")
            CB.append({'id': cid, 'loai': 'anh', 'file': a['file'], 'khung': khung})
            if a.get('bai'):
                nguon_anh.append({'tu': tu0 + .2, 'den': den, 'chu': f"{LN['anh']}: {tn.get('nguon_bai') or 'bài báo'}"})
        KC.append(o)

    # ---- đồ hoạ ----
    DH, sfx = [], []
    def S(ten, luc):
        if ten in SFX and kh.get('sfx', True) is not False:
            f, db, lech = SFX[ten]
            sfx.append({'luc': round(luc + lech, 3), 'file': f, 'db': db, 'ten': ten})
    for i, c in enumerate(KC):
        if i > 0 and CHUYEN[c['vao']['kieu']][1]:
            S(CHUYEN[c['vao']['kieu']][1], c['tu'])
    lon = []
    for k, d in enumerate(kh.get('do_hoa', [])):
        d = dict(d)
        loai = d.get('loai')
        did = d['id'] = d.get('id') or f'd{k + 1:02d}'
        if loai not in LOAI:
            E(f'{did}: loại đồ hoạ lạ «{loai}» (có: {", ".join(LOAI)})')
            continue
        for f in BAT_BUOC[loai]:
            if d.get(f) in (None, '', []):
                E(f'{did} ({loai}): thiếu trường «{f}»')
        try:
            d['tu'], d['den'] = float(d['tu']), float(d['den'])
        except Exception:
            E(f'{did}: thiếu / sai tu, den')
            continue
        if d['den'] - d['tu'] < 1.2:
            E(f"{did}: hiện {d['den'] - d['tu']:.2f}s < 1,2s — không kịp đọc")
        if d['tu'] < 0 or d['den'] > dur + .01:
            E(f"{did}: thời gian {d['tu']}–{d['den']} ngoài video 0–{dur:.2f}")
        if cta and d['den'] > float(cta['tu']) + .05:
            E(f"{did}: đè lên CTA (CTA bắt đầu {cta['tu']}) — kết thúc trước CTA")
        if loai == 'hanh_trinh':
            if not _hanh_trinh(d, did, nn, E, Wn, kiem_chu, work, lj):
                continue
        for f in TRUONG_CHU.get(loai, ()):
            kiem_chu(d.get(f), f'{did}.{f}')
        buoc ={'tu_khoa': (0, .6), 'chip': (0, .2), 'liet_ke': (.5, .4)}.get(loai, (0, .3))
        for j, m in enumerate(d.get('muc', []) or []):
            if m.get('luc') is None:
                m['luc_abs'] = round(d['tu'] + buoc[0] + j * buoc[1], 3)
            kiem_chu(m.get('chu'), f'{did}.muc')
            if m.get('phu'):
                kiem_chu(m['phu'], f'{did}.muc.phu')
            if 'icon' in m and m['icon'] not in ICON_HOP_LE:
                E(f"{did}: icon lạ «{m['icon']}» (có: {', '.join(sorted(ICON_HOP_LE))})")
            if m.get('luc') is not None:
                m['luc_abs'] = float(m['luc'])
                if not d['tu'] - .01 <= m['luc_abs'] <= d['den'] - .5:
                    E(f"{did}: mục «{m.get('chu')}» luc {m['luc']} ngoài {d['tu']}–{d['den'] - .5}")
        if loai == 'the_anh':
            a = NG.get(d.get('anh'))
            if not a or a['loai'] != 'anh':
                E(f"{did}: ảnh «{d.get('anh')}» không có (res_XX / bai_XX)")
                continue
            d['aw'], d['ah'] = a['w'], a['h']
            CB.append({'id': did, 'loai': 'anh_the', 'file': a['file']})
            if a.get('bai'):
                nguon_anh.append({'tu': d['tu'] + .3, 'den': d['den'], 'chu': f"{LN['anh']}: {tn.get('nguon_bai') or 'bài báo'}"})
        if loai == 'chuong':
            d.setdefault('y', 360)
        if loai == 'so_lon':
            try:
                d['so'] = float(d['so'])
            except Exception:
                E(f'{did}: so phải là số')
            else:                                    # không bịa số: phải thấy trong lời hoặc bài báo
                if not _so_co_trong_nguon(d['so'], _chu_so_nguon(work, lj)):
                    Wn(f"{did}: số {d['so']:.10g} không có trong lời / bài báo — đừng bịa số (số đọc bằng chữ "
                       f"khác 'trăm / nghìn / triệu…' thì kiểm tay)")
        if loai not in NHO:
            for (a0, a1, aid) in lon:
                if d['tu'] < a1 - .3 and d['den'] > a0 + .3:
                    E(f'{did} chồng thời gian với {aid} — mỗi lúc chỉ 1 đồ hoạ lớn (ghim / chip được đi kèm)')
            lon.append((d['tu'], d['den'], did))
        # SFX
        if loai == 'mo_dau':
            S('mo_dau', d['tu']); S('lap_lanh', d['tu'] + 1.25)
        elif loai == 'tu_khoa':
            for m in d.get('muc', []):
                S('tu_khoa', m.get('luc_abs', d['tu']))
        elif loai == 'chuong':
            S('chuong', d['tu'])
            if d.get('so'):
                S('chuong_so', d['tu'])
        elif loai == 'tieu_de':
            S('chuong', d['tu'])
        elif loai == 'ghim':
            S('ghim', d['tu'])
        elif loai == 'chip':
            for j, m in enumerate(d.get('muc', [])):
                S('chip', m.get('luc_abs', d['tu'] + j * .2))
        elif loai == 'so_lon':
            td = float(d.get('dem_tu', d['tu'] + .15))
            S('so_lon', td); S('so_xong', td + float(d.get('dem_dai', 1.4)))
        elif loai == 'the_anh':
            S('the_anh', d['tu'])
        elif loai == 'liet_ke':
            for j, m in enumerate(d.get('muc', [])):
                S('liet_ke', m.get('luc_abs', d['tu'] + .5 + j * .4))
        elif loai == 'trich':
            S('trich', d['tu'])
        elif loai == 'hanh_trinh':
            pt = d['phuong_tien']
            S('ht_vao', d['tu'])
            am = {'may_bay': 'ht_may_bay', 'tau_thuy': 'ht_song', 'o_to': 'ht_xe', 'xe_may': 'ht_xe', 'xe_buyt': 'ht_xe',
                  'tau_hoa': 'ht_xe'}.get(pt)
            if am:
                S(am, d['luc_di'])
            S('ht_tg', d['luc_tg']); S('ht_den', d['luc_den'])
            if d.get('kc_tren'):
                S('ht_tg', d.get('luc_kc', d['luc_di'] + .3))
        DH.append(d)

    # ---- CTA ----
    CT = None
    if cta:
        CT = dict(cta)
        CT['tu'] = float(cta['tu'])
        CT['luc_bam'], CT['luc_tim'] = luc_bam, luc_tim
        for f in ('nut', 'nut_da'):
            CT.setdefault(f, LN[f])
        CT.setdefault('icon', ['thich', 'binh_luan', 'chia_se', 'luu'])
        nh = dict({k: LN[k] for k in ('thich', 'binh_luan', 'chia_se', 'luu')}, **(cta.get('nhan_icon') or {}))
        CT['nhan_icon'] = nh
        for f in ('tieu_de', 'viet_tay', 'nut', 'nut_da'):
            kiem_chu(CT.get(f), f'cta.{f}')
        for k2, v in nh.items():
            kiem_chu(v, f'cta.nhan_icon.{k2}')
        kenh = kh.get('kenh') or {}
        CT['ten'] = kenh.get('ten') or ''
        CT['handle'] = kenh.get('handle') or ''
        CT['chu_cai'] = (kenh.get('ten') or kenh.get('handle') or '★').lstrip('@')[:1].upper()
        if kenh.get('avatar'):
            if Path(kenh['avatar']).exists():
                CB.append({'id': 'avatar', 'loai': 'avatar', 'file': kenh['avatar']})
            else:
                E(f"kenh.avatar không thấy file {kenh['avatar']}")
        if not CT['ten'] and not CT['handle']:
            Wn('CTA chưa có tên kênh (kenh.ten / kenh.handle) — hỏi người dùng ở cổng duyệt')
        if dur - CT['tu'] < 3.8:
            E(f"CTA chỉ {dur - CT['tu']:.1f}s — cần ≥ 3,8s (đặt cta.tu sớm hơn hoặc tăng them_giay)")
        if kh.get('sfx_cta', True) is not False:
            S('cta_vao', CT['tu']); S('bam', luc_bam); S('icon', luc_bam + .35); S('tim', luc_tim); S('bam', luc_tim)
    nc = kh.get('nhac')
    if isinstance(nc, dict) and nc.get('file'):
        if not Path(nc['file']).exists():
            E(f"nhac.file không thấy: {nc['file']}")
        elif not -30 <= float(nc.get('muc_db', -18)) <= -10:
            Wn(f"nhac.muc_db {nc.get('muc_db')} lạ — chuẩn −14 (−10 lấn giọng, −30 gần như không nghe)")
    # không có nhạc = Resources không có file nhạc → đúng luật, không nhắc
    # ---- câu nói di chuyển A → B mà chưa có đồ hoạ hanh_trinh (SKILL mục 13) ----
    ht = [(float(d.get('tu', 0)), float(d.get('den', 0))) for d in kh.get('do_hoa', []) if d.get('loai') == 'hanh_trinh']
    bo = [float(x) for x in kh.get('bo_di_chuyen', []) or []]
    for r in cau_di_chuyen(lj.get('cau'), nn_giong):
        if any(r['s'] - .3 <= x <= r['e'] + .3 for x in bo):
            continue
        if not any(min(b, r['e']) - max(a, r['s']) > min(.8, (r['e'] - r['s']) * .4) for a, b in ht):
            Wn(f"câu {r['s']:.1f}–{r['e']:.1f}s nói di chuyển ({', '.join(r['cum'])}"
               + (f", {r['pt']}" if r['pt'] else '') + f") mà chưa có đồ hoạ hanh_trinh phủ câu: «{r['text'][:70]}» — "
               "thêm hanh_trinh (SKILL mục 13); không phải đi lại thì ghi giây câu vào bo_di_chuyen")
    # ---- sub ----
    giu = list((kh.get('sub') or {}).get('giu_lien') or []) + list((kh.get('sua_loi') or {}).values())
    for d in kh.get('do_hoa', []):
        for f in TRUONG_CHU.get(d.get('loai'), ()):
            if d.get(f):
                giu.append(str(d[f]))
        for m in d.get('muc', []) or []:
            if m.get('chu'):
                giu.append(m['chu'])
        for k in ('xuat_phat', 'diem_den'):
            o = d.get(k)
            if isinstance(o, dict) and o.get('ten'):
                giu.append(str(o['ten']))
    if not (kh.get('sub') or {}).get('bat', True):
        sub = []
    elif dich:
        sub = sub_dich(kh, tu, dur, nn, E, Wn, kiem_chu)
    else:
        sub = gom_sub(tu, nn_giong, giu)
    # ---- SFX: bỏ tiếng sát nhau ----
    sfx.sort(key=lambda e: e['luc'])
    gon = []
    for e in sfx:
        if gon and e['luc'] - gon[-1]['luc'] < .22:
            if e['db'] > gon[-1]['db']:
                gon[-1] = e
            continue
        if 0 <= e['luc'] < dur:
            gon.append(e)
    loe = []
    if KC and KC[0]['vao']['kieu'] == 'loe':
        loe.append({'t': -.25, 'dai': 1.1})
    KH = {'fps': FPS, 'dur': dur, 'ngon_ngu': nn, 'ngon_ngu_giong': nn_giong, 'canh': KC, 'do_hoa': DH, 'cta': CT, 'sub': sub, 'sub_y': SUB_Y,
          'nguon_anh': nguon_anh, 'loe': loe, 'het_loi': het_loi, 'an_toan': AN_TOAN}
    return KH, gon, CB, L


def kiem_kh(work, in_ra=True):
    KH, sfx, CB, L = giai(work)
    nd = sum(1 for m, _ in L if m == '⛔')
    nw = sum(1 for m, _ in L if m == '⚠')
    if in_ra:
        for m, msg in L:
            loi(f'{m} {msg}')
        if KH:
            loi(f"\nVideo {KH['dur']:.2f}s · {len(KH['canh'])} cảnh · {len(KH['do_hoa'])} đồ hoạ · {len(KH['sub'])} cụm sub · "
                f"{len(sfx)} SFX · ngôn ngữ chữ {KH['ngon_ngu']}"
                + (f" (giọng {KH['ngon_ngu_giong']} — sub dịch)" if KH['ngon_ngu'] != KH['ngon_ngu_giong'] else ''))
        loi(f"KIỂM KẾ HOẠCH: {'ĐẠT' if nd == 0 else 'CHƯA ĐẠT'} — {nd} ⛔, {nw} ⚠")
    return nd == 0
