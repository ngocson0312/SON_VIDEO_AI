# -*- coding: utf-8 -*-
"""Soát kế hoạch (kiem-kh) trước khi dựng + tự kiểm video cuối (kiem) ra soat.jpg."""
import os, math, subprocess
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont
import chung as C


def kiem_kh(plan, work):
    loi, canh_bao = [], []
    if plan.get('CAN_CLAUDE_SUA', True):
        loi.append('CAN_CLAUDE_SUA vẫn true — Claude chưa soát nghĩa từng cảnh (mở tờ khung, chọn clip / giây / tâm rồi đặt false)')
    nh = plan['nhac']
    if not os.path.exists(nh['file']):
        loi.append(f"không thấy file nhạc {nh['file']}")
    P, B, F = nh['phach_s'], nh['nhip_s'], nh['F']
    res = plan.get('res')
    cs = plan['canh']
    tn = C.doc_json(os.path.join(work, 'tai_nguyen.json')) if os.path.exists(os.path.join(work, 'tai_nguyen.json')) else {}
    infos = {v['file']: v for v in tn.get('video', [])}
    dung = {}
    for i, c in enumerate(cs):
        tag = f"cảnh {c['id']} ({c.get('vai', '')})"
        if i == 0 and abs(c['t0']) > 1e-6:
            loi.append(f'{tag}: cảnh đầu phải bắt đầu 0')
        if i and abs(c['t0'] - cs[i - 1]['t1']) > 0.002:
            loi.append(f"{tag}: t0 {c['t0']} không nối liền t1 cảnh trước {cs[i - 1]['t1']}")
        dur = c['t1'] - c['t0']
        if dur < 0.45:
            loi.append(f'{tag}: dài {dur:.2f} s < 0,45 s')
        elif dur < 0.9:
            canh_bao.append(f'{tag}: dài {dur:.2f} s (< 2 phách) — dồn quá gấp')
        if i:
            g = (c['t0'] - F) / (B / 2)
            gp = (c['t0'] - F) / P
            if abs(g - round(g)) * (B / 2) > 0.02:
                if abs(gp - round(gp)) * P > 0.02:
                    loi.append(f"{tag}: cắt ở {c['t0']:.3f} s KHÔNG rơi vào phách (lệch {abs(gp - round(gp)) * P * 1000:.0f} ms)")
                else:
                    canh_bao.append(f"{tag}: cắt ở phách thường, không phải đầu nhịp / nửa nhịp")
            kieu = (c.get('chuyen') or {}).get('kieu', 'cat')
            if kieu not in C.CHUYEN:
                loi.append(f'{tag}: chuyển cảnh lạ "{kieu}" (có: {", ".join(C.CHUYEN)})')
            else:
                truoc = C.CHUYEN[kieu]['truoc']
                tr = cs[i - 1]
                kt = (tr.get('chuyen') or {}).get('kieu', 'cat') if i > 1 else 'cat'
                if truoc + C.CHUYEN.get(kt, C.CHUYEN['cat'])['sau'] > (tr['t1'] - tr['t0']) + 0.01:
                    canh_bao.append(f"{tag}: '{kieu}' ({truoc} s) chồng lên chuyển vào cảnh {tr['id']} — cảnh trước quá ngắn")
        p = C.tim_file(res, c['nguon'])
        if not p:
            loi.append(f"{tag}: không thấy nguồn {c['nguon']}"); continue
        if os.path.splitext(p)[1].lower() in C.VIDEO_EXT:
            v = infos.get(c['nguon']) or C.probe(p)
            toc = float(c.get('toc', 1.0))
            kieu = (c.get('chuyen') or {}).get('kieu', 'cat') if i else 'cat'
            a = float(c.get('tu_giay', 0)) - (C.CHUYEN[kieu]['truoc']) * toc
            b = float(c.get('tu_giay', 0)) + (dur + 0.5) * toc
            if c.get('tu_giay', 0) < 0 or c.get('tu_giay', 0) >= v['dur']:
                loi.append(f"{tag}: tu_giay {c.get('tu_giay')} ngoài clip ({v['dur']:.2f} s)")
            elif b > v['dur'] + 0.05:
                thieu = b - v['dur']
                (loi if thieu > 0.6 * toc else canh_bao).append(
                    f"{tag}: clip hết trước khi cảnh hết {thieu / toc:.2f} s (đứng hình) — lùi tu_giay hoặc giảm toc")
            if a < -0.05:
                canh_bao.append(f'{tag}: đoạn mảnh/chuyển trước cú cắt cần nguồn trước giây 0 ({a:.2f}) — sẽ đứng hình đầu')
            tr = cs[i - 1] if i else None
            noi_tiep = (tr is not None and tr['nguon'] == c['nguon'] and
                        float(c.get('tu_giay', 0)) >= float(tr.get('tu_giay', 0)) + (tr['t1'] - tr['t0']) * float(tr.get('toc', 1)) - 0.05)
            for (s0, s1, cid) in dung.get(c['nguon'], []):
                if noi_tiep and cid == tr['id']:
                    continue      # cảnh nối tiếp đúng mạch cảnh trước (vd hero → thẻ kết qua glitch như mẫu)
                if not (b <= s0 or a >= s1):
                    canh_bao.append(f"{tag}: trùng đoạn nguồn với cảnh {cid} ({c['nguon']})")
            dung.setdefault(c['nguon'], []).append((a, b, c['id']))
        for e in c.get('hieu_ung', []):
            if e.get('kieu') not in ('khung_dien_anh', 'dap_zoom', 'nay', 'manh_tay', 'manh_cho'):
                loi.append(f"{tag}: hiệu ứng lạ \"{e.get('kieu')}\"")
            elif e['kieu'] == 'manh_tay':
                if not (c['t0'] <= float(e.get('t0', -1)) < c['t1']):
                    loi.append(f"{tag}: manh_tay t0 {e.get('t0')} phải nằm trong cảnh")
                nx = cs[i + 1] if i + 1 < len(cs) else None
                if not nx or (nx.get('chuyen') or {}).get('kieu') != 'manh_vo':
                    canh_bao.append(f"{tag}: manh_tay nên đi với chuyển 'manh_vo' vào cảnh sau (mảnh trong tay thành mảnh vỡ)")
                if not os.path.isdir(os.path.join(work, 'tay')):
                    canh_bao.append(f"{tag}: chưa dò tay — chạy run.py tay --work … rồi MỞ tay_{c['id']}.jpg soi chấm tay")
        z = float(c.get('zoom', 1.0))
        if z < 1.0 or z > C.ZOOM_TOI_DA:
            loi.append(f'{tag}: zoom {z} ngoài [1, {C.ZOOM_TOI_DA}]')
        tm = c.get('tam', [0.5, 0.5])
        if not (0 <= tm[0] <= 1 and 0 <= tm[1] <= 1):
            loi.append(f'{tag}: tam {tm} phải trong 0..1')
    ch = plan.get('chu', {})
    for k, mx in (('tieu_de', 12), ('dong_xe', 10)):
        s = ch.get(k, '')
        if s and len(s) > mx:
            canh_bao.append(f'chữ {k} "{s}" dài {len(s)} ký tự (> {mx}) — sẽ nhỏ')
        if s in ('TÊN HÃNG', 'DÒNG XE'):
            loi.append(f'chữ {k} vẫn là chữ giữ chỗ "{s}" — hỏi người dùng tên hãng / dòng xe')
    if ch.get('tieu_de'):
        hero = next((c for c in cs if c.get('vai') == 'hero'), None)
        if hero:
            ket_go = ch['go_tu'] + (len(ch['tieu_de']) - 1) * P / 2
            if ket_go > hero['t1'] - 0.05:
                canh_bao.append(f"gõ chữ xong ở {ket_go:.2f} s, sau khi cảnh hero hết ({hero['t1']:.2f})")
    for s in loi:
        C.in_ra('  ⛔ ' + s)
    for s in canh_bao:
        C.in_ra('  ⚠ ' + s)
    C.in_ra(f'Soát kế hoạch: {len(loi)} lỗi, {len(canh_bao)} cảnh báo' + (' → ĐƯỢC DỰNG' if not loi else ' → SỬA HẾT ⛔ RỒI CHẠY LẠI'))
    return 0 if not loi else 2


