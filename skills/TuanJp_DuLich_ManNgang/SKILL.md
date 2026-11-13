---
name: TuanJp_DuLich_ManNgang
description: Dựng VIDEO GIỚI THIỆU / TRẢI NGHIỆM DU LỊCH Việt Nam khổ NGANG 16:9 (1920×1080, 30 fps) để ĐĂNG YOUTUBE, từ 2 đầu vào — 1 FILE AUDIO giọng đọc kịch bản + 1 THƯ MỤC RESOURCES clip / ảnh (ngang hay dọc đều được) — theo phong cách điện ảnh tự thiết kế cho khổ ngang: footage chỉnh màu ấm + hạt phim + tối mép, Ken Burns mỗi cảnh, KHUNG ĐIỆN ẢNH 2.35:1 mở màn; clip / ảnh DỌC không phóng vỡ mà thành THẺ BO GÓC trên nền nhoè của chính nó hoặc GHÉP 2–4 Ô cao trọn khung trượt vào so le đúng giây đọc tên (có nhãn serif + viết tay), ảnh nhỏ thành THẺ ẢNH viền kem; 1 ảnh to cắt nhiều VÙNG cho nhiều cảnh; 9 kiểu chuyển (hoà tan, nhoè, lia nhoè chuyển động, lia dọc, zoom xuyên, loé nắng, đẩy ngang, MÀN SÁNG QUÉT CHÉO mở chương, cắt); 10 kiểu ĐỒ HOẠ CHỮ (mở đầu tên lớn từng chữ hiện + viết tay vàng, CHƯƠNG 01/02… số viền vàng tô dần + tên + THẺ BẢN ĐỒ VIỆT NAM góc màn hình có ghim toả sóng và đủ Hoàng Sa / Trường Sa, thẻ địa danh góc dưới, từ khoá bật theo lời, tiêu đề đoạn vàng 2 dòng cân, chip, bảng liệt kê kính tối tick vàng đặt cạnh thẻ dọc, số lớn đếm lên, trích dẫn, bản đồ VN ghim rơi); SUB KARAOKE 1 dòng (dài thì 2) đáy khung, không tách từ ghép / tên riêng, chữ đang đọc vàng; MÀN KẾT YOUTUBE ≥ 5 s: avatar vòng xoay + tên kênh, CÂU HỎI BÌNH LUẬN + lựa chọn đánh số, nút ĐĂNG KÝ bóng quét → BÀN TAY bấm → ĐÃ ĐĂNG KÝ + chuông lắc → tay bấm THÍCH tô xanh + tim bay; SFX theo sự kiện, nhạc nền CHỈ khi Resources có file nhạc (−14 dB dưới giọng, né lời), −14 LUFS. Whisper nhận lời → Claude viết ke_hoach.json theo NGHĨA (soi từng tờ khung clip) → kiểm → ảnh duyệt → Chrome headless dựng (mã hoá 1 lần) → tự kiểm trên file cuối. Trigger '/TuanJp_DuLich_ManNgang', 'video du lịch màn ngang', 'video du lịch YouTube 16:9 từ audio + resources', 'giới thiệu du lịch Việt Nam khổ ngang', 'ráp audio kịch bản với thư mục resources thành video du lịch ngang'.
---

# TuanJp_DuLich_ManNgang — video du lịch NGANG 16:9 cho YouTube

Đầu vào: **1 file giọng đọc kịch bản** + **thư mục Resources** (clip / ảnh, ngang hoặc dọc; file nhạc nền nếu có).
Đầu ra: `<audio>_DLN.mp4` 1920×1080 30 fps, −14 LUFS, có sub karaoke, đồ hoạ chữ theo lời, màn kết YouTube.

