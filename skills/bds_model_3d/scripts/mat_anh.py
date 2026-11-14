# -*- coding: utf-8 -*-
"""mat_anh.py — DÁN MẶT ĐỨNG ẢNH THẬT: cắt 1 mặt tháp trong ảnh phối cảnh khách đưa, NẮN PHẲNG phối cảnh (homography 4 góc)
thành texture chữ nhật → tháp có "anh_mat": "<id>" mang đúng mặt kính / khung / đèn / vườn treo như ảnh.

  run.py mat-anh --work W --anh <ảnh> --goc "x,y x,y x,y x,y" --id dong_a [--tang 33] [--rong 320] [--sang 1.0]
     --goc  4 góc mặt đứng trong ảnh GỐC (px), thứ tự: TRÊN-TRÁI, TRÊN-PHẢI, DƯỚI-PHẢI, DƯỚI-TRÁI.
            Lấy từ mép trong khung viền (đỉnh = ngay dưới mái / viền mái, đáy = chân tháp hoặc mép đế, KHÔNG lấy cây che).
     --tang số tầng mà vùng cắt phủ (ghi vào mat_anh.json để kiểm khớp với tháp; 0 = không rõ)
     Mặc định TỰ NẮN THẲNG: dò vạch cửa / cột + vạch sàn, dời góc dưới / góc phải vài px cho mặt hết xiên (ảnh chụp trên cao
     cạnh đứng chụm xuống, chấm bằng mắt lệch là texture xiên 3–5°). --giu-goc để dùng nguyên góc chấm; mặt < 45 px không tự nắn.
→ W/mat_anh/<id>.jpg (texture), <id>_xem.jpg (ảnh gốc khoanh tứ giác + texture nắn — Claude MỞ soi), mat_anh.json (sổ).
Toạ độ đọc bằng: run.py luoi-anh --anh <ảnh> --vung x0,y0,x1,y1 [--to 2] (kẻ lưới toạ độ gốc).
"""
import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

from chung import ASSETS, loi


def _he_so(dich, nguon):
    """hệ số PIL PERSPECTIVE: điểm ra (dich) → điểm ảnh gốc (nguon)."""
    A, b = [], []
    for (x, y), (u, v) in zip(dich, nguon):
        A.append([x, y, 1, 0, 0, 0, -u * x, -u * y]); b.append(u)
        A.append([0, 0, 0, x, y, 1, -v * x, -v * y]); b.append(v)
    return np.linalg.solve(np.array(A, float), np.array(b, float)).tolist()


def doc_goc(s):
    try:
        P = [tuple(float(v) for v in c.split(',')) for c in str(s).replace(';', ' ').split()]
    except ValueError:
        P = []
    if len(P) != 4 or any(len(p) != 2 for p in P):
        raise SystemExit('⛔ --goc cần đúng 4 điểm "x,y x,y x,y x,y" (trên-trái, trên-phải, dưới-phải, dưới-trái)')
    return P


def _nan_xam(xam, goc, rw, rh):
    """nắn nhanh ảnh xám (float) theo 4 góc → mảng rh×rw để chấm điểm thẳng."""
    hs = _he_so([(0, 0), (rw, 0), (rw, rh), (0, rh)], goc)
    return np.asarray(xam.transform((rw, rh), Image.PERSPECTIVE, hs, Image.BILINEAR), np.float32)


def _diem_thang(a):
    """độ 'thẳng' của mặt nắn: vạch đứng (cột, đố cửa) dồn vào ít cột + vạch ngang (sàn, ban công) dồn vào ít hàng
    → hệ số biến thiên² của tổng gradient theo cột / theo hàng (bỏ 4 % mép kẻo khung / nền lấn át)."""
    h, w = a.shape
    mx, my = max(1, int(w * .04)), max(1, int(h * .02))
    gx = np.abs(np.diff(a, axis=1))[my:h - my, mx:w - mx - 1]
    gy = np.abs(np.diff(a, axis=0))[my:h - my - 1, mx:w - mx]
    cx, cy = gx.sum(0), gy.sum(1)
    return float(cx.var() / (cx.mean() ** 2 + 1e-6)), float(cy.var() / (cy.mean() ** 2 + 1e-6))


