---
name: video-oto-viral
description: Edit VIDEO Ô TÔ viral (giới thiệu / review xe) 16:9 hoặc 9:16 từ THƯ MỤC CLIP quay xe (iPhone 4K/60, HDR, xoay dọc đều được) + 1 FILE NHẠC, đúng phong cách video mẫu F:\VIDA_TEST\Oto\Video_mau.mp4 (VinFast đỏ, đo từng khung 10/11/2026) — nhạc là xương sống: tự tìm BPM / phách / DROP, khuôn 13 cảnh đặt trên lưới nhịp (drop đúng nhịp 6, cắt trễ 1 khung sau trống, đoạn dồn cắt mỗi nửa nhịp), mở bằng KHUNG ĐIỆN ẢNH dải ngang + người nổi ra ngoài dải + ĐẬP ZOOM ×1,2 đúng phách + NẢY, chuyển cảnh MẢNH VỠ 3D (mảnh cảnh mới bay vào, halftone, vệt đỏ, tấm kính, lóe cảnh cũ 1 khung, nhoè-loé), LƯỚT TRẮNG tăng tốc, GỢN SÓNG đúng drop, KHÓI, LIA NHOÈ + rung tắt dần, GLITCH kéo dọc; máy quay ảo đẩy/kéo chậm mỗi cảnh, HUD công nghệ (số 7 đoạn rỗng, chuỗi dữ liệu, mũi tên nhấp nháy theo móc đơn), TÊN HÃNG trắng giãn chữ gõ từng ký tự theo nhịp + DÒNG XE đỏ nghiêng hiện giữa glitch, màu nét-bão hoà, nhạc dừng cứng + giữ hình + đen, −14 LUFS, mã hoá 1 lần, tự kiểm. Script quét clip + phân tích nhạc + lập nháp → Claude chọn clip theo NGHĨA (soi tờ khung) → DỪNG 1 lần ở cổng duyệt → dựng → tự kiểm. Trigger '/video-oto-viral', 'edit video ô tô này như video mẫu', 'dựng video xe viral', 'edit video review xe kiểu VinFast', 'làm video ô tô từ resources này', 'edit video car viral'.
---

# video-oto-viral — edit video ô tô viral y như mẫu

Người dùng chỉ đưa **thư mục clip quay xe** (+ 1 file nhạc). Skill dựng ra video giống mẫu
`F:\VIDA_TEST\Oto\Video_mau.mp4` từ nhịp cắt, zoom, chuyển cảnh, HUD tới chữ — chỉ khác hình là xe của người dùng.

Phân tích đầy đủ từng khung của mẫu: **`references/phan-tich-mau.md`** (đọc trước khi sửa bất kỳ con số nào).
Mọi con số phong cách nằm ở **`scripts/chung.py`** — không đặt số trong script khác.

## Skill này được bồi thêm sau mỗi lần chạy thật

