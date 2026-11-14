# Khuôn `ke_hoach.json` — TuanJp_DuLich_ManNgang (16:9, 1920×1080, 30 fps)

Bản chốt 14/11/2026 (khách: luôn tràn màn, teaser cao trào, bản đồ A → B, bình luận ảo, màn cảm ơn). Mẫu điền đủ:
`references/vi-du-4-diem-den.json` (bản cũ thẻ dọc / ghép ô đã BỎ: `vi-du-4-diem-den_ban3_cu.json` — chỉ để tra giờ lời).

**Giờ:** phần thân (`canh`, `do_hoa`, `cta`, `luc_*`) = giây trong FILE AUDIO (lời Whisper, `loi_doc.txt`). Teaser (`mo_man`) = giây
từ 0 của video. `ke_hoach.py` tự dời cả phần thân thêm `OFF` = độ dài teaser (khớp ô nhịp) — KHÔNG tự cộng tay.

```jsonc
{
  "CAN_CLAUDE_SUA": false,            // nháp = true; Claude viết lại theo nghĩa rồi đặt false (kiem-kh ⛔ nếu còn true)
  "ngon_ngu": "vi",                   // = tiếng của audio — mọi chữ trên hình đúng tiếng này (trừ bình luận ảo: en / ko)
  "kenh": {"ten": "", "handle": "", "avatar": null},   // màn kết; avatar = tên file trong Resources hoặc đường dẫn
  "nhac": null,                       // null = tự lấy file nhạc trong Resources (nếu có); false = tắt; "đường dẫn" = ép file
  "nhac_bat_dau": null,               // giây bắt đầu nhạc THÂN (mặc định tự lùi cho nốt kết trùng cuối video)
  "dien_anh": true,                   // khung điện ảnh 2.35:1 từ đầu (cả teaser) tới lúc chữ mo_dau (cú DROP) hiện
  "sua_loi": {"chữ Whisper": "chữ đúng"},   // khoá khớp ĐÚNG chữ trong loi_doc.txt (bỏ dấu câu, không phân biệt hoa)
  "mo_man": { … },                    // TEASER mở màn (chỉ nhạc) — cần file nhạc; không nhạc thì tự bỏ + ⚠
  "canh": [ … ],
  "do_hoa": [ … ],
  "binh_luan": true,                  // false = tắt mọi bình luận ảo tự động
  "binh_luan_nn": ["en", "ko"],       // tiếng của bình luận ảo (mặc định Anh + Hàn)
  "cta": { … },
  "sub": {"bat": true, "giu_lien": ["Sa Pa", "Hạ Long"]},   // cụm không được ngắt (thêm từ chung vào assets/tu_ghep_vi.txt)
  "sfx_cta": true
}
```

## `mo_man` — MONTAGE TỔNG HỢP ≤ 10 s, CHỈ NHẠC (khách vòng 3: "chỉ giới thiệu 5–10 s, sau giây 10 phải có giọng… giống 1 cái tổng hợp cả video trong 10 giây đầu")

Claude chỉ XẾP THỨ TỰ cảnh + chữ, KHÔNG ghi giờ: `ke_hoach._tong_hop` đặt lên LƯỚI PHÁCH (độ dài tự khớp phách gần 9,5 s, 5–10 s), tự gán
vai + kỹ xảo + chữ (SKILL mục 15, 17). `kiem-kh` in 🔧 bảng "montage tổng hợp: nguồn vai giây kỹ xảo «tên»".

