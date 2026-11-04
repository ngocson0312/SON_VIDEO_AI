# -*- coding: utf-8 -*-
"""Bước 3 (cần mạng): đọc work/kich_ban.json -> giải quyết mọi thực thể (nước, bang, biển, thành phố, người, vật thể,
ảnh minh hoạ), tải cờ / ảnh / ô bản đồ về cache, cắt nền ảnh người, ghi work/thuc_the.json + work/duyet.jpg.

python -I scripts/tai_tai_nguyen.py --work <thư mục work> [--khong-tai-vat] [--khong-o]
"""
import argparse
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import chung as C
import chuan_bi

GEOCACHE = os.path.join(C.CACHE, "geocode.json")
GIAY_PHEP_OK = ("public domain", "pd", "cc0", "cc by", "cc-by", "cc by-sa", "cc-by-sa", "gfdl", "no restrictions")


# ---------------- gom tham chiếu ----------------
def gom_tham_chieu(kb):
    diem, nguoi, vat, anh = [], [], [], []

    def them(x):
        if isinstance(x, str) and x.strip():
            diem.append(x.strip())

    for n in kb.get("nhip", []):
        cams = n.get("camera") or {}
        for cam in (cams if isinstance(cams, list) else [cams]):
            them(cam.get("toi"))
        for d in n.get("dong_tac", []) or []:
            loai = d.get("loai")
            for k in ("tai", "nuoc", "tu", "toi", "den_diem"):
                them(d.get(k))
            if loai == "phong" and isinstance(d.get("den"), str):
                them(d["den"])
            if loai == "nguoi" and d.get("ten"):
                nguoi.append(d["ten"].strip())
            if loai in ("vat_the", "phong", "tuyen") and d.get("vat"):
                vat.append(str(d["vat"]).strip())
            if loai == "anh":
                if d.get("tim"):
                    anh.append(d["tim"].strip())
                elif d.get("file"):
                    anh.append(d["file"].strip())
    ud = []
    for x in diem + nguoi + vat + anh:
        pass
    return (sorted(set(diem), key=diem.index), sorted(set(nguoi), key=nguoi.index),
            sorted(set(vat), key=vat.index), sorted(set(anh), key=anh.index))


# ---------------- geocode ----------------
def _doc_geocache():
    if os.path.exists(GEOCACHE):
        try:
            return C.doc_json(GEOCACHE)
        except Exception:
            return {}
    return {}


def geocode(ten, cache):
    k = C.ten_khong_dau(ten)
    if k in cache:
        return cache[k]
    kq = None
    j = C.lay_json("https://nominatim.openstreetmap.org/search",
                   {"q": ten, "format": "json", "limit": 1, "accept-language": "vi,en"}, im=True)
    if j:
        kq = {"lon": float(j[0]["lon"]), "lat": float(j[0]["lat"]), "ten": j[0].get("display_name", ten).split(",")[0],
              "nguon": "nominatim"}
    if kq is None:
        j = C.lay_json("https://photon.komoot.io/api/", {"q": ten, "limit": 1, "lang": "en"}, im=True)
        if j and j.get("features"):
            f = j["features"][0]
            lon, lat = f["geometry"]["coordinates"]
            kq = {"lon": float(lon), "lat": float(lat), "ten": f["properties"].get("name", ten), "nguon": "photon"}
    cache[k] = kq
    C.ghi_json(GEOCACHE, cache)
    time.sleep(1.0)  # lịch sự với Nominatim
    return kq


# ---------------- cờ ----------------
def tai_co(ma, thu_muc):
    ma = ma.lower()
    p = os.path.join(thu_muc, "%s.png" % ma)
    if os.path.exists(p):
        return p
    if C.tai_file("https://flagcdn.com/w640/%s.png" % ma, p, im=True):
        return p
    return None


# ---------------- cắt nền u2net ----------------
_U2 = None


