#!/bin/bash
# เปิดเซิร์ฟเวอร์แชร์เว็บ liverV1 บน macOS — ดับเบิลคลิกไฟล์นี้ใน Finder
# (ถ้าเปิดไม่ได้ครั้งแรก: คลิกขวา > Open > Open หรือ chmod +x start-mac.command)
cd "$(dirname "$0")" || exit 1
PORT="${1:-8080}"

pick_python() {
  for c in python3 python; do
    if command -v "$c" >/dev/null 2>&1; then
      if "$c" -c 'import sys;sys.exit(0 if sys.version_info>=(3,8) else 1)' >/dev/null 2>&1; then
        echo "$c"; return 0
      fi
    fi
  done
  return 1
}

PY=$(pick_python)
if [ -z "$PY" ]; then
  echo
  echo "[error] ไม่พบ Python 3.8 ขึ้นไป"
  echo "        ติดตั้งจาก https://www.python.org/downloads/ หรือรัน: xcode-select --install"
  echo "        หรือเปิดเว็บออนไลน์ที่ https://kittanasan.github.io/liver-fat-web/"
  echo
  read -r -p "กด Enter เพื่อปิด..." _
  exit 1
fi

echo "ใช้ $PY — กำลังเปิดเซิร์ฟเวอร์ที่พอร์ต $PORT"
"$PY" serve.py "$PORT"
echo
read -r -p "ปิดเซิร์ฟเวอร์แล้ว กด Enter เพื่อปิดหน้าต่าง..." _
