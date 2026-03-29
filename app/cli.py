#!/usr/bin/env python3
"""Tiny CLI: show one composer's human summary or regenerate comparison markdown."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from composer_system.creation import creative_concepts
from composer_system.load import load_profile
from composer_system.reflection import human_reflection_summary

_DATA_DIR = _REPO_ROOT / "data" / "composers"
_DIVIDER_WIDTH = 48


def _divider() -> str:
    return "-" * _DIVIDER_WIDTH


def _section(title: str, body: str) -> None:
    text = (body or "").strip()
    print(title)
    print(text if text else "(not set)")
    print()


def _format_concept_line(seed: dict) -> str:
    parts: list[str] = []
    for key in sorted(k for k in seed if k != "index"):
        val = seed[key]
        if isinstance(val, str):
            escaped = val.replace("\\", "\\\\").replace('"', '\\"')
            parts.append(f'{key}="{escaped}"')
        else:
            parts.append(f"{key}={val!r}")
    return ", ".join(parts) if parts else "(empty row)"


def _cmd_show(composer_id: str) -> None:
    profile = load_profile(composer_id, data_dir=_DATA_DIR)
    summary = human_reflection_summary(profile)
    concepts = creative_concepts(profile)

    print(f"{profile.display_name} ({profile.id})")
    print(_divider())
    print()

    public = getattr(profile, "public_impression", "") or ""
    deeper = getattr(profile, "deeper_dimensions", "") or ""
    _section("Public Impression", public)
    _section("Deeper Dimensions", deeper)
    _section("Summary", summary)

    print("Creative Concepts")
    seeds = concepts.get("concept_seeds") or []
    if not seeds:
        print("(none — profile lists for style, process, aims, or traits were empty)")
    else:
        for i, seed in enumerate(seeds, start=1):
            print(f"{i}. {_format_concept_line(seed)}")


def _cmd_compare() -> None:
    from app.profile_comparison import run_comparison

    run_comparison()


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="composer-system",
        description="Load composer profiles and print summaries or regenerate comparison output.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_show = sub.add_parser(
        "show",
        help="Print profile sections, human summary, and creative concept seeds",
    )
    p_show.add_argument("id", metavar="COMPOSER_ID", help="e.g. bach, chopin")

    sub.add_parser("compare", help="Write outputs/profile_comparison.md for all profiles")

    args = parser.parse_args()
    if args.command == "show":
        _cmd_show(args.id)
    elif args.command == "compare":
        _cmd_compare()


if __name__ == "__main__":
    main()
