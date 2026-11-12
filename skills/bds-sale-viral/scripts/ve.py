# -*- coding: utf-8 -*-
"""Vẽ đồ hoạ tĩnh (1 lần, có cache) — mỗi hàm trả `Anh`: ảnh RGBA + vị trí hộp chữ bên trong ảnh
(ox, oy, w, h) để đặt chính xác dù có bóng / khối 3D tràn ra ngoài.
Chuyển động (phóng, trượt, nhoè, mờ) làm ở dung.py bằng `bien()`."""
import math, os, re
from dataclasses import dataclass
from functools import lru_cache
import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageFilter
import chung as C


@dataclass
class Anh:
    img: Image.Image      # RGBA
    ox: int               # góc trên-trái hộp nội dung trong img
    oy: int
    w: int                # kích thước hộp nội dung
    h: int
    meta: dict = None


# ------------------------------------------------------------------ cơ bản
def _np(img):
    return np.asarray(img).astype(np.float32) / 255.0


def _pil(a):
    return Image.fromarray(np.clip(a * 255 + 0.5, 0, 255).astype(np.uint8))


def _mask_chu(text, fnt, gian=0, pad=40):
    """mặt nạ L của dòng chữ + hộp nội dung. Đo theo bbox thật (dấu tiếng Việt nằm trong)."""
    asc, desc = fnt.getmetrics()
    if gian:
        wtot = sum(fnt.getlength(ch) for ch in text) + gian * max(0, len(text) - 1)
    else:
        wtot = fnt.getlength(text)
    Wi, Hi = int(wtot + 2 * pad + 4), int(asc + desc + 2 * pad)
    m = Image.new('L', (Wi, Hi), 0)
    d = ImageDraw.Draw(m)
    if gian:
        x = pad
        for ch in text:
            d.text((x, pad + asc), ch, font=fnt, fill=255, anchor='ls')
            x += fnt.getlength(ch) + gian
    else:
        d.text((pad, pad + asc), text, font=fnt, fill=255, anchor='ls')
    bb = m.getbbox() or (pad, pad, pad + 1, pad + 1)
    # hộp "chữ hoa" (không tính dấu) để canh màu gradient đều giữa các chữ
    hb = fnt.getbbox('H', anchor='ls')
    cap_top, cap_bot = pad + asc + hb[1], pad + asc
    return m, bb, (cap_top, cap_bot), pad + asc


def _gradient(h, w, stops, y0, y1):
    """gradient dọc nhiều mốc màu trong đoạn [y0, y1], ngoài đoạn giữ màu mép."""
    ys = np.clip((np.arange(h, dtype=np.float32) - y0) / max(1.0, (y1 - y0)), 0, 1)
    st = np.array(stops, np.float32) / 255.0
    k = len(st) - 1
    pos = ys * k
    i = np.minimum(pos.astype(int), k - 1)
    f = (pos - i)[:, None]
    col = st[i] * (1 - f) + st[i + 1] * f
    return np.repeat(col[:, None, :], w, axis=1)


def _bong(alpha, dx, dy, mo, a):
    """bóng mềm từ kênh alpha (float HxW) → mảng alpha bóng."""
    s = np.roll(np.roll(alpha, int(dy), 0), int(dx), 1)
    if mo > 0: s = cv2.GaussianBlur(s, (0, 0), mo)
    return s * a


def _ghep(lop):
    """ghép danh sách lớp (rgb float HxWx3, alpha HxW) từ dưới lên → RGBA float (thẳng, không nhân trước)."""
    H, W = lop[0][1].shape
    out_rgb = np.zeros((H, W, 3), np.float32); out_a = np.zeros((H, W), np.float32)
    for rgb, a in lop:
        a3 = a[..., None]
        out_rgb = rgb * a3 + out_rgb * (1 - a3)
        out_a = a + out_a * (1 - a)
    # out_rgb đang là nhân trước → về thẳng
    nz = out_a > 1e-4
    out_rgb[nz] = out_rgb[nz] / out_a[nz][:, None]
    return np.dstack([out_rgb, out_a])


def _cat(rgba_f, box, pad=0):
    """cắt ảnh RGBA float theo vùng có alpha, trả (Image, dời x, dời y)."""
    a = rgba_f[..., 3]
    ys, xs = np.where(a > 0.003)
    if len(xs) == 0:
        return _pil(rgba_f[:2, :2]), 0, 0
    x0, x1, y0, y1 = max(0, xs.min() - pad), xs.max() + 1 + pad, max(0, ys.min() - pad), ys.max() + 1 + pad
    return _pil(rgba_f[y0:y1, x0:x1]), x0, y0


def _nghieng(img, k):
    """nghiêng chữ (italic giả) hệ số k (0,2 ≈ 11°)."""
    if not k: return img, 0
    w, h = img.size
    add = int(abs(k) * h) + 2
    out = img.transform((w + add, h), Image.AFFINE, (1, k, -add if k > 0 else 0, 0, 1, 0), resample=Image.BICUBIC)
    return out, add if k > 0 else 0


