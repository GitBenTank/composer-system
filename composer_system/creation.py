"""Structured creative concepts derived from profile data (generative scaffolding, not agents)."""

from __future__ import annotations

from typing import Any

from composer_system.models import ComposerProfile

_SUMMARY_FIELD_ORDER = (
    "artistic_aim",
    "musical_element",
    "personality_trait",
    "process_habit",
)


def creative_concepts(profile: ComposerProfile, *, max_seeds: int = 12) -> dict[str, Any]:
    """
    Build concept seeds by weaving personality, aims, style, and process lists.

    Rows are capped by ``max_seeds``. When list lengths differ, shorter axes use
    **cyclic** indexing so each seed still mixes every non-empty dimension that
    appears in the profile—deterministic, no randomness, no generation APIs.
    """
    style = [s.strip() for s in profile.musical_style.characteristic_elements if s.strip()]
    process = [h.strip() for h in profile.creative_process.habits if h.strip()]
    aims = [a.strip() for a in profile.artistic_identity.aims if a.strip()]
    traits = [t.strip() for t in profile.personality.traits if t.strip()]

    ls, lp, la, lt = len(style), len(process), len(aims), len(traits)
    if ls == 0 and lp == 0 and la == 0 and lt == 0:
        empty: dict[str, Any] = {
            "composer_id": profile.id,
            "display_name": profile.display_name,
            "concept_seeds": [],
            "narrative_hooks": {
                "public_impression": profile.public_impression,
                "deeper_dimensions": profile.deeper_dimensions,
            },
            "style_and_process_notes": {
                "musical_style_notes": profile.musical_style.notes,
                "creative_process_notes": profile.creative_process.notes,
            },
        }
        return empty

    n = min(max(ls, lp, la, lt), max_seeds)
    seeds: list[dict[str, Any]] = []

    for i in range(n):
        artistic_aim = aims[i % la] if la else None
        musical_element = style[i % ls] if ls else None
        personality_trait = traits[i % lt] if lt else None
        process_habit = process[i % lp] if lp else None

        entry: dict[str, Any] = {
            "index": i,
            "seed_id": f"{profile.id}:{i:02d}",
            "artistic_aim": artistic_aim,
            "musical_element": musical_element,
            "personality_trait": personality_trait,
            "process_habit": process_habit,
        }

        present = [k for k in _SUMMARY_FIELD_ORDER if entry[k] is not None]
        entry["dimensions"] = present
        entry["summary"] = _summarize_seed(entry)

        seeds.append(entry)

    return {
        "composer_id": profile.id,
        "display_name": profile.display_name,
        "concept_seeds": seeds,
        "narrative_hooks": {
            "public_impression": profile.public_impression,
            "deeper_dimensions": profile.deeper_dimensions,
        },
        "style_and_process_notes": {
            "musical_style_notes": profile.musical_style.notes,
            "creative_process_notes": profile.creative_process.notes,
        },
    }


def _summarize_seed(entry: dict[str, Any]) -> str:
    chunks = [str(entry[k]) for k in _SUMMARY_FIELD_ORDER if entry.get(k)]
    return " · ".join(chunks)
