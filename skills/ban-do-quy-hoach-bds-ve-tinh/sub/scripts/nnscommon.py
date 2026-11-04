# -*- coding: utf-8 -*-
"""Ham dung chung cho skill nns-auto-sub.

Chi phu thuoc: python3 + numpy + ffmpeg/ffprobe co san trong PATH.
Khong import bat ky module nao ngoai thu muc skill nay.
"""
from __future__ import annotations

import io
import json
import os
import shutil
import struct
import subprocess
import sys
import tempfile

# ----------------------------------------------------------------------------
# console Windows mac dinh cp1252 -> in tieng Viet la crash. Phai bat utf-8.
# ----------------------------------------------------------------------------


def setup_stdout():
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass


def die(msg, code=1):
    """Chet ON AO: in ro loi bang tieng Viet roi exit != 0."""
    setup_stdout()
    print("")
    print("!! LOI: " + str(msg))
    sys.exit(code)


class ThieuThuVien(Exception):
    """Thieu 1 thu vien Python.

    Nem ra o cho SU DUNG (khong phai o dau file) de:
      - preflight bat duoc va in thanh 1 dong THIEU + khoi huong dan,
      - cac script khac bat duoc va in lenh pip install,
    tuc la NGUOI DUNG KHONG BAO GIO thay traceback.
    """

    def __init__(self, lib, why, pip=None):
        self.lib = lib
        self.why = why
        self.pip = pip or lib
        Exception.__init__(self, "thieu thu vien Python: %s" % lib)

    def title(self):
        return "Chua cai thu vien %s (%s)" % (self.lib, self.why)

    def steps(self):
        mod = self.lib.replace("-", "_")
        return ["Chay lenh nay:",
                "    pip install %s" % self.pip,
                "Neu may co nhieu ban Python, dung dung ban dang chay skill nay:",
                "    python -m pip install %s" % self.pip,
                'Kiem lai:  python -c "import %s; print(\'ok\')"' % mod]


class ThieuCongCu(Exception):
    """Thieu 1 cong cu dong lenh (ffmpeg / ffprobe).

    Nem ra tu run() khi Windows/Linux bao "khong tim thay file", de nguoi dung
    thay huong dan cai dat chu KHONG phai traceback cua subprocess.
    """

    WHY = {"ffmpeg": "de ve chu vao video",
           "ffprobe": "de doc thong so video"}

    def __init__(self, exe):
        self.exe = os.path.basename(str(exe))
        Exception.__init__(self, "thieu cong cu: %s" % self.exe)

    def title(self):
        why = self.WHY.get(self.exe.replace(".exe", ""), "de xu ly video")
        return "Chua co %s tren may nay (%s)" % (self.exe, why)

    def steps(self):
        return ['Windows: tai ban "full" tai  https://www.gyan.dev/ffmpeg/builds/',
                "    giai nen ra vd  C:\\ffmpeg  roi them  C:\\ffmpeg\\bin  vao PATH",
                "    (Windows -> Sua bien moi truong -> Path -> New)",
                "macOS:   brew install ffmpeg",
                "Linux:   sudo apt install ffmpeg",
                "Ban ffmpeg PHAI co libass (de ve sub). Ban 'full' o tren co san.",
                "Kiem lai:  ffmpeg -version   va   ffprobe -version"]


def import_numpy():
    """Lay numpy. Thieu thi nem ThieuThuVien (khong de ImportError lot ra)."""
    try:
        import numpy as np
        return np
    except Exception:
        raise ThieuThuVien("numpy", "de do pixel khi kiem font va kiem ket qua")


def die_thieu_lib(exc):
    """In loi thieu thu vien / cong cu bang tieng Viet roi exit 1 — khong traceback."""
    setup_stdout()
    print("")
    print("!! LOI: " + exc.title())
    for line in exc.steps():
        print("   " + line)
    print("")
    sys.exit(1)


def run_main(main_func):
    """Bao boc main(): moi loi thieu thu vien/cong cu thanh huong dan, khong traceback."""
    try:
        main_func()
    except (ThieuThuVien, ThieuCongCu) as exc:
        die_thieu_lib(exc)


