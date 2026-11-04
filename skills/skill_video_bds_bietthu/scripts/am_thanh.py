# -*- coding: utf-8 -*-
"""Bước 4 — tiếng: giọng (đã cắt lặng) + nhạc nền của user (thấp hơn giọng ~16 dB, nhích lên ở khe)
+ SFX thưa ở hiệu ứng (đỉnh 10 ms cao hơn giọng tại chỗ ~+5 dB) → master −14 LUFS / TP −1,5.
Ghi riêng từng lớp để bước kiểm đo lại được."""
import os, re, subprocess, json
import numpy as np
import chung as C

SR = C.SR


def doc_am(path, dur=None):
    cmd = ['ffmpeg', '-v', 'error', '-i', path, '-ac', '2', '-ar', str(SR), '-f', 'f32le', '-']
    raw = subprocess.run(cmd, capture_output=True).stdout
    x = np.frombuffer(raw, np.float32).reshape(-1, 2).copy()
    if dur is not None:
        n = int(dur * SR)
        x = x[:n] if len(x) >= n else np.vstack([x, np.zeros((n - len(x), 2), np.float32)])
    return x


def ghi_wav(path, x):
    p = subprocess.Popen(['ffmpeg', '-y', '-v', 'error', '-f', 'f32le', '-ar', str(SR), '-ac', '2', '-i', '-',
                          '-c:a', 'pcm_f32le', path], stdin=subprocess.PIPE)
    p.stdin.write(np.ascontiguousarray(x, np.float32).tobytes()); p.stdin.close(); p.wait()


def db(v):
    return 20 * np.log10(max(float(v), 1e-9))


def rms_cua_so(x, win=0.05):
    m = x.mean(1); n = int(win * SR); k = len(m) // n
    return np.sqrt((m[:k * n].reshape(k, n) ** 2).mean(1) + 1e-12)


def lufs(path):
    r = subprocess.run(['ffmpeg', '-hide_banner', '-i', path, '-af', 'ebur128=peak=true', '-f', 'null', '-'],
                       capture_output=True, text=True, encoding='utf-8', errors='replace')
    s = r.stderr[r.stderr.rfind('Summary'):]
    I = float(re.search(r'I:\s*(-?[\d.]+) LUFS', s).group(1))
    tp = re.search(r'Peak:\s*(-?[\d.]+|-inf) dBFS', s)
    return I, (float(tp.group(1)) if tp and tp.group(1) != '-inf' else -99.0)


def mat_na_noi(words, n_win, win=0.05):
    m = np.zeros(n_win, np.float32)
    for w in words:
        a, b = int(w['s'] / win), int(w['e'] / win) + 1
        m[max(0, a):min(n_win, b)] = 1
    return m


