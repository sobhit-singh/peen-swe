# Model Troubleshooting

This guide addresses common errors encountered when connecting Peen-SWE to language models and Model Context Protocol (MCP) servers.

---

## Authentication & API Keys

### Invalid API Key Error

```text
AuthenticationError: litellm.AuthenticationError: ProviderException - API key not valid.
```

**Resolution**:
1. Confirm your provider's API key is set in your current terminal session:
   ```bash
   echo $ANTHROPIC_API_KEY   # Or OPENAI_API_KEY, GEMINI_API_KEY, etc.
   ```
2. If unset, export it directly:
   ```bash
   export ANTHROPIC_API_KEY="sk-ant-..."
   ```
3. To persist keys permanently across all sessions, use the Peen config helper:
   ```bash
   peen-extra config set ANTHROPIC_API_KEY "sk-ant-..."
   ```
4. You can review all persisted keys at any time:
   ```bash
   peen-extra config edit
   ```

---

### Missing Provider Prefix

```text
google.auth.exceptions.DefaultCredentialsError: Your default credentials were not found.
```
or
```text
BadRequestError: LLM Provider NOT provided. Pass in the LLM provider you are trying to call.
```

**Resolution**:
Peen-SWE uses provider-prefixed model strings to route requests accurately. Always prefix model names with their provider:

| Correct | Incorrect |
| :--- | :--- |
| `anthropic/claude-3-5-sonnet-20241022` | `claude-3-5-sonnet-20241022` |
| `openai/gpt-4o` | `gpt-4o` |
| `gemini/gemini-2.0-flash` | `gemini-2.0-flash` |
| `ollama/qwen2.5-coder:32b` | `qwen2.5-coder:32b` |
| `openrouter/deepseek/deepseek-chat` | `deepseek/deepseek-chat` |

You can pass the prefixed name via CLI or environment variable:
```bash
peen -m "anthropic/claude-3-5-sonnet-20241022"
# or
export PEEN_MODEL_NAME="anthropic/claude-3-5-sonnet-20241022"
```

---

## Cost Calculation & Unmapped Models

### Model Not Mapped Exception

```text
Exception: This model isn't mapped yet. model=ollama/qwen2.5-coder, custom_llm_provider=ollama.
```

**Resolution**:
When using local models (Ollama, vLLM, LM Studio) or newly released models that do not exist in the default cost table, cost calculation raises an exception.

Bypass cost calculation by setting:
```bash
export MSWEA_COST_TRACKING="ignore_errors"
```
Or in your YAML config file:
```yaml
model:
  cost_tracking: "ignore_errors"
```

For custom token pricing, supply a JSON registry file as documented in the [Local Models Guide](local_models.md).

---

## Parameter Compatibility

### Temperature Not Supported

```text
BadRequestError: Unsupported parameter: 'temperature' is not supported by this model.
```

**Resolution**:
Certain reasoning models (e.g. OpenAI `o1`, `o3-mini`) reject non-default temperature values.
Peen-SWE's default configuration omits the temperature parameter, allowing models to use their native defaults. If using custom configs, remove `temperature: ...` from your `model:` block.

---

## Model Context Protocol (MCP) Errors

### Server Process Failed to Start

```text
FileNotFoundError: [Errno 2] No such file or directory: 'uvx'
```

**Resolution**:
1. Ensure the executable specified in `command:` is installed in your `$PATH`.
2. For Python-based MCP servers using `uvx`, ensure `uv` is installed:
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```
3. For Node-based MCP servers using `npx`, ensure Node.js and npm are installed.

### Tool Call Timed Out

```text
TimeoutError: MCP tool execution timed out after 60.0s.
```

**Resolution**:
Long-running operations (such as large git clones or heavy database queries) can exceed the default 60-second execution window. You can adjust the timeout per tool or server in your MCP configuration.

{% include-markdown "../_footer.md" %}
