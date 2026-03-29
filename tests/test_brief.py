from pathlib import Path

from composer_system.brief import get_brief
from composer_system.load import load_profile

_DATA = Path(__file__).resolve().parent.parent / "data" / "composers"


def test_get_brief_shape_and_determinism():
    profile = load_profile("chopin", data_dir=_DATA)
    b1 = get_brief(profile, "  nocturne about night  ")
    b2 = get_brief(profile, "  nocturne about night  ")
    assert b1 == b2
    assert b1["composer_id"] == "chopin"
    assert b1["intent"] == "nocturne about night"
    assert b1["output_target"] == "music_prompt_v1"
    assert set(b1["musical_direction"]) == {"aims", "style_elements", "process_habits"}
    assert isinstance(b1["seed"], dict)
