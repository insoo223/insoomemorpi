import csv
import sqlite3
import re

def load_bible_sqlite(path="kjv.sqlite", translation="kjv"):
    """
    Load Bible data from Scrollmapper SQLite schema.
    Joins <translation>_verses with <translation>_books.
    """
    conn = sqlite3.connect(path)
    cursor = conn.cursor()

    query = f"""
    SELECT b.name, v.chapter, v.verse, v.text
    FROM {translation}_verses v
    JOIN {translation}_books b ON v.book_id = b.id
    ORDER BY b.id, v.chapter, v.verse
    """
    cursor.execute(query)
    verses = [
        {"book": book, "chapter": chapter, "verse": verse, "text": text}
        for book, chapter, verse, text in cursor.fetchall()
    ]
    conn.close()
    return verses

def search_bible(verses, query, book=None, chapter=None, whole_word=False):
    if whole_word:
        pattern = re.compile(rf"\b{re.escape(query)}\b", re.IGNORECASE)
    else:
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

def load_bible_csv(path="KJV.csv"):
    """
    Load Bible data from Scrollmapper flat CSV (formats/csv/*.csv).
    Expected columns: Book, Chapter, Verse, Text
    """
    verses = []
    with open(path, newline='', encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            verses.append({
                "book": row["Book"],          # capitalized
                "chapter": int(row["Chapter"]),
                "verse": int(row["Verse"]),
                "text": row["Text"]
            })
    return verses

def bibleTest():
    bibleDBPath="/home/insoo/github/bible_databases/"
    csvPath="formats/csv/"
    #ver="KJV.csv"
    ver="KorRV.csv"
    bible = load_bible_csv(bibleDBPath + csvPath + ver)
    query = input("Enter keyword: ")
    results = search_bible(bible, query)
    i=0
    for v in results[:1000]:
        i += 1
        print(f'{i: }{v["book"]} {v["chapter"]}:{v["verse"]} — {v["text"]}')
