# SPEC v1 — skill "bản đồ BĐS từ audio" (tên tạm: `ban-do-bds`)

Bản này ghi các quyết định đã chốt ngày 04/11/2026 sau khi phân tích `ho_dan.mp4` (xem `PHAN_TICH_ho_dan.md`). Khi dựng skill, mục ĐÃ CHỐT này chép sang SKILL.md.

## 1. ĐÃ CHỐT (04/11/2026)

| # | Quyết định | Ghi chú |
|---|---|---|
| C1 | **Nền hình = bản đồ vệ tinh dựng bằng code**, không quay màn hình | Esri World Imagery (ghi nguồn) + tim sông/đường/ranh từ OpenStreetMap; camera trượt dọc tuyến; không kéo ô Google |
| C2 | **Sub nguyên văn, kiểu karaoke** | KHÔNG dùng "thẻ ý" tóm tắt như video mẫu. Cả cụm hiện, chữ đang đọc sáng vàng. Kiểu chữ cụ thể: xem mục 4 (cần chốt 1 lần ở lần dựng đầu) |
| C3 | **Mọi thứ bám audio**. Audio do bên mình/người dùng đưa vào, luôn có | Lời không nhắc → không đồ hoạ. Lời nhắc địa danh → bản đồ. Lời nhắc văn bản/số liệu → quy trình tài liệu (C4) |
| C4 | **Thẻ tài liệu: resources trước, không có thì tự tìm trên web, phải xác minh 100 %, không xác minh được thì KHÔNG đưa gì lên** | Không được bịa, không được dùng ảnh "gần giống". Chi tiết mục 3 |
| C5 | Ảnh nhân vật: chỉ dùng khi người dùng đưa vào resources hoặc duyệt ở cổng duyệt | AI không tự chèn mặt người |
| C6 | Âm thanh: chỉ giọng, −14 LUFS, −1 dBTP; SFX tối đa 2 chỗ (vào bản đồ tổng, vào CTA) — **đổi 04/11/2026: chỉ 1 chỗ (bản đồ tổng), CTA không SFX; xem SKILL.md C6** | Như 2 skill hiện có |
| C7 | 1 cổng duyệt duy nhất trước khi dựng | Bảng cảnh + toạ độ + ứng viên tài liệu (kèm nguồn, bằng chứng khớp) |

## 2. Đầu vào / đầu ra

Đầu vào:
- `audio.m4a|mp3|wav` (bắt buộc)
- `resources\` (tuỳ chọn): ảnh/PDF công văn, bảng, sơ đồ; ảnh nhân vật; logo kênh, clip CTA
- `kenh.json` (1 lần cho mỗi kênh): tên kênh, logo, màu, font, CTA

Đầu ra: `*_ban1.mp4` 1080×1920 30 fps, `ke_hoach.json`, `soat.jpg`, `bao_cao.md` (liệt kê rõ: tài liệu nào tìm được/không tìm được, nguồn nào, vì sao bỏ).

## 3. Quy trình tài liệu (C4) — "tìm → xác minh → mới được dùng"

Kích hoạt khi lời đọc có từ khoá: hồ sơ, báo cáo, tờ trình, quyết định, công văn, văn bản, nghị quyết, thông báo, quy hoạch, số liệu, theo … (kèm số đi sau: km, ha, hộ, m, tỷ, %).

```
B1  Trích "mệnh đề số liệu" từ lời: {con số, đơn vị, thực thể, câu gốc, giây}
B2  resources\ có?  → OCR (ảnh/PDF) → chuẩn hoá số (6.068 = 6068 = 6,068) → tìm mệnh đề trong OCR
      khớp ≥ 1 số + đúng thực thể  → dùng ảnh đó, cắt vùng chứa số (bbox OCR), tiêu đề = số đang đọc
      không khớp                   → B3
B3  Tìm web (chỉ khi B2 trống/không khớp): truy vấn = thực thể + 2–3 con số nguyên văn
      - vòng 1 tìm thường; không thấy → vòng 2 tìm mở rộng
      - lọc tên miền: ưu tiên .gov.vn, chinhphu.vn, báo lớn (vnexpress, tuoitre, dantri, thanhnien, cafef, baoxaydung, kinhtedothi, hanoimoi…)
B4  Tải trang bằng trình duyệt thật (Playwright) — KHÔNG tin HTML curl (thử 04/11: CafeF/CafeBiz trả về bài khác cho cùng URL)
      Xác minh: văn bản trang phải chứa ĐÚNG ≥ 2 con số của mệnh đề + tên thực thể; tiêu đề trang khớp tiêu đề kết quả tìm
      Không đạt → thử URL khác (tối đa 5) → vẫn không → KHÔNG THẺ, ghi vào bao_cao.md
