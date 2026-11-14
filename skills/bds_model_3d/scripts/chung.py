# -*- coding: utf-8 -*-
"""chung.py — hằng số phong cách + tiện ích dùng chung cho skill bds_model_3d.

Mọi con số PHONG CÁCH (đo từ video mẫu Khánh Nguyễn 12/11/2026) nằm ở đây và trong assets/khung/bds3d.css|js.
Muốn đổi kiểu → sửa ở đây, đừng rải số ra các file khác.
"""
import difflib
import json
import math
import os
import re
import shutil
import subprocess
import sys
import unicodedata
from pathlib import Path

SKILL = Path(__file__).resolve().parent.parent
ASSETS = SKILL / 'assets'
SFX_DIR = ASSETS / 'sfx'
KHUNG = ASSETS / 'khung'

W, H, FPS = 1080, 1920, 30
LEAD = 0.22            # chữ bắt đầu hiện trước lời đọc (giây) — mẫu: chữ nét đúng lúc nghe từ đó
DUOI = 0.30            # giữ khung sau tiếng cuối
LUFS, TP = -14.0, -1.0

VIDEO_EXT = {'.mp4', '.mov', '.m4v', '.mkv', '.avi', '.webm'}
IMG_EXT = {'.jpg', '.jpeg', '.png', '.webp', '.bmp'}
AUDIO_EXT = {'.m4a', '.mp3', '.wav', '.aac', '.flac', '.ogg', '.opus'}

# loại cảnh → trạng thái footage
MODE = {'the_noi': 'card', 'tran_man': 'full', 'nen_nhoe': 'blur', 'nen_toi': 'none', 'giao_dien': 'none', 'dien_thoai': 'none'}
MAU_GIAO_DIEN = ('ban_do', 'chat_ai', 'anh')

CAP_TOP = {'tren': 148, 'giua': 560}   # mép trên cụm chữ (px)
CAP_TOP_PHONE = 100                     # cảnh điện thoại: chữ đẩy cao hơn
PILL_Y = 980                            # tâm viên kính
TILE_Y = 1056                           # tâm hàng ô kính
KIEU_CHU = ('dan', 'vang', 'trang', 'buoc', 'tit', 'noi', 'trich')
KIEU_NGUYEN_CUM = ('buoc', 'tit', 'noi', 'trich')   # hiện cả cụm một lúc (không từng từ)

# SFX: tên sự kiện → (file, dB so với đỉnh −1 dBFS, lệch giây so với mốc sự kiện)
SFX = {
    'the_vao':      ('pop.mp3', -9, 0.10),
    'phong_the':    ('swoosh.mp3', -10, 0.22),
    'nhoe_nen':     ('quick-swoosh.mp3', -16, 0.10),
    'ket_qua_vao':  ('quick-swoosh.mp3', -10, 0.25),
    'giao_dien_vao': ('quick-swoosh.mp3', -13, 0.05),
    'dien_thoai_vao': ('quick-swoosh.mp3', -9, 0.25),
    'vien_kinh':    ('pop.mp3', -9, 0.12),
    'gach':         ('swoosh.mp3', -13, 0.02),
    'o_kinh':       ('pop-2.mp3', -9, 0.05),
    'go_phim':      ('iphone-typing.mp3', -20, 0.0),
    'ghim':         ('pop.mp3', -8, 0.26),
    'bang_truot':   ('quick-swoosh.mp3', -11, 0.05),
    'cham':         ('click-button.mp3', -7, 0.0),
    'thong_bao':    ('pop-2.mp3', -10, 0.05),
    'chip':         ('pop-2.mp3', -9, 0.03),
    'gui':          ('click-button.mp3', -7, 0.0),
    'xoa':          ('swoosh.mp3', -14, 0.02),
    'video_tha':    ('pop.mp3', -8, 0.05),
    'video_vao_o':  ('swoosh.mp3', -12, 0.05),
    'tin_nhan':     ('pop-2.mp3', -9, 0.03),
    'tai_lieu':     ('pop.mp3', -9, 0.05),
    # cảnh 3D
    'vong_3d':      ('quick-swoosh.mp3', -15, 0.05),
    'chu_thich_3d': ('pop-2.mp3', -11, 0.06),
    'dia_danh_3d':  ('pop-2.mp3', -13, 0.05),
    'logo_3d':      ('sparkle.mp3', -15, 0.10),
}
NHAC_MUC = -23.0        # nhạc dưới giọng khi đang nói (dB so với giọng)
NHAC_DANG = 16.0        # nhạc dâng thêm ở khoảng lặng lời ≥ 1 s


