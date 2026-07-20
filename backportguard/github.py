from __future__ import annotations

import base64
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

import httpx
import jwt


class GitHubError(RuntimeError):
    pass


class GitHubClient(Protocol):
    def get_config(self, repository: str, ref: str) -> str: ...

    def create_issue(self, repository: str, title: str, body: str) -> str: ...


@dataclass
class ApiGitHubClient:
    token: str | None = None
    app_id: str | None = None
    installation_id: str | None = None
    private_key_path: str | None = None

    def _headers(self) -> dict[str, str]:
        token = self._installation_token() if not self.token else self.token
        return {
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
            "X-GitHub-Api-Version": "2022-11-28",
        }

    def _installation_token(self) -> str:
        if not all((self.app_id, self.installation_id, self.private_key_path)):
            raise GitHubError("GitHub App credentials are not configured")
        private_key = Path(self.private_key_path).read_text(encoding="utf-8")
        app_jwt = jwt.encode(
            {"iat": int(time.time()) - 30, "exp": int(time.time()) + 540, "iss": self.app_id},
            private_key,
            algorithm="RS256",
        )
        response = httpx.post(
            f"https://api.github.com/app/installations/{self.installation_id}/access_tokens",
            headers={"Accept": "application/vnd.github+json", "Authorization": f"Bearer {app_jwt}"},
            timeout=10,
        )
        if response.status_code != 201:
            raise GitHubError("could not obtain GitHub installation token")
        return response.json()["token"]

    def get_config(self, repository: str, ref: str) -> str:
        response = httpx.get(
            f"https://api.github.com/repos/{repository}/contents/.backportguard.yml",
            params={"ref": ref}, headers=self._headers(), timeout=10,
        )
        if response.status_code != 200:
            raise GitHubError("could not read .backportguard.yml")
        content = response.json().get("content", "")
        try:
            return base64.b64decode(content).decode("utf-8")
        except Exception as exc:  # content is untrusted remote data
            raise GitHubError("invalid configuration file encoding") from exc

    def create_issue(self, repository: str, title: str, body: str) -> str:
        response = httpx.post(
            f"https://api.github.com/repos/{repository}/issues",
            json={"title": title, "body": body}, headers=self._headers(), timeout=10,
        )
        if response.status_code != 201:
            raise GitHubError("could not create backport reminder issue")
        return str(response.json().get("html_url", ""))
