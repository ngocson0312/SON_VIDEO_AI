---
name: edit-gym-video-huongdan
description: Edit video NGƯỜI NÓI chuyên gia (HLV thể hình, bác sĩ, giáo viên…) dọc 9:16 tiếng Việt kiểu HƯỚNG DẪN / GIẢI THÍCH — video thô có giọng + hình làm mẫu → bản edit có BẢNG MINH HOẠ VẼ TAY Ở TRÊN (cột sống, xương chậu, cơ, người que, mũi tên, ✓/✗, góc 90°, đếm lần… vẽ dần đúng lúc lời nhắc) + VIDEO NGƯỜI Ở DƯỚI (tràn đáy, cắt theo hành động, zoom nhảy), HOOK teaser mở đầu (câu hứa hẹn lấy từ cuối video + cảnh làm mẫu + chữ đập có viền + khối 3D), sub karaoke vàng-trắng (sửa lỗi Whisper), tem từ khoá, chuyển cảnh quét + chớp + tách màu RGB, SFX ~1 tiếng / 2–3 s, nhạc nền tự tạo né giọng, màn kết CTA = nút FOLLOW 3D + bàn tay con trỏ BẤM ĐÚNG 1 LẦN rồi hết video, −14 LUFS, chữ nằm trong vùng an toàn TikTok / Reels / Shorts. ĐÃ CHỐT 18/11/2026 (bản 6 khách duyệt, video Vinh "đau lưng dưới"). Đã đóng thành skill và đẩy repo SON_VIDEO_AI (CHƯA đưa vào tool). Trigger '/edit-gym-video-huongdan', 'edit video HLV này', 'edit video hướng dẫn tập có hình vẽ minh hoạ', 'video thô người nói → edit xịn có hình vẽ', 'edit video giải thích kiểu bảng vẽ'.
---

# edit-gym-video-huongdan

Video mẫu ProCoaching (`Video_Mẫu.mp4`) CHỈ để tham khảo — phong cách này là riêng: nền navy ô li, bảng vẽ tay, chữ Be Vietnam Pro Black + Pacifico, màu coral (đau / sai) · mint (đúng) · amber (nhấn) · ice (chú thích).
Bản chạy chuẩn đã chốt: video thô `Vinh\Video_Hướng dẫn\Video_Thô.MOV` → `Video_Tho_EDIT_ban6.mp4` (158,8 s, 1080×1920, −14 LUFS). Cấu hình của bản đó nằm ở `references/ke_hoach_mau_vinh.json`, cảnh vẽ nằm ở `scripts/canh.py`.

## Bố cục chốt (đừng đổi)
- **Bảng minh hoạ Ở TRÊN** (1008×736 thu 0,93 → y 112…, rộng ~937 px), **video người Ở DƯỚI** tràn mép (x 0–1080, y 810–1920; mặt / tay / sub nằm trên y 1480). Khách chê khi bảng to / video bé / lệch trên-dưới — giữ cân đối như vậy.
- Mở đầu `COLD` ~3,7 s (hook) → thân video theo thứ tự gốc → ~7 s cuối chuyển video ra TOÀN MÀN + sub y=1130 → CTA.
- **VÙNG AN TOÀN** (TikTok + Facebook Reels + YouTube Shorts) — LUẬT CỨNG: chữ / hình quan trọng trong **x 60–940, y 150–1480**; sub y ≈ 1410 (toàn màn 1130); thanh tiến độ y 98–103. Kiểm: `GUIDE=1 … dung.py xem <T…>` vẽ khung đỏ.
- Hook chữ đập: viền tối 11 px + khối 3D (không chữ trần trên nền hình).
- **CTA cuối (khách chốt)**: CHỈ nút FOLLOW 3D đỏ bóng + bàn tay con trỏ trắng viền đen trượt vào, **bấm ĐÚNG 1 lần** (1 vòng sóng + 1 tiếng click) rồi lùi ra, hình tối dần và **video hết ngay (~1 s sau cú bấm)**. Không thẻ kênh, không tim bay, không bấm lặp, không giữ đuôi dài. `EXTRA` ≈ 0,5 s.

## Quy trình (Claude làm; chạy từ thư mục skill, lệnh `python -I -X utf8 scripts\<file>.py …`)
Đặt biến môi trường cho video mới (PowerShell): `$env:GYM_SRC='<video thô>'; $env:GYM_WORK='<thư mục work>'; $env:GYM_OUT='<ra.mp4>'` (mặc định = bản Vinh). Đường dẫn có dấu cách / tiếng Việt luôn để trong "…".