def _do_nghieng(a, buoc=.004, tam=.08):
    """góc xiên còn lại (độ) của vạch đứng trong mặt đã nắn: thử xô ngang x' = x + s·(y − h/2), s nào cho vạch đứng thẳng nhất."""
    h, w = a.shape
    yy = np.arange(h)[:, None] - h / 2
    best, bs = -1, 0.0
    for s in np.arange(-tam, tam + 1e-9, buoc):
        xs = np.arange(w)[None, :] + s * yy
        x0 = np.clip(np.floor(xs).astype(int), 0, w - 2); f = xs - np.floor(xs)
        b = a[np.arange(h)[:, None], x0] * (1 - f) + a[np.arange(h)[:, None], x0 + 1] * f
        d = _diem_thang(b)[0]
        if d > best:
            best, bs = d, s
    return float(np.degrees(np.arctan(-bs)))


def chinh_goc(anh, goc):
    """TỰ NẮN THẲNG: góc chấm bằng mắt lệch vài px là mặt nắn ra bị xiên (ảnh chụp trên cao: cạnh đứng chụm dần xuống dưới,
    mỗi cạnh chụm 1 mức). Dò 2 góc dưới theo x (vạch đứng thẳng, cả độ chụm) rồi 2 góc phải theo y (vạch sàn ngang),
    giữ góc trên-trái. Trả (góc mới, thông tin)."""
    xam = Image.open(anh).convert('L')
    (a, b, c, d) = [list(p) for p in goc]
    L = lambda p, q: float(np.hypot(p[0] - q[0], p[1] - q[1]))
    w0, h0 = max(L(a, b), L(d, c)), max(L(a, d), L(b, c))
    rw, rh = max(48, round(w0 * 2)), max(96, round(h0))
    Rx, Ry = max(4.0, .16 * w0), max(3.0, .035 * h0)

    def dung(dx1, dx2, dy1, dy2):
        return [a, [b[0], b[1] + dy1], [c[0] + dx2, c[1] + dy2], [d[0] + dx1, d[1]]]

    def tim(f, R, cu):
        """lưới thô bước R/8 rồi mịn bước 0,5 px quanh chỗ tốt nhất; f(p, q) → điểm."""
        tot, best = cu, f(*cu)
        for buoc, tam in ((R / 8, R), (.5, R / 8)):
            ds = np.arange(-tam, tam + 1e-9, buoc)
            c0 = tot
            for p in ds:
                for q in ds:
                    v = f(c0[0] + p, c0[1] + q)
                    if v > best:
                        best, tot = v, (c0[0] + p, c0[1] + q)
        return tot, best

    dx = (0.0, 0.0); dy = (0.0, 0.0)
    goc_dau = dung(0, 0, 0, 0)
    v0, h0d = _diem_thang(_nan_xam(xam, goc_dau, rw, rh))
    ng0 = _do_nghieng(_nan_xam(xam, goc_dau, rw, rh))
    for _ in range(2):
        dx, vx = tim(lambda p, q: _diem_thang(_nan_xam(xam, dung(p, q, *dy), rw, rh))[0], Rx, dx)
        dy, vy = tim(lambda p, q: _diem_thang(_nan_xam(xam, dung(*dx, p, q), rw, rh))[1], Ry, dy)
    moi = dung(*dx, *dy)
    v1, h1 = _diem_thang(_nan_xam(xam, moi, rw, rh))
    r = lambda v, n=1: round(float(v), n)
    if v1 < v0 * 1.03 and h1 < h0d * 1.03:          # không khá hơn rõ → giữ góc người chấm
        return [tuple(p) for p in goc], {'chinh': False, 'nghieng_truoc': r(ng0, 2), 'nghieng_sau': r(ng0, 2)}
    ng1 = _do_nghieng(_nan_xam(xam, moi, rw, rh))
    return [tuple(r(v) for v in p) for p in moi], {
        'chinh': True, 'nghieng_truoc': r(ng0, 2), 'nghieng_sau': r(ng1, 2),
        'doi_px': [r(dx[0]), r(dx[1]), r(dy[0]), r(dy[1])],
        'diem_dung': [r(v0, 3), r(v1, 3)], 'diem_ngang': [r(h0d, 3), r(h1, 3)]}


def nan(anh, goc, ra, rong=None, cao=None, sang=1.0):
    im = Image.open(anh).convert('RGB')
    (a, b, c, d) = goc
    L = lambda p, q: float(np.hypot(p[0] - q[0], p[1] - q[1]))
    w0, h0 = max(L(a, b), L(d, c)), max(L(a, d), L(b, c))
    if w0 < 8 or h0 < 8:
        raise SystemExit('⛔ tứ giác quá nhỏ — kiểm lại --goc')
    rong = int(rong or min(512, max(128, round(w0 * 2.2))))
    cao = int(cao or round(rong * h0 / w0))
    hs = _he_so([(0, 0), (rong, 0), (rong, cao), (0, cao)], goc)
    t = im.transform((rong, cao), Image.PERSPECTIVE, hs, Image.BICUBIC)
    if sang and abs(sang - 1) > .01:
        t = Image.fromarray(np.clip(np.asarray(t, np.float32) * sang, 0, 255).astype(np.uint8))
    Path(ra).parent.mkdir(parents=True, exist_ok=True)
    t.save(ra, quality=94)
    return t, im, (w0, h0)


