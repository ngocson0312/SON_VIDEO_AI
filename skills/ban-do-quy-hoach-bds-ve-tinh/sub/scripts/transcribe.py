# -*- coding: utf-8 -*-
"""Nhan dang loi noi ra chu, CO MOC THOI GIAN TUNG TU (word timestamps).

    python scripts/transcribe.py --video <video> --out <video_ra.mp4> \
        [--model large-v3] [--language vi] [--force]

Ket qua duoc CACHE canh --out (<stem>.words.json) nen chay lai gan nhu tuc thi.
Muon nhan dang lai tu dau: them --force.
"""
from __future__ import annotations

import argparse
import os
import shutil
import sys
import tempfile
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import nnscommon as C  # noqa: E402

CACHE_VERSION = 2


def extract_wav(video, dest):
    """Tach tieng ra wav 16 kHz mono — dinh dang Whisper an vao truc tiep."""
    cmd = ["ffmpeg", "-v", "error", "-y", "-i", video, "-vn",
           "-ac", "1", "-ar", "16000", "-c:a", "pcm_s16le", dest]
    C.run(cmd, what="tach tieng ra wav")
    if not os.path.isfile(dest) or os.path.getsize(dest) < 1024:
        C.die("tach tieng that bai, file wav rong: %s" % dest)
    return dest


def load_cache(path, video, model, language):
    if not os.path.isfile(path):
        return None
    try:
        data = C.read_json(path)
    except Exception:
        return None
    if data.get("cache_version") != CACHE_VERSION:
        return None
    if data.get("model") != model or data.get("language") != language:
        return None
    if os.path.abspath(data.get("video", "")) != os.path.abspath(video):
        return None
    try:
        if os.path.getmtime(video) > data.get("video_mtime", 0) + 1:
            return None    # video da bi sua sau khi nhan dang -> khong dung nua
    except OSError:
        return None
    return data


def doc_wav(path):
    """wav PCM 16-bit mono 16 kHz -> mang float32 cho Whisper. Dua MANG chu khong dua duong dan: duong dan thi
    faster-whisper tu mo bang PyAV va goi av.open(..., metadata_errors=...) — PyAV 19 (21/10/2026) bo tham so nay
    => may cai moi loi "open() got an unexpected keyword argument 'metadata_errors'" (bat duoc 28/10 tren venv sach)."""
    import wave
    import numpy as np
    with wave.open(path, "rb") as f:
        raw = f.readframes(f.getnframes())
    return np.frombuffer(raw, dtype="<i2").astype(np.float32) / 32768.0


def transcribe(video, model_name, language, device, compute_type, vad):
    try:
        from faster_whisper import WhisperModel
    except Exception as exc:
        C.die("chua cai faster-whisper (%s).\n"
              "  Chay:  pip install faster-whisper\n"
              "  Roi chay lai preflight de kiem." % exc)

    if device == "auto":
        device, compute_default = "cpu", "int8"
        try:
            import torch
            if torch.cuda.is_available():
                device, compute_default = "cuda", "float16"
        except Exception:
            pass
    else:
        compute_default = "float16" if device == "cuda" else "int8"
    compute_type = compute_type or compute_default

    print("  nhan dang bang model %s (%s / %s), ngon ngu=%s, vad=%s"
          % (model_name, device, compute_type, language, "co" if vad else "khong"))
    t0 = time.time()
    try:
        wm = WhisperModel(model_name, device=device, compute_type=compute_type)
    except Exception as exc:
        C.die("khong nap duoc model '%s' (%s).\n"
              "  Neu day la lan chay dau: can mang de tai model ve.\n"
              "  May yeu thi dung model nho hon:  --model small\n"
              "  Loi GPU thi ep dung CPU:         --device cpu"
              % (model_name, exc))

    tmpdir = tempfile.mkdtemp(prefix="nnssub_")
    try:
        wav = extract_wav(video, os.path.join(tmpdir, "a.wav"))
        segs, info = wm.transcribe(
            doc_wav(wav), language=language, word_timestamps=True, vad_filter=vad,
            beam_size=5, condition_on_previous_text=False)
        out_segs, flat = [], []
        for s in segs:
            words = []
            for w in (s.words or []):
                item = {"w": w.word.strip(), "start": round(float(w.start), 3),
                        "end": round(float(w.end), 3),
                        "p": round(float(getattr(w, "probability", 0.0) or 0.0), 3)}
                if not item["w"]:
                    continue
                words.append(item)
                flat.append(item)
            out_segs.append({"start": round(float(s.start), 3),
                             "end": round(float(s.end), 3),
                             "text": s.text.strip(), "words": words})
            print("    [%6.2f - %6.2f] %s" % (s.start, s.end, s.text.strip()))
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)

    if not flat:
        C.die("khong nhan ra tu nao trong video.\n"
              "  Kiem: video co tieng noi khong? Ngon ngu co dung --language khong?\n"
              "  Thu lai voi:  --no-vad   (bo loc im lang, hay dung khi tieng nho)")
    print("  xong sau %.1fs — %d cau, %d tu"
          % (time.time() - t0, len(out_segs), len(flat)))
    return {"segments": out_segs, "words": flat,
            "detected_language": getattr(info, "language", language)}


