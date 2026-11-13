# -*- coding: utf-8 -*-
"""chung.py — hằng số phong cách + tiện ích dùng chung cho skill TuấnJp_Dulich_ManDoc.

Mọi con số PHONG CÁCH nằm ở đây và trong assets/khung/dulich.css|js. Muốn đổi kiểu → sửa ở đây, đừng rải số ra file khác.
"""
import difflib
import hashlib
import json
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
FONT_DIR = ASSETS / 'fonts'
KHUNG = ASSETS / 'khung'

W, H, FPS = 1080, 1920, 30
DUOI = 0.9              # giữ hình sau tiếng cuối (giây) — CTA cần thời gian bấm nút
LUFS, TP = -14.0, -1.0

VIDEO_EXT = {'.mp4', '.mov', '.m4v', '.mkv', '.avi', '.webm', '.3gp', '.mts', '.m2ts', '.ts', '.wmv', '.flv', '.mpg', '.mpeg'}
IMG_EXT = {'.jpg', '.jpeg', '.jfif', '.png', '.webp', '.bmp', '.gif', '.tif', '.tiff', '.avif', '.heic', '.heif'}
AUDIO_EXT = {'.m4a', '.mp3', '.wav', '.aac', '.flac', '.ogg', '.opus'}

# ---- vùng an toàn khung dọc (né giao diện TikTok / Reels / Shorts) ----
AN_TOAN = {'tren': 150, 'duoi': 1640, 'trai': 60, 'phai': 940}
SUB_Y = 1405            # tâm dòng sub (px) — trên vùng chữ mô tả của app
SUB_RONG = 900          # bề rộng tối đa khối sub
SUB_MAX_KY_TU = 30      # ký tự / dòng (Latin) — CJK tự chia đôi
SUB_MAX_TU = 8          # từ / cụm (Latin)
SUB_NGAT = 0.38         # khoảng lặng ≥ này giữa 2 từ ⇒ ngắt cụm

# ---- chuyển cảnh: tên → (thời lượng giây, SFX) ----
CHUYEN = {
    'cat':      (0.00, None),
    'hoa_tan':  (0.45, None),
    'nhoe':     (0.50, 'nhoe'),
    'lia':      (0.36, 'lia'),        # lia nhoè ngang (whip pan)
    'lia_doc':  (0.36, 'lia'),
    'zoom':     (0.42, 'zoom'),       # zoom xuyên
    'loe':      (0.55, 'loe'),        # loé sáng ánh nắng (light leak)
    'truot':    (0.40, 'lia'),        # đẩy cảnh lên
}

# ---- SFX: sự kiện → (file, dB so với đỉnh −1 dBFS, lệch giây so với mốc) ----
SFX = {
    'lia':       ('whoosh-short.mp3', -12, -0.10),
    'zoom':      ('swoosh.mp3', -11, -0.12),
    'nhoe':      ('quick-swoosh.mp3', -15, -0.05),
    'loe':       ('fairy-dust.mp3', -17, -0.05),
    'mo_dau':    ('whoosh.wav', -13, -0.05),
    'lap_lanh':  ('sparkle.mp3', -15, 0.0),
    'chuong':    ('swoosh.mp3', -12, -0.02),
    'chuong_so': ('ding.mp3', -17, 0.30),
    'ghim':      ('pop.mp3', -11, 0.22),
    'chip':      ('pop-2.mp3', -11, 0.05),
    'tu_khoa':   ('quick-swoosh.mp3', -15, 0.0),
    'so_lon':    ('riser-metallic.mp3', -18, 0.0),
    'so_xong':   ('ding.mp3', -15, 0.0),
    'the_anh':   ('camera-shutter.mp3', -12, 0.05),
    'liet_ke':   ('pop.mp3', -12, 0.05),
    'trich':     ('quick-swoosh.mp3', -14, 0.0),
    'cta_vao':   ('swoosh.mp3', -12, 0.0),
    'bam':       ('click-button.mp3', -7, 0.0),
    'tim':       ('pop.mp3', -9, 0.0),
    'icon':      ('pop-2.mp3', -12, 0.0),
    # hành trình (điểm đi → điểm đến): tiếng phương tiện tự tổng hợp (assets/sfx/CREDITS.md)
    'ht_vao':    ('whoosh.wav', -13, -0.05),
    'ht_den':    ('ding.mp3', -15, 0.0),
    'ht_tg':     ('pop.mp3', -13, 0.0),
    'ht_may_bay': ('jet-flyby.wav', -15, -0.3),
    'ht_xe':     ('xe-chay.wav', -17, -0.2),
    'ht_song':   ('song-nuoc.wav', -18, 0.0),
}
# ---- hành trình: phương tiện → nền tự vẽ mặc định; nhãn theo ngôn ngữ (dòng dẫn, tên phương tiện, khoảng cách) ----
PHUONG_TIEN = ('may_bay', 'o_to', 'xe_may', 'xe_buyt', 'xe_dap', 'tau_hoa', 'tau_thuy', 'di_bo', 'khong')
NEN_HT = ('troi', 'duong', 'bien', 'ban_do', 'canh')
NEN_PT = {'may_bay': 'troi', 'o_to': 'duong', 'xe_may': 'duong', 'xe_buyt': 'duong', 'xe_dap': 'duong', 'tau_hoa': 'duong',
          'tau_thuy': 'bien', 'di_bo': 'ban_do', 'khong': 'ban_do'}
