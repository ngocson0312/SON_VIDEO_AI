# CẢNH 3D công trình trên ảnh vệ tinh — `mo_hinh_3d` + `canh_3d`

Cảnh 3D tái tạo đoạn 0–9 s và 25,5–29 s của video mẫu: camera bay vòng quanh **mô hình công trình** đặt đúng lô đất
trên **ảnh vệ tinh thật** (Esri World Imagery, cache chung `_cache_tiles\esri`). Các lớp đi kèm:
- chân trời mờ sương, tia nắng nhẹ;
- **vòng vàng** trên mặt đất, **thẻ logo vàng** nổi trên công trình;
- **chú thích bám công trình** (chấm trắng + gạch + chữ ExtraBold 2 dòng), **nhãn địa danh**;
- **chữ 2 tầng bên trong cảnh** (y 1290, đi theo thẻ khi thẻ nghiêng / phóng).

Dựng bằng Three.js r149 (`assets/khung/lib/three.min.js`) trong Chrome headless: `assets/khung/bds3d_3d.js` + `scripts/mo_hinh_3d.py` + `scripts/ve_tinh.py`.
Mỗi cảnh 3D được dựng thành chuỗi ảnh 30 fps rồi dùng **y như 1 clip footage**: thẻ nổi, tràn màn, nền nhoè, chữ ngoài, SFX đều giữ nguyên quy tắc của skill.

## Quy trình riêng cho video có cảnh 3D

1. `quet --audio <giọng> --res <thư mục ảnh phối cảnh> --3d --vi-tri "lat,lon"`. Không có toạ độ thì dùng `--dia-chi "<tên dự án / địa chỉ>"` (OSM, ghi ĐOÁN).
   Có video giọng thì vẫn dùng `--video …` kèm `--3d`.
2. Claude MỞ MỌI ảnh dự án (`tai_nguyen.jpg` + ảnh gốc), đếm và ghi ra:
   - số tháp, số tầng (đếm vạch sàn), tỉ lệ rộng / cao;
   - dải vườn treo ở tầng nào, chân cột, khối đế mấy tầng;
   - hồ bơi nằm đâu, màu kính, màu đế, kiểu mái.

   Sau đó viết `mo_hinh_3d`.
3. `xem-3d --work <dir>` → `mo_hinh_3d.jpg` (ảnh dự án + mô hình 6 góc). Claude MỞ, so từng điểm, sửa tham số tới khi giống (thường 2–3 vòng).
4. Viết `canh_3d` (camera, chú thích, chữ trong) theo NGHĨA lời. Cảnh nào chiếu 3D thì `"footage": {"nguon": "3d:<id>"}`.
5. Chạy `kiem-kh`. Nó tự đo trong Chrome và báo ⛔ khi:
   - chú thích, logo hoặc địa danh ra ngoài khung hay đè nhau;
   - chú thích sau lưng camera;
   - địa danh không lọt khung.

   Số trên cảnh 3D không có trong lời sẽ bị ⚠.
6. Chạy `duyet`: lần đầu dựng khung 3D (~13 khung/s, có cache).
7. Qua CỔNG DUYỆT (hỏi thêm **D6**, xem SKILL.md) thì chạy `dung`.

**Chỉ có ảnh, chưa có giọng:** `quet --res <ảnh> --3d --vi-tri …` (không `--audio`) → bước 2–3 → `bay-thu --work <dir>` (video câm 12 s
camera hạ từ cao rồi bay vòng; muốn camera riêng thì viết `canh_3d.bay_thu`). Giọng đến sau: `quet --audio … --3d --work <cùng work>`
giữ nguyên `mo_hinh_3d`.

**Dự án đang xây (tháp dở đã có trên ảnh vệ tinh):** đo từng tháp trên ảnh z19 có lưới mét (mái = phần sáng ở đầu Đông-Nam của
vệt bóng tối), đặt mô hình trùng tháp thật, `nang.goc` theo hướng bóng thật, phủ `san_vuon`.

## Toạ độ

Gốc là `vi_tri` (tâm lô đất). **x = Đông, z = Nam, y = cao**, đơn vị mét thật.

