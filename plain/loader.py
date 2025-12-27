from core.db import read_records

function_registry = {}

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

    exec(body, globals())
    function_registry[subj] = eval(subj)
    print(f"[PLAIN] Function '{subj}' registered (unsafe).")