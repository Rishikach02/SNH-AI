"""
Service layer containing the business logic for managing tree nodes.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Optional

import sqlite3

from . import db


class TreeServiceError(Exception):
    """Base error for service failures."""


class ValidationError(TreeServiceError):
    """Raised when the input payload is invalid."""


class NodeNotFound(TreeServiceError):
    """Raised when a requested node does not exist."""


@dataclass
class TreeNode:
    id: int
    label: str
    parent_id: Optional[int]
    children: List["TreeNode"] = field(default_factory=list)

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "label": self.label,
            "children": [child.to_dict() for child in self.children],
        }


def create_node(label: str, parent_id: Optional[int]) -> TreeNode:
    label = (label or "").strip()
    if not label:
        raise ValidationError("label is required")

    with db.get_connection() as conn:
        if parent_id is not None:
            parent = conn.execute(
                "SELECT id FROM nodes WHERE id = ?", (parent_id,)
            ).fetchone()
            if parent is None:
                raise NodeNotFound(f"Parent node {parent_id} does not exist")

        cursor = conn.execute(
            "INSERT INTO nodes (label, parent_id) VALUES (?, ?)",
            (label, parent_id),
        )
        node_id = cursor.lastrowid
        conn.commit()

        return TreeNode(id=node_id, label=label, parent_id=parent_id)


def list_trees() -> List[TreeNode]:
    with db.get_connection() as conn:
        rows = conn.execute(
            "SELECT id, label, parent_id FROM nodes ORDER BY id"
        ).fetchall()

    return _rows_to_forest(rows)


def clear_all() -> None:
    """Utility helper used in tests to clear the database."""
    with db.get_connection() as conn:
        conn.execute("DELETE FROM nodes")
        conn.commit()


def _rows_to_forest(rows: Iterable[sqlite3.Row]) -> List[TreeNode]:
    nodes: Dict[int, TreeNode] = {}
    roots: List[TreeNode] = []

    for row in rows:
        nodes[row["id"]] = TreeNode(
            id=row["id"],
            label=row["label"],
            parent_id=row["parent_id"],
        )

    for node in nodes.values():
        if node.parent_id is None:
            roots.append(node)
        else:
            parent = nodes.get(node.parent_id)
            if parent:
                parent.children.append(node)
            else:
                roots.append(node)

    # ensure deterministic order: parents before children already satisfied by insert order
    def sort_children(tree_node: TreeNode) -> None:
        tree_node.children.sort(key=lambda c: c.id)
        for child in tree_node.children:
            sort_children(child)

    roots.sort(key=lambda n: n.id)
    for root in roots:
        sort_children(root)

    return roots
