# Schema `kich_ban.json` — kịch bản bản đồ (Claude viết từ `loi_doc.txt`)

Mọi mốc thời gian là **giây tuyệt đối** của audio (lấy từ `loi_doc.txt`: `từ@giây`). Video dài = audio + 0,9 s.

```json
{
 "phien_ban": 1,
 "khung": {"rong": 1080, "cao": 1920, "fps": 30},
 "audio": "đường dẫn audio",
 "nhac": "auto" | "khong" | "đường dẫn mp3",
 "sub": {"toi_da_tu": 3},
 "nhip": [ {nhịp}, … ]
}
```

## Nhịp (= 1 câu lời, lấy đúng giây bắt đầu câu)

```json
{"id": "n01", "t": 0.0, "loi": "câu lời (để đối chiếu)",
 "camera": {"toi": <vị trí>, "rong_km": 2200, "nghieng": 35, "kieu": "bay|vong|giu", "bay_trong": 1.5},
 "dong_tac": [ … ]}
```

- `camera.toi`: tên nước / bang / biển / thành phố (tiếng Việt hoặc Anh) hoặc `[lon, lat]`.
- `rong_km`: bề rộng mặt đất nhìn thấy (30–30000). Cận 1 nước nhỏ ≈ 1200–2500; cả nước lớn ≈ 5000–9000; cả đại dương ≈ 10000–14000.
- `nghieng`: 0 = nhìn thẳng xuống, mặc định 35. `kieu`: `bay` (bay thẳng), `vong` (lùi xa rồi sà vào — dùng khi đổi lục địa hoặc câu chuyển/câu hỏi), `giu` (đứng yên, trôi chậm). Bỏ `kieu` thì tự chọn theo khoảng cách. `bay_trong`: giây bay (mặc định ≈ 65 % độ dài nhịp, tối đa 2,4).
- Nhịp có `"camera": {"kieu": "giu"}` = giữ cảnh cũ.
- **Camera dạng danh sách** (khuyên dùng): `"camera": [{"luc": 3.4, "toi": [111,12], "rong_km": 2200}, {"luc": 8.6, "toi": [115,50], "rong_km": 5200}]` — `luc` = giây camera ĐẾN NƠI; camera chạy liên tục (PCHIP) qua các điểm dừng, không dừng-rồi-chạy. Cách nhau tối thiểu ≈ (quãng đường ÷ bề rộng màn hình + 0,5·|ln tỉ lệ zoom|) ÷ 0,35 giây, quá gần thì engine báo ⛔.

## Vị trí (`tai`, `nuoc`, `tu`, `toi`)

Nước: "Triều Tiên", "Mỹ", "Nga", "Trung Quốc", … (bảng `chung.NUOC`) hoặc mã ISO2 ("KP"). Bang/tỉnh: "Alaska", "California", "Bắc Kinh", "Hokkaido" (Natural Earth admin1). Biển: "Biển Đông", "Thái Bình Dương", "Bắc Thái Bình Dương", "Biển Nhật Bản", "Eo biển Malacca", "Guam" … (bảng `chung.BIEN`). Thành phố / địa danh khác: ghi tên đầy đủ, bước `tai` sẽ geocode ("Washington, D.C." chứ không phải "Washington" — Washington là bang). Chắc nhất: `[lon, lat]`.

## Bộ động tác chuẩn (`loai`)

