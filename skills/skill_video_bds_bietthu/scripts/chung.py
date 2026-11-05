# -*- coding: utf-8 -*-
"""Cấu hình ĐÃ CHỐT + hàm dùng chung cho skill_video_bds_bietthu.

Số đo gốc ở references/phan-tich-mau.md (video mẫu BDS_1/MAU.mp4, đo 04/11/2026).
Sửa thông số ở ĐÂY, không rải hằng số trong các script khác.
"""
import json, os, subprocess, sys

SKILL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS = os.path.join(SKILL, 'assets')
FONTS = os.path.join(ASSETS, 'fonts')
SFX_DIR = os.path.join(ASSETS, 'sfx')
FACE_MODEL = os.path.join(ASSETS, 'models', 'det_10g.onnx')
# det_10g (InsightFace) giấy phép PHI THƯƠNG MẠI → không đưa lên git; tìm ở các chỗ quen, không có thì dùng Haar OpenCV
FACE_MODEL_TIM = [FACE_MODEL,
                  os.path.join(os.path.expanduser('~'), '.insightface', 'models', 'buffalo_l', 'det_10g.onnx'),
                  os.path.join(os.path.dirname(SKILL), 'nns-edit-bds', 'assets', 'det_10g.onnx')]


def ap_dung_plan(plan):
    """plan.json có thể đặt kiểu viết tay chung: "viet_tay_kieu": "vet" | "mau" | "vang" | "trang"."""
    k = (plan or {}).get('viet_tay_kieu')
    if k:
        VIET_TAY['mac_dinh'] = k
    if plan is not None:
        lam_da_dang(plan)


def tim_model_mat():
    return next((p for p in FACE_MODEL_TIM if os.path.isfile(p)), None)

W, H, FPS = 1080, 1920, 30
SR = 48000

# ---- vùng an toàn (UI TikTok/FB che đáy ~330 px; luật đã chốt) ----
SAFE = {'x0': 40, 'x1': 1040, 'y0': 150, 'y1': 1600}

# ---- cắt lặng THEO NĂNG LƯỢNG (04/11: bản cắt theo mốc chữ Whisper làm "hụt hơi" — cắt mất hơi thở + đuôi chữ
#      đỉnh −7…−11 dB). Chỉ bỏ quãng im thật ≥ khe_toi_da, chừa giu_lai cho tiếng lấy hơi.
#      Video ĐÃ DỰNG SẴN (CapCut, đã nối gọn) → mặc định KHÔNG cắt (hỏi D6). ----
CAT_LANG = {'nguong_db': 8.0, 'khe_toi_da': 0.45, 'giu_lai': 0.28, 'giu_dau_cuoi': 0.10}

# ---- nhịp cảnh: trung bình 3,16 s. Mẫu cắt ~0,25 s SAU chữ mở cụm, nhưng user 04/11 chê "chuyển cảnh không khớp"
#      → cắt ĐÚNG đầu câu (1–2 khung trước chữ mở cụm) ----
NHIP = {'cum_toi_da': 3.6, 'cum_toi_thieu': 1.4, 'cat_tre': -0.05, 'hook_toi_thieu': 8.0}

