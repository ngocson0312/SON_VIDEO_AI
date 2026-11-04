# -*- coding: utf-8 -*-
"""Bước 5: dựng video từ work/kich_ban.json + thuc_the.json + loi_doc.json.
Hình: camera bay liên tục trên bản đồ vệ tinh + động tác; sub karaoke; tiếng: giọng + nhạc + SFX −14 LUFS.
Mã hoá hình 1 lần (khung thô → ffmpeg, burn sub ngay trong lượt mã hoá).

python -I scripts/dung.py --work <work> [--ra <file.mp4>] [--mang] [--nhanh] [--xem-truoc]
"""
import argparse
import os
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import chung as C
import chuan_bi


def duong_ffmpeg(p):
    """Đường dẫn cho filter ffmpeg trên Windows: / và thoát dấu :"""
    return p.replace("\\", "/").replace(":", "\\:")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--work", required=True)
    ap.add_argument("--ra", help="file mp4 đầu ra (mặc định: cạnh audio, <tên>_bando.mp4, không ghi đè)")
    ap.add_argument("--mang", action="store_true", help="cho phép tải ô bản đồ thiếu trong lúc dựng")
    ap.add_argument("--nhanh", action="store_true", help="dựng thử 540x960, crf cao (xem bố cục)")
    ap.add_argument("--xem-truoc", action="store_true", help="chỉ xuất tờ khung 1 s/khung ra work/xem_truoc.jpg, không mã hoá")
    ap.add_argument("--tu", type=float, default=None, help="chỉ dựng từ giây này (thử)")
    ap.add_argument("--den", type=float, default=None, help="…đến giây này (thử)")
    a = ap.parse_args()
    work = os.path.abspath(a.work)
    kb = C.doc_json(os.path.join(work, "kich_ban.json"))
    loi = C.doc_json(os.path.join(work, "loi_doc.json"))
    f_tt = os.path.join(work, "thuc_the.json")
    if not os.path.exists(f_tt):
        C.die("chưa có thuc_the.json — chạy tai_tai_nguyen.py trước")
    thuc_the = C.doc_json(f_tt)
    audio = kb.get("audio") or loi["audio"]
    if not os.path.exists(audio):
        C.die("không thấy audio: " + audio)
    t_end = float(loi["thoi_luong"]) + C.DUOI_SAU_TIENG_CUOI
    kb["thoi_luong"] = t_end
    du = chuan_bi.bao_dam(can_mang=False, u2net=False)
    from engine.render import BoDung
    from engine import sub as SUB
    from engine import am_thanh as AM

    kh = kb.get("khung") or {}
    W, H, fps = int(kh.get("rong", 1080)), int(kh.get("cao", 1920)), int(kh.get("fps", 30))
    if a.nhanh:
        W, H = W // 2, H // 2
    C.buoc("Dựng video %dx%d @%d, %.2f s" % (W, H, fps, t_end))
    bd = BoDung(kb, thuc_the, du, os.path.join(C.CACHE, "tiles"), mang=a.mang, W=W, H=H, fps=fps)
    print("   %d động tác, %d đoạn camera" % (len(bd.dong_tac), len(bd.lo_trinh.doan)))
    for v in bd.lo_trinh.van_de:
        print("⛔ " + v)

    if a.xem_truoc:
        import cv2
        import numpy as np
        khung = []
        t = 0.0
        while t < t_end:
            fr = bd.khung(t)
            fr = cv2.resize(fr, (W // 4, H // 4), interpolation=cv2.INTER_AREA)
            cv2.putText(fr, "%.0fs" % t, (6, 22), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
            khung.append(fr)
            t += 1.0
        cot = 6
        hang = (len(khung) + cot - 1) // cot
        sheet = np.full((hang * (H // 4), cot * (W // 4), 3), 255, np.uint8)
        for i, fr in enumerate(khung):
            y, x = (i // cot) * (H // 4), (i % cot) * (W // 4)
            sheet[y:y + H // 4, x:x + W // 4] = fr
        out = os.path.join(work, "xem_truoc.jpg")
        cv2.imwrite(out, sheet, [cv2.IMWRITE_JPEG_QUALITY, 85])
        C.ok("tờ xem trước: " + out)
        return

    # sub
    ass, cum = SUB.tao_ass(loi["tu"], W, H, toi_da=int((kb.get("sub") or {}).get("toi_da_tu", 3)),
                           font_file=du.get("font_sub"))
    f_ass = os.path.join(work, "sub.ass")
    C.ghi_text(f_ass, ass)
    print("   sub: %d cụm karaoke" % len(cum))

    # tiếng
    nhac = kb.get("nhac")
    if nhac in (None, "auto", "", True):
        nhac = None
        d_nhac = os.path.join(C.ASSETS, "nhac")
        if os.path.isdir(d_nhac):
            fs = [f for f in sorted(os.listdir(d_nhac)) if f.lower().endswith((".mp3", ".wav", ".m4a", ".ogg"))]
            if fs:
                nhac = os.path.join(d_nhac, fs[0])
        # không có nhạc thật trong assets/nhac → KHÔNG nhạc (drone tự sinh có nền ồn xì xào, đã bỏ khỏi mặc định)
    elif nhac in ("khong", "none", False):
        nhac = None
    elif not os.path.exists(nhac):
        C.canh_bao("không thấy nhạc %s → không nhạc" % nhac)
        nhac = None
    cues = bd.sfx_cues()
    f_am = AM.tron(audio, t_end, cues, work, nhac=nhac, sfx_dirs=tuple(C.thu_muc_sfx()) + (du["sfx"],))

    # đầu ra
    ra = a.ra
    if not ra:
        goc = os.path.splitext(os.path.basename(audio))[0]
        goc = goc.replace("_audio", "")
        ra = os.path.join(os.path.dirname(audio), "%s_bando%s.mp4" % (goc, "_thu" if a.nhanh else ""))
    ra = C.ten_ban_moi(os.path.abspath(ra))

    t_tu = a.tu or 0.0
    t_den = a.den or t_end
    n_khung = int(round((t_den - t_tu) * fps))
    fontsdir = duong_ffmpeg(C.FONTS)
    vf = "subtitles=sub.ass:fontsdir='%s'" % fontsdir
    cmd = ["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", "%dx%d" % (W, H),
           "-r", str(fps), "-i", "-", "-ss", "%.3f" % t_tu, "-i", f_am, "-vf", vf,
           "-c:v", "libx264", "-preset", "fast" if a.nhanh else "medium", "-crf", "26" if a.nhanh else "18",
           "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", "-shortest", ra]
    print("   mã hoá → " + ra)
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE, cwd=work, stderr=subprocess.PIPE)
    t0 = time.time()
    moc = max(1, n_khung // 20)
    try:
        for i in range(n_khung):
            t = t_tu + i / fps
            fr = bd.khung(t)
            p.stdin.write(fr.tobytes())
            if i % moc == 0:
                da = time.time() - t0
                con = da / max(1, i) * (n_khung - i) if i else 0
                print("   %3d%%  khung %d/%d  %.0fs đã chạy, còn ~%.0fs" % (100 * i // n_khung, i, n_khung, da, con),
                      flush=True)
        p.stdin.close()
        err = p.stderr.read().decode("utf-8", "replace")
        p.wait()
    except BrokenPipeError:
        err = p.stderr.read().decode("utf-8", "replace")
        p.wait()
    if p.returncode != 0:
        C.die("ffmpeg lỗi:\n" + err[-2000:])
    thieu = len(bd.nen.thieu)
    if thieu:
        C.canh_bao("%d ô bản đồ thiếu (vùng tối/mờ). Chạy lại tai_tai_nguyen.py hoặc dựng với --mang" % thieu)
    loi_dt = [(d.LOAI, d.loi) for d in bd.dong_tac if getattr(d, "loi", None)]
    for l, e in loi_dt:
        C.canh_bao("động tác %s gặp lỗi: %s" % (l, e))
    C.ghi_json(os.path.join(work, "dung_info.json"),
               {"ra": ra, "khung": n_khung, "sfx": len(cues), "cum_sub": len(cum), "thoi_luong": t_end,
                "o_thieu": thieu, "loi_dong_tac": loi_dt, "nhac": nhac})
    C.ok("xong sau %.0f s: %s" % (time.time() - t0, ra))


if __name__ == "__main__":
    main()
