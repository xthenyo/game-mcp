"""Bible documentation status tools."""

from __future__ import annotations

import re
from pathlib import Path

from .._context import BIBLE_ROOT, mcp

PLACEHOLDER_PATTERN = re.compile(r"\[(PLACEHOLDER|TBD|TODO|GAME_SPECIFIC)\]", re.IGNORECASE)

BIBLE_SECTIONS = [
    ("00-meta", "Meta"), ("01-vision", "Vision"), ("02-mechanics", "Mechanics"),
    ("03-entities", "Entities"), ("04-attributes", "Attributes"), ("05-world", "World"),
    ("06-narrative", "Narrative"), ("07-quests", "Quests"), ("08-relations", "Relations"),
    ("09-events", "Events"), ("10-art", "Art"), ("11-release", "Release"), ("12-audio", "Audio"),
]


def _scan_section(section_path: Path) -> dict:
    if not section_path.exists():
        return {"exists": False, "files": 0, "placeholders": 0, "completion": 0}
    files = list(section_path.rglob("*.md")) + list(section_path.rglob("*.yaml"))
    total_placeholders = 0
    for f in files:
        content = f.read_text(encoding="utf-8", errors="ignore")
        total_placeholders += len(PLACEHOLDER_PATTERN.findall(content))
    completion = 100 if total_placeholders == 0 and files else 0 if not files else max(0, 100 - total_placeholders * 10)
    return {"exists": True, "files": len(files), "placeholders": total_placeholders, "completion": max(0, min(100, completion))}


@mcp.tool(description="Check Bible documentation completion status per section")
def bible_status() -> dict:
    """Shows completion percentage for each Bible section."""
    sections = {}
    total_placeholders = 0
    total_files = 0
    for section_id, section_name in BIBLE_SECTIONS:
        info = _scan_section(BIBLE_ROOT / section_id)
        sections[section_id] = {"name": section_name, **info}
        total_placeholders += info["placeholders"]
        total_files += info["files"]
    return {
        "sections": sections, "total_files": total_files,
        "total_placeholders": total_placeholders,
        "overall_completion": 100 if total_placeholders == 0 else max(0, 100 - total_placeholders * 2),
    }


@mcp.tool(description="Find placeholder gaps in Bible documentation")
def bible_gaps() -> dict:
    """Lists all files with remaining placeholders."""
    gaps = []
    for section_id, section_name in BIBLE_SECTIONS:
        section_path = BIBLE_ROOT / section_id
        if not section_path.exists():
            continue
        for f in list(section_path.rglob("*.md")) + list(section_path.rglob("*.yaml")):
            content = f.read_text(encoding="utf-8", errors="ignore")
            matches = list(PLACEHOLDER_PATTERN.finditer(content))
            if matches:
                gaps.append({
                    "file": str(f.relative_to(BIBLE_ROOT)),
                    "section": section_name,
                    "count": len(matches),
                    "types": list(set(m.group(1).upper() for m in matches)),
                })
    return {"gaps": gaps, "total_files_with_gaps": len(gaps)}
