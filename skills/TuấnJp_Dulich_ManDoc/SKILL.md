---
name: TuấnJp_Dulich_ManDoc
description: Dựng VIDEO QUẢNG BÁ / GIỚI THIỆU DU LỊCH dọc 9:16 (1080×1920, 30 fps) từ 3 đầu vào — LINK 1 BÀI BÁO du lịch (tự lấy chữ + ảnh, hỗ trợ vietnamtourism.gov.vn qua API công khai, trang thường, trang JS), 1 FILE AUDIO giọng đọc kịch bản, 1 THƯ MỤC RESOURCES clip / ảnh — theo phong cách du lịch cao cấp tự thiết kế (video mẫu Tuấn_jp chỉ là THAM KHẢO, không phải quy chuẩn): footage chỉnh màu ấm điện ảnh + hạt phim + loé nắng, Ken Burns mỗi cảnh, 8 kiểu chuyển (hoà tan, nhoè, lia nhoè, lia dọc, zoom xuyên, loé sáng, trượt, cắt), ảnh bài báo nhỏ thành THẺ BO GÓC trên nền nhoè của chính nó + ghi nguồn; ĐỒ HOẠ HÀNH TRÌNH khi lời nói di chuyển A → B (điểm đi / điểm đến, phương tiện, thời gian / km đúng lời; MẶC ĐỊNH trên BẢN ĐỒ THẬT: ảnh vệ tinh Esri + đường đi thật OSRM / cung bay, camera cận điểm đi → toàn tuyến → sà điểm đến, máy bay / xe chạy theo tuyến, ảnh Resources gắn ghim; kế hoạch nháp TỰ dựng khung hành trình đặt sẵn giờ cho mọi câu di chuyển; nền tự vẽ hoặc đè thẻ lên clip phương tiện chỉ khi người dùng muốn), KỊP NHÌN (mỗi chữ đứng ≥ 1,6 s, ảnh ≥ 2 s, hiện sớm hơn lời một chút — tự sửa khi kiểm / dựng), 10 kiểu ĐỒ HOẠ CHỮ (mở đầu chữ serif lớn + viết tay vàng, từ khoá bật theo lời, CHƯƠNG 'Điểm đến 01' số viền vàng tô dần + tên in hoa, tiêu đề đoạn gradient vàng tự ngắt 2 dòng cân, ghim địa điểm rơi, chip icon, SỐ LỚN đếm lên, thẻ polaroid, bảng liệt kê kính mờ tick vàng, trích dẫn), lớp tối mềm sau chữ lớn để luôn đọc được trên nền sáng, SUB KARAOKE gom theo nghĩa (không tách từ ghép / tên riêng, ngắt ở dấu câu – chỗ ngừng), chữ đang đọc vàng; CTA cuối: avatar vòng xoay, tên kênh tích xanh, tiêu đề + viết tay, NÚT THEO DÕI gradient bóng quét + BÀN TAY bấm → 'Đã theo dõi' + chuông lắc, hàng icon Thích / Bình luận / Chia sẻ / Lưu bật lần lượt, tay bấm TIM nổ tim bay; SFX theo sự kiện, NHẠC NỀN mặc định (file nhạc trong Resources tự nhận, chỉ file người dùng đưa) −14 dB né lời, dâng ở chỗ lặng, lùi nhạc cho nốt kết trùng CTA, −14 LUFS. LUẬT CỨNG: audio tiếng gì thì MỌI CHỮ TRÊN HÌNH (sub, tiêu đề, CTA, nhãn icon, nguồn ảnh) phải đúng tiếng đó — tự nhận ngôn ngữ, tự kiểm chặn; chữ Nhật / Trung / Hàn / Thái dùng font đúng tiếng. Chạy được với MỌI chủ đề / kịch bản / Resources: tự khớp tên file Resources + chú thích ảnh bài báo với lời (cả tên viết liền, sai dấu, Whisper nghe nhầm) → nháp đặt đúng giây, khuôn kể chuyện theo kiểu câu. Whisper nhận lời → Claude viết ke_hoach.json theo NGHĨA → DỪNG 1 lần ở cổng duyệt → dựng bằng Chrome headless (khung HTML tất định, mã hoá 1 lần) → tự kiểm trên file cuối. Trigger '/TuấnJp_Dulich_ManDoc', 'làm video du lịch từ link bài báo + audio + resources', 'video quảng bá du lịch Việt', 'video giới thiệu điểm đến', 'dựng video du lịch dọc có sub, tiêu đề, CTA theo dõi', 'video travel từ bài báo'.
---

# TuấnJp_Dulich_ManDoc — video quảng bá / giới thiệu du lịch dọc 9:16

Đầu vào: **link bài báo du lịch** + **1 file giọng đọc** + **thư mục Resources** (clip / ảnh). Đầu ra: 1 video dọc
1080×1920 có footage chỉnh màu, đồ hoạ chữ du lịch cao cấp theo lời, sub karaoke, CTA theo dõi có bàn tay bấm.

- Khuôn kế hoạch (mọi trường, mọi loại đồ hoạ): **`references/ke_hoach_schema.md`**.
- Bản điền chuẩn (lần chạy thật đầu, Hà Nội 118 s): **`references/vi-du-ha-noi.json`** — đọc trước khi viết kế hoạch mới.
- Bản điền chuẩn có HÀNH TRÌNH (Incheon ✈ Nội Bài 🚗 trung tâm, Hồ Gươm → Văn Miếu; 104 s): **`references/vi-du-hanh-trinh.json`** —
  đọc khi lời có câu di chuyển A → B (mục "CÂU DI CHUYỂN" trong `goi_y.txt`).
- **BẢN CHUẨN MỚI NHẤT — KHÁCH ĐÃ DUYỆT (13/11/2026, `KịchBảnVoice_1_DLV_ban3.mp4`): `references/vi-du-hanh-trinh-ban-do-that.json`**
  — ĐỌC ĐẦU TIÊN trước khi viết kế hoạch mới; mọi video sau phải đạt mức này (mục "CHUẨN XỊN" dưới đây): hook + mở đầu tên điểm
  đến, 3 hành trình trên BẢN ĐỒ THẬT (bay / ô tô / đi bộ, ảnh sân bay gắn ghim), chương 01-02-03, bảng liệt kê, chip, montage ảnh món,
  tiêu đề đoạn đêm / mùa thu / kết, CTA; giờ đã chỉnh KỊP NHÌN.
- Bản điền chuẩn hành trình ĐÈ LÊN CLIP THẬT (`nen: "canh"`: ảnh sân bay đi → clip máy bay → thẻ ảnh sân bay đến; clip quay từ
  trong ô tô): **`references/vi-du-hanh-trinh-canh.json`** — dùng khi Resources có ảnh / clip phương tiện.
- Số phong cách: `scripts/chung.py` (khổ, vùng an toàn, sub, bảng chuyển cảnh, bảng SFX, mức nhạc, chữ CTA mặc định theo ngôn ngữ) +
  `assets/khung/dulich.css|js` (màu, phông, hình khối, chuyển động). Không rải số ra chỗ khác.
- Từ ghép tiếng Việt cho sub: `assets/tu_ghep_vi.txt` (gặp sub ngắt xấu thì thêm từ vào đây).

## Skill này được bồi thêm sau mỗi lần chạy thật

