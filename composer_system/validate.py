"""Validate raw dicts / JSON-decoded objects against the shared composer schema."""

from __future__ import annotations

import json
from typing import Any

from pydantic import ValidationError as PydanticValidationError

from composer_system.exceptions import ProfileValidationError
from composer_system.models import ComposerProfile


def validate_profile(data: dict[str, Any]) -> ComposerProfile:
    """
    Validate ``data`` and return a ``ComposerProfile``.

    Raises:
        ProfileValidationError: if the payload does not satisfy the schema.
    """
    try:
        return ComposerProfile.model_validate(data)
    except PydanticValidationError as e:
        raise ProfileValidationError(str(e)) from e


def profile_json_schema(*, indent: int | None = 2) -> str:
    """JSON Schema for ``ComposerProfile`` (for editors and external validators)."""
    schema = ComposerProfile.model_json_schema()
    return json.dumps(schema, indent=indent)
