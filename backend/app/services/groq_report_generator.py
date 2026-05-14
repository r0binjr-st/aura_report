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


async def generate_report_with_groq(
    photos: list[UploadFile],
    nickname: str,
    music: str,
    freeform_text: str,
) -> AuraReport:
    settings = get_settings()
    if not settings.groq_api_key:
        raise HTTPException(status_code=500, detail="GROQ_API_KEY is not configured")

    prompt = (
        f"{PROMPT_PATH.read_text(encoding='utf-8')}\n\n"
        "Return only valid JSON that matches this schema exactly:\n"
        f"{json.dumps(report_schema(), ensure_ascii=False)}\n\n"
        "INPUT:\n"
        f"Nickname:\n{nickname}\n\n"
        f"Music field, usually artists/tracks/playlists:\n{music}\n\n"
        f"Freeform text:\n{freeform_text}\n"
    )
    body = {
        "model": settings.groq_model,
        "messages": [
            {
                "role": "user",
                "content": await content_parts(photos, prompt),
            }
        ],
        "temperature": 1.0,
        "max_completion_tokens": 4096,
        "response_format": {"type": "json_object"},
    }
    url = f"{settings.groq_base_url.rstrip('/')}/chat/completions"
    headers = {
        "Authorization": f"Bearer {settings.groq_api_key}",
        "Content-Type": "application/json",
    }

    try:
        async with httpx.AsyncClient(timeout=90) as client:
            response = await client.post(url, headers=headers, json=body)
            response.raise_for_status()
            payload = response.json()
            text = payload["choices"][0]["message"]["content"]
            data = json.loads(text)
            model = payload.get("model") or settings.groq_model
            return validate_report(data, f"groq:{model}")
    except httpx.HTTPStatusError as exc:
        detail = exc.response.text[:1000]
        try:
            message = exc.response.json().get("error", {}).get("message", "")
        except Exception:
            message = ""
        if "invalid key" in message.lower() or "invalid api key" in message.lower():
            detail = "Groq API key is invalid. Rotate the key and update GROQ_API_KEY in Render environment variables."
        raise HTTPException(status_code=502, detail=f"Groq API error: {detail}") from exc
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Groq report generation failed: {exc}") from exc
