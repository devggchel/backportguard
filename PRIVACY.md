# Privacy

BackportGuard stores only GitHub delivery identifiers and timestamps in its local SQLite database to prevent duplicate handling. It sends GitHub API requests only to read `.backportguard.yml` and create the reminder issue. Webhook secrets, GitHub App private keys, and access tokens are not logged or committed.
