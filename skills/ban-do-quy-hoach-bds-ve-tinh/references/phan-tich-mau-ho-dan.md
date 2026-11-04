# Phân tích video mẫu `ho_dan.mp4` (kênh MINH ĐOÀN) — dạng "bản đồ + bất động sản"

Nguồn: `F:\VIDA_TEST\0411\ho_dan.mp4` · 576×1024 (9:16, bản tải TikTok, gốc chắc 1080×1920) · 30 fps · 161,4 s · AAC 32 kbps.
Tờ khung theo giây + khung full-res: thư mục `khung_theo_giay\` cạnh file này.

---

## 1. Kết luận nhanh

| Mục | Video mẫu làm thế nào | Tự động hoá từ 1 file audio được không |
|---|---|---|
| Nền hình | **Quay màn hình Google Earth** (thấy con trỏ chuột ✋ ở 62 s, 128 s; ô bản đồ chưa tải ở 76 s) + **quay màn hình app GIS quy hoạch** (nút định vị tròn ở 95 s, thước đo "450.2743" ở 87–90 s, thanh công cụ ở 83 s, 142 s) | **Được, và tốt hơn**: kéo ô ảnh vệ tinh Esri World Imagery (đã có `ban_do.py` của minh-tam-edit), lấy tim sông/đường từ OpenStreetMap, cho "camera" trượt dọc tuyến → không có con trỏ, không ô trống, toạ độ đúng tuyệt đối |
| Bản đồ tổng 3 đoạn (44–56 s) | Dựng bằng code: nền Esri tối đi, sông vẽ xanh lơ, đoạn đang nói vẽ vàng chạy dần (có ghi "Ảnh: Esri World Imagery · Dòng sông: © OpenStreetMap") | Được 100% — cùng stack với `ban_do.py` |
| Lớp quy hoạch màu (70–125 s) | Quay màn hình app quy hoạch (vùng chấm xanh, đê xanh lá, tim kênh xanh dương đứt, đường tím/hồng) | **Khó**: cần nguồn tile quy hoạch; thay bằng lớp tự vẽ (hành lang 500 m, 2 tuyến đê, ranh xã) từ dữ liệu OSM + số trong công văn |
| Chữ dưới (sub) | **Không phải sub nguyên văn** — 47 "thẻ ý" 2 dòng (trắng + vàng), mỗi thẻ 2–5 s, tóm nghĩa + nhấn số | Được: Whisper → sửa lỗi → LLM viết 2 dòng/cụm (có luật) |
| Thẻ tài liệu | 9 thẻ navy ở 1/3 trên, chứa ảnh cắt từ hồ sơ đề xuất (sơ đồ tuyến, mặt cắt, bảng số) + dòng "Nguồn: …" | Được: người dùng đưa ảnh công văn → OCR → tự đặt vào đúng lúc lời nhắc tới số/tên trong ảnh |
| Nhân vật / địa danh | Video mẫu **không** chèn ảnh người hay ảnh địa danh nào — chỉ bản đồ | Địa danh → bản đồ: tự động 100%. Ảnh địa danh: bán tự động (có cổng duyệt). Ảnh nhân vật: **không nên tự chèn** (xem mục 7) |
| Âm thanh | Chỉ giọng đọc, không nhạc nền, 1 tiếng "ding" nhỏ lúc vào bản đồ tổng (43,8 s); nén rất mạnh: −10,3 LUFS, true peak **+2,6 dBTP (vỡ)**, LRA 2,2 | Chuẩn hoá −14 LUFS / −1 dBTP như 2 skill hiện có |

---

## 2. Cấu trúc thời gian (5 phần + hook + CTA)

| Giây | Phần | Nền hình | Đồ hoạ thêm |
|---|---|---|---|
| 0 – 3,8 | **Hook** | Google Earth zoom gần (khung ≈ 0,6 km ngang), làng ven khúc cong sông Đáy, 2 vạch vàng = hành lang ~500 m | Thẻ tiêu đề navy trên cùng (3 dòng) + thẻ ý 1 |
| 3,8 – 43,6 | **Đặt vấn đề** | Bay liên tục dọc sông, zoom gần, hướng Bắc cố định | 11 thẻ ý; 1 thẻ tài liệu (32–34,7 s: sơ đồ tuyến 110 km) |
| 43,6 – 56,2 | **Bản đồ tổng 3 đoạn** | Dựng bằng code (Esri tối + sông xanh lơ) | Thẻ đầu đề navy đổi 4 lần; đoạn vàng chạy dần ~2 s/đoạn; chữ cuối "Ảnh: Esri…" |
| 56,2 – 100 | **Hai phương án** | Google Earth (có lớp đường cao tốc xanh/hồng) → từ 70 s app quy hoạch (chấm xanh, đê, thước đo 450 m) | 13 thẻ ý; 3 thẻ tài liệu (mặt cắt PA1 61–64 s, PA2 66–70 s, PA2 80–83 s) |
| 100 – 123 | **Số liệu** | App quy hoạch; 119–125 s bản đồ sử dụng đất màu | 8 thẻ ý; 4 thẻ tài liệu (bảng: 3.002 ha 94–97 s, 6.068 hộ 97–100 s, 1.217 hộ 109–112 s, 1.074 hộ 114–117 s, 3.777 hộ 120–123 s) |
| 123 – 156,4 | **Lợi ích + cảm xúc** | Google Earth + **dùng lại** đúng đoạn quay 70–100 s (cảnh thước đo 450 m lặp ở 147–150 s) | 9 thẻ ý, không thẻ tài liệu |
| 156,7 – 159,4 | **CTA** | Nền đen, avatar tròn viền phát sáng xanh, logo MĐ, dấu tick, chữ "Nhớ Follow để / xem thêm nhiều video / từ kênh của mình!!!" quét hiện trái→phải 0,5 s | Cắt cứng vào/ra |
| 159,4 – 161,4 | Đuôi | Về bản đồ, không chữ, giọng nói "…mọi người nhé" | |

Điểm cắt cứng (scene > 0,3): 8,9 · 43,6 · 56,2 · 96,8 · 99,8 · 117,5–120,5 (5 nhát zoom liên tiếp) · 125,4 · 135,7 · 156,7 · 159,4. Còn lại là chuyển động liên tục (kéo chuột), 1 chỗ hoà tan ~1 s ở 125 s (lớp màu → vệ tinh).

---

## 3. Các lớp đồ hoạ — thông số đo được (quy về 1080×1920, nhân 1,875 từ bản 576×1024)

### 3.1 Logo kênh (luôn hiện)
- "MINH ĐOÀN" chữ serif trắng (kiểu Playfair Display), cao ≈ 56 px, góc phải trên, mép phải x ≈ 1012, tâm y ≈ 95.
- Thêm 1 logo "MĐ" vàng mờ ~25 % ở giữa khung (vị trí lệch theo từng đoạn quay → được dán vào từng clip nguồn, không phải lớp cố định).

### 3.2 Thẻ tiêu đề hook (0–3,8 s)
- Hộp navy `#0F2C52` (viền sáng hơn 1 px, bo ≈ 15 px), x 60–1020, y 202–345.
- Dòng 1 vàng `#FFD24D` Montserrat SemiBold ≈ 30 px: "SÔNG ĐÁY MỞ RỘNG 500M?"
- Dòng 2 trắng ≈ 30 px: "HƠN 6.000 HỘ DỰ KIẾN DI DỜI!"
- Dòng 3 xám nhỏ ≈ 16 px: "THEO HỒ SƠ ĐỀ XUẤT DỰ ÁN"
- Vào: có sẵn từ frame 0. Ra: **cắt cứng** ở 3,75 s (không fade).

