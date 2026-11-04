# -*- coding: utf-8 -*-
"""Hàm dùng chung cho skill skill-bando-tintuc-chinhtri: đường dẫn, log, tải file, toán Mercator, bảng tên nước."""
import io
import json
import math
import os
import re
import subprocess
import sys
import time
import unicodedata

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

SCRIPTS = os.path.dirname(os.path.abspath(__file__))
SKILL = os.path.dirname(SCRIPTS)
ASSETS = os.path.join(SKILL, "assets")
CACHE = os.path.join(SKILL, "cache")
FONTS = os.path.join(ASSETS, "fonts")
THU_VIEN = os.path.join(ASSETS, "thu_vien")
REFERENCES = os.path.join(SKILL, "references")
UA = "skill-bando-tintuc-chinhtri/1.0 (video map explainer; contact: local user)"

KHUNG_MAC_DINH = {"rong": 1080, "cao": 1920, "fps": 30}
DUOI_SAU_TIENG_CUOI = 0.9  # video kéo dài 0,9 s sau tiếng cuối


# ---------- log ----------
def ok(msg):
    print("✅ " + msg)


def canh_bao(msg):
    print("⚠ " + msg)


def die(msg, code=2):
    print("⛔ " + msg)
    sys.exit(code)


def buoc(msg):
    print("\n== " + msg + " ==")


# ---------- file ----------
def doc_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def ghi_json(path, data):
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=1)


def ghi_text(path, text):
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


def mkdir(path):
    os.makedirs(path, exist_ok=True)
    return path


def ten_khong_dau(s):
    """'Triều Tiên' -> 'trieu tien' (dùng để tra bảng)."""
    s = unicodedata.normalize("NFD", s)
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    s = s.replace("đ", "d").replace("Đ", "D")
    s = re.sub(r"[^A-Za-z0-9 ]+", " ", s)
    return re.sub(r"\s+", " ", s).strip().lower()


def ten_file_an_toan(s):
    s = ten_khong_dau(s).replace(" ", "_")
    return s[:60] or "x"


def ten_ban_moi(duong_dan):
    """Không ghi đè: a.mp4 -> a.mp4 nếu chưa có, không thì a_ban2.mp4, a_ban3.mp4…"""
    if not os.path.exists(duong_dan):
        return duong_dan
    goc, duoi = os.path.splitext(duong_dan)
    i = 2
    while True:
        p = "%s_ban%d%s" % (goc, i, duoi)
        if not os.path.exists(p):
            return p
        i += 1


# ---------- ffmpeg ----------
def chay(cmd, im=False, timeout=None):
    p = subprocess.run(cmd, capture_output=True, timeout=timeout)
    out = (p.stdout or b"").decode("utf-8", "replace") + (p.stderr or b"").decode("utf-8", "replace")
    if p.returncode != 0 and not im:
        die("lệnh lỗi (%d): %s\n%s" % (p.returncode, " ".join(str(c) for c in cmd[:6]), out[-1500:]))
    return out


def ffprobe_thoi_luong(path):
    out = chay(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                "-of", "default=noprint_wrappers=1:nokey=1", path])
    try:
        return float(out.strip().splitlines()[0])
    except Exception:
        die("ffprobe không đọc được thời lượng của %s" % path)


def ffmpeg_loudness(path):
    out = chay(["ffmpeg", "-nostats", "-i", path, "-af", "ebur128=peak=true", "-f", "null", "-"], im=True)
    # ebur128 in cả dòng đo từng khung (I: -70 LUFS ở giây 0) → chỉ đọc phần "Summary:" ở cuối
    k = out.rfind("Summary:")
    tom = out[k:] if k >= 0 else out
    i = re.findall(r"I:\s+(-?[\d.]+) LUFS", tom)
    tp = re.findall(r"Peak:\s+(-?[\d.]+) dBFS", tom)
    return (float(i[-1]) if i else None, float(tp[-1]) if tp else None)


