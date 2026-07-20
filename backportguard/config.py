from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import yaml


class ConfigurationError(ValueError):
    """Raised when .backportguard.yml has an unsupported shape."""


@dataclass(frozen=True)
class BackportConfig:
    branches: tuple[str, ...]
    required_labels: tuple[str, ...]


def _string_list(value: Any, field: str) -> tuple[str, ...]:
    if not isinstance(value, list) or not value:
        raise ConfigurationError(f"{field} must be a non-empty list")
    if not all(isinstance(item, str) and item.strip() for item in value):
        raise ConfigurationError(f"{field} must contain non-empty strings")
    return tuple(dict.fromkeys(item.strip() for item in value))


def parse_config(contents: str) -> BackportConfig:
    """Parse only the declarative settings used by BackportGuard."""
    try:
        raw = yaml.safe_load(contents)
    except yaml.YAMLError as exc:
        raise ConfigurationError("invalid YAML") from exc
    if not isinstance(raw, dict):
        raise ConfigurationError("configuration must be a mapping")
    labels = raw.get("labels")
    if not isinstance(labels, dict):
        raise ConfigurationError("labels must be a mapping")
    return BackportConfig(
        branches=_string_list(raw.get("branches"), "branches"),
        required_labels=_string_list(labels.get("required"), "labels.required"),
    )
