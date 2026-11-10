---
name: nns-ban-do-ha-tang
description: Dựng video BẢN ĐỒ HẠ TẦNG dọc 9:16 quanh MỘT ĐỊA ĐIỂM BẤT KỲ ở Việt Nam chỉ từ CÁI TÊN — dự án BĐS (The Matrix One…), di tích/địa danh (Lăng Bác, Hồ Tây…), toà nhà (Landmark 81…) — kiểu video mẫu KB5 "Hạ tầng giao thông quanh The CityOn". Gõ tên là skill TỰ KHẢO SÁT trên OpenStreetMap: tìm đúng công trình (Photon + chấm điểm, tên lặt vặt thì lấy mốc rồi chọn công trình nổi bật quanh đó), lấy ranh khu đất/mặt hồ, rồi tìm hạ tầng ĐANG VẬN HÀNH quanh đó — metro (chỉ ray đang chạy + ga nằm trên ray, đúng hai đầu tuyến), vành đai/đại lộ/cao tốc, cầu lớn qua sông, sân bay (chấm ở nhà ga), tiện ích nổi bật (di tích, TTTM, SVĐ, bệnh viện, đại học, hồ, công viên) — bỏ hẳn thứ đang xây/chạy thử/quy hoạch; tự xếp 5 chương (Ngay sát bên/Ven hồ · Vành đai · Metro đang chạy · Tiện ích · Cầu & sân bay) rồi dựng: ảnh vệ tinh Esri thật, icon phương tiện chạy vẽ tuyến (đường đi thật trên mạng đường OSM), ghim + nhãn "cách <tên> ~X km", spotlight vòng km, chú giải; KHÔNG giọng, chỉ SFX (+ nhạc nếu user đưa file); máy quay êm; tự kiểm 9 mục trên file cuối. Dừng 1 lần ở CỔNG DUYỆT NỘI DUNG (bảng chương/điểm/khoảng cách + ảnh xem trước). Khác `nns-video-ban-do` (cái đó dựng theo GIỌNG ĐỌC + kịch bản). Trigger '/nns-ban-do-ha-tang', 'làm video hạ tầng quanh <địa điểm>', 'video bản đồ giao thông cho dự án X', 'dự án X gần metro/vành đai/sân bay', 'làm video như The Matrix One cho Lăng Bác / Hồ Tây / Landmark 81', 'video vị trí thuận tiện của toà nhà', 'video bản đồ tiện ích quanh công trình'.
---

# nns-ban-do-ha-tang — địa điểm nằm giữa mạng giao thông

**Gọi bằng TÊN là đủ** (vd user: "làm cho tôi Lăng Bác", "Hồ Tây", "Landmark 81", "dự án The Matrix One ở Mỹ Đình"):
```bash
python .claude/skills/nns-ban-do-ha-tang/scripts/run.py --ten "Lăng Bác" --work _bandoht_lang_bac          # bước 1: khảo sát + xem trước
python .claude/skills/nns-ban-do-ha-tang/scripts/run.py --ten "Lăng Bác" --work _bandoht_lang_bac --render # bước 2: dựng + tự kiểm
```
> **Máy mới (skill chép từ zip):** lần đầu chạy `python <thư mục skill>/scripts/kiem_tra_cai_dat.py`; báo thiếu thư viện →
> `python -m pip install -r <thư mục skill>/requirements.txt`, thiếu ffmpeg → hướng dẫn trong `HUONG_DAN_CAI_DAT.md`.
> Lệnh trong file này viết cho skill nằm ở `<dự án>/.claude/skills/`; skill cài ở `~/.claude/skills/` thì thay
> `.claude/skills/nns-ban-do-ha-tang` bằng thư mục gốc của skill (Base directory). Các thư mục `_bandoht_*` nhắc bên dưới là
> các lần chạy trên máy tác giả — máy khác không có, bỏ qua.

**`--ten` nhận NGUYÊN VĂN câu user gõ**, kể cả địa chỉ ("Chợ Hàn, Đà Nẵng", "Tòa nhà The Matrix One . Số 1 Lê Quang Đạo, Hà Nội"):
skill tự lấy phần trước dấu phẩy / " . " làm tên (bỏ chữ đệm "Tòa nhà", "Dự án"), phần sau chỉ để chấm điểm vị trí (đúng tỉnh/thành
+3 điểm), tên ứng viên so CÓ DẤU. Đặt `--work _bandoht_<tên không dấu, gạch dưới>`.
Tên tìm không ra / trùng nhiều chỗ → thêm `--vi_tri "lat,lon"` (hoặc dán link Google Maps). Khảo sát lại từ đầu: `--khao_sat_lai`.
Bước 1 ghi `<work>/du_an.json` (hồ sơ nháp — Claude SOÁT và sửa tay được) + `<work>/khao_sat.json` (mọi ứng viên + lý do bị bỏ).
Ví dụ đã chạy: `_bandoht_matrixone/` (dự án BĐS, hồ sơ viết tay), `_bandoht_lang_bac/`, `_bandoht_ho_tay/`, `_bandoht_landmark81/` (tự khảo sát).

Số đo video mẫu: `references/phan-tich-mau.md`. Hằng số: `scripts/common.py` — **script khác không tự đặt số.**
Hồ sơ mẫu chạy được ngay (chỉ cần mạng): `examples/the_matrix_one/du_an.json` — mọi tuyến/điểm lấy từ OSM, không nhạc, có cả
tuyến `"trang_thai": "dang_xay"` bị tự bỏ. `examples/the_cityon/` chỉ là mẫu ĐỊNH DẠNG (tuyến lấy từ ảnh, phối cảnh, nhạc) — thiếu
file nhạc/phối cảnh nên không chạy nguyên trạng, và toàn hạ tầng tương lai. Font/SFX nằm sẵn trong `assets/` (skill tự đứng được).
Tile vệ tinh cache chung ở `SON_AI_VIDEO/_cache_tiles/esri/` (đừng xoá giữa các lần chạy).

> Quy ước với chủ dự án: trả lời tiếng Việt có dấu; SỐT RUỘT — báo tiến độ ngắn, có ảnh xem trước là gửi.
> BẢN ĐỒ PHẢI CHUẨN: mọi tuyến/điểm có nguồn (OSM / ảnh quy hoạch / toạ độ hồ sơ). Không có nguồn → hỏi, không vẽ.
> Sửa theo góp ý: plan → ok → sửa skill → ok → dựng lại.

## LUẬT CỨNG — CHỈ HẠ TẦNG ĐÃ VẬN HÀNH [user chốt 17/10/2026]

"Chỉ ghi hoặc đưa cái gì lên khi đã đi vào hoạt động; cái gì đang làm hoặc đang test thì chưa đưa vào."
- Tuyến/ga/cầu/nút giao/sân bay đang xây, chạy thử, quy hoạch → **BỎ HẲN**. Không nét đứt, không chữ "dự kiến".
- Truy vấn OSM đã lọc sẵn: ray chỉ lấy `railway=rail|subway|light_rail|…` (bỏ `construction`/`proposed`), đường bỏ
  `highway=construction|proposed|…` (`common.RAIL_OPERATING`, `HIGHWAY_NOT_OPERATING`). Tuyến chạy một phần (metro 3 chỉ
  Nhổn – Cầu Giấy) tự còn đúng đoạn đã chạy — nhãn phụ ghi đúng đoạn đó.
