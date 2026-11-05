---
name: diataxis-docs-audit
description: Audits and enforces the Diataxis documentation framework (tutorials, how-to guides, reference, explanation) for files under docs/. Use when asked to review, restructure, classify, create, or "check Diataxis compliance" for anything in docs/.
allowed-tools: shell
---

# Diataxis documentation audit

[Diataxis](https://diataxis.fr) is a documentation framework built around
one idea: a documentation page should serve **exactly one** of four
purposes, because each purpose implies a different writing mode. Mixing
modes on one page is the most common cause of documentation that is hard
to use and hard to maintain.

| Quadrant | User need | Writing mode | Example trigger phrase |
| --- | --- | --- | --- |
| **Tutorial** | "Teach me, I'm new" (learning-oriented) | A concrete, numbered, guaranteed-to-work lesson. First-person plural ("we'll"), minimal choices, minimal "why". | "Getting started", "Your first pipeline run" |
| **How-to guide** | "Help me do this specific thing" (goal-oriented) | Imperative steps assuming prior competence. Addresses one real-world task, may branch ("if X, do Y"). | "How to add a new source table", "How to reset the database" |
| **Reference** | "Tell me the facts" (information-oriented) | Dry, structured, exhaustive description: tables, signatures, schemas. No narrative, no opinions. | "Configuration options", "Schema reference", "CLI flags" |
| **Explanation** | "Help me understand" (understanding-oriented) | Discursive prose about *why* — design decisions, trade-offs, alternatives, background/theory. No steps to follow. | "Why we chose X over Y", "Architecture", "Concepts" |

A fifth, non-Diataxis category — the **landing/overview page** (e.g. an
`index.md` that links out to the other four) — is fine and expected; it
should mostly be a short map, not itself fall into one of the four modes.

## Current mapping in this repo (verify before trusting — docs/ evolves)

`docs/` is organized into quadrant subfolders, each file carrying a
matching `diataxis:` frontmatter key:

| File | Quadrant | Why |
| --- | --- | --- |
| `docs/index.md` | Landing page | Overview + links out, not a lesson/task/reference/theory page itself |
| `docs/tutorials/setup.md` | Tutorial | Numbered, linear, "do this then this" first-run walkthrough |
| `docs/explanation/architecture.md` | Explanation | Discusses design/data-flow rationale, not actionable steps |
| `docs/explanation/concepts.md` | Explanation | Teaches concepts (ETL, Lambda, Kappa, Data mesh, ...) with no steps to execute |

`docs/how-to/` and `docs/reference/` exist (currently empty, holding only
a `.gitkeep`) — they're reserved for content such as "how to add a new
ETL source", "how to reset the demo database", or a `schema.sql`/CLI
reference page. Don't invent content for them unprompted; only fill them
in when the user asks for that specific guide/reference.

## How to audit docs/

1. Run the heuristic checker from the repo root:

   ```bash
   python3 .github/skills/diataxis-docs-audit/check_diataxis.py
   ```

   It scans every `docs/**/*.md`, infers each file's quadrant (from YAML
   frontmatter `diataxis: tutorial|how-to|reference|explanation` if
   present, else from a `docs/<quadrant>/...` subfolder, else
   "uncategorized"), and prints a report flagging:
   - files with no assigned quadrant,
   - tutorials/how-tos with no numbered step sequence,
   - reference pages with heavy narrative ("why"/"trade-off" prose),
   - explanation pages that read like a step-by-step how-to instead,
   - non-lowercase filenames (except `README.md`).

2. Treat the script's output as **advisory signal, not a hard gate** —
   it uses simple text heuristics and will have false positives/negatives.
   Always re-read the flagged file yourself before acting on a warning.

3. For each real issue found, prefer the smallest fix:
   - A page mixing two modes → split the offending section into its own
     page (e.g. pull a "why we did X" aside out of a how-to into
     explanation/concepts.md), and cross-link the two.
   - A page with the wrong mode for its stated purpose → rewrite in the
     correct mode rather than moving it, if the content/location is
     otherwise right.
   - An uncategorized page → either add a `diataxis:` frontmatter key or
     move it under a `docs/<quadrant>/` subfolder consistent with the
     rest of the project (ask the user before introducing subfolders —
     it's a bigger structural change than relabeling).

4. After any restructuring, update `mkdocs.yml`'s `nav:` and
   `.github/instructions/docs.instructions.md`, then validate with
   `uv run --group docs mkdocs build --strict` before committing.
