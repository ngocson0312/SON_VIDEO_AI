# ke_hoach.json — khuôn kế hoạch TuấnJp_Dulich_ManDoc

Mọi giây là giây TUYỆT ĐỐI trên file giọng (lấy từ `loi_doc.txt`). Trường bắt đầu bằng `_` (vd `_loi`) là ghi chú, script bỏ qua.
Bản điền chuẩn: `vi-du-ha-noi.json`; có hành trình (máy bay / ô tô / bản đồ): `vi-du-hanh-trinh.json`; hành trình đè lên clip thật (`nen: "canh"`): `vi-du-hanh-trinh-canh.json`.

## Gốc

| Trường | Kiểu | Ý nghĩa |
|---|---|---|
| `CAN_CLAUDE_SUA` | bool | nháp = `true`; Claude sửa xong đặt `false` (còn `true` → ⛔) |
| `ngon_ngu` | `vi` / `en` / `ko` / `ja` / `zh` / `th` / `fr` / `de` / `es` / `it` / `pt` / `id` / `ru` | PHẢI trùng ngôn ngữ audio (⛔). Mọi chữ trên hình viết bằng tiếng này |
| `chu_ngon_ngu` | mã như trên | CHỈ khi người dùng yêu cầu chữ / sub khác tiếng giọng (vd `ko` cho giọng Việt): mọi chữ trên hình theo tiếng này, `ngon_ngu` vẫn là tiếng giọng. Tạo bằng `run.py sub-dich --work <dir> --ngon-ngu ko` |
| `sub_dich` | `[{tu, den, goc, chu}]` | sub DỊCH (cần khi `chu_ngon_ngu` khác giọng): `goc` = lời gốc (tham khảo), `chu` = bản dịch 1–2 dòng (ngắt " / "), ≤ ~14,6 em / dòng; cụm ≥ 0,6 s, không chồng nhau; gộp cụm gốc theo nghĩa được. `sub.karaoke_dich: false` → chữ vàng không chạy |
| `tieu_de` | chuỗi | ghi chú (tên bài) |
| `kenh` | `{ten, handle, avatar}` | CTA: tên kênh, @handle, đường dẫn ảnh avatar (null → chữ cái / ★). Trống → ⚠ hỏi ở cổng duyệt |
| `nhac` | `{file, muc_db, bat_dau?, khop_cuoi?}` / `null` / `false` | nhạc nền (file người dùng đưa — quet tự nhận trong Resources). `muc_db` −14 = nhạc dưới giọng (cả bài; to hơn: −12, nhỏ hơn: −16); `khop_cuoi` (mặc định true) lùi nhạc cho nốt kết trùng cuối video; `bat_dau` = giây bắt đầu trong nhạc (ghi đè lùi nhạc); `null` = không nhạc (Resources không có file nhạc — đúng luật, không nhắc), `false` = người dùng tắt nhạc dù có file |
| `sua_loi` | `{"sai": "đúng"}` | sửa chữ Whisper nghe sai (khớp chuỗi từ liên tiếp, không phân biệt hoa thường, giữ dấu câu). Chữ "đúng" tự được giữ liền trong sub |
| `bo_di_chuyen` | `[giây, …]` | câu bị tự dò nhầm là "di chuyển" (mục CÂU DI CHUYỂN trong `goi_y.txt`, ⚠ trong `kiem-kh`) nhưng không phải đi lại — ghi 1 giây bất kỳ trong câu để bỏ ⚠ |
| `sub` | `{bat, giu_lien}` | `bat: false` tắt sub; `giu_lien`: danh sách cụm chữ không được ngắt giữa |
| `sfx` | bool | `false` tắt mọi SFX |
| `sfx_cta` | bool | `false` tắt SFX ở CTA |
| `canh` | mảng | cảnh footage (bên dưới) |
| `do_hoa` | mảng | đồ hoạ chữ (bên dưới) |
| `cta` | đối tượng | CTA cuối (bên dưới) |