- OSM có thể chậm cập nhật: hạng mục nào còn nghi → tra báo mới nhất trước khi đưa vào; hồ sơ ghi `"trang_thai": "dang_xay"`
  (hoặc `chay_thu`, `quy_hoach`) thì planner tự bỏ và in "BỎ … chưa vận hành".
- Mẫu KB5 The CityOn toàn hạ tầng tương lai — theo luật này phần lớn bị bỏ; muốn làm kiểu "hạ tầng tương lai" phải HỎI user.

## CẤU HÌNH MẶC ĐỊNH (đo từ mẫu + luật user đã chốt ở các video bản đồ khác — CHƯA có bản user duyệt toàn bộ)

Khi user duyệt một bản: đổi tiêu đề mục này thành "CẤU HÌNH ĐÃ CHỐT — KHÔNG HỎI LẠI" và ghi ngày.
Dòng có **[user chốt <ngày>]** là quyết định của user — không hỏi lại, không tự đổi.

| Lớp | Mặc định | Nguồn |
|---|---|---|
| Khung | 1080×1920, 30 fps, x264 crf 17, bt709 (`out_color_matrix=bt709`) | mẫu 720p → nâng |
| Nền | Esri World Imagery z8–z18, hoà 2 tầng khi chuyển, lọc Gauss khi thu nhỏ > 1,3×; tương phản ×1,04 | mẫu |
| Máy quay | van Wijk ρ 1,42 + ease sin; **lia ≤ 14 px/khung, zoom ≤ 7 %/khung, KHÔNG xoay**, bắc ở trên; cú bay tự kéo dài tới khi đạt ngưỡng | user chốt 17/10 (SongDay v3); mẫu zoom 8,7 %/khung là vượt |
| Bìa | 2 dòng chữ khối nghiêng Barlow Condensed Black Italic: dòng 1 gradient cam-vàng, dòng 2 xanh dương, viền tối; dòng phụ **Be Vietnam Pro Black trắng viền tối, thẳng (bỏ thư pháp — user 18/10)**; **giữ 1,25 s** + mờ 0,3 s | mẫu chỉ 3 khung (thumbnail) — user không thích tiêu đề "mất ngay" |
| Phối cảnh | ảnh RGBA đã cắt theo ranh lô (bounds lat/lon) hoà vào 0,55–0,95 s, viền vàng phát sáng; tan khi máy lùi ra | mẫu |
| Thẻ dự án | thẻ trắng bo góc (logo PNG nếu có, không thì tên 2 dòng Montserrat Black) + dòng phụ; khung rộng > 9 km tự thu thành chip; ghim đỏ viền đen-vàng | mẫu |
| Tuyến | lõi 9 px màu tuyến + viền trắng 2 px + bóng mềm; **vẽ 400 px/s (1,1–3 s/tuyến), vào nhanh rồi chậm dần (ease-out)**; tuyến sau bắt đầu khi tuyến trước vẽ 45 % **[user chốt 18/10: "xem cứ thấy hơi chậm"]** | mẫu ≈ 210–315 px/s — chậm so với ý user |
| Icon dẫn nét | huy hiệu tròn 72 px màu tuyến, viền trắng, glyph tàu / ô tô / máy bay (vẽ vector); bật back-out 0,32 s, nhún 5 px khi chạy; **gần mép khung thì mờ dần** (dải 110 px) | user chọn "icon phương tiện" thay linh vật (17/10); mẫu để linh vật kẹt nửa người ở mép |
| Ghim điểm | giọt nước màu tuyến, ruột trắng có glyph (ga / cầu / nút giao / sân bay) + chấm đen; bật lúc icon chạm điểm | mẫu |
| Nhãn điểm | Be Vietnam Pro Black IN HOA 50 px màu tuyến (đậm hơn) viền trắng 7 px + dòng "cách <dự án> ~X km" Bold 30 trắng viền tối; **đứng 3,5 s rồi thu về tên ngắn**; nhãn mới đè chỗ thì nhãn cũ nhường; tên ngắn chỉ đặt sát ghim, không có chỗ thì ẩn; **mọi nhãn TRỌN trong khung — không cắt ở mép** (máy quay chừa chỗ, xem dòng Spotlight) **[user chốt 17/10, kiểu A]** | mẫu để nguyên mọi nhãn → 29–40 s quá tải chữ |
| Nhãn tuyến | Black 40 px màu tuyến viền trắng ("TUYẾN 8", "KẾT NỐI VÀNH ĐAI R1"), dòng phụ 28 px; đặt lệch vuông góc khỏi nét, tránh xa ghim | mẫu |
| Chữ chương | **Be Vietnam Pro Black 80 px — chữ ĐẬM THẲNG, KHÔNG dùng thư pháp/chữ uốn lượn** (user 18/10: "bỏ mấy kiểu chữ uốn lượn, cho nhìn rõ chữ"; "&" của Great Vibes đọc thành "jj") · **VÀNG gradient (#FFEE8C → #FFBE1E) + viền nâu 4 px [user chốt 18/10]** + quầng tối mềm; vào 0,4 s / ra 0,3 s; tự đặt vào ô trống (8 ứng viên trên/dưới/giữa) | mẫu |
| Spotlight | chương có `"spotlight": true`: ngoài vòng còn 64 % độ sáng, vòng trắng 3 px bung back-out 0,9 s từ dự án, to dần theo nét đang vẽ; vòng km nét đứt ĐỨNG YÊN bậc 1/2/5/10/20/30/50 (≤ 4 vòng) + nhãn km; máy quay khớp nội dung đang hiện và **CHỪA CHỖ CHO NHÃN từng ghim** (`fit_with_labels`, ±170 px ngang / 150 px dọc) — mọi nhãn trọn trong khung, bản đồ nhìn xa hơn mẫu **[user chốt 17/10, kiểu A — `EDGE_FIT = False`]** | mẫu đo −36 %; nét đứt đứng yên = user chốt; user xem cả 2 bản A (trọn nhãn) / B (sát mép như mẫu, nhãn bị cắt) và chọn A |
| Kết | toàn cảnh mọi tuyến **chừa chỗ cho tên ngắn, không cắt nhãn ở mép [user chốt 17/10, kiểu A]** + tên ngắn + chú giải trắng 2 cột (thanh màu 44×12, Be Vietnam Pro SemiBold 34; màu quá sáng có viền xám) giữ 3 s; khung kết tuỳ chọn (`khung_ket`) | mẫu; mẫu ghi "xám" nhưng vẽ trắng — skill lấy đúng màu tuyến |
| Nhịp chương [user chốt 18/10] | chữ chương hiện 0,3 s sau khi máy bắt đầu bay (không đợi tới nơi); icon đầu bật ngay khi máy dừng (0,05 s), chờ 0,12 s rồi chạy; giữ sau nét cuối 0,5 s; nhãn cuối đứng ≥ 1,2 s; nhãn đầy đủ 2,6 s rồi thu gọn; bìa 0,9 s; chú giải hiện giữa cú lùi cuối, khung kết 2,2 s → video ~28–32 s (cũ 43–50 s, gần nửa thời gian là khe chờ) | đo 18/10: 7 khe > 2 s cộng 24 s ở bản cũ |
| Vùng an toàn | chữ trong x 48–1032, y 200–1590 (đáy ~330 px bị UI TikTok/Facebook che) | memory |
| Âm thanh | nhạc của user (ngắn hơn video → lặp NGUYÊN FILE, crossfade 80 ms, không có khe im) + SFX: pop (icon), ting (nhãn), quick-swoosh (chữ chương), whoosh (cú bay lớn), ting (spotlight), take-off (sân bay), new-item (chú giải); **đỉnh SFX = nhạc tại chỗ + 3 dB** (+ gain riêng); master tuyến tính −14 LUFS + alimiter 4× oversample, TP ≤ −1,5 | mẫu hở 0,4 s im ở mỗi mối nối nhạc; SFX mẫu dưới nhạc 7–15 dB = user chê "không thấy SFX" |
| Không tự tổng hợp nhạc | không có file nhạc → chỉ SFX (báo ở cổng duyệt) | user bỏ nhạc tự tạo 13/10 |

## Đầu vào: hồ sơ `du_an.json`

```jsonc
{
 "ten": "The CityOn",                       // tên dự án — in trên thẻ và trong "cách … km"
 "vi_tri": [20.95839, 105.98528],           // lat, lon của ghim dự án (BẮT BUỘC, toạ độ thật)
 "the_phu": "Ga số 11 · tuyến 8",           // dòng phụ trên thẻ (tuỳ chọn)
 "logo": "logo.png",                        // PNG nền trong (tuỳ chọn; không có thì in tên)
 "phoi_canh": {"anh": "phoi_canh.png",      // RGBA đã cắt theo ranh lô, hướng bắc lên (tuỳ chọn)
               "bounds": [[lat_bắc, lon_tây], [lat_nam, lon_đông]]},
 "tieu_de": ["HẠ TẦNG GIAO THÔNG", "QUANH THE CITYON"], "tieu_de_phu": "đường sắt · vành đai · sân bay",
 "nhac": "nhac.mp3",                        // file nhạc của user (tuỳ chọn)
 "watermark": null,                         // chữ thư pháp mờ cố định (tuỳ chọn; mẫu có "Tiến Hiệp")
 "khung_ket": {"dong1": "THE CITYON", "dong2": "Hotline 09xx"},   // tuỳ chọn
 "chuong": [ {"ten": "Phía Bắc · nội đô", "tuyen": ["metro8", "tuyen5"]},
             {"ten": "Đường bộ & cầu", "tuyen": ["vd35", "vd4"], "spotlight": true} ],
 "tuyen": {
   "metro8": {"ten": "Đường sắt tuyến 8",   // tên trong chú giải
              "nhan": "TUYẾN 8", "nhan_phu": null,   // nhãn trên nét (tuỳ chọn)
              "loai": "metro",              // metro → icon tàu · duong → ô tô · sanbay → máy bay
              "mau": "#2FC85E",
              "nguon": {"osm": "^Đường sắt đô thị số 8", "loai": "railway"},   // HOẶC
                       // {"trace": "georef/tuyen.json", "key": "metro8"}       // HOẶC {"latlon": [[lat,lon], …]}
              "huong": "auto",              // auto | dau | cuoi | both — vẽ về phía nào từ điểm gần dự án nhất
              "tu": null, "den": null,      // [lat,lon] tuỳ chọn: điểm bắt đầu vẽ / vẽ về phía điểm này
              "ve_km": null,                // độ dài vẽ cố định (km)
              "diem": [ {"ten": ["GA SỐ 10", "ECOPARK"], "ten_ngan": "GA 10", "loai": "ga",
                         "latlon": [20.9639, 105.9336],   // HOẶC "osm": "^Cầu Mễ Sở$" · "giao": "<khoá tuyến khác>" · "cuoi": true
                         "km": 5.6,                       // số hồ sơ (tuỳ chọn) — lệch > 15 % so số đo thì cảnh báo
                         "cach_tinh": "chim_bay",         // chim_bay (mặc định) | theo_tuyen
                         "an_khoang_cach": false, "an_o_ket": false} ] } } }
```

`loai` điểm: `ga`, `cau`, `nutgiao`, `sanbay`, `diem`. Đường dẫn tương đối tính từ thư mục chứa `du_an.json`.

### Lấy hình học tuyến — thứ tự ưu tiên
1. **OSM theo tên** (`"osm": regex`): skill nối các way (dung sai 250 m, cấm nối quay đầu), chọn chuỗi đi gần dự án nhất. Tuyến đang thi công/quy hoạch thường có trong OSM ("Đường sắt đô thị Số 5…", "Đường cao tốc vành đai 4 vùng thủ đô Hà Nội", "Đường kết nối Sân bay Gia Bình với Thủ đô Hà Nội"). Tra tên thật trước bằng một truy vấn Overpass trong bbox (in tên way + số khúc).
2. **Ảnh có vẽ tuyến** (ảnh quy hoạch, ảnh chụp màn hình bản đồ, khung video mẫu) → `trace_lines.py`:
   ```bash
   python .claude/skills/nns-ban-do-ha-tang/scripts/trace_lines.py --image anh.png --near LAT,LON --zooms 12,13 \
     --palette "metro8=#2FC85E,vd4=#CC75FF,gb=white" [--via "metro8=x1,y1;x2,y2;…|vd4=…"] --out georef/tuyen.json
   ```
   Tự khớp ảnh lên vệ tinh (SIFT + CLAHE, chọn zoom nhiều điểm khớp nhất; ảnh vẽ không phải vệ tinh → `--points` khớp tay ≥ 3 điểm),
   tách nét theo màu Lab ∩ lớp vẽ đè, bỏ mảng dày (icon, chữ, thẻ), dựng đồ thị xương + cầu nối khe bị nhãn che, lấy đường dài nhất.
   Tuyến bị nhãn cắt nhiều khúc / có 2 nét cùng màu → **cho `--via` (vài điểm px theo thứ tự đi)**. LUÔN MỞ `*_trace.jpg` RA NHÌN.
3. **Đường đi thật** (`"duong_di": {"den": [lat,lon], "qua": [[lat,lon],…], "hang": "tertiary|primary"}`): định tuyến trên đồ thị đường
   OSM đang vận hành (Dijkstra, ưu tiên trục lớn; trong 1,6 km quanh 2 đầu được đi cả đường nhỏ tới tận cổng). Dùng cho "từ dự án
   tới SVĐ / TTTM / cầu / sân bay". **Nối khúc theo tên làm nét cụt** khi OSM chia đường thành nhiều khúc rời (Lê Quang Đạo cụt cách
   SVĐ 800 m — user chỉ ra). Đích nên là điểm TRÊN đường (đầu đường sát cổng, đầu cầu bên kia sông, nhà ga T2), không phải tâm
   khu đất/đường băng — lệch bám > 400 m thì planner cảnh báo.
