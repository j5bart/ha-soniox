"""Config flow for the Soniox integration."""

from __future__ import annotations

import logging
from typing import Any

import aiohttp
import voluptuous as vol

from homeassistant.config_entries import (
    ConfigEntry,
    ConfigFlow,
    ConfigFlowResult,
    OptionsFlow,
)
from homeassistant.core import callback
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.selector import (
    BooleanSelector,
    NumberSelector,
    NumberSelectorConfig,
    NumberSelectorMode,
    SelectOptionDict,
    SelectSelector,
    SelectSelectorConfig,
    SelectSelectorMode,
)

from .const import (
    CONF_API_KEY,
    CONF_STT_MODEL,
    CONF_TTS_AUDIO_FORMAT,
    CONF_TTS_LANGUAGE,
    CONF_TTS_MODEL,
    CONF_TTS_REDUCE_SILENCE,
    CONF_TTS_SAMPLE_RATE,
    CONF_TTS_SPEED,
    CONF_TTS_VOICE,
    DEFAULT_STT_MODEL,
    DEFAULT_TTS_AUDIO_FORMAT,
    DEFAULT_TTS_LANGUAGE,
    DEFAULT_TTS_MODEL,
    DEFAULT_TTS_REDUCE_SILENCE,
    DEFAULT_TTS_SAMPLE_RATE,
    DEFAULT_TTS_SPEED,
    DEFAULT_TTS_VOICE,
    DOMAIN,
    SUPPORTED_LANGUAGES,
    TTS_MODELS,
    TTS_MODELS_URL,
    TTS_SPEED_MAX,
    TTS_SPEED_MIN,
    TTS_SPEED_STEP,
    TTS_VOICES,
)

_LOGGER = logging.getLogger(__name__)

TTS_AUDIO_FORMATS = ["mp3", "wav", "pcm_s16le"]
TTS_SAMPLE_RATES = [8000, 16000, 24000, 44100, 48000]


async def _async_fetch_tts_models(
    session: aiohttp.ClientSession, api_key: str
) -> tuple[str | None, list[dict[str, Any]]]:
    """Fetch the TTS model catalog.

    Returns ``(error_key, models)``. ``error_key`` is None when the call
    succeeded, otherwise a translation key for the config-flow error slot.
    """
    try:
        async with session.get(
            TTS_MODELS_URL,
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=aiohttp.ClientTimeout(total=10),
        ) as resp:
            if resp.status == 401:
                return "invalid_auth", []
            if resp.status >= 400:
                return "cannot_connect", []
            payload = await resp.json()
    except aiohttp.ClientError:
        return "cannot_connect", []
    except TimeoutError:
        return "cannot_connect", []
    except ValueError:
        # A 200 that is not JSON still proves the key works.
        return None, []

    models = payload.get("models") if isinstance(payload, dict) else None
    return None, models if isinstance(models, list) else []


async def _validate_api_key(
    session: aiohttp.ClientSession, api_key: str
) -> str | None:
    """Return an error key, or None if the key works."""
    error, _ = await _async_fetch_tts_models(session, api_key)
    return error


def _model_ids(models: list[dict[str, Any]]) -> list[str]:
    """Model ids from the catalog, newest first, aliases last.

    Ids carry their version (tts-rt-v1, tts-rt-v2, ...), so a reverse sort is
    a good enough approximation of "newest first" for a dropdown. Aliases such
    as tts-rt-v1-preview point at a concrete model and are listed after it.
    """
    concrete: list[str] = []
    aliases: list[str] = []
    for model in models:
        model_id = model.get("id")
        if not isinstance(model_id, str):
            continue
        (aliases if model.get("aliased_model_id") else concrete).append(model_id)
    return sorted(concrete, reverse=True) + sorted(aliases, reverse=True)


def _voice_ids(models: list[dict[str, Any]]) -> list[str]:
    """Every voice offered by any model, in catalog order, deduplicated.

    The options form covers all models at once, so it offers the union rather
    than the voices of whichever model happens to be selected.
    """
    voices: list[str] = []
    for model in models:
        for voice in model.get("voices") or []:
            voice_id = voice.get("id") if isinstance(voice, dict) else None
            if isinstance(voice_id, str) and voice_id not in voices:
                voices.append(voice_id)
    return voices


def _silence_support(models: list[dict[str, Any]]) -> dict[str, bool]:
    """Map model id → whether it supports ``reduce_silence``.

    Only models that actually report the flag are included, so a catalog that
    omits it altogether reads as "unknown" rather than "unsupported".
    """
    return {
        m["id"]: bool(m["supports_silence_reduction"])
        for m in models
        if isinstance(m.get("id"), str) and "supports_silence_reduction" in m
    }


class SonioxConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Soniox."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Prompt for the API key."""
        errors: dict[str, str] = {}

        if user_input is not None:
            await self.async_set_unique_id(user_input[CONF_API_KEY][-8:])
            self._abort_if_unique_id_configured()

            session = async_get_clientsession(self.hass)
            error = await _validate_api_key(session, user_input[CONF_API_KEY])
            if error:
                errors["base"] = error
            else:
                return self.async_create_entry(title="Soniox", data=user_input)

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({vol.Required(CONF_API_KEY): str}),
            errors=errors,
        )

    async def async_step_reconfigure(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Allow updating the API key on an existing entry."""
        errors: dict[str, str] = {}
        entry = self._get_reconfigure_entry()

        if user_input is not None:
            session = async_get_clientsession(self.hass)
            error = await _validate_api_key(session, user_input[CONF_API_KEY])
            if error:
                errors["base"] = error
            else:
                return self.async_update_reload_and_abort(
                    entry, data={**entry.data, **user_input}
                )

        return self.async_show_form(
            step_id="reconfigure",
            data_schema=vol.Schema({vol.Required(CONF_API_KEY): str}),
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry) -> OptionsFlow:
        """Return the options flow."""
        return SonioxOptionsFlow()


class SonioxOptionsFlow(OptionsFlow):
    """Per-engine defaults that the user can change without re-adding the entry."""

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Show / save the options form."""
        errors: dict[str, str] = {}
        opts = self.config_entry.options

        # The catalog tells us which models and voices the account can use, so
        # a new Soniox model shows up here without an integration update. When
        # it is unreachable we fall back to the bundled lists rather than
        # blocking the form.
        session = async_get_clientsession(self.hass)
        fetch_error, models = await _async_fetch_tts_models(
            session, self.config_entry.data[CONF_API_KEY]
        )
        if fetch_error:
            _LOGGER.debug(
                "Could not fetch the Soniox TTS model catalog (%s); "
                "falling back to the bundled model and voice lists",
                fetch_error,
            )
        silence_support = _silence_support(models)

        if user_input is not None:
            model = user_input.get(CONF_TTS_MODEL, DEFAULT_TTS_MODEL)
            # Soniox rejects the whole request when reduce_silence is sent to a
            # model that does not support it, so catch it here instead.
            if user_input.get(CONF_TTS_REDUCE_SILENCE) and not silence_support.get(
                model, True
            ):
                errors[CONF_TTS_REDUCE_SILENCE] = "silence_not_supported"
            else:
                return self.async_create_entry(title="", data=user_input)
            opts = {**opts, **user_input}

        current_model = opts.get(CONF_TTS_MODEL, DEFAULT_TTS_MODEL)
        current_voice = opts.get(CONF_TTS_VOICE, DEFAULT_TTS_VOICE)
        model_ids = _model_ids(models) or list(TTS_MODELS)
        voice_ids = _voice_ids(models) or list(TTS_VOICES)
        # Keep a configured-but-unlisted model or voice selectable.
        if current_model not in model_ids:
            model_ids.append(current_model)
        if current_voice not in voice_ids:
            voice_ids.append(current_voice)

        lang_options = [
            SelectOptionDict(value=code, label=code) for code in SUPPORTED_LANGUAGES
        ]
        model_options = [SelectOptionDict(value=m, label=m) for m in model_ids]
        voice_options = [SelectOptionDict(value=v, label=v) for v in voice_ids]
        format_options = [
            SelectOptionDict(value=f, label=f) for f in TTS_AUDIO_FORMATS
        ]
        sample_rate_options = [
            SelectOptionDict(value=str(r), label=str(r)) for r in TTS_SAMPLE_RATES
        ]

        schema = vol.Schema(
            {
                vol.Optional(
                    CONF_STT_MODEL,
                    default=opts.get(CONF_STT_MODEL, DEFAULT_STT_MODEL),
                ): str,
                vol.Optional(
                    CONF_TTS_MODEL,
                    default=current_model,
                ): SelectSelector(
                    SelectSelectorConfig(
                        options=model_options,
                        mode=SelectSelectorMode.DROPDOWN,
                        custom_value=True,
                    )
                ),
                vol.Optional(
                    CONF_TTS_VOICE,
                    default=current_voice,
                ): SelectSelector(
                    SelectSelectorConfig(
                        options=voice_options,
                        mode=SelectSelectorMode.DROPDOWN,
                        custom_value=True,
                    )
                ),
                vol.Optional(
                    CONF_TTS_LANGUAGE,
                    default=opts.get(CONF_TTS_LANGUAGE, DEFAULT_TTS_LANGUAGE),
                ): SelectSelector(
                    SelectSelectorConfig(
                        options=lang_options, mode=SelectSelectorMode.DROPDOWN
                    )
                ),
                vol.Optional(
                    CONF_TTS_AUDIO_FORMAT,
                    default=opts.get(CONF_TTS_AUDIO_FORMAT, DEFAULT_TTS_AUDIO_FORMAT),
                ): SelectSelector(
                    SelectSelectorConfig(
                        options=format_options, mode=SelectSelectorMode.DROPDOWN
                    )
                ),
                vol.Optional(
                    CONF_TTS_SAMPLE_RATE,
                    default=str(
                        opts.get(CONF_TTS_SAMPLE_RATE, DEFAULT_TTS_SAMPLE_RATE)
                    ),
                ): SelectSelector(
                    SelectSelectorConfig(
                        options=sample_rate_options, mode=SelectSelectorMode.DROPDOWN
                    )
                ),
                vol.Optional(
                    CONF_TTS_SPEED,
                    default=float(opts.get(CONF_TTS_SPEED, DEFAULT_TTS_SPEED)),
                ): NumberSelector(
                    NumberSelectorConfig(
                        min=TTS_SPEED_MIN,
                        max=TTS_SPEED_MAX,
                        step=TTS_SPEED_STEP,
                        mode=NumberSelectorMode.SLIDER,
                    )
                ),
                vol.Optional(
                    CONF_TTS_REDUCE_SILENCE,
                    default=bool(
                        opts.get(CONF_TTS_REDUCE_SILENCE, DEFAULT_TTS_REDUCE_SILENCE)
                    ),
                ): BooleanSelector(),
            }
        )
        return self.async_show_form(step_id="init", data_schema=schema, errors=errors)
