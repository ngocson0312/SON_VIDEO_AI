---
name: bds_model_3d
description: Dựng VIDEO BĐS / hướng dẫn dạng MOTION GRAPHIC dọc 9:16 tiếng Việt theo ĐÚNG phong cách video mẫu Khánh Nguyễn (D:\____TTT_____\KH_Test\Khánh_Nguyễn\Video_Mẫu.mp4, đo từng khung 12/11/2026) — giọng đọc là xương sống; footage (video dự án / video kết quả / flycam / ảnh) nằm trong THẺ NỔI NGHIÊNG 3D bo góc viền sáng trên nền than #101116 ở hook, PHÓNG TRÀN MÀN khi khoe, NHOÈ + TỐI làm nền cho đồ hoạ; CHỮ 2 TẦNG Be Vietnam Pro (dẫn trắng nhỏ Regular + KHOÁ to vàng chanh #FDF02A ExtraBold Italic / trắng ExtraBold) hiện TỪNG TỪ nhoè→nét trước lời 0,22 s, ra nhoè-mờ; VIÊN KÍNH (kính mờ bo tròn + icon app) + GẠCH NGANG quét khi lời bác bỏ cách cũ ("không cần After Effects"); HÀNG Ô KÍNH đánh số bật lần lượt khi liệt kê N bước; "BƯỚC N" vàng + tít trắng + THẺ GIAO DIỆN APP MÔ PHỎNG có thao tác (Google Maps: gõ tìm, ghim rơi, bảng trượt, chạm copy, thông báo; chat AI kiểu Claude: chip dán, tệp PDF, gõ prompt, gửi, đang làm + checklist, thả video mẫu; hoặc ảnh / quay màn hình thật); KẾT QUẢ trồi từ thẻ lên tràn màn, nhạc dâng; CTA iPHONE NGHIÊNG 3D chat 'Khách hàng' (bong bóng từ khoá → đang gõ → thẻ tài liệu → trả lời); không cắt cứng (hoà tan mờ / phóng thẻ / nhoè nền); SFX pop-click ngắn ở mọi vật hiện + gõ phím; nhạc né lời −23 dB, dâng +16 dB ở khoảng lặng; −14 LUFS, đỉnh ≤ −1 dBTP; dựng bằng Chrome headless (khung HTML tất định) mã hoá 1 lần; tự kiểm. CẢNH 3D CÔNG TRÌNH (như 0–9 s của mẫu): chỉ cần GIỌNG + ẢNH PHỐI CẢNH dự án — Claude đọc ảnh ra mô hình tham số (tháp kính vạch sàn, vườn treo đèn ấm, chân cột, vương miện lượn sóng, khối đế lam nâu cửa sáng, hồ bơi, cọ, cây, nhà phố mái ngói) đặt đúng lô đất trên ẢNH VỆ TINH THẬT (Esri), camera bay vòng nội suy êm, chân trời sương, vòng vàng, thẻ logo vàng, chú thích chấm-gạch bám công trình, nhãn địa danh, chữ 2 tầng trong cảnh, tia nắng — dựng Three.js trong Chrome thành footage cho thẻ nổi / tràn màn / nền nhoè. Đầu vào: 1 video có giọng, HOẶC 1 file giọng + thư mục clip/ảnh/quay màn hình (thêm --3d để dựng cảnh 3D từ ảnh). Whisper nhận lời → Claude viết ke_hoach.json theo NGHĨA (khuôn 6 phần) → DỪNG 1 lần ở cổng duyệt → dựng → tự kiểm. Trigger '/bds_model_3d', 'edit video như video mẫu Khánh Nguyễn', 'dựng video kiểu thẻ nổi 3D + chữ vàng', 'video hướng dẫn có giao diện Google Maps / chat AI', 'làm video BĐS model 3D', 'edit video này kiểu bds model 3d', 'dựng mô hình 3D dự án từ ảnh', 'video 3D dự án trên bản đồ vệ tinh', 'chỉ có giọng + ảnh phối cảnh, dựng 3D như video mẫu'.
---

# bds_model_3d — video BĐS / hướng dẫn kiểu "thẻ nổi 3D + chữ 2 tầng + giao diện app"

Người dùng đưa **1 video có giọng** (hoặc **1 file giọng + thư mục clip / ảnh / quay màn hình**). Skill dựng ra video giống
mẫu `D:\____TTT_____\KH_Test\Khánh_Nguyễn\Video_Mẫu.mp4` từ chữ, khối kính, giao diện app, chuyển cảnh, SFX tới âm lượng —
chỉ khác nội dung là của người dùng.

- Phân tích từng khung của mẫu: **`references/phan-tich-mau.md`** + ảnh **`references/bang_phong_cach.jpg`** (đọc trước khi sửa bất kỳ số nào).
- Khuôn kế hoạch: **`references/ke_hoach_schema.md`**; bản điền chuẩn dựng lại đúng mẫu: **`references/vi-du-video-mau.json`**.
- **Cảnh 3D công trình** (giọng + ảnh phối cảnh → mô hình 3D trên ảnh vệ tinh): **`references/mo_hinh_3d.md`**; bản điền chuẩn: **`references/vi-du-3d.json`** (dựng lại mẫu, cảnh 3D thay footage).
- Số phong cách: `scripts/chung.py` (cỡ chữ vị trí, bảng SFX, mức nhạc) + `assets/khung/bds3d.css|js` (hình khối, chuyển động). Không rải số ra chỗ khác.

