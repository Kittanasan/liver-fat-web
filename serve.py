# -*- coding: utf-8 -*-
"""
เสิร์ฟเวอร์แชร์เว็บ liverV1 ให้เครื่องอื่นในวงเดียวกันเปิดได้

วิธีใช้ (ดับเบิลคลิก share-server.bat หรือรันใน terminal):
    py -3 serve.py            # พอร์ต 8080
    py -3 serve.py 9000       # เลือกพอร์ตเอง

เปิดได้ทั้ง http://127.0.0.1:8080/ (เครื่องนี้) และ http://<IP ของเครื่องนี้>:8080/
สำหรับเครื่องอื่นที่อยู่ใน Wi-Fi / LAN เดียวกัน
"""

from __future__ import annotations

import os
import socket
import sys
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

ROOT = os.path.dirname(os.path.abspath(__file__))

# คอนโซล Windows บางเครื่องเป็น cp1252 ทำให้ print ภาษาไทยแล้ว error
for stream in (sys.stdout, sys.stderr):
    try:
        stream.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass


class Handler(SimpleHTTPRequestHandler):
    # ให้ .onnx ถูกส่งแบบ binary ไม่ถูกบีบอัด/ตีความเป็น text
    extensions_map = {
        **SimpleHTTPRequestHandler.extensions_map,
        ".onnx": "application/octet-stream",
        ".wasm": "application/wasm",
        ".mjs": "text/javascript",
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=ROOT, **kwargs)

    def end_headers(self):
        # หน้าเว็บแก้บ่อย ปิด cache เพื่อให้เครื่องอื่นเห็นเวอร์ชันล่าสุด
        self.send_header("Cache-Control", "no-store")
        self.send_header("Access-Control-Allow-Origin", "*")
        super().end_headers()

    def log_message(self, fmt, *args):
        try:
            sys.stdout.write("[web] %s %s\n" % (self.address_string(), fmt % args))
            sys.stdout.flush()
        except Exception:
            pass


def local_ips() -> list[str]:
    ips = set()
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(0.2)
        s.connect(("8.8.8.8", 80))
        ips.add(s.getsockname()[0])
        s.close()
    except OSError:
        pass
    try:
        for info in socket.getaddrinfo(socket.gethostname(), None, socket.AF_INET):
            ips.add(info[4][0])
    except OSError:
        pass
    return sorted(ip for ip in ips if not ip.startswith("127."))


def main() -> int:
    port = 8080
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            print("พอร์ตไม่ถูกต้อง ใช้ค่าเริ่มต้น 8080")
    host = "0.0.0.0"
    try:
        httpd = ThreadingHTTPServer((host, port), Handler)
    except OSError as exc:
        print("[error] เปิดพอร์ต %d ไม่ได้: %s" % (port, exc))
        print("        ลองเลือกพอร์ตอื่น เช่น  py -3 serve.py 8090")
        return 1

    print("=" * 62)
    print(" liverV1 — แชร์เว็บให้เครื่องอื่นเปิดใช้งาน")
    print(" โฟลเดอร์ที่แชร์ : %s" % ROOT)
    print("-" * 62)
    print(" เครื่องนี้        : http://127.0.0.1:%d/" % port)
    ips = local_ips()
    if ips:
        for ip in ips:
            print(" เครื่องอื่นใน LAN: http://%s:%d/" % (ip, port))
    else:
        print(" เครื่องอื่นใน LAN: (หา IP ไม่ได้ — ตรวจว่าเชื่อม Wi-Fi/LAN อยู่)")
    print("-" * 62)
    print(" เงื่อนไข: เครื่องอื่นต้องอยู่ในวง LAN เดียวกัน และ")
    print("          Windows Firewall ต้องอนุญาต Python (Private network)")
    print(" หยุดเซิร์ฟเวอร์: กด Ctrl + C")
    print("=" * 62)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n[stop] ปิดเซิร์ฟเวอร์แล้ว")
    finally:
        httpd.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
