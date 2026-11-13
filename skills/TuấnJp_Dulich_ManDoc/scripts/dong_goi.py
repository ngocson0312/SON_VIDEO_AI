# -*- coding: utf-8 -*-
"""dong_goi.py — đóng gói skill thành 1 file zip gửi khách: giải nén → CAI_DAT.bat → mở thư mục trong Claude Code là chạy.

  python -I -X utf8 run.py dong-goi [--out <file.zip>]
  (mặc định <thư mục dự án>\\Goi_khach\\TuanJp_Dulich_ManDoc_<ngày>.zip; có rồi thì _ban2… — không ghi đè)

Trong zip (thư mục gốc ASCII 'TuanJp_Dulich_ManDoc\\'):
  .claude\\skills\\<skill>\\   toàn bộ skill (code, font, SFX, khung đồ hoạ, mẫu) — bỏ __pycache__
  CLAUDE.md + AGENTS.md         chỉ dẫn cho trợ lý AI (từ goi_khach\\CLAUDE.md)
  CAI_DAT.bat                   cài thư viện Python + kiểm máy (run.py cai-dat)
  HUONG_DAN_CAI_DAT.txt         hướng dẫn cho người dùng (có BOM cho Notepad)
KHÔNG kèm: Resources / work / video từng khách, cache ảnh vệ tinh, mô hình Whisper (tự tải lần đầu).
"""
import datetime as dt
import shutil
import tempfile
import zipfile
from pathlib import Path

SKILL = Path(__file__).resolve().parent.parent
TL = SKILL / 'goi_khach'
GOC_ZIP = 'TuanJp_Dulich_ManDoc'
BO = ('__pycache__', '*.pyc', '.DS_Store', 'Thumbs.db', '*_work', '*.mp4')


def _crlf(src, dst, bom=False):
    s = src.read_text(encoding='utf-8').replace('\r\n', '\n').replace('\n', '\r\n')
    dst.write_bytes((b'\xef\xbb\xbf' if bom else b'') + s.encode('utf-8'))


def dong_goi(out=None):
    if out:
        out = Path(out)
    else:
        du_an = SKILL.parent.parent if SKILL.parent.name == 'skills' and SKILL.parent.parent.name == '.claude' \
            else SKILL.parent.parent.parent                       # máy chủ skill: SON_VIDEO_AI\skills\<skill> → thư mục dự án
        out = du_an / 'Goi_khach' / f'{GOC_ZIP}_{dt.date.today():%Y-%m-%d}.zip'
    if out.exists():
        i = 2
        while out.with_name(f'{out.stem}_ban{i}{out.suffix}').exists():
            i += 1
        out = out.with_name(f'{out.stem}_ban{i}{out.suffix}')
    out.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='dlv_goi_') as tmp:
        st = Path(tmp) / GOC_ZIP
        shutil.copytree(SKILL, st / '.claude' / 'skills' / SKILL.name, ignore=shutil.ignore_patterns(*BO))
        _crlf(TL / 'CLAUDE.md', st / 'CLAUDE.md')
        _crlf(TL / 'CLAUDE.md', st / 'AGENTS.md')
        _crlf(TL / 'CAI_DAT.bat', st / 'CAI_DAT.bat')
        _crlf(TL / 'HUONG_DAN_CAI_DAT.txt', st / 'HUONG_DAN_CAI_DAT.txt', bom=True)
        n = 0
        with zipfile.ZipFile(out, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as z:   # tên có dấu → cờ UTF-8 (Windows 10/11, 7-Zip đọc đúng)
            for p in sorted(st.rglob('*')):
                arc = p.relative_to(st.parent).as_posix()
                if p.is_dir():
                    z.writestr(arc + '/', '')
                else:
                    z.write(p, arc)
                    n += 1
    print(f'ĐÓNG GÓI: {n} file → {out}  ({out.stat().st_size / 1e6:.1f} MB)')
    print('  khách: giải nén → nháy đúp CAI_DAT.bat (phải ra "SẴN SÀNG") → mở thư mục trong Claude Code → đọc HUONG_DAN_CAI_DAT.txt')
    return out
