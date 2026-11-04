# -*- coding: utf-8 -*-
"""Tự kiểm trên FILE CUỐI: khổ / fps / độ dài / LUFS / đỉnh, rồi rút khung từ chính file mp4:
    soat_canh.jpg   — 1 khung giữa mỗi cảnh (+ mỗi đoạn của bản đồ tổng): soi bản đồ đúng chỗ, nhãn, thẻ, không đè sub
    soat_sub_N.jpg  — dải sub ở giữa MỖI cụm karaoke: soi chính tả, chữ vàng đúng chữ đang đọc
    soat_sub.txt    — chữ từng cụm sub để đọc lại

    python -I scripts/kiem.py --work <dir> [--video <mp4>]
"""
import argparse
import os
import subprocess
import sys

import numpy as np
from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import am_thanh as A
import chung as C
from chung import W, H, FPS


def rut_khung(video, giay):
    """1 lượt ffmpeg, chọn đúng các khung theo chỉ số → list ảnh RGB (theo thứ tự giay đã sắp)"""
    idx = sorted(set(max(0, int(round(t * FPS))) for t in giay))
    if not idx:
        return {}
    expr = "+".join("eq(n\\,%d)" % i for i in idx)
    r = subprocess.run([C.ffbin("ffmpeg"), "-v", "error", "-i", video, "-an", "-vf", "select='%s'" % expr, "-fps_mode", "passthrough",
                        "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True)
    n = len(r.stdout) // (W * H * 3)
    arr = np.frombuffer(r.stdout[:n * W * H * 3], np.uint8).reshape(n, H, W, 3)
    return {i: arr[k] for k, i in enumerate(idx[:n])}


def nhan(im, text, size=26):
    d = ImageDraw.Draw(im)
    f = C.font("bold", size)
    d.rectangle((0, 0, im.width, size + 14), fill=(0, 0, 0))
    d.text((8, 5), text, font=f, fill=(255, 230, 120))
    return im


def to_luoi(imgs, cot, out):
    if not imgs:
        return
    w, h = imgs[0].size
    hang = (len(imgs) + cot - 1) // cot
    sheet = Image.new("RGB", (cot * w + (cot + 1) * 6, hang * h + (hang + 1) * 6), (30, 30, 30))
    for i, im in enumerate(imgs):
        sheet.paste(im, (6 + (i % cot) * (w + 6), 6 + (i // cot) * (h + 6)))
    sheet.save(out, quality=88)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--work", required=True)
    ap.add_argument("--video")
    a = ap.parse_args()
    work = os.path.abspath(a.work)
    bc = C.jload(os.path.join(work, "dung_bao_cao.json"))
    video = os.path.abspath(a.video) if a.video else bc["ra"]
    if not os.path.isfile(video):
        C.die("không thấy video: %s" % video)
    loi = []
    info = C.probe(video)
    print("▶ %s" % video)
    print("   %dx%d · %.3f fps · %.2f s · tiếng: %s" % (info["w"], info["h"], info["fps"], info["duration"], info["audio"]))
    if (info["w"], info["h"]) != (W, H):
        loi.append("khổ %dx%d ≠ %dx%d" % (info["w"], info["h"], W, H))
    if abs(info["fps"] - FPS) > 0.01:
        loi.append("fps %.3f ≠ %d" % (info["fps"], FPS))
    if abs(info["duration"] - bc["giay"]) > 0.15:
        loi.append("độ dài %.2f ≠ dự kiến %.2f" % (info["duration"], bc["giay"]))
    if info["duration"] < bc["giong"] + 0.5:
        loi.append("video kết thúc sát tiếng cuối (%.2f / giọng %.2f)" % (info["duration"], bc["giong"]))
    if not info["audio"]:
        loi.append("không có tiếng")
    lufs, tp = A.do_lufs(video)
    print("   độ to %.1f LUFS · đỉnh %.1f dBFS" % (lufs if lufs is not None else 0, tp if tp is not None else 0))
    if lufs is None or abs(lufs + 14) > 0.7:
        loi.append("độ to %s LUFS (chuẩn −14 ± 0,7)" % lufs)
    if tp is not None and tp > -0.5:
        loi.append("đỉnh %.1f dBFS quá sát 0" % tp)
    if bc.get("o_thieu"):
        print("⚠ %d ô ảnh vệ tinh thiếu (đã phóng ô mức dưới thay): %s" % (len(bc["o_thieu"]), bc["o_thieu"][:5]))

    # khung soát cảnh
    moc = []
    plan = C.jload(os.path.join(work, "ke_hoach.json"))
    for c in bc["canh"]:
        moc.append((min(c["t1"] - 0.15, c["t0"] + max(0.6, (c["t1"] - c["t0"]) / 2)), "%s %.1f–%.1f" % (c["loai"], c["t0"], c["t1"])))
    for it in plan.get("canh", []):
        for d in it.get("doan", []) or []:
            moc.append((float(d["t"]) + float(d.get("dai_ve", 2.0)) + 0.4, "đoạn %s" % (d.get("nhan") or "")[:28]))
    for th in bc.get("the_tai_lieu", []):
        moc.append(((th["t0"] + th["t1"]) / 2, "thẻ tài liệu"))
    moc.sort()
    subs = bc.get("sub_cum", [])
    sub_moc = [((s0 + min(s1, s0 + 1.2)) / 2 + 0.15, txt) for s0, s1, txt in subs]
    kh = rut_khung(video, [t for t, _ in moc] + [t for t, _ in sub_moc])

    thumbs = []
    for t, ten in moc:
        f = kh.get(max(0, int(round(t * FPS))))
        if f is None:
            continue
        im = Image.new("RGB", (360, 640 + 30), (0, 0, 0))
        im.paste(Image.fromarray(f).resize((360, 640), Image.LANCZOS), (0, 30))
        thumbs.append(nhan(im, "%.2f s · %s" % (t, ten), 17))
    to_luoi(thumbs, 4, os.path.join(work, "soat_canh.jpg"))

    strips = []
    for t, txt in sub_moc:
        f = kh.get(max(0, int(round(t * FPS))))
        if f is None:
            continue
        cy = int(plan.get("cai_dat", {}).get("sub_y", 1545))
        im = Image.fromarray(f[max(0, cy - 190):min(H, cy + 40)]).resize((540, 115), Image.LANCZOS)
        strips.append(nhan(im, "%.2f s" % t, 16))
    n_sheet = 0
    for k in range(0, len(strips), 24):
        n_sheet += 1
        to_luoi(strips[k:k + 24], 2, os.path.join(work, "soat_sub_%d.jpg" % n_sheet))
    C.ghi_text(os.path.join(work, "soat_sub.txt"),
               "\n".join("%6.2f–%6.2f  %s" % (s0, s1, txt) for s0, s1, txt in subs) + "\n")

    print("▶ soat_canh.jpg (%d khung) · soat_sub_1..%d.jpg (%d cụm) · soat_sub.txt" % (len(thumbs), n_sheet, len(strips)))
    if loi:
        for x in loi:
            print("⛔ " + x)
        sys.exit(1)
    print("✅ số đo đạt — giờ Claude MỞ soat_canh.jpg + soat_sub_*.jpg soi bằng mắt (bản đồ đúng chỗ, nhãn, chính tả, không đè)")


if __name__ == "__main__":
    main()