def _doc_xam(path, sw=320):
    info = C.probe(path)
    sh = int(round(sw * info['h'] / info['w'] / 2) * 2)
    p = subprocess.Popen(['ffmpeg', '-v', 'error', '-i', path, '-vf', f'scale={sw}:{sh},format=gray', '-f', 'rawvideo', '-'], stdout=subprocess.PIPE)
    raw = p.stdout.read(); p.wait()
    n = len(raw) // (sw * sh)
    return np.frombuffer(raw[:n * sw * sh], np.uint8).reshape(n, sh, sw), info


def kiem_video(plan, work, video):
    import dung as D
    kq = []
    def muc(ten, ok, ghi):
        kq.append((ten, ok, ghi)); C.in_ra(f"  {'ĐẠT ' if ok else 'LỖI '} {ten}: {ghi}")
    nh = plan['nhac']
    T = nh['ket_nhac'] + C.AM['giu_hinh'] + C.AM['den']
    info = C.probe(video)
    muc('1 thời lượng', abs(info['dur'] - T) < 0.08, f"{info['dur']:.2f} s (kế hoạch {T:.2f})")
    I, tp = D.lufs(video)
    muc('2 âm lượng', abs(I - C.AM['lufs']) <= 1.0 and tp <= -1.0, f'{I:.1f} LUFS, TP {tp:.1f} dBFS')
    g, _ = _doc_xam(video)
    n = len(g)
    diff = np.r_[0, np.abs(np.diff(g.astype(np.int16), axis=0)).mean((1, 2))]
    luma = g.mean((1, 2))
    lap = np.array([cv2.Laplacian(f, cv2.CV_64F).var() for f in g])
    # 3 cú cắt đúng mốc: đỉnh khác khung trong ±4 khung quanh mốc
    lech = []
    for c in plan['canh'][1:]:
        s = int(round(C.moc_cat(c) * C.FPS))
        a, b = max(1, s - 4), min(n, s + 5)
        if b <= a:
            continue
        k = a + int(np.argmax(diff[a:b]))
        lech.append((c['id'], k - s))
    xa = [f'#{i}:{d:+d}' for i, d in lech if abs(d) > 2]
    muc('3 cắt đúng phách', not xa, f"{len(lech)} cú cắt, lệch ≤ 2 khung" + (f' — lệch: {", ".join(xa)}' if xa else ''))
    # 4 khung đen ngoài đoạn kết
    t_den = nh['ket_nhac'] + C.AM['giu_hinh']
    den = [i for i in range(int(1.2 * C.FPS), min(n, int(t_den * C.FPS) - 1)) if luma[i] < 10]
    muc('4 không khung đen giữa video', len(den) <= 1, f'{len(den)} khung đen' + (f' (từ {den[0] / C.FPS:.2f} s)' if den else ''))
    # 5 đứng hình (clip hết nguồn)
    dung_y = []
    run = 0
    for i in range(1, int(t_den * C.FPS)):
        run = run + 1 if diff[i] < 0.05 else 0
        if run == int(0.4 * C.FPS):
            dung_y.append(i / C.FPS)
    muc('5 không đứng hình', not dung_y, 'ok' if not dung_y else 'đứng hình ở ' + ', '.join(f'{x:.2f}s' for x in dung_y))
    # 6 nét lại sau chuyển cảnh
    xau = []
    for i, c in enumerate(plan['canh'][1:], 1):
        s = int(round((c['t0'] + 0.5) * C.FPS)); e = int(round(c['t1'] * C.FPS)) - 2
        if e - s < 3 or s >= n:
            continue
        med = np.median(lap[int(c['t0'] * C.FPS):min(n, e)])
        if lap[min(s, n - 1)] < 0.35 * med:
            xau.append(c['id'])
    muc('6 nét lại sau 0,5 s', not xau, 'ok' if not xau else 'còn nhoè ở cảnh ' + ', '.join(map(str, xau)))
    # 7 chữ có mặt ở thẻ kết
    ch = plan.get('chu', {})
    ket = plan['canh'][-1]
    tk = int(round((ket['t0'] + 0.7) * C.FPS))
    if tk < n and ch.get('tieu_de'):
        y = C.CHU['tieu_de']['y'][plan['kho']]
        gh = g.shape[1]
        r = g[tk, int((y - 0.07) * gh):int((y + 0.07) * gh), :]
        trang = float((r > 235).mean())
        muc('7 chữ tên hãng ở thẻ kết', trang > 0.01, f'{trang * 100:.1f} % điểm trắng trong dải chữ')
    # tờ soát
    moc = [min(c['t0'] + (c['t1'] - c['t0']) * 0.55, T - 0.5) for c in plan['canh']]
    moc += [C.moc_cat(c) - 0.12 for c in plan['canh'][1:]]
    moc = sorted(set(round(m, 2) for m in moc if 0 <= m < T))
    p = os.path.join(work, 'soat.jpg')
    to_soat(video, moc, p)
    C.in_ra(f'  → mở {p} soi: chữ đúng chính tả, cảnh đúng nghĩa, không mép đen, chuyển cảnh đẹp')
    loi = [x for x in kq if not x[1]]
    C.in_ra(f'Tự kiểm: {len(kq) - len(loi)}/{len(kq)} ĐẠT')
    return 0 if not loi else 1


