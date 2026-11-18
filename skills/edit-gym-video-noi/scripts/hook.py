# -*- coding: utf-8 -*-
"""HOOK ĐƯA LÊN ĐẦU — chọn đoạn "đắt" nhất của video nói rồi chèn làm teaser 4–9 s ở ĐẦU video, sau đó video chạy lại
từ đầu như bình thường (kiểu TikTok / Reels: người xem bị giữ ngay giây đầu).

  run.py goi-y-hook --work <dir>              → chấm điểm mọi cửa sổ lời 4–9 s, in top 6 + hook_goi_y.txt
  run.py hook --work <dir> --tu 36.3 --den 44.6 → dựng lại nguon.mp4 = [hook] + [toàn bộ video]; dời words / cut / mặt;
                                                  sinh lại ke_hoach.json NHÁP + loi_doc.txt; ghi hook.json

Dòng thời gian sau khi chèn: 0 … L là hook (copy), L … L+dur là video đầy đủ. Mọi mốc trong ke_hoach.json tính theo
dòng thời gian MỚI. `hook` chỉ chạy được 1 lần cho mỗi work (chạy lại thì tự lấy lại nguon_chinh.mp4)."""
import os, re, json, shutil, unicodedata
import numpy as np
import chung as C

TU_DAT = {   # từ "đắt" kích thích tò mò / cảm xúc / con số — điểm cộng cho cửa sổ lời
    'bí mật': 3, 'sai lầm': 3, 'dấu hiệu': 3, 'quan trọng': 2.5, 'nguy hiểm': 3, 'hậu quả': 3, 'tiền': 2, 'triệu': 2.5,
    'mất': 2, 'khách hàng': 1.5, 'không': 0.8, 'chưa': 1, 'đừng': 2.5, 'tại sao': 3, 'vì sao': 3, 'làm sao': 2,
    'cách': 1.2, 'bạn': 0.6, 'nếu': 1, 'giả sử': 2, 'thu nhập': 2.5, 'kiếm': 2, 'phải': 0.8, 'hệ thống': 2, 'khoá học': 2.5,
    'khóa học': 2.5, 'thiết kế': 1.5, 'kinh nghiệm': 1.5, 'kiến thức': 1.5, 'bị': 1, 'rối': 2, 'mệt': 2, 'đau': 2, 'chấn thương': 2.5,
    'cải thiện': 1.5, 'tăng': 1.2, 'giảm': 1.2, 'ba': 1, 'năm': 0.5, 'chỉ': 0.8, 'chính': 0.8, 'sự thật': 3, 'thật ra': 2.5,
    'thực ra': 2.5, 'ai cũng': 2.5, 'hầu hết': 2.5, 'nhiều người': 2.5, 'bí quyết': 3, 'cuối cùng': 1.5,
}


def _bd(s):
    s = unicodedata.normalize('NFD', s.lower()).replace('đ', 'd')
    return ''.join(c for c in s if unicodedata.category(c) != 'Mn')


def cham_cua_so(words, dur, lo=4.0, hi=9.0):
    """mọi cửa sổ lời [bắt đầu ở đầu câu .. kết thúc ở cuối câu] dài lo..hi s, chấm điểm."""
    n = len(words); ds = []
    # đầu câu: sau khoảng lặng ≥ 0,35 s hoặc sau dấu chấm
    dau = [i for i in range(n) if i == 0 or words[i]['s'] - words[i - 1]['e'] >= 0.35 or re.search(r'[.?!…]$', words[i - 1]['w'])]
    cuoi = [i for i in range(n) if i == n - 1 or words[i + 1]['s'] - words[i]['e'] >= 0.35 or re.search(r'[.?!…]$', words[i]['w'])]
    for i in dau:
        for j in cuoi:
            if j <= i: continue
            a, b = words[i]['s'], words[j]['e']
            if not (lo <= b - a <= hi): continue
            txt = ' '.join(w['w'] for w in words[i:j + 1]); t = _bd(txt)
            sc = sum(v for k, v in TU_DAT.items() if _bd(k) in t)
            sc += 1.5 * len(re.findall(r'\d', txt)) ** 0.5
            sc += 2.0 if '?' in txt else 0
            nhip = (j - i + 1) / (b - a)             # chữ / giây — nói nhanh, gọn = cuốn
            sc += 0.6 * min(nhip, 3.5)
            sc -= 0.6 * abs((b - a) - 6.0)           # ưa ~6 s
            sc -= 3.0 * (a / dur < 0.04)             # đoạn ngay đầu video thì không cần hook
            sc += 1.0 * (a / dur > 0.35)             # lấy từ thân video (đỡ lặp lại đoạn mở)
            ds.append((sc, a, b, txt))
    ds.sort(key=lambda x: -x[0])
    ra = []
    for d in ds:                                       # bỏ trùng nhau
        if all(d[2] <= r[1] or d[1] >= r[2] for r in ra): ra.append(d)
        if len(ra) >= 6: break
    return ra


