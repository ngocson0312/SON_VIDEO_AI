# -*- coding: utf-8 -*-
"""Claude soạn chữ nhấn + chuyển cảnh theo NGHĨA lời (video Vinh — giảm cân). Chạy sau `hook` / `nhap-vinh`."""
import json, os, re, sys
W = os.path.dirname(os.path.abspath(__file__))
plan = json.load(open(os.path.join(W, 'ke_hoach.json'), encoding='utf-8'))
words = json.load(open(os.path.join(W, 'words.json'), encoding='utf-8'))
L = json.load(open(os.path.join(W, 'hook.json'), encoding='utf-8'))['L']


def tk(w): return re.sub(r'[.,!?;:…"“”]+$', '', w['w']).lower()


def tim(seq, sau=0.0, truoc=1e9):
    """chỉ số chữ đầu của chuỗi chữ `seq` đầu tiên có start trong [sau, truoc)."""
    for i in range(len(words) - len(seq) + 1):
        if words[i]["s"] < sau - 0.05 or words[i]['s'] >= truoc: continue
        if all(tk(words[i + k]) == seq[k] for k in range(len(seq))): return i
    raise SystemExit('Không thấy: ' + ' '.join(seq))


nhan = []


def N(seq, text, dai=2.0, sau=0.0, truoc=1e9, phu=None, kieu='chu', t1=None, lui=0.10, an_sub=None, t1_seq=None, **kw):
    i = tim(seq, sau, truoc)
    t0 = round(max(0.1, words[i]['s'] - lui), 2)
    if t1_seq:
        t1 = round(words[tim(t1_seq, words[i]['s'] + 0.1, truoc)]['s'] - 0.06, 2)
    t1 = t1 if t1 else round(t0 + dai, 2)
    d = {'t0': t0, 't1': round(t1, 2), 'text': text, 'kieu': kieu}
    if phu: d['phu'] = phu
    if an_sub or kieu == 'so': d['an_sub'] = True
    d.update(kw)
    nhan.append(d)
    return d