def loi(msg):
    print(msg, flush=True)


def run(cmd, check=True, capture=False, **kw):
    r = subprocess.run([str(c) for c in cmd], capture_output=capture, text=capture, encoding='utf-8' if capture else None,
                       errors='replace' if capture else None, **kw)
    if check and r.returncode != 0:
        raise SystemExit(f"⛔ Lệnh lỗi ({r.returncode}): {' '.join(map(str, cmd))[:300]}\n{(r.stderr or '')[-1500:] if capture else ''}")
    return r


def probe(p):
    r = run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration:stream=codec_type,width,height,r_frame_rate:stream_side_data=rotation',
             '-of', 'json', p], capture=True)
    d = json.loads(r.stdout or '{}')
    o = {'duration': float(d.get('format', {}).get('duration') or 0), 'w': 0, 'h': 0, 'fps': 0, 'audio': False, 'video': False}
    for s in d.get('streams', []):
        if s.get('codec_type') == 'video' and not o['video']:
            o['video'] = True; o['w'], o['h'] = s.get('width', 0), s.get('height', 0)
            try:
                a, b = s.get('r_frame_rate', '0/1').split('/'); o['fps'] = float(a) / float(b or 1)
            except Exception:
                pass
            rot = 0
            for sd in s.get('side_data_list', []) or []:
                rot = int(sd.get('rotation', 0) or 0)
            if abs(rot) in (90, 270):
                o['w'], o['h'] = o['h'], o['w']
        if s.get('codec_type') == 'audio':
            o['audio'] = True
    return o


def bo_dau(s):
    s = unicodedata.normalize('NFD', str(s).lower()).replace('đ', 'd')
    s = ''.join(c for c in s if unicodedata.category(c) != 'Mn')
    return re.sub(r'[^a-z0-9]+', '', s)


def giong_nhau(a, b):
    a, b = bo_dau(a), bo_dau(b)
    if not a or not b:
        return 0.0
    if a == b:
        return 1.0
    return difflib.SequenceMatcher(None, a, b).ratio()


def ten_moi(p):
    p = Path(p)
    if not p.exists():
        return p
    k = 2
    stem = re.sub(r'_ban\d+$', '', p.stem)
    while True:
        q = p.with_name(f'{stem}_ban{k}{p.suffix}')
        if not q.exists():
            return q
        k += 1


def url(p, thu_muc=False):
    u = Path(p).resolve().as_uri()
    return u + '/' if thu_muc and not u.endswith('/') else u


def doc_json(p):
    return json.loads(Path(p).read_text(encoding='utf-8'))


def ghi_json(p, d):
    Path(p).write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding='utf-8')


def node():
    n = shutil.which('node')
    if not n:
        raise SystemExit('⛔ Thiếu Node.js (>= 22) trong PATH — cài Node rồi chạy lại.')
    v = run([n, '-v'], capture=True).stdout.strip().lstrip('v').split('.')[0]
    if int(v or 0) < 22:
        raise SystemExit(f'⛔ Node {v} quá cũ, cần >= 22 (có WebSocket sẵn).')
    return n


# ---------------- nhận lời ----------------
def nhan_loi(wav16, tu_khoa=None, model='large-v3'):
    """Whisper large-v3 (CPU int8) → danh sách từ [{w,s,e}] + câu. Đọc wav bằng numpy (tránh lỗi PyAV)."""
    import wave
    import numpy as np
    from faster_whisper import WhisperModel
    wf = wave.open(str(wav16))
    a = np.frombuffer(wf.readframes(wf.getnframes()), dtype=np.int16).astype(np.float32) / 32768
    m = WhisperModel(model, device='cpu', compute_type='int8')
    prompt = None
    if tu_khoa:
        prompt = 'Các từ có trong lời: ' + ', '.join(tu_khoa) + '.'
    segs, _ = m.transcribe(a, language='vi', word_timestamps=True, vad_filter=False, beam_size=5, initial_prompt=prompt)
    cau, tu = [], []
    for s in segs:
        ws = [{'w': w.word.strip(), 's': round(w.start, 2), 'e': round(w.end, 2)} for w in s.words if w.word.strip()]
        tu += ws
        cau.append({'s': round(s.start, 2), 'e': round(s.end, 2), 'text': s.text.strip()})
    return tu, cau