### 3.3 Thẻ ý 2 dòng (lớp quan trọng nhất, 47 thẻ)
- Canh giữa, khối chữ tâm y ≈ 1580 (dòng 1 ≈ 1552, dòng 2 ≈ 1609) → **gần trùng y 1545 của sub minh-tam-edit**.
- Montserrat ExtraBold, IN HOA, cỡ ≈ 50–52 px, giãn dòng ≈ 1,45; dòng 1 trắng, dòng 2 vàng `#FFD24D`; bóng đen mờ 6–8 px (không viền cứng).
- Dòng 1 = bối cảnh (≤ 26 ký tự), dòng 2 = **con số / từ khoá** (≤ 28 ký tự). Không bao giờ 3 dòng.
- Vào/ra: **hoà tan nhanh 0,10–0,15 s** (3–4 frame), không trượt, không phóng, không karaoke.
- Thời lượng: ngắn nhất 2,0 s, dài nhất 5,0 s, trung bình 3,3 s; thẻ hiện **sớm hơn chữ đầu của cụm 0,2–0,5 s**.
- Thẻ **ẩn hoàn toàn** trong 2 giây đuôi (159,4–161,4 s) và khi CTA hiện.

### 3.4 Thẻ tài liệu (9 thẻ, mỗi thẻ 2,7–3,5 s)
- Hộp navy `#0F2C52` (đục ~95 %), bo ≈ 19 px, x 112–968 (rộng 856), y 300–825 (cao ≈ 525) → nằm trong 1/3 trên, **không bao giờ đè thẻ ý ở dưới**.
- Tiêu đề vàng Montserrat Bold ≈ 32 px IN HOA (vd "PHƯƠNG ÁN 2 · BỀ RỘNG MẶT 350–500 M"); ảnh bên trong viền trắng 2 px, giữ tỉ lệ; dòng cuối trắng ≈ 22 px "Nguồn: Báo cáo đề xuất • Phương án nghiên cứu".
- Vào: hoà tan + trượt xuống nhẹ (~20 px) trong 0,15–0,2 s. Ra: hoà tan 0,15 s.
- Cùng 1 ảnh bảng số được dùng lại 5 lần với tiêu đề khác nhau (3.002 ha → 6.068 hộ → 1.217 → 1.074 → 3.777) — tức là **1 ảnh công văn có thể sinh nhiều thẻ, tiêu đề đổi theo con số đang đọc**.