| Trường | Ý nghĩa |
|---|---|
| `kieu` | `tong_hop` (mặc định) · `nhip` (kiểu cũ 1 cảnh / ô nhịp — khách chê tuần tự, ⚠) |
| `nhac_tu` | giây trong file nhạc bắt đầu; trống = tự chọn đoạn CAO TRÀO / DROP (`nhip.chon_dau`). Nhạc teaser to ~ngang giọng (+12 dB so với nền), hoà vào nhạc thân 1 s ở chỗ giọng vào |
| `canh` | 10–14 cảnh hay nhất KHẮP video, THEO THỨ TỰ: 3 cảnh đầu = **BA CỘT** (3 điểm đến khác nhau, mỗi cảnh `chu` + `nhan`) → **tên** (cảnh đầu mỗi điểm đến còn lại có `chu` = tên, `nhan` = 1 tính từ đắt trong lời: Thơ mộng / Kỳ vĩ…; + 0–1 cảnh cùng điểm; cảnh rơi vào kỹ xảo `hai_nua` = **CÚ ĐẨY**: `chu` / `nhan` thành chữ chạy theo mép đẩy — nên chọn cảnh CÓ NGƯỜI rõ (2–50 % khung) để người tách nền nhô qua mép, `chu` vẫn phải có trong lời, vd "Cáp treo · Biển mây"; `nhan_vat: false` tắt người) → **dồn** (4–8 cảnh không chữ: người, trải nghiệm, món, cảnh lạ — nối bằng ĐẨY phải → trái mỗi 1 phách; 3–4 cảnh là đủ, thừa thì script bỏ bớt) → cảnh cuối = **đỉnh** (ảnh to nét nhất). Mỗi cảnh: `nguon`, `vao` (giây clip), `cat_y` / `vung`, `chu`, `nhan`; tuỳ chọn `nhip` (số phách, bước 0,5), `vai` (`cot` / `mo` / `ten` / `nhanh` / `dinh`), `chuyen` (kỹ xảo bất kỳ trong bảng `canh.chuyen`), `toc_do`, `khop`, `loi` (ghi chú, không dùng) |
| `dinh` | tít cảnh đỉnh `{dan, khoa, viet_tay}` — chữ lấy từ lời (vd "4 điểm đến / 4 vẻ đẹp / khác nhau"), cỡ 210, đập cùng cảnh đỉnh |
| `ba_cot` | `false` = cảnh đầu mở thường (cảnh `mo` 2 phách, không ba cột) |
| `bat` | `false` = bỏ teaser |

Mọi nấc kỹ xảo montage rơi đúng phách / ½ phách (`CHUYEN_NHIP`, lưới phách bám tiếng trống thật); giọng vào = VỠ KÍNH + riser + boom (vòng 4).

Ví dụ (Màn Ngang 14/11/2026 vòng 4, 15 phách × 0,631 s = 9,47 s):
`{"kieu": "tong_hop", "canh": [{"nguon": "res_07", "chu": "Sa Pa", "nhan": "Thơ mộng"}, {"nguon": "res_05", "chu": "Hạ Long", "nhan": "Kỳ vĩ"},
{"nguon": "res_06", "chu": "Ninh Bình", "nhan": "Bình yên"}, {"nguon": "clip_03", "vao": 3.6, "chu": "Bản Giốc", "nhan": "Hoang sơ"},
{"nguon": "res_04", "chu": "Cáp treo", "nhan": "Biển mây"}, {"nguon": "clip_09", "vao": 9.0}, {"nguon": "clip_16", "vao": 0.3}, …, {"nguon": "res_08"}], "dinh": {"dan": "4 điểm đến", "khoa": "4 vẻ đẹp", "viet_tay": "khác nhau"}}`

## `cao_trao` — KỸ XẢO ĐIỆN ẢNH ~30 s đầu (tự động; người dùng 14/11/2026: "cảnh đầu hiệu ứng chuyển cảnh xịn liên tục… sau 30 s bình thường")

Không ghi gì = BẬT: mọi cú cắt từ 0 tới cú DROP (`mo_dau` đầu tiên; không có thì 30 s) tự gán kỹ xảo xoay vòng
`vo_kinh` → `xoay` → `glitch` → `lat_3d` → `chay_phim` → `xuyen` → `iris` → `tia_sang` → `khung_bung` → `hai_nua` → `dai_truot` →
`hai_nua_doc` (kiểu montage CHƯA dùng lên trước, không lặp vỡ kính; kiểu dài cần 2 cảnh kề ≥ 1,8 s, không thì `xoay`), cú trùng DROP = `xuyen`;
+ khung 0 đập mở màn, đập theo phách giữa 2 cú cắt teaser, 1 tiếng mỗi kỹ xảo. `kiem-kh` in 🔧 danh sách đã gán.
Tuỳ chỉnh: `"cao_trao": {"fx": ["xoay", "glitch"], "het": 25, "mo": false}` · tắt: `"cao_trao": false` · giữ 1 cú: `chuyen` là 1 kỹ xảo
(giữ nguyên), hoặc `"giu_chuyen": true` trên cảnh; `man` (mở chương) luôn giữ.

## `canh` — mỗi cụm lời 1 cảnh, LUÔN TRÀN MÀN (≥ 2,5 s; < 1,5 s ⛔), `tu` = đầu cụm lời (− 0,1 s)