| Ngày | Video | Góp ý / sửa |
|---|---|---|
| 13/11/2026 | Hà Nội (Tuấn_jp: KịchBảnVoice.mp3 + 5 clip + vietnamtourism.gov.vn/post/67596) | bản đầu. Người dùng: "video mẫu chỉ là tham khảo, không phải quy chuẩn — làm xịn hơn"; "audio tiếng gì thì chữ trên hình bắt buộc tiếng đó — quy chuẩn của skill". Chạy thật sửa: cảnh nền bị CSS `display:none` → đen; tiêu đề dài gãy giữa chữ (khối rộng 1080 nên `scrollWidth` không đo được) → đo bằng Range + tự ngắt 2 dòng cân; chữ chìm trên trời / đường nắng → lớp tối mềm sau chữ lớn + viền sub; sub tách đôi từ ghép ("sôi / động", "Hà / Nội") → gom sub quy hoạch động + từ điển từ ghép + phạt ngắt sau hư từ; tự kiểm báo vượt vùng an toàn sai (đo cả khối) → đo phần chữ / icon thật, bỏ qua lúc đang bay vào / ra |
| 13/11/2026 | Hà Nội bản 2 — người dùng: "cũng xịn rồi, làm lại đi, tôi mới thêm ảnh Resources" (5 ảnh món: phở bò, bún chả, chả cá Lã Vọng, bánh cuốn Thanh Trì, cà phê trứng) | đoạn ẩm thực đổi từ cảnh phố + bảng liệt kê sang MONTAGE ẢNH MÓN: mỗi món 1 cảnh tràn màn đổi đúng giây đọc tên (lia / zoom xuyên, `lech_x` lấy đúng tâm món), ảnh nhỏ (cà phê 640 px) thành thẻ; tiêu đề "Món ngon Hà Nội" + chip món tích dần ở PHẦN TRÊN, món ăn chiếm giữa khung (đây là bố cục chuẩn cho đoạn liệt kê có ảnh từng mục). Sửa: quét lại Resources giữ nguyên mã `clip_NN` / `res_NN` cũ (trước đó thêm file làm lệch mã); khoá `sua_loi` phải đúng chữ Whisper ("lã" không phải "lá"); tờ soát lấy đúng khung theo số thứ tự (bộ lọc `fps` làm nhãn giây lệch nửa bước 1,25 s) |
| 13/11/2026 | Hà Nội bản 3 — người dùng: "thêm âm thanh music_Bg vào video, sau này cũng sẽ có music_bg như vậy" (bỏ `Music_Bg.mp3` 126 s vào Resources) | NHẠC NỀN thành mặc định: quét tự nhận file nhạc trong Resources (trừ file giọng, bỏ tiếng < 8 s), tự thêm vào kế hoạch đã sửa; mức −18 dB dưới giọng (trước −21, nghe chìm), dâng +10 dB ở chỗ lặng; LÙI NHẠC cho nốt kết trùng cuối video (bỏ 6 s intro); lặp nối hoà tan khi nhạc ngắn. Kèm: đọc ảnh đủ kiểu (xoay EXIF ảnh điện thoại, HEIC iPhone, AVIF, GIF, PNG trong suốt, CMYK), clip .3gp / .mts / .wmv…, +30 icon chủ đề (biển, đảo, thác, hang, ruộng bậc thang, lều, khách sạn, chợ, ẩm thực, đồ uống, giá, tuyết, mưa, ô tô, xe đạp, tàu hoả, cáp treo, balo, vali, la bàn, pháo hoa, nón lá…); quet không chạy lại Whisper khi chỉ bỏ `--ngon-ngu` |
| 13/11/2026 | Hà Nội bản 4 — người dùng: "hơi bé, cho to nhạc lên chút nữa, nhạc nền ấy" | mức nhạc chuẩn −18 → **−14 dB dưới giọng**, dâng chỗ lặng +10 → +8, thêm SAN BẰNG đoạn nhạc nhỏ (+5 dB tối đa; intro đầu video trước chìm −26 dB nay −18). Thêm lệnh `run.py tron-lai` — chỉ đổi tiếng (mức / file nhạc, SFX), giữ hình video đã dựng, ~40 s thay vì dựng lại vài phút. Tự kiểm thêm mục nhạc nền (đọc `tron_bao_cao.json`) |
| 13/11/2026 | Củng cố cho MỌI đầu vào — người dùng: "Resources có file nhạc nền thì ghép vào, không thì thôi"; "sau này tôi đưa kịch bản, resources nào cũng edit được, chuẩn chỉ và xịn xò" | Luật nhạc chốt (mục 10). **`goi_y.py`**: khớp tên file Resources + chú thích ảnh bài báo ↔ lời (không dấu, tên viết liền / camelCase, khớp gần đúng âm Việt tr/ch, gi/d, x/s… → gợi ý `sua_loi` "bún trà"→"bún chả") → `goi_y.txt`. **Kế hoạch nháp tự đặt tài nguyên khớp tên đúng giây lời nhắc** (montage tách cảnh ở từng tên), lấp phần còn lại theo bậc, ảnh nhỏ tự thành thẻ, CTA tự bắt câu kêu gọi cuối (theo dõi / follow / 구독 / フォロー…) → nháp Hà Nội qua `kiem-kh` 0 ⛔. Thẻ ảnh tự co (đáy ≤ 1295; > 1300 ⛔ vì đè sub 2 dòng), chữ đồ hoạ che ảnh thẻ → ⚠. `so_lon` không thấy trong lời / bài báo → ⚠ (hiểu "một nghìn", "a thousand"). Bài báo: lấy ảnh to nhất trong srcset, ảnh Wikimedia nâng 1280 px, bỏ bản đồ / svg / băng rôn, bỏ đuôi tên trang ở tiêu đề, bỏ đoạn lặp. **Thử audio tiếng Anh + Wikivoyage**, chữ tiếng Nhật: sub tiếng Anh dính chữ (chữ đang đọc phồng lấn khoảng trắng) → phồng ≤ 5 px mỗi bên + lề chữ; sub ngắt "grilled / pork", "old / quarter" → luật ngắt mới (thưởng ngắt TRƯỚC liên từ / giới từ, phạt đầu cụt / đuôi cụt quanh dấu phẩy, phạt dòng 1 chữ) — tiếng Việt cũng đẹp hơn; chữ Nhật / Trung / Hàn / Thái: chồng font đúng tiếng + dòng viết tay thành Gothic đậm nhỏ dưới tít (trước đè lên tít) |
| 13/11/2026 | Hà Nội kịch bản 2 (KịchBảnVoice_1.mp3: Incheon → Nội Bài ~4 tiếng rưỡi bay, Nội Bài → trung tâm 27 km ô tô 40–50 phút, Hồ Gươm → Văn Miếu 2,5 km) — người dùng: "kịch bản nói di chuyển từ A về B mất bao lâu thì vẽ icon xịn sò bay, có điểm xuất phát, điểm đến, thời gian di chuyển, bg môi trường di chuyển (trên không / đi đường); Resources có cảnh máy bay thì lấy vào ghép text, không có thì tự vẽ; sau này xe máy / ô tô, Hà Nội → Hạ Long, Hoàn Kiếm → nhà thờ… đều được" | Đồ hoạ mới **`hanh_trinh`** (mục 13): thẻ tuyến kính tối (điểm đi ●—cung vàng vẽ dần—📍 điểm đến, huy hiệu phương tiện chạy theo cung, máy bay xoay theo hướng bay, nhãn km nằm trên đường, số thời gian lớn vàng + nhãn phương tiện) trên **nền môi trường TỰ VẼ** đầy khung: `troi` máy bay chở khách to bay giữa biển mây hoàng hôn 4 lớp trôi + vệt khói; `duong` xe (ô tô / xe máy có người lái / xe khách / tàu hoả / xe đạp) chạy trên đường, bánh xoay, vạch kẻ + cọc tiêu lướt, cảnh xa `doi` / `thanh_pho` / `nui`; `bien` du thuyền buồm nâu bập bềnh giữa núi đá, sóng lớp, bọt; `ban_do` bản đồ phố tối, đường đi vàng vẽ dần, hồ vẽ đúng tại điểm là hồ; `canh` chỉ thẻ đè lên clip phương tiện có sẵn trong Resources. SFX tự tổng hợp (`tao_sfx_ht.py`: phản lực lướt qua, xe chạy, sóng nước). Kiểm: số giờ / km phải có trong lời ("rưỡi" = 30), giờ xe chạy / tới / hiện số đúng thứ tự. Kèm: SFX CTA trước chỉ kêu khi có nhạc nền (thụt lề sai) → sửa; `ke_hoach.json` lưu có BOM (Notepad / PowerShell 5.1) không còn lỗi đọc; Whisper tách "2 ,5" → ghép lại khi soát số; `goi_y` ghép nhầm ảnh "Hoàng thành Thăng Long… của Thủ đô" vào «của thủ đô» → bỏ khớp chú thích mà mọi từ thực chỉ thuộc cụm nhắc ≥ 4 lần ("thủ đô", "Hà Nội"). Người dùng: "ô tô bị ngược à" → vẽ lại xe đầu hướng PHẢI (nắp capô dài phía trước), nhãn km cách cung ≥ 50 px → bản 2. "Cập nhật hết vào skill để test" → **tự dò câu di chuyển** (`chung.cau_di_chuyen`: số + km / phút / tiếng / 時間 / 시간 / 小时… + từ đi lại, bỏ giờ mở cửa "từ 8 giờ", "dài 5 km"; đoán phương tiện, "sân bay" không tính là bay, "Bay" tiếng Anh = vịnh) → mục CÂU DI CHUYỂN trong `goi_y.txt` + ⚠ ở `kiem-kh`, `bo_di_chuyen` để bỏ câu dò nhầm; mẫu `references/vi-du-hanh-trinh.json` |
| 13/11/2026 | TEST skill: KịchBảnVoice_1 + Resources thêm `Video_máybay.mp4`, ảnh `sân bay incheon.jpg` / `sân bay nội bài.jpg`, KHÔNG link bài báo — người dùng "duyệt, dựng luôn" | Tự dò bắt đúng 4 câu di chuyển; `goi_y` đặt ảnh sân bay + clip máy bay đúng câu. Lần đầu dựng `nen: "canh"`: chặng bay = ảnh sân bay Incheon → clip máy bay trên trời → thẻ ảnh Nội Bài (`the_y` 1010 ngay dưới thẻ tuyến); chặng ô tô = clip quay từ trong xe chạy trên phố. Tự kiểm 12/12. Mẫu `references/vi-du-hanh-trinh-canh.json`. Thấy: tên file "sân bay incheon" khớp vào cụm chung «sân bay» (Whisper chèn "quốc tế" ở giữa) — đặt cảnh theo câu có TÊN RIÊNG |
| 13/11/2026 | KịchBảnVoice_1 (giọng Việt) — người dùng: "làm 1 video sub thì là tiếng Hàn, giọng đọc vẫn là Việt Nam" → duyệt, dựng | Chế độ **SUB DỊCH** (ĐÃ CHỐT 1 ngoại lệ): `chu_ngon_ngu` tách tiếng CHỮ khỏi tiếng GIỌNG (`ngon_ngu`); lệnh `run.py sub-dich` tạo khung `sub_dich` theo cụm lời gốc; `kiem-kh` soát chữ Hàn / độ dài dòng (em) / cụm < 0,6 s / chồng cụm / lời chưa có sub; karaoke ước lượng theo nhịp lời gốc (`sub.karaoke_dich: false` tắt); hành trình, CTA (팔로우 / 팔로잉 / 좋아요…), nguồn ảnh theo tiếng chữ; tự dò câu di chuyển vẫn theo tiếng giọng. 48 cụm sub Việt gộp theo nghĩa còn 32 cụm Hàn 1–2 dòng. Mẫu `references/vi-du-sub-dich-ko.json` |
| 13/11/2026 | KịchBảnVoice_1 bản tiếng Hàn — khách góp ý: "di chuyển máy bay hay ô tô thì kiểu dạng bản đồ map thực" → cập nhật skill, làm lại | Nền **`that` = BẢN ĐỒ THẬT** thành MẶC ĐỊNH cho mọi hành trình (`ban_do_that.py`): ảnh vệ tinh Esri + đường đi thật OSRM (Nội Bài → Hoàn Kiếm 26,7 km khớp lời 27 km; Hồ Gươm → Văn Miếu đi bộ 2,6 km) + cung bay Incheon → Nội Bài 2 684 km; camera từng khung tính sẵn (cận điểm đi z≈12 → lùi toàn tuyến → sà điểm đến), ô ảnh nạp theo khung (trang dựng chờ decode rồi vẽ canvas, nhả ô cũ). Ảnh Resources sân bay gắn ghim điểm đi / đến; tên nước (`diem_phu`) hiện lúc nhìn toàn tuyến; km trên tuyến. Sửa sau khi soi: máy bay ra khỏi khung lúc camera còn lùi → lùi TRƯỚC lúc rời bến 0,7 s; ảnh điểm đến đặt dưới ghim đè sub → đặt CẠNH ghim; nhãn km trôi lên mép thẻ lúc sà vào → ẩn khi tới / khi điểm neo ra khỏi vùng; ảnh Hà Nội mờ tối → sáng .96. Lệnh mới `run.py tim "<tên>"`. Ảnh vệ tinh Esri có chỗ ghép ảnh khác màu trên biển (dữ liệu thật, không phải lỗi dựng) |
| 13/11/2026 | KịchBảnVoice_1 bản tiếng Việt bản đồ thật (ban2) — khách: "hình chưa hiển thị lên là bị tắt rồi, hiện trước 1 chút cũng được, ví dụ ảnh sân bay Nội Bài và vài cảnh khác — chưa kịp nhìn đã mất" → làm lại (ban3) | Luật **KỊP NHÌN** (ĐÃ CHỐT 6): mục chữ ≥ 1,6 s, ảnh ≥ 2 s, hiện SỚM hơn lời được. Rà cả video: ảnh Nội Bài gắn ghim chỉ 1,0 s (hiện lúc tới nơi 11,2 s, bản đồ tắt 12,2 s) → ảnh + tên điểm đến hiện từ `luc_ten_den` (chữ "hạ cánh tại…" 10,6 s) tới `den` − 0,3 = 2,15 s; ghim Văn Miếu đứng 0,6 s → 1,85 s; dòng "Đền Ngọc Sơn", chip "Cửa hàng truyền thống" / "Văn hóa lâu đời" / "Không khí nhộn nhịp" / "Se lạnh" đứng 0,5–1,0 s → ≥ 1,6 s (hiện sớm 0,3–0,7 s + kéo `den`); "Nhịp sống đặc trưng" 1,4 s → 2,1 s; ảnh phở 1,8 s → 2,4 s (vào sớm 0,6 s). `kiem-kh` tự đẩy mục cuối của chip / liệt kê / từ khoá sớm lên cho đủ 1,6 s + ⚠ mọi chỗ còn ngắn |
| 13/11/2026 | Khách duyệt ban3: "OK, được rồi — update vào hết skill, sau này Resources và kịch bản nào cũng ra XỊN như này" | `vi-du-hanh-trinh-ban-do-that.json` = BẢN CHUẨN khách duyệt (đọc đầu tiên) + mục **CHUẨN XỊN** (8 điểm soát). **Kế hoạch nháp tự dựng khung `hanh_trinh` bản đồ thật** cho mọi câu di chuyển (thử lại `quet` từ đầu với KịchBảnVoice_1: ra đúng 3 chuyến, giờ `luc_di` / `luc_den` / `luc_tg` / `luc_kc` lệch bản chỉnh tay ≤ 0,7 s, "~4h30" / "~27 km" / "~40–50 phút" / "~2,5 km", ảnh Incheon + Nội Bài tự gắn ghim h1). Sửa khi thử: "ba" khớp nhầm đầu chữ "bay" (thêm ranh từ), "bay" trong "sân bay" / "máy bay" không phải lúc rời bến. **KỊP NHÌN tự sửa** (🔧) ở `kiem-kh` / `dung`: kéo `den` vào chỗ trống, tới nơi sớm, ảnh vào sớm — kế hoạch tiếng Hàn cũ (chưa chỉnh tay) tự hết 6 ⚠; bản Việt đã chỉnh giữ nguyên |

