# Unpinned

**The AI voice-note pin, without the pin or the subscription.**

Tap a button on your phone, talk, and a couple of minutes later the transcript is a note in your
Obsidian vault (or any notes folder). Transcription runs **on your own computer**, so your audio is
never uploaded to a transcription company. No device to buy, no monthly fee.

```
 phone                      synced folder                 your computer                     your notes
 tap → talk → stop  ──►  iCloud Drive / Syncthing  ──►  Unpinned (local Whisper)  ──►  inbox/2026-10-19 1432 voice.md
```

## Pick your setup

| Your phone | Your computer | Status | Guides |
|---|---|---|---|
| iPhone | Mac | ✅ tested | [iPhone](docs/iphone.md) + [Mac](docs/mac.md) |
| iPhone | Windows | 🧪 untested | [iPhone](docs/iphone.md) + [Windows](docs/windows.md) |
| Android | Windows | 🧪 untested | [Android](docs/android.md) + [Windows](docs/windows.md) |
| Android | Mac | 🧪 untested | [Android](docs/android.md) + [Mac](docs/mac.md) |
| Any | Linux | 🧪 untested | `pip install faster-whisper`, then cron: `*/2 * * * * python3 /path/to/unpinned.py` |

Untested means the steps are standard but nobody has confirmed them yet. If you try one, please open
an issue saying what worked or broke.

## What you get
- **One-tap capture.** Action Button, Home Screen, Siri, or any Android recorder.
- **Local transcription.** whisper.cpp on Mac, faster-whisper on Windows/Linux.
- **Works on the road.** Over cellular, and with no signal it syncs later.
- **10-minute undo.** Delete the recording on your phone before the grace period ends and it's never transcribed.
- **Text too.** Drop a `.txt` (for example a Voice Memos transcript) and it's filed as-is.
- **Nothing is deleted.** Originals move to `processed/`, errors to `failed/`.

## How it works
`unpinned.py` is one standard-library Python file. Your scheduler (launchd, Task Scheduler or cron) runs it every
2 minutes. It finds recordings older than the grace period in your watch folders, transcribes them, writes
`<inbox>/YYYY-MM-DD HHMM voice.md`, and moves the original to `processed/`. All settings live in `config.json`
(start from [config.example.json](config.example.json)).

```bash
python3 unpinned.py --check   # is everything configured?
python3 unpinned.py --now     # process right now, ignoring the grace period
```

## Honest costs
- **Transcription:** $0. It runs on hardware you already own.
- **Your computer has to be on** to process notes. An always-on mini PC or Mac mini makes this hands-off.
- **Optional:** if you have an AI assistant tidy and file your inbox afterward, that part depends on whichever
  tool and plan you use. Unpinned itself just gets clean transcripts into your inbox.

## License
MIT. See [LICENSE](LICENSE).
