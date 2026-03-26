import sys
import os
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import Response
import logging
from dotenv import load_dotenv

load_dotenv()

# Add VaaniTTS_Standalone to path
_vaani_path = os.path.join(os.path.dirname(__file__), '..', '..', 'VaaniTTS_Standalone')
if _vaani_path not in sys.path:
    sys.path.insert(0, _vaani_path)

from tts_service import text_to_speech_stream      # noqa: E402
from prosody_mapper import generate_prosody_hint   # noqa: E402

router = APIRouter(prefix="/tts", tags=["TTS"])
logger = logging.getLogger("tts_api")

_MAX_TEXT_LENGTH = 500  # characters — gTTS has limits on very long text


@router.get("/speak")
async def speak(
    text: str = Query(..., min_length=1, max_length=_MAX_TEXT_LENGTH),
    lang: str = Query("en"),
    tone: str = Query("neutral"),
    translate: bool = Query(False),
):
    """
    Generate speech audio from text.
    Returns audio/mpeg (MP3 via gTTS) or audio/wav (pyttsx3 fallback).
    """
    try:
        prosody = generate_prosody_hint(text, lang, tone)
        logger.info(f"[TTS] lang={lang} tone={prosody.get('tone')} chars={len(text)}")

        audio_data = text_to_speech_stream(
            text=text,
            language=lang,
            use_google_tts=True,
            translate=translate
        )

        if not audio_data:
            raise HTTPException(status_code=500, detail="TTS returned empty audio.")

        # Detect format: MP3 starts with ID3 or 0xFF 0xFB; WAV starts with RIFF
        media_type = "audio/wav" if audio_data[:4] == b'RIFF' else "audio/mpeg"

        return Response(
            content=audio_data,
            media_type=media_type,
            headers={"Cache-Control": "public, max-age=3600"}
        )

    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        logger.error(f"[TTS] All engines failed: {e}")
        raise HTTPException(status_code=503, detail="TTS service unavailable. Check network or gTTS access.")
    except Exception as e:
        logger.error(f"[TTS] Unexpected error: {e}")
        raise HTTPException(status_code=500, detail=f"TTS failed: {str(e)}")


@router.get("/prosody")
async def get_prosody(
    text: str = Query(..., min_length=1),
    lang: str = Query("ar"),
    tone: str = Query("educational"),
):
    """Get Vaani prosody hint for given text, language, and tone."""
    try:
        return generate_prosody_hint(text, lang, tone)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
