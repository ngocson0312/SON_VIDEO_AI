---
name: TuanJp_DuLich_ManNgang
description: Dựng VIDEO GIỚI THIỆU / TRẢI NGHIỆM DU LỊCH Việt Nam khổ NGANG 16:9 (1920×1080, 30 fps) để ĐĂNG YOUTUBE, từ 2 đầu vào — 1 FILE AUDIO giọng đọc kịch bản + 1 THƯ MỤC RESOURCES clip / ảnh (ngang hay dọc đều được, nhạc nền để luôn trong Resources) — phong cách điện ảnh riêng cho khổ ngang (khách chốt 14/11/2026): ẢNH / CLIP LUÔN TRÀN MÀN (không chia ô, không thẻ dọc; clip dọc lấy dải 16:9 neo cao + làm nét bù), footage chỉnh màu ấm + hạt phim + tối mép, Ken Burns, KHUNG ĐIỆN ẢNH 2.35:1 tới cú drop; MONTAGE TỔNG HỢP ≤ 10 s đầu chỉ nhạc (tự dò BPM / phách, lấy đoạn CAO TRÀO của bài; cảnh hay nhất KHẮP video xếp trên lưới phách: BA CỘT bật theo phách → cột 3 bung → tên điểm đến đập (khung nhỏ bung to / hai nửa đổi vai / xoay / đập) → dồn nửa phách → DẢI ẢNH TRƯỢT các điểm đến → cảnh đỉnh phóng ra + tít + boom; giọng vào trước giây 10; 5 kỹ xảo mẫu người dùng gửi: ba cột, khung bung, dải trượt, cắt nối theo hình, hai nửa) rồi giọng hook + cú DROP tên chủ đề (cao trào tới drop giữ người xem: MỌI cú cắt là KỸ XẢO ĐIỆN ẢNH tự gán — vỡ kính, xoay zoom, glitch, khối 3D, cháy phim, xuyên cảnh, mở tròn, tia sáng — + đập theo phách + tách màu RGB, sau 30 s chuyển êm); mỗi điểm đến mở bằng BẢN ĐỒ VỆ TINH THẬT A → B kiểu GOOGLE MAPS (Esri + đường đi thật OSRM, camera cận điểm đi → toàn tuyến → sà điểm đến, tuyến xanh chạy + xe chạy theo tuyến, ghim đỏ rơi, thẻ trắng '≈ 4 giờ 15 phút (314 km)' đếm lên, bản đồ VN nhỏ góc có Hoàng Sa / Trường Sa), BÌNH LUẬN ẢO tiếng Anh + tiếng Hàn khen / chê nhẹ kiểu YouTube cho mỗi điểm đến / món ăn (tự đặt chỗ trống, tên giả, cờ, lượt thích, tim tác giả); bộ CHỮ RIÊNG khác màn dọc (Barlow Condensed IN HOA trắng + nhấn XANH NGỌC, Montserrat nghiêng, nhãn giãn chữ) — mở đầu, hook, chương, địa danh, từ khoá, tiêu đề, chip, số lớn, liệt kê, trích dẫn; SUB hộp tối bo góc 1 dòng, chữ đang đọc xanh ngọc, không tách từ ghép; MÀN KẾT CẢM ƠN: câu hỏi bình luận + lựa chọn → 'Cảm ơn bạn đã xem' → lời mời Thích & Đăng ký → tay bấm ĐĂNG KÝ + chuông + THÍCH tim bay; SFX thưa, nhạc nền CHỈ khi Resources có file nhạc (−14 dB dưới giọng, teaser to như giọng), −14 LUFS. Whisper nhận lời → Claude viết ke_hoach.json theo NGHĨA → kiểm → ảnh duyệt → Chrome headless dựng (mã hoá 1 lần) → tự kiểm trên file cuối. Trigger '/TuanJp_DuLich_ManNgang', 'video du lịch màn ngang', 'video du lịch YouTube 16:9 từ audio + resources', 'giới thiệu du lịch Việt Nam khổ ngang', 'ráp audio kịch bản với thư mục resources thành video du lịch ngang'.
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
- Bản giao 14/11/2026: `D:\____TTT_____\KH_Test\Tuấn_jp\Màn Ngang\Audio_DLN.mp4` (người dùng duyệt D1–D8 mặc định); người dùng chê
  "những cảnh đầu chưa xịn" → `Audio_DLN_ban2.mp4` (30 s đầu kỹ xảo, ĐÃ CHỐT 16); chê "tuần tự, chưa wao, chỉ 5–10 s" → `Audio_DLN_ban3.mp4`
  (montage tổng hợp 9,42 s, ĐÃ CHỐT 15) → `Audio_DLN_ban4.mp4` (+ 5 kỹ xảo mẫu, ĐÃ CHỐT 17); chê "nhịp loạn, không liên kết, chỉ hình
  đẩy, vào lời chưa có tiếng chốt" → `Audio_DLN_ban5.mp4` (= demo 4 làm lại: lưới phách bám trống thật, mọi nấc kỹ xảo đúng phách,
  cú đẩy có chữ + người tách nền, dồn = đẩy nhanh 1 hướng, vào giọng vỡ kính + boom — vòng 4); chê "chuyển cảnh nhanh quá, khó chịu" →
  **`Audio_DLN_ban6.mp4`** (người dùng đã đổi tên thành `demo2_ManNgang.mp4`; dồn mỗi cảnh 1 phách, đẩy 0,34 s êm — vòng 5) + LUẬT NHỊP
  CẮT cho cả video (ĐÃ CHỐT 18) + mục "CHUẨN XỊN" ở dưới — chờ người dùng xem. Người dùng hay đổi tên / dọn video cũ: `lan_dung.json` trỏ
  file không còn → `run.py kiem --work … --file "<file mới>"`.
- Còn mở: D1 tên kênh / avatar màn kết đang TRỐNG; clip DỌC 720 px tràn khung ngang phóng 2,7× (mềm — đã làm nét `cas`); khách gửi clip
  ngang / 4K thì nét hẳn. Chưa có: đóng gói zip gửi khách (`dong-goi` như bản dọc).

## CHUẨN XỊN — TÓM TẮT MỌI ĐIỀU KHÁCH ĐÃ DUYỆT (đọc TRƯỚC khi viết kế hoạch; áp cho MỌI video, MỌI chỗ trong video)

Gọi skill là ra video đạt các điều dưới đây — phần lớn script TỰ LÀM (✔ = tự động, ✍ = Claude phải chọn đúng khi viết kế hoạch).
Góp ý của khách có kèm giây ("giây 5, 6, 7…") chỉ là CHỖ HỌ THẤY lỗi → sửa thành LUẬT CHO CẢ VIDEO, không viết cứng theo giây.

**Nhịp & cắt**
- ✔ Lưới phách bám tiếng TRỐNG THẬT của bài (khớp cục bộ từng phách, lệch ~1 ms), đầu ô nhịp = cú DROP; mọi cú cắt / nấc kỹ xảo montage rơi
  đúng phách hoặc ½ phách (`CHUYEN_NHIP`). Nấc trong 1 kỹ xảo được ½ phách, nhưng ĐỔI CẢNH thì không.
- ✔ **KHÔNG CẮT DỒN DẬP Ở BẤT KỲ ĐÂU** (ĐÃ CHỐT 18): montage mỗi cảnh ≥ 1 phách và ≥ 0,55 s (nhạc nhanh tự lên 1,5 / 2 phách), thân video
  ≥ 1,5 s (nên ≥ 2,5 s), mỗi cảnh ĐỨNG YÊN RÕ ≥ 0,25 s giữa 2 cú chuyển; cú di chuyển cả khung (đẩy) ≥ 0,34 s chậm dần đều.
  `kiem-kh` ⛔ / tự sửa 🔧 `nhip` quá nhỏ, tự kiểm cuối có mục "nhịp cắt".
- ✔ Liền mạch: đoạn dồn chỉ 1 kiểu ĐẨY cùng 1 hướng (phải → trái) + Ken Burns trôi cùng hướng; không trộn chớp / đập / glitch liên tiếp.
- ✔ Teaser ≤ 10 s chỉ nhạc (đoạn cao trào của bài), giọng vào trước giây 10 bằng cao trào DUY NHẤT: VỠ KÍNH + riser + boom chốt.