def cat_nen(src, dst, model_path):
    """Cắt nền ảnh (người / vật) bằng u2net.onnx -> PNG RGBA, cắt sát biên. Trả True/False."""
    global _U2
    import cv2
    import numpy as np
    if not os.path.exists(model_path):
        return False
    try:
        if _U2 is None:
            import onnxruntime as ort
            _U2 = ort.InferenceSession(model_path, providers=["CPUExecutionProvider"])
        img = cv2.imdecode(np.fromfile(src, np.uint8), cv2.IMREAD_COLOR)
        if img is None:
            return False
        h, w = img.shape[:2]
        if max(h, w) > 1600:
            k = 1600 / max(h, w)
            img = cv2.resize(img, (int(w * k), int(h * k)), interpolation=cv2.INTER_AREA)
            h, w = img.shape[:2]
        x = cv2.cvtColor(cv2.resize(img, (320, 320), interpolation=cv2.INTER_AREA), cv2.COLOR_BGR2RGB)
        x = x.astype(np.float32) / 255.0
        x = (x - np.array([0.485, 0.456, 0.406], np.float32)) / np.array([0.229, 0.224, 0.225], np.float32)
        x = x.transpose(2, 0, 1)[None]
        name = _U2.get_inputs()[0].name
        out = _U2.run(None, {name: x})[0][0, 0]
        out = (out - out.min()) / max(1e-6, out.max() - out.min())
        mask = cv2.resize(out, (w, h), interpolation=cv2.INTER_LINEAR)
        mask = np.clip((mask - 0.15) / 0.7, 0, 1)
        mask = cv2.GaussianBlur(mask, (3, 3), 0)
        a = (mask * 255).astype(np.uint8)
        ys, xs = np.nonzero(a > 30)
        if len(xs) < 50:
            return False
        x0, x1, y0, y1 = max(0, xs.min() - 6), min(w, xs.max() + 7), max(0, ys.min() - 6), min(h, ys.max() + 7)
        rgba = np.dstack([img[y0:y1, x0:x1], a[y0:y1, x0:x1]])
        ok, buf = cv2.imencode(".png", rgba)
        if not ok:
            return False
        buf.tofile(dst)
        return True
    except Exception as exc:
        C.canh_bao("cắt nền lỗi (%s): %s" % (os.path.basename(src), exc))
        return False


# ---------------- Wikipedia / Commons ----------------
def anh_wikipedia(ten):
    """Ảnh đại diện bài Wikipedia (vi rồi en). Trả (url, tên file commons) hoặc (None, None)."""
    for lang in ("vi", "en"):
        j = C.lay_json("https://%s.wikipedia.org/w/api.php" % lang,
                       {"action": "query", "prop": "pageimages", "piprop": "original|name", "titles": ten,
                        "redirects": 1, "format": "json"}, im=True)
        if not j:
            continue
        for p in j.get("query", {}).get("pages", {}).values():
            o = p.get("original")
            if o and o.get("source"):
                return o["source"], p.get("pageimage")
        # thử tìm kiếm
        s = C.lay_json("https://%s.wikipedia.org/w/api.php" % lang,
                       {"action": "query", "list": "search", "srsearch": ten, "srlimit": 1, "format": "json"}, im=True)
        if s and s.get("query", {}).get("search"):
            title = s["query"]["search"][0]["title"]
            j2 = C.lay_json("https://%s.wikipedia.org/w/api.php" % lang,
                            {"action": "query", "prop": "pageimages", "piprop": "original|name", "titles": title,
                             "redirects": 1, "format": "json"}, im=True)
            if j2:
                for p in j2.get("query", {}).get("pages", {}).values():
                    o = p.get("original")
                    if o and o.get("source"):
                        return o["source"], p.get("pageimage")
    return None, None


def giay_phep_commons(ten_file):
    if not ten_file:
        return None
    j = C.lay_json("https://commons.wikimedia.org/w/api.php",
                   {"action": "query", "titles": "File:" + ten_file, "prop": "imageinfo",
                    "iiprop": "extmetadata|url", "format": "json"}, im=True)
    if not j:
        return None
    for p in j.get("query", {}).get("pages", {}).values():
        ii = p.get("imageinfo")
        if ii:
            md = ii[0].get("extmetadata", {})
            return {"giay_phep": md.get("LicenseShortName", {}).get("value"),
                    "tac_gia": md.get("Artist", {}).get("value", "")[:120], "url": ii[0].get("url")}
    return None


