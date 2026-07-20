from __future__ import annotations

import hashlib
import hmac
import json

from fastapi.testclient import TestClient

from backportguard.main import Settings, create_app


class FakeGitHub:
    def __init__(self) -> None:
        self.issues: list[tuple[str, str, str]] = []

    def get_config(self, repository: str, ref: str) -> str:
        return "branches:\n  - release/1.0\nlabels:\n  required:\n    - backport\n"

    def create_issue(self, repository: str, title: str, body: str) -> str:
        self.issues.append((repository, title, body))
        return "https://example.test/issues/1"


def payload() -> dict:
    return {
        "action": "closed",
        "number": 14,
        "repository": {"full_name": "octo/example"},
        "pull_request": {
            "number": 14,
            "merged": True,
            "merge_commit_sha": "abc123",
            "title": "Fix parser",
            "html_url": "https://github.com/octo/example/pull/14",
            "labels": [{"name": "backport"}],
        },
    }


def signed_headers(body: bytes) -> dict[str, str]:
    signature = hmac.new(b"test-secret", body, hashlib.sha256).hexdigest()
    return {
        "X-GitHub-Event": "pull_request",
        "X-Hub-Signature-256": f"sha256={signature}",
        "X-GitHub-Delivery": "delivery-1",
    }


def test_health(tmp_path) -> None:
    client = TestClient(create_app(Settings("test-secret", str(tmp_path / "db.sqlite3")), FakeGitHub()))
    assert client.get("/health").json() == {"status": "ok"}


def test_valid_merged_backport_creates_one_issue(tmp_path) -> None:
    github = FakeGitHub()
    client = TestClient(create_app(Settings("test-secret", str(tmp_path / "db.sqlite3")), github))
    body = json.dumps(payload()).encode()
    assert client.post("/webhooks/github", content=body, headers=signed_headers(body)).status_code == 201
    assert client.post("/webhooks/github", content=body, headers=signed_headers(body)).status_code == 202
    assert len(github.issues) == 1
    assert "release/1.0" in github.issues[0][2]


def test_invalid_signature_is_rejected(tmp_path) -> None:
    client = TestClient(create_app(Settings("test-secret", str(tmp_path / "db.sqlite3")), FakeGitHub()))
    assert client.post("/webhooks/github", content=b"{}", headers={"X-GitHub-Event": "pull_request"}).status_code == 401


def test_unlabelled_pr_is_ignored(tmp_path) -> None:
    github = FakeGitHub()
    client = TestClient(create_app(Settings("test-secret", str(tmp_path / "db.sqlite3")), github))
    event = payload()
    event["pull_request"]["labels"] = []
    body = json.dumps(event).encode()
    assert client.post("/webhooks/github", content=body, headers=signed_headers(body)).status_code == 202
    assert github.issues == []
