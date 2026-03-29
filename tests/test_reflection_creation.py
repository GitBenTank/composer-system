from composer_system.creation import creative_concepts
from composer_system.models import ComposerProfile
from composer_system.reflection import structured_reflection


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