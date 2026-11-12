# -*- coding: utf-8 -*-
"""Dò MẶT + ĐẦU người nói bằng MediaPipe (FaceDetection tầm xa + Pose) — chạy trong venv RIÊNG của skill
(~/.bds_sale_viral/venv_tay, cùng chỗ với tay_mp.py). tay.py gọi file này qua subprocess.

  <venv>/python mat_mp.py <nguon.mp4> <ra.json> [buoc=3] [rong=540]

Vì sao: Haar (OpenCV) chỉ bắt mặt NHÌN THẲNG — người nói đi dọc tường, quay nghiêng, quay lưng thì mất mặt hàng chục giây
(ONE ERA 12/11: 63 % mẫu phải đoán) ⇒ chữ xếp theo chỗ mặt sai, đè mặt. Pose luôn ra đầu (mũi, mắt, tai, vai) kể cả
lúc nghiêng / quay lưng; FaceDetection cho hộp mặt chính xác khi thấy mặt.

Ra JSON: {buoc, n, w, h, mau: [{t, fd: [[x0, y0, x1, y1, diem], …], pose: [[x, y, vis] × 13] | null}, …]}
(toạ độ PIXEL video nguồn; pose 13 điểm đầu = mũi, mắt, tai, miệng, 2 vai). Chỉ dùng cv2 + mediapipe."""
import sys, json
import cv2
import mediapipe as mp


def main():
    src, out = sys.argv[1], sys.argv[2]
    buoc = int(sys.argv[3]) if len(sys.argv) > 3 else 3
    rong = int(sys.argv[4]) if len(sys.argv) > 4 else 540
    cap = cv2.VideoCapture(src)
    W, H = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    n_uoc = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    cao = int(round(H * rong / W))
    fd = mp.solutions.face_detection.FaceDetection(model_selection=1, min_detection_confidence=0.5)
    pose = mp.solutions.pose.Pose(static_image_mode=False, model_complexity=1, min_detection_confidence=0.5,
                                  min_tracking_confidence=0.5)
    mau, i = [], 0
    while True:
        ok, f = cap.read()
        if not ok: break
        if i % buoc == 0:
            nho = cv2.cvtColor(cv2.resize(f, (rong, cao), interpolation=cv2.INTER_AREA), cv2.COLOR_BGR2RGB)
            r = fd.process(nho)
            ds = []
            for d in (r.detections or []):
                b = d.location_data.relative_bounding_box
                ds.append([round(b.xmin * W, 1), round(b.ymin * H, 1), round((b.xmin + b.width) * W, 1),
                           round((b.ymin + b.height) * H, 1), round(float(d.score[0]), 3)])
            p = pose.process(nho)
            pts = None
            if p.pose_landmarks:
                pts = [[round(q.x * W, 1), round(q.y * H, 1), round(float(q.visibility), 3)]
                       for q in p.pose_landmarks.landmark[:13]]
            mau.append({'t': round(i / fps, 3), 'fd': ds, 'pose': pts})
            if len(mau) % 300 == 0:
                print(f'  face {i}/{n_uoc} frames', flush=True)
        i += 1
    json.dump({'buoc': buoc, 'n': i, 'w': W, 'h': H, 'mau': mau}, open(out, 'w', encoding='utf-8'))
    print(f'  done {i} frames, {sum(1 for m in mau if m["fd"])} with face, {sum(1 for m in mau if m["pose"])} with pose',
          flush=True)


if __name__ == '__main__':
    main()