4. **Toạ độ tay** (`"latlon"`) từ hồ sơ / KMZ.
5. Không có nguồn nào → **hỏi user**, không vẽ.

## Quy trình khi được gọi

0. **Khảo sát tự động** (`khao_sat.py`, run.py tự gọi khi có `--ten` mà chưa có hồ sơ; ~1–3 phút, phần lớn là chờ Overpass):
   - **Tìm địa điểm**: Photon (photon.komoot.io — Nominatim bị chặn DNS trên máy này) khoanh Việt Nam, bỏ đường/nhà lẻ/cửa hàng;
     chấm điểm = khớp tên (so với MỌI cách gọi: tên user gõ + `ALIAS`) + loại đối tượng + thứ hạng Photon. Ứng viên tốt nhất chỉ là
     điểm lặt vặt → lấy làm MỐC, chọn công trình nổi bật nhất quanh 250 m (wikidata, chiều cao, diện tích). Tên in ra = chữ user gõ.
   - **Vùng**: đối tượng ≥ 1,5 ha (hồ, khu đất, quảng trường) → `vung` (ranh): viền vàng phát sáng, khoảng cách đo từ MÉP vùng,
     đường đi xuất phát từ điểm ranh gần đích nhất. Đối tượng là HỒ → chương "Ven hồ": icon chạy hết bờ, chùa/đền ven bờ bật dọc đường.
   - **Hạ tầng ĐANG VẬN HÀNH** (luật cứng ở trên): metro = ray `subway|light_rail|monorail` + ga trong 90 m quanh ray đó (ga của tuyến
     quy hoạch cũng gắn `railway=stop` — vd "Ga Lê Đức Thọ T5.07"); hai đầu tuyến = cặp ga xa nhau nhất trên TOÀN tuyến đang chạy.
     Trục lớn = vành đai/đại lộ/cao tốc/xa lộ/quốc lộ có đoạn LIỀN ≥ 2,5 km (OSM chỉ gắn tên "Vành đai 1" cho vài khúc → bỏ, kẻo nét
     cụt); thiếu thì lấy trục chính dài gần đó. Cầu lớn = `bridge` + tên "Cầu …" ≥ 450 m, ≤ 15 km, 2 cầu khác hẳn nhau. Sân bay có IATA
     ≤ 40 km, chấm ở nhà ga quốc tế. Tiện ích = có wikidata / TTTM / SVĐ / bệnh viện / đại học / bến xe / hồ ≥ 8 ha / công viên ≥ 5 ha;
     bỏ cơ quan, phòng khám, khách sạn, sông/kênh/rạch, thứ đang xây; hai điểm < 180 m giữ một.
   - **Xếp chương** (≤ 4 điểm có nhãn/chương): Ngay cửa nhà (dự án) | Ngay sát bên (địa danh) | Ven hồ (hồ) · Vành đai & trục lớn ·
     Metro đang chạy · Tiện ích quanh đây · Cầu & sân bay (spotlight). Chương rỗng tự bỏ. Đường đi tới tiện ích không vào chú giải.
   - Hồ sơ viết tay (dự án BĐS có tài liệu bán hàng, logo, phối cảnh) vẫn dùng được: `--brief du_an.json` như cũ.
   **Claude PHẢI soát `du_an.json`** trước cổng duyệt: tên trên nhãn/tên ngắn (tự rút gọn: SVĐ, TTTM, BV, ĐH, KDL, SB; bỏ đuôi
   "Hà Nội/TP.HCM"), điểm nào lạc đề thì xoá, user muốn thêm điểm nào thì thêm (tra toạ độ OSM).
