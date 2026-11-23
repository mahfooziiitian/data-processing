# Agent instructions

This repository is a Python/pandas data-engineering proof of concept with
ETL, Kappa, Lambda, and Data Mesh demos backed by local PostgreSQL.

## Shared guidance

Read `.github/copilot-instructions.md` for repository architecture and
commands. Before modifying files, read the matching path-specific guidance:

| Scope | Instructions |
| --- | --- |
| `src/data_proc/etl/` | `.github/instructions/etl.instructions.md` |
| `src/data_proc/kappa/` | `.github/instructions/kappa.instructions.md` |
| `src/data_proc/lambda_arch/` | `.github/instructions/lambda.instructions.md` |
| `src/data_proc/data_mesh/` | `.github/instructions/data-mesh.instructions.md` |
| `examples/` | `.github/instructions/examples.instructions.md` |
| `tests/` | `.github/instructions/tests.instructions.md` |
| `sql/schema.sql`, `infra/`, `.env.example` | `.github/instructions/database.instructions.md` |
| `docs/`, `mkdocs.yml` | `.github/instructions/docs.instructions.md` |

These are ordinary Markdown instructions; follow their content regardless
of whether the agent automatically loads Copilot's path-specific format.
For documentation work, follow the applicable workflows in
`.github/skills/`; invoke the skills when the client supports them, or
read their `SKILL.md` files and perform the same checks otherwise.

## Working and validation

- Preserve unrelated working-tree changes. Keep reusable logic in
  `src/data_proc/`, runnable orchestration in `examples/`, and DDL in
  `sql/schema.sql`.
- Run Python through `uv run`. Use `uv sync --all-groups` when dependencies
  need installation; run focused tests with `uv run pytest` and broaden as
  appropriate. Tests use temporary files, in-memory SQLite, and mocked HTTP;
  they do not require Docker or live APIs.
- For documentation changes, run `uv run --group docs mkdocs build --strict`,
  `uv run python .github/skills/diataxis-docs-audit/check_diataxis.py`, and
  `git diff --check`. The Diátaxis checker reports advisory warnings with a
  nonzero exit; inspect rather than automatically rewriting flagged pages.
- Do not reset database volumes, delete user data, start services, or call
  external APIs without permission. `docker compose --project-directory . -f infra/docker-compose.yml down -v` and `make clean`
  remove the database volume. SQLite tests do not establish PostgreSQL
  integration correctness.
