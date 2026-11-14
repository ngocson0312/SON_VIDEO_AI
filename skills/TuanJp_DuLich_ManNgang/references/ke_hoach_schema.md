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

## `mo_man` — TEASER mở màn ~20 s, CHỈ NHẠC (khách: "đầu video ~30 s cao trào, xem cái là muốn đi du lịch luôn")

| Trường | Ý nghĩa |
|---|---|
| `dai` | độ dài teaser (12–32 s, mặc định 20) — tự khớp về ô nhịp gần nhất (`nhip.py`: BPM, phách mạnh) |
| `nhac_tu` | giây trong file nhạc bắt đầu teaser; bỏ trống = tự chọn đoạn CAO TRÀO (`nhip.chon_dau`). Nhạc teaser to ~ngang giọng (+12 dB so với nền), hoà vào nhạc thân 1 s ở chỗ giọng vào |
| `canh` | 6–10 cảnh ĐẸP NHẤT (mỗi điểm đến 1–2 cảnh), `tu` từ 0, cảnh ≥ 1,8 s (`CANH_TEASER_MIN`); `tu` tự bám phách; chuyển mặc định `phong` (đập vào đúng phách), cảnh đầu `cat`; cảnh cuối phải kết ≥ 1,8 s trước khi giọng vào |
| `do_hoa` | `hook_tu` mỗi điểm đến (`chu` = tên, `nhan` = 1 tính từ đắt trong lời: Thơ mộng / Kỳ vĩ…) hiện khi cảnh vào xong; kết bằng `tieu_de` tóm tắt (chữ lấy từ lời, vd "4 điểm đến / 4 vẻ đẹp / khác nhau"); mọi chữ teaser phải hết trước `dai` |
| `bat` | `false` = bỏ teaser |

## `canh` — mỗi cụm lời 1 cảnh, LUÔN TRÀN MÀN (≥ 2,5 s; < 1,5 s ⛔), `tu` = đầu cụm lời (− 0,1 s)

| Trường | Ý nghĩa |
|---|---|
| `id`, `tu` | mã + giây bắt đầu (cảnh kết thúc ở `tu` cảnh sau) |
| `nguon` | 1 mã `clip_NN` / `res_NN` (xem `goi_y.txt`, `tai_nguyen.jpg`) — KHÔNG ghép nhiều nguồn |
| `vao` | giây bắt đầu trong clip (soi `khung/clip_NN.jpg`: tránh tay / điện thoại che, rung, chữ dán) |
| `bo_cuc` | chỉ `tran` (mặc định). `the_doc` / `ghep` / `the_anh` ĐÃ BỎ (khách 14/11: "giống màn hình dọc quá") → ⛔ |
| `cat_y`, `cat_x` | neo dải 16:9 khi cắt (0 trên/trái … 1 dưới/phải). Nguồn DỌC mặc định `cat_y` 0,42 (trời + chủ thể); soi khung rồi chỉnh để giữ mặt / chủ thể |
| `vung` | cắt 1 vùng nguồn `[x0, y0, x1, y1]` (0–1) TRƯỚC khi khớp khung — 1 ảnh to cho nhiều cảnh khác khung, cắt logo dán |
| `chuyen` | chuyển VÀO cảnh (KHÔNG nhoè, MƯỢT 0,6–0,8 s): `zoom_muot` · `lia` / `lia_doc` · `truot` · `loe` · `hoa_tan` · `nhoe` (ngày → đêm) · `man` (màn quét — mở CHƯƠNG / bản đồ) · `cat`. Gấp, chỉ khi cố ý: `zoom`, `phong` |
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
