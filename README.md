# Tree API Server

A production-ready HTTP API for managing hierarchical tree structures, built entirely with Python's standard library and SQLite for persistence.

## Table of Contents

- [Overview](#overview)
- [Architecture & Design](#architecture--design)
- [Project Structure](#project-structure)
- [How It Works](#how-it-works)
- [Features](#features)
- [Requirements](#requirements)
- [Installation & Setup](#installation--setup)
- [Running the Server](#running-the-server)
- [API Documentation](#api-documentation)
- [Testing](#testing)
- [Design Decisions](#design-decisions)
- [Further Improvements](#further-improvements)

## Overview

This project implements a RESTful API for creating and managing tree data structures. It supports:
- Creating root nodes
- Attaching child nodes to existing parents
- Retrieving the entire forest (multiple trees) as nested JSON
- Persistent storage using SQLite
- Proper error handling and HTTP status codes

**Key Highlight**: Built using only Python's standard library - no external dependencies required!

## Architecture & Design

### High-Level Architecture

The application follows a **layered architecture** pattern with clear separation of concerns:

```
┌─────────────────────────────────────────────────────────────────┐
│                        CLIENT (curl, browser, app)               │
└────────────────────────────────┬────────────────────────────────┘
                                 │ HTTP Request
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                    HTTP LAYER (server.py)                        │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  ThreadingHTTPServer + TreeRequestHandler               │    │
│  │  • Route requests (GET/POST /api/tree)                  │    │
│  │  • Parse/serialize JSON                                 │    │
│  │  • HTTP status codes & error handling                   │    │
│  └─────────────────────────────────────────────────────────┘    │
└────────────────────────────────┬────────────────────────────────┘
                                 │ Function Call
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                SERVICE LAYER (tree_service.py)                   │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  Business Logic & Validation                            │    │
│  │  • create_node(label, parent_id)                        │    │
│  │  • list_trees() → builds forest structure               │    │
│  │  • Input validation (empty labels, etc.)                │    │
│  │  • Custom exceptions (ValidationError, NodeNotFound)    │    │
│  └─────────────────────────────────────────────────────────┘    │
└────────────────────────────────┬────────────────────────────────┘
                                 │ SQL Queries
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                    DATA LAYER (db.py)                            │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  Database Operations                                    │    │
│  │  • initialize() → creates schema                        │    │
│  │  • get_connection() → context manager                   │    │
│  │  • Connection pooling & cleanup                         │    │
│  └─────────────────────────────────────────────────────────┘    │
└────────────────────────────────┬────────────────────────────────┘
                                 │ Read/Write
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                  PERSISTENCE LAYER                               │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  SQLite Database (data/trees.db)                        │    │
│  │  ┌─────────────────────────────────────────────┐        │    │
│  │  │  nodes table                                │        │    │
│  │  │  • id (PK, AUTOINCREMENT)                   │        │    │
│  │  │  • label (TEXT, NOT NULL)                   │        │    │
│  │  │  • parent_id (FK → nodes.id, nullable)      │        │    │
│  │  └─────────────────────────────────────────────┘        │    │
│  └─────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘

                    ┌───────────────────────┐
                    │   config.py           │
                    │  • Environment vars   │
                    │  • DB_PATH, HOST, PORT│
                    │  • Path resolution    │
                    └───────────────────────┘
                             │
                             └───► Used by all layers
```

### Component Interaction Diagram

```
┌──────────────┐
│   Client     │
└──────┬───────┘
       │
       │ 1. HTTP Request
       ▼
┌──────────────────────────────────────────────────────────────┐
│  TreeRequestHandler                                          │
│  ┌────────────────────────────────────────────────────┐     │
│  │  2. do_GET() or do_POST()                          │     │
│  │     │                                               │     │
│  │     ├─► handle_list_trees()                        │     │
│  │     │   │                                           │     │
│  │     │   └─► tree_service.list_trees()              │     │
│  │     │       │                                       │     │
│  │     │       ├─► db.get_connection()                │     │
│  │     │       ├─► SELECT * FROM nodes                │     │
│  │     │       └─► _rows_to_forest()                  │     │
│  │     │           (Build tree hierarchy)             │     │
│  │     │                                               │     │
│  │     └─► handle_create_node()                       │     │
│  │         │                                           │     │
│  │         ├─► _read_json_body()                      │     │
│  │         ├─► validate payload                       │     │
│  │         └─► tree_service.create_node()             │     │
│  │             │                                       │     │
│  │             ├─► Validate label                     │     │
│  │             ├─► Check parent exists (if needed)    │     │
│  │             ├─► db.get_connection()                │     │
│  │             ├─► INSERT INTO nodes                  │     │
│  │             └─► Return TreeNode                    │     │
│  │                                                     │     │
│  │  3. _send_json() or _send_error_json()            │     │
│  └────────────────────────────────────────────────────┘     │
└──────┬───────────────────────────────────────────────────────┘
       │
       │ 4. HTTP Response (JSON)
       ▼
┌──────────────┐
│   Client     │
└──────────────┘
```

### Layer Responsibilities

1. **HTTP Layer** (`server.py`):
   - Handles HTTP requests and responses
   - Routes requests to appropriate handlers
   - Serializes/deserializes JSON
   - Manages HTTP status codes
   - Error response formatting

2. **Service Layer** (`tree_service.py`):
   - Contains business logic
   - Performs input validation
   - Builds tree structures from flat data
   - Handles domain-specific errors
   - Data transformation (rows → TreeNode objects)

3. **Data Layer** (`db.py`):
   - Manages database connections
   - Initializes database schema
   - Provides connection context managers
   - Ensures proper resource cleanup

4. **Configuration** (`config.py`):
   - Centralizes all configuration
   - Handles environment variables
   - Computes paths and defaults
   - No hardcoded values

## Project Structure

```
assesment/
├── data/
│   └── trees.db              # SQLite database (created on first run)
├── src/
│   ├── __init__.py           # Package marker
│   ├── config.py             # Configuration and environment variables
│   ├── db.py                 # Database initialization and connection management
│   ├── server.py             # HTTP server and request handlers
│   └── tree_service.py       # Business logic for tree operations
├── tests/
│   ├── __init__.py           # Test package marker
│   ├── test_server.py        # HTTP API integration tests
│   └── test_tree_service.py  # Service layer unit tests
├── requirements.txt          # Python dependencies (empty - stdlib only!)
└── README.md                 # This file
```

## How It Works

### 1. Server Initialization

When you run `python -m src.server`:

1. **Configuration is loaded** from `config.py`:
   - Reads environment variables or uses defaults
   - Sets up database path, host, and port

2. **Database is initialized** via `db.initialize()`:
   - Creates `data/` directory if missing
   - Creates `nodes` table if it doesn't exist
   - Schema: `id`, `label`, `parent_id` (self-referencing foreign key)

3. **HTTP server starts** on the configured host and port:
   - Uses Python's `ThreadingHTTPServer` for concurrent request handling
   - Registers `TreeRequestHandler` for request processing

### 2. Request Flow Diagrams

#### Creating a Node (POST /api/tree)

```
┌─────────┐
│ Client  │
└────┬────┘
     │
     │  POST /api/tree
     │  Content-Type: application/json
     │  Body: {"label": "child", "parent_id": 1}
     ▼
┌────────────────────────────────────────────────────────┐
│  server.py :: TreeRequestHandler                       │
├────────────────────────────────────────────────────────┤
│  1. do_POST()                                          │
│     └─► Check path == "/api/tree"                     │
│         └─► Call handle_create_node()                 │
│                                                        │
│  2. handle_create_node()                              │
│     ├─► Read Content-Length header                    │
│     ├─► Read request body                             │
│     ├─► Parse JSON: json.loads()                      │
│     │   └─► Extract: label, parent_id                 │
│     │                                                  │
│     │   ┌─────── Validation ──────┐                   │
│     │   │ parent_id not None?     │                   │
│     │   │   → Convert to int      │                   │
│     │   │   → If fails: 400 error │                   │
│     │   └─────────────────────────┘                   │
│     │                                                  │
│     └─► Call tree_service.create_node(label, parent_id)
└────┬───────────────────────────────────────────────────┘
     │
     ▼
┌────────────────────────────────────────────────────────┐
│  tree_service.py                                       │
├────────────────────────────────────────────────────────┤
│  3. create_node(label, parent_id)                     │
│     │                                                  │
│     ├─► Validate label                                │
│     │   label = (label or "").strip()                 │
│     │   └─► if not label:                             │
│     │       raise ValidationError("label is required")│
│     │                                                  │
│     ├─► Get database connection                       │
│     │   with db.get_connection() as conn:             │
│     │                                                  │
│     ├─► If parent_id provided:                        │
│     │   │   SELECT id FROM nodes WHERE id = ?         │
│     │   │   └─► If not found:                         │
│     │   │       raise NodeNotFound(...)               │
│     │                                                  │
│     ├─► Insert into database                          │
│     │   INSERT INTO nodes (label, parent_id)          │
│     │   VALUES (?, ?)                                 │
│     │   └─► Get lastrowid → node_id                   │
│     │                                                  │
│     ├─► Commit transaction                            │
│     │   conn.commit()                                 │
│     │                                                  │
│     └─► Return TreeNode(id, label, parent_id)         │
└────┬───────────────────────────────────────────────────┘
     │
     ▼
┌────────────────────────────────────────────────────────┐
│  db.py                                                 │
├────────────────────────────────────────────────────────┤
│  4. SQLite Operations                                 │
│     ├─► Open connection to data/trees.db              │
│     ├─► Execute SQL queries                           │
│     ├─► Return results                                │
│     └─► Close connection (context manager)            │
└────┬───────────────────────────────────────────────────┘
     │
     ▼
┌────────────────────────────────────────────────────────┐
│  server.py :: TreeRequestHandler (continued)          │
├────────────────────────────────────────────────────────┤
│  5. Response Handling                                 │
│     │                                                  │
│     ├─► Success Path:                                 │
│     │   ├─► node.to_dict() → {"id": 2, "label":...}  │
│     │   ├─► json.dumps() → serialize                  │
│     │   ├─► Set status: 201 CREATED                   │
│     │   ├─► Set header: Content-Type: application/json│
│     │   └─► Write response body                       │
│     │                                                  │
│     └─► Error Paths:                                  │
│         ├─► ValidationError → 400 BAD REQUEST         │
│         ├─► NodeNotFound → 404 NOT FOUND              │
│         └─► Exception → 500 INTERNAL SERVER ERROR     │
└────┬───────────────────────────────────────────────────┘
     │
     │  HTTP/1.1 201 Created
     │  Content-Type: application/json
     │  Body: {"id": 2, "label": "child", "children": []}
     ▼
┌─────────┐
│ Client  │
└─────────┘
```

#### Retrieving Trees (GET /api/tree)

```
┌─────────┐
│ Client  │
└────┬────┘
     │
     │  GET /api/tree
     ▼
┌────────────────────────────────────────────────────────┐
│  server.py :: TreeRequestHandler                       │
├────────────────────────────────────────────────────────┤
│  1. do_GET()                                          │
│     └─► Check path == "/api/tree"                     │
│         └─► Call handle_list_trees()                  │
│                                                        │
│  2. handle_list_trees()                               │
│     └─► Call tree_service.list_trees()                │
└────┬───────────────────────────────────────────────────┘
     │
     ▼
┌────────────────────────────────────────────────────────┐
│  tree_service.py                                       │
├────────────────────────────────────────────────────────┤
│  3. list_trees()                                      │
│     │                                                  │
│     ├─► Get database connection                       │
│     │   with db.get_connection() as conn:             │
│     │                                                  │
│     ├─► Query all nodes                               │
│     │   SELECT id, label, parent_id                   │
│     │   FROM nodes                                    │
│     │   ORDER BY id                                   │
│     │   └─► Returns: [Row(1,'root',None),            │
│     │                 Row(2,'child',1), ...]          │
│     │                                                  │
│     └─► Call _rows_to_forest(rows)                    │
└────┬───────────────────────────────────────────────────┘
     │
     ▼
┌────────────────────────────────────────────────────────┐
│  tree_service.py :: _rows_to_forest()                 │
├────────────────────────────────────────────────────────┤
│  4. Build Tree Hierarchy                              │
│     │                                                  │
│     ├─► Phase 1: Create node objects                  │
│     │   nodes = {}                                    │
│     │   for row in rows:                              │
│     │     nodes[row.id] = TreeNode(                   │
│     │       id=row.id,                                │
│     │       label=row.label,                          │
│     │       parent_id=row.parent_id                   │
│     │     )                                            │
│     │   Result: {1: TreeNode(...), 2: TreeNode(...)} │
│     │                                                  │
│     ├─► Phase 2: Link children to parents             │
│     │   roots = []                                    │
│     │   for node in nodes.values():                   │
│     │     if node.parent_id is None:                  │
│     │       roots.append(node)  # Root node          │
│     │     else:                                       │
│     │       parent = nodes.get(node.parent_id)        │
│     │       if parent:                                │
│     │         parent.children.append(node)            │
│     │       else:                                     │
│     │         roots.append(node)  # Orphaned node    │
│     │                                                  │
│     ├─► Phase 3: Sort for deterministic output        │
│     │   roots.sort(key=lambda n: n.id)               │
│     │   for each root:                                │
│     │     sort_children(root)  # Recursive sort      │
│     │                                                  │
│     └─► Return [root1, root2, ...]                    │
│                                                        │
│   Example Result:                                     │
│   [TreeNode(id=1, label='root', children=[           │
│      TreeNode(id=2, label='child', children=[])       │
│   ])]                                                 │
└────┬───────────────────────────────────────────────────┘
     │
     ▼
┌────────────────────────────────────────────────────────┐
│  server.py :: TreeRequestHandler (continued)          │
├────────────────────────────────────────────────────────┤
│  5. Serialize Response                                │
│     │                                                  │
│     ├─► trees = [node.to_dict() for node in ...]     │
│     │   │                                              │
│     │   └─► Recursive serialization via TreeNode.to_dict()
│     │       def to_dict():                            │
│     │         return {                                │
│     │           "id": self.id,                        │
│     │           "label": self.label,                  │
│     │           "children": [                         │
│     │             child.to_dict() for child in ...    │
│     │           ]                                     │
│     │         }                                       │
│     │                                                  │
│     ├─► json.dumps(trees)                             │
│     ├─► Set status: 200 OK                            │
│     ├─► Set header: Content-Type: application/json    │
│     └─► Write response body                           │
└────┬───────────────────────────────────────────────────┘
     │
     │  HTTP/1.1 200 OK
     │  Content-Type: application/json
     │  Body: [{"id":1,"label":"root","children":[...]}]
     ▼
┌─────────┐
│ Client  │
└─────────┘
```

### 3. Data Transformation Flow

This diagram shows how data is transformed at each layer:

```
┌─────────────────────────────────────────────────────────────────┐
│  CLIENT REQUEST                                                  │
├─────────────────────────────────────────────────────────────────┤
│  Raw HTTP Request:                                              │
│  POST /api/tree HTTP/1.1                                        │
│  Content-Type: application/json                                 │
│  Content-Length: 35                                             │
│                                                                 │
│  {"label": "child", "parent_id": 1}                             │
└────────────────────────────────┬────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│  HTTP LAYER                                                      │
├─────────────────────────────────────────────────────────────────┤
│  Python dict:                                                   │
│  {                                                              │
│    "label": "child",                                            │
│    "parent_id": 1                                               │
│  }                                                              │
└────────────────────────────────┬────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│  SERVICE LAYER                                                   │
├─────────────────────────────────────────────────────────────────┤
│  Function parameters:                                           │
│  label: str = "child"                                           │
│  parent_id: int | None = 1                                      │
│                                                                 │
│  After validation:                                              │
│  label: str = "child" (trimmed, non-empty)                      │
│  parent_id: int = 1 (exists in database)                        │
└────────────────────────────────┬────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│  DATA LAYER                                                      │
├─────────────────────────────────────────────────────────────────┤
│  SQL Query:                                                     │
│  INSERT INTO nodes (label, parent_id) VALUES (?, ?)            │
│  Parameters: ("child", 1)                                       │
│                                                                 │
│  Result:                                                        │
│  cursor.lastrowid = 2                                           │
└────────────────────────────────┬────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│  DATABASE                                                        │
├─────────────────────────────────────────────────────────────────┤
│  Table: nodes                                                   │
│  ┌────┬────────┬───────────┐                                   │
│  │ id │ label  │ parent_id │                                   │
│  ├────┼────────┼───────────┤                                   │
│  │  1 │ root   │    NULL   │                                   │
│  │  2 │ child  │      1    │  ← NEW ROW                        │
│  └────┴────────┴───────────┘                                   │
└────────────────────────────────┬────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│  SERVICE LAYER                                                   │
├─────────────────────────────────────────────────────────────────┤
│  TreeNode object:                                               │
│  TreeNode(                                                      │
│    id=2,                                                        │
│    label="child",                                               │
│    parent_id=1,                                                 │
│    children=[]                                                  │
│  )                                                              │
└────────────────────────────────┬────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│  HTTP LAYER                                                      │
├─────────────────────────────────────────────────────────────────┤
│  Python dict (via .to_dict()):                                 │
│  {                                                              │
│    "id": 2,                                                     │
│    "label": "child",                                            │
│    "children": []                                               │
│  }                                                              │
│                                                                 │
│  JSON string (via json.dumps()):                               │
│  '{"id": 2, "label": "child", "children": []}'                 │
└────────────────────────────────┬────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│  CLIENT RESPONSE                                                 │
├─────────────────────────────────────────────────────────────────┤
│  HTTP/1.1 201 Created                                           │
│  Content-Type: application/json                                 │
│  Content-Length: 42                                             │
│                                                                 │
│  {"id": 2, "label": "child", "children": []}                    │
└─────────────────────────────────────────────────────────────────┘
```

### 4. Tree Construction Algorithm

The `_rows_to_forest()` function in `tree_service.py` converts a flat list of database rows into a hierarchical structure:

```python
# Algorithm steps:
1. Create a dictionary: node_id → TreeNode object
2. Iterate through nodes:
   - If parent_id is NULL → add to roots list
   - Otherwise → append to parent's children list
3. Sort roots and recursively sort children by ID
4. Return list of root nodes (each with nested children)
```

**Time Complexity**: **O(n)** where n = number of nodes

**Visual Example**:

```
Database (Flat):                      Memory (Hierarchical):
┌────┬────────┬───────────┐
│ id │ label  │ parent_id │           1: root
├────┼────────┼───────────┤           ├─► 2: child1
│  1 │ root   │   NULL    │           │   └─► 4: grandchild
│  2 │ child1 │     1     │   ───►    └─► 3: child2
│  3 │ child2 │     1     │
│  4 │ grandch│     2     │           5: another_root
│  5 │ another│   NULL    │           
└────┴────────┴───────────┘
    (Rows in DB)                    (TreeNode objects with .children)

Final JSON Output:
[
  {
    "id": 1,
    "label": "root",
    "children": [
      {
        "id": 2,
        "label": "child1",
        "children": [
          {"id": 4, "label": "grandchild", "children": []}
        ]
      },
      {"id": 3, "label": "child2", "children": []}
    ]
  },
  {
    "id": 5,
    "label": "another_root",
    "children": []
  }
]
```

## Features

- ✅ **RESTful API** with proper HTTP semantics
- ✅ **Persistent storage** - data survives server restarts
- ✅ **Hierarchical trees** - unlimited nesting depth
- ✅ **Multiple trees** - supports a forest of independent trees
- ✅ **Input validation** - proper error messages for invalid input
- ✅ **No external dependencies** - pure Python standard library
- ✅ **Concurrent requests** - ThreadingHTTPServer handles multiple clients
- ✅ **Type hints** - full type annotations for better code quality
- ✅ **Comprehensive tests** - unit and integration tests included
- ✅ **Configurable** - environment variables for all settings

## Requirements

- **Python 3.10+** (uses modern type hints and features)
- No third-party packages required!

## Installation & Setup

1. **Clone or download** the project

2. **(Optional) Create a virtual environment**:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **No dependencies to install** - the project uses only Python's standard library!

## Running the Server

### Basic Usage

```bash
python -m src.server
```

The server will start on `http://127.0.0.1:8000`

### Custom Configuration

Use environment variables to customize:

```bash
# Run on a different port
TREE_API_PORT=9000 python -m src.server

# Run on all interfaces
TREE_API_HOST=0.0.0.0 TREE_API_PORT=8080 python -m src.server

# Use a different database file
TREE_API_DB_PATH=/tmp/my_trees.db python -m src.server
```

### Available Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `TREE_API_DB_PATH` | Path to SQLite database file | `data/trees.db` |
| `TREE_API_HOST` | Host/interface to bind | `127.0.0.1` |
| `TREE_API_PORT` | Port for the HTTP server | `8000` |

## API Documentation

### Endpoints

#### `GET /api/tree`

**Description**: Retrieve all trees (forest) as nested JSON.

**Response**: `200 OK`

**Response Body**:
```json
[
  {
    "id": 1,
    "label": "root",
    "children": [
      {
        "id": 2,
        "label": "child",
        "children": []
      }
    ]
  }
]
```

**Example**:
```bash
curl http://127.0.0.1:8000/api/tree
```

---

#### `POST /api/tree`

**Description**: Create a new node, optionally attaching it to a parent.

**Request Headers**:
- `Content-Type: application/json`

**Request Body**:
```json
{
  "label": "string (required)",
  "parent_id": "integer (optional)"
}
```

**Response**: `201 Created`

**Response Body**:
```json
{
  "id": 1,
  "label": "node label",
  "children": []
}
```

**Examples**:

Create a root node:
```bash
curl -X POST http://127.0.0.1:8000/api/tree \
  -H 'Content-Type: application/json' \
  -d '{"label": "root"}'
```

Create a child node:
```bash
curl -X POST http://127.0.0.1:8000/api/tree \
  -H 'Content-Type: application/json' \
  -d '{"label": "child", "parent_id": 1}'
```

### Error Responses

#### `400 Bad Request`
- Empty or whitespace-only label
- Invalid JSON body
- Invalid parent_id type

**Example**:
```json
{
  "error": "label is required",
  "status": 400
}
```

#### `404 Not Found`
- Parent node doesn't exist
- Unknown endpoint

**Example**:
```json
{
  "error": "Parent node 999 does not exist",
  "status": 404
}
```

#### `500 Internal Server Error`
- Unexpected server errors

### Complete Usage Example

```bash
# 1. Create root node
curl -X POST http://127.0.0.1:8000/api/tree \
  -H 'Content-Type: application/json' \
  -d '{"label": "Company"}'
# Response: {"id": 1, "label": "Company", "children": []}

# 2. Create department
curl -X POST http://127.0.0.1:8000/api/tree \
  -H 'Content-Type: application/json' \
  -d '{"label": "Engineering", "parent_id": 1}'
# Response: {"id": 2, "label": "Engineering", "children": []}

# 3. Create team
curl -X POST http://127.0.0.1:8000/api/tree \
  -H 'Content-Type: application/json' \
  -d '{"label": "Backend", "parent_id": 2}'
# Response: {"id": 3, "label": "Backend", "children": []}

# 4. View the complete tree
curl http://127.0.0.1:8000/api/tree | python -m json.tool
```

**Result**:
```json
[
  {
    "id": 1,
    "label": "Company",
    "children": [
      {
        "id": 2,
        "label": "Engineering",
        "children": [
          {
            "id": 3,
            "label": "Backend",
            "children": []
          }
        ]
      }
    ]
  }
]
```

## Testing

### Run All Tests

```bash
python -m unittest discover -s tests -v
```

### Run Specific Test File

```bash
# Test service layer
python -m unittest tests.test_tree_service

# Test HTTP server
python -m unittest tests.test_server
```

### Test Coverage

The test suite includes:

**Service Layer Tests** (`test_tree_service.py`):
- ✅ Creating root nodes
- ✅ Creating child nodes
- ✅ Validating required fields
- ✅ Handling missing parent references
- ✅ Building nested tree structures

**HTTP API Tests** (`test_server.py`):
- ✅ GET requests for empty forest
- ✅ POST requests to create nodes
- ✅ Nested children serialization
- ✅ HTTP status codes
- ✅ JSON request/response handling

**Test Isolation**: 
- Each test uses a temporary database
- No test data pollution between runs
- Server tests use dynamic port allocation
- Automatic cleanup after each test

## Design Decisions

### 1. Why Python Standard Library Only?

- **Simplicity**: No dependency management required
- **Portability**: Runs anywhere Python is installed
- **Learning**: Demonstrates core Python capabilities
- **Production-Ready**: Stdlib is battle-tested and stable

### 2. Why SQLite?

- **Zero Configuration**: No database server setup needed
- **File-Based**: Easy backups and migrations
- **ACID Compliant**: Reliable data integrity
- **Sufficient**: Perfect for small-to-medium data volumes
- **Standard Library**: Built into Python

### 3. Why ThreadingHTTPServer?

- **Concurrent Requests**: Handles multiple clients simultaneously
- **Simple**: No async complexity for this use case
- **Standard Library**: No need for external web frameworks
- **Adequate Performance**: Sufficient for typical API loads

### 4. Why Layered Architecture?

- **Separation of Concerns**: Each layer has a clear responsibility
- **Testability**: Layers can be tested independently
- **Maintainability**: Easy to modify one layer without affecting others
- **Scalability**: Easy to swap implementations (e.g., different database)


### 5. Data Model Design

**Schema**:
```sql
CREATE TABLE nodes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    label TEXT NOT NULL,
    parent_id INTEGER REFERENCES nodes(id)
)
```

- **Simple**: Only 3 columns needed
- **Self-Referencing**: parent_id creates the tree structure
- **Flexible**: NULL parent_id indicates root nodes
- **Scalable**: Supports any tree depth and multiple forests

### 6. Error Handling Strategy

- **HTTP Semantics**: Proper status codes (400, 404, 500)
- **Descriptive Messages**: Clear error messages for debugging
- **Custom Exceptions**: Domain-specific errors (ValidationError, NodeNotFound)
- **Defensive Programming**: Catches unexpected errors to prevent crashes

