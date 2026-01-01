# core/add_command.py
from core.db import add_record

def handle_add():
    subject = input("subject: ").strip()
    print("Enter memo text (multi-line). Type END on its own line to finish:")
    lines = []
    while True:
        line = input()
        if line == "END":
            break
        lines.append(line)
    body = "\n".join(lines)
    depends = input("Dependencies (comma-separated): ").strip()
    add_record(subject, body, depends)
    print("(handle_add) New memo added successfully!")