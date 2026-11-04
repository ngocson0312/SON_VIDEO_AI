# -*- coding: utf-8 -*-
"""skill_video_bds_bietthu — điểm vào duy nhất.

  python run.py ke-hoach --video THO.mp4 --resources DIR --out WORK [--ten Nghĩa] [--nhac nhac.mp3] [--khong-cat-lang]
      → đo + plan.json NHÁP + bang_duyet.md + tu_lieu_sheet.jpg ; THOÁT MÃ 2 (chờ Claude sửa plan + hỏi cổng duyệt)
  python run.py kiem-plan --out WORK            → soát plan (glyph, giờ, nguồn, vùng an toàn); mã 0 = được dựng
  python run.py xem --out WORK --moc 1.5,14.3   → dựng vài khung PNG để soát bố cục (WORK/xem/)
  python run.py dung --out WORK --ra FINAL.mp4  → kiem-plan → hình → tiếng → ghép → tự kiểm 8 mục
  python run.py kiem --out WORK --ra FINAL.mp4  → chỉ tự kiểm
"""
import argparse, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import chung as C
C.utf8_stdout()

DIALOG = """
================ CÁC DIALOG PHẢI HỎI (AskUserQuestion, tiếng Việt có dấu, LẦN NÀO CŨNG HỎI) ================
D1 Nội dung chữ từng cảnh (đã sửa chính tả/tên riêng theo nghĩa) — đề xuất: bản Claude viết trong plan.json
D2 Gán tư liệu cho từng cảnh (ảnh/video nào cho cụm ý nào) — đề xuất: theo nghĩa, xem tu_lieu_sheet.jpg
D3 Hiệu ứng đặc biệt lần này: nhân bản loé · tấm kính 3D · ghép 3 thẻ + bướm · loé cam · zoom-nhoè đúng mẫu
   — đề xuất: dùng tất cả TRỪ zoom-nhoè (user ghét nhoè)
D4 Nhạc nền: file trong Resources / file khác / không nhạc — đề xuất: file nhạc tìm thấy (KHÔNG tự tổng hợp nhạc)
D5 Tên người nói + câu CTA cuối — đề xuất: tên nghe được trong lời / "Inbox ngay nhận layout chi tiết"
Sau khi sửa plan.json: đặt "CAN_CLAUDE_SUA": false rồi chạy kiem-plan.
=========================================================================================================="""


