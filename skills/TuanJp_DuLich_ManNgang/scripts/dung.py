# -*- coding: utf-8 -*-
"""dung.py — chuẩn bị footage theo BỐ CỤC (tràn / thẻ dọc / ghép ô / thẻ ảnh — trích khung + chỉnh màu 1 lần, có cache),
viết trang dựng, ảnh duyệt, dựng video (Chrome headless, mã hoá 1 lần), trộn tiếng, ghép."""
import json
import math
import shutil
import subprocess
import time
from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont

from chung import (FONT_DIR, FPS, H, KHUNG, SKILL, THE_DOC_CAO, W, bam, doc_json, ghi_json, loi, mo_anh, node, run, ten_moi, url)
from ke_hoach import giai

MAU_CLIP = 'eq=contrast=1.06:saturation=1.16:brightness=0.008:gamma=0.98,colorbalance=rm=0.025:bm=-0.03:rh=0.03:gh=0.01:bh=-0.03'
NET = 'unsharp=5:5:0.6:5:5:0'
NET_PHONG = 'cas=0.55,unsharp=5:5:0.35:5:5:0'   # nguồn phải phóng > 1,5× (clip dọc tràn khung ngang): làm nét thích ứng bù độ mềm
DOC_CW, DOC_CH = 576, 1024          # khung lưu của thẻ dọc (hiện 506×900, dư cho Ken Burns)
NEN_W, NEN_H = 384, 216             # nền nhoè lưu nhỏ, trang phóng lên (đã nhoè nên không lộ)


def _hdr_vf():
    r = run(['ffmpeg', '-hide_banner', '-filters'], capture=True)
    if ' zscale ' in (r.stdout or ''):
        return 'zscale=t=linear:npl=100,format=gbrpf32le,zscale=p=bt709,tonemap=tonemap=hable:desat=0,zscale=t=bt709:m=bt709:r=tv,format=yuv420p,'
    return ''


def _chinh_anh(im):
    im = ImageEnhance.Contrast(im.convert('RGB')).enhance(1.06)
    im = ImageEnhance.Color(im).enhance(1.14)
    return im


def _vung_px(p, w, h):
    """vùng cắt [x0,y0,x1,y1] (0–1) của nguồn → (x, y, cw, ch) px."""
    v = p.get('vung') or [0, 0, 1, 1]
    x0, y0, x1, y1 = [float(z) for z in v]
    return int(w * x0), int(h * y0), max(2, int(w * (x1 - x0))), max(2, int(h * (y1 - y0)))


def _crop_ti_le(w, h, ti, cx, cy):
    """khung lớn nhất tỉ lệ `ti` (rộng/cao) trong w×h, neo theo cx, cy (0–1) → (cw, ch, x, y)."""
    if w / h > ti:
        cw, ch = int(h * ti) // 2 * 2, h // 2 * 2
    else:
        cw, ch = w // 2 * 2, int(w / ti) // 2 * 2
    return cw, ch, int((w - cw) * cx), int((h - ch) * cy)


def _kich_thuoc(p):
    k = p['kieu']
    if k == 'full':
        return W, H
    if k == 'card_doc':
        return DOC_CW, DOC_CH
    if k == 'nen':
        return NEN_W, NEN_H
    if k == 'panel':
        return p['pw'], H
    return 0, 0