Skill dọc `TuấnJp_Dulich_ManDoc` chỉ là THAM KHẢO (người dùng 13/11/2026: "cái này là skill màn ngang, skill kia bạn tham khảo
thôi"). Skill này đứng riêng: code, phông, SFX, khung trang dựng đều nằm trong thư mục skill.

- Khuôn kế hoạch: **`references/ke_hoach_schema.md`** (mọi trường, mọi bố cục, mọi đồ hoạ).
- Bản điền chuẩn (lần chạy thật đầu, 4 điểm đến, 115 s): **`references/vi-du-4-diem-den.json`** — ĐỌC TRƯỚC khi viết kế hoạch mới.
- Số phong cách: `scripts/chung.py` (khổ, vùng an toàn, sub, bố cục, chuyển cảnh, SFX, nhạc, chữ màn kết theo ngôn ngữ) +
  `assets/khung/ngang.css|js` (màu, phông, chuyển động). Bản đồ VN: `assets/khung/vn_ban_do.js`.

## TRẠNG THÁI / VIỆC TIẾP THEO (đọc trước khi train tiếp)

- **13/11/2026 — người dùng: "trước mắt oki rồi đó"** với `Audio_DLN_ban3.mp4` (hook 4 cảnh mượt + cú drop VIỆT NAM, cảnh ≥ 2,5 s, SFX thưa,
  nhạc `Music_Bg.mp3`). Đang CHỜ khách góp ý → mỗi góp ý: plan → người dùng duyệt → sửa SKILL.md / code → hỏi → dựng lại; ghi vào bảng bên dưới.
- Kế hoạch đã duyệt của video này: `references/vi-du-4-diem-den.json` (mã tài nguyên theo thứ tự tên file trong `Tuấn_Jp_Skill2\Resources`).
  Thư mục `<audio>_dln_work` có thể đã bị dọn → chạy lại `quet` (Whisper lại ~7 phút CPU), chép file mẫu này vào `ke_hoach.json`, `kiem-kh`, `dung`.
- Còn mở (chưa ai yêu cầu, đừng tự đổi): D1 tên kênh / avatar màn kết đang TRỐNG (người dùng chọn để trống); nền nhoè sau thẻ clip dọc ở
  thân video vẫn giữ (đề xuất đổi nền tối sắc nét nếu khách chê "mờ"); bảng liệt kê hiện khung trống ~0,7 s trước mục đầu (vd 19,8 → 21,0 s).
- Chưa có: đóng gói zip gửi khách (`dong-goi` như bản dọc), hành trình A → B trên bản đồ thật (bản dọc có `hanh_trinh`) — kịch bản này không cần.

## Skill này được bồi thêm sau mỗi lần chạy thật

| Ngày | Video | Học được / sửa |
|---|---|---|
| 13/11/2026 | `Tuấn_Jp_Skill2\Audio.mp3` (113 s: hook 4 câu → "Việt Nam" → Sa Pa → Hạ Long → Ninh Bình → thác Bản Giốc → tổng kết 4 điểm → câu hỏi khán giả) + Resources 16 clip (12 DỌC 720×1280, 4 ngang 1280×720) + 8 ảnh (3 ảnh ≥ 2000 px, 5 ảnh 600–1024 px), không nhạc | Bản đầu. **Clip dọc chiếm đa số** → khổ ngang không được phóng tràn (720 → 1920 = 2,7× vỡ): bố cục `the_doc` (thẻ 506×900 + nền nhoè chính nó) và `ghep` (2–4 ô). **Tư liệu ít** (Bản Giốc chỉ 1 clip 15 s + 1 ảnh cho ~25 s lời) → `vung` cắt 1 ảnh to thành nhiều khung khác nhau (toàn cảnh / tầng thác trên / cận thác dưới / rừng). Lỗi bắt khi soi: CSS `.dh {display:none}` làm MỌI đồ hoạ không hiện (JS `show()` chỉ xoá style inline) → ẩn bằng JS; đo chữ lúc phần tử đang `display:none` ra bề rộng 0 → bật tạm khi `init`; chữ có gradient `background-clip:text` mà từng ký tự con có `transform` thì MẤT CHỮ → gradient đặt trên từng ký tự; dòng viết tay màn kết thiếu `position:absolute` nhảy lên góc trái; câu hỏi màn kết rộng 1060 đè thẻ ảnh bên phải → cột chữ ≤ 760; chữ "Hùng vĩ" đè người trên xích đu → thêm `y` cho khối chữ. Whisper sai 19 chữ (Phan Xipan, Tháp Bản Dốc, cắp treo, trốn bồng lai viên cảnh, Hạ Long trên cạm…) → `sua_loi`. GPU không dùng được (thiếu cublas64_12.dll) → Whisper CPU 7 phút. Kết quả `Audio_DLN.mp4` 114,97 s: tự kiểm ĐẠT 9/9 (−14,0 LUFS, đỉnh −1,8 dBTP, không khung đen, chữ không đè); dựng ~3 phút (4 luồng × ~6 khung/s); file 479 MB (CRF 17 + hạt phim — YouTube nhận tốt). Bỏ 4 tài nguyên: tàu sắt Hà Nội + 2 clip drone đêm (không có trong lời, tay / điện thoại che), ảnh cáp treo trên BIỂN |
| 13/11/2026 | cùng video — người dùng: **"ở đoạn đầu video tôi thấy chưa edit hay"**, **"ý là đoạn đầu edit video chưa oki"** → duyệt plan | Soi 0–16 s: mở bằng 0,6 s màn đen; 3/4 cú chuyển trong hook NHOÈ (lia nhoè chuyển động 3,0 s / 7,2 s, zoom nhoè 4,9 s — hình nát ~0,45 s mỗi cú, trùng góp ý cũ "hiệu ứng mờ khó chịu, làm video mờ hẳn đi"); hook 10,6 s chỉ 4 cảnh (3 ảnh tĩnh đứng 2–3 s) → như trình chiếu; cảnh 3,6–4,8 s là thẻ dọc nhỏ trên nền xám nhoè; hook không có chữ; "VIỆT NAM" hiện từng chữ + viết tay quét ≈ 2 s mới đọc trọn, nền là 3 clip điện thoại tầm thường. Sửa → **LUẬT HOOK** (mục 12): vào thẳng hình khung 0; mỗi vế 1–2 cảnh 0,8–1,7 s, cắt `phong` (đập vào 1,22 → 1 + loé nhẹ + whoosh) đúng nhịp; mọi cảnh PHỦ KÍN khung (clip dọc → `ghep`); mỗi vế 1 `hook_tu` (KHỐI CHỮ Anton + nhãn địa danh có ghim) hiện ngay khung cắt; khung 0 có câu hỏi serif đủ chữ ngay; tên chủ đề = **CÚ DROP** (dồn riser 1,85 s → nổ trầm `boom.wav` tự tổng hợp + loé trắng 0,9 + rung 0,4 s + khung điện ảnh bung 0,32 s; chữ đập vào trọn trong 0,32 s, vệt sáng vàng quét); nền drop = ảnh ĐẸP NHẤT toàn cảnh (lộ rộng của chính ảnh cận mở đầu). **Bỏ NHOÈ ở MỌI chuyển cảnh + chữ** (lia = đẩy nhanh sắc nét, zoom = phóng vụt → loé → thu, nhoe = hoà tan sáng bừng); chữ chương / tiêu đề / địa danh đọc được ≤ 0,45 s. Lỗi bắt khi soi: chữ GRADIENT (`background-clip:text`) mất DẤU tiếng Việt ("BIEN MAY") vì dấu nằm ngoài hộp line-height 1 → nới padding .26em / bù margin âm. **SFX nghe rõ**: bộ trộn đo giọng TẠI CHỖ (±1,5 s) và tự tính gain cho từng tiếng tới mức `SFX_TREN` (hook +5…+7 dB, chuyển cảnh +3, pop 0) — báo trong `tron_bao_cao.json` + tự kiểm (lỗi khi chạy: số numpy float32 không ghi được JSON → ép `float`). Kết quả `Audio_DLN_ban2.mp4`: tự kiểm ĐẠT 10/10, SFX nghe rõ 56/56, −14,0 LUFS, đỉnh −1,6 dBTP |
| 13/11/2026 | cùng video, vòng 3 — người dùng: "cảnh đầu oki rồi, nhưng hiệu ứng chuyển chưa xịn, **1-2 giây lại hiển thị cái ảnh**, chuyển hình xong có sfx, **chưa kịp nhìn**, chuyển nhanh quá"; thêm `Resources\Music_Bg.mp3` (125,7 s): "hết nhạc mà video còn thì LOOP, Resources không có nhạc thì làm không có, có thì làm có — lưu vào skill" | Hook 8 cú cắt / 10,6 s (1,0–1,6 s mỗi cảnh) + whoosh mỗi cú = quá gấp → **mỗi vế câu 1 cảnh** (4 cảnh 2,0–3,5 s), chữ khoá đổi trên cùng cảnh; chuyển MƯỢT 0,6–0,8 s: kiểu mới `zoom_muot` (cũ đẩy vào 1 → 1,18, mới thu 1,12 → 1 chồng lên), `lia` thành trượt có chiều sâu (cũ lùi + tối, mới phủ lên), `truot` đẩy êm, `loe` 0,8 s; `phong` / `zoom` gấp chỉ dùng khi cố ý. **Luật thời lượng cảnh**: ≥ 2,5 s (`CANH_MIN`), montage thẻ dọc cùng chỗ ≥ 2,0, hook ≥ 1,8; < 1,5 s ⛔. Thân video gộp 5 chỗ < 2,5 s (đỉnh Fansipan + cờ, du thuyền + boong tàu, giãn Ninh Bình / Bản Giốc). **SFX THƯA**: cú chuyển thường KHÔNG tiếng; chữ hiện KHÔNG tiếng; chỉ còn cú drop (riser + boom + lấp lánh), whoosh màn quét mở chương, ding số chương, pop NHỎ (−4 dB dưới giọng) ở chip / liệt kê, nút màn kết. Nhạc nền: luật mục 9 (loop khi ngắn). Thư mục `_dln_work` bị dọn giữa chừng → kế hoạch lấy lại từ `references/vi-du-4-diem-den.json`, chạy lại Whisper. Chữ hook hiện khi cảnh cũ còn trên hình → `kiem-kh` tự dời chữ `hook_tu` tới lúc cảnh vào xong. Kết quả `Audio_DLN_ban3.mp4`: tự kiểm ĐẠT 11/11 — nhạc −14,1 dB dưới giọng (bỏ 9,9 s đầu bài cho nốt kết trùng cuối), SFX 26 tiếng (trước 68) đều nghe rõ, −14,0 LUFS, đỉnh −1,6 dBTP |

## CÁC DIALOG SKILL PHẢI HỎI (cổng duyệt — dừng 1 lần, LẦN NÀO GỌI SKILL CŨNG HỎI LẠI, có đề xuất sẵn)

| # | Hỏi | Đề xuất mặc định | Bắt buộc trả lời |
|---|---|---|---|
| D1 | Kênh cho màn kết: tên kênh, @handle, file avatar | trống → avatar la bàn, không tên (KHÔNG tự bịa tên kênh) | có |
| D2 | Nhạc nền — CHỈ hỏi khi Resources có file nhạc: báo file đã ghép (tên, độ dài, lặp mấy lần / lùi bao nhiêu giây) — giữ / đổi / tắt | giữ | khi có nhạc |
| D3 | Màn kết: câu hỏi bình luận + lựa chọn (lấy từ câu cuối của lời) hoặc tiêu đề + viết tay — giữ hay đổi | câu hỏi trong lời | không |
| D4 | Phần lời KHÔNG có tư liệu khớp → đang dùng cảnh mượn / cắt vùng ảnh nào (liệt kê theo giây) — bổ sung clip hay giữ | giữ | không |
| D5 | Chữ đã sửa lỗi nhận giọng (bảng `sua_loi`) + chỗ còn đoán | — | không |
| D6 | Tài nguyên KHÔNG dùng và lý do (vd ảnh cáp treo trên BIỂN không khớp lời cáp treo Fansipan; clip có tay / điện thoại che kín) | — | không |

Không phải hỏi (đã chốt bên dưới): khổ, fps, phong cách chữ, vị trí sub, mức nhạc, −14 LUFS.

## ĐÃ CHỐT (không tự đổi trừ khi người dùng yêu cầu)

1. **Khổ NGANG 1920×1080, 30 fps** — YouTube. Hết hình = max(tiếng cuối + 0,8 s, đầu màn kết + 5 s). Vùng chữ title-safe x 96–1824, y 54–1026.
2. **Clip / ảnh DỌC không bao giờ phóng tràn khung ngang** (`kiem-kh` ⚠). Dùng `the_doc` (thẻ giữa / trái / phải, chữ đồ hoạ đặt bên trống) hoặc
   `ghep` (2–4 ô). Đoạn LIỆT KÊ nhiều nơi / nhiều thứ có tư liệu từng mục → `ghep` với `luc_o` = giây đọc từng tên + `nhan` từng ô.
   Ảnh < 1500 px ngang → `the_anh`. Ảnh / clip ngang ≥ 1280 → `tran`.
3. **Footage**: chỉnh màu 1 lần lúc trích (tương phản 1,06, bão hoà 1,16, ấm vùng sáng, làm nét nhẹ) + lớp màu ấm soft-light + tối mép +
   dải tối đáy (cho sub) + hạt phim; mỗi cảnh Ken Burns (ảnh mạnh 7,5 %, clip nhẹ). Video vào THẲNG hình ở khung 0 (không mở từ đen — khung
   đầu là ảnh xem trước YouTube); KHUNG ĐIỆN ẢNH 2.35:1 từ đầu tới cú drop `mo_dau` thì bung ra 0,32 s (sub nằm trên dải đen) — `dien_anh: false` để tắt.
4. **KHÔNG NHOÈ** (người dùng ghét: "hiệu ứng mờ khó chịu, làm video mờ hẳn đi"): không chuyển cảnh nhoè / zoom-blur / lia nhoè chuyển động,
   chữ không nhoè vào / ra. Lực chuyển cảnh = đổi khung phóng, loé trắng, đẩy sắc nét, whoosh. (Nền nhoè sau thẻ clip dọc ở THÂN video vẫn giữ —
   người dùng chưa chê; chê thì đổi nền tối sắc nét.)
   **MƯỢT, KHÔNG GẤP** (người dùng: "1-2 giây lại hiển thị cái ảnh… chưa kịp nhìn… chuyển nhanh quá"): mỗi cảnh đứng **≥ 2,5 s** (`CANH_MIN`;
   montage thẻ dọc cùng chỗ chỉ đổi hình ≥ 2,0; hook ≥ 1,8 theo vế câu; `kiem-kh` ⚠ dưới ngưỡng, ⛔ < 1,5 s) — thiếu thì GỘP với cảnh kề,
   đừng cắt vụn; chuyển 0,6–0,8 s, mặc định `zoom_muot` / `lia` (trượt có chiều sâu) / `loe` / `hoa_tan`; `phong`, `zoom` (gấp, có loé) chỉ khi cố ý.
   **Chuyển cảnh** theo `CHUYEN` trong `chung.py`; đổi kiểu liên tục; `man` (màn sáng quét chéo) để MỞ CHƯƠNG / điểm đến mới; `nhoe` (hoà tan sáng bừng) ngày → đêm;
   `lia` / `truot` cùng mạch; `zoom` khi đi sâu vào cùng 1 cảnh (vd ảnh toàn cảnh → vùng cận); thẻ dọc nối thẻ dọc cùng chỗ thì `hoa_tan` (thẻ đứng yên, hình đổi).
5. **Phông / màu**: Playfair Display 900 (chữ khoá) · Dancing Script 700 (viết tay vàng `#F4C66A`) · Be Vietnam Pro (sub, nhãn) · Montserrat
   (chữ in giãn) · Anton (số). Gradient kem / vàng, đỏ nút `#FF2A4D`. Chữ khoá dài tự ngắt 2 dòng cân rồi mới co.
6. **Đồ hoạ**: CHỮ HIỆN NGAY — khối chữ chính đọc được ≤ 0,4 s sau khi vào (không chạy từng chữ, không chờ mốc nói muộn); mỗi lúc 1 đồ hoạ lớn (`dia_danh`, `chip` được chồng); mỗi mục chữ ≥ 1,6 s (được hiện SỚM hơn lời — `kiem-kh` tự sửa 🔧);
   không quá 10–12 s không có chữ đồ hoạ; chữ đồ hoạ là chữ ĐẮT của lời (1–6 chữ), không bịa số. Mỗi điểm đến lớn = 1 `chuong` (số
   01/02…, `toa_do` → thẻ bản đồ VN góc). **Bản đồ Việt Nam trên hình LUÔN có quần đảo Hoàng Sa, Trường Sa** (đã nằm trong `vn_ban_do.js`).
7. **Sub karaoke**: Be Vietnam Pro 700 50 px trắng viền tối, đáy 990, ưu tiên 1 dòng ≤ 46 ký tự (dài thì 2 dòng), chữ đang đọc vàng `#FFC845`
   phồng nhẹ; không tách từ ghép (`assets/tu_ghep_vi.txt`, `sub.giu_lien`, tên trong `sua_loi`) hay tên riêng; tắt trong màn kết.
8. **Màn kết YouTube ≥ 5 s** (chỗ gắn End screen): cột trái ≤ 780 px (avatar, tên kênh, câu hỏi bình luận + lựa chọn / tiêu đề, viết tay,
   nút ĐĂNG KÝ → tay bấm `cta.tu + 1,9 s` → ĐÃ ĐĂNG KÝ + chuông → tay bấm Thích `+1,25 s`), cảnh dưới là thẻ ảnh / thẻ dọc bên phải.
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
     `lia`), KHÔNG whoosh mỗi cú; MỌI cảnh phủ kín khung — clip dọc thì `ghep` 2–3 ô (KHÔNG `the_doc`); ảnh to cắt `vung` đẹp nhất;
   - mỗi vế 1 `hook_tu`: chữ đắt nhất của vế (BIỂN MÂY / ĐẢO ĐÁ VÔI…) + `nhan` = địa danh, `tu` = khung cắt, `den` = khung cắt sau − 0,03;
   - tên chủ đề (`mo_dau`, mặc định `drop: true`) = CÚ DROP: cảnh `cat` sang ảnh đẹp nhất toàn cảnh, tự có riser trước 1,85 s + boom + loé + rung,
     chữ đập vào trọn trong 0,32 s; dòng viết tay / dòng điểm đến hiện ngay sau 0,2–0,35 s;
   - chữ `hook_tu` hiện SAU khi cảnh của nó đã vào xong (`kiem-kh` tự dời 🔧 tới `tu` cảnh + nửa thời lượng chuyển; ô ghép: ô cuối + 0,45 s) —
     không bao giờ hiện chữ vế mới trên hình của vế cũ;
   - không tách thành thẻ nhỏ, không nhoè, không cắt vụn (< 1,8 s), không SFX mỗi cú chuyển.

