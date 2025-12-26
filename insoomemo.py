import jaydebeapi
import os
import requests
import ast

from datetime import date
from dotenv import load_dotenv

# Load variables from .env file
load_dotenv()

# Paths
ACCDB_PATH = os.getenv("ACCDB_PATH")
UCANACCESS_LIB = os.getenv("UCANACCESS_LIB")
if os.getenv("ENV") == "TEST":
    print(f"ACCDB_PATH is {ACCDB_PATH}")
    print(f"UCANACCESS_LIB is {UCANACCESS_LIB}")

# Build classpath from all jars in UCANACCESS_LIB
classpath_jars = [os.path.join(UCANACCESS_LIB, j) for j in os.listdir(UCANACCESS_LIB) if j.endswith(".jar")]
CLASSPATH = ":".join(classpath_jars)

# JDBC details
JDBC_DRIVER = os.getenv("JDBC_DRIVER")
JDBC_URL = f"jdbc:ucanaccess://{ACCDB_PATH}"

# global registry at module level
function_registry = {}

def get_conn():
    return jaydebeapi.connect(JDBC_DRIVER, JDBC_URL, [], CLASSPATH)

def read_records(search_text):
    conn = get_conn()
    try:
        curs = conn.cursor()
        try:
            float(search_text)
            is_num = True
        except ValueError:
            is_num = False

        if is_num:
            query = "SELECT ID, mySubj, myMemo, dependsOn FROM tblMemo WHERE ID = ?"
            params = [search_text]
        else:
            query = "SELECT ID, mySubj, myMemo, dependsOn FROM tblMemo WHERE mySubj LIKE ?"
            params = [f"%{search_text}%"]

        curs.execute(query, params)
        rows = curs.fetchall()
        results = []
        for row in rows:
            results.append({
                "ID": row[0],
                "mySubj": row[1],
                "myMemo": row[2],
                "dependsOn": row[3] if len(row) > 3 else ""
            })
        return results
    finally:
        conn.close()

def update_record(record_id, subj, memo):
    conn = get_conn()
    try:
        curs = conn.cursor()
        today_str = date.today().strftime("%Y-%m-%d")
        query = "UPDATE tblMemo SET mySubj = ?, myMemo = ?, Updated = ? WHERE ID = ?"
        params = [subj, memo, today_str, record_id]
        curs.execute(query, params)
        conn.commit()
        return curs.rowcount
    finally:
        conn.close()

def add_record(subj, memo, dependsOn=""):
    conn = get_conn()
    try:
        curs = conn.cursor()
        query = "INSERT INTO tblMemo (mySubj, myMemo, dependsOn) VALUES (?, ?, ?)"
        params = [subj, memo, dependsOn]
        curs.execute(query, params)
        conn.commit()
        return curs.rowcount
    finally:
        conn.close()

def clear_fields():
    return {"ID": "", "mySubj": "", "myMemo": "", "search": ""}

# 🔑 New helper: load function with dependency resolution
def load_function_unsafe(rec):
    subj = rec["mySubj"].strip()
    body = rec["myMemo"]
    deps = rec.get("dependsOn", "").split(",") if rec.get("dependsOn") else []

    # Load dependencies first
    for dep in deps:
        dep = dep.strip()
        if dep and dep not in function_registry:
            dep_records = read_records(dep)
            if dep_records:
                load_function(dep_records[0])

    # Load the function itself
    exec(body, globals())
    function_registry[subj] = eval(subj)
    print(f"Function '{subj}' registered successfully.")

#---------- SAFETY Measure (Ctrlable) ---------------------------
def allow_builtin(name, func):
    """Add a new builtin to the whitelist."""
    SAFE_BUILTINS[name] = func
    print(f"Allowed builtin: {name}")

def disallow_builtin(name):
    """Remove a builtin from the whitelist."""
    if name in SAFE_BUILTINS:
        SAFE_BUILTINS.pop(name)
        print(f"Disallowed builtin: {name}")
    else:
        print(f"{name} not in whitelist.")
        
