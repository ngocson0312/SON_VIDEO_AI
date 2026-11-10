# -*- coding: utf-8 -*-
"""Quét thư mục Resources: phân loại clip / ảnh / nhạc, đo từng clip (độ nét, độ rung theo 0,5 s, có người),
xuất tờ khung có nhãn giây cho Claude chọn đoạn: tai_nguyen.jpg (tổng quan) + khung/clip_XX.jpg."""
import os, subprocess
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont
import chung as C

_HOG = None


def _co_nguoi(img):
    """Có người (mặt hoặc dáng đứng) trong khung không — chỉ để gợi ý cảnh mở đầu."""
    global _HOG
    g = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    fc = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    f = fc.detectMultiScale(g, 1.15, 6, minSize=(max(24, g.shape[0] // 18),) * 2)
    if len(f):
        return True
    if _HOG is None:
        _HOG = cv2.HOGDescriptor(); _HOG.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())
    s = 640 / max(img.shape[:2])
    r, w = _HOG.detectMultiScale(cv2.resize(img, None, fx=s, fy=s), winStride=(8, 8))
    return bool(len(r) and (np.array(w).max() > 0.9))


def doc_khung_deu(path, info, buoc, sw=480):
    sh = int(round(sw * info['h'] / info['w'] / 2) * 2)
    p = subprocess.Popen(['ffmpeg', '-v', 'error', '-i', path, '-vf', f'fps=1/{buoc},scale={sw}:{sh}', '-pix_fmt', 'bgr24',
                          '-f', 'rawvideo', '-'], stdout=subprocess.PIPE)
    raw = p.stdout.read(); p.wait()
    n = len(raw) // (sw * sh * 3)
    return np.frombuffer(raw[:n * sw * sh * 3], np.uint8).reshape(n, sh, sw, 3)


def do_clip(path, info):
    """Mỗi 0,25 s: độ nét (Laplacian), độ động (khác khung). Trả list theo 0,5 s + khung minh hoạ."""
    buoc = 0.25
    fr = doc_khung_deu(path, info, buoc, 320)
    net, dong = [], []
    prev = None
    for f in fr:
        g = cv2.cvtColor(f, cv2.COLOR_BGR2GRAY)
        net.append(float(cv2.Laplacian(g, cv2.CV_64F).var()))
        dong.append(0.0 if prev is None else float(np.abs(g.astype(np.int16) - prev).mean()))
        prev = g.astype(np.int16)
    return net, dong, buoc


def to_khung(path, info, out, nhan, buoc=0.5, cot=6):
    fr = doc_khung_deu(path, info, buoc, 300)
    if len(fr) == 0:
        return 0
    if len(fr) > 60:
        idx = np.linspace(0, len(fr) - 1, 60).astype(int); fr = fr[idx]; ts = idx * buoc
    else:
        ts = np.arange(len(fr)) * buoc
    h, w = fr.shape[1:3]
    hang = (len(fr) + cot - 1) // cot
    tw = 300; th = int(tw * h / w)
    canvas = Image.new('RGB', (cot * (tw + 4) + 4, hang * (th + 4) + 44), (20, 20, 20))
    d = ImageDraw.Draw(canvas)
    fnt = ImageFont.truetype(C.font_hud(), 16); fb = ImageFont.truetype(C.font('BarlowCondensed-ExtraBold.ttf'), 26)
    d.text((8, 8), nhan, font=fb, fill=(255, 220, 0))
    for k, (f, s) in enumerate(zip(fr, ts)):
        im = Image.fromarray(cv2.cvtColor(cv2.resize(f, (tw, th)), cv2.COLOR_BGR2RGB))
        x = 4 + (k % cot) * (tw + 4); y = 44 + (k // cot) * (th + 4)
        canvas.paste(im, (x, y))
        d.rectangle([x, y, x + 58, y + 20], fill=(0, 0, 0))
        d.text((x + 3, y + 2), f'{s:.1f}s', font=fnt, fill=(255, 255, 0))
    canvas.save(out, quality=88)
    return len(fr)


def chay(res, work):
    os.makedirs(os.path.join(work, 'khung'), exist_ok=True)
    files = sorted(os.listdir(res))
    video, anh, nhac = [], [], []
    for fn in files:
        p = os.path.join(res, fn)
        if not os.path.isfile(p):
            continue
        ext = os.path.splitext(fn)[1].lower()
        if ext in C.NHAC_EXT:
            nhac.append(dict(file=fn))
        elif ext in C.ANH_EXT:
            try:
                im = Image.open(p); anh.append(dict(file=fn, w=im.width, h=im.height))
            except Exception:
                C.in_ra(f'  ⚠ không đọc được ảnh {fn}')
        elif ext in C.VIDEO_EXT:
            info = C.probe(p)
            if not info or info['dur'] <= 0.3:
                C.in_ra(f'  ⚠ bỏ {fn} (không đọc được / quá ngắn)'); continue
            video.append(dict(file=fn, **info))
    if not video and not anh:
        raise RuntimeError(f'Không có clip / ảnh nào trong {res}')
    tq = []
    for i, v in enumerate(video, 1):
        p = os.path.join(res, v['file'])
        C.in_ra(f'  [{i:02d}] {v["file"]} · {v["dur"]:.1f} s · {v["w"]}x{v["h"]} · {v["fps"]:.0f} fps' + (' · HDR' if v['hdr'] else ''))
        net, dong, buoc = do_clip(p, v)
        net = np.array(net); dong = np.array(dong)
        med = float(np.median(net)) if len(net) else 0
        # chấm theo 0,5 s: tốt = nét ≥ 60 % trung vị và động vừa phải (không lia gắt)
        diem = []
        for s in np.arange(0, v['dur'] - 0.25, 0.5):
            a, b = int(s / buoc), int((s + 0.5) / buoc) + 1
            n_ = float(net[a:b].mean()) if b > a and a < len(net) else 0
            d_ = float(dong[a:b].mean()) if b > a and a < len(dong) else 0
            xau = (n_ < 0.6 * med) or (d_ > 14)
            diem.append(dict(t=round(float(s), 2), net=round(n_, 1), dong=round(d_, 1), xau=bool(xau)))
        v['i'] = i
        v['doc'] = v['h'] > v['w']
        v['diem'] = diem
        # người: 3 khung
        fr = doc_khung_deu(p, v, max(0.5, v['dur'] / 3.2), 640)
        v['co_nguoi'] = bool(any(_co_nguoi(f) for f in fr[:4]))
        sheet = os.path.join(work, 'khung', f'clip_{i:02d}.jpg')
        to_khung(p, v, sheet, f'[{i:02d}] {v["file"]}  ({v["dur"]:.1f}s {v["w"]}x{v["h"]}{" DỌC" if v["doc"] else ""}{" · CÓ NGƯỜI" if v["co_nguoi"] else ""})')
        v['to_khung'] = os.path.relpath(sheet, work)
        # khung đại diện giữa clip cho tờ tổng quan
        mid = doc_khung_deu(p, v, max(0.5, v['dur'] / 2), 320)
        tq.append((f'[{i:02d}] {v["file"][:34]}', mid[min(1, len(mid) - 1)] if len(mid) else np.zeros((180, 320, 3), np.uint8)))
    for k, a in enumerate(anh, 1):
        a['i'] = 100 + k
        im = cv2.imdecode(np.fromfile(os.path.join(res, a['file']), np.uint8), cv2.IMREAD_COLOR)
        if im is not None:
            tq.append((f'[{a["i"]}] {a["file"][:34]}', cv2.resize(im, (320, int(320 * im.shape[0] / im.shape[1])))))
    # tờ tổng quan
    cot = 4; tw, th = 420, 236
    hang = (len(tq) + cot - 1) // cot
    canvas = Image.new('RGB', (cot * (tw + 6) + 6, hang * (th + 34) + 8), (16, 16, 16))
    d = ImageDraw.Draw(canvas)
    fnt = ImageFont.truetype(C.font('BarlowCondensed-ExtraBold.ttf'), 22)
    for k, (nh, im) in enumerate(tq):
        h0, w0 = im.shape[:2]; s = min(tw / w0, th / h0)
        im2 = cv2.resize(im, (int(w0 * s), int(h0 * s)))
        x = 6 + (k % cot) * (tw + 6); y = 8 + (k // cot) * (th + 34)
        canvas.paste(Image.fromarray(cv2.cvtColor(im2, cv2.COLOR_BGR2RGB)), (x + (tw - im2.shape[1]) // 2, y))
        d.text((x, y + th + 4), nh, font=fnt, fill=(255, 220, 0))
    canvas.save(os.path.join(work, 'tai_nguyen.jpg'), quality=88)
    so_doc = sum(1 for v in video if v['doc']) + sum(1 for a in anh if a['h'] > a['w'])
    tong = len(video) + len(anh)
    kho = '9:16' if so_doc * 2 > tong else '16:9'
    kq = dict(res=os.path.abspath(res), video=video, anh=anh, nhac=nhac, kho_de_xuat=kho)
    C.ghi_json(os.path.join(work, 'tai_nguyen.json'), kq)
    C.in_ra(f'Quét xong: {len(video)} clip, {len(anh)} ảnh, {len(nhac)} nhạc · khổ đề xuất {kho} ({so_doc}/{tong} dọc)')
    C.in_ra(f'  → mở {os.path.join(work, "tai_nguyen.jpg")} và từng {os.path.join(work, "khung", "clip_XX.jpg")}')
    return kq
