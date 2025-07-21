from dataclasses import dataclass
from unittest.mock import Mock, patch

import pytest
import requests

from src.retriever import _parse_action, get_action_sha, get_latest_release_tag


@dataclass(frozen=True)
class ParseActionParams:
    action: str
    expected_result: tuple[str, str, str]


VALID_ACTION = ParseActionParams(
    action="actions/checkout@v3",
    expected_result=("actions", "checkout", "v3"),
)

VALID_LATEST_ACTION = ParseActionParams(
    action="actions/checkout@latest",
    expected_result=("actions", "checkout", "latest"),
)

INVALID_ACTION = ParseActionParams(
    action="actions/checkout",
    expected_result=("", "", ""),
)


@pytest.mark.parametrize(
    "test_params",
    [
        VALID_ACTION,
        VALID_LATEST_ACTION,
        INVALID_ACTION,
    ],
)
def test_parse_action(test_params: ParseActionParams) -> None:
    result = _parse_action(test_params.action)
    assert result == test_params.expected_result


@dataclass(frozen=True)
class GetLatestReleaseParams:
    owner: str
    repo: str
    mock_response: dict
    mock_status_code: int
    expected_result: str = None
    expected_exception: bool = False


SUCCESSFUL_LATEST_RELEASE = GetLatestReleaseParams(
    owner="actions",
    repo="checkout",
    mock_response={"tag_name": "v4"},
    mock_status_code=200,
    expected_result="v4",
)

FAILED_LATEST_RELEASE = GetLatestReleaseParams(
    owner="actions",
    repo="checkout",
    mock_response={"message": "Not Found"},
    mock_status_code=404,
    expected_result=None,
    expected_exception=True,
)


@pytest.mark.parametrize(
    "test_params",
    [
        SUCCESSFUL_LATEST_RELEASE,
        FAILED_LATEST_RELEASE,
    ],
)
def test_get_latest_release_tag(test_params: GetLatestReleaseParams) -> None:
    # Create mock response
    mock_response = Mock()
    mock_response.status_code = test_params.mock_status_code
    mock_response.json.return_value = test_params.mock_response

    if test_params.expected_exception:
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError()

    # Mock the requests.get method
    with patch("src.retriever.requests.get", return_value=mock_response):
        # Call the function
        result = get_latest_release_tag(test_params.owner, test_params.repo)
        assert result == test_params.expected_result


@dataclass(frozen=True)
class GetActionShaParams:
    action: str
    mock_response: dict
    mock_status_code: int
    parse_result: tuple[str, str, str] = None
    latest_tag: str = None
    expected_exception: bool = False


SUCCESSFUL_ACTION = GetActionShaParams(
    action="actions/checkout@v3",
    mock_response={"sha": "abc123def456"},
    mock_status_code=200,
    parse_result=("actions", "checkout", "v3"),
)

SUCCESSFUL_LATEST_ACTION = GetActionShaParams(
    action="actions/checkout@latest",
    mock_response={"sha": "abc123def456"},
    mock_status_code=200,
    parse_result=("actions", "checkout", "latest"),
    latest_tag="v4",
)

FAILED_ACTION = GetActionShaParams(
    action="actions/checkout@v3",
    mock_response={"message": "Not Found"},
    mock_status_code=404,
    parse_result=("actions", "checkout", "v3"),
    expected_exception=True,
)

FAILED_LATEST_ACTION = GetActionShaParams(
    action="actions/checkout@latest",
    mock_response={},
    mock_status_code=200,
    parse_result=("actions", "checkout", "latest"),
    latest_tag=None,
)

INVALID_ACTION_FORMAT = GetActionShaParams(
    action="actions/checkout",
    mock_response={},
    mock_status_code=200,
    parse_result=("", "", ""),
)


@pytest.mark.parametrize(
    "test_params",
    [
        SUCCESSFUL_ACTION,
        SUCCESSFUL_LATEST_ACTION,
        FAILED_ACTION,
        FAILED_LATEST_ACTION,
        INVALID_ACTION_FORMAT,
    ],
)
def test_get_action_sha(test_params: GetActionShaParams) -> None:
    # Create mock response
    mock_response = Mock()
    mock_response.status_code = test_params.mock_status_code
    mock_response.json.return_value = test_params.mock_response

    if test_params.expected_exception:
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError()

    # Mock the requests.get method, _parse_action, and get_latest_release_tag
    with (
        patch("src.retriever.requests.get", return_value=mock_response),
        patch("src.retriever._parse_action", return_value=test_params.parse_result),
        patch(
            "src.retriever.get_latest_release_tag", return_value=test_params.latest_tag
        ),
    ):
        # Call the function
        result = get_action_sha(test_params.action)

        # For invalid action format, _parse_action returns empty strings
        if "" in test_params.parse_result:
            assert result is None
        # For latest tag that failed to retrieve
        elif test_params.parse_result[2] == "latest" and test_params.latest_tag is None:
            assert result is None
        # For successful API call
        elif test_params.mock_status_code == 200 and not test_params.expected_exception:
            assert result == test_params.mock_response.get("sha")
        # For failed API call
        else:
            assert result is None
