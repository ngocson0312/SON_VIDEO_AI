# -*- coding: utf-8 -*-
"""Tách NGƯỜI NÓI khỏi nền để TIÊU ĐỀ + LOGO nằm SAU người (đặc trưng video mẫu: đầu người che chữ).

u2net_human_seg (onnxruntime, ~0,3 s/khung CPU) chạy trên ô vuông 1080x1080 quanh mặt, mỗi `NGUOI['buoc']` khung,
chỉ giữ thành phần chứa mặt. Kết quả lưu `<work>/nguoi_mask.npy` (N x 320 x 320 uint8) + `nguoi_mask.json`
(ya từng khung) ⇒ dựng lại không phải tính lại. Không có model → tiêu đề nằm trên người (kiem báo LỖI)."""
import os, json, time, subprocess
import numpy as np
import cv2
import chung as C

_S = {'sess': None, 'thu': False}
M = 320


def tim_model():
    return next((p for p in C.NGUOI['model_tim'] if os.path.isfile(p)), None)


def _phien():
    if _S['sess'] is None and not _S['thu']:
        _S['thu'] = True
        p = tim_model()
        if p:
            import onnxruntime as ort
            so = ort.SessionOptions(); so.intra_op_num_threads = max(2, (os.cpu_count() or 4))
            _S['sess'] = ort.InferenceSession(p, sess_options=so, providers=['CPUExecutionProvider'])
    return _S['sess']


def san_sang():
    return _phien() is not None


def _ya(mat):
    cy = (mat[1] + mat[3]) / 2.0 if mat else C.H * 0.35
    return int(min(max(0, cy - 0.30 * C.W), C.H - C.W))


def _chay(frame_rgb, mat):
    """→ (mặt nạ 320x320 uint8, ya)"""
    sess = _phien()
    ya = _ya(mat)
    x = cv2.resize(frame_rgb[ya:ya + C.W], (M, M), interpolation=cv2.INTER_AREA).astype(np.float32) / 255.0
    x = (x - np.array([0.485, 0.456, 0.406], np.float32)) / np.array([0.229, 0.224, 0.225], np.float32)
    out = sess.run(None, {sess.get_inputs()[0].name: x.transpose(2, 0, 1)[None]})[0][0, 0]
    out = (out - out.min()) / max(1e-6, float(out.max() - out.min()))
    lo, hi = C.NGUOI['nguong']
    m = np.clip((out - lo) / (hi - lo), 0, 1)
    n, lab, st, _ = cv2.connectedComponentsWithStats((m > 0.5).astype(np.uint8), connectivity=8)
    if n <= 1:
        return np.zeros((M, M), np.uint8), ya
    keep = None
    if mat:
        fx = int((mat[0] + mat[2]) / 2 * M / C.W); fy = int(((mat[1] + mat[3]) / 2 - ya) * M / C.W)
        if 0 <= fx < M and 0 <= fy < M and lab[fy, fx] > 0: keep = lab == lab[fy, fx]
    if keep is None:
        keep = lab == (1 + int(np.argmax(st[1:, cv2.CC_STAT_AREA])))
    keep = cv2.dilate(keep.astype(np.uint8), np.ones((3, 3), np.uint8)).astype(np.float32)
    return (m * keep * 255).astype(np.uint8), ya


def mat_theo_khung(work, n):
    """mặt (x0,y0,x1,y1) cho từng khung nguồn — nội suy từ mat.json (mỗi 0,2 s)."""
    ds = C.doc_json(os.path.join(work, 'mat.json'))
    ts = np.array([d['t'] for d in ds]); ok = [d['mat'] is not None for d in ds]
    out = []
    for i in range(n):
        t = i / C.FPS
        j = int(np.argmin(np.abs(ts - t)))
        if ok[j]: out.append(ds[j]['mat']); continue
        # mặt gần nhất có
        cand = [k for k in range(len(ds)) if ok[k]]
        out.append(ds[min(cand, key=lambda k: abs(ts[k] - t))]['mat'] if cand else None)
    return out


def mat_that_theo_khung(work, n):
    """True ở khung có mặt THẬT (mẫu gần nhất ≤ 0,3 s không phải 'doan') — chỉ những khung này mới tính vùng mặt cấm chữ
    (mặt đoán = chép từ mẫu khác, sai chỗ)."""
    ds = C.doc_json(os.path.join(work, 'mat.json'))
    ts = np.array([d['t'] for d in ds]); ok = np.array([bool(d.get('mat')) and not d.get('doan') for d in ds])
    t = np.arange(n) / C.FPS
    j = np.clip(np.searchsorted(ts, t), 1, len(ts) - 1)
    j = np.where(np.abs(ts[j - 1] - t) <= np.abs(ts[j] - t), j - 1, j)
    return list(ok[j] & (np.abs(ts[j] - t) <= 0.3))


