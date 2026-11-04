# -*- coding: utf-8 -*-
"""Sua transcript o MUC TU (token), co xet tu lan can.

    python scripts/fix_tokens.py --video <video> --out <video_ra.mp4> \
        [--fixes luat_cua_toi.json] [--no-default-fixes] [--dry-run]

VI SAO KHONG DUNG REGEX CUM TU:
  Sub karaoke ve TUNG TU. Mot token chi la "cloud", khong bao gio la
  "dung cloud de". Nen regex kieu  r"dung cloud"  KHONG BAO GIO khop.
  Moi luat o day chay tren 1 token, va duoc phep NHIN token truoc/sau.

Luat lam 2 viec:
  1. sua CHU   — ten rieng bi nghe sai (Cloud -> Claude, Hyperframe -> HyperFrames)
  2. sua THOI GIAN — Whisper keo dai do dai tu (do that: "va" mot am tiet ra
     0.600s trong khi trung vi ca cau la 0.280s)

Luon in RO: da sua gi, va CO Y khong sua gi (de luat sai lo ra ngay).
"""
from __future__ import annotations

import argparse
import os
import statistics
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import nnscommon as C  # noqa: E402

PUNCT = u".,!?;:…\"'()[]{}“”‘’-–—"

# --------------------------------------------------------------------------
# Luat mac dinh — domain kenh AI tieng Viet. Doi/them bang --fixes.
# --------------------------------------------------------------------------
DEFAULT_FIXES = {
    # 1 token -> 1 token. So sanh khong phan biet hoa/thuong, bo dau cau.
    "token": {
        "cloud": "Claude",
        "clau": "Claude",
        "cờ-lốt": "Claude",
        "hyperframe": "HyperFrames",
        "hyperframes": "HyperFrames",
        "capcut": "CapCut",
        "chatgpt": "ChatGPT",
        "gpt": "GPT",
        "ai": "AI",
        "remotion": "Remotion",
        "gemini": "Gemini",
        "midjourney": "Midjourney",
        "veo": "Veo",
        "prompt": "prompt",
    },
    # nhieu token lien nhau -> 1 token (moc thoi gian gop lai)
    "merge": [
        {"words": ["chat", "gpt"], "to": "ChatGPT"},
        {"words": ["hyper", "frame"], "to": "HyperFrames"},
        {"words": ["hyper", "frames"], "to": "HyperFrames"},
        {"words": ["cap", "cut"], "to": "CapCut"},
        {"words": ["mid", "journey"], "to": "Midjourney"},
    ],
    # luat co dieu kien: chi doi khi tu lan can dat/khong dat dieu kien.
    # Cai nay chan duoc truong hop "cloud" that su la dam may.
    "context": [
        {"token": "cloud", "to": "Claude",
         "not_next": ["computing", "server", "storage", "sql", "run",
                      "function", "gaming"],
         "not_prev": ["google", "aws", "azure", "alibaba", "icloud"]},
    ],
    # danh sach cam: token nam trong day KHONG BAO GIO bi doi
    "keep": ["cloudflare", "icloud", "soundcloud"],
}

# Thoi gian: chan do dai tu bi phinh
DUR_FACTOR = 2.0        # cap = trung vi * 2.0
DUR_MIN_CAP = 0.35      # nhung khong bao gio duoi 0.35s
DUR_PER_CHAR = 0.06     # tu dai hon 6 ky tu thi noi them theo so ky tu
DUR_LONG_CHARS = 6


def norm(tok):
    """Dang chuan de so luat: bo dau cau 2 dau, ha ve chu thuong."""
    return tok.strip(PUNCT).strip().lower()


def split_punct(tok):
    """Tra ve (dau_truoc, than, dau_sau) de giu lai dau cau khi thay chu."""
    lead = ""
    trail = ""
    body = tok
    while body and body[0] in PUNCT:
        lead += body[0]
        body = body[1:]
    while body and body[-1] in PUNCT:
        trail = body[-1] + trail
        body = body[:-1]
    return lead, body, trail


