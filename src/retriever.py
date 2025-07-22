from re import Match, match
from typing import Any, Optional

import requests
from requests import Response

from src.common.constants import (
    ACTION_REGEX_PATTERN,
    ERROR_RETRIEVING_LATEST_RELEASE,
    ERROR_RETRIEVING_SHA,
    EXPECTED_FORMAT_MESSAGE,
    GITHUB_API_COMMITS_URL,
    GITHUB_API_RELEASES_URL,
    INVALID_ACTION_FORMAT_ERROR,
    ORIGINAL_ACTION_FORMAT,
    PINNED_ACTION_FORMAT,
    PRIVATE_OR_INVALID_ACTION_ERROR,
    UNABLE_TO_PIN_ACTION,
)


def _parse_action(action: str) -> tuple[str, str, str]:
    """Parse the action string (owner/repo@ref)"""
    matched: Match[str] = match(ACTION_REGEX_PATTERN, action)
    if not matched:
        print(INVALID_ACTION_FORMAT_ERROR.format(action))
        print(EXPECTED_FORMAT_MESSAGE)
        return ("", "", "")

    return matched.groups()


def get_latest_release_tag(owner: str, repo: str) -> Optional[str]:
    """Get the latest release tag for a repository"""
    api_url: str = GITHUB_API_RELEASES_URL.format(owner, repo)
    try:
        response: Response = requests.get(api_url)
        response.raise_for_status()
        data: dict[str, Any] = response.json()
        return data.get("tag_name")
    except Exception as e:
        print(ERROR_RETRIEVING_LATEST_RELEASE.format(owner, repo, e))
        return None


def get_action_sha(action: str) -> Optional[str]:
    """Retrieve the commit SHA for a GitHub Action."""

    owner, repo, ref = _parse_action(action)

    if owner == "" or repo == "" or ref == "":
        return None

    # Handle @latest tag by fetching the latest release tag
    if ref == "latest":
        latest_tag = get_latest_release_tag(owner, repo)
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
    except requests.exceptions.HTTPError as e:
        # Handle 404 errors (private or invalid actions)
        try:
            if hasattr(e, "response") and e.response and e.response.status_code == 404:
                print(PRIVATE_OR_INVALID_ACTION_ERROR.format(action))
        except AttributeError:
            print(ERROR_RETRIEVING_SHA.format(action, e))
        return None
    except requests.exceptions.RequestException as e:
        print(ERROR_RETRIEVING_SHA.format(action, e))
        return None


def print_pinned_action(action: str, sha: Optional[str]) -> None:
    """Print the pinned action"""
    if sha:
        owner, repo, ref = _parse_action(action)
        print(ORIGINAL_ACTION_FORMAT.format(action))
        print(PINNED_ACTION_FORMAT.format(f"{owner}/{repo}", sha))
    else:
        print(UNABLE_TO_PIN_ACTION.format(action))
