import pytest

from composer_system.exceptions import ProfileValidationError
from composer_system.models import ComposerProfile
from composer_system.validate import validate_profile


def test_validate_minimal():
    p = validate_profile({"id": "x", "display_name": "X"})
    assert isinstance(p, ComposerProfile)
    assert p.id == "x"


def test_validate_rejects_bad_id():
    with pytest.raises(ProfileValidationError):
        validate_profile({"id": "Bad", "display_name": "X"})


def test_validate_full_matches_sample_shape():
    data = {
        "schema_version": "1.0",
        "id": "test_composer",
        "display_name": "Test Composer",
        "life_span": {"birth_year": 1900, "death_year": 1950},
        "era_context": "Example era.",
        "public_impression": "Public view.",
        "deeper_dimensions": "Deeper view.",
        "personality": {"traits": ["a"], "notes": "n"},
        "artistic_identity": {"aims": ["aim"], "notes": "n"},
        "musical_style": {"characteristic_elements": ["x"], "notes": "n"},
        "creative_process": {"habits": ["h"], "notes": "n"},
        "source_notes": "Interpretive.",
    }
    p = validate_profile(data)
    assert p.life_span.birth_year == 1900
