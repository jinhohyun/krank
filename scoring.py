"""K-Score 6대 팩트 지표 산출 & Tier 매핑 엔진 (v3.0)

변경 이력
  2026-11-16 1차 (레드팀 NEEDS_FIX 대응)
    - P1 결측 처리: stats.get(key, 50.0) 기본값 **완전 제거**.
      데이터 없는 지표를 50점(중간 성적)으로 위장하던 왜곡을 없애고,
      사용 가능한 지표만으로 가중치를 재정규화한다. 커버리지 부족 시 score=None.
    - P2 변별력: 백분위·분포 기반 Tier 제공.
    - P3 지표 중복: Pearson 상관계수 분석 추가.

  2026-11-16 2차 (가중치 재설계 — 진호님 승인 "2번 진행")
    - PCA 실측 결과 2요인 구조 확인 (누적 설명분산 86.4%):
        PC1 58.1% → music_stream, youtube_views, sns_growth, google_buzz (디지털 노출)
        PC2 28.3% → album_sales, fandom_power                        (팬덤 결집)
    - 6개 지표 독립 가중 → **2요인(디지털 노출 67.2% / 팬덤 결집 32.8%)** 재설계.
      비율은 각 요인의 설명분산(58.1 : 28.3)을 정규화한 값이다.
    - **z-score 표준화 후 합성**: 원시값이 81~99.5 구간에 몰려 있어
      가중치만 바꿔서는 변별력이 생기지 않았다(표준편차 2.57 → 12.63).
    - 40~100 구간 매핑: 최하위가 0점이 되어 '무능'으로 읽히는 것을 막는다.
"""
from pathlib import Path
import sys
import statistics

# 공통 통계 모듈(rank_core) 로드 — 사본/원본 어느 쪽에서 실행돼도 찾도록 경로 보강
_HERE = Path(__file__).resolve().parent
for _cand in (_HERE / "rank_core", _HERE.parent / "rank_core"):
    if (_cand / "rank_stats.py").is_file():
        if str(_cand) not in sys.path:
            sys.path.insert(0, str(_cand))
        break

import rank_stats as rs

# ── 원시 지표 (DB·API 키 이름 유지 — 하위 호환) ────────────────────────────
RAW_KEYS = (
    "music_stream",
    "album_sales",
    "youtube_views",
    "sns_growth",
    "google_buzz",
    "fandom_power",
)

# ── 2요인 구성 (PCA 로딩 기반) ────────────────────────────────────────────
# 디지털 노출 = 음원·유튜브·SNS·구글버즈 (PC1)
DIGITAL_WEIGHTS = {
    "music_stream": 0.30,
    "youtube_views": 0.25,
    "sns_growth": 0.20,
    "google_buzz": 0.25,
}
# 팬덤 결집 = 앨범·팬덤파워 (PC2)
FANDOM_WEIGHTS = {
    "album_sales": 0.60,
    "fandom_power": 0.40,
}
# 요인 가중 = 설명분산 정규화 (58.1 : 28.3 → 67.2% : 32.8%)
FACTOR_WEIGHTS = {"digital": 0.672, "fandom": 0.328}

# 출력 스케일 (최하위 0점 = '무능' 오독 방지)
SCORE_FLOOR = 40.0
SCORE_CEIL = 100.0

# 구버전 호환용 평평한 가중치 (결측 재정규화 경로에서 사용)
WEIGHTS = {
    "music_stream": 0.30,
    "album_sales": 0.25,
    "youtube_views": 0.20,
    "sns_growth": 0.15,
    "google_buzz": 0.05,
    "fandom_power": 0.05,
}

METRIC_LABELS_KR = {
    "music_stream": "음원 스트리밍",
    "album_sales": "앨범 판매",
    "youtube_views": "유튜브 조회",
    "sns_growth": "SNS 성장",
    "google_buzz": "구글 버즈",
    "fandom_power": "팬덤 파워",
}

MIN_COVERAGE = 0.5

SCORING_VERSION = "3.0"


# ── 표준화 기준값 (모집단 전체로 계산) ────────────────────────────────────
def compute_population_stats(all_stats: list) -> dict:
    """모집단 평균·표준편차 계산 (z-score 표준화용).

    반환: {"mu": {k: float}, "sd": {k: float}, "n": int}
    표준편차가 0인 지표는 sd 를 1.0 으로 둬 0으로 나누기를 막는다.
    """
    rows = [s for s in (all_stats or []) if isinstance(s, dict)]
    mu, sd = {}, {}
    for k in RAW_KEYS:
        vals = [float(r[k]) for r in rows if r.get(k) is not None]
        if not vals:
            mu[k], sd[k] = 0.0, 1.0
            continue
        mu[k] = statistics.mean(vals)
        p = statistics.pstdev(vals) if len(vals) > 1 else 0.0
        sd[k] = p if p > 0 else 1.0
    return {"mu": mu, "sd": sd, "n": len(rows)}