_PT8 = ('may_bay', 'o_to', 'xe_may', 'xe_buyt', 'xe_dap', 'tau_hoa', 'tau_thuy', 'di_bo')
HANH_TRINH_NN = {   # nn: (dòng dẫn, nhãn khoảng cách, nhãn 8 phương tiện theo thứ tự _PT8)
    'vi': ('Hành trình', 'Khoảng cách', ('Máy bay', 'Ô tô', 'Xe máy', 'Xe khách', 'Xe đạp', 'Tàu hỏa', 'Du thuyền', 'Đi bộ')),
    'en': ('Journey', 'Distance', ('By plane', 'By car', 'By motorbike', 'By bus', 'By bike', 'By train', 'By boat', 'On foot')),
    'fr': ('Itinéraire', 'Distance', ('En avion', 'En voiture', 'En moto', 'En bus', 'À vélo', 'En train', 'En bateau', 'À pied')),
    'de': ('Reiseroute', 'Entfernung', ('Flugzeug', 'Auto', 'Motorrad', 'Bus', 'Fahrrad', 'Zug', 'Schiff', 'Zu Fuß')),
    'es': ('Itinerario', 'Distancia', ('En avión', 'En coche', 'En moto', 'En autobús', 'En bici', 'En tren', 'En barco', 'A pie')),
    'it': ('Itinerario', 'Distanza', ('In aereo', 'In auto', 'In moto', 'In autobus', 'In bici', 'In treno', 'In barca', 'A piedi')),
    'pt': ('Roteiro', 'Distância', ('De avião', 'De carro', 'De moto', 'De ônibus', 'De bicicleta', 'De trem', 'De barco', 'A pé')),
    'id': ('Perjalanan', 'Jarak', ('Pesawat', 'Mobil', 'Motor', 'Bus', 'Sepeda', 'Kereta', 'Kapal', 'Jalan kaki')),
    'ja': ('旅程', '距離', ('飛行機', '車', 'バイク', 'バス', '自転車', '電車', '船', '徒歩')),
    'ko': ('여정', '거리', ('비행기', '자동차', '오토바이', '버스', '자전거', '기차', '배', '도보')),
    'zh': ('行程', '距离', ('飞机', '汽车', '摩托车', '巴士', '自行车', '火车', '游船', '步行')),
    'th': ('การเดินทาง', 'ระยะทาง', ('เครื่องบิน', 'รถยนต์', 'มอเตอร์ไซค์', 'รถบัส', 'จักรยาน', 'รถไฟ', 'เรือ', 'เดินเท้า')),
    'ru': ('Маршрут', 'Расстояние', ('Самолётом', 'На машине', 'На мотоцикле', 'На автобусе', 'На велосипеде', 'Поездом', 'На корабле', 'Пешком')),
}


def nhan_ht(nn):
    """→ (dòng dẫn, nhãn khoảng cách, {phương tiện: nhãn}) theo ngôn ngữ; ngôn ngữ chưa có → None (Claude phải tự ghi chữ)."""
    v = HANH_TRINH_NN.get(nn)
    return (v[0], v[1], dict(zip(_PT8, v[2]))) if v else None


