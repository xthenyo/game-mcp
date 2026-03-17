# Game MCP

Multi-agent game development framework for **Claude Code**. Build games with an AI team — Lead, Engineer, Designer, Artist, QA, and Story Consultant.

## Quick Start

```bash
npx game-mcp
```

The CLI will guide you through:

1. **Game name** and code
2. **Game type** — Web (HTML/JS), Unity 2D, or Unity 3D
3. **API keys** — Gemini, PixelLab, GitHub/GitLab (stored encrypted, gitignored)
4. **Platform targets** — PC, iOS, Android, Steam
5. **Git provider** — GitHub, GitLab, or local

Then open the project in **Claude Code** and type `/lead` to start.

## Game Types

### Web Game
- Single HTML file with inline CSS/JS
- Canvas API game loop
- Packageable for Steam via Electron
- No dependencies, pure vanilla JS

### Unity 2D
- Unity 6 with URP 2D
- PixelLab MCP for AI pixel art generation
- Aseprite CLI for sprite post-processing
- VContainer DI + UniTask async

### Unity 3D
- Unity 6 with URP 3D
- Blender MCP for 3D modeling
- PBR materials and lighting
- VContainer DI + UniTask async

## How It Works

Game MCP uses a **Bible-first** approach: design your game completely in documentation before writing code.

### Agent Roles

| Command | Role | What They Do |
|---------|------|-------------|
| `/lead` | Team Lead | Research, plan, create tasks |
| `/engineer` | Engineer | Write game code |
| `/designer` | Designer | Write game design docs |
| `/artist` | Artist | Generate and process art assets |
| `/qa` | QA | 5-check verification of all changes |
| `/story` | Story | Narrative structure consulting |

### Task Flow

```
/lead → analyzes request → creates tasks with priorities
/engineer → claims task → implements → self-reviews → completes
/qa → verifies → 5-check gate → approves or reports bugs
```

## Requirements

- [Claude Code](https://claude.ai/code) (CLI)
- [Python 3.11+](https://python.org) + [uv](https://docs.astral.sh/uv/)
- [Git](https://git-scm.com)
- [Node.js 18+](https://nodejs.org) (for CLI and web games)

### Optional (by game type)

| Tool | Web | Unity 2D | Unity 3D |
|------|-----|----------|----------|
| [Unity 6](https://unity.com) | | Required | Required |
| [Blender](https://blender.org) | | | Required |
| [Aseprite](https://aseprite.org) | | Recommended | |
| [Gemini CLI](https://github.com/google-gemini/gemini-cli) | Recommended | Recommended | Recommended |

### API Keys (optional, enable AI features)

| Key | Purpose | Get it at |
|-----|---------|-----------|
| `GOOGLE_API_KEY` | Gemini research + image gen | [Google AI Studio](https://aistudio.google.com) |
| `PIXELLAB_API_TOKEN` | AI pixel art (2D) | [PixelLab](https://pixellab.ai) |
| `RODIN_API_KEY` | AI 3D models (3D) | [Rodin](https://hyper.ai) |
| `GIT_TOKEN` | GitHub/GitLab integration | GitHub/GitLab settings |

## Project Structure (after setup)

```
my-game/
├── .claude/           # Claude Code config + agent commands
│   ├── CLAUDE.md      # Project instructions
│   ├── settings.json  # Permissions
│   └── commands/      # /lead, /engineer, /designer, /artist, /qa, /story
├── .mcp.json          # MCP server config
├── .env               # API keys (gitignored)
├── src/               # Game code (HTML or Unity scripts)
├── docs/bible/        # Game design document (13 sections)
├── workflow/           # Task management state
├── game-mcp.json      # Project config
└── pyproject.toml     # MCP server dependencies
```

## MCP Server

The framework includes a Python MCP server (`game-mcp-team`) that provides:

- **Task management** — create, claim, complete, search tasks with priorities
- **Decision log** — cross-agent context sharing
- **Bible status** — documentation completeness tracking
- **External tools** — Gemini CLI, Aseprite CLI, background removal

## License

MIT
