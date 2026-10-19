# iPhone: the record button

You'll make one Shortcut that records and drops the audio into iCloud Drive. Status: **tested**.

## Build the "Unpinned" Shortcut
Add actions by searching for them by name. Menus move around between iOS versions, so don't hunt by location.

1. Open **Shortcuts** → **+** → name it **Unpinned**.
2. Add **Record Audio**. In its options: start **immediately**, finish **on tap**.
3. Add **Save File**:
   - Turn **Ask Where to Save** off.
   - If it gives you a folder picker: choose **iCloud Drive → Unpinned**.
   - If you have to type a path: type `Unpinned/` (trailing slash). That saves to
     **iCloud Drive → Shortcuts → Unpinned**. The default config watches both places.
   - Leave **Overwrite** off.
4. Optional: add **Show Notification** with "Sent ✅".

If your Shortcuts app can build a shortcut from a description, you can try:
> "Make a shortcut called Unpinned that records audio until I tap stop, then saves it to the Unpinned folder in iCloud Drive without asking where to save."

Then check that it has those two steps.

## Make it one tap
- **Action Button** (iPhone 15 Pro and newer): Settings → Action Button → Shortcut → Unpinned
- **Home Screen / Lock Screen / Control Center**: add the shortcut there
- **Siri**: "Hey Siri, Unpinned"

## Already transcribed? Send text instead
Voice Memos can show a transcript. Copy it (**Copy Transcript**, or select the text and copy), then run a second
two-action Shortcut, **Unpinned Text**: **Get Clipboard** → **Save File** (same folder as above).
The computer files `.txt` notes without transcribing them again.

## Good to know
- **No Wi-Fi?** Works on cellular. Check Settings → [your name] → iCloud → iCloud Drive → **Use Cellular Data**.
  With no signal at all, iCloud uploads it later on its own.
- **Undo:** delete the file from Files → iCloud Drive → Unpinned within the grace period (default 10 minutes).

Next: set up the computer side, either [Mac](mac.md) or [Windows](windows.md).
