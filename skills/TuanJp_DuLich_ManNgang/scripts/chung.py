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
CTA_MIN = 6.5            # màn kết (câu hỏi → CẢM ƠN → Thích & Đăng ký) dài tối thiểu — YouTube cho gắn màn hình kết thúc 5–20 s cuối
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
# KHÁCH 14/11/2026: "không làm ảnh kiểu chia màn hình… giống màn hình dọc quá, LÚC NÀO CŨNG FULL MÀN HÌNH giữa ảnh và video"
# → chỉ cho `tran` (clip / ảnh dọc cũng cắt dải 16:9 rồi phóng tràn, làm nét bù); the_doc / ghep / the_anh bị kiem-kh chặn ⛔.
BO_CUC_CHO = ('tran',)
CAT_Y_DOC = 0.42         # clip / ảnh DỌC tràn khung ngang: neo dải 16:9 hơi cao hơn giữa (trời + chủ thể, bớt chân / tay cầm máy)
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
    'ban_do_vao': ('swoosh.mp3', -12, -0.08),        # bản đồ A → B bay vào
    'xe_chay':   ('xe-chay.wav', -20, 0.0),           # tiếng xe rất nhỏ lúc tuyến chạy (bản đồ ô tô / xe máy)
    'toi_noi':   ('ding.mp3', -16, 0.0),              # tới điểm đến — ghim rơi
    'binh_luan': ('pop-2.mp3', -12, 0.0),             # mỗi thẻ bình luận ảo bật lên
    'teaser_dap': ('whoosh-short.mp3', -9, -0.12),    # cú đập chữ trong teaser (chỉ cảnh `phong`)
}

# SFX phải NGHE RÕ trên nền giọng (người dùng từng chê "không thấy có SFX" khi đặt nhỏ): mức đỉnh 10 ms của tiếng so với giọng
# TẠI CHỖ (±1,5 s quanh tiếng, trung vị RMS 50 ms) — bộ trộn tự tính gain cho từng tiếng; tiếng không có trong bảng dùng dB cố định.
SFX_TREN = {'phong': 4, 'boom': 7, 'riser': 3, 'mo_dau': 4, 'zoom': 2, 'chuong_so': 0, 'bam': 4, 'thich': 2, 'cta_vao': 1,
            'chip': -4, 'liet_ke': -4, 'ghim': -3, 'chuong_bell': 1, 'ban_do_vao': 1, 'toi_noi': -2, 'binh_luan': -5,
            'xe_chay': -12}

# ---- TEASER mở màn (khách 14/11/2026: "đầu video để đoạn cao trào giật gân giữ người xem tầm 30 s, xem cái là muốn đi du lịch luôn")
#   ke_hoach.mo_man = {dai, canh[], do_hoa[]} — giờ RIÊNG 0…dai; giọng đọc lùi `dai` giây (mọi giờ phần thân = giờ trong loi_doc.txt).
#   Teaser ~20 s chỉ có NHẠC (to như giọng, tới lúc giọng vào thì hạ về nền) + cảnh ĐẸP NHẤT mọi điểm đến cắt THEO NHỊP nhạc
#   + chữ lớn đập vào; cộng hook lời ~10 s → ~30 s cao trào trước khi vào điểm đến đầu tiên.
MO_MAN_DAI = 20.0        # teaser mặc định (giây) — tự khớp về ô nhịp gần nhất khi có nhạc
MO_MAN_MIN, MO_MAN_MAX = 12.0, 32.0
NHAC_TEASER = 12.0       # nhạc trong teaser dâng thêm (dB) so với mức nền (−14 + 12 ≈ −2 dB so với giọng) — nhạc là "giọng" của teaser
CANH_TEASER_MIN = 1.8    # cảnh teaser cắt theo nhịp: ≥ 1,8 s (1 ô nhịp ~2–2,5 s) — người dùng ghét 1–2 s/cảnh "chưa kịp nhìn"

# ---- BẢN ĐỒ A → B (khách 14/11/2026: "có ghi gg map Việt Nam đi từ điểm A đến B bao nhiêu km, bao nhiêu lâu")
#   Mỗi `chuong` có toa_do = 1 BẢN ĐỒ VỆ TINH THẬT bay từ điểm trước (chương đầu: XUAT_PHAT_MAC_DINH) → điểm đến, tuyến xanh kiểu
#   Google Maps, thẻ "≈ giờ · km" tính bằng đường đi thật OSRM (luôn có "≈"), bản đồ VN nhỏ góc (có Hoàng Sa, Trường Sa).
XUAT_PHAT_MAC_DINH = {'ten': 'Hà Nội', 'toa_do': [21.0285, 105.8542]}
BAN_DO_MIN = 3.6         # bản đồ đứng ≥ 3,6 s (bay ra → chạy → sà vào → tên điểm đến)
TUYEN_XANH = '#4C8DF6'   # màu tuyến kiểu Google Maps

