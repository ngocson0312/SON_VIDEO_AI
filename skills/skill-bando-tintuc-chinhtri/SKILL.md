---
name: skill-bando-tintuc-chinhtri
description: Dựng VIDEO BẢN ĐỒ 3D kiểu tin tức / địa chính trị dọc 9:16 CHỈ TỪ 1 FILE AUDIO giọng đọc (m4a/mp3/wav), đúng phong cách video mẫu beo.mp4 (Khám Phá Thế Giới) — camera bay liên tục trên bản đồ vệ tinh không cắt cảnh, nước được nhắc phủ cờ / tô khối nổi, nhãn viết tay trắng, biển chữ neon xanh, thành phố ghim trắng, tên lửa bay theo cung sáng vàng, nổ, vỡ vụn, sóng radar, tách đầu đạn, tuyến đường / dòng chảy mũi tên, vùng lan rộng, vệ tinh / tàu / giàn phóng / thùng dầu đặt lên bản đồ, nhân vật cắt nền tải từ Wikipedia, sub karaoke 3 từ IN HOA vàng-trắng viền đen, nhạc nền + SFX bám sự kiện, −14 LUFS. Whisper nhận lời → Claude viết kịch bản JSON (bộ 16 động tác chuẩn) → tự tải cờ / ảnh / ô bản đồ → DỪNG 1 lần ở cổng duyệt → render → tự kiểm. Trigger '/skill-bando-tintuc-chinhtri', 'làm video bản đồ từ audio này', 'dựng video tin tức địa chính trị kiểu bản đồ', 'video kiểu Khám Phá Thế Giới', 'audio này ra video bản đồ', 'template NNS bản đồ'.
---

# skill-bando-tintuc-chinhtri — audio → video bản đồ 3D kiểu tin tức

Phân tích gốc của phong cách: `D:\____TTT_____\SON_AI_VIDEO\phan_tich_video_ban_do\phan_tich_beo.md`.
Video mẫu: `F:\VIDA_TEST\0411\Beo\beo.mp4` (69 s, Triều Tiên phóng Hwasong-20). Kịch bản dựng lại của mẫu: `references/vi-du-beo.json`.

Mọi lệnh chạy từ thư mục dự án `D:\____TTT_____\SON_AI_VIDEO`, dạng:
`python -I -X utf8 .claude\skills\skill-bando-tintuc-chinhtri\scripts\run.py <lệnh> …`

## Phong cách ĐÃ CHỐT (không đổi trừ khi người dùng yêu cầu)