def chuan_bi(work, CB, bao=loi):
    """→ {part_id: {dir|src, n, w, h, anh}} — trích khung / ảnh đã cắt + chỉnh màu theo bố cục; cache theo khoá."""
    work = Path(work)
    fd = work / 'footage'
    fd.mkdir(exist_ok=True)
    out, hdr_vf, t0 = {}, None, time.time()
    for p in CB:
        k = p['kieu']
        tw, th = _kich_thuoc(p)
        if p['loai'] == 'clip':
            khoa = bam(p['file'], p['vao'], p['toc'], p['n'], k, tw, th, p['cat_x'], p['cat_y'], p.get('vung'), MAU_CLIP, NET_PHONG, 4)
            d = fd / f"{p['id']}_{khoa}"
            if not (d / f"{p['n']:05d}.jpg").exists():
                if d.exists():
                    shutil.rmtree(d)
                d.mkdir()
                vx, vy, vw, vh = _vung_px(p, p['w'], p['h'])
                cw, ch, x, y = _crop_ti_le(vw, vh, tw / th, p['cat_x'], p['cat_y'])
                crop = f'crop={vw}:{vh}:{vx}:{vy},crop={cw}:{ch}:{x}:{y}'
                if p.get('hdr') and hdr_vf is None:
                    hdr_vf = _hdr_vf()
                if k == 'nen':
                    vf = f"setpts=PTS/{p['toc']},fps={FPS},{crop},scale={tw}:{th}:flags=bicubic,gblur=sigma=5,eq=saturation=1.2:brightness=-0.03"
                    q = '5'
                else:
                    net = NET if tw / max(1, cw) <= 1.5 else NET_PHONG
                    vf = f"setpts=PTS/{p['toc']},fps={FPS},{crop},scale={tw}:{th}:flags=lanczos,{MAU_CLIP},{net}"
                    q = '3'
                vf = (hdr_vf if p.get('hdr') else '') + vf
                run(['ffmpeg', '-v', 'error', '-y', '-ss', f"{p['vao']:.3f}", '-i', p['file'], '-vf', vf, '-frames:v', str(p['n']),
                     '-q:v', q, str(d / '%05d.jpg')])
                co = len(list(d.glob('*.jpg')))
                if co == 0:
                    raise SystemExit(f"⛔ không trích được khung {p['id']} ({Path(p['file']).name} từ {p['vao']}s)")
                for i in range(co + 1, p['n'] + 1):          # clip hết sớm → lặp khung cuối
                    shutil.copyfile(d / f'{co:05d}.jpg', d / f'{i:05d}.jpg')
                bao(f"  khung {p['id']}: {p['n']} khung {tw}x{th} ({Path(p['file']).name} từ {p['vao']:.1f}s)")
            out[p['id']] = {'dir': url(d, thu_muc=True), 'n': p['n'], 'w': tw, 'h': th, 'anh': False, '_tep': str(d)}
        else:
            khoa = bam(p['file'], k, tw, th, p['cat_x'], p['cat_y'], p.get('vung'), 4)
            f = fd / f"{p['id']}_{khoa}.jpg"
            if not f.exists():
                im = mo_anh(p['file'])
                vx, vy, vw, vh = _vung_px(p, im.width, im.height)
                im = im.crop((vx, vy, vx + vw, vy + vh))
                if k == 'card_anh':
                    s = min(1500 / im.width, 1000 / im.height, 1.0)
                    if s < 1:
                        im = im.resize((int(im.width * s), int(im.height * s)), Image.LANCZOS)
                    im = _chinh_anh(im)
                    tw, th = im.size
                else:
                    if k == 'full':
                        tw, th = int(W * 1.1), int(H * 1.1)          # dư 10 % cho Ken Burns
                    cw, ch, x, y = _crop_ti_le(im.width, im.height, tw / th, p['cat_x'], p['cat_y'])
                    im = im.crop((x, y, x + cw, y + ch))
                    if k == 'nen':
                        im = im.resize((tw, th), Image.LANCZOS).filter(ImageFilter.GaussianBlur(5))
                        im = ImageEnhance.Brightness(ImageEnhance.Color(im).enhance(1.2)).enhance(.95)
                    else:
                        if im.width < tw * .62:
                            bao(f"  ⚠ {p['id']}: ảnh {Path(p['file']).name} phải phóng {tw / im.width:.1f}× — sẽ mờ")
                        im = _chinh_anh(im.resize((tw, th), Image.LANCZOS))
                        if tw / max(1, cw) > 1.25:
                            im = im.filter(ImageFilter.UnsharpMask(2, 60, 2))
                im.save(f, quality=93)
            im = Image.open(f)
            out[p['id']] = {'src': url(f), 'n': 1, 'w': im.width, 'h': im.height, 'anh': True, '_tep': str(f)}
    bao(f'  footage sẵn sàng ({time.time() - t0:.0f}s)')
    return out


