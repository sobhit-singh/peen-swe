# Language Model Setup

Peen-SWE supports any commercial or open-weight language model through unified provider routing, including Anthropic, OpenAI, OpenRouter, Google Gemini, and local inference engines.

---

## Setting Up Your Provider

### 1. Configure API Keys

Set your provider's API key in your current shell:

=== "Anthropic"

    ```bash
    export ANTHROPIC_API_KEY="sk-ant-..."
    ```

=== "OpenAI"

    ```bash
    export OPENAI_API_KEY="sk-..."
    ```

=== "OpenRouter"

    ```bash
    export OPENROUTER_API_KEY="sk-or-..."
    ```

=== "Google Gemini"

    ```bash
    export GEMINI_API_KEY="..."
    ```

=== "Local (Ollama / vLLM)"

    No API key required. See the [Local Models Guide](local_models.md) for endpoint configuration:

    ```bash
    export PEEN_MODEL_NAME="ollama/qwen2.5-coder:32b"
    export MSWEA_COST_TRACKING="ignore_errors"
    ```

### 2. Persisting Keys Across Sessions

To store your keys permanently without re-exporting in every new shell:

```bash
# Interactive setup wizard
peen-extra config setup

# Or set individual variables directly
peen-extra config set PEEN_MODEL_NAME "anthropic/claude-3-5-sonnet-20241022"
peen-extra config set ANTHROPIC_API_KEY "sk-ant-..."

# Edit the persisted .env configuration file
peen-extra config edit
```

---

## Specifying Models

Always include the provider prefix when specifying a model:

```bash
# Run interactively with a specific model
peen -m "anthropic/claude-3-5-sonnet-20241022"

# Run with an OpenAI model
peen -m "openai/gpt-4o"

# Run with OpenRouter
peen -m "openrouter/deepseek/deepseek-r1"
```

To set your default model globally:

```bash
export PEEN_MODEL_NAME="anthropic/claude-3-5-sonnet-20241022"
```

---

## Recommended Models for Software Engineering

| Provider | Model Identifier | Strengths |
| :--- | :--- | :--- |
| **Anthropic** | `anthropic/claude-3-5-sonnet-20241022` | Industry gold-standard for code generation and test fixing. |
| **Anthropic** | `anthropic/claude-3-7-sonnet-20250219` | State-of-the-art reasoning and multi-step refactoring. |
| **OpenAI** | `openai/gpt-4o` | High throughput, reliable JSON/tool call adherence. |
| **OpenRouter** | `openrouter/deepseek/deepseek-chat` | Highly cost-effective full-context coding. |
| **Ollama (Local)** | `ollama/qwen2.5-coder:32b` | Best local open-weight model for terminal agents. |

---

## Full Provider Key Reference

Peen-SWE reads the following standard environment variables for provider authentication:

| Provider | Environment Variable |
| :--- | :--- |
| Anthropic | `ANTHROPIC_API_KEY` |
| OpenAI | `OPENAI_API_KEY` |
| OpenRouter | `OPENROUTER_API_KEY` |
| Google Gemini | `GEMINI_API_KEY` |
| DeepSeek | `DEEPSEEK_API_KEY` |
| Groq | `GROQ_API_KEY` |
| Mistral AI | `MISTRAL_API_KEY` |
| Together AI | `TOGETHERAI_API_KEY` |
| Portkey | `PORTKEY_API_KEY` |
| Azure OpenAI | `AZURE_API_KEY`, `AZURE_API_BASE` |

{% include-markdown "../_footer.md" %}
