# -*- coding: utf-8 -*-
"""Bước 1 — đo + kế hoạch NHÁP.

video thô người nói → (cắt lặng theo năng lượng nếu quay thô) → nguon.mp4 1080x1920/30 + giong.wav
→ Whisper large-v3 (mốc từng chữ) → dò mặt mỗi 0,2 s → dò cú cắt (đổi bối cảnh / nhảy) → quét Resources
→ ke_hoach.json NHÁP theo NGỮ PHÁP mẫu (mỗi câu = 1 tiêu đề 3 tầng + sub cụm ở ngực + đồ hoạ theo từ khoá)
+ loi_doc.txt + tai_nguyen.jpg. Claude PHẢI sửa ke_hoach.json theo NGHĨA trước khi dựng."""
import os, re, subprocess, math, shutil
import numpy as np
from PIL import Image, ImageDraw
import chung as C

PROMPT = ('Bất động sản, dự án, căn hộ, biệt thự, liền kề, shophouse, mặt bằng, bảng giá, vị trí, tiện ích, pháp lý, '
          'sổ hồng, chủ đầu tư, tư vấn, mét vuông, tỷ, triệu, Vinhomes, Masteri, Ecopark, sale.')
# câu ảo giác quen thuộc của Whisper tiếng Việt (học từ phụ đề YouTube) — gặp là bỏ cả đoạn
AO_GIAC = re.compile(r'subscribe|Ghiền Mì Gõ|đăng ký kênh|like và share|bấm chuông|Hẹn gặp lại các bạn trong',
                     re.IGNORECASE)
TU_DAN = set('khi và vậy nhưng đó là bởi vì những các một nếu còn hãy bạn tôi anh chị em mình họ này với có cho để thì mà '
             'nên ai gì điều đã đang sẽ rất cũng lại chỉ mới hay hoặc thật tại ở trong ngay chính đây kia ấy'.split())


# ------------------------------------------------------------------ âm thanh / cắt lặng (giữ hơi thở)
def nang_luong(wav):
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', wav, '-ac', '1', '-ar', '16000', '-af', 'highpass=f=200',
                          '-f', 'f32le', '-'], capture_output=True).stdout
    x = np.frombuffer(raw, np.float32)
    n = 160; k = len(x) // n
    e = 20 * np.log10(np.sqrt((x[:k * n].reshape(k, n) ** 2).mean(1)) + 1e-9)
    return e, float(np.percentile(e, 5))


def doan_giu(wav, dur, cfg=C.CAT_LANG):
    e, san = nang_luong(wav)
    im = e < san + cfg['nguong_db']
    runs, i = [], 0
    while i < len(im):
        if im[i]:
            j = i
            while j < len(im) and im[j]: j += 1
            runs.append((i * 0.01, j * 0.01)); i = j
        else: i += 1
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
        bo.append((round(ca, 2), round(cb, 2)))
        cur = cb
    if cur < dur: keep.append([cur, dur])
    return keep or [[0.0, dur]], bo


def dung_nguon(video, keep, out_mp4, out_wav):
    vf = (f'fps={C.FPS},scale={C.W}:{C.H}:force_original_aspect_ratio=increase:flags=lanczos,crop={C.W}:{C.H},setsar=1')
    parts, n = [], len(keep)
    for i, (a, b) in enumerate(keep):
        parts.append(f'[0:v]trim=start={a:.3f}:end={b:.3f},setpts=PTS-STARTPTS[v{i}]')
        fo = max(0.0, b - a - 0.015)
        parts.append(f'[0:a]atrim=start={a:.3f}:end={b:.3f},asetpts=PTS-STARTPTS,'
                     f'afade=t=in:d=0.015,afade=t=out:st={fo:.3f}:d=0.015[a{i}]')
    parts.append(''.join(f'[v{i}][a{i}]' for i in range(n)) + f'concat=n={n}:v=1:a=1[vc][ac]')
    parts.append(f'[vc]{vf}[vo]'); parts.append(f'[ac]aresample={C.SR}[ao]')
    C.run(['ffmpeg', '-y', '-v', 'error', '-i', video, '-filter_complex', ';'.join(parts), '-map', '[vo]', '-map', '[ao]',
           '-c:v', 'libx264', '-crf', '14', '-preset', 'fast', '-pix_fmt', 'yuv420p',
           '-color_primaries', 'bt709', '-color_trc', 'bt709', '-colorspace', 'bt709', '-c:a', 'aac', '-b:a', '256k', out_mp4])
    C.run(['ffmpeg', '-y', '-v', 'error', '-i', out_mp4, '-vn', '-ac', '2', '-ar', str(C.SR), '-c:a', 'pcm_s16le', out_wav])


