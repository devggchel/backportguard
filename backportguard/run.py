"""Run Uvicorn and, when configured, one Cloudflare Tunnel child process."""
from __future__ import annotations

import os
import signal
import subprocess
import sys
import time


def main() -> int:
    token = os.environ.pop("CLOUDFLARE_TUNNEL_TOKEN", None)
    command = [sys.executable, "-m", "uvicorn", "backportguard.main:app", "--host", "127.0.0.1", "--port", os.environ.get("PORT", "8765")]
    app = subprocess.Popen(command)
    tunnel: subprocess.Popen | None = None
    if token:
        binary = os.environ.get("CLOUDFLARED_BIN", "/opt/backportguard/bin/cloudflared")
        tunnel_environment = os.environ.copy()
        tunnel_environment["TUNNEL_TOKEN"] = token
        tunnel = subprocess.Popen(
            [binary, "tunnel", "--no-autoupdate", "run"],
            env=tunnel_environment,
        )

    def stop(_signum: int, _frame: object) -> None:
        for process in (tunnel, app):
            if process and process.poll() is None:
                process.terminate()

    signal.signal(signal.SIGTERM, stop)
    signal.signal(signal.SIGINT, stop)
    while True:
        if app.poll() is not None:
            stop(0, None)
            if tunnel:
                tunnel.wait(timeout=15)
            return app.returncode
        if tunnel and tunnel.poll() is not None:
            stop(0, None)
            app.wait(timeout=15)
            return tunnel.returncode or 1
        time.sleep(1)


if __name__ == "__main__":
    raise SystemExit(main())
