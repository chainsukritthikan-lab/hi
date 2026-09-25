# -*- coding: utf-8 -*-
"""CEE's remote control for Chain's Clip Factory (http://127.0.0.1:8840). Standard library only.

  python factory_ctl.py status                 what every worker is doing, shots on the belt, queue
  python factory_ctl.py stats                  average time per stage / per clip
  python factory_ctl.py new "<topic>"          ask the script writer for a script (shown, not queued yet)
  python factory_ctl.py approve | reject       queue or drop the script just written
  python factory_ctl.py retry <folder> <n>     remake one shot
  python factory_ctl.py history [k]            last k finished clips (default 5)
  python factory_ctl.py frames <video> [n]     save n frames tiled in one image for review (default 8)
  python factory_ctl.py blame <worker> "<what went wrong + how to fix>" [--folder F] [--shot N]
  python factory_ctl.py notes [worker]         what each worker has been told
  python factory_ctl.py rules                  the factory's rule library
workers: script, flow, qa, edit, sound, upgrade
"""
import io, os, re, sys, json, subprocess, tempfile, urllib.request, urllib.error

URL = os.environ.get("FACTORY_URL", "http://127.0.0.1:8840").rstrip("/")
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace", line_buffering=True)


def api(method, path, body=None, timeout=900):
    req = urllib.request.Request(URL + path, method=method, headers={"Content-Type": "application/json"},
                                 data=json.dumps(body, ensure_ascii=False).encode("utf-8") if body is not None else None)
    try:
        return json.load(urllib.request.urlopen(req, timeout=timeout))
    except urllib.error.HTTPError as e:
        try:
            return {"error": json.load(e).get("error", str(e)), "http": e.code}
        except Exception:
            return {"error": str(e), "http": e.code}
    except OSError as e:
        sys.exit(f"Factory is not running at {URL} ({e}). Ask Chain to double-click start.bat.")


def status():
    s = api("GET", "/api/state")
    print(f"stage: {s.get('stage')}   queue: {len(s.get('queue', []))} {s.get('queue', [])[:5]}")
    print("workers:")
    for k, w in (s.get("workers") or {}).items():
        print(f"  {k:8} {w.get('status', ''):8} {w.get('text', '')}")
    st = api("GET", "/api/stats")
    for folder, shots in (st.get("active") or {}).items():
        print(f"on belt: {folder}  " + "  ".join(f"#{n}:{v}" for n, v in sorted(shots.items(), key=lambda x: int(x[0]))))
    for n, sh in (s.get("shots") or {}).items():          # shots of the job in focus: {n: {status, reasons, attempts}}
        if isinstance(sh, dict) and sh.get("reasons"):
            print(f"  {s.get('folder', '')} shot {n} ({sh.get('status')}, try {sh.get('attempts', 0)}): {'; '.join(map(str, sh['reasons']))}")
    if s.get("output"):
        print("latest output:", s["output"])
    print("recent log:")
    for ln in (s.get("log") or [])[-10:]:
        print("  ", ln if isinstance(ln, str) else json.dumps(ln, ensure_ascii=False))


def frames(video, n=8):
    tmp = tempfile.mkdtemp(prefix="cee_review_")
    out = os.path.join(tmp, "contact.jpg")
    info = subprocess.run(["ffmpeg", "-hide_banner", "-i", video], capture_output=True, text=True, errors="replace").stderr
    m = re.search(r"Duration: (\d+):(\d+):([\d.]+)", info)
    if not m:
        sys.exit(f"can't read {video}: {info.strip().splitlines()[-1] if info.strip() else 'no ffmpeg?'}")
    dur = int(m[1]) * 3600 + int(m[2]) * 60 + float(m[3])
    cols = 4 if n > 4 else n
    rows = (n + cols - 1) // cols
    fps = n / max(dur, 0.1)
    r = subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", video, "-vf",
                        f"fps={fps:.4f},scale=360:-1,drawtext=text='%{{pts\\:hms}}':x=6:y=6:fontsize=18:fontcolor=yellow:box=1:boxcolor=black@0.6,"
                        f"tile={cols}x{rows}", "-frames:v", "1", out], capture_output=True, text=True)
    if r.returncode != 0:     # drawtext may be missing a font on some Windows builds - retry without timestamps
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", video, "-vf", f"fps={fps:.4f},scale=360:-1,tile={cols}x{rows}",
                        "-frames:v", "1", out], check=True)
    print(f"{n} frames over {dur:.1f}s (one every {dur / n:.1f}s, left-to-right, top-to-bottom):")
    print(out)


def main(a):
    if not a or a[0] in ("-h", "--help", "help"):
        return print(__doc__)
    cmd = a[0]
    if cmd == "status":
        return status()
    if cmd == "stats":
        return print(json.dumps(api("GET", "/api/stats"), ensure_ascii=False, indent=1)[:4000])
    if cmd == "new":
        r = api("POST", "/api/chat", {"text": " ".join(a[1:])})
        return print(r.get("reply", r))
    if cmd == "approve":
        return print(api("POST", "/api/chat", {"approve": True}).get("reply"))
    if cmd == "reject":
        return print(api("POST", "/api/chat", {"reject": True}).get("reply"))
    if cmd == "retry":
        return print(api("POST", "/api/retry", {"folder": a[1], "n": int(a[2])}))
    if cmd == "history":
        k = int(a[1]) if len(a) > 1 else 5
        for h in (api("GET", "/api/state").get("history") or [])[-k:]:
            print(f"{h.get('when', '')}  {h.get('topic', '')}  {h.get('file', '')}")
        return
    if cmd == "frames":
        return frames(a[1], int(a[2]) if len(a) > 2 else 8)
    if cmd == "blame":
        folder = a[a.index("--folder") + 1] if "--folder" in a else ""
        shot = a[a.index("--shot") + 1] if "--shot" in a else ""
        note = a[2] if len(a) > 2 else ""
        r = api("POST", "/api/feedback", {"worker": a[1], "note": note, "folder": folder, "n": shot, "by": "CEE"})
        return print(r.get("line") or r)
    if cmd == "notes":
        notes = api("GET", "/api/feedback").get("notes", {})
        for w, lines in notes.items():
            if len(a) > 1 and w != a[1]:
                continue
            print(f"[{w}]" + ("" if lines else " (clean record)"))
            for ln in lines:
                print("  " + ln)
        return
    if cmd == "rules":
        return print(api("GET", "/api/rules").get("rules", "")[-4000:])
    sys.exit(f"unknown command '{cmd}' - run with --help")


if __name__ == "__main__":
    main(sys.argv[1:])
