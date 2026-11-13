# -*- coding: utf-8 -*-
"""kiem.py — tự kiểm TRÊN FILE CUỐI: khổ 1920×1080 · 30 fps · độ dài · có tiếng · không cắt giọng · −14 LUFS · đỉnh ≤ −1 dBTP ·
không khung đen giữa video · sub không đè chữ đồ hoạ · có màn kết → soat.jpg (24 khung) để mở soi."""
import io
import json
import re
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from chung import FONT_DIR, FPS, H, LUFS, TP, W, doc_json, loi, probe, run


def _do_to(f):
    r = run(['ffmpeg', '-hide_banner', '-nostats', '-i', f, '-af', 'loudnorm=I=-14:TP=-1:LRA=11:print_format=json', '-f', 'null', '-'],
            capture=True)
    m = re.findall(r'\{[^{}]*"input_i"[^{}]*\}', r.stderr or '')
    return json.loads(m[-1]) if m else None


def _khung_den(f, dur):
    r = run(['ffmpeg', '-hide_banner', '-nostats', '-i', f, '-vf', 'blackdetect=d=0.25:pix_th=0.06', '-an', '-f', 'null', '-'], capture=True)
    o = []
    for a, b in re.findall(r'black_start:([\d.]+) black_end:([\d.]+)', r.stderr or ''):
        a, b = float(a), float(b)
        if a < .9 or b > dur - .7:       # mở từ đen / tắt dần cuối là cố ý
            continue
        o.append((a, b))
    return o


def _de_nhau(work):
    """dò sub đè chữ đồ hoạ: chụp hộp chữ mỗi 0,5 s bằng chính trang dựng."""
    from dung import _render
    trang = Path(work) / 'trang.html'
    KH = None
    try:
        txt = trang.read_text(encoding='utf-8')
        KH = json.loads(re.search(r'window\.KH = (\{.*?\});</script>', txt, re.S).group(1))
    except Exception:
        return None
    ts = [round(x * .5, 2) for x in range(1, int(KH['dur'] / .5))]
    rp = Path(work) / '_hop.json'
    _render(['--html', trang, '--report', rp, '--times', ','.join(map(str, ts))], bao=lambda m: None)
    bc = json.loads(rp.read_text(encoding='utf-8'))
    rp.unlink()
    loi_ds = []
    for k in bc:
        subs = [h for h in k['hop'] if h['loai'] == 'sub']
        dhs = [h for h in k['hop'] if h['loai'] != 'sub']
        for s in subs:
            for d in dhs:
                ox = min(s['x'] + s['w'], d['x'] + d['w']) - max(s['x'], d['x'])
                oy = min(s['y'] + s['h'], d['y'] + d['h']) - max(s['y'], d['y'])
                if ox > 20 and oy > 12:
                    loi_ds.append((k['t'], d['id'], d['loai']))
        for d in dhs:
            if d['x'] < 40 or d['x'] + d['w'] > W - 40 or d['y'] < 20 or d['y'] + d['h'] > H - 20:
                loi_ds.append((k['t'], d['id'], d['loai'] + ' tràn mép'))
    return loi_ds


