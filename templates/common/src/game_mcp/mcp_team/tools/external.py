"""External tool wrappers — Gemini CLI, Aseprite CLI, rembg."""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path
from typing import Optional

from .._context import PROJECT_ROOT, mcp


def _run(cmd: list[str], timeout: int = 120) -> tuple[int, str, str]:
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, cwd=str(PROJECT_ROOT))
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return -1, "", f"Command timed out after {timeout}s"
    except FileNotFoundError:
        return -1, "", f"Command not found: {cmd[0]}"


def _find_exe(name: str, env_var: str | None = None) -> str | None:
    if env_var:
        import os
        path = os.environ.get(env_var)
        if path and Path(path).exists():
            return path
    return shutil.which(name)


@mcp.tool(description="Run internet research via Gemini CLI.")
def research(query: str, output_file: Optional[str] = None) -> dict:
    """Ask Gemini CLI to research a topic."""
    gemini = _find_exe("gemini")
    if not gemini:
        return {"error": "Gemini CLI not found. Install: npm install -g @anthropic/gemini-cli"}
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


@mcp.tool(description="Generate an image via Gemini CLI.")
def generate_image(prompt: str, output_path: str, style: str = "") -> dict:
    """Use Gemini CLI to generate a concept image."""
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


def _aseprite() -> str | None:
    return _find_exe("aseprite", "ASEPRITE_PATH") or _find_exe("aseprite.exe")


@mcp.tool(description="Flatten all layers in a sprite file (Aseprite CLI)")
def sprite_flatten(input_path: str, output_path: str) -> dict:
    """Merge all layers and export as PNG."""
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
def sprite_sheet(input_path: str, output_path: str, sheet_type: str = "horizontal", data_path: Optional[str] = None) -> dict:
    """Export sprite animation as a single sheet image."""
    exe = _aseprite()
    if not exe:
        return {"error": "Aseprite not found"}
    abs_in = str(PROJECT_ROOT / input_path)
    abs_out = str(PROJECT_ROOT / output_path)
    Path(abs_out).parent.mkdir(parents=True, exist_ok=True)
    cmd = [exe, "-b", abs_in, "--sheet", abs_out, "--sheet-type", sheet_type]
    if data_path:
        cmd += ["--data", str(PROJECT_ROOT / data_path)]
    code, stdout, stderr = _run(cmd)
    if code != 0:
        return {"error": f"Aseprite sheet failed: {stderr[:500]}"}
    result = {"success": True, "output": output_path}
    if data_path:
        result["data"] = data_path
    return result


@mcp.tool(description="Remove background from an image — outputs transparent PNG.")
def sprite_remove_bg(input_path: str, output_path: str, model: str = "u2net", alpha_matting: bool = False) -> dict:
    """AI-powered background removal."""
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
            result = remove(img, session=session, alpha_matting=alpha_matting,
                          alpha_matting_foreground_threshold=240 if alpha_matting else 0,
                          alpha_matting_background_threshold=10 if alpha_matting else 0)
            result.save(str(abs_out))
        return {"success": True, "output": output_path, "model": model, "size": f"{result.width}x{result.height}"}
    except ImportError:
        return {"error": "rembg not installed. Run: uv add rembg"}
    except Exception as e:
        return {"error": f"Background removal failed: {str(e)[:500]}"}
