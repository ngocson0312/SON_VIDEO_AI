"""Tạo nhạc nền mẫu (beat + bass + pluck) bằng numpy khi người dùng chưa đưa nhạc.
Dùng: python nhac_mau.py --bpm 100 --giay 40 --out nhac_mau.wav
Chỉ là nhạc THAY THẾ tạm — có file nhạc thật thì dùng cờ nhac trong ke_hoach.json."""
import argparse, wave
import numpy as np

SR = 44100


def env(n, a=0.002, d=0.1):
    t = np.arange(n) / SR
    return np.minimum(1, t / a) * np.exp(-t / d)


def kick(n=int(SR * 0.3)):
    t = np.arange(n) / SR
    f = 50 + 110 * np.exp(-t * 28)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 9)


def hat(n=int(SR * 0.06)):
    r = np.random.RandomState(1).randn(n)
    r = np.diff(r, prepend=0)
    return r * np.exp(-np.arange(n) / SR * 80) * 0.5


def clap(n=int(SR * 0.18)):
    r = np.random.RandomState(2).randn(n)
    return r * np.exp(-np.arange(n) / SR * 22) * 0.6


def pluck(freq, dur=0.34):
    n = int(SR * dur)
    t = np.arange(n) / SR
    w = (np.sin(2 * np.pi * freq * t) + 0.4 * np.sin(4 * np.pi * freq * t) + 0.2 * np.sin(6 * np.pi * freq * t))
    return w * np.exp(-t * 7) * 0.5


def bass(freq, dur):
    n = int(SR * dur)
    t = np.arange(n) / SR
    return np.sin(2 * np.pi * freq * t) * np.minimum(1, t / 0.01) * np.exp(-t * 2.2) * 0.8


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--bpm", type=float, default=100)
    ap.add_argument("--giay", type=float, default=40)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    beat = 60.0 / a.bpm
    n = int(SR * (a.giay + 1))
    y = np.zeros(n)

    def put(sig, t, g=1.0):
        i = int(t * SR)
        if i >= n:
            return
        j = min(n, i + len(sig))
        y[i:j] += sig[: j - i] * g

    # Am - F - C - G (mỗi hợp âm 4 phách = 1 ô nhịp)
    roots = [55.0, 43.65, 65.41, 49.0]
    chords = [[220.0, 261.63, 329.63], [174.61, 220.0, 261.63], [261.63, 329.63, 392.0], [196.0, 246.94, 293.66]]
    k = kick(); h = hat(); c = clap()
    nb = int(a.giay / beat) + 2
    for b in range(nb):
        t = b * beat
        bar = (b // 4) % 4
        if b >= 0:
            put(k, t, 1.0)
            put(h, t + beat / 2, 0.55)
            put(h, t + beat / 4, 0.25)
            put(h, t + 3 * beat / 4, 0.25)
        if b % 4 in (1, 3):
            put(c, t, 0.9)
        if b % 2 == 0:
            put(bass(roots[bar], beat * 1.8), t, 0.9)
        # pluck arpeggio nửa phách
        ch = chords[bar]
        put(pluck(ch[(b * 2) % 3]), t, 0.5)
        put(pluck(ch[(b * 2 + 1) % 3] * 2), t + beat / 2, 0.45)
    y = np.tanh(y * 0.9)
    y = y / (np.abs(y).max() + 1e-9) * 0.85
    fade = int(SR * 1.2)
    y[-fade:] *= np.linspace(1, 0, fade)
    pcm = (np.stack([y, y], 1) * 32767).astype(np.int16)
    with wave.open(a.out, "wb") as f:
        f.setnchannels(2); f.setsampwidth(2); f.setframerate(SR)
        f.writeframes(pcm.tobytes())
    print("nhạc mẫu:", a.out)


if __name__ == "__main__":
    main()