- `xoay` (độ, theo chiều kim đồng hồ nhìn từ trên) xoay cả công trình cho khớp hướng đường / ranh đất trên ảnh vệ tinh.
- `tim "<tên>"` trả toạ độ OSM.
- Nhà ĐANG XÂY thường chưa có trên OSM: lấy toạ độ từ link Google Maps người dùng đưa, chưa có thì `"chac": false` và hỏi ở cổng duyệt.
- Lô đất trên ảnh vệ tinh phải là đất trống hoặc công trường. Đặt mô hình đè lên toà nhà có sẵn trông rất giả, nên dời `x`/`z` hoặc hỏi người dùng.

## `mo_hinh_3d`

```json
"mo_hinh_3d": {
  "vi_tri": {"lat": 10.72381, "lon": 106.74209, "ten": "Đào Trí, Phú Thuận, Q7", "chac": true},
  "xoay": 12,
  "thap": [
    {"x": -28, "z": -10, "rong": 36, "sau": 32, "tang": 33, "cao_tang": 3.3, "chan": 0, "vuon": [11], "mai": "song", "mai_cao": 8, "buoc_cot": 3.6},
    {"x": 28,  "z": -10, "rong": 36, "sau": 32, "tang": 33, "vuon": [11], "mai": "song", "chan": 7}
  ],
  "de":   [{"x": -12, "z": 8, "rong": 68, "sau": 56, "tang": 4, "ho_boi": {"x": 14, "z": 8, "rong": 22, "sau": 18}, "cay": 10}],
  "khoi": [{"x": 60, "z": 40, "rong": 8, "sau": 16, "tang": 4, "kieu": "tuong", "mai": "ngoi"}],
  "khu":  {"rong": 120, "sau": 100, "toi": 0.3},
  "cay_quanh": 70,
  "mau":  {"kinh": "#f3f6fa", "kinh2": "#d5deea", "san": "#8d9bb0", "mai": "#6f7782", "de": "#232733", "de_lam": "#3a4050",
           "den": "#e0a253", "vien": "#d6b15c", "vien_de": "#d9d5cc", "ho": "#41c3d8", "tuong": "#ece8df"},
  "nang": {"goc": 32, "cao": 55}
}
```

### Tháp (`thap`)
- Mặc định là khối chữ nhật `rong` (theo x) × `sau` (theo z), cao `tang` × `cao_tang` (mặc định 3,3 m).
- Vạch sàn và mép ban công đậm, cột kính mỗi `buoc_cot` m.
- `vuon`: danh sách tầng bắt đầu **dải vườn treo** (cao 2 tầng): lõm vào, cây xanh, đèn ấm, 2 chỉ vàng.
- `chan`: chiều cao chân cột / sảnh (m). Sảnh kính tối được bao bởi hàng cột trắng.
- `mai`: `"song"` là vương miện lưới xám mép trên lượn sóng (như mẫu), `"phang"` là lưới thẳng. `mai_cao` mặc định 2,4 tầng.
- `xoay` riêng từng tháp được (ngoài `xoay` chung) — cụm tháp xoay khác hướng.
- **Hình chân tháp — `hinh`** (khách đưa kiểu gì cũng dựng được):

  | `hinh` | Khoá | Dùng cho |
  |---|---|---|
  | `chu_nhat` (mặc định) | `rong`, `sau` | tháp hộp, phiến chung cư |
  | `tron` | `rong`, `sau` (khác nhau = elip) | tháp trụ tròn / elip, landmark, khách sạn |
  | `bo_goc` | `rong`, `sau`, `bo` (bán kính góc, m) | tháp văn phòng bo góc, condotel |
  | `da_giac` | `diem` [[x, z], …] ≥ 3 điểm, toạ độ trong tháp (m) | chữ L, U, T, tam giác, cánh cung, mặt bằng lạ |

  Đọc mặt bằng từ ảnh phối cảnh / ảnh vệ tinh / mặt bằng tổng thể rồi vẽ `diem` theo mét. Đa giác vẫn có vườn treo, chân cột, vương miện như hộp.
