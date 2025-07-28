import os
import re
from typing import Dict, List, Tuple

from src.common.action_status import ActionStatus
from src.common.constants import (
    ACTION_PARSING_ERROR,
    ACTION_SKIP_ERROR,
    ERROR_PROCESSING_FILE,
    FILE_NOT_FOUND_ERROR,
    NEEDS_PINNING_FORMAT,
    NOT_WORKFLOW_FILE_ERROR,
    SHA_REGEX_PATTERN,
    SUCCESS_PIN_MESSAGE,
    SUCCESS_VALIDATION_MESSAGE,
    WORKFLOW_ACTION_PATTERN,
    WORKFLOW_FILE_EXTENSIONS,
)
from src.retriever import get_action_sha, get_latest_release_tag


def _is_sha_reference(ref: str) -> bool:
    """Check if the reference is already a SHA (40 hex characters)"""
    return bool(re.match(SHA_REGEX_PATTERN, ref))


def _is_github_workflow_file(file: str) -> bool:
    """Check if the file is a GitHub workflow file based on extension"""
    # Check file extension
    return file.lower().endswith(WORKFLOW_FILE_EXTENSIONS)


def _process_actions_in_workflow_content(
    content: str, validate_only: bool = False
) -> Tuple[str, List[Dict[str, str]]]:
    """Process actions in the workflow content

    Args:
        content: The workflow file content
        validate_only: If True, only validate actions without modifying content

    Returns:
        Tuple containing:
        - Updated content (or original if validate_only=True)
        - List of actions found with their details
    """
    # Find all actions in the format 'uses: owner/repo@ref' or other valid formats
    # This pattern handles standard actions, actions with organization, and docker actions
    pattern = WORKFLOW_ACTION_PATTERN
    actions_found = []

    def replace_action(match):
        indent = match.group(1)
        action = match.group(2)

        # Try to parse the action reference
        try:
            # For GitHub actions in the format owner/repo@ref
            if "@" in action and "/" in action:
                action_base, ref = action.rsplit("@", 1)

                # Skip if already pinned with SHA
                if _is_sha_reference(ref):
                    actions_found.append(
                        {
                            "action": action,
                            "status": ActionStatus.ALREADY_PINNED,
                            "sha": ref,
                        }
                    )
                    return match.group(0)

                # Store the original ref for comment
                original_ref = ref

                # If the reference is 'latest', get the actual latest version tag
                if ref == "latest":
                    # Parse the owner and repo from the action
                    parts = action_base.split("/")
                    if len(parts) >= 2:
                        owner = parts[-2]
                        repo = parts[-1]
                        latest_tag = get_latest_release_tag(owner, repo)
                        if latest_tag:
                            original_ref = f"latest ({latest_tag})"

                sha = get_action_sha(action)

                if sha:
                    # Add to found actions
                    actions_found.append(
                        {
                            "action": action,
                            "status": ActionStatus.NEEDS_PINNING,
                            "original_ref": original_ref,
                            "sha": sha,
                        }
                    )

                    # Replace the reference with the SHA and append the original version as a comment
                    if validate_only:
                        return match.group(0)
                    else:
                        return f"{indent}{action_base}@{sha} # {original_ref}"
                else:
                    # If we couldn't get the SHA, it might be a private action or there was an error
                    actions_found.append(
                        {
                            "action": action,
                            "status": ActionStatus.ERROR,
                            "message": "Unable to retrieve SHA",
                        }
                    )
                    # Keep the original and print a message
                    print(ACTION_SKIP_ERROR.format(action))
                    return match.group(0)
            else:
                # Not a GitHub action or already using a different format
                actions_found.append(
                    {
                        "action": action,
                        "status": ActionStatus.SKIPPED,
                        "message": "Not a standard GitHub action format",
                    }
                )
                return match.group(0)
        except Exception as e:
            actions_found.append(
                {"action": action, "status": ActionStatus.ERROR, "message": str(e)}
            )
            print(ACTION_PARSING_ERROR.format(action, e))
            return match.group(0)

    updated_content = re.sub(pattern, replace_action, content)
    return updated_content, actions_found


def pin_action_in_file(file: str, validate_only: bool = False) -> List[Dict[str, str]]:
    """Pin the action in the file or validate actions that need pinning

    Args:
        file: Path to the GitHub Action workflow file
        validate_only: If True, only validate actions without modifying file

    Returns:
        List of actions found with their details
    """
    actions_found = []

    if not os.path.exists(file):
        print(FILE_NOT_FOUND_ERROR.format(file))
        return actions_found

    if not _is_github_workflow_file(file):
        print(NOT_WORKFLOW_FILE_ERROR.format(file))
        return actions_found

    try:
        # Read the file content
        with open(file, "r") as f:
            content = f.read()

        # Process actions in the content
        updated_content, actions_found = _process_actions_in_workflow_content(
            content, validate_only
        )

        if not validate_only:
            # Write the updated content back to the file
            with open(file, "w") as f:
                f.write(updated_content)
            print(SUCCESS_PIN_MESSAGE.format(file))
        else:
            for action in actions_found:
                if action["status"] == ActionStatus.NEEDS_PINNING:
                    print(
                        NEEDS_PINNING_FORMAT.format(
                            action["action"],
                            action["action"].split("@")[0],
                            action["sha"],
                        )
                    )
            print(SUCCESS_VALIDATION_MESSAGE.format(file))

    except Exception as e:
        print(ERROR_PROCESSING_FILE.format(file, e))

    return actions_found


def pin_actions_in_dir(dir: str, validate_only: bool = False) -> List[Dict[str, str]]:
    """Pin the actions in the directory recursively or validate actions that need pinning

    Args:
        dir: Path to the directory
        validate_only: If True, only validate actions without modifying files

    Returns:
        List of actions found with their details
    """
    all_actions = []

    if not os.path.exists(dir):
        print(FILE_NOT_FOUND_ERROR.format(dir))
        return all_actions

    for file in os.listdir(dir):
        file_path = os.path.join(dir, file)
        if os.path.isdir(file_path):
            actions = pin_actions_in_dir(file_path, validate_only)
            all_actions.extend(actions)
        elif _is_github_workflow_file(file_path):
            actions = pin_action_in_file(file_path, validate_only)
            all_actions.extend(actions)

    return all_actions
