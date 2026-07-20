from __future__ import annotations

import hashlib
import hmac
import logging
import os
from dataclasses import dataclass

from fastapi import FastAPI, Header, HTTPException, Request, Response

from .config import BackportConfig, ConfigurationError, parse_config
from .db import DeliveryStore
from .github import ApiGitHubClient, GitHubClient, GitHubError

MAX_BODY_BYTES = 1_048_576
logger = logging.getLogger(__name__)


@dataclass
class Settings:
    webhook_secret: str
    database_path: str = "/var/lib/backportguard/backportguard.sqlite3"
    github_token: str | None = None
    github_app_id: str | None = None
    github_installation_id: str | None = None
    github_private_key_path: str | None = None

    @classmethod
    def from_environment(cls) -> "Settings":
        secret = os.environ.get("WEBHOOK_SECRET", "")
        if not secret:
            raise RuntimeError("WEBHOOK_SECRET is required")
        return cls(
            webhook_secret=secret,
            database_path=os.environ.get("DATABASE_PATH", cls.database_path),
            github_token=os.environ.get("GITHUB_TOKEN") or None,
            github_app_id=os.environ.get("GITHUB_APP_ID") or None,
            github_installation_id=os.environ.get("GITHUB_INSTALLATION_ID") or None,
            github_private_key_path=os.environ.get("GITHUB_PRIVATE_KEY_PATH") or None,
        )


def verify_signature(secret: str, body: bytes, signature: str | None) -> bool:
    if not signature or not signature.startswith("sha256="):
        return False
    expected = "sha256=" + hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature)


def should_handle(payload: dict, config: BackportConfig) -> bool:
    pull_request = payload.get("pull_request")
    if not isinstance(pull_request, dict) or not pull_request.get("merged"):
        return False
    labels = pull_request.get("labels", [])
    names = {item.get("name") for item in labels if isinstance(item, dict)}
    return set(config.required_labels).issubset(names)


def _issue_text(payload: dict, config: BackportConfig) -> tuple[str, str]:
    pr = payload["pull_request"]
    repo = payload["repository"]
    number = pr.get("number") or payload.get("number")
    title = str(pr.get("title", "Merged pull request"))
    url = str(pr.get("html_url", ""))
    branches = "\n".join(f"- `{branch}`" for branch in config.branches)
    issue_title = f"Backport reminder: #{number} {title}"[:240]
    body = (
        "A merged pull request marked for backport needs review.\n\n"
        f"Source PR: {url}\n\n"
        "Target branches:\n"
        f"{branches}\n\n"
        "BackportGuard only creates this reminder; it never applies code automatically."
    )
    return issue_title, body


def create_app(settings: Settings | None = None, github: GitHubClient | None = None) -> FastAPI:
    settings = settings or Settings.from_environment()
    store = DeliveryStore(settings.database_path)
    client = github or ApiGitHubClient(
        token=settings.github_token,
        app_id=settings.github_app_id,
        installation_id=settings.github_installation_id,
        private_key_path=settings.github_private_key_path,
    )
    store.initialize()
    app = FastAPI(title="BackportGuard", version="0.1.0")

    @app.middleware("http")
    async def request_limit(request: Request, call_next):
        length = request.headers.get("content-length")
        if length and (not length.isdigit() or int(length) > MAX_BODY_BYTES):
            return Response(status_code=413)
        return await call_next(request)

    @app.get("/", response_class=Response)
    def index() -> Response:
        return Response(
            '<!doctype html><title>BackportGuard</title><h1>BackportGuard</h1><p>Open-source GitHub backport reminders.</p>',
            media_type="text/html",
        )

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.post("/webhooks/github")
    async def github_webhook(
        request: Request,
        x_github_event: str | None = Header(default=None),
        x_hub_signature_256: str | None = Header(default=None),
        x_github_delivery: str | None = Header(default=None),
    ) -> Response:
        if x_github_event != "pull_request":
            return Response(status_code=202)
        body = await request.body()
        if len(body) > MAX_BODY_BYTES:
            raise HTTPException(status_code=413, detail="payload too large")
        if not verify_signature(settings.webhook_secret, body, x_hub_signature_256):
            raise HTTPException(status_code=401, detail="invalid signature")
        try:
            payload = await request.json()
        except Exception as exc:
            raise HTTPException(status_code=400, detail="invalid JSON") from exc
        if not isinstance(payload, dict) or payload.get("action") != "closed":
            return Response(status_code=202)
        repository = payload.get("repository", {})
        pr = payload.get("pull_request", {})
        full_name = repository.get("full_name") if isinstance(repository, dict) else None
        ref = pr.get("merge_commit_sha") if isinstance(pr, dict) else None
        if not isinstance(full_name, str) or not isinstance(ref, str) or not ref:
            raise HTTPException(status_code=400, detail="missing repository or merge commit")
        try:
            config = parse_config(client.get_config(full_name, ref))
        except (GitHubError, ConfigurationError):
            logger.warning("webhook configuration unavailable or invalid for repository")
            return Response(status_code=202)
        if not should_handle(payload, config):
            return Response(status_code=202)
        delivery_id = x_github_delivery or f"{full_name}:{pr.get('number')}:{ref}"
        if not store.claim(delivery_id):
            return Response(status_code=202)
        try:
            title, issue_body = _issue_text(payload, config)
            client.create_issue(full_name, title, issue_body)
        except GitHubError:
            store.release(delivery_id)
            logger.exception("GitHub issue creation failed")
            raise HTTPException(status_code=502, detail="GitHub request failed")
        return Response(status_code=201)

    return app


app = create_app() if os.environ.get("WEBHOOK_SECRET") else FastAPI(title="BackportGuard")
