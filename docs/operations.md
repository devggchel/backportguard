# Operations

## Service layout

| Path | Purpose |
| --- | --- |
| `/opt/backportguard` | Application code and isolated Python environment |
| `/etc/backportguard` | Root-owned configuration and secrets |
| `/var/lib/backportguard` | SQLite data |

The supplied unit binds the application to `127.0.0.1:8765`, uses the dedicated `backportguard` account, and applies memory, CPU, task, filesystem, and privilege restrictions.

## Checks

```bash
systemctl status backportguard.service
curl --fail http://127.0.0.1:8765/health
```

Do not open an inbound firewall port. A dedicated public hostname should point through the existing Cloudflare Tunnel to `http://127.0.0.1:8765`.

## Recovery

`Restart=on-failure` restarts only BackportGuard. To stop it deliberately:

```bash
sudo systemctl stop backportguard.service
```

To remove only this project, disable its unit, remove `/opt/backportguard`, `/etc/backportguard`, `/var/lib/backportguard`, and the `backportguard` system user, then remove its Cloudflare Tunnel and Pages resources. Do not alter unrelated services or DNS records.
