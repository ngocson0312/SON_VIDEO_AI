# -*- coding: utf-8 -*-
"""BÀN TAY TRỎ kiểu 3D-emoji (làm lại 18/11/2026 — người dùng: "làm ra bàn tay xịn xịn tí, đừng như kia").

Không dùng hình có sẵn: dựng bằng code từ các ỐNG TRỤ (capsule chain) có pháp tuyến thật → shading mịn như nhựa mềm:
  da ấm 3 tông (bóng / sáng / vùng tối), Lambert bọc + phản chiếu mềm + viền SÁNG dưới da (subsurface đỏ ở mép),
  bóng tiếp xúc giữa các ngón, nếp gấp khớp, móng tay có vệt sáng, cẳng tay mờ dần ra ngoài.
Trả (sprite premult RGBA float32, (tip_x, tip_y)) — đầu ngón trỏ ở tip, tay nghiêng ~16°."""
import math
from functools import lru_cache
import numpy as np
import cv2
from PIL import Image, ImageDraw

SSK = 2                      # siêu lấy mẫu
CW, CH = 500, 800            # canvas 1x
L = np.array([-0.50, -0.62, 0.60], np.float32); L /= np.linalg.norm(L)
V = np.array([0, 0, 1], np.float32)
Hh = L + V; Hh /= np.linalg.norm(Hh)
DA_TOI = np.array([196, 118, 92], np.float32)
DA_GIUA = np.array([238, 180, 142], np.float32)
DA_SANG = np.array([255, 224, 196], np.float32)
DO_MAU = np.array([232, 104, 92], np.float32)


def _grid():
    yy, xx = np.mgrid[:CH * SSK, :CW * SSK].astype(np.float32) / SSK
    return xx, yy


def _ong(xx, yy, pts, rs):
    """ống trụ qua chuỗi điểm pts với bán kính rs: trả (alpha, nx, ny, nz, z)."""
    best_z = np.full(xx.shape, -1.0, np.float32)
    nx = np.zeros_like(xx); ny = np.zeros_like(xx); nz = np.zeros_like(xx); al = np.zeros_like(xx)
    for (x0, y0), (x1, y1), r0, r1 in zip(pts[:-1], pts[1:], rs[:-1], rs[1:]):
        dx, dy = x1 - x0, y1 - y0
        ll = dx * dx + dy * dy + 1e-6
        t = np.clip(((xx - x0) * dx + (yy - y0) * dy) / ll, 0, 1)
        cx, cy = x0 + t * dx, y0 + t * dy
        r = r0 + (r1 - r0) * t
        ex, ey = (xx - cx), (yy - cy)
        d = np.hypot(ex, ey)
        a = np.clip((r - d) * SSK * 0.5 + 0.5, 0, 1)
        q = np.clip(d / np.maximum(r, 1e-3), 0, 1)
        z = np.sqrt(np.clip(1 - q * q, 0, 1)) * r
        m = (a > 0) & (z > best_z - 1e-4)
        best_z = np.where(m, z, best_z)
        nx = np.where(m, ex / np.maximum(r, 1e-3), nx); ny = np.where(m, ey / np.maximum(r, 1e-3), ny)
        nz = np.where(m, np.sqrt(np.clip(1 - q * q, 0, 1)), nz)
        al = np.maximum(al, a)
    return al, nx, ny, nz


def _blob(xx, yy, cx, cy, rx, ry):
    """khối elip (lòng bàn tay / mu bàn tay): pháp tuyến dạng vòm."""
    ex, ey = (xx - cx) / rx, (yy - cy) / ry
    q2 = ex * ex + ey * ey
    al = np.clip((1 - np.sqrt(q2)) * min(rx, ry) * SSK * 0.5 + 0.5, 0, 1)
    nz = np.sqrt(np.clip(1 - q2, 0, 1))
    return al, ex * 0.9, ey * 0.9, nz


SKIN = (DA_TOI, DA_GIUA, DA_SANG, DO_MAU, 0.32)
GANG = (np.array([168, 182, 226], np.float32), np.array([234, 239, 252], np.float32), np.array([255, 255, 255], np.float32),
        np.array([140, 160, 236], np.float32), 0.22)         # găng trắng hoạt hình: bóng lam tím, viền sáng lam