| Ngày | Góp ý của người dùng | Đã sửa ở đâu |
|---|---|---|
| 10/11/2026 | Tạo skill từ video mẫu VinFast đỏ, dựng thử với F:\VIDA_TEST\Oto\Resources | toàn bộ |
| 10/11/2026 | "dựng kích thước dọc chứ nhỉ" | khổ 9:16, `tam` từng cảnh vào chủ thể |
| 10/11/2026 | "đoạn đầu chưa hiển thị đúng tay người · cả video chưa đạt · muốn PHONG CÁCH như mẫu chứ không phải y hệt kích thước" | `tay.py` + hiệu ứng `manh_tay` (mảnh bám 2 bàn tay thật, ngón đè mép, mặt lộ, đẩy sát vào tay khi chuyển cảnh); `MangVo` viết lại theo mẫu (chấm bi cảnh cũ → kính bo góc → vệt đỏ→đen → ô chữ nhật bo góc ráp lại); làm chậm bằng nội suy chuyển động; HUD khổ dọc to + rõ; chọn cảnh đa dạng cho khổ dọc |
| 10/11/2026 | "fade đen trên dưới chưa hợp lý và khớp · mảnh chưa khớp bàn tay, xem kỹ bàn tay, làm chuẩn nhịp · chuyển cảnh mẫu oki mà bạn làm xấu, không khớp · làm lại" | dải đen 0,47 H mở đều 0,05→0,97 s (`KHUNG_MO`); `nhac.py` sửa lệch pha lưới 46 ms; `tay.py` dò ĐẦU NGÓN (mô hình màu da riêng, 1920 px) + CHỖ GẤP trỏ–cái, `the_tay` 4 góc = 2 đầu ngón trỏ + 2 chỗ gấp, chỉ bàn tay đè mảnh (`che_dau`), mặt nạ sắc không viền; `MangMo` mở đầu (lớp tay + mảnh lao về máy, 6 mảnh lớn bay vào, phủ kín u≈0,45, không loé người); `MangVo` chấm bi rõ ngay, loé 2 khung cảnh cũ đang vỡ quanh mốc cắt; mốc cắt `lech` theo từng kiểu; sóng tắt 8 khung; glitch bật mạnh ngay |
| 10/11/2026 | "đoạn kéo dây chưa kéo từ tay ra mà lại đưa từ dưới lên" (bản 3) | `tay.py`: hộp cổ chỉ bỏ da NỐI với mặt, cắt ở mũi chữ V (`co_no`); chỗ chụm Lc/Rc = điểm hướng vào trong + lên (`chum_goc`), 2 khối chạm sát (`cham`) hay dính 1 khối (chia ở cột mảnh nhất) → Lc = Rc = chỗ 2 đầu ngón chạm; `mau_dam` / `mau_xa` chặn lan sang áo ám hồng; `the_tay` sợi mảnh (`day`) giữa Lc–Rc dài theo khoảng tách, nở thành dải bản ở `ban_phach` |
| 10/11/2026 | "xịn rồi đó, update vào skill" — DUYỆT bản 4 (`Resources_OTO_ban4.mp4`) | ĐÃ CHỐT 14 (bản chuẩn + dải kéo từ đầu ngón); `examples/vi-du-vf7-doc.json` = kế hoạch bản 4 |

## ĐÃ CHỐT (không tự đổi trừ khi người dùng yêu cầu)

1. **Nhạc quyết định nhịp.** Cảnh đặt theo lưới nhịp của bài nhạc (khuôn 13 cảnh `KHUON`), drop rơi đúng **nhịp 6** tính từ phách mạnh đầu F. Mốc đổi hình = phách + **1 khung** + `lech` riêng từng kiểu chuyển cảnh (`CHUYEN` trong chung.py, đo khung đầu cảnh mới của mẫu — người dùng duyệt 10/11/2026: sóng drop sớm ~5 khung, glitch sớm ~2 khung). Không cắt theo giây cố định.
2. **Chỉ có nhạc** — không giọng, không sub. SFX **tắt** (mẫu không có); chỉ bật khi người dùng xin.
3. **Khuôn chuyển cảnh**: mảnh vỡ ×3 → lướt trắng → gợn sóng (drop) → khói → lia nhoè ×5 → glitch. Không thay bằng hoà tan / fade.
4. **Mở đầu**: khung điện ảnh dải 0,47 H (cả 16:9 lẫn 9:16), 2 thanh đen mở ĐỀU, đối xứng, gần tuyến tính từ 0,05 s tới ~0,97 s (người dùng chê bản 2 "dải 0,30 H giữ rồi bật" 10/11/2026); người nổi ra ngoài dải nếu cảnh mở có người; đập zoom ×1,20 kết thúc đúng phách nhịp 1; nảy 7 khung trước cú cắt sang cảnh 2.
5. **Mỗi cảnh luôn có chuyển động máy** (đẩy +3…+12 %/s hoặc kéo −9…−11 %/s). Không để cảnh đứng im (trừ hero/kết đã có chữ).
6. **HUD** từ cảnh `logo` tới hết, chỉ ở mép khung, né chữ.
7. **Chữ**: chỉ 2 dòng — TÊN HÃNG (trắng, giãn, gõ từng ký tự mỗi ½ phách từ hero + 0,4 phách) và DÒNG XE (đỏ nghiêng, hiện giữa glitch +0,13 s). **In hoa.** Không bịa tên dòng xe: lấy từ người dùng hoặc đọc được rõ trên thân xe trong clip.
8. **Kết**: nhạc dừng cứng sau 2,67 phách kể từ glitch (fade 25 ms) → giữ hình 0,33 s → đen 0,13 s.
9. **Âm**: −14 LUFS, TP −1,5, loudnorm 2 lượt. Nhạc vào giữa bài thì vào dần trong 0,9·F.
10. **Màu**: nét + rõ + tương phản 1,08 + bão hoà 1,18 + tối góc; HDR iPhone tonemap hable → BT.709.
11. **Khổ**: theo đa số clip (ngang → 1920×1080 như mẫu; dọc → 1080×1920). 30 fps, x264 crf 17, yuv420p BT.709.
12. Clip ≥ 50 fps mặc định **tốc 0,6** (slow-motion mượt, kéo dài nguồn).
13. Không ghi đè video cũ — tự đặt `_ban2`, `_ban3`…
14. **Video chuẩn đã duyệt** (10/11/2026, "xịn rồi đó"): `F:\VIDA_TEST\Oto\Resources_OTO_ban4.mp4` (9:16, 25,83 s, kế hoạch `examples/vi-du-vf7-doc.json`). Đoạn mở `manh_tay`: lúc 2 tay chụm KHÔNG có gì; 2 tay vừa tách là **sợi đỏ mảnh kéo ra từ đúng chỗ 2 đầu ngón chạm nhau**, 2 đầu sợi luôn dính đầu ngón, dài theo khoảng tách; tới `ban_phach` (3→3,5 phách sau t0) nở thành dải bản rồi mở khung chữ L (4 góc = 2 đầu ngón trỏ + 2 chỗ gấp). Không bao giờ để dải hiện sẵn dài / mọc từ dưới lên.