# ------------------------------------------------------------------ Whisper
def nghe(wav, prompt):
    from faster_whisper import WhisperModel
    import wave
    tmp = wav + '.16k.wav'
    # highpass 90 Hz bỏ ù gió / bước chân; hạ 8 dB vì mic cài áo hay nén sát 0 dBFS (Test.mp4 −9,8 LUFS)
    C.run(['ffmpeg', '-y', '-v', 'error', '-i', wav, '-ac', '1', '-ar', '16000', '-af', 'highpass=f=90,volume=-8dB',
           '-c:a', 'pcm_s16le', tmp])
    with wave.open(tmp, 'rb') as wf:
        pcm = np.frombuffer(wf.readframes(wf.getnframes()), np.int16).astype(np.float32) / 32768.0
    os.remove(tmp)
    m = WhisperModel('large-v3', device='cpu', compute_type='int8')
    # vad + KHÔNG nối ngữ cảnh: file dài nói liền (tour nhà mẫu 135 s) mà nối ngữ cảnh thì Whisper rơi vào vòng ảo giác
    # "Hãy subscribe cho kênh Ghiền Mì Gõ…" suốt video (75 chữ / 135 s) — thử 12/11/2026: cách này ra đúng lời, nhanh gấp 2
    segs, _ = m.transcribe(pcm, language='vi', word_timestamps=True, vad_filter=True,
                           vad_parameters=dict(min_silence_duration_ms=500, speech_pad_ms=300),
                           condition_on_previous_text=False, beam_size=5, initial_prompt=prompt)
    words = []
    for s in segs:
        if AO_GIAC.search(s.text): continue
        for w in s.words:
            t = w.word.strip()
            if t: words.append({'w': t, 's': round(w.start, 3), 'e': round(w.end, 3), 'p': round(w.probability, 2)})
    for i, w in enumerate(words):
        if w['e'] - w['s'] > 1.2: w['e'] = round(w['s'] + 0.6, 3)
        if i + 1 < len(words) and w['e'] > words[i + 1]['s']: w['e'] = words[i + 1]['s']
    return words


# ------------------------------------------------------------------ mặt
def do_mat(video, step=0.2):
    import cv2
    model = C.tim_model_mat()
    pr = C.probe(video)
    if model:
        import onnxruntime as ort
        IN = 640; sc = IN / max(pr['w'], pr['h']); sw, sh = int(round(pr['w'] * sc)), int(round(pr['h'] * sc))
        sess = ort.InferenceSession(model, providers=['CPUExecutionProvider'])
        iname = sess.get_inputs()[0].name; onames = [o.name for o in sess.get_outputs()]
        strides, NA = [8, 16, 32], 2; cen = {}
        for st in strides:
            hh = ww = IN // st; yy, xx = np.mgrid[:hh, :ww]
            cen[st] = np.repeat((np.stack([xx, yy], -1).astype(np.float32) * st).reshape(-1, 2), NA, axis=0)
        p = subprocess.Popen(['ffmpeg', '-v', 'error', '-i', video, '-vf', f'fps=1/{step},scale={sw}:{sh}',
                              '-pix_fmt', 'rgb24', '-f', 'rawvideo', '-'], stdout=subprocess.PIPE)
        out, i = [], 0
        while True:
            buf = p.stdout.read(sw * sh * 3)
            if len(buf) < sw * sh * 3: break
            img = np.frombuffer(buf, np.uint8).reshape(sh, sw, 3)
            pad = np.zeros((IN, IN, 3), np.uint8); pad[:sh, :sw] = img
            o = dict(zip(onames, sess.run(None, {iname: ((pad.astype(np.float32) - 127.5) / 128.0).transpose(2, 0, 1)[None]})))
            sk = sorted([n for n in onames if o[n].shape[1] == 1], key=lambda n: -o[n].shape[0])
            bk = sorted([n for n in onames if o[n].shape[1] == 4], key=lambda n: -o[n].shape[0])
            ung = []
            for st, a, b in zip(strides, sk, bk):
                s_ = o[a].ravel(); d = o[b] * st; c = cen[st]; mm = s_ >= 0.5
                for sc_, cc, dd in zip(s_[mm], c[mm], d[mm]):
                    ung.append((float(sc_), [round(float(v)) for v in np.array([cc[0] - dd[0], cc[1] - dd[1], cc[0] + dd[2], cc[1] + dd[3]]) / sc]))
            out.append({'t': round(i * step, 2), 'ung': _nms(ung)}); i += 1
        p.stdout.close(); p.wait()
        return out, 'det_10g'
    casc = cv2.CascadeClassifier(os.path.join(cv2.data.haarcascades, 'haarcascade_frontalface_default.xml'))
    sw = 540; sh = int(round(pr['h'] * sw / pr['w'])); k = pr['w'] / sw
    p = subprocess.Popen(['ffmpeg', '-v', 'error', '-i', video, '-vf', f'fps=1/{step},scale={sw}:{sh}',
                          '-pix_fmt', 'gray', '-f', 'rawvideo', '-'], stdout=subprocess.PIPE)
    out, i = [], 0
    while True:
        buf = p.stdout.read(sw * sh)
        if len(buf) < sw * sh: break
        g = np.frombuffer(buf, np.uint8).reshape(sh, sw)
        f = casc.detectMultiScale(g, scaleFactor=1.1, minNeighbors=5, minSize=(22, 22))
        ung = [[round(float(v * k)) for v in (x, y, x + w, y + h)] for x, y, w, h in f]
        out.append({'t': round(i * step, 2), 'ung': ung}); i += 1
    p.stdout.close(); p.wait()
    return out, 'haar'


