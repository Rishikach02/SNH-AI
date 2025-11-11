from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from src import config, db, tree_service


class TreeServiceTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.tmpdir = tempfile.TemporaryDirectory()
        config.DB_PATH = Path(self.tmpdir.name) / "test.db"
        db.initialize()
        tree_service.clear_all()

    def tearDown(self) -> None:
        self.tmpdir.cleanup()

    def test_create_root_node(self) -> None:
        node = tree_service.create_node("root", None)
        self.assertEqual(node.label, "root")
        self.assertIsNone(node.parent_id)

        trees = tree_service.list_trees()
        self.assertEqual(len(trees), 1)
        self.assertEqual(trees[0].label, "root")

    def test_create_child_node(self) -> None:
        parent = tree_service.create_node("root", None)
        child = tree_service.create_node("leaf", parent.id)
        self.assertEqual(child.parent_id, parent.id)

        trees = tree_service.list_trees()
        self.assertEqual(len(trees[0].children), 1)
        self.assertEqual(trees[0].children[0].label, "leaf")

    def test_missing_parent_raises(self) -> None:
        with self.assertRaises(tree_service.NodeNotFound):
            tree_service.create_node("orphan", 999)

    def test_label_required(self) -> None:
        with self.assertRaises(tree_service.ValidationError):
            tree_service.create_node("   ", None)


if __name__ == "__main__":
    unittest.main()
