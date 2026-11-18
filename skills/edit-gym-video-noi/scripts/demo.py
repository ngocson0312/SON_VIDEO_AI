# -*- coding: utf-8 -*-
"""DEMO FULL MÀN — cảnh đồ hoạ minh hoạ phủ KÍN khung (giọng người nói vẫn chạy, sub karaoke vẫn nằm trên cùng).

Người nói nhắc "4, 5, 6, hơn 10 cân" → hiện bảng kết quả; "không cắt calo / tinh bột" → danh sách ✗; "80 % PT" → vòng phần trăm;
"cân bằng năng lượng" → cái cân; "giảm nhanh – lên cũng nhanh" → biểu đồ yo-yo; "comment ở dưới" → nút bình luận…
Mọi chữ / con số trên hình PHẢI có trong lời (kiem-kh cảnh báo). Nội dung nằm trong VÙNG AN TOÀN (C.AN_TOAN) và phía trên dải sub.

plan['demo'] = [{t0, t1, kieu, tieu_de?, ...}], kieu:
  ket_qua    {tieu_de, items:[{text, t}], don_vi}             bảng thẻ số trượt vào lần lượt (t = giây từ đầu cảnh)
  danh_sach  {tieu_de, mark: tick|x, items:[{text, t}]}       thẻ có dấu ✓ / ✗ hiện lần lượt
  donut      {tieu_de, gia_tri (0-100), nhan}                  vòng phần trăm chạy
  bieu_do    {tieu_de, dang: yoyo|bac_thang, nhan:[{text,t}]}  đường vẽ dần + nhãn
  can_bang   {tieu_de, trai, phai}                             cái cân lắc rồi cân bằng
  cta        {tieu_de, dong:[text,…]}                          nút bình luận + mũi tên nhún
"""
import math
from functools import lru_cache
import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageFilter
import chung as C
import ve

W, H = C.W, C.H
HONG = (255, 64, 140); HONG_D = (214, 0, 92); VANG = (255, 214, 60); XANH = (46, 214, 120); DO = (255, 72, 72)
NAVY = (14, 18, 44)
CX = (C.AN_TOAN['x0'] + C.AN_TOAN['x1']) / 2          # tâm ngang vùng an toàn (chừa cột nút bên phải)
RONG = C.AN_TOAN['x1'] - C.AN_TOAN['x0']


# ------------------------------------------------------------------ sprite (RGBA nhân trước alpha, float32)
def _pm(img):
    a = np.asarray(img.convert('RGBA'), np.float32) / 255.0
    a = a.copy(); a[..., :3] *= a[..., 3:4]
    return a


def _ss(w, h, k=3):
    return Image.new('RGBA', (int(w * k), int(h * k)), (0, 0, 0, 0)), k


def _fin(im, k, w, h):
    return _pm(im.resize((int(w), int(h)), Image.LANCZOS))


def over(G, S, cx, cy, sc=1.0, al=1.0, goc=0.0):
    """đặt sprite S (premult) tâm (cx, cy) lên G (premult) — phóng sc, mờ al."""
    if al <= 0.003 or sc <= 0.02: return
    h, w = S.shape[:2]
    if abs(sc - 1) > 1e-3 or goc:
        nw, nh = max(1, int(round(w * sc))), max(1, int(round(h * sc)))
        S = cv2.resize(S, (nw, nh), interpolation=cv2.INTER_AREA if sc < 1 else cv2.INTER_LINEAR)
        if goc:
            R = cv2.getRotationMatrix2D((nw / 2, nh / 2), goc, 1.0)
            S = cv2.warpAffine(S, R, (nw, nh), flags=cv2.INTER_LINEAR, borderValue=(0, 0, 0, 0))
        h, w = nh, nw
    x0, y0 = int(round(cx - w / 2)), int(round(cy - h / 2))
    a0, b0, a1, b1 = max(0, x0), max(0, y0), min(W, x0 + w), min(H, y0 + h)
    if a1 <= a0 or b1 <= b0: return
    Q = S[b0 - y0:b1 - y0, a0 - x0:a1 - x0] * al
    R = G[b0:b1, a0:a1]
    R *= (1.0 - Q[..., 3:4]); R += Q


@lru_cache(maxsize=256)
def chu(text, co=64, font='Montserrat-ExtraBold.ttf', mau=(255, 255, 255), vien=0, grad=None, bong=True):
    A = ve.chu_trang(text, font, co, mau, vien, (0, 5, 14, 0.55) if bong else None, grad=grad)
    return _cat(A)


def _cat(A):
    """hộp nội dung của Anh → sprite premult (bỏ lề dư)."""
    im = A.img
    return _pm(im.crop((max(0, A.ox - 14), max(0, A.oy - 14), min(im.width, A.ox + A.w + 14), min(im.height, A.oy + A.h + 14))))


