# -*- coding: utf-8 -*-
"""cai_dat.py — máy mới: cài thư viện Python + kiểm đủ phần mềm cho skill TuanJp_DuLich_ManNgang.

  python -I -X utf8 run.py cai-dat                 (cài thư viện thiếu + kiểm ffmpeg / Node / Chrome / Whisper / mô hình tách người)
  python -I -X utf8 run.py cai-dat --tai-mo-hinh   (tải luôn mô hình Whisper large-v3 ~3 GB, để lần quét đầu khỏi chờ)
"""
import importlib.util
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

SKILL = Path(__file__).resolve().parent.parent
GOI = (('PIL', 'pillow'), ('numpy', 'numpy'), ('scipy', 'scipy'), ('requests', 'requests'),
       ('faster_whisper', 'faster-whisper'), ('onnxruntime', 'onnxruntime'), ('cv2', 'opencv-python-headless'))
NODE_MIN = 22


def _chay(cmd):
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=60)
        return (r.stdout or '') + (r.stderr or '')
    except Exception:
        return ''


def _co_mo_hinh():
    goc = os.environ.get('HF_HUB_CACHE') or os.path.join(
        os.environ.get('HF_HOME') or os.path.join(Path.home(), '.cache', 'huggingface'), 'hub')
    d = Path(goc) / 'models--Systran--faster-whisper-large-v3' / 'snapshots'
    return d.exists() and any(d.glob('*/model.bin'))


def tim_u2net():
    """Mô hình tách người (cú ĐẨY montage có người nhô qua mép): trong gói zip nằm ở assets/models/."""
    for p in (SKILL / 'assets' / 'models' / 'u2net_human_seg.onnx', Path.home() / '.u2net' / 'u2net_human_seg.onnx',
              SKILL.parent / 'bds-sale-viral' / 'assets' / 'models' / 'u2net_human_seg.onnx'):
        if p.exists() and p.stat().st_size > 100e6:
            return p
    return None


def cai_dat(tai_mo_hinh=False):
    loi_ = []
    print(f'SKILL: {SKILL}')
    # ---- Python + thư viện ----
    print(f'• Python {sys.version.split()[0]}  ({sys.executable})')
    if sys.version_info < (3, 10):
        loi_.append('Python phải ≥ 3.10 — cài bản mới ở python.org (tick "Add python.exe to PATH")')
    thieu = [p for m, p in GOI if importlib.util.find_spec(m) is None]
    if thieu:
        print(f'  … cài thư viện Python còn thiếu: {", ".join(thieu)} (cần mạng, vài phút)')
        r = subprocess.run([sys.executable, '-I', '-m', 'pip', 'install', '--upgrade', '-r', str(SKILL / 'requirements.txt')])
        importlib.invalidate_caches()
        thieu = [p for m, p in GOI if importlib.util.find_spec(m) is None]
        if r.returncode or thieu:
            loi_.append(f'chưa cài được thư viện Python: {", ".join(thieu) or "xem lỗi pip ở trên"} — chạy tay: '
                        f'"{sys.executable}" -I -m pip install -r "{SKILL / "requirements.txt"}"')
    if not thieu:
        print('  ✓ thư viện Python đủ (' + ', '.join(p for _, p in GOI) + ')')
    if importlib.util.find_spec('pillow_heif') is None:
        print('  (tuỳ chọn) ảnh HEIC iPhone: pip install pillow-heif — không có thì skill tự đổi bằng ffmpeg')
    # ---- ffmpeg ----
    for exe in ('ffmpeg', 'ffprobe'):
        if not shutil.which(exe):
            loi_.append(f'thiếu {exe} — cài: winget install Gyan.FFmpeg (hoặc tải bản "full" ở gyan.dev, giải nén, thêm thư mục bin '
                        f'vào PATH), mở lại cửa sổ lệnh')
    if shutil.which('ffmpeg'):
        print('• ' + _chay(['ffmpeg', '-version']).split('\n')[0][:90])
        f = _chay(['ffmpeg', '-hide_banner', '-filters'])
        e = _chay(['ffmpeg', '-hide_banner', '-encoders'])
        for loc in ('loudnorm', 'alimiter', 'cas', 'unsharp'):
            if f' {loc} ' not in f:
                loi_.append(f'ffmpeg thiếu bộ lọc {loc} — cài bản "full" (gyan.dev / winget Gyan.FFmpeg)')
        if 'libx264' not in e:
            loi_.append('ffmpeg thiếu bộ mã hoá libx264 — cài bản "full" (gyan.dev / winget Gyan.FFmpeg)')
        if ' zscale ' not in f:
            print('  (tuỳ chọn) ffmpeg không có zscale → clip HDR iPhone sẽ không được nắn màu; bản "full" có sẵn')
        if not [x for x in loi_ if 'ffmpeg' in x]:
            print('  ✓ ffmpeg đủ (loudnorm, alimiter, cas, libx264' + (', zscale' if ' zscale ' in f else '') + ')')
    # ---- Node ----
    node = shutil.which('node')
    if not node:
        loi_.append(f'thiếu Node.js ≥ {NODE_MIN} — cài: winget install OpenJS.NodeJS.LTS (hoặc nodejs.org), mở lại cửa sổ lệnh')
    else:
        v = _chay([node, '--version']).strip()
        m = re.match(r'v(\d+)', v)
        if not m or int(m.group(1)) < NODE_MIN:
            loi_.append(f'Node.js {v} quá cũ — cần ≥ {NODE_MIN} (winget install OpenJS.NodeJS.LTS)')
        else:
            print(f'• Node.js {v}  ✓')
    # ---- Chrome / Edge ----
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from chung import tim_chrome
    c = tim_chrome()
    if c:
        print(f'• Trình duyệt dựng hình: {c}  ✓')
    else:
        loi_.append('không thấy Chrome / Edge — cài Google Chrome, hoặc đặt biến môi trường DLN_CHROME=<đường dẫn chrome.exe>')
    # ---- mô hình tách người (cú ĐẨY montage) ----
    u2 = tim_u2net()
    if u2:
        print(f'• Mô hình tách người u2net_human_seg: {u2}  ✓')
    else:
        print('• ⚠ chưa có mô hình tách người u2net_human_seg.onnx (~170 MB; gói zip có sẵn ở assets\\models) — thiếu thì cú ĐẨY '
              'montage chỉ có chữ + vạch sáng, không có người nhô qua mép')
    # ---- mô hình Whisper ----
    if _co_mo_hinh():
        print('• Mô hình Whisper large-v3: đã có  ✓')
    elif tai_mo_hinh and importlib.util.find_spec('faster_whisper'):
        print('• Tải mô hình Whisper large-v3 (~3 GB, cần mạng — đừng tắt) …')
        from faster_whisper import WhisperModel
        WhisperModel('large-v3', device='cpu', compute_type='int8')
        print('  ✓ đã tải')
    else:
        print('• Mô hình Whisper large-v3 chưa có — lần quét đầu tự tải ~3 GB (hoặc chạy: run.py cai-dat --tai-mo-hinh)')
    print('• Cần MẠNG khi làm video: ảnh vệ tinh Esri, đường đi OSRM, tìm toạ độ Nominatim (bản đồ A → B), lần đầu tải Whisper')
    print()
    if loi_:
        for x in loi_:
            print('⛔ ' + x)
        print('\nCÀI ĐẶT: CHƯA ĐỦ — sửa các mục ⛔ ở trên rồi chạy lại')
        return False
    print('CÀI ĐẶT: SẴN SÀNG ✅')
    return True
