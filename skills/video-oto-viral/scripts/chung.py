# -*- coding: utf-8 -*-
"""Hằng số phong cách + tiện ích chung của skill video-oto-viral.

MỌI con số phong cách nằm ở file này (đo từ video mẫu F:/VIDA_TEST/Oto/Video_mau.mp4, xem
references/phan-tich-mau.md). Script khác KHÔNG tự đặt số.
"""
import os, sys, json, math, re, subprocess

SKILL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS = os.path.join(SKILL, 'assets')
FONT_DIR = os.path.join(ASSETS, 'fonts')
SFX_DIR = os.path.join(ASSETS, 'sfx')

FPS = 30
SR = 44100
KHO = {'16:9': (1920, 1080), '9:16': (1080, 1920)}

# ---------------------------------------------------------------- nhịp / khuôn dựng
# Mẫu 117,2 BPM: nhịp (bar) 2,05 s; cú cắt rơi vào PHÁCH MẠNH đầu nhịp, hình đổi trễ ~1 khung sau tiếng trống.
TRE_CAT = 1.0 / FPS
F_MAU = 1.485           # giây của phách mạnh đầu tiên (tiếng trống) trong mẫu; drop 13,787 s (đo lại tâm cửa sổ 10/11/2026)
# Khuôn 13 cảnh của mẫu, đơn vị NHỊP (bar) tính từ phách mạnh đầu tiên F; drop rơi đúng nhịp 6.
#  vai        : vai trò cảnh (Claude chọn clip đúng nghĩa)
#  b0, b1     : nhịp bắt đầu / kết thúc (b1 None = cảnh kết, dài theo AM['ket_phach'])
#  vao        : chuyển cảnh VÀO cảnh này
#  dong       : chuyển động máy trong cảnh (+ = đẩy vào, - = kéo ra, %/giây)
KHUON = [
    dict(vai='mo_dau',      b0=None, b1=2,    vao=None,        dong=0.0,
         mo_ta='Mở đầu: người giới thiệu cạnh xe / xe toàn cảnh. Khung điện ảnh mở + đập zoom + nảy trước cú cắt'),
    dict(vai='toan_canh',   b0=2,  b1=3,    vao='manh_vo',   dong=0.06, mo_ta='Xe 3/4 trước toàn thân'),
    dict(vai='chi_tiet',    b0=3,  b1=4,    vao='manh_vo',   dong=0.06, mo_ta='Cận chi tiết đẹp (đèn pha / mâm / gương)'),
    dict(vai='logo',        b0=4,  b1=5,    vao='manh_vo',   dong=0.03, mo_ta='Cận logo / chữ tên xe trên thân (HUD bắt đầu hiện)'),
    dict(vai='goc_thap',    b0=5,  b1=6,    vao='luot_trang', dong=-0.11, mo_ta='Đầu xe góc thấp / nắp capo (kéo ra)'),
    dict(vai='noi_that',    b0=6,  b1=7,    vao='gon_song',  dong=0.06, mo_ta='DROP: nội thất đắt nhất (vô lăng / màn hình)'),
    dict(vai='chinh_dien',  b0=7,  b1=8,    vao='khoi',      dong=0.09, mo_ta='Đầu xe chính diện'),
    dict(vai='nhanh_1',     b0=8,  b1=8.5,  vao='lia_nhoe',  dong=0.0,  mo_ta='Dồn nhanh 2 phách: chi tiết ngoại thất'),
    dict(vai='nhanh_2',     b0=8.5, b1=9,   vao='lia_nhoe',  dong=0.12, mo_ta='Dồn nhanh: chi tiết nội thất (cần số / nút)'),
    dict(vai='nhanh_3',     b0=9,  b1=9.5,  vao='lia_nhoe',  dong=0.09, mo_ta='Dồn nhanh: chi tiết nội thất khác'),
    dict(vai='nhanh_4',     b0=9.5, b1=10,  vao='lia_nhoe',  dong=-0.09, mo_ta='Dồn nhanh: đuôi xe / đèn hậu / logo sau'),
    dict(vai='hero',        b0=10, b1=11,   vao='lia_nhoe',  dong=0.0,  mo_ta='Xe 3/4 đẹp nhất + chữ hãng gõ từng ký tự theo nhịp'),
    dict(vai='ket',         b0=11, b1=None, vao='glitch',    dong=0.0,  mo_ta='Thẻ kết: xe + tên hãng trắng + dòng xe đỏ'),
]
DROP_NHIP = 6
HUD_TU_NHIP = 4          # HUD hiện từ cảnh 'logo' (mẫu 9,8 s) tới hết