def tim_commons(query, so=6):
    """Tìm ảnh trên Wikimedia Commons, ưu tiên giấy phép tự do. Trả list dict {url, giay_phep, tieu_de}."""
    j = C.lay_json("https://commons.wikimedia.org/w/api.php",
                   {"action": "query", "generator": "search", "gsrsearch": "filetype:bitmap " + query,
                    "gsrnamespace": 6, "gsrlimit": so, "prop": "imageinfo",
                    "iiprop": "url|extmetadata|size|mime", "iiurlwidth": 1200, "format": "json"}, im=True)
    out = []
    if not j:
        return out
    for p in j.get("query", {}).get("pages", {}).values():
        ii = (p.get("imageinfo") or [None])[0]
        if not ii or ii.get("mime") not in ("image/jpeg", "image/png"):
            continue
        md = ii.get("extmetadata", {})
        gp = (md.get("LicenseShortName", {}).get("value") or "").lower()
        if gp and not any(x in gp for x in GIAY_PHEP_OK):
            continue
        out.append({"url": ii.get("thumburl") or ii.get("url"), "giay_phep": gp or "?", "tieu_de": p.get("title"),
                    "rong": ii.get("width", 0)})
    out.sort(key=lambda x: -x.get("rong", 0))
    return out


# ---------------- chính ----------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--work", required=True)
    ap.add_argument("--khong-tai-vat", action="store_true", help="không tải ảnh vật thể từ Commons, dùng icon có sẵn")
    ap.add_argument("--tai-vat", action="store_true", help="ép tải ảnh Commons cả cho vật đã có icon tự vẽ")
    ap.add_argument("--khong-o", action="store_true", help="không tải trước ô bản đồ")
    a = ap.parse_args()
    work = os.path.abspath(a.work)
    f_kb = os.path.join(work, "kich_ban.json")
    if not os.path.exists(f_kb):
        C.die("chưa có %s — Claude phải viết kịch bản trước (xem SKILL.md)" % f_kb)
    kb = C.doc_json(f_kb)
    C.buoc("Giải quyết thực thể & tải tài nguyên")
    du = chuan_bi.bao_dam(can_mang=True)
    from engine.dia_ly import DiaLy
    dl = DiaLy(du["nuoc"], du["bang"])
    tn = C.mkdir(os.path.join(work, "tai_nguyen"))
    tn_user = os.path.join(os.path.dirname(work), "tai_nguyen")   # ảnh người dùng tự bỏ vào
    co_dir = C.mkdir(os.path.join(C.CACHE, "co"))
    thu_vien_tai = C.mkdir(os.path.join(C.CACHE, "thu_vien_tai"))
    geocache = _doc_geocache()
    thuc_the = {}
    if os.path.exists(os.path.join(work, "thuc_the.json")):
        try:
            thuc_the = C.doc_json(os.path.join(work, "thuc_the.json"))
        except Exception:
            thuc_the = {}
    diem, nguoi, vat, anh = gom_tham_chieu(kb)
    khong_ro = []

    def anh_user(ten):
        for d in (tn_user, tn):
            if not os.path.isdir(d):
                continue
            k = C.ten_khong_dau(ten)
            for f in os.listdir(d):
                g, e = os.path.splitext(f)
                if e.lower() in (".png", ".jpg", ".jpeg", ".webp") and C.ten_khong_dau(g) in (k, "nguoi " + k, "anh " + k):
                    return os.path.join(d, f)
        return None

    # --- điểm / vùng ---
    print("· %d tham chiếu vị trí" % len(diem))
    for ref in diem:
        if ref in thuc_the and thuc_the[ref].get("loai") != "khong_ro":
            continue
        rec = dl.tim(ref)
        if rec:
            r = {"loai": rec["loai"], "ten": rec["ten"], "ten_ne": rec["ten"], "iso": rec["iso"],
                 "lon": rec["lon"], "lat": rec["lat"]}
            ma = rec["iso"].lower() if rec["iso"] and len(rec["iso"]) == 2 else None
            if rec["loai"] == "bang":
                # cờ bang Mỹ theo mã US-XX
                ma_bang = None
                for ft in ():
                    pass
                ma_bang = _ma_bang(rec, dl)
                if ma_bang:
                    p = tai_co(ma_bang, co_dir)
                    if p:
                        r["co"] = p
            if "co" not in r and ma:
                p = tai_co(ma, co_dir)
                if p:
                    r["co"] = p
            thuc_the[ref] = r
            print("   ✓ %-28s → %s %s (%.2f, %.2f)%s" % (ref, rec["loai"], rec["ten"], rec["lon"], rec["lat"],
                                                       "" if r.get("co") else "  [không có cờ]"))
            continue
        b = C.tim_bien(ref)
        if b:
            thuc_the[ref] = {"loai": "bien", "ten": b[0], "lon": b[1], "lat": b[2]}
            print("   ✓ %-28s → biển %s" % (ref, b[0]))
            continue
        g = geocode(ref, geocache)
        if g:
            thuc_the[ref] = {"loai": "thanh_pho", "ten": g["ten"], "lon": g["lon"], "lat": g["lat"], "nguon": g["nguon"]}
            print("   ✓ %-28s → điểm %s (%.2f, %.2f) [%s]" % (ref, g["ten"], g["lon"], g["lat"], g["nguon"]))
        else:
            thuc_the[ref] = {"loai": "khong_ro"}
            khong_ro.append(ref)
            print("   ✗ %-28s → KHÔNG tìm được" % ref)

    # --- người ---
    print("· %d nhân vật" % len(nguoi))
    for ten in nguoi:
        key = ten
        slug = C.ten_file_an_toan(ten)
        dst = os.path.join(tn, "nguoi_%s.png" % slug)
        r = thuc_the.get(key) or {}
        if r.get("anh") and os.path.exists(r["anh"]):
            continue
        src_user = anh_user(ten)
        if src_user:
            if cat_nen(src_user, dst, du["u2net"]) or _copy(src_user, dst):
                thuc_the[key] = {"loai": "nguoi", "ten": ten, "anh": dst, "nguon": "người dùng cấp"}
                print("   ✓ %-28s → ảnh người dùng cấp" % ten)
                continue
        url, ten_file = anh_wikipedia(ten)
        if not url:
            thuc_the[key] = {"loai": "nguoi", "ten": ten}
            khong_ro.append("ảnh người: " + ten)
            print("   ✗ %-28s → không có ảnh Wikipedia" % ten)
            continue
        raw = os.path.join(tn, "nguoi_%s_goc%s" % (slug, os.path.splitext(url)[1][:5] or ".jpg"))
        if not C.tai_file(url, raw, im=True):
            thuc_the[key] = {"loai": "nguoi", "ten": ten}
            khong_ro.append("ảnh người: " + ten)
            print("   ✗ %-28s → tải ảnh lỗi" % ten)
            continue
        gp = giay_phep_commons(ten_file) or {}
        if cat_nen(raw, dst, du["u2net"]):
            thuc_the[key] = {"loai": "nguoi", "ten": ten, "anh": dst, "nguon": url, "giay_phep": gp.get("giay_phep"),
                             "tac_gia": gp.get("tac_gia")}
            print("   ✓ %-28s → Wikipedia, cắt nền xong (giấy phép: %s)" % (ten, gp.get("giay_phep")))
        else:
            thuc_the[key] = {"loai": "nguoi", "ten": ten, "anh": raw, "nguon": url, "giay_phep": gp.get("giay_phep")}
            print("   ⚠ %-28s → có ảnh nhưng không cắt được nền" % ten)

    # --- vật thể ---
    print("· %d vật thể" % len(vat))
    for v in vat:
        k = C.tim_vat_the(v)
        if os.path.exists(v):
            continue
        if k is None:
            khong_ro.append("vật thể: %s (không có trong bảng VAT_THE, dùng icon mặc định nếu trùng tên file)" % v)
            print("   ✗ %-28s → từ khoá lạ" % v)
            continue
        co_user = os.path.exists(os.path.join(C.THU_VIEN, k + ".png"))
        co_tai = os.path.exists(os.path.join(thu_vien_tai, k + ".png"))
        co_mac_dinh = os.path.exists(os.path.join(du["icon"], k + ".png"))
        if co_user or co_tai:
            print("   ✓ %-28s → %s (%s)" % (v, k, "thư viện người dùng" if co_user else "đã tải trước đó"))
            continue
        if a.khong_tai_vat or (co_mac_dinh and not a.tai_vat):
            print("   • %-28s → %s icon tự vẽ%s" % (v, k, "" if co_mac_dinh else " (KHÔNG CÓ)"))
            continue
        q = C.VAT_THE[k][1]
        kq = tim_commons(q + " png" if False else q, 6)
        tai_duoc = False
        for it in kq[:3]:
            raw = os.path.join(thu_vien_tai, "%s_goc.jpg" % k)
            if C.tai_file(it["url"], raw, im=True):
                dst = os.path.join(thu_vien_tai, k + ".png")
                if cat_nen(raw, dst, du["u2net"]):
                    C.ghi_json(os.path.join(thu_vien_tai, k + ".json"),
                               {"nguon": it["url"], "giay_phep": it["giay_phep"], "tieu_de": it["tieu_de"]})
                    print("   ✓ %-28s → tải Commons + cắt nền (%s)" % (v, it["giay_phep"]))
                    tai_duoc = True
                    break
                try:
                    os.remove(raw)
                except Exception:
                    pass
        if not tai_duoc:
            print("   • %-28s → %s icon mặc định%s" % (v, k, "" if co_mac_dinh else " (KHÔNG CÓ)"))

    # --- ảnh minh hoạ ---
    print("· %d ảnh minh hoạ" % len(anh))
    for q in anh:
        if os.path.exists(q):
            continue
        key = q
        r = thuc_the.get(key) or {}
        if r.get("anh") and os.path.exists(r["anh"]):
            continue
        src_user = anh_user(q)
        if src_user:
            thuc_the[key] = {"loai": "anh", "anh": src_user, "nguon": "người dùng cấp"}
            print("   ✓ %-28s → ảnh người dùng cấp" % q)
            continue
        kq = tim_commons(q, 5)
        ok = False
        for it in kq[:3]:
            dst = os.path.join(tn, "anh_%s.jpg" % C.ten_file_an_toan(q))
            if C.tai_file(it["url"], dst, im=True):
                thuc_the[key] = {"loai": "anh", "anh": dst, "nguon": it["url"], "giay_phep": it["giay_phep"]}
                print("   ✓ %-28s → Commons (%s)" % (q, it["giay_phep"]))
                ok = True
                break
        if not ok:
            thuc_the[key] = {"loai": "anh"}
            khong_ro.append("ảnh: " + q)
            print("   ✗ %-28s → không tìm được ảnh" % q)

    C.ghi_json(os.path.join(work, "thuc_the.json"), thuc_the)
    C.ok("đã ghi thuc_the.json (%d mục)" % len(thuc_the))

    # --- ô bản đồ ---
    if not a.khong_o:
        from engine.render import BoDung
        kb.setdefault("thoi_luong", _thoi_luong(work, kb))
        bd = BoDung(kb, thuc_the, du, os.path.join(C.CACHE, "tiles"), mang=True)
        ks = bd.o_can_toan_bo(0.25)
        n, loi = bd.nen.tai_truoc(ks)
        print("· ô bản đồ cần: %d, tải mới: %d, lỗi: %d" % (len(ks), n, loi))
        if loi:
            C.canh_bao("%d ô tải lỗi — chỗ đó sẽ dùng ô mức thấp hơn (mờ)" % loi)

    # --- tờ duyệt ---
    lam_to_duyet(work, thuc_the, vat, du)
    if khong_ro:
        print("\n⚠ CHƯA GIẢI QUYẾT ĐƯỢC (hỏi người dùng ở cổng duyệt hoặc sửa kịch bản):")
        for x in khong_ro:
            print("   - " + x)
    else:
        C.ok("mọi thực thể đều giải quyết được")


