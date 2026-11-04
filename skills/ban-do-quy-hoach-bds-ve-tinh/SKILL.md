---
name: ban-do-quy-hoach-bds-ve-tinh
description: "Dựng VIDEO BẢN ĐỒ VỆ TINH tin quy hoạch / bất động sản dọc 9:16 CHỈ TỪ 1 FILE AUDIO giọng đọc (m4a/mp3/wav), theo phong cách video mẫu ho_dan.mp4 (kênh MINH ĐOÀN — mở rộng sông Đáy) nhưng nền là BẢN ĐỒ VỆ TINH DỰNG BẰNG CODE (Esri World Imagery + hình học thật OpenStreetMap, không quay màn hình): bay dọc sông/đường với HÀNH LANG ±N m vàng, BẢN ĐỒ TỔNG nền tối vẽ từng đoạn A→B vàng chạy + nhãn 2 đầu + thẻ đầu đề navy đổi theo đoạn, TÔ RANH xã/huyện (cả ranh huyện cũ trước sáp nhập 2025) hiện đúng lúc đọc tên, GHIM công trình, THƯỚC ĐO bề rộng, ĐIỂM NHẤN ĐA DẠNG (gợn sóng, ghim rơi, chú thích kéo dây, huy hiệu số, vùng ngắm, vạch chảy dọc sông, viền vùng tự vẽ nhiều màu, bản đồ định vị nhỏ) + TÊN ĐỊA DANH THẬT quanh camera (làng/xã/thị trấn OSM, tự né chữ), thẻ hook navy đầu video, THẺ TÀI LIỆU chỉ khi tài liệu XÁC MINH 100 % (Resources trước, không có thì tự tìm web + kiểm số trên trang; không khớp = không thẻ), SUB KARAOKE NGUYÊN VĂN (Montserrat chữ thường trắng viền navy, chữ đang đọc vàng phồng nhẹ, y 1545), số liệu trên hình bị chặn nếu không có trong lời, CTA cuối có NÚT đỏ + chuông + tay bấm + icon (không SFX), SFX 1 chỗ, −14 LUFS, mã hoá 1 lần, tự kiểm trên file cuối. Whisper nhận lời → Claude viết ke_hoach.json (cảnh theo nghĩa lời) → tự tìm toạ độ/ranh → DỪNG 1 lần ở cổng duyệt → dựng → tự kiểm. Trigger '/ban-do-quy-hoach-bds-ve-tinh', 'làm video bản đồ quy hoạch từ audio này', 'video bản đồ vệ tinh BĐS', 'video kiểu Minh Đoàn sông Đáy', 'audio tin quy hoạch ra video bản đồ', 'template NNS bản đồ quy hoạch'."
---

# ban-do-quy-hoach-bds-ve-tinh — audio tin quy hoạch / BĐS → video bản đồ vệ tinh

> Chủ dự án 04/11/2026 (video mẫu `F:\VIDA_TEST\0411\Ho_dan\ho_dan.mp4`, kênh MINH ĐOÀN): *"chỉ cần đưa vào file audio nói
> thôi là có thể tạo ra đầy đủ được video. Lưu ý là vị trí được nói đến trên video phải đúng với map hiển thị ra"* →
> *"làm bằng bản đồ vệ tinh luôn nhé, sub phải sub nguyên bản … sub karaoke nhé, thẻ tài liệu kia bạn tự đi tìm và tự tải …
> văn bản là phải chính xác 100 %, nếu k tìm đc hoặc k tìm đúng thì video k được đưa gì lên, k được kiểu trí trá nhé"* →
> *"user gửi vào file audio k phải nói về giống video kia nữa mà nói kiểu khác nhưng cũng theo phong cách giống video kia"*.
>
> Phân tích đầy đủ video mẫu (bố cục, số đo, màu, nhịp): `references/phan-tich-mau-ho-dan.md`. Quyết định gốc:
> `references/spec-v1.md`. Kế hoạch mẫu đã dựng thật: `references/vi-du-ho-dan.json` (audio thử
> `F:\VIDA_TEST\0411\Ho_dan\ho_dan_audio.mp3`, 72 s, 12 cảnh). Skill này sau sẽ làm template trên tool NNS.
>
> **VIDEO CHUẨN ĐÃ CHỐT (04/11/2026, chủ dự án: "oki rồi đó"):** `F:\VIDA_TEST\0411\Ho_dan\ho_dan_audio_BDQH_ban5.mp4`
> — dựng từ đúng `references/vi-du-ho-dan.json`. Mọi audio mới làm ĐÚNG phong cách này (C1–C11), không hỏi lại kiểu;
> chỉ đổi khi người dùng góp ý.