#---------- SAFETY Measure (Too strict) ---------------------------
# Define which built-ins are allowed
SAFE_BUILTINS = {
    "print": print,
    "len": len,
    "range": range,
    "str": str,
    "int": int,
    "float": float,
    "dict": dict,
    "list": list,
    "set": set,
    "tuple": tuple,
}

def is_safe_code(code):
    try:
        tree = ast.parse(code)
    except SyntaxError as e:
        print(f"Syntax error: {e}")
        return False

    for node in ast.walk(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom, ast.Global, ast.Nonlocal,
                             ast.With, ast.AsyncWith, ast.Try, ast.Raise,
                             ast.Delete)):
            print(f"Unsafe node detected: {type(node).__name__}")
            return False
    return True


def load_function(rec):
    subj = rec["mySubj"].strip()
    body = rec["myMemo"]
    deps = rec.get("dependsOn", "").split(",") if rec.get("dependsOn") else []

    # Load dependencies first
    for dep in deps:
        dep = dep.strip()
        if dep and dep not in function_registry:
            dep_records = read_records(dep)
            if dep_records:
                load_function(dep_records[0])

    # Validate code before execution
    if not is_safe_code(body):
        print(f"Rejected unsafe code for function '{subj}'.")
        return

    # Restricted environment
    safe_globals = {"__builtins__": SAFE_BUILTINS}
    try:
        exec(body, safe_globals)
        func = safe_globals.get(subj)
        if callable(func):
            function_registry[subj] = func
            print(f"Function '{subj}' registered safely.")
        else:
            print(f"Function '{subj}' not found after exec.")
    except Exception as e:
        print(f"Error executing function '{subj}': {e}")

class SafePath:
    join = staticmethod(os.path.join)
    getsize = staticmethod(os.path.getsize)
    isfile = staticmethod(os.path.isfile)

class SafeOS:
    listdir = staticmethod(os.listdir)
    path = SafePath

# ----------------------------------------------------------------
def main():
    print("Welcome to Insoo's Memo DB Program!")
    print("Available commands: add(a), read(r), quit(q)")

    #-- White list mgmt --
    """
    allow_builtin("listdir", os.listdir)
    allow_builtin("path_join", os.path.join)
    allow_builtin("getsize", os.path.getsize)
    allow_builtin("isfile", os.path.isfile)
    """
    allow_builtin("os", SafeOS)


    while True:
        command = input("\nEnter command: ").strip().lower()

        if command in ("a", "add"):
            subject = input("subject: ").strip()
            print("Enter memo text (multi-line). Type END on its own line to finish:")
            lines = []
            while True:
                line = input()
                if line == "END":
                    break
                lines.append(line)
            body = "\n".join(lines)
            depends = input("Dependencies (comma-separated, leave blank if none): ").strip()
            add_record(subject, body, depends)
            print("New memo added successfully!")

        elif command in ("r", "read"):
            target = input("ID or subject: ").strip()
            records = read_records(target)
            if records:
                total = len(records)
                for i, rec in enumerate(records, start=1):
                    action = ""
                    # Do the current def until press "x"
                    while action != "x": 
                        print(f"{i}. ID: {rec['ID']}")
                        print(f"   Subject: {rec['mySubj']}")
                        clean_memo = rec['myMemo'].replace("\r", "").replace("\t", "")
                        print("   Memo:")
                        print("   " + clean_memo.strip().replace("\n", "\n   "))
                        print("-" * 40)

                        remain = total - i
                        action = input(f"Continue? ({remain}/{total} remain, Enter=next, s=stop, u=update, d=do ft def): ").strip().lower()
                        if remain > 0 and action == "s":
                            break
                        if action == "u":
                            newSubj = input("New subj: ").strip()
                            newBody = input("New body: ").strip()
                            if newSubj and newBody:
                                count = update_record(rec["ID"], newSubj, newBody)
                                print(f"{count} record(s) updated.")
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
            print("Exiting program. Goodbye!")
            break
        else:
            print("Unknown command. Try again.")

if __name__ == "__main__":
    main()