def tron(plan, work):
    dur = float(plan['dur'])
    voice = doc_am(os.path.join(work, 'giong.wav'), dur)
    voice = voice - voice.mean(0)
    words = C.doc_json(os.path.join(work, 'words.json'))
    r = rms_cua_so(voice)
    noi = mat_na_noi(words, len(r))
    giong_db = db(np.median(r[noi > 0])) if (noi > 0).any() else db(np.median(r))
    N = len(voice)
    music = np.zeros_like(voice)
    nhac = plan.get('nhac')
    bao_cao = {'giong_rms_db': round(giong_db, 1)}
    if nhac and os.path.exists(nhac):
        mu = doc_am(nhac)
        if len(mu) < N: mu = np.tile(mu, (N // len(mu) + 1, 1))
        ss = int(float(plan.get('nhac_ss', 0)) * SR)
        mu = mu[ss:ss + N]
        if len(mu) < N: mu = np.vstack([mu, np.zeros((N - len(mu), 2), np.float32)])
        mr = rms_cua_so(mu)
        nhac_db = db(np.median(mr[mr > 1e-4])) if (mr > 1e-4).any() else -60
        g_base = giong_db - plan.get('nhac_duoi_giong_db', C.AM['nhac_duoi_giong_db']) - nhac_db
        # vỏ ducking: lúc nói = g_base; ở khe nhích +4 dB; attack 80 ms / release 350 ms
        env = noi.copy()
        out = np.zeros_like(env); a_up, a_dn = 0.05 / 0.08, 0.05 / 0.35
        v = 0.0
        for i, e in enumerate(env):
            v = v + (e - v) * (min(1, a_up) if e > v else min(1, a_dn)); out[i] = v
        gdb = g_base + 4.0 * (1 - out)
        g = 10 ** (np.repeat(gdb, int(0.05 * SR)) / 20)
        g = np.concatenate([g, np.full(max(0, N - len(g)), g[-1])])[:N]
        music = mu * g[:, None]
        fi, fo = int(0.6 * SR), int(1.5 * SR)
        music[:fi] *= np.linspace(0, 1, fi)[:, None]; music[-fo:] *= np.linspace(1, 0, fo)[:, None]
        bao_cao['nhac_duoi_giong_db'] = round(giong_db - db(np.median(rms_cua_so(music)[noi > 0])), 1)
    # SFX
    cues = C.doc_json(os.path.join(work, 'sfx.json')) if os.path.exists(os.path.join(work, 'sfx.json')) else []
    sfx = np.zeros_like(voice)
    bc = []
    for q in cues:
        f = q['file'] if os.path.isabs(q['file']) else os.path.join(C.SFX_DIR, q['file'])
        s = doc_am(f)
        mono = np.abs(s).max(1)
        pk = mono.max() + 1e-9
        on = int(np.argmax(mono > pk * 0.05))
        s = s[on:]
        dmax = C.SFX_DAI_MAX.get(os.path.basename(f), 2.0)
        s = s[:int(dmax * SR)]
        fo = min(len(s), int(0.15 * SR)); s[-fo:] *= np.linspace(1, 0, fo)[:, None]
        r10 = rms_cua_so(s, 0.01)
        if q.get('canh') == 'dinh':     # đỉnh tiếng rơi đúng mốc (whoosh vào cú cắt)
            st = int(q['t'] * SR) - int(np.argmax(r10) * 0.01 * SR)
        elif q.get('canh') == 'dinh_giua':   # zoom mượt: đỉnh tiếng rơi giữa cú zoom
            st = int((q['t'] + C.ZOOM_MUOT['khung'] / 2 / C.FPS) * SR) - int(np.argmax(r10) * 0.01 * SR)
        else:
            st = int(q['t'] * SR)
        # giọng tại chỗ ±3 s (chỉ tính lúc nói)
        a, b = max(0, int((q['t'] - 3) / 0.05)), min(len(r), int((q['t'] + 3) / 0.05))
        seg = r[a:b][noi[a:b] > 0]
        loc = db(np.median(seg)) if len(seg) else giong_db
        gain = loc + q.get('tren_giong_db', C.AM['sfx_tren_giong_db']) - db(r10.max())
        s = s * 10 ** (gain / 20)
        a0, b0 = max(0, st), min(N, st + len(s))
        if b0 > a0: sfx[a0:b0] += s[a0 - st:b0 - st]
        bc.append({'t': q['t'], 'file': os.path.basename(f), 'gain_db': round(gain, 1), 'giong_tai_cho_db': round(loc, 1)})
    bao_cao['sfx'] = bc
    mix = voice + music + sfx
    ghi_wav(os.path.join(work, 'lop_giong.wav'), voice)
    ghi_wav(os.path.join(work, 'lop_nhac.wav'), music)
    ghi_wav(os.path.join(work, 'lop_sfx.wav'), sfx)
    tho = os.path.join(work, 'tron_tho.wav'); ghi_wav(tho, mix)
    # master: loudnorm 2 lượt, tuyến tính
    r1 = subprocess.run(['ffmpeg', '-hide_banner', '-i', tho, '-af',
                         f'loudnorm=I={C.AM["lufs"]}:TP={C.AM["tp"]}:LRA=11:print_format=json', '-f', 'null', '-'],
                        capture_output=True, text=True, encoding='utf-8', errors='replace')
    js = json.loads(r1.stderr[r1.stderr.rfind('{'):r1.stderr.rfind('}') + 1])
    af = (f'loudnorm=I={C.AM["lufs"]}:TP={C.AM["tp"]}:LRA=11:measured_I={js["input_i"]}:measured_TP={js["input_tp"]}'
          f':measured_LRA={js["input_lra"]}:measured_thresh={js["input_thresh"]}:offset={js["target_offset"]}:linear=true')
    master = os.path.join(work, 'tieng.wav')
    C.run(['ffmpeg', '-y', '-v', 'error', '-i', tho, '-af', af + f',aresample={SR}', '-c:a', 'pcm_s16le', master])
    I, tp = lufs(master)
    bao_cao.update(lufs=I, tp=tp)
    C.ghi_json(os.path.join(work, 'am_thanh.json'), bao_cao)
    print(f'Tiếng xong: {I:.1f} LUFS, TP {tp:.1f} dBFS · giọng {giong_db:.1f} dB · nhạc thấp hơn giọng {bao_cao.get("nhac_duoi_giong_db", "—")} dB · {len(bc)} SFX')
    return master
