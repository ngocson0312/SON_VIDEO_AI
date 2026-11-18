# -*- coding: utf-8 -*-
"""dung.py — dựng video: cửa sổ video (cắt theo nội dung) + bảng minh hoạ vẽ tay + sub karaoke + SFX + nhạc, −14 LUFS.
  dung.py xem  <T1> <T2> ...   → ảnh xem thử đúng giây ra (T tính theo video thành phẩm)
  dung.py am                   → dựng âm thanh (giọng + SFX + nhạc, −14 LUFS)
  dung.py hinh                 → dựng hình (không tiếng)
  dung.py full                 → am + hinh + ghép
"""
import os, sys, json, math, subprocess, time
import numpy as np, cv2
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ve import *
import canh, sub as SUB, cta3d
from hinh import board_bg
from canh import BW, BH, pop, pill

HERE = os.path.dirname(os.path.abspath(__file__))
SFXDIR = os.path.abspath(os.path.join(HERE, '..', 'assets', 'sfx'))
# Đường dẫn: đặt biến môi trường GYM_SRC (video thô), GYM_WORK (thư mục làm việc), GYM_OUT (file ra); mặc định = bản chạy mẫu Vinh.
SRC = os.environ.get('GYM_SRC', r'D:\____TTT_____\KH_Test\Vinh\Vinh\Video_Hướng dẫn\Video_Thô.MOV')
WORK = os.environ.get('GYM_WORK', r'D:\____TTT_____\KH_Test\Vinh\Vinh\Video_Hướng dẫn\work_edit')
OUT = os.environ.get('GYM_OUT', os.path.join(os.path.dirname(WORK), os.path.splitext(os.path.basename(SRC))[0] + '_EDIT.mp4'))
FPS = 30
SW, SH = 1080, 1920
HOOK = (147.75, 151.45)           # đoạn lời mở đầu (teaser) lấy từ cuối video
D0 = round(HOOK[1] - HOOK[0], 2)  # 3.70
SRC_DUR = 154.567
EXTRA = 0.5                      # kéo dài đuôi (giữ hình cuối) cho màn CTA FOLLOW diễn đủ
END_TS = SRC_DUR + EXTRA
TOT = D0 + SRC_DUR + EXTRA

# VÙNG AN TOÀN TikTok / Reels / Shorts: chữ nằm trong x 60-940, y 150-1480 (trên: thanh tìm kiếm; dưới: tên + mô tả; phải: cột nút)
VX, VY, VW, VH = 0, 810, 1080, 1110        # video người Ở DƯỚI, tràn hết đáy (mặt / tay / sub nằm trên y 1480), bảng minh hoạ Ở TRÊN
BSC = 0.93                      # bảng vẽ (1008x736) thu lại cho vừa vùng an toàn
BWS, BHS = int(1008 * BSC), int(736 * BSC)
BX, BY = (1080 - BWS) // 2, 112
SUB_FULL_Y = 1130

# cảnh quay gốc (cắt cứng) + khung cắt (cx, cy, cw đầu → cw cuối)
SHOTS = [(0, 28.73, 540, 955, 1080, 1010), (28.73, 32.63, 580, 1190, 1180, 1180), (32.63, 47.43, 540, 1340, 1080, 1080),
         (47.43, 74.53, 540, 1340, 1080, 1080), (74.53, 137.77, 540, 990, 1200, 1200), (137.77, 154.6, 540, 950, 1100, 1100)]
CUTS = [28.73, 32.63, 47.43, 74.53, 137.77]
PUNCH = [0.0, 11.4, 27.7, 75.0, 85.7, 94.4, 111.4, 119.3] + CUTS
FULL_OUT = 147.7

COLD = [(0.0, 1.0, 66.0), (1.0, 2.0, 108.0), (2.0, 2.9, 122.0), (2.9, 3.7, 20.0)]
COLD_TXT = [(0.0, 1.0, '2 BÀI TẬP\nĐƠN GIẢN', COL['amber']), (1.0, 2.3, 'THOÁT\nCƠN ĐAU', COL['white']), (2.3, 3.75, 'GIẢI PHÓNG\nVÙNG ĐAU', COL['mint'])]

STICKERS = [(0.15, 3.2, 'ĐAU LƯNG DƯỚI?', COL['coral']), (5.2, 7.6, 'VÕNG LƯNG', COL['amber']), (13.0, 16.0, '2 BÀI TẬP', COL['mint']),
            (30.3, 32.4, 'CƠ GẬP HÔNG', COL['coral']), (33.4, 37.4, 'LƯNG ÁP SÀN', COL['mint']), (47.6, 53.4, 'TỪNG CHÂN MỘT', COL['amber']),
            (66.8, 69.6, 'GỒNG CƠ LÕI', COL['amber']), (75.3, 79.0, 'BÀI 2 · GIÃN CƠ', COL['mint']), (98.9, 102.0, 'VUÔNG GÓC 90°', COL['amber']),
            (119.6, 123.6, 'SAI: ƯỠN LƯNG', COL['coral']), (125.0, 128.4, 'ĐÚNG: LƯNG THẲNG', COL['mint']), (143.4, 147.0, 'COMMENT NGAY', COL['ice'])]

