from argparse import Namespace
from dataclasses import dataclass

import pytest

from src.main import parse_args


@dataclass(frozen=True)
class ParseArgsParams:
    args: list[str]
    expected_result: list[bool]


ACTION_FLAG = ParseArgsParams(
    args=["-a", "actions/checkout@v3"],
    expected_result=Namespace(action="actions/checkout@v3", file=None, version=False),
)
ACTION_LONG_FLAG = ParseArgsParams(
    args=["--action", "actions/checkout@v3"],
    expected_result=Namespace(action="actions/checkout@v3", file=None, version=False),
)
FILE_FLAG = ParseArgsParams(
    args=["-f", "path/to/file.yml"],
    expected_result=Namespace(action=None, file="path/to/file.yml", version=False),
)
FILE_LONG_FLAG = ParseArgsParams(
    args=["--file", "path/to/file.yml"],
    expected_result=Namespace(action=None, file="path/to/file.yml", version=False),
)
VERSION_FLAG = ParseArgsParams(
    args=["-v"], expected_result=Namespace(action=None, file=None, version=True)
)
VERSION_LONG_FLAG = ParseArgsParams(
    args=["--version"], expected_result=Namespace(action=None, file=None, version=True)
)
MULTIPLE_FLAGS = ParseArgsParams(
    args=["-a", "actions/checkout@v3", "-v"],
    expected_result=Namespace(action="actions/checkout@v3", file=None, version=True),
)


@pytest.mark.parametrize(
    "test_args",
    [
        ACTION_FLAG,
        ACTION_LONG_FLAG,
        FILE_FLAG,
        FILE_LONG_FLAG,
        VERSION_FLAG,
        VERSION_LONG_FLAG,
        MULTIPLE_FLAGS,
    ],
)
def test_parse_args(test_args: ParseArgsParams) -> None:
    result = parse_args(test_args.args)
    assert not (result.action is not None and result.file is not None)
    assert result == test_args.expected_result
