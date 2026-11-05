# -*- coding: utf-8 -*-
"""Bước 1 — đo + lập kế hoạch nháp.

Làm: Whisper large-v3 (mốc từng chữ) → cắt lặng sát như mẫu → dựng nguon.mp4 (1080x1920, 30 fps)
→ dò mặt người nói mỗi 0,2 s → quét tư liệu (ảnh/video dự án) ra bảng hình có nhãn
→ chia lời thành CỤM Ý → plan.json NHÁP (cảnh + cụm chữ + hiệu ứng) + bang_duyet.md.
Claude phải đọc lời + nhìn bảng tư liệu rồi SỬA plan.json theo nghĩa trước khi dựng.
"""
import os, re, shutil, subprocess, math
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import chung as C

PROMPT_BDS = ('Biệt thự, tầng hầm, dự án, phân khu, quy mô, hecta, mét vuông, chiết khấu, ân hạn gốc, '
              'vốn tự có, chủ đầu tư, layout, inbox, căn hộ, shophouse, Ecopark, Vinhomes, Masteri.')
SUA_TU = [('triết', 'chiết'), ('hecta', 'ha'), ('hectare', 'ha'), ('héc-ta', 'ha')]


# ---------------------------------------------------------------- Whisper
def nghe(wav, model='large-v3'):
    from faster_whisper import WhisperModel
    m = WhisperModel(model, device='cpu', compute_type='int8')
    # faster-whisper + PyAV mới lỗi `metadata_errors` khi tự mở file → tự đọc wav 16 kHz mono bằng `wave` rồi đưa mảng numpy
    import wave, numpy as np
    with wave.open(wav, 'rb') as wf:
        pcm = np.frombuffer(wf.readframes(wf.getnframes()), np.int16).astype(np.float32) / 32768.0
        if wf.getnchannels() > 1: pcm = pcm.reshape(-1, wf.getnchannels()).mean(1)
    segs, _ = m.transcribe(pcm, language='vi', word_timestamps=True, vad_filter=False, beam_size=5,
                           initial_prompt=PROMPT_BDS)
    words = []
    for s in segs:
        for w in s.words:
            t = w.word.strip()
            if not t: continue
            words.append({'w': t, 's': round(w.start, 3), 'e': round(w.end, 3), 'p': round(w.probability, 2)})
    # chặn từ phình (Whisper hay kéo dài chữ cuối câu)
    for i, w in enumerate(words):
        if w['e'] - w['s'] > 1.2: w['e'] = round(w['s'] + 0.6, 3)
        if i + 1 < len(words) and w['e'] > words[i + 1]['s']: w['e'] = words[i + 1]['s']
    return words


# ---------------------------------------------------------------- cắt lặng
def nang_luong(wav16k):
    """đường năng lượng 10 ms (lọc 200 Hz cho bỏ ù) + sàn ồn = phân vị 5."""
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', wav16k, '-ac', '1', '-ar', '16000', '-af', 'highpass=f=200',
                          '-f', 'f32le', '-'], capture_output=True).stdout
    x = np.frombuffer(raw, np.float32)
    n = 160; k = len(x) // n
    e = 20 * np.log10(np.sqrt((x[:k * n].reshape(k, n) ** 2).mean(1)) + 1e-9)
    return e, float(np.percentile(e, 5))


