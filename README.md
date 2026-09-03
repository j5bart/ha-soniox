# Soniox for Home Assistant

[![HACS Custom](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://hacs.xyz)
[![Validate](https://github.com/kororos/ha-soniox/actions/workflows/validate.yml/badge.svg)](https://github.com/kororos/ha-soniox/actions/workflows/validate.yml)
[![GitHub release (latest by date)](https://img.shields.io/github/v/release/kororos/ha-soniox)](https://github.com/kororos/ha-soniox/releases)
[![License: MIT](https://img.shields.io/github/license/kororos/ha-soniox)](https://github.com/kororos/ha-soniox/blob/main/LICENSE)

A custom Home Assistant integration that exposes [Soniox](https://soniox.com)
as both a **speech-to-text** and **text-to-speech** provider, ready to plug
into the Assist voice pipeline.

> **Disclaimer**: This is an unofficial project and is not affiliated with,
> endorsed by, or maintained by Soniox. The Soniox name and logo are used
> with permission for the purpose of this community integration.

- **STT** — real-time transcription via Soniox `stt-rt-v4` over WebSocket.
  Supports 60+ languages and sends low-latency final tokens as the user speaks.
- **TTS** — `tts-rt-v2` voices, both as a one-shot REST call and as a
  streaming WebSocket session (so LLM-generated text can start speaking before
  it's fully written).

## Installation

### Via HACS (recommended)

1. Open **HACS → Integrations** in Home Assistant.
2. Click the **⋮** menu → **Custom repositories**.
3. Add `https://github.com/kororos/ha-soniox` with category **Integration**.
4. Search for **Soniox**, install, then restart Home Assistant.
5. **Settings → Devices & Services → Add Integration → Soniox**.
6. Paste an API key from [console.soniox.com](https://console.soniox.com).

### Manual

Copy `custom_components/soniox/` into your Home Assistant `config/custom_components/`
directory, restart, and follow steps 5–6 above.

## Configuration

Open the integration's **Configure** screen to set defaults:

| Option              | Default      | Notes                                                                |
| ------------------- | ------------ | -------------------------------------------------------------------- |
| STT model           | `stt-rt-v4`  | Soniox real-time STT model.                                          |
| TTS model           | `tts-rt-v2`  | Soniox real-time TTS model (see below).                              |
| Default TTS voice   | `Maya`       | Any voice from the Soniox catalog (see below).                       |
| Default TTS language| `en`         | Two-letter ISO code.                                                 |
| TTS audio format    | `mp3`        | `mp3`, `wav`, or `pcm_s16le`.                                        |
| TTS sample rate     | `24000`      | Used only for raw/wav formats.                                       |
| TTS speaking rate   | `1.0`        | `0.7`–`1.3`. Sent only when it differs from `1.0`.                   |
| Shorten pauses      | off          | Soniox `reduce_silence`; needs `tts-rt-v2` or newer.                 |

Per-service-call overrides:

- `voice` — any voice name (Maya, Adrian, Kenji, Sofia, …).
- `audio_output` — `mp3`, `wav`, or `pcm_s16le`.

## Use it in the Assist pipeline

**Settings → Voice assistants → Assistant → Add assistant**, then pick the
`Soniox` STT entity and the `Soniox` TTS entity.

> **Note**: To use the browser mic icon on your laptop, Home Assistant must be
> served over HTTPS (browsers block microphone access on plain HTTP from
> non-localhost origins). The Home Assistant mobile apps don't have this
> restriction.

## TTS models

The **TTS model** and **voice** dropdowns are filled from your account's
[model catalog](https://soniox.com/docs/tts/models) (`GET
https://api.soniox.com/v1/tts-models`) each time the options screen opens, so a
newly released Soniox model appears without an update to this integration. If
the catalog can't be reached the bundled lists below are used instead, and both
dropdowns accept a typed-in value — which is also how you select a
[cloned voice](https://soniox.com/docs/tts/concepts/voice-cloning) by its id.

| Model       | Notes                                                                        |
| ----------- | ---------------------------------------------------------------------------- |
| `tts-rt-v2` | Default. Emotion and delivery control via audio tags, voice cloning, shorter pauses between sentences, better handling of names, numbers and identifiers. |
| `tts-rt-v1` | Deprecated by Soniox; removed on 2026-08-31, after which requests are served by `tts-rt-v2`. |

`tts-rt-v2` is a drop-in replacement for `tts-rt-v1` — existing entries keep
whatever model they were configured with, so switch the dropdown to `tts-rt-v2`
to pick up the newer model.

### Shorten pauses (`reduce_silence`)

`tts-rt-v2` can shorten the gaps between words, which is noticeably snappier for
Assist responses. Soniox rejects the option on models that don't support it, so
the options screen refuses to save that combination.

## Supported voices

`Maya`, `Daniel`, `Noah`, `Nina`, `Emma`, `Jack`, `Adrian`, `Claire`,
`Grace`, `Owen`, `Mina`, `Kenji`, `Rafael`, `Mateo`, `Lucia`, `Sofia`,
`Oliver`, `Arthur`, `Isla`, `Victoria`, `Cooper`, `Mason`, `Ruby`,
`Elise`, `Arjun`, `Rohan`, `Priya`, `Meera`. All voices speak all
supported languages. This is the fallback list; the live catalog is what the
options screen offers.

## Issues

Please file bugs and feature requests at
[github.com/kororos/ha-soniox/issues](https://github.com/kororos/ha-soniox/issues).

## License

MIT — see [LICENSE](LICENSE).
