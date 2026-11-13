# -*- coding: utf-8 -*-
"""dung.py — chuẩn bị footage (trích khung + chỉnh màu 1 lần), viết trang dựng, ảnh duyệt, dựng video, trộn tiếng."""
import json
import math
import shutil
import subprocess
import time
from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont

from chung import (FONT_DIR, FPS, H, KHUNG, NHAC_MUC, SKILL, W, bam, doc_json, ghi_json, loi, mo_anh, node, run, ten_moi, url)
from ke_hoach import giai

MAU_CLIP = 'eq=contrast=1.05:saturation=1.14:brightness=0.005,colorbalance=rm=0.03:bm=-0.03:rh=0.02:bh=-0.02'
NET = 'unsharp=5:5:0.55:5:5:0'


def _hdr_vf():
    r = run(['ffmpeg', '-hide_banner', '-filters'], capture=True)
    if ' zscale ' in (r.stdout or ''):
        return 'zscale=t=linear:npl=100,format=gbrpf32le,zscale=p=bt709,tonemap=tonemap=hable:desat=0,zscale=t=bt709:m=bt709:r=tv,format=yuv420p,'
    return ''


def _chinh_anh(im):
    im = im.convert('RGB')
    im = ImageEnhance.Contrast(im).enhance(1.05)
    im = ImageEnhance.Color(im).enhance(1.12)
    return im