## canh — mỗi cụm lời 1 cảnh

Cảnh nối tiếp nhau: cảnh i chạy từ `tu` của nó tới `tu` cảnh sau (cảnh cuối tới hết video). Cảnh đầu `tu: 0`. Mỗi cảnh ≥ 1,2 s (⛔), > 9 s ⚠.

| Trường | Ý nghĩa |
|---|---|
| `id` | `c01`… |
| `tu` | giây bắt đầu (đặt ở đầu cụm lời, sớm hơn chữ đầu ~0,05–0,15 s) |
| `nguon` | `clip_NN` / `res_NN` (Resources) hoặc `bai_NN` (ảnh bài báo) — xem `tai_nguyen.jpg` |
| `vao_giay` | clip: giây bắt đầu lấy trong clip (soi `khung/clip_NN.jpg`); đoạn vượt cuối clip → ⛔ |
| `toc_do` | clip: 1 = thường, 0,5–0,9 = chậm (điện ảnh, kéo dài clip ngắn) |
| `khung` | `tran` (tràn màn, cắt 9:16) · `the` (ảnh thành thẻ bo góc trên nền nhoè của chính nó — cho ảnh nhỏ / ngang) |
| `the_y`, `the_rong` | thẻ: tâm y (mặc định 820) và bề rộng (bỏ trống = tự co: rộng ≤ 960, đáy ≤ 1295). Đáy thẻ > 1300 = ⛔ (sub 2 dòng cao tới y ≈ 1330, thẻ lắc ±20 px). Chữ đồ hoạ che ảnh thẻ quá 40 px → tự kiểm ⚠ |
| `cat_x`, `cat_y` | tràn màn: vị trí cắt 0–1 (0,5 = giữa) khi nguồn ngang / vuông |
| `lech_x` | ảnh tràn màn: lệch ngang −1…1 |
| `chuyen` | kiểu VÀO cảnh: `hoa_tan` · `nhoe` · `lia` · `lia_doc` · `zoom` · `loe` · `truot` · `cat`. Chuyển dài hơn 0,6 × cảnh → ⛔ |
| `chuyen_dong` | `zoom_vao` · `zoom_ra` · `lia_trai` · `lia_phai` · `lia_len` · `lia_xuong` · `dung` |

Clip dùng lại đoạn đã dùng → ⚠ (khán giả thấy lặp). Ảnh tràn màn phóng > 2,3× → ⚠ (vỡ) — dùng `khung: "the"`.

## do_hoa — đồ hoạ chữ

Chung: `id` (`d01`…), `loai`, `tu`, `den` (≥ 1,2 s ⛔; đồ hoạ lớn nên ≥ 2 s; mỗi mục đứng ≥ 1,6 s, ảnh ≥ 2 s — KỊP NHÌN, hiện sớm hơn lời 0,3–0,8 s được; `kiem-kh` / `dung` tự kéo `den` vào chỗ trống + cho mục / ảnh hiện sớm — dòng 🔧), `y` (tâm hoặc mép trên tuỳ loại). Hai đồ hoạ LỚN không chồng thời gian (⛔);
`ghim`, `chip` là đồ hoạ NHỎ, được chồng với 1 đồ hoạ lớn. Không đồ hoạ nào chồng CTA. Mục có `luc` (giây đọc chữ đó) phải nằm trong
`tu … den − 0,5` (⛔). Mọi chữ kiểm ngôn ngữ. Chọn loại theo KIỂU CÂU: bảng "Khuôn kể chuyện du lịch" trong `SKILL.md`.
Tiếng ja / zh / ko / th: `viet_tay` (và `kieu: "tay"`, `nhan` số lớn) hiện thành chữ Gothic đậm nhỏ nằm dưới tít — viết ngắn.

