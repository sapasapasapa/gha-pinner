from dataclasses import dataclass
from typing import List, Optional

import pytest
from typer.testing import CliRunner

from src.main import app


@dataclass(frozen=True)
class CommandTestParams:
    args: List[str]
    expected_exit_code: int
    expected_output: Optional[str] = None


runner = CliRunner()

# Test cases
ACTION_COMMAND = CommandTestParams(
    args=["action", "actions/checkout@v3"],
    expected_exit_code=0,
)
FILE_COMMAND = CommandTestParams(
    args=["file", "path/to/file.yml"],
    expected_exit_code=0,
)
VERSION_FLAG = CommandTestParams(
    args=["--version"],
    expected_exit_code=0,
    expected_output="gha-pinner v0.1.6",
)
NO_ARGS = CommandTestParams(
    args=[],
    expected_exit_code=1,
)
NO_FILE_SPECIFIED = CommandTestParams(
    args=["file"],
    expected_exit_code=2,  # Typer returns 2 for missing required arguments
    expected_output="Missing argument 'FILE'",
)
NO_ACTION_SPECIFIED = CommandTestParams(
    args=["action"],
    expected_exit_code=2,  # Typer returns 2 for missing required arguments
    expected_output="Missing argument 'ACTION'",
)


@pytest.mark.parametrize(
    "test_params",
    [
        ACTION_COMMAND,
        FILE_COMMAND,
        VERSION_FLAG,
        NO_ARGS,
        NO_FILE_SPECIFIED,
        NO_ACTION_SPECIFIED,
    ],
)
def test_command_execution(test_params: CommandTestParams, monkeypatch) -> None:
    """Test the CLI command execution with different arguments."""
    # Mock the functions that would make external API calls
    if "action" in test_params.args:
        monkeypatch.setattr("src.retriever.get_action_sha", lambda _: "mock-sha")
        monkeypatch.setattr("src.retriever.print_pinned_action", lambda *_: None)

    if "file" in test_params.args:
        # Mock the pin_action_in_file function to return an empty list of actions
        monkeypatch.setattr("src.editor.pin_action_in_file", lambda *_: [])

    if "dir" in test_params.args:
        # Mock the pin_actions_in_dir function to return an empty list of actions
        monkeypatch.setattr("src.editor.pin_actions_in_dir", lambda *_: [])

    # Run the command
    result = runner.invoke(app, test_params.args)

    # Check exit code
    assert result.exit_code == test_params.expected_exit_code

    # Check output if expected
    if test_params.expected_output:
        assert test_params.expected_output in result.stdout