def load_fixes(path, use_default):
    fixes = {"token": {}, "merge": [], "context": [], "keep": []}
    if use_default:
        fixes["token"].update(DEFAULT_FIXES["token"])
        fixes["merge"].extend(DEFAULT_FIXES["merge"])
        fixes["context"].extend(DEFAULT_FIXES["context"])
        fixes["keep"].extend(DEFAULT_FIXES["keep"])
    if path:
        if not os.path.isfile(path):
            C.die("khong thay file --fixes: %s\n"
                  "  File nay la JSON, dang:\n"
                  '    {"token": {"cloud": "Claude"},\n'
                  '     "merge": [{"words":["chat","gpt"],"to":"ChatGPT"}],\n'
                  '     "context": [{"token":"cloud","to":"Claude",'
                  '"not_next":["computing"]}],\n'
                  '     "keep": ["cloudflare"]}' % path)
        try:
            user = C.read_json(path)
        except Exception as exc:
            C.die("file --fixes khong phai JSON hop le: %s\n  %s" % (path, exc))
        if not isinstance(user, dict):
            C.die("file --fixes phai la mot object JSON { ... }, khong phai %s"
                  % type(user).__name__)
        bad = [k for k in user if k not in ("token", "merge", "context", "keep")]
        if bad:
            C.die("file --fixes co khoa la: %s\n"
                  "  Chi nhan: token, merge, context, keep" % ", ".join(bad))
        for k, v in (user.get("token") or {}).items():
            fixes["token"][norm(k)] = v
        fixes["merge"].extend(user.get("merge") or [])
        fixes["context"].extend(user.get("context") or [])
        fixes["keep"].extend(norm(k) for k in (user.get("keep") or []))
    fixes["token"] = {norm(k): v for k, v in fixes["token"].items()}
    fixes["keep"] = set(norm(k) for k in fixes["keep"])
    return fixes


# --------------------------------------------------------------------------

def apply_merges(words, fixes, changed):
    """Gop token lien nhau. Chay TRUOC luat 1-token."""
    rules = []
    for r in fixes["merge"]:
        seq = [norm(w) for w in (r.get("words") or [])]
        if len(seq) < 2 or not r.get("to"):
            continue
        rules.append((seq, r["to"]))
    rules.sort(key=lambda x: -len(x[0]))
    out, i = [], 0
    while i < len(words):
        hit = None
        for seq, to in rules:
            if i + len(seq) > len(words):
                continue
            got = [norm(words[i + k]["w"]) for k in range(len(seq))]
            if got == seq:
                hit = (seq, to)
                break
        if hit:
            seq, to = hit
            grp = words[i:i + len(seq)]
            old = " ".join(w["w"] for w in grp)
            _l, _b, trail = split_punct(grp[-1]["w"])
            new = {"w": to + trail, "start": grp[0]["start"],
                   "end": grp[-1]["end"],
                   "p": min(w.get("p", 1.0) for w in grp)}
            out.append(new)
            changed.append((grp[0]["start"], old, new["w"],
                            "merge %s" % "+".join(seq)))
            i += len(seq)
        else:
            out.append(dict(words[i]))
            i += 1
    return out


def apply_context(words, fixes, changed, skipped):
    """Luat co dieu kien — day la cho 'nhin tu lan can'."""
    for i, w in enumerate(words):
        n = norm(w["w"])
        if n in fixes["keep"]:
            continue
        prev_n = norm(words[i - 1]["w"]) if i > 0 else ""
        next_n = norm(words[i + 1]["w"]) if i + 1 < len(words) else ""
        for r in fixes["context"]:
            if norm(r.get("token", "")) != n:
                continue
            to = r.get("to")
            if not to:
                continue
            block = None
            if next_n and next_n in [norm(x) for x in (r.get("not_next") or [])]:
                block = 'tu SAU la "%s" (not_next)' % words[i + 1]["w"]
            if prev_n and prev_n in [norm(x) for x in (r.get("not_prev") or [])]:
                block = 'tu TRUOC la "%s" (not_prev)' % words[i - 1]["w"]
            need_next = [norm(x) for x in (r.get("next") or [])]
            if need_next and next_n not in need_next:
                block = 'tu SAU khong nam trong next=%s' % (r.get("next"),)
            need_prev = [norm(x) for x in (r.get("prev") or [])]
            if need_prev and prev_n not in need_prev:
                block = 'tu TRUOC khong nam trong prev=%s' % (r.get("prev"),)
            if block:
                skipped.append((w["start"], w["w"],
                                'luat context %s->%s bi chan: %s'
                                % (r.get("token"), to, block)))
                w["_ctx_locked"] = True
                break
            lead, _body, trail = split_punct(w["w"])
            new = lead + to + trail
            if new != w["w"]:
                changed.append((w["start"], w["w"], new,
                                "context %s->%s" % (r.get("token"), to)))
                w["w"] = new
            w["_ctx_locked"] = True
            break
    return words


def apply_token(words, fixes, changed, skipped):
    for w in words:
        if w.pop("_ctx_locked", False):
            continue
        n = norm(w["w"])
        if not n:
            continue
        if n in fixes["keep"]:
            skipped.append((w["start"], w["w"], "nam trong danh sach keep"))
            continue
        if n not in fixes["token"]:
            continue
        lead, _body, trail = split_punct(w["w"])
        new = lead + fixes["token"][n] + trail
        if new == w["w"]:
            continue
        changed.append((w["start"], w["w"], new, "token %s" % n))
        w["w"] = new
    return words