def to_soat(video, moc, out, cot=5):
    fr = []
    for t in moc:
        r = subprocess.run(['ffmpeg', '-v', 'error', '-ss', f'{t:.3f}', '-i', video, '-frames:v', '1', '-vf', 'scale=384:-2',
                            '-f', 'image2pipe', '-vcodec', 'png', '-'], capture_output=True)
        im = cv2.imdecode(np.frombuffer(r.stdout, np.uint8), cv2.IMREAD_COLOR)
        if im is not None:
            fr.append((t, im))
    if not fr:
        return
    th, tw = fr[0][1].shape[:2]
    hang = (len(fr) + cot - 1) // cot
    cv = Image.new('RGB', (cot * (tw + 4) + 4, hang * (th + 26) + 4), (12, 12, 12))
    d = ImageDraw.Draw(cv)
    f = ImageFont.truetype(C.font('BarlowCondensed-ExtraBold.ttf'), 20)
    for k, (t, im) in enumerate(fr):
        x = 4 + (k % cot) * (tw + 4); y = 4 + (k // cot) * (th + 26)
        cv.paste(Image.fromarray(cv2.cvtColor(im, cv2.COLOR_BGR2RGB)), (x, y))
        d.text((x + 2, y + th + 2), f'{t:.2f}s', font=f, fill=(255, 220, 0))
    cv.save(out, quality=88)
