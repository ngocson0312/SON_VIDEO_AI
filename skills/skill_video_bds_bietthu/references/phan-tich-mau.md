# Phân tích video mẫu BĐS "Biệt thự rừng tầng hầm" (BDS_1/MAU.mp4)

Đo ngày 04/11/2026 trên `Downloads/ToDay/BDS_1/MAU.mp4`. Mọi số dưới đây là **số đo** (ffprobe / ffmpeg /
OpenCV / faster-whisper large-v3), không phải ước đoán. Đồ đo nằm ở `OUT/bietthu_mau/`.

## 0. Video mẫu là gì

- 576×1024, 30 fps, 91,73 s; AAC 44,1 kHz stereo **32 kb/s** (tiếng nén rất nặng, xem §6).
- Đây là video **khoe so sánh**: nền là bản EDITED phóng to + nhoè, thẻ **RAW** nhỏ ở mép trái
  (x 0–128, y ~600–843), thẻ **EDITED** to bên phải. Phần cần học là thẻ EDITED.
- Thẻ EDITED đo bằng gradient trung bình theo thời gian: **x 128–532, y 127–842** (404×715 px ≈ 9:16)
  ⇒ bản gốc là video dọc 1080×1920 thu nhỏ ×0,374. Mọi cỡ chữ dưới đây đã quy đổi về **khung 1080×1920**
  (hệ số 1080/404 = 2,673).
- Thẻ RAW cho biết **nguồn thô**: 0–15 s là người nói (Nghĩa, áo vest xám) quay một mạch ở 2 chỗ;
  16–41 s máy chĩa xuống nền sỏi (người vẫn nói) ⇒ **phần lớn hình thô bỏ đi, chỉ giữ TIẾNG**;
  từ 42 s thẻ RAW xám (hết nguồn). Toàn bộ hình còn lại là **tư liệu dự án** (render ngoại thất,
  flycam, quay nhà mẫu, ảnh phối cảnh).

⇒ Công thức của kiểu edit này: **lấy giọng nói của sale làm xương sống, phủ hình dự án lên ~70 % thời
lượng, mỗi ý một cảnh, mỗi cảnh một cụm chữ "bảng giá/ thông số" đẹp**.

## 1. Cấu trúc kể chuyện (lời → cảnh)

Lời (Whisper, đã sửa tên riêng): 18 câu, 91,3 s, nói liền (khe giữa câu chỉ 0,1–0,15 s ⇒ đã cắt lặng).

| Đoạn | Thời gian | Lời | Hình |
|---|---|---|---|
| HOOK câu hỏi | 0–4,1 | "Đã bao giờ bạn thấy một căn biệt thự mà tầng hầm mới là nơi đáng sống nhất chưa?" | người nói, chữ to trên đầu |
| HOOK giữ chân | 4,2–9,7 | "Đừng bỏ qua video này vì Nghĩa sắp hé lộ một siêu phẩm biệt thự rừng tại dự án Eco Retreat nhé" | người nói, từng chữ to thay nhau, tiêu đề dự án |
| Tổng quan | 9,7–16,2 | phân khu, quy mô 56 ha, 604 căn | người nói (cảnh 2) → thẻ ảnh flycam trên nền nhoè |
| Sản phẩm | 16,2–22,4 | 3 dòng sản phẩm (liệt kê tên) | người đi dạo + màn hình kính 3D → ghép 3 thẻ ảnh trên nền xanh ngọc |
| Điểm khác biệt | 22,4–37,2 | tầng hầm trải nghiệm: mở, đón nắng, hầm rượu, phòng chiếu phim, khu làm việc | 7 cảnh nội thất/ngoại thất, mỗi phòng một cảnh |
| Tiện ích/ cảnh quan | 37,2–51,7 | 12 ha mặt nước, 13,5 ha rừng, tắm rừng, suối hoa | thẻ ảnh flycam (số ha) → flythrough rừng → flycam hồ → flycam biệt thự |
| Giá & chính sách | 51,7–86,1 | giá 17 tỷ, 99 tr/m², 4,5 tỷ = 25 %, miễn lãi, ân hạn 24 tháng, chiết khấu 10 %, 0,5 %, quà 300 tr | 11 cảnh nội thất, MỖI CON SỐ một cảnh, số to giữa khung |
| CTA | 86,1–91,3 | "Inbox ngay cho Nghĩa để nhận layout chi tiết…" | người nói trước biệt thự + tên người nói to |