**Kỹ xảo phải "có hồn"**
- ✔ 5 kỹ xảo mẫu khách gửi (ba cột, khung bung, dải trượt, khớp hình, hai nửa) tự gán trong montage / 30 s đầu; kết thúc LUÔN tràn màn.
- ✔✍ Cú ĐẨY không bao giờ chỉ là hình trơn: cảnh có `chu` / `nhan` → chữ chạy theo mép đẩy; cảnh CÓ NGƯỜI → người tách nền nhô qua mép.
  Claude chọn cho cú đẩy (`hai_nua`) 1 cảnh có người rõ (2–50 % khung) + chữ lấy TỪ LỜI.
- ✔ SFX theo nấc: mỗi nấc 1 tiếng nhẹ, nấc cuối 1 tiếng CHỐT; cú cắt thường sau 30 s không SFX.

**Chọn cảnh (✍)**
- Montage: 3 cột = 3 điểm đến khác nhau; cảnh dồn 3–4 cảnh, mỗi cảnh 1 điểm đến / trải nghiệm khác, màu sáng rõ, có người / hành động;
  tránh cảnh xám nhạt, đông người lộn xộn, mờ, rung. Thừa thì script tự bỏ cảnh dồn cuối cho cảnh đỉnh đủ 3 phách.
- Cảnh đỉnh = ảnh to nét đẹp nhất; tít đỉnh lấy từ lời ("4 điểm đến, 4 vẻ đẹp").
- Luôn tràn màn; clip dọc / ảnh nhỏ chỉ khi không có nguồn tốt hơn (⚠ mềm — báo ở cổng duyệt).

**Không bịa** — mọi chữ, số, tên trên hình lấy từ lời; số km / giờ bản đồ ghi "≈ ước tính" và hỏi D7.

**Tự kiểm trước khi giao** — tự kiểm ĐẠT hết; MỞ `soat.jpg` + cắt khung quanh MỌI cú cắt trong 10–30 s đầu (ffmpeg `-ss`) soi bằng mắt:
chữ không đè mặt, người nhô không thành 2 người, kỹ xảo không lộ khung đen, nhịp đều.

## Skill này được bồi thêm sau mỗi lần chạy thật