### 3.5 Bản đồ tổng 3 đoạn (43,6–56,2 s) — lớp "chuẩn template"
- Nền: Esri World Imagery, giảm sáng ≈ 40 %, giảm bão hoà ≈ 30 % để vạch nổi.
- Tim sông: polyline OSM màu xanh lơ `#4FC3F7` ≈ 4 px.
- Đoạn đang nói: vàng `#FFD24D` ≈ 9 px, **vẽ chạy dần từ điểm đầu tới điểm cuối trong ~2 s**, đầu vạch có chấm trắng chạy theo; 2 đầu có chấm trắng + nhãn IN HOA trắng ≈ 20 px ("SÔNG HỒNG", "ĐẬP ĐÁY", "BA THÁ").
- Thẻ đầu đề navy y 56–140: dòng vàng "ĐẬP ĐÁY → BA THÁ · 54 KM", dòng trắng "Chiều dài theo báo cáo đề xuất dự án".
- Chữ nguồn cuối khung y ≈ 1830, ≈ 17 px: "Ảnh: Esri World Imagery • Dòng sông: © OpenStreetMap".
- Trình tự: 43,6 s vào bằng cắt cứng + hiện toàn tuyến **thu nhỏ có 2 dải đen hai bên** (2 s) → 45,6 s **zoom phóng** 0,4 s vào đoạn 1 → vẽ đoạn 1 → cắt sang đoạn 2 (49 s) → đoạn 3 (52 s) → 56,2 s cắt cứng về vệ tinh.

### 3.6 Chuyển động camera (phần quay màn hình)
- Hướng Bắc cố định, không xoay, không nghiêng.
- Trôi đều dọc sông ≈ 40–60 px/s (ở 1080), thỉnh thoảng zoom chậm; 2 lần nhảy cảnh cứng (8,9 s; 60,3 s) và 1 chuỗi 5 nhát zoom (117,5–120,5 s) để "lặn" vào bản đồ màu.
- Tỉ lệ: zoom gần ≈ 0,6–1 km ngang khung (tương đương Esri z≈18); phần quy hoạch ≈ 2 km (z≈16); bản đồ tổng ≈ 60 km (z≈10).