# ---------------------------------------------------------------- chuyển cảnh (số khung @30 fps)
# truoc = số giây TRƯỚC mốc cắt bị ảnh hưởng, sau = số giây SAU mốc cắt.
# lech = dời mốc đổi hình so với (phách + 1 khung): mẫu đổi sang cảnh drop ~4 khung TRƯỚC tiếng trống (13,70 s, trống 13,79)
# Đo lại khung ĐẦU TIÊN của cảnh mới trong mẫu (10/11/2026, so lưới F=1,4856): lướt 11,767 · sóng 13,667 · khói 15,833 ·
# glitch bật mạnh ngay 23,967 (không tăng dần) → bản 3a trễ 1–2 khung ở các chỗ này (mốc = phách + 1 khung rơi lố khung
# vì sai số vài ms). Mốc 'lech' dưới đây đặt mốc cắt vào GIỮA 2 khung mong muốn.
CHUYEN = {
    'cat':        dict(truoc=0.0, sau=0.0),
    'nhoe_loe':   dict(truoc=0.0, sau=0.45),
    'manh_vo':    dict(truoc=1.10, sau=0.20),
    'luot_trang': dict(truoc=0.36, sau=0.24, lech=-0.010),
    'gon_song':   dict(truoc=0.14, sau=0.27, lech=-0.165),
    'khoi':       dict(truoc=0.30, sau=0.12, lech=-0.046),
    'lia_nhoe':   dict(truoc=0.10, sau=0.40),
    'glitch':     dict(truoc=0.034, sau=0.37, lech=-0.082),
}

# nhoè-loé sau mảnh vỡ (đo từng khung 7,70–7,84 s mẫu): 1 khung loé lại cảnh cũ → NHOÈ MẠNH 1 khung → nét lại sau 3 khung,
# hầu như KHÔNG trắng (bản 2 trắng sữa 4 khung — sai)
NHOE_LOE = dict(sigma=[0.034, 0.016, 0.013, 0.005, 0.001], loe=0.10, loe_tau=1.5, loe_khung=4)
# MẢNH VỠ (6,45–7,70 / 8,45–9,77 s mẫu, đo lại từng khung 10/11/2026):
#  u 0–0,45 cảnh cũ phủ CHẤM BI rõ dần · 0,08–0,7 cảnh cũ VỠ thành 2 tấm dài chéo trượt dọc trục (có chấm bi)
#  · 0,12–0,45 2 vệt NHOÈ NGANG quét qua · 0,16–0,75 vệt đỏ nhọn · 0,15–0,6 TẤM KÍNH bo góc mang cảnh mới ĐÚNG CHỖ của nó
#  (bật ra, lệch nhẹ) · 0,42–0,95 cảnh mới về thành Ô bo góc lớn (lưới 2×3 dọc / 3×2 ngang) LỆCH NHẸ rồi khớp dần
#  (kiểu ghép hình, KHÔNG bay từ xa + xoay như bản 2) · 0,95 khớp hẳn → 1 khung loé cảnh cũ → nhoè
#  Soi lại 10/11/2026 (bản 3): 7,60–7,63 cảnh mới ghép xong → 7,667 + 7,70 LOÉ 2 khung cảnh cũ ĐANG VỠ (chấm bi + tấm
#  chéo, không phải cảnh cũ trơn) → 7,733 nhoè mạnh cảnh mới → nét lại 7,87. Chấm bi phủ đủ ngay đầu (bản 3a chỉ rõ
#  dần tới u 0,45, bước chấm theo bề NGANG khổ dọc ~9 px → gần như không thấy) → bước theo CẠNH DÀI.
#  fb_truoc / flashback = số khung loé trước / sau mốc cắt · fb_u = pha mảnh vỡ dùng cho khung loé
MANH = dict(so_dai=2, so_nhoe=2, so_do=3, so_kinh=3, bo_goc=0.03, o_tu=(0.42, 0.70), o_dai=0.22, o_xong=0.95,
            lap_day=(0.90, 0.97), cham_cu=0.92, cham_vao=0.15, halftone_buoc=0.0078, tang_toc_tu=0.80, tang_toc=1.045,
            mau_do=((26, 16, 200), (40, 40, 255), (14, 8, 46)), flashback=1, fb_truoc=1, fb_u=0.32)
