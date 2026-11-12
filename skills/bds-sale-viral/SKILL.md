---
name: bds-sale-viral
description: "Edit video NGƯỜI NÓI (sale BĐS / chuyên gia nói trước máy quay) dọc 9:16 tiếng Việt theo ĐÚNG phong cách video mẫu 'Hết Hồn Real' (Vinhomes Saigon Park, đo từng khung 12/11/2026): MỖI CÂU MỞ BẰNG 1 TIÊU ĐỀ 3 TẦNG nằm SAU ĐẦU người nói (dòng dẫn trắng mảnh trên-trái + CHỮ KHOÁ to gradient / khối 3D màu luân phiên cam-tím-nâu-vàng + chữ viết tay trắng dưới-phải đè mép khoá; vào bằng rơi từ trên / lớn dần / trượt trái loé trắng / mọc ra từ sau đầu, 'thở' chậm, ra bằng chui vào sau đầu / trôi xuống / vỡ từng chữ rơi), SUB CỤM 1–4 CHỮ Ở NGỰC trắng đậm viền tối đổi cụm bằng ĐẨY NGANG nhoè chuyển động (dòng 2 nghiêng nhạt, chữ nhấn [50m²] hồng-đỏ nghiêng, chữ to bật, chữ vàng gradient, vòng vẽ tay cam quanh chữ), THẺ ẢNH bay ra từ TAY người nói (phẳng / nghiêng 3D / xếp chồng / ảnh nhỏ lên góc), ICON 3D BÓNG MỌC RA TỪ BÀN TAY người nói suốt video (dò tay MediaPipe, icon gợi ý tự động theo lời) + nhãn viên thuốc (vị trí, tiện ích, phòng ngủ, view hồ, bình luận…), Ô TÌM KIẾM kiểu Google gõ từng ký tự, SỐ TIỀN vàng to + vệt tốc độ, LOGO dự án rơi xuống sau người, LIỆT KÊ chữ khoá tím + dòng trượt vào, zoom nhảy bám mặt ở mỗi cú cắt, màu ấm + tối mép, CHUYỂN CẢNH ở chỗ đổi bối cảnh (zoom-nhoè, tia sáng dọc, cháy phim, tách màu RGB), nhạc beat dưới giọng ~9 dB, ~20 SFX theo loại sự kiện (whoosh, lấp lánh, pop, gõ phím, ka-ching, riser), −14 LUFS, chữ / icon không bao giờ đè mặt người nói (dò mặt MediaPipe). Whisper nhận lời → script lập kế hoạch NHÁP → Claude sửa theo NGHĨA → DỪNG 1 lần ở cổng duyệt → dựng (mã hoá 1 lần) → tự kiểm 9 mục. Trigger '/bds-sale-viral', 'edit video này như video mẫu Hết Hồn Real', 'edit kiểu Hết Hồn', 'edit video người nói BĐS có tiêu đề sau đầu', 'edit video talking head sale nhà như mẫu Vinhomes Saigon Park'."
---

# bds-sale-viral — edit video người nói kiểu "Hết Hồn Real"

Video mẫu: `D:\____TTT_____\KH_Test\Hết_Hồn_Real\video_mau.mp4` (45,3 s, 576×970, 1 người nói áo trắng, 5 bối cảnh).
Số đo + lý do từng con số: **`references/phan-tich-mau.md`**. Hằng số phong cách: **`scripts/chung.py`**
(`TIEU_DE`, `KIEU_KHOA`, `SUB`, `THE_ANH`, `ICON`, `TIM_KIEM`, `SO_TIEN`, `LOGO`, `LIET_KE`, `CHUYEN`, `AM`, `SFX_NHOM`) —
**script khác không tự đặt số**. Font / SFX nằm trong `assets/` (skill tự đứng được). Kế hoạch mẫu dựng lại chính
video mẫu: `examples/plan_mau.json` (đọc để hiểu "ngữ pháp" — mỗi câu dùng đồ hoạ gì).

> Quy ước với chủ dự án: trả lời tiếng Việt có dấu, ngắn. Không bịa số (giá, diện tích…): số trên hình phải có trong lời.
> Không ghi đè video cũ (tự đặt `_BSV_ban2`…).

## NGỮ PHÁP PHONG CÁCH (đã chốt từ mẫu — không đổi trừ khi người dùng yêu cầu)

