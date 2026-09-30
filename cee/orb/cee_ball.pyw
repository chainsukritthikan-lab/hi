# CEE taskbar ball (Windows). A little yellow face that sits on the taskbar.
#   idle      -> dull yellow, bored face
#   Ctrl+Shift (tap) or click -> bright yellow, happy, listening
#   then it thinks, talks back, and goes back to idle.
# Right-click: EN/TH, open the big orb, quit. Drag it to move it.
#
# Ears and mouth are a hidden Microsoft Edge window (ear.html: Edge speech
# recognition + natural voices). The brain call goes from here to CEE's local API.
import ctypes, ctypes.wintypes as wt, json, math, os, queue, re, subprocess, sys
import threading, time, urllib.request, http.server
import tkinter as tk

sys.stdout = sys.stderr = open(os.devnull, "w")  # pythonw has no console
HERE = os.path.dirname(os.path.abspath(__file__))
PORT = 8766
SETTINGS = os.path.join(HERE, "ball.json")
VOICE_STYLE = (
    "You are in a live spoken conversation through the CEE taskbar ball; your reply is read aloud. "
    "Speak like JARVIS from Iron Man: calm, polished, quietly witty and always one step ahead. "
    "Call the user 'boss' now and then. Sound human: contractions, a brief natural reaction first. "
    "Keep it to one to three short sentences unless asked for detail. No markdown, lists, emojis or URLs."
)

user32 = ctypes.windll.user32
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except Exception:
    pass