def _to_soat(f, dur, out, n=24):
    font = ImageFont.truetype(str(FONT_DIR / 'BeVietnamPro-Bold.ttf'), 18)
    w, h, cot = 480, 270, 4
    sh = Image.new('RGB', (cot * (w + 6), ((n + cot - 1) // cot) * (h + 28)), (12, 12, 16))
    for k in range(n):
        t = dur * (k + .5) / n
        r = subprocess.run(['ffmpeg', '-v', 'error', '-ss', f'{t:.2f}', '-i', str(f), '-frames:v', '1', '-vf', f'scale={w}:{h}', '-f',
                            'image2pipe', '-c:v', 'mjpeg', '-'], capture_output=True)
        try:
            im = Image.open(io.BytesIO(r.stdout)).convert('RGB')
        except Exception:
            continue
        x, y = (k % cot) * (w + 6), (k // cot) * (h + 28)
        sh.paste(im, (x, y + 26))
        ImageDraw.Draw(sh).text((x + 4, y + 3), f'{t:.1f}s', font=font, fill=(255, 220, 90))
    sh.save(out, quality=86)


def kiem(work, file=None, bao=loi):
    work = Path(work)
    f = Path(file) if file else Path(doc_json(work / 'lan_dung.json')['video'])
    lj = doc_json(work / 'loi.json')
    kh = doc_json(work / 'ke_hoach.json')
    pa = probe(f)
    ok, R = True, []

    def M(dat, ten, chi_tiet):
        nonlocal ok
        ok = ok and dat
        R.append(f"{'✅' if dat else '⛔'} {ten}: {chi_tiet}")
    M(pa['w'] == W and pa['h'] == H, 'khổ', f"{pa['w']}×{pa['h']}")
    M(abs(pa['fps'] - FPS) < .01, 'fps', f"{pa['fps']:.2f}")
    het = lj['tu'][-1]['e'] if lj.get('tu') else 0
    M(pa['duration'] >= het + .3, 'không cắt giọng', f"video {pa['duration']:.2f}s, tiếng cuối {het:.2f}s")
    M(pa['audio'], 'có tiếng', 'AAC' if pa['audio'] else 'KHÔNG CÓ')
    d = _do_to(f)
    if d:
        i, tp = float(d['input_i']), float(d['input_tp'])
        M(abs(i - LUFS) <= 1.0, 'độ to', f'{i:.1f} LUFS (chuẩn {LUFS:.0f} ±1)')
        M(tp <= TP + .05, 'đỉnh', f'{tp:+.1f} dBTP (≤ {TP:.0f})')
    rb = work / 'tron_bao_cao.json'
    if (kh.get('nhac') or doc_json(work / 'tai_nguyen.json').get('nhac')) and kh.get('nhac') is not False:
        if rb.exists():
            r = doc_json(rb)['nhac_so_giong_db']
            M(-24 <= r <= -9, 'nhạc nền', f'{r:.1f} dB dưới giọng')
        else:
            M(False, 'nhạc nền', 'kế hoạch có nhạc nhưng không thấy bản trộn')
    if rb.exists() and doc_json(rb).get('sfx'):
        ds = doc_json(rb)['sfx']
        dat = [x for x in ds if x['tren_giong_db'] >= x['muc_tieu'] - 1.5]
        M(len(dat) >= .9 * len(ds), 'SFX nghe rõ', f"{len(dat)}/{len(ds)} tiếng đạt mức đặt trong SFX_TREN (so với giọng tại chỗ)")
    den = _khung_den(f, pa['duration'])
    M(not den, 'không khung đen', 'sạch' if not den else ', '.join(f'{a:.1f}–{b:.1f}s' for a, b in den[:6]))
    try:
        dn = _de_nhau(work)
    except SystemExit as e:
        dn = None
        bao(f'  (bỏ qua dò đè chữ: {str(e)[:160]})')
    if dn is not None:
        gom = {}
        for t, i_, l_ in dn:
            gom.setdefault((i_, l_), []).append(t)
        M(not gom, 'chữ không đè nhau / không tràn mép', 'sạch' if not gom else '; '.join(f'{k[0]} ({k[1]}) @ {v[0]:.1f}–{v[-1]:.1f}s' for k, v in list(gom.items())[:6]))
    M(bool(kh.get('cta', {}).get('bat', True)), 'màn kết', 'có' if kh.get('cta', {}).get('bat', True) else 'tắt')
    _to_soat(f, pa['duration'], work / 'soat.jpg')
    for x in R:
        bao(x)
    bao(('TỰ KIỂM: ĐẠT' if ok else 'TỰ KIỂM: CHƯA ĐẠT') + f'  → mở {work / "soat.jpg"}')
    return ok