## Skill này được bồi thêm sau mỗi lần chạy thật

| Ngày | Video | Góp ý / sửa |
|---|---|---|
| 12/11/2026 | dựng lại mẫu (giọng mẫu + video map Vinhomes Olympic làm footage) | bản đầu; so khung cạnh mẫu → sửa iPhone nghiêng ngược chiều + chữ trong máy to hơn + thẻ tài liệu khung đen dày, kính mất mờ, icon Maps thành ô vuông, đỉnh AAC vượt −1 dBTP |
| 12/11/2026 | người dùng: "cái tôi muốn là đoạn 3–9 s, 3D xịn như kia, chỉ truyền âm thanh + hình ảnh là dựng được" | thêm CẢNH 3D: ảnh phối cảnh → mô hình tham số trên vệ tinh thật, camera bay, chú thích bám công trình (`mo_hinh_3d.py`, `bds3d_3d.js`, `ve_tinh.py`, `xem-3d`, `tim`, `quet --3d`); so khung cạnh mẫu → nắng phải từ phía Nam, mặt kính / mái đế bớt cháy sáng, camera hook chéo cao thay vì nhìn thẳng xuống |
| 12/11/2026 | Lumi Hà Nội (CapitaLand) — người dùng chỉ đưa 3 ảnh phối cảnh: "đưa ảnh dự án vào là dựng được mô hình 3D trong video" | thêm chế độ CHỈ ẢNH (`quet --res --3d` không giọng, giọng đưa sau giữ mô hình), `bay-thu` (video câm bay quanh mô hình), bảng màu riêng từng tháp (`mau` trong tháp: kính tối + lưới khung trắng / đồng, `luoi`, `mep`, `phat`, `mai_tren`), `san_vuon` (cỏ + cây theo ranh OSM che công trường); dự án đang xây → đo vị trí 10 phiến tháp trên ảnh z19 |
| 12/11/2026 | Lumi bản 2 — người dùng: "mặt đứng giống ảnh hơn, bố cục theo ảnh, chân đế + sân vườn, số tầng" + "sau này khách đưa vào KIỂU GÌ cũng phối được model 3D" | bộ dựng TỔNG QUÁT: chân tháp `hinh` tròn / elip / bo góc / đa giác tự do (L, U, tam giác…), `lui` (tháp bậc thang), `cao_nen` (cầu nối trên cao), `buoi` ngày / hoàng hôn / đêm, cửa sổ sáng đèn `den_cua`, vương miện sáng `mai_den`, lưới khung sáng `luoi_den`, tường hồi `tuong_hoi`, `mat_dat` (hồ bơi, sân tennis / bóng rổ / pickleball / bóng đá, sân lát, đường dạo, cầu đi bộ trên tán cây); Lumi về đúng 9 tòa 29–35 tầng theo thông cáo CapitaLand |
| 12/11/2026 | Lumi bản 3 — người dùng: "XẤU QUÁ, không giống ảnh tôi gửi, cái tòa nhà, texture các thứ" | soi lại ảnh: tháp thật là các module "khung tranh" (khung đặc đồng / trắng bọc mặt kính tối nhiều ô cửa sáng ấm, tầng đỉnh sáng dưới viền) — mô hình cũ là hộp kính kẻ lưới thô. Thêm `vien` (khung viền module nổi), `mat: "can_ho"` (ô cửa căn hộ mảnh, đèn nhiều mức), `luoi_min`, `den_dinh`, tán cây chùm lá, `goc_anh` (dựng mô hình đúng góc từng ảnh, đặt cạnh ảnh để so) |
| 12/11/2026 | Lumi bản 4 — người dùng: "có cái gì cứ nhấp nha nhấp nháy, lỗi à" + "video mẫu có các đường line chạy quanh khu nhà, đang thiếu" + "nhìn cứ giả giả, có cách nào cho tòa nhà giống thật không" | nhấp nháy = chi tiết ảnh vệ tinh xa sát chân trời lấp lánh khi camera hạ thấp (không phải lỗi luồng dựng) → HẬU KỲ tự bật: siêu mẫu ×2 + nhoè theo độ sâu (xa mờ sương như ống kính) + toả sáng đèn; thêm `duong_vien` (line vàng vẽ dần quanh ranh rồi xung sáng chạy mãi, `bay-thu` tự có + vòng vàng); giống thật: buổi `chang_vang` (giờ xanh như ảnh phối cảnh), kính phản chiếu trời / phố lên đèn, chân tường tối dần, cỏ + cây nhuộm theo buổi |
| 12/11/2026 | Lumi bản 5 — người dùng chọn "Dán mặt đứng ảnh thật" | thêm `luoi-anh` (lưới toạ độ để đọc góc) + `mat-anh` (cắt 1 mặt tháp trong ảnh phối cảnh, nắn phẳng homography 4 góc → texture), tháp `anh_mat` / `anh_hoi` dán ảnh thật lên mặt dài / đầu hồi (ảnh tự phát sáng + nhận nắng 1 phần); trụ góc `vien` mang texture tường hồi (dải cửa giữa) thay mảng trơn |
| 12/11/2026 | Lumi bản 6 — người dùng: "mặt trước nhìn lệch hẳn, không thẳng, mấy cái texture ban công" | góc mặt đứng chấm bằng mắt lệch vài px trên ảnh chụp trên cao → mặt nắn ra xiên 2,7–4,6°. `mat-anh` giờ TỰ NẮN THẲNG (dò vạch cửa / sàn, dời góc tới khi thẳng, in độ xiên trước → sau, ⚠ khi còn > 1°), `_xem.jpg` thêm phóng vùng cắt + vạch đỏ để soi; cache khung 3D tính cả nội dung ảnh mặt đứng |

