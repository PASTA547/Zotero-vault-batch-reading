---
name: zotero-vault-batch-reading
description: "Two-tier Zotero batch reading and vault retrieval workflow. Phase 1-2 script: PDF to Markdown plus auto skim notes in 03_reading_notes. Phase 3-4 agent: research-context-aware paper recommendation plus full-text deep reading notes in 04_deep_reading_notes. Phase 5-6: overview maintenance plus evidence-only retrieval from an existing reading vault. Use when processing a Zotero collection into structured Chinese reading notes, or when the user mentions batch read Zotero, vault retrieval, batch literature triage, 深读, 泛读, or processing a collection."
---

# Zotero Vault Batch Reading

Two-tier batch reading workflow for Zotero collections: **skim** (auto-generated from metadata + abstracts -> `03_reading_notes/`) then **deep** (agent full-text analysis -> `04_deep_reading_notes/`), with research-context-aware paper recommendation and evidence-only retrieval from an existing reading vault.

## Workflow Overview

```text
Phase 0: Onboarding    -> Agent gathers research context
Phase 1: Prepare       -> Script: Zotero API -> metadata -> PDF -> Markdown
Phase 2: Skim (03)     -> Script: auto-generate structured skim notes
Phase 3: Recommend     -> Agent: score papers against research context
Phase 4: Deep (04)     -> Agent: full-text reading -> detailed notes + .meta cards
Phase 5: Overview      -> Dual-layer index with 03/04 links
Phase 6: Retrieval     -> Evidence-only answers from the populated vault
```

## Key Principle

**The script handles mechanical work** (Phase 1-2). **The agent handles intellectual work** (Phase 0, 3-6). The script's auto-generated notes are explicitly labeled as **skim** notes: they provide quick orientation and must mark missing detail plainly. Only full-text analysis produces genuine **deep** notes.

## When to Use

Invoke this skill when:
- User wants to process a Zotero collection into structured reading notes
- User wants to retrieve answers only from an existing reading vault
- User mentions batch literature triage, Zotero collection processing, 深读, 泛读, or vault retrieval
- User asks to read papers from a Zotero category
- User mentions a collection name like `ES` or another existing Zotero collection

## Phase 0: Onboarding

Before running any script, gather the user's research context.

### Context Sources
1. `CLAUDE.md` / `GEMINI.md` / `AGENTS.md` in the current workspace
2. Project memory or previous research plans in the workspace
3. Direct questions to the user

### Minimum Context to Collect
- Research topic and compound hazards of interest
- Geographic focus
- Research dimension: exposure / health burden / projection / mechanisms / policy
- Key variables
- Deep reading strategy: `recommend`, `all-core`, or `all`

If the user declines to answer, use default heuristics: recommend papers with matching keywords for compound events, heat, PM2.5 or ozone, mortality, or exposure; deprioritize unrelated climatology-only papers.

## Phase 1: Prepare

Run the collection-to-Markdown pipeline:

```powershell
python "$SKILL_DIR\scripts\run_zotero_vault_batch_reading.py" `
  --collection-key <KEY> `
  --collection-name "<NAME>" `
  --output-root "<OUTPUT>" `
  --mode prepare
```

What it does:
- Connects to Zotero local API (`http://127.0.0.1:23119`)
- Fetches all top-level items in the collection with paginated Zotero API calls
- Locates attached PDFs and copies them to `01_original_pdf/`
- Converts each PDF to Markdown via PyMuPDF -> `02_original_md/`
- Saves metadata to `_workflow/collection_items.json`

Prerequisite: Zotero Desktop running with local API enabled.

## Phase 2: Skim

Generate auto notes for all papers:

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

What it does:
- Reads Zotero metadata such as title, abstract, authors, year, and DOI
- Classifies papers by simple keyword heuristics
- Generates structured skim notes with the script renderer
- Writes outputs to `03_reading_notes/`
- Generates `00_collection_overview.md`
- Generates `_ProcessLog_进度记录.md`

Skim note characteristics:
- Structured sections filled from metadata and abstracts
- Missing methodology or data details must be marked clearly
- Findings should come from abstract-level content only

## Phase 3: Recommend

After Phase 2, the agent analyzes skim notes against the user's research context.

### Process
1. Read all skim notes in `03_reading_notes/`
2. Score each paper on topic, geography, methodology, variables, and impact relevance
3. Present a recommendation table with rationale
4. Let the user decide which papers should be deep-read

Recommendation tiers:
- `强推`
- `推荐`
- `可选`
- `可跳过`

## Phase 4: Deep

The agent reads the full Markdown text of selected papers and writes comprehensive notes.

