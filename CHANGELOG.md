# Changelog

## v2.1.0 (2026-05-21)

### Reliability fixes

- Added paginated Zotero collection fetching so collections over 100 top-level items are not truncated.
- Added Zotero `item_key` to generated `03_reading_notes/` filenames to prevent duplicate-title overwrites.
- Added empty-collection handling that writes a diagnostic overview and process log instead of crashing.
- Added template heading validation before script-generated skim notes are written.
- Aligned README, SKILL.md, and prompts around Phase 0 ordering and agent-tool fallbacks.

## v2.0.0 (2026-05-21)

### Architecture redesign: Two-tier reading workflow

**Breaking changes from v1.x:**

- Script no longer claims to produce "精读" (deep reading) notes. The script output in `03_reading_notes/` is now explicitly labeled as **泛读 (skim)** — auto-generated from metadata and abstracts only.
- Deep reading (`04_deep_reading_notes/`) is now exclusively done by Claude, reading the full Markdown text.
- Added **Phase 0 (Onboarding)**: Claude asks about user's research context before processing.
- Added **Phase 3 (Recommend)**: After skim notes are generated, Claude scores papers against the user's research context and recommends which to deep-read.

### New files

- `README.md` — User-facing guide with prerequisites, quick start, output structure, and tips
- `prompts/onboarding.md` — Research context interview prompt for Phase 0
- `prompts/recommend.md` — Paper recommendation scoring and presentation prompt for Phase 3
- `prompts/deep_reading.md` — Full-text deep reading agent prompt for Phase 4
- `CHANGELOG.md` — This file

### Changed files

- `SKILL.md` — Complete rewrite: 5-phase workflow documentation, file reference table
- `scripts/run_zotero_vault_batch_reading.py` — Major changes:
  - `build_note()` → `build_skim_note()`: renamed and updated to label output as 泛读
  - `--mode notes` → `--mode skim`: renamed for clarity
  - Frontmatter now includes `泛读` tag
  - Overview template updated with two-tier note structure placeholder
  - Added explicit "泛读说明" section in method analysis
  - End-of-script message directs Claude to Phase 0 onboarding

### Concept changes

| v1.x | v2.0 |
|------|------|
| Script does everything | Script does mechanical, Claude does intellectual |
| `notes` mode | `skim` mode |
| Notes presented as "精读" | Notes explicitly labeled as "泛读" |
| No user context integration | Research-context-aware recommendations |
| No paper triage | Smart recommendation before deep reading |
| Single output layer | Dual-layer: 03 skim + 04 deep |

## v1.0.0 (earlier)

- Initial implementation: PDF to Markdown conversion + auto note generation
- Local Zotero API integration
- Basic keyword-based paper classification
- Single-pass note generation from metadata + abstract