def doan_giu(wav16k, dur, cfg=C.CAT_LANG):
    """04/11: KHÔNG dựa mốc chữ Whisper (đã cắt mất hơi thở + đuôi chữ −7…−11 dB → user: "hụt hơi").
    Chỉ bỏ quãng IM THẬT (năng lượng < sàn ồn + nguong_db liên tục ≥ khe_toi_da), và luôn chừa giu_lai giây
    khoảng nghỉ (chia đôi trước/sau) để còn tiếng lấy hơi."""
    e, san = nang_luong(wav16k)
    im = e < san + cfg['nguong_db']
    runs, i = [], 0
    while i < len(im):
        if im[i]:
            j = i
            while j < len(im) and im[j]: j += 1
            runs.append((i * 0.01, j * 0.01)); i = j
        else:
            i += 1
    keep, cur, bo = [], 0.0, []
    for a, b in runs:
        dau, cuoi = a <= 0.02, b >= dur - 0.02
        giu = cfg['giu_dau_cuoi'] if (dau or cuoi) else cfg['giu_lai']
        if b - a < cfg['khe_toi_da'] or b - a <= giu: continue
        ca = a + (0 if dau else giu / 2); cb = b - (0 if cuoi else giu / 2)
        if dau: ca, cb = 0.0, b - giu
        if cuoi: ca, cb = a + giu, dur
        if cb - ca < 0.05: continue
        if ca > cur: keep.append([cur, ca])
        bo.append((round(ca, 2), round(cb, 2), round(float(e[int(ca * 100):max(int(ca * 100) + 1, int(cb * 100))].max()), 1)))
        cur = cb
    if cur < dur: keep.append([cur, dur])
    return keep or [[0.0, dur]], bo, san


def doi_moc(t, timemap):
    """t (giây file thô) → giây trên timeline đã cắt."""
    for a, b, d in timemap:
        if t < a: return d
        if t <= b: return d + (t - a)
    a, b, d = timemap[-1]
    return d + (b - a)


def dung_nguon(video, keep, out_mp4, out_wav, pr):
    """cắt + ghép frame-exact, quy về 1080x1920 30 fps phủ kín (crop giữa)."""
    vf = f'fps={C.FPS},scale={C.W}:{C.H}:force_original_aspect_ratio=increase,crop={C.W}:{C.H},setsar=1'
    parts, n = [], len(keep)
    for i, (a, b) in enumerate(keep):
        parts.append(f'[0:v]trim=start={a:.3f}:end={b:.3f},setpts=PTS-STARTPTS[v{i}]')
        fo = max(0.0, b - a - 0.015)
        parts.append(f'[0:a]atrim=start={a:.3f}:end={b:.3f},asetpts=PTS-STARTPTS,'
                     f'afade=t=in:d=0.015,afade=t=out:st={fo:.3f}:d=0.015[a{i}]')
    parts.append(''.join(f'[v{i}][a{i}]' for i in range(n)) + f'concat=n={n}:v=1:a=1[vc][ac]')
    parts.append(f'[vc]{vf}[vo]')
    parts.append(f'[ac]aresample={C.SR}[ao]')
    fc = ';'.join(parts)
    C.run(['ffmpeg', '-y', '-v', 'error', '-i', video, '-filter_complex', fc, '-map', '[vo]', '-map', '[ao]',
           '-c:v', 'libx264', '-crf', '15', '-preset', 'fast', '-pix_fmt', 'yuv420p',
           '-color_primaries', 'bt709', '-color_trc', 'bt709', '-colorspace', 'bt709',
           '-c:a', 'aac', '-b:a', '256k', out_mp4])
    C.run(['ffmpeg', '-y', '-v', 'error', '-i', out_mp4, '-vn', '-ac', '2', '-ar', str(C.SR), '-c:a', 'pcm_s16le', out_wav])


# ---------------------------------------------------------------- mặt người nói
def do_mat_haar(video, step=0.2):
    """dự phòng khi máy không có det_10g: Haar mặt chính diện của OpenCV (cần opencv < 5)."""
    import cv2
    casc = cv2.CascadeClassifier(os.path.join(cv2.data.haarcascades, 'haarcascade_frontalface_default.xml'))
    pr = C.probe(video)
    sw = 540; sh = int(round(pr['h'] * sw / pr['w']))
    p = subprocess.Popen(['ffmpeg', '-v', 'error', '-i', video, '-vf', f'fps=1/{step},scale={sw}:{sh}',
                          '-pix_fmt', 'gray', '-f', 'rawvideo', '-'], stdout=subprocess.PIPE)
    out, i, k = [], 0, C.W / sw
    while True:
        buf = p.stdout.read(sw * sh)
        if len(buf) < sw * sh: break
        g = np.frombuffer(buf, np.uint8).reshape(sh, sw)
        f = casc.detectMultiScale(g, scaleFactor=1.1, minNeighbors=5, minSize=(24, 24))
        mat = None
        if len(f):
            x, y, w, h = max(f, key=lambda r: r[2] * r[3])
            mat = [round(float(v * k)) for v in (x, y, x + w, y + h)]
        out.append({'t': round(i * step, 2), 'mat': mat}); i += 1
    p.stdout.close(); p.wait()
    return out


