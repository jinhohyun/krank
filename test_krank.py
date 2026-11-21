"""Comprehensive Unit & Integration Tests for K-Rank (50 Artists & Global i18n)"""

import unittest
import json
from fastapi.testclient import TestClient

from app import app
from database import init_db, get_db
from scoring import calculate_kscore, calculate_tier

class TestKRankGlobal(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        init_db()
        cls.client = TestClient(app)

    def setUp(self):
        # Clear cheer logs for predictable anti-duplicate tests
        conn = get_db()
        with conn:
            conn.execute("DELETE FROM cheer_logs")
            conn.execute("DELETE FROM post_logs")
            conn.execute("DELETE FROM fan_discussions")
        conn.close()

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
        self.assertIn("K-Score 6-Axis Formula & Methodology", res.text)

    def test_06_feedback_submission(self):
        res = self.client.post("/api/feedback", json={
            "category": "기능제안",
            "content": "K-Rank global i18n support is awesome!",
            "email": "global@example.com"
        })
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()["status"], "success")

    def test_07_discussion_rate_limit(self):
        """공개 토론 도배 방지: 10분 5건까지, 6번째는 429."""
        for i in range(5):
            res = self.client.post("/api/artists/1/discussions", json={
                "author": "팬", "content": f"응원합니다 {i}"
            })
            self.assertEqual(res.status_code, 200, res.text)
        res = self.client.post("/api/artists/1/discussions", json={
            "author": "팬", "content": "여섯번째"
        })
        self.assertEqual(res.status_code, 429)
        self.assertIn("Retry-After", res.headers)

    def test_08_discussion_validation_and_tag_strip(self):
        """200자 상한·태그 제거: 저장 전에 서버가 정규화한다."""
        too_long = self.client.post("/api/artists/2/discussions", json={"content": "x" * 201})
        self.assertEqual(too_long.status_code, 400)

        res = self.client.post("/api/artists/2/discussions", json={
            "author": "<b>팬</b>", "content": "<script>alert(1)</script>안녕"
        })
        self.assertEqual(res.status_code, 200, res.text)
        conn = get_db()
        row = conn.execute(
            "SELECT author, content FROM fan_discussions WHERE artist_id = 2 ORDER BY id DESC LIMIT 1"
        ).fetchone()
        conn.close()
        self.assertNotIn("<", row["author"])
        self.assertNotIn("<", row["content"])
        self.assertEqual(row["content"], "alert(1)안녕")

    def test_09_discussion_unknown_artist_404(self):
        res = self.client.post("/api/artists/99999/discussions", json={"content": "응원"})
        self.assertEqual(res.status_code, 404)

if __name__ == "__main__":
    unittest.main()