1. **Bước 1 — kế hoạch + xem trước** (~30 s):
   ```bash
   python .claude/skills/nns-ban-do-ha-tang/scripts/run.py --brief <du_an.json> --work <thư mục>
   ```
   In BẢNG DUYỆT (chương, tuyến + nguồn, nhãn + khoảng cách chim bay/theo tuyến/hồ sơ, mốc giây, vòng km, ngưỡng máy quay,
   SFX, ⚠ cảnh báo), dựng `xem_truoc_*.jpg` rồi dừng (mã 2). **Claude MỞ ẢNH XEM TRƯỚC RA NHÌN**, sửa hồ sơ tới khi hết ⚠ quan trọng.
   Xem thêm khung bất kỳ: `render.py --plan <work>/plan.json --frames 6.5,24 --outdir <thư mục>` (~1 s/khung).
2. **CỔNG DUYỆT (1 lần)** — gửi bảng + ảnh xem trước, hỏi các dialog. User giục / bảo cứ làm → tự chọn theo đề xuất, nói rõ đã chọn gì.
3. **Bước 2 — dựng + tự kiểm** (~3–4 phút / 32 s, 6 tiến trình): thêm `--render [--out <ra.mp4>]`.
   Ra MP4 + `verify.json`. `ĐẠT 9/9` mới giao; mục trượt → sửa gốc rồi dựng lại.
4. **Giao** file + 1 dòng mỗi lớp (số chương/tuyến/nhãn/SFX, nhạc, LUFS/TP, kết quả tự kiểm), nêu rõ số liệu nào lệch hồ sơ.
   Rồi **bồi nhật ký** cuối file này.

## CÁC DIALOG SKILL PHẢI HỎI (một lần, ở cổng duyệt — LẦN NÀO CŨNG HỎI, lựa chọn cũ chỉ là đề xuất)

| # | Hỏi | Đề xuất mặc định | Bắt buộc |
|---|---|---|---|
| 1 | Đúng địa điểm chưa (khảo sát in OSM đã chọn + các ứng viên khác) + tên in trên thẻ, có logo PNG không | ứng viên điểm cao nhất, tên user gõ | ✔ |
| 2 | Danh sách hạng mục theo chương — thêm/bớt điểm nào | theo khảo sát tự động (hoặc tài liệu bán hàng user gửi) | ✔ |
| 3 | Nguồn hình học từng tuyến (OSM / ảnh / toạ độ) — tuyến OSM không có thì xin ảnh quy hoạch | OSM nếu có | ✔ |
| 4 | Khoảng cách in ra: số hồ sơ hay số đo (chim bay) khi lệch > 15 % | số hồ sơ + báo lệch | ✔ khi lệch |
| 5 | Nhạc nền: file nào (KHÔNG tự tổng hợp) | file trong thư mục dự án | ✔ |
| 6 | Bìa: 2 dòng tiêu đề + dòng phụ | "HẠ TẦNG GIAO THÔNG / QUANH <TÊN>" | |
| 7 | Ảnh phối cảnh cắt theo ranh lô có không | có thì dùng | |
| 8 | Khung kết (tên + hotline) / watermark | không | |

