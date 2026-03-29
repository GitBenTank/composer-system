#!/usr/bin/env python3
"""Generate a side-by-side markdown snapshot of reflections and concept seeds for all profiles."""

from __future__ import annotations

import json
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from composer_system.creation import creative_concepts
from composer_system.load import load_profile
from composer_system.reflection import structured_reflection

_DATA_DIR = _REPO_ROOT / "data" / "composers"
_OUTPUT_PATH = _REPO_ROOT / "outputs" / "profile_comparison.md"


def _escape_md(text: str) -> str:
    return text.replace("\r\n", "\n").strip()


def _json_block(obj: object) -> str:
    return json.dumps(obj, indent=2, ensure_ascii=False)


def main() -> None:
    if not _DATA_DIR.is_dir():
        raise SystemExit(f"Missing data directory: {_DATA_DIR}")

    paths = sorted(_DATA_DIR.glob("*.json"))
    if not paths:
        raise SystemExit(f"No composer JSON files in {_DATA_DIR}")

    lines: list[str] = [
        "# Composer profile comparison",
        "",
        "Generated deterministically from `data/composers/*.json` via `structured_reflection` and `creative_concepts`.",
        "",
    ]

    for path in paths:
        composer_id = path.stem
        profile = load_profile(composer_id, data_dir=_DATA_DIR)
        reflection = structured_reflection(profile)
        concepts = creative_concepts(profile)

        lines.extend(
            [
                f"## {profile.display_name} (`{profile.id}`)",
                "",
                "### From profile",
                "",
                f"- **Display name:** {profile.display_name}",
                f"- **Life span:** {profile.life_span.birth_year}–{profile.life_span.death_year}",
                "",
                "**Public impression**",
                "",
                _escape_md(profile.public_impression),
                "",
                "**Deeper dimensions**",
                "",
                _escape_md(profile.deeper_dimensions),
                "",
                "### Structured reflection",
                "",
                "```json",
                _json_block(reflection),
                "```",
                "",
                "### Creative concepts",
                "",
                "```json",
                _json_block(concepts),
                "```",
                "",
                "---",
                "",
            ]
        )

    _OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    _OUTPUT_PATH.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    print(f"Wrote {_OUTPUT_PATH.relative_to(_REPO_ROOT)}")


if __name__ == "__main__":
    main()
