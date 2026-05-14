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


async def image_inputs(photos: list[UploadFile]) -> list[dict[str, Any]]:
    inputs: list[dict[str, Any]] = []
    for photo in photos[:3]:
        blob = await photo.read()
        await photo.seek(0)
        if not blob:
            continue
        mime_type = photo.content_type or "image/jpeg"
        data = base64.b64encode(blob).decode("ascii")
        inputs.append(
            {
                "type": "input_image",
                "image_url": f"data:{mime_type};base64,{data}",
                "detail": "high",
            }
        )
    return inputs


def extract_response_text(payload: dict[str, Any]) -> str:
    for item in payload.get("output", []):
        if item.get("type") != "message":
            continue
        for content in item.get("content", []):
            if content.get("type") == "output_text" and content.get("text"):
                return str(content["text"])
    raise ValueError("xAI response did not contain output_text")


async def generate_report_with_xai(
    photos: list[UploadFile],
    nickname: str,
    music: str,
    freeform_text: str,
) -> AuraReport:
    settings = get_settings()
    if not settings.xai_api_key:
        raise HTTPException(status_code=500, detail="XAI_API_KEY is not configured")

    prompt = (
        f"{PROMPT_PATH.read_text(encoding='utf-8')}\n\n"
        "INPUT:\n"
        f"Nickname:\n{nickname}\n\n"
        f"Music field, usually artists/tracks/playlists:\n{music}\n\n"
        f"Freeform text:\n{freeform_text}\n"
    )

    content: list[dict[str, Any]] = await image_inputs(photos)
    content.append({"type": "input_text", "text": prompt})
    schema = report_schema()

    body = {
        "model": settings.xai_model,
        "input": [{"role": "user", "content": content}],
        "temperature": 1.0,
        "text": {
            "format": {
                "type": "json_schema",
                "name": "aura_report",
                "schema": schema,
                "strict": True,
            }
        },
    }
    url = f"{settings.xai_base_url.rstrip('/')}/responses"
    headers = {
        "Authorization": f"Bearer {settings.xai_api_key}",
        "Content-Type": "application/json",
    }

    try:
        async with httpx.AsyncClient(timeout=90) as client:
            response = await client.post(url, headers=headers, json=body)
            response.raise_for_status()
            text = extract_response_text(response.json())
            data = json.loads(text)
            return validate_report(data, f"xai:{settings.xai_model}")
    except httpx.HTTPStatusError as exc:
        detail = exc.response.text[:1000]
        raise HTTPException(status_code=502, detail=f"xAI API error: {detail}") from exc
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"xAI report generation failed: {exc}") from exc
