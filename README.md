# BackportGuard

BackportGuard is a free, open-source webhook service for GitHub repositories. When a pull request is merged with the configured `backport` label, it reads `.backportguard.yml` at the merge commit and opens one reminder issue listing the older branches to review. It never cherry-picks, clones, runs, or otherwise applies third-party code.

## Quick start

Create `.backportguard.yml` in the monitored repository:

```yaml
branches:
  - release/1.0
  - release/0.9
labels:
  required:
    - backport
```

Create a GitHub App with Metadata/Contents/Pull requests read-only and Issues read/write permissions, subscribe it to **Pull request** events, then configure its webhook URL as `https://YOUR-TUNNEL/webhooks/github` and set the same secret in `WEBHOOK_SECRET`.

## Local development

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements-dev.txt
WEBHOOK_SECRET=development-only DATABASE_PATH=/tmp/backportguard.sqlite3 .venv/bin/uvicorn backportguard.main:app --host 127.0.0.1 --port 8765
.venv/bin/pytest -q
```

`GET /health` returns `{"status":"ok"}`. The request body limit is 1 MiB; signatures use `X-Hub-Signature-256`; GitHub deliveries are deduplicated in SQLite.

## Production deployment

The supplied unit is deliberately the only new systemd unit. It starts the FastAPI application bound to `127.0.0.1:8765` and, when `CLOUDFLARE_TUNNEL_TOKEN` is configured, its Cloudflare Tunnel child process in the same protected service cgroup.

1. Create user `backportguard`, `/opt/backportguard`, `/etc/backportguard`, and `/var/lib/backportguard` with root privileges.
2. Copy this repository to `/opt/backportguard`, create its isolated `.venv`, and install `requirements.txt` there.
3. Put secrets only in `/etc/backportguard/backportguard.env` (mode `0600`), including `WEBHOOK_SECRET`, GitHub App values, and the Cloudflare Tunnel token.
4. Install `deploy/backportguard.service` as `backportguard.service`, then enable and start it.

The unit limits memory to 512 MiB, sustained CPU to half a core, and tasks to 64. It does not open inbound ports; only Cloudflare Tunnel makes an outbound connection. Use a named token-based tunnel from Cloudflare Zero Trust and do not expose SSH.

## GitHub App credentials

Production authentication uses `GITHUB_APP_ID`, `GITHUB_INSTALLATION_ID`, and `GITHUB_PRIVATE_KEY_PATH`; the PEM belongs under `/etc/backportguard` and is never committed. `GITHUB_TOKEN` is supported only as a local-development fallback.

## Security

See [SECURITY.md](SECURITY.md) and [PRIVACY.md](PRIVACY.md). No webhook data is executed as code, and the service logs neither webhook secrets nor GitHub credentials.

## License

Apache-2.0. See [LICENSE](LICENSE).
