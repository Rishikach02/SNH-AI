"""
Comprehensive test suite covering edge cases and complex scenarios.
"""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from src import config, db, tree_service


class ComprehensiveTreeTestCase(unittest.TestCase):
    """Extended test cases for complex tree operations and edge cases."""

    def setUp(self) -> None:
        self.tmpdir = tempfile.TemporaryDirectory()
        config.DB_PATH = Path(self.tmpdir.name) / "test.db"
        db.initialize()
        tree_service.clear_all()

    def tearDown(self) -> None:
        self.tmpdir.cleanup()

    # ===== Input Validation Tests =====

    def test_empty_label_raises_validation_error(self) -> None:
        """Empty string label should raise ValidationError."""
        with self.assertRaises(tree_service.ValidationError) as ctx:
            tree_service.create_node("", None)
        self.assertIn("label is required", str(ctx.exception))

    def test_whitespace_only_label_raises_validation_error(self) -> None:
        """Whitespace-only label should raise ValidationError."""
        with self.assertRaises(tree_service.ValidationError) as ctx:
            tree_service.create_node("   \t\n   ", None)
        self.assertIn("label is required", str(ctx.exception))

    def test_none_label_raises_validation_error(self) -> None:
        """None as label should raise ValidationError."""
        with self.assertRaises(tree_service.ValidationError):
            tree_service.create_node(None, None)

    def test_label_with_surrounding_whitespace_is_trimmed(self) -> None:
        """Label with leading/trailing whitespace should be trimmed."""
        node = tree_service.create_node("  test  ", None)
        self.assertEqual(node.label, "test")

    def test_nonexistent_parent_raises_not_found(self) -> None:
        """Referencing non-existent parent should raise NodeNotFound."""
        with self.assertRaises(tree_service.NodeNotFound) as ctx:
            tree_service.create_node("orphan", 99999)
        self.assertIn("99999", str(ctx.exception))

    def test_negative_parent_id_raises_not_found(self) -> None:
        """Negative parent_id should raise NodeNotFound."""
        with self.assertRaises(tree_service.NodeNotFound):
            tree_service.create_node("orphan", -1)

    def test_zero_parent_id_raises_not_found(self) -> None:
        """Zero parent_id should raise NodeNotFound."""
        with self.assertRaises(tree_service.NodeNotFound):
            tree_service.create_node("orphan", 0)

    # ===== Multiple Roots Tests =====

    def test_multiple_independent_trees(self) -> None:
        """Should support multiple independent root nodes (forest)."""
        root1 = tree_service.create_node("root1", None)
        root2 = tree_service.create_node("root2", None)
        root3 = tree_service.create_node("root3", None)

        trees = tree_service.list_trees()
        self.assertEqual(len(trees), 3)
        self.assertEqual(trees[0].label, "root1")
        self.assertEqual(trees[1].label, "root2")
        self.assertEqual(trees[2].label, "root3")

    def test_forest_with_mixed_structures(self) -> None:
        """Should handle forest with different tree depths."""
        # Tree 1: Deep hierarchy
        root1 = tree_service.create_node("Company A", None)
        dept1 = tree_service.create_node("Engineering", root1.id)
        team1 = tree_service.create_node("Backend Team", dept1.id)
        member1 = tree_service.create_node("John", team1.id)

        # Tree 2: Shallow hierarchy
        root2 = tree_service.create_node("Company B", None)
        dept2 = tree_service.create_node("Sales", root2.id)

        # Tree 3: Just root
        root3 = tree_service.create_node("Company C", None)

        trees = tree_service.list_trees()
        self.assertEqual(len(trees), 3)
        self.assertEqual(len(trees[0].children), 1)  # Company A has 1 dept
        self.assertEqual(len(trees[1].children), 1)  # Company B has 1 dept
        self.assertEqual(len(trees[2].children), 0)  # Company C has no children

    # ===== Deep Nesting Tests =====

    def test_deep_hierarchy(self) -> None:
        """Should handle deeply nested tree structures."""
        root = tree_service.create_node("Level 0", None)
        current = root

        # Create 10 levels deep
        for i in range(1, 11):
            current = tree_service.create_node(f"Level {i}", current.id)

        trees = tree_service.list_trees()
        self.assertEqual(len(trees), 1)

        # Traverse to verify depth
        depth = 0
        node = trees[0]
        while node.children:
            depth += 1
            node = node.children[0]
        self.assertEqual(depth, 10)

    # ===== Wide Tree Tests =====

    def test_many_children_single_parent(self) -> None:
        """Should handle parent with many children."""
        root = tree_service.create_node("root", None)

        # Create 50 children
        for i in range(50):
            tree_service.create_node(f"child_{i}", root.id)

        trees = tree_service.list_trees()
        self.assertEqual(len(trees), 1)
        self.assertEqual(len(trees[0].children), 50)

    def test_children_are_sorted_by_id(self) -> None:
        """Children should be returned in sorted order by ID."""
        root = tree_service.create_node("root", None)
        child1 = tree_service.create_node("zzzz", root.id)
        child2 = tree_service.create_node("aaaa", root.id)
        child3 = tree_service.create_node("mmmm", root.id)

        trees = tree_service.list_trees()
        children = trees[0].children

        # Should be sorted by ID, not label
        self.assertEqual(children[0].id, child1.id)
        self.assertEqual(children[1].id, child2.id)
        self.assertEqual(children[2].id, child3.id)

    # ===== Large Dataset Tests =====

    def test_large_flat_tree(self) -> None:
        """Should handle large number of nodes efficiently."""
        root = tree_service.create_node("root", None)

        # Create 100 nodes
        for i in range(100):
            tree_service.create_node(f"node_{i:03d}", root.id)

        trees = tree_service.list_trees()
        self.assertEqual(len(trees), 1)
        self.assertEqual(len(trees[0].children), 100)

    def test_balanced_tree(self) -> None:
        """Should handle balanced tree structure."""
        root = tree_service.create_node("root", None)

        # Level 1: 3 children
        level1_nodes = []
        for i in range(3):
            node = tree_service.create_node(f"L1_{i}", root.id)
            level1_nodes.append(node)

        # Level 2: each L1 node gets 3 children
        for l1_node in level1_nodes:
            for j in range(3):
                tree_service.create_node(f"L2_{l1_node.id}_{j}", l1_node.id)

        trees = tree_service.list_trees()
        self.assertEqual(len(trees), 1)
        self.assertEqual(len(trees[0].children), 3)
        for child in trees[0].children:
            self.assertEqual(len(child.children), 3)

    # ===== Special Characters and Unicode =====

    def test_label_with_special_characters(self) -> None:
        """Should handle labels with special characters."""
        special_labels = [
            "node-with-dash",
            "node_with_underscore",
            "node.with.dots",
            "node@with#symbols",
            "node (with) parentheses",
            "node/with/slashes",
        ]

        for label in special_labels:
            node = tree_service.create_node(label, None)
            self.assertEqual(node.label, label)

        trees = tree_service.list_trees()
        self.assertEqual(len(trees), len(special_labels))

    def test_label_with_unicode(self) -> None:
        """Should handle Unicode characters in labels."""
        unicode_labels = [
            "日本語",  # Japanese
            "中文",  # Chinese
            "العربية",  # Arabic
            "Русский",  # Russian
            "🌲🎄🌳",  # Emojis
            "Café",  # Accented characters
        ]

        for label in unicode_labels:
            node = tree_service.create_node(label, None)
            self.assertEqual(node.label, label)

        trees = tree_service.list_trees()
        self.assertEqual(len(trees), len(unicode_labels))

    def test_very_long_label(self) -> None:
        """Should handle very long labels."""
        long_label = "A" * 1000
        node = tree_service.create_node(long_label, None)
        self.assertEqual(node.label, long_label)
        self.assertEqual(len(node.label), 1000)

    # ===== Tree Structure Tests =====

    def test_siblings_at_same_level(self) -> None:
        """Should correctly handle multiple siblings."""
        root = tree_service.create_node("root", None)
        child1 = tree_service.create_node("child1", root.id)
        child2 = tree_service.create_node("child2", root.id)
        child3 = tree_service.create_node("child3", root.id)

        # Add grandchildren to first child
        grandchild1 = tree_service.create_node("grandchild1", child1.id)
        grandchild2 = tree_service.create_node("grandchild2", child1.id)

        trees = tree_service.list_trees()
        self.assertEqual(len(trees), 1)
        self.assertEqual(len(trees[0].children), 3)
        self.assertEqual(len(trees[0].children[0].children), 2)
        self.assertEqual(len(trees[0].children[1].children), 0)
        self.assertEqual(len(trees[0].children[2].children), 0)

    def test_complex_organizational_structure(self) -> None:
        """Should handle realistic organizational hierarchy."""
        # CEO
        ceo = tree_service.create_node("CEO", None)

        # C-Suite
        cto = tree_service.create_node("CTO", ceo.id)
        cfo = tree_service.create_node("CFO", ceo.id)
        coo = tree_service.create_node("COO", ceo.id)

        # Engineering under CTO
        eng_vp = tree_service.create_node("VP Engineering", cto.id)
        backend = tree_service.create_node("Backend Team", eng_vp.id)
        frontend = tree_service.create_node("Frontend Team", eng_vp.id)
        devops = tree_service.create_node("DevOps Team", eng_vp.id)

        # Finance under CFO
        accounting = tree_service.create_node("Accounting", cfo.id)
        fp_and_a = tree_service.create_node("FP&A", cfo.id)

        # Operations under COO
        sales = tree_service.create_node("Sales", coo.id)
        support = tree_service.create_node("Support", coo.id)

        trees = tree_service.list_trees()
        self.assertEqual(len(trees), 1)
        self.assertEqual(trees[0].label, "CEO")
        self.assertEqual(len(trees[0].children), 3)  # 3 C-suite members

        # Verify CTO has VP Engineering
        cto_node = trees[0].children[0]
        self.assertEqual(cto_node.label, "CTO")
        self.assertEqual(len(cto_node.children), 1)

        # Verify VP Engineering has 3 teams
        vp_node = cto_node.children[0]
        self.assertEqual(len(vp_node.children), 3)

    # ===== Empty State Tests =====

    def test_list_trees_empty_database(self) -> None:
        """list_trees() should return empty list for empty database."""
        trees = tree_service.list_trees()
        self.assertEqual(trees, [])
        self.assertIsInstance(trees, list)

    # ===== Node Creation Order Tests =====

    def test_nodes_created_out_of_order(self) -> None:
        """Should handle nodes created in non-sequential order."""
        # Create root
        root = tree_service.create_node("root", None)

        # Create leaf first (will be orphaned initially in this test's concept,
        # but actually we create with parent, so this tests parent reference)
        child1 = tree_service.create_node("child1", root.id)
        grandchild = tree_service.create_node("grandchild", child1.id)
        child2 = tree_service.create_node("child2", root.id)

        trees = tree_service.list_trees()
        self.assertEqual(len(trees), 1)
        self.assertEqual(len(trees[0].children), 2)

    # ===== Duplicate Labels Tests =====

    def test_duplicate_labels_different_parents(self) -> None:
        """Should allow duplicate labels under different parents."""
        root1 = tree_service.create_node("root1", None)
        root2 = tree_service.create_node("root2", None)

        child1a = tree_service.create_node("child", root1.id)
        child2a = tree_service.create_node("child", root2.id)

        trees = tree_service.list_trees()
        self.assertEqual(len(trees), 2)
        self.assertEqual(trees[0].children[0].label, "child")
        self.assertEqual(trees[1].children[0].label, "child")
        # But different IDs
        self.assertNotEqual(trees[0].children[0].id, trees[1].children[0].id)

    def test_duplicate_labels_same_parent(self) -> None:
        """Should allow duplicate labels under same parent."""
        root = tree_service.create_node("root", None)
        child1 = tree_service.create_node("duplicate", root.id)
        child2 = tree_service.create_node("duplicate", root.id)

        trees = tree_service.list_trees()
        self.assertEqual(len(trees[0].children), 2)
        self.assertEqual(trees[0].children[0].label, "duplicate")
        self.assertEqual(trees[0].children[1].label, "duplicate")
        self.assertNotEqual(trees[0].children[0].id, trees[0].children[1].id)

    # ===== TreeNode Tests =====

    def test_treenode_to_dict_no_children(self) -> None:
        """TreeNode.to_dict() should work for leaf nodes."""
        node = tree_service.create_node("leaf", None)
        node_dict = node.to_dict()

        self.assertEqual(node_dict["id"], node.id)
        self.assertEqual(node_dict["label"], "leaf")
        self.assertEqual(node_dict["children"], [])
        self.assertNotIn("parent_id", node_dict)

    def test_treenode_to_dict_with_children(self) -> None:
        """TreeNode.to_dict() should recursively serialize children."""
        root = tree_service.create_node("root", None)
        child = tree_service.create_node("child", root.id)

        trees = tree_service.list_trees()
        root_dict = trees[0].to_dict()

        self.assertEqual(root_dict["label"], "root")
        self.assertEqual(len(root_dict["children"]), 1)
        self.assertEqual(root_dict["children"][0]["label"], "child")
        self.assertNotIn("parent_id", root_dict)

    # ===== Concurrent Creation Tests =====

    def test_sequential_node_ids(self) -> None:
        """Node IDs should be sequential and auto-incremented."""
        node1 = tree_service.create_node("node1", None)
        node2 = tree_service.create_node("node2", None)
        node3 = tree_service.create_node("node3", None)

        self.assertEqual(node2.id, node1.id + 1)
        self.assertEqual(node3.id, node2.id + 1)

    # ===== Real-World Scenario Tests =====

    def test_file_system_structure(self) -> None:
        """Should handle file system-like hierarchy."""
        root = tree_service.create_node("/", None)
        home = tree_service.create_node("home", root.id)
        user = tree_service.create_node("user", home.id)
        documents = tree_service.create_node("documents", user.id)
        file1 = tree_service.create_node("report.pdf", documents.id)

        etc = tree_service.create_node("etc", root.id)
        config = tree_service.create_node("config", etc.id)

        trees = tree_service.list_trees()
        self.assertEqual(len(trees), 1)
        self.assertEqual(trees[0].label, "/")
        self.assertEqual(len(trees[0].children), 2)  # home and etc

    def test_category_hierarchy(self) -> None:
        """Should handle e-commerce category structure."""
        electronics = tree_service.create_node("Electronics", None)
        computers = tree_service.create_node("Computers", electronics.id)
        laptops = tree_service.create_node("Laptops", computers.id)
        gaming = tree_service.create_node("Gaming Laptops", laptops.id)
        business = tree_service.create_node("Business Laptops", laptops.id)

        phones = tree_service.create_node("Phones", electronics.id)
        smartphones = tree_service.create_node("Smartphones", phones.id)

        trees = tree_service.list_trees()
        self.assertEqual(len(trees), 1)
        
        # Verify structure
        elec = trees[0]
        self.assertEqual(len(elec.children), 2)  # Computers and Phones
        comp = elec.children[0]
        self.assertEqual(len(comp.children), 1)  # Laptops
        laps = comp.children[0]
        self.assertEqual(len(laps.children), 2)  # Gaming and Business


if __name__ == "__main__":
    unittest.main()