## Tự kiểm (`verify.py`, trên file cuối)
1 định dạng (đếm khung thật) · 2 −14 ±1 LUFS, TP ≤ −1 · 3 không khe im ≥ 0,1 s · 4 từng SFX khớp mẫu sóng trong âm thanh cuối đã trừ nhạc,
lệch ≤ 1 khung · 5 đỉnh SFX ≥ nhạc + 1 dB · 6 máy quay ORB+RANSAC từng cặp khung (p99 trong ngưỡng, tối đa ≤ +15 %) · 7 SIFT khung cuối ↔ Esri
ở mỗi chương, lệch ≤ 3 px · 8 nhãn trong vùng an toàn, chồng nhau ≤ 6 % (chỉ khi `EDGE_FIT = True` thì nhãn ghim sát mép mới được cắt ngang — liệt kê ở `cat_o_mep_da_cho_phep`; kiểu A đã chốt thì mọi nhãn ra ngoài đều tính trượt) · 9 đủ tile.

## Bẫy đã gặp

- **Overpass**: `overpass-api.de` hay báo 502 "at capacity", kumi/private.coffee trả 500 → `geo.overpass` luân phiên 4 mirror; `maps.mail.ru` chạy được (17/10/2026). POST bằng requests (chữ có dấu qua curl Git Bash hỏng âm thầm). Truy vấn điểm dùng `out center` (cầu là way nhiều khúc, `out geom` của 0,7° quanh Hà Nội làm mirror 500).
- **Đường đôi trong OSM** (2 làn ngược chiều) bị nối thành chữ U nếu chỉ xét đầu mút gần → cấm nối quay đầu (`geo._uturn`). Tuyến đang thi công rời khúc 100–250 m → dung sai 250 m. Có nhiều chuỗi → chọn chuỗi **gần dự án nhất**, không phải dài nhất (vành đai 4 dài nhất đi cách dự án 11,8 km, chuỗi đúng 2,6 km). Cầu là way riêng → thêm tên cầu vào regex tuyến (`^(…vành đai 4…|Cầu Mễ Sở)$`) kẻo thủng nét ở cầu.
- **"Theo tuyến" phình 10–45 %** khi tuyến lấy từ ảnh (nét gợn) → mặc định khoảng cách CHIM BAY. Mẫu KB5 ghi Ga 10 ~5,6 km (đo chim bay 5,2), Ga 9 ~10,1 (9,8), Cầu Ngọc Hồi ~11,0 (đo 14,3 — lệch 30 %, có thể mẫu đo theo đường hoặc tới đầu cầu).
- **Tách tuyến từ ảnh**: nối khúc kiểu tham lam nổ O(n³) và nối lung tung → dùng đồ thị xương + Dijkstra; loại đốm trắng gọn-đặc (ruột ghim, chữ) nhưng GIỮ viền trắng dài của chính nét; mảng dày (linh vật, thẻ) loại theo distance transform > 2,2× nửa bề dày trung vị.
- `cv2.warpAffine` với ma trận đích→nguồn phải kèm `WARP_INVERSE_MAP` — quên thì ảnh phối cảnh co lại còn một vòng tí hon.
- **Nhãn đặt theo khung cuối chương là SAI** khi máy quay còn trôi (spotlight): nhãn đúng ở cuối nhưng chồng nhau lúc hiện → đặt từng nhãn theo camera **tại lúc nó hiện**, và cho nhãn cũ nhường/thu gọn.
- **Thẻ dự án hai bản chồng** khi một khung đứng yên rơi đúng ngưỡng đổi thẻ to/nhỏ → `plan.py` dời ngưỡng khỏi mọi khung đứng yên ±8 %, dải hoà hẹp.
- **Đo BPM tự tương quan sai 4 %** (130,8 vs 125,6) → không cắt vòng lặp theo BPM; lặp nguyên file.
- **True peak vượt +1,7 dB** khi limiter chạy ở 48 kHz (SFX pop/ting nhiều cao tần) → limiter ở 192 kHz. Rồi **AAC đẩy đỉnh thêm ~1,4 dB** (WAV −1,8 → MP4 −0,4 dBTP) → trần limiter thấp hơn TP `AAC_HEADROOM` = 1,3 dB; luôn đo TP trên file MP4 cuối.
- **Whoosh dâng chậm**: `whoosh.wav` đỉnh ở 2,55 s sau onset — canh onset thì tiếng to nhất đến khi máy quay đã dừng. Loại trong `SFX_PEAK` canh ĐỈNH vào mốc hình (giữa cú bay). Đo "nghe rõ" phải tìm đỉnh trong 3 s, không phải 0,4 s đầu (đo 0,4 s báo trượt oan −3 dB).
- **Ghim sát mép khung**: nhãn hết chỗ phía trên → bị đẩy sang trái, đứng ngay trên ghim KHÁC (đọc nhầm "Sân bay Gia Bình" thành nút giao). Sửa ở MÁY QUAY: `fit_with_labels` khớp khung chừa ±170 px ngang / 150 px dọc cho nhãn từng ghim; thêm luật nhãn phải gần ghim của nó hơn mọi ghim khác (+120 điểm phạt).
- **Nhãn ngắn đặt xa ghim** thì không biết của ghim nào → chỉ 6 vị trí sát ghim; không vừa thì ẩn tên (ghim vẫn còn).
- Tự kiểm toạ độ: khung spotlight tối + zoom gần có thể chỉ còn 22–24 điểm khớp SIFT mà lệch vẫn chỉ 0,5 px → ngưỡng tối thiểu 15 điểm, phán theo độ lệch (≤ 3 px), đừng phán theo số điểm khớp (ngưỡng 25 từng báo trượt oan).
- Tuyến không có điểm nào (tuyến 5, R1) phải giới hạn `ve_km` hoặc `den`, không thì vẽ hết bán kính, khung chương bị kéo rộng và chữ nhỏ đi.
- **Điểm mốc nằm xa đường** (sân vận động, sân bay, bến xe, TTTM): có `latlon`/`osm` mà cách tuyến > 300 m (`POI_OFF_ROUTE_M`) → ghim + km theo VỊ TRÍ THẬT; mốc giờ vẫn theo chỗ icon chạy qua gần nhất. Kéo ghim vào đường làm sai km (SVĐ Mỹ Đình 0,8 thay vì 1,6 km).
- **Nhãn bị đẩy xa ghim** (ghim chật, sát nhau): có đường dẫn trắng mảnh từ đầu ghim tới mép nhãn khi xa > `LEADER_MIN` px. Ghim DỰ ÁN cũng tính trong luật "gần ghim mình nhất"; phạt nhầm ghim = `WRONG_PIN_PENALTY` 400 (120 thua phạt chồng nét).
- **Mọi chương** (không chỉ spotlight) khớp khung bằng `fit_with_labels` — ghim cách mép < 200 px thì nhãn bị đẩy sang đứng cạnh ghim khác.
- **Đặt nhãn theo THỜI GIAN**: ghim sắp mọc trong lúc nhãn còn đứng cũng là vật cản; nhãn mới né nhãn đầy đủ đang đứng trước, chỉ bắt nhãn cũ nhường khi hết chỗ (không thì nhãn cũ chỉ sống 0,7 s); nhãn ngắn né mọi nhãn đầy đủ còn đứng trong khoảng hiện của nó; chương spotlight đặt theo khung lúc nhãn sắp thu gọn (máy còn lùi ra).
- **Một chương ≤ 3–4 điểm có nhãn**: 6 điểm/chương (VĐ3 + metro 3 + 2A) là quá tải → tách chương. Hai tuyến chạy chồng nhau (Metro 5 dọc Đại lộ Thăng Long) → gộp 1 nét, ghi chú ở nhãn phụ.
- Thẻ dự án: chỉ "The" nhỏ phía trên ("The / Matrix One"), không cắt chữ cuối ra dòng to; thu thành chip khi khung rộng > `CARD_MINI_KM` 4 km (9 km để thẻ to che ga sát nhà). Chú giải tên dài tự co cho vừa khung.
- `run.py` xoá khung xem trước CŨ (do chính nó sinh) mỗi lần chạy — không thì tấm ghép trộn khung cũ/mới.
- **Không có nhạc (chỉ SFX)**: đừng lấy mức nhạc (= 0) làm chuẩn đặt SFX — SFX thành −100 dB rồi master +56 dB. Nền giả `SFX_NO_MUSIC_REF` −22 dB; KHÔNG chuẩn −14 LUFS tích phân (đa phần là lặng) mà đẩy theo độ to TỨC THỜI lớn nhất ≈ −12 LUFS-M; tự kiểm bỏ qua mục "khe im". Đo LUFS-M bằng `ebur128=metadata=1,ametadata=print:key=lavfi.r128.M` (đừng lọc dòng log theo chữ "TARGET" — dòng nào cũng có).
- Chữ chương dài ("Vành đai 3 · Phạm Hùng") tự co cho vừa vùng an toàn.
- **Soát từng khung** (user 17/10: "làm chi tiết vào, để ý từng cái nhỏ nhất"): trước khi giao, dựng khung mỗi 1,2 s + mỗi 0,25 s ở các
  đoạn chuyển (nhãn nhường nhau, icon bật, đổi chương) và NHÌN hết. Lần Matrix One soi ra 15 lỗi mà tự kiểm chưa bắt — đã thêm vào
  tự kiểm: ghim chồng ghim, thẻ dự án vào bộ hộp chữ (chữ đè thẻ / thẻ cụt mép), nhãn tính cả lúc đang mờ dần.
