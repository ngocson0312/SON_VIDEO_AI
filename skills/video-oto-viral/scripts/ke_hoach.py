# -*- coding: utf-8 -*-
"""Lập ke_hoach.json NHÁP: khuôn 13 cảnh của mẫu đặt lên lưới nhịp của nhạc (drop = nhịp 6), gợi ý clip theo
TÊN FILE + độ nét. Claude PHẢI soát lại theo hình (tờ khung) rồi đặt CAN_CLAUDE_SUA = false."""
import os, unicodedata, math
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont
import chung as C

TU_KHOA = {
    'mo_dau': ['dau tien', 'intro', 'mo dau', 'gioi thieu', 'nguoi', 'review'],
    'toan_canh': ['45', '2 phan 3', '3/4', 'goc nghien', 'toan canh', 'tong quan dau'],
    'chi_tiet': ['can den', 'den', 'xi nhan', 'mam', 'banh', 'la zang', 'guong'],
    'logo': ['logo', 'huy hieu', 'ten xe', 'chu', 'can dau xe'],
    'goc_thap': ['zoom out', 'can dau xe', 'capo', 'dau xe', 'goc thap'],
    'noi_that': ['vo lang', 'vi tri lai', 'lai xe', 'man hinh', 'taplo', 'khoang'],
    'chinh_dien': ['thang dau', 'thang', 'chinh dien', 'tong quan dau'],
    'nhanh_1': ['xi nhan guong', 'guong', 'xi nhan', 'den'],
    'nhanh_2': ['man hinh', 'dieu khien', 'can so', 'nut'],
    'nhanh_3': ['ghe', 'yen ngua', 'cho de do', 'khoang'],
    'nhanh_4': ['zoom gan lai dit', 'dit', 'duoi', 'den hau', 'sau xe'],
    'hero': ['2 phan 3', '45', 'goc nghien', 'xoay'],
    'ket': ['xoay', 'tong quan dit', 'goc nghieng dit', 'tong quan', '45'],
}


def bo_dau(s):
    s = s.lower().replace('đ', 'd').replace('_', ' ')
    return ''.join(ch for ch in unicodedata.normalize('NFD', s) if unicodedata.category(ch) != 'Mn')


def diem_ten(vai, ten):
    t = bo_dau(ten)
    sc = 0.0
    for k, kw in enumerate(TU_KHOA.get(vai, [])):
        if kw in t:
            sc += 3.0 - k * 0.25
    return sc


def chon_doan(v, can):
    """Chọn giây vào tốt nhất (nét, ít lia gắt) cho đoạn dài 'can' giây nguồn."""
    d = v.get('diem', [])
    if not d or v['dur'] <= can + 0.1:
        return 0.0
    best = (-1e9, 0.0)
    med = np.median([x['net'] for x in d]) or 1
    for i in range(len(d)):
        a = d[i]['t']
        if a + can > v['dur'] - 0.05:
            break
        win = [x for x in d if a <= x['t'] < a + can]
        if not win:
            continue
        s = np.mean([min(1.5, x['net'] / med) for x in win]) - 0.6 * np.mean([x['xau'] for x in win]) - 0.01 * a
        if s > best[0]:
            best = (s, a)
    return round(float(best[1]), 2)