## ĐÃ CHỐT — không hỏi lại

| # | Quyết định |
|---|---|
| C1 | **Nền = bản đồ vệ tinh dựng bằng code** (ô ảnh Esri World Imagery, cache đĩa) — KHÔNG quay màn hình. Sông/đường/ranh lấy hình học THẬT từ OpenStreetMap. Dòng nguồn bắt buộc ở y 1830: "Ảnh: Esri World Imagery · Dữ liệu: © OpenStreetMap". |
| C2 | **Sub nguyên văn karaoke**: cả cụm hiện trắng viền navy + bóng (Montserrat ExtraBold 56, chữ thường có dấu), chữ đang đọc vàng `#FFD24D` phồng 6 %, ≤ 2 dòng, rộng ≤ 960 px, chân dòng cuối y 1545. Gom cụm bằng bộ nns-auto-sub (`sub/scripts/build_ass.py`), cặp từ không tách: `assets/cap_tu_quy_hoach.txt`. KHÔNG dùng thẻ ý tóm tắt như mẫu. Ẩn lúc CTA. |
| C3 | **Mọi thứ bám audio**: lời không nhắc → không đồ hoạ; nhắc địa danh → bản đồ đúng chỗ; nhắc số liệu → chữ trên hình chỉ được dùng ĐÚNG số trong lời (`run.py kiem-kh` chặn mọi số không có trong lời). |
| C4 | **Thẻ tài liệu**: Resources của người dùng trước; không có → tự tìm web → `tai_lieu.py xac-minh` phải ĐẠT (mọi số + tên có trên trang tại lúc dựng) → mới làm thẻ. Không tìm được / không khớp ⇒ **KHÔNG thẻ, không ảnh thay thế, không ảnh "gần giống"**. Snippet máy tìm kiếm không phải bằng chứng. |
| C5 | Ảnh người thật chỉ khi người dùng đưa vào Resources hoặc duyệt ở cổng. AI không tự chèn mặt người. |
| C6 | Tiếng: chỉ giọng + SFX **1 chỗ** (ding khi vào bản đồ tổng), −14 LUFS / −1 dBTP. **CTA KHÔNG có SFX** (04/11 bản 3: chime cuối "nghe chói quá bỏ đi"). Thêm tiếng khác chỉ khi người dùng đòi (`cai_dat.sfx_them: true`). Không nhạc nền (trừ khi đòi). |
| C7 | DỪNG đúng 1 lần ở cổng duyệt (sau `duyet`), rồi dựng + tự kiểm + giao. |
| C8 | Phong cách đồ hoạ cố định (đo từ mẫu): navy `#0F2C52` viền `#3E6296`, vàng `#FFD24D`, sông xanh lơ `#4FC3F7`; thẻ hook x 60–1020 y 202; thẻ đầu đề y 56; thẻ tài liệu x 112–968 y 300; logo góc phải trên; CTA vào cắt cứng (C11); hoà tan 0,25 s giữa các cảnh; video kéo 0,9 s sau tiếng cuối; 1080×1920 30 fps, x264 bt709 mã hoá 1 lần. |
| C9 | Địa danh hành chính: lời đọc dùng tên CŨ (huyện trước 1/7/2025) ⇒ tô **ranh huyện cũ** (`boundary=historic`, `cap: "huyen_cu"`), thẻ phụ ghi "Ranh giới huyện cũ (trước sáp nhập)". Lời dùng tên MỚI ⇒ ranh mới (`admin_level` 4/6). Không trộn. |
| C10 | **Điểm nhấn rõ + đa dạng + có TÊN ĐỊA DANH** (04/11 bản 3: "highlight rõ các địa điểm, trên bản đồ vẫn hơi thô, chưa hl đa dạng, và có tên địa danh"). Tự bật theo loại cảnh (`diem_nhan.py`): **bay_tuyen** = tên sông/đường gắn vào tuyến (pill chấm xanh) + vạch trắng chạy dọc tim tuyến + nhãn điểm xuất phát có gợn sóng + **tên làng/xã/thị trấn THẬT** quanh camera + **bản đồ định vị nhỏ** góc dưới trái (tuyến > 8 km); **ban_do_tong** = mỗi đoạn 1 màu (vàng → cam → ngọc → xanh → hồng), gợn sóng đầu đoạn, ghim rơi + sóng cuối đoạn, vạch chạy trên đoạn vừa vẽ, **huy hiệu số** (pill vàng mũi nhọn) ở giữa đoạn đúng giây đọc số, tên thị trấn/phường; **to_vung** = mỗi vùng 1 màu, viền tự vẽ quanh ranh 0,7 s rồi phủ màu, gợn sóng ở tâm, pill chấm màu bật; **diem** = vùng ngắm (tối ngoài + vòng nét đứt xoay) + ghim rơi nảy + gợn sóng + chú thích kéo dây. Tên địa danh phụ chỉ lấy từ OSM (Photon reverse, `place` = city/town/suburb/village/hamlet…, tên có chữ số bị bỏ), đặt đúng toạ độ, tự né thẻ đầu đề / hook / logo / dải sub / bản đồ định vị / nhãn chính; KHÔNG bịa tên, không có dữ liệu thì không nhãn. Thêm tay: `nhan_manh` (dưới). |
| C11 | **CTA có NÚT + ICON** (04/11 bản 3: "cta nên có button, icon thay vì text đơn giản"), `cta.py`: nền = khung cuối cảnh trước làm mờ + tối; thẻ navy viền vàng; avatar tròn (logo kênh, chưa có ⇒ icon ghim bản đồ nền vàng) + vòng sóng; tên kênh (CHỈ khi có `kenh.ten`); dòng "THEO DÕI KÊNH" + dòng phụ lấy từ lời CTA; 3 chip icon (ghim · tài liệu · chuông: Bản đồ / Quy hoạch / Tin mới); nút đỏ có chuông rung "THEO DÕI" → tay trỏ trượt vào bấm (nút lún + sóng trắng) → nút xám "✓ ĐÃ THEO DÕI" → tay rút. Không SFX. Kênh có clip/ảnh CTA riêng (`kenh.cta`) thì dùng clip đó. |

