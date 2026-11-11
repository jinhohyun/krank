"""FastAPI Web Server & REST API Router for K-Rank MVP"""

import json
from typing import Optional
from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from pathlib import Path

from database import get_db, init_db

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"

app = FastAPI(title="K-Rank API", version="1.0.0")

# Mount Static Files
STATIC_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


@app.on_event("startup")
def startup():
    init_db()


@app.get("/", response_class=HTMLResponse)
def read_root():
    index_path = STATIC_DIR / "index.html"
    if index_path.exists():
        return index_path.read_text(encoding="utf-8")
    return "<h1>K-Rank API Running</h1>"


@app.get("/api/artists")
def get_artists(query: Optional[str] = None):
    """Retrieve all artists sorted by K-Score descending."""
    conn = get_db()
    with conn:
        cur = conn.cursor()
        sql = "SELECT * FROM artists"
        params = []
        if query:
            sql += " WHERE name LIKE ? OR name_en LIKE ? OR agency LIKE ?"
            q = f"%{query}%"
            params = [q, q, q]
        sql += " ORDER BY kscore DESC"

        rows = cur.execute(sql, params).fetchall()

    results = []
    for r in rows:
        d = dict(r)
        d["tags"] = json.loads(d["tags_json"]) if d["tags_json"] else []
        d["stats"] = json.loads(d["stats_json"]) if d["stats_json"] else {}
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
        d["tags"] = json.loads(d["tags_json"]) if d["tags_json"] else []
        d["stats"] = json.loads(d["stats_json"]) if d["stats_json"] else {}

    return d


@app.post("/api/artists/{artist_id}/cheer")
def cheer_artist(artist_id: int, request: Request):
    """Increment cheer/heart count for an artist."""
    conn = get_db()
    with conn:
        row = conn.execute("SELECT id, cheer_count FROM artists WHERE id = ?", (artist_id,)).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Artist not found")

        new_count = row["cheer_count"] + 1
        conn.execute("UPDATE artists SET cheer_count = ? WHERE id = ?", (new_count, artist_id))
        conn.execute("INSERT INTO cheer_logs (artist_id, ip_hash) VALUES (?, ?)", (artist_id, "anon_client"))

    return {"status": "success", "artist_id": artist_id, "cheer_count": new_count}


@app.get("/api/artists/{artist_id}/discussions")
def get_discussions(artist_id: int):
    """Retrieve fan discussion messages for an artist."""
    conn = get_db()
    with conn:
        rows = conn.execute(
            "SELECT * FROM fan_discussions WHERE artist_id = ? ORDER BY id DESC LIMIT 20",
            (artist_id,)
        ).fetchall()

    return [dict(r) for r in rows]


@app.post("/api/artists/{artist_id}/discussions")
def create_discussion(artist_id: int, data: dict):
    """Post a new fan discussion comment."""
    stance = data.get("stance", "💖 응원")
    author = data.get("author", "익명버니즈")
    content = data.get("content", "").strip()

    if not content:
        raise HTTPException(status_code=400, detail="Content cannot be empty")

    conn = get_db()
    with conn:
        conn.execute(
            "INSERT INTO fan_discussions (artist_id, stance, author, content) VALUES (?, ?, ?, ?)",
            (artist_id, stance, author, content)
        )

    return {"status": "success"}
