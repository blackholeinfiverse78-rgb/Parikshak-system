"""
Vaani TTS Service
Primary: gTTS (Google TTS) - works on all platforms including Linux servers
Fallback: pyttsx3 - local only (requires audio device, not available on servers)
"""
import io
import os
import re
import logging
import requests

logger = logging.getLogger("vaani_tts")


def remove_emojis(text: str) -> str:
    emoji_pattern = re.compile(
        "["
        "\U0001F600-\U0001F64F"
        "\U0001F300-\U0001F5FF"
        "\U0001F680-\U0001F6FF"
        "\U0001F1E0-\U0001F1FF"
        "\U00002702-\U000027B0"
        "\U000024C2-\U0001F251"
        "\U0001F900-\U0001F9FF"
        "\U00002600-\U000026FF"
        "]+",
        flags=re.UNICODE
    )
    return re.sub(r'\s+', ' ', emoji_pattern.sub('', text)).strip()


def translate_text(text: str, target_language: str = 'en') -> str:
    """Translate text using Groq API. Returns original text if unavailable."""
    if target_language.lower() == 'en':
        return text

    api_key = os.getenv('GROQ_API_KEY')
    if not api_key:
        return text

    language_names = {
        'es': 'Spanish', 'fr': 'French', 'de': 'German', 'it': 'Italian',
        'pt': 'Portuguese', 'ru': 'Russian', 'zh': 'Chinese (Simplified)',
        'ja': 'Japanese', 'ko': 'Korean', 'hi': 'Hindi', 'ar': 'Arabic',
    }
    target_lang_name = language_names.get(target_language.lower(), target_language)

    try:
        payload = {
            "model": "llama-3.1-8b-instant",
            "messages": [
                {"role": "system", "content": f"Translate to {target_lang_name}. Return ONLY the translation."},
                {"role": "user", "content": text}
            ],
            "temperature": 0.0,
            "max_tokens": min(len(text.split()) * 2 + 50, 300)
        }
        resp = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            json=payload,
            timeout=10
        )
        if resp.status_code == 200:
            return resp.json()['choices'][0]['message']['content'].strip().strip('"\'')
    except Exception as e:
        logger.warning(f"[TTS] Translation failed: {e}")

    return text


def _gtts_stream(text: str, language: str) -> bytes:
    """Generate audio using Google TTS. Returns MP3 bytes."""
    import urllib3
    import requests
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    from gtts import gTTS

    tts = gTTS(text=text, lang=language.lower(), slow=False)

    # Override the internal session to disable SSL verification
    session = requests.Session()
    session.verify = False
    tts.session = session

    buf = io.BytesIO()
    tts.write_to_fp(buf)
    buf.seek(0)
    data = buf.read()
    return data


def _pyttsx3_stream(text: str, language: str) -> bytes:
    """
    Generate audio using pyttsx3 (local fallback).
    Only works on machines with an audio device (not on Linux servers).
    """
    import tempfile
    import pyttsx3

    engine = pyttsx3.init()
    voices = engine.getProperty('voices') or []

    lang_keywords = {
        'en': ['english', 'zira', 'david', 'en-us'],
        'es': ['spanish', 'helena', 'es-es'],
        'fr': ['french', 'hortense', 'fr-fr'],
        'de': ['german', 'hedda', 'de-de'],
        'ar': ['arabic', 'hoda', 'ar-sa'],
    }.get(language.lower(), ['english'])

    for voice in voices:
        if any(k in voice.name.lower() or k in voice.id.lower() for k in lang_keywords):
            engine.setProperty('voice', voice.id)
            break

    engine.setProperty('rate', 175)
    engine.setProperty('volume', 0.9)

    with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as f:
        tmp = f.name

    try:
        engine.save_to_file(text, tmp)
        engine.runAndWait()
        with open(tmp, 'rb') as f:
            return f.read()
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


def text_to_speech_stream(
    text: str,
    language: str = 'en',
    use_google_tts: bool = True,
    translate: bool = True
) -> bytes:
    """
    Convert text to speech bytes.
    Returns MP3 bytes (gTTS) or WAV bytes (pyttsx3 fallback).
    Raises ValueError if text is empty.
    Raises RuntimeError if all engines fail.
    """
    if not text or not text.strip():
        raise ValueError("Text is required")

    text = remove_emojis(text)

    if translate and language.lower() != 'en':
        text = translate_text(text, language)

    # Primary: gTTS (works on all platforms)
    if use_google_tts:
        try:
            data = _gtts_stream(text, language)
            if data:
                return data
        except Exception as e:
            logger.warning(f"[TTS] gTTS failed: {e} — trying pyttsx3 fallback")

    # Fallback: pyttsx3 (local only)
    try:
        data = _pyttsx3_stream(text, language)
        if data:
            return data
    except Exception as e:
        logger.error(f"[TTS] pyttsx3 fallback failed: {e}")

    raise RuntimeError("All TTS engines failed. Check GTTS network access or pyttsx3 installation.")
