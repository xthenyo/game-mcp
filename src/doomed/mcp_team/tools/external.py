"""External tool wrappers — Gemini CLI, Aseprite CLI, rembg (background removal).

These tools wrap CLI commands so agents don't need to remember Bash syntax.
All outputs are standardized to project paths.
"""

from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path
from typing import Optional

from .._context import PROJECT_ROOT, mcp


def _run(cmd: list[str], timeout: int = 120) -> tuple[int, str, str]:
    """Run a subprocess and return (returncode, stdout, stderr)."""
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=str(PROJECT_ROOT),
        )
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return -1, "", f"Command timed out after {timeout}s"
    except FileNotFoundError:
        return -1, "", f"Command not found: {cmd[0]}"


def _find_exe(name: str, env_var: str | None = None) -> str | None:
    """Find an executable on PATH or via env var."""
    if env_var:
        import os
        path = os.environ.get(env_var)
        if path and Path(path).exists():
            return path
    return shutil.which(name)


# ─── Gemini CLI ────────────────────────────────────────────────────────────────


@mcp.tool(description="Run internet research via Gemini CLI — saves Claude tokens. Returns Gemini's response.")
def research(query: str, output_file: Optional[str] = None) -> dict:
    """Ask Gemini CLI to research a topic. Saves result to a file if specified.

    Args:
        query: Research question or topic (in English or Turkish)
        output_file: Optional path to save results (relative to project root, e.g. 'docs/research/topic.md')
    """
    gemini = _find_exe("gemini")
    if not gemini:
        return {"error": "Gemini CLI not found. Install: npm install -g @anthropic/gemini-cli or check PATH"}

    prompt = query
    if output_file:
        abs_path = PROJECT_ROOT / output_file
        abs_path.parent.mkdir(parents=True, exist_ok=True)
        prompt += f"\n\nWrite the full result to: {abs_path}"

    code, stdout, stderr = _run([gemini, prompt], timeout=180)

    if code != 0:
        return {"error": f"Gemini failed (code {code}): {stderr[:500]}"}

    result = {"success": True, "response": stdout[:3000]}
    if output_file:
        result["saved_to"] = output_file
    return result


@mcp.tool(description="Generate an image via Gemini CLI. Returns the generated image path.")
def generate_image(prompt: str, output_path: str, style: str = "") -> dict:
    """Use Gemini CLI to generate a concept image.

    Args:
        prompt: Image description (be specific: subject, style, lighting, mood)
        output_path: Where to save (relative to project root, e.g. 'Assets/_Project/Art/Concepts/scene.png')
        style: Optional style modifier (e.g. 'pixel art', 'concept art', 'isometric')
    """
    gemini = _find_exe("gemini")
    if not gemini:
        return {"error": "Gemini CLI not found"}

    abs_path = PROJECT_ROOT / output_path
    abs_path.parent.mkdir(parents=True, exist_ok=True)

    full_prompt = f"Generate an image: {prompt}"
    if style:
        full_prompt += f", style: {style}"
    full_prompt += f"\nSave the image to: {abs_path}"

    code, stdout, stderr = _run([gemini, full_prompt], timeout=180)

    if code != 0:
        return {"error": f"Gemini image gen failed: {stderr[:500]}"}

    return {"success": True, "output_path": output_path, "response": stdout[:1000]}


# ─── Aseprite CLI ──────────────────────────────────────────────────────────────


def _aseprite() -> str | None:
    """Find Aseprite executable."""
    return _find_exe("aseprite", "ASEPRITE_PATH") or _find_exe("aseprite.exe")


@mcp.tool(description="Flatten all layers in a sprite file into a single image (Aseprite CLI)")
def sprite_flatten(input_path: str, output_path: str) -> dict:
    """Merge all layers and export as PNG.

    Args:
        input_path: Source file (relative to project root)
        output_path: Output PNG path (relative to project root)
    """
    exe = _aseprite()
    if not exe:
        return {"error": "Aseprite not found. Set ASEPRITE_PATH or add to PATH."}

    abs_in = str(PROJECT_ROOT / input_path)
    abs_out = str(PROJECT_ROOT / output_path)
    Path(abs_out).parent.mkdir(parents=True, exist_ok=True)

    code, stdout, stderr = _run([exe, "-b", abs_in, "--flatten", "--save-as", abs_out])
    if code != 0:
        return {"error": f"Aseprite flatten failed: {stderr[:500]}"}
    return {"success": True, "output": output_path}


@mcp.tool(description="Export animation frames as a sprite sheet (Aseprite CLI)")
def sprite_sheet(
    input_path: str,
    output_path: str,
    sheet_type: str = "horizontal",
    data_path: Optional[str] = None,
) -> dict:
    """Export sprite animation as a single sheet image + optional JSON data.

    Args:
        input_path: Source .ase/.aseprite file (relative)
        output_path: Output sprite sheet PNG (relative)
        sheet_type: 'horizontal', 'vertical', 'rows', or 'packed'
        data_path: Optional JSON data output path (frame positions, sizes)
    """
    exe = _aseprite()
    if not exe:
        return {"error": "Aseprite not found"}

    abs_in = str(PROJECT_ROOT / input_path)
    abs_out = str(PROJECT_ROOT / output_path)
    Path(abs_out).parent.mkdir(parents=True, exist_ok=True)

    cmd = [exe, "-b", abs_in, "--sheet", abs_out, "--sheet-type", sheet_type]
    if data_path:
        abs_data = str(PROJECT_ROOT / data_path)
        cmd += ["--data", abs_data]

    code, stdout, stderr = _run(cmd)
    if code != 0:
        return {"error": f"Aseprite sheet failed: {stderr[:500]}"}

    result = {"success": True, "output": output_path}
    if data_path:
        result["data"] = data_path
    return result


