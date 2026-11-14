# -*- coding: utf-8 -*-
"""dong_goi.py — đóng gói skill thành 1 file zip gửi khách: giải nén → CAI_DAT.bat → mở thư mục trong Claude Code là chạy.

  python -I -X utf8 run.py dong-goi [--out <file.zip>] [--mau <thư mục có giọng đọc + Resources>]
  (mặc định <thư mục dự án>\\Goi_khach\\TuanJp_DuLich_ManNgang_<ngày>.zip; có rồi thì _ban2… — không ghi đè)

Trong zip (thư mục gốc ASCII 'TuanJp_DuLich_ManNgang\\'):
  .claude\\skills\\TuanJp_DuLich_ManNgang\\   toàn bộ skill: code, font (đã vá dấu nặng), SFX, khung đồ hoạ, bản đồ VN, bình luận ảo,
                                            mẫu kế hoạch đã duyệt — bỏ __pycache__ / work / video
      assets\\models\\u2net_human_seg.onnx   mô hình TÁCH NGƯỜI (~170 MB, Apache-2.0) cho cú ĐẨY montage — không có trên git,
                                            lấy từ máy đóng gói (~/.u2net hoặc skill bds-sale-viral)
  CLAUDE.md + AGENTS.md                     chỉ dẫn cho trợ lý AI (từ goi_khach\\CLAUDE.md)
  CAI_DAT.bat                               cài thư viện Python + kiểm máy (run.py cai-dat)
  HUONG_DAN_CAI_DAT.txt                     hướng dẫn cho người dùng (có BOM cho Notepad)
  Mau_thu\\  (khi có --mau)                  1 file giọng + Resources của bộ thử → làm ra đúng bản demo đã duyệt để kiểm máy
KHÔNG kèm: work / video của khách, cache ảnh vệ tinh (tự tải), mô hình Whisper ~3 GB (tự tải lần đầu / CAI_DAT.bat --tai-mo-hinh).
"""
import datetime as dt
import shutil
import tempfile
import zipfile
from pathlib import Path

from cai_dat import tim_u2net

SKILL = Path(__file__).resolve().parent.parent
TL = SKILL / 'goi_khach'
GOC_ZIP = 'TuanJp_DuLich_ManNgang'
BO = ('__pycache__', '*.pyc', '.DS_Store', 'Thumbs.db', '*_work', '*_work_*', '*.mp4', '_hop*.json')
AM = {'.mp3', '.m4a', '.wav', '.aac', '.flac', '.ogg'}
KICH_BAN = {'.txt', '.md', '.docx', '.pdf'}                      # kịch bản / prompt đi kèm bộ thử
DA_NEN = {'.mp4', '.mov', '.m4v', '.mkv', '.webm', '.mp3', '.m4a', '.aac', '.jpg', '.jpeg', '.jfif', '.png', '.webp', '.heic',
          '.avif', '.zip'}

MAU_CLAUDE = """
## 4. Bộ dữ liệu thử (Mau_thu)

`Mau_thu\\Audio.mp3` + `Mau_thu\\Resources` (clip / ảnh / `Music_Bg.mp3`) là bộ thử của bản demo khách đã duyệt (4 điểm đến Sa Pa →
Hạ Long → Ninh Bình → Bản Giốc, ~127 s). Kiểm máy mới: "Làm video du lịch ngang từ audio Mau_thu\\Audio.mp3 + Resources
Mau_thu\\Resources". Mã tài nguyên của bộ này khớp `references\\vi-du-4-diem-den.json` (kế hoạch đã duyệt): chép file đó thành
`ke_hoach.json` trong thư mục work (sau bước quét) là ra đúng bản demo; với Resources khác thì viết kế hoạch mới theo NGHĨA lời.
"""

MAU_HD = """

7. BỘ DỮ LIỆU THỬ (thư mục Mau_thu)
--------------------------------------------------------------------------------
Mau_thu\\Audio.mp3 + Mau_thu\\Resources là bộ thử của bản demo đã duyệt (Sa Pa → Hạ Long → Ninh Bình → Bản Giốc, ~2 phút).
Cài xong, gõ trong Claude Code:

    Làm video du lịch ngang từ audio Mau_thu\\Audio.mp3 + Resources Mau_thu\\Resources

→ ra Mau_thu\\Audio_DLN.mp4 giống bản demo. Chạy được bộ này là máy đã đủ để làm video mới.
"""


def _crlf(src, dst, bom=False, them=''):
    s = (src.read_text(encoding='utf-8') + them).replace('\r\n', '\n').replace('\n', '\r\n')
    dst.write_bytes((b'\xef\xbb\xbf' if bom else b'') + s.encode('utf-8'))


def _du_an():
    return SKILL.parent.parent.parent       # <dự án>\.claude\skills\<skill> (gói khách) hoặc <dự án>\SON_VIDEO_AI\skills\<skill>