# ---- vai chữ: font, cỡ (khung 1080), màu mặc định ----
VAI = {
    'dan':       {'font': 'BeVietnamPro-Medium.ttf',   'co': 46,  'mau': '#FFFFFF', 'rong_max': 960},
    'chu_thich': {'font': 'BeVietnamPro-SemiBold.ttf', 'co': 50,  'mau': '#FFFFFF', 'rong_max': 960},
    'cau_hoi':   {'font': 'BeVietnamPro-Bold.ttf',     'co': 96,  'mau': '#FFFFFF', 'rong_max': 940},
    'so':        {'font': 'Montserrat-SemiBold.ttf',   'co': 340, 'mau': '#FCE773', 'rong_max': 860},
    'khoa':      {'font': 'BarlowCondensed-Black.ttf', 'co': 280, 'mau': '#1AD1C3', 'rong_max': 900},
    'nhan':      {'font': 'Montserrat-Bold.ttf',       'co': 110, 'mau': '#FCE773', 'rong_max': 900},
    'viet_tay':  {'font': 'GreatVibes-Regular.ttf',    'co': 120, 'mau': '#FFFFFF', 'rong_max': 900},
    'tu_lon':    {'font': 'BarlowCondensed-Black.ttf', 'co': 330, 'mau': '#1AD1C3', 'rong_max': 900},   # 04/11: bạc → MÀU kiểu A
    'ten':       {'font': 'Montserrat-Bold.ttf',       'co': 118, 'mau': '#FFFFFF', 'rong_max': 940},
    'sub':       {'font': 'BeVietnamPro-SemiBold.ttf', 'co': 40,  'mau': '#FFFFFF', 'rong_max': 960},
    'nhan_the':  {'font': 'BeVietnamPro-Bold.ttf',     'co': 40,  'mau': '#FFFFFF', 'rong_max': 900},
}
# chồng dòng: dòng sau đè lên đáy dòng trước bao nhiêu phần cao (mẫu: dòng gần như dính, viết tay đè ~30 %)
CHONG = {'viet_tay': 0.30, 'chu_thich': 0.02, 'default': -0.04}
CHU_TO = ('so', 'khoa', 'nhan', 'tu_lon', 'ten', 'cau_hoi')   # chỉ đè lên dòng TO; dưới dòng nhỏ thì xếp thường

# ---- chuyển động chữ (đo từng khung) ----
CHU = {
    'ky_tu_moi_khung': 1.25,   # gõ chữ 1–1,5 ký tự/khung
    'ky_tu_to': 0.6,           # chữ TO (số, khoá, chữ to...) gõ CHẬM hơn để thấy từng ký tự chạy (05/11: "thiếu chữ chạy từng cái một")
    'xoa_khung': 5,            # xoá ngược 4–5 khung
    'xoa_troi_px': 14,         # trôi phải lúc xoá
    'troi_px_s': 6,            # cụm trôi chậm liên tục
    'nhay_khung': 6,           # nhấp nháy bật/tắt 6 khung
    'roi_khung': 5,            # rơi từ trên 4–5 khung
    'roi_px': 140,
    'bong': (0, 5, 9, 150),    # bóng đổ: dx, dy, nhoè, alpha
    'quang_nho': (10, 150),    # chữ nhỏ (dẫn/sub/chú thích/viết tay/câu hỏi): quầng tối sát chữ để đọc được trên nền sáng
    'tat_truoc_cat': 0.20,     # khối bắt đầu xoá 0,20 s trước cú cắt → xoá xong ~0,03 s trước cắt (mẫu: 0,13–0,17 s)
}

# ---- KIỂU A (user chọn 04/11 trong 3 kiểu A đúng mẫu / B khối 3D / C neon): chữ khoá có quầng CÙNG MÀU,
#      bóng đen đậm, viền tối cùng màu, mặt gradient sáng→gốc→tối + vân ----
CHU_A = ('khoa', 'tu_lon', 'so', 'nhan')
KIEU_A = {'quang_k': 0.10, 'quang_a': 0.55, 'bong_nhoe': 8, 'bong_dy': 6, 'bong_a': 0.75, 'vien': 7, 'vien_toi': 0.25,
          'mat_tren': 0.55, 'mat_duoi': -0.38}
# hook: nửa trên khung tối dần (0 ở y 900 → 32 % ở đỉnh) để chữ màu nổi trên nền sáng
TOI_TREN = {'y': 900, 'manh': 0.32}

