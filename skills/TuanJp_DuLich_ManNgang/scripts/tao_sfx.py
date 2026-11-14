# -*- coding: utf-8 -*-
"""tao_sfx.py — TỰ TỔNG HỢP SFX: boom.wav (cú DROP tên chủ đề, tiếng nổ trầm điện ảnh) + tiếng kỹ xảo cao trào 30 s đầu:
vo_kinh.wav (vỡ kính), xoay.wav (whoosh xoay, đỉnh 0,36 s), glitch.wav (glitch số).
Không lấy mẫu từ đâu (sóng sin quét + hài + ồn lọc) → dùng tự do. Chạy lại: python -I -X utf8 scripts/tao_sfx.py

Loa điện thoại không phát được dưới ~100 Hz → ngoài sóng trầm 110 → 38 Hz còn có HÀI bậc 3 và cú đập ồn dải 150–500 Hz
để tiếng nổ vẫn nghe thấy trên điện thoại / laptop."""
import subprocess
from pathlib import Path

import numpy as np

SR = 48000
OUT = Path(__file__).resolve().parent.parent / 'assets' / 'sfx'


def _loc_thong(x, fc):          # lọc thông thấp 1 cực
    a = np.exp(-2 * np.pi * fc / SR)
    y = np.zeros_like(x)
    acc = 0.0
    for i, v in enumerate(x):
        acc = (1 - a) * v + a * acc
        y[i] = acc
    return y


def boom(dai=1.7, seed=7):
    t = np.arange(int(dai * SR)) / SR
    f = 38 + (110 - 38) * np.exp(-t / .16)                    # quét tần số 110 → 38 Hz
    pha = 2 * np.pi * np.cumsum(f) / SR
    env = (1 - np.exp(-t / .004)) * np.exp(-t / .55)
    trau = np.sin(pha) * env
    hai = .32 * np.sin(3 * pha) * (1 - np.exp(-t / .003)) * np.exp(-t / .22)     # hài bậc 3: nghe được trên loa nhỏ
    rng = np.random.default_rng(seed)
    n = rng.standard_normal(len(t))
    dap = _loc_thong(n, 500) - _loc_thong(n, 150)                                 # ồn dải 150–500 Hz
    dap = dap / (np.abs(dap).max() + 1e-9) * .9 * np.exp(-t / .07)
    x = trau + hai + dap
    x[-int(.05 * SR):] *= np.linspace(1, 0, int(.05 * SR))
    x = x / np.abs(x).max() * 10 ** (-1 / 20)
    return np.stack([x, x], 1).astype(np.float32)


def _chuan(x, db=-1):
    return x / (np.abs(x).max() + 1e-9) * 10 ** (db / 20)


def _leng_keng(n, rng, so=90):
    """mảnh kính nhỏ rơi: tiếng 'ting' 2,5–9 kHz (bội 2,76 — kim loại / kính), phần lớn trong 0,5 s đầu, nhỏ dần."""
    x = np.zeros(n)
    dai = n / SR
    for _ in range(so):
        t0 = min(dai - .15, rng.exponential(.17) + .004)
        f = rng.uniform(2500, 9000)
        tau = rng.uniform(.012, .06)
        a = rng.uniform(.15, .5) * np.exp(-t0 / .5)
        i0 = int(t0 * SR)
        m = min(n - i0, int(tau * 6 * SR))
        tt = np.arange(m) / SR
        env = np.exp(-tt / tau) * (1 - np.exp(-tt / .0008))
        x[i0:i0 + m] += a * env * (np.sin(2 * np.pi * f * tt) + .45 * np.sin(2 * np.pi * f * 2.76 * tt + 1.3))
    return x


