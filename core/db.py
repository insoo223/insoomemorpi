import jaydebeapi
import os
from datetime import date
from dotenv import load_dotenv

# Load variables from .env file
load_dotenv()

ACCDB_PATH = os.getenv("ACCDB_PATH")
UCANACCESS_LIB = os.getenv("UCANACCESS_LIB")
JDBC_DRIVER = os.getenv("JDBC_DRIVER")
classpath_jars = [os.path.join(UCANACCESS_LIB, j) for j in os.listdir(UCANACCESS_LIB) if j.endswith(".jar")]
CLASSPATH = ":".join(classpath_jars)
JDBC_URL = f"jdbc:ucanaccess://{ACCDB_PATH}"

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
        return [
            {"ID": row[0], "mySubj": row[1], "myMemo": row[2], "dependsOn": row[3] if len(row) > 3 else ""}
            for row in rows
        ]
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