def _do_hinh(f):
    """E — tìm HÌNH NỔI BẬT trong 1 khung → [x, y, r] chuẩn hoá 0–1 (x theo ngang, y theo dọc, r theo chiều cao):
    1) VÙNG SÁNG GỌN, tròn (mặt trời, đèn lồng, trăng): điểm sáng hẳn so với cả khung, khối liền đủ tròn;
    2) HÌNH TRÒN NÉT (bánh xe, miệng bát, vòm hang) — Hough ngưỡng CAO (ngưỡng thấp bắt nhầm vòng ảo trên phong cảnh, thử 14/11/2026);
    3) không có → giữa khung r 0,2 (khớp tâm, vẫn mượt). Hình chắc chắn thì Claude ghi `khop` tay."""
    import cv2
    import numpy as np
    im = cv2.imdecode(np.fromfile(str(f), dtype=np.uint8), cv2.IMREAD_COLOR)
    if im is None:
        return None
    h0, w0 = im.shape[:2]
    im = cv2.resize(im, (480, max(1, int(h0 * 480 / w0))), interpolation=cv2.INTER_AREA)
    h, w = im.shape[:2]
    v = cv2.GaussianBlur(cv2.cvtColor(im, cv2.COLOR_BGR2HSV)[:, :, 2], (0, 0), 2.5).astype(np.float32)
    nguong = max(238.0, float(np.percentile(v, 99.4)), float(v.max()) - 9)       # lõi sáng nhất (tách mặt trời khỏi dải chân trời sáng)
    if float(v.max()) >= 238:                                              # có điểm cháy sáng
        so, nhan, tk, _ = cv2.connectedComponentsWithStats((v >= nguong).astype(np.uint8), 8)
        tot = None
        for i in range(1, so):
            x, y, bw, bh, s = tk[i]
            m = int(.03 * h)
            if s < .0004 * w * h or s > .05 * w * h or x <= m or y <= m or x + bw >= w - m or y + bh >= h - m:
                continue                                                   # vụn nhỏ / mảng trời lớn / chạm mép khung → bỏ
            (cx, cy), r = cv2.minEnclosingCircle(np.argwhere(nhan == i)[:, ::-1].astype(np.float32))
            tron = s / max(1.0, math.pi * r * r)                         # 1 = tròn đầy
            if tron >= .3 and (tot is None or s > tot[3]):           # mặt trời sát chân trời loe ngang ~0,37
                tot = (cx, cy, r, s)
        if tot:
            cx, cy, r, _ = tot
            return [round(cx / w, 3), round(cy / h, 3), round(max(.05, min(.4, 1.6 * r / h)), 3)]   # quầng sáng to hơn lõi
    g = cv2.medianBlur(cv2.cvtColor(im, cv2.COLOR_BGR2GRAY), 5)
    c = cv2.HoughCircles(g, cv2.HOUGH_GRADIENT, dp=1.2, minDist=80, param1=140, param2=80,
                         minRadius=int(.07 * h), maxRadius=int(.42 * h))
    if c is not None and len(c[0]):
        x, y, r = c[0][0]                           # HoughCircles xếp hình tròn nhiều phiếu nhất lên đầu
        return [round(float(x) / w, 3), round(float(y) / h, 3), round(float(r) / h, 3)]
    return [.5, .5, .2]


def _tep_khung(P, pid, t, a):
    """file khung của lớp `pid` ở giây t (như partUrl trong ngang.js)."""
    p = P.get(pid) or {}
    if p.get('anh'):
        return p.get('_tep')
    i = min(max(int((t - a) * FPS + 1e-4), 0), p.get('n', 1) - 1) + 1
    return str(Path(p['_tep']) / f'{i:05d}.jpg') if p.get('_tep') else None


