# {{GAME_NAME}} — Unity 3D Game

Bible-first game development with multi-agent AI team. Design your game completely in documentation before writing a single line of code.

## Quick Start (First Time)

1. **Open Unity Hub** and add this project folder — Unity 6 with URP 3D will load
2. **Open Blender** — Blender MCP needs it running in the background
3. Type `/lead` — the Lead agent will verify all MCP connections and tools
4. Tell Lead what game you want to make — be as detailed as possible
5. Lead creates tasks, then tells you which agent to call next
6. Follow the execution order: usually `/designer` -> `/artist` -> `/engineer` -> `/qa`

**Example first prompt:** `/lead` then "I want to make a third-person adventure game with low-poly 3D art"

## MCP Servers

This project uses these MCP servers (configured in `.mcp.json`):

| Server | Purpose | Setup |
|--------|---------|-------|
| `game-mcp-team` | Task management, decisions, Bible | Auto (Python MCP) |
| `blender` | 3D modeling, UV, materials, export | Blender must be open |
| `photoshop` | Texture/material editing (50+ tools) | Photoshop 2021+ must be open |
| `unity` | Unity editor control | Unity must be open with project loaded |

**Troubleshooting:**
- If Blender MCP fails: make sure Blender 3.6+ is open, install blender-mcp addon
- If Unity MCP fails: make sure Unity 6 is open with this project loaded
- Run `uv sync` if Python MCP server won't start

## Required Tools

| Tool | Install | Purpose |
|------|---------|---------|
| Unity 6 | unity.com/download | Game engine |
| Blender 3.6+ | blender.org | 3D modeling |
| Python 3.11+ | python.org | MCP server runtime |
| uv | `pip install uv` | Python package manager |
| Gemini CLI | `npm i -g @google/gemini-cli` | Research + concepts |

## Core Principles

1. **Quality is absolute priority** — No shortcuts, workarounds, or hacks. Always the most permanent, professional solution.
2. **Work autonomously** — Don't ask questions, make decisions and implement. Solve blockers yourself.
3. **Research then implement** — Use `gemini "..."` to research best practices, double-check, then implement.
4. **Full implementation** — No abbreviating, truncating, or leaving placeholders.
5. **Never sacrifice quality** for token/time savings.

## Stack

| | |
|---|---|
| Engine | Unity 6 (URP 3D) |
| Stack | VContainer (DI) - UniTask (async) - UI Toolkit (UI) - Ink (dialogue) |
| MCP | game-mcp-team (task management) - Blender MCP (3D) - Unity MCP |
| 3D Tools | Blender MCP - Gemini (concepts) |
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
| `/artist` | Artist | Blender 3D, Gemini concepts, materials |
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
| Blender MCP | Artist | 3D modeling (Blender must be open) |
| Unity MCP | Engineer | Unity editor integration |

## File Structure

```
Assets/_Project/Scripts/{Core,Gameplay,UI,Services,Generated,Editor}/
Assets/_Project/Models/{Characters,Environment,Props,Vehicles}/
Assets/_Project/Materials/
Assets/_Project/Prefabs/
Assets/_Project/Scenes/
Assets/_Project/Animations/
src/game_mcp/mcp_team/
docs/bible/{00-meta -> 12-audio}/
workflow/{team-state.json, decisions.md, archive/}
```

## 3D-Specific Guidelines

- **Models:** FBX import from Blender, consistent scale (1 unit = 1 meter)
- **Materials:** URP/Lit shader, PBR textures (albedo, normal, metallic, AO)
- **Lighting:** Mixed lighting mode, baked GI for static, realtime for dynamic
- **Physics:** Rigidbody + Colliders, use layers for collision matrix
- **Camera:** Cinemachine FreeLook or Virtual Camera
- **LOD:** LOD Groups for complex meshes (LOD0: full, LOD1: 50%, LOD2: 25%)
- **Occlusion:** Occlusion Culling for large scenes
- **Navigation:** NavMesh for AI pathfinding