def goi_y(work):
    words = C.doc_json(os.path.join(work, 'words.json'))
    dur = C.probe(os.path.join(work, 'nguon.mp4'))['dur']
    ra = cham_cua_so(words, dur)
    with open(os.path.join(work, 'hook_goi_y.txt'), 'w', encoding='utf-8') as f:
        for sc, a, b, txt in ra:
            s = f'{sc:5.1f}  {a:6.2f}–{b:6.2f} ({b - a:.1f}s)  {txt}'
            print(s); f.write(s + '\n')
    return ra


def chay(work, a, b):
    gop = os.path.join(work, 'nguon.mp4'); chinh = os.path.join(work, 'nguon_chinh.mp4')
    gchinh = os.path.join(work, 'giong_chinh.wav'); wchinh = os.path.join(work, 'words_chinh.json')
    cchinh = os.path.join(work, 'cut_chinh.json')
    if not os.path.exists(chinh):                        # lần đầu: giữ bản gốc (không hook)
        shutil.copy(gop, chinh); shutil.copy(os.path.join(work, 'giong.wav'), gchinh)
        shutil.copy(os.path.join(work, 'words.json'), wchinh); shutil.copy(os.path.join(work, 'cut.json'), cchinh)
    words = C.doc_json(wchinh); cuts = C.doc_json(cchinh)
    dur = C.probe(chinh)['dur']
    a = round(max(0.0, a) * C.FPS) / C.FPS; b = round(min(dur, b) * C.FPS) / C.FPS
    L = round(b - a, 4)
    if L < 2: raise SystemExit('Hook < 2 s')
    vf = (f'[0:v]trim=start={a:.4f}:end={b:.4f},setpts=PTS-STARTPTS[hv];'
          f'[0:a]atrim=start={a:.4f}:end={b:.4f},asetpts=PTS-STARTPTS,afade=t=in:d=0.01,afade=t=out:st={L - 0.015:.3f}:d=0.015[ha];'
          f'[0:v]setpts=PTS-STARTPTS[mv];[0:a]asetpts=PTS-STARTPTS,afade=t=in:d=0.015[ma];'
          f'[hv][ha][mv][ma]concat=n=2:v=1:a=1[v][a]')
    C.run(['ffmpeg', '-y', '-v', 'error', '-i', chinh, '-filter_complex', vf, '-map', '[v]', '-map', '[a]', '-c:v', 'libx264',
           '-crf', '14', '-preset', 'fast', '-pix_fmt', 'yuv420p', '-color_primaries', 'bt709', '-color_trc', 'bt709',
           '-colorspace', 'bt709', '-c:a', 'aac', '-b:a', '256k', gop])
    C.run(['ffmpeg', '-y', '-v', 'error', '-i', gop, '-vn', '-ac', '2', '-ar', str(C.SR), '-c:a', 'pcm_s16le',
           os.path.join(work, 'giong.wav')])
    # lời: hook (copy, dời về 0) + toàn bộ video dời L
    hw = [dict(w, s=round(w['s'] - a, 3), e=round(w['e'] - a, 3), hook=True) for w in words if w['s'] >= a - 0.08 and w['e'] <= b + 0.06]
    for w in hw: w['s'] = max(0.0, w['s']); w['e'] = min(L, w['e'])
    mw = [dict(w, s=round(w['s'] + L, 3), e=round(w['e'] + L, 3)) for w in words]
    C.ghi_json(os.path.join(work, 'words.json'), hw + mw)
    cc = [dict(c, t=round(c['t'] + L, 3)) for c in cuts] + [{'t': round(L, 3), 'diem': 1.0, 'loai': 'boi_canh'}]
    cc.sort(key=lambda c: c['t'])
    C.ghi_json(os.path.join(work, 'cut.json'), cc)
    # mặt Haar nháp: dời theo (MediaPipe dò lại ở run.py nguoi vì nguon.mp4 đã đổi)
    mp = os.path.join(work, 'mat_haar.json') if os.path.exists(os.path.join(work, 'mat_haar.json')) else os.path.join(work, 'mat.json')
    cu = C.doc_json(mp)
    if os.path.exists(os.path.join(work, 'mat_chinh.json')): cu = C.doc_json(os.path.join(work, 'mat_chinh.json'))
    else: C.ghi_json(os.path.join(work, 'mat_chinh.json'), cu)
    ts = np.array([d['t'] for d in cu])
    moi = []
    for k in range(int((L + dur) / 0.2) + 1):
        t = k * 0.2; to = a + t if t < L else t - L
        d = cu[int(np.argmin(np.abs(ts - to)))]
        moi.append(dict(d, t=round(t, 2)))
    C.ghi_json(os.path.join(work, 'mat.json'), moi)
    for f in ('mat_haar.json', 'mat_mp.json', 'nguoi_mask.json', 'nguoi_mask.npy', 'tay.json'):
        p = os.path.join(work, f)
        if os.path.exists(p): os.remove(p)
    C.ghi_json(os.path.join(work, 'hook.json'), {'tu': a, 'den': b, 'L': L, 'dur_chinh': dur})
    tong = C.probe(gop)['dur']
    import vinh
    vinh.nhap(work)
    print(f'Hook {a:.2f}–{b:.2f} s ({L:.2f} s) đã chèn lên đầu → nguon.mp4 dài {tong:.2f} s (hook 0–{L:.2f}, video đầy đủ {L:.2f}–{tong:.2f})')
    return L
