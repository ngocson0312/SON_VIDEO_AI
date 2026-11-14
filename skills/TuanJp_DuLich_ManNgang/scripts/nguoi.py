# -*- coding: utf-8 -*-
"""nguoi.py — TÁCH NGƯỜI (u2net_human_seg qua onnxruntime, không cần rembg) cho cú ĐẨY hai nửa trong montage:
người trong cảnh mới nhô ra khỏi mép chia như đang đẩy (khách vòng 4 14/11/2026: "chỉ có hình ảnh đẩy, không có text đẩy hay
nhân vật gì đó đẩy… kiểu đẩy từ phải qua trái"). Không có model / không thấy người → None (cú đẩy chỉ còn chữ + vạch sáng).
Model: ~/.u2net/u2net_human_seg.onnx (máy mới: run.py cai-dat hoặc copy từ máy khác) hoặc assets/models/."""
import os
from pathlib import Path

import numpy as np

from chung import ASSETS, SKILL, bam, loi

_SESS = None
_THU = False


def _tim_model():
    for p in (ASSETS / 'models' / 'u2net_human_seg.onnx', Path.home() / '.u2net' / 'u2net_human_seg.onnx',
              SKILL.parent / 'bds-sale-viral' / 'assets' / 'models' / 'u2net_human_seg.onnx'):
        if p.exists():
            return str(p)
    return None


def _sess(bao=loi):
    global _SESS, _THU
    if _THU:
        return _SESS
    _THU = True
    p = _tim_model()
    if not p:
        bao('  ⚠ không có model u2net_human_seg.onnx (~/.u2net) → cú đẩy hai nửa bỏ phần người nhô ra, còn chữ + vạch sáng')
        return None
    try:
        import onnxruntime as ort
        _SESS = ort.InferenceSession(p, providers=['CPUExecutionProvider'])
    except Exception as e:
        bao(f'  ⚠ không nạp được model tách người: {e}')
        _SESS = None
    return _SESS


def _chay(s, img):
    import cv2
    x = cv2.resize(img, (320, 320), interpolation=cv2.INTER_AREA)[..., ::-1].astype(np.float32) / 255.0
    x = (x - np.array([0.485, 0.456, 0.406], np.float32)) / np.array([0.229, 0.224, 0.225], np.float32)
    out = s.run(None, {s.get_inputs()[0].name: x.transpose(2, 0, 1)[None]})[0][0, 0]
    return (out - out.min()) / (out.max() - out.min() + 1e-6)


def _loc_dan(I, p, r, eps):
    """lọc dẫn hướng (He 2010): mép mặt nạ bám mép ảnh (tóc, ngón tay) — không quầng nền."""
    import cv2
    k = (2 * r + 1, 2 * r + 1)
    mI = cv2.boxFilter(I, -1, k); mp = cv2.boxFilter(p, -1, k)
    a = (cv2.boxFilter(I * p, -1, k) - mI * mp) / (cv2.boxFilter(I * I, -1, k) - mI * mI + eps)
    b = mp - a * mI
    return cv2.boxFilter(a, -1, k) * I + cv2.boxFilter(b, -1, k)


def mat_na(img, bao=loi):
    """img BGR uint8 → mặt nạ float32 0..1 (khối người LỚN NHẤT), hoặc None khi không có model.
    2 lượt: cả khung (tìm người) → cắt sát quanh người chạy lại (nét gấp ~2) → lọc dẫn hướng."""
    import cv2
    s = _sess(bao)
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
    g = cv2.cvtColor(img[y0:y1, x0:x1], cv2.COLOR_BGR2GRAY).astype(np.float32) / 255.0
    r = max(3, int(0.004 * max(W, H)))
    m[y0:y1, x0:x1] = _loc_dan(g, m[y0:y1, x0:x1].astype(np.float32), r, 2e-3)
    return np.clip((m - 0.25) / 0.5, 0, 1).astype(np.float32)


def cat_nguoi(f, out_dir, bao=loi, dt_min=.02, dt_max=.5):
    """khung ảnh f → PNG người tách nền (CÙNG cỡ khung, nền trong suốt) + hộp người chuẩn hoá.
    → {'png': path, 'hop': [x0, y0, x1, y1] (0–1), 'dt': diện tích / khung} hoặc None (không model / người quá nhỏ / quá to)."""
    import cv2
    f = Path(f)
    out = Path(out_dir) / f'nv_{bam(str(f), f.stat().st_size, int(f.stat().st_mtime), "nv1")}.png'
    img = cv2.imdecode(np.fromfile(str(f), np.uint8), cv2.IMREAD_COLOR)     # imread không đọc được đường dẫn có dấu (Windows)
    if img is None:
        return None
    m = mat_na(img, bao)
    if m is None:
        return None
    dt = float((m > .5).mean())
    if not dt_min <= dt <= dt_max:
        bao(f'  người trong {f.name}: chiếm {100 * dt:.0f}% khung — ngoài {100 * dt_min:.0f}–{100 * dt_max:.0f}% → không nhô người')
        return None
    ys, xs = np.where(m > .5)
    H, W = m.shape
    hop = [round(float(xs.min()) / W, 4), round(float(ys.min()) / H, 4), round(float(xs.max() + 1) / W, 4), round(float(ys.max() + 1) / H, 4)]
    if not out.exists():
        rgba = np.dstack([img, (m * 255).astype(np.uint8)])
        ok, buf = cv2.imencode('.png', rgba)
        buf.tofile(str(out))
    return {'png': str(out), 'hop': hop, 'dt': round(dt, 4)}