# ---- CHỮ VIẾT TAY (user 04/11 tối: "mấy cái chữ uốn lượn không được để chữ trắng, phải là chữ có HIGHLIGHT") ----
#      vet  = chữ trắng trên VỆT HIGHLIGHT (nét bút dạ quang) màu của cụm, vệt "vẽ ra" theo nhịp gõ  <- MẶC ĐỊNH
#      mau  = chữ MÀU KHOÁ của cụm + quầng cùng màu (đồng bộ kiểu A)
#      vang = chữ vàng kim gradient + viền nâu + quầng sáng (kiểu BĐS user đã duyệt ở minh-tam-edit)
#      trang = kiểu cũ (trắng trơn) — CHỈ khi plan ghi "cho_phep_trang": true; kiem-plan báo lỗi nếu gặp mà không có cờ
VIET_TAY = {
    'mac_dinh': 'vet',
    'vet': {'cao': 0.58, 'duoi': 0.16, 'le': 0.10, 'goc': -1.4, 'a': 0.93, 'toi_den_L': 0.40, 'nhieu': 0.10,
            'bong_a': 0.50, 'chu_bong_a': 0.60, 'mau_mac_dinh': 'xanh_ngoc'},
    'mau': {'quang_k': 0.10, 'quang_a': 0.60, 'bong_a': 0.70, 'vien': 3, 'vien_toi': 0.30, 'sang': 0.25},
    'vang': {'tren': '#FFF4B8', 'giua': '#F7C948', 'duoi': '#C47A17', 'vien': '#4A2A0C', 'vien_px': 5, 'quang_k': 0.10,
             'quang_a': 0.55, 'bong_a': 0.70},
}

# ---- màu khoá gợi ý (lấy mẫu trên khung gốc) ----
BANG_MAU = {
    'vang': '#FCE773', 'vang_nhat': '#F1DC92', 'xanh_ngoc': '#1AD1C3', 'xanh_ngoc_sang': '#32ECEA',
    'tim_hong': '#E417F6', 'hong_do': '#F21552', 'navy': '#173C6B', 'bac_ha': '#AEE5C9',
    'cam_dao': '#F2A287', 'xanh_rung': '#195236', 'bac': '#E8EEEA',
}

# ---- bố cục cảnh ----
THE_MO = {'rong': 1036, 'bo_goc': 50, 'tam_y': 1150, 'nhoe': 28, 'toi': 0.82}
GHEP3 = {'nen': '#2BA898', 'rong': 1000, 'cao': 470, 'khe': 28, 'y0': 160, 'bo_goc': 40,   # 3 thẻ: 160–1626, nhãn thẻ 3 vẫn trên y 1600
         'truot_khung': 5, 'cach_the': 0.15, 'hoa_tan': 0.25}
KEN_BURNS = {'day_vao_s': 0.025, 'lia_px_s': 10}   # ảnh tĩnh: đẩy vào 2,5 %/s + lia nhẹ

# ---- hiệu ứng (đo từng khung, xem bảng §3 phan-tich-mau.md) ----
HU = {
    'phong_lui': {'tu': 1.35, 'khung': 6},
    # 04/11 user: "chuyển cảnh bị dài, không khớp" → mọi hiệu ứng chuyển ngắn lại
    'loe': {'khung': 8, 'dinh': 2, 'sang': 0.55, 'rung_px': 10},
    'phong_nhanh': {'khung': 3, 'toi': 1.22, 'loe': 0.35},     # thay zoom-nhoè của mẫu (user ghét nhoè)
    'nhoe_zoom': {'khung': 3},                                  # chỉ khi plan bật "nhoe": true (mẫu 5 khung)
    'nhan_ban': {'khung': 6},
    'loe_cam': {'truoc': 0.06, 'sau': 0.19, 'manh': 0.85},     # 0,25 s (mẫu 0,45 s)
    'the3d': {'vao': 0.25, 'goc': (-38, -18), 'doi_anh': 0.7},
}

# ---- âm thanh ----
AM = {
    'lufs': -14.0, 'tp': -1.5,
    'nhac_duoi_giong_db': 16.0,      # mẫu: nhạc thấp hơn giọng 14–18 dB
    'sfx_tren_giong_db': 5.0,        # SFX phải nghe rõ: đỉnh 10 ms > RMS giọng tại chỗ +3…+7 dB
}
# ---- zoom mượt giữa 2 cảnh người nói liền nhau (04/11: "zoom in zoom out không mượt, không có SFX, giật") ----
ZOOM_MUOT = {'khung': 10}     # 0,33 s, ease in-out, neo nội suy; mỗi cú có 1 whoosh

