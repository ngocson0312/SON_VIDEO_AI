# -*- coding: utf-8 -*-
"""Gom tu thanh cum roi xuat file .ASS sub karaoke word-by-word.

    python scripts/build_ass.py --video <video> --out <video_ra.mp4> \
        [--max-words 4] [--max-chars 22] [--gap 0.35] \
        [--y 1536] [--safe "0-12:1100,12-30:1536"] \
        [--font-size 80] [--outline 7] \
        [--active-color "#FFD600"] [--base-color "#FFFFFF"]

KHONG DUNG TAG \\k. Da kiem tren may nay: \\k boi mau phan CHUA doc toi,
tuc nguoc y muon. Cach dung o day: moi TU phat MOT dong Dialogue rieng,
dong nao cung cho ca cum, chi khac o cho tu dang doc duoc boc bang
{\\c&H..&} ... {\\c&H..&} — mau ghi thang, khong nho vao \\k.
"""
from __future__ import annotations

import argparse
import io
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import nnscommon as C  # noqa: E402

END_PUNCT = u".!?…:;"
SOFT_PUNCT = u","

# Cum ngan hon nguong nay thi khong cat theo ranh vung an toan nua — thay vao
# do cho no y cua doan sau. 0.15s = ~4-5 frame, duoi muc do la nhay nhay.
MIN_CHUNK_DUR = 0.15


# --------------------------------------------------------------------------
# mau: nhan #RRGGBB hoac &HAABBGGRR, luon xuat ra dang ASS &HAABBGGRR
# --------------------------------------------------------------------------

def to_ass_color(text, what="mau"):
    s = str(text).strip()
    if s.lower().startswith("&h"):
        body = s[2:].rstrip("&")
        if not re.fullmatch(r"[0-9a-fA-F]{6,8}", body or ""):
            C.die("%s '%s' khong dung dang &HAABBGGRR" % (what, text))
        return "&H" + body.upper().rjust(8, "0") + "&"
    s = s.lstrip("#")
    if not re.fullmatch(r"[0-9a-fA-F]{6}", s):
        C.die("%s '%s' khong hieu duoc.\n"
              "  Dung dang #RRGGBB (vd #FFD600) hoac &HAABBGGRR (vd &H0000D6FF&)"
              % (what, text))
    r, g, b = s[0:2], s[2:4], s[4:6]
    # ASS la &HAABBGGRR — dao thu tu so voi HTML, AA=00 la duc hoan toan
    return ("&H00%s%s%s&" % (b, g, r)).upper()


def disp_word(text):
    """Chu HIEN tren man hinh: bo dau cau o CUOI tu (, . ; : …) - chu du an khong muon thay dau phay tren sub
    karaoke, va dau cham bom vao ranh cau chi de tach cum. Dau o GIUA tu giu nguyen ('1,5' khong thanh '15')."""
    t = text.rstrip(u",.;:…")
    return t if t else text


def ass_escape(text):
    """Chu trong Dialogue khong duoc chua { } (libass hieu la tag)."""
    return (text.replace("\\", "/").replace("{", "(").replace("}", ")")
                .replace("\r", " ").replace("\n", " "))


# --------------------------------------------------------------------------
# vung an toan theo thoi gian: --safe "a-b:y,c-d:y"
# --------------------------------------------------------------------------

def parse_safe(spec, video_h):
    """Tra ve list (start, end, y) da sap xep."""
    if not spec:
        return []
    out = []
    for part in spec.split(","):
        part = part.strip()
        if not part:
            continue
        m = re.fullmatch(r"\s*([0-9]*\.?[0-9]+)\s*-\s*([0-9]*\.?[0-9]+)\s*:"
                         r"\s*(-?[0-9]+)\s*", part)
        if not m:
            C.die("--safe sai dang o doan '%s'.\n"
                  '  Dung dang:  --safe "0-12:1100,12-30:1536"\n'
                  "  nghia la: giay 0..12 dat sub o y=1100, giay 12..30 dat o y=1536"
                  % part)
        a, b, y = float(m.group(1)), float(m.group(2)), int(m.group(3))
        if b <= a:
            C.die("--safe doan '%s': giay ket thuc phai lon hon giay bat dau"
                  % part)
        if not (0 <= y <= video_h):
            C.die("--safe doan '%s': y=%d nam ngoai khung cao %d px"
                  % (part, y, video_h))
        out.append((a, b, y))
    out.sort()
    for i in range(len(out) - 1):
        if out[i][1] > out[i + 1][0] + 1e-9:
            C.die("--safe co 2 doan chong nhau: %.2f-%.2f va %.2f-%.2f"
                  % (out[i][0], out[i][1], out[i + 1][0], out[i + 1][1]))
    return out


