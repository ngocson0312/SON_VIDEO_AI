# SON_VIDEO_AI - 2 skill video ban do (Claude Code)

- skills/ban-do-quy-hoach-bds-ve-tinh : audio tin quy hoach/BDS -> video ban do ve tinh 9:16
- skills/skill-bando-tintuc-chinhtri  : audio tin tuc/dia chinh tri -> video ban do 3D 9:16

## Cai tren may moi (PowerShell, trong thu muc du an co .claude\skills)
    git clone https://github.com/ngocson0312/SON_VIDEO_AI.git SON_VIDEO_AI
    New-Item -ItemType Junction -Path .claude\skills\ban-do-quy-hoach-bds-ve-tinh -Target SON_VIDEO_AI\skills\ban-do-quy-hoach-bds-ve-tinh
    New-Item -ItemType Junction -Path .claude\skills\skill-bando-tintuc-chinhtri -Target SON_VIDEO_AI\skills\skill-bando-tintuc-chinhtri
    python -I -m pip install -r SON_VIDEO_AI\requirements.txt
    python -I -X utf8 .claude\skills\skill-bando-tintuc-chinhtri\scripts\run.py chuan-bi   (tai ~200 MB cache, lan dau)
Cap nhat: git pull trong SON_VIDEO_AI. Thu muc cache/ khong len git (tu tai lai).
