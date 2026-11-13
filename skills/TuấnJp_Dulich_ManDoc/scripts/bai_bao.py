# -*- coding: utf-8 -*-
"""bai_bao.py — lấy bài báo du lịch từ link: tiêu đề, sapo, các đoạn, ẢNH (tải về + chú thích).

Thứ tự thử:
  1. trang có API riêng đã biết (vietnamtourism.gov.vn — trang Vue, HTML gốc rỗng → gọi public API)
  2. HTML thường (urllib) → og:title / <article> / <p> / <img>
  3. trang dựng bằng JS (chữ quá ít) → Chrome headless --dump-dom rồi đọc lại như (2)
Kết quả: <out>/bai_bao.json, <out>/bai_bao.txt, <out>/anh/bai_01.jpg …
"""
import html as H
import io
import json
import re
import subprocess
import sys
import urllib.parse
import urllib.request
from html.parser import HTMLParser
from pathlib import Path

from chung import ghi_json, loi, tim_chrome

UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36'
ANH_NHO = 360          # ảnh nhỏ hơn cạnh này (px) = icon / logo → bỏ


def tai(u, timeout=30):
    rq = urllib.request.Request(u, headers={'User-Agent': UA, 'Accept-Language': 'vi,en;q=0.8'})
    with urllib.request.urlopen(rq, timeout=timeout) as r:
        return r.read(), r.headers.get_content_charset() or 'utf-8', r.geturl()


def _lam_sach(s):
    s = H.unescape(re.sub(r'<[^>]+>', '', s or ''))
    return re.sub(r'\s+', ' ', s).strip()


class _Doc(HTMLParser):
    """đọc HTML → dãy khối theo thứ tự: ('h', text) ('p', text) ('img', src, alt) ('cap', text)."""
    BO = {'script', 'style', 'noscript', 'nav', 'footer', 'header', 'aside', 'form', 'svg', 'button'}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.khoi, self.meta = [], {}
        self._bo = 0
        self._the = None
        self._buf = []
        self.trong_article = 0
        self.co_article = False

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == 'meta':
            k = (a.get('property') or a.get('name') or '').lower()
            if k in ('og:title', 'og:description', 'og:image', 'description', 'og:site_name'):
                self.meta.setdefault(k, a.get('content') or '')
        if tag in self.BO:
            self._bo += 1
            return
        if tag == 'article':
            self.trong_article += 1
            self.co_article = True
        if self._bo:
            return
        if tag in ('p', 'h1', 'h2', 'h3', 'h4', 'li', 'figcaption', 'blockquote', 'title'):
            self._dong()
            self._the = tag
        elif tag == 'br' and self._the:
            self._buf.append('\n')
        elif tag == 'img':
            src = a.get('data-src') or a.get('data-original') or a.get('data-lazy-src') or ''
            ss = a.get('data-srcset') or a.get('srcset') or ''
            if not src and ss:                    # srcset → lấy bản RỘNG nhất (src thường là bản thu nhỏ)
                best, bw = '', -1.0
                for part in ss.split(','):
                    xs = part.strip().split()
                    if not xs:
                        continue
                    m = re.match(r'([\d.]+)[wx]$', xs[1]) if len(xs) > 1 else None
                    w = float(m.group(1)) if m else 0.0
                    if w >= bw:
                        best, bw = xs[0], w
                src = best
            src = src or a.get('src') or ''
            if src and not src.startswith('data:'):
                self.khoi.append(('img', src, a.get('alt') or a.get('title') or '', self.trong_article > 0))

    def handle_endtag(self, tag):
        if tag in self.BO:
            self._bo = max(0, self._bo - 1)
            return
        if tag == 'article':
            self.trong_article = max(0, self.trong_article - 1)
        if tag == self._the:
            self._dong()

    def handle_data(self, d):
        if self._the and not self._bo:
            self._buf.append(d)

    def _dong(self):
        if self._the and self._buf:
            t = re.sub(r'[ \t\r\f\v]+', ' ', ''.join(self._buf)).strip()
            if t:
                k = {'h1': 'h', 'h2': 'h', 'h3': 'h', 'h4': 'h', 'figcaption': 'cap', 'title': 'title'}.get(self._the, 'p')
                self.khoi.append((k, t, self.trong_article > 0))
        self._the, self._buf = None, []


