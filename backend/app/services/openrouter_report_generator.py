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


async def content_parts(
    photos: list[UploadFile],
    prompt: str,
) -> list[dict[str, Any]]:
    parts: list[dict[str, Any]] = [{"type": "text", "text": prompt}]
    for photo in photos[:3]:
        blob = await photo.read()
        await photo.seek(0)
        if not blob:
            continue
        mime_type = photo.content_type or "image/jpeg"
        data = base64.b64encode(blob).decode("ascii")
        parts.append(
            {
                "type": "image_url",
                "image_url": {
                    "url": f"data:{mime_type};base64,{data}",
                    "detail": "high",
                },
            }
        )
    return parts


def parse_content(content: Any) -> dict[str, Any]:
    if isinstance(content, list):
        text = "".join(
            item.get("text", "")
            for item in content
            if isinstance(item, dict) and item.get("type") in {"text", "output_text"}
        )
    else:
        text = str(content)
    return json.loads(text)


async def generate_report_with_openrouter(
    photos: list[UploadFile],
    nickname: str,
    music: str,
    freeform_text: str,
) -> AuraReport:
    settings = get_settings()
    if not settings.openrouter_api_key:
        raise HTTPException(status_code=500, detail="OPENROUTER_API_KEY is not configured")

    prompt = (
        f"{PROMPT_PATH.read_text(encoding='utf-8')}\n\n"
        "Return only valid JSON that matches the supplied schema.\n\n"
        "INPUT:\n"
        f"Nickname:\n{nickname}\n\n"
        f"Music field, usually artists/tracks/playlists:\n{music}\n\n"
        f"Freeform text:\n{freeform_text}\n"
    )
    schema = report_schema()
    body = {
        "model": settings.openrouter_model,
        "messages": [
            {
                "role": "user",
                "content": await content_parts(photos, prompt),
            }
        ],
        "temperature": 1.0,
        "provider": {"require_parameters": True},
        "response_format": {
            "type": "json_schema",
            "json_schema": {
                "name": "aura_report",
                "strict": True,
                "schema": schema,
            },
        },
    }
    url = f"{settings.openrouter_base_url.rstrip('/')}/chat/completions"
    headers = {
        "Authorization": f"Bearer {settings.openrouter_api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://aura-report.local",
        "X-Title": "Aura Report",
    }

    try:
        async with httpx.AsyncClient(timeout=90) as client:
            response = await client.post(url, headers=headers, json=body)
            response.raise_for_status()
            payload = response.json()
            data = parse_content(payload["choices"][0]["message"]["content"])
            model = payload.get("model") or settings.openrouter_model
            return validate_report(data, f"openrouter:{model}")
    except httpx.HTTPStatusError as exc:
        detail = exc.response.text[:1000]
        raise HTTPException(status_code=502, detail=f"OpenRouter API error: {detail}") from exc
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"OpenRouter report generation failed: {exc}") from exc
