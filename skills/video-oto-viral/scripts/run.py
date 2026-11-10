# -*- coding: utf-8 -*-
"""video-oto-viral — CLI.
  python -I -X utf8 run.py quet --res <thư mục clip> [--nhac <file nhạc>] [--kho 16:9|9:16] [--hang VINFAST] [--dong VF3]
  python -I -X utf8 run.py nhac --work <dir> --file <nhạc> [--drop 13.7]      (phân tích lại nhạc + lập lại nháp)
  python -I -X utf8 run.py ke-hoach --work <dir> [--kho] [--hang] [--dong] [--de]
  python -I -X utf8 run.py kiem-kh --work <dir>
  python -I -X utf8 run.py tay --work <dir>              → tay_<id>.jpg (dò 2 bàn tay cho hiệu ứng manh_tay)
  python -I -X utf8 run.py duyet --work <dir>            → duyet.jpg (khung giữa mỗi cảnh + giữa mỗi chuyển cảnh)
  python -I -X utf8 run.py xem --work <dir> --t 1.2 5.6  → xem\\xem_*.jpg
  python -I -X utf8 run.py dung --work <dir> [--nhap] [--ra <file.mp4>]
  python -I -X utf8 run.py kiem --work <dir> [--video <file.mp4>]
"""
import os, sys, argparse, shutil
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import chung as C


def _work_mac_dinh(res):
    return os.path.abspath(res.rstrip('\\/')) + '_oto_work'


def _ra_mac_dinh(plan):
    res = os.path.abspath(plan['res'].rstrip('\\/'))
    return os.path.join(os.path.dirname(res), os.path.basename(res) + '_OTO.mp4')


def _plan(work):
    p = os.path.join(work, 'ke_hoach.json')
    if not os.path.exists(p):
        C.in_ra(f'⛔ chưa có {p} — chạy quet trước'); sys.exit(2)
    return C.doc_json(p)


def cmd_quet(a):
    import quet, nhac, ke_hoach
    work = a.work or _work_mac_dinh(a.res)
    os.makedirs(work, exist_ok=True)
    C.in_ra(f'Thư mục làm việc: {work}')
    tn = quet.chay(a.res, work)
    f = a.nhac
    if not f:
        if len(tn['nhac']) == 1:
            f = os.path.join(tn['res'], tn['nhac'][0]['file'])
        elif len(tn['nhac']) > 1:
            C.in_ra('⛔ thư mục có nhiều file nhạc: ' + ', '.join(x['file'] for x in tn['nhac']) + ' — hỏi người dùng rồi chạy: run.py nhac --work ... --file <nhạc>')
            return 2
        else:
            C.in_ra('⛔ KHÔNG có file nhạc trong thư mục — hỏi người dùng (gợi ý: nhạc của video mẫu) rồi chạy: run.py nhac --work ... --file <nhạc>')
            return 2
    kq = nhac.chay(f, work, a.drop)
    ke_hoach.lap(work, kq, tn, a.kho, a.hang or 'TÊN HÃNG', a.dong or 'DÒNG XE')
    C.in_ra(f'Nháp kế hoạch: {os.path.join(work, "ke_hoach.json")} — Claude soát nghĩa từng cảnh (mở khung\\clip_XX.jpg), đặt CAN_CLAUDE_SUA=false')
    return 0


def cmd_nhac(a):
    import nhac, ke_hoach
    kq = nhac.chay(a.file, a.work, a.drop)
    tn = C.doc_json(os.path.join(a.work, 'tai_nguyen.json'))
    p = os.path.join(a.work, 'ke_hoach.json')
    if os.path.exists(p):
        cu = C.doc_json(p)
        if not cu.get('CAN_CLAUDE_SUA', True):
            shutil.copy(p, p.replace('.json', '_cu.json'))
            C.in_ra('  (kế hoạch đã soát được lưu ke_hoach_cu.json — lưới nhịp đổi nên lập lại nháp)')
        ke_hoach.lap(a.work, kq, tn, cu.get('kho'), cu['chu'].get('tieu_de'), cu['chu'].get('dong_xe'))
    else:
        ke_hoach.lap(a.work, kq, tn)
    return 0


def cmd_ke_hoach(a):
    import ke_hoach
    p = os.path.join(a.work, 'ke_hoach.json')
    if os.path.exists(p) and not C.doc_json(p).get('CAN_CLAUDE_SUA', True) and not a.de:
        C.in_ra('⛔ ke_hoach.json đã được soát (CAN_CLAUDE_SUA=false) — thêm --de nếu thật sự muốn lập lại nháp'); return 2
    kq = C.doc_json(os.path.join(a.work, 'nhac.json'))
    tn = C.doc_json(os.path.join(a.work, 'tai_nguyen.json'))
    ke_hoach.lap(a.work, kq, tn, a.kho, a.hang or 'TÊN HÃNG', a.dong or 'DÒNG XE')
    return 0


def cmd_kiem_kh(a):
    import kiem
    return kiem.kiem_kh(_plan(a.work), a.work)