# MẢNH VỠ MỞ ĐẦU có người cầm mảnh (4,45–5,67 s mẫu): khung tay + mảnh LAO VỀ MÁY (phóng ×~4, tay văng ra 2 mép rồi
# mất ở u≈0,5) · cảnh mới về thành 5–6 MẢNH LỚN bay vào xoay 3D, đáp chỗ ở u 0,12–0,45, còn lệch nhẹ rồi khớp dần tới 0,95
# Bản 3a mảnh đáp tới u 0,68 + nền đổi 0,40–0,52 → áo trắng người dẫn còn trơ giữa khung tới 4,92 s; mẫu phủ kín ~4,98 s
# (u≈0,45). KHÔNG loé lại cảnh người ở cú cắt (mẫu 5,6–5,7 s chỉ nhoè cảnh mới).
MANH_MO = dict(luoi={'doc': (2, 3), 'ngang': (3, 2)}, rung_dinh=0.16, dap=(0.12, 0.36), bay=0.16, lech_du=0.035,
               nen_doi=(0.28, 0.38), lop_zoom=16.0, lop_mu=2.5, lop_het=(0.30, 0.44), so_do=2)
# lướt trắng (11,43–12,0 s): px/khung @1920 + độ trắng. Mẫu chỉ trắng ~45 % rồi cảnh mới vào còn trắng ~45 % tan dần
# (bản 2 trắng 82 % gần như cháy — sai)
LUOT = dict(toc_truoc=[1, 4, 7.5, 10, 13, 18, 23, 28, 38, 54, 54], trang_truoc=[0, 0, 0, .02, .06, .12, .2, .28, .36, .42, .46],
            toc_sau=[31, 22, 15, 10, 7.5, 4, 2], trang_sau=[.46, .34, .22, .12, .05, .02, 0])
# gợn sóng (13,57–13,84 s, DROP): cảnh cũ gợn MẠNH + nhoè dần 4 khung → đổi cảnh ~13,70 → gợn tắt sau 5 khung
# mẫu còn gợn + nhoè rõ tới 13,80 và gợn nhẹ 13,87 (bản 3a tắt sau 4 khung — hụt)
SONG = dict(bien_truoc=[.014, .022, .032, .042], bien_sau=[.04, .032, .024, .017, .011, .006, .003, 0],
            buoc_song=0.16, nhoe_truoc=[2, 5, 12, 26], nhoe_sau=[14, 9, 6, 4, 2.5, 1.5, 0.5, 0])
# khói / chất lỏng (15,5–15,83 s)
KHOI = dict(bien_truoc=[.003, .006, .01, .015, .02, .026, .032, .038, .044], bien_sau=[.024, .012, .004, 0],
            nhat=0.12)
# lia nhoè + rung (17,9 / 18,93 / 19,93 / 20,97 / 21,97 s): mẫu NHOÈ CHUYỂN ĐỘNG NGANG rất dài 2 khung trước + 2 khung sau
LIA = dict(dich_truoc=[0.0, 0.03, 0.08], nhoe_truoc=[0.0, 0.10, 0.22], dich_sau=[0.06, 0.025, 0.008], nhoe_sau=[0.20, 0.08, 0.02],
           zoom_sau=[1.07, 1.03, 1.01], rung_bien=0.016, rung_tau=5.0, rung_khung=15)