def do_mat(video, step=0.2):
    model = C.tim_model_mat()
    if model is None:
        print('  (không thấy det_10g.onnx — dùng Haar OpenCV để dò mặt)')
        return do_mat_haar(video, step)
    import onnxruntime as ort
    pr = C.probe(video)
    IN = 640; sc = IN / max(pr['w'], pr['h']); sw, sh = int(round(pr['w'] * sc)), int(round(pr['h'] * sc))
    sess = ort.InferenceSession(model, providers=['CPUExecutionProvider'])
    iname = sess.get_inputs()[0].name; onames = [o.name for o in sess.get_outputs()]
    strides, NA = [8, 16, 32], 2
    cen = {}
    for st in strides:
        hh = ww = IN // st; yy, xx = np.mgrid[:hh, :ww]
        cen[st] = np.repeat((np.stack([xx, yy], -1).astype(np.float32) * st).reshape(-1, 2), NA, axis=0)
    p = subprocess.Popen(['ffmpeg', '-v', 'error', '-i', video, '-vf', f'fps=1/{step},scale={sw}:{sh}',
                          '-pix_fmt', 'rgb24', '-f', 'rawvideo', '-'], stdout=subprocess.PIPE)
    out, i, k = [], 0, C.W / pr['w']
    while True:
        buf = p.stdout.read(sw * sh * 3)
        if len(buf) < sw * sh * 3: break
        img = np.frombuffer(buf, np.uint8).reshape(sh, sw, 3)
        pad = np.zeros((IN, IN, 3), np.uint8); pad[:sh, :sw] = img
        o = dict(zip(onames, sess.run(None, {iname: ((pad.astype(np.float32) - 127.5) / 128.0).transpose(2, 0, 1)[None]})))
        sk = sorted([n for n in onames if o[n].shape[1] == 1], key=lambda n: -o[n].shape[0])
        bk = sorted([n for n in onames if o[n].shape[1] == 4], key=lambda n: -o[n].shape[0])
        best = None
        for st, a, b in zip(strides, sk, bk):
            s_ = o[a].ravel(); d = o[b] * st; c = cen[st]; m = s_ >= 0.5
            for cc, dd in zip(c[m], d[m]):
                box = np.array([cc[0] - dd[0], cc[1] - dd[1], cc[0] + dd[2], cc[1] + dd[3]]) / sc
                area = (box[2] - box[0]) * (box[3] - box[1])
                if best is None or area > best[1]: best = (box, area)
        out.append({'t': round(i * step, 2), 'mat': [round(float(v * k)) for v in best[0]] if best is not None else None})
        i += 1
    p.stdout.close(); p.wait()
    return out


