# Clip Factory × CEE add-on

Connects CEE (the Hermes agent) to Chain's Clip Factory as its **director**.

- `worker_notes.py`: a notebook per worker (`worker_notes/<worker>.md`). Notes CEE writes are read by the script writer (script + flow notes, inside the script prompt) and by the QA checker (qa notes, prepended to every vision question). `edit` and `sound` are code-only; their notes are for Chain or the upgrade room.
- `patch_factory.py`: adds `GET/POST /api/feedback` to `factory.py` and the notebook reads to `brain.py` and `qa_check.py`. It backs up each file as `*.before-cee` and is safe to run twice.
- Install on Windows: `cee/factory-connect.ps1`. CEE's side lives in `cee/skills/cee/clip-factory/`.

Undo: copy each `*.before-cee` file back over the original.
