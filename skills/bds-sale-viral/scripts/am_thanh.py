# -*- coding: utf-8 -*-
"""Bước 2 — TIẾNG: giọng (nguồn) + nhạc nền (nếu có, thấp hơn giọng ~9 dB, nhích +3 dB ở khe)
+ SFX tự đặt theo SỰ KIỆN đồ hoạ trong ke_hoach.json (đúng loại như mẫu: whoosh ở tiêu đề / chuyển cảnh,
lấp lánh khi chữ đáp, pop ở icon / thẻ / chữ to, gõ phím ở ô tìm kiếm, ka-ching ở số tiền, riser trước chuyển cảnh lớn)
→ master −14 LUFS / TP −1,5. Ghi riêng từng lớp + sfx.json để bước kiểm đo lại."""
import os, re, subprocess, json
import numpy as np
import chung as C

SR = C.SR
K1 = 1.0 / C.FPS


def doc_am(path, dur=None):
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', path, '-ac', '2', '-ar', str(SR), '-f', 'f32le', '-'],
                         capture_output=True).stdout
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


# ------------------------------------------------------------------ sự kiện → SFX
def su_kien(plan, work=None):
    """[{t, nhom, canh: 'dau'|'dinh', dai?}] từ kế hoạch (mốc khớp đúng chuyển động ở dung.py).
    Có `work` (tay.json) thì icon / thẻ ảnh đặt lên tay kêu đúng lúc tay mở (tay.xep giống dung.py)."""
    ev = []
    xep = {}
    if work:
        import tay
        xep = tay.xep(plan, tay.doc(work))
    for k, td in enumerate(plan.get('tieu_de', [])):
        if not td.get('khoa'): continue
        t0, t1 = float(td['t0']), float(td['t1'])
        ev.append({'t': t0 + 5 * K1, 'nhom': 'tieu_de', 'canh': 'dinh'})
        if td.get('vao', 'roi') in ('phong', 'tu_dau'):
            ev.append({'t': t0 + 13 * K1, 'nhom': 'tieu_de_dap', 'canh': 'dau'})
        if td.get('ra') == 'vo_chu':
            ev.append({'t': t1 - 13 * K1, 'nhom': 'tieu_de_ra', 'canh': 'dau'})
    for c in plan.get('chuyen', []):
        ev.append({'t': float(c['t']), 'nhom': c['kieu'], 'canh': 'dinh'})
        if c['kieu'] in ('loe_doc', 'chay_phim'):
            ev.append({'t': float(c['t']) - 1.35, 'nhom': 'riser', 'canh': 'dau'})
    for s in plan.get('sub', []):
        for j, d in enumerate(s.get('dong', [])):
            t = float(d['t']) if d.get('t') is not None else float(s['t0'])
            if d.get('kieu') == 'to':
                ev.append({'t': t + 1 * K1, 'nhom': 'sub_to', 'canh': 'dau'})
            elif '[' in d.get('text', ''):
                ev.append({'t': t + 2 * K1, 'nhom': 'sub_nhan', 'canh': 'dau'})
            if d.get('vong'):
                ev.append({'t': t + 3 * K1, 'nhom': 'vong_ve', 'canh': 'dau'})
    for k, th in enumerate(plan.get('the_anh', [])):
        t = xep[('the_anh', k)]['t0'] if ('the_anh', k) in xep else float(th['t0'])
        ev.append({'t': t, 'nhom': 'the_anh', 'canh': 'dau'})
    for k, ic in enumerate(plan.get('icon', [])):
        t = xep[('icon', k)]['t0'] if ('icon', k) in xep else float(ic['t0'])
        ev.append({'t': t + 2 * K1, 'nhom': 'icon', 'canh': 'dau'})
    for tk in plan.get('tim_kiem', []):
        ev.append({'t': float(tk['t0']), 'nhom': 'tim_kiem', 'canh': 'dau'})
        tg = float(tk.get('t_go', float(tk['t0']) + 0.3))
        dai = len(tk.get('chu', '')) * K1 / C.TIM_KIEM['ky_tu_khung']
        if dai > 0.15: ev.append({'t': tg, 'nhom': 'go_phim', 'canh': 'dau', 'dai': dai})
    for st in plan.get('so_tien', []):
        for s in st.get('so', []):
            ev.append({'t': float(s.get('t', st['t0'])) + 4 * K1, 'nhom': 'so_tien', 'canh': 'dau'})
    for lg in plan.get('logo', []):
        ev.append({'t': float(lg['t0']) + 10 * K1, 'nhom': 'logo', 'canh': 'dau'})
    for lk in plan.get('liet_ke', []):
        ev.append({'t': float(lk['t0']), 'nhom': 'sub_to', 'canh': 'dau'})
        for d in lk.get('dong', [])[1:]:
            ev.append({'t': float(d.get('t', lk['t0'])), 'nhom': 'liet_ke', 'canh': 'dau'})
    return ev