def lap(work, nhac, tn, kho=None, hang='TÊN HÃNG', dong='DÒNG XE'):
    dx = nhac['de_xuat']
    F, B, P = dx['F'], nhac['nhip_s'], nhac['phach_s']
    n = dx['so_nhip_truoc_drop']
    khuon = [dict(x) for x in C.KHUON]
    bo = ['chi_tiet', 'logo', 'toan_canh'][:max(0, C.DROP_NHIP - n)]
    khuon = [k for k in khuon if k['vai'] not in bo]
    # đánh lại nhịp
    b = 2
    for k in khuon[1:]:
        dai = k['b1'] - k['b0'] if k['b1'] is not None else None
        if k['b0'] < C.DROP_NHIP:
            k['b0'] = b; k['b1'] = b + 1; b += 1
        else:
            k['b0'] = k['b0'] - (C.DROP_NHIP - n)
            k['b1'] = None if dai is None else k['b0'] + dai
    tt = lambda bb: round(F + bb * B, 4)
    ket_nhac = round(tt(khuon[-1]['b0']) + C.AM['ket_phach'] * P, 4)
    video = tn['video'] + [dict(file=a['file'], dur=1e9, w=a['w'], h=a['h'], fps=0, diem=[], co_nguoi=False, doc=a['h'] > a['w'])
                           for a in tn.get('anh', [])]
    dung_roi = {}
    canh = []
    for i, k in enumerate(khuon):
        t0 = 0.0 if i == 0 else tt(k['b0'])
        t1 = ket_nhac if k['b1'] is None else tt(k['b1'])
        # chọn clip: điểm tên + người (mở đầu) − đã dùng
        def sc(v):
            s = diem_ten(k['vai'], v['file'])
            if k['vai'] == 'mo_dau' and v.get('co_nguoi'):
                s += 4
            s -= 5 * dung_roi.get(v['file'], 0)
            return s
        v = max(video, key=sc)
        dung_roi[v['file']] = dung_roi.get(v['file'], 0) + 1
        toc = 0.6 if v.get('fps', 0) >= 50 else 1.0
        kieu = k['vao']
        lead = (C.CHUYEN[kieu]['truoc'] + 0.1) if kieu else 0
        can = (t1 - t0 + lead + 0.6) * toc
        c = dict(id=i + 1, vai=k['vai'], mo_ta=k['mo_ta'], t0=t0, t1=round(t1, 4), nguon=v['file'],
                 tu_giay=chon_doan(v, can) + lead * toc if v['dur'] < 1e8 else 0.0, toc=toc, tam=[0.5, 0.5], zoom=1.0,
                 dong=k['dong'], hieu_ung=[])
        c['tu_giay'] = round(min(c['tu_giay'], max(0.0, v['dur'] - (t1 - t0) * toc - 0.1)), 2) if v['dur'] < 1e8 else 0.0
        # tên file ghi "xoay 90 độ (về bên) trái/phải" → gợi ý xoay lại (Claude PHẢI soát trên tờ khung: chữ / biển số nằm dọc)
        tb = bo_dau(v['file'])
        if 'xoay 90' in tb or 'xoay 90' in tb.replace('do', ''):
            c['xoay'] = -90 if 'trai' in tb.split('xoay 90', 1)[1] else (90 if 'phai' in tb.split('xoay 90', 1)[1] else 0)
        if kieu:
            c['chuyen'] = dict(kieu=kieu)
        if k['vai'] == 'mo_dau':
            c['hieu_ung'] = [dict(kieu='khung_dien_anh', nguoi=bool(v.get('co_nguoi'))), dict(kieu='dap_zoom', t=tt(1))]
        canh.append(c)
    # chuyển mảnh vỡ đầu tiên kết bằng 'nảy' như mẫu, người đứng trước mảnh nếu cảnh mở có người
    if len(canh) > 1 and canh[1].get('chuyen', {}).get('kieu') == 'manh_vo':
        canh[1]['chuyen'].update(ket='nay', nguoi_tren_manh=bool(canh[0]['hieu_ung'][0]['nguoi']))
    vai = {c['vai']: c for c in canh}
    hud_tu = vai['logo']['t0'] if 'logo' in vai else tt(max(2, n - 2))
    plan = dict(CAN_CLAUDE_SUA=True, res=tn['res'], kho=kho or tn.get('kho_de_xuat', '16:9'),
                nhac=dict(file=nhac['file'], bat_dau=dx['bat_dau'], bpm=nhac['bpm'], phach_s=P, nhip_s=B, F=F,
                          drop_video=tt(n), ket_nhac=ket_nhac),
                chu=dict(tieu_de=hang, dong_xe=dong, go_tu=round(vai['hero']['t0'] + C.CHU['go_tre_phach'] * P, 3),
                         dong_xe_tu=round(vai['ket']['t0'] + C.TRE_CAT + C.CHU['dong_xe']['tre'], 3)),
                hud=dict(bat=True, tu=hud_tu, seed=7), mau=dict(bat=True), sfx=False, canh=canh)
    C.ghi_json(os.path.join(work, 'ke_hoach.json'), plan)
    in_bang(plan)
    return plan


def in_bang(plan):
    C.in_ra(f"Khổ {plan['kho']} · nhạc từ {plan['nhac']['bat_dau']:.2f} s · {plan['nhac']['bpm']} BPM · drop ở {plan['nhac']['drop_video']:.2f} s video · "
            f"dài {plan['nhac']['ket_nhac'] + C.AM['giu_hinh'] + C.AM['den']:.2f} s")
    for c in plan['canh']:
        ch = (c.get('chuyen') or {}).get('kieu', '—')
        C.in_ra(f"  {c['id']:>2} {c['t0']:6.2f}–{c['t1']:6.2f}  {c['vai']:<11} ←{ch:<10} {c['nguon'][:44]:<44} @{c['tu_giay']:.2f}s ×{c['toc']}")
    ch = plan['chu']
    C.in_ra(f"  Chữ: '{ch['tieu_de']}' gõ từ {ch['go_tu']:.2f} s · '{ch['dong_xe']}' hiện {ch['dong_xe_tu']:.2f} s · HUD từ {plan['hud']['tu']:.2f} s")


def to_duyet(plan, work, anh):
    """anh = list (t, path, frame) — ghép tờ duyệt có nhãn cảnh."""
    cot = 4
    tw = 480
    th = int(tw * anh[0][2].shape[0] / anh[0][2].shape[1])
    hang = (len(anh) + cot - 1) // cot
    cv = Image.new('RGB', (cot * (tw + 6) + 6, hang * (th + 58) + 8), (14, 14, 14))
    d = ImageDraw.Draw(cv)
    f = ImageFont.truetype(C.font('BarlowCondensed-ExtraBold.ttf'), 22)
    for k, (t, p, fr) in enumerate(anh):
        c = next((c for c in reversed(plan['canh']) if c['t0'] <= t), plan['canh'][0])
        im = Image.fromarray(cv2.cvtColor(cv2.resize(fr, (tw, th), interpolation=cv2.INTER_AREA), cv2.COLOR_BGR2RGB))
        x = 6 + (k % cot) * (tw + 6); y = 8 + (k // cot) * (th + 58)
        cv.paste(im, (x, y))
        ch = (c.get('chuyen') or {}).get('kieu', '')
        d.text((x, y + th + 2), f"{t:.2f}s · #{c['id']} {c['vai']} ← {ch}", font=f, fill=(255, 220, 0))
        d.text((x, y + th + 28), f"{c['nguon'][:40]} @{c['tu_giay']}s", font=f, fill=(200, 200, 200))
    out = os.path.join(work, 'duyet.jpg')
    cv.save(out, quality=88)
    return out
