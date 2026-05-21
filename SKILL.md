---
name: zotero-vault-batch-reading
description: 'Two-tier Zotero batch reading workflow. Phase 1-2 script: PDF to Markdown plus auto skim notes in 03_reading_notes. Phase 3-4 Claude: research-context-aware paper recommendation plus full-text deep reading notes in 04_deep_reading_notes. Use when processing a Zotero collection into structured Chinese reading notes, or when the user mentions batch read Zotero, 论文精读, 泛读, or processing a collection.'
---

# Zotero Vault Batch Reading

Two-tier batch reading workflow for Zotero collections: **skim** (auto-generated from metadata + abstracts → `03_reading_notes/`) then **deep** (Claude full-text analysis → `04_deep_reading_notes/`), with research-context-aware paper recommendation.

## Workflow Overview

```
Phase 0: Onboarding    → Claude asks about user's research context
Phase 1: Prepare       → Script: Zotero API → metadata → PDF → Markdown
Phase 2: Skim (03)     → Script: auto-generate structured notes from metadata + abstracts
Phase 3: Recommend     → Claude: score papers against research context, user decides
Phase 4: Deep (04)     → Claude: full-text reading → detailed notes with formulas & quotes
Phase 5: Overview      → Dual-layer index with 03/04 links
```

### Key Principle

**The script handles mechanical work** (Phase 1-2). **Claude handles intellectual work** (Phase 0, 3-4, 5). The script's auto-generated notes are explicitly labeled as **泛读 (skim)** — they provide quick orientation but mark gaps as "需查全文". Only Claude's full-text analysis produces genuine **精读 (deep)** notes.

## When to Use

Invoke this skill when:
- User wants to process a Zotero collection into structured reading notes
- User mentions "批量精读", "Zotero批处理", "论文泛读", "文献整理"
- User asks to read papers from a Zotero category
- User mentions a collection name like "ES", "复合灾害", etc.

## Phase 0: Onboarding (Claude)

**Before running any script**, gather the user's research context.

### Context Sources (priority order)
1. `CLAUDE.md` / `GEMINI.md` / `AGENTS.md` in the current workspace
2. Memory files at `.claude/projects/<project>/memory/`
3. Direct questions to the user

### What to Collect
See `prompts/onboarding.md` for the full interview template. Minimum:
- Research topic and compound hazards of interest
- Geographic focus
- Research dimension (exposure / health burden / projection / mechanisms / policy)
- Key variables
- Deep reading strategy: **recommend** (default), **all-core**, or **all**

### If User Declines to Answer
Use default heuristics: recommend papers with matching keywords (compound + heat + PM2.5/ozone + mortality/exposure), deprioritize pure climatology or unrelated hazards.

## Phase 1: Prepare (Script)

Run the collection-to-Markdown pipeline:

```powershell
python "$SKILL_DIR\scripts\run_zotero_vault_batch_reading.py" `
  --collection-key <KEY> `
  --collection-name "<NAME>" `
  --output-root "<OUTPUT>" `
  --mode prepare
```

**What it does:**
- Connects to Zotero local API (`http://127.0.0.1:23119`)
- Fetches all top-level items in the collection with paginated Zotero API calls
- Locates attached PDFs and copies them to `01_original_pdf/`
- Converts each PDF to Markdown via PyMuPDF → `02_original_md/`
- Saves metadata to `_workflow/collection_items.json`

**Prerequisites:** Zotero Desktop running with local API enabled.

## Phase 2: Skim / 泛读 (Script)

Generate auto notes for ALL papers:

```powershell
python "$SKILL_DIR\scripts\run_zotero_vault_batch_reading.py" `
  --collection-key <KEY> `
  --collection-name "<NAME>" `
  --output-root "<OUTPUT>" `
  --mode skim
```

Or run both phases at once:

```powershell
python "$SKILL_DIR\scripts\run_zotero_vault_batch_reading.py" `
  --collection-key <KEY> `
  --collection-name "<NAME>" `
  --output-root "<OUTPUT>" `
  --mode all
```

**What it does:**
- For each paper: reads Zotero metadata (title, abstract, authors, year, DOI)
- Classifies papers: `核心复合灾害` or `支撑背景` (keyword-based)
- Generates structured skim notes with the script renderer, after validating the required headings in `templates/论文精读模板.md`
- Output to `03_reading_notes/` — explicitly labeled as **泛读**
- Generates `00_collection_overview.md` with item index
- Generates `_ProcessLog_进度记录.md`

**Skim note characteristics (~5-10 KB each):**
- Structured sections filled from metadata + abstract
- Methodology/data details may be incomplete
- Gaps explicitly marked: "摘要未完整提供，需查全文"
- Findings extracted from abstract sentences only

## Phase 3: Recommend (Claude)