## Quy trình

Mọi lệnh: `python -I -X utf8 .claude\skills\video-oto-viral\scripts\run.py <lệnh> …` (chạy từ thư mục dự án).
Thư mục làm việc mặc định `<thư mục clip>_oto_work`, video ra `<thư mục cha>\<tên thư mục clip>_OTO.mp4`.

1. **Quét** — `run.py quet --res "<thư mục clip>" [--nhac "<file nhạc>"] [--hang VINFAST] [--dong "VF 3"]`
   - Đọc mọi clip (xoay, HDR, fps), chấm độ nét / độ lia mỗi 0,5 s, tìm người, ra `tai_nguyen.jpg` + `khung\clip_XX.jpg` (tờ khung có nhãn giây).
   - Phân tích nhạc → `nhac.json`, `nhac.png` (phổ + phách + drop + đoạn chọn).
   - Lập **nháp** `ke_hoach.json` (gợi ý clip theo TÊN FILE + độ nét — chỉ là nháp).
   - Thư mục không có nhạc / có ≥ 2 nhạc → lệnh dừng mã 2: **hỏi người dùng** file nhạc (gợi ý nhạc của video mẫu), rồi `run.py nhac --work <dir> --file <nhạc>`.
2. **Claude soát nghĩa** — mở `tai_nguyen.jpg`, **mở từng `khung\clip_XX.jpg`** (bắt buộc nhìn thật), mở `nhac.png`. Sửa `ke_hoach.json`:
   - mỗi cảnh: `nguon` đúng **vai** (bảng ở dưới), `tu_giay` ở đoạn nét / không lia gắt, `tam` [x, y] 0..1 đặt vào chủ thể (xe / logo / đèn), `zoom` 1..1,6 khi cần cận hơn, `toc`;
   - cảnh mở: clip có **người** giới thiệu nếu có (`khung_dien_anh.nguoi = true`), không có người thì xe toàn cảnh;
   - không dùng lại 1 đoạn nguồn 2 lần; **kết = nối tiếp đúng clip hero** (mẫu 22–25,7 s là 1 cảnh xuyên qua glitch: `tu_giay` kết = `tu_giay` hero + (t1−t0)·toc);
   - mỗi cảnh 1 CHỦ THỂ khác nhau (đèn, logo, bánh, vô lăng, đuôi, gương, màn hình, ghế, đèn hậu…) — đừng để logo + biển số lặp 3–4 lần;
   - cảnh mở có người làm cử chỉ tay (chụm ngón, kéo căng, khung tay chữ L) → thêm `manh_tay` (dưới), chạy **`run.py tay --work <dir>`** và **MỞ `tay_<id>.jpg`** soi: chấm xanh (tay trái) / đỏ (tay phải) phải nằm ĐÚNG ĐẦU NGÓN (trỏ + cái / chỗ chụm), chấm tím = chỗ gấp ngón trỏ–ngón cái, chấm vàng = chỗ chụm Lc/Rc (lúc chụm 2 chấm vàng phải TRÙNG nhau ở chỗ 2 đầu ngón chạm, tách ra thì nằm ở đầu ngón cái + trỏ đang kẹp), khung xanh lơ = mảnh sẽ vẽ (góc trên ở đầu ngón trỏ, góc dưới ở chỗ gấp khi làm khung chữ L);
   - `chu.tieu_de` = tên hãng, `chu.dong_xe` = dòng xe (không chắc ⇒ để trống "" và hỏi ở cổng duyệt);
   - xong đặt `CAN_CLAUDE_SUA: false`.