- **Lùi tầng — `lui`**: `[{"tu": 24, "co": 0.85}, …]` từ tầng `tu` trở lên co đa giác còn `co` lần (0,3–1). Tháp bậc thang, tháp vát đỉnh.
- **Nâng nền — `cao_nen`** (m, cả `thap` lẫn `khoi`): đặt khối lơ lửng. Cầu nối trên cao giữa 2 tháp = `khoi` `kieu: "kinh"` có `cao_nen`.
- Tháp nhiều cánh dạng hộp thì ghép 2–3 tháp sát nhau. Phiến dài 2 cánh (như Lumi) = 2 tháp cách 2 m, lệch 1–2 m, chênh 2 tầng.
- `mau` riêng từng tháp: ghi đè bảng màu chung cho tháp đó (nhiều dự án có 2–3 kiểu mặt đứng). Thêm khoá:
  - `luoi`: màu **lưới khung mặt đứng** (lam đứng dày so le + khung ngang mỗi 4 tầng), dùng cho mặt "kính tối + khung trắng / đồng";
  - `luoi_den` (0–1): lưới khung **phát sáng** như đèn LED viền (ảnh phối cảnh đêm / hoàng hôn);
  - `tuong_hoi`: màu **tường hồi đặc** ở 2 mặt ngắn của tháp hộp (đầu hồi chung cư VN: vách trắng / đồng, giữa 1 cột cửa hẹp);
  - `den_cua` (0–1): tỉ lệ ô cửa **sáng đèn ấm**, `den_mau` màu đèn. Mặc định theo `buoi` (ngày 0, hoàng hôn 0,3, đêm 0,62) — ảnh phối cảnh thật thường chỉ 0,08–0,12;
  - `mai_den`: màu **vương miện phát sáng** (tầng mái lên đèn vàng);
  - `mep` (mép ban công), `phat` (ánh tự phát của kính, mặc định `#3a4656` hơi xanh — kính tối trung tính dùng `#4a4a4a`), `mai_tren` (màu mái bằng).
  - `mat: "can_ho"`: mặt **chung cư kính tối** như ảnh phối cảnh — mỗi bước cột 1 ô cửa có đố giữa, lan can mảnh, đèn ấm NHIỀU MỨC sáng
    (có ô kéo rèm sáng nửa dưới), `luoi_min` = lưới mảnh mỗi cột + mỗi tầng (khung đồng / trắng). Dùng với `buoc_cot` 2,2–2,6.
  - `den_dinh`: màu **tầng đỉnh sáng đèn** (dải vàng ấm ngay dưới viền mái), `den_dinh_tang` số tầng sáng (mặc định 1).
  - Màu `mau` chung của mô hình được MỌI tháp thừa hưởng: tháp không có lưới thì ghi `"luoi": null` kẻo dính lưới của bảng chung.
- **Khung viền module — `vien`** (tháp hộp): `{"rong": 2.4, "noi": 0.5, "dinh": 3.0, "giua": 1, "mau": "#9a5536", "phat": 0.04}`
  - 2 trụ góc đặc bọc kín đầu hồi + `giua` trụ chia mặt dài thành module + vành đỉnh cao `dinh` m → khối thành **"khung tranh"**
    đặc (đồng / trắng / xám) bọc mặt kính tối. Đây là thứ làm tháp chung cư hiện đại trông giống ảnh phối cảnh; thiếu nó tháp như hộp đồ chơi.
  - Module trong ảnh rộng ~15–20 m: cánh 35 m thì `giua: 1`. Đặt `mai_cao: 0` (vành `vien` thay vương miện lưới).
  - Bộ màu Lumi (bản 2, hoàng hôn) — trắng `{kinh #34373c, kinh2 #24272b, san #3d4045, luoi #f2f1ec, luoi_den .8, tuong_hoi #e8e7e2, mai_den #f3c46e, den_cua .09}`,
    đồng `{kinh #2f2622, san #3c2b23, luoi #c07a50, luoi_den .55, tuong_hoi #9c5b3c, den_cua .1}`. **`san` (dải sàn) để TỐI**: `san` sáng ở mọi tầng làm mặt đứng thành sọc / lưới gạch.
  - Trụ góc bọc kín đầu hồi nên mặt ngoài trụ mang texture tường hồi (`tuong_hoi` + dải cửa giữa từng tầng) hoặc ảnh `anh_hoi` — không còn mảng trơn.
