# -*- coding: utf-8 -*-
"""ĐIỂM NHẤN trên bản đồ (góp ý chủ dự án 04/11/2026 sau bản 3: "highlight rõ các địa điểm, đa dạng, có tên địa danh").

Bộ động tác (khai trong `nhan_manh` của từng cảnh, hoặc tự bật theo loại cảnh — SKILL.md C10):
  song       gợn sóng loang từ 1 điểm (lặp theo chu kỳ)
  ghim       ghim rơi xuống, nảy, có bóng đổ
  chu_thich  chú thích kéo dây: chấm → dây gấp khúc → hộp navy có vạch màu (tên IN HOA + dòng phụ)
  huy_hieu   huy hiệu số: pill vàng chữ navy có mũi nhọn chỉ xuống điểm, bật kiểu back-out
  ngam       vùng ngắm: tối dần ngoài vòng tròn + vòng nét đứt xoay
  nhan       nhãn địa danh trắng viền tối + chấm (kiểu nhãn đầu/cuối đoạn)
  + vạch chảy dọc tuyến (ve_dong_chay), viền vùng tự vẽ (ve_vien_chay), pill chấm màu (pill_cham),
    TÊN ĐỊA DANH quanh camera (DiaDanh: OSM place qua Photon reverse, tránh đè chữ khác),
    bản đồ định vị nhỏ góc dưới trái (DinhVi).
Mọi chữ phụ tự đặt đều tránh: thẻ đầu đề, thẻ hook, logo, dải sub (y ≥ 1385), bản đồ định vị (lớp Chiem).
"""
import cv2
import numpy as np
from PIL import Image, ImageDraw

import ban_do as B
import chung as C
from chung import W, H, clamp, ramp, smooth, ease_out

CAM = (255, 145, 60)
NGOC = (90, 222, 170)
XANH = (120, 175, 255)
HONG = (245, 120, 180)
DO = (232, 52, 48)
BANG_MAU = [C.VANG, CAM, NGOC, XANH, HONG]
MAU_TEN = {"vang": C.VANG, "cam": CAM, "ngoc": NGOC, "xanh": XANH, "hong": HONG, "do": DO, "trang": C.TRANG,
           "navy": C.NAVY}
VIEN_TOI = (10, 18, 30)
DAI_SUB = (0, 1385, W, H)          # dải sub karaoke 2 dòng: không đặt chữ bản đồ vào đây


def mau(x, i=0):
    """None → màu thứ i của bảng; tên màu (vang, cam, ngoc, xanh, hong, do, trang, navy) hoặc [r, g, b]"""
    if x is None:
        return BANG_MAU[i % len(BANG_MAU)]
    if isinstance(x, str):
        return MAU_TEN.get(x.lower(), C.VANG)
    return tuple(int(v) for v in list(x)[:3])


def back_out(x, s=1.70158):
    x = clamp(x) - 1
    return 1 + (s + 1) * x ** 3 + s * x ** 2


def bounce_out(x):
    x = clamp(x)
    n, d = 7.5625, 2.75
    if x < 1 / d:
        return n * x * x
    if x < 2 / d:
        x -= 1.5 / d
        return n * x * x + 0.75
    if x < 2.5 / d:
        x -= 2.25 / d
        return n * x * x + 0.9375
    x -= 2.625 / d
    return n * x * x + 0.984375


# ---------------------------------------------------------------- chiếm chỗ (chống đè chữ)

class Chiem:
    """các hộp (x0, y0, x1, y1) đã có chữ/thẻ trong khung hiện tại"""

    def __init__(self, cam=()):
        self.r = [tuple(float(v) for v in r) for r in cam if r]

    def dat(self, r, pad=0):
        if r:
            self.r.append((r[0] - pad, r[1] - pad, r[2] + pad, r[3] + pad))

    def trung(self, r, pad=6):
        x0, y0, x1, y1 = r
        for a in self.r:
            if x0 - pad < a[2] and x1 + pad > a[0] and y0 - pad < a[3] and y1 + pad > a[1]:
                return True
        return False