- **Đường dẫn nhãn→ghim (vạch trắng) đã BỎ** — user hỏi "mấy cái này là gì". Nhãn đầy đủ chỉ đặt ở 8 vị trí KỀ ghim; chật thì nhỏ còn
  0,82; nhãn cũ nhường thì nhãn mới CHỜ nhãn cũ mờ hết rồi mới hiện (`t_label`), nhãn ngắn hiện sau khi nhãn đầy đủ tắt hẳn.
- **Thẻ dự án** chọn 1 phía cố định (trên/phải/trái/dưới) ít đè nét tuyến nhất; khung mỗi chương chừa trọn thẻ (AEON: thẻ cụt mép phải).
  Thẻ vẽ SAU icon phương tiện → icon bật ra từ sau thẻ, không đè chữ tên dự án.
- **Nhãn tuyến** phải gần nét của mình hơn mọi nét khác ("LÊ QUANG ĐẠO" từng nằm trên Đại lộ Thăng Long).
- **Tuyến vẽ 2 chiều**: icon chiều 2 chờ icon 1 chạy ra ≥ 2,6 bán kính icon (tính cả 0,25 s đứng chờ) — trễ cố định 0,3 s vẫn chồng.
- **Ghim chồng nhau** (2 điểm < ~100 m, vd Bảo tàng HN – TT Hội nghị): giữ 1 điểm. Ghim chương trước chồng ghim chương mới → mờ đi
  trong chương đó (gộp khoảng ẩn liền nhau, nối tới hết nếu khung kết cũng ẩn — không nhấp nháy). Khung kết ẩn ghim kém ưu tiên
  nằm gần ghim khác < 46 px; tên ngắn ở khung kết không được chạm thẻ dự án.
- **Vòng km**: bỏ vòng bán kính màn hình < 130 px; nhãn km chọn trong 10 góc chỗ ít đè nhất, vẽ trên nét tuyến.
- **Chữ chương** coi ghim đang hiện là vật cản (từng đè ghim SVĐ) — có thêm 3 vị trí hàng 2 phía trên.
- **Font thiếu glyph**: "→" trong Be Vietnam Pro hiện ô trống ở chú giải → `sprites.safe_text` tự thay "–" và cảnh báo.
- **Thẻ dự án là vật cản CỨNG** (`CARD_HARD` 12): chữ không bao giờ chạm thẻ; ở chương spotlight máy còn lùi nên nhãn được kiểm
  thẻ + vùng an toàn suốt thời gian nó hiện (12 mẫu, tới hết lúc mờ). Phía đặt thẻ chọn có tính cả khung mở đầu và giữa các cú bay
  (thẻ "Landmark 81 · Phường Thạnh Mỹ Tây…" dài tràn mép trái lúc mở đầu).
- **Không có chỗ hợp lệ sát ghim** (điểm > `FULL_FAIL_SCORE` 900) → KHÔNG hiện nhãn đầy đủ, chỉ tên ngắn sát ghim (hoặc chỉ ghim).
  Đặt đại thì nhãn đứng cạnh ghim KHÁC — "CẦU CHƯƠNG DƯƠNG" từng nằm giữa 2 ghim metro, cách ghim cầu 300 px (Hồ Tây 17/10).
- **Ghép tiếng KHÔNG dùng `-shortest`**: luồng AAC luôn ngắn hơn chút → cắt mất 4 khung cuối. Dùng `-af apad -t <thời lượng plan>`.
- **Whoosh của cú bay sớm** (nhịp nhanh: cú bay đầu lúc ~1,4 s, đỉnh whoosh ở 2,55 s sau onset) → cắt bớt ĐẦU tiếng (`skip` trong
  cues.json) để đỉnh vẫn rơi giữa cú bay. Tự kiểm so mẫu ở đoạn 0,15 s TO NHẤT của tiếng, không ở 0,15 s đầu (whoosh đầu gần câm → r ≈ 0).
