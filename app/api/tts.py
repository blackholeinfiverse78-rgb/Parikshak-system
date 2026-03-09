import sys
import os
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import Response
import logging
from dotenv import load_dotenv

load_dotenv()

# Add VaaniTTS_Standalone to path so it can be imported directly
_vaani_path = os.path.join(os.path.dirname(__file__), '..', '..', 'VaaniTTS_Standalone')
if _vaani_path not in sys.path:
    sys.path.insert(0, _vaani_path)

from tts_service import text_to_speech_stream  # noqa: E402
from prosody_mapper import generate_prosody_hint  # noqa: E402

router = APIRouter(prefix="/tts", tags=["TTS"])
logger = logging.getLogger("tts_api")

@router.get("/speak")
async def speak(
    text: str = Query(..., min_length=1),
    lang: str = Query("en"),
    tone: str = Query("neutral"),
    translate: bool = Query(True)
):
    """
    Generate speech using Vaani TTS Standalone.
    Returns audio/mpeg (MP3 via gTTS) or audio/wav (pyttsx3 fallback).
    """
    try:
        # 1. Generate prosody hint for logging/future use
        prosody = generate_prosody_hint(text, lang, tone)
        logger.info(f"TTS requested: lang={lang}, tone={prosody['tone']}, text_len={len(text)}")

        # 2. Get audio stream from Vaani TTS service
        # Uses gTTS (Google TTS) by default; falls back to pyttsx3 if needed
        audio_data = text_to_speech_stream(
            text=text,
            language=lang,
            use_google_tts=True,
            translate=translate
        )

        if not audio_data:
            raise HTTPException(status_code=500, detail="TTS service returned empty audio.")

        # gTTS returns MP3 bytes; pyttsx3 returns WAV bytes
        # Both are playable by HTML5 Audio
        media_type = "audio/mpeg"
        return Response(content=audio_data, media_type=media_type)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"TTS generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"TTS failed: {str(e)}")


@router.get("/prosody")
async def get_prosody(
    text: str = Query(..., min_length=1),
    lang: str = Query("ar"),
    tone: str = Query("educational")
):
    """
    Get Vaani prosody hint for given text, language, and tone.
    """
    try:
        return generate_prosody_hint(text, lang, tone)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