def chon_sfx(plan, work=None):
    """lọc theo ưu tiên + cửa sổ 0,30 s, xoay biến thể (file ít dùng nhất, không lặp trong 4 s), cộng sfx_them, trừ sfx_bo."""
    if plan.get('sfx') is False: return []
    ev = su_kien(plan, work)
    dur = float(plan['dur'])
    bo = [float(t) for t in plan.get('sfx_bo', [])]
    ev = [e for e in ev if 0 <= e['t'] < dur - 0.1 and not any(abs(e['t'] - b) < 0.2 for b in bo)]
    uu = {n: k for k, n in enumerate(C.SFX_UU_TIEN)}
    ev.sort(key=lambda e: (uu.get(e['nhom'], 99), e['t']))
    giu = []
    for e in ev:
        if e['nhom'] in ('go_phim', 'riser'):
            if any(abs(e['t'] - g['t']) < 0.12 for g in giu): continue
        elif any(abs(e['t'] - g['t']) < (C.SFX_CUA_SO_PHU if e['nhom'] in C.SFX_PHU else C.SFX_CUA_SO)
                 and g['nhom'] not in ('go_phim', 'riser') for g in giu):
            continue
        giu.append(e)
    giu.sort(key=lambda e: e['t'])
    dung, lan = {}, {}
    out = []
    for e in giu:
        ds = C.SFX_NHOM.get(e['nhom'], ['pop.mp3'])
        ok = [f for f in ds if e['t'] - lan.get(f, -99) >= C.SFX_KHONG_LAP_S] or ds
        f = min(ok, key=lambda x: (dung.get(x, 0), lan.get(x, -99)))
        dung[f] = dung.get(f, 0) + 1; lan[f] = e['t']
        q = dict(e, file=f, to=C.SFX_TO.get(e['nhom'], 0))
        out.append(q)
    for x in plan.get('sfx_them', []):
        f = x.get('file') or C.SFX_NHOM.get(x.get('nhom', 'icon'), ['pop.mp3'])[0]
        out.append({'t': float(x['t']), 'nhom': x.get('nhom', 'them'), 'file': f, 'canh': x.get('canh', 'dau'),
                    'to': float(x.get('db', C.SFX_TO.get(x.get('nhom'), 0)))})
    out.sort(key=lambda e: e['t'])
    return out


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
    bc = {'giong_rms_db': round(giong_db, 1), 'nhac': os.path.basename(nhac) if nhac else None}
    if nhac and os.path.exists(nhac):
        mu = doc_am(nhac)
        ss = int(float(plan.get('nhac_ss', 0)) * SR)
        mu = mu[ss:] if ss < len(mu) else mu
        if len(mu) < N: mu = np.tile(mu, (N // max(1, len(mu)) + 1, 1))
        mu = mu[:N]
        mr = rms_cua_so(mu)
        nhac_db = db(np.median(mr[mr > 1e-4])) if (mr > 1e-4).any() else -60
        g_base = giong_db - float(plan.get('nhac_duoi_giong_db', C.AM['nhac_duoi_giong_db'])) - nhac_db
        out = np.zeros_like(noi); v = 0.0
        for i, e in enumerate(noi):          # attack 80 ms / release 350 ms
            v = v + (e - v) * (min(1, 0.05 / 0.08) if e > v else min(1, 0.05 / 0.35)); out[i] = v
        gdb = g_base + C.AM['nhac_khe_db'] * (1 - out)
        g = 10 ** (np.repeat(gdb, int(0.05 * SR)) / 20)
        g = np.concatenate([g, np.full(max(0, N - len(g)), g[-1])])[:N]
        music = mu * g[:, None]
        fi, fo = int(0.4 * SR), int(1.2 * SR)
        music[:fi] *= np.linspace(0, 1, fi)[:, None]; music[-fo:] *= np.linspace(1, 0, fo)[:, None]
        mr2 = rms_cua_so(music)
        bc['nhac_duoi_giong_db'] = round(giong_db - db(np.median(mr2[:len(noi)][noi[:len(mr2)] > 0])), 1)
    cues = chon_sfx(plan, work)
    sfx = np.zeros_like(voice)
    ds = []
    cache = {}
    for q in cues:
        f = C.sfx_path(q['file'])
        if not os.path.exists(f):
            print('  ⚠ thiếu SFX', f); continue
        if f not in cache: cache[f] = doc_am(f)
        s = cache[f].copy()
        mono = np.abs(s).max(1); pk = mono.max() + 1e-9
        s = s[int(np.argmax(mono > pk * 0.05)):]
        dmax = q.get('dai') or C.SFX_DAI_MAX.get(os.path.basename(f), 1.2)
        s = s[:int(dmax * SR)]
        if len(s) < 10: continue
        fo = min(len(s), int(0.12 * SR)); s[-fo:] *= np.linspace(1, 0, fo)[:, None]
        r10 = rms_cua_so(s, 0.01)
        st = int(q['t'] * SR) - (int(np.argmax(r10) * 0.01 * SR) if q.get('canh') == 'dinh' else 0)
        a, b = max(0, int((q['t'] - 3) / 0.05)), min(len(r), int((q['t'] + 3) / 0.05))
        seg = r[a:b][noi[a:b] > 0]
        loc = db(np.median(seg)) if len(seg) else giong_db
        gain = loc + q['to'] - db(r10.max())
        s = s * 10 ** (gain / 20)
        a0, b0 = max(0, st), min(N, st + len(s))
        if b0 > a0: sfx[a0:b0] += s[a0 - st:b0 - st]
        ds.append({'t': round(q['t'], 3), 'nhom': q['nhom'], 'file': os.path.basename(f), 'gain_db': round(gain, 1)})
    bc['sfx'] = ds
    C.ghi_json(os.path.join(work, 'sfx.json'), ds)
    mix = voice + music + sfx
    ghi_wav(os.path.join(work, 'lop_giong.wav'), voice)
    ghi_wav(os.path.join(work, 'lop_nhac.wav'), music)
    ghi_wav(os.path.join(work, 'lop_sfx.wav'), sfx)
    tho = os.path.join(work, 'tron_tho.wav'); ghi_wav(tho, mix)
    r1 = subprocess.run(['ffmpeg', '-hide_banner', '-i', tho, '-af',
                         f'loudnorm=I={C.AM["lufs"]}:TP={C.AM["tp"]}:LRA=11:print_format=json', '-f', 'null', '-'],
                        capture_output=True, text=True, encoding='utf-8', errors='replace')
    js = json.loads(r1.stderr[r1.stderr.rfind('{'):r1.stderr.rfind('}') + 1])
    af = (f'loudnorm=I={C.AM["lufs"]}:TP={C.AM["tp"]}:LRA=11:measured_I={js["input_i"]}:measured_TP={js["input_tp"]}'
          f':measured_LRA={js["input_lra"]}:measured_thresh={js["input_thresh"]}:offset={js["target_offset"]}:linear=true')
    master = os.path.join(work, 'tieng.wav')
    # chặn đỉnh sau loudnorm: giọng gốc nén sát 0 dBFS (mic cài áo) ⇒ wav TP −1,4 nhưng mã hoá AAC vọt −0,9 dBTP (ONE ERA
    # 12/11 tự kiểm ⛔) ⇒ đích TP −2,0 + limiter có nhìn trước, chừa ~1 dB cho AAC
    lim = 10 ** (C.AM['tp'] / 20)
    C.run(['ffmpeg', '-y', '-v', 'error', '-i', tho, '-af',
           af + f',aresample=192000,alimiter=limit={lim:.4f}:attack=2:release=60:level=disabled,aresample={SR}',
           '-c:a', 'pcm_s16le', master])
    I, tp = lufs(master)
    bc.update(lufs=I, tp=tp)
    C.ghi_json(os.path.join(work, 'am_thanh.json'), bc)
    print(f'  tiếng: {I:.1f} LUFS, TP {tp:.1f} dBFS · nhạc thấp hơn giọng {bc.get("nhac_duoi_giong_db", "—")} dB · '
          f'{len(ds)} SFX ({len(set(d["file"] for d in ds))} loại)')
    return master