def chuan_bi(work, CB, KH, bao=loi):
    """trích khung clip (đã crop 9:16, chỉnh màu, làm nét) + chuẩn bị ảnh — có cache theo khoá."""
    work = Path(work)
    fd = work / 'footage'
    fd.mkdir(exist_ok=True)
    m = {c['id']: c for c in KH['canh']}
    dh = {d['id']: d for d in KH['do_hoa']}
    hdr_vf = None
    t0 = time.time()
    for c in CB:
        if c['loai'] == 'clip':
            khoa = bam(c['file'], c['vao'], c['toc'], c['n'], c['cat_x'], c['cat_y'], MAU_CLIP, 2)
            d = fd / f"{c['id']}_{khoa}"
            if not (d / f"{c['n']:05d}.jpg").exists():
                if d.exists():
                    shutil.rmtree(d)
                d.mkdir()
                w, h = c['w'], c['h']
                if w / h > 9 / 16:
                    cw = int(h * 9 / 16) // 2 * 2
                    crop = f"crop={cw}:{h}:{int((w - cw) * c['cat_x'])}:0"
                else:
                    ch = int(w * 16 / 9) // 2 * 2
                    crop = f"crop={w}:{ch}:0:{int((h - ch) * c['cat_y'])}"
                if c['hdr'] and hdr_vf is None:
                    hdr_vf = _hdr_vf()
                vf = (hdr_vf if c['hdr'] else '') + f"setpts=PTS/{c['toc']},fps={FPS},{crop},scale={W}:{H}:flags=lanczos,{MAU_CLIP},{NET}"
                run(['ffmpeg', '-v', 'error', '-y', '-ss', f"{c['vao']:.3f}", '-i', c['file'], '-vf', vf, '-frames:v', str(c['n']),
                     '-q:v', '3', str(d / '%05d.jpg')])
                co = len(list(d.glob('*.jpg')))
                if co < c['n']:          # clip hết sớm → lặp khung cuối cho đủ
                    last = d / f'{co:05d}.jpg'
                    for i in range(co + 1, c['n'] + 1):
                        shutil.copyfile(last, d / f'{i:05d}.jpg')
                bao(f"  khung {c['id']}: {c['n']} khung ({Path(c['file']).name} từ {c['vao']:.1f}s)")
            m[c['id']]['dir'] = url(d, thu_muc=True)
        else:
            khoa = bam(c['file'], c.get('khung'), 4)
            d = fd / f"{c['id']}_{khoa}"
            d.mkdir(exist_ok=True)
            fa, fn = d / 'anh.jpg', d / 'nen.jpg'
            if not fa.exists():
                im = _chinh_anh(mo_anh(c['file']))
                if max(im.size) > 2600:
                    r = 2600 / max(im.size)
                    im = im.resize((int(im.width * r), int(im.height * r)), Image.LANCZOS)
                im.save(fa, quality=94)
                if c['loai'] == 'anh' and c.get('khung') == 'the':
                    s = max(W / im.width, H / im.height)
                    nen = im.resize((int(im.width * s) + 2, int(im.height * s) + 2), Image.LANCZOS)
                    nen = nen.crop(((nen.width - W) // 2, (nen.height - H) // 2, (nen.width - W) // 2 + W, (nen.height - H) // 2 + H))
                    nen = nen.resize((W // 4, H // 4), Image.LANCZOS).filter(ImageFilter.GaussianBlur(12)).resize((W, H), Image.BILINEAR)
                    nen = ImageEnhance.Brightness(nen).enhance(.62)
                    nen = ImageEnhance.Color(nen).enhance(1.15)
                    nen.save(fn, quality=90)
            if c['loai'] == 'anh':
                m[c['id']]['anh'] = url(fa)
                if c.get('khung') == 'the':
                    m[c['id']]['nen'] = url(fn)
            elif c['loai'] == 'anh_the':
                dh[c['id']]['anh_url'] = url(fa)
            elif c['loai'] == 'avatar':
                KH['cta']['avatar_url'] = url(fa)
    bao(f'  footage sẵn sàng ({time.time() - t0:.0f}s)')


def viet_trang(work, KH):
    work = Path(work)
    F = {'PF': [('PlayfairDisplay-VF.ttf', '400 900', 'normal')], 'PFI': [('PlayfairDisplay-Italic.ttf', '400 900', 'normal')],
         'GV': [('GreatVibes-Regular.ttf', '400', 'normal')], 'DS': [('DancingScript.ttf', '400 700', 'normal')],
         'AN': [('Anton-Regular.ttf', '400', 'normal')],
         'BVP': [('BeVietnamPro-Medium.ttf', '500', 'normal'), ('BeVietnamPro-SemiBold.ttf', '600', 'normal'),
                 ('BeVietnamPro-Bold.ttf', '700', 'normal'), ('BeVietnamPro-ExtraBold.ttf', '800', 'normal'),
                 ('BeVietnamPro-Black.ttf', '900', 'normal')],
         'MS': [('Montserrat-SemiBold.ttf', '600', 'normal'), ('Montserrat-Bold.ttf', '700', 'normal'), ('Montserrat-ExtraBold.ttf', '800', 'normal')]}
    ff = []
    for fam, ds in F.items():
        for f, wt, st in ds:
            ff.append(f"@font-face{{font-family:'{fam}';src:url('{url(FONT_DIR / f)}');font-weight:{wt};font-style:{st};font-display:block}}")
    html = f"""<!doctype html><html lang="{KH['ngon_ngu']}"><head><meta charset="utf-8">
<style>{''.join(ff)}</style>
<link rel="stylesheet" href="{url(KHUNG / 'dulich.css')}">
</head><body><div id="stage"></div>
<script>window.KH = {json.dumps(KH, ensure_ascii=False)};</script>
<script src="{url(KHUNG / 'dulich.js')}"></script>
</body></html>"""
    p = work / 'trang.html'
    p.write_text(html, encoding='utf-8')
    return p


def _render(args, bao=loi):
    cmd = [node(), str(SKILL / 'scripts' / 'render.mjs')] + [str(a) for a in args]
    r = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='replace')
    if r.stdout.strip():
        for d in r.stdout.strip().splitlines()[-6:]:
            bao('  ' + d)
    if r.returncode != 0:
        raise SystemExit('⛔ Dựng khung lỗi:\n' + (r.stderr or '')[-2000:])
    if r.stderr.strip():
        bao('  ' + r.stderr.strip()[-600:])
    return r


def _chuan_bi_het(work, can_dat=True):
    KH, sfx, CB, L = giai(work)
    nd = [m for m in L if m[0] == '⛔']
    for mm, msg in L:
        loi(f'{mm} {msg}')
    if nd and can_dat:
        raise SystemExit(f'⛔ Kế hoạch còn {len(nd)} lỗi ⛔ — sửa ke_hoach.json rồi chạy lại (run.py kiem-kh)')
    if KH is None:
        raise SystemExit('⛔ không giải được kế hoạch')
    chuan_bi(work, CB, KH)
    trang = viet_trang(work, KH)
    ghi_json(Path(work) / 'kh_giai.json', {'KH': KH, 'sfx': sfx})
    return KH, sfx, trang


def _font(sz):
    return ImageFont.truetype(str(FONT_DIR / 'BeVietnamPro-Bold.ttf'), sz)


def _moc_duyet(KH):
    """các mốc chụp duyệt: mỗi đồ hoạ lúc đã hiện đủ + giữa mỗi cảnh không có đồ hoạ + CTA."""
    ms = []
    for d in KH['do_hoa']:
        t = d['tu'] + min(1.9, (d['den'] - d['tu']) * .62)
        if d['loai'] in ('tu_khoa', 'liet_ke', 'chip') and d.get('muc'):
            t = max(t, min(d['den'] - .25, max(m.get('luc_abs', d['tu']) for m in d['muc']) + .7))
        ms.append((t, f"{d['id']} {d['loai']}"))
    for c in KH['canh']:
        mid = (c['tu'] + c['den']) / 2
        if not any(abs(mid - t) < 1.2 for t, _ in ms):
            ms.append((mid, f"{c['id']} {c['nguon']}"))
    for c in KH['canh'][1:]:
        if c['vao']['kieu'] in ('lia', 'zoom', 'loe') and len([1 for _, n in ms if n.startswith('chuyển')]) < 3:
            ms.append((c['tu'] + c['vao']['dai'] * .45, f"chuyển {c['vao']['kieu']}"))
    if KH['cta']:
        ms.append((KH['cta']['luc_bam'] - .2, 'CTA tay vào'))
        ms.append((KH['cta']['luc_tim'] + .15, 'CTA bấm tim'))
        ms.append((KH['dur'] - .05, 'khung cuối'))
    ms.sort()
    return ms


def _luoi_anh(files, nhan, out, cot=6, w=270, h=480):
    hang = math.ceil(len(files) / cot)
    sh = Image.new('RGB', (cot * w + (cot + 1) * 6, hang * (h + 30) + (hang + 1) * 6), (34, 34, 40))
    d = ImageDraw.Draw(sh)
    f = _font(18)
    for i, (p, n) in enumerate(zip(files, nhan)):
        x, y = 6 + (i % cot) * (w + 6), 6 + (i // cot) * (h + 36)
        im = Image.open(p).convert('RGB').resize((w, h), Image.LANCZOS)
        sh.paste(im, (x, y + 30))
        d.text((x + 4, y + 4), n[:30], font=f, fill=(255, 214, 90))
    sh.save(out, quality=88)
    return out


def kiem_hop(bao_cao, KH):
    """hộp chữ: sub đè đồ hoạ (⛔), chữ ra ngoài vùng an toàn (⚠)."""
    L = []
    AT = KH['an_toan']
    for r in bao_cao:
        hs = r['hop']
        sub = [b for b in hs if b['loai'] == 'sub']
        khac = [b for b in hs if b['loai'] != 'sub']
        for s in sub:
            for b in khac:
                ox = min(s['x'] + s['w'], b['x'] + b['w']) - max(s['x'], b['x'])
                oy = min(s['y'] + s['h'], b['y'] + b['h']) - max(s['y'], b['y'])
                if ox > 8 and oy > 8:
                    L.append(('⛔', f"{r['t']:.2f}s: sub đè {b['loai']} {b['id']} ({ox}x{oy}px)"))
        dh = {d['id']: d for d in KH.get('do_hoa', [])}
        kc = {c['id']: c for c in KH.get('canh', [])}

        def dang_bay(b):
            d = dh.get(b['id'])
            if d and not (d['tu'] + .7 <= r['t'] <= d['den'] - .45):
                return True                    # đồ hoạ đang bay vào / ra
            c = kc.get(b['id'])
            return bool(c) and not (c['tu'] + .5 <= r['t'] <= c.get('den', 1e9) - .5)   # cảnh đang chuyển

        for i, a in enumerate(khac):
            for b in khac[i + 1:]:
                if a['id'] == b['id'] or {a['loai'], b['loai']} <= {'cta'} or {a['loai'], b['loai']} == {'the_canh'}:
                    continue
                ox = min(a['x'] + a['w'], b['x'] + b['w']) - max(a['x'], b['x'])
                oy = min(a['y'] + a['h'], b['y'] + b['h']) - max(a['y'], b['y'])
                if ox > 12 and oy > 12:
                    if 'the_canh' in (a['loai'], b['loai']):
                        if not (dang_bay(a) or dang_bay(b)) and oy > 40:
                            the, chu = (a, b) if a['loai'] == 'the_canh' else (b, a)
                            L.append(('⚠', f"{r['t']:.2f}s: {chu['loai']} {chu['id']} che ảnh cảnh {the['id']} ({ox}x{oy}px) — "
                                           f"dời y chữ hoặc the_y / the_rong của cảnh"))
                        continue
                    L.append(('⛔', f"{r['t']:.2f}s: {a['loai']} {a['id']} đè {b['loai']} {b['id']} ({ox}x{oy}px)"))
        for b in hs:
            if b['loai'] == 'the_canh':
                continue          # thẻ ảnh không phải chữ — vùng an toàn chỉ áp cho chữ
            d = dh.get(b['id'])
            if d and not (d['tu'] + .7 <= r['t'] <= d['den'] - .45):
                continue          # đang bay vào / ra (giãn chữ, phóng to) — chỉ xét lúc đứng yên
            if b['x'] < AT['trai'] - 25 or b['x'] + b['w'] > W - 35 or b['y'] < AT['tren'] - 40 or b['y'] + b['h'] > AT['duoi']:
                L.append(('⚠', f"{r['t']:.2f}s: {b['loai']} {b['id']} ra ngoài vùng an toàn ({b['x']},{b['y']} {b['w']}x{b['h']})"))
    gon, da = [], set()
    for m, s in L:
        k = s.split(': ', 1)[1].split(' (')[0]
        if k not in da:
            da.add(k)
            gon.append((m, s))
    return gon


def duyet(work):
    work = Path(work)
    loi('Chuẩn bị footage + trang dựng …')
    KH, sfx, trang = _chuan_bi_het(work)
    ms = _moc_duyet(KH)
    d = work / 'duyet'
    if d.exists():
        shutil.rmtree(d)
    d.mkdir()
    loi(f'Chụp {len(ms)} khung duyệt …')
    _render(['--html', trang, '--anh', d, '--report', work / 'hop_duyet.json', '--times', ','.join(f'{t:.2f}' for t, _ in ms)])
    files = [d / f'k_{t:.2f}.jpg' for t, _ in ms]
    _luoi_anh(files, [f'{t:.1f}s {n}' for t, n in ms], work / 'duyet.jpg')
    L = kiem_hop(doc_json(work / 'hop_duyet.json'), KH)
    for m, s in L:
        loi(f'{m} {s}')
    # bảng duyệt
    lj = doc_json(work / 'loi.json')
    dong = [f"VIDEO {KH['dur']:.1f}s · 1080x1920 · {len(KH['canh'])} cảnh · ngôn ngữ chữ: {KH['ngon_ngu']}", '', 'CẢNH:']
    for c in KH['canh']:
        dong.append(f"  {c['tu']:6.2f}–{c['den']:6.2f}  {c['id']}  {c['nguon']:8s} {c['khung']:4s} vào:{c['vao']['kieu']:7s} {c['chuyen_dong']}")
    dong += ['', 'ĐỒ HOẠ:']
    for g in KH['do_hoa']:
        chu = ' | '.join(str(g.get(f)) for f in ('tren', 'chinh', 'viet_tay', 'duoi', 'so', 'nhan', 'ten', 'phu', 'dan', 'khoa', 'tieu', 'tien_to',
                                                    'hau_to', 'chu_thich', 'noi') if g.get(f) not in (None, ''))
        if g.get('muc'):
            chu += ' | ' + ', '.join(m.get('chu', '') for m in g['muc'])
        dong.append(f"  {g['tu']:6.2f}–{g['den']:6.2f}  {g['id']} {g['loai']:8s} {chu}")
    if KH['cta']:
        c = KH['cta']
        dong += ['', f"CTA {c['tu']:.2f}s: «{c.get('tieu_de', '')}» «{c.get('viet_tay', '')}» kênh «{c.get('ten', '')}» {c.get('handle', '')} "
                     f"nút «{c['nut']}»→«{c['nut_da']}» · tay bấm {c['luc_bam']:.2f}s, tim {c['luc_tim']:.2f}s"]
    dong += ['', f'SFX: {len(sfx)} tiếng', '', 'SUB (đã sửa lỗi nhận lời):']
    for s in KH['sub']:
        dong.append(f"  {s['tu']:6.2f}  " + ' / '.join(' '.join(w['w'] for w in dd) for dd in s['dong']))
    (work / 'bang_duyet.txt').write_text('\n'.join(dong), encoding='utf-8')
    loi(f"\nẢNH DUYỆT: {work / 'duyet.jpg'}\nBẢNG DUYỆT: {work / 'bang_duyet.txt'}")
    return L


def chup_khung(work, times):
    work = Path(work)
    KH, sfx, trang = _chuan_bi_het(work, can_dat=False)
    d = work / 'khung_le'
    d.mkdir(exist_ok=True)
    _render(['--html', trang, '--anh', d, '--times', ','.join(f'{t:.2f}' for t in times)])
    for t in times:
        loi(f"  {d / f'k_{t:.2f}.jpg'}")


def _tron_tieng(work, KH, sfx, lj, audio, dur, tieng):
    """giọng + nhạc nền (theo ke_hoach.nhac) + SFX → tieng (wav −14 LUFS)."""
    from am_thanh import tron
    kh = doc_json(work / 'ke_hoach.json')
    nc = kh.get('nhac') or {}
    nhac = nc.get('file') if isinstance(nc, dict) else None
    muc = float(nc.get('muc_db', NHAC_MUC)) if nhac else NHAC_MUC
    loi(f"Trộn tiếng: giọng{f' + nhạc nền {Path(nhac).name} ({muc:+.0f} dB dưới giọng)' if nhac else ''} + {len(sfx)} SFX → −14 LUFS …")
    tron(audio, dur, tieng, tu=lj['tu'], nhac=nhac, sfx=sfx, nhac_muc=muc, bao=loi, nhac_bat_dau=nc.get('bat_dau') if nhac else None,
         nhac_khop_cuoi=nc.get('khop_cuoi', True) if nhac else True, dai_video=KH['dur'])


def tron_lai(work, nguon=None, out=None):
    """CHỈ đổi tiếng (mức nhạc, file nhạc, SFX) — giữ nguyên hình của video đã dựng, khỏi dựng lại (~30 s thay vì vài phút).
    Hình KHÔNG đổi: sửa chữ / cảnh / đồ hoạ thì phải run.py dung."""
    from am_thanh import ghep
    work = Path(work)
    lj = doc_json(work / 'loi.json')
    nguon = Path(nguon) if nguon else Path(doc_json(work / 'ra.json')['file'])
    if not nguon.exists():
        raise SystemExit(f'⛔ không thấy video nguồn {nguon}')
    KH, sfx, _ = _chuan_bi_het(work)
    audio = Path(lj['nguon'])
    out = Path(out) if out else ten_moi(audio.with_name(audio.stem + '_DLV.mp4'))
    t0 = time.time()
    loi(f'Trộn lại tiếng, giữ hình của {nguon.name}')
    tieng = work / '_tieng.wav'
    _tron_tieng(work, KH, sfx, lj, audio, KH['dur'], tieng)
    tp = ghep(nguon, tieng, KH['dur'], out)
    loi(f'  đỉnh thật {tp:+.2f} dBTP')
    for p_ in (tieng, work / '_tieng_gh.wav'):
        try:
            p_.unlink()
        except Exception:
            pass
    loi(f'\nRA: {out}  ({time.time() - t0:.0f}s)')
    ghi_json(work / 'ra.json', {'file': str(out)})
    from kiem import kiem
    kiem(work, str(out))
    return out


def dung(work, luong=4, out=None, xem_truoc=False):
    from am_thanh import ghep
    work = Path(work)
    lj = doc_json(work / 'loi.json')
    KH, sfx, trang = _chuan_bi_het(work)
    audio = Path(lj['nguon'])
    out = Path(out) if out else ten_moi(audio.with_name(audio.stem + ('_DLV_xem_truoc.mp4' if xem_truoc else '_DLV.mp4')))
    dur = KH['dur'] if not xem_truoc else min(KH['dur'], 20.0)     # xem trước: 20 s đầu, không tự kiểm
    t0 = time.time()
    hinh = work / '_hinh.mp4'
    loi(f'Dựng hình {dur:.1f}s ({int(dur * FPS)} khung, {luong} luồng Chrome) …')
    args = ['--html', trang, '--out', hinh, '--fps', FPS, '--tu', 0, '--den', f'{dur:.4f}', '--luong', luong, '--crf', 17]
    _render(args)
    loi(f'  xong hình ({time.time() - t0:.0f}s)')
    tieng = work / '_tieng.wav'
    _tron_tieng(work, KH, sfx, lj, audio, dur, tieng)
    tp = ghep(hinh, tieng, dur, out)
    loi(f'  đỉnh thật {tp:+.2f} dBTP')
    for p in (hinh, tieng, work / '_tieng_gh.wav'):
        try:
            p.unlink()
        except Exception:
            pass
    loi(f'\nRA: {out}  ({time.time() - t0:.0f}s)')
    if xem_truoc:
        return out
    ghi_json(work / 'ra.json', {'file': str(out)})
    from kiem import kiem
    kiem(work, str(out))
    return out
