# -*- coding: utf-8 -*-
"""PHONG CÁCH VINH — kế hoạch NHÁP tự động cho video người nói (PT / giáo dục / chuyên gia).

  run.py nhap-vinh --work <dir>   → ghi ke_hoach.json NHÁP từ words.json + cut.json (+ hook.json nếu đã chèn hook):
      sub     : cụm 3–6 chữ ngắt theo nhịp nói, 1 dòng TRÊN ĐẦU (sub_vi_tri = 'tren')
      nhan    : chữ nhấn hồng đậm — cụm 1–3 chữ "đắt" nhất mỗi câu (số, hậu quả, tên khái niệm…), glitch khi vào
      zoom    : nhảy 1,0 / 1,12 / 1,0 / 1,22 ở đầu câu (cách ≥ 3 s)
      chuyen  : loé vàng ở chỗ nối hook → video chính; glitch ở đầu "chương" (khoảng lặng ≥ 1,0 s)
  Claude PHẢI sửa theo NGHĨA: đúng chữ khoá, số mục (kieu "so" + phu), tên khái niệm, lời Whisper nghe sai."""
import os, re, unicodedata
import chung as C
import hook as H

TU_DAN = set('khi và vậy nhưng đó là bởi vì những các một nếu còn hãy bạn tôi anh chị em mình họ này với có cho để thì mà '
             'nên ai gì điều đã đang sẽ rất cũng lại chỉ mới hay hoặc thật tại ở trong ngay chính đây kia ấy của được cái '
             'thế như đều từ ra vào lên xuống rồi nữa luôn vẫn phải cần'.split())
NGAT_TRUOC = set('và nhưng mà để thì là vì nên nếu khi hoặc với còn bởi'.split())


def _sach(w):
    return re.sub(r'[.,!?;:…"“”]+$', '', w)


GHEP = ['quảng ngãi', 'đào tạo', 'nghề nghiệp', 'kinh nghiệm', 'huấn luyện', 'dinh dưỡng', 'duy trì', 'điều độ', 'tích lũy',
        'quan trọng', 'tinh bột', 'phòng tập', 'thói quen', 'tập luyện', 'ăn uống', 'năng lượng', 'giảm cân', 'cân nặng',
        'cân bằng', 'hiệu ứng', 'thậm chí', 'chuyên sâu', 'mọi người', 'khó khăn', 'ăn đủ', 'cắt giảm', 'cắt bỏ', 'huấn luyện viên',
        'tăng cân', 'tạm biệt', 'đầy đủ', 'một cái', 'cái điều', 'thứ nhất', 'thứ hai', 'thứ 2', 'quan trọng', 'không hề', 'ở đây', 'rất nhiều', 'hơn 10']          # cặp chữ KHÔNG được ngắt giữa chừng
GHEP_CAP = {g for g in GHEP if g.count(' ') == 1} | {'luyện viên'}
LUNG_LO = set('là một cái của các những và với như cũng trong về để thì mà đó rất sẽ đã bị được có cho hay nếu khi từ ở'
              ' mình chúng ta tôi bạn nó này tại sẽ không hay lên thứ'.split())   # cụm không nên KẾT THÚC bằng các chữ này
GIU_HOA = {'PT', 'Quảng', 'Ngãi', 'HLV', 'BMI'}


def _hoa(t):
    return t if (t in GIU_HOA or t.upper() == t and len(t) > 1) else t[:1].lower() + t[1:]


def cum_sub(words, toi_da_tu=None, toi_da_chu=None):
    """chia lời thành cụm sub bằng quy hoạch động: ưa 3–6 chữ, ngắt ở dấu câu / khoảng lặng / trước liên từ,
    không ngắt giữa từ ghép (GHEP), không kết thúc bằng chữ lửng (LUNG_LO), không vượt quá giới hạn ký tự.
    Chỗ nối hook → video chính luôn là chỗ ngắt."""
    V = C.VINH
    tu = toi_da_tu or V['sub_toi_da_tu']; ch = toi_da_chu or V['sub_toi_da_chu']
    ra = []
    seg, cur_hook = [], None
    for w in words + [None]:
        hk = bool(w.get('hook')) if w else None
        if w is not None and (cur_hook is None or hk == cur_hook):
            seg.append(w); cur_hook = hk; continue
        if seg: ra += _dp(seg, tu, ch)
        seg, cur_hook = ([w], hk) if w else ([], None)
    return ra


def _chi_phi_ngat(ws, i):
    """chi phí ngắt SAU chữ i (thấp = chỗ ngắt tốt)."""
    w = ws[i]; n = ws[i + 1] if i + 1 < len(ws) else None
    c = 0.0
    if re.search(r'[,.?!…]$', w['w']): c -= 3.0
    if n is not None:
        gap = n['s'] - w['e']
        c -= 2.0 if gap > 0.3 else (1.0 if gap > 0.15 else 0.0)
        if _sach(n['w']).lower() in NGAT_TRUOC: c -= 1.5
        pair = _sach(w['w']).lower() + ' ' + _sach(n['w']).lower()
        if pair in GHEP_CAP: c += 6.0
        if _sach(w['w']).lower() in LUNG_LO: c += 4.0
    return c