def load_settings():
    try:
        with open(SETTINGS, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def save_settings(s):
    try:
        with open(SETTINGS, "w", encoding="utf-8") as f:
            json.dump(s, f)
    except Exception:
        pass


def api_config():
    with open(os.path.join(HERE, "config.js"), encoding="utf-8") as f:
        js = f.read()
    url = re.search(r"url:\s*'([^']+)'", js).group(1)
    key = re.search(r"key:\s*'([^']+)'", js).group(1)
    return url, key


def ask_cee(text):
    url, key = api_config()
    body = json.dumps({
        "model": "cee", "input": text, "conversation": "cee-orb", "stream": False,
        "instructions": VOICE_STYLE, "model_options": {"reasoning_effort": "low"},
    }).encode()
    req = urllib.request.Request(url + "/responses", body, {
        "Content-Type": "application/json", "Authorization": "Bearer " + key})
    with urllib.request.urlopen(req, timeout=240) as r:
        data = json.load(r)
    if data.get("output_text"):
        return data["output_text"]
    parts = []
    for item in data.get("output", []):
        for c in item.get("content", []) or []:
            if c.get("type") in ("output_text", "text") and c.get("text"):
                parts.append(c["text"])
    return "\n".join(parts).strip() or "Hmm, I came up empty on that one."


# ---------- the ear (hidden Edge window) talks to us over this tiny server ----------
events = queue.Queue()          # ear -> ball
ear = {"id": None, "cmds": queue.Queue(), "hwnd_hidden": False}


class EarHandler(http.server.BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def _send(self, code, body=b"", ctype="application/json"):
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path == "/" or self.path.startswith("/?"):
            with open(os.path.join(HERE, "ear.html"), "rb") as f:
                return self._send(200, f.read(), "text/html; charset=utf-8")
        if self.path.startswith("/cmd"):
            me = self.path.split("id=", 1)[-1]
            if me != ear["id"]:
                return self._send(200, b'{"cmd":"close"}')
            try:
                cmd = ear["cmds"].get(timeout=20)   # long-poll: no browser timers needed
            except queue.Empty:
                cmd = {}
            return self._send(200, json.dumps(cmd).encode())
        self._send(404)

    def do_POST(self):
        n = int(self.headers.get("Content-Length") or 0)
        try:
            msg = json.loads(self.rfile.read(n) or b"{}")
        except Exception:
            msg = {}
        if self.path == "/hello":
            ear["id"] = msg.get("id")
            ear["cmds"] = queue.Queue()
        events.put((self.path.strip("/"), msg))
        self._send(200, b"{}")


def start_server():
    srv = http.server.ThreadingHTTPServer(("127.0.0.1", PORT), EarHandler)
    threading.Thread(target=srv.serve_forever, daemon=True).start()


def find_edge():
    for p in (os.environ.get("ProgramFiles(x86)", ""), os.environ.get("ProgramFiles", "")):
        exe = os.path.join(p, "Microsoft", "Edge", "Application", "msedge.exe")
        if os.path.exists(exe):
            return exe
    return None


def launch_ear():
    edge = find_edge()
    if not edge:
        return None
    return subprocess.Popen([
        edge, f"--app=http://127.0.0.1:{PORT}/",
        "--user-data-dir=" + os.path.join(HERE, "ear-profile"),
        "--no-first-run", "--no-default-browser-check",
        "--autoplay-policy=no-user-gesture-required",   # lets it talk without a click
        "--use-fake-ui-for-media-stream",               # mic allowed, no popup
        "--disable-background-timer-throttling", "--disable-renderer-backgrounding",
        "--disable-backgrounding-occluded-windows",
        "--disable-features=CalculateNativeWinOcclusion",
        "--window-size=320,240", "--window-position=40,40",
    ])


def ear_window(show):
    """Park the Edge 'CEE Ear' window off-screen (still 'visible' so Edge keeps listening),
    without a taskbar button - or bring it back on screen to fix the mic."""
    found = []

    @ctypes.WINFUNCTYPE(wt.BOOL, wt.HWND, wt.LPARAM)
    def cb(hwnd, _):
        buf = ctypes.create_unicode_buffer(256)
        user32.GetWindowTextW(hwnd, buf, 256)
        if buf.value.startswith("CEE Ear") and user32.IsWindowVisible(hwnd):
            found.append(hwnd)
        return True
    user32.EnumWindows(cb, 0)
    for h in found:
        if show:
            user32.SetWindowPos(h, 0, 120, 120, 420, 320, 0x0040)          # SWP_SHOWWINDOW
            user32.SetForegroundWindow(h)
        else:
            user32.ShowWindow(h, 0)                                        # hide, restyle, re-show
            ex = user32.GetWindowLongW(h, -20)
            user32.SetWindowLongW(h, -20, (ex | 0x80) & ~0x40000)          # TOOLWINDOW: no taskbar button
            user32.SetWindowPos(h, 0, -20000, -20000, 320, 240, 0x0010)    # SWP_NOACTIVATE
            user32.ShowWindow(h, 4)                                        # SW_SHOWNOACTIVATE
    return bool(found)


# ---------- Ctrl+Shift detector (tap = both down, released, nothing else pressed) ----------
MODS = {0x10, 0x11, 0xA0, 0xA1, 0xA2, 0xA3}
OTHER = [vk for vk in range(0x08, 0xFF) if vk not in MODS and vk not in (0x12, 0xA4, 0xA5)] + [0x12]


def down(vk):
    return bool(user32.GetAsyncKeyState(vk) & 0x8000)


class Chord:
    def __init__(self):
        self.armed = False
        self.spoiled = False

    def poll(self):
        ctrl, shift = down(0x11), down(0x10)
        if ctrl and shift and not self.armed:
            self.armed, self.spoiled = True, False
        if not self.armed:
            return False
        if any(down(vk) for vk in OTHER) or down(0x01) or down(0x02):
            self.spoiled = True       # Ctrl+Shift+Esc, Ctrl+Shift+T, Ctrl+C... not for us
        if not ctrl and not shift:
            self.armed = False
            return not self.spoiled
        return False


# ---------- the ball ----------
KEY = "#010203"   # transparent colour


class Ball:
    def __init__(self):
        self.s = load_settings()
        self.lang = self.s.get("lang", "en-US")
        self.scale = user32.GetDpiForSystem() / 96 if hasattr(user32, "GetDpiForSystem") else 1
        self.size = int(34 * self.scale)
        self.state = "idle"          # idle | listening | thinking | speaking | oops
        self.t0 = time.time()
        self.heard = ""
        self.chord = Chord()
        self.ear_proc = None
        self.ear_ready = False
        self.drag = None

        r = self.root = tk.Tk()
        r.overrideredirect(True)
        r.attributes("-topmost", True)
        r.configure(bg=KEY)
        r.attributes("-transparentcolor", KEY)
        self.c = tk.Canvas(r, width=self.size + 14, height=self.size + 14, bg=KEY, highlightthickness=0)
        self.c.pack()
        r.geometry(f"+{self.s.get('x', self.default_xy()[0])}+{self.s.get('y', self.default_xy()[1])}")

        self.bubble = tk.Toplevel(r)
        self.bubble.overrideredirect(True)
        self.bubble.attributes("-topmost", True)
        self.bubble.configure(bg="#1f1f1f")
        self.btext = tk.Label(self.bubble, bg="#1f1f1f", fg="#ffe98a", font=("Segoe UI", 10),
                              wraplength=int(300 * self.scale), justify="left", padx=10, pady=6)
        self.btext.pack()
        self.bubble.withdraw()
        self.bubble_until = 0

        self.menu = tk.Menu(r, tearoff=0)
        self.menu.add_command(label="Talk  (Ctrl+Shift)", command=self.toggle)
        self.menu.add_command(label="", command=self.switch_lang)
        self.menu.add_command(label="Open the big orb", command=self.open_orb)
        self.menu.add_command(label="Show ear window (fix mic)", command=lambda: ear_window(True))
        self.menu.add_separator()
        self.menu.add_command(label="Quit CEE ball", command=self.quit)
        self.refresh_menu()

        self.c.bind("<ButtonPress-1>", self.press)
        self.c.bind("<B1-Motion>", self.move)
        self.c.bind("<ButtonRelease-1>", self.release)
        self.c.bind("<Button-3>", lambda e: self.menu.tk_popup(e.x_root, e.y_root))

        start_server()
        self.ear_proc = launch_ear()
        if not self.ear_proc:
            self.say_bubble("I need Microsoft Edge for my ears and voice.", 10)
        self.tick()

    # --- placement ---
    def default_xy(self):
        sw, sh = user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)
        rect = wt.RECT()
        user32.SystemParametersInfoW(0x30, 0, ctypes.byref(rect), 0)  # work area
        bar = max(sh - rect.bottom, int(40 * self.scale))
        return int(14 * self.scale), sh - bar + (bar - self.size - 14) // 2

    def press(self, e):
        self.drag = (e.x_root, e.y_root, self.root.winfo_x(), self.root.winfo_y(), False)

    def move(self, e):
        x0, y0, wx, wy, _ = self.drag
        if abs(e.x_root - x0) + abs(e.y_root - y0) > 4:
            self.drag = (x0, y0, wx, wy, True)
            self.root.geometry(f"+{wx + e.x_root - x0}+{wy + e.y_root - y0}")

    def release(self, e):
        moved = self.drag and self.drag[4]
        self.drag = None
        if moved:
            self.s["x"], self.s["y"] = self.root.winfo_x(), self.root.winfo_y()
            save_settings(self.s)
        else:
            self.toggle()

    # --- menu actions ---
    def refresh_menu(self):
        self.menu.entryconfig(1, label="Language: English -> switch to Thai" if self.lang == "en-US"
                              else "Language: Thai -> switch to English")

    def switch_lang(self):
        self.lang = "th-TH" if self.lang == "en-US" else "en-US"
        self.s["lang"] = self.lang
        save_settings(self.s)
        self.refresh_menu()
        self.say_bubble("Listening in Thai now." if self.lang == "th-TH" else "Listening in English now.", 3)

    def open_orb(self):
        edge = find_edge()
        if edge:
            subprocess.Popen([edge, "--app=http://127.0.0.1:8765/"])
        else:
            os.startfile("http://127.0.0.1:8765/")

    def quit(self):
        try:
            if self.ear_proc:
                self.ear_proc.terminate()
        finally:
            self.root.destroy()

    # --- talking ---
    def send(self, cmd):
        ear["cmds"].put(cmd)

    def set_state(self, st):
        self.state, self.t0 = st, time.time()

    def toggle(self):
        if self.state == "idle" or self.state == "oops":
            if not self.ear_ready:
                self.set_state("oops")
                return self.say_bubble("My ears are still waking up, give me a sec...", 4)
            self.heard = ""
            self.set_state("listening")
            self.send({"cmd": "listen", "lang": self.lang})
        else:   # tap again = stop / shush
            self.send({"cmd": "stop"})
            self.set_state("idle")
            self.bubble.withdraw()

    def think(self, text):
        self.set_state("thinking")
        self.say_bubble("You: " + text, 60)

        def work():
            try:
                reply = ask_cee(text)
            except Exception as e:
                reply = None
                err = str(e)
            events.put(("reply", {"text": reply} if reply else {"error": err}))
        threading.Thread(target=work, daemon=True).start()

    def say_bubble(self, text, secs):
        self.btext.config(text=text if len(text) < 400 else text[:400] + "...")
        self.bubble.update_idletasks()
        bw, bh = self.bubble.winfo_reqwidth(), self.bubble.winfo_reqheight()
        x = max(0, min(self.root.winfo_x(), user32.GetSystemMetrics(0) - bw - 4))
        y = self.root.winfo_y() - bh - 6
        if y < 0:
            y = self.root.winfo_y() + self.size + 18
        self.bubble.geometry(f"+{x}+{y}")
        self.bubble.deiconify()
        self.bubble.lift()
        self.bubble_until = time.time() + secs

    def handle(self, kind, msg):
        if kind == "hello":
            self.ear_ready = True
            ear_window(False)
        elif kind == "heard":
            if self.state != "listening":
                return
            if msg.get("error"):
                self.set_state("oops")
                hint = {"not-allowed": "I can't use the mic. Right-click me > Show ear window, then allow the microphone.",
                        "no-speech": "Didn't catch anything. Tap Ctrl+Shift and try again.",
                        "network": "My ears need internet (Edge speech)."}.get(msg["error"], "Ear trouble: " + msg["error"])
                return self.say_bubble(hint, 6)
            self.heard = msg.get("text", "")
            if self.heard:
                self.say_bubble("You: " + self.heard, 30)
            if msg.get("final"):
                if self.heard.strip():
                    self.think(self.heard.strip())
                else:
                    self.set_state("idle")
                    self.bubble.withdraw()
        elif kind == "reply":
            if self.state != "thinking":
                return
            if msg.get("error"):
                self.set_state("oops")
                return self.say_bubble("I can't reach my brain right now. Is CEE running? (" + msg["error"][:80] + ")", 8)
            self.set_state("speaking")
            self.say_bubble(msg["text"], 120)
            self.send({"cmd": "speak", "text": msg["text"], "lang": self.lang})
        elif kind == "spoken":
            if self.state == "speaking":
                self.set_state("idle")
                self.bubble_until = time.time() + 5

    # --- main loop ---
    def tick(self):
        try:
            while True:
                self.handle(*events.get_nowait())
        except queue.Empty:
            pass
        if self.chord.poll():
            self.toggle()
        if self.state == "oops" and time.time() - self.t0 > 6:
            self.set_state("idle")
        if self.bubble_until and time.time() > self.bubble_until and self.state in ("idle", "oops"):
            self.bubble.withdraw()
            self.bubble_until = 0
        if int(time.time() * 2) % 4 == 0:
            self.root.attributes("-topmost", True)   # stay above the taskbar
            self.root.lift()
        self.draw()
        self.root.after(40, self.tick)

    def draw(self):
        c, s, t = self.c, self.size, time.time()
        c.delete("all")
        pad = 7
        happy = self.state in ("listening", "thinking", "speaking")
        grow = 0
        if self.state == "listening":
            grow = 1.5 + 1.5 * math.sin(t * 6)
        elif self.state == "idle":
            pad += 1 if math.sin(t * 1.2) > 0.6 else 0     # slow sulky bob
        x0, y0, x1, y1 = pad - grow, pad - grow, pad + s + grow, pad + s + grow
        if happy:   # glow ring
            c.create_oval(x0 - 3, y0 - 3, x1 + 3, y1 + 3, outline="#fff3a0", width=2)
        fill = "#ffd21f" if happy else "#c9a93a" if self.state == "idle" else "#e0b030"
        c.create_oval(x0, y0, x1, y1, fill=fill, outline="#8a6a00" if not happy else "#e0a800", width=1)
        cx, cy, u = (x0 + x1) / 2, (y0 + y1) / 2, s / 34
        ink = "#3b2a00"
        blink = (t % 4.5) < 0.12
        if self.state == "idle":
            # bored: flat half-closed eyes, little frown
            for ex in (-7, 7):
                c.create_line(cx + (ex - 3) * u, cy - 3 * u, cx + (ex + 3) * u, cy - 3 * u, fill=ink, width=max(2, 2 * u))
            c.create_arc(cx - 6 * u, cy + 5 * u, cx + 6 * u, cy + 13 * u, start=20, extent=140,
                         style="arc", outline=ink, width=max(2, 2 * u))
        elif self.state == "oops":
            for ex in (-7, 7):
                c.create_oval(cx + (ex - 2) * u, cy - 6 * u, cx + (ex + 2) * u, cy - 1 * u, fill=ink, outline="")
            c.create_oval(cx - 3 * u, cy + 5 * u, cx + 3 * u, cy + 10 * u, outline=ink, width=max(2, 2 * u))
        else:
            look = -2 * u if self.state == "thinking" else 0
            for ex in (-7, 7):
                if blink:
                    c.create_line(cx + (ex - 3) * u, cy - 4 * u, cx + (ex + 3) * u, cy - 4 * u, fill=ink, width=2)
                else:
                    c.create_arc(cx + (ex - 3.5) * u, cy - 8 * u + look, cx + (ex + 3.5) * u, cy - 1 * u + look,
                                 start=0, extent=180, style="arc", outline=ink, width=max(2, 2.2 * u))   # ^ ^ happy eyes
            if self.state == "speaking":
                o = 2 + 5 * abs(math.sin(t * 11))
                c.create_oval(cx - 5 * u, cy + 4 * u, cx + 5 * u, cy + (5 + o) * u, fill="#7a2b00", outline=ink)
            elif self.state == "thinking":
                for i in range(3):
                    on = int(t * 3) % 3 == i
                    c.create_oval(cx + (i - 1) * 5 * u - 1.5 * u, cy + 7 * u - 1.5 * u,
                                  cx + (i - 1) * 5 * u + 1.5 * u, cy + 7 * u + 1.5 * u,
                                  fill=ink if on else "#a88400", outline="")
            else:
                c.create_arc(cx - 8 * u, cy - 2 * u, cx + 8 * u, cy + 12 * u, start=200, extent=140,
                             style="chord", fill="#7a2b00", outline=ink, width=max(2, 2 * u))   # big smile
            c.create_oval(cx - 12 * u, cy + 2 * u, cx - 8 * u, cy + 5 * u, fill="#ffab5e", outline="")   # cheeks
            c.create_oval(cx + 8 * u, cy + 2 * u, cx + 12 * u, cy + 5 * u, fill="#ffab5e", outline="")


if __name__ == "__main__":
    # one ball at a time: if the port is taken, another ball is already running
    import socket
    probe = socket.socket()
    try:
        probe.bind(("127.0.0.1", PORT))
        probe.close()
    except OSError:
        sys.exit(0)
    Ball().root.mainloop()
