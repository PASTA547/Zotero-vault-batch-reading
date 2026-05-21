# Zotero Vault Batch Reading

`zotero-vault-batch-reading` is a Claude/Codex skill for turning a Zotero collection into a structured Markdown reading vault. It separates mechanical batch work from intellectual reading work:

- `01_original_pdf/`: copied Zotero PDF attachments.
- `02_original_md/`: PDF-to-Markdown reading substrate.
- `03_reading_notes/`: automatic skim notes generated from Zotero metadata, abstracts, and converted Markdown.
- `04_deep_reading_notes/`: agent-written deep reading notes based on full-text Markdown.
- `00_collection_overview.md`: two-layer collection index linking skim and deep notes.

The workflow is designed for research projects where a user needs to process many papers, triage them against a research question, and then deep-read the most relevant papers without losing traceability to Zotero, PDFs, and local Markdown files.

## What This Skill Does

1. Reads a Zotero collection through Zotero Desktop's local API.
2. Finds PDF attachments and copies them into a local vault folder.
3. Converts PDFs into page-marked Markdown with PyMuPDF.
4. Generates skim-level Chinese notes for all papers.
5. Prompts the agent to recommend papers for deep reading based on the user's research context.
6. Guides the agent to write source-grounded deep reading notes for selected papers.
7. Maintains a collection overview and process log.

The script intentionally does not pretend to perform deep reading. It handles export, conversion, metadata extraction, and skim-note generation. Full-text interpretation remains the agent's responsibility.

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
  scripts/
    run_zotero_vault_batch_reading.py
  templates/
    论文精读模板.md
```

## Prerequisites

- Zotero Desktop is installed and running.
- Zotero local API is enabled at `http://127.0.0.1:23119`.
- Python 3.8+ is available.
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

The agent gathers the user's research context before running the full reading workflow. At minimum, it should identify:

- research topic and target hazards;
- geographic focus;
- research dimension, such as exposure, health burden, projection, mechanism, or policy;
- key variables, such as PM2.5, ozone, heatwaves, mortality, and population exposure;
- deep-reading strategy: recommend, all-core, or all.

### Phase 1: Prepare

The script connects to Zotero's local API, fetches all top-level items in the collection with pagination, finds PDF attachments, copies PDFs to `01_original_pdf/`, converts each PDF to Markdown in `02_original_md/`, and writes item metadata to `_workflow/collection_items.json`.

### Phase 2: Skim

The script generates one skim note per paper in `03_reading_notes/`. These notes are useful for triage, but they are explicitly labeled as skim-level notes. Missing details should be treated as a signal to read the full Markdown or PDF.

### Phase 3: Recommend

The agent reads `00_collection_overview.md` and all skim notes, then scores papers against the user's research context. The recommendation prompt is in `prompts/recommend.md`.

### Phase 4: Deep Reading

For selected papers, the agent reads the full Markdown in `02_original_md/` and writes comprehensive notes in `04_deep_reading_notes/`. Deep notes should include methods, formulas, data sources, specific numbers, source-grounded findings, limitations, and relevance to the user's research.

### Phase 5: Overview

The collection overview should link each paper's skim note and, when available, its deep note. The process log should record newly processed or deep-read items.

## Output Contract

```text
<output-root>/
  00_collection_overview.md
  _ProcessLog_进度记录.md
  01_original_pdf/
  02_original_md/
  03_reading_notes/
  04_deep_reading_notes/
  _workflow/
    collection_items.json
```

## Design Principles

- Keep traceability from every note back to Zotero, DOI, PDF, and Markdown.
- Treat `03_reading_notes/` as fast orientation, not final literature analysis.
- Reserve `04_deep_reading_notes/` for full-text, source-grounded reading.
- Avoid duplicate outputs by using Zotero item keys in generated file names.
- Do not fabricate methods, formulas, data sources, or findings when they are absent from the paper.
- Keep the user's research context visible when recommending papers.

## Notes on Privacy

Generated vault outputs can include local file paths, Zotero item keys, PDFs, and notes derived from copyrighted papers. Publish the skill code and prompts, not a populated research vault, unless you have reviewed the contents and have the right to share them.

## License

MIT
