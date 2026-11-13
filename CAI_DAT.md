# SON_VIDEO_AI - skill video (Claude Code)

- skills/ban-do-quy-hoach-bds-ve-tinh : audio tin quy hoach/BDS -> video ban do ve tinh 9:16
- skills/skill-bando-tintuc-chinhtri  : audio tin tuc/dia chinh tri -> video ban do 3D 9:16
- skills/ban-do-tien-ich-nha-dat      : thong tin nha + audio + anh/clip nha -> video ban do tien ich quanh nha 9:16
- skills/skill_video_bds_bietthu      : video nguoi noi (sale BDS) + Resources (anh/video du an) -> video kieu "Biet thu rung tang ham" 9:16
                                        (doc skills/skill_video_bds_bietthu/SKILL.md, muc "VIEC DANG DO" truoc khi lam)
- skills/nns-ban-do-ha-tang            : ten 1 dia diem (du an BDS, toa nha, di tich, ho...) -> video ban do ha tang giao thong quanh do 9:16
                                        (khong giong, chi SFX + nhac neu co; tile ve tinh cache o <du an>\_cache_tiles\esri)
- skills/nns-ha-tang-quy-hoach-tien-ich : link Google My Maps ban do quy hoach + danh sach tien ich -> video ban do quy hoach
                                        (lop mau quy hoach + line sang tu ranh toi tung diem ghi khoang cach m/km) 9:16, nhan ban tu nns-ban-do-ha-tang
- skills/bds-sale-viral               : video nguoi noi (sale BDS, 9:16) + Resources tuy chon -> edit kieu "Het Hon Real"
                                        (tieu de 3 tang SAU DAU nguoi, sub nguc day ngang, icon 3D moc tu ban tay, SFX)
- skills/TuấnJp_Dulich_ManDoc         : link bai bao du lich + audio giong doc + Resources clip/anh (+ nhac nen) -> video quang ba
                                        du lich 9:16 (do hoa chu, hanh trinh A->B tu ve / de len clip, sub karaoke, CTA theo doi)
- skills/TuanJp_DuLich_ManNgang       : audio giong doc + Resources clip/anh (doc hay ngang, + nhac nen neu co) -> video du lich
                                        NGANG 16:9 cho YouTube (clip doc thanh the / ghep o, chuong 01-04 + ban do VN, sub karaoke,
                                        man ket Dang ky). Doc muc "TRANG THAI / VIEC TIEP THEO" trong SKILL.md truoc khi train tiep

## Cai tren may moi (PowerShell, trong thu muc du an co .claude\skills)
    git clone https://github.com/ngocson0312/SON_VIDEO_AI.git SON_VIDEO_AI
    git clone https://github.com/ngocson0312/PLA.git SON_VIDEO_AI\skills\ban-do-tien-ich-nha-dat   (repo rieng)
    git clone https://github.com/ngocson0312/nns-ha-tang-quy-hoach-tien-ich.git SON_VIDEO_AI\skills\nns-ha-tang-quy-hoach-tien-ich   (repo rieng)
    New-Item -ItemType Junction -Path .claude\skills\ban-do-quy-hoach-bds-ve-tinh -Target SON_VIDEO_AI\skills\ban-do-quy-hoach-bds-ve-tinh
    New-Item -ItemType Junction -Path .claude\skills\skill-bando-tintuc-chinhtri -Target SON_VIDEO_AI\skills\skill-bando-tintuc-chinhtri
    New-Item -ItemType Junction -Path .claude\skills\skill_video_bds_bietthu -Target SON_VIDEO_AI\skills\skill_video_bds_bietthu
    New-Item -ItemType Junction -Path .claude\skills\ban-do-tien-ich-nha-dat -Target SON_VIDEO_AI\skills\ban-do-tien-ich-nha-dat
    New-Item -ItemType Junction -Path .claude\skills\nns-ban-do-ha-tang -Target SON_VIDEO_AI\skills\nns-ban-do-ha-tang
    New-Item -ItemType Junction -Path .claude\skills\nns-ha-tang-quy-hoach-tien-ich -Target SON_VIDEO_AI\skills\nns-ha-tang-quy-hoach-tien-ich
    New-Item -ItemType Junction -Path .claude\skills\bds-sale-viral -Target SON_VIDEO_AI\skills\bds-sale-viral
    New-Item -ItemType Junction -Path .claude\skills\TuấnJp_Dulich_ManDoc -Target SON_VIDEO_AI\skills\TuấnJp_Dulich_ManDoc
    New-Item -ItemType Junction -Path .claude\skills\TuanJp_DuLich_ManNgang -Target SON_VIDEO_AI\skills\TuanJp_DuLich_ManNgang
    python -I -m pip install -r SON_VIDEO_AI\requirements.txt
    python -I -X utf8 .claude\skills\skill-bando-tintuc-chinhtri\scripts\run.py chuan-bi   (tai ~200 MB cache, lan dau)
