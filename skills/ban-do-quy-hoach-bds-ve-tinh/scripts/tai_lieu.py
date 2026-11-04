# -*- coding: utf-8 -*-
"""Tài liệu cho thẻ: tìm → TẢI → XÁC MINH bằng con số trong lời → mới được dùng (chốt 04/11/2026: không khớp = không thẻ).

    python -I scripts/tai_lieu.py tim "sông Đáy 6.068 hộ 3.002 ha"            # DuckDuckGo HTML (best-effort)
    python -I scripts/tai_lieu.py xac-minh --url <url> --so 6068 --so 24272 --tu "sông Đáy" --out <thư mục>
    python -I scripts/tai_lieu.py trich-dan --cau "…" --nguon "CafeF 21/9/2026" --out the.png

xac-minh: tải trang (requests, UA trình duyệt) → chữ trên trang → chuẩn hoá số (6.068 = 6,068 = 6068) → mỗi --so phải
có mặt, mỗi --tu phải có mặt → tải ảnh trong bài (≥ 300 px) để Claude MỞ XEM → xac_minh.json + trang.txt.
Không đạt ⇒ in ⛔ và KHÔNG tải ảnh. Snippet máy tìm kiếm không phải bằng chứng (bài có thể đã bị gỡ/thay).
"""
import argparse
import html
import io
import os
import re
import sys
import time
from urllib.parse import urljoin, urlparse

import requests

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import chung as C

UA_TRINH_DUYET = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                                "Chrome/130.0 Safari/537.36", "Accept-Language": "vi,en;q=0.8"}
NGUON_TIN = ("gov.vn", "chinhphu.vn", "vnexpress.net", "tuoitre.vn", "thanhnien.vn", "dantri.com.vn", "vietnamnet.vn",
             "baoxaydung.vn", "kinhtedothi.vn", "hanoimoi.vn", "cafef.vn", "cafebiz.vn", "markettimes.vn",
             "nhandan.vn", "laodong.vn", "tienphong.vn", "baochinhphu.vn", "vtv.vn", "vov.vn", "baodautu.vn",
             "thuvienphapluat.vn", "qdnd.vn", "sggp.org.vn", "plo.vn", "nguoiquansat.vn", "vietnamplus.vn")


def _text_tu_html(h):
    h = re.sub(r"(?is)<(script|style|noscript|svg|iframe)[^>]*>.*?</\1>", " ", h)
    h = re.sub(r"(?i)<br\s*/?>|</p>|</div>|</li>|</h\d>|</tr>", "\n", h)
    h = re.sub(r"(?s)<[^>]+>", " ", h)
    h = html.unescape(h)
    h = re.sub(r"[ \t\r\f\v]+", " ", h)
    h = re.sub(r"\n\s*\n+", "\n", h)
    return C.nfc(h).strip()


def _title(h):
    m = re.search(r"(?is)<title[^>]*>(.*?)</title>", h)
    return C.nfc(html.unescape(re.sub(r"\s+", " ", m.group(1)))).strip() if m else ""


def _chuan_text_so(t):
    """chữ trên trang: mọi số dạng 6.068 / 6,068 → 6068 để so khớp; giữ số thập phân ngắn"""
    return re.sub(r"\d{1,3}(?:[.,]\d{3})+|\d+(?:[.,]\d{1,2})?", lambda m: C.chuan_hoa_so(m.group(0)), t)


def tim_ddg(q, n=10):
    """DuckDuckGo HTML (không cần khoá). Hay bị chặn/đổi giao diện ⇒ chỉ là best-effort; Claude Code nên dùng WebSearch."""
    out = []
    try:
        r = requests.post("https://html.duckduckgo.com/html/", data={"q": q}, headers=UA_TRINH_DUYET, timeout=30)
        for m in re.finditer(r'(?is)<a[^>]+class="result__a"[^>]+href="([^"]+)"[^>]*>(.*?)</a>.*?'
                             r'(?:<a[^>]+class="result__snippet"[^>]*>(.*?)</a>)?', r.text):
            url = html.unescape(m.group(1))
            mm = re.search(r"uddg=([^&]+)", url)
            if mm:
                from urllib.parse import unquote
                url = unquote(mm.group(1))
            out.append({"url": url, "tieu_de": _text_tu_html(m.group(2)), "mo_ta": _text_tu_html(m.group(3) or "")})
            if len(out) >= n:
                break
    except Exception as e:
        print("⚠ tìm DDG lỗi: %s" % e)
    return out


def tai_trang(url, timeout=40):
    r = requests.get(url, headers=UA_TRINH_DUYET, timeout=timeout, allow_redirects=True)
    r.raise_for_status()
    if not r.encoding or r.encoding.lower() in ("iso-8859-1", "ascii"):
        r.encoding = r.apparent_encoding or "utf-8"
    return r.text, r.url


def anh_trong_trang(h, base):
    urls = []
    for m in re.finditer(r'(?is)<img[^>]+>', h):
        tag = m.group(0)
        for attr in ("data-original", "data-src", "data-lazy-src", "src"):
            mm = re.search(r'%s=["\']([^"\']+)["\']' % attr, tag)
            if mm and not mm.group(1).startswith("data:"):
                u = urljoin(base, html.unescape(mm.group(1)))
                if re.search(r"\.(jpe?g|png|webp)(\?|$)", u, re.I) and u not in urls:
                    urls.append(u)
                break
    return urls


