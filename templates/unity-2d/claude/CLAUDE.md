# {{GAME_NAME}} — Unity 2D Game

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
| Engine | Unity 6 (URP 2D) |
| Stack | VContainer (DI) - UniTask (async) - UI Toolkit (UI) - Ink (dialogue) |
| MCP | game-mcp-team (task management) - PixelLab (pixel art) - Unity MCP |
| Art Tools | PixelLab MCP - Aseprite CLI - Gemini (concepts) |
| Platforms | {{PLATFORMS}} |

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

**Architecture:** Model -> ViewModel (VContainer) -> View (UXML/USS). EventBus pub/sub. UniTask + CancellationToken.

**Python:** UTF-8 mandatory (`encoding="utf-8"`). JSON with `ensure_ascii=False`.

## Bible

`docs/bible/` — 13 sections (00-meta through 12-audio). This is your game design document.

Placeholder check: `Grep(pattern="\[(PLACEHOLDER|TBD|TODO)\]", path="docs/bible/")`

## Roles

| Command | Role | Responsibility |
|---------|------|----------------|
| `/lead` | Team Lead | Research -> be 100% sure -> write tasks -> write agent prompts |
| `/engineer` | Engineer | Unity C# code |
| `/designer` | Designer | Bible documents |
| `/artist` | Artist | PixelLab pixel art, Aseprite, Gemini concepts |
| `/qa` | QA | 5-check verification, testing, builds |
| `/story` | Story | Consultant: story structure analysis |

**Lead ONLY researches and writes tasks.** Edit/Write/claim_task/complete_task FORBIDDEN.
**Agents don't call `create_task()`.** Task creation is Lead's job.

## Task System

```
get_context(role) -> claim_task(id, role) -> do work -> log_decision(role, decision, tag) -> complete_task(id, role, self_review) -> next task
```

- Priority 0-100 (0=urgent). Agent picks lowest OPEN task.
- `complete_task` requires `self_review`: what you did + does it meet requirements?
- `log_decision` tags: ARCH, ART, PERF, BUG, API, NAMING, STYLE, TOOL, CONFIG

## Context Hygiene

- Run `/compact` after each task.
- Long sessions: `/compact` at 60% context, `/clear` + new session at 80%.
- One conversation = one task.

## Tools

| Tool | User | Usage |
|------|------|-------|
| `gemini "..."` | Everyone | Research + double-check |
| Aseprite CLI `-b` | Artist | Sprite post-process |
| PixelLab MCP | Artist | Pixel art (async: create -> get poll) |
| Unity MCP | Engineer | Unity editor integration |

## File Structure

```
Assets/_Project/Scripts/{Core,Gameplay,UI,Services,Generated,Editor}/
Assets/_Project/Art/{Sprites,Tilesets,UI,Animations}/
Assets/_Project/Prefabs/
Assets/_Project/Scenes/
src/game_mcp/mcp_team/
docs/bible/{00-meta -> 12-audio}/
workflow/{team-state.json, decisions.md, archive/}
```

## 2D-Specific Guidelines

- **Sprites:** Point filter, PPU=32, no compression, no mip maps
- **Tilemaps:** Use Unity Tilemap system with Rule Tiles
- **Animation:** Animator Controller + sprite sheets from Aseprite
- **Physics:** Rigidbody2D + Collider2D, FixedUpdate for physics
- **Camera:** Cinemachine 2D with pixel-perfect extension
- **Sorting:** Use Sorting Layers: Background -> Environment -> Characters -> Effects -> UI