class Layout(object):
    def __init__(self, safe, default_y):
        self.safe = safe
        self.default_y = default_y
        # moc GIAO NHAU giua cac vung — cum sub KHONG duoc vat qua cac moc nay
        self.bounds = sorted({t for a, b, _y in safe for t in (a, b)})

    def y_at(self, t):
        for a, b, y in self.safe:
            if a - 1e-9 <= t < b:
                return y
        return self.default_y

    def next_change(self, t, y):
        """Moc dau tien sau t ma y doi khac -> dung de CAT NGAN cum."""
        for b in self.bounds:
            if b > t + 1e-9 and self.y_at(b) != y:
                return b
        return None


# --------------------------------------------------------------------------
# do BE RONG chu that bang libass (khong doan)
# --------------------------------------------------------------------------

CALIB_TEXT = u"những đường cong ắt phải đủ rộng ẩm ướt AI Claude 0123"


def calibrate_char_px(font, family, bold, size):
    h = max(120, int(size * 2.5))
    r = C.render_ink(CALIB_TEXT, font, family, bold, size=size, w=3200, h=h)
    if r["ink"] <= 0 or r["w"] <= 0:
        C.die("khong do duoc be rong chu — libass ve ra khung trong.\n"
              "  Chay lai preflight de kiem font.")
    return r["w"] / float(len(CALIB_TEXT)), r


def measure_text_px(text, font, family, bold, size):
    h = max(120, int(size * 2.5))
    r = C.render_ink(text, font, family, bold, size=size, w=3200, h=h)
    return r["w"]


# --------------------------------------------------------------------------
# gom tu thanh cum
# --------------------------------------------------------------------------

# Cap tu KHONG NEN tach doi qua 2 cum (tu ghep / ten rieng hay gap trong video AI).
# Da tra gia (khoa hoc Bai 3): "tai | khoan", "ngan | hang", "Ha | Noi", "toi | thieu"
# bi cat dung tran 6 tu -> nguoi xem doc hut nghia. Bo sung bang --keep-pairs <file>.
KEEP_PAIRS = set(x.strip() for x in u"""
tài khoản|ngân hàng|quan tâm|cái nào|có thể|sử dụng|chia sẻ|bên dưới|như thế|đi đặt|hà nội|phú thọ|việt nam|tối thiểu|so sánh|liên quan|nôm na|phiên bản
điều kiện|chuẩn bị|tự động|chính chủ|chợ đen|kinh nghiệm|xương máu|khóa học|khoá học|máy tính
thẻ visa|thanh toán|đăng nhập|đăng ký|tài liệu|công ty|cá nhân|doanh nghiệp|mọi người|các bác
anh em|bây giờ|hiện tại|thời gian|sử dụng|trực tiếp|google play|postal code|zip code|credit card
bắt đầu|công việc|thông tin|chúng ta|chuyển cảnh|hiệu ứng|thương hiệu|xây dựng|chi tiết|quy trình
tổng hợp|hoàn chỉnh|nốt nhạc|mạng xã|xã hội|ứng dụng|phục vụ|tưởng chừng|lo lắng|tuy nhiên|đặc biệt
thiếu sót|động hóa|động hoá|sound effect|ai editor|bình luận|claude ai|tự xây|cà phê|đồng hồ|thủ công|toàn bộ|bất động|động sản|video trám|cảnh trám|cảnh phụ|quản trị|phát triển|quá trình|tất cả|làm sao|agent editor|tiến bộ|mọi ngày|hôm sau|đi lặp
hoàn toàn|các bạn|a đến|đến z|video thô|đơn giản|tìm hiểu|lĩnh vực
bản đồ|hạ tầng|vị trí|the matrix|matrix one|số 1|lê quang|quang đạo|mễ trì|từ liêm|sân bay|xem qua
""".replace("\n", "|").split("|") if x.strip())
# Da tra gia (khoa hoc Bai 3): dung .split() KHONG doi so la SAI — no tach theo
# MOI khoang trang (ke ca xuong dong), bien "tài khoản|ngân hàng" thanh cac tu
# le "tài", "khoản|ngân", "hàng|hà"... KEEP_PAIRS rong tro (0/44 cap dung), is_pair
# khong bao gio khop -> "tài khoản" van bi tach doi nhu cu du da co logic is_pair.

