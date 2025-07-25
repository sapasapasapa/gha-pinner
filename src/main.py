#!/usr/bin/env python3

from typing import Optional

import typer

from src.common.constants import (
    ACTION_ARG_HELP,
    DIR_ARG_HELP,
    FILE_ARG_HELP,
    PROGRAM_DESCRIPTION,
    PROGRAM_NAME,
    VERSION,
    VERSION_ARG_HELP,
)
from src.editor import pin_action_in_file, pin_actions_in_dir
from src.retriever import get_action_sha, print_pinned_action

app = typer.Typer(help=PROGRAM_DESCRIPTION)


def version_callback(value: bool) -> None:
    if value:
        typer.echo(f"{PROGRAM_NAME} {VERSION}")
        raise typer.Exit()


@app.callback(invoke_without_command=True)
def callback(
    version: bool = typer.Option(
        False,
        "-v",
        "--version",
        help=VERSION_ARG_HELP,
        callback=version_callback,
        is_flag=True,
    ),
    ctx: typer.Context = typer.Option(None, hidden=True),
) -> None:
    """
    Pin GitHub Actions to specific commit SHAs for improved security.
    """
    # If no command is provided and version flag is not used, show help
    if ctx.invoked_subcommand is None and not version:
        typer.echo(ctx.get_help())
        raise typer.Exit(code=1)


@app.command("action", help="Get the commit SHA for a specific GitHub Action.")
def pin_action(
    action: str = typer.Argument(..., help=ACTION_ARG_HELP),
) -> None:
    """
    Pin a specific GitHub Action by name and get its commit SHA.
    """
    sha: str = get_action_sha(action)
    print_pinned_action(action, sha)


@app.command("file", help="Process a workflow file and pin all actions in it.")
def pin_file(
    file: str = typer.Argument(..., help=FILE_ARG_HELP),
) -> None:
    """
    Process a workflow file and pin all actions in it.
    """
    pin_action_in_file(file)

@app.command("dir", help="Process a directory and pin all actions in it.")
def pin_dir(
    dir: str = typer.Argument(..., help=DIR_ARG_HELP),
) -> None:
    """
    Process a directory and pin all actions in it.
    """
    pin_actions_in_dir(dir)

if __name__ == "__main__":
    app()
