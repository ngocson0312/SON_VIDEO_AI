# ke_hoach.json — khuôn kế hoạch bds_model_3d

Mọi giây là **giây tuyệt đối của video ra**. Mẫu đầy đủ (dựng lại video mẫu): `vi-du-video-mau.json`.
Sau khi sửa: đặt `"CAN_CLAUDE_SUA": false` → `run.py kiem-kh`.

```jsonc
{
 "CAN_CLAUDE_SUA": false,
 "thoi_luong": 35.82,            // quet tự điền (video: đúng độ dài video; audio: tiếng cuối + ~1,4 s)
 "doan": ["tên dự án trên Maps lấy từ ...?"],   // mục Claude ĐOÁN → in ở bang_duyet.txt, hỏi ở cổng duyệt
 "canh": [ … ],                  // liền nhau từ 0 tới thoi_luong, mỗi cảnh ≥ 0,8 s (nên 2,5–4 s)
 "chu": [ … ],                   // chữ 2 tầng (KHÔNG phải sub nguyên văn)
 "vien_kinh": [ … ],             // viên kính icon + gạch ngang (bác bỏ cách cũ)
 "o_kinh": [ … ],                // hàng ô kính đánh số (N bước / N thứ)
 "nhac": {"file": null, "muc": -23, "dang": 16},
 "sfx": {"tat": false, "bo": [], "them": []}
}
```

## 1. `canh` — 6 loại

| loai | footage | dùng khi |
|---|---|---|
| `the_noi` | thẻ nổi nghiêng 3D giữa nền than | HOOK mở đầu (2,5–6 s) |
| `tran_man` | tràn màn + dải tối trên đầu cho chữ | khoe kết quả / "đây là…" |
| `nen_nhoe` | tràn màn nhoè 30 px + tối 58 % | nền cho ô kính / chữ giữa |
| `nen_toi` | không (nền than) | chỉ chữ / chỉ viên kính |
| `giao_dien` | không — thẻ app mô phỏng 880×1400 | "Bước N", thao tác: tìm, ghim, chat AI, gửi |
| `dien_thoai` | không — iPhone nghiêng 3D | CTA "comment / nhắn / inbox + từ khoá" |

Chung: `{"id": "hook", "loai": "...", "tu": 0.0, "den": 6.2}`.

**Footage** (`the_noi`, `tran_man`, `nen_nhoe`):
```json
"footage": {"nguon": "ket_qua_ban_do", "tu_giay": 0.0, "toc_do": 1.0, "tam": [0.5, 0.5]}
```
- `nguon` = khoá trong `footage.json` (quet in ra tờ `tai_nguyen.jpg`; chế độ `--video` có khoá `video` = chính video vào).
- **Không ghi `footage`** ở cảnh footage nối ngay sau cảnh footage → **giữ shot cũ** (cùng clip chạy tiếp) và chuyển trạng thái mượt: thẻ→tràn 0,5 s, tràn→nhoè 0,7 s, nhoè→tràn 0,5 s. Muốn shot mới (cắt sang clip khác / đoạn khác) thì ghi `footage`.
- `tu_giay` mặc định: nguồn `video` = giây cảnh (đồng bộ lời); clip khác = 0. `toc_do` < 1 chậm lại. `tam` = điểm giữ khi cắt 9:16 (x, y 0–1).
- Cảnh `tran_man` ngay sau `giao_dien`: footage **trồi lên từ khung thẻ** (giống mẫu 25,5 s). Ghi `"vao": "hoa_tan"` nếu muốn hoà tan thường.

### `giao_dien` + `"mau": "ban_do"` → khối `"ban_do"`
```json
{"goi_y": "Tìm kiếm tại đây", "avatar": "V",
 "o_tim": {"chu": "Dự án JDI Land", "luc": 13.5, "den": 14.4},
 "nhan_ban_do": ["Hồ Đống Đa", "Thanh Xuân", "Royal City", "Láng Hạ"],
 "ghim": {"ten": "Dự án JDI Land", "luc": 14.95},
 "bang": {"luc": 15.4, "ten": "Dự án JDI Land", "phu": "Khu căn hộ", "dia_chi": "37 Lê Văn Lương, Thanh Xuân, Hà Nội"},
 "cham": {"luc": 15.9},
 "thong_bao": {"luc": 16.15, "chu": "Đã sao chép địa chỉ"}}
```
Bản đồ là hình vẽ minh hoạ (không phải bản đồ thật) — tên / địa chỉ chỉ lấy từ lời hoặc người dùng, không có thì ghi vào `doan`.
Gõ phím ~12–16 ký tự/giây (`den − luc ≈ len(chu)/14`).

