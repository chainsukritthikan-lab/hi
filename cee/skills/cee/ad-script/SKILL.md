---
name: ad-script
description: "Write a short-form ad script (Reels/TikTok/Shorts, 15/30/60s) with hook options, timed beats, shot list, on-screen text — Thai or English."
version: 0.1.0
author: Chain
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [Ads, Video, Script, Reels, TikTok, Thai, Content]
    related_skills: [reel-breakdown, caption-pack]
---

# Short-Form Ad Script

Produce a script that can be filmed today and that a client would pay for.

## When to Use

- "Write an ad / script / reel for X", "เขียนสคริปต์โฆษณา...", "hook for my product".
- Rewriting or tightening an existing script.

## Procedure

### 1. Get the brief (only ask for what's missing)
You need:

- Product or offer
- Audience
- Their pain point
- The main win or result
- Proof, if there is any (numbers, reviews, before/after)
- The call to action
- Length: 15, 30, or 60 seconds. Default to 30.
- Language: default to the language Chain used.
- Platform

If Chain gives a link or a product name, search the web for real details. Never make up claims, prices, or reviews.

### 2. Write 5 hooks, each using a different formula
Formulas: call-out ("ถ้าคุณเป็น..."), shocking stat, contrarian, before/after, "stop doing X", POV, question, show the result first, mistake, secret or insider, challenge, and "I tried X for 7 days".

Each hook must be under 2 seconds spoken. That's about 8 English words or about 15 Thai syllables. Mark your top pick with ⭐.

### 3. Write the beat sheet using the top hook
Use this structure: Hook → Problem → Solution → Proof → Payoff → CTA.

For each beat, give:

- **Time range**, for example 0–2s
- **Voiceover line**
- **On-screen text**: 3–6 words, big
- **Shot**: framing and what's on screen
- **Edit note**: cut, zoom, sound effect, or b-roll

Speaking speed is about 2.5 English words per second and about 5–6 Thai syllables per second. Trim anything that runs over.

### 4. Finish
- One-line caption plus the CTA.
- Tell Chain they can ask for the `caption-pack` skill for a full caption and hashtags.
- Offer to save the script as a Google Doc if Google is connected.

## Output Shape

```
HOOKS
⭐ 1. ...
2. ...
...

SCRIPT — 30s — TH
[0–2s] HOOK
VO: ...
TEXT: ...
SHOT: ...
EDIT: ...
...
```

On Telegram, send the hooks in one message and the script in a second message.

## Pitfalls

- Generic hooks like "Are you tired of...?" are banned unless they're given a sharp twist.
- Don't use claims the product can't prove, especially health, money, or before/after results. Flag these as risky under Thai and Meta ad rules.
- Write Thai the way people speak, not formal written Thai.

## Verification

Add up the beat durations and check they match the target length within ±2 seconds. Check that every beat has VO, TEXT, and SHOT.
