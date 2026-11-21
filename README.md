<div align="center">

```
  ___  ___ ___ _  _     ______      _____ 
 | _ \/ __| __| \| |___/ __\ \    / / __|
 |  _/ (__| _|| .` |___\__ \\ \/\/ /| _|  
 |_|  \___|___|_|\_|   |___/ \_/\_/ |___| 
```

### **Peen-SWE**
*Compact, workshop-forged terminal agent built to shape and refine code with zero black-box bloat.*

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg?style=flat-square)](LICENSE.md)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg?style=flat-square)](https://www.python.org/downloads/)
[![MCP Ready](https://img.shields.io/badge/MCP-Protocol%202.0-8A2BE2?style=flat-square)](https://modelcontextprotocol.io/)
[![SWE-bench Verified](https://img.shields.io/badge/SWE--bench-74%25%20Verified-success?style=flat-square)](https://www.swebench.com/)
[![PyPI](https://img.shields.io/pypi/v/peen?color=blue&style=flat-square)](https://pypi.org/project/peen/)
[![CI](https://github.com/sobhit-singh/peen-swe/actions/workflows/pytest.yaml/badge.svg)](https://github.com/sobhit-singh/peen-swe/actions)

[Quick Start](#-quick-start) • [Why Peen-SWE](#-why-peen-swe) • [MCP Superpowers](#-mcp-superpowers) • [Configuration](#-configuration) • [Credits & Attribution](#-credits--upstream-attribution)

---

</div>

## 🔨 Why Peen-SWE?

Most AI coding assistants have become heavy, opaque black boxes filled with proprietary scaffolding, silent prompt injections, and rigid execution harnesses.

Like a **ball-peen hammer** in a master craftsman's workshop, **Peen-SWE** is built to do one thing with surgical precision: shape, anneal, and refine code directly in your terminal without getting in your way.

* **Ultra-Transparent Control Flow**: The entire agent loop fits in readable, unbloated Python. No complex agent graphs, no buried telemetry, and no magic abstractions.
* **Dual Execution Engine**: Pairs native, stateless subshell Bash commands with standardized **Model Context Protocol (MCP)** tool discovery and calling.
* **Human-in-the-Loop Safeguards**: Displays exact shell commands and MCP calls with interactive confirmation before execution, or toggle into autonomous `--yolo` mode when you trust the run.
* **Proven Benchmark Pedigree**: Inherits the battle-tested, linear SWE-bench architecture that solves >74% of real-world GitHub issues.
* **Model Agnostic**: Works out of the box with Claude 3.7 / 3.5 Sonnet, GPT-4o, DeepSeek-R1, Qwen, or local models via LiteLLM, Ollama, OpenRouter, and Portkey.

---

## ⚡ Architecture

```
                       ┌──────────────────────┐
                       │     User Prompt      │
                       └──────────┬───────────┘
                                  │
                                  ▼
                       ┌──────────────────────┐
                       │   Peen-SWE Agent     │ ◄── [peen.yaml]
                       │ (Minimal Control Loop│
                       └──────────┬───────────┘
                                  │
         ┌────────────────────────┴────────────────────────┐
         ▼                                                 ▼
┌──────────────────┐                              ┌──────────────────┐
│  Bash Subshell   │                              │  MCP Stdio Hub   │
│ (Local / Docker) │                              │ (ClientSession)  │
└────────┬─────────┘                              └────────┬─────────┘
         │                                                 │
   [ls, git, edit, tests]                        [sqlite, fetch, custom APIs]
         │                                                 │
         └────────────────────────┬────────────────────────┘
                                  │ Observation Messages
                                  ▼
                       ┌──────────────────────┐
                       │   Next Action Loop   │
                       └──────────────────────┘
```

---

## 🚀 Quick Start

### 1. Installation & Usage

**Run instantly with `uvx` (no install required):**
```bash
# Run directly from PyPI (once published)
uvx peen

# Or run directly from GitHub before publishing
uvx --from git+https://github.com/sobhit-singh/peen-swe peen
```

**Install via `pip`:**
```bash
# Install with Model Context Protocol (MCP) support
pip install "peen[mcp]"

# Or install editable from source
git clone https://github.com/sobhit-singh/peen-swe.git
cd peen-swe
pip install -e ".[mcp]"
```

### 2. Configure Your API Key

Set the API key for your model of choice:

```bash
# Anthropic
export ANTHROPIC_API_KEY="sk-ant-..."

# OpenAI
export OPENAI_API_KEY="sk-..."

# OpenRouter
export OPENROUTER_API_KEY="sk-or-..."
```

### 3. Launch Peen-SWE

Run the interactive terminal interface:

```bash
peen
```

Or pass a specific task and model directly:

```bash
peen -m anthropic/claude-3-7-sonnet-20250219 -t "Fix bug in auth middleware where token expiration throws 500"
```

To run autonomously without manual confirmation prompts:
```bash
peen -y -t "Write unit tests for utils/date_parser.py and make sure they pass"
```

---

## 🔌 MCP Superpowers

Peen-SWE natively connects to any local or remote **Model Context Protocol (MCP)** server via standard stdio pipes.

All MCP tools are automatically namespaced as `{server_name}__{tool_name}` to prevent name collisions with standard shell commands.

### Defining MCP Servers in `peen.yaml`

Create a `peen.yaml` in your workspace or home directory:

```yaml
mcp:
  servers:
    # Query databases directly without manual shell pipelines
    db:
      command: "uvx"
      args: ["mcp-server-sqlite", "--db-path", "./analytics.db"]

    # Provide safe file access outside current repo
    docs:
      command: "npx"
      args: ["-y", "@modelcontextprotocol/server-filesystem", "../shared-docs"]

    # Web browsing & documentation fetcher
    web:
      command: "uvx"
      args: ["mcp-server-fetch"]
```

When you start `peen`, it automatically connects all servers, introspects their tool definitions, registers them with the model, and routes execution through an isolated async thread pool.

---

## ⚙️ Configuration

Peen-SWE supports hierarchical configuration:
1. Built-in defaults (`src/peen/config/peen.yaml`)
2. Local workspace config (`./peen.yaml`)
3. CLI overrides (`-c key=value` or `--mcp-config <path>`)

```bash
# Run with a dedicated MCP config file
peen --mcp-config ./my_tools.yaml

# Set a hard cost limit in USD
peen -l 2.50 -t "Refactor the payment webhook handler"
```

---

## 📋 CLI Reference

| Flag | Short | Description |
|---|---|---|
| `--model` | `-m` | Model name (e.g. `anthropic/claude-3-7-sonnet`, `openai/gpt-4o`, `ollama/deepseek-r1`) |
| `--task` | `-t` | Problem statement or task to solve |
| `--yolo` | `-y` | Autonomous mode (skip confirmation prompts) |
| `--config` | `-c` | Config spec path, file, or `key=value` override |
| `--mcp-config` | | Path to standalone JSON/YAML MCP server configuration |
| `--cost-limit` | `-l` | Cost limit in USD (set `0` to disable) |
| `--output` | `-o` | Output trajectory file path (`.traj.json`) |

---

## 📄 License

This project is licensed under the [MIT License](LICENSE.md).
