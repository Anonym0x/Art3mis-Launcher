"""
ART3MIS Launcher - Python Server v3
======================================
Endpoints:
  /open?path=...        -> Dosya / klasor / program ac
  /pick-file            -> Native dosya secici (tkinter)
  /pick-folder          -> Native klasor secici (tkinter)
  /list-folder?path=... -> Klasor icerigi (isim, boyut, tarih)
  /drives               -> Windows surucü listesi (C:, D: ...)
  /ping                 -> Server saglik kontrolu

BASLATMA: start.bat  veya  python server.py
"""

import http.server, urllib.parse, subprocess
import os, sys, json, threading, webbrowser, time, datetime
from pathlib import Path

PORT      = 7842
HTML_FILE = Path(__file__).parent / "launcher.html"

try:
    import tkinter as tk
    from tkinter import filedialog
    HAS_TK = True
except ImportError:
    HAS_TK = False
    print("[ART3MIS] WARNING: tkinter not found - file picker may not work.")
    print("[ART3MIS] UYARI: tkinter bulunamadi - dosya secici calismayabilir.")

# ── Tkinter dialog thread-safe queue ──
import queue
_dialog_queue  = queue.Queue()
_dialog_result = {}
_result_event  = threading.Event()


def _tk_pick_file(title="Dosya Sec", filetypes=None):
    if not HAS_TK: return None
    if filetypes is None:
        filetypes = [("Calistirilabilir", "*.exe;*.bat;*.cmd;*.lnk"), ("Tum dosyalar", "*.*")]
    root = tk.Tk(); root.withdraw()
    root.wm_attributes("-topmost", True); root.focus_force()
    path = filedialog.askopenfilename(title=title, filetypes=filetypes)
    root.destroy()
    return path or None


def _tk_pick_folder(title="Klasor Sec"):
    if not HAS_TK: return None
    root = tk.Tk(); root.withdraw()
    root.wm_attributes("-topmost", True); root.focus_force()
    path = filedialog.askdirectory(title=title)
    root.destroy()
    return path or None


def _dialog_worker():
    while True:
        try:
            req = _dialog_queue.get(timeout=0.05)
            if req["type"] == "file":
                res = _tk_pick_file(req.get("title","Dosya Sec"), req.get("filetypes"))
            else:
                res = _tk_pick_folder(req.get("title","Klasor Sec"))
            _dialog_result["value"] = res
            _result_event.set()
        except queue.Empty:
            pass


def _fmt_date(ts):
    """Unix timestamp -> 'YYYY-MM-DD HH:MM' string"""
    try:
        return datetime.datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M")
    except Exception:
        return ""


def _get_drives():
    """Windows: C:\\, D:\\ listesi.  Linux/mac: / ve home."""
    drives = []
    if sys.platform == "win32":
        import string
        for letter in string.ascii_uppercase:
            d = f"{letter}:\\"
            if os.path.exists(d):
                drives.append({"name": d, "path": d})
    else:
        drives.append({"name": "/", "path": "/"})
        home = os.path.expanduser("~")
        if home != "/":
            drives.append({"name": "Home", "path": home})
    return drives