Cap nhat: git pull trong SON_VIDEO_AI. Skill co repo rieng (ban-do-tien-ich-nha-dat, nns-ha-tang-quy-hoach-tien-ich): git pull / git push ngay trong thu muc skill do. Thu muc cache/ khong len git (tu tai lai).

## skill_video_bds_bietthu - ghi chu
- Can ffmpeg/ffprobe trong PATH.
- Model do mat det_10g.onnx (InsightFace, giay phep phi thuong mai) KHONG len git. Chep vao
  skills\skill_video_bds_bietthu\assets\models\ neu co (vd tu skill nns-edit-bds); khong co thi skill tu dung Haar OpenCV.
- rembg tu tai u2net_human_seg (~170 MB) lan dau dung hieu ung "nhan ban loe".
- File .wav trong assets\sfx\ DUOC len git (ngoai le trong .gitignore).

## bds-sale-viral - ghi chu
- Can ffmpeg/ffprobe trong PATH. Whisper large-v3 (~3 GB) tu tai lan dau, chay CPU.
- Tieu de nam SAU DAU can u2net_human_seg.onnx (175 MB, KHONG len git): de o ~\.u2net\ hoac
  skills\bds-sale-viral\assets\models\. Tai: python -I -c "from rembg import new_session; new_session('u2net_human_seg')"
- Do ban tay (icon moc tu tay): chay 1 lan / may (can mang, ~150 MB, venv RIENG ~\.bds_sale_viral\venv_tay,
  mediapipe can numpy<2 nen KHONG cai vao Python chinh):
    python -I -X utf8 .claude\skills\bds-sale-viral\scripts\run.py cai-tay
  venv nay cung do MAT + DAU (mat_mp.py, MediaPipe FaceDetection + Pose) cho luat "chu khong de mat nguoi noi"
  (chot 12/11/2026). May da cai-tay roi thi khong cai them; git pull xong la dung duoc.
- SFX trong assets\sfx\ chua ro giay phep (xem CREDITS.md) - lam thuong mai thi thay file cung ten.

## TuấnJp_Dulich_ManDoc - ghi chu
- Can ffmpeg/ffprobe trong PATH, Node.js >= 22 + Chrome hoac Edge (dung khung bang Chrome headless; Chrome cho la -> bien DLV_CHROME).
- Whisper large-v3 (~3 GB) tu tai lan dau, chay CPU. Anh HEIC iPhone: cai them pillow-heif (khong co thi tu doi qua ffmpeg).
- SFX hanh trinh (jet-flyby / xe-chay / song-nuoc .wav) tu tong hop bang scripts\tao_sfx_ht.py, da len git.
- Lenh: python -I -X utf8 .claude\skills\TuấnJp_Dulich_ManDoc\scripts\run.py quet --audio <giong> --link <bai bao> --res <Resources>

## TuanJp_DuLich_ManNgang - ghi chu
- Can ffmpeg/ffprobe trong PATH, Node.js >= 22 + Chrome hoac Edge (Chrome cho la -> bien DLN_CHROME). Kiem may: run.py cai-dat
- Whisper large-v3 (~3 GB) tu tai lan dau; khong co cublas64_12.dll thi chay CPU (~4 phut / phut audio).
- boom.wav (cu drop ten chu de) tu tong hop bang scripts\tao_sfx.py, da len git. Ban do VN: assets\khung\vn_ban_do.js (co Hoang Sa, Truong Sa).
- Lenh: python -I -X utf8 .claude\skills\TuanJp_DuLich_ManNgang\scripts\run.py quet --audio <giong> --res <Resources>
  -> Claude viet ke_hoach.json theo nghia (mau references\vi-du-4-diem-den.json) -> kiem-kh -> duyet -> dung