- **MẶT ĐỨNG ẢNH THẬT — `anh_mat` / `anh_hoi`** (cách giống ảnh khách nhất; Lumi bản 5): cắt 1 mặt tháp trong ảnh phối cảnh, nắn phẳng
  (homography 4 góc) rồi dán trọn mặt dài (`anh_mat`) / đầu hồi (`anh_hoi`) của tháp → đúng kính, khung, đèn, vườn treo như render.
  1. Chọn ảnh **chụp trên cao, gần góc camera video nhất** (Lumi: ảnh hoàng hôn trên cao). Ảnh ngước từ dưới đất méo nặng, ít dùng được.
  2. `run.py luoi-anh --anh <ảnh> --vung x0,y0,x1,y1 --to 3 --work <dir>` → lưới toạ độ gốc, đọc 4 góc **mép trong khung viền**
     (đỉnh ngay dưới viền mái, đáy chân tháp / mép đế, không lấy cây che, không dính tường hồi hay nền trời).
  3. `run.py mat-anh --work <dir> --anh <ảnh> --goc "TL TR BR BL" --id dong_a [--tang 33] [--rong 160] [--sang 1.0] [--giu-goc]`
     → `mat_anh/<id>.jpg` + `<id>_xem.jpg` (ảnh gốc + phóng vùng cắt + texture kẻ vạch đỏ). Cắt 2–3 mặt mỗi kiểu, xen kẽ
     giữa các tháp kẻo cả khu giống hệt nhau.
     - **Tự nắn thẳng (mặc định)**: ảnh chụp trên cao thì cạnh đứng tháp chụm dần xuống dưới, mỗi cạnh 1 mức; chấm góc bằng mắt lệch
       vài px là mặt nắn ra XIÊN 3–5° (lam / ban công chéo hẳn khi dán lên tháp). Lệnh dò vạch cửa / cột (đứng) và vạch sàn (ngang),
       dời 2 góc dưới theo x + 2 góc phải theo y tới khi chúng thẳng, in "xiên +4,6° → −0,2°" (vàng = vùng dùng, xanh = góc chấm).
       Còn xiên > 1° thì báo ⚠ → chấm lại. Mặt hẹp < 45 px (tường hồi trơn) KHÔNG tự nắn — ít vạch, bộ dò trượt sang mặt bên.
     - Claude MỞ `<id>_xem.jpg` soi: vạch cửa / lam song song vạch đỏ, mép trái / phải đúng khung, không lẹm trời / mái / cây.
  4. Tháp: `"anh_mat": "dong_a"`, tuỳ chọn `"anh_hoi": "hoi_dong"`, `anh_phat` (ánh tự phát của ảnh, mặc định 0,6), `anh_sang` (phần
     nhận nắng, 0,4). Ảnh đã có ánh sáng sẵn → chọn `buoi` / `troi` khớp ảnh đó (ảnh hoàng hôn ⇒ `hoang_hon`).
  - Chỉ cho tháp `chu_nhat` không `lui` (`kiem-kh` chặn kiểu khác). Có `anh_mat` thì engine bỏ `vuon`, `den_dinh`, trụ `giua` của `vien`
    (ảnh đã có sẵn) — vẫn giữ trụ góc + vành đỉnh `vien` làm khung, nên `mau.tuong_hoi` / `vien.mau` lấy đúng màu khung trong ảnh.
  - **Mặt cắt hẹp hơn 60 px trong ảnh gốc** (lệnh báo ⚠) phóng ra sẽ nhoè thành vệt: tường hồi SÁNG (trắng / kem) thì vệt xám trông
    như vết bẩn ⇒ bỏ `anh_hoi`, để texture tường hồi; tường màu đậm (đồng) thì vẫn dùng được.

### Khối đế (`de`)
- Mặt than / nâu có lam đứng, cửa sáng ấm, chỉ vàng, mép đỉnh `vien_de`.
- Mái sân thượng xám nhạt.
- `ho_boi` đặt trên mái, toạ độ tính tương đối theo tâm đế; không được tràn khỏi mặt đế.
- `cay`: số cây cọ trên mép mái.