def kiem_plan(work):
    from fontTools.ttLib import TTFont
    plan = C.doc_json(os.path.join(work, 'plan.json'))
    loi, canh_bao = [], []
    if plan.get('CAN_CLAUDE_SUA', True): loi.append('plan còn CAN_CLAUDE_SUA=true — Claude chưa sửa chữ/tư liệu theo nghĩa + chưa qua cổng duyệt')
    cs = sorted(plan['canh'], key=lambda c: c['t0'])
    if abs(cs[0]['t0']) > 1e-6: loi.append('cảnh đầu phải bắt đầu ở 0')
    for a, b in zip(cs, cs[1:]):
        if abs(a['t1'] - b['t0']) > 0.011: loi.append(f"cảnh {a['id']}→{b['id']} hở/chồng: {a['t1']} vs {b['t0']}")
    if abs(cs[-1]['t1'] - plan['dur']) > 0.05: loi.append(f"cảnh cuối kết {cs[-1]['t1']} ≠ dur {plan['dur']}")
    cmap = {}
    for c in cs:
        if c['t1'] - c['t0'] < 0.6: canh_bao.append(f"cảnh {c['id']} chỉ {c['t1'] - c['t0']:.2f}s")
        for f in ([c.get('nguon')] if c.get('nguon') else []) + [t['nguon'] for t in c.get('the', [])] + \
                 [d['nguon'] for t in c.get('the', []) for d in t.get('doi', [])] + (c.get('the3d') or {}).get('nguon', []):
            p = f if os.path.isabs(f) else os.path.join(plan.get('resources') or '', f)
            if not os.path.exists(p): loi.append(f"cảnh {c['id']}: không thấy tư liệu {f}")
        if c['loai'] not in ('noi', 'anh', 'video', 'the_mo', 'ghep3'): loi.append(f"cảnh {c['id']}: loại lạ {c['loai']}")
        for b in c.get('chu', []):
            for d in b['dong']:
                if d.get('vai') not in C.VAI: loi.append(f"cảnh {c['id']}: vai chữ lạ {d.get('vai')}"); continue
                fn = C.VAI[d['vai']]['font']
                if fn not in cmap: cmap[fn] = TTFont(C.font(fn)).getBestCmap()
                import unicodedata
                thieu = sorted({ch for ch in unicodedata.normalize('NFC', d['text']) if ch.strip() and ord(ch) not in cmap[fn]})
                if thieu: loi.append(f"cảnh {c['id']}: font {fn} thiếu ký tự {''.join(thieu)} trong '{d['text']}'")
                if not (b.get('t1', 1e9) > d['t']): loi.append(f"cảnh {c['id']}: dòng '{d['text']}' hiện sau khi khối đã tắt")
            if b.get('ra', 'xoa') == 'xoa' and not b.get('vat_qua_cat') and b.get('t1', 0) + C.CHU['xoa_khung'] / C.FPS > c['t1'] + 0.02                     and c['t1'] < plan['dur'] - 0.05:
                canh_bao.append(f"cảnh {c['id']}: khối '{b['dong'][0]['text']}' xoá chưa xong lúc cắt (t1 nên ≤ {c['t1'] - C.CHU['tat_truoc_cat']:.2f}, hoặc đặt vat_qua_cat)")
            if b['dong'] and b.get('t1', 1e9) - min(d['t'] for d in b['dong']) < 0.5:
                canh_bao.append(f"cảnh {c['id']}: khối '{b['dong'][0]['text']}' hiện < 0,5 s")
    import chu
    for c in cs:
        for b in c.get('chu', []):
            lay = chu.bo_cuc(b)
            if lay:
                x0, y0, x1, y1 = chu.hop(lay)
                if y1 > C.SAFE['y1'] + 2 or y0 < C.SAFE['y0'] - 2: loi.append(f"cảnh {c['id']}: khối chữ ra ngoài vùng an toàn y {y0:.0f}–{y1:.0f}")
                if x0 < C.SAFE['x0'] - 2 or x1 > C.SAFE['x1'] + 2: loi.append(f"cảnh {c['id']}: khối chữ rộng quá vùng an toàn x {x0:.0f}–{x1:.0f}")
    for x in canh_bao: print('  CẢNH BÁO:', x)
    for x in loi: print('  LỖI:', x)
    print('kiem-plan:', 'ĐẠT' if not loi else f'{len(loi)} lỗi')
    return not loi


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('lenh', choices=['ke-hoach', 'kiem-plan', 'xem', 'dung', 'kiem'])
    ap.add_argument('--video'); ap.add_argument('--resources'); ap.add_argument('--out', required=True)
    ap.add_argument('--ten'); ap.add_argument('--nhac'); ap.add_argument('--khong-cat-lang', action='store_true')
    ap.add_argument('--moc', default=''); ap.add_argument('--ra'); ap.add_argument('--model', default='large-v3')
    ap.add_argument('--chi-tieng', action='store_true', help='giữ hinh.mp4, chỉ trộn lại tiếng + ghép + kiểm')
    a = ap.parse_args()
    work = os.path.abspath(a.out)
    if a.lenh == 'ke-hoach':
        import ke_hoach
        ke_hoach.main(a.video, a.resources, work, a.ten, a.nhac, not a.khong_cat_lang, a.model)
        print(f'\nĐã ghi {work}\\plan.json (NHÁP) · bang_duyet.md · tu_lieu_sheet.jpg')
        print(DIALOG)
        sys.exit(2)
    plan = C.doc_json(os.path.join(work, 'plan.json'))
    if a.lenh == 'kiem-plan':
        sys.exit(0 if kiem_plan(work) else 1)
    if a.lenh == 'xem':
        import dung
        moc = [float(x) for x in a.moc.split(',') if x.strip()]
        for p in dung.xem(plan, work, moc, os.path.join(work, 'xem')): print(p)
        return
    final = os.path.abspath(a.ra) if a.ra else os.path.join(work, 'final.mp4')
    if a.lenh == 'dung':
        if not kiem_plan(work): sys.exit(1)
        import dung, am_thanh
        hinh = os.path.join(work, 'hinh.mp4')
        if not (a.chi_tieng and os.path.exists(hinh)):
            dung.dung_hinh(plan, work, hinh)
        else:                                    # chỉ làm lại tiếng: vẫn tính lại danh sách SFX theo plan + luật mới
            C.ghi_json(os.path.join(work, 'sfx.json'), dung.Dung(plan, work).sfx())
        tieng = am_thanh.tron(plan, work)
        C.run(['ffmpeg', '-y', '-v', 'error', '-i', hinh, '-i', tieng, '-map', '0:v', '-map', '1:a', '-c:v', 'copy',
               '-c:a', 'aac', '-b:a', '256k', '-ar', str(C.SR), '-shortest', '-movflags', '+faststart', final])
        print('Video:', final)
    import kiem_tra
    sys.exit(0 if kiem_tra.kiem(plan, work, final) else 1)


if __name__ == '__main__':
    main()
