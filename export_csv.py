#!/usr/bin/env python3
"""
Export any search query or category from mega_apis.sqlite to CSV.
Usage:
    python3 export_csv.py <query_or_category> [output_file.csv]
Examples:
    python3 export_csv.py freight freight_apis.csv
    python3 export_csv.py "Government" gov_apis.csv
    python3 export_csv.py ALL all_76k_apis.csv
"""

import sys
import sqlite3
import csv
import os

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "mega_apis.sqlite")

def export(query, out_csv):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    if query.upper() == "ALL":
        cur.execute("SELECT id, name, category, auth, cors, rating, source, url, description FROM apis")
    else:
        # Check category first, then FTS
        cur.execute("SELECT id, name, category, auth, cors, rating, source, url, description FROM apis WHERE category LIKE ?", (f"%{query}%",))
        rows = cur.fetchall()
        if not rows:
            cur.execute("""
            SELECT apis.id, apis.name, apis.category, apis.auth, apis.cors, apis.rating, apis.source, apis.url, apis.description
            FROM apis_fts
            JOIN apis ON apis.id = apis_fts.rowid
            WHERE apis_fts MATCH ?
            """, (f"{query}*",))
            rows = cur.fetchall()

    if query.upper() == "ALL":
        rows = cur.fetchall()

    with open(out_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["ID", "Name", "Category", "Auth", "CORS", "Rating", "Source", "URL", "Description"])
        writer.writerows(rows)
        
    print(f"Exported {len(rows):,} APIs matching '{query}' to: {out_csv}")
    conn.close()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 export_csv.py <query_or_category> [output_file.csv]")
        sys.exit(1)
        
    q = sys.argv[1]
    out = sys.argv[2] if len(sys.argv) > 2 else f"{q.replace(' ', '_').lower()}_export.csv"
    export(q, out)
