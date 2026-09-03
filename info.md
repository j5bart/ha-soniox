# Soniox

Speech-to-text and text-to-speech for Home Assistant powered by
[Soniox](https://soniox.com) — 60+ languages, low-latency streaming.

> **Disclaimer**: This is an unofficial project and is not affiliated with,
> endorsed by, or maintained by Soniox.

## Highlights

- Real-time STT (`stt-rt-v4`) — WebSocket streaming with final tokens.
- TTS (`tts-rt-v2`) — every voice speaks every language, with adjustable
  speaking rate and optional pause shortening.
- Model and voice lists read from your Soniox account, so new models show up
  on their own.
- Per-call voice and audio-format overrides.
- No external Python dependencies — built on Home Assistant's bundled `aiohttp`.

## Quick setup

1. Install via HACS, restart Home Assistant.
2. **Settings → Devices & Services → Add Integration → Soniox**.
3. Paste an API key from [console.soniox.com](https://console.soniox.com).
4. **Settings → Voice assistants** → set both STT and TTS engines to **Soniox**.

Full docs and configuration options:
[github.com/kororos/ha-soniox](https://github.com/kororos/ha-soniox).
