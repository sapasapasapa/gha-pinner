#!/usr/bin/env python3

import sys
from argparse import ArgumentParser, Namespace

from common.constants import (
    ACTION_ARG_HELP,
    ACTION_EXAMPLE,
    FILE_ARG_HELP,
    NO_ACTION_ERROR,
    PROGRAM_DESCRIPTION,
    PROGRAM_NAME,
    VERSION,
    VERSION_ARG_HELP,
)
from retriever import get_action_sha


def parse_args(args=None) -> Namespace:
    parser = ArgumentParser(description=PROGRAM_DESCRIPTION)

    # Add arguments with flags
    parser.add_argument("-a", "--action", help=ACTION_ARG_HELP, required=False)

    parser.add_argument("-f", "--file", help=FILE_ARG_HELP, required=False)

    parser.add_argument("-v", "--version", help=VERSION_ARG_HELP, action="store_true")

    return parser.parse_args(args)


def main() -> None:
    args: Namespace = parse_args()
    print(args)

    # Handle version flag
    if args.version:  # args[2] is has_version
        print(f"{PROGRAM_NAME} {VERSION}")
        sys.exit(0)

    # Get and display the SHA for the specified action
    if args.action:  # args[0] is has_action
        # Extract the actual action from sys.argv
        action_index: int = sys.argv.index("-a" if "-a" in sys.argv else "--action") + 1
        action: str = sys.argv[action_index]
        get_action_sha(action)
    elif args.file:
        pass
    else:
        # No action specified, show help
        print(NO_ACTION_ERROR)
        print(ACTION_EXAMPLE)
        sys.exit(1)


if __name__ == "__main__":
    main()
