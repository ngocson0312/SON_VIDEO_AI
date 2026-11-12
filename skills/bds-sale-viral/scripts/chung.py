# -*- coding: utf-8 -*-
"""bds-sale-viral — HẰNG SỐ PHONG CÁCH (đo từng khung video mẫu Hết Hồn Real, 12/11/2026).

Mọi con số của phong cách nằm ở đây; script khác KHÔNG tự đặt số. Lý do từng số: references/phan-tich-mau.md.
Khung chuẩn 1080x1920 (mẫu 576x970 → nhân 1,875 / 1,98)."""
import os, sys, json, subprocess, math
from functools import lru_cache

W, H, FPS, SR = 1080, 1920, 30, 48000
SKILL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS = os.path.join(SKILL, 'assets')
FONT_DIR = os.path.join(ASSETS, 'fonts')
SFX_DIR = os.path.join(ASSETS, 'sfx')
IMG_EXT = ('.jpg', '.jpeg', '.png', '.webp', '.bmp')
VID_EXT = ('.mp4', '.mov', '.m4v', '.mkv', '.avi')
AUD_EXT = ('.mp3', '.wav', '.m4a', '.aac', '.flac', '.ogg')


# ------------------------------------------------------------------ tiện ích chung
def utf8_stdout():
    for s in (sys.stdout, sys.stderr):
        try: s.reconfigure(encoding='utf-8', errors='replace')
        except Exception: pass


def run(cmd, **kw):
    r = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='replace', **kw)
    if r.returncode != 0:
        raise RuntimeError('Lệnh lỗi: ' + ' '.join(map(str, cmd))[:400] + '\n' + r.stderr[-1500:])
    return r


def probe(path):
    r = run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration:stream=codec_type,width,height,r_frame_rate:stream_tags=rotate',
             '-show_entries', 'stream_side_data=rotation', '-of', 'json', path])
    js = json.loads(r.stdout)
    out = {'dur': float(js.get('format', {}).get('duration', 0) or 0)}
    for s in js.get('streams', []):
        if s.get('codec_type') == 'video' and 'w' not in out:
            w, h = int(s.get('width', 0)), int(s.get('height', 0))
            rot = 0
            try: rot = int(float(s.get('tags', {}).get('rotate', 0)))
            except Exception: pass
            for sd in s.get('side_data_list', []) or []:
                if 'rotation' in sd:
                    try: rot = int(float(sd['rotation']))
                    except Exception: pass
            if abs(rot) in (90, 270): w, h = h, w
            out.update(w=w, h=h)
            try:
                a, b = s.get('r_frame_rate', '30/1').split('/'); out['fps'] = float(a) / float(b)
            except Exception: out['fps'] = 30.0
        if s.get('codec_type') == 'audio': out['audio'] = True
    return out


def doc_json(p):
    with open(p, encoding='utf-8') as f: return json.load(f)


def ghi_json(p, obj):
    with open(p, 'w', encoding='utf-8') as f: json.dump(obj, f, ensure_ascii=False, indent=1)


def font_path(name):
    p = os.path.join(FONT_DIR, name)
    if not os.path.isfile(p): raise FileNotFoundError('Thiếu phông ' + p)
    return p


@lru_cache(maxsize=256)
def font(name, size):
    """Phông biến thiên (Baloo2, DancingScript) mặc định là Regular → tự đặt đúng độ đậm theo tên file."""
    from PIL import ImageFont
    f = ImageFont.truetype(font_path(name), int(size))
    try:
        ten = [n.decode() if isinstance(n, bytes) else n for n in f.get_variation_names()]
    except Exception:
        ten = []
    if ten:
        muon = next((t for t in ('ExtraBold', 'Bold', 'SemiBold', 'Medium') if t.lower() in name.lower()), None)
        if muon is None and 'DancingScript' in name: muon = 'Bold'
        if muon and muon in ten:
            f.set_variation_by_name(muon)
    return f


def clamp(x, a=0.0, b=1.0):
    return a if x < a else (b if x > b else x)


