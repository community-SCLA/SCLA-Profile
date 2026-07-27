#!/usr/bin/env python3
"""Review dashboard for SCLA HyperFrames lesson builds — one stable URL.

The problem this solves: `hyperframes preview` can only ever serve ONE
workspace (it requires an index.html in its cwd), so reviewing N videos meant
N terminal commands on N remembered ports, with no way to see which builds
were even ready. This serves a single page on a fixed port that:

  * lists every workspace in renders-hyperframes/
  * runs render-qa/preflight.py live for each (~0.4s) to show READY / NOT READY
  * launches a preview on demand when you click Watch, and redirects you to it

Usage:  bash scripts/review.sh        (starts this and prints the URL)
        python3 scripts/review.py     (same, no wrapper)

Stdlib only — no install step, so it survives a fresh Codespace.
"""

import html
import json
import os
import re
import socket
import subprocess
import sys
import threading
import time
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse, parse_qs

REPO = Path(__file__).resolve().parent.parent
ROOT = REPO / "projects/video-production/renders-hyperframes"
PREFLIGHT = REPO / "projects/video-production/render-qa/preflight.py"

DASH_PORT = int(os.environ.get("SCLA_REVIEW_PORT", "3002"))
# Preview servers get their own ports. The dashboard owns DASH_PORT.
PREVIEW_PORTS = [3003, 3004, 3005, 3006, 3007, 3008]
HF_PKG = "hyperframes@0.7.76"

# stem -> port, for previews this process knows about
LAUNCHED = {}
LOCK = threading.Lock()

# SCLA web palette (brand/visual-identity.md)
C = {
    "navy": "#0d2437",
    "navy_dark": "#0a1e2f",
    "blue": "#3393d6",
    "yellow": "#eaab2d",
    "cultured": "#f6f6f9",
    "subtle": "#e5eff6",
    "border": "#cccedf",
    "muted": "#98a4cc",
    "body": "#292f35",
}


# ---------------------------------------------------------------- helpers


def base_url(port):
    """External URL for a port — forwarded https in a Codespace, else local."""
    name = os.environ.get("CODESPACE_NAME")
    domain = os.environ.get("GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN")
    if name and domain:
        return f"https://{name}-{port}.{domain}"
    return f"http://localhost:{port}"


def port_open(port):
    with socket.socket() as s:
        s.settimeout(0.4)
        return s.connect_ex(("127.0.0.1", port)) == 0


def project_on_port(port):
    """Which workspace stem is the preview server on `port` serving?"""
    try:
        with urllib.request.urlopen(
            f"http://127.0.0.1:{port}/api/projects", timeout=2
        ) as r:
            projects = json.load(r).get("projects", [])
            return projects[0]["id"] if projects else None
    except Exception:
        return None


def workspaces():
    if not ROOT.is_dir():
        return []
    out = []
    for d in sorted(ROOT.iterdir()):
        if d.name.startswith("_") or not d.is_dir():
            continue
        if (d / "index.html").is_file():
            out.append(d.name)
    return out


CHECK_RE = re.compile(r"^\[(ok|!!)\s*\]\s*(\S+)", re.M)


def preflight(stem):
    """Run the deterministic gate. Returns (ready, [failing check names])."""
    try:
        p = subprocess.run(
            [sys.executable, str(PREFLIGHT), str(ROOT / stem)],
            capture_output=True,
            text=True,
            timeout=120,
        )
    except Exception as e:
        return False, [f"gate error: {e}"]
    failed = [name for mark, name in CHECK_RE.findall(p.stdout) if mark == "!!"]
    return p.returncode == 0, failed


def scan_all():
    """Gate every workspace in parallel — the whole set lands in well under a second."""
    stems = workspaces()
    results = {}

    def work(s):
        results[s] = preflight(s)

    threads = [threading.Thread(target=work, args=(s,)) for s in stems]
    for t in threads:
        t.start()
    for t in threads:
        t.join(timeout=130)
    return [(s, *results.get(s, (False, ["timed out"]))) for s in stems]


def find_preview(stem):
    """Port already serving `stem`, or None. Survives dashboard restarts."""
    with LOCK:
        port = LAUNCHED.get(stem)
    if port and port_open(port) and project_on_port(port) == stem:
        return port
    for port in PREVIEW_PORTS:
        if port_open(port) and project_on_port(port) == stem:
            with LOCK:
                LAUNCHED[stem] = port
            return port
    return None


def free_port():
    """A preview port with nothing on it, else the one serving the oldest claim."""
    for port in PREVIEW_PORTS:
        if not port_open(port):
            return port
    # All busy — recycle the first one not currently claimed by a live project.
    for port in PREVIEW_PORTS:
        if project_on_port(port) is None:
            return port
    return PREVIEW_PORTS[0]


