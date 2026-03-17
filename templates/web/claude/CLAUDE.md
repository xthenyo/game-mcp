# {{GAME_NAME}} — Web Game

Bible-first game development with multi-agent AI team. Design your game completely in documentation before writing a single line of code.

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
