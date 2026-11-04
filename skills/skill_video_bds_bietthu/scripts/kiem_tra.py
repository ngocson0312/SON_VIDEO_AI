# -*- coding: utf-8 -*-
"""Bước 5 — tự kiểm 8 mục trên FILE CUỐI (không tin plan): thời lượng, độ to, cú cắt đúng mốc, chữ hiện +
trong vùng an toàn, chữ không đè mặt, độ nét quanh cú cắt, SFX nghe rõ, nhạc dưới giọng."""
import os, subprocess
import numpy as np
import cv2
import chung as C
import am_thanh as AT

SW, SH = 540, 960          # khung đo (½ kích thước)
K = SW / C.W


def _nguon_canh(c):
    return 'noi' if c['loai'] == 'noi' else (c['loai'] + ':' + str(c.get('nguon', c['id'])))


def kiem(plan, work, final):
    kq = []
    ok = lambda ten, dat, chi_tiet: kq.append((ten, bool(dat), chi_tiet))
    pr = C.probe(final)
    ok('1. Thời lượng', abs(pr['dur'] - plan['dur']) < 0.15, f"{pr['dur']:.2f}s (plan {plan['dur']:.2f}s)")
    I, tp = AT.lufs(final)
    ok('2. Độ to', abs(I - C.AM['lufs']) <= 1.0 and tp <= -1.0, f'{I:.1f} LUFS, TP {tp:.1f} dBFS')

    canh = sorted(plan['canh'], key=lambda c: c['t0'])
    ranh = [c['t0'] for i, c in enumerate(canh) if i > 0 and _nguon_canh(c) != _nguon_canh(canh[i - 1])]
    hop = C.doc_json(os.path.join(work, 'hop_chu.json')) if os.path.exists(os.path.join(work, 'hop_chu.json')) else []
    mat = C.doc_json(os.path.join(work, 'mat.json')) if os.path.exists(os.path.join(work, 'mat.json')) else []
    # khung cần đo độ phủ chữ: giữa khối & ngay trước khối
    can = {}
    for i, h in enumerate(hop):
        t1 = h['t1'] if h['t1'] and h['t1'] < 1e8 else plan['dur']
        can.setdefault(int(round(((h['t0'] + t1) / 2) * C.FPS)), []).append(('giua', i))
        can.setdefault(max(0, int(round(h['t0'] * C.FPS)) - 2), []).append(('truoc', i))
    p = subprocess.Popen(['ffmpeg', '-v', 'error', '-i', final, '-vf', f'scale={SW}:{SH},format=gray', '-f', 'rawvideo', '-'],
                         stdout=subprocess.PIPE)
    diffs, sharp, prev, i = [], [], None, 0
    mat_do = {}
    while True:
        b = p.stdout.read(SW * SH)
        if len(b) < SW * SH: break
        g = np.frombuffer(b, np.uint8).reshape(SH, SW).astype(np.float32)
        diffs.append(0.0 if prev is None else float(np.abs(g - prev).mean()))
        gg = g[SH // 8:SH * 7 // 8]
        # độ nét CHUẨN HOÁ theo tương phản: loé cam/loé trắng (screen) nén tương phản chứ không làm nhoè
        sharp.append(float(cv2.Laplacian(gg, cv2.CV_32F).var() / (gg.var() + 1.0)))
        if i in can:
            for kind, j in can[i]:
                x0, y0, x1, y1 = [int(v * K) for v in hop[j]['hop']]
                x0, y0 = max(0, x0), max(0, y0); x1, y1 = min(SW, max(x0 + 2, x1)), min(SH, max(y0 + 2, y1))
                e = cv2.Canny(g[y0:y1, x0:x1].astype(np.uint8), 60, 160).mean()
                mat_do.setdefault(j, {})[kind] = float(e)
        prev = g; i += 1
    p.stdout.close(); p.wait()
    diffs, sharp = np.array(diffs), np.array(sharp)
    # 3. cú cắt
    lech = []
    for t in ranh:
        f = int(round(t * C.FPS)); a, b = max(1, f - 3), min(len(diffs), f + 4)
        j = a + int(np.argmax(diffs[a:b]))
        nen = np.median(diffs[max(1, f - 30):f - 3]) if f > 34 else np.median(diffs)
        ke = np.concatenate([diffs[max(1, j - 3):j], diffs[j + 1:j + 4]])
        dinh = diffs[j] / (ke.max() + 1e-3) if len(ke) else 9.9     # khung cắt vượt hẳn khung kề (nền nhiều chuyển động)
        lech.append((t, (j - f), max(diffs[j] / (nen + 1e-3), 2.5 if dinh >= 1.8 else 0)))
    sai = [x for x in lech if abs(x[1]) > 2 or x[2] < 2.5]
    ok('3. Cắt cứng đúng mốc', not sai, f'{len(ranh) - len(sai)}/{len(ranh)} cú cắt khớp ±2 khung' +
       (f' · lệch: ' + ', '.join(f'{t:.2f}s({d:+d}k, x{r:.1f})' for t, d, r in sai[:6]) if sai else ''))
    # 4. chữ hiện + vùng an toàn
    ngoai, mo = [], []
    for j, h in enumerate(hop):
        x0, y0, x1, y1 = h['hop']
        if x0 < C.SAFE['x0'] - 5 or x1 > C.SAFE['x1'] + 5 or y0 < C.SAFE['y0'] - 5 or y1 > C.SAFE['y1'] + 5: ngoai.append(h['text'])
        m = mat_do.get(j, {})
        if 'giua' in m and m['giua'] < 0.015 and m['giua'] <= m.get('truoc', 0) * 1.05: mo.append(h['text'])
    ok('4. Chữ hiện + trong vùng an toàn', not ngoai and not mo,
       f'{len(hop)} khối chữ' + (f' · ngoài vùng: {ngoai[:3]}' if ngoai else '') + (f' · không thấy nét chữ: {mo[:3]}' if mo else ''))
    # 5. chữ không đè mặt (chỉ cảnh người nói)
    de = []
    noi = [(c['t0'], c['t1']) for c in canh if c['loai'] == 'noi']
    for h in hop:
        t1 = min(h['t1'] or plan['dur'], plan['dur'])
        for t in np.arange(h['t0'], t1, 0.4):
            if not any(a <= t < b for a, b in noi) or not mat: continue
            m = mat[min(len(mat) - 1, int(round(t / 0.2)))]['mat']
            if not m: continue
            x0, y0, x1, y1 = h['hop']
            ix = max(0, min(x1, m[2]) - max(x0, m[0])); iy = max(0, min(y1, m[3]) - max(y0, m[1]))
            if ix * iy > 0.08 * (m[2] - m[0]) * (m[3] - m[1]): de.append(f"{h['text'][:24]}@{t:.1f}s"); break
    ok('5. Chữ không đè mặt', not de, 'không khối nào đè mặt' if not de else 'đè: ' + '; '.join(de[:4]))
    # 6. độ nét quanh cú cắt
    if plan.get('nhoe'):
        ok('6. Độ nét quanh cú cắt', True, 'bỏ qua (plan bật nhoè đúng mẫu)')
    else:
        thap, bo = [], 0
        loe = [x['t'] for x in plan.get('chuyen', []) if x['kieu'] == 'loe_cam']
        for t in ranh:
            if any(abs(t - x) < 0.4 for x in loe): bo += 1; continue   # lớp loé cam cố ý làm mềm/nén tương phản
            f = int(round(t * C.FPS))
            # so mỗi phía với CHÍNH cảnh của nó (cảnh thẻ-nền-nhoè vốn mềm hơn cảnh ảnh phủ kín)
            ref_sau = np.median(sharp[f + 5:f + 25]) if f + 25 < len(sharp) else np.median(sharp)
            ref_truoc = np.median(sharp[max(0, f - 25):f - 5]) if f > 30 else ref_sau
            r = min(sharp[max(0, f - 3):f].min() / ref_truoc if f > 3 else 1.0, sharp[f:f + 4].min() / ref_sau)
            if r < 0.5: thap.append(f'{t:.2f}s ({r * 100:.0f}%)')
        ok('6. Độ nét quanh cú cắt', not thap, ('không nhoè' if not thap else 'tụt nét: ' + ', '.join(thap[:5])) +
           (f' (bỏ qua {bo} cú cắt có loé cam)' if bo else ''))
    # 7. SFX nghe rõ
    st = C.doc_json(os.path.join(work, 'am_thanh.json'))
    sfx = AT.doc_am(os.path.join(work, 'lop_sfx.wav')); gi = AT.doc_am(os.path.join(work, 'lop_giong.wav'))
    r50 = AT.rms_cua_so(gi); s10 = AT.rms_cua_so(sfx, 0.01)
    words = C.doc_json(os.path.join(work, 'words.json'))
    noi_m = AT.mat_na_noi(words, len(r50))
    nho = []
    for q in st.get('sfx', []):
        a, b = int(q['t'] / 0.01) - 30, int(q['t'] / 0.01) + 150
        pk = AT.db(s10[max(0, a):b].max()) if b > 0 else -99
        a2, b2 = max(0, int((q['t'] - 3) / 0.05)), int((q['t'] + 3) / 0.05)
        seg = r50[a2:b2][noi_m[a2:b2] > 0]
        loc = AT.db(np.median(seg)) if len(seg) else st['giong_rms_db']
        if not (2.0 <= pk - loc <= 9.0): nho.append(f"{q['file']}@{q['t']:.2f}s {pk - loc:+.1f}dB")
    ok('7. SFX nghe rõ (+2…+9 dB so giọng tại chỗ)', not nho, f"{len(st.get('sfx', []))} cue" + (' · lệch: ' + ', '.join(nho[:5]) if nho else ''))
    # 8. nhạc
    if plan.get('nhac'):
        d = st.get('nhac_duoi_giong_db')
        ok('8. Nhạc nền dưới giọng 12–20 dB', d is not None and 12 <= d <= 20, f'{d} dB')
    else:
        ok('8. Nhạc nền', True, 'không dùng nhạc (đã hỏi ở cổng duyệt)')
    # 9. không hụt hơi: mọi quãng bị bỏ phải là IM THẬT trong file thô (04/11 user bắt lỗi "hụt hơi")
    cl = os.path.join(work, 'cat_lang.json')
    if os.path.exists(cl) and C.doc_json(cl).get('cat'):
        import ke_hoach as KH
        e, san = KH.nang_luong(os.path.join(work, 'tho.wav'))
        keep = C.doc_json(cl)['keep']; xau = []
        for (a1, b1), (a2, b2) in zip(keep, keep[1:]):
            seg = e[int(b1 * 100):int(a2 * 100)]
            if len(seg) and seg.max() > san + C.CAT_LANG['nguong_db'] + 2: xau.append(f'{b1:.2f}–{a2:.2f}s ({seg.max():.0f} dB)')
        ok('9. Không hụt hơi (chỉ cắt quãng im thật)', not xau,
           f'{len(keep) - 1} quãng cắt, đều im' if not xau else 'cắt mất âm: ' + ', '.join(xau[:5]))
    else:
        ok('9. Không hụt hơi (chỉ cắt quãng im thật)', True, 'không cắt lặng')
    # 10. mọi cú zoom (phóng-lùi, phóng nhanh, zoom mượt) có tiếng trong ±0,4 s (04/11: "zoom không có SFX")
    cues = [q['t'] for q in st.get('sfx', [])]
    can_tieng = []
    for i, c in enumerate(canh):
        for h in c.get('hieu_ung', []):
            if h['kieu'] in ('phong_lui', 'phong_nhanh') and h.get('sfx', True): can_tieng.append((h['kieu'], h['t']))
        if i and c['loai'] == 'noi' and canh[i - 1]['loai'] == 'noi' and abs(canh[i - 1]['t1'] - c['t0']) < 0.02 \
                and abs(canh[i - 1].get('zoom', 1.0) - c.get('zoom', 1.0)) >= 0.02 and c.get('sfx_zoom', True) \
                and not any(h['kieu'] == 'phong_lui' and abs(h['t'] - c['t0']) < 0.05 for h in c.get('hieu_ung', [])):
            can_tieng.append(('zoom_muot', c['t0']))
    thieu = [f'{k}@{t:.2f}' for k, t in can_tieng if not any(abs(t - q) <= 0.4 for q in cues)]
    ok('10. Cú zoom nào cũng có SFX', not thieu, f'{len(can_tieng)} cú zoom' + (' · thiếu tiếng: ' + ', '.join(thieu[:6]) if thieu else ''))
    print('\nTỰ KIỂM trên file cuối:')
    for ten, dat, ct in kq:
        print(f"  {'ĐẠT ' if dat else 'LỖI '} {ten}: {ct}")
    n = sum(d for _, d, _ in kq)
    print(f'  → {n}/{len(kq)} ĐẠT')
    C.ghi_json(os.path.join(work, 'tu_kiem.json'), [{'muc': a, 'dat': b, 'chi_tiet': c} for a, b, c in kq])
    return n == len(kq)