def xac_minh(url, so, tu, out, max_anh=12, min_px=300):
    os.makedirs(out, exist_ok=True)
    try:
        h, url_cuoi = tai_trang(url)
    except Exception as e:
        print("⛔ không tải được trang: %s" % e)
        return {"url": url, "ok": False, "loi": str(e)}
    text = _text_tu_html(h)
    tt = _title(h)
    C.ghi_text(os.path.join(out, "trang.txt"), "# %s\n# %s\n\n%s" % (tt, url_cuoi, text))
    norm = _chuan_text_so(text).lower()
    norm_khong_dau = C.ten_khong_dau(norm)
    thay, thieu = [], []
    for s in so:
        s2 = C.chuan_hoa_so(str(s))
        if re.search(r"(?<![\d.])" + re.escape(s2) + r"(?![\d])", norm):
            thay.append(s2)
        else:
            thieu.append(s2)
    tu_thay, tu_thieu = [], []
    for t in tu:
        if C.ten_khong_dau(t) in norm_khong_dau:
            tu_thay.append(t)
        else:
            tu_thieu.append(t)
    cau = []
    for s2 in thay:
        for m in re.finditer(r"[^\n.]*(?<![\d.])" + re.escape(s2) + r"(?![\d])[^\n.]*", norm):
            cau.append(m.group(0).strip()[:300])
            if len(cau) >= 12:
                break
    host = urlparse(url_cuoi).netloc.lower()
    tin_cay = any(host.endswith(d) for d in NGUON_TIN)
    ok = not thieu and not tu_thieu and bool(so)
    rp = {"url": url, "url_cuoi": url_cuoi, "tieu_de": tt, "host": host, "nguon_tin_cay": tin_cay, "ok": ok,
          "so_thay": thay, "so_thieu": thieu, "tu_thay": tu_thay, "tu_thieu": tu_thieu, "cau_chua_so": cau, "anh": []}
    print("▶ %s" % tt)
    print("   %s" % url_cuoi)
    print("   số thấy: %s · thiếu: %s · từ thiếu: %s · nguồn tin cậy: %s" % (thay, thieu, tu_thieu, tin_cay))
    for c in cau[:6]:
        print("   … %s" % c)
    if not ok:
        print("⛔ KHÔNG ĐẠT — không tải ảnh, không được làm thẻ từ trang này")
        C.jsave(os.path.join(out, "xac_minh.json"), rp)
        return rp
    from PIL import Image
    n = 0
    for u in anh_trong_trang(h, url_cuoi):
        if n >= max_anh:
            break
        try:
            r = requests.get(u, headers=UA_TRINH_DUYET, timeout=30)
            if r.status_code != 200 or len(r.content) < 8000:
                continue
            im = Image.open(io.BytesIO(r.content))
            im.load()
            if min(im.size) < min_px or max(im.size) / max(1, min(im.size)) > 4:
                continue
            n += 1
            p = os.path.join(out, "anh_%02d.jpg" % n)
            im.convert("RGB").save(p, quality=92)
            rp["anh"].append({"file": p, "url": u, "kich_thuoc": list(im.size)})
            print("   ảnh %02d %dx%d  %s" % (n, im.size[0], im.size[1], u[:90]))
        except Exception:
            continue
    C.jsave(os.path.join(out, "xac_minh.json"), rp)
    print("✅ ĐẠT: %d số khớp, %d ảnh tải về %s — Claude MỞ từng ảnh, chọn ảnh chứa đúng số; không có ảnh ⇒ dùng trich-dan"
          % (len(thay), n, out))
    return rp


def trich_dan(cau, nguon, out, rong=816):
    """thẻ trích dẫn chữ (khi trang xác minh được nhưng không có ảnh/bảng): hộp trắng, câu in nghiêng đậm, nguồn"""
    from PIL import Image
    lines = C.bo_dong(cau.strip(), "semi", 30, rong - 80)
    imgs = [C.chu(l, "semi", 30, fill=(20, 30, 50)) for l in lines[:8]]
    txt = C.xep_doc(imgs, gap=8, align="left")
    q = C.chu("“", "black", 90, fill=C.VANG)
    h = txt.height + 110
    im = Image.new("RGB", (rong, h), (248, 249, 252))
    im.paste(q, (28, 10), q)
    im.paste(txt, (40, 72), txt)
    src = C.chu("— " + nguon, "semi", 22, fill=(90, 100, 120))
    im.paste(src, (rong - src.width - 30, h - src.height - 14), src)
    im.save(out, quality=94)
    print("✅ thẻ trích dẫn: %s" % out)


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd")
    t = sub.add_parser("tim")
    t.add_argument("q")
    t.add_argument("--n", type=int, default=10)
    x = sub.add_parser("xac-minh")
    x.add_argument("--url", required=True)
    x.add_argument("--so", action="append", default=[], help="con số phải có (nguyên văn trong lời, vd 6.068)")
    x.add_argument("--tu", action="append", default=[], help="từ/tên phải có (vd 'sông Đáy')")
    x.add_argument("--out", required=True)
    d = sub.add_parser("trich-dan")
    d.add_argument("--cau", required=True)
    d.add_argument("--nguon", required=True)
    d.add_argument("--out", required=True)
    a = ap.parse_args()
    if a.cmd == "tim":
        for i, r in enumerate(tim_ddg(a.q, a.n), 1):
            print("%2d. %s\n    %s\n    %s" % (i, r["tieu_de"], r["url"], r["mo_ta"][:160]))
    elif a.cmd == "xac-minh":
        xac_minh(a.url, a.so, a.tu, a.out)
    elif a.cmd == "trich-dan":
        trich_dan(a.cau, a.nguon, a.out)
    else:
        ap.print_help()


if __name__ == "__main__":
    main()
