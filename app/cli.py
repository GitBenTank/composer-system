#!/usr/bin/env python3
"""Tiny CLI: show one composer's human summary or regenerate comparison markdown."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from composer_system.load import load_profile
from composer_system.reflection import human_reflection_summary

_DATA_DIR = _REPO_ROOT / "data" / "composers"


def _cmd_show(composer_id: str) -> None:
    profile = load_profile(composer_id, data_dir=_DATA_DIR)
    print(f"## {profile.display_name} ({profile.id})\n")
    print(human_reflection_summary(profile))


def _cmd_compare() -> None:
    from app.profile_comparison import run_comparison

    run_comparison()


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="composer-system",
        description="Load composer profiles and print summaries or regenerate comparison output.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_show = sub.add_parser("show", help="Print human reflection summary for one composer")
    p_show.add_argument("id", metavar="COMPOSER_ID", help="e.g. bach, chopin")

    sub.add_parser("compare", help="Write outputs/profile_comparison.md for all profiles")

    args = parser.parse_args()
    if args.command == "show":
        _cmd_show(args.id)
    elif args.command == "compare":
        _cmd_compare()


if __name__ == "__main__":
    main()