def require_video_out(a, script):
    """Bao thieu --video/--out bang TIENG VIET (argparse required=True in tieng Anh)."""
    thieu = []
    if not getattr(a, "video", None):
        thieu.append("--video (video co tieng noi)")
    if not getattr(a, "out", None):
        thieu.append("--out (duong dan file ket qua)")
    if thieu:
        die("thieu tham so bat buoc: %s\n"
            "  Goi lai day du 2 tham so nay:\n"
            '      python scripts/%s --video "D:\\quay\\video_tho.mp4" '
            '--out "D:\\quay\\video_co_sub.mp4"\n'
            "  (--out la file KET QUA; cac file .words.json / .ass / .plan.json\n"
            "   se nam canh no, cung ten)" % (", ".join(thieu), script))


def read_json(path):
    with io.open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def write_json(path, obj):
    d = os.path.dirname(os.path.abspath(path))
    if d and not os.path.isdir(d):
        os.makedirs(d)
    with io.open(path, "w", encoding="utf-8") as fh:
        json.dump(obj, fh, ensure_ascii=False, indent=2)


def read_text(path):
    with io.open(path, "r", encoding="utf-8") as fh:
        return fh.read()


def write_text(path, text):
    d = os.path.dirname(os.path.abspath(path))
    if d and not os.path.isdir(d):
        os.makedirs(d)
    with io.open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text)


# ----------------------------------------------------------------------------
# duong dan phu tro: moi file trung gian nam CANH --out
# ----------------------------------------------------------------------------

def side_path(out_path, suffix):
    """<out>/../<stem><suffix>  — vd  video_sub.mp4 -> video_sub.words.json"""
    out_path = os.path.abspath(out_path)
    stem = os.path.splitext(os.path.basename(out_path))[0]
    return os.path.join(os.path.dirname(out_path), stem + suffix)


# ----------------------------------------------------------------------------
# ffmpeg / ffprobe
# ----------------------------------------------------------------------------

def which(name):
    return shutil.which(name) or shutil.which(name + ".exe")


def tool_version(name):
    exe = which(name)
    if not exe:
        return None
    try:
        out = subprocess.run([exe, "-version"], capture_output=True, text=True,
                             errors="replace").stdout
        first = (out.splitlines() or [""])[0]
        parts = first.split()
        if len(parts) >= 3:
            return parts[2]
        return first.strip() or "?"
    except Exception:
        return None


def run(cmd, cwd=None, binary=False, check=True, what="lenh ffmpeg"):
    """Chay 1 lenh. binary=True -> tra ve stdout dang bytes."""
    try:
        p = subprocess.run(cmd, cwd=cwd, stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE)
    except FileNotFoundError:
        # KHONG de FileNotFoundError cua subprocess lot ra thanh traceback:
        # tren may moi chua cai ffmpeg thi day la loi dau tien nguoi dung gap.
        raise ThieuCongCu(cmd[0])
    if check and p.returncode != 0:
        err = p.stderr.decode("utf-8", "replace")
        die("%s that bai (exit %d).\n%s" % (what, p.returncode, err[-4000:]))
    if binary:
        return p.stdout, p.stderr.decode("utf-8", "replace"), p.returncode
    return (p.stdout.decode("utf-8", "replace"),
            p.stderr.decode("utf-8", "replace"), p.returncode)


def probe_video(path):
    """Doc thong so video. nb_frames lay tu container; neu thieu thi DEM that."""
    if not os.path.isfile(path):
        die("khong thay file video: %s" % path)
    cmd = ["ffprobe", "-v", "error", "-select_streams", "v:0",
           "-show_entries", "stream=width,height,r_frame_rate,nb_frames,duration",
           "-show_entries", "format=duration", "-of", "json", path]
    out, err, _ = run(cmd, what="ffprobe video")
    try:
        j = json.loads(out)
        st = j["streams"][0]
    except Exception:
        die("ffprobe khong doc duoc stream video trong: %s\n%s" % (path, err[-2000:]))
    num, den = st["r_frame_rate"].split("/")
    fps = float(num) / float(den)
    dur = None
    for src in (st.get("duration"), j.get("format", {}).get("duration")):
        try:
            dur = float(src)
            break
        except (TypeError, ValueError):
            continue
    nbf = st.get("nb_frames")
    try:
        nbf = int(nbf)
    except (TypeError, ValueError):
        nbf = count_frames(path)
    return {
        "path": os.path.abspath(path),
        "width": int(st["width"]),
        "height": int(st["height"]),
        "fps": fps,
        "fps_str": st["r_frame_rate"],
        "nb_frames": nbf,
        "duration": dur if dur is not None else (nbf / fps if fps else 0.0),
    }


