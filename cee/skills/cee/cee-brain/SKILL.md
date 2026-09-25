---
name: cee-brain
description: "CEE's long-term memory in Chain's Obsidian vault: recall before answering, save what matters after. Projects, people, ideas, daily log."
version: 0.1.0
author: Chain
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [Memory, Obsidian, Second-Brain, Notes, CEE]
    related_skills: [obsidian, cee-onboarding]
---

# CEE Brain (Obsidian)

The Obsidian vault is CEE's long-term memory. Chain can open it in Obsidian, read it and edit it. Treat what's in it as true unless Chain says otherwise.

## Vault

- **Path:** `OBSIDIAN_VAULT_PATH` from the profile `.env`. Resolve it to an absolute path once, then use the file tools (see the `obsidian` skill).
- **Layout:**
  - `Home.md`: index
  - `About Chain.md`: who Chain is, their goals, and how they like things done
  - `Projects/<name>.md`
  - `People/<name>.md`
  - `Ideas/<title>.md`
  - `Daily/YYYY-MM-DD.md`: a short log of each day's conversations and decisions
- Create a folder or note if it doesn't exist yet. Link notes with `[[Note Name]]`.

## When to Use

- **Recall:** before answering anything about Chain's past, projects, clients, people, plans or preferences ("what did we decide about…", "remind me…", "my project X"). Search the vault first with `search_files`, `target: content`, and `file_glob: *.md`.
- **Save:** whenever something new is worth keeping, such as:
  - a decision
  - a new project or client
  - a person's details
  - an idea
  - a preference
  - a task outcome
  - a script or caption Chain liked
- **"Remember this" / "จำไว้":** save it right away and confirm in one line.

## Procedure

### 1. Recall
Search the vault for the key nouns (project name, person, topic). Read the top 1–3 matching notes. Use what you find, and say "from your notes…" when it matters.

### 2. Save
Update the right note. Check whether it already exists before creating a new one.
- Projects, people and ideas: keep one note per thing. Update the existing note; don't create duplicates.
- Daily log: append 1–3 bullets to `Daily/<today>.md` under `## Log`, e.g. `- 14:20 Decided the café ad hook: "POV: your coffee knows your name" → [[Café Ad]]`.
- Keep entries short and factual. Always put the date on decisions.

### 3. Built-in memory vs the vault
- The built-in `memory` tool (USER.md / MEMORY.md) holds a tiny always-loaded summary: Chain's top facts and the vault path.
- The vault holds everything else in detail.

## Pitfalls

- Never write passwords, API keys, bank or ID numbers into the vault.
- Don't rewrite or delete notes Chain wrote without asking. Appending is fine.
- Don't log small talk. Only log what Chain would want to find later.

## Verification

After saving, the note exists at the resolved path and has the new line. On request, show Chain the note name so they can open it in Obsidian.
