"""Structured reflections derived only from validated profile fields (no LLM)."""

from __future__ import annotations

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

    Uses only data present on the profile; favors varied pacing, sound wrapped
    with its caveats, and reception set against depth—without extra-template
    phrasing between composers.
    """
    name = profile.display_name
    v = sum(ord(c) for c in profile.id) % 3
    sentences: list[str] = []

    era = _first_sentence_complete(profile.era_context)
    aims = [a.strip() for a in profile.artistic_identity.aims if a.strip()]
    aim_phrase = _join_phrases(aims[:2])
    milieu = _milieu_sentence(name, era, aim_phrase, v)
    if milieu:
        sentences.append(milieu)

    pub = _first_sentence_complete(profile.public_impression)
    deep = _first_sentence_complete(profile.deeper_dimensions)
    recv = _reception_sentence(pub, deep, v)
    if recv:
        sentences.append(recv)

    craft = _sound_and_work_sentence(profile, name, v)
    if craft:
        sentences.append(craft)

    if not sentences:
        return (
            f"{name} is represented by a sparse profile; add era, impression, style, "
            "and process fields to articulate a fuller creative identity."
        )

    text = " ".join(sentences)
    parts = _split_sentences(text)
    if len(parts) > 4:
        parts = parts[:4]
    return " ".join(parts).strip()


def _milieu_sentence(name: str, era: str, aim_phrase: str, v: int) -> str:
    if era and aim_phrase:
        era_core = _strip_period(_clause_from_text(era, max_len=220))
        if v == 0:
            return (
                f"{name} is read alongside priorities such as {aim_phrase}, "
                f"within a historical frame summarized as {era_core}."
            )
        if v == 1:
            return (
                f"Within a milieu described as {era_core}, this portrait highlights "
                f"aims including {aim_phrase} for {name}."
            )
        return (
            f"For {name}, aims like {aim_phrase} are set against a backdrop "
            f"characterized as {era_core}."
        )
    if era:
        era_snip = _strip_period(_clause_from_text(era, max_len=220))
        return f"The surrounding context for {name} is summarized as {era_snip}."
    if aim_phrase:
        return f"The artistic priorities emphasized for {name} include {aim_phrase}."
    return ""


def _reception_sentence(pub: str, deep: str, v: int) -> str:
    if pub and deep:
        p = _strip_period(pub)
        d = _strip_period(deep)
        if v == 0:
            return f"{p}; {_lower_first(d)}."
        if v == 1:
            return f"{p}, though {_lower_first(d)}."
        return f"{p}, while {_lower_first(d)}."
    if pub:
        return pub
    if deep:
        return deep
    return ""


def _sound_and_work_sentence(profile: ComposerProfile, name: str, v: int) -> str:
    elements = [s.strip() for s in profile.musical_style.characteristic_elements if s.strip()]
    style_notes = profile.musical_style.notes.strip()
    habits = [h.strip() for h in profile.creative_process.habits if h.strip()]
    proc_notes = profile.creative_process.notes.strip()

    core = _join_phrases(elements[:3])
    habit_str = _join_phrases(habits[:2])
    qual = _qualification_tail(style_notes)
    proc_d = _process_tail(proc_notes)

    if core and habit_str:
        if v == 0:
            return (
                f"The sound-world associated with {name} turns on {core}{qual}; "
                f"habitual labor keeps circling back to {habit_str}{proc_d}."
            )
        if v == 1:
            return (
                f"{name}'s sonic fingerprint, in this reading, is built from {core}{qual}; "
                f"day-to-day work reverts again to {habit_str}{proc_d}."
            )
        return (
            f"Sonically the profile highlights {core}{qual}, "
            f"anchoring practice in {habit_str}{proc_d}."
        )

    if core and qual:
        return f"The sonic emphasis falls on {core}{qual}."
    if core:
        return f"The sonic emphasis falls on {core}."
    if habit_str and proc_d:
        return (
            f"In the workshop, {name} is sketched as moving between {habit_str}{proc_d}."
        )
    if habit_str and qual:
        return f"Recurring working motions pivot on {habit_str}{qual}."
    if habit_str:
        return f"Recurring working motions pivot on {habit_str}."
    if style_notes:
        return _first_sentence_complete(style_notes)
    if proc_notes:
        return _first_sentence_complete(proc_notes)
    return ""


def _qualification_tail(notes: str, *, max_len: int = 170) -> str:
    if not notes:
        return ""
    clause = _primary_clause(notes, max_len=max_len)
    if not clause:
        return ""
    body = _lower_first(_strip_period(clause))
    return f", although {body}"


def _process_tail(proc_notes: str, *, max_len: int = 170) -> str:
    if not proc_notes:
        return ""
    clause = _primary_clause(proc_notes, max_len=max_len)
    if not clause:
        return ""
    c = _strip_period(clause.strip())
    return f" — {c}"


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


def _clause_from_text(text: str, max_len: int) -> str:
    """Pull a bounded, grammatical clause without dangling ellipses."""
    sent = _first_sentence_complete(text)
    if len(sent) <= max_len:
        return sent
    punct = _cut_at_punctuation(text, max_len)
    if punct:
        return punct
    return _clip_at_boundary(text, max_len)


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


def _split_sentences(text: str) -> list[str]:
    out: list[str] = []
    buf: list[str] = []
    i = 0
    t = text.strip()
    while i < len(t):
        buf.append(t[i])
        if t[i] in ".!?" and (i + 1 >= len(t) or t[i + 1].isspace()):
            out.append("".join(buf).strip())
            buf = []
        i += 1
    tail = "".join(buf).strip()
    if tail:
        out.append(tail)
    return [s for s in out if s]