| loai | trường bắt buộc | tuỳ chọn | ý nghĩa |
|---|---|---|---|
| `to_nuoc` | `nuoc`, `luc` | `co: true` (phủ cờ) / `mau: "#ff4a1f"`, `den` | tô khối nước/bang nổi lên, giữ tới `den` (mặc định hết video) |
| `nhan` | `tai`, `chu`, `luc` | `kieu: viet_tay\|neon\|doc`, `co_km`, `lech_km: [đông, bắc]`, `mau`, `den` | chữ viết tay trắng nằm trên mặt đất (tên nước). `doc` = chữ vàng dựng dọc cạnh vật (tên vũ khí) |
| `chu_neon` | `tai`, `chu`, `luc` | `co_km`, `mau`, `den` | chữ neon xanh phát sáng (tên biển / vùng) |
| `ghim` | `tai`, `luc` | `chu` (mặc định = tai), `den` | bong bóng ghim trắng chỉ xuống thành phố |
| `vat_the` | `tai`, `vat`, `luc` | `co_dinh: true` + `co` (phần chiều cao khung, vd 0.16) hoặc `co_km`; `hieu_ung: noi_len\|truot_vao\|hien`; `tu_huong: tren\|trai\|phai\|duoi`; `lech: [dx, dy]` (phần chiều cao khung); `nam_dat: true` + `goc` (đặt nằm trên mặt đất, xoay theo độ); `den` | vật thể dựng đứng tại điểm: `ten_lua`, `ve_tinh`, `tau_chien`, `tau_san_bay`, `tau_dau`, `gian_phong`, `may_bay`, `xe_tang`, `thung_dau`, `tien`, `toa_nha`, `virus`, `binh_linh`, `bom_hat_nhan` … (bảng `chung.VAT_THE`, hoặc đường dẫn PNG) |
| `nguoi` | `ten`, `luc` | `tai` (neo vào điểm) hoặc `vi_tri: giua\|trai\|phai`; `co` (0.42); `lech`; `den` | ảnh cắt nền nhân vật (tải Wikipedia, cần duyệt) |
| `anh` | `luc` | `tim` (câu tìm Commons) hoặc `file`; `rong` (0.76); `vi_tri: [x, y]`; `tieu_de`; `den` | thẻ ảnh minh hoạ bo góc viền trắng trượt vào |
| `so` | `chu`, `luc` | `phu` (dòng phụ), `vi_tri`, `mau`, `den` | số to vàng đếm lên (hoặc chữ ngắn màn hình, vd "THEO DÕI KÊNH") |
| `phong` | `tu`, `toi`, `luc` | `bay_trong` (3), `so_luong` (1–3), `du_kien: true` (vẽ sẵn nét đứt), `vat`, `mau`, `cong` (0.22), `co_km` | tên lửa dựng lên rồi bay theo cung sáng vàng từ `tu` tới `toi`; đặt `no` tại `toi` lúc `luc + 0.6 + bay_trong` |
| `no` | `tai`, `luc` | `co_km`, `keo_dai` (1.5) | vụ nổ lửa + loé trắng + vệt cháy trên đất |
| `vo_vun` | `nuoc`, `luc` | `keo_dai` (1.6) | khối nước + nhãn vỡ thành mảnh văng ra, tự tắt `to_nuoc`/`nhan` của nước đó |
| `radar` | `tai`, `luc` | `ban_kinh_km`, `so_vong` (3), `chu_ky` (1.8), `den` (luc + 3.6) | vòng sóng lan từ điểm |
| `tach` | `tai`, `luc` | `toi` hoặc `huong` (độ), `so_vet` (4), `dai_km`, `keo_dai` (1.4) | tách thành nhiều vệt trắng (đầu đạn) |
| `tuyen` | `tu`, `toi`, `luc` | `bien` (true = đi theo biển tránh đất liền; tự bật khi `vat` là tàu), `qua: [điểm dẫn]` (eo hẹp), `keo_dai` (2), `vat` (icon chạy dọc tuyến, nằm đất), `mau`, `net_dut` (true), `cong`, `co_km`, `den` | tuyến đường / dòng chảy A→B có mũi tên vẽ dần |
| `cta` | `luc` | `chu` (THEO DÕI KÊNH), `phu`, `vi_tri` ([0.5,0.42]), `mau` | nút kêu gọi theo dõi cuối video: nút đỏ bo tròn + chuông + con trỏ bấm + sóng loé (thay chữ trơn) |
| `lan` | `tai`, `luc` | `ban_kinh_km`, `keo_dai` (2), `mau`, `den` | vùng tròn lan rộng (ảnh hưởng, dịch, căng thẳng) |

## Luật dựng (rút từ video mẫu — bắt buộc)

1. **1 câu = 1 nhịp**, `t` = giây bắt đầu câu. Mỗi nhịp **1 việc chính** (bay tới nơi mới, hoặc phóng/nổ/vỡ, hoặc hiện vật). Tối đa 2 hiệu ứng lớn (`phong`/`no`/`vo_vun`/`tach`) mỗi nhịp, 2 vụ nổ cách nhau ≥ 1 s.
2. **Danh từ đọc tới đâu, hiện tới đó**: `luc` của `ghim`/`vat_the`/`nhan`/`nguoi` = giây của từ đó trong `loi_doc.txt` (trừ 0,1–0,2 s).
3. **Cao trào cuối câu**: `no`/`vo_vun` đặt ở 0,3–0,6 s trước khi câu kết thúc.
4. **Camera không bao giờ cắt**: chỉ bay. Đổi lục địa hoặc câu chuyển/câu hỏi → `kieu: "vong"`. Câu nối ý → `giu`. Đừng bay 2 lần trong 1 nhịp.
5. Nước được nhắc = `to_nuoc` (nước chính phủ cờ `co: true`, nước phụ tô màu `#2fa8ff`/`#ffcc00`), kèm `nhan` tên viết tay ĐÚNG TIẾNG VIỆT như lời đọc (Nga, Trung Quốc, Hoa Kỳ). Biển = `chu_neon`. Thành phố = `ghim`.
6. Nhân vật nổi tiếng được nhắc → `nguoi` hiện ~3 s, neo vào nước của họ. Không bịa người không được nhắc.
7. Không bịa con số: `so` chỉ dùng số có trong lời.
8. Mọi `vat` phải có trong bảng `VAT_THE` (hoặc PNG người dùng cấp). Thiếu loại → chọn loại gần nghĩa nhất, ghi chú ở cổng duyệt.
9. Video phải có động tác hoặc camera mới ít nhất mỗi 4 s; câu dài > 4 s cần 2 động tác nhỏ.
