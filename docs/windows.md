# Windows: the transcriber

Status: **untested by the author**. Please open an issue with what worked or broke.

## 1. Get the recordings onto the PC
- **iPhone:** install **iCloud for Windows** (Microsoft Store), sign in, turn on **iCloud Drive**. In File Explorer,
  right-click the `Unpinned` folder → **Always keep on this device**. Typical paths:
  `C:/Users/you/iCloudDrive/Unpinned` and, for typed Shortcut paths, `C:/Users/you/iCloudDrive/Shortcuts/Unpinned`.
  Check yours in File Explorer.
- **Android:** see [android.md](android.md) (Syncthing).

## 2. Install
1. Install **Python 3.9+** from https://www.python.org/downloads/ and tick **Add python.exe to PATH**.
2. Download this repo (green **Code** button → Download ZIP, then unzip), or `git clone` it.
3. In PowerShell, from the repo folder:
   ```powershell
   powershell -ExecutionPolicy Bypass -File install\windows.ps1
   ```
   The first run creates `config.json` and stops.
4. Edit `config.json`. Use forward slashes in paths:
   ```json
   "watch_folders": ["C:/Users/you/iCloudDrive/Unpinned", "C:/Users/you/iCloudDrive/Shortcuts/Unpinned"],
   "inbox": "C:/Users/you/Documents/MyVault/inbox",
   "log_file": "C:/Users/you/unpinned.log"
   ```
5. Run the installer again. It installs `faster-whisper` and schedules Unpinned every 2 minutes.
   The first transcription downloads the speech model (~500 MB).

## Check it
```powershell
python unpinned.py --check
Get-Content C:/Users/you/unpinned.log -Wait
```

## Notes
- The PC must be on and you must be logged in for the task to run.
- Uninstall: `Unregister-ScheduledTask -TaskName Unpinned -Confirm:$false`
