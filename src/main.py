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

    # Create a mutually exclusive group for action arguments
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-a", dest="action", help=ACTION_ARG_HELP, required=False)
    group.add_argument("--action", dest="action", help=ACTION_ARG_HELP, required=False)
    group.add_argument("-f", dest="file", help=FILE_ARG_HELP, required=False)
    group.add_argument("--file", dest="file", help=FILE_ARG_HELP, required=False)

    parser.add_argument("-v", "--version", help=VERSION_ARG_HELP, action="store_true")

    return parser.parse_args(args)


def main() -> None:
    args: Namespace = parse_args()
    print(args)

    # Handle version flag
    if args.version:
        print(f"{PROGRAM_NAME} {VERSION}")
        sys.exit(0)

    # Get and display the SHA for the specified action
    if args.action:
        get_action_sha(args.action)
    elif args.file:
        pass
    else:
        # No action specified, show help
        print(NO_ACTION_ERROR)
        print(ACTION_EXAMPLE)
        sys.exit(1)


if __name__ == "__main__":
    main()
