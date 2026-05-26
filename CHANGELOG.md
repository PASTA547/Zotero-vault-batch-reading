# Changelog

## v2.2.0 (2026-05-26)

### Retrieval and naming alignment

- Merged the local vault-retrieval enhancements into `zotero-vault-batch-reading` instead of keeping them as a separately named workflow.
- Added Phase 6 retrieval guidance so the populated reading vault can answer questions with evidence-only responses.
- Added `.meta.md` sibling-card requirements for deep-reading outputs to support low-token retrieval.
- Added `prompts/vault_retrieval.md` as the retrieval-mode prompt.
- Updated README and SKILL documentation so the public-facing project name and internal workflow name are consistently `zotero-vault-batch-reading`.

## v2.1.0 (2026-05-21)

### Reliability fixes

- Added paginated Zotero collection fetching so collections over 100 top-level items are not truncated.
- Added Zotero `item_key` to generated `03_reading_notes/` filenames to prevent duplicate-title overwrites.
- Added empty-collection handling that writes a diagnostic overview and process log instead of crashing.
- Added template heading validation before script-generated skim notes are written.
- Aligned README, SKILL.md, and prompts around Phase 0 ordering and agent-tool fallbacks.

## v2.0.0 (2026-05-21)

### Architecture redesign: Two-tier reading workflow

Breaking changes from v1.x:

- Script no longer claims to produce deep-reading notes. The script output in `03_reading_notes/` is explicitly labeled as skim-level notes generated from metadata and abstracts only.
- Deep reading in `04_deep_reading_notes/` is now exclusively done by the agent reading the full Markdown text.
- Added Phase 0 onboarding so the agent asks about research context before processing.
- Added Phase 3 recommendation so the agent scores papers against the user's research context before deep reading.

### New files

- `README.md`
- `prompts/onboarding.md`
- `prompts/recommend.md`
- `prompts/deep_reading.md`
- `CHANGELOG.md`

### Changed files

- `SKILL.md`: full workflow documentation
- `scripts/run_zotero_vault_batch_reading.py`: updated around skim mode, note labeling, and overview generation

## v1.0.0

- Initial implementation: PDF to Markdown conversion plus auto note generation
- Local Zotero API integration
- Basic keyword-based paper classification
- Single-pass note generation from metadata and abstract