# glitch kéo dọc (23,97–24,25 s): 2 khung đầu gần trắng xanh-hồng, cột ảnh kéo dọc phủ ~80 % bề ngang, tắt sau ~8 khung
GLITCH = dict(manh=[1, 1, .95, .85, .72, .58, .45, .32, .2, .1, .04, 0], trang=0.62, lech_rgb=0.018, truoc=[1.0])

# ---------------------------------------------------------------- hiệu ứng trong cảnh
# dải hình / H lúc đầu: mẫu 0,47 (đo từng khung); khổ dọc cũng 0,47 — dải 0,30 (bản 2) để trống đen trên quá to, lệch
KHUNG_DIEN_ANH = {'16:9': 0.47, '9:16': 0.47}
# mẫu: 2 thanh đen MỞ ĐỀU (gần tuyến tính, đối xứng) từ 0,05 s tới 0,97 s — không giữ rồi bật (bản 2 sai)
KHUNG_MO = dict(tu=0.05, dai=0.92, vao=0.10)    # vao = đoạn đầu tăng tốc mềm (phần của dai)
DAP_ZOOM = dict(dai=0.40, len=1.20)             # 3,17→3,57 s ×1,20 kết thúc đúng phách
NAY = [1.033, 1.072, 1.103, 1.120, 1.114, 1.070, 1.015]   # 5,40–5,60 s, nảy vào rồi bật ra trước cú cắt
ZOOM_TOI_DA = 1.6
# mảnh cảnh sau GHIM VÀO ĐẦU NGÓN (mẫu 2,9–4,4 s: dải mỏng giữa 2 đầu ngón chụm → kéo dãn → khung chữ L: 4 góc =
# đầu ngón trỏ + đầu ngón cái, ngón đè mép, mặt lộ). Bản 2 neo TÂM LÒNG BÀN TAY + lấn 0,25 tay → lệch ngón, người dùng chê.
#  cr/cb: ngưỡng da YCrCb · co: vùng cổ bỏ khi dò (×cao mặt) · dt_min: khối da tối thiểu (×diện tích mặt)
#  chum_rong: 1 khối rộng hơn (×bề ngang mặt) = 2 tay chụm · dau_ngon: dải mép lấy trung bình (×cỡ tay)
#  dung_l: độ dựng ngón trỏ trên ngón cái (×cỡ tay) từ → tới = dải chụm → khung L · soi / soi_min: cao dải chụm
#  (×khoảng cách / ×cỡ tay) · tach: 2 đầu ngón cách nhau (×cỡ tay) từ → tới mới cho mở khung L
#  lan / lan_duoi / lan_tren: mép mảnh luồn dưới ngón (×cỡ tay) · co_che: cổ (chỉ khi che_dau)
#  che_dau: False = mảnh nằm TRƯỚC mặt, chỉ bàn tay đè lên (bản 3 — người khung chữ L ngang mặt, để đầu trước
#  mảnh làm mảnh vỡ vụn quanh mặt + lúc chuyển cảnh mặt người phóng to theo lớp → xấu) · ong_long / ong_ngon / ong_qua:
#  'ống' lòng bàn tay → đầu ngón để lọc da tay khỏi da mặt (×cỡ tay)
#  DẢI KÉO (người dùng chê bản 3 "chưa kéo từ tay ra mà đưa từ dưới lên"): 2 đầu dải = CHỖ CHỤM (chum_goc: hướng
#  vào trong + lên bao nhiêu độ) · hien_keo: dải hiện dần khi 2 chỗ chụm tách (×cỡ tay) · day: bề dày SỢI (×cỡ tay)
#  · ban_phach: số phách sau t0 sợi bắt đầu → xong nở thành dải bản (mẫu sợi 2,7–3,07 s, bản 3,13–3,3 s)
#  · cham: 2 khối tay cách nhau ≤ cham·cỡ tay = đầu ngón đang chạm → chỗ chụm chung · co_no: hộp cổ chỉ bỏ da NỐI
#  với mặt, cắt ở hàng hẹp nhất (mũi chữ V cổ áo) nếu phía dưới nở ≥ co_no × (= ngón chụm chạm mũi V)
#  zoom_cu: nền cảnh cũ đẩy nhẹ khi chuyển cảnh
MANH_TAY = dict(cr=(136, 176), cb=(78, 128), co=0.75, dt_min=0.07, chum_rong=1.1, dau_ngon=0.10,
                dung_l=(0.30, 0.60), tach=(1.2, 1.8), soi=0.09, soi_min=0.20, lan=0.10, lan_duoi=0.06, lan_tren=-0.03, co_che=0.25,
                che_dau=False, ong_long=0.55, ong_ngon=0.17, ong_qua=0.10, mau_nguong=3.0, mau_noi=0.9, mau_dam=0.45, mau_xa=0.6, gap_sau=0.12,
                chum_goc=20, cham=0.12, co_no=2.5, day=0.035, ban_phach=(3.0, 3.5), hien_keo=(0.12, 0.40),
                vien=0.55, zoom_cu=1.10)

