# Design Document: Model Context Protocol (MCP) Support for mini-SWE-agent

**Date:** 2026-11-20  
**Status:** In Review (Reviewed by Builder Check)  
**Topic:** Model Context Protocol (MCP) Integration  

---

## 1. Intent and Why

Currently, `peen` exclusively exposes a single execution mechanism to language models: a `bash` tool call that executes shell commands in an `Environment` (`LocalEnvironment`, `DockerEnvironment`, etc.).

While bash provides broad capability, requiring the model to formulate bash commands for every operation (such as web fetches, vector search / RAG, API queries, or structured repository inspection) introduces unnecessary friction, prompt bloat, shell quoting hazards, and error-prone multi-step scripting. 

By adding native **Model Context Protocol (MCP)** support, `peen` can connect directly to local or external MCP servers (over stdio), exposing specialized tools (e.g. documentation fetchers, code search, RAG indexes, database inspectors) directly as native tool calls to the model alongside `bash`. This provides substantial leverage and efficiency without compromising the simplicity of the agent.

---

## 2. Goals, Non-Goals, and Anti-Goals

### Goals
- **Config-driven Stdio MCP Servers**: Users can declare one or more MCP servers in configuration files (YAML) or CLI flags using standard `{command, args, env}` properties.
- **Dynamic Tool Registration**: Discovered MCP tools are seamlessly converted to standard function-calling schemas and provided to the model alongside `bash`.
- **Clean Action Routing**: When the model issues tool calls, `bash` is routed to the configured `Environment`, while MCP tool calls are dispatched to the appropriate MCP server session.
- **Human-in-the-Loop Confirmation**: `InteractiveAgent` allows users to review, confirm, or reject MCP tool calls with clear display of tool names and parameters, matching the existing interactive UX.
- **Full Serialization & Logging**: MCP tool invocations, results, and server configurations are recorded in the trajectory JSON (`.traj.json`).
- **Minimalist, Pythonic Code**: Maintain `peen`'s core philosophy—concise, readable, polymorphism-friendly implementations with typed data structures.

### Non-Goals
- **In-process MCP Server Hosting**: `peen` will not act as an MCP server for other agents; it acts strictly as an MCP client.
- **Full SSE/WebSocket Transport (Initial Scope)**: Stdio transport satisfies 99% of local developer and benchmark use cases (e.g., `uvx mcp-server-...`, `npx -y ...`, local python scripts). SSE/WebSocket can be added later if needed.
- **Replacing Bash**: MCP does not replace the execution environment; bash remains the default primary tool for terminal interaction and file modification.

### Anti-Goals
- **Heavy Framework Overhead**: Do not introduce complex orchestration frameworks (e.g. LangChain, LlamaIndex) or massive client wrapper hierarchies.
- **Forced Dependencies**: If a user runs without MCP configurations, the core agent must run without requiring MCP packages to be installed (`mcp` will be an optional dependency or handled cleanly).

---

## 3. Constraints & Style Guidelines (from `AGENTS.md`)
- Target Python $\ge$ 3.10 with type annotations (`list` instead of `List`, `pathlib.Path`).
- Minimal code footprint: concise, short, no redundant intermediate variables.
- Use `pydantic.BaseModel` for configuration tracking.
- Test with `pytest` without unnecessary mocking.
- Adhere to commit message conventions (`feat(mcp): ...`, `fix(agents): ...`).

---

## 4. Approaches Considered

1. **Config-Driven Stdio Client via Official MCP SDK (Chosen)**:
   - MCP servers are defined in config dictionaries/YAML.
   - A lightweight `MCPManager` manages the client connections via `mcp` Python SDK (using `stdio_client` and `ClientSession`).
   - Discovered tools are merged into model tools; actions are routed between `env` and `mcp_manager`.
   - *Why chosen:* Standard across AI agent ecosystems (Claude Code, Cursor, Antigravity), robust, keeps agent decoupled from environment internals.

2. **Environment-Hosted MCP**:
   - The environment container (Docker/Local) hosts MCP servers internally and tunnels tool calls through a shell wrapper.
   - *Rejected:* Heavy, container-dependent, prevents host-level tools (e.g. local browser, host git, host secrets) from being used cleanly when running in containers.

3. **Pure-MCP Re-architecture (Replacing Environment with MCP Bash)**:
   - Turn bash itself into an MCP server and route 100% of actions through MCP protocol.
   - *Rejected:* Violates simplicity and backwards compatibility of existing benchmark setups (SWE-bench, ProgramBench).

---

## 5. Detailed System Architecture & Builder Decisions

### 5.1 Architecture Diagram

