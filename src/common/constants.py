"""
Constants used throughout the application.
"""

# Program information
PROGRAM_NAME = "gha-pinner"
VERSION = "v0.1.0"

# CLI descriptions and help messages
PROGRAM_DESCRIPTION = "Pin third-party Github Actions using the commit SHA"
ACTION_ARG_HELP = "The GitHub Action to pin (e.g., 'actions/checkout@v3')"
VERSION_ARG_HELP = "Show gha-pinner's version and exit"
FILE_ARG_HELP = "The file in which to pin the actions (e.g., 'path/to/file.yml')"

# Error and info messages
NO_ACTION_ERROR = "No GitHub Action specified. Use -a/--action to specify an action."
ACTION_EXAMPLE = "Example: gha-pinner -a actions/checkout@v3"
INVALID_ACTION_FORMAT_ERROR = "Error: Invalid action format: {}"
EXPECTED_FORMAT_MESSAGE = "Expected format: owner/repo@ref (e.g., actions/checkout@v3)"
ERROR_RETRIEVING_SHA = "Error retrieving SHA for {}: {}"
ERROR_RETRIEVING_LATEST_RELEASE = "Error retrieving latest release for {}/{}: {}"
PRIVATE_OR_INVALID_ACTION_ERROR = "Action '{}' might be private or invalid. Skipping."

# Output formats
ORIGINAL_ACTION_FORMAT = "Original: {}"
PINNED_ACTION_FORMAT = "Pinned:   {}@{}"

# Regex patterns
ACTION_REGEX_PATTERN = r"([^/]+)/([^@]+)@(.+)"

# API URL formats
GITHUB_API_COMMITS_URL = "https://api.github.com/repos/{}/{}/commits/{}"
GITHUB_API_RELEASES_URL = "https://api.github.com/repos/{}/{}/releases/latest"
