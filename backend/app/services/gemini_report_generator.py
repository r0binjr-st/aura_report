from __future__ import annotations

import base64
import json
from pathlib import Path
from typing import Any

import httpx
from fastapi import HTTPException, UploadFile

from backend.app.config import get_settings
from backend.app.schemas.aura import AuraReport
from backend.app.services.report_common import report_schema, validate_report

PROMPT_PATH = Path(__file__).resolve().parents[1] / "prompts" / "gemini_report_generation.txt"


async def image_parts(photos: list[UploadFile]) -> list[dict[str, Any]]:
    parts: list[dict[str, Any]] = []
    for photo in photos[:3]:
        blob = await photo.read()
        await photo.seek(0)
        if not blob:
            continue
        parts.append(
            {
                "inline_data": {
                    "mime_type": photo.content_type or "image/jpeg",
                    "data": base64.b64encode(blob).decode("ascii"),
                }
            }
        )
    return parts


async def generate_report_with_gemini(
    photos: list[UploadFile],
    nickname: str,
    music: str,
    freeform_text: str,
) -> AuraReport:
    settings = get_settings()
    if not settings.gemini_api_key:
        raise HTTPException(status_code=500, detail="GEMINI_API_KEY is not configured")

    prompt = (
        f"{PROMPT_PATH.read_text(encoding='utf-8')}\n\n"
        "INPUT:\n"
        f"Nickname:\n{nickname}\n\n"
        f"Music field, usually artists/tracks/playlists:\n{music}\n\n"
        f"Freeform text:\n{freeform_text}\n"
    )
    parts: list[dict[str, Any]] = [{"text": prompt}]
    parts.extend(await image_parts(photos))

    body = {
        "contents": [{"role": "user", "parts": parts}],
        "generationConfig": {
            "responseMimeType": "application/json",
            "responseJsonSchema": report_schema(),
            "temperature": 1.05,
        },
    }
    url = (
        "https://generativelanguage.googleapis.com/v1beta/models/"
        f"{settings.gemini_model}:generateContent"
    )

    try:
        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(url, params={"key": settings.gemini_api_key}, json=body)
            response.raise_for_status()
            text = response.json()["candidates"][0]["content"]["parts"][0]["text"]
            data = json.loads(text)
            return validate_report(data, f"gemini:{settings.gemini_model}")
    except httpx.HTTPStatusError as exc:
        detail = exc.response.text[:1000]
        raise HTTPException(status_code=502, detail=f"Gemini API error: {detail}") from exc
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Gemini report generation failed: {exc}") from exc
