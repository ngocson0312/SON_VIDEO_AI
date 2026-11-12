# -*- coding: utf-8 -*-
"""Dò BÀN TAY người nói → chỗ icon / thẻ ảnh MỌC RA TỪ TAY (chữ ký của video mẫu: icon "Vị trí" / "Tiện ích" trên lòng
bàn tay, thẻ ảnh bay ra từ tay).

Nguồn dò (tự chọn):
  1. MediaPipe Hands (21 điểm / tay) — chạy trong venv riêng `~/.bds_sale_viral/venv_tay` qua `tay_mp.py`
     (cài: `run.py cai-tay`). Bắt MỌI tư thế: xoè tay trước ngực, giơ tay, chỉ tay, dang tay; bỏ tay cầm mic
     (sát miệng) và tay buông thõng (ngón chúc xuống ở hông).
  2. Không có venv → mặt nạ người (nguoi_mask.npy): chỉ bắt được lúc DANG TAY sang ngang (vươn ≥ 2 × cao mặt).
Ra `<work>/tay.json`:
  khung: {trai: [[x, y, ngang, mo, hoat] | null …], phai: …}  mỗi `buoc` khung, toạ độ NGUỒN (x, y = giữa lòng bàn tay),
         ngang = |x − tâm mặt| / cao mặt, mo = số ngón duỗi (0–5),
         hoat = 0 (không dùng được: cầm mic / buông thõng / ngoài tầm) · 1 (tay RẢNH trước người — icon mọc được)
                · 2 (XOÈ ≥ mo_min ngón hoặc DANG ≥ ngang_min — nhịp đẹp nhất để icon bật ra)
  cu_chi: [{ben, t0, t1, x, y, ext, mo, loi}]   đoạn làm cử chỉ ≥ C.TAY['min_s'] (loi = chữ đang nói)
  goi_y:  [{t0, t1, loai, nhan, ben, tu}]        icon gợi ý: từ khoá trong lời (C.ICON_TU) trùng lúc tay đang làm cử chỉ
+ `tay.jpg` (khung đầu mỗi cử chỉ, vòng vàng ở lòng bàn tay + chữ đang nói) để Claude soi.
'trai' / 'phai' = bên TRÁI / PHẢI KHUNG HÌNH (người xem)."""
import os, re, subprocess, unicodedata
import numpy as np
import cv2
from PIL import Image, ImageDraw
import chung as C
import nguoi

PHIEN = 3
VENV = os.path.join(os.path.expanduser('~'), '.bds_sale_viral', 'venv_tay')


def venv_py():
    for p in (os.path.join(VENV, 'Scripts', 'python.exe'), os.path.join(VENV, 'bin', 'python')):
        if os.path.isfile(p): return p
    return None


def cai_dat():
    """tạo venv riêng + cài mediapipe 0.10.21 (cần mạng, ~150 MB)."""
    import sys
    if not venv_py():
        subprocess.run([sys.executable, '-m', 'venv', VENV], check=True)
    py = venv_py()
    subprocess.run([py, '-m', 'pip', 'install', '-q', '--upgrade', 'pip'], check=False)
    subprocess.run([py, '-m', 'pip', 'install', '-q', 'mediapipe==0.10.21'], check=True)
    r = subprocess.run([py, '-c', 'import mediapipe as mp; print(mp.__version__)'], capture_output=True, text=True)
    print('  mediapipe', r.stdout.strip() or r.stderr[-300:])
    return r.returncode == 0


# ------------------------------------------------------------------ 1 mốc
def _ngon(xs, ys):
    """số ngón duỗi (cái + trỏ, giữa, áp út, út) + ngón chúc xuống?"""
    w = np.array([xs[0], ys[0]])
    d = lambda k: float(np.hypot(xs[k] - w[0], ys[k] - w[1]))
    mo = sum(1 for tip, pip in ((8, 6), (12, 10), (16, 14), (20, 18)) if d(tip) > 1.12 * d(pip))
    if np.hypot(xs[4] - xs[17], ys[4] - ys[17]) > 1.1 * np.hypot(xs[3] - xs[17], ys[3] - ys[17]): mo += 1
    chuc = float(np.mean([ys[k] for k in (8, 12, 16, 20)])) > ys[0] + 0.5 * d(9)
    return mo, chuc


