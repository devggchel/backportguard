# GitHub App setup

BackportGuard needs a GitHub App rather than a personal access token in production. This limits access to installed repositories and gives operators a revocable identity.

## Required settings

Use `github-app-manifest.json` as the starting point, then replace `YOUR-BACKPORTGUARD-HOST` with the dedicated public Tunnel hostname.

| Setting | Value |
| --- | --- |
| Homepage URL | `https://backportguard.pages.dev/` |
| Webhook URL | `https://backportguard.space/webhooks/github` |
| Webhook event | Pull request |
| Metadata | Read-only (always required by GitHub Apps) |
| Contents | Read-only |
| Pull requests | Read-only |
| Issues | Read and write |

Set a strong webhook secret and put the same value only in `WEBHOOK_SECRET` inside `/etc/backportguard/backportguard.env` (mode `0600`). Do not commit it or paste it into an issue.

After installing the App on a repository, add these server-side values:

```ini
GITHUB_APP_ID=...
GITHUB_INSTALLATION_ID=...
GITHUB_PRIVATE_KEY_PATH=/etc/backportguard/github-app.pem
```

The private key must be readable by the `backportguard` service user and must never be placed in Git.