SFX = {  # theo giây GỐC (main); cold theo T
    'cold': [(0.0, 'punch.mp3', -4), (0.0, 'swoosh.mp3', -8), (1.0, 'whoosh-short.mp3', -6), (1.02, 'punch.mp3', -6), (2.0, 'quick-swoosh.mp3', -6),
             (2.3, 'whoosh-short.mp3', -5), (2.32, 'punch.mp3', -4), (3.5, 'swoosh.mp3', -6)],
    'main': [(0.05, 'whoosh.wav', -14), (2.2, 'pop.mp3', -8), (5.4, 'pop-2.mp3', -8), (6.3, 'quick-ting.mp3', -10), (9.5, 'punch.mp3', -9),
             (11.4, 'swoosh.mp3', -9), (12.9, 'pop.mp3', -8), (17.4, 'pop.mp3', -8), (22.6, 'ting.wav', -14), (24.2, 'ting.wav', -14), (26.4, 'ting.wav', -14),
             (27.7, 'whoosh-short.mp3', -8), (29.7, 'quick-swoosh.mp3', -9), (30.8, 'pop.mp3', -8),
             (32.64, 'swoosh.mp3', -8), (32.9, 'pop.mp3', -9), (35.5, 'ding.mp3', -10), (37.7, 'pop-2.mp3', -9), (42.8, 'punch.mp3', -9),
             (47.43, 'whoosh-short.mp3', -8), (49.0, 'pop.mp3', -9), (55.0, 'click-button.mp3', -7), (55.4, 'pop.mp3', -9), (61.3, 'click-button.mp3', -7),
             (66.7, 'click-button.mp3', -7), (70.2, 'click-button.mp3', -7), (74.5, 'ding.mp3', -9), (74.6, 'sparkle.mp3', -12),
             (75.0, 'swoosh.mp3', -8), (75.15, 'punch.mp3', -9), (75.5, 'pop.mp3', -9), (84.7, 'pop-2.mp3', -8),
             (85.7, 'whoosh-short.mp3', -8), (85.95, 'pop.mp3', -9), (88.5, 'pop.mp3', -9), (90.9, 'ding.mp3', -10),
             (94.4, 'swoosh.mp3', -8), (98.9, 'pop.mp3', -8), (102.3, 'pop.mp3', -8), (104.5, 'quick-ting.mp3', -10), (114.0, 'whoosh-short.mp3', -9),
             (119.5, 'punch.mp3', -9), (124.8, 'ding.mp3', -10), (128.8, 'quick-swoosh.mp3', -9), (135.0, 'pop.mp3', -8), (137.2, 'sparkle.mp3', -11),
             (137.77, 'swoosh.mp3', -8), (138.0, 'pop.mp3', -9), (139.8, 'pop.mp3', -9), (143.0, 'pop.mp3', -9), (143.5, 'iphone-typing.mp3', -13),
             (145.5, 'pop.mp3', -9), (145.6, 'quick-ting.mp3', -11), (147.7, 'whoosh.wav', -12), (152.5, 'pop-2.mp3', -7), (153.2, 'quick-swoosh.mp3', -9)],
}


# ------------------------------------------------------------------ kế hoạch riêng từng video: <WORK>\ke_hoach.json (hoặc GYM_PLAN)
# Có file thì ĐÈ các hằng số ở trên (xem references/ke_hoach_schema.md). Không có thì chạy đúng bản mẫu Vinh.
def _probe_audio_dur(src):
    try:
        o = subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'a:0', '-show_entries', 'stream=duration', '-of', 'default=nw=1:nk=1', src],
                           capture_output=True, text=True).stdout.strip()
        return float(o)
    except Exception:
        return None


def _col(c):
    return COL[c] if isinstance(c, str) else tuple(c)