def thu_muc_sfx():
    """Thư mục SFX THẬT của người dùng: assets/sfx của skill, và bản ở repo SON_VIDEO_AI nếu skill đã được chuyển sang đó."""
    out = [os.path.join(ASSETS, "sfx")]
    goc = os.path.dirname(os.path.dirname(os.path.dirname(SKILL)))   # .../SON_AI_VIDEO
    for p in (os.path.join(goc, "SON_VIDEO_AI", "skills", os.path.basename(SKILL), "assets", "sfx"),):
        if os.path.isdir(p) and p not in out:
            out.append(p)
    return [d for d in out if os.path.isdir(d)] or out


def sua_duong_dan(p):
    """Đường dẫn tuyệt đối cũ trỏ vào cache/ hoặc assets/ của skill (skill bị đổi tên, chuyển máy, chuyển sang tool NNS)
    → đặt lại theo vị trí skill hiện tại. Đường dẫn còn tồn tại hoặc không thuộc skill thì giữ nguyên."""
    if not p or not isinstance(p, str) or os.path.exists(p):
        return p
    q = p.replace("\\", "/")
    for goc, moi in (("/cache/", CACHE), ("/assets/", ASSETS)):
        k = q.rfind(goc)
        if k >= 0:
            c = os.path.join(moi, *q[k + len(goc):].split("/"))
            if os.path.exists(c):
                return c
    return p


# ---------- mạng ----------
def _session():
    import requests
    s = requests.Session()
    s.headers.update({"User-Agent": UA})
    return s


_SES = None


def session():
    global _SES
    if _SES is None:
        _SES = _session()
    return _SES


def tai_file(url, path, lan=3, timeout=60, im=False):
    """Tải url về path (bỏ qua nếu đã có). Trả True/False."""
    if os.path.exists(path) and os.path.getsize(path) > 0:
        return True
    mkdir(os.path.dirname(os.path.abspath(path)))
    tmp = path + ".part"
    for i in range(lan):
        try:
            r = session().get(url, timeout=timeout, stream=True)
            if r.status_code != 200:
                raise RuntimeError("HTTP %d" % r.status_code)
            with open(tmp, "wb") as f:
                for chunk in r.iter_content(1 << 16):
                    f.write(chunk)
            os.replace(tmp, path)
            return True
        except Exception as exc:
            if not im:
                print("   … tải lỗi (%s) lần %d: %s" % (exc, i + 1, url[:90]))
            time.sleep(1.5 * (i + 1))
    try:
        os.remove(tmp)
    except Exception:
        pass
    return False


def lay_json(url, params=None, timeout=30, im=False):
    try:
        r = session().get(url, params=params, timeout=timeout)
        if r.status_code != 200:
            raise RuntimeError("HTTP %d" % r.status_code)
        return r.json()
    except Exception as exc:
        if not im:
            print("   … gọi API lỗi: %s (%s)" % (exc, url[:80]))
        return None


# ---------- Mercator ----------
def lonlat_den_don_vi(lon, lat):
    """Toạ độ Web Mercator chuẩn hoá [0,1]×[0,1] (x sang đông, y xuống nam)."""
    lat = max(-85.05, min(85.05, lat))
    x = (lon + 180.0) / 360.0
    s = math.sin(math.radians(lat))
    y = 0.5 - math.log((1 + s) / (1 - s)) / (4 * math.pi)
    return x, y


def don_vi_den_lonlat(x, y):
    lon = x * 360.0 - 180.0
    lat = math.degrees(2 * math.atan(math.exp((0.5 - y) * 2 * math.pi)) - math.pi / 2)
    return lon, lat


def km_moi_don_vi(lat):
    """Số km ứng với 1 đơn vị Mercator (cả chiều rộng thế giới) tại vĩ độ lat."""
    return 40075.017 * math.cos(math.radians(max(-85, min(85, lat))))


def km_den_don_vi(km, lat):
    return km / km_moi_don_vi(lat)


def khoang_cach_km(lon1, lat1, lon2, lat2):
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp = p2 - p1
    dl = math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 6371.0 * 2 * math.asin(math.sqrt(a))


