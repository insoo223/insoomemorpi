import os
from dotenv import load_dotenv
from core.db import add_record, read_records, update_record
from core.add_command import handle_add
from bible.bible import bibleTest

load_dotenv()
ENABLE_SECURITY = os.getenv("ENABLE_SECURITY", "true").lower() == "true"

if ENABLE_SECURITY:
    from secure.loader import load_function, function_registry
else:
    from plain.loader import load_function, function_registry

def main():
    print("Welcome to Insoo's Memo DB Program!")
    print("Available commands: add(a), read(r), quit(q)")
    while True:
        command = input("\nEnter command: ").strip().lower()
        if command in ("a", "add"):
            handle_add()
            """
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
            print("New memo added successfully!")
            """
            

        elif command in ("b", "bible"):
            # target = input("ID or subject: ").strip()
            bibleTest()
        elif command in ("rs", "readSimple"):
            target = input("ID or subject: ").strip()
            records = read_records(target)
            if records:
                for rec in records:
                    print(f"ID: {rec['ID']}, Subject: {rec['mySubj']}")
                    load_function(rec)
            else:
                print("No record found.")
        elif command in ("r", "read"):
            target = input("ID or subject: ").strip()
            records = read_records(target)
            if records:
                total = len(records)
                for i, rec in enumerate(records, start=1):
                    action = ""
                    # Do the current def until press "x"
                    sameDefIteration = 0
                    while action != "x": 
                        sameDefIteration += 1;
                        print(f"{i}. ID: {rec['ID']}")
                        print(f"   Subject: {rec['mySubj']}")
                        clean_memo = rec['myMemo'].replace("\r", "").replace("\t", "")
                        # Show the full def only the 1st time
                        if sameDefIteration == 1:
                            print("   Memo:")
                            print("   " + clean_memo.strip().replace("\n", "\n   "))
                            print("-" * 40)

                        remain = total - i
                        action = input(f"Continue? ({remain}/{total} remain, Enter=next, s=stop, u=update, d=do ft def): ").strip().lower()
                        if remain > 0 and action == "s":
                            break
                        if action == "u":
                            """
                            newSubj = input("New subj: ").strip()
                            newBody = input("New body: ").strip()
                            if newSubj and newBody:
                                count = update_record(rec["ID"], newSubj, newBody)
                                print(f"{count} record(s) updated.")
                            """
                            subject = input("updated subject: ").strip()
                            print("Enter updated memo text (multi-line). Type END on its own line to finish:")
                            lines = []
                            while True:
                                line = input()
                                if line == "END":
                                    break
                                lines.append(line)
                            body = "\n".join(lines)
                            # depends = input("Dependencies (comma-separated): ").strip()
                            # count = update_record(rec["ID"], subject, body)
                            update_record(rec["ID"], subject, body)
                            # add_record(subject, body, depends)
                            print("Updated memo successfully!")

                        if action == "d":
                            try:
                                load_function(rec)
                                params = input("Enter parameters separated by commas: ")
                                args = [p.strip() for p in params.split(",") if p.strip()]
                                result = function_registry[rec["mySubj"]](*args)
                                print(f"Demo {rec['mySubj']}: {result}")
                            except Exception as e:
                                print(f"Error loading function: {e}")
                        if action == "l":
                            try:
                                params = input("Enter builtin names (comma-separated): ").strip().split(",")
                                for name in [p.strip() for p in params if p.strip()]:
                                    if name in dir(__builtins__):
                                        allow_builtin(name, getattr(__builtins__, name))
                                        print(f"Whitelisted {name}")
                                    else:
                                        print(f"{name} is not a recognized builtin.")
                            except Exception as e:
                                print(f"Error allow function: {e}")                                
            else:
                print("No record found.")
        elif command in ("q", "quit"):
            break

if __name__ == "__main__":
    main()