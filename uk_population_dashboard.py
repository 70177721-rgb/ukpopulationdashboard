from flask import Flask, Response
import os
import subprocess
import sys

app = Flask(__name__)

BASE_DIR         = os.path.dirname(os.path.abspath(__file__))
DASHBOARD_SCRIPT = os.path.join(BASE_DIR, "uk_population_dashboard.py")
DASHBOARD_HTML   = os.path.join(BASE_DIR, "uk_population_dashboard.html")

_CACHED_HTML   = None
_STARTUP_ERROR = None

def generate_dashboard():
    """Run the dashboard generator script and cache the HTML."""
    global _CACHED_HTML, _STARTUP_ERROR

    # ── Check files exist before running ──────────────────────────────────
    if not os.path.exists(DASHBOARD_SCRIPT):
        _STARTUP_ERROR = f"MISSING FILE: {DASHBOARD_SCRIPT}"
        print(f"[ERROR] {_STARTUP_ERROR}", flush=True)
        return

    xlsx = os.path.join(BASE_DIR, "mye24tablesuk.xlsx")
    if not os.path.exists(xlsx):
        _STARTUP_ERROR = f"MISSING FILE: {xlsx}"
        print(f"[ERROR] {_STARTUP_ERROR}", flush=True)
        return

    print("[startup] Running dashboard generator...", flush=True)
    result = subprocess.run(
        [sys.executable, DASHBOARD_SCRIPT],
        capture_output=True,
        text=True,
        cwd=BASE_DIR,
        timeout=120          # 2-minute hard limit
    )

    if result.returncode != 0:
        _STARTUP_ERROR = result.stderr or result.stdout or "Unknown error (no output)"
        print(f"[ERROR] Dashboard generation failed:\n{_STARTUP_ERROR}", flush=True)
        return

    if not os.path.exists(DASHBOARD_HTML):
        _STARTUP_ERROR = f"Script ran OK but {DASHBOARD_HTML} was not created."
        print(f"[ERROR] {_STARTUP_ERROR}", flush=True)
        return

    with open(DASHBOARD_HTML, "r", encoding="utf-8") as f:
        _CACHED_HTML = f.read()

    print(f"[startup] Dashboard ready — {len(_CACHED_HTML)//1024} KB", flush=True)


# Generate once at import / startup
generate_dashboard()


@app.route("/")
def dashboard():
    if _CACHED_HTML is None:
        error_html = f"""<!DOCTYPE html>
<html><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<style>
  body{{font-family:monospace;background:#1a1a2e;color:#f87171;padding:32px;max-width:800px;margin:auto}}
  h2{{color:#fbbf24;margin-bottom:16px}}
  pre{{background:#111;padding:20px;border-radius:8px;white-space:pre-wrap;word-break:break-word;
       color:#e2e8f0;font-size:13px;border:1px solid #374151}}
  .hint{{color:#94a3b8;font-size:13px;margin-top:20px;line-height:1.6}}
</style></head>
<body>
<h2>⚠ Dashboard failed to start</h2>
<pre>{_STARTUP_ERROR or 'No error details captured.'}</pre>
<div class="hint">
  Check your Render logs for the full traceback.<br>
  Common causes: missing <strong>mye24tablesuk.xlsx</strong>,
  missing pip package, or script crash at import time.
</div>
</body></html>"""
        return Response(error_html, status=500, mimetype="text/html")

    return Response(_CACHED_HTML, mimetype="text/html")


@app.route("/health")
def health():
    if _CACHED_HTML:
        return {"status": "ok", "html_kb": len(_CACHED_HTML) // 1024}, 200
    return {"status": "error", "reason": _STARTUP_ERROR}, 500


@app.route("/reload")
def reload_dashboard():
    """Force-regenerate the dashboard (useful after data updates)."""
    generate_dashboard()
    if _CACHED_HTML:
        return {"status": "ok", "html_kb": len(_CACHED_HTML) // 1024}, 200
    return {"status": "error", "reason": _STARTUP_ERROR}, 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