# ---------------------------------------------------------------- màu (look xe HDR: nét + rõ + bão hoà)
MAU = dict(net=0.65, net_sigma=1.1, ro=0.22, ro_sigma=22, tuong_phan=1.08, bao_hoa=1.18, toi_goc=0.10)

# ---------------------------------------------------------------- chữ
CHU = {
    'tieu_de': dict(font='BarlowCondensed-ExtraBold.ttf', mau=(255, 255, 255), gian=0.62,
                    rong={'16:9': 0.50, '9:16': 0.84}, cao_max={'16:9': 0.17, '9:16': 0.075},
                    y={'16:9': 0.285, '9:16': 0.30}, bong=0.45),
    'dong_xe': dict(font='BarlowCondensed-BlackItalic.ttf', mau_tren=(255, 48, 40), mau_duoi=(200, 14, 22), gian=0.06,
                    cao={'16:9': 0.145, '9:16': 0.085}, x={'16:9': 0.552, '9:16': 0.5}, y={'16:9': 0.715, '9:16': 0.76},
                    bong=0.5, tre=0.13),
    'go_tre_phach': 0.40,    # chữ đầu hiện sau phách mạnh 0,4 phách; sau đó mỗi chữ 1 móc đơn (1/2 phách)
}

# ---------------------------------------------------------------- HUD công nghệ
# số rỗng cao 0,56·H ở 16:9 (mẫu); khổ dọc 0,30·H (≈ 30 % bề ngang, ở 2 mép). bong = bóng tối dưới chữ để đọc được trên nền sáng
HUD = dict(so_lon_cao={'16:9': 0.56, '9:16': 0.30}, so_net=0.016, so_lon_alpha=0.34, chu_alpha=0.66, mui_ten_alpha=0.95,
           vach_alpha=0.28, bong=0.30,
           chu_cao=0.030, chuoi=['<35468>', '<CONT.66452318>', '<0002350213802083>', '<ERROR/2B122>', '<2001/01>',
                                  '<453267>', '<12540063>', '<354554>', '(66123308)', '<2002/05>'])

# ---------------------------------------------------------------- âm thanh
AM = dict(lufs=-14.0, tp=-1.5, ket_phach=2.67, giu_hinh=0.33, den=0.13, fade_cuoi=0.025, vao_cong=0.9)
SFX = {'luot_trang': 'whoosh-short.mp3', 'lia_nhoe': 'quick-swoosh.mp3', 'manh_vo': 'swoosh.mp3',
       'glitch': 'camera-flash-1.wav', 'khoi': 'whoosh-short.mp3', 'gon_song': 'swoosh.mp3'}
SFX_DUOI_NHAC_DB = 6.0