# ---- SFX THEO LOẠI SỰ KIỆN, mỗi loại nhiều biến thể (05/11 user: "hiệu ứng chữ và SFX bị hạn chế, cứ lặp đi lặp lại mấy cái") ----
# Mỗi cue chọn biến thể ÍT DÙNG NHẤT và không trùng file nào trong SFX_KHONG_LAP_S giây (dùng chung lịch sử cho mọi loại).
SFX_NHOM = {
    'zoom_muot':   ['whoosh-short.mp3', 'quick-swoosh.mp3', 'swoosh.mp3'],
    'loe_cam':     ['swoosh.mp3', 'whoosh.wav', 'whoosh-short.mp3', 'quick-swoosh.mp3'],
    'phong_lui':   ['quick-swoosh.mp3', 'swoosh.mp3'],
    'loe':         ['camera-flash-1.wav', 'camera-shutter.mp3'],
    'phong_nhanh': ['whoosh.wav', 'whoosh-short.mp3'],
    'nhoe_zoom':   ['whoosh.wav'],
    'the3d':       ['sparkle.mp3', 'fairy-dust.mp3'],
    'ghep3':       ['new-item.mp3', 'quick-swoosh.mp3'],
    'nhay':        ['quick-ting.mp3', 'sparkle.mp3'],          # chữ khoá nhấp nháy
    'khung_vao':   ['pop.mp3', 'pop-2.mp3', 'click-button.mp3'],   # khối chữ có KHOÁ / câu hỏi vào
    'khoa_roi':    ['click-button.mp3', 'pop-2.mp3'],          # chữ khoá rơi từ trên xuống
    'so_hien':     ['ting.mp3', 'quick-ting.mp3', 'chime.mp3'],    # con số hiện
    'tien':        ['ka-ching.mp3', 'ding.mp3'],               # số tiền / % / giá
    'tu_lon':      ['pop-2.mp3', 'camera-shutter.mp3', 'pop.mp3'], # từng chữ to ở hook
    'cta':         ['chime.mp3', 'ding.mp3'],                  # tên người nói ở CTA
}
SFX_MAP = {k: v[0] for k, v in SFX_NHOM.items()}      # tương thích cũ (biến thể đầu)
SFX_XOAY = {}
# ưu tiên khi 2 tiếng chen nhau trong SFX_CUA_SO: chuyển cảnh / hiệu ứng lớn trước, chữ sau
SFX_UU_TIEN = ['loe_cam', 'phong_nhanh', 'nhoe_zoom', 'ghep3', 'zoom_muot', 'phong_lui', 'loe', 'the3d', 'cta', 'tien',
               'so_hien', 'nhay', 'khoa_roi', 'khung_vao', 'tu_lon', 'them']
SFX_CUA_SO = 0.40
SFX_KHONG_LAP_S = 5.0
# SFX của CHỮ nhỏ nhẹ hơn SFX chuyển cảnh (đỉnh so với giọng tại chỗ, dB); mặc định AM['sfx_tren_giong_db']
SFX_TREN = {'khung_vao': 3.0, 'khoa_roi': 3.0, 'tu_lon': 3.0, 'so_hien': 3.5, 'tien': 4.0, 'nhay': 3.5, 'cta': 4.0}
SFX_CHU_VAI = {'so': 'so_hien', 'khoa': 'khung_vao', 'tu_lon': 'tu_lon', 'cau_hoi': 'khung_vao', 'ten': 'cta'}
SFX_TIEN_RE = r'tỷ|tỉ|triệu|\btr\b|%|vnđ|vnd|\bgiá\b|chiết khấu|ưu đãi'
SFX_HO = [['quick-swoosh.mp3', 'whoosh-short.mp3', 'swoosh.mp3']]
SFX_DAI_MAX = {'fairy-dust.mp3': 1.2, 'whoosh.wav': 0.8, 'camera-flash-1.wav': 0.35, 'ka-ching.mp3': 1.3, 'chime.mp3': 1.2,
               'ding.mp3': 1.0, 'ting.mp3': 1.0, 'sparkle.mp3': 1.0, 'new-item.mp3': 0.9, 'quick-ting.mp3': 0.6,
               'pop.mp3': 0.4, 'click-button.mp3': 0.35, 'camera-shutter.mp3': 0.34, 'pop-2.mp3': 0.3}


