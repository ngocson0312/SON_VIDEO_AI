# Khuôn `ke_hoach.json` — TuanJp_DuLich_ManNgang (16:9, 1920×1080, 30 fps)

Mọi giây là giây trong file audio (lời Whisper, `loi_doc.txt`). Mẫu điền đủ: `references/vi-du-4-diem-den.json`.

```jsonc
{
  "CAN_CLAUDE_SUA": false,            // nháp = true; Claude viết lại theo nghĩa rồi đặt false (kiem-kh ⛔ nếu còn true)
  "ngon_ngu": "vi",                   // = tiếng của audio — mọi chữ trên hình đúng tiếng này
  "kenh": {"ten": "", "handle": "", "avatar": null},   // màn kết; avatar = tên file trong Resources hoặc đường dẫn
  "nhac": null,                       // null = tự lấy file nhạc trong Resources (nếu có); false = tắt; "đường dẫn" = ép file
  "nhac_bat_dau": null,               // giây bắt đầu trong file nhạc (mặc định tự lùi cho nốt kết trùng cuối video)
  "dien_anh": true,                   // khung điện ảnh 2.35:1 (dải đen trên/dưới) từ đầu tới lúc chữ mo_dau hiện
  "sua_loi": {"chữ Whisper": "chữ đúng"},   // khoá khớp ĐÚNG chữ trong loi_doc.txt (bỏ dấu câu, không phân biệt hoa)
  "canh": [ … ],
  "do_hoa": [ … ],
  "cta": { … },
  "sub": {"bat": true, "giu_lien": ["Sa Pa", "Hạ Long"]},   // cụm không được ngắt giữa 2 dòng / 2 cụm sub
  "sfx_cta": true
}
```

## `canh` — mỗi cụm lời 1 cảnh (≥ 1,2 s; ảnh ≥ 2 s), `tu` = đầu cụm lời (− 0,1 s)

| Trường | Ý nghĩa |
|---|---|
| `id`, `tu` | mã + giây bắt đầu (cảnh kết thúc ở `tu` cảnh sau) |
| `nguon` | `clip_NN` / `res_NN` (xem `goi_y.txt`, `tai_nguyen.jpg`); `ghep` = danh sách 2–4 mã |
| `vao` | giây bắt đầu trong clip (soi `khung/clip_NN.jpg`: tránh tay / điện thoại che, rung, chữ dán); `ghep` = danh sách |
| `bo_cuc` | `tran` (clip / ảnh NGANG tràn khung) · `the_doc` (clip / ảnh DỌC thành thẻ bo góc 506×900 trên nền nhoè của chính nó) · `ghep` (2–4 ô cao trọn khung, trượt vào so le) · `the_anh` (ảnh nhỏ < 1500 px thành thẻ ảnh viền kem nghiêng nhẹ). Bỏ trống = tự chọn theo hướng / cỡ nguồn |
| `vi_tri` | `the_doc` / `the_anh`: `giua` / `trai` / `phai` — thẻ một bên thì chữ đồ hoạ đặt bên kia |
| `chuyen` | chuyển VÀO cảnh (KHÔNG nhoè, MƯỢT 0,6–0,8 s): `zoom_muot` (mặc định "xịn": cũ đẩy vào, mới thu về chồng lên) · `lia` / `lia_doc` (trượt có chiều sâu) · `truot` (đẩy ngang êm) · `loe` (loé nắng ấm) · `hoa_tan` · `nhoe` (hoà tan sáng bừng, ngày → đêm) · `man` (màn sáng quét chéo + whoosh — mở CHƯƠNG) · `cat`. Gấp, chỉ khi cố ý: `zoom` (phóng vụt → loé), `phong` (cắt + đập vào 0,3 s). Cảnh ≥ 2,5 s |
| `chuyen_dong` | Ken Burns: `zoom_vao` · `zoom_ra` · `lia_trai` · `lia_phai` · `lia_len` · `lia_xuong` · `dung` (ảnh mạnh, clip nhẹ) |
| `vung` | cắt 1 vùng nguồn `[x0, y0, x1, y1]` (0–1) TRƯỚC khi khớp khung — dùng 1 ảnh to cho nhiều cảnh khác khung (toàn cảnh / cận thác / cận thuyền…), cắt logo dán; `ghep` = danh sách vùng |
| `cat_x`, `cat_y` | neo cắt khi khớp tỉ lệ (0 trái/trên … 1 phải/dưới); `ghep` = danh sách |
| `toc_do` | tốc độ clip (0,6–1,2) |
| `luc_o` | `ghep`: giây từng ô trượt vào (khớp lúc đọc tên từng mục); cảnh trước nằm dưới tới khi phủ kín. Bỏ trống = so le 0,12 s |
| `nhan` | `ghep`: nhãn từng ô `[{"chu": "Sa Pa", "phu": "thơ mộng"}]` (serif + viết tay, hiện sau khi ô vào) |
| `nghieng` | độ nghiêng thẻ (độ) |