### 3.7 CTA cuối (156,7–159,4 s)
- Clip dựng sẵn (nền đen, avatar tròn, viền phát sáng xanh, tick đỏ, chữ Oswald/Roboto Condensed Bold trắng quét hiện trái→phải). Dùng lại cho mọi video → **tài sản kênh** cần người dùng cung cấp 1 lần.

---

## 4. Bảng lời ↔ hình (28 cụm Whisper large-v3, đã ghi chú lỗi nhận dạng)

| Giây | Lời đọc (Whisper, *lỗi* → đúng) | Thẻ ý trên hình | Nền / thẻ tài liệu |
|---|---|---|---|
| 0,0–6,5 | Hơn 6.000 hộ dân có thể sẽ phải di dời… mặt cắt sông Đáy rộng tới gần 500 m | HƠN 6.000 HỘ DÂN / CÓ THỂ PHẢI DI DỜI → MẶT CẮT SÔNG ĐÁY / RỘNG TỚI GẦN 500 M | Thẻ hook + Google Earth làng ven sông, 2 vạch vàng |
| 6,5–14,9 | Nếu nhà đất của bạn nằm dọc 2 bên sông Đáy, đặc biệt Quốc Oai, *Trường Mỹ*→Chương Mỹ, Thanh Oai, Mỹ Đức… | NHÀ ĐẤT CỦA BẠN / DỌC HAI BÊN SÔNG ĐÁY? → QUỐC OAI · CHƯƠNG MỸ / THANH OAI · MỸ ĐỨC | Bay dọc sông (nhảy cảnh 8,9 s). **Không** tô ranh 4 huyện — chỗ template làm tốt hơn |
| 15,6–25,0 | Hồ sơ đề xuất… không chỉ *nạn*→nạo vét, khơi thông… mở rộng lòng sông, đê điều, giao thông 2 bên | HỒ SƠ ĐỀ XUẤT / DỰ ÁN CẢI TẠO SÔNG ĐÁY → NẠO VÉT · KHƠI THÔNG / DÒNG CHẢY → NGHIÊN CỨU MỞ RỘNG LÒNG SÔNG / ĐÊ ĐIỀU · GIAO THÔNG HAI BÊN | Bay dọc sông |
| 25,6–29,3 | Phạm vi ảnh hưởng đến đâu, bao nhiêu hộ phải di dời? | PHẠM VI ẢNH HƯỞNG ĐẾN ĐÂU? / BAO NHIÊU HỘ DỰ KIẾN DI DỜI? | Bay dọc sông |
| 29,3–31,3 | Thông tin sẽ được tham khảo trong video này | CÙNG ĐOÀN XEM KỸ / THÔNG TIN TRONG HỒ SƠ | Bay dọc sông |
| 31,3–42,7 | Theo báo cáo… 110 km, 23 xã và 2 phường, phạm vi 24.440 ha | CHIỀU DÀI NGHIÊN CỨU / KHOẢNG 110 KM → 23 XÃ VÀ 02 PHƯỜNG / THUỘC THÀNH PHỐ HÀ NỘI → PHẠM VI NGHIÊN CỨU / KHOẢNG 24.440 HA | **Thẻ tài liệu** "110 KM – 25 XÃ, PHƯỜNG" (sơ đồ tuyến) 32–34,7 s |
| 43,8–55,6 | Toàn tuyến 3 đoạn: *sông Hồng Hà*→sông Hồng → đập Đáy 12 km; đập Đáy → Ba Thá 54 km; Ba Thá → Ninh Bình 44 km | TOÀN TUYẾN / ĐƯỢC CHIA THÀNH 3 ĐOẠN → SÔNG HỒNG → ĐẬP ĐÁY / KHOẢNG 12 KM → ĐẬP ĐÁY → BA THÁ / KHOẢNG 54 KM → BA THÁ → ĐỊA PHẬN NINH BÌNH / KHOẢNG 44 KM | **Bản đồ tổng** dựng code, đoạn vàng vẽ dần đúng lúc đọc tên đoạn; SFX "ding" 43,8 s |
| 56,2–60,9 | Đáng chú ý là phương án cải tạo lòng sông; báo cáo nghiên cứu 2 phương án | ĐÁNG CHÚ Ý NHẤT / PHƯƠNG ÁN CẢI TẠO LÒNG SÔNG → BÁO CÁO NGHIÊN CỨU / HAI PHƯƠNG ÁN | Google Earth có lớp cao tốc xanh |
| 60,9–65,4 | PA1: *nặng*→nạo vét trong hành lang đê hiện trạng | PHƯƠNG ÁN 1 · NẠO VÉT / TRONG HÀNH LANG ĐÊ HIỆN TRẠNG | **Thẻ tài liệu** mặt cắt PA1 61,4–64,3 s |
| 65,4–71,1 | PA2: kênh hoá sông Đáy, mặt nước 350–500 m | PHƯƠNG ÁN 2 / KÊNH HOÁ SÔNG ĐÁY → BỀ RỘNG MẶT NƯỚC / KHOẢNG 350–500 M | **Thẻ tài liệu** mặt cắt PA2 66,2–70 s |
| 71,1–77,6 | Bề rộng đáy 200–400 m, 2 tuyến đê mới dọc kênh dẫn | BỀ RỘNG ĐÁY / TỪ 200 ĐẾN 400 M → XÂY DỰNG HAI TUYẾN ĐÊ MỚI / DỌC THEO KÊNH DẪN | App quy hoạch (vùng chấm xanh, tim kênh, đê) |
| 77,6–83,8 | Một kịch bản: khoảng cách 2 tuyến đê lên tới 500 m | MẶT CẮT GIỮA HAI ĐÊ / TRONG SƠ ĐỒ NGHIÊN CỨU → KHOẢNG CÁCH / GẦN 500 M | Thẻ PA2 lần 2 (79,6–82,6 s); zoom vào 2 đê song song |
| 84,2–90,9 | Đây là phương án nghiên cứu, không phải toàn tuyến mở 500 m | MỌI NGƯỜI CẦN HIỂU RÕ / ĐÂY LÀ PHƯƠNG ÁN NGHIÊN CỨU → KHÔNG ĐỒNG NGHĨA TOÀN TUYẾN / ĐỀU MỞ RỘNG 500 M | **Thước đo 450.2743 m** giữa 2 đê (87–90 s) — minh hoạ "gần 500 m" rất đắt |
| 90,9–96,7 | *Ổng*→Tổng diện tích thu hồi khoảng 3.002 ha | THEO SỐ LIỆU / TRONG HỒ SƠ ĐỀ XUẤT → DIỆN TÍCH ĐẤT DỰ KIẾN THU HỒI / KHOẢNG 3.002 HA | **Thẻ bảng** "3.002 HA ĐẤT DỰ KIẾN THU HỒI" 94–96,8 s |
| 96,7–102,6 | 6.068 hộ ảnh hưởng *đất ả*→đất ở, dự kiến *di dài*→di dời | 6.068 HỘ ẢNH HƯỞNG ĐẤT Ở / DỰ KIẾN PHẢI DI DỜI → SỐ LIỆU DỰ KIẾN / THEO BÁO CÁO | Cùng ảnh bảng, tiêu đề đổi "6.068 HỘ DỰ KIẾN DI DỜI" 96,8–99,8 s |
| 102,6–105,9 | 6.724 hộ ảnh hưởng đất nông nghiệp | KHOẢNG 6.724 HỘ / ẢNH HƯỞNG ĐẤT NÔNG NGHIỆP | App quy hoạch |
| 105,9–112,2 | Sông Hồng → Đại lộ Thăng Long: 1.217 hộ | SÔNG HỒNG / ĐẾN ĐẠI LỘ THĂNG LONG → DỰ KIẾN ẢNH HƯỞNG ĐẤT Ở / 1.217 HỘ | Thẻ bảng cột 1 "1.217 HỘ · …" 109–112 s. **Không** vẽ đoạn trên bản đồ — template nên vẽ |
| 112,2–116,3 | Đại lộ Thăng Long → Mai Lĩnh: 1.074 hộ | ĐẠI LỘ THĂNG LONG / ĐẾN MAI LĨNH → DỰ KIẾN / 1.074 HỘ | Thẻ bảng cột 2 114–116,5 s |
| 116,9–122,8 | Mai Lĩnh → hết địa phận Hà Nội: 3.777 hộ | MAI LĨNH / ĐẾN HẾT ĐỊA PHẬN HÀ NỘI → DỰ KIẾN ẢNH HƯỞNG ĐẤT Ở / 3.777 HỘ | 5 nhát zoom 117,5–120,5 s vào bản đồ sử dụng đất màu; thẻ bảng cột 3 120–123 s |
| 123,3–134,1 | Nâng cấp đê, giao thông 2 bên, nước thải; môi trường, chống ngập *nụt*→lụt, cảnh quan | BÊN CẠNH CẢI TẠO / LÒNG SÔNG → NÂNG CẤP ĐÊ ĐIỀU / PHÁT TRIỂN GIAO THÔNG HAI BÊN → THU GOM NƯỚC THẢI / CẢI THIỆN MÔI TRƯỜNG · CHỐNG NGẬP → PHÁT TRIỂN KHÔNG GIAN / CẢNH QUAN VEN SÔNG | Hoà tan về Google Earth (125 s), bay dọc sông |
| 134,6–145,3 | Mong dòng sông rộng hơn, đê vững hơn, không còn *nỗi no*→nỗi lo ngập; không gia đình nào đơn độc | MONG MỘT DÒNG SÔNG RỘNG HƠN / NHỮNG TUYẾN ĐÊ VỮNG CHÃI HƠN → MỘT THỦ ĐÔ / VƠI NỖI LO NGẬP LỤT → MONG KHÔNG GIA ĐÌNH NÀO / PHẢI ĐƠN ĐỘC TRƯỚC ĐỔI THAY | **Dùng lại** đoạn quay 70–100 s |
| 146,9–155,6 | Mỗi con đường mới… cơ hội; sông hồi sinh… yên bình; không *máy ấm*→mái ấm nào bị *lạc*→lãng quên | MỖI CON ĐƯỜNG MỚI / MANG THEO NHỮNG CƠ HỘI MỚI → MỖI DÒNG SÔNG HỒI SINH / MANG LẠI SỰ YÊN BÌNH → TRÊN HÀNH TRÌNH ĐỔI THAY / MONG KHÔNG MÁI ẤM NÀO BỊ LÃNG QUÊN | Lặp lại cảnh thước đo 450 m (147–150 s) |
| 156,4–160,8 | Theo dõi kênh để cập nhật thông tin dự án sông Đáy mọi người nhé | (không thẻ ý) | CTA 156,7–159,4 s → bản đồ 2 s cuối |

