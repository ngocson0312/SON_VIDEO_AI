# -*- coding: utf-8 -*-
"""Trộn tiếng: giọng đọc + nhạc nền + SFX theo mốc -> wav 48 kHz stereo đã chuẩn −14 LUFS."""
import os
import sys
import wave

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import chung as C

SR = 48000


def _doc_wav_48k(path, tmp):
    """Đọc file âm thanh bất kỳ -> np float32 (N,2) 48 kHz (qua ffmpeg)."""
    C.chay(["ffmpeg", "-v", "error", "-y", "-i", path, "-vn", "-ac", "2", "-ar", str(SR), "-c:a", "pcm_s16le", tmp])
    with wave.open(tmp, "rb") as f:
        raw = f.readframes(f.getnframes())
    x = np.frombuffer(raw, dtype="<i2").astype(np.float32) / 32768.0
    return x.reshape(-1, 2)


def _ghi_wav(path, x):
    x = np.clip(x, -1, 1)
    with wave.open(path, "wb") as f:
        f.setnchannels(2)
        f.setsampwidth(2)
        f.setframerate(SR)
        f.writeframes((x * 32767).astype("<i2").tobytes())


def _db(x):
    return 10 ** (x / 20.0)


# SFX tự sinh làm từ nhiễu trắng (xì xào như mưa) → bỏ khi chưa có bản thật trong assets/sfx
SFX_NHIEU = {"luot", "lan", "hien", "tach", "phong", "dem"}   # "dem" tự sinh = chuỗi tick "tạch tạch tạch"


def tron(audio_goc, t_end, sfx_cues, work, nhac=None, sfx_dirs=(), nhac_db=-19.0, sfx_db=-7.0, hoa_tan_nhac=1.5):
    """Trả đường dẫn wav đã chuẩn hoá."""
    tmp = C.mkdir(os.path.join(work, "tmp_am"))
    n = int(t_end * SR)
    mix = np.zeros((n, 2), np.float32)
    giong = _doc_wav_48k(audio_goc, os.path.join(tmp, "giong48.wav"))
    # giọng: chuẩn đỉnh −3 dB trước khi trộn
    pk = float(np.max(np.abs(giong))) or 1.0
    giong = giong / pk * _db(-3)
    m = min(n, len(giong))
    mix[:m] += giong[:m]
    # nhạc nền
    if nhac and os.path.exists(nhac):
        bgm = _doc_wav_48k(nhac, os.path.join(tmp, "nhac48.wav"))
        if len(bgm) < n:
            lap = int(np.ceil(n / max(1, len(bgm))))
            bgm = np.tile(bgm, (lap, 1))
        bgm = bgm[:n].copy()
        rms = float(np.sqrt(np.mean(bgm ** 2))) or 1e-6
        bgm *= _db(nhac_db) * (_db(-3) * 0.35 / rms)   # đặt RMS nhạc thấp hơn giọng
        fo = int(hoa_tan_nhac * SR)
        if fo > 0 and n > fo:
            bgm[n - fo:] *= np.linspace(1, 0, fo)[:, None]
        fi = int(0.8 * SR)
        bgm[:fi] *= np.linspace(0, 1, fi)[:, None]
        mix += bgm
    # SFX — thưa ra: 2 tiếng cách nhau < 1,0 s thì chỉ giữ 1 (tiếng "hien" nhường tiếng quan trọng hơn);
    # nhiều tiếng dồn dập nghe như "tạch tạch tạch"
    giu = []
    for ten, t in sorted(sfx_cues, key=lambda x: x[1]):
        if giu and t - giu[-1][1] < 1.0:
            if giu[-1][0] == "hien" and ten != "hien":
                giu[-1] = (ten, t)
            continue
        giu.append((ten, t))
    sfx_cues = giu
    cache = {}
    dem = 0
    for ten, t in sfx_cues:
        if ten not in cache:
            p = None
            for d in sfx_dirs:
                for ext in (".wav", ".mp3", ".m4a", ".ogg"):
                    c = os.path.join(d, ten + ext)
                    if os.path.exists(c):
                        if ten in SFX_NHIEU and d == sfx_dirs[-1]:   # thư mục cuối = bản tự sinh
                            continue
                        p = c
                        break
                if p:
                    break
            cache[ten] = _doc_wav_48k(p, os.path.join(tmp, "sfx_%s.wav" % ten)) if p else None
        s = cache[ten]
        if s is None:
            continue
        i0 = int(max(0.0, t) * SR)
        if i0 >= n:
            continue
        k = min(len(s), n - i0)
        mix[i0:i0 + k] += s[:k] * _db(sfx_db)
        dem += 1
    # chống clip mềm
    pk = float(np.max(np.abs(mix))) or 1.0
    if pk > 0.98:
        mix = mix / pk * 0.98
    raw = os.path.join(work, "am_thanh_tho.wav")
    _ghi_wav(raw, mix)
    out = os.path.join(work, "am_thanh.wav")
    chuan_loudness(raw, out)
    print("   trộn tiếng: giọng + %s + %d SFX → %s" % ("nhạc" if nhac else "không nhạc", dem, out))
    return out


def chuan_loudness(src, dst, lufs=-14.0, tp=-1.0):
    """loudnorm 2 bước về −14 LUFS, true peak −1."""
    import json
    import re
    o = C.chay(["ffmpeg", "-nostats", "-i", src, "-af",
                "loudnorm=I=%s:TP=%s:LRA=11:print_format=json" % (lufs, tp), "-f", "null", "-"], im=True)
    m = re.search(r"\{[^{}]*\"input_i\"[^{}]*\}", o, re.S)
    if m:
        j = json.loads(m.group(0))
        af = ("loudnorm=I=%s:TP=%s:LRA=11:measured_I=%s:measured_TP=%s:measured_LRA=%s:measured_thresh=%s:"
              "offset=%s:linear=true:print_format=summary" % (lufs, tp, j["input_i"], j["input_tp"], j["input_lra"],
                                                                 j["input_thresh"], j["target_offset"]))
    else:
        af = "loudnorm=I=%s:TP=%s:LRA=11" % (lufs, tp)
    C.chay(["ffmpeg", "-v", "error", "-y", "-i", src, "-af", af, "-ar", str(SR), "-ac", "2", "-c:a", "pcm_s16le", dst])
    return dst
