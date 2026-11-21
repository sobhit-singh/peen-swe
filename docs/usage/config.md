# `peen-extra config`

!!! abstract "Overview"

    `peen-extra config` manages the global configuration file for Peen-SWE.
    Run it anytime to adjust default models, API keys, or sandbox paths.

## Commands

### `setup`

Interactive setup wizard for your default model and API keys:

```bash
peen-extra config setup
```

Prompts for:
1. Default model name (e.g., `anthropic/claude-3-5-sonnet-20241022` or `openai/gpt-4o`)
2. Provider API key (e.g., `ANTHROPIC_API_KEY`)

### `set`

Set a key in the global config file:

```bash
peen-extra config set PEEN_MODEL_NAME "anthropic/claude-3-5-sonnet-20241022"
```

### `unset`

Remove a key from the global config file:

```bash
peen-extra config unset ANTHROPIC_API_KEY
```

### `edit`

Open the global config file in your default editor:

```bash
peen-extra config edit
```

## Configuration Keys

For the full list of options, see [Global Configuration](../advanced/global_configuration.md).

## Implementation

??? note "Run Script"

    - [Read on GitHub](https://github.com/sobhit-singh/peen-swe/blob/main/src/peen/run/utilities/config.py)
    - [API Reference](../reference/run/config.md)

    ```python
    --8<-- "src/peen/run/utilities/config.py"
    ```

{% include-markdown "../_footer.md" %}
