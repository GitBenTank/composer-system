"""Structured reflections derived only from validated profile fields (no LLM)."""

from __future__ import annotations

import hashlib
from typing import Any

from composer_system.models import ComposerProfile


def structured_reflection(profile: ComposerProfile) -> dict[str, Any]:
    """
    Build a nested reflection object for prompts or downstream tooling.

    All strings are taken from the profile; nothing is invented about history.
    """
    return {
        "subject": {
            "id": profile.id,
            "display_name": profile.display_name,
            "life_span": profile.life_span.model_dump(),
            "era_context": profile.era_context,
        },
        "impression_and_depth": {
            "public_impression": profile.public_impression,
            "deeper_dimensions": profile.deeper_dimensions,
        },
        "creative_identity": {
            "personality": profile.personality.model_dump(),
            "artistic_identity": profile.artistic_identity.model_dump(),
            "musical_style": profile.musical_style.model_dump(),
            "creative_process": profile.creative_process.model_dump(),
        },
        "epistemics": {"source_notes": profile.source_notes},
        "prompt_fragments": _prompt_fragments(profile),
    }


def human_reflection_summary(profile: ComposerProfile) -> str:
    """
    Short prose that weaves profile fields into a coherent creative identity.

    Uses only data present on the profile. Wording varies by composer id so
    adjacent figures do not read as copy-pasted; about two to four sentences.
    """
    name = profile.display_name

    sentences: list[str] = []

    s_open = _summary_opening(name, profile)
    if s_open:
        sentences.extend(s_open)

    s_recv = _summary_reception(profile)
    if s_recv:
        sentences.extend(s_recv)

    s_craft = _summary_craft(name, profile)
    if s_craft:
        sentences.append(s_craft)

    s_traits = _summary_traits(profile, len(sentences))
    if s_traits and len(sentences) < 4:
        sentences.append(s_traits)

    sentences = [s.strip() for s in sentences if s.strip()]
    if not sentences:
        return (
            f"{name} is represented by a sparse profile; add era, impression, style, "
            "and process fields to articulate a fuller creative identity."
        )

    if len(sentences) > 4:
        sentences = sentences[:4]
    return " ".join(sentences).strip()


def _voice_mod(profile: ComposerProfile, m: int) -> int:
    return int(hashlib.sha256(profile.id.encode()).hexdigest()[:8], 16) % max(m, 1)


def _era_core(profile: ComposerProfile, max_len: int) -> str:
    era = profile.era_context.strip()
    if not era:
        return ""
    return _strip_period(_clause_from_text(era, max_len=max_len))


def _summary_opening(name: str, profile: ComposerProfile) -> list[str]:
    era_c = _era_core(profile, 190)
    aims_raw = [a.strip() for a in profile.artistic_identity.aims if a.strip()]
    aims = _join_phrases(aims_raw[:2])

    if not era_c and not aims:
        return []

    v = _voice_mod(profile, 5)

    if era_c and aims:
        if v == 0:
            return [
                _fused_period(
                    f"{name} is charted against {era_c}",
                    f"named ambitions include {aims}",
                )
            ]
        if v == 1:
            return [f"In this construction, {name} is positioned within {era_c}, pursuing {aims}."]
        if v == 2:
            return [
                f"{_capitalize_first(era_c)}.",
                f"{name} is credited here with aims such as {aims}.",
            ]
        if v == 3:
            return [f"{name} moves inside a horizon described as {era_c}; priorities listed are {aims}."]
        return [f"Working assumptions about setting: {era_c}. Creative targets emphasized: {aims}."]

    if era_c:
        if v % 2 == 0:
            return [f"{name} is framed chiefly through {_capitalize_first(era_c)}."]
        return [f"The historical setting sketched for {name} is {_capitalize_first(era_c)}."]
    return [f"Stated aims for {name} center on {aims}."]


def _summary_reception(profile: ComposerProfile) -> list[str]:
    pub = _first_sentence_complete(profile.public_impression)
    deep = _first_sentence_complete(profile.deeper_dimensions)
    if not pub and not deep:
        return []

    v = _voice_mod(profile, 4)

    if pub and deep:
        p = _strip_period(pub)
        d = _strip_period(deep)
        if v == 0:
            return [_fused_period(p, _lower_first(d))]
        if v == 1:
            return [f"{p}, even as {_lower_first(d)}."]
        if v == 2:
            return [f"{_ensure_period(p)} {_ensure_period(_capitalize_first(d))}"]
        return [f"A shorthand reception: {p}; a counterbalance in this file: {_lower_first(d)}."]

    if pub:
        return [pub]
    return [deep]


def _summary_craft(name: str, profile: ComposerProfile) -> str:
    elements = [s.strip() for s in profile.musical_style.characteristic_elements if s.strip()]
    habits = [h.strip() for h in profile.creative_process.habits if h.strip()]
    style_notes = profile.musical_style.notes.strip()
    proc_notes = profile.creative_process.notes.strip()

    core = _join_phrases(elements[:3])
    habit_str = _join_phrases(habits[:2])
    v = _voice_mod(profile, 3)

    if core and habit_str:
        if v == 0:
            return f"Stylistic bullets highlight {core}. Described working routines return to {habit_str}."
        if v == 1:
            return f"The musical checklist stresses {core}; habits on record include {habit_str}."
        return f"Under style, {name} is tied to {core}; under process, the profile repeats {habit_str}."

    if core:
        snip = _strip_period(_primary_clause(style_notes, max_len=140)) if style_notes else ""
        if snip:
            if v % 2 == 0:
                return _fused_period(f"Listeners model {name} through {core}", snip.lower())
            return f"Musical emphases cluster on {core}, qualified by the note that {snip.lower()}."
        return f"Musical emphases cluster on {core}."

    if habit_str:
        pn = _strip_period(_primary_clause(proc_notes, max_len=140)) if proc_notes else ""
        if pn:
            return f"Habitual motion circles {habit_str}; commentary adds that {pn.lower()}."
        return f"Habitual motion in the dossier centers on {habit_str}."

    if style_notes:
        return _first_sentence_complete(style_notes)
    if proc_notes:
        return _first_sentence_complete(proc_notes)
    return ""


