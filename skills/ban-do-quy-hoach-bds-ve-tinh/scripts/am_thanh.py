# -*- coding: utf-8 -*-
"""Tiếng: đọc giọng, SFX bám hình với độ to tính theo giọng tại chỗ, nhạc nền tuỳ chọn, loudnorm 2 lượt −14 LUFS / −1 dBTP.
(Chép + rút gọn từ minh-tam-edit/am_thanh.py.)"""
import json
import os
import subprocess

import numpy as np

import chung as C

SR = 48000


def doc(path, sr=SR):
    r = subprocess.run([C.ffbin("ffmpeg"), "-v", "error", "-i", path, "-vn", "-ac", "1", "-ar", str(sr), "-f", "f32le", "-"],
                       capture_output=True)
    if r.returncode != 0:
        C.die("không đọc được tiếng: " + path)
    return np.frombuffer(r.stdout, np.float32).copy()


def ghi(path, x, sr=SR, ch=1):
    x = np.asarray(x, np.float32)
    p = subprocess.Popen([C.ffbin("ffmpeg"), "-v", "error", "-y", "-f", "f32le", "-ar", str(sr), "-ac", str(ch), "-i", "-",
                          "-c:a", "pcm_f32le", path], stdin=subprocess.PIPE)
    p.stdin.write(x.tobytes())
    p.stdin.close()
    p.wait()


def _rms_db(x):
    return 20 * np.log10(np.sqrt(np.mean(x.astype(np.float64) ** 2)) + 1e-9)


def _env(x, sr, win):
    h = int(sr * win)
    n = len(x) // h
    if n == 0:
        return np.array([-120.0])
    e = np.sqrt(np.mean(x[:n * h].astype(np.float64).reshape(n, h) ** 2, axis=1) + 1e-12)
    return 20 * np.log10(e + 1e-9)


def cat_sfx(path, dai=None, sr=SR):
    x = doc(path, sr)
    e = _env(x, sr, 0.005)
    pk = e.max()
    on = int(np.argmax(e > pk - 30)) * int(sr * 0.005)
    x = x[on:]
    if dai:
        n = int(dai * sr)
        if len(x) > n:
            x = x[:n].copy()
            fo = int(sr * 0.08)
            x[-fo:] *= np.linspace(1, 0, fo, dtype=np.float32)
    return x


def tron_sfx(voice, events, sr=SR, nguon_sfx=C.SFX_DIR):
    """events: [{t, file, muc 'chinh'|'nhe', dai?}] → (lớp sfx, báo cáo). Đỉnh RMS-10ms SFX = giọng tại chỗ +4 dB (chính) / +1 dB (nhẹ)"""
    lop = np.zeros(len(voice) + sr * 4, np.float32)
    env_v = _env(voice, sr, 0.05)
    voiced = env_v[env_v > -45]
    v_med = float(np.median(voiced)) if len(voiced) else -20.0
    bc, cache = [], {}
    for ev in sorted(events, key=lambda e: e["t"]):
        key = (ev["file"], ev.get("dai"))
        if key not in cache:
            p = ev["file"] if os.path.isabs(ev["file"]) else os.path.join(nguon_sfx, ev["file"])
            if not os.path.isfile(p):
                print("⚠ thiếu SFX %s — bỏ qua" % ev["file"])
                continue
            cache[key] = cat_sfx(p, ev.get("dai"))
        s = cache[key]
        t = max(0.0, ev["t"])
        i0 = int(t * sr)
        a, b = max(0, int((t - 1.5) / 0.05)), int((t + 1.5) / 0.05)
        loc = env_v[a:b]
        loc = loc[loc > -45]
        v_loc = float(np.median(loc)) if len(loc) else v_med
        s_pk = float(_env(s, sr, 0.01).max())
        off = 4.0 if ev.get("muc", "chinh") == "chinh" else 1.0
        g_db = max(-36.0, min(8.0, v_loc + off - s_pk))
        seg = s * (10 ** (g_db / 20))
        lop[i0:i0 + len(seg)] += seg[:max(0, len(lop) - i0)]
        bc.append({"t": round(t, 3), "file": ev["file"], "gain_db": round(g_db, 1), "giong_db": round(v_loc, 1)})
    return lop[:len(voice) + sr], bc


def nhac_nen(path, n, voice, sr=SR, duoi_db=20.0):
    m = doc(path, sr)
    if len(m) == 0:
        return np.zeros(n, np.float32)
    m = np.tile(m, int(np.ceil(n / len(m))))[:n]
    env_v = _env(voice, sr, 0.05)
    voiced = env_v[env_v > -45]
    v_med = float(np.median(voiced)) if len(voiced) else -20.0
    m = m * (10 ** ((v_med - duoi_db - _rms_db(m)) / 20))
    fi, fo = int(sr * 1.0), int(sr * 1.5)
    m[:fi] *= np.linspace(0, 1, fi, dtype=np.float32)
    m[-fo:] *= np.linspace(1, 0, fo, dtype=np.float32)
    return m


def master(mix_path, out_path, lufs=-14.0, tp=-1.0):
    r = subprocess.run([C.ffbin("ffmpeg"), "-v", "info", "-i", mix_path, "-af",
                        "loudnorm=I=%g:TP=%g:LRA=11:print_format=json" % (lufs, tp), "-f", "null", "-"],
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    txt = r.stderr
    j = json.loads(txt[txt.rfind("{"):txt.rfind("}") + 1])
    af = ("loudnorm=I=%g:TP=%g:LRA=11:measured_I=%s:measured_TP=%s:measured_LRA=%s:measured_thresh=%s:offset=%s:"
          "linear=true:print_format=summary" % (lufs, tp, j["input_i"], j["input_tp"], j["input_lra"], j["input_thresh"],
                                                j["target_offset"]))
    C.run([C.ffbin("ffmpeg"), "-v", "error", "-y", "-i", mix_path, "-af", af + ",aresample=48000", "-ac", "2",
           "-c:a", "pcm_s24le", out_path])
    return j


def do_lufs(path):
    r = subprocess.run([C.ffbin("ffmpeg"), "-nostats", "-i", path, "-af", "ebur128=peak=true", "-f", "null", "-"],
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    import re
    # ebur128 in cả dòng chạy (I: -70 LUFS ở khung đầu) ⇒ chỉ đọc phần Summary cuối
    txt = r.stderr[r.stderr.rfind("Summary:"):] if "Summary:" in r.stderr else r.stderr
    i = re.findall(r"I:\s+(-?[\d.]+) LUFS", txt)
    tp = re.findall(r"Peak:\s+(-?[\d.]+) dBFS", txt)
    return (float(i[-1]) if i else None, float(tp[-1]) if tp else None)
