# API Testing Guide

Quick reference for testing the Tree API with sample data and various scenarios.

## Prerequisites

1. Start the server:
```bash
python -m src.server
# Or on custom port:
TREE_API_PORT=9000 python -m src.server
```

2. (Optional) Populate sample data:
```bash
python -m scripts.populate_sample_data
```

---

## Basic API Tests

### 1. Get All Trees (Empty Database)
```bash
curl http://127.0.0.1:9000/api/tree
```
**Expected Response:**
```json
[]
```

### 2. Create Root Node
```bash
curl -X POST http://127.0.0.1:9000/api/tree \
  -H 'Content-Type: application/json' \
  -d '{"label": "My Root"}'
```
**Expected Response:**
```json
{
  "id": 1,
  "label": "My Root",
  "children": []
}
```

### 3. Create Child Node
```bash
curl -X POST http://127.0.0.1:9000/api/tree \
  -H 'Content-Type: application/json' \
  -d '{"label": "Child Node", "parent_id": 1}'
```
**Expected Response:**
```json
{
  "id": 2,
  "label": "Child Node",
  "children": []
}
```

### 4. Get Hierarchical Tree
```bash
curl http://127.0.0.1:9000/api/tree | python -m json.tool
```
**Expected Response:**
```json
[
  {
    "id": 1,
    "label": "My Root",
    "children": [
      {
        "id": 2,
        "label": "Child Node",
        "children": []
      }
    ]
  }
]
```

---

## Error Handling Tests

### 5. Missing Label (400 Bad Request)
```bash
curl -X POST http://127.0.0.1:9000/api/tree \
  -H 'Content-Type: application/json' \
  -d '{"label": "   "}'
```
**Expected Response:**
```json
{
  "error": "label is required",
  "status": 400
}
```

### 6. Invalid Parent ID (404 Not Found)
```bash
curl -X POST http://127.0.0.1:9000/api/tree \
  -H 'Content-Type: application/json' \
  -d '{"label": "Orphan", "parent_id": 99999}'
```
**Expected Response:**
```json
{
  "error": "Parent node 99999 does not exist",
  "status": 404
}
```

### 7. Invalid JSON (400 Bad Request)
```bash
curl -X POST http://127.0.0.1:9000/api/tree \
  -H 'Content-Type: application/json' \
  -d '{invalid json}'
```
**Expected Response:**
```json
{
  "error": "Request body must be valid JSON",
  "status": 400
}
```

### 8. Missing Content-Type Header
```bash
curl -X POST http://127.0.0.1:9000/api/tree \
  -d '{"label": "test"}'
```
**Expected Response:**
```json
{
  "error": "Request body must be valid JSON",
  "status": 400
}
```

### 9. Unknown Endpoint (404 Not Found)
```bash
curl http://127.0.0.1:9000/api/unknown
```
**Expected Response:**
```
404 Not Found error page
```

---

## Complex Scenarios

### 10. Build Organization Chart
```bash
# CEO
curl -X POST http://127.0.0.1:9000/api/tree \
  -H 'Content-Type: application/json' \
  -d '{"label": "CEO"}' | python -m json.tool

# CTO (reports to CEO, id=1)
curl -X POST http://127.0.0.1:9000/api/tree \
  -H 'Content-Type: application/json' \
  -d '{"label": "CTO", "parent_id": 1}' | python -m json.tool

# Engineering Team (reports to CTO, id=2)
curl -X POST http://127.0.0.1:9000/api/tree \
  -H 'Content-Type: application/json' \
  -d '{"label": "Engineering", "parent_id": 2}' | python -m json.tool

# View the structure
curl http://127.0.0.1:9000/api/tree | python -m json.tool
```

### 11. Multiple Independent Trees (Forest)
```bash
# Tree 1
curl -X POST http://127.0.0.1:9000/api/tree \
  -H 'Content-Type: application/json' \
  -d '{"label": "Company A"}'

# Tree 2
curl -X POST http://127.0.0.1:9000/api/tree \
  -H 'Content-Type: application/json' \
  -d '{"label": "Company B"}'

# Tree 3
curl -X POST http://127.0.0.1:9000/api/tree \
  -H 'Content-Type: application/json' \
  -d '{"label": "Company C"}'

# View all trees
curl http://127.0.0.1:9000/api/tree | python -m json.tool
```

