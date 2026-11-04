# -*- coding: utf-8 -*-
"""Cổng lệnh của skill ban-do-quy-hoach-bds-ve-tinh (audio → video bản đồ vệ tinh quy hoạch / BĐS 9:16).

    python -I -X utf8 scripts/run.py quet --audio <file> [--res <thư mục>] [--kenh kenh.json]
    python -I -X utf8 scripts/run.py dia-diem --work <dir>          # cần mạng: Photon + OSM API
    python -I -X utf8 scripts/run.py kiem-kh --work <dir>           # kiểm ke_hoach.json (số liệu phải có trong lời …)
    python -I -X utf8 scripts/run.py duyet --work <dir>             # cần mạng: ảnh xem trước từng cảnh → duyet.jpg
    python -I -X utf8 scripts/run.py dung --work <dir> [--out …]    # cần mạng (ô ảnh chưa cache)
    python -I -X utf8 scripts/run.py kiem --work <dir>              # tự kiểm trên file cuối → soat_*.jpg
    python -I -X utf8 scripts/run.py tai-lieu xac-minh --url … --so … --tu … --out …
"""
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import chung as C

HERE = os.path.dirname(os.path.abspath(__file__))
SO_RE = re.compile(r"\d{1,3}(?:[.,]\d{3})+|\d+(?:[.,]\d+)?")


def goi(script, args):
    r = subprocess.run([sys.executable, "-X", "utf8", os.path.join(HERE, script)] + list(args))
    return r.returncode


def lay_arg(args, ten, mac_dinh=None):
    if ten in args:
        i = args.index(ten)
        if i + 1 < len(args):
            return args[i + 1]
    return mac_dinh


# ---------------------------------------------------------------- kiểm kế hoạch

def so_trong_loi(work):
    import dung
    src = C.jload(os.path.join(work, "loi_doc.json"))
    words = dung.gop_so([dict(w) for w in src["words"] if w.get("w")])
    text = " ".join(w["w"] for w in words)
    return {C.chuan_hoa_so(m.group(0)) for m in SO_RE.finditer(text)}, words


def chu_tren_hinh(plan):
    """mọi chữ Claude đặt lên hình (hook, đầu đề, nhãn, thước) → [(chỗ, chữ)]"""
    out = []
    hk = plan.get("hook") or {}
    for k in ("dong1", "dong2", "dong3"):
        if hk.get(k):
            out.append(("hook." + k, hk[k]))
    for i, c in enumerate(plan.get("canh", [])):
        tag = "canh[%d] %s" % (i, c.get("loai"))
        for k in ("tieu_de", "phu"):
            if c.get(k):
                out.append((tag + "." + k, c[k]))
        for j, d in enumerate(c.get("dau_de") or []):
            for k in ("tieu_de", "phu"):
                if d.get(k):
                    out.append((tag + ".dau_de[%d].%s" % (j, k), d[k]))
        for j, d in enumerate(c.get("doan") or []):
            for k in ("nhan", "phu", "nhan_dau", "nhan_cuoi", "huy_hieu"):
                if d.get(k):
                    out.append((tag + ".doan[%d].%s" % (j, k), d[k]))
        for j, n in enumerate(c.get("nhan_manh") or []):
            for k in ("text", "phu"):
                if n.get(k):
                    out.append((tag + ".nhan_manh[%d].%s" % (j, k), n[k]))
        for k in ("phu_nhan", "dinh_vi_ten"):
            if c.get(k):
                out.append((tag + "." + k, c[k]))
        if isinstance(c.get("ten_tuyen"), str):
            out.append((tag + ".ten_tuyen", c["ten_tuyen"]))
        for j, x in enumerate(c.get("dong") or []):
            out.append((tag + ".dong[%d]" % j, x))
        if isinstance(c.get("nhan"), str):
            out.append((tag + ".nhan", c["nhan"]))
        elif isinstance(c.get("nhan"), dict):
            for k, v in c["nhan"].items():
                out.append((tag + ".nhan." + k, v))
        elif isinstance(c.get("nhan"), list):
            for j, n in enumerate(c["nhan"]):
                if n.get("text"):
                    out.append((tag + ".nhan[%d]" % j, n["text"]))
        if (c.get("thuoc") or {}).get("nhan"):
            out.append((tag + ".thuoc", c["thuoc"]["nhan"]))
    for i, t in enumerate(plan.get("the_tai_lieu", [])):
        if t.get("tieu_de"):
            out.append(("the_tai_lieu[%d].tieu_de" % i, t["tieu_de"]))
    return out


