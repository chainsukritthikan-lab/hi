# Tiny local web server for the CEE orb (127.0.0.1 only).
# Runs under pythonw (no console), so logs go to devnull instead of a missing stderr.
import functools, http.server, os, sys

sys.stdout = sys.stderr = open(os.devnull, "w")
root = os.path.dirname(os.path.abspath(__file__))


class Handler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        super().end_headers()


http.server.ThreadingHTTPServer(
    ("127.0.0.1", 8765), functools.partial(Handler, directory=root)
).serve_forever()
