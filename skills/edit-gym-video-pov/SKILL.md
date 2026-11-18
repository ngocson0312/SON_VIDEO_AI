---
name: edit-gym-video-pov
description: "Edit video POV (quay góc nhìn thứ nhất, camera đeo ngực/đầu/cầm tay, ví dụ HLV dẫn khách đi tham quan phòng tập) dọc 9:16 tiếng Việt thành clip viral 20-30 s: cắt theo PHÁCH nhạc (mỗi cảnh = số phách nguyên), zoom đập đúng phách, chuyển cảnh (trượt / chớp trắng / zoom / radial / cắt cứng), tiêu đề 'POV: …' đập vào, nhãn vàng từng khu, sub karaoke chỉ ở câu có lời rõ, SFX ~1 tiếng / cảnh, nhạc nền né giọng, −14 LUFS. Whisper nhận lời → Claude soi tờ khung chọn đoạn hook + cảnh đẹp → viết ke_hoach.json → dựng → tự kiểm. ĐÃ CHỐT thành skill 18/11/2026 (CHƯA đưa vào tool, chưa đẩy git). Trigger '/edit-gym-video-pov', 'edit video POV', 'video POV này edit xịn', 'edit video quay góc nhìn thứ nhất'."
---

# edit-gym-video-pov — video POV thô → bản edit viral GIỮ TRỌN nội dung (bản thử 2, 18/11/2026)

Mẫu thử: `D:\____TTT_____\KH_Test\Vinh\Vinh\POV\Video_Thô.mp4` (128 s, HLV Vinh đón mẹ + 2 bé ở phòng tập DQ). Video mẫu KHÔNG có trong thư mục → khuôn lấy từ nghiên cứu cách làm POV phổ biến (xem dưới), chưa phải "chuẩn khách chốt".

## DNA của một clip POV viral (nghiên cứu web + áp vào skill)
- **Ngắn 15-30 s**, đổi hình mỗi 2-3 s (nhiều nguồn: "thay đổi gì đó trên hình ≤ 3 s": cắt / zoom / chữ / SFX).
- **Mở bằng dòng "POV: …"** đặt người xem vào vai (ở đây "BẠN LÀ HLV ĐÓN KHÁCH VÀO PHÒNG TẬP").
- **Hook = khoảnh khắc đầu có người + lời** (video thô này: lời chào "Dạ em Vinh đây, hello hai con" + bé ghé sát ống kính) — nếu có cảnh mạnh hơn ở giữa/cuối thì đưa lên đầu.
- **Nhạc là xương sống**: cắt cảnh đúng phách (skill khoá mỗi cảnh = N phách, chuyển cảnh nằm GIỮA điểm phách), nhạc hạ khi có người nói (sidechain).
- **Chữ**: nhãn ngắn tên khu vực, sub bật từng chữ (karaoke) chỉ khi lời nghe rõ; đoạn ồn / thì thầm KHÔNG sub (Whisper bịa).
- ~~HUD REC~~ — khách bảo BỎ (18/11): không tự thêm thứ khách không yêu cầu; `rec_hud` mặc định tắt.
- Cắt bỏ đoạn tĩnh dài (video thô: phút 76-128 là ngồi nói chuyện, 50 s → chỉ giữ câu "chị cứ ngồi đi" + câu chốt "để em lấy cái tờ giấy").

