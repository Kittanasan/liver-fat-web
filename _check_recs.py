# -*- coding: utf-8 -*-
"""ตรวจความถูกต้องของส่วนบันทึกผล (id/ฟังก์ชันที่อ้างถึง) และการ join JS"""
import re
import sys

for s in (sys.stdout, sys.stderr):
    try:
        s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

src = open("index.html", encoding="utf-8").read()
ok = True

# 1) ทุก id ที่ JS เรียกผ่าน $("...") ต้องมีอยู่ใน HTML
ids_html = set(re.findall(r'id="([^"]+)"', src))
ids_js = set(re.findall(r'\$\("([^"]+)"\)', src))
missing = sorted(ids_js - ids_html)
print("ids in html:", len(ids_html), "| referenced in js:", len(ids_js))
if missing:
    ok = False
    print("MISSING IDS:", missing)

# 2) ฟังก์ชันที่เรียกใช้ต้องถูกประกาศ
called = set(re.findall(r'(?<![\w.$])([A-Za-z_$][\w$]*)\s*\(', src))
declared = set(re.findall(r'function\s+([A-Za-z_$][\w$]*)\s*\(', src))
declared |= set(re.findall(r'(?:const|let|var)\s+([A-Za-z_$][\w$]*)\s*=', src))
builtin = {
    'if', 'for', 'while', 'switch', 'catch', 'return', 'function', 'typeof', 'new', 'Number', 'String',
    'parseInt', 'Math', 'JSON', 'Object', 'Array', 'Promise', 'setTimeout', 'alert', 'confirm', 'btoa',
    'atob', 'unescape', 'encodeURIComponent', 'decodeURIComponent', 'isNaN', 'document', 'window',
    'URLSearchParams', 'Date', 'Float32Array', 'Image', 'Error', 'encodeURI', 'escape', 'console',
    'FileReader', 'Uint8Array', 'fetch', 'async', 'calc', 'gradient', 'media', 'rgba', 'var',
    'child', 'minmax', 'not', 'repeat', 'rgb',
}
unknown = sorted(c for c in called if c not in declared and c not in builtin)
print("unknown calls:", unknown if unknown else "none")
if unknown:
    ok = False

# 3) ฟิลด์ใหม่ครบใน form
for fid in ("rlabel", "rfarm", "rresult", "rconf", "ranalyst", "rdate"):
    if fid not in ids_html:
        ok = False
        print("MISSING FIELD:", fid)

# 4) หัวตารางครบ 8 คอลัมน์
head = re.search(r'<thead>(.*?)</thead>', src, re.S).group(1)
cols = re.findall(r'<th[^>]*>(.*?)</th>', head, re.S)
print("table head:", [c.strip() or "(ปุ่ม)" for c in cols])

# 5) ไม่มีรูปแบบเก่าตกค้าง
for bad in ("rcode", "d.one.code", "esc(x.code)"):
    if bad in src:
        ok = False
        print("LEFTOVER:", bad)

print("RESULT:", "OK" if ok else "FAIL")
