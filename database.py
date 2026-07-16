import sqlite3
import pandas as pd
import json
import os

def initialize_database():
    conn = sqlite3.connect("swift.db")
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS controls(
    id INTEGER PRIMARY KEY,
    control_id TEXT,
    title TEXT,
    start_page INTEGER,
    end_page INTEGER,
    summary TEXT,
    keywords TEXT
    )
    """)
    conn.commit()
    conn.close()

def seed_database(csv_path="swift_controls.csv"):
    df = pd.read_csv(csv_path)
    conn = sqlite3.connect("swift.db")
    for _, row in df.iterrows():
        # Prevent duplicates
        if conn.execute("SELECT 1 FROM controls WHERE control_id = ?", (row.get("control_id", row.get("id")),)).fetchone():
            continue
        conn.execute("""
        INSERT INTO controls(control_id, title, start_page, end_page)
        VALUES(?,?,?,?)
        """, (
            row.get("control_id", row.get("id")),
            row.get("title", row.get("control")),
            row.get("start_page"),
            row.get("end_page")
        ))
    conn.commit()
    conn.close()

def update_database_with_extras(summaries_file="control_summaries.json", keywords_file="keywords.json"):
    conn = sqlite3.connect("swift.db")
    if os.path.exists(summaries_file):
        with open(summaries_file, "r", encoding="utf-8") as f:
            summaries = json.load(f)
        for c_id, summ in summaries.items():
            conn.execute("UPDATE controls SET summary = ? WHERE control_id = ?", (summ, c_id))
            
    if os.path.exists(keywords_file):
        with open(keywords_file, "r", encoding="utf-8") as f:
            keywords = json.load(f)
        for c_id, kw_list in keywords.items():
            conn.execute("UPDATE controls SET keywords = ? WHERE control_id = ?", (json.dumps(kw_list), c_id))
            
    conn.commit()
    conn.close()

if __name__ == "__main__":
    initialize_database()
    seed_database()
    update_database_with_extras()