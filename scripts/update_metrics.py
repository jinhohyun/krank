#!/usr/bin/env python3
"""K-Rank 지표 갱신 파이프라인 (초안 v0.1 — 2026-11-22 야간 감사)

원칙
  1) **공식 API 로 얻을 수 있는 지표만** 자동 수집한다. (진호 님 기준: 공식 API 로
     자동화할 수 없으면 하지 않는다.) 크롤링·비공식 엔드포인트는 쓰지 않는다.
  2) 수집한 원값(raw)은 출처·수집시각과 함께 그대로 남긴다. 점수 변환은 별도 단계다.
  3) 지표가 없는 아티스트는 50점 대체가 아니라 가중치 재정규화(기존 scoring.py v2/v3)
     로 처리하고, 커버리지 50% 미만은 랭킹에서 뺀다.
  4) 기본 실행은 dry-run. DB 반영은 --apply 를 명시해야 한다.

수집 가능/불가 판정 (2026-11-22)
  YouTube Data API v3   공식  O   채널 statistics(subscriberCount, viewCount) — 일 10,000 unit, 50명이면 50 unit
  Spotify Web API       공식  O   artists/{id} followers.total, popularity — Client Credentials
  Last.fm API           공식  O   artist.getInfo listeners/playcount (음원 대체 지표)
  Circle Chart          공식  X   공개 API 없음 → 수동 입력(분기/월간) + provenance 기록
  Google Trends         공식  X   공개 API 없음 → 자동화 금지, 수동 참고만
  Instagram / X 지표     공식  X   임의 계정 지표 공개 API 없음 → 제외

사용
  python3 scripts/update_metrics.py            # dry-run: 무엇을 수집할지/몇 건인지 출력
  YOUTUBE_API_KEY=... SPOTIFY_CLIENT_ID=... SPOTIFY_CLIENT_SECRET=... \
      python3 scripts/update_metrics.py --fetch
  python3 scripts/update_metrics.py --apply    # data/raw 최신 스냅샷을 DB 에 반영
"""
from __future__ import annotations

import argparse
import base64
import datetime as dt
import json
import math
import os
import sqlite3
import sys
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DB_PATH = ROOT / "krank.db"
SOURCES_PATH = ROOT / "data" / "artist_sources.json"
RAW_DIR = ROOT / "data" / "raw"
LATEST_PATH = ROOT / "data" / "metrics_latest.json"

# 6축 지표 → 수집 소스 매핑. (지표명: (source, raw field, 변환 방식))
METRIC_MAP = {
    "youtube_views": ("youtube", "viewCount", "log"),
    "sns_growth": ("spotify", "followers", "log"),
    "music_stream": ("lastfm", "playcount", "log"),
}


def _http_json(url: str, headers: dict | None = None, timeout: int = 20) -> dict:
    req = urllib.request.Request(url, headers=headers or {"User-Agent": "krank-metrics/0.1"})
    with urllib.request.urlopen(req, timeout=timeout) as res:
        return json.loads(res.read().decode("utf-8"))


