#!/usr/bin/env python
"""
Populate the database with realistic sample data for testing and demonstration.

This script creates a comprehensive organizational hierarchy with multiple companies,
departments, teams, and employees to showcase the tree API's capabilities.
"""

from __future__ import annotations

from src import db, tree_service


def clear_database() -> None:
    """Clear all existing data."""
    print("Clearing existing data...")
    tree_service.clear_all()
    print("✓ Database cleared")


def create_tech_company() -> None:
    """Create a large technology company organizational structure."""
    print("\n📊 Creating TechCorp organizational structure...")

    # CEO
    ceo = tree_service.create_node("Sarah Chen - CEO", None)
    print(f"  Created: {ceo.label} (id={ceo.id})")

    # C-Suite reporting to CEO
    cto = tree_service.create_node("Michael Kumar - CTO", ceo.id)
    cfo = tree_service.create_node("Jennifer Williams - CFO", ceo.id)
    cmo = tree_service.create_node("David Martinez - CMO", ceo.id)
    coo = tree_service.create_node("Lisa Anderson - COO", ceo.id)
    chro = tree_service.create_node("Robert Taylor - CHRO", ceo.id)

    # Engineering Organization under CTO
    print("  Building Engineering org...")
    vp_eng = tree_service.create_node("VP Engineering - James Wilson", cto.id)

    # Backend Teams
    backend_dir = tree_service.create_node("Director Backend - Amy Zhang", vp_eng.id)
    api_team = tree_service.create_node("API Services Team", backend_dir.id)
    tree_service.create_node("Alice Johnson - Senior Engineer", api_team.id)
    tree_service.create_node("Bob Smith - Engineer", api_team.id)
    tree_service.create_node("Carol Davis - Engineer", api_team.id)

    data_team = tree_service.create_node("Data Platform Team", backend_dir.id)
    tree_service.create_node("David Lee - Staff Engineer", data_team.id)
    tree_service.create_node("Emma Garcia - Senior Engineer", data_team.id)
    tree_service.create_node("Frank Miller - Engineer", data_team.id)

    infra_team = tree_service.create_node("Infrastructure Team", backend_dir.id)
    tree_service.create_node("Grace Kim - Principal Engineer", infra_team.id)
    tree_service.create_node("Henry Brown - Senior Engineer", infra_team.id)

    # Frontend Teams
    frontend_dir = tree_service.create_node("Director Frontend - Tom Rodriguez", vp_eng.id)
    web_team = tree_service.create_node("Web Platform Team", frontend_dir.id)
    tree_service.create_node("Ivy Thompson - Tech Lead", web_team.id)
    tree_service.create_node("Jack Wilson - Senior Engineer", web_team.id)
    tree_service.create_node("Kate Martinez - Engineer", web_team.id)

    mobile_team = tree_service.create_node("Mobile Team", frontend_dir.id)
    tree_service.create_node("Liam Anderson - iOS Lead", mobile_team.id)
    tree_service.create_node("Maya Patel - Android Lead", mobile_team.id)
    tree_service.create_node("Noah White - React Native Engineer", mobile_team.id)

    # QA Teams
    qa_dir = tree_service.create_node("Director QA - Olivia Brown", vp_eng.id)
    automation_team = tree_service.create_node("Automation Team", qa_dir.id)
    tree_service.create_node("Paul Green - QA Lead", automation_team.id)
    tree_service.create_node("Quinn Davis - QA Engineer", automation_team.id)

    manual_qa = tree_service.create_node("Manual QA Team", qa_dir.id)
    tree_service.create_node("Rachel Foster - QA Lead", manual_qa.id)
    tree_service.create_node("Sam Cooper - QA Engineer", manual_qa.id)

    # DevOps
    devops = tree_service.create_node("DevOps Team", cto.id)
    tree_service.create_node("Tony Stark - DevOps Lead", devops.id)
    tree_service.create_node("Uma Thurman - Site Reliability Engineer", devops.id)
    tree_service.create_node("Victor Hugo - Cloud Engineer", devops.id)

    # Security
    security = tree_service.create_node("Security Team", cto.id)
    tree_service.create_node("Wendy Wu - Security Lead", security.id)
    tree_service.create_node("Xavier Knight - Security Engineer", security.id)

    # Finance Organization under CFO
    print("  Building Finance org...")
    accounting = tree_service.create_node("Accounting Department", cfo.id)
    tree_service.create_node("Yara Singh - Controller", accounting.id)
    tree_service.create_node("Zack Morgan - Accountant", accounting.id)

    fpa = tree_service.create_node("FP&A Department", cfo.id)
    tree_service.create_node("Anna Bell - FP&A Lead", fpa.id)
    tree_service.create_node("Brian Cox - Financial Analyst", fpa.id)

    # Marketing Organization under CMO
    print("  Building Marketing org...")
    digital = tree_service.create_node("Digital Marketing", cmo.id)
    tree_service.create_node("Claire Hunt - Digital Marketing Manager", digital.id)
    tree_service.create_node("Derek Fox - SEO Specialist", digital.id)
    tree_service.create_node("Ella Moore - Content Marketer", digital.id)

    brand = tree_service.create_node("Brand & Communications", cmo.id)
    tree_service.create_node("Felix Stone - Brand Manager", brand.id)
    tree_service.create_node("Gina Ross - PR Manager", brand.id)

    # Operations under COO
    print("  Building Operations org...")
    customer_success = tree_service.create_node("Customer Success", coo.id)
    tree_service.create_node("Hannah Lake - CS Manager", customer_success.id)
    tree_service.create_node("Ian Cross - CS Lead", customer_success.id)

    sales = tree_service.create_node("Sales Department", coo.id)
    tree_service.create_node("Julia Reed - VP Sales", sales.id)
    tree_service.create_node("Kevin Park - Enterprise Sales", sales.id)
    tree_service.create_node("Laura Chen - SMB Sales", sales.id)

    # HR under CHRO
    print("  Building HR org...")
    recruiting = tree_service.create_node("Recruiting", chro.id)
    tree_service.create_node("Mike Flynn - Recruiting Manager", recruiting.id)
    tree_service.create_node("Nina Bell - Technical Recruiter", recruiting.id)

    people_ops = tree_service.create_node("People Operations", chro.id)
    tree_service.create_node("Oscar Wade - People Ops Manager", people_ops.id)

    print("✓ TechCorp structure created")