def load_plan():
    global HOOK, D0, SRC_DUR, EXTRA, END_TS, TOT, SHOTS, CUTS, PUNCH, FULL_OUT, COLD, COLD_TXT, STICKERS, SFX, SUB_FULL_Y
    p = os.environ.get('GYM_PLAN') or os.path.join(WORK, 'ke_hoach.json')
    if not os.path.exists(p): return
    k = json.load(open(p, encoding='utf-8'))
    if 'hook' in k: HOOK = tuple(k['hook'])
    SRC_DUR = k.get('src_dur') or _probe_audio_dur(SRC) or SRC_DUR
    EXTRA = k.get('extra', EXTRA)
    if 'shots' in k: SHOTS = [tuple(x) for x in k['shots']]
    if 'cuts' in k: CUTS = list(k['cuts'])
    PUNCH = list(k.get('punch', [])) + CUTS
    FULL_OUT = k.get('full_out', SRC_DUR - 7.0)
    if 'cold' in k: COLD = [tuple(x) for x in k['cold']]
    if 'cold_txt' in k: COLD_TXT = [(a, b, t, _col(c)) for a, b, t, c in k['cold_txt']]
    if 'stickers' in k: STICKERS = [(a, b, t, _col(c)) for a, b, t, c in k['stickers']]
    if 'sfx' in k: SFX = {'cold': [tuple(x) for x in k['sfx'].get('cold', [])], 'main': [tuple(x) for x in k['sfx'].get('main', [])]}
    D0 = round(HOOK[1] - HOOK[0], 2); END_TS = SRC_DUR + EXTRA; TOT = D0 + SRC_DUR + EXTRA
    # CTA: nút FOLLOW hiện, tay bấm ĐÚNG 1 lần rồi hết video (mặc định tay vào ~1,4 s trước hết lời)
    t_hand = k.get('cta', {}).get('t_hand', SRC_DUR - 1.37); t_btn = k.get('cta', {}).get('t_btn', t_hand - 0.7)
    cta3d.config(t_btn, t_hand)
    SFX['main'] += [(FULL_OUT, 'whoosh.wav', -12), (t_btn, 'pop-2.mp3', -7), (t_hand, 'quick-swoosh.mp3', -9)]
    if k.get('scenes_file'):
        import importlib.util
        sp = k['scenes_file'] if os.path.isabs(k['scenes_file']) else os.path.join(WORK, k['scenes_file'])
        spec = importlib.util.spec_from_file_location('canh_video', sp); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
        canh.SCENES = m.SCENES
    print('kế hoạch:', p)


load_plan()


# tiếng bấm (1 lần)
for _t in cta3d.tap_times(SRC_DUR + EXTRA):
    SFX['main'].append((_t, 'mouse-click.mp3', -3)); SFX['main'].append((_t + .01, 'pop.mp3', -8))


