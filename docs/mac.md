# Mac: the transcriber

Status: **tested** (Apple silicon, macOS 27).

## Install
```bash
git clone https://github.com/Mitchymayo/unpinned.git ~/unpinned
cd ~/unpinned
bash install/macos.sh        # first run creates config.json, then stops
```
Edit `config.json`:
- `inbox`: your notes inbox folder, e.g. `~/Documents/MyVault/inbox` for an Obsidian vault.
- `watch_folders`: the defaults already cover the iPhone Shortcut. For Android/Syncthing, use your synced folder.

Then run it again:
```bash
bash install/macos.sh
```
It installs whisper.cpp and ffmpeg (Homebrew), downloads the speech model (~470 MB, once), builds a small
launcher and schedules it every 2 minutes.

## The one manual step: Full Disk Access
macOS won't let background jobs read iCloud Drive until you allow it:
**System Settings → Privacy & Security → Full Disk Access → +**, press **Cmd+Shift+G**, paste
`~/.local/share/unpinned/unpinned-runner`, then **Open** and toggle it **on**.

This covers only that small launcher, not Python or anything else.

## Check it
```bash
python3 unpinned.py --check                        # config + engine
tail -f ~/.local/share/unpinned/unpinned.log       # watch notes get filed
```

## Notes
- The Mac must be awake to process. Notes recorded while it sleeps wait in iCloud.
- Long runs are light: a 1-minute note transcribes in a few seconds on Apple silicon.
- Uninstall: `launchctl bootout gui/$(id -u)/com.unpinned.capture && rm ~/Library/LaunchAgents/com.unpinned.capture.plist`