def _mot_mp(ds, m, T):
    """ds: các tay MediaPipe của 1 mốc; m: hộp mặt (nguồn). → {ben: [x, y, ngang, mo, hoat] | None}"""
    out = {'trai': None, 'phai': None}
    if not ds: return out
    if m: fx, fy, fh = (m[0] + m[2]) / 2, (m[1] + m[3]) / 2, max(1.0, m[3] - m[1])
    else: fx, fy, fh = C.W / 2, C.H * 0.33, C.W * 0.14
    ung = {'trai': [], 'phai': []}
    for h in ds:
        xs, ys = np.array(h['x']), np.array(h['y'])
        px = float(np.mean(xs[[0, 5, 9, 13, 17]])); py = float(np.mean(ys[[0, 5, 9, 13, 17]]))
        mo, chuc = _ngon(xs, ys)
        ngang = abs(px - fx) / fh
        mieng = np.hypot(px - fx, py - (fy + 0.55 * fh)) / fh            # tay cầm mic / chạm cằm
        doc = (py - fy) / fh
        ranh = mieng >= T['mieng'] and T['doc'][0] <= doc <= T['doc'][1] and not (chuc and doc > T['buong'])
        hoat = (2 if (mo >= T['mo_min'] or ngang >= T['ngang_min']) else 1) if ranh else 0
        ben = 'trai' if px < fx else 'phai'
        ung[ben].append([round(px, 1), round(py, 1), round(ngang, 2), int(mo), int(hoat)])
    for b in ung:
        if ung[b]: out[b] = max(ung[b], key=lambda v: (v[4], v[2]))
    return out


def _mot_mask(a, m, ya, T):
    """dự phòng không có MediaPipe: điểm mặt nạ xa tâm mặt nhất trong dải ngực–hông (chỉ bắt DANG TAY)."""
    out = {'trai': None, 'phai': None}
    if not m or not a.any(): return out
    s = nguoi.M / C.W
    fx, fy, fh = (m[0] + m[2]) / 2, (m[1] + m[3]) / 2, max(1.0, m[3] - m[1])
    r0 = int(max(0, (fy + T['bang'][0] * fh - ya) * s)); r1 = int(min(nguoi.M, (fy + T['bang'][1] * fh - ya) * s))
    if r1 - r0 < 3: return out
    sub = a[r0:r1]; co = sub.any(1)
    if not co.any(): return out
    L = np.where(co, np.argmax(sub, 1), nguoi.M)
    R = np.where(co, nguoi.M - 1 - np.argmax(sub[:, ::-1], 1), -1)
    mx, mfh = fx * s, fh * s
    for ben in ('trai', 'phai'):
        if ben == 'trai': k = int(np.argmin(L)); x = float(L[k]); ext = (mx - x) / mfh; huong = 1
        else: k = int(np.argmax(R)); x = float(R[k]); ext = (x - mx) / mfh; huong = -1
        # NHÔ RA: hàng phía TRÊN điểm xa nhất phải lùi vào ≥ C.TAY['nho'] × cao mặt (khuỷu tay khép sát thân thì không)
        kt = r0 + k
        tren = a[max(0, int(kt - 1.2 * mfh)):max(0, int(kt - 0.6 * mfh))]
        tren = tren[tren.any(1)]
        if len(tren):
            xt = (np.argmax(tren, 1).min() if ben == 'trai' else (nguoi.M - 1 - np.argmax(tren[:, ::-1], 1)).max())
            nho = (xt - x) / mfh if ben == 'trai' else (x - xt) / mfh
        else: nho = 9.0
        dung = [j for j in range(max(0, k - int(0.35 * mfh)), min(len(L), k + int(0.35 * mfh) + 1))
                if co[j] and abs((L[j] if ben == 'trai' else R[j]) - x) < 0.45 * mfh]
        yk = float(np.mean(dung)) if dung else float(k)
        px = (x + huong * T['vao_long'] * mfh) / s; py = ya + (r0 + yk) / s
        hoat = ext >= T['nguong'] and nho >= T['nho']
        out[ben] = [round(float(px), 1), round(float(py), 1), round(float(ext), 2), 5 if hoat else 0, 2 if hoat else 0]
    return out