class Handler(http.server.BaseHTTPRequestHandler):

    def log_message(self, fmt, *a):
        if a and str(a[1]) not in ("200", "204"):
            print(f"  [?] {a[0]}  {a[1]}")

    def do_OPTIONS(self):
        self.send_response(204); self._cors(); self.end_headers()

    def do_POST(self):
        p = urllib.parse.urlparse(self.path)
        # Body oku
        length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(length) if length else b'{}'
        try:
            data = json.loads(body)
        except Exception:
            data = {}

        # /browse — klasör veya dosya seçici (mode: 'folder' veya 'file')
        if p.path == '/browse':
            if not HAS_TK:
                return self._json(200, {'ok': False, 'error': 'tkinter yok'})
            mode = data.get('mode', 'folder')
            _result_event.clear()
            _dialog_queue.put({'type': mode})
            _result_event.wait(timeout=120)
            path = _dialog_result.get('value')
            if path:
                self._json(200, {'ok': True, 'path': os.path.normpath(path)})
            else:
                self._json(200, {'ok': False, 'cancelled': True})

        else:
            self._json(404, {'ok': False, 'error': 'endpoint yok'})

    def do_GET(self):
        p = urllib.parse.urlparse(self.path)
        q = urllib.parse.parse_qs(p.query)

        # / veya /index.html → launcher.html servis et
        if p.path in ("/", "/index.html", "/launcher.html"):
            if not HTML_FILE.exists():
                self.send_response(404); self._cors(); self.end_headers()
                self.wfile.write(b"launcher.html bulunamadi")
                return
            body = HTML_FILE.read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", len(body))
            self._cors(); self.end_headers()
            self.wfile.write(body)
            return

        # /open
        if p.path == "/open":
            raw = q.get("path", [None])[0]
            if not raw: return self._json(400, {"ok": False, "error": "path eksik"})
            self._json(200, self._launch(urllib.parse.unquote(raw)))

        # /pick-file
        elif p.path == "/pick-file":
            if not HAS_TK: return self._json(200, {"ok": False, "error": "tkinter yok"})
            _result_event.clear()
            _dialog_queue.put({"type": "file"})
            _result_event.wait(timeout=120)
            path = _dialog_result.get("value")
            if path:
                self._json(200, {"ok": True, "path": os.path.normpath(path)})
            else:
                self._json(200, {"ok": False, "cancelled": True})

        # /pick-folder
        elif p.path == "/pick-folder":
            if not HAS_TK: return self._json(200, {"ok": False, "error": "tkinter yok"})
            _result_event.clear()
            _dialog_queue.put({"type": "folder"})
            _result_event.wait(timeout=120)
            path = _dialog_result.get("value")
            if path:
                self._json(200, {"ok": True, "path": os.path.normpath(path)})
            else:
                self._json(200, {"ok": False, "cancelled": True})

        # /list-folder  — returns dirs+files with size+created date
        elif p.path == "/list-folder":
            raw = q.get("path", [None])[0]
            if not raw: return self._json(400, {"ok": False, "error": "path eksik"})
            target = os.path.normpath(os.path.expandvars(os.path.expanduser(urllib.parse.unquote(raw))))
            if not os.path.isdir(target):
                return self._json(200, {"ok": False, "error": f"Klasor bulunamadi: {target}"})
            try:
                dirs, files = [], []
                for entry in sorted(os.scandir(target), key=lambda e: (not e.is_dir(), e.name.lower())):
                    try:
                        st = entry.stat()
                        created = _fmt_date(st.st_ctime)
                        modified = _fmt_date(st.st_mtime)
                        if entry.is_dir(follow_symlinks=False):
                            dirs.append({
                                "name": entry.name,
                                "path": os.path.normpath(entry.path),
                                "created": created,
                                "modified": modified
                            })
                        else:
                            files.append({
                                "name": entry.name,
                                "path": os.path.normpath(entry.path),
                                "size": st.st_size,
                                "created": created,
                                "modified": modified,
                                "ext": os.path.splitext(entry.name)[1].lower()
                            })
                    except (PermissionError, OSError):
                        pass
                parent_path = os.path.dirname(target)
                has_parent  = os.path.normpath(parent_path) != os.path.normpath(target)
                self._json(200, {
                    "ok": True, "path": target, "dirs": dirs, "files": files,
                    "parent": os.path.normpath(parent_path) if has_parent else None,
                    "parentLabel": os.path.basename(parent_path) or parent_path
                })
            except PermissionError:
                self._json(200, {"ok": False, "error": "Erisim izni yok"})
            except Exception as e:
                self._json(200, {"ok": False, "error": str(e)})

        # /drives
        elif p.path == "/drives":
            self._json(200, {"ok": True, "drives": _get_drives()})

        # /ping
        elif p.path == "/ping":
            self._json(200, {"ok": True, "platform": sys.platform, "tk": HAS_TK, "ver": "3.1"})

        # /file?path=... — yerel ses dosyasi servis eder (MP3, FLAC, OGG, WAV, M4A vb.)
        elif p.path == "/file":
            raw = q.get("path", [None])[0]
            if not raw:
                return self._json(400, {"ok": False, "error": "path eksik"})
            fpath = os.path.normpath(urllib.parse.unquote(raw))
            if not os.path.isfile(fpath):
                return self._json(404, {"ok": False, "error": "Dosya bulunamadi"})
            AUDIO_MIME = {
                ".mp3": "audio/mpeg", ".flac": "audio/flac",
                ".ogg": "audio/ogg",  ".wav": "audio/wav",
                ".m4a": "audio/mp4",  ".aac": "audio/aac",
                ".opus": "audio/ogg", ".wma": "audio/x-ms-wma",
            }
            ext = os.path.splitext(fpath)[1].lower()
            mime = AUDIO_MIME.get(ext, "application/octet-stream")
            try:
                size = os.path.getsize(fpath)
                range_hdr = self.headers.get("Range", "")
                start, end = 0, size - 1
                status = 200
                if range_hdr.startswith("bytes="):
                    parts = range_hdr[6:].split("-")
                    start = int(parts[0]) if parts[0] else 0
                    end = int(parts[1]) if parts[1] else size - 1
                    status = 206
                length = end - start + 1
                self.send_response(status)
                self.send_header("Content-Type", mime)
                self.send_header("Content-Length", length)
                self.send_header("Accept-Ranges", "bytes")
                if status == 206:
                    self.send_header("Content-Range", f"bytes {start}-{end}/{size}")
                self._cors()
                self.end_headers()
                with open(fpath, "rb") as f:
                    f.seek(start)
                    remaining = length
                    while remaining > 0:
                        chunk = f.read(min(65536, remaining))
                        if not chunk: break
                        self.wfile.write(chunk)
                        remaining -= len(chunk)
            except Exception as e:
                print(f"  [!] File stream error / Dosya servisi hatasi: {e}")

        else:
            self._json(404, {"ok": False, "error": "endpoint yok"})

    def _launch(self, target: str) -> dict:
        path = os.path.normpath(os.path.expandvars(os.path.expanduser(target)))
        if not os.path.exists(path):
            return {"ok": False, "error": f"Bulunamadi: {path}"}
        try:
            if sys.platform == "win32":
                os.startfile(path)
            elif sys.platform == "darwin":
                subprocess.Popen(["open", path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            else:
                subprocess.Popen(["xdg-open", path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print(f"  [+] Launched / Acildi : {path}")
            return {"ok": True}
        except Exception as e:
            print(f"  [!] Error / Hata : {e}")
            return {"ok": False, "error": str(e)}

    def _cors(self):
        self.send_header("Access-Control-Allow-Origin",  "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def _json(self, code, data):
        body = json.dumps(data, ensure_ascii=False).encode()
        self.send_response(code)
        self.send_header("Content-Type",   "application/json; charset=utf-8")
        self.send_header("Content-Length", len(body))
        self._cors(); self.end_headers()
        self.wfile.write(body)


def _open_browser():
    time.sleep(1.2)
    # Her zaman localhost:7842 aç — file:// değil!
    # file:// ile açılırsa server özellikleri çalışmaz
    webbrowser.open(f"http://localhost:{PORT}")


def main():
    srv = http.server.ThreadingHTTPServer(("0.0.0.0", PORT), Handler)
    # Windows CMD encoding fix — UTF-8 output
    if sys.platform == "win32":
        try:
            import ctypes
            ctypes.windll.kernel32.SetConsoleOutputCP(65001)
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass

    # Sistem dilini tespit et (modül seviyesinde IS_TR değişkeni kullanılır)
    if IS_TR:
        tk_status = "MEVCUT" if HAS_TK else "YOK"
        print()
        print("  +===========================================+")
        print("  |                                           |")
        print("  |         ART3MIS  Launcher  v3.1          |")
        print("  |                                           |")
        print(f"  |   Sunucu    ->  localhost:{PORT}            |")
        print(f"  |   Platform  ->  {sys.platform:<26}|")
        print(f"  |   Tkinter   ->  {tk_status:<26}|")
        print("  |                                           |")
        print("  +===========================================+")
        print()
        print("  Sunucu baslatildi.")
        print("  Tarayici 1 saniye sonra aciliyor...")
        print("  Durdurmak icin Ctrl+C")
        print()
        print("  -------------------------------------------")
        print()
    else:
        tk_status = "FOUND" if HAS_TK else "MISSING"
        print()
        print("  |                                           |")
        print("  |         ART3MIS  Launcher  v3.1          |")
        print("  |                                           |")
        print(f"  |   Server    ->  localhost:{PORT}            |")
        print(f"  |   Platform  ->  {sys.platform:<26}|")
        print(f"  |   Tkinter   ->  {tk_status:<26}|")
        print("  |                                           |")
        print("  +===========================================+")
        print()
        print("  Server is running.")
        print("  Opening browser in 1 second...")
        print("  Press Ctrl+C to stop.")
        print()
        print("  -------------------------------------------")
        print()
    threading.Thread(target=lambda: srv.serve_forever(), daemon=True).start()
    threading.Thread(target=_open_browser, daemon=True).start()
    _dialog_worker()


# Sistem dilini modül seviyesinde tespit et
_lang_env = os.environ.get("LANG", os.environ.get("LANGUAGE", "")).lower()
if sys.platform == "win32":
    try:
        import ctypes as _ctypes
        _lcid = _ctypes.windll.kernel32.GetUserDefaultUILanguage()
        IS_TR = (_lcid & 0xFF) == 0x1F
    except Exception:
        IS_TR = "tr" in _lang_env
else:
    IS_TR = _lang_env.startswith("tr")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        if IS_TR:
            print("\n  Sunucu durduruldu.\n")
        else:
            print("\n  Server stopped.\n")
