# -*- coding: utf-8 -*-
"""nhac.py — tự tạo nhạc nền êm (pad + arpeggio + kick nhẹ) cho video giải thích. Không cần file nhạc ngoài."""
import numpy as np, wave

SR = 44100


def _env(n, a=0.01, r=0.2):
    e = np.ones(n); na = int(a * SR); nr = int(r * SR)
    e[:na] = np.linspace(0, 1, na); e[-nr:] = np.linspace(1, 0, nr) if nr < n else e[-nr:]
    return e


def tao(path, dur, bpm=92):
    n = int(dur * SR); out = np.zeros((n, 2), np.float64)
    beat = 60.0 / bpm; bar = beat * 4
    # Am – F – C – G
    chords = [[57, 60, 64, 69], [53, 57, 60, 65], [48, 55, 60, 64], [55, 59, 62, 67]]
    mf = lambda m: 440.0 * 2 ** ((m - 69) / 12)
    t_all = np.arange(n) / SR
    for b in range(int(dur / bar) + 2):
        ch = chords[b % 4]; t0 = b * bar; i0 = int(t0 * SR); L = int(bar * SR)
        if i0 >= n: break
        L = min(L, n - i0); tt = np.arange(L) / SR
        pad = np.zeros(L)
        for m in ch:
            f = mf(m)
            for det in (-0.4, 0.0, 0.5):
                pad += np.sin(2 * np.pi * (f + det) * tt) + 0.3 * np.sin(4 * np.pi * (f + det) * tt)
        e = np.minimum(1, tt / 0.6) * np.minimum(1, (bar - tt) / 0.6)
        out[i0:i0 + L, 0] += pad * e * 0.020; out[i0:i0 + L, 1] += pad * e * 0.020
        # arpeggio (pluck) nốt 8
        for k in range(8):
            m = ch[k % 4] + (12 if k % 4 == 3 else 12)
            ts = t0 + k * beat / 2; i1 = int(ts * SR)
            if i1 >= n: break
            ll = min(int(0.5 * SR), n - i1); x = np.arange(ll) / SR
            nt = np.sin(2 * np.pi * mf(m) * x) * np.exp(-x * 7) * 0.05
            pan = 0.3 + 0.4 * ((k % 2))
            out[i1:i1 + ll, 0] += nt * (1 - pan); out[i1:i1 + ll, 1] += nt * pan
        # kick nhẹ + hat
        for k in range(4):
            ts = t0 + k * beat; i1 = int(ts * SR)
            if i1 >= n: break
            if k % 2 == 0:
                ll = min(int(0.28 * SR), n - i1); x = np.arange(ll) / SR
                kk = np.sin(2 * np.pi * (45 + 80 * np.exp(-x * 25)) * x) * np.exp(-x * 9) * 0.16
                out[i1:i1 + ll] += kk[:, None]
            ts2 = ts + beat / 2; i2 = int(ts2 * SR)
            if i2 + 2000 < n:
                x = np.arange(2000) / SR
                h = np.random.RandomState(k + b).randn(2000) * np.exp(-x * 90) * 0.012
                out[i2:i2 + 2000] += h[:, None]
        # bass
        i3 = i0; ll = min(int(bar * SR), n - i3); x = np.arange(ll) / SR
        bs = np.sin(2 * np.pi * mf(ch[0] - 12) * x) * np.minimum(1, x / 0.05) * np.minimum(1, (bar - x) / 0.1) * 0.07
        out[i3:i3 + ll] += bs[:, None]
    out *= 1.0
    fade = np.minimum(1, np.minimum(t_all / 1.0, (dur - t_all) / 2.0))[:, None]
    out *= fade
    out = np.clip(out / (np.abs(out).max() + 1e-9) * 0.8, -1, 1)
    pcm = (out * 32767).astype(np.int16)
    with wave.open(path, 'wb') as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())
