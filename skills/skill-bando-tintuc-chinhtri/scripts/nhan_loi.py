# -*- coding: utf-8 -*-
"""Bước 1: audio -> work/loi_doc.json (từng từ có mốc giây) + loi_doc.txt (để Claude đọc và viết kịch bản).

python -I scripts/nhan_loi.py <audio> [--work <thư mục>] [--model large-v3] [--lang vi]
"""
import argparse
import os
import sys
import time
import wave

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import chung as C


def tach_wav(audio, wav):
    C.chay(["ffmpeg", "-v", "error", "-y", "-i", audio, "-vn", "-ac", "1", "-ar", "16000",
            "-c:a", "pcm_s16le", wav])
    return wav


def doc_wav(path):
    import numpy as np
    with wave.open(path, "rb") as f:
        raw = f.readframes(f.getnframes())
    return np.frombuffer(raw, dtype="<i2").astype(np.float32) / 32768.0


def nhan_dang(wav, model_name="large-v3", lang="vi"):
    try:
        from faster_whisper import WhisperModel
    except Exception as exc:
        C.die("chưa cài faster-whisper (%s). Chạy: python -I -m pip install faster-whisper" % exc)
    device, compute = "cpu", "int8"
    try:
        import torch  # noqa
        if torch.cuda.is_available():
            device, compute = "cuda", "float16"
    except Exception:
        pass
    print("   model %s (%s/%s) — lần đầu tải ~3 GB, chạy CPU lâu, đừng huỷ" % (model_name, device, compute))
    t0 = time.time()
    wm = WhisperModel(model_name, device=device, compute_type=compute)
    segs, info = wm.transcribe(doc_wav(wav), language=lang, word_timestamps=True, vad_filter=True,
                               beam_size=5, condition_on_previous_text=False)
    cau, tu = [], []
    for s in segs:
        words = []
        for w in (s.words or []):
            item = {"w": w.word.strip(), "s": round(float(w.start), 3), "e": round(float(w.end), 3)}
            if item["w"]:
                words.append(item)
                tu.append(item)
        cau.append({"s": round(float(s.start), 3), "e": round(float(s.end), 3),
                    "text": s.text.strip(), "words": words})
    print("   xong sau %.0f s: %d câu, %d từ" % (time.time() - t0, len(cau), len(tu)))
    return cau, tu


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("audio")
    ap.add_argument("--work")
    ap.add_argument("--model", default="large-v3")
    ap.add_argument("--lang", default="vi")
    a = ap.parse_args()
    audio = os.path.abspath(a.audio)
    if not os.path.exists(audio):
        C.die("không thấy audio: " + audio)
    work = a.work or os.path.join(os.path.dirname(audio), "work_ban_do")
    C.mkdir(work)
    C.buoc("Nhận lời: " + os.path.basename(audio))
    dai = C.ffprobe_thoi_luong(audio)
    wav = tach_wav(audio, os.path.join(work, "giong.wav"))
    cau, tu = nhan_dang(wav, a.model, a.lang)
    data = {"audio": audio, "thoi_luong": round(dai, 3), "cau": cau, "tu": tu}
    C.ghi_json(os.path.join(work, "loi_doc.json"), data)
    lines = ["# Lời đọc: %s (%.1f s)" % (os.path.basename(audio), dai),
             "# Mỗi dòng: [giây bắt đầu – kết thúc] câu. Dòng dưới: mốc từng từ.", ""]
    for c in cau:
        lines.append("[%6.2f – %6.2f] %s" % (c["s"], c["e"], c["text"]))
        lines.append("      " + "  ".join("%s@%.2f" % (w["w"], w["s"]) for w in c["words"]))
    C.ghi_text(os.path.join(work, "loi_doc.txt"), "\n".join(lines) + "\n")
    C.ok("đã ghi %s và loi_doc.txt" % os.path.join(work, "loi_doc.json"))
    print("   thời lượng audio: %.2f s → video sẽ dài %.2f s" % (dai, dai + C.DUOI_SAU_TIENG_CUOI))


if __name__ == "__main__":
    main()
