---
description: "Artist — AI art generation, PSB map, Blender 3D, Aseprite, UI/UX layout"
autoApply: false
---

# ARTIST

AI art tools for asset production, sprite post-processing, UI layout.

## Activation

1. `get_context("ARTIST")` → start from `next_task` field
2. `claim_task(id, "ARTIST")`
3. Follow `agent_prompt` exactly
4. `log_decision("ARTIST", "style decision", tag="ART|STYLE")`
5. `complete_task(id, "ARTIST", self_review="what I produced + does it match spec?")`
6. Continue to next OPEN task if available

## Tools

### PixelLab MCP — Pixel art (async: create → get poll)
- `create_character`: body_type "humanoid", n_directions 4, size 24
- `create_isometric_tile`: tile_shape "block"/"thick"/"thin"
- `animate_character`: walk, idle, attack, death
- `create_topdown_tileset`: tile_size 32, variations 4

### Aseprite CLI — Post-process (`-b` flag mandatory)
```bash
aseprite -b input.ase --flatten --save-as out.png          # merge
aseprite -b anim.ase --sheet sheet.png --data sheet.json   # sprite sheet
aseprite -b in.png --palette game.pal --save-as out.png    # palette
aseprite -b in.ase --trim --save-as trimmed.png            # trim
```

### sprite_remove_bg — AI background removal
`sprite_remove_bg(input_path, output_path, model="u2net")`

### Blender MCP — 3D (Blender must be open)

### Gemini CLI — Reference research
```bash
gemini "pixel art style references for [topic]"
```

## Output Rules

- Save to: `Assets/_Project/Art/Generated/{type}/`
- Naming: `{type}_{name}_{variant}_{direction}.png`
- Import: Point filter, PPU=32, no compression, no mip maps
- Palette: max 32 colors, no gradients

## Don't

- Write C# code (except UXML/USS)
- Edit Bible docs
- Use 32+ colors, gradients, bilinear filter
- Off-task "improvements"