### `giao_dien` + `"mau": "chat_ai"` → khối `"chat_ai"`
```json
{"ten_app": "Claude", "mo_hinh": "Opus 5.5", "loi_chao": "Hôm nay mình\nlàm gì nhỉ?",
 "viec": [
  {"lam": "dan", "luc": 17.45, "nhan": "ĐÃ DÁN", "chu": "37 Lê Văn Lương…"},
  {"lam": "tep", "luc": 18.4, "ten": "Tong-hop-du-an.pdf", "phu": "PDF · 4,2 MB"},
  {"lam": "go", "luc": 19.7, "den": 20.4, "chu": "Dựng video map 3D…"},
  {"lam": "gui", "luc": 20.5, "the_nho": ["37 Lê Văn Lương…", "Tong-hop-du-an.pdf"]},
  {"lam": "dang_lam", "luc": 20.8, "chu": "Đang dựng video…", "buoc": ["Đọc file", "Định vị dự án"]},
  {"lam": "xoa", "luc": 21.25},
  {"lam": "video", "luc": 22.4, "nhan": "Video mẫu", "anh": {"nguon": "ket_qua_ban_do", "tu_giay": 9.7}},
  {"lam": "video_vao_o", "luc": 23.3},
  {"lam": "go", "luc": 23.9, "den": 24.6, "chu": "Làm lại theo phong cách video mẫu này nhé!"},
  {"lam": "gui", "luc": 24.95}]}
```
`xoa` = cuộn sạch khung chat (đổi bước trong cùng thẻ, mẫu Bước 2 → Bước 3). `video.anh` = `{"nguon", "tu_giay"}` hoặc `{"file": "ảnh.jpg"}`.
Đổi tên app (ChatGPT, Gemini…) bằng `ten_app`; icon vẫn là hình sao cam kiểu Claude.

### `giao_dien` + `"mau": "anh"` → khối `"anh"` (ảnh / quay màn hình thật trong thẻ)
```json
{"file": "D:/…/anh.png"}                                 // hoặc
{"nguon": "quay_man_hinh", "tu_giay": 3.0}                // 1 khung tĩnh của clip, hoặc
{"clip": {"nguon": "quay_man_hinh", "tu_giay": 3.0, "toc_do": 1.0}}   // clip chạy trong thẻ
// thêm: "zoom": [1, 1.06], "cham": [{"luc": 14.2, "x": 0.8, "y": 0.35}]   (gợn chạm, x/y 0–1 của thẻ)
```

### `dien_thoai` → khối `"dien_thoai"`
```json
{"ten": "Khách hàng", "trang_thai": "Vừa mới truy cập", "ngay": "Hôm nay", "gio_may": "9:41",
 "tin": [
  {"luc": 30.0, "ben": "khach", "chu": "prompt map", "gio": "21:14"},
  {"luc": 30.55, "den": 31.3, "lam": "dang_go"},
  {"luc": 31.35, "ben": "toi", "loai": "tai_lieu", "tieu_de": "Hướng dẫn làm video map BĐS", "phu": "Google Tài liệu · docs.google.com", "gio": "21:15"},
  {"luc": 33.0, "ben": "toi", "chu": "Hướng dẫn **chi tiết** đây nhé!", "gio": "21:15"}]}
```
Tin khách ≤ 16 ký tự tự in TO (từ khoá CTA). `**…**` = chữ đậm. Tối đa ~4 tin (màn hình không cuộn).

## 2. `chu` — chữ 2 tầng