# ---- tự dò câu nói DI CHUYỂN A → B (số + đơn vị quãng đường / thời gian + từ di chuyển) → nhắc làm đồ hoạ hanh_trinh ----
_HT_LAT = r'(?<![0-9a-zà-ɏḀ-ỿа-яё])'      # trước số: không dính chữ Latin / Việt / Kirin (CJK, Hàn, Thái thì được dính)
_HT_SO = (r'(?:' + _HT_LAT + r'(?:\d+(?:\s?[.,]\s?\d+)?(?:\s*[-–—~]\s*\d+(?:[.,]\d+)?)?|một|hai|ba|bốn|năm|sáu|bảy|tám|chín|mười|vài|mấy|nửa|'
          r'one|two|three|four|five|six|seven|eight|nine|ten|fifteen|twenty|thirty|forty|fifty|half an?|an?|a few)'
          r'(?:\s+and\s+a\s+half)?|[一二三四五六七八九十百半两兩]+(?:个|個)?半?|(?<![가-힣])(?:한|두|세|네|다섯|여섯|일곱|여덟|아홉|열))\s*-?')
_HT_KC = (r'(?:km\b|cây số|ki-?lô-?mét|kilomet\w*|kilometr\w*|miles?\b|公里|キロ|킬로미터?|กิโลเมตร|км\b|километр\w*)')
_HT_M = r'(?:mét\b|m\b|meters?\b|metres?\b|米|メートル|미터|เมตร|метр\w*)'
_HT_TG = (r'(?:tiếng|giờ|phút|h\b|hours?\b|hrs?\b|minutes?\b|mins?\b|heures?\b|stunden?\b|minuten\b|horas?\b|minutos?\b|ore\b|'
          r'minuti\b|jam\b|menit\b|時間|分|小时|小時|分钟|시간|분|ชั่วโมง|นาที|час\w*|минут\w*)')
# từ di chuyển: MẠNH (đủ cho cả thời gian) / RỘNG (chỉ đủ cho quãng đường)
_HT_DI_MANH = (r'\b(?:bay|chuyến bay|di chuyển|lái xe|đi xe|đi bộ|đi tàu|đi thuyền|chạy xe|hành trình|lộ trình|quãng đường|'
               r'đường đi|chuyến đi|khởi hành|xuất phát|hạ cánh|cất cánh|ô tô|taxi|xe máy|xe buýt|xe khách|tàu|thuyền|phà|cách|mất|'
               r'fly|flight|flying|drive|driving|ride|train|bus|ferry|boat|cruise|walk|walking|travel|journey|trip|away|'
               r'vol|vole|voiture|trajet|flug|fahrt|fahren|vuelo|viaje|volo|viaggio|voo|viagem|terbang|perjalanan|'
               r'езд\w*|лет\w*|перел\w*|пут\w*)\b|飛行|フライト|移動|飞|航班|车程|路程|비행|이동|차로|บิน|เดินทาง')