## Cách chạy (mọi lệnh: `python -I -X utf8 .claude\skills\edit-gym-video-pov\scripts\pov.py …`; Whisper cần `faster-whisper`, ảnh cần `pillow`, `numpy`)
1. `pov.py quet --video "<video thô>" [--prompt "tên riêng, từ chuyên ngành"]` → `<video>_pov_work\`: `loi_doc.txt`, `rms.txt`, `to_khung_*.jpg` (1 khung/giây, nhãn vàng = giây nguồn). Lần đầu tải Whisper large-v3 (~3 GB, CPU nên lâu).
   ⚠ Whisper hay BỊA ở đoạn ồn/im ("hãy subscribe cho kênh …") → đối chiếu `rms.txt` + khung hình + nghe nghĩa; chỉ dùng câu thật.
2. **Claude MỞ MỌI `to_khung_*.jpg`** + đọc `loi_doc.txt`, rồi viết `ke_hoach.json` (mẫu `references/ke_hoach_mau.json`):
   - `bpm` 100 (mặc định), `nhac`: `"mau"` (nhạc tự tạo `nhac_mau.py`, chỉ để thử) / đường dẫn file nhạc thật / `"khong"`.
   - `title`: `["POV:", "dòng 1", "dòng 2"]`, `title_y` (mặc định 1130; đặt cao hơn sub, tránh mặt), `title_t` [bắt đầu, kết thúc].
   - `sub`: các đoạn **giây nguồn** có lời rõ để làm karaoke, vd `[[0,1.7],[80.2,81.8]]`; `sua`: `{"chữ sai":"chữ đúng"}`.
   - `scenes[]`: `src` (giây nguồn, điểm vào ĐÚNG phách), `beats` (số phách, 1 phách = 60/bpm s; cảnh ≥ 2 phách ≈ 1,2 s), `voice` (true = giữ tiếng nói, false = tiếng nền chỉ 22 %), `zoom` `punch|in|out|none` (+ `zslow`, `tam` [x,y] 0-1), `trans` chuyển vào cảnh này: `slideleft|slideright|slideup|zoomin|radial|circleopen|fadewhite|fadeblack|pixelize|cut` (nhiều cảnh nhanh liền nhau dùng `cut`), `label` (nhãn vàng ≤ 3 từ, IN HOA, CHỈ đặt khi nhìn khung thấy đúng khu đó), `sfx` `[["ding",0.0]]` (tên: swoosh swoosh2 whoosh pop pop2 ting ting2 riser flash shutter punch glitch tada click ding buildup).
   - Thứ tự gợi ý: HOOK có lời (6-7 phách) → 5-8 cảnh b-roll 2-4 phách (đa dạng: phòng, thiết bị, tay POV đưa đồ, mô hình) → cảnh có lời chốt (4-5 phách) cuối.
   - Cảnh KHÔNG được kéo quá hết video nguồn (clip nguồn ngắn hơn → đứng hình đen).
3. `pov.py dung --work <dir>` (~40 s cho 25 s; `--ghi-de` để ghi đè, mặc định ra `_ban2`…) → ghép xfade 1 lần, ASS (title, nhãn, HUD, sub), SFX tự đặt ở mỗi chuyển cảnh/nhãn/tiêu đề, nhạc sidechain, rồi `loudnorm` 2 lượt tuyến tính −14 LUFS, TP ≤ −2 dB.
4. `pov.py kiem --work <dir>` → độ dài, LUFS, true peak, `soat.jpg` (2 khung/cảnh). **Mở soat.jpg**: chữ không đè mặt/sub không chồng, cắt đúng cảnh, không cảnh trống tường.

## Bản 2 (khách góp ý 18/11): GIỮ TRỌN video + chữ đẹp
- ⛔ **KHÔNG rút video thô thành clip 25 s** — khách: "video hơn 2 phút mà cắt hết nội dung". Mặc định phủ TOÀN BỘ video: `pov.py nhap --work <dir> --video <v> [--tua "[[54,61.5,2.5]]"] [--ngoi-noi 66]` lập `ke_hoach.json` nháp ~40 cảnh liên tục theo phách (đoạn đi tham quan: chuyển cảnh đẹp + SFX; đoạn ngồi nói: jump-cut zoom luân phiên, giữ tiếng; đoạn chết/tường trắng: tua nhanh + huy hiệu đỏ "TUA NHANH x2"), sub chỉ ở câu Whisper tin cậy (TB ≥ 0.7, min ≥ 0.4). Sau đó Claude thêm `labels` `[[giây nguồn,"CHỮ"],…]` + `title`/`title_hi` rồi `dung`.
- **Chữ / bubble vẽ bằng PIL → PNG** (`overlays.py`): viên thuốc gradient vàng + viền trắng + bóng + huy hiệu pin, tiêu đề "POV:" viên vàng nghiêng + dòng trắng viền navy dày + từ khoá vàng gradient + lấp lánh, huy hiệu đỏ. ffmpeg phủ (đập vào / trượt vào + mờ ra). Bản ASS (`lop_ass`: true) chỉ là dự phòng — xấu, thô. sub là ASS.
- Âm thanh: loudnorm 2 lượt + `alimiter 0.6` + AAC 256k (limit cao hơn thì sau AAC vẫn vọt > 0 dBFS).
- Chữ không hiện đủ dấu: canvas dòng chữ phải cao đủ (dấu mũ cắt ngọn).

- **Tiêu đề kiểu PHẲNG (khách chốt kiểu 18/11, ảnh mẫu)**: ô vàng phẳng nhỏ "POV:" chữ tối + 2 dòng trắng đậm đổ bóng mềm, từ khoá vàng, đặt TRÊN (`title_y` 215), KHÔNG thẻ kính / viên to (`title_style` "phang" mặc định; "the" = bản viên to cũ).
- **Sub = tiếng người trong video (cả khách)**: nghe được (Whisper tin cậy) thì sub, không nghe được thì KHÔNG sub. Lọc tiếng ồn trước khi nhận lời (`highpass 120 + afftdn + dynaudnorm`) cho câu xa mic rõ hơn; ghép 2 lượt nhận (thường + đã lọc), bỏ câu vô nghĩa ('bản Nhật', 'bác chơi').

- **CTA FOLLOW 3D (bản chốt hướng 18/11, thay kiểu chữ+nút phẳng bị chê 'lỏ, không xịn')**: `"cta": {"dur":4.6,"y":930}` → `cta3d.py`: CHỈ nút FOLLOW 3D (khối đỏ có độ dày, bóng, viền sáng, chữ FOLLOW, KHÔNG logo TikTok) + bàn tay 3D kiểu icon con trỏ tay (mặt trắng-xám bóng, viền đen, khối dày đen phía dưới-trái, ngón trỏ dài nhất — mẫu khách gửi 18/11; găng hoạt hình đã bị chê 'xấu') trượt lên rồi BẤM LIÊN TỤC mỗi 1 s (nút lún, vòng sóng, tia lấp lánh), nền cuối làm nhoè + tối, SFX click mỗi lần bấm. Không chữ phụ. (Kiểu cũ dưới đây chỉ để tham khảo.)
- ~~CTA FOLLOW chữ + nút phẳng~~ (khách 18/11): `"cta": {"kenh":"HLV VINH","dong2":"ĐỂ XEM THÊM VIDEO","dur":3.6,"y":800}` → đóng băng khung cuối + tối nền, chữ FOLLOW <KÊNH>, nút đỏ TikTok bật ra, BÀN TAY trượt vào bấm (vòng sóng) → đổi "ĐÃ FOLLOW", tay trượt ra; SFX swoosh / pop / click / ting. Dùng `cta_follow.py` (mượn từ dung-toi-edit). Tên kênh phải hỏi khách (bản thử ghi tạm "HLV VINH").
- **ÊM, không giật (khách 18/11: "giật cục, khó chịu")**: video POV quay tay đã rung sẵn → KHÔNG cắt dồn, KHÔNG zoom đập, KHÔNG chuyển cảnh lướt/xoay, KHÔNG tua nhanh quét. Cảnh dài 3,6–7 s (6-12 phách), nối bằng hoà tan 0,5 s, zoom chậm ≤ 5 %, đoạn ngồi nói đổi cỡ hình nhẹ 1,0↔1,16. Zoom tính ở độ phân giải gấp đôi (rồi thu nhỏ) để không rung vì làm tròn pixel. Nhiều cú cắt + đập zoom chỉ hợp video có nhạc nhanh, không hợp footage đã rung.

- **Nhãn CHỈ để chỉ ĐỊA ĐIỂM đang ở** (khách 18/11: "mô hình cột sống… thêm vào làm j"): không gắn nhãn cho vật / chi tiết ngẫu nhiên trong cảnh (mô hình cột sống, dụng cụ, poster) và không tự bịa nhãn hành động. Chỉ tên khu vực nhìn thấy rõ (PHÒNG TRỊ LIỆU, KHU TẬP GYM) hoặc lời nói đang nhắc tới. Không tự thêm thành phần khách không yêu cầu (HUD REC cũng đã bị bỏ).
- **Nhạc nền nhỏ**: `nhac_vol` 0,2 (giọng nói phải nghe rõ, khách 18/11 chê nhạc to); sidechain ratio 12.

- **CTA CHỈ BẤM 1 LẦN (khách 18/11)**: nút FOLLOW 3D + tay con trỏ 3D hiện, bấm ĐÚNG 1 LẦN lúc 1,3 s (1 vòng sóng + 1 SFX click) rồi HẾT VIDEO NGAY (khách: không để lâu); `cta.dur` 2,0 s. Không lặp bấm.
- **CẮT PHẦN THỪA (khách 18/11 cho phép "cứ mạnh dạn cắt")**: `pov.py nhap --giu "[[a,b],…]"` chỉ giữ các đoạn chọn (bản thử: 128 s → 74 s + CTA). Cắt: đoạn tường trắng / camera ngẩng, đi hành lang trống, ngồi im nhận dạng rác, câu lặp. Giữ: lời chào hook, đổi khu vực (có thể nhận ra), tay POV đưa đồ, các câu nói rõ, câu chốt. Nối đoạn bằng hoà tan 0,5 s.
- Câu ngắn cũng phải có sub nếu nghe được ('Dạ', 'Chị vô ngồi đi chị nha'): nhận lời lại từng đoạn nghi thiếu bằng `faster-whisper` trên âm đã lọc (vad_filter True/False so sánh).
- `nhac_vol` mặc định 0,1 (0,2 vẫn bị chê "hơi to").

## Bẫy đã gặp (18/11 chạy thật)
- **Tên font ASS**: dùng `Be Vietnam Pro Black` (đủ tên). `Be Vietnam Pro` → libass rơi về Arial (nhìn mỏng, xấu).
- ffmpeg 9: dùng `-/filter_complex file`, không còn `-filter_complex_script`.
- Escape ASS (`\k`, `\fad`, `\t`) viết bằng chuỗi raw `r"…"` — chuỗi thường biến `\f`/`\t` thành ký tự điều khiển, sub mất hiệu ứng.
- Tiêu đề giữa màn hình đè sub (y 1130 + 3 dòng chạm 1590) → để `title_y` ≈ 860 khi sub ở dưới.
- Cụm sub sau phải cắt cụm trước (không chồng "HELLO" lên "CON").
- Nhạc + SFX + giọng trộn xong có thể TP > 0 dBFS sau AAC → luôn chuẩn âm 2 lượt + `alimiter`.
- Cảnh quay vào tường trắng (camera ngẩng) trông chết → chọn lại `src` hoặc `tam` kéo xuống nơi có đồ.

## Việc còn lại trước khi đóng vào tool (chờ khách chốt bản thử)
- Nhạc thật (hiện là beat tự tạo), có thể thêm tách người / chữ lớn sau đầu (dùng `bds-sale-viral`), cảnh mở teaser, màn kết CTA, tự dò cú cắt / hook bằng RMS + chuyển động thay vì Claude chọn tay, nhãn tự gợi ý từ khung (mô hình hình ảnh).
