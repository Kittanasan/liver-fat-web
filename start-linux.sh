#!/usr/bin/env bash
# เปิดเซิร์ฟเวอร์แชร์เว็บ liverV1 บน Linux
# ใช้: ./start-linux.sh   หรือ   ./start-linux.sh 9000
set -u
cd "$(dirname "$0")" || exit 1
PORT="${1:-8080}"

PY=""
for c in python3 python; do
  if command -v "$c" >/dev/null 2>&1 && "$c" -c 'import sys;sys.exit(0 if sys.version_info>=(3,8) else 1)' >/dev/null 2>&1; then
    PY="$c"; break
  fi
done

if [ -z "$PY" ]; then
  echo "[error] ไม่พบ Python 3.8 ขึ้นไป"
  echo "        Debian/Ubuntu: sudo apt install python3"
  echo "        Fedora       : sudo dnf install python3"
  echo "        Arch         : sudo pacman -S python"
  echo "        หรือเปิดเว็บออนไลน์ที่ https://kittanasan.github.io/liver-fat-web/"
  exit 1
fi

exec "$PY" serve.py "$PORT"
