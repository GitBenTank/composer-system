"""Structured reflections derived only from validated profile fields (no LLM)."""

from __future__ import annotations

from typing import Any

from composer_system.models import ComposerProfile


def structured_reflection(profile: ComposerProfile) -> dict[str, Any]:
    """
    Build a nested reflection object for prompts or downstream tooling.

    All strings are taken from the profile; nothing is invented about history.
    """
    return {
        "subject": {
            "id": profile.id,
            "display_name": profile.display_name,
            "life_span": profile.life_span.model_dump(),
            "era_context": profile.era_context,
        },
        "impression_and_depth": {
            "public_impression": profile.public_impression,
            "deeper_dimensions": profile.deeper_dimensions,
        },
        "creative_identity": {
            "personality": profile.personality.model_dump(),
            "artistic_identity": profile.artistic_identity.model_dump(),
            "musical_style": profile.musical_style.model_dump(),
            "creative_process": profile.creative_process.model_dump(),
        },
        "epistemics": {"source_notes": profile.source_notes},
        "prompt_fragments": _prompt_fragments(profile),
    }


def _prompt_fragments(profile: ComposerProfile) -> list[str]:
    """Short, reusable clauses assembled from structured lists (still profile-bound)."""
    fragments: list[str] = []
    if profile.personality.traits:
        fragments.append(
            "Personality traits to respect: " + "; ".join(profile.personality.traits) + "."
        )
    if profile.artistic_identity.aims:
        fragments.append(
            "Artistic aims named in profile: " + "; ".join(profile.artistic_identity.aims) + "."
        )
    if profile.musical_style.characteristic_elements:
        fragments.append(
            "Musical fingerprints from profile: "
            + "; ".join(profile.musical_style.characteristic_elements)
            + "."
        )
    if profile.creative_process.habits:
        fragments.append(
            "Creative process habits from profile: "
            + "; ".join(profile.creative_process.habits)
            + "."
        )
    if profile.source_notes:
        fragments.append("Source / epistemic note: " + profile.source_notes)
    return fragments
