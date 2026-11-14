# -*- coding: utf-8 -*-
"""quet.py — bước 1: nhận lời (Whisper, có cache) + quét Resources (clip / ảnh / nhạc) + tờ khung soi + gợi ý khớp tên ↔ lời
+ kế hoạch NHÁP để Claude sửa theo nghĩa."""
import io
import re
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from chung import (AUDIO_EXT, GIONG_TEN, IMG_EXT, NGON_NGU, NHAC_TEN, VIDEO_EXT, bam, bo_dau, doc_json, ghi_json, loi, mo_anh,
                   nhan_loi, probe, run)

# chữ trong tên file KHÔNG mang nghĩa địa điểm (bỏ khi khớp tên ↔ lời)
TU_RONG = {'anh', 'ngam', 'xem', 'view', 'di', 'o', 'cua', 'tai', 'the', 'video', 'clip', 'img', 'image', 'photo', 'ben', 'ngoai',
           'trong', 'tren', 'duoi', 'mot', 'cac', 'nhung', 'va', 'voi', 'bang', 'ngan', 'man', 'canh', 'khung', 'final', 'copy',
           'ket', 'thuc', 'mp4', 'jpg', 'jfif', 'png', 'phim'}
CTA_TU = r'(đăng ký|theo dõi|subscribe|follow|like|chia sẻ|bấm chuông|nhấn chuông|구독|チャンネル登録|订阅)'


def _font(co):
    for f in ('C:/Windows/Fonts/arial.ttf', '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'):
        if Path(f).exists():
            return ImageFont.truetype(f, co)
    return ImageFont.load_default()