KHOA_DIA_DIEM = ("tuyen", "tu_diem", "den_diem", "diem", "a", "b")


def kiem_ke_hoach(work, in_ra=True):
    plan = C.doc_ke_hoach(work)
    dd = plan.get("dia_diem") or {}
    dur = C.probe(plan["audio"])["duration"] + float(plan.get("cai_dat", {}).get("duoi", C.DUOI_SAU_TIENG_CUOI))
    loi, canh_bao = [], []
    so_loi, words = so_trong_loi(work)
    # 1. số liệu trên hình phải có trong lời (không bịa)
    for cho, txt in chu_tren_hinh(plan):
        for m in SO_RE.finditer(txt):
            s = C.chuan_hoa_so(m.group(0))
            if s not in so_loi:
                loi.append("%s: số '%s' trong \"%s\" KHÔNG có trong lời đọc — bỏ hoặc sửa (không bịa số)" % (cho, m.group(0), txt))
    # 2. cảnh phủ kín 0 → hết
    canh = sorted(plan.get("canh", []), key=lambda x: float(x["tu"]))
    if not canh:
        loi.append("chưa có cảnh nào")
    else:
        if float(canh[0]["tu"]) > 0.05:
            loi.append("cảnh đầu bắt đầu ở %.2f s (phải 0)" % float(canh[0]["tu"]))
        for i, c in enumerate(canh):
            den = c.get("den")
            nxt = float(canh[i + 1]["tu"]) if i + 1 < len(canh) else dur
            if den is not None and float(den) < nxt - 0.05:
                loi.append("hở hình %.2f–%.2f sau cảnh %d" % (float(den), nxt, i))
            d = (float(den) if den is not None else nxt) - float(c["tu"])
            if d < 1.5 and c.get("loai") != "cta":
                canh_bao.append("cảnh %d (%s) chỉ %.2f s — dưới 1,5 s dễ giật" % (i, c.get("loai"), d))
            vys = [c.get("vung_y")] + [d_.get("vung_y") for d_ in (c.get("doan") or [])]
            for vy in vys:
                if vy and float(vy[1]) > 0.72:
                    loi.append("cảnh %d: vung_y đáy %.2f > 0,72 — nhãn/đoạn sẽ đè dải sub (y ≥ 1400)" % (i, float(vy[1])))
            for k in KHOA_DIA_DIEM:
                v = c.get(k)
                if isinstance(v, str) and v not in dd:
                    loi.append("cảnh %d: '%s' = %s chưa khai trong dia_diem" % (i, k, v))
            for v in c.get("vung", []) or []:
                if v not in dd:
                    loi.append("cảnh %d: vùng %s chưa khai trong dia_diem" % (i, v))
            if isinstance(c.get("dinh_vi"), str) and c["dinh_vi"] not in dd:
                loi.append("cảnh %d: dinh_vi = %s chưa khai trong dia_diem" % (i, c["dinh_vi"]))
            for j, n in enumerate(c.get("nhan_manh") or []):
                if n.get("kieu") not in ("song", "ghim", "chu_thich", "huy_hieu", "ngam", "nhan"):
                    loi.append("cảnh %d: nhan_manh[%d].kieu = %s (có: song, ghim, chu_thich, huy_hieu, ngam, nhan)"
                               % (i, j, n.get("kieu")))
                if isinstance(n.get("diem"), str) and n["diem"] not in dd:
                    loi.append("cảnh %d: nhan_manh[%d].diem = %s chưa khai trong dia_diem" % (i, j, n["diem"]))
                if n.get("diem") is None and not n.get("man_hinh"):
                    loi.append("cảnh %d: nhan_manh[%d] thiếu diem / man_hinh" % (i, j))
            for d_ in c.get("doan", []) or []:
                for k in ("tu_diem", "den_diem"):
                    if isinstance(d_.get(k), str) and d_[k] not in dd:
                        loi.append("cảnh %d: đoạn %s = %s chưa khai trong dia_diem" % (i, k, d_[k]))
    for k in (plan.get("cai_dat") or {}).get("dinh_vi_doan") or []:
        if isinstance(k, str) and k not in dd:
            loi.append("cai_dat.dinh_vi_doan: %s chưa khai trong dia_diem" % k)
    # 3. địa điểm đã giải
    for k in dd:
        if not os.path.isfile(os.path.join(work, "dia_ly", k + ".json")):
            loi.append("địa điểm %s chưa có dia_ly/%s.json — chạy `run.py dia-diem`" % (k, k))
    # 4. thẻ tài liệu: chỉ khi đã xác minh hoặc do người dùng đưa
    for i, t in enumerate(plan.get("the_tai_lieu", [])):
        if t.get("nguon_user"):
            if not plan.get("res"):
                loi.append("the_tai_lieu[%d] ghi nguon_user nhưng không có thư mục Resources" % i)
            continue
        xm = t.get("xac_minh")
        p = os.path.join(work, xm) if xm and not os.path.isabs(xm) else xm
        if not p or not os.path.isfile(p):
            loi.append("the_tai_lieu[%d]: thiếu xac_minh.json (tài liệu tự tìm PHẢI qua `tai_lieu.py xac-minh`)" % i)
        elif not C.jload(p).get("ok"):
            loi.append("the_tai_lieu[%d]: xac_minh.json KHÔNG ĐẠT — không được làm thẻ" % i)
    # 5. hook
    hk = plan.get("hook")
    if hk and float(hk.get("den", 0)) <= float(hk.get("tu", 0)):
        loi.append("hook: den ≤ tu")
    if in_ra:
        for x in canh_bao:
            print("⚠ " + x)
        for x in loi:
            print("⛔ " + x)
        if not loi:
            print("✅ ke_hoach.json đạt: %d cảnh, %d địa điểm, %d thẻ tài liệu, %d chữ trên hình (số liệu đều có trong lời)"
                  % (len(canh), len(dd), len(plan.get("the_tai_lieu", [])), len(chu_tren_hinh(plan))))
    return loi, plan, words