## Khuôn kể chuyện du lịch → bố cục + đồ hoạ (áp cho MỌI kịch bản)

| Kiểu câu | Cảnh | Đồ hoạ |
|---|---|---|
| Hook mở (câu hỏi "bạn đã bao giờ…", 2–4 vế) | LUẬT HOOK (mục 12): mỗi vế ĐÚNG 1 cảnh (≥ 1,8 s) phủ kín khung, chuyển mượt `loe` / `zoom_muot` / `lia`; clip dọc → `ghep` | `hook_tu` mỗi vế (chữ khoá + địa danh); khung 0: `hook_tu` `kieu: "cau"` (đổi chữ trên cùng cảnh được) |
| Gọi tên chủ đề ("vẻ đẹp của Việt Nam") | CÚ DROP: `cat` sang ảnh / clip ĐẸP NHẤT toàn cảnh (không ghép clip điện thoại tầm thường) | `mo_dau` `drop` (tren / TÊN / viết tay / dòng liệt kê điểm đến) |
| Mở 1 điểm đến ("hành trình đầu tiên… Sa Pa") | clip ngang toàn cảnh / đường tới, `chuyen: "man"` | `chuong` + `toa_do` |
| Kể 2–4 đặc điểm của điểm đó | `the_doc` cùng 1 bên, đổi hình đúng giây từng đặc điểm (`hoa_tan`) | `liet_ke` bên kia (tick đúng giây đọc) |
| Tên 1 điểm cụ thể (đỉnh, hang, bến…) | tư liệu khớp tên | `dia_danh` góc dưới |
| Trải nghiệm ("ngồi trên du thuyền…") | ảnh / clip đúng trải nghiệm (`the_anh` / `the_doc`) | `chip` hàng trên |
| Cảm nhận ("bồng lai tiên cảnh", "hùng vĩ & yên bình") | cảnh chậm, `ghep` 2 ô hoặc tràn | `tu_khoa` (serif + tay), `y` né người |
| Câu chốt của 1 điểm ("ít nhất một lần trong đời") | toàn cảnh đẹp nhất, `zoom_ra` | `tieu_de` |
| Tổng kết N điểm ("Sa Pa thơ mộng, Hạ Long kỳ vĩ…") | `ghep` N ô, `luc_o` = giây đọc từng tên, `nhan` = tên + tính từ | `tieu_de` trước đó ("Bốn điểm đến") |
| Câu kết ý nghĩa | clip người / hành trình | `tieu_de` rồi `tu_khoa` (động từ đắt) |
| Câu hỏi / kêu gọi cuối | `the_anh` / `the_doc` `vi_tri: "phai"` | màn kết: `cau_hoi` + `lua_chon` từ lời |

