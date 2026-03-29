"""Load composer profiles from disk with path confinement."""

from __future__ import annotations

import json
from pathlib import Path

from composer_system.exceptions import ProfileLoadError
from composer_system.models import ComposerProfile
from composer_system.validate import validate_profile

_DEFAULT_NAME = "composers"


def _resolved_data_root(root: Path) -> Path:
    try:
        return root.expanduser().resolve(strict=False)
    except OSError as e:
        raise ProfileLoadError(f"Cannot resolve data directory: {e}") from e


def _safe_json_path(data_dir: Path, composer_id: str) -> Path:
    if not composer_id or "\x00" in composer_id:
        raise ProfileLoadError("Invalid composer id.")
    raw = Path(composer_id)
    if raw.name != str(raw) or raw.suffix:
        raise ProfileLoadError("Composer id must be a single path segment without suffix.")
    data_dir = _resolved_data_root(data_dir)
    if not data_dir.is_dir():
        raise ProfileLoadError(f"Data directory is not a directory: {data_dir}")
    candidate = (data_dir / f"{composer_id}.json").resolve()
    try:
        candidate.relative_to(data_dir)
    except ValueError as e:
        raise ProfileLoadError("Composer path escapes data directory.") from e
    return candidate


def load_profile(composer_id: str, *, data_dir: Path | None = None) -> ComposerProfile:
    """
    Load ``{composer_id}.json`` from ``data_dir`` (default: ``<cwd>/data/composers``).

    Only basenames are allowed; directory traversal is rejected.
    """
    root = data_dir if data_dir is not None else Path.cwd() / "data" / _DEFAULT_NAME
    path = _safe_json_path(root, composer_id)
    if not path.is_file():
        raise ProfileLoadError(f"Profile not found: {path}")
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as e:
        raise ProfileLoadError(f"Cannot read profile: {e}") from e
    try:
        raw = json.loads(text)
    except json.JSONDecodeError as e:
        raise ProfileLoadError(f"Invalid JSON in {path}: {e}") from e
    if not isinstance(raw, dict):
        raise ProfileLoadError(f"Profile root must be a JSON object: {path}")
    profile = validate_profile(raw)
    if profile.id != composer_id:
        raise ProfileLoadError(
            f"File {path} has id {profile.id!r}, expected {composer_id!r}."
        )
    return profile
