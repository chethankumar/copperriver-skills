---
name: codebase-memory
description: "Code intelligence engine that indexes codebases into a persistent knowledge graph. 158 languages, sub-ms queries, 120x fewer tokens than grep. Use when exploring unfamiliar codebases, tracing call chains, finding dead code, or understanding architecture."
version: 1.0.0
category: coding
source: copperriver
author: DeusData
author-url: https://github.com/DeusData/codebase-memory-mcp
license: MIT
upstream-repo: DeusData/codebase-memory-mcp
---

# Codebase Memory (codebase-memory-mcp)

> **Attribution:** Adapted from [codebase-memory-mcp](https://github.com/DeusData/codebase-memory-mcp) by [DeusData](https://github.com/DeusData) (⭐18K). MIT License.

The fastest code intelligence engine for AI agents. Full-indexes an average repo in milliseconds, the Linux kernel in 3 minutes. Answers structural queries in under 1ms. Single static binary, zero dependencies.

## Setup

```bash
# macOS / Linux one-line install
curl -fsSL https://raw.githubusercontent.com/DeusData/codebase-memory-mcp/main/install.sh | bash

# With graph visualization UI
curl -fsSL https://raw.githubusercontent.com/DeusData/codebase-memory-mcp/main/install.sh | bash -s -- --ui

# Windows
irm https://raw.githubusercontent.com/DeusData/codebase-memory-mcp/main/install.ps1 | iex
```

This installs a single static binary + auto-configures MCP server entries for all detected coding agents.

**Verify:**
```bash
codebase-memory-mcp --version
```

## First Use

After install, restart CopperRiver. The MCP server runs automatically. In any conversation:

```
"Index this project"
```

The agent will call `index_repository` → full AST parse of 158 languages → persistent knowledge graph in SQLite. After that, all structural queries are sub-millisecond.

Enable auto-indexing for new projects:
```bash
codebase-memory-mcp config set auto_index true
```

## MCP Tools (14 total)

### Indexing

| Tool | What it does |
|------|-------------|
| `index_repository` | Index a repo into the graph. Auto-syncs after that via git watcher. |
| `list_projects` | List all indexed projects with node/edge counts. |
| `delete_project` | Remove a project and all its graph data. |
| `index_status` | Check indexing status of a project. |

### Querying

| Tool | What it does |
|------|-------------|
| `search_graph` | Structured search: by label, name pattern, file pattern, degree filters. |
| `trace_path` | BFS traversal — who calls X and what X calls. Depth 1-5. |
| `detect_changes` | Map git diff → affected symbols + blast radius with risk classification. |
| `query_graph` | Execute Cypher-like graph queries (read-only openCypher subset). |
| `get_graph_schema` | Node/edge counts, relationship patterns, property definitions. **Run this first** to understand the graph. |
| `get_code_snippet` | Read source code for a function by qualified name. |
| `get_architecture` | Codebase overview: languages, packages, routes, hotspots, clusters, ADRs. |
| `search_code` | Grep-like text search within indexed project files. |
| `manage_adr` | CRUD for Architecture Decision Records. |
| `ingest_traces` | Ingest runtime traces to validate HTTP_CALLS edges. |

## Common Workflows

### Understanding a new codebase

```python
# 1. Get the high-level architecture
get_architecture({"project": "my-app"})
# → languages, packages, routes, hotspots

# 2. Get the schema to understand what's queryable
get_graph_schema({"project": "my-app"})

# 3. Find the entry points
search_graph({"project": "my-app", "label": "Function", "degree_min": 3})
```

### Tracing a call chain

```python
# Who calls this function and what does it call?
trace_path({
    "project": "my-app",
    "qualified_name": "my-app.src.api.handler",
    "direction": "both",
    "depth": 3
})
```

### Finding dead code

```python
# Cypher query: functions that are never called
query_graph({
    "project": "my-app",
    "query": "MATCH (f:Function) WHERE NOT EXISTS { (f)<-[:CALLS]-() } RETURN f.name, f.file"
})
```

### Impact analysis before changes

```python
# What breaks if I modify this function?
trace_path({
    "project": "my-app",
    "qualified_name": "my-app.src.utils.format",
    "direction": "incoming",
    "depth": 5
})
```

### Cross-service HTTP tracing

```python
# Find all HTTP calls between services
search_graph({"project": "my-app", "edge_type": "HTTP_CALLS"})
```

## Graph Data Model

### Node Labels
`Project`, `Package`, `Folder`, `File`, `Module`, `Class`, `Function`, `Method`, `Interface`, `Enum`, `Type`, `Route`, `Resource`

### Edge Types
`CONTAINS_PACKAGE`, `CONTAINS_FOLDER`, `CONTAINS_FILE`, `DEFINES`, `DEFINES_METHOD`, `IMPORTS`, `CALLS`, `HTTP_CALLS`, `ASYNC_CALLS`, `IMPLEMENTS`, `HANDLES`, `USAGE`, `CONFIGURES`, `WRITES`, `MEMBER_OF`, `TESTS`, `USES_TYPE`, `FILE_CHANGES_WITH`

### Qualified Names
Format: `<project>.<path_parts>.<name>`. Use `search_graph` to discover them before calling `get_code_snippet`.

## Cypher Query Support

Read-only openCypher subset:
- **Clauses**: `MATCH`, `OPTIONAL MATCH`, `WHERE`, `WITH`, `RETURN`, `ORDER BY`, `SKIP`, `LIMIT`, `DISTINCT`, `UNWIND`, `UNION`, `CASE`
- **Patterns**: labelled nodes, relationship types/direction, variable-length paths `[*1..3]`
- **WHERE**: `= <> < <= > >=`, `AND/OR/XOR/NOT`, `IN`, `CONTAINS`, `STARTS WITH`, `ENDS WITH`, `IS [NOT] NULL`, regex `=~`, label test `n:Label`, `EXISTS { ... }`
- **Aggregates**: `count`, `sum`, `avg`, `min`, `max`, `collect`

## Performance

| Metric | Value |
|--------|-------|
| Average repo index | Milliseconds |
| Linux kernel (28M LOC, 75K files) | 3 minutes |
| Query response | < 1ms |
| Token savings | ~120x vs grep/read cycles |
| Languages | 158 (tree-sitter) + 9 with Hybrid LSP type resolution |

## Graph Visualization

If installed with `--ui` flag:
```bash
codebase-memory-mcp --ui=true --port=9749
# Open http://localhost:9749
```

## Configuration

```bash
codebase-memory-mcp config list
codebase-memory-mcp config set auto_index true
codebase-memory-mcp config set auto_index_limit 50000
```

| Env Var | Default | Purpose |
|---------|---------|---------|
| `CBM_CACHE_DIR` | `~/.cache/codebase-memory-mcp` | Database storage |
| `CBM_LOG_LEVEL` | `info` | Log verbosity |
| `CBM_WORKERS` | auto-detected | Parallel indexing workers |

## Derivative Work Notice

This skill is adapted from [codebase-memory-mcp](https://github.com/DeusData/codebase-memory-mcp) by DeusData, MIT License.