After Phase 2, Claude analyzes the skim notes against the user's research context.

### Process
1. Read all skim notes in `03_reading_notes/`
2. Score each paper on 5 dimensions (see `prompts/recommend.md`)
3. Present a recommendation table with rationale
4. User decides which papers to deep-read

### Recommendation Tiers
- **强推 (Strong)**: high match across topic, method, and variables
- **推荐 (Recommended)**: good match in 2+ dimensions
- **可选 (Optional)**: partial relevance, methodology transferable
- **可跳过 (Skip)**: weak relevance to user's research

### User Decision
The user can:
- Accept all recommendations
- Select specific papers
- Choose "deep-read all core papers"
- Choose "deep-read everything"

## Phase 4: Deep / 精读 (Claude)

Claude reads the full Markdown text of selected papers and writes comprehensive notes.

### Process
1. Read the FULL Markdown file in `02_original_md/` for each selected paper
2. Extract: specific numbers, methods details, formulas, data sources, findings with page references
3. Write detailed notes → `04_deep_reading_notes/`
4. Use parallel agent invocations when the runtime supports them; otherwise process selected papers sequentially

### Deep Note Characteristics (~15-30 KB each)
- All template sections filled with detail from the body text
- Formulas with LaTeX rendering and symbol breakdowns
- 5-8 pairs of "主要发现 + 原文引用" with page/section markers
- Specific numbers: frequencies, exposure person-days, mortality counts, CIs
- Model names, resolutions, validation metrics (R², RMSE)
- Personalized judgment: transferable methods, follow-up questions, research connection

### Agent Dispatch Pattern
See `prompts/deep_reading.md` for the full agent prompt. Dispatch 2-3 agents in parallel, each handling 2-3 papers:

```
Agent 1: papers 1-3
Agent 2: papers 4-6
Agent 3: papers 7-9
```

## Phase 5: Overview (Claude)

After deep reading completes:
1. Update `00_collection_overview.md` to a dual-column format:
   - `泛读(03)` column links to skim notes
   - `精读(04)` column links to deep notes (or `-` if not deep-read)
2. Add a summary table of deep-read papers with key findings
3. Verify: 03 has all papers, 04 has only deep-read papers

## Output Contract

```
<output-root>\
  00_collection_overview.md        ← Dual-layer index
  _ProcessLog_进度记录.md
  01_original_pdf\                  ← PDF copies
  02_original_md\                   ← Markdown (reading substrate)
  03_reading_notes\                 ← SKIM: auto-generated, all papers
  04_deep_reading_notes\            ← DEEP: Claude full-text, selected papers
  _workflow\
    collection_items.json
```

## Template Compliance

All notes (both skim and deep) follow `templates/论文精读模板.md`:

1. 基本信息 → 2. 一句话摘要 → 3. 研究对象 → 4. 研究方法 → 5. 数据来源 → 6. 研究结论 → 7. 我的判断

Skim notes may have incomplete sections with "需查全文" markers. Deep notes must fill all sections with body-text evidence.

## Workflow Rules

1. **Script does mechanical, Claude does intellectual.** The script never pretends to do deep reading.
2. **Prefer Markdown.** Once conversion is done, use Markdown as the reading substrate.
3. **Don't fabricate.** If details are missing from abstract or Markdown, say so plainly.
4. **Traceability.** Every note includes Zotero select links and local file paths.
5. **Chinese prose.** Notes are in Chinese except for direct English quotes.
6. **Template contract.** For script-generated skim notes, validate that `templates/论文精读模板.md` still contains the required section headings before writing outputs. For Claude deep-reading notes, read the template before generating notes and preserve its section order.

## Environment

- Zotero Desktop installed and running
- Zotero local API enabled on `http://127.0.0.1:23119`
- Python 3.8+ with `pymupdf` and `requests`
- Windows/Linux/macOS compatible

## Script Reference

```
python scripts/run_zotero_vault_batch_reading.py \
  --collection-key <KEY> \      # Zotero collection key (find via API)
  --collection-name "<NAME>" \  # Human-readable name
  --output-root "<PATH>" \      # Output directory
  --mode <MODE>                 # prepare | skim | all
```

To find a collection key, query: `curl http://127.0.0.1:23119/api/users/0/collections`

## Skill Files

| File | Purpose |
|------|---------|
| `SKILL.md` | This file — skill definition and workflow |
| `README.md` | User-facing guide, prerequisites, quick start |
| `scripts/run_zotero_vault_batch_reading.py` | Phases 1-2 automation |
| `templates/论文精读模板.md` | Note structure template |
| `prompts/onboarding.md` | Phase 0 research context interview |
| `prompts/recommend.md` | Phase 3 paper recommendation |
| `prompts/deep_reading.md` | Phase 4 deep reading agent prompt |
| `CHANGELOG.md` | Version history |