### 12. Deep Nesting
```bash
# Create a 5-level hierarchy
IDS=(0 0 0 0 0)

# Level 1
ID=$(curl -s -X POST http://127.0.0.1:9000/api/tree \
  -H 'Content-Type: application/json' \
  -d '{"label": "Level 1"}' | python -c "import json, sys; print(json.load(sys.stdin)['id'])")
IDS[1]=$ID

# Level 2
ID=$(curl -s -X POST http://127.0.0.1:9000/api/tree \
  -H 'Content-Type: application/json' \
  -d "{\"label\": \"Level 2\", \"parent_id\": ${IDS[1]}}" | python -c "import json, sys; print(json.load(sys.stdin)['id'])")
IDS[2]=$ID

# Level 3
ID=$(curl -s -X POST http://127.0.0.1:9000/api/tree \
  -H 'Content-Type: application/json' \
  -d "{\"label\": \"Level 3\", \"parent_id\": ${IDS[2]}}" | python -c "import json, sys; print(json.load(sys.stdin)['id'])")
IDS[3]=$ID

# Level 4
ID=$(curl -s -X POST http://127.0.0.1:9000/api/tree \
  -H 'Content-Type: application/json' \
  -d "{\"label\": \"Level 4\", \"parent_id\": ${IDS[3]}}" | python -c "import json, sys; print(json.load(sys.stdin)['id'])")
IDS[4]=$ID

# Level 5
curl -X POST http://127.0.0.1:9000/api/tree \
  -H 'Content-Type: application/json' \
  -d "{\"label\": \"Level 5\", \"parent_id\": ${IDS[4]}}" | python -m json.tool

# View the deep tree
curl http://127.0.0.1:9000/api/tree | python -m json.tool
```

### 13. Many Siblings
```bash
# Create parent
PARENT_ID=$(curl -s -X POST http://127.0.0.1:9000/api/tree \
  -H 'Content-Type: application/json' \
  -d '{"label": "Parent"}' | python -c "import json, sys; print(json.load(sys.stdin)['id'])")

# Create 10 children
for i in {1..10}; do
  curl -s -X POST http://127.0.0.1:9000/api/tree \
    -H 'Content-Type: application/json' \
    -d "{\"label\": \"Child $i\", \"parent_id\": $PARENT_ID}" > /dev/null
  echo "Created child $i"
done

# View the wide tree
curl http://127.0.0.1:9000/api/tree | python -m json.tool
```

### 14. Unicode and Special Characters
```bash
# Japanese
curl -X POST http://127.0.0.1:9000/api/tree \
  -H 'Content-Type: application/json' \
  -d '{"label": "日本語"}' | python -m json.tool

# Emoji
curl -X POST http://127.0.0.1:9000/api/tree \
  -H 'Content-Type: application/json' \
  -d '{"label": "🌲 Tree Node 🎄"}' | python -m json.tool

# Special characters
curl -X POST http://127.0.0.1:9000/api/tree \
  -H 'Content-Type: application/json' \
  -d '{"label": "Node@123#!$%"}' | python -m json.tool

# View all
curl http://127.0.0.1:9000/api/tree | python -m json.tool
```

---

## Sample Data Tests

### 15. Query TechCorp Organization
```bash
# Get all trees
curl -s http://127.0.0.1:9000/api/tree | python -m json.tool > output.json

# Count total nodes
curl -s http://127.0.0.1:9000/api/tree | \
  python -c "import json, sys; data = json.load(sys.stdin); 
def count(nodes): return sum(1 + count(n['children']) for n in nodes)
print(f'Total nodes: {count(data)}')"

# Get tree names
curl -s http://127.0.0.1:9000/api/tree | \
  python -c "import json, sys; data = json.load(sys.stdin); 
print('\\n'.join(f'{i+1}. {tree[\"label\"]}' for i, tree in enumerate(data)))"

# Get TechCorp structure (first tree)
curl -s http://127.0.0.1:9000/api/tree | \
  python -c "import json, sys; data = json.load(sys.stdin); 
print(json.dumps(data[0], indent=2))" | head -100
```

### 16. Query Product Categories
```bash
# Get Electronics category (5th tree after populating sample data)
curl -s http://127.0.0.1:9000/api/tree | \
  python -c "import json, sys; data = json.load(sys.stdin); 
print(json.dumps(data[4] if len(data) > 4 else {}, indent=2))"
```