def fix_durations(words, factor, min_cap, report):
    """Chan do dai tu bi Whisper phinh. Khong bao gio lam tu dai ra.

    Luon tra ve (words, trung_vi) — 2 gia tri, ke ca khi khong lam gi.
    """
    if len(words) < 3:
        # qua it tu de tinh trung vi -> khong chan gi, nhung VAN tra ve 2 gia tri
        return words, 0.0
    durs = [w["end"] - w["start"] for w in words]
    med = statistics.median(durs)
    for i, w in enumerate(words):
        cap = max(min_cap, med * factor)
        body = norm(w["w"])
        if len(body) > DUR_LONG_CHARS:
            cap += DUR_PER_CHAR * (len(body) - DUR_LONG_CHARS)
        dur = w["end"] - w["start"]
        if dur > cap + 1e-6:
            new_end = round(w["start"] + cap, 3)
            report.append((w["start"], w["w"], dur, cap))
            w["end"] = new_end
        # khong bao gio de tu nay tran qua tu sau
        if i + 1 < len(words) and w["end"] > words[i + 1]["start"]:
            w["end"] = words[i + 1]["start"]
        if w["end"] <= w["start"]:
            w["end"] = round(w["start"] + 0.08, 3)
    return words, med


def main():
    C.setup_stdout()
    ap = argparse.ArgumentParser()
    ap.add_argument("--video")
    ap.add_argument("--out")
    ap.add_argument("--resources")
    ap.add_argument("--fixes", help="file JSON luat rieng cua ban")
    ap.add_argument("--no-default-fixes", action="store_true",
                    help="bo het luat mac dinh, chi dung --fixes")
    ap.add_argument("--dur-factor", type=float, default=DUR_FACTOR)
    ap.add_argument("--dur-min-cap", type=float, default=DUR_MIN_CAP)
    ap.add_argument("--no-dur-fix", action="store_true",
                    help="khong chan do dai tu")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    C.require_video_out(a, "fix_tokens.py")

    src = C.side_path(a.out, ".words.json")
    dst = C.side_path(a.out, ".fixed.json")
    if not os.path.isfile(src):
        C.die("chua co transcript: %s\n"
              "  Chay buoc nhan dang truoc:\n"
              '      python scripts/transcribe.py --video "%s" --out "%s"'
              % (src, a.video, a.out))
    data = C.read_json(src)
    words = [dict(w) for w in data["words"]]
    fixes = load_fixes(a.fixes, not a.no_default_fixes)

    print("")
    print("  " + C.hr("-"))
    print("  BUOC 2/4 — sua transcript o muc TU")
    print("  " + C.hr("-"))
    print("  luat: %d token, %d merge, %d context, %d keep%s"
          % (len(fixes["token"]), len(fixes["merge"]), len(fixes["context"]),
             len(fixes["keep"]),
             "  (+ file %s)" % a.fixes if a.fixes else ""))

    changed, skipped = [], []
    words = apply_merges(words, fixes, changed)
    words = apply_context(words, fixes, changed, skipped)
    words = apply_token(words, fixes, changed, skipped)

    dur_report = []
    med = None
    if not a.no_dur_fix:
        words, med = fix_durations(words, a.dur_factor, a.dur_min_cap, dur_report)

    print("")
    print("  DA SUA CHU (%d):" % len(changed))
    if not changed:
        print("      (khong co)")
    for t, old, new, why in changed:
        print('      [%6.2f]  "%s"  ->  "%s"      (%s)' % (t, old, new, why))

    print("")
    print("  CO Y KHONG SUA (%d) — doc ky, luat sai se lo ra o day:" % len(skipped))
    if not skipped:
        print("      (khong co)")
    for t, tok, why in skipped:
        print('      [%6.2f]  "%s"  giu nguyen — %s' % (t, tok, why))

    if not a.no_dur_fix:
        print("")
        print("  CHAN DO DAI TU (%d/%d tu, trung vi %.3fs):"
              % (len(dur_report), len(words), med or 0))
        if not dur_report:
            print("      (khong tu nao bi phinh)")
        for t, tok, dur, cap in dur_report[:25]:
            print('      [%6.2f]  "%s"  %.3fs -> %.3fs' % (t, tok, dur, cap))
        if len(dur_report) > 25:
            print("      ... con %d tu nua" % (len(dur_report) - 25))

    if a.dry_run:
        print("")
        print("  [dry-run] khong ghi file. Se ghi vao: %s" % dst)
        return

    out = dict(data)
    out["words"] = words
    out["fixed"] = {"changed": len(changed), "skipped": len(skipped),
                    "duration_capped": len(dur_report),
                    "median_word_dur": med}
    C.write_json(dst, out)
    print("")
    print("  da ghi: %s" % dst)


if __name__ == "__main__":
    C.run_main(main)