| Lớp | Đã chốt |
|---|---|
| Khung | 1080×1920, 30 fps, phủ kín; x264 crf 18, bt709. Màu ấm hơn nguồn (tương phản 1,06, bão hoà 1,14, ấm +0,015); mép dưới tối dần từ 66 % chiều cao (tối nhất 62 %), mép trên tối nhẹ |
| Zoom | **nhảy** (không mượt) ở mỗi cú cắt cùng bối cảnh + đầu câu: luân phiên 1,15 / 1,0 / 1,28 / 1,0, neo mặt ở 36 % chiều cao, khung cố định cả đoạn (trung vị mặt), trôi vào chậm +1,2 %/s |
| **Tiêu đề 3 tầng** (1 câu = 1 tiêu đề, suốt câu) | dẫn (Be Vietnam Pro Medium 66 trắng, trên-trái, đè 22 % đỉnh khoá) · **KHOÁ** (cỡ 205, rộng ≤ 84 % khung, gradient 3 mốc + khối 3D + loé mép trên + bóng) · viết tay (Great Vibes 92 trắng viền tối 1 px + bóng mềm đậm để đọc được trên nền trời sáng, dưới-phải, đè 42 % đáy khoá). Đáy khoá = đỉnh đầu THẬT (hàng trên cùng của mặt nạ người trong cột mặt, lấy lúc đầu cao nhất trong câu) + max(0,30 × cao mặt, 0,30 × cao khoá — người đứng xa mặt nhỏ vẫn đè được chữ) ⇒ **đầu người che một phần KHOÁ** (khoá ở LỚP SAU người — tách người u2net); dẫn + viết tay luôn ở lớp TRƯỚC người (đầu không bao giờ che chữ phụ). `vi_tri: giua` = giữa khung, trước người (khi trên đầu đã có logo) |
| Màu khoá (luân phiên, 2 tiêu đề liền nhau không trùng) | `cam` Anton trắng→cam đào · `tim` Montserrat Black oải hương→tím + khối tím đậm · `nau` Baloo 2 kem→caramel + khối nâu · `vang` Anton vàng chanh đặc (+ icon nét vàng chìa khoá-nhà) · `cam_nghieng` Montserrat BoldItalic kem→cam vàng |
| Vào / ra tiêu đề | dẫn + viết tay hiện mờ→nét trước (6 khung), khoá vào sau 2 khung trong 10 khung: `roi` (rơi từ trên mép, to 1,28→1) · `phong` (0,15→nảy→1) · `truot` (từ trái, nhoè ngang, LOÉ TRẮNG rồi về màu) · `tu_dau` (mọc ra từ sau đầu). Cả khối "thở" 1→1,035. Ra 7 khung: `chui_dau` (thu nhỏ chui vào sau đầu) · `troi_xuong` (trôi xuống + mờ, dùng trước chuyển cảnh) · `vo_chu` (14 khung, từng chữ rơi xoay — tiêu đề CUỐI video) |
| **Sub ngực** | cụm 1–4 chữ, Montserrat Bold 64 trắng viền tối + bóng; tâm = tâm mặt + 3,4 × cao mặt, kẹp 49–69 % chiều cao, tâm ngang bám người. Cụm liền nhau **ĐẨY NGANG** 4 khung 230 px + nhoè chuyển động (luân phiên hướng), cụm đầu sau khoảng lặng **nhoè vào** (9 px→0, 1,12→1). Dòng 2 = `phu` (SemiBoldItalic 54); dòng 1 giống cụm trước thì ĐỨNG YÊN, chỉ dòng 2 đổi. `[..]` = nhấn hồng-đỏ (232,22,92) BoldItalic (số, m², tỷ, "VỊ TRÍ"); `to` = 1 chữ to 128 bật 0,55→1,08→1; `vang` = BoldItalic vàng gradient (chủ ngữ quan trọng); `vong` = vòng vẽ tay cam + mũi tên quanh dòng |
| Không lặp chữ | lời đã nằm trong tiêu đề thì sub KHÔNG nhắc lại; khi có số tiền / liệt kê, sub ẩn (chúng thay sub) |
| **CHỮ KHÔNG ĐÈ MẶT** (người dùng chốt 12/11/2026) | Mọi thứ ở LỚP TRƯỚC người — dòng dẫn, viết tay, khoá `giua`, icon nét, sub, icon 3D + nhãn, thẻ ảnh, ô tìm kiếm, số tiền, liệt kê — **KHÔNG được chạm VÙNG MẶT người nói ở BẤT KỲ khung nào** (hộp mặt MediaPipe nới ngang 12 %, lên 30 % phủ tóc, xuống 15 % phủ cằm — `C.MAT_CAM`). Khoá sau đầu thì được (đầu nằm TRƯỚC chữ, mặt không bị che). `dung` tự né theo vùng mặt suốt thời gian chữ hiện: dẫn / viết tay dời ngang dưới khoá → lên trên khoá → dạt sang bên mặt, vẫn chạm thì BỎ dòng đó; khoá `giua` lên trọn trên / xuống trọn dưới mặt; cả chuỗi sub dời xuống dưới mặt, hết chỗ thì dạt ngang; icon trên tay coi mặt là vùng cấm; icon mép / thẻ ảnh đổi bên / lên / xuống. `duyet` báo ⛔ trong bảng duyệt, tự kiểm mục 5 quét mọi khung — chạm ⇒ ⛔ |
| Thẻ ảnh (`the_anh`) | bo 22 + viền trắng 5 + bóng; **bay ra từ TAY** người nói (9 khung, 0,12→nảy→1) và thu về tay khi hết — tay đang mở thì bay từ LÒNG BÀN TAY THẬT (tay.json), không thì ước từ mặt; `dat: tay` = thẻ rộng 420 nằm ngay trên lòng bàn tay như icon; `phang` đáy khung (bảng giá) · `nghieng` 3D 22° · `xep` 3 thẻ chồng lệch (mặt bằng) · `nho` ảnh cắt NGANG 3:2 rộng 470 px (~0,45 W) bay lên dải TRÊN CÙNG sát mép an toàn trái / phải (ảnh toà nhà, cảnh minh hoạ); có tiêu đề cùng lúc thì thẻ tự thu nhỏ để đáy thẻ nằm trên đỉnh tiêu đề; nhún nhẹ ±5 px |
| Icon 3D | cỡ 175, bóng, gradient + vát mép + vệt kính + nhãn viên thuốc cùng màu. **MỌC RA TỪ BÀN TAY người nói** (chữ ký của mẫu, 6,2 s / 7,2 s): nhỏ xíu 0,12 ngay lòng bàn tay → lớn + nảy ra chỗ đặt trong 6 khung, bám 60 % chuyển động tay, nhún ±4 px, ra thì thu nhỏ về tay. Chỗ đặt: ưu tiên ngay TRÊN tay (đáy nhãn cách lòng bàn tay 14 px); tay trước ngực mà trên tay đè mặt / sub / tiêu đề / liệt kê / số tiền / ô tìm kiếm ⇒ lách ra phía NGOÀI người, lên trên hoặc ngang tay (tính 1 lần cho cả đoạn, không giật). 1 tay giữ 1 icon một lúc (2 tay = 2 icon), không vắt qua cú cắt. Không thấy tay ⇒ trái 17 % / phải 83 % ngang vai, trượt từ mép vào + nảy, nhún ±10 px, né tiêu đề. **Mật độ: mỗi lần nói chữ đắt mà tay rảnh → 1 icon (~1 icon / 3–5 s)**, như mẫu 10 s đầu (5 đồ hoạ từ tay). 15 loại: vi_tri, tien_ich / truong_hoc, nha, tien, cong_vien, benh_vien, mua_sam, giao_thong, sao, phong_ngu (giường), binh_luan (chat), ho_nuoc (sóng — view hồ / sông / vịnh / biển), tim, chia_khoa |
| Ô tìm kiếm | trắng bo tròn 900×104, kính lúp + micro; trượt từ trái to 1,35→1, **gõ 1 ký tự/khung** có con trỏ `_` (xong thì nhấp nháy); ngay dưới sub; ra = mờ + nhoè |
| Số tiền | dòng trên = sub ("Có căn"); số Anton 168 vàng gradient dưới, **vệt tốc độ ≫ vàng 3 khung trước** rồi số trượt từ trái nhoè ngang; dòng dưới nghiêng ("Hơn", "Gần") + icon túi tiền; số mới đẩy số cũ ra phải |
| Logo | rộng 86 % khung, rơi từ trên (12 khung) nằm SAU người, đỉnh y 70 |
| Liệt kê | chữ khoá tím to ("Là") bên trái ngang ngực + các dòng trượt từ phải vào, tối đa 3 dòng |
| Chuyển cảnh | CHỈ ở chỗ **đổi bối cảnh** (cut.json `boi_canh`); cùng bối cảnh = cắt + đổi zoom. Xoay vòng: `zoom_nhoe` (phóng 1→1,38 + nhoè toả tròn, 4+5 khung) · `loe_doc` (tia sáng dọc quét ngang + loé) · `chay_phim` (cam bốc từ đáy → trắng → đỏ quét trái) · `tach_mau` (tách RGB 26 px + nhoè + rung). `loe_doc`/`chay_phim` có riser 1,35 s trước |
| Tiếng | giọng gốc; nhạc beat (người dùng đưa) thấp hơn giọng 9 dB lúc nói, +3 dB ở khe; SFX theo loại sự kiện (`SFX_NHOM`), đỉnh 10 ms so với giọng TẠI CHỖ theo `SFX_TO`, ≤ 1 tiếng / 0,30 s, tiếng PHỤ (lấp lánh, nhấn sub, liệt kê, vòng vẽ, chữ to) phải cách mọi tiếng khác ≥ 0,7 s, lấp lánh chỉ khi khoá vào kiểu `phong` / `tu_dau`; 1 file không lặp trong 4 s, xoay biến thể ⇒ mật độ ~1 tiếng / 2 s như mẫu; master −14 LUFS, TP −1,5 |