# ================================================================ tiện ích
def moc_cat(c):
    """Giây hình đổi sang cảnh c = t0 (phách) + trễ 1 khung + lệch riêng của kiểu chuyển (gợn sóng drop đổi TRƯỚC trống)."""
    kieu = (c.get('chuyen') or {}).get('kieu', 'cat')
    return c['t0'] + TRE_CAT + CHUYEN.get(kieu, CHUYEN['cat']).get('lech', 0.0)


def ease_io(u):
    u = min(1.0, max(0.0, u)); return u * u * (3 - 2 * u)


def ease_out(u, p=3):
    u = min(1.0, max(0.0, u)); return 1 - (1 - u) ** p


def ease_in(u, p=2):
    u = min(1.0, max(0.0, u)); return u ** p


def doc_json(p):
    with open(p, encoding='utf-8') as f:
        return json.load(f)


def ghi_json(p, d):
    os.makedirs(os.path.dirname(os.path.abspath(p)), exist_ok=True)
    with open(p, 'w', encoding='utf-8') as f:
        json.dump(d, f, ensure_ascii=False, indent=1)


def run(cmd, **kw):
    r = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='replace', **kw)
    if r.returncode != 0:
        raise RuntimeError(f'Lệnh lỗi: {" ".join(map(str, cmd))[:300]}\n{r.stderr[-1500:]}')
    return r


def probe(path):
    """Thông tin video/ảnh: w, h (đã tính xoay), fps, dur, xoay, hdr."""
    r = run(['ffprobe', '-v', 'error', '-show_entries',
             'format=duration:stream=index,codec_type,width,height,r_frame_rate,color_transfer:stream_side_data=rotation:stream_tags=rotate',
             '-of', 'json', path])
    js = json.loads(r.stdout)
    v = next((s for s in js.get('streams', []) if s.get('codec_type') == 'video'), None)
    if v is None:
        return None
    rot = 0
    for sd in v.get('side_data_list', []) or []:
        if 'rotation' in sd:
            rot = int(float(sd['rotation']))
    if 'tags' in v and 'rotate' in v['tags']:
        rot = int(v['tags']['rotate'])
    w, h = int(v['width']), int(v['height'])
    if abs(rot) % 180 == 90:
        w, h = h, w
    num, den = (v.get('r_frame_rate') or '0/1').split('/')
    fps = float(num) / float(den) if float(den) else 0
    dur = float(js.get('format', {}).get('duration') or 0)
    return dict(w=w, h=h, fps=fps, dur=dur, xoay=rot, hdr=v.get('color_transfer') in ('arib-std-b67', 'smpte2084'))


def font(ten):
    p = os.path.join(FONT_DIR, ten)
    if os.path.exists(p):
        return p
    for d in (r'C:\Windows\Fonts', '/usr/share/fonts', '/Library/Fonts'):
        q = os.path.join(d, ten)
        if os.path.exists(q):
            return q
    raise FileNotFoundError(f'Thiếu phông {ten} (đặt vào {FONT_DIR})')


def font_hud():
    for p in (r'C:\Windows\Fonts\consolab.ttf', r'C:\Windows\Fonts\consola.ttf', os.path.join(FONT_DIR, 'BarlowCondensed-ExtraBold.ttf')):
        if os.path.exists(p):
            return p
    return font('BarlowCondensed-ExtraBold.ttf')


VIDEO_EXT = ('.mp4', '.mov', '.m4v', '.mkv', '.avi', '.webm', '.mts', '.3gp')
ANH_EXT = ('.jpg', '.jpeg', '.png', '.webp', '.bmp', '.heic')
NHAC_EXT = ('.mp3', '.m4a', '.wav', '.aac', '.flac', '.ogg', '.opus')


def tim_file(res, ten):
    """Đường dẫn nguồn: tuyệt đối hoặc tên file trong thư mục Resources."""
    if not ten:
        return None
    if os.path.isabs(ten) and os.path.exists(ten):
        return ten
    p = os.path.join(res or '', ten)
    return p if os.path.exists(p) else None


def in_ra(*a):
    print(*a, flush=True)