def to_xem(im, goc, t, ra, nhan, goc_cham=None):
    """ảnh soát: ảnh gốc khoanh tứ giác (vàng = vùng dùng; xanh mảnh = góc người chấm nếu đã tự nắn) + PHÓNG vùng cắt
    + texture nắn cùng chiều cao (kẻ vạch đứng / ngang đỏ mảnh để soi thẳng)."""
    H = 900
    k = H / im.height
    g = im.resize((round(im.width * k), H))
    dr = ImageDraw.Draw(g)
    if goc_cham:
        Q = [(x * k, y * k) for x, y in goc_cham]
        dr.line(Q + [Q[0]], fill=(0, 220, 255), width=1)
    P = [(x * k, y * k) for x, y in goc]
    dr.line(P + [P[0]], fill=(255, 214, 0), width=2)
    for i, p in enumerate(P):
        dr.ellipse([p[0] - 4, p[1] - 4, p[0] + 4, p[1] + 4], fill=(255, 60, 60))
    # phóng vùng cắt trong ảnh gốc (để so cạnh tứ giác với cạnh tháp thật)
    xs = [p[0] for p in goc + (goc_cham or [])]; ys = [p[1] for p in goc + (goc_cham or [])]
    m = 8
    hop_ = (max(0, int(min(xs)) - m), max(0, int(min(ys)) - m), min(im.width, int(max(xs)) + m), min(im.height, int(max(ys)) + m))
    z = H / (hop_[3] - hop_[1])
    ph = im.crop(hop_).resize((max(1, round((hop_[2] - hop_[0]) * z)), H), Image.LANCZOS)
    dp = ImageDraw.Draw(ph)
    tf = lambda Pp: [((x - hop_[0]) * z, (y - hop_[1]) * z) for x, y in Pp]
    if goc_cham:
        Q = tf(goc_cham); dp.line(Q + [Q[0]], fill=(0, 220, 255), width=1)
    P = tf(goc); dp.line(P + [P[0]], fill=(255, 214, 0), width=2)
    tt = t.resize((max(1, round(t.width * H / t.height)), H)).convert('RGB')
    dt = ImageDraw.Draw(tt)
    for i in range(1, 4):
        X = tt.width * i / 4; dt.line([(X, 0), (X, H)], fill=(255, 40, 40), width=1)
    for i in range(1, 12):
        Y = H * i / 12; dt.line([(0, Y), (tt.width, Y)], fill=(255, 40, 40), width=1)
    S = Image.new('RGB', (g.width + ph.width + tt.width + 60, H + 46), (18, 18, 20))
    S.paste(g, (0, 46)); S.paste(ph, (g.width + 30, 46)); S.paste(tt, (g.width + ph.width + 60, 46))
    try:
        f = ImageFont.truetype(str(ASSETS / 'fonts' / 'BeVietnamPro-SemiBold.ttf'), 22)
    except OSError:
        f = ImageFont.load_default()
    ImageDraw.Draw(S).text((10, 10), nhan, fill=(255, 255, 255), font=f)
    S.save(ra, quality=88)


