# Zotero Vault Batch Reading

`zotero-vault-batch-reading` is a Claude/Codex skill for turning a Zotero collection into a structured Markdown reading vault and then querying that vault as an evidence-only literature knowledge base.

It separates mechanical batch work from intellectual reading work:

- `01_original_pdf/`: copied Zotero PDF attachments
- `02_original_md/`: PDF-to-Markdown reading substrate
- `03_reading_notes/`: automatic skim notes generated from Zotero metadata, abstracts, and converted Markdown
- `04_deep_reading_notes/`: agent-written deep reading notes based on full-text Markdown
- `04_deep_reading_notes/*.meta.md`: compact retrieval cards for low-token evidence lookup
- `00_collection_overview.md`: two-layer collection index linking skim and deep notes

The workflow is designed for research projects where a user needs to process many papers, triage them against a research question, deep-read the most relevant papers, and later query the resulting vault without losing traceability to Zotero, PDFs, and local Markdown files.

## What This Skill Does

1. Reads a Zotero collection through Zotero Desktop's local API
2. Finds PDF attachments and copies them into a local vault folder
3. Converts PDFs into page-marked Markdown with PyMuPDF
4. Generates skim-level Chinese notes for all papers
5. Prompts the agent to recommend papers for deep reading based on the user's research context
6. Guides the agent to write source-grounded deep reading notes for selected papers
7. Generates compact `.meta.md` cards that summarize research aim, variables, figure logic, and limits
8. Supports evidence-only retrieval from the populated reading vault

The script intentionally does not pretend to perform deep reading. It handles export, conversion, metadata extraction, and skim-note generation. Full-text interpretation remains the agent's responsibility.

## Install With an AI Agent

Most users will not install this skill manually file by file. A practical path is to let an AI coding agent install and configure it inside the local skill directory, then help the user connect it to Zotero and an optional Markdown knowledge base.

For agents, the practical installation flow is:

1. Clone or download this repository.
2. Place the folder in the local skills directory, for example:
   - `%USERPROFILE%\.codex\skills\zotero-vault-batch-reading`
   - or another skill search path used by the local agent runtime.
3. Install Python dependencies:

```bash
pip install -r requirements.txt
```

4. Verify that Zotero Desktop is running and that the local API is reachable:

```bash
curl http://127.0.0.1:23119/api/users/0/collections
```

5. Ask the user which Zotero collection should be processed and what output directory should be used.
6. Run `prepare` or `all` mode for the first pass.
7. Use the prompts in `prompts/` to gather research context, recommend deep-reading candidates, write full-text notes, and later retrieve evidence from the vault.

Related guides:
- [Skill introduction](INTRODUCTION.zh-CN.md)
- [Detailed setup guide](SETUP_GUIDE.zh-CN.md)
- [Vault retrieval prompt](prompts/vault_retrieval.md)

## Hard Requirements

- **Required**: Zotero Desktop
- **Required**: Zotero local API at `127.0.0.1:23119`
- **Required**: Python 3.8+ and the dependencies in `requirements.txt`
- **Optional**: Obsidian or another Markdown knowledge base

Obsidian is not a prerequisite. This skill writes ordinary Markdown folders. Obsidian simply makes the resulting vault easier to browse, cross-link, and maintain over time.

## Repository Layout

```text
zotero-vault-batch-reading/
  SKILL.md
  README.md
  CHANGELOG.md
  requirements.txt
  LICENSE
  prompts/
    onboarding.md
    recommend.md
    deep_reading.md
    vault_retrieval.md
  scripts/
    run_zotero_vault_batch_reading.py
  templates/
    论文精读模板.md
```

## Prerequisites

- Zotero Desktop is installed and running
- Zotero local API is enabled at `http://127.0.0.1:23119`
- Python 3.8+ is available
- Python dependencies are installed:

```bash
pip install -r requirements.txt
```

You can check whether Zotero's local API is reachable with:

```bash
curl http://127.0.0.1:23119/api/users/0/collections
```

## Quick Start

First let the agent gather or infer the research context. This context is used later to recommend which papers deserve full-text deep reading.

Then run the automated prepare-and-skim pipeline:

