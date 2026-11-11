"""Comprehensive Unit & Integration Tests for K-Rank (50 Artists & Anti-Duplicate Architecture)"""

import unittest
import json
from fastapi.testclient import TestClient

from app import app
from database import init_db, get_db
from scoring import calculate_kscore, calculate_tier

class TestKRankPro(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        init_db()
        cls.client = TestClient(app)

    def test_01_scoring_algorithm(self):
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

    def test_02_50_artists_database_integrity(self):
        conn = get_db()
        with conn:
            cur = conn.cursor()
            rows = cur.execute("SELECT COUNT(*) FROM artists").fetchone()
            self.assertEqual(rows[0], 50, "Database should contain exactly 50 production artists")

    def test_03_api_artists_filtering_and_sorting(self):
        res = self.client.get("/api/artists?sort=music")
        self.assertEqual(res.status_code, 200)
        artists = res.json()
        self.assertEqual(len(artists), 50)
        self.assertGreaterEqual(artists[0]["stats"]["music_stream"], artists[-1]["stats"]["music_stream"])

        # Generation Filter Test
        res_gen = self.client.get("/api/artists?gen=5세대")
        self.assertEqual(res_gen.status_code, 200)
        gen5_artists = res_gen.json()
        self.assertTrue(all(a["generation"] == "5세대" for a in gen5_artists))

    def test_04_anti_duplicate_cheer_prevention(self):
        # 1st Cheer
        res1 = self.client.post("/api/artists/1/cheer")
        self.assertEqual(res1.status_code, 200)
        self.assertIn("krank_vid", res1.cookies)

        # 2nd Duplicate Cheer attempt (same client/cookie)
        res2 = self.client.post("/api/artists/1/cheer", cookies=res1.cookies)
        self.assertEqual(res2.status_code, 409)

    def test_05_methodology_page_serving(self):
        res = self.client.get("/methodology")
        self.assertEqual(res.status_code, 200)
        self.assertIn("K-Score 6대 가중 산출 수식", res.text)

    def test_06_feedback_submission(self):
        res = self.client.post("/api/feedback", json={
            "category": "기능제안",
            "content": "K-Rank 서비스 최고입니다! 50팀 라인업 훌륭해요.",
            "email": "test@example.com"
        })
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()["status"], "success")

if __name__ == "__main__":
    unittest.main()