- **Nhãn tuyến đè nhãn điểm / chạm ghim** (Matrix One 18/10: "VÀNH ĐAI 3" đè "TT HỘI NGHỊ", "Nhổn – Cầu Giấy" chạm đầu ghim SVĐ,
  tự kiểm chưa bắt vì không đo chữ↔ghim): nhãn tuyến đặt TRƯỚC nhãn điểm chỉ đoán chỗ bằng vùng chừa quanh ghim — vùng đó không phủ
  8 chỗ kề ghim (nhãn nằm DƯỚI ghim lọt ra ngoài). Nay có **lượt 2**: nhãn điểm chốt xong thì đặt LẠI nhãn tuyến né đúng hộp nhãn điểm
  (đầy đủ + tên ngắn); dò **cả 2 nhánh** vẽ; chạm ghim (±6 px) phạt `LABEL_ON_PIN_PENALTY` 2000 (phạt theo diện tích thì chạm mép
  ghim chỉ ~20 điểm). Vẫn chật (tuyến ngắn kẹp giữa cụm ghim, metro 3 vẽ 2,2 km) → tăng `ve_km` trong hồ sơ cho nét có khúc trống.
- **Thẻ dự án lố mép ở khung mở đầu** khi dòng phụ dài ("Số 1 Lê Quang Đạo · Nam Từ Liêm" 478 px > 466 px nửa khung): dự án đứng
  giữa khung nên thẻ trái/phải không vừa → máy quay mở đầu tự lệch tâm cho thẻ trọn vùng an toàn.
- **Khung "Ngay cửa nhà" nhìn quá xa** khi trục lớn không có điểm vẽ dài (Đại lộ Thăng Long `ve_km` 2,4 → 3 điểm sát nhà dồn vào
  một góc) → `ve_km` 1,4: máy đẩy gần, nhãn tách ra.
- **Tìm địa điểm khớp nhầm khi tên kèm thành phố** (bản zip thử 18/10): "Chợ Hàn Đà Nẵng" ra "Nhà thi đấu Đa Năng" ở Đồng Nai —
  so tên BỎ DẤU ("da nang" khớp "Đa Năng"), chỉ cộng điểm khi khớp NGUYÊN cụm (tên đúng "Chợ Hàn" không được điểm vì câu gõ dài
  hơn), hạng mục SVĐ +4 thắng. Sửa: `tach_ten()` + so tên giữ dấu theo tỷ lệ chữ + thưởng đúng tỉnh/thành; mốc là chợ thì ưu tiên
  công trình mang đúng tên mốc. Thử lại 9/9 câu gõ (Chợ Hàn ×2, Lăng Bác, Hồ Tây, Landmark 81, Matrix One kèm địa chỉ, Cầu Rồng,
  Nhà thờ Đức Bà, Vinhomes Ocean Park).
- **Khảo sát chọn điểm trùng** (Chợ Hàn 18/10): (1) cầu/sân bay đã có chương "Cầu & sân bay" vẫn được gắn làm tiện ích dọc trục
  lớn → `build_brief` giữ chỗ trước cho cầu + sân bay; (2) lọc "< 180 m giữ một" chạy TRƯỚC khi ghim công trình lớn dời về mép gần
  nhất → lọc lần 2 theo ghim cuối + bỏ điểm nằm TRÊN công trình đã chọn (< 80 m tới nét): "Dragon's Tail/Head" là mảnh của Cầu Rồng;
  (3) nhãn 2 dòng ngắt giữa từ ghép ("BẢO TÀNG MỸ / THUẬT") → `LABEL_HEADS` + `LABEL_PAIRS`; (4) khoảng cách sân bay ở bảng khảo sát
  đo tới tâm sân bay, ghim cắm ở nhà ga → đo tới nhà ga.
- **File không có giọng**: Whisper bịa câu "Hãy subscribe cho kênh…" — dấu hiệu chỉ có nhạc, không phải lời thật.
- Video mẫu TikTok: kiểm watermark/end card trước khi đo; mẫu KB5 không có end card.

## Skill này được bồi thêm sau mỗi lần chạy thật