def _nms(ung, iou=0.4):
    ung = sorted(ung, key=lambda x: -x[0]); giu = []
    for sc, b in ung:
        ok = True
        for g in giu:
            ix = max(0, min(b[2], g[2]) - max(b[0], g[0])) * max(0, min(b[3], g[3]) - max(b[1], g[1]))
            u = (b[2] - b[0]) * (b[3] - b[1]) + (g[2] - g[0]) * (g[3] - g[1]) - ix
            if u > 0 and ix / u > iou: ok = False; break
        if ok: giu.append(b)
    return giu


def chon_mat(ds, ranh, cua_so=3.0):
    """chọn mặt NGƯỜI NÓI trong các ứng viên: ứng viên lặp lại đều trong ±3 s cùng cảnh thắng (ứng viên sai
    của Haar thường lẻ tẻ / nhảy chỗ). Mẫu không có ứng viên đủ tin → None (lam_muot_mat lấp)."""
    def canh(t):
        return sum(1 for r in ranh if r <= t)
    for d in ds:
        d['canh'] = canh(d['t'])
    for i, d in enumerate(ds):
        cs = d.get('ung') or []
        if not cs: d['mat'] = None; continue
        win = [e for e in ds if e['canh'] == d['canh'] and abs(e['t'] - d['t']) <= cua_so]
        best, bs = None, -1.0
        for c in cs:
            w = c[2] - c[0]; cx, cy = (c[0] + c[2]) / 2, (c[1] + c[3]) / 2; n = 0
            for e in win:
                for c2 in e.get('ung') or []:
                    w2 = c2[2] - c2[0]
                    if 0.6 < w2 / max(1, w) < 1.6 and math.hypot((c2[0] + c2[2]) / 2 - cx, (c2[1] + c2[3]) / 2 - cy) < 0.6 * max(w, w2):
                        n += 1; break
            sc = n + w * 1e-4
            if sc > bs: best, bs = c, sc
        d['mat'] = best if bs >= max(2, 0.3 * len(win)) else None
    for d in ds:
        d.pop('canh', None)
    return ds


def lam_muot_mat(ds):
    """lọc trung vị 5 mẫu + lấp chỗ trống bằng mẫu gần nhất (mặt quay đi / mờ)."""
    ok = [i for i, d in enumerate(ds) if d['mat']]
    if not ok: return ds
    arr = np.array([ds[i]['mat'] for i in ok], np.float32)
    for j in range(len(ok)):
        a, b = max(0, j - 2), min(len(ok), j + 3)
        ds[ok[j]]['mat'] = [round(float(v)) for v in np.median(arr[a:b], 0)]
    for i, d in enumerate(ds):
        if not d['mat']:
            k = min(ok, key=lambda q: abs(q - i)); d['mat'] = list(ds[k]['mat']); d['doan'] = True
    return ds