## Cần gì

- **Bắt buộc:** 1 file audio giọng đọc.
- Tuỳ chọn: thư mục Resources (ảnh/PDF công văn, bảng số liệu, sơ đồ quy hoạch, logo kênh, clip CTA), `kenh.json`
  `{"ten": "MINH ĐOÀN", "logo": "logo.png", "cta": "cta.mp4"}`.
- Máy: Python 3.10+ (`requirements.txt`), ffmpeg full trong PATH, mạng (Photon, OSM API, ô Esri — lệnh `dia-diem`,
  `duyet`, `dung` chạy NGOÀI sandbox). Lần đầu Whisper large-v3 tải ~3 GB, chạy CPU (~2 phút cho 70 s audio).

## Cách Claude chạy (trả lời tiếng Việt có dấu)

Mọi lệnh: `python -I -X utf8 .claude/skills/ban-do-quy-hoach-bds-ve-tinh/scripts/run.py <lệnh> …`

1. **`quet --audio <file> [--res <thư mục>] [--kenh kenh.json]`** → thư mục work `<audio>_bdqh_work/`: `loi_doc.txt`
   (câu + chữ@giây), `so_lieu.txt` (mọi số nghe được), `tai_nguyen.jpg` (ảnh Resources), khung `ke_hoach.json`.