### 17. Search for Nodes by Label
```bash
# Get all nodes and search (requires jq or python)
curl -s http://127.0.0.1:9000/api/tree | \
  python -c "
import json, sys
data = json.load(sys.stdin)

def search(nodes, term):
    results = []
    for node in nodes:
        if term.lower() in node['label'].lower():
            results.append(node['label'])
        results.extend(search(node['children'], term))
    return results

term = 'engineer'
results = search(data, term)
print(f'Found {len(results)} nodes matching \"{term}\":')
for r in results: print(f'  - {r}')
"
```

---

## Performance Tests

### 18. Create 100 Nodes Quickly
```bash
# Create root
ROOT_ID=$(curl -s -X POST http://127.0.0.1:9000/api/tree \
  -H 'Content-Type: application/json' \
  -d '{"label": "Root"}' | python -c "import json, sys; print(json.load(sys.stdin)['id'])")

# Create 100 children
echo "Creating 100 nodes..."
time for i in {1..100}; do
  curl -s -X POST http://127.0.0.1:9000/api/tree \
    -H 'Content-Type: application/json' \
    -d "{\"label\": \"Node$i\", \"parent_id\": $ROOT_ID}" > /dev/null
done

echo "Retrieving tree..."
time curl -s http://127.0.0.1:9000/api/tree > /dev/null
```

### 19. Measure Response Time
```bash
# GET request timing
time curl -s http://127.0.0.1:9000/api/tree > /dev/null

# POST request timing
time curl -s -X POST http://127.0.0.1:9000/api/tree \
  -H 'Content-Type: application/json' \
  -d '{"label": "Test"}' > /dev/null
```

---

## Useful Helper Commands

### Count Nodes
```bash
curl -s http://127.0.0.1:9000/api/tree | \
  python -c "import json, sys; data = json.load(sys.stdin); 
def count(nodes): return sum(1 + count(n['children']) for n in nodes)
print(count(data))"
```

### Get Max Depth
```bash
curl -s http://127.0.0.1:9000/api/tree | \
  python -c "import json, sys; data = json.load(sys.stdin); 
def depth(nodes, d=0): return max([d] + [depth(n['children'], d+1) for n in nodes if n['children']])
print(depth(data))"
```

### Pretty Print Tree Structure
```bash
curl -s http://127.0.0.1:9000/api/tree | \
  python -c "
import json, sys
data = json.load(sys.stdin)

def print_tree(nodes, indent=0):
    for node in nodes:
        print('  ' * indent + f'├─ {node[\"label\"]} (id={node[\"id\"]})')
        print_tree(node['children'], indent + 1)

print_tree(data)
"
```

### Export to File
```bash
# Export as JSON
curl -s http://127.0.0.1:9000/api/tree > trees.json

# Export pretty-printed
curl -s http://127.0.0.1:9000/api/tree | python -m json.tool > trees_pretty.json
```

---

## Testing Checklist

- [ ] Server starts successfully
- [ ] GET empty database returns `[]`
- [ ] POST creates root node (201 status)
- [ ] POST creates child node (201 status)
- [ ] GET returns nested structure
- [ ] Empty label returns 400 error
- [ ] Invalid parent_id returns 404 error
- [ ] Invalid JSON returns 400 error
- [ ] Unknown endpoint returns 404
- [ ] Unicode characters work
- [ ] Special characters work
- [ ] Multiple trees (forest) work
- [ ] Deep nesting works (10+ levels)
- [ ] Wide trees work (50+ children)
- [ ] Large datasets work (100+ nodes)
- [ ] Data persists after server restart

---

## Troubleshooting

### Server not responding
```bash
# Check if server is running
curl -v http://127.0.0.1:9000/api/tree

# Check server logs
# (Look at terminal where server is running)
```

### Port already in use
```bash
# Use different port
TREE_API_PORT=8080 python -m src.server
```

### Database locked
```bash
# Stop server, then restart
# SQLite locks are released on process exit
```

### Clear all data
```bash
# Stop server
# Delete database
rm data/trees.db
# Restart server (will recreate empty database)
```

---

## Next Steps

1. ✅ Run all test scenarios above
2. ✅ Populate sample data: `python -m scripts.populate_sample_data`
3. ✅ Run automated tests: `python -m unittest discover -s tests -v`
4. ✅ Review test coverage in `TEST_CASES_SUMMARY.md`
5. ✅ Check architecture documentation in `README.md`