# ---- BÌNH LUẬN ẢO (khách 14/11/2026: "mỗi địa điểm / món ăn có bình luận ảo bằng tiếng Anh, tiếng Hàn khen chê")
#   Thẻ bình luận kiểu YouTube nổi bên PHẢI (avatar chữ cái, tên giả, cờ nhỏ, câu khen / chê nhẹ, lượt thích) — mỗi điểm đến 1 đợt
#   2–3 thẻ. Ngân hàng câu theo loại cảnh: assets/binh_luan.json. NGOẠI LỆ duy nhất của luật ngôn ngữ (mục 10): bình luận theo
#   tiếng `binh_luan_nn` (mặc định ["en", "ko"]), không theo tiếng audio. Tên người dùng tự đặt, không phải người thật.
BINH_LUAN_NN = ('en', 'ko')
BINH_LUAN_CACH = 1.25    # 2 thẻ cách nhau (giây)
BINH_LUAN_DUNG = 6.0     # 1 đợt 3 thẻ đứng (giây) tính từ thẻ đầu — đủ đọc 3 câu ngắn

# ---- nhạc nền (CHỈ file người dùng đưa trong Resources / --nhac) ----
NHAC_MUC = -14.0         # nhạc dưới giọng (dB, cả bài)
NHAC_DANG = 8.0          # dâng ở khoảng lặng ≥ 1 s
NHAC_SAN = 5.0           # nâng đoạn nhạc nhỏ tối đa
NHAC_LUI_MAX = 45.0      # nhạc dài hơn video ≤ chừng này → bỏ bớt đầu cho nốt kết trùng cuối video
NHAC_TEN = r'(music|background|nhac|nhạc|bgm|(^|[^a-z])bg([^a-z]|$)|beat|soundtrack|song|melody|instrumental|audio_?bg)'
GIONG_TEN = r'(voice|giong|giọng|kich ?ban|kịch ?bản|thuyet ?minh|thuyết ?minh|narrat|loi ?doc|lời ?đọc|vo\b|audio)'

# ---- chữ mặc định màn kết YouTube (theo ngôn ngữ giọng) ----
#   cam_on / loi_moi: màn kết CẢM ƠN + mời Thích & Đăng ký (khách 14/11/2026: "cuối video cảm ơn mọi người xem và hãy like và đăng ký")
#   gio / phut / o_to…: chữ trên thẻ bản đồ A → B
NGON_NGU = {
    'vi': {'ten': 'tiếng Việt', 'nut': 'ĐĂNG KÝ', 'nut_da': 'ĐÃ ĐĂNG KÝ', 'tieu_de': 'Cùng khám phá Việt Nam',
           'viet_tay': 'Hẹn gặp bạn ở chuyến đi tiếp theo', 'thich': 'Thích', 'chia_se': 'Chia sẻ', 'chuong_nhan': 'Bật chuông', 'dan_chuong': 'Điểm đến',
           'nguon': 'Ảnh', 'cam_on': 'Cảm ơn bạn đã xem', 'loi_moi': 'Nhấn Thích & Đăng ký kênh để cùng đi tiếp những hành trình mới nhé!',
           'gio': 'giờ', 'phut': 'phút', 'xe': {'o_to': 'Ô tô', 'xe_may': 'Xe máy', 'xe_buyt': 'Xe khách', 'di_bo': 'Đi bộ',
                                                  'may_bay': 'Máy bay', 'tau_hoa': 'Tàu hoả', 'tau_thuy': 'Tàu thuỷ', 'xe_dap': 'Xe đạp'},
           'tuyen': 'Tuyến đường', 'uoc': 'ước tính theo đường đi thật'},
    'en': {'ten': 'English', 'nut': 'SUBSCRIBE', 'nut_da': 'SUBSCRIBED', 'tieu_de': 'Explore Vietnam with us',
           'viet_tay': 'See you on the next trip', 'thich': 'Like', 'chia_se': 'Share', 'chuong_nhan': 'Notify', 'dan_chuong': 'Destination', 'nguon': 'Photo',
           'cam_on': 'Thanks for watching', 'loi_moi': 'Like & subscribe to join the next journey!', 'gio': 'h', 'phut': 'min',
           'xe': {'o_to': 'Car', 'xe_may': 'Motorbike', 'xe_buyt': 'Bus', 'di_bo': 'Walk', 'may_bay': 'Flight', 'tau_hoa': 'Train',
                  'tau_thuy': 'Boat', 'xe_dap': 'Bike'}, 'tuyen': 'Route', 'uoc': 'estimated by real road'},
    'ko': {'ten': '한국어', 'nut': '구독', 'nut_da': '구독중', 'tieu_de': '함께 베트남을 여행해요', 'viet_tay': '다음 여행에서 만나요',
           'thich': '좋아요', 'chia_se': '공유', 'chuong_nhan': '알림', 'dan_chuong': '여행지', 'nguon': '사진', 'cam_on': '시청해 주셔서 감사합니다',
           'loi_moi': '좋아요와 구독으로 다음 여행도 함께해요!', 'gio': '시간', 'phut': '분',
           'xe': {'o_to': '자동차', 'xe_may': '오토바이', 'xe_buyt': '버스', 'di_bo': '도보', 'may_bay': '비행기', 'tau_hoa': '기차',
                  'tau_thuy': '배', 'xe_dap': '자전거'}, 'tuyen': '경로', 'uoc': '실제 도로 기준 예상'},
    'ja': {'ten': '日本語', 'nut': 'チャンネル登録', 'nut_da': '登録済み', 'tieu_de': 'ベトナムを一緒に旅しよう', 'viet_tay': '次の旅でまた会いましょう',
           'thich': '高評価', 'chia_se': '共有', 'chuong_nhan': '通知', 'dan_chuong': '目的地', 'nguon': '写真', 'cam_on': 'ご視聴ありがとうございました',
           'loi_moi': '高評価とチャンネル登録で次の旅もご一緒に！', 'gio': '時間', 'phut': '分',
           'xe': {'o_to': '車', 'xe_may': 'バイク', 'xe_buyt': 'バス', 'di_bo': '徒歩', 'may_bay': '飛行機', 'tau_hoa': '列車',
                  'tau_thuy': '船', 'xe_dap': '自転車'}, 'tuyen': 'ルート', 'uoc': '実際の道路で概算'},
    'zh': {'ten': '中文', 'nut': '订阅', 'nut_da': '已订阅', 'tieu_de': '一起探索越南', 'viet_tay': '下次旅行再见',
           'thich': '点赞', 'chia_se': '分享', 'chuong_nhan': '通知', 'dan_chuong': '目的地', 'nguon': '图片', 'cam_on': '感谢观看',
           'loi_moi': '点赞并订阅，一起开启下一段旅程！', 'gio': '小时', 'phut': '分钟',
           'xe': {'o_to': '汽车', 'xe_may': '摩托车', 'xe_buyt': '大巴', 'di_bo': '步行', 'may_bay': '飞机', 'tau_hoa': '火车',
                  'tau_thuy': '船', 'xe_dap': '自行车'}, 'tuyen': '路线', 'uoc': '按实际道路估算'},
}
KHONG_CACH = ('ja', 'zh', 'th')

