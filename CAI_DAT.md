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
    python -I -m pip install -r SON_VIDEO_AI\requirements.txt
    python -I -X utf8 .claude\skills\skill-bando-tintuc-chinhtri\scripts\run.py chuan-bi   (tai ~200 MB cache, lan dau)
Cap nhat: git pull trong SON_VIDEO_AI. Skill co repo rieng (ban-do-tien-ich-nha-dat, nns-ha-tang-quy-hoach-tien-ich): git pull / git push ngay trong thu muc skill do. Thu muc cache/ khong len git (tu tai lai).

## skill_video_bds_bietthu - ghi chu
- Can ffmpeg/ffprobe trong PATH.
- Model do mat det_10g.onnx (InsightFace, giay phep phi thuong mai) KHONG len git. Chep vao
  skills\skill_video_bds_bietthu\assets\models\ neu co (vd tu skill nns-edit-bds); khong co thi skill tu dung Haar OpenCV.
- rembg tu tai u2net_human_seg (~170 MB) lan dau dung hieu ung "nhan ban loe".
- File .wav trong assets\sfx\ DUOC len git (ngoai le trong .gitignore).
