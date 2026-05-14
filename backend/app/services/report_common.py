from __future__ import annotations

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


def validate_report(data: dict[str, Any], source: str) -> AuraReport:
    stats = {name: clamp_int(data["stats"][name]) for name in STAT_NAMES}
    hidden_traits = {name: clamp_float(data["hidden_traits"][name]) for name in TRAIT_NAMES}
    mental_state = data["mental_state"]
    location = data["location"]

    if mental_state not in MENTAL_STATES:
        raise ValueError(f"{source} returned invalid mental_state")
    if location not in LOCATIONS:
        raise ValueError(f"{source} returned invalid location")

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
