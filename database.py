"""SQLite Database ORM & Initialization for K-Rank (krank.db) with Bilingual Support"""

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
        # Recreate table if bilingual columns missing
        cur = conn.cursor()
        table_info = cur.execute("PRAGMA table_info(artists)").fetchall()
        column_names = [col[1] for col in table_info]
        if table_info and ("agency_en" not in column_names or "signature_quote_en" not in column_names):
            conn.executescript("DROP TABLE IF EXISTS artists; DROP TABLE IF EXISTS cheer_logs; DROP TABLE IF EXISTS fan_discussions;")

        conn.executescript("""
        CREATE TABLE IF NOT EXISTS artists (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            name_en TEXT NOT NULL,
            agency TEXT,
            agency_en TEXT,
            debut_year INTEGER,
            photo_url TEXT,
            avatar_url TEXT,
            kscore REAL DEFAULT 0.0,
            tier TEXT DEFAULT 'C',
            cheer_count INTEGER DEFAULT 0,
            fandom_name TEXT,
            fandom_name_en TEXT,
            signature_quote TEXT,
            signature_quote_en TEXT,
            tags_json TEXT,
            tags_en_json TEXT,
            stats_json TEXT,
            is_verified INTEGER DEFAULT 1,
            generation TEXT DEFAULT '4세대',
            generation_en TEXT DEFAULT '4th Gen',
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

        # Force full re-seed to ensure signature_quote_en is loaded
        cur = conn.cursor()
        if SEED_PATH.exists():
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
                    (id, name, name_en, agency, agency_en, debut_year, photo_url, avatar_url, kscore, tier, cheer_count, fandom_name, fandom_name_en, signature_quote, signature_quote_en, tags_json, tags_en_json, stats_json, is_verified, generation, generation_en)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    item.get("id"),
                    item.get("name"),
                    item.get("name_en"),
                    item.get("agency"),
                    item.get("agency_en", item.get("agency")),
                    item.get("debut_year"),
                    item.get("photo_url"),
                    item.get("avatar_url"),
                    kscore,
                    tier,
                    item.get("cheer_count", 0),
                    item.get("fandom_name"),
                    item.get("fandom_name_en", item.get("fandom_name")),
                    item.get("signature_quote"),
                    item.get("signature_quote_en", item.get("signature_quote")),
                    json.dumps(item.get("tags", []), ensure_ascii=False),
                    json.dumps(item.get("tags_en", []), ensure_ascii=False),
                    json.dumps(stats, ensure_ascii=False),
                    1 if item.get("is_verified", True) else 0,
                    item.get("generation", "4세대"),
                    item.get("generation_en", "4th Gen")
                ))
            print("✓ [K-Rank] 50 production artists re-seeded with bilingual data into krank.db!")


if __name__ == "__main__":
    init_db()
