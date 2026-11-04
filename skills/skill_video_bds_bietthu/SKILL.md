---
name: skill_video_bds_bietthu
description: "Dựng video sale bất động sản dọc 9:16 tiếng Việt (biệt thự / dự án) từ 1 video NGƯỜI NÓI quay thô + thư mục TƯ LIỆU dự án (ảnh phối cảnh, flycam, quay nhà mẫu), theo phong cách video mẫu BDS_1/MAU.mp4 'Biệt thự rừng tầng hầm' (đo từng khung 04/11/2026) — giọng sale làm xương sống, chỉ cắt quãng IM THẬT (giữ hơi thở; video đã dựng sẵn thì không cắt); HOOK người nói ~10 s có chữ câu hỏi to, chữ khoá nhấp nháy, loé sáng + rung, phóng-lùi mở đầu, từng chữ to thay nhau, nhân bản loé trước cú cắt; GIỮA phủ hình dự án ~70 % thời lượng, mỗi cụm ý ~2,5–3,5 s một cảnh cắt ĐÚNG đầu câu; địa danh không có tư liệu thì chiếu người nói (zoom mượt có whoosh); MỖI CẢNH 1 CỤM CHỮ (dẫn trắng nhỏ + KHOÁ to màu có quầng cùng màu: số vàng chanh / chữ hẹp đậm màu ăn theo cảnh + dòng viết tay trắng) gõ từng ký tự đúng lúc nói, xoá ngược khi hết cảnh; ảnh ngang thành THẺ BO GÓC trên nền nhoè của chính nó; liệt kê 3 sản phẩm = GHÉP 3 THẺ nền xanh ngọc + bướm bay; tấm kính 3D xoay cạnh người nói; loé ánh cam ở cú chuyển chương; CTA người nói + tên to; nhạc nền của user thấp hơn giọng ~16 dB, SFX thưa chỉ ở hiệu ứng (nghe rõ), −14 LUFS; tự kiểm 10 mục trên file cuối. Dừng 1 lần ở cổng duyệt NỘI DUNG (chữ, tư liệu, hiệu ứng, nhạc, tên CTA, cắt lặng). Trigger '/skill_video_bds_bietthu', 'edit video biệt thự này như video mẫu', 'dựng video sale BĐS có chữ bảng giá', 'phủ ảnh dự án lên video tôi nói', 'edit video bds biệt thự', 'làm video giống mẫu biệt thự rừng tầng hầm'."
---

# skill_video_bds_bietthu — video sale BĐS kiểu "Biệt thự rừng tầng hầm"

Số đo video mẫu + mọi chỗ cố ý khác mẫu: **`references/phan-tich-mau.md`** (đọc khi cần lý do của một con số).
Hằng số phong cách: `scripts/chung.py` (`VAI`, `CHONG`, `CHU`, `BANG_MAU`, `THE_MO`, `GHEP3`, `KEN_BURNS`, `HU`, `AM`, `SFX_MAP`).
**Script khác không tự đặt số.** Font / SFX / model dò mặt nằm trong `assets/` (skill tự đứng được).

> Quy ước với chủ dự án: trả lời tiếng Việt có dấu, báo tiến độ ngắn, có bản xem trước là gửi.
> "Giống mẫu" = giống CẢM GIÁC, KHÔNG chép tật mẫu (zoom-nhoè, −8,8 LUFS clip). Góp ý trên bản dựng:
> plan → ok → sửa skill → ok → dựng lại.

## LỖI USER ĐÃ BẮT — CẤM LẶP LẠI (đọc TRƯỚC khi lập plan; mỗi dòng có cơ chế chặn trong code)