def count_frames(path):
    """DEM frame that (khong tin nb_frames cua container)."""
    cmd = ["ffprobe", "-v", "error", "-select_streams", "v:0", "-count_frames",
           "-show_entries", "stream=nb_read_frames", "-of",
           "default=nw=1:nk=1", path]
    out, _, _ = run(cmd, what="ffprobe dem frame")
    out = out.strip().splitlines()
    for line in out:
        line = line.strip()
        if line.isdigit():
            return int(line)
    die("khong dem duoc so frame cua %s" % path)


def audio_duration(path):
    cmd = ["ffprobe", "-v", "error", "-select_streams", "a:0", "-show_entries",
           "stream=duration", "-of", "default=nw=1:nk=1", path]
    out, _, rc = run(cmd, check=False, what="ffprobe audio")
    try:
        return float(out.strip().splitlines()[0])
    except Exception:
        return None


def has_audio(path):
    cmd = ["ffprobe", "-v", "error", "-select_streams", "a", "-show_entries",
           "stream=index", "-of", "default=nw=1:nk=1", path]
    out, _, _ = run(cmd, check=False, what="ffprobe audio")
    return bool(out.strip())


def gray_frame(path, frame_index, width, height, extra_vf=None):
    """Lay DUNG frame so N thanh mang numpy gray (h,w).

    Dung select=eq(n\\,N) chu KHONG dung -ss: da do, -ss nhay sai frame.
    Doi lai: ffmpeg phai decode tuan tu tu dau -> frame cang xa cang lau.
    """
    np = import_numpy()
    vf = "select=eq(n\\,%d)" % int(frame_index)
    if extra_vf:
        vf += "," + extra_vf
    cmd = ["ffmpeg", "-v", "error", "-i", path, "-vf", vf, "-vsync", "0",
           "-frames:v", "1", "-f", "rawvideo", "-pix_fmt", "gray", "-"]
    raw, err, _ = run(cmd, binary=True, what="ffmpeg lay frame %d" % frame_index)
    need = width * height
    if len(raw) < need:
        die("lay frame %d cua %s that bai (nhan %d byte, can %d).\n%s"
            % (frame_index, path, len(raw), need, err[-1500:]))
    return np.frombuffer(raw[:need], dtype=np.uint8).reshape(height, width)


# ----------------------------------------------------------------------------
# doc bang 'name' + 'cmap' trong file TTF/OTF — khong can fontTools
# ----------------------------------------------------------------------------

# ky tu tieng Viet kho nhat: dau + nguyen am rieng cua tieng Viet.
VN_TEST_TEXT = u"Cắt khoảng lặng ậm ừ"
VN_CTRL_TEXT = u"Cat khoang lang am u"      # doi chung, ASCII, cung so ky tu
VN_CODEPOINTS = [
    0x0102, 0x0103,          # A-brave / a-brave
    0x0110, 0x0111,          # D-stroke / d-stroke
    0x01A0, 0x01A1,          # O-horn / o-horn
    0x01AF, 0x01B0,          # U-horn / u-horn
    0x1EA1, 0x1EA3, 0x1EA5,  # a-dot / a-hook / a-circ-acute
    0x1EAD, 0x1EAF, 0x1EB7,  # a-circ-dot / a-brave-acute / a-brave-dot
    0x1EC7, 0x1ED1, 0x1EEB,  # e-circ-dot / o-circ-acute / u-horn-grave
    0x1EF9,                  # y-tilde
]


def _u16(b, o):
    return struct.unpack(">H", b[o:o + 2])[0]


def _i16(b, o):
    return struct.unpack(">h", b[o:o + 2])[0]


def _u32(b, o):
    return struct.unpack(">I", b[o:o + 4])[0]


def _sfnt_tables(data):
    if len(data) < 12:
        raise ValueError("file font qua ngan")
    tag = data[0:4]
    if tag == b"ttcf":
        # TrueType Collection: lay font dau tien
        off = _u32(data, 12)
        return _sfnt_tables_at(data, off)
    return _sfnt_tables_at(data, 0)


