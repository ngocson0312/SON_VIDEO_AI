# -*- coding: utf-8 -*-
"""chung.py — hằng số phong cách + tiện ích dùng chung cho skill TuanJp_DuLich_ManNgang (video du lịch NGANG 16:9 cho YouTube).

Mọi con số PHONG CÁCH nằm ở đây và trong assets/khung/ngang.css|js. Muốn đổi kiểu → sửa ở đây, đừng rải số ra file khác.
"""
import hashlib
import json
import os
import re
import shutil
import subprocess
import unicodedata
from pathlib import Path

SKILL = Path(__file__).resolve().parent.parent
ASSETS = SKILL / 'assets'
SFX_DIR = ASSETS / 'sfx'
FONT_DIR = ASSETS / 'fonts'
KHUNG = ASSETS / 'khung'

W, H, FPS = 1920, 1080, 30
DUOI = 0.8               # giữ hình sau tiếng cuối (giây)
CTA_MIN = 5.0            # màn kết (Đăng ký kênh) dài tối thiểu — YouTube cho gắn màn hình kết thúc 5–20 s cuối
HIEN_MIN = 1.6           # mỗi mục chữ đứng ≥ 1,6 s (được hiện SỚM hơn lời)
HIEN_ANH = 2.0           # ảnh đứng ≥ 2 s
LUFS, TP = -14.0, -1.0   # YouTube chuẩn hoá về −14 LUFS

VIDEO_EXT = {'.mp4', '.mov', '.m4v', '.mkv', '.avi', '.webm', '.3gp', '.mts', '.m2ts', '.ts', '.wmv', '.flv', '.mpg', '.mpeg'}
IMG_EXT = {'.jpg', '.jpeg', '.jfif', '.png', '.webp', '.bmp', '.gif', '.tif', '.tiff', '.avif', '.heic', '.heif'}
AUDIO_EXT = {'.m4a', '.mp3', '.wav', '.aac', '.flac', '.ogg', '.opus'}

# ---- vùng an toàn khung ngang (title-safe 90 % của YouTube / TV) ----
AN_TOAN = {'tren': 54, 'duoi': 1026, 'trai': 96, 'phai': 1824}
SUB_Y = 990              # đáy dòng sub cuối (px) — trên thanh tiến trình YouTube
SUB_CO = 50              # cỡ chữ sub
SUB_MAX_KY_TU = 46       # ký tự / dòng (Latin) — ưu tiên 1 dòng, quá thì 2 dòng
SUB_MAX_TU = 12
SUB_NGAT = 0.38          # khoảng lặng ≥ này giữa 2 từ ⇒ ngắt cụm

# ---- bố cục footage ----
#   tran      clip / ảnh ngang tràn khung 16:9 (Ken Burns)
#   the_doc   clip / ảnh DỌC thành thẻ bo góc giữa / trái / phải trên nền nhoè của chính nó (không phóng vỡ clip dọc)
#   ghep      2–3 clip / ảnh dọc ghép cạnh nhau thành các ô cao trọn khung (trượt vào lần lượt)
#   the_anh   ảnh nhỏ (< 1500 px ngang) thành thẻ ảnh có viền trên nền nhoè của chính nó
BO_CUC = ('tran', 'the_doc', 'ghep', 'the_anh')
THE_DOC_CAO = 900        # chiều cao thẻ clip dọc (px) → rộng 506
THE_DOC_X = {'giua': 960, 'trai': 600, 'phai': 1320}   # tâm x thẻ dọc theo vị trí
GHEP_KHE = 10            # khe giữa các ô ghép
CHUYEN_DONG = ('zoom_vao', 'zoom_ra', 'lia_trai', 'lia_phai', 'lia_len', 'lia_xuong', 'dung')