def _tu_html(raw, base):
    d = _Doc()
    d.feed(raw)
    d._dong()
    khoi = d.khoi
    if d.co_article:                       # có <article> → chỉ lấy trong article (bỏ menu, tin liên quan)
        trong = [k for k in khoi if k[-1]]
        if sum(len(k[1]) for k in trong if k[0] in ('p', 'h')) > 400:
            khoi = trong
    tieu_de = d.meta.get('og:title') or next((k[1] for k in khoi if k[0] == 'h'), '') or next((k[1] for k in d.khoi if k[0] == 'title'), '')
    doan, anh = [], []
    truoc = None
    for k in khoi:
        if k[0] in ('p', 'h') and len(k[1]) >= 2:
            if k[0] == 'p' and truoc == 'img' and anh and not anh[-1]['chu_thich'] and len(k[1]) <= 160:
                anh[-1]['chu_thich'] = k[1]          # đoạn ngắn ngay dưới ảnh = chú thích ảnh
            doan.append(('## ' if k[0] == 'h' else '') + k[1])
        elif k[0] == 'cap' and anh:
            anh[-1]['chu_thich'] = k[1]
        elif k[0] == 'img':
            anh.append({'url': urllib.parse.urljoin(base, k[1]), 'alt': k[2], 'chu_thich': ''})
        truoc = k[0]
    if d.meta.get('og:image'):
        anh.insert(0, {'url': urllib.parse.urljoin(base, d.meta['og:image']), 'alt': 'og:image', 'chu_thich': ''})
    return {'tieu_de': _lam_sach(tieu_de), 'sapo': _lam_sach(d.meta.get('og:description') or d.meta.get('description') or ''),
            'doan': doan, 'anh': anh}


def _vietnamtourism(u):
    m = re.search(r'vietnamtourism\.gov\.vn/(?:[a-z]{2}/)?post/(\d+)', u)
    if not m:
        return None
    api = f'https://public.vietnamtourism.gov.vn/post/{m.group(1)}?param=' + urllib.parse.quote('{"lang":"vi"}')
    raw, cs, _ = tai(api)
    d = json.loads(raw.decode('utf-8', 'replace'))
    if not d.get('title'):
        return None
    body = (d.get('summary') or '') + (d.get('content') or '')
    # ảnh '/images/…' của trang này nằm ở máy chủ ảnh riêng (đường gốc trả về HTML của app Vue)
    kq = _tu_html('<article>' + body + '</article>', 'https://vietnamtourism.gov.vn/')
    for a in kq['anh']:
        a['url'] = re.sub(r'^https://vietnamtourism\.gov\.vn/(?:vn/)?images/', 'https://images.vietnamtourism.gov.vn/vn/images/', a['url'])
    kq['tieu_de'] = _lam_sach(d['title'])
    kq['sapo'] = kq['doan'][0] if kq['doan'] else ''
    kq['nguon'] = 'vietnamtourism.gov.vn'
    kq['the'] = d.get('tags_view') or ''
    return kq


def _chrome_dom(u):
    c = tim_chrome()
    if not c:
        return None
    r = subprocess.run([c, '--headless=new', '--disable-gpu', '--virtual-time-budget=12000', '--dump-dom', u],
                       capture_output=True, timeout=90)
    return r.stdout.decode('utf-8', 'replace') if r.returncode == 0 else None