def _sfnt_tables_at(data, base):
    num = _u16(data, base + 4)
    tables = {}
    for i in range(num):
        rec = base + 12 + 16 * i
        if rec + 16 > len(data):
            break
        t = data[rec:rec + 4]
        tables[t] = (_u32(data, rec + 8), _u32(data, rec + 12))
    return tables


def font_weight(path):
    """usWeightClass trong bang OS/2 (100..900). None neu font khong co OS/2."""
    with io.open(path, "rb") as fh:
        data = fh.read()
    tables = _sfnt_tables(data)
    if b"OS/2" not in tables:
        return None
    off = tables[b"OS/2"][0]
    return _u16(data, off + 4)


def font_names(path):
    """Tra ve ten cua font, KEM ten se dat vao Style Fontname cua ASS.

    !!! DA DO TREN MAY THAT — DUNG SUA THANH nameID 16 !!!
    libass khop font theo nameID 1 (ten ho "RIBBI", vd 'Be Vietnam Pro ExtraBold'),
    KHONG theo nameID 16 (ten ho kieu chu, vd 'Be Vietnam Pro').
    Dat nameID 16 vao Style Fontname thi libass IM LANG bo file .ttf trong
    fontsdir va ve bang font he thong — chu van co dau, van dep, nen rat de
    tuong la da chay dung. Do duoc: ExtraBold + 'Be Vietnam Pro' cho ra dung
    15249 pixel = y hệt khi fontsdir RONG; con + 'Be Vietnam Pro ExtraBold'
    cho 14560 pixel (dung font that).
    """
    with io.open(path, "rb") as fh:
        data = fh.read()
    try:
        tables = _sfnt_tables(data)
    except Exception as exc:
        raise ValueError("khong doc duoc header font: %s" % exc)
    if b"name" not in tables:
        raise ValueError("font khong co bang 'name'")
    off, _ln = tables[b"name"]
    count = _u16(data, off + 2)
    str_off = off + _u16(data, off + 4)
    picked = {}
    for i in range(count):
        rec = off + 6 + 12 * i
        pid = _u16(data, rec)
        eid = _u16(data, rec + 2)
        nid = _u16(data, rec + 6)
        ln = _u16(data, rec + 8)
        so = _u16(data, rec + 10)
        if nid not in (1, 2, 4, 16, 17):
            continue
        raw = data[str_off + so: str_off + so + ln]
        try:
            if pid == 3 or (pid == 0 and eid in (3, 4, 5, 6)):
                val = raw.decode("utf-16-be", "strict")
            elif pid == 1:
                val = raw.decode("mac-roman", "strict")
            else:
                val = raw.decode("utf-16-be", "strict")
        except Exception:
            continue
        val = val.strip()
        if not val:
            continue
        # uu tien ban Windows/unicode (pid==3) neu co nhieu ban
        if nid not in picked or pid == 3:
            picked[nid] = val
    fam = picked.get(1) or picked.get(16)
    if not fam:
        raise ValueError("font khong khai bao ten ho (nameID 1/16)")
    return {
        "family": picked.get(1) or fam,
        "typo_family": picked.get(16),
        "ass_family": fam,          # <- nameID 1. Ten dat vao Style Fontname.
        "subfamily": picked.get(2) or "",
        "typo_subfamily": picked.get(17) or "",
        "full": picked.get(4) or "",
    }


