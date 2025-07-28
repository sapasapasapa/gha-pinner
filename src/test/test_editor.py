from dataclasses import dataclass
from unittest.mock import mock_open, patch

import pytest

from src.common.action_status import ActionStatus
from src.common.constants import ERROR_PROCESSING_FILE, FILE_NOT_FOUND_ERROR
from src.editor import (
    _is_github_workflow_file,
    _is_sha_reference,
    _process_actions_in_workflow_content,
    pin_action_in_file,
    pin_actions_in_dir,
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
    validate_only: bool = False


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
def test_process_actions_in_workflow_content(test_params: PinActionsParams) -> None:
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
        result, actions_found = _process_actions_in_workflow_content(
            test_params.content, test_params.validate_only
        )
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
    mock_actions_found = [
        {
            "action": "actions/checkout@v3",
            "status": ActionStatus.NEEDS_PINNING,
            "original_ref": "v3",
            "sha": "0123456789abcdef0123456789abcdef01234567",
        }
    ]

    with (
        patch("os.path.exists", return_value=True),
        patch("builtins.open", mock_open(read_data=mock_content)),
        patch(
            "src.editor._process_actions_in_workflow_content",
            return_value=(expected_content, mock_actions_found),
        ),
    ):
        result = pin_action_in_file("workflow.yml")
        assert result == mock_actions_found


def test_pin_action_in_file_not_exists() -> None:
    with (
        patch("os.path.exists", return_value=False),
        patch("builtins.print") as mock_print,
    ):
        result = pin_action_in_file("nonexistent.yml")
        mock_print.assert_called_once_with(
            FILE_NOT_FOUND_ERROR.format("nonexistent.yml")
        )
        assert result == []


def test_pin_action_in_file_exception() -> None:
    with (
        patch("os.path.exists", return_value=True),
        patch("builtins.open", side_effect=Exception("Test exception")),
        patch("builtins.print") as mock_print,
    ):
        result = pin_action_in_file("workflow.yml")
        mock_print.assert_called_once_with(
            ERROR_PROCESSING_FILE.format("workflow.yml", "Test exception")
        )
        assert result == []


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


@dataclass(frozen=True)
class PinActionsInDirParams:
    directory: str
    file_structure: dict
    expected_calls: list


RECURSIVE_DIR_TEST = PinActionsInDirParams(
    directory="/test_dir",
    file_structure={
        "/test_dir": ["workflow.yml", "other.txt", "subdir"],
        "/test_dir/subdir": ["nested_workflow.yml", "nested.txt"],
    },
    expected_calls=[
        "/test_dir/workflow.yml",
        "/test_dir/subdir/nested_workflow.yml",
    ],
)

FLAT_DIR_TEST = PinActionsInDirParams(
    directory="/test_dir",
    file_structure={
        "/test_dir": ["workflow.yml", "workflow.yaml", "other.txt"],
    },
    expected_calls=[
        "/test_dir/workflow.yml",
        "/test_dir/workflow.yaml",
    ],
)

EMPTY_DIR_TEST = PinActionsInDirParams(
    directory="/empty_dir",
    file_structure={
        "/empty_dir": [],
    },
    expected_calls=[],
)

NO_WORKFLOW_FILES_TEST = PinActionsInDirParams(
    directory="/no_workflows",
    file_structure={
        "/no_workflows": ["text.txt", "doc.md", "subdir"],
        "/no_workflows/subdir": ["nested.txt"],
    },
    expected_calls=[],
)


@pytest.mark.parametrize(
    "test_params",
    [
        RECURSIVE_DIR_TEST,
        FLAT_DIR_TEST,
        EMPTY_DIR_TEST,
        NO_WORKFLOW_FILES_TEST,
    ],
)
def test_pin_actions_in_dir(test_params: PinActionsInDirParams) -> None:
    """Test pin_actions_in_dir with various directory structures."""

    def mock_listdir(path):
        return test_params.file_structure.get(path, [])

    def mock_isdir(path):
        parts = path.split("/")
        dir_path = "/".join(parts[:-1])
        dirname = parts[-1]
        return (
            dirname in test_params.file_structure.get(dir_path, [])
            and path in test_params.file_structure
        )

    def mock_exists(path):
        return path in test_params.file_structure

    mock_actions = [{"action": "test-action", "status": ActionStatus.NEEDS_PINNING}]

    with (
        patch("os.listdir", side_effect=mock_listdir),
        patch("os.path.isdir", side_effect=mock_isdir),
        patch("os.path.exists", side_effect=mock_exists),
        patch(
            "src.editor._is_github_workflow_file",
            side_effect=lambda f: f.lower().endswith((".yml", ".yaml")),
        ),
        patch(
            "src.editor.pin_action_in_file", return_value=mock_actions
        ) as mock_pin_action,
    ):
        result = pin_actions_in_dir(test_params.directory)

        assert mock_pin_action.call_count == len(test_params.expected_calls)
        for call in test_params.expected_calls:
            mock_pin_action.assert_any_call(call, False)

        # Check that the result contains the expected number of actions
        assert len(result) == len(test_params.expected_calls) * len(mock_actions)
