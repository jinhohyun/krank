"""FastAPI Web Server & REST API Router for K-Rank (Global K-Pop Ranking)"""

import hashlib
import json
import os
import uuid
from typing import Optional
from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from pathlib import Path

import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
WORKSPACE_ROOT = BASE_DIR.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

try:
    import krank_mvp.database as krank_db
except ImportError:
    import database as krank_db

get_db = krank_db.get_db
init_db = krank_db.init_db
from krank_core_config import KRANK_CONFIG, KrankScoringEngine
from rank_core import create_ranking_app, BaseDatabaseManager

# Rank Core 서브 앱 마운트
core_engine = KrankScoringEngine(KRANK_CONFIG.weights)
core_db_path = str(BASE_DIR / KRANK_CONFIG.db_filename)
core_db = BaseDatabaseManager(core_db_path)
core_app = create_ranking_app(KRANK_CONFIG, core_db, core_engine)

STATIC_DIR = BASE_DIR / "static"
VID_COOKIE_NAME = "krank_vid"

app = FastAPI(title="K-Rank API", version="2.0.0")
app.mount("/core", core_app)

# Mount Static Files
STATIC_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


@app.on_event("startup")
def startup():
    init_db()


def _get_client_ip(request: Request) -> str:
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "127.0.0.1"


def _generate_ip_hash(request: Request) -> str:
    ip = _get_client_ip(request)
    ua = request.headers.get("User-Agent", "")
    return hashlib.sha256(f"{ip}:{ua}:krank_salt".encode("utf-8")).hexdigest()


@app.get("/", response_class=HTMLResponse)
def read_root():
    index_path = STATIC_DIR / "index.html"
    if index_path.exists():
        return index_path.read_text(encoding="utf-8")
    return "<h1>K-Rank API Running</h1>"


@app.get("/methodology", response_class=HTMLResponse)
def read_methodology():
    methodology_path = STATIC_DIR / "methodology.html"
    if methodology_path.exists():
        return methodology_path.read_text(encoding="utf-8")
    return "<h1>Methodology Page</h1>"


@app.get("/api/artists")
def get_artists(
    query: Optional[str] = None,
    sort: Optional[str] = "kscore",
    gen: Optional[str] = None
):
    """Retrieve artists with filtering and sorting options."""
    conn = get_db()
    with conn:
        cur = conn.cursor()
        sql = "SELECT * FROM artists WHERE 1=1"
        params = []

        if query:
            sql += " AND (name LIKE ? OR name_en LIKE ? OR agency LIKE ? OR agency_en LIKE ? OR fandom_name LIKE ? OR fandom_name_en LIKE ?)"
            q = f"%{query}%"
            params.extend([q, q, q, q, q, q])

        if gen:
            sql += " AND (generation = ? OR generation_en = ?)"
            params.extend([gen, gen])

        # Dynamic Sorting
        if sort == "music":
            sql += " ORDER BY json_extract(stats_json, '$.music_stream') DESC"
        elif sort == "album":
            sql += " ORDER BY json_extract(stats_json, '$.album_sales') DESC"
        elif sort == "youtube":
            sql += " ORDER BY json_extract(stats_json, '$.youtube_views') DESC"
        elif sort == "sns":
            sql += " ORDER BY json_extract(stats_json, '$.sns_growth') DESC"
        elif sort == "cheer":
            sql += " ORDER BY cheer_count DESC"
        else:
            sql += " ORDER BY kscore DESC"

        rows = cur.execute(sql, params).fetchall()

    results = []
    for r in rows:
        d = dict(r)
        d["tags"] = json.loads(d["tags_json"]) if d.get("tags_json") else []
        d["tags_en"] = json.loads(d["tags_en_json"]) if d.get("tags_en_json") else []
        d["stats"] = json.loads(d["stats_json"]) if d.get("stats_json") else {}
        results.append(d)

    return results


