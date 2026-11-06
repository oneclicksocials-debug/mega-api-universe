#!/usr/bin/env python3
import sys
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "mega_apis.sqlite")

def search(query, limit=20):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    print(f"\nSearching {DB_PATH} for: '{query}'...\n")
    cur.execute("""
    SELECT apis.id, apis.name, apis.url, apis.description, apis.category, apis.auth, apis.source
    FROM apis_fts
    JOIN apis ON apis.id = apis_fts.rowid
    WHERE apis_fts MATCH ?
    LIMIT ?
    """, (f"{query}*", limit))
    rows = cur.fetchall()
    if not rows:
        # Fallback to LIKE
        cur.execute("""
        SELECT id, name, url, description, category, auth, source
        FROM apis
        WHERE name LIKE ? OR description LIKE ? OR category LIKE ?
        LIMIT ?
        """, (f"%{query}%", f"%{query}%", f"%{query}%", limit))
        rows = cur.fetchall()

    for idx, (aid, name, url, desc, cat, auth, src) in enumerate(rows, 1):
        print(f"[{idx}] {name} ({cat})")
        print(f"    URL:    {url}")
        print(f"    Auth:   {auth} | Source: {src}")
        print(f"    Desc:   {desc[:120]}...")
        print("-" * 70)
    print(f"\nFound {len(rows)} matching APIs.\n")
    conn.close()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 search.py <keyword> [limit]")
        sys.exit(1)
    q = sys.argv[1]
    lim = int(sys.argv[2]) if len(sys.argv) > 2 else 20
    search(q, lim)