## 2. Cảnh & nhịp cắt

- **29 cảnh / 91,7 s**: trung bình **3,16 s**, trung vị ~2,4 s; ngắn nhất 0,90 s (phòng chiếu phim), dài nhất
  9,9 s (hook người nói — trong đó có chuyển cảnh nội bộ bằng hiệu ứng).
- Người nói lộ mặt ~**30 %** thời lượng (hook 0–13,2 s, 1 cảnh đi dạo 16,4–19, 1 cảnh đi trong nhà tắm
  51,9–58,4, CTA 86,3–hết). **~70 % là hình dự án.**
- **Gần như 100 % cắt cứng** (sai khác khung 47–96 / 255 trong 1 khung). Không có crossfade giữa cảnh.
- **Điểm cắt bám lời**: 16 cú cắt đầu câu rơi **+0,07…+0,41 s sau chữ đầu câu** (trung vị ~+0,25 s);
  các cú cắt giữa câu rơi đúng chữ khoá ("Villa", "phòng", "khu", "13", "chỉ cần", "EcoPark"…).
  ⇒ quy tắc: **mỗi cụm ý = 1 cảnh, cắt ~0,25 s sau chữ mở cụm** (không cắt theo nhịp nhạc).
- Chuyển động máy trong cảnh (ORB, ước lượng tích luỹ): đa số cảnh hình dự án là **video có chuyển động
  thật** (parallax rõ) với tốc độ đẩy vào **+0,3…+6 %/s** và lia ngang chậm; 1 cảnh flythrough rừng
  (42–46,5 s) bay tới liên tục. Với ẢNH TĨNH thì tương đương Ken Burns đẩy vào 1,5–4 %/s + lia nhẹ.

### Bố cục cảnh đặc biệt

1. **Thẻ ảnh trên nền nhoè** (13,2 / 37,4 / 39,8 s — ảnh flycam NGANG): ảnh ngang đặt thành thẻ bo góc
   rộng ~96 % khung, bán kính ~50 px (1080), có bóng mềm, tâm ở ~y 60 % khung; nền = chính ảnh đó phóng
   to phủ kín + nhoè mạnh + tối nhẹ; con số to nằm phía TRÊN thẻ.
