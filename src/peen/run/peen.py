#!/usr/bin/env python3

"""Peen-SWE: Compact, workshop-forged terminal agent built to shape and refine code with zero black-box bloat."""

import json
import os
from pathlib import Path
from typing import Any

import typer
import yaml
from rich.console import Console
from rich.panel import Panel

from peen import global_config_dir
from peen.agents import get_agent
from peen.agents.utils.prompt_user import _multiline_prompt
from peen.config import builtin_config_dir, get_config_from_spec
from peen.environments import get_environment
from peen.models import get_model
from peen.run.utilities.config import configure_if_first_time
from peen.utils.serialize import UNSET, recursive_merge

_DEFAULT_PEEN_YAML = (
    Path("peen.yaml") if Path("peen.yaml").exists() else builtin_config_dir / "peen.yaml"
)
DEFAULT_CONFIG_FILE = Path(
    os.getenv("PEEN_CONFIG_PATH", _DEFAULT_PEEN_YAML if _DEFAULT_PEEN_YAML.exists() else builtin_config_dir / "mini.yaml")
)
DEFAULT_OUTPUT_FILE = global_config_dir / "last_peen_run.traj.json"

BANNER = r"""[bold cyan]
  ___  ___ ___ _  _     ______      _____ 
 | _ \/ __| __| \| |___/ __\ \    / / __|
 |  _/ (__| _|| .` |___\__ \\ \/\/ /| _|  
 |_|  \___|___|_|\_|   |___/ \_/\_/ |___| 
[/bold cyan]
[dim]Compact, workshop-forged terminal agent · Bash + MCP superpowers[/dim]"""

_HELP_TEXT = """Peen-SWE: Autonomous code engineering agent in your local terminal.

Run tasks interactively or in autonomous YOLO mode with native Bash and MCP protocol tools.
"""

console = Console(highlight=False)
app = typer.Typer(rich_markup_mode="rich")


@app.command(help=_HELP_TEXT)
def main(
    model_name: str | None = typer.Option(None, "-m", "--model", help="Model name (e.g. gpt-4o, claude-3-7-sonnet, ollama/deepseek-r1)"),
    model_class: str | None = typer.Option(None, "--model-class", help="Model class to use (e.g. 'litellm')", rich_help_panel="Advanced"),
    agent_class: str | None = typer.Option(None, "--agent-class", help="Agent class to use ('interactive' or 'default')", rich_help_panel="Advanced"),
    environment_class: str | None = typer.Option(None, "--environment-class", help="Environment class ('local' or 'docker')", rich_help_panel="Advanced"),
    task: str | None = typer.Option(None, "-t", "--task", help="Task or issue statement to execute"),
    yolo: bool = typer.Option(False, "-y", "--yolo", help="Run without human confirmation prompts (autonomous execution)"),
    cost_limit: float | None = typer.Option(None, "-l", "--cost-limit", help="Cost limit in USD. Set to 0 to disable."),
    config_spec: list[str] = typer.Option([str(DEFAULT_CONFIG_FILE)], "-c", "--config", help="Configuration file path, name, or key=value overrides"),
    mcp_config_path: Path | None = typer.Option(None, "--mcp-config", help="Path to dedicated MCP configuration file (.json or .yaml)"),
    output: Path | None = typer.Option(DEFAULT_OUTPUT_FILE, "-o", "--output", help="Output trajectory file path"),
    exit_immediately: bool = typer.Option(False, "--exit-immediately", help="Exit immediately upon task completion without prompt", rich_help_panel="Advanced"),
) -> Any:
    console.print(Panel(BANNER, border_style="cyan"))
    configure_if_first_time()

    configs = [get_config_from_spec(spec) for spec in config_spec]
    if isinstance(mcp_config_path, (str, Path)) and Path(mcp_config_path).exists():
        path = Path(mcp_config_path)
        raw_text = path.read_text(encoding="utf-8")
        parsed_mcp = json.loads(raw_text) if path.suffix == ".json" else yaml.safe_load(raw_text)
        configs.append({"mcp": parsed_mcp.get("mcp", parsed_mcp)})

    configs.append({
        "run": {"task": task or UNSET},
        "agent": {
            "agent_class": agent_class or UNSET,
            "mode": "yolo" if yolo else UNSET,
            "cost_limit": cost_limit if cost_limit is not None else UNSET,
            "confirm_exit": False if exit_immediately else UNSET,
            "output_path": output or UNSET,
        },
        "model": {
            "model_class": model_class or UNSET,
            "model_name": model_name or UNSET,
        },
        "environment": {
            "environment_class": environment_class or UNSET,
        },
    })
    config = recursive_merge(*configs)

    if (run_task := config.get("run", {}).get("task", UNSET)) is UNSET:
        console.print("\n[bold cyan]🔨 What code would you like to shape or refine today?[/bold cyan]")
        run_task = _multiline_prompt()
        console.print("[bold green]Task accepted. Starting agent...[/bold green]\n")

    mcp_manager = None
    if (mcp_config := config.get("mcp")) and mcp_config.get("servers"):
        from peen.mcp import MCPManager

        console.print(f"[bold cyan]Connecting MCP servers:[/bold cyan] {list(mcp_config['servers'].keys())}")
        mcp_manager = MCPManager(mcp_config)

    model = get_model(config=config.get("model", {}))
    env = get_environment(config.get("environment", {}), default_type="local")
    agent_config = {**config.get("agent", {})}
    if mcp_manager is not None:
        agent_config["mcp_manager"] = mcp_manager
    agent = get_agent(model, env, agent_config, default_type="interactive")
    agent.run(run_task)
    if output_path := config.get("agent", {}).get("output_path"):
        console.print(f"\n[dim]Trajectory saved to [bold green]'{output_path}'[/bold green][/dim]")
    return agent


if __name__ == "__main__":
    app()
