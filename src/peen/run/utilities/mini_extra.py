#!/usr/bin/env python3

"""This is the central entry point to the mini-extra script. Use subcommands
to invoke other command line utilities like running on benchmarks, editing config,
inspecting trajectories, etc.
"""

import sys
from importlib import import_module

from rich.console import Console

subcommands = [
    ("peen.run.utilities.config", ["config"], "Manage the global config file"),
    ("peen.run.utilities.inspector", ["inspect", "i", "inspector"], "Run inspector (browse trajectories)"),
    ("peen.run.benchmarks.swebench", ["swebench"], "Evaluate on SWE-bench (batch mode)"),
    ("peen.run.benchmarks.swebench_single", ["swebench-single"], "Evaluate on SWE-bench (single instance)"),
    ("peen.run.benchmarks.programbench", ["programbench"], "Run on ProgramBench (batch mode)"),
]


def get_docstring(prog: str = "peen-extra") -> str:
    app_name = "Peen-SWE" if "peen" in prog else "peen"
    lines = [
        f"This is the [yellow]central entry point for all extra commands[/yellow] from {app_name}.",
        "",
        "Available sub-commands:",
        "",
    ]
    for _, aliases, description in subcommands:
        alias_text = " or ".join(f"[bold green]{alias}[/bold green]" for alias in aliases)
        lines.append(f"  {alias_text}: {description}")
    return "\n".join(lines)


def main():
    prog = "peen-extra" if "peen" in sys.argv[0] else "mini-extra"
    args = sys.argv[1:]

    if len(args) == 0 or len(args) == 1 and args[0] in ["-h", "--help"]:
        return Console().print(get_docstring(prog))

    for module_path, aliases, _ in subcommands:
        if args[0] in aliases:
            return import_module(module_path).app(args[1:], prog_name=f"{prog} {aliases[0]}")

    return Console().print(get_docstring(prog))


if __name__ == "__main__":
    main()
