# MCP — Model Context Protocol Tool Bridge

Access any MCP server's tools directly from bash via `mcporter`. No agent code changes needed.

## Setup (auto-run on first use)

If `mcporter` is not installed, set it up:

```bash
# Check if installed
which mcporter || npm install -g mcporter
```

If no MCP servers are configured yet, create the config:

```bash
mkdir -p ~/.mcporter
cat > ~/.mcporter/mcporter.json << 'EOF'
{
  "servers": {}
}
EOF
```

> mcporter also auto-discovers servers from Claude Desktop, Cursor, Codex, Windsurf, and VS Code configs. If the user already has MCP servers configured in any of those, they'll work automatically.

## How to Use

### 1. Discover available tools

```bash
# List all configured servers + status
mcporter list

# List tools from a specific server (TS-style signatures)
mcporter list <server>

# Full JSON schema for all tools (best for understanding params)
mcporter list <server> --schema

# JSON output (machine-readable)
mcporter list <server> --json

# Query an ad-hoc server without adding to config
mcporter list --stdio "python /path/to/server.py"
mcporter list --http-url https://example.com/mcp
```

### 2. Call a tool

```bash
# Colon-delimited flag style (shell-friendly)
mcporter call <server>.<tool> key:value key2:'string value'

# Function-call style (matches list output signatures)
mcporter call '<server>.<tool>(key: "value", key2: 42)'

# Read an arg from a file
mcporter call <server>.<tool> prompt:@./input.txt

# Control output format
mcporter call <server>.<tool> key:value --output json
mcporter call <server>.<tool> key:value --output markdown
mcporter call <server>.<tool> key:value --output text

# Save returned images to a directory
mcporter call <server>.<tool> key:value --save-images /tmp/mcp-images

# Set a timeout (ms)
mcporter call <server>.<tool> key:value --timeout 30000
```

### 3. Read resources (if server supports them)

```bash
# List resources
mcporter resource <server>

# Read a specific resource
mcporter resource <server> <uri>
```

## Adding MCP Servers

Add servers to `~/.mcporter/mcporter.json`:

### stdio server (local process)
```json
{
  "servers": {
    "capcut": {
      "type": "stdio",
      "command": "python",
      "args": ["/path/to/capcut-mcp-server.py"],
      "env": { "DRAFTS_DIR": "/Users/chethan/Movies/CapCut/User Data/Projects/com.lveditor.draft" }
    }
  }
}
```

### HTTP/SSE server (remote)
```json
{
  "servers": {
    "github": {
      "type": "http",
      "url": "https://mcp-server.example.com/mcp",
      "headers": { "Authorization": "Bearer ${GITHUB_TOKEN}" }
    }
  }
}
```

### Ad-hoc (try before configuring)
```bash
# stdio — test without adding to config
mcporter list --stdio "npx -y @modelcontextprotocol/server-filesystem /tmp"

# HTTP — test remote server
mcporter list --http-url https://mcp.linear.app/mcp

# Persist after testing
mcporter list --stdio "python server.py" --persist --name myserver
```

## Workflow Pattern

When you need a capability that might exist as an MCP tool:

1. **Check what's available**: `mcporter list`
2. **Inspect a server's tools**: `mcporter list <server> --schema`
3. **Call the tool**: `mcporter call <server>.<tool> args...`
4. **Parse output**: use `--output json` for structured data, `--output text` for plain text

## Tips

- Use `--json` with `list` and `--output json` with `call` for structured parsing
- Environment variables in config use `${VAR_NAME}` syntax (expanded at runtime)
- stdio servers spawn fresh per call — if startup is slow, consider `"lifecycle": "keep-alive"` in the server config and use `mcporter serve` bridge mode
- Multiple MCP servers can be called independently; each is a separate `mcporter call`
- Tool names are always `<server>.<tool>` (dot-separated)
