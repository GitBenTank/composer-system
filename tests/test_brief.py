from pathlib import Path

import pytest

from composer_system.brief import get_brief
from composer_system.load import load_profile

_DATA = Path(__file__).resolve().parent.parent / "data" / "composers"


def test_get_brief_shape_and_determinism():
    profile = load_profile("chopin", data_dir=_DATA)
    b1 = get_brief(profile, "  nocturne about night  ")
    b2 = get_brief(profile, "  nocturne about night  ")
    assert b1 == b2
    assert b1["composer_id"] == "chopin"
    assert b1["trimmed_intent"] == "nocturne about night"
    assert b1["output_target"] == "music_prompt_v1"
    assert set(b1["musical_direction"]) == {"aims", "style_elements", "process_habits"}
    assert isinstance(b1["seed"], dict)


def test_get_brief_trimmed_intent_collapses_internal_space():
    profile = load_profile("chopin", data_dir=_DATA)
    b = get_brief(profile, "  slow  nocturne  ")
    assert b["trimmed_intent"] == "slow nocturne"


def test_get_brief_chopin_has_non_empty_musical_direction():
    profile = load_profile("chopin", data_dir=_DATA)
    b = get_brief(profile, "étude")
    md = b["musical_direction"]
    assert any(md["aims"])
    assert any(md["style_elements"])
    assert any(md["process_habits"])


def test_get_brief_seed_is_deterministic_for_same_inputs():
    profile = load_profile("bach", data_dir=_DATA)
    intent = "fugue subject in minor"
    s1 = get_brief(profile, intent)["seed"]
    s2 = get_brief(profile, intent)["seed"]
    assert s1 == s2
    assert s1


def test_get_brief_seed_changes_when_intent_changes():
    profile = load_profile("bach", data_dir=_DATA)
    a = get_brief(profile, "fugue")["seed"]
    b = get_brief(profile, "chorale prelude")["seed"]
    assert a and b
    assert a != b


@pytest.mark.parametrize("composer_id", ["bach", "mozart"])
def test_get_brief_non_empty_payload(composer_id: str):
    profile = load_profile(composer_id, data_dir=_DATA)
    b = get_brief(profile, "sketch")
    assert b["composer_id"] == composer_id
    assert b["trimmed_intent"] == "sketch"
    assert b["seed"]