def to_khung(f, ma, info, out):
    """tờ khung soi 1 clip: 8–12 khung đều nhau có nhãn giây → Claude chọn đoạn đẹp / tránh tay che."""
    d = info['duration']
    n = 12 if d > 40 else (8 if d > 14 else 6)
    cao = 300
    ims = []
    for k in range(n):
        t = d * (k + .5) / n
        r = run(['ffmpeg', '-v', 'error', '-ss', f'{t:.2f}', '-i', f, '-frames:v', '1', '-vf', f'scale=-2:{cao}', '-f', 'image2pipe',
                 '-c:v', 'mjpeg', '-'], capture=False, check=False, stdout=-1, stderr=-1)
        try:
            im = Image.open(io.BytesIO(r.stdout)).convert('RGB')
        except Exception:
            continue
        dr = ImageDraw.Draw(im)
        dr.rectangle((0, 0, 84, 30), fill=(0, 0, 0))
        dr.text((5, 3), f'{t:.1f}s', font=_font(22), fill=(255, 225, 0))
        ims.append(im)
    if not ims:
        return
    hang = 6 if len(ims) > 6 else len(ims)
    wmax = max(i.width for i in ims)
    so_hang = (len(ims) + hang - 1) // hang
    sh = Image.new('RGB', (hang * (wmax + 4), 36 + so_hang * (cao + 4)), (18, 18, 18))
    for k, im in enumerate(ims):
        sh.paste(im, ((k % hang) * (wmax + 4), 36 + (k // hang) * (cao + 4)))
    ImageDraw.Draw(sh).text((6, 6), f"{ma}  {Path(f).name}  {d:.1f}s  {info['w']}x{info['h']}  "
                                    f"{'DỌC' if info['h'] > info['w'] else 'NGANG'}", font=_font(24), fill=(255, 255, 255))
    sh.save(out, quality=86)


def to_tong(ds, out):
    """tai_nguyen.jpg — mọi tài nguyên 1 ô (khung giữa clip / ảnh) + mã + kích thước."""
    o = []
    for r in ds:
        try:
            if r['loai'] == 'clip':
                rr = run(['ffmpeg', '-v', 'error', '-ss', f"{r['dai'] * .4:.2f}", '-i', r['file'], '-frames:v', '1', '-vf', 'scale=-2:280',
                          '-f', 'image2pipe', '-c:v', 'mjpeg', '-'], check=False, stdout=-1, stderr=-1)
                im = Image.open(io.BytesIO(rr.stdout)).convert('RGB')
            else:
                im = mo_anh(r['file'])
        except Exception:
            continue
        im.thumbnail((400, 280))
        c = Image.new('RGB', (410, 330), (22, 22, 26))
        c.paste(im, ((410 - im.width) // 2, 44))
        dr = ImageDraw.Draw(c)
        dr.text((6, 4), f"{r['ma']}  {r['w']}x{r['h']} {'DỌC' if r['h'] > r['w'] else 'NGANG'}"
                        + (f" {r['dai']:.0f}s" if r['loai'] == 'clip' else ''), font=_font(20), fill=(255, 220, 0))
        dr.text((6, 24), Path(r['file']).name[:38], font=_font(17), fill=(235, 235, 235))
        o.append(c)
    if not o:
        return
    cot = 5
    sh = Image.new('RGB', (cot * 410, ((len(o) + cot - 1) // cot) * 330), (0, 0, 0))
    for k, c in enumerate(o):
        sh.paste(c, ((k % cot) * 410, (k // cot) * 330))
    sh.save(out, quality=86)


def quet_res(res, audio, work, cu):
    """→ danh sách tài nguyên {ma, loai, file, w, h, dai, doc}; GIỮ mã cũ khi quét lại (file mới nhận số kế tiếp)."""
    cu_ma = {r['file']: r['ma'] for r in (cu or [])}
    ds, nhac = [], []
    if not res:
        return ds, nhac
    res = Path(res)
    if not res.is_dir():
        raise SystemExit(f'⛔ Không thấy thư mục Resources {res}')
    so = {'clip': 0, 'res': 0}
    for v in cu_ma.values():
        m = re.match(r'(clip|res)_(\d+)', v)
        if m:
            so[m.group(1)] = max(so[m.group(1)], int(m.group(2)))
    for f in sorted(res.iterdir(), key=lambda p: p.name.lower()):
        if not f.is_file() or f.resolve() == Path(audio).resolve():
            continue
        ext = f.suffix.lower()
        if ext in AUDIO_EXT:
            ten = bo_dau(f.stem)
            if re.search(GIONG_TEN, ten) and not re.search(NHAC_TEN, ten):
                continue
            pa = probe(f)
            if pa['duration'] >= 8:
                nhac.append((f, pa['duration']))
            continue
        if ext not in VIDEO_EXT and ext not in IMG_EXT:
            continue
        loai = 'clip' if ext in VIDEO_EXT else 'anh'
        if loai == 'clip':
            pa = probe(f)
            if not pa['video'] or pa['duration'] < .5:
                continue
            w, h, dai, hdr = pa['w'], pa['h'], pa['duration'], pa['hdr']
        else:
            try:
                im = mo_anh(f)
            except Exception as e:
                loi(f'  ⚠ bỏ ảnh {f.name}: {e}')
                continue
            w, h, dai, hdr = im.width, im.height, 0, False
        fs = str(f.resolve())
        if fs in cu_ma:
            ma = cu_ma[fs]
        else:
            k = 'clip' if loai == 'clip' else 'res'
            so[k] += 1
            ma = f'{k}_{so[k]:02d}'
        ds.append({'ma': ma, 'loai': loai, 'file': fs, 'ten': f.stem, 'w': w, 'h': h, 'dai': round(dai, 2), 'doc': h > w * 1.05,
                   'hdr': hdr})
    for r in cu or []:
        if r['file'] not in {d['file'] for d in ds}:
            loi(f"  ⚠ {r['ma']} ({Path(r['file']).name}) không còn trong Resources")
    return ds, nhac


def khop_ten(ds, tu):
    """khớp tên file ↔ lời: tìm chuỗi chữ (không dấu) trong tên file xuất hiện liền trong lời → giây nhắc. → {ma: [(giây, cụm)]}"""
    loi_bd = [bo_dau(w['w']) for w in tu]
    loi_dau = [re.sub(r'[^\w]+', '', w['w'].lower()) for w in tu]
    o = {}
    for r in ds:
        ten = r['ten'].replace('_', ' ')
        chu = [c for c in bo_dau(ten).split() if c and c not in TU_RONG]
        chu_dau = [re.sub(r'[^\w]+', '', c.lower()) for c in ten.split()]
        best = []
        for L in range(min(4, len(chu)), 0, -1):
            for i in range(len(chu) - L + 1):
                cum = chu[i:i + L]
                if L == 1 and len(cum[0]) < 3:
                    continue
                for j in range(len(loi_bd) - L + 1):
                    # 1 chữ đơn phải khớp CẢ DẤU ("bản" ≠ "bạn", "đồng" ≠ "dòng"); cụm ≥ 2 chữ khớp không dấu (chịu Whisper nghe sai dấu)
                    if L == 1 and loi_dau[j] not in chu_dau:
                        continue
                    if loi_bd[j:j + L] == cum:
                        best.append((tu[j]['s'], ' '.join(w['w'] for w in tu[j:j + L]), L))
            if best:
                break
        if best:
            o[r['ma']] = best
    return o


def loi_doc_txt(tu, cau, work):
    L = ['# lời + giây (Whisper). Mỗi dòng 1 câu; [giây] trước mỗi từ để đặt cảnh / đồ hoạ đúng lúc nói.', '']
    for c in cau:
        ws = [w for w in tu if c['s'] - .01 <= w['s'] <= c['e'] + .01]
        L.append(f"[{c['s']:6.2f}–{c['e']:6.2f}] {c['text']}")
        L.append('    ' + ' '.join(f"{w['w']}⁽{w['s']:.1f}⁾" for w in ws))
    (work / 'loi_doc.txt').write_text('\n'.join(L) + '\n', encoding='utf-8')


def _teaser_nhap(ds, nhip_d, nn):
    """khung MONTAGE TỔNG HỢP ≤ 10 s (khách 14/11/2026 vòng 3: "chỉ giới thiệu 5–10 s, sau giây 10 phải có giọng… đang tuần tự, chưa wao…
    1 cái tổng hợp cả video trong 10 s đầu"): danh sách cảnh THEO THỨ TỰ, script tự xếp lên lưới phách (kiem-kh).
    Nháp (+ 5 kỹ xảo mẫu người dùng gửi 14/11/2026): 3 cảnh BA CỘT có chỗ chừa tên → 1 cảnh tên (khung bung) → 7 cảnh dồn (cảnh cuối
    tự 2 phách cho dải ảnh trượt) → ảnh to thứ 2 làm cảnh đỉnh — Claude chọn lại cảnh ĐẸP NHẤT, đúng điểm đến."""
    import nhip as NH
    from chung import MO_MAN_DAI
    dau = NH.chon_dau(nhip_d, MO_MAN_DAI)
    anh = sorted([r for r in ds if r['loai'] == 'anh'], key=lambda r: -r['w'] * r['h'])
    clip = sorted([r for r in ds if r['loai'] == 'clip'], key=lambda r: (r.get('doc', False), -r['w']))
    tron = []
    for k in range(max(len(anh), len(clip))):
        tron += ([anh[k]] if k < len(anh) else []) + ([clip[k]] if k < len(clip) else [])
    dinh = anh[1] if len(anh) > 1 else (tron[-1] if tron else None)
    con = [r for r in tron if r is not dinh]
    canh = []
    for k, r in enumerate(con[:11]):             # ba cột 4 phách + tên 2 + dồn 6 × ½ + trước đỉnh 2 = 11 + đỉnh 4 = 15 phách ≈ 9,4 s @ 96 BPM
        c = {'nguon': r['ma'], **({'vao': round(r['dai'] * .4, 1)} if r['loai'] == 'clip' else {})}
        if k < 4:
            c.update({'chu': '<TÊN ĐIỂM ĐẾN>', 'nhan': '<1–2 chữ cảm xúc>'})
        canh.append(c)
    if dinh:
        canh.append({'nguon': dinh['ma']})
    return {'kieu': 'tong_hop', 'nhac_tu': round(dau, 3), 'canh': canh,
            'dinh': {'dan': '<dẫn ngắn>', 'khoa': '<CHỮ KHOÁ ĐỈNH, vd "4 điểm đến">', 'viet_tay': '<1 dòng gợi cảm xúc>'},
            '_goi_y': 'MONTAGE TỔNG HỢP ≤ 10 s: liệt kê cảnh THEO THỨ TỰ (không ghi tu — script tự đặt lên lưới phách): '
                      '3 cảnh đầu = BA CỘT (3 điểm đến khác nhau, mỗi cảnh chu = tên + nhan = cảm xúc; khung 0 = ảnh xem trước YouTube); '
                      'điểm đến còn lại mỗi cái 1 cảnh có chu (khung bung / hai nửa tự gán; cảnh thứ 2 CÙNG điểm đến thì không chu, '
                      'cảnh KHÁC điểm đến không chu thì vai "nhanh"; cảnh tên THỨ 2 = CÚ ĐẨY hai nửa → chọn cảnh CÓ NGƯỜI rõ + chu / nhan lấy từ lời); '
                      'sau tên cuối 3–4 cảnh DỒN hay nhất khắp video (mỗi cảnh 1 điểm đến / trải nghiệm khác, sáng rõ, có người; mỗi cảnh 1 phách — '
                      'luật nhịp cắt, thừa thì script bỏ bớt; cảnh dồn cuối = nền dải ảnh trượt); cảnh CUỐI = cảnh ĐỈNH ảnh to nét nhất + dinh.khoa (chữ từ lời). Không lặp đoạn clip với nhau; tránh đoạn mờ / tay / điện thoại.'}


def nhap(ds, tu, cau, dur, nn, khop, nhac, nhip_d=None):
    """kế hoạch NHÁP: mỗi câu 1 cảnh TRÀN MÀN, tài nguyên khớp tên đặt đúng câu nhắc, còn lại xoay vòng; có nhạc → khung TEASER.
    Claude PHẢI sửa theo nghĩa (teaser, chương + toạ độ bản đồ, đồ hoạ, đoạn clip, chuyển cảnh)."""
    dung = {}
    for ma, ks in khop.items():
        for (s, cum, L) in ks[:1]:
            dung.setdefault(round(s, 2), ma)
    canh, ton = [], [r['ma'] for r in ds if r['ma'] not in dung.values()]
    by = {r['ma']: r for r in ds}
    chuyen = ['loe', 'zoom', 'lia', 'hoa_tan', 'truot', 'nhoe']
    k = 0
    for i, c in enumerate(cau):
        ma = None
        for s, m in dung.items():
            if c['s'] - .05 <= s <= c['e'] + .05:
                ma = m
                break
        if ma is None and ton:
            ma = ton.pop(0)
        if ma is None and ds:
            ma = ds[i % len(ds)]['ma']
        if ma is None:
            continue
        r = by[ma]
        canh.append({'id': f'c{len(canh) + 1}', 'tu': round(0 if not canh else c['s'] - .1, 2), 'nguon': ma,
                     'vao': round(r['dai'] * .2, 1) if r['loai'] == 'clip' else 0, 'chuyen': chuyen[k % len(chuyen)] if canh else 'loe',
                     'chuyen_dong': 'zoom_vao' if k % 2 == 0 else 'lia_phai', 'loi': c['text'][:60]})
        k += 1
    cta_tu = None
    for c in reversed(cau):
        if re.search(CTA_TU, c['text'].lower()):
            cta_tu = c['s']
            break
    T = NGON_NGU.get(nn, NGON_NGU['en'])
    return {
        'CAN_CLAUDE_SUA': True,
        'ngon_ngu': nn,
        'kenh': {'ten': '', 'handle': '', 'avatar': None},
        'nhac': str(nhac) if nhac else None,
        'sua_loi': {},
        **({'mo_man': _teaser_nhap(ds, nhip_d, nn)} if nhip_d else {}),
        'canh': canh,
        'do_hoa': [],
        'binh_luan_nn': ['en', 'ko'],
        'cta': {'tu': round(cta_tu if cta_tu is not None else max(0, dur - 5), 2), 'cau_hoi': None, 'lua_chon': [],
                'cam_on': T.get('cam_on'), 'loi_moi': T.get('loi_moi')},
        'sub': {'bat': True, 'giu_lien': []},
    }


def quet(audio, res=None, nhac=None, ngon_ngu=None, work=None):
    audio = Path(audio).resolve()
    if not audio.exists():
        raise SystemExit(f'⛔ Không thấy file audio {audio}')
    work = Path(work) if work else audio.with_name(audio.stem + '_dln_work')
    work.mkdir(parents=True, exist_ok=True)
    (work / 'khung').mkdir(exist_ok=True)
    loi(f'THƯ MỤC WORK: {work}')
    pa = probe(audio)
    st = audio.stat()
    # ---- 1. nhận lời (cache theo file + ngôn ngữ) ----
    lj = work / 'loi.json'
    khoa = bam(str(audio), st.st_size, int(st.st_mtime))
    cu = doc_json(lj) if lj.exists() else {}
    if cu.get('tu') and (cu.get('khoa') == khoa or (not cu.get('khoa') and cu.get('nguon') == str(audio))) \
            and (not ngon_ngu or ngon_ngu == cu.get('ngon_ngu')):
        tu, cau, nn = cu['tu'], cu['cau'], cu.get('ngon_ngu') or 'vi'
        loi(f'1/3 Lời: dùng lại loi.json ({len(tu)} từ, {nn})')
    else:
        loi('1/3 Nhận lời bằng Whisper large-v3 (lần đầu tải ~3 GB; CPU thì vài phút — đừng huỷ) …')
        wav = work / 'giong16k.wav'
        run(['ffmpeg', '-v', 'error', '-y', '-i', audio, '-ac', '1', '-ar', '16000', '-c:a', 'pcm_s16le', wav])
        tu, cau, nn, xs = nhan_loi(wav, ngon_ngu)
        loi(f'  → ngôn ngữ: {nn} ({xs:.2f})')
    ghi_json(lj, {'nguon': str(audio), 'khoa': khoa, 'ngon_ngu': nn, 'dai': round(pa['duration'], 3), 'cau': cau, 'tu': tu})
    loi_doc_txt(tu, cau, work)
    # ---- 2. Resources ----
    loi('2/3 Quét Resources …')
    tj = work / 'tai_nguyen.json'
    cu_ds = doc_json(tj).get('ds', []) if tj.exists() else []
    ds, nhac_ds = quet_res(res, audio, work, cu_ds)
    nhac_f = Path(nhac).resolve() if nhac else (max(nhac_ds, key=lambda x: x[1])[0] if nhac_ds else None)
    if nhac_ds and len(nhac_ds) > 1 and not nhac:
        loi(f'  ⚠ nhiều file âm thanh: lấy {nhac_f.name} (dài nhất) làm nhạc nền — báo người dùng ở cổng duyệt')
    ghi_json(tj, {'res': str(Path(res).resolve()) if res else None, 'ds': ds, 'nhac': str(nhac_f) if nhac_f else None})
    for r in ds:
        out = work / 'khung' / f"{r['ma']}.jpg"
        if r['loai'] == 'clip' and not out.exists():
            to_khung(r['file'], r['ma'], {'duration': r['dai'], 'w': r['w'], 'h': r['h']}, out)
    to_tong(ds, work / 'tai_nguyen.jpg')
    n_doc = sum(1 for r in ds if r['doc'])
    loi(f"  {len(ds)} tài nguyên ({sum(r['loai'] == 'clip' for r in ds)} clip, {sum(r['loai'] == 'anh' for r in ds)} ảnh; "
        f"{n_doc} DỌC → vẫn TRÀN MÀN, dải 16:9 neo cao), nhạc nền: {nhac_f.name if nhac_f else 'không có'}")
    nhip_d = None
    if nhac_f:
        import nhip as NH
        from chung import MO_MAN_DAI
        nhip_d = NH.phan_tich(nhac_f, work)
        loi(f"  teaser: đoạn cao trào gợi ý từ {NH.chon_dau(nhip_d, MO_MAN_DAI):.2f}s của bài")
    # ---- 3. gợi ý + nháp ----
    loi('3/3 Gợi ý khớp tên ↔ lời + kế hoạch nháp …')
    khop = khop_ten(ds, tu)
    G = ['# GỢI Ý: tài nguyên ↔ lời (khớp chữ trong TÊN FILE với lời — chỉ là gợi ý, phải mở ảnh / tờ khung kiểm)', '']
    for r in ds:
        k = khop.get(r['ma'])
        hinh = f"{r['w']}x{r['h']} {'DỌC' if r['doc'] else 'NGANG'}" + (f" {r['dai']:.1f}s" if r['loai'] == 'clip' else ' ảnh')
        if k:
            G.append(f"KHỚP  {r['ma']:8s} {Path(r['file']).name:40s} {hinh:22s} ← " + '; '.join(f'«{c}» {s:.1f}s' for s, c, _ in k[:4]))
        else:
            G.append(f"---   {r['ma']:8s} {Path(r['file']).name:40s} {hinh:22s} (không thấy tên trong lời → ghép theo nghĩa)")
    (work / 'goi_y.txt').write_text('\n'.join(G) + '\n', encoding='utf-8')
    kp = work / 'ke_hoach.json'
    if kp.exists() and not doc_json(kp).get('CAN_CLAUDE_SUA', True):
        loi('  ke_hoach.json đã sửa → GIỮ NGUYÊN (chỉ cập nhật tài nguyên)')
    else:
        ghi_json(kp, nhap(ds, tu, cau, pa['duration'], nn, khop, nhac_f, nhip_d))
    loi(f'XONG. Đọc {work / "goi_y.txt"}, {work / "loi_doc.txt"}, mở tai_nguyen.jpg + khung/*.jpg, rồi viết ke_hoach.json theo NGHĨA.')
    return work
