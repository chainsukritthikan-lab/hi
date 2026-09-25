# -*- coding: utf-8 -*-
"""ติดตั้งส่วนเสริม CEE ลงโรงงานคลิป (แก้ factory.py, brain.py, qa_check.py แบบปลอดภัย รันซ้ำได้)

    python patch_factory.py "C:\\path\\to\\clip-factory"

- สำรองไฟล์เดิมเป็น *.before-cee ก่อนแก้ครั้งแรก
- เพิ่ม worker_notes.py (สมุดคนงาน) และประตู /api/feedback ให้ CEE ติคนงานได้
- คนเขียนบทอ่านสมุด script+flow, คนตรวจอ่านสมุด qa ก่อนทำงานทุกครั้ง
"""
import io, os, sys, shutil

MARK = "# [cee-addon]"


def patch(path, anchor, insert, tag, where="after"):
    src = io.open(path, encoding="utf-8").read()
    if f"{MARK}:{tag}" in src:
        return "มีอยู่แล้ว"
    insert = insert.replace(MARK, f"{MARK}:{tag}", 1)
    if where == "before":
        insert = insert.lstrip("\n") + "\n"
    if anchor not in src:
        raise SystemExit(f"หาไม่เจอใน {os.path.basename(path)}: {anchor[:60]!r} - โค้ดโรงงานอาจเปลี่ยนไป ส่งไฟล์ให้ดูก่อน")
    if not os.path.exists(path + ".before-cee"):
        shutil.copy2(path, path + ".before-cee")
    new = src.replace(anchor, anchor + insert if where == "after" else insert + anchor, 1)
    io.open(path, "w", encoding="utf-8").write(new)
    return "แก้แล้ว"


def main(root):
    root = os.path.abspath(root)
    for f in ("factory.py", "brain.py", "qa_check.py"):
        if not os.path.exists(os.path.join(root, f)):
            raise SystemExit(f"ไม่เจอ {f} ใน {root}")
    shutil.copy2(os.path.join(os.path.dirname(os.path.abspath(__file__)), "worker_notes.py"), os.path.join(root, "worker_notes.py"))

    # 1) factory.py: ประตู /api/feedback (POST จดคำติ, GET อ่านสมุด)
    get_block = f'''
        if self.path.startswith("/api/feedback"):   {MARK}
            import worker_notes
            return self._json({{"workers": worker_notes.WORKERS, "notes": worker_notes.all_notes()}})'''
    post_block = f'''
        if self.path.startswith("/api/feedback"):   {MARK}
            import worker_notes
            n = int(self.headers.get("Content-Length", 0))
            body = json.loads(self.rfile.read(n).decode("utf-8")) if n else {{}}
            w = body.get("worker", "")
            try:
                line = worker_notes.add(w, body.get("note", ""), body.get("folder", ""), body.get("n", ""), body.get("by", "CEE"))
            except ValueError as e:
                return self._json({{"error": str(e)}}, 400)
            with lock:
                if w in state["workers"]:
                    state["workers"][w]["text"] = "โดนติ: " + str(body.get("note", ""))[:60]
            log(f"[CEE] ติ{{worker_notes.WORKERS[w]}}: {{body.get('note', '')}}")
            return self._json({{"ok": True, "line": line}})'''
    fp = os.path.join(root, "factory.py")
    print("factory.py GET :", patch(fp, '        if self.path.startswith("/api/rules"):', get_block, "get", where="before"))
    print("factory.py POST:", patch(fp, '    def do_POST(self):', post_block, "post"))

    # 2) brain.py: คนเขียนบทอ่านสมุด script + flow ต่อท้ายกฎจากห้องสมุด
    bp = os.path.join(root, "brain.py")
    rules_block = f'''
def _rules_with_notes():   {MARK}
    try:
        import worker_notes
        extra = worker_notes.text("script", "flow")
    except Exception:
        extra = ""
    base = _rules_plain()
    return base + ("\\nMistakes the boss (CEE) blamed on the script writer / picture orders - never repeat them:\\n" + extra if extra else "")

'''
    src = io.open(bp, encoding="utf-8").read()
    if MARK not in src:
        shutil.copy2(bp, bp + ".before-cee") if not os.path.exists(bp + ".before-cee") else None
        src = src.replace("\ndef rules():", "\ndef _rules_plain():", 1)
        src = src.replace("\ndef avoid():", rules_block + "rules = _rules_with_notes\n\n\ndef avoid():", 1)
        io.open(bp, "w", encoding="utf-8").write(src)
        print("brain.py       : แก้แล้ว")
    else:
        print("brain.py       : มีอยู่แล้ว")

    # 3) qa_check.py: คนตรวจอ่านสมุด qa ก่อนดูภาพทุกครั้ง
    qa_block = f'''
    try:   {MARK}
        import worker_notes as _wn
        _qa = _wn.text("qa", last=8)
        if _qa:
            prompt = "Problems you MISSED before (the boss caught them) - look extra carefully for these:\\n" + _qa + "\\n\\n" + prompt
    except Exception:
        pass'''
    print("qa_check.py    :", patch(os.path.join(root, "qa_check.py"),
                                    'def vision(prompt, images, num_predict=260, prefer=None):\n    """ถามโมเดลดูภาพ: Gemini ก่อน (ตาดี ไม่กินการ์ดจอ) ถ้าไม่ได้ใช้ Ollama"""',
                                    qa_block, "qa"))
    print("\nเสร็จ - ปิดโรงงานแล้วเปิดใหม่ (start.bat) ให้ส่วนเสริมทำงาน")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else ".")
