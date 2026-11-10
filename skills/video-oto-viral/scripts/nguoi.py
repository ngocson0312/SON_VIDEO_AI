# -*- coding: utf-8 -*-
"""Tách người (u2net_human_seg qua onnxruntime) cho: người nổi ra khỏi khung điện ảnh, người đứng trước mảnh vỡ.
Không có model → trả None (hiệu ứng tự bỏ phần 'người nổi')."""
import os
import numpy as np, cv2
import chung as C

_SESS = None
_TRIED = False


def _tim_model():
    ung = [os.path.join(C.ASSETS, 'models', 'u2net_human_seg.onnx'),
           os.path.join(os.path.expanduser('~'), '.u2net', 'u2net_human_seg.onnx'),
           os.path.join(C.SKILL, '..', 'skill-bando-tintuc-chinhtri', 'cache', 'models', 'u2net.onnx')]
    for p in ung:
        if os.path.exists(p):
            return os.path.abspath(p)
    return None


def _sess():
    global _SESS, _TRIED
    if _TRIED:
        return _SESS
    _TRIED = True
    p = _tim_model()
    if not p:
        C.in_ra('  ⚠ không có model u2net_human_seg.onnx → bỏ hiệu ứng người nổi ra khỏi khung')
        return None
    try:
        import onnxruntime as ort
        _SESS = ort.InferenceSession(p, providers=['CPUExecutionProvider'])
    except Exception as e:
        C.in_ra(f'  ⚠ không nạp được model tách người: {e}')
        _SESS = None
    return _SESS


def co_model():
    return _sess() is not None


def _chay(s, img):
    x = cv2.resize(img, (320, 320), interpolation=cv2.INTER_AREA)[..., ::-1].astype(np.float32) / 255.0
    x = (x - np.array([0.485, 0.456, 0.406], np.float32)) / np.array([0.229, 0.224, 0.225], np.float32)
    out = s.run(None, {s.get_inputs()[0].name: x.transpose(2, 0, 1)[None]})[0][0, 0]
    return (out - out.min()) / (out.max() - out.min() + 1e-6)


def loc_dan(I, p, r, eps):
    """Lọc dẫn hướng (guided filter, He 2010): mép mặt nạ p bám mép ảnh I (xám 0..1) — hết viền sáng/quầng."""
    k = (2 * r + 1, 2 * r + 1)
    mI = cv2.boxFilter(I, -1, k); mp = cv2.boxFilter(p, -1, k)
    a = (cv2.boxFilter(I * p, -1, k) - mI * mp) / (cv2.boxFilter(I * I, -1, k) - mI * mI + eps)
    b = mp - a * mI
    return cv2.boxFilter(a, -1, k) * I + cv2.boxFilter(b, -1, k)


def mat_na(img):
    """img BGR uint8 → mặt nạ float32 0..1 cùng kích thước, hoặc None.
    2 lượt: cả khung (tìm người) → cắt sát quanh người chạy lại (nét gấp ~2) → lọc dẫn hướng theo ảnh gốc
    (mép bám tóc / ngón tay, không quầng nền — bản 2 VF7 bị viền trắng quanh người nổi ra dải đen)."""
    s = _sess()
    if s is None:
        return None
    H, W = img.shape[:2]
    m = cv2.resize(_chay(s, img), (W, H), interpolation=cv2.INTER_LINEAR)
    b = (m > 0.5).astype(np.uint8)
    n, lab, st, _ = cv2.connectedComponentsWithStats(b)
    if n < 2:
        return np.zeros((H, W), np.float32)
    k = 1 + int(np.argmax(st[1:, cv2.CC_STAT_AREA]))
    x0, y0, w, h = st[k, 0], st[k, 1], st[k, 2], st[k, 3]
    px, py = int(0.12 * w) + 8, int(0.08 * h) + 8
    x0, y0, x1, y1 = max(0, x0 - px), max(0, y0 - py), min(W, x0 + w + px), min(H, y0 + h + py)
    m2 = np.zeros((H, W), np.float32)
    m2[y0:y1, x0:x1] = cv2.resize(_chay(s, img[y0:y1, x0:x1]), (x1 - x0, y1 - y0), interpolation=cv2.INTER_LINEAR)
    m = np.clip((m2 - 0.35) / 0.35, 0, 1)
    b = (m > 0.5).astype(np.uint8)
    n, lab, st, _ = cv2.connectedComponentsWithStats(b)
    if n > 2:
        k = 1 + int(np.argmax(st[1:, cv2.CC_STAT_AREA]))
        m = m * cv2.dilate((lab == k).astype(np.uint8), np.ones((15, 15), np.uint8))
    # lọc dẫn hướng trong hộp người (nhanh), rồi siết: mép nhoè còn ~1 px
    g = cv2.cvtColor(img[y0:y1, x0:x1], cv2.COLOR_BGR2GRAY).astype(np.float32) / 255.0
    r = max(3, int(0.004 * max(W, H)))
    m[y0:y1, x0:x1] = loc_dan(g, m[y0:y1, x0:x1].astype(np.float32), r, 2e-3)
    return np.clip((m - 0.25) / 0.5, 0, 1).astype(np.float32)
