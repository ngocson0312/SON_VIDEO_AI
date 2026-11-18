# -*- coding: utf-8 -*-
"""sub.py — phụ đề karaoke: sửa lời theo sua_loi.txt (mỗi dòng = 1 đoạn Whisper trong loi_doc.txt), căn lại thời gian từng chữ."""
import os, re, json, difflib
import numpy as np
from ve import *


def _norm(w): return re.sub(r'[^\wÀ-ỹ]', '', w.lower())


def doc_segs(work):
    segs = []
    for ln in open(os.path.join(work, 'loi_doc.txt'), encoding='utf-8'):
        m = re.match(r'\[([\d.]+)-([\d.]+)\]\s*(.*)', ln.strip())
        if m: segs.append((float(m[1]), float(m[2]), m[3]))
    return segs


def words_fixed(work):
    """-> list {w,s,e} đã sửa lỗi nghe."""
    W = json.load(open(os.path.join(work, 'words.json'), encoding='utf-8'))
    segs = doc_segs(work)
    fix_p = os.path.join(work, 'sua_loi.txt')
    fixes = [l.strip() for l in open(fix_p, encoding='utf-8')] if os.path.exists(fix_p) else []
    out = []
    used = set()
    for si, (s0, e0, txt) in enumerate(segs):
        idx = [i for i, w in enumerate(W) if i not in used and s0 - 0.12 <= w['s'] < e0 + 0.02]
        used.update(idx)
        ow = [W[i] for i in idx]
        if not ow: continue
        new = fixes[si].split() if si < len(fixes) and fixes[si] and fixes[si] != '=' else [w['w'] for w in ow]
        sm = difflib.SequenceMatcher(None, [_norm(w['w']) for w in ow], [_norm(x) for x in new], autojunk=False)
        T = [None] * len(new)
        for tag, i1, i2, j1, j2 in sm.get_opcodes():
            if tag == 'equal':
                for k in range(i2 - i1): T[j1 + k] = (ow[i1 + k]['s'], ow[i1 + k]['e'])
            elif tag in ('replace', 'insert'):
                if i2 > i1:
                    a, b = ow[i1]['s'], ow[i2 - 1]['e']
                else:
                    a = ow[i1 - 1]['e'] if i1 > 0 else ow[0]['s']; b = ow[i1]['s'] if i1 < len(ow) else ow[-1]['e']
                n = j2 - j1
                tot = sum(max(1, len(new[j])) for j in range(j1, j2)); acc = a
                for j in range(j1, j2):
                    d = (b - a) * max(1, len(new[j])) / tot
                    T[j] = (acc, acc + d); acc += d
        # lấp chỗ trống còn lại
        for j in range(len(new)):
            if T[j] is None:
                pj = next((T[k] for k in range(j - 1, -1, -1) if T[k]), None); nj = next((T[k] for k in range(j + 1, len(new)) if T[k]), None)
                a = pj[1] if pj else ow[0]['s']; b = nj[0] if nj else ow[-1]['e']
                T[j] = (a, max(a + .08, b))
        for j, w in enumerate(new):
            out.append({'w': w, 's': round(T[j][0], 3), 'e': round(max(T[j][1], T[j][0] + .08), 3), 'seg': si})
    out.sort(key=lambda x: x['s'])
    for i in range(len(out) - 1):
        if out[i]['e'] > out[i + 1]['s']: out[i]['e'] = max(out[i]['s'] + .05, out[i + 1]['s'])
    return out


def phrases(words, max_words=5, max_chars=30, gap=0.5):
    P = []; cur = []
    for i, w in enumerate(words):
        if cur:
            g = w['s'] - cur[-1]['e']
            ch = sum(len(x['w']) + 1 for x in cur) + len(w['w'])
            br = g > gap or len(cur) >= max_words or ch > max_chars or w['seg'] != cur[-1]['seg'] and len(cur) >= 3
            if cur[-1]['w'][-1:] in ',.?!' and len(cur) >= 3: br = True
            if br: P.append(cur); cur = []
        cur.append(w)
    if cur: P.append(cur)
    # gộp cụm quá ngắn (1–2 chữ) vào cụm kề nếu cách nhau gần
    out = []
    for p in P:
        if out and len(p) <= 2 and p[0]['s'] - out[-1][-1]['e'] < 0.25 and len(out[-1]) + len(p) <= max_words + 1 \
                and sum(len(x['w']) + 1 for x in out[-1] + p) <= max_chars + 6 and out[-1][-1]['seg'] == p[0]['seg']:
            out[-1] = out[-1] + p
        else: out.append(p)
    res = []
    for k, p in enumerate(out):
        t0 = p[0]['s'] - 0.06
        nxt = out[k + 1][0]['s'] - 0.06 if k + 1 < len(out) else p[-1]['e'] + 0.5
        t1 = min(p[-1]['e'] + 0.28, nxt - 0.01) if nxt - p[-1]['e'] > 0.28 else nxt - 0.01
        t1 = max(t1, p[-1]['e'] + 0.05)
        res.append({'t0': t0, 't1': t1, 'w': p})
    return res


def layout_phrase(p, size, maxw):
    """chia 1–2 dòng cân bằng, trả về list dòng, mỗi dòng list (idx, word, x, width) và tổng w,h."""
    f = font(F_XB, size)
    ws = [x['w'] for x in p['w']]
    sp = size * 0.28
    wl = [f.getlength(w) for w in ws]
    tot = sum(wl) + sp * (len(ws) - 1)
    lines = [list(range(len(ws)))]
    if tot > maxw:
        best = None
        for c in range(1, len(ws)):
            a = sum(wl[:c]) + sp * (c - 1); b = sum(wl[c:]) + sp * (len(ws) - c - 1)
            m = max(a, b)
            if best is None or m < best[0]: best = (m, c)
        lines = [list(range(best[1])), list(range(best[1], len(ws)))]
    out = []
    for ln in lines:
        wlw = sum(wl[i] for i in ln) + sp * (len(ln) - 1)
        x = -wlw / 2; row = []
        for i in ln:
            row.append((i, ws[i], x, wl[i])); x += wl[i] + sp
        out.append(row)
    return out


def draw_sub(cv, p, t, cx, cy, size=54, maxw=900, a=1.0):
    """vẽ cụm karaoke tại giây t (cx,cy tâm khối)."""
    if t < p['t0'] or t > p['t1']: return
    k = back(prog(t, p['t0'], p['t0'] + 0.14))
    fade = min(1.0, prog(t, p['t0'], p['t0'] + 0.08) * 1.0, 1 - prog(t, p['t1'] - 0.1, p['t1']))
    rows = layout_phrase(p, size, maxw)
    lh = size * 1.22
    y0 = cy - lh * (len(rows) - 1) / 2 + (1 - k) * 14
    for r, row in enumerate(rows):
        y = y0 + r * lh
        for (i, w, x, wd) in row:
            ww = p['w'][i]
            cur = ww['s'] - 0.02 <= t < ww['e'] + 0.02 or (t >= ww['e'] and (i + 1 >= len(p['w']) or t < p['w'][i + 1]['s']) and False)
            col = COL['amber'] if cur else COL['white']
            sc = 1.0 + (0.10 * eo(prog(t, ww['s'] - .02, ww['s'] + .08)) if cur else 0)
            sp = sprite(w, F_XB, size, col, 9, (8, 14, 26))
            blit(cv, sp, cx + x + wd / 2, y, a * fade, sc * (0.92 + 0.08 * k))
