# BackportGuard — FINAL REPORT

## Done

- BackportGuard 0.1.0 is installed and active on the VPS as `backportguard.service`.
- FastAPI listens only on `127.0.0.1:8765`; `GET /health` returns `{"status":"ok"}`.
- Source includes HMAC verification, 1 MiB request limit, safe YAML parsing, SQLite delivery deduplication, GitHub Issue creation, tests, documentation, Apache-2.0 licence, and GitHub Actions workflow.
- Deployed source revision: `aa41df3` (package version `0.1.0`); public release `v0.1.0` was published after the successful test workflow.

## Links

- GitHub: https://github.com/devggchel/backportguard
- Cloudflare Pages: https://backportguard.pages.dev/
- Application: `http://127.0.0.1:8765/health` on the VPS; Cloudflare Tunnel is healthy but has no public hostname yet.

## Verification

- Local: `python -m pytest -q` — 4 passed; HTTP health check passed; Git-tracked files were checked for credentials.
- VPS: service is active; memory cap 512 MiB, CPU quota 50%, task limit 64; no new inbound port is open.
- GitHub Actions: [tests passed](https://github.com/devggchel/backportguard/actions/runs/29771124458) on GitHub.

## GitHub App and remaining manual work

GitHub App is not registered. `github-app-manifest.json` is prepared with the required minimum permissions (Metadata is always read-only for GitHub Apps; Contents and Pull requests read-only; Issues read/write) and the Pull request event. The free hostname registration is pending review in [is-a.dev PR #44339](https://github.com/is-a-dev/register/pull/44339); after it is merged, point the existing healthy Tunnel at `backportguard.is-a.dev` → `http://127.0.0.1:8765`, then use that hostname in the manifest before registering and installing the App.

## Created resources and removal

Created: `/opt/backportguard`, `/etc/backportguard/backportguard.env`, `/var/lib/backportguard`, system user `backportguard`, `backportguard.service`, one Cloudflare Pages project, and one healthy Cloudflare Tunnel. To remove only this project: `systemctl disable --now backportguard.service`, then remove its unit, the three BackportGuard directories, and the `backportguard` user; also remove its Tunnel route, Tunnel, and Pages project.

## Safety

`felix-bot.service` and `neoguard-go.service` remained active before and after every VPS stage; no bot files, databases, environments, containers, cron jobs, network/SSH/DNS settings, or existing Cloudflare resources were modified. No paid resources or fictitious activity were created.
