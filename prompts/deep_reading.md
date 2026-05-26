# Deep Reading Agent Prompt

Use this prompt when dispatching agents for Phase 4 (deep reading). One agent invocation per 2-3 papers for optimal parallel processing.

---

## Task

Write DETAILED Chinese reading notes for the assigned papers based on FULL-TEXT reading of their Markdown files.

## Template

Read `templates/论文精读模板.md` FIRST. Follow its structure EXACTLY:

1. **YAML frontmatter** — all 10 metadata fields filled
2. **基本信息** — table with author, year, source, topic, link
3. **分类判断** — classification tag + basis
4. **一句话摘要** — one Chinese sentence: who, what method, what finding
5. **研究对象** — object, core question, context/scope
6. **研究方法** — method type, overall approach, rationale, detailed analysis with formula breakdowns
7. **数据来源** — data type, sample, time range, sample size, limitations
8. **研究结论** — 5-8 pairs of "主要发现 N" + "原文引用 N" with direct English quotes and page/section references
9. **我的判断** — most inspiring point, transferable methods, follow-up questions, relevance to my research
10. **原始语料** — Zotero link, DOI, PDF path, Markdown path
11. **摘要原文** — full original abstract

## Quality Requirements

### Must Include
- **Specific numbers**: event frequencies, exposure person-days, mortality counts, percentage changes, confidence intervals
- **Method details**: model names, spatial/temporal resolution, thresholds, algorithms, validation metrics (R², RMSE)
- **Formulas**: key equations with symbol explanations and step mapping (use LaTeX `$$` blocks)
- **Direct quotes**: original English text from the paper with page/section markers, paired with Chinese findings
- **Data sources**: exact dataset names, versions, URLs from the paper

### Must NOT
- Fabricate details not in the paper
- Use only the abstract — read the FULL Markdown
- Skip template sections — if information is truly missing, state "论文正文未提供，需查补充材料"
- Write in English (except for direct quotes in 原文引用)

## Length

2000-4000 words per note (Chinese). The note should be comprehensive enough that another researcher could understand the paper's full methodology and findings without reading the original.

## Output Location

Write to `04_deep_reading_notes/<filename>.md` using the same filename stem as the corresponding file in `03_reading_notes/`.

## Parallel Processing

When processing multiple papers, use background or parallel agent calls if the runtime supports them, dispatching 2-3 papers per agent. If no parallel agent tool is available, process papers sequentially with the same assignment structure and keep one output file per paper.

## Paper Assignments

[INSERT SPECIFIC PAPER ASSIGNMENTS HERE — one per Agent invocation]