# ------------------------------------------------------------------ đọc khung nguồn
class Reader:
    def __init__(self, start=0.0, src=SRC):
        self.p = subprocess.Popen(['ffmpeg', '-v', 'error', '-ss', str(start), '-i', src, '-an', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-fps_mode', 'passthrough', '-'],
                                  stdout=subprocess.PIPE, bufsize=SW * SH * 3 * 2)
    def read(self):
        b = self.p.stdout.read(SW * SH * 3)
        if len(b) < SW * SH * 3: return None
        return np.frombuffer(b, np.uint8).reshape(SH, SW, 3).copy()
    def close(self):
        try: self.p.stdout.close(); self.p.kill()
        except Exception: pass


def one_frame(ts, src=SRC):
    r = subprocess.run(['ffmpeg', '-v', 'error', '-ss', str(ts), '-i', src, '-frames:v', '1', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], capture_output=True)
    return np.frombuffer(r.stdout, np.uint8).reshape(SH, SW, 3).copy()


# ------------------------------------------------------------------ trạng thái dựng
class Comp:
    def __init__(self):
        self.bg = self._bg()
        self.board_bg = board_bg(BW, BH)
        words = SUB.words_fixed(WORK)
        self.ph = SUB.phrases(words)
        for _i in range(len(self.ph) - 1):            # cụm sau vào là cụm trước tắt: không để 2 cụm chồng chữ
            self.ph[_i]['t1'] = min(self.ph[_i]['t1'], self.ph[_i + 1]['t0'])
        self.hook_ph = []
        for p in self.ph:
            if p['w'][0]['s'] >= HOOK[0] - 0.05 and p['w'][-1]['e'] <= HOOK[1] + 0.3:
                q = json.loads(json.dumps(p))
                for w in q['w']: w['s'] -= HOOK[0]; w['e'] -= HOOK[0]
                q['t0'] -= HOOK[0]; q['t1'] -= HOOK[0]
                self.hook_ph.append(q)
        # cụm hook: ép dòng
        self.xx = np.arange(BW, dtype=np.float32)[None, :] + 0.35 * np.arange(BH, dtype=np.float32)[:, None]
        self.rng = np.random.RandomState(7)

    def _bg(self):
        img = board_bg(SW, SH)
        yy, xx = np.mgrid[0:SH, 0:SW].astype(np.float32)
        d = np.sqrt(((xx - SW / 2) / (SW * .75)) ** 2 + ((yy - SH / 2) / (SH * .7)) ** 2)
        v = np.clip(1.0 - 0.45 * d ** 2, 0.45, 1.0)[..., None]
        return (img * v).astype(np.uint8)

    # --- toạ độ
    @staticmethod
    def full_k(T):
        if T < D0: return 1.0
        ts = T - D0
        return max(1 - eio(prog(ts, 0, 0.6)), eio(prog(ts, FULL_OUT, FULL_OUT + 0.8)))

    @staticmethod
    def shot_of(ts):
        for s in SHOTS:
            if s[0] <= ts < s[1]: return s
        return SHOTS[-1]

    def crop_for(self, ts, fk):
        s = self.shot_of(ts)
        k = prog(ts, s[0], s[1])
        cw0 = lerp(s[4], s[5], k); cy0 = s[3]; cx0 = s[2]
        cw = lerp(cw0, 1080, fk)
        cy = lerp(cy0, 960, fk); cx = lerp(cx0, 540, fk)
        # punch
        z = 1.0
        for tc in PUNCH:
            if tc <= ts < tc + 0.32: z = 1 + 0.075 * (1 - eo((ts - tc) / 0.32))
        cw = cw / z
        return cx, cy, cw

    def win_rect(self, fk):
        return (lerp(VX, 0, fk), lerp(VY, 0, fk), lerp(VW, SW, fk), lerp(VH, SH, fk))

    def draw_window(self, canvas, img, cx, cy, cw, rect, fk, extra=None):
        vx, vy, vw, vh = [int(round(v)) for v in rect]
        ch = cw * vh / vw
        x0 = (SW - cw) / 2 if cw > SW else min(max(cx - cw / 2, 0), SW - cw)
        y0 = min(max(cy - ch / 2, 0), SH - ch) if ch < SH else 0
        s = vw / cw
        M = np.array([[s, 0, -x0 * s], [0, s, -y0 * s]], np.float32)
        w = cv2.warpAffine(img, M, (vw, vh), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
        if extra: w = extra(w)
        # chỉnh màu nhẹ: tương phản + bão hoà
        w = cv2.convertScaleAbs(w, alpha=1.05, beta=-4)
        if fk > 0.985: canvas[vy:vy + vh, vx:vx + vw] = w
        else: paste_round(canvas, w, vx, vy, int(46 * (1 - fk)) + 1)
        if fk < 0.9:
            poly(canvas, rr_pts(vx, vy, vx + vw - 1, vy + vh - 1, 46 * (1 - fk) + 1), mix(COL['ice'], COL['ink'], .35), False, 4)
        return (vx, vy, vw, vh)

    # --- bảng
    def board(self, ts):
        idx = 0
        for i, (a, b, f) in enumerate(canh.SCENES):
            if a <= ts < b: idx = i
        if ts >= canh.SCENES[-1][1]: idx = len(canh.SCENES) - 1
        a, b, f = canh.SCENES[idx]
        cv = self.board_bg.copy(); f(cv, ts)
        d = ts - a
        TR = 0.5
        if idx > 0 and 0 <= d < TR:
            pv = self.board_bg.copy(); canh.SCENES[idx - 1][2](pv, ts)
            e = eio(d / TR); xb = lerp(-60, BW + 60 + 0.35 * BH, e)
            m = np.clip((xb - self.xx) / 16.0 + 0.5, 0, 1)[..., None]
            out = (pv * (1 - m) + cv * m).astype(np.uint8)
            edge = (np.clip(1 - np.abs(xb - self.xx) / 9.0, 0, 1) * 0.9)[..., None]
            out = np.clip(out + (np.array(COL['ice'], np.float32) - out) * edge * 0.6, 0, 255).astype(np.uint8)
            return out
        return cv

    # --- chữ đè
    def stickers(self, canvas, ts, vrect):
        vx, vy, vw, vh = vrect
        for (a, b, tx, col) in STICKERS:
            if a <= ts < b:
                k = back(prog(ts, a, a + .3)) * (1 - prog(ts, b - .2, b))
                blit(canvas, badge(tx, col, COL['ink'], 42), vx + 40 + 20, vy + 84, 1.0, k, 'l', rot=-4)
                break

    def hearts(self, canvas, ts):
        for i in range(7):
            ph = ((ts - 147.9) * 0.45 + i * 0.37) % 1.0
            x = 790 + 60 * math.sin(ph * 6 + i); y = 1040 - ph * 520
            s = 22 + 12 * (i % 3)
            a = (1 - ph) * min(1, (ts - 147.9) * 2)
            if ts < 147.9: continue
            pts = [(x + s * 16 * math.sin(t) ** 3 / 16, y - s * (13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t)) / 16)
                   for t in np.linspace(0, 2 * math.pi, 40)]
            lay_alpha(canvas, a * .9, lambda c: poly(c, pts, COL['coral'], True))

    def outro(self, canvas, ts):
        if ts < FULL_OUT + 0.4: return
        cta3d.draw(canvas, ts)
        # tắt dần cuối
        if ts > END_TS - 0.5:
            f = prog(ts, END_TS - 0.5, END_TS)
            canvas[:] = (canvas * (1 - f) + np.array(COL['ink'], np.float32) * f).astype(np.uint8)

    # --- CTA THEO DÕI: thẻ kênh + nút + bàn tay bấm + chuông + tim
    @staticmethod
    def _rot(pts, ang, c):
        a = math.radians(ang); ca, sa = math.cos(a), math.sin(a)
        return [(c[0] + (x - c[0]) * ca - (y - c[1]) * sa, c[1] + (x - c[0]) * sa + (y - c[1]) * ca) for x, y in pts]

    def hand(self, canvas, tip, sc=1.0, ang=-18, a=1.0):
        """bàn tay chỉ ngón (hoạt hình) — đầu ngón tại tip."""
        def P(x, y): return (tip[0] + x * sc, tip[1] + y * sc)
        parts = [('cap', P(0, 14), P(3, 100), 30 * sc),
                 ('rr', P(-26, 84), P(54, 170), 28 * sc),
                 ('c', P(22, 90), 15 * sc), ('c', P(38, 94), 15 * sc), ('c', P(50, 102), 15 * sc),
                 ('cap', P(-20, 128), P(-46, 104), 26 * sc),
                 ('arm', P(-22, 160), P(50, 560), 8 * sc)]

        def rot(p): return self._rot([p], ang, tip)[0]

        def draw(c):
            for out in (True, False):
                ex = 9 * sc if out else 0
                for part in parts:
                    kind = part[0]
                    colr = COL['ink'] if out else ((60, 90, 140) if kind == 'arm' else (255, 232, 214))
                    if kind == 'cap':
                        p0, p1 = rot(part[1]), rot(part[2]); w = part[3] + ex
                        cv2.line(c, (int(p0[0]), int(p0[1])), (int(p1[0]), int(p1[1])), colr, int(w), cv2.LINE_AA)
                        circle(c, p0, w / 2, colr); circle(c, p1, w / 2, colr)
                    elif kind == 'c':
                        circle(c, rot(part[1]), part[2] + ex / 2, colr)
                    else:
                        pts = [rot(q) for q in rr_pts(part[1][0] - ex / 2, part[1][1] - ex / 2, part[2][0] + ex / 2, part[2][1] + ex / 2, part[3])]
                        poly(c, pts, colr, True)
        lay_alpha(canvas, a, draw)

    def bell(self, canvas, c, ang, sc=1.0, a=1.0):
        pts = [(-24, 22), (-22, -4), (-12, -22), (0, -28), (12, -22), (22, -4), (24, 22), (32, 30), (-32, 30)]
        P = [(c[0] + x * sc, c[1] + y * sc) for x, y in pts]
        piv = (c[0], c[1] - 34 * sc)
        P = self._rot(P, ang, piv)
        cl = self._rot([(c[0], c[1] + 38 * sc)], ang, piv)[0]

        def d(cc):
            poly(cc, P, COL['ink'], True)
            poly(cc, [(piv[0] + (x - piv[0]) * .86, piv[1] + (y - piv[1]) * .86 + 3) for x, y in P], COL['amber'], True)
            circle(cc, cl, 7 * sc, COL['amber'])
        lay_alpha(canvas, a, d)

    def follow_cta(self, canvas, ts):
        T0 = 153.15
        if ts < T0: return
        k = back(prog(ts, T0, T0 + 0.5))
        x0, y0, x1, y1 = 70, 1250 + (1 - k) * 160, 930, 1462 + (1 - k) * 160
        rrect(canvas, x0, y0, x1, y1, 46, (246, 249, 253), None, 0, c01(k * 1.4))
        circle(canvas, (150, y0 + 106), 62, COL['amber']); circle(canvas, (150, y0 + 106), 62, COL['ink'], False, 5)
        text(canvas, 'V', 150, y0 + 110, F_BLACK, 76, COL['ink'], c01(k * 1.4))
        text(canvas, 'HLV VINH', 238, y0 + 78, F_BLACK, 40, COL['ink'], c01(k * 1.4), 1.0, 'l')
        text(canvas, 'Giải phóng lưng · giãn cơ', 238, y0 + 126, F_M, 24, (90, 110, 140), c01(k * 1.4), 1.0, 'l')
        TAP = 155.0
        bx, by = 740, y0 + 150
        if ts < TAP:
            pu = 1 + 0.035 * math.sin((ts - T0) * 7)
            for i in range(2):                                   # sóng lan quanh nút
                ph = ((ts - T0) * 1.1 + i * .5) % 1.0
                rrect(canvas, bx - 125 - 40 * ph, by - 44 - 20 * ph, bx + 125 + 40 * ph, by + 44 + 20 * ph, 50, None, COL['coral'], 4, (1 - ph) * .7 * c01(k))
            rrect(canvas, bx - 125 * pu, by - 46 * pu, bx + 125 * pu, by + 46 * pu, 46, COL['coral'], None, 0, c01(k * 1.4))
            text(canvas, '+ THEO DÕI', bx, by + 2, F_BLACK, 38, COL['white'], c01(k * 1.4), pu)
        else:
            e = back(prog(ts, TAP, TAP + 0.3))
            rrect(canvas, bx - 125, by - 46, bx + 125, by + 46, 46, (232, 238, 246), COL['mint'], 4, 1.0)
            text(canvas, 'ĐÃ THEO DÕI', bx + 14, by + 2, F_BLACK, 31, (60, 90, 120), 1.0, e)
            check(canvas, (bx - 92, by + 3), 15 * e, COL['mint'], 1.0, 8)
            swing = 24 * math.exp(-(ts - TAP) * 2.2) * math.sin((ts - TAP) * 20)       # chuông rung
            self.bell(canvas, (880, y0 + 64), swing, 1.0, c01((ts - TAP) * 6))
            ph = c01((ts - TAP) / 0.55)                                                 # ripple + tia
            if ph < 1:
                circle(canvas, (bx + 20, by + 10), 20 + 150 * eo(ph), COL['white'], False, max(2, int(10 * (1 - ph))))
                for i in range(10):
                    an = i * math.pi / 5 + .3
                    r0 = 70 + 80 * eo(ph); r1 = r0 + 30 * (1 - ph)
                    line(canvas, (bx + 20 + r0 * math.cos(an), by + 10 + r0 * math.sin(an)), (bx + 20 + r1 * math.cos(an), by + 10 + r1 * math.sin(an)), COL['amber'], 6)
            for i in range(9):                                                          # tim bay
                u = c01((ts - TAP - 0.05 - i * .07) / 1.5)
                if u <= 0 or u >= 1: continue
                hx = bx + (i - 4) * 38 + 26 * math.sin(u * 5 + i); hy = by - 40 - u * 300
                sz = 16 + 9 * (i % 3)
                pts = [(hx + sz * 16 * math.sin(t) ** 3 / 16, hy - sz * (13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t)) / 16) for t in np.linspace(0, 2 * math.pi, 36)]
                lay_alpha(canvas, (1 - u) * .95, lambda c, pts=pts: poly(c, pts, COL['coral'], True))
        # bàn tay: vào -> di chuyển -> bấm -> rút
        if ts >= 153.8:
            tgt = (bx + 14, by + 14); st = (1010, 1700)
            if ts < 154.95:
                u = eio(prog(ts, 153.8, 154.9)); tip = (lerp(st[0], tgt[0], u) + 40 * math.sin(u * math.pi), lerp(st[1], tgt[1], u)); sc = 1.0
            elif ts < 155.6:
                press = math.sin(math.pi * c01((ts - 154.95) / 0.3)) if ts < 155.25 else 0
                tip = (tgt[0], tgt[1] + 10 * press); sc = 1.0 - 0.07 * press
            else:
                u = eio(prog(ts, 155.6, 156.4)); tip = (lerp(tgt[0], 1020, u), lerp(tgt[1], 1720, u)); sc = 1.0
            ha = 1.0 if ts < 156.2 else 1 - prog(ts, 156.2, 156.6)
            self.hand(canvas, tip, sc, -18, ha)

    # --- mở đầu
    def cold_texts(self, canvas, T):
        for (a, b, tx, col) in COLD_TXT:
            if a <= T < b:
                k = back(prog(T, a, a + .22))
                sh = 14 * max(0, 1 - (T - a) / .35)
                ox = self.rng.randn() * sh; oy = self.rng.randn() * sh
                sc = lerp(1.9, 1.0, k)
                size = 150 if '\n' in tx and len(tx) < 16 else 126
                extc = COL['coral'] if col == COL['white'] else (COL['coral'] if col == COL['amber'] else (20, 120, 100))
                blit(canvas, sprite(tx, F_BLACK, size, col, 11, COL['ink'], (extc, 18), 1.02), 540 + ox, 1050 + oy, c01(k * 2) * (1 - prog(T, b - .08, b)), sc, 'c', rot=-3)

    def render(self, T, src=None, cold=None):
        canvas = self.bg.copy()
        if src is not None:      # nền = chính khung hình làm mờ + tối (lấp vùng trống ở trên / dưới)
            sm = cv2.resize(src, (36, 64), interpolation=cv2.INTER_AREA)
            big = cv2.resize(sm, (SW, SH), interpolation=cv2.INTER_CUBIC)
            canvas = (big * 0.30 + canvas * 0.70).astype(np.uint8)
        fk = self.full_k(T)
        if T < D0:
            # --- cold open
            idx = [i for i, c in enumerate(COLD) if c[0] <= T < c[1]]
            sh = COLD[idx[0]] if idx else COLD[-1]
            tt = T - sh[0]
            z = 1.0 + 0.16 * tt / (sh[1] - sh[0]) + 0.09 * (1 - eo(tt / .25))
            cw = 1080 / z
            vr = (0, 0, SW, SH)
            ex = None
            if tt < 0.2:
                sft = int(14 * (1 - tt / .2))
                def ex(w, sft=sft):
                    w = w.copy(); w[..., 0] = np.roll(w[..., 0], sft, 1); w[..., 2] = np.roll(w[..., 2], -sft, 1); return w
            self.draw_window(canvas, cold, 540, 960, cw, vr, 1.0, ex)
            # tối nhẹ phần dưới để chữ nổi
            g = np.linspace(0, 1, SH, dtype=np.float32)[:, None, None]
            canvas[:] = (canvas * (1 - 0.5 * np.clip((g - 0.35) / 0.65, 0, 1))).astype(np.uint8)
            self.cold_texts(canvas, T)
            for p in self.hook_ph: SUB.draw_sub(canvas, p, T, 540, 1380, 58, 800)
            if T < 0.12: canvas[:] = np.clip(canvas.astype(np.int16) + int(255 * (1 - T / .12)), 0, 255).astype(np.uint8)
            if T > D0 - 0.12: canvas[:] = np.clip(canvas.astype(np.int16) + int(255 * (T - (D0 - .12)) / .12), 0, 255).astype(np.uint8)
        else:
            ts = T - D0
            cx, cy, cw = self.crop_for(ts, fk)
            ex = None
            for tc in CUTS:
                if tc <= ts < tc + 0.2:
                    sft = int(12 * (1 - (ts - tc) / .2))
                    def ex(w, sft=sft):
                        w = w.copy(); w[..., 0] = np.roll(w[..., 0], sft, 1); w[..., 2] = np.roll(w[..., 2], -sft, 1); return w
            vr = self.draw_window(canvas, src, cx, cy, cw, self.win_rect(fk), fk, ex)
            # chớp trắng ở cú cắt
            for tc in CUTS + [0.0]:
                if tc <= ts < tc + 0.17:
                    a = 0.5 * (1 - (ts - tc) / .17)
                    canvas[:] = np.clip(canvas.astype(np.float32) * (1 - a) + 255 * a, 0, 255).astype(np.uint8)
            by = lerp(BY, -BHS - 12, fk)
            if by > -BHS:
                bd = cv2.resize(self.board(ts), (BWS, BHS), interpolation=cv2.INTER_AREA)
                paste_round(canvas, bd, BX, int(by), 34)
                poly(canvas, [(x + BX, y + int(by)) for x, y in rr_pts(0, 0, BWS - 1, BHS - 1, 34)], mix(COL['ice'], COL['ink'], .35), False, 4)
            if fk < 0.5: self.stickers(canvas, ts, vr)
            ysub = lerp(1410, SUB_FULL_Y, fk)
            for p in self.ph:
                if p['t0'] - 0.05 <= ts <= p['t1']: SUB.draw_sub(canvas, p, ts, 540, ysub, 52 if fk < 0.5 else 56, 800)
            self.outro(canvas, ts)
        # thanh tiến độ
        cv2.rectangle(canvas, (60, 98), (1020, 103), (24, 44, 70), -1)
        cv2.rectangle(canvas, (60, 98), (60 + int(960 * T / TOT), 103), COL['amber'], -1)
        return canvas


