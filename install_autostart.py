# ============================================================
#  Turns the silent always-on monitor ON or OFF.
#  Uses the Windows Startup folder (no administrator needed).
#  Called by the two .bat files in this folder.
# ============================================================

import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
MONITOR = os.path.join(HERE, "monitor.py")
PYTHONW = sys.executable.replace("python.exe", "pythonw.exe")
STARTUP = os.path.join(os.environ.get("APPDATA", ""), "Microsoft", "Windows",
                       "Start Menu", "Programs", "Startup")
LAUNCHER = os.path.join(STARTUP, "Stock Buddy Monitor.vbs")


def install():
    if not os.path.isdir(STARTUP):
        print("Couldn't find your Windows Startup folder.")
        return
    if not os.path.exists(PYTHONW):
        print("Couldn't find pythonw.exe - can't start silently.")
        return
    # A tiny script that starts the monitor with no window, at every logon.
    vbs = (
        'Set WshShell = CreateObject("WScript.Shell")\n'
        f'WshShell.Run """{PYTHONW}"" ""{MONITOR}""", 0, False\n'
    )
    with open(LAUNCHER, "w", encoding="utf-8") as f:
        f.write(vbs)
    print("DONE! Stock Buddy will now start by itself when you log in.")
    print("It runs quietly in the background - no window needed.")
    print("To stop it, use 'Turn Off Always-On.bat'.")


def remove():
    removed = False
    if os.path.exists(LAUNCHER):
        os.remove(LAUNCHER)
        removed = True
    # Stop the copy that's running right now, without touching other
    # python programs (only processes whose command mentions monitor.py).
    ps = ("Get-CimInstance Win32_Process -Filter \"name='pythonw.exe'\" | "
          "Where-Object { $_.CommandLine -like '*monitor.py*' } | "
          "ForEach-Object { Stop-Process -Id $_.ProcessId -Force }")
    subprocess.run(["powershell", "-NoProfile", "-Command", ps],
                   capture_output=True, text=True)
    print("Always-on monitor turned off." if removed else
          "No always-on monitor was installed.")


if __name__ == "__main__":
    if "--remove" in sys.argv:
        remove()
    else:
        install()
