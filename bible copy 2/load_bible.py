import csv
import sqlite3

def load_bible_csv(path="kjv.csv"):
    verses = []
    with open(path, newline='', encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            verses.append({
                "book": row["book"],
                "chapter": int(row["chapter"]),
                "verse": int(row["verse"]),
                "text": row["text"]
            })
    return verses

def load_bible_sqlite(path="kjv.sqlite"):
    conn = sqlite3.connect(path)
    cursor = conn.cursor()
    cursor.execute("SELECT book, chapter, verse, text FROM verses")
    verses = [
        {"book": book, "chapter": chapter, "verse": verse, "text": text}
        for book, chapter, verse, text in cursor.fetchall()
    ]
    conn.close()
    return verses

import re

def search_bible(verses, query, book=None, chapter=None):
    pattern = re.compile(re.escape(query), re.IGNORECASE)
    results = []
    for v in verses:
        if book and v["book"].lower() != book.lower():
            continue
        if chapter and v["chapter"] != chapter:
            continue
        if pattern.search(v["text"]):
            results.append(v)
    return results