## ĐÃ CHỐT (không tự đổi trừ khi người dùng yêu cầu)

1. Khổ 1080×1920, 30 fps, nền than gradient #0A0B0E → #101116 → #06070A. **Không cắt cứng** — chỉ 4 kiểu chuyển: hoà tan mờ-tối 0,25 s, phóng thẻ→tràn 0,5 s, tràn→nhoè 0,7 s, đổi nội dung trong thẻ (cuộn lên).
2. Phông duy nhất **Be Vietnam Pro**. Chữ 2 tầng: dẫn Regular 43 px trắng + khoá ExtraBold Italic 74 px **#FDF02A** (hoặc ExtraBold 68 px trắng); "Bước N" Italic 52 px vàng + tít ExtraBold 62 px trắng; từ khoá CTA vàng trong ngoặc kép cong. Bóng mềm, không viền. Mép trên cụm chữ y 148 (cảnh điện thoại 100, giữa 560).
3. Chữ là **TÓM TẮT 2–6 từ** mỗi cụm lời, không sub nguyên văn, không dòng sub chạy dưới. Từng từ hiện trước lời 0,22 s (nhoè 10 px → nét 0,22 s). 2 cụm không bao giờ chồng nhau.
4. Thẻ nổi: 712×1266 tâm (550, 1158), bo 38, viền sáng 2 px, xoay −3,6° → −1,4° dần suốt hook + lắc rất nhẹ, ngả 3D (rotateX 3°, rotateY −2°), vào 0,6 s (mờ+tối+0,94 → nét 1,0).
5. Viên kính y 980 cao 122, gạch trắng 6 px quét 0,22 s rồi viên tối 45 %. Ô kính 250 px bo 26 %, y 1056, số góc trái, bật cách 0,1 s.
6. Thẻ giao diện 880×1400 tại (100, 430) bo 52, trắng (chat: kem #FAF9F5), phóng chậm +3,5 % suốt cảnh. iPhone 740×1540 tại (200, 250) nghiêng −5,5°, chữ trong máy to (từ khoá khách 60 px).
7. Âm thanh: giọng chuẩn −16 LUFS trước trộn; nhạc −23 dB dưới giọng, dâng +16 dB ở khoảng lặng ≥ 1 s (dốc 0,35 s); SFX ngắn theo bảng `SFX` (pop khi vật hiện, click khi chạm/gửi, swoosh ngắn khi trượt/phóng, gõ phím khi gõ). Master **−14 LUFS, đỉnh ≤ −1 dBTP** (đo trên file AAC cuối).
8. Không bịa thông tin dự án (tên, địa chỉ, giá, diện tích): chữ trên Maps / chat / điện thoại chỉ lấy từ lời hoặc người dùng; thiếu thì ghi `doan` và hỏi ở cổng duyệt.
9. Không ghi đè video cũ (`_ban2`, `_ban3`…). Bản gửi khách xem trước: `run.py nns` (chữ NNS mờ chạy, giữ bản sạch).
10. **Cảnh 3D** (khi người dùng chỉ có giọng + ảnh, hoặc muốn "3D như video mẫu"):
    - Nền là ảnh vệ tinh Esri thật đúng lô đất (5 lớp z19 → z11, mờ dần ra chân trời sương #B9C1C5), trời than → xám-xanh.
    - Mô hình tham số kính trắng-xanh vạch sàn đậm, nắng từ phía Nam, bóng mềm.
    - Camera luôn bay: hook chéo cao 55–65° → khoe 20–26° → xa 13–16°.
    - Lớp trên cảnh: vòng vàng #F3D23C + thẻ logo vàng kính ở hook, chú thích chấm trắng + gạch 118 px + chữ 46/27 px, chữ 2 tầng trong cảnh y 1290.
    - Cảnh 3D là FOOTAGE: mọi quy tắc thẻ nổi / chữ / SFX ở trên giữ nguyên.
    - Số trên cảnh phải có trong lời / do người dùng đưa; mô hình là ƯỚC LƯỢNG theo ảnh → hỏi D6.
    - **Ảnh khách kiểu gì cũng dựng**: không ép mọi dự án về "2 tháp hộp kính trắng". Chọn `hinh` (hộp / tròn / bo góc / đa giác), `lui`, `khoi` (biệt thự, nhà phố, cầu nối), `de`, `mat_dat`, `buoi` theo đúng ảnh — bảng "Đọc ảnh phối cảnh ra tham số" trong `references/mo_hinh_3d.md`. Số tháp / số tầng có nguồn chính thức (thông cáo chủ đầu tư) thì theo nguồn, không theo đếm ảnh.

## Cài đặt (1 lần)

- Python 3.10+ có `faster_whisper`, `numpy`, `Pillow` (cài bằng `python -I -m pip install …`); ffmpeg/ffprobe bản full.
- **Node.js ≥ 22** (dùng WebSocket có sẵn, không cần npm) + **Chrome hoặc Edge** đã cài (hoặc biến `BDS3D_CHROME=<chrome.exe>`).
- Cảnh 3D: Three.js r149 nằm sẵn `assets/khung/lib/three.min.js` (không tải lúc chạy).
  - WebGL chạy trong Chrome headless (cờ `--ignore-gpu-blocklist --enable-unsafe-swiftshader`).
  - Ảnh vệ tinh tải lần đầu (~400 ô, ~50 s, cần mạng), cache chung `SON_AI_VIDEO\_cache_tiles\esri` với các skill bản đồ — đừng xoá.
  - `requests` cho `tim` / tải ô.
- Junction: `.claude\skills\bds_model_3d` → `SON_VIDEO_AI\skills\bds_model_3d`. Whisper large-v3 dùng chung cache với các skill khác.

## Quy trình

Mọi lệnh: `python -I -X utf8 .claude\skills\bds_model_3d\scripts\run.py <lệnh> …` (chạy từ thư mục dự án).

1. **Quét** — `quet --video "<video có giọng>"` hoặc `quet --audio "<giọng>" --res "<thư mục clip/ảnh>"` (có thể thêm `--res` nhiều lần, `--nhac <file>`,
   `--tu-khoa "Claude AI,After Effects,Google Maps"` để Whisper viết đúng tên riêng). Ra thư mục work `<tên>_bds3d_work`:
   `loi_doc.txt` (câu + từng từ@giây), `footage.json`, `tai_nguyen*.jpg` (tờ khung footage có nhãn khoá@giây), `ke_hoach.json` NHÁP.
2. **Claude viết kế hoạch** — đọc `loi_doc.txt` + `ke_hoach_schema.md` + `vi-du-video-mau.json`; MỞ MỌI `tai_nguyen*.jpg`; viết lại `ke_hoach.json` theo nghĩa lời (mục "Chọn khối theo nghĩa"), chọn đoạn footage đẹp nhất cho hook / khoe / kết quả, đặt `CAN_CLAUDE_SUA=false`.
3. **Kiểm** — `kiem-kh --work <dir>`: cảnh liền nhau, giờ trong cảnh, chữ không chồng, gạch trong viên, footage đủ dài, rồi đo hộp chữ thật trong Chrome (tràn mép / đè thẻ / đè ô kính = ⛔). Sửa hết ⛔.
4. **Duyệt** — `duyet --work <dir>` → `duyet.jpg` (≤ 24 khung) + `bang_duyet.txt`. Claude MỞ `duyet.jpg` soi: chữ có đè chữ sẵn trong footage không, chữ đúng chính tả, thẻ giao diện đúng nội dung → **CỔNG DUYỆT**.
5. **Dựng** — `dung --work <dir> [--luong 3]` → `<tên>_BDS3D.mp4` cạnh file vào (3 Chrome song song, ~70–80 s cho 36 s video), tự trộn tiếng, tự chạy `kiem`.
6. **Tự kiểm** — `kiem --work <dir>`: khổ, fps, thời lượng, −14 LUFS ±0,6, đỉnh ≤ −1 dBTP, `soat.jpg` từ file cuối. Claude MỞ `soat.jpg` soi chính tả, chữ đè, khung đen/trắng. Chưa đạt thì sửa rồi dựng lại (ra `_ban2`…).
7. (Khi gửi khách xem trước) `nns --file <video>` → `<tên>_NNS_gui_khach.mp4`.

### Có CẢNH 3D công trình (giọng + ảnh phối cảnh) — chi tiết `references/mo_hinh_3d.md`

1. `quet --audio <giọng> --res <thư mục ảnh dự án> --3d --vi-tri "lat,lon"` (hoặc `--dia-chi "…"` → ĐOÁN; tìm thêm bằng `tim "<tên>"`).
   Nháp: hook `the_noi` + `tran_man` dùng `3d:bay1`, mô hình 2 tháp mẫu, camera bay mặc định.
2. Claude MỞ MỌI ảnh dự án và đếm: tháp, tầng (vạch sàn), vườn treo, chân cột, khối đế, hồ bơi, màu kính / đế, kiểu mái. Sau đó viết `mo_hinh_3d`.
   Lô đất phải là đất trống / công trường trên ảnh vệ tinh.
3. `xem-3d --work <dir>` → MỞ `mo_hinh_3d.jpg` (ảnh dự án cạnh mô hình 6 góc), sửa tới khi giống. Thường 2–3 vòng, mỗi vòng ~10 s.
   - **Giống thật nhất = dán mặt đứng ảnh thật** (tháp hộp, có ảnh chụp trên cao): `luoi-anh --anh <ảnh> --vung x0,y0,x1,y1 --to 3` đọc 4 góc
     mặt tháp → `mat-anh --work <dir> --anh <ảnh> --goc "TL TR BR BL" --id <id>` → MỞ `mat_anh\<id>_xem.jpg` → tháp `"anh_mat": "<id>"`
     (+ `anh_hoi`). Cắt 2–3 mặt mỗi kiểu, xen kẽ giữa các tháp. Chi tiết + giới hạn: `references/mo_hinh_3d.md`.
4. Viết `canh_3d`:
   - camera theo nhịp lời (hook chéo cao + vòng + logo, khoe gần + chú thích số liệu, lượt xa + địa danh, kết quả vòng hồ bơi);
   - chữ trong cảnh = thông tin dự án, chữ ngoài = tóm tắt lời.
5. `kiem-kh` → `duyet` → `dung` như trên.
   - `kiem-kh` tự đo chú thích / logo / địa danh ra khung, đè nhau, sau lưng camera.
   - `duyet` dựng khung 3D (~13 khung/s, có cache theo nội dung).

**Chỉ có ẢNH DỰ ÁN, chưa có giọng** (người dùng đưa mỗi thư mục ảnh): dựng mô hình trước, giọng đưa sau.
1. `quet --res "<thư mục ảnh>" --3d --vi-tri "lat,lon"` (hoặc `--dia-chi`) → work `<thư mục>_bds3d_work` (không lời, không cảnh).
2. Như bước 2–3 ở trên: mở ảnh, viết `mo_hinh_3d`, `xem-3d` tới khi giống.
   - **Dự án đang xây** (ảnh vệ tinh đã có tháp dở / bóng tháp): đo vị trí + hướng từng tháp trên ảnh z19 có lưới mét, đặt mô hình đúng chỗ tháp thật.
   - Phủ `san_vuon` (cỏ + cây) theo ranh đất OSM để che công trường.
3. `bay-thu --work <dir>` → `bay_thu.mp4` (12 s, câm): camera hạ từ cao rồi bay vòng — gửi người dùng xem mô hình trong video ngay.
4. Có giọng: `quet --audio "<giọng>" --res "<ảnh>" --3d --work <cùng work>` → giữ nguyên `mo_hinh_3d`, lập kế hoạch mới theo lời, đi tiếp bước 4–5.

## Chọn khối theo NGHĨA lời (khuôn 6 phần của mẫu)

| Phần | Lời thường gặp | Khối |
|---|---|---|
| 1 HOOK (0 → ~3 s) | câu mở / khẳng định mạnh | `the_noi` + chữ 2 tầng, khoá vàng = từ đắt nhất |
| 2 BÁC BỎ CÁCH CŨ | "không cần / không phải / không mất + X" | `vien_kinh` (icon app của X) + `gach` ngay sau khi đọc xong X; thẻ nổi giữ nguyên |
| 3 KHOE | "mà vẫn… / trực quan / thu hút / đẹp" | cùng shot → `tran_man` (phóng thẻ) + chữ trên đầu |
| 4 TÓM TẮT | "chỉ với N bước / có N thứ" | `nen_nhoe` + `o_kinh` N ô + chữ `giua` |
| 5 TỪNG BƯỚC | "Bước N / đầu tiên / tiếp theo" | chữ `buoc` + `tit`; `giao_dien` đúng thao tác trong lời (tìm vị trí → `ban_do`; dán / gửi / AI làm → `chat_ai`; app khác / màn hình thật → `anh`). 2 bước cùng app → 1 thẻ + `xoa` |
| 6a KẾT QUẢ | "đây chính là kết quả / thành phẩm" | `tran_man` shot mới (trồi từ thẻ), chừa khoảng lặng cho nhạc dâng |
| 6b CTA | "comment / nhắn / inbox + TỪ KHOÁ" | `dien_thoai`: khách gửi từ khoá → đang gõ → tài liệu → trả lời; chữ `trich` cho từ khoá |

Video không phải hướng dẫn (giới thiệu dự án thuần): bỏ phần 4–5 giao diện, dùng `the_noi` / `tran_man` / `nen_nhoe` + ô kính tiện ích
(icon nha, toa_nha, tien, vi_tri…) + viên kính cho điểm mạnh; vẫn giữ quy tắc mỗi cảnh 2,5–4 s và luôn có vật đang chuyển động.

## CỔNG DUYỆT — hỏi 1 lần, đủ các câu, rồi DỪNG chờ

Gửi `duyet.jpg` + tóm tắt `bang_duyet.txt`, rồi hỏi:
- **D1 Nhạc nền**: file nào? (mẫu có nhạc ~122 BPM nhưng không tách khỏi giọng được). Không đưa → dựng không nhạc.
- **D2 CTA**: từ khoá khách comment, tên tài liệu gửi lại, câu trả lời trên iPhone đúng chưa? (hoặc bỏ cảnh điện thoại)
- **D3 Mục ĐOÁN**: từng mục trong `doan` (tên dự án / địa chỉ trên Maps, nội dung prompt, tên tệp…).
- **D4 Footage**: đoạn chọn cho hook / khoe / kết quả ổn chưa; chữ của video có đè chữ sẵn trong footage chỗ nào không.
- **D5 Bản gửi khách**: có xuất thêm bản NNS mờ không?
- **D6 Cảnh 3D** (khi có), gửi kèm `mo_hinh_3d.jpg`:
  - vị trí lô đất đúng chưa (link Google Maps nếu ĐOÁN);
  - mô hình (số tháp / tầng / khối đế / vườn treo) giống ảnh chưa;
  - số liệu trên chú thích (diện tích, số căn, số tầng) có đúng không;
  - tên dự án / logo (file logo nếu có).

Không hỏi lại phông, màu chữ, kiểu khối (đã chốt).

## Bẫy đã gặp

- **Kính mất mờ**: Chrome coi phần tử có `filter` / `opacity < 1` là *backdrop root* → `backdrop-filter` của con không thấy nền. Đặt opacity/filter lên chính viên/ô kính, KHÔNG lên khung bọc; khi nét hẳn thì xoá filter (`''`).
- **Icon Google Maps thành ô vuông**: SVG dùng `clipPath id` trùng nhau, id đầu nằm trong thẻ đang ẩn → mọi icon mất clip. Mọi icon đi qua `uniq()` đổi id riêng.
- **Đỉnh âm vượt sau AAC**: wav −1,5 dBTP ra AAC thành +0,4 dBTP (tiếng click). `am_thanh.ghep` chặn trần −1,8 dBFS trước khi mã hoá rồi đo lại file cuối, vượt thì hạ trần ghép lại.
- **Chrome song song mở hụt** (DevTools không có trang) → đoạn đó ffmpeg báo "Output file does not contain any stream". `render.mjs` mở lệch 0,6 s mỗi luồng + tự thử lại 3 lần.
- `python -I` không tự thêm thư mục script vào `sys.path` → `run.py` tự chèn; luôn chạy kèm `-X utf8` (bỏ qua PYTHONUTF8).
- Whisper viết "Claude" thành "Cloud" → truyền `--tu-khoa`.
- **Footage có chữ sẵn ở vùng trên** (video kết quả của skill khác có tít to y < 420) → chữ 2 tầng đè lên. Chọn đoạn footage khác, dời chữ (`vi_tri: "giua"` hoặc số px), hoặc báo người dùng ở D4.
- Bản đồ trong `ban_do` là hình minh hoạ vẽ bằng code (giống giao diện Google Maps, không phải dữ liệu thật) — đừng ghi khoảng cách / vị trí như thật.
- **Cảnh 3D tối xám**: nắng đặt phía Bắc (`goc` 140 cũ) → mặt quay về camera (phía Nam) không được chiếu. Mặc định `nang.goc` 32 (từ Đông Nam), camera nên đứng phía Nam (`goc` −60…+40).
- **Địa danh lọt khung**: sông ở phía Đông mà camera đứng phía Đông → nhãn sau lưng. `kiem-kh` báo ⛔. Quay `goc` để camera nhìn về phía địa danh, hoặc dời `tu` tới lúc camera đã quay.
- **Nội suy camera vọt**: Catmull-Rom thường vọt quá khoá rồi quay lại → dùng Hermite đơn điệu. 2 khoá trùng nhau = camera đứng.
- **Mô hình trên toà có sẵn** trông rất giả. Chọn đúng lô trống (soi z19 trong `ve_tinh\nen_z19_*.jpg`), dời `x`/`z` hoặc `vi_tri`.
- Mặt phẳng nền nhiều lớp phải `depthWrite:false` + vẽ xa → gần (renderOrder), không thì nhấp nháy (z-fighting). Cây là sprite tán tròn + bóng mềm. Khối đa giác trông như hoạt hình, đã bỏ.
- **Đơn vị trong chữ hiện trễ**: "m²" không có trong lời nên khớp mờ nhầm sang chữ "mà" 1,5 s sau, làm "10.000 m²" hiện cụt. `_giai_chu` giờ chỉ nhận từ kế tiếp nếu nó nằm trong 1,2 s sau từ trước; quá 1,2 s thì từ đó hiện cùng lúc với từ trước.
- **Dự án đang xây có sẵn trên ảnh vệ tinh**: đặt mô hình lệch khỏi tháp thật thì thấy cả tháp dở + bóng thật cạnh mô hình. Đo từng tháp trên ảnh z19 lưới 10 m (mái sáng ở đầu Đông-Nam của vệt bóng), đặt `nang.goc` trùng hướng bóng thật (bóng chĩa Tây-Bắc → nắng Đông-Nam ≈ 45–50), phủ `san_vuon` che công trường.
- **Mô hình NHÁP lọt vào video**: `quet --3d` tạo sẵn 2 tháp mẫu. `kiem-kh` ⛔ khi `mo_hinh_3d` còn `_GHI_CHU` NHÁP, ⚠ khi chưa có `mo_hinh_3d.jpg` (chưa chạy `xem-3d` so với ảnh). Claude PHẢI mở ảnh dự án, dựng lại theo ảnh, xoá `_GHI_CHU`.
- **Sân / đường mặt đất bị cỏ che mất**: `san_vuon` là vật trong suốt nên luôn vẽ SAU mọi vật đục. Sân đục + `depthWrite:false` thì bị cỏ phủ kín. Mọi lớp phẳng của `mat_dat` phải `transparent: true` để xếp theo `renderOrder` (cỏ −28 < sân −27/−26).
- **Cửa sổ sáng đèn thành cột / chấm bi**: ô kính lặp 4 tầng làm ô đèn lặp thành cột dọc, `den_cua` 0,2–0,3 thì mặt đứng như chấm bi. Ô kính giờ lặp 12 tầng + lệch dọc ngẫu nhiên; ảnh phối cảnh thật chỉ cần `den_cua` 0,08–0,12.
- **Mặt đứng thành lưới gạch**: `san` (dải sàn) sáng màu ở mọi tầng (đồng `#a9694b`, trắng `#ecebe6`) → sọc ngang dày như tường gạch. Để `san` TỐI gần màu kính, màu khung dồn vào `luoi` + `tuong_hoi`.
- **`bay-thu` treo sau khi đủ khung** (máy đang chạy job khác, 1 luồng Chrome không thoát): `khung\3d__bay_thu_0.00\` đủ ~376 ảnh mà 10 phút không có mp4. Dừng cây tiến trình `render.mjs` (`taskkill /T /F /PID <node>`, KHÔNG giết chrome của người dùng) rồi ghép tay: `ffmpeg -framerate 30 -i khung\3d__bay_thu_0.00\%05d.jpg -ss 0.1 -t 12 -c:v libx264 -crf 17 -pix_fmt yuv420p -movflags +faststart bay_thu_banN.mp4`.
- **Mô hình "như đồ chơi", khách chê không giống ảnh**: đừng dừng ở số tháp / màu. Zoom ảnh phối cảnh (crop 2–3×) tìm CẤU TRÚC mặt đứng: khung viền đặc quanh module (`vien`), kích thước ô cửa (`buoc_cot`), tỉ lệ đèn sáng, dải sáng đỉnh, dải vườn treo mấy tầng. Rồi đặt `goc_anh` cho ảnh chính và so cặp ẢNH – MÔ HÌNH cùng góc trước khi gửi.
- **Tháp dính lưới trắng lạ**: `mo_hinh_3d.mau` chung có `luoi` → mọi tháp thừa hưởng. Tháp không lưới ghi `"luoi": null`.
- **Số tháp đo trên vệ tinh ≠ số chính thức** (Lumi: 10 phiến đo được, thông cáo 9 tòa): 2 phiến nối nhau là 1 tòa. Theo số chính thức, ghi cách gộp vào `doan`.
- **"Cứ nhấp nha nhấp nháy"**: không phải khung lỗi (đo chênh khung-khung không có đột biến) mà là chi tiết nhỏ của ảnh vệ tinh xa ở góc nghiêng (chân trời) + lưới cửa trượt qua điểm ảnh khi camera bay. MSAA không khử được răng cưa TRONG texture. Đã sửa ở engine: vẽ ×`ssaa` 2 + nhoè xa theo độ sâu (`hau_ky`). Đo: trung vị chỉ số nháy khung-khung Lumi 1,36 → 0,52. Khi khách vẫn thấy nháy: tăng `hau_ky.mo_xa`, đừng hạ `ssaa`.
- **Mờ gần mạnh = trông như đồ chơi**: nhoè cả tiền cảnh (tilt-shift) làm khu nhà giống sa bàn thu nhỏ. Giữ `mo_gan` ≤ 1,2, chỉ làm mờ xa.
- **Chạng vạng mà cỏ / cây xanh chói**: sprite cây + cỏ `san_vuon` không nhận đèn → phải nhân màu buổi (`BUOI.nen`). Buổi mới thêm vào `BUOI` nhớ khai `nen`, `dat`, `dat_pc`.
- **Ảnh khách trời xanh thẫm mà dựng `hoang_hon`** (trời cam) → lệch hẳn không khí ảnh, khách thấy "giả". Ảnh giờ xanh có viền đèn ⇒ `chang_vang`.
- **Ảnh tường hồi dán vào không thấy**: trụ góc của `vien` bọc kín đầu hồi, che mất mặt hồi của thân tháp. Engine giờ dán `anh_hoi` (hoặc texture `tuong_hoi`) lên MẶT NGOÀI trụ góc.
- **Mặt cắt quá hẹp (< 60 px trong ảnh gốc)**: tường hồi trắng Lumi chỉ 36 px → phóng ra 21 m thành vệt xám dọc như vết bẩn. Tường sáng màu thì bỏ `anh_hoi`, để texture tường hồi; tường đồng đậm vẫn dùng ảnh được.
- **Mặt đứng dán lên trông XIÊN / lệch** (Lumi bản 5): ảnh chụp trên cao có 3 điểm tụ — cạnh đứng chụm xuống dưới, vạch sàn dốc khác nhau ở đỉnh và chân. Chấm 4 góc lệch 10–20 px là texture xiên 3–5°, lên tháp thẳng đứng thấy lam / ban công chéo rõ. Đừng tắt tự nắn (`--giu-goc`) với mặt dài; soi `_xem.jpg` vạch cửa phải song song vạch đỏ.
- **Cắt lại ảnh mặt đứng mà video không đổi**: khung 3D cache theo HTML; trước đây đường dẫn ảnh không đổi nên dùng lại khung cũ. Nay URL ảnh kèm `?v=<md5>` — nếu sửa tay ảnh trong `mat_anh\` thì vẫn tự dựng lại.
- **Cắt mặt đứng lẹm nền / tường hồi**: góc lấy ở mép NGOÀI khung thì texture dính dải tường hồi trắng hoặc trời, dán lên thành sọc lạ. Lấy mép TRONG khung (khung viền đã có `vien` dựng), mở `<id>_xem.jpg` soi trước khi dùng.

## Nhật ký

- 12/11/2026 — tạo skill từ video mẫu Khánh Nguyễn. Dựng lại mẫu bằng giọng mẫu + video map làm footage: so 18 cặp khung cạnh mẫu, khớp bố cục / cỡ chữ / vị trí khối; tự kiểm 5/5 (1080×1920, 30 fps, 35,83 s, −14,2 LUFS, −1,7 dBTP).
- 12/11/2026 — thêm CẢNH 3D.
  - Thử: giọng mẫu + 3 khung mô hình của mẫu làm "ảnh phối cảnh", lô trống cạnh Q7 Saigon Riverside (10.72381, 106.74209).
  - 2 lượt bay (hook 0–13 s, kết quả 25,5–28,9 s); WebGL headless ~13 khung/s với 3 luồng; trọn video 36 s dựng ~2 phút.
  - Tự kiểm 5/5 (−14,4 LUFS, −2,1 dBTP).
  - So 8 cặp khung với mẫu: khớp bố cục thẻ, logo, vòng, chú thích, chữ trong cảnh, chân trời; mô hình gần giống, đơn giản hơn bản dựng tay của mẫu.
- 12/11/2026 — Lumi Hà Nội: 3 ảnh phối cảnh, chưa có giọng. Vị trí lấy ranh OSM "Lumi Hà Nội" (way 1503811634, Xuân Phương, cạnh Đại lộ Thăng Long).
  - Ảnh vệ tinh Esri đã có tháp đang xây: đo 10 phiến tháp trên ảnh z19 có lưới mét → 20 cánh tháp (5 phiến trắng/xám xen kẽ, 5 phiến đồng), `xoay` −35.
  - `bay_thu.mp4` 12 s; so với ảnh phối cảnh trên cao: khớp bố cục 2 cụm đồng / trắng, vườn treo vàng, Đại lộ Thăng Long phía trước. Số tầng là ĐOÁN.
- 12/11/2026 — người dùng chốt: cốt lõi skill là "đưa ảnh dự án vào → dựng được mô hình 3D trong video". Thêm chặn mô hình NHÁP + nhắc `xem-3d` ở `kiem-kh`, `quet --3d` in sẵn 4 bước dựng từ ảnh, sửa giờ chữ trong cảnh. Bản 3 (`giong_mau_3D_ban3.mp4`) tự kiểm 5/5, "10.000 m²" hiện đủ ở 4,7 s.
- 12/11/2026 — bộ dựng tổng quát + Lumi bản 2.
  - Mô hình thử mọi kiểu (`test_bds3d\thu_hinh_work`): tháp tròn vương miện sóng sáng vàng, tháp bo góc 2 bậc lùi + chân cột, tháp chữ L, cầu kính nối 2 tháp ở 75 m, 2 biệt thự mái ngói, đế + hồ bơi, hồ, sân tennis, sân bóng rổ, sân lát, đường dạo, cầu đi bộ cao 8 m; trời hoàng hôn. Lên hình đủ, không lỗi.
  - Lumi: 9 tòa (gộp 2 phiến SA + SB), cánh lệch 2 tầng trong 29–35, sảnh 4,5 m, hoàng hôn nắng Tây; mặt dài kính tối + lưới khung sáng trắng / đồng, đầu hồi đặc, đèn cửa 9–10 %, vương miện vàng; 3 hồ bơi, 8 sân, 3 đường dạo, cầu trên tán cây ~190 m dọc trục công viên giữa (vị trí tiện ích ĐOÁN).
- 12/11/2026 — Lumi bản 4 (`bay_thu_ban4.mp4`, 12 s, 1080×1920, 30 fps, dựng 73 s / 3 luồng): hậu kỳ (siêu mẫu ×2, nhoè xa, toả sáng), `duong_vien` line vàng chạy quanh ranh + vòng vàng, buổi `chang_vang`, kính phản chiếu, AO chân tường. Chỉ số nháy khung-khung trung vị 1,36 → 0,52, không khung nào nhảy đột ngột; dải chân trời mờ sương, hết lấp lánh.
- 12/11/2026 — Lumi bản 5 (`bay_thu_ban5.mp4`, 12 s, 1080×1920, 30 fps): mặt đứng dán từ ảnh phối cảnh hoàng hôn trên cao (`capitaland-khoi-cong…1177x800.jpg`) — 2 mặt đồng (`dong_a`, `dong_b`) xen kẽ, 2 mặt trắng, 1 mặt xám, hồi đồng `hoi_dong`; buổi `hoang_hon` + trời theo ảnh. Cặp ẢNH 1 – MÔ HÌNH cùng góc khớp màu / khung / đèn rõ hơn hẳn bản 4. Giới hạn: ảnh gốc mỗi mặt chỉ ~60–120 px nên lại gần vẫn hơi nhoè; mặt ảnh giống nhau lặp ở nhiều tháp.
- 12/11/2026 — Lumi bản 6 (`bay_thu_ban6.mp4`, 12 s, 1080×1920, 30 fps): tự nắn thẳng 5 mặt dài — dong_a −4,1° → 0°, dong_b −3,2° → 0°, trang_a +3,7° → −0,2°, trang_b +4,6° → −0,2°, xam_a +2,8° → −0,2° (mỗi mặt 2–6 s). So cùng khung 9 s với bản 5: lam trắng chân tháp + dải ban công thẳng đứng / ngang.