| Trường | Ý nghĩa |
|---|---|
| `id`, `tu` | mã + giây bắt đầu (cảnh kết thúc ở `tu` cảnh sau) |
| `nguon` | 1 mã `clip_NN` / `res_NN` (xem `goi_y.txt`, `tai_nguyen.jpg`) — KHÔNG ghép nhiều nguồn |
| `vao` | giây bắt đầu trong clip (soi `khung/clip_NN.jpg`: tránh tay / điện thoại che, rung, chữ dán) |
| `bo_cuc` | chỉ `tran` (mặc định). `the_doc` / `ghep` / `the_anh` ĐÃ BỎ (khách 14/11: "giống màn hình dọc quá") → ⛔ |
| `cat_y`, `cat_x` | neo dải 16:9 khi cắt (0 trên/trái … 1 dưới/phải). Nguồn DỌC mặc định `cat_y` 0,42 (trời + chủ thể); soi khung rồi chỉnh để giữ mặt / chủ thể |
| `vung` | cắt 1 vùng nguồn `[x0, y0, x1, y1]` (0–1) TRƯỚC khi khớp khung — 1 ảnh to cho nhiều cảnh khác khung, cắt logo dán |
| `chuyen` | chuyển VÀO cảnh (KHÔNG nhoè, MƯỢT 0,6–0,8 s): `zoom_muot` · `lia` / `lia_doc` · `truot` · `loe` · `hoa_tan` · `nhoe` (ngày → đêm) · `man` (màn quét — mở CHƯƠNG / bản đồ) · `cat`. Gấp, chỉ khi cố ý: `zoom`, `phong`. Kỹ xảo điện ảnh (đoạn cao trào, tự gán): `vo_kinh` · `xoay` · `glitch` · `lat_3d` · `chay_phim` · `xuyen` · `iris` · `tia_sang` · `dap` · `nhay_trang` · `nhay_den` · `day_nhanh` (đẩy phải → trái, đoạn dồn montage). **5 kỹ xảo mẫu** (SKILL mục 17; chia màn tạm thời → tràn): `khung_bung` (khung nhỏ viền trắng bung to) · `hai_nua` (cú ĐẨY: cảnh cũ bị đẩy trái, mép sáng 3 nấc, chữ chạy theo mép + người tách nền nhô qua mép) / `hai_nua_doc` (chia trên / dưới) · `dai_truot` (dải ảnh trượt, ảnh cảnh mới phóng ra; `dai: [id…]` chọn ảnh dải) · `khop_hinh` (cắt nối theo hình; `khop: {ra: [x, y, r], vao: [x, y, r]}` 0–1, thiếu = tự dò) · `ba_cot` (chỉ montage) — kiểu dài cần 2 cảnh kề ≥ 1,8 s |
| `chuyen_dong` | Ken Burns: `zoom_vao` · `zoom_ra` · `lia_trai` · `lia_phai` · `lia_len` · `lia_xuong` · `dung` |
| `toc_do` | tốc độ clip (0,6–1,2) |

Nguồn nhỏ phóng > 1,6× (ngang) / > 1,9× (dọc) → ⚠ mềm (đã tự làm nét `cas`) — báo ở D4.

## `do_hoa` — mỗi lúc tối đa 1 đồ hoạ LỚN (`dia_danh`, `chip` nhỏ, được chồng). Mỗi mục chữ đứng ≥ 1,6 s.

Chung: `id`, `loai`, `tu`, `den`, `vi_tri` (`trai` / `phai` / `giua`), `y` (tâm dọc khối chữ, mặc định 470 — đổi để né MẶT người / chủ thể).

