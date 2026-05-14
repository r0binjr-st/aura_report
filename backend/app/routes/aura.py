from __future__ import annotations

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from backend.app.config import get_settings
from backend.app.schemas.aura import AuraReport
from backend.app.services.gemini_report_generator import generate_report_with_gemini
from backend.app.services.groq_report_generator import generate_report_with_groq
from backend.app.services.openrouter_report_generator import generate_report_with_openrouter
from backend.app.services.xai_report_generator import generate_report_with_xai

router = APIRouter(prefix="/api/aura", tags=["aura"])


@router.post("/analyze", response_model=AuraReport)
async def analyze_aura(
    photos: list[UploadFile] = File(default=[]),
    nickname: str = Form(...),
    music: str = Form(...),
    freeform_text: str = Form(...),
) -> AuraReport:
    limited_photos = photos[:3]
    provider = get_settings().llm_provider.lower().strip()
    if provider == "groq":
        return await generate_report_with_groq(limited_photos, nickname, music, freeform_text)
    if provider in {"openrouter", "free"}:
        return await generate_report_with_openrouter(limited_photos, nickname, music, freeform_text)
    if provider in {"xai", "grok"}:
        return await generate_report_with_xai(limited_photos, nickname, music, freeform_text)
    if provider == "gemini":
        return await generate_report_with_gemini(limited_photos, nickname, music, freeform_text)
    raise HTTPException(status_code=500, detail=f"Unsupported LLM_PROVIDER: {provider}")