class _Cmap(object):
    """Tra loi 1 cau hoi duy nhat: codepoint nay co glyph THAT trong font khong."""

    def __init__(self, data, off):
        self.data = data
        self.kind = None
        self.off = None
        best = None
        n = _u16(data, off + 2)
        for i in range(n):
            rec = off + 4 + 8 * i
            pid = _u16(data, rec)
            eid = _u16(data, rec + 2)
            sub = off + _u32(data, rec + 4)
            fmt = _u16(data, sub)
            score = -1
            if pid == 3 and eid == 10 and fmt == 12:
                score = 4
            elif pid == 0 and eid in (4, 6) and fmt == 12:
                score = 3
            elif pid == 3 and eid == 1 and fmt == 4:
                score = 2
            elif pid == 0 and fmt == 4:
                score = 1
            if score > 0 and (best is None or score > best[0]):
                best = (score, fmt, sub)
        if best is None:
            raise ValueError("font khong co cmap unicode (format 4 hay 12)")
        _s, self.kind, self.off = best

    def gid(self, cp):
        d, o = self.data, self.off
        if self.kind == 12:
            ngroups = _u32(d, o + 12)
            lo, hi = 0, ngroups - 1
            while lo <= hi:
                mid = (lo + hi) // 2
                g = o + 16 + 12 * mid
                start, end = _u32(d, g), _u32(d, g + 4)
                if cp < start:
                    hi = mid - 1
                elif cp > end:
                    lo = mid + 1
                else:
                    return _u32(d, g + 8) + (cp - start)
            return 0
        # format 4
        if cp > 0xFFFF:
            return 0
        seg2 = _u16(d, o + 6)
        seg = seg2 // 2
        end_o = o + 14
        start_o = end_o + seg2 + 2
        delta_o = start_o + seg2
        range_o = delta_o + seg2
        for i in range(seg):
            if _u16(d, end_o + 2 * i) >= cp:
                start = _u16(d, start_o + 2 * i)
                if start > cp:
                    return 0
                ro = _u16(d, range_o + 2 * i)
                if ro == 0:
                    return (cp + _i16(d, delta_o + 2 * i)) & 0xFFFF
                addr = range_o + 2 * i + ro + 2 * (cp - start)
                if addr + 2 > len(d):
                    return 0
                g = _u16(d, addr)
                if g == 0:
                    return 0
                return (g + _i16(d, delta_o + 2 * i)) & 0xFFFF
        return 0


def font_missing_codepoints(path, codepoints=None):
    """Liet ke codepoint tieng Viet MA FONT KHONG CO. [] = du glyph."""
    codepoints = codepoints or VN_CODEPOINTS
    with io.open(path, "rb") as fh:
        data = fh.read()
    tables = _sfnt_tables(data)
    if b"cmap" not in tables:
        raise ValueError("font khong co bang 'cmap'")
    cm = _Cmap(data, tables[b"cmap"][0])
    return [cp for cp in codepoints if cm.gid(cp) == 0]


# ----------------------------------------------------------------------------
# do PIXEL that: render chu qua ffmpeg+libass roi dem muc in
# ----------------------------------------------------------------------------

PROBE_W, PROBE_H, PROBE_SIZE = 1280, 300, 90
FAKE_FAMILY = "ZzzNnsNoSuchFamily991"   # ten ho chac chan khong ton tai


