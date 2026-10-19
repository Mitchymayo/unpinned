# Unpinned for Windows: installs faster-whisper and schedules unpinned.py every 2 minutes.
# UNTESTED by the author so far - please open an issue with what worked or broke.
# Usage (PowerShell, from the repo folder):   powershell -ExecutionPolicy Bypass -File install\windows.ps1
$ErrorActionPreference = "Stop"

$Repo = Split-Path -Parent $PSScriptRoot
$Script = Join-Path $Repo "unpinned.py"
$Config = Join-Path $Repo "config.json"

Write-Host "1/4 python"
$Python = (Get-Command python -ErrorAction SilentlyContinue).Source
if (-not $Python) { throw "Install Python 3.9+ from https://www.python.org/downloads/ (tick 'Add python.exe to PATH'), then re-run." }
# pythonw.exe runs without flashing a console window every 2 minutes.
$PythonW = Join-Path (Split-Path $Python) "pythonw.exe"
if (-not (Test-Path $PythonW)) { $PythonW = $Python }

Write-Host "2/4 faster-whisper (first transcription downloads the speech model, ~500 MB)"
& $Python -m pip install --upgrade --quiet faster-whisper

Write-Host "3/4 config"
if (-not (Test-Path $Config)) {
    Copy-Item (Join-Path $Repo "config.example.json") $Config
    Write-Host "   created config.json. EDIT it: set watch_folders (e.g. your iCloud Drive or Syncthing folder)"
    Write-Host "   and inbox (your notes inbox folder). Use forward slashes or doubled backslashes. Then re-run."
    exit 0
}
& $Python $Script --check

Write-Host "4/4 schedule (every 2 minutes, while you're logged in)"
$Action = New-ScheduledTaskAction -Execute $PythonW -Argument "`"$Script`"" -WorkingDirectory $Repo
$Trigger = New-ScheduledTaskTrigger -Once -At (Get-Date) -RepetitionInterval (New-TimeSpan -Minutes 2)
$Settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -MultipleInstances IgnoreNew
Register-ScheduledTask -TaskName "Unpinned" -Action $Action -Trigger $Trigger -Settings $Settings `
    -Description "Phone voice notes -> local transcription -> notes inbox" -Force | Out-Null

Write-Host ""
Write-Host "Done. Set a log_file in config.json to watch it work."
Write-Host "Uninstall:  Unregister-ScheduledTask -TaskName Unpinned -Confirm:`$false"
