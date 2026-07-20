# Architecture

BackportGuard is deliberately a single Python service. It has no queue, worker fleet, container runtime, or automatic Git operation.

## Request path

1. FastAPI receives `POST /webhooks/github`.
2. The middleware rejects a declared body larger than 1 MiB. The endpoint checks the actual body size as well.
3. Only `pull_request` deliveries are considered. The raw body must pass `X-Hub-Signature-256` validation before JSON is parsed.
4. Only a `closed` pull request with `merged: true` can continue.
5. The service reads `.backportguard.yml` at `merge_commit_sha` through the GitHub API and safely parses the declared labels and branches.
6. SQLite atomically claims the GitHub delivery ID. Retries then return without creating another issue.
7. The GitHub App installation token creates one reminder issue.

## Data

SQLite stores only the delivery identifier needed for replay protection. Configuration is read from the monitored repository and is not stored. GitHub credentials, private keys, webhook secrets, and raw deliveries are never written to the database or logs.

## Failure model

- Invalid signatures and malformed bodies are rejected.
- Unsupported events, missing configuration, and policy mismatches are acknowledged without side effects.
- A failed GitHub issue request releases the delivery claim so GitHub can retry safely.
- The service does not run a command, clone a repository, or consume executable configuration.

## Deployment boundary

`backportguard.service` is the only service required. It runs as its own system user, binds FastAPI to loopback only, and can run the Cloudflare Tunnel client in the same constrained cgroup. See [operations](operations.md).
