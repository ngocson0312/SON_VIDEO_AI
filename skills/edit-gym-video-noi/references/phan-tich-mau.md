# Phân tích video mẫu "Hết Hồn Real" (đo từng khung 12/11/2026)

`D:\____TTT_____\KH_Test\Hết_Hồn_Real\video_mau.mp4` — 45,33 s, 576×970 (≈ 9:16), 30 fps. Một người nói (sơ mi trắng)
giới thiệu cách tư vấn Vinhomes Saigon Park, 5 bối cảnh (sảnh sa bàn, hành lang vòm, vườn, phòng khách, phòng sách).
Mọi số dưới đây quy về khung 1080×1920 (nhân ~1,875 ngang / 1,98 dọc). Hằng số tương ứng: `scripts/chung.py`.

## 1. Bố cục mỗi câu (ngữ pháp)

| Thành phần | Mẫu | Hằng số |
|---|---|---|
| Tiêu đề 3 tầng | mỗi câu (vế đầu) 1 tiêu đề: **dẫn** trắng mảnh trên-trái · **KHOÁ** to giữa · **viết tay** trắng dưới-phải. Đứng suốt câu, nằm SAU đầu người (đầu che phần dưới khoá: "Thông Tin" 11,3 s, "QUAN TRỌNG" 32,7 s) | `TIEU_DE` |
| Sub ngực | phần lời còn lại, cụm 1–4 chữ ở ngực (0,50–0,67 H), trắng đậm viền tối | `SUB` |
| Đồ hoạ theo nghĩa | lời nhắc "bảng giá" → ảnh bảng giá bật ra từ tay; "mặt bằng" → 3 thẻ xếp nghiêng; "vị trí" / "tiện ích" → icon 3D; "tự tìm hiểu" → ô Google gõ tên dự án; giá "5 tỷ / 8 tỷ" → số vàng to; tên dự án → logo rơi sau người; "Là …, là …, hay …" → liệt kê | `THE_ANH`, `ICON`, `TIM_KIEM`, `SO_TIEN`, `LOGO`, `LIET_KE` |

Lời mẫu (Whisper, mốc giây): Khi bạn tìm mua một căn nhà (0,0) · bất kỳ sale nào cũng có thể gửi cho bạn một bảng giá (1,36)
· hoặc có thể cho bạn xem mặt bằng, phân tích vị trí, giới thiệu tiện ích (3,68) · rồi nói với bạn rằng căn này đẹp, căn
kia tiềm năng (7,14) · Những thông tin đấy bạn hoàn toàn có thể tự tìm hiểu (10,18) · Cùng một dự án, cùng một diện tích
50m², có căn hơn 5 tỷ, có căn lại gần 8 tỷ (12,86) · Vậy điều gì khiến bạn bỏ ra thêm 1 tỷ hay thậm chí là 2 tỷ… (18,0) ·
Là vị trí, là khả năng khai thác hay đơn giản là căn có mức giá cao hơn? (23,02) · Và quan trọng hơn, phần tiền chênh
lệch ấy… (27,46) · Đó là lý do khi tư vấn Vinhomes Saigon Park… (33,06) · Bởi với một tài sản lớn, người tư vấn phải… (38,12).
Kế hoạch dựng lại đủ: `examples/plan_mau.json`.

## 2. Tiêu đề

| Tiêu đề (giây) | Phông khoá | Màu | Vào → ra |
|---|---|---|---|
| Khi bạn / TÌM MUA / 1 căn nhà (0,2) | nén cao kiểu Anton, HOA | trắng → cam đào (gradient dọc) | dẫn + viết tay hiện mờ trước (0,23 s), khoá **rơi từ mép trên** to dần rồi về cỡ (0,30–0,53 s, ~10 khung) → chui vào sau đầu |
| Họ có thể / CHO BẠN / Xem (3,65) | rộng đậm kiểu Montserrat Black, HOA | oải hương → tím + khối 3D tím đậm | lớn dần từ nhỏ ở trên đầu |
| Những / Thông Tin / Ấy (10,6) | tròn đậm kiểu Baloo, chữ thường hoa đầu | kem → caramel + khối nâu | lớn dần từ nhỏ (10,63–11,0 s) → trôi xuống + mờ ở 12,9 s |
| Vậy điều gì / Khiến bạn (18,0) | Baloo | caramel | trượt từ trái, **loé trắng** rồi về màu |
| Và / QUAN TRỌNG / Hơn (27,5) | Montserrat Black | tím | **mọc ra từ sau đầu** |
| Đó là / Lý do / Khi tư vấn (33,4) | nghiêng đậm | kem → cam vàng | ở GIỮA khung (vì logo chiếm đỉnh) |
| Bởi với 1 / TÀI SẢN LỚN (38,2) | Anton | vàng chanh đặc + icon nét vàng chìa khoá-nhà; dẫn viết bút lông | **vỡ từng chữ rơi** ở cuối (44,6–45,0 s) |