# ---- chuyển cảnh: tên → (thời lượng giây, SFX) ----
# KHÔNG NHOÈ (người dùng ghét nhoè: "hiệu ứng mờ khó chịu, làm video bị mờ hẳn đi") — mọi kiểu đều sắc nét.
# MƯỢT, KHÔNG GẤP (người dùng 13/11/2026: "1-2 giây lại hiển thị cái ảnh… chuyển hình xong có sfx… chưa kịp nhìn… chuyển nhanh quá")
# → chuyển 0,6–0,8 s; cú chuyển thường KHÔNG có SFX (chỉ màn quét mở chương và cú `phong` cố ý mới có tiếng).
CHUYEN = {
    'cat':       (0.00, None),
    'zoom_muot': (0.70, None),        # ZOOM MƯỢT: cũ đẩy vào, mới thu về chồng lên từ từ — kiểu "xịn" mặc định
    'hoa_tan':   (0.60, None),
    'nhoe':      (0.60, None),        # (tên cũ) hoà tan + sáng bừng — KHÔNG nhoè
    'lia':       (0.65, None),        # trượt có chiều sâu: cũ lùi chậm + tối, mới trượt phủ lên
    'lia_doc':   (0.65, None),
    'truot':     (0.60, None),        # đẩy ngang cả 2 cảnh
    'loe':       (0.80, None),        # loé nắng ấm (light leak) + hoà tan
    'zoom':      (0.45, None),        # zoom xuyên sắc nét (phóng vụt → loé → thu) — dùng HIẾM, chỗ cần lực
    'phong':     (0.30, 'phong'),     # cắt + đập vào 1,22 → 1 — chỉ khi CỐ Ý (không dùng mặc định cho hook)
    'man':       (0.80, 'zoom'),      # MÀN SÁNG quét chéo — mở CHƯƠNG / điểm đến mới (có whoosh)
}
CANH_MIN = 2.5          # mỗi cảnh đứng ≥ 2,5 s (kịp nhìn); montage thẻ dọc cùng chỗ (chỉ đổi hình) ≥ 2,0; hook ≥ 1,8 (theo nhịp vế câu)

# ---- SFX: sự kiện → (file, dB so với đỉnh −1 dBFS, lệch giây so với mốc) ----
SFX = {
    'lia':       ('whoosh-short.mp3', -12, -0.10),
    'zoom':      ('swoosh.mp3', -11, -0.12),
    'nhoe':      ('quick-swoosh.mp3', -15, -0.05),
    'loe':       ('fairy-dust.mp3', -17, -0.05),
    'mo_dau':    ('whoosh.wav', -12, -0.05),
    'phong':     ('whoosh-short.mp3', -8, -0.12),
    'boom':      ('boom.wav', -2, -0.02),            # cú DROP tên chủ đề (tự tổng hợp: scripts/tao_sfx.py)
    'riser':     ('riser-metallic.mp3', -8, 0.0),     # dồn 1,85 s, đỉnh rơi đúng cú drop
    'lap_lanh':  ('sparkle.mp3', -15, 0.0),
    'chuong':    ('swoosh.mp3', -12, -0.02),
    'chuong_so': ('ding.mp3', -17, 0.35),
    'dia_danh':  ('quick-swoosh.mp3', -14, 0.0),
    'ghim':      ('pop.mp3', -11, 0.15),
    'chip':      ('pop-2.mp3', -11, 0.05),
    'tu_khoa':   ('quick-swoosh.mp3', -15, 0.0),
    'so_lon':    ('riser-metallic.mp3', -18, 0.0),
    'so_xong':   ('ding.mp3', -15, 0.0),
    'the_anh':   ('camera-shutter.mp3', -12, 0.05),
    'liet_ke':   ('pop.mp3', -12, 0.05),
    'tieu_de':   ('whoosh.wav', -14, -0.05),
    'trich':     ('quick-swoosh.mp3', -14, 0.0),
    'ban_do':    ('swoosh.mp3', -13, -0.05),
    'cta_vao':   ('swoosh.mp3', -12, 0.0),
    'bam':       ('click-button.mp3', -7, 0.0),
    'chuong_bell': ('quick-ting.mp3', -10, 0.0),
    'thich':     ('pop.mp3', -9, 0.0),
}

# SFX phải NGHE RÕ trên nền giọng (người dùng từng chê "không thấy có SFX" khi đặt nhỏ): mức đỉnh 10 ms của tiếng so với giọng
# TẠI CHỖ (±1,5 s quanh tiếng, trung vị RMS 50 ms) — bộ trộn tự tính gain cho từng tiếng; tiếng không có trong bảng dùng dB cố định.
SFX_TREN = {'phong': 4, 'boom': 7, 'riser': 3, 'mo_dau': 4, 'zoom': 2, 'chuong_so': 0, 'bam': 4, 'thich': 2, 'cta_vao': 1,
            'chip': -4, 'liet_ke': -4, 'ghim': -3, 'chuong_bell': 1}

# ---- nhạc nền (CHỈ file người dùng đưa trong Resources / --nhac) ----
NHAC_MUC = -14.0         # nhạc dưới giọng (dB, cả bài)
NHAC_DANG = 8.0          # dâng ở khoảng lặng ≥ 1 s
NHAC_SAN = 5.0           # nâng đoạn nhạc nhỏ tối đa
NHAC_LUI_MAX = 45.0      # nhạc dài hơn video ≤ chừng này → bỏ bớt đầu cho nốt kết trùng cuối video
NHAC_TEN = r'(music|background|nhac|nhạc|bgm|(^|[^a-z])bg([^a-z]|$)|beat|soundtrack|song|melody|instrumental|audio_?bg)'
GIONG_TEN = r'(voice|giong|giọng|kich ?ban|kịch ?bản|thuyet ?minh|thuyết ?minh|narrat|loi ?doc|lời ?đọc|vo\b|audio)'

