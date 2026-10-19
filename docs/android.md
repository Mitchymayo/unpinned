# Android: the record button

Status: **untested by the author**. The approach is standard, but please open an issue with what worked.

Android has no Shortcuts app, so the plan is:
**any recorder app that saves into a folder** + **Syncthing**, which copies that folder to your computer
directly (phone to PC, no cloud account, free).

## 1. Pick a recorder that saves to a folder you choose
Any voice recorder works if you can set where it saves (look for "storage location" or "save folder" in its settings),
or if you can **Share → save to a folder** from it. Use phone storage, not the SD card. Syncthing only gets read
access to SD cards on many phones.

Make a folder for it, e.g. `Internal storage/Unpinned`.

## 2. Sync that folder to your computer with Syncthing
- **Phone:** install **Syncthing-Fork** (F-Droid or Google Play).
- **Computer:** install Syncthing from https://syncthing.net (Windows, Mac and Linux).
- Pair the two devices (scan the QR code shown on the computer). On the phone, share the `Unpinned` folder
  with the computer and accept it there. Note where the computer keeps it, e.g. `C:/Users/you/Unpinned`
  or `~/Unpinned`.

**Prefer Google Drive?** That works too: save recordings to a Drive folder and run Google Drive for desktop on the
computer. Your audio does pass through Google, though.

## 3. Point Unpinned at it
In `config.json` on the computer, set `watch_folders` to the synced folder, e.g. `["C:/Users/you/Unpinned"]`.

## Already transcribed?
Some recorder apps make their own transcript. Share or copy it as text and save it as a `.txt` file in the same
folder. Unpinned files it without transcribing again.

Next: set up the computer, either [Windows](windows.md) or [Mac](mac.md).