def launch_preview(stem):
    """Start a preview for `stem`; returns its port immediately (may not be up yet)."""
    existing = find_preview(stem)
    if existing:
        return existing
    port = free_port()
    if port_open(port):
        subprocess.run(
            ["pkill", "-f", f"[h]yperframes.* preview --port {port}"],
            capture_output=True,
        )
        time.sleep(2)
    subprocess.Popen(
        ["npx", "--yes", HF_PKG, "preview", "--port", str(port)],
        cwd=str(ROOT / stem),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        start_new_session=True,
    )
    with LOCK:
        LAUNCHED[stem] = port
    return port


# ---------------------------------------------------------------- pages


def pretty(stem):
    """Human title from a workspace stem: drop the trailing program + date."""
    name = re.sub(r"_\d{4}-\d{2}-\d{2}$", "", stem)
    parts = name.rsplit("_", 1)
    title = parts[0].replace("-", " ").replace("_", " ")
    program = parts[1].replace("-", " ") if len(parts) > 1 else ""
    return title.strip(), program.strip()


CSS = f"""
*{{box-sizing:border-box}}
body{{margin:0;font:16px/1.5 -apple-system,BlinkMacSystemFont,"Segoe UI",Helvetica,Arial,sans-serif;
background:{C['cultured']};color:{C['body']}}}
header{{background:{C['navy']};color:#fff;padding:28px 32px}}
header h1{{margin:0;font-size:26px;font-weight:800;letter-spacing:-.02em}}
header p{{margin:6px 0 0;color:#a9c4dc;font-size:14px}}
main{{max-width:1000px;margin:0 auto;padding:28px 20px 60px}}
h2{{font-size:13px;text-transform:uppercase;letter-spacing:.09em;color:{C['navy']};
margin:34px 0 12px;font-weight:800}}
h2:first-child{{margin-top:6px}}
.card{{background:#fff;border:1px solid {C['border']};border-radius:12px;padding:18px 20px;
margin-bottom:12px;display:flex;align-items:center;gap:18px;flex-wrap:wrap}}
.card.ready{{border-left:5px solid {C['yellow']}}}
.card.blocked{{border-left:5px solid {C['muted']};opacity:.85}}
.info{{flex:1;min-width:260px}}
.title{{font-weight:700;font-size:17px;color:{C['navy']};text-transform:capitalize}}
.meta{{font-size:13px;color:#5d6b7a;margin-top:3px}}
.stem{{font:12px ui-monospace,SFMono-Regular,Menlo,monospace;color:{C['muted']};
margin-top:6px;word-break:break-all}}
.btn{{background:{C['yellow']};color:{C['navy']};font-weight:800;font-size:15px;
padding:12px 26px;border-radius:8px;text-decoration:none;white-space:nowrap;border:0;cursor:pointer}}
.btn:hover{{background:#ffd355}}
.btn.live{{background:{C['blue']};color:#fff}}
.badge{{font-size:12px;font-weight:700;padding:5px 11px;border-radius:20px;white-space:nowrap}}
.badge.no{{background:{C['subtle']};color:#4a6070}}
.fails{{font-size:13px;color:#7a4a4a;margin-top:5px}}
.empty{{background:#fff;border:1px dashed {C['border']};border-radius:12px;padding:28px;
text-align:center;color:{C['muted']}}}
footer{{max-width:1000px;margin:0 auto;padding:0 20px 50px;font-size:13px;color:#6a7684}}
footer code{{background:{C['subtle']};padding:2px 6px;border-radius:4px;font-size:12px}}
.bar{{display:flex;justify-content:space-between;align-items:baseline;gap:12px;flex-wrap:wrap}}
a.refresh{{color:{C['blue']};font-size:13px;text-decoration:none;font-weight:600}}
"""