# ---- chữ mặc định màn kết YouTube (theo ngôn ngữ giọng) ----
NGON_NGU = {
    'vi': {'ten': 'tiếng Việt', 'nut': 'ĐĂNG KÝ', 'nut_da': 'ĐÃ ĐĂNG KÝ', 'tieu_de': 'Cùng khám phá Việt Nam',
           'viet_tay': 'Hẹn gặp bạn ở chuyến đi tiếp theo', 'thich': 'Thích', 'chia_se': 'Chia sẻ', 'dan_chuong': 'Điểm đến',
           'nguon': 'Ảnh'},
    'en': {'ten': 'English', 'nut': 'SUBSCRIBE', 'nut_da': 'SUBSCRIBED', 'tieu_de': 'Explore Vietnam with us',
           'viet_tay': 'See you on the next trip', 'thich': 'Like', 'chia_se': 'Share', 'dan_chuong': 'Destination', 'nguon': 'Photo'},
    'ko': {'ten': '한국어', 'nut': '구독', 'nut_da': '구독중', 'tieu_de': '함께 베트남을 여행해요', 'viet_tay': '다음 여행에서 만나요',
           'thich': '좋아요', 'chia_se': '공유', 'dan_chuong': '여행지', 'nguon': '사진'},
    'ja': {'ten': '日本語', 'nut': 'チャンネル登録', 'nut_da': '登録済み', 'tieu_de': 'ベトナムを一緒に旅しよう', 'viet_tay': '次の旅でまた会いましょう',
           'thich': '高評価', 'chia_se': '共有', 'dan_chuong': '目的地', 'nguon': '写真'},
    'zh': {'ten': '中文', 'nut': '订阅', 'nut_da': '已订阅', 'tieu_de': '一起探索越南', 'viet_tay': '下次旅行再见',
           'thich': '点赞', 'chia_se': '分享', 'dan_chuong': '目的地', 'nguon': '图片'},
}
KHONG_CACH = ('ja', 'zh', 'th')

# ---- icon hợp lệ cho chip / địa danh / liệt kê (vẽ SVG trong ngang.js) ----
ICON = {'ghim', 'nui', 'bien', 'dao', 'thac', 'may', 'mat_troi', 'trang', 'sao', 'tim', 'may_anh', 'tau', 'tau_hoa', 'cap_treo',
        'xe_may', 'o_to', 'may_bay', 'di_bo', 'co', 'den_long', 'phao_hoa', 'drone', 'hoa', 'la', 'lua', 'ruong', 'chua', 'cau',
        'thanh_pho', 'lich_su', 'dong_ho', 'nhiet_do', 'an_uong', 'ca_phe', 'lap_lanh', 'balo', 'la_ban', 'ban_do', 'nguoi', 'gio',
        'tuyet', 'mua', 'song_nuoc', 'non_la', 'cay', 'tich', 've', 'gia', 'khach_san', 'leu', 'hang'}

LOAI_DH = ('mo_dau', 'hook_tu', 'chuong', 'dia_danh', 'tu_khoa', 'tieu_de', 'chip', 'so_lon', 'liet_ke', 'trich', 'ban_do')
NHO = ('dia_danh', 'chip')       # đồ hoạ nhỏ — được chồng thời gian với 1 đồ hoạ lớn


# ---------------- tiện ích ----------------
def loi(msg):
    print(msg, flush=True)


def run(cmd, check=True, capture=False, **kw):
    r = subprocess.run([str(c) for c in cmd], capture_output=capture, text=capture, encoding='utf-8' if capture else None,
                       errors='replace' if capture else None, **kw)
    if check and r.returncode != 0:
        raise SystemExit(f"⛔ Lệnh lỗi ({r.returncode}): {' '.join(map(str, cmd))[:300]}\n{(r.stderr or '')[-1500:] if capture else ''}")
    return r


def probe(p):
    r = run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration:stream=codec_type,width,height,r_frame_rate,color_transfer'
             ':stream_side_data=rotation', '-of', 'json', p], capture=True)
    d = json.loads(r.stdout or '{}')
    o = {'duration': float(d.get('format', {}).get('duration') or 0), 'w': 0, 'h': 0, 'fps': 0, 'audio': False, 'video': False,
         'hdr': False}
    for s in d.get('streams', []):
        if s.get('codec_type') == 'video' and not o['video']:
            o['video'] = True
            o['w'], o['h'] = s.get('width', 0), s.get('height', 0)
            o['hdr'] = s.get('color_transfer') in ('smpte2084', 'arib-std-b67')
            try:
                a, b = s.get('r_frame_rate', '0/1').split('/')
                o['fps'] = float(a) / float(b or 1)
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
    return re.sub(r'[^\w]+', ' ', s).strip()


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


