# -*- coding: utf-8 -*-
"""cai_dat.py — máy mới: cài thư viện Python thiếu (requirements.txt) + kiểm ffmpeg / Node ≥ 22 / Chrome-Edge / mô hình Whisper."""
import importlib
import shutil
import subprocess
import sys
from pathlib import Path

from chung import SKILL, loi, tim_chrome

MOD = {'PIL': 'pillow', 'numpy': 'numpy', 'scipy': 'scipy', 'requests': 'requests', 'faster_whisper': 'faster-whisper'}


def cai_dat():
    ok = True
    thieu = []
    for m, goi in MOD.items():
        try:
            importlib.import_module(m)
        except ImportError:
            thieu.append(goi)
    if thieu:
        loi(f'Cài thư viện thiếu: {", ".join(thieu)} …')
        r = subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', str(SKILL / 'requirements.txt')])
        ok &= r.returncode == 0
    loi(f"{'✅' if not thieu or ok else '⛔'} Python {sys.version.split()[0]} + thư viện")
    ff = shutil.which('ffmpeg') and shutil.which('ffprobe')
    loi(f"{'✅' if ff else '⛔'} ffmpeg / ffprobe {'có' if ff else 'THIẾU — cài bản full (gyan.dev) và thêm vào PATH'}")
    ok &= bool(ff)
    n = shutil.which('node')
    v = subprocess.run([n, '-v'], capture_output=True, text=True).stdout.strip() if n else ''
    nok = bool(v) and int(v.lstrip('v').split('.')[0]) >= 22
    loi(f"{'✅' if nok else '⛔'} Node {v or 'THIẾU'} (cần ≥ 22)")
    ok &= nok
    c = tim_chrome()
    loi(f"{'✅' if c else '⛔'} Chrome / Edge {c or 'THIẾU — cài Chrome hoặc đặt DLN_CHROME'}")
    ok &= bool(c)
    hub = Path.home() / '.cache' / 'huggingface' / 'hub' / 'models--Systran--faster-whisper-large-v3'
    loi(f"{'✅' if hub.exists() else 'ℹ'} Whisper large-v3 {'đã tải' if hub.exists() else 'chưa tải — lần quét đầu tự tải ~3 GB'}")
    loi('CÀI ĐẶT: ' + ('SẴN SÀNG' if ok else 'CHƯA ĐỦ — xem dòng ⛔'))
    return ok
