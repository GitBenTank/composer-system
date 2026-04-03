"""Deterministic creative brief from profile + user intent (handoff to music layer)."""

from __future__ import annotations

import hashlib
from typing import Any

from composer_system.creation import creative_concepts
from composer_system.models import ComposerProfile


def _trim_intent(intent: str) -> str:
    """Collapse whitespace; stable across leading/trailing/multiple spaces."""
    return " ".join(intent.split())


def _clean_lines(lines: list[str], *, limit: int) -> list[str]:
    """Strip entries, drop empties; preserve order; cap length for bounded payloads."""
    out: list[str] = []
    for raw in lines:
        s = str(raw).strip()
        if s and s not in out:
            out.append(s)
        if len(out) >= limit:
            break
    return out


def _concept_seed_index(composer_id: str, trimmed_intent: str, num_seeds: int) -> int:
    if num_seeds <= 0:
        return 0
    digest = hashlib.sha256(f"{composer_id}\n{trimmed_intent}".encode()).digest()
    return int.from_bytes(digest[:8], "big") % num_seeds


def get_brief(profile: ComposerProfile, intent: str) -> dict[str, Any]:
    """
    Build a deterministic brief from profile fields and normalized user intent.

    Uses only the loaded profile and the intent string: no randomness, no I/O,
    no external APIs. The same (profile, intent) pair always yields the same object.

    Intended for composer-runtime: ``musical_direction`` and ``seed`` feed
    ``build_music_prompt``; ``display_name`` and ``profile_schema_version`` aid
    logging and versioned tooling without touching generator logic.
    """
    trimmed = _trim_intent(intent)

    seeds = creative_concepts(profile).get("concept_seeds") or []
    if seeds:
        i = _concept_seed_index(profile.id, trimmed, len(seeds))
        seed: dict[str, Any] = dict(seeds[i])
    else:
        seed = {}

    aims = _clean_lines(list(profile.artistic_identity.aims), limit=2)
    style_elements = _clean_lines(
        list(profile.musical_style.characteristic_elements), limit=3
    )
    process_habits = _clean_lines(list(profile.creative_process.habits), limit=2)

    return {
        "composer_id": profile.id,
        "display_name": profile.display_name,
        "profile_schema_version": profile.schema_version,
        "trimmed_intent": trimmed,
        "musical_direction": {
            "aims": aims,
            "style_elements": style_elements,
            "process_habits": process_habits,
        },
        "seed": seed,
        "output_target": "music_prompt_v1",
    }