def dong_goi(out=None, mau=None):
    out = Path(out) if out else _du_an() / 'Goi_khach' / f'{GOC_ZIP}_{dt.date.today():%Y-%m-%d}.zip'
    if out.exists():
        i = 2
        while out.with_name(f'{out.stem}_ban{i}{out.suffix}').exists():
            i += 1
        out = out.with_name(f'{out.stem}_ban{i}{out.suffix}')
    out.parent.mkdir(parents=True, exist_ok=True)
    mau = Path(mau) if mau else None
    if mau and not mau.is_dir():
        raise SystemExit(f'⛔ --mau không phải thư mục: {mau}')
    with tempfile.TemporaryDirectory(prefix='dln_goi_') as tmp:
        st = Path(tmp) / GOC_ZIP
        sk = st / '.claude' / 'skills' / SKILL.name
        shutil.copytree(SKILL, sk, ignore=shutil.ignore_patterns(*BO))
        # ---- mô hình tách người ----
        u2 = tim_u2net()
        if u2:
            (sk / 'assets' / 'models').mkdir(parents=True, exist_ok=True)
            shutil.copy2(u2, sk / 'assets' / 'models' / 'u2net_human_seg.onnx')
            (sk / 'assets' / 'models' / 'README.txt').write_text(
                'u2net_human_seg.onnx — mô hình tách người U²-Net (Qin et al.), giấy phép Apache-2.0\r\n'
                'https://github.com/xuebinqin/U-2-Net — dùng cho cú ĐẨY montage (người nhô qua mép). Đừng xoá.\r\n', encoding='utf-8')
            print(f'  + mô hình tách người: {u2} ({u2.stat().st_size / 1e6:.0f} MB)')
        else:
            print('  ⚠ KHÔNG thấy u2net_human_seg.onnx (~/.u2net) — gói thiếu tách người: cú ĐẨY montage chỉ có chữ + vạch sáng')
        # ---- bộ thử ----
        them_cl = them_hd = ''
        if mau:
            dm = st / 'Mau_thu'
            dm.mkdir()
            giong = [p for p in sorted(mau.iterdir()) if p.is_file() and p.suffix.lower() in AM]
            res = [p for p in sorted(mau.iterdir()) if p.is_dir() and p.name.lower() in ('resources', 'resource', 'res')]
            if not giong or not res:
                raise SystemExit(f'⛔ --mau phải có 1 file giọng (mp3 / m4a / wav) + thư mục Resources ngay trong {mau}')
            kb = [p for p in sorted(mau.iterdir()) if p.is_file() and p.suffix.lower() in KICH_BAN]
            giong += kb
            for p in giong:
                shutil.copy2(p, dm / p.name)
            shutil.copytree(res[0], dm / res[0].name, ignore=shutil.ignore_patterns('__pycache__', '*_work', 'Thumbs.db', '.DS_Store'))
            n_res = sum(1 for _ in (dm / res[0].name).rglob('*') if _.is_file())
            print(f'  + bộ thử: {", ".join(p.name for p in giong)} + {res[0].name}\\ ({n_res} file)')
            them_cl, them_hd = MAU_CLAUDE, MAU_HD
        _crlf(TL / 'CLAUDE.md', st / 'CLAUDE.md', them=them_cl)
        _crlf(TL / 'CLAUDE.md', st / 'AGENTS.md', them=them_cl)
        _crlf(TL / 'CAI_DAT.bat', st / 'CAI_DAT.bat')
        _crlf(TL / 'HUONG_DAN_CAI_DAT.txt', st / 'HUONG_DAN_CAI_DAT.txt', bom=True, them=them_hd)
        n = 0
        with zipfile.ZipFile(out, 'w') as z:                     # tên có dấu → cờ UTF-8 (Windows 10/11, 7-Zip đọc đúng)
            for p in sorted(st.rglob('*')):
                arc = p.relative_to(st.parent).as_posix()
                if p.is_dir():
                    z.writestr(arc + '/', '')
                elif p.suffix.lower() in DA_NEN:                 # ảnh / video / nhạc đã nén sẵn → cất nguyên (nhanh, không phình)
                    z.write(p, arc, compress_type=zipfile.ZIP_STORED)
                    n += 1
                else:
                    z.write(p, arc, compress_type=zipfile.ZIP_DEFLATED, compresslevel=6)
                    n += 1
    print(f'ĐÓNG GÓI: {n} file → {out}  ({out.stat().st_size / 1e6:.1f} MB)')
    print('  khách: giải nén → nháy đúp CAI_DAT.bat (phải ra "SẴN SÀNG") → mở thư mục trong Claude Code → đọc HUONG_DAN_CAI_DAT.txt')
    return out
