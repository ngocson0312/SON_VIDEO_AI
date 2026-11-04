# -*- coding: utf-8 -*-
"""Bước 6: tự kiểm trên FILE CUỐI: thời lượng, khổ, loudness, tờ khung 1 s/khung (Claude phải mở soi),
khung tối (thiếu ô bản đồ), bảng động tác theo giây để đối chiếu lời ↔ hình.

python -I scripts/kiem.py --work <work> [--video <mp4>]
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import chung as C


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--work", required=True)
    ap.add_argument("--video")
    a = ap.parse_args()
    work = os.path.abspath(a.work)
    info = C.doc_json(os.path.join(work, "dung_info.json")) if os.path.exists(os.path.join(work, "dung_info.json")) else {}
    video = a.video or info.get("ra")
    if not video or not os.path.exists(video):
        C.die("không thấy video để kiểm (truyền --video)")
    loi = C.doc_json(os.path.join(work, "loi_doc.json"))
    kb = C.doc_json(os.path.join(work, "kich_ban.json"))
    C.buoc("Tự kiểm " + os.path.basename(video))
    loi_list, canh = [], []
    dai = C.ffprobe_thoi_luong(video)
    mong = float(loi["thoi_luong"]) + C.DUOI_SAU_TIENG_CUOI
    out = C.chay(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height,r_frame_rate",
                  "-of", "default=noprint_wrappers=1:nokey=1", video])
    print("   khổ/fps: " + " ".join(out.split()))
    print("   thời lượng: %.2f s (mong %.2f s)" % (dai, mong))
    if abs(dai - mong) > 0.25:
        loi_list.append("thời lượng lệch %.2f s so với audio + 0,9 s" % (dai - mong))
    I, TP = C.ffmpeg_loudness(video)
    print("   loudness: %s LUFS, true peak %s dBFS" % (I, TP))
    if I is None or abs(I + 14) > 1.0:
        loi_list.append("loudness %s LUFS, lệch quá 1 LU so với −14" % I)
    if TP is not None and TP > -0.5:
        canh.append("true peak %.1f dBFS cao" % TP)
    # tờ khung
    import cv2
    import numpy as np
    cap = cv2.VideoCapture(video)
    fps = cap.get(cv2.CAP_PROP_FPS) or 30
    n = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    W, H = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    khung, toi = [], []
    for s in range(int(dai) + 1):
        cap.set(cv2.CAP_PROP_POS_FRAMES, min(n - 1, int(s * fps)))
        ok, fr = cap.read()
        if not ok:
            break
        if fr.mean() < 18:
            toi.append(s)
        sm = cv2.resize(fr, (W // 4, H // 4), interpolation=cv2.INTER_AREA)
        cv2.putText(sm, "%ds" % s, (6, 24), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
        khung.append(sm)
    cap.release()
    cot = 6
    hang = (len(khung) + cot - 1) // cot
    if khung:
        sheet = np.full((hang * (H // 4), cot * (W // 4), 3), 255, np.uint8)
        for i, fr in enumerate(khung):
            y, x = (i // cot) * (H // 4), (i % cot) * (W // 4)
            sheet[y:y + fr.shape[0], x:x + fr.shape[1]] = fr
        f_sheet = os.path.join(work, "kiem_khung.jpg")
        cv2.imwrite(f_sheet, sheet, [cv2.IMWRITE_JPEG_QUALITY, 85])
        print("   tờ khung: " + f_sheet + "  ← Claude PHẢI mở soi: nước/nhãn đúng chỗ, sub không bị đè, không khung tối")
    if toi:
        loi_list.append("khung gần như tối đen ở giây: %s (thiếu ô bản đồ hoặc camera nhìn ra ngoài)" % toi[:10])
    if info.get("o_thieu"):
        canh.append("%d ô bản đồ thiếu khi dựng" % info["o_thieu"])
    for l, e in info.get("loi_dong_tac", []):
        loi_list.append("động tác %s có lỗi khi vẽ: %s" % (l, e))
    # bảng lời ↔ động tác
    print("\n   giây   lời (câu)                                   động tác bắt đầu trong câu")
    dts = []
    for nh in kb.get("nhip", []):
        for d in nh.get("dong_tac", []) or []:
            dts.append((float(d.get("luc", 0)), d.get("loai"), d.get("tai") or d.get("nuoc") or d.get("tu") or d.get("ten") or d.get("chu") or ""))
    dts.sort()
    for c in loi["cau"]:
        trong = [x for x in dts if c["s"] - 0.3 <= x[0] < c["e"] + 0.3]
        mo_ta = ", ".join("%s(%s)@%.1f" % (l, str(r)[:14], t) for t, l, r in trong) or "—"
        print("   %5.1f  %-44s %s" % (c["s"], c["text"][:44], mo_ta[:70]))
        if not trong and c["e"] - c["s"] > 2.5:
            canh.append("câu ở %.1f s dài %.1f s không có động tác nào" % (c["s"], c["e"] - c["s"]))
    print()
    for s in loi_list:
        print("⛔ " + s)
    for s in canh:
        print("⚠ " + s)
    if loi_list:
        sys.exit(2)
    C.ok("file cuối đạt các mục tự kiểm máy; còn phần soi mắt trên kiem_khung.jpg")


if __name__ == "__main__":
    main()