def ease_out(p):        # cubic
    p = clamp(p); return 1 - (1 - p) ** 3


def ease_in(p):
    p = clamp(p); return p ** 3


def ease_io(p):
    p = clamp(p); return 4 * p ** 3 if p < 0.5 else 1 - (-2 * p + 2) ** 3 / 2


def ease_back(p, s=1.9):   # vọt quá rồi về (nảy nhẹ)
    p = clamp(p) - 1; return 1 + (s + 1) * p ** 3 + s * p ** 2


def ease_bounce(p):
    p = clamp(p); n, d = 7.5625, 2.75
    if p < 1 / d: return n * p * p
    if p < 2 / d: p -= 1.5 / d; return n * p * p + 0.75
    if p < 2.5 / d: p -= 2.25 / d; return n * p * p + 0.9375
    p -= 2.625 / d; return n * p * p + 0.984375


def khung(t):  # giây → số khung
    return int(round(t * FPS))


# ------------------------------------------------------------------ PHONG CÁCH (đo từ mẫu)
# Khung hình gốc: phủ kín 1080x1920; mỗi cú NHẢY (jump cut) đổi zoom tức thì 1,0 ↔ 1,15 ↔ 1,3 (mẫu: 0,9 s, 7,45 s, 15,45 s…)
ZOOM = {'muc': [1.0, 1.15, 1.28], 'neo_mat_y': 0.36,     # khi zoom, đặt tâm mặt ở ~36 % chiều cao (đầu không bị cắt)
        'troi': 0.012}                                   # cả cảnh đẩy vào rất chậm +1,2 %/s (mẫu: hình hơi "thở")
MAU_SAC = {'tuong_phan': 1.06, 'bao_hoa': 1.14, 'am': 0.015}   # mẫu ấm, rực hơn nguồn một chút
TOI = {'duoi_tu': 0.66, 'duoi_max': 0.62, 'tren_den': 0.16, 'tren_max': 0.30}  # mép dưới đen dần (sub + UI dễ đọc), mép trên tối nhẹ