def _dp(ws, tu, ch):
    n = len(ws)
    INF = 1e9
    best = [INF] * (n + 1); best[0] = 0.0; tr = [0] * (n + 1)
    for j in range(1, n + 1):
        for i in range(max(0, j - tu), j):
            L = j - i
            s = ' '.join(_sach(x['w']) for x in ws[i:j])
            if len(s) > ch: continue
            c = best[i] + 0.35 * (L - 4.5) ** 2 + (_chi_phi_ngat(ws, j - 1) if j < n else -1.0)
            if L == 1 and j < n: c += 2.0
            if c < best[j]: best[j] = c; tr[j] = i
    out, j = [], n
    if best[n] >= INF:      # không chia được (chữ quá dài) → mỗi chữ 1 cụm
        return [[x] for x in ws]
    while j > 0:
        out.append(ws[tr[j]:j]); j = tr[j]
    return out[::-1]


def _cum_sub_cu(words, toi_da_tu=None, toi_da_chu=None):
    V = C.VINH
    return []


def _trong(w):
    t = _sach(w['w']).lower()
    if re.search(r'\d', t): return 2.2
    return 0.0 if t in TU_DAN else 0.5 + 0.25 * min(len(t), 8) / 8


def chon_nhan(cau):
    """mỗi câu: tối đa 1–2 cụm 1–3 chữ đắt nhất (điểm theo từ khoá H.TU_DAT + chữ nội dung)."""
    ra = []
    for ws in cau:
        if len(ws) < 3: continue
        t0c, t1c = ws[0]['s'], ws[-1]['e']
        ung = []
        for i in range(len(ws)):
            for L in (1, 2, 3):
                if i + L > len(ws): break
                sp = ws[i:i + L]
                txt = ' '.join(_sach(x['w']) for x in sp)
                if len(txt) > 20: continue
                if _sach(sp[0]['w']).lower() in TU_DAN or _sach(sp[-1]['w']).lower() in TU_DAN: continue
                bd = H._bd(txt)
                sc = sum(_trong(x) for x in sp) + sum(v for k, v in H.TU_DAT.items() if H._bd(k) in bd)
                sc += 0.35 * (L - 1)
                if sp[-1]['s'] > t0c + 0.5: sc += 0.2           # ưa vế sau (ý chính hay ở cuối)
                ung.append((sc, i, i + L, txt))
        if not ung: continue
        ung.sort(key=lambda x: -x[0])
        chon = []
        for sc, a, b, txt in ung:
            if sc < 1.6: break
            if all(b <= c[0] or a >= c[1] for c in chon) and (not chon or abs(ws[a]['s'] - ws[chon[0][0]]['s']) >= 2.5):
                chon.append((a, b, txt, sc))
            if len(chon) >= (2 if t1c - t0c > 6.5 else 1): break
        for a, b, txt, sc in chon:
            ra.append({'t0': ws[a]['s'] - 0.12, 'tw1': ws[b - 1]['e'], 'text': txt.upper(), 'sc': sc, 'cau_t1': t1c})
    ra.sort(key=lambda x: x['t0'])
    out = []
    for k, r in enumerate(ra):
        t0 = max(0.25, r['t0'])
        if out and t0 < out[-1]['t1'] + 0.08:       # nhấn trước kết thúc sớm cho nhấn sau
            if t0 - out[-1]['t0'] < 1.2: continue    # quá sát → bỏ cái điểm thấp hơn (ở đây: cái sau)
            out[-1]['t1'] = t0 - 0.08
        t1 = max(t0 + 1.7, r['tw1'] + 0.9)
        t1 = min(t1, r['cau_t1'] + 0.8)
        out.append({'t0': round(t0, 2), 't1': round(t1, 2), 'text': r['text'], 'kieu': 'chu'})
    nxt_t0 = [o['t0'] for o in out[1:]] + [1e9]
    for o, n in zip(out, nxt_t0):
        o['t1'] = round(max(o['t0'] + 1.0, min(o['t1'], n - 0.08)), 2)
    return out