# ---------------------------------------------------------------- duyệt

def duyet(work):
    loi, plan, words = kiem_ke_hoach(work)
    if loi:
        C.die("sửa hết ⛔ rồi duyệt lại")
    from PIL import Image, ImageDraw
    canh = sorted(plan["canh"], key=lambda x: float(x["tu"]))
    dur = C.probe(plan["audio"])["duration"] + float(plan.get("cai_dat", {}).get("duoi", C.DUOI_SAU_TIENG_CUOI))
    moc = []
    for i, c in enumerate(canh):
        den = float(c["den"]) if c.get("den") is not None else (float(canh[i + 1]["tu"]) if i + 1 < len(canh) else dur)
        tu = float(c["tu"])
        loi_c = " ".join(w["w"] for w in words if tu - 0.05 <= w["start"] < den)
        if c.get("doan"):
            for d in c["doan"]:
                t_d = float(d["t"]) + float(d.get("dai_ve", 2.0)) + 0.4
                if d.get("huy_hieu_tu") is not None:
                    t_d = max(t_d, float(d["huy_hieu_tu"]) + 0.5)
                moc.append((min(den - 0.3, t_d), i, c, loi_c))
            moc.append((tu + 0.6, i, c, loi_c))
        else:
            moc.append((tu + min(den - tu - 0.3, max(0.8, (den - tu) * 0.6)), i, c, loi_c))
    moc.sort(key=lambda x: x[0])
    ts = ",".join("%.2f" % m[0] for m in moc)
    rc = goi("dung.py", ["--work", work, "--xem-truoc", ts])
    if rc != 0:
        C.die("xem trước lỗi")
    thumbs = []
    f_ = C.font("bold", 17)
    for t, i, c, loi_c in moc:
        p = os.path.join(work, "xem_truoc_%06.2f.jpg" % float("%.2f" % t))
        if not os.path.isfile(p):
            continue
        im = Image.new("RGB", (360, 640 + 50), (0, 0, 0))
        im.paste(Image.open(p).convert("RGB").resize((360, 640), Image.LANCZOS), (0, 0))
        d = ImageDraw.Draw(im)
        d.text((6, 644), "#%d %s · %.2f s" % (i, c.get("loai"), t), font=f_, fill=(255, 230, 120))
        d.text((6, 668), loi_c[:46], font=C.font("semi", 13), fill=(255, 255, 255))
        thumbs.append(im)
    cot = 4
    hang = (len(thumbs) + cot - 1) // cot
    sheet = Image.new("RGB", (cot * 366 + 6, hang * 696 + 6), (30, 30, 30))
    for k, im in enumerate(thumbs):
        sheet.paste(im, (6 + (k % cot) * 366, 6 + (k // cot) * 696))
    out = os.path.join(work, "duyet.jpg")
    sheet.save(out, quality=88)
    print("\n▶ BẢNG CẢNH (lời → hình):")
    for i, c in enumerate(canh):
        den = c.get("den") if c.get("den") is not None else (canh[i + 1]["tu"] if i + 1 < len(canh) else round(dur, 2))
        dau = c.get("tieu_de") or "; ".join(x.get("tieu_de", "") for x in (c.get("dau_de") or [])) or \
            "; ".join(x.get("nhan", "") for x in (c.get("doan") or []))
        dia = c.get("tuyen") or c.get("diem") or ",".join(c.get("vung", []) or []) or ""
        print("   #%-2d %6.2f–%6.2f  %-11s %-14s %s" % (i, float(c["tu"]), float(den), c.get("loai"), str(dia)[:14], dau[:70]))
    print("✅ duyet.jpg: %s (%d khung) — Claude MỞ XEM rồi mới hỏi người dùng ở cổng duyệt" % (out, len(thumbs)))


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(0)
    cmd, args = sys.argv[1], sys.argv[2:]
    if cmd == "quet":
        sys.exit(goi("quet.py", args))
    if cmd == "tai-lieu":
        sys.exit(goi("tai_lieu.py", args))
    if cmd == "tim":
        sys.exit(goi("dia_ly.py", ["tim"] + args))
    work = lay_arg(args, "--work")
    if not work:
        C.die("thiếu --work <thư mục làm việc>")
    work = os.path.abspath(work)
    if cmd == "dia-diem":
        import dia_ly as G
        kh = os.path.join(work, "ke_hoach.json")
        raw = C.jload(kh)
        bao = G.giai_quyet(raw, work)
        C.jsave(kh, raw)
        n = sum(1 for b in bao if b[2].startswith("⛔"))
        if n:
            C.die("%d địa điểm chưa giải được — sửa ten / osm / lat,lon rồi chạy lại" % n)
        print("✅ %d địa điểm → %s" % (len(bao), os.path.join(work, "dia_ly")))
    elif cmd == "kiem-kh":
        loi, _, _ = kiem_ke_hoach(work)
        sys.exit(1 if loi else 0)
    elif cmd == "duyet":
        duyet(work)
    elif cmd == "dung":
        loi, _, _ = kiem_ke_hoach(work)
        if loi:
            C.die("ke_hoach.json còn ⛔ — không dựng")
        sys.exit(goi("dung.py", args))
    elif cmd == "kiem":
        sys.exit(goi("kiem.py", args))
    else:
        print(__doc__)
        C.die("lệnh lạ: " + cmd)


if __name__ == "__main__":
    main()