Nhận xét từ bảng: thẻ ý **luôn bám nghĩa** và nhấn đúng con số; nhưng nền bản đồ chỉ "đúng vị trí" thật sự ở đoạn bản đồ tổng (44–56 s) và hành lang sông nói chung — khi lời nhắc 4 huyện (11–14 s) hay 3 đoạn tuyến có số hộ (106–123 s), hình không tô vùng/đoạn tương ứng. Đây là chỗ bản tự động phải làm tốt hơn mẫu.

---

## 5. Âm thanh

| Đo | Giá trị | Ghi chú |
|---|---|---|
| Integrated | −10,3 LUFS | quá to so với chuẩn −14 |
| True peak | +2,6 dBTP | **vỡ tiếng** (peak mẫu −0,45 dBFS, intersample vượt 0) |
| LRA | 2,2 LU | nén/limit rất mạnh |
| Nhạc nền | Không | phổ trong các khoảng nghỉ (vd 45,9–46,4 s) tối hoàn toàn, chỉ có ù ~60 Hz ở −85 dB |
| SFX | 1 tiếng "ding" ~0,5 s ở 43,8 s (vạch hài phẳng 400/800/1200 Hz…), có thể 1 tiếng nhỏ lúc vào CTA | không whoosh ở mọi chỗ đổi thẻ |
| Giọng | Nam, đọc liền, gần như không nghỉ (Whisper chỉ tìm được 10 khoảng ≥ 0,45 s) | cụm ý trung bình 5,7 s / 28 cụm |

