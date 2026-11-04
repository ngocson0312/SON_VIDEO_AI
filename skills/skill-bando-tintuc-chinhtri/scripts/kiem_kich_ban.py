# -*- coding: utf-8 -*-
"""Bước 2b: kiểm work/kich_ban.json trước khi tải tài nguyên / dựng. ⛔ = phải sửa, ⚠ = nên xem lại.

python -I scripts/kiem_kich_ban.py --work <work>
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import chung as C

LOAI_HOP_LE = {"to_nuoc", "nhan", "chu_neon", "ghim", "vat_the", "nguoi", "anh", "so", "phong", "no", "vo_vun",
               "radar", "tach", "tuyen", "lan", "cta"}
BAT_BUOC = {
    "to_nuoc": ["nuoc"], "nhan": ["tai", "chu"], "chu_neon": ["tai", "chu"], "ghim": ["tai"],
    "vat_the": ["tai", "vat"], "nguoi": ["ten"], "anh": [], "so": ["chu"], "phong": ["tu", "toi"],
    "no": ["tai"], "vo_vun": ["nuoc"], "radar": ["tai"], "tach": ["tai"], "tuyen": ["tu", "toi"], "lan": ["tai"], "cta": [],
}
LON = {"no", "vo_vun", "phong", "tach"}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--work", required=True)
    a = ap.parse_args()
    work = os.path.abspath(a.work)
    f = os.path.join(work, "kich_ban.json")
    if not os.path.exists(f):
        C.die("không có " + f)
    try:
        kb = C.doc_json(f)
    except Exception as exc:
        C.die("kich_ban.json không phải JSON hợp lệ: %s" % exc)
    loi = C.doc_json(os.path.join(work, "loi_doc.json")) if os.path.exists(os.path.join(work, "loi_doc.json")) else None
    T = (float(loi["thoi_luong"]) + C.DUOI_SAU_TIENG_CUOI) if loi else float(kb.get("thoi_luong") or 0)
    tt = {}
    if os.path.exists(os.path.join(work, "thuc_the.json")):
        tt = C.doc_json(os.path.join(work, "thuc_the.json"))
    sai, canh = [], []
    nhip = kb.get("nhip")
    if not isinstance(nhip, list) or not nhip:
        C.die("kịch bản không có danh sách 'nhip'")
    nhip = sorted(nhip, key=lambda n: float(n.get("t", 0)))
    refs = set()
    print("%-5s %-7s %-28s %-5s %s" % ("id", "t", "camera", "ĐT", "lời"))
    so_no = []
    for i, n in enumerate(nhip):
        t = float(n.get("t", 0))
        t_het = float(nhip[i + 1]["t"]) if i + 1 < len(nhip) else T
        cams = n.get("camera") or {}
        cams = cams if isinstance(cams, list) else [cams]
        cam = cams[0] if cams else {}
        for ck in cams[1:]:
            if ck.get("luc") is None:
                sai.append("nhịp %s: camera dạng danh sách thì MỖI điểm dừng phải có 'luc' (giây camera ĐẾN NƠI)" % n.get("id"))
            if ck.get("rong_km") is not None and not (30 <= float(ck["rong_km"]) <= 30000):
                sai.append("nhịp %s: rong_km=%s ngoài khoảng 30–30000" % (n.get("id"), ck["rong_km"]))
            if ck.get("toi") is not None and not isinstance(ck["toi"], list):
                refs.add(str(ck["toi"]))
        dts = n.get("dong_tac") or []
        if T and t > T:
            sai.append("nhịp %s: t=%.2f vượt thời lượng %.2f" % (n.get("id"), t, T))
        if t_het - t < 1.2 and i + 1 < len(nhip):
            canh.append("nhịp %s chỉ dài %.1f s — cảnh đổi dồn dập, nên gộp" % (n.get("id"), t_het - t))
        if not cam and i == 0:
            sai.append("nhịp đầu tiên phải có camera")
        if cam and cam.get("toi") is not None:
            refs.add(str(cam["toi"]) if not isinstance(cam["toi"], list) else "")
        if cam and cam.get("rong_km") is not None and not (30 <= float(cam["rong_km"]) <= 30000):
            sai.append("nhịp %s: rong_km=%s ngoài khoảng 30–30000" % (n.get("id"), cam["rong_km"]))
        lon_trong_nhip = 0
        for d in dts:
            loai = d.get("loai")
            if loai not in LOAI_HOP_LE:
                sai.append("nhịp %s: loại động tác lạ %r (bộ chuẩn: %s)" % (n.get("id"), loai, ", ".join(sorted(LOAI_HOP_LE))))
                continue
            for k in BAT_BUOC[loai]:
                if d.get(k) in (None, ""):
                    sai.append("nhịp %s: %s thiếu trường '%s'" % (n.get("id"), loai, k))
            if (loai in ("nhan", "chu_neon", "ghim") and not d.get("giu_lau") and d.get("luc") is not None
                    and d.get("den") is not None and float(d["den"]) - float(d["luc"]) > 3.5):
                sai.append("nhịp %s: %s '%s' hiện %.1f s — quá lâu, chữ chỉ ở ≤ 3,5 s sau khi được nhắc (sửa 'den', hoặc thêm giu_lau:true nếu thật sự cần)"
                           % (n.get("id"), loai, d.get("chu") or d.get("tai"), float(d["den"]) - float(d["luc"])))
            luc = d.get("luc")
            if luc is None:
                sai.append("nhịp %s: %s thiếu 'luc' (giây tuyệt đối)" % (n.get("id"), loai))
            else:
                luc = float(luc)
                if T and luc > T + 0.01:
                    sai.append("nhịp %s: %s luc=%.2f vượt thời lượng" % (n.get("id"), loai, luc))
                if luc < t - 0.5 or luc > t_het + 0.5:
                    canh.append("nhịp %s: %s luc=%.2f nằm ngoài khoảng nhịp [%.2f, %.2f]" % (n.get("id"), loai, luc, t, t_het))
                if d.get("den") is not None and float(d["den"]) <= luc:
                    sai.append("nhịp %s: %s den=%.2f phải > luc" % (n.get("id"), loai, float(d["den"])))
                if loai == "no":
                    so_no.append(luc)
            for k in ("tai", "nuoc", "tu", "toi", "den_diem"):
                v = d.get(k)
                if isinstance(v, str):
                    refs.add(v)
            if loai in LON:
                lon_trong_nhip += 1
        if lon_trong_nhip >= 3:
            canh.append("nhịp %s có %d hiệu ứng lớn (phóng/nổ/vỡ/tách) — nên tối đa 2" % (n.get("id"), lon_trong_nhip))
        if not dts and not cam:
            canh.append("nhịp %s không có camera lẫn động tác" % n.get("id"))
        print("%-5s %-7.2f %-28s %-5d %s" % (n.get("id", "?"), t, (str(cam.get("toi")) + " " + str(cam.get("rong_km", "")) + "km")[:28],
                                             len(dts), str(n.get("loi", ""))[:60]))
    so_no.sort()
    for x, y in zip(so_no, so_no[1:]):
        if y - x < 1.0:
            canh.append("2 vụ nổ cách nhau %.1f s (%.2f, %.2f) — dồn dập" % (y - x, x, y))
    # lời chưa có nhịp
    if loi:
        for c in loi["cau"]:
            if not any(float(n.get("t", 0)) - 0.6 <= c["s"] < (float(nhip[i + 1]["t"]) if i + 1 < len(nhip) else T) for i, n in enumerate(nhip)):
                pass
        dau = float(nhip[0].get("t", 0))
        if dau > 0.6:
            canh.append("nhịp đầu bắt đầu ở %.2f s, video sẽ trống %.1f s đầu — nên để t=0" % (dau, dau))
    # thực thể
    if tt:
        for r in sorted(refs):
            if r and r in tt and tt[r].get("loai") == "khong_ro":
                sai.append("thực thể '%s' chưa giải quyết được (xem tai_tai_nguyen)" % r)
    else:
        from engine.dia_ly import DiaLy
        import chuan_bi
        du = chuan_bi.duong_dan_du_lieu()
        dl = DiaLy(du["nuoc"], du["bang"]) if os.path.exists(du["nuoc"]) else None
        for r in sorted(refs):
            if not r:
                continue
            if (dl and dl.tim(r)) or C.tim_bien(r):
                continue
            canh.append("'%s' không phải nước/bang/biển trong bảng → sẽ geocode (thành phố/địa danh) ở bước tải" % r)
    print()
    for s in sai:
        print("⛔ " + s)
    for s in canh:
        print("⚠ " + s)
    if sai:
        print("\n⛔ %d lỗi phải sửa trong kich_ban.json" % len(sai))
        sys.exit(2)
    C.ok("kịch bản hợp lệ: %d nhịp, %d thực thể, %.1f s" % (len(nhip), len([r for r in refs if r]), T))


if __name__ == "__main__":
    main()
