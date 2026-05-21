# Paper Recommendation Prompt

Use this prompt after Phase 2 (skim) completes. It analyzes skim notes against the user's research context and recommends papers for deep reading.

---

## Instructions for Claude

You have:
1. The user's research context (gathered in Phase 0)
2. `00_collection_overview.md` — list of all papers with classifications
3. All skim notes in `03_reading_notes/` — quick structured overviews of every paper

## Scoring Criteria

Score each paper on a 1-5 scale for each dimension:

| Dimension | 1 (Low relevance) | 5 (High relevance) |
|-----------|-------------------|---------------------|
| **Topic match** | Unrelated hazards/events | Directly studies user's compound hazards |
| **Geographic match** | Different region, no transferable insight | Same study area as user |
| **Methodology match** | Completely different approach | Methods directly applicable to user |
| **Variable match** | No overlap in key variables | Same exposure/outcome variables |
| **Health/Impact dimension** | Pure climatology, no health/impact | Direct health burden or exposure assessment |

## Output Format

Present your analysis as a table:

```markdown
## 精读推荐

基于你的研究背景（[brief summary of user's context]），对9篇核心论文的分析如下：

| # | 论文 | 主题匹配 | 方法匹配 | 变量匹配 | 总推荐 | 理由 |
|---|------|:---:|:---:|:---:|:---:|------|
| 1 | Ban 2022 热浪-臭氧 | ★★★★★ | ★★★★☆ | ★★★☆☆ | **强推** | 未来情景预测方法可复用，收入不平等框架直接借鉴 |
| 2 | Chen 2024 欧洲 | ★★★★☆ | ★★★☆☆ | ★★★★★ | **强推** | 四污染物复合暴露定义、人群加权指标可直接迁移 |
| ... | ... | ... | ... | ... | ... | ... |

### 推荐精读（强推+推荐）
- [ ] Paper A — 理由
- [ ] Paper B — 理由

### 可选精读（有一定参考价值）
- [ ] Paper C — 理由

### 可跳过（与当前研究关联较弱）
- [ ] Paper D — 理由
```

## Decision

After presenting the recommendation table, ask the user which papers to deep-read. The user can:
- Accept all recommendations
- Select specific papers
- Choose "deep-read all"
- Modify criteria and re-score

## Classification Logic

If the user didn't provide explicit research context, use these default heuristics:

| Paper theme keywords | Default recommendation |
|---------------------|----------------------|
| "compound" + "heat" + "PM2.5"/"ozone" + "mortality"/"death" | **Strong** — directly relevant to compound health burden |
| "compound" + "heat" + "PM2.5"/"ozone" + "exposure" | **Strong** — exposure assessment is foundational |
| "compound" + "heat" + "PM2.5"/"ozone" (no health/exposure) | **Recommended** — methodology transferable |
| "compound" + multiple hazards (no health) | **Optional** — framework reference |
| Review/scoping + compound + health | **Recommended** — valuable literature synthesis |
| Urban/rural comparison + compound | **Context-dependent** — recommend if user studies urbanization |