def main():
    C.setup_stdout()
    ap = argparse.ArgumentParser()
    ap.add_argument("--video")
    ap.add_argument("--out",
                    help="file video ket qua — dung de biet dat cache o dau")
    ap.add_argument("--resources", help="khong dung o buoc nay, nhan cho dung hop dong")
    ap.add_argument("--model", default="large-v3")
    ap.add_argument("--language", default="vi")
    ap.add_argument("--device", default="auto", choices=["auto", "cpu", "cuda"])
    ap.add_argument("--compute-type", default=None,
                    help="int8 | float16 | float32 (mac dinh tu chon theo device)")
    ap.add_argument("--no-vad", action="store_true",
                    help="tat vad_filter (dung khi tieng nho bi cat mat)")
    ap.add_argument("--force", action="store_true", help="nhan dang lai, bo cache")
    ap.add_argument("--dry-run", action="store_true",
                    help="chi in ke hoach, khong nhan dang, khong ghi file")
    a = ap.parse_args()
    C.require_video_out(a, "transcribe.py")

    if not os.path.isfile(a.video):
        C.die("khong thay video: %s" % a.video)
    cache = C.side_path(a.out, ".words.json")

    print("")
    print("  " + C.hr("-"))
    print("  BUOC 1/4 — nhan dang loi noi (word timestamps)")
    print("  " + C.hr("-"))
    print("  video : %s" % a.video)
    print("  cache : %s" % cache)

    if a.dry_run:
        hit = load_cache(cache, a.video, a.model, a.language)
        print("  [dry-run] %s" % ("da co cache, se dung lai"
                                  if hit and not a.force else
                                  "se chay nhan dang model %s" % a.model))
        return

    if not a.force:
        hit = load_cache(cache, a.video, a.model, a.language)
        if hit:
            print("  dung lai cache co san: %d cau, %d tu"
                  % (len(hit["segments"]), len(hit["words"])))
            for s in hit["segments"]:
                print("    [%6.2f - %6.2f] %s" % (s["start"], s["end"], s["text"]))
            return

    res = transcribe(a.video, a.model, a.language, a.device, a.compute_type,
                     not a.no_vad)
    info = C.probe_video(a.video)
    C.write_json(cache, {
        "cache_version": CACHE_VERSION,
        "video": os.path.abspath(a.video),
        "video_mtime": os.path.getmtime(a.video),
        "video_fps": info["fps"], "video_frames": info["nb_frames"],
        "video_w": info["width"], "video_h": info["height"],
        "model": a.model, "language": a.language,
        "segments": res["segments"], "words": res["words"]})
    print("  da ghi: %s" % cache)


if __name__ == "__main__":
    C.run_main(main)