# ---------- bảng tên nước (tiếng Việt / tiếng Anh -> ISO2) ----------
NUOC = {
    "KP": ["Triều Tiên", "Bắc Triều Tiên", "Bắc Hàn", "North Korea", "DPRK", "Korea, North"],
    "KR": ["Hàn Quốc", "Nam Hàn", "South Korea", "Korea, South", "Republic of Korea"],
    "US": ["Mỹ", "Hoa Kỳ", "Nước Mỹ", "United States", "United States of America", "USA", "America"],
    "CN": ["Trung Quốc", "China", "Tàu", "Trung Hoa"],
    "RU": ["Nga", "Russia", "Russian Federation", "Liên Xô", "Soviet Union"],
    "JP": ["Nhật", "Nhật Bản", "Japan"],
    "VN": ["Việt Nam", "Vietnam", "Viet Nam"],
    "TW": ["Đài Loan", "Taiwan"],
    "IN": ["Ấn Độ", "India"],
    "PK": ["Pakistan"],
    "IR": ["Iran"],
    "IQ": ["Iraq"],
    "IL": ["Israel"],
    "PS": ["Palestine", "Gaza"],
    "SY": ["Syria"],
    "TR": ["Thổ Nhĩ Kỳ", "Turkey", "Türkiye"],
    "SA": ["Ả Rập Xê Út", "Saudi Arabia", "Ả Rập Saudi"],
    "AE": ["UAE", "Các Tiểu vương quốc Ả Rập Thống nhất", "United Arab Emirates"],
    "QA": ["Qatar"],
    "YE": ["Yemen"],
    "EG": ["Ai Cập", "Egypt"],
    "LY": ["Libya"],
    "SD": ["Sudan"],
    "ET": ["Ethiopia"],
    "NG": ["Nigeria"],
    "ZA": ["Nam Phi", "South Africa"],
    "KE": ["Kenya"],
    "CD": ["Congo", "DR Congo", "Democratic Republic of the Congo"],
    "SO": ["Somalia"],
    "UA": ["Ukraine", "Ukraina"],
    "BY": ["Belarus"],
    "PL": ["Ba Lan", "Poland"],
    "DE": ["Đức", "Germany"],
    "FR": ["Pháp", "France"],
    "GB": ["Anh", "Vương quốc Anh", "United Kingdom", "UK", "Britain", "Great Britain"],
    "IT": ["Ý", "Italia", "Italy"],
    "ES": ["Tây Ban Nha", "Spain"],
    "PT": ["Bồ Đào Nha", "Portugal"],
    "NL": ["Hà Lan", "Netherlands"],
    "BE": ["Bỉ", "Belgium"],
    "CH": ["Thụy Sĩ", "Switzerland"],
    "AT": ["Áo", "Austria"],
    "SE": ["Thụy Điển", "Sweden"],
    "NO": ["Na Uy", "Norway"],
    "FI": ["Phần Lan", "Finland"],
    "DK": ["Đan Mạch", "Denmark"],
    "GL": ["Greenland"],
    "IS": ["Iceland"],
    "IE": ["Ireland"],
    "GR": ["Hy Lạp", "Greece"],
    "RO": ["Romania"],
    "HU": ["Hungary"],
    "CZ": ["Séc", "Czechia", "Czech Republic"],
    "SK": ["Slovakia"],
    "RS": ["Serbia"],
    "BG": ["Bulgaria"],
    "LT": ["Lithuania", "Litva"],
    "LV": ["Latvia"],
    "EE": ["Estonia"],
    "MD": ["Moldova"],
    "GE": ["Gruzia", "Georgia"],
    "AM": ["Armenia"],
    "AZ": ["Azerbaijan"],
    "KZ": ["Kazakhstan"],
    "UZ": ["Uzbekistan"],
    "AF": ["Afghanistan"],
    "MN": ["Mông Cổ", "Mongolia"],
    "TH": ["Thái Lan", "Thailand"],
    "MM": ["Myanmar", "Miến Điện", "Burma"],
    "LA": ["Lào", "Laos"],
    "KH": ["Campuchia", "Cambodia"],
    "MY": ["Malaysia"],
    "SG": ["Singapore"],
    "ID": ["Indonesia"],
    "PH": ["Philippines"],
    "AU": ["Úc", "Australia"],
    "NZ": ["New Zealand"],
    "CA": ["Canada"],
    "MX": ["Mexico"],
    "CU": ["Cuba"],
    "VE": ["Venezuela"],
    "CO": ["Colombia"],
    "BR": ["Brazil", "Brasil"],
    "AR": ["Argentina"],
    "CL": ["Chile"],
    "PE": ["Peru"],
    "PA": ["Panama"],
    "BD": ["Bangladesh"],
    "LK": ["Sri Lanka"],
    "NP": ["Nepal"],
    "JO": ["Jordan"],
    "LB": ["Lebanon", "Li Băng"],
    "KW": ["Kuwait"],
    "OM": ["Oman"],
    "MA": ["Morocco", "Ma Rốc"],
    "DZ": ["Algeria"],
    "TN": ["Tunisia"],
    "NE": ["Niger"],
    "ML": ["Mali"],
    "GH": ["Ghana"],
    "TZ": ["Tanzania"],
    "AO": ["Angola"],
    "MZ": ["Mozambique"],
    "MG": ["Madagascar"],
    "VA": ["Vatican"],
    "TL": ["Đông Timor", "Timor-Leste"],
    "BN": ["Brunei"],
}
_NUOC_TRA = {}
for _iso, _ten in NUOC.items():
    for _t in _ten:
        _NUOC_TRA[ten_khong_dau(_t)] = _iso


