# -*- coding: utf-8 -*-
"""
serve.py — เสิร์ฟเว็บ liverV1 ให้เปิดได้จากทุกแพลตฟอร์ม

    python3 serve.py            # พอร์ต 8080
    python3 serve.py 9000       # เลือกพอร์ตเอง
    python3 serve.py 8080 0.0   # ระบุ bind address (0.0.0.0 = เครื่องอื่นในวงเปิดได้)

ใช้ได้ทั้ง Windows / macOS / Linux (Python 3.8+ ไม่ต้องติดตั้งแพ็กเกจเพิ่ม)
- Windows : ดับเบิลคลิก share-server.bat ได้เลย
- macOS   : ดับเบิลคลิก start-mac.command (ครั้งแรกอาจต้อง Allow ใน System Settings)
- Linux   : ./start-linux.sh  หรือ python3 serve.py
- เปิดผ่าน LAN: http://<IP ของเครื่องนี้>:8080/  (ไฟร์วอลล์ต้องอนุญาตพอร์ตนี้)
"""

from __future__ import annotations

import os
import socket
import sys
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

ROOT = os.path.dirname(os.path.abspath(__file__))

# คอนโซลบางระบบ (Windows cp1252 / macOS บาง locale) พิมพ์ภาษาไทยแล้ว error
for stream in (sys.stdout, sys.stderr):
    try:
        stream.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass


class Handler(SimpleHTTPRequestHandler):
    # ชนิดไฟล์ครบทุกแพลตฟอร์ม: .onnx ต้องเป็น binary, .wasm/.mjs/.webmanifest ให้ถูกต้อง
    extensions_map = {
        **SimpleHTTPRequestHandler.extensions_map,
        ".onnx": "application/octet-stream",
        ".wasm": "application/wasm",
        ".mjs": "text/javascript",
        ".webmanifest": "application/manifest+json",
        ".svg": "image/svg+xml",
        ".json": "application/json",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".webp": "image/webp",
        "": "application/octet-stream",
    }

    def __init__(self, *args, directory=None, **kwargs):
        super().__init__(*args, directory=ROOT)

    def handle_one_request(self):
        # ไม่ให้ traceback ยาว ๆ เมื่อผู้ใช้ปิดแท็บกลางทาง (ConnectionAbortedError)
        try:
            super().handle_one_request()
        except (ConnectionError, TimeoutError, BrokenPipeError, OSError):
            self.close_connection = True

    def end_headers(self):
        # หน้าเว็บแก้บ่อย ปิด cache เพื่อให้เครื่องอื่นเห็นเวอร์ชันล่าสุด
        self.send_header("Cache-Control", "no-store")
        self.send_header("Access-Control-Allow-Origin", "*")
        # กันเบราว์เซอร์เดาชนิดไฟล์ผิด (Windows registry / macOS บางตัวคืนค่าแคร่)
        self.send_header("X-Content-Type-Options", "nosniff")
        super().end_headers()

    def log_message(self, fmt, *args):
        try:
            sys.stdout.write("[web] %s %s\n" % (self.address_string(), fmt % args))
            sys.stdout.flush()
        except Exception:
            pass

    # Python 3.8 ไม่มี directory kwarg จึงรับมาแล้วส่งต่อเอง
    def finish(self):
        try:
            super().finish()
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
    host = "0.0.0.0"
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            print("พอร์ตไม่ถูกต้อง ใช้ค่าเริ่มต้น 8080")
    if len(sys.argv) > 2:
        host = sys.argv[2]

    url_host = "127.0.0.1" if host in ("0.0.0.0", "::", "") else host
    try:
        httpd = ThreadingHTTPServer((host, port), Handler)
    except OSError as exc:
        print("[error] เปิดพอร์ต %d ไม่ได้: %s" % (port, exc))
        print("        ลองเลือกพอร์ตอื่น เช่น  python3 serve.py 8090")
        print("        (บน macOS/Linux พอร์ต 80/443 ต้องใช้สิทธิ์ sudo)")
        return 1

    line = "=" * 62
    print(line)
    print(" liverV1 — แชร์เว็บให้เปิดได้จากทุกอุปกรณ์ (Windows / macOS / Linux / มือถือ)")
    print(" โฟลเดอร์ที่แชร์ : %s" % ROOT)
    print("-" * 62)
    print(" เครื่องนี้        : http://%s:%d/" % (url_host, port))
    if os.path.exists(os.path.join(ROOT, "liverV1.onnx")):
        print(" ไฟล์แบบจำลอง      : พบ liverV1.onnx")
    else:
        print(" ไฟล์แบบจำลอง      : ไม่พบ liverV1.onnx (วางไฟล์ไว้ข้าง index.html)")
    if host in ("0.0.0.0", "::", ""):
        ips = local_ips()
        if ips:
            for ip in ips:
                print(" เครื่องอื่นใน LAN: http://%s:%d/" % (ip, port))
        else:
            print(" เครื่องอื่นใน LAN: (หา IP ไม่ได้ — ตรวจว่าเชื่อม Wi-Fi/LAN อยู่)")
        print("-" * 62)
        print(" เงื่อนไข: อุปกรณ์อื่นต้องอยู่ในวง LAN เดียวกัน และไฟร์วอลล์ต้องอนุญาตพอร์ตนี้")
        print("          Windows: ไฟร์วอลล์จะถามตอนเปิดครั้งแรก ให้เลือก Private network")
        print("          macOS  : System Settings > Network > Firewall อนุญาต Python")
        print("          Linux  : sudo ufw allow %d/tcp" % port)
    print("-" * 62)
    print(" หยุดเซิร์ฟเวอร์: กด Ctrl + C")
    print(line)
    try:
        sys.stdout.flush()
    except Exception:
        pass
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n[stop] ปิดเซิร์ฟเวอร์แล้ว")
    finally:
        httpd.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
