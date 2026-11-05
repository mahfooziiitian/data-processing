---
name: documentation-content-enhancer
description: Enhances documentation under docs/ for clarity, completeness, structure, technical accuracy, and reader value while preserving the repository's Diataxis, MkDocs, naming, navigation, and diagram conventions. Use when asked to improve, enrich, rewrite, polish, or expand documentation content.
allowed-tools: shell
---

# Documentation content enhancer

Improve documentation as an editor and subject-matter reviewer, not as a
generic text generator. Preserve the author's intent and repository behavior;
make the smallest coherent change that materially improves the reader's
understanding or ability to use the content.

## Required workflow

1. **Identify the target and audience**
   - Read the complete target page and nearby linked pages before editing.
   - Determine whether the reader is learning, completing a task, looking up
     facts, or understanding design rationale.
   - Check the page's `diataxis:` frontmatter and folder against that purpose.
   - Inspect existing terminology, examples, links, diagrams, and navigation
     before adding new material.

2. **Choose the right content shape**
   - Keep one primary Diátaxis purpose per page.
   - Use tutorials for linear learning journeys with a working outcome.
   - Use how-to guides for one practical goal and justified branching steps.
   - Use reference pages for precise, structured, searchable facts.
   - Use explanation pages for concepts, context, trade-offs, alternatives,
     and design rationale.
   - If the requested content mixes purposes or is too large, split it into
     focused pages and cross-link them instead of creating a long mixed-mode
     page.

3. **Enhance the substance**
   - Add the context needed to answer what the concept is, why it matters,
     when to use it, and what its limitations are.
   - Make distinctions explicit when terms are commonly confused.
   - Add practical examples, assumptions, edge cases, and failure modes where
     they improve understanding.
   - For architecture or data-engineering content, cover relevant concerns
     such as latency, throughput, correctness, scalability, recoverability,
     cost, operational complexity, and ownership.
   - Tie abstract concepts back to this repository when a meaningful mapping
     exists; clearly label hypothetical or non-implemented examples.
   - Do not claim that code, infrastructure, integrations, or guarantees
     exist unless verified in the repository.

4. **Improve readability**
   - Start with a concise framing paragraph that tells the reader what the
     page covers and who it serves.
   - Use descriptive, consistently ordered headings.
   - Prefer short paragraphs, precise wording, and active voice.
   - Convert aligned plain-text data into Markdown tables and use lists only
     when items are genuinely parallel.
   - Put code in fenced blocks with an appropriate language identifier.
   - Explain non-obvious code, diagrams, assumptions, and output immediately
     around the example.
   - Avoid filler, repeated conclusions, unsupported superlatives, and
     interview-style claims presented as universal rules.

5. **Handle diagrams and links**
   - Use Mermaid for structural relationships and workflows.
   - Use D3 only for data-driven or interactive visualizations, reusing
     helpers in `docs/assets/js/d3-diagrams.js`.
   - Keep static assets under `docs/assets/{js,css,images}/`.
   - Add meaningful alt text and captions where images are used.
   - Verify relative links, anchors, code symbols, and page references.
   - Add every new page to `mkdocs.yml` navigation.

6. **Preserve repository conventions**
   - Keep Markdown filenames under `docs/` lowercase.
   - Preserve required frontmatter and the matching Diátaxis folder.
   - Do not remove `navigation.tabs`, `toc.integrate`, or
     `navigation.footer` from the Material theme configuration.
   - Do not commit `site/` or other generated build output.
   - Update related documentation when a renamed page, command, or convention
     makes an existing link or statement stale.

## Quality and accuracy checks

Before reporting completion:

```bash
uv run --group docs mkdocs build --strict
python3 .github/skills/diataxis-docs-audit/check_diataxis.py
git diff --check
```

Treat Diátaxis warnings as advisory: inspect the page and fix real
misclassification, but do not distort a valid explanation page merely to
silence a heuristic warning. Run the focused project tests when documentation
examples or repository behavior descriptions were changed. Remove `site/`
after validation if the build created it, unless it is already ignored.

## Enhancement checklist

- [ ] Audience and purpose are clear.
- [ ] Page remains in the correct Diátaxis quadrant.
- [ ] Content adds substance rather than repetition.
- [ ] Definitions, distinctions, assumptions, and trade-offs are explicit.
- [ ] Examples are technically honest and clearly labeled.
- [ ] Tables, code blocks, headings, links, and diagrams render correctly.
- [ ] New pages are included in navigation.
- [ ] Required MkDocs features remain enabled.
- [ ] Strict build, audit, and diff checks were run.