# ---------------------------------------------------------------- động tác

def ve_song(frame, x, y, tl, mau_=C.VANG, r0=12, r1=95, chu_ky=1.5, so_vong=2, day=4, alpha=1.0, lap=True):
    """gợn sóng loang từ (x, y); tl = giây kể từ lúc bắt đầu; lap=False: chỉ 1 lượt"""
    if tl < 0 or alpha <= 0.003:
        return
    R = int(r1 + day + 4)
    lay = np.zeros((2 * R, 2 * R, 4), np.uint8)
    co = False
    for k in range(so_vong):
        ph = tl / chu_ky - k / so_vong
        if ph < 0 or (not lap and ph >= 1):
            continue
        ph = ph % 1.0
        r = r0 + (r1 - r0) * ease_out(ph)
        a = (1 - ph) ** 1.3
        cv2.circle(lay, (R, R), int(r), (0, 0, 0, int(140 * a)), day + 3, cv2.LINE_AA)
        cv2.circle(lay, (R, R), int(r), tuple(int(v) for v in mau_) + (int(255 * a),), day, cv2.LINE_AA)
        co = True
    if co:
        C.dan(frame, lay, x - R, y - R, alpha)


def _bong_elip(frame, x, y, rx, ry, alpha):
    if alpha <= 0.01:
        return
    R = int(rx + 14)
    lay = np.zeros((2 * R, 2 * R, 4), np.uint8)
    cv2.ellipse(lay, (R, R), (max(1, int(rx)), max(1, int(ry))), 0, 0, 360, (0, 0, 0, 255), -1, cv2.LINE_AA)
    lay = cv2.GaussianBlur(lay, (0, 0), 4)
    C.dan(frame, lay, x - R, y - R, alpha)


def ve_ghim_roi(frame, x, y, tl, mau_=C.VANG, co=1.0, roi=0.5, alpha=1.0):
    """ghim rơi từ trên xuống (x, y), nảy, bóng đổ lớn dần → hộp chiếm chỗ"""
    if tl < 0 or alpha <= 0.003:
        return None
    u = clamp(tl / roi)
    dy = -170 * (1 - bounce_out(u))
    _bong_elip(frame, x, y + 2, 18 * co * (0.4 + 0.6 * u), 6 * co * (0.4 + 0.6 * u), 0.5 * alpha * u)
    B.ve_ghim(frame, x, y + dy, mau_, co, alpha * clamp(u * 4))
    s = 44 * co
    return (x - s / 2, y + dy - s * 1.6, x + s / 2, y + dy)


_cache = {}


def _the_chu_thich(text, phu, mau_):
    k = ("ct", text, phu, tuple(mau_))
    if k in _cache:
        return _cache[k]
    parts = [C.chu(text.upper(), "xbold", 30, fill=C.TRANG, track=1)]
    if phu:
        parts.append(C.chu(phu, "semi", 23, fill=tuple(mau_)))
    txt = C.xep_doc(parts, gap=4, align="left")
    w, h = txt.width + 52, txt.height + 28
    box = C.hop_bo((w, h), 12, tuple(C.NAVY) + (242,), vien=tuple(C.NAVY_VIEN) + (255,), vien_w=2)
    ImageDraw.Draw(box).rounded_rectangle((0, 0, 11, h - 1), radius=6, fill=tuple(mau_) + (255,))
    box.alpha_composite(txt, (30, 14))
    sh, p = C.bong_do(box, blur=10, alpha=0.5)
    out = Image.new("RGBA", (w + 2 * p, h + 2 * p), (0, 0, 0, 0))
    out.alpha_composite(sh, (0, 5))
    out.alpha_composite(box, (p, p))
    _cache[k] = (np.asarray(out), p, w, h)
    return _cache[k]