# --- TIÊU ĐỀ 3 TẦNG (mỗi câu mở bằng 1 tiêu đề, nằm SAU người — đầu người che chữ) ---
#  dẫn (trắng mảnh, trên-trái)  +  KHOÁ (to, màu gradient / khối 3D)  +  viết tay (trắng, dưới-phải, đè mép dưới khoá)
TIEU_DE = {
    'dan': {'font': 'BeVietnamPro-Medium.ttf', 'co': 66, 'mau': (255, 255, 255)},
    'viet_tay': {'font': 'GreatVibes-Regular.ttf', 'co': 92, 'mau': (255, 255, 255)},
    'viet_tay_co_cho': {'Pacifico.ttf': 64, 'DancingScript.ttf': 84, 'GreatVibes-Regular.ttf': 92},
    'khoa_co': 205,            # cỡ gốc; tự thu cho vừa 'khoa_rong'
    'khoa_rong': 0.84 * W,     # khoá rộng tối đa (mẫu 0,75–0,82 W)
    'khoa_cao_min': 120,       # chữ khoá không bao giờ thấp hơn (đọc được trên điện thoại)
    'y_min': 150,              # đỉnh khối không cao hơn (mép trên app)
    'day_tren_dau': 0.30,      # đáy chữ KHOÁ = đỉnh đầu + 0,30 × cao mặt  ⇒ đầu che 1 phần chữ (chữ sau đầu)
    'dau_tren_mat': 0.22,      # chưa có mặt nạ người: đỉnh đầu ≈ đỉnh hộp mặt − 0,22 × cao mặt (tóc)
    'de_khoa_min': 0.30,       # người đứng xa (mặt nhỏ): đầu vẫn che ≥ 30 % chiều cao khoá (mẫu: đầu luôn đè phần dưới chữ)
    'dan_de': 0.22,            # dòng dẫn đè 22 % lên đỉnh khoá
    'viet_tay_de': 0.42,       # viết tay đè 42 % lên đáy khoá
    'tho': 0.035,              # cả khối phóng chậm 1 → 1,035 suốt thời gian hiện ("thở")
    'vao_khung': 10, 'ra_khung': 7, 'dan_vao_khung': 6,
}
# kiểu màu khoá — luân phiên, 2 tiêu đề liền nhau không trùng kiểu
KIEU_KHOA = {
    'cam':  {'font': 'Anton-Regular.ttf', 'hoa': True, 'grad': [(255, 255, 255), (255, 206, 178), (238, 104, 62)],
             'khoi': None, 'vien': None, 'nghieng': 0.0, 'gian': 0},          # TÌM MUA
    'tim':  {'font': 'Montserrat-Black.ttf', 'hoa': True, 'grad': [(238, 224, 255), (176, 112, 255), (112, 40, 226)],
             'khoi': (62, 14, 140), 'khoi_px': 9, 'vien': None, 'nghieng': 0.0, 'gian': -2},  # CHO BẠN / QUAN TRỌNG
    'nau':  {'font': 'Baloo2-ExtraBold.ttf', 'hoa': False, 'grad': [(255, 248, 232), (238, 182, 112), (178, 102, 44)],
             'khoi': (92, 46, 16), 'khoi_px': 11, 'vien': None, 'nghieng': 0.0, 'gian': 0},  # Thông Tin / Khiến bạn
    'vang': {'font': 'Anton-Regular.ttf', 'hoa': True, 'grad': [(255, 248, 120), (255, 232, 30), (246, 196, 0)],
             'khoi': None, 'vien': None, 'nghieng': 0.0, 'gian': 0},          # TÀI SẢN LỚN
    'cam_nghieng': {'font': 'Montserrat-BoldItalic.ttf', 'hoa': False, 'grad': [(255, 252, 238), (255, 196, 92), (232, 122, 26)],
             'khoi': (120, 52, 8), 'khoi_px': 6, 'vien': None, 'nghieng': 0.0, 'gian': -2},  # Lý do
}
KIEU_XOAY = ['cam', 'tim', 'nau', 'tim', 'cam_nghieng', 'vang', 'nau']
TIEU_DE_VAO = ['roi', 'phong', 'truot', 'tu_dau']        # rơi từ trên · lớn dần từ nhỏ · trượt từ trái (loé trắng) · mọc ra từ sau đầu
TIEU_DE_RA = ['chui_dau', 'troi_xuong', 'vo_chu']        # thu nhỏ chui vào sau đầu · trôi xuống mờ · vỡ từng chữ rơi

# --- SUB (cụm 1–4 chữ ở NGỰC người nói, trắng đậm, đổi cụm bằng ĐẨY NGANG) ---
SUB = {
    'chinh': {'font': 'Montserrat-Bold.ttf', 'co': 64, 'mau': (255, 255, 255)},
    'phu': {'font': 'Montserrat-SemiBoldItalic.ttf', 'co': 54, 'mau': (255, 255, 255)},      # dòng 2 nghiêng nhạt hơn
    'to': {'font': 'Montserrat-ExtraBold.ttf', 'co': 128, 'mau': (255, 255, 255)},           # 1 chữ nhấn ("Sale")
    'vang': {'font': 'Montserrat-BoldItalic.ttf', 'co': 70, 'grad': [(255, 226, 120), (240, 170, 30), (196, 120, 10)]},  # "Người tư vấn"
    'nhan': {'mau': (232, 22, 92), 'font': 'Montserrat-BoldItalic.ttf'},                     # [50m²] [1 tỷ] "[VỊ TRÍ]"
    'list': {'font': 'BeVietnamPro-Medium.ttf', 'co': 50, 'mau': (255, 255, 255)},
    'rong_max': 0.86 * W,
    'gian_dong': 0.88,         # dòng 2 sát dòng 1 (mẫu chồng nhẹ)
    'y_mat': 3.4,              # tâm khối sub = tâm mặt + 3,4 × cao mặt …
    'y_min': 0.49 * H, 'y_max': 0.69 * H,     # … kẹp trong dải ngực (mẫu 0,50–0,67 H)
    'x_min': 330, 'x_max': W - 330,           # tâm ngang bám người nói, kẹp
    'day_khung': 4, 'day_px': 230,            # ĐẨY NGANG: cụm mới vào từ 1 bên 230 px, cụm cũ ra bên kia, 4 khung, nhoè chuyển động
    'nhoe_khung': 5,                          # vào kiểu nhoè: nhoè 9 px → nét, phóng 1,12 → 1
    'bat_khung': 6,                           # chữ 'to' bật 0,55 → 1,08 → 1
    'bong': {'dx': 0, 'dy': 4, 'mo': 9, 'alpha': 0.62}, 'vien_px': 2,
}

