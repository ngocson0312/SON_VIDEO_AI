# -*- coding: utf-8 -*-
"""Cổng vào duy nhất của skill skill-bando-tintuc-chinhtri.

python -I scripts/run.py chuan-bi
python -I scripts/run.py nhan-loi <audio>                 -> work_ban_do/loi_doc.txt (Claude đọc, viết kich_ban.json)
python -I scripts/run.py kiem-kb  --work <work>           -> kiểm kịch bản (⛔ phải sửa)
python -I scripts/run.py tai      --work <work>           -> thực thể, cờ, ảnh người, ô bản đồ, duyet.jpg  (cần mạng)
python -I scripts/run.py dung     --work <work> [--nhanh] -> video (cạnh audio)
python -I scripts/run.py kiem     --work <work>           -> tự kiểm file cuối + kiem_khung.jpg
"""
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import chung as C

LENH = {
    "chuan-bi": "chuan_bi.py",
    "nhan-loi": "nhan_loi.py",
    "kiem-kb": "kiem_kich_ban.py",
    "tai": "tai_tai_nguyen.py",
    "dung": "dung.py",
    "kiem": "kiem.py",
}


def main():
    if len(sys.argv) < 2 or sys.argv[1] not in LENH:
        print(__doc__)
        sys.exit(1)
    script = os.path.join(C.SCRIPTS, LENH[sys.argv[1]])
    cmd = [sys.executable, "-I", "-X", "utf8", script] + sys.argv[2:]
    r = subprocess.run(cmd)
    sys.exit(r.returncode)


if __name__ == "__main__":
    main()