Khuyến nghị cho template: giữ "chỉ giọng", chuẩn −14 LUFS / −1 dBTP (như 2 skill hiện có), SFX chỉ ở 2 chỗ: vào bản đồ tổng và vào CTA. *(Đổi 04/11/2026 sau bản 3: chime CTA chói ⇒ chỉ còn ding ở bản đồ tổng — SKILL.md C6.)*

---

## 6. Quy trình tự động "đưa audio vào là ra video" — đề xuất cho template NNS

```
audio.m4a (+ ảnh công văn, + bộ nhận diện kênh)
  │
  ├─ 1. Whisper large-v3 (có mốc từng chữ)  ──► 2. SỬA LỖI nhận dạng bằng LLM + từ điển địa danh
  │       (mẫu này sai 10 chỗ: Chương Mỹ, nạo vét, đất ở, di dời, ngập lụt, mái ấm, lãng quên, tổng…)
  │
  ├─ 3. TRÍCH THỰC THỂ: địa danh (sông/đường/huyện/xã/cầu/đập), con số (km, ha, hộ, m), tên dự án, nhân vật
  │
  ├─ 4. ĐỊNH VỊ: Photon/Nominatim (đã có trong ban_do.py) → toạ độ; Overpass → polyline sông/đường, polygon ranh huyện
  │       Sông Đáy = relation OSM; "Đập Đáy", "Ba Thá", "Mai Lĩnh", "Đại lộ Thăng Long" = node/way → cắt polyline thành đoạn
  │
  ├─ 5. KẾ HOẠCH CẢNH (ke_hoach.json như minh-tam-edit): mỗi cụm ý → {thẻ ý 2 dòng, kiểu cảnh, vùng/đoạn cần tô, thẻ tài liệu nếu lời khớp OCR ảnh}
  │       kiểu cảnh: bay-doc-tuyen | ban-do-tong-ve-doan | to-ranh-huyen | zoom-diem | the-tai-lieu | cta
  │
  ├─ 6. CỔNG DUYỆT (1 lần): bảng cảnh + toạ độ tìm được + ảnh ứng viên (nếu có) → người dùng sửa/duyệt
  │
  ├─ 7. DỰNG: kéo ô Esri World Imagery (z 10/16/18) theo tuyến → camera trượt dọc polyline (ease 2 đầu) → vẽ hành lang ±250 m (buffer) → vẽ đoạn vàng chạy dần
  │       + lớp chữ (thẻ ý, thẻ tài liệu, thẻ đầu đề, logo, nguồn) + CTA clip của kênh → ffmpeg 1 lần mã hoá
  │
  └─ 8. KIỂM: soát chính tả thẻ ý, số khớp lời, thẻ tài liệu không đè thẻ ý, loudness, tờ soát khung
```