# --- ĐỒ HOẠ PHỤ ---
THE_ANH = {'bo': 22, 'vien': 5, 'rong': 640, 'rong_tay': 420, 'rong_nho': 470, 'nho_ty_le': 1.5,   # ảnh nhỏ: cắt NGANG 3:2, ~0,45 W, sát mép trên
            'vao_khung': 9, 'ra_khung': 6,
           'nghieng_do': 22, 'xep_lech': (46, -30), 'bong_alpha': 0.55}
ICON = {'co': 175, 'nhan_co': 34, 'vao_khung': 8, 'nhun': 10,   # nhún lên xuống 10 px chu kỳ 1,6 s
        'mau': {'vi_tri': (150, 70, 250), 'truong_hoc': (40, 200, 110), 'tien_ich': (40, 200, 110), 'nha': (255, 140, 40),
                'tien': (250, 196, 30), 'cong_vien': (60, 190, 80), 'benh_vien': (235, 60, 70), 'mua_sam': (255, 90, 160),
                'sao': (255, 200, 40), 'giao_thong': (40, 150, 255), 'phong_ngu': (90, 120, 255),
                'binh_luan': (40, 170, 255), 'ho_nuoc': (30, 180, 230), 'tim': (240, 60, 110), 'chia_khoa': (250, 176, 30)},
        # trên TAY (mẫu ic_a/ic_b): mọc từ lòng bàn tay 0,12→nảy→1 trong 6 khung, đáy nhãn ngay trên lòng bàn tay
        'tay_vao_khung': 6, 'tay_tu': 0.12, 'tay_tren': 14, 'tay_nhun': 4, 'tay_bam': 0.6}   # bám 60 % chuyển động tay
# DÒ TAY (tay.py). MediaPipe (venv riêng): tay RẢNH = KHÔNG sát miệng (cầm mic: < mieng × cao mặt), lòng bàn tay trong
# [doc] × cao mặt dưới tâm mặt, không buông thõng (ngón chúc xuống dưới `buong`) — icon mọc được từ tay rảnh; tay XOÈ
# (≥ mo_min ngón duỗi) hoặc DANG (cách tâm mặt ≥ ngang_min × cao mặt) = nhịp đẹp nhất để icon bật ra.
# Dự phòng mặt nạ người: bang / nguong / nho / vao_long (chỉ bắt dang tay).
# Đoạn ≥ min_s, gộp khe ≤ lap_s; icon / thẻ ăn theo cử chỉ trong [t0 − truoc_s, t0 + sau_s].
# Icon gợi ý (từ khoá ICON_TU trùng lúc tay làm cử chỉ): cách nhau ≥ goi_y_cach s cùng tay, dài goi_y_dai s.
TAY = {'mp_buoc': 2, 'mieng': 1.3, 'doc': (0.4, 6.5), 'buong': 4.2, 'mo_min': 3, 'ngang_min': 1.4,
       'bang': (1.0, 5.5), 'nguong': 2.0, 'nho': 0.45, 'vao_long': 0.25,
       'min_s': 0.35, 'lap_s': 0.25, 'truoc_s': 0.4, 'sau_s': 0.6, 'goi_y_cach': 1.8, 'goi_y_min': 1.0, 'goi_y_dai': (1.0, 1.8),
       'trong_s': 6.0}   # kiem-kh: tay rảnh ≥ trong_s giây liền mà không icon / thẻ nào trên tay → ⚠