## Cài đặt (máy mới)

- Python 3.10+, ffmpeg/ffprobe trong PATH. `python -I -m pip install -r requirements.txt` (trong thư mục skill).
- **Tách người** (bắt buộc cho tiêu đề sau đầu): `u2net_human_seg.onnx` (175 MB, không lên git). Skill tìm ở
  `assets/models/` rồi `~/.u2net/` (rembg tự tải về đó: `python -I -c "from rembg import new_session; new_session('u2net_human_seg')"`).
  Không có → tiêu đề nằm TRÊN người, tự kiểm mục 4 báo ⛔.
- **Dò bàn tay** (để icon / thẻ mọc từ tay): `run.py cai-tay` 1 lần / máy (cần mạng, ~150 MB) — tạo venv RIÊNG
  `~/.bds_sale_viral/venv_tay` + mediapipe 0.10.21 (cần numpy < 2, protobuf < 5 — KHÔNG cài vào Python chính kẻo vỡ
  skill khác). Không có venv → dò từ mặt nạ người, chỉ bắt được lúc DANG TAY ngang (kiem-kh báo ⚠).
- Dò mặt: `phan-tich` dùng `det_10g.onnx` nếu có, không thì Haar OpenCV (nhanh, chỉ để lập nháp). `run.py nguoi` thay bằng
  **MediaPipe FaceDetection tầm xa + Pose** (`mat_mp.py`, cùng venv tay, ~1 phút / 2 phút video) → `mat.json` mới (Haar cũ
  giữ ở `mat_haar.json`): bắt cả lúc nghiêng / đi / quay lưng (ONE ERA: Haar 37 % → MediaPipe 100 % mẫu). Không có venv
  ⇒ vẫn Haar, khung mặt đoán không được bảo vệ (tự kiểm mục 5 ghi % khung có mặt thật). Máy đã `cai-tay` trước đó
  không phải cài thêm (FaceDetection + Pose có sẵn trong gói mediapipe). Work cũ (mat.json Haar) ⇒ `dung` tự dò mặt
  MediaPipe + tách người lại.