_HT_DI_RONG = _HT_DI_MANH + r'|かかり|かかる|걸립|걸려|需要|大约' + r'|\b(?:đi|đến|tới|về|ra|từ|from|to|reach|à|nach|zu|hasta|desde|da|até|ke|dari)\b|から|まで|从|到|에서|까지'
_HT_GIO_DONG_HO = r'(?:\b(?:lúc|từ|đến|tới|vào|tầm)\s+\d+\s*(?:giờ|h)\b|\d+\s*(?:giờ|h)\s*(?:sáng|trưa|chiều|tối|đêm)|\d+\s*h\s*\d+)'
_HT_XE = (   # thứ tự quan trọng: xe cụ thể trước xe chung ('自転車' trước '車', 'motorbike' trước 'bike')
    ('may_bay', r'máy bay|chuyến bay|\bbay\b|hạ cánh|cất cánh|\b(?:flight|fly|flying|plane|airplane|avion|flug|flugzeug|vuelo|avión|'
                r'aereo|volo|avião|voo|pesawat|terbang)\b|飛行機|フライト|飞机|航班|비행기|เครื่องบิน|самол'),
    ('tau_hoa', r'tàu h[oỏ]a|tàu hoả|tàu điện|đường sắt|\b(?:train|railway|métro|metro|zug|tren|treno|trem|kereta)\b|電車|新幹線|列车|火车|高铁|'
                r'기차|열차|รถไฟ|поезд'),
    ('tau_thuy', r'du thuyền|thuyền|\bphà\b|tàu thủy|tàu thuỷ|ca nô|\b(?:boat|ferry|cruise|ship|bateau|barco|barca|nave|kapal|perahu)\b|'
                 r'船|フェリー|游船|渡轮|เรือ|паром|корабл|лодк'),
    ('xe_buyt', r'xe buýt|xe bus|xe khách|limousine|\b(?:bus|coach|autobus|autobús|ônibus|bis)\b|バス|巴士|公交|大巴|버스|รถบัส|автобус'),
    ('xe_may', r'xe máy|xe mô tô|\b(?:motorbike|motorcycle|scooter|moto|motorrad|motor)\b|バイク|摩托|오토바이|มอเตอร์ไซค์|мотоцикл'),
    ('xe_dap', r'xe đạp|\b(?:bicycle|bike|cycling|vélo|fahrrad|bici|bicicleta|sepeda)\b|自転車|自行车|자전거|จักรยาน|велосипед'),
    ('o_to', r'ô tô|ôtô|xe hơi|taxi|\bgrab\b|lái xe|开车|打车|坐车|车程|\b(?:car|drive|driving|voiture|auto|coche|carro|mobil)\b|車|汽车|자동차|รถยนต์|машин'),
    ('di_bo', r'đi bộ|tản bộ|\b(?:walk|walking|on foot|à pied|zu fuß|a pie|a piedi|a pé|jalan kaki)\b|徒歩|歩いて|步行|도보|걸어|เดิน|пешком'),
)


def cau_di_chuyen(cau, nn=None):
    """Câu nào nói DI CHUYỂN (có số + km / phút / tiếng… + từ di chuyển) → [{'s','e','text','pt' (đoán, có thể None),'kc','tg','cum'}].
    Chỉ là dò tự động để NHẮC (⚠) — giờ mở cửa 'từ 8 giờ', 'bãi biển dài 5 km'… đã loại phần lớn, còn sót thì Claude tự bỏ qua."""
    ra = []
    for c in cau or []:
        t = ' ' + str(c.get('text', '')).lower() + ' '
        if nn and nn != 'vi':
            t = re.sub(r'\bbay\b', ' ', t)                               # 'bay' = vịnh ở tiếng khác; chỉ tiếng Việt 'bay' mới là bay (máy bay)
        t2 = re.sub(_HT_GIO_DONG_HO, ' ', t)                               # bỏ giờ đồng hồ (giờ mở cửa…)
        t3 = re.sub(r'sân bay|airport|aéroport|flughafen|aeropuerto|aeroporto|bandara|空港|机场|공항|สนามบิน|аэропорт', ' ', t2)
        pt = next((k for k, rx in _HT_XE if re.search(rx, t3)), None)
        manh = pt is not None or re.search(_HT_DI_MANH, t2) is not None
        rong = manh or re.search(_HT_DI_RONG, t2) is not None
        kc = [m.group(0).strip() for m in re.finditer(rf'{_HT_SO}\s*{_HT_KC}', t2)] if rong else []
        kc += [m.group(0).strip() for m in re.finditer(rf'{_HT_SO}\s*{_HT_M}', t2)] if manh else []
        tg = [m.group(0).strip() for m in re.finditer(rf'{_HT_SO}\s*{_HT_TG}(?:\s*rưỡi)?', t2)] if manh else []
        if not (kc or tg):
            continue
        ra.append({'s': c['s'], 'e': c['e'], 'text': c.get('text', ''), 'pt': pt, 'kc': bool(kc), 'tg': bool(tg), 'cum': kc + tg})
    return ra