def vo_kinh(dai=1.5, seed=11):
    """VỠ KÍNH: cú va (ồn cao tần + 'thịch' 95 Hz) → rắc rắc dải 2–7 kHz có hạt → mảnh leng keng rơi (L / R khác nhau cho rộng)."""
    n = int(dai * SR)
    t = np.arange(n) / SR
    rng = np.random.default_rng(seed)
    no = rng.standard_normal(n)
    va = (no - _loc_thong(no, 1800)) * (1 - np.exp(-t / .0015)) * np.exp(-t / .035)
    va = va / (np.abs(va).max() + 1e-9) + .55 * np.sin(2 * np.pi * 95 * t) * (1 - np.exp(-t / .002)) * np.exp(-t / .07)
    bp = _loc_thong(no, 7000) - _loc_thong(no, 2200)
    hat = np.convolve((rng.random(n) < .012).astype(float), np.exp(-np.arange(240) / 40), 'same')
    rac = .9 * bp / (np.abs(bp).max() + 1e-9) * np.exp(-t / .22) * (.35 + np.minimum(hat, 1.5))
    goc = va + rac
    L = goc + _leng_keng(n, np.random.default_rng(seed + 1))
    R = goc + _leng_keng(n, np.random.default_rng(seed + 2))
    x = np.stack([L, R], 1)
    x[-int(.08 * SR):] *= np.linspace(1, 0, int(.08 * SR))[:, None]
    return _chuan(x).astype(np.float32)


def xoay(dai=.75, dinh=.36, seed=5):
    """WHOOSH XOAY: ồn qua lọc dải quét 300 → 3200 → 500 Hz, đỉnh đúng `dinh` (cú cắt), lia trái → phải."""
    n = int(dai * SR)
    t = np.arange(n) / SR
    no = np.random.default_rng(seed).standard_normal(n)
    fc = 300 + 2900 * np.exp(-((t - dinh) / .15) ** 2)
    y = np.zeros(n)
    low = band = 0.0
    for i in range(n):                         # lọc biến trạng thái (state-variable), tâm đổi theo từng mẫu
        f = 2 * np.sin(np.pi * fc[i] / SR)
        high = no[i] - low - .7 * band
        band += f * high
        low += f * band
        y[i] = band
    sig = np.where(t < dinh, .17, .10)
    x = y * np.exp(-((t - dinh) / sig) ** 2)
    p = 1 / (1 + np.exp(-(t - dinh) / .08))
    return _chuan(np.stack([x * (1.15 - .7 * p), x * (.45 + .7 * p)], 1)).astype(np.float32)


def glitch(dai=.42, seed=3):
    """GLITCH SỐ: chuỗi đoạn 18–60 ms ngẫu nhiên — xung vuông, ồn nén bit giữ mẫu, blip cao, khoảng lặng — mở bằng tiếng 'tạch'."""
    n = int(dai * SR)
    rng = np.random.default_rng(seed)
    x = np.zeros(n)
    i = 0
    while i < n:
        m = min(n - i, int(rng.uniform(.018, .06) * SR))
        tt = np.arange(m) / SR
        k = rng.random()
        if k < .3:
            s = np.sign(np.sin(2 * np.pi * rng.uniform(120, 1800) * tt))
        elif k < .6:
            buoc = int(rng.integers(6, 20))
            s = np.repeat(rng.uniform(-1, 1, m // buoc + 1), buoc)[:m]
            s = np.round(s * 3) / 3
        elif k < .8:
            s = np.sin(2 * np.pi * rng.uniform(2000, 5000) * tt)
        else:
            s = np.zeros(m)
        r = min(m // 2, int(.001 * SR))
        env = np.ones(m)
        if r:
            env[:r] = np.linspace(0, 1, r)
            env[-r:] = np.linspace(1, 0, r)
        x[i:i + m] = s * env * rng.uniform(.5, 1)
        i += m
    t = np.arange(n) / SR
    no = np.random.default_rng(seed + 9).standard_normal(n)
    x += 1.2 * (no - _loc_thong(no, 2500)) * np.exp(-t / .012)          # 'tạch' đầu
    x *= np.minimum(1, (dai - t) / .05)
    L = x
    R = np.roll(x, int(.004 * SR))
    return _chuan(np.stack([L, R], 1)).astype(np.float32)


def ghi(p, a):
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'f32le', '-ac', '2', '-ar', str(SR), '-i', '-', '-c:a', 'pcm_s16le', str(p)],
                   input=a.tobytes(), check=True)


if __name__ == '__main__':
    for ten, ham in (('boom.wav', boom), ('vo_kinh.wav', vo_kinh), ('xoay.wav', xoay), ('glitch.wav', glitch)):
        ghi(OUT / ten, ham())
        print('→', OUT / ten)
