# Game MCP — npm CLI Framework

This is the **game-mcp** npm package source. It's a CLI tool that scaffolds game projects with Claude Code multi-agent support.

## Structure

- `bin/game-mcp.js` — CLI entry point
- `lib/` — CLI modules (prompts, scaffold, secrets, deps, launcher)
- `templates/` — Project templates per game type
  - `common/` — Shared across all types (MCP server, workflow, Bible)
  - `web/` — Web game (HTML/JS)
  - `unity-2d/` — Unity 2D (PixelLab, Aseprite)
  - `unity-3d/` — Unity 3D (Blender)

## Development

```bash
npm install          # Install deps
npm start            # Run CLI locally
npm link             # Link globally for testing
```

## Templates

Templates use `{{VARIABLE}}` syntax for substitution. The scaffold module replaces these during project creation.

Files in `templates/*/claude/` are copied to `.claude/` (dot-prefixed) in the output project.
Files named `mcp.json` are renamed to `.mcp.json` in the output project.