### Khối tự do (`khoi`)
- Dùng cho nhà phố, biệt thự, shophouse, khối thấp.
- `kieu`: `kinh` | `de` | `tuong` (tường kem, cửa sổ).
- `mai`: `"ngoi"` cho mái dốc ngói đỏ (`mau_ngoi`), bỏ trống cho mái bằng.
- Dãy nhà phố thì liệt kê nhiều khối sát nhau, so le màu (`mau_mai`).

### Khung cảnh
- `khu`: ranh lô đất (m). Nền lô hơi sẫm (`toi`, 0 = tắt), cây quanh ranh (`cay_quanh` cây tán tròn + bóng mềm, 0 = tắt).
- `san_vuon`: `[{"diem": [[x, z], …], "cay": 300, "mau": "#ffffff", "dam": 0.94}]` — đa giác **cỏ + cây** phủ lên ảnh vệ tinh
  (che công trường / đất trống thành cảnh đã hoàn thiện như ảnh phối cảnh). Toạ độ CẢNH: gốc `vi_tri`, x Đông, z Nam, **không xoay**
  theo `xoay`. Lấy theo ranh OSM của dự án (co vào 6–8 m để lộ đường nội bộ). Cây tự né chân tháp / đế / khối.
- `mat_dat`: tiện ích **trên mặt đất trong khu**, toạ độ MÔ HÌNH (như tháp, xoay theo `xoay`); cây sân vườn tự né:
  ```json
  "mat_dat": [
    {"loai": "ho", "x": 70, "z": 40, "rong": 30, "sau": 14, "xoay": 20, "ve": 2.5},
    {"loai": "san_tt", "kieu": "tennis", "x": 85, "z": 75, "xoay": 90},
    {"loai": "san", "diem": [[-30, 55], [20, 55], [20, 70], [-30, 70]]},
    {"loai": "duong", "diem": [[-90, 85], [-20, 80], [40, 95]], "rong": 3},
    {"loai": "cau_tren_cao", "diem": [[-90, 20], [-80, 70], [-30, 95]], "rong": 3.2, "cao": 8}
  ]
  ```
  - `ho`: hồ bơi / hồ cảnh quan, chữ nhật (`rong`, `sau`, `xoay`) hoặc `diem` (hồ tự do), `ve` = viền sàn đá.
  - `san_tt`: sân thể thao `kieu` `tennis` | `bong_ro` | `pickleball` | `bong_da`, kích thước chuẩn tự lấy (ghi `rong` / `sau` để đổi).
  - `san`: quảng trường / sân lát (`diem` hoặc chữ nhật). `duong`: đường dạo nội khu theo đường gấp khúc.
  - `cau_tren_cao`: đường dạo trên tán cây / cầu đi bộ: mặt cầu + lan can + cột mỗi 9 m, cao `cao` m.
  - Ảnh vệ tinh còn là công trường thì vị trí tiện ích là ĐOÁN: đặt vào khoảng trống giữa tháp, ghi vào `doan`.