# từ khoá trong lời → loại icon (khớp không dấu, cụm dài trước). Nhãn icon = chính chữ trong lời; Claude sửa theo nghĩa.
ICON_TU = {
    'vi_tri': ['vị trí', 'toạ lạc', 'tọa lạc', 'nằm ngay', 'nằm ở', 'trung tâm', 'mặt tiền', 'kết nối'],
    'tien_ich': ['tiện ích', 'dịch vụ', 'nội khu', 'hồ bơi', 'bể bơi', 'gym', 'clubhouse', 'spa'],
    'truong_hoc': ['trường học', 'trường', 'giáo dục', 'mầm non', 'học'],
    'benh_vien': ['bệnh viện', 'y tế', 'phòng khám', 'vinmec'],
    'cong_vien': ['công viên', 'cây xanh', 'sân golf', 'golf', 'thể thao', 'sport', 'vườn', 'chạy bộ'],
    'ho_nuoc': ['view', 'mặt nước', 'du thuyền', 'marina', 'thuỷ cung', 'thủy cung', 'đại dương', 'hồ', 'sông', 'biển', 'vịnh',
                'hoàng hôn'],
    'giao_thong': ['cao tốc', 'vành đai', 'sân bay', 'metro', 'di chuyển', 'đường', 'cầu', 'phút'],
    'mua_sam': ['trung tâm thương mại', 'mua sắm', 'siêu thị', 'vincom', 'aeon', 'ẩm thực', 'nhà hàng'],
    'tien': ['thanh toán', 'chiết khấu', 'ưu đãi', 'đầu tư', 'giá', 'tỷ', 'tỉ', 'triệu', 'tiền'],
    'phong_ngu': ['phòng ngủ', 'ngủ'],
    'nha': ['căn hộ', 'biệt thự', 'shophouse', 'tổ ấm', 'ngôi nhà', 'căn', 'nhà'],
    'chia_khoa': ['sở hữu', 'nhận nhà', 'bàn giao', 'sổ hồng', 'pháp lý'],
    'binh_luan': ['bình luận', 'comment', 'inbox', 'nhắn tin', 'liên hệ'],
    'tim': ['tận hưởng', 'trải nghiệm', 'hạnh phúc', 'yêu thích', 'thăng hoa', 'kỳ nghỉ', 'đam mê', 'âm nhạc'],
    'sao': ['thế giới', 'quốc tế', 'đẳng cấp', 'sang trọng', 'cao cấp', 'đặc biệt', 'nổi bật', 'khám phá', 'sự kiện',
            'chinh phục', 'sức hút'],
}
TIM_KIEM = {'rong': 900, 'cao': 104, 'co': 46, 'font': 'BeVietnamPro-Medium.ttf', 'ky_tu_khung': 1.0,
            'vao_khung': 6, 'ra_khung': 5}
SO_TIEN = {'font': 'Anton-Regular.ttf', 'co': 168, 'grad': [(255, 252, 150), (255, 228, 20), (236, 168, 0)],
           'vet_khung': 3, 'vao_khung': 5, 'rong_max': 0.90 * W}
LOGO = {'rong': 0.86 * W, 'y': 70, 'vao_khung': 12}
LIET_KE = {'khoa_co': 230, 'khoa_rong': 0.44, 'gian_dong': 1.12, 'dong_co': 52, 'toi_da': 3, 'vao_khung': 6}   # mẫu: 'Là' ~0,26 W, cao ~0,10 H
VONG_VE = {'mau': (246, 168, 34), 'day': 7, 'khung': 10}

