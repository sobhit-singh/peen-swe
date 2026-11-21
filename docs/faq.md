# FAQ

## General

??? question "What operating systems does Peen-SWE support?"

    Peen-SWE runs on Linux, macOS, and Windows. It works anywhere a bash shell is available or inside container runtimes (Docker, Podman, Singularity/Apptainer, Bubblewrap).

??? question "How does Peen-SWE differ from older agents like SWE-agent?"

    Peen-SWE strips away bloated scaffold abstractions in favor of radical simplicity:

    - **Stateless execution**: Actions run via clean `subprocess.run` calls rather than keeping an interactive shell process open. This prevents state contamination, pseudo-terminal hangs, and shell crashes.
    - **Native Bash + MCP tools**: Instead of proprietary internal tools with custom prompt engines, Peen-SWE pairs bare shell commands with standard Model Context Protocol (MCP) servers.
    - **Linear history**: Context is an append-only log of messages with zero magic prompt rewriting, making debugging predictable and straightforward.

??? question "Where is the global configuration stored?"

    Global configuration resides in the `.env` file within your user config directory (the full path is printed when you run `peen`). You can also inspect or edit it using `peen-extra config edit`.

## Models

??? question "Which models are supported?"

    Peen-SWE supports any model available through LiteLLM, OpenRouter, Portkey, or direct local providers (Ollama, vLLM, LM Studio).

??? question "How do I configure API keys?"

    Set them in your shell environment:

    ```bash
    export ANTHROPIC_API_KEY="sk-ant-..."
    ```

    Or persist them across all sessions with the config helper:

    ```bash
    peen-extra config set ANTHROPIC_API_KEY "sk-ant-..."
    ```

??? question "How do I set the default model?"

    Set the `PEEN_MODEL_NAME` environment variable:

    ```bash
    peen-extra config set PEEN_MODEL_NAME "anthropic/claude-3-5-sonnet-20241022"
    ```

## Architecture

??? question "Why avoid a persistent background shell session?"
    <a name="why-no-shell-session"></a>

    Traditional coding agents keep a persistent pseudo-terminal session open across all steps. This causes several critical problems:
    1. **Termination ambiguity**: Determining when an arbitrary shell command has finished requires fragile heuristics (watching prompt escapes, monitoring PIDs, or polling buffers).
    2. **Shell corruption**: Misbehaving commands can leave the shell in raw mode, corrupt environment variables, or orphan background child processes.
    3. **Session death**: If a command triggers a shell segfault or kills the parent terminal, the entire agent run crashes.

    Peen-SWE executes each command independently using standard `subprocess.run` (or `docker exec` in containerized environments). The exit code and exact output are captured deterministically with zero heuristics.

{% include-markdown "_footer.md" %}
