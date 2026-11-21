# Peen-SWE

<p class="subtitle" style="font-size: 1.15rem; color: #8E9BAE; margin-top: -0.5rem; margin-bottom: 1.5rem;">
  Compact, workshop-forged terminal agent built to shape and refine code with zero black-box bloat.
</p>

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg?style=flat-square)](https://github.com/sobhit-singh/peen-swe/blob/main/LICENSE.md)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg?style=flat-square)](https://www.python.org/downloads/)
[![MCP Ready](https://img.shields.io/badge/MCP-Protocol%202.0-8A2BE2?style=flat-square)](https://modelcontextprotocol.io/)
[![SWE-bench Verified](https://img.shields.io/badge/SWE--bench-74%25%20Verified-success?style=flat-square)](https://www.swebench.com/)
[![GitHub Repo](https://img.shields.io/badge/GitHub-sobhit--singh%2Fpeen--swe-black?style=flat-square&logo=github)](https://github.com/sobhit-singh/peen-swe)

---

## What is Peen-SWE?

Peen-SWE is a minimal, transparent software engineering agent for the terminal. Built on a clean 100-line Python core, it executes shell commands directly via stateless execution and connects to external developer tools using the **Model Context Protocol (MCP)**.

No bloated abstractions, no opaque prompt graphs, and no fragile shell sessions.

```bash
# Install with MCP support
pip install "peen[mcp]"

# Or run directly without installation
uvx peen

# Launch the interactive terminal agent
peen
```

## Key Capabilities

- **Direct Bash Execution**: Runs shell commands cleanly via independent `subprocess.run` calls—no state corruption or stuck terminal sessions.
- **Model Context Protocol (MCP)**: Mount external tools (Git, issue trackers, database clients, linters) using standard stdio MCP servers via `--mcp-config`.
- **Linear, Inspectable History**: Prompt history is an append-only sequence of user inputs, agent bash actions, MCP tool calls, and command outputs.
- **Three Interactive Modes**:
  - `confirm` (`/c`): Inspect and approve every proposed action.
  - `yolo` (`/y`): Unattended autonomous execution.
  - `human` (`/u`): Step in and run commands manually at any point.
- **Broad Model Support**: Cloud APIs (Anthropic, OpenAI, OpenRouter, Portkey) and local LLMs (Ollama, vLLM, LM Studio) without code changes.
- **Pluggable Sandboxes**: Run locally or isolate execution inside Docker, Podman, Bubblewrap, or Singularity.

## Upstream Lineage & Attribution

Peen-SWE is forked and overhauled from [peen](https://github.com/sobhit-singh/peen-swe) (Princeton NLP / SWE-bench team). We extend the minimal core with full Model Context Protocol (MCP) integration, enhanced CLI workflows (`peen`), dedicated local model profiles, and an overhaul of tooling and documentation.

## Core Workflows

| Mode | Entrypoint | Description |
| :--- | :--- | :--- |
| **Interactive Terminal** | [`peen`](usage/peen.md) | Interactive REPL with confirmation, YOLO, and human takeover. |
| **Benchmarking** | [`swebench`](usage/swebench.md) | Run batch evaluations on SWE-bench and ProgramBench. |
| **Trajectory Browser** | [`inspector`](usage/inspector.md) | Web-based visual viewer for inspectable session step logs. |
| **Python Library** | [`python_bindings`](usage/python_bindings.md) | Embed the agent in three lines of Python code. |

## Quick Navigation

<div class="grid cards">
  <a href="quickstart/" class="nav-card-link">
    <div class="nav-card">
      <div class="nav-card-header">
        <span class="material-icons nav-card-icon">rocket_launch</span>
        <span class="nav-card-title">Quickstart</span>
      </div>
      <p class="nav-card-description">Install Peen-SWE and run your first task in 2 minutes.</p>
    </div>
  </a>

  <a href="usage/peen/" class="nav-card-link">
    <div class="nav-card">
      <div class="nav-card-header">
        <span class="material-icons nav-card-icon">terminal</span>
        <span class="nav-card-title">CLI: <code>peen</code></span>
      </div>
      <p class="nav-card-description">Flags, interactive modes, and MCP server configuration.</p>
    </div>
  </a>

  <a href="models/local_models/" class="nav-card-link">
    <div class="nav-card">
      <div class="nav-card-header">
        <span class="material-icons nav-card-icon">dns</span>
        <span class="nav-card-title">Local Models</span>
      </div>
      <p class="nav-card-description">Configure Ollama, vLLM, and LM Studio for offline coding.</p>
    </div>
  </a>

  <a href="advanced/yaml_configuration/" class="nav-card-link">
    <div class="nav-card">
      <div class="nav-card-header">
        <span class="material-icons nav-card-icon">tune</span>
        <span class="nav-card-title">Configuration</span>
      </div>
      <p class="nav-card-description">Customize prompt templates, agent limits, and environments.</p>
    </div>
  </a>
</div>

{% include-markdown "_footer.md" %}
