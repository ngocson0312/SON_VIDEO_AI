# -*- coding: utf-8 -*-
"""CỔNG DUYỆT — dựng thử khung ở mọi đồ hoạ → duyet.jpg + bang_duyet.md (bảng đồ hoạ + SFX) để Claude gửi người dùng."""
import os, re
import chung as C
import am_thanh, dung


def _ms(t):
    return f'{int(t // 60)}:{t % 60:05.2f}'


def lam(plan, work):
    moc = []
    for td in plan.get('tieu_de', []):
        moc.append((td['t0'] + 0.20, 'TĐ vào ' + td['khoa']))
        moc.append((min(td['t1'] - 0.1, td['t0'] + 0.75), 'TĐ ' + td['khoa']))
    for key, ten, f in (('the_anh', 'thẻ ảnh', 0.5), ('tim_kiem', 'tìm kiếm', 0.8),
                        ('logo', 'logo', 0.6), ('liet_ke', 'liệt kê', 0.9)):
        for x in plan.get(key, []): moc.append((x['t0'] + (x['t1'] - x['t0']) * f, ten))
    import tay
    xep0 = tay.xep(plan, tay.doc(work))
    for k, ic in enumerate(plan.get('icon', [])):
        r = xep0.get(('icon', k))
        t0 = r['t0'] if r else ic['t0']
        moc.append((t0 + min(0.5, (ic['t1'] - t0) * 0.4), 'icon ' + ('trên tay' if r else 'mép')))
    for st in plan.get('so_tien', []):
        for s in st.get('so', []): moc.append((float(s.get('t', st['t0'])) + 0.4, 'số ' + s.get('text', '')))
    for c in plan.get('chuyen', []):
        moc.append((c['t'] - 1.5 / C.FPS, 'chuyển ' + c['kieu']))
    subs = plan.get('sub', [])
    dac = [s for s in subs if any(d.get('kieu') in ('to', 'vang') or '[' in d.get('text', '') or d.get('vong') for d in s['dong'])]
    for s in dac[:8]: moc.append((s['t0'] + 0.3, 'sub ' + s['dong'][0]['text']))
    thuong = [s for s in subs if s not in dac]
    for s in thuong[::max(1, len(thuong) // 6)][:6]: moc.append((s['t0'] + 0.3, 'sub ' + s['dong'][0]['text']))
    moc = sorted({round(t, 2): (t, n) for t, n in moc if 0 <= t < plan['dur']}.values())
    if len(moc) > 42: moc = moc[::max(1, len(moc) // 42 + 1)]
    out = os.path.join(work, 'duyet.jpg')
    print(f'Dựng thử {len(moc)} khung…', flush=True)
    dung.xem_truoc(plan, work, moc, out)
    # bảng
    sfx = am_thanh.chon_sfx(plan, work)
    L = ['# Bảng duyệt — bds-sale-viral', '',
         f'- Video: `{plan.get("video_goc", "")}` · {plan["dur"]:.1f} s · cắt lặng: **{plan.get("cat_lang", "?")}**',
         f'- Dự án: **{plan.get("ten_du_an") or "—"}** · nhạc: **{os.path.basename(plan["nhac"]) if plan.get("nhac") else "KHÔNG"}**'
         f' · SFX: **{len(sfx)}** tiếng', '',
         '## Tiêu đề 3 tầng (dẫn / KHOÁ / viết tay)', '', '| # | Giờ | Dẫn | KHOÁ | Viết tay | Màu | Vào → Ra |', '|---|---|---|---|---|---|---|']
    for k, td in enumerate(plan.get('tieu_de', [])):
        L.append(f'| {k + 1} | {_ms(td["t0"])}–{_ms(td["t1"])} | {td.get("dan") or ""} | **{td["khoa"]}** | {td.get("viet_tay") or ""} | '
                 f'{td.get("kieu")} | {td.get("vao")} → {td.get("ra")} |')
    L += ['', '## Đồ hoạ', '', '| Giờ | Loại | Nội dung |', '|---|---|---|']
    rows = []
    for th in plan.get('the_anh', []):
        rows.append((th['t0'], 'thẻ ảnh ' + th.get('kieu', 'phang'), ', '.join(os.path.basename(p) for p in th.get('nguon', []))))
    import tay
    kq_tay = tay.doc(work)
    xep = tay.xep(plan, kq_tay) if kq_tay else {}
    for k, ic in enumerate(plan.get('icon', [])):
        r = xep.get(('icon', k))
        o = f'mọc từ TAY {"TRÁI" if r["ben"] == "trai" else "PHẢI"} lúc {r["t0"]:.2f}s' if r else f'trượt từ mép {ic.get("ben")} (không có cử chỉ tay)'
        rows.append((ic['t0'], 'icon 3D', f'{ic.get("loai")} "{ic.get("nhan") or ""}" — {o}'))
    for tk in plan.get('tim_kiem', []): rows.append((tk['t0'], 'ô tìm kiếm', tk.get('chu', '')))
    for st in plan.get('so_tien', []):
        rows.append((st['t0'], 'số tiền', (st.get('tren') or '') + ' · ' + ' → '.join(f'{s["text"]} {s.get("duoi") or ""}' for s in st.get('so', []))))
    for lg in plan.get('logo', []): rows.append((lg['t0'], 'logo', os.path.basename(lg.get('nguon', ''))))
    for lk in plan.get('liet_ke', []): rows.append((lk['t0'], 'liệt kê', lk.get('khoa', '') + ': ' + ' / '.join(d['text'] for d in lk.get('dong', []))))
    for c in plan.get('chuyen', []): rows.append((c['t'], 'chuyển cảnh', c['kieu']))
    for t, a, b in sorted(rows): L.append(f'| {_ms(t)} | {a} | {b} |')
    if kq_tay is not None:
        cc = kq_tay.get('cu_chi', [])
        L += ['', f'## Cử chỉ MỞ TAY ({len(cc)} lần — tay.jpg)', '']
        L.append(' · '.join(f'{_ms(c["t0"])}–{_ms(c["t1"])} tay {c["ben"]}' for c in cc) if cc else
                 'Người nói không mở tay sang bên → icon trượt từ mép vào (muốn icon mọc từ tay: quay mở lòng bàn tay khi nói ý chính)')
    L += ['', f'## Sub ngực ({len(plan.get("sub", []))} cụm)', '']
    L.append(' · '.join(' / '.join(d['text'] for d in s['dong']) for s in plan.get('sub', [])))
    L += ['', '## SFX', '', ' · '.join(f'{_ms(q["t"])} {q["file"]}' for q in sfx)]
    # chữ đè mặt (người dùng chốt 12/11/2026) — quét mọi khung trước khi tới cổng duyệt
    import kiem
    Dq = dung.Dung(plan, work)
    de = kiem.de_mat(Dq)
    L += ['', '## Chữ đè mặt người nói', '',
          ('⛔ ' + '; '.join(de) + ' — sửa kế hoạch (dời giờ / đổi bên / bỏ chữ) rồi duyệt lại') if de else
          f'✅ không chữ / icon / thẻ nào đè mặt (mặt thật {sum(Dq.mat_that) / max(1, Dq.n):.0%} khung)']
    L += ['', f'Zoom nhảy: {len(plan.get("zoom", [])) - 1} lần · ảnh dựng thử: `{out}`']
    md = os.path.join(work, 'bang_duyet.md')
    with open(md, 'w', encoding='utf-8') as f: f.write('\n'.join(L) + '\n')
    print('\n'.join(L))
    print(f'\n→ {out}\n→ {md}')
    return out, md
