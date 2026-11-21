"""FastAPI Web Server & REST API Router for K-Rank (Global K-Pop Ranking)"""

import hashlib
import json
import os
import re
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
import scoring  # K-Score 엔진 v2 — 결측 재정규화·백분위·분포 Tier·상관분석 (2026-11-16)

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


# ── 공개 쓰기 엔드포인트 보호 (2026-11-22 야간 감사) ────────────────────────────
# 토론·피드백은 로그인 없이 누구나 POST 할 수 있는데 상한도 검증도 없어서
#   (1) 초당 대량 도배(스팸) (2) 200자 넘는 본문 (3) HTML/스크립트 삽입이 가능했다.
# 응원(cheer)만 3중 중복 방지가 있고 토론에는 아무 장치가 없던 비대칭을 맞춘다.
DISCUSSION_MAX_LEN = 200
DISCUSSION_AUTHOR_MAX_LEN = 20
DISCUSSION_WINDOW_SEC = 600
DISCUSSION_MAX_POSTS = 5          # 동일 IP+UA 기준 10분에 5건
FEEDBACK_MAX_LEN = 1000
FEEDBACK_WINDOW_SEC = 3600
FEEDBACK_MAX_POSTS = 3            # 동일 IP+UA 기준 1시간에 3건

_HTML_TAG_RE = re.compile(r"<[^>]*>")
_KEEP_CONTROL = {"\n", "\t"}


def _clean_text(value: str, max_len: int) -> str:
    """태그 제거 + 제어문자 제거 + 길이 상한. 서버는 저장 전에 정규화한다."""
    text = (value or "").strip()
    text = _HTML_TAG_RE.sub("", text)
    text = "".join(ch for ch in text if ch in _KEEP_CONTROL or ch.isprintable())
    return text[:max_len]


def _post_rate_limited(conn, ip_hash: str, endpoint: str, max_posts: int, window_sec: int) -> bool:
    row = conn.execute(
        "SELECT COUNT(*) AS c FROM post_logs "
        "WHERE ip_hash = ? AND endpoint = ? AND created_at >= datetime('now', ?)",
        (ip_hash, endpoint, f"-{window_sec} seconds"),
    ).fetchone()
    return bool(row and row["c"] >= max_posts)


