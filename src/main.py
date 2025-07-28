#!/usr/bin/env python3


import sys

import typer

from src.common.action_status import ActionStatus
from src.common.constants import (
    ACTION_ARG_HELP,
    DIR_ARG_HELP,
    FILE_ARG_HELP,
    PROGRAM_DESCRIPTION,
    PROGRAM_NAME,
    VALIDATE_ARG_HELP,
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
    validate: bool = typer.Option(
        False,
        "--validate",
        help=VALIDATE_ARG_HELP,
        is_flag=True,
    ),
) -> None:
    """
    Process a workflow file and pin all actions in it.
    """
    actions_found = pin_action_in_file(file, validate)

    # Exit with non-zero code if validation is enabled and unpinned actions are found
    if validate and any(
        action["status"] == ActionStatus.NEEDS_PINNING for action in actions_found
    ):
        sys.exit(1)


@app.command("dir", help="Process a directory and pin all actions in it.")
def pin_dir(
    dir: str = typer.Argument(..., help=DIR_ARG_HELP),
    validate: bool = typer.Option(
        False,
        "--validate",
        help=VALIDATE_ARG_HELP,
        is_flag=True,
    ),
) -> None:
    """
    Process a directory and pin all actions in it.
    """
    actions_found = pin_actions_in_dir(dir, validate)

    # Exit with non-zero code if validation is enabled and unpinned actions are found
    if validate and any(
        action["status"] == ActionStatus.NEEDS_PINNING for action in actions_found
    ):
        sys.exit(1)


if __name__ == "__main__":
    app()
