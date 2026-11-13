# -*- coding: utf-8 -*-
"""kiem.py — tự kiểm trên FILE CUỐI: khổ / fps / độ dài, −14 LUFS & đỉnh, khung đen, chữ đúng ngôn ngữ, chữ đè nhau, tờ soát."""
import math
import re
import shutil
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from chung import FONT_DIR, FPS, H, LUFS, TP, W, doc_json, loi, probe, run
from ke_hoach import giai


def kiem(work, file=None):
    work = Path(work)
    if not file:
        r = work / 'ra.json'
        if not r.exists():
            raise SystemExit('⛔ chưa có video ra — chạy run.py dung trước hoặc truyền --file')
        file = doc_json(r)['file']
    file = Path(file)
    KH, sfx, CB, L = giai(work)
    kq = []

    def muc(ten, ok, ghi=''):
        kq.append((ten, ok, ghi))
        loi(f"{'✅' if ok else '⛔'} {ten}{(' — ' + ghi) if ghi else ''}")

    pr = probe(file)
    muc('Khổ 1080x1920 dọc', pr['w'] == W and pr['h'] == H, f"{pr['w']}x{pr['h']}")
    muc('30 fps', abs(pr['fps'] - FPS) < .05, f"{pr['fps']:.2f}")
    muc('Độ dài khớp kế hoạch', abs(pr['duration'] - KH['dur']) < .2, f"{pr['duration']:.2f}s / {KH['dur']:.2f}s")
    muc('Có tiếng', pr['audio'])
    lj = doc_json(work / 'loi.json')
    muc('Không cắt giọng', pr['duration'] >= lj['tu'][-1]['e'] + .3, f"tiếng cuối {lj['tu'][-1]['e']:.2f}s")
    # nhạc nền: kế hoạch có nhạc → bộ trộn phải đo được nhạc trong bản trộn ở mức nghe được mà không che lời
    nc = doc_json(work / 'ke_hoach.json').get('nhac')
    if isinstance(nc, dict) and nc.get('file'):
        bc = work / 'tron_bao_cao.json'
        if bc.exists() and bc.stat().st_mtime >= file.stat().st_mtime - 600:
            r_ = doc_json(bc).get('nhac_so_giong_db', -99)
            muc('Có nhạc nền (−24…−10 dB dưới giọng)', -24 <= r_ <= -10, f"{Path(nc['file']).name}: {r_:.1f} dB dưới giọng")
        else:
            loi('⚠ chưa có tron_bao_cao.json mới cho video này — không đo được nhạc nền (dựng lại bằng run.py dung)')
    # độ to
    r = run(['ffmpeg', '-hide_banner', '-nostats', '-i', file, '-af', f'loudnorm=I={LUFS}:TP={TP}:print_format=json', '-f', 'null', '-'],
            capture=True)
    m = re.findall(r'\{[^{}]*"input_i"[^{}]*\}', r.stderr or '')
    import json
    d = json.loads(m[-1]) if m else {'input_i': -99, 'input_tp': 99}
    muc('Độ to −14 LUFS (±1)', abs(float(d['input_i']) - LUFS) <= 1.0, f"{float(d['input_i']):.1f} LUFS")
    muc('Đỉnh ≤ −1 dBTP', float(d['input_tp']) <= TP + .05, f"{float(d['input_tp']):+.2f} dBTP")
    # khung đen
    r = run(['ffmpeg', '-hide_banner', '-nostats', '-i', file, '-vf', 'blackdetect=d=0.25:pix_th=0.06', '-an', '-f', 'null', '-'], capture=True)
    den = re.findall(r'black_start:([\d.]+)', r.stderr or '')
    muc('Không có khung đen', not den, ('đen ở ' + ', '.join(den[:5]) + 's') if den else '')
    # chữ đúng ngôn ngữ + kế hoạch
    nl = [x for x in L if x[0] == '⛔' and ('ngôn ngữ' in x[1] or 'tiếng' in x[1])]
    gi = KH.get('ngon_ngu_giong') or KH['ngon_ngu']
    nhan = (f"Mọi chữ trên hình bằng ngôn ngữ audio ({KH['ngon_ngu']})" if gi == KH['ngon_ngu'] else
            f"Mọi chữ trên hình bằng {KH['ngon_ngu']} (giọng {gi}, sub dịch theo yêu cầu)")
    muc(nhan, not nl, '; '.join(x[1] for x in nl[:3]))
    # chữ đè nhau: đo hộp ở nhiều mốc
    from dung import _render, kiem_hop, viet_trang
    trang = work / 'trang.html'
    if not trang.exists():
        raise SystemExit('⛔ thiếu trang.html — chạy run.py duyet / dung')
    moc = sorted(set([round(x * .5, 2) for x in range(1, int(KH['dur'] * 2))] +
                     [round(dd['tu'] + min(1.9, (dd['den'] - dd['tu']) * .6), 2) for dd in KH['do_hoa']]))
    _render(['--html', trang, '--report', work / 'hop_kiem.json', '--times', ','.join(f'{t:.2f}' for t in moc)], bao=lambda s: None)
    LH = kiem_hop(doc_json(work / 'hop_kiem.json'), KH)
    de = [x for x in LH if x[0] == '⛔']
    muc('Chữ / sub không đè nhau', not de, '; '.join(x[1] for x in de[:4]))
    ra = [x for x in LH if x[0] == '⚠']
    if ra:
        loi('⚠ ' + '; '.join(x[1] for x in ra[:4]))
    # CTA
    c = KH.get('cta')
    muc('CTA cuối (nút theo dõi + bàn tay + icon)', bool(c) and KH['dur'] - c['tu'] >= 3.8,
        f"{c['tu']:.1f}s → {KH['dur']:.1f}s" if c else 'thiếu')
    # tờ soát
    tmp = work / '_soat'
    if tmp.exists():
        shutil.rmtree(tmp)
    tmp.mkdir()
    buoc = 2.0 if KH['dur'] <= 90 else 2.5
    # lấy ĐÚNG khung thứ k·buoc·FPS (bộ lọc fps lấy mẫu giữa khoảng → nhãn giây lệch nửa bước)
    run(['ffmpeg', '-v', 'error', '-y', '-i', file, '-vf', f'select=not(mod(n\\,{int(round(buoc * FPS))})),scale=216:384', '-fps_mode', 'vfr',
         '-q:v', '3', str(tmp / '%04d.jpg')])
    fs = sorted(tmp.glob('*.jpg'))
    cot = 8
    hang = math.ceil(len(fs) / cot)
    sh = Image.new('RGB', (cot * 222 + 6, hang * 412 + 6), (30, 30, 36))
    dr = ImageDraw.Draw(sh)
    f = ImageFont.truetype(str(FONT_DIR / 'BeVietnamPro-Bold.ttf'), 18)
    for i, p in enumerate(fs):
        x, y = 6 + (i % cot) * 222, 6 + (i // cot) * 412
        sh.paste(Image.open(p), (x, y + 24))
        dr.text((x + 2, y + 2), f'{i * buoc:.1f}s', font=f, fill=(255, 214, 90))
    sh.save(work / 'soat.jpg', quality=86)
    shutil.rmtree(tmp, ignore_errors=True)
    dat = sum(1 for _, ok, _ in kq if ok)
    loi(f"\nTỰ KIỂM: {'ĐẠT' if dat == len(kq) else 'CHƯA ĐẠT'} {dat}/{len(kq)} · tờ soát {work / 'soat.jpg'}")
    return dat == len(kq)