Những gì **đã có sẵn** trong skill minh-tam-edit để tái dùng: Whisper + gom cụm, `ban_do.py` (Esri + OSRM + Photon, chữ nguồn), thẻ navy viền vàng, cổng duyệt, kiểm −14 LUFS, kiem.py.
Những gì **phải viết mới**: (a) lấy polyline sông/đường + ranh huyện từ Overpass; (b) camera trượt dọc polyline với zoom theo từng cảnh; (c) buffer hành lang ±N m; (d) bộ viết "thẻ ý 2 dòng" có luật (dòng 2 phải chứa số/từ khoá, ≤ 28 ký tự, giữ nguyên số trong lời); (e) OCR ảnh công văn → ghép số trong ảnh với số trong lời để đặt thẻ tài liệu đúng lúc, tự cắt vùng cột/bảng tương ứng; (f) bộ tài sản kênh (logo, màu, font, CTA clip).

Luật thời gian rút từ mẫu (để ghi vào ĐÃ CHỐT nếu chọn kiểu này):
- 1 thẻ ý / 2–5 s, hiện trước chữ đầu 0,3 s, hoà tan 0,12 s, ẩn trong 2 s đuôi và lúc CTA.
- Thẻ tài liệu 3 s, chỉ ở 1/3 trên, đúng lúc đọc tới con số/tên có trong ảnh; 1 ảnh có thể dùng nhiều lần với tiêu đề khác.
- Cứ nói tới tên đoạn/tuyến có điểm đầu-cuối → chuyển sang bản đồ tổng và vẽ đoạn vàng 2 s; nói tới huyện/xã → tô ranh + nhãn; nói "gần X m" → vẽ thước đo trên vệ tinh.
- Cảnh nền tối thiểu 3 s, không nhảy cảnh dồn (mẫu nhảy 5 nhát trong 3 s ở 117 s là chỗ xấu, không bắt chước).
- Mỗi đoạn quay nền chỉ dùng 1 lần (mẫu dùng lại 70–100 s ở 135–156 s vì thiếu cảnh — bản tự động không thiếu).