| `loai` | Trường | Hình | Dùng khi |
|---|---|---|---|
| `mo_dau` | `tren`, **`chinh`**, `viet_tay`, `duoi`, `y` (820), `co` (230) | dòng nhỏ giãn chữ có 2 gạch vàng → TÊN ĐIỂM ĐẾN serif cực lớn hiện từng chữ + bóng sáng quét → viết tay vàng vẽ dần → viên "📍 duoi" | lần đầu nói tên điểm đến |
| `tu_khoa` | **`muc`**[{`chu`, `luc`, `kieu`: `"tay"`?}], `y` (800) | các chữ serif nghiêng (hoặc viết tay) bật lên đúng lúc đọc, gạch vàng dưới | chuỗi tính từ / từ khoá ("cổ kính, hiện đại, sôi động") |
| `chuong` | `nhan`, `so`, **`ten`**, `phu`, `y` (360; chương có thẻ ảnh dùng ~190) | "ĐIỂM ĐẾN" + số viền vàng tô dần + TÊN IN HOA đẩy từ dưới lên + gạch vàng + dòng viết tay | mở mỗi địa điểm / mục lớn (đánh số 01, 02…) |
| `tieu_de` | `dan`, **`khoa`**, `viet_tay`, `mau` (`"trang"` = trắng thay vàng), `co` (132), `y` (760) | dòng dẫn giãn chữ + chữ khoá serif gradient vàng hiện từng chữ (dài thì tự ngắt 2 dòng cân) + viết tay | ý chính của 1 đoạn ("Thiên đường ẩm thực") |
| `ghim` | **`ten`**, `phu`, `y` (214) hoặc `vi_tri: "duoi"` | ghim tròn vàng rơi + vòng toả + nhãn kính tối trượt ra | gọi tên vị trí (thường chồng với thẻ ảnh / cảnh) |
| `chip` | **`muc`**[{`icon`, `chu`, `luc`}], `y` (mặc định đáy 1292) | viên kính tối icon vàng bật lần lượt | 2–3 đặc điểm ngắn nói liền nhau |
| `so_lon` | `tien_to`, **`so`**, `hau_to`, `nhan`, `dem_tu`, `dem_dai` (1,4), `y` (800) | số vàng cực lớn đếm lên (tách nghìn theo ngôn ngữ) + bật nhẹ + nhãn viết tay | con số ("hơn 1.000 năm") — số phải có trong lời / bài báo (không thấy → ⚠; "một nghìn", "a thousand" được) |
| `the_anh` | **`anh`** (`res_NN` / `bai_NN`), `chu_thich`, `x`, `y`, `goc` (−4) | ảnh polaroid băng dính rơi xoay vào, lắc nhẹ, bay ra phải | ảnh minh hoạ phụ trên nền cảnh |
| `liet_ke` | `dan`, `tieu`, **`muc`**[{`icon`, `chu`, `phu`, `luc`}], `y` (300) | bảng kính mờ: dòng dẫn + tít serif + từng dòng icon vàng trượt vào + tick | liệt kê 2–6 món / điểm |
| `trich` | **`noi`**, `nguon`, `y` (780) | ngoặc kép vàng lớn + câu nghiêng + nguồn | câu trích / cảm nhận |
| `hanh_trinh` | **`xuat_phat`** {`ten`, `phu`}, **`diem_den`** {`ten`, `phu`}, `phuong_tien` (`may_bay` · `o_to` · `xe_may` · `xe_buyt` · `xe_dap` · `tau_hoa` · `tau_thuy` · `di_bo` · `khong`), `nen` (**`that` = BẢN ĐỒ THẬT, mặc định khi 2 điểm có `toa_do`** · `troi` · `duong` · `bien` · `ban_do` · `canh`), `xuat_phat.toa_do` / `diem_den.toa_do` ([lat, lon] — `run.py tim "<tên>"`; BẮT BUỘC với `that`), `xuat_phat.anh` / `diem_den.anh` (res_XX / bai_XX gắn ghim, chỉ `that`), `diem_phu` ([{ten, toa_do}] tên nước / thành phố lúc nhìn toàn tuyến), `duong` (`o_to` · `di_bo` · `xe_dap` · `cung` · `cung_thap` · `thang`; mặc định theo phương tiện), `zoom_gan`, `canh_xa` (nền đường: `doi` · `thanh_pho` · `nui`), `thoi_gian` ("~4h30", "40–50 phút"), `nhan_tg` ("thời gian bay"), `khoang_cach` ("~27 km"), `dan` / `nhan_pt` (mặc định theo ngôn ngữ: "Hành trình" / "Máy bay"…), `luc_ten_di`, `luc_di`, `luc_kc`, `luc_ten_den`, `luc_den`, `luc_tg`, `ho_tai` (`di` / `den` / `khong`, tự đoán theo tên "Hồ…"), `y` (180) | `that`: ảnh vệ tinh thật + đường đi thật vẽ dần + máy bay / xe chạy theo tuyến + camera cận điểm đi → toàn tuyến → sà điểm đến, ghim + nhãn + ảnh gắn ghim, km trên tuyến, thẻ tuyến gọn ở trên. Nền khác: nền môi trường tự vẽ đầy khung (máy bay bay giữa biển mây / xe chạy trên đường / du thuyền / bản đồ phố vẽ đường đi) + thẻ tuyến kính tối: ● điểm đi — cung vàng vẽ dần + huy hiệu phương tiện chạy — 📍 điểm đến rơi + vòng toả; nhãn km trên đường; số thời gian vàng lớn + nhãn phương tiện. `canh` = chỉ thẻ, đè lên clip phương tiện trong Resources | lời nói DI CHUYỂN A → B (mất bao lâu / bao xa / bằng gì) — BẮT BUỘC (SKILL mục 13). Cần `thoi_gian` hoặc `khoang_cach`; số phải có trong lời ("rưỡi" = 30) ⚠; `tu ≤ luc_di < luc_den ≤ den − 0,4` ⛔; nên dài ≥ 3 s |

