# Game MCP — Multi-Agent Game Development Framework

Bible-first game development with multi-agent AI team. Design your game completely in documentation before writing a single line of code.

## Core Principles

1. **Quality is absolute priority** — No shortcuts, workarounds, or hacks. Always the most permanent, professional solution.
2. **Work autonomously** — Don't ask questions, make decisions and implement. Solve blockers yourself.
3. **Research then implement** — Use `gemini "..."` to research best practices, double-check, then implement.
4. **Full implementation** — No abbreviating, truncating, or leaving placeholders.
5. **Never sacrifice quality** for token/time savings.

## Stack

| | |
|---|---|
| Engine | Unity 6 (URP) |
| Stack | VContainer (DI) · UniTask (async) · UI Toolkit (UI) · Ink (dialogue) |
| MCP | doomed-team (task management) · PixelLab (pixel art) · Blender MCP (3D) · Unity MCP |

## Code Standard

**All code in English.** No non-English identifiers, comments, or string literals.

```csharp
// GOOD                              // BAD
private int _healthPoints;           private int hp;
public bool IsAlive { get; }         public bool alive;
[SerializeField] private float _ms;  public float moveSpeed;
const int MAX_SQUAD_SIZE = 12;       const int max = 12;
```

**Naming:** Class `PascalCase`, Interface `IPascalCase`, Method `PascalCase verb`, Property `PascalCase`, Private `_camelCase`, Local `camelCase`, Bool `is/has/can/should`, Const `UPPER_SNAKE`, Event `*Event`, Enum `PascalCase`.

**Architecture:** Model → ViewModel (VContainer) → View (UXML/USS). EventBus pub/sub. UniTask + CancellationToken.

**Python:** UTF-8 mandatory (`encoding="utf-8"`). JSON with `ensure_ascii=False`.

## Bible

`docs/bible/` — 13 sections (00-meta through 12-audio). This is your game design document.

Placeholder check: `Grep(pattern="\[(PLACEHOLDER|TBD|TODO)\]", path="docs/bible/")`

## Roles

| Command | Role | Responsibility |
|---------|------|----------------|
| `/lead` | Team Lead | Research → be 100% sure → write tasks → write agent prompts |
| `/engineer` | Engineer | Unity C# code |
| `/designer` | Designer | Bible documents |
| `/artist` | Artist | AI art, PSB, Blender, Aseprite |
| `/qa` | QA | 5-check verification, testing, builds |
| `/story` | Story | Consultant: story structure analysis |

**Lead ONLY researches and writes tasks.** Edit/Write/claim_task/complete_task FORBIDDEN.
**Agents don't call `create_task()`.** Task creation is Lead's job.
**Feedback:** If small and in your domain, fix immediately. If large, say "call /lead".

## Task System

```
get_context(role) → claim_task(id, role) → do work → log_decision(role, decision, tag) → complete_task(id, role, self_review) → next task
```

- Priority 0-100 (0=urgent). Agent picks lowest OPEN task.
- `complete_task` requires `self_review`: what you did + does it meet requirements?
- `log_decision` tags: ARCH, ART, PERF, BUG, API, NAMING, STYLE, TOOL, CONFIG

## Context Hygiene

- Run `/compact` after each task.
- Long sessions: `/compact` at 60% context, `/clear` + new session at 80%.
- One conversation = one task. When task is done, start new conversation.

## Tools

| Tool | User | Usage |
|------|------|-------|
| `gemini "..."` | Everyone | Research + double-check |
| Aseprite CLI `-b` | Artist | Sprite post-process |
| PixelLab MCP | Artist | Pixel art (async: create → get poll) |
| Blender MCP | Artist | 3D (Blender must be open) |

## File Structure

```
Assets/_Project/Scripts/{Core,Gameplay,UI,Services,Generated,Editor}/
src/doomed/mcp_team/
docs/bible/{00-meta → 12-audio}/
workflow/{team-state.json, decisions.md, archive/}
```
