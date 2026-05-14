# Aura Report

Мемный мультимодальный AI vibe engine: пользователь загружает фото, вводит ник, музыку и свободный текст, а приложение выдает абсурдно-точный Aura Report.

Это не психологический тест и не диагностика. Это post-ironic internet artifact для друзей, локального лора и красивой карточки результата.

## Что уже есть в MVP

- FastAPI endpoint `POST /api/aura/analyze`
- multipart input: `photos`, `nickname`, `music`, `freeform_text`
- hidden trait система
- weighted fusion engine вместо чистого random
- строгие списки mental state и location
- обязательные stats
- статический frontend flow без Node.js
- loading screen с мемными сообщениями
- шарибельная карточка и copy report

## Запуск

```powershell
cd D:\aura_report
C:\Users\fario\AppData\Local\Programs\Python\Python310\python.exe -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r backend\requirements.txt
python -m uvicorn backend.app.main:app --reload --host 127.0.0.1 --port 8000
```

Открой:

```text
http://127.0.0.1:8000
```

## Модель

Проект работает через внешний multimodal LLM. Локальных правил для генерации отчета больше нет: модель сама генерирует проценты, состояние, локацию, архетип, диагноз, объяснение и hidden traits.

### Бесплатно: GroqCloud

В `.env`:

```env
LLM_PROVIDER=groq
GROQ_API_KEY=your_groq_key
GROQ_MODEL=meta-llama/llama-4-scout-17b-16e-instruct
```

Ключ: https://console.groq.com/ -> API Keys -> Create API Key.

Если в ответе API `analysis_source` начинается с `groq:`, работает GroqCloud.

### Бесплатный запасной вариант: OpenRouter Free

```env
LLM_PROVIDER=openrouter
OPENROUTER_API_KEY=your_openrouter_key
OPENROUTER_MODEL=openrouter/free
```

OpenRouter `openrouter/free` бесплатный, но с лимитами. Для аккаунта без купленных credits документация указывает 50 free-запросов в день и до 20 запросов в минуту для free-моделей.

### Grok / xAI

Grok оставлен как запасной платный провайдер:

```env
LLM_PROVIDER=xai
XAI_API_KEY=your_xai_key
XAI_MODEL=grok-4.3
```

### Gemini

Gemini оставлен как запасной провайдер:

1. Получи ключ в Google AI Studio: https://aistudio.google.com/app/apikey
2. В `.env` укажи:

```env
LLM_PROVIDER=gemini
GEMINI_API_KEY=your_gemini_key
GEMINI_MODEL=gemini-2.5-flash
```

Если в ответе API `analysis_source` начинается с `gemini:`, работает Gemini. Если ключ выбранного провайдера не задан или API недоступен, backend вернет ошибку, а не локальный fallback.

## Deploy на Render

Перед заливкой на GitHub проверь, что `.env` не попадает в репозиторий. Он уже добавлен в `.gitignore`.

На Render:

1. Создай Web Service или Blueprint из GitHub репозитория.
2. Build command:
   ```text
   pip install -r backend/requirements.txt
   ```
3. Start command:
   ```text
   uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT
   ```
4. Environment variables:
   ```text
   LLM_PROVIDER=groq
   GROQ_MODEL=meta-llama/llama-4-scout-17b-16e-instruct
   GROQ_API_KEY=твой ключ из Groq Console
   ```

Имя сервиса в `render.yaml`: `aura-report-trax`. Если оно свободно, публичная ссылка будет:

```text
https://aura-report-trax.onrender.com
```

Не коммить API-ключи в GitHub.

## API

```text
POST /api/aura/analyze
```

Form-data:

- `photos`: 1-3 image files
- `nickname`: string
- `music`: string
- `freeform_text`: string

Response:

```json
{
  "stats": {
    "арка злодея": 87,
    "темный друн": 94,
    "секс маньяк": 61,
    "М М": 2,
    "потапыч R.I.P": 38,
    "артем коршунов (джокер)": 91,
    "саша епифановский": 74,
    "сигма синдром": 69
  },
  "mental_state": "дофаминовое голодание",
  "location": "путилково (роковой поворот)",
  "archetype": "полуночный дискорд-злодей",
  "diagnosis": "опасен для группового чата после 23:00",
  "explanation": "...",
  "analysis_source": "groq:meta-llama/llama-4-scout-17b-16e-instruct",
  "observations": {
    "image": "...",
    "nickname": "...",
    "music": "...",
    "text": "..."
  },
  "hidden_traits": {}
}
```

## Следующие шаги

- Перенести frontend на Next.js, когда на машине появятся `node` и `npm`.
- Добавить сохранение карточки как изображения.
- Добавить dev/debug панель hidden traits.

