# -*- coding: utf-8 -*-
"""Dò 21 điểm BÀN TAY bằng MediaPipe Hands — chạy trong môi trường Python RIÊNG (~/.bds_sale_viral/venv_tay,
mediapipe 0.10.21 cần numpy<2 / protobuf<5 nên không cài chung với Python chính). tay.py gọi file này qua subprocess.

  <venv>/python tay_mp.py <nguon.mp4> <ra.json> [buoc=2] [rong=540]

Ra JSON: {buoc, n, w, h, khung: [[{x: [21], y: [21], ben: 'Left'|'Right', diem}, …] | [] mỗi `buoc` khung]}
(toạ độ PIXEL của video nguồn). Chỉ dùng cv2 + numpy + mediapipe — không import module khác của skill."""
import sys, json
import cv2
import mediapipe as mp


def main():
    src, out = sys.argv[1], sys.argv[2]
    buoc = int(sys.argv[3]) if len(sys.argv) > 3 else 2
    rong = int(sys.argv[4]) if len(sys.argv) > 4 else 540
    cap = cv2.VideoCapture(src)
    W, H = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    n_uoc = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    cao = int(round(H * rong / W))
    hands = mp.solutions.hands.Hands(static_image_mode=False, max_num_hands=2, model_complexity=1,
                                     min_detection_confidence=0.45, min_tracking_confidence=0.45)
    kh, i = [], 0
    while True:
        ok, f = cap.read()
        if not ok: break
        if i % buoc == 0:
            nho = cv2.cvtColor(cv2.resize(f, (rong, cao), interpolation=cv2.INTER_AREA), cv2.COLOR_BGR2RGB)
            r = hands.process(nho)
            ds = []
            if r.multi_hand_landmarks:
                for lm, hd in zip(r.multi_hand_landmarks, r.multi_handedness or []):
                    c = hd.classification[0]
                    ds.append({'x': [round(p.x * W, 1) for p in lm.landmark], 'y': [round(p.y * H, 1) for p in lm.landmark],
                               'ben': c.label, 'diem': round(float(c.score), 3)})
            kh.append(ds)
            if len(kh) % 150 == 0:
                print(f'  hand {i}/{n_uoc} frames', flush=True)
        i += 1
    json.dump({'buoc': buoc, 'n': i, 'w': W, 'h': H, 'khung': kh}, open(out, 'w', encoding='utf-8'))
    print(f'  done {i} frames, {sum(1 for d in kh if d)} samples with hands', flush=True)


if __name__ == '__main__':
    main()