# ------------------------------------------------------------------ cú cắt
def do_cat(video, nhay_tu_cat_lang):
    """'boi_canh' = đổi bối cảnh (điểm scene cao) → chuyển cảnh hiệu ứng; 'nhay' = cùng chỗ (jump cut) → đổi zoom."""
    r = subprocess.run(['ffmpeg', '-hide_banner', '-i', video, '-vf', "scale=270:480,select='gte(scene,0)',metadata=print",
                        '-an', '-f', 'null', '-'], capture_output=True, text=True, encoding='utf-8', errors='replace')
    ts, ss, t = [], [], None
    for line in r.stderr.splitlines():
        m = re.search(r'pts_time:([\d.]+)', line)
        if m: t = float(m.group(1)); continue
        m = re.search(r'scene_score=([\d.]+)', line)
        if m and t is not None:
            ts.append(t); ss.append(float(m.group(1))); t = None
    ts, ss = np.array(ts), np.array(ss)
    # cú cắt = ĐỈNH NHỌN so với nền ±1,5 s (p90, bỏ ±2 khung quanh nó) — máy quay cầm tay đi bộ (tour nhà mẫu) cho điểm
    # 0,10–0,25 liên tục ⇒ ngưỡng cứng 0,10 bắt nhầm 100 "cú nhảy" / 135 s; video đứng yên nền ~0,005 nên jump cut 0,10 vẫn qua
    cuts = []
    for i in np.where(ss >= 0.10)[0]:
        lo, hi = np.searchsorted(ts, ts[i] - 1.5), np.searchsorted(ts, ts[i] + 1.5)
        idx = [j for j in range(lo, hi) if abs(j - i) > 2]
        nen = float(np.percentile(ss[idx], 90)) if idx else 0.0
        s = float(ss[i])
        if s >= max(0.10, 2.5 * nen) and s >= ss[max(0, i - 3):i + 4].max():
            cuts.append({'t': round(float(ts[i]), 3), 'diem': round(s, 3), 'loai': 'boi_canh' if s >= 0.32 else 'nhay'})
    for t in nhay_tu_cat_lang:
        if not any(abs(c['t'] - t) < 0.12 for c in cuts):
            cuts.append({'t': round(t, 3), 'diem': 0, 'loai': 'nhay'})
    cuts.sort(key=lambda c: c['t'])
    out = []
    for c in cuts:                       # gộp cú cắt sát nhau
        if out and c['t'] - out[-1]['t'] < 0.5:
            if c['diem'] > out[-1]['diem']: out[-1] = c
            continue
        out.append(c)
    return [c for c in out if c['t'] > 0.3]


# ------------------------------------------------------------------ Resources
def quet_tai_nguyen(res, work):
    lst = []
    if res and os.path.isdir(res):
        for f in sorted(os.listdir(res)):
            p = os.path.join(res, f); ext = os.path.splitext(f)[1].lower()
            if ext in C.IMG_EXT:
                try:
                    im = Image.open(p); w, h = im.size
                except Exception: continue
                lst.append({'file': p, 'ten': f, 'loai': 'logo' if 'logo' in f.lower() else 'anh', 'w': w, 'h': h})
            elif ext in C.VID_EXT:
                pr = C.probe(p)
                if 'w' in pr: lst.append({'file': p, 'ten': f, 'loai': 'video', 'w': pr['w'], 'h': pr['h'], 'dur': round(pr['dur'], 1)})
            elif ext in C.AUD_EXT:
                lst.append({'file': p, 'ten': f, 'loai': 'nhac', 'dur': round(C.probe(p)['dur'], 1)})
    import ve
    tiles = []
    fo = C.font('BeVietnamPro-Bold.ttf', 22)
    for i, a in enumerate(lst):
        if a['loai'] == 'nhac': continue
        try:
            im = ve.doc_anh_nguon(a['file'])
        except Exception: continue
        th = 260; im = im.resize((max(1, int(im.width * th / im.height)), th))
        t = Image.new('RGB', (max(im.width, 320), th + 34), (24, 24, 24)); t.paste(im, (0, 34))
        ImageDraw.Draw(t).text((6, 5), f'[{i}] {a["ten"]} ({a["loai"]})', font=fo, fill=(255, 230, 90))
        tiles.append(t)
    if tiles:
        Wm = 2000; rows, cur, cw = [], [], 0
        for t in tiles:
            if cur and cw + t.width > Wm: rows.append(cur); cur, cw = [], 0
            cur.append(t); cw += t.width + 8
        if cur: rows.append(cur)
        Ht = sum(max(t.height for t in r) + 8 for r in rows); Wt = max(sum(t.width + 8 for t in r) for r in rows)
        sh = Image.new('RGB', (Wt, Ht), (10, 10, 10)); y = 0
        for r in rows:
            x = 0
            for t in r: sh.paste(t, (x, y)); x += t.width + 8
            y += max(t.height for t in r) + 8
        sh.save(os.path.join(work, 'tai_nguyen.jpg'), quality=88)
    return lst