NHAC_MUC = -14.0        # nhạc nền dưới giọng (dB so với giọng, cả bài) — người dùng 13/11/2026: −18 "hơi bé" → −14
NHAC_DANG = 8.0         # nhạc dâng thêm ở khoảng lặng lời ≥ 1 s
NHAC_SAN = 5.0          # san bằng: đoạn nhạc nhỏ (intro / outro / bridge) được nâng tối đa chừng này dB cho nghe rõ suốt video
NHAC_LUI_MAX = 45.0     # nhạc dài hơn video ≤ chừng này giây → bỏ bớt ĐẦU để nốt kết của nhạc trùng cuối video
# tên file nhạc nền trong Resources (tự nhận): Music_Bg.mp3, bgm.mp3, nhac_nen.m4a, beat.wav, soundtrack…
NHAC_TEN = r'(music|background|nhac|nhạc|bgm|(^|[^a-z])bg([^a-z]|$)|beat|soundtrack|song|melody|nen|nền|instrumental|audio_?bg)'

# ---- NGÔN NGỮ: mọi chữ trên hình PHẢI cùng ngôn ngữ với audio (quy chuẩn skill) ----
NGON_NGU = {
    'vi': {'ten': 'Tiếng Việt', 'chu_viet': 'latin_vi', 'nut': 'Theo dõi', 'nut_da': 'Đã theo dõi', 'thich': 'Thích',
           'binh_luan': 'Bình luận', 'chia_se': 'Chia sẻ', 'luu': 'Lưu', 'anh': 'Ảnh', 'nguon': 'Nguồn'},
    'en': {'ten': 'English', 'chu_viet': 'latin', 'nut': 'Follow', 'nut_da': 'Following', 'thich': 'Like',
           'binh_luan': 'Comment', 'chia_se': 'Share', 'luu': 'Save', 'anh': 'Photo', 'nguon': 'Source'},
    'fr': {'ten': 'Français', 'chu_viet': 'latin', 'nut': "S'abonner", 'nut_da': 'Abonné', 'thich': "J'aime",
           'binh_luan': 'Commenter', 'chia_se': 'Partager', 'luu': 'Enregistrer', 'anh': 'Photo', 'nguon': 'Source'},
    'de': {'ten': 'Deutsch', 'chu_viet': 'latin', 'nut': 'Folgen', 'nut_da': 'Gefolgt', 'thich': 'Gefällt mir',
           'binh_luan': 'Kommentar', 'chia_se': 'Teilen', 'luu': 'Speichern', 'anh': 'Foto', 'nguon': 'Quelle'},
    'es': {'ten': 'Español', 'chu_viet': 'latin', 'nut': 'Seguir', 'nut_da': 'Siguiendo', 'thich': 'Me gusta',
           'binh_luan': 'Comentar', 'chia_se': 'Compartir', 'luu': 'Guardar', 'anh': 'Foto', 'nguon': 'Fuente'},
    'it': {'ten': 'Italiano', 'chu_viet': 'latin', 'nut': 'Segui', 'nut_da': 'Segui già', 'thich': 'Mi piace',
           'binh_luan': 'Commenta', 'chia_se': 'Condividi', 'luu': 'Salva', 'anh': 'Foto', 'nguon': 'Fonte'},
    'pt': {'ten': 'Português', 'chu_viet': 'latin', 'nut': 'Seguir', 'nut_da': 'Seguindo', 'thich': 'Curtir',
           'binh_luan': 'Comentar', 'chia_se': 'Compartilhar', 'luu': 'Salvar', 'anh': 'Foto', 'nguon': 'Fonte'},
    'id': {'ten': 'Bahasa Indonesia', 'chu_viet': 'latin', 'nut': 'Ikuti', 'nut_da': 'Mengikuti', 'thich': 'Suka',
           'binh_luan': 'Komentar', 'chia_se': 'Bagikan', 'luu': 'Simpan', 'anh': 'Foto', 'nguon': 'Sumber'},
    'ja': {'ten': '日本語', 'chu_viet': 'ja', 'nut': 'フォロー', 'nut_da': 'フォロー中', 'thich': 'いいね',
           'binh_luan': 'コメント', 'chia_se': 'シェア', 'luu': '保存', 'anh': '写真', 'nguon': '出典'},
    'ko': {'ten': '한국어', 'chu_viet': 'ko', 'nut': '팔로우', 'nut_da': '팔로잉', 'thich': '좋아요',
           'binh_luan': '댓글', 'chia_se': '공유', 'luu': '저장', 'anh': '사진', 'nguon': '출처'},
    'zh': {'ten': '中文', 'chu_viet': 'zh', 'nut': '关注', 'nut_da': '已关注', 'thich': '点赞',
           'binh_luan': '评论', 'chia_se': '分享', 'luu': '收藏', 'anh': '图片', 'nguon': '来源'},
    'th': {'ten': 'ไทย', 'chu_viet': 'th', 'nut': 'ติดตาม', 'nut_da': 'กำลังติดตาม', 'thich': 'ถูกใจ',
           'binh_luan': 'ความคิดเห็น', 'chia_se': 'แชร์', 'luu': 'บันทึก', 'anh': 'ภาพ', 'nguon': 'ที่มา'},
    'ru': {'ten': 'Русский', 'chu_viet': 'ru', 'nut': 'Подписаться', 'nut_da': 'Вы подписаны', 'thich': 'Нравится',
           'binh_luan': 'Комментарий', 'chia_se': 'Поделиться', 'luu': 'Сохранить', 'anh': 'Фото', 'nguon': 'Источник'},
}
KHONG_CACH = {'ja', 'zh', 'th'}     # ngôn ngữ không cách chữ → sub chia theo ký tự