| Ngày | Video | Học được / sửa |
|---|---|---|
| 13/11/2026 | `Tuấn_Jp_Skill2\Audio.mp3` (113 s: hook 4 câu → "Việt Nam" → Sa Pa → Hạ Long → Ninh Bình → thác Bản Giốc → tổng kết 4 điểm → câu hỏi khán giả) + Resources 16 clip (12 DỌC 720×1280, 4 ngang 1280×720) + 8 ảnh (3 ảnh ≥ 2000 px, 5 ảnh 600–1024 px), không nhạc | Bản đầu. **Clip dọc chiếm đa số** → khổ ngang không được phóng tràn (720 → 1920 = 2,7× vỡ): bố cục `the_doc` (thẻ 506×900 + nền nhoè chính nó) và `ghep` (2–4 ô). **Tư liệu ít** (Bản Giốc chỉ 1 clip 15 s + 1 ảnh cho ~25 s lời) → `vung` cắt 1 ảnh to thành nhiều khung khác nhau (toàn cảnh / tầng thác trên / cận thác dưới / rừng). Lỗi bắt khi soi: CSS `.dh {display:none}` làm MỌI đồ hoạ không hiện (JS `show()` chỉ xoá style inline) → ẩn bằng JS; đo chữ lúc phần tử đang `display:none` ra bề rộng 0 → bật tạm khi `init`; chữ có gradient `background-clip:text` mà từng ký tự con có `transform` thì MẤT CHỮ → gradient đặt trên từng ký tự; dòng viết tay màn kết thiếu `position:absolute` nhảy lên góc trái; câu hỏi màn kết rộng 1060 đè thẻ ảnh bên phải → cột chữ ≤ 760; chữ "Hùng vĩ" đè người trên xích đu → thêm `y` cho khối chữ. Whisper sai 19 chữ (Phan Xipan, Tháp Bản Dốc, cắp treo, trốn bồng lai viên cảnh, Hạ Long trên cạm…) → `sua_loi`. GPU không dùng được (thiếu cublas64_12.dll) → Whisper CPU 7 phút. Kết quả `Audio_DLN.mp4` 114,97 s: tự kiểm ĐẠT 9/9 (−14,0 LUFS, đỉnh −1,8 dBTP, không khung đen, chữ không đè); dựng ~3 phút (4 luồng × ~6 khung/s); file 479 MB (CRF 17 + hạt phim — YouTube nhận tốt). Bỏ 4 tài nguyên: tàu sắt Hà Nội + 2 clip drone đêm (không có trong lời, tay / điện thoại che), ảnh cáp treo trên BIỂN |
| 13/11/2026 | cùng video — người dùng: **"ở đoạn đầu video tôi thấy chưa edit hay"**, **"ý là đoạn đầu edit video chưa oki"** → duyệt plan | Soi 0–16 s: mở bằng 0,6 s màn đen; 3/4 cú chuyển trong hook NHOÈ (lia nhoè chuyển động 3,0 s / 7,2 s, zoom nhoè 4,9 s — hình nát ~0,45 s mỗi cú, trùng góp ý cũ "hiệu ứng mờ khó chịu, làm video mờ hẳn đi"); hook 10,6 s chỉ 4 cảnh (3 ảnh tĩnh đứng 2–3 s) → như trình chiếu; cảnh 3,6–4,8 s là thẻ dọc nhỏ trên nền xám nhoè; hook không có chữ; "VIỆT NAM" hiện từng chữ + viết tay quét ≈ 2 s mới đọc trọn, nền là 3 clip điện thoại tầm thường. Sửa → **LUẬT HOOK** (mục 12): vào thẳng hình khung 0; mỗi vế 1–2 cảnh 0,8–1,7 s, cắt `phong` (đập vào 1,22 → 1 + loé nhẹ + whoosh) đúng nhịp; mọi cảnh PHỦ KÍN khung (clip dọc → `ghep`); mỗi vế 1 `hook_tu` (KHỐI CHỮ Anton + nhãn địa danh có ghim) hiện ngay khung cắt; khung 0 có câu hỏi serif đủ chữ ngay; tên chủ đề = **CÚ DROP** (dồn riser 1,85 s → nổ trầm `boom.wav` tự tổng hợp + loé trắng 0,9 + rung 0,4 s + khung điện ảnh bung 0,32 s; chữ đập vào trọn trong 0,32 s, vệt sáng vàng quét); nền drop = ảnh ĐẸP NHẤT toàn cảnh (lộ rộng của chính ảnh cận mở đầu). **Bỏ NHOÈ ở MỌI chuyển cảnh + chữ** (lia = đẩy nhanh sắc nét, zoom = phóng vụt → loé → thu, nhoe = hoà tan sáng bừng); chữ chương / tiêu đề / địa danh đọc được ≤ 0,45 s. Lỗi bắt khi soi: chữ GRADIENT (`background-clip:text`) mất DẤU tiếng Việt ("BIEN MAY") vì dấu nằm ngoài hộp line-height 1 → nới padding .26em / bù margin âm. **SFX nghe rõ**: bộ trộn đo giọng TẠI CHỖ (±1,5 s) và tự tính gain cho từng tiếng tới mức `SFX_TREN` (hook +5…+7 dB, chuyển cảnh +3, pop 0) — báo trong `tron_bao_cao.json` + tự kiểm (lỗi khi chạy: số numpy float32 không ghi được JSON → ép `float`). Kết quả `Audio_DLN_ban2.mp4`: tự kiểm ĐẠT 10/10, SFX nghe rõ 56/56, −14,0 LUFS, đỉnh −1,6 dBTP |
| 13/11/2026 | cùng video, vòng 3 — người dùng: "cảnh đầu oki rồi, nhưng hiệu ứng chuyển chưa xịn, **1-2 giây lại hiển thị cái ảnh**, chuyển hình xong có sfx, **chưa kịp nhìn**, chuyển nhanh quá"; thêm `Resources\Music_Bg.mp3` (125,7 s): "hết nhạc mà video còn thì LOOP, Resources không có nhạc thì làm không có, có thì làm có — lưu vào skill" | Hook 8 cú cắt / 10,6 s (1,0–1,6 s mỗi cảnh) + whoosh mỗi cú = quá gấp → **mỗi vế câu 1 cảnh** (4 cảnh 2,0–3,5 s), chữ khoá đổi trên cùng cảnh; chuyển MƯỢT 0,6–0,8 s: kiểu mới `zoom_muot` (cũ đẩy vào 1 → 1,18, mới thu 1,12 → 1 chồng lên), `lia` thành trượt có chiều sâu (cũ lùi + tối, mới phủ lên), `truot` đẩy êm, `loe` 0,8 s; `phong` / `zoom` gấp chỉ dùng khi cố ý. **Luật thời lượng cảnh**: ≥ 2,5 s (`CANH_MIN`), montage thẻ dọc cùng chỗ ≥ 2,0, hook ≥ 1,8; < 1,5 s ⛔. Thân video gộp 5 chỗ < 2,5 s (đỉnh Fansipan + cờ, du thuyền + boong tàu, giãn Ninh Bình / Bản Giốc). **SFX THƯA**: cú chuyển thường KHÔNG tiếng; chữ hiện KHÔNG tiếng; chỉ còn cú drop (riser + boom + lấp lánh), whoosh màn quét mở chương, ding số chương, pop NHỎ (−4 dB dưới giọng) ở chip / liệt kê, nút màn kết. Nhạc nền: luật mục 9 (loop khi ngắn). Thư mục `_dln_work` bị dọn giữa chừng → kế hoạch lấy lại từ `references/vi-du-4-diem-den.json`, chạy lại Whisper. Chữ hook hiện khi cảnh cũ còn trên hình → `kiem-kh` tự dời chữ `hook_tu` tới lúc cảnh vào xong. Kết quả `Audio_DLN_ban3.mp4`: tự kiểm ĐẠT 11/11 — nhạc −14,1 dB dưới giọng (bỏ 9,9 s đầu bài cho nốt kết trùng cuối), SFX 26 tiếng (trước 68) đều nghe rõ, −14,0 LUFS, đỉnh −1,6 dBTP |
| 14/11/2026 | `KH_Test\Tuấn_jp\Màn Ngang` (cùng Audio.mp3 113 s + Resources 16 clip, 8 ảnh, `Music_Bg.mp3`) — **khách góp 5 ý** (video YouTube `YQRM2WOHGiA` chỉ tham khảo): (1) bản đồ GG Maps A → B có km + bao lâu, (2) bình luận ảo tiếng Anh + Hàn khen chê mỗi điểm / món, (3) cuối video cảm ơn + mời like & đăng ký, (4) ~30 s đầu cao trào "xem là muốn đi du lịch luôn", (5) KHÔNG chia màn / thẻ kiểu màn dọc — ảnh / video luôn full màn, chữ + sub khác hẳn màn dọc. Người dùng chọn: teaser nhạc + hook lời; vệ tinh + tuyến kiểu GG Maps | Tất cả thành LUẬT TỰ ĐỘNG (ĐÃ CHỐT 2, 5, 7, 8, 13–15): **luôn tràn màn** (`bo_cuc` chỉ `tran`, clip dọc lấy dải 16:9 `cat_y` 0,42 + làm nét `cas`); **teaser** `mo_man` (`nhip.py` dò BPM / phách / đoạn cao trào; cảnh cắt đúng phách; nhạc teaser to ~giọng, hoà 1 s sang nhạc thân; phần thân tự dời `OFF`); **bản đồ A → B** tự có ở mỗi `chuong` có `toa_do` (`ban_do_that.py`: Esri + OSRM, camera cận → toàn tuyến → sà, xe chạy, ghim đỏ, thẻ trắng "≈ giờ (km)", VN nhỏ có Hoàng Sa / Trường Sa; số ước tính luôn "≈" + hỏi D7); lệnh mới `run.py tim "<tên>"`; **bình luận ảo** tự đặt mỗi chương (`binh_luan.py` + `assets/binh_luan.json`, 2 khen + 1 chê nhẹ, en / ko, chỗ trống không đè đồ hoạ lớn; D8); **màn cảm ơn** (câu hỏi + lựa chọn → "Cảm ơn bạn đã xem" sau khi giọng đọc xong → lời mời → tay bấm Đăng ký + chuông + Thích); **bộ chữ mới** Barlow Condensed in hoa trắng + nhấn xanh ngọc, Montserrat nghiêng, sub hộp tối. Lỗi bắt khi soi: Ninh Bình ra bình luận "vịnh" (mô tả "Hạ Long trên cạn") → xét tên trước; `luc_binh_luan` chưa dời theo teaser → thêm vào `KHOA_GIO`; cảm ơn hiện khi giọng còn hỏi → tính giờ CTA trước; thẻ bản đồ tràn "(314 km)" → co theo chữ; MẤT DẤU NẶNG ("VINH HA LONG", "CẢM ƠN BAN") — `.mask` đệm theo em của chính nó → đệm theo cỡ chữ con, và Barlow đặt dấu nặng quá sâu → `sua_font.py`; từ khoá 3 mục 1 hàng đè mặt người → tự xếp cột + dời `vi_tri` / `y`; sub tách "tiếp / tục", "kỳ / quan", "hành / trình", "cảnh / tượng" → +77 từ ghép du lịch. Kết quả `Màn Ngang\Audio_DLN.mp4` 137,8 s (teaser 20,1 s + giọng), 1920×1080: tự kiểm ĐẠT 17/17 — −14,1 LUFS, đỉnh −1,7 dBTP, nhạc thân −13,7 dB dưới giọng, teaser −1,9 dB so với giọng, SFX 50/50 nghe rõ; dựng 262 s (4 luồng × ~5 khung/s), 643 MB |
| 14/11/2026 | cùng video, vòng 2 — người dùng: **"những cảnh đầu làm xịn xò, hiệu ứng chuyển cảnh xịn xò liên tục, kỹ xảo điện ảnh chuyển cảnh… edit vịn vào, h chưa oki… chỉ cần 5 s đầu kỹ xảo chuyển xịn vào (đầu video để đoạn cao trào giật gân ~30 s), những cái hay tinh tuý ở 30 s đầu, sau 30 giây đầu như bình thường"** | Bản 1 teaser chỉ `cat` / `phong` / `zoom` + hook chuyển êm → như trình chiếu. → **LUẬT CAO TRÀO** (ĐÃ CHỐT 16), tự động trong `ke_hoach.py` cho mọi kịch bản: mọi cú cắt 0 → cú DROP = 1 trong 8 kỹ xảo mới vẽ trong `ngang.js` (`vo_kinh` mảnh kính canvas ~60 mảnh, `xoay`, `glitch` dải canvas, `lat_3d` khối hộp CSS 3D, `chay_phim` đốm lửa, `xuyen`, `iris`, `tia_sang`), xoay vòng không lặp liền, vỡ kính luôn ở 5 s đầu, cú DROP = xuyên cảnh; khung 0 đập mở màn + đập theo phách giữa 2 cú cắt; tách màu RGB sắc nét (SVG filter); cửa sổ kỹ xảo tự co ≤ nửa cảnh kề; tên điểm đến teaser đập vào đúng phách sau kỹ xảo; 1 tiếng mỗi kỹ xảo đúng cú cắt (`tao_sfx.py` tổng hợp thêm vỡ kính / whoosh xoay / glitch), bỏ whoosh chữ trùng. Lỗi bắt khi soi khung: khối 3D lộ mặt trong + hở nền đen → điểm nhìn bám cạnh khối + phóng 1,28. Kế hoạch KHÔNG phải sửa (tự gán: t2 vỡ kính, t3 xoay, t4 glitch, t5 khối 3D, t6 cháy phim, t7 xuyên, t8 mở tròn, h1 tia sáng lúc giọng vào, h3 xoay, h4 glitch, h6 khối 3D, h8 xuyên + DROP; 8 cú đập phách). Kết quả `Audio_DLN_ban2.mp4` 137,8 s: tự kiểm ĐẠT 17/17 — −14,1 LUFS, đỉnh −1,4 dBTP, SFX 63/63 nghe rõ; dựng 267 s (kỹ xảo gần như không làm chậm) |
| 14/11/2026 | cùng video, vòng 3 — người dùng: **"chưa oki lắm, chỉ giới thiệu tầm 5–10 s thôi, sau giây thứ 10 là phải có giọng nói rồi… mấy giây đầu đang kiểu tuần tự về mặt edit, chưa cao trào, chưa wao… giống 1 cái tổng hợp cả video trong 10 giây đầu"**; giữa chừng gửi 5 tờ ảnh: **"có 1 vài kỹ xảo chuyển cảnh, hãy ghi nhớ và cho vào skill"** (3 cột bật theo nhịp · khung nhỏ bung to · dải ảnh trượt · cắt nối theo hình · hai nửa đổi vai) | Teaser 20 s 1 cảnh / ô nhịp → **MONTAGE TỔNG HỢP ≤ 10 s** (ĐÃ CHỐT 15, `mo_man.kieu: "tong_hop"`): Claude chỉ xếp THỨ TỰ, `ke_hoach._tong_hop` đặt lên lưới phách (15 phách × 0,628 s = 9,42 s, giọng vào đúng phách trước giây 10, `kiem` ⛔ > 10,05 s), vai cot / ten / nhanh / dinh, cú cắt mới `dap` / `nhay_trang` / `nhay_den`, cửa sổ chuyển LỆCH (`d_t` / `d_s`), tên + tít đỉnh ĐẬP (`dap: true`), nháp quét tự lập khuôn → `Audio_DLN_ban3.mp4` (montage 9,42 s, ĐẠT 18/18, −14,1 LUFS, đỉnh −1,5 dBTP). **5 KỸ XẢO MẪU** (ĐÃ CHỐT 17) vẽ trong `ngang.js`: A `ba_cot` (nhóm 3 cột `veNhom`, cột 3 bung, tên dưới cột → ra giữa), C `khung_bung`, D `dai_truot` (dải ảnh các điểm đến, ảnh đỉnh dừng giữa → phóng), E `khop_hinh` (+ `dung._do_hinh` OpenCV tự dò vùng sáng / hình tròn), F `hai_nua` / `hai_nua_doc`; tự dùng trong montage (mở = A, tên = C / F, đỉnh = D) + `KY_XAO` đoạn hook; SFX `fx_cot` / `fx_cot_bung` / `fx_khung_bung` / `fx_dai_truot` / `fx_hai_nua`. Lỗi bắt khi soi: tên cột bị dải đen 2.35:1 cắt chân → `COT_Y` 822; chữ "BẢN GIỐC" đè mây Sa Pa (cảnh khác điểm đến để vai ten) → vai nhanh; tên sau khung bung chỉ 0,48 s → đập ở 62 % cửa sổ; dải trượt lộ mép đen + tít đè dải → giữ cảnh cũ tối, tít ở 70 %; Hough bắt vòng ảo trên phong cảnh → ưu tiên vùng sáng gọn + Hough ngưỡng 80; khớp hình bọt thác → mặt trời lệch chỗ quá xa → KHÔNG dùng ở video này (chỉ khi 2 hình gần cùng chỗ); dựng bản 3 treo 15 phút (Chrome mở hụt EBUSY không bị đóng) → `render.mjs` giết cả cây Chrome + tự thoát. Kết quả `Audio_DLN_ban4.mp4` 127,1 s (montage 9,42 s: ba cột → khung bung → hai nửa → dồn → dải trượt → đỉnh): tự kiểm ĐẠT 18/18 — −14,1 LUFS, đỉnh −1,4 dBTP, nhạc thân −13,6 dB, teaser −1,9 dB so với giọng, SFX 58/58 nghe rõ; dựng 248 s (bản 3 treo 1224 s) |
| 14/11/2026 | cùng video, vòng 4 — người dùng xem bản 4: **"từ giây thứ 3 đến giây thứ 9 không có sự liên kết, nhịp loạn, hiệu ứng chèn không khớp nhịp… chuyển cảnh bắt đầu vào lời nói chưa có sfx kiểu chốt chuyển, giống kiểu đổ vỡ ở bản demo 3… hiệu ứng chuyển oki nhưng chưa có nhịp chuẩn… đoạn đẩy hình ảnh chỉ có mỗi hình ảnh đẩy, không có text đẩy hay nhân vật gì đó đẩy… kiểu đẩy từ phải qua trái"** | Đo thật: lưới phách cũ (BPM bước 0,5, khung 23 ms) TRÔI 0 → +52 ms sau 15 phách; đầu ô nhịp chọn theo onset toàn dải rơi nhầm phách 2/4. Sửa `nhip.py`: **khớp cục bộ** từng phách với đỉnh onset 6 ms (hồi quy ±8/6/5 phách, trọng số Gauss) → lệch TB 1 ms, độ lệch chuẩn 4 ms; **cú DROP** (độ to [t, t+2 s] − [t−2 s, t] lớn nhất, ≥ 4 dB) = đầu ô nhịp (bài không drop: trầm + đổi hợp âm); độ to 0,5 s đo đúng 0,5 s (trước 21 khung = 0,4876 s, giây 20 lệch 0,5 s). Montage (ĐÃ CHỐT 15/17): cửa sổ kỹ xảo tính bằng PHÁCH (`CHUYEN_NHIP`), mọi nấc rơi đúng phách / ½ phách — khung bung bật (phách) → vừa (½) → tràn + tên (phách sau); HAI NỬA thành cú **ĐẨY**: cảnh cũ bị đẩy trái, cảnh mới lộ sau mép sáng 3 nấc, **CHỮ chạy theo mép** (`day_chu` từ `chu` / `nhan` của cảnh, né người, đứng giữa rồi bị đẩy ra cùng cảnh), **NGƯỜI tách nền** (`scripts/nguoi.py`, u2net_human_seg) nhô qua mép ở nấc 1 (mép tự đặt cắt ngang người) rồi về đúng chỗ; đoạn dồn = chuỗi **ĐẨY NHANH** phải → trái mỗi ½ phách (bỏ trộn 5 kiểu cắt), Ken Burns trôi trái cùng hướng; dải trượt vào phách, khựng ½ phách, ảnh đỉnh phóng đúng phách; **GIỌNG VÀO = VỠ KÍNH** + riser dồn từ ảnh đỉnh + boom chốt (đỉnh chỉ còn thịch nhẹ); SFX theo NẤC (`fx_buoc` / `fx_cham` / `fx_day`). Kế hoạch: ảnh cáp treo (có người) + chữ "Cáp treo · Biển mây" (lời 31,4 s) làm cú đẩy. Bẫy: `cv2.imread` không đọc đường dẫn có dấu → `imdecode(np.fromfile)`. Kết quả `Audio_DLN_ban5.mp4` 127,2 s 1920×1080, teaser 9,47 s (15 phách × 0,631 s), −14,1 LUFS, đỉnh −1,3 dBTP, 72/72 SFX nghe rõ, tự kiểm ĐẠT. |
| 14/11/2026 | cùng video, vòng 5 — người dùng xem bản 5: **"giây thứ 5, 6, 7 chuyển cảnh nhanh quá, hơi khó chịu, chậm lại chút"** | Đoạn dồn trước cắt mỗi ½ phách (≈ 0,32 s/cảnh) + đẩy outExpo 0,2 s + clip tua ×1,5 → mắt không kịp nhìn. Sửa (tự động): dồn mỗi cảnh **1 PHÁCH** (`TONG_HOP_NHIP['nhanh']` 1,0), cú đẩy **0,34 s** chậm dần đều (outCubic, cửa sổ `CHUYEN_NHIP` ½ → 0,55 phách), clip dồn tua **×1,1**; thừa cảnh dồn thì tự bỏ bớt để cảnh ĐỈNH vẫn đủ 3 phách (dải trượt + tít + vỡ kính không bị dồn). Kế hoạch: dồn còn 3 cảnh khác điểm đến (đầm sen Ninh Bình, thuyền Hạ Long, ruộng Sa Pa — bỏ mây Sa Pa xám, Fansipan đông người). Kết quả `Audio_DLN_ban6.mp4` 127,2 s 1920×1080, dồn 5,05 / 5,68 / 6,32 s, −14,1 LUFS, đỉnh −1,5 dBTP, 70/70 SFX nghe rõ, tự kiểm ĐẠT. Người dùng nói thêm: **"các giây kia là tôi xem thấy vậy thì bảo sửa, đừng ghi hard là giây 5, 6, 7… không được chuyển cảnh nhanh như vậy dù là ở đâu trong video; cập nhật tất cả những cái xịn, lưu ý vào skill để chỉ cần gọi skill là edit xịn"** → LUẬT NHỊP CẮT (ĐÃ CHỐT 18: `CAT_MIN_*`, `DUNG_RO_MIN`, `DAY_S`; `kiem-kh` ⛔ / 🔧, tự kiểm mục "nhịp cắt") + mục "CHUẨN XỊN" tóm tắt mọi điều khách đã duyệt; tự kiểm đặt tên file tạm `_hop_<pid>.json` (chạy `kiem` tay lúc `dung` đang tự kiểm từng giẫm nhau → `FileNotFoundError`). |

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
   NGOẠI LỆ: đoạn CAO TRÀO ~30 s đầu dùng KỸ XẢO ĐIỆN ẢNH ở mọi cú cắt (mục 16) — vẫn sắc nét, không nhoè.
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
   chương, pop NHỎ ở chip / mục liệt kê / ghim (−4…−3 dB dưới giọng), riser + ding số lớn, click / chuông / thích ở màn kết, và 1 tiếng
   ở mỗi kỹ xảo đoạn cao trào 30 s đầu (mục 16). Tiếng nào có thì
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
   - mỗi vế câu hook ĐÚNG 1 cảnh (≥ 1,8 s — vòng 3 người dùng chê 1–2 s/cảnh là "chưa kịp nhìn"); hook nằm trong đoạn CAO TRÀO → cú cắt tự
     thành KỸ XẢO ĐIỆN ẢNH + 1 tiếng (mục 16; `chuyen` ghi trong kế hoạch chỉ dùng khi tắt cao trào); MỌI cảnh tràn khung (mục 2); ảnh to cắt `vung` đẹp nhất;
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
15. **TEASER MỞ MÀN = MONTAGE TỔNG HỢP ≤ 10 s** (khách 14/11/2026 vòng 1: "đầu video để đoạn cao trào giật gân giữ người xem, xem cái là
   muốn đi du lịch luôn"; **vòng 3: "chỉ giới thiệu tầm 5–10 s thôi, sau giây thứ 10 là phải có giọng nói rồi… mấy giây đầu đang kiểu tuần
   tự về mặt edit, chưa cao trào, chưa wao… giống 1 cái TỔNG HỢP cả video trong 10 giây đầu"**). `mo_man: {kieu: "tong_hop", canh[], dinh}` —
   Claude chỉ XẾP THỨ TỰ cảnh + chữ, KHÔNG ghi giờ; `ke_hoach._tong_hop` tự đặt lên LƯỚI PHÁCH; phần thân viết theo giờ `loi_doc.txt`, script dời
   mọi giờ (+ giọng, sub, SFX) thêm độ dài teaser:
   - `nhip.py` dò BPM / phách rồi **khớp lưới vào tiếng trống thật** (vòng 4: lưới đều trôi tới +52 ms sau 15 phách → "nhịp loạn"): mỗi phách
     bám đỉnh onset 6 ms gần nhất, hồi quy cục bộ ±5–8 phách → lệch ≤ ~5 ms suốt bài; **cú DROP = đầu ô nhịp** (onset toàn dải hay rơi phách
     2/4); `nhac_tu` = đầu ô nhịp to nhất + có cú dâng (thường đúng DROP của bài); độ dài teaser tự khớp về PHÁCH gần
     9,5 s, **≤ 10 s** (`MO_MAN_MIN/MAX` 5–10) → giọng vào đúng phách trước giây 10 (`run.py kiem` ⛔ nếu > 10,05 s);
   - khuôn nhịp độ (`TONG_HOP_NHIP`): **BA CỘT** (≥ 5 cảnh → 3 cảnh đầu `cot`, mỗi cảnh có `chu` + `nhan`: cột 1 bật khung 0 + đập mở màn,
     cột 2 sau 1 phách, cột 3 sau 1 phách nữa, đứng 1 phách rồi BUNG tràn màn, tên nhỏ dưới mỗi cột, tên cột 3 lớn dần ra giữa — khung 0 =
     ảnh xem trước YouTube có 3 cảnh; mục 17 A; ít cảnh / `ba_cot: false` → cảnh 1 `mo` 2 phách) → **tên** (mỗi điểm đến 1–2 cảnh, cảnh đầu
     có `chu` = TÊN + `nhan` = tính từ trong lời; cắt thường 1 phách, kỹ xảo dài KHUNG BUNG / HAI NỬA 2 phách; tên ĐẬP lúc cảnh LỘ HẾT 1,6 → 1
     trong 0,16 s + giật, đứng tới tên kế, tắt cứng) → **dồn** (4–8 cảnh hay nhất KHẮP video — người, trải nghiệm, món, cảnh lạ — mỗi cảnh
     1 PHÁCH (vòng 5: ½ phách bị chê "nhanh quá, khó chịu"), clip tua ×1,1, nối nhau bằng ĐẨY phải → trái cùng 1 hướng + Ken Burns trôi
     trái — vòng 4: trộn 5 kiểu cắt bị chê "không liên kết, nhịp loạn"; thừa cảnh thì tự bỏ cảnh dồn cuối để đỉnh đủ 3 phách — Claude nên
     chọn sẵn 3–4 cảnh dồn khác điểm đến) → **đỉnh** (cảnh cuối, ảnh to nét nhất, phần phách còn lại 2–4: DẢI ẢNH TRƯỢT các điểm đến vào 1 phách
     trước, khựng ½ phách, ảnh đỉnh phóng tràn ĐÚNG phách (tự cho cảnh trước đỉnh 2 phách) + tít `dinh` {dan, khoa, viet_tay} cỡ 210 đập ở
     phách sau, ảnh zoom lùi / clip quay chậm ×0,7; cảnh trước đỉnh ghi `nhip` < 1,5 thì VỠ KÍNH) → **giọng vào = VỠ KÍNH** (`TONG_HOP_CAT
     giong`; khách vòng 4: "chuyển cảnh vào lời nói chưa có sfx chốt, như đổ vỡ ở demo 3") + riser dồn 1,85 s từ ảnh đỉnh + boom CHỐT;
   - cú cắt tự gán theo vai (`TONG_HOP_CAT`): cảnh tên xoay vòng `khung_bung` → `hai_nua` → `xoay` → `dap` → `hai_nua_doc` → `glitch` →
     `lat_3d` → `xuyen` → `nhay_trang` (kiểu dài chỉ khi cảnh vào ≥ 1,5 phách — `nhip` ghi < 1,5 thì bỏ qua kiểu dài); đoạn dồn
     **`day_nhanh`** (đẩy phải → trái mỗi 1 phách, outCubic 0,34 s rồi đứng tới phách sau, vạch sáng ở mép); `dap` / `nhay_trang` / `nhay_den` còn dùng tay được;
     cửa sổ kỹ xảo montage = **bội số PHÁCH** (`CHUYEN_NHIP`: khung bung / hai nửa 0 trước + 1 phách sau + 0,18 s cho nấc cuối chạy, dải trượt
     1 phách trước + ½ sau, đẩy 0,55) — MỌI NẤC đúng phách / ½ phách (vòng 4: "hiệu ứng chèn không khớp nhịp"); kiểu khác vẫn cửa sổ LỆCH
     `CHUYEN_LECH` (≤ nửa cảnh kề); thiếu phách → bỏ cảnh dồn cuối, rồi hạ kỹ xảo dài thành `dap` (⚠);
   - `nhip` (bước 0,5) / `vai` (cot / mo / ten / nhanh / dinh) / `chuyen` / `toc_do` / `khop` ghi rõ thì giữ;
   - âm thanh: NHẠC (dâng +12 dB ≈ to như giọng) + **tiếng THEO NẤC, nấc nào cũng đúng phách** (vòng 4): boom khung 0, whoosh mỗi cột
     bật, swoosh cột 3 bung; khung bung / hai nửa: `fx_buoc` ở nấc 1 + nấc ½, `fx_cham` (thịch trầm) ở nấc CHỐT tràn màn (tên đập cùng lúc, bỏ
     whoosh chữ); đẩy nhanh: `fx_day` mỗi cú; dải trượt: `fx_buoc` lúc vào + lúc khựng, `fx_cham` lúc ảnh đỉnh phóng; riser 1,85 s → **vỡ kính
     + boom lúc giọng vào**; 0,6 s trước giọng vào nhạc hạ về nền, nối hoà tan 1 s sang nhạc phần thân;
   - sau montage là hook lời + cú DROP (mục 12) — đoạn cao trào tới drop vẫn kỹ xảo (mục 16), ưu tiên kiểu montage CHƯA dùng, không lặp vỡ kính;
   - kiểu cũ 1 cảnh / ô nhịp: `kieu: "nhip"` (⚠ — khách chê tuần tự); Resources KHÔNG có nhạc → ⚠ bỏ teaser; `mo_man.bat: false` để tắt.
16. **CAO TRÀO 30 s ĐẦU = KỸ XẢO ĐIỆN ẢNH Ở MỌI CÚ CẮT** (người dùng 14/11/2026: "những cảnh đầu làm xịn xò, hiệu ứng chuyển cảnh xịn xò liên
   tục, kỹ xảo điện ảnh chuyển cảnh… chỉ cần 5 s đầu kỹ xảo xịn vào… những cái hay tinh tuý sẽ có ở 30 s đầu này, xong sau 30 giây đầu sẽ
   như bình thường") — TỰ ĐỘNG trong `ke_hoach.py`, Claude không phải ghi:
   - đoạn cao trào = 0 → cú DROP `mo_dau` đầu tiên (8–45 s; không có thì 30 s, `CAO_TRAO_DAI`). MỌI cú cắt trong đoạn (teaser + hook) tự
     thành 1 kỹ xảo, xoay vòng `KY_XAO` không lặp liền: **`vo_kinh`** (nứt toả 0,16 s → khung đứng của cảnh cũ vỡ ~60 mảnh bay / xoay / lật /
     rơi, cảnh mới đập vào — luôn là cú đầu, rơi vào 5 s đầu) · **`xoay`** (xoáy +24° phóng 1,9× → loé → xoáy về) · **`glitch`** (dải ngang
     lệch, nháy 2 cảnh, vạch xanh-hồng) · **`lat_3d`** (2 cảnh là 2 mặt khối hộp xoay 90°, điểm nhìn bám cạnh khối + phóng 1,28 → không hở
     nền, không lộ mặt trong) · **`chay_phim`** (đốm lửa cam-trắng loang, cảnh cũ cháy sáng) · **`xuyen`** (lao vụt vào 2,2× + loé → cảnh mới
     đập ra + rung) · **`iris`** (mở tròn từ tâm, viền sáng xanh ngọc) · **`tia_sang`** (màn sáng quét + loé nắng — thường rơi đúng lúc giọng
     vào); vòng 2 bỏ vỡ kính; cú cắt trùng DROP = `xuyen` (+ boom sẵn có);
   - kèm: **khung 0 đập mở màn** (phóng 1,32 → 1 + tách màu RGB 26 px → 0 trong 0,6 s, tiếng `boom`); **đập theo PHÁCH** ở giữa 2 cú cắt teaser
     (phóng 5,5 % + tách màu + loé nhẹ, 5 s đầu ×1,3); tách màu RGB SẮC NÉT (SVG `#rgb_tach`, không nhoè) ở đỉnh mỗi kỹ xảo;
   - mỗi kỹ xảo 1 tiếng ĐÚNG CÚ CẮT (`fx_*` trong `SFX`: vỡ kính / whoosh xoay / glitch tự tổng hợp bằng `tao_sfx.py`, còn lại swoosh); chữ teaser
     hiện cùng / ngay sau kỹ xảo thì BỎ whoosh chữ (1 cú = 1 tiếng);
   - cảnh hook vẫn ≥ 1,8 s (montage ≤ 10 s đầu là ngoại lệ cố ý — mục 15); cửa sổ kỹ xảo (0,6–1,2 s, tâm = cú cắt đúng phách) tự co ≤ nửa
     cảnh kề → luôn còn ≥ ½ cảnh đứng yên cho kịp nhìn; chữ hook chờ kỹ xảo xong (tên trong montage thì đập ĐÚNG cú cắt);
   - Claude ghi rõ 1 kỹ xảo trong `chuyen` → giữ; `man` / `giu_chuyen: true` → giữ; `cao_trao: {"fx": […]}` đổi thứ tự, `{"het": 25}` đổi
     điểm kết, `false` tắt. SAU đoạn cao trào: chuyển êm như mục 4 (kỹ xảo vẫn dùng tay được nhưng đừng — khách chốt "sau 30 s bình thường").

17. **5 KỸ XẢO CHUYỂN CẢNH MẪU** (người dùng gửi 5 tờ ảnh 14/11/2026: "có 1 vài kỹ xảo chuyển cảnh, hãy ghi nhớ và cho vào skill") — CHIA
   MÀN TẠM THỜI trong lúc chuyển, kết thúc LUÔN tràn màn (không trái mục 2); cảnh luôn sắc nét, viền trắng 5 px + bóng khi là khung nhỏ.
   Vẽ trong `ngang.js` (`veNhom`, case `khung_bung` / `hai_nua` / `dai_truot` / `khop_hinh`), bảng `CHUYEN` + `CHUYEN_LECH` trong `chung.py`:
   - **A `ba_cot` — 3 CỘT BẬT THEO NHỊP:** cảnh + 2 cảnh sau thành 3 cột (rộng ⅓, khe 10 px, phần còn lại đen): cột 1 bật (trượt xuống
     70 px + loé) → cột 2 → cột 3 đúng từng phách, tên nhỏ (nhãn + tên in hoa + vạch) dưới mỗi cột → cột 3 BUNG tràn màn (0,38 s), tên cột 3
     phóng ×2,15 ra giữa. Chỉ ở MONTAGE (3 cảnh đầu, tự gán khi ≥ 5 cảnh — mục 15); `ke_hoach` lập nhóm `nhom` {ids, moc, bung, het, nhan}.
   - **C `khung_bung` — KHUNG NHỎ BUNG TO** (bắt đầu đúng cú cắt): cảnh mới hiện thành khung nhỏ viền trắng giữa cảnh cũ; MONTAGE (có `p`):
     3 NẤC theo phách — bật 0,12 → 0,36 (nảy) đúng phách, 0,64 (nảy) ở ½ phách, tràn màn (outExpo 0,17 s) ở phách sau + tên đập cùng nấc;
     ngoài montage: liền 1,0 s (0,3 nảy → 0,78 → tràn). Cảnh cũ tối 32 % + phóng 7 %. SFX montage `fx_buoc` × 2 + `fx_cham`, ngoài `fx_khung_bung`.
   - **D `dai_truot` — DẢI ẢNH TRƯỢT**: cảnh cũ tối dần (38 %), dải ảnh nhỏ (30 % khung, viền trắng; ảnh = khung đầu các cảnh có tên trong
     montage, ngoài montage = 3 cảnh kế, hoặc `dai: [id…]`) trượt từ phải vào, ảnh cảnh mới nằm GIỮA dải dừng ở tâm → phóng tràn màn, ảnh 2
     bên bay dạt ra + mờ. MONTAGE: dải VÀO đúng phách (1 phách trước cú cắt), KHỰNG ½ phách (ảnh đỉnh vào giữa), ảnh đỉnh PHÓNG đúng phách
     (outExpo ½ phách); ngoài montage: trượt liền 0,9 s + phóng 0,5 s. Đỉnh montage mặc định. SFX montage `fx_buoc` × 2 + `fx_cham`, ngoài
     `fx_dai_truot` lúc dải bắt đầu trượt.
   - **E `khop_hinh` — CẮT NỐI THEO HÌNH** (0,6 s): 2 cảnh có hình giống nhau (tròn: bánh xe → bát phở → đèn lồng → mặt trời; người →
     người) — cảnh cũ phóng 1,28 vào hình đó, cảnh mới vào với hình của nó TRÙNG CHỖ + CỠ rồi trôi về khung thường + loé nhẹ. Chỉ khi
     CLAUDE thấy 2 cảnh có hình giống nhau Ở GẦN CÙNG CHỖ trong khung (soi tờ khung) → ghi `chuyen: "khop_hinh"`; `khop: {ra: [x, y, r],
     vao: [x, y, r]}` (0–1, r theo chiều cao) tuỳ chọn — thiếu thì `dung.py` (`_do_hinh`) tự dò ở khung cuối cảnh cũ + khung đầu cảnh mới:
     ① vùng sáng gọn (mặt trời, đèn lồng: lõi sáng nhất, không chạm mép, độ tròn ≥ 0,3) → ② hình tròn nét (Hough ngưỡng cao 80 — ngưỡng thấp
     bắt nhầm vòng ảo trên phong cảnh) → ③ giữa khung. Cảnh mới chỉ dời được trong giới hạn không hở mép (phóng ≤ 2,2×): 2 hình cách xa nhau
     (bọt thác dưới-trái → mặt trời trên-giữa, thử 14/11/2026) thì thành "phóng ra từ mặt trời", không còn là khớp hình → đừng dùng.
   - **F `hai_nua` — CÚ ĐẨY HAI NỬA** (vòng 4, khách: "chỉ có hình ảnh đẩy, không có text đẩy hay nhân vật gì đó đẩy… đẩy từ phải qua trái"):
     cảnh cũ BỊ ĐẨY sang trái (dịch thật, tối dần), cảnh mới lộ ra sau MÉP SÁNG (vạch trắng-xanh ngọc phát sáng) dừng 3 nấc đúng phách
     (montage: phách → ½ → phách sau; ngoài montage 0 / 0,36 / 0,72 cửa sổ): nấc 1 tự đặt cắt ngang **NGƯỜI** trong cảnh mới (¼ thân tính từ
     mép trái người, kẹp 45–80 % khung; không người 66 %), nấc 2 ≤ 33 %, nấc 3 tràn. **Người** (`dung._tach_nguoi` → `scripts/nguoi.py`
     u2net_human_seg, khung đầu cảnh mới, người 2–50 % khung; tắt: `nhan_vat: false`) là lớp PNG nền trong trùng khít cảnh mới, không bị cắt
     ở mép → nhô qua mép sang cảnh cũ như đang đẩy, phóng 6 % + viền sáng, về đúng chỗ khi mép qua hết rồi tắt. **Chữ** (`chu` + `nhan` của
     cảnh montage → `day_chu`, KHÔNG đập giữa như tên thường): tên in hoa 150 px + nhãn dưới + vạch, mép trái bám mép đẩy + 44 px, tự co vừa
     phần mới ở nấc 1, dải trên (y 170) hoặc dưới (đáy 930) — bên nào ít đè người hơn; tràn màn thì đứng giữa; cú cắt kế là đẩy nhanh thì chữ
     bị đẩy ra cùng cảnh. **`hai_nua_doc`** chia TRÊN / DƯỚI 2 nấc (cắt giữa khung, chữ bám mép ngang). SFX montage `fx_buoc` × 2 + `fx_cham`.
   - **`day_nhanh` — ĐẨY** (vòng 4, đoạn dồn; vòng 5 chậm lại): cảnh cũ ra trái, cảnh mới vào từ phải trong 0,34 s (outCubic, không giật), 1 cú / 1 phách, vạch sáng
     ở mép, tách màu nhẹ; cùng 1 hướng suốt đoạn dồn → các cảnh nối mạch (không trộn chớp trắng / đập / glitch). SFX `fx_day`.
   - TỰ DÙNG: montage (mục 15: mở = A, tên = C / F xoay vòng với xoay / đập / glitch…, đỉnh = D); đoạn cao trào hook (mục 16): `KY_XAO`
     thêm `khung_bung` · `hai_nua` · `dai_truot` · `hai_nua_doc`, kiểu dài chỉ khi 2 cảnh kề đều ≥ 1,8 s (không thì `xoay`). Ngoài 2 đoạn đó
     Claude ghi tay được (`chuyen`), nhưng sau 30 s nên êm (khách chốt).
18. **LUẬT NHỊP CẮT — KHÔNG CHUYỂN CẢNH DỒN DẬP Ở BẤT KỲ ĐÂU** (khách 14/11/2026 vòng 5: "chuyển cảnh nhanh quá, hơi khó chịu, chậm lại
    chút"; rồi nói rõ: "các giây kia là tôi xem thấy vậy thì bảo sửa, đừng ghi hard là giây 5, 6, 7… không được chuyển cảnh nhanh như vậy
    dù là ở đâu trong video"). Số ở `chung.py`: `CAT_MIN_PHACH` 1 phách + `CAT_MIN_S` 0,55 s (montage; nhạc nhanh → `_tong_hop` tự nâng
    1,5 / 2 phách), `CAT_MIN_THAN` 1,5 s (thân), `DUNG_RO_MIN` 0,25 s đứng yên rõ giữa 2 cú chuyển, `DAY_S` 0,34 s cho cú đẩy cả khung
    (outCubic). `nhip` Claude ghi nhỏ hơn → 🔧 tự nâng; cảnh / khoảng đứng rõ dưới ngưỡng → ⛔ `kiem-kh`; tự kiểm cuối mục "nhịp cắt" ⛔.
    Nấc BÊN TRONG 1 kỹ xảo (khung bung bật → vừa → tràn, đẩy 3 nấc) vẫn ½ phách — đó là 1 cảnh đang lộ ra, không phải đổi cảnh.

## Khuôn kể chuyện du lịch → bố cục + đồ hoạ (áp cho MỌI kịch bản)

| Kiểu câu | Cảnh | Đồ hoạ |
|---|---|---|
| (trước lời) MONTAGE TỔNG HỢP ≤ 10 s chỉ nhạc | `mo_man` `kieu: "tong_hop"`: cảnh xếp THỨ TỰ, không giờ — 3 cảnh đẹp nhất của 3 điểm đến (BA CỘT) → 1–2 cảnh / điểm đến còn lại → 4–8 cảnh dồn hay nhất khắp video → cảnh đỉnh ảnh to nét nhất (mục 15, 17; giờ + cú cắt TỰ trên lưới phách) | `chu` + `nhan` trên 3 cảnh ba cột + cảnh đầu mỗi điểm đến còn lại (tên đập theo phách); `dinh` {dan, khoa, viet_tay} tít đỉnh (vd "4 điểm đến · 4 vẻ đẹp", chữ từ lời) |
| Hook mở (câu hỏi "bạn đã bao giờ…", 2–4 vế) | LUẬT HOOK (mục 12): mỗi vế ĐÚNG 1 cảnh (≥ 1,8 s) tràn khung; cú cắt = kỹ xảo điện ảnh tự gán (còn trong 30 s cao trào) | `hook_tu` mỗi vế (chữ khoá + địa danh); đầu hook: `hook_tu` `kieu: "cau"` |
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
   mọi cảnh tràn; có nhạc → khung `mo_man` montage tổng hợp 13 cảnh + đỉnh + đoạn cao trào gợi ý). Quét lại giữ mã cũ, file mới nhận số kế tiếp, kế hoạch đã sửa
   giữ nguyên. Whisper lần đầu tải ~3 GB; CPU ~4 phút / phút audio — chạy nền, đừng huỷ.
2. **Claude viết kế hoạch theo NGHĨA**: đọc mục **CHUẨN XỊN** ở trên (luật nhịp cắt, chọn cảnh montage, cú đẩy có chữ / người), `goi_y.txt`, `loi_doc.txt`; MỞ `tai_nguyen.jpg` + MỌI `khung\clip_NN.jpg`; gán mỗi câu 1 kiểu
   (bảng trên); viết `mo_man` (teaser), `canh` / `do_hoa` (chương có `toa_do` — `run.py tim "<tên>"`, cần mạng) / `cta` / `sua_loi`
   (mẫu `references/vi-du-4-diem-den.json`, khuôn `references/ke_hoach_schema.md`); đặt `CAN_CLAUDE_SUA: false`.
3. `run.py kiem-kh --work <dir>` → hết ⛔ (⚠ cân nhắc; 🔧 = đã tự sửa giờ cho kịp nhìn).
4. `run.py duyet --work <dir>` → `duyet.jpg` (khung giữa mỗi cảnh / đồ hoạ / màn kết) + `bang_duyet.txt`. MỞ `duyet.jpg` soi như dân mỹ
   thuật: chữ mất / đè người / đè thẻ / quá nhỏ, thẻ sai bên, ảnh sai nghĩa, logo dán. Soi gần: `run.py khung --work <dir> --times 12.3,45.6`
   (→ `khung_le.jpg`; nên soi cả giây giữa chuyển cảnh).
5. **CỔNG DUYỆT** — gửi `duyet.jpg` + bảng tóm tắt (teaser, số bản đồ, bình luận ảo trong `bang_duyet.txt`), hỏi D1–D8.
6. `run.py dung --work <dir> [--luong 4]` (~115 s video ≈ 6–8 phút, chạy nền) → `<audio>_DLN.mp4`, tự chạy `kiem`.
   Thử nhanh: `--xem-truoc` (20 s đầu — đủ montage + hook). Chỉ đổi TIẾNG: `run.py tron-lai --work <dir>`.
7. `run.py kiem` phải **ĐẠT**: 1920×1080 · 30 fps · không cắt giọng (tính cả giọng lùi sau teaser) · có tiếng · −14 LUFS ±1 · đỉnh ≤ −1 dBTP ·
   nhạc −24…−9 dB (khi có) · nhạc teaser −6…+3 dB so với giọng · luôn tràn màn · đủ bản đồ A → B · đủ đợt bình luận ảo · có teaser · màn
   cảm ơn · không khung đen giữa video · sub không đè chữ đồ hoạ / chữ không tràn mép (chụp hộp chữ mỗi 0,5 s). MỞ `soat.jpg`.
8. Giao: đường dẫn, độ dài, bảng lời → cảnh / đồ hoạ, mục còn đoán (D4–D6). Dọn: `run.py don --work <dir>` (xoá `footage\`, ~1 GB).

## Bẫy đã gặp (trang dựng HTML)

- **Góp ý kèm giây ≠ luật theo giây (vòng 5):** khách chỉ "giây 5, 6, 7 nhanh quá" → sửa riêng chỗ đó là SAI; phải tìm NGUYÊN NHÂN chung
  (cắt ½ phách + đẩy 0,2 s giật + clip tua ×1,5) và đặt luật cho mọi chỗ (ĐÃ CHỐT 18) + kiểm tự động.
- `run.py kiem` chạy tay trong lúc `dung` còn tự kiểm → 2 tiến trình cùng ghi / xoá `_hop.json` → `FileNotFoundError` → tên file tạm theo
  pid. Chờ `dung` in "TỰ KIỂM: ĐẠT" rồi hãy kiểm thêm.

- **"Nhịp loạn" dù cú cắt đặt đúng lưới phách (vòng 4):** lưới đều từ BPM bước 0,5 + khung 23 ms trôi +52 ms sau 15 phách (bài thật
  ~95,2 BPM chứ không 95,5) và đầu ô nhịp chọn theo onset toàn dải rơi vào phách 2 / 4 (snare) → `nhip._tinh_chinh` (khớp cục bộ từng phách
  vào đỉnh onset 6 ms) + `_drop` (cú drop = đầu ô). Kỹ xảo chạy LIỀN 0,8–1,2 s (ease đều) cũng nghe lệch nhịp dù bắt đầu đúng phách → mọi
  kỹ xảo montage chia NẤC, mỗi nấc outExpo ≤ 0,2 s đặt ĐÚNG phách / ½ phách (`CHUYEN_NHIP`), 1 tiếng mỗi nấc. Đổi lưới phách phải đổi
  khoá cache `nhip.py` (`'nhip6'`), không thì `nhac_nhip.json` cũ vẫn được dùng.
- Đo độ to theo khối "0,5 s" bằng 21 khung × 512 mẫu = 0,4876 s → tới giây 20 lệch 0,5 s, `chon_dau` đọc nhầm khối → đo thẳng trên mẫu.
- Người nhô qua mép: lớp PNG phải là CÙNG file khung (`_tep_khung` ở cú cắt) + cùng Ken Burns với cảnh mới → trùng khít, không ra 2 người.
  Mép nấc 1 phải cắt NGANG người (không thì người nằm gọn trong phần mới, không thấy "nhô"). `cv2.imread` / `imwrite` không đọc / ghi đường
  dẫn có dấu tiếng Việt trên Windows → `cv2.imdecode(np.fromfile(...))` / `imencode(...).tofile(...)`.

- **Dựng xong mà không thoát (treo 15 phút, 14/11/2026):** 1 luồng Chrome mở hụt (`EBUSY` đọc `DevToolsActivePort`) → ném lỗi TRƯỚC khi có
  `dong()` → Chrome sót giữ ống → node không thoát dù `_hinh.mp4` đã đủ khung. Sửa `render.mjs`: đọc cổng có thử lại, lỗi thì giết CẢ CÂY
  Chrome (`taskkill /T /F` — `proc.kill()` trên Windows chỉ giết tiến trình chính), `main()` xong là `process.exit(0)`. Gặp lại: `_hinh.mp4`
  đủ khung (ffprobe nb_frames = giây × 30) thì giết Chrome con của node render → `dung` tự đi tiếp trộn tiếng + ghép + kiểm.
- Montage BA CỘT: tên dưới cột phải nằm TRÊN dải đen điện ảnh 2.35:1 (khung thấy được y 131–949) → `COT_Y` 822; đặt 912 bị dải đen cắt chân chữ.
- Montage: cảnh vai `ten` KHÔNG có `chu` = cảnh thứ 2 CÙNG điểm đến → tên trước còn đứng trên nó. Cảnh khác điểm đến (mây Sa Pa sau Bản Giốc)
  mà để `ten` thì chữ "BẢN GIỐC" đè lên mây Sa Pa → ghi `vai: "nhanh"` (+ `nhip` / `chuyen` nếu muốn kỹ xảo dài).
- Tên đập sau KHUNG BUNG / HAI NỬA: đợi cảnh lộ hết thì chỉ còn 0,48 s (⛔ < 0,5 s) → tên đập khi khung đã ~80 % màn (0,62 cửa sổ sau cắt).
- DẢI TRƯỢT: cảnh cũ mờ dần trong lúc ảnh mới phóng → lộ mép đen 2 bên → cảnh cũ giữ (tối 38 %) tới khi ảnh mới phủ kín; tít đỉnh hiện
  lúc ảnh đã ~90 % màn (0,7 cửa sổ sau cắt), không đè lên dải ảnh.

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
- Kỹ xảo vẽ trên canvas (`#fx_ve`: mảnh kính, dải glitch) phải vẽ trong `VE_SAU` (sau khi ảnh khung đã `decode`) và vẽ lại đúng Ken Burns
  của cảnh (`veKhung` = `object-fit: cover` + `kbOf`) — vẽ ngay trong `ghepCanh` ra mảnh trống / lệch hình.
- Khối hộp 3D (`lat_3d`) với điểm nhìn cố định giữa khung: lúc đầu / cuối cú xoay thấy mặt kia từ BÊN TRONG (dải hình gập đè lên cảnh cũ)
  + hở nền đen → `perspectiveOrigin` bám cạnh khối (`W·(1−e)`) + phóng `#canh_lop` 1 + 0,28·sin(πe) (soát 14/11/2026).
- Tách màu RGB bằng SVG filter để lại dải mép thiếu kênh màu rộng = độ lệch → phóng `#canh_lop` thêm 2,4·lệch/W khi đang tách màu.
- Cửa sổ kỹ xảo rộng hơn chuyển êm → `kiem-kh` dời chữ `hook_tu` tới lúc kỹ xảo xong; teaser thì bắt lên PHÁCH kế tiếp (không thì tên điểm
  đến hết bám nhạc).

## Tệp

- `scripts/run.py` (lệnh) · `quet.py` (Whisper, quét Resources, tờ khung, gợi ý, nháp) · `ke_hoach.py` (kiểm + giải giờ cảnh / chuyển /
  đồ hoạ / sub / SFX) · `dung.py` (trích khung theo bố cục, trang dựng, duyệt, dựng, trộn) · `render.mjs` (Chrome headless qua DevTools,
  chia luồng) · `am_thanh.py` (trộn giọng / nhạc / SFX, −14 LUFS, AAC) · `kiem.py` (tự kiểm file cuối) · `chung.py` (hằng số, tiện ích) ·
  `cai_dat.py` (kiểm máy) · `tao_sfx.py` (tự tổng hợp `boom.wav` cho cú drop + `vo_kinh.wav` / `xoay.wav` / `glitch.wav` cho kỹ xảo cao trào) · `ban_do_that.py` (tìm toạ độ `run.py tim`, tuyến
  OSRM, camera + ô vệ tinh Esri cho bản đồ A → B; cache `_cache_tiles\esri`) · `nhip.py` (BPM, phách mạnh, đoạn cao trào của nhạc cho
  teaser) · `binh_luan.py` (bình luận ảo en / ko theo loại cảnh, chọn tất định) · `sua_font.py` (nâng dấu nặng Barlow Condensed).
- `assets/khung/ngang.css|js` (trang dựng) · `assets/khung/vn_ban_do.js` (đường viền VN Natural Earth 1:50m + Hoàng Sa, Trường Sa) ·
  `assets/binh_luan.json` (kho câu khen / chê en + ko theo loại cảnh, tên người tự đặt, cờ, tên địa danh theo tiếng) ·
  `assets/fonts` (OFL; Barlow Condensed đã sửa dấu nặng) · `assets/sfx` (xem `CREDITS.md`) · `assets/tu_ghep_vi.txt`.
