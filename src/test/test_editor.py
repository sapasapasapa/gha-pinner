from dataclasses import dataclass
from unittest.mock import mock_open, patch

import pytest

from src.common.constants import ERROR_PROCESSING_FILE, FILE_NOT_FOUND_ERROR
from src.editor import (
    _is_github_workflow_file,
    _is_sha_reference,
    _pin_actions_in_workflow_content,
    pin_action_in_file,
)


@dataclass(frozen=True)
class IsShaReferenceParams:
    ref: str
    expected_result: bool


VALID_SHA = IsShaReferenceParams(
    ref="0123456789abcdef0123456789abcdef01234567",
    expected_result=True,
)

INVALID_SHA_TOO_SHORT = IsShaReferenceParams(
    ref="0123456789abcdef",
    expected_result=False,
)

INVALID_SHA_TOO_LONG = IsShaReferenceParams(
    ref="0123456789abcdef0123456789abcdef012345670123456789",
    expected_result=False,
)

INVALID_SHA_NON_HEX = IsShaReferenceParams(
    ref="0123456789abcdef0123456789abcdef0123456z",
    expected_result=False,
)

TAG_REFERENCE = IsShaReferenceParams(
    ref="v3",
    expected_result=False,
)


@pytest.mark.parametrize(
    "test_params",
    [
        VALID_SHA,
        INVALID_SHA_TOO_SHORT,
        INVALID_SHA_TOO_LONG,
        INVALID_SHA_NON_HEX,
        TAG_REFERENCE,
    ],
)
def test_is_sha_reference(test_params: IsShaReferenceParams) -> None:
    result = _is_sha_reference(test_params.ref)
    assert result == test_params.expected_result


@dataclass(frozen=True)
class PinActionsParams:
    content: str
    get_sha_returns: dict
    get_latest_tag_returns: dict
    expected_result: str


ALREADY_PINNED_ACTION = PinActionsParams(
    content="""name: Test
on: push
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@0123456789abcdef0123456789abcdef01234567
""",
    get_sha_returns={},
    get_latest_tag_returns={},
    expected_result="""name: Test
on: push
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@0123456789abcdef0123456789abcdef01234567
""",
)

PIN_VERSIONED_ACTION = PinActionsParams(
    content="""name: Test
on: push
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
""",
    get_sha_returns={"actions/checkout@v3": "0123456789abcdef0123456789abcdef01234567"},
    get_latest_tag_returns={},
    expected_result="""name: Test
on: push
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@0123456789abcdef0123456789abcdef01234567 # v3
""",
)

PIN_LATEST_ACTION = PinActionsParams(
    content="""name: Test
on: push
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@latest
""",
    get_sha_returns={
        "actions/checkout@latest": "0123456789abcdef0123456789abcdef01234567"
    },
    get_latest_tag_returns={("actions", "checkout"): "v4"},
    expected_result="""name: Test
on: push
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@0123456789abcdef0123456789abcdef01234567 # latest (v4)
""",
)

FAILED_TO_PIN_ACTION = PinActionsParams(
    content="""name: Test
on: push
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
""",
    get_sha_returns={"actions/checkout@v3": None},
    get_latest_tag_returns={},
    expected_result="""name: Test
on: push
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
""",
)

MULTIPLE_ACTIONS = PinActionsParams(
    content="""name: Test
on: push
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
""",
    get_sha_returns={
        "actions/checkout@v3": "0123456789abcdef0123456789abcdef01234567",
        "actions/setup-node@v3": "fedcba9876543210fedcba9876543210fedcba98",
    },
    get_latest_tag_returns={},
    expected_result="""name: Test
on: push
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@0123456789abcdef0123456789abcdef01234567 # v3
      - uses: actions/setup-node@fedcba9876543210fedcba9876543210fedcba98 # v3
""",
)


@pytest.mark.parametrize(
    "test_params",
    [
        ALREADY_PINNED_ACTION,
        PIN_VERSIONED_ACTION,
        PIN_LATEST_ACTION,
        FAILED_TO_PIN_ACTION,
        MULTIPLE_ACTIONS,
    ],
)
def test_pin_actions_in_workflow_content(test_params: PinActionsParams) -> None:
    def mock_get_action_sha(action):
        return test_params.get_sha_returns.get(action)

    def mock_get_latest_release_tag(owner, repo):
        return test_params.get_latest_tag_returns.get((owner, repo))

    with (
        patch("src.editor.get_action_sha", side_effect=mock_get_action_sha),
        patch(
            "src.editor.get_latest_release_tag", side_effect=mock_get_latest_release_tag
        ),
    ):
        result = _pin_actions_in_workflow_content(test_params.content)
        assert result == test_params.expected_result


def test_pin_action_in_file_success() -> None:
    mock_content = """name: Test
on: push
jobs:
  test:
    steps:
      - uses: actions/checkout@v3
"""
    expected_content = """name: Test
on: push
jobs:
  test:
    steps:
      - uses: actions/checkout@0123456789abcdef0123456789abcdef01234567 # v3
"""

    with (
        patch("os.path.exists", return_value=True),
        patch("builtins.open", mock_open(read_data=mock_content)),
        patch(
            "src.editor._pin_actions_in_workflow_content", return_value=expected_content
        ),
    ):
        pin_action_in_file("workflow.yml")


def test_pin_action_in_file_not_exists() -> None:
    with (
        patch("os.path.exists", return_value=False),
        patch("builtins.print") as mock_print,
    ):
        pin_action_in_file("nonexistent.yml")
        mock_print.assert_called_once_with(
            FILE_NOT_FOUND_ERROR.format("nonexistent.yml")
        )


def test_pin_action_in_file_exception() -> None:
    with (
        patch("os.path.exists", return_value=True),
        patch("builtins.open", side_effect=Exception("Test exception")),
        patch("builtins.print") as mock_print,
    ):
        pin_action_in_file("workflow.yml")
        mock_print.assert_called_once_with(
            ERROR_PROCESSING_FILE.format("workflow.yml", "Test exception")
        )


@dataclass(frozen=True)
class IsGithubWorkflowFileParams:
    file: str
    expected_result: bool


@pytest.mark.parametrize(
    "file,expected",
    [
        ("workflow.yml", True),
        ("workflow.yaml", True),
        ("WORKFLOW.YML", True),
        ("WORKFLOW.YAML", True),
        ("workflow.txt", False),
        ("workflow.md", False),
        ("workflow", False),
        ("/path/to/workflow.yml", True),
        ("/path/to/workflow.yaml", True),
        ("/path/to/workflow.txt", False),
        ("", False),
    ],
)
def test_is_github_workflow_file(file: str, expected: bool) -> None:
    """Test the _is_github_workflow_file function with various file paths."""
    result = _is_github_workflow_file(file)
    assert result == expected