def _tong(al, nx, ny, nz, tang=1.0, pal=SKIN):
    toi, giua, sang, rim, spk = pal
    nrm = np.sqrt(nx * nx + ny * ny + nz * nz) + 1e-6
    nx, ny, nz = nx / nrm, ny / nrm, nz / nrm
    dif = np.clip(nx * L[0] + ny * L[1] + nz * L[2], 0, 1)
    wrap = np.clip(dif * 0.85 + 0.15, 0, 1)
    col = np.where(wrap[..., None] < 0.5, toi + (giua - toi) * (wrap[..., None] / 0.5),
                   giua + (sang - giua) * ((wrap[..., None] - 0.5) / 0.5))
    fres = np.clip(1 - nz, 0, 1) ** 2.6
    col = col * (1 - 0.55 * fres[..., None]) + rim * 0.55 * fres[..., None] * (0.55 + 0.45 * dif[..., None])
    sp = np.clip(nx * Hh[0] + ny * Hh[1] + nz * Hh[2], 0, 1) ** 36 * spk
    col = col + sp[..., None] * 255
    return np.clip(col, 0, 255), al * tang


def _dat_phan(buf, ab, col, al, bong=0.38, lech=(10, 14)):
    """ghép 1 bộ phận (col, al) lên buf (RGB nhân trước + alpha) và đổ BÓNG TIẾP XÚC lên những gì đã có bên dưới."""
    rgb, a = buf
    sh = cv2.GaussianBlur(al, (0, 0), 7 * SSK)
    sh = np.roll(np.roll(sh, int(lech[1] * SSK), 0), int(lech[0] * SSK), 1)
    rgb *= (1 - bong * sh * (a > 0.01))[..., None]
    rgb[:] = rgb * (1 - al[..., None]) + col * al[..., None]
    a[:] = a * (1 - al) + al


@lru_cache(maxsize=2)
def tay_xin():
    xx, yy = _grid()
    rgb = np.zeros((CH * SSK, CW * SSK, 3), np.float32); a = np.zeros((CH * SSK, CW * SSK), np.float32)
    buf = (rgb, a)
    # --- cẳng tay + mu bàn tay (khối lớn)
    for (al, nx, ny, nz) in (
            _ong(xx, yy, [(262, 560), (270, 800)], [108, 100]),
            _blob(xx, yy, 258, 500, 124, 134)):
        c, aa = _tong(al, nx, ny, nz); _dat_phan(buf, a, c, aa, 0.0)
    # --- ngón trỏ (duỗi thẳng, hơi cong ở đầu)
    idx = _ong(xx, yy, [(238, 380), (236, 270), (233, 180), (229, 110), (226, 92)], [34, 31, 28, 25, 23])
    c, aa = _tong(*idx); _dat_phan(buf, a, c, aa, 0.34, (9, 12))
    # nếp gấp khớp + móng
    kh = Image.new('L', (CW * SSK, CH * SSK), 0); dk = ImageDraw.Draw(kh)
    for yk, hw in ((272, 24), (184, 21)):
        for dyk in (-7, 0, 7):
            dk.arc(((236 - hw) * SSK, (yk - 10 + dyk) * SSK, (236 + hw) * SSK, (yk + 12 + dyk) * SSK), 20, 160, fill=255, width=int(1.6 * SSK))
    kh = cv2.GaussianBlur(np.asarray(kh).astype(np.float32) / 255, (0, 0), 0.9 * SSK) * idx[0] * 0.30
    rgb *= (1 - kh)[..., None] * 0.0 + 1 - (kh)[..., None] * 0.9
    ng = Image.new('L', (CW * SSK, CH * SSK), 0)
    ImageDraw.Draw(ng).rounded_rectangle((212 * SSK, 70 * SSK, 246 * SSK, 118 * SSK), 15 * SSK, fill=255)
    nga = cv2.GaussianBlur(np.asarray(ng).astype(np.float32) / 255, (0, 0), 0.8 * SSK)
    yy_n = np.clip((yy - 70) / 48, 0, 1)
    ngcol = np.array([255, 214, 208], np.float32) * (1 - yy_n[..., None]) + np.array([248, 180, 176], np.float32) * yy_n[..., None]
    rgb[:] = rgb * (1 - 0.82 * nga[..., None] * idx[0][..., None]) + ngcol * 0.82 * nga[..., None] * idx[0][..., None]
    vet = Image.new('L', (CW * SSK, CH * SSK), 0)
    ImageDraw.Draw(vet).ellipse((217 * SSK, 76 * SSK, 228 * SSK, 96 * SSK), fill=255)
    vet = cv2.GaussianBlur(np.asarray(vet).astype(np.float32) / 255, (0, 0), 2.0 * SSK) * 0.75 * idx[0]
    rgb[:] = rgb + vet[..., None] * 90
    # --- 3 ngón cuộn (chạm vào lòng bàn tay) — xếp sau ngón cái
    for ch in ([(290, 392), (338, 396), (352, 420)], [(292, 440), (336, 444), (346, 466)], [(292, 484), (326, 488), (334, 506)]):
        rs = [29, 28, 25] if ch[0][1] < 420 else ([27, 26, 23] if ch[0][1] < 460 else [24, 23, 21])
        c, aa = _tong(*_ong(xx, yy, ch, rs)); _dat_phan(buf, a, c, aa, 0.36, (8, 11))
    # --- ngón cái (vắt chéo phía trước)
    th = _ong(xx, yy, [(170, 540), (176, 470), (200, 418), (232, 392)], [38, 34, 30, 26])
    c, aa = _tong(*th); _dat_phan(buf, a, c, aa, 0.40, (10, 12))
    # móng ngón cái
    ng2 = Image.new('L', (CW * SSK, CH * SSK), 0)
    ImageDraw.Draw(ng2).ellipse((218 * SSK, 378 * SSK, 244 * SSK, 408 * SSK), fill=255)
    n2 = cv2.GaussianBlur(np.asarray(ng2).astype(np.float32) / 255, (0, 0), 0.8 * SSK) * th[0] * 0.55
    rgb[:] = rgb * (1 - n2[..., None]) + np.array([255, 214, 208], np.float32) * n2[..., None]
    # --- cẳng tay mờ dần ra ngoài + bóng đổ
    fade = np.clip((CH - yy - 6) / 200.0, 0, 1)
    a[:] = a * fade
    out = np.dstack([np.clip(rgb, 0, 255) / 255.0 * a[..., None], a]).astype(np.float32)
    big = cv2.resize(out, (CW, CH), interpolation=cv2.INTER_AREA)
    # bóng đổ mềm phía sau
    sh = cv2.GaussianBlur(big[..., 3], (0, 0), 13)
    ca = np.zeros_like(big); ca[16:, 12:, 3] = sh[:-16, :-12] * 0.42
    res = big + ca * (1 - big[..., 3:4])
    tip = (226.0, 70.0)
    pad = 280
    can = cv2.copyMakeBorder(res, pad, pad, pad, pad, cv2.BORDER_CONSTANT, value=(0, 0, 0, 0))
    R = cv2.getRotationMatrix2D((tip[0] + pad, tip[1] + pad), 14, 1.0)
    can = cv2.warpAffine(can, R, (can.shape[1], can.shape[0]), flags=cv2.INTER_LINEAR, borderValue=(0, 0, 0, 0))
    return can, (tip[0] + pad, tip[1] + pad)