# ------------------------------------------------------------------ xem thử
def imsave(path, bgr, q=88):
    """cv2.imwrite không ghi được đường dẫn có dấu tiếng Việt → ghi qua imencode."""
    ok, buf = cv2.imencode('.jpg', bgr, [cv2.IMWRITE_JPEG_QUALITY, q])
    with open(path, 'wb') as f: f.write(buf.tobytes())


def cmd_xem(Ts):
    C = Comp()
    outs = []
    for T in Ts:
        if T < D0:
            sh = [c for c in COLD if c[0] <= T < c[1]] or [COLD[-1]]
            sh = sh[0]; cold = one_frame(sh[2] + (T - sh[0]))
            im = C.render(T, None, cold)
        else:
            im = C.render(T, one_frame(min(T - D0, SRC_DUR - 0.2)), None)
        outs.append(im)
    if os.environ.get('GUIDE'):
        for im in outs:
            cv2.rectangle(im, (60, 150), (940, 1480), (255, 0, 0), 3)
    pth = os.path.join(WORK, 'xem.jpg')
    sm = [cv2.resize(i, (540, 960), interpolation=cv2.INTER_AREA) for i in outs]
    rows = [np.hstack(sm[i:i + 4]) for i in range(0, len(sm), 4)]
    wd = max(r.shape[1] for r in rows)
    rows = [np.pad(r, ((0, 0), (0, wd - r.shape[1]), (0, 0))) for r in rows]
    imsave(pth, cv2.cvtColor(np.vstack(rows), cv2.COLOR_RGB2BGR))
    if len(outs) <= 2:
        imsave(os.path.join(WORK, 'xem_full.jpg'), cv2.cvtColor(np.hstack(outs), cv2.COLOR_RGB2BGR), 92)
    print('→', pth)


