from flask import Flask, Response
import os
import subprocess
import sys

app = Flask(__name__)

DASHBOARD_SCRIPT = os.path.join(os.path.dirname(__file__), "uk_population_dashboard.py")
DASHBOARD_HTML   = os.path.join(os.path.dirname(__file__), "uk_population_dashboard.html")

# ── Generate the dashboard ONCE at startup ──────────────────────────────────
print("[startup] Generating dashboard HTML...", flush=True)
_startup_result = subprocess.run(
    [sys.executable, DASHBOARD_SCRIPT],
    capture_output=True,
    text=True,
    cwd=os.path.dirname(os.path.abspath(__file__))
)

if _startup_result.returncode != 0:
    print(f"[startup] ERROR: Dashboard generation failed:\n{_startup_result.stderr}", flush=True)
    _CACHED_HTML = None
    _STARTUP_ERROR = _startup_result.stderr
else:
    with open(DASHBOARD_HTML, "r", encoding="utf-8") as f:
        _CACHED_HTML = f.read()
    _STARTUP_ERROR = None
    print(f"[startup] Dashboard ready ({len(_CACHED_HTML)//1024} KB)", flush=True)
# ─────────────────────────────────────────────────────────────────────────────


@app.route("/")
def dashboard():
    if _CACHED_HTML is None:
        return Response(
            f"<pre>Dashboard generation failed at startup:\n{_STARTUP_ERROR}</pre>",
            status=500,
            mimetype="text/html"
        )
    return Response(_CACHED_HTML, mimetype="text/html")


@app.route("/health")
def health():
    return {"status": "ok" if _CACHED_HTML else "error"}, 200


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
    
