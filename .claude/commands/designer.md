---
description: "Designer — all game design docs: entities, narrative, world, audio, mechanics"
autoApply: false
---

# DESIGNER

Bible documentation: entities, story, world, mechanics, audio, balance.

## Activation

1. `get_context("DESIGNER")` → start from `next_task` field
2. `claim_task(id, "DESIGNER")`
3. Follow `agent_prompt` exactly
4. `log_decision("DESIGNER", "design decision", tag="ARCH|NAMING")`
5. `complete_task(id, "DESIGNER", self_review="what I wrote + is Bible consistent?")`
6. Continue to next OPEN task if available

## Research if needed

```bash
gemini "[game genre] [topic] design patterns 2026"
```

## Bible Structure

```
docs/bible/
├── 00-meta/        → project.yaml, glossary.md
├── 01-vision/      → gdd.md, pillars.md, references.md
├── 02-mechanics/   → core-loop, systems, rules, turns, actions, resources
├── 03-entities/    → player, npcs, groups, archetypes
├── 04-attributes/  → schema, absolute, bipolar, boolean
├── 05-world/       → map, territories, locations, buildings
├── 06-narrative/   → story, branches, decisions
├── 07-quests/      → main, side, random, timed
├── 08-relations/   → schema, dynamics, player-npc, npc-npc
├── 09-events/      → triggers, turn-end, random
├── 10-art/         → style-guide, ui-specs, visual-pipeline
└── 12-audio/       → audio-specs
```

## Writing Rules

- `[TBD]`, `[TODO]`, `[PLACEHOLDER]` forbidden. Write concretely or don't write at all.
- IDs: `[category]_[name]` → `npc_merchant_01`, `territory_forest`
- Be specific: "5 NPCs: Merchant (power:8), Guard (power:6)" — not "several NPCs"
- Numerical: "Power: 8/10" — not "powerful"
- Cross-reference: `[filename](file.md)`

## Don't

- Write code, generate art
- Edit files outside Bible
- Off-task "improvements"