```bash
python scripts/run_zotero_vault_batch_reading.py \
  --collection-key <ZOTERO_COLLECTION_KEY> \
  --collection-name "ES" \
  --output-root "./ES" \
  --mode all
```

To run only PDF staging and Markdown conversion:

```bash
python scripts/run_zotero_vault_batch_reading.py \
  --collection-key <ZOTERO_COLLECTION_KEY> \
  --collection-name "ES" \
  --output-root "./ES" \
  --mode prepare
```

To regenerate skim notes from an existing `_workflow/collection_items.json`:

```bash
python scripts/run_zotero_vault_batch_reading.py \
  --collection-key <ZOTERO_COLLECTION_KEY> \
  --collection-name "ES" \
  --output-root "./ES" \
  --mode skim
```

## Workflow

### Phase 0: Onboarding

The agent gathers the user's research context before running the workflow. At minimum, it should identify:

- research topic and target hazards
- geographic focus
- research dimension, such as exposure, health burden, projection, mechanism, or policy
- key variables, such as PM2.5, ozone, heatwaves, mortality, and population exposure
- deep-reading strategy: `recommend`, `all-core`, or `all`

### Phase 1: Prepare

The script connects to Zotero's local API, fetches all top-level items in the collection with pagination, finds PDF attachments, copies PDFs to `01_original_pdf/`, converts each PDF to Markdown in `02_original_md/`, and writes item metadata to `_workflow/collection_items.json`.

### Phase 2: Skim

The script generates one skim note per paper in `03_reading_notes/`. These notes are useful for triage, but they are explicitly labeled as skim-level notes. Missing details should be treated as a signal to read the full Markdown or PDF.

### Phase 3: Recommend

The agent reads `00_collection_overview.md` and all skim notes, then scores papers against the user's research context. The recommendation prompt is in `prompts/recommend.md`.

### Phase 4: Deep Reading

For selected papers, the agent reads the full Markdown in `02_original_md/` and writes comprehensive notes in `04_deep_reading_notes/`. Deep notes should include methods, formulas, data sources, specific numbers, source-grounded findings, limitations, and relevance to the user's research.

Each deep note should also produce a sibling `.meta.md` card for lightweight retrieval. The card should capture:

- `研究目标与核心假说`
- `关键变量与识别逻辑`
- `出图思路与图表释义`
- `核心结论与研究局限`

### Phase 5: Overview

The collection overview should link each paper's skim note and, when available, its deep note. The process log should record newly processed or deep-read items.

### Phase 6: Retrieval

Once the vault has notes, the agent can answer literature questions directly from the vault.

Recommended retrieval order:
1. `00_collection_overview.md`
2. Optional root indexes such as `文献索引.md`, `研究主题索引.md`, `研究方法索引.md`, `字段补全检查.md`
3. Matching `.meta.md` cards
4. Full deep or skim notes only when the cards are insufficient

Default retrieval answer structure:
1. `结论`
2. `支持文献`
3. `出图思路与图表释义`
4. `差异/争议`
5. `对我研究的启发`

If the vault does not contain enough support, the answer should explicitly say `Vault 中未找到足够依据`.

## Output Contract

```text
<output-root>/
  00_collection_overview.md
  _ProcessLog_进度记录.md
  01_original_pdf/
  02_original_md/
  03_reading_notes/
  04_deep_reading_notes/
    *.meta.md
  _workflow/
    collection_items.json
```

## Design Principles

- Keep traceability from every note back to Zotero, DOI, PDF, and Markdown
- Treat `03_reading_notes/` as fast orientation, not final literature analysis
- Reserve `04_deep_reading_notes/` for full-text, source-grounded reading
- Use `.meta.md` cards first when answering from the vault
- Avoid duplicate outputs by using Zotero item keys in generated file names
- Do not fabricate methods, formulas, data sources, or findings when they are absent from the paper
- Keep the user's research context visible when recommending papers

## Notes on Privacy

Generated vault outputs can include local file paths, Zotero item keys, PDFs, and notes derived from copyrighted papers. Publish the skill code and prompts, not a populated research vault, unless you have reviewed the contents and have the right to share them.

## License

MIT