def _copy(src, dst):
    try:
        from PIL import Image
        Image.open(src).convert("RGBA").save(dst)
        return True
    except Exception:
        return False


def _ma_bang(rec, dl):
    """Mã cờ flagcdn cho bang Mỹ (us-ak). Chỉ hỗ trợ Mỹ."""
    if rec.get("iso") != "US":
        return None
    ten = C.ten_khong_dau(rec["ten"])
    bang_my = {"alaska": "ak", "california": "ca", "texas": "tx", "hawaii": "hi", "florida": "fl", "new york": "ny",
               "washington": "wa", "nevada": "nv", "arizona": "az", "colorado": "co", "oregon": "or", "utah": "ut",
               "new mexico": "nm", "montana": "mt", "idaho": "id", "wyoming": "wy", "north dakota": "nd",
               "south dakota": "sd", "nebraska": "ne", "kansas": "ks", "oklahoma": "ok", "minnesota": "mn",
               "iowa": "ia", "missouri": "mo", "arkansas": "ar", "louisiana": "la", "wisconsin": "wi",
               "illinois": "il", "michigan": "mi", "indiana": "in", "ohio": "oh", "kentucky": "ky", "tennessee": "tn",
               "mississippi": "ms", "alabama": "al", "georgia": "ga", "south carolina": "sc", "north carolina": "nc",
               "virginia": "va", "west virginia": "wv", "pennsylvania": "pa", "maryland": "md", "delaware": "de",
               "new jersey": "nj", "connecticut": "ct", "rhode island": "ri", "massachusetts": "ma", "vermont": "vt",
               "new hampshire": "nh", "maine": "me"}
    ma = bang_my.get(ten)
    return ("us-" + ma) if ma else None


