"""Structured creative concepts derived from profile data (generative scaffolding, not agents)."""

from __future__ import annotations

from typing import Any

from composer_system.models import ComposerProfile


def creative_concepts(profile: ComposerProfile, *, max_seeds: int = 12) -> dict[str, Any]:
    """
    Combine lists from the profile into explicit "concept seeds" for ideation.

    Caps list sizes to keep payloads bounded. Does not assert historical facts beyond the profile.
    """
    style = profile.musical_style.characteristic_elements[:max_seeds]
    process = profile.creative_process.habits[:max_seeds]
    aims = profile.artistic_identity.aims[:max_seeds]
    traits = profile.personality.traits[:max_seeds]

    lengths = (len(style), len(process), len(aims), len(traits))
    seeds: list[dict[str, Any]] = []
    if any(lengths):
        n = min(max(lengths), max_seeds)
        for i in range(n):
            entry: dict[str, Any] = {"index": i}
            if i < len(style):
                entry["musical_element"] = style[i]
            if i < len(process):
                entry["process_habit"] = process[i]
            if i < len(aims):
                entry["artistic_aim"] = aims[i]
            if i < len(traits):
                entry["personality_trait"] = traits[i]
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