# ------------------------------------------------------------------ dựng hình
def cmd_hinh(out_silent, t_from=0.0, t_to=None):
    C = Comp()
    n = int(round(TOT * FPS)); i0 = int(round(t_from * FPS)); i1 = n if t_to is None else min(n, int(round(t_to * FPS)))
    ff = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{SW}x{SH}', '-r', str(FPS), '-i', '-',
                           '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '17', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', out_silent],
                          stdin=subprocess.PIPE)
    cold_rd = None; cold_i = -1; main = None; last = None
    t0 = time.time()
    for i in range(i0, i1):
        T = i / FPS
        if T < D0:
            ci = [k for k, c in enumerate(COLD) if c[0] <= T < c[1]]; ci = ci[0] if ci else len(COLD) - 1
            if ci != cold_i:
                if cold_rd: cold_rd.close()
                cold_rd = Reader(COLD[ci][2]); cold_i = ci
            fr = cold_rd.read()
            if fr is None: fr = np.zeros((SH, SW, 3), np.uint8)
            im = C.render(T, None, fr)
        else:
            if main is None:
                main = Reader(max(0.0, T - D0))
            fr = main.read()
            if fr is None: fr = last if last is not None else np.zeros((SH, SW, 3), np.uint8)
            last = fr
            im = C.render(T, fr, None)
        ff.stdin.write(im.tobytes())
        if i % 150 == 0: print(f'{i}/{n}  {time.time() - t0:.0f}s', flush=True)
    ff.stdin.close(); ff.wait()
    print('hình xong', out_silent)


