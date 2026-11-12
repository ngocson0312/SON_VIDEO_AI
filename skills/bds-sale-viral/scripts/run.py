# -*- coding: utf-8 -*-
"""bds-sale-viral — 1 cửa lệnh.

  phan-tich --video <video thô> [--res <thư mục ảnh/clip/logo/nhạc>] [--nhac <file>] [--ten "<tên dự án>"]
            [--cat-lang auto|co|khong] [--work <thư mục>]          → đo + ke_hoach.json NHÁP (thoát mã 2: Claude phải sửa)
  nguoi     --work <dir>     → tách người cả video (để tiêu đề nằm SAU người; ~0,15 s/khung, chạy nền được)
                               + dò cử chỉ TAY (tay.json + tay.jpg — chỗ icon / thẻ ảnh mọc ra từ lòng bàn tay)
  tay       --work <dir> [--gop]   → dò lại cử chỉ tay (MediaPipe nếu đã cai-tay, không thì mặt nạ người);
                               --gop: chép icon GỢI Ý (từ khoá trong lời trùng lúc tay làm cử chỉ) vào ke_hoach.json
  cai-tay                    → (1 lần / máy, cần mạng) venv riêng ~/.bds_sale_viral/venv_tay + mediapipe 0.10.21
  kiem-kh   --work <dir>     → soát kế hoạch (⛔ phải sửa / ⚠ nên xem)
  duyet     --work <dir>     → duyet.jpg (khung dựng thử ở mọi đồ hoạ) + bang_duyet.md — CỔNG DUYỆT
  dung      --work <dir> [--out <file.mp4>]   → tiếng + hình (mã hoá 1 lần) → tự kiểm
  kiem      --work <dir> --video <file.mp4>   → tự kiểm file cuối + soat.jpg
"""
import os, sys, argparse
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import chung as C


def _work(a, video=None):
    if a.work: return os.path.abspath(a.work)
    v = video or a.video
    return os.path.splitext(os.path.abspath(v))[0] + '_bsv_work'


def main():
    C.utf8_stdout()
    ap = argparse.ArgumentParser()
    ap.add_argument('lenh')
    ap.add_argument('--video'); ap.add_argument('--res'); ap.add_argument('--nhac'); ap.add_argument('--ten', default='')
    ap.add_argument('--cat-lang', dest='cat_lang', default='auto'); ap.add_argument('--work'); ap.add_argument('--out')
    ap.add_argument('--bo-kiem', action='store_true'); ap.add_argument('--gop', action='store_true')
    a = ap.parse_args()
    L = a.lenh
    if L == 'cai-tay':
        import tay
        sys.exit(0 if tay.cai_dat() else 1)
    if L == 'phan-tich':
        import phan_tich
        if not a.video or not os.path.exists(a.video): sys.exit('Thiếu --video hoặc file không có')
        w = _work(a)
        phan_tich.chay(a.video, a.res, w, a.nhac, a.cat_lang, a.ten)
        print('\n→ Claude: mở loi_doc.txt, tai_nguyen.jpg, khung tiêu biểu; SỬA ke_hoach.json theo NGHĨA rồi đặt '
              '"CAN_CLAUDE_SUA": false → run.py nguoi (nền) + kiem-kh + duyet.')
        sys.exit(2)
    w = _work(a)
    if not os.path.isdir(w): sys.exit('Không thấy thư mục work ' + w)
    if L == 'nguoi':
        import nguoi, tay
        tay.do_mat(w)          # mặt / đầu MediaPipe trước (tách người cắt ô quanh mặt, chữ né mặt theo mặt này)
        ok = nguoi.tinh_het(w)
        if ok or tay.venv_py():
            tay.tinh(w)
        sys.exit(0 if ok else 1)
    if L == 'tay':
        import tay
        tay.do_mat(w)
        kq = tay.tinh(w)
        if kq is None: sys.exit('⛔ chưa dò được tay: chạy run.py cai-tay (MediaPipe) hoặc run.py nguoi (mặt nạ người)')
        print('  ảnh soát: ' + os.path.join(w, 'tay.jpg'))
        if a.gop:
            p = os.path.join(w, 'ke_hoach.json')
            plan = C.doc_json(p)
            them = tay.gop_ke_hoach(plan, kq)
            C.ghi_json(p, plan)
            print(f'  đã chép {them} icon gợi ý vào ke_hoach.json — Claude SỬA nhãn / loại theo nghĩa, bỏ cái thừa')
        return
    plan = C.doc_json(os.path.join(w, 'ke_hoach.json'))
    if L == 'kiem-kh':
        import kiem
        loi = kiem.kiem_ke_hoach(plan, w)
        sys.exit(1 if loi else 0)
    if L == 'duyet':
        import kiem, duyet
        loi = kiem.kiem_ke_hoach(plan, w)
        if loi: sys.exit('⛔ sửa ke_hoach.json trước khi duyệt')
        duyet.lam(plan, w)
        return
    if L == 'dung':
        import kiem, am_thanh, dung, nguoi
        if plan.get('CAN_CLAUDE_SUA'): sys.exit('⛔ ke_hoach.json còn CAN_CLAUDE_SUA=true — Claude chưa sửa theo nghĩa')
        if kiem.kiem_ke_hoach(plan, w): sys.exit('⛔ sửa ke_hoach.json trước')
        import tay
        tay.do_mat(w, bao=False)
        if plan.get('tieu_de') or plan.get('logo') or plan.get('icon') or plan.get('the_anh'):
            nguoi.tinh_het(w)
        print('Trộn tiếng…', flush=True)
        tieng = am_thanh.tron(plan, w)
        out = a.out or dung.ten_ra(plan.get('video_goc') or os.path.join(w, 'video.mp4'))
        print('Dựng hình…', flush=True)
        dung.dung_video(plan, w, tieng, out)
        if not a.bo_kiem:
            ok = kiem.kiem_video(plan, w, out)
            sys.exit(0 if ok else 1)
        return
    if L == 'kiem':
        import kiem
        if not a.video: sys.exit('Thiếu --video')
        ok = kiem.kiem_video(plan, w, a.video)
        sys.exit(0 if ok else 1)
    sys.exit('Lệnh lạ: ' + L)


if __name__ == '__main__':
    main()