3. **`run.py kiem-kh --work <dir>`** — sửa hết ⛔ (cắt lệch phách, clip hết nguồn → đứng hình, chuyển cảnh lạ, chữ giữ chỗ…). ⚠ nên sửa.
4. **`run.py duyet --work <dir>`** → `duyet.jpg` (khung giữa mỗi cảnh + giữa mỗi chuyển cảnh, có nhãn). **Mở và soi**: đúng nghĩa, tâm đúng xe, không mép đen, chữ đúng.
5. **CỔNG DUYỆT** — DỪNG 1 lần, đưa người dùng bảng cảnh ↔ clip + đường dẫn `duyet.jpg` + hỏi D1–D6 (dưới). Chờ trả lời, sửa kế hoạch, chạy lại 3–4 nếu đổi.
6. **`run.py dung --work <dir>`** (tự chạy kiem-kh trước; `--nhap` = nửa độ phân giải để xem nhanh). 4K HEVC: ~1–3 phút cho 25 s.
7. **`run.py kiem --work <dir>`** — 7 mục: thời lượng, LUFS/TP, cắt đúng phách (±2 khung), không khung đen, không đứng hình, nét lại sau chuyển cảnh, có chữ ở thẻ kết. Mở **`soat.jpg`** soi lại. Lỗi → sửa → dựng bản mới.
8. Giao: đường dẫn, độ dài, khổ, bảng cảnh ↔ clip, mục còn đoán.

## Vai cảnh (Claude chọn clip theo nghĩa)

| Vai | Nhịp | Nên chọn |
|---|---|---|
| mo_dau | 0–2 | người giới thiệu cạnh xe / xe toàn cảnh đẹp (clip "đầu tiên", intro) |
| toan_canh | 2–3 | xe 3/4 trước toàn thân |
| chi_tiet | 3–4 | cận chi tiết đẹp: đèn pha, mâm, gương |
| logo | 4–5 | cận logo / chữ tên xe trên thân |
| goc_thap | 5–6 | đầu xe góc thấp / nắp capo (kéo ra) |
| noi_that | 6–7 (DROP) | nội thất "đắt" nhất: vô lăng, màn hình |
| chinh_dien | 7–8 | đầu xe chính diện |
| nhanh_1..4 | 8–10 (½ nhịp) | 4 chi tiết nhanh: xi nhan gương, cần số / nút, ghế, đuôi xe / đèn hậu |
| hero | 10–11 | góc 3/4 đẹp nhất (chữ tên hãng gõ ở đây — để trống phần trên khung) |
| ket | 11–hết | xe toàn cảnh / đuôi / xoay — thẻ kết có 2 dòng chữ |

## CỔNG DUYỆT — hỏi đủ, 1 lần

- **D1 Khổ**: 16:9 như mẫu hay 9:16 (đề xuất theo đa số clip)?
- **D2 Nhạc**: file nào, có cắt từ giây đề xuất (drop rơi đúng nhịp 6) không? Không có nhạc → gợi ý nhạc của video mẫu.
- **D3 Chữ**: tên hãng (VD `VINFAST`) + dòng xe (VD `VF 3`) — **không đoán dòng xe**.
- **D4 Cảnh**: bảng cảnh ↔ clip từ `duyet.jpg` có cần đổi cảnh nào?
- **D5 Mở đầu**: giữ khung điện ảnh + người nổi (nếu có người) như mẫu?
- **D6 SFX**: mẫu không có SFX — giữ tắt hay thêm whoosh nhẹ ở chuyển cảnh?