@mcp.tool(description="Apply a color palette to a sprite (Aseprite CLI)")
def sprite_palette(input_path: str, palette_path: str, output_path: str) -> dict:
    """Remap sprite colors to match a palette file.

    Args:
        input_path: Source image (relative)
        palette_path: Palette file .pal/.gpl/.ase (relative)
        output_path: Output PNG (relative)
    """
    exe = _aseprite()
    if not exe:
        return {"error": "Aseprite not found"}

    abs_in = str(PROJECT_ROOT / input_path)
    abs_pal = str(PROJECT_ROOT / palette_path)
    abs_out = str(PROJECT_ROOT / output_path)
    Path(abs_out).parent.mkdir(parents=True, exist_ok=True)

    code, stdout, stderr = _run([exe, "-b", abs_in, "--palette", abs_pal, "--save-as", abs_out])
    if code != 0:
        return {"error": f"Aseprite palette failed: {stderr[:500]}"}
    return {"success": True, "output": output_path}


@mcp.tool(description="Trim transparent borders and optionally scale a sprite (Aseprite CLI)")
def sprite_trim_scale(input_path: str, output_path: str, scale: int = 1) -> dict:
    """Remove transparent borders and optionally resize.

    Args:
        input_path: Source image (relative)
        output_path: Output PNG (relative)
        scale: Scale factor (1=no scale, 2=2x, 3=3x)
    """
    exe = _aseprite()
    if not exe:
        return {"error": "Aseprite not found"}

    abs_in = str(PROJECT_ROOT / input_path)
    abs_out = str(PROJECT_ROOT / output_path)
    Path(abs_out).parent.mkdir(parents=True, exist_ok=True)

    cmd = [exe, "-b", abs_in, "--trim"]
    if scale > 1:
        cmd += ["--scale", str(scale)]
    cmd += ["--save-as", abs_out]

    code, stdout, stderr = _run(cmd)
    if code != 0:
        return {"error": f"Aseprite trim/scale failed: {stderr[:500]}"}
    return {"success": True, "output": output_path, "scale": scale}


@mcp.tool(description="Split sprite layers into separate PNG files (Aseprite CLI)")
def sprite_split_layers(input_path: str, output_dir: str) -> dict:
    """Export each layer as a separate PNG file.

    Args:
        input_path: Source .ase/.aseprite file (relative)
        output_dir: Output directory (relative). Files named layer_{layername}.png
    """
    exe = _aseprite()
    if not exe:
        return {"error": "Aseprite not found"}

    abs_in = str(PROJECT_ROOT / input_path)
    abs_dir = PROJECT_ROOT / output_dir
    abs_dir.mkdir(parents=True, exist_ok=True)

    cmd = [exe, "-b", abs_in, "--split-layers", "--save-as", str(abs_dir / "layer_{layer}.png")]

    code, stdout, stderr = _run(cmd)
    if code != 0:
        return {"error": f"Aseprite split failed: {stderr[:500]}"}
    return {"success": True, "output_dir": output_dir}


# ─── rembg — AI Background Removal ───────────────────────────────────────────


@mcp.tool(description="Remove background from an image — outputs transparent PNG. Uses AI (U2Net) to detect objects.")
def sprite_remove_bg(
    input_path: str,
    output_path: str,
    model: str = "u2net",
    alpha_matting: bool = False,
) -> dict:
    """AI-powered background removal — select object, output transparent PNG.

    Perfect for:
    - Extracting characters/objects from reference photos
    - Cleaning up AI-generated art with messy backgrounds
    - Creating game-ready sprites from concept art
    - Dekupe (cutout) for 2D game assets

    Args:
        input_path: Source image (relative to project root)
        output_path: Output transparent PNG (relative to project root)
        model: AI model — 'u2net' (general), 'isnet-general-use' (high quality), 'u2net_human_seg' (people)
        alpha_matting: Enable alpha matting for soft edges (hair, fur, feathers)
    """
    abs_in = PROJECT_ROOT / input_path
    abs_out = PROJECT_ROOT / output_path

    if not abs_in.exists():
        return {"error": f"Input file not found: {input_path}"}

    abs_out.parent.mkdir(parents=True, exist_ok=True)

    try:
        from rembg import remove, new_session
        from PIL import Image

        session = new_session(model)

        with Image.open(abs_in) as img:
            result = remove(
                img,
                session=session,
                alpha_matting=alpha_matting,
                alpha_matting_foreground_threshold=240 if alpha_matting else 0,
                alpha_matting_background_threshold=10 if alpha_matting else 0,
            )
            result.save(str(abs_out))

        return {
            "success": True,
            "output": output_path,
            "model": model,
            "alpha_matting": alpha_matting,
            "size": f"{result.width}x{result.height}",
        }
    except ImportError:
        return {"error": "rembg not installed. Run: uv add rembg"}
    except Exception as e:
        return {"error": f"Background removal failed: {str(e)[:500]}"}
