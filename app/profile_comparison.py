#!/usr/bin/env python3
"""Write a deterministic markdown comparison of all composer profiles."""

import json
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from composer_system.load import load_profile
from composer_system.reflection import human_reflection_summary, structured_reflection
from composer_system.creation import creative_concepts

_DATA_DIR = _REPO_ROOT / "data" / "composers"
_OUTPUT = _REPO_ROOT / "outputs" / "profile_comparison.md"


def _concept_list_markdown(concepts: dict) -> str:
    seeds = concepts.get("concept_seeds") or []
    if not seeds:
        return "1. _(No concept seeds: profile lists were empty.)_"
    lines: list[str] = []
    for i, seed in enumerate(seeds, start=1):
        pairs = [f"{k}={json.dumps(v, ensure_ascii=False)}" for k, v in sorted(seed.items())]
        lines.append(f"{i}. " + ", ".join(pairs))
    return "\n".join(lines)


def run_comparison() -> None:
    paths = sorted(_DATA_DIR.glob("*.json"))
    if not paths:
        raise SystemExit(f"No JSON profiles in {_DATA_DIR}")

    parts: list[str] = ["# Composer Profile Comparison", ""]

    for path in paths:
        composer_id = path.stem
        profile = load_profile(composer_id, data_dir=_DATA_DIR)
        reflection = structured_reflection(profile)
        summary = human_reflection_summary(profile)
        concepts = creative_concepts(profile)

        public = getattr(profile, "public_impression", "") or ""
        deeper = getattr(profile, "deeper_dimensions", "") or ""

        parts.extend(
            [
                f"## {profile.display_name} ({profile.id})",
                "",
                "### Public Impression",
                "",
                public.strip() or "_(not set)_",
                "",
                "### Deeper Dimensions",
                "",
                deeper.strip() or "_(not set)_",
                "",
                "### Human Reflection Summary",
                "",
                summary.strip() or "_(not generated)_",
                "",
                "### Reflection",
                "",
                "```json",
                json.dumps(reflection, indent=2, ensure_ascii=False),
                "```",
                "",
                "### Creative Concepts",
                "",
                _concept_list_markdown(concepts),
                "",
            ]
        )

    _OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    _OUTPUT.write_text("\n".join(parts).rstrip() + "\n", encoding="utf-8")
    print(f"Wrote {_OUTPUT.relative_to(_REPO_ROOT)}")


def main() -> None:
    run_comparison()


if __name__ == "__main__":
    main()
