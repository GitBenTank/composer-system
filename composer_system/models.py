"""Pydantic models: single source of truth for the composer profile schema."""

from __future__ import annotations

from pydantic import BaseModel, Field


class LifeSpan(BaseModel):
    birth_year: int | None = Field(default=None, ge=1000, le=2100)
    death_year: int | None = Field(default=None, ge=1000, le=2100)


class Personality(BaseModel):
    traits: list[str] = Field(default_factory=list, max_length=64)
    notes: str = Field(default="", max_length=20_000)


class ArtisticIdentity(BaseModel):
    aims: list[str] = Field(default_factory=list, max_length=64)
    notes: str = Field(default="", max_length=20_000)


class MusicalStyle(BaseModel):
    characteristic_elements: list[str] = Field(default_factory=list, max_length=64)
    notes: str = Field(default="", max_length=20_000)


class CreativeProcess(BaseModel):
    habits: list[str] = Field(default_factory=list, max_length=64)
    notes: str = Field(default="", max_length=20_000)


class ComposerProfile(BaseModel):
    """
    Structured creative identity for a historically grounded composer.

    Interpretive fields should stay clearly separated from well-attested facts;
    use ``source_notes`` to document epistemic stance where helpful.
    """

    schema_version: str = Field(
        default="1.0",
        pattern=r"^1\.\d+$",
        description="Schema version for migration and tooling.",
    )
    id: str = Field(
        ...,
        pattern=r"^[a-z][a-z0-9_-]*$",
        min_length=1,
        max_length=64,
        description="Stable slug, ASCII lowercase.",
    )
    display_name: str = Field(..., min_length=1, max_length=256)
    life_span: LifeSpan = Field(default_factory=LifeSpan)
    era_context: str = Field(
        default="",
        max_length=20_000,
        description="Brief historical/cultural framing; keep claims cautious.",
    )
    public_impression: str = Field(
        default="",
        max_length=20_000,
        description="How the figure is often perceived in public memory.",
    )
    deeper_dimensions: str = Field(
        default="",
        max_length=20_000,
        description="Nuanced traits beyond caricature.",
    )
    personality: Personality = Field(default_factory=Personality)
    artistic_identity: ArtisticIdentity = Field(default_factory=ArtisticIdentity)
    musical_style: MusicalStyle = Field(default_factory=MusicalStyle)
    creative_process: CreativeProcess = Field(default_factory=CreativeProcess)
    source_notes: str = Field(
        default="",
        max_length=20_000,
        description="What is well-attested vs interpretive; avoid overstating certainty.",
    )
