# Deep Reading Agent Prompt

Use this prompt when dispatching agents for Phase 4 (deep reading). One agent invocation per 2-3 papers for optimal parallel processing.

---

## Task

Write DETAILED Chinese reading notes for the assigned papers based on FULL-TEXT reading of their Markdown files.
**Crucially, also automatically generate an ultra-lightweight `.meta.md` metadata card for each paper in the same output directory to facilitate extremely fast, low-token cross-paper comparisons later.**

## Template

Read `templates/论文精读模板.md` FIRST. Follow its structure EXACTLY for the main reading note (`<filename>.md`):

1. **YAML frontmatter** — all 10 metadata fields filled
2. **基本信息** — table with author, year, source, topic, link
3. **一句话摘要** — one Chinese sentence: who, what method, what finding
4. **研究对象** — object, core question, context/scope
5. **研究方法** — method type, overall approach, rationale, detailed analysis with formula breakdowns
6. **数据来源** — data type, sample, time range, sample size, limitations
7. **关键图表设计与作者释义** — **[IMPORTANT]** Extract the paper's figures/tables design logic (how they serve the research goals), core captions/legends (which figures/tables were produced), and how the author explains/discusses these figures/tables in the body text.
8. **研究结论** — 5-8 pairs of "主要发现 N" + "原文引用 N" with direct English quotes and page/section references
9. **我的判断** — most inspiring point, transferable methods, follow-up questions, relevance to my research

## Metadata Card (.meta.md) Requirements

For each paper, you MUST also generate a corresponding `<filename>.meta.md` card file. It must be highly condensed (strictly under 800 words, written in Chinese) with the following structure:
```markdown
# 元数据卡片: [Paper Title]

- **研究目标与核心假说**：一句话点明该论文要解决的核心问题。
- **关键变量与识别逻辑**：说明核心自变量、因变量、中介/控制变量，以及核心识别设计（如模型/方法学）。
- **出图思路与图表释义**：结合图例列出作者为支撑研究目标而设计的关键图表，并高度浓缩正文中作者对这些图表的具体解释逻辑。
- **核心结论与研究局限**：列出最核心的研究发现和提及的方法/数据局限性。
```

## Quality Requirements

### Must Include
- **Specific numbers**: event frequencies, exposure person-days, mortality counts, percentage changes, confidence intervals
- **Method details**: model names, spatial/temporal resolution, thresholds, algorithms, validation metrics (R², RMSE)
- **Formulas**: key equations with symbol explanations and step mapping (use LaTeX `$$` blocks)
- **Direct quotes**: original English text from the paper with page/section markers, paired with Chinese findings
- **Data sources**: exact dataset names, versions, URLs from the paper
- **Figure design & explanations**: complete breakdown of the author's visualization logic and textual explanations of figures/tables

### Must NOT
- Fabricate details not in the paper
- Use only the abstract — read the FULL Markdown
- Skip template sections — if information is truly missing, state "论文正文未提供，需查补充材料"
- Write in English (except for direct quotes in 原文引用)

## Length

- **Main reading note (`.md`)**: 2000-4000 words (Chinese). The note should be comprehensive enough that another researcher could understand the paper's full methodology and findings without reading the original.
- **Metadata Card (`.meta.md`)**: strictly under 800 words (Chinese) to enable low-token batch comparison.

## Output Location

- Main note: Write to `04_deep_reading_notes/<filename>.md` using the same filename stem as the corresponding file in `03_reading_notes/`.
- Metadata card: Write to `04_deep_reading_notes/<filename>.meta.md`.

## Parallel Processing

When processing multiple papers, use background or parallel agent calls if the runtime supports them, dispatching 2-3 papers per agent. If no parallel agent tool is available, process papers sequentially with the same assignment structure and keep one output file per paper.

## Paper Assignments

[INSERT SPECIFIC PAPER ASSIGNMENTS HERE — one per Agent invocation]