# ------------------------------------------------------------------ chia câu + kế hoạch nháp
def _sach(w):
    return re.sub(r'[.,!?;:…"“”]+$', '', w)


def chia_cau(words, cuts):
    bc = [c['t'] for c in cuts if c['loai'] == 'boi_canh']
    cau, cur = [], []
    for i, w in enumerate(words):
        cur.append(w)
        nxt = words[i + 1] if i + 1 < len(words) else None
        het = re.search(r'[.?!…]$', w['w']) is not None
        if nxt:
            if nxt['s'] - w['e'] >= 0.55: het = True
            if any(w['e'] - 0.05 <= t <= nxt['s'] + 0.15 for t in bc): het = True
            if cur[-1]['e'] - cur[0]['s'] > 11 and re.search(r',$', w['w']): het = True
        if het or nxt is None:
            cau.append(cur); cur = []
    return cau


def _cum_sub(ws):
    """chia lời thành cụm 1–3 chữ (≤ 15 ký tự), ngắt ở dấu phẩy / khoảng nghỉ."""
    out, cur = [], []
    for i, w in enumerate(ws):
        cur.append(w)
        s = ' '.join(_sach(x['w']) for x in cur)
        nxt = ws[i + 1] if i + 1 < len(ws) else None
        cat = (nxt is None or re.search(r'[,.?!]$', w['w']) or len(cur) >= 3 or len(s) >= 13
               or (nxt and nxt['s'] - w['e'] > 0.22)
               or (nxt and len(s) + 1 + len(_sach(nxt['w'])) > 16))
        if cat: out.append(cur); cur = []
    return out


SO = re.compile(r'^\d')
DON_VI = {'tỷ', 'triệu', 'nghìn', 'm2', 'm²', '%', 'mét', 'km', 'năm', 'phút', 'ha', 'tầng', 'phòng'}


def _text_cum(ws):
    toks = [_sach(w['w']) for w in ws]
    toks = ['m²' if t.lower() in ('m2', 'mét vuông') else re.sub(r'(\d)m2$', r'\1m²', t) for t in toks]
    out, i = [], 0
    while i < len(toks):
        if SO.match(toks[i]):
            j = i + 1
            if j < len(toks) and toks[j].lower() in DON_VI:
                out.append('[' + toks[i] + ' ' + toks[j] + ']'); i = j + 1; continue
            out.append('[' + toks[i] + ']'); i += 1; continue
        out.append(toks[i]); i += 1
    s = ' '.join(out).replace(' m²', 'm²')
    return s[:1].upper() + s[1:] if s else s


def tach_tieu_de(cw):
    """[chữ…] → (dẫn, khoá, viết tay). Nháp: chữ chức năng đầu = dẫn, 1–2 chữ nội dung = khoá, đuôi ≤ 2 chữ = viết tay."""
    t = [_sach(w['w']) for w in cw]
    i = 0
    while i < len(t) - 1 and i < 2 and t[i].lower() in TU_DAN: i += 1
    dan = ' '.join(t[:i])
    rest = t[i:]
    nk = 1 if len(rest) <= 2 else 2
    khoa = ' '.join(rest[:nk]); vt = ' '.join(rest[nk:nk + 2])
    return dan[:1].upper() + dan[1:], khoa, vt