def _z(value: float, key: str, pop: dict) -> float:
    """지표값 → z-score. 모집단 통계가 없으면 0(중립) 반환."""
    if not pop or not isinstance(pop, dict):
        return 0.0
    m = (pop.get("mu") or {}).get(key)
    s = (pop.get("sd") or {}).get(key)
    if m is None or not s:
        return 0.0
    return (float(value) - m) / s


def factor_scores(stats: dict, pop: dict) -> dict:
    """2요인(디지털 노출 / 팬덤 결집) z-score 합성.

    결측 지표는 그 요인의 가중치에서 제외하고 재정규화한다(50점 대체 금지).
    """
    stats = stats or {}

    def _agg(weights: dict) -> tuple:
        avail = [(k, w) for k, w in weights.items() if stats.get(k) is not None]
        wsum = sum(w for _, w in avail)
        if wsum <= 0:
            return (0.0, 0.0)
        z = sum(_z(stats[k], k, pop) * w for k, w in avail) / wsum
        return (z, wsum / sum(weights.values()))

    dz, dcov = _agg(DIGITAL_WEIGHTS)
    fz, fcov = _agg(FANDOM_WEIGHTS)
    return {"digital": dz, "fandom": fz,
            "digital_coverage": round(dcov, 3),
            "fandom_coverage": round(fcov, 3)}


def _map_to_scale(composite: float, lo: float, hi: float) -> float:
    """합성 z 값을 SCORE_FLOOR~SCORE_CEIL 로 선형 매핑."""
    if hi <= lo:
        return round((SCORE_FLOOR + SCORE_CEIL) / 2.0, 1)
    ratio = (composite - lo) / (hi - lo)
    ratio = max(0.0, min(1.0, ratio))
    return round(SCORE_FLOOR + ratio * (SCORE_CEIL - SCORE_FLOOR), 1)


def calculate_composites(all_stats: list) -> list:
    """모집단 전체의 2요인 합성값 계산 (스케일 매핑의 lo/hi 산출용)."""
    rows = [s for s in (all_stats or []) if isinstance(s, dict)]
    pop = compute_population_stats(rows)
    out = []
    for r in rows:
        fs = factor_scores(r, pop)
        comp = (fs["digital"] * FACTOR_WEIGHTS["digital"]
                + fs["fandom"] * FACTOR_WEIGHTS["fandom"])
        out.append({"stats": r, "composite": comp, "factors": fs})
    return out


# ── 기존 시그니처 (하위 호환) ──────────────────────────────────────────────
def calculate_kscore(stats: dict) -> float:
    """하위 호환용 원점수.

    ⚠️ 모집단 통계가 없으면 z-score 를 쓸 수 없으므로 결측 재정규화 점수를 돌려준다.
    실제 서비스 경로(calculate_kscore_v2 + pop)는 모집단 상대 위치로 계산한다.
    """
    res = rs.renormalize(stats or {}, WEIGHTS, min_weight=MIN_COVERAGE)
    return round(res["score"], 1) if res["score"] is not None else 0.0


def calculate_kscore_v2(stats: dict, pop: dict = None) -> dict:
    """결측·커버리지를 정직하게 반영한 K-Score.

    pop 이 주어지면 2요인 z-score 경로(모집단 상대 위치)로 계산하고,
    없으면 결측 재정규화 절대점수로 폴백한다.

    반환
      kscore            : float | None — None 이면 랭킹 제외(커버리지 부족)
      data_completeness : 0.0~1.0
      available_metrics / missing_metrics : list[str]
      confidence        : "low" | "mid" | "high"
      factors           : {"digital": z, "fandom": z} (pop 있을 때)
      composite_z       : 요인 합성 z (pop 있을 때)
      scoring_version   : str
    """
    stats = stats or {}
    available = [k for k in RAW_KEYS if stats.get(k) is not None]
    missing = [k for k in RAW_KEYS if k not in available]
    coverage = sum(WEIGHTS[k] for k in available) / sum(WEIGHTS.values())

    base = {
        "data_completeness": round(coverage, 3),
        "available_metrics": available,
        "missing_metrics": missing,
        "confidence": rs.confidence_label(len(available)),
        "scoring_version": SCORING_VERSION,
    }

    if coverage < MIN_COVERAGE:
        base["kscore"] = None
        return base

    if pop:
        fs = factor_scores(stats, pop)
        base["factors"] = {"digital": round(fs["digital"], 3),
                           "fandom": round(fs["fandom"], 3)}
        base["composite_z"] = round(
            fs["digital"] * FACTOR_WEIGHTS["digital"]
            + fs["fandom"] * FACTOR_WEIGHTS["fandom"], 4)
        # 모집단 매핑 전 근사값 (정확한 점수는 app 이 calculate_composites 로 매핑)
        base["kscore"] = round(50.0 + base["composite_z"] * 10.0, 1)
        return base

    res = rs.renormalize(stats, WEIGHTS, min_weight=MIN_COVERAGE)
    base["kscore"] = round(res["score"], 1) if res.get("score") is not None else None
    return base


