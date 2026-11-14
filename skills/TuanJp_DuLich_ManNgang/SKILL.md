---
name: TuanJp_DuLich_ManNgang
description: Dựng VIDEO GIỚI THIỆU / TRẢI NGHIỆM DU LỊCH Việt Nam khổ NGANG 16:9 (1920×1080, 30 fps) để ĐĂNG YOUTUBE, từ 2 đầu vào — 1 FILE AUDIO giọng đọc kịch bản + 1 THƯ MỤC RESOURCES clip / ảnh (ngang hay dọc đều được, nhạc nền để luôn trong Resources) — phong cách điện ảnh riêng cho khổ ngang (khách chốt 14/11/2026): ẢNH / CLIP LUÔN TRÀN MÀN (không chia ô, không thẻ dọc; clip dọc lấy dải 16:9 neo cao + làm nét bù), footage chỉnh màu ấm + hạt phim + tối mép, Ken Burns, KHUNG ĐIỆN ẢNH 2.35:1 tới cú drop; TEASER MỞ MÀN ~20 s chỉ nhạc (tự dò BPM / ô nhịp, lấy đoạn CAO TRÀO của bài, cảnh đẹp nhất mỗi điểm đến cắt đúng phách + tên điểm đến đập vào) rồi giọng hook + cú DROP tên chủ đề (~30 s cao trào giữ người xem); mỗi điểm đến mở bằng BẢN ĐỒ VỆ TINH THẬT A → B kiểu GOOGLE MAPS (Esri + đường đi thật OSRM, camera cận điểm đi → toàn tuyến → sà điểm đến, tuyến xanh chạy + xe chạy theo tuyến, ghim đỏ rơi, thẻ trắng '≈ 4 giờ 15 phút (314 km)' đếm lên, bản đồ VN nhỏ góc có Hoàng Sa / Trường Sa), BÌNH LUẬN ẢO tiếng Anh + tiếng Hàn khen / chê nhẹ kiểu YouTube cho mỗi điểm đến / món ăn (tự đặt chỗ trống, tên giả, cờ, lượt thích, tim tác giả); bộ CHỮ RIÊNG khác màn dọc (Barlow Condensed IN HOA trắng + nhấn XANH NGỌC, Montserrat nghiêng, nhãn giãn chữ) — mở đầu, hook, chương, địa danh, từ khoá, tiêu đề, chip, số lớn, liệt kê, trích dẫn; SUB hộp tối bo góc 1 dòng, chữ đang đọc xanh ngọc, không tách từ ghép; MÀN KẾT CẢM ƠN: câu hỏi bình luận + lựa chọn → 'Cảm ơn bạn đã xem' → lời mời Thích & Đăng ký → tay bấm ĐĂNG KÝ + chuông + THÍCH tim bay; SFX thưa, nhạc nền CHỈ khi Resources có file nhạc (−14 dB dưới giọng, teaser to như giọng), −14 LUFS. Whisper nhận lời → Claude viết ke_hoach.json theo NGHĨA → kiểm → ảnh duyệt → Chrome headless dựng (mã hoá 1 lần) → tự kiểm trên file cuối. Trigger '/TuanJp_DuLich_ManNgang', 'video du lịch màn ngang', 'video du lịch YouTube 16:9 từ audio + resources', 'giới thiệu du lịch Việt Nam khổ ngang', 'ráp audio kịch bản với thư mục resources thành video du lịch ngang'.
---

# TuanJp_DuLich_ManNgang — video du lịch NGANG 16:9 cho YouTube

Đầu vào: **1 file giọng đọc kịch bản** + **thư mục Resources** (clip / ảnh, ngang hoặc dọc; file nhạc nền nếu có).
Đầu ra: `<audio>_DLN.mp4` 1920×1080 30 fps, −14 LUFS, có sub karaoke, đồ hoạ chữ theo lời, màn kết YouTube.