# ---------- HOOK (0 … L): kết quả giảm cân + KHÔNG cắt calo / tinh bột
N(['4', 'cân'], '4 - 5 - 6 CÂN', 2.4, truoc=L, t1_seq=['hơn', '10'])
N(['hơn', '10'], 'HƠN 10 CÂN', 1.6, truoc=L, t1_seq=['không', 'hề'])
N(['không', 'hề'], 'KHÔNG CẮT CALO', 2.6, truoc=L, t1_seq=['cắt', 'bỏ'])
N(['cắt', 'bỏ'], 'KHÔNG BỎ TINH BỘT', 1.4, truoc=L, t1=L - 0.12)
# ---------- MỞ BÀI
N(['80%'], '80% PT KHÔNG NÓI', 2.9, sau=L)
N(['bí', 'mật'], 'BÍ MẬT NGHỀ NGHIỆP', 2.0, sau=L)
N(['kinh', 'nghiệm', 'trong'], 'KINH NGHIỆM GIẢM CÂN', 2.2, sau=L)
# ---------- ĐIỀU QUAN TRỌNG NHẤT
N(['quan', 'trọng', 'nhất'], 'QUAN TRỌNG NHẤT', 1.4, sau=L)
N(['duy', 'trì'], 'DUY TRÌ', 1.5, sau=L + 14)
N(['điều', 'độ'], 'ĐIỀU ĐỘ', 1.5, sau=L + 14, lui=0.5)
N(['việc', 'đến'], '1', phu='Đến phòng tập đều', kieu='so', sau=L, t1_seq=['thứ', 'hai'])
N(['thứ', 'hai'], '2', phu='Thói quen tập luyện', kieu='so', sau=L, t1=None, dai=3.2)
N(['ăn', 'đủ'], 'ĂN ĐỦ BỮA', 1.9, sau=L)
N(['rất', 'rất'], 'ĂN RẤT ÍT', 2.0, sau=L)
N(['muốn', 'giảm'], 'MUỐN GIẢM CÂN', 1.7, sau=L)
N(['lo', 'là', 'ăn'], 'ĂN ÍT, CẮT TINH BỘT', 2.6, sau=L, t1_seq=['thì', 'mình', 'là', 'một'])
# ---------- KINH NGHIỆM + LỜI KHUYÊN
N(['người', 'đào', 'tạo'], 'ĐÀO TẠO HLV', 2.0, sau=L)
N(['chuyên', 'sâu'], 'CHUYÊN SÂU DINH DƯỠNG', 2.1, sau=L)
N(['cân', 'bằng', 'trong'], 'CÂN BẰNG NĂNG LƯỢNG', 1.5, sau=L, t1_seq=['nên', 'mọi'])
N(['vẫn', 'ăn'], '1', phu='Ăn đầy đủ', kieu='so', sau=L, dai=1.55)
N(['thứ', '2'], '2', phu='Duy trì + điều độ', kieu='so', sau=L, dai=3.5)
N(['tích', 'lũy'], 'TÍCH LŨY DẦN DẦN', 1.9, sau=L)
# ---------- ĐỪNG GIẢM NHANH
N(['đừng', 'quan'], 'ĐỪNG GIẢM QUÁ NHANH', 2.4, sau=L)
N(['bị', 'hiệu'], 'HIỆU ỨNG YO-YO', 2.0, sau=L, lui=0.0)
yo = tim(['yo-yo'], L)
N(['giảm', 'nhanh'], 'GIẢM NHANH, LÊN NHANH', 2.0, sau=words[yo]['e'] + 0.3, lui=0.2)
N(['comment', 'ở', 'dưới'], 'COMMENT Ở DƯỚI', 1.7, sau=L + 70, lui=0.9)
# ---------- KẾT
fin = tim(['ở', 'đây', 'có'], L + 80)
N(['hơn', '10'], 'HƠN 10 CÂN', 1.5, sau=L + 80)
N(['không', 'hề'], 'KHÔNG CẮT CALO', 2.3, sau=L + 80, t1_seq=['cắt', 'bỏ'])
N(['cắt', 'bỏ'], 'KHÔNG BỎ TINH BỘT', 1.6, sau=L + 80)
N(['feedback'], 'FEEDBACK PHÒNG TẬP', 1.7, sau=L + 80, lui=0.15)
N(['comment', 'nha'], 'COMMENT NGAY', 1.6, sau=L + 100, lui=0.4)

# chống chồng nhau
nhan.sort(key=lambda x: x['t0'])
for a, b in zip(nhan[:-1], nhan[1:]):
    if a['t1'] > b['t0'] - 0.06: a['t1'] = round(b['t0'] - 0.06, 2)
for n in nhan:
    if n['t1'] - n['t0'] < 1.0: print('⚠ nhấn ngắn', n)
plan['nhan'] = nhan

# ---------- chuyển cảnh (ngoài loé vàng ở chỗ nối hook)
ch = [{'t': round(L, 3), 'kieu': 'flash_vang'}]
for seq, kieu, sau in ((['khi', 'mọi', 'người'], 'glitch', L), (['thì', 'mình', 'là', 'một'], 'flash_vang', L + 40),
                       (['thứ', '2', 'nữa'], 'glitch', L + 60), (['nhưng', 'mà', 'khi'], 'flash_vang', L + 70),
                       (['ở', 'đây', 'có'], 'glitch', L + 80)):
    i = tim(seq, sau)
    ch.append({'t': round(words[i]['s'] - 0.06, 3), 'kieu': kieu})
plan['chuyen'] = sorted(ch, key=lambda c: c['t'])
# zoom: bỏ zoom trùng chuyển cảnh (zoom đổi cùng lúc với loé cho mượt)
plan['mau_nhan'] = None
json.dump(plan, open(os.path.join(W, 'ke_hoach.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(len(nhan), 'chữ nhấn,', len(plan['chuyen']), 'chuyển cảnh')
for n in nhan: print('%6.2f-%6.2f %-5s %s %s' % (n['t0'], n['t1'], n['kieu'], n['text'], n.get('phu', '')))
for c in plan['chuyen']: print(c)
