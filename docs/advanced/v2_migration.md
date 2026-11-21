# Migration & Upstream Compatibility

This guide covers migrating from upstream `peen` to **Peen-SWE** and outlines backwards compatibility guarantees.

## Upstream Compatibility Guarantees

Peen-SWE is a direct evolution of the `peen` architecture. It is designed to be a drop-in replacement while adding native Model Context Protocol (MCP) support and workshop-grade CLI tools.

### 1. CLI Commands & Aliases

| Upstream Command | Peen-SWE Command | Status |
| :--- | :--- | :--- |
| `mini` | `peen` | `mini` remains supported as a built-in alias. |
| `peen` | `peen-swe` | Both commands invoke the interactive agent. |
| `mini-extra` | `peen-extra` | Both commands invoke the utility toolkit. |
| `mini-extra inspector` | `peen-inspector` | Standalone direct shortcut added. |
| `mini-extra swebench` | `peen-swebench` | Direct runner alias. |

### 2. Environment Variables

All Peen-SWE environment variables fall back automatically to legacy `MSWEA_*` definitions if set:

```bash
# New preferred variables
export PEEN_MODEL_NAME="anthropic/claude-3-5-sonnet-20241022"
export PEEN_CONFIG_PATH="/path/to/custom_peen.yaml"
export PEEN_GLOBAL_CONFIG_DIR="~/.peen"

# Legacy fallback variables (still fully respected)
# MSWEA_MODEL_NAME
# MSWEA_MINI_CONFIG_PATH
# MSWEA_GLOBAL_CONFIG_DIR
```

### 3. Adding Model Context Protocol (MCP)

To upgrade your existing workflows with MCP tools, supply a standard MCP JSON configuration:

```bash
peen -t "Query SQLite database and run pytest" --mcp-config mcp.json
```

Where `mcp.json` contains standard stdio server declarations:

```json
{
  "mcpServers": {
    "sqlite": {
      "command": "uvx",
      "args": ["mcp-server-sqlite", "--db-path", "test.db"]
    }
  }
}
```

### 4. Configuration Changes

Existing `mini.yaml` configuration files are compatible with Peen-SWE. To use the new workshop profile, select `peen.yaml` or pass `-c peen.yaml`.

{% include-markdown "../_footer.md" %}
