# Phân tích video mẫu `F:\VIDA_TEST\Oto\Video_mau.mp4` (đo từng khung 10/11/2026)

1920×1080 · 30 fps · 25,83 s · H.264 · AAC 32 kb/s · chỉ có NHẠC (không giọng, không SFX riêng) · xe VinFast đỏ.
Mọi con số bên dưới đã đưa vào `scripts/chung.py` — **đổi số thì đổi ở chung.py**, file này là bản giải thích.

## 1. Nhạc là xương sống

| Mục | Giá trị đo |
|---|---|
| Tempo | **117,06 BPM** → phách P = 0,5125 s, nhịp (4 phách) B = 2,050 s |
| Phách mạnh đầu F | 1,44–1,46 s (trước đó: nhạc dạo nhỏ + khung điện ảnh) |
| DROP | 13,74 s = F + **6 nhịp** (bass + trống vào đầy) |
| Cú cắt | trễ **1 khung** sau tiếng trống đầu nhịp (`TRE_CAT = 1/30`) |
| Đoạn dồn | 17,9–22 s cắt mỗi **nửa nhịp** (2 phách) |
| Kết | glitch 24,0 s = F + 11 nhịp; nhạc **dừng cứng** sau 2,67 phách (25,37 s, fade 25 ms) → giữ hình 0,33 s → đen 0,13 s |
| Âm lượng | −14 LUFS, TP ≤ −1,5 dBFS |

→ Skill không đặt cảnh theo giây cố định mà theo **lưới nhịp của bài nhạc người dùng đưa**: `nhac.py` tìm BPM, pha phách, drop rồi chọn giây bắt đầu cắt nhạc sao cho drop rơi đúng nhịp 6 của video.

## 2. Khuôn 13 cảnh (đơn vị nhịp tính từ F)

| # | Vai | Nhịp | Giây mẫu | Chuyển VÀO | Máy trong cảnh | Nội dung mẫu |
|---|---|---|---|---|---|---|
| 1 | mo_dau | 0 → 2 | 0 – 5,56 | — | khung điện ảnh mở, đập zoom ×1,20, nảy | người giới thiệu cạnh xe |
| 2 | toan_canh | 2 → 3 | 5,56 – 7,61 | **mảnh vỡ 3D** (kết bằng nảy) | đẩy vào +6 %/s | xe 3/4 trước |
| 3 | chi_tiet | 3 → 4 | 7,61 – 9,66 | mảnh vỡ 3D | +6 %/s | cận đèn |
| 4 | logo | 4 → 5 | 9,66 – 11,71 | mảnh vỡ 3D | +3 %/s, **HUD bắt đầu 9,8 s** | logo V |
| 5 | goc_thap | 5 → 6 | 11,71 – 13,76 | **lướt trắng** | **kéo ra −11 %/s** | đầu xe góc thấp |
| 6 | noi_that | 6 → 7 | 13,76 – 15,81 | **gợn sóng (DROP)** | +6 %/s | vô lăng / màn hình |
| 7 | chinh_dien | 7 → 8 | 15,81 – 17,86 | **khói** | +9 %/s | đầu xe thẳng |
| 8–11 | nhanh_1..4 | 8 → 10 mỗi ½ nhịp | 17,86 / 18,89 / 19,91 / 20,94 | **lia nhoè + rung** | 0 / +12 / +9 / −9 %/s | gương, cần số, ghế, đuôi |
| 12 | hero | 10 → 11 | 21,96 – 24,01 | lia nhoè | giữ | xe 3/4 + **chữ VINFAST gõ** |
| 13 | ket | 11 → hết | 24,01 – 25,37 | **glitch** | giữ | xe + VINFAST trắng + dòng xe đỏ |

Ít hơn 6 nhịp trước drop (nhạc vào drop sớm) → bỏ lần lượt `chi_tiet`, `logo`, `toan_canh` (ke_hoach.py tự làm).

## 3. Máy quay ảo (đo bằng ghép đặc trưng ORB khung-khung, `khung.json`)

- **Đẩy chậm / kéo chậm** liên tục trong mọi cảnh: +3…+12 %/s, kéo ra −9…−11 %/s (mũ: `z = e^{ln(1+d)·t}`).
- **Đập zoom** cảnh mở: 3,17 → 3,57 s phóng ×1,20, ease-in-out, **kết thúc đúng phách**.
- **Nảy** trước cú cắt cảnh 1→2 (5,40–5,60 s, 7 khung): ×1,033 1,072 1,103 1,120 1,114 1,070 1,015 — phồng vào rồi bật ra ngay trước khi mảnh vỡ lấp đầy.
- **Tăng tốc zoom** ở 20 % cuối mỗi cú mảnh vỡ: ×1,045 mỗi khung (hút vào tâm).
- **Rung tắt dần** sau lia nhoè: biên 1,6 % W, τ = 5 khung, 15 khung.
- Zoom tối đa trong kế hoạch 1,6 (nguồn 4K cho phép phóng tới ~2× mà vẫn nét ở 1080p).