---

## 7. Trả lời câu "AI tự tải nhân vật, địa danh, khu vực chèn vào luôn được không?"

| Loại thực thể | Làm được không | Cách + điều kiện |
|---|---|---|
| Khu vực / huyện / xã / sông / đường / cầu / đập | **Tự động hoàn toàn, đúng toạ độ** | OSM (Nominatim/Photon + Overpass) → bản đồ Esri; đây là phần mạnh nhất, chính xác hơn quay màn hình tay |
| Ảnh thật của địa danh (chùa, cầu, khu đô thị) | **Bán tự động** | Wikimedia Commons API (giấy phép rõ) → tải 3–5 ứng viên → hiện ở cổng duyệt để người dùng chọn; Google Ảnh/Bing thì bản quyền không rõ, không nên tự chèn vào video thương mại |
| Ảnh công văn, bảng số, sơ đồ | **Tự động nếu người dùng đưa ảnh** | OCR → khớp số với lời → tự cắt vùng, đặt tiêu đề, ghi "Nguồn: …" |
| Nhân vật (lãnh đạo, chủ đầu tư, người dân) | **Không nên tự chèn** | Rủi ro: nhầm người (rất dễ với tên Việt), quyền hình ảnh, nội dung nhạy cảm về quy hoạch/thu hồi đất → chỉ chèn ảnh do người dùng cung cấp hoặc đã duyệt ở cổng duyệt; AI có thể gợi ý ứng viên từ Wikimedia nhưng phải có người xác nhận |
| Lớp quy hoạch màu (QHSDĐ) | **Khó** | Không có nguồn tile công khai ổn định; thay bằng lớp tự vẽ từ dữ liệu trong công văn (hành lang, tuyến đê, ranh thu hồi) |

Lưu ý nguồn ảnh nền: kéo ô ảnh Google (Maps/Earth) bằng script là vi phạm điều khoản; Esri World Imagery dùng được khi ghi nguồn (mẫu đã ghi "Ảnh: Esri World Imagery"), đúng như `ban_do.py` đang làm.

---

## 8. Bộ thông số kiểu (style tokens) để đưa lên NNS

```
khung: 1080x1920 @30fps, hướng Bắc cố định
mau: navy #0F2C52 | vang #FFD24D | trang #FFFFFF | xanh-lo song #4FC3F7 | nen toi: brightness -40%, saturation -30% (chi ban do tong)
font: Montserrat ExtraBold (the y, IN HOA 52px) | Montserrat SemiBold/Bold (thẻ đầu đề 30–34px) | serif Playfair (logo)
the_y: y_tam 1580, 2 dong (trang/vang), fade 0.12s, 2–5s/the, som 0.3s
the_tai_lieu: x 112–968, y 300–825, bo 19px, fade+truot 0.18s, 3s
the_dau_de: y 56–140, navy, dong vang + dong trang
ban_do_tong: song 4px xanh lo, doan vang 9px ve dan 2s, cham trang 2 dau, nhan IN HOA 20px, chu nguon 17px y 1830
hanh_lang: 2 vach vang 3px, offset ±250 m tim song (hoac ±N m theo loi)
camera: 40–60 px/s doc tuyen, ease 0.6s dau/cuoi, zoom gan z18 / vua z16 / tong z10
cat_canh: >= 3s/canh, hoa tan 0.2s; cat cung chi khi vao/ra ban do tong & CTA
am_thanh: chi giong, -14 LUFS, -1 dBTP, SFX 2 cho (vao ban do tong, vao CTA)
cta: clip kenh 2.7s cat cung, roi 2s ban do khong chu
```
