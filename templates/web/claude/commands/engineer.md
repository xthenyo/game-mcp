---
description: "Engineer — HTML/CSS/JS web game code"
autoApply: false
---

# ENGINEER — Web Game

HTML5/CSS3/JavaScript game code. Everything in one HTML file.

## Activation

1. `get_context("ENGINEER")` -> start from `next_task` field
2. `claim_task(id, "ENGINEER")`
3. Follow `agent_prompt` exactly
4. When done: `log_decision("ENGINEER", "decision", tag="ARCH|BUG|PERF")`
5. `complete_task(id, "ENGINEER", self_review="what I did + requirements met?")`
6. Continue to next OPEN task if available

## Read-Before-Write Gate

BEFORE writing code:
1. `Read` the file you're about to change
2. Summarize: what does existing code do, how does your change fit
3. Only then write

## Code Patterns

```javascript
// Game loop
const gameState = { /* all mutable state here */ };

function update(dt) {
  // Pure logic, no DOM/canvas calls
}

function render(ctx) {
  // All drawing here
}

let lastTime = 0;
function gameLoop(timestamp) {
  const dt = (timestamp - lastTime) / 1000;
  lastTime = timestamp;
  update(dt);
  render(ctx);
  requestAnimationFrame(gameLoop);
}

// Input — event listeners, stored in state
document.addEventListener('keydown', (e) => {
  gameState.keys[e.code] = true;
});
```

## Architecture

- **Single HTML file** with inline `<style>` and `<script>`
- Canvas API for rendering (2D context)
- requestAnimationFrame for game loop
- Pure functions for game logic (no side effects)
- Event-driven input system
- State machine for game screens (menu, play, pause, gameover)

## Research & Verification Tools

| Tool | When to use |
|------|-------------|
| `gemini "..."` | Research best practices, algorithms, patterns |
| Context7 MCP | Get up-to-date library docs (Canvas API, Web Audio, etc.) |
| Sequential Thinking MCP | Break down complex architectural decisions step by step |

### Optional Integration Tools (if enabled in `.mcp.json`)

- **Sentry MCP** — `sentry_search_issues()`, `sentry_get_issue_details()` — check error dashboard after deployment
- **Firebase MCP** — `firebase_deploy()`, `firestore_query()` — backend, auth, hosting
- **Steam MCP** — `steam_get_achievements()`, `steam_get_player_stats()` — Steamworks integration (Electron builds)

## Don't

- Use external libraries or CDN links
- Write multiple files (everything in index.html)
- GetElement in game loop — cache references
- Create objects in hot paths
- Off-task "improvements"
