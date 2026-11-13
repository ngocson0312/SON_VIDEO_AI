# -*- coding: utf-8 -*-
"""Tổng hợp SFX phương tiện cho đồ hoạ hành trình (không cần tải file, không bản quyền):
  jet-flyby.wav  — máy bay phản lực lướt qua (ồn dải rộng quét tần số kiểu Doppler + rền trầm)
  xe-chay.wav    — ô tô / xe chạy qua (rền động cơ + tiếng lốp)
  song-nuoc.wav  — sóng nước vỗ (ồn lọc thấp, nhịp sóng chậm)
Chạy: python -I -X utf8 scripts/tao_sfx_ht.py  → ghi vào assets/sfx/ (ghi đè)."""
import wave
from pathlib import Path

import numpy as np
from scipy.signal import butter, sosfilt

SR = 44100
RA = Path(__file__).resolve().parent.parent / 'assets' / 'sfx'
rng = np.random.default_rng(20261113)


def ghi(ten, x):
    x = x / (np.max(np.abs(x)) + 1e-9) * 0.89
    y = (x * 32767).astype(np.int16)
    with wave.open(str(RA / ten), 'wb') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes(y.tobytes())
    print('ghi', RA / ten, f'{len(x) / SR:.2f}s')


def loc_quet(x, f0, f1, khoi=1024, bac=2, kieu='band', rong=.9):
    """lọc theo khối, tần số giữa quét theo đường f(t) (mảng f0→f1 tuỳ ý)."""
    n = len(x)
    f = np.interp(np.arange(0, n, khoi), np.linspace(0, n, len(f0)), f0) if hasattr(f0, '__len__') else None
    out = np.zeros(n)
    zi = None
    for k, i in enumerate(range(0, n, khoi)):
        fc = f[k] if f is not None else f0
        if kieu == 'band':
            lo, hi = max(30, fc * (1 - rong / 2)), min(SR / 2 - 100, fc * (1 + rong / 2))
            sos = butter(bac, [lo, hi], btype='band', fs=SR, output='sos')
        else:
            sos = butter(bac, min(SR / 2 - 100, fc), btype='low', fs=SR, output='sos')
        if zi is None or zi.shape[0] != sos.shape[0]:
            zi = np.zeros((sos.shape[0], 2))
        out[i:i + khoi], zi = sosfilt(sos, x[i:i + khoi], zi=zi)
    return out


def bao(n, dinh, len_, xuong):
    t = np.linspace(0, 1, n)
    return np.where(t < dinh, (t / dinh) ** len_, ((1 - t) / (1 - dinh)) ** xuong)


def jet():
    d = 3.6; n = int(SR * d)
    on = rng.standard_normal(n)
    hong = np.cumsum(rng.standard_normal(n)); hong -= sosfilt(butter(1, 20, 'high', fs=SR, output='sos'), hong) * 0; hong = sosfilt(butter(1, 20, 'high', fs=SR, output='sos'), hong)
    # Doppler: cao lên khi tới, tụt khi qua
    fq = np.concatenate([np.linspace(1400, 3200, 60), np.linspace(3200, 900, 40)])
    a = loc_quet(on, fq, None, rong=1.2) * 1.0
    b = sosfilt(butter(2, [60, 240], 'band', fs=SR, output='sos'), hong) * 0.35
    s = loc_quet(on, np.concatenate([np.linspace(5000, 8000, 60), np.linspace(8000, 2500, 40)]), None, rong=.6) * .25
    x = (a + b + s) * bao(n, .58, 2.2, 1.6)
    return x


def xe():
    d = 2.6; n = int(SR * d)
    t = np.arange(n) / SR
    f = np.interp(t, [0, d * .55, d], [62, 78, 54])
    ph = 2 * np.pi * np.cumsum(f) / SR
    dong_co = sum(np.sin(k * ph) / k for k in range(1, 9))
    dong_co = sosfilt(butter(2, 900, 'low', fs=SR, output='sos'), dong_co)
    lop = sosfilt(butter(2, [300, 2400], 'band', fs=SR, output='sos'), rng.standard_normal(n)) * .6
    x = (dong_co * .7 + lop) * bao(n, .55, 1.8, 1.4)
    return x


def song():
    d = 3.2; n = int(SR * d)
    t = np.arange(n) / SR
    on = rng.standard_normal(n)
    x = sosfilt(butter(2, 1100, 'low', fs=SR, output='sos'), on)
    x += sosfilt(butter(2, [1800, 5000], 'band', fs=SR, output='sos'), on) * .25
    nhip = .55 + .45 * np.sin(2 * np.pi * t / 1.6 - 1.2) ** 2
    return x * nhip * bao(n, .3, 1.2, 1.2)


if __name__ == '__main__':
    ghi('jet-flyby.wav', jet())
    ghi('xe-chay.wav', xe())
    ghi('song-nuoc.wav', song())