LUAT_TU_KHOA = [   # (mẫu lời, loại đồ hoạ, tham số) — CHỈ là gợi ý nháp, Claude quyết theo nghĩa
    (r'bảng giá', 'the_anh', {'tim': r'gia|price|bang'}),
    (r'mặt bằng|layout|quy hoạch', 'the_anh', {'tim': r'mat.?bang|layout|master|quy.?hoach', 'kieu': 'xep'}),
    (r'phối cảnh|căn hộ mẫu|nhà mẫu', 'the_anh', {'tim': r'phoi|canh|mau|render|view'}),
    (r'vị trí', 'icon', {'loai': 'vi_tri', 'nhan': 'Vị trí'}),
    (r'tiện ích', 'icon', {'loai': 'tien_ich', 'nhan': 'Tiện ích'}),
    (r'trường học|trường', 'icon', {'loai': 'truong_hoc', 'nhan': 'Trường học'}),
    (r'bệnh viện', 'icon', {'loai': 'benh_vien', 'nhan': 'Bệnh viện'}),
    (r'công viên|cây xanh', 'icon', {'loai': 'cong_vien', 'nhan': 'Công viên'}),
    (r'trung tâm thương mại|siêu thị|mua sắm', 'icon', {'loai': 'mua_sam', 'nhan': 'Mua sắm'}),
    (r'metro|giao thông|cao tốc|vành đai', 'icon', {'loai': 'giao_thong', 'nhan': 'Giao thông'}),
    (r'tìm hiểu|tra cứu|google|lên mạng', 'tim_kiem', {}),
]


def ke_hoach_nhap(words, cuts, dur, tai, ten_du_an):
    cau = chia_cau(words, cuts)
    plan = {'CAN_CLAUDE_SUA': True, 'dur': round(dur, 3), 'ten_du_an': ten_du_an or '', 'nhac': None, 'nhac_ss': 0.0,
            'sfx': True, 'zoom': [{'t': 0.0, 'z': 1.0}], 'chuyen': [], 'tieu_de': [], 'sub': [], 'the_anh': [],
            'icon': [], 'tim_kiem': [], 'so_tien': [], 'logo': [], 'liet_ke': [], 'sfx_them': [], 'sfx_bo': []}
    for n in tai:
        if n['loai'] == 'nhac' and not plan['nhac']: plan['nhac'] = n['file']
    k = 0
    for c in cuts:
        if c['loai'] == 'boi_canh':
            plan['chuyen'].append({'t': c['t'], 'kieu': C.CHUYEN_XOAY[k % len(C.CHUYEN_XOAY)]}); k += 1
    # zoom: đổi ở mỗi cú nhảy + đầu câu (không trùng chuyển cảnh)
    muc = [1.15, 1.0, 1.28, 1.0]
    zi = 0
    moc_zoom = sorted([c['t'] for c in cuts if c['loai'] == 'nhay'] + [round(cc[0]['s'] - 0.05, 3) for cc in cau[1:]])
    last = 0.0
    for t in moc_zoom:
        if t - last < 1.6 or any(abs(t - x['t']) < 0.6 for x in plan['chuyen']): continue
        plan['zoom'].append({'t': round(t, 3), 'z': muc[zi % len(muc)]}); zi += 1; last = t
    ki, prev_k = 0, None
    anh = [n for n in tai if n['loai'] in ('anh', 'video')]
    logo = next((n for n in tai if n['loai'] == 'logo'), None)
    for ci, ws in enumerate(cau):
        t_cau0, t_cau1 = ws[0]['s'], ws[-1]['e']
        nxt0 = cau[ci + 1][0]['s'] if ci + 1 < len(cau) else dur
        cw = []
        for w in ws:
            cw.append(w)
            if re.search(r',$', w['w']) or len(cw) >= 5: break
        dung_td = (t_cau1 - t_cau0) >= 2.2 and len(ws) >= 4 and len(cw) < len(ws)
        con = ws
        if dung_td:
            if len(cw) > 4: cw = cw[:4]
            dan, khoa, vt = tach_tieu_de(cw)
            kieu = C.KIEU_XOAY[ki % len(C.KIEU_XOAY)]
            if kieu == prev_k: ki += 1; kieu = C.KIEU_XOAY[ki % len(C.KIEU_XOAY)]
            prev_k = kieu
            ra = 'vo_chu' if ci == len(cau) - 1 else ('troi_xuong' if any(abs(x['t'] - nxt0) < 0.8 for x in plan['chuyen']) else 'chui_dau')
            plan['tieu_de'].append({'t0': round(max(0.05, t_cau0 - 0.12), 3), 't1': round(max(t_cau1 + 0.1, nxt0 - 0.3), 3),
                                    'dan': dan, 'khoa': khoa, 'viet_tay': vt, 'kieu': kieu,
                                    'vao': C.TIEU_DE_VAO[ki % len(C.TIEU_DE_VAO)], 'ra': ra, 'icon': None, 'vi_tri': 'tren'})
            ki += 1
            con = ws[len(cw):]
        cums = _cum_sub(con)
        for j, cm in enumerate(cums):
            t0 = round(cm[0]['s'] - 0.05, 3)
            t1 = round(cums[j + 1][0]['s'] - 0.05, 3) if j + 1 < len(cums) else round(min(cm[-1]['e'] + 0.45, nxt0 - 0.05), 3)
            plan['sub'].append({'t0': t0, 't1': t1, 'dong': [{'text': _text_cum(cm)}]})
        # đồ hoạ theo từ khoá (gợi ý)
        loi = ' '.join(_sach(w['w']).lower() for w in ws)
        for pat, loai, ts in LUAT_TU_KHOA:
            m = re.search(pat, loi)
            if not m: continue
            # mốc chữ đầu của cụm từ khoá
            ktu = pat.split('|')[0].split()[0]
            tw = next((w['s'] for w in ws if _sach(w['w']).lower() == ktu), ws[0]['s'])
            if loai == 'the_anh':
                f = next((a for a in anh if re.search(ts['tim'], a['ten'].lower())), None)
                if f:
                    plan['the_anh'].append({'t0': round(tw, 3), 't1': round(min(tw + 2.2, nxt0 - 0.1), 3), 'nguon': [f['file']],
                                            'tu': 'tay_trai', 'dat': 'duoi', 'kieu': ts.get('kieu', 'phang')})
            elif loai == 'icon':
                ben = 'trai' if len(plan['icon']) % 2 == 0 else 'phai'
                plan['icon'].append({'t0': round(tw + 0.1, 3), 't1': round(min(tw + 2.0, nxt0 - 0.1), 3), 'loai': ts['loai'],
                                     'nhan': ts['nhan'], 'ben': ben})
            elif loai == 'tim_kiem':
                plan['tim_kiem'].append({'t0': round(tw - 0.3, 3), 't1': round(min(tw + 1.8, nxt0 - 0.1), 3),
                                         'chu': ten_du_an or 'Tên dự án', 't_go': round(tw + 0.1, 3)})
        if logo and ten_du_an and ten_du_an.split()[0].lower() in loi:
            plan['logo'].append({'t0': round(ws[0]['s'], 3), 't1': round(nxt0 - 0.1, 3), 'nguon': logo['file']})
    return plan, cau