# ------------------------------------------------------------------ cả video
def _chay_mp(work, bao):
    py = venv_py()
    if not py: return None
    out = os.path.join(work, 'tay_mp.json')
    src = os.path.join(work, 'nguon.mp4')
    if not (os.path.exists(out) and os.path.getmtime(out) > os.path.getmtime(src)):
        if bao: print('  dò bàn tay MediaPipe (venv riêng)…', flush=True)
        env = dict(os.environ, PYTHONIOENCODING='utf-8', GLOG_minloglevel='2', TF_CPP_MIN_LOG_LEVEL='3')
        r = subprocess.run([py, '-X', 'utf8', os.path.join(os.path.dirname(os.path.abspath(__file__)), 'tay_mp.py'), src, out,
                            str(C.TAY['mp_buoc'])], capture_output=True, text=True, encoding='utf-8', errors='replace', env=env)
        if r.returncode != 0 or not os.path.exists(out):
            print('  ⚠ MediaPipe lỗi → dùng mặt nạ người', (r.stderr or '')[-400:])
            return None
    return C.doc_json(out)


def _doan(on, dt, T):
    doan, j = [], 0
    while j < len(on):
        if on[j]:
            k = j
            while k + 1 < len(on) and on[k + 1]: k += 1
            doan.append([j, k]); j = k + 1
        else: j += 1
    gop = []
    for d in doan:
        if gop and (d[0] - gop[-1][1]) * dt <= T['lap_s']: gop[-1][1] = d[1]
        else: gop.append(d)
    return [d for d in gop if (d[1] - d[0] + 1) * dt >= T['min_s']]


def _gom(ts, dt):
    """các mốc → [[t0, t1], …] (nhịp xoè / dang tay trong 1 đoạn)."""
    ra = []
    for t in ts:
        if ra and t - ra[-1][1] <= dt * 1.5: ra[-1][1] = t
        else: ra.append([t, t])
    return [[a, round(b + dt, 2)] for a, b in ra]


def _cat_theo_canh(cu_chi, cuts, words, T):
    """tách đoạn cử chỉ ở mỗi cú cắt nằm trong đoạn (sau cú cắt tay ở chỗ khác)."""
    ra = []
    for c in cu_chi:
        mocs = [c['t0']] + [t for t in cuts if c['t0'] + 0.05 < t < c['t1'] - 0.05] + [c['t1']]
        for a, b in zip(mocs, mocs[1:]):
            a, b = round(a + (0.05 if a != c['t0'] else 0), 2), round(b - (0.05 if b != c['t1'] else 0), 2)
            if b - a < T['min_s']: continue
            ra.append(dict(c, t0=a, t1=b, xoe=[[max(x0, a), min(x1, b)] for x0, x1 in c['xoe'] if x1 > a and x0 < b],
                           loi=_loi(words, a, b)))
    return ra


def _loi(words, t0, t1):
    return ' '.join(w['w'] for w in words if w['e'] > t0 and w['s'] < t1).strip()


