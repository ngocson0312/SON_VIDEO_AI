# -*- coding: utf-8 -*-
"""tao_sfx.py — TỰ TỔNG HỢP SFX cho cú DROP tên chủ đề: assets/sfx/boom.wav (tiếng nổ trầm điện ảnh).
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


def ghi(p, a):
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'f32le', '-ac', '2', '-ar', str(SR), '-i', '-', '-c:a', 'pcm_s16le', str(p)],
                   input=a.tobytes(), check=True)


if __name__ == '__main__':
    ghi(OUT / 'boom.wav', boom())
    print('→', OUT / 'boom.wav')
