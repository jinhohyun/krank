"""SQLite Database ORM & Initialization for K-Rank (krank.db)"""

import json
import os
import shutil
import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "krank.db"
SEED_PATH = BASE_DIR / "seed_data.json"


def get_db():
    target_db = DB_PATH
    if os.environ.get("VERCEL"):
        tmp_db = Path("/tmp/krank.db")
        if not tmp_db.exists() and DB_PATH.exists():
            try:
                shutil.copy2(DB_PATH, tmp_db)
            except Exception:
                pass
        if tmp_db.exists():
            target_db = tmp_db

    conn = sqlite3.connect(target_db)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    with conn:
        # Migrate or recreate table if schema updated
        cur = conn.cursor()
        table_info = cur.execute("PRAGMA table_info(artists)").fetchall()
        column_names = [col[1] for col in table_info]
        if table_info and "is_verified" not in column_names:
            conn.executescript("DROP TABLE IF EXISTS artists; DROP TABLE IF EXISTS cheer_logs; DROP TABLE IF EXISTS fan_discussions;")

        conn.executescript("""
        CREATE TABLE IF NOT EXISTS artists (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            name_en TEXT NOT NULL,
            agency TEXT,
            debut_year INTEGER,
            photo_url TEXT,
            avatar_url TEXT,
            kscore REAL DEFAULT 0.0,
            tier TEXT DEFAULT 'C',
            cheer_count INTEGER DEFAULT 0,
            fandom_name TEXT,
            signature_quote TEXT,
            tags_json TEXT,
            stats_json TEXT,
            is_verified INTEGER DEFAULT 1,
            generation TEXT DEFAULT '4세대',
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS cheer_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            artist_id INTEGER,
            ip_hash TEXT,
            vid TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (artist_id) REFERENCES artists (id)
        );

        CREATE TABLE IF NOT EXISTS fan_discussions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            artist_id INTEGER,
            stance TEXT,
            author TEXT,
            content TEXT,
            is_official INTEGER DEFAULT 0,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (artist_id) REFERENCES artists (id)
        );

        CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT,
            content TEXT,
            email TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );
        """)

        # Seed data if needed
        cur = conn.cursor()
        count = cur.execute("SELECT COUNT(*) FROM artists").fetchone()[0]
        if SEED_PATH.exists() and count < 50:
            cur.execute("DELETE FROM artists")
            with open(SEED_PATH, "r", encoding="utf-8") as f:
                seed_data = json.load(f)

            from scoring import calculate_kscore, calculate_tier

            for item in seed_data:
                stats = item.get("stats", {})
                kscore = calculate_kscore(stats)
                tier = calculate_tier(kscore)

                cur.execute("""
                    INSERT INTO artists 
                    (id, name, name_en, agency, debut_year, photo_url, avatar_url, kscore, tier, cheer_count, fandom_name, signature_quote, tags_json, stats_json, is_verified, generation)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    item.get("id"),
                    item.get("name"),
                    item.get("name_en"),
                    item.get("agency"),
                    item.get("debut_year"),
                    item.get("photo_url"),
                    item.get("avatar_url"),
                    kscore,
                    tier,
                    item.get("cheer_count", 0),
                    item.get("fandom_name"),
                    item.get("signature_quote"),
                    json.dumps(item.get("tags", []), ensure_ascii=False),
                    json.dumps(stats, ensure_ascii=False),
                    1 if item.get("is_verified", True) else 0,
                    item.get("generation", "4세대")
                ))
            print("✓ [K-Rank] 50 production artists re-seeded into krank.db!")


if __name__ == "__main__":
    init_db()