_VN_RIENG = set('ăâđêôơưĂÂĐÊÔƠƯ' 'ạảấầẩẫậắằẳẵặẹẻẽếềểễệỉịọỏốồổỗộớờởỡợụủứừửữựỳỵỷỹ'
                'ẠẢẤẦẨẪẬẮẰẲẴẶẸẺẼẾỀỂỄỆỈỊỌỎỐỒỔỖỘỚỜỞỠỢỤỦỨỪỬỮỰỲỴỶỸ' 'àáãèéìíòóõùúýÀÁÃÈÉÌÍÒÓÕÙÚÝ')
_VN_CHAC = set('ăđơưĂĐƠƯ' 'ạảấầẩẫậắằẳẵặẹẻẽếềểễệỉịọỏốồổỗộớờởỡợụủứừửữựỳỵỷỹ'
               'ẠẢẤẦẨẪẬẮẰẲẴẶẸẺẼẾỀỂỄỆỈỊỌỎỐỒỔỖỘỚỜỞỠỢỤỦỨỪỬỮỰỲỴỶỸ')   # chỉ tiếng Việt mới có


def dem_chu_viet(s):
    """đếm ký tự theo hệ chữ."""
    d = {'latin': 0, 'hangul': 0, 'kana': 0, 'han': 0, 'thai': 0, 'cyrillic': 0}
    for c in s:
        o = ord(c)
        if 0xAC00 <= o <= 0xD7AF or 0x1100 <= o <= 0x11FF or 0x3130 <= o <= 0x318F:
            d['hangul'] += 1
        elif 0x3040 <= o <= 0x30FF:
            d['kana'] += 1
        elif 0x4E00 <= o <= 0x9FFF or 0x3400 <= o <= 0x4DBF:
            d['han'] += 1
        elif 0x0E00 <= o <= 0x0E7F:
            d['thai'] += 1
        elif 0x0400 <= o <= 0x04FF:
            d['cyrillic'] += 1
        elif c.isalpha() and o < 0x2000:
            d['latin'] += 1
    return d