def render_dashboard():
    rows = scan_all()
    ready = [r for r in rows if r[1]]
    blocked = [r for r in rows if not r[1]]

    def card(stem, is_ready, failed):
        title, program = pretty(stem)
        live = find_preview(stem) if is_ready else None
        cls = "ready" if is_ready else "blocked"
        if is_ready:
            label = "Watch again" if live else "Watch"
            btn = (
                f'<a class="btn{" live" if live else ""}" '
                f'href="/open?stem={html.escape(stem)}">{label} &rarr;</a>'
            )
            extra = ""
        else:
            btn = '<span class="badge no">not ready</span>'
            shown = ", ".join(failed[:4]) or "gate failed"
            extra = f'<div class="fails">failing: {html.escape(shown)}</div>'
        return f"""<div class="card {cls}">
  <div class="info">
    <div class="title">{html.escape(title)}</div>
    <div class="meta">{html.escape(program) or "&nbsp;"}</div>
    {extra}
    <div class="stem">{html.escape(stem)}</div>
  </div>
  {btn}
</div>"""

    body = []
    body.append(
        f'<div class="bar"><h2>Ready for your review &mdash; {len(ready)}</h2>'
        f'<a class="refresh" href="/">re-check &#8635;</a></div>'
    )
    if ready:
        body += [card(*r) for r in ready]
    else:
        body.append('<div class="empty">Nothing is gate-clean right now.</div>')

    if blocked:
        body.append(f"<h2>Not ready &mdash; don't spend time here ({len(blocked)})</h2>")
        body += [card(*r) for r in blocked]

    return f"""<!doctype html><html><head><meta charset="utf-8">
<title>SCLA — Lesson Video Review</title>
<meta name="viewport" content="width=device-width,initial-scale=1">
<style>{CSS}</style></head><body>
<header>
  <h1>Lesson video review</h1>
  <p>Every build on this machine, checked against the Motion v2 gate just now.
     Click Watch &mdash; the preview starts itself.</p>
</header>
<main>{"".join(body)}</main>
<footer>
  <p><strong>Ready</strong> means <code>render-qa/preflight.py</code> passed all seven
  deterministic checks, including the Motion v2 pacing gate. Anything under
  &ldquo;not ready&rdquo; would fail your ear for a reason the gate already caught.</p>
  <p>Approve one by telling Claude <code>ship &lt;stem&gt;</code> &mdash; that is what turns a
  hyperframe into an MP4 and publishes it.</p>
</footer>
</body></html>"""


def render_starting(stem, port):
    """Interstitial: poll until the preview answers, then bounce the browser to it."""
    target = f"{base_url(port)}/#project/{stem}"
    title, _ = pretty(stem)
    return f"""<!doctype html><html><head><meta charset="utf-8">
<title>Starting {html.escape(title)}…</title>
<style>{CSS}
.wrap{{max-width:640px;margin:16vh auto;text-align:center;padding:0 24px}}
.spin{{width:34px;height:34px;border:4px solid {C['subtle']};border-top-color:{C['yellow']};
border-radius:50%;margin:0 auto 22px;animation:r .9s linear infinite}}
@keyframes r{{to{{transform:rotate(360deg)}}}}
</style></head><body>
<div class="wrap">
  <div class="spin"></div>
  <div class="title" style="font-size:21px">{html.escape(title)}</div>
  <p style="color:#5d6b7a">Starting its preview&hellip; this takes a few seconds the first time.
     You'll be sent there automatically.</p>
  <p style="font-size:13px;color:{C['muted']}">If nothing happens,
     <a href="{html.escape(target)}">open it directly</a>
     or <a href="/">go back</a>.</p>
</div>
<script>
const target = {json.dumps(target)};
let tries = 0;
(function poll(){{
  tries++;
  fetch('/ready?port={port}&stem=' + encodeURIComponent({json.dumps(stem)}))
    .then(r => r.json())
    .then(d => {{
      if (d.ready) {{ location.replace(target); }}
      else if (tries < 90) {{ setTimeout(poll, 1000); }}
      else {{ document.querySelector('.spin').style.display = 'none'; }}
    }})
    .catch(() => {{ if (tries < 90) setTimeout(poll, 1000); }});
}})();
</script>
</body></html>"""


# ---------------------------------------------------------------- server


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass  # keep the terminal quiet

    def _send(self, body, code=200, ctype="text/html; charset=utf-8"):
        raw = body.encode()
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(raw)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(raw)

    def do_GET(self):
        u = urlparse(self.path)
        q = parse_qs(u.query)

        if u.path == "/":
            self._send(render_dashboard())

        elif u.path == "/open":
            stem = (q.get("stem") or [""])[0]
            if stem not in workspaces():
                self._send("<p>Unknown build. <a href='/'>Back</a></p>", 404)
                return
            port = launch_preview(stem)
            self._send(render_starting(stem, port))

        elif u.path == "/ready":
            port = int((q.get("port") or ["0"])[0])
            stem = (q.get("stem") or [""])[0]
            ok = port_open(port) and project_on_port(port) == stem
            self._send(json.dumps({"ready": ok}), ctype="application/json")

        else:
            self._send("<p>Not found. <a href='/'>Back</a></p>", 404)


def main():
    if not ROOT.is_dir():
        sys.exit(f"No renders-hyperframes/ at {ROOT}")
    try:
        srv = ThreadingHTTPServer(("127.0.0.1", DASH_PORT), Handler)
    except OSError:
        sys.exit(
            f"Port {DASH_PORT} is busy — something else is on it.\n"
            f"Clear it with:  pkill -f '[h]yperframes preview --port {DASH_PORT}'"
        )
    url = base_url(DASH_PORT)
    print()
    print("  SCLA lesson video review")
    print(f"  {url}")
    print("  (ctrl/cmd-click the link. Ctrl-C here to stop.)")
    print()
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        print("\n  stopped.\n")


if __name__ == "__main__":
    main()
