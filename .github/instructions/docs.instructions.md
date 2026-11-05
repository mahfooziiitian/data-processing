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
- Markdown filenames under `docs/` must be **lowercase** (e.g.
  `architecture.md`, `setup.md`, `concepts.md`), not `UPPERCASE.md` —
  this keeps links/paths consistent across OSes and with the
  `docs/<quadrant>/` folder convention above. `README.md` is the sole
  repo-wide exception (GitHub convention expects it uppercase); a
  `SKILL.md` under `.github/skills/*/` is also exempt since the skill
  filename is required by the Copilot CLI skill spec, not a `docs/` page.
- Adding a new page under `docs/` requires also adding it to the `nav:`
  list in `mkdocs.yml`, or it won't appear in the site navigation.
- **Diagrams**: use fenced ` ```mermaid ` code blocks for structural/flow
  diagrams (flowcharts, sequence/state/class) — enabled via
  `pymdownx.superfences.custom_fences` in `mkdocs.yml`, no extra files
  needed. For data-driven custom visualizations, use D3.js (v7, loaded
  from CDN via `extra_javascript`): add a `<div id="...">` plus an inline
  `<script>` calling a helper from `docs/javascripts/d3-diagrams.js` (add
  new reusable helpers there rather than duplicating D3 boilerplate per
  page). See `docs/explanation/architecture.md` for both patterns in use.
  Prefer plain ASCII diagrams in prose for quick sketches; reach for
  Mermaid/D3 when a diagram benefits from being interactive or rendered
  from real data.
- Validate changes with `uv run --group docs mkdocs build --strict` (fails
  the build on broken links/nav entries) before considering a docs change
  complete; preview with `uv run --group docs mkdocs serve`.
- Keep `docs/index.md` (site home) and the root `README.md` roughly in
  sync for the quickstart section — `README.md` is GitHub-facing,
  `docs/index.md` is site-facing, and both should reflect the same
  commands.
