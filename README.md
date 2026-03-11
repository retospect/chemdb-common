# chemdb-common

Shared library for chemistry database MCP servers. Provides SQLAlchemy models, sync utilities, and CLI tools used by `grandmofty-mcp` and `catapult-mcp`.

## Features

- **Pydantic models** — typed schemas for MOFs, reactions, isotherms
- **SQLAlchemy ORM** — SQLite and PostgreSQL support
- **Sync framework** — pull data from remote APIs (mofdb-client, Zenodo, Materials Project)
- **CLI** — `chemdb` command for database management

## Installation

```bash
uv pip install -e .
# With PostgreSQL support:
uv pip install -e ".[postgres]"
```

## Usage

```bash
chemdb sync          # sync all data sources
chemdb stats         # show database statistics
```

## Dependencies

- **pydantic** — data validation
- **sqlalchemy** — ORM
- **typer** — CLI framework
- **httpx** — HTTP client for API calls

## License

LGPL-3.0-or-later — see [LICENSE](LICENSE).
