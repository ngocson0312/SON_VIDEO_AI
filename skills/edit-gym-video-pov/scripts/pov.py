#!/usr/bin/env python
"""edit-gym-video-pov — video POV quay thô → bản edit viral 9:16 (cắt theo phách, zoom đập, chuyển cảnh, nhãn, sub karaoke, SFX, nhạc, -14 LUFS).

Lệnh:
  pov.py quet --video V [--work DIR]      nhận lời (Whisper) + tờ khung có nhãn giây → Claude đọc rồi viết ke_hoach.json
  pov.py dung --work DIR                  dựng từ DIR/ke_hoach.json
  pov.py kiem --work DIR                  tự kiểm file ra (độ dài, LUFS, tờ khung từng cảnh → soat.jpg)
"""
import argparse, glob, json, math, os, re, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
SK = os.path.dirname(HERE)
SFX = os.path.join(SK, "assets", "sfx")
FONTS = os.path.join(SK, "assets", "fonts")
W, H, FPS = 1080, 1920, 30
YEL = "&H0000D8FF"   # #FFD800 (ASS = BGR)
WHITE = "&H00FFFFFF"
BLACK = "&H00000000"
RED = "&H003030FF"

SFX_FILES = {
    "swoosh": "swoosh.mp3", "swoosh2": "quick-swoosh.mp3", "whoosh": "whoosh.wav", "pop": "pop.mp3",
    "pop2": "pop-2.mp3", "ting": "ting.wav", "ting2": "quick-ting.mp3", "riser": "riser-metallic.mp3",
    "flash": "camera-flash-1.wav", "shutter": "camera-shutter-1.wav", "punch": "punch.mp3",
    "glitch": "glitch.mp3", "tada": "ta-da.mp3", "click": "click-button.mp3", "ding": "ding.mp3",
    "buildup": "build-up.mp3",
}
SFX_VOL = {"swoosh": 0.75, "swoosh2": 0.75, "whoosh": 0.6, "pop": 0.9, "pop2": 0.9, "ting": 0.7, "ting2": 0.7,
           "riser": 0.55, "flash": 0.55, "shutter": 0.7, "punch": 0.8, "glitch": 0.6, "tada": 0.7,
           "click": 0.8, "ding": 0.7, "buildup": 0.5}


def run(cmd, **kw):
    r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", **kw)
    if r.returncode != 0:
        sys.exit("⛔ lệnh lỗi: " + " ".join(cmd[:4]) + " …\n" + r.stderr[-1800:])
    return r


def probe_dur(p):
    r = run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=nk=1:nw=1", p])
    return float(r.stdout.strip())