Skill dọc `TuấnJp_Dulich_ManDoc` chỉ là THAM KHẢO (người dùng 13/11/2026: "cái này là skill màn ngang, skill kia bạn tham khảo
thôi"). Skill này đứng riêng: code, phông, SFX, khung trang dựng đều nằm trong thư mục skill.

- Khuôn kế hoạch: **`references/ke_hoach_schema.md`** (mọi trường, mọi bố cục, mọi đồ hoạ).
- Bản điền chuẩn (bản khách chốt 14/11/2026: teaser + 4 bản đồ A → B + bình luận ảo + màn cảm ơn, 4 điểm đến, ~138 s):
  **`references/vi-du-4-diem-den.json`** — ĐỌC TRƯỚC khi viết kế hoạch mới.
- Số phong cách: `scripts/chung.py` (khổ, vùng an toàn, sub, bố cục, chuyển cảnh, SFX, nhạc, chữ màn kết theo ngôn ngữ) +
  `assets/khung/ngang.css|js` (màu, phông, chuyển động). Bản đồ VN: `assets/khung/vn_ban_do.js`.

## TRẠNG THÁI / VIỆC TIẾP THEO (đọc trước khi train tiếp)

- **14/11/2026 — train lại theo 5 góp ý của khách** (video tham khảo YouTube `YQRM2WOHGiA` — CHỈ tham khảo): (1) bản đồ GG Maps A → B có km + giờ,
  (2) bình luận ảo Anh / Hàn khen chê mỗi điểm / món, (3) cuối video cảm ơn + mời Thích & Đăng ký, (4) ~30 s đầu cao trào giữ người xem,
  (5) KHÔNG chia màn / thẻ kiểu màn dọc — ảnh / clip luôn tràn màn, chữ + sub khác hẳn màn dọc. Người dùng chọn: teaser nhạc + hook lời;
  bản đồ vệ tinh + tuyến kiểu GG Maps. Tất cả đã thành LUẬT TỰ ĐỘNG trong script (mục 2, 5, 7, 8, 13–15 ĐÃ CHỐT) cho mọi kịch bản.
- Kế hoạch mẫu bản mới (Màn Ngang, 4 điểm đến, teaser + 4 bản đồ + 4 đợt bình luận + màn cảm ơn): **`references/vi-du-4-diem-den.json`**
  (`D:\____TTT_____\KH_Test\Tuấn_jp\Màn Ngang`, mã tài nguyên theo thứ tự tên file trong `Resources`). Bản cũ (thẻ dọc / ghép ô, đã bỏ):
  `references/vi-du-4-diem-den_ban3_cu.json` — chỉ để tra giờ lời.
- Bản giao 14/11/2026: `D:\____TTT_____\KH_Test\Tuấn_jp\Màn Ngang\Audio_DLN.mp4` (người dùng duyệt D1–D8 mặc định) — chờ khách xem.
- Còn mở: D1 tên kênh / avatar màn kết đang TRỐNG; clip DỌC 720 px tràn khung ngang phóng 2,7× (mềm — đã làm nét `cas`); khách gửi clip
  ngang / 4K thì nét hẳn. Chưa có: đóng gói zip gửi khách (`dong-goi` như bản dọc).

## Skill này được bồi thêm sau mỗi lần chạy thật

| Ngày | Video | Học được / sửa |
|---|---|---|
| 13/11/2026 | `Tuấn_Jp_Skill2\Audio.mp3` (113 s: hook 4 câu → "Việt Nam" → Sa Pa → Hạ Long → Ninh Bình → thác Bản Giốc → tổng kết 4 điểm → câu hỏi khán giả) + Resources 16 clip (12 DỌC 720×1280, 4 ngang 1280×720) + 8 ảnh (3 ảnh ≥ 2000 px, 5 ảnh 600–1024 px), không nhạc | Bản đầu. **Clip dọc chiếm đa số** → khổ ngang không được phóng tràn (720 → 1920 = 2,7× vỡ): bố cục `the_doc` (thẻ 506×900 + nền nhoè chính nó) và `ghep` (2–4 ô). **Tư liệu ít** (Bản Giốc chỉ 1 clip 15 s + 1 ảnh cho ~25 s lời) → `vung` cắt 1 ảnh to thành nhiều khung khác nhau (toàn cảnh / tầng thác trên / cận thác dưới / rừng). Lỗi bắt khi soi: CSS `.dh {display:none}` làm MỌI đồ hoạ không hiện (JS `show()` chỉ xoá style inline) → ẩn bằng JS; đo chữ lúc phần tử đang `display:none` ra bề rộng 0 → bật tạm khi `init`; chữ có gradient `background-clip:text` mà từng ký tự con có `transform` thì MẤT CHỮ → gradient đặt trên từng ký tự; dòng viết tay màn kết thiếu `position:absolute` nhảy lên góc trái; câu hỏi màn kết rộng 1060 đè thẻ ảnh bên phải → cột chữ ≤ 760; chữ "Hùng vĩ" đè người trên xích đu → thêm `y` cho khối chữ. Whisper sai 19 chữ (Phan Xipan, Tháp Bản Dốc, cắp treo, trốn bồng lai viên cảnh, Hạ Long trên cạm…) → `sua_loi`. GPU không dùng được (thiếu cublas64_12.dll) → Whisper CPU 7 phút. Kết quả `Audio_DLN.mp4` 114,97 s: tự kiểm ĐẠT 9/9 (−14,0 LUFS, đỉnh −1,8 dBTP, không khung đen, chữ không đè); dựng ~3 phút (4 luồng × ~6 khung/s); file 479 MB (CRF 17 + hạt phim — YouTube nhận tốt). Bỏ 4 tài nguyên: tàu sắt Hà Nội + 2 clip drone đêm (không có trong lời, tay / điện thoại che), ảnh cáp treo trên BIỂN |
| 13/11/2026 | cùng video — người dùng: **"ở đoạn đầu video tôi thấy chưa edit hay"**, **"ý là đoạn đầu edit video chưa oki"** → duyệt plan | Soi 0–16 s: mở bằng 0,6 s màn đen; 3/4 cú chuyển trong hook NHOÈ (lia nhoè chuyển động 3,0 s / 7,2 s, zoom nhoè 4,9 s — hình nát ~0,45 s mỗi cú, trùng góp ý cũ "hiệu ứng mờ khó chịu, làm video mờ hẳn đi"); hook 10,6 s chỉ 4 cảnh (3 ảnh tĩnh đứng 2–3 s) → như trình chiếu; cảnh 3,6–4,8 s là thẻ dọc nhỏ trên nền xám nhoè; hook không có chữ; "VIỆT NAM" hiện từng chữ + viết tay quét ≈ 2 s mới đọc trọn, nền là 3 clip điện thoại tầm thường. Sửa → **LUẬT HOOK** (mục 12): vào thẳng hình khung 0; mỗi vế 1–2 cảnh 0,8–1,7 s, cắt `phong` (đập vào 1,22 → 1 + loé nhẹ + whoosh) đúng nhịp; mọi cảnh PHỦ KÍN khung (clip dọc → `ghep`); mỗi vế 1 `hook_tu` (KHỐI CHỮ Anton + nhãn địa danh có ghim) hiện ngay khung cắt; khung 0 có câu hỏi serif đủ chữ ngay; tên chủ đề = **CÚ DROP** (dồn riser 1,85 s → nổ trầm `boom.wav` tự tổng hợp + loé trắng 0,9 + rung 0,4 s + khung điện ảnh bung 0,32 s; chữ đập vào trọn trong 0,32 s, vệt sáng vàng quét); nền drop = ảnh ĐẸP NHẤT toàn cảnh (lộ rộng của chính ảnh cận mở đầu). **Bỏ NHOÈ ở MỌI chuyển cảnh + chữ** (lia = đẩy nhanh sắc nét, zoom = phóng vụt → loé → thu, nhoe = hoà tan sáng bừng); chữ chương / tiêu đề / địa danh đọc được ≤ 0,45 s. Lỗi bắt khi soi: chữ GRADIENT (`background-clip:text`) mất DẤU tiếng Việt ("BIEN MAY") vì dấu nằm ngoài hộp line-height 1 → nới padding .26em / bù margin âm. **SFX nghe rõ**: bộ trộn đo giọng TẠI CHỖ (±1,5 s) và tự tính gain cho từng tiếng tới mức `SFX_TREN` (hook +5…+7 dB, chuyển cảnh +3, pop 0) — báo trong `tron_bao_cao.json` + tự kiểm (lỗi khi chạy: số numpy float32 không ghi được JSON → ép `float`). Kết quả `Audio_DLN_ban2.mp4`: tự kiểm ĐẠT 10/10, SFX nghe rõ 56/56, −14,0 LUFS, đỉnh −1,6 dBTP |
| 13/11/2026 | cùng video, vòng 3 — người dùng: "cảnh đầu oki rồi, nhưng hiệu ứng chuyển chưa xịn, **1-2 giây lại hiển thị cái ảnh**, chuyển hình xong có sfx, **chưa kịp nhìn**, chuyển nhanh quá"; thêm `Resources\Music_Bg.mp3` (125,7 s): "hết nhạc mà video còn thì LOOP, Resources không có nhạc thì làm không có, có thì làm có — lưu vào skill" | Hook 8 cú cắt / 10,6 s (1,0–1,6 s mỗi cảnh) + whoosh mỗi cú = quá gấp → **mỗi vế câu 1 cảnh** (4 cảnh 2,0–3,5 s), chữ khoá đổi trên cùng cảnh; chuyển MƯỢT 0,6–0,8 s: kiểu mới `zoom_muot` (cũ đẩy vào 1 → 1,18, mới thu 1,12 → 1 chồng lên), `lia` thành trượt có chiều sâu (cũ lùi + tối, mới phủ lên), `truot` đẩy êm, `loe` 0,8 s; `phong` / `zoom` gấp chỉ dùng khi cố ý. **Luật thời lượng cảnh**: ≥ 2,5 s (`CANH_MIN`), montage thẻ dọc cùng chỗ ≥ 2,0, hook ≥ 1,8; < 1,5 s ⛔. Thân video gộp 5 chỗ < 2,5 s (đỉnh Fansipan + cờ, du thuyền + boong tàu, giãn Ninh Bình / Bản Giốc). **SFX THƯA**: cú chuyển thường KHÔNG tiếng; chữ hiện KHÔNG tiếng; chỉ còn cú drop (riser + boom + lấp lánh), whoosh màn quét mở chương, ding số chương, pop NHỎ (−4 dB dưới giọng) ở chip / liệt kê, nút màn kết. Nhạc nền: luật mục 9 (loop khi ngắn). Thư mục `_dln_work` bị dọn giữa chừng → kế hoạch lấy lại từ `references/vi-du-4-diem-den.json`, chạy lại Whisper. Chữ hook hiện khi cảnh cũ còn trên hình → `kiem-kh` tự dời chữ `hook_tu` tới lúc cảnh vào xong. Kết quả `Audio_DLN_ban3.mp4`: tự kiểm ĐẠT 11/11 — nhạc −14,1 dB dưới giọng (bỏ 9,9 s đầu bài cho nốt kết trùng cuối), SFX 26 tiếng (trước 68) đều nghe rõ, −14,0 LUFS, đỉnh −1,6 dBTP |
| 14/11/2026 | `KH_Test\Tuấn_jp\Màn Ngang` (cùng Audio.mp3 113 s + Resources 16 clip, 8 ảnh, `Music_Bg.mp3`) — **khách góp 5 ý** (video YouTube `YQRM2WOHGiA` chỉ tham khảo): (1) bản đồ GG Maps A → B có km + bao lâu, (2) bình luận ảo tiếng Anh + Hàn khen chê mỗi điểm / món, (3) cuối video cảm ơn + mời like & đăng ký, (4) ~30 s đầu cao trào "xem là muốn đi du lịch luôn", (5) KHÔNG chia màn / thẻ kiểu màn dọc — ảnh / video luôn full màn, chữ + sub khác hẳn màn dọc. Người dùng chọn: teaser nhạc + hook lời; vệ tinh + tuyến kiểu GG Maps | Tất cả thành LUẬT TỰ ĐỘNG (ĐÃ CHỐT 2, 5, 7, 8, 13–15): **luôn tràn màn** (`bo_cuc` chỉ `tran`, clip dọc lấy dải 16:9 `cat_y` 0,42 + làm nét `cas`); **teaser** `mo_man` (`nhip.py` dò BPM / phách / đoạn cao trào; cảnh cắt đúng phách; nhạc teaser to ~giọng, hoà 1 s sang nhạc thân; phần thân tự dời `OFF`); **bản đồ A → B** tự có ở mỗi `chuong` có `toa_do` (`ban_do_that.py`: Esri + OSRM, camera cận → toàn tuyến → sà, xe chạy, ghim đỏ, thẻ trắng "≈ giờ (km)", VN nhỏ có Hoàng Sa / Trường Sa; số ước tính luôn "≈" + hỏi D7); lệnh mới `run.py tim "<tên>"`; **bình luận ảo** tự đặt mỗi chương (`binh_luan.py` + `assets/binh_luan.json`, 2 khen + 1 chê nhẹ, en / ko, chỗ trống không đè đồ hoạ lớn; D8); **màn cảm ơn** (câu hỏi + lựa chọn → "Cảm ơn bạn đã xem" sau khi giọng đọc xong → lời mời → tay bấm Đăng ký + chuông + Thích); **bộ chữ mới** Barlow Condensed in hoa trắng + nhấn xanh ngọc, Montserrat nghiêng, sub hộp tối. Lỗi bắt khi soi: Ninh Bình ra bình luận "vịnh" (mô tả "Hạ Long trên cạn") → xét tên trước; `luc_binh_luan` chưa dời theo teaser → thêm vào `KHOA_GIO`; cảm ơn hiện khi giọng còn hỏi → tính giờ CTA trước; thẻ bản đồ tràn "(314 km)" → co theo chữ; MẤT DẤU NẶNG ("VINH HA LONG", "CẢM ƠN BAN") — `.mask` đệm theo em của chính nó → đệm theo cỡ chữ con, và Barlow đặt dấu nặng quá sâu → `sua_font.py`; từ khoá 3 mục 1 hàng đè mặt người → tự xếp cột + dời `vi_tri` / `y`; sub tách "tiếp / tục", "kỳ / quan", "hành / trình", "cảnh / tượng" → +77 từ ghép du lịch. Kết quả `Màn Ngang\Audio_DLN.mp4` 137,8 s (teaser 20,1 s + giọng), 1920×1080: tự kiểm ĐẠT 17/17 — −14,1 LUFS, đỉnh −1,7 dBTP, nhạc thân −13,7 dB dưới giọng, teaser −1,9 dB so với giọng, SFX 50/50 nghe rõ; dựng 262 s (4 luồng × ~5 khung/s), 643 MB |

## CÁC DIALOG SKILL PHẢI HỎI (cổng duyệt — dừng 1 lần, LẦN NÀO GỌI SKILL CŨNG HỎI LẠI, có đề xuất sẵn)

| # | Hỏi | Đề xuất mặc định | Bắt buộc trả lời |
|---|---|---|---|
| D1 | Kênh cho màn kết: tên kênh, @handle, file avatar | trống → avatar la bàn, không tên (KHÔNG tự bịa tên kênh) | có |
| D2 | Nhạc nền + TEASER — CHỈ hỏi khi Resources có file nhạc: file đã ghép (tên, độ dài, BPM, teaser lấy đoạn từ giây mấy của bài, dài bao nhiêu ô nhịp; phần thân lùi bao nhiêu giây) — giữ / đổi đoạn / tắt teaser | giữ | khi có nhạc |
| D7 | SỐ TRÊN BẢN ĐỒ A → B (bảng `bang_duyet.txt` mục BẢN ĐỒ): điểm đi (chương đầu mặc định Hà Nội), phương tiện, "≈ km · ≈ giờ" ước tính OSRM — đúng ý khách chưa / đổi điểm đi / ghi số khác (`thoi_gian`, `khoang_cach`) | giữ số ước tính có "≈" | có |
| D8 | BÌNH LUẬN ẢO (mục BÌNH LUẬN ẢO): tiếng (mặc định Anh + Hàn), 3 thẻ / điểm đến, câu khen / chê — giữ / đổi câu / thêm cho món ăn / tắt | giữ | không |
| D3 | Màn kết: câu hỏi bình luận + lựa chọn (lấy từ câu cuối của lời) hoặc tiêu đề + viết tay — giữ hay đổi | câu hỏi trong lời | không |
| D4 | Phần lời KHÔNG có tư liệu khớp → đang dùng cảnh mượn / cắt vùng ảnh nào (liệt kê theo giây) — bổ sung clip hay giữ | giữ | không |
| D5 | Chữ đã sửa lỗi nhận giọng (bảng `sua_loi`) + chỗ còn đoán | — | không |
| D6 | Tài nguyên KHÔNG dùng và lý do (vd ảnh cáp treo trên BIỂN không khớp lời cáp treo Fansipan; clip có tay / điện thoại che kín) | — | không |

Không phải hỏi (đã chốt bên dưới): khổ, fps, phong cách chữ, vị trí sub, mức nhạc, −14 LUFS.

## ĐÃ CHỐT (không tự đổi trừ khi người dùng yêu cầu)

1. **Khổ NGANG 1920×1080, 30 fps** — YouTube. Hết hình = max(tiếng cuối + 0,8 s, đầu màn kết + 5 s). Vùng chữ title-safe x 96–1824, y 54–1026.
2. **LUÔN TRÀN MÀN** (khách 14/11/2026: "không làm ảnh kiểu chia màn hình… giống màn hình dọc quá, lúc nào cũng full màn hình giữa ảnh và
   video"): mọi cảnh `bo_cuc` = `tran` (bỏ trống là `tran`; `the_doc` / `ghep` / `the_anh` → ⛔ `kiem-kh`; 1 cảnh 1 nguồn — liệt kê nhiều thứ
   thì nhiều cảnh nối tiếp). Clip / ảnh DỌC: lấy dải 16:9 neo cao `CAT_Y_DOC` 0,42 (trời + chủ thể; đổi bằng `cat_y`), phóng > 1,5× thì làm nét
   `cas` bù (⚠ khi phóng > 1,9× — báo D4). Ảnh nhỏ: cắt `vung` vừa phải, ⚠ khi phóng > 1,6×. Ưu tiên clip ngang / ảnh ≥ 1920 cho cảnh dài.
3. **Footage**: chỉnh màu 1 lần lúc trích (tương phản 1,06, bão hoà 1,16, ấm vùng sáng, làm nét nhẹ) + lớp màu ấm soft-light + tối mép +
   dải tối đáy (cho sub) + hạt phim; mỗi cảnh Ken Burns (ảnh mạnh 7,5 %, clip nhẹ). Video vào THẲNG hình ở khung 0 (không mở từ đen — khung
   đầu là ảnh xem trước YouTube); KHUNG ĐIỆN ẢNH 2.35:1 từ đầu tới cú drop `mo_dau` thì bung ra 0,32 s (sub nằm trên dải đen) — `dien_anh: false` để tắt.
4. **KHÔNG NHOÈ** (người dùng ghét: "hiệu ứng mờ khó chịu, làm video mờ hẳn đi"): không chuyển cảnh nhoè / zoom-blur / lia nhoè chuyển động,
   chữ không nhoè vào / ra. Lực chuyển cảnh = đổi khung phóng, loé trắng, đẩy sắc nét, whoosh.
   **MƯỢT, KHÔNG GẤP** (người dùng: "1-2 giây lại hiển thị cái ảnh… chưa kịp nhìn… chuyển nhanh quá"): mỗi cảnh đứng **≥ 2,5 s** (`CANH_MIN`;
   montage thẻ dọc cùng chỗ chỉ đổi hình ≥ 2,0; hook ≥ 1,8 theo vế câu; `kiem-kh` ⚠ dưới ngưỡng, ⛔ < 1,5 s) — thiếu thì GỘP với cảnh kề,
   đừng cắt vụn; chuyển 0,6–0,8 s, mặc định `zoom_muot` / `lia` (trượt có chiều sâu) / `loe` / `hoa_tan`; `phong`, `zoom` (gấp, có loé) chỉ khi cố ý.
   **Chuyển cảnh** theo `CHUYEN` trong `chung.py`; đổi kiểu liên tục; `man` (màn sáng quét chéo) để MỞ CHƯƠNG / điểm đến mới; `nhoe` (hoà tan sáng bừng) ngày → đêm;
   `lia` / `truot` cùng mạch; `zoom` khi đi sâu vào cùng 1 cảnh (vd ảnh toàn cảnh → vùng cận); thẻ dọc nối thẻ dọc cùng chỗ thì `hoa_tan` (thẻ đứng yên, hình đổi).
5. **Phông / màu — BỘ CHỮ NGANG RIÊNG** (khách 14/11/2026: "text đang giống text của skill màn dọc, muốn khác hẳn, nhưng vẫn là kiểu chữ /
   sub du lịch"): KHÔNG serif Playfair, KHÔNG viết tay vàng. Tít `.tit` = Barlow Condensed Black IN HOA trắng đổ bóng (nghiêng `.tit_i` ở hook);
   nhãn `.nhan_nho` = Barlow Condensed ExtraBold giãn chữ màu XANH NGỌC `#4FE3D0`; dòng phụ `.nghieng` = Montserrat SemiBold / Bold Italic
   (thay viết tay); số viền xanh ngọc; chữ sáng gradient `.chu_sang` cho tên chủ đề; vạch nhấn xanh ngọc. Đỏ nút `#FF2A4D`. Trường `viet_tay`,
   kiểu `tay` / `serif` trong kế hoạch vẫn dùng được — trang dựng tự vẽ theo bộ chữ mới. Chữ khoá dài tự ngắt 2 dòng cân rồi mới co.
6. **Đồ hoạ**: CHỮ HIỆN NGAY — khối chữ chính đọc được ≤ 0,4 s sau khi vào (không chạy từng chữ, không chờ mốc nói muộn); mỗi lúc 1 đồ hoạ lớn (`dia_danh`, `chip` được chồng); mỗi mục chữ ≥ 1,6 s (được hiện SỚM hơn lời — `kiem-kh` tự sửa 🔧);
   không quá 10–12 s không có chữ đồ hoạ; chữ đồ hoạ là chữ ĐẮT của lời (1–6 chữ), không bịa số. Mỗi điểm đến lớn = 1 `chuong` (số
   01/02… tự đánh, `toa_do` → BẢN ĐỒ A → B toàn màn, mục 13). **Bản đồ Việt Nam trên hình LUÔN có quần đảo Hoàng Sa, Trường Sa** (`vn_ban_do.js`).
7. **Sub**: HỘP TỐI bo góc (rgba(8,12,16,.6), bo 14) mỗi dòng, Be Vietnam Pro 600 44 px trắng, chữ đang đọc XANH NGỌC (không vàng, không phồng
   viền như màn dọc); đáy khung, ưu tiên 1 dòng ≤ 46 ký tự (dài thì 2 dòng, rộng > 1720 px tự co); không tách từ ghép (`assets/tu_ghep_vi.txt`,
   `sub.giu_lien`, tên trong `sua_loi`) hay tên riêng; tắt trong màn kết.
8. **MÀN KẾT CẢM ƠN ≥ 6,5 s** (khách 14/11/2026: "cuối video cảm ơn mọi người xem và hãy like và đăng ký"; chỗ gắn End screen YouTube): nền cảnh
   chậm tối dần → (nếu lời có câu hỏi) `cau_hoi` + hàng nút `lua_chon` → **"Cảm ơn bạn đã xem"** (`cam_on`, tít to giữa) hiện khi giọng đọc
   xong câu cuối (`luc_cam_on`, tự tính) + vạch xanh ngọc + lời mời **"Nhấn Thích & Đăng ký kênh…"** (`loi_moi`) → hàng nút ĐĂNG KÝ + Thích +
   Chuông + Chia sẻ → tay bấm Đăng ký (`luc_cam_on + 1,8`) → chuông lắc → tay bấm Thích (`+1,3`) tim bay. Chữ mặc định theo `NGON_NGU`
   (`cam_on`, `loi_moi`); video tự kéo dài cho tay bấm Thích xong + 1,5 s.
9. **Âm thanh**: chỉ giọng của file audio (tiếng clip bỏ hết) + **SFX THƯA** (người dùng: "chuyển hình xong có sfx… khó chịu"): cú chuyển cảnh
   thường và chữ hiện KHÔNG có tiếng; chỉ có: cú drop tên chủ đề (riser + boom + lấp lánh), whoosh màn quét mở chương (`man`), ding nhỏ số
   chương, pop NHỎ ở chip / mục liệt kê / ghim (−4…−3 dB dưới giọng), riser + ding số lớn, click / chuông / thích ở màn kết. Tiếng nào có thì
   phải NGHE RÕ: gain tự tính theo giọng tại chỗ tới mức `SFX_TREN` (`chung.py`; drop +7, nút màn kết +4).
   **NHẠC NỀN (người dùng chốt 13/11/2026): Resources CÓ file nhạc → ghép; KHÔNG có → làm không nhạc** (không hỏi, không tự tổng hợp nhạc).
   Nhận file theo tên (music / bg / bgm / nhac…, ≥ 8 s; file giọng tên voice / giọng / kịch bản… không bị lấy). Nhạc NGẮN hơn video → **LẶP LẠI**
   cho tới hết video (nối hoà tan 1,5 s); dài hơn ≤ 45 s → bỏ bớt ĐẦU cho nốt kết của nhạc trùng cuối video; dài hơn nữa → giữ đầu, mờ dần cuối.
   Nhạc −14 dB dưới giọng (cả bài), dâng +8 dB ở khoảng lặng ≥ 1 s, san bằng đoạn nhạc nhỏ.
   Master **−14 LUFS, đỉnh ≤ −1 dBTP** đo trên file AAC cuối.
10. **Ngôn ngữ**: audio tiếng gì thì mọi chữ trên hình tiếng đó (chữ màn kết mặc định theo `NGON_NGU` trong `chung.py`).
11. Không ghi đè video cũ: `<audio>_DLN.mp4`, có rồi thì `_DLN_ban2`…
12. **LUẬT HOOK** (người dùng 13/11/2026: "đoạn đầu edit chưa oki" — mẫu: `references/vi-du-4-diem-den.json` h1–h8, k1–k5, g1):
   - khung 0 = hình đẹp + chữ ĐỦ ngay (câu hỏi `hook_tu` `kieu: "cau"` khi lời mở bằng câu hỏi); không màn đen, không loé che hình;
   - mỗi vế câu hook ĐÚNG 1 cảnh (≥ 1,8 s — vòng 3 người dùng chê 1–2 s/cảnh là "chưa kịp nhìn"), chuyển MƯỢT 0,6–0,8 s (`loe`, `zoom_muot`,
     `lia`), KHÔNG whoosh mỗi cú; MỌI cảnh tràn khung (mục 2); ảnh to cắt `vung` đẹp nhất;
   - mỗi vế 1 `hook_tu`: chữ đắt nhất của vế (BIỂN MÂY / ĐẢO ĐÁ VÔI…) + `nhan` = địa danh, `tu` = khung cắt, `den` = khung cắt sau − 0,03;
   - tên chủ đề (`mo_dau`, mặc định `drop: true`) = CÚ DROP: cảnh `cat` sang ảnh đẹp nhất toàn cảnh, tự có riser trước 1,85 s + boom + loé + rung,
     chữ đập vào trọn trong 0,32 s; dòng viết tay / dòng điểm đến hiện ngay sau 0,2–0,35 s;
   - chữ `hook_tu` hiện SAU khi cảnh của nó đã vào xong (`kiem-kh` tự dời 🔧 tới `tu` cảnh + nửa thời lượng chuyển; ô ghép: ô cuối + 0,45 s) —
     không bao giờ hiện chữ vế mới trên hình của vế cũ;
   - không tách thành thẻ nhỏ, không nhoè, không cắt vụn (< 1,8 s), không SFX mỗi cú chuyển.
13. **BẢN ĐỒ A → B KIỂU GOOGLE MAPS** (khách 14/11/2026: "có ghi gg map Việt Nam đi từ điểm A đến B bao nhiêu km, bao nhiêu lâu"; người dùng
   chọn "vệ tinh + tuyến kiểu GG Maps"): mỗi `chuong` có `toa_do` [lat, lon] (tra `run.py tim "<tên>"`) TỰ thành 1 bản đồ toàn màn ≥ 3,6 s
   (`BAN_DO_MIN`) — ĐẶT `tu` ĐÚNG ĐẦU CÂU MỞ ĐIỂM ĐẾN ("Hành trình đầu tiên…", "Rời Sa Pa…"), `den` hết câu, `luc_den` = giây đọc tên điểm đến:
   - điểm đi = điểm đến của chương trước; chương đầu = `kh.xuat_phat` hoặc **Hà Nội** (`XUAT_PHAT_MAC_DINH`); đổi riêng: `xuat_phat: {ten, toa_do}`;
   - ảnh vệ tinh Esri thật (cache chung `_cache_tiles\esri`), đường đi THẬT OSRM (`phuong_tien` o_to mặc định / xe_may / xe_buyt / di_bo / xe_dap;
     may_bay = cung bay, không giờ); camera cận điểm đi → lùi toàn tuyến → giữ khi xe chạy → sà vào điểm đến; tuyến xanh `#4C8DF6` viền
     đậm chạy dần + huy hiệu xe chạy theo tuyến (máy bay xoay theo hướng); nhãn trắng điểm đi, nhãn đỏ + GHIM ĐỎ Google rơi ở điểm đến;
   - thẻ trắng kiểu Google: nhãn "Tuyến đường", **giờ xanh lá to "≈ 4 giờ 15 phút"** + km đếm lên "(314 km)" + "Ô tô · ước tính theo đường đi
     thật"; số ƯỚC TÍNH luôn có "≈" (làm tròn 5 phút < 1 giờ, 15 phút ≥ 1 giờ; xe khách ×1,15, xe máy ×1,2) — lời nói số thì ghi `thoi_gian` /
     `khoang_cach` theo lời (không "≈"); bản đồ VN nhỏ góc phải trên có tuyến nét đứt + Hoàng Sa, Trường Sa;
   - tới nơi: tên điểm đến tít to + nhãn "Điểm đến 01" + `phu`; vào bằng phóng nhẹ 1,07 → 1, ra mờ + phóng;
   - SFX: swoosh lúc bay vào, tiếng xe rất nhỏ khi chạy (đường bộ), ding nhỏ lúc ghim rơi;
   - `ban_do: false` để chương không có bản đồ; câu di chuyển giữa chừng dùng `hanh_trinh` (`xuat_phat`, `diem_den` có `toa_do`) — cùng bản đồ.
   - `kiem-kh` in số từng tuyến (🔧) → HỎI D7; `kiem` đếm số bản đồ.
14. **BÌNH LUẬN ẢO tiếng Anh + tiếng Hàn** (khách 14/11/2026: "mỗi địa điểm, món ăn có bình luận ảo bằng tiếng Anh, tiếng Hàn khen chê"):
   - TỰ ĐỘNG mỗi `chuong` 1 đợt 3 thẻ (2 khen + 1 chê nhẹ, xen tiếng `binh_luan_nn` mặc định ["en", "ko"]) — NGOẠI LỆ DUY NHẤT của luật ngôn ngữ;
   - thẻ kiểu YouTube nổi cột PHẢI (x 1250, y 104): avatar chữ cái màu, @tên GIẢ tự đặt, cờ nhỏ (KR / US / GB / AU / CA), "2 tuần trước",
     câu, 👍 lượt thích (1.7K / 1.2천), "Trả lời", tim tác giả bật sau 1,1 s; 3 thẻ trượt vào cách 1,25 s, đứng 6 s; pop nhỏ mỗi thẻ;
   - câu lấy từ `assets/binh_luan.json` theo LOẠI cảnh đoán từ TÊN trước rồi mới `phu` (núi, cáp treo, vịnh, thác, sông nước, biển, chùa,
     thành phố, ẩm thực, chung); tên địa danh dịch (Ha Long Bay / 하롱베이…); chọn tất định (dựng lại ra y bản duyệt), không trùng câu / người
     trong cả video; thêm câu / địa danh mới → sửa `binh_luan.json`;
   - chỗ đặt: sớm nhất từ `den` chương + 2,5 s (hoặc `luc_binh_luan` của chương) mà KHÔNG trùng đồ hoạ lớn nào (chỉ chung khung với
     `dia_danh` / `chip`), xong trước chương sau; không có chỗ → ⚠ → Claude dời / bỏ bớt chữ hoặc thêm tay;
   - MÓN ĂN / điểm phụ: thêm tay `{"loai": "binh_luan", "tu": …, "ten": "Phở bò", "loai_canh": "am_thuc"}` (thiếu `muc` thì tự sinh; `muc`
     viết tay được: `{nn, chu, ten, khen: false}`); tắt: `binh_luan: false` (cả video) hoặc trên chương.
15. **TEASER MỞ MÀN ~20 s** (khách 14/11/2026: "đầu video để đoạn cao trào giật gân giữ người xem tầm 30 s, xem cái là muốn đi du lịch luôn";
   người dùng chọn "teaser nhạc + hook lời"): `mo_man: {dai, canh[], do_hoa[]}` — giờ RIÊNG 0…dai; phần thân viết theo giờ `loi_doc.txt`
   như cũ, script tự dời mọi giờ (+ giọng, sub, SFX) thêm `dai`:
   - `nhip.py` dò BPM / phách / ô nhịp của nhạc nền, chọn đoạn CAO TRÀO (`nhac_tu` tự chọn: đầu ô nhịp mà 20 s sau to nhất + có cú dâng);
     `dai` tự khớp về đầu ô nhịp → giọng vào đúng phách mạnh; giờ cảnh / chữ teaser tự bắt về phách gần nhất;
   - 1 cảnh / ô nhịp (≥ 1,8 s), cảnh ĐẸP NHẤT mỗi điểm đến (2 cảnh / điểm), cắt `cat` / đập `phong` / `zoom` đúng phách; tên điểm đến
     `hook_tu` (`chu` = tên, `nhan` = tính từ trong lời) đập vào; kết bằng 1 `tieu_de` (vd "4 điểm đến · 4 vẻ đẹp"); chữ teaser không quá lúc giọng vào (⛔);
   - âm thanh: chỉ NHẠC (dâng +12 dB ≈ to như giọng), cắt cảnh không whoosh, chữ đập 1 whoosh ngắn; 0,6 s trước giọng vào nhạc hạ về nền,
     nối hoà tan 1 s sang nhạc phần thân (phần thân vẫn lùi nhạc cho nốt kết trùng cuối video);
   - sau teaser là hook lời + cú DROP như mục 12 → ~30 s cao trào trước điểm đến đầu tiên; khung điện ảnh giữ từ đầu tới drop;
   - Resources KHÔNG có nhạc → ⚠ bỏ teaser (không tự tổng hợp nhạc); `mo_man.bat: false` để tắt.

## Khuôn kể chuyện du lịch → bố cục + đồ hoạ (áp cho MỌI kịch bản)

| Kiểu câu | Cảnh | Đồ hoạ |
|---|---|---|
| (trước lời) TEASER ~20 s chỉ nhạc | `mo_man.canh`: 1 cảnh / ô nhịp, cảnh đẹp nhất mỗi điểm đến (2 / điểm), `cat` / `phong` / `zoom` | `mo_man.do_hoa`: `hook_tu` tên điểm + tính từ trong lời; kết `tieu_de` (vd "4 điểm đến · 4 vẻ đẹp") |
| Hook mở (câu hỏi "bạn đã bao giờ…", 2–4 vế) | LUẬT HOOK (mục 12): mỗi vế ĐÚNG 1 cảnh (≥ 1,8 s) tràn khung, chuyển mượt `loe` / `zoom_muot` / `lia` | `hook_tu` mỗi vế (chữ khoá + địa danh); đầu hook: `hook_tu` `kieu: "cau"` |
| Gọi tên chủ đề ("vẻ đẹp của Việt Nam") | CÚ DROP: `cat` sang cảnh ĐẸP / Ý NGHĨA nhất (vd cờ Tổ quốc tung bay) | `mo_dau` `drop` (tren / TÊN / dòng phụ / dòng liệt kê điểm đến) |
| Mở 1 điểm đến ("hành trình đầu tiên… Sa Pa", "Rời Sa Pa… hướng về Hạ Long") | cảnh dưới bản đồ = cảnh mở của điểm đó, `chuyen: "man"` | `chuong` + `toa_do` = BẢN ĐỒ A → B (mục 13), `luc_den` = giây đọc tên |
| Kể 2–4 đặc điểm của điểm đó | mỗi đặc điểm 1 cảnh TRÀN (≥ 2,5 s; ngắn thì gộp) | `liet_ke` (tick đúng giây đọc) |
| Tên 1 điểm cụ thể (đỉnh, hang, bến…) | tư liệu khớp tên | `dia_danh` góc dưới — + đợt BÌNH LUẬN ẢO thường rơi vào đây |
| Trải nghiệm ("ngồi trên du thuyền…") | ảnh / clip đúng trải nghiệm, tràn | `chip` |
| Món ăn / đặc sản | ảnh món tràn, đổi đúng giây đọc tên | `chip` / `liet_ke` + `binh_luan` thêm tay (`loai_canh: "am_thuc"`) |
| Cảm nhận ("bồng lai tiên cảnh", "hùng vĩ & yên bình") | cảnh chậm, tràn | `tu_khoa` (2 dòng: tít + nghiêng), `y` né người |
| Câu chốt của 1 điểm ("ít nhất một lần trong đời") | toàn cảnh đẹp nhất, `zoom_ra` | `tieu_de` |
| Tổng kết N điểm ("Sa Pa thơ mộng, Hạ Long kỳ vĩ…") | 2 cảnh tràn đẹp nhất (không ghép ô) | `tieu_de` ("4 điểm đến") rồi `liet_ke` "tên · tính từ" đúng giây đọc |
| Câu kết ý nghĩa | clip người / hành trình | `tieu_de` rồi `tu_khoa` (động từ đắt) |
| Câu hỏi / kêu gọi cuối | cảnh đẹp chậm (`toc_do` 0,6), tràn | màn kết CẢM ƠN (mục 8): `cau_hoi` + `lua_chon` từ lời |

Chọn footage: tên riêng → tư liệu khớp tên (`goi_y.txt`) đúng giây; soi `khung/clip_NN.jpg` để chọn `vao` (tránh tay / điện thoại che,
rung, nghiêng); không lặp cùng đoạn clip (cùng clip khác đoạn được — teaser được dùng lại cảnh đẹp nhất); thiếu tư liệu → cắt `vung` khác
nhau của ảnh to, mượn cảnh cùng kiểu địa hình (báo ở D4); tài nguyên SAI NGHĨA thì bỏ (báo ở D6) — vd ảnh cáp treo trên biển không dùng cho
câu cáp treo Fansipan. Clip dọc tràn khung chỉ thấy dải giữa-trên (29–60 % chiều cao với `cat_y` 0,42) — soi tờ khung xem chủ thể có nằm trong dải.

## Quy trình

Mọi lệnh: `python -I -X utf8 .claude\skills\TuanJp_DuLich_ManNgang\scripts\run.py <lệnh> …` (từ thư mục dự án; PowerShell: đầu phiên
`[Console]::OutputEncoding=[Text.Encoding]::UTF8; $env:PYTHONUTF8='1'`). Cần Python ≥ 3.10 + `requirements.txt`, ffmpeg full, Node ≥ 22,
Chrome / Edge (`DLN_CHROME` nếu nằm chỗ lạ). Máy mới: `run.py cai-dat`.

1. **Quét**: `run.py quet --audio "<giọng>" --res "<Resources>" [--nhac "<nhạc>"] [--ngon-ngu vi]` → `<audio>_dln_work\`: `loi.json`,
   `loi_doc.txt` (lời + giây từng từ), `tai_nguyen.json` + `tai_nguyen.jpg` (mọi tài nguyên + mã + DỌC/NGANG), `khung\clip_NN.jpg` (tờ khung
   có nhãn giây), `goi_y.txt` (tên file ↔ lời), `nhac_nhip.json` (BPM / ô nhịp nhạc nền), `ke_hoach.json` NHÁP (`CAN_CLAUDE_SUA: true`;
   mọi cảnh tràn; có nhạc → khung `mo_man` 8 ô nhịp + đoạn cao trào gợi ý). Quét lại giữ mã cũ, file mới nhận số kế tiếp, kế hoạch đã sửa
   giữ nguyên. Whisper lần đầu tải ~3 GB; CPU ~4 phút / phút audio — chạy nền, đừng huỷ.
2. **Claude viết kế hoạch theo NGHĨA**: đọc `goi_y.txt`, `loi_doc.txt`; MỞ `tai_nguyen.jpg` + MỌI `khung\clip_NN.jpg`; gán mỗi câu 1 kiểu
   (bảng trên); viết `mo_man` (teaser), `canh` / `do_hoa` (chương có `toa_do` — `run.py tim "<tên>"`, cần mạng) / `cta` / `sua_loi`
   (mẫu `references/vi-du-4-diem-den.json`, khuôn `references/ke_hoach_schema.md`); đặt `CAN_CLAUDE_SUA: false`.
3. `run.py kiem-kh --work <dir>` → hết ⛔ (⚠ cân nhắc; 🔧 = đã tự sửa giờ cho kịp nhìn).
4. `run.py duyet --work <dir>` → `duyet.jpg` (khung giữa mỗi cảnh / đồ hoạ / màn kết) + `bang_duyet.txt`. MỞ `duyet.jpg` soi như dân mỹ
   thuật: chữ mất / đè người / đè thẻ / quá nhỏ, thẻ sai bên, ảnh sai nghĩa, logo dán. Soi gần: `run.py khung --work <dir> --times 12.3,45.6`
   (→ `khung_le.jpg`; nên soi cả giây giữa chuyển cảnh).
5. **CỔNG DUYỆT** — gửi `duyet.jpg` + bảng tóm tắt (teaser, số bản đồ, bình luận ảo trong `bang_duyet.txt`), hỏi D1–D8.
6. `run.py dung --work <dir> [--luong 4]` (~115 s video ≈ 6–8 phút, chạy nền) → `<audio>_DLN.mp4`, tự chạy `kiem`.
   Thử nhanh: `--xem-truoc` (20 s đầu). Chỉ đổi TIẾNG: `run.py tron-lai --work <dir>`.
7. `run.py kiem` phải **ĐẠT**: 1920×1080 · 30 fps · không cắt giọng (tính cả giọng lùi sau teaser) · có tiếng · −14 LUFS ±1 · đỉnh ≤ −1 dBTP ·
   nhạc −24…−9 dB (khi có) · nhạc teaser −6…+3 dB so với giọng · luôn tràn màn · đủ bản đồ A → B · đủ đợt bình luận ảo · có teaser · màn
   cảm ơn · không khung đen giữa video · sub không đè chữ đồ hoạ / chữ không tràn mép (chụp hộp chữ mỗi 0,5 s). MỞ `soat.jpg`.
8. Giao: đường dẫn, độ dài, bảng lời → cảnh / đồ hoạ, mục còn đoán (D4–D6). Dọn: `run.py don --work <dir>` (xoá `footage\`, ~1 GB).

## Bẫy đã gặp (trang dựng HTML)

- Lớp JS bật / tắt thì CSS **không** được `display:none` (JS `show(el, true)` chỉ xoá style inline → vẫn ẩn). `mk(..., 'dh')` tự ẩn bằng style inline.
- Đo chữ (`Range.getBoundingClientRect`) khi phần tử / cha đang `display:none` → 0 → không co chữ. `__ready` bật tạm từng đồ hoạ lúc `init`.
- `background-clip: text` (chữ gradient) trên khối cha + span con có `transform` / `filter` → chữ con TRONG SUỐT (mất chữ). Gradient đặt trên từng span.
- Phần tử đặt `left/top` phải có `position:absolute` (lớp `.tay` không có sẵn) — thiếu là nhảy về góc trái trên.
- Chữ gradient (`.kem_grad`, `.vang_grad`, `.chu_drop`) chỉ được tô TRONG hộp phần tử: dấu tiếng Việt cao hơn line-height (Ể, Ấ, Ữ…) thành trong suốt
  → MẤT DẤU. CSS đã nới padding .26em trên / .16em dưới + margin âm; đổi line-height / phông thì soi lại chữ có dấu ở khung thật.
- Màn kết: cột chữ ≤ 760–780 px vì thẻ ảnh bên phải bắt đầu ở x ≈ 975.
- Ô ghép (`ghep`) không dùng chuyển cảnh chung: cảnh trước nằm DƯỚI, các ô trượt phủ dần (`luc_o`), nền tối giữa khe chỉ hiện khi ô cuối đã vào.
- Clip điện thoại có tay / điện thoại / ngón tay che (vd "Ngắm tàu sắt", "lễ hội drone") → soi tờ khung, bỏ nếu không có đoạn sạch.
- faster-whisper GPU cần `cublas64_12.dll` (CUDA 12) — thiếu thì tự lùi CPU int8.
- `.mask` (mặt nạ chữ trượt lên) đặt đệm bằng `em` thì `em` là cỡ chữ của CHÍNH mặt nạ (~16 px), không phải chữ to bên trong → đệm 5 px
  cắt mất dấu nặng / dấu hỏi ("VINH HA LONG", "CẢM ƠN BAN"). `__ready` tự đặt đệm theo cỡ chữ thật của con (`.26em` trên / `.36em` dưới).
- Barlow Condensed gốc đặt dấu nặng rất sâu (đáy −0,274 em) → chấm lạc xa chữ, sát dòng dưới. Font trong `assets/fonts` ĐÃ SỬA bằng
  `scripts/sua_font.py` (OFL không có Reserved Font Name → được sửa). Tải lại / thay font thì chạy lại script. Soi dấu nặng: tô đỏ chữ
  (`style.color='red'`) để phân biệt dấu của chữ với chấm khác trên hình — đừng đoán từ ảnh phóng nhỏ.
- Từ khoá ≥ 3 mục trên 1 hàng dài đè người → tự xếp cột; vẫn soi khung có người và dời `vi_tri` / `y` khỏi MẶT.
- Thẻ bản đồ cố định bề rộng thì "(314 km)" tràn → thẻ `width: max-content` (520–780 px).

## Tệp

- `scripts/run.py` (lệnh) · `quet.py` (Whisper, quét Resources, tờ khung, gợi ý, nháp) · `ke_hoach.py` (kiểm + giải giờ cảnh / chuyển /
  đồ hoạ / sub / SFX) · `dung.py` (trích khung theo bố cục, trang dựng, duyệt, dựng, trộn) · `render.mjs` (Chrome headless qua DevTools,
  chia luồng) · `am_thanh.py` (trộn giọng / nhạc / SFX, −14 LUFS, AAC) · `kiem.py` (tự kiểm file cuối) · `chung.py` (hằng số, tiện ích) ·
  `cai_dat.py` (kiểm máy) · `tao_sfx.py` (tự tổng hợp `boom.wav` cho cú drop) · `ban_do_that.py` (tìm toạ độ `run.py tim`, tuyến
  OSRM, camera + ô vệ tinh Esri cho bản đồ A → B; cache `_cache_tiles\esri`) · `nhip.py` (BPM, phách mạnh, đoạn cao trào của nhạc cho
  teaser) · `binh_luan.py` (bình luận ảo en / ko theo loại cảnh, chọn tất định) · `sua_font.py` (nâng dấu nặng Barlow Condensed).
- `assets/khung/ngang.css|js` (trang dựng) · `assets/khung/vn_ban_do.js` (đường viền VN Natural Earth 1:50m + Hoàng Sa, Trường Sa) ·
  `assets/binh_luan.json` (kho câu khen / chê en + ko theo loại cảnh, tên người tự đặt, cờ, tên địa danh theo tiếng) ·
  `assets/fonts` (OFL; Barlow Condensed đã sửa dấu nặng) · `assets/sfx` (xem `CREDITS.md`) · `assets/tu_ghep_vi.txt`.