# --- CHUYỂN CẢNH (ở chỗ đổi BỐI CẢNH; nhảy cùng bối cảnh = cắt + đổi zoom, không hiệu ứng) ---
CHUYEN = {
    'zoom_nhoe': {'truoc': 4, 'sau': 5, 'phong': 0.38},           # 10,1 s · 27,47 s
    'loe_doc':   {'truoc': 4, 'sau': 5},                           # 23,5 s: tia sáng dọc quét ngang
    'chay_phim': {'truoc': 3, 'sau': 4},                           # 33,3 s: cháy phim cam → trắng → đỏ
    'tach_mau':  {'truoc': 3, 'sau': 4, 'lech': 26},               # 38,2 s: tách RGB + nhoè + rung
}
CHUYEN_XOAY = ['zoom_nhoe', 'loe_doc', 'zoom_nhoe', 'chay_phim', 'tach_mau']

# --- ÂM THANH ---
AM = {'lufs': -14.0, 'tp': -2.0, 'nhac_duoi_giong_db': 9.0, 'nhac_khe_db': 3.0}   # mẫu: nhạc beat ~93 BPM thấp hơn giọng ~9 dB
# tp −2,0 (không phải −1,5): mã hoá AAC đẩy đỉnh lên ~0,5 dB, tự kiểm đòi ≤ −1 dBTP trên FILE CUỐI
SFX_NHOM = {   # loại sự kiện → biến thể (xoay vòng, chọn file ít dùng nhất)
    'tieu_de': ['whoosh-short.mp3', 'quick-swoosh.mp3', 'swoosh.mp3'],
    'tieu_de_dap': ['sparkle.mp3', 'quick-ting.mp3', 'fairy-dust.mp3'],
    'tieu_de_ra': ['swoosh.mp3', 'quick-swoosh.mp3'],
    'sub_to': ['pop.mp3', 'pop-2.mp3'],
    'sub_nhan': ['quick-ting.mp3', 'click-button.mp3', 'pop-2.mp3'],
    'the_anh': ['new-item.wav', 'pop.mp3', 'swoosh.mp3'],
    'icon': ['pop-2.mp3', 'click-button.mp3', 'pop.mp3'],
    'tim_kiem': ['quick-swoosh.mp3', 'whoosh-short.mp3'],
    'go_phim': ['iphone-typing.mp3'],
    'so_tien': ['ka-ching.mp3', 'money.mp3'],
    'logo': ['ding.mp3', 'ting.wav'],
    'liet_ke': ['click-button.mp3', 'mouse-click.mp3'],
    'vong_ve': ['quick-swoosh.mp3', 'swoosh.mp3'],
    'zoom_nhoe': ['whoosh.wav', 'whoosh-short.mp3'],
    'loe_doc': ['camera-flash-1.wav', 'whoosh.wav'],
    'chay_phim': ['whoosh.wav', 'take-off.mp3'],
    'tach_mau': ['swoosh.mp3', 'punch.mp3'],
    'riser': ['riser-metallic.mp3'],
}
# độ to so với giọng TẠI CHỖ (dB, đỉnh 10 ms của SFX so trung vị RMS giọng) — mẫu: SFX rõ nhưng không át lời
SFX_TO = {'zoom_nhoe': 4, 'loe_doc': 4, 'chay_phim': 4, 'tach_mau': 3, 'riser': 1, 'tieu_de': 2, 'tieu_de_dap': 0,
          'tieu_de_ra': -1, 'sub_to': 0, 'sub_nhan': -2, 'the_anh': 1, 'icon': 0, 'tim_kiem': 1, 'go_phim': -9,
          'so_tien': 1, 'logo': 1, 'liet_ke': -3, 'vong_ve': -1}
SFX_UU_TIEN = ['zoom_nhoe', 'loe_doc', 'chay_phim', 'tach_mau', 'tieu_de', 'so_tien', 'logo', 'the_anh', 'icon',
               'tim_kiem', 'sub_to', 'tieu_de_dap', 'vong_ve', 'sub_nhan', 'liet_ke', 'tieu_de_ra', 'riser', 'go_phim']
