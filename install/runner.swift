// macOS only. A tiny launcher for unpinned.py.
//
// Background jobs can't read iCloud Drive until you grant "Full Disk Access". Granting it to
// this one helper keeps the permission narrow; granting it to python3 would cover every
// Python script on your Mac. install/macos.sh compiles this with the paths filled in.
import Foundation

let p = Process()
p.executableURL = URL(fileURLWithPath: "__PYTHON__")
p.arguments = ["__SCRIPT__"] + CommandLine.arguments.dropFirst()
try p.run()
p.waitUntilExit()
exit(p.terminationStatus)
