---
name: cee-onboarding
description: "First-run interview: learn who Chain is (work, goals, how they like things) and save it to memory."
version: 0.1.0
author: Chain
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [Onboarding, Profile, Memory, CEE]
    related_skills: [google-workspace]
---

# CEE Onboarding: "Who I Am"

Teach CEE who Chain is, so every later answer fits their work, goals, and style. This is step 4 of the setup ("Who I am").

## When to Use

- The first message ever, or USER.md is empty or nearly empty.
- "Get to know me", "onboard me", "รู้จักฉันหน่อย", "/cee-onboarding".
- Chain says their situation changed a lot (new job, new business, new goal).

## Procedure

### 1. Say what's happening
One line, in Chain's language: you'll ask about 6 quick questions so CEE can remember them. They can skip any question.

### 2. Ask one question at a time
Wait for each answer. Accept voice notes. Keep your follow-ups short.

1. **Work.** What do you do day to day? What are you building or selling right now?
2. **Goals.** What are your top 1–3 goals for the next 3 months? (Money, launches, audience, and so on.)
3. **Clients and audience.** Who do you make things for? Thai businesses? Which platforms: IG, TikTok, LINE, YouTube?
4. **Style.** How should CEE talk to you: language mix, how short, emoji or none? Anything that annoys you?
5. **Routine.** When do you usually work? Do you want a morning brief? At what time?
6. **Tools.** Which apps do you actually use: Gmail, Google Calendar, Drive, Notion, CapCut, Canva, and so on?

Done when all six are answered or skipped.

### 3. Save
Use the `memory` tool with target `user`. Write short, factual entries (for example "Goal Q4: land 3 paying ad clients at ≥15k THB each"). Stay under the USER.md limit and merge with existing entries instead of duplicating them. Put working facts about projects in the regular memory (target `memory`).

### 4. Offer next steps
Offer these in one short message. Don't set them up without a yes.

- Connect Google (Gmail, Calendar, Drive) with the `google-workspace` skill, if it isn't connected yet.
- A daily morning brief at the time Chain gave, using `/blueprint morning-brief time=HH:MM`.
- Voice replies with `/voice on`.

## Pitfalls

- Don't turn it into a form. Keep it conversational, one question per message.
- Never store passwords, API keys, bank details, or ID numbers.
- USER.md is small (about 1,400 characters). Compress; don't write essays.

## Verification

Read back a 3–5 bullet summary of what you saved. Ask "ถูกไหม / Anything wrong?"