def _log_post(conn, ip_hash: str, endpoint: str, artist_id: Optional[int] = None) -> None:
    conn.execute(
        "INSERT INTO post_logs (ip_hash, endpoint, artist_id) VALUES (?, ?, ?)",
        (ip_hash, endpoint, artist_id),
    )


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

    # 분포 기반 Tier·백분위 산출 (2026-11-16 레드팀 대응)
    #   기존 절대 임계값 Tier 는 50명 전원이 86점 이상이라 B·C 가 0명 = 변별력 없음.
    #   순위 기반 등급과 백분위를 함께 내려준다.
    total_n = len(rows)
    rank_map = {}
    # kscore 내림차순 정렬 기준 순위(동점은 같은 순위)
    ordered = sorted(rows, key=lambda x: (-(x["kscore"] if x["kscore"] is not None else -1), x["id"]))
    prev_score, prev_rank = None, 0
    for idx, rr in enumerate(ordered, start=1):
        sc = rr["kscore"]
        if prev_score is not None and sc == prev_score:
            rank_map[rr["id"]] = prev_rank
        else:
            rank_map[rr["id"]] = idx
            prev_rank, prev_score = idx, sc

    results = []
    for r in rows:
        d = dict(r)
        d["tags"] = json.loads(d["tags_json"]) if d.get("tags_json") else []
        d["tags_en"] = json.loads(d["tags_en_json"]) if d.get("tags_en_json") else [f"#{d.get('name_en')}"]
        d["stats"] = json.loads(d["stats_json"]) if d.get("stats_json") else {}
        if not d.get("agency_en"):
            d["agency_en"] = d.get("agency")
        if not d.get("fandom_name_en"):
            d["fandom_name_en"] = d.get("fandom_name")
        if not d.get("signature_quote_en"):
            d["signature_quote_en"] = d.get("signature_quote")
        if not d.get("generation_en"):
            d["generation_en"] = d.get("generation")

        # 신뢰도·커버리지·분포 등급 (레드팀 P1·P2)
        try:
            v2 = scoring.calculate_kscore_v2(d.get("stats") or {})
        except Exception:
            v2 = {"kscore": d.get("kscore"), "data_completeness": 1.0,
                  "available_metrics": [], "missing_metrics": [], "confidence": "low"}
        rank = rank_map.get(d["id"], 0)
        d["rank"] = rank
        d["kscore_percentile"] = scoring.calculate_percentile(rank, total_n) if rank else 0.0
        d["tier_distribution"] = scoring.calculate_tier_by_rank(rank, total_n) if rank else d.get("tier")
        d["data_completeness"] = v2.get("data_completeness", 1.0)
        d["missing_metrics"] = v2.get("missing_metrics", [])
        d["confidence"] = v2.get("confidence", "low")
        d["assessment_label"] = ("데이터 부족" if (v2.get("data_completeness") or 0) < 0.8
                                 else "정량 평가")
        # 데이터 기준 시점 노출 (레드팀 P4 — 투명성)
        d["data_as_of"] = (d.get("updated_at") or "")[:10] or None
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
        d["tags_en"] = json.loads(d["tags_en_json"]) if d.get("tags_en_json") else [f"#{d.get('name_en')}"]
        d["stats"] = json.loads(d["stats_json"]) if d.get("stats_json") else {}
        if not d.get("agency_en"):
            d["agency_en"] = d.get("agency")
        if not d.get("fandom_name_en"):
            d["fandom_name_en"] = d.get("fandom_name")
        if not d.get("signature_quote_en"):
            d["signature_quote_en"] = d.get("signature_quote")
        if not d.get("generation_en"):
            d["generation_en"] = d.get("generation")

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
def create_discussion(artist_id: int, data: dict, request: Request):
    """Post a new fan discussion comment (rate limited, length capped, tags stripped)."""
    stance = _clean_text(data.get("stance", "💖 응원"), 20)
    author = _clean_text(data.get("author", "익명팬덤"), DISCUSSION_AUTHOR_MAX_LEN) or "익명팬덤"
    content = _clean_text(data.get("content", ""), DISCUSSION_MAX_LEN)
    is_official = 1 if data.get("is_official") else 0

    if not content:
        raise HTTPException(status_code=400, detail="Content cannot be empty")
    if len((data.get("content") or "").strip()) > DISCUSSION_MAX_LEN:
        raise HTTPException(
            status_code=400,
            detail=f"Content is limited to {DISCUSSION_MAX_LEN} characters.",
        )

    ip_hash = _generate_ip_hash(request)

    conn = get_db()
    with conn:
        if _post_rate_limited(conn, ip_hash, "discussion", DISCUSSION_MAX_POSTS, DISCUSSION_WINDOW_SEC):
            raise HTTPException(
                status_code=429,
                detail="Too many comments. Please try again later.",
                headers={"Retry-After": str(DISCUSSION_WINDOW_SEC)},
            )
        row = conn.execute("SELECT id FROM artists WHERE id = ?", (artist_id,)).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Artist not found")
        conn.execute(
            "INSERT INTO fan_discussions (artist_id, stance, author, content, is_official) VALUES (?, ?, ?, ?, ?)",
            (artist_id, stance, author, content, is_official)
        )
        _log_post(conn, ip_hash, "discussion", artist_id)

    return {"status": "success"}


@app.post("/api/feedback")
def submit_feedback(data: dict, request: Request):
    """Submit user feedback or donation inquiry (rate limited, length capped)."""
    category = _clean_text(data.get("category", "의견"), 20)
    content = _clean_text(data.get("content", ""), FEEDBACK_MAX_LEN)
    email = _clean_text(data.get("email", ""), 120)

    if not content:
        raise HTTPException(status_code=400, detail="Feedback content required")

    ip_hash = _generate_ip_hash(request)

    conn = get_db()
    with conn:
        if _post_rate_limited(conn, ip_hash, "feedback", FEEDBACK_MAX_POSTS, FEEDBACK_WINDOW_SEC):
            raise HTTPException(
                status_code=429,
                detail="Too many feedback submissions. Please try again later.",
                headers={"Retry-After": str(FEEDBACK_WINDOW_SEC)},
            )
        conn.execute(
            "INSERT INTO feedback (category, content, email) VALUES (?, ?, ?)",
            (category, content, email)
        )
        _log_post(conn, ip_hash, "feedback")

    return {"status": "success", "message": "Feedback received. Thank you!"}


@app.get("/api/support")
def read_support():
    """개발자 후원 링크 조회 — rank_core 공통 소스(Buy Me a Coffee).

    2026-11-16: polirank 와 동일한 링크를 쓴다. rank_core 를 고치면 두 사이트가
    함께 바뀌므로 사이트별로 링크를 따로 관리하지 않는다.
    """
    try:
        from rank_core import get_support_links
        links = get_support_links()
    except Exception:
        import os
        links = {
            "buymeacoffee": os.environ.get("BUYMEACOFFEE_URL", "https://buymeacoffee.com/javaleo"),
            "support_message": "이 사이트는 1인 개발자가 운영합니다. 커피 한 잔으로 응원해 주세요!",
        }
    return {"status": "success", "dev_buymeacoffee_url": links.get("buymeacoffee", ""),
            "support_message": links.get("support_message", "")}
