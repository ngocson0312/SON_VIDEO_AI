# -*- coding: utf-8 -*-
"""quet.py — bước 1: nhận lời (tự nhận ngôn ngữ), lấy bài báo, quét Resources, tờ khung, kế hoạch NHÁP."""
import json
import math
import shutil
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

import re

from chung import (AUDIO_EXT, FONT_DIR, IMG_EXT, NGON_NGU, NHAC_MUC, NHAC_TEN, VIDEO_EXT, bam, bo_dau, doc_json, ghi_json, loi, mo_anh,
                   nhan_loi, probe, run)

TW, TH = 216, 384          # ô tờ khung (dọc)


def _font(sz, dam=True):
    f = FONT_DIR / ('BeVietnamPro-Bold.ttf' if dam else 'BeVietnamPro-Medium.ttf')
    return ImageFont.truetype(str(f), sz)


def _o_anh(im, w, h, nhan=None, nhan2=None):
    """ảnh → ô w×h (giữ tỉ lệ, nền đen) + nhãn."""
    im = im.convert('RGB')
    r = min(w / im.width, h / im.height)
    im2 = im.resize((max(1, int(im.width * r)), max(1, int(im.height * r))), Image.LANCZOS)
    o = Image.new('RGB', (w, h), (18, 18, 22))
    o.paste(im2, ((w - im2.width) // 2, (h - im2.height) // 2))
    d = ImageDraw.Draw(o)
    if nhan:
        f = _font(22)
        bb = d.textbbox((0, 0), nhan, font=f)
        d.rectangle([0, 0, bb[2] + 12, bb[3] + 10], fill=(0, 0, 0))
        d.text((6, 4), nhan, font=f, fill=(255, 214, 90))
    if nhan2:
        f = _font(17, False)
        bb = d.textbbox((0, 0), nhan2, font=f)
        d.rectangle([0, h - bb[3] - 10, min(w, bb[2] + 12), h], fill=(0, 0, 0))
        d.text((6, h - bb[3] - 6), nhan2, font=f, fill=(255, 255, 255))
    return o


def _luoi(o_list, cot, out, tieu_de=None):
    if not o_list:
        return None
    w, h = o_list[0].size
    hang = math.ceil(len(o_list) / cot)
    top = 46 if tieu_de else 0
    sh = Image.new('RGB', (cot * w + (cot + 1) * 6, hang * h + (hang + 1) * 6 + top), (40, 40, 46))
    if tieu_de:
        ImageDraw.Draw(sh).text((10, 8), tieu_de, font=_font(26), fill=(255, 255, 255))
    for i, o in enumerate(o_list):
        sh.paste(o, (6 + (i % cot) * (w + 6), top + 6 + (i // cot) * (h + 6)))
    sh.save(out, quality=88)
    return out


def to_khung_clip(f, cid, dur, out_dir):
    """tờ khung 1 clip: mỗi bước 1 khung có nhãn GIÂY → khung/<cid>.jpg"""
    buoc = 1.0 if dur <= 24 else (2.0 if dur <= 60 else math.ceil(dur / 30))
    tmp = out_dir / f'_{cid}'
    tmp.mkdir(parents=True, exist_ok=True)
    run(['ffmpeg', '-v', 'error', '-y', '-i', f, '-vf', f'fps=1/{buoc},scale={TW}:{TH}:force_original_aspect_ratio=decrease',
         '-q:v', '4', str(tmp / '%04d.jpg')])
    os_ = []
    for i, p in enumerate(sorted(tmp.glob('*.jpg'))):
        t = i * buoc
        if t > dur:
            break
        os_.append(_o_anh(Image.open(p), TW, TH, f'{t:.0f}s'))
    shutil.rmtree(tmp, ignore_errors=True)
    return _luoi(os_, 8, out_dir / f'{cid}.jpg', f'{cid} — {Path(f).name} — {dur:.1f}s (nhãn = giây trong clip)')


def quet_res(res, work):
    kq = []
    if not res:
        return kq
    res = Path(res)
    files = sorted([p for p in res.rglob('*') if p.is_file()], key=lambda p: str(p).lower())
    kd = work / 'khung'
    kd.mkdir(parents=True, exist_ok=True)
    # mã cũ GIỮ NGUYÊN khi quét lại (kế hoạch đã viết trỏ theo mã): file đã có → mã cũ, file mới → số kế tiếp
    cu = {}
    if (work / 'tai_nguyen.json').exists():
        try:
            cu = {str(Path(a['file']).resolve()).lower(): a['id'] for a in doc_json(work / 'tai_nguyen.json').get('ds', [])}
        except Exception:
            cu = {}
    dung_roi = set(cu.values())

    def ma(p, tien_to):
        kp = str(p.resolve()).lower()
        if kp in cu and cu[kp].startswith(tien_to):
            return cu[kp]
        k = 1
        while f'{tien_to}{k:02d}' in dung_roi:
            k += 1
        m = f'{tien_to}{k:02d}'
        dung_roi.add(m)
        return m
    for p in files:
        e = p.suffix.lower()
        if e in VIDEO_EXT:
            cid = ma(p, 'clip_')
            pr = probe(p)
            if not pr['video'] or pr['duration'] < 0.5:
                loi(f'  ⚠ bỏ {p.name} (không đọc được hình)')
                continue
            r = run(['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream=color_transfer', '-of', 'csv=p=0', p],
                    capture=True)
            hdr = (r.stdout or '').strip() in ('smpte2084', 'arib-std-b67')
            to_khung_clip(p, cid, pr['duration'], kd)
            kq.append({'id': cid, 'loai': 'clip', 'file': str(p), 'ten': p.name, 'dai': round(pr['duration'], 2),
                       'w': pr['w'], 'h': pr['h'], 'fps': round(pr['fps'], 2), 'hdr': hdr})
            loi(f"  {cid}: {p.name}  {pr['w']}x{pr['h']}  {pr['duration']:.1f}s{'  HDR' if hdr else ''}")
        elif e in IMG_EXT:
            iid = ma(p, 'res_')
            try:
                im = mo_anh(p)
                w, h = im.size
            except Exception as e:
                loi(f'  ⚠ bỏ ảnh {p.name} ({e})')
                continue
            kq.append({'id': iid, 'loai': 'anh', 'file': str(p), 'ten': p.name, 'w': w, 'h': h})
            loi(f'  {iid}: {p.name}  {w}x{h}')
        elif e in AUDIO_EXT:
            pass                      # file âm thanh trong Resources → xét làm NHẠC NỀN ở tim_nhac()
    mat = [m for f, m in cu.items() if not Path(f).exists()]
    if mat:
        loi(f"  ⚠ file đã bị xoá / đổi tên khỏi Resources: {', '.join(sorted(mat))} — cảnh nào trỏ mã này phải sửa")
    kq.sort(key=lambda a: (a['loai'], a['id']))
    return kq


def tim_nhac(res, audio, nhac=None):
    """LUẬT (người dùng chốt 13/11/2026): Resources CÓ file nhạc nền → ghép vào; KHÔNG có → thôi (giọng + SFX), không hỏi, không nhắc.
    --nhac nếu có; không thì xét file âm thanh trong Resources (trừ chính file giọng, file tên kiểu giọng đọc, tiếng < 8 s):
    1 file → dùng; nhiều file → file có tên kiểu nhạc (Music_Bg, bgm, nhac_nen, beat…); vẫn không rõ → file dài nhất (báo ở D2)."""
    if nhac:
        p = Path(nhac).resolve()
        if not p.exists():
            raise SystemExit(f'⛔ Không thấy file nhạc {p}')
        loi(f'  nhạc nền: {p.name} (--nhac)')
        return str(p)
    if not res or not Path(res).is_dir():
        return None
    giong = str(Path(audio).resolve()).lower()
    ds = sorted([p for p in Path(res).rglob('*') if p.is_file() and p.suffix.lower() in AUDIO_EXT
                 and str(p.resolve()).lower() != giong], key=lambda p: str(p).lower())
    dai = {p: probe(p)['duration'] for p in ds}
    ds = [p for p in ds if dai[p] >= 8]                                     # bỏ tiếng ngắn (SFX lẻ)
    ds = [p for p in ds if not re.search(r'(voice|giong|loi_doc|kich_?ban|thuyet_?minh|narrat|vo_?over|(^|_| )vo(_| |$))', bo_dau_ten(p.stem), re.I)
          or re.search(NHAC_TEN, bo_dau_ten(p.stem), re.I)]                 # bỏ file giọng đọc khác để trong Resources
    if not ds:
        loi('  nhạc nền: Resources không có file nhạc → không nhạc (giọng + SFX)')
        return None
    hop = [p for p in ds if re.search(NHAC_TEN, bo_dau_ten(p.stem), re.I)]
    if len(ds) == 1:
        chon, ly_do = ds[0], 'file âm thanh duy nhất trong Resources'
    elif len(hop) == 1:
        chon, ly_do = hop[0], 'tên kiểu nhạc nền'
    else:
        chon = max(hop or ds, key=lambda p: dai[p])
        ly_do = f"dài nhất trong {', '.join(p.name for p in (hop or ds))} — báo người dùng ở D2"
    loi(f'  nhạc nền: {chon.name} ({dai[chon]:.0f}s; {ly_do})')
    return str(chon.resolve())


def bo_dau_ten(s):
    """tên file → chữ thường không dấu, giữ dấu cách / gạch (để regex tên nhạc bắt được ranh giới từ)."""
    return re.sub(r'[\-_.]+', '_', ' '.join(bo_dau(x) for x in re.split(r'(?<=[a-z0-9])(?=[A-Z])|\s+', s)))


def tai_nguyen_jpg(tn, bai, work):
    """tờ tổng: mỗi clip 1 khung giữa + mọi ảnh bài báo / ảnh Resources, có mã."""
    os_ = []
    for a in tn:
        if a['loai'] == 'clip':
            tmp = work / f"_tn_{a['id']}.jpg"
            run(['ffmpeg', '-v', 'error', '-y', '-ss', f"{a['dai'] / 2:.2f}", '-i', a['file'], '-frames:v', '1', '-q:v', '3', tmp])
            os_.append(_o_anh(Image.open(tmp), TW, TH, a['id'], f"{a['ten'][:22]} {a['dai']:.0f}s"))
            tmp.unlink()
        else:
            os_.append(_o_anh(mo_anh(a['file']), TW, TH, a['id'], a['ten'][:24]))
    for a in (bai or {}).get('anh', []):
        os_.append(_o_anh(Image.open(a['file']), TW, TH, a['id'], (a.get('chu_thich') or a.get('alt') or 'ảnh bài báo')[:26]))
    return _luoi(os_, 6, work / 'tai_nguyen.jpg', 'TÀI NGUYÊN: clip_ / res_ = Resources · bai_ = ảnh bài báo')


def loi_doc_txt(tu, cau, nn, work):
    dong = [f'NGÔN NGỮ AUDIO: {nn} ({NGON_NGU.get(nn, {}).get("ten", "?")}) — MỌI CHỮ TRÊN HÌNH PHẢI VIẾT BẰNG NGÔN NGỮ NÀY (trừ khi người dùng yêu cầu chữ / sub tiếng khác → run.py sub-dich)', '']
    for c in cau:
        dong.append(f"[{c['s']:7.2f} – {c['e']:7.2f}] {c['text']}")
    dong += ['', '--- TỪNG TỪ (giây bắt đầu) ---']
    hang = []
    for w in tu:
        hang.append(f"{w['s']:.2f} {w['w']}")
        if len(hang) == 8:
            dong.append('  |  '.join(hang))
            hang = []
    if hang:
        dong.append('  |  '.join(hang))
    (work / 'loi_doc.txt').write_text('\n'.join(dong), encoding='utf-8')


CTA_TU = (r'(follow|subscribe|theo dõi|đăng ký|đăng kí|kênh|channel|like and share|フォロー|チャンネル登録|구독|팔로우|关注|订阅|'
          r'ติดตาม|abonne|folg|abonnier|sígu|suscrib|seguir|segui|iscriv|ikuti|langganan|подпис|inscreva|siga)')


# ---- khung HÀNH TRÌNH nháp (BẢN ĐỒ THẬT) cho mọi câu nói di chuyển — khách chốt 13/11/2026 ----
_HT_BO_TRUOC = {'sân', 'máy', 'chuyến', 'cuộc'}          # 'sân bay', 'máy bay', 'chuyến đi' là danh từ, không phải lúc rời bến
_HT_CHUNG = {'san', 'bay', 'airport', 'ga', 'ben', 'xe', 'tau', 'anh', 'img', 'photo', 'image', 'pic', 'quoc', 'te', 'international'}
_HT_DI = (r'(?:bay|di chuyển|đi|đến|tới|lái|chạy|khởi hành|xuất phát|cất cánh|tản bộ|fly|flight|drive|driving|walk|ride|take|travel|'
          r'head|depart|移動|飛|乗|비행|이동|출발|飞|坐|开车|เดินทาง|บิน)\b')
_HT_DEN = r'(?:hạ cánh|đến|tới|arriv\w*|reach\w*|land\w*|get to|着|到|도착|抵达|ถึง)\b'
_HT_BAT_DAU = r'\b(?:từ|bắt đầu|xuất phát|khởi hành|from|start\w*|depart\w*)\b|から|에서|从|出发'
_HT_KHOANG = r'(?:khoảng|chừng|tầm|gần|hơn|around|about|approximately|roughly|nearly|over|約|약|大约|大概|ประมาณ)'


def _tg_vi(s):
    """'4 tiếng rưỡi' → '4h30', '40 -50 phút' → '40–50 phút', '2 ,5 km' → '2,5 km' (tiếng Việt); tiếng khác giữ nguyên."""
    s = re.sub(r'\s*([.,])\s*(?=\d)', r'\1', s.strip())
    s = re.sub(r'\s*[-–—~]\s*(?=\d)', '–', s)
    s = re.sub(r'^(\d+)\s*(?:tiếng|giờ)\s*rưỡi$', r'\1h30', s)
    s = re.sub(r'^(\d+)\s*(?:tiếng|giờ)$', r'\1h', s)
    return s.replace('.', ',') if re.search(r'\d\.\d', s) else s


def nhap_hanh_trinh(tu, cau, nn, gy, tat):
    """mỗi câu (chuỗi câu liền) nói DI CHUYỂN → 1 đồ hoạ hanh_trinh nen 'that' đã đặt sẵn giờ (tu / den / luc_di / luc_den /
    luc_tg / luc_kc), phương tiện đoán, thời gian / km đúng lời, ảnh Resources khớp tên gắn điểm đi / đến.
    CHỪA TRỐNG tên + toa_do điểm đi / đến → kiem-kh ⛔ tới khi Claude điền (run.py tim "<tên>"). Dò nhầm → Claude xoá + bo_di_chuyen."""
    from chung import _HT_KC, _HT_SO, _HT_TG, cau_di_chuyen
    dc = cau_di_chuyen(cau, nn)
    nhom = []
    for r in dc:                                    # câu km rồi câu thời gian nối liền → 1 hành trình
        if nhom and r['s'] - nhom[-1][-1]['e'] <= .6:
            nhom[-1].append(r)
        else:
            nhom.append([r])
    ws = [w for w in tu]

    def tim_tu(rx, t0, t1, bo=False):
        for j, w in enumerate(ws):
            if t0 - .01 <= w['s'] <= t1 + .01:
                if bo and j and re.sub(r'\W', '', ws[j - 1]['w'].lower()) in _HT_BO_TRUOC:
                    continue
                ghep = (w['w'] + ' ' + (ws[j + 1]['w'] if j + 1 < len(ws) else '')).lower()
                if re.match(rx, ghep):
                    return w['s']
        return None

    def tim_so(chu, t0, t1):                          # giây của chữ số đầu cụm ('27 km' → giây chữ '27')
        m = re.search(r'\d+', chu)
        for w in ws:
            if t0 - .01 <= w['s'] <= t1 + .01 and (m and re.sub(r'\D', '', w['w']).startswith(m.group(0))):
                return w['s']
        return tim_tu(so, t0, t1)

    khong_dau = [re.sub(r'[^a-z0-9]', '', bo_dau(w['w']).lower()) for w in ws]

    def nhac_ten(k, t0, t1):                          # tên riêng trong tên file ảnh ('sân bay nội bài' → 'noi bai') đọc lúc nào
        ten = [re.sub(r'[^a-z0-9]', '', bo_dau(x).lower()) for x in re.split(r'[\s_\-.,]+', Path(str(tat[k].get('file', ''))).stem)]
        ten = [x for x in ten if x]
        rieng = [x for x in ten if x not in _HT_CHUNG and not x.isdigit()]
        if not rieng:
            return None
        for j, w in enumerate(ws):
            if t0 - .01 <= w['s'] <= t1 + .01 and khong_dau[j:j + len(rieng)] == rieng:
                return w['s']
        return None

    so = r'(?:\d|(?:một|hai|ba|bốn|năm|sáu|bảy|tám|chín|mười|vài|nửa|one|two|three|four|five|six|seven|eight|nine|ten|half)\b)'
    da_gan = set()

    ra = []
    for i, g in enumerate(nhom):
        s_ht, e0 = g[0]['s'], g[-1]['e']
        tu0 = s_ht
        truoc = [c for c in cau if c['e'] <= s_ht + .05 and s_ht - c['e'] <= .6]
        if truoc and re.search(_HT_BAT_DAU, truoc[-1]['text'].lower()) and not cau_di_chuyen([truoc[-1]], nn):
            tu0 = truoc[-1]['s']                     # câu trước nói điểm xuất phát ("bắt đầu từ sân bay Incheon")
        sau = [c['s'] for c in cau if c['s'] >= e0 - .01]
        den = round(min(e0 + .8, (sau[0] + .15) if sau else e0 + .8), 2)
        t_so = tim_tu(so, s_ht, e0)
        t_di = tim_tu(_HT_DI, s_ht, e0, bo=True)
        luc_di = min(x for x in (t_di, t_so, e0 - 2) if x is not None) - .1
        luc_di = max(tu0 + .3, luc_di)
        t_den = tim_tu(_HT_DEN, luc_di + 1.0, e0)
        luc_den = (t_den + .6) if t_den is not None else e0 - 1.0
        luc_den = round(min(max(luc_den, luc_di + 1.6), den - 1.6), 2)
        luc_di = round(min(luc_di, luc_den - 1.2), 2)
        # thời gian / km: cụm đúng lời (giờ đọc = giây chữ số đầu cụm)
        tg = kc = ''
        luc_tg = luc_kc = None
        for c in g:
            t = c['text']
            for m in re.finditer(rf'({_HT_KHOANG}\s+)?({_HT_SO}\s*{_HT_TG}(?:\s*rưỡi)?)', t, re.I):
                if not tg:
                    tg = ('~' if m.group(1) and nn == 'vi' else '') + (_tg_vi(m.group(2)) if nn == 'vi' else m.group(2).strip())
                    luc_tg = tim_so(m.group(2), c['s'], c['e'])
            for m in re.finditer(rf'({_HT_KHOANG}\s+)?({_HT_SO}\s*{_HT_KC})', t, re.I):
                if not kc:
                    kc = ('~' if m.group(1) else '') + (_tg_vi(m.group(2)) if nn == 'vi' else m.group(2).strip())
                    luc_kc = tim_so(m.group(2), c['s'], c['e'])
        if luc_kc is not None:
            luc_kc = min(max(luc_kc, tu0), den - .8)
        luc_tg = round(min(max(luc_tg if luc_tg is not None else (luc_kc or luc_di + .4), tu0), den - .8), 2)
        pt = next((r['pt'] for r in g if r['pt']), None) or 'khong'
        d = {'id': f'h{i + 1}', 'loai': 'hanh_trinh', 'tu': round(tu0, 2), 'den': den, 'phuong_tien': pt, 'nen': 'that',
             'xuat_phat': {'ten': '', 'phu': '', 'toa_do': None}, 'diem_den': {'ten': '', 'phu': '', 'toa_do': None},
             'luc_di': luc_di, 'luc_den': luc_den, 'luc_tg': luc_tg,
             '_loi': ' '.join(c['text'] for c in cau if tu0 - .01 <= c['s'] < e0 - .05),
             '_can_dien': 'tên NGẮN điểm đi / đến (phần phụ vào phu) + toa_do [lat, lon] bằng run.py tim "<tên>" (sân bay = '
                          'aerodrome, di tích = cổng); luc_ten_di / luc_ten_den = giây đọc tên; diem_phu tên nước / thành phố '
                          'khi bay xa; số thời gian / km soát lại đúng lời. Dò nhầm (không phải đi lại) → xoá mục này + ghi '
                          'giây câu vào bo_di_chuyen'}
        if tg:
            d['thoi_gian'] = tg
        if kc:
            d['khoang_cach'] = kc
            if luc_kc is not None:
                d['luc_kc'] = luc_kc
        for k in tat:                                 # ảnh Resources có tên riêng đọc trong câu → gắn ghim điểm đi / đến (mỗi ảnh 1 lần)
            if (tat.get(k) or {}).get('loai') != 'anh' or k in da_gan or not str(k).startswith('res_'):
                continue
            t = nhac_ten(k, tu0, e0)
            if t is None:
                v = (gy or {}).get(k) or {}
                t = next((x for x in v.get('luc') or [] if tu0 - .05 <= x <= e0 + .05), None) if v.get('khop') and not v.get('chung') else None
            if t is not None:
                o = d['xuat_phat'] if t < luc_di else d['diem_den']
                if 'anh' not in o:
                    o['anh'] = k
                    da_gan.add(k)
        ra.append(d)
    return ra


def nhap_ke_hoach(tu, cau, nn, tn, bai, audio_dai, nhac, work, gy=None):
    """kế hoạch NHÁP: mỗi câu 1 cảnh — tài nguyên có tên / chú thích KHỚP RIÊNG lời của câu thì đặt đúng câu đó (goi_y),
    còn lại xoay vòng (clip khớp chung trước → clip → ảnh → ảnh bài báo, chưa dùng trước). Claude PHẢI sửa theo nghĩa."""
    L = NGON_NGU.get(nn, NGON_NGU['en'])
    gy = gy or {}
    tat = {a['id']: a for a in list(tn) + list((bai or {}).get('anh', []))}
    for a in (bai or {}).get('anh', []):
        tat[a['id']]['loai'] = 'anh'
    thu_tu = ([k for k, a in tat.items() if a.get('loai') == 'clip' and (gy.get(k) or {}).get('chung')]
              + [k for k, a in tat.items() if a.get('loai') == 'clip' and not (gy.get(k) or {}).get('chung')]
              + [k for k in tat if k.startswith('res_')] + [k for k in tat if k.startswith('bai_')])
    # tài nguyên khớp RIÊNG → GIỮ CHỖ cho đúng lúc lời nhắc (lần nhắc đầu); câu nhắc nhiều thứ → tách cảnh đúng giây từng thứ (montage)
    moc = sorted((v['luc'][0], k) for k, v in gy.items() if v.get('khop') and not v.get('chung'))
    giu = {k for _, k in moc}
    pool = [k for k in thu_tu if k not in giu] or thu_tu
    ds = []
    for i, c in enumerate(cau):
        cur = {'tu': 0.0 if i == 0 else c['s'], 'nguon': None, 'ghi': '', 'loi': c['text'], 's': c['s'], 'e': c['e']}
        ds.append(cur)
        for t, k in moc:
            if not c['s'] - .05 <= t <= c['e'] + .05:
                continue
            g = f"gợi ý: {k} ↔ «{gy[k]['khop']}» lúc {t:.1f}s"
            if cur['nguon'] is None and t - cur['tu'] <= 2.5:
                cur['nguon'], cur['ghi'] = k, g
            elif t - .1 - cur['tu'] >= 1.2:
                cur = {'tu': round(t - .1, 2), 'nguon': k, 'ghi': g, 'loi': '… ' + gy[k]['khop'], 's': t, 'e': c['e']}
                ds.append(cur)
    # cảnh < 1,2 s (liệt kê đọc nhanh) → nắn ranh: đẩy cảnh sau trễ ≤ 0,35 s, kéo cảnh này sớm hơn; vẫn ngắn → bỏ cảnh này
    i = 0
    while i < len(ds) - 1:
        gap = ds[i + 1]['tu'] - ds[i]['tu']
        if gap >= 1.25:
            i += 1
            continue
        can = 1.25 - gap
        tran_sau = (ds[i + 2]['tu'] - 1.25 if i + 2 < len(ds) else ds[i + 1]['tu'] + .35) - ds[i + 1]['tu']
        d1 = max(0.0, min(can, .35, tran_sau))
        ds[i + 1]['tu'] = round(ds[i + 1]['tu'] + d1, 2)
        can -= d1
        if can > 1e-6 and i > 0:
            d2 = max(0.0, min(can, ds[i]['tu'] - (ds[i - 1]['tu'] + 1.25)))
            ds[i]['tu'] = round(ds[i]['tu'] - d2, 2)
            can -= d2
        if can > 1e-6:
            if i > 0 and ds[i]['nguon'] and not ds[i + 1]['nguon']:
                ds[i + 1]['nguon'], ds[i + 1]['ghi'] = ds[i]['nguon'], ds[i]['ghi']
            ds.pop(i + 1 if i == 0 else i)
            continue
        i += 1
    # cảnh còn trống: lần nhắc SAU của tài nguyên đã giữ chỗ → dùng lại; không thì chọn theo bậc
    # (clip chưa dùng → ảnh chưa dùng → clip còn đoạn chưa dùng → ảnh đã dùng → clip lặp), lâu chưa dùng trước
    het_loi = tu[-1]['e'] if tu else audio_dai
    vao, lan_cuoi = {}, {}

    def con_lai(k):
        return tat[k].get('dai', 0) - vao.get(k, 0.0)

    for i, cd in enumerate(ds):
        dai_canh = (ds[i + 1]['tu'] if i + 1 < len(ds) else het_loi) - cd['tu']
        if cd['nguon'] is None:
            sau = [k for k in giu if any(cd['s'] - .05 <= t <= cd['e'] + .05 for t in gy[k]['luc'][1:])
                   and (tat[k].get('loai') != 'clip' or con_lai(k) >= min(dai_canh, 2.5) + .6)]
            if sau:
                k = sau[0]
                cd['nguon'], cd['ghi'] = k, f"gợi ý: {k} ↔ «{gy[k]['khop']}» (lần nhắc sau)"
            elif pool:
                def bac(k):
                    clip = tat[k].get('loai') == 'clip'
                    dung = k in lan_cuoi
                    if clip:
                        b = 0 if not dung else (2 if con_lai(k) >= min(dai_canh, 3.0) + .6 else 4)
                    else:
                        b = 3 if dung else 1
                    return (b, lan_cuoi.get(k, -99), pool.index(k))
                k = min(pool, key=bac)
                cd['nguon'], cd['ghi'] = k, 'tự lấp — chọn lại theo nghĩa'
        k = cd['nguon']
        cd['vao'] = 0.0
        if k and tat.get(k, {}).get('loai') == 'clip':
            v0 = vao.get(k, 0.0)
            if v0 + min(dai_canh, 3.0) + .6 > tat[k].get('dai', 0):     # + đuôi chuyển cảnh
                v0 = 0.0                                # hết đoạn mới → quay lại đầu (kiem-kh sẽ báo lặp ⚠)
            cd['vao'] = round(v0, 2)
            vao[k] = v0 + dai_canh + .3
        if k:
            lan_cuoi[k] = i
    canh = []
    for i, cd in enumerate(ds):
        a = tat.get(cd['nguon']) or {}
        # ảnh phải phóng > 2 lần mới phủ kín 1080×1920 → để dạng THẺ trên nền nhoè của chính nó
        nho = a.get('loai') == 'anh' and max(1080 / max(1, a.get('w', 1)), 1920 / max(1, a.get('h', 1))) > 2.0
        canh.append({'id': f'c{i + 1:02d}', 'tu': cd['tu'], 'nguon': cd['nguon'], 'vao_giay': cd['vao'],
                     'khung': 'the' if nho else 'tran', 'chuyen': 'cat' if i == 0 else 'hoa_tan', 'chuyen_dong': 'zoom_vao',
                     '_loi': cd['loi'], '_goi_y': cd['ghi']})
    sua_loi = {x: y for v in gy.values() for x, y in (v.get('sua_loi') or {}).items()}
    het = tu[-1]['e'] if tu else audio_dai
    # CTA: câu kêu gọi cuối (theo dõi / follow / đăng ký / 구독 / フォロー …) trong 12 s cuối; không có → câu cuối nếu ngắn
    cta_tu = max(0.0, het - 4.5)
    goi = [c for c in cau if c['s'] >= het - 12 and re.search(CTA_TU, c['text'].lower())]
    if goi:
        cta_tu = max(0.0, goi[-1]['s'] - .05)
    elif cau and het - cau[-1]['s'] <= 6:
        cta_tu = max(0.0, cau[-1]['s'] - .05)
    kh = {
        'CAN_CLAUDE_SUA': True,
        '_huong_dan': 'Sửa theo NGHĨA lời (xem references/ke_hoach_schema.md + references/vi-du-ha-noi.json). Xong đặt CAN_CLAUDE_SUA=false.',
        'ngon_ngu': nn,
        'tieu_de': (bai or {}).get('tieu_de', ''),
        'kenh': {'ten': '', 'handle': '', 'avatar': None},
        'nhac': {'file': nhac, 'muc_db': NHAC_MUC} if nhac else None,
        'sua_loi': sua_loi,
        'sub': {'bat': True},
        'canh': canh,
        'do_hoa': nhap_hanh_trinh(tu, cau, nn, gy, tat),
        'cta': {'tu': round(cta_tu, 2), 'them_giay': 1.6, 'tieu_de': '', 'viet_tay': '',
                'nut': L['nut'], 'nut_da': L['nut_da'], 'icon': ['thich', 'binh_luan', 'chia_se', 'luu'],
                'nhan_icon': {k: L[k] for k in ('thich', 'binh_luan', 'chia_se', 'luu')}},
    }
    ghi_json(work / 'ke_hoach.json', kh)


def quet(audio, link=None, res=None, nhac=None, ngon_ngu=None, work=None):
    audio = Path(audio).resolve()
    if not audio.exists():
        raise SystemExit(f'⛔ Không thấy file audio {audio}')
    work = Path(work) if work else audio.with_name(audio.stem + '_dlv_work')
    work.mkdir(parents=True, exist_ok=True)
    loi(f'THƯ MỤC WORK: {work}')
    pa = probe(audio)
    st = audio.stat()
    # ---- 1. nhận lời (có cache) ----
    lj = work / 'loi.json'
    khoa = bam(str(audio), st.st_size, int(st.st_mtime))
    cu = doc_json(lj) if lj.exists() else {}
    # cùng file audio (khoá cũ có kèm ngôn ngữ vẫn nhận) + không ép ngôn ngữ khác → dùng lại, khỏi chạy Whisper lần nữa
    k_cu = cu.get('khoa')
    cung = bool(cu.get('tu')) and (k_cu in (khoa, bam(str(audio), st.st_size, int(st.st_mtime), None),
                                            bam(str(audio), st.st_size, int(st.st_mtime), cu.get('ngon_ngu')))
                                   or (cu.get('nguon') == str(audio) and not k_cu))
    if cung and (not ngon_ngu or ngon_ngu == cu.get('ngon_ngu')):
        tu, cau = cu['tu'], cu['cau']
        nn = cu.get('ngon_ngu') or ngon_ngu or 'vi'
        loi(f'1/4 Lời: dùng lại loi.json ({len(tu)} từ, ngôn ngữ {nn})')
    else:
        loi('1/4 Nhận lời bằng Whisper large-v3 (CPU, lần đầu tải ~3 GB, lâu — đừng huỷ) …')
        wav = work / 'giong16k.wav'
        run(['ffmpeg', '-v', 'error', '-y', '-i', audio, '-ac', '1', '-ar', '16000', '-c:a', 'pcm_s16le', wav])
        tu, cau, nn, xs = nhan_loi(wav, ngon_ngu)
        loi(f'  → ngôn ngữ nhận ra: {nn} (xác suất {xs:.2f})')
    cu = {'nguon': str(audio), 'khoa': khoa, 'ngon_ngu': nn, 'dai': round(pa['duration'], 3), 'cau': cau, 'tu': tu}
    ghi_json(lj, cu)
    if nn not in NGON_NGU:
        loi(f'  ⚠ ngôn ngữ {nn} chưa có bảng chữ CTA mặc định — Claude tự điền nut / nut_da / nhan_icon bằng {nn}')
    loi_doc_txt(tu, cau, nn, work)
    # ---- 2. bài báo ----
    bai = None
    if link:
        loi(f'2/4 Lấy bài báo {link} …')
        from bai_bao import lay_bai
        try:
            bai = lay_bai(link, work / 'bai_bao')
        except Exception as e:
            loi(f'  ⛔ không lấy được bài báo: {e} — dán nội dung vào {work / "bai_bao" / "bai_bao.txt"} rồi chạy lại')
    else:
        loi('2/4 Không có link bài báo — bỏ qua')
    # ---- 3. Resources ----
    loi(f'3/4 Quét Resources {res or "(không có)"} …')
    tn = quet_res(res, work)
    nhac = tim_nhac(res, audio, nhac)
    ghi_json(work / 'tai_nguyen.json', {'res': str(res) if res else None, 'ds': tn, 'bai': (bai or {}).get('anh', []),
                                        'nguon_bai': (bai or {}).get('nguon', ''), 'nhac': nhac})
    tai_nguyen_jpg(tn, bai, work)
    from goi_y import goi_y
    gy = goi_y(tu, cau, tn, bai, nn, work)
    so = sum(1 for v in gy.values() if v.get('khop') and not v.get('chung'))
    nsl = sum(len(v.get('sua_loi') or {}) for v in gy.values())
    loi(f'  gợi ý ghép: {so}/{len(gy)} tài nguyên khớp riêng một cụm lời'
        + (f', {nsl} chỗ Whisper có thể nghe sai tên' if nsl else '') + ' → goi_y.txt')
    from chung import cau_di_chuyen
    ndc = len(cau_di_chuyen(cau, nn))
    if ndc:
        loi(f'  {ndc} câu nói DI CHUYỂN (số km / phút / tiếng) → cần đồ hoạ hanh_trinh (SKILL mục 13) — xem cuối goi_y.txt')
    # ---- 4. kế hoạch nháp ----
    kh = work / 'ke_hoach.json'
    if kh.exists() and not doc_json(kh).get('CAN_CLAUDE_SUA', True):
        loi('4/4 ke_hoach.json đã được Claude sửa (CAN_CLAUDE_SUA=false) — GIỮ NGUYÊN, không ghi đè')
        k = doc_json(kh)
        if nhac and k.get('nhac') is None:           # chưa có nhạc (null / thiếu) → thêm; false = người dùng tắt nhạc, giữ
            k['nhac'] = {'file': nhac, 'muc_db': NHAC_MUC}
            ghi_json(kh, k)
            loi(f'  + đã thêm nhạc nền {Path(nhac).name} vào ke_hoach.json')
    else:
        nhap_ke_hoach(tu, cau, nn, tn, bai, pa['duration'], nhac, work, gy)
        loi('4/4 Đã ghi ke_hoach.json NHÁP (CAN_CLAUDE_SUA=true; cảnh khớp tên đã đặt đúng câu, sua_loi điền sẵn gợi ý)')
    loi('\nCLAUDE LÀM TIẾP:')
    loi(f'  • đọc {work / "loi_doc.txt"} (ngôn ngữ audio = {nn} → mọi chữ trên hình bằng {nn})')
    loi(f'  • đọc {work / "goi_y.txt"} (tài nguyên ↔ cụm lời + giây, gợi ý sửa lời — chỉ là gợi ý, soi hình rồi mới chốt)')
    if bai:
        loi(f'  • đọc {work / "bai_bao" / "bai_bao.txt"} (số liệu / tên riêng lấy từ đây, chỉ dùng điều KHỚP lời)')
    loi(f'  • MỞ {work / "tai_nguyen.jpg"} + MỌI {work / "khung"}\\clip_XX.jpg (nhãn = giây trong clip)')
    if ndc:
        loi(f'  • kế hoạch nháp ĐÃ CÓ khung hanh_trinh (BẢN ĐỒ THẬT, giờ đặt sẵn) cho câu di chuyển: điền tên ngắn + toa_do '
            f'(run.py tim "<tên>") điểm đi / đến, soát số thời gian / km; mẫu references/vi-du-hanh-trinh-ban-do-that.json')
    loi(f'  • viết {kh} theo nghĩa lời (kiểu câu → đồ hoạ: mục "Khuôn kể chuyện du lịch" trong SKILL.md; trường: '
        f'references/ke_hoach_schema.md) → run.py kiem-kh --work "{work}"')
    return work
