# -*- coding: utf-8 -*-
"""run.py — skill bds_model_3d: video BĐS kiểu "thẻ nổi 3D + chữ 2 tầng + giao diện app" (video mẫu Khánh Nguyễn).

Lệnh (chạy: python -I -X utf8 .claude\\skills\\bds_model_3d\\scripts\\run.py <lệnh> …):
  quet     --video X | --audio A --res DIR  [--res DIR] [--nhac M] [--tu-khoa "a,b"] [--work W]
           [--3d [--vi-tri "lat,lon" | --dia-chi "tên / địa chỉ"]]   (nháp có CẢNH 3D công trình trên ảnh vệ tinh)
  quet     --res ẢNH --3d [--vi-tri …] [--work W]   (CHỈ CÓ ẢNH, chưa có giọng: dựng mô hình trước; giọng đưa sau
           bằng quet --audio … --3d --work W — mô hình giữ nguyên)
  tim      "tên dự án / địa chỉ"              (tìm toạ độ OSM cho mo_hinh_3d.vi_tri — cần mạng)
  xem-3d   --work W                          (ảnh mô hình 6 góc + ảnh dự án → mo_hinh_3d.jpg để so — cần mạng lần đầu)
  bay-thu  --work W [--giay 12] [--out X]    (video câm camera bay quanh mô hình — xem trước khi chưa có giọng)
  luoi-anh --anh ẢNH --vung x0,y0,x1,y1 [--to 2] [--work W]   (kẻ lưới toạ độ lên ảnh phối cảnh để đọc 4 góc mặt đứng)
  mat-anh  --work W --anh ẢNH --goc "x,y x,y x,y x,y" --id ten [--tang N] [--rong 320] [--sang 1] [--giu-goc]
           (DÁN MẶT ĐỨNG ẢNH THẬT: cắt + nắn phẳng 1 mặt tháp → W/mat_anh/<id>.jpg; tháp ghi "anh_mat": "<id>";
            tự dò vạch cửa / sàn chỉnh góc cho mặt THẲNG — --giu-goc để dùng nguyên góc chấm)
  nhac     --work W --file M                 (đặt / đổi nhạc nền)
  kiem-kh  --work W                          (kiểm kế hoạch + đo bố cục chữ trong Chrome)
  duyet    --work W                          (ảnh duyệt duyet.jpg + bang_duyet.txt → CỔNG DUYỆT)
  dung     --work W [--out ra.mp4] [--luong 3]
  kiem     --work W [--file ra.mp4]
  nns      --file ra.mp4                     (bản gửi khách: chữ NNS mờ chạy quanh khung)
"""
import argparse
import json
import math
import shutil
import sys
import time
import unicodedata
import re
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from chung import (ASSETS, AUDIO_EXT, DUOI, FPS, H, IMG_EXT, KHUNG, LUFS, TP, VIDEO_EXT, W, doc_json, ghi_json, loi,  # noqa: E402
                   nhan_loi, node, probe, run, ten_moi, url)
import ke_hoach as KHM  # noqa: E402

SCRIPTS = Path(__file__).resolve().parent
FONT = ASSETS / 'fonts' / 'BeVietnamPro-SemiBold.ttf'


# ---------------- tiện ích ----------------
def khoa(stem, da_co):
    s = unicodedata.normalize('NFD', stem.lower()).replace('đ', 'd')
    s = ''.join(c for c in s if unicodedata.category(c) != 'Mn')
    s = re.sub(r'[^a-z0-9]+', '_', s).strip('_')[:28] or 'clip'
    k, i = s, 2
    while k in da_co:
        k = f'{s}_{i}'; i += 1
    return k


def work_dir(a):
    w = Path(a.work)
    if not w.exists():
        raise SystemExit(f'⛔ không có thư mục work {w}')
    return w


def nap(w):
    meta = doc_json(w / 'meta.json')
    kh = doc_json(w / 'ke_hoach.json')
    tu = doc_json(w / 'tu.json')['tu']
    fo = {k: v['file'] for k, v in doc_json(w / 'footage.json').items()}
    return meta, kh, tu, fo


def font(sz):
    from PIL import ImageFont
    return ImageFont.truetype(str(FONT), sz)