@lru_cache(maxsize=32)
def the(w, h, r=36, fill=(22, 28, 62, 232), vien=None, glow=None):
    k = 3
    pad = 26
    im = Image.new('RGBA', ((w + 2 * pad) * k, (h + 2 * pad) * k), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    if glow:
        g = Image.new('RGBA', im.size, (0, 0, 0, 0)); ImageDraw.Draw(g).rounded_rectangle(
            (pad * k, pad * k, (pad + w) * k, (pad + h) * k), r * k, fill=glow + (150,))
        im.alpha_composite(g.filter(ImageFilter.GaussianBlur(14 * k)))
    d.rounded_rectangle((pad * k, pad * k, (pad + w) * k, (pad + h) * k), r * k, fill=fill)
    if vien:
        d.rounded_rectangle((pad * k, pad * k, (pad + w) * k, (pad + h) * k), r * k, outline=vien, width=4 * k)
    return _fin(im, k, w + 2 * pad, h + 2 * pad)


@lru_cache(maxsize=16)
def dau(kind, co=96):
    """icon tròn: tick / x / mui_ten (xuống) / lua (calo)."""
    k = 4; S = co * k
    im = Image.new('RGBA', (S, S), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    if kind in ('tick', 'x', 'xuong'):
        col = {'tick': XANH, 'x': DO, 'xuong': XANH}[kind]
        d.ellipse((S * 0.04, S * 0.04, S * 0.96, S * 0.96), fill=col + (255,))
        w = int(S * 0.10)
        if kind == 'tick':
            d.line([(S * 0.27, S * 0.52), (S * 0.43, S * 0.67), (S * 0.74, S * 0.34)], fill=(255, 255, 255, 255), width=w, joint='curve')
        elif kind == 'x':
            d.line([(S * 0.31, S * 0.31), (S * 0.69, S * 0.69)], fill=(255, 255, 255, 255), width=w)
            d.line([(S * 0.69, S * 0.31), (S * 0.31, S * 0.69)], fill=(255, 255, 255, 255), width=w)
        else:
            d.line([(S * 0.5, S * 0.24), (S * 0.5, S * 0.70)], fill=(255, 255, 255, 255), width=w)
            d.polygon([(S * 0.27, S * 0.52), (S * 0.73, S * 0.52), (S * 0.5, S * 0.78)], fill=(255, 255, 255, 255))
    return _fin(im, k, co, co)


@lru_cache(maxsize=8)
def san_cam(co=300):
    """biển cấm đỏ (vòng + gạch chéo)."""
    k = 3; S = co * k
    im = Image.new('RGBA', (S, S), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    w = int(S * 0.085)
    d.ellipse((w, w, S - w, S - w), outline=DO + (255,), width=w)
    d.line([(S * 0.22, S * 0.78), (S * 0.78, S * 0.22)], fill=DO + (255,), width=w)
    return _fin(im, k, co, co)


def ease_back(p):
    return C.ease_back(p, 1.7)


def tieu(G, text, t, y=300):
    """tiêu đề cảnh: chữ trắng to + thanh hồng kéo dài."""
    p = C.clamp(t / 0.35)
    A = chu(text, 66, 'Montserrat-ExtraBold.ttf', (255, 255, 255), 3)
    over(G, A, CX, y, sc=0.9 + 0.1 * C.ease_out(p), al=C.ease_out(p))
    wb = int(min(RONG, A.shape[1]) * 0.42 * C.ease_out(C.clamp((t - 0.1) / 0.4)))
    if wb > 4:
        bar = np.zeros((14, wb, 4), np.float32); bar[..., 0] = 1.0; bar[..., 1] = 0.25; bar[..., 2] = 0.55; bar[..., 3] = 1.0
        bar[..., :3] *= bar[..., 3:4]
        over(G, bar, CX, y + A.shape[0] / 2 + 14)


# ------------------------------------------------------------------ các kiểu cảnh
def ve_ket_qua(G, sp, t, dur):
    tieu(G, sp.get('tieu_de', 'HỌC VIÊN GIẢM'), t, 300)
    its = sp['items']; n = len(its)
    y0 = 440
    for k, it in enumerate(its):
        last = k == n - 1
        h = 210 if last else 150
        y = y0 + k * 176 + (30 if last else 0)
        p = C.clamp((t - it['t']) / 0.42)
        if p <= 0: continue
        w = 760
        card = the(w, h, 40, (255, 64, 140, 255) if last else (24, 30, 66, 238), None if last else (255, 255, 255, 40),
                   HONG if last else None)
        sc = 0.55 + 0.45 * ease_back(p)
        dx = 260 * (1 - C.ease_out(p))
        over(G, card, CX + dx, y, sc=sc, al=C.clamp(p * 2.5))
        num = chu(it['text'], 84 if last else 80, 'Montserrat-Black.ttf', (255, 255, 255), 0, None, False)
        over(G, num, CX + dx + (78 if last else 46), y, sc=sc, al=C.clamp(p * 2.5))
        over(G, dau('xuong', 92 if last else 74), CX + dx - w / 2 + 84, y, sc=sc, al=C.clamp(p * 2.5))
    # chữ phụ cuối
    if sp.get('chu_cuoi'):
        p = C.clamp((t - sp['chu_cuoi'][1]) / 0.4)
        over(G, chu(sp['chu_cuoi'][0], 50, 'Montserrat-Bold.ttf', (255, 226, 120), 2), CX, y0 + n * 176 + 90, al=C.ease_out(p))


def ve_danh_sach(G, sp, t, dur):
    tieu(G, sp.get('tieu_de', ''), t, 320)
    mark = sp.get('mark', 'tick')
    its = sp['items']
    for k, it in enumerate(its):
        p = C.clamp((t - it['t']) / 0.4)
        if p <= 0: continue
        y = 520 + k * 190
        w, h = 800, 150
        card = the(w, h, 42, (24, 30, 66, 238), (255, 255, 255, 46))
        dx = 300 * (1 - C.ease_out(p)); al = C.clamp(p * 2.5)
        over(G, card, CX + dx, y, sc=0.92 + 0.08 * ease_back(p), al=al)
        ic = C.clamp((t - it['t'] - 0.18) / 0.35)
        over(G, dau(mark, 100), CX + dx - w / 2 + 84, y, sc=0.3 + 0.7 * ease_back(ic), al=C.clamp(ic * 3) * al)
        tx = chu(it['text'], 54, 'Montserrat-ExtraBold.ttf', (255, 255, 255), 0, None, False)
        sc = min(1.0, (w - 200) / tx.shape[1])
        over(G, tx, CX + dx - w / 2 + 160 + tx.shape[1] * sc / 2, y, sc=sc, al=al)


def _vong(co, p, mau_a, mau_b, day=0.16):
    """vòng % : p 0..1 → sprite premult (co × co)."""
    k = 2; S = co * k
    yy, xx = np.mgrid[:S, :S].astype(np.float32); cxy = S / 2
    r = np.hypot(xx - cxy, yy - cxy); r1 = S / 2 - 4; r0 = r1 * (1 - day)
    ang = (np.degrees(np.arctan2(xx - cxy, -(yy - cxy))) + 360) % 360
    ring = np.clip((r1 - r) * 1.0, 0, 1) * np.clip((r - r0), 0, 1)
    ring = np.clip(np.minimum(r1 - r, r - r0) + 0.5, 0, 1)
    fill = np.clip((p * 360 - ang) * 0.6 + 0.5, 0, 1) * ring
    base = ring * 0.18
    a = np.maximum(fill, base)
    t = np.clip(ang / 360.0, 0, 1)[..., None]
    col = np.array(mau_a, np.float32) / 255 * (1 - t) + np.array(mau_b, np.float32) / 255 * t
    rgb = np.where(fill[..., None] > 0.01, col, np.array([1, 1, 1], np.float32))
    out = np.dstack([rgb * a[..., None], a])
    return cv2.resize(out.astype(np.float32), (co, co), interpolation=cv2.INTER_AREA)


def ve_donut(G, sp, t, dur):
    tieu(G, sp.get('tieu_de', ''), t, 330)
    p = C.ease_out(C.clamp((t - 0.25) / 1.25)) * sp.get('gia_tri', 80) / 100.0
    co = 640
    glow = np.zeros((co + 120, co + 120, 4), np.float32)
    over(G, _vong(co, p, (255, 160, 200), HONG_D), CX, 800)
    n = int(round(p * 100))
    num = chu(f'{n}%', 200, 'Montserrat-Black.ttf', (255, 255, 255), 0, ((255, 220, 238), (255, 90, 160), (230, 20, 100)), True)
    over(G, num, CX, 790, sc=1.0 + 0.04 * math.sin(t * 6))
    if sp.get('nhan'):
        q = C.clamp((t - 0.9) / 0.4)
        over(G, chu(sp['nhan'], 62, 'Montserrat-ExtraBold.ttf', (255, 255, 255), 3), CX, 1160, sc=0.9 + 0.1 * ease_back(q), al=C.ease_out(q))


def _poly_dai(pts, p):
    """đường gấp khúc cắt theo tỉ lệ độ dài p."""
    pts = np.array(pts, np.float32)
    d = np.r_[0, np.cumsum(np.hypot(*(pts[1:] - pts[:-1]).T))]
    L = d[-1] * p
    out = [pts[0]]
    for i in range(1, len(pts)):
        if d[i] <= L: out.append(pts[i])
        else:
            f = (L - d[i - 1]) / max(1e-6, d[i] - d[i - 1]); out.append(pts[i - 1] + (pts[i] - pts[i - 1]) * f); break
    return np.array(out, np.float32)


def ve_bieu_do(G, sp, t, dur):
    tieu(G, sp.get('tieu_de', ''), t, 320)
    x0, x1, y0, y1 = 150, 900, 540, 1090
    cv = np.zeros((H, W, 4), np.uint8)
    for gy in np.linspace(y0, y1, 5):          # lưới
        cv2.line(cv, (x0, int(gy)), (x1, int(gy)), (255, 255, 255, 38), 2, cv2.LINE_AA)
    cv2.line(cv, (x0, y0 - 20), (x0, y1), (255, 255, 255, 140), 5, cv2.LINE_AA)
    cv2.line(cv, (x0, y1), (x1, y1), (255, 255, 255, 140), 5, cv2.LINE_AA)
    dang = sp.get('dang', 'yoyo')
    if dang == 'yoyo':       # giảm vèo rồi vọt lại
        P = [(0, .08), (.10, .12), (.38, .90), (.46, .92), (.62, .30), (.76, .12), (.95, .05)]
    else:                    # bậc thang giảm dần đều
        P = [(0, .10), (.16, .10), (.20, .28), (.38, .28), (.42, .46), (.60, .46), (.64, .64), (.82, .64), (.86, .82), (1.0, .82)]
    pts = [(x0 + 20 + (x1 - x0 - 40) * a, y0 + (y1 - y0 - 30) * b) for a, b in P]
    p = C.ease_io(C.clamp((t - 0.35) / max(0.8, dur * 0.62)))
    seg = _poly_dai(pts, p)
    col = (255, 64, 140, 255) if dang == 'yoyo' else (46, 214, 120, 255)
    if len(seg) >= 2:
        glow = cv.copy()
        cv2.polylines(glow, [seg.astype(np.int32)], False, col[:3] + (150,), 30, cv2.LINE_AA)
        glow = cv2.GaussianBlur(glow, (0, 0), 14)
        cv = np.maximum(cv, glow)
        cv2.polylines(cv, [seg.astype(np.int32)], False, col, 13, cv2.LINE_AA)
        cv2.circle(cv, tuple(int(v) for v in seg[-1]), 24, (255, 255, 255, 255), -1, cv2.LINE_AA)
        cv2.circle(cv, tuple(int(v) for v in seg[-1]), 14, col, -1, cv2.LINE_AA)
    S = cv.astype(np.float32) / 255.0; S[..., :3] *= S[..., 3:4]
    over(G, S, W / 2, H / 2)
    for nh in sp.get('nhan', []):
        q = C.clamp((t - nh['t']) / 0.35)
        if q <= 0: continue
        over(G, chu(nh['text'], 56, 'Montserrat-ExtraBold.ttf', (255, 255, 255), 3), nh.get('x', CX), nh.get('y', 1165),
             sc=0.8 + 0.2 * ease_back(q), al=C.ease_out(q))


def ve_can_bang(G, sp, t, dur):
    tieu(G, sp.get('tieu_de', ''), t, 330)
    cx, cy = CX, 760
    p = C.clamp(t / max(1.0, dur - 0.5))
    ang = 16 * math.cos(p * 3 * math.pi) * (1 - C.ease_out(p)) ** 0.8 if p < 1 else 0.0   # lắc rồi cân bằng
    cv = np.zeros((H, W, 4), np.uint8)
    L = 330
    a = math.radians(ang)
    lx, ly = cx - L * math.cos(a), cy + L * math.sin(a) * -1 + 0
    rx, ry = cx + L * math.cos(a), cy - L * math.sin(a) * -1 + 0
    lx, ly, rx, ry = cx - L * math.cos(a), cy + L * math.sin(a), cx + L * math.cos(a), cy - L * math.sin(a)
    cv2.line(cv, (int(cx), int(cy)), (int(cx), 1050), (230, 236, 255, 255), 16, cv2.LINE_AA)       # trụ
    cv2.fillPoly(cv, [np.array([[cx - 150, 1090], [cx + 150, 1090], [cx, 1030]], np.int32)], (230, 236, 255, 255), cv2.LINE_AA)
    cv2.line(cv, (int(lx), int(ly)), (int(rx), int(ry)), (255, 255, 255, 255), 18, cv2.LINE_AA)    # đòn cân
    for (ex, ey, col) in ((lx, ly, HONG), (rx, ry, XANH)):
        cv2.line(cv, (int(ex), int(ey)), (int(ex) - 120, int(ey) + 230), (255, 255, 255, 200), 5, cv2.LINE_AA)
        cv2.line(cv, (int(ex), int(ey)), (int(ex) + 120, int(ey) + 230), (255, 255, 255, 200), 5, cv2.LINE_AA)
        cv2.ellipse(cv, (int(ex), int(ey) + 236), (150, 44), 0, 0, 180, col + (255,), -1, cv2.LINE_AA)
    cv2.circle(cv, (int(cx), int(cy)), 26, (255, 255, 255, 255), -1, cv2.LINE_AA)
    S = cv.astype(np.float32) / 255.0; S[..., :3] *= S[..., 3:4]
    over(G, S, W / 2, H / 2)
    for txt, ex, ey in ((sp.get('trai', 'NẠP VÀO'), lx, ly), (sp.get('phai', 'TIÊU HAO'), rx, ry)):
        q = C.clamp((t - 0.4) / 0.4)
        A = chu(txt, 50, 'Montserrat-ExtraBold.ttf', (255, 255, 255), 3)
        sc = min(1.0, 300 / A.shape[1])
        over(G, A, ex, ey + 330, sc=sc * (0.85 + 0.15 * ease_back(q)), al=C.ease_out(q))
    if p >= 0.98:
        q = C.clamp((t - (dur - 0.5)) / 0.3)
        over(G, chu('CÂN BẰNG', 74, 'Montserrat-Black.ttf', (255, 255, 255), 0, ((255, 255, 190), (255, 214, 60), (250, 160, 0)), True),
             CX, 1150, sc=0.8 + 0.2 * ease_back(q), al=C.ease_out(q))


def ve_cta(G, sp, t, dur):
    p = C.clamp(t / 0.5)
    k = 3; S = 330 * k
    im = Image.new('RGBA', (S, S), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((S * 0.04, S * 0.06, S * 0.96, S * 0.74), S * 0.18, fill=(255, 64, 140, 255))
    d.polygon([(S * 0.20, S * 0.70), (S * 0.46, S * 0.70), (S * 0.18, S * 0.94)], fill=(255, 64, 140, 255))
    for i in range(3):
        a = 0.5 + 0.5 * math.sin(t * 7 - i * 1.0)
        r = S * (0.055 + 0.02 * a)
        cx = S * (0.30 + 0.20 * i); cy = S * 0.40
        d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(255, 255, 255, int(150 + 105 * a)))
    ic = _fin(im, k, 330, 330)
    over(G, ic, CX, 560, sc=0.4 + 0.6 * ease_back(p), al=C.clamp(p * 3))
    y = 800 + 18 * math.sin(t * 6)
    over(G, dau('xuong', 130), CX, y, al=C.ease_out(C.clamp((t - 0.3) / 0.3)))
    for k2, txt in enumerate(sp.get('dong', [])):
        q = C.clamp((t - 0.4 - 0.25 * k2) / 0.35)
        A = chu(txt, 78 if k2 == 0 else 58, 'Montserrat-Black.ttf' if k2 == 0 else 'Montserrat-ExtraBold.ttf', (255, 255, 255), 3)
        sc = min(1.0, (RONG - 20) / A.shape[1])
        over(G, A, CX, 1000 + k2 * 120, sc=sc * (0.85 + 0.15 * ease_back(q)), al=C.ease_out(q))


# ------------------------------------------------------------------ CTA FOLLOW: nút THEO DÕI + chuông + bàn tay bấm + tim bay
# (người dùng chốt 18/11/2026: "khách không nói comment ở cuối thì cuối video PHẢI có nút CTA FOLLOW có anim, hiệu ứng bàn tay đầy đủ")
DO_NUT = (229, 38, 44); DO_SANG = (255, 92, 92); XAM_NUT = (86, 95, 112)
SS = 4


@lru_cache(maxsize=8)
def _chuong(size):
    S = size * SS
    im = Image.new('RGBA', (S, S), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    c = (255, 255, 255, 255); cx = S / 2
    d.ellipse((cx - 0.07 * S, 0.04 * S, cx + 0.07 * S, 0.18 * S), fill=c)
    d.pieslice((cx - 0.30 * S, 0.13 * S, cx + 0.30 * S, 0.73 * S), 180, 360, fill=c)
    d.polygon([(cx - 0.30 * S, 0.42 * S), (cx + 0.30 * S, 0.42 * S), (cx + 0.40 * S, 0.74 * S), (cx - 0.40 * S, 0.74 * S)], fill=c)
    d.rounded_rectangle((cx - 0.45 * S, 0.70 * S, cx + 0.45 * S, 0.80 * S), radius=0.05 * S, fill=c)
    d.ellipse((cx - 0.10 * S, 0.78 * S, cx + 0.10 * S, 0.96 * S), fill=c)
    return im.resize((size, size), Image.LANCZOS)


@lru_cache(maxsize=8)
def _tick(size):
    S = size * SS
    im = Image.new('RGBA', (S, S), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    pts = [(0.16 * S, 0.53 * S), (0.41 * S, 0.77 * S), (0.86 * S, 0.27 * S)]; wd = int(0.14 * S)
    d.line(pts, fill=(255, 255, 255, 255), width=wd, joint='curve')
    for x, y in (pts[0], pts[-1]): d.ellipse((x - wd / 2, y - wd / 2, x + wd / 2, y + wd / 2), fill=(255, 255, 255, 255))
    return im.resize((size, size), Image.LANCZOS)


@lru_cache(maxsize=16)
def _tim(size, mau=(255, 64, 100)):
    S = size * SS
    im = Image.new('RGBA', (S, S), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    r = S * 0.235; c = mau + (255,)
    d.ellipse((S * 0.06, S * 0.12, S * 0.06 + 2 * r, S * 0.12 + 2 * r), fill=c)
    d.ellipse((S * 0.94 - 2 * r, S * 0.12, S * 0.94, S * 0.12 + 2 * r), fill=c)
    d.polygon([(S * 0.07, S * 0.44), (S * 0.93, S * 0.44), (S * 0.5, S * 0.93)], fill=c)
    d.rectangle((S * 0.28, S * 0.28, S * 0.72, S * 0.50), fill=c)
    return im.resize((size, size), Image.LANCZOS)


def _ic_chip(kind, size=46):
    if kind == 'tim':
        return _tim(size)
    S = size * SS
    im = Image.new('RGBA', (S, S), (0, 0, 0, 0)); d = ImageDraw.Draw(im); w = (255, 255, 255, 255)
    if kind == 'bl':
        d.rounded_rectangle((S * 0.08, S * 0.12, S * 0.92, S * 0.70), S * 0.18, fill=w)
        d.polygon([(S * 0.24, S * 0.64), (S * 0.46, S * 0.64), (S * 0.20, S * 0.92)], fill=w)
    elif kind == 'cs':       # chia sẻ: mũi tên cong
        d.polygon([(S * 0.55, S * 0.10), (S * 0.95, S * 0.45), (S * 0.55, S * 0.80), (S * 0.55, S * 0.58), (S * 0.12, S * 0.84),
                   (S * 0.20, S * 0.46), (S * 0.55, S * 0.32)], fill=w)
    else:                    # lưu: bookmark
        d.polygon([(S * 0.22, S * 0.08), (S * 0.78, S * 0.08), (S * 0.78, S * 0.94), (S * 0.50, S * 0.70), (S * 0.22, S * 0.94)], fill=w)
    return im.resize((size, size), Image.LANCZOS)


@lru_cache(maxsize=4)
def _tay(size=250):
    """bàn tay trỏ vector (trắng viền tối, tay áo xanh); đầu ngón trỏ ở TÂM ảnh 2size × 2size, nghiêng 18°."""
    S = size * SS
    m = Image.new('L', (S, S), 0); d = ImageDraw.Draw(m)
    d.rounded_rectangle((0.31 * S, 0.02 * S, 0.49 * S, 0.62 * S), radius=0.09 * S, fill=255)
    d.rounded_rectangle((0.46 * S, 0.33 * S, 0.63 * S, 0.62 * S), radius=0.085 * S, fill=255)
    d.rounded_rectangle((0.60 * S, 0.38 * S, 0.76 * S, 0.65 * S), radius=0.08 * S, fill=255)
    d.rounded_rectangle((0.73 * S, 0.44 * S, 0.87 * S, 0.68 * S), radius=0.07 * S, fill=255)
    d.rounded_rectangle((0.25 * S, 0.46 * S, 0.87 * S, 0.90 * S), radius=0.17 * S, fill=255)
    th = Image.new('L', (S, S), 0)
    ImageDraw.Draw(th).rounded_rectangle((0.10 * S, 0.50 * S, 0.40 * S, 0.66 * S), radius=0.08 * S, fill=255)
    th = th.rotate(-28, center=(0.36 * S, 0.62 * S), resample=Image.BICUBIC)
    m = Image.fromarray(np.maximum(np.asarray(m), np.asarray(th)))
    ao = Image.new('L', (S, S), 0)
    ImageDraw.Draw(ao).rounded_rectangle((0.27 * S, 0.84 * S, 0.85 * S, 1.0 * S), radius=0.04 * S, fill=255)
    tong = Image.fromarray(np.maximum(np.asarray(m), np.asarray(ao)))
    vien = tong.filter(ImageFilter.MaxFilter(int(0.035 * S) | 1))
    im = Image.new('RGBA', (S, S), (0, 0, 0, 0))
    im.paste((24, 30, 44, 255), (0, 0), vien); im.paste((255, 255, 255, 255), (0, 0), m); im.paste((44, 96, 210, 255), (0, 0), ao)
    dd = ImageDraw.Draw(im)
    for x in (0.475, 0.615, 0.745): dd.line([(x * S, 0.42 * S), (x * S, 0.60 * S)], fill=(196, 204, 218, 255), width=int(0.012 * S))
    dd.arc((0.33 * S, 0.06 * S, 0.47 * S, 0.20 * S), 200, 340, fill=(206, 214, 226, 255), width=int(0.012 * S))
    im = im.resize((size, size), Image.LANCZOS)
    can = Image.new('RGBA', (2 * size, 2 * size), (0, 0, 0, 0))
    can.alpha_composite(im, (int(size - 0.40 * size), int(size - 0.03 * size)))
    sh = can.copy(); sh.paste((0, 0, 0, 255), (0, 0), can.getchannel('A'))
    sh.putalpha(can.getchannel('A').point(lambda v: int(v * 0.45))); sh = sh.filter(ImageFilter.GaussianBlur(9))
    out = Image.new('RGBA', can.size, (0, 0, 0, 0)); out.alpha_composite(sh, (10, 14)); out.alpha_composite(can)
    return _pm(out.rotate(18, center=(size, size), resample=Image.BICUBIC))


@lru_cache(maxsize=8)
def _nut(mau, text, rong=560, cao=128, icon=None):
    box = Image.new('RGBA', (rong, cao), (0, 0, 0, 0)); d = ImageDraw.Draw(box)
    d.rounded_rectangle((0, 0, rong - 1, cao - 1), radius=cao // 2, fill=mau + (255,))
    bong = Image.new('RGBA', (rong, cao), (0, 0, 0, 0))
    ImageDraw.Draw(bong).rounded_rectangle((10, 6, rong - 11, cao // 2), radius=cao // 3, fill=(255, 255, 255, 46))
    box.alpha_composite(bong)
    A = ve.chu_trang(text, 'Montserrat-Black.ttf', 52, (255, 255, 255), 0, (0, 3, 4, 0.35))
    t = A.img.crop((A.ox, A.oy, A.ox + A.w, A.oy + A.h))
    ic = None
    if icon == 'chuong': ic = _chuong(62)
    elif icon == 'tick': ic = _tick(54)
    iw = ic.width if ic is not None else 0
    gap = 22 if iw else 0
    x = (rong - (iw + gap + t.width)) // 2
    if ic is not None: box.alpha_composite(ic, (x, (cao - ic.height) // 2))
    box.alpha_composite(t, (x + iw + gap, (cao - t.height) // 2))
    return _pm(box), x + iw / 2


@lru_cache(maxsize=4)
def _glow():
    g = Image.new('RGBA', (640, 208), (0, 0, 0, 0))
    ImageDraw.Draw(g).rounded_rectangle((40, 40, 599, 167), radius=64, fill=DO_SANG + (255,))
    return _pm(g.filter(ImageFilter.GaussianBlur(18)))


@lru_cache(maxsize=2)
def _avatar():
    k = 3; D_ = 196
    av = Image.new('RGBA', (D_ * k, D_ * k), (0, 0, 0, 0)); dv = ImageDraw.Draw(av)
    dv.ellipse((0, 0, D_ * k - 1, D_ * k - 1), fill=(255, 255, 255, 255))
    dv.ellipse((8 * k, 8 * k, (D_ - 8) * k, (D_ - 8) * k), fill=HONG + (255,))
    dv.ellipse((D_ * k * 0.36, D_ * k * 0.22, D_ * k * 0.64, D_ * k * 0.50), fill=(255, 255, 255, 255))
    dv.pieslice((D_ * k * 0.22, D_ * k * 0.52, D_ * k * 0.78, D_ * k * 1.06), 180, 360, fill=(255, 255, 255, 255))
    mk = Image.new('L', av.size, 0); ImageDraw.Draw(mk).ellipse((0, 0, D_ * k - 1, D_ * k - 1), fill=255)
    av.putalpha(Image.fromarray(np.minimum(np.asarray(mk), np.asarray(av.getchannel('A')))))
    return _pm(av.resize((D_, D_), Image.LANCZOS))


def _vong_song(G, cx, cy, p, r0, r1, day=5, al=1.0):
    """vòng sóng trắng nở ra, p 0..1."""
    if p <= 0 or p >= 1: return
    r = r0 + (r1 - r0) * C.ease_out(p)
    S = int(r * 2 + day * 4 + 6)
    cv = np.zeros((S, S, 4), np.uint8)
    cv2.circle(cv, (S // 2, S // 2), int(r), (255, 255, 255, 255), max(1, int(day * (1 - p) + 1)), cv2.LINE_AA)
    a = cv.astype(np.float32) / 255.0; a[..., :3] *= a[..., 3:4]
    over(G, a, cx, cy, al=(1 - p) * 0.8 * al)


def ve_follow(G, sp, t, dur):
    """avatar tròn (không bịa tên kênh) → 'THEO DÕI' → 4 chip Thích / Bình luận / Chia sẻ / Lưu → nút đỏ + chuông →
    bàn tay trượt vào BẤM (nút lún + sóng) → nút xám 'ĐÃ THEO DÕI' + tim bay → tay rút."""
    dong = sp.get('dong') or ['THEO DÕI', 'để xem thêm chia sẻ hữu ích']
    T_BAM = sp.get('t_bam', 1.15); T_DOI = T_BAM + 0.08
    y_av, y_tit, y_phu, y_chip, y_nut = 400, 590, 674, 810, 960
    u = C.clamp((t - 0.05) / 0.4)
    for j in range(2):
        tj = t - 0.5 - 0.8 * j
        if tj > 0: _vong_song(G, CX, y_av, (tj % 1.6) / 1.6, 104, 160, 4, C.clamp(u * 3))
    over(G, _avatar(), CX, y_av, sc=0.2 + 0.8 * ease_back(u), al=C.clamp(u * 3))
    v = C.ease_out(C.clamp((t - 0.25) / 0.3))
    over(G, chu(dong[0].upper(), 78, 'Montserrat-Black.ttf', (255, 255, 255), 3), CX, y_tit + 14 * (1 - v), al=v)
    if len(dong) > 1 and dong[1]:
        v2 = C.ease_out(C.clamp((t - 0.38) / 0.3))
        A = chu(dong[1], 40, 'Montserrat-SemiBold.ttf', (214, 224, 240), 0)
        over(G, A, CX, y_phu + 14 * (1 - v2), sc=min(1.0, (RONG - 30) / A.shape[1]), al=v2)
    # 4 chip biểu tượng (tim nảy sau khi bấm)
    chips = [('tim', 'Thích'), ('bl', 'Bình luận'), ('cs', 'Chia sẻ'), ('luu', 'Lưu')]
    w = 192; gap = 12; x = CX - (w * 4 + gap * 3) / 2
    for i, (kd, nhan) in enumerate(chips):
        q = C.clamp((t - 0.46 - 0.08 * i) / 0.32)
        if q > 0:
            cx0 = x + w / 2; sq = 0.5 + 0.5 * ease_back(q); aq = C.clamp(q * 3)
            nay = 1.0 + (0.28 * math.sin(math.pi * C.clamp((t - T_BAM - 0.12) / 0.4)) if kd == 'tim' else 0)
            over(G, the(w, 84, 42, (255, 255, 255, 40), (255, 255, 255, 110)), cx0, y_chip, sc=sq, al=aq)
            over(G, _pm(_ic_chip(kd, 40)), cx0 - w / 2 + 44, y_chip, sc=sq * nay, al=aq)
            tx = chu(nhan, 26, 'Montserrat-SemiBold.ttf', (255, 255, 255), 0, None, False)
            over(G, tx, cx0 + 26, y_chip, sc=min(1.0, (w - 92) / tx.shape[1]) * sq, al=aq)
        x += w + gap
    # nút + chuông + tay
    vb = C.clamp((t - 0.52) / 0.35)
    if vb <= 0: return
    nhan_l = 1 - 0.06 * math.sin(math.pi * (t - T_BAM) / 0.2) if T_BAM <= t < T_BAM + 0.2 else 1.0
    s = max(0.05, ease_back(vb)) * nhan_l
    n1, xc = _nut(DO_NUT, 'THEO DÕI', 560, 128, 'chuong')
    if t < T_DOI:
        nhip = 0.5 + 0.5 * math.sin(2 * math.pi * t / 0.8)
        over(G, _glow(), CX, y_nut, sc=s, al=C.clamp(vb) * (0.35 + 0.35 * nhip))
        over(G, n1, CX, y_nut, sc=s, al=C.clamp(vb * 3))
    else:
        w2 = C.clamp((t - T_DOI) / 0.12)
        n2, _ = _nut(XAM_NUT, 'ĐÃ THEO DÕI', 560, 128, 'tick')
        over(G, n1, CX, y_nut, sc=s, al=1 - w2)
        over(G, n2, CX, y_nut, sc=s * (0.92 + 0.08 * ease_back(w2)), al=w2)
    # tim bay sau khi bấm
    for j in range(9):
        tj = t - (T_DOI + 0.05 + 0.16 * j)
        if 0 <= tj < 1.5:
            pj = tj / 1.5
            hx = CX + (1 if j % 2 else -1) * (250 + 38 * (j % 3)) + 26 * math.sin(tj * 5 + j)     # tim bay hai bên, không che chữ
            hy = y_nut - 80 - 420 * C.ease_out(pj)
            over(G, _pm(_tim(54 if j % 2 else 40)), hx, hy, sc=0.5 + 0.5 * C.clamp(pj * 5), al=1 - C.clamp((pj - 0.55) / 0.45))
    # bàn tay: trượt vào → bấm → rút
    T_IN, T_OUT = T_BAM - 0.45, T_BAM + 0.65
    if T_IN <= t <= T_OUT + 0.45:
        dx, dyt = CX + 120, y_nut + 34
        if t < T_BAM - 0.05:
            kk = C.ease_out((t - T_IN) / 0.40); ox, oy, at = 300 * (1 - kk), 440 * (1 - kk), C.clamp((t - T_IN) / 0.15)
        elif t < T_OUT:
            ox, oy, at = 0.0, 0.0, 1.0
        else:
            kk = C.ease_io((t - T_OUT) / 0.4); ox, oy, at = 170 * kk, 280 * kk, 1 - kk
        sc = 1 - 0.08 * math.sin(math.pi * (t - T_BAM + 0.05) / 0.25) if T_BAM - 0.05 <= t < T_BAM + 0.2 else 1.0
        _vong_song(G, dx, dyt, (t - T_BAM) / 0.6 if T_BAM <= t < T_BAM + 0.6 else 0, 18, 150, 5)
        over(G, _tay(250), dx + ox, dyt + oy, sc=sc, al=at)


KIEU = {'ket_qua': ve_ket_qua, 'danh_sach': ve_danh_sach, 'donut': ve_donut, 'bieu_do': ve_bieu_do, 'can_bang': ve_can_bang,
        'cta': ve_cta, 'follow': ve_follow}


def ve_demo(F, sp, i, i0, i1, nen_mo):
    """vẽ cảnh demo ở khung i lên F (float 0..1 HxWx3): nền = ảnh người nói nhoè + tối, đồ hoạ phủ lên."""
    VAO, RA = 6, 5
    f = i - i0; g = i1 - i
    pv = C.clamp(f / VAO); pr = C.clamp(g / RA) if g < RA else 1.0
    al = C.ease_out(pv) * C.ease_out(pr)
    if al <= 0.003: return F
    F = F * (1 - al) + nen_mo * al
    G = np.zeros((H, W, 4), np.float32)
    KIEU[sp['kieu']](G, sp, f / C.FPS, (i1 - i0) / C.FPS)
    sc = 1.0 + 0.10 * (1 - C.ease_out(pv)) + 0.05 * (1 - pr)
    if abs(sc - 1) > 1e-3:
        M = np.array([[sc, 0, W / 2 * (1 - sc)], [0, sc, H / 2 * (1 - sc)]], np.float32)
        G = cv2.warpAffine(G, M, (W, H), flags=cv2.INTER_LINEAR, borderValue=(0, 0, 0, 0))
    G *= al
    return F * (1 - G[..., 3:4]) + G[..., :3]


def nen_demo(F):
    """nền demo: người nói nhoè mạnh + tối + ánh xanh tím, hơi hồng ở góc."""
    s = cv2.resize(F, (W // 6, H // 6), interpolation=cv2.INTER_AREA)
    s = cv2.GaussianBlur(s, (0, 0), 6)
    b = cv2.resize(s, (W, H), interpolation=cv2.INTER_CUBIC)
    b = b * 0.26 + np.array(NAVY, np.float32) / 255 * 0.72
    yy = np.linspace(0, 1, H, dtype=np.float32)[:, None, None]
    b = b + np.array([0.10, 0.02, 0.10], np.float32) * np.clip(1 - yy * 1.6, 0, 1) * 0.6
    return np.clip(b, 0, 1)
