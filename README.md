# Game MCP

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Unity 6](https://img.shields.io/badge/Unity-6-black.svg)](https://unity.com/)
[![Claude Code](https://img.shields.io/badge/Claude-Code-orange.svg)](https://claude.ai/)

**Bible-first game development with multi-agent AI team simulation.**

Design your game completely in documentation (the "Bible") before writing a single line of code. Each Claude Code chat window becomes a specialized team member working together through a shared MCP server.

---

## Quick Start

```bash
git clone https://github.com/xthenyo/game-mcp.git my-game
cd my-game
bash setup.sh "My Game" MG
```

Then open VS Code, launch Claude Code, and type `/lead` to start.

---

## How It Works

```
┌─────────────────────────────────────────────────────────────┐
│                    VS Code + Claude Code                    │
│                                                             │
│   ┌─────────┐   ┌─────────┐   ┌─────────┐   ┌─────────┐   │
│   │  /lead  │   │/engineer│   │/designer│   │  /qa    │   │
│   │         │   │         │   │         │   │         │   │
│   │Decisions│   │  Code   │   │  Docs   │   │ Testing │   │
│   └────┬────┘   └────┬────┘   └────┬────┘   └────┬────┘   │
│        │             │             │             │         │
│        └─────────────┴──────┬──────┴─────────────┘         │
│                             ▼                               │
│                    ┌─────────────┐                          │
│                    │ MCP Server  │                          │
│                    │Shared State │                          │
│                    └─────────────┘                          │
└─────────────────────────────────────────────────────────────┘
```

Open multiple chat windows, assign roles with slash commands, and collaborate like a real team.

---

## Roles

| Command | Role | Domain |
|---------|------|--------|
| `/lead` | Team Lead | Coordination, decisions, tasks |
| `/engineer` | Engineer | Unity C# code, gameplay, systems |
| `/designer` | Designer | Game design docs (Bible) |
| `/artist` | Artist | AI art, sprites, 3D, UI |
| `/qa` | QA | Testing, validation, builds |
| `/story` | Story | Narrative structure analysis |

---

## MCP Servers

| Server | Purpose |
|--------|---------|
| **doomed-team** | Task management, Bible status, decision log, cross-agent context |
| **PixelLab** | AI pixel art generation (characters, tiles, animations) |
| **Blender MCP** | 3D modeling and rendering |
| **Unity MCP** | Unity Editor integration |

---

## Workflow

```
DISCOVERY → DESIGN → PLANNING → DEVELOPMENT → QA → RELEASE
```

**Rule:** Complete Bible documentation before writing code.

---

## Project Structure

```
├── .claude/commands/    # Role definitions (slash commands)
├── docs/bible/          # Game design documentation
│   ├── 00-meta/         # Project config, glossary
│   ├── 01-vision/       # GDD, pillars, references
│   ├── 02-mechanics/    # Core loop, systems, rules
│   ├── 03-entities/     # Player, NPCs, groups
│   ├── 04-attributes/   # Character attributes
│   ├── 05-world/        # Map, locations
│   ├── 06-narrative/    # Story, branches
│   ├── 07-quests/       # Quest definitions
│   ├── 08-relations/    # NPC relationships
│   ├── 09-events/       # Events, triggers
│   ├── 10-art/          # Art style, UI specs
│   ├── 11-release/      # Platform config
│   └── 12-audio/        # Audio specs
├── workflow/            # Tasks, state, decisions
├── src/doomed/mcp_team/ # MCP server (multi-agent shared state)
└── Assets/_Project/     # Unity game code
```

---

## Setup

### Prerequisites

- [Python 3.11+](https://python.org)
- [uv](https://github.com/astral-sh/uv) (Python package manager)
- [Git](https://git-scm.com)
- [VS Code](https://code.visualstudio.com) with [Claude Code](https://claude.ai/claude-code)
- [Unity 6](https://unity.com) (for game development)

### MCP Configuration

After running `setup.sh`, edit `.mcp.json` to set your API keys:

```json
{
  "mcpServers": {
    "pixellab": {
      "headers": {
        "Authorization": "Bearer YOUR_PIXELLAB_TOKEN"
      }
    }
  }
}
```

Optional environment variables:
- `GOOGLE_API_KEY` — For Gemini image generation
- `PIXELLAB_API_TOKEN` — For PixelLab pixel art
- `ASEPRITE_PATH` — Path to Aseprite executable

---

## Tech Stack

| Technology | Purpose |
|------------|---------|
| Unity 6 (URP) | Game Engine |
| VContainer | Dependency Injection |
| UniTask | Async Operations |
| UI Toolkit | User Interface |
| Ink | Dialogue System |
| MCP | Multi-agent coordination |

---

## License

MIT License - See [LICENSE](LICENSE)