- SFX trong `assets/sfx/` từ thư viện sưu tầm không rõ giấy phép (`assets/sfx/CREDITS.md`) — làm thương mại thì thay
  file cùng tên.

## Quy trình khi được gọi

Mọi lệnh: `python -I -X utf8 .claude\skills\bds-sale-viral\scripts\run.py <lệnh> …` (chạy từ thư mục dự án).

1. **Phân tích** — `run.py phan-tich --video "<video thô>" [--res "<thư mục ảnh/clip/logo/nhạc>"] [--nhac <file>] [--ten "<tên dự án>"] [--cat-lang auto|co|khong]`
   → `<video>_bsv_work\`: `nguon.mp4` (1080×1920/30, cắt lặng theo năng lượng nếu quay thô — `auto` tự quyết, video
   đã dựng sẵn thì không cắt), `giong.wav`, `words.json` (Whisper large-v3 CPU, lần đầu tải ~3 GB — đợi, đừng huỷ),
   `mat.json`, `cut.json` (`boi_canh` / `nhay`), `tai_nguyen.json` + `tai_nguyen.jpg`, `loi_doc.txt`, `ke_hoach.json` NHÁP. Thoát mã 2.
2. **Ngay sau đó chạy nền** `run.py nguoi --work <dir>` (trước hết dò MẶT + ĐẦU bằng MediaPipe → `mat.json` mới, ~1 phút;
   rồi tách người CPU cách 2 khung lấy 1 quanh mặt mới, ~0,4–0,8 s/lần ⇒ 1 phút video ≈ 10–12 phút (Test.mp4 115 s: 22 phút) — chạy nền trong lúc Claude
   viết kế hoạch, đặt thời gian chờ dài; `mat.json` đổi thì tách người tự chạy lại). Xong thì tự **dò BÀN TAY** (`tay.py` → MediaPipe 21 điểm, ~35 s / phút video): mỗi tay là RẢNH (không sát miệng — tay cầm mic bị bỏ; lòng bàn tay ở tầm ngực–hông; không buông thõng) và XOÈ / DANG (≥ 3 ngón duỗi hoặc cách tâm mặt ≥ 1,4 × cao mặt = nhịp đẹp để icon bật); đoạn tay rảnh tách ở mọi cú cắt → `tay.json` (cu_chi + **goi_y**: icon gợi ý = từ khoá trong lời `C.ICON_TU` trùng lúc tay rảnh, bật đúng nhịp xoè gần nhất) + `tay.jpg` (vòng vàng ở lòng bàn tay + lời đang nói). Dò lại: `run.py tay`; chép gợi ý vào kế hoạch: `run.py tay --gop` (tự bỏ cái trùng giờ với icon / thẻ có sẵn và cái có nhãn đang nằm trong tiêu đề / liệt kê).
3. **Claude sửa `ke_hoach.json` theo NGHĨA** (bắt buộc — nháp chỉ chia máy móc). Mở `loi_doc.txt`, `tai_nguyen.jpg`,
   vài khung nguồn (`ffmpeg -ss <t> -i nguon.mp4 -frames:v 1 x.jpg`) để biết bối cảnh. Làm theo `examples/plan_mau.json`:
   - mỗi CÂU 1 tiêu đề: khoá = 1–2 chữ ĐẮT NHẤT của vế đầu (động từ / danh từ chốt: "TÌM MUA", "Thông Tin", "QUAN TRỌNG",
     "Lý do", "TÀI SẢN LỚN"), dẫn = chữ đứng trước, viết tay = 1–3 chữ đứng sau; chữ phải là CHỮ TRONG LỜI.
     Câu ngắn < 2 s hoặc câu nối tiếp ý → không tiêu đề, chỉ sub. Tiêu đề cuối `ra: vo_chu`; trước chuyển cảnh `troi_xuong`.
   - sub: lời còn lại chia cụm 1–4 chữ theo nhịp nói; số / đơn vị / chữ cần nhấn đặt trong `[..]`; 1 chữ cảm thán
     hoặc chủ đề ("Sale") → `kieu: to`; chủ ngữ trang trọng ("Người tư vấn") → `vang`; cụm 2 vế → 2 dòng.
   - **ICON TRÊN TAY là chữ ký của phong cách này — không được để video chỉ có chữ.** Mở `tay.jpg`, chạy `run.py tay --gop`
     rồi SỬA từng icon theo nghĩa: nhãn = 1–2 chữ đắt đang nói (tên riêng đầy đủ: "Sport District", "Vịnh Di Sản"), không
     trùng chữ tiêu đề đang hiện (trùng sub thì được — mẫu: sub "Phân tích VỊ TRÍ" + icon "Vị trí"), `loai` gần nghĩa nhất
     (phòng ngủ → phong_ngu, view / hồ / sông / vịnh / biển / thuỷ cung → ho_nuoc, bình luận → binh_luan, tận hưởng / kỳ nghỉ →
     tim, sở hữu / bàn giao → chia_khoa, giá → tien, vị trí → vi_tri, tiện ích / trường → tien_ich, golf / thể thao →
     cong_vien, đặc biệt / quốc tế → sao…), xoay loại cho đỡ lặp; bỏ icon < 0,8 s hoặc sát chuyển cảnh; THÊM icon ở đoạn tay
     rảnh dài chưa có (kiem-kh báo ⚠ "tay rảnh ≥ 6 s không icon"). Mục tiêu ~1 icon / 3–5 s khi tay rảnh. Thẻ ảnh `tu: tay_*`
     cũng bay ra từ lòng bàn tay thật. Video tay cầm mic + tay kia sau lưng (0 tay rảnh) thì icon trượt từ mép như cũ — báo
     người dùng ở cổng duyệt, khuyên lần sau quay tay rảnh đưa ra trước người khi nói ý chính.
   - đồ hoạ theo nghĩa: nói "bảng giá / mặt bằng / phối cảnh" mà Resources có → `the_anh`; "vị trí / tiện ích / trường…"
     → `icon`; "tự tìm hiểu / lên mạng" → `tim_kiem` gõ tên dự án; nói giá → `so_tien` (số CHỈ lấy từ lời); đọc tên dự án
     mà có logo → `logo`; liệt kê "là…, là…, hay…" → `liet_ke`; câu chốt ý quan trọng → `vong` trên 1 dòng sub.
   - `chuyen` ở MỌI cú `boi_canh` trong cut.json (xoay 4 kiểu), `zoom` ở cú `nhay` + đầu câu.
   - đặt `"CAN_CLAUDE_SUA": false`.
4. `run.py kiem-kh --work <dir>` → sửa hết ⛔, xem ⚠.
5. `run.py duyet --work <dir>` → **mở `duyet.jpg`** soi: chữ khoá có bị đầu che quá nửa không, sub có đè mặt / chồng
   ô tìm kiếm không, chính tả có dấu đúng chưa; bảng duyệt mục **"Chữ đè mặt người nói"** phải ✅ (⛔ = dời giờ / đổi bên /
   bỏ chữ đó). Sửa rồi chạy lại.
6. **CỔNG DUYỆT (DỪNG 1 lần)** — gửi `bang_duyet.md` + `duyet.jpg`, hỏi các câu ở mục DIALOG, chờ trả lời.
7. `run.py dung --work <dir> [--out <file>]` → trộn tiếng → dựng (mã hoá 1 lần, ~0,1–0,2 s/khung) → tự kiểm 9 mục.
   Ra `<video>_BSV.mp4` cạnh video gốc (có rồi thì `_BSV_ban2`…).
8. **Mở `soat.jpg`** soi bằng mắt; mục nào ⛔ thì sửa kế hoạch → `dung` lại. Giao: đường dẫn, độ dài, khổ, bảng đồ hoạ, mục còn đoán.

## DIALOG ở cổng duyệt (hỏi lại tất cả mỗi lần — lựa chọn cũ chỉ là gợi ý)

| # | Câu hỏi | Mặc định đề xuất |
|---|---|---|
| D1 | Nội dung chữ: tiêu đề từng câu (dẫn / KHOÁ / viết tay) + các cụm sub nhấn có đúng ý không? | như bảng duyệt |
| D2 | Đồ hoạ theo nghĩa: thẻ ảnh nào dùng file nào, icon, ô tìm kiếm gõ chữ gì, số tiền, logo, liệt kê — thêm / bớt? | như bảng |
| D3 | Nhạc nền: file nào? (mẫu dùng beat lo-fi ~93 BPM; skill KHÔNG tự tổng hợp nhạc) — hoặc không nhạc | file người dùng đưa |
| D4 | Tên dự án / số liệu trên hình (giá, diện tích) — đúng chưa? Mục nào ĐOÁN thì hỏi | chỉ số có trong lời |
| D5 | Cắt lặng: có / không (video quay thô có / đã dựng sẵn không) | theo `auto` |
| D6 | Mức SFX: như mẫu (~1 tiếng / 2 s) / ít hơn / tắt | như mẫu |

Không hỏi lại kiểu chữ, kiểu sub, màu khoá, kiểu chuyển cảnh (đã chốt theo mẫu) trừ khi người dùng tự nêu.

## ke_hoach.json — các khoá

```
CAN_CLAUDE_SUA  true ở bản nháp; Claude sửa xong đặt false (dung từ chối nếu còn true)
dur, video_goc, cat_lang, ten_du_an
nhac (đường dẫn | null), nhac_ss (giây bắt đầu trong file nhạc), nhac_duoi_giong_db (mặc định 9)
sfx (true/false), sfx_them [{t, nhom|file, db}], sfx_bo [giây]   — nhóm SFX: xem C.SFX_NHOM
zoom    [{t, z}]                 z ∈ {1.0, 1.15, 1.28} (nhảy tức thì)
chuyen  [{t, kieu}]              kieu ∈ zoom_nhoe | loe_doc | chay_phim | tach_mau ; t = đúng mốc cú đổi bối cảnh
tieu_de [{t0, t1, dan, khoa, viet_tay, kieu, vao, ra, icon?, vi_tri?, dan_kieu?, font_viet_tay?, mau?}]
        kieu ∈ cam|tim|nau|vang|cam_nghieng ; vao ∈ roi|phong|truot|tu_dau ; ra ∈ chui_dau|troi_xuong|vo_chu
        icon ∈ chia_khoa_nha|tui_tien|bieu_do (icon nét vàng cạnh khoá) ; vi_tri: tren (mặc định, sau đầu) | giua
        dan_kieu: viet_tay (dòng dẫn kiểu bút lông Pacifico, như "Bởi với 1") ; mau: [r,g,b] đổi màu khoá tuỳ ý