## `do_hoa` — mỗi lúc tối đa 1 đồ hoạ LỚN (`dia_danh`, `chip` là nhỏ, được chồng). Mỗi mục chữ đứng ≥ 1,6 s.

Chung: `id`, `loai`, `tu`, `den`, `vi_tri` (`trai` / `phai` / `giua`), `y` (tâm dọc khối chữ, mặc định 470 — đổi để né người / chủ thể).

| `loai` | Trường | Dùng khi |
|---|---|---|
| `mo_dau` | `tren` (chữ in giãn nhỏ), `chinh` (TÊN serif lớn), `viet_tay`, `duoi` (dòng nhỏ: liệt kê điểm đến…), `drop` (mặc định true: riser → boom + loé + rung + chữ đập vào trọn 0,32 s) | lần đầu gọi tên chủ đề / điểm đến (1 lần) |
| `hook_tu` | `chu` (chữ khoá — khối chữ Anton in hoa), `nhan` (địa danh nhỏ có ghim), `icon`, `kieu: "cau"` (câu hỏi serif nghiêng, cho khung 0), `y` (mặc định 520) | mỗi vế của câu hook (1 cảnh / vế); `tu` = đầu cảnh (hoặc chữ khoá trong vế), `den` = cảnh sau − 0,03 |
| `chuong` | `so` ("01"), `nhan` (mặc định "Điểm đến"), `ten`, `ten_ngan` (nhãn bản đồ), `phu`, `icon`, `toa_do` [lat, lon] → thẻ BẢN ĐỒ VIỆT NAM góc trên (có Hoàng Sa, Trường Sa) với ghim toả sóng | mở mỗi địa điểm lớn (đi kèm cảnh `chuyen: "man"`) |
| `dia_danh` | `ten`, `phu`, `icon` | thẻ góc dưới (lower third) khi lời nói tên 1 điểm cụ thể (đỉnh, hang, bến…) |
| `tu_khoa` | `muc: [{chu, luc, kieu: serif / tay / sans}]` | 1–3 từ đắt của câu, bật đúng giây đọc |
| `tieu_de` | `dan`, `khoa` (serif vàng, tự 2 dòng cân), `viet_tay` | ý chuyển đoạn / câu tổng kết / câu kết |
| `chip` | `muc: [{chu, icon, luc}]`, `y` (mặc định 96 — hàng trên) | 1–3 đặc điểm ngắn |
| `liet_ke` | `dan`, `muc: [{chu, icon, luc}]` | 2–5 thứ được kể — đặt bên trống cạnh thẻ dọc / thẻ ảnh |
| `so_lon` | `so`, `tien_to`, `hau_to`, `nhan`, `dem_tu` | con số CÓ TRONG LỜI (không bịa) |
| `trich` | `noi`, `tac_gia` | câu nói nổi bật |
| `ban_do` | `diem: [{ten, toa_do, luc, nhan: trai/phai}]` | lời liệt kê nhiều nơi trên đất nước — bản đồ VN to, ghim rơi đúng giây đọc tên |

Icon: `ghim nui bien dao thac may mat_troi trang sao tim may_anh tau tau_hoa cap_treo xe_may o_to may_bay di_bo co den_long phao_hoa drone hoa la lua ruong chua cau thanh_pho lich_su dong_ho nhiet_do an_uong ca_phe lap_lanh balo la_ban ban_do nguoi gio tuyet mua song_nuoc non_la cay tich ve gia khach_san leu hang`.

## `cta` — màn kết YouTube (≥ 5 s, chỗ gắn màn hình kết thúc)

`tu` (đầu câu kêu gọi / câu hỏi cuối), `cau_hoi` (câu hỏi cho khán giả bình luận — lấy từ lời), `lua_chon` (2–4 lựa chọn đánh số),
`tieu_de` (dùng khi không có câu hỏi), `viet_tay`, `nut` / `nut_da` (mặc định ĐĂNG KÝ / ĐÃ ĐĂNG KÝ), `bat: false` để tắt.
Tự động: avatar vòng xoay + tên kênh tích xanh, nút Đăng ký bóng quét + sóng → tay bấm → xám + chuông lắc, tay bấm Thích → tô xanh + tim bay.
Sub tắt trong màn kết (màn kết đã có chữ). Cảnh dưới màn kết nên là `the_anh` / `the_doc` `vi_tri: "phai"` (cột chữ bên trái ≤ 780 px).
