# BackportGuard — final report

## Status

The application source, tests, systemd unit template, Cloudflare Pages static site, and deployment documentation are present in this repository. Local verification is pending dependency installation.

## Links

- GitHub: pending repository creation (`devggchel/backportguard` intended)
- Site: pending Cloudflare Pages project
- Application: pending Cloudflare Tunnel

## GitHub App

Not registered. Required minimal permissions: Metadata read-only, Contents read-only, Pull requests read-only, Issues read/write; event: Pull request.

## Required manual authority

The VPS account has no `sudo` binary and cannot create `/opt/backportguard`, `/etc/backportguard`, `/var/lib/backportguard`, the `backportguard` system user, or `backportguard.service`. GitHub and Cloudflare connectors available in this session do not expose repository creation, GitHub App registration, Cloudflare Pages, or Tunnel management.

## Removal (BackportGuard only)

Stop and disable `backportguard.service`, then remove `/opt/backportguard`, `/etc/backportguard`, `/var/lib/backportguard`, the `backportguard` user, and its Cloudflare Tunnel/Pages project. Do not touch existing bot services or files.

## Safety confirmation

No Telegram bot files, services, dependencies, databases, environment, containers, cron jobs, network settings, or existing Cloudflare resources were modified. No paid resources or fictitious activity were created.
