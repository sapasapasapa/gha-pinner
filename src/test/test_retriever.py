from dataclasses import dataclass
from unittest.mock import Mock, patch

import pytest
import requests

from src.retriever import _parse_action, get_action_sha


@dataclass(frozen=True)
class TestParseAction:
    action: str
    expected_result: tuple[str, str, str]


VALID_ACTION = TestParseAction(
    action="actions/checkout@v3",
    expected_result=("actions", "checkout", "v3"),
)

INVALID_ACTION = TestParseAction(
    action="actions/checkout",
    expected_result=("", "", ""),
)


@pytest.mark.parametrize(
    "test_params",
    [
        VALID_ACTION,
        INVALID_ACTION,
    ],
)
def test_parse_action(test_params: TestParseAction) -> None:
    result = _parse_action(test_params.action)
    assert result == test_params.expected_result


@dataclass(frozen=True)
class TestGetActionSha:
    action: str
    mock_response: dict
    mock_status_code: int
    parse_result: tuple[str, str, str] = None
    expected_exception: bool = False


SUCCESSFUL_ACTION = TestGetActionSha(
    action="actions/checkout@v3",
    mock_response={"sha": "abc123def456"},
    mock_status_code=200,
    parse_result=("actions", "checkout", "v3"),
)

FAILED_ACTION = TestGetActionSha(
    action="actions/checkout@v3",
    mock_response={"message": "Not Found"},
    mock_status_code=404,
    parse_result=("actions", "checkout", "v3"),
    expected_exception=True,
)

INVALID_ACTION_FORMAT = TestGetActionSha(
    action="actions/checkout",
    mock_response={},
    mock_status_code=200,
    parse_result=("", "", ""),
)


@pytest.mark.parametrize(
    "test_params",
    [
        SUCCESSFUL_ACTION,
        FAILED_ACTION,
        INVALID_ACTION_FORMAT,
    ],
)
def test_get_action_sha(test_params: TestGetActionSha) -> None:
    # Create mock response
    mock_response = Mock()
    mock_response.status_code = test_params.mock_status_code
    mock_response.json.return_value = test_params.mock_response

    if test_params.expected_exception:
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError()

    # Mock the requests.get method and _parse_action
    with (
        patch("src.retriever.requests.get", return_value=mock_response),
        patch("src.retriever._parse_action", return_value=test_params.parse_result),
        patch("src.retriever._print_pinned_action") as mock_print,
    ):
        # Call the function
        result = get_action_sha(test_params.action)

        # For invalid action format, _parse_action returns None
        if test_params.action == "actions/checkout":
            assert result is None
        # For successful API call
        elif test_params.mock_status_code == 200 and not test_params.expected_exception:
            mock_print.assert_called_once_with(
                test_params.action, test_params.mock_response.get("sha")
            )
        # For failed API call
        else:
            assert result is None
