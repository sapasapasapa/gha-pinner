from re import Match, match
from typing import Any, Optional

import requests
from requests import Response

from common.constants import (
    ACTION_REGEX_PATTERN,
    ERROR_RETRIEVING_LATEST_RELEASE,
    ERROR_RETRIEVING_SHA,
    EXPECTED_FORMAT_MESSAGE,
    GITHUB_API_COMMITS_URL,
    GITHUB_API_RELEASES_URL,
    INVALID_ACTION_FORMAT_ERROR,
    ORIGINAL_ACTION_FORMAT,
    PINNED_ACTION_FORMAT,
)


def _parse_action(action: str) -> tuple[str, str, str]:
    """Parse the action string (owner/repo@ref)"""
    matched: Match[str] = match(ACTION_REGEX_PATTERN, action)
    if not matched:
        print(INVALID_ACTION_FORMAT_ERROR.format(action))
        print(EXPECTED_FORMAT_MESSAGE)
        return ("", "", "")

    return matched.groups()


def _get_latest_release_tag(owner: str, repo: str) -> Optional[str]:
    """Get the latest release tag for a repository"""
    api_url: str = GITHUB_API_RELEASES_URL.format(owner, repo)

    try:
        response: Response = requests.get(api_url)
        response.raise_for_status()
        data: dict[str, Any] = response.json()
        return data.get("tag_name")
    except requests.exceptions.RequestException as e:
        print(ERROR_RETRIEVING_LATEST_RELEASE.format(owner, repo, e))
        return None


def get_action_sha(action: str) -> str:
    """Retrieve the commit SHA for a GitHub Action."""

    owner, repo, ref = _parse_action(action)

    if owner == "" or repo == "" or ref == "":
        return None

    # Handle @latest tag by fetching the latest release tag
    if ref == "latest":
        latest_tag = _get_latest_release_tag(owner, repo)
        if not latest_tag:
            return None
        ref = latest_tag

    # GitHub API URL to get the commit SHA
    api_url: str = GITHUB_API_COMMITS_URL.format(owner, repo, ref)

    try:
        response: Response = requests.get(api_url)
        response.raise_for_status()
        data: dict[str, Any] = response.json()
        return data.get("sha")
    except requests.exceptions.RequestException as e:
        print(ERROR_RETRIEVING_SHA.format(action, e))
        return None

def print_pinned_action(action: str, sha: str) -> None:
    """Print the pinned action"""
    print(ORIGINAL_ACTION_FORMAT.format(action))
    print(PINNED_ACTION_FORMAT.format(action.split("@")[0], sha))