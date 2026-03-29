"""Load and validate every shipped composer profile; catch shallow duplicates and voice shortcuts."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from composer_system.validate import validate_profile

_DATA = Path(__file__).resolve().parent.parent / "data" / "composers"

# Pop-writing clichés and caricature shortcuts—not exhaustive, but a guardrail for example data.
_FORBIDDEN_VOICE_MARKERS = (
    "tortured genius",
    "mad genius",
    "miracle child",
    "wonder child",
    "chosen by god",
    "divine child",
    "rock star",
    "superhuman",
)


def _all_voice_text(profile) -> str:
    parts = [
        profile.era_context,
        profile.public_impression,
        profile.deeper_dimensions,
        profile.source_notes,
        profile.personality.notes,
        profile.artistic_identity.notes,
        profile.musical_style.notes,
        profile.creative_process.notes,
    ]
    return "\n".join(parts).lower()


def _load_and_validate_every_profile():
    paths = sorted(_DATA.glob("*.json"))
    assert paths, f"No profiles found in {_DATA}"
    profiles = []
    for path in paths:
        raw = json.loads(path.read_text(encoding="utf-8"))
        p = validate_profile(raw)
        assert p.id == path.stem, f"{path.name}: id field {p.id!r} must match filename stem"
        profiles.append(p)
    return profiles


def test_all_profiles_validate_unique_ids_rich_source_notes():
    profiles = _load_and_validate_every_profile()
    ids = [p.id for p in profiles]
    assert len(ids) == len(set(ids)), f"Duplicate ids: {ids}"

    for p in profiles:
        assert p.source_notes.strip(), f"{p.id}: source_notes must be non-empty"

        assert p.public_impression.strip(), f"{p.id}: public_impression must be non-empty"
        assert p.deeper_dimensions.strip(), f"{p.id}: deeper_dimensions must be non-empty"

        for field_name, text in (
            ("public_impression", p.public_impression),
            ("deeper_dimensions", p.deeper_dimensions),
        ):
            assert len(text.strip()) >= 40, (
                f"{p.id}: {field_name} should carry substance (avoid one-line caricature capsules)"
            )

        blob = _all_voice_text(p)
        for bad in _FORBIDDEN_VOICE_MARKERS:
            assert bad not in blob, f"{p.id}: avoid caricature shortcut phrase {bad!r} in profile voice text"


@pytest.mark.parametrize(
    "composer_id",
    ["bach", "beethoven", "chopin", "mozart"],
)
def test_shipped_example_ids_exist(composer_id: str):
    assert (_DATA / f"{composer_id}.json").is_file()