def ghi_loi(cau, path):
    with open(path, 'w', encoding='utf-8') as f:
        for i, ws in enumerate(cau):
            f.write(f"[{i + 1}] {ws[0]['s']:6.2f}–{ws[-1]['e']:6.2f}  " + ' '.join(w['w'] for w in ws) + '\n')
            f.write('     ' + ' '.join(f"{_sach(w['w'])}@{w['s']:.2f}" for w in ws) + '\n')


def chay(video, res, out, nhac=None, cat_lang='auto', ten_du_an=''):
    os.makedirs(out, exist_ok=True)
    pr = C.probe(video)
    if 'w' not in pr: raise SystemExit('Không đọc được hình của ' + video)
    print(f'Video: {pr["w"]}x{pr["h"]}, {pr["dur"]:.1f} s')
    nguon, giong = os.path.join(out, 'nguon.mp4'), os.path.join(out, 'giong.wav')
    meta_p = os.path.join(out, 'nguon_meta.json')
    st = os.stat(video)
    meta_moi = {'video': os.path.abspath(video), 'size': st.st_size, 'cat_lang_hoi': cat_lang}
    meta = C.doc_json(meta_p) if os.path.exists(meta_p) else None
    dung_lai = bool(meta) and all(meta.get(k) == v for k, v in meta_moi.items()) and os.path.exists(nguon) and os.path.exists(giong)
    if dung_lai:      # chạy lại phan-tich (vd sau khi bị ngắt) → giữ nguon/giong/words đã có, khỏi Whisper lại
        cat_lang, nhay = meta['cat_lang'], meta['nhay']
        print(f'  dùng lại nguon.mp4 + giong.wav đã có (cắt lặng: {cat_lang})')
    else:
        tho_wav = os.path.join(out, '_tho.wav')
        C.run(['ffmpeg', '-y', '-v', 'error', '-i', video, '-vn', '-ac', '1', '-ar', '16000', '-c:a', 'pcm_s16le', tho_wav])
        keep, bo = doan_giu(tho_wav, pr['dur'])
        if cat_lang == 'auto':
            dai = [b - a for a, b in bo if a > 0.05 and b < pr['dur'] - 0.05]
            cat_lang = 'co' if sum(1 for d in dai if d >= 0.6) >= 2 else 'khong'
            print(f'  cắt lặng tự quyết: {"CÓ" if cat_lang == "co" else "KHÔNG"} ({len(dai)} quãng lặng, {sum(1 for d in dai if d >= 0.6)} quãng ≥ 0,6 s)')
        if cat_lang != 'co': keep = [[0.0, pr['dur']]]
        print('Dựng nguon.mp4 (1080x1920, 30 fps)…', flush=True)
        dung_nguon(video, keep, nguon, giong)
        os.remove(tho_wav)
        nhay, acc = [], 0.0
        for a, b in keep[:-1]:
            acc += b - a; nhay.append(round(acc, 3))
        for f in ('words.json', 'mat.json', 'nguoi_mask.json', 'nguoi_mask.npy'):
            if os.path.exists(os.path.join(out, f)): os.remove(os.path.join(out, f))
        C.ghi_json(meta_p, dict(meta_moi, cat_lang=cat_lang, nhay=nhay))
    dur = C.probe(nguon)['dur']
    wp = os.path.join(out, 'words.json')
    if os.path.exists(wp):
        words = C.doc_json(wp); print(f'  dùng lại words.json ({len(words)} chữ)')
    else:
        print('Whisper large-v3 (CPU, lần đầu tải ~3 GB)…', flush=True)
        words = nghe(giong, PROMPT + (' ' + ten_du_an if ten_du_an else ''))
        if dur > 20 and len(words) / dur < 1.0:
            print(f'  ⚠ chỉ {len(words)} chữ / {dur:.0f} s — Whisper có thể nhận hỏng (nhạc to / ảo giác): mở loi_doc.txt '
                  f'kiểm, nghe lại đoạn trống trước khi viết kế hoạch', flush=True)
        C.ghi_json(wp, words)
    print('Dò cú cắt…', flush=True)
    cuts = do_cat(nguon, nhay)
    C.ghi_json(os.path.join(out, 'cut.json'), cuts)
    mp = os.path.join(out, 'mat.json')
    if os.path.exists(mp) and all('ung' in d for d in C.doc_json(mp)):
        mats, kieu_mat = C.doc_json(mp), 'đã có'
    else:
        print('Dò mặt…', flush=True)
        mats, kieu_mat = do_mat(nguon)
        mats = lam_muot_mat(chon_mat(mats, [c['t'] for c in cuts if c['loai'] == 'boi_canh']))
        C.ghi_json(mp, mats)
    tai = quet_tai_nguyen(res, out)
    if nhac: tai.append({'file': os.path.abspath(nhac), 'ten': os.path.basename(nhac), 'loai': 'nhac'})
    C.ghi_json(os.path.join(out, 'tai_nguyen.json'), tai)
    plan, cau = ke_hoach_nhap(words, cuts, dur, tai, ten_du_an)
    plan['video_goc'] = os.path.abspath(video); plan['cat_lang'] = cat_lang
    if nhac: plan['nhac'] = os.path.abspath(nhac)
    kh = os.path.join(out, 'ke_hoach.json')
    if os.path.exists(kh):
        shutil.copy(kh, os.path.join(out, 'ke_hoach_cu.json'))
        print('  (đã có ke_hoach.json → chép sang ke_hoach_cu.json, ghi nháp mới)')
    C.ghi_json(kh, plan)
    ghi_loi(cau, os.path.join(out, 'loi_doc.txt'))
    print(f'\nXONG bước 1 → {out}')
    print(f'  {len(words)} chữ · {len(cau)} câu · mặt: {kieu_mat} · cú cắt: '
          f'{sum(c["loai"] == "boi_canh" for c in cuts)} đổi bối cảnh + {sum(c["loai"] == "nhay" for c in cuts)} nhảy')
    print(f'  nháp: {len(plan["tieu_de"])} tiêu đề, {len(plan["sub"])} cụm sub, {len(plan["the_anh"])} thẻ ảnh, '
          f'{len(plan["icon"])} icon, {len(plan["tim_kiem"])} ô tìm kiếm, nhạc: {plan["nhac"] or "KHÔNG"}')
    print('\nLỜI:')
    print(open(os.path.join(out, 'loi_doc.txt'), encoding='utf-8').read())
    return plan
