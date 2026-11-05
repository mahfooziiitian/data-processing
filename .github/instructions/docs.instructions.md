---
applyTo: "docs/**/*.md,mkdocs.yml"
---

# Documentation site conventions

- Files under `docs/` are both plain-Markdown reference docs and the
  source for the MkDocs (Material theme) site defined in `mkdocs.yml`
  (`docs_dir: docs`).
- `docs/` is organized by [Diataxis](https://diataxis.fr) quadrant:
  `docs/tutorials/` (learning-oriented, numbered walkthroughs),
  `docs/how-to/` (goal-oriented task guides), `docs/reference/`
  (dry, structured facts/tables), `docs/explanation/` (discursive
  "why"/design-rationale prose). `docs/index.md` is the one exception —
  it's a landing page that links out, not a quadrant page itself. New
  pages should go in the matching subfolder and carry a `diataxis: ...`
  frontmatter key; use the `diataxis-docs-audit` skill
  (`.github/skills/diataxis-docs-audit/`) to check a page's fit.
- Adding a new page under `docs/` requires also adding it to the `nav:`
  list in `mkdocs.yml`, or it won't appear in the site navigation.
- Validate changes with `uv run --group docs mkdocs build --strict` (fails
  the build on broken links/nav entries) before considering a docs change
  complete; preview with `uv run --group docs mkdocs serve`.
- Keep `docs/index.md` (site home) and the root `README.md` roughly in
  sync for the quickstart section — `README.md` is GitHub-facing,
  `docs/index.md` is site-facing, and both should reflect the same
  commands.