- `buoi`: `ngay` (mặc định, khớp ảnh vệ tinh) | `hoang_hon` (trời cam, nắng thấp ấm, cửa sổ sáng) | `chang_vang` (giờ xanh: trời xanh thẫm, đất vệ tinh nhuộm xanh tối, kính tối phản chiếu trời + phố lên đèn, viền LED / đèn ấm toả sáng — kiểu ảnh phối cảnh chung cư hay dùng nhất) | `dem` (trời xanh đêm). Chọn theo ảnh phối cảnh chính của khách: ảnh trời xanh thẫm có viền đèn ⇒ `chang_vang`, đừng lấy `hoang_hon` (trời cam lệch hẳn ảnh).
- **Hậu kỳ + khử nhấp nháy (tự bật)**: cảnh vẽ ×`ssaa` (mặc định 2) rồi 1 lượt hậu kỳ: nhoè theo độ sâu (xa / chân trời mờ sương như ống kính thật — chính dải ảnh vệ tinh xa này hay LẤP LÁNH khi camera hạ thấp), mờ gần rất nhẹ, toả sáng (bloom) cho đèn cửa / viền LED / vương miện. Chỉnh bằng `"hau_ky": {"mo_xa": 4.5, "mo_gan": 1.2, "bloom": 0.6, "nguong": 0.6}` (px khung 1080; `false` = tắt). **Đừng tăng `mo_gan`**: mờ gần mạnh = tilt-shift → công trình trông như mô hình đồ chơi.
- Kính tự **phản chiếu** môi trường theo buổi (trời + dải phố xa, lấm tấm đèn khi chiều tối) qua mặt nạ ô kính; khung / tường / ô đang sáng đèn không phản chiếu. Mức: `mau.phan_chieu` (mặc định 0,38; chạng vạng 0,55; 0 = tắt). Chân tường tự tối dần 26 m dưới cùng (giả AO) — khối nhà đứng trên đất, không dán lên ảnh.
- `nang`: hướng nắng, dùng cùng quy ước `goc` như camera (0 = từ phía Nam). **VN: nắng phía Nam** nên ban ngày giữ 20–60. Đặt nắng phía Bắc thì mặt nhìn vào camera tối xám.
  Hoàng hôn: nắng từ Tây (`goc` −70, `cao` 20–26); `cao` thấp hơn thì bóng tháp phủ kín cả khu.
- Tuỳ chọn thêm `troi` {dinh, giua, chan} (màu trời / sương chân trời), `loc` (CSS filter cả cảnh), `mau_dat`.

### Đọc ảnh phối cảnh ra tham số

| Nhìn thấy trong ảnh | Ghi |
|---|---|
| đếm vạch sàn từ đỉnh đế tới chân vương miện | `tang` (tháp mẫu ~33) |
| bề ngang mặt chính ÷ chiều cao thân | `rong` ≈ cao × tỉ lệ (cao = tang × 3,3) |
| dải tối có đèn vàng, cây giữa thân | `vuon` = tầng của dải đó |
| cột trắng hở chân | `chan` 6–8 m |
| khối thấp sẫm ôm chân tháp | `de` (tầng ≈ cao ÷ 4,5 m) |
| mặt nước xanh trên mái đế | `ho_boi` |
| kính trắng xanh / xanh lam / ánh vàng | `mau.kinh`, `kinh2`, `san` |
| tháp trụ tròn / elip | `hinh: "tron"` |
| góc tháp bo tròn | `hinh: "bo_goc"`, `bo` ≈ ⅕ cạnh ngắn |
| mặt bằng chữ L / U / tam giác / lượn | `hinh: "da_giac"` + `diem` |
| đỉnh tháp thu nhỏ dần thành bậc | `lui` mỗi bậc `co` 0,8–0,9 |
| cầu kính nối 2 tháp trên cao | `khoi` `kieu: "kinh"` + `cao_nen` |
| biệt thự / nhà phố mái ngói | `khoi` `kieu: "tuong"`, `mai: "ngoi"`, so le `mau_ngoi` |
| đầu hồi đặc trắng / màu, mặt dài kính | `mau.tuong_hoi` |
| khung viền sáng đèn ban đêm | `mau.luoi` + `luoi_den` |
| ảnh chụp lúc hoàng hôn / đêm | `buoi` + `den_cua` 0,08–0,12 + `mai_den` |
| trời xanh thẫm, mặt tối, viền LED trắng sáng, dải vườn treo đèn ấm | `buoi: "chang_vang"`, `luoi_den` 0,9–1, `den_cua` 0,12–0,16 |
| hồ bơi / sân tennis / đường dạo / cầu trên tán cây ở mặt đất | `mat_dat` |
| công viên, thảm cỏ phủ cả khu | `san_vuon` theo ranh OSM |
| khối có khung viền đặc bao quanh mặt kính, trụ chia mặt thành dải mảnh | `vien` (+ `giua`) |
| mặt kính tối nhiều ô cửa nhỏ sáng vàng | `mat: "can_ho"`, `buoc_cot` 2,3, `den_cua` 0,25–0,32 |
| tầng trên cùng sáng vàng dưới viền mái | `mau.den_dinh` |
| ảnh chụp trên cao thấy rõ mặt dài tháp hộp (cách giống thật nhất) | `anh_mat` (+ `anh_hoi`) — `luoi-anh` → `mat-anh` |

