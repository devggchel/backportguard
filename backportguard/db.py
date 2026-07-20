from __future__ import annotations

import sqlite3
from pathlib import Path


class DeliveryStore:
    def __init__(self, path: str) -> None:
        self.path = Path(path)

    def initialize(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as connection:
            connection.execute(
                """CREATE TABLE IF NOT EXISTS deliveries (
                    delivery_id TEXT PRIMARY KEY,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                )"""
            )

    def claim(self, delivery_id: str) -> bool:
        try:
            with self._connect() as connection:
                connection.execute("INSERT INTO deliveries (delivery_id) VALUES (?)", (delivery_id,))
            return True
        except sqlite3.IntegrityError:
            return False

    def release(self, delivery_id: str) -> None:
        with self._connect() as connection:
            connection.execute("DELETE FROM deliveries WHERE delivery_id = ?", (delivery_id,))

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self.path, timeout=5)
