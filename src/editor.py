import os
import re

from src.common.constants import (
    ACTION_PARSING_ERROR,
    ACTION_SKIP_ERROR,
    ERROR_PROCESSING_FILE,
    FILE_NOT_FOUND_ERROR,
    NOT_WORKFLOW_FILE_ERROR,
    SHA_REGEX_PATTERN,
    SUCCESS_PIN_MESSAGE,
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


def _pin_actions_in_workflow_content(content: str) -> str:
    """Pin actions in the workflow content"""
    # Find all actions in the format 'uses: owner/repo@ref' or other valid formats
    # This pattern handles standard actions, actions with organization, and docker actions
    pattern = WORKFLOW_ACTION_PATTERN

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
                    # Replace the reference with the SHA and append the original version as a comment
                    return f"{indent}{action_base}@{sha} # {original_ref}"
                else:
                    # If we couldn't get the SHA, it might be a private action or there was an error
                    # Keep the original and print a message
                    print(ACTION_SKIP_ERROR.format(action))
                    return match.group(0)
            else:
                # Not a GitHub action or already using a different format
                return match.group(0)
        except Exception as e:
            print(ACTION_PARSING_ERROR.format(action, e))
            return match.group(0)

    return re.sub(pattern, replace_action, content)


def pin_action_in_file(file: str) -> None:
    """Pin the action in the file

    Args:
        file: Path to the GitHub Action workflow file
    """
    if not os.path.exists(file):
        print(FILE_NOT_FOUND_ERROR.format(file))
        return

    if not _is_github_workflow_file(file):
        print(NOT_WORKFLOW_FILE_ERROR.format(file))
        return

    try:
        # Read the file content
        with open(file, "r") as f:
            content = f.read()

        # Pin actions in the content
        updated_content = _pin_actions_in_workflow_content(content)

        # Write the updated content back to the file
        with open(file, "w") as f:
            f.write(updated_content)

        print(SUCCESS_PIN_MESSAGE.format(file))

    except Exception as e:
        print(ERROR_PROCESSING_FILE.format(file, e))