def nhap(work):
    import phan_tich as P
    words = C.doc_json(os.path.join(work, 'words.json'))
    cuts = C.doc_json(os.path.join(work, 'cut.json')) if os.path.exists(os.path.join(work, 'cut.json')) else []
    src = os.path.join(work, 'nguon.mp4')
    dur = C.probe(src)['dur']
    meta = C.doc_json(os.path.join(work, 'nguon_meta.json')) if os.path.exists(os.path.join(work, 'nguon_meta.json')) else {}
    hk = C.doc_json(os.path.join(work, 'hook.json')) if os.path.exists(os.path.join(work, 'hook.json')) else None
    plan = {'CAN_CLAUDE_SUA': True, 'phong_cach': 'vinh', 'sub_vi_tri': 'nguc', 'sub_kieu': 'karaoke', 'demo': [], 'cta': [], 'dur': round(dur, 3),
            'video_goc': meta.get('video'), 'cat_lang': meta.get('cat_lang', 'khong'), 'nhac': None, 'nhac_ss': 0.0, 'sfx': True,
            'zoom': [{'t': 0.0, 'z': 1.0}], 'chuyen': [], 'tieu_de': [], 'sub': [], 'nhan': [], 'the_anh': [], 'icon': [],
            'tim_kiem': [], 'so_tien': [], 'logo': [], 'liet_ke': [], 'sfx_them': [], 'sfx_bo': []}
    if hk: plan['hook'] = hk
    L = hk['L'] if hk else 0.0
    cau = P.chia_cau(words, [c for c in cuts if c['loai'] == 'boi_canh'])
    # --- sub
    cums = cum_sub(words, C.VINH['sub_nguc_tu'], C.VINH['sub_nguc_chu']) if plan['sub_vi_tri'] == 'nguc' else cum_sub(words)
    for j, cm in enumerate(cums):
        t0 = round(max(0.0, cm[0]['s'] - 0.05), 3)
        t1 = round(cums[j + 1][0]['s'] - 0.05, 3) if j + 1 < len(cums) and cums[j + 1][0]['s'] - cm[-1]['e'] < 0.5 else round(min(dur, cm[-1]['e'] + 0.35), 3)
        if t1 - t0 < 0.35: continue
        toks = [{'w': _hoa(_sach(x['w'])), 's': round(x['s'], 3), 'e': round(x['e'], 3)} for x in cm]
        txt = ' '.join(t['w'] for t in toks)
        plan['sub'].append({'t0': t0, 't1': t1, 'dong': [{'text': txt, 'kieu': 'tren' if plan['sub_vi_tri'] == 'tren' else 'chinh'}],
                            'tu': toks})
    # --- nhấn
    plan['nhan'] = chon_nhan(cau)
    # --- zoom nhảy: ưu tiên đúng các cú cắt (jump cut do cắt lặng — đổi khung giấu mối nối), rồi đầu câu
    muc = C.VINH['zoom']; zi = 0; last = -9.0
    cand = [(c['t'], 0) for c in cuts if c['loai'] == 'nhay'] + [(ws[0]['s'] - 0.04, 1) for ws in cau[1:]]
    for t, uu in sorted(cand):
        t = round(t, 3)
        if t - last < (1.2 if uu == 0 else 3.0) or abs(t - L) < 0.6: continue
        plan['zoom'].append({'t': t, 'z': muc[zi % 4]}); zi += 1; last = t
    # --- chuyển cảnh
    if hk:
        plan['chuyen'].append({'t': round(L, 3), 'kieu': 'flash_vang'})
        plan['zoom'].append({'t': round(L, 3), 'z': 1.0})
    ngat = [(words[k]['s'], words[k - 1]['e']) for k in range(1, len(words)) if words[k]['s'] - words[k - 1]['e'] >= 1.0 and words[k]['s'] > L + 3]
    kieu = ['glitch', 'flash_vang']
    for k, (t, _) in enumerate(ngat):
        if any(abs(t - c['t']) < 4 for c in plan['chuyen']): continue
        plan['chuyen'].append({'t': round(t - 0.05, 3), 'kieu': kieu[k % 2]})
    # --- CTA cuối video: OVERLAY (4 bóng icon → nút THEO DÕI → tay 3D bấm → tút) ở ~4,2 s cuối; lời không nói comment / theo dõi thì BẮT BUỘC
    import re as _re
    cuoi = ' '.join(w['w'] for w in words if w['s'] >= dur - C.CTA['cuoi_s'])
    plan['cta_loi'] = bool(_re.search(C.CTA['regex'], cuoi, _re.I))
    plan['cta'] = [{'t0': round(dur - C.CTA['dai_s'] - 0.05, 2), 't1': round(dur - 0.05, 2), 'kieu': 'follow'}]
    plan['zoom'].sort(key=lambda z: z['t'])
    plan['chuyen'].sort(key=lambda c: c['t'])
    kh = os.path.join(work, 'ke_hoach.json')
    if os.path.exists(kh):
        import shutil; shutil.copy(kh, os.path.join(work, 'ke_hoach_cu.json'))
    C.ghi_json(kh, plan)
    P.ghi_loi(cau, os.path.join(work, 'loi_doc.txt'))
    print(f'Nháp Vinh: {len(plan["sub"])} cụm sub · {len(plan["nhan"])} chữ nhấn · {len(plan["chuyen"])} chuyển cảnh · '
          f'{len(plan["zoom"])} zoom · dài {dur:.1f} s' + (f' · hook {L:.1f} s' if hk else ''))
    return plan