@app.get("/api/artists/{artist_id}")
def get_artist_detail(artist_id: int):
    """Retrieve detailed info for a single artist."""
    conn = get_db()
    with conn:
        row = conn.execute("SELECT * FROM artists WHERE id = ?", (artist_id,)).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Artist not found")

        d = dict(row)
        d["tags"] = json.loads(d["tags_json"]) if d.get("tags_json") else []
        d["tags_en"] = json.loads(d["tags_en_json"]) if d.get("tags_en_json") else []
        d["stats"] = json.loads(d["stats_json"]) if d.get("stats_json") else {}

    return d


@app.get("/api/my-cheers")
def get_my_cheers(request: Request):
    """Return list of artist IDs cheered by this user (IP/Cookie hash)."""
    vid = request.cookies.get(VID_COOKIE_NAME)
    ip_hash = _generate_ip_hash(request)

    conn = get_db()
    with conn:
        cur = conn.cursor()
        rows = cur.execute(
            "SELECT DISTINCT artist_id FROM cheer_logs WHERE ip_hash = ? OR (vid IS NOT NULL AND vid = ?)",
            (ip_hash, vid or "")
        ).fetchall()

    return [r[0] for r in rows]


@app.post("/api/artists/{artist_id}/cheer")
def cheer_artist(artist_id: int, request: Request, response: Response):
    """3-Layer Anti-Duplicate Cheer Increment (IP+UA Hash + HttpOnly Cookie + DB transaction)."""
    vid = request.cookies.get(VID_COOKIE_NAME)
    if not vid:
        vid = str(uuid.uuid4())
        response.set_cookie(key=VID_COOKIE_NAME, value=vid, max_age=31536000, httponly=True, samesite="lax")

    ip_hash = _generate_ip_hash(request)

    conn = get_db()
    with conn:
        cur = conn.cursor()
        conn.execute("BEGIN IMMEDIATE")

        # Check existing cheer
        existing = cur.execute(
            "SELECT id FROM cheer_logs WHERE artist_id = ? AND (ip_hash = ? OR (vid IS NOT NULL AND vid = ?))",
            (artist_id, ip_hash, vid)
        ).fetchone()

        if existing:
            raise HTTPException(status_code=409, detail="Already cheered for this artist today.")

        row = cur.execute("SELECT id, cheer_count FROM artists WHERE id = ?", (artist_id,)).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Artist not found")

        new_count = row["cheer_count"] + 1
        cur.execute("UPDATE artists SET cheer_count = ? WHERE id = ?", (new_count, artist_id))
        cur.execute("INSERT INTO cheer_logs (artist_id, ip_hash, vid) VALUES (?, ?, ?)", (artist_id, ip_hash, vid))

    return {"status": "success", "artist_id": artist_id, "cheer_count": new_count}


@app.get("/api/artists/{artist_id}/discussions")
def get_discussions(artist_id: int):
    """Retrieve fan discussion messages for an artist."""
    conn = get_db()
    with conn:
        rows = conn.execute(
            "SELECT * FROM fan_discussions WHERE artist_id = ? ORDER BY id DESC LIMIT 30",
            (artist_id,)
        ).fetchall()

    return [dict(r) for r in rows]


@app.post("/api/artists/{artist_id}/discussions")
def create_discussion(artist_id: int, data: dict):
    """Post a new fan discussion comment."""
    stance = data.get("stance", "💖 응원")
    author = data.get("author", "익명팬덤")
    content = data.get("content", "").strip()
    is_official = 1 if data.get("is_official") else 0

    if not content:
        raise HTTPException(status_code=400, detail="Content cannot be empty")

    conn = get_db()
    with conn:
        conn.execute(
            "INSERT INTO fan_discussions (artist_id, stance, author, content, is_official) VALUES (?, ?, ?, ?, ?)",
            (artist_id, stance, author, content, is_official)
        )

    return {"status": "success"}


@app.post("/api/feedback")
def submit_feedback(data: dict):
    """Submit user feedback or donation inquiry."""
    category = data.get("category", "의견")
    content = data.get("content", "").strip()
    email = data.get("email", "").strip()

    if not content:
        raise HTTPException(status_code=400, detail="Feedback content required")

    conn = get_db()
    with conn:
        conn.execute(
            "INSERT INTO feedback (category, content, email) VALUES (?, ?, ?)",
            (category, content, email)
        )

    return {"status": "success", "message": "Feedback received. Thank you!"}