def tinh(work, bao=True):
    """→ dict tay.json. None nếu chưa có cả MediaPipe lẫn mặt nạ người."""
    T = C.TAY
    n = int(round(C.probe(os.path.join(work, 'nguon.mp4'))['dur'] * C.FPS))
    mp_ = _chay_mp(work, bao)
    kh = {'trai': [], 'phai': []}
    if mp_:
        nguon, buoc = 'mediapipe', mp_['buoc']
        n = mp_.get('n') or n
        mats = nguoi.mat_theo_khung(work, n)
        for j, ds in enumerate(mp_['khung']):
            r = _mot_mp(ds, mats[min(j * buoc, n - 1)], T)
            for b in kh: kh[b].append(r[b])
    else:
        js_p, np_p = os.path.join(work, 'nguoi_mask.json'), os.path.join(work, 'nguoi_mask.npy')
        if not (os.path.exists(js_p) and os.path.exists(np_p)): return None
        js = C.doc_json(js_p)
        if not js.get('xong'): return None
        nguon, buoc = 'mat_na', js['buoc']
        arr = np.load(np_p, mmap_mode='r'); n, yas = js['n'], js['ya']
        mats = nguoi.mat_theo_khung(work, n)
        ker = np.ones((3, 3), np.uint8)
        for j in range(len(arr)):
            a = cv2.morphologyEx((arr[j] > 128).astype(np.uint8), cv2.MORPH_OPEN, ker).astype(bool)
            r = _mot_mask(a, mats[min(j * buoc, n - 1)], yas[j], T)
            for b in kh: kh[b].append(r[b])
    dt = buoc / C.FPS
    words = C.doc_json(os.path.join(work, 'words.json')) if os.path.exists(os.path.join(work, 'words.json')) else []
    cu_chi = []
    for ben, ds in kh.items():
        on = np.array([bool(d and d[4] >= 1) for d in ds])
        if len(on) >= 5:   # đa số trong 5 mốc (~0,33 s) — bỏ nhiễu 1 mốc
            pad = np.pad(on.astype(np.int8), 2, mode='edge')
            on = np.sum(np.stack([pad[k:k + len(on)] for k in range(5)]), 0) >= 3
        for j0, j1 in _doan(on, dt, T):
            dau = [ds[q] for q in range(j0, min(j1 + 1, j0 + int(0.3 / dt) + 1)) if ds[q] and ds[q][4]]
            if not dau: continue
            t0, t1 = round(j0 * dt, 2), round((j1 + 1) * dt, 2)
            xoe = [round(q * dt, 2) for q in range(j0, j1 + 1) if ds[q] and ds[q][4] == 2]
            cu_chi.append({'ben': ben, 't0': t0, 't1': t1,
                           'x': round(float(np.median([d[0] for d in dau])), 1), 'y': round(float(np.median([d[1] for d in dau])), 1),
                           'ext': round(max(d[2] for d in ds[j0:j1 + 1] if d), 2),
                           'mo': int(max(d[3] for d in ds[j0:j1 + 1] if d)), 'xoe': _gom(xoe, dt),
                           'loi': _loi(words, t0, t1)})
    cuts = [float(c['t']) for c in C.doc_json(os.path.join(work, 'cut.json'))] if os.path.exists(os.path.join(work, 'cut.json')) else []
    cu_chi = _cat_theo_canh(cu_chi, cuts, words, T)
    cu_chi.sort(key=lambda c: c['t0'])
    kq = {'phien': PHIEN, 'nguon': nguon, 'buoc': buoc, 'n': n, 'khung': kh, 'cu_chi': cu_chi}
    kq['goi_y'] = goi_y(kq, words)
    C.ghi_json(os.path.join(work, 'tay.json'), kq)
    if bao:
        tg = sum(c['t1'] - c['t0'] for c in cu_chi)
        print(f'  cử chỉ tay ({nguon}): {len(cu_chi)} đoạn, {tg:.1f} s' +
              ('' if cu_chi else ' — người nói không làm cử chỉ (cầm mic / tay sau lưng) → icon trượt từ mép vào'))
        for c in cu_chi:
            print(f"    {c['t0']:6.2f}–{c['t1']:6.2f} s  tay {c['ben']:4s}  ({c['x']:.0f}, {c['y']:.0f})  xoè/dang {len(c['xoe'])} nhịp"
                  f"  «{c['loi'][:40]}»")
        if kq['goi_y']:
            print(f"  icon gợi ý theo lời + cử chỉ: {len(kq['goi_y'])}")
            for g in kq['goi_y']:
                print(f"    {g['t0']:6.2f}–{g['t1']:6.2f} s  tay {g['ben']:4s}  {g['loai']:10s} «{g['nhan']}»")
    try:
        ve_to(work, kq)
    except Exception as ex:
        print('  ⚠ không vẽ được tay.jpg:', ex)
    return kq