def _thoi_luong(work, kb):
    f = os.path.join(work, "loi_doc.json")
    if os.path.exists(f):
        return float(C.doc_json(f)["thoi_luong"]) + C.DUOI_SAU_TIENG_CUOI
    return float(kb.get("thoi_luong") or 30.0)


def lam_to_duyet(work, thuc_the, vat, du):
    """Tờ ảnh work/duyet.jpg: cờ, người, vật thể, ảnh đã có — để Claude mở soi và đưa người dùng duyệt."""
    from PIL import Image, ImageDraw, ImageFont
    o = []
    for k, r in thuc_the.items():
        if r.get("co"):
            o.append((r["co"], "cờ: %s" % k))
    for k, r in thuc_the.items():
        if r.get("loai") == "nguoi":
            o.append((r.get("anh"), "người: %s%s" % (k, "" if r.get("anh") else " (KHÔNG CÓ ẢNH)")))
    thu_vien = [C.THU_VIEN, os.path.join(C.CACHE, "thu_vien_tai"), du["icon"]]
    for v in vat:
        k = C.tim_vat_the(v) or v
        p = None
        for d in thu_vien:
            c = os.path.join(d, k + ".png")
            if os.path.exists(c):
                p = c
                break
        o.append((p, "vật: %s → %s" % (v, os.path.basename(os.path.dirname(p)) if p else "KHÔNG CÓ")))
    for k, r in thuc_the.items():
        if r.get("loai") == "anh":
            o.append((r.get("anh"), "ảnh: %s" % k))
    if not o:
        return
    cot, ow, oh = 4, 300, 340
    hang = (len(o) + cot - 1) // cot
    sheet = Image.new("RGB", (cot * ow, hang * oh), (28, 32, 40))
    d = ImageDraw.Draw(sheet)
    try:
        f = ImageFont.truetype(du["font_dam"] if os.path.exists(du["font_dam"]) else "C:/Windows/Fonts/arialbd.ttf", 18)
    except Exception:
        f = ImageFont.load_default()
    for i, (p, nhan) in enumerate(o):
        x, y = (i % cot) * ow, (i // cot) * oh
        if p and os.path.exists(p):
            try:
                im = Image.open(p).convert("RGBA")
                im.thumbnail((ow - 20, oh - 60))
                bg = Image.new("RGBA", im.size, (90, 90, 100, 255))
                bg.alpha_composite(im)
                sheet.paste(bg.convert("RGB"), (x + 10 + (ow - 20 - im.size[0]) // 2, y + 10))
            except Exception:
                pass
        d.text((x + 8, y + oh - 44), nhan[:34], font=f, fill=(255, 230, 120))
        if len(nhan) > 34:
            d.text((x + 8, y + oh - 24), nhan[34:68], font=f, fill=(255, 230, 120))
    out = os.path.join(work, "duyet.jpg")
    sheet.save(out, quality=85)
    print("· tờ duyệt tài nguyên: " + out)


if __name__ == "__main__":
    main()
