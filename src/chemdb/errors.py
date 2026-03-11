"""Rich exceptions with resolution hints.

Every error renders as markdown in the MCP response, never raw tracebacks.
"""

from __future__ import annotations


class ChemdbError(Exception):
    """Base for all chemdb errors with a user-facing hint."""

    def __init__(self, message: str, hint: str = ""):
        self.hint = hint
        super().__init__(message)

    def to_markdown(self) -> str:
        parts = [f"⚠ {self}"]
        if self.hint:
            parts.append(f"  → {self.hint}")
        return "\n".join(parts)


class DbMissingError(ChemdbError):
    """Database has not been synced yet."""

    def __init__(self, schema: str):
        super().__init__(
            f"Database '{schema}' not found",
            hint=f"Run 'chemdb sync {schema}' to download the database",
        )


class DbCorruptError(ChemdbError):
    """Database exists but schema doesn't match."""

    def __init__(self, schema: str):
        super().__init__(
            f"Database '{schema}' has mismatched schema",
            hint=f"Run 'chemdb sync {schema} --force' to rebuild",
        )


class NoResultsError(ChemdbError):
    """Query returned zero results."""

    def __init__(self) -> None:
        super().__init__(
            "No results found",
            hint="Try broadening: drop a filter, widen a range, or remove query text",
        )


class IdNotFoundError(ChemdbError):
    """Identifier lookup returned nothing."""

    def __init__(self, id_str: str):
        super().__init__(
            f'No match for "{id_str}"',
            hint="Try name: prefix or check spelling.",
        )


class InvalidRangeError(ChemdbError):
    """Range string could not be parsed."""

    def __init__(self, field: str, raw: str):
        super().__init__(
            f'Could not parse {field}="{raw}"',
            hint=f'Expected: "5", "3..9", ">5", "<12"',
        )


class InvalidSortError(ChemdbError):
    """Unknown sort field."""

    def __init__(self, field: str, available: list[str]):
        avail = ", ".join(available)
        super().__init__(
            f'Unknown sort field "{field}"',
            hint=f"Available: {avail}",
        )
