# -*- coding: utf-8 -*-
"""run.py — điểm vào skill TuấnJp_Dulich_ManDoc.

  python -I -X utf8 run.py cai-dat [--tai-mo-hinh]   (máy mới: cài thư viện + kiểm ffmpeg / Node / Chrome / Whisper)
  python -I -X utf8 run.py dong-goi [--out <file.zip>]   (đóng gói skill thành zip gửi khách — giải nén là chạy)
  python -I -X utf8 run.py quet   --audio <giọng> [--link <url bài báo>] [--res <thư mục clip/ảnh>] [--nhac <file>] [--ngon-ngu vi] [--work <dir>]
  python -I -X utf8 run.py kiem-kh --work <dir>
  python -I -X utf8 run.py tim "<tên địa điểm>"   (toạ độ cho hành trình bản đồ thật — cần mạng)
  python -I -X utf8 run.py sub-dich --work <dir> --ngon-ngu ko   (giọng 1 tiếng, CHỮ trên hình tiếng khác: thêm khung sub dịch)
  python -I -X utf8 run.py duyet  --work <dir>            (dựng ảnh duyệt duyet.jpg + bang_duyet.txt)
  python -I -X utf8 run.py dung   --work <dir> [--luong 4] [--out <ra.mp4>] [--xem-truoc]
  python -I -X utf8 run.py tron-lai --work <dir> [--file <video đã dựng>] [--out <ra.mp4>]  (CHỈ đổi tiếng: mức / file nhạc, SFX — giữ hình)
  python -I -X utf8 run.py kiem   --work <dir> [--file <video>]
  python -I -X utf8 run.py khung  --work <dir> --times 1.2,5.0      (chụp khung lẻ để soi)
  python -I -X utf8 run.py don    --work <dir>                      (xoá khung footage đã trích — giải phóng ổ đĩa)
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('lenh')
    ap.add_argument('ten', nargs='?')
    ap.add_argument('--audio')
    ap.add_argument('--link')
    ap.add_argument('--res')
    ap.add_argument('--nhac')
    ap.add_argument('--ngon-ngu', dest='ngon_ngu')
    ap.add_argument('--work')
    ap.add_argument('--luong', type=int, default=4)
    ap.add_argument('--out')
    ap.add_argument('--file')
    ap.add_argument('--times')
    ap.add_argument('--xem-truoc', dest='xem_truoc', action='store_true')
    ap.add_argument('--tai-mo-hinh', dest='tai_mo_hinh', action='store_true')
    a = ap.parse_args()
    L = a.lenh.replace('_', '-')
    if L == 'quet':
        if not a.audio:
            raise SystemExit('⛔ thiếu --audio')
        from quet import quet
        quet(a.audio, a.link, a.res, a.nhac, a.ngon_ngu, a.work)
        return
    if L == 'cai-dat':
        from cai_dat import cai_dat
        sys.exit(0 if cai_dat(a.tai_mo_hinh) else 2)
    if L == 'dong-goi':
        from dong_goi import dong_goi
        dong_goi(a.out)
        return
    if L == 'tim':
        if not a.ten:
            raise SystemExit('⛔ run.py tim "<tên địa điểm>"')
        from ban_do_that import tim
        tim(a.ten)
        return
    if not a.work:
        raise SystemExit('⛔ thiếu --work')
    w = Path(a.work)
    if L == 'kiem-kh':
        from ke_hoach import kiem_kh
        ok = kiem_kh(w)
        sys.exit(0 if ok else 2)
    elif L == 'sub-dich':
        if not a.ngon_ngu:
            raise SystemExit('⛔ thiếu --ngon-ngu (tiếng của chữ trên hình, vd ko / en / ja)')
        from ke_hoach import khung_sub_dich
        khung_sub_dich(w, a.ngon_ngu)
    elif L == 'duyet':
        from dung import duyet
        duyet(w)
    elif L == 'dung':
        from dung import dung
        dung(w, luong=a.luong, out=a.out, xem_truoc=a.xem_truoc)
    elif L == 'tron-lai':
        from dung import tron_lai
        tron_lai(w, a.file, a.out)
    elif L == 'kiem':
        from kiem import kiem
        ok = kiem(w, a.file)
        sys.exit(0 if ok else 2)
    elif L == 'khung':
        from dung import chup_khung
        chup_khung(w, [float(x) for x in (a.times or '').split(',') if x.strip()])
    elif L == 'don':
        import shutil
        d = w / 'footage'
        if d.exists():
            shutil.rmtree(d)
        print('đã xoá', d)
    else:
        raise SystemExit(f'⛔ lệnh lạ: {a.lenh}')


if __name__ == '__main__':
    main()
