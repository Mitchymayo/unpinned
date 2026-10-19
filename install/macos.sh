#!/usr/bin/env bash
# Unpinned for macOS: installs whisper.cpp + a model, builds the launcher, schedules it every 2 min.
# Safe to re-run. Usage:  bash install/macos.sh
set -euo pipefail

REPO="$(cd "$(dirname "$0")/.." && pwd)"
DATA="$HOME/.local/share/unpinned"
MODEL="$DATA/ggml-small.en.bin"
LABEL="com.unpinned.capture"
PLIST="$HOME/Library/LaunchAgents/$LABEL.plist"
PY="/usr/bin/python3"

mkdir -p "$DATA"

echo "1/5 tools"
command -v brew >/dev/null || { echo "Install Homebrew first: https://brew.sh"; exit 1; }
command -v whisper-cli >/dev/null || brew install whisper-cpp
command -v ffmpeg >/dev/null || brew install ffmpeg
command -v swiftc >/dev/null || { echo "Run: xcode-select --install   (then re-run this script)"; exit 1; }

echo "2/5 speech model (~470 MB, one time)"
[ -f "$MODEL" ] || curl -L --fail -o "$MODEL" \
  https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-small.en.bin

echo "3/5 config"
if [ ! -f "$REPO/config.json" ]; then
  cp "$REPO/config.example.json" "$REPO/config.json"
  mkdir -p "$HOME/Library/Mobile Documents/com~apple~CloudDocs/Unpinned" \
           "$HOME/Library/Mobile Documents/iCloud~is~workflow~my~workflows/Documents/Unpinned" 2>/dev/null || true
  echo "   created config.json. EDIT \"inbox\" to point at your notes inbox folder, then re-run."
  exit 0
fi
"$PY" "$REPO/unpinned.py" --check

echo "4/5 launcher"
sed -e "s#__PYTHON__#$PY#" -e "s#__SCRIPT__#$REPO/unpinned.py#" "$REPO/install/runner.swift" > "$DATA/runner.swift"
swiftc -O "$DATA/runner.swift" -o "$DATA/unpinned-runner"
codesign -s - -f "$DATA/unpinned-runner" 2>/dev/null

echo "5/5 schedule (every 2 minutes)"
cat > "$PLIST" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
  <key>Label</key><string>$LABEL</string>
  <key>ProgramArguments</key><array><string>$DATA/unpinned-runner</string></array>
  <key>StartInterval</key><integer>120</integer>
  <key>RunAtLoad</key><true/>
  <key>Nice</key><integer>10</integer>
  <key>LowPriorityIO</key><true/>
  <key>StandardOutPath</key><string>$DATA/launchd.log</string>
  <key>StandardErrorPath</key><string>$DATA/launchd.log</string>
</dict></plist>
EOF
launchctl bootout "gui/$(id -u)/$LABEL" 2>/dev/null || true
launchctl bootstrap "gui/$(id -u)" "$PLIST"

cat <<EOF

Done. ONE manual step left (macOS privacy):
  System Settings -> Privacy & Security -> Full Disk Access -> +
  press Cmd+Shift+G, paste:  $DATA/unpinned-runner   -> Open -> toggle ON

Then check it:   tail -f "$DATA/unpinned.log"
Uninstall:       launchctl bootout gui/\$(id -u)/$LABEL && rm "$PLIST"
EOF