def probe_ass(text, family, bold=0, size=PROBE_SIZE, w=PROBE_W, h=PROBE_H):
    return (
        "[Script Info]\n"
        "ScriptType: v4.00+\n"
        "PlayResX: %d\nPlayResY: %d\n"
        "WrapStyle: 2\nScaledBorderAndShadow: yes\n\n"
        "[V4+ Styles]\n"
        "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, "
        "OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, "
        "ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, "
        "MarginL, MarginR, MarginV, Encoding\n"
        "Style: P,%s,%d,&H00FFFFFF,&H00FFFFFF,&H00FFFFFF,&H00FFFFFF,"
        "%d,0,0,0,100,100,0,0,1,0,0,5,0,0,0,1\n\n"
        "[Events]\n"
        "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Text\n"
        "Dialogue: 0,0:00:00.00,0:00:10.00,P,,0,0,0,{\\pos(%d,%d)}%s\n"
        % (w, h, family, size, bold, w // 2, h // 2, text)
    )


def render_ink(text, font_file, family, bold=0, size=PROBE_SIZE,
               w=PROBE_W, h=PROBE_H):
    """Render `text` (trang tren den) qua ffmpeg+libass, DEM pixel co muc.

    Ky thuat da kiem: subtitles=<file>.ass:fontsdir=<dir chua .ttf>.
    Hai chi tiet quan trong:
      - KHONG dat duong dan tuyet doi vao filter (dau ':' cua 'C:/' lam ffmpeg
        hieu la dau phan cach option) -> chay ffmpeg voi cwd la thu muc tam,
        dung ten file tuong doi.
      - .ass phai nam NGOAI fontsdir, vi libass thu nap MOI file trong fontsdir
        nhu font va in "Error opening memory font 'probe.ass'".
    font_file=None -> fontsdir rong, dung de lay CHU KY FALLBACK.
    """
    np = import_numpy()
    tmp = tempfile.mkdtemp(prefix="nnsfont_")
    try:
        fdir = os.path.join(tmp, "fonts")
        os.makedirs(fdir)
        if font_file:
            shutil.copy2(font_file, os.path.join(fdir, os.path.basename(font_file)))
        write_text(os.path.join(tmp, "probe.ass"),
                   probe_ass(text, family, bold, size, w, h))
        cmd = ["ffmpeg", "-v", "info", "-f", "lavfi", "-i",
               "color=c=black:s=%dx%d:d=1:r=1" % (w, h),
               "-vf", "subtitles=probe.ass:fontsdir=fonts",
               "-frames:v", "1", "-f", "rawvideo", "-pix_fmt", "gray", "-"]
        raw, err, rc = run(cmd, cwd=tmp, binary=True, check=False)
        need = w * h
        if rc != 0 or len(raw) < need:
            die("render thu font that bai (ffmpeg exit %d).\n%s"
                % (rc, err[-2500:]))
        img = np.frombuffer(raw[:need], dtype=np.uint8).reshape(h, w)
        mask = img > 40
        ink = int(mask.sum())
        cols = np.where(mask.any(axis=0))[0]
        rows = np.where(mask.any(axis=1))[0]
        box = ((int(cols[0]), int(rows[0]), int(cols[-1]), int(rows[-1]))
               if len(cols) and len(rows) else (0, 0, 0, 0))
        return {"ink": ink, "box": box,
                "w": box[2] - box[0] + 1 if ink else 0,
                "h": box[3] - box[1] + 1 if ink else 0,
                "log": err}
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


# Nguong DA HIEU CHUAN tren may nay, 9 do day cua Be Vietnam Pro
# (chi tiet so lieu: references/font-tieng-viet.md)
#   ink_vn / ink_ascii : do duoc 1.050 .. 1.095   (font bo dau -> 1.00)
#   cao_vn / cao_ascii : do duoc 1.136 .. 1.259   (font bo dau -> 1.00)
INK_RATIO_MIN = 1.02
INK_RATIO_MAX = 1.45      # tren nguong nay = dang ve o vuong tofu
HEIGHT_RATIO_MIN = 1.08   # chu co dau BAT BUOC cao hon chu khong dau


def ass_bold_for(weight):
    """Style Bold nen la 0 hay 1 voi font co usWeightClass=weight.

    Font da day (>=600) thi de Bold=0: libass lay dung mat chu day do.
    Dat Bold=1 len font day se doi mat chu (hoac tuot ve font he thong).
    Font nhe thi Bold=1 de libass lam dam (hoac lay mat Bold cung ho).
    """
    return 0 if (weight or 400) >= 600 else 1


def check_font_vietnamese(font_file, family, bold=None, weight=None):
    """Font nay co ve duoc tieng Viet co dau THAT khong — 3 lop doc lap.

    lop 1 CMAP     : doc thang bang cmap trong file, xem co codepoint hay khong
    lop 2 FALLBACK : render bang font nay, roi render lai voi fontsdir RONG +
                     ten ho bia. Neu HAI ban giong nhau tung pixel -> libass
                     KHONG dung file font cua ta, no ve bang font he thong.
                     Day la lop bat duoc loi 'ten ho sai' — loi im lang nhat.
    lop 3 DAU      : so muc in va chieu cao giua ban CO DAU va ban KHONG DAU.
                     Font bo dau cho ty le ~1.00; font ve tofu cho ty le rat cao.
    """
    if weight is None:
        try:
            weight = font_weight(font_file)
        except Exception:
            weight = None
    if bold is None:
        bold = ass_bold_for(weight)
    res = {"font": font_file, "family": family, "weight": weight, "bold": bold,
           "ok": False, "reasons": [], "missing": None, "ink_vn": 0,
           "ink_ascii": 0, "ink_fallback": 0, "ratio": 0.0, "h_ratio": 0.0,
           "used_our_font": False}

    # --- lop 1: cmap ---
    try:
        missing = font_missing_codepoints(font_file)
    except Exception as exc:
        res["reasons"].append("khong doc duoc bang cmap: %s" % exc)
        return res
    res["missing"] = missing
    if missing:
        res["reasons"].append(
            "file font thieu %d/%d ky tu tieng Viet (vd U+%04X)"
            % (len(missing), len(VN_CODEPOINTS), missing[0]))
        return res

    # --- lop 2: chu ky fallback ---
    vn = render_ink(VN_TEST_TEXT, font_file, family, bold)
    fb = render_ink(VN_TEST_TEXT, None, FAKE_FAMILY, bold)
    res["ink_vn"], res["ink_fallback"] = vn["ink"], fb["ink"]
    if vn["ink"] <= 0:
        res["reasons"].append("libass khong ve ra pixel nao ca")
        return res
    if vn["ink"] == fb["ink"] and vn["box"] == fb["box"]:
        res["reasons"].append(
            "libass KHONG dung file font nay (ve ra y het khi khong co font: "
            "%d pixel, cung khung %s) -> ten ho '%s' sai"
            % (fb["ink"], fb["box"], family))
        return res
    res["used_our_font"] = True

    # --- lop 3: dau co thuc su duoc ve ---
    ct = render_ink(VN_CTRL_TEXT, font_file, family, bold)
    res["ink_ascii"] = ct["ink"]
    if ct["ink"] <= 0:
        res["reasons"].append("ban doi chung khong dau render ra khung trong")
        return res
    res["ratio"] = round(vn["ink"] / float(ct["ink"]), 3)
    res["h_ratio"] = round(vn["h"] / float(ct["h"]), 3) if ct["h"] else 0.0
    if res["ratio"] < INK_RATIO_MIN:
        res["reasons"].append(
            "chu co dau chi nhieu muc hon ban khong dau %.3f lan (can >= %.2f)"
            " -> dau bi bo" % (res["ratio"], INK_RATIO_MIN))
    elif res["ratio"] > INK_RATIO_MAX:
        res["reasons"].append(
            "chu co dau nhieu muc gap %.2f lan ban khong dau (> %.2f)"
            " -> dang ve o vuong tofu" % (res["ratio"], INK_RATIO_MAX))
    if res["h_ratio"] < HEIGHT_RATIO_MIN:
        res["reasons"].append(
            "chu co dau khong cao hon chu khong dau (%.3f lan, can >= %.2f)"
            " -> dau bi bo" % (res["h_ratio"], HEIGHT_RATIO_MIN))
    res["ok"] = not res["reasons"]
    return res


# ----------------------------------------------------------------------------
# tim font trong --resources / assets kem san
# ----------------------------------------------------------------------------

FONT_DIR_NAMES = ("font", "fonts")
FONT_PRIORITY = ("bevietnam", "inter", "roboto", "noto")
FONT_WEIGHT_PRIORITY = ("extrabold", "black", "bold", "semibold", "medium",
                        "regular")


def find_fonts(resources):
    """Tim DE QUY *.ttf/*.otf duoi cac thu muc ten font/fonts/Font.

    Neu khong thay thu muc nao ten font/fonts thi quet ca --resources
    (de nguoi dung chi vao thang thu muc font cung chay).
    """
    if not resources or not os.path.isdir(resources):
        return []
    scoped, anywhere = [], []
    for root, dirs, files in os.walk(resources):
        dirs[:] = [d for d in dirs if not d.startswith(".")]
        parts = [p.lower() for p in os.path.abspath(root).replace("\\", "/").split("/")]
        in_font_dir = any(p in FONT_DIR_NAMES for p in parts)
        for f in files:
            if f.lower().endswith((".ttf", ".otf")):
                p = os.path.join(root, f)
                (scoped if in_font_dir else anywhere).append(p)
    return sorted(scoped) or sorted(anywhere)


def rank_font(path):
    name = os.path.basename(path).lower()
    fam = 99
    for i, key in enumerate(FONT_PRIORITY):
        if key in name.replace("_", "").replace("-", "").replace(" ", ""):
            fam = i
            break
    wt = 99
    for i, key in enumerate(FONT_WEIGHT_PRIORITY):
        if key in name.replace("_", "").replace("-", "").replace(" ", ""):
            wt = i
            break
    italic = 1 if "italic" in name else 0
    return (fam, italic, wt, len(name), name)


def skill_dir():
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def bundled_fonts():
    d = os.path.join(skill_dir(), "assets", "fonts")
    if not os.path.isdir(d):
        return []
    return sorted(os.path.join(d, f) for f in os.listdir(d)
                  if f.lower().endswith((".ttf", ".otf")))


SRC_RESOURCES = "--resources"
SRC_BUNDLED = "assets kem san trong skill"


def huong_dan_font_resources(res):
    """Cac buoc PHAI lam khi --resources co that nhung khong co font tieng Viet."""
    n = res.get("n_resource_fonts") or 0
    where = res.get("resources") or "<thu-muc-ban-dua>"
    if n:
        head = ["Trong thu muc --resources co %d file font nhung KHONG file nao "
                "ve duoc" % n,
                "chu tieng Viet co dau (da thu tung file, ly do o duoi)."]
    else:
        head = ["Trong thu muc --resources KHONG co file .ttf/.otf nao.",
                "Da tim de quy cac thu muc ten Font/ fonts/ font/ va ca toan bo "
                "thu muc."]
    return head + [
        "",
        "Cach A — NHANH NHAT, dung font kem san trong skill:",
        "    Bo han tham so --resources di. Skill se dung",
        "    assets/fonts/BeVietnamPro-ExtraBold.ttf (da co san trong thu muc skill).",
        "Cach B — dung font cua ban:",
        '    - Tao thu muc (neu chua co):   "%s/Font/"'
        % str(where).replace("\\", "/"),
        "    - Tai Be Vietnam Pro (mien phi) tai",
        "        https://fonts.google.com/specimen/Be+Vietnam+Pro",
        "      giai nen roi copy file BeVietnamPro-ExtraBold.ttf vao thu muc tren",
        '    - Goi lai voi:   --resources "%s"' % where,
        "  (Font khac cung duoc nhung PHAI du dau tieng Viet: Inter, Roboto,",
        "   Noto Sans. Font bieu tuong nhu Webdings/Symbol/Marlett thi khong.)",
    ]


def resolve_font(resources, explicit=None, verbose=True):
    """Thu tu uu tien theo hop dong: --font > --resources > assets kem san.

    Tra ve dict {file, dir, family, source, check} hoac None neu khong co
    font nao dat.
    """
    tried = []
    groups = []
    n_res_files = 0
    if explicit:
        if not os.path.isfile(explicit):
            die("--font tro vao file khong ton tai: %s" % explicit)
        # Nguoi dung CHI DINH font nay -> neu no khong dat thi BAO LOI,
        # TUYET DOI khong lang le doi sang font khac.
        groups.append(("--font do ban chi dinh", [explicit]))
    if resources:
        res_files = sorted(find_fonts(resources), key=rank_font)
        n_res_files = len(res_files)
        groups.append((SRC_RESOURCES, res_files))
    groups.append((SRC_BUNDLED, bundled_fonts()))

    def base(extra):
        d = {"tried": tried, "resources": resources,
             "n_resource_fonts": n_res_files}
        d.update(extra)
        return d

    for source, cands in groups:
        for path in cands[:12]:
            try:
                names = font_names(path)
                weight = font_weight(path)
            except Exception as exc:
                tried.append((path, source, ["khong doc duoc bang name: %s" % exc]))
                continue
            chk = check_font_vietnamese(path, names["ass_family"], weight=weight)
            if chk["ok"]:
                # Neu nguoi dung DA dua --resources ma phai lui ve assets kem san
                # thi KHONG duoc lang le dung: bao ro de ho tu quyet
                # (hop dong muc 4: khong doan, khong tu thay the).
                return base({
                    "file": os.path.abspath(path),
                    "dir": os.path.dirname(os.path.abspath(path)),
                    "family": names["ass_family"],
                    "weight": weight, "bold": chk["bold"],
                    "names": names, "source": source, "check": chk,
                    "resources_unused": bool(resources and source == SRC_BUNDLED)})
            tried.append((path, source, chk["reasons"]))
            if explicit and path == explicit:
                # font chi dinh that bai -> dung han, khong thu font khac
                return base({"file": None,
                             "explicit_failed": explicit,
                             "explicit_reasons": chk["reasons"]})
    return base({"file": None})


# ----------------------------------------------------------------------------
# thoi gian <-> ASS
# ----------------------------------------------------------------------------

def ass_time(t):
    if t < 0:
        t = 0.0
    cs = int(round(t * 100.0))
    h, cs = divmod(cs, 360000)
    m, cs = divmod(cs, 6000)
    s, cs = divmod(cs, 100)
    return "%d:%02d:%02d.%02d" % (h, m, s, cs)


def parse_ass_time(txt):
    h, m, rest = txt.strip().split(":")
    return int(h) * 3600 + int(m) * 60 + float(rest)


def hr(char="=", n=72):
    return char * n