def chunk_words(words, layout, max_words, max_chars, gap, px_budget,
                char_px, break_punct, keep_pairs=None, tail_fix=True, soft_break=True):
    chunks = []
    cur = []
    reasons = []
    keep_pairs = KEEP_PAIRS if keep_pairs is None else keep_pairs

    def is_pair(a, b):
        return (a["w"].rstrip(u".,!?…:;").lower() + " " + b["w"].rstrip(u".,!?…:;").lower()) in keep_pairs

    def flush(reason):
        if not cur:
            return
        start = cur[0]["start"]
        y = layout.y_at(start)
        end = max(w["end"] for w in cur)
        cut = layout.next_change(start, y)
        clamped = snapped = False
        if cut is not None and end > cut:
            if cut - start < MIN_CHUNK_DUR:
                # Cum nay gan nhu nam tron ben kia ranh gioi. Cat ngan no chi
                # con vai frame se thanh cai nhay nhay. Cho no luon y cua doan
                # SAU ranh gioi va giu nguyen do dai — dung cho hon la de sai
                # cho gan nua giay.
                y = layout.y_at(cut + 1e-6)
                snapped = True
            else:
                end = cut
                clamped = True
        chunks.append({"words": [dict(w) for w in cur],
                       "start": start, "end": round(end, 3),
                       "y": y, "clamped_to_boundary": clamped,
                       "snapped_to_next_zone": snapped,
                       "break_reason": reason})
        reasons.append(reason)
        del cur[:]

    for w in words:
        if cur:
            y_cur = layout.y_at(cur[0]["start"])
            y_new = layout.y_at(w["start"])
            text_try = " ".join(x["w"] for x in cur + [w])
            why = None
            if y_new != y_cur:
                # LUAT CUNG: khong bao gio de 1 cum vat qua ranh vung an toan.
                # Neu vat, cum se giu y cua doan truoc va co the de len mat.
                why = "ranh vung an toan (y %d -> %d)" % (y_cur, y_new)
            elif w["start"] - cur[-1]["end"] >= gap:
                why = "khoang nghi %.2fs" % (w["start"] - cur[-1]["end"])
            elif len(cur) + 1 > max_words:
                why = "du %d tu" % max_words
            elif len(text_try) > max_chars:
                why = "du %d ky tu" % max_chars
            elif char_px and len(text_try) * char_px > px_budget:
                why = "uoc rong %d px > %d px" % (
                    int(len(text_try) * char_px), px_budget)
            elif break_punct and cur[-1]["w"][-1:] in END_PUNCT:
                why = "het cau"
            elif (soft_break and break_punct and cur[-1]["w"][-1:] in SOFT_PUNCT
                  and len(cur) >= 2):
                why = "dau phay"
            if why and tail_fix:
                # (1) Tu ke tiep KET CAU va them no chi vuot tran 1 tu / vai ky tu:
                #     cho no vao luon, con hon de 1 tu moi coi hien 3-5 frame roi tat.
                #     Da tra gia (Bai 3): 21 cum 1 tu hien 0.08-0.24 s ("này.", "bị.").
                last_of_sentence = w["w"][-1:] in END_PUNCT
                if (why.startswith(("du ", "uoc rong")) and last_of_sentence
                        and len(cur) + 1 <= max_words + 1
                        and len(text_try) <= max_chars + 8
                        and (not char_px or len(text_try) * char_px <= px_budget * 1.08)):
                    why = None
                # (2) Diem cat rơi GIUA mot cap tu ghep: keo tu dau cua cap sang cum sau.
                #     Ap dung cho MOI ly do cat (du tu, khoang nghi, het cau...) — da
                #     tra gia: "tài | khoản", "Hà | Nội" hay bi "khoang nghi" (Whisper
                #     danh dau mot khoang lang ngan GIUA hai am tiet cua CUNG mot tu/
                #     cum tu) cat doi, khong chi khi vua tran do dai.
                elif cur and is_pair(cur[-1], w):
                    moved = cur.pop()
                    flush(why + " (giu cap '%s %s')" % (moved["w"], w["w"]))
                    cur.append(moved)
                    why = None
            if why:
                flush(why)
        cur.append(w)
    flush("het transcript")
    return chunks


