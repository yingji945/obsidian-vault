#!/usr/bin/env python3
"""三省六部 · 实时辩论页面 HTTP 服务器

提供 debate.html（自动刷新聊天式辩论看板）的 HTTP 服务。
监听 8899 端口，服务 /opt/data/dashboard/ 目录的静态文件。

用法：
    python3 /opt/data/skills/multi-agent-roundtable/scripts/debate_server.py

前置条件：
    - debate.html 需位于同一目录或 /opt/data/dashboard/debate.html
    - roundtable_live.py 运行时写入 /opt/data/dashboard/dashboard_status.json
    - Docker 端口 8899 需映射到宿主机（docker-compose.yml ports 段）
"""
import http.server, os, urllib.parse
from pathlib import Path

PORT = int(os.environ.get("DEBATE_PORT", 8899))
DASHBOARD_DIR = Path("/opt/data/dashboard")
STATUS_FILE = DASHBOARD_DIR / "dashboard_status.json"
HTML_FILE = DASHBOARD_DIR / "debate.html"

# Fallback: if deployed files not in shared volume, copy from skill dir
SKILL_DIR = Path("/opt/data/skills/multi-agent-roundtable")
if not HTML_FILE.exists():
    src = SKILL_DIR / "templates/debate.html"
    if src.exists():
        DASHBOARD_DIR.mkdir(parents=True, exist_ok=True)
        HTML_FILE.write_text(src.read_text())


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(DASHBOARD_DIR), **kwargs)

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path == "/":
            self.path = "/debate.html"
        super().do_GET()

    def log_message(self, fmt, *args):
        pass  # quiet


if __name__ == "__main__":
    if not HTML_FILE.exists():
        print(f"❌ 找不到 {HTML_FILE}，请确保文件存在")
        exit(1)
    port = PORT
    host = os.environ.get("DEBATE_HOST", "0.0.0.0")
    with http.server.HTTPServer((host, port), Handler) as s:
        print(f"✅ 辩论看板服务：http://0.0.0.0:{port}/")
        print(f"   页面：{HTML_FILE}")
        print(f"   数据：{STATUS_FILE}")
        s.serve_forever()