- Cỡ khoá ~0,75–0,82 W; dẫn ~66 px; viết tay ~90 px. Dẫn đè ~22 % đỉnh khoá, viết tay đè ~42 % đáy khoá.
- Cả khối "thở" (phóng chậm ~3 %) suốt lúc hiện. Ra: thu nhỏ về sau đầu (~7 khung) / trôi xuống mờ / vỡ chữ.
- Màu khoá luân phiên, 2 tiêu đề liền nhau không trùng.

## 3. Sub

- Montserrat Bold trắng, viền tối mảnh + bóng mềm; 1–4 chữ / cụm; tâm ngang theo người, dọc ở ngực.
- Đổi cụm = **đẩy ngang** (~4 khung, cụm mới vào từ 1 bên, cụm cũ ra bên kia, nhoè chuyển động, hướng thay đổi);
  cụm đầu sau quãng lặng = nhoè vào.
- "Sale" (1,76 s) chữ TO bật (~2×) + "Nào" nghiêng nhỏ dưới. 2 dòng: dòng 1 đậm, dòng 2 nghiêng nhạt ("Cùng một / Dự án");
  dòng 1 giữ nguyên khi dòng 2 đổi ("Cùng một / Diện tích 50m²").
- Nhấn: hồng-đỏ đậm nghiêng "50m²", "1 tỷ", "2 tỷ"; ngoặc kép HOA "VỊ TRÍ"; vàng gradient nghiêng "Người tư vấn"; to "Cho điều gì?".
- Vòng vẽ tay cam-vàng có mũi tên quanh "Chênh lệch ấy" (29,3 s).

## 4. Đồ hoạ phụ

- **Thẻ ảnh bật ra từ tay**: bảng giá (3,1 s) ở đáy; mặt bằng 3 thẻ xếp chồng nghiêng 3D từ dưới-trái (4,7 s);
  ảnh nhà phố nhỏ NGANG (~0,45 W) bay từ bàn tay giơ lên ra 2 góc trên (8,6–10,0 s), sát mép trên. Ra = thu về.
- **Icon 3D bóng** + nhãn viên thuốc: ghim tím "Vị trí" bên trái (5,8 s), mũ tốt nghiệp xanh lá "Tiện ích" bên phải (6,7 s);
  trượt vào, nhún, thu nhỏ khi ra.
- **Ô tìm kiếm** kiểu Google (11,45–13,0 s): trượt từ trái phóng to rồi về cỡ ~0,83 W, ngay dưới sub; gõ "Vinhome Saigon Park"
  ~1 ký tự / khung với con trỏ "_"; ra = mờ + nhoè.
- **Số tiền** (15,5–17,9 s): "Có căn" (sub) + "5.000.000.000" vàng nén to, **vệt ≫ vàng** chạy trước rồi số trượt từ trái
  nhoè ngang; dưới-phải "Hơn" nghiêng + icon túi tiền; đổi "8.000.000.000 / Gần" cùng kiểu.
- **Logo** Vinhomes Saigon Park xanh rơi từ trên xuống SAU người khi đọc tên dự án (34,6–35,1 s).
- **Liệt kê** (23,5–27 s): "Là" tím 3D to (~0,26 W, cao ~0,10 H) ở trái ngang ngực; các dòng trắng trượt từ phải vào bên phải nó, chồng xuống.

## 5. Khung, màu, chuyển cảnh

- Cắt nhảy (jump cut) có đổi zoom tức thì (0,9 s, 7,45 s, 15,45 s…). Màu ấm, rực; đáy tối dần (vignette dưới), đỉnh tối nhẹ.
- Chuyển cảnh CHỈ ở chỗ đổi bối cảnh: zoom-nhoè toả tròn (10,1 s; 27,47 s) · tia sáng dọc quét + loé (23,5 s) ·
  cháy phim cam → trắng → đỏ (33,3 s) · tách màu RGB + nhoè + rung (38,2 s). Mỗi cái ~7–9 khung quanh cú cắt.

## 6. Tiếng

- Nhạc beat lo-fi / hip-hop ~93 BPM suốt video; RMS khe ≈ −21…−22 dBFS so với giọng ≈ −12,6 ⇒ nhạc dưới giọng ~9 dB, nén nhẹ.
- ~21 SFX (đỉnh cao tần ở 0,95 · 3,33 · 4,54 · 6,14 · 6,94 · 10,12 · 10,98 · 13,27 · 14,65 · 16,19 · 17,33 · 19,58 · 22,62 ·
  27,29 · 29,38 · 33,25 · 36,68 · 37,62 · 39,24 · 40,80 · 43,32 s): whoosh ở chuyển cảnh / tiêu đề, lấp lánh khi chữ đáp,
  pop ở thẻ / icon, riser trước chuyển cảnh lớn, swish. Mật độ ~1 tiếng / 2 s.
- Master −14 LUFS.

## 7. Chỗ skill cố ý khác mẫu

- Không có nhạc đi kèm (không tự tổng hợp) — người dùng đưa file beat; không có thì hỏi ở cổng duyệt.
- Icon / thẻ / logo vẽ bằng code hoặc lấy từ Resources của người dùng (không chép ảnh mẫu).
- Đáy khoá đặt theo đỉnh đầu THẬT (mặt nạ người) lúc đầu cao nhất trong câu, để zoom nhảy giữa câu không làm đầu che hết chữ.
