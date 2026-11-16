"""CLI 경계에서 종료 코드로 바꾸는 오류."""


class ToolError(Exception):
    exit_code = 2


class InputError(ToolError):
    exit_code = 2


class OutputConflict(ToolError):
    exit_code = 3


class Unavailable(ToolError):
    exit_code = 4


class IoFailure(ToolError):
    exit_code = 5