sub     [{t0, t1, vao?, dong: [{text, kieu?, t?, vong?}]}]
        kieu dòng ∈ chinh (dòng 1) | phu (dòng 2 nghiêng) | to | vang | list ; t = dòng hiện trễ ; [..] = nhấn hồng-đỏ
        cụm sau nối liền cụm trước (≤ 0,1 s) → đẩy ngang; dòng 1 trùng chữ cụm trước → đứng yên
the_anh [{t0, t1, nguon:[file ảnh/clip], tu: tay_trai|tay_phai|giua|[x,y], dat: duoi|giua|tren_trai|tren_phai|trai_duoi,
          kieu: phang|nghieng|xep|nho, rong?, giay?, tay?}]  (clip → lấy khung giữa hoặc giây `giay`; dat: tay = nằm trên lòng bàn tay)
icon    [{t0, t1, loai, nhan, ben: trai|phai, y?, mau?, tay?}] loai: vi_tri tien_ich truong_hoc nha tien cong_vien benh_vien mua_sam
        giao_thong sao phong_ngu binh_luan ho_nuoc tim chia_khoa ; ben = bên TRÁI / PHẢI KHUNG HÌNH (người xem)
        tay (mặc định true): tay rảnh trong [t0 − 0,4; t0 + 0,6] s → mọc từ bàn tay (đúng `ben` trước, rồi tay kia nếu tay
        kia không bận), t0 thực = lúc tay bắt đầu rảnh nếu muộn hơn; false = luôn trượt từ mép. SFX pop tự dời theo t0 thực
