"""Run Uvicorn and, when configured, one Cloudflare Tunnel child process."""
from __future__ import annotations

import os
import signal
import subprocess
import sys


def main() -> int:
    token = os.environ.get("CLOUDFLARE_TUNNEL_TOKEN")
    command = [sys.executable, "-m", "uvicorn", "backportguard.main:app", "--host", "127.0.0.1", "--port", os.environ.get("PORT", "8765")]
    app = subprocess.Popen(command)
    tunnel: subprocess.Popen | None = None
    if token:
        binary = os.environ.get("CLOUDFLARED_BIN", "/opt/backportguard/bin/cloudflared")
        tunnel = subprocess.Popen([binary, "tunnel", "--no-autoupdate", "run", "--token", token])

    def stop(_signum: int, _frame: object) -> None:
        for process in (tunnel, app):
            if process and process.poll() is None:
                process.terminate()

    signal.signal(signal.SIGTERM, stop)
    signal.signal(signal.SIGINT, stop)
    status = app.wait()
    stop(0, None)
    if tunnel:
        tunnel.wait(timeout=15)
    return status


if __name__ == "__main__":
    raise SystemExit(main())
