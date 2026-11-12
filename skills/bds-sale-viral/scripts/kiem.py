# -*- coding: utf-8 -*-
"""Tự kiểm: (1) kế hoạch trước khi dựng, (2) file cuối sau khi dựng (+ soat.jpg để Claude soi bằng mắt)."""
import os, re, unicodedata
import numpy as np
import chung as C

KIEU_VAO = set(C.TIEU_DE_VAO); KIEU_RA = set(C.TIEU_DE_RA)


def _bo_dau(s):
    s = unicodedata.normalize('NFD', s.lower()).replace('đ', 'd')
    return ''.join(c for c in s if unicodedata.category(c) != 'Mn')


def _tu(s):
    return [w for w in re.findall(r'[\wÀ-ỹ²]+', re.sub(r'\[|\]', ' ', s.lower())) if w]


def _loi_doan(words, a, b):
    return ' '.join(w['w'] for w in words if w['e'] > a and w['s'] < b)


def kiem_ke_hoach(plan, work, in_ra=True):
    loi, canh = [], []
    dur = float(plan.get('dur', 0))
    words = C.doc_json(os.path.join(work, 'words.json')) if os.path.exists(os.path.join(work, 'words.json')) else []
    cuts = C.doc_json(os.path.join(work, 'cut.json')) if os.path.exists(os.path.join(work, 'cut.json')) else []
    if plan.get('CAN_CLAUDE_SUA'): loi.append('CAN_CLAUDE_SUA vẫn true — Claude chưa sửa kế hoạch theo NGHĨA lời')

    def loi_tg(ten, x):
        t0, t1 = float(x.get('t0', -1)), float(x.get('t1', -1))
        if not (0 <= t0 < t1 <= dur + 0.05): loi.append(f'{ten}: thời gian sai ({t0}–{t1}, video {dur:.2f} s)'); return False
        return True

    def loi_noi(t0, t1):
        return {_bo_dau(w['w']).strip('.,!?…"“”') for w in words if w['e'] >= t0 - 1.2 and w['s'] <= t1 + 1.2}

    # tiêu đề
    tds = sorted(plan.get('tieu_de', []), key=lambda x: x.get('t0', 0))
    prev = None
    for k, td in enumerate(tds):
        ten = f'tiêu đề #{k + 1} "{td.get("khoa", "")}"'
        if not td.get('khoa'): loi.append(ten + ': thiếu khoa'); continue
        if not loi_tg(ten, td): continue
        if td.get('kieu', 'cam') not in C.KIEU_KHOA: loi.append(f'{ten}: kieu lạ {td.get("kieu")} (có: {", ".join(C.KIEU_KHOA)})')
        if td.get('vao', 'roi') not in KIEU_VAO: loi.append(f'{ten}: vao lạ {td.get("vao")}')
        if td.get('ra', 'chui_dau') not in KIEU_RA: loi.append(f'{ten}: ra lạ {td.get("ra")}')
        if td['t1'] - td['t0'] < 1.0: canh.append(f'{ten}: hiện < 1 s — mẫu giữ tiêu đề suốt câu')
        if len(td['khoa']) > 16: canh.append(f'{ten}: khoá dài {len(td["khoa"])} ký tự → chữ nhỏ (mẫu 1–2 chữ)')
        if prev is not None:
            if td['t0'] < prev['t1'] - 0.02: loi.append(f'{ten}: chồng thời gian với tiêu đề trước (kết thúc {prev["t1"]})')
            if td.get('kieu') == prev.get('kieu'): canh.append(f'{ten}: cùng kiểu màu với tiêu đề trước ({td.get("kieu")})')
        noi = loi_noi(td['t0'], td['t1'])
        la = [w for w in _tu(' '.join(str(td.get(x) or '') for x in ('dan', 'khoa', 'viet_tay'))) if not w.isdigit()]
        thieu = [w for w in la if _bo_dau(w) not in noi]
        if thieu and words: canh.append(f'{ten}: chữ không có trong lời quanh đó: {", ".join(thieu)}')
        if td.get('icon') and td['icon'] not in ('chia_khoa_nha', 'tui_tien', 'bieu_do'):
            loi.append(f'{ten}: icon lạ {td["icon"]}')
        prev = td
    # sub
    subs = sorted(plan.get('sub', []), key=lambda x: x.get('t0', 0))
    for k, s in enumerate(subs):
        ten = f'sub #{k + 1} {s.get("t0")}s'
        if not loi_tg(ten, s): continue
        if not s.get('dong'): loi.append(ten + ': không có dòng'); continue
        if k and s['t0'] < subs[k - 1]['t1'] - 0.05: loi.append(f'{ten}: chồng sub trước ({subs[k - 1]["t1"]})')
        for d in s['dong']:
            tx = re.sub(r'[\[\]]', '', d.get('text', ''))
            if d.get('kieu') not in (None, 'chinh', 'phu', 'to', 'vang', 'list'): loi.append(f'{ten}: kieu dòng lạ {d.get("kieu")}')
            if len(tx) > 24 or len(tx.split()) > 5: canh.append(f'{ten}: dòng "{tx}" dài — mẫu 1–4 chữ/cụm')
        noi = loi_noi(s['t0'], s['t1'])
        la = [w for w in _tu(' '.join(d.get('text', '') for d in s['dong'])) if not re.match(r'^\d', w) and w != 'm²']
        thieu = [w for w in la if _bo_dau(w) not in noi]
        if thieu and words: canh.append(f'{ten}: chữ sub không khớp lời: {", ".join(thieu)}')
    # đồ hoạ phụ
    for k, th in enumerate(plan.get('the_anh', [])):
        ten = f'thẻ ảnh #{k + 1}'
        loi_tg(ten, th)
        for p in th.get('nguon', []):
            if not os.path.exists(p): loi.append(f'{ten}: thiếu file {p}')
        if th.get('kieu', 'phang') not in ('phang', 'nghieng', 'xep', 'nho'): loi.append(f'{ten}: kieu lạ {th.get("kieu")}')
        if th.get('dat') == 'tay' and th.get('kieu') == 'nho': loi.append(f'{ten}: dat "tay" không dùng với kieu "nho"')
    # icon / thẻ ảnh trên TAY: chỉ khi người nói MỞ TAY (tay.json từ run.py nguoi)
    import tay
    kq_tay = tay.doc(work)
    xep = tay.xep(plan, kq_tay) if kq_tay else {}
    for k, ic in enumerate(plan.get('icon', [])):
        loi_tg(f'icon #{k + 1}', ic)
        if ic.get('loai') not in C.ICON['mau']: loi.append(f'icon #{k + 1}: loai lạ {ic.get("loai")} (có: {", ".join(C.ICON["mau"])})')
        if kq_tay is not None and ic.get('tay', True) is not False and ('icon', k) not in xep:
            canh.append(f'icon #{k + 1} ({ic.get("nhan")}, {ic["t0"]}s): không có cử chỉ mở tay quanh đó → trượt từ mép vào '
                        f'(mẫu: icon mọc từ lòng bàn tay — xem tay.jpg, dời icon sang lúc tay mở nếu hợp lời)')
    for k, th in enumerate(plan.get('the_anh', [])):
        if th.get('dat') == 'tay' and kq_tay is not None and ('the_anh', k) not in xep:
            canh.append(f'thẻ ảnh #{k + 1} ({th["t0"]}s): dat "tay" mà không có cử chỉ mở tay → nằm giữa khung')
    if kq_tay is not None and kq_tay.get('nguon') != 'mediapipe':
        canh.append('dò tay đang dùng mặt nạ người (chỉ bắt DANG TAY ngang) — chạy run.py cai-tay để bắt mọi cử chỉ')
    if kq_tay is not None:
        # khoảng tay RẢNH dài mà không có icon / thẻ nào mọc từ tay
        # khoảng trống tính từ lúc đồ hoạ trên tay KẾT THÚC tới lúc cái sau bắt đầu (không phải từ lúc nó bắt đầu)
        moc = sorted((v['t0'], float(plan[kk[0]][kk[1]]['t1'])) for kk, v in xep.items())
        trong = []
        for c in kq_tay.get('cu_chi', []):
            cur, ds = c['t0'], []
            for a, b in moc:
                if b <= c['t0'] or a >= c['t1']: continue
                if a > cur: ds.append((cur, a))
                cur = max(cur, b)
            ds.append((cur, c['t1']))
            for a, b in ds:
                if b - a >= C.TAY['trong_s']: trong.append(dict(c, t0=round(a, 2), t1=round(b, 2), loi=_loi_doan(words, a, b)))
        for c in trong[:6]:
            canh.append(f'{c["t0"]:.2f}–{c["t1"]:.2f}s người nói làm cử chỉ tay {"TRÁI" if c["ben"] == "trai" else "PHẢI"} '
                        f'(«{c.get("loi", "")[:30]}») mà chưa có icon / thẻ — nên đặt 1 icon nhãn = chữ đắt đang nói '
                        f'(tay.jpg; gợi ý sẵn: run.py tay --gop)')
    for k, tk in enumerate(plan.get('tim_kiem', [])):
        if loi_tg(f'ô tìm kiếm #{k + 1}', tk):
            tg = float(tk.get('t_go', tk['t0'] + 0.3)); can = len(tk.get('chu', '')) / C.FPS
            if tg + can > tk['t1'] - 0.3: canh.append(f'ô tìm kiếm #{k + 1}: gõ xong lúc {tg + can:.2f}s, sát/quá lúc tắt {tk["t1"]}')
    so_noi = re.sub(r'[.,]', '', ' '.join(w['w'] for w in words))
    for k, st in enumerate(plan.get('so_tien', [])):
        if not loi_tg(f'số tiền #{k + 1}', st): continue
        for s in st.get('so', []):
            dau = re.match(r'\d+', re.sub(r'[.,]', '', s.get('text', '')))
            if dau and words and dau.group(0)[:1] not in so_noi:
                canh.append(f'số tiền #{k + 1}: "{s.get("text")}" — chữ số không có trong lời (KHÔNG bịa số)')
    for k, lg in enumerate(plan.get('logo', [])):
        loi_tg(f'logo #{k + 1}', lg)
        if not lg.get('nguon') or not os.path.exists(lg['nguon']): loi.append(f'logo #{k + 1}: thiếu file logo')
    for k, lk in enumerate(plan.get('liet_ke', [])):
        loi_tg(f'liệt kê #{k + 1}', lk)
    bc = [c['t'] for c in cuts if c.get('loai') == 'boi_canh']
    for c in plan.get('chuyen', []):
        if c.get('kieu') not in C.CHUYEN: loi.append(f'chuyển cảnh {c.get("t")}: kieu lạ {c.get("kieu")} (có: {", ".join(C.CHUYEN)})')
        if bc and not any(abs(c['t'] - t) < 0.2 for t in bc):
            canh.append(f'chuyển cảnh {c["t"]}s không trùng cú đổi bối cảnh nào (cut.json) — mẫu chỉ đặt ở chỗ đổi bối cảnh')
    for z in plan.get('zoom', []):
        if not (0.95 <= float(z.get('z', 1)) <= 1.45): canh.append(f'zoom {z.get("t")}s: z={z.get("z")} ngoài 1,0–1,4')
    if plan.get('nhac') and not os.path.exists(plan['nhac']): loi.append('nhạc: không thấy file ' + plan['nhac'])
    if not plan.get('nhac'): canh.append('chưa có nhạc nền — video mẫu có beat lo-fi ~93 BPM dưới giọng ~9 dB (hỏi ở cổng duyệt)')
    if (plan.get('tieu_de') or plan.get('logo')) and not os.path.exists(os.path.join(work, 'nguoi_mask.json')):
        canh.append('chưa tách người (run.py nguoi) — bước dung sẽ tự chạy, mất thêm vài phút')
    # chỗ nói dài mà không có chữ nào
    if words and dur:
        phu = np.zeros(int(dur * 10) + 2, bool)
        for key in ('tieu_de', 'sub', 'so_tien', 'liet_ke', 'tim_kiem', 'the_anh'):
            for x in plan.get(key, []):
                phu[int(x['t0'] * 10):int(x['t1'] * 10) + 1] = True
        trong, bd = [], None
        for w in words:
            k = int((w['s'] + w['e']) / 2 * 10)
            if k < len(phu) and not phu[k]:
                bd = w['s'] if bd is None else bd
                if w['e'] - bd > 1.5 and (not trong or trong[-1][0] != bd): trong.append([bd, w['e']])
                elif trong and trong[-1][0] == bd: trong[-1][1] = w['e']
            else: bd = None
        for a, b in trong: canh.append(f'{a:.1f}–{b:.1f}s đang nói mà không có chữ (mẫu luôn có sub/tiêu đề)')
    if in_ra:
        for x in loi: print('  ⛔', x)
        for x in canh: print('  ⚠', x)
        print(f'Kiểm kế hoạch: {len(loi)} ⛔, {len(canh)} ⚠' + (' — ĐẠT' if not loi else ''))
    return loi