def _moc_duyet(plan):
    moc = []
    cs = plan['canh']
    for i, c in enumerate(cs):
        moc.append(c['t0'] + (c['t1'] - c['t0']) * 0.55)
        if i:
            kieu = (c.get('chuyen') or {}).get('kieu', 'cat')
            tr = C.CHUYEN.get(kieu, C.CHUYEN['cat'])['truoc']
            s = C.moc_cat(c)
            if tr >= 0.3:
                moc.append(s - tr * 0.45)
            elif kieu != 'cat':
                moc.append(s + 0.05)
    T = plan['nhac']['ket_nhac']
    return sorted(set(round(min(m, T - 0.05), 3) for m in moc))


def cmd_duyet(a):
    import dung, ke_hoach
    plan = _plan(a.work)
    anh = dung.xem(plan, a.work, _moc_duyet(plan), os.path.join(a.work, 'xem'))
    p = ke_hoach.to_duyet(_plan(a.work), a.work, anh)
    ke_hoach.in_bang(_plan(a.work))
    C.in_ra(f'Tờ duyệt: {p}')
    return 0


def cmd_xem(a):
    import dung
    plan = _plan(a.work)
    ra = dung.xem(plan, a.work, sorted(a.t), os.path.join(a.work, 'xem'))
    for t, p, _ in ra:
        C.in_ra(f'  {t:.2f} s → {p}')
    return 0


def cmd_tay(a):
    """Dò 2 bàn tay cho cảnh có hiệu ứng manh_tay → tay_<id>.jpg (Claude MỞ soi: chấm xanh/đỏ phải nằm trên 2 bàn tay)."""
    import dung, tay
    plan = _plan(a.work)
    d = dung.Dung(plan, a.work)
    try:
        co = False
        for c in d.canh:
            if not c.get('_tay'):
                continue
            co = True
            p = C.tim_file(plan['res'], c['nguon'])
            ra = tay.to_soat(c['_tay'], p, c['_info'], c.get('xoay', 0), os.path.join(a.work, f"tay_{c['id']}.jpg"))
            ok = c['_tay']['ok']
            toc = float(c.get('toc', 1.0))
            C.in_ra(f"  cảnh {c['id']}: thấy 2 tay {sum(ok)}/{len(ok)} khung nguồn → {ra}")
            C.in_ra(f"    giây VIDEO = {c['_tref']:.3f} + (giây NGUỒN − {c['_ss_goc']:.3f}) / {toc} "
                    f"— đặt manh_tay.t0 lúc tay bắt đầu cầm / căng (vd phách mạnh gần nhất)")
        if not co:
            C.in_ra('  (không cảnh nào có hiệu ứng manh_tay)')
    finally:
        d.dong()
    return 0


def cmd_dung(a):
    import dung, kiem
    plan = _plan(a.work)
    if kiem.kiem_kh(plan, a.work):
        C.in_ra('⛔ kế hoạch còn lỗi — không dựng'); return 2
    plan = _plan(a.work)
    ra = a.ra or _ra_mac_dinh(plan)
    if a.nhap:
        b, e = os.path.splitext(ra); ra = b + '_nhap' + e
    ra, het = dung.dung(plan, a.work, ra, a.nhap)
    with open(os.path.join(a.work, 'ra.txt'), 'w', encoding='utf-8') as f:
        f.write(ra)
    return 0


def cmd_kiem(a):
    import kiem
    v = a.video
    if not v:
        p = os.path.join(a.work, 'ra.txt')
        if not os.path.exists(p):
            C.in_ra('⛔ chưa dựng — không biết video nào'); return 2
        v = open(p, encoding='utf-8').read().strip()
    C.in_ra(f'Tự kiểm {v}')
    return kiem.kiem_video(_plan(a.work), a.work, v)


def main():
    ap = argparse.ArgumentParser(prog='video-oto-viral')
    sp = ap.add_subparsers(dest='lenh', required=True)
    q = sp.add_parser('quet'); q.add_argument('--res', required=True); q.add_argument('--work'); q.add_argument('--nhac')
    q.add_argument('--drop', type=float); q.add_argument('--kho', choices=list(C.KHO)); q.add_argument('--hang'); q.add_argument('--dong')
    n = sp.add_parser('nhac'); n.add_argument('--work', required=True); n.add_argument('--file', required=True); n.add_argument('--drop', type=float)
    k = sp.add_parser('ke-hoach'); k.add_argument('--work', required=True); k.add_argument('--kho', choices=list(C.KHO))
    k.add_argument('--hang'); k.add_argument('--dong'); k.add_argument('--de', action='store_true')
    for ten in ('kiem-kh', 'duyet', 'tay'):
        x = sp.add_parser(ten); x.add_argument('--work', required=True)
    x = sp.add_parser('xem'); x.add_argument('--work', required=True); x.add_argument('--t', type=float, nargs='+', required=True)
    d = sp.add_parser('dung'); d.add_argument('--work', required=True); d.add_argument('--nhap', action='store_true'); d.add_argument('--ra')
    v = sp.add_parser('kiem'); v.add_argument('--work', required=True); v.add_argument('--video')
    a = ap.parse_args()
    if getattr(a, 'work', None):
        a.work = os.path.abspath(a.work)
    f = {'quet': cmd_quet, 'nhac': cmd_nhac, 'ke-hoach': cmd_ke_hoach, 'kiem-kh': cmd_kiem_kh, 'duyet': cmd_duyet,
         'xem': cmd_xem, 'dung': cmd_dung, 'kiem': cmd_kiem, 'tay': cmd_tay}[a.lenh]
    sys.exit(f(a) or 0)


if __name__ == '__main__':
    main()