| # | User nói (04/11, video Hạ Long) | Luật | Chặn ở đâu |
|---|---|---|---|
| L1 | "text đầu thô, đơn, trắng, xấu, chưa đủ wao" | Hook KHÔNG có chữ trắng/bạc trơn: câu hỏi = dòng dẫn 60 px + KHOÁ MÀU; từng chữ to thay nhau = `tu_lon` mỗi chữ 1 màu. Chữ khoá kiểu A (quầng cùng màu, viền tối, gradient + vân). Người nói đứng xa → `zoom` 1,55 + `tam` cho cận; cảnh người nói `toi_tren` | `C.KIEU_A`, `C.CHU_A`, `VAI['tu_lon']` màu; plan |
| L2 | "bỏ cái công trường đi" | KHÔNG dùng clip công trường (xe tải, san lấp, cần cẩu) dù có trong Resources, trừ khi user bảo | Claude khi gán tư liệu (D2 phải nói rõ clip nào bị loại) |
| L3 | "nói đến địa danh nào mà Resources không có thì cứ chiếu video thô" | Câu nhắc địa danh / tiện ích không có tư liệu ĐÚNG nghĩa → cảnh `noi`; không gán clip "gần gần" | Claude khi gán tư liệu; bảng duyệt ghi lý do từng cảnh |
| L4 | "chuyển cảnh dài, không khớp" | Cắt ĐÚNG đầu câu (`NHIP['cat_tre']` −0,05); loé cam 0,25 s; zoom-nhoè/phóng nhanh 3 khung; ghép 3 trượt 5 khung | `C.NHIP`, `C.HU`, `C.GHEP3` |
| L5 | "âm thanh nói bị lặp khi sang cảnh Resources" | Lời KHÔNG bị nhân đôi (đã đo); thủ phạm là SFX `glitch` + 1 swoosh lặp y hệt. Cấm glitch; ≤ 1 tiếng / 0,35 s; cùng file không lặp trong 4 s; chuyển chương xoay vòng tiếng | `C.SFX_MAP`, `SFX_CUA_SO`, `SFX_KHONG_LAP_S`, `SFX_XOAY` |
| L6 | "giây 24 đang nói tự nhiên hụt hơi … nhiều chỗ hụt hơi là không được" | Cắt lặng THEO NĂNG LƯỢNG: chỉ bỏ quãng im thật (< sàn ồn + 8 dB) dài ≥ 0,45 s, chừa 0,28 s cho hơi thở; KHÔNG dựa mốc chữ Whisper (đã cắt mất âm −7…−11 dB). Video ĐÃ DỰNG SẴN (CapCut) → KHÔNG cắt (D6) | `ke_hoach.doan_giu`, `C.CAT_LANG`; tự kiểm mục 9 |
| L7 | "zoom in zoom out không mượt, không có SFX, người di chuyển thì giật giật" | Neo zoom CỐ ĐỊNH cả cảnh (trung vị tâm mặt), không bám mặt từng 0,2 s; 2 cảnh người nói liền nhau khác zoom → ZOOM MƯỢT 10 khung ease + 1 whoosh; mọi cú phóng có tiếng | `Dung.neo`, `Dung.truoc`, `C.ZOOM_MUOT`; tự kiểm mục 10 |
| L8 | (lượt chạy thật 1) "cau_hoi" tràn ngang | Mọi vai có `rong_max`; `kiem-plan` soát cả chiều ngang | `C.VAI`, `run.kiem_plan` |

Khi user góp ý lần sau: thêm 1 dòng L vào bảng này + cơ chế chặn trong code + (nếu đo được) 1 mục tự kiểm.

## ⚠️ VIỆC ĐANG DỞ — làm tiếp ở công ty (user ghi 04/11/2026 tối, chưa sửa)

