---
name: clip-factory
description: "Direct Chain's Clip Factory (localhost:8840): start clips, watch the belt, review finished videos, and blame the right worker so they learn."
version: 0.1.0
author: Chain
license: MIT
platforms: [windows, linux, macos]
metadata:
  hermes:
    tags: [Video, Factory, Director, QA, Feedback, Workers, CEE]
    related_skills: [ad-script, reel-breakdown, cee-brain]
---

# Clip Factory Director

Chain built a clip factory: a local server at `http://127.0.0.1:8840`. It has a 3D view in the browser and runs these workers:

| worker id | who | what they do | can they learn from notes? |
|---|---|---|---|
| `script` | script writer (Ollama/Gemini) | 8-shot Thai script + English picture descriptions | ✅ reads its notebook every script |
| `flow` | Flow worker | sends each shot's picture description to Google Flow and downloads the clip | ✅ via the script writer (the picture descriptions come from the script) |
| `qa` | 3 QA checkers | watch every shot (vision + Whisper) and reject bad ones (up to 4 tries) | ✅ reads its notebook before every look |
| `edit` | 2 editors | cut the finished shots into one clip | ⚠️ code only. Notes are for Chain / the upgrade room to fix |
| `sound` | sound | loudness, export, delivery | ⚠️ code only, same as `edit` |
| `upgrade` | upgrade room | reviews the factory's own work | ⚠️ |

**You are the director.** You don't do the workers' jobs. You give orders, check the result, and tell the right worker exactly what went wrong so the same mistake doesn't happen again.

## The remote

Everything goes through one script. Resolve your profile folder (HERMES_HOME) first, then run:

```
python "<HERMES_HOME>/skills/cee/clip-factory/scripts/factory_ctl.py" <command>
```

| command | use |
|---|---|
| `status` | What every worker is doing, which shots are on the belt, and why shots were rejected |
| `new "<topic>"` | Asks the script writer for a script. It is shown to you, not started yet. |
| `approve` / `reject` | Starts or drops that script |
| `retry <folder> <n>` | Remakes one shot |
| `history [k]` | The last finished clips (file paths) |
| `frames <video> [n]` | Makes one image of n frames with timestamps, so you can look at the clip |
| `blame <worker> "<note>" --folder <f> --shot <n>` | Writes a note in that worker's notebook. It also shows up in the 3D view. |
| `notes [worker]` | Shows what each worker has been told so far |
| `rules`, `stats` | The factory's rule library, and timing |

If it says the factory is not running, tell Chain to double-click **start.bat**. Don't try to start it yourself.

## Procedure

### Making a clip
1. `new "<topic>"`, then show Chain the 8 lines in short form.
2. Once Chain says ok (or already told you "just make it"), run `approve`.
3. When Chain asks "how's it going", run `status` and answer in 2–3 lines: which shots are done, which are being remade, and roughly how long is left.

### Reviewing a finished clip
1. `history 1` gets the newest file. Then `frames "<file>" 8`, and look at the image with vision.
2. Check it against this list. Each problem has an owner:

| problem you see or hear | blame |
|---|---|
| Boring or confusing hook, a wrong fact, lines too long, repeated, or not flowing | `script` |
| Wrong picture for the line, weird AI hands, floating or duplicate objects, a face in a hands-only shot, text burned into the picture, looks like a real person instead of the cartoon | `flow`, plus `qa` if QA let it pass (add "you missed …") |
| Cut lands in the middle of a word, jumpy cut, frozen frame, wrong shot order, captions wrong | `edit` |
| Too quiet or too loud, distorted, music drowning the voice | `sound` |

3. Write **one note per problem** with evidence, and say how to fix it. Good: `blame qa "shot 3 at 0:14 has two wrenches, one floating - count objects in every hands shot" --folder give-rustnut --shot 3`. Bad: `blame qa "bad job"`.
4. If the clip is unusable, `retry` the broken shots after blaming.
5. Report to Chain in one short message: **verdict** (✅ ship it / ⚠️ fixable / ❌ redo), what was wrong, who got blamed, and what's being fixed.

## Pitfalls
- **Blame fairly.** Only blame what you actually saw, with the time or shot. Never invent problems, and don't blame 3 workers for one mistake. If you can't tell whose fault it is, say so to Chain.
- Don't repeat a note that's already in `notes <worker>`. The worker already knows. Tell Chain it's happening again instead.
- `edit` and `sound` can't learn by themselves. After blaming them, tell Chain: "the editor keeps doing X, the code needs a fix".
- Never delete or move clips, and never edit the factory's files yourself.

## Verification
After `blame`, the line printed back starts with `- <date>`. After `approve`, `status` shows the new job in the queue or on the belt.
