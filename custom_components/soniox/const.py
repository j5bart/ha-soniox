"""Constants for the Soniox integration."""

from __future__ import annotations

from typing import Final

DOMAIN: Final = "soniox"

# Config / options keys
CONF_API_KEY: Final = "api_key"
CONF_STT_MODEL: Final = "stt_model"
CONF_TTS_MODEL: Final = "tts_model"
CONF_TTS_VOICE: Final = "tts_voice"
CONF_TTS_LANGUAGE: Final = "tts_language"
CONF_TTS_AUDIO_FORMAT: Final = "tts_audio_format"
CONF_TTS_SAMPLE_RATE: Final = "tts_sample_rate"
CONF_TTS_SPEED: Final = "tts_speed"
CONF_TTS_REDUCE_SILENCE: Final = "tts_reduce_silence"

# Soniox endpoints
STT_WEBSOCKET_URL: Final = "wss://stt-rt.soniox.com/transcribe-websocket"
TTS_REST_URL: Final = "https://tts-rt.soniox.com/tts"
TTS_WEBSOCKET_URL: Final = "wss://tts-rt.soniox.com/tts-websocket"
TTS_MODELS_URL: Final = "https://api.soniox.com/v1/tts-models"

# Defaults
DEFAULT_STT_MODEL: Final = "stt-rt-v4"
DEFAULT_TTS_MODEL: Final = "tts-rt-v2"
DEFAULT_TTS_VOICE: Final = "Maya"
DEFAULT_TTS_LANGUAGE: Final = "en"
DEFAULT_TTS_AUDIO_FORMAT: Final = "mp3"
DEFAULT_TTS_SAMPLE_RATE: Final = 24000
DEFAULT_TTS_SPEED: Final = 1.0
DEFAULT_TTS_REDUCE_SILENCE: Final = False

# Soniox accepts a speaking rate between these bounds; 1.0 is unmodified.
TTS_SPEED_MIN: Final = 0.7
TTS_SPEED_MAX: Final = 1.3
TTS_SPEED_STEP: Final = 0.05

# Fallback model list, used when the models endpoint cannot be reached while
# the options form is built. Soniox is the source of truth
# (https://soniox.com/docs/tts/models); tts-rt-v1 is deprecated and is removed
# on 2026-08-31, after which requests to it are served by tts-rt-v2.
TTS_MODELS: Final = ["tts-rt-v2", "tts-rt-v1"]

# Fallback voice list, used when the models endpoint cannot be reached while
# the options form is built. All voices speak all supported languages
# (https://soniox.com/docs/tts/models).
TTS_VOICES: Final = [
    "Maya", "Daniel", "Noah", "Nina", "Emma", "Jack", "Adrian", "Claire",
    "Grace", "Owen", "Mina", "Kenji", "Rafael", "Mateo", "Lucia", "Sofia",
    "Oliver", "Arthur", "Isla", "Victoria", "Cooper", "Mason", "Ruby",
    "Elise", "Arjun", "Rohan", "Priya", "Meera",
]

# Curated subset of the 60+ languages Soniox advertises. Used as the
# advertised supported_languages list for both STT and TTS — the Soniox
# models actually handle far more codes, but Home Assistant prefers a
# concrete list it can match assist-pipeline languages against.
SUPPORTED_LANGUAGES: Final = [
    "af", "ar", "az", "be", "bg", "bn", "bs", "ca", "cs", "cy", "da", "de",
    "el", "en", "es", "et", "eu", "fa", "fi", "fr", "gl", "gu", "he", "hi",
    "hr", "hu", "hy", "id", "is", "it", "ja", "kk", "kn", "ko", "lt", "lv",
    "mi", "mk", "ml", "mn", "mr", "ms", "ne", "nl", "no", "pa", "pl", "ps",
    "pt", "ro", "ru", "sk", "sl", "sq", "sr", "sv", "sw", "ta", "te", "th",
    "tl", "tr", "uk", "ur", "uz", "vi", "zh",
]