# ---------------------------------------------------------------- tư liệu
def quet_tu_lieu(res_dir, work):
    lst = []
    if not res_dir or not os.path.isdir(res_dir): return lst
    for f in sorted(os.listdir(res_dir)):
        p = os.path.join(res_dir, f); ext = os.path.splitext(f)[1].lower()
        if ext in C.IMG_EXT:
            im = Image.open(p); w, h = im.size
            lst.append({'file': f, 'loai': 'anh', 'w': w, 'h': h, 'huong': 'ngang' if w > h * 1.1 else ('doc' if h > w * 1.1 else 'vuong')})
        elif ext in C.VID_EXT:
            pr = C.probe(p)
            if 'w' not in pr: continue
            lst.append({'file': f, 'loai': 'video', 'w': pr['w'], 'h': pr['h'], 'dur': round(pr['dur'], 2),
                        'huong': 'ngang' if pr['w'] > pr['h'] * 1.1 else ('doc' if pr['h'] > pr['w'] * 1.1 else 'vuong')})
        elif ext in ('.mp3', '.wav', '.m4a', '.aac', '.flac'):
            lst.append({'file': f, 'loai': 'nhac', 'dur': round(C.probe(p)['dur'], 1)})
    # bảng hình có nhãn để Claude NHÌN khi gán tư liệu theo nghĩa
    tiles = []
    fo = ImageFont.truetype(C.font('BeVietnamPro-Bold.ttf'), 22)
    for i, a in enumerate(lst):
        if a['loai'] == 'nhac': continue
        p = os.path.join(res_dir, a['file'])
        if a['loai'] == 'anh':
            ims = [Image.open(p).convert('RGB')]
        else:
            ims = []
            for fr in (0.15, 0.5, 0.85):
                tmp = os.path.join(work, '_th.png')
                C.run(['ffmpeg', '-y', '-v', 'error', '-ss', f'{a["dur"] * fr:.2f}', '-i', p, '-frames:v', '1', tmp])
                ims.append(Image.open(tmp).convert('RGB'))
        th = 240
        row = [im.resize((max(1, int(im.width * th / im.height)), th)) for im in ims]
        tw = sum(r.width for r in row) + 4 * (len(row) - 1)
        t = Image.new('RGB', (max(tw, 300), th + 34), (24, 24, 24)); x = 0
        for r in row: t.paste(r, (x, 34)); x += r.width + 4
        d = ImageDraw.Draw(t)
        lab = f'[{i}] {a["file"]}  ({a["loai"]} {a["huong"]}' + (f' {a["dur"]}s)' if a['loai'] == 'video' else ')')
        d.text((6, 4), lab, font=fo, fill=(255, 230, 90))
        tiles.append(t)
    if tiles:
        Wmax = 2000; rows, cur, cw = [], [], 0
        for t in tiles:
            if cur and cw + t.width > Wmax: rows.append(cur); cur, cw = [], 0
            cur.append(t); cw += t.width + 8
        if cur: rows.append(cur)
        Ht = sum(max(t.height for t in r) + 8 for r in rows); Wt = max(sum(t.width + 8 for t in r) for r in rows)
        sheet = Image.new('RGB', (Wt, Ht), (10, 10, 10)); y = 0
        for r in rows:
            x = 0
            for t in r: sheet.paste(t, (x, y)); x += t.width + 8
            y += max(t.height for t in r) + 8
        sheet.save(os.path.join(work, 'tu_lieu_sheet.jpg'), quality=88)
    return lst


# ---------------------------------------------------------------- chia cụm ý
SO_RE = re.compile(r'(\d+(?:[.,]\d+)?)\s*(tỷ|tỉ|triệu|ha|hecta|hectare|%|phần trăm|m2|m²|mét vuông|căn|tháng|năm|km|phút)?', re.I)


def chuan_so(words):
    """gộp '4' ',5' → '4,5'; '25' '%' → '25%'."""
    out = []
    for w in words:
        t = w['w']
        if out and re.fullmatch(r'[.,]\d+', t) and re.search(r'\d$', out[-1]['w']):
            out[-1] = dict(out[-1], w=out[-1]['w'] + t, e=w['e']); continue
        if out and t == '%' and re.search(r'\d$', out[-1]['w']):
            out[-1] = dict(out[-1], w=out[-1]['w'] + '%', e=w['e']); continue
        out.append(dict(w))
    return out


def chia_cau(words):
    cau, cur = [], []
    for w in words:
        cur.append(w)
        if re.search(r'[.?!]$', w['w']): cau.append(cur); cur = []
    if cur: cau.append(cur)
    return cau


