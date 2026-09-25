# -*- coding: utf-8 -*-
"""สมุดประจำตัวคนงาน - คำติจากหัวหน้า (CEE หรือเจ้าของงาน) แยกตามคนงาน

แต่ละคนงานมีสมุดของตัวเองใน worker_notes/<คนงาน>.md คนงานที่ใช้ AI อ่านสมุดตัวเองก่อนทำงานทุกครั้ง:
  script -> คนเขียนบท (brain.py ใส่ในพรอมต์เขียนบท)
  flow   -> คนสั่งภาพ Flow (บทบรรยายภาพเขียนโดยคนเขียนบท เลยใส่ในพรอมต์เขียนบทด้วย)
  qa     -> คนตรวจบั๊ก (qa_check.py ใส่ในทุกคำถามดูภาพ)
  edit / sound -> เป็นโค้ดล้วน อ่านสมุดไม่ได้ - คำติไปรอให้ห้องอัพเกรด/เจ้าของงานแก้โค้ด
"""
import io, os, datetime, threading

HERE = os.path.dirname(os.path.abspath(__file__))
DIR = os.path.join(HERE, "worker_notes")
WORKERS = {
    "script": "คนเขียนบท",
    "flow": "คนงาน Flow (ทำภาพ)",
    "qa": "คนตรวจบั๊ก",
    "edit": "ช่างตัด",
    "sound": "คนทำเสียง",
    "upgrade": "ห้องอัพเกรด",
}
_lock = threading.Lock()


def path(worker):
    return os.path.join(DIR, f"{worker}.md")


def add(worker, note, folder="", n="", by="CEE"):
    """จดคำติลงสมุดคนงาน - คืนบรรทัดที่จด"""
    if worker not in WORKERS:
        raise ValueError(f"ไม่รู้จักคนงาน '{worker}' (มี: {', '.join(WORKERS)})")
    note = " ".join(str(note).split())[:300]
    if not note:
        raise ValueError("คำติว่าง")
    where = f" {folder}" + (f" ช็อต {n}" if n not in ("", None) else "") if folder else ""
    line = f"- {datetime.date.today()}{where} ({by}): {note}"
    with _lock:
        os.makedirs(DIR, exist_ok=True)
        old = io.open(path(worker), encoding="utf-8").read() if os.path.exists(path(worker)) else ""
        if note in old:                       # คำติเดิมซ้ำ ไม่ต้องจดซ้ำ
            return line
        if not old:
            old = f"# สมุด{WORKERS[worker]} - ความผิดที่หัวหน้าจับได้ อ่านก่อนทำงานทุกครั้ง อย่าทำซ้ำ\n"
        io.open(path(worker), "w", encoding="utf-8").write(old + line + "\n")
    return line


def lines(worker, last=10):
    p = path(worker)
    if not os.path.exists(p):
        return []
    return [ln for ln in io.open(p, encoding="utf-8").read().splitlines() if ln.startswith("- ")][-last:]


def text(*workers, last=10):
    """คำติล่าสุดของคนงาน (ไว้แปะในพรอมต์) - ว่างถ้ายังไม่เคยโดนติ"""
    out = []
    for w in workers:
        out += lines(w, last)
    return "\n".join(out)


def all_notes(last=20):
    return {w: lines(w, last) for w in WORKERS}