def calculate_tier(kscore: float) -> str:
    """절대 임계값 기반 Tier (하위 호환 유지)."""
    if kscore is None:
        return "N/A"
    if kscore >= 95.0:
        return "S+"
    elif kscore >= 90.0:
        return "S"
    elif kscore >= 80.0:
        return "A"
    elif kscore >= 70.0:
        return "B"
    else:
        return "C"


def calculate_tier_by_rank(rank: int, total: int) -> str:
    """분포 기반 Tier — 상위 10% S+, 다음 20% S, 다음 30% A, 다음 30% B, 하위 10% C."""
    return rs.tier_by_rank(rank, total)


def calculate_percentile(rank: int, total: int) -> float:
    """순위 기반 백분위 (1위 → 100에 가까움, 최하위 → 0에 가까움)."""
    return rs.percentile_from_rank(rank, total)


def analyze_metric_correlations(all_stats: list, threshold: float = 0.8) -> dict:
    """지표 간 상관계수 분석 — 중복 지표 검증용.

    2026-11-16 실측: 음원↔구글버즈 r=0.902, 앨범↔팬덤 r=0.822, SNS↔구글버즈 r=0.839
    → 2요인 재설계의 근거가 된 분석.
    """
    rows = [s for s in (all_stats or []) if isinstance(s, dict)]
    res = rs.analyze_correlations(rows, threshold=threshold)
    res["label_map"] = {k: METRIC_LABELS_KR.get(k, k) for k in RAW_KEYS}
    res["weights"] = dict(WEIGHTS)
    res["factor_weights"] = dict(FACTOR_WEIGHTS)
    return res


if __name__ == "__main__":
    ok = True

    # 1) 결측 지표를 50점으로 채우지 않는다
    full = {k: 90.0 for k in RAW_KEYS}
    part = {"music_stream": 90.0, "album_sales": 90.0,
            "youtube_views": 90.0, "sns_growth": 90.0}
    r_full = calculate_kscore_v2(full)
    r_part = calculate_kscore_v2(part)
    ok1 = (r_full["kscore"] is not None and r_part["kscore"] == 90.0
           and r_part["data_completeness"] < 1.0)
    print("PASS: 결측 대체 없음" if ok1 else "FAIL: 결측 대체 없음")
    ok &= ok1

    # 2) 커버리지 부족 → None
    r_low = calculate_kscore_v2({"music_stream": 90.0})
    print("PASS: 커버리지 부족 제외" if r_low["kscore"] is None else "FAIL: 커버리지 부족 제외")
    ok &= r_low["kscore"] is None

    # 3) 분포 Tier 가 여러 등급을 만든다
    tiers = {calculate_tier_by_rank(r, 50) for r in range(1, 51)}
    ok3 = len(tiers) >= 4
    print("PASS: 분포 Tier 다양성" if ok3 else f"FAIL: 분포 Tier {tiers}")
    ok &= ok3

    # 4) 백분위 범위
    p1, p50 = calculate_percentile(1, 50), calculate_percentile(50, 50)
    ok4 = (p1 > p50 and 0 <= p50 <= p1 <= 100)
    print("PASS: 백분위 범위" if ok4 else "FAIL: 백분위 범위")
    ok &= ok4

    # 5) 상관분석 동작
    rows = [{"music_stream": 90 + i, "album_sales": 88 + i, "youtube_views": 70 + i} for i in range(8)]
    c = analyze_metric_correlations(rows)
    ok5 = c["pair_count"] >= 2
    print("PASS: 상관분석" if ok5 else f"FAIL: 상관분석 {c}")
    ok &= ok5

    # 6) 2요인 z-score 표준화가 변별력을 만든다
    sample = []
    for i in range(10):
        sample.append({
            "music_stream": 90 + i * 0.9,
            "album_sales": 88 + i * 1.1,
            "youtube_views": 86 + i * 1.3,
            "sns_growth": 85 + i * 1.2,
            "google_buzz": 85 + i * 1.4,
            "fandom_power": 86 + i * 1.3,
        })
    comps = calculate_composites(sample)
    lo = min(x["composite"] for x in comps)
    hi = max(x["composite"] for x in comps)
    mapped = [_map_to_scale(x["composite"], lo, hi) for x in comps]
    spread = max(mapped) - min(mapped)
    ok6 = spread > 40.0
    print("PASS: 2요인 변별력" if ok6 else f"FAIL: 2요인 변별력 (폭 {spread:.1f})")
    ok &= ok6

    # 7) 매핑 하한/상한 준수
    ok7 = (_map_to_scale(lo, lo, hi) == SCORE_FLOOR
           and _map_to_scale(hi, lo, hi) == SCORE_CEIL)
    print("PASS: 스케일 경계" if ok7 else "FAIL: 스케일 경계")
    ok &= ok7

    # 8) 요인 가중 합 = 1.0
    ok8 = abs(sum(FACTOR_WEIGHTS.values()) - 1.0) < 1e-6
    print("PASS: 요인 가중 합" if ok8 else "FAIL: 요인 가중 합")
    ok &= ok8

    print("SELF-TEST", "PASS" if ok else "FAIL")
    sys.exit(0 if ok else 1)