# ---- icon hợp lệ cho chip / địa danh / liệt kê (vẽ SVG trong ngang.js) ----
ICON = {'ghim', 'nui', 'bien', 'dao', 'thac', 'may', 'mat_troi', 'trang', 'sao', 'tim', 'may_anh', 'tau', 'tau_hoa', 'cap_treo',
        'xe_may', 'o_to', 'may_bay', 'di_bo', 'co', 'den_long', 'phao_hoa', 'drone', 'hoa', 'la', 'lua', 'ruong', 'chua', 'cau',
        'thanh_pho', 'lich_su', 'dong_ho', 'nhiet_do', 'an_uong', 'ca_phe', 'lap_lanh', 'balo', 'la_ban', 'ban_do', 'nguoi', 'gio',
        'tuyet', 'mua', 'song_nuoc', 'non_la', 'cay', 'tich', 've', 'gia', 'khach_san', 'leu', 'hang'}

LOAI_DH = ('mo_dau', 'hook_tu', 'chuong', 'dia_danh', 'tu_khoa', 'tieu_de', 'chip', 'so_lon', 'liet_ke', 'trich', 'ban_do',
           'hanh_trinh', 'binh_luan')
NHO = ('dia_danh', 'chip', 'binh_luan')   # đồ hoạ nhỏ — được chồng thời gian với 1 đồ hoạ lớn (bình luận: cột phải)


def gio_phut(giay, nn='vi'):
    """giây → '≈ 5 giờ 15 phút' (làm tròn 5 phút dưới 1 giờ, 15 phút từ 1 giờ trở lên) theo chữ của ngôn ngữ."""
    T = NGON_NGU.get(nn, NGON_NGU['en'])
    p = giay / 60
    p = max(5, int(round(p / 5) * 5)) if p < 60 else int(round(p / 15) * 15)
    g, m = divmod(p, 60)
    kc = '' if nn in KHONG_CACH or nn == 'ko' else ' '
    if nn == 'en':
        s = (f'{g} h ' if g else '') + (f'{m} min' if m else '')
    elif g and m:
        s = f"{g}{kc}{T['gio']} {m}{kc}{T['phut']}"
    elif g:
        s = f"{g}{kc}{T['gio']}"
    else:
        s = f"{m}{kc}{T['phut']}"
    return '≈ ' + s.strip()


def so_km(km, nn='vi'):
    if km is None:
        return ''
    s = f'{km:.0f}' if km >= 20 else f'{km:.1f}'
    if nn == 'vi':
        s = s.replace('.', ',')
    return f'{s} km'


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
