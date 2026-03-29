"""Deterministic creative brief from profile + user intent (handoff to music layer)."""

from __future__ import annotations

from typing import Any

from composer_system.creation import creative_concepts
from composer_system.models import ComposerProfile


def get_brief(profile: ComposerProfile, intent: str) -> dict[str, Any]:
    """
    Build profile-bound brief contract v1 for downstream music prompt / generation.

    Uses only profile fields and stripped user intent; does not invent history.
    """
    seeds = creative_concepts(profile).get("concept_seeds") or []
    seed0 = dict(seeds[0]) if seeds else {}

    aims = list(profile.artistic_identity.aims[:2])
    elements = list(profile.musical_style.characteristic_elements[:3])
    habits = list(profile.creative_process.habits[:2])

    return {
        "composer_id": profile.id,
        "intent": intent.strip(),
        "musical_direction": {
            "aims": aims,
            "style_elements": elements,
            "process_habits": habits,
        },
        "seed": seed0,
        "output_target": "music_prompt_v1",
    }