# ───────────────────────── quét ─────────────────────────
def cmd_quet(a):
    v = os.path.abspath(a.video)
    work = a.work or os.path.splitext(v)[0] + "_pov_work"
    os.makedirs(work, exist_ok=True)
    wav = os.path.join(work, "a16.wav")
    run(["ffmpeg", "-v", "error", "-y", "-i", v, "-ac", "1", "-ar", "16000", wav])
    dur = probe_dur(v)
    print(f"video {dur:.1f}s → {work}")
    wj = os.path.join(work, "words.json")
    if not os.path.exists(wj):
        from faster_whisper import WhisperModel
        m = WhisperModel(a.model, device="cpu", compute_type="int8")
        segs, _ = m.transcribe(wav, language="vi", word_timestamps=True, vad_filter=False, beam_size=5,
                               no_speech_threshold=0.95, log_prob_threshold=-2.0, condition_on_previous_text=False,
                               initial_prompt=a.prompt)
        out = []
        for s in segs:
            out.append({"s": s.start, "e": s.end, "t": s.text.strip(),
                        "w": [(x.word.strip(), round(x.start, 2), round(x.end, 2), round(x.probability, 2)) for x in s.words]})
        json.dump(out, open(wj, "w", encoding="utf-8"), ensure_ascii=False)
    segs = json.load(open(wj, encoding="utf-8-sig"))
    with open(os.path.join(work, "loi_doc.txt"), "w", encoding="utf-8") as f:
        for o in segs:
            f.write(f"{o['s']:6.1f} {o['e']:6.1f}  {o['t']}\n")
    print("lời → loi_doc.txt (⚠ Whisper hay BỊA 'subscribe…' ở đoạn im / ồn — đối chiếu RMS + khung hình)")
    # RMS mỗi giây
    import numpy as np, wave
    f = wave.open(wav)
    x = np.frombuffer(f.readframes(f.getnframes()), dtype=np.int16).astype(float)
    rms = [int(20 * math.log10(math.sqrt(np.mean(x[i * 16000:(i + 1) * 16000] ** 2)) + 1)) for i in range(len(x) // 16000)]
    open(os.path.join(work, "rms.txt"), "w").write(" ".join(f"{i}:{r}" for i, r in enumerate(rms)))
    # tờ khung có nhãn giây (1 khung / 1 s, 28 khung / tờ)
    from PIL import Image, ImageDraw, ImageFont
    fr = os.path.join(work, "fr")
    os.makedirs(fr, exist_ok=True)
    for p in glob.glob(fr + "/*.jpg"):
        os.remove(p)
    run(["ffmpeg", "-v", "error", "-y", "-i", v, "-vf", "fps=1,scale=240:-1", os.path.join(fr, "%04d.jpg")])
    fs = sorted(glob.glob(fr + "/*.jpg"))
    font = ImageFont.truetype("arialbd.ttf", 30) if os.name == "nt" else ImageFont.load_default()
    per = 28
    for k in range(math.ceil(len(fs) / per)):
        sub = fs[k * per:(k + 1) * per]
        im = Image.new("RGB", (7 * 240, 4 * 427))
        for i, p in enumerate(sub):
            t = Image.open(p)
            d = ImageDraw.Draw(t)
            d.rectangle((0, 0, 64, 34), fill=(0, 0, 0))
            d.text((4, 2), str(k * per + i), fill=(255, 230, 0), font=font)
            im.paste(t, ((i % 7) * 240, (i // 7) * 427))
        im.save(os.path.join(work, f"to_khung_{k + 1}.jpg"), quality=80)
    print(f"tờ khung: {os.path.join(work, 'to_khung_*.jpg')} (nhãn vàng = giây nguồn)")
    print("→ MỞ từng tờ khung + đọc loi_doc.txt, rồi viết ke_hoach.json (xem references/ke_hoach_mau.json)")


# ───────────────────────── lịch cảnh ─────────────────────────
def lap_lich(plan):
    B = 60.0 / plan.get("bpm", 100)
    sc = plan["scenes"]
    n = len(sc)
    TR = {"cut": 0.034}
    ov = []  # chồng lấn giữa cảnh i và i+1
    for i in range(n - 1):
        t = sc[i + 1].get("trans", "slideleft")
        ov.append(TR["cut"] if t == "cut" else sc[i + 1].get("ov", 0.24))
    S = [0.0]
    for i in range(n - 1):
        S.append(S[-1] + sc[i]["beats"] * B)
    for i, s in enumerate(sc):
        lo = ov[i - 1] / 2 if i > 0 else 0.0
        hi = ov[i] / 2 if i < n - 1 else 0.0
        s["_lo"], s["_hi"] = lo, hi
        s["_out0"] = S[i] - lo                      # lúc cảnh bắt đầu phát (đã gồm phần chồng)
        s["_d"] = s["beats"] * B + lo + hi          # thời lượng phát
        s["_sp"] = s.get("speed", 1.0)
        s["_a"] = s["src"] - lo * s["_sp"]          # giây nguồn bắt đầu
        if s["_a"] < 0:
            s["_a"] = 0
    total = S[-1] + sc[-1]["beats"] * B + plan.get("duoi", 0.5)
    sc[-1]["_d"] += plan.get("duoi", 0.5)
    cta = plan.get("cta")
    if cta:
        plan["_cta_t0"] = total - 0.2
        total = plan["_cta_t0"] + cta.get("dur", 4.6)
        sc[-1]["_d"] += cta.get("dur", 4.6) - 0.2
    return B, S, ov, total


def out_time(sc, ts):
    for s in sc:
        if s["_a"] - 1e-3 <= ts <= s["_a"] + s["_d"] * s["_sp"] + 1e-3:
            return s["_out0"] + (ts - s["_a"]) / s["_sp"]
    return None


sys.path.insert(0, HERE)
from ass_dep import build_ass as _build_ass, ts  # noqa: E402


def build_ass(plan, sc, S, B, total, words, path):
    _build_ass(plan, sc, S, B, total, words, path, out_time)


def load_words(work, sua):
    wj = os.path.join(work, "words.json")
    segs = json.load(open(wj, encoding="utf-8-sig"))
    out = []
    for o in segs:
        for (w, a0, a1, p) in o["w"]:
            w = re.sub(r"[^\wÀ-ỹ]", "", w, flags=re.U)
            if w:
                out.append([w, a0, a1])
    # sửa lời theo cụm: "chữ sai": "chữ đúng" (so khớp chuỗi từ liên tiếp)
    for bad, good in (sua or {}).items():
        bw = bad.lower().split()
        i = 0
        while i <= len(out) - len(bw):
            if [x[0].lower() for x in out[i:i + len(bw)]] == bw:
                gw = good.split()
                a0, a1 = out[i][1], out[i + len(bw) - 1][2]
                step = (a1 - a0) / max(1, len(gw))
                out[i:i + len(bw)] = [[g, a0 + k * step, a0 + (k + 1) * step] for k, g in enumerate(gw)]
                i += len(gw)
            else:
                i += 1
    return out


def lop_phu(plan, sc, B, work, total):
    """Sinh PNG + thông số phủ cho tiêu đề / nhãn / huy hiệu."""
    import overlays as ovl
    out = []
    ti = plan.get("title")
    if ti:
        t0, t1 = plan.get("title_t", [0.12, 3.9])
        tf = ovl.title_flat if plan.get("title_style", "phang") == "phang" else ovl.title_card
        p, w_, h_ = tf(ti[1:], plan.get("title_hi", []), pov=ti[0], path=os.path.join(work, "ov_title.png"))
        out.append({"png": p, "t0": t0, "t1": t1, "dur": t1 - t0, "x": 0, "y": plan.get("title_y", 760), "w": w_, "h": h_, "pop": True})
    for i, s in enumerate(sc):
        a0 = s["_out0"] + s["_lo"]
        a1 = s["_out0"] + s["_d"] - s["_hi"] - 0.05
        lb = s.get("label")
        if lb:
            t0 = a0 + s.get("label_dt", 0.12)
            t1 = min(a1, t0 + s.get("label_dur", 3.2))
            p, w_, h_, pad = ovl.pill(lb, path=os.path.join(work, f"ov_l{i}.png"))
            out.append({"png": p, "t0": t0, "t1": t1, "dur": t1 - t0, "x": 64 - pad, "y": 250 - pad, "w": w_, "h": h_, "pop": False})
        bg = s.get("badge")
        if bg:
            t0 = a0 + 0.1
            p, w_, h_, pad = ovl.pill(bg, size=52, c1=ovl.R1, c2=ovl.R2, txt=ovl.WHITE, icon="ff", path=os.path.join(work, f"ov_b{i}.png"))
            out.append({"png": p, "t0": t0, "t1": a1, "dur": a1 - t0, "x": 64 - pad, "y": (250 if not lb else 420) - pad, "w": w_, "h": h_, "pop": False})
    return out


# ───────────────────────── dựng ─────────────────────────
def cmd_dung(a):
    work = os.path.abspath(a.work)
    plan = json.load(open(os.path.join(work, "ke_hoach.json"), encoding="utf-8-sig"))
    video = os.path.abspath(plan["video"])
    sc = plan["scenes"]
    B, S, ov, total = lap_lich(plan)
    n = len(sc)
    # nhãn theo giây nguồn: plan["labels"] = [[giây, "CHỮ"], ...] → gắn vào cảnh chứa giây đó
    for (lt, ltxt) in plan.get("labels", []):
        for s_ in sc:
            if s_["src"] - 1e-6 <= lt < s_["src"] + s_["beats"] * B * s_["_sp"]:
                s_["label"] = ltxt
                s_["label_dt"] = max(0.12, (lt - s_["src"]) / s_["_sp"] + 0.05)
                break
    words = load_words(work, plan.get("sua"))
    build_ass(plan, sc, S, B, total, words, os.path.join(work, "pov.ass"))

    # nhạc
    nhac = plan.get("nhac", "mau")
    nhac_path = None
    if nhac and nhac != "khong":
        if nhac == "mau":
            nhac_path = os.path.join(work, "nhac_mau.wav")
            run([sys.executable, os.path.join(HERE, "nhac_mau.py"), "--bpm", str(plan.get("bpm", 100)),
                 "--giay", str(math.ceil(total) + 1), "--out", nhac_path])
        else:
            nhac_path = os.path.abspath(nhac)

    # ---- video ----
    fc = []
    for i, s in enumerate(sc):
        d, aa, sp = s["_d"], s["_a"], s["_sp"]
        z = s.get("zoom", "punch")
        slow = s.get("zslow", {"in": 0.12, "out": -0.0, "punch": 0.07, "none": 0.0}.get(z, 0.07))
        punch = {"punch": 0.16, "in": 0.0, "out": 0.0, "none": 0.0}.get(z, 0.16)
        base = 1.0 + (0.12 if z == "out" else 0.0)
        if z == "out":
            expr = f"({base}-0.12*t/{d:.3f})"
        else:
            expr = f"({s.get('zbase', 1.0)}*(1+{slow}*t/{d:.3f}+{punch}*exp(-8*t)))"
        fx, fy = s.get("tam", [0.5, 0.5])
        chain = (f"[0:v]trim=start={aa:.3f}:duration={d * sp:.3f},setpts=(PTS-STARTPTS)/{sp},fps={FPS},"
                 f"scale={W * 2}:-2:flags=bicubic,"
                 f"scale=w='trunc({W * 2}*{expr}/2)*2':h=-2:eval=frame:flags=bilinear,"
                 f"crop={W * 2}:{H * 2}:x='(iw-{W * 2})*{fx}':y='(ih-{H * 2})*{fy}',scale={W}:{H}:flags=lanczos,"
                 f"eq=contrast=1.07:saturation=1.22,unsharp=5:5:0.5,setsar=1,format=yuv420p,settb=AVTB[v{i}]")
        if plan.get("cta") and i == n - 1:
            chain = chain.replace(f"fps={FPS},", f"fps={FPS},tpad=stop_mode=clone:stop_duration={plan['cta'].get('dur', 4.6) + 2:.2f},", 1)
        fc.append(chain)
    cur = "v0"
    L = sc[0]["_d"]
    for i in range(1, n):
        t = sc[i].get("trans", "slideleft")
        o = ov[i - 1]
        xt = "fade" if t == "cut" else t
        off = L - o
        fc.append(f"[{cur}][v{i}]xfade=transition={xt}:duration={o:.3f}:offset={off:.3f}[x{i}]")
        cur = f"x{i}"
        L += sc[i]["_d"] - o
    SUBLINE = (f"subtitles=pov.ass:fontsdir='{FONTS.replace(chr(92), '/').replace(':', chr(92) + ':')}'")
    vcur = cur

    # ---- âm thanh ----
    inputs = ["-i", video]
    idx = 1
    music_idx = None
    if nhac_path:
        inputs += ["-i", nhac_path]
        music_idx = idx; idx += 1
    voice, amb = [], []
    for i, s in enumerate(sc):
        d, aa, sp = s["_d"], s["_a"], s["_sp"]
        ms = int(round(s["_out0"] * 1000))
        isv = s.get("voice", False)
        g = s.get("vol", 1.15 if isv else 0.22)
        f = (f"[0:a]atrim=start={aa:.3f}:duration={d * sp:.3f},asetpts=PTS-STARTPTS"
             + (f",atempo={sp}" if sp != 1 else "")
             + f",afade=t=in:d=0.05,afade=t=out:st={max(0, d - 0.08):.3f}:d=0.08,volume={g},adelay={ms}|{ms}[a{i}]")
        fc.append(f)
        (voice if isv else amb).append(f"[a{i}]")
    def mix(lst, name):
        if not lst:
            fc.append(f"anullsrc=r=48000:cl=stereo,atrim=0:{total:.2f}[{name}]")
        elif len(lst) == 1:
            fc.append(f"{lst[0]}anull[{name}]")
        else:
            fc.append("".join(lst) + f"amix=inputs={len(lst)}:normalize=0:duration=longest[{name}]")
    mix(voice, "vbus"); mix(amb, "abus")
    fc.append("[vbus]asplit=2[vk][vm]")
    parts = ["[vm]", "[abus]"]
    if music_idx is not None:
        mg = plan.get("nhac_vol", 0.25)
        fc.append(f"[{music_idx}:a]aresample=48000,aformat=channel_layouts=stereo,volume={mg},atrim=0:{total:.2f}[mu]")
        fc.append("[mu][vk]sidechaincompress=threshold=0.01:ratio=12:attack=10:release=400[mud]")
        parts.append("[mud]")
    else:
        fc.append("[vk]anull[vk2]")
    # SFX
    sfx = []
    for i in range(1, n):
        t = sc[i].get("trans", "slideleft")
        T = S[i]
        if t not in ("cut", "fade"):
            sfx.append((("swoosh" if i % 2 else "swoosh2") if t != "fadewhite" else "flash", T - 0.2))
        elif sc[i].get("sfx_cut"):
            sfx.append(("punch", T - 0.03))
    for i, s in enumerate(sc):
        for nm, dt in s.get("sfx", []):
            sfx.append((nm, s["_out0"] + s["_lo"] + dt))
        if s.get("label") and not s.get("no_label_sfx"):
            sfx.append(("pop", s["_out0"] + s["_lo"] + s.get("label_dt", 0.12)))
    if plan.get("title"):
        sfx.append(("pop2", plan.get("title_t", [0.12, 3.7])[0]))
    if plan.get("cta"):
        t0c = plan["_cta_t0"]
        sfx += [("swoosh2", t0c), ("pop2", t0c + 0.12)] + [("click", t0c + 1.30)] + [("ting2", t0c + 1.32)]
    sfx += [tuple(x) for x in plan.get("sfx", [])]
    sfx = [(nm, max(0, t)) for nm, t in sfx if nm in SFX_FILES and t < total]
    sfx.sort(key=lambda x: x[1])
    labels = []
    for k, (nm, t) in enumerate(sfx):
        inputs += ["-i", os.path.join(SFX, SFX_FILES[nm])]
        ms = int(round(t * 1000))
        fc.append(f"[{idx}:a]aresample=48000,aformat=channel_layouts=stereo,volume={SFX_VOL.get(nm, 0.7)},adelay={ms}|{ms}[s{k}]")
        labels.append(f"[s{k}]"); idx += 1
    if labels:
        fc.append("".join(labels) + f"amix=inputs={len(labels)}:normalize=0:duration=longest[sfxb]")
        parts.append("[sfxb]")
    fc.append("[vm]aresample=48000,aformat=channel_layouts=stereo[vst]")
    parts[0] = "[vst]"
    fc.append("".join(parts) + f"amix=inputs={len(parts)}:normalize=0:duration=longest,atrim=0:{total:.2f},"
              f"aresample=48000[aout]")

    # ---- lớp bubble / tiêu đề PNG (PIL) phủ lên rồi mới chồng sub ----
    ovs = lop_phu(plan, sc, B, work, total)
    ovs = [o for o in ovs if o['dur'] >= 0.5]
    for k, o in enumerate(ovs):
        inputs += ["-loop", "1", "-framerate", str(FPS), "-t", f"{o['dur']:.3f}", "-i", o["png"]]
        f = f"[{idx}:v]format=rgba,fade=t=in:st=0:d=0.08:alpha=1,fade=t=out:st={max(0, o['dur'] - 0.16):.3f}:d=0.16:alpha=1"
        if o["pop"]:
            f += ",scale=w='trunc(iw*(1+0.2*exp(-9*t))/2)*2':h=-2:eval=frame"
        f += f",setpts=PTS+{o['t0']:.3f}/TB[ov{k}]"
        fc.append(f)
        if o["pop"]:
            xe = f"{o['x'] + o['w'] / 2:.1f}-w/2"; ye = f"{o['y'] + o['h'] / 2:.1f}-h/2"
        else:
            xe = f"{o['x']}-540*pow(max(0,1-(t-{o['t0']:.3f})/0.3),2)"; ye = f"{o['y']}"
        fc.append(f"[{vcur}][ov{k}]overlay=x='{xe}':y='{ye}':eof_action=pass:enable='between(t,{o['t0']:.3f},{o['t1']:.3f})'[vo{k}]")
        vcur = f"vo{k}"; idx += 1
    if plan.get("cta"):
        c = plan["cta"]; t0c = plan["_cta_t0"]; dc = c.get("dur", 4.6)
        mov = os.path.join(work, "ov_cta.mov")
        run([sys.executable, os.path.join(HERE, "cta3d.py"), "--dur", f"{dc:.2f}", "--y", str(c.get("y", 930)), "--out", mov])
        inputs += ["-i", mov]
        # nền cuối: làm nhoè + tối (chỉ nút + tay là chủ thể)
        fc.append(f"[{vcur}]split[cb1][cb2];[cb2]gblur=sigma=22,eq=brightness=-0.16:saturation=0.85[cbl];"
                  f"[cb1][cbl]overlay=enable='gte(t,{t0c:.2f})'[vdim]")
        fc.append(f"[{idx}:v]format=rgba,setpts=PTS+{t0c:.3f}/TB[ovcta]")
        fc.append(f"[vdim][ovcta]overlay=x=0:y=0:eof_action=pass:enable='gte(t,{t0c:.2f})'[vcta]")
        vcur = "vcta"; idx += 1
    fc.append(f"[{vcur}]" + SUBLINE + "[vout]")

    script = os.path.join(work, "filter.txt")
    open(script, "w", encoding="utf-8").write(";\n".join(fc))
    out = plan.get("out") or os.path.splitext(video)[0] + "_POV.mp4"
    base_out = out; k = 2
    while os.path.exists(out) and not a.ghi_de:
        out = os.path.splitext(base_out)[0] + f"_ban{k}.mp4"; k += 1
    cmd = ["ffmpeg", "-v", "error", "-y"] + inputs + ["-/filter_complex", "filter.txt",
           "-map", "[vout]", "-map", "[aout]", "-t", f"{total:.2f}", "-c:v", "libx264", "-crf", "18", "-preset", "medium",
           "-pix_fmt", "yuv420p", "-r", str(FPS), "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", out]
    print(f"dựng {n} cảnh, {total:.1f}s, {len(sfx)} SFX …")
    r = subprocess.run(cmd, cwd=work, text=True, encoding="utf-8", errors="replace")
    if r.returncode:
        sys.exit("⛔ ffmpeg lỗi")
    chuan_am(out)
    json.dump({"out": out, "total": total, "S": S, "scenes": [{k: v for k, v in s.items() if k.startswith("_") or k in ("label", "src", "beats", "trans")} for s in sc]},
              open(os.path.join(work, "last_build.json"), "w", encoding="utf-8"), ensure_ascii=False)
    print("✅", out)


def chuan_am(out, I=-14.0, TP=-1.5):
    """loudnorm 2 lượt (tuyến tính) trên tiếng đã trộn rồi ghép lại, hình giữ nguyên."""
    r = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", out, "-vn", "-af",
                        f"loudnorm=I={I}:TP={TP}:LRA=11:print_format=json", "-f", "null", "-"],
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    js = json.loads(r.stderr[r.stderr.rfind("{"):r.stderr.rfind("}") + 1])
    af = (f"loudnorm=I={I}:TP={TP}:LRA=11:measured_I={js['input_i']}:measured_TP={js['input_tp']}:"
          f"measured_LRA={js['input_lra']}:measured_thresh={js['input_thresh']}:offset={js['target_offset']}:linear=true,"
          f"alimiter=limit=0.68:attack=2:release=50:level=disabled")
    tmp = out + ".tmp.mp4"
    run(["ffmpeg", "-v", "error", "-y", "-i", out, "-map", "0:v", "-map", "0:a", "-c:v", "copy", "-af", af,
         "-c:a", "aac", "-b:a", "256k", "-ar", "48000", "-movflags", "+faststart", tmp])
    os.replace(tmp, out)


# ───────────────────────── nháp toàn video ─────────────────────────
def cmd_nhap(a):
    """Lập ke_hoach.json NHÁP phủ TOÀN BỘ video (không bỏ nội dung): cảnh liên tục theo phách, tua nhanh đoạn chết,
    cảnh có lời giữ tiếng, chuyển cảnh đẹp ở đoạn đi tham quan, jump-cut zoom luân phiên ở đoạn ngồi nói."""
    work = os.path.abspath(a.work)
    v = os.path.abspath(a.video)
    D = probe_dur(v)
    bpm = a.bpm
    B = 60.0 / bpm
    segs = json.load(open(os.path.join(work, "words.json"), encoding="utf-8-sig"))
    good, speech = [], []
    for o in segs:
        if re.search(r"subscribe|lalaschool|đăng ký kênh", o["t"], re.I):
            continue
        speech.append((o["s"], o["e"]))
        ps = [w[3] for w in o["w"]] or [0]
        if sum(ps) / len(ps) >= 0.7 and min(ps) >= 0.4 and len(o["w"]) >= 2:
            good.append([round(o["s"] - 0.05, 2), round(o["e"] + 0.05, 2)])
    if a.giu:
        keep = json.loads(a.giu)          # [[giây_a, giây_b], ...] đoạn GIỮ, phần còn lại bị cắt
        scenes = []
        for (ka, kb) in keep:
            nb = max(2, round((kb - ka) / B))
            parts, left = [], nb
            while left > 0:               # đoạn dài chia ≤ 14 phách, nối hoà tan (liền mạch)
                p = left if left <= 14 else (left // 2 if left < 20 else 12)
                parts.append(p); left -= p
            t = ka
            for pi, pb in enumerate(parts):
                span = pb * B
                has = any(s0 < t + span and e0 > t for (s0, e0) in speech)
                sc = {"src": round(t, 3), "beats": pb, "voice": bool(has), "zoom": "in", "zslow": 0.05}
                if pi % 2:
                    sc["zbase"] = 1.12; sc["tam"] = [0.55, 0.55]
                if scenes:
                    sc["trans"] = "fade"; sc["ov"] = 0.5
                scenes.append(sc); t += span
        plan = {"video": v, "out": os.path.splitext(v)[0] + "_POV.mp4", "bpm": bpm, "nhac": "mau", "nhac_vol": 0.1,
                "title": ["POV:", "BẠN LÀ HLV ĐÓN KHÁCH", "VÀO PHÒNG TẬP"], "title_hi": ["HLV"], "title_y": 215,
                "sub": good, "labels": [], "rec_hud": False, "scenes": scenes}
        json.dump(plan, open(os.path.join(work, "ke_hoach.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        print(f"giữ {sum(b - a_ for a_, b in keep):.0f}s / {D:.0f}s, {len(scenes)} cảnh → ke_hoach.json")
        return
    slow = [tuple(x) for x in (json.loads(a.tua) if a.tua else [])]   # [[a,b,speed],...]
    talk0 = a.ngoi_noi
    scenes, t, k = [], 0.0, 0
    cyc_tour, cyc_talk = [8, 6, 10, 6, 8, 10], [10, 12, 10, 12]
    fancy = ["slideleft", "zoomin", "fadewhite", "slideup", "radial", "slideright", "circleopen"]
    fi = 0
    while t < D - 0.8:
        sp = 1.0
        for (x0, x1, sv) in slow:
            if x0 <= t < x1:
                sp = sv
        intalk = talk0 is not None and t >= talk0
        beats = (cyc_talk if intalk else cyc_tour)[k % (len(cyc_talk) if intalk else len(cyc_tour))]
        if sp > 1:
            beats = max(2, beats - 1)
        span = beats * B * sp
        if t + span > D - 0.2:
            beats = max(2, int((D - 0.2 - t) / (B * sp)))
            span = beats * B * sp
        has = any(s0 < t + span and e0 > t for (s0, e0) in speech)
        sc = {"src": round(t, 3), "beats": beats, "voice": bool(has and sp == 1.0)}
        if sp > 1:
            sc["speed"] = sp; sc["badge"] = f"TUA NHANH x{sp:g}"; sc["zoom"] = "none"
        else:
            # ÊM: cảnh dài, zoom chậm, nối bằng hoà tan — KHÔNG cắt cứng / đập zoom (khách 18/11: "giật cục, khó chịu")
            sc["zoom"] = "in"; sc["zslow"] = 0.05
            if intalk and k % 2:
                sc["zbase"] = 1.16; sc["tam"] = [0.6, 0.55]
        if scenes:
            sc["trans"] = "fade"; sc["ov"] = 0.5
        scenes.append(sc)
        t += span; k += 1
    plan = {"video": v, "out": os.path.splitext(v)[0] + "_POV.mp4", "bpm": bpm, "nhac": "mau",
            "title": ["POV:", "BẠN LÀ HLV ĐÓN KHÁCH", "VÀO PHÒNG TẬP"], "title_hi": ["HLV"], "title_y": 860,
            "sub": good, "labels": [], "scenes": scenes}
    json.dump(plan, open(os.path.join(work, "ke_hoach.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"nháp {len(scenes)} cảnh phủ {D:.0f}s, {len(good)} đoạn sub tin cậy → ke_hoach.json (sửa title/labels/chuyển cảnh theo nghĩa)")


# ───────────────────────── kiểm ─────────────────────────
def cmd_kiem(a):
    work = os.path.abspath(a.work)
    lb = json.load(open(os.path.join(work, "last_build.json"), encoding="utf-8"))
    out = lb["out"]
    d = probe_dur(out)
    r = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", out, "-af", "ebur128=peak=true", "-f", "null", "-"],
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    m = re.findall(r"I:\s+(-?[\d.]+) LUFS", r.stderr)
    tp = re.findall(r"Peak:\s+(-?[\d.]+) dBFS", r.stderr)
    ok = True
    print(f"độ dài {d:.2f}s (kế hoạch {lb['total']:.2f}s)")
    if m:
        lu = float(m[-1]); print(f"loudness {lu:.1f} LUFS", "✅" if abs(lu + 14) <= 1 else "⛔"); ok &= abs(lu + 14) <= 1
    if tp:
        print(f"true peak {tp[-1]} dBFS", "✅" if float(tp[-1]) <= -0.9 else "⛔")
    # tờ soát: mỗi cảnh 1 khung giữa + 1 khung ngay sau điểm cắt
    from PIL import Image, ImageDraw, ImageFont
    ts_ = []
    for i, s in enumerate(lb["scenes"]):
        t0 = lb["S"][i]
        ts_ += [t0 + 0.12, t0 + s["beats"] * 60 / 100 * 0.6 if False else t0 + 0.9]
    ts_ = [min(t, d - 0.05) for t in ts_][:28]
    tmp = os.path.join(work, "soat_fr"); os.makedirs(tmp, exist_ok=True)
    font = ImageFont.truetype("arialbd.ttf", 26) if os.name == "nt" else ImageFont.load_default()
    im = Image.new("RGB", (7 * 240, 4 * 427))
    for k, t in enumerate(ts_):
        p = os.path.join(tmp, f"{k:02d}.jpg")
        run(["ffmpeg", "-v", "error", "-y", "-ss", f"{t:.2f}", "-i", out, "-frames:v", "1", "-vf", "scale=240:-1", p])
        x = Image.open(p); dr = ImageDraw.Draw(x)
        dr.rectangle((0, 0, 70, 30), fill=(0, 0, 0)); dr.text((4, 1), f"{t:.1f}s", fill=(255, 230, 0), font=font)
        im.paste(x, ((k % 7) * 240, (k // 7) * 427))
    im.save(os.path.join(work, "soat.jpg"), quality=82)
    print("tờ soát:", os.path.join(work, "soat.jpg"), "— mở soi chữ không đè mặt, cắt đúng phách")


def main():
    ap = argparse.ArgumentParser()
    sp = ap.add_subparsers(dest="c", required=True)
    q = sp.add_parser("quet"); q.add_argument("--video", required=True); q.add_argument("--work")
    q.add_argument("--model", default="large-v3"); q.add_argument("--prompt", default="")
    d = sp.add_parser("dung"); d.add_argument("--work", required=True); d.add_argument("--ghi-de", action="store_true")
    n_ = sp.add_parser("nhap"); n_.add_argument("--work", required=True); n_.add_argument("--video", required=True)
    n_.add_argument("--bpm", type=float, default=100); n_.add_argument("--tua", help='[[a,b,tốc độ],...] giây nguồn tua nhanh')
    n_.add_argument("--giu", help='[[a,b],...] giây nguồn GIỮ LẠI (cắt phần còn lại)'); n_.add_argument("--ngoi-noi", type=float, default=None, help="giây nguồn bắt đầu đoạn ngồi nói tĩnh")
    k = sp.add_parser("kiem"); k.add_argument("--work", required=True)
    a = ap.parse_args()
    {"quet": cmd_quet, "dung": cmd_dung, "kiem": cmd_kiem, "nhap": cmd_nhap}[a.c](a)


if __name__ == "__main__":
    main()
