#!/usr/bin/env python3
"""Small local web UI for the G-BungE log analysis CLI.

Run:
    python3 web/server.py

Then open:
    http://127.0.0.1:8765
"""

from __future__ import annotations

import contextlib
import html
import io
import json
import os
import sys
import threading
import time
import traceback
import urllib.parse
import uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
HOST = os.environ.get("GBUNGE_LOG_WEB_HOST", "127.0.0.1")
PORT = int(os.environ.get("GBUNGE_LOG_WEB_PORT", "8765"))
RUNS_ROOT = PROJECT_ROOT / "web_runs"
MAX_FIELD_BYTES = 1024 * 1024

os.environ.setdefault("MPLBACKEND", "Agg")
os.environ.setdefault("MPLCONFIGDIR", str(PROJECT_ROOT / ".matplotlib-cache"))

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, str(PROJECT_ROOT))
import main as cli


RUNS_ROOT.mkdir(exist_ok=True)


def page_shell(body: str, title: str = "G-BungE Log Analysis Web") -> bytes:
    return f"""<!doctype html>
<html lang="ko">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(title)}</title>
  <style>
    :root {{
      color-scheme: light;
      --bg: #f5f6f8;
      --panel: #ffffff;
      --ink: #13181d;
      --muted: #66727d;
      --line: #d9dee5;
      --accent: #dc2f27;
      --accent-soft: #fff0ee;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      background: var(--bg);
      color: var(--ink);
      font-family: ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }}
    header {{
      padding: 26px 32px 18px;
      border-bottom: 1px solid var(--line);
      background: var(--panel);
    }}
    header p {{ margin: 5px 0 0; color: var(--muted); }}
    h1 {{ margin: 0; font-size: 26px; letter-spacing: 0; }}
    main {{ max-width: 1220px; margin: 0 auto; padding: 26px; }}
    .layout {{ display: grid; grid-template-columns: minmax(320px, 420px) minmax(0, 1fr); gap: 20px; align-items: start; }}
    .panel {{
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 18px;
    }}
    label {{ display: grid; gap: 7px; margin-bottom: 14px; font-weight: 750; }}
    select, input, button {{
      min-height: 40px;
      border: 1px solid var(--line);
      border-radius: 6px;
      padding: 0 10px;
      font: inherit;
      background: #fff;
    }}
    select[multiple] {{ min-height: 240px; padding: 8px; }}
    button {{
      width: 100%;
      border-color: var(--accent);
      background: var(--accent);
      color: #fff;
      font-weight: 800;
      cursor: pointer;
    }}
    .hint {{ color: var(--muted); font-size: 13px; line-height: 1.5; margin: -5px 0 15px; }}
    .plots {{ display: grid; gap: 16px; }}
    .plot {{ border: 1px solid var(--line); border-radius: 8px; overflow: hidden; background: #fff; }}
    .plot img {{ width: 100%; display: block; }}
    pre {{
      white-space: pre-wrap;
      overflow-wrap: anywhere;
      max-height: 360px;
      overflow: auto;
      background: #11181d;
      color: #edf3f7;
      border-radius: 8px;
      padding: 14px;
      font-size: 13px;
      line-height: 1.5;
    }}
    .error {{ color: #9f1d18; background: var(--accent-soft); border-color: #f1bbb6; }}
    @media (max-width: 860px) {{ .layout {{ grid-template-columns: 1fr; }} main {{ padding: 16px; }} }}
  </style>
</head>
<body>
  <header>
    <h1>{html.escape(title)}</h1>
    <p>CLI 메뉴를 브라우저 폼으로 실행하고, Matplotlib 결과를 PNG로 저장해 보여줍니다.</p>
  </header>
  <main>{body}</main>
</body>
</html>""".encode("utf-8")


def get_form_options() -> tuple[list[str], dict[str, list[str]], list[str]]:
    groups = cli.discover_log_groups()
    logs_by_group = {group: cli.discover_logs(group) for group in groups}
    actions = list(cli.get_action_registry())
    return groups, logs_by_group, actions


