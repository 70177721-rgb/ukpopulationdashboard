from flask import Flask, Response
import os
import subprocess
import sys

app = Flask(__name__)

DASHBOARD_SCRIPT = os.path.join(os.path.dirname(__file__), "uk_population_dashboard.py")
DASHBOARD_HTML   = os.path.join(os.path.dirname(__file__), "uk_population_dashboard.html")

@app.route("/")
def dashboard():
    # Run the dashboard generator as a subprocess so it has full access to
    # its own globals, working directory, and file paths (exec in {} loses all of that)
    result = subprocess.run(
        [sys.executable, DASHBOARD_SCRIPT],
        capture_output=True,
        text=True,
        cwd=os.path.dirname(__file__)
    )
    if result.returncode != 0:
        return Response(
            f"<pre>Dashboard generation failed:\n{result.stderr}</pre>",
            status=500,
            mimetype="text/html"
        )

    # Read and serve the generated HTML
    with open(DASHBOARD_HTML, "r", encoding="utf-8") as f:
        html = f.read()
    return Response(html, mimetype="text/html")

@app.route("/health")
def health():
    return {"status": "ok"}, 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
