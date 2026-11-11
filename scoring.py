"""K-Score 6대 팩트 지표 산출 & Tier 매핑 엔진"""

def calculate_kscore(stats: dict) -> float:
    """
    Calculate weighted K-Score (100-point scale).
    - Music Stream: 30%
    - Album Sales: 25%
    - YouTube Views: 20%
    - SNS Growth: 15%
    - Google Buzz: 5%
    - Fandom Power: 5%
    """
    weights = {
        "music_stream": 0.30,
        "album_sales": 0.25,
        "youtube_views": 0.20,
        "sns_growth": 0.15,
        "google_buzz": 0.05,
        "fandom_power": 0.05
    }
    
    total = 0.0
    for key, weight in weights.items():
        score = stats.get(key, 50.0)
        total += score * weight
        
    return round(total, 1)


def calculate_tier(kscore: float) -> str:
    """Map K-Score to Tier Badge."""
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