SFX_CUA_SO = 0.30          # trong 0,30 s chỉ 1 tiếng (giữ tiếng ưu tiên cao)
SFX_PHU = {'sub_nhan', 'liet_ke', 'tieu_de_dap', 'tieu_de_ra', 'vong_ve', 'sub_to'}
SFX_CUA_SO_PHU = 0.70      # nhóm phụ phải cách mọi tiếng khác ≥ 0,7 s (mẫu ~1 tiếng / 2 s, không dày)
SFX_KHONG_LAP_S = 4.0      # cùng 1 file không lặp trong 4 s
SFX_DAI_MAX = {'whoosh.wav': 1.3, 'iphone-typing.mp3': 3.0, 'ding.mp3': 1.4, 'ting.wav': 1.4, 'new-item.wav': 1.2,
               'mouse-click.mp3': 0.4, 'ka-ching.mp3': 1.6, 'money.mp3': 1.6, 'riser-metallic.mp3': 1.6,
               'take-off.mp3': 1.4, 'camera-flash-1.wav': 1.0, 'fairy-dust.mp3': 1.4}

# --- VÙNG AN TOÀN (UI TikTok / Reels che đáy + cột phải) ---
AN_TOAN = {'x0': 36, 'x1': W - 36, 'y0': 120, 'y1': 1660}

# --- CẮT LẶNG (video quay thô; video đã dựng sẵn thì tắt) — giữ hơi thở như skill_video_bds_bietthu L6 ---
CAT_LANG = {'nguong_db': 8.0, 'khe_toi_da': 0.40, 'giu_lai': 0.24, 'giu_dau_cuoi': 0.12}

# --- TÁCH NGƯỜI (u2net_human_seg) để tiêu đề + logo nằm SAU người ---
NGUOI = {'model_tim': [os.path.join(ASSETS, 'models', 'u2net_human_seg.onnx'),
                       os.path.join(os.path.expanduser('~'), '.u2net', 'u2net_human_seg.onnx')],
         'nguong': (0.30, 0.70), 'mem': 1.6, 'no': 9, 'buoc': 2}   # tính mặt nạ mỗi 2 khung, nội suy giữa
# MẶT bằng MediaPipe (tay.do_mat, venv riêng): mẫu mỗi 3 khung; hộp đầu từ Pose = vuông cạnh 0,89 × (mũi–giữa vai), tâm
# ở mũi (đo ONE ERA 983 mẫu: FaceDetection vuông, cao 0,71–1,05 × mũi–vai, tâm lệch mũi ≤ 0,2 cạnh); FD cách hộp Pose
# > 1 cạnh = mặt người khác phía sau → bỏ
MAT_MP = {'buoc': 3, 'dau_canh': 0.89, 'dau_dy': -0.02, 'vis_vai': 0.3, 'vis_mui': 0.3, 'fd_lech': 1.0}
# VÙNG MẶT CẤM CHỮ (người dùng chốt 12/11/2026: "text không được đè vào mặt diễn giả đang nói"): hộp mặt nới
# ngang `ngang` × cạnh mỗi bên, lên `tren` (trán + tóc), xuống `duoi` (cằm). Mọi chữ / icon / thẻ ở LỚP TRƯỚC người
# (dẫn, viết tay, khoá kiểu giữa, sub, icon, nhãn, thẻ ảnh, ô tìm kiếm, số tiền, liệt kê) không được chạm vùng này ở
# BẤT KỲ khung nào (khoá sau đầu thì được — đầu nằm trước chữ). Tự kiểm mục 5 quét mọi khung, chạm ⇒ ⛔.
MAT_CAM = {'ngang': 0.12, 'tren': 0.30, 'duoi': 0.15, 'cham_px2': 150}


def tim_model_mat():
    cands = [os.path.join(ASSETS, 'models', 'det_10g.onnx'),
             os.path.join(os.path.expanduser('~'), '.insightface', 'models', 'buffalo_l', 'det_10g.onnx')]
    for base in (os.path.dirname(SKILL), os.path.join(os.path.dirname(SKILL), '..', '..', '.claude', 'skills')):
        cands.append(os.path.join(base, 'nns-edit-bds', 'assets', 'models', 'det_10g.onnx'))
    return next((p for p in cands if os.path.isfile(p)), None)


def sfx_path(name):
    return name if os.path.isabs(name) else os.path.join(SFX_DIR, name)
