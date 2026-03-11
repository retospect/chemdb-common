"""Sort-string parser.

Format: comma-separated field names. Prefix ``!`` for descending.
First field is primary sort, subsequent break ties.

Examples:
  "lcd"            → LCD ascending
  "!lcd"           → LCD descending
  "!lcd,sa"        → LCD desc, then SA asc
  "relevance"      → FTS rank (only when query is non-empty)
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SortField:
    name: str
    descending: bool = False

    def to_sql(self) -> str:
        direction = "DESC" if self.descending else "ASC"
        return f"{self.name} {direction}"


def parse_sort(s: str, valid_fields: set[str]) -> list[SortField]:
    """Parse a sort string into a list of ``SortField``.

    ``valid_fields`` should include ``"relevance"`` if FTS is active.

    Raises ``ValueError`` if an unknown field is encountered.
    """
    if not s.strip():
        return []

    fields = []
    for part in s.split(","):
        part = part.strip()
        if not part:
            continue
        desc = part.startswith("!")
        name = part.lstrip("!")
        if name not in valid_fields:
            avail = ", ".join(sorted(valid_fields))
            raise ValueError(f'Unknown sort field "{name}". Available: {avail}')
        fields.append(SortField(name=name, descending=desc))
    return fields
