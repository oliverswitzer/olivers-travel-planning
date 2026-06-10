#!/usr/bin/env python3
"""
Oliver's Travel Planning — itinerary server.

Serves the itineraries/ directory as a browsable index over HTTP.
Accessible on your Tailscale network at http://100.126.32.92:3031/

Usage:
    python bin/serve.py           # Start on port 3031
    python bin/serve.py --port 4040
"""

import argparse
import http.server
import os
import socketserver
from pathlib import Path
from datetime import datetime

PROJECT_ROOT    = Path(__file__).parent.parent
ITINERARIES_DIR = PROJECT_ROOT / "itineraries"
PORT_DEFAULT    = 3031
TAILSCALE_IP    = "100.126.32.92"

INDEX_STYLE = """
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    background: #0a0e1a; color: #e8eaf6;
    min-height: 100vh; padding: 32px 20px;
  }
  .header { max-width: 800px; margin: 0 auto 36px; }
  h1 { font-size: 26px; color: #a78bfa; margin-bottom: 6px; display: flex; align-items: center; gap: 10px; }
  .sub { color: #64748b; font-size: 13px; }
  .grid { max-width: 800px; margin: 0 auto; display: grid; gap: 12px; }
  .card {
    background: #131829; border: 1px solid #1e2a40;
    border-radius: 12px; padding: 18px 22px;
    display: flex; justify-content: space-between; align-items: center;
    transition: border-color 0.15s;
  }
  .card:hover { border-color: #a78bfa; }
  .card a { color: #a78bfa; text-decoration: none; font-size: 16px; font-weight: 600; }
  .card a:hover { text-decoration: underline; }
  .meta { color: #64748b; font-size: 12px; margin-top: 5px; }
  .badge {
    background: rgba(167,139,250,0.12); color: #a78bfa;
    font-size: 11px; font-weight: 700; padding: 4px 10px;
    border-radius: 20px; white-space: nowrap;
  }
  .empty { color: #64748b; font-style: italic; text-align: center; margin-top: 60px; font-size: 15px; }
  .empty code { background: #131829; border: 1px solid #1e2a40; padding: 2px 6px; border-radius: 4px; color: #a78bfa; }
</style>
"""


def parse_itinerary_meta(path: Path) -> dict:
    """Try to extract a title and date from an HTML itinerary."""
    meta = {"name": path.stem.replace("-", " ").replace("_", " ").title(), "size_kb": round(path.stat().st_size / 1024, 1)}
    try:
        chunk = path.read_text(encoding="utf-8", errors="ignore")[:2000]
        import re
        m = re.search(r"<title>([^<]+)</title>", chunk, re.IGNORECASE)
        if m:
            meta["name"] = m.group(1).strip()
        # Try to get date from filename prefix YYYY-MM-DD
        stem = path.stem
        dm = re.match(r"(\d{4}-\d{2}-\d{2})", stem)
        if dm:
            meta["date"] = dm.group(1)
        else:
            ts = path.stat().st_mtime
            meta["date"] = datetime.fromtimestamp(ts).strftime("%Y-%m-%d")
    except Exception:
        meta["date"] = "unknown"
    return meta


class TravelHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ITINERARIES_DIR), **kwargs)

    def do_GET(self):
        if self.path in ("/", ""):
            self.serve_index()
        else:
            super().do_GET()

    def serve_index(self):
        files = sorted(
            [f for f in ITINERARIES_DIR.iterdir() if f.suffix == ".html" and f.name != "index.html"],
            key=lambda f: f.stat().st_mtime,
            reverse=True,
        )

        cards = ""
        for f in files:
            m = parse_itinerary_meta(f)
            cards += f"""
            <div class="card">
              <div>
                <a href="/{f.name}">✈️ {m['name']}</a>
                <div class="meta">📅 {m.get('date','?')} &nbsp;·&nbsp; {m['size_kb']} KB</div>
              </div>
              <span class="badge">itinerary</span>
            </div>"""

        if not cards:
            cards = '<p class="empty">No itineraries yet.<br><br>Ask Claude to search for flights and save an itinerary — it will appear here.</p>'

        count_label = f"{len(files)} itinerar{'y' if len(files)==1 else 'ies'}"
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>✈️ Oliver's Travel Plans</title>
{INDEX_STYLE}
</head>
<body>
  <div class="header">
    <h1>✈️ Oliver's Travel Plans</h1>
    <div class="sub">{count_label} saved &nbsp;·&nbsp; http://{TAILSCALE_IP}:{PORT_DEFAULT}/</div>
  </div>
  <div class="grid">{cards}</div>
</body>
</html>"""

        encoded = html.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)

    def log_message(self, fmt, *args):
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {self.address_string()} — {fmt % args}")


def main():
    parser = argparse.ArgumentParser(description="Travel planning itinerary server")
    parser.add_argument("--port", type=int, default=PORT_DEFAULT)
    parser.add_argument("--host", default="0.0.0.0",
                        help="Bind host (0.0.0.0 = all interfaces including Tailscale)")
    args = parser.parse_args()

    ITINERARIES_DIR.mkdir(exist_ok=True)

    with socketserver.TCPServer((args.host, args.port), TravelHandler) as httpd:
        httpd.allow_reuse_address = True
        print(f"✈️  Oliver's Travel Planning — itinerary server")
        print(f"   Local:     http://localhost:{args.port}/")
        print(f"   Tailscale: http://{TAILSCALE_IP}:{args.port}/")
        print(f"   Itineraries: {ITINERARIES_DIR}")
        print(f"   Ctrl+C to stop\n")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nStopped.")


if __name__ == "__main__":
    main()
