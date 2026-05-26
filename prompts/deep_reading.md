# Deep Reading Prompt

Use this prompt when dispatching agents for Phase 4 deep reading. One agent invocation per 2-3 papers is a good default when parallel execution is available.

---

## Task

Write detailed Chinese reading notes for the assigned papers based on full-text reading of their Markdown files.

Also write one compact sibling `.meta.md` retrieval card per paper.

## Template

Read `templates/论文精读模板.md` first and follow its structure exactly.

Required output elements:
1. YAML frontmatter with all metadata fields filled
2. Structured note sections in the exact template order
3. Source-grounded findings, methods, formulas, and limitations
4. Traceability links back to Zotero, DOI, PDF path, and Markdown path

## Quality Requirements

### Must Include

- Specific numbers such as event frequencies, exposure person-days, mortality counts, percentage changes, and confidence intervals when present
- Method details such as model names, spatial or temporal resolution, thresholds, algorithms, and validation metrics
- Key formulas with symbol explanations and step mapping when present
- Direct quotes from the paper with page or section markers when useful
- Exact dataset names, versions, or sources mentioned by the paper

### Must Not

- Fabricate details not in the paper
- Use only the abstract
- Skip template sections without explanation
- Write the full note in English except for direct quotes

If information is truly missing, say so plainly.

## Output Location

Write the full note to:

```text
04_deep_reading_notes/<filename>.md
```

Then write the sibling retrieval card to:

```text
04_deep_reading_notes/<filename>.meta.md
```

## `.meta.md` Card Format

Keep the card compact, ideally within 800 Chinese characters. Use exactly these sections:

1. `研究目标与核心假说`
2. `关键变量与识别逻辑`
3. `出图思路与图表释义`
4. `核心结论与研究局限`

The card must be extracted from the full note or source paper only. Do not invent missing information.

## Length

Aim for roughly 2000-4000 Chinese words per full note unless the source paper is unusually short.

## Parallel Processing

When processing multiple papers, use parallel agent calls if the runtime supports them, dispatching 2-3 papers per agent. If no parallel tool is available, process papers sequentially with one output pair per paper.

## Paper Assignments

[INSERT SPECIFIC PAPER ASSIGNMENTS HERE]