@lru_cache(maxsize=2)
def tay_gang():
    """BÀN TAY GĂNG TRẮNG hoạt hình (người dùng gửi ảnh mẫu 18/11/2026: găng trắng, viền đen mảnh + viền sáng vàng nhạt, cổ tay có
    miệng găng hình oval): ngón trỏ chỉ, ba ngón cuộn mập, ngón cái; shading ống trụ mịn (bóng lam tím)."""
    xx, yy = _grid()
    rgb = np.zeros((CH * SSK, CW * SSK, 3), np.float32); a = np.zeros((CH * SSK, CW * SSK), np.float32)
    buf = (rgb, a)
    P = GANG
    # miệng găng (cuff): khối oval + lòng găng lam tím
    c, aa = _tong(*_blob(xx, yy, 262, 640, 120, 66), pal=P); _dat_phan(buf, a, c, aa, 0.0)
    lg = _blob(xx, yy, 262, 668, 92, 34)
    in_col = np.array([122, 132, 214], np.float32) * (0.75 + 0.25 * np.clip(lg[3], 0, 1))[..., None]
    rgb[:] = rgb * (1 - lg[0][..., None] * 0.95) + in_col * lg[0][..., None] * 0.95
    # mu bàn tay
    c, aa = _tong(*_blob(xx, yy, 258, 520, 128, 128), pal=P); _dat_phan(buf, a, c, aa, 0.34, (6, 9))
    # ngón trỏ (mập, ngắn hơn bản da)
    idx = _ong(xx, yy, [(242, 430), (240, 350), (238, 285), (235, 238), (233, 226)], [46, 44, 42, 40, 38])
    c, aa = _tong(*idx, pal=P); _dat_phan(buf, a, c, aa, 0.34, (8, 10))
    # 3 ngón cuộn
    for ch, rs in (([(292, 412), (344, 416), (360, 444)], [35, 34, 31]), ([(294, 466), (342, 470), (354, 496)], [33, 32, 29]),
                   ([(294, 516), (332, 520), (342, 540)], [30, 29, 27])):
        c, aa = _tong(*_ong(xx, yy, ch, rs), pal=P); _dat_phan(buf, a, c, aa, 0.34, (7, 10))
    # ngón cái
    th = _ong(xx, yy, [(168, 560), (172, 492), (198, 440), (232, 414)], [42, 38, 34, 30])
    c, aa = _tong(*th, pal=P); _dat_phan(buf, a, c, aa, 0.38, (8, 10))
    # 3 vạch đặc trưng trên mu găng
    vach = Image.new('L', (CW * SSK, CH * SSK), 0); dv = ImageDraw.Draw(vach)
    for k, dxk in enumerate((-30, 0, 30)):
        dv.arc(((250 + dxk - 8) * SSK, (500 - 30) * SSK, (250 + dxk + 8) * SSK, (500 + 36) * SSK), 80, 280, fill=255, width=int(3.2 * SSK))
    vach = cv2.GaussianBlur(np.asarray(vach).astype(np.float32) / 255, (0, 0), 0.9 * SSK)
    rgb[:] = rgb * (1 - 0.8 * vach[..., None]) + np.array([40, 42, 64], np.float32) * 0.8 * vach[..., None]
    # viền đen mảnh + viền sáng vàng nhạt bên ngoài
    m1 = (a > 0.4).astype(np.uint8)
    ring_d = cv2.dilate(m1, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (int(7 * SSK) | 1,) * 2)).astype(np.float32)
    ring_g = cv2.dilate(m1, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (int(21 * SSK) | 1,) * 2)).astype(np.float32)
    ring_d = cv2.GaussianBlur(ring_d, (0, 0), 0.8 * SSK); ring_g = cv2.GaussianBlur(ring_g, (0, 0), 1.6 * SSK)
    out_rgb = np.zeros_like(rgb); out_a = np.zeros_like(a)
    out_rgb = np.array([255, 240, 178], np.float32) * ring_g[..., None]; out_a = ring_g * 0.96
    out_rgb = out_rgb * (1 - ring_d[..., None]) + np.array([34, 36, 56], np.float32) * ring_d[..., None]; out_a = np.maximum(out_a, ring_d)
    af = a
    fin_rgb = out_rgb * (1 - af[..., None]) + rgb * af[..., None]
    fin_a = np.maximum(out_a, af)
    res = np.dstack([np.clip(fin_rgb, 0, 255) / 255.0 * fin_a[..., None], fin_a]).astype(np.float32)
    big = cv2.resize(res, (CW, CH), interpolation=cv2.INTER_AREA)
    sh = cv2.GaussianBlur(big[..., 3], (0, 0), 12)
    ca = np.zeros_like(big); ca[14:, 10:, 3] = sh[:-14, :-10] * 0.36
    big = big + ca * (1 - big[..., 3:4])
    tip = (234.0, 190.0)
    pad = 280
    can = cv2.copyMakeBorder(big, pad, pad, pad, pad, cv2.BORDER_CONSTANT, value=(0, 0, 0, 0))
    R = cv2.getRotationMatrix2D((tip[0] + pad, tip[1] + pad), 16, 1.0)
    can = cv2.warpAffine(can, R, (can.shape[1], can.shape[0]), flags=cv2.INTER_LINEAR, borderValue=(0, 0, 0, 0))
    return can, (tip[0] + pad, tip[1] + pad)


