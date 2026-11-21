# `peen`

!!! abstract "Overview"

    `peen` is the interactive terminal interface for Peen-SWE. It runs directly in your local environment or sandbox, providing a fast REPL loop with direct bash execution and optional Model Context Protocol (MCP) integration.

```bash
# Start an interactive session
peen

# Run directly on a specific task
peen -t "Fix TypeError in test_cli.py"

# Run in YOLO mode with an MCP server configuration
peen -t "Analyze logs and database" -y --mcp-config mcp.json
```

## Command Line Options

| Flag | Type | Description |
| :--- | :--- | :--- |
| `-h`, `--help` | flag | Show help message and exit. |
| `-t`, `--task` | text | Task description to solve. If omitted, `peen` prompts interactively. |
| `-c`, `--config` | path | Path or filename of YAML config (defaults to `peen.yaml` or `PEEN_CONFIG_PATH`). |
| `-m`, `--model` | text | Model identifier (defaults to `PEEN_MODEL_NAME` or `MSWEA_MODEL_NAME`). |
| `-y`, `--yolo` | flag | Start in `yolo` mode (skip step-by-step confirmation). |
| `--mcp-config` | path | Path to JSON file defining Model Context Protocol servers to launch. |

## Interactive Modes

During a session, you can switch execution modes at any prompt by typing the mode command, or by pressing `Ctrl+C` to interrupt running execution:

- **Confirm mode (`/c`)**: The agent outputs its proposed action and waits. Press `Enter` to approve, or type instructions to redirect it. Default mode.
- **YOLO mode (`/y`)**: The agent executes every step automatically without prompting for confirmation.
- **Human mode (`/u`)**: You take over the shell directly to run manual commands, inspect files, or edit state.

## Model Context Protocol (MCP)

Peen-SWE supports Model Context Protocol servers via `--mcp-config`:

```json
{
  "mcpServers": {
    "git": {
      "command": "uvx",
      "args": ["mcp-server-git", "--repository", "."]
    },
    "fetch": {
      "command": "uvx",
      "args": ["mcp-server-fetch"]
    }
  }
}
```

When an MCP config is supplied:
1. `peen` starts each configured server over stdio.
2. Tools are discovered dynamically via JSON-RPC.
3. The language model can invoke MCP tools as structured toolcalls alongside bash execution.
4. All MCP processes terminate cleanly when the session exits.

## Session Artifacts & Trajectories

Every run records its full trajectory (prompts, toolcalls, outputs, token usage, and git diffs) to:

```text
~/.peen/trajectories/<session_id>.json
```

The exact file path is printed to stdout at the start and conclusion of each run. You can inspect saved trajectories using the built-in inspector:

```bash
peen-inspector ~/.peen/trajectories/
```

## Implementation Details

??? note "Default Configuration (`peen.yaml`)"

    - [View file on GitHub](https://github.com/sobhit-singh/peen-swe/blob/main/src/peen/config/peen.yaml)

    ```yaml
    --8<-- "src/peen/config/peen.yaml"
    ```

??? note "CLI Entrypoint (`peen.py`)"

    - [View file on GitHub](https://github.com/sobhit-singh/peen-swe/blob/main/src/peen/run/peen.py)
    - [API Reference](../reference/run/peen.md)

    ```python
    --8<-- "src/peen/run/peen.py"
    ```

??? note "Interactive Agent Class (`interactive.py`)"

    - [View file on GitHub](https://github.com/sobhit-singh/peen-swe/blob/main/src/peen/agents/interactive.py)
    - [API Reference](../reference/agents/interactive.md)

    ```python
    --8<-- "src/peen/agents/interactive.py"
    ```

{% include-markdown "../_footer.md" %}
