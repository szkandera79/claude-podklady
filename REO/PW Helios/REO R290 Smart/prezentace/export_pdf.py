#!/usr/bin/env python3
"""PPTX → PDF exportem z Microsoft PowerPointu (AppleScript). Výstup musí být ve složce, kam má PowerPoint přístup."""
import os
import subprocess
import sys


SANDBOX = os.path.expanduser('~/Library/Containers/com.microsoft.Powerpoint/Data/Documents/reo-export')


def export(pptx, pdf):
    """Export přes sandbox kontejner PowerPointu (tam má vždy přístup) → kopie PDF do cíle."""
    import shutil
    pptx, final = os.path.abspath(pptx), os.path.abspath(pdf)
    os.makedirs(SANDBOX, exist_ok=True)
    src = os.path.join(SANDBOX, os.path.basename(pptx))
    shutil.copyfile(pptx, src)
    pptx, pdf = src, os.path.join(SANDBOX, os.path.basename(final))
    if os.path.exists(pdf):
        os.remove(pdf)
    name = os.path.basename(pptx)
    script = f'''
with timeout of 900 seconds
tell application "Microsoft PowerPoint"
  open POSIX file "{pptx}"
  repeat 60 times
    if (name of every presentation) contains "{name}" then exit repeat
    delay 1
  end repeat
  delay 3
  set p to presentation "{name}"
  save p in POSIX file "{pdf}" as save as PDF
  delay 2
  close p saving no
end tell
end timeout'''
    r = subprocess.run(['osascript', '-e', script], capture_output=True, text=True)
    if not os.path.exists(pdf):
        raise SystemExit('export selhal: ' + r.stderr)
    shutil.copyfile(pdf, final)
    os.remove(pdf)
    os.remove(pptx)
    return final


if __name__ == '__main__':
    print(export(sys.argv[1], sys.argv[2]))