## ke_hoach.json

```json
{
  "CAN_CLAUDE_SUA": false,
  "res": "F:\\...\\Resources", "kho": "16:9",
  "nhac": {"file": "...m4a", "bat_dau": 0.0, "bpm": 117.06, "phach_s": 0.5125, "nhip_s": 2.05, "F": 1.4856,
           "drop_video": 13.74, "ket_nhac": 25.37},
  "chu": {"tieu_de": "VINFAST", "dong_xe": "VF 3", "go_tu": 22.17, "dong_xe_tu": 24.17},
  "hud": {"bat": true, "tu": 9.66, "seed": 7}, "mau": {"bat": true}, "sfx": false,
  "canh": [
    {"id": 1, "vai": "mo_dau", "t0": 0.0, "t1": 5.54, "nguon": "đầu tiên.mp4", "tu_giay": 0.0, "toc": 1.0,
     "tam": [0.5, 0.5], "zoom": 1.0, "dong": 0.0,
     "hieu_ung": [{"kieu": "khung_dien_anh", "nguoi": true}, {"kieu": "dap_zoom", "t": 3.49}]},
    {"id": 2, "vai": "toan_canh", "t0": 5.54, "t1": 7.59, "nguon": "...MOV", "tu_giay": 1.2, "toc": 0.6,
     "tam": [0.55, 0.5], "zoom": 1.0, "dong": 0.06, "hieu_ung": [],
     "chuyen": {"kieu": "manh_vo", "ket": "nay", "zoom_cu": 1.10}}
  ]
}
```

- `t0/t1` giây video (cảnh liền nhau; t0 đã nằm trên lưới — đừng sửa tay trừ khi biết rõ).
- `tu_giay` = giây trong clip ứng với **cú cắt** (đoạn trước cú cắt cho chuyển cảnh được lấy lùi lại tự động).
- `toc` 0,6 = chậm (clip 60 fps); 1 = thường. Nguồn cần ≈ (t1 − t0 + 0,6) × toc giây sau `tu_giay`.
- `dong` %/giây (+ đẩy vào, − kéo ra). `zoom` nền 1..1,6. `tam` điểm nhìn.
- `chuyen.kieu`: `cat · nhoe_loe · manh_vo · luot_trang · gon_song · khoi · lia_nhoe · glitch`; `huong` (độ) cho lia_nhoe; `seed` cho mảnh vỡ.
- `xoay`: `-90` = xoay trái (ngược kim đồng hồ), `90` = xoay phải, `180` — cho clip quay nghiêng điện thoại (chữ / biển số nằm dọc trên tờ khung).
- `hieu_ung`: `khung_dien_anh {nguoi, ty_le, mo, dai}`, `dap_zoom {t, dai, len}`, `nay {t}`, `manh_tay {t0}`, (`manh_cho` cũ).
  `manh_tay` = mảnh cảnh sau **GHIM VÀO ĐẦU NGÓN THẬT** (mẫu 2,9–4,4 s): dò tay tự động (`tay.py`: tách người ∧ màu da − mặt → mở rộng theo màu riêng của bàn tay để bắt trọn ngón). Tay chụm → chưa hiện gì; 2 tay tách → SỢI mảnh (`day`) kéo ra từ đúng chỗ 2 đầu ngón chạm (Lc = Rc lúc chụm), hiện dần theo khoảng tách (`hien_keo`), dài đúng bằng khoảng cách 2 chỗ chụm, nở thành dải bản ở `ban_phach`; tay làm KHUNG CHỮ L → mảnh 4 góc = 2 đầu ngón trỏ (trên) + 2 chỗ gấp trỏ–cái (dưới), mép luồn dưới ngón (`lan…`). Chỉ BÀN TAY nằm trước mảnh (`MANH_TAY.che_dau=false`); áo, mặt nằm sau — người khung chữ L ngang mặt thì mảnh che miệng/mũi như vật cầm trước mặt. Chuyển `manh_vo` sang cảnh 2 dùng `MangMo`: lớp "tay + mảnh" lao về máy, cảnh cũ đẩy nhẹ `chuyen.zoom_cu` (1,10), 6 mảnh lớn cảnh mới bay vào xoay 3D phủ kín u≈0,45, không loé lại cảnh người. `t0` = giây video mảnh hiện (đặt đúng phách mạnh lúc tay đang chụm).
  `manh_cho {t0, t1, x, y, rong}` = mảnh cố định (chỉ dùng khi dò tay hỏng): `x, y` toạ độ khung RA.