**So đúng góc ảnh — `goc_anh`**: `"goc_anh": [{"anh": 1, "goc": 20, "nghieng": 30, "xa": 640, "fov": 38, "nhin": [0, 45, 0]}]`
— Claude ước camera của từng ảnh phối cảnh (`anh` = số thứ tự ảnh trong `mo_hinh_3d.jpg`), `xem-3d` dựng thêm mô hình ĐÚNG góc đó và đặt
cặp "ẢNH k – MÔ HÌNH cùng góc" cạnh nhau ở cuối tờ. So mặt đứng / màu / tỉ lệ trên cặp này (so lệch góc thì không thấy sai). Ảnh chụp
ngước từ dưới đất (camera nhìn lên) không dựng được góc đó — bỏ qua, so mặt đứng bằng mắt.

## `canh_3d` — mỗi lượt bay là 1 khoá

```json
"canh_3d": {
  "bay1": {
    "cam": [
      {"luc": 0,   "nhin": [0, 20, 0], "goc": 30, "nghieng": 62, "xa": 1150, "fov": 55},
      {"luc": 3,   "nhin": [0, 35, 0], "goc": 14, "nghieng": 44, "xa": 760,  "fov": 55},
      {"luc": 6.2, "nhin": [0, 58, 0], "goc": -8, "nghieng": 24, "xa": 390,  "fov": 55}
    ],
    "vong": [{"tu": 0.3, "den": 5.6, "r": 150}],
    "logo": {"tu": 0.6, "den": 4.6, "chu": "Tên dự án", "phu": "Phường · Quận", "file": "D:/…/logo.png", "diem": [0, 140, 0]},
    "chu_thich": [{"tu": 4.9, "den": 9.6, "diem": "thap1@0.72", "chu": "35 tầng", "phu": "2 tòa tháp", "ben": "trai"}],
    "dia_danh": [{"tu": 10.2, "den": 13.4, "chu": "Sông Sài Gòn", "lat": 10.7236, "lon": 106.749}],
    "tia": [{"tu": 7.6, "den": 13.4}],
    "chu": [{"tu": 6.3, "den": 9.4, "dong": [[{"t": "chỉ vỏn vẹn", "k": "dan", "luc": 6.3}], [{"t": "602 căn hộ", "k": "vang", "luc": 6.8}]]}]
  }
}
```

### Camera (`cam`)
- `luc` là **giây tuyệt đối** của video, khoá cách nhau ≥ 0,6 s (nên 2,5–4 s).
- Nội suy Hermite đơn điệu: êm, không vọt quá khoá. 2 khoá giống nhau thì camera đứng.
- `nhin`: điểm nhìn [x, y, z].
- `goc`: hướng camera (0 = đứng phía Nam nhìn lên Bắc, 90 = đứng phía Đông). Được vượt 360 hoặc âm để bay tiếp một chiều.
- `nghieng`: 90 là nhìn thẳng xuống, 15 là gần ngang.
- `xa`: khoảng cách (m). `fov` mặc định 55.
- Ngôn ngữ camera của mẫu:
  - hook: thẻ nổi, nhìn chéo cao 55–65°, xa 1000–1300 m, công trình nhỏ, có vòng + logo;
  - hạ dần về 40–45°;
  - khoe (tràn màn): 20–26°, xa ~1,6 × chiều cao tháp + 200 m, tháp chiếm ~35–40 % chiều cao khung, chân trời ở ~15 % từ trên;
  - lượt xa: 13–16°, thấy sông / thành phố;
  - kết quả: vòng gần quanh mặt có hồ bơi, 18–23°.

  Lúc nào camera cũng phải đang bay (đổi `goc` 15–40° mỗi 3 s).

### Các lớp trên cảnh
- `diem` của chú thích / logo:
  - [x, y, z] toạ độ mô hình;
  - hoặc chuỗi `"thap1@0.72"` (tâm tháp 1 ở 72 % chiều cao), `"de1"` (mái đế 1), `"khoi2@0.5"`.