def _luu_anh(ds, out):
    from PIL import Image, ImageOps
    thu = out / 'anh'
    thu.mkdir(parents=True, exist_ok=True)
    da, kq, k = set(), [], 0
    for a in ds:
        u = a['url'].split('#')[0]
        goc = re.sub(r'[-_]\d{2,4}x\d{2,4}(?=\.\w+$)', '', u)         # ảnh thu nhỏ kiểu wordpress → bản gốc
        goc = re.sub(r'(upload\.wikimedia\.org/.+/thumb/.+)/\d+px-([^/]+)$', r'\1/1280px-\2', goc)   # Wikipedia / Wikivoyage
        if goc in da:
            continue
        da.add(goc)
        if re.search(r'(logo|icon|avatar|sprite|banner-ads|qr|captcha|pixel|blank|emoji|flag)\b|maps\.wikimedia|osm-intl|staticmap|@2x\.png\?|\.svg(\?|$)',
                     u, re.I):
            continue
        im = None
        for th in ([goc, u] if goc != u else [u]):
            try:
                raw, _, _ = tai(th)
                im = Image.open(io.BytesIO(raw))
                im.load()
                break
            except Exception:
                im = None
        if im is None:
            loi(f'  ⚠ không tải được ảnh {u}')
            continue
        if min(im.size) < ANH_NHO or max(im.size) / max(1, min(im.size)) > 3.2:
            continue                                  # icon / logo / băng rôn đầu trang (quá dẹt)
        k += 1
        f = thu / f'bai_{k:02d}.jpg'
        try:
            im = ImageOps.exif_transpose(im)          # ảnh chụp điện thoại có cờ xoay
        except Exception:
            pass
        if im.mode in ('RGBA', 'LA', 'PA', 'P'):
            im = im.convert('RGBA')
            nen = Image.new('RGB', im.size, (18, 20, 26))
            nen.paste(im, mask=im.split()[-1])
            im = nen
        im.convert('RGB').save(f, quality=93)
        kq.append({'id': f'bai_{k:02d}', 'file': str(f), 'w': im.size[0], 'h': im.size[1], 'url': u, 'alt': a.get('alt', ''),
                   'chu_thich': a.get('chu_thich', '')})
        loi(f'  ảnh bai_{k:02d}: {im.size[0]}x{im.size[1]}  {a.get("chu_thich") or a.get("alt") or ""}'[:150])
    return kq


def _bo_duoi_trang(t, mien):
    """'Hanoi – Travel guide at Wikivoyage' → 'Hanoi'; 'Xưởng chạm bạc … - VnExpress Du lịch' → 'Xưởng chạm bạc …'."""
    from chung import bo_dau
    goc = bo_dau((mien.split('.')[-2] if mien.count('.') >= 1 else mien))
    while True:
        p = re.split(r'\s+[|–—-]\s+', t)
        if len(p) < 2:
            return t
        cuoi = bo_dau(p[-1])
        if (goc and goc in cuoi) or re.search(r'(travel guide|wiki|bao |tin tuc|news|magazine|tap chi)', p[-1], re.I):
            t = t[:len(t) - len(p[-1])].rstrip(' |–—-')
        else:
            return t


def lay_bai(link, out):
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    kq = None
    try:
        kq = _vietnamtourism(link)
    except Exception as e:
        loi(f'  ⚠ API vietnamtourism lỗi: {e}')
    if kq is None:
        raw, cs, base = tai(link)
        kq = _tu_html(raw.decode(cs, 'replace'), base)
        if sum(len(x) for x in kq['doan']) < 600:                      # trang JS → nhờ Chrome dựng
            loi('  trang ít chữ (có thể dựng bằng JS) → mở bằng Chrome headless …')
            dom = _chrome_dom(link)
            if dom:
                k2 = _tu_html(dom, base)
                if sum(len(x) for x in k2['doan']) > sum(len(x) for x in kq['doan']):
                    kq = k2
        kq['nguon'] = urllib.parse.urlparse(link).netloc.replace('www.', '')
    kq['tieu_de'] = _bo_duoi_trang(kq.get('tieu_de', ''), kq['nguon'])
    gon = []                                                          # bỏ đoạn lặp liền nhau (tiêu đề in 2 lần…)
    for x in kq.get('doan', []):
        if not gon or gon[-1] != x:
            gon.append(x)
    kq['doan'] = gon
    kq['link'] = link
    kq['anh'] = _luu_anh(kq.get('anh', []), out)
    ghi_json(out / 'bai_bao.json', kq)
    txt = [f"NGUỒN: {kq['nguon']}  ({link})", f"TIÊU ĐỀ: {kq['tieu_de']}", '']
    txt += kq['doan']
    txt += ['', 'ẢNH:'] + [f"  {a['id']}  {a['w']}x{a['h']}  {a['chu_thich'] or a['alt']}" for a in kq['anh']]
    (out / 'bai_bao.txt').write_text('\n'.join(txt), encoding='utf-8')
    loi(f"  bài: «{kq['tieu_de']}» — {len(kq['doan'])} đoạn, {len(kq['anh'])} ảnh")
    if sum(len(x) for x in kq['doan']) < 300:
        loi('  ⚠ lấy được rất ít chữ — mở link xem tay, dán nội dung vào bai_bao.txt nếu cần')
    return kq


if __name__ == '__main__':
    lay_bai(sys.argv[1], sys.argv[2])