def lam(work, anh, goc_s, mid, tang=0, rong=None, sang=1.0, chinh=True):
    work = Path(work)
    if not Path(anh).exists():
        raise SystemExit(f'⛔ không thấy ảnh {anh}')
    if not mid or not all(c.isalnum() or c in '_-' for c in mid):
        raise SystemExit('⛔ --id chỉ gồm chữ không dấu, số, _ hoặc -')
    goc_cham = doc_goc(goc_s)
    rong_cham = max(np.hypot(goc_cham[0][0] - goc_cham[1][0], goc_cham[0][1] - goc_cham[1][1]),
                    np.hypot(goc_cham[3][0] - goc_cham[2][0], goc_cham[3][1] - goc_cham[2][1]))
    if chinh and rong_cham < 45:   # mặt hẹp / tường hồi trơn: ít vạch cửa → bộ dò trượt sang mặt bên (Lumi hoi_dong lấy cả cửa mặt dài)
        loi(f'  mặt hẹp {rong_cham:.0f} px — không tự nắn, dùng nguyên góc chấm (soi kỹ _xem.jpg)')
        chinh = False
    goc, info = (chinh_goc(anh, goc_cham) if chinh else (goc_cham, {'chinh': False}))
    od = work / 'mat_anh'
    ra = od / f'{mid}.jpg'
    t, im, (w0, h0) = nan(anh, goc, ra, rong=rong, sang=sang)
    ng = (f' · tự nắn thẳng: xiên {info["nghieng_truoc"]:+.1f}° → {info["nghieng_sau"]:+.1f}°' if info.get('chinh') else
          (f' · đã thẳng ({info["nghieng_truoc"]:+.1f}°)' if 'nghieng_truoc' in info else ''))
    to_xem(im, goc, t, od / f'{mid}_xem.jpg',
           f'MẶT ĐỨNG "{mid}" — vàng = vùng dùng{", xanh = góc chấm" if info.get("chinh") else ""} · giữa = phóng vùng cắt · phải = texture '
           f'{t.width}×{t.height} (vạch đỏ để soi thẳng){ng}', goc_cham if info.get('chinh') else None)
    so = od / 'mat_anh.json'
    ds = json.loads(so.read_text(encoding='utf-8')) if so.exists() else {}
    ds[mid] = {'file': str(ra), 'anh': str(anh), 'goc': [list(p) for p in goc], 'goc_cham': [list(p) for p in goc_cham], 'tu_nan': info,
               'tang': int(tang or 0), 'rong': t.width, 'cao': t.height, 'nguon_px': [round(w0), round(h0)]}
    so.write_text(json.dumps(ds, ensure_ascii=False, indent=1), encoding='utf-8')
    if w0 < 60:
        loi(f'⚠ mặt cắt chỉ rộng {w0:.0f} px trong ảnh gốc — dán lên tháp to sẽ nhoè; tìm ảnh nét hơn nếu có')
    if info.get('chinh'):
        loi(f'  tự nắn thẳng: góc dưới dời x {info["doi_px"][0]:+.1f} / {info["doi_px"][1]:+.1f} px, góc phải dời y {info["doi_px"][2]:+.1f} / {info["doi_px"][3]:+.1f} px'
            f' → vạch đứng xiên {info["nghieng_truoc"]:+.1f}° → {info["nghieng_sau"]:+.1f}° (--giu-goc để tắt)')
    if abs(info.get('nghieng_sau', 0)) > 1:
        loi(f'⚠ mặt vẫn xiên {info["nghieng_sau"]:+.1f}° — chấm lại 4 góc (luoi-anh --to 3) rồi chạy lại')
    loi(f'✅ {ra}  (gốc {w0:.0f}×{h0:.0f} px → {t.width}×{t.height}) — MỞ {od / (mid + "_xem.jpg")} soi: vạch cửa / cột song song vạch đỏ, '
        f'mép trái/phải là khung tháp, đỉnh/đáy không dính trời / mái / cây')
    return ra


def luoi_anh(anh, vung, ra, to=2.0, buoc=None):
    x0, y0, x1, y1 = [int(float(v)) for v in str(vung).split(',')]
    im = Image.open(anh).convert('RGB').crop((x0, y0, x1, y1))
    im = im.resize((int(im.width * to), int(im.height * to)), Image.LANCZOS)
    b = int(buoc or (5 if to >= 4 else 10 if to >= 3 else 20))
    d = ImageDraw.Draw(im)
    try:
        f = ImageFont.truetype(str(ASSETS / 'fonts' / 'BeVietnamPro-SemiBold.ttf'), 14)
    except OSError:
        f = ImageFont.load_default()
    for x in range((x0 // b + 1) * b, x1, b):
        X = (x - x0) * to; m = x % (b * 5) == 0
        d.line([(X, 0), (X, im.height)], fill=(0, 255, 255) if m else (0, 150, 150), width=1)
        if m:
            d.text((X + 2, 2), str(x), fill=(255, 255, 0), font=f)
    for y in range((y0 // b + 1) * b, y1, b):
        Y = (y - y0) * to; m = y % (b * 5) == 0
        d.line([(0, Y), (im.width, Y)], fill=(255, 0, 255) if m else (150, 0, 150), width=1)
        if m:
            d.text((2, Y + 2), str(y), fill=(255, 255, 0), font=f)
    Path(ra).parent.mkdir(parents=True, exist_ok=True)
    im.save(ra, quality=90)
    loi(f'✅ {ra} — lưới mỗi {b} px ảnh gốc (vạch đậm + số mỗi {b * 5} px). Đọc 4 góc mặt đứng rồi chạy mat-anh')
    return ra