def _summary_traits(profile: ComposerProfile, already: int) -> str:
    traits = [t.strip() for t in profile.personality.traits if t.strip()]
    if not traits:
        return ""
    if already >= 3:
        return ""

    trait_line = _join_phrases(traits[:3])
    v = _voice_mod(profile, 2)
    if v == 0:
        return f"Personality tags sketched in this file include {trait_line}."
    return f"Traits on record read: {trait_line}."


def _fused_period(a: str, b: str) -> str:
    aa = _strip_period(a.strip())
    bb = b.strip()
    if not bb:
        return _ensure_period(aa)
    if not aa:
        return _ensure_period(bb)
    return f"{aa}; {bb}."


def _capitalize_first(s: str) -> str:
    s = s.strip()
    if not s:
        return s
    return s[0].upper() + s[1:]


def _primary_clause(text: str, *, max_len: int) -> str:
    """First survey-friendly clause, often splitting at ';' before clipping."""
    t = " ".join(text.strip().split())
    if not t:
        return ""
    if "; " in t:
        chunk = t.split("; ", 1)[0].strip()
        base = _ensure_period(chunk)
    else:
        base = _first_sentence_complete(t, soft_limit=max_len + 80)
    if len(base) > max_len:
        return _clip_at_boundary(_strip_period(base), max_len)
    return base


def _prompt_fragments(profile: ComposerProfile) -> list[str]:
    """Short, reusable clauses assembled from structured lists (still profile-bound)."""
    fragments: list[str] = []
    if profile.personality.traits:
        fragments.append(
            "Personality traits to respect: " + "; ".join(profile.personality.traits) + "."
        )
    if profile.artistic_identity.aims:
        fragments.append(
            "Artistic aims named in profile: " + "; ".join(profile.artistic_identity.aims) + "."
        )
    if profile.musical_style.characteristic_elements:
        fragments.append(
            "Musical fingerprints from profile: "
            + "; ".join(profile.musical_style.characteristic_elements)
            + "."
        )
    if profile.creative_process.habits:
        fragments.append(
            "Creative process habits from profile: "
            + "; ".join(profile.creative_process.habits)
            + "."
        )
    if profile.source_notes:
        fragments.append("Source / epistemic note: " + profile.source_notes)
    return fragments


def _first_sentence_complete(text: str, soft_limit: int = 280) -> str:
    """Return the first full sentence, or a clean bounded clause if none appears."""
    t = " ".join(text.strip().split())
    if not t:
        return ""
    for delim in (". ", "? ", "! "):
        idx = t.find(delim)
        if idx != -1:
            return (t[: idx + 1]).strip()
    return _clip_at_boundary(t, max_len=soft_limit)


def _cut_at_punctuation(text: str, max_len: int) -> str:
    """Prefer endings at ; or — before forcing a word boundary."""
    t = " ".join(text.strip().split())
    if not t or len(t) <= max_len:
        return t
    window = t[:max_len]
    for mark in ("; ", "—", ", "):
        cut = window.rfind(mark)
        if cut > max_len * 0.55:
            chunk = t[: cut + 1].strip().rstrip(",")
            return _ensure_period(chunk)
    return ""


def _clip_at_boundary(text: str, max_len: int) -> str:
    """Shorten at a word edge and close with a period—no mid-word ellipses."""
    t = " ".join(text.split())
    if not t:
        return ""
    if len(t) <= max_len:
        return _ensure_period(t)
    chunk = t[:max_len]
    last_space = chunk.rfind(" ")
    if last_space > max_len * 0.55:
        chunk = chunk[:last_space].rstrip(",;:")
    else:
        chunk = chunk.rstrip(",;:")
    return _ensure_period(chunk)


def _clause_from_text(text: str, max_len: int) -> str:
    """Pull a bounded, grammatical clause without dangling ellipses."""
    sent = _first_sentence_complete(text)
    if len(sent) <= max_len:
        return sent
    punct = _cut_at_punctuation(text, max_len)
    if punct:
        return punct
    return _clip_at_boundary(text, max_len)


def _ensure_period(s: str) -> str:
    s = s.strip()
    if not s:
        return s
    if s[-1] in ".!?":
        return s
    return s + "."


def _strip_period(s: str) -> str:
    s = s.strip()
    if not s:
        return s
    if s[-1] in ".!?":
        return s[:-1].strip()
    return s


def _lower_first(s: str) -> str:
    s = s.strip()
    if not s:
        return s
    return s[0].lower() + s[1:]


def _join_phrases(items: list[str]) -> str:
    cleaned = [i.rstrip(".") for i in items if i.strip()]
    if not cleaned:
        return ""
    if len(cleaned) == 1:
        return cleaned[0]
    if len(cleaned) == 2:
        return f"{cleaned[0]} and {cleaned[1]}"
    return ", ".join(cleaned[:-1]) + f", and {cleaned[-1]}"