def _spotify_token() -> str | None:
    cid = os.environ.get("SPOTIFY_CLIENT_ID")
    secret = os.environ.get("SPOTIFY_CLIENT_SECRET")
    if not (cid and secret):
        return None
    basic = base64.b64encode(f"{cid}:{secret}".encode()).decode()
    req = urllib.request.Request(
        "https://accounts.spotify.com/api/token",
        data=b"grant_type=client_credentials",
        headers={"Authorization": f"Basic {basic}", "Content-Type": "application/x-www-form-urlencoded"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=20) as res:
        return json.loads(res.read().decode("utf-8")).get("access_token")


def fetch_youtube(channel_id: str, key: str) -> dict | None:
    url = (
        "https://www.googleapis.com/youtube/v3/channels?"
        + urllib.parse.urlencode({"part": "statistics", "id": channel_id, "key": key})
    )
    data = _http_json(url)
    items = data.get("items") or []
    if not items:
        return None
    st = items[0].get("statistics", {})
    return {"subscriberCount": int(st.get("subscriberCount", 0)), "viewCount": int(st.get("viewCount", 0))}


def fetch_spotify(artist_id: str, token: str) -> dict | None:
    data = _http_json(
        f"https://api.spotify.com/v1/artists/{urllib.parse.quote(artist_id)}",
        headers={"Authorization": f"Bearer {token}"},
    )
    return {
        "followers": int((data.get("followers") or {}).get("total", 0) or 0),
        "popularity": int(data.get("popularity", 0) or 0),
    }


def fetch_lastfm(name: str, key: str) -> dict | None:
    url = (
        "https://ws.audioscrobbler.com/2.0/?"
        + urllib.parse.urlencode(
            {"method": "artist.getInfo", "artist": name, "api_key": key, "format": "json"}
        )
    )
    data = _http_json(url)
    st = (data.get("artist") or {}).get("stats") or {}
    if not st:
        return None
    return {"listeners": int(st.get("listeners", 0) or 0), "playcount": int(st.get("playcount", 0) or 0)}


def load_artists() -> list[dict]:
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    rows = [dict(r) for r in con.execute("SELECT id, name, name_en, stats_json FROM artists ORDER BY id")]
    con.close()
    return rows


def load_sources() -> dict:
    if not SOURCES_PATH.exists():
        return {"artists": {}}
    return json.loads(SOURCES_PATH.read_text(encoding="utf-8"))


def collect(sources: dict) -> dict:
    """설정·키가 있는 소스만 수집한다. 없는 소스는 조용히 건너뛰고 기록만 남긴다."""
    yt_key = os.environ.get("YOUTUBE_API_KEY")
    fm_key = os.environ.get("LASTFM_API_KEY")
    sp_token = _spotify_token()

    raw: dict[str, dict] = {}
    skipped: dict[str, str] = {}
    if not yt_key:
        skipped["youtube"] = "YOUTUBE_API_KEY 없음"
    if not fm_key:
        skipped["lastfm"] = "LASTFM_API_KEY 없음"
    if not sp_token:
        skipped["spotify"] = "SPOTIFY_CLIENT_ID/SECRET 없음"

    for name_en, ids in (sources.get("artists") or {}).items():
        entry: dict[str, dict] = {}
        if yt_key and ids.get("youtube_channel_id"):
            try:
                v = fetch_youtube(ids["youtube_channel_id"], yt_key)
                if v:
                    entry["youtube"] = {**v, "source": "YouTube Data API v3", "fetched_at": _now()}
            except Exception as exc:  # noqa: BLE001 — 한 소스 실패가 전체를 막지 않게
                entry["youtube_error"] = str(exc)
        if sp_token and ids.get("spotify_artist_id"):
            try:
                v = fetch_spotify(ids["spotify_artist_id"], sp_token)
                if v:
                    entry["spotify"] = {**v, "source": "Spotify Web API", "fetched_at": _now()}
            except Exception as exc:  # noqa: BLE001
                entry["spotify_error"] = str(exc)
        if fm_key and (ids.get("lastfm_name") or name_en):
            try:
                v = fetch_lastfm(ids.get("lastfm_name") or name_en, fm_key)
                if v:
                    entry["lastfm"] = {**v, "source": "Last.fm API", "fetched_at": _now()}
            except Exception as exc:  # noqa: BLE001
                entry["lastfm_error"] = str(exc)
        if entry:
            raw[name_en] = entry
    return {"fetched_at": _now(), "skipped_sources": skipped, "artists": raw}


def _now() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()


def to_scores(raw: dict) -> dict[str, dict]:
    """원값 → 0~100 지표 점수. log 스케일 + 표본 min-max (동점/이상치 완화)."""
    values: dict[str, dict[str, float]] = {}
    for metric, (src, field, mode) in METRIC_MAP.items():
        col = {}
        for artist, entry in (raw.get("artists") or {}).items():
            src_entry = entry.get(src)
            if not src_entry or field not in src_entry:
                continue
            v = float(src_entry[field] or 0)
            col[artist] = math.log1p(v) if mode == "log" else v
        if not col:
            continue
        lo, hi = min(col.values()), max(col.values())
        span = (hi - lo) or 1.0
        for artist, v in col.items():
            values.setdefault(artist, {})[metric] = round((v - lo) / span * 100, 1)
    return values


def apply_to_db(scores: dict[str, dict]) -> int:
    if not scores:
        return 0
    sys.path.insert(0, str(ROOT))
    from scoring import calculate_kscore, calculate_tier  # noqa: PLC0415

    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    changed = 0
    for row in con.execute("SELECT id, name_en, stats_json FROM artists").fetchall():
        new = scores.get(row["name_en"])
        if not new:
            continue
        stats = json.loads(row["stats_json"] or "{}")
        stats.update(new)  # 수집된 지표만 덮어쓰고, 없는 지표는 기존 값을 유지(추후 재정규화 대상)
        kscore = calculate_kscore(stats)
        con.execute(
            "UPDATE artists SET stats_json = ?, kscore = ?, tier = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
            (json.dumps(stats, ensure_ascii=False), kscore, calculate_tier(kscore), row["id"]),
        )
        changed += 1
    con.commit()
    con.close()
    return changed


def main() -> int:
    ap = argparse.ArgumentParser(description="K-Rank 지표 갱신 (공식 API 전용)")
    ap.add_argument("--fetch", action="store_true", help="실제 API 호출 후 data/raw 에 스냅샷 저장")
    ap.add_argument("--apply", action="store_true", help="최신 스냅샷을 krank.db 에 반영")
    args = ap.parse_args()

    if args.apply:
        if not LATEST_PATH.exists():
            print("반영할 스냅샷이 없습니다:", LATEST_PATH)
            return 1
        snapshot = json.loads(LATEST_PATH.read_text(encoding="utf-8"))
        n = apply_to_db(to_scores(snapshot))
        print(f"DB 반영 완료: {n}명")
        return 0

    sources = load_sources()
    artists = load_artists()
    configured = sources.get("artists") or {}
    print(f"아티스트 {len(artists)}명 / 소스 매핑 {len(configured)}명")
    missing = [a["name_en"] for a in artists if a["name_en"] not in configured]
    if missing:
        print(f"매핑 없는 아티스트 {len(missing)}명 (예: {', '.join(missing[:5])})")

    if not args.fetch:
        print("\n[dry-run] 수집 예정 소스")
        print("  youtube_views ← YouTube Data API v3", "(키 있음)" if os.environ.get("YOUTUBE_API_KEY") else "(키 없음 → 건너뜀)")
        print("  sns_growth    ← Spotify Web API", "(키 있음)" if os.environ.get("SPOTIFY_CLIENT_ID") else "(키 없음 → 건너뜀)")
        print("  music_stream  ← Last.fm API", "(키 있음)" if os.environ.get("LASTFM_API_KEY") else "(키 없음 → 건너뜀)")
        print("  album_sales / google_buzz / fandom_power ← 공식 API 없음(수동 입력·provenance 유지)")
        print("\n실제 호출은 --fetch, DB 반영은 --apply.")
        return 0

    RAW_DIR.mkdir(parents=True, exist_ok=True)
    snapshot = collect(sources)
    out = RAW_DIR / f"metrics_{dt.datetime.now():%Y%m%d_%H%M%S}.json"
    out.write_text(json.dumps(snapshot, ensure_ascii=False, indent=1), encoding="utf-8")
    LATEST_PATH.write_text(json.dumps(snapshot, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"스냅샷 저장: {out} ({len(snapshot['artists'])}명)")
    if snapshot["skipped_sources"]:
        print("건너뛴 소스:", json.dumps(snapshot["skipped_sources"], ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
