# Blender MCP Addon

Connects Blender to Claude Code via MCP for AI-assisted 3D modeling.

## Setup

### 1. Install the addon in Blender
1. Open Blender 3.6+
2. Edit > Preferences > Add-ons
3. Click "Install..." and select `addon.py` from this directory
4. Enable "Interface: Blender MCP"

### 2. Connect
1. In Blender's 3D viewport, open sidebar (N key)
2. Find the "BlenderMCP" tab
3. Click "Connect to Claude"
4. The addon starts a socket server on `localhost:9876`

### 3. Use from Claude Code
The `.mcp.json` already includes the blender server config.
Claude Code will auto-connect when you start a session in the project.

## Capabilities

- **Scene inspection**: Get scene info, object list, materials
- **Object manipulation**: Create, modify, delete 3D objects
- **Material control**: Apply and modify materials/colors
- **Code execution**: Run Python in Blender's context
- **Poly Haven**: Download free models/textures
- **Viewport screenshots**: See what's in the scene

## Use Cases for Game Dev

- 3D blockouts for level design reference
- Isometric camera setup for render-to-sprite workflows
- Material/lighting experiments before pixel art
- Map layout prototyping with basic geometry

## Source

Addon from [blender-mcp](https://github.com/ahujasid/blender-mcp) by Siddharth Ahuja.
MCP server package: `uvx blender-mcp` (auto-installed via .mcp.json).
