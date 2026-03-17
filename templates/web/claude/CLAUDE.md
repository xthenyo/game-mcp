# {{GAME_NAME}} — Web Game

Bible-first game development with multi-agent AI team. Design your game completely in documentation before writing a single line of code.

## Quick Start (First Time)

1. Type `/lead` — the Lead agent will verify all MCP connections and tools
2. Tell Lead what game you want to make — be as detailed as possible
3. Lead creates tasks, then tells you which agent to call next
4. Follow the execution order: usually `/designer` -> `/engineer` -> `/qa`

**Example first prompt:** `/lead` then "I want to make a 2D platformer with pixel art graphics and 10 levels"

## MCP Servers

This project uses these MCP servers (configured in `.mcp.json`):

| Server | Purpose | Status Check |
|--------|---------|-------------|
| `game-mcp-team` | Task management, decisions, Bible tracking | `get_context("LEAD")` |

## Required Tools

| Tool | Install | Purpose |
|------|---------|---------|
| Gemini CLI | `npm i -g @google/gemini-cli` | Research + image generation |
| Python 3.11+ | python.org | MCP server runtime |
| uv | `pip install uv` | Python package manager |

## Core Principles

1. **Quality is absolute priority** — No shortcuts, workarounds, or hacks.
2. **Work autonomously** — Don't ask questions, make decisions and implement.
3. **Research then implement** — Use `gemini "..."` to research best practices, then implement.
4. **Full implementation** — No abbreviating, truncating, or leaving placeholders.
5. **Never sacrifice quality** for token/time savings.

## Stack

| | |
|---|---|
| Platform | Web (HTML5/CSS3/JavaScript) |
| Packaging | Single HTML file, Electron for Steam |
| MCP | game-mcp-team (task management) |

## Code Standard

**All code in English.** No non-English identifiers, comments, or string literals.

- **Everything in one HTML file** — inline CSS and JS
- Use modern ES2024+ features (modules, async/await, canvas API)
- Canvas for rendering, requestAnimationFrame for game loop
- Clean separation: game state, rendering, input handling
- No external dependencies — pure vanilla JS

## Bible

`docs/bible/` — 13 sections (00-meta through 12-audio). This is your game design document.

Placeholder check: `Grep(pattern="\[(PLACEHOLDER|TBD|TODO)\]", path="docs/bible/")`

## Roles

| Command | Role | Responsibility |
|---------|------|----------------|
| `/lead` | Team Lead | Research -> be 100% sure -> write tasks -> write agent prompts |
| `/engineer` | Engineer | HTML/CSS/JS code |
| `/designer` | Designer | Bible documents |
| `/artist` | Artist | Gemini image gen, CSS art, SVG |
| `/qa` | QA | 5-check verification, testing |
| `/story` | Story | Consultant: story structure analysis |

**Lead ONLY researches and writes tasks.** Edit/Write/claim_task/complete_task FORBIDDEN.
**Agents don't call `create_task()`.** Task creation is Lead's job.

## Task System

```
get_context(role) -> claim_task(id, role) -> do work -> log_decision(role, decision, tag) -> complete_task(id, role, self_review) -> next task
```

- Priority 0-100 (0=urgent). Agent picks lowest OPEN task.
- `complete_task` requires `self_review`: what you did + does it meet requirements?

## Context Hygiene

- Run `/compact` after each task.
- One conversation = one task.

## File Structure

```
src/index.html                    # Main game file (everything in one file)
src/assets/                       # Images, sounds
docs/bible/{00-meta -> 12-audio}/ # Game design document
workflow/                         # Task state, decisions
```