def tim_ma_nuoc(ten):
    """'Triều Tiên' / 'north korea' / 'KP' -> 'KP' hoặc None. Mã ISO chỉ nhận khi viết HOA đúng 2 chữ
    (tránh 'Mỹ' -> 'my' -> Malaysia)."""
    if not ten:
        return None
    s = str(ten).strip()
    if len(s) == 2 and s.isupper() and s in NUOC:
        return s
    k = ten_khong_dau(s)
    if k in _NUOC_TRA:
        return _NUOC_TRA[k]
    k2 = re.sub(r"^(nuoc|dat nuoc|quoc gia) ", "", k)
    return _NUOC_TRA.get(k2)


# biển, đại dương: điểm đặt nhãn (lon, lat)
BIEN = {
    "thai binh duong": ("Pacific", 180.0, 20.0),
    "pacific": ("Pacific", 180.0, 20.0),
    "pacific ocean": ("Pacific", 180.0, 20.0),
    "bac thai binh duong": ("North Pacific", -170.0, 35.0),
    "dai tay duong": ("Atlantic", -35.0, 25.0),
    "atlantic": ("Atlantic", -35.0, 25.0),
    "an do duong": ("Indian Ocean", 78.0, -15.0),
    "indian ocean": ("Indian Ocean", 78.0, -15.0),
    "bac bang duong": ("Arctic Ocean", 0.0, 84.0),
    "bien dong": ("Biển Đông", 114.0, 14.0),
    "south china sea": ("South China Sea", 114.0, 14.0),
    "bien hoa dong": ("East China Sea", 125.0, 28.0),
    "east china sea": ("East China Sea", 125.0, 28.0),
    "bien nhat ban": ("Sea of Japan", 135.0, 40.0),
    "sea of japan": ("Sea of Japan", 135.0, 40.0),
    "hoang hai": ("Yellow Sea", 123.0, 36.0),
    "yellow sea": ("Yellow Sea", 123.0, 36.0),
    "bien philippines": ("Philippine Sea", 133.0, 18.0),
    "bien dia trung hai": ("Mediterranean", 18.0, 35.0),
    "dia trung hai": ("Mediterranean", 18.0, 35.0),
    "mediterranean": ("Mediterranean", 18.0, 35.0),
    "bien den": ("Black Sea", 34.0, 43.5),
    "black sea": ("Black Sea", 34.0, 43.5),
    "bien do": ("Red Sea", 38.0, 20.0),
    "red sea": ("Red Sea", 38.0, 20.0),
    "vinh ba tu": ("Persian Gulf", 51.0, 27.0),
    "persian gulf": ("Persian Gulf", 51.0, 27.0),
    "bien a rap": ("Arabian Sea", 63.0, 15.0),
    "vinh bengal": ("Bay of Bengal", 88.0, 14.0),
    "bien baltic": ("Baltic Sea", 20.0, 58.0),
    "bien bac": ("North Sea", 3.0, 56.0),
    "bien caribe": ("Caribbean", -75.0, 15.0),
    "caribbean": ("Caribbean", -75.0, 15.0),
    "vinh mexico": ("Gulf of Mexico", -90.0, 25.0),
    "bien bering": ("Bering Sea", -175.0, 58.0),
    "bering sea": ("Bering Sea", -175.0, 58.0),
    "bien okhotsk": ("Sea of Okhotsk", 150.0, 55.0),
    "eo bien dai loan": ("Taiwan Strait", 119.5, 24.5),
    "eo bien hormuz": ("Strait of Hormuz", 56.5, 26.5),
    "eo bien malacca": ("Strait of Malacca", 100.0, 3.0),
    "kenh dao suez": ("Suez Canal", 32.5, 30.5),
    "kenh dao panama": ("Panama Canal", -79.7, 9.1),
}


