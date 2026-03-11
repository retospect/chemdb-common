"""Range-string parser using ``..`` delimiter.

Supports:
  "5"        → exact
  "3..9"     → closed range
  "5.."      → open lower (≥ 5)
  "..9"      → open upper (≤ 9)
  ">5"       → greater than
  "<12"      → less than

The ``..`` delimiter avoids ambiguity with negative numbers:
  "-1.5..0"  → range from −1.5 to 0
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto


class RangeOp(Enum):
    EXACT = auto()
    CLOSED = auto()
    GTE = auto()
    LTE = auto()
    GT = auto()
    LT = auto()


@dataclass(frozen=True)
class ParsedRange:
    op: RangeOp
    low: float | None = None
    high: float | None = None
    value: float | None = None

    def matches(self, v: float) -> bool:
        """Test whether *v* satisfies this range."""
        if self.op is RangeOp.EXACT:
            return v == self.value
        if self.op is RangeOp.CLOSED:
            return self.low <= v <= self.high  # type: ignore[operator]
        if self.op is RangeOp.GTE:
            return v >= self.low  # type: ignore[operator]
        if self.op is RangeOp.LTE:
            return v <= self.high  # type: ignore[operator]
        if self.op is RangeOp.GT:
            return v > self.value  # type: ignore[operator]
        if self.op is RangeOp.LT:
            return v < self.value  # type: ignore[operator]
        return False  # pragma: no cover

    def to_sql_clause(self, column: str) -> tuple[str, dict[str, float]]:
        """Return a SQL WHERE fragment and parameter dict.

        Example: ``("lcd >= :lcd_lo AND lcd <= :lcd_hi", {"lcd_lo": 3, "lcd_hi": 9})``
        """
        if self.op is RangeOp.EXACT:
            return f"{column} = :{column}_eq", {f"{column}_eq": self.value}
        if self.op is RangeOp.CLOSED:
            return (
                f"{column} >= :{column}_lo AND {column} <= :{column}_hi",
                {f"{column}_lo": self.low, f"{column}_hi": self.high},
            )
        if self.op is RangeOp.GTE:
            return f"{column} >= :{column}_lo", {f"{column}_lo": self.low}
        if self.op is RangeOp.LTE:
            return f"{column} <= :{column}_hi", {f"{column}_hi": self.high}
        if self.op is RangeOp.GT:
            return f"{column} > :{column}_gt", {f"{column}_gt": self.value}
        if self.op is RangeOp.LT:
            return f"{column} < :{column}_lt", {f"{column}_lt": self.value}
        raise ValueError(f"Unknown op: {self.op}")  # pragma: no cover


def parse_range(s: str) -> ParsedRange:
    """Parse a range string into a ``ParsedRange``.

    Raises ``ValueError`` on unparseable input.
    """
    s = s.strip()
    if not s:
        raise ValueError("Empty range string")

    # >N, <N
    if s.startswith(">") and not s.startswith(">="):
        return ParsedRange(op=RangeOp.GT, value=float(s[1:]))
    if s.startswith("<") and not s.startswith("<="):
        return ParsedRange(op=RangeOp.LT, value=float(s[1:]))
    if s.startswith(">="):
        return ParsedRange(op=RangeOp.GTE, low=float(s[2:]))
    if s.startswith("<="):
        return ParsedRange(op=RangeOp.LTE, high=float(s[2:]))

    # ..N (open upper)
    if s.startswith(".."):
        return ParsedRange(op=RangeOp.LTE, high=float(s[2:]))

    # N.. (open lower) or N..M (closed)
    if ".." in s:
        parts = s.split("..", 1)
        left, right = parts[0], parts[1]
        if right == "":
            return ParsedRange(op=RangeOp.GTE, low=float(left))
        return ParsedRange(op=RangeOp.CLOSED, low=float(left), high=float(right))

    # Exact value
    return ParsedRange(op=RangeOp.EXACT, value=float(s))