@lru_cache(maxsize=2)
def tay_tro():
    """CON TRỎ BÀN TAY kiểu icon liên kết (người dùng gửi ảnh mẫu 18/11/2026 'như này nè'): tay trắng, VIỀN ĐEN dày, ngón trỏ chỉ lên,
    3 ngón gập có vạch ngăn, ngón cái bên trái, miệng cổ tay, bóng đổ mềm. Vẽ vector siêu lấy mẫu. Trả (sprite premult RGBA, (tip_x, tip_y))."""
    SS = 4; cw, ch = 440, 560
    def mk(): return Image.new('L', (cw * SS, ch * SS), 0)
    def rr(d, x0, y0, x1, y1, r): d.rounded_rectangle((x0 * SS, y0 * SS, x1 * SS, y1 * SS), r * SS, fill=255)
    m = mk(); d = ImageDraw.Draw(m)
    rr(d, 150, 30, 214, 330, 32)           # ngón trỏ
    rr(d, 210, 152, 266, 340, 27)          # ngón giữa
    rr(d, 262, 174, 316, 340, 26)          # ngón áp út
    rr(d, 312, 204, 364, 340, 25)          # ngón út
    rr(d, 118, 262, 364, 444, 52)          # lòng bàn tay
    d.line([(150 * SS, 372 * SS), (96 * SS, 296 * SS)], fill=255, width=62 * SS)   # ngón cái
    for p in ((150, 372), (96, 296)): d.ellipse(((p[0] - 31) * SS, (p[1] - 31) * SS, (p[0] + 31) * SS, (p[1] + 31) * SS), fill=255)
    rr(d, 138, 438, 346, 494, 16)          # miệng cổ tay
    a = np.asarray(m).astype(np.uint8)
    k = int(13 * SS) | 1
    vien = cv2.dilate(a, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (k, k)))
    # lòng trắng + bóng xám rất nhẹ (dưới cằm các ngón, dưới lòng bàn tay)
    yy = np.mgrid[:ch * SS, :cw * SS][0].astype(np.float32) / SS
    sang = 255 - 18 * np.clip((yy - 300) / 160, 0, 1)
    rgb = np.dstack([sang, sang, sang + 4]).astype(np.float32)
    ln = mk(); dl = ImageDraw.Draw(ln); w = int(6.4 * SS)
    for x, y0, y1 in ((213, 172, 300), (265, 196, 300), (315, 222, 300), (151, 262, 340)):
        dl.line([(x * SS, y0 * SS), (x * SS, y1 * SS)], fill=255, width=w)
    dl.line([(140 * SS, 441 * SS), (344 * SS, 441 * SS)], fill=255, width=w)          # mép miệng cổ tay
    for x in (176, 240, 304):                                                           # 3 vạch ngắn ở cổ tay
        dl.line([(x * SS, 458 * SS), (x * SS, 480 * SS)], fill=255, width=int(3.4 * SS))
    ln = cv2.GaussianBlur(np.asarray(ln).astype(np.float32) / 255, (0, 0), 0.7 * SS)
    ln = np.minimum(ln, 1.0) * (a > 0)
    den = np.array([16, 18, 24], np.float32)
    rgb = rgb * (1 - ln[..., None]) + den * ln[..., None]
    af = cv2.GaussianBlur(a.astype(np.float32) / 255, (0, 0), 0.5 * SS)
    vf = cv2.GaussianBlur(vien.astype(np.float32) / 255, (0, 0), 0.6 * SS)
    fin = den * (1 - af[..., None]) * vf[..., None] + rgb * af[..., None]
    fa = np.maximum(vf, af)
    res = np.dstack([np.clip(fin, 0, 255) / 255.0, fa]).astype(np.float32)
    res[..., :3] = np.clip(res[..., :3], 0, 1) * 1.0
    big = cv2.resize(res, (cw, ch), interpolation=cv2.INTER_AREA)
    big[..., :3] = np.clip(big[..., :3], 0, 1)
    big[..., :3] *= 1.0
    # premult: fin đã là màu trên vùng có alpha; nhân alpha
    big[..., :3] = big[..., :3] * big[..., 3:4] / np.maximum(big[..., 3:4], 1e-3) * big[..., 3:4]
    sh = cv2.GaussianBlur(big[..., 3], (0, 0), 11)
    ca = np.zeros_like(big); ca[16:, 10:, 3] = sh[:-16, :-10] * 0.40
    big = big + ca * (1 - big[..., 3:4])
    tip = (182.0, 26.0)
    pad = 240
    can = cv2.copyMakeBorder(big, pad, pad, pad, pad, cv2.BORDER_CONSTANT, value=(0, 0, 0, 0))
    R = cv2.getRotationMatrix2D((tip[0] + pad, tip[1] + pad), 10, 1.0)
    can = cv2.warpAffine(can, R, (can.shape[1], can.shape[0]), flags=cv2.INTER_LINEAR, borderValue=(0, 0, 0, 0))
    return can, (tip[0] + pad, tip[1] + pad)


if __name__ == '__main__':
    import sys
    s, tip = (tay_tro() if (len(sys.argv) > 2 and sys.argv[2] == 'tro') else tay_gang() if (len(sys.argv) > 2 and sys.argv[2] == 'gang') else tay_xin())
    h, w = s.shape[:2]
    bg = np.ones((h, w, 3), np.float32) * np.array([0.30, 0.34, 0.36], np.float32)
    o = bg * (1 - s[..., 3:4]) + s[..., :3]
    Image.fromarray((np.clip(o, 0, 1) * 255).astype(np.uint8)).save(sys.argv[1] if len(sys.argv) > 1 else 'tay_xin.png')
    print(s.shape, tip)