```json
{"tu": 0.5, "den": 2.75, "vi_tri": "tren", "dong": [
  [{"t": "Video này hoàn toàn", "k": "dan"}],
  [{"t": "được làm từ", "k": "dan"}, {"t": "Claude AI", "k": "vang"}]]}
```
| k | kiểu | dùng |
|---|---|---|
| `dan` | Regular 43 px trắng | dòng dẫn nhỏ |
| `vang` | ExtraBold Italic 74 px **#FDF02A** | từ ĐẮT nhất cụm (số, kết quả, tính từ mạnh) |
| `trang` | ExtraBold 68 px trắng | khoá không cần màu |
| `buoc` | ExtraBold Italic 52 px vàng | "Bước N" (hiện nguyên cụm) |
| `tit` | ExtraBold 62 px trắng | tít bước (hiện nguyên cụm) |
| `noi` | Regular 30 px | từ nối nhỏ giữa tít: "+", "cho" |
| `trich` | ExtraBold Italic 62 px vàng + “ ” | từ khoá CTA |

- `vi_tri`: `tren` (mép trên 148 px; cảnh điện thoại tự lên 100), `giua` (560 — đi với ô kính), hoặc số px.
- Từng từ tự khớp lời (hiện trước tiếng 0,22 s, nhoè→nét). Cụm chưa tới `tu` thì từ chưa hiện. `luc` ép giờ hiện của 1 mảnh; `tung_tu: true/false` ép kiểu hiện.
- Ra: cả cụm nhoè-mờ 0,22 s trước `den`. **Hai cụm cùng vị trí không được chồng giờ** (kiem-kh báo ⛔).
- Chữ tóm tắt 2–6 từ/cụm, ≤ 2 dòng; dòng `vang` ≤ ~22 ký tự (rộng > 1000 px là ⛔ tràn mép).

## 3. `vien_kinh` / `o_kinh`
```json
"vien_kinh": [{"tu": 2.9, "den": 4.3, "dan": "không cần", "icon": "ae", "chu": "After Effects", "gach": 3.75, "y": 980}]
"o_kinh": [{"tu": 10.65, "den": 12.95, "so": true, "y": 1056, "muc": [
   {"icon": "google_maps", "nhan": "Google Maps"}, {"icon": "claude", "nhan": "Claude"}, {"icon": "video", "nhan": "Video mẫu"}]}]
```
- `gach` (bỏ = không gạch) phải nằm trong (tu, den). Ô kính ≤ 5 ô (> 3 tự thu nhỏ), mỗi ô hiện cách 0,1 s (`luc` riêng nếu cần).
- **Icon có sẵn**: google_maps, claude, video, ae, dong_ho, tai_lieu, ban_do, nha, toa_nha, tien, dien_thoai, camera, check, sao, chat, ai, tim, nguoi, vi_tri, may_tinh, link, file;
  `chu:Pr:#2D0C4E:#E68CFF` (ô vuông có 1–3 chữ, màu nền:màu chữ — vd logo Premiere), `anh:file:///D:/…/logo.png`.

## 4. `nhac`, `sfx`
- `nhac.file`: file nhạc người dùng đưa (lặp nếu ngắn, mờ vào/ra). `muc` = dB so với giọng khi đang nói (−23), `dang` = dB dâng ở khoảng lặng lời ≥ 1 s (+16).
- SFX tự gắn theo sự kiện (bảng `SFX` trong `scripts/chung.py`). `tat: true` tắt hết; `bo: [giây,…]` bỏ tiếng gần giây đó (±0,12 s);
  `them: [{"luc": 12.3, "file": "sparkle.mp3", "db": -12}]` (file trong `assets/sfx`).

## Cảnh 3D công trình (`mo_hinh_3d`, `canh_3d`)

Khi người dùng chỉ có giọng + ảnh phối cảnh, hoặc muốn "3D như đoạn 3–9 s của mẫu", cảnh nào chiếu mô hình thì ghi
`"footage": {"nguon": "3d:<id>"}`. Cảnh sau không ghi footage thì bay tiếp cùng lượt.
Thêm 2 khối gốc:
- `mo_hinh_3d` = vị trí + tháp / đế / khối;
- `canh_3d` = mỗi lượt bay: camera `cam`, `chu_thich`, `logo`, `vong`, `dia_danh`, `tia`, chữ trong cảnh `chu`.

Schema đầy đủ + cách đọc ảnh ra tham số + ngôn ngữ camera: **`references/mo_hinh_3d.md`**; ví dụ chuẩn: **`references/vi-du-3d.json`**.
