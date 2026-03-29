"""Guardrails on human_reflection_summary wording (no stale template leakage)."""

from __future__ import annotations

from pathlib import Path

import pytest

from composer_system.load import load_profile
from composer_system.reflection import human_reflection_summary

_DATA = Path(__file__).resolve().parent.parent / "data" / "composers"

_BANNED_SUBSTRINGS = (
    "the file foregrounds",
    "Public memory, in shorthand, is modeled as",
    "the capsule adds that",
)


@pytest.mark.parametrize("composer_id", ["bach", "beethoven", "chopin", "mozart"])
def test_human_summary_avoids_stale_template_phrases(composer_id: str) -> None:
    profile = load_profile(composer_id, data_dir=_DATA)
    text = human_reflection_summary(profile)
    assert text.strip()
    lower = text.lower()
    for bad in _BANNED_SUBSTRINGS:
        assert bad.lower() not in lower, f"{composer_id}: summary must not contain {bad!r}"