2. **Claude đọc hết `loi_doc.txt`, `so_lieu.txt`, MỞ `tai_nguyen.jpg`** rồi điền `ke_hoach.json` (mẫu
   `references/vi-du-ho-dan.json`):
   - `hook` (0 → hết câu 1): 3 dòng lấy từ lời câu đầu (+ câu nói về hồ sơ/nguồn nếu có).
   - `dia_diem`: mọi địa danh lời nhắc. Tìm bằng `run.py tim "<tên>" --gan lat,lon` → ghi `osm` (R…/W…/N…) đã chọn;
     ranh huyện cũ thêm `cap: "huyen_cu"`. Điểm suy ra (không bịa toạ độ):
     `{"dau_tuyen": "song_x"}`, `{"cuoi_tuyen": …}`,
     `{"giao": {"tuyen": "song_x", "duong": "Đại lộ Thăng Long", "quanh": [lat, lon]}}` (chỗ đường cắt sông, OSM API /map),
     `{"giao": {"tuyen": "song_x", "ra_khoi": "ha_noi", "sau": "ba_tha"}}` (chỗ sông ra khỏi địa phận).
   - `canh`: phủ kín 0 → hết, mỗi cụm ý 1 cảnh ≥ 3 s, đổi cảnh ở khoảng lặng giữa câu (xem bảng loại cảnh dưới).
   - **Điểm nhấn (C10)** — phần lớn tự bật, Claude chỉ điền: mỗi `bay_tuyen` có `nhan` = tên điểm xuất phát
     (`[{"diem": "<tu_diem>", "text": "<tên>"}]`); mỗi đoạn `ban_do_tong` lời có đọc số ⇒ `huy_hieu` = đúng số + đơn vị
     trong lời ("12 km", "1.217 hộ", "≈ 110 km") và `huy_hieu_tu` = giây đọc số đó; `diem` muốn dòng phụ thì `phu_nhan`
     (chỉ chữ có trong lời) và `dinh_vi: "<key tuyến>"`; `cai_dat.dinh_vi_doan` = khúc tuyến lời nói tới (vd
     `["dau_song", "ra_hn"]`). Chỗ lời nhắc 1 điểm mà cảnh không tự có ⇒ `nhan_manh` (≤ 2–3/cảnh). Không tự viết tên
     làng/xã — tên phụ do script lấy từ OSM.
   - **CTA (C11)**: `{"loai": "cta", "dong": ["Theo dõi kênh", "<ý phụ lấy từ câu CTA trong lời>"]}`; có logo/tên kênh
     thì điền `kenh`, không thì để trống (avatar = icon ghim bản đồ, không hiện tên kênh).
   - `sua_chu`: sửa lỗi Whisper cho SUB (tên riêng viết hoa, từ nghe nhầm) — chỉ sửa chữ, KHÔNG đổi số.
   - `the_tai_lieu`: rỗng trừ khi có tài liệu đạt C4.
   - Mục nào lời không nói rõ (tên kênh, logo, vị trí mơ hồ) ghi vào `_doan` để hỏi ở cổng.
3. **`dia-diem --work <dir>`** (mạng) → `dia_ly/<key>.json`; hết ⛔ mới đi tiếp. Đọc cột tên OSM trả về: phải đúng
   thực thể (vd hỏi "Huyện Chương Mỹ" mà ra "Thị trấn Xuân Mai" là sai).
4. Tài liệu (chỉ khi lời nhắc hồ sơ/văn bản/số liệu và không có Resources): tìm web (WebSearch thường → mở rộng) →
   `run.py tai-lieu xac-minh --url <url> --so 6.068 --so 3.002 --tu "sông Đáy" --out <work>/tai_lieu/<n>` → ĐẠT thì MỞ
   từng ảnh tải về, chọn ảnh chứa đúng số; không ảnh thì `trich-dan`. Thẻ ghi `"xac_minh": "tai_lieu/<n>/xac_minh.json"`,
   `"nguon": "<báo> · <ngày>"`. Không ĐẠT ⇒ không thẻ, ghi lý do vào `_doan`.
5. **`kiem-kh --work <dir>`** → sửa hết ⛔ (số không có trong lời, hở hình, địa điểm thiếu, thẻ chưa xác minh).
6. **`duyet --work <dir>`** (mạng) → `duyet.jpg` (ảnh xem trước từng cảnh + từng đoạn) + bảng cảnh. **Claude MỞ
   `duyet.jpg`** soi: bản đồ đúng chỗ lời nói, nhãn không đè thẻ/sub, hành lang/đoạn vẽ đúng, huy hiệu đúng số và đúng
   đoạn, tên địa danh phụ không đè nhau / không trùng tên, bản đồ định vị chấm đúng khúc, CTA có nút + icon. Cần soi kỹ 1 giây nào thì
   `scripts/dung.py --work <dir> --xem-truoc 9.8,30.9` → `xem_truoc_*.jpg` (có sub).