def create_retail_company() -> None:
    """Create a retail company structure."""
    print("\n🏪 Creating RetailCo organizational structure...")

    ceo = tree_service.create_node("RetailCo - John Retail (CEO)", None)

    # Store Operations
    ops = tree_service.create_node("Store Operations", ceo.id)
    region_west = tree_service.create_node("West Region", ops.id)
    tree_service.create_node("San Francisco Store", region_west.id)
    tree_service.create_node("Los Angeles Store", region_west.id)
    tree_service.create_node("Seattle Store", region_west.id)

    region_east = tree_service.create_node("East Region", ops.id)
    tree_service.create_node("New York Store", region_east.id)
    tree_service.create_node("Boston Store", region_east.id)

    # Supply Chain
    supply_chain = tree_service.create_node("Supply Chain", ceo.id)
    tree_service.create_node("Procurement Team", supply_chain.id)
    tree_service.create_node("Logistics Team", supply_chain.id)
    tree_service.create_node("Warehouse Operations", supply_chain.id)

    print("✓ RetailCo structure created")


def create_educational_hierarchy() -> None:
    """Create an educational institution structure."""
    print("\n🎓 Creating University organizational structure...")

    university = tree_service.create_node("State University", None)

    # Academic Affairs
    academic = tree_service.create_node("Academic Affairs", university.id)

    # College of Engineering
    eng_college = tree_service.create_node("College of Engineering", academic.id)
    cs_dept = tree_service.create_node("Computer Science Department", eng_college.id)
    tree_service.create_node("Algorithms Course", cs_dept.id)
    tree_service.create_node("Databases Course", cs_dept.id)
    tree_service.create_node("AI/ML Course", cs_dept.id)

    ee_dept = tree_service.create_node("Electrical Engineering Department", eng_college.id)
    tree_service.create_node("Circuits Course", ee_dept.id)
    tree_service.create_node("Signals Course", ee_dept.id)

    # College of Arts
    arts_college = tree_service.create_node("College of Arts & Sciences", academic.id)
    math_dept = tree_service.create_node("Mathematics Department", arts_college.id)
    tree_service.create_node("Calculus Course", math_dept.id)
    tree_service.create_node("Linear Algebra Course", math_dept.id)

    physics_dept = tree_service.create_node("Physics Department", arts_college.id)
    tree_service.create_node("Quantum Mechanics Course", physics_dept.id)

    # Student Affairs
    student_affairs = tree_service.create_node("Student Affairs", university.id)
    tree_service.create_node("Housing & Residence Life", student_affairs.id)
    tree_service.create_node("Career Services", student_affairs.id)
    tree_service.create_node("Student Activities", student_affairs.id)

    print("✓ University structure created")


