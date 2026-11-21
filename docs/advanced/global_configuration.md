# Global Configuration

This guide describes how to configure global settings for Peen-SWE, including default models, API keys, cost limits, and runtime environment paths.

## Setting Global Variables

Global settings can be defined in two ways:
1. Environment variables in your current shell or system profile.
2. The global `.env` file located in your user config directory (the path is displayed at startup by `peen`).

Environment variables in your active shell take precedence over entries in `.env`.

### CLI Configuration Helpers

You can manage configuration using the CLI helper:

```bash
# Interactive setup wizard for default model and API keys
peen-extra config setup

# Set a specific key
peen-extra config set PEEN_MODEL_NAME "anthropic/claude-3-5-sonnet-20241022"
peen-extra config set ANTHROPIC_API_KEY "sk-ant-..."

# Remove a configured key
peen-extra config unset ANTHROPIC_API_KEY

# Open the global .env file in your default editor
peen-extra config edit
```

## Model and Key Settings

```bash
# Default model name
# (Checked before MSWEA_MODEL_NAME)
PEEN_MODEL_NAME="anthropic/claude-3-5-sonnet-20241022"

# Primary API keys (standard provider names)
ANTHROPIC_API_KEY="sk-ant-..."
OPENAI_API_KEY="sk-..."
OPENROUTER_API_KEY="sk-or-..."
```

### Cost and Call Limits

```bash
# Maximum number of model API calls per agent execution (0 = unlimited)
MSWEA_GLOBAL_CALL_LIMIT="100"

# Maximum dollar spending per session (0 = unlimited)
MSWEA_GLOBAL_COST_LIMIT="10.00"

# Number of retry attempts on network or rate limit failure (default: 10)
MSWEA_MODEL_RETRY_STOP_AFTER_ATTEMPT="10"

# Ignore cost tracking errors for local or unregistered models
MSWEA_COST_TRACKING="ignore_errors"
```

## Config and Storage Paths

```bash
# Default configuration YAML path for the peen CLI
# (default: builtin peen.yaml)
PEEN_CONFIG_PATH="/path/to/custom_peen.yaml"

# Additional directory to search for agent configuration templates
MSWEA_CONFIG_DIR="/path/to/my/configs"

# Global config directory override (default: OS user config dir)
PEEN_GLOBAL_CONFIG_DIR="/path/to/.peen"

# Suppress startup banner
PEEN_SILENT_STARTUP="true"
```

## Sandbox Environments

```bash
# Path to Docker / Podman binary
MSWEA_DOCKER_EXECUTABLE="docker"

# Path to Singularity / Apptainer binary
MSWEA_SINGULARITY_EXECUTABLE="singularity"

# Path to Bubblewrap binary
MSWEA_BUBBLEWRAP_EXECUTABLE="bwrap"
```

{% include-markdown "../_footer.md" %}
