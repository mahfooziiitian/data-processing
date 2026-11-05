#!/usr/bin/env python3
"""Heuristic Diataxis compliance checker for a docs/ tree.

Scans every Markdown file under docs/ (relative to the current working
directory, or a path given as the first argument), tries to classify it
into one of the four Diataxis quadrants (tutorial, how-to, reference,
explanation), and prints advisory warnings about likely mode-mixing.

This is a heuristic, text-based tool — not a strict linter. Treat its
output as signal to investigate, not as ground truth. See
.github/skills/diataxis-docs-audit/SKILL.md for how to act on its output.

Usage:
    python3 check_diataxis.py [docs_dir]

Exit code is 0 if no files are uncategorized and no warnings were raised,
1 otherwise (useful as a soft CI signal, but not intended to hard-fail a
build by default).
"""

from __future__ import annotations

import pathlib
import re
import sys

QUADRANTS = {"tutorial", "how-to", "reference", "explanation"}

FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)
FRONTMATTER_KEY_RE = re.compile(r"^diataxis:\s*([a-z-]+)\s*$", re.MULTILINE)

ORDERED_STEP_RE = re.compile(r"^\s*\d+\.\s+\S", re.MULTILINE)
NUMBERED_HEADING_RE = re.compile(r"^#{1,4}\s*\d+\.\s+\S", re.MULTILINE)
STEP_HEADING_RE = re.compile(r"^#{1,4}\s*step\b", re.MULTILINE | re.IGNORECASE)
HOWTO_HEADING_RE = re.compile(r"^#{1,4}\s*how to\b", re.MULTILINE | re.IGNORECASE)
WHY_MARKER_RE = re.compile(
    r"\b(why|trade-?off|alternative|instead of|rationale|in other words)\b",
    re.IGNORECASE,
)
TABLE_ROW_RE = re.compile(r"^\|.+\|\s*$", re.MULTILINE)
CODE_FENCE_RE = re.compile(r"^```", re.MULTILINE)


def split_frontmatter(text: str) -> tuple[dict[str, str], str]:
    match = FRONTMATTER_RE.match(text)
    if not match:
        return {}, text
    raw = match.group(1)
    body = text[match.end():]
    meta: dict[str, str] = {}
    key_match = FRONTMATTER_KEY_RE.search(raw)
    if key_match:
        meta["diataxis"] = key_match.group(1)
    return meta, body


def infer_quadrant(path: pathlib.Path, docs_root: pathlib.Path, meta: dict[str, str]) -> str | None:
    if meta.get("diataxis") in QUADRANTS:
        return meta["diataxis"]
    try:
        rel = path.relative_to(docs_root)
    except ValueError:
        rel = path
    if len(rel.parts) > 1:
        folder = rel.parts[0].lower()
        if folder in QUADRANTS:
            return folder
        if folder == "howto" or folder == "how_to":
            return "how-to"
    return None


def analyze(body: str) -> dict[str, int]:
    return {
        "ordered_steps": len(ORDERED_STEP_RE.findall(body)),
        "step_headings": len(STEP_HEADING_RE.findall(body)) + len(NUMBERED_HEADING_RE.findall(body)),
        "howto_headings": len(HOWTO_HEADING_RE.findall(body)),
        "why_markers": len(WHY_MARKER_RE.findall(body)),
        "table_rows": len(TABLE_ROW_RE.findall(body)),
        "code_fences": len(CODE_FENCE_RE.findall(body)) // 2,
    }


def warnings_for(quadrant: str | None, stats: dict[str, int]) -> list[str]:
    warnings: list[str] = []
    steps = stats["ordered_steps"] + stats["step_headings"]

    if quadrant is None:
        warnings.append(
            "Uncategorized: add a `diataxis:` frontmatter key or move under "
            "docs/<quadrant>/ so this page's purpose is explicit."
        )
        return warnings

    if quadrant == "tutorial":
        if steps < 2:
            warnings.append(
                "Tutorial has few/no numbered steps — tutorials should be a "
                "concrete, linear, step-by-step lesson."
            )
        if stats["why_markers"] >= 6:
            warnings.append(
                "Tutorial has many 'why/trade-off' markers — heavy rationale "
                "discussion belongs in an Explanation page, not a tutorial."
            )

    elif quadrant == "how-to":
        if steps < 1 and stats["howto_headings"] == 0:
            warnings.append(
                "How-to guide has no numbered steps or 'How to ...' heading — "
                "how-to guides should give actionable steps for one task."
            )
        if stats["why_markers"] >= 8:
            warnings.append(
                "How-to guide has many 'why/trade-off' markers — consider "
                "moving background rationale to an Explanation page."
            )

    elif quadrant == "reference":
        if stats["why_markers"] >= 4:
            warnings.append(
                "Reference page has several 'why/trade-off' markers — "
                "reference material should be dry/descriptive, not "
                "persuasive or narrative."
            )
        if stats["table_rows"] == 0 and stats["code_fences"] == 0:
            warnings.append(
                "Reference page has no tables or code blocks — reference "
                "pages are usually structured data (tables, signatures, "
                "schemas), not prose."
            )
        if steps >= 4:
            warnings.append(
                "Reference page has many numbered steps — sequential "
                "instructions usually belong in a how-to guide, not "
                "reference material."
            )

    elif quadrant == "explanation":
        if stats["ordered_steps"] >= 6:
            warnings.append(
                "Explanation page has many numbered steps — this may "
                "actually be a how-to guide or tutorial in disguise."
            )
        if stats["why_markers"] == 0:
            warnings.append(
                "Explanation page has no 'why/trade-off' markers — make "
                "sure it actually discusses rationale/background, not just "
                "restates facts (which would belong in reference)."
            )

    return warnings


def main() -> int:
    docs_root = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "docs").resolve()
    if not docs_root.is_dir():
        print(f"error: {docs_root} is not a directory", file=sys.stderr)
        return 2

    files = sorted(docs_root.rglob("*.md"))
    if not files:
        print(f"No Markdown files found under {docs_root}")
        return 0

    had_issue = False
    rows: list[tuple[str, str, str]] = []

    for path in files:
        naming_issue = None
        if path.name != "README.md" and path.name.lower() != path.name:
            naming_issue = (
                f"Filename '{path.name}' is not lowercase — docs/ Markdown "
                "filenames must be lowercase (README.md is the only exception)."
            )

        if path.name.lower() == "index.md":
            # Landing pages are intentionally outside the four quadrants.
            rows.append(
                (str(path.relative_to(docs_root)), "landing page", naming_issue or "-")
            )
            if naming_issue:
                had_issue = True
            continue

        text = path.read_text(encoding="utf-8")
        meta, body = split_frontmatter(text)
        quadrant = infer_quadrant(path, docs_root, meta)
        stats = analyze(body)
        issues = warnings_for(quadrant, stats)
        if naming_issue:
            issues.append(naming_issue)

        if issues:
            had_issue = True
        rows.append(
            (
                str(path.relative_to(docs_root)),
                quadrant or "UNCATEGORIZED",
                "; ".join(issues) if issues else "-",
            )
        )

    width_file = max(len(r[0]) for r in rows) + 2
    width_quad = max(len(r[1]) for r in rows) + 2
    print(f"{'File':<{width_file}}{'Quadrant':<{width_quad}}Warnings")
    print("-" * (width_file + width_quad + 40))
    for file_, quadrant, issues in rows:
        print(f"{file_:<{width_file}}{quadrant:<{width_quad}}{issues}")

    return 1 if had_issue else 0


if __name__ == "__main__":
    raise SystemExit(main())