def ve_chu_thich(frame, x, y, tl, text, phu=None, mau_=C.VANG, huong=None, cao=78, alpha=1.0):
    """chấm ở (x, y) → dây chéo lên rồi ngang (0,3 s) → hộp navy vạch màu trượt vào → hộp chiếm chỗ"""
    if tl < 0 or alpha <= 0.003 or not text:
        return None
    arr, p, w, h = _the_chu_thich(text, phu, mau_)
    if huong is None:
        huong = "trai" if x > W * 0.56 else "phai"
    sx = 1 if huong == "phai" else -1

    def dat(sx_):
        ex_ = x + sx_ * (cao * 0.7 + 44)
        return ex_, (ex_ if sx_ > 0 else ex_ - w)
    ex, bx = dat(sx)
    if bx < 20 or bx + w > W - 20:
        sx = -sx
        ex, bx = dat(sx)
    bx = clamp(bx, 20, W - 20 - w)
    ey = clamp(y - cao, 205 + h / 2, 1370 - h / 2)
    by = ey - h / 2
    pts = np.array([[x, y], [x + sx * cao * 0.7, ey], [ex, ey]], np.float64)
    u = smooth(clamp(tl / 0.3))
    part, _ = B.doan_theo_tien_do(pts, u)
    if len(part) >= 2 and alpha > 0.5:
        q = np.round(part).astype(np.int32).reshape(-1, 1, 2)
        cv2.polylines(frame, [q], False, VIEN_TOI, 7, cv2.LINE_AA)
        cv2.polylines(frame, [q], False, tuple(int(v) for v in mau_), 3, cv2.LINE_AA)
    B.ve_cham(frame, x, y, 8, mau_, alpha=alpha)
    a = ease_out(ramp(tl, 0.22, 0.25))
    if a > 0:
        C.dan(frame, arr, bx - p + sx * 16 * (1 - a), by - p, a * alpha)
    return (bx, by, bx + w, by + h)