## Bẫy đã gặp

- `python -I` bỏ qua biến môi trường → phải có `-X utf8` (không thì lỗi cp1252 khi in tiếng Việt). `-I` cũng không thêm thư mục script vào sys.path — run.py tự thêm.
- Clip iPhone xoay (`rotation −90`): ffmpeg tự xoay khi giải mã; probe đã đảo w/h — đừng xoay lần nữa.
  NHƯNG clip quay khi cầm điện thoại nghiêng (tên file kiểu "xoay 90 độ về bên trái", trên tờ khung chữ "VF7" nằm dọc) → đặt `xoay: -90` (trái) / `90` (phải) trong cảnh; Nguon xoay thêm bằng `transpose` rồi tính lại khung phủ.
- Clip 24/30 fps mà đặt `toc` < 1 (cảnh mở dài 5,5 s mà clip chỉ 4 s): trộn khung (`framerate`) để lại BÓNG MA ở tay → nay tự nội suy chuyển động `minterpolate mci` lên 60 fps 1 lần, lưu `work\cham\` (~1–2 phút cho 4 s 1080p). Chọn `toc` vừa đủ phủ cảnh (vd 4,1 s clip / 5,54 s cảnh → 0,72), đừng chậm hơn cần thiết. Clip 60 fps thì chậm 0,6 vẫn mượt.
- Mảnh giữa 2 tay đặt TAY ở toạ độ cố định → lệch tay ngay khi người cử động (người dùng chê "chưa hiển thị đúng tay"). Luôn dùng `manh_tay` (bám tay) và soi `tay_<id>.jpg`.
- Bản 2 neo mảnh vào TÂM LÒNG BÀN TAY + nở mặt nạ che (dilate + nhoè) → mảnh lố ra ngoài ngón + viền trắng áo quanh ngón; người dùng chê "chưa khớp bàn tay". Neo vào ĐẦU NGÓN + CHỖ GẤP, mặt nạ sắc (chỉ close/open, nhoè 0,7 px).
- u2net cụt đầu ngón mảnh giơ ra ngoài người (ngón trỏ dựng lên nền xe) → đầu ngón trỏ dò thấp hơn thật ~0,4 cỡ tay (bản 3a). Không nới mặt nạ người (nền xe ĐỎ lọt ngưỡng da YCrCb) — dùng `mo_rong_mau`: mô hình (a,b) Lab của chính bàn tay, lan tới điểm gần màu nối với khối tay. Khung phân tích phải 1920 px (`DAI_NHAT`; 960 px ngón chỉ ~6 px).
- Dải mở đầu "đưa từ dưới lên, không kéo từ tay ra" (bản 3): (1) hộp CỔ 0,75 cao mặt bỏ trắng cả hộp → 2 đầu ngón chụm trước ngực (nằm trong hộp) bị xoá, chỗ chụm dò ra = mép hộp cách nhau ~1,1 cỡ tay; (2) lấy điểm 'trong cùng' của mỗi tay → lúc chụm đó là ngón cong phía dưới; (3) mô hình màu lan sang áo trắng ám hồng (phản chiếu xe đỏ). Sửa: hộp cổ chỉ bỏ da nối với mặt, cắt ở hàng hẹp nhất (mũi chữ V — ngón chụm hay chạm đúng mũi V); chỗ chụm = điểm xa nhất hướng vào trong + lên 20°; 2 khối chạm sát / dính 1 khối → Lc = Rc (chia khối ở cột MẢNH NHẤT, không phải trung vị); ngưỡng độ đậm màu + bán kính lan. Kiểm: `d/s` Lc–Rc phải ≈ 0 suốt lúc chụm và chỉ tăng khi 2 tay tách (clip mở: 0 tới 1,47 s, tách 1,53 → 2,0 s).
- Góc dưới khung chữ L lấy ĐẦU NGÓN CÁI → hình thang hụt vào trong, mép không chạy dọc ngón. Lấy CHỖ GẤP = khuyết lồi sâu nhất (`convexityDefects`) dưới đầu ngón trỏ.
- Người làm khung L ngang MẶT mà để đầu nằm trước mảnh (bản 3a) → mảnh vỡ vụn quanh mặt, lúc chuyển cảnh mặt người phóng to theo lớp lao về máy (rất xấu). Để chỉ bàn tay trước mảnh; lớp lao về máy = mảnh ∪ bàn tay, không gồm đầu/áo.
- Chuyển cảnh mảnh vỡ: mẫu KHÔNG phải nhiều mảnh tam giác bay loạn — là chấm bi phủ cảnh cũ, 3 tấm kính bo góc nhỏ, vệt đỏ nhọn đỏ→đen, rồi cảnh mới về thành Ô CHỮ NHẬT bo góc trượt vào lưới (khe hở còn thấy cảnh cũ tới u ~0,95).
  Chấm bi phải rõ NGAY từ đầu cửa sổ và bước chấm tính theo CẠNH DÀI (khổ dọc tính theo bề ngang → chấm 9 px, không thấy). Khung loé = cảnh cũ ĐANG VỠ (chấm bi + tấm chéo), 2 khung quanh mốc cắt (1 trước + 1 sau), rồi nhoè mạnh cảnh mới — không phải cảnh cũ trơn.
- Mở đầu (`MangMo`) mà nền đổi muộn (u 0,40–0,52) → áo trắng người dẫn trơ giữa khung khi mảnh đã bay vào. Mảnh đáp u 0,12–0,36, nền đổi 0,28–0,38, lớp tay tắt 0,30–0,44. Không loé lại cảnh người ở mốc cắt (mẫu 5,6–5,7 s chỉ nhoè).
- Mốc đổi hình = phách + 1 khung rơi lố khung đích vài ms (11,7703 > 11,7667) → cảnh mới hiện trễ 1 khung. `lech` trong `CHUYEN` đặt mốc vào GIỮA 2 khung mong muốn; soi khung đầu cảnh mới của mẫu từng kiểu trước khi chỉnh.
- `nhac.py` lấy giây khung STFT = ĐẦU cửa sổ → lưới phách sớm 46 ms (≈ 1,4 khung) so với tiếng trống: cộng nửa cửa sổ (2048/2/sr).
- `xem` / `duyet` nhiều mốc trải khắp video từng tràn RAM (mỗi cảnh 1 ffmpeg giải mã 4K + đệm 100 MB) → Dung tự đóng bộ đọc của cảnh xa mốc đang vẽ.
- HUD khổ dọc: số rỗng 0,56·H của mẫu 16:9 thành gần hết bề ngang khổ dọc và alpha 0,2 trên nền sáng gần như không thấy → khổ dọc dùng 0,30·H ở 2 mép, viền dày hơn, alpha 0,34, chữ dữ liệu có bóng tối.
- Ra 9:16 không bao giờ thấy được cả xe từ clip ngang (xe chiếm > 32 % bề ngang): "toàn cảnh" = góc 3/4 cắt góc đầu xe (đèn + bánh + capo), clip đuôi xe quay xa (xe nhỏ trong khung) dùng cho cảnh `chinh_dien`; hero đặt logo V + biển giữa khung, chữ hãng trên capo, dòng xe đỏ dưới biển (y 0,76) — không đè biển số.
- Ra 9:16 từ clip quay NGANG: khung dọc chỉ thấy ~32 % bề ngang clip (đã là mức rộng nhất) → `tam` x của TỪNG cảnh phải đặt vào chủ thể (logo / biển VF / đèn / vô lăng), soi `duyet.jpg` rồi chỉnh — để 0,5 hay bị lệch nửa logo. Cảnh mở có người (người thường chỉ ở 40 % dưới khung ngang): `zoom` ~1,15 + `tam` y ~0,8 cho người to, 2 tay vẫn lọt khung sau đập zoom ×1,2.
- Cảnh mở dài ~5,5 s (2 nhịp + nhạc dạo): clip mở ngắn hơn thì giảm `toc` (0,6–0,7) thay vì để đứng hình; kiem-kh báo ⚠ "clip hết trước khi cảnh hết".
- iPhone HDR (HLG / PQ, bt2020): phải tonemap (zscale + hable) không thì màu xám bạc. `probe` gắn cờ `hdr`.
- 4K HEVC giải mã chậm: Nguon thu nhỏ ngay trong ffmpeg về cỡ "phủ kín × q" (q ≤ 1,25) để còn chỗ zoom.
- Nhạc vào drop sớm (< 6 nhịp trước drop): ke_hoach tự bỏ bớt `chi_tiet` → `logo` → `toan_canh`.
- Sau drop cần ≥ 5,67 nhịp nhạc; thiếu thì `nhac` báo ⛔ — chọn bài / đoạn khác hoặc `--drop` tay.
- Model tách người `u2net_human_seg.onnx` ở `~/.u2net/`; không có thì bỏ hiệu ứng người nổi (vẫn dựng được).

## Nhật ký

- 10/11/2026 — tạo skill: đo mẫu từng khung (zoom bằng ORB, phổ nhạc, chữ gõ), viết 9 script, dựng thử với 17 clip VinFast VF7 đỏ (16 iPhone 4K/60 + 1 clip mở 1080p/30 có người) ở F:\VIDA_TEST\Oto\Resources, nhạc của video mẫu (thư mục không có nhạc).
  So khung với mẫu rồi chỉnh: mảnh vỡ phủ ~50 % ở u 0,4, kín ở 0,9 (trước đó phủ quá sớm); gợn sóng drop = uốn lỏng bước dài + nhoè mạnh (trước đó sin dày quá); khói = gợn dọc + bóng mờ 2 lớp; mảnh vỡ tăng tốc 7× (chỉ tính trong hộp bao mảnh). Kế hoạch mẫu: `examples/vi-du-vf7.json`.
- 10/11/2026 (lần 2, khổ dọc) — người dùng chê đoạn mở sai tay + cả video chưa tới. Soi lại mẫu từng 0,1 s (đoạn mở, 3 chuyển mảnh vỡ, HUD, thẻ kết) và tờ khung bản mình: mảnh ở tay cố định + nhỏ, bóng ma tay do trộn khung, 5 cảnh lặp logo + biển VF7, HUD không thấy, mảnh vỡ loạn tam giác, kết khác clip hero. Sửa: `tay.py` dò tay (117/123 khung thấy 2 tay ở clip mở), `manh_tay`, `MangVo` mới, `cham_muot` (mci), HUD dọc, chọn lại 12 cảnh khác chủ thể, kết nối tiếp hero. Kế hoạch: `examples/vi-du-vf7-doc.json`.
- 10/11/2026 (lần 3, "làm lại") — người dùng chê dải đen mở đầu, mảnh không khớp tay, chuyển cảnh xấu + lệch nhịp. Đo lại: dải đen mẫu mở đều 0,05→0,97 s; lưới phách lệch 46 ms (lỗi STFT); khung đầu cảnh mới của từng kiểu chuyển (lướt 11,767 · sóng 13,667 · khói 15,833 · glitch 23,967); 3 chuyển mảnh vỡ soi từng khung (loé 2 khung cảnh cũ đang vỡ ở 7,667–7,70). Dựng thử từng đoạn bằng khung lẻ, soi cạnh mẫu, sửa tới khi khớp rồi dựng `Resources_OTO_ban3.mp4`.
- 10/11/2026 (lần 4) — người dùng duyệt hết trừ dải kéo mở đầu ("đưa từ dưới lên"). Soi mặt nạ da từng khung lúc chụm: hộp cổ xoá đầu ngón, điểm 'trong cùng' rơi vào ngón cong. Sửa dò chỗ chụm (cổ nối mặt + cắt mũi V, Lc/Rc, chạm sát, cột mảnh nhất), sợi kéo ra từ đúng chỗ 2 đầu ngón chạm. Dựng `Resources_OTO_ban4.mp4` (kiem 7/7) — người dùng DUYỆT ("xịn rồi đó"), chốt làm bản chuẩn.
