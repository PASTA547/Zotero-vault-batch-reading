# Zotero Vault Retrieval Prompt

Use this prompt when the reading vault already exists and the user wants answers based only on the vault contents.

---

## Task

Answer the user's literature question using only the populated `zotero-vault-batch-reading` vault.

## Retrieval Order

1. Read the root overview or index files first, in this order when present:
   - `00_collection_overview.md`
   - `文献索引.md`
   - `研究主题索引.md`
   - `研究方法索引.md`
   - `字段补全检查.md`
2. Narrow the candidate notes from those files before running keyword search.
3. Search both Chinese and English keywords, as well as method names, variable names, region names, and common aliases.
4. Prefer matching sibling `.meta.md` cards first.
5. Read the full note only if the `.meta.md` card is missing or insufficient.

## Evidence Rules

- Every conclusion must come from a note that actually exists in the vault.
- Do not use external knowledge as vault evidence.
- Do not infer a deep-note label unless the note clearly shows it.
- If the vault does not contain enough support, say `Vault 中未找到足够依据` before any limited answer.

## Default Answer Structure

1. `结论`
2. `支持文献`
3. `出图思路与图表释义`
4. `差异/争议`
5. `对我研究的启发`

## Notes

- If only one note supports a definition, explicitly say the definition is only based on the current vault rather than a universal academic definition.
- If the user asks a vague question, still run the full retrieval flow before deciding the vault cannot answer.