## 4. Từng kiểu chuyển cảnh (số khung @30 fps)

| Kiểu | Trước cắt | Sau cắt | Mô tả đo được |
|---|---|---|---|
| `manh_vo` | 1,10 s | 0,45 s | Lưới 3×3 lệch ngẫu nhiên → các **tứ giác / tam giác của cảnh MỚI** bay vào từ ngoài khung, nghiêng 3D + xoay, lưới **halftone** chấm, 3 **vệt tam giác đỏ**, 2 **tấm kính bo góc** mờ; phủ 55 % ở u 0,55 → kín 100 % ở u 0,80; 20 % cuối zoom tăng tốc (hoặc nảy). Đúng phách: **lóe lại cảnh cũ 1 khung** rồi nhoè-loé. Người ở cảnh cũ (nếu có) **đứng trước mảnh** (tách nền u2net). |
| `nhoe_loe` | 0 | 0,45 s | Nhoè Gauss σ = 3,0 · 2,6 · 1,8 · 0,8 · 0,2 % W + phủ trắng α = 0,46·e^(−k/4,3) và giảm màu; dùng sau mảnh vỡ. |
| `luot_trang` | 0,36 s | 0,24 s | Cảnh cũ lia ngang **tăng tốc** 1 → 54 px/khung + trắng dần tới 0,82; cảnh mới vào từ trắng 0,62 và **giảm tốc** 31 → 2 px/khung, nhoè ngang theo tốc độ. |
| `gon_song` | 0,14 s | 0,32 s | Đúng DROP: ánh xạ sóng sin (bước 9 % W) biên 0,4 → 2,6 % W, xoay nhẹ, nhoè; sau cắt biên 3 % → 0 trong 10 khung + phồng ×1,02. |
| `khoi` | 0,30 s | 0,12 s | Dịch pixel theo nhiễu mượt (kiểu khói / chất lỏng) biên tăng 0,2 → 3,2 % W + nhạt 18 %; sau cắt tan nhanh trong 4 khung. |
| `lia_nhoe` | 0,08 s | 0,50 s | Nhoè hướng 2,5 → 7 % W theo góc (90°, 35°, 0°, 145°…), dịch 1,2 → 3,5 % W; sau cắt dịch ngược 4,5 → 0,8 % W, zoom 1,07 → 1,01, nhoè 7 → 1,2 % + **rung tắt dần**. |
| `glitch` | 0,07 s | 0,37 s | Kéo giãn dọc theo dải, lệch RGB 1,5 % W, ám xanh / hồng, cháy trắng 0,55; giảm dần trong 13 khung. Chữ cũng bị glitch. |
| `cat` | 0 | 0 | Cắt thẳng. |

## 5. Khung điện ảnh mở đầu

- 0 → 0,76 s: hình chỉ là **dải ngang cao 0,47 H** (16:9; 9:16 dùng 0,30 H) giữa nền đen.
- Mở ra hết trong **0,25 s ease-out**, kết thúc trước phách F ~0,45 s.
- Người trong cảnh **nổi ra ngoài dải** (phần người vượt khỏi thanh đen vẫn hiện) — cần model `u2net_human_seg.onnx` (`~/.u2net/`).

## 6. HUD công nghệ (9,8 s → hết)

- **Số 7 đoạn rỗng** (chỉ viền) cao ~56 % H, trắng α 0,20, đổi số mỗi nửa nhịp.
- Chuỗi dữ liệu kiểu `<35468>`, `<CONT.66452318>`, `<ERROR/2B122>`… cỡ 3 % H, α 0,42.
- Mũi tên `>` `>>` nhấp nháy theo **móc đơn** (½ phách), α 0,92; vạch dọc mảnh α 0,22.
- Chỉ ở **mép khung**, hoà kiểu screen, né hộp chữ tên hãng.

## 7. Chữ

- **Tên hãng** (VINFAST): Barlow Condensed ExtraBold trắng, giãn chữ rất rộng (0,62 em), rộng 50 % W, tâm y 28,5 % H, bóng mềm 45 %.
  Gõ **từng ký tự**: chữ đầu hiện sau phách mạnh cảnh hero 0,4 phách, mỗi chữ sau +½ phách (22,16 → 23,7 s). Các ký tự đặt sẵn đúng chỗ cuối (không canh giữa lại khi gõ).
- **Dòng xe**: Barlow Condensed Black Italic, gradient đỏ (255,48,40) → (200,14,22), bóng, tâm (55 % W, 71,5 % H), hiện giữa cú glitch +0,13 s.
- Không có sub, không có chữ nào khác.

## 8. Màu

Xe sáng rực: làm nét (unsharp 0,65), độ rõ vùng trung (0,22), tương phản 1,08, **bão hoà 1,18**, tối góc 10 %. Nguồn iPhone HLG/PQ → tonemap hable về BT.709 trước.

## 9. Thứ tự lớp mỗi khung

cảnh (máy quay ảo + màu) → chuyển cảnh → HUD → chữ tên hãng → dòng xe → glitch (đè cả chữ) → khung điện ảnh (+ người nổi).