1. **Nhận lời**: `nghe.py <video> <work>` → `words.json`, `loi_doc.txt` (Whisper large-v3 CPU, ~5 phút / 2,5 phút video; lần đầu tải ~3 GB, đừng huỷ).
2. **Sửa lỗi nghe** vào `<work>\sua_loi.txt`: mỗi dòng = 1 đoạn của `loi_doc.txt`, đúng thứ tự, đã sửa theo nghĩa (thuật ngữ hay nghe sai: thoát vị đĩa đệm, võng / ưỡn lưng, cơ lõi, duỗi chân, giãn cơ, tịnh tiến, cẳng chân, vuông góc). `sub.py` tự căn chữ đã sửa vào mốc giây Whisper.
3. **Xem video thô**: tờ khung mỗi ~5 s (lưới + nhãn giây); dò cú cắt cứng `ffmpeg -vf select='gt(scene,0.25)'`. Ghi nhận: các cảnh quay (khung cắt), cú cắt, câu hook.
4. **Chọn HOOK**: câu "hứa hẹn kết quả" (thoát cơn đau, giải phóng vùng đau…) ở CUỐI video thô → `hook: [t_đầu, t_cuối]`; cảnh mở `cold` (4 cảnh làm mẫu đẹp nhất, giây nguồn) + `cold_txt` 3 cụm chữ đập (ví dụ "2 BÀI TẬP ĐƠN GIẢN / THOÁT CƠN ĐAU / GIẢI PHÓNG VÙNG ĐAU"). Phần chính giữ nguyên thứ tự gốc.
5. **Viết `<work>\ke_hoach.json`** (khuôn: `references/ke_hoach_schema.md`; mẫu thật: `references/ke_hoach_mau_vinh.json`): `shots` (khung cắt từng cảnh quay: tâm cx, cy, bề rộng đầu → cuối; cắt VUÔNG quanh hành động, không cắt đầu), `cuts`, `punch` (mốc zoom đập), `stickers` (tem từ khoá góc trên-trái ô video, 1,5–4 s, không đè mặt), `sfx` (giây GỐC; 1 tiếng / 2–3 s, loại: whoosh / swoosh khi đổi cảnh, pop khi tem / thẻ hiện, ting / ding khi ✓, punch khi nhấn, click khi bước).
6. **Viết cảnh minh hoạ** cho đề tài mới: file `<work>\canh_<chude>.py` định nghĩa `SCENES = [(t0, t1, hàm), …]` (giây GỐC; hàm `f(cv, t)` vẽ lên bảng 1008×736) — đặt `"scenes_file": "canh_<chude>.py"` trong `ke_hoach.json`. File đó `from canh import *` để dùng `pill/pop/text/…` và thư viện hình:
   - `hinh.py`: `board_bg`, `spine/spine_curve`, `pelvis`, `psoas_path`, `lying`, `kneeling`, pose `LY/KN` + `blend_pose` (người que nằm / quỳ chống);
   - `ve.py`: `stroke` (nét vẽ tăng dần), `arrow`, `dashed`, `check`, `cross`, `glow`, `sprite/text` (chữ nổi khối 3D), `badge`, `paste_round`, easing;
   - `canh.py` (9 cảnh mẫu sA…sH: vùng đau, 2 bài, cơ gập hông, sai / đúng, 4 bước, thảm / giường, tư thế quỳ 90°, câu hỏi / comment) — dùng làm KHUÔN cho cảnh mới, neo giây theo `words.json`; chữ trong bảng nhân hệ số `FS = 1.18` (bảng bị thu nhỏ).
   Cảnh sát lời: mỗi ý hiện đúng giây nhắc, chữ kịp đọc (≥ 1,6 s), không đè nhau.
7. **Xem thử**: `dung.py xem <T…>` (T = giây thành phẩm = giây gốc + `D0`≈3,7) → `<work>\xem.jpg`. MỞ ẢNH soi: chữ không đè nhau / không đè mặt, nét vẽ đúng giải phẫu, sub đúng chính tả, trong vùng an toàn (`GUIDE=1`). Quét hết video bằng `xem` mỗi ~1,5 s để bắt lỗi ngoại lệ trước khi dựng.
8. **Dựng**: `dung.py am` (giọng + SFX + nhạc `nhac.py` + sidechain, loudnorm −14) → `dung.py hinh` (1 lần x264 crf17, ~13 phút / 2,6 phút video — chạy NỀN, 1 tiến trình duy nhất) → `dung.py ghep` (ra `…_EDIT.mp4`, có rồi thì `_ban2…`). `dung.py full` = cả ba.
9. **Tự kiểm** rồi giao: `ffprobe` (1080×1920, 30 fps), −14 ± 0,5 LUFS, đỉnh ≤ −1 dBFS, soi khung đầu / giữa / cuối. **Luôn gửi file bấm xem được** (SendUserFile + link). Báo mục chưa nghe / chưa thử trên app.

## Bẫy đã gặp (đừng lặp lại)
- `cv2.imwrite` KHÔNG ghi được đường dẫn có tiếng Việt (im lặng) → dùng `imsave()` (imencode); công cụ Read cache theo đường dẫn → copy ảnh sang tên mới trước khi mở.
- ffmpeg 9: dùng `-fps_mode passthrough` (không `-vsync`); `drawtext` sập (fontconfig) → vẽ chữ bằng PIL / cv2.
- Chạy 2 lần `dung.py hinh` song song làm hỏng `hinh_cam.mp4` → xoá file trước khi chạy lại; KHÔNG `taskkill /IM python.exe` — kill đúng PID.
- Font không có ⟂ ↓ → (ô trống) → dùng chữ. `arrow()` cần ≥ 2 điểm. Mảng điểm phải là `np.array`.
- Cụm sub liền nhau chồng giờ 0,1 s → `dung.py` đã cắt `t1` cụm trước = `t0` cụm sau (không để 2 cụm chồng chữ).
- Hình giải phẫu chỉ minh hoạ phổ thông (không chẩn đoán); chữ trên hình bám lời HLV, không thêm số liệu y khoa.
- Chữ trên ô video chỉ là tem nhỏ góc trên-trái; sub ở đáy ô video.
- Cảnh bảng vẽ có thể còn trống bên phải (như cảnh A) — khi viết cảnh mới dàn đều chiều ngang 1008 px.

## Việc tiếp theo (khi đưa vào tool)
- Dò mặt tự động (MediaPipe) để tem / chữ không đè mặt; dò cú cắt + chọn hook tự động bằng Whisper + điểm "hứa hẹn".
- Gom cảnh minh hoạ thành thư viện theo chủ đề (đau lưng, vai, gối, giảm mỡ…) để khỏi vẽ lại từ đầu.
- Đóng gói `run.py` (quet → duyet → dung → kiem) theo khuôn các skill khác; thêm cổng duyệt 1 lần (hook, tem, bảng vẽ, nhạc, CTA).