```
                     ┌────────────────────────┐
                     │    mini CLI / Config   │
                     │  (mini.yaml / -c spec) │
                     └───────────┬────────────┘
                                 │
                     ┌───────────▼────────────┐
                     │       MCPManager       │
                     │ (stdio subprocesses)   │
                     └─────┬────────────┬─────┘
           Tools Schema    │            │ Tool Call Execution
      ┌────────────────────┘            └────────────────────┐
      ▼                                                      ▼
┌──────────────┐         actions: [bash, mcp]         ┌──────────────┐
│  Model API   │ ◄─────────────────────────────────── │ DefaultAgent │
│ (LitellmModel│                                      │ (Action      │
│  + MCP Tools)│                                      │  Dispatcher) │
└──────────────┘                                      └──────┬───────┘
                                                             │
                                                      action:│bash
                                                             ▼
                                                      ┌──────────────┐
                                                      │ Environment  │
                                                      │(Local/Docker)│
                                                      └──────────────┘
```

### 5.2 Resolved Architectural Decisions (from Builder Check)

#### Decision 1: Lifecycle Ownership & Wiring
- **Ownership**: `MCPManager` lifecycle is managed via context manager in `DefaultAgent.run()` (with fallback to runner-level lifecycle if pre-initialized).
- **Wiring**:
  - `DefaultAgent.__init__` accepts `mcp_manager: MCPManager | None = None` (or builds it from `mcp` config).
  - When `DefaultAgent.run()` begins, it starts `mcp_manager` (if configured and not already running).
  - Discovered tools are registered with `model.set_tools([BASH_TOOL, *mcp_manager.get_tools()])`.
  - On exit/finally, `mcp_manager.close()` ensures all stdio subprocesses are terminated without orphaning children.
  - This ensures programmatic usage (`DefaultAgent(model, env, mcp_manager=...)`) and all runners (`mini.py`, benchmarks) get automatic lifecycle and process hygiene.

#### Decision 2: Model Scope
- **Scope**: Tool-calling models built on OpenAI function calling format are supported.
- `actions_toolcall.py`'s `parse_toolcall_actions()` is updated to be tool-agnostic: it accepts `bash` and any registered MCP tool.
- `LitellmModel` dynamically stores and uses `self.tools` (defaulting to `[BASH_TOOL]`, updated via `set_tools`). Other models sharing `actions_toolcall.py` (e.g. `OpenRouterModel`, `PortkeyModel`) gain the same capability by exposing `set_tools()` or inheriting.

#### Decision 3: Tool Naming & Namespacing
- **Rule**: All MCP tools are namespaced as `{server_name}__{tool_name}` (e.g. `fetch__fetch_url`).
- **Why**: Zero collision risk with `bash` or across multiple MCP servers; routing is deterministic and stateless (`server_name, actual_name = name.split("__", 1)`). Trajectories, interactive prompts, and whitelist filters remain unambiguous.

#### Decision 4: Validation & Error Semantics
- **Parsing**: `parse_toolcall_actions` checks that the tool name is in `[bash, *registered_tools]` and that arguments parse as a JSON dictionary. Unrecognized tool names or invalid JSON raise `FormatError`.
- **Execution**: Argument schema mismatches or tool execution failures during `mcp_manager.execute()` return an observation dictionary:
  `{"output": str(e), "returncode": 1, "exception_info": f"MCP error: {e}"}`.
- This allows the model to receive the error observation and self-correct, without prematurely exhausting `max_consecutive_format_errors`.

---

## 6. Components & File Changes

1. **`src/peen/mcp/`** (New Package):
   - `config.py`: `MCPServerConfig`, `MCPConfig`.
   - `manager.py`: `MCPManager` managing stdio client sessions and tool execution via synchronous loop runner.
   - `__init__.py`: Export `MCPManager`, `MCPConfig`, `get_mcp_manager`.
2. **`src/peen/models/utils/actions_toolcall.py`**:
   - Generalize `parse_toolcall_actions` to allow registered tool names and return `{"tool_name": ..., "arguments": ..., "command": ...}`.
3. **`src/peen/models/litellm_model.py`**:
   - Add `set_tools(tools: list[dict])` and use `self.tools` in `_query()`.
4. **`src/peen/agents/default.py` & `interactive.py`**:
   - In `DefaultAgent`: accept `mcp_manager`, manage lifecycle in `run()`, route actions between `env` and `mcp_manager`.
   - In `InteractiveAgent`: format confirmation prompt for both `bash` and MCP tool calls.
5. **`src/peen/run/mini.py`**:
   - Parse `mcp` config section and wire `MCPManager` to the agent.
6. **Tests**:
   - Unit tests for `MCPManager` using a mock/dummy stdio server.
   - Unit tests for `actions_toolcall.py` with multi-tool parsing.
   - Integration test with `DefaultAgent` executing both `bash` and an MCP tool.

---

## 7. What's Left to the Builder

- Synchronous async event-loop runner utility for bridging async `mcp` SDK calls into peen's synchronous architecture.
- Pretty-printing multi-parameter tool calls in `InteractiveAgent` confirmation display.
- Graceful degradation when `mcp` library is not installed (raising friendly install instructions if MCP servers are configured).

---

## 8. Approvals

- [x] Technical Review (Builder Check - Passed)
- [ ] User Approval