# ------------------------------------------------------------------ âm thanh
def cmd_am(out_wav):
    import nhac
    bgm = os.path.join(WORK, 'nhac_nen.wav')
    if not os.path.exists(bgm): nhac.tao(bgm, TOT + 1.0)
    ins = ['-i', SRC, '-i', bgm]
    sfx = [(t, n, d) for (t, n, d) in SFX['cold']] + [(t + D0, n, d) for (t, n, d) in SFX['main']]
    for (t, n, d) in sfx: ins += ['-i', os.path.join(SFXDIR, n)]
    fc = []
    fc.append(f'[0:a]atrim={HOOK[0]}:{HOOK[1]},asetpts=PTS-STARTPTS,afade=t=in:d=0.02,afade=t=out:st={D0 - 0.05}:d=0.05[h]')
    fc.append(f'[0:a]atrim=0:{SRC_DUR},asetpts=PTS-STARTPTS[m]')
    fc.append('[h][m]concat=n=2:v=0:a=1,aformat=sample_rates=44100:channel_layouts=stereo,highpass=f=75,'
              f'acompressor=threshold=0.05:ratio=3:attack=8:release=160:makeup=2,apad=whole_dur={TOT + 0.5},asplit=2[v][vs]')
    labs = []
    for k, (t, n, d) in enumerate(sfx):
        ms = int(t * 1000)
        fc.append(f'[{k + 2}:a]aformat=sample_rates=44100:channel_layouts=stereo,volume={d}dB,adelay={ms}|{ms}[s{k}]')
        labs.append(f'[s{k}]')
    fc.append(''.join(labs) + f'amix=inputs={len(labs)}:normalize=0:dropout_transition=0,volume=1.0[fx]')
    fc.append(f'[1:a]aformat=sample_rates=44100:channel_layouts=stereo,volume=-17dB,atrim=0:{TOT},asetpts=PTS-STARTPTS[b0]')
    fc.append('[b0][vs]sidechaincompress=threshold=0.03:ratio=6:attack=15:release=450[b]')
    fc.append('[v][fx][b]amix=inputs=3:normalize=0:dropout_transition=0,alimiter=limit=0.95[mix]')
    fc.append('[mix]loudnorm=I=-14:TP=-1.5:LRA=11[out]')
    cmd = ['ffmpeg', '-v', 'error', '-y'] + ins + ['-filter_complex', ';'.join(fc), '-map', '[out]', '-t', f'{TOT:.3f}', '-ar', '44100', '-c:a', 'pcm_s16le', out_wav]
    subprocess.run(cmd, check=True)
    print('âm xong', out_wav)