def _the_huy_hieu(text, nen, chu_mau):
    k = ("hh", text, tuple(nen), tuple(chu_mau))
    if k in _cache:
        return _cache[k]
    t = C.chu(text.upper(), "black", 38, fill=tuple(chu_mau), track=1)
    w, h, mui = t.width + 54, t.height + 26, 16
    im = Image.new("RGBA", (w, h + mui), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.polygon([(w / 2 - 16, h - 4), (w / 2 + 16, h - 4), (w / 2, h + mui - 1)], fill=(255, 255, 255, 255))
    d.rounded_rectangle((0, 0, w - 1, h - 1), radius=h // 2, fill=(255, 255, 255, 255))
    d.polygon([(w / 2 - 12, h - 6), (w / 2 + 12, h - 6), (w / 2, h + mui - 5)], fill=tuple(nen) + (255,))
    d.rounded_rectangle((3, 3, w - 4, h - 4), radius=h // 2 - 3, fill=tuple(nen) + (255,))
    im.alpha_composite(t, ((w - t.width) // 2, (h - t.height) // 2))
    sh, p = C.bong_do(im, blur=12, alpha=0.55)
    out = Image.new("RGBA", (w + 2 * p, h + mui + 2 * p), (0, 0, 0, 0))
    out.alpha_composite(sh, (0, 6))
    out.alpha_composite(im, (p, p))
    _cache[k] = (out, np.asarray(out), p, w, h + mui)
    return _cache[k]


def hop_huy_hieu(x, y, text, nen=C.VANG, chu_mau=C.NAVY):
    """hộp chiếm chỗ của huy hiệu (chưa vẽ) — để bỏ huy hiệu cũ nếu đè thẻ đầu đề / chữ khác"""
    _, _, _, w, h = _the_huy_hieu(text, nen, chu_mau)
    return (x - w / 2, y - 4 - h, x + w / 2, y - 4)


def ve_huy_hieu(frame, x, y, tl, text, nen=C.VANG, chu_mau=C.NAVY, alpha=1.0):
    """huy hiệu số, mũi nhọn chạm (x, y), bật back-out 0,35 s → hộp chiếm chỗ"""
    if tl < 0 or alpha <= 0.003 or not text:
        return None
    im, arr, p, w, h = _the_huy_hieu(text, nen, chu_mau)
    s = 0.25 + 0.75 * back_out(clamp(tl / 0.35))
    if abs(s - 1) > 2e-3:
        arr = np.asarray(im.resize((max(1, int(im.width * s)), max(1, int(im.height * s))), Image.BILINEAR))
    tx, ty = (p + w / 2) * s, (p + h) * s
    C.dan(frame, arr, x - tx, y - 4 - ty, alpha * clamp(tl / 0.1))
    return (x - w / 2, y - 4 - h, x + w / 2, y - 4)


_mask = {}


def ve_ngam(frame, x, y, tl, R=180, mau_=C.VANG, toi=0.45, alpha=1.0):
    """vùng ngắm: ngoài vòng tròn tối dần, vòng nét đứt xoay co về bán kính R"""
    if tl < 0 or alpha <= 0.003:
        return
    a = smooth(clamp(tl / 0.45)) * alpha
    k = (int(x) // 3, int(y) // 3, int(R))
    f = _mask.get(k)
    if f is None:
        yy, xx = np.ogrid[:H, :W]
        d = np.sqrt((xx - x) ** 2 + (yy - y) ** 2)
        f = np.clip((d - R * 1.05) / 70.0, 0, 1).astype(np.float32)
        if len(_mask) > 6:
            _mask.clear()
        _mask[k] = f
    g = (1 - toi * a * f)[..., None]
    frame[:] = (frame.astype(np.float32) * g).astype(np.uint8)
    r = int(R * (1.3 - 0.3 * smooth(clamp(tl / 0.45))))
    P = r + 10
    lay = np.zeros((2 * P, 2 * P, 4), np.uint8)
    goc = tl * 30.0
    for i in range(16):
        g0 = goc + i * 22.5
        cv2.ellipse(lay, (P, P), (r, r), 0, g0, g0 + 13, (0, 0, 0, 170), 8, cv2.LINE_AA)
        cv2.ellipse(lay, (P, P), (r, r), 0, g0, g0 + 13, tuple(int(v) for v in mau_) + (255,), 4, cv2.LINE_AA)
    C.dan(frame, lay, x - P, y - P, a)


def ve_dong_chay(frame, P, tl, toc=90.0, dash=22.0, gap=60.0, mau_=C.TRANG, day=3, alpha=1.0):
    """vạch đứt chạy dọc polyline màn hình P theo chiều điểm (hướng dòng chảy)"""
    if alpha <= 0.003 or tl < 0:
        return
    P = np.asarray(P, dtype=np.float64)
    if len(P) < 2:
        return
    seg = np.linalg.norm(np.diff(P, axis=0), axis=1)
    cum = np.concatenate([[0.0], np.cumsum(seg)])
    L = cum[-1]
    if L < dash * 1.5:
        return
    s = np.arange(0.0, L, 3.0)
    xs, ys = np.interp(s, cum, P[:, 0]), np.interp(s, cum, P[:, 1])
    on = ((s - toc * tl) % gap) < dash
    on &= (xs > -40) & (xs < W + 40) & (ys > -40) & (ys < H + 40)
    edge = np.flatnonzero(np.diff(np.concatenate([[0], on.astype(np.int8), [0]])))
    lines = [np.stack([xs[a:b], ys[a:b]], 1).round().astype(np.int32).reshape(-1, 1, 2)
             for a, b in edge.reshape(-1, 2) if b - a >= 2]
    if not lines:
        return
    col = tuple(int(v) for v in mau_)
    if alpha >= 0.99:
        cv2.polylines(frame, lines, False, col, day, cv2.LINE_AA)
        return
    tmp = frame.copy()
    cv2.polylines(tmp, lines, False, col, day, cv2.LINE_AA)
    cv2.addWeighted(frame, 1 - alpha, tmp, alpha, 0, dst=frame)


def ve_vien_chay(frame, ring_px, u, mau_, day=4):
    """viền vùng tự vẽ quanh ranh theo tiến độ u (0→1), đầu vạch có chấm trắng"""
    P = np.asarray(ring_px, dtype=np.float64)
    if len(P) < 3 or u <= 0:
        return
    P = np.vstack([P, P[:1]])
    part, head = B.doan_theo_tien_do(P, u)
    if len(part) < 2:
        return
    q = np.round(part).astype(np.int32).reshape(-1, 1, 2)
    cv2.polylines(frame, [q], False, VIEN_TOI, day + 4, cv2.LINE_AA)
    cv2.polylines(frame, [q], False, tuple(int(v) for v in mau_), day, cv2.LINE_AA)
    if u < 0.999 and head is not None:
        B.ve_cham(frame, head[0], head[1], 7, C.TRANG)


def ve_ten_tuyen(frame, P, ten, mau_, chiem, tl, neo=(W * 0.5, H * 0.60), alpha=1.0):
    """tên tuyến (sông/đường) gắn vào tuyến: điểm tuyến gần `neo` → dây ngắn → pill chấm màu bên phải (đụng thì bên
    trái). P = polyline màn hình. → hộp chiếm chỗ | None"""
    if tl < 0 or alpha <= 0.003 or not ten:
        return None
    P = np.asarray(P, dtype=np.float64)
    if len(P) < 2:
        return None
    i = int(np.argmin(((P - np.array(neo)) ** 2).sum(1)))
    x, y = P[i]
    if not (60 < x < W - 60 and 220 < y < 1340):
        return None
    im, arr, w, h = pill_cham(ten, mau_, 26)
    a = clamp(tl / 0.3) * alpha
    for sx in (1, -1):
        cx = x + sx * (48 + w / 2)
        cy = y - 54
        r = (cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2)
        if r[0] < 16 or r[2] > W - 16 or chiem.trung(r, 6):
            continue
        if a >= 0.99:
            ex = cx - sx * w / 2
            cv2.line(frame, (int(x), int(y)), (int(ex), int(cy)), VIEN_TOI, 5, cv2.LINE_AA)
            cv2.line(frame, (int(x), int(y)), (int(ex), int(cy)), tuple(int(v) for v in mau_), 2, cv2.LINE_AA)
        B.ve_cham(frame, x, y, 6, mau_, alpha=a)
        C.dan(frame, arr, cx - arr.shape[1] / 2, cy - arr.shape[0] / 2, a)
        chiem.dat(r)
        return r
    return None


def pill_cham(text, mau_, size=30):
    """pill navy: chấm màu viền trắng + TÊN IN HOA trắng (nhãn vùng / địa danh chính)"""
    k = ("pc", text, tuple(mau_), size)
    if k in _cache:
        return _cache[k]
    t = C.chu(text.upper(), "xbold", size, fill=C.TRANG, track=1)
    dot = int(size * 0.62)
    w, h = 20 + dot + 12 + t.width + 24, t.height + 24
    box = C.hop_bo((w, h), h // 2, tuple(C.NAVY) + (240,), vien=tuple(C.NAVY_VIEN) + (255,), vien_w=2)
    d = ImageDraw.Draw(box)
    cy = h / 2
    d.ellipse((18, cy - dot / 2 - 2, 22 + dot, cy + dot / 2 + 2), fill=(255, 255, 255, 255))
    d.ellipse((20, cy - dot / 2, 20 + dot, cy + dot / 2), fill=tuple(mau_) + (255,))
    box.alpha_composite(t, (20 + dot + 12, (h - t.height) // 2))
    sh, p = C.bong_do(box, blur=10, alpha=0.5)
    out = Image.new("RGBA", (w + 2 * p, h + 2 * p), (0, 0, 0, 0))
    out.alpha_composite(sh, (0, 4))
    out.alpha_composite(box, (p, p))
    _cache[k] = (out, np.asarray(out), w, h)
    return _cache[k]


def ve_pop(frame, sprite, cx, cy, tl, alpha=1.0, dur=0.32):
    """dán sprite (từ pill_cham) ở tâm (cx, cy), bật back-out → hộp chiếm chỗ"""
    if tl < 0 or alpha <= 0.003:
        return None
    im, arr, w, h = sprite
    s = 0.4 + 0.6 * back_out(clamp(tl / dur))
    if abs(s - 1) > 2e-3:
        arr = np.asarray(im.resize((max(1, int(im.width * s)), max(1, int(im.height * s))), Image.BILINEAR))
    C.dan(frame, arr, cx - arr.shape[1] / 2, cy - arr.shape[0] / 2, alpha * clamp(tl / 0.12))
    return (cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2)


# ---------------------------------------------------------------- nhấn mạnh khai trong kế hoạch

class NhanManh:
    """ke_hoach.canh[i].nhan_manh = [{kieu, diem | man_hinh, t, den?, text?, phu?, mau?, ban_kinh?, huong?, co?}]"""

    THU_TU = (("ngam",), ("song", "ghim"), ("nhan", "chu_thich", "huy_hieu"))

    def __init__(self, ds, dl, t0, t1):
        self.ds = []
        for n in ds or []:
            n = dict(n)
            n["_p"] = dl.diem(n["diem"]) if n.get("diem") is not None else None
            n["_t"] = float(n.get("t", t0))
            n["_den"] = float(n["den"]) if n.get("den") is not None else t1 + 5
            if n.get("text") is None and isinstance(n.get("diem"), str) and n.get("kieu") in ("chu_thich", "nhan"):
                n["text"] = dl.ten(n["diem"])
            n["_mau"] = mau(n.get("mau"), 0)
            self.ds.append(n)

    def dang_ngam(self, t):
        """mức tối của vùng ngắm đang chạy (để làm mờ tên địa danh phụ)"""
        a = 0.0
        for n in self.ds:
            if n.get("kieu") == "ngam" and n["_t"] <= t <= n["_den"]:
                a = max(a, smooth(clamp((t - n["_t"]) / 0.45)))
        return a

    def ve(self, frame, t, cam, chiem):
        for lop in self.THU_TU:
            for n in self.ds:
                if n.get("kieu") not in lop:
                    continue
                tl = t - n["_t"]
                if tl < 0 or t > n["_den"]:
                    continue
                a = clamp((n["_den"] - t) / 0.2)
                if n.get("man_hinh"):
                    x, y = float(n["man_hinh"][0]), float(n["man_hinh"][1])
                elif n["_p"] is not None:
                    x, y = cam.chieu(n["_p"][0], n["_p"][1])
                else:
                    continue
                k = n["kieu"]
                r = None
                if k == "ngam":
                    ve_ngam(frame, x, y, tl, float(n.get("ban_kinh", 180)), n["_mau"], alpha=a)
                elif k == "song":
                    ve_song(frame, x, y, tl, n["_mau"], r1=float(n.get("ban_kinh", 95)), alpha=a,
                            lap=bool(n.get("lap", True)))
                elif k == "ghim":
                    r = ve_ghim_roi(frame, x, y, tl, n["_mau"], float(n.get("co", 1.0)), alpha=a)
                elif k == "chu_thich":
                    r = ve_chu_thich(frame, x, y, tl, n.get("text") or "", n.get("phu"), n["_mau"], n.get("huong"),
                                     alpha=a)
                elif k == "huy_hieu":
                    r = ve_huy_hieu(frame, x, y, tl, n.get("text") or "", mau(n.get("nen"), 0),
                                    mau(n.get("chu", "navy")), alpha=a)
                elif k == "nhan":
                    r = B.nhan_diem(frame, x, y, n.get("text") or "", int(n.get("co", 28)), a * clamp(tl / 0.25),
                                    tren=n.get("tren", True))
                chiem.dat(r)


# ---------------------------------------------------------------- tên địa danh quanh camera (OSM place)

UU_TIEN = {"city": 0, "town": 1, "suburb": 2, "quarter": 3, "village": 4, "neighbourhood": 5, "hamlet": 6}


def loai_theo_zoom(zf):
    if zf >= 14.0:
        return set(UU_TIEN)
    if zf >= 11.5:
        return {"city", "town", "suburb", "village"}
    return {"city", "town"}


class DiaDanh:
    """nhãn tên làng/xã/thị trấn THẬT (OSM place, toạ độ node) quanh camera: chữ thường trắng viền tối + chấm nhỏ,
    hiện/ẩn mờ 0,3 s, không đè chữ khác (Chiem), giữ ổn định nhãn đang hiện, tối đa `toi_da` nhãn, cách nhau ≥ `cach` px"""

    def __init__(self, ds, bo_ten=(), toi_da=6, co=26, cach=170, a_max=0.92):
        bo = {C.ten_khong_dau(x) for x in bo_ten if x}
        gap = {}
        for d in sorted(ds, key=lambda d: UU_TIEN.get(d["loai"], 9)):
            k = C.ten_khong_dau(d["ten"])
            if k not in bo and k not in gap:
                gap[k] = d
        self.ds = list(gap.values())
        self.toi_da, self.co, self.cach, self.a_max = toi_da, co, cach, a_max
        self.sp, self.a, self.t_last = {}, {}, None

    def _sp(self, ten):
        if ten not in self.sp:
            self.sp[ten] = np.asarray(C.chu(ten, "bold", self.co, fill=C.TRANG, stroke=3, stroke_fill=VIEN_TOI,
                                            shadow=(0, 2, 3, 0.75)))
        return self.sp[ten]

    def _vi_tri(self, d, x, y):
        sp = self._sp(d["ten"])
        w, h = sp.shape[1], sp.shape[0]
        tx = x + 11 if x + 11 + w < W - 24 else x - 11 - w
        return sp, (tx, y - h / 2, tx + w, y + h / 2)

    def ve(self, frame, t, cam, chiem, alpha=1.0):
        if not self.ds:
            return
        dau = self.t_last is None
        dt = 0.0 if dau else t - self.t_last
        self.t_last = t
        nhay = dau or dt < -1e-6 or dt > 0.25
        hop = loai_theo_zoom(cam.zf)
        cand = []
        for d in self.ds:
            if d["loai"] not in hop:
                continue
            x, y = cam.chieu(d["lat"], d["lon"])
            if not (40 < x < W - 40 and 200 < y < 1372):
                continue
            cand.append((0 if self.a.get(d["id"], 0) > 0.4 else 1, UU_TIEN.get(d["loai"], 9), d, x, y))
        cand.sort(key=lambda c: (c[0], c[1]))
        hien, vt, dat = set(), {}, []
        for _, _, d, x, y in cand:
            sp, r = self._vi_tri(d, x, y)
            vt[d["id"]] = (sp, r, x, y)
            if len(hien) >= self.toi_da:
                continue
            if r[0] < 16 or r[2] > W - 16 or chiem.trung((r[0] - 14, r[1], r[2], r[3]), 8):
                continue
            if any(abs(x - px) < self.cach and abs(y - py) < 70 for px, py in dat):
                continue
            hien.add(d["id"])
            dat.append((x, y))
            chiem.dat((r[0] - 14, r[1], r[2], r[3]))
        for i in set(self.a) | hien:
            muc = 1.0 if i in hien else 0.0
            v = self.a.get(i, 0.0)
            if nhay:
                self.a[i] = muc
            elif muc > v:
                self.a[i] = clamp(v + dt / 0.3)
            elif muc < v:
                self.a[i] = clamp(v - dt / 0.3)
        for i, v in list(self.a.items()):
            if v <= 0.003 or i not in vt:
                continue
            sp, r, x, y = vt[i]
            a = v * self.a_max * alpha
            B.ve_cham(frame, x, y, 5, alpha=a)
            C.dan(frame, sp, r[0], r[1], a)


# ---------------------------------------------------------------- bản đồ định vị nhỏ (góc dưới trái)

class DinhVi:
    """khung nhỏ bo góc viền trắng: cả tuyến (vệ tinh tối + tim tuyến xanh lơ) + chấm vàng gợn sóng = chỗ camera đang
    đứng; tab tên tuyến vàng trên mép. Mặc định x 34, y 1052, 262x292 (nằm trên dải sub)."""

    def __init__(self, tuyen, ten, x=34, y=1052, w=262, h=292):
        self.tuyen = np.asarray(tuyen, dtype=np.float64)
        la0, lo0 = self.tuyen.min(0)
        la1, lo1 = self.tuyen.max(0)
        self.cam = B.Camera.vua_bbox([la0, lo0, la1, lo1], le=0.05)
        self.x, self.y, self.w, self.h, self.ten = x, y, w, h, ten
        self.card = None

    def o_can(self, nen):
        return self.cam.o_can(nen)

    def rect(self):
        return (self.x - 8, self.y - 28, self.x + self.w + 10, self.y + self.h + 10)

    def _dung(self, nen):
        fr = B.lam_toi(self.cam.render(nen), 0.78, 0.85)
        P = self.cam.chieu_mang(self.tuyen)
        (x0, y0), (x1, y1) = P.min(0), P.max(0)
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        hc = max(y1 - y0, (x1 - x0) * self.h / self.w) * 1.18
        wc = hc * self.w / self.h
        s = self.w / wc
        self.ox, self.oy, self.s = cx - wc / 2, cy - hc / 2, s
        M = np.float32([[s, 0, -self.ox * s], [0, s, -self.oy * s]])
        im = cv2.warpAffine(fr, M, (self.w, self.h), flags=cv2.INTER_AREA, borderMode=cv2.BORDER_CONSTANT,
                            borderValue=B.MAU_TRONG)
        Q = np.round((P - [self.ox, self.oy]) * s).astype(np.int32).reshape(-1, 1, 2)
        cv2.polylines(im, [Q], False, (10, 30, 50), 7, cv2.LINE_AA)
        cv2.polylines(im, [Q], False, C.XANH_LO, 3, cv2.LINE_AA)
        bw, R = 4, 18
        mp = Image.fromarray(im).convert("RGBA")
        mp.putalpha(C.mat_na_bo(self.w, self.h, R - 3))
        khung = C.hop_bo((self.w + 2 * bw, self.h + 2 * bw), R, (255, 255, 255, 255))
        khung.alpha_composite(mp, (bw, bw))
        sh, p = C.bong_do(khung, blur=12, alpha=0.55)
        tab = Image.fromarray(B.nhan_pill(self.ten.upper(), "xbold", 21, C.VANG, C.NAVY))
        top = max(p, tab.height // 2 + 2)
        out = Image.new("RGBA", (khung.width + 2 * p, khung.height + p + top), (0, 0, 0, 0))
        out.alpha_composite(sh, (0, top - p + 6))
        out.alpha_composite(khung, (p, top))
        out.alpha_composite(tab, (p + 6, top - tab.height // 2 - 4))
        self.card = np.asarray(out)
        self.cx0, self.cy0 = p + bw, top + bw

    def ve(self, frame, nen, tl, lat, lon, alpha=1.0):
        if tl < 0:
            return
        if self.card is None:
            self._dung(nen)
        a = smooth(clamp(tl / 0.35)) * alpha
        if a <= 0.003:
            return
        dy = 18 * (1 - a)
        C.dan(frame, self.card, self.x - self.cx0, self.y - self.cy0 + dy, a)
        px, py = self.cam.chieu(lat, lon)
        ix = self.x + (px - self.ox) * self.s
        iy = self.y + (py - self.oy) * self.s + dy
        ve_song(frame, ix, iy, tl, C.VANG, r0=6, r1=30, chu_ky=1.3, day=3, alpha=a)
        B.ve_cham(frame, ix, iy, 7, C.VANG, alpha=a)
