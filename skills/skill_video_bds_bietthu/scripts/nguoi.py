# -*- coding: utf-8 -*-
"""Tách NGƯỜI NÓI khỏi khung để chữ chạm đầu / vai nằm DƯỚI lớp người (05/11 user: "chữ nếu vào đầu người thì nên ở dưới
lớp layer đầu người"). Chạy u2net_human_seg bằng onnxruntime (không cần rembg), chỉ cắt vùng quanh mặt, chỉ giữ thành phần
chứa khuôn mặt. Không có model -> san_sang() False, chữ nằm trên như cũ (kiem-plan / tự kiểm báo)."""
import os
import numpy as np
import cv2
import chung as C

_S = {'sess': None, 'thu': False}


def tim_model():
    return next((p for p in C.NGUOI['model_tim'] if os.path.isfile(p)), None)


def _phien():
    if _S['sess'] is None and not _S['thu']:
        _S['thu'] = True
        p = tim_model()
        if p:
            try:
                import onnxruntime as ort
                so = ort.SessionOptions(); so.intra_op_num_threads = 4
                _S['sess'] = ort.InferenceSession(p, sess_options=so, providers=['CPUExecutionProvider'])
            except Exception as e:           # noqa
                print('  (không nạp được model tách người:', e, ')')
    return _S['sess']


def san_sang():
    return _phien() is not None


def mask(frame_bgr, mat):
    """mat = [x0, y0, x1, y1] khuôn mặt (px khung 1080x1920). Trả float32 (H, W) 0..1 hoặc None."""
    sess = _phien()
    if sess is None or not mat:
        return None
    H, W = frame_bgr.shape[:2]
    cx, cy = (mat[0] + mat[2]) / 2.0, (mat[1] + mat[3]) / 2.0
    S = W                                                   # cắt vùng vuông rộng bằng khung, quanh mặt
    ya = int(min(max(0, cy - C.NGUOI['len'] * S), H - S)); yb = ya + S
    x = cv2.cvtColor(cv2.resize(frame_bgr[ya:yb], (320, 320), interpolation=cv2.INTER_AREA), cv2.COLOR_BGR2RGB)
    x = x.astype(np.float32) / 255.0
    x = (x - np.array([0.485, 0.456, 0.406], np.float32)) / np.array([0.229, 0.224, 0.225], np.float32)
    out = sess.run(None, {sess.get_inputs()[0].name: x.transpose(2, 0, 1)[None]})[0][0, 0]
    out = (out - out.min()) / max(1e-6, float(out.max() - out.min()))
    m = cv2.resize(out, (S, S), interpolation=cv2.INTER_CUBIC)
    lo, hi = C.NGUOI['nguong']
    m = np.clip((m - lo) / (hi - lo), 0, 1)
    n, lab, st, _ = cv2.connectedComponentsWithStats((m > 0.5).astype(np.uint8), connectivity=8)
    fx, fy = int(cx), int(cy - ya)
    if 0 <= fy < S and 0 <= fx < S and lab[fy, fx] > 0:
        keep = lab == lab[fy, fx]
    elif n > 1:
        keep = lab == (1 + int(np.argmax(st[1:, cv2.CC_STAT_AREA])))
    else:
        return None
    keep = cv2.dilate(keep.astype(np.uint8), np.ones((C.NGUOI['no'], C.NGUOI['no']), np.uint8)).astype(np.float32)
    m = cv2.GaussianBlur(m * keep, (0, 0), C.NGUOI['mem'])
    full = np.zeros((H, W), np.float32)
    full[ya:yb] = m
    return full


def vung_nguoi(mat):
    """hộp (x0, y0, x1, y1) nơi chữ mà chạm vào thì phải tính lớp người: quanh mặt + thân + khoảng trên đầu."""
    fw, fh = mat[2] - mat[0], mat[3] - mat[1]
    cx = (mat[0] + mat[2]) / 2.0
    return (cx - C.NGUOI['vung_x'] * fw, mat[1] - C.NGUOI['vung_tren'] * fh, cx + C.NGUOI['vung_x'] * fw, C.H)