| `loai` | Trường | Dùng khi |
|---|---|---|
| `mo_dau` | `tren`, `chinh` (TÊN in hoa lớn), `viet_tay`, `duoi`, `drop` (mặc định true: riser → boom + loé + rung + chữ đập trọn 0,32 s) | lần đầu gọi tên chủ đề (1 lần) — cú DROP, hết khung điện ảnh |
| `hook_tu` | `chu`, `nhan` (nhỏ, có ghim), `icon`, `kieu: "cau"` (câu hỏi nghiêng), `y` | mỗi vế câu hook / mỗi cảnh teaser |
| `chuong` | `so` (tự đánh 01, 02…), `ten`, `phu`, `icon`, **`toa_do` [lat, lon]** (`run.py tim "<tên>"`), `ten_ban_do`, `xuat_phat` ({ten, toa_do}; mặc định = chương trước, chương đầu = Hà Nội), `phuong_tien` (`o_to` mặc định · `xe_may` · `xe_buyt` · `may_bay` · `tau_hoa` · `tau_thuy` · `di_bo` · `xe_dap`), `luc_den` (giây sà tới điểm đến — tên điểm đến đập vào), `thoi_gian` / `khoang_cach` (CHỈ khi lời nói số — ghi đè số ước tính), `ban_do: false` (tắt bản đồ), `binh_luan: false` / `so_binh_luan` / `luc_binh_luan` / `ten_binh_luan` / `loai_canh` | MỞ mỗi điểm đến = **BẢN ĐỒ VỆ TINH A → B kiểu Google Maps** (≥ 3,6 s, cảnh dưới `chuyen: "man"`): camera cận điểm đi → toàn tuyến → sà điểm đến, tuyến xanh + xe chạy theo đường thật OSRM, ghim đỏ rơi, thẻ trắng "≈ 4 giờ 15 phút (314 km)", bản đồ VN nhỏ có Hoàng Sa / Trường Sa. Số ước tính luôn "≈" → XÁC NHẬN ở D7 |
| `hanh_trinh` | `xuat_phat`, `diem_den` ({ten, toa_do}), `phuong_tien`, `thoi_gian`, `khoang_cach`, `luc_di`, `luc_den` | câu DI CHUYỂN A → B không phải mở chương (cùng kiểu bản đồ) |
| `binh_luan` | `ten` (điểm / món), `muc: [{nn, chu, ten, khen: false}]` (thiếu thì tự điền từ `assets/binh_luan.json`), `so`, `loai_canh` | tự viết tay bình luận cho MÓN ĂN / điểm không phải chương. Chương tự có 1 đợt 3 thẻ (2 khen + 1 chê nhẹ, en / ko) ở chỗ trống đầu tiên sau `den` + 2,5 s, cột phải, né mọi đồ hoạ lớn |
| `dia_danh` | `ten`, `phu`, `icon` | thẻ góc dưới khi lời nói tên 1 điểm cụ thể (đỉnh, hang, bến…) |
| `tu_khoa` | `muc: [{chu, luc, kieu: serif / tay / sans}]`, `co` | 1–3 từ đắt; ≥ 3 mục tự xếp CỘT (1 hàng dài dễ đè người) |
| `tieu_de` | `dan`, `khoa` (in hoa, tự 2 dòng cân), `viet_tay` | ý chuyển đoạn / tổng kết / câu kết |
| `chip` | `muc: [{chu, icon, luc}]`, `y` (mặc định 96 — hàng trên) | 1–3 đặc điểm ngắn |
| `liet_ke` | `dan`, `muc: [{chu, icon, luc}]` | 2–5 thứ được kể — đặt bên trống của khung (né chủ thể) |
| `so_lon` | `so`, `tien_to`, `hau_to`, `nhan`, `dem_tu` | con số CÓ TRONG LỜI (không bịa) |
| `trich` | `noi`, `tac_gia` | câu nói nổi bật |
| `ban_do` | `diem: [{ten, toa_do, luc, nhan: trai/phai}]` | lời liệt kê nhiều nơi trên đất nước — bản đồ VN to, ghim rơi đúng giây đọc tên |

Icon: `ghim nui bien dao thac may mat_troi trang sao tim may_anh tau tau_hoa cap_treo xe_may o_to may_bay di_bo co den_long phao_hoa drone hoa la lua ruong chua cau thanh_pho lich_su dong_ho nhiet_do an_uong ca_phe lap_lanh balo la_ban ban_do nguoi gio tuyet mua song_nuoc non_la cay tich ve gia khach_san leu hang`.

## `cta` — MÀN KẾT CẢM ƠN (khách: "cuối video cảm ơn mọi người xem và hãy like và đăng ký")

`tu` (đầu câu hỏi / câu kêu gọi cuối), `cau_hoi` (câu hỏi cho khán giả — lấy từ lời), `lua_chon` (2–5 lựa chọn đánh số; cần `cau_hoi`),
`cam_on` (mặc định "Cảm ơn bạn đã xem"), `loi_moi` (mặc định "Nhấn Thích & Đăng ký kênh…"), `nut` / `nut_da`, `chuong_nhan`, `bat: false` để tắt.
Giờ tự tính: `luc_cam_on` = sau khi giọng đọc xong câu hỏi (≤ `tu` + 3,5 s) → `luc_bam` (+1,8: tay bấm ĐĂNG KÝ → xám + chuông lắc)
→ `luc_thich` (+1,3: tay bấm Thích → tim bay); video tự kéo dài đủ ≥ 1,5 s sau cú Thích. Sub tắt trong màn kết.