def mau_hex(c):
    if isinstance(c, (list, tuple)): return tuple(int(v) for v in c[:3])
    c = c.lstrip('#'); return tuple(int(c[i:i + 2], 16) for i in (0, 2, 4))


# ------------------------------------------------------------------ CHỮ KHOÁ (tiêu đề)
@lru_cache(maxsize=64)
def chu_khoa(text, kieu='cam', co=None, rong_max=None, mau_tuy=None):
    """Chữ khoá to: mặt gradient + khối 3D đẩy xuống + viền sáng mép trên + bóng mềm.
    Tự thu cỡ để rộng ≤ rong_max. mau_tuy: (r,g,b) đổi bảng màu sang 1 màu tuỳ chọn."""
    k = dict(C.KIEU_KHOA.get(kieu, C.KIEU_KHOA['cam']))
    if mau_tuy:
        c = np.array(mau_hex(mau_tuy), np.float32)
        k['grad'] = [tuple(np.clip(c * 0.35 + 255 * 0.65, 0, 255)), tuple(c), tuple(np.clip(c * 0.62, 0, 255))]
        if k.get('khoi'): k['khoi'] = tuple(np.clip(c * 0.38, 0, 255))
    s = text.upper() if k['hoa'] else text
    co = co or C.TIEU_DE['khoa_co']
    rong_max = rong_max or C.TIEU_DE['khoa_rong']
    for _ in range(12):
        f = C.font(k['font'], co)
        wl = f.getlength(s) + k['gian'] * max(0, len(s) - 1) + abs(k['nghieng']) * co
        if wl <= rong_max or co <= 60: break
        co = int(co * rong_max / wl * 0.98)
    f = C.font(k['font'], co)
    pad = int(co * 0.35)
    m, bb, (ct, cb), base = _mask_chu(s, f, k['gian'], pad)
    a = np.asarray(m).astype(np.float32) / 255.0
    H, W = a.shape
    lop = []
    # bóng mềm
    kp = k.get('khoi_px', 0) if k.get('khoi') else 0
    lop.append((np.zeros((H, W, 3), np.float32), _bong(a, co * 0.02, co * 0.05 + kp, co * 0.06, 0.55)))
    # khối 3D
    if k.get('khoi'):
        kc = np.array(k['khoi'], np.float32) / 255.0
        acc = np.zeros_like(a)
        for i in range(1, kp + 1):
            acc = np.maximum(acc, np.roll(np.roll(a, i, 0), int(round(i * 0.35)), 1))
        sh = np.linspace(1.0, 0.7, H, dtype=np.float32)[:, None, None]
        lop.append((np.broadcast_to(kc, (H, W, 3)) * sh, acc))
        # viền tối mảnh cho mép chữ sắc trên khối
        ed = cv2.dilate(a, np.ones((3, 3), np.uint8)) - a
        lop.append((np.broadcast_to(kc * 0.8, (H, W, 3)).copy(), np.clip(ed, 0, 1) * 0.9))
    # mặt chữ gradient
    g = _gradient(H, W, k['grad'], ct, cb)
    lop.append((g, a))
    # loé mép trên (ánh kim)
    hl = np.clip(a - np.roll(a, max(2, co // 45), 0), 0, 1)
    lop.append((np.ones((H, W, 3), np.float32), hl * 0.55))
    rgba = _ghep(lop)
    img = _pil(rgba)
    img, dx = _nghieng(img, k['nghieng'])
    rgba = _np(img)
    out, x0, y0 = _cat(rgba, None, 2)
    # hộp nội dung = bbox mặt chữ (không tính bóng/khối)
    return Anh(out, bb[0] + dx - x0, bb[1] - y0, bb[2] - bb[0], bb[3] - bb[1],
               {'co': co, 'cap': (ct - y0, cb - y0), 'font': k['font'], 'text': s, 'gian': k['gian']})


def ranh_chu(anh, text):
    """x các mép chữ (trong hệ toạ độ ảnh) — dùng cho hiệu ứng vỡ từng chữ."""
    f = C.font(anh.meta['font'], anh.meta['co'])
    g = anh.meta.get('gian', 0)
    xs, x = [anh.ox], anh.ox
    for ch in text:
        x += f.getlength(ch) + g
        xs.append(x)
    sc = anh.w / max(1.0, xs[-1] - xs[0])
    return [anh.ox + (v - xs[0]) * sc for v in xs]


# ------------------------------------------------------------------ CHỮ TRẮNG (dẫn, viết tay, sub) + đoạn nhấn
_NHAN = re.compile(r'\[([^\]]+)\]')


def _doan(text):
    """'Diện tích [50m²]' → [('Diện tích ', False), ('50m²', True)]"""
    out, i = [], 0
    for m in _NHAN.finditer(text):
        if m.start() > i: out.append((text[i:m.start()], False))
        out.append((m.group(1), True)); i = m.end()
    if i < len(text): out.append((text[i:], False))
    return out or [('', False)]


@lru_cache(maxsize=512)
def chu_trang(text, font_name, co, mau=(255, 255, 255), vien=2, bong=(0, 4, 9, 0.62), nhan_mau=None,
              nhan_font=None, grad=None, quang=0.0, nghieng_nhan=0.0):
    """1 dòng chữ (có thể chứa đoạn [nhấn] đổi màu / phông). Trắng + viền tối mảnh + bóng mềm như sub mẫu."""
    segs = _doan(text)
    f = C.font(font_name, co)
    fn = C.font(nhan_font or font_name, int(co * 1.06)) if any(s[1] for s in segs) else f
    asc = max(f.getmetrics()[0], fn.getmetrics()[0]); desc = max(f.getmetrics()[1], fn.getmetrics()[1])
    pad = int(co * 0.5) + 10
    wtot = sum((fn if hi else f).getlength(s) for s, hi in segs)
    Wi, Hi = int(wtot + 2 * pad + co * 0.3), int(asc + desc + 2 * pad)
    m = Image.new('L', (Wi, Hi), 0); mh = Image.new('L', (Wi, Hi), 0)
    d, dh = ImageDraw.Draw(m), ImageDraw.Draw(mh)
    x = pad
    for s, hi in segs:
        (dh if hi else d).text((x, pad + asc), s, font=fn if hi else f, fill=255, anchor='ls')
        x += (fn if hi else f).getlength(s)
    a = np.asarray(m).astype(np.float32) / 255.0
    ah = np.asarray(mh).astype(np.float32) / 255.0
    at = np.maximum(a, ah)
    Hh, Ww = a.shape
    bb = Image.fromarray((at * 255).astype(np.uint8)).getbbox() or (pad, pad, pad + 1, pad + 1)
    lop = []
    if bong:
        lop.append((np.zeros((Hh, Ww, 3), np.float32), _bong(at, bong[0], bong[1], bong[2], bong[3])))
    if quang:
        lop.append((np.zeros((Hh, Ww, 3), np.float32), cv2.GaussianBlur(at, (0, 0), co * 0.25) * quang))
    if vien:
        ed = cv2.dilate(at, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * vien + 1, 2 * vien + 1)))
        lop.append((np.zeros((Hh, Ww, 3), np.float32), ed * 0.55))
    if grad:
        hb = f.getbbox('H', anchor='ls')
        g = _gradient(Hh, Ww, grad, pad + asc + hb[1], pad + asc)
        lop.append((g, a))
    else:
        lop.append((np.broadcast_to(np.array(mau, np.float32) / 255, (Hh, Ww, 3)).copy(), a))
    if ah.max() > 0:
        lop.append((np.broadcast_to(np.array(nhan_mau or C.SUB['nhan']['mau'], np.float32) / 255, (Hh, Ww, 3)).copy(), ah))
    rgba = _ghep(lop)
    out, x0, y0 = _cat(rgba, None, 2)
    return Anh(out, bb[0] - x0, bb[1] - y0, bb[2] - bb[0], bb[3] - bb[1], {'co': co, 'asc': pad + asc - y0})


def dan(text):
    t = C.TIEU_DE['dan']
    return chu_trang(text, t['font'], t['co'], t['mau'], 1, (0, 3, 8, 0.68))


def viet_tay(text, font_name=None):
    t = C.TIEU_DE['viet_tay']
    fn = font_name or t['font']
    co = C.TIEU_DE['viet_tay_co_cho'].get(fn, t['co'])
    # viền tối 1 px + bóng mềm đậm: nét bút mảnh vẫn đọc được trên nền trời sáng
    return chu_trang(text, fn, co, t['mau'], 1, (0, 2, 9, 0.85))


def sub_dong(text, kieu='chinh'):
    """kieu: chinh | phu | to | vang | list. Đoạn [..] = nhấn hồng-đỏ nghiêng đậm."""
    S = C.SUB
    if kieu == 'vang':
        v = S['vang']
        return chu_trang(text, v['font'], v['co'], (255, 210, 80), 2, (0, 4, 9, 0.6), grad=tuple(map(tuple, v['grad'])))
    st = S.get(kieu, S['chinh'])
    co = st['co']
    # tự thu cho vừa bề rộng
    f = C.font(st['font'], co)
    wl = f.getlength(_NHAN.sub(r'\1', text))
    if wl > S['rong_max']: co = int(co * S['rong_max'] / wl)
    nf = S['nhan']['font']
    return chu_trang(text, st['font'], co, st['mau'], S['vien_px'], (0, 4, 9, 0.62), nhan_font=nf)


# ------------------------------------------------------------------ THẺ ẢNH
def doc_anh_nguon(path, t=None):
    """ảnh hoặc 1 khung video (giữa clip) → PIL RGB."""
    ext = os.path.splitext(path)[1].lower()
    if ext in C.VID_EXT:
        import subprocess
        d = C.probe(path)['dur']
        ss = t if t is not None else d * 0.5
        raw = subprocess.run(['ffmpeg', '-v', 'error', '-ss', f'{ss:.2f}', '-i', path, '-frames:v', '1', '-f', 'image2pipe',
                              '-vcodec', 'png', '-'], capture_output=True).stdout
        import io
        return Image.open(io.BytesIO(raw)).convert('RGB')
    im = Image.open(path)
    if im.mode in ('RGBA', 'LA', 'P'):
        im = im.convert('RGBA'); bg = Image.new('RGBA', im.size, (255, 255, 255, 255)); bg.alpha_composite(im); im = bg
    return im.convert('RGB')


@lru_cache(maxsize=64)
def the_anh(path, rong, bo=None, vien=None, t=None, ty_le=None):
    """ty_le (rộng/cao): cắt giữa ảnh về tỉ lệ đó trước (ảnh nhỏ góc trên = ngang 3:2 như mẫu)."""
    T = C.THE_ANH
    bo = T['bo'] if bo is None else bo; vien = T['vien'] if vien is None else vien
    im = doc_anh_nguon(path, t)
    if ty_le:
        w0, h0 = im.size
        if w0 / h0 < ty_le:
            nh = int(w0 / ty_le); im = im.crop((0, (h0 - nh) // 2, w0, (h0 - nh) // 2 + nh))
        else:
            nw = int(h0 * ty_le); im = im.crop(((w0 - nw) // 2, 0, (w0 - nw) // 2 + nw, h0))
    h = int(im.height * rong / im.width)
    im = im.resize((int(rong), h), Image.LANCZOS)
    pad = 40
    Wt, Ht = int(rong) + 2 * vien, h + 2 * vien
    can = Image.new('RGBA', (Wt + 2 * pad, Ht + 2 * pad), (0, 0, 0, 0))
    mk = Image.new('L', (Wt, Ht), 0); ImageDraw.Draw(mk).rounded_rectangle((0, 0, Wt - 1, Ht - 1), bo + vien, fill=255)
    # bóng
    sh = Image.new('L', can.size, 0); sh.paste(mk, (pad, pad + 10))
    sh = sh.filter(ImageFilter.GaussianBlur(16)).point(lambda v: int(v * T['bong_alpha']))
    can.paste(Image.new('RGBA', can.size, (0, 0, 0, 255)), (0, 0), sh)
    # viền trắng + ảnh
    can.paste(Image.new('RGBA', (Wt, Ht), (255, 255, 255, 255)), (pad, pad), mk)
    mi = Image.new('L', im.size, 0); ImageDraw.Draw(mi).rounded_rectangle((0, 0, im.width - 1, im.height - 1), bo, fill=255)
    can.paste(im.convert('RGBA'), (pad + vien, pad + vien), mi)
    return Anh(can, pad, pad, Wt, Ht)


def phoi_canh(anh, goc_y=22, goc_x=8):
    """xoay thẻ trong không gian (nghiêng 3D kiểu thẻ mặt bằng mẫu)."""
    im = np.asarray(anh.img)
    h, w = im.shape[:2]
    f = w * 1.6
    def chieu(x, y):
        X, Y = x - w / 2, y - h / 2
        ry, rx = math.radians(goc_y), math.radians(goc_x)
        x1 = X * math.cos(ry); z1 = -X * math.sin(ry)
        y1 = Y * math.cos(rx) - z1 * math.sin(rx); z2 = Y * math.sin(rx) + z1 * math.cos(rx)
        s = f / (f + z2)
        return x1 * s + w / 2, y1 * s + h / 2
    src = np.float32([[0, 0], [w, 0], [w, h], [0, h]])
    dst = np.float32([chieu(*p) for p in src])
    M = cv2.getPerspectiveTransform(src, dst)
    out = cv2.warpPerspective(im, M, (w, h), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=(0, 0, 0, 0))
    return Anh(Image.fromarray(out), anh.ox, anh.oy, anh.w, anh.h)


# ------------------------------------------------------------------ ICON 3D BÓNG (vẽ bằng code)
def _hinh_icon(loai, S):
    """mặt nạ hình icon (L, SxS) + mặt nạ lỗ/khắc (L)."""
    m = Image.new('L', (S, S), 0); k = Image.new('L', (S, S), 0)
    d, dk = ImageDraw.Draw(m), ImageDraw.Draw(k)
    c = S / 2
    if loai == 'vi_tri':
        r = S * 0.30
        d.ellipse((c - r, S * 0.10, c + r, S * 0.10 + 2 * r), fill=255)
        d.polygon([(c - r * 0.86, S * 0.10 + r * 1.5), (c + r * 0.86, S * 0.10 + r * 1.5), (c, S * 0.90)], fill=255)
        ri = r * 0.42
        dk.ellipse((c - ri, S * 0.10 + r - ri, c + ri, S * 0.10 + r + ri), fill=255)
    elif loai in ('truong_hoc', 'tien_ich'):
        d.polygon([(S * 0.06, S * 0.40), (c, S * 0.18), (S * 0.94, S * 0.40), (c, S * 0.62)], fill=255)
        d.rounded_rectangle((S * 0.26, S * 0.46, S * 0.74, S * 0.78), S * 0.06, fill=255)
        d.line([(S * 0.86, S * 0.40), (S * 0.86, S * 0.70)], fill=255, width=int(S * 0.04))
        d.ellipse((S * 0.82, S * 0.68, S * 0.90, S * 0.78), fill=255)
        dk.line([(S * 0.26, S * 0.56), (S * 0.74, S * 0.56)], fill=255, width=int(S * 0.03))
    elif loai == 'nha':
        d.polygon([(S * 0.10, S * 0.48), (c, S * 0.12), (S * 0.90, S * 0.48)], fill=255)
        d.rectangle((S * 0.20, S * 0.44, S * 0.80, S * 0.86), fill=255)
        dk.rounded_rectangle((S * 0.42, S * 0.60, S * 0.58, S * 0.86), S * 0.03, fill=255)
    elif loai == 'tien':
        d.ellipse((S * 0.12, S * 0.12, S * 0.88, S * 0.88), fill=255)
        dk.ellipse((S * 0.22, S * 0.22, S * 0.78, S * 0.78), outline=255, width=int(S * 0.035))
        fo = C.font('Montserrat-Black.ttf', int(S * 0.42))
        dk.text((c, c), '$', font=fo, fill=255, anchor='mm')
    elif loai == 'cong_vien':
        d.ellipse((S * 0.18, S * 0.08, S * 0.82, S * 0.62), fill=255)
        d.rounded_rectangle((S * 0.44, S * 0.50, S * 0.56, S * 0.90), S * 0.03, fill=255)
    elif loai == 'benh_vien':
        d.rounded_rectangle((S * 0.12, S * 0.12, S * 0.88, S * 0.88), S * 0.16, fill=255)
        dk.rectangle((S * 0.42, S * 0.26, S * 0.58, S * 0.74), fill=255)
        dk.rectangle((S * 0.26, S * 0.42, S * 0.74, S * 0.58), fill=255)
    elif loai == 'mua_sam':
        d.rounded_rectangle((S * 0.16, S * 0.32, S * 0.84, S * 0.90), S * 0.08, fill=255)
        d.arc((S * 0.32, S * 0.10, S * 0.68, S * 0.50), 180, 360, fill=255, width=int(S * 0.06))
    elif loai == 'giao_thong':
        d.rounded_rectangle((S * 0.10, S * 0.40, S * 0.90, S * 0.72), S * 0.08, fill=255)
        d.polygon([(S * 0.24, S * 0.42), (S * 0.34, S * 0.22), (S * 0.66, S * 0.22), (S * 0.76, S * 0.42)], fill=255)
        for x in (0.28, 0.72): d.ellipse((S * (x - 0.1), S * 0.62, S * (x + 0.1), S * 0.82), fill=255)
        dk.polygon([(S * 0.32, S * 0.40), (S * 0.39, S * 0.27), (S * 0.61, S * 0.27), (S * 0.68, S * 0.40)], fill=255)
    elif loai == 'phong_ngu':      # giường: đầu giường + nệm + gối
        d.rounded_rectangle((S * 0.08, S * 0.22, S * 0.22, S * 0.86), S * 0.04, fill=255)
        d.rounded_rectangle((S * 0.08, S * 0.52, S * 0.92, S * 0.74), S * 0.06, fill=255)
        d.rectangle((S * 0.80, S * 0.70, S * 0.92, S * 0.86), fill=255)
        d.rounded_rectangle((S * 0.26, S * 0.36, S * 0.48, S * 0.52), S * 0.06, fill=255)
        dk.line([(S * 0.22, S * 0.60), (S * 0.90, S * 0.60)], fill=255, width=int(S * 0.03))
    elif loai == 'binh_luan':      # bong bóng chat + 3 chấm
        d.rounded_rectangle((S * 0.08, S * 0.14, S * 0.92, S * 0.70), S * 0.16, fill=255)
        d.polygon([(S * 0.24, S * 0.62), (S * 0.46, S * 0.66), (S * 0.18, S * 0.90)], fill=255)
        for x in (0.32, 0.50, 0.68):
            dk.ellipse((S * (x - 0.055), S * 0.365, S * (x + 0.055), S * 0.475), fill=255)
    elif loai == 'ho_nuoc':        # vòng tròn + 3 làn sóng khắc (view hồ / sông / vịnh / biển)
        d.ellipse((S * 0.10, S * 0.10, S * 0.90, S * 0.90), fill=255)
        for y in (0.36, 0.52, 0.68):
            pts = [(S * (0.20 + 0.60 * j / 24), S * y + S * 0.045 * math.sin(j / 24 * 4 * math.pi)) for j in range(25)]
            dk.line(pts, fill=255, width=int(S * 0.045), joint='curve')
    elif loai == 'tim':            # trái tim
        r = S * 0.215
        d.ellipse((S * 0.08, S * 0.16, S * 0.08 + 2 * r, S * 0.16 + 2 * r), fill=255)
        d.ellipse((S * 0.92 - 2 * r, S * 0.16, S * 0.92, S * 0.16 + 2 * r), fill=255)
        d.polygon([(S * 0.10, S * 0.46), (S * 0.90, S * 0.46), (c, S * 0.90)], fill=255)
        d.rectangle((S * 0.30, S * 0.30, S * 0.70, S * 0.50), fill=255)
    elif loai == 'chia_khoa':      # chìa khoá: vòng + thân + răng
        d.ellipse((S * 0.08, S * 0.10, S * 0.48, S * 0.50), fill=255)
        dk.ellipse((S * 0.19, S * 0.21, S * 0.37, S * 0.39), fill=255)
        d.polygon([(S * 0.36, S * 0.40), (S * 0.44, S * 0.32), (S * 0.92, S * 0.80), (S * 0.84, S * 0.88)], fill=255)
        d.polygon([(S * 0.66, S * 0.70), (S * 0.74, S * 0.62), (S * 0.84, S * 0.72), (S * 0.76, S * 0.80)], fill=255)
        d.polygon([(S * 0.56, S * 0.60), (S * 0.62, S * 0.54), (S * 0.70, S * 0.62), (S * 0.64, S * 0.68)], fill=255)
    else:  # sao
        pts = []
        for i in range(10):
            r = S * (0.42 if i % 2 == 0 else 0.18); a = -math.pi / 2 + i * math.pi / 5
            pts.append((c + r * math.cos(a), S * 0.53 + r * math.sin(a)))
        d.polygon(pts, fill=255)
    return m, k


@lru_cache(maxsize=32)
def icon_3d(loai, co=None, nhan=None, mau=None):
    """icon bóng 3D (gradient + vát mép + khối dưới + vệt bóng) + nhãn viên thuốc cùng màu."""
    co = co or C.ICON['co']
    base = np.array(mau_hex(mau) if mau else C.ICON['mau'].get(loai, (150, 70, 250)), np.float32) / 255
    S = co * 3
    m, k = _hinh_icon(loai, S)
    a = np.asarray(m).astype(np.float32) / 255; kh = np.asarray(k).astype(np.float32) / 255
    face = np.clip(a - kh, 0, 1)
    sm = cv2.GaussianBlur(a, (0, 0), S * 0.03)
    gy, gx = np.gradient(sm)
    light = np.clip(-(gx + gy) * S * 0.9, -1, 1)          # sáng từ trên-trái
    ys = np.linspace(0, 1, S, dtype=np.float32)[:, None, None]
    col = np.clip(base * (1.30 - 0.55 * ys) + 0.12 * (1 - ys), 0, 1)
    col = np.broadcast_to(col, (S, S, 3)).copy()
    col = np.clip(col + light[..., None] * 0.35, 0, 1)
    inner = np.clip(base * 0.45 + 0.55, 0, 1)              # lỗ khắc: sáng nhạt (như tâm ghim mẫu)
    lop = []
    ext = np.zeros_like(a)
    for i in range(1, int(S * 0.05)):
        ext = np.maximum(ext, np.roll(a, i, 0))
    lop.append((np.zeros((S, S, 3), np.float32), _bong(a, 0, S * 0.07, S * 0.04, 0.45)))
    lop.append((np.broadcast_to(base * 0.45, (S, S, 3)).copy(), ext))
    lop.append((col, face))
    lop.append((np.broadcast_to(inner, (S, S, 3)).copy(), np.clip(kh * a, 0, 1) * 0.95))
    # vệt bóng kính góc trên-trái
    gl = Image.new('L', (S, S), 0)
    ImageDraw.Draw(gl).ellipse((S * 0.22, S * 0.12, S * 0.55, S * 0.30), fill=255)
    gla = cv2.GaussianBlur(np.asarray(gl).astype(np.float32) / 255, (0, 0), S * 0.03) * face
    lop.append((np.ones((S, S, 3), np.float32), gla * 0.45))
    rgba = _ghep(lop)
    ic = _pil(rgba).resize((co, co), Image.LANCZOS)
    if not nhan:
        return Anh(ic, 0, 0, co, co)
    fo = C.font('BeVietnamPro-Bold.ttf', C.ICON['nhan_co'])
    tw = fo.getlength(nhan)
    pw, ph = int(tw + 44), int(C.ICON['nhan_co'] * 1.55)
    Wt = max(co, pw) + 20; Ht = co + ph - int(co * 0.06) + 20
    can = Image.new('RGBA', (Wt, Ht), (0, 0, 0, 0))
    py = co - int(co * 0.06)
    pill = Image.new('RGBA', (pw, ph), (0, 0, 0, 0))
    pd = ImageDraw.Draw(pill)
    pc = tuple(int(v * 255) for v in np.clip(base * 0.95, 0, 1))
    pd.rounded_rectangle((0, 0, pw - 1, ph - 1), ph // 2, fill=pc + (240,), outline=(255, 255, 255, 230), width=3)
    pd.text((pw / 2, ph / 2), nhan, font=fo, fill=(255, 255, 255, 255), anchor='mm')
    can.alpha_composite(pill, ((Wt - pw) // 2, py))
    can.alpha_composite(ic, ((Wt - co) // 2, 0))
    return Anh(can, 0, 0, Wt, Ht)


# ------------------------------------------------------------------ ICON NÉT (vàng, cạnh chữ khoá / số tiền)
@lru_cache(maxsize=16)
def icon_net(loai, co=150, mau=(255, 226, 30)):
    S = co * 3; lw = int(S * 0.045)
    im = Image.new('L', (S, S), 0); d = ImageDraw.Draw(im)
    if loai == 'chia_khoa_nha':
        r = S * 0.13
        d.ellipse((S * 0.06, S * 0.10, S * 0.06 + 2 * r, S * 0.10 + 2 * r), outline=255, width=lw)
        d.line([(S * 0.06 + 2 * r - lw, S * 0.10 + r), (S * 0.86, S * 0.10 + r)], fill=255, width=lw)
        for x in (0.66, 0.78): d.line([(S * x, S * 0.10 + r), (S * x, S * 0.10 + r + S * 0.10)], fill=255, width=lw)
        # nhà treo
        d.line([(S * 0.42, S * 0.10 + r), (S * 0.42, S * 0.46)], fill=255, width=lw // 2 + 2)
        d.polygon([(S * 0.24, S * 0.62), (S * 0.42, S * 0.46), (S * 0.60, S * 0.62)], outline=255, width=lw)
        d.rectangle((S * 0.28, S * 0.62, S * 0.56, S * 0.88), outline=255, width=lw)
        d.rectangle((S * 0.38, S * 0.72, S * 0.46, S * 0.88), outline=255, width=lw // 2 + 2)
    elif loai == 'tui_tien':
        d.ellipse((S * 0.16, S * 0.30, S * 0.84, S * 0.92), outline=255, width=lw)
        d.polygon([(S * 0.36, S * 0.10), (S * 0.64, S * 0.10), (S * 0.56, S * 0.30), (S * 0.44, S * 0.30)], outline=255, width=lw)
        fo = C.font('Montserrat-Black.ttf', int(S * 0.36))
        d.text((S * 0.5, S * 0.62), '$', font=fo, fill=255, anchor='mm')
    else:  # bieu_do
        d.line([(S * 0.10, S * 0.88), (S * 0.90, S * 0.88)], fill=255, width=lw)
        d.line([(S * 0.14, S * 0.74), (S * 0.40, S * 0.52), (S * 0.56, S * 0.62), (S * 0.86, S * 0.24)], fill=255, width=lw, joint='curve')
        d.polygon([(S * 0.90, S * 0.18), (S * 0.70, S * 0.22), (S * 0.86, S * 0.38)], fill=255)
    a = np.asarray(im.resize((co, co), Image.LANCZOS)).astype(np.float32) / 255
    lop = [(np.zeros((co, co, 3), np.float32), _bong(a, 0, 3, 4, 0.6)),
           (np.broadcast_to(np.array(mau, np.float32) / 255, (co, co, 3)).copy(), a)]
    return Anh(_pil(_ghep(lop)), 0, 0, co, co)


# ------------------------------------------------------------------ Ô TÌM KIẾM (kiểu Google)
def o_tim_kiem(text, con_tro=True):
    T = C.TIM_KIEM
    Wt, Ht = T['rong'], T['cao']; pad = 30
    can = Image.new('RGBA', (Wt + 2 * pad, Ht + 2 * pad), (0, 0, 0, 0))
    sh = Image.new('L', can.size, 0); ImageDraw.Draw(sh).rounded_rectangle((pad, pad + 8, pad + Wt, pad + Ht + 8), Ht // 2, fill=120)
    can.paste(Image.new('RGBA', can.size, (0, 0, 0, 255)), (0, 0), sh.filter(ImageFilter.GaussianBlur(12)))
    d = ImageDraw.Draw(can)
    d.rounded_rectangle((pad, pad, pad + Wt, pad + Ht), Ht // 2, fill=(255, 255, 255, 255))
    g = (95, 99, 104, 255); cy = pad + Ht / 2
    r = Ht * 0.17; cx = pad + Ht * 0.48
    d.ellipse((cx - r, cy - r - 3, cx + r, cy + r - 3), outline=g, width=5)
    d.line([(cx + r * 0.7, cy + r * 0.7 - 3), (cx + r * 1.6, cy + r * 1.6 - 3)], fill=g, width=6)
    mx = pad + Wt - Ht * 0.48
    d.rounded_rectangle((mx - 9, cy - 22, mx + 9, cy + 6), 9, fill=g)
    d.arc((mx - 16, cy - 12, mx + 16, cy + 16), 0, 180, fill=g, width=4)
    d.line([(mx, cy + 16), (mx, cy + 24)], fill=g, width=4)
    fo = C.font(T['font'], T['co'])
    s = text + ('_' if con_tro else '')
    d.text((pad + Ht * 0.95, cy), s, font=fo, fill=(32, 33, 36, 255), anchor='lm')
    return Anh(can, pad, pad, Wt, Ht)


# ------------------------------------------------------------------ VÒNG VẼ TAY + MŨI TÊN (quanh 1 dòng sub)
@lru_cache(maxsize=32)
def _diem_vong(w, h):
    pts = []
    n = 90
    for i in range(n + 1):
        u = i / n
        a = math.radians(200 + u * 400)            # hơn 1 vòng, hở đuôi
        rx = w / 2 * (1.08 - 0.06 * u); ry = h / 2 * (1.25 - 0.18 * u)
        pts.append((w / 2 + rx * math.cos(a) + 6 * math.sin(u * 7), h / 2 + ry * math.sin(a) - 8 * u))
    return pts


def vong_ve(w, h, p):
    V = C.VONG_VE
    pad = 40
    can = Image.new('RGBA', (int(w) + 2 * pad, int(h) + 2 * pad), (0, 0, 0, 0))
    pts = [(x + pad, y + pad) for x, y in _diem_vong(int(w), int(h))]
    k = max(2, int(len(pts) * C.clamp(p)))
    d = ImageDraw.Draw(can)
    col = V['mau'] + (255,)
    d.line(pts[:k], fill=col, width=V['day'], joint='curve')
    if p >= 0.98:     # đầu mũi tên
        (x1, y1), (x0, y0) = pts[-1], pts[-6]
        ang = math.atan2(y1 - y0, x1 - x0)
        for s in (-1, 1):
            a = ang + math.pi - s * 0.5
            d.line([(x1, y1), (x1 + 26 * math.cos(a), y1 + 26 * math.sin(a))], fill=col, width=V['day'])
    return Anh(can, pad, pad, int(w), int(h))


# ------------------------------------------------------------------ VỆT TỐC ĐỘ (trước số tiền)
def vet_toc_do(w, h, p, mau=(255, 226, 30)):
    can = Image.new('RGBA', (int(w), int(h)), (0, 0, 0, 0))
    d = ImageDraw.Draw(can)
    for i in range(3):
        x = (p * 1.25 - i * 0.12) * w
        a = int(255 * C.clamp(1 - abs(p - 0.5) * 1.6))
        for dy in (-0.22, 0.0, 0.22):
            y = h / 2 + dy * h
            L = w * (0.10 if dy else 0.16)
            d.polygon([(x - L, y - h * 0.05), (x, y), (x - L, y + h * 0.05), (x - L * 0.75, y)], fill=mau + (a,))
    return Anh(can, 0, 0, int(w), int(h))


# ------------------------------------------------------------------ LOGO dự án (nền trắng/đen → trong suốt)
@lru_cache(maxsize=8)
def logo(path, rong):
    im = Image.open(path)
    if im.mode != 'RGBA' or np.asarray(im.convert('RGBA'))[..., 3].min() == 255:
        rgb = np.asarray(im.convert('RGB')).astype(np.float32)
        goc = np.concatenate([rgb[:8, :8].reshape(-1, 3), rgb[:8, -8:].reshape(-1, 3), rgb[-8:, :8].reshape(-1, 3), rgb[-8:, -8:].reshape(-1, 3)])
        bg = np.median(goc, 0)
        dist = np.sqrt(((rgb - bg) ** 2).sum(-1))
        a = np.clip((dist - 18) / 40, 0, 1)
        im = Image.fromarray(np.dstack([rgb, a * 255]).astype(np.uint8), 'RGBA')
    bb = im.getbbox()
    if bb: im = im.crop(bb)
    h = int(im.height * rong / im.width)
    im = im.resize((int(rong), h), Image.LANCZOS)
    a = np.asarray(im).astype(np.float32) / 255
    pad = 30
    big = np.zeros((h + 2 * pad, int(rong) + 2 * pad, 4), np.float32); big[pad:pad + h, pad:pad + int(rong)] = a
    lop = [(np.zeros(big.shape[:2] + (3,), np.float32), _bong(big[..., 3], 0, 6, 10, 0.45)), (big[..., :3], big[..., 3])]
    return Anh(_pil(_ghep(lop)), pad, pad, int(rong), h)