def _tu_do_khop(KH, bao=loi):
    """E — cắt nối theo hình thiếu `khop` → dò hình ở khung cuối cảnh trước + khung đầu cảnh vào (cv2), ghi vào cảnh."""
    C = KH.get('canh') or []
    for i, c in enumerate(C):
        if c.get('chuyen') != 'khop_hinh' or c.get('khop') or i == 0:
            continue
        r = C[i - 1]
        fa = _tep_khung(KH['part'], (r.get('lop') or [None])[0], c['tu'] - .04, r['a'])
        fb = _tep_khung(KH['part'], (c.get('lop') or [None])[0], c['tu'] + .04, c['a'])
        try:
            ka, kb = (_do_hinh(fa) if fa else None), (_do_hinh(fb) if fb else None)
        except Exception as e:                      # thiếu cv2 / lỗi đọc → khớp giữa khung
            bao(f'  ⚠ {c.get("id")}: không dò được hình ({e}) — khớp giữa khung')
            ka = kb = None
        c['khop'] = {'ra': ka or [.5, .5, .2], 'vao': kb or [.5, .5, .2]}
        bao(f"  khớp hình {c.get('id')}: {c['khop']['ra']} → {c['khop']['vao']}")


def _tach_nguoi(work, KH, bao=loi):
    """F — cú ĐẨY hai nửa (montage, vòng 4): tách NGƯỜI ở khung đầu cảnh mới → PNG nền trong (cùng cỡ khung) + hộp người;
    ngang.js cho mép nấc 1 cắt ngang người → người nhô qua mép như đang đẩy. Không có model / không thấy người → chỉ chữ + vạch sáng."""
    for c in KH.get('canh') or []:
        if c.get('nv') is not True:
            c['nv'] = c.get('nv') if isinstance(c.get('nv'), dict) else None
            continue
        f = _tep_khung(KH['part'], (c.get('lop') or [None])[0], c['tu'] + .05, c['a'])
        r = None
        if f and Path(f).exists():
            try:
                import nguoi
                r = nguoi.cat_nguoi(f, Path(work) / 'footage', bao)
            except Exception as e:                      # thiếu onnxruntime / cv2 → bỏ người nhô, giữ chữ đẩy
                bao(f'  ⚠ {c.get("id")}: không tách được người ({e})')
        c['nv'] = {'src': url(Path(r['png'])), 'hop': r['hop']} if r else None
        if r:
            bao(f"  người nhô qua mép đẩy {c.get('id')}: hộp {r['hop']} ({100 * r['dt']:.0f}% khung)")


