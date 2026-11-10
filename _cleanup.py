# -*- coding: utf-8 -*-
"""ลบไฟล์ตรวจสอบชั่วคราวที่สร้างขึ้นระหว่างงาน"""
import os
import sys

for stream in (sys.stdout, sys.stderr):
    try:
        stream.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

here = os.path.dirname(os.path.abspath(__file__))
for name in ("_check_assets.py", "_check_js.py", "_shot_prev.png", "_shot_prev_top.png"):
    path = os.path.join(here, name)
    try:
        os.remove(path)
        print("removed", name)
    except OSError:
        print("skip", name)
print("done")