def kiem_ngon_ngu(chu, nn):
    """→ (muc, loi) với muc ∈ {None, '⚠', '⛔'}. Chữ trên hình phải cùng ngôn ngữ audio `nn`."""
    s = unicodedata.normalize('NFC', str(chu or ''))
    d = dem_chu_viet(s)
    tong = sum(d.values())
    if tong < 3:
        return None, ''
    kieu = NGON_NGU.get(nn, {'chu_viet': 'latin'})['chu_viet']
    can = {'ko': 'hangul', 'th': 'thai', 'ru': 'cyrillic'}.get(kieu)
    if can:
        if d[can] == 0:
            return '⛔', f'audio {nn} nhưng chữ không có ký tự {can}'
        return None, ''
    if kieu == 'ja':
        if d['kana'] + d['han'] == 0:
            return '⛔', 'audio tiếng Nhật nhưng chữ không có kana/kanji'
        return None, ''
    if kieu == 'zh':
        if d['han'] == 0 or d['kana'] or d['hangul']:
            return '⛔', 'audio tiếng Trung nhưng chữ không phải chữ Hán'
        return None, ''
    # Latin
    la = d['latin']
    if tong - la > 0:
        return '⛔', f'audio {nn} (chữ Latin) nhưng chữ có ký tự hệ khác'
    tu = [w for w in re.findall(r'[^\W\d_]+', s) if len(w) >= 2]
    if kieu == 'latin_vi':
        if len(tu) >= 3 and sum(c in _VN_RIENG for c in s) == 0:
            return '⚠', 'audio tiếng Việt nhưng chữ không có dấu nào — có phải tiếng Việt không dấu / tiếng nước khác?'
        return None, ''
    co_dau = [w for w in tu if any(c in _VN_CHAC for c in w)]
    if tu and len(co_dau) / len(tu) >= 0.7 and len(tu) >= 2:
        return '⛔', f'audio {nn} nhưng chữ đang là tiếng Việt — dịch sang {NGON_NGU.get(nn, {}).get("ten", nn)}'
    if tu and len(co_dau) / len(tu) >= 0.4:
        return '⚠', f'chữ có nhiều từ tiếng Việt có dấu — audio {nn}, kiểm lại (tên riêng thì được)'
    return None, ''


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
            o['video'] = True
            o['w'], o['h'] = s.get('width', 0), s.get('height', 0)
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
    return re.sub(r'[^\w]+', '', s)


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


def mo_anh(p, nen=(18, 20, 26)):
    """mở MỌI kiểu ảnh → PIL RGB đứng đúng chiều.
    - ảnh điện thoại có cờ xoay EXIF → xoay thật (không thì ảnh dọc hiện nằm ngang);
    - HEIC / HEIF (iPhone): dùng pillow-heif nếu có, không thì ffmpeg đổi sang PNG (cache ở thư mục tạm dlv_heic);
    - GIF / ảnh nhiều khung → khung đầu; CMYK / 16 bit → RGB; PNG trong suốt → lót nền tối."""
    import tempfile
    from PIL import Image, ImageOps
    p = Path(p)
    if p.suffix.lower() in ('.heic', '.heif'):
        try:
            import pillow_heif
            pillow_heif.register_heif_opener()
        except ImportError:
            tam = Path(tempfile.gettempdir()) / 'dlv_heic' / f'{bam(str(p.resolve()), p.stat().st_mtime)}.png'
            if not tam.exists():
                tam.parent.mkdir(parents=True, exist_ok=True)
                run(['ffmpeg', '-v', 'error', '-y', '-i', p, '-frames:v', '1', tam], check=False)
            if not tam.exists():
                raise RuntimeError(f'không đọc được {p.name} (HEIC) — cài: python -I -m pip install pillow-heif')
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
    ung = [os.environ.get('DLV_CHROME'),
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


# ---------------- nhận lời ----------------
def nhan_loi(wav16, ngon_ngu=None, goi_y=None, model='large-v3'):
    """Whisper large-v3 (CPU int8), TỰ NHẬN NGÔN NGỮ (trừ khi ép) → (từ [{w,s,e}], câu, mã ngôn ngữ, xác suất)."""
    import wave
    import numpy as np
    from faster_whisper import WhisperModel
    wf = wave.open(str(wav16))
    a = np.frombuffer(wf.readframes(wf.getnframes()), dtype=np.int16).astype(np.float32) / 32768
    m = WhisperModel(model, device='cpu', compute_type='int8')
    segs, info = m.transcribe(a, language=ngon_ngu or None, word_timestamps=True, vad_filter=False, beam_size=5,
                              initial_prompt=goi_y or None)
    cau, tu = [], []
    for s in segs:
        ws = [{'w': w.word.strip(), 's': round(w.start, 2), 'e': round(w.end, 2)} for w in s.words if w.word.strip()]
        if not ws:
            continue
        tu += ws
        cau.append({'s': ws[0]['s'], 'e': ws[-1]['e'], 'text': s.text.strip()})
        loi(f"  [{ws[0]['s']:7.2f}-{ws[-1]['e']:7.2f}] {s.text.strip()}")
    return tu, cau, (ngon_ngu or info.language), float(getattr(info, 'language_probability', 1.0) or 1.0)
