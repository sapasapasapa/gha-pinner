from enum import Enum


class ActionStatus(Enum):
    NEEDS_PINNING = "needs_pinning"
    ALREADY_PINNED = "already_pinned"
    SKIPPED = "skipped"
    ERROR = "error"