def chon_sfx(kieu, t, lich_su):
    """Biến thể của loại `kieu` ít dùng nhất, không trùng file nào trong SFX_KHONG_LAP_S giây. lich_su: list (file, t)."""
    ds = SFX_NHOM.get(kieu)
    if not ds:
        return None

    def diem(f):
        gan = [u for ff, u in lich_su if ff == f and u <= t]
        return (any(t - u < SFX_KHONG_LAP_S for u in gan), len([1 for ff, _ in lich_su if ff == f]), ds.index(f))
    f = min(ds, key=diem)
    lich_su.append((f, t))
    return f


# ---- ĐA DẠNG CHỮ (05/11): phông luân phiên theo vai, kiểu VÀO / RA luân phiên, căn lề trái-giữa-phải khi cảnh không có mặt.
#      Chỉ ĐIỀN chỗ plan để trống — khoá nào plan ghi rõ (font, vao, ra, can) luôn được giữ. Tắt: plan "da_dang": false ----
DA_DANG = {
    'font': {
        'dan':      ['BeVietnamPro-Medium.ttf', 'Montserrat-SemiBold.ttf', 'BeVietnamPro-Medium.ttf', 'PlayfairDisplay-Italic.ttf'],
        'so':       ['Montserrat-SemiBold.ttf', 'Baloo2-ExtraBold.ttf', 'Montserrat-ExtraBold.ttf'],
        'khoa':     ['BarlowCondensed-Black.ttf', 'Baloo2-ExtraBold.ttf', 'BarlowCondensed-Black.ttf', 'Montserrat-ExtraBold.ttf'],
        'nhan':     ['Montserrat-Bold.ttf', 'Baloo2-ExtraBold.ttf'],
        'tu_lon':   ['BarlowCondensed-Black.ttf', 'Baloo2-ExtraBold.ttf'],
        'viet_tay': ['GreatVibes-Regular.ttf', 'PlayfairDisplay-Italic.ttf', 'DancingScript.ttf'],
    },
    # 05/11 user: "thiếu chữ chạy từng cái một" -> GÕ TỪNG KÝ TỰ (go) chiếm khoảng một nửa, phần còn lại xen kiểu khác
    'vao': {
        'dan':       ['go', 'go', 'tung_tu', 'go', 'truot', 'go'],
        'viet_tay':  ['go', 'go', 'quet', 'go', 'nhoe'],
        'chu_thich': ['go', 'go', 'truot'],
        'so':        ['go', 'roi', 'go', 'phong'],
        'khoa':      ['go', 'nhay', 'go', 'phong', 'go', 'roi'],
        'nhan':      ['go', 'phong'],
        'cau_hoi':   ['go', 'go', 'nhoe'],
        'tu_lon':    ['go', 'phong'],
        'ten':       ['go', 'phong'],
    },
    'ra': ['xoa', 'mo', 'xoa', 'mo'],
    'can': ['giua', 'trai', 'phai'],
    'can_rong_toi_da': 700,       # khối rộng hơn thì giữ canh giữa
}