def cmd_full():
    sil = os.path.join(WORK, 'hinh_cam.mp4'); wav = os.path.join(WORK, 'am_thanh.wav')
    cmd_am(wav)
    cmd_hinh(sil)
    out = OUT
    n = 2
    while os.path.exists(out):
        out = OUT.replace('.mp4', f'_ban{n}.mp4'); n += 1
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', sil, '-i', wav, '-c:v', 'copy', '-c:a', 'aac', '-b:a', '256k', '-shortest', out], check=True)
    print('XONG →', out)


if __name__ == '__main__':
    a = sys.argv[1]
    if a == 'xem': cmd_xem([float(x) for x in sys.argv[2:]])
    elif a == 'am': cmd_am(os.path.join(WORK, 'am_thanh.wav'))
    elif a == 'hinh': cmd_hinh(os.path.join(WORK, 'hinh_cam.mp4'), *( [float(x) for x in sys.argv[2:]] ))
    elif a == 'ghep':
        sil = os.path.join(WORK, 'hinh_cam.mp4'); wav = os.path.join(WORK, 'am_thanh.wav'); out = OUT; n = 2
        while os.path.exists(out): out = OUT.replace('.mp4', f'_ban{n}.mp4'); n += 1
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', sil, '-i', wav, '-c:v', 'copy', '-c:a', 'aac', '-b:a', '256k', '-shortest', out], check=True); print('XONG →', out)
    elif a == 'full': cmd_full()