def render_index(result_html: str = "") -> bytes:
    groups, logs_by_group, actions = get_form_options()
    default_group = cli.DEFAULT_LOG_GROUP if cli.DEFAULT_LOG_GROUP in groups else (groups[0] if groups else "")
    logs_json = html.escape(json.dumps(logs_by_group, ensure_ascii=False))

    group_options = "\n".join(
        f'<option value="{html.escape(group)}" {"selected" if group == default_group else ""}>{html.escape(group)}</option>'
        for group in groups
    )
    action_options = "\n".join(
        f'<option value="{html.escape(action)}">{html.escape(cli.format_action_option(action))}</option>'
        for action in actions
    )

    body = f"""
<div class="layout">
  <form class="panel" method="post" action="/run">
    <label>
      로그 그룹
      <select id="group" name="group">{group_options}</select>
    </label>
    <label>
      로그 파일
      <select id="logs" name="logs" multiple required></select>
    </label>
    <p class="hint">분할 세션은 여러 로그를 순서대로 선택하면 됩니다. Mac에서는 Cmd를 누르고 여러 개를 고를 수 있습니다.</p>
    <label>
      분석 플롯
      <select name="plots" multiple required>{action_options}</select>
    </label>
    <p class="hint">여러 플롯을 선택하면 한 번에 실행합니다. 오래 걸리는 분석은 브라우저가 잠시 기다릴 수 있습니다.</p>
    <label>
      <span><input type="checkbox" name="strict" value="1"> 누락 로그가 있으면 즉시 실패</span>
    </label>
    <button type="submit">Run Analysis</button>
  </form>
  <section class="panel">
    {result_html or "<p class='hint'>왼쪽에서 로그와 분석 항목을 선택하면 결과가 여기에 표시됩니다.</p>"}
  </section>
</div>
<script>
  const logsByGroup = JSON.parse("{logs_json}".replaceAll("&quot;", '"'));
  const groupSelect = document.querySelector("#group");
  const logSelect = document.querySelector("#logs");
  function renderLogs() {{
    const logs = logsByGroup[groupSelect.value] || [];
    logSelect.innerHTML = logs.map((name) => `<option value="${{name}}">${{name}}</option>`).join("");
  }}
  groupSelect.addEventListener("change", renderLogs);
  renderLogs();
</script>
"""
    return page_shell(body)


def run_analysis(group: str, logs: list[str], plots: list[str], strict: bool) -> tuple[str, list[Path]]:
    run_id = time.strftime("%Y%m%d-%H%M%S") + "-" + uuid.uuid4().hex[:8]
    run_dir = RUNS_ROOT / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    registry = cli.get_action_registry()
    output = io.StringIO()
    saved_plots: list[Path] = []
    plot_index = 0
    original_show = plt.show

    def save_current_figures(*args, **kwargs) -> None:
        nonlocal plot_index
        figures = [plt.figure(num) for num in plt.get_fignums()]
        if not figures:
            return
        for figure in figures:
            plot_index += 1
            filename = f"plot-{plot_index:02d}.png"
            output_path = run_dir / filename
            figure.savefig(output_path, dpi=145, bbox_inches="tight")
            saved_plots.append(output_path)
        plt.close("all")

    try:
        with contextlib.redirect_stdout(output), contextlib.redirect_stderr(output):
            plt.show = save_current_figures
            action_names = cli.validate_actions(plots, registry)
            log_data = cli.load_logs(logs, group=group, strict=strict)
            cli.run_actions(log_data, action_names, registry)
            save_current_figures()
    finally:
        plt.show = original_show
        plt.close("all")

    return output.getvalue(), saved_plots


class Handler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        path = urllib.parse.urlparse(self.path).path
        if path == "/":
            self.respond(200, render_index(), "text/html; charset=utf-8")
            return
        if path.startswith("/runs/"):
            self.serve_run_file(path)
            return
        self.respond(404, b"Not found", "text/plain; charset=utf-8")

    def do_POST(self) -> None:
        if urllib.parse.urlparse(self.path).path != "/run":
            self.respond(404, b"Not found", "text/plain; charset=utf-8")
            return

        length = min(int(self.headers.get("Content-Length", "0")), MAX_FIELD_BYTES)
        raw_body = self.rfile.read(length).decode("utf-8")
        fields = urllib.parse.parse_qs(raw_body)
        group = fields.get("group", [""])[0]
        logs = fields.get("logs", [])
        plots = fields.get("plots", [])
        strict = fields.get("strict", ["0"])[0] == "1"

        try:
            text_output, images = run_analysis(group, logs, plots, strict)
            image_html = "".join(
                f'<article class="plot"><img src="/runs/{html.escape(path.parent.name)}/{html.escape(path.name)}" alt="{html.escape(path.name)}"></article>'
                for path in images
            )
            result = f"""
<h2>Run Result</h2>
<p class="hint">{len(images)}개 이미지가 생성되었습니다.</p>
<div class="plots">{image_html}</div>
<h3>Console Output</h3>
<pre>{html.escape(text_output or "No console output.")}</pre>
"""
            self.respond(200, render_index(result), "text/html; charset=utf-8")
        except Exception:
            result = f"""
<div class="panel error">
  <h2>실행 실패</h2>
  <pre>{html.escape(traceback.format_exc())}</pre>
</div>
"""
            self.respond(500, render_index(result), "text/html; charset=utf-8")

    def serve_run_file(self, path: str) -> None:
        parts = Path(path.removeprefix("/runs/")).parts
        if len(parts) != 2:
            self.respond(404, b"Not found", "text/plain; charset=utf-8")
            return
        file_path = RUNS_ROOT / parts[0] / parts[1]
        if not file_path.is_file() or file_path.suffix != ".png":
            self.respond(404, b"Not found", "text/plain; charset=utf-8")
            return
        self.respond(200, file_path.read_bytes(), "image/png")

    def respond(self, status: int, body: bytes, content_type: str) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format: str, *args) -> None:
        print(f"[web] {self.address_string()} - {format % args}")


def main() -> int:
    server = ThreadingHTTPServer((HOST, PORT), Handler)
    thread_count = threading.active_count()
    print(f"Serving G-BungE Log Analysis Web at http://{HOST}:{PORT}")
    print(f"Active threads before serve: {thread_count}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down.")
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