7. **CỔNG DUYỆT — DỪNG 1 lần**, đưa người dùng: bảng cảnh (giây · lời · hình · địa điểm OSM), thẻ tài liệu (hoặc "không
   có — vì sao"), danh sách ĐOÁN, rồi hỏi đủ D1–D5 dưới. Chờ trả lời.
8. **`dung --work <dir>`** (mạng nếu thiếu ô) → `<audio>_BDQH.mp4` cạnh audio (đã có thì `_ban2`, `_ban3`… không ghi đè).
   Chỉ đổi SFX/nhạc: `scripts/dung.py --work <dir> --chi-tieng <video đã dựng>` (chép nguyên hình, ra bản mới).
9. **`kiem --work <dir>`** → số đo (khổ, fps, độ dài, LUFS, đỉnh) + `soat_canh.jpg` + `soat_sub_*.jpg` + `soat_sub.txt`
   rút từ CHÍNH file mp4. **Claude MỞ hết ảnh soát**: chính tả từng cụm sub, chữ vàng đúng chữ đang đọc, bản đồ đúng
   chỗ, không đè. Có lỗi → sửa kế hoạch → dựng bản mới.
10. Giao: đường dẫn file, độ dài, khổ, bảng lời → cảnh, các mục còn ĐOÁN. Không kể lể quá trình.

## CÁC DIALOG Ở CỔNG DUYỆT (lần nào cũng hỏi, có đề xuất sẵn)

- **D1 Kênh:** tên kênh / logo / clip CTA (chưa có ⇒ đề xuất: không logo, CTA nút đỏ "THEO DÕI" + tay bấm, avatar = icon ghim bản đồ — C11).
- **D2 Địa điểm:** bảng địa danh → đối tượng OSM + toạ độ; mục nào Claude tự suy (giao điểm, đầu tuyến) hoặc ĐOÁN thì
  đánh dấu; người dùng xác nhận/sửa.
- **D3 Tài liệu:** thẻ nào có (ảnh + URL + câu chứa số) / không có (vì sao). Người dùng có file thì đưa vào Resources.
- **D4 Chữ trên hình:** hook 3 dòng + các thẻ đầu đề (đều lấy từ lời) — đồng ý hay sửa câu chữ.
- **D5 Sửa chính tả sub:** bảng `sua_chu` (Whisper nghe nhầm → sửa) — xác nhận tên riêng.

## Loại cảnh (`canh[].loai`, mốc giây = giây AUDIO)

| loai | Khi lời nói | Trường chính |
|---|---|---|
| `bay_tuyen` | sông/đường/kênh, "mở rộng N m", hành lang, cảnh chuyển | `tuyen`, `tu_diem` [`den_diem`, `nguoc`, `giua`], `zoom` 14–16.5, `toc_do` m/s (90–160), `hanh_lang_m` (+`hanh_lang_tu`), `ve_tuyen`, `thuoc {t, nhan, rong_m}`, `nhan [{diem,text}]` (nên đặt tên điểm xuất phát), `ten_tuyen` (mặc định tên tuyến; `false` tắt), `dong_chay`, `dia_danh`, `dinh_vi` |
| `ban_do_tong` | "từ A đến B … km", chia đoạn, số liệu theo đoạn, toàn tuyến | `tuyen`, `bbox_doan [a,b]`, `tieu_de`/`phu`, `doan [{t, tu_diem, den_diem, nhan, phu, phu_tu, nhan_dau, nhan_cuoi, zoom_vao, dai_ve, mau, huy_hieu, huy_hieu_tu}]` — `huy_hieu` = số ĐÚNG lời ("12 km", "1.217 hộ") hiện ở giây `huy_hieu_tu` (giây đọc số) |
| `to_vung` | tên xã/huyện/phường/tỉnh | `vung [keys]`, `hien {key: giây đọc tên}`, `nhan {key: chữ}`, `tuyen` (vẽ sông kèm), `mau` (bỏ trống = mỗi vùng 1 màu) |
| `diem` | cầu, đập, nút giao, công trình | `diem`, `zoom_tu`→`zoom`, `t_zoom`, `nhan`, `phu_nhan` (dòng phụ chú thích — chỉ chữ có trong lời), `ngam` (mặc định bật), `ban_kinh_ngam`, `huong_nhan` (phai/trai), `dinh_vi: "<key tuyến>"` |
| `thuoc_do` | khoảng cách giữa 2 điểm | `a`, `b`, `nhan` (mặc định "≈ N M" đo thật) |
| `tinh` | câu cảm xúc, bay chậm | `diem`, `zoom` |
| `cta` | "theo dõi kênh…" ở cuối | `file` (clip/ảnh) hoặc thẻ nút C11: `dong` [dòng chính, dòng phụ theo lời], `bieu_tuong` (false = bỏ chip icon), `nhan_bieu_tuong` |

Mọi cảnh (trừ `ban_do_tong`, `cta`) nhận thẻ đầu đề: `tieu_de`/`phu` hoặc `dau_de [{t, tieu_de, phu}]` (đổi thẻ theo
mốc giây — đặt `t` = lúc lời đọc tới ý/số đó). Không lặp 1 đoạn bay 2 lần; cảnh bay khác nhau chọn `tu_diem` khác nhau.

**Nhấn mạnh thêm tay (mọi cảnh, C10):** `nhan_manh: [{kieu, diem | man_hinh [x,y], t, den?, text?, phu?, mau?, ban_kinh?}]`,
`kieu` ∈ `song` (gợn sóng) · `ghim` (ghim rơi) · `chu_thich` (dây + hộp tên) · `huy_hieu` (số nổi — số phải có trong lời)
· `ngam` (vùng ngắm) · `nhan` (nhãn trắng). Đặt `t` = giây lời nhắc. Mỗi cảnh ≤ 2–3 điểm nhấn, không chồng chéo.
**`cai_dat`:** `dia_danh` (true), `dia_danh_bo` [tên không muốn hiện], `dinh_vi` (true), `dinh_vi_doan` [a, b] (khúc tuyến
vẽ trong bản đồ định vị — nên = khúc lời nói tới, vd `["dau_song", "ra_hn"]`), `dinh_vi_ten`.

## Các lớp đồ hoạ (do_hoa.py / ban_do.py — toạ độ khung 1080×1920)

- Thẻ hook: hộp navy 960 px ở y 202, dòng 1 vàng SemiBold 32, dòng 2 trắng ExtraBold 32, dòng 3 xám 17, IN HOA.
- Thẻ đầu đề: hộp navy 1004 px ở y 56, tiêu đề vàng ExtraBold 34 IN HOA (tự thu ≤ 950 px), dòng phụ trắng 24.
- Bản đồ tổng: nền vệ tinh tối 62 % + bớt màu, sông xanh lơ 4 px, đoạn đang nói 9 px phát sáng vẽ chạy 2 s (màu theo
  đoạn), đoạn cũ mờ 55 % (giữ huy hiệu số nếu không đè), nhãn 2 đầu IN HOA trắng viền tối + chấm trắng, gợn sóng đầu
  đoạn, ghim rơi + sóng cuối đoạn, vạch trắng chạy trên đoạn đã vẽ, huy hiệu số giữa đoạn, tên thị trấn/phường chữ
  thường trắng 24 mờ 85 %, camera zoom vào đoạn 0,6 s.
- Hành lang: vùng đệm ±N/2 m quanh tim tuyến (nét dày → đường viền, không xoắn ở khúc uốn), viền vàng 3 px, phủ vàng 10 %.
- Tô vùng: mỗi vùng 1 màu, viền 4 px tự vẽ quanh ranh 0,7 s (đầu vạch chấm trắng) → phủ 24 %, gợn sóng ở tâm,
  pill navy chấm màu bật back-out; hiện đúng giây đọc tên.
- Điểm (`diem`): vùng ngắm (ngoài vòng R 190 tối 45 %, vòng nét đứt vàng xoay) + ghim rơi nảy có bóng + gợn sóng +
  chú thích kéo dây (hộp navy vạch màu, tên IN HOA trắng 30). Thước: vạch trắng 2 ngạnh + pill vàng chữ navy.
- Cảnh bay: tim tuyến xanh lơ + vạch trắng chạy (hướng dòng chảy), tên tuyến pill chấm xanh có dây, nhãn điểm có gợn
  sóng, tên làng/xã chữ thường trắng 26 viền tối + chấm (≤ 6 nhãn, cách ≥ 170 px, hiện/ẩn mờ 0,3 s), bản đồ định vị
  262×292 ở x 34 y 1052 (viền trắng, tab tên tuyến vàng, chấm vàng gợn sóng = chỗ đang bay).
- Logo góc phải trên (cao 70) hoặc tên kênh; dòng nguồn ảnh y 1830; CTA nút (C11) hoặc clip kênh.

## Bẫy đã gặp (đừng lặp lại)

- **Overpass công cộng 502 / quá giờ (04/11/2026)** ⇒ không dùng. Photon (tìm, trả osm_type/osm_id) + OSM API
  `…/api/0.6/<type>/<id>/full.json` (hình học) + `/api/0.6/map.json?bbox=` (đường cắt sông).
- **`full.json` của relation kèm cả relation con** (huyện chứa thị trấn) ⇒ phải lấy relation đúng id, không lấy cái
  đầu tiên (04/11: "Huyện Chương Mỹ" ra ranh "Thị trấn Xuân Mai").
- **Tên hành chính cũ/mới sau sáp nhập 1/7/2025**: huyện cũ là `boundary=historic`, `end_date=2025-06-30`; xã mới
  `admin_level=6`. Lời đọc "Quốc Oai, Chương Mỹ…" = huyện cũ.
- **Whisper tách số** "6.068" thành "6" + ".068" ⇒ `dung.gop_so` gộp lại trước sub và trước khi kiểm số. Whisper nghe
  nhầm tên riêng ("Trường Mỹ" → Chương Mỹ, "canh hóa" → kênh hóa, "đêm mới" → đê mới, "di rời" → di dời,
  "hectare" → ha, "sông đáy" → sông Đáy) ⇒ `sua_chu`.
- **Chữ bắt đầu đúng mốc hết câu** (vd "và"@52,70 = hết câu trước) từng bị gán vào 2 câu ⇒ mỗi chữ chỉ thuộc 1 câu
  (câu có `start` lớn nhất ≤ chữ). build_ass tự bơm dấu chấm vào chữ cuối câu để cắt cụm — dấu câu KHÔNG hiện trên sub.
- **build_ass đo cụm theo 1 dòng** ⇒ truyền `--font-size` = cỡ sub; vẫn báo rộng thì chạy lại `--no-measure` (lớp
  SubKaraoke tự xuống 2 dòng).
- **Bài báo tìm được có thể đã bị thay nội dung** (CafeBiz 21/9/2026: cùng URL, curl và trình duyệt thật đều ra bài
  khác) ⇒ chỉ tin `xac-minh` tại lúc dựng; không đạt = không thẻ.
- **PyAV 19 bỏ `metadata_errors`** ⇒ faster-whisper nhận mảng numpy float32 đọc từ wav, không truyền đường dẫn.
- **ffmpeg drawtext lỗi Fontconfig / segfault trên máy này** ⇒ mọi chữ vẽ bằng PIL, ffmpeg chỉ mã hoá.
- **In tiếng Việt ra console Windows lỗi cp1252** ⇒ chạy `python -I -X utf8`, script tự `reconfigure` stdout.
- **Sông nhỏ (Đáy ~30–60 m) khó thấy ở zoom 15** ⇒ cảnh bay bật `ve_tuyen: true` (tim sông xanh lơ mờ).
- Tờ duyệt/soát: chú thích đặt NGOÀI khung ảnh (che thẻ đầu đề y 56–140 là soi sai).
- **Nhãn cuối đoạn sát dải sub** (04/11 bản 1: "ĐỊA PHẬN NINH BÌNH", "HẾT ĐỊA PHẬN HÀ NỘI" chạm mép trên sub 2 dòng)
  ⇒ mọi nội dung bản đồ (đoạn, nhãn, vùng, thước) nằm trong `vung_y` có đáy ≤ 0,70–0,72 khung; mặc định đã đặt,
  `kiem-kh` báo ⛔ nếu kế hoạch đặt đáy > 0,72.
- **Đo LUFS bằng ebur128**: phải đọc phần `Summary:` cuối (dòng chạy đầu in "I: -70 LUFS" ⇒ từng báo sai −70).
- **ffmpeg 9 (gyan full) trên máy này**: rút khung dùng `-fps_mode passthrough` (không dùng `-vsync`).
- Dựng 73 s mất ~12 phút CPU (2200 khung); chỉ đổi tiếng thì dùng `--chi-tieng`, không dựng lại hình.
- **Tên địa danh OSM thưa ở vài khu** (04/11: quanh đại lộ Thăng Long–Quốc Oai, Photon reverse 4 km chỉ ra Vân Côn, Quốc
  Oai) ⇒ cảnh bay luôn có tên sông + tên điểm xuất phát (`nhan`), không tự thêm tên. Photon reverse trả lẫn
  `house`/`postcode` ⇒ lọc `place`; phường/xã mới sau sáp nhập là RELATION `place=suburb` (Chương Mỹ, Yên Nghĩa…) ⇒
  nhận cả relation; bỏ tên có chữ số ("Xóm 7"); 2 thôn trùng tên ("Phù Yên" ×2) ⇒ chỉ giữ 1. Cache
  `~/.cache/ban-do-quy-hoach-bds-ve-tinh/dia_danh` (khoá `v2_…`).
- **Xem trước từng giây rời** (`--xem-truoc`): nhãn phụ phải hiện ngay ở khung đầu (không mờ từ 0), nếu không tờ duyệt
  thiếu nhãn dù video có.
- **Huy hiệu số của đoạn cũ trôi lên dưới thẻ đầu đề** khi camera zoom sang đoạn sau ⇒ đoạn cũ chỉ giữ huy hiệu nếu
  không đè (`hop_huy_hieu` + Chiem).
- **Nhãn thước "350 – 500 M" chạm vòng sóng nhãn điểm** (04/11 bản 4, 30–31 s: thước giữa khung, "ĐẬP ĐÁY" ngay trên)
  ⇒ thước vẽ sau nhãn điểm, nhãn thước đụng thì xuống dưới thước và giữ phía đó tới hết cảnh.
- **Heredoc trong Bash của máy này lỗi trích dẫn** khi nội dung có dấu nháy ⇒ viết file bằng Write, vá bằng script
  Python nhỏ.

## Skill này được bồi thêm sau mỗi lần chạy thật

| Ngày | Video | Góp ý / phát hiện | Đã sửa |
|---|---|---|---|
| 04/11/2026 | `ho_dan.mp4` (mẫu) → `ho_dan_audio.mp3` (72 s) → `ho_dan_audio_BDQH_ban3.mp4` | Tạo skill. Không quay màn hình, sub karaoke nguyên văn, tài liệu phải xác minh 100 %. Thử: 6.068 hộ / 3.002 ha tìm thấy dấu vết CafeBiz 21/9 nhưng trang đã đổi ⇒ không thẻ. | C1–C9, kiem-kh chặn số bịa, giao đường–sông, ra khỏi địa phận, ranh huyện cũ, sửa relation con, SFX đúng C6 + `--chi-tieng`, vùng bản đồ ≤ 70 % (không sát sub), đo LUFS đọc Summary |
| 04/11/2026 | `ho_dan_audio_BDQH_ban3.mp4` → `_ban4` → `_ban5` | Chủ dự án: "highlight rõ các địa điểm, trên bản đồ hiển thị lên vẫn hơi thô, chưa hl đa dạng, và có tên địa danh; ở cuối video kêu gọi có cái sfx nghe chói quá bỏ đi; cta nên có button, icon thay vì text đơn giản". | C6 bỏ chime CTA; C10 `diem_nhan.py` (gợn sóng, ghim rơi, chú thích, huy hiệu số, vùng ngắm, vạch chảy, viền tự vẽ, pill chấm màu, tên địa danh OSM tự né chữ, bản đồ định vị), `nhan_manh`; C11 `cta.py` (nút đỏ + chuông + tay bấm + chip icon); `kiem-kh` soát cả chữ huy hiệu / chú thích / CTA; nhãn thước tự né (bản 5) |
| 04/11/2026 | `ho_dan_audio_BDQH_ban5.mp4` | Chủ dự án: "oki rồi đó update tất cả vào skill nha" ⇒ bản 5 là CHUẨN. | Ghi video chuẩn vào đầu SKILL.md; hướng dẫn điền điểm nhấn + CTA (bước 2) và soi (bước 6); `quet` sinh sẵn `cai_dat.dia_danh/dinh_vi/dinh_vi_doan`; bỏ lớp `CtaTinh` cũ; spec/phân tích ghi chú C6 mới |
