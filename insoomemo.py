import jaydebeapi
import os
from datetime import date

# Paths
ACCDB_PATH = "/home/insoo/Documents/share/insooMemo.accdb"  # update to your actual path
UCANACCESS_LIB = "/home/insoo/ucanaccess/lib"                   # folder with all required JARs

# Build classpath from all jars in UCANACCESS_LIB
classpath_jars = [os.path.join(UCANACCESS_LIB, j) for j in os.listdir(UCANACCESS_LIB) if j.endswith(".jar")]
CLASSPATH = ":".join(classpath_jars)


# JDBC details
JDBC_DRIVER = "net.ucanaccess.jdbc.UcanaccessDriver"
# If your Access DB is encrypted with a password:
#JDBC_URL = f"jdbc:ucanaccess://{ACCDB_PATH};jackcessOpener=com.healthmarketscience.jackcess.encryption.AESOpener"

# If your DB is NOT encrypted:
JDBC_URL = f"jdbc:ucanaccess://{ACCDB_PATH}"

def get_conn():
    return jaydebeapi.connect(JDBC_DRIVER, JDBC_URL, [], CLASSPATH)

def read_record(search_text):
    """
    If search_text is numeric: SELECT by ID
    Else: SELECT by subject LIKE '%text%'
    Returns (ID, mySubj, myMemo) or None
    """
    conn = get_conn()
    try:
        curs = conn.cursor()
        # Determine numeric vs string
        try:
            float(search_text)
            is_num = True
        except ValueError:
            is_num = False

        if is_num:
            query = "SELECT ID, mySubj, myMemo FROM tblMemo WHERE ID = ?"
            params = [search_text]
        else:
            query = "SELECT ID, mySubj, myMemo FROM tblMemo WHERE mySubj LIKE ?"
            params = [f"%{search_text}%"]

        curs.execute(query, params)
        row = curs.fetchone()
        if row:
            return {"ID": row[0], "mySubj": row[1], "myMemo": row[2]}
        return None
    finally:
        conn.close()

def update_record(record_id, subj, memo):
    """
    UPDATE tblMemo SET mySubj=?, myMemo=?, Updated=? WHERE ID=?
    Returns affected row count
    """
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

def add_record(subj, memo):
    """
    INSERT INTO tblMemo (mySubj, myMemo) VALUES (?, ?)
    Returns affected row count
    """
    conn = get_conn()
    try:
        curs = conn.cursor()
        query = "INSERT INTO tblMemo (mySubj, myMemo) VALUES (?, ?)"
        params = [subj, memo]
        curs.execute(query, params)
        conn.commit()
        return curs.rowcount
    finally:
        conn.close()
def clear_fields():
    """
    Mirrors btnClear_Click: simply returns blank defaults for UI use.
    """
    return {"ID": "", "mySubj": "", "myMemo": "", "search": ""}

def main():
    notes = []  # store notes as dictionaries

    print("Welcome to Insoo's Memo DB Program!")
    print("Available commands: add(a), read(r), quit(q)")

    while True:
        command = input("\nEnter command: ").strip().lower()

        if command in ("a", "add"):
            subject = input("subject: ").strip()
            body = input("body: ").strip()
            add_record(subject, body)
            print("New memo added successfully!")
        elif command in ("r", "read"):
            target = input("ID or subject: ").strip()
            record = read_record(target)
            if record:
                print("\nRead by ID or subject:")
                print(f"ID: {record['ID']}")
                print(f"Subject: {record['mySubj']}")
                print("Memo:")
                # Clean up carriage returns and tabs
                clean_memo = record['myMemo'].replace("\r", "").replace("\t", "")
                print(clean_memo.strip())
            else:
                print("No record found.")        
        elif command in ("q", "quit"):
                    print("Exiting program. Goodbye!")
                    break
        else:
            print("Unknown command. Try again.")

if __name__ == "__main__":
    main()