def doc(work):
    """tay.json (tính nếu thiếu / phiên cũ, khi đã có MediaPipe hoặc mặt nạ)."""
    p = os.path.join(work, 'tay.json')
    if os.path.exists(p):
        kq = C.doc_json(p)
        if kq.get('phien') == PHIEN and (kq.get('nguon') == 'mediapipe' or not venv_py()): return kq
    return tinh(work, bao=False)


# ------------------------------------------------------------------ icon gợi ý từ lời
def goi_y(kq, words, cach=None):
    """từ khoá trong lời (C.ICON_TU) rơi vào lúc tay đang làm cử chỉ → icon {t0, t1, loai, nhan, ben, tu}."""
    if not kq or not words or not kq.get('cu_chi'): return []
    cach = C.TAY['goi_y_cach'] if cach is None else cach
    nfc = lambda s: re.sub(r'[^\w²]', '', unicodedata.normalize('NFC', s.lower()))
    tok = [nfc(w['w']) for w in words]
    bang = sorted(((cum.split(), loai, cum) for loai, ds in C.ICON_TU.items() for cum in ds), key=lambda x: -len(x[0]))
    bang = [([nfc(x) for x in ct], loai, cum) for ct, loai, cum in bang]
    ra, dung = [], set()
    for i in range(len(words)):
        if i in dung: continue
        for ct, loai, cum in bang:
            if tok[i:i + len(ct)] != ct: continue
            ts = float(words[i]['s'])
            if any(abs(g['t0'] - ts) < C.TAY['goi_y_min'] for g in ra): break
            ung = [c for c in (cu_chi_gan(kq, ts, b, truoc=0.3, sau=0.5) for b in ('trai', 'phai')) if c]
            ung = [c for c in ung if not any(g['ben'] == c['ben'] and abs(g['t0'] - ts) < cach for g in ra)]
            if not ung: break
            # tay đang XOÈ / DANG gần lúc nói chữ đó thì ưu tiên + bật đúng nhịp đó
            def nhip(c):
                xs = [a for a, b in c['xoe'] if ts - 0.4 <= a <= ts + 0.7] + [ts for a, b in c['xoe'] if a <= ts <= b]
                return min(xs, key=lambda a: abs(a - ts)) if xs else None
            ung.sort(key=lambda c: (nhip(c) is None, c['ben'] != 'phai'))
            cc = ung[0]; nx = nhip(cc)
            t0 = round(max(ts - 0.1 if nx is None else nx, cc['t0']), 2)
            t1 = round(min(cc['t1'], t0 + C.TAY['goi_y_dai'][1], words[-1]['e'] + 0.3), 2)
            if t1 - t0 < C.TAY['goi_y_dai'][0]:
                t0 = round(max(cc['t0'], t1 - C.TAY['goi_y_dai'][0]), 2)
            if t1 - t0 < 0.7: break
            nhan = ' '.join(re.sub(r'[.,!?…]+$', '', w['w']) for w in words[i:i + len(ct)])
            ra.append({'t0': t0, 't1': t1, 'loai': loai, 'nhan': nhan[:1].upper() + nhan[1:], 'ben': cc['ben'], 'tu': cum})
            dung.update(range(i, i + len(ct)))
            break
    return ra