def tinh_het(work, bao=True):
    """tính mặt nạ cho cả video (mỗi `buoc` khung) → nguoi_mask.npy. Bỏ qua nếu đã có và khớp."""
    if not san_sang():
        print('  ⚠ không có model u2net_human_seg.onnx → tiêu đề sẽ nằm TRÊN người (xem SKILL.md mục Cài đặt)')
        return False
    src = os.path.join(work, 'nguon.mp4')
    pr = C.probe(src); n = int(round(pr['dur'] * C.FPS))
    buoc = C.NGUOI['buoc']
    js_p, np_p = os.path.join(work, 'nguoi_mask.json'), os.path.join(work, 'nguoi_mask.npy')
    # mặt nạ cắt ô vuông QUANH MẶT + giữ thành phần chứa mặt ⇒ mat.json đổi (Haar → MediaPipe) thì phải tính lại
    import hashlib
    ky = hashlib.md5(open(os.path.join(work, 'mat.json'), 'rb').read()).hexdigest()[:12]
    if os.path.exists(js_p) and os.path.exists(np_p):
        js = C.doc_json(js_p)
        cu = js.get('mat_ky')
        mat_doi = (cu is not None and cu != ky) or (cu is None and os.path.exists(os.path.join(work, 'mat_haar.json')))
        if js.get('n') == n and js.get('buoc') == buoc and js.get('xong') and not mat_doi:
            return True
        if mat_doi and bao: print('  mặt đã đổi (MediaPipe) → tách người lại theo mặt mới', flush=True)
    mats = mat_theo_khung(work, n)
    k = (n + buoc - 1) // buoc + 1
    arr = np.lib.format.open_memmap(np_p, mode='w+', dtype=np.uint8, shape=(k, M, M))
    yas = [0] * k
    p = subprocess.Popen(['ffmpeg', '-v', 'error', '-i', src, '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], stdout=subprocess.PIPE)
    sz = C.W * C.H * 3; i = 0; t0 = time.time()
    while True:
        buf = p.stdout.read(sz)
        if len(buf) < sz: break
        if i % buoc == 0:
            fr = np.frombuffer(buf, np.uint8).reshape(C.H, C.W, 3)
            m, ya = _chay(fr, mats[min(i, n - 1)])
            arr[i // buoc] = m; yas[i // buoc] = ya
            if bao and (i // buoc) % 60 == 0:
                print(f'  tách người {i}/{n} khung · {time.time() - t0:.0f} s', flush=True)
        i += 1
    p.stdout.close(); p.wait()
    last = (i - 1) // buoc
    for j in range(last + 1, k): arr[j] = arr[last]; yas[j] = yas[last]
    arr.flush(); del arr
    C.ghi_json(js_p, {'n': n, 'buoc': buoc, 'ya': yas, 'xong': True, 'mat_ky': ky})
    print(f'  tách người xong {i} khung trong {time.time() - t0:.0f} s')
    return True


class Kho:
    """đọc mặt nạ đã tính; trả mặt nạ float (H, W) ở toạ độ NGUỒN cho khung i (nội suy giữa 2 mốc)."""
    def __init__(self, work):
        self.ok = False
        js_p, np_p = os.path.join(work, 'nguoi_mask.json'), os.path.join(work, 'nguoi_mask.npy')
        if os.path.exists(js_p) and os.path.exists(np_p):
            self.js = C.doc_json(js_p)
            self.arr = np.load(np_p, mmap_mode='r')
            self.ok = bool(self.js.get('xong'))
        self.buoc = C.NGUOI['buoc'] if not self.ok else self.js['buoc']

    def lay(self, i):
        if not self.ok: return None
        j, r = divmod(i, self.buoc)
        j = min(j, len(self.arr) - 1); j2 = min(j + 1, len(self.arr) - 1)
        a = self.arr[j].astype(np.float32)
        if r and j2 != j:
            f = r / self.buoc; a = a * (1 - f) + self.arr[j2].astype(np.float32) * f
        ya = self.js['ya'][j]
        m = cv2.resize(a / 255.0, (C.W, C.W), interpolation=cv2.INTER_CUBIC)
        m = cv2.GaussianBlur(np.clip(m, 0, 1), (0, 0), C.NGUOI['mem'])
        full = np.zeros((C.H, C.W), np.float32)
        full[ya:ya + C.W] = m
        return full


def mot_khung(frame_rgb, mat):
    """dùng cho xem trước (không cache)."""
    if not san_sang(): return None
    m, ya = _chay(frame_rgb, mat)
    mm = cv2.resize(m.astype(np.float32) / 255.0, (C.W, C.W), interpolation=cv2.INTER_CUBIC)
    mm = cv2.GaussianBlur(np.clip(mm, 0, 1), (0, 0), C.NGUOI['mem'])
    full = np.zeros((C.H, C.W), np.float32); full[ya:ya + C.W] = mm
    return full
