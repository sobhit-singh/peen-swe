# Quick Start

Get started with Peen-SWE in under two minutes.

## Installation

=== "pip (Recommended)"

    Install Peen with MCP support:

    ```bash
    pip install "peen[mcp]"
    ```

    Then run the interactive agent:

    ```bash
    peen
    ```

=== "uv / uvx"

    Run immediately without activating an environment:

    ```bash
    uvx peen
    ```

    Or run directly from GitHub:

    ```bash
    uvx --from git+https://github.com/sobhit-singh/peen-swe peen
    ```

    Or install into your global `uv` toolchain:

    ```bash
    uv tool install "peen[mcp]"
    peen
    ```

=== "From Source"

    For development or custom modifications:

    ```bash
    git clone https://github.com/sobhit-singh/peen-swe.git
    cd peen-swe
    pip install -e ".[full]"
    peen
    ```

## Running Your First Task

Run `peen` directly from your terminal inside any Git repository or project folder:

```bash
# Interactive REPL prompt
peen

# Provide task directly via CLI flag
peen -t "Find and fix the failing test in tests/test_calc.py"

# Unattended autonomous execution
peen -t "Generate API docs from docstrings" -y

# Mount external Model Context Protocol tools
peen -t "Query PostgreSQL and update migrations" --mcp-config mcp.json
```

## Configuring Models

Peen-SWE supports any language model through LiteLLM, OpenRouter, Portkey, or direct local providers (Ollama, vLLM, LM Studio).

Set your API key:

```bash
# For Anthropic
export ANTHROPIC_API_KEY="sk-ant-..."

# For OpenAI
export OPENAI_API_KEY="sk-..."

# For OpenRouter
export OPENROUTER_API_KEY="sk-or-..."
```

Set your preferred default model:

```bash
export PEEN_MODEL_NAME="anthropic/claude-3-5-sonnet-20241022"
```

Or pass it per run:

```bash
peen -m "openai/gpt-4o"
```

For offline local execution, see the [Local Models Guide](models/local_models.md).

## Example Prompts to Try

- `peen -t "Run pytest, find all failing tests, and fix them without changing test contracts."`
- `peen -t "Add type annotations and Google-style docstrings across src/utils.py."`
- `peen -t "Refactor the database connection logic into a context manager."`

{% include-markdown "_footer.md" %}