# ---- chữ nằm DƯỚI lớp người khi chạm (05/11) ----
NGUOI = {
    'model_tim': [os.path.join(ASSETS, 'models', 'u2net_human_seg.onnx'),
                  os.path.join(os.path.expanduser('~'), '.u2net', 'u2net_human_seg.onnx'),
                  os.path.join(os.path.dirname(SKILL), 'skill-bando-tintuc-chinhtri', 'cache', 'models', 'u2net.onnx')],
    'len': 0.45,          # vùng cắt bắt đầu cao hơn tâm mặt 0,45 × chiều rộng khung
    'nguong': (0.30, 0.65),
    'no': 9, 'mem': 1.5,
    'vung_x': 1.9, 'vung_tren': 0.9,   # vùng người: ±1,9 bề rộng mặt, từ 0,9 chiều cao mặt phía trên đầu xuống đáy khung
}


def lam_da_dang(plan):
    """Điền font / vao / ra / can còn trống trong plan (CHỈ trong bộ nhớ, plan.json giữ nguyên). Luân phiên theo thứ tự thời gian."""
    if plan.get('_da_dang_xong') or plan.get('da_dang') is False:
        return plan
    cf, cv, cr, cc = {}, {}, 0, 0
    for c in sorted(plan.get('canh', []), key=lambda q: q['t0']):
        for b in sorted(c.get('chu', []), key=lambda q: min([d['t'] for d in q['dong']] or [0])):
            if 'ra' not in b:
                b['ra'] = DA_DANG['ra'][cr % len(DA_DANG['ra'])]; cr += 1
            if c['loai'] != 'noi' and 'can' not in b and 'x' not in b:
                b['can'] = DA_DANG['can'][cc % len(DA_DANG['can'])]; cc += 1
            for d in b['dong']:
                v = d.get('vai')
                if 'font' not in d and v in DA_DANG['font']:
                    p = DA_DANG['font'][v]; d['font'] = p[cf.get(v, 0) % len(p)]; cf[v] = cf.get(v, 0) + 1
                if 'vao' not in d and v in DA_DANG['vao']:
                    p = DA_DANG['vao'][v]; d['vao'] = p[cv.get(v, 0) % len(p)]; cv[v] = cv.get(v, 0) + 1
    plan['_da_dang_xong'] = True
    return plan


def font_dong(d):
    """Tên file phông thật của 1 dòng chữ (plan đã qua lam_da_dang)."""
    return d.get('font') or VAI[d['vai']]['font']


IMG_EXT = ('.jpg', '.jpeg', '.png', '.webp', '.bmp')
VID_EXT = ('.mp4', '.mov', '.m4v', '.mkv', '.webm')


def font(ten):
    return os.path.join(FONTS, ten)


def run(cmd, **kw):
    r = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='replace', **kw)
    if r.returncode != 0:
        raise RuntimeError('Lệnh lỗi: ' + ' '.join(map(str, cmd))[:300] + '\n' + r.stderr[-1500:])
    return r


def probe(path):
    r = run(['ffprobe', '-v', 'error', '-show_entries', 'stream=codec_type,width,height,r_frame_rate,avg_frame_rate,duration'
             ':stream_side_data=rotation:format=duration', '-of', 'json', path])
    d = json.loads(r.stdout)
    v = next((s for s in d['streams'] if s['codec_type'] == 'video'), None)
    a = next((s for s in d['streams'] if s['codec_type'] == 'audio'), None)
    out = {'dur': float(d['format'].get('duration', 0) or 0), 'audio': a is not None}
    if v:
        w, h = int(v['width']), int(v['height'])
        rot = 0
        for sd in v.get('side_data_list', []) or []:
            if 'rotation' in sd: rot = int(sd['rotation'])
        if abs(rot) in (90, 270): w, h = h, w
        num, den = (v.get('avg_frame_rate') or v.get('r_frame_rate') or '30/1').split('/')
        out.update(w=w, h=h, fps=float(num) / float(den or 1) if float(den or 1) else 30.0)
    return out


def doc_json(p):
    with open(p, encoding='utf-8') as f:
        return json.load(f)


def ghi_json(p, d):
    with open(p, 'w', encoding='utf-8') as f:
        json.dump(d, f, ensure_ascii=False, indent=1)


def hex2rgb(h):
    h = h.lstrip('#')
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def utf8_stdout():
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass
