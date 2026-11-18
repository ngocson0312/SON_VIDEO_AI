# -*- coding: utf-8 -*-
"""CTA CUỐI VIDEO — OVERLAY (không phủ kín màn), làm theo ẢNH MẪU người dùng gửi 18/11/2026:
  nút FOLLOW đỏ BÓNG (icon người+ bên trái, chữ trắng đậm) nằm ngay dưới cằm (đúng dải chữ nhấn, trong vùng an toàn) →
  CON TRỎ BÀN TAY trắng viền đen (TX.tay_tro, ảnh mẫu 'như này nè') trượt vào chỉ ngón trỏ vào nút, vòng tròn mảnh quanh đầu ngón →
  BẤM: nút lún, chấm chạm + vòng sóng trắng, TIA NỔ vàng toả quanh đầu ngón, sao nhấp nháy → nút chuyển kính "FOLLOWING ✓" → tay rút.
  (bản trước: 4 icon bóng loáng bị chê "lỏ"; bản kính mờ 4 icon cũng bỏ — người dùng chỉ muốn nút + tay như ảnh mẫu.)
plan['cta'] = [{t0, t1, kieu: 'follow', t_bam?}]."""
import math
from functools import lru_cache
import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageFilter
import chung as C
import ve
import demo as DM
import tay_xin as TX
from demo import over, _pm

W, H = C.W, C.H
CX = (C.AN_TOAN['x0'] + C.AN_TOAN['x1']) / 2
K3 = 4
DO_A, DO_B = (255, 70, 104), (236, 28, 72)            # nút đỏ: gradient rất nhẹ
ACC = {'tim': (255, 62, 96), 'bl': (72, 168, 255), 'cs': (56, 214, 150), 'luu': (255, 202, 70)}
T = {'nut': 0.18, 'tay_vao': 0.80, 'bam': 1.42, 'tay_ra': 2.15}
ICON_D, ICON_GAP = 104, 146


# ------------------------------------------------------------------ kính mờ (frosted glass) vẽ thẳng lên khung F
@lru_cache(maxsize=16)
def _mask_bo(w, h, r):
    k = 3
    m = Image.new('L', (w * k, h * k), 0)
    ImageDraw.Draw(m).rounded_rectangle((0, 0, w * k - 1, h * k - 1), r * k, fill=255)
    return np.asarray(m.resize((w, h), Image.LANCZOS)).astype(np.float32) / 255.0


def vitro(F, cx, cy, w, h, r, al=1.0, tint=(14, 16, 24), mix=0.44, blur=14):
    """kính mờ: vùng nền nhoè + phủ tối nhẹ, sáng dần ở mép trên; bo góc r."""
    x0, y0 = int(round(cx - w / 2)), int(round(cy - h / 2))
    a0, b0, a1, b1 = max(0, x0), max(0, y0), min(W, x0 + w), min(H, y0 + h)
    if a1 <= a0 or b1 <= b0 or al <= 0.003: return
    reg = F[b0:b1, a0:a1]
    m = _mask_bo(int(w), int(h), int(r))[b0 - y0:b1 - y0, a0 - x0:a1 - x0, None] * al
    bl = cv2.GaussianBlur(reg, (0, 0), blur)
    tinted = bl * (1 - mix) + np.array(tint, np.float32) / 255 * mix
    tinted = tinted + np.linspace(0.10, 0.0, b1 - b0, dtype=np.float32)[:, None, None]
    F[b0:b1, a0:a1] = reg * (1 - m) + tinted * m


@lru_cache(maxsize=16)
def vien_kinh(w, h, r, a=0.34):
    k = 3; pad = 6
    im = Image.new('RGBA', ((w + 2 * pad) * k, (h + 2 * pad) * k), (0, 0, 0, 0))
    ImageDraw.Draw(im).rounded_rectangle((pad * k, pad * k, (pad + w) * k, (pad + h) * k), r * k, outline=(255, 255, 255, int(255 * a)), width=2 * k)
    hl = Image.new('RGBA', im.size, (0, 0, 0, 0))      # vệt sáng mảnh ở mép trên
    ImageDraw.Draw(hl).rounded_rectangle(((pad + 10) * k, (pad + 2) * k, (pad + w - 10) * k, (pad + 5) * k), 2 * k, fill=(255, 255, 255, 70))
    im.alpha_composite(hl)
    return _pm(im.resize((w + 2 * pad, h + 2 * pad), Image.LANCZOS))


@lru_cache(maxsize=16)
def quang(d, mau, cuong=0.55):
    """quầng sáng mềm tròn."""
    S = int(d)
    yy, xx = np.mgrid[:S, :S].astype(np.float32)
    r = np.hypot(xx - S / 2, yy - S / 2) / (S / 2)
    a = np.clip(1 - r, 0, 1) ** 2 * cuong
    rgb = np.broadcast_to(np.array(mau, np.float32) / 255, (S, S, 3)) * a[..., None]
    return np.dstack([rgb, a]).astype(np.float32)


@lru_cache(maxsize=16)
def quang_det(rx, ry, mau, cuong=0.5):
    """quầng sáng dẹt (elip) — nằm trong dải nút, không bắn lên mặt."""
    Wd, Hd = int(rx * 2), int(ry * 2)
    yy, xx = np.mgrid[:Hd, :Wd].astype(np.float32)
    r = np.hypot((xx - Wd / 2) / (Wd / 2), (yy - Hd / 2) / (Hd / 2))
    a = np.clip(1 - r, 0, 1) ** 2 * cuong
    rgb = np.broadcast_to(np.array(mau, np.float32) / 255, (Hd, Wd, 3)) * a[..., None]
    return np.dstack([rgb, a]).astype(np.float32)


# ------------------------------------------------------------------ biểu tượng NÉT (line icon) trắng / màu
def _tim_pts(cx, cy, s, n=120):
    t = np.linspace(0, 2 * math.pi, n)
    x = 16 * np.sin(t) ** 3
    y = -(13 * np.cos(t) - 5 * np.cos(2 * t) - 2 * np.cos(3 * t) - np.cos(4 * t))
    return [(cx + s * a, cy + s * b) for a, b in zip(x, y)]


@lru_cache(maxsize=64)
def glyph(kind, size, mau=(255, 255, 255), dac=False):
    """kind: tim | bl | cs | luu | chuong | tick ; dac=True → tô đặc (tim, bookmark). Trả PIL RGBA size × size."""
    S = size * K3
    im = Image.new('RGBA', (S, S), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    c = tuple(mau) + (255,); w = max(3, int(S * 0.075))

    def duong(pts, close=False):
        pts = list(pts) + ([pts[0]] if close else [])
        d.line(pts, fill=c, width=w, joint='curve')
        for p in (pts[0], pts[-1]): d.ellipse((p[0] - w / 2, p[1] - w / 2, p[0] + w / 2, p[1] + w / 2), fill=c)
    if kind == 'tim':
        pts = _tim_pts(S / 2, S * 0.48, S * 0.0245)
        if dac: d.polygon(pts, fill=c)
        duong(pts, True)
    elif kind == 'bl':
        d.rounded_rectangle((S * 0.17, S * 0.20, S * 0.83, S * 0.68), S * 0.16, outline=c, width=w)
        d.polygon([(S * 0.30, S * 0.64), (S * 0.46, S * 0.64), (S * 0.27, S * 0.82)], fill=c)
        for i in range(3): d.ellipse((S * (0.355 + 0.13 * i), S * 0.415, S * (0.415 + 0.13 * i), S * 0.475), fill=c)
    elif kind == 'cs':
        duong([(S * 0.20, S * 0.50), (S * 0.20, S * 0.80), (S * 0.80, S * 0.80), (S * 0.80, S * 0.50)])
        duong([(S * 0.50, S * 0.64), (S * 0.50, S * 0.16)])
        duong([(S * 0.32, S * 0.33), (S * 0.50, S * 0.15), (S * 0.68, S * 0.33)])
    elif kind == 'luu':
        pts = [(S * 0.30, S * 0.16), (S * 0.70, S * 0.16), (S * 0.70, S * 0.84), (S * 0.50, S * 0.66), (S * 0.30, S * 0.84)]
        if dac: d.polygon(pts, fill=c)
        duong(pts, True)
    elif kind == 'chuong':
        cx = S / 2
        d.arc((cx - 0.27 * S, 0.14 * S, cx + 0.27 * S, 0.70 * S), 180, 360, fill=c, width=w)
        d.line([(cx - 0.27 * S, 0.42 * S), (cx - 0.36 * S, 0.74 * S), (cx + 0.36 * S, 0.74 * S), (cx + 0.27 * S, 0.42 * S)], fill=c, width=w, joint='curve')
        d.ellipse((cx - 0.08 * S, 0.80 * S, cx + 0.08 * S, 0.94 * S), fill=c)
        d.ellipse((cx - 0.045 * S, 0.06 * S, cx + 0.045 * S, 0.17 * S), fill=c)
    else:   # tick
        duong([(S * 0.20, S * 0.54), (S * 0.42, S * 0.74), (S * 0.82, S * 0.28)])
    return im.resize((size, size), Image.LANCZOS)


@lru_cache(maxsize=16)
def nut_do(rong, cao):
    """nút đỏ PHẲNG: gradient nhẹ + bóng sáng mép trên (không gờ dày) — chữ Theo dõi (chuông vẽ riêng để rung)."""
    k = 3; pad = 6
    im = Image.new('RGBA', ((rong + 2 * pad) * k, (cao + 2 * pad) * k), (0, 0, 0, 0))
    face = np.zeros((cao * k, rong * k, 4), np.float32)
    ys = np.linspace(0, 1, cao * k, dtype=np.float32)[:, None, None]
    face[..., :3] = (np.array(DO_A, np.float32) * (1 - ys) + np.array(DO_B, np.float32) * ys) / 255.0
    face[..., 3] = 1
    fm = Image.new('L', (rong * k, cao * k), 0); ImageDraw.Draw(fm).rounded_rectangle((0, 0, rong * k - 1, cao * k - 1), (cao // 2) * k, fill=255)
    fi = Image.fromarray((face * 255).astype(np.uint8), 'RGBA'); fi.putalpha(fm)
    im.alpha_composite(fi, (pad * k, pad * k))
    hl = Image.new('RGBA', im.size, (0, 0, 0, 0))
    ImageDraw.Draw(hl).rounded_rectangle(((pad + 14) * k, (pad + 3) * k, (pad + rong - 14) * k, (pad + cao * 0.42) * k), (cao // 3) * k, fill=(255, 255, 255, 38))
    im.alpha_composite(hl)
    ImageDraw.Draw(im).rounded_rectangle((pad * k, pad * k, (pad + rong) * k, (pad + cao) * k), (cao // 2) * k, outline=(255, 255, 255, 70), width=k)
    return _pm(im.resize((rong + 2 * pad, cao + 2 * pad), Image.LANCZOS))


@lru_cache(maxsize=32)
def chu_nut(text, co=44):
    A = ve.chu_trang(text, 'Montserrat-ExtraBold.ttf', co, (255, 255, 255), 0, (0, 3, 6, 0.40))
    return _pm(A.img.crop((A.ox - 2, A.oy - 2, A.ox + A.w + 2, A.oy + A.h + 2)))


@lru_cache(maxsize=2)
def tay3d(size=300):
    """bàn tay TRỎ giả 3D: mỗi ngón / lòng bàn tay là 1 khối có bản đồ độ cao (distance transform) → Lambert + phản chiếu nhẹ
    + tối ở khe ngón; cổ tay MỜ DẦN (không tay áo), bóng đổ mềm. Trả (premult RGBA, (tip_x, tip_y))."""
    S = size
    def rr(x0, y0, x1, y1, r):
        m = Image.new('L', (S * 2, S * 2), 0)
        ImageDraw.Draw(m).rounded_rectangle((x0 * S * 2, y0 * S * 2, x1 * S * 2, y1 * S * 2), r * S * 2, fill=255)
        return m
    parts = {'index': rr(0.40, 0.04, 0.56, 0.62, 0.08), 'mid': rr(0.55, 0.36, 0.69, 0.62, 0.07), 'ring': rr(0.68, 0.41, 0.80, 0.64, 0.06),
             'pinky': rr(0.79, 0.47, 0.90, 0.68, 0.055), 'palm': rr(0.30, 0.46, 0.90, 1.0, 0.14)}
    th = Image.new('L', (S * 2, S * 2), 0)
    ImageDraw.Draw(th).rounded_rectangle((0.08 * S * 2, 0.52 * S * 2, 0.40 * S * 2, 0.68 * S * 2), 0.07 * S * 2, fill=255)
    parts['thumb'] = th.rotate(-26, center=(0.38 * S * 2, 0.64 * S * 2), resample=Image.BICUBIC)
    H2 = np.zeros((S * 2, S * 2), np.float32); mask = np.zeros((S * 2, S * 2), np.float32)
    for kname, m in parts.items():
        a = np.asarray(m).astype(np.uint8)
        dist = cv2.distanceTransform((a > 127).astype(np.uint8), cv2.DIST_L2, 5).astype(np.float32)
        if dist.max() > 0: dist = (dist / dist.max()) ** 0.55
        H2 = np.maximum(H2, dist * (a > 127)); mask = np.maximum(mask, (a > 127).astype(np.float32))
    Hs = cv2.GaussianBlur(H2, (0, 0), 3.0)
    gy, gx = np.gradient(Hs)
    nz = 1.0 / np.sqrt(1 + (gx * 9) ** 2 + (gy * 9) ** 2); nx, ny = -gx * 9 * nz, -gy * 9 * nz
    L = np.array([-0.45, -0.60, 0.66], np.float32); L /= np.linalg.norm(L)
    diff = np.clip(nx * L[0] + ny * L[1] + nz * L[2], 0, 1)
    spec = np.clip(nx * -0.3 + ny * -0.5 + nz * 0.8, 0, 1) ** 24 * 0.35
    k = np.clip(diff * 1.05, 0, 1)[..., None]
    col = np.array([226, 160, 118], np.float32) * (1 - k) + np.array([255, 224, 190], np.float32) * k
    col = col * (0.72 + 0.28 * np.clip(Hs * 1.8, 0, 1))[..., None] + spec[..., None] * 255
    nail = Image.new('L', (S * 2, S * 2), 0)
    ImageDraw.Draw(nail).rounded_rectangle((0.435 * S * 2, 0.07 * S * 2, 0.525 * S * 2, 0.16 * S * 2), 0.03 * S * 2, fill=255)
    nl = cv2.GaussianBlur(np.asarray(nail).astype(np.float32) / 255, (0, 0), 1.2)[..., None]
    col = col * (1 - 0.5 * nl) + np.array([255, 236, 230], np.float32) * 0.5 * nl
    edge = np.clip(cv2.dilate(mask, np.ones((5, 5), np.uint8)) - mask, 0, 1)
    col = np.where(edge[..., None] > 0, col * 0.55, col)
    al = np.clip(cv2.GaussianBlur(np.maximum(mask, edge), (0, 0), 0.9) * 1.15, 0, 1)
    fade = np.clip((1.0 - np.linspace(0, 1, S * 2, dtype=np.float32)) / 0.14, 0, 1)[:, None]     # cổ tay mờ dần
    al = al * fade
    rgba = np.dstack([np.clip(col, 0, 255) / 255.0, al]).astype(np.float32)
    sh = cv2.GaussianBlur(al, (0, 0), 14)
    out = np.zeros((S * 2, S * 2, 4), np.float32); off = (14, 18)
    out[off[1]:, off[0]:, 3] = sh[:S * 2 - off[1], :S * 2 - off[0]] * 0.40
    a3 = rgba[..., 3:4]
    out = np.dstack([out[..., :3] * (1 - a3) + rgba[..., :3] * a3, out[..., 3] * (1 - al) + al])
    out[..., :3] *= out[..., 3:4]
    big = cv2.resize(out, (S, S), interpolation=cv2.INTER_AREA)
    tip = (0.48 * S, 0.045 * S)
    pad = int(S * 0.5)
    can = cv2.copyMakeBorder(big, pad, pad, pad, pad, cv2.BORDER_CONSTANT, value=(0, 0, 0, 0))
    R = cv2.getRotationMatrix2D((tip[0] + pad, tip[1] + pad), 16, 1.0)
    can = cv2.warpAffine(can, R, (can.shape[1], can.shape[0]), flags=cv2.INTER_LINEAR, borderValue=(0, 0, 0, 0))
    return can, (tip[0] + pad, tip[1] + pad)


@lru_cache(maxsize=8)
def sao(size, mau=(255, 246, 190)):
    """sao 4 cánh MẢNH (lõm) — lấp lánh tinh tế."""
    k = 4; S = size * k
    im = Image.new('RGBA', (S, S), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    c = S / 2; q = S * 0.07
    d.polygon([(c, 0), (c + q, c - q), (S, c), (c + q, c + q), (c, S), (c - q, c + q), (0, c), (c - q, c - q)], fill=mau + (255,))
    return _pm(im.filter(ImageFilter.GaussianBlur(0.8)).resize((size, size), Image.LANCZOS))


@lru_cache(maxsize=8)
def tim_kinh(size):
    """tim nhỏ gradient hồng → đỏ."""
    k = 4; S = size * k
    m = Image.new('L', (S, S), 0)
    ImageDraw.Draw(m).polygon(_tim_pts(S / 2, S * 0.50, S * 0.0285), fill=255)
    a = np.asarray(m.filter(ImageFilter.GaussianBlur(1.0))).astype(np.float32) / 255
    ys = np.linspace(0, 1, S, dtype=np.float32)[:, None, None]
    col = (np.array([255, 120, 150], np.float32) * (1 - ys) + np.array([232, 26, 76], np.float32) * ys) / 255
    out = np.dstack([np.broadcast_to(col, (S, S, 3)) * a[..., None], a]).astype(np.float32)
    return cv2.resize(out, (size, size), interpolation=cv2.INTER_AREA)


def _song_el(G, cx, cy, p, rx0, rx1, ratio=0.30, day=3, al=1.0, mau=(255, 255, 255)):
    """vòng sóng MẢNH hình elip dẹt (cao = ratio × rộng) — nằm trong dải nút, không quét lên mặt."""
    if p <= 0 or p >= 1: return
    rx = rx0 + (rx1 - rx0) * C.ease_out(p); ry = rx * ratio
    Wd, Hd = int(rx * 2 + 16), int(ry * 2 + 16)
    cv = np.zeros((Hd, Wd, 4), np.uint8)
    cv2.ellipse(cv, (Wd // 2, Hd // 2), (int(rx), int(ry)), 0, 0, 360, mau + (255,), max(1, int(day * (1 - p) + 1)), cv2.LINE_AA)
    a = cv.astype(np.float32) / 255.0; a[..., :3] *= a[..., 3:4]
    over(G, a, cx, cy, al=(1 - p) * 0.7 * al)


def _lap_lanh(G, cx, cy, t, seed, n=10, rx=300, ry=80, dai=0.9, kich=24):
    """n sao mảnh nhấp nháy trong elip dẹt quanh (cx, cy): hiện / tắt lệch pha."""
    if t < 0 or t > dai + 0.4: return
    rng = np.random.default_rng(seed)
    for j in range(n):
        ang = rng.uniform(0, 2 * math.pi); rr = math.sqrt(rng.uniform(0.15, 1.0))
        px = cx + rx * rr * math.cos(ang); py = cy + ry * rr * math.sin(ang)
        t0 = rng.uniform(0, 0.4); q = (t - t0) / 0.5
        if 0 < q < 1:
            tw = math.sin(math.pi * q)
            over(G, sao(max(10, int(kich * rng.uniform(0.6, 1.0)))), px, py, sc=0.4 + 0.8 * tw, al=tw, goc=rng.uniform(-20, 20))


def _tim_bay(G, cx, cy, t, n=6, dai=1.8):
    for j in range(n):
        tj = t - 0.10 * j
        if 0 <= tj < dai:
            p = tj / dai; side = -1 if j % 2 else 1
            hx = cx + side * (340 + 46 * (j % 3)) + 18 * math.sin(tj * 4 + j)              # hai bên, ngoài mặt
            hy = cy - 14 - 170 * C.ease_out(p)
            over(G, tim_kinh(44 if j % 2 else 34), hx, hy, sc=0.5 + 0.5 * C.clamp(p * 6), al=(1 - C.clamp((p - 0.5) / 0.5)) * 0.95)


@lru_cache(maxsize=4)
def ic_nguoi_cong(size=64):
    """icon người + dấu cộng (follow): đầu tròn + vai + dấu + nhỏ ở góc phải trên."""
    k = K3; S = size * k
    im = Image.new('RGBA', (S, S), (0, 0, 0, 0)); d = ImageDraw.Draw(im); c = (255, 255, 255, 255)
    d.ellipse((S * 0.14, S * 0.14, S * 0.50, S * 0.50), fill=c)
    d.pieslice((S * 0.02, S * 0.52, S * 0.62, S * 1.12), 180, 360, fill=c)
    w = int(S * 0.085)
    d.line([(S * 0.80, S * 0.18), (S * 0.80, S * 0.50)], fill=c, width=w)
    d.line([(S * 0.64, S * 0.34), (S * 0.96, S * 0.34)], fill=c, width=w)
    return im.resize((size, size), Image.LANCZOS)


@lru_cache(maxsize=4)
def nut_follow(rong=540, cao=116):
    """nút đỏ BÓNG như ảnh mẫu: gradient đỏ sáng → đỏ đậm, vệt bóng trắng nửa trên, gờ đậm mảnh dưới, bóng đổ mềm."""
    k = 3; pad = 22; dep = 8
    Wt, Ht = rong + 2 * pad, cao + dep + 2 * pad
    im = Image.new('RGBA', (Wt * k, Ht * k), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    r = cao // 2
    sh = Image.new('RGBA', im.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle((pad * k, (pad + dep + 8) * k, (pad + rong) * k, (pad + dep + cao + 8) * k), r * k, fill=(0, 0, 0, 120))
    im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(9 * k)))
    d.rounded_rectangle((pad * k, (pad + dep) * k, (pad + rong) * k, (pad + dep + cao) * k), r * k, fill=(150, 10, 34, 255))       # gờ dưới
    face = np.zeros((cao * k, rong * k, 4), np.float32)
    ys = np.linspace(0, 1, cao * k, dtype=np.float32)[:, None, None]
    face[..., :3] = (np.array((255, 96, 108), np.float32) * (1 - ys) + np.array((214, 22, 50), np.float32) * ys) / 255.0
    face[..., 3] = 1
    fm = Image.new('L', (rong * k, cao * k), 0); ImageDraw.Draw(fm).rounded_rectangle((0, 0, rong * k - 1, cao * k - 1), r * k, fill=255)
    fi = Image.fromarray((face * 255).astype(np.uint8), 'RGBA'); fi.putalpha(fm)
    im.alpha_composite(fi, (pad * k, pad * k))
    gl = Image.new('RGBA', im.size, (0, 0, 0, 0))
    ImageDraw.Draw(gl).rounded_rectangle(((pad + 16) * k, (pad + 6) * k, (pad + rong - 16) * k, (pad + cao * 0.48) * k), (cao // 3) * k, fill=(255, 255, 255, 64))
    im.alpha_composite(gl)
    return _pm(im.resize((Wt, Ht), Image.LANCZOS)), -dep / 2


def _tia(G, cx, cy, p, r0=52, r1=120, n=10, mau=(255, 206, 70), day=5, dai=24):
    """TIA NỔ: n vạch ngắn toả quanh (cx, cy) như ảnh mẫu (vạch vàng quanh đầu ngón)."""
    if p <= 0 or p >= 1: return
    S = int(r1 * 2 + 40)
    cv = np.zeros((S, S, 4), np.uint8)
    rr0 = r0 + (r1 - r0) * 0.55 * C.ease_out(p); rr1 = rr0 + dai * (1 - 0.6 * p)
    for j in range(n):
        ang = 2 * math.pi * j / n + 0.3
        x0, y0 = S / 2 + rr0 * math.cos(ang), S / 2 + rr0 * math.sin(ang)
        x1, y1 = S / 2 + rr1 * math.cos(ang), S / 2 + rr1 * math.sin(ang)
        cv2.line(cv, (int(x0), int(y0)), (int(x1), int(y1)), mau + (255,), max(2, int(day * (1 - 0.5 * p))), cv2.LINE_AA)
    a = cv.astype(np.float32) / 255.0; a[..., :3] *= a[..., 3:4]
    over(G, a, cx, cy, al=1 - C.clamp((p - 0.45) / 0.55))


def ve_cta(F, sp, i, i0, i1, y_c):
    """vẽ CTA overlay ở khung i lên F (float 0..1 HxWx3). y_c = tâm dải (đúng chỗ chữ nhấn, dưới cằm)."""
    t = (i - i0) / C.FPS
    if t < 0 or i > i1: return F
    F = F.copy()
    G = np.zeros((H, W, 4), np.float32)
    tb = sp.get('t_bam', T['bam']); ra = min(T['tay_ra'], tb + 0.7)
    RW, RH = 540, 116
    vb = C.clamp((t - T['nut']) / 0.42)
    if vb > 0:
        da_bam = t >= tb + 0.06
        press = math.sin(math.pi * (t - tb + 0.06) / 0.28) if tb - 0.06 <= t < tb + 0.22 else 0.0
        s = max(0.05, C.ease_back(vb, 1.8)) * (1 - 0.05 * press)
        dyp = 6 * press
        sp_n, dy_n = nut_follow(RW, RH)
        nhip = 0.5 + 0.5 * math.sin(2 * math.pi * t / 1.0)
        if not da_bam:
            over(G, quang_det(RW * 0.62, RH * 1.15, (255, 56, 92), 0.55), CX, y_c + 8, sc=s, al=C.clamp(vb) * (0.5 + 0.35 * nhip))
            over(G, sp_n, CX, y_c + dy_n + dyp, sc=s, al=C.clamp(vb * 3))
            tx = chu_nut('FOLLOW', 50); ic = _pm(ic_nguoi_cong(66))
            wt = ic.shape[1] + 22 + tx.shape[1]
            xi = CX - wt / 2 + ic.shape[1] / 2; xt = CX - wt / 2 + ic.shape[1] + 22 + tx.shape[1] / 2
            pulso = 1.0 + 0.05 * math.sin(2 * math.pi * t / 0.9) if t < tb - 0.3 else 1.0
            over(G, ic, CX + (xi - CX) * s, y_c + dyp, sc=s * pulso, al=C.clamp(vb * 3))
            over(G, tx, CX + (xt - CX) * s, y_c + dyp, sc=s, al=C.clamp(vb * 3))
        else:
            w2 = C.clamp((t - tb - 0.06) / 0.16)
            nay = 1.0 + 0.07 * math.sin(math.pi * C.clamp((t - tb - 0.06) / 0.4))
            tx = chu_nut('FOLLOW', 50); ic = _pm(ic_nguoi_cong(66)); wt = ic.shape[1] + 22 + tx.shape[1]
            over(G, sp_n, CX, y_c + dy_n, sc=s, al=1 - w2)
            over(G, ic, CX - wt / 2 + ic.shape[1] / 2, y_c, sc=s, al=1 - w2)
            over(G, tx, CX - wt / 2 + ic.shape[1] + 22 + tx.shape[1] / 2, y_c, sc=s, al=1 - w2)
            dw = int(RW * 0.88 * s * nay); dh = int(RH * 0.92 * s * nay)
            vitro(F, CX, y_c, dw, dh, dh // 2, al=w2 * 0.98, tint=(20, 22, 32), mix=0.50)
            over(G, vien_kinh(dw, dh, dh // 2, 0.5), CX, y_c, al=w2)
            tx2 = chu_nut('FOLLOWING', 44); wt2 = 58 + 20 + tx2.shape[1]
            over(G, _pm(glyph('tick', 50, (96, 230, 160))), CX - wt2 / 2 + 29, y_c, sc=s * nay, al=w2)
            over(G, tx2, CX - wt2 / 2 + 78 + tx2.shape[1] / 2, y_c, sc=s * nay, al=w2)
        tk = t - (tb + 0.04)
        if tk >= 0:
            over(G, quang_det(330, 100, (255, 214, 120), 0.65), CX, y_c, al=math.exp(-tk * 3.4))
            _lap_lanh(G, CX, y_c, tk, 91, 9, 300, 64, 0.9, 24)
    # --- bàn tay găng trắng + chấm chạm + vòng sóng + tia nổ
    if T['tay_vao'] <= t <= ra + 0.5:
        hand, tip = TX.tay_tro()
        dx, dyt = CX + 215, y_c + 14
        if t < tb - 0.06:
            kk = C.ease_out((t - T['tay_vao']) / (tb - 0.06 - T['tay_vao'])); ox, oy, at = 360 * (1 - kk), 520 * (1 - kk), C.clamp((t - T['tay_vao']) / 0.15)
            goc = -16 * (1 - kk)
        elif t < ra:
            ox, oy, at, goc = 0.0, 0.0, 1.0, 0.0
        else:
            kk = C.ease_io((t - ra) / 0.45); ox, oy, at = 240 * kk, 400 * kk, 1 - kk; goc = 10 * kk
        sc = 0.52 * (1 - 0.09 * math.sin(math.pi * (t - tb + 0.06) / 0.28) if tb - 0.06 <= t < tb + 0.22 else 1.0)
        if tb - 0.40 <= t < tb + 0.9:        # VÒNG TRÒN MẢNH quanh đầu ngón (như ảnh mẫu), nhịp phình nhẹ
            q = C.clamp((t - (tb - 0.40)) / 0.25)
            rr = int(74 * (0.85 + 0.15 * C.ease_out(q)) * (1 + 0.10 * C.clamp((t - tb) / 0.9)))
            ring = np.zeros((2 * rr + 12, 2 * rr + 12, 4), np.float32)
            cv2.circle(ring, (rr + 6, rr + 6), rr, (1, 1, 1, 0.80), 3, cv2.LINE_AA); ring[..., :3] *= ring[..., 3:4]
            over(G, ring, dx, dyt, al=C.clamp(q * 2) * (1 - C.clamp((t - tb - 0.45) / 0.45)))
        if tb - 0.12 <= t < tb + 0.5:        # chấm chạm
            u = C.clamp((t - (tb - 0.12)) / 0.18)
            dia = int(70 * (0.7 + 0.3 * C.ease_back(u)) * (1 + 0.22 * C.clamp((t - tb) / 0.5)))
            dot = np.zeros((dia + 8, dia + 8, 4), np.float32)
            cv2.circle(dot, ((dia + 8) // 2, (dia + 8) // 2), dia // 2, (1, 1, 1, 0.34), -1, cv2.LINE_AA)
            cv2.circle(dot, ((dia + 8) // 2, (dia + 8) // 2), dia // 2, (1, 1, 1, 0.75), 2, cv2.LINE_AA)
            dot[..., :3] *= dot[..., 3:4]
            over(G, dot, dx, dyt, al=(1 - C.clamp((t - tb - 0.25) / 0.25)))
        if tb <= t < tb + 0.6:
            _song_el(G, dx, dyt, (t - tb) / 0.6, 34, 150, 1.0, 3, 1.0, (255, 255, 255))
            _tia(G, dx, dyt, (t - tb) / 0.6)
        h, w = hand.shape[:2]
        over(G, hand, dx + ox + (w / 2 - tip[0]) * sc, dyt + oy + (h / 2 - tip[1]) * sc, sc=sc, al=at, goc=goc)
    a = G[..., 3:4]
    return F * (1 - a) + G[..., :3]
