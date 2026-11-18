# ke_hoach.json — cấu hình riêng từng video

Đặt ở `<GYM_WORK>\ke_hoach.json` (hoặc đường dẫn trong biến `GYM_PLAN`). `dung.py` đọc khi khởi động và ĐÈ các hằng số mặc định. Mọi giây là **giây GỐC** (của video thô) trừ `cold` / `cold_txt` / `sfx.cold` (giây của đoạn hook, 0 → D0). Mẫu đầy đủ đã chạy: `ke_hoach_mau_vinh.json`.

| Khoá | Kiểu | Ý nghĩa |
|---|---|---|
| `hook` | `[t0, t1]` | đoạn lời (giây gốc) lấy làm teaser mở đầu; `D0 = t1 − t0` (≈ 3–4 s). Âm của đoạn này phát ở đầu, rồi video chạy lại từ 0 |
| `src_dur` | số | độ dài tiếng của video thô (bỏ trống → ffprobe) |
| `extra` | số | giữ đuôi sau khi hết lời (mặc định 0,5 s — CTA bấm xong là hết) |
| `shots` | `[[t0, t1, cx, cy, cw0, cw1], …]` | khung cắt từng cảnh quay: tâm (cx, cy) trong khung nguồn 1080×1920, bề rộng cắt đầu → cuối cảnh (zoom chậm). Ô video là 1080×1110 nên cắt cân quanh hành động, không cắt đầu |
| `cuts` | `[giây…]` | cú cắt cứng của video thô (đổi cảnh quay) |
| `punch` | `[giây…]` | mốc zoom đập thêm (đầu mỗi cảnh bảng vẽ…); `cuts` tự được cộng vào |
| `full_out` | số | giây video ra TOÀN MÀN + sub xuống y = 1130 (mặc định `src_dur − 7`) |
| `cold` | `[[t0, t1, giây_nguồn], …]` | 4 cảnh hook: trong khoảng t0–t1 (giây hook) lấy clip nguồn bắt đầu ở `giây_nguồn` |
| `cold_txt` | `[[t0, t1, "DÒNG 1\nDÒNG 2", "màu"], …]` | chữ đập có viền + khối 3D; màu: `amber`, `white`, `mint`, `coral`, `ice`, `violet` hoặc `[r,g,b]` |
| `stickers` | `[[t0, t1, "TEM", "màu"], …]` | tem từ khoá góc trên-trái ô video |
| `sfx` | `{"cold": [[t, "file", dB]…], "main": […]}` | file trong `assets/sfx`; `cold` theo giây hook, `main` theo giây gốc |
| `cta` | `{"t_btn": s, "t_hand": s}` | giờ nút FOLLOW hiện / tay vào (mặc định tay vào `src_dur − 1,37`, nút hiện trước 0,7 s). Tay bấm tại `t_hand + 0,72`, hết video ~1 s sau |
| `scenes_file` | đường dẫn | file `.py` có `SCENES = [(t0, t1, hàm)…]` thay cảnh bảng vẽ mẫu (xem SKILL.md mục 6) |

SFX CTA (whoosh toàn màn tại `full_out`, pop nút, swoosh tay, click + pop khi bấm) được `dung.py` TỰ thêm — đừng ghi lại trong `sfx`.

Thư mục skill chạy được từ bất kỳ đâu; font ở `assets/fonts`, SFX ở `assets/sfx`.