# ------------------------------------------------------------------ kiểm file cuối
def kiem_video(plan, work, video):
    import am_thanh, dung
    from PIL import Image, ImageDraw
    print(f'\nTỰ KIỂM {video}')
    kq = []

    def ghi(ok, ten, chi=''):
        kq.append((ok, ten, chi)); print(('  ✅ ' if ok is True else ('  ⚠ ' if ok is None else '  ⛔ ')) + ten + (' — ' + chi if chi else ''))

    pr = C.probe(video)
    dur = float(plan['dur'])
    ghi(pr.get('w') == C.W and pr.get('h') == C.H and abs(pr.get('fps', 0) - C.FPS) < 0.1, '1. Khổ 1080x1920, 30 fps',
        f'{pr.get("w")}x{pr.get("h")} {pr.get("fps", 0):.2f} fps')
    ghi(abs(pr['dur'] - dur) < 0.2, '2. Độ dài khớp nguồn', f'{pr["dur"]:.2f} s / {dur:.2f} s')
    I, tp = am_thanh.lufs(video)
    ghi(abs(I - C.AM['lufs']) <= 1.0 and tp <= -1.0, '3. Âm lượng −14 LUFS, đỉnh ≤ −1 dBTP', f'{I:.1f} LUFS, {tp:.1f} dBTP')
    D = dung.Dung(plan, work)
    # 4. tiêu đề sau người + đọc được
    if D.tds:
        if D.kho is None or not D.kho.ok:
            ghi(False, '4. Tiêu đề nằm SAU người', 'chưa có mặt nạ người')
        else:
            te = []
            for td in D.tds:
                if not td['sau']: continue
                i = (td['i0'] + td['i1']) // 2; M = D.cam(i); m = D.mask(i, M)
                K = td['K']; P = dung.pm(K)[K.oy:K.oy + K.h, K.ox:K.ox + K.w, 3]
                x0, y0 = int(td['kpos'][0] - K.w / 2), int(td['kpos'][1] - K.h / 2)
                a0, b0, a1, b1 = max(0, x0), max(0, y0), min(C.W, x0 + K.w), min(C.H, y0 + K.h)
                if a1 <= a0 or b1 <= b0: continue
                al = P[b0 - y0:b1 - y0, a0 - x0:a1 - x0]; mm = m[b0:b1, a0:a1]
                che = float((al * mm).sum() / max(1e-6, al.sum()))
                if che > 0.45: te.append(f'"{K.meta["text"]}" bị đầu che {che:.0%}')
            ghi(None if te else True, '4. Tiêu đề nằm SAU người, đầu che ≤ 45 %', '; '.join(te))
    else:
        ghi(None, '4. Tiêu đề', 'kế hoạch không có tiêu đề nào')
    # 5. sub không đè mặt + vùng an toàn
    de, ra_ngoai = [], []
    A = C.AN_TOAN
    for o in D.dongs:
        i = (o['ii'] + o['io']) // 2; m = D.mat_ra(i)
        x0, y0, x1, y1 = o['x'] - o['A'].w / 2, o['y'] - o['A'].h / 2, o['x'] + o['A'].w / 2, o['y'] + o['A'].h / 2
        ix = max(0, min(x1, m[2]) - max(x0, m[0])) * max(0, min(y1, m[3]) - max(y0, m[1]))
        if ix > 0.10 * (m[2] - m[0]) * (m[3] - m[1]): de.append(f'{i / C.FPS:.1f}s')
        if x0 < A['x0'] - 2 or x1 > A['x1'] + 2 or y1 > A['y1']: ra_ngoai.append(f'{i / C.FPS:.1f}s')
    ghi(False if de else True, '5. Sub không đè mặt', ', '.join(de[:8]))
    for td in D.tds:
        K = td['K']; x0, x1 = td['kpos'][0] - K.w / 2, td['kpos'][0] + K.w / 2
        if x0 < A['x0'] - 2 or x1 > A['x1'] + 2 or td['kpos'][1] - K.h / 2 < A['y0'] - 40:
            ra_ngoai.append(f'tiêu đề "{K.meta["text"]}"')
    ghi(None if ra_ngoai else True, '6. Chữ trong vùng an toàn (không bị UI che)', ', '.join(ra_ngoai[:8]))
    # 7. SFX
    ds = C.doc_json(os.path.join(work, 'sfx.json')) if os.path.exists(os.path.join(work, 'sfx.json')) else []
    if plan.get('sfx') is False:
        ghi(None, '7. SFX', 'tắt theo kế hoạch')
    else:
        from collections import Counter
        ct = Counter(d['file'] for d in ds)
        top = ct.most_common(1)[0] if ct else ('', 0)
        thieu = [c['t'] for c in plan.get('chuyen', []) if not any(abs(d['t'] - c['t']) < 0.15 for d in ds)]
        ok = len(ds) >= 4 and (len(ds) < 10 or len(ct) >= 6) and (not ds or top[1] / len(ds) <= 0.35) and not thieu
        ghi(ok, '7. SFX đa dạng, chuyển cảnh nào cũng có tiếng',
            f'{len(ds)} tiếng / {len(ct)} loại, nhiều nhất {top[0]} {top[1]}' + (f'; chuyển cảnh thiếu tiếng: {thieu}' if thieu else ''))
    # 8. nhạc
    bc = C.doc_json(os.path.join(work, 'am_thanh.json')) if os.path.exists(os.path.join(work, 'am_thanh.json')) else {}
    if plan.get('nhac'):
        d = bc.get('nhac_duoi_giong_db')
        ghi(d is not None and 6 <= d <= 12, '8. Nhạc nền thấp hơn giọng ~9 dB', f'{d} dB')
    else:
        ghi(None, '8. Nhạc nền', 'không có nhạc (mẫu có beat lo-fi)')
    # 9. tờ soát
    moc = []
    for td in D.tds: moc.append((min(td['i1'], td['i0'] + 16), 'TĐ ' + td['K'].meta['text']))
    for key, ten in (('the_anh', 'thẻ'), ('icon', 'icon'), ('tim_kiem', 'tìm'), ('logo', 'logo'), ('liet_ke', 'liệt kê')):
        for x in plan.get(key, []): moc.append((C.khung((x['t0'] + x['t1']) / 2), ten))
    for st in plan.get('so_tien', []):
        for s in st.get('so', []): moc.append((C.khung(s.get('t', st['t0'])) + 10, 'số ' + s.get('text', '')))
    for c in plan.get('chuyen', []): moc.append((C.khung(c['t']), 'chuyển ' + c['kieu']))
    rest = [o for o in D.dongs]
    for o in rest[::max(1, len(rest) // 10)]: moc.append(((o['ii'] + o['io']) // 2, 'sub'))
    moc = sorted({m[0]: m for m in moc if 0 <= m[0] < D.n}.values())
    out = os.path.join(work, 'soat.jpg')
    rong, oh, cot = 270, 480, 8
    tiles = []
    fo = C.font('BeVietnamPro-Bold.ttf', 17)
    for i, nhan in moc:
        fr = dung.doc_khung(video, i / C.FPS + 0.001)
        if fr is None: continue
        im = Image.fromarray(fr).resize((rong, oh))
        t = Image.new('RGB', (rong, oh + 40), (16, 16, 16)); t.paste(im, (0, 40))
        dd = ImageDraw.Draw(t); dd.text((4, 2), f'{i / C.FPS:.2f}s', font=fo, fill=(255, 220, 80)); dd.text((4, 20), nhan[:28], font=fo, fill=(230, 230, 230))
        tiles.append(t)
    if tiles:
        r = (len(tiles) + cot - 1) // cot
        sh = Image.new('RGB', (cot * (rong + 4), r * (oh + 44)), (6, 6, 6))
        for k, t in enumerate(tiles): sh.paste(t, ((k % cot) * (rong + 4), (k // cot) * (oh + 44)))
        sh.save(out, quality=86)
    ghi(None, '9. Tờ soát bằng mắt', out + ' — Claude PHẢI mở soi chính tả, chữ sau đầu, không đè mặt')
    loi = sum(1 for k in kq if k[0] is False)
    print(f'KẾT QUẢ: {sum(1 for k in kq if k[0] is True)} ✅ · {sum(1 for k in kq if k[0] is None)} ⚠ · {loi} ⛔')
    C.ghi_json(os.path.join(work, 'kiem.json'), [{'ok': k[0], 'muc': k[1], 'chi_tiet': k[2]} for k in kq])
    return loi == 0