- `chu_thich`:
  - `ben` `trai` / `phai`: chữ nằm phía nào của chấm. Chọn phía có trời / đất trống, không đè tháp kia.
  - `chu` ExtraBold 46 px, `phu` 27 px. `dai` = dài gạch (mặc định 118 px).
- `vong`: tâm `x`, `z`, bán kính `r` (m), mặc định 1,5 × nửa khu đất.
- `logo`: thẻ vàng kính + mũi nhọn, hiện ở hook. Có `file` (logo người dùng đưa) thì hiện ảnh, không thì hiện chữ `chu` / `phu`.
- `dia_danh`: nhãn kính tối chữ IN HOA tại lat/lon thật (hoặc `diem`). Camera phải quay về phía đó, kiem-kh báo ⛔ nếu lọt khung.
- `tia`: tia nắng mờ từ trên, cho lượt xa / kết quả (chỉ hợp buổi `ngay` / `hoang_hon`).
- `duong_vien`: **đường line sáng CHẠY quanh khu** như mẫu (viền vàng bám mép khu / đế): `[{"tu": 1.4, "den": 9, "diem": "ranh", "ve": 2.6}]`.
  - `diem`: `"ranh"` (= `mo_hinh_3d.ranh` [[x,z],…] nếu có, không thì `san_vuon` 1), `"san_vuon2"`, `"mat_dat3"` (tuyến / đa giác mặt đất, tự xoay về cảnh), hoặc `[[x, z], …]` toạ độ CẢNH (x Đông, z Nam).
  - Vẽ dần hết vòng trong `ve` giây (đầu sáng trắng), sau đó xung sáng chạy dọc mãi (`chay: false` = đứng yên, `buoc` m giữa 2 xung). `rong` lõi (m, mặc định 3,2) + quầng; `cao` nổi trên đất (0,7); `mau` (#ffd54a); `kin: false` = tuyến hở (đường, sông).
  - `bay-thu` tự thêm vòng vàng + line quanh `ranh` khi mô hình có ranh / sân vườn.
- `chu`: chữ 2 tầng BÊN TRONG cảnh 3D, cùng schema `chu` của skill, mặc định `vi_tri` 1290.
  - Dùng cho thông tin dự án ("trên quỹ đất / 10.000 m²").
  - Chữ ngoài (`chu` gốc, y 148) vẫn là tóm tắt lời đọc.
  - 2 lớp chữ không được kể cùng 1 câu.
- SFX tự thêm: vòng (swoosh nhẹ), chú thích (pop-2), địa danh (pop-2 nhỏ), logo (sparkle). Chỉ tính phần nằm trong đoạn cảnh được dùng.

### Dùng trong `canh`

```json
{"id": "hook", "loai": "the_noi",  "tu": 0,   "den": 6.2,  "footage": {"nguon": "3d:bay1"}},
{"id": "khoe", "loai": "tran_man", "tu": 6.2, "den": 9.55},
{"id": "tom_tat", "loai": "nen_nhoe", "tu": 9.55, "den": 13.0},
{"id": "ket_qua", "loai": "tran_man", "tu": 25.5, "den": 28.9, "footage": {"nguon": "3d:bay2"}}
```

- Cảnh tiếp theo không ghi `footage` thì dùng tiếp cùng lượt bay: thẻ phóng ra tràn màn, camera vẫn bay liền mạch.
- Hai cảnh dùng 2 lượt bay khác nhau thì có hoà tan.
- Khung 3D được dựng cho [tu − 0,1 s, den + 0,45 s] của đoạn dùng, nên camera phải có khoá phủ hết đoạn đó.

## Không bịa

- Số tầng, số tháp, kích thước lấy từ ảnh là **ƯỚC LƯỢNG**: ghi vào `doan` và hỏi ở D6.
- Số in lên cảnh (chú thích, logo, chữ trong) phải có trong lời hoặc do người dùng đưa (kiem-kh báo ⚠).
- Tên dự án và logo chỉ lấy từ người dùng.
- Mô hình là **minh hoạ tham số**, không phải dựng lại 3D chính xác từ ảnh. Nói rõ với người dùng nếu họ hỏi.
