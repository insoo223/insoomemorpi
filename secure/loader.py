import ast
from core.db import read_records

SAFE_BUILTINS = {
    "print": print, "len": len, "range": range,
    "str": str, "int": int, "float": float,
    "dict": dict, "list": list, "set": set, "tuple": tuple,
}

function_registry = {}

def is_safe_code(code):
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return False
    for node in ast.walk(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom, ast.Global, ast.Nonlocal,
                             ast.With, ast.AsyncWith, ast.Try, ast.Raise, ast.Delete)):
            return False
    return True

def load_function(rec):
    subj = rec["mySubj"].strip()
    body = rec["myMemo"]
    deps = rec.get("dependsOn", "").split(",") if rec.get("dependsOn") else []

    for dep in deps:
        dep = dep.strip()
        if dep and dep not in function_registry:
            dep_records = read_records(dep)
            if dep_records:
                load_function(dep_records[0])

    if not is_safe_code(body):
        print(f"Rejected unsafe code for function '{subj}'.")
        return

    safe_globals = {"__builtins__": SAFE_BUILTINS}
    exec(body, safe_globals)
    func = safe_globals.get(subj)
    if callable(func):
        function_registry[subj] = func
        print(f"[SECURE] Function '{subj}' registered safely.")