| Lớp | Chốt |
|---|---|
| Nền | ảnh vệ tinh Esri World Imagery (có địa hình đáy biển), Mercator, camera nghiêng 35°, 1080×1920 @30, **không cắt cảnh — chỉ bay** |
| Nhịp | 1 câu lời = 1 nhịp; 1 việc chính / nhịp; nổ-vỡ rơi vào cuối câu; câu chuyển / câu hỏi → camera lùi ra (`vong`) |
| Nước | nước chính phủ texture cờ, nước phụ tô màu, khối có độ dày, viền sẫm; nhãn viết tay trắng (Caveat đậm cho chữ không dấu, Pacifico cho chữ có dấu) nằm trên đất, to nhỏ theo zoom |
| Biển / vùng | chữ neon xanh phát sáng |
| Thành phố | bong bóng ghim trắng, chữ viết tay đen |
| Vật thể | dựng đứng tại điểm (billboard), đổ bóng; tàu nằm đất xoay theo hướng |
| Sự kiện | cung bay vàng phát sáng (nét đứt = dự kiến), nổ lửa + loé trắng + vệt cháy, vỡ vụn Voronoi, radar 3 vòng, vệt tách trắng, tuyến mũi tên cam, vùng lan đỏ |
| Nhân vật | ảnh cắt nền nửa người (u2net), hiện ~3 s, neo vào nước |
| Sub | karaoke cụm 2–3 từ IN HOA, Paytone One nghiêng (đậm bo tròn, có dấu tiếng Việt — thay cho Lilita One của mẫu vì Lilita thiếu dấu), trắng viền đen + bóng, chữ đang đọc **vàng**, chữ HOA cao 2,7 % khung (≈ 52 px ở 1920, viền 8, bóng 4 — `tao_ass` tự tính Fontsize từ số đo font; cụm rộng > 90 % tự thu nhỏ), y = 75 % khung, ẩn bên dưới mọi đồ hoạ |
| Tiếng | giọng gốc + nhạc nền (assets/nhac/*.mp3 nếu có, không thì drone tự sinh) + SFX bám sự kiện (assets/sfx/ ghi đè), master **−14 LUFS, TP −1** |
| Đuôi | video dài = audio + 0,9 s; không ghi đè file cũ (_ban2, _ban3…) |

## Quy trình (làm đúng thứ tự, không bỏ bước)

### 0. Lần đầu trên máy (cần mạng)
`run.py chuan-bi` — tải ranh giới Natural Earth (10m nước, 50m bang), font Paytone One / Caveat / Pacifico, u2net.onnx (176 MB), sinh sprite nổ, SFX, nhạc drone, icon dự phòng. Các bước sau tự gọi lại nếu thiếu.

### 1. Nhận lời
`run.py nhan-loi "<audio>"` → `<thư mục audio>\work_ban_do\loi_doc.txt` + `loi_doc.json` (Whisper large-v3, từng từ có giây). Lần đầu tải model ~3 GB, CPU chậm: đặt timeout dài, không huỷ.
Thư mục chỉ có 0 hoặc ≥ 2 file audio → hỏi người dùng chọn.

### 2. Claude viết `work_ban_do\kich_ban.json` (việc chính của Claude)
Đọc HẾT `loi_doc.txt`, `references/kich_ban_schema.md` (schema + 16 động tác + 9 luật) và HAI ví dụ: `references/vi-du-beo.json` (tên lửa) và `references/vi-du-bien-dong.json` (BẢN CHUẨN MỚI NHẤT, người dùng đã duyệt 04/11: camera danh sách điểm dừng, tuyến tàu theo biển, nhãn tiếng Việt, thẻ cờ, CTA nút). Với từng câu:
1. Câu nói về đâu → `camera` DANH SÁCH điểm dừng `{luc, toi, rong_km}` (luc = giây camera ĐẾN NƠI, đúng từ khoá); mỗi chủ đề lùi rộng rồi zoom vào; đổi lục địa tính ≥ 4–5 s bay; câu nối → `giu`. Không `vong`.
2. Nước nhắc tới → `to_nuoc` (+ `nhan`), biển → `chu_neon`, thành phố → `ghim`, vật → `vat_the`, người nổi tiếng → `nguoi`, hành động (phóng, nổ, lan, tuyến, tách, radar) → động tác tương ứng, số trong lời → `so`, câu kêu gọi theo dõi cuối → `cta` (nút). Tuyến tàu/dầu → `tuyen` có `vat` tàu (tự đi theo biển). Nước không nằm trong khung camera lúc được nhắc → thẻ `anh` cờ hoặc `so`, đừng bay quá tốc độ.
3. `luc` = giây của từ tương ứng trong `loi_doc.txt` (trừ 0,1–0,2 s). Nổ / vỡ đặt 0,3–0,6 s trước khi câu kết.
4. Không bịa: số, người, nước không có trong lời thì không đưa vào. Mục nào phải ĐOÁN (ví dụ tàu đi tuyến nào, tên lửa bắn vào đâu) → ghi vào danh sách "ĐOÁN" để hỏi ở cổng duyệt.
Rồi `run.py kiem-kb --work <work>` → sửa hết ⛔, cân nhắc ⚠.

### 3. Tải tài nguyên (cần mạng — chạy với quyền mạng)
`run.py tai --work <work>` → `thuc_the.json` (nước/bang/biển/thành phố → toạ độ + cờ flagcdn; người → ảnh Wikipedia cắt nền; vật → thư viện người dùng `assets/thu_vien/<vat>.png` > ảnh Commons tải + cắt nền `cache/thu_vien_tai/` > icon tự vẽ `cache/thu_vien_mac_dinh/`), tải trước ô bản đồ cho cả lộ trình camera, xuất `duyet.jpg`.
Người dùng có thể bỏ ảnh riêng vào `<thư mục audio>\tai_nguyen\<tên người hoặc vật>.png` — được ưu tiên.
Claude PHẢI mở `duyet.jpg` soi: ảnh người đúng người chưa, vật thể cắt nền có ra hình không (cắt hỏng → thêm `--khong-tai-vat` để dùng icon tự vẽ, hoặc xin người dùng ảnh).

### 4. CỔNG DUYỆT — DỪNG 1 lần, hỏi người dùng
Đưa: (a) bảng nhịp: giây | câu | camera | động tác; (b) `duyet.jpg`; (c) danh sách ĐOÁN. Hỏi gọn:
- D1. Nước / vùng / thành phố nhận đúng chưa (đặc biệt tên trùng: Washington bang ≠ thủ đô, Georgia).
- D2. Ảnh nhân vật / vật thể dùng được không, có ảnh riêng muốn thay không.
- D3. Các mục ĐOÁN có đúng ý không.
- D4. Nhạc nền: dùng drone mặc định hay file riêng (`assets/nhac/`).
Kiểu chữ, kiểu sub, bố cục đã chốt — không hỏi. Chờ trả lời rồi mới dựng.

### 5. Dựng
`run.py dung --work <work> --xem-truoc` → `xem_truoc.jpg` (1 khung/giây, không mã hoá) → Claude mở soi nhanh bố cục; lệch thì sửa kịch bản.
`run.py dung --work <work>` → `<tên audio>_bando.mp4` cạnh audio (bỏ hậu tố `_audio`). ~0,1–0,4 s/khung → 50 s video ≈ 4–8 phút. Thêm `--nhanh` để thử 540×960. Thiếu ô bản đồ → chạy lại `tai` hoặc `dung --mang`.

### 6. Tự kiểm trên file cuối
`run.py kiem --work <work>` → thời lượng, loudness, `kiem_khung.jpg`, bảng lời ↔ động tác. Claude PHẢI mở `kiem_khung.jpg` soi: nước tô đúng chỗ, nhãn không che vật, sub không bị đè, không khung tối, hiệu ứng đúng giây đọc. Sai → sửa kịch bản, dựng lại.

### 7. Giao kết quả
Đường dẫn file, độ dài, khổ, bảng nhịp (giây | lời | hình), các mục đã đoán và nguồn ảnh (Wikipedia/Commons + giấy phép từ `thuc_the.json`). Không kể lể quá trình.

## Cấu trúc

```
scripts/run.py            cổng vào: chuan-bi | nhan-loi | kiem-kb | tai | dung | kiem
scripts/chung.py          bảng tên nước VN→ISO, biển, vật thể, toán Mercator
scripts/engine/camera.py  camera 3D nghiêng, nội suy bay / vòng
scripts/engine/nen.py     ô vệ tinh Esri cache + ghép ROI
scripts/engine/dia_ly.py  Natural Earth → đa giác
scripts/engine/ve.py      chữ viền/bóng, neon, sprite, vạch sáng, bong bóng, thẻ ảnh, tô cờ, mảnh vỡ
scripts/engine/dong_tac.py 16 động tác chuẩn
scripts/engine/render.py  lộ trình camera + ghép khung
scripts/engine/sub.py     ASS karaoke
scripts/engine/am_thanh.py trộn giọng + nhạc + SFX, loudnorm
assets/thu_vien/<vat>.png  thư viện vật thể người dùng (ưu tiên cao nhất)
assets/nhac/*.mp3          nhạc nền riêng;  assets/sfx/<ten>.wav  SFX thay thế (no, phong, ping, vo, hien, tach, luot, lan, dem)
cache/                     dữ liệu tải (không đẩy git)
```

## Bẫy đã gặp

- `-I` bỏ qua biến môi trường PYTHON*: in tiếng Việt phải chạy `python -I -X utf8`.
- Caveat / Caveat Brush / Lilita One KHÔNG có dấu tiếng Việt (ể, ạ, ộ, ư, ơ thành ô vuông). `ve.chon_font()` tự đổi sang Pacifico (viết tay) / Paytone One (đậm) khi chữ có dấu; sub dùng Paytone One.
- Nước rộng (Nga, Mỹ, Canada) phủ cờ sẽ chiếm nửa khung: luôn đặt `den` cho `to_nuoc` nước phụ, chỉ giữ nước đang nói tới. Nhãn nước rộng đặt `tai: [lon, lat]` ngay giữa phần đang nhìn thấy, không dùng điểm nhãn mặc định (Nga mặc định ở tận phía tây).
- Ảnh Commons cho vật thể chung chung hay sai (tìm 'aircraft carrier' ra máy bay Boeing): mặc định vật nào đã có icon tự vẽ thì dùng icon; chỉ tải Commons cho vật chưa có icon hoặc khi chạy `tai --tai-vat`.
- faster-whisper + av mới lỗi `metadata_errors`: đọc wav bằng `wave` rồi đưa mảng numpy (đã làm trong `nhan_loi.py`).
- "Mỹ" không dấu = "my" trùng mã ISO Malaysia → chỉ nhận mã ISO khi viết HOA 2 chữ.
- "Washington" = bang; thủ đô ghi "Washington, D.C.". "Georgia" ưu tiên nước Gruzia.
- Camera nhìn quá mép bắc/nam bản đồ sẽ ra vùng tối → `rang_buoc()` tự hạ góc nghiêng rồi thu tầm nhìn; đừng đặt `rong_km` > 14000.
- Ảnh Commons cắt nền u2net không phải lúc nào cũng đẹp (ảnh có nền phức tạp) → soi `duyet.jpg`, lúc cần dùng `--khong-tai-vat`.
- Nominatim giới hạn 1 yêu cầu/giây; kết quả được cache ở `cache/geocode.json`.
- Nhịp < 1,2 s hoặc 3 hiệu ứng lớn / nhịp → `kiem-kb` cảnh báo: gộp nhịp, đừng dồn.
- CHỮ KHÔNG Ở LẠI LÂU: nhãn / chữ neon / ghim chỉ hiện ≈ 3,5 s kể từ lúc được nhắc rồi tắt (người dùng góp ý 04/11: "Biển Đông" nằm hơn 6 s dù lời đã sang chuyện khác). Engine tự cắt `den` ≤ `luc` + 3,5; `kiem-kb` báo ⛔ nếu kịch bản ghi dài hơn; chỉ khi thật sự là chủ đề xuyên suốt mới thêm `"giu_lau": true`. Nhắc lại tên ở câu sau thì bắn lại 1 nhãn mới, đừng kéo dài nhãn cũ. Áp cho MỌI loại chữ.
- Camera phải trôi liên tục: không dừng-rồi-chạy theo từng nhịp (`LoTrinh` nội suy PCHIP qua các mốc), không hạ góc nghiêng từng bậc 1° (`rang_buoc` chia đôi liên tục), không trôi zoom thêm lúc "giữ".
- Không dùng nền ồn: nhạc drone tự sinh và SFX làm từ nhiễu trắng (lướt, lan, hiện, tách, phóng) nghe như tiếng mưa xì xào → mặc định KHÔNG nhạc nếu `assets/nhac` trống, và bỏ các SFX nhiễu tự sinh (chỉ giữ nổ, vỡ, ping). Muốn có thì bỏ file thật vào `assets/nhac`, `assets/sfx`.
- TUYẾN PHẢI ĐI ĐÚNG NGHĨA (góp ý 04/11: mũi tên "qua Biển Đông" lại cắt xuyên đất liền Đông Dương — "quá lỏ"): tàu / dầu / hàng hải đi THEO BIỂN. `tuyen` có `vat` là tàu hoặc có `bien: true` hoặc có `qua: [điểm dẫn]` thì engine tự dò đường biển tránh đất liền (`engine/duong_bien.py`, A* trên mặt nạ Natural Earth 0,1°). Eo hẹp (Singapore, Malacca, Đài Loan) hẹp hơn độ phân giải → ĐẶT điểm xuất phát ở ngoài eo (vd [105.2,1.4]) hoặc thêm `qua`. Điểm đầu/cuối trên đất (cảng) tự dời ra mặt biển. Chỉ tên lửa / máy bay mới dùng cung cong (`bien: false`). Mở hình soi: tuyến không được đè lên đất.
- HÌNH PHẢI KHỚP LỜI TỪNG TỪ (góp ý 04/11: "hình không khớp giọng nói"): mỗi động tác `luc` = giây của đúng TỪ được nhắc trong `loi_doc.txt` (`từ@giây`), không lấy giây đầu câu. Vật chưa được nhắc thì chưa hiện (không đặt tuyến tàu dầu khi lời chưa nói tới tàu). Nước/địa danh nằm ngoài khung camera lúc được nhắc thì hình vô nghĩa: camera phải ĐẾN nơi đó trước từ ≈ 0,3 s, hoặc dùng `so` chữ màn hình cho đoạn không có chỗ trên bản đồ (vd "WASHINGTON khẳng định").
- CAMERA = ĐIỂM DỪNG ZOOM THEO TỪ (góp ý 04/11: "chưa zoom highlight chính xác, đúng nhịp, đúng ý"): `camera` của nhịp có thể là DANH SÁCH `[{luc, toi, rong_km, nghieng}]`, `luc` = giây camera ĐẾN NƠI (đúng lúc từ khoá được nói). Kiểu nhịp: câu mở → rộng; nêu đối tượng → zoom vào đối tượng (rong_km nhỏ); sang chủ đề khác → lùi ra rồi mới tiến. Không bay quá 1 lần mỗi chủ đề.
- CAMERA KHÔNG LIA GẮT (góp ý 04/11: "lia cam vớ vẩn, dễ đau mắt, cắt vẫn giật"): tốc độ tối đa 0,35 "đơn vị" mỗi giây (1 đơn vị = 1 bề rộng màn hình dịch chuyển, hoặc zoom đổi e² lần). `LoTrinh._kiem_toc_do` in ⛔ khi 2 điểm dừng cách nhau quá gần so với quãng đường; sửa bằng cách nới thời gian, bỏ bớt điểm dừng, hoặc dùng `rong_km` rộng hơn. Đổi lục địa mất ≥ 4–5 s: tính trước, bắt đầu rời chủ đề cũ sớm. Không dùng `vong` (lùi xa rồi sà) trừ khi thật cần. Đi cắt cảnh (đổi nền đột ngột) bị cấm: chỉ bay.
- SFX LÀ CỦA NGƯỜI DÙNG, MỖI SỰ KIỆN 1 TIẾNG (góp ý 04/11: "tạch tạch tạch nghe khó chịu, thay hết bằng sfx của mình"): `assets/sfx` chứa bản sao SFX từ kho minh-tam-edit, tên theo cue: `hien`=pop (nhãn/ghim/vật/ảnh hiện), `dem`=ting (số hiện, KHÔNG tick từng chữ số), `phong`=whoosh, `luot`=swoosh (tuyến bắt đầu vẽ), `lan` và `tach`=quick-swoosh, `ping`=chime (radar chỉ 1 tiếng cho cả cụm sóng). Các cue chưa có file thật (`no`, `vo`) mới dùng bản tự sinh. Không bao giờ phát tiếng lặp dồn dập (≥ 3 tiếng trong 2 s); muốn đổi tiếng thì thay file cùng tên trong `assets/sfx`.
- NHÃN TIẾNG VIỆT KHỚP LỜI (góp ý 04/11: "Bắc Kinh là Beijing à"): lời đọc tiếng Việt thì nhãn `nhan` / `ghim` / `chu_neon` viết đúng tiếng Việt như người đọc nói (Bắc Kinh, Quảng Châu, Trung Quốc, Nga, Hoa Kỳ), không dùng tên tiếng Anh của video mẫu trừ khi người dùng bảo. Font viết tay Pacifico có đủ dấu.
- CTA CUỐI VIDEO LÀ NÚT, KHÔNG PHẢI CHỮ TRƠN (góp ý 04/11): câu kêu gọi theo dõi / bình luận dùng động tác `cta` (nút đỏ bo tròn có chuông, nảy lên, con trỏ bay tới bấm, sóng loé, chuông rung, 2 tiếng pop + ting), `luc` = giây bắt đầu câu kêu gọi, `chu` mặc định "THEO DÕI KÊNH", `phu` dòng nhỏ dưới nút (vd "Bấm chuông để không bỏ lỡ"). Không dùng `so` cho CTA.
- KHÔNG BAO GIỜ DÙNG SFX TỰ SINH ĐỂ PHÁT (góp ý 04/11 lần 2: "cứ có tiếng tạch tạch tạch"): tiếng đó là cue `dem` bản tự sinh (chuỗi tick đếm số) — nó xuất hiện khi `assets/sfx` không tìm thấy (skill bị chuyển thư mục). Giờ `am_thanh.py` BỎ HẲN các cue `luot, lan, hien, tach, phong, dem` nếu chỉ có bản tự sinh (im lặng, không phát tick); `chung.thu_muc_sfx()` tìm SFX thật ở `assets/sfx` của skill và ở `SON_VIDEO_AI/skills/<tên skill>/assets/sfx`. Ngoài ra 2 tiếng cách nhau < 1,0 s chỉ giữ 1 (tiếng `hien` nhường tiếng quan trọng hơn) để không dồn "tạch tạch". Trước khi dựng luôn kiểm `assets/sfx` còn đủ 7 file (hien, dem, phong, luot, lan, tach, ping); `dung` in số SFX đã trộn — số 0 hoặc quá thấp là thiếu file.
- CỠ NHÃN THEO MẶT ĐẤT (chạy audio Hàn–Triều 04/11): `co_km` là cỡ chữ trên MẶT ĐẤT nên camera zoom sát thì chữ phình to, lùi xa thì bé tí. Quy tắc: `co_km` ≈ 8–12 % `rong_km` của điểm dừng camera lúc nhãn hiện; hai nhãn cùng lúc phải cách nhau ≥ 1,3 × bề rộng chữ (≈ 2,5 × `co_km`); nhãn gần mép khung bị cắt → dời vào trong hoặc tắt sớm (chữ chỉ cần ở lại tới hết từ được nhắc + ~0,5 s). Soi `xem_truoc.jpg` từng nhãn: cắt mép, chồng nhau, quá bé đều sửa trước khi dựng.
- Dải đen ở đáy / đỉnh khung = thiếu ô bản đồ (`kiem` báo ⚠ "ô bản đồ thiếu"): chạy lại `tai` rồi `dung --mang`.
- Ảnh Commons cho vật chung chung có thể sai quốc gia (máy bay MiG-29 có huy hiệu Ba Lan cho tin Mỹ–Hàn): ở cổng duyệt hỏi D2, nếu không hợp thì truyền `vat` là đường dẫn PNG icon tự vẽ trong `cache/thu_vien_mac_dinh/`.
- libass đặt Fontsize = ascender − descender của font. Paytone One chừa nhiều chỗ cho dấu nên Fontsize 66 chỉ ra chữ hoa ≈ 30 px, nhỏ hơn mẫu gần nửa. Đừng đặt Fontsize tay: `sub.tao_ass(font_file=…)` đo tỉ lệ chữ hoa / Fontsize rồi tính ngược từ `cao_hoa` (0,027).
- `ffmpeg -af ebur128` in cả dòng đo từng khung (`I: -70.0 LUFS` ở giây 0) trước phần `Summary:`. Đọc nhầm dòng đầu sẽ báo file câm −70 LUFS; `C.ffmpeg_loudness` chỉ đọc sau `Summary:`.
- `thuc_the.json` lưu đường dẫn tuyệt đối tới `cache\co\…`. Đổi tên / chuyển thư mục skill (hay bê sang tool NNS) làm đường cũ chết; `render.BoDung` gọi `C.sua_duong_dan()` nắn lại theo vị trí skill hiện tại, khỏi chạy lại `tai`.

## Skill này được bồi thêm sau mỗi lần chạy thật

| Ngày | Việc | Góp ý / sửa |
|---|---|---|
| 04/11/2026 | Tạo skill từ phân tích beo.mp4; chạy thử audio Biển Đông (`F:\VIDA_TEST\0411\Beo\beo_audio.mp3`) | Engine Python thuần (OpenCV + PIL + ffmpeg), nền Esri, 16 động tác, sub karaoke, master −14 LUFS |
| 04/11/2026 | Người dùng chốt tên skill mới `skill-bando-tintuc-chinhtri` (skill riêng, không đè skill khác); đổi tên thư mục; soi bản thử 1 | Sub nhỏ hơn mẫu ≈ 40 % → tính Fontsize từ chiều cao chữ hoa 2,7 %; sửa đo loudness đọc nhầm −70 LUFS; nắn đường dẫn cache cũ sau khi đổi tên |
| 04/11/2026 | Người dùng soi bản Biển Đông: có tiếng xì xào như mưa, camera giật / lia chưa mượt, chữ "Biển Đông" hiện quá lâu. Thử audio hộ dân (sông Đáy, 72 s) bằng Sonnet 5.5 mức medium | Bỏ nhạc drone + SFX nhiễu tự sinh; camera nội suy PCHIP liên tục + `cam_tai()` làm mượt ràng buộc mép (gia tốc nghiêng 1,5° → 0,11°); chữ nhãn/neon/ghim ≤ 3,5 s (engine cắt, `kiem-kb` ⛔); địa danh nhỏ gần nhau (≤ 10 km) phải `rong_km` ≈ 30 để ghim không chồng; tuyến sông vẽ đường thẳng nên chỉ gần đúng (muốn đúng dòng sông dùng skill ban-do-quy-hoach-bds-ve-tinh, có hình học OSM) |
| 04/11/2026 | ĐÓNG BẢN 1: người dùng duyệt `beo_bando_ban8.mp4` ("oki rồi"). Thêm CTA nút (`cta`), SFX của người dùng, nhãn tiếng Việt | Bản chuẩn mới nhất lưu ở `references/vi-du-bien-dong.json`. Còn yếu: icon vật thể tự vẽ nhỏ, vài đoạn 3–4 s bản đồ trống, chưa có SFX nổ / vỡ thật, nước ngoài khung camera dùng thẻ cờ thay vì phủ lên bản đồ, tuyến sông nhỏ (quy hoạch BĐS) không hợp skill này → dùng ban-do-quy-hoach-bds-ve-tinh |
| 04/11/2026 | Chạy audio Hàn Quốc – Triều Tiên (`F:\VIDA_TEST\0411\hanquoc_trieutien.mp3`, 48,8 s; video `hanquoc_trieutien_bando_ban8.mp4`). Người dùng nghe vẫn có "tạch tạch tạch" | Nguyên nhân: SFX thật bị dời cùng đợt chuyển skill sang `SON_VIDEO_AI`, engine rơi về cue `dem` tự sinh. Đã bỏ hẳn SFX tự sinh, tìm SFX ở cả thư mục mới, thưa SFX ≥ 1,0 s; ghi luật cỡ nhãn theo mặt đất và dải đen thiếu ô |