def create_filesystem_example() -> None:
    """Create a file system-like structure."""
    print("\n📁 Creating file system structure...")

    root = tree_service.create_node("root (/)", None)

    # /home
    home = tree_service.create_node("home", root.id)
    user1 = tree_service.create_node("alice", home.id)
    tree_service.create_node("documents", user1.id)
    tree_service.create_node("downloads", user1.id)
    tree_service.create_node("projects", user1.id)

    user2 = tree_service.create_node("bob", home.id)
    tree_service.create_node("documents", user2.id)
    tree_service.create_node("music", user2.id)

    # /etc
    etc = tree_service.create_node("etc", root.id)
    tree_service.create_node("nginx", etc.id)
    tree_service.create_node("ssh", etc.id)
    tree_service.create_node("systemd", etc.id)

    # /var
    var = tree_service.create_node("var", root.id)
    log = tree_service.create_node("log", var.id)
    tree_service.create_node("nginx", log.id)
    tree_service.create_node("syslog", log.id)

    print("✓ File system structure created")


def create_product_categories() -> None:
    """Create e-commerce product categories."""
    print("\n🛍️  Creating product category structure...")

    electronics = tree_service.create_node("Electronics", None)

    # Computers
    computers = tree_service.create_node("Computers & Tablets", electronics.id)
    laptops = tree_service.create_node("Laptops", computers.id)
    tree_service.create_node("Gaming Laptops", laptops.id)
    tree_service.create_node("Business Laptops", laptops.id)
    tree_service.create_node("Ultrabooks", laptops.id)

    desktops = tree_service.create_node("Desktop Computers", computers.id)
    tree_service.create_node("Gaming PCs", desktops.id)
    tree_service.create_node("Workstations", desktops.id)

    tablets = tree_service.create_node("Tablets", computers.id)
    tree_service.create_node("iPad", tablets.id)
    tree_service.create_node("Android Tablets", tablets.id)

    # Mobile Devices
    mobile = tree_service.create_node("Mobile Devices", electronics.id)
    smartphones = tree_service.create_node("Smartphones", mobile.id)
    tree_service.create_node("iPhone", smartphones.id)
    tree_service.create_node("Samsung Galaxy", smartphones.id)
    tree_service.create_node("Google Pixel", smartphones.id)

    accessories = tree_service.create_node("Accessories", mobile.id)
    tree_service.create_node("Phone Cases", accessories.id)
    tree_service.create_node("Screen Protectors", accessories.id)
    tree_service.create_node("Chargers & Cables", accessories.id)

    # Audio
    audio = tree_service.create_node("Audio", electronics.id)
    headphones = tree_service.create_node("Headphones", audio.id)
    tree_service.create_node("Over-Ear Headphones", headphones.id)
    tree_service.create_node("In-Ear Headphones", headphones.id)
    tree_service.create_node("True Wireless Earbuds", headphones.id)

    speakers = tree_service.create_node("Speakers", audio.id)
    tree_service.create_node("Bluetooth Speakers", speakers.id)
    tree_service.create_node("Smart Speakers", speakers.id)

    print("✓ Product categories created")


def print_statistics() -> None:
    """Print statistics about the created data."""
    print("\n" + "="*60)
    print("📈 DATABASE STATISTICS")
    print("="*60)

    trees = tree_service.list_trees()
    print(f"\nTotal number of root nodes (trees): {len(trees)}")

    total_nodes = 0
    max_depth = 0

    def count_nodes_and_depth(node, depth=0):
        nonlocal total_nodes, max_depth
        total_nodes += 1
        max_depth = max(max_depth, depth)
        for child in node.children:
            count_nodes_and_depth(child, depth + 1)

    for i, tree in enumerate(trees, 1):
        tree_nodes = 0
        tree_depth = 0

        def count_tree(node, depth=0):
            nonlocal tree_nodes, tree_depth
            tree_nodes += 1
            tree_depth = max(tree_depth, depth)
            for child in node.children:
                count_tree(child, depth + 1)

        count_tree(tree)
        print(f"\nTree {i}: {tree.label}")
        print(f"  - Total nodes: {tree_nodes}")
        print(f"  - Max depth: {tree_depth}")
        print(f"  - Direct children: {len(tree.children)}")

    count_nodes_and_depth(trees[0] if trees else None)
    print(f"\n{'='*60}")
    print(f"TOTAL NODES IN DATABASE: {total_nodes}")
    print(f"MAXIMUM TREE DEPTH: {max_depth}")
    print(f"{'='*60}\n")


def main() -> None:
    """Main function to populate sample data."""
    print("\n" + "="*60)
    print("🌲 TREE API - SAMPLE DATA POPULATION SCRIPT")
    print("="*60)

    # Initialize database
    db.initialize()

    # Clear existing data
    clear_database()

    # Create various organizational structures
    create_tech_company()
    create_retail_company()
    create_educational_hierarchy()
    create_filesystem_example()
    create_product_categories()

    # Print statistics
    print_statistics()

    print("✅ Sample data population complete!")
    print("\nYou can now test the API with:")
    print("  curl http://127.0.0.1:9000/api/tree | python -m json.tool")
    print()


if __name__ == "__main__":
    main()