def tim_bien(ten):
    return BIEN.get(ten_khong_dau(ten))


# vật thể: từ khoá tiếng Việt -> tên chuẩn + câu tìm ảnh (Wikimedia Commons)
VAT_THE = {
    "ten_lua": (["tên lửa", "tên lửa đạn đạo", "icbm", "missile", "rocket", "hwasong", "hoa song"],
                "Hwasong-15 ICBM missile launch"),
    "ve_tinh": (["vệ tinh", "satellite", "vệ tinh do thám"], "satellite spacecraft solar panels"),
    "tau_chien": (["tàu chiến", "tàu khu trục", "chiến hạm", "warship", "destroyer", "tàu hải quân", "tàu"],
                  "Arleigh Burke destroyer aerial view"),
    "tau_san_bay": (["tàu sân bay", "aircraft carrier", "hàng không mẫu hạm"], "USS Nimitz aircraft carrier aerial"),
    "tau_dau": (["tàu dầu", "tàu chở dầu", "siêu tàu chở dầu", "tanker", "oil tanker"], "oil tanker ship aerial view"),
    "tau_ngam": (["tàu ngầm", "submarine"], "submarine surfaced"),
    "gian_phong": (["giàn phóng", "thiết bị đánh chặn", "đánh chặn", "thaad", "patriot", "interceptor", "launcher",
                    "phòng không", "phòng thủ tên lửa"], "THAAD missile launcher"),
    "may_bay": (["máy bay", "tiêm kích", "chiến đấu cơ", "fighter jet", "máy bay chiến đấu", "f-35", "f-16"],
                "fighter jet aircraft flying"),
    "may_bay_nem_bom": (["máy bay ném bom", "bomber", "b-2", "b-52"], "strategic bomber aircraft"),
    "truc_thang": (["trực thăng", "helicopter"], "military helicopter"),
    "xe_tang": (["xe tăng", "tank", "thiết giáp"], "main battle tank"),
    "drone": (["drone", "uav", "máy bay không người lái"], "military drone UAV"),
    "binh_linh": (["binh lính", "lính", "quân đội", "soldier", "troops", "bộ binh"], "soldiers marching"),
    "bom_hat_nhan": (["bom hạt nhân", "đầu đạn hạt nhân", "nuclear", "hạt nhân", "vũ khí hạt nhân"],
                     "nuclear weapon warhead"),
    "sung": (["súng", "rifle", "ak-47", "vũ khí"], "assault rifle"),
    "thung_dau": (["dầu", "thùng dầu", "dầu mỏ", "oil", "xăng dầu"], "oil drum barrel isolated"),
    "khi_dot": (["khí đốt", "gas", "lng", "đường ống"], "gas pipeline"),
    "nha_may": (["nhà máy", "factory", "công nghiệp", "xưởng"], "factory industrial plant"),
    "nha_may_dien": (["nhà máy điện", "điện hạt nhân", "lò phản ứng", "power plant"], "nuclear power plant"),
    "tien": (["tiền", "đô la", "usd", "money", "dollar", "tỷ đô", "ngân sách"], "US dollar banknotes stack"),
    "vang": (["vàng", "gold"], "gold bars"),
    "chip": (["chip", "bán dẫn", "semiconductor", "vi mạch"], "semiconductor chip"),
    "container": (["container", "hàng hoá", "xuất khẩu", "thương mại", "tàu hàng", "tàu container"],
                  "container ship cargo"),
    "lua_mi": (["lúa mì", "lương thực", "ngũ cốc", "wheat", "gạo"], "wheat grain"),
    "virus": (["virus", "dịch bệnh", "covid", "đại dịch", "vi rút"], "virus particle 3d"),
    "benh_vien": (["bệnh viện", "hospital", "y tế"], "hospital building"),
    "toa_nha": (["toà nhà", "tòa nhà", "thành phố", "cao ốc", "building"], "skyscraper building"),
    "nha_trang": (["nhà trắng", "white house"], "White House"),
    "dien_kremlin": (["điện kremlin", "kremlin"], "Moscow Kremlin"),
    "lau_nam_goc": (["lầu năm góc", "pentagon"], "The Pentagon aerial"),
    "quoc_hoi": (["quốc hội", "nghị viện", "parliament", "capitol"], "United States Capitol"),
    "co": (["cờ", "flag", "quốc kỳ"], "flag waving"),
    "ban_tay_bat": (["bắt tay", "handshake", "thoả thuận", "hiệp định"], "handshake"),
    "can_cu": (["căn cứ", "căn cứ quân sự", "military base"], "military base aerial"),
    "radar": (["radar", "trạm radar", "ăng ten"], "radar station"),
    "cang": (["cảng", "hải cảng", "port", "harbor"], "seaport aerial"),
    "san_bay": (["sân bay", "airport"], "airport aerial"),
    "dap": (["đập", "đập thuỷ điện", "dam"], "hydroelectric dam"),
    "mo": (["mỏ", "khai thác", "mine", "đất hiếm", "khoáng sản"], "open pit mine"),
    "nui_lua": (["núi lửa", "volcano"], "volcano eruption"),
    "bao": (["bão", "siêu bão", "hurricane", "typhoon"], "hurricane satellite view"),
    "dong_dat": (["động đất", "earthquake"], "earthquake damage"),
    "lu_lut": (["lũ", "lũ lụt", "flood"], "flood aerial"),
    "chay_rung": (["cháy rừng", "wildfire"], "wildfire"),
    "nguoi_ti_nan": (["người tị nạn", "di cư", "refugee", "migrant"], "refugees walking"),
    "bieu_tinh": (["biểu tình", "protest", "bạo loạn"], "protest crowd"),
    "lien_hop_quoc": (["liên hợp quốc", "united nations", "un"], "United Nations headquarters"),
    "nato": (["nato"], "NATO flag"),
    "eu": (["eu", "liên minh châu âu", "european union"], "European Union flag"),
}
_VAT_TRA = {}
for _k, (_alias, _q) in VAT_THE.items():
    _VAT_TRA[_k] = _k
    for _a in _alias:
        _VAT_TRA[ten_khong_dau(_a)] = _k


def tim_vat_the(ten):
    if not ten:
        return None
    k = ten_khong_dau(str(ten))
    if k in _VAT_TRA:
        return _VAT_TRA[k]
    k2 = k.replace(" ", "_")
    if k2 in VAT_THE:
        return k2
    return None


# ---------- màu ----------
def mau_hex(s, mac_dinh=(255, 74, 31)):
    if not s:
        return mac_dinh
    s = str(s).strip().lstrip("#")
    if len(s) == 6:
        return tuple(int(s[i:i + 2], 16) for i in (0, 2, 4))
    return mac_dinh


MAU_NUOC = ["#ff4a1f", "#2fa8ff", "#ffcc00", "#3ddc84", "#c35bff", "#ff5fa2", "#ff9a3c", "#8ad6ff"]


def thoi_gian_hms(t):
    m, s = divmod(max(0.0, t), 60)
    return "%02d:%05.2f" % (int(m), s)