def mo_anh(p, nen=(18, 20, 26)):
    """mở MỌI kiểu ảnh → PIL RGB đứng đúng chiều (xoay EXIF, HEIC qua pillow-heif / ffmpeg, GIF khung đầu, PNG trong suốt lót nền)."""
    import tempfile
    from PIL import Image, ImageOps
    p = Path(p)
    if p.suffix.lower() in ('.heic', '.heif', '.avif'):
        try:
            import pillow_heif
            pillow_heif.register_heif_opener()
        except ImportError:
            tam = Path(tempfile.gettempdir()) / 'dln_heic' / f'{bam(str(p.resolve()), p.stat().st_mtime)}.png'
            if not tam.exists():
                tam.parent.mkdir(parents=True, exist_ok=True)
                run(['ffmpeg', '-v', 'error', '-y', '-i', p, '-frames:v', '1', tam], check=False)
            if not tam.exists():
                raise RuntimeError(f'không đọc được {p.name} — cài: python -I -m pip install pillow-heif')
            p = tam
    im = Image.open(p)
    if getattr(im, 'n_frames', 1) > 1:
        im.seek(0)
    try:
        im = ImageOps.exif_transpose(im)
    except Exception:
        pass
    if im.mode in ('RGBA', 'LA', 'PA') or (im.mode == 'P' and 'transparency' in im.info):
        im = im.convert('RGBA')
        o = Image.new('RGB', im.size, nen)
        o.paste(im, mask=im.split()[-1])
        return o
    if im.mode in ('I;16', 'I;16B', 'I;16L', 'I'):
        im = im.point(lambda v: v / 256).convert('L')
    return im.convert('RGB')


def doc_json(p):
    return json.loads(Path(p).read_text(encoding='utf-8-sig'))   # chịu BOM (Notepad / PowerShell 5.1)


def ghi_json(p, d):
    Path(p).write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding='utf-8')


def bam(*xs):
    return hashlib.md5(json.dumps(xs, ensure_ascii=False, sort_keys=True, default=str).encode('utf-8')).hexdigest()[:10]


def node():
    n = shutil.which('node')
    if not n:
        raise SystemExit('⛔ Thiếu Node.js (>= 22) trong PATH — cài Node rồi chạy lại.')
    v = run([n, '-v'], capture=True).stdout.strip().lstrip('v').split('.')[0]
    if int(v or 0) < 22:
        raise SystemExit(f'⛔ Node {v} quá cũ, cần >= 22 (có WebSocket sẵn).')
    return n


def tim_chrome():
    ung = [os.environ.get('DLN_CHROME'),
           'C:/Program Files/Google/Chrome/Application/chrome.exe',
           'C:/Program Files (x86)/Google/Chrome/Application/chrome.exe',
           os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Google/Chrome/Application/chrome.exe'),
           'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe',
           'C:/Program Files/Microsoft/Edge/Application/msedge.exe',
           '/usr/bin/google-chrome', '/usr/bin/chromium', '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome']
    for p in ung:
        if p and os.path.exists(p):
            return p
    return None


def nhan_loi(wav16, ngon_ngu=None, goi_y=None, model='large-v3'):
    """Whisper large-v3 (GPU nếu có cuBLAS, không thì CPU int8), tự nhận ngôn ngữ → (từ [{w,s,e}], câu, mã ngôn ngữ, xác suất)."""
    import wave
    import numpy as np
    from faster_whisper import WhisperModel
    wf = wave.open(str(wav16))
    a = np.frombuffer(wf.readframes(wf.getnframes()), dtype=np.int16).astype(np.float32) / 32768

    def chay(dev, ct):
        m = WhisperModel(model, device=dev, compute_type=ct)
        segs, info = m.transcribe(a, language=ngon_ngu or None, word_timestamps=True, vad_filter=False, beam_size=5,
                                  initial_prompt=goi_y or None)
        return list(segs), info
    try:
        segs, info = chay('cuda', 'float16')
    except Exception as e:
        loi(f'  (GPU không dùng được: {str(e)[:80]} → chạy CPU, lâu hơn)')
        segs, info = chay('cpu', 'int8')
    cau, tu = [], []
    for s in segs:
        ws = [{'w': w.word.strip(), 's': round(w.start, 2), 'e': round(w.end, 2)} for w in s.words if w.word.strip()]
        if not ws:
            continue
        tu += ws
        cau.append({'s': ws[0]['s'], 'e': ws[-1]['e'], 'text': s.text.strip()})
        loi(f"  [{ws[0]['s']:7.2f}-{ws[-1]['e']:7.2f}] {s.text.strip()}")
    return tu, cau, (ngon_ngu or info.language), float(getattr(info, 'language_probability', 1.0) or 1.0)