### Process
1. Read the full Markdown file in `02_original_md/`
2. Extract specific numbers, methods, formulas, data sources, and source-grounded findings
3. Write detailed notes to `04_deep_reading_notes/`
4. Write a compact sibling `.meta.md` card for each deep note
5. Use parallel agent invocations when the runtime supports them; otherwise process sequentially

### Deep Note Characteristics
- All template sections filled with body-text evidence
- Formulas with LaTeX rendering and symbol breakdowns
- Source-grounded direct quotes with page or section markers
- Specific numbers such as event frequencies, exposure person-days, mortality counts, confidence intervals, thresholds, or validation metrics
- Personalized judgment on transferability and research relevance

### `.meta.md` Card Requirements

Write one sibling card per deep note using the same filename stem:

```text
04_deep_reading_notes/<paper>.md
04_deep_reading_notes/<paper>.meta.md
```

Keep the `.meta.md` card compact, ideally within 800 Chinese characters, and include:
1. `研究目标与核心假说`
2. `关键变量与识别逻辑`
3. `出图思路与图表释义`
4. `核心结论与研究局限`

## Phase 5: Overview

After deep reading completes:
1. Update `00_collection_overview.md` to a dual-column format
2. Add a summary table of deep-read papers with key findings
3. Verify `03_reading_notes/` contains all papers and `04_deep_reading_notes/` contains only selected deep-read papers

## Phase 6: Retrieval

Use the populated vault as an evidence-only literature knowledge base.

### Retrieval Workflow

1. Limit the scope to the target reading vault only.
2. Read the root-level overview or index files first, in this order when present:
   - `00_collection_overview.md`
   - `文献索引.md`
   - `研究主题索引.md`
   - `研究方法索引.md`
   - `字段补全检查.md`
3. Use those files to narrow candidate notes before running `rg`.
4. Search both Chinese and English keywords, plus method names, variable names, regions, and common paper aliases.
5. Prefer matching sibling `.meta.md` cards first.
6. Read the full note only when the `.meta.md` card is missing or insufficient.
7. Answer only from notes that actually exist in the vault.

### Retrieval Answer Contract

Default answer structure:
1. `结论`
2. `支持文献`
3. `出图思路与图表释义`
4. `差异/争议`
5. `对我研究的启发`

If evidence is insufficient, state `Vault 中未找到足够依据` before giving any limited answer.

## Output Contract

```text
<output-root>\
  00_collection_overview.md
  _ProcessLog_进度记录.md
  01_original_pdf\
  02_original_md\
  03_reading_notes\
  04_deep_reading_notes\
    *.meta.md
  _workflow\
    collection_items.json
```

## Workflow Rules

1. **Script does mechanical, agent does intellectual.** The script never pretends to do deep reading.
2. **Prefer Markdown.** Once conversion is done, use Markdown as the reading substrate.
3. **Do not fabricate.** If details are missing from abstract or Markdown, say so plainly.
4. **Traceability matters.** Every note should link back to Zotero, DOI, PDF, and Markdown.
5. **Chinese prose.** Notes are in Chinese except for direct English quotes.
6. **Template contract.** For script-generated skim notes, validate that `templates/论文精读模板.md` still contains the required section headings before writing outputs. For deep-reading notes, read the template before generating notes and preserve its section order.
7. **Prefer `.meta.md` for retrieval.** Use compact cards to reduce token cost and escalate to full notes only when necessary.

## Environment

- Zotero Desktop installed and running
- Zotero local API enabled on `http://127.0.0.1:23119`
- Python 3.8+ with `pymupdf` and `requests`
- Windows, Linux, or macOS

## Script Reference

```text
python scripts/run_zotero_vault_batch_reading.py \
  --collection-key <KEY> \
  --collection-name "<NAME>" \
  --output-root "<PATH>" \
  --mode <MODE>
```

Modes:
- `prepare`
- `skim`
- `all`

To find a collection key:

```bash
curl http://127.0.0.1:23119/api/users/0/collections
```

## Skill Files

| File | Purpose |
|------|---------|
| `SKILL.md` | Skill definition and workflow |
| `README.md` | User-facing guide and quick start |
| `scripts/run_zotero_vault_batch_reading.py` | Phases 1-2 automation |
| `templates/论文精读模板.md` | Note structure template |
| `prompts/onboarding.md` | Phase 0 research context interview |
| `prompts/recommend.md` | Phase 3 paper recommendation |
| `prompts/deep_reading.md` | Phase 4 deep reading prompt |
| `prompts/vault_retrieval.md` | Phase 6 vault retrieval prompt |
| `CHANGELOG.md` | Version history |
