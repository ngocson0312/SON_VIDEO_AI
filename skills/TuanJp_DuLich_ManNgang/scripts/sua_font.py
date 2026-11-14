# -*- coding: utf-8 -*-
"""sua_font.py — chỉnh DẤU NẶNG của Barlow Condensed (bộ chữ tít màn ngang) cho tiếng Việt (soát 14/11/2026).

Barlow Condensed gốc đặt dấu nặng (dotbelowcomb) rất sâu: đỉnh dấu −0,092 em, đáy −0,274 em dưới chân chữ, chấm to 0,18 em
(≈ dấu chấm câu). Trên video chữ tít IN HOA line-height 0,94 → dấu nặng trông như chấm lạc xa chữ, sát / đè dòng phụ bên dưới
("VỊNH HẠ LONG" + "Kỳ quan thiên nhiên"). Script đặt chấm = 72 % dấu chấm câu (period) của chính font, đỉnh ở −0,035 em,
giữ tâm ngang (font nghiêng: dịch theo góc nghiêng). Mọi chữ có dấu nặng (Ạ Ặ Ậ Ẹ Ệ Ị Ọ Ộ Ợ Ụ Ự Ỵ + chữ thường) dùng chung glyph này.

Giấy phép SIL OFL 1.1, KHÔNG có Reserved Font Name → được phép chỉnh và giữ tên. Đích tính TUYỆT ĐỐI (cỡ theo period, đỉnh cố
định) → chạy lại bao nhiêu lần cũng ra cùng kết quả. Dùng: python -I -X utf8 scripts/sua_font.py
"""
import math
from pathlib import Path

from fontTools.ttLib import TTFont

FONTS = Path(__file__).resolve().parent.parent / 'assets' / 'fonts'
TEP = ['BarlowCondensed-Black.ttf', 'BarlowCondensed-BlackItalic.ttf', 'BarlowCondensed-ExtraBold.ttf']
TY_LE = 0.72          # cỡ chấm / cỡ dấu chấm câu của font
DINH = -35            # đỉnh chấm (đơn vị font, em = 1000)


def sua(p):
    t = TTFont(p)
    gl = t['glyf']
    g = gl['dotbelowcomb']
    if g.isComposite() or g.numberOfContours <= 0:
        return f'{p.name}: dotbelowcomb không phải nét đơn — bỏ qua'
    g.recalcBounds(gl)
    pd = gl['period']
    pd.recalcBounds(gl)
    ty = (pd.yMax - pd.yMin) * TY_LE / (g.yMax - g.yMin)
    if abs(ty - 1) < .01 and abs(g.yMax - DINH) <= 1:
        return f'{p.name}: đã đúng ({g.yMin}…{g.yMax})'
    nghieng = math.tan(math.radians(-(t['post'].italicAngle or 0.0)))
    cx, top = (g.xMin + g.xMax) / 2, g.yMax
    tam_cu = (g.yMin + g.yMax) / 2
    tam_moi = DINH - (g.yMax - g.yMin) * ty / 2
    dx = (tam_moi - tam_cu) * nghieng
    co = g.coordinates
    for i in range(len(co)):
        x, y = co[i]
        co[i] = (round(cx + (x - cx) * ty + dx), round(DINH + (y - top) * ty))
    g.recalcBounds(gl)
    t.save(p)
    return f'{p.name}: dấu nặng {g.yMin}…{g.yMax} (nghiêng dx {dx:+.0f})'


if __name__ == '__main__':
    for ten in TEP:
        f = FONTS / ten
        print(sua(f) if f.exists() else f'{ten}: không có')
