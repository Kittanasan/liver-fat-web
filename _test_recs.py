# -*- coding: utf-8 -*-
"""ทดสอบส่วนบันทึกผลจริงในเบราว์เซอร์ headless: บันทึก -> ตารางแสดง -> ลบ"""
import json
import os
import shutil
import subprocess
import sys
import urllib.request

for s in (sys.stdout, sys.stderr):
    try:
        s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

PORT = 8161
JS = r"""
(() => {
  const out = {};
  localStorage.removeItem('liverV1_records');
  renderRecs();
  out.emptyShown = getComputedStyle(document.getElementById('tempty')).display !== 'none';

  // 1) บันทึกไม่ครบ -> ต้องฟ้อง error
  document.getElementById('save').click();
  out.errLabel = document.getElementById('saveMsg').className.includes('err');

  // 2) บันทึกครบ 2 รายการ
  const fill = (label, farm, cls, conf, analyst, date) => {
    document.getElementById('rlabel').value = label;
    document.getElementById('rfarm').value = farm;
    document.getElementById('rresult').value = cls;
    document.getElementById('rconf').value = conf;
    document.getElementById('ranalyst').value = analyst;
    document.getElementById('rdate').value = date;
    document.getElementById('save').click();
  };
  fill('LV-0001', 'ฟาร์มบางน้ำเปรี้ยว', 'Low', '60.7', 'นายสมชาย ก.', '2026-11-10');
  fill('LV-0002', 'ฟาร์มอยุธยา', 'Hight', '88.2', 'นางสาวสมหญิง', '2026-11-09');

  out.rows = document.querySelectorAll('#tbody tr').length;
  out.cells = [...document.querySelectorAll('#tbody tr:first-child td')].map(t => t.textContent.trim());
  out.emptyHidden = getComputedStyle(document.getElementById('tempty')).display === 'none';
  out.sum = document.getElementById('sum').textContent;
  out.saved = JSON.parse(localStorage.getItem('liverV1_records'));
  out.okMsg = document.getElementById('saveMsg').className === 's' && document.getElementById('saveMsg').textContent.startsWith('บันทึกแล้ว');

  // 3) ลบแถวแรก (auto-confirm)
  window.confirm = () => true;
  document.querySelector('#tbody .tbl-del').click();
  out.afterDelete = JSON.parse(localStorage.getItem('liverV1_records')).map(r => r.label);
  out.rowsAfter = document.querySelectorAll('#tbody tr').length;
  out.msgAfterDelete = document.getElementById('saveMsg').textContent;

  // 4) ล้างทั้งหมด
  document.getElementById('clear').click();
  out.afterClear = document.querySelectorAll('#tbody tr').length;
  localStorage.removeItem('liverV1_records');
  document.title = 'CHECK ' + JSON.stringify(out);
  return JSON.stringify(out);
})()
"""

CHROME = [r"C:\Program Files\Google\Chrome\Application\chrome.exe",
          r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
          r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
          r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"]
exe = next((p for p in CHROME if os.path.exists(p)), None)
if not exe:
    print("NO_BROWSER"); sys.exit(0)
print("browser:", exe)

# ต้องโหลดผ่าน http เพื่อให้ localStorage ทำงาน
url = "http://127.0.0.1:%d/index.html" % PORT
print("page:", urllib.request.urlopen(url, timeout=10).status)

profile = os.path.abspath("_chrome_tmp")
shutil.rmtree(profile, ignore_errors=True)
dump = subprocess.run([exe, "--headless=new", "--disable-gpu", "--no-sandbox",
                       "--user-data-dir=" + profile, "--virtual-time-budget=4000",
                       "--dump-dom", url], capture_output=True, text=True,
                      encoding="utf-8", errors="replace", timeout=90)
title = ""
for line in (dump.stdout or "").splitlines():
    if "CHECK " in line:
        title = line
        break
print("dom_bytes:", len(dump.stdout or ""), "stderr_tail:", (dump.stderr or "")[-200:])
if title:
    import re
    m = re.search(r"CHECK (\{.*\})", title)
    print("RESULT:", json.dumps(json.loads(m.group(1)), ensure_ascii=False, indent=1) if m else title)
else:
    print("NO_RESULT (ดู dom ที่ dump.txt)")
open("_dom.txt", "w", encoding="utf-8").write(dump.stdout or "")
shutil.rmtree(profile, ignore_errors=True)
