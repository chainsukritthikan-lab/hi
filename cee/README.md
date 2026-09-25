# CEE 🟢

Chain's personal AI agent: a Jarvis you can actually use, named **CEE**.

Built on [Hermes Agent](https://github.com/NousResearch/hermes-agent) (Nous Research, MIT) as a **profile distribution**. You talk to it on Telegram, by text or voice, in Thai or English.

| Step (from the reel) | CEE |
|---|---|
| Agent harness | Hermes Agent, free and open source |
| Pick the brain | Google Gemini (free tier). Swap anytime with `cee model`, e.g. to Claude. |
| Who I am | `SOUL.md` (CEE's personality) + `/cee-onboarding` (learns about you) |
| Long-term memory | Built-in memory + Holographic fact store, both local and free |
| Skills | `ad-script`, `reel-breakdown`, `caption-pack`, `cee-onboarding` + Hermes' built-in skills |
| Tools | Gmail, Calendar, Drive and Docs (`google-workspace`), web search, browser |
| Channels + voice | Telegram, voice notes in (local Whisper), voice replies out (Edge TTS, Thai voice) |
| Always on | Oracle Cloud Always Free VM, systemd service |

👉 **Start here:** [SETUP.md](SETUP.md)

## Files

```
cee/
├── distribution.yaml   # manifest + required keys
├── SOUL.md             # who CEE is
├── config.yaml         # brain, memory, voice, web, safety
└── skills/cee/         # CEE's own skills
```

To edit CEE's personality or skills, change the files here, push, then run `hermes profile update cee` on the server.
