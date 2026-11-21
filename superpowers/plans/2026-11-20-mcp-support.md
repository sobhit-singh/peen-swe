# Model Context Protocol (MCP) Support Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement Model Context Protocol (MCP) support in peen so agents can discover and invoke tools from stdio MCP servers alongside bash without altering existing bash execution.

**Architecture:** A lightweight `MCPManager` handles stdio subprocess lifecycles and tool calls using the standard `mcp` SDK. Discovered MCP tools are namespaced (`{server_name}__{tool_name}`) and registered with the model; `DefaultAgent` dispatches `bash` tool calls to `Environment.execute()` as before and routes namespaced MCP tool calls to `MCPManager.execute()`.

**Tech Stack:** Python 3.10+, `mcp` SDK, `pydantic`, `litellm`, `pytest`

**Spec:** [`docs/superpowers/specs/2026-11-20-mcp-support-design.md`](file:///C:/Users/ShobhitSingh/Desktop/Alchemy/peen/docs/superpowers/specs/2026-11-20-mcp-support-design.md)

## Global Constraints
- Target Python >= 3.10 with type annotations (`list` instead of `List`, `pathlib.Path`).
- Minimal code footprint; avoid intermediate variables just for passing to functions.
- Bash remains 100% untouched and functional: MCP is additive.
- All MCP tools exposed to the model must be namespaced as `{server_name}__{tool_name}`.
- If no MCP servers are configured, zero runtime overhead and no requirement for the `mcp` package.
- All unit and integration tests must pass cleanly.

## Review Focus
1. **MCP Server Startup Failure:** A misconfigured command or missing binary raises a descriptive error during startup without orphaning any child processes.
2. **Bash Backward Compatibility:** When no MCP servers are present, existing tests and bash workflows behave with zero behavioral or signature difference.
3. **Execution Error Handling:** An MCP tool returning an error produces an observation message (`returncode=1`, `exception_info=...`) rather than crashing or triggering an unintended format error.
4. **Interactive Action Display:** In `InteractiveAgent`, MCP tool calls are formatted as `[mcp:server_name__tool_name] {args}` so users can distinguish MCP calls from bash commands during confirmation.
5. **Clean Process Termination:** On agent finish or uncaught exception, all stdio child processes are terminated cleanly via `MCPManager.close()`.

---

### Task 1: MCP Configuration Models

**Files:**
- Create: `src/peen/mcp/__init__.py`
- Create: `src/peen/mcp/config.py`
- Test: `tests/mcp/test_config.py`

**Interfaces:**
- Produces:
  - `MCPServerConfig(command: str, args: list[str] = [], env: dict[str, str] = {})`
  - `MCPConfig(servers: dict[str, MCPServerConfig] = {})`

- [ ] **Step 1: Write the failing test**

```python
# tests/mcp/test_config.py
from peen.mcp.config import MCPConfig, MCPServerConfig

def test_mcp_server_config():
    cfg = MCPServerConfig(command="uvx", args=["mcp-server-fetch"], env={"KEY": "VAL"})
    assert cfg.command == "uvx"
    assert cfg.args == ["mcp-server-fetch"]
    assert cfg.env == {"KEY": "VAL"}

def test_mcp_config_defaults():
    cfg = MCPConfig()
    assert cfg.servers == {}

def test_mcp_config_parsing():
    data = {"servers": {"fetch": {"command": "uvx", "args": ["mcp-server-fetch"]}}}
    cfg = MCPConfig(**data)
    assert "fetch" in cfg.servers
    assert cfg.servers["fetch"].command == "uvx"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/mcp/test_config.py -v`  
Expected: FAIL with ModuleNotFoundError (`No module named 'peen.mcp'`)

- [ ] **Step 3: Implement `MCPServerConfig` and `MCPConfig`**

Create `src/peen/mcp/config.py` using `pydantic.BaseModel`. Create `src/peen/mcp/__init__.py` exporting them.

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/mcp/test_config.py -v`  
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/peen/mcp/ tests/mcp/test_config.py
git commit -n --no-gpg-sign -m "feat(mcp): add MCP configuration models"
```

---

### Task 2: MCP Stdio Client & Manager

**Files:**
- Create: `src/peen/mcp/manager.py`
- Modify: `src/peen/mcp/__init__.py`
- Test: `tests/mcp/test_manager.py`

**Interfaces:**
- Consumes: `MCPConfig`, `MCPServerConfig` from `src/peen/mcp/config.py`
- Produces:
  - `MCPManager(config: MCPConfig | dict)`
  - `MCPManager.start() -> None`
  - `MCPManager.close() -> None`
  - `MCPManager.get_tools() -> list[dict]`
  - `MCPManager.execute(action: dict) -> dict[str, Any]`

- [ ] **Step 1: Write the failing test with a dummy stdio MCP server**

Create `tests/mcp/test_manager.py` that spins up a minimal mock MCP server script via python stdio, calls `start()`, verifies `get_tools()` returns namespaced tools (`dummy__echo`), calls `execute({"tool_name": "dummy__echo", "arguments": {"msg": "hello"}})`, and calls `close()`.

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/mcp/test_manager.py -v`  
Expected: FAIL with `ImportError: cannot import name 'MCPManager'`

- [ ] **Step 3: Implement `MCPManager` in `src/peen/mcp/manager.py`**

Implement `MCPManager` using `mcp.client.stdio` and `mcp.ClientSession`. Use a background asyncio runner thread or dedicated loop runner to provide synchronous `start()`, `close()`, `get_tools()`, and `execute(action)` methods. Ensure `{server_name}__{tool_name}` prefixing on tool discovery and unprefixing on tool execution.

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/mcp/test_manager.py -v`  
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/peen/mcp/manager.py src/peen/mcp/__init__.py tests/mcp/test_manager.py
git commit -n --no-gpg-sign -m "feat(mcp): implement MCPManager for stdio server management"
```

---

### Task 3: Tool-Agnostic Action Parsing & Dynamic Model Tools

**Files:**
- Modify: `src/peen/models/utils/actions_toolcall.py`
- Modify: `src/peen/models/litellm_model.py`
- Test: `tests/models/test_actions_toolcall.py`

**Interfaces:**
- `parse_toolcall_actions(tool_calls: list, *, format_error_template: str, template_kwargs: dict | None = None, valid_tool_names: list[str] | None = None) -> list[dict]`
  - Produces: `list[dict]` where each element is `{"tool_name": name, "command": cmd, "arguments": args, "tool_call_id": id}`
- `LitellmModel.set_tools(tools: list[dict]) -> None`

- [ ] **Step 1: Write failing tests for multi-tool parsing and model tool setting**

In `tests/models/test_actions_toolcall.py`, test that:
1. `parse_toolcall_actions` succeeds when given an MCP tool call (e.g. `dummy__echo`) with valid arguments if `valid_tool_names` includes it.
2. `parse_toolcall_actions` raises `FormatError` if tool name is unknown.
3. `LitellmModel.set_tools(...)` sets `model.tools` and uses them in completion.

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/models/test_actions_toolcall.py -v`  
Expected: FAIL on multi-tool parsing (`Unknown tool 'dummy__echo'`)

- [ ] **Step 3: Update `actions_toolcall.py` and `litellm_model.py`**

1. In `actions_toolcall.py`:
   - Keep `BASH_TOOL` default.
   - If `tool_call.function.name == "bash"`, require `command` in `args`.
   - If `tool_call.function.name != "bash"`, check against `valid_tool_names` (if provided) and verify `args` is a dict.
   - Return `{"tool_name": tool_call.function.name, "command": args.get("command", ""), "arguments": args, "tool_call_id": tool_call.id}`.
2. In `litellm_model.py`:
   - Add `self.tools = [BASH_TOOL]` in `__init__`.
   - Add `def set_tools(self, tools: list[dict]): self.tools = tools`.
   - Use `self.tools` in `litellm.completion(..., tools=self.tools)`.
   - Pass `valid_tool_names=[t["function"]["name"] for t in self.tools]` to `parse_toolcall_actions`.

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/models/test_actions_toolcall.py -v`  
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/peen/models/utils/actions_toolcall.py src/peen/models/litellm_model.py tests/models/test_actions_toolcall.py
git commit -n --no-gpg-sign -m "feat(models): support dynamic tools and generalized toolcall parsing"
```

---

### Task 4: Agent Action Routing & Lifecycle in `DefaultAgent`

**Files:**
- Modify: `src/peen/agents/default.py`
- Test: `tests/agents/test_mcp_routing.py`

**Interfaces:**
- `DefaultAgent(model, env, mcp_manager: MCPManager | None = None, ...)`
- In `run()`: starts `mcp_manager` if present, sets `model.set_tools([BASH_TOOL, *mcp_manager.get_tools()])`, cleans up `mcp_manager.close()` in `finally`.
- In `execute_actions()`:
  - If `action.get("tool_name", "bash") == "bash"`: `self.env.execute(action)`
  - Else: `self.mcp_manager.execute(action)`

- [ ] **Step 1: Write failing test for DefaultAgent action routing**

Create `tests/agents/test_mcp_routing.py`:
Instantiate a mock `MCPManager` that has tools `[{"type": "function", "function": {"name": "fetch__url"}}]`.
Verify that an action with `tool_name="bash"` is sent to `env.execute()`, and an action with `tool_name="fetch__url"` is routed to `mcp_manager.execute()`.

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/agents/test_mcp_routing.py -v`  
Expected: FAIL

- [ ] **Step 3: Update `DefaultAgent` in `src/peen/agents/default.py`**

Add `mcp_manager` parameter to `__init__`.
In `run()`: wrap loop in `try...finally` with `mcp_manager` lifecycle.
In `execute_actions()`: route based on `action.get("tool_name", "bash")`.

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/agents/test_mcp_routing.py -v`  
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/peen/agents/default.py tests/agents/test_mcp_routing.py
git commit -n --no-gpg-sign -m "feat(agents): add MCP action routing and lifecycle in DefaultAgent"
```

---

### Task 5: Interactive Confirmation & UX in `InteractiveAgent`

**Files:**
- Modify: `src/peen/agents/interactive.py`
- Test: `tests/agents/test_interactive_mcp.py`

**Interfaces:**
- In `InteractiveAgent.execute_actions()` and `_ask_confirmation_or_interrupt()`:
  - Extract display representations:
    - If bash: `action["command"]`
    - If MCP tool: `f"[mcp:{action['tool_name']}] {json.dumps(action['arguments'])}"`
  - Display them cleanly in confirmation prompt.

- [ ] **Step 1: Write failing test for InteractiveAgent with MCP actions**

In `tests/agents/test_interactive_mcp.py`, test that an MCP action without `"command"` does not crash `commands = [action["command"] for action in actions]` and displays the MCP tool call in confirm mode.

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/agents/test_interactive_mcp.py -v`  
Expected: FAIL with `KeyError: 'command'`

- [ ] **Step 3: Update `InteractiveAgent` in `src/peen/agents/interactive.py`**

Safely handle actions where `tool_name != "bash"` so `commands` extraction uses `action.get("command") or f"[mcp:{action.get('tool_name')}] {action.get('arguments')}"`.

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/agents/test_interactive_mcp.py -v`  
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/peen/agents/interactive.py tests/agents/test_interactive_mcp.py
git commit -n --no-gpg-sign -m "feat(agents): support MCP action confirmation in InteractiveAgent"
```

---

### Task 6: CLI & Configuration Wiring in `mini.py`

**Files:**
- Modify: `src/peen/run/mini.py`
- Modify: `pyproject.toml` (optional dependency `mcp`)
- Test: `tests/run/test_cli_mcp.py`

**Interfaces:**
- In `mini.py`: reads `config.get("mcp", {})`. If servers are defined, instantiates `MCPManager(config["mcp"])` and passes `mcp_manager` to `get_agent(...)`.

- [ ] **Step 1: Write test for CLI configuration parsing**

In `tests/run/test_cli_mcp.py`, verify that a configuration containing `mcp.servers` properly initializes `MCPManager` and attaches it to the instantiated agent.

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/run/test_cli_mcp.py -v`  
Expected: FAIL

- [ ] **Step 3: Update `src/peen/run/mini.py` and `pyproject.toml`**

Add `mcp` optional dependency in `pyproject.toml`. Wire `mcp_manager` in `mini.py`.

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/run/test_cli_mcp.py -v`  
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/peen/run/mini.py pyproject.toml tests/run/test_cli_mcp.py
git commit -n --no-gpg-sign -m "feat(cli): wire MCP configuration and dependency support in mini"
```

---

### Task 7: Full Regression & Verification

**Files:**
- Test: `tests/`

- [ ] **Step 1: Run all existing unit tests to verify zero regressions**

Run: `uv run pytest tests/config/ tests/utils/ tests/models/test_init.py`  
Expected: All pass.

- [ ] **Step 2: Run new MCP test suite**

Run: `uv run pytest tests/mcp/ tests/agents/test_mcp_routing.py tests/agents/test_interactive_mcp.py tests/run/test_cli_mcp.py -v`  
Expected: All pass.

- [ ] **Step 3: Commit plan completion**

```bash
git commit -n --no-gpg-sign --allow-empty -m "chore: verify MCP implementation and test suite"
```