def chia_cum(cau):
    cum = []
    for c in cau:
        dur = c[-1]['e'] - c[0]['s']
        if dur <= C.NHIP['cum_toi_da']:
            cum.append(c); continue
        n = max(2, math.ceil(dur / 2.8))
        tgt = [c[0]['s'] + dur * k / n for k in range(1, n)]
        cuts = []
        for tt in tgt:   # ưu tiên ranh dấu phẩy gần mốc
            best = min(range(1, len(c)), key=lambda i: abs(c[i]['s'] - tt) - (0.6 if re.search(r',$', c[i - 1]['w']) else 0))
            if best not in cuts: cuts.append(best)
        cuts = sorted(cuts); prev = 0
        for k in cuts + [len(c)]:
            if k - prev >= 1: cum.append(c[prev:k]); prev = k
    # gộp cụm quá ngắn vào cụm trước
    out = []
    for c in cum:
        if out and c[-1]['e'] - c[0]['s'] < C.NHIP['cum_toi_thieu'] and not re.search(r'[.?!]$', out[-1][-1]['w']):
            out[-1] = out[-1] + c
        else:
            out.append(c)
    return out


def sach(t):
    return re.sub(r'[.,?!]+$', '', t)


def nhap_chu(cum, t_cat):
    """cụm chữ NHÁP theo luật đơn giản — Claude phải viết lại theo nghĩa."""
    ws = [dict(w, w=sach(w['w'])) for w in cum]
    txt = ' '.join(w['w'] for w in ws)
    so_idx = next((i for i, w in enumerate(ws) if re.match(r'\d', w['w'])), None)
    dong = []
    tt = lambda i: round(max(t_cat + 0.05, ws[i]['s'] - 0.1), 2)
    if so_idx is not None:
        j = so_idx + 1
        key = ws[so_idx]['w']
        if j < len(ws) and re.fullmatch(r'(tỷ|tỉ|triệu|ha|hecta|hectare|căn|tháng|%|m2)', ws[j]['w'], re.I):
            u = ws[j]['w'].lower(); u = {'tỷ': 'Tỷ', 'tỉ': 'Tỷ', 'triệu': 'Triệu', 'hecta': 'ha', 'hectare': 'ha'}.get(u, u)
            key += ('' if u == '%' else ' ') + u; j += 1
        a = max(0, so_idx - 3)
        if so_idx > a: dong.append({'text': ' '.join(w['w'] for w in ws[a:so_idx]), 'vai': 'dan', 't': tt(a)})
        dong.append({'text': key, 'vai': 'so', 't': tt(so_idx), 'vao': 'roi' if '%' in key or 'Tỷ' in key else 'go'})
        if j < len(ws): dong.append({'text': ' '.join(w['w'] for w in ws[j:j + 4]), 'vai': 'chu_thich', 't': tt(j)})
    else:
        n = len(ws)
        a = min(3, max(1, n // 3))
        dong.append({'text': ' '.join(w['w'] for w in ws[:a]), 'vai': 'dan', 't': tt(0)})
        b = min(n, a + 3)
        dong.append({'text': ' '.join(w['w'] for w in ws[a:b]), 'vai': 'nhan', 't': tt(a)})
        if b < n: dong.append({'text': ' '.join(w['w'] for w in ws[b:b + 3]), 'vai': 'viet_tay', 't': tt(b)})
    return {'dong': dong, 'loi': txt}


# ---------------------------------------------------------------- plan nháp
def lap_plan(words, tu_lieu, dur, ten, nhac):
    cau = chia_cau(words)
    cum = chia_cum(cau)
    if not cum: raise SystemExit('Không nghe được lời nào.')
    # hook = các câu đầu đến khi ≥ 8 s (kết ở ranh câu); CTA = câu cuối
    hook_end = 0
    for i, c in enumerate(cum):
        if re.search(r'[.?!]$', c[-1]['w']) and c[-1]['e'] >= C.NHIP['hook_toi_thieu']:
            hook_end = i + 1; break
    hook_end = max(1, min(hook_end or 2, len(cum) - 2))
    cta_i = len(cum) - 1
    hinh = [a for a in tu_lieu if a['loai'] in ('anh', 'video')]
    canh = []

    def t_cat(i):
        return 0.0 if i == 0 else round(cum[i][0]['s'] + C.NHIP['cat_tre'], 2)

    # cảnh hook
    hook = {'id': 1, 'loai': 'noi', 't0': 0.0, 't1': t_cat(hook_end), 'loi': ' '.join(w['w'] for c in cum[:hook_end] for w in c),
            'chu': [], 'hieu_ung': [{'kieu': 'phong_lui', 't': 0.0}], 'toi_tren': True}
    for k in range(hook_end):
        b = nhap_chu(cum[k], t_cat(k))
        if k == 0:
            b['dong'] = [{'text': sach(b['loi']), 'vai': 'cau_hoi', 't': round(max(0.05, cum[0][0]['s']), 2)}]
        hook['chu'].append({'t1': round((t_cat(k + 1) if k + 1 < hook_end else hook['t1']) - C.CHU['tat_truoc_cat'], 2),
                            'y': 300, **b})
    if hook_end >= 2:
        hook['hieu_ung'].append({'kieu': 'phong_nhanh', 't': round(cum[1][0]['s'], 2)})
    hook['hieu_ung'].append({'kieu': 'nhan_ban', 't': round(hook['t1'] - 0.23, 2)})
    canh.append(hook)
    # cảnh giữa
    k_tl = 0
    for i in range(hook_end, cta_i):
        a = hinh[k_tl % len(hinh)] if hinh else None; k_tl += 1
        b = nhap_chu(cum[i], t_cat(i))
        co_so = any(d['vai'] == 'so' for d in b['dong'])
        if a is None: loai = 'noi'
        elif a['loai'] == 'video': loai = 'video'
        elif a['huong'] == 'ngang' and co_so: loai = 'the_mo'
        else: loai = 'anh'
        c = {'id': len(canh) + 1, 'loai': loai, 't0': t_cat(i), 't1': t_cat(i + 1), 'loi': b['loi'],
             'chu': [{'t1': round(t_cat(i + 1) - C.CHU['tat_truoc_cat'], 2), 'y': 300 if loai != 'the_mo' else 330, **b}],
             'hieu_ung': []}
        if a: c['nguon'] = a['file']
        if loai == 'video': c.update(ss=0.0, speed=1.0)
        canh.append(c)
    # CTA
    cta = {'id': len(canh) + 1, 'loai': 'noi', 't0': t_cat(cta_i), 't1': round(dur, 2), 'loi': ' '.join(w['w'] for w in cum[cta_i]),
           'chu': [{'t1': round(dur - 0.02, 2), 'y': 520, 'ra': 'giu', 'dong': [
               {'text': 'Inbox ngay nhận layout chi tiết', 'vai': 'dan', 't': round(cum[cta_i][0]['s'] + 0.2, 2)},
               {'text': ten or 'TÊN NGƯỜI NÓI', 'vai': 'ten', 't': round(cum[cta_i][0]['s'] + 0.5, 2), 'vao': 'nhay'},
               {'text': 'Biệt thự đẹp nhất', 'vai': 'viet_tay', 't': round(cum[cta_i][0]['s'] + 1.2, 2)}]}],
           'hieu_ung': [], 'toi_tren': True}
    canh.append(cta)
    chuyen = [{'t': cta['t0'], 'kieu': 'loe_cam'}]
    mid = [c for c in canh[1:-1]]
    if len(mid) >= 4: chuyen.append({'t': mid[len(mid) // 2]['t0'], 'kieu': 'loe_cam'})
    return {'phien_ban': 1, 'ten': ten, 'nhac': nhac, 'sub_nho': True, 'nhoe': False, 'dur': round(dur, 2),
            'canh': canh, 'chuyen': chuyen, 'CAN_CLAUDE_SUA': True}


def bang_duyet(plan, path):
    L = ['| # | thời gian | lời | cảnh | nguồn | chữ | hiệu ứng |', '|---|---|---|---|---|---|---|']
    for c in plan['canh']:
        chu = ' ⏎ '.join('; '.join(f"{d['vai']}:{d['text']}" for d in b['dong']) for b in c.get('chu', []))
        hu = ', '.join(h['kieu'] for h in c.get('hieu_ung', []))
        L.append(f"| {c['id']} | {c['t0']:.2f}–{c['t1']:.2f} | {c.get('loi', '')[:90]} | {c['loai']} | {c.get('nguon', '')} | {chu} | {hu} |")
    L.append('')
    L.append('Chuyển cảnh đặc biệt: ' + ', '.join(f"{x['kieu']}@{x['t']}" for x in plan.get('chuyen', [])))
    L.append(f"Nhạc nền: {plan.get('nhac') or 'KHÔNG'} · sub nhỏ: {plan.get('sub_nho')} · nhoè đúng mẫu: {plan.get('nhoe')}")
    with open(path, 'w', encoding='utf-8') as f: f.write('\n'.join(L))
    return '\n'.join(L)


def main(video, res_dir, work, ten=None, nhac=None, cat_lang=True, model='large-v3'):
    os.makedirs(work, exist_ok=True)
    pr = C.probe(video)
    print(f'Nguồn: {video}  {pr.get("w")}x{pr.get("h")} {pr["dur"]:.2f}s')
    raw_wav = os.path.join(work, 'tho.wav')
    C.run(['ffmpeg', '-y', '-v', 'error', '-i', video, '-vn', '-ac', '1', '-ar', '16000', raw_wav])
    words_raw = os.path.join(work, 'words_tho.json')
    if os.path.exists(words_raw): words = C.doc_json(words_raw)
    else:
        print('Nhận lời (Whisper large-v3, CPU)…'); words = nghe(raw_wav, model); C.ghi_json(words_raw, words)
    if cat_lang:
        keep, bo, san = doan_giu(raw_wav, pr['dur'])
        print(f'Sàn ồn {san:.1f} dB · bỏ {len(bo)} quãng im thật: ' + ', '.join(f'{a}–{b}s (đỉnh {p} dB)' for a, b, p in bo))
    else:
        keep = [[0.0, pr['dur']]]
        print('KHÔNG cắt lặng (video đã dựng sẵn / user chọn ở D6)')
    timemap, d = [], 0.0
    for a, b in keep: timemap.append((a, b, d)); d += b - a
    print(f'Cắt lặng: {pr["dur"]:.2f}s → {d:.2f}s ({len(keep)} đoạn giữ)')
    C.ghi_json(os.path.join(work, 'cat_lang.json'), {'cat': cat_lang, 'keep': keep})
    nguon = os.path.join(work, 'nguon.mp4'); giong = os.path.join(work, 'giong.wav')
    dung_nguon(video, keep, nguon, giong, pr)
    dur = C.probe(nguon)['dur']
    words2 = [dict(w, s=round(doi_moc(w['s'], timemap), 3), e=round(doi_moc(w['e'], timemap), 3)) for w in words]
    words2 = chuan_so(words2)
    C.ghi_json(os.path.join(work, 'words.json'), words2)
    C.ghi_json(os.path.join(work, 'timemap.json'), {'keep': keep, 'map': timemap})
    print('Dò mặt người nói…'); C.ghi_json(os.path.join(work, 'mat.json'), do_mat(nguon))
    tu_lieu = quet_tu_lieu(res_dir, work); C.ghi_json(os.path.join(work, 'tu_lieu.json'), tu_lieu)
    if not nhac:
        nh = [a for a in tu_lieu if a['loai'] == 'nhac']
        if nh: nhac = os.path.join(res_dir, nh[0]['file'])
    plan = lap_plan(words2, tu_lieu, dur, ten, nhac)
    plan.update(video=os.path.abspath(video), resources=os.path.abspath(res_dir) if res_dir else None)
    C.ghi_json(os.path.join(work, 'plan.json'), plan)
    print(bang_duyet(plan, os.path.join(work, 'bang_duyet.md')))
    print('\nLời đã nghe (đã cắt lặng):')
    for c in chia_cau(words2):
        print(f"  {c[0]['s']:6.2f}–{c[-1]['e']:6.2f}  " + ' '.join(w['w'] for w in c))
    return plan