Icon hợp lệ (`ICON_HOP_LE` trong `ke_hoach.py`): ghim dong_ho lich_su sao may_anh bat_pho ca_phe chua ho thanh_pho la trang mat_troi ve
ban_do di_bo may_bay tich cong sach vuong_mien co di_tich cay tim binh_luan chia_se luu chuong nhac lap_lanh cau den_long xe_may nguoi
tau nui qua_tang ca cuon lua hoa gio · bien dao thac song_nuoc suoi_nong hang ruong leu khach_san nha lau_dai cho an_uong do_uong gia tien tuyet may mua nhiet_do o_to xe_dap tau_hoa cap_treo balo vali la_ban ong_nhom phao_hoa non_la. Icon mới: vẽ SVG vào `IC` trong `dulich.js` + thêm tên vào `ICON_HOP_LE`.

## cta

| Trường | Mặc định | Ý nghĩa |
|---|---|---|
| `tu` | — | giây CTA hiện (thường đầu câu kêu gọi cuối) |
| `them_giay` | 1,6 | giữ thêm sau tiếng cuối; video dài = max(hết lời + 0,9 + them_giay, lúc bấm tim + 1,3); CTA ≥ 3,8 s (⛔) |
| `tieu_de`, `viet_tay` | — | dòng serif + dòng viết tay vàng (đúng ngôn ngữ audio) |
| `nut`, `nut_da` | theo ngôn ngữ | chữ nút trước / sau khi bấm ("Theo dõi" / "Đã theo dõi") |
| `icon` | thich, binh_luan, chia_se, luu | hàng icon dưới nút |
| `nhan_icon` | theo ngôn ngữ | nhãn dưới từng icon |
| `luc_bam`, `luc_tim` | tu + 1,9 · luc_bam + 1,35 | giây tay bấm nút / bấm tim |
