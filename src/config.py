"""
Runtime configuration helpers for the tree API server.
"""

from __future__ import annotations

import os
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DB_PATH = Path(os.environ.get("TREE_API_DB_PATH", DATA_DIR / "trees.db"))

HOST = os.environ.get("TREE_API_HOST", "127.0.0.1")
PORT = int(os.environ.get("TREE_API_PORT", "9001"))