tim_kiem [{t0, t1, chu, t_go, y?}]
so_tien [{t0, t1, tren, so:[{t, text, duoi}], icon?}]      text kiểu "5.000.000.000"; icon: tui_tien
logo    [{t0, t1, nguon, rong?, sau_nguoi?}]
liet_ke [{t0, t1, khoa, kieu, dong:[{t, text}]}]
```

## Bẫy đã biết

- `python -I` bỏ qua PYTHONUTF8 → luôn `-X utf8`; `-I` cũng bỏ thư mục script khỏi sys.path → run.py tự chèn.
- Phông biến thiên (Baloo2, DancingScript) mặc định Regular → `chung.font` tự đặt ExtraBold/Bold.
- faster-whisper đọc file qua PyAV hay lỗi `metadata_errors` → đọc wav bằng `wave` rồi đưa mảng numpy.
- Tiêu đề sau đầu cần mặt nạ người: thiếu `nguoi_mask.npy` thì `dung` tự chạy tách người (thêm vài phút); xem trước
  (`duyet`) tính tại chỗ từng khung.
- Cận mặt (mặt to) → khoá bị đầu che nhiều: tự kiểm mục 4 báo; sửa bằng giảm `zoom` đoạn đó hoặc `vi_tri: giua`.
- Ảnh soát thu nhỏ có thể làm mất dấu sắc nhỏ ("Đó là") — mở khung gốc trước khi kết luận lỗi chính tả.
- Haar (không có det_10g) hay bắt nhầm "mặt" ở mép khung (cây, biển hiệu) → `phan_tich.chon_mat` giữ ứng viên lặp lại
  trong ±3 s cùng bối cảnh. Thấy tiêu đề / sub lệch hẳn khỏi người trong `duyet.jpg` thì mở `mat.json` kiểm đoạn đó.
- Thẻ `nho` từ CLIP mặc định lấy khung giữa, có thể tối / vô nghĩa → mở `tai_nguyen.jpg`, đặt `giay` vào khung đẹp
  hợp lời (vd "hoàng hôn" → khung hoàng hôn); 1 clip dùng 2 lần thì 2 `giay` khác nhau.
- Whisper nghe sai tên riêng / tiếng Anh (golf → "gốc", view → "viêu", VinWonders, hecta…) → sửa chữ trong tiêu đề /
  sub theo nghĩa; tên dự án không chắc thì ghi ĐOÁN và hỏi ở cổng duyệt.
- Dò tay bản đầu (chỉ mặt nạ người) chỉ bắt DANG TAY ngang ⇒ BDS_1 54 s chỉ ra 1 cử chỉ, video gần như toàn chữ — người
  dùng chê "khác gì skill khác". Bản MediaPipe: tay nói chuyện bình thường là tay KHUM trước ngực (đếm 0–2 ngón duỗi) — nếu
  đòi xoè ≥ 3 ngón thì loại gần hết ⇒ điều kiện là tay RẢNH, xoè chỉ để chọn nhịp bật.
- mediapipe 0.10.21 đòi numpy < 2 / protobuf < 5 — Python chính đang numpy 2.x ⇒ luôn venv riêng (`run.py cai-tay`), gọi
  qua subprocess `tay_mp.py` với `-X utf8` (console cp1252 làm script con chết khi in tiếng Việt).
- Khớp từ khoá CÓ DẤU (bỏ dấu thì "sống" khớp nhầm "sông" → icon sóng nước sai nghĩa).
- Người đứng nghiêng (dự phòng mặt nạ): khuỷu tay chìa ra xa tâm mặt ~2,2 × cao mặt ⇒ điều kiện NHÔ (hàng trên điểm xa nhất
  lùi vào ≥ 0,45 × cao mặt). Icon đặt sai tay thì mở `tay.jpg`, icon đó `tay: false`.
- Whisper trên video DÀI nói liền (tour nhà mẫu 135 s, mic cài áo nén −9,8 LUFS) mà nối ngữ cảnh ⇒ ra toàn câu ảo giác
  "Hãy subscribe cho kênh Ghiền Mì Gõ…" (75 chữ / 135 s) ⇒ `nghe()` dùng vad + `condition_on_previous_text=False` +
  highpass 90 Hz + hạ 8 dB, bỏ đoạn khớp `AO_GIAC`; < 1 chữ/s thì phan-tich báo ⚠ — mở `loi_doc.txt` trước khi viết kế hoạch.
- Máy quay CẦM TAY ĐI BỘ: điểm scene 0,10–0,25 liên tục ⇒ ngưỡng cứng bắt 100 "cú nhảy" giả (băm vụn đoạn tay, zoom nhảy
  loạn) ⇒ `do_cat` chỉ nhận ĐỈNH ≥ 2,5 × nền p90 ±1,5 s (BDS_1 vẫn đủ 7 cú thật, ONE ERA còn 3 cú đổi bối cảnh thật).
- Haar chỉ thấy mặt NHÌN THẲNG: ONE ERA (đi dọc tường, quay nghiêng) mất mặt 63 % mẫu → mặt bị CHÉP từ mẫu khác ⇒ sub /
  viết tay / icon xếp theo chỗ mặt SAI, tách người cắt ô quanh mặt sai ⇒ người dùng: "text không được đè vào mặt diễn giả"
  ⇒ `run.py nguoi` dò mặt + đầu bằng MediaPipe (FaceDetection + Pose) trước khi tách người; mọi chữ lớp trước né
  `C.MAT_CAM`; tự kiểm mục 5 quét mọi khung. Thấy chữ sát mặt trong `soat.jpg` mà mục 5 ✅ ⇒ mở `mat.json` (`nguon`) đoạn đó.
- Người QUAY LƯNG / đi ngang sát máy (Haar không thấy mặt): đầu che TRỌN mấy chữ khoá ("IAI THƯỞNG", "KIM __NH") ⇒
  soi `duyet.jpg`, tiêu đề đó `vi_tri: giua`.
- Dòng dẫn đè 22 % đỉnh khoá từng che DẤU trên chữ hoa ("Trưng bày" che dấu hỏi ⇒ "GIAI THƯỞNG") ⇒ `dung._dau_tren` tự
  nâng dòng dẫn lên trên dấu.
- Giọng gốc nén sát 0 dBFS: master wav TP −1,4 nhưng mã hoá AAC vọt −0,9 dBTP ⇒ tự kiểm ⛔ ⇒ `AM['tp']` −2,0 + limiter
  sau loudnorm trong `am_thanh.tron`.
- Sub bám ngang theo người: người đi sát mép thì dòng sub tràn ra ngoài vùng an toàn ⇒ mỗi dòng tự kẹp trong `AN_TOAN`.
- Tên riêng Whisper nghe không ra (đối tác "Long4") ⇒ soi khung hình lúc người nói chỉ vào biển / tường: ONE ERA ghi rõ
  LONGFOR. Chữ trên hình là nguồn xác minh tốt nhất cho tên riêng.

## Skill này được bồi thêm sau mỗi lần chạy thật

| Ngày | Video | Góp ý người dùng → đã sửa |
|---|---|---|
| 12/11/2026 | dựng skill từ video_mau.mp4; chạy thử trên BDS_1/video_final_capcut.mp4 (54 s, 11 tiêu đề, 34 cụm sub, 4 thẻ ảnh, 2 icon, ô tìm kiếm, liệt kê, 5 chuyển cảnh, 30 SFX) | Claude tự soát: đáy khoá theo đỉnh đầu từ mặt nạ (trước đó chữ nằm trên đầu); dẫn / viết tay ra lớp trước người; thẻ `nho` ngang 3:2 ở dải trên, né tiêu đề; icon né tiêu đề; SFX thưa lại (37 → 30); viết tay thêm viền + bóng. Tự kiểm 7 ✅ · 2 ⚠ (thiếu nhạc, soát mắt). **Người dùng DUYỆT skill 12/11/2026** — bản test chuẩn: `video_final_capcut_HHR_ban2.mp4` (dựng khi skill còn tên cũ `het-hon-real-edit`) |
| 12/11/2026 | — | Đổi tên 2 lần theo người dùng: "nghĩ tên skill khác, tránh trùng" → `het-hon-real-edit` thành `nns-nguoi-noi-tieu-de-sau-dau`; "nghe tên skill chán, nghĩ lại, bds gì đó" → chọn **`bds-sale-viral`**. Đuôi ra `_HHR` → `_BSV`, thư mục work `_hhr_work` → `_bsv_work` |
| 12/11/2026 | Chinh Lê Vinhomes/Done.mp4 (15,9 s, 1 người nữ đứng xa, 1 bối cảnh) | Claude tự soát `duyet.jpg`: người đứng xa (mặt ~130 px) ⇒ khoá nằm hẳn TRÊN đầu, không giống mẫu → thêm `TIEU_DE['de_khoa_min']` 0,30 (đầu luôn che ≥ 30 % chiều cao khoá); sub đệm "Anh chị nhé" đè thẻ bản đồ đáy khung → bỏ sub đệm khi có thẻ `duoi` |
| 12/11/2026 | — | Người dùng: "video mẫu có icon đưa tay ra là hiệu ứng ra đẹp lắm, sao bản dựng không có" → **nâng cấp**: `tay.py` dò cử chỉ mở tay từ mặt nạ người (thử trên khung mẫu 6,3 / 7,0 / 20 / 30 s đúng lòng bàn tay; BDS_1 ra 45,8 s mở 2 tay), icon + thẻ ảnh mọc ra từ lòng bàn tay thật, SFX dời theo, kiem-kh / bảng duyệt báo cử chỉ; thêm 5 icon phong_ngu, binh_luan, ho_nuoc, tim, chia_khoa. Done.mp4: 0 cử chỉ (cầm mic) ⇒ icon trượt từ mép như cũ. Bản thử: `video_final_capcut_BSV_ban2.mp4` (icon "Thế giới" + "Tận hưởng" trên 2 tay ở 45,8 s) |
| 12/11/2026 | BDS_1/video_final_capcut.mp4 | Người dùng: "trong video có nhiều đoạn mà không thấy icon tự đưa / tự hiện theo tay diễn giả, chỉ text thì khác gì skill khác" → dò tay bằng **MediaPipe** (venv riêng, `run.py cai-tay`), tay RẢNH (không cầm mic) là chỗ icon mọc, xoè / dang = nhịp bật; icon tự lách khỏi mặt / sub / tiêu đề / liệt kê; **icon gợi ý tự động** từ lời + tay (`run.py tay --gop`); kiem-kh báo đoạn tay rảnh ≥ 6 s chưa có icon. BDS_1: 1 → 8 đoạn tay rảnh (gần trọn video), 2 → 11 icon + 4 thẻ ảnh đều mọc từ tay. Bản thử `video_final_capcut_BSV_ban3.mp4` |
| 12/11/2026 | BDS_1/Test.mp4 (135 s, tour nhà mẫu ONE ERA — Kim Oanh, máy quay đi bộ, 2 tay rảnh, mic cài áo) | Claude tự soát: Whisper ảo giác cả video → sửa `nghe()` (vad, không nối ngữ cảnh) ra 511 chữ đúng; 100 cú nhảy giả do máy đi bộ → dò cú cắt theo đỉnh so với nền (còn 3 cú thật); dòng dẫn che dấu chữ hoa → tự nâng; 3 tiêu đề người quay lưng → `giua`; kiem-kh tính khoảng tay trống từ lúc icon KẾT THÚC. Kế hoạch: 19 tiêu đề, 57 cụm sub, 23 icon (22 mọc từ tay, liệt kê tiện ích → 3 icon nối tiếp trên tay phải). Người dùng duyệt ngay. Bản đầu `Test_BSV.mp4` tự kiểm ⛔ đỉnh −0,9 dBTP + ⚠ sub tràn mép → TP −2,0 + limiter, kẹp sub vào vùng an toàn, thêm "LONGFOR" (đọc trên tường) → `Test_BSV_ban2.mp4` |
| 12/11/2026 | BDS_1/Test.mp4 bản mới (115 s, cùng tour ONE ERA đã cắt gọn) | Chạy lại sạch bằng skill vừa đẩy git → `Test_BSV.mp4` 7 ✅. Người dùng: **"ghi vào là text không được đè vào mặt của diễn giả đang nói trong video"** → luật CHỮ KHÔNG ĐÈ MẶT (bảng phong cách): dò mặt + đầu MediaPipe (`mat_mp.py`, Haar chỉ thấy 37 % mẫu → 100 %), tách người lại theo mặt mới, mọi lớp chữ trước người né `C.MAT_CAM` (dẫn / viết tay dời hoặc bỏ, khoá `giua` lên trên / xuống dưới mặt, sub dời xuống, icon coi mặt là vùng cấm), `duyet` báo ⛔ + tự kiểm mục 5 quét mọi khung → `Test_BSV_ban2.mp4` (7 ✅ · 2 ⚠ · 0 ⛔, mục 5 ✅ mặt thật 100 % khung; soi phóng to 8 khung tiêu đề sát đầu: không chữ nào đè mặt, khoá sau đầu giữ đúng kiểu mẫu; dòng dẫn "Anh chị nào" của tiêu đề cuối bị bỏ vì cận mặt hết chỗ) |