def _chu_dang_hien(plan, t0, t1):
    """chữ to đang hiện trong [t0, t1]: tiêu đề (dẫn / khoá / viết tay), liệt kê, ô tìm kiếm — icon không lặp lại."""
    ra = []
    for td in plan.get('tieu_de', []):
        if td['t0'] < t1 and td['t1'] > t0: ra += [td.get('dan') or '', td.get('khoa') or '', td.get('viet_tay') or '']
    for lk in plan.get('liet_ke', []):
        if lk['t0'] < t1 and lk['t1'] > t0: ra += [lk.get('khoa') or ''] + [x.get('text', '') for x in lk.get('dong', [])]
    for tk in plan.get('tim_kiem', []):
        if tk['t0'] < t1 and tk['t1'] > t0: ra.append(tk.get('chu') or '')
    return unicodedata.normalize('NFC', ' '.join(ra).lower())


def gop_ke_hoach(plan, kq):
    """chép icon gợi ý vào kế hoạch: bỏ cái trùng giờ với icon / thẻ ảnh đã có, và cái có nhãn đang nằm sẵn trong tiêu đề /
    liệt kê / ô tìm kiếm cùng lúc (không lặp chữ). → số icon thêm"""
    da = [(float(x['t0']), float(x['t1'])) for k in ('icon', 'the_anh') for x in plan.get(k, [])]
    them = 0
    for g in (kq or {}).get('goi_y', []):
        if any(a < g['t1'] and b > g['t0'] for a, b in da): continue
        if unicodedata.normalize('NFC', g['nhan'].lower()) in _chu_dang_hien(plan, g['t0'] - 0.3, g['t1']): continue
        plan.setdefault('icon', []).append({k: g[k] for k in ('t0', 't1', 'loai', 'nhan', 'ben')})
        da.append((g['t0'], g['t1'])); them += 1
    plan['icon'] = sorted(plan.get('icon', []), key=lambda x: x['t0'])
    return them


