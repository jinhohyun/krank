import os
import sys

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

from rank_core import PlatformConfig, ScoringWeightConfig, WeightedScoringEngine

KRANK_CONFIG = PlatformConfig(
    platform_id="krank",
    platform_title="K-Rank (K-Culture & Artist Global Ranking)",
    entity_name_kr="아티스트",
    entity_name_en="K-Culture Artist",
    description="K-POP 및 K-컬처 글로벌 아티스트 실시간 버즈 & 팬덤 투표 랭킹 플랫폼",
    theme_primary_color="#EC4899", # Pink/K-Pop 스타일
    db_filename="krank.db",
    weights=ScoringWeightConfig(metrics={
        "fan_vote_score": 0.35,     # 글로벌 팬덤 투표
        "global_buzz_score": 0.25,  # 소셜/유튜브 버즈
        "music_chart_score": 0.25,  # 음원/음반 차트
        "fandom_power_score": 0.15  # 팬덤 커뮤니티 활성도
    }),
    custom_labels={
        "cheer_button": "팬심 투표 (Vote)",
        "entity_unit": "팀/인"
    }
)

class KrankScoringEngine(WeightedScoringEngine):
    """K-Rank 전용 확장 스코어링 엔진"""
    pass
