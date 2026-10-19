#!/usr/bin/env python3
"""Unpinned: voice notes from your phone -> transcribed on your own computer -> your notes inbox.

Your phone saves recordings into a synced folder (iCloud Drive, Syncthing, Google Drive...).
A scheduler runs this script every couple of minutes. Each run it:
  1. looks in every watch folder for audio (.m4a .mp3 .wav ...) or text (.txt .md),
  2. skips anything newer than the grace period (delete it on your phone to cancel),
  3. transcribes audio locally (whisper.cpp or faster-whisper; nothing is uploaded),
  4. writes  <inbox>/YYYY-MM-DD HHMM voice.md  and moves the original into processed/.
Failures move to failed/ and are logged. Nothing is ever deleted.

usage:
  python3 unpinned.py                 one pass (what the scheduler runs)
  python3 unpinned.py --now           one pass, ignoring the grace period
  python3 unpinned.py --check         show config and which transcription engine was found
  python3 unpinned.py --config FILE   use a specific config (default: see CONFIG_PATHS)

Standard library only (Python 3.9+). Transcription needs ONE of:
  whisper.cpp  (`whisper-cli` + a ggml model + ffmpeg)   - recommended on macOS
  faster-whisper (`pip install faster-whisper`)          - easiest on Windows/Linux
"""
import argparse
import datetime as dt
import json
import os
import platform
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
CONFIG_PATHS = [
    HERE / "config.json",
    Path.home() / ".config" / "unpinned" / "config.json",
]
AUDIO = {".m4a", ".mp3", ".wav", ".caf", ".aac", ".ogg", ".opus", ".amr", ".3gp", ".mp4", ".mov", ".webm"}
TEXT = {".txt", ".md"}
DEFAULTS = {
    "watch_folders": [],
    "inbox": "",
    "grace_minutes": 10,
    "engine": "auto",  # auto | whisper-cpp | faster-whisper
    "language": "en",
    "whisper_cpp": {"binary": "whisper-cli", "model": "", "ffmpeg": "ffmpeg"},
    "faster_whisper": {"model": "small.en", "compute_type": "int8"},
    "log_file": "",
}


# ---------- config ----------

def load_config(path=None):
    candidates = [Path(path).expanduser()] if path else CONFIG_PATHS
    for p in candidates:
        if p.exists():
            cfg = json.loads(p.read_text())
            merged = {**DEFAULTS, **cfg}
            for k in ("whisper_cpp", "faster_whisper"):
                merged[k] = {**DEFAULTS[k], **cfg.get(k, {})}
            merged["_path"] = str(p)
            return merged
    sys.exit("no config found. Copy config.example.json to config.json and edit it. Looked in:\n  "
             + "\n  ".join(str(p) for p in candidates))


def expand(p):
    return Path(os.path.expandvars(os.path.expanduser(p)))


# ---------- logging ----------

LOG = None


def log(msg):
    line = f"{dt.datetime.now():%Y-%m-%d %H:%M:%S} {msg}"
    print(line, flush=True)
    if LOG:
        with open(LOG, "a", encoding="utf-8") as f:
            f.write(line + "\n")


# ---------- transcription engines ----------

def find_whisper_cpp(cfg):
    w = cfg["whisper_cpp"]
    binary = shutil.which(w["binary"]) or (w["binary"] if Path(w["binary"]).exists() else None)
    ffmpeg = shutil.which(w["ffmpeg"]) or (w["ffmpeg"] if Path(w["ffmpeg"]).exists() else None)
    model = expand(w["model"]) if w["model"] else None
    if binary and ffmpeg and model and model.exists():
        return binary, ffmpeg, model
    return None


def has_faster_whisper():
    try:
        import faster_whisper  # noqa: F401
        return True
    except ImportError:
        return False


def pick_engine(cfg):
    want = cfg["engine"]
    if want in ("auto", "whisper-cpp") and find_whisper_cpp(cfg):
        return "whisper-cpp"
    if want in ("auto", "faster-whisper") and has_faster_whisper():
        return "faster-whisper"
    return None


_FW_MODEL = None


