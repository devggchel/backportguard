# BackportGuard — FINAL REPORT

## Done

- BackportGuard 0.1.0 is installed and active on the VPS as `backportguard.service`.
- FastAPI listens only on `127.0.0.1:8765`; `GET /health` returns `{"status":"ok"}`.
- Source includes HMAC verification, 1 MiB request limit, safe YAML parsing, SQLite delivery deduplication, GitHub Issue creation, tests, documentation, Apache-2.0 licence, and GitHub Actions workflow.
- Deployed source revision: `5c6da55` (package version `0.1.0`); local annotated release tag: `v0.1.0` (`d0d9e10`).

## Links

- GitHub: not created — the connected GitHub interface has no repository-creation capability and local `gh` is unavailable.
- Cloudflare Pages: not created — no Cloudflare account authentication is available on this laptop.
- Application: local-only `http://127.0.0.1:8765/health`; a public URL is intentionally absent until a named Cloudflare Tunnel token is supplied.

## Verification

- Local: `python -m pytest -q` — 4 passed; HTTP health check passed; Git-tracked files were checked for credentials.
- VPS: service is active; memory cap 512 MiB, CPU quota 50%, task limit 64; no new inbound port is open.
- GitHub Actions: workflow committed locally but cannot run until the public repository exists.

## GitHub App and remaining manual work

GitHub App is not registered. Create it with Metadata/Contents/Pull requests read-only, Issues read/write, and Pull request event; install it, then place its ID, installation ID and PEM in `/etc/backportguard`. In the same Cloudflare account, create a free named token-based tunnel to `http://127.0.0.1:8765`, add its token as `CLOUDFLARE_TUNNEL_TOKEN` to `/etc/backportguard/backportguard.env`, and restart only `backportguard.service`. Create the public repository, push this local `main` and tag, then deploy `site/` to a free Pages project.

## Created resources and removal

Created: `/opt/backportguard`, `/etc/backportguard/backportguard.env`, `/var/lib/backportguard`, system user `backportguard`, and `backportguard.service`; `cloudflared` is isolated under `/opt/backportguard/bin` and is not running without a tunnel token. To remove only this project: `systemctl disable --now backportguard.service`, then remove its unit, the three BackportGuard directories, and the `backportguard` user; also remove its future Tunnel and Pages project.

## Safety

`felix-bot.service` and `neoguard-go.service` remained active before and after every VPS stage; no bot files, databases, environments, containers, cron jobs, network/SSH/DNS settings, or existing Cloudflare resources were modified. No paid resources or fictitious activity were created.
