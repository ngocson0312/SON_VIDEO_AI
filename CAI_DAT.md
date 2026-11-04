# SON_VIDEO_AI - skill video (Claude Code)

- skills/ban-do-quy-hoach-bds-ve-tinh : audio tin quy hoach/BDS -> video ban do ve tinh 9:16
- skills/skill-bando-tintuc-chinhtri  : audio tin tuc/dia chinh tri -> video ban do 3D 9:16
- skills/skill_video_bds_bietthu      : video nguoi noi (sale BDS) + Resources (anh/video du an) -> video kieu "Biet thu rung tang ham" 9:16
                                        (doc skills/skill_video_bds_bietthu/SKILL.md, muc "VIEC DANG DO" truoc khi lam)

## Cai tren may moi (PowerShell, trong thu muc du an co .claude\skills)
    git clone https://github.com/ngocson0312/SON_VIDEO_AI.git SON_VIDEO_AI
    New-Item -ItemType Junction -Path .claude\skills\ban-do-quy-hoach-bds-ve-tinh -Target SON_VIDEO_AI\skills\ban-do-quy-hoach-bds-ve-tinh
    New-Item -ItemType Junction -Path .claude\skills\skill-bando-tintuc-chinhtri -Target SON_VIDEO_AI\skills\skill-bando-tintuc-chinhtri
    New-Item -ItemType Junction -Path .claude\skills\skill_video_bds_bietthu -Target SON_VIDEO_AI\skills\skill_video_bds_bietthu
    python -I -m pip install -r SON_VIDEO_AI\requirements.txt
    python -I -X utf8 .claude\skills\skill-bando-tintuc-chinhtri\scripts\run.py chuan-bi   (tai ~200 MB cache, lan dau)
Cap nhat: git pull trong SON_VIDEO_AI. Thu muc cache/ khong len git (tu tai lai).

## skill_video_bds_bietthu - ghi chu
- Can ffmpeg/ffprobe trong PATH.
- Model do mat det_10g.onnx (InsightFace, giay phep phi thuong mai) KHONG len git. Chep vao
  skills\skill_video_bds_bietthu\assets\models\ neu co (vd tu skill nns-edit-bds); khong co thi skill tu dung Haar OpenCV.
- rembg tu tai u2net_human_seg (~170 MB) lan dau dung hieu ung "nhan ban loe".
- File .wav trong assets\sfx\ DUOC len git (ngoai le trong .gitignore).