def viet_trang(work, KH):
    work = Path(work)
    F = {'PF': [('PlayfairDisplay-VF.ttf', '400 900', 'normal')], 'PFI': [('PlayfairDisplay-Italic.ttf', '400 900', 'normal')],
         'DS': [('DancingScript.ttf', '400 700', 'normal')], 'GV': [('GreatVibes-Regular.ttf', '400', 'normal')],
         'AN': [('Anton-Regular.ttf', '400', 'normal')],
         'BVP': [('BeVietnamPro-Medium.ttf', '500', 'normal'), ('BeVietnamPro-SemiBold.ttf', '600', 'normal'),
                 ('BeVietnamPro-Bold.ttf', '700', 'normal'), ('BeVietnamPro-ExtraBold.ttf', '800', 'normal'),
                 ('BeVietnamPro-Black.ttf', '900', 'normal')],
         'MS': [('Montserrat-SemiBold.ttf', '600', 'normal'), ('Montserrat-Bold.ttf', '700', 'normal'),
                ('Montserrat-ExtraBold.ttf', '800', 'normal')],
         # bộ chữ NGANG riêng (khách 14/11/2026: "text khác hẳn màn dọc"): Barlow Condensed IN HOA + Montserrat nghiêng
         'BC': [('BarlowCondensed-Black.ttf', '900', 'normal')], 'BCI': [('BarlowCondensed-BlackItalic.ttf', '900', 'normal')],
         'BCE': [('BarlowCondensed-ExtraBold.ttf', '800', 'normal')],
         'MSI': [('Montserrat-SemiBoldItalic.ttf', '600', 'normal'), ('Montserrat-BoldItalic.ttf', '700', 'normal')]}
    ff = [f"@font-face{{font-family:'{fam}';src:url('{url(FONT_DIR / f)}');font-weight:{wt};font-style:{st};font-display:block}}"
          for fam, ds in F.items() for f, wt, st in ds]
    html = f"""<!doctype html><html lang="{KH['ngon_ngu']}"><head><meta charset="utf-8">
<style>{''.join(ff)}</style>
<link rel="stylesheet" href="{url(KHUNG / 'ngang.css')}">
</head><body><div id="stage"></div>
<script>window.KH = {json.dumps(KH, ensure_ascii=False)};</script>
<script src="{url(KHUNG / 'vn_ban_do.js')}"></script>
<script src="{url(KHUNG / 'ngang.js')}"></script>
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
        raise SystemExit('⛔ Dựng khung lỗi:\n' + (r.stderr or '')[-2500:])
    if r.stderr.strip():
        bao('  ' + r.stderr.strip()[-800:])
    return r


def _chuan_bi_trang(work, bao=loi, cho_phep_loi=False):
    KH, CB, cue, L = giai(work)
    for m, s in L:
        if m != '🔧':
            bao(f'{m} {s}')
    so = sum(1 for m, _ in L if m == '⛔')
    if (so or not KH) and not cho_phep_loi:
        raise SystemExit(f'⛔ Kế hoạch còn {so} lỗi — chạy kiem-kh, sửa rồi dựng lại')
    tn = doc_json(Path(work) / 'tai_nguyen.json')
    KH['part'] = chuan_bi(work, CB, bao)
    _tu_do_khop(KH, bao)
    _tach_nguoi(work, KH, bao)
    bds = [d for d in KH['do_hoa'] if d.get('diem_den') and d.get('xuat_phat') and (d['loai'] == 'hanh_trinh' or d['loai'] == 'chuong')]
    if bds:
        import ban_do_that as BDT
        bao(f'  bản đồ A → B: {len(bds)} tuyến …')
        for d in bds:
            d['bd'] = BDT.chuan_bi(work, d, bao)
    kenh = KH.get('kenh') or {}
    if kenh.get('avatar'):
        a = Path(kenh['avatar'])
        if not a.is_absolute() and tn.get('res'):
            a = Path(tn['res']) / a
        if a.exists():
            f = Path(work) / 'footage' / 'avatar.jpg'
            im = mo_anh(a)
            s = min(im.size)
            im.crop(((im.width - s) // 2, (im.height - s) // 2, (im.width - s) // 2 + s, (im.height - s) // 2 + s)).resize((400, 400)).save(f, quality=92)
            KH['kenh']['avatar_url'] = url(f)
        else:
            bao(f'⚠ không thấy avatar {a}')
    return KH, cue, viet_trang(work, KH)


def _cho_duyet(KH):
    ts = []
    for c in KH['canh']:
        ts.append((round(c['tu'] + min(1.4, (c['den'] - c['tu']) * .55), 2), f"{c['id']} {c['bo_cuc']}"))
    for d in KH['do_hoa']:
        if d.get('luc_den') and d.get('diem_den'):           # bản đồ: 1 khung lúc đang chạy tuyến + 1 khung lúc tới nơi
            ts.append((round((d['luc_di'] + d['luc_den']) / 2 + .3, 2), f"{d['id']} bản đồ chạy"))
            ts.append((round(min(d['den'] - .3, d['luc_den'] + .9), 2), f"{d['id']} tới {d['diem_den'].get('ten', '')}"))
            continue
        ts.append((round(min(d['den'] - .3, d['tu'] + max(1.0, (d['den'] - d['tu']) * .6)), 2), f"{d['id']} {d['loai']}"))
    if KH.get('cta'):
        ts.append((round(KH['dur'] - .4, 2), 'màn kết'))
    ts.sort()
    gon = []
    for t, n in ts:
        if gon and abs(t - gon[-1][0]) < .35:
            gon[-1] = (gon[-1][0], gon[-1][1] + ' + ' + n)
        else:
            gon.append((t, n))
    return gon


def _to_anh(work, items, out, cot=4, w=480):
    h = int(w * 9 / 16)
    font = ImageFont.truetype(str(FONT_DIR / 'BeVietnamPro-Bold.ttf'), 18)
    hang = (len(items) + cot - 1) // cot
    sh = Image.new('RGB', (cot * (w + 6), hang * (h + 30)), (14, 14, 18))
    for k, (f, nhan) in enumerate(items):
        try:
            im = Image.open(f).convert('RGB').resize((w, h), Image.LANCZOS)
        except Exception:
            continue
        x, y = (k % cot) * (w + 6), (k // cot) * (h + 30)
        sh.paste(im, (x, y + 28))
        ImageDraw.Draw(sh).text((x + 4, y + 4), nhan[:52], font=font, fill=(255, 220, 90))
    sh.save(out, quality=88)


def duyet(work, bao=loi):
    work = Path(work)
    KH, cue, trang = _chuan_bi_trang(work, bao)
    ts = _cho_duyet(KH)
    d = work / 'duyet_khung'
    if d.exists():
        shutil.rmtree(d)
    _render(['--html', trang, '--anh', d, '--times', ','.join(f'{t:.2f}' for t, _ in ts)], bao)
    items = [(d / f'k_{t:.2f}.jpg', f'{t:.1f}s  {n}') for t, n in ts]
    _to_anh(work, items, work / 'duyet.jpg')
    B = [f"DUYỆT — {KH['dur']:.1f}s, {len(KH['canh'])} cảnh, {len(KH['do_hoa'])} đồ hoạ, {len(KH['sub'])} cụm sub, {len(cue)} SFX", '']
    if KH.get('lech'):
        B += [f"TEASER mở màn 0–{KH['lech']:.2f}s (chỉ nhạc, từ {KH.get('teaser_dau') or 0:.2f}s của bài, ≈ {KH.get('bpm') or 0:.0f} BPM) → giọng vào {KH['lech']:.2f}s", '']
    bd = [d for d in KH['do_hoa'] if d.get('_so')]
    if bd:
        B += ['BẢN ĐỒ A → B (số ≈ ước tính đường đi thật — XÁC NHẬN):'] + [f"  {d['tu']:6.2f}  {d['id']:5s} {d['_so']}" for d in bd] + ['']
    bl = [d for d in KH['do_hoa'] if d['loai'] == 'binh_luan']
    if bl:
        B.append('BÌNH LUẬN ẢO:')
        for d in bl:
            B.append(f"  {d['tu']:6.2f}–{d['den']:6.2f}  {d.get('ten', '')} ({d.get('vi_tri')})")
            B += [f"      [{m.get('nn')}] {m.get('ten')}: {m.get('chu')}" for m in d.get('muc') or []]
        B.append('')
    B.append('CẢNH:')
    for c in KH['canh']:
        B.append(f"  {c['tu']:6.2f}–{c['den']:6.2f}  {c['id']:5s} {c['bo_cuc']:8s} {c['chuyen']:8s} {', '.join(c['lop'])}")
    B += ['', 'ĐỒ HOẠ:']
    for g in KH['do_hoa']:
        chu = ' / '.join(str(g.get(k)) for k in ('tren', 'chinh', 'nhan', 'ten', 'dan', 'khoa', 'viet_tay', 'phu', 'noi', 'so') if g.get(k))
        if g.get('muc'):
            chu += ' | ' + ' · '.join(str(m.get('chu') if isinstance(m, dict) else m) for m in g['muc'])
        B.append(f"  {g['tu']:6.2f}–{g['den']:6.2f}  {g['id']:4s} {g['loai']:9s} {chu}")
    if KH.get('cta'):
        c = KH['cta']
        B += ['', f"MÀN KẾT {c['tu']:.2f}s: {c.get('cau_hoi') or ''} {' / '.join(c.get('lua_chon') or [])} | {c['cam_on']} | {c['loi_moi']} | "
                  f"kênh: {KH['kenh'].get('ten') or '(trống)'}"]
    B += ['', 'SUB:'] + [f"  {s['tu']:6.2f}  " + ' / '.join(' '.join(w['w'] for w in dg) for dg in s['dong']) for s in KH['sub']]
    (work / 'bang_duyet.txt').write_text('\n'.join(B) + '\n', encoding='utf-8')
    bao(f'→ {work / "duyet.jpg"}  ({len(ts)} khung) + bang_duyet.txt')


def chup_khung(work, times, bao=loi):
    work = Path(work)
    KH, cue, trang = _chuan_bi_trang(work, bao, cho_phep_loi=True)
    d = work / 'khung_le'
    d.mkdir(exist_ok=True)
    _render(['--html', trang, '--anh', d, '--times', ','.join(f'{t:.2f}' for t in times)], bao)
    _to_anh(work, [(d / f'k_{t:.2f}.jpg', f'{t:.2f}s') for t in times], work / 'khung_le.jpg', cot=min(4, len(times)) or 1, w=640)
    bao(f'→ {d}  +  {work / "khung_le.jpg"}')


def _tron(work, KH, cue, out_wav, dur, bao=loi):
    from am_thanh import tron
    lj = doc_json(Path(work) / 'loi.json')
    kh = doc_json(Path(work) / 'ke_hoach.json')
    nhac = kh.get('nhac')
    if nhac is False:
        nhac = None
    elif not nhac:
        nhac = doc_json(Path(work) / 'tai_nguyen.json').get('nhac')
    if nhac and not Path(nhac).exists():
        bao(f'⚠ không thấy file nhạc {nhac} — bỏ nhạc')
        nhac = None
    return tron(lj['nguon'], dur, out_wav, tu=lj['tu'], nhac=nhac, sfx=cue, bao=bao, dai_video=KH['dur'],
                nhac_bat_dau=kh.get('nhac_bat_dau'), lech=KH.get('lech') or 0.0, teaser_dau=KH.get('teaser_dau'))


def dung(work, luong=4, out=None, xem_truoc=False, bao=loi):
    from am_thanh import ghep
    work = Path(work)
    t0 = time.time()
    bao('1/4 Chuẩn bị kế hoạch + footage …')
    KH, cue, trang = _chuan_bi_trang(work, bao)
    lj = doc_json(work / 'loi.json')
    dur = min(KH['dur'], 20.0) if xem_truoc else KH['dur']
    au = Path(lj['nguon'])
    if out:
        out = Path(out)
    else:
        out = ten_moi(au.with_name(au.stem + ('_DLN_xem_truoc.mp4' if xem_truoc else '_DLN.mp4')))
    hinh = work / '_hinh.mp4'
    bao(f'2/4 Dựng hình {dur:.1f}s × {FPS} fps bằng Chrome ({luong} luồng) …')
    _render(['--html', trang, '--out', hinh, '--fps', FPS, '--tu', 0, '--den', f'{dur:.3f}', '--luong', luong, '--crf', 17], bao)
    bao('3/4 Trộn giọng + SFX (+ nhạc nền nếu có), −14 LUFS …')
    wav = work / '_tieng.wav'
    _tron(work, KH, [c for c in cue if c['luc'] < dur], wav, dur, bao)
    bao('4/4 Ghép …')
    tp = ghep(hinh, wav, dur, out, bao)
    for f in (hinh, wav, work / '_tieng_gh.wav'):
        try:
            f.unlink()
        except Exception:
            pass
    bao(f'XONG → {out}  ({time.time() - t0:.0f}s, đỉnh {tp:+.1f} dBTP)')
    ghi_json(work / 'lan_dung.json', {'video': str(out), 'dur': dur, 'xem_truoc': xem_truoc})
    if not xem_truoc:
        from kiem import kiem
        kiem(work, out)
    return out


def tron_lai(work, file=None, out=None, bao=loi):
    """chỉ đổi TIẾNG (nhạc / SFX) — giữ nguyên hình đã dựng."""
    from am_thanh import ghep
    work = Path(work)
    KH, CB, cue, L = giai(work)
    vid = Path(file) if file else Path(doc_json(work / 'lan_dung.json')['video'])
    out = Path(out) if out else ten_moi(vid)
    wav = work / '_tieng.wav'
    _tron(work, KH, cue, wav, KH['dur'], bao)
    tp = ghep(vid, wav, KH['dur'], out, bao)
    bao(f'XONG → {out} (đỉnh {tp:+.1f} dBTP)')
    ghi_json(work / 'lan_dung.json', {'video': str(out), 'dur': KH['dur'], 'xem_truoc': False})
    from kiem import kiem
    kiem(work, out)