2. **Ghép 3 thẻ** (19,0–22,7 s, liệt kê 3 dòng sản phẩm): nền xanh ngọc (#2BA898) + đàn bướm xanh bay
   qua; 3 thẻ ảnh ngang xếp dọc, **trượt vào từ trái lần lượt cách nhau ~0,2 s**; mỗi thẻ có nhãn IN HOA
   trắng nhỏ góc dưới-trái ("VILLA ĐẠI LỘ"…); ảnh trong thẻ **đổi (hoà tan 0,3 s) đúng lúc đọc tên**.
3. **Người + màn hình kính 3D** (16,4–19,0 s): người hiện dần từ trong suốt (hiệu ứng "tàng hình") rồi
   một tấm kính bo góc viền xanh ngọc phát sáng hiện cạnh người, **xoay 3D quanh trục đứng**, bên trong
   chiếu ảnh dự án đổi liên tục. (Cần clean plate để làm phần "tàng hình" — skill chỉ tái tạo tấm kính 3D.)

## 3. Hiệu ứng & chuyển cảnh (đo từng khung)

| Thời điểm | Hiệu ứng | Thông số đo |
|---|---|---|
| 0,00–0,20 | **Phóng-lùi mở đầu** | khung đầu phóng ~1,35× rồi lùi về 1,0 trong 6 khung (ease-out) |
| 1,47–1,63 | **Chữ khoá nhấp nháy** "CĂN BIỆT THỰ" | bật/tắt xen kẽ mỗi khung, 6 khung rồi đứng |
| 1,87–2,20 | **Loé sáng + rung** | độ sáng khung 86→133→78 (đỉnh +55 %), chữ giật xuống ~10 px, 10 khung |
| 4,43–4,60 | **Zoom-nhoè** chuyển ý (vào "Đừng bỏ qua") | nhoè chuyển động dọc rất mạnh 5 khung + whoosh (HF +38 dB, phân vị 98) |
| 9,67–9,87 | **Nhân bản loé** trước khi cắt | bóng người tách nền nhấp nháy trắng ↔ âm bản xám, 6 khung, rồi cắt cứng |
| 16,4–17,0 | Người hiện dần từ trong suốt + tấm kính 3D xuất hiện | ~0,6 s |
| 19,0 | Cắt sang nền xanh ngọc, bướm bay, thẻ trượt vào | thẻ trượt ~6 khung/thẻ |
| 22,7–25,6 | **Loé ánh sáng cam** (light leak) phủ góc dưới-trái, trôi sang phải | suốt cảnh, hoà kiểu screen |
| 46,4–46,5 | Lớp đỏ cam phủ cả khung ngay trước cắt | 3–4 khung |
| 51,8–52,3 | **Loé cam/đỏ qua cú cắt** | trước cắt 3 khung + sau cắt 8 khung |
| 86,1–86,3 | **Loé cam/đỏ qua cú cắt** vào CTA | trước 4 khung + sau 2 khung |

- Không dùng vignette, không viền khung, không chữ đè lên mặt người.
- Màu: hình dự án sáng, ấm, bão hoà nhẹ; người nói để tự nhiên.

## 4. Chữ (phần quan trọng nhất của phong cách)

### 4.1 Cấu trúc "cụm chữ" (text stack)
Gần như mọi cảnh có **1 cụm chữ 2–4 dòng xếp chồng, dòng sát nhau (gần như dính)**, gồm các VAI:

| Vai | Kiểu chữ (gần nhất có sẵn) | Cỡ đo (cao chữ hoa, khung 1080) | Màu |
|---|---|---|---|
| **dẫn** (kicker) — "Chỉ vốn vẹn", "Tương đương", "Khách hàng" | sans mảnh vừa (Be Vietnam Pro Medium) | ~30–40 px | trắng |
| **KHOÁ số** — "604", "24", "13 ha", "10%", "Miễn Lãi" | sans hình học đậm vừa (Montserrat SemiBold) | 140–250 px | vàng chanh **#FCE773** (mặc định) |
| **KHOÁ chữ** — "BIỆT THỰ", "TẦNG HẦM", "ECO PARK", "17 Tỉ" | sans đứng hẹp rất đậm (Barlow Condensed Black), có gradient + vân | 130–200 px | màu ăn theo cảnh (xem 4.3) |
| **viết tay** — "căn biệt thự", "tắm rừng", "Rừng", "xa xỉ nhất" | thư pháp nghiêng (Great Vibes) | 60–110 px | trắng |
| **chú thích** dưới số — "diện tích rừng", "thanh toán sớm" | sans vừa | ~40–60 px | trắng |
| **sub nhỏ** — "là quý khách hàng", "dòng suối đầy hoa" | sans nhỏ | ~25–32 px | trắng, bóng mờ |

Các khuôn cụm hay gặp:
- **P1 dẫn + KHOÁ + viết tay**: dẫn nằm sát trên-trái KHOÁ, viết tay CHỒNG lên ~30 % đáy-phải KHOÁ
  ("Chỉ vốn vẹn / 604 / căn biệt thự", "ECO RETREAT / BIỆT THỰ / Rừng", "với Hệ sinh thái / 24 / túi rừng").
- **P2 KHOÁ + chú thích**: chú thích canh phải dưới số ("12 ha / diện tích mặt nước", "25% / vốn tự có ban đầu").
- **P3 viết tay làm KHOÁ**: "Liệu pháp / tắm rừng", "Khu làm việc / vô cực / giữa lòng thiên nhiên".
- **P4 hook**: câu hỏi trắng to ~90 px; rồi **từng chữ to thay nhau** ("Đừng" → "Bỏ" → "Qua" → "Video này"),
  chữ bạc gradient hơi trong (~85 %).

### 4.2 Chuyển động chữ (đo từng khung)
- **Vào = gõ chữ** (typewriter) cực nhanh: **1–1,5 ký tự/khung (30–45 ký tự/s)**, từ trái sang phải,
  kèm trôi ngang nhẹ. Mỗi dòng gõ **đúng lúc chữ đó được nói** (lệch −0,25…+0,4 s); KHOÁ có thể hiện
  trước dòng dẫn nếu lời nói theo thứ tự đó (vd "TẦNG HẦM" 2,53 s rồi "mới là nơi" 3,03 s).
- **KHOÁ vào** theo 3 kiểu: **nhấp nháy** (bật/tắt mỗi khung, 6 khung — "CĂN BIỆT THỰ", "ECO PARK");
  **rơi từ trên xuống** 4–5 khung có vệt dọc ("17 Tỉ", "25%"); **gõ** ("12 ha", "13 ha").
- **Ra = xoá ngược** (backspace) 4–5 khung từ cuối dòng về đầu + trôi sang phải ~10–15 px
  ("604" → "60" → hết; "Hầm rượu" → "Hầm" → hết). Chữ tắt **ngay trước cú cắt** (≤ 0,1 s) — cụm chữ
  có thể **vắt qua cú cắt** nếu câu chưa xong ("Khách hàng 10%" giữ nguyên qua 75,1 s).
- Cụm chữ luôn có **trôi chậm** (vài px/s) để không đứng chết.

### 4.3 Màu KHOÁ "ăn theo cảnh"
Lấy mẫu trên khung gốc:
vàng chanh #FCE773 (604, 24, Hầm rượu, 10 %) · xanh ngọc #1AD1C3→#32ECEA (TẦNG HẦM, BIỆT THỰ, 17 Tỉ) ·
tím hồng #E417F6 (CĂN BIỆT THỰ) · hồng đỏ #F21552 (Phân khu tâm điểm) · navy #173C6B (25 % trên tường be)
· xanh bạc hà #AEE5C9 (ECO PARK trên tường xanh rêu) · cam đào #F2A287 (99 Triệu/m² trong phòng tắm gỗ)
· xanh rừng #195236 (300 Triệu trong phòng sofa xanh) · vàng nhạt #F1DC92 (Miễn Lãi).
⇒ Quy tắc: số tiền/% mặc định **vàng chanh**; khi cảnh có một màu nhấn rõ (rèm, sofa, tường), KHOÁ lấy
**màu nhấn của chính cảnh** (đậm hơn hoặc nhạt hơn nền để đủ tương phản). Cảnh người nói ngoài trời
(nền cây xanh) dùng xanh ngọc / tím hồng / hồng đỏ cho nổi.

### 4.4 Vị trí
- Cụm chữ đặt vào **khoảng trống của hình**: mặc định **dải trên y 230–700** (trên đầu người nói / trần nhà);
  khi phần trên bận (cây, đèn) thì xuống giữa (y ~1000–1300) như "24 túi rừng", "10%".
- Không bao giờ đè mặt người nói. Không có chữ ở đáy khung (dưới y ~1500) trừ sub nhỏ.
- Sub nhỏ (khi cảnh không có cụm chữ) nằm giữa khung, chỉ 2–4 chữ đang nói.
- CTA cuối: "Inbox ngay nhận layout chi tiết" nhỏ / **tên người nói** trắng đậm ~110 px / viết tay
  "Biệt thự tầng hầm" / "đẹp nhất dự án" nhỏ.

### 4.5 Chữ sửa theo nghĩa, không chép Whisper
Chữ trên màn hình đúng chính tả & tên riêng dù lời nghe ra sai: "xe rinh gia cư" → **Shinrin-Yoku**,
"EcoBuck" → **ECO PARK**, "triết khấu" → **chiết khấu**, "lơi" → **nơi**, "sinh tái" → **sinh thái**.
⇒ Skill cần bước Claude sửa chữ theo nghĩa + cổng duyệt nội dung.

## 5. Âm thanh

- Độ to tổng **−8,8 LUFS, LRA 1,0 LU, true peak +0,5 dBTP** ⇒ nén/limiter rất gắt (quá to, có clip).
  Skill KHÔNG chép con số này — master về −14 LUFS / TP −1,5 (chuẩn đăng TikTok/FB của dự án).
- **Nhạc nền chạy liên tục** suốt video: sàn âm 50 ms không bao giờ xuống dưới −30 dBFS (p1 = −28,5)
  trong khi giọng ~−11 dBFS ⇒ nhạc thấp hơn giọng ~**14–18 dB**; nhịp đo bằng tự tương quan dải trống
  ~**136 BPM** (68 nửa nhịp) — nhạc sôi động nhẹ, đoạn giá cả (64 s+) trống dày hơn.
- **SFX thưa, chỉ ở chuyển cảnh đặc biệt** — kiểm bằng mô hình rỗng (so 3000 cửa sổ ngẫu nhiên):
  năng lượng 9–15,5 kHz tại 30 điểm cắt có phân vị trung bình 54 % (≈ ngẫu nhiên) ⇒ **cắt thường KHÔNG có
  tiếng**. Chỉ nổi rõ (≥ phân vị 92) ở: 4,45 (zoom-nhoè, whoosh), 22,73 (vào cảnh mở chương), 32,57,
  46,53 (lớp đỏ), 51,93 (loé cam), 86,27 (loé cam vào CTA). Phổ 16–17,5 s có vạch âm cao kiểu "lấp lánh"
  lúc tấm kính 3D hiện; 9,3–9,7 s có vạch cao lúc nhân bản loé.
  ⇒ Quy tắc: **whoosh cho loé/zoom chuyển chương, lấp lánh cho hiệu ứng "phép thuật"; cắt thường im.**
- Âm thanh mẫu chỉ 32 kb/s nên KHÔNG nhận diện được đúng file SFX gốc — skill dùng thư viện riêng.

## 6. Tóm tắt phong cách (để dựng lại)

1. Giọng sale = xương sống; cắt lặng sát; hook người nói 10–13 s, CTA người nói 5 s; giữa phủ hình dự án.
2. Mỗi cụm ý ~2–3,5 s một cảnh, cắt cứng ~0,25 s sau chữ mở cụm.
3. Mỗi cảnh một cụm chữ: dẫn trắng nhỏ + KHOÁ to (số vàng / chữ hẹp đậm màu theo cảnh) + viết tay trắng;
   gõ chữ 30–45 ký tự/s đúng lúc nói, xoá ngược khi hết cảnh.
4. Ảnh ngang → thẻ bo góc trên nền nhoè của chính nó; liệt kê 3 thứ → ghép 3 thẻ nền xanh ngọc + bướm.
5. Điểm nhấn hiệu ứng chỉ ở hook (phóng-lùi, nhấp nháy, loé + rung, zoom chuyển ý, nhân bản loé) và ở
   2–3 cú chuyển chương (loé ánh cam).
6. Nhạc nền sôi động nhẹ ~136 BPM, thấp hơn giọng 14–18 dB; SFX thưa chỉ ở hiệu ứng.

## 7. Điểm skill cố ý KHÁC mẫu (theo các luật user đã chốt)

- **Zoom-nhoè 4,43 s**: user ghét nhoè ("video bị mờ hẳn đi", 17/10) ⇒ mặc định thay bằng **phóng nhanh +
  loé trắng, sắc nét**; muốn đúng mẫu thì bật `"nhoe": true` trong plan.
- **Độ to**: −14 LUFS thay vì −8,8 LUFS (mẫu clip).
- **SFX**: đặt cùng chỗ mẫu nhưng phải NGHE RÕ (đỉnh cao hơn giọng tại chỗ +3…+6 dB).
- **Người hiện từ trong suốt** (16,4 s): cần clean plate, không làm tự động; chỉ làm tấm kính 3D.
- **Chữ an toàn nền tảng**: không đặt chữ đọc được dưới y 1600 (UI TikTok/FB che).
