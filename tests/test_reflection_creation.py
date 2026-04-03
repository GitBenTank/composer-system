from pathlib import Path

import pytest

from composer_system.creation import creative_concepts
from composer_system.load import load_profile
from composer_system.models import ComposerProfile
from composer_system.reflection import structured_reflection

_DATA = Path(__file__).resolve().parent.parent / "data" / "composers"


def _minimal_profile() -> ComposerProfile:
    return ComposerProfile.model_validate({"id": "x", "display_name": "X"})


def test_structured_reflection_keys():
    r = structured_reflection(_minimal_profile())
    assert set(r) == {
        "subject",
        "impression_and_depth",
        "creative_identity",
        "epistemics",
        "prompt_fragments",
    }
    assert r["subject"]["id"] == "x"


def test_prompt_fragments_use_lists_only():
    p = ComposerProfile.model_validate(
        {
            "id": "y",
            "display_name": "Y",
            "personality": {"traits": ["calm"]},
            "source_notes": "Note.",
        }
    )
    fr = structured_reflection(p)["prompt_fragments"]
    assert any("calm" in s for s in fr)
    assert any("Source" in s for s in fr)


def test_creative_concepts_empty_lists():
    c = creative_concepts(_minimal_profile())
    assert c["concept_seeds"] == []


def test_creative_concepts_zips_rows():
    p = ComposerProfile.model_validate(
        {
            "id": "z",
            "display_name": "Z",
            "musical_style": {"characteristic_elements": ["a", "b"]},
            "creative_process": {"habits": ["p1"]},
        }
    )
    c = creative_concepts(p, max_seeds=5)
    assert len(c["concept_seeds"]) == 2
    row0, row1 = c["concept_seeds"]
    assert row0["musical_element"] == "a" and row0["process_habit"] == "p1"
    assert row1["musical_element"] == "b" and row1["process_habit"] == "p1"


def test_creative_concepts_is_deterministic_for_same_profile():
    p = ComposerProfile.model_validate(
        {
            "id": "q",
            "display_name": "Q",
            "personality": {"traits": ["bold"]},
            "artistic_identity": {"aims": ["aim-a"]},
            "musical_style": {"characteristic_elements": ["el-a"]},
            "creative_process": {"habits": ["hab-a"]},
        }
    )
    c1 = creative_concepts(p)
    c2 = creative_concepts(p)
    assert c1 == c2


def test_creative_concepts_chopin_non_empty_structured_seeds():
    profile = load_profile("chopin", data_dir=_DATA)
    c = creative_concepts(profile)
    c2 = creative_concepts(profile)
    assert c == c2

    seeds = c["concept_seeds"]
    assert len(seeds) >= 2
    row = seeds[0]
    assert row["seed_id"].startswith("chopin:")
    assert row["summary"]
    assert set(row["dimensions"]) <= {
        "artistic_aim",
        "musical_element",
        "personality_trait",
        "process_habit",
    }
    assert row["artistic_aim"] or row["musical_element"]


@pytest.mark.parametrize("composer_id", ["bach", "mozart"])
def test_creative_concepts_bundled_profiles_deterministic(composer_id: str):
    profile = load_profile(composer_id, data_dir=_DATA)
    assert creative_concepts(profile) == creative_concepts(profile)
    assert creative_concepts(profile)["concept_seeds"]