Chọn footage: tên riêng → tư liệu khớp tên (`goi_y.txt`) đúng giây; soi `khung/clip_NN.jpg` để chọn `vao` (tránh tay / điện thoại che,
rung, nghiêng); không lặp cùng đoạn clip (cùng clip khác đoạn được); thiếu tư liệu → cắt `vung` khác nhau của ảnh to, mượn cảnh cùng kiểu
địa hình (báo ở D4); tài nguyên SAI NGHĨA thì bỏ (báo ở D6) — vd ảnh cáp treo trên biển không dùng cho câu cáp treo Fansipan.

## Quy trình

Mọi lệnh: `python -I -X utf8 .claude\skills\TuanJp_DuLich_ManNgang\scripts\run.py <lệnh> …` (từ thư mục dự án; PowerShell: đầu phiên
`[Console]::OutputEncoding=[Text.Encoding]::UTF8; $env:PYTHONUTF8='1'`). Cần Python ≥ 3.10 + `requirements.txt`, ffmpeg full, Node ≥ 22,
Chrome / Edge (`DLN_CHROME` nếu nằm chỗ lạ). Máy mới: `run.py cai-dat`.

1. **Quét**: `run.py quet --audio "<giọng>" --res "<Resources>" [--nhac "<nhạc>"] [--ngon-ngu vi]` → `<audio>_dln_work\`: `loi.json`,
   `loi_doc.txt` (lời + giây từng từ), `tai_nguyen.json` + `tai_nguyen.jpg` (mọi tài nguyên + mã + DỌC/NGANG), `khung\clip_NN.jpg` (tờ khung
   có nhãn giây), `goi_y.txt` (tên file ↔ lời), `ke_hoach.json` NHÁP (`CAN_CLAUDE_SUA: true`). Quét lại giữ mã cũ, file mới nhận số kế tiếp,
   kế hoạch đã sửa giữ nguyên. Whisper lần đầu tải ~3 GB; CPU ~4 phút / phút audio — chạy nền, đừng huỷ.
2. **Claude viết kế hoạch theo NGHĨA**: đọc `goi_y.txt`, `loi_doc.txt`; MỞ `tai_nguyen.jpg` + MỌI `khung\clip_NN.jpg`; gán mỗi câu 1 kiểu
   (bảng trên); viết `canh` / `do_hoa` / `cta` / `sua_loi` (mẫu `references/vi-du-4-diem-den.json`, khuôn `references/ke_hoach_schema.md`);
   đặt `CAN_CLAUDE_SUA: false`.
3. `run.py kiem-kh --work <dir>` → hết ⛔ (⚠ cân nhắc; 🔧 = đã tự sửa giờ cho kịp nhìn).
4. `run.py duyet --work <dir>` → `duyet.jpg` (khung giữa mỗi cảnh / đồ hoạ / màn kết) + `bang_duyet.txt`. MỞ `duyet.jpg` soi như dân mỹ
   thuật: chữ mất / đè người / đè thẻ / quá nhỏ, thẻ sai bên, ảnh sai nghĩa, logo dán. Soi gần: `run.py khung --work <dir> --times 12.3,45.6`
   (→ `khung_le.jpg`; nên soi cả giây giữa chuyển cảnh).
5. **CỔNG DUYỆT** — gửi `duyet.jpg` + bảng tóm tắt, hỏi D1–D6.
6. `run.py dung --work <dir> [--luong 4]` (~115 s video ≈ 6–8 phút, chạy nền) → `<audio>_DLN.mp4`, tự chạy `kiem`.
   Thử nhanh: `--xem-truoc` (20 s đầu). Chỉ đổi TIẾNG: `run.py tron-lai --work <dir>`.
7. `run.py kiem` phải **ĐẠT**: 1920×1080 · 30 fps · không cắt giọng · có tiếng · −14 LUFS ±1 · đỉnh ≤ −1 dBTP · nhạc −24…−9 dB (khi có) ·
   không khung đen giữa video · sub không đè chữ đồ hoạ / chữ không tràn mép (chụp hộp chữ mỗi 0,5 s) · có màn kết. MỞ `soat.jpg`.
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

## Tệp

- `scripts/run.py` (lệnh) · `quet.py` (Whisper, quét Resources, tờ khung, gợi ý, nháp) · `ke_hoach.py` (kiểm + giải giờ cảnh / chuyển /
  đồ hoạ / sub / SFX) · `dung.py` (trích khung theo bố cục, trang dựng, duyệt, dựng, trộn) · `render.mjs` (Chrome headless qua DevTools,
  chia luồng) · `am_thanh.py` (trộn giọng / nhạc / SFX, −14 LUFS, AAC) · `kiem.py` (tự kiểm file cuối) · `chung.py` (hằng số, tiện ích) ·
  `cai_dat.py` (kiểm máy) · `tao_sfx.py` (tự tổng hợp `boom.wav` cho cú drop).
- `assets/khung/ngang.css|js` (trang dựng) · `assets/khung/vn_ban_do.js` (đường viền VN Natural Earth 1:50m + Hoàng Sa, Trường Sa) ·
  `assets/fonts` (OFL) · `assets/sfx` (xem `CREDITS.md`) · `assets/tu_ghep_vi.txt`.