def luoi(anh_nhan, out, cot=6, cw=270, ch=480, tieu_de=''):
    """ghép ảnh (đường dẫn, nhãn) thành 1 tờ có nhãn."""
    from PIL import Image, ImageDraw
    n = len(anh_nhan)
    hang = max(1, math.ceil(n / cot))
    top = 70 if tieu_de else 0
    sheet = Image.new('RGB', (cot * (cw + 10) + 10, top + hang * (ch + 64) + 10), (24, 25, 30))
    d = ImageDraw.Draw(sheet)
    if tieu_de:
        d.text((14, 16), tieu_de, font=font(34), fill=(253, 240, 42))
    f = font(22)
    for i, (p, nhan) in enumerate(anh_nhan):
        x, y = 10 + (i % cot) * (cw + 10), top + 10 + (i // cot) * (ch + 64)
        try:
            im = Image.open(p).convert('RGB')
            im.thumbnail((cw, ch))
            sheet.paste(im, (x + (cw - im.width) // 2, y + (ch - im.height) // 2))
        except Exception:
            d.rectangle([x, y, x + cw, y + ch], outline=(200, 60, 60), width=3)
        dong = []
        for part in str(nhan).split('\n'):
            m = max(10, cw // 12)
            while len(part) > m:
                dong.append(part[:m]); part = part[m:]
            dong.append(part)
        for j, s in enumerate(dong[:2]):
            d.text((x + 4, y + ch + 4 + j * 28), s, font=f, fill=(235, 235, 235))
    sheet.save(out, quality=88)
    return out


def html(w, KH, ten='khung.html'):
    p = w / ten
    js = json.dumps(KH, ensure_ascii=False).replace('</', '<\\/')
    p.write_text(f'''<!doctype html><html><head><meta charset="utf-8"><link rel="stylesheet" href="{url(KHUNG / 'bds3d.css')}"></head>
<body><div id="stage"></div><script>window.KH={js};</script><script src="{url(KHUNG / 'bds3d.js')}"></script></body></html>''', encoding='utf-8')
    return p


def render(args_):
    return run([node(), SCRIPTS / 'render.mjs'] + [str(x) for x in args_])


def in_bao(bao):
    for m in bao.loi:
        loi(m)
    for m in bao.canh_bao:
        loi(m)
    if not bao.loi and not bao.canh_bao:
        loi('✅ không có lỗi')


# ---------------- quet ----------------
def cmd_quet(a):
    if a.video and a.audio:
        raise SystemExit('⛔ chỉ 1 trong --video hoặc --audio')
    if not a.video and not a.audio:
        if a.mo3d and a.res:
            return quet_mo_hinh(a)
        raise SystemExit('⛔ cần --video hoặc --audio (chỉ có ảnh dự án thì: quet --res <ảnh> --3d [--vi-tri …] để dựng mô hình trước)')
    nguon = Path(a.video or a.audio).resolve()
    if not nguon.exists():
        raise SystemExit(f'⛔ không thấy {nguon}')
    w = Path(a.work) if a.work else nguon.with_name(nguon.stem + '_bds3d_work')
    w.mkdir(parents=True, exist_ok=True)
    mh_cu = None                               # work lập từ ảnh trước (quet --3d không giọng): giữ mô hình đã dựng
    if (w / 'meta.json').exists() and doc_json(w / 'meta.json').get('kieu') == 'mo_hinh' and (w / 'ke_hoach.json').exists():
        mh_cu = doc_json(w / 'ke_hoach.json').get('mo_hinh_3d')
        if mh_cu:
            a.mo3d, a.lam_lai, a.nhan_lai = True, True, True
            loi('▶ work đã có mô hình 3D dựng từ ảnh — giữ nguyên mo_hinh_3d, lập kế hoạch mới theo giọng')
    info = probe(nguon)
    if not info['audio']:
        raise SystemExit(f'⛔ {nguon.name} không có tiếng — skill cần giọng đọc làm xương sống')
    loi(f'▶ nguồn: {nguon.name} ({info["duration"]:.2f} s)')
    # footage
    fo = {}
    if a.video:
        fo['video'] = {'file': str(nguon), 'loai': 'video', 'dai': info['duration'], 'w': info['w'], 'h': info['h']}
    for d in a.res or []:
        d = Path(d)
        if not d.exists():
            raise SystemExit(f'⛔ không thấy thư mục {d}')
        for f in sorted(d.iterdir()):
            ext = f.suffix.lower()
            if ext in VIDEO_EXT or ext in IMG_EXT:
                pi = probe(f)
                k = khoa(f.stem, fo)
                fo[k] = {'file': str(f.resolve()), 'loai': 'anh' if ext in IMG_EXT else 'video', 'dai': pi['duration'], 'w': pi['w'], 'h': pi['h']}
    if not fo and not a.mo3d:
        raise SystemExit('⛔ không có footage nào (video có hình / thư mục --res có clip, ảnh) — hoặc thêm --3d để dựng cảnh 3D')
    mo3d = None
    if mh_cu:
        mo3d = dict(mh_cu.get('vi_tri') or {})
    elif a.mo3d:
        mo3d = _mo3d(a)
    ghi_json(w / 'footage.json', fo)
    # giọng
    g16 = w / 'giong16.wav'
    run(['ffmpeg', '-v', 'error', '-y', '-i', nguon, '-vn', '-ac', '1', '-ar', '16000', '-c:a', 'pcm_s16le', g16])
    tk = [x.strip() for x in (a.tu_khoa or '').split(',') if x.strip()]
    if (w / 'tu.json').exists() and not a.nhan_lai:
        loi('▶ đã có tu.json — dùng lại (thêm --nhan-lai để nhận lời lại)')
        tu, cau = doc_json(w / 'tu.json')['tu'], doc_json(w / 'tu.json')['cau']
    else:
        loi('▶ nhận lời Whisper large-v3 (CPU, lần đầu tải ~3 GB)…')
        t0 = time.time()
        tu, cau = nhan_loi(g16, tk)
        ghi_json(w / 'tu.json', {'tu': tu, 'cau': cau})
        loi(f'  xong {len(tu)} từ / {time.time() - t0:.0f} s')
    if not tu:
        raise SystemExit('⛔ Whisper không nhận được lời nào')
    D = info['duration'] if a.video else min(info['duration'], tu[-1]['e'] + 1.4)
    D = round(max(D, tu[-1]['e'] + DUOI), 2)
    meta = {'nguon': str(nguon), 'kieu': 'video' if a.video else 'audio', 'thoi_luong': D, 'tu_khoa': tk}
    ghi_json(w / 'meta.json', meta)
    # loi_doc.txt
    L = [f'LỜI ĐỌC (Whisper large-v3) — {nguon.name} — thời lượng video ra {D:.2f} s', '']
    for c in cau:
        L.append(f"[{c['s']:.2f}–{c['e']:.2f}] {c['text']}")
        ws = [x for x in tu if c['s'] - .05 <= x['s'] <= c['e'] + .05]
        L.append('    ' + '  '.join(f"{x['w']}@{x['s']:.2f}" for x in ws))
    (w / 'loi_doc.txt').write_text('\n'.join(L), encoding='utf-8')
    # tờ footage
    tam = w / '_tn'
    shutil.rmtree(tam, ignore_errors=True); tam.mkdir()
    items = []
    for k, v in fo.items():
        if v['loai'] == 'anh':
            items.append((v['file'], f"{k} (ảnh {v['w']}x{v['h']})"))
            continue
        dur = v['dai']
        buoc = (1.0 if dur <= 40 else dur / 40) if k == 'video' else max(.5, dur / 8)
        run(['ffmpeg', '-v', 'error', '-y', '-i', v['file'], '-vf', f'fps=1/{buoc:.4f},scale=270:-2', '-q:v', '4', tam / f'{k}_%04d.jpg'])
        for i, f in enumerate(sorted(tam.glob(f'{k}_*.jpg'))):
            items.append((f, f'{k}\n@ {i * buoc:.1f}s'))
    tn = []
    for i in range(0, len(items), 48):
        p = w / ('tai_nguyen.jpg' if i == 0 else f'tai_nguyen_{i // 48 + 1}.jpg')
        luoi(items[i:i + 48], p, cot=8, tieu_de=f'FOOTAGE — {len(fo)} nguồn (khoá = tên dùng trong ke_hoach.json)')
        tn.append(p)
    # kế hoạch nháp
    khp = w / 'ke_hoach.json'
    if khp.exists() and not a.lam_lai:
        loi('▶ đã có ke_hoach.json — giữ nguyên (thêm --lam-lai để tạo nháp mới)')
    else:
        kh = KHM.tao_nhap(tu, {k: v['file'] for k, v in fo.items()}, D, mo3d=mo3d)
        if mh_cu:
            kh['mo_hinh_3d'] = mh_cu
        if a.nhac:
            kh['nhac']['file'] = str(Path(a.nhac).resolve())
        ghi_json(khp, kh)
    loi(f'''
✅ QUÉT XONG — work: {w}
   lời: {w / 'loi_doc.txt'}   ({len(tu)} từ, {len(cau)} câu)
   footage: {', '.join(fo)}  → mở {', '.join(p.name for p in tn)}
   kế hoạch NHÁP: {khp}
Bước tiếp (Claude): đọc loi_doc.txt + references/ke_hoach_schema.md + references/vi-du-video-mau.json,
   mở tai_nguyen*.jpg, sửa ke_hoach.json theo NGHĨA lời (6 phần), đặt CAN_CLAUDE_SUA=false → run.py kiem-kh --work "{w}"''')
    if mo3d is not None:
        loi(f'''
CẢNH 3D — dựng mô hình TỪ ẢNH DỰ ÁN (đọc references/mo_hinh_3d.md + vi-du-3d.json):
   1. MỞ MỌI ảnh dự án, đếm: số tháp, số tầng (vạch sàn), tỉ lệ rộng/cao, dải vườn treo, chân cột, khối đế, hồ bơi, màu kính / đế, kiểu mái
   2. viết lại mo_hinh_3d theo ảnh (xoá "_GHI_CHU" NHÁP), vi_tri {"ĐOÁN — hỏi người dùng" if not mo3d.get('chac') else "đã có"}
   3. run.py xem-3d --work "{w}" → MỞ mo_hinh_3d.jpg (ảnh dự án cạnh mô hình 6 góc), sửa tới khi giống
   4. viết canh_3d (camera bay, chú thích, chữ trong cảnh) theo lời → kiem-kh''')


def cmd_nhac(a):
    w = work_dir(a)
    f = Path(a.file).resolve()
    if not f.exists() or f.suffix.lower() not in AUDIO_EXT | VIDEO_EXT:
        raise SystemExit(f'⛔ file nhạc không hợp lệ: {f}')
    kh = doc_json(w / 'ke_hoach.json')
    kh.setdefault('nhac', {})['file'] = str(f)
    ghi_json(w / 'ke_hoach.json', kh)
    loi(f'✅ nhạc nền: {f.name} ({probe(f)["duration"]:.1f} s)')


# ---------------- kiem-kh ----------------
def _giai(w, trich):
    meta, kh, tu, fo = nap(w)
    kh.setdefault('thoi_luong', meta['thoi_luong'])
    bao = KHM.Bao()
    KH, sfx = KHM.giai(kh, tu, fo, w, bao, trich=trich)
    nh = (kh.get('nhac') or {}).get('file')
    if nh and not Path(nh).exists():
        bao.L(f'không thấy file nhạc {nh}')
    return meta, kh, tu, KH, sfx, bao


def _thoi_diem_kiem(KH):
    ts = set()
    for c in KH['caps']:
        ts.add(round(min(c['den'] - .05, max(w['t'] for r in c['dong'] for ch in r for w in ch['words']) + .3), 2))
    for s in KH['scenes']:
        ts.add(round((s['tu'] + s['den']) / 2, 2))
    return sorted(t for t in ts if 0 <= t < KH['dur'])


def _giao(a, b):
    x = max(0, min(a['x1'], b['x1']) - max(a['x0'], b['x0']))
    y = max(0, min(a['y1'], b['y1']) - max(a['y0'], b['y0']))
    return x * y


def cmd_kiem_kh(a, im_lang=False):
    w = work_dir(a)
    meta, kh, tu, KH, sfx, bao = _giai(w, trich=False)
    if KH is None:
        in_bao(bao); raise SystemExit(1)
    # đo bố cục chữ trong Chrome
    hp = html(w, KH, '_kiem.html')
    ts = _thoi_diem_kiem(KH)
    rp = w / '_bo_cuc.json'
    render(['--html', hp, '--report', rp, '--times', ','.join(f'{t:.2f}' for t in ts)])
    seen = set()
    for fr in doc_json(rp):
        hop = fr['hop']
        chu = [h for h in hop if h['loai'] == 'chu']
        khac = [h for h in hop if h['loai'] != 'chu']
        for c in chu:
            if c['x0'] < 24 or c['x1'] > W - 24 or c['y0'] < 30 or c['y1'] > H - 40:
                k = ('le', c['chu'])
                if k not in seen:
                    seen.add(k); bao.L(f"{fr['t']:.2f}s chữ '{c['chu']}' tràn mép khung ({c['x0']},{c['y0']})–({c['x1']},{c['y1']}) → bớt chữ / tách dòng")
            for o in khac:
                ar = _giao(c, o)
                if ar > 400:
                    k = ('de', c['chu'], o['loai'])
                    if k in seen:
                        continue
                    seen.add(k)
                    msg = f"{fr['t']:.2f}s chữ '{c['chu']}' đè {o['loai']} ({ar} px²)"
                    (bao.C if o['loai'] == 'dien_thoai' else bao.L)(msg + (' — hộp xoay nên đo rộng, soi ảnh duyệt' if o['loai'] == 'dien_thoai' else ''))
    if KH.get('canh3d') and not bao.loi:
        import mo_hinh_3d as M3D
        M3D.kiem_bo_cuc(kh, [(c['id'], c['t0'], c['t1']) for c in KH['canh3d']], tu, w, bao)
    ghi_json(w / 'kh_giai.json', KH)
    ghi_json(w / 'sfx.json', sfx)
    if not im_lang:
        loi(f'▶ {len(KH["scenes"])} cảnh · {len(KH["caps"])} cụm chữ · {len(KH["pills"])} viên kính · {len(KH["tiles"])} hàng ô · {len(sfx)} SFX')
        in_bao(bao)
        if bao.loi:
            raise SystemExit(f'⛔ còn {len(bao.loi)} lỗi — sửa ke_hoach.json rồi chạy lại kiem-kh')
        loi(f'✅ kế hoạch hợp lệ → run.py duyet --work "{w}"')
    return bao


# ---------------- duyet ----------------
def cmd_duyet(a):
    w = work_dir(a)
    bao = cmd_kiem_kh(a, im_lang=True)
    if bao.loi:
        in_bao(bao); raise SystemExit('⛔ kiem-kh còn lỗi')
    meta, kh, tu, KH, sfx, bao = _giai(w, trich=True)
    hp = html(w, KH)
    ts = []
    for s in KH['scenes']:
        d = s['den'] - s['tu']
        ts += [s['tu'] + d * .3, s['tu'] + d * .75] if d > 4 else [s['tu'] + d * .6]
    for c in KH['caps']:
        if not any(abs(c['den'] - .15 - t) < .8 for t in ts):
            ts.append(c['den'] - .15)
    ts = sorted(round(t, 2) for t in ts if 0 <= t < KH['dur'])
    if len(ts) > 24:
        ts = [ts[round(i * (len(ts) - 1) / 23)] for i in range(24)]
    od = w / '_duyet'
    shutil.rmtree(od, ignore_errors=True)
    loi(f'▶ chụp {len(ts)} khung duyệt…')
    render(['--html', hp, '--anh', od, '--times', ','.join(f'{t:.2f}' for t in ts)])
    def scene_at(t):
        for s in KH['scenes']:
            if s['tu'] <= t < s['den']:
                return s
        return KH['scenes'][-1]
    items = []
    for t in ts:
        s = scene_at(t)
        items.append((od / f'k_{t:.2f}.jpg', f"{t:.2f}s {s['id']} {s['loai']}{'·' + s['mau'] if s.get('mau') else ''}"))
    luoi(items, w / 'duyet.jpg', cot=6, tieu_de=f'DUYỆT bds_model_3d — {Path(meta["nguon"]).name} — {KH["dur"]:.1f} s')
    # bảng duyệt
    L = [f'BẢNG DUYỆT — {Path(meta["nguon"]).name} — {KH["dur"]:.2f} s — 1080x1920 30 fps', '', 'CẢNH:']
    for s in KH['scenes']:
        L.append(f"  {s['tu']:6.2f}–{s['den']:6.2f}  {s['id']:<5} {s['loai']}{'(' + s['mau'] + ')' if s.get('mau') else ''}{'  footage ' + s['shot'] if s.get('shot') else ''}")
    L += ['', 'CHỮ (dẫn trắng / KHOÁ vàng):']
    for c in KH['caps']:
        L.append(f"  {c['tu']:6.2f}–{c['den']:6.2f}  " + ' / '.join(' '.join(f"[{ch['k']}]{ch['text']}" for ch in r) for r in c['dong']))
    if KH['pills']:
        L += ['', 'VIÊN KÍNH (gạch = bác bỏ):'] + [f"  {p['tu']:.2f}–{p['den']:.2f}  {p['dan']} | {p['chu']}  gạch {p['gach']}" for p in KH['pills']]
    if KH['tiles']:
        L += ['', 'Ô KÍNH:'] + [f"  {T['tu']:.2f}–{T['den']:.2f}  " + ' · '.join(m['nhan'] for m in T['muc']) for T in KH['tiles']]
    if KH.get('canh3d'):
        mh = kh['mo_hinh_3d']; vt = mh.get('vi_tri') or {}
        L += ['', f"CẢNH 3D — vị trí {vt.get('lat')}, {vt.get('lon')} ({vt.get('ten', '')}){'' if vt.get('chac') else '  ⚠ ĐOÁN'}  → ảnh mô hình: mo_hinh_3d.jpg"]
        for i, T in enumerate(mh.get('thap') or []):
            L.append(f"  tháp {i + 1}: {T.get('tang')} tầng, {T.get('rong')}×{T.get('sau')} m, vườn treo tầng {T.get('vuon') or '—'}, chân cột {T.get('chan', 0)} m")
        for i, Dz in enumerate(mh.get('de') or []):
            L.append(f"  khối đế {i + 1}: {Dz.get('tang', '')} tầng {Dz.get('rong')}×{Dz.get('sau')} m{', hồ bơi' if Dz.get('ho_boi') else ''}")
        if mh.get('khoi'):
            L.append(f"  khối khác: {len(mh['khoi'])}")
        for c in KH['canh3d']:
            c3 = kh['canh_3d'][c['id']]
            L.append(f"  bay '{c['id']}' {c['t0']:.2f}–{c['t1']:.2f} s: {len(c3.get('cam') or [])} khoá camera · chú thích: "
                     + (', '.join(f"{o.get('chu')} / {o.get('phu', '')}" for o in c3.get('chu_thich') or []) or '—')
                     + f" · logo: {(c3.get('logo') or {}).get('chu', '—')} · địa danh: {', '.join(o.get('chu', '') for o in c3.get('dia_danh') or []) or '—'}")
            for g in c3.get('chu') or []:
                L.append(f"    chữ trong 3D {g.get('tu')}–{g.get('den')}: " + ' / '.join(' '.join(ch.get('t', '') for ch in d) for d in g.get('dong') or []))
    nh = (kh.get('nhac') or {}).get('file')
    L += ['', f"NHẠC: {Path(nh).name if nh else 'CHƯA CÓ — hỏi người dùng (D1)'}", f"SFX: {len(sfx)} tiếng — " + ', '.join(sorted({e['ten'] for e in sfx}))]
    doan = kh.get('doan') or []
    L += ['', 'MỤC ĐOÁN (hỏi người dùng):'] + ([f'  - {x}' for x in doan] or ['  (không)'])
    if bao.canh_bao:
        L += ['', 'CẢNH BÁO:'] + ['  ' + x for x in bao.canh_bao]
    (w / 'bang_duyet.txt').write_text('\n'.join(L), encoding='utf-8')
    loi('\n'.join(L))
    loi(f'''
✅ ẢNH DUYỆT: {w / 'duyet.jpg'}
CỔNG DUYỆT — Claude mở duyet.jpg soi từng khung rồi hỏi người dùng D1–D5 (SKILL.md), chờ trả lời → run.py dung --work "{w}"''')


# ---------------- dung ----------------
def cmd_dung(a):
    w = work_dir(a)
    bao = cmd_kiem_kh(a, im_lang=True)
    if bao.loi:
        in_bao(bao); raise SystemExit('⛔ kiem-kh còn lỗi')
    meta, kh, tu, KH, sfx, bao = _giai(w, trich=True)
    nguon = Path(meta['nguon'])
    out = Path(a.out) if a.out else nguon.with_name(nguon.stem + '_BDS3D.mp4')
    out = ten_moi(out)
    hp = html(w, KH)
    hinh = w / '_hinh.mp4'
    loi(f'▶ dựng hình {KH["dur"]:.2f} s ({round(KH["dur"] * FPS)} khung, {a.luong} luồng Chrome)…')
    t0 = time.time()
    render(['--html', hp, '--out', hinh, '--fps', FPS, '--tu', 0, '--den', f'{KH["dur"]:.4f}', '--luong', a.luong, '--crf', 17])
    loi(f'  hình xong {time.time() - t0:.0f} s')
    import am_thanh
    nh = (kh.get('nhac') or {})
    tieng = w / '_tieng.wav'
    am_thanh.tron(nguon, KH['dur'], tieng, tu=tu, nhac=nh.get('file'), sfx=sfx,
                  nhac_muc=float(nh.get('muc', -23)), nhac_dang=float(nh.get('dang', 16)), bao=loi)
    am_thanh.ghep(hinh, tieng, KH['dur'], out, bao=loi)
    loi(f'✅ RA: {out}')
    a.file = str(out)
    cmd_kiem(a)


# ---------------- kiem ----------------
def cmd_kiem(a):
    w = work_dir(a)
    f = Path(a.file) if a.file else None
    if not f:
        meta = doc_json(w / 'meta.json'); n = Path(meta['nguon'])
        ds = sorted(n.parent.glob(n.stem + '_BDS3D*.mp4'), key=lambda p: p.stat().st_mtime)
        if not ds:
            raise SystemExit('⛔ chưa có video ra — chạy dung trước')
        f = ds[-1]
    KH = doc_json(w / 'kh_giai.json')
    pi = probe(f)
    import am_thanh
    ld = am_thanh.do_lufs(f)
    I, tp = float(ld['input_i']), float(ld['input_tp'])
    ok = []
    ok.append(('khổ 1080x1920', (pi['w'], pi['h']) == (W, H), f"{pi['w']}x{pi['h']}"))
    ok.append(('30 fps', abs(pi['fps'] - FPS) < .05, f"{pi['fps']:.2f}"))
    ok.append(('thời lượng', abs(pi['duration'] - KH['dur']) < .15, f"{pi['duration']:.2f} s (kế hoạch {KH['dur']:.2f})"))
    ok.append(('−14 LUFS', abs(I - LUFS) <= .6, f'{I:.1f} LUFS'))
    ok.append(('đỉnh ≤ −1 dBTP', tp <= TP + .3, f'{tp:.1f} dBTP'))
    # soát khung
    ts = _thoi_diem_kiem(KH)
    if len(ts) > 24:
        ts = [ts[round(i * (len(ts) - 1) / 23)] for i in range(24)]
    od = w / '_soat'
    shutil.rmtree(od, ignore_errors=True); od.mkdir()
    items = []
    for t in ts:
        p = od / f'k_{t:.2f}.jpg'
        run(['ffmpeg', '-v', 'error', '-y', '-ss', f'{t:.3f}', '-i', f, '-frames:v', '1', '-q:v', '3', p])
        items.append((p, f'{t:.2f}s'))
    luoi(items, w / 'soat.jpg', cot=6, tieu_de=f'SOÁT FILE CUỐI — {f.name}')
    for ten, d, gt in ok:
        loi(f"{'✅' if d else '⛔'} {ten}: {gt}")
    loi(f'▶ soát khung: {w / "soat.jpg"} — Claude mở soi chính tả, chữ đè, khung đen/trắng')
    if not all(d for _, d, _ in ok):
        raise SystemExit('⛔ file cuối chưa đạt')


# ---------------- 3D: tìm toạ độ, xem mô hình ----------------
def cmd_tim(a):
    import mo_hinh_3d as M3D
    ds = M3D.tim(a.ten)
    if not ds:
        loi(f'⚠ OSM không ra "{a.ten}" — thử tên ngắn hơn / tên đường + phường, hoặc xin người dùng link Google Maps')
    for x in ds:
        loi(f"{x['osm']:<14} {x['loai']:<24} ({x['lat']:.5f}, {x['lon']:.5f})  {x['ten']}")


def cmd_xem_3d(a):
    w = work_dir(a)
    import mo_hinh_3d as M3D
    meta, kh, tu, fo = nap(w)
    bao = KHM.Bao()
    M3D.kiem_mo_hinh(kh.get('mo_hinh_3d'), bao, nhap_la_loi=False)
    if bao.loi:
        in_bao(bao); raise SystemExit('⛔ mo_hinh_3d còn lỗi')
    items = M3D.xem(kh, tu, w, bao)
    anh = [(k, Path(f)) for k, f in fo.items() if Path(f).suffix.lower() in IMG_EXT]
    ref = [(f, f'ẢNH DỰ ÁN {i + 1}: {k}') for i, (k, f) in enumerate(anh[:6])]
    # cặp "ảnh k – mô hình cùng góc" (mo_hinh_3d.goc_anh) xếp liền nhau ở cuối
    ga = [g for g in ((kh.get('mo_hinh_3d') or {}).get('goc_anh') or []) if isinstance(g, dict)]
    cap = []
    for g, it in zip(ga, items[6:]):
        k = int(g.get('anh', 1) or 1) - 1
        if 0 <= k < len(anh):
            cap.append((anh[k][1], f'ẢNH {k + 1}'))
        cap.append(it)
    luoi(ref + items[:6] + cap, w / 'mo_hinh_3d.jpg', cot=6,
         tieu_de='MÔ HÌNH 3D — ảnh dự án, mô hình 6 góc, cặp ẢNH – MÔ HÌNH CÙNG GÓC (so mặt đứng, màu, tỉ lệ)')
    in_bao(bao)
    loi(f'✅ {w / "mo_hinh_3d.jpg"} — Claude MỞ so với ảnh dự án, sửa mo_hinh_3d tới khi giống rồi mới viết camera / chữ')


def cmd_bay_thu(a):
    w = work_dir(a)
    import mo_hinh_3d as M3D
    meta, kh, tu, fo = nap(w)
    bao = KHM.Bao()
    M3D.kiem_mo_hinh(kh.get('mo_hinh_3d'), bao, work=w)
    if bao.loi:
        in_bao(bao); raise SystemExit('⛔ mo_hinh_3d còn lỗi')
    out = ten_moi(Path(a.out).resolve() if a.out else w / 'bay_thu.mp4')
    loi(f'▶ bay thử quanh mô hình {a.giay:g} s (câm)…')
    if not M3D.bay_thu(kh, w, bao, out, giay=a.giay, luong=a.luong):
        in_bao(bao); raise SystemExit('⛔ camera bay_thu còn lỗi')
    in_bao(bao)
    loi(f'✅ {out} — mô hình trong video (chưa giọng / chữ). Có giọng thì: run.py quet --audio "<giọng>" --res "<ảnh>" --3d --work "{w}" (giữ mô hình)')


def _mo3d(a):
    """--vi-tri / --dia-chi → {'lat','lon','ten','chac'} cho nháp mô hình 3D."""
    mo3d = {'ten': a.dia_chi or '', 'chac': False}
    if a.vi_tri:
        so = re.findall(r'-?\d+(?:\.\d+)?', a.vi_tri)
        if len(so) < 2:
            raise SystemExit(f'⛔ --vi-tri "{a.vi_tri}" không đọc được (dạng "10.7238,106.7421")')
        mo3d.update(lat=float(so[0]), lon=float(so[1]), chac=True)
    elif a.dia_chi:
        import mo_hinh_3d as M3D
        ds = M3D.tim(a.dia_chi)
        if ds:
            mo3d.update(lat=ds[0]['lat'], lon=ds[0]['lon'])
            loi(f"▶ vị trí ĐOÁN theo OSM: {ds[0]['ten']} ({ds[0]['lat']:.5f}, {ds[0]['lon']:.5f}) — Claude soát, chắc thì đặt vi_tri.chac=true")
        else:
            loi(f'⚠ OSM không ra "{a.dia_chi}" — Claude tự tìm (run.py tim) rồi điền mo_hinh_3d.vi_tri')
    return mo3d


def quet_mo_hinh(a):
    """CHỈ CÓ ẢNH DỰ ÁN (chưa có giọng): lập work để dựng mô hình 3D trước (xem-3d, bay-thu).
    Giọng đưa sau: quet --audio … --res … --3d --work <cùng work> — mô hình đã dựng được giữ nguyên."""
    d0 = Path(a.res[0]).resolve()
    w = Path(a.work) if a.work else d0.with_name(d0.name + '_bds3d_work')
    w.mkdir(parents=True, exist_ok=True)
    fo = {}
    for d in a.res:
        d = Path(d)
        if not d.exists():
            raise SystemExit(f'⛔ không thấy thư mục {d}')
        for f in sorted(d.iterdir()):
            if f.suffix.lower() in IMG_EXT or f.suffix.lower() in VIDEO_EXT:
                pi = probe(f)
                fo[khoa(f.stem, fo)] = {'file': str(f.resolve()), 'loai': 'anh' if f.suffix.lower() in IMG_EXT else 'video',
                                        'dai': pi['duration'], 'w': pi['w'], 'h': pi['h']}
    if not any(v['loai'] == 'anh' for v in fo.values()):
        raise SystemExit('⛔ thư mục --res không có ảnh dự án (jpg / png / webp) để dựng mô hình')
    mo3d = _mo3d(a)
    ghi_json(w / 'footage.json', fo)
    ghi_json(w / 'meta.json', {'nguon': None, 'kieu': 'mo_hinh', 'thoi_luong': 0, 'tu_khoa': []})
    if not (w / 'tu.json').exists():
        ghi_json(w / 'tu.json', {'tu': [], 'cau': []})
    luoi([(v['file'], f"{k} (ảnh {v['w']}x{v['h']})") for k, v in fo.items() if v['loai'] == 'anh'][:48], w / 'tai_nguyen.jpg', cot=4, cw=420, ch=300,
         tieu_de=f'ẢNH DỰ ÁN — {len(fo)} nguồn (dựng mô hình 3D theo các ảnh này)')
    khp = w / 'ke_hoach.json'
    if khp.exists() and doc_json(khp).get('mo_hinh_3d') and not a.lam_lai:
        loi('▶ đã có mo_hinh_3d trong ke_hoach.json — giữ nguyên (thêm --lam-lai để tạo nháp mới)')
    else:
        nh = KHM.tao_nhap([], {}, 10.0, mo3d=mo3d)
        ghi_json(khp, {'CAN_CLAUDE_SUA': True, 'mo_hinh_3d': nh['mo_hinh_3d'], 'canh_3d': {}, 'doan': nh.get('doan', [])})
    loi(f'''
✅ WORK MÔ HÌNH (chưa có giọng): {w}
   ảnh dự án: {w / 'tai_nguyen.jpg'}   kế hoạch: {khp}
CẢNH 3D — dựng mô hình TỪ ẢNH DỰ ÁN (đọc references/mo_hinh_3d.md + vi-du-3d.json):
   1. MỞ MỌI ảnh dự án, đếm: số tháp, số tầng (vạch sàn), tỉ lệ rộng/cao, dải vườn treo, chân cột, khối đế, hồ bơi, màu mặt đứng từng tháp, kiểu mái
   2. soi ảnh vệ tinh lô đất (dự án đang xây thì đo vị trí từng tháp trên ảnh), viết lại mo_hinh_3d (xoá "_GHI_CHU" NHÁP),
      vi_tri {"ĐOÁN — hỏi người dùng" if not mo3d.get('chac') else "đã có"}
   3. run.py xem-3d --work "{w}" → MỞ mo_hinh_3d.jpg, sửa tới khi giống
   4. run.py bay-thu --work "{w}" → video câm bay quanh mô hình (gửi người dùng xem trước)
   5. có giọng: run.py quet --audio "<giọng>" --res "{d0}" --3d --work "{w}" (mô hình giữ nguyên)''')


# ---------------- nns ----------------
def cmd_luoi_anh(a):
    import mat_anh
    od = Path(a.work) / 'mat_anh' if a.work else Path(a.anh).parent
    ra = od / f'luoi_{Path(a.anh).stem[:24]}_{a.vung.replace(",", "_")}.jpg'
    mat_anh.luoi_anh(a.anh, a.vung, ra, to=a.to)


def cmd_mat_anh(a):
    import mat_anh
    mat_anh.lam(work_dir(a), a.anh, a.goc, a.id, tang=a.tang, rong=a.rong, sang=a.sang, chinh=not a.giu_goc)


def cmd_nns(a):
    f = Path(a.file).resolve()
    if not f.exists():
        raise SystemExit(f'⛔ không thấy {f}')
    out = ten_moi(f.with_name(f.stem + '_NNS_gui_khach.mp4'))
    fnt = Path('C:/Windows/Fonts/ariblk.ttf')
    if not fnt.exists():
        fnt = ASSETS / 'fonts' / 'BeVietnamPro-ExtraBold.ttf'
    ff = str(fnt).replace('\\', '/').replace(':', '\\:')

    def dt(sz, al, px, py, ph):
        x = f"(w-tw)*abs(mod(t/{px}+{ph}\\,2)-1)"
        y = f"(h-th)*abs(mod(t/{py}+{ph * .7:.2f}\\,2)-1)"
        return (f"drawtext=fontfile='{ff}':text='NNS':fontsize={sz}:fontcolor=white@{al}:borderw=3:bordercolor=black@{al * .5:.2f}"
                f":x={x}:y={y}")
    vf = dt(170, .30, 7.3, 11.9, .3) + ',' + dt(120, .24, 9.1, 8.3, 1.1)
    run(['ffmpeg', '-v', 'error', '-y', '-i', f, '-vf', vf, '-c:v', 'libx264', '-crf', '20', '-preset', 'medium', '-pix_fmt', 'yuv420p',
         '-c:a', 'copy', '-movflags', '+faststart', out])
    loi(f'✅ bản gửi khách (NNS mờ chạy): {out}\n   bản sạch giữ nguyên: {f}')


def main():
    ap = argparse.ArgumentParser(description='bds_model_3d')
    sp = ap.add_subparsers(dest='lenh', required=True)
    q = sp.add_parser('quet')
    q.add_argument('--video'); q.add_argument('--audio'); q.add_argument('--res', action='append')
    q.add_argument('--nhac'); q.add_argument('--tu-khoa', dest='tu_khoa'); q.add_argument('--work')
    q.add_argument('--nhan-lai', dest='nhan_lai', action='store_true'); q.add_argument('--lam-lai', dest='lam_lai', action='store_true')
    q.add_argument('--3d', dest='mo3d', action='store_true'); q.add_argument('--vi-tri', dest='vi_tri'); q.add_argument('--dia-chi', dest='dia_chi')
    t = sp.add_parser('tim'); t.add_argument('ten')
    x = sp.add_parser('xem-3d'); x.add_argument('--work', required=True)
    n = sp.add_parser('nhac'); n.add_argument('--work', required=True); n.add_argument('--file', required=True)
    for ten in ('kiem-kh', 'duyet'):
        s = sp.add_parser(ten); s.add_argument('--work', required=True)
    d = sp.add_parser('dung'); d.add_argument('--work', required=True); d.add_argument('--out'); d.add_argument('--luong', type=int, default=3)
    d.add_argument('--file')
    k = sp.add_parser('kiem'); k.add_argument('--work', required=True); k.add_argument('--file')
    s = sp.add_parser('nns'); s.add_argument('--file', required=True)
    b = sp.add_parser('bay-thu'); b.add_argument('--work', required=True); b.add_argument('--out')
    b.add_argument('--giay', type=float, default=12.0); b.add_argument('--luong', type=int, default=3)
    la = sp.add_parser('luoi-anh'); la.add_argument('--anh', required=True); la.add_argument('--vung', required=True)
    la.add_argument('--to', type=float, default=2.0); la.add_argument('--work')
    ma = sp.add_parser('mat-anh'); ma.add_argument('--work', required=True); ma.add_argument('--anh', required=True)
    ma.add_argument('--goc', required=True); ma.add_argument('--id', required=True); ma.add_argument('--tang', type=int, default=0)
    ma.add_argument('--rong', type=int); ma.add_argument('--sang', type=float, default=1.0); ma.add_argument('--giu-goc', action='store_true')
    a = ap.parse_args()
    {'quet': cmd_quet, 'nhac': cmd_nhac, 'kiem-kh': cmd_kiem_kh, 'duyet': cmd_duyet, 'dung': cmd_dung, 'kiem': cmd_kiem, 'nns': cmd_nns,
     'tim': cmd_tim, 'xem-3d': cmd_xem_3d, 'bay-thu': cmd_bay_thu, 'luoi-anh': cmd_luoi_anh, 'mat-anh': cmd_mat_anh}[a.lenh](a)


if __name__ == '__main__':
    main()
