from __future__ import annotations

from difflib import get_close_matches
from typing import Any

from backend.app.schemas.aura import AuraReport, LOCATIONS, MENTAL_STATES, STAT_NAMES, TRAIT_NAMES, Observations


def report_schema() -> dict[str, Any]:
    stats_props = {name: {"type": "integer", "minimum": 0, "maximum": 100} for name in STAT_NAMES}
    traits_props = {name: {"type": "number", "minimum": 0, "maximum": 1} for name in TRAIT_NAMES}
    return {
        "type": "object",
        "additionalProperties": False,
        "required": [
            "stats",
            "mental_state",
            "location",
            "archetype",
            "diagnosis",
            "explanation",
            "observations",
            "hidden_traits",
        ],
        "properties": {
            "stats": {
                "type": "object",
                "additionalProperties": False,
                "required": STAT_NAMES,
                "properties": stats_props,
            },
            "mental_state": {"type": "string", "enum": MENTAL_STATES},
            "location": {"type": "string", "enum": LOCATIONS},
            "archetype": {"type": "string"},
            "diagnosis": {"type": "string"},
            "explanation": {"type": "string"},
            "observations": {
                "type": "object",
                "additionalProperties": False,
                "required": ["image", "nickname", "music", "text"],
                "properties": {
                    "image": {"type": "string"},
                    "nickname": {"type": "string"},
                    "music": {"type": "string"},
                    "text": {"type": "string"},
                },
            },
            "hidden_traits": {
                "type": "object",
                "additionalProperties": False,
                "required": TRAIT_NAMES,
                "properties": traits_props,
            },
        },
    }


def clamp_int(value: Any) -> int:
    return max(0, min(100, int(round(float(value)))))


def clamp_float(value: Any) -> float:
    return round(max(0.0, min(1.0, float(value))), 3)


def coerce_choice(value: Any, allowed: list[str], fallback: str) -> str:
    text = str(value).strip()
    if text in allowed:
        return text

    lowered = {choice.casefold(): choice for choice in allowed}
    if text.casefold() in lowered:
        return lowered[text.casefold()]

    matches = get_close_matches(text, allowed, n=1, cutoff=0.55)
    return matches[0] if matches else fallback


def validate_report(data: dict[str, Any], source: str) -> AuraReport:
    stats = {name: clamp_int(data["stats"][name]) for name in STAT_NAMES}
    hidden_traits = {name: clamp_float(data["hidden_traits"][name]) for name in TRAIT_NAMES}
    mental_state = coerce_choice(data.get("mental_state"), MENTAL_STATES, MENTAL_STATES[0])
    location = coerce_choice(data.get("location"), LOCATIONS, LOCATIONS[0])

    return AuraReport(
        stats=stats,
        mental_state=mental_state,
        location=location,
        archetype=str(data["archetype"]),
        diagnosis=str(data["diagnosis"]),
        explanation=str(data["explanation"]),
        observations=Observations(**data["observations"]),
        analysis_source=source,
        hidden_traits=hidden_traits,
    )