def wrap_breaks(ws, char_px, budget, max_lines, keep_pairs):
    """Chỉ số từ mà SAU nó xuống dòng, để khối vừa bề rộng. Ưu tiên 2 dòng dài gần bằng nhau, không tách cặp từ
    ghép, ưu tiên ngắt sau dấu phẩy. Ước theo px/ký tự đã đo bằng libass."""
    t = [disp_word(w["w"]) for w in ws]
    n = len(t)

    def wid(lo, hi):
        return len(" ".join(t[lo:hi])) * char_px

    if n < 2 or wid(0, n) <= budget:
        return []

    def pair(k):
        a_ = ws[k - 1]["w"].rstrip(u".,!?…:;").lower()
        b_ = ws[k]["w"].rstrip(u".,!?…:;").lower()
        return (a_ + " " + b_) in keep_pairs

    best = None
    for k in range(1, n):
        w1, w2 = wid(0, k), wid(k, n)
        if w1 <= budget and w2 <= budget:
            sc = abs(w1 - w2) + (10 * budget if pair(k) else 0) - (0.15 * budget if ws[k - 1]["w"][-1:] == "," else 0)
            if best is None or sc < best[0]:
                best = (sc, k)
    if best is not None or max_lines < 3:
        return [best[1] - 1] if best is not None else [max(0, n // 2 - 1)]
    out, lo = [], 0                                  # 3+ dòng: tham lam
    for k in range(1, n + 1):
        if k == n or wid(lo, k + 1) > budget:
            if k < n:
                out.append(k - 1)
            lo = k
    return out


def karaoke_events(chunk, base_c, active_c, video_w, mode="highlight"):
    """Moi TU mot dong Dialogue; ca dong cho ca cum.
    highlight: ca cum hien san mau thuong, tu dang doc doi mau.
    reveal   : (yeu cau chu du an 02/10/2026 'noi chu nao hien chu do') chu DA noi hien mau active, chu CHUA noi
               trong suot {\\alpha&HFF&} nhung VAN GIU CHO -> dong khong xo khi chu moi hien ra."""
    ws = chunk["words"]
    if mode == "reveal":
        ev = []
        for i, w in enumerate(ws):
            start = chunk["start"] if i == 0 else max(w["start"], chunk["start"])
            end = max(ws[i + 1]["start"], start + 0.04) if i + 1 < len(ws) else chunk["end"]
            end = min(end, chunk["end"])
            if end <= start + 1e-4:
                continue
            # khối nhiều dòng: xuống dòng (\N) đặt CỐ ĐỊNH sau các từ trong chunk['breaks'] -> chữ hiện dần không
            # làm khối nhảy dòng
            brk = set(chunk.get("breaks") or [])

            def join(lo, hi):
                out = ""
                for j in range(lo, hi):
                    out += ass_escape(disp_word(ws[j]["w"]))
                    if j + 1 < len(ws):
                        out += "\\N" if j in brk else " "
                return out
            shown = join(0, i + 1)
            hidden = join(i + 1, len(ws))
            txt = "{\\c%s}%s" % (active_c, shown) + ("{\\alpha&HFF&}%s" % hidden if hidden else "")
            ev.append({"start": round(start, 3), "end": round(end, 3), "y": chunk["y"], "active": i,
                       "text": "{\\an2\\pos(%d,%d)}%s" % (video_w // 2, chunk["y"], txt)})
        return ev
    ev = []
    for i, w in enumerate(ws):
        start = max(w["start"], chunk["start"])
        if i + 1 < len(ws):
            end = max(ws[i + 1]["start"], start + 0.04)
        else:
            end = chunk["end"]
        end = min(end, chunk["end"])
        if end <= start + 1e-4:
            continue
        parts = []
        for j, x in enumerate(ws):
            t = ass_escape(disp_word(x["w"]))
            if j == i:
                parts.append("{\\c%s}%s{\\c%s}" % (active_c, t, base_c))
            else:
                parts.append(t)
        ev.append({"start": round(start, 3), "end": round(end, 3),
                   "y": chunk["y"], "active": i,
                   "text": "{\\an2\\pos(%d,%d)}%s"
                           % (video_w // 2, chunk["y"], " ".join(parts))})
    return ev


ASS_HEADER = u"""[Script Info]
; sinh boi nns-auto-sub
ScriptType: v4.00+
PlayResX: %(w)d
PlayResY: %(h)d
WrapStyle: 2
ScaledBorderAndShadow: yes
YCbCr Matrix: None

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Sub,%(family)s,%(size)d,%(base)s,%(base)s,%(outline_c)s,%(shadow_c)s,%(bold)d,0,0,0,100,100,%(spacing).1f,0,1,%(outline).1f,%(shadow).1f,2,%(margin)d,%(margin)d,%(margin)d,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Text
"""


def main():
    C.setup_stdout()
    ap = argparse.ArgumentParser()
    ap.add_argument("--video")
    ap.add_argument("--out")
    ap.add_argument("--resources")
    ap.add_argument("--font", help="chi dinh thang 1 file .ttf/.otf")
    ap.add_argument("--max-words", type=int, default=4)
    ap.add_argument("--max-chars", type=int, default=22)
    ap.add_argument("--gap", type=float, default=0.35,
                    help="khoang nghi (giay) thi tach cum")
    ap.add_argument("--y", type=int, default=None,
                    help="vi tri DAY cua khoi chu, tinh bang pixel (mac dinh 0.80*cao)")
    ap.add_argument("--safe", default=None,
                    help='doi cho theo doan: "0-12:1100,12-30:1536"')
    ap.add_argument("--font-size", type=int, default=None,
                    help="mac dinh = cao_video/24")
    ap.add_argument("--outline", type=float, default=None,
                    help="do day vien, mac dinh = 0.09*co chu")
    ap.add_argument("--shadow", type=float, default=0.0)
    ap.add_argument("--spacing", type=float, default=0.0)
    ap.add_argument("--margin", type=int, default=None,
                    help="le trai/phai, mac dinh 0.06*rong")
    ap.add_argument("--base-color", default="#FFFFFF")
    ap.add_argument("--active-color", default="#FFD600")
    ap.add_argument("--outline-color", default="#000000")
    ap.add_argument("--no-break-punct", action="store_true",
                    help="khong tach cum o dau cau / dau phay")
    ap.add_argument("--no-measure", action="store_true",
                    help="bo buoc do be rong chu bang libass (nhanh hon, kem chac)")
    ap.add_argument("--keep-pairs", dest="keep_pairs", default=None,
                    help="file txt, moi dong 1 cap tu (thuong) khong duoc tach qua 2 cum, bo sung cho KEEP_PAIRS")
    ap.add_argument("--no-tail-fix", dest="no_tail_fix", action="store_true",
                    help="tat luat: cho tu ket cau vao cum dang day (tranh cum 1 tu 3-5 frame) va giu cap tu ghep")
    ap.add_argument("--mode", choices=("highlight", "reveal"), default="highlight",
                    help="highlight: ca cum hien, tu dang doc doi mau | reveal: noi toi chu nao chu do moi hien")
    ap.add_argument("--block", choices=("chunk", "sentence"), default="chunk",
                    help="chunk: cum 3-4 tu thay nhau | sentence: moi khoi la 1 CAU, chu cong don toi het cau moi tat")
    ap.add_argument("--max-lines", type=int, default=2, help="--block sentence: so dong toi da cua 1 khoi")
    ap.add_argument("--block-gap", type=float, default=0.8,
                    help="--block sentence: nghi lau hon nay (giay) trong cau thi moi tach khoi")
    ap.add_argument("--hold", type=float, default=0.4,
                    help="--block sentence: giu khoi them bao lau sau khi noi xong (khong de khoi sau)")
    ap.add_argument("--cta", default=None,
                    help='the CTA to giua man hinh, vd "QUAN TÂM": hien tu luc noi tu goi (comment/binh luan) truoc '
                         'lan nhac CUOI cua chu do, giu toi het video')
    ap.add_argument("--cta-label", default="COMMENT", help="dong nho phia tren the CTA ('' = khong co)")
    ap.add_argument("--cta-y", type=int, default=None, help="tam doc the CTA, px (mac dinh 0.50*cao)")
    ap.add_argument("--cta-anchor", default="comment,bình luận,còm men,cmt",
                    help="tu goi CTA - the hien tu luc noi tu nay (lan cuoi, trong 6 s truoc chu CTA)")
    ap.add_argument("--cta-box", default="#FFD600", help="mau hop the CTA")
    ap.add_argument("--cta-text-color", default="#111111")
    ap.add_argument("--skip", default=None,
                    help='KHONG dat sub trong cac doan giay nay, vd "29.767-50.533" (doan phat video khac). '
                         'Tu co TAM nam trong doan bi bo.')
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    C.require_video_out(a, "build_ass.py")

    info = C.probe_video(a.video)
    W, H = info["width"], info["height"]

    src = C.side_path(a.out, ".fixed.json")
    if not os.path.isfile(src):
        alt = C.side_path(a.out, ".words.json")
        if os.path.isfile(alt):
            src = alt
        else:
            C.die("chua co transcript. Chay 2 buoc truoc:\n"
                  '      python scripts/transcribe.py --video "%s" --out "%s"\n'
                  '      python scripts/fix_tokens.py --video "%s" --out "%s"'
                  % (a.video, a.out, a.video, a.out))
    data = C.read_json(src)
    words = [w for w in data["words"] if w.get("w")]
    # RANH CÂU: Whisper có ranh câu ở segments nhưng KHÔNG chấm câu vào từ -> cụm vắt 2 câu ('vấn đề này Thì',
    # 'cả Nhanh hay không' - Chensub 02/10; trước đó done_2/done_3 phải vá tay). Bơm dấu chấm vào từ cuối mỗi
    # segment (biên phải MỞ: từ có start == seg.end là từ ĐẦU câu sau) để luật tách ở dấu câu cắt cụm tại đó.
    # Dấu câu KHÔNG hiện trên màn hình - xem disp_word().
    n_sent = 0
    for sg in data.get("segments") or []:
        inside = [w for w in words if sg["start"] <= w["start"] < sg["end"]]
        if inside and inside[-1]["w"][-1:] not in END_PUNCT:
            inside[-1]["w"] = inside[-1]["w"].rstrip(u",;:") + u"."
            n_sent += 1
    if n_sent:
        print("  ranh cau: bom dau cham vao %d tu cuoi segment (dau cau khong hien len sub)" % n_sent)
    skips = []
    if a.skip:
        for part in a.skip.split(","):
            try:
                s0, s1 = [float(x) for x in part.strip().split("-")]
            except Exception:
                C.die("--skip '%s' khong hieu. Dang dung: \"29.767-50.533,70-80\" (giay)" % part)
            if s1 <= s0:
                C.die("--skip '%s': giay ket thuc phai lon hon giay bat dau" % part)
            skips.append((s0, s1))
        before = len(words)
        dropped = [w for w in words if any(s0 <= (w["start"] + w["end"]) / 2 < s1 for s0, s1 in skips)]
        words = [w for w in words if not any(s0 <= (w["start"] + w["end"]) / 2 < s1 for s0, s1 in skips)]
        print("  --skip: bo %d/%d tu nam trong %s (vd: %s)"
              % (before - len(words), before, ", ".join("%.2f-%.2fs" % s for s in skips),
                 " ".join(w["w"] for w in dropped[:8])))
    if not words:
        C.die("transcript khong co tu nao: %s" % src)

    font = C.resolve_font(a.resources, a.font)
    if not font["file"]:
        C.die("khong co font tieng Viet dung duoc.\n"
              '  Chay:  python scripts/preflight.py --video "%s"%s\n'
              "  roi lam theo huong dan no in ra."
              % (a.video, ' --resources "%s"' % a.resources if a.resources else ""))
    if font.get("resources_unused"):
        # KHONG lang le doi sang font kem san khi nguoi dung da chi --resources
        C.die("thu muc --resources ban dua khong co font tieng Viet nao dung duoc.\n"
              + "\n".join("  " + ln
                          for ln in C.huong_dan_font_resources(font)))

    size = a.font_size or max(24, int(round(H / 24.0)))
    outline = a.outline if a.outline is not None else max(3.0, round(size * 0.09, 1))
    margin = a.margin if a.margin is not None else int(round(W * 0.06))
    y_def = a.y if a.y is not None else int(round(H * 0.80))
    if not (0 <= y_def <= H):
        C.die("--y %d nam ngoai khung cao %d px" % (y_def, H))
    base_c = to_ass_color(a.base_color, "--base-color")
    act_c = to_ass_color(a.active_color, "--active-color")
    out_c = to_ass_color(a.outline_color, "--outline-color")

    layout = Layout(parse_safe(a.safe, H), y_def)
    px_budget = W - 2 * margin

    print("")
    print("  " + C.hr("-"))
    print("  BUOC 3/4 — gom cum va xuat file .ass")
    print("  " + C.hr("-"))
    print("  video     : %dx%d %.4gfps %.2fs" % (W, H, info["fps"], info["duration"]))
    print("  transcript: %s (%d tu)" % (os.path.basename(src), len(words)))
    print("  font      : %s" % font["file"])
    print('  ten ho ASS: "%s"  (Bold=%d, co chu %d px, vien %.1f px)'
          % (font["family"], font["bold"], size, outline))
    print("  mau       : thuong %s / dang doc %s / vien %s"
          % (base_c, act_c, out_c))
    print("  cho dat   : y=%d px (day khoi chu), le %d px, be rong dung duoc %d px"
          % (y_def, margin, px_budget))
    if layout.safe:
        for s0, s1, yy in layout.safe:
            print("              vung an toan %.2fs-%.2fs -> y=%d" % (s0, s1, yy))
    else:
        print("              (khong dat --safe: dung 1 cho cho ca video)")

    char_px = None
    if not a.no_measure:
        char_px, calib = calibrate_char_px(font["file"], font["family"],
                                          font["bold"], size)
        print("  do that    : chuoi mau %d ky tu rong %d px -> %.1f px/ky tu"
              % (len(CALIB_TEXT), calib["w"], char_px))

    keep_pairs = set(KEEP_PAIRS)
    if a.keep_pairs:
        for ln in io.open(a.keep_pairs, encoding="utf-8"):
            ln = ln.strip().lower()
            if ln and not ln.startswith("#"):
                keep_pairs.add(ln)
    if a.block == "sentence":
        # KHỐI THEO CÂU (chủ dự án 02/10: 'chữ đã ra rồi thì không mất, nói xong cả đoạn đó thì mới mất'):
        # một khối = một câu, tối đa --max-lines dòng; chỉ tách câu khi quá dài; không tách ở dấu phẩy;
        # khoảng nghỉ trong câu phải dài hơn --block-gap mới tách.
        cpx = char_px or (size * 0.35)
        line_chars = max(8, int(px_budget / cpx))
        chunks = chunk_words(words, layout, 999, line_chars * a.max_lines - 2, a.block_gap,
                             px_budget * a.max_lines * 0.92, char_px, not a.no_break_punct,
                             keep_pairs=keep_pairs, tail_fix=not a.no_tail_fix, soft_break=False)
        # câu dài bị tách thì chia lại cho CÂN: không để khối sau chỉ còn 1-2 chữ ('… có thể edit | được video.')
        cap_chars = line_chars * a.max_lines - 2
        for i in range(len(chunks) - 1):
            A, B = chunks[i], chunks[i + 1]
            if A["words"][-1]["w"][-1:] in END_PUNCT or A["y"] != B["y"] \
                    or B["start"] - A["words"][-1]["end"] >= a.block_gap:
                continue
            ta = len(" ".join(disp_word(w["w"]) for w in A["words"]))
            tb = len(" ".join(disp_word(w["w"]) for w in B["words"]))
            if tb >= 0.35 * (ta + tb):
                continue
            allw = A["words"] + B["words"]
            best = None
            for k in range(1, len(allw)):
                l1 = len(" ".join(disp_word(w["w"]) for w in allw[:k]))
                l2 = len(" ".join(disp_word(w["w"]) for w in allw[k:]))
                if l1 > cap_chars or l2 > cap_chars:
                    continue
                pr = (allw[k - 1]["w"].rstrip(u".,!?…:;").lower() + " "
                      + allw[k]["w"].rstrip(u".,!?…:;").lower()) in keep_pairs
                sc = abs(l1 - l2) + (100 if pr else 0) - (6 if allw[k - 1]["w"][-1:] == "," else 0)
                if best is None or sc < best[0]:
                    best = (sc, k)
            if best:
                k = best[1]
                A["words"], B["words"] = allw[:k], allw[k:]
                A["end"] = round(max(w["end"] for w in A["words"]), 3)
                B["start"] = B["words"][0]["start"]
                B["end"] = round(max(w["end"] for w in B["words"]), 3)
                A["break_reason"] = "chia lai cau cho can"
        for c, nx in zip(chunks, chunks[1:] + [None]):
            c["breaks"] = wrap_breaks(c["words"], cpx, px_budget, a.max_lines, keep_pairs)
            # giữ khối thêm --hold giây sau khi nói xong (không đè khối sau, không vắt ranh --safe / --skip)
            lim = nx["start"] - 0.02 if nx else info["duration"]
            cut = layout.next_change(c["start"], c["y"])
            if cut is not None:
                lim = min(lim, cut)
            for s0, s1 in skips:
                if c["start"] < s0:
                    lim = min(lim, s0)
            c["end"] = round(max(c["end"], min(lim, c["end"] + a.hold)), 3)
    else:
        chunks = chunk_words(words, layout, a.max_words, a.max_chars, a.gap,
                             px_budget, char_px, not a.no_break_punct,
                             keep_pairs=keep_pairs, tail_fix=not a.no_tail_fix)

    def lines_of(c):
        brk = set(c.get("breaks") or [])
        out, cur = [], []
        for j, w in enumerate(c["words"]):
            cur.append(disp_word(w["w"]))
            if j in brk:
                out.append(" ".join(cur))
                cur = []
        if cur:
            out.append(" ".join(cur))
        return out

    # do THAT be rong 3 DONG dai nhat -> khong tin uoc luong
    all_lines = [ln for c in chunks for ln in lines_of(c)]
    widest = sorted(all_lines, key=lambda t: -len(t))[:3]
    over = []
    if not a.no_measure:
        print("")
        print("  do be rong THAT cua 3 dong dai nhat:")
        for txt in widest:
            px = measure_text_px(txt, font["file"], font["family"],
                                 font["bold"], size)
            flag = "OK" if px <= px_budget else "TRAN LE"
            if px > px_budget:
                over.append((txt, px))
            print('      "%s"  = %d px  (%s)' % (txt, px, flag))

    events = []
    for c in chunks:
        events.extend(karaoke_events(c, base_c, act_c, W, a.mode))
    # luoi an toan: khong cum nao duoc cham vao doan --skip
    for s0, s1 in skips:
        bad = [c for c in chunks if c["start"] < s1 and c["end"] > s0]
        if bad:
            C.die("co %d cum cham vao doan --skip %.2f-%.2fs: %s" % (len(bad), s0, s1,
                  " | ".join(" ".join(w["w"] for w in c["words"]) for c in bad[:3])))

    print("")
    print("  ket qua: %d cum, %d dong Dialogue (1 dong / 1 tu dang doc)"
          % (len(chunks), len(events)))
    clamped = [c for c in chunks if c["clamped_to_boundary"]]
    if clamped:
        print("  co %d cum bi cat ngan tai ranh vung an toan (dung y cu de len mat):"
              % len(clamped))
        for c in clamped[:5]:
            print("      [%6.2f-%6.2f] y=%d  %s"
                  % (c["start"], c["end"], c["y"],
                     " ".join(w["w"] for w in c["words"])))
    snapped = [c for c in chunks if c["snapped_to_next_zone"]]
    if snapped:
        print("  co %d cum qua ngan o cuoi vung nen duoc doi sang y cua vung sau:"
              % len(snapped))
        for c in snapped[:5]:
            print("      [%6.2f-%6.2f] y=%d  %s"
                  % (c["start"], c["end"], c["y"],
                     " ".join(w["w"] for w in c["words"])))
    print("")
    print("  10 cum dau:")
    for c in chunks[:10]:
        print("      [%6.2f-%6.2f] y=%-5d %-26s  (tach vi: %s)"
              % (c["start"], c["end"], c["y"],
                 " ".join(w["w"] for w in c["words"]), c["break_reason"]))

    if over:
        C.die("co %d cum ve ra rong hon vung dung duoc (%d px).\n"
              "  Giam bot bang 1 trong cac cach:\n"
              "      --max-chars %d      (dang %d)\n"
              "      --max-words %d      (dang %d)\n"
              "      --font-size %d      (dang %d)\n"
              % (len(over), px_budget, max(8, a.max_chars - 4), a.max_chars,
                 max(2, a.max_words - 1), a.max_words, int(size * 0.85), size))

    # THẺ CTA (chủ dự án 02/10: 'tôi nói comment Quan tâm thì chữ Quan tâm hiển thị lên màn hình, 1 lúc lâu vào từ
    # lúc nói để người ta biết'): hộp màu + chữ to giữa màn hình, hiện từ lúc nói TỪ GỌI (comment / bình luận) ngay
    # trước lần nhắc CUỐI của chữ CTA, giữ tới hết video.
    cta = None
    if a.cta:
        import unicodedata

        def nrm(s):
            return re.sub(r"[^\w\s]", "", unicodedata.normalize("NFC", s.lower())).strip()

        toks = nrm(a.cta).split()
        hits = [i for i in range(len(words) - len(toks) + 1)
                if [nrm(words[i + j]["w"]) for j in range(len(toks))] == toks]
        if not hits:
            C.die("--cta '%s': khong thay chu nay trong loi noi (ngoai doan --skip). Kiem lai chu." % a.cta)
        ki = hits[-1]
        t_kw = words[ki]["start"]
        t0 = t_kw
        anchors = [nrm(x).split() for x in a.cta_anchor.split(",") if x.strip()]
        for i in range(ki - 1, -1, -1):
            if t_kw - words[i]["start"] > 6.0:
                break
            if any([nrm(words[i + j]["w"]) for j in range(len(at)) if i + j < len(words)] == at for at in anchors):
                t0 = words[i]["start"]
                break
        t1 = info["duration"]
        for s0, s1 in skips:
            if t0 < s0 < t1:
                t1 = s0
        big = int(round(size * 1.9))
        small = int(round(size * 0.62))
        if not a.no_measure:
            px = measure_text_px(a.cta.upper(), font["file"], font["family"], font["bold"], big)
            while px > px_budget * 0.9 and big > size:
                big = int(big * 0.9)
                px = measure_text_px(a.cta.upper(), font["file"], font["family"], font["bold"], big)
        cy = a.cta_y if a.cta_y is not None else int(round(H * 0.50))
        lab = ("{\\fs%d}%s\\N" % (small, ass_escape(a.cta_label.upper()))) if a.cta_label else ""
        txt = ("{\\an5\\pos(%d,%d)\\fad(120,0)\\fscx70\\fscy70\\t(0,160,\\fscx108\\fscy108)"
               "\\t(160,260,\\fscx100\\fscy100)}" % (W // 2, cy)) + lab + "{\\fs%d}%s" % (big, ass_escape(a.cta.upper()))
        cta = {"text": a.cta.upper(), "label": a.cta_label.upper(), "start": round(t0, 3), "end": round(t1, 3),
               "y": cy, "size": big, "pad": int(round(big * 0.22)), "box": to_ass_color(a.cta_box, "--cta-box"),
               "color": to_ass_color(a.cta_text_color, "--cta-text-color"), "ass_text": txt,
               "keyword_t": round(t_kw, 3)}
        print("  CTA      : '%s' hien %.2f-%.2fs (tu goi luc %.2fs, chu CTA luc %.2fs), tam y=%d, co %d px"
              % (cta["text"], t0, t1, t0, t_kw, cy, big))

    ass_path = C.side_path(a.out, ".ass")
    plan_path = C.side_path(a.out, ".plan.json")
    if a.dry_run:
        print("")
        print("  [dry-run] khong ghi file. Se ghi:")
        print("      %s" % ass_path)
        print("      %s" % plan_path)
        return

    body = [ASS_HEADER % {"w": W, "h": H, "family": font["family"],
                          "size": size, "base": base_c, "outline_c": out_c,
                          "shadow_c": out_c, "bold": font["bold"],
                          "outline": outline, "shadow": a.shadow,
                          "spacing": a.spacing, "margin": margin}]
    if cta:
        # thêm style Cta vào cuối [V4+ Styles]: BorderStyle 3 = hộp đặc màu OutlineColour, Outline = đệm hộp
        st = ("Style: Cta,%s,%d,%s,%s,%s,%s,%d,0,0,0,100,100,0.0,0,3,%d,0,5,%d,%d,0,1\n"
              % (font["family"], cta["size"], cta["color"], cta["color"], cta["box"], cta["box"], font["bold"],
                 cta["pad"], margin, margin))
        body[0] = body[0].replace("\n\n[Events]", "\n" + st + "\n[Events]")
    for e in events:
        body.append("Dialogue: 0,%s,%s,Sub,,0,0,0,%s\n"
                    % (C.ass_time(e["start"]), C.ass_time(e["end"]), e["text"]))
    if cta:
        body.append("Dialogue: 1,%s,%s,Cta,,0,0,0,%s\n"
                    % (C.ass_time(cta["start"]), C.ass_time(cta["end"]), cta["ass_text"]))
    C.write_text(ass_path, "".join(body))

    C.write_json(plan_path, {
        "video": os.path.abspath(a.video), "out": os.path.abspath(a.out),
        "ass": os.path.abspath(ass_path),
        "video_w": W, "video_h": H, "fps": info["fps"],
        "nb_frames": info["nb_frames"],
        "font_file": font["file"], "font_dir": font["dir"],
        "font_family": font["family"], "font_bold": font["bold"],
        "font_size": size, "outline": outline, "margin": margin,
        "default_y": y_def, "safe": layout.safe,
        "base_color": base_c, "active_color": act_c,
        "chunks": chunks, "n_events": len(events) + (1 if cta else 0), "mode": a.mode, "skip": skips,
        "block": a.block, "cta": cta})
    print("")
    print("  da ghi: %s" % ass_path)
    print("  da ghi: %s" % plan_path)


if __name__ == "__main__":
    C.run_main(main)
