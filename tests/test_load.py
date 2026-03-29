from pathlib import Path

import pytest

from composer_system.exceptions import ProfileLoadError, ProfileValidationError
from composer_system.load import load_profile


def test_load_bach_from_repo_data():
    root = Path(__file__).resolve().parent.parent / "data" / "composers"
    p = load_profile("bach", data_dir=root)
    assert p.id == "bach"
    assert "Bach" in p.display_name


def test_load_rejects_traversal(tmp_path: Path):
    d = tmp_path / "composers"
    d.mkdir(parents=True)
    with pytest.raises(ProfileLoadError):
        load_profile("../etc/passwd", data_dir=d)


def test_load_id_mismatch(tmp_path: Path):
    d = tmp_path / "composers"
    d.mkdir(parents=True)
    f = d / "alpha.json"
    f.write_text('{"id": "beta", "display_name": "B"}', encoding="utf-8")
    with pytest.raises(ProfileLoadError, match="expected"):
        load_profile("alpha", data_dir=d)


def test_load_invalid_json(tmp_path: Path):
    d = tmp_path / "composers"
    d.mkdir(parents=True)
    (d / "bad.json").write_text("{", encoding="utf-8")
    with pytest.raises(ProfileLoadError, match="Invalid JSON"):
        load_profile("bad", data_dir=d)


def test_load_validation_error(tmp_path: Path):
    d = tmp_path / "composers"
    d.mkdir(parents=True)
    (d / "bad.json").write_text('{"id": "bad", "display_name": 1}', encoding="utf-8")
    with pytest.raises(ProfileValidationError):
        load_profile("bad", data_dir=d)
