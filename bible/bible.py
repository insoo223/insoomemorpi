import csv
import sqlite3
import re

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

def bibleTest():
    bible = load_bible_csv("/home/insoo/github/bible_databases/formats/csv/KJV.csv")   # or load_bible_sqlite("kjv.sqlite")
    query = input("Enter keyword: ")
    results = search_bible(bible, query)
    for v in results[:10]:  # show first 10 matches
        print(f'{v["book"]} {v["chapter"]}:{v["verse"]} — {v["text"]}')
