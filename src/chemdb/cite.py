"""Citation formatting — [@doi] + source database."""

from __future__ import annotations


def format_citation(doi: str | None, source: str = "") -> str:
    """Format a citation line.

    Returns e.g. ``📎 Li et al. [@10.1126/science.283.5405.1148] via CoRE MOF``
    """
    parts = []
    if doi:
        parts.append(f"[@{doi}]")
    if source:
        parts.append(f"via {source}")
    if not parts:
        return ""
    return "📎 " + " ".join(parts)
