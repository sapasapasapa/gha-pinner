import os
import re
from typing import Optional, Match

from retriever import get_action_sha, print_pinned_action, get_latest_release_tag


def _is_sha_reference(ref: str) -> bool:
    """Check if the reference is already a SHA (40 hex characters)"""
    return bool(re.match(r'^[0-9a-f]{40}$', ref))


def _is_private_action(action: str) -> bool:
    """Check if the action is a private action (starts with ./ or uses docker:// or contains {{}})"""
    return (
        action.startswith("./") or
        action.startswith("docker://") or
        "{" in action
    )


def _pin_actions_in_workflow_content(content: str) -> str:
    """Pin actions in the workflow content"""
    # Find all actions in the format 'uses: owner/repo@ref' or other valid formats
    # This pattern handles standard actions, actions with organization, and docker actions
    pattern = r"(\s+uses:\s+)([^\s]+)"

    def replace_action(match):
        indent = match.group(1)
        action = match.group(2)
        
        # Skip if it's a private action or uses variables
        if _is_private_action(action):
            return match.group(0)
            
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
                    parts = action_base.split('/')
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
        except Exception as e:
            # If any error occurs during parsing, keep the original
            print(f"Error parsing action '{action}': {e}")
            pass
            
        # If we couldn't get the SHA or the action format is not supported, keep the original
        return match.group(0)

    # Replace all actions with their pinned versions
    return re.sub(pattern, replace_action, content)


def pin_action_in_file(file: str) -> None:
    """Pin the action in the file

    Args:
        file: Path to the GitHub Action workflow file
    """
    if not os.path.exists(file):
        print(f"Error: File '{file}' does not exist.")
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

        print(f"Successfully pinned actions in '{file}'")

    except Exception as e:
        print(f"Error processing file '{file}': {e}")
