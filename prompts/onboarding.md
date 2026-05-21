# Onboarding Prompt

Use this prompt when starting a new batch reading session. It gathers the user's research context before the collection is processed or before deep-reading recommendations are made.

---

## Instructions for the Agent

Before running the full workflow, gather the user's research context. Check for existing context in this order:

1. `CLAUDE.md`, `GEMINI.md`, or `AGENTS.md` in the current workspace.
2. Project memory or previous research plans in the workspace.
3. Direct questions to the user if the files above do not provide enough context.

## Required Information

Collect these six items. If they are not available in files, ask the user concise questions:

1. **Research topic**: What compound events, hazards, or phenomena are being studied?
2. **Geographic focus**: Global, regional, or specific countries/areas?
3. **Research dimension**: Exposure assessment, health burden, future projection/scenarios, mechanisms/attribution, policy evaluation, or another dimension?
4. **Key variables of interest**: PM2.5, ozone, temperature/heat, precipitation, drought, wildfire, population exposure, mortality, morbidity, or other variables?
5. **Existing research plan**: Is there a plan, proposal, manuscript draft, or project note that defines the research?
6. **Deep reading strategy**:
   - `recommend`: let the agent recommend papers for deep reading based on the research context.
   - `all-core`: deep-read all papers classified as core or topical.
   - `all`: deep-read every paper in the collection.

## Example User Profile

```text
Research topic: Global population exposure and premature mortality from compound heat-pollution events
Geographic focus: Global, with regional comparisons
Dimension: Exposure assessment and health burden
Key variables: PM2.5, heatwaves, ozone, compound events, population exposure, mortality
Deep reading strategy: recommend
```

## After Gathering Context

If the runtime provides a memory mechanism and the user permits it, save a brief project memory recording the user's research focus. Then proceed to Phase 1 (`prepare`) or Phase 2 (`skim`) depending on what has already been generated.