| Ngày | Video | Học được |
|---|---|---|
| 17/10/2026 | Dựng lại The CityOn (thử nội bộ, nhạc = trung vị 3 vòng nhạc mẫu, KHÔNG đăng) → `_bandoht_cityon/work/The_CityOn_ban_do_ha_tang.mp4` 38,6 s | toàn bộ mục "Bẫy đã gặp"; khung mẫu dò ra dự án ở 20,95839 N 105,98528 E (SIFT 1821 điểm khớp z16); tuyến 8/5/R1/VĐ3.5 lấy từ khung 45,5 s của mẫu bằng trace_lines (`--via`), VĐ4 + đường Gia Bình lấy OSM (lệch so nét mẫu trung vị 20–35 m). Tự kiểm lần 1 ĐẠT 6/9 (TP, khe im ở nhạc thử, SFX nhỏ) → sửa gốc → **9/9**: −14,5 LUFS, TP −1,8, 21 SFX lệch 0 ms, lia p99 13,5 px/khung, zoom p99 3,8 %/khung, toạ độ lệch ≤ 0,12 px (≤ 4,5 m) ở 5 khung. Cùng 3 chương nhưng ngắn hơn mẫu (38,6 vs 46,7 s); cú bay đầu tự kéo dài 3,8 s cho đạt ngưỡng êm |
| 17/10/2026 (2) | Góp ý của user trên bản thử The CityOn | user chọn "zoom sát như mẫu, chấp nhận sân bay nằm ở mép, nhãn có thể bị cắt" → thêm `EDGE_FIT` / `EDGE_PAD` / `EDGE_CROP_ZONE` trong `common.py`; chương spotlight + khung kết khớp theo mép khung thật; nhãn ghim sát mép được tràn; verify mục 8 tách "cắt ở mép (đã cho phép)" |
| 17/10/2026 (3) | User so 2 bản A/B | **chốt kiểu A** ("giữ trọn nhãn, bản đồ nhìn xa hơn cũng được") → `EDGE_FIT = False`; kiểu B giữ lại trong mã làm tuỳ chọn nhưng KHÔNG dùng khi chưa được hỏi. Bài học: "giống mẫu" không phải lúc nào cũng thắng — user ưu tiên đọc được chữ hơn khung sát. Bản giao: `_bandoht_cityon/work/The_CityOn_ban_do_ha_tang.mp4` (= kiểu A, 9/9); kiểu B lưu `…_v2_sat_mep.mp4` |
| 17/10/2026 (4) | **The Matrix One** (MIK Group, Lê Quang Đạo – Mễ Trì) → `_bandoht_matrixone/work/The_Matrix_One_ban_do_ha_tang.mp4` — lần chạy thật đầu tiên trên dự án mới | toạ độ dự án lấy từ OSM (relation "The Matrix One" 21,009183 N 105,774146 E); mọi tuyến/ga/điểm từ OSM (metro 5 quy hoạch, 3, 2A; VĐ3; Lê Quang Đạo; VĐ3–Thăng Long ra Nội Bài; Võ Chí Công – Nhật Tân). User: chỉ SFX (không nhạc), SVĐ in "~1 km" theo quảng cáo (đo 1,6), không khung kết, thêm Keangnam/Bảo tàng HN/AEON Hà Đông/cầu Nhật Tân. 4 chương: Ngay cửa nhà · Vành đai 3 · Metro đang chạy · Cầu & sân bay. Các luật đặt nhãn theo thời gian + đường dẫn ở mục Bẫy sinh ra từ lần này |
| 17/10/2026 (5) | The Matrix One — góp ý của user sau bản 1 | (1) "metro 5 có chưa" → luật CHỈ HẠ TẦNG ĐÃ VẬN HÀNH (bỏ metro 5 đang xây; lọc OSM theo trạng thái); (2) "đoạn đỏ từ SVĐ tới toà nhà thiếu" → nguồn `duong_di` định tuyến thật; (3) "mấy cái này là gì" → bỏ vạch dẫn nhãn; (4) "làm chi tiết, để ý từng cái nhỏ nhất" → soát 35 + 12 khung, sửa 15 lỗi nhỏ (xem Bẫy). Bản 1 lưu `The_Matrix_One_v1_co_metro5.mp4` |
| 17/10/2026 (6) | **Gọi bằng tên địa điểm bất kỳ** — user: "đóng lại vào skill, sau này đưa Lăng Bác, Hồ Tây, Landmark 81… là ra video kiểu kia" | thêm `khao_sat.py` + `run.py --ten`; chạy thử Lăng Bác (Hà Nội), Hồ Tây (vùng 530 ha, chương Ven hồ), Landmark 81 (TP.HCM — OSM tên "Vincom Center", metro 1, cầu Sài Gòn 2, Tân Sơn Nhất). Bẫy: Photon lọc chặt mất Landmark 81 → tìm thả lỏng lấy mốc; `out tags` không trả toạ độ node, `out center bb` chỉ giữ bb → hàm `cen()`; ga của tuyến quy hoạch gắn railway=stop → lọc ga theo khoảng cách tới ray đang chạy; đầu tuyến phải lấy trên toàn tuyến (2A từng ra "La Thành – Cát Linh"); khung bao đường dài (Phố đường tàu) thổi điểm diện tích → chỉ cộng cho đối tượng dạng vùng; rút gọn tên bỏ theo CẶP từ cuối ("HOÀNG THÀNH", không "HOÀNG THÀNH THĂNG"); hồ thì giữ điểm ven bờ/trên đảo (Chùa Trấn Quốc) với dòng phụ "ngay bên hồ" |
| 18/10/2026 | User: "xem video cứ thấy hơi chậm" | đo nhịp: bản cũ 1 sự kiện/1,3 s (dày hơn mẫu 1,7 s) nhưng 7 khe > 2 s cộng 24 s ≈ nửa video, toàn ở chuyển chương (chờ sau nét cuối 1,4–1,8 s + bay 1,2–2 s + chữ chương lúc tới nơi) và nét vẽ chậm 250 px/s ease sin. Sửa: bảng "Nhịp chương" + dòng "Tuyến" ở trên; giữ nguyên ngưỡng máy quay êm. Kết quả: Matrix One 43 → 28 s, Lăng Bác 50 → 32 s, Hồ Tây 45 → 28 s, Landmark 81 49 → 29 s; khe còn lại đều nằm trong lúc máy bay/nét đang vẽ |
| 18/10/2026 (2) | User: "mấy chữ title này màu vàng nhé, sửa trong skill, không cần render lại" | chữ chương đổi trắng → vàng gradient + viền nâu (`common.CHAPTER_TOP/BOT/EDGE`); video cũ giữ nguyên |
| 18/10/2026 (3) | User: "bỏ mấy kiểu chữ uốn lượn này đi, cho nhìn rõ chữ… chữ giữa đó không biết là chữ gì" | mọi chữ thư pháp (Great Vibes) → Be Vietnam Pro Black (`common.F_TITLE`): chữ chương 80 px vàng viền nâu 4 px, dòng phụ bìa trắng viền tối. KHÔNG dùng lại font uốn lượn cho chữ cần đọc |
| 18/10/2026 (4) | **The Matrix One gọi bằng tên + địa chỉ** ("Số 1 Lê Quang Đạo, ngã tư Lê Quang Đạo – Mễ Trì") → `_bandoht_matrixone_ten/The_Matrix_One_ban_do_ha_tang.mp4` 27,3 s, nhịp + chữ mới 18/10 | khảo sát tên tìm đúng relation OSM, nhưng bộ điểm tự động lệch bộ user đã chốt (thiếu AEON, cầu Nhật Tân; thừa cầu Chương Dương, Bảo tàng Hậu Cần) → ghép: bộ đã chốt + điểm mới đáng giá của khảo sát (Cung Hữu nghị Việt – Trung 0,5 km, tra báo: khánh thành 11/2017). Dự án đã có hồ sơ cũ thì chép cache `osm/` sang + dùng đúng `vi_tri` cũ → truy vấn trùng khoá, khỏi chờ Overpass (khảo sát thô mất > 10 phút vì mirror chậm). User chọn hết theo đề xuất (dòng phụ thẻ theo địa chỉ user gõ, SVĐ ~1,0 km, chỉ SFX). Tự kiểm lần 1 ĐẠT 8/9 (thẻ lố mép lúc mở đầu) → sửa gốc → 9/9; soát 91 khung file cuối bắt thêm 2 lỗi nhãn tuyến mà tự kiểm không thấy → lượt 2 đặt nhãn tuyến (xem Bẫy) → 9/9: TP −2,7, 34 SFX lệch 0 ms, lia p99 8,8 px/khung, zoom p99 4,9 %, toạ độ lệch ≤ 0,2 px |
| 18/10/2026 (5) | **Đóng zip gửi người khác** (user: "ngta tải về giải nén là chạy được, điền địa điểm nào vào gọi skill ra là chạy ngon") → `Output/chia_se_skill/nns-ban-do-ha-tang.zip` (+ `nns-video-ban-do.zip`); đóng lại: `python tools/dong_goi_skill.py <skill…>` | thêm `CAI_DAT.bat` / `CAI_DAT.command` → `scripts/cai_dat.py` (chép vào `~/.claude/skills`, pip, hỏi cài ffmpeg, kiểm tra) + `scripts/kiem_tra_cai_dat.py` + `requirements.txt` + `HUONG_DAN_CAI_DAT.md`; cache về `~/.cache/nns_ban_do` khi cài cho mọi dự án (`NNS_TILE_CACHE` để tự chọn); font xem trước không còn trỏ C:/Windows. Thử trên venv SẠCH từ zip: Matrix One 9/9; gọi bằng tên "Chợ Hàn Đà Nẵng" lộ 4 lỗi khảo sát → sửa (xem Bẫy): khớp nhầm nhà thi đấu "Đa Năng" ở Đồng Nai, Cầu Sông Hàn hiện 2 lần, "Dragon's Tail/Head" (mảnh của Cầu Rồng) thành tiện ích, nhãn ngắt "MỸ / THUẬT"; sân bay tóm tắt đo tới tâm sân (4,0) thay vì nhà ga cắm ghim (2,7) |