## ĐÃ CHỐT (không tự đổi trừ khi người dùng yêu cầu)

1. **NGÔN NGỮ (luật cứng):** audio nói tiếng gì thì MỌI chữ trên hình — sub, chữ đồ hoạ, CTA, nhãn icon, dòng nguồn ảnh — đúng tiếng đó.
   `quet` tự nhận ngôn ngữ (Whisper) → `ke_hoach.ngon_ngu`; `kiem-kh` ⛔ khi `ngon_ngu` khác ngôn ngữ audio hoặc chữ nào sai chữ viết
   (Hàn / Nhật / Trung / Thái / Nga / Latin) hay thiếu dấu tiếng Việt; chữ CTA mặc định lấy từ `NGON_NGU` trong `chung.py`.
   Bài báo tiếng khác audio → DỊCH chữ đồ hoạ sang tiếng của audio, không chép nguyên.
   **Ngoại lệ — SUB DỊCH (người dùng chốt 13/11/2026):** CHỈ khi người dùng NÓI RÕ muốn chữ / sub tiếng khác giọng (vd "giọng Việt,
   sub tiếng Hàn" cho khách Hàn) → `run.py sub-dich --work <dir> --ngon-ngu ko` thêm `chu_ngon_ngu: "ko"` + khung `sub_dich`
   (cụm lời gốc + giây, chữ dịch trống). Khi đó MỌI chữ trên hình (sub, đồ hoạ, hành trình, CTA, nguồn ảnh) theo `chu_ngon_ngu`,
   `ngon_ngu` vẫn = tiếng giọng. Dịch theo NGHĨA: gộp cụm lời gốc thành câu trọn ý (tiếng đích đảo trật tự từ — đừng dịch từng mảnh
   0,7 s), mỗi cụm 1–2 dòng (ngắt bằng " / "), ≤ ~14,6 em / dòng (Hàn / Nhật / Trung ≈ 13–14 chữ). Tên riêng theo cách gọi quen của
   người đọc đích (Hàn: 호안끼엠 호수, 문묘 국자감, 분짜, 반미, 에그커피; 還劍 = 환검). Số giữ đúng như lời. Chữ vàng karaoke chạy
   ƯỚC LƯỢNG theo nhịp lời gốc (trật tự từ khác nên không khớp từng chữ) — người dùng muốn chữ đứng yên: `sub.karaoke_dich: false`.
   Mẫu: **`references/vi-du-sub-dich-ko.json`**.
2. Video mẫu `D:\____TTT_____\KH_Test\Tuấn_jp\Video_Mẫu.mp4` chỉ là tham khảo. Chuẩn là phong cách của skill này (mục 3–9).
3. Khổ 1080×1920, 30 fps, hết 0,9 s sau tiếng cuối (+ đủ dài cho CTA). Footage: cắt 9:16, lanczos, tăng tương phản / bão hoà nhẹ,
   ấm vùng sáng, làm nét nhẹ; lớp màu ấm soft-light + tối mép + tối trên / dưới + hạt phim; mỗi cảnh Ken Burns (zoom 1,00→1,10 hoặc lia).
4. Chuyển cảnh theo `CHUYEN` trong `chung.py`: hoa_tan 0,45 · nhoe 0,5 · lia 0,36 · lia_doc · zoom 0,42 · loe 0,55 (loé nắng) · truot 0,40 · cat.
   Đổi kiểu liên tục, không lặp 1 kiểu 3 lần liền; cảnh mở đầu dùng `loe`.
5. Phông: Playfair Display (chữ khoá serif) · Great Vibes / Dancing Script (viết tay) · Be Vietnam Pro (sans, sub, nhãn) · Anton / Montserrat
   (số, phụ). Bảng màu: vàng `#F4C66A` + gradient vàng, kem `#FFF6E6`, đỏ nút `#FE2C55`. Chữ khoá dài tự ngắt 2 dòng cân rồi mới co.
   Chữ không Latin dùng font Windows đúng tiếng (`FONT_NN` trong `dulich.js`: ja Yu Gothic / Meiryo, zh Microsoft YaHei, ko Malgun Gothic,
   th Leelawadee UI); với ja / zh / ko / th không có font viết tay → dòng "viết tay" thành Gothic đậm ×0,58, nằm DƯỚI tít, nghiêng −2° (lớp `phi_latin`).
6. Đồ hoạ: mỗi cụm ý tối đa 1 đồ hoạ LỚN; `ghim` / `chip` (nhỏ) được chồng thời gian với 1 đồ hoạ lớn. Mỗi đồ hoạ ≥ 1,2 s. Chữ đồ hoạ
   TÓM TẮT 1–6 chữ, chữ khoá là chữ đắt nhất của lời. Đồ hoạ lớn có lớp tối mềm phía sau (luôn đọc được trên nền sáng).
   **KỊP NHÌN (người dùng chốt 13/11/2026: "hình chưa hiển thị lên đã bị tắt, chưa kịp nhìn — hiện trước 1 chút cũng được"):**
   mỗi mục chữ / chip / dòng liệt kê / tên điểm đến đứng **≥ 1,6 s** trước khi tắt (`HIEN_MIN`), ảnh (cảnh ảnh, ảnh gắn ghim hành
   trình) **≥ 2 s** (`HIEN_ANH`), đồ hoạ lớn nên ≥ 2 s. Cách sửa theo thứ tự: cho hiện SỚM hơn lời 0,3–0,8 s (được phép) → kéo `den`
   tới sát đồ hoạ / cảnh sau → bớt mục. **`kiem-kh` / `dung` TỰ SỬA (dòng 🔧, không ghi đè `ke_hoach.json`):** kéo `den` đồ hoạ vào
   chỗ trống (không chạm đồ hoạ cùng lớp kế tiếp / CTA, tối đa +1,2 s); mục cuối chip / liệt kê / từ khoá hiện sớm cho đủ 1,6 s (giữ
   thứ tự); hành trình: kéo `den` (≤ +0,8 s) rồi cho tới nơi sớm hơn để ghim điểm đến đứng ≥ 1,5 s, ảnh + tên điểm đến hiện sớm cho đủ
   2 s; cảnh ảnh < 2 s vào SỚM hơn (lấy bớt cảnh trước còn dư, ≤ 0,8 s). Còn ngắn sau khi tự sửa → ⚠ (mục < 1,2 s, ảnh < 2 s, đồ
   hoạ lớn < 2 s, tới nơi < 1,5 s) — Claude sửa tay. Cảnh nằm dưới nền hành trình che kín thì không tính.
7. Sub karaoke: Be Vietnam Pro 700 60 px trắng viền tối, tâm y 1405, ≤ 2 dòng × 30 ký tự, chữ đang đọc vàng `#FFC845` phồng nhẹ
   (mỗi bên nở ≤ ~5 px — từ dài không lấn sang từ bên cạnh). Gom cụm bằng quy hoạch động: ngắt ở dấu câu / chỗ ngừng ≥ 0,38 s,
   ưu tiên ngắt TRƯỚC liên từ / giới từ (`TU_TRUOC`: và, với, nhưng, khi… / and, with, of, where…), KHÔNG tách từ ghép
   (`tu_ghep_vi.txt`, chữ đồ hoạ, tên trong `sua_loi`, `sub.giu_lien`) hay tên riêng viết hoa, phạt ngắt ngay sau hư từ (một, những, the, a…),
   phạt đầu cụt ("old / quarter,") và đuôi cụt ("pho, grilled /") quanh dấu câu, phạt dòng chỉ 1 chữ. Sửa lỗi Whisper bằng `sua_loi`.
8. Vùng an toàn: chữ trong y 150–1640, x 60–1020; chip mặc định đáy y 1292 (ngay trên sub); sub không bao giờ đè đồ hoạ (⛔ tự kiểm).
   Thẻ ảnh (`khung: "the"`): tâm `the_y` 820, bề rộng tự co để đáy ≤ 1295 (đáy > 1300 ⛔ — sub 2 dòng cao tới y ≈ 1330, thẻ lắc ±20 px);
   chữ đồ hoạ che ảnh thẻ quá 40 px → ⚠ tự kiểm (dời `y` chữ hoặc `the_y`).
9. CTA ≥ 3,8 s ở cuối: nền nhoè 16 px + tối; avatar (ảnh kênh hoặc chữ cái) vòng gradient xoay; tên kênh + tích xanh + @handle; tiêu đề serif +
   viết tay vàng; nút Theo dõi đỏ gradient có bóng quét + sóng → bàn tay bấm (`luc_bam` = cta.tu + 1,9 s) → "Đã theo dõi" + chuông lắc;
   icon Thích / Bình luận / Chia sẻ / Lưu bật lần lượt; tay bấm tim (`luc_tim` = luc_bam + 1,35 s) → tim đỏ + tim bay; Lưu tô vàng.
10. Âm thanh: chỉ giọng của file audio (tiếng clip bỏ hết) + **NHẠC NỀN MẶC ĐỊNH** (người dùng chốt 13/11/2026: "sau này cũng có
    music_bg"): file nhạc nằm trong Resources (vd `Music_Bg.mp3`; nhiều file âm thanh thì lấy file tên kiểu music / bg / bgm / nhac / beat…)
    hoặc `--nhac` → tự dùng, không phải hỏi. Nhạc **−14 dB dưới giọng** (cả bài; người dùng chê −18 "hơi bé"), **dâng +8 dB** ở khoảng lặng ≥ 1 s,
    **san bằng**: đoạn nhạc nhỏ (intro / outro / bridge) nâng tối đa +5 dB cho nghe rõ suốt video (4 s cuối giữ nguyên nốt kết);
    **lùi nhạc**: nhạc dài hơn video ≤ 45 s thì bỏ bớt ĐẦU để nốt kết của bài trùng cuối video (CTA kết cùng nhạc, không cắt ngang),
    dài hơn nữa thì giữ đầu + mờ dần 2,5 s cuối; ngắn hơn video thì lặp nối hoà tan 1,5 s; tự bỏ lặng đầu / cuối file nhạc.
    **LUẬT: Resources CÓ file nhạc nền → ghép vào; KHÔNG có → thôi** (giọng + SFX, không hỏi, không nhắc). Chỉ dùng file người dùng
    đưa (không tự tổng hợp nhạc); file giọng đọc khác để lẫn trong Resources (tên voice / giọng / kịch bản…) không bị lấy làm nhạc;
    nhiều file nhạc không rõ → lấy file dài nhất và báo ở D2; cố ý tắt nhạc: `"nhac": false`; SFX theo bảng `SFX` (whoosh ở chuyển lia / zoom, pop ở ghim / chip / dòng liệt kê, riser + ding ở số lớn,
    click ở nút…), 2 tiếng cách ≥ 0,22 s. Master **−14 LUFS, đỉnh ≤ −1 dBTP** đo trên file AAC cuối.
11. Không bịa: số liệu / tên / năm trên hình chỉ lấy từ lời hoặc bài báo (`so_lon` không thấy số trong lời / bài báo → ⚠; số đọc bằng
    chữ "một nghìn" / "a thousand" / "千" được chấp nhận). Ảnh bài báo luôn kèm dòng nguồn ("Ảnh: <tên miền>").
12. Không ghi đè video cũ: `<audio>_DLV.mp4`, có rồi thì `_DLV_ban2`…
13. **HÀNH TRÌNH (người dùng chốt 13/11/2026):** lời nói DI CHUYỂN từ A tới B (kèm thời gian / quãng đường / phương tiện: "bay khoảng
    4 tiếng rưỡi từ Incheon tới Nội Bài", "đi ô tô 27 km, 40–50 phút", "từ Hà Nội về Hạ Long", "từ Hoàn Kiếm ra Nhà thờ Lớn mất 5 phút đi bộ")
    → BẮT BUỘC 1 đồ hoạ `hanh_trinh` phủ trọn câu đó (lời không nói di chuyển thì KHÔNG tạo). Có: điểm đi + điểm đến (tên ngắn ≤ 26 ký tự,
    phần phụ vào `phu`), phương tiện, thời gian và / hoặc khoảng cách ĐÚNG như lời (không bịa; "~" khi lời nói "khoảng").
    **Nền MẶC ĐỊNH = BẢN ĐỒ THẬT `nen: "that"` (khách chốt 13/11/2026: "di chuyển máy bay hay ô tô thì kiểu bản đồ map thực"):**
    ảnh vệ tinh Esri thật (cache chung `_cache_tiles\esri`) + ĐƯỜNG ĐI THẬT (ô tô / xe máy / xe buýt → OSRM, đi bộ → OSRM foot,
    xe đạp → OSRM bike, máy bay → cung bay đường tròn lớn phồng nhẹ, tàu → cung thấp) + camera bay: cận điểm đi (ảnh `anh` gắn
    trên ghim) → lùi ra toàn tuyến TRƯỚC lúc rời bến 0,7 s (phương tiện luôn trong khung) → máy bay bay / xe chạy, vạch vàng vẽ dần
    → sà vào điểm đến, ghim rơi + vòng toả + ảnh điểm đến đặt CẠNH ghim (dưới ghim sẽ đè sub). Thẻ tuyến gọn ở trên (tên đi → tên
    đến, số thời gian), km nằm trên tuyến lúc đọc số km. BẮT BUỘC `toa_do: [lat, lon]` cho `xuat_phat` + `diem_den`
    (`run.py tim "<tên>"` — Nominatim, cần mạng; lấy điểm cụ thể: sân bay = aerodrome, đền / di tích = cổng / vé; "trung tâm
    thành phố" = quận trung tâm, điểm dừng ngay sau). Tuỳ chọn: `anh` (res_XX / bai_XX gắn ghim), `diem_phu` [{ten, toa_do}] (tên
    nước / thành phố hiện lúc nhìn toàn tuyến, viết đúng tiếng chữ — đặt xa nhãn ghim), `duong` (`o_to` / `di_bo` / `xe_dap` /
    `cung` / `cung_thap` / `thang`), `zoom_gan`. `duyet` / `dung` tự tải ô ảnh + đường (cần mạng; in "đường thật ≈ X km" — lệch
    xa số trong lời thì kiểm lại toạ độ). Không có toạ độ → ⚠ và lùi về nền tự vẽ dưới đây.
    Nền KHÁC chỉ khi người dùng yêu cầu: Resources có clip đúng phương tiện → `nen: "canh"` (thẻ tuyến đè lên clip);
    TỰ VẼ: máy bay → `troi`, ô tô / xe máy / xe khách / tàu hoả / xe đạp → `duong` (`canh_xa`: `thanh_pho` khi đi vào / ra
    thành phố, `nui` cho Hạ Long / Ninh Bình / Hà Giang, `doi` mặc định), thuyền → `bien`, đi bộ / quãng ngắn trong phố / không rõ
    phương tiện → `ban_do`. Giờ: tên điểm đi hiện lúc đọc tên đó, phương tiện CHẠY từ lúc đọc "di chuyển / bay…" (`luc_di`) tới lúc đọc
    tên điểm đến (`luc_den` ≈ giây chữ đến tên — hoặc sớm hơn ở chữ "hạ cánh / tới…" cho ghim đứng ≥ 1,5 s trước `den`), số thời gian
    bật đúng giây đọc số (`luc_tg`), km nằm trên đường lúc đọc số km (`luc_kc`). Bản đồ thật: `luc_ten_den` = lúc tên + ảnh điểm đến
    hiện (mặc định `luc_den`; đặt sớm ở chữ "hạ cánh tại…" để ảnh đứng ≥ 2 s), ảnh điểm đi đứng từ `tu` + 0,45 tới `luc_di`.
    Thẻ ở y 180 (trên), phương tiện to giữa khung, sub vẫn đọc được (dải tối dưới). Nền tự vẽ che hết footage → cảnh dưới chỉ để nối chuyển.
    **Tự dò:** `quet` liệt kê mọi câu có số + km / phút / tiếng / giờ (mọi ngôn ngữ) + từ di chuyển ở mục "CÂU DI CHUYỂN" cuối
    `goi_y.txt` (kèm phương tiện đoán + câu trước để tìm điểm đi); `kiem-kh` báo ⚠ câu di chuyển chưa có `hanh_trinh` phủ.
    **Kế hoạch NHÁP tự dựng khung `hanh_trinh` (`quet.nhap_hanh_trinh`) cho mỗi chuyến:** `nen: "that"`, gộp câu km + câu thời gian
    liền nhau, lấy cả câu trước nói điểm xuất phát ("bắt đầu từ…"), đặt sẵn `tu` / `den` / `luc_di` (chữ di chuyển / số đầu câu) /
    `luc_den` (chữ "hạ cánh / đến…" + 0,6 s) / `luc_tg` / `luc_kc` (giây chữ số), phương tiện đoán, `thoi_gian` / `khoang_cach` đúng lời
    ("4 tiếng rưỡi" → "~4h30", "~" khi lời nói "khoảng"), ảnh Resources có TÊN RIÊNG đọc trong câu ("sân bay nội bài.jpg" ↔ "…quốc tế
    Nội Bài") gắn điểm đi / đến. CHỪA TRỐNG tên + `toa_do` → `kiem-kh` ⛔ tới khi Claude điền (tên ngắn, `run.py tim "<tên>"`,
    `diem_phu` khi bay xa). Câu dò nhầm
    (không phải đi lại, vd "nấu 8 tiếng") → xoá khung nháp đó + ghi giây câu vào `bo_di_chuyen: [12.3]` cho hết ⚠. Mẫu đủ 3 kiểu (trời / đường / bản đồ):
    **`references/vi-du-hanh-trinh.json`** (nền tự vẽ); BẢN ĐỒ THẬT (mặc định): **`references/vi-du-hanh-trinh-ban-do-that.json`** (h1 bay, h2 ô tô, h3 đi bộ — toạ độ, ảnh gắn ghim, `diem_phu`).
    **Nền `canh` (có tư liệu thật):** cảnh dưới thẻ nối theo lời — ảnh / clip ĐIỂM ĐI (tràn) → clip PHƯƠNG TIỆN (máy bay trên trời, xe
    chạy…) → ảnh ĐIỂM ĐẾN dạng thẻ `the_y` ≈ 1010 (thẻ tuyến cao tới y ≈ 740, thẻ ảnh nằm ngay dưới, đáy ≤ 1295). Clip quay từ TRONG
    xe / dashcam / cửa sổ máy bay cũng là clip phương tiện. Chọn đoạn clip có phương tiện nằm DƯỚI y 760 (thẻ tuyến che phần trên).
    Mẫu: **`references/vi-du-hanh-trinh-canh.json`**.

## Khuôn kể chuyện du lịch — áp cho MỌI chủ đề / ngôn ngữ / Resources

Kịch bản du lịch nào cũng gồm các KIỂU CÂU dưới đây (thành phố, biển đảo, núi, lễ hội, resort, ẩm thực, tour nước ngoài…). Đọc
`loi_doc.txt`, gán mỗi câu 1 kiểu, rồi lấy đồ hoạ + cảnh theo bảng — đừng chép giây của ví dụ Hà Nội, chép CÁCH LÀM.

| Kiểu câu trong lời | Đồ hoạ | Cảnh / chuyển | Ghi chú |
|---|---|---|---|
| Hook mở (câu hỏi, "nếu bạn đang tìm…") 0–5 s | `tu_khoa` 2–4 từ bật đúng giây đọc (từ đầu kiểu `tay`) | cảnh đẹp nhất (flycam, toàn cảnh), `loe`; câu dài thì 2 cảnh | chưa nói tên điểm đến thì chưa hiện tên |
| Lần đầu gọi tên điểm đến | `mo_dau`: `tren` "Khám phá" / "Welcome to" / "ようこそ", `chinh` = TÊN, `viet_tay` = câu định danh trong lời, `duoi` = nước / tỉnh | toàn cảnh, `zoom` | 1 lần / video |
| Con số (năm, km, mét, số đảo…) | `so_lon` (`dem_tu` = giây đọc số) | cảnh liên quan, giữ nguyên | số phải có trong lời / bài báo |
| Di chuyển A → B (bay / đi xe / đi thuyền / đi bộ, mất bao lâu, bao xa) | **`hanh_trinh`** phủ trọn câu (mục 13) | **BẢN ĐỒ THẬT** `nen: "that"` (vệ tinh + đường đi thật, `toa_do` 2 điểm, ảnh Resources của điểm đi / đến gắn ghim); nền tự vẽ / `canh` chỉ khi người dùng muốn | 2 câu liền (km rồi thời gian) gộp 1 hành trình; km câu sau "cách X khoảng 2,5 km" cũng là hành trình |
| 2–3 đặc điểm ngắn nói liền | `chip` (đáy y 1292) hoặc `tu_khoa` | cảnh minh hoạ chung | icon theo nghĩa (`ICON_HOP_LE`) |
| Mở 1 địa điểm / mục lớn | `chuong` đánh số 01, 02… (`ten` = tên, `phu` = mô tả ngắn từ lời) | tài nguyên KHỚP TÊN (`goi_y.txt`) hoặc ảnh bài báo dạng thẻ (`chuong` y ≈ 190) | + `ghim` khi lời nói vị trí ("nằm giữa…") |
| 2–6 thứ quanh 1 điểm (cầu, đền, bãi…) | `liet_ke` bảng kính, `luc` = giây đọc từng mục | 1 cảnh nền | có ảnh từng mục → montage (dòng dưới) |
| Liệt kê CÓ ảnh từng mục (món ăn, đảo, homestay…) | `tieu_de` trên (y ≈ 285) + `chip` y ≈ 440 tích dần | MONTAGE: 1 ảnh / mục đổi đúng giây đọc tên, ảnh nhỏ làm thẻ dưới chip | cảnh ≥ 1,2 s |
| Ý chính / chuyển đoạn ("thiên đường ẩm thực", "về đêm", "mùa thu") | `tieu_de` (`dan` + `khoa` + `viet_tay`); cảnh đêm `mau: "trang"` | cảnh mở đoạn, `nhoe` khi ngày → đêm, `lia` / `truot` khi cùng mạch | 1 đồ hoạ lớn / 4–8 s, không quá 10 s trống chữ |
| Cảm nhận / trích dẫn ("thơ mộng và lãng mạn") | `tu_khoa` (từ cuối kiểu `tay`) hoặc `trich` | cảnh chậm (`toc_do` 0,8) | |
| Câu kết trước CTA | `tieu_de` `co` 190, `khoa` = tên điểm đến, `viet_tay` = ý cuối | cảnh đẹp nhất còn lại, `loe` | kết đúng trước CTA |
| Kêu gọi theo dõi | CTA (`cta.tu` = đầu câu kêu gọi; nháp tự bắt) | cảnh chậm `toc_do` 0,5–0,6 | chữ CTA đúng tiếng audio |

Chọn footage: tên riêng → tài nguyên khớp tên / chú thích (đặt đúng giây); câu chung → cảnh đẹp CHƯA dùng (clip dài thì cắt nhiều đoạn
khác nhau, soi tờ khung); lời về đêm → cảnh đêm; không có gì khớp → ảnh bài báo dạng thẻ hoặc cảnh chung + chữ (báo ở D5).
Tên file tiếng khác audio (file "Phở bò.jpg", audio tiếng Anh "beef pho") thì `goi_y` không khớp được — Claude tự ghép theo nghĩa.
Tên riêng trên hình theo tiếng của audio: tiếng Anh dùng tên quốc tế không dấu ("Hoan Kiem Lake"), tiếng Nhật katakana / kanji quen
("ホアンキエム湖"); tên riêng tiếng Việt có dấu trong video tiếng khác → `kiem-kh` ⚠ (tên riêng thì được), cả cụm tiếng Việt → ⛔.

## CHUẨN XỊN — mức bản khách duyệt, MỌI kịch bản / Resources phải đạt

Soát kế hoạch theo danh sách này trước cổng duyệt (mẫu: `references/vi-du-hanh-trinh-ban-do-that.json`, video
`D:\____TTT_____\KH_Test\Tuấn_jp\KịchBảnVoice_1_DLV_ban3.mp4`):

1. **Không khoảng trống chữ > 8–10 s**: mỗi câu có 1 đồ hoạ khớp nghĩa (hook → `mo_dau` tên điểm đến → `chuong` 01/02/03 cho mỗi
   địa điểm → `liet_ke` / `chip` cho thứ được kể → `tieu_de` cho ý chuyển đoạn (đêm, mùa, ẩm thực) → `tieu_de` kết → CTA).
2. **Mọi câu di chuyển = hành trình BẢN ĐỒ THẬT** (khung nháp đã có — điền tên ngắn + toạ độ; ảnh Resources của điểm đi / đến gắn ghim;
   bay xa thêm `diem_phu` tên nước); thời gian / km đúng lời.
3. **Footage khớp nghĩa từng cụm lời**: tên riêng → tài nguyên khớp tên đúng giây; liệt kê có ảnh từng mục → MONTAGE đổi đúng giây
   đọc tên; lời về đêm → cảnh đêm; không lặp đoạn clip.
4. **KỊP NHÌN**: chữ ≥ 1,6 s, ảnh ≥ 2 s, đồ hoạ lớn ≥ 2 s; hiện sớm hơn lời 0,3–0,8 s được (tự sửa 🔧 — còn ⚠ thì sửa tay).
5. Chuyển cảnh đổi kiểu liên tục (`loe` mở đầu, `nhoe` ngày → đêm, `lia` / `truot` cùng mạch, `zoom` vào địa điểm mới).
6. Sub karaoke không tách từ ghép / tên riêng (`sua_loi` mọi tên Whisper nghe sai); MỌI chữ đúng tiếng của audio (hoặc tiếng người
   dùng yêu cầu — sub dịch).
7. Nhạc nền trong Resources tự ghép (−14 dB dưới giọng, lùi nhạc cho nốt kết trùng CTA); SFX theo sự kiện; −14 LUFS.
8. Trước khi giao: `run.py khung --times …` soi gần các chỗ hành trình / liệt kê / montage, tự kiểm ĐẠT hết, mở `soat.jpg`.

## Quy trình

Mọi lệnh: `python -I -X utf8 .claude\skills\TuấnJp_Dulich_ManDoc\scripts\run.py <lệnh> …` (chạy từ `D:\____TTT_____\SON_AI_VIDEO`;
đầu phiên PowerShell `[Console]::OutputEncoding=[Text.Encoding]::UTF8; $env:PYTHONUTF8='1'`). Cần Node ≥ 22 + Chrome / Edge
(biến môi trường `DLV_CHROME` nếu Chrome nằm chỗ lạ), ffmpeg full, faster-whisper.

1. **Quét** (cần mạng cho bài báo):
   `run.py quet --audio "<giọng>" --link "<link bài báo>" --res "<thư mục Resources>" [--nhac "<nhạc>"] [--ngon-ngu vi]`
   (file nhạc nền để luôn trong Resources là tự nhận — không cần `--nhac`; kế hoạch đã sửa mà chưa có nhạc thì quet thêm `nhac` vào)
   → thư mục `<audio>_dlv_work\`: `loi.json` + `loi_doc.txt` (lời + giây từng từ, có cache), `bai_bao\` (`bai_bao.txt`, `anh\bai_NN.jpg`),
   `khung\clip_NN.jpg` (tờ khung có nhãn giây từng clip), `tai_nguyen.jpg`, `goi_y.txt` (tài nguyên ↔ lời), `ke_hoach.json` NHÁP
   (`CAN_CLAUDE_SUA: true`). Nháp đã: đặt tài nguyên KHỚP TÊN đúng giây lời nhắc (câu nhắc nhiều thứ → tách cảnh từng thứ), lấp cảnh còn
   lại theo bậc (clip chưa dùng → ảnh chưa dùng → đoạn clip mới…), ảnh cần phóng > 2× thành thẻ, `sua_loi` gợi ý, CTA ở câu kêu gọi cuối,
   **khung `hanh_trinh` BẢN ĐỒ THẬT cho mọi câu di chuyển** (giờ + số + ảnh gắn ghim đặt sẵn, chừa tên + toạ độ — mục 13).
   Không truyền `--ngon-ngu` → tự nhận; nhận sai thì chạy lại với `--ngon-ngu`.
2. **Claude đọc & viết kế hoạch:** đọc `goi_y.txt` trước (KHỚP RIÊNG = giữ đúng giây; GỢI Ý SỬA LỜI = kiểm rồi đưa vào `sua_loi`;
   KHÔNG KHỚP = tự ghép theo nghĩa; CÂU DI CHUYỂN = mỗi chuyến 1 `hanh_trinh`, mục 13), rồi `loi_doc.txt` + `bai_bao\bai_bao.txt`; MỞ `tai_nguyen.jpg`, MỌI `khung\clip_NN.jpg`, MỌI ảnh
   `bai_bao\anh\*.jpg` (chú thích ảnh do script đoán từ đoạn văn kế bên — chỉ là gợi ý, phải nhìn ảnh). Viết `ke_hoach.json` theo NGHĨA
   (mẫu CHUẨN `references/vi-du-hanh-trinh-ban-do-that.json` — bản khách duyệt; thêm `references/vi-du-ha-noi.json`; khuôn
   `references/ke_hoach_schema.md`; cách gán đồ hoạ theo kiểu câu: mục "Khuôn kể chuyện" ở trên; soát lại theo mục "CHUẨN XỊN"):
   - `canh`: mỗi cụm lời 1 cảnh khớp nghĩa (2,5–6 s, ≥ 1,2 s), đổi cảnh ở đầu cụm lời; đoạn clip nét, không lặp đoạn đã dùng, tránh khung
     xấu (che mặt, rung, lia nhanh); ảnh bài báo nhỏ (< 1080 ngang) dùng `khung: "the"`.
   - `do_hoa`: chữ tóm tắt, xuất hiện đúng giây lời nhắc (mục liệt kê / chip / từ khoá đặt `luc` = giây đọc chữ đó).
   - `sua_loi`: sửa mọi tên riêng / chữ Whisper nghe sai.
   - `kenh`, `cta`, `nhac` theo người dùng; chưa biết thì để trống và hỏi ở cổng duyệt. Xong đặt `CAN_CLAUDE_SUA: false`.
   - Người dùng muốn chữ / sub tiếng khác giọng → trước khi viết đồ hoạ chạy `run.py sub-dich --work <dir> --ngon-ngu <mã>`, điền
     `chu` cho từng cụm `sub_dich` (gộp cụm theo nghĩa được, giữ `tu` cụm đầu / `den` cụm cuối) và viết mọi chữ đồ hoạ bằng tiếng đó
     (ĐÃ CHỐT 1, ngoại lệ). Cổng duyệt hỏi thêm: giữ tô vàng karaoke hay tắt; bảng tên riêng đã dịch.
3. `run.py kiem-kh --work <dir>` → sửa hết ⛔ (⚠ cân nhắc).
4. `run.py duyet --work <dir>` → `duyet.jpg` (khung ở mỗi cảnh / đồ hoạ / CTA) + `bang_duyet.txt` (cảnh, đồ hoạ, CTA, sub đã sửa).
   MỞ `duyet.jpg` soi: chữ gãy, chữ chìm, đè nhau, ảnh sai nghĩa. Soi gần: `run.py khung --work <dir> --times 12.3,45.6` → `khung_le\`.
5. **CỔNG DUYỆT — DỪNG 1 lần**, gửi `duyet.jpg` + bảng tóm tắt, hỏi:
   - **D1** Kênh cho CTA: tên kênh, @handle, file avatar (để trống = avatar chữ cái / ngôi sao, không tên).
   - **D2** Nhạc nền — CHỈ hỏi khi có nhạc: báo file đã ghép (tên, độ dài, đã lùi bao nhiêu giây) — giữ / đổi file / tắt.
     Resources không có file nhạc → bỏ câu này (không nhạc, không xin file).
   - **D3** Chữ CTA (tiêu đề + dòng viết tay) giữ hay đổi.
   - **D4** SFX ở CTA (tiếng bấm / tim) giữ hay tắt (`sfx_cta: false`).
   - **D5** Phần lời không có footage khớp (liệt kê cụ thể) — bổ sung clip hay giữ cách thay thế (ảnh bài báo dạng thẻ / chữ phủ cảnh chung).
     Có `hanh_trinh`: báo từng chặng (điểm đi → điểm đến, phương tiện, số) đang TỰ VẼ nền gì hay đè lên clip Resources nào — có clip
     phương tiện (máy bay, xe, tàu…) muốn thay nền tự vẽ không.
   - **D6** Danh sách chữ đã sửa lỗi nhận giọng + chỗ còn ĐOÁN — có chữ nào sai không.
6. `run.py dung --work <dir> [--luong 4]` → `<audio>_DLV.mp4` (tự chạy `kiem`; ~2 phút video ≈ 4 phút dựng với 4 luồng, chạy nền).
   Thử nhanh: `--xem-truoc` → `<audio>_DLV_xem_truoc.mp4` chỉ 20 s đầu, không tự kiểm.
   Chỉ đổi TIẾNG (mức nhạc, file nhạc, SFX) sau khi đã dựng: `run.py tron-lai --work <dir> [--file <video đã dựng>]` → bản mới
   giữ nguyên hình, ~40 s, tự kiểm luôn. Đổi chữ / cảnh / đồ hoạ thì phải `dung` lại.
7. `run.py kiem --work <dir>` (tự chạy sau dung) → phải **ĐẠT** đủ mục: khổ 1080×1920 · 30 fps · độ dài khớp · có tiếng · không cắt giọng ·
   có nhạc nền −24…−10 dB dưới giọng (khi kế hoạch có nhạc) · −14 LUFS ±1 · đỉnh ≤ −1 dBTP · không khung đen · mọi chữ đúng ngôn ngữ audio · chữ / sub không đè nhau · CTA cuối.
   MỞ `soat.jpg` soi lại. Giao: đường dẫn, độ dài, khổ, bảng lời → cảnh / đồ hoạ, mục còn đoán.
8. Dọn: `run.py don --work <dir>` xoá `footage\` (khung ảnh trích, nặng) khi đã giao xong.

## Bẫy đã gặp

- **vietnamtourism.gov.vn là trang Vue (SPA)**: tải HTML chỉ có khung rỗng. Lấy bài qua API công khai
  `https://public.vietnamtourism.gov.vn/post/<id>?param=%7B%22lang%22%3A%22vi%22%7D` (param JSON mã hoá URL; `param[lang]=vi` → lỗi 500).
  Ảnh trong bài trỏ `vietnamtourism.gov.vn/images/...` trả HTML → đổi sang `https://images.vietnamtourism.gov.vn/vn/images/...`.
- Trang báo khác: thử HTML thường (ưu tiên `<article>`), chữ < 600 ký tự thì tự dựng DOM bằng Chrome `--dump-dom`. Logo / icon / ảnh < 360 px bị bỏ.
- Chú thích ảnh bài báo là ĐOÁN (đoạn ngắn ngay sau ảnh) — từng gán nhầm ảnh Lăng Bác thành ảnh khác. Luôn mở ảnh.
- Ảnh bài báo thường chỉ ~800 px ngang: phóng tràn màn sẽ vỡ (⚠ khi phóng > 2,3×) → dùng `khung: "the"`.
- CSS lớp ẩn mặc định + `show(el, true)` chỉ xoá style inline → phần tử vẫn ẩn. Lớp nào JS bật / tắt thì CSS KHÔNG đặt `display: none`.
- Khối chữ `div` rộng 1080 → `scrollWidth` không bao giờ vượt → không co chữ. Đo bề rộng chữ bằng `Range.getBoundingClientRect()`
  (hàm `rong`, `vua` trong `dulich.js`). Dòng tràn khung thì `text-align: center` dồn về trái — tính mốc giữa từ mép ký tự đầu.
- Clip điện thoại 576×1024 → phóng lên 1080×1920 hơi mềm: đã làm nét `unsharp` khi trích khung; ưu tiên clip ≥ 1080 ngang nếu có.
- Whisper large-v3 lần đầu tải ~3 GB, chạy CPU lâu — để chạy, không huỷ. Kết quả nhận lời có cache theo file + ngôn ngữ.
- Người dùng thêm file vào Resources rồi bảo "làm lại": chạy lại `quet` cùng tham số — nhận lời / bài báo lấy cache, kế hoạch đã sửa
  GIỮ NGUYÊN, mã cũ giữ nguyên, file mới nhận số kế tiếp (file bị xoá → ⚠). Mở lại `tai_nguyen.jpg`, đưa tư liệu mới vào đúng đoạn lời;
  trước khi sửa chép `ke_hoach.json` → `ke_hoach_ban1.json` để giữ bản cũ; video ra tự thành `_DLV_ban2`.
- Khoá `sua_loi` phải khớp ĐÚNG chữ Whisper in trong `loi_doc.txt` (dấu thanh khác là không khớp: "lã" ≠ "lá") — `kiem-kh` ⚠ "không thấy cụm".
- Đoạn liệt kê có ảnh từng mục (món ăn, điểm đến): montage 1 ảnh / mục đổi đúng giây đọc tên (cảnh ≥ 1,2 s — mục đọc dồn thì lùi
  cảnh sau 0,1–0,2 s), tiêu đề + chip ở PHẦN TRÊN (chip `y` ≈ 440), ảnh nhỏ làm thẻ đặt dưới chip (đáy ≤ 1300). Chip dài nhiều mục
  xuống 3 hàng (~440–760) — thẻ phải bắt đầu dưới 770.
- Người trong clip có nhãn dán / che mặt (vd clip "Lá Rơi" 34–37,9 s) — soi tờ khung để tránh.

- Bài báo: trang nhiều cỡ ảnh (`srcset`) → lấy cỡ to nhất; ảnh Wikimedia `/NNNpx-` nâng lên 1280 px; bản đồ, svg, cờ, emoji, băng rôn
  (ngang > 3,2×) bị bỏ; tiêu đề bỏ đuôi " – Wikivoyage" / " | VnExpress"; đoạn văn lặp liền nhau bỏ. Đã chạy: vietnamtourism, VnExpress, Wikivoyage.
- Chữ đang đọc phồng `scale` 1,07 với từ dài tiếng Anh (~290 px) nở 10 px mỗi bên → ăn hết khoảng trắng, "Welcometo" dính chữ.
  Biên độ phồng theo bề rộng từ (≤ ~5 px mỗi bên) + lề `.035em`.
- Viết tay của chữ Nhật / Trung / Hàn rơi về font Gothic cỡ 132 px, `margin-top` âm → đè lên tít. Lớp `phi_latin` xếp lại (mục 5).
- Kế hoạch nháp cũ đặt CTA = hết lời − 4,5 s → rơi giữa câu "Come to Hanoi…". Nay bắt câu kêu gọi cuối (`CTA_TU` trong `quet.py`).
- **Hành trình**: SVG `<linearGradient>` mặc định `objectBoundingBox` → mỗi vòng tròn của đám mây có gradient riêng → lộ thành bong bóng /
  vạch ngang; mây dùng gradient `userSpaceOnUse` chung cho cả lớp. Huy hiệu phương tiện phải tắt NGAY lúc tới (`luc_den`), không thì
  chồng lên ghim điểm đến thành 2 ghim; không có phương tiện (`khong`) thì là đầu sáng, không phải ghim. Bản đồ phố là sơ đồ, không phải
  bản đồ thật — hồ chỉ vẽ ở điểm tên là hồ (`ho_tai`), đừng thêm chi tiết địa lý không có trong lời. Nền đường mặc định núi đá vôi trông
  như Hạ Long → sân bay / thành phố dùng `canh_xa: "thanh_pho"`.
  Xe vẽ nhìn ngang phải ĐẦU XE QUAY THEO HƯỚNG CHẠY (sang phải): nắp capô dài + kính lái xiên ở phía trước, cốp ngắn + kính hậu dốc ở sau,
  gương chiếu hậu sát kính lái, đèn pha trước / đèn hậu đỏ sau — người dùng bắt lỗi "ô tô bị ngược" khi capô ngắn hơn cốp (dáng xe quay đầu trái).
  Nhãn km trên đường đặt cách cung ≥ 50 px để huy hiệu xe chạy qua không đè.
- `goi_y` khớp tên file nhiều chữ theo chuỗi LIỀN: "sân bay incheon.jpg" ↔ lời "sân bay quốc tế Incheon" chỉ khớp được «sân bay»
  (cụm chung, nhắc 3 lần) → giây gợi ý có thể rơi vào câu khác. Luôn đặt cảnh vào câu có TÊN RIÊNG (Incheon), không theo cụm chung.
- **Nhạc nền nghe có thấy không**: đừng đo ở khe giữa các từ — giọng đọc (nhất là giọng AI) gần như liền mạch, khe chỉ 0,3 s còn đuôi vang, video không nhạc cũng ra −19 dBFS. Bộ trộn ghi `tron_bao_cao.json` (mức nhạc so với giọng, cả bài), tự kiểm đọc số đó (chuẩn −24…−10 dB). Bài nhạc có intro / outro nhỏ thì đầu và cuối video nhạc chìm hơn ~5–8 dB so với đoạn chính — bình thường.

## Tệp

- `scripts/run.py` (lệnh) · `quet.py` (nhận lời, bài báo, quét Resources, kế hoạch nháp) · `goi_y.py` (khớp tên tài nguyên / chú thích ↔ lời,
  gợi ý sửa lời) · `bai_bao.py` (lấy bài) · `ke_hoach.py` (kiểm + giải
  giờ + gom sub + SFX) · `dung.py` (trích khung, trang HTML, duyệt, dựng) · `render.mjs` (Chrome headless qua DevTools) · `am_thanh.py`
  (trộn giọng / nhạc / SFX, −14 LUFS) · `kiem.py` (tự kiểm file cuối) · `chung.py` (hằng số, ngôn ngữ, tiện ích, chữ hành trình
  `HANH_TRINH_NN`) · `tao_sfx_ht.py` (tổng hợp SFX phương tiện: `jet-flyby.wav`, `xe-chay.wav`, `song-nuoc.wav`).
- `assets/khung/dulich.css|js` (trang dựng) · `assets/fonts` (OFL) · `assets/sfx` (xem `CREDITS.md`) · `assets/tu_ghep_vi.txt`.