# ------------------------------------------------------------------ ảnh soát
def ve_to(work, kq, rong=240):
    cc = kq['cu_chi'][:30]
    if not cc: return None
    src = os.path.join(work, 'nguon.mp4')
    oh = int(rong * C.H / C.W)
    fo = C.font('BeVietnamPro-Bold.ttf', 15)
    gy = {(g['ben'], round(g['t0'], 1)): g for g in kq.get('goi_y', [])}
    tiles = []
    for c in cc:
        t = c['t0'] + 0.15
        raw = subprocess.run(['ffmpeg', '-v', 'error', '-ss', f'{t:.3f}', '-i', src, '-frames:v', '1', '-f', 'rawvideo',
                              '-pix_fmt', 'rgb24', '-'], capture_output=True).stdout
        if len(raw) < C.W * C.H * 3: continue
        im = Image.fromarray(np.frombuffer(raw[:C.W * C.H * 3], np.uint8).reshape(C.H, C.W, 3))
        d = ImageDraw.Draw(im); r = 30
        d.ellipse((c['x'] - r, c['y'] - r, c['x'] + r, c['y'] + r), outline=(255, 220, 40), width=9)
        im = im.resize((rong, oh), Image.LANCZOS)
        o = Image.new('RGB', (rong, oh + 44), (18, 18, 18)); o.paste(im, (0, 44))
        dd = ImageDraw.Draw(o)
        dd.text((4, 3), f"{c['t0']:.2f}–{c['t1']:.2f}s tay {c['ben']}", font=fo, fill=(255, 220, 80))
        dd.text((4, 23), c['loi'][:30], font=fo, fill=(230, 230, 230))
        tiles.append(o)
    if not tiles: return None
    cot = min(8, len(tiles)); hang = (len(tiles) + cot - 1) // cot
    sh = Image.new('RGB', (cot * (rong + 4), hang * (oh + 48)), (8, 8, 8))
    for k, o in enumerate(tiles): sh.paste(o, ((k % cot) * (rong + 4), (k // cot) * (oh + 48)))
    p = os.path.join(work, 'tay.jpg'); sh.save(p, quality=88)
    return p


# ------------------------------------------------------------------ tra cứu cho dung.py / am_thanh.py / kiem.py
def diem(kq, i, ben, cua_so=6):
    """lòng bàn tay (nguồn) bên `ben` quanh khung i khi tay đang làm cử chỉ; None nếu không."""
    if not kq: return None
    ds = kq['khung'].get(ben) or []
    b = kq['buoc']; j = i // b; w = max(1, cua_so // b)
    can = [ds[q] for q in range(max(0, j - w), min(len(ds), j + w + 1)) if ds[q] and ds[q][4] >= 1]
    if not can: return None
    return float(np.median([d[0] for d in can])), float(np.median([d[1] for d in can]))


def cu_chi_gan(kq, t0, ben=None, truoc=None, sau=None):
    """đoạn cử chỉ phủ quanh t0 (đúng bên nếu cho `ben`)."""
    if not kq: return None
    truoc = C.TAY['truoc_s'] if truoc is None else truoc; sau = C.TAY['sau_s'] if sau is None else sau
    ung = [c for c in kq['cu_chi'] if (ben is None or c['ben'] == ben) and c['t0'] <= t0 + sau and c['t1'] >= t0 - truoc]
    return min(ung, key=lambda c: abs(max(c['t0'], min(t0, c['t1'])) - t0)) if ung else None


def gan(kq, t0, ben=None, cam=()):
    """chọn cử chỉ cho 1 đồ hoạ bắt đầu ở t0: đúng `ben` trước, rồi bên kia; bỏ bên đang có đồ hoạ khác (`cam`).
    → {'ben', 't0' (= lúc tay bắt đầu cử chỉ nếu muộn hơn t0), 'cc'} | None"""
    if not kq or not kq.get('cu_chi'): return None
    thu = [ben, 'phai' if ben == 'trai' else 'trai'] if ben in ('trai', 'phai') else ['trai', 'phai']
    ung = [c for c in (cu_chi_gan(kq, t0, b) for b in thu) if c and c['ben'] not in cam]
    if not ung: return None
    if ben not in ('trai', 'phai'): ung.sort(key=lambda c: abs(c['t0'] - t0))
    cc = ung[0]
    return {'ben': cc['ben'], 't0': round(max(float(t0), cc['t0']), 2), 'cc': cc}


def xep(plan, kq):
    """gán TAY cho icon + thẻ ảnh (theo thời gian, 1 tay giữ 1 đồ hoạ một lúc).
    → {('icon', k) | ('the_anh', k): {'ben', 't0', 'cc'}} — dung.py, am_thanh.py, kiem.py, duyet.py dùng chung."""
    out = {}
    if not kq or not kq.get('cu_chi'): return out
    viec = []
    for k, ic in enumerate(plan.get('icon', [])):
        if ic.get('tay', True) is False: continue
        viec.append(('icon', k, ic, ic.get('ben')))
    for k, th in enumerate(plan.get('the_anh', [])):
        tu = th.get('tu', 'tay_trai')
        if th.get('tay', True) is False or tu not in ('tay_trai', 'tay_phai', 'tay'): continue
        viec.append(('the_anh', k, th, {'tay_trai': 'trai', 'tay_phai': 'phai'}.get(tu)))
    viec.sort(key=lambda v: float(v[2]['t0']))
    chiem = []
    for loai, k, x, ben in viec:
        t0, t1 = float(x['t0']), float(x['t1'])
        cam = {b for b, a0, a1 in chiem if a0 < t1 and a1 > t0}
        r = gan(kq, t0, ben, cam)
        if not r: continue
        out[(loai, k)] = r
        chiem.append((r['ben'], r['t0'], t1))
    return out