**T1. Chữ viết tay (chữ "uốn lượn") KHÔNG được để TRẮNG — phải là chữ có HIGHLIGHT.**
User: *"mấy cái chữ uốn lượn ý, không được để chữ trắng, chữ này phải là chữ có highlight nhé"*.
- Đang sai ở đâu: vai `viet_tay` (Great Vibes, trắng #FFFFFF, chỉ có quầng tối) — `chung.VAI['viet_tay']` +
  nhánh `else` trong `chu.Dong.__init__` (không đi qua kiểu A). Gặp ở mọi khối P1/P3/CTA ("không?", "Hạ Long",
  "bao điều đáng mong chờ", "phía dưới nhé!"…). Video đang có lỗi này: `OUT/bietthu_halong/HaLong_BIETTHU.mp4` (bản 3).
- Cách làm khi bắt tay (theo luật dựng ảnh tĩnh cho user chọn — đừng đoán):
  1. Dựng 3 ảnh tĩnh trên khung thật của video Hạ Long (dùng `run.py xem` sau khi thêm kiểu), ví dụ:
     (a) viết tay MÀU KHOÁ của chính cụm + quầng cùng màu (đồng bộ kiểu A);
     (b) viết tay vàng kim gradient + viền nâu + quầng sáng (kiểu chữ BĐS user đã duyệt ở nns-edit-bds / minh-tam-edit);
     (c) viết tay trắng trên VỆT HIGHLIGHT màu (nét bút dạ quang sau chữ, bo đầu).
  2. Cân nhắc đổi font: user từng chê Great Vibes "không rõ, chữ & thành jj" và chọn Pacifico (xem ghi nhớ
     `feedback_chu_ro_khong_uon_luon`, `feedback_chu_noi_khoi_3d`) — đưa 1 phương án Pacifico vào bộ ảnh.
  3. User chọn xong → thêm kiểu vào `chung.py` (vd `KIEU_VIET_TAY`), sửa `chu.Dong`, ghi dòng **L9** vào bảng lỗi
     ở trên, thêm mục tự kiểm "không có dòng viết tay màu trắng trơn", dựng lại Hạ Long, ghi Nhật ký.
- Xong T1 thì XOÁ mục này.

**T2. Trau chuốt để làm TEMPLATE cho tool NNS** (user 04/11: "sau này cho vào làm template của tool nns hết, nên
phải trau chuốt"): giữ code sạch, mọi số trong `chung.py`, SKILL.md đọc độc lập được, có ví dụ plan
(`examples/plan_mau_halong.json`), không đường dẫn tuyệt đối, không file model/video trong git.

## Cài đặt (máy mới)

- Python 3.11+ và ffmpeg/ffprobe trong PATH. `python -I -m pip install -r requirements.txt` (trong thư mục skill).
- Model dò mặt `det_10g.onnx` (InsightFace, giấy phép PHI THƯƠNG MẠI) **không đi kèm git**. Skill tự tìm ở
  `assets/models/`, `~/.insightface/models/buffalo_l/`, skill `nns-edit-bds` bên cạnh; không có thì tự dùng bộ dò
  mặt Haar của OpenCV (kém hơn chút, vẫn chạy). `rembg` tự tải `u2net_human_seg` lần đầu (hiệu ứng nhân bản loé).
- SFX trong `assets/sfx/` lấy từ thư viện sưu tầm KHÔNG rõ giấy phép (xem `assets/sfx/CREDITS.md`) — video
  thương mại thì thay bằng SFX có giấy phép, giữ nguyên tên file.

## CẤU HÌNH ĐÃ CHỐT (đo từ mẫu, xem phan-tich-mau.md)

| Lớp | Đã chốt |
|---|---|
| Khung ra | 1080×1920, 30 fps, x264 crf 17, bt709 (đọc `in_color_matrix=auto`, ghi `out_color_matrix=bt709`) |
| Nguồn người nói | phủ kín 1080×1920. **Cắt lặng theo năng lượng** (L6): bỏ quãng < sàn ồn + 8 dB dài ≥ 0,45 s, chừa 0,28 s (hơi thở), đầu/cuối chừa 0,10 s, nối có fade 15 ms; video đã dựng sẵn → `--khong-cat-lang` (hỏi D6) |
| Nhịp cảnh | mỗi CỤM Ý 1 cảnh (1,4–3,6 s, mẫu TB 3,16 s); cắt cứng **ĐÚNG đầu câu (−0,05 s trước chữ mở cụm)** — mẫu +0,25 s nhưng user 04/11 chê "không khớp"; hook người nói ≥ 8 s (mẫu 13 s); CTA người nói câu cuối |
| Tư liệu theo nghĩa (user 04/11) | CHỈ chiếu tư liệu khi lời nói đúng thứ có trong Resources; câu nhắc **địa danh / tiện ích KHÔNG có tư liệu** (sân golf, thuỷ cung, marina, sân khấu, ngôi nhà…) → chiếu **người nói** (cảnh `noi`, luân phiên `zoom` 1,0 / 1,3 cho đỡ đơn điệu). **KHÔNG dùng clip công trường** (xe tải, san lấp) trừ khi user yêu cầu |
| Hình dự án | ảnh: Ken Burns đẩy vào 2,5 %/s (+ lia 10 px/s nếu `day` trái/phải); video: dùng chuyển động thật, đẩy thêm 1 %/s; ảnh NGANG có số → `the_mo` (thẻ 1036 px bo 50, tâm y 1150, nền = chính ảnh nhoè σ28 tối ×0,82) |
| Ghép 3 | nền #2BA898 gradient + vân; 3 thẻ 1000×470 bo 40, khe 28, từ y 160 (đáy 1626 — nhãn thẻ 3 vẫn trên y 1600); trượt vào từ trái 7 khung, cách nhau 0,2 s (hoặc đúng mốc đọc tên); nhãn IN HOA Be Vietnam Pro Bold 40 góc dưới-trái; đổi ảnh trong thẻ = hoà tan 0,3 s; 14 con bướm xanh bay chéo lên |
| Kiểu chữ (user chọn A 04/11 trong A đúng mẫu / B khối 3D / C neon) | `khoa`, `tu_lon`, `so`, `nhan` = **quầng cùng màu** (σ 0,10·cỡ, 55 %) + bóng đen đậm + viền tối cùng màu (MaxFilter 7, ×0,25) + mặt gradient sáng 55 %→gốc→tối 38 % + vân; `C.KIEU_A`. Hook KHÔNG dùng chữ trắng/bạc: câu hỏi = `dan` 60 px + KHOÁ màu; từng chữ to thay nhau = `tu_lon` mỗi chữ 1 màu bảng |
| Zoom người nói | neo cố định theo cảnh (trung vị tâm mặt, hoặc `tam`); 2 cảnh `noi` liền nhau khác `zoom` → zoom mượt 10 khung ease in-out + whoosh (L7); luân phiên `zoom` 1,0 / 1,3; nguồn rung nhiều thì dùng 1,15 thay 1,3 (phóng to làm rung to theo) |
| Khung hook | người nói đứng xa (mặt nhỏ, nền sáng) → `zoom` 1,55 + `tam` [560, 1080] cho cận như mẫu; mọi cảnh `noi` `toi_tren` (tối dần nửa trên 0→32 %) để chữ màu nổi |
| Cụm chữ | vai `dan` BVPro Medium 46 trắng · `so` Montserrat SemiBold ≤340 (tự thu ≤860 px) **#FCE773** gradient · `khoa` Barlow Condensed Black ≤280 (≤900 px) gradient + vân + viền tối · `nhan` Montserrat Bold 110 · `viet_tay` Great Vibes 120 trắng (đè 30 % đáy dòng trên — CHỈ khi dòng trên là chữ TO; dưới dòng nhỏ thì xếp thường) · `chu_thich` BVPro SemiBold 50 canh phải · `cau_hoi` BVPro Bold 96 · `tu_lon` Montserrat Bold 230 bạc trong 88 % · `ten` Montserrat Bold 118 · `sub` BVPro SemiBold 40 |
| Chuyển động chữ | gõ 1,25 ký tự/khung; KHOÁ: `nhay` (bật/tắt 6 khung) · `roi` (rơi 140 px 5 khung, giãn dọc, KHÔNG nhoè) · `go`; ra = **xoá ngược 5 khung + trôi phải 14 px**, bắt đầu 0,20 s trước cú cắt (xoá xong ~0,03 s trước cắt); cả cụm trôi 6 px/s; bóng mềm; chữ nhỏ (dẫn/sub/chú thích/viết tay) thêm quầng tối σ18 để đọc được trên tường/trời sáng |
| Màu khoá | số tiền/%: vàng chanh; `"mau": "tu_dong"` = lấy màu nhấn của chính cảnh (k-means Lab, ép tương phản sáng ≥ 55); bảng có sẵn: `vang, vang_nhat, xanh_ngoc, xanh_ngoc_sang, tim_hong, hong_do, navy, bac_ha, cam_dao, xanh_rung, bac` |
| Vùng chữ | khối chữ trong x 40–1040, y 150–1600 (UI TikTok/FB che đáy); mặc định dải trên y≈300; KHÔNG đè mặt (tự kiểm mục 5) |
| Sub nhỏ | khi cảnh không có khối chữ: cụm 2–4 chữ đang nói, y 1240 (né mặt), gõ chữ |
| Hiệu ứng hook | `phong_lui` (1,35→1 trong 6 khung, neo mặt) · `loe` (sáng +55 %, 8 khung, rung chữ 10 px) · `phong_nhanh` (1→1,22 trong 3 khung + loé trắng — THAY zoom-nhoè của mẫu; zoom-nhoè khi bật `nhoe` = 3 khung) · `nhan_ban` (bóng người trắng ↔ âm bản 6 khung, rembg u2net_human_seg) |
| Chuyển chương | `loe_cam` qua cú cắt (−0,06/+0,19 s = 0,25 s, screen; mẫu 0,45 s bị chê dài) ở 2–3 chỗ: vào chương giá, vào CTA…; `loe_cam_troi` nhẹ suốt 1 cảnh |
| Tấm kính 3D | `the3d` trong cảnh người nói: tấm 400×720 viền xanh ngọc phát sáng, xoay −38°↔−18°, đổi ảnh 0,7 s, hiện 0,4 s; đặt PHÍA KHÔNG CÓ NGƯỜI: tâm mặt x < 540 → `x` 880, ngược lại `x` 220; `y` sao cho đỉnh tấm dưới đáy khối chữ |
| Nhạc nền | file của user (đề xuất mặc định: nhạc trong Resources); thấp hơn giọng 16 dB lúc nói, +4 dB ở khe, vào 80 / nhả 350 ms, fade 0,6/1,5 s. **KHÔNG tự tổng hợp nhạc** |
| SFX | chỉ ở hiệu ứng (mẫu: cắt thường KHÔNG có tiếng); **tối đa 1 tiếng / 0,35 s**, **cùng 1 file không lặp trong 4 s** (tự đổi trong họ swoosh), `loe_cam` xoay vòng swoosh → whoosh-short → quick-swoosh; **KHÔNG glitch** (22 cú giật/0,84 s, user nghe thành "tiếng nói bị lặp"): phong_lui quick-swoosh · loe camera-flash (cắt 0,35 s) · phong_nhanh whoosh (0,8 s) · nhan_ban im · loe_cam swoosh (đỉnh đúng cú cắt) · the3d fairy-dust · ghep3 quick-swoosh; gain tính để đỉnh 10 ms = giọng tại chỗ **+5 dB** |
| Master | loudnorm 2 lượt tuyến tính → −14 LUFS, TP −1,5 |

## Quy trình khi được gọi

0. Hỏi/nhận: video thô người nói (`--video`), thư mục tư liệu (`--resources`, mặc định `<thư mục video>/Resources`),
   nơi lưu. Chép nguồn vào thư mục dự án nếu nó nằm ở Downloads (16/10 cả thư mục BDS từng bị xoá ngoài ý muốn).
1. **Đo + nháp** (Whisper large-v3 CPU ~1–2 phút / 30 s):
   ```bash
   python .claude/skills/skill_video_bds_bietthu/scripts/run.py ke-hoach --video <thô.mp4> --resources <DIR> --out <WORK> [--ten "Nghĩa"] [--nhac <file>]
   ```
   Ra trong `<WORK>/`: `nguon.mp4` (đã cắt lặng, 1080×1920), `giong.wav`, `words.json`, `mat.json`, `tu_lieu.json`,
   **`tu_lieu_sheet.jpg`** (bảng hình có nhãn [i] tên file), **`plan.json` NHÁP**, `bang_duyet.md`. Thoát mã 2.
2. **Claude sửa plan.json THEO NGHĨA** (bắt buộc — bản nháp chỉ chia cụm máy móc):
   - ĐỌC lời (in cuối bước 1) + NHÌN `tu_lieu_sheet.jpg`. Gán tư liệu khớp nghĩa từng cụm (nói "phòng ngủ" → ảnh phòng ngủ;
     "flycam/quy mô/ha" → ảnh flycam ngang dạng `the_mo`; liệt kê 3 dòng sản phẩm → `ghep3`).
   - Viết lại cụm chữ: **sửa chính tả + tên riêng theo nghĩa** (mẫu: "xe rinh gia cư"→Shinrin-Yoku, "EcoBuck"→ECO PARK,
     "triết khấu"→chiết khấu); mỗi cụm 2–4 dòng theo khuôn P1–P4 (bên dưới); KHOÁ là CON SỐ / DANH TỪ ĐẮT; mốc `t` của
     từng dòng = mốc chữ đó trong `words.json` −0,1 s (dòng KHOÁ có thể hiện trước dòng dẫn nếu lời nói theo thứ tự đó).
   - Hook: dòng 1 `cau_hoi`; câu giữ chân → các khối `tu_lon` 1 chữ (`"ra": "tat"`, mỗi khối tắt khi chữ sau hiện);
     tiêu đề dự án dạng P1 (`khoa` + `viet_tay` + dẫn nhỏ).
   - Sửa lỗi nghe trong sub nhỏ bằng `"sua_loi": {"sai": "đúng"}`.
   - Xong đặt `"CAN_CLAUDE_SUA": false`.
3. **Cổng duyệt (AskUserQuestion — xem bảng DIALOG)**. Trong lúc chờ có thể chạy `xem` để có ảnh minh hoạ cho câu hỏi.
4. **Soát + xem trước**: `run.py kiem-plan --out <WORK>` (mã 0 mới được dựng) và
   `run.py xem --out <WORK> --moc 0.5,3.2,…` → PNG trong `<WORK>/xem/` — NHÌN ít nhất 1 khung mỗi kiểu cảnh.
5. **Dựng**: `run.py dung --out <WORK> --ra <final.mp4>` (hình ~2–4× thời lượng; tiếng vài giây; rồi tự kiểm).
   Chỉ sửa tiếng: thêm `--chi-tieng` (giữ `hinh.mp4`).
6. **Tự kiểm 10 mục** (in cuối bước 5; chạy riêng: `run.py kiem`): thời lượng · −14±1 LUFS & TP ≤ −1 · cú cắt đúng mốc ±2 khung ·
   chữ hiện + trong vùng an toàn · chữ không đè mặt · không tụt nét quanh cú cắt · SFX +2…+9 dB so giọng tại chỗ ·
   nhạc dưới giọng 12–20 dB · **không cắt mất âm thật (hụt hơi)** · **cú zoom nào cũng có SFX**. LỖI nào cũng phải sửa hoặc báo thẳng cho user.
7. Giao: "Video đây ạ" + thời lượng, số cảnh, tư liệu đã dùng, chỗ nào là phỏng đoán. Rồi **bồi bảng Nhật ký** cuối file này.

## CÁC DIALOG SKILL PHẢI HỎI (lần nào gọi cũng hỏi lại TẤT CẢ — lựa chọn cũ chỉ là ĐỀ XUẤT mặc định)

| # | Hỏi gì | Ai in | Đề xuất mặc định | Bắt buộc |
|---|---|---|---|---|
| D1 | Nội dung chữ từng cảnh (đã sửa chính tả/tên riêng) | `ke-hoach` in nhắc; Claude hỏi bằng AskUserQuestion kèm bảng | bản Claude viết | có |
| D2 | Tư liệu cho từng cảnh | như trên, kèm `tu_lieu_sheet.jpg` | Claude gán theo nghĩa | có |
| D3 | Hiệu ứng đặc biệt lần này: nhân bản loé · tấm kính 3D · ghép 3 + bướm · loé cam · zoom-nhoè đúng mẫu | Claude | tất cả TRỪ zoom-nhoè | có |
| D4 | Nhạc nền: file trong Resources / file khác / không nhạc | Claude | file nhạc tìm thấy | có |
| D5 | Tên người nói + câu CTA | Claude | tên nghe được + "Inbox ngay nhận layout chi tiết" | có |
| D6 | Cắt lặng: theo năng lượng (giữ hơi thở) / KHÔNG cắt | Claude (hỏi TRƯỚC khi chạy `ke-hoach`; khác lựa chọn thì chạy lại `ke-hoach`) | video đã dựng sẵn (CapCut, file `*final*`, ít khe > 0,5 s) → KHÔNG cắt; video quay thô → theo năng lượng | có |

Luôn báo đã chọn gì và dựa vào đâu. Nếu user giục "làm luôn": chọn đề xuất, NÓI RÕ đã chọn gì.

## plan.json — các khoá

```jsonc
{
 "dur": 33.1, "ten": "Nghĩa", "nhac": "D:/.../nhac.mp3", "nhac_ss": 0, "sub_nho": true, "sub_y": 1240, "nhoe": false,
 "sua_loi": {"triết": "chiết"},
 "canh": [
  {"id": 1, "loai": "noi", "t0": 0, "t1": 9.9, "zoom": 1.0,
   "hieu_ung": [{"kieu": "phong_lui", "t": 0}, {"kieu": "loe", "t": 1.87}, {"kieu": "phong_nhanh", "t": 4.3},
                {"kieu": "nhan_ban", "t": 9.67}],
   "the3d": null,                                   // hoặc {"nguon": ["a.jpg","b.jpg"], "t0": 16.6, "t1": 19, "x": 300, "y": 980}
   "chu": [
    {"y": 300, "t1": 1.0, "dong": [{"text": "Đã bao giờ ?", "vai": "cau_hoi", "t": 0.4}]},
    {"y": 280, "t1": 2.2, "dong": [{"text": "Bạn thấy", "vai": "dan", "t": 1.1},
                                   {"text": "CĂN BIỆT THỰ", "vai": "khoa", "t": 1.47, "vao": "nhay", "mau": "tim_hong"}]},
    {"y": 330, "t1": 4.7, "ra": "tat", "dong": [{"text": "Đừng", "vai": "tu_lon", "t": 4.45, "vao": "hien"}]}
   ]},
  {"id": 3, "loai": "the_mo", "nguon": "flycam.jpg", "t0": 13.2, "t1": 16.4,
   "chu": [{"y": 300, "t1": 16.34, "dong": [{"text": "Chỉ vỏn vẹn", "vai": "dan", "t": 13.3},
            {"text": "604", "vai": "so", "t": 14.25}, {"text": "căn biệt thự", "vai": "viet_tay", "t": 15.2}]}]},
  {"id": 5, "loai": "ghep3", "t0": 19.0, "t1": 22.7, "nen": "#2BA898", "buom": true,
   "the": [{"nguon": "a.jpg", "nhan": "VILLA ĐẠI LỘ", "t": 19.0, "doi": [{"nguon": "a2.jpg", "t": 21.9}]},
           {"nguon": "b.jpg", "nhan": "VILLA ĐƠN LẬP", "t": 19.2}, {"nguon": "c.mp4", "nhan": "VILLA SONG LẬP", "t": 19.4}]},
  {"id": 7, "loai": "video", "nguon": "phong_ngu.mp4", "ss": 2.0, "speed": 1.0, "t0": 27.9, "t1": 30.4, "chu": [...]},
  {"id": 8, "loai": "anh", "nguon": "ngoai_that.jpg", "day": "vao|ra|trai|phai|dung", "t0": 30.4, "t1": 32.6, "chu": [...]}
 ],
 "chuyen": [{"t": 51.93, "kieu": "loe_cam"}, {"t": 86.27, "kieu": "loe_cam"}],
 "sfx_them": [{"t": 54.0, "file": "pop.mp3"}],
 "CAN_CLAUDE_SUA": false
}
```
- Khối chữ: `y` (đỉnh), `x` (tâm ngang, mặc định 540), `t1` (bắt đầu xoá), `ra`: `xoa` | `tat` | `giu`, `gian` (px cộng giữa dòng),
  `troi` (hệ số trôi). Dòng: `text`, `vai`, `t`, `vao`: `go` | `nhay` | `roi` | `hien`, `mau` (hex / tên bảng / `tu_dong`),
  `le`: `trai` | `phai` | `giua`, `dx`, `dy`, `co` (cỡ), `rong_max`.
- Khối được VẮT QUA cú cắt (mẫu giữ "Khách hàng 10%" qua 75,1 s): đặt `t1` lớn hơn `t1` của cảnh.
- Hiệu ứng có `"sfx": false` để tắt tiếng; `loe_cam_troi`: `{"kieu": "loe_cam_troi", "t": 22.7, "dai": 2.9, "manh": 0.45}`.
- `sua_loi` khớp theo CỤM từ liền nhau (khoá nhiều chữ): `{"hòa hôn": "hoàng hôn", "đánh gốc": "đánh golf"}` — không đụng
  "hòa nhịp". Chỉ ảnh hưởng SUB NHỎ (khối chữ thì Claude tự viết đúng).
- Viết plan bằng 1 file `.py` trong thư mục làm việc (vd `viet_plan.py`) rồi chạy — heredoc Bash có tiếng Việt + ngoặc
  từng vỡ ("unexpected EOF", 04/11).

### Khuôn cụm chữ (mẫu)
- **P1** dẫn + KHOÁ + viết tay: `Chỉ vỏn vẹn / 604 / căn biệt thự` · `ECO RETREAT / BIỆT THỰ / Rừng` · `với Hệ sinh thái / 24 / túi rừng`.
- **P2** KHOÁ + chú thích canh phải: `12 ha / diện tích mặt nước` · `25% / vốn tự có ban đầu`.
- **P3** viết tay làm khoá: `Liệu pháp / tắm rừng` · `Khu làm việc / vô cực / giữa lòng thiên nhiên`.
- **P4** hook: câu hỏi `cau_hoi`; giữ chân = từng chữ `tu_lon` thay nhau.
- CTA: `dan` "Inbox ngay nhận layout chi tiết" / `ten` tên người nói (`vao: nhay`) / `viet_tay` / `dan` nhỏ; `ra: giu`.

## Bẫy đã biết

- Whisper nghe sai tên dự án/thuật ngữ — chữ trên màn hình phải theo NGHĨA, không chép Whisper; hỏi D1 khi không chắc.
  Khi lời nhiều tên riêng, NGHE LẠI 1 lượt Whisper với `initial_prompt` liệt kê tên/thuật ngữ đoán được để đối chiếu
  (04/11: lượt 2 xác nhận golf, hoàng hôn, swing, view biển; nhưng lượt có gợi ý BỎ SÓT 1,3 s lời ⇒ giữ mốc của lượt 1,
  chỉ dùng lượt 2 để sửa chữ). Chỗ cả 2 lượt vẫn mơ hồ ("Hà Nội mới", "lưng ni") → để ngoài chữ khoá + hỏi D1.
- Tư liệu thiếu cho một ý (golf, sân thể thao, sân khấu…) → dùng cảnh NGƯỜI NÓI (`zoom` 1,12) với khối số/chữ, đừng gán
  bừa clip lệch nghĩa; clip flycam công trường hợp với ý QUY MÔ (ha, sở hữu nhà).
- Video ghép sẵn từ CapCut (người nói đổi bối cảnh) vẫn chạy được: cắt lặng chỉ rút thêm ~4 %; kiểm nhạc sẵn có bằng
  sàn âm (p1 −56 dB = chỉ giọng) trước khi hỏi D4.
- Ảnh tư liệu thường có watermark/chữ chủ đầu tư ở đáy → ưu tiên `the_mo` hoặc `day` để đẩy vùng đó ra ngoài.
- `nhan_ban` cần `rembg` + model `~/.u2net/u2net_human_seg.onnx`; không có thì hiệu ứng tự bỏ (không lỗi).
- Cú cắt `noi`→`noi` cùng nguồn là liền mạch (không tính là cú cắt khi tự kiểm).
- Tự kiểm mục 3 cần cảnh trước/sau khác hình rõ; 2 ảnh rất giống nhau có thể báo lệch giả — nhìn khung trước khi sửa.
- Mục 6 (nhoè) BỎ QUA cú cắt có `loe_cam`: lớp loé screen nén tương phản nên Laplacian tụt 40–60 % dù khung vẫn nét
  (đã soi từng khung ở lượt thử 04/11). Độ nét đo chuẩn hoá theo phương sai độ sáng.
- `t1` của khối = mốc cắt − 0,20 s (xoá 5 khung xong trước cắt); `kiem-plan` cảnh báo khối xoá chưa xong lúc cắt
  — muốn giữ chữ qua cú cắt (như mẫu "10%") thì đặt `"vat_qua_cat": true`.
- Cùng 1 file video dùng cho 2 thẻ ghép 3: mỗi thẻ có bộ đọc riêng (đã sửa) — đừng tự gộp lại.
- Cảnh người nói đứng xa (mặt ở y > 900): khối chữ y 280–330 vẫn thoáng; sub nhỏ tự né xuống dưới cằm.

## Skill này được bồi thêm sau mỗi lần chạy thật

| Ngày | Video | Học được |
|---|---|---|
| 04/11/2026 | Đóng skill từ BDS_1/MAU.mp4 (91,7 s, 29 cảnh) | xem phan-tich-mau.md |
| 04/11/2026 | Chạy thử: `BDS/Tho.mp4` (cô sale phân khu Paris, 33,6 s → cắt lặng 33,5 s) + 5 ảnh Resources + `phong_khach.mp4` (Minh_Tâm, chỉ để thử đường video) + nhạc KB5 → `OUT/bietthu_test/Tho_BIETTHU.mp4`, 12 cảnh, 16 khối chữ, 9 SFX, −14,0 LUFS, **8/8 ĐẠT** | (1) cache ảnh bị VẼ ĐÈ vì `ken_burns` z=1 trả bộ đệm gốc → luôn `.copy()`; (2) ghép 3 ban đầu 540 px/thẻ tràn đáy 1938 → 470 px từ y 160; (3) viết tay đè 30 % chỉ khi dòng trên là chữ TO (đè lên dòng dẫn nhỏ thì che mất); (4) chữ nhỏ trắng trên trời/tường sáng không đọc được → quầng tối σ18; (5) `tu_dong` lấy màu k-means rồi ép sáng ra nâu đục → đổi sang chọn trong BẢNG MÀU mẫu theo sắc cảnh + tương phản ≥ 60; (6) xoá chữ phải bắt đầu 0,20 s trước cắt (0,06 s làm "62" sót sang cảnh sau); (7) sub nhỏ không hiện khi 0,5 s tới có khối chữ (tránh lặp "Em thực" → "Em thực sự"); (8) mô tả SKILL.md phải bọc ngoặc kép (có ": " trong mô tả làm YAML hỏng). Dựng hình 1005 khung ~75 s. Không có tên người nói trong lời → CTA dùng "TƯ VẤN NGAY" (D5 phải hỏi). |
| 04/11/2026 | **Lần chạy thật 1**: `BDS_1/video_final_capcut.mp4` (anh Sơn, Vinhomes Global Gate Hạ Long, "một ngày làm cư dân", 54,3 s → cắt lặng 52,0 s, 6 bối cảnh ghép sẵn) + 4 clip dọc Resources (toàn cảnh vịnh, đảo đá–bãi biển, du thuyền, flycam công trường) → `OUT/bietthu_halong/HaLong_BIETTHU.mp4`, 16 cảnh (4 người nói, 1 ghép 3, 1 thẻ nền nhoè, 10 video), 23 khối chữ, 9 SFX, không nhạc, **8/8 ĐẠT** (lần đầu 6/8). D1–D5: giữ chữ + tư liệu đề xuất; D3 user BẬT CẢ zoom-nhoè đúng mẫu (khác mặc định — vẫn phải hỏi mỗi lần); D4 không nhạc | (1) vai `cau_hoi` thiếu `rong_max` → "Nếu một ngày thức dậy" tràn x 1075: MỌI vai nay có `rong_max`, `kiem-plan` soát cả chiều ngang; (2) mục 3 báo lệch giả ở cú cắt flycam→thẻ cùng clip (nền xe tải chuyển động nhiều, tỉ lệ x1,9) → chấp nhận khi khung cắt ≥ 1,8× mọi khung kề ±3; (3) `sua_loi` theo cụm từ (từng chữ làm hỏng "hòa nhịp"); (4) Whisper lượt 2 có gợi ý tên riêng để đối chiếu; (5) mốc giờ trong ngày (6h30/8h/12h30/14h30/20h) dùng `so` + `roi` rất hợp kiểu mẫu; (6) dựng 1560 khung ~80 s. |
| 04/11/2026 | **Lần chạy thật 1 — bản 2** sau góp ý: *"text đầu thô, đơn, trắng, xấu, chưa đủ wao"* · *"bỏ công trường, địa danh không có trong Resources thì chiếu video thô"* · *"chuyển cảnh dài, không khớp; âm thanh nói bị lặp khi sang cảnh Resources"* → `OUT/bietthu_halong/HaLong_BIETTHU.mp4` (bản 1 giữ `HaLong_BIETTHU_ban1.mp4`), 17 cảnh (13 người nói, ghép 3, 3 video vịnh), 8 SFX, **8/8 ĐẠT** | (1) dựng 3 ảnh tĩnh trên khung thật (A đúng mẫu nâng cấp / B khối 3D vàng cam / C neon, `OUT/bietthu_halong/kieu_chu/`) → user chọn **A** ⇒ `KIEU_A` thành mặc định; (2) hook trắng/bạc + người đứng xa trên nền toà nhà sáng là gốc của "thô": phóng 1,55 + tối nửa trên; (3) **"tiếng lặp" KHÔNG phải lời bị nhân đôi** — đo tương quan dạng sóng: lời trong file cuối khớp 100 % giọng gốc, không đoạn nào phát 2 lần, lệch hình/tiếng ≤ 40 ms; thủ phạm là SFX `glitch.mp3` (giật lặp) ngay trước cảnh Resources đầu + cùng 1 swoosh lặp y hệt ở mọi cú chuyển ⇒ bỏ glitch, 1 tiếng/0,35 s, không lặp file trong 4 s; (4) cắt đúng đầu câu thay vì +0,25 s; loé cam 0,25 s; (5) Whisper đoạn ngắn (< 3 s) BỊA chữ ("subscribe kênh…") — đừng dùng để soát mối nối; (6) `--chi-tieng` nay tính lại SFX theo luật mới. |
| 04/11/2026 | **Lần chạy thật 1 — bản 3** sau góp ý: *"giây 24 hụt hơi… nhiều chỗ hụt hơi là không được"* · *"zoom in/out không mượt, không có SFX, người di chuyển thì giật giật"* · *"ghi toàn bộ vào skill để video khác không mắc"* → `OUT/bietthu_halong/HaLong_BIETTHU.mp4` 54,3 s (bản 2 giữ `_ban2.mp4`), KHÔNG cắt lặng, 17 cảnh, 11 cú zoom đều có whoosh, 16 SFX, **10/10 ĐẠT** | (1) đo khe bị cắt trên file thô: 4/7 khe có âm thật đỉnh −7…−11 dB (hơi thở + đuôi chữ) — mốc chữ Whisper sai ⇒ cắt lặng chuyển sang NĂNG LƯỢNG + mục tự kiểm 9; video CapCut đã dựng sẵn → không cắt (D6); (2) giật khi zoom = neo bám mặt từng 0,2 s ⇒ neo cố định theo cảnh (đo lại: dịch khung bản cuối 1,16× nguồn ở cảnh phóng 1,3 = không thêm rung); (3) đổi zoom giữa 2 cảnh người nói = zoom mượt 10 khung + whoosh, mục tự kiểm 10; (4) bảng "LỖI USER ĐÃ BẮT — CẤM LẶP LẠI" L1–L8 đầu file; (5) plan bản 2 đổi mốc sang timeline gốc bằng timemap (`OUT/bietthu_halong/doi_moc_plan.py`) — không cần viết lại plan. |