B5  Lấy ảnh: (a) ảnh/bảng trong bài có OCR chứa số → dùng; (b) không có ảnh → chụp đoạn văn chứa số (clip vùng) làm thẻ "trích dẫn", ghi rõ nguồn
B6  Thẻ in dòng nguồn bắt buộc: "Nguồn: <tên báo/cơ quan> · <ngày>"; cổng duyệt hiện ảnh + URL + câu chứa số để người dùng xác nhận
```

Luật cứng:
- Không khớp số → không thẻ. Không thay bằng ảnh minh hoạ chung chung, không dùng ảnh từ bài khác cùng chủ đề.
- Số trong thẻ phải trùng số trong lời; lời "hơn 6.000 hộ" + tài liệu "6.068 hộ" được coi là khớp (làm tròn lên/xuống trong 5 %); lệch hơn → không thẻ, báo lại.
- Kết quả thử trên video mẫu (04/11/2026): tìm thường chỉ ra 110 km / 3 đoạn / 54 km; tìm mở rộng ra đúng bài 21/9/2026 (Nhịp sống thị trường → CafeF/CafeBiz) có 6.068 hộ, 24.272 người, 6.724 hộ, 3 dự án thành phần, tờ trình 25/8/2026 — tức là **tìm được**. Nhưng tải trang bằng curl **và cả bằng trình duyệt thật** đều ra bài khác ("Giữ nguyên quy định công chứng…", cùng ngày 21/9, còn giữ từ khoá "mik group · giải phóng mặt bằng" và ảnh "Sông Đáy qua địa phận Quốc Oai") ⇒ bài gốc đã bị gỡ/thay nội dung. Theo luật C4: **không có thẻ** cho các số đó, chỉ ghi vào bao_cao.md "tìm thấy dấu vết nguồn ngày 21/9/2026 nhưng trang hiện không còn số liệu". Bài học: snippet máy tìm kiếm không phải bằng chứng; phải xác minh trên trang tại thời điểm dựng. Các số 24.440 ha, 3.002 ha, 23 xã 2 phường, 350–500 m chưa thấy trên web ⇒ nếu không có trong resources thì **không có thẻ** cho các câu đó.

## 4. Sub karaoke (C2) — đề xuất, chốt ở lần dựng đầu

- Nguyên văn sau khi sửa lỗi Whisper (có bước LLM + từ điển địa danh; giữ nguyên con số).
- Gom cụm ≤ 2 dòng, ≤ 32 ký tự/dòng, ngắt theo nghĩa (bộ nns-auto-sub hiện có).
- Vị trí tâm y 1545 (như minh-tam-edit), canh giữa.
- Kiểu đề xuất cho dạng bản đồ/tin tức: Montserrat ExtraBold, chữ thường có dấu (không IN HOA để dễ đọc câu dài), cả cụm trắng viền tối mềm, chữ đang đọc vàng `#FFD24D` + phồng nhẹ 1,06; không Pacifico (viết tay hợp video nhà, không hợp tin quy hoạch).
- Ẩn khi thẻ tài liệu che tới vùng sub (không xảy ra vì thẻ ở 1/3 trên), ẩn 0,9 s cuối và lúc CTA.

## 5. Cảnh bản đồ (C1) — luật chọn cảnh theo lời

| Lời nhắc | Cảnh | Dữ liệu |
|---|---|---|
| Tên sông/đường/kênh | Bay dọc tuyến, z 16–18, hành lang ±N m nếu lời có "rộng N m" | Overpass way/relation |
| "Từ A đến B … km" | Bản đồ tổng (Esri tối), vẽ đoạn vàng A→B chạy 2 s, thẻ đầu đề "A → B · N KM" | Photon A, B + cắt polyline |
| Tên huyện/xã/phường | Tô ranh + nhãn, zoom vừa | Overpass admin boundary |
| Cầu/đập/công trình | Zoom điểm z 18, ghim + nhãn | Photon/Overpass node |
| "gần/khoảng N m" | Thước đo trên vệ tinh giữa 2 điểm | buffer/offset |
| Số liệu/hồ sơ | Thẻ tài liệu (mục 3), nền giữ cảnh đang bay | |
| Câu cảm xúc/kết | Bay chậm cảnh rộng, không đồ hoạ | |

Luật chung: mỗi cảnh ≥ 3 s, hoà tan 0,2 s, không nhảy cảnh dồn; không dùng lại 1 đoạn bay 2 lần; toạ độ sai (Photon không ra hoặc ra ngoài tỉnh) → hỏi ở cổng duyệt, không đoán.

## 6. Thông số kiểu kế thừa từ mẫu (đã đo, xem PHAN_TICH mục 8)

navy `#0F2C52`, vàng `#FFD24D`, sông xanh lơ `#4FC3F7`; thẻ tài liệu x 112–968 / y 300–825; thẻ đầu đề y 56–140; chữ nguồn y 1830; logo góc phải trên; CTA clip kênh 2,7 s + 2 s bản đồ không chữ.

## 7. Chưa chốt — hỏi 1 lần ở lần dựng đầu

1. Kiểu chữ sub karaoke (mục 4) — đồng ý Montserrat chữ thường, hay muốn IN HOA?
2. Có thẻ hook navy đầu video (tự sinh từ câu đầu) không?
3. Logo + CTA của kênh (file).
4. Vòng tìm web có được dùng báo điện tử, hay chỉ nguồn .gov.vn?
