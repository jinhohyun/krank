"""Bilingual Seed Extender for K-Rank (50 Artists)"""
import json
import os
from database import init_db

seed_path = os.path.join(os.path.dirname(__file__), "seed_data.json")
with open(seed_path, "r", encoding="utf-8") as f:
    artists = json.load(f)

agency_map = {
    "하이브 / 빅히트 뮤직": "HYBE / BIGHIT MUSIC",
    "YG 엔터테인먼트": "YG Entertainment",
    "어도어 (ADOR)": "ADOR",
    "JYP 엔터테인먼트": "JYP Entertainment",
    "하이브 / 플레디스": "HYBE / PLEDIS",
    "SM 엔터테인먼트": "SM Entertainment",
    "스타쉽 엔터테인먼트": "STARSHIP Entertainment",
    "하이브 / 빌리프랩": "HYBE / BELIFT LAB",
    "하이브 / 쏘스뮤직": "HYBE / SOURCE MUSIC",
    "큐브 엔터테인먼트": "CUBE Entertainment",
    "KQ 엔터테인먼트": "KQ Entertainment",
    "웨이크원": "WAKEONE",
    "타마고 프로덕션": "Tamago Production",
    "S2 엔터테인먼트": "S2 Entertainment",
    "하이브 / KOZ 엔터테인먼트": "HYBE / KOZ Entertainment",
    "어트랙트": "ATTRAKT",
    "EDAM 엔터테인먼트": "EDAM Entertainment",
    "하이업 엔터테인먼트": "High Up Entertainment",
    "웨이크원 / 클랩": "WAKEONE / KLAP",
    "워너뮤직 코리아": "Warner Music Korea",
    "비투비 컴퍼니": "BTOB Company",
    "RBW": "RBW",
    "WM 엔터테인먼트": "WM Entertainment",
    "드림캐쳐 컴퍼니": "Dreamcatcher Company",
    "모드하우스": "MODHAUS",
    "하이브 / 게펜 레코드": "HYBE / Geffen Records",
    "더블랙레이블": "THEBLACKLABEL",
    "어비스 컴퍼니": "ABYSS Company",
    "판타지오": "Fantagio",
    "DSP 미디어": "DSP Media",
    "위에화 엔터테인먼트": "YUEHUA Entertainment"
}

fandom_map = {
    "아미 (ARMY)": "ARMY",
    "블링크 (BLINK)": "BLINK",
    "버니즈 (Bunnies)": "Bunnies",
    "스테이 (STAY)": "STAY",
    "캐럿 (CARAT)": "CARAT",
    "마이 (MY)": "MY",
    "다이브 (DIVE)": "DIVE",
    "원스 (ONCE)": "ONCE",
    "엔진 (ENGENE)": "ENGENE",
    "피어너 (FEARNOT)": "FEARNOT",
    "모아 (MOA)": "MOA",
    "네버랜드 (NEVERLAND)": "NEVERLAND",
    "에이티니 (ATINY)": "ATINY",
    "제로즈 (ZEROSE)": "ZEROSE",
    "브리즈 (BRIIZE)": "BRIIZE",
    "42 (SAI)": "42 (SAI)",
    "글릿 (GLLIT)": "GLLIT",
    "몬스티즈 (MONSTIEZ)": "MONSTIEZ",
    "엔써 (NSWER)": "NSWER",
    "러비 (ReVeluv)": "ReVeluv",
    "엑소엘 (EXO-L)": "EXO-L",
    "유애나 (UAENA)": "UAENA",
    "소원 (SONE)": "SONE",
    "마이데이 (My Day)": "My Day",
    "바위게 (BAWIGE)": "BAWIGE",
    "키씨 (KISSY)": "KISSY",
    "원도어 (ONEDOOR)": "ONEDOOR",
    "트웨니 (TWENY)": "TWENY",
    "시즈니 (NCTzen)": "NCTzen",
    "샤이니월드 (SHINee World)": "SHINee World",
    "믿지 (MIDZY)": "MIDZY",
    "스윗 (SWITH)": "SWITH",
    "트레저메이커 (TREASURE MAKER)": "TREASURE MAKER",
    "러비티 (LUVITY)": "LUVITY",
    "케플리안 (Kep1ian)": "Kep1ian",
    "아가새 (I GOT7)": "I GOT7",
    "몬베베 (MONBEBE)": "MONBEBE",
    "멜로디 (MELODY)": "MELODY",
    "무무 (MOOMOO)": "MOOMOO",
    "미라클 (MIRACLE)": "MIRACLE",
    "인썸니아 (InSomnia)": "InSomnia",
    "웨이브 (WAV)": "WAV",
    "아이즈 (EYEKONS)": "EYEKONS",
    "미야오 (MEOW)": "MEOW",
    "악덕 (AKKA)": "AKKA",
    "미야네 (Miya-ne)": "Miya-ne",
    "아로하 (AROHA)": "AROHA",
    "히든카드 (Hidden KARD)": "Hidden KARD",
    "iE (아이)": "iE"
}

gen_map = {
    "5세대": "5th Gen",
    "4세대": "4th Gen",
    "3세대": "3rd Gen",
    "2세대": "2nd Gen"
}

for item in artists:
    item["agency_en"] = agency_map.get(item.get("agency"), item.get("agency"))
    item["fandom_name_en"] = fandom_map.get(item.get("fandom_name"), item.get("fandom_name"))
    item["generation_en"] = gen_map.get(item.get("generation"), "4th Gen")
    
    # Signature quote english fallback
    quote = item.get("signature_quote", "")
    if "(" in quote and ")" in quote:
        item["signature_quote_en"] = quote.split("(")[1].split(")")[0]
    else:
        item["signature_quote_en"] = quote

    # English tags
    tags = item.get("tags", [])
    item["tags_en"] = [f"#{item['name_en']}"] + [t.replace("세대", "Gen").replace("위", "No1") for t in tags[1:]]

with open(seed_path, "w", encoding="utf-8") as f:
    json.dump(artists, f, ensure_ascii=False, indent=2)

print("✓ Updated seed_data.json with full English fields!")