def transcribe(audio, cfg, engine):
    if engine == "whisper-cpp":
        binary, ffmpeg, model = find_whisper_cpp(cfg)
        with tempfile.TemporaryDirectory() as tmp:
            wav = Path(tmp) / "in.wav"
            subprocess.run([ffmpeg, "-nostdin", "-loglevel", "error", "-i", str(audio),
                            "-ar", "16000", "-ac", "1", "-c:a", "pcm_s16le", str(wav)], check=True)
            cmd = [binary, "-m", str(model), "-f", str(wav), "-nt", "-np"]
            if cfg["language"]:
                cmd += ["-l", cfg["language"]]
            out = subprocess.run(cmd, check=True, capture_output=True, text=True)
        return " ".join(l.strip() for l in out.stdout.splitlines() if l.strip())

    global _FW_MODEL
    from faster_whisper import WhisperModel
    if _FW_MODEL is None:
        fw = cfg["faster_whisper"]
        _FW_MODEL = WhisperModel(fw["model"], device="cpu", compute_type=fw["compute_type"])
    segments, _ = _FW_MODEL.transcribe(str(audio), language=cfg["language"] or None)
    return " ".join(s.text.strip() for s in segments if s.text.strip())


# ---------- files ----------

def created_at(path):
    st = path.stat()
    t = getattr(st, "st_birthtime", None)  # macOS, and Windows on Python 3.12+
    if t is None:
        t = st.st_ctime if platform.system() == "Windows" else st.st_mtime
    return dt.datetime.fromtimestamp(t)


def unique(path):
    n = 2
    base = path.stem
    while path.exists():
        path = path.with_name(f"{base} ({n}){path.suffix}")
        n += 1
    return path


def request_icloud_downloads(folder):
    # macOS keeps not-yet-downloaded iCloud files as ".name.icloud" placeholders.
    if platform.system() == "Darwin":
        for p in folder.glob(".*.icloud"):
            subprocess.run(["brctl", "download", str(p)], capture_output=True)


def process(item, folder, inbox, cfg, engine):
    made = created_at(item)
    done = unique(folder / "processed" / item.name)
    if item.suffix.lower() in TEXT:
        text = item.read_text(encoding="utf-8", errors="replace").strip()
        kind = "text"
    else:
        if engine is None:
            raise RuntimeError("no transcription engine found (run with --check)")
        text = transcribe(item, cfg, engine)
        kind = "voice"
    note = unique(inbox / f"{made:%Y-%m-%d %H%M} {kind}.md")
    note.write_text(f"Captured {made:%Y-%m-%d %H:%M} ({kind}). Original: {done.name}\n\n{text or '(empty)'}\n",
                    encoding="utf-8")
    shutil.move(str(item), str(done))
    log(f"filed {item.name} -> {note.name} ({len(text.split())} words)")


def run(cfg, now=False):
    folders = [expand(f) for f in cfg["watch_folders"]]
    inbox = expand(cfg["inbox"])
    if not cfg["inbox"] or not inbox.parent.exists():
        sys.exit(f"inbox folder's parent doesn't exist: {inbox}")
    inbox.mkdir(exist_ok=True)
    engine = pick_engine(cfg)
    cutoff = time.time() - (0 if now else cfg["grace_minutes"] * 60)
    for folder in folders:
        if not folder.exists():
            log(f"skipping missing watch folder: {folder}")
            continue
        request_icloud_downloads(folder)
        for sub in ("processed", "failed"):
            (folder / sub).mkdir(exist_ok=True)
        for item in sorted(folder.iterdir()):
            if not item.is_file() or item.name.startswith("."):
                continue
            if item.suffix.lower() not in AUDIO | TEXT:
                continue
            if item.stat().st_mtime > cutoff:
                continue
            try:
                process(item, folder, inbox, cfg, engine)
            except Exception as e:
                log(f"FAILED {item.name}: {e!r}")
                shutil.move(str(item), str(unique(folder / "failed" / item.name)))


def check(cfg):
    inbox = expand(cfg["inbox"])
    print(f"config:  {cfg['_path']}")
    print(f"inbox:   {inbox}  ({'ok' if cfg['inbox'] and inbox.parent.exists() else 'PARENT MISSING'})")
    for f in cfg["watch_folders"]:
        print(f"watch:   {expand(f)}  ({'ok' if expand(f).exists() else 'MISSING'})")
    engine = pick_engine(cfg)
    print(f"engine:  {engine or 'NONE FOUND: install whisper.cpp or `pip install faster-whisper`'}")
    print(f"grace:   {cfg['grace_minutes']} min")
    return 0 if engine else 1


def main():
    global LOG
    ap = argparse.ArgumentParser(description="Phone voice notes -> local transcription -> notes inbox.")
    ap.add_argument("--now", action="store_true", help="ignore the grace period")
    ap.add_argument("--check", action="store_true", help="validate config and engine, then exit")
    ap.add_argument("--config", help="path to config.json")
    args = ap.parse_args()
    cfg = load_config(args.config)
    LOG = expand(cfg["log_file"]) if cfg["log_file"] else None
    if args.check:
        sys.exit(check(cfg))
    run(cfg, now=args.now)


if __name__ == "__main__":
    main()
