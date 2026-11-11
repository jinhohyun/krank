"""Comprehensive Unit & Integration Tests for K-Rank MVP"""

import unittest
import json
import sqlite3
from pathlib import Path

from database import init_db, get_db
from scoring import calculate_kscore, calculate_tier

class TestKRank(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        init_db()

    def test_scoring_algorithm(self):
        stats = {
            "music_stream": 100.0,
            "album_sales": 100.0,
            "youtube_views": 100.0,
            "sns_growth": 100.0,
            "google_buzz": 100.0,
            "fandom_power": 100.0
        }
        score = calculate_kscore(stats)
        self.assertEqual(score, 100.0)
        self.assertEqual(calculate_tier(score), "S+")

    def test_database_integrity(self):
        conn = get_db()
        with conn:
            cur = conn.cursor()
            rows = cur.execute("SELECT COUNT(*) FROM artists").fetchone()
            self.assertGreater(rows[0], 0, "Database should contain seeded artists")

    def test_cheer_functionality(self):
        conn = get_db()
        with conn:
            cur = conn.cursor()
            artist = cur.execute("SELECT id, cheer_count FROM artists LIMIT 1").fetchone()
            artist_id, initial_count = artist["id"], artist["cheer_count"]

            cur.execute("UPDATE artists SET cheer_count = cheer_count + 1 WHERE id = ?", (artist_id,))
            updated_count = cur.execute("SELECT cheer_count FROM artists WHERE id = ?", (artist_id,)).fetchone()[0]

            self.assertEqual(updated_count, initial_count + 1)


if __name__ == "__main__":
    unittest.main()
