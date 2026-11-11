"""Generate 50 production-grade K-Pop artists dataset with real-photo URLs and 6-axis stats."""
import json
import os
from database import init_db

artists = [
    {
        "id": 1, "name": "방탄소년단", "name_en": "BTS", "agency": "하이브 / 빅히트 뮤직", "debut_year": 2013,
        "photo_url": "https://images.unsplash.com/photo-1511671782779-c97d3d27a1d4?auto=format&fit=crop&w=800&q=80",
        "avatar_url": "https://api.dicebear.com/7.x/bottts/svg?seed=BTS&backgroundColor=b6e3f4",
        "fandom_name": "아미 (ARMY)", "signature_quote": "팀워크가 꿈을 이루게 해줍니다. (Teamwork makes the dream work)",
        "tags": ["#21세기팝아이콘", "#빌보드HOT100_1위", "#글로벌팬덤아미"],
        "is_verified": True, "generation": "3세대",
        "stats": {"music_stream": 98.5, "album_sales": 99.0, "youtube_views": 97.0, "sns_growth": 96.5, "google_buzz": 99.0, "fandom_power": 99.5}
    },
    {
        "id": 2, "name": "BLACKPINK", "name_en": "BLACKPINK", "agency": "YG 엔터테인먼트", "debut_year": 2016,
        "photo_url": "https://images.unsplash.com/photo-1514525253161-7a46d19cd819?auto=format&fit=crop&w=800&q=80",
        "avatar_url": "https://api.dicebear.com/7.x/bottts/svg?seed=BLACKPINK&backgroundColor=ffd5e5",
        "fandom_name": "블링크 (BLINK)", "signature_quote": "BLACKPINK in your area! 언제나 최고의 무대로 보답할게요.",
        "tags": ["#글로벌퀸", "#유튜브구독자1위", "#코첼라헤드라이너"],
        "is_verified": True, "generation": "3세대",
        "stats": {"music_stream": 96.0, "album_sales": 94.5, "youtube_views": 99.5, "sns_growth": 98.0, "google_buzz": 97.5, "fandom_power": 96.5}
    },
    {
        "id": 3, "name": "NewJeans", "name_en": "NewJeans", "agency": "어도어 (ADOR)", "debut_year": 2022,
        "photo_url": "https://images.unsplash.com/photo-1492684223066-81342ee5ff30?auto=format&fit=crop&w=800&q=80",
        "avatar_url": "https://api.dicebear.com/7.x/bottts/svg?seed=NewJeans&backgroundColor=d1d5db",
        "fandom_name": "버니즈 (Bunnies)", "signature_quote": "매일 찾게 되고 언제 입어도 질리지 않는 청바지처럼!",
        "tags": ["#이지리스닝", "#빌보드200_1위", "#Y2K감성"],
        "is_verified": True, "generation": "4세대",
        "stats": {"music_stream": 97.0, "album_sales": 92.0, "youtube_views": 93.5, "sns_growth": 95.0, "google_buzz": 94.0, "fandom_power": 93.0}
    },
    {
        "id": 4, "name": "Stray Kids", "name_en": "Stray Kids", "agency": "JYP 엔터테인먼트", "debut_year": 2018,
        "photo_url": "https://images.unsplash.com/photo-1470225620780-dba8ba36b745?auto=format&fit=crop&w=800&q=80",
        "avatar_url": "https://api.dicebear.com/7.x/bottts/svg?seed=StrayKids&backgroundColor=fef3c7",
        "fandom_name": "스테이 (STAY)", "signature_quote": "Stray Kids Everywhere All Around the World!",
        "tags": ["#자체제작돌", "#빌보드200_4연속1위", "#글로벌음반강자"],
        "is_verified": True, "generation": "4세대",
        "stats": {"music_stream": 91.5, "album_sales": 98.0, "youtube_views": 92.0, "sns_growth": 93.0, "google_buzz": 92.5, "fandom_power": 95.0}
    },
    {
        "id": 5, "name": "세븐틴", "name_en": "SEVENTEEN", "agency": "하이브 / 플레디스", "debut_year": 2015,
        "photo_url": "https://images.unsplash.com/photo-1501386761578-eac5c94b800a?auto=format&fit=crop&w=800&q=80",
        "avatar_url": "https://api.dicebear.com/7.x/bottts/svg?seed=SEVENTEEN&backgroundColor=e0e7ff",
        "fandom_name": "캐럿 (CARAT)", "signature_quote": "손을 잡고 함께 걸어가자, 세븐틴과 캐럿의 칼군무와 에너지!",
        "tags": ["#자체제작칼군무", "#단일앨범500만장", "#음반제왕"],
        "is_verified": True, "generation": "3세대",
        "stats": {"music_stream": 92.0, "album_sales": 99.5, "youtube_views": 89.5, "sns_growth": 90.0, "google_buzz": 91.0, "fandom_power": 96.0}
    },
    {
        "id": 6, "name": "aespa", "name_en": "aespa", "agency": "SM 엔터테인먼트", "debut_year": 2020,
        "photo_url": "https://images.unsplash.com/photo-1516450360452-9312f5e86fc7?auto=format&fit=crop&w=800&q=80",
        "avatar_url": "https://api.dicebear.com/7.x/bottts/svg?seed=aespa&backgroundColor=f3e8ff",
        "fandom_name": "마이 (MY)", "signature_quote": "쇠맛 쇠맛! 메타버스 세계관과 차원 다른 카리스마!",
        "tags": ["#쇠맛Kpop", "#Supernova히트", "#메타버스아이돌"],
        "is_verified": True, "generation": "4세대",
        "stats": {"music_stream": 96.5, "album_sales": 91.0, "youtube_views": 94.0, "sns_growth": 92.0, "google_buzz": 95.0, "fandom_power": 91.5}
    },
    {
        "id": 7, "name": "IVE", "name_en": "IVE", "agency": "스타쉽 엔터테인먼트", "debut_year": 2021,
        "photo_url": "https://images.unsplash.com/photo-1469488865564-c2de10f69f96?auto=format&fit=crop&w=800&q=80",
        "avatar_url": "https://api.dicebear.com/7.x/bottts/svg?seed=IVE&backgroundColor=fce7f3",
        "fandom_name": "다이브 (DIVE)", "signature_quote": "나르시시즘과 주체적인 자신감, 그것이 바로 IVE!",
        "tags": ["#자기애아이콘", "#음원퀸", "#초통령아이돌"],
        "is_verified": True, "generation": "4세대",
        "stats": {"music_stream": 95.5, "album_sales": 90.5, "youtube_views": 91.0, "sns_growth": 91.5, "google_buzz": 92.0, "fandom_power": 90.0}
    },
    {
        "id": 8, "name": "TWICE", "name_en": "TWICE", "agency": "JYP 엔터테인먼트", "debut_year": 2015,
        "photo_url": "https://images.unsplash.com/photo-1526478806334-5fd488fcaabc?auto=format&fit=crop&w=800&q=80",
        "avatar_url": "https://api.dicebear.com/7.x/bottts/svg?seed=TWICE&backgroundColor=fee2e2",
        "fandom_name": "원스 (ONCE)", "signature_quote": "One in a Million! 안녕하세요 트와이스입니다!",
        "tags": ["#글로벌스타디움투어", "#국민걸그룹", "#9인9색"],
        "is_verified": True, "generation": "3세대",
        "stats": {"music_stream": 89.0, "album_sales": 91.5, "youtube_views": 93.0, "sns_growth": 89.5, "google_buzz": 90.0, "fandom_power": 92.0}
    },
    {
        "id": 9, "name": "ENHYPEN", "name_en": "ENHYPEN", "agency": "하이브 / 빌리프랩", "debut_year": 2020,
        "photo_url": "https://images.unsplash.com/photo-1511671782779-c97d3d27a1d4?auto=format&fit=crop&w=800&q=80",
        "avatar_url": "https://api.dicebear.com/7.x/bottts/svg?seed=ENHYPEN&backgroundColor=c7d2fe",
        "fandom_name": "엔진 (ENGENE)", "signature_quote": "연결하고 다리를 놓아 서로를 성장시키는 글로벌 서사!",
        "tags": ["#글로벌밀리언셀러", "#다크판타지", "#월드투어강자"],
        "is_verified": True, "generation": "4세대",
        "stats": {"music_stream": 90.0, "album_sales": 95.0, "youtube_views": 89.0, "sns_growth": 92.5, "google_buzz": 88.5, "fandom_power": 93.5}
    },
    {
        "id": 10, "name": "LE SSERAFIM", "name_en": "LE SSERAFIM", "agency": "하이브 / 쏘스뮤직", "debut_year": 2022,
        "photo_url": "https://images.unsplash.com/photo-1514525253161-7a46d19cd819?auto=format&fit=crop&w=800&q=80",
        "avatar_url": "https://api.dicebear.com/7.x/bottts/svg?seed=LESSERAFIM&backgroundColor=fbcfe8",
        "fandom_name": "피어너 (FEARNOT)", "signature_quote": "IM FEARLESS! 세상의 시선에 흔들리지 않는 당당함!",
        "tags": ["#걸그룹퍼포먼스최강", "#빌보드HOT100진입", "#EASY히트"],
        "is_verified": True, "generation": "4세대",
        "stats": {"music_stream": 93.5, "album_sales": 90.0, "youtube_views": 92.0, "sns_growth": 93.0, "google_buzz": 92.0, "fandom_power": 90.5}
    },
    {
        "id": 11, "name": "투모로우바이투게더", "name_en": "TOMORROW X TOGETHER", "agency": "하이브 / 빅히트 뮤직", "debut_year": 2019,
        "photo_url": "https://images.unsplash.com/photo-1492684223066-81342ee5ff30?auto=format&fit=crop&w=800&q=80",
        "avatar_url": "https://api.dicebear.com/7.x/bottts/svg?seed=TXT&backgroundColor=ddd6fe",
        "fandom_name": "모아 (MOA)", "signature_quote": "서로 다른 너와 내가 하나의 꿈으로 모여 만들어가는 내일!",
        "tags": ["#청춘동화", "#빌보드200_1위", "#북미돔투어"],
        "is_verified": True, "generation": "4세대",
        "stats": {"music_stream": 91.0, "album_sales": 96.0, "youtube_views": 88.5, "sns_growth": 91.0, "google_buzz": 90.0, "fandom_power": 94.0}
    },
    {
        "id": 12, "name": "(여자)아이들", "name_en": "(G)I-DLE", "agency": "큐브 엔터테인먼트", "debut_year": 2018,
        "photo_url": "https://images.unsplash.com/photo-1470225620780-dba8ba36b745?auto=format&fit=crop&w=800&q=80",
        "avatar_url": "https://api.dicebear.com/7.x/bottts/svg?seed=GIDLE&backgroundColor=fed7aa",
        "fandom_name": "네버랜드 (NEVERLAND)", "signature_quote": "편견을 깨는 주체적인 음악, 자체 프로듀싱의 정점!",
        "tags": ["#자체프로듀싱", "#SuperLady", "#음원차트올킬"],
        "is_verified": True, "generation": "4세대",
        "stats": {"music_stream": 94.5, "album_sales": 89.0, "youtube_views": 93.0, "sns_growth": 90.5, "google_buzz": 93.0, "fandom_power": 89.0}
    },
    {
        "id": 13, "name": "에이티즈", "name_en": "ATEEZ", "agency": "KQ 엔터테인먼트", "debut_year": 2018,
        "photo_url": "https://images.unsplash.com/photo-1501386761578-eac5c94b800a?auto=format&fit=crop&w=800&q=80",
        "avatar_url": "https://api.dicebear.com/7.x/bottts/svg?seed=ATEEZ&backgroundColor=bfdbfe",
        "fandom_name": "에이티니 (ATINY)", "signature_quote": "8명이 1팀으로 항해하는 폭발적인 무대 에너지!",
        "tags": ["#빌보드200_1위", "#코첼라최초남돌", "#무대장인"],
        "is_verified": True, "generation": "4세대",
        "stats": {"music_stream": 88.5, "album_sales": 95.5, "youtube_views": 90.0, "sns_growth": 91.5, "google_buzz": 89.0, "fandom_power": 95.0}
    },
    {
        "id": 14, "name": "ZEROBASEONE", "name_en": "ZEROBASEONE", "agency": "웨이크원", "debut_year": 2023,
        "photo_url": "https://images.unsplash.com/photo-1516450360452-9312f5e86fc7?auto=format&fit=crop&w=800&q=80",
        "avatar_url": "https://api.dicebear.com/7.x/bottts/svg?seed=ZB1&backgroundColor=fef08a",
        "fandom_name": "제로즈 (ZEROSE)", "signature_quote": "0에서 시작해 1이 되는 자유로운 여정!",
        "tags": ["#데뷔앨범더블밀리언", "#5세대대표남돌", "#화력최강"],
        "is_verified": True, "generation": "5세대",
        "stats": {"music_stream": 87.0, "album_sales": 96.5, "youtube_views": 86.5, "sns_growth": 90.0, "google_buzz": 88.0, "fandom_power": 96.0}
    },
    {
        "id": 15, "name": "라이즈", "name_en": "RIIZE", "agency": "SM 엔터테인먼트", "debut_year": 2023,
        "photo_url": "https://images.unsplash.com/photo-1469488865564-c2de10f69f96?auto=format&fit=crop&w=800&q=80",
        "avatar_url": "https://api.dicebear.com/7.x/bottts/svg?seed=RIIZE&backgroundColor=bbf7d0",
        "fandom_name": "브리즈 (BRIIZE)", "signature_quote": "함께 성장하고 실현하는 이모셔널 팝!",
        "tags": ["#이모셔널팝", "#GetAGuitar", "#5세대아이콘"],
        "is_verified": True, "generation": "5세대",
        "stats": {"music_stream": 93.0, "album_sales": 93.5, "youtube_views": 89.0, "sns_growth": 94.0, "google_buzz": 91.5, "fandom_power": 92.5}
    },
    {
        "id": 16, "name": "TWS", "name_en": "TWS", "agency": "하이브 / 플레디스", "debut_year": 2024,
        "photo_url": "https://images.unsplash.com/photo-1526478806334-5fd488fcaabc?auto=format&fit=crop&w=800&q=80",
        "avatar_url": "https://api.dicebear.com/7.x/bottts/svg?seed=TWS&backgroundColor=e9d5ff",
        "fandom_name": "42 (SAI)", "signature_quote": "첫 만남은 계획대로 되지 않아, 청량 감성의 신예!",
        "tags": ["#첫만남은계획대로되지않아", "#보이후드팝", "#신인상싹쓸이"],
        "is_verified": True, "generation": "5세대",
        "stats": {"music_stream": 94.0, "album_sales": 89.5, "youtube_views": 88.0, "sns_growth": 92.0, "google_buzz": 93.5, "fandom_power": 90.0}
    },
    {
        "id": 17, "name": "아일릿", "name_en": "ILLIT", "agency": "하이브 / 빌리프랩", "debut_year": 2024,
        "photo_url": "https://images.unsplash.com/photo-1511671782779-c97d3d27a1d4?auto=format&fit=crop&w=800&q=80",
        "avatar_url": "https://api.dicebear.com/7.x/bottts/svg?seed=ILLIT&backgroundColor=fce7f3",
        "fandom_name": "글릿 (GLLIT)", "signature_quote": "무엇이든 될 수 있는 엉뚱발랄 10대들의 시그널!",
        "tags": ["#Magnetic", "#빌보드HOT100신기록", "#글로벌숏폼대세"],
        "is_verified": True, "generation": "5세대",
        "stats": {"music_stream": 96.0, "album_sales": 88.0, "youtube_views": 94.5, "sns_growth": 95.5, "google_buzz": 96.0, "fandom_power": 88.5}
    },
    {
        "id": 18, "name": "베이비몬스터", "name_en": "BABYMONSTER", "agency": "YG 엔터테인먼트", "debut_year": 2024,
        "photo_url": "https://images.unsplash.com/photo-1514525253161-7a46d19cd819?auto=format&fit=crop&w=800&q=80",
        "avatar_url": "https://api.dicebear.com/7.x/bottts/svg?seed=BABYMONSTER&backgroundColor=fed7aa",
        "fandom_name": "몬스티즈 (MONSTIEZ)", "signature_quote": "YG의 DNA를 이은 라이브 보컬 몬스터!",
        "tags": ["#SHEESH", "#유튜브괴물신인", "#올라운더걸그룹"],
        "is_verified": True, "generation": "5세대",
        "stats": {"music_stream": 90.5, "album_sales": 91.0, "youtube_views": 96.0, "sns_growth": 93.5, "google_buzz": 91.0, "fandom_power": 91.0}
    },
    {
        "id": 19, "name": "NMIXX", "name_en": "NMIXX", "agency": "JYP 엔터테인먼트", "debut_year": 2022,
        "photo_url": "https://images.unsplash.com/photo-1492684223066-81342ee5ff30?auto=format&fit=crop&w=800&q=80",
        "avatar_url": "https://api.dicebear.com/7.x/bottts/svg?seed=NMIXX&backgroundColor=ccfbf1",
        "fandom_name": "엔써 (NSWER)", "signature_quote": "장르를 믹스한 MIXX POP, 폭발적인 핸드마이크 라이브!",
        "tags": ["#MIXXPOP", "#보컬천재", "#DASH"],
        "is_verified": True, "generation": "4세대",
        "stats": {"music_stream": 89.5, "album_sales": 90.0, "youtube_views": 89.0, "sns_growth": 88.5, "google_buzz": 89.5, "fandom_power": 90.0}
    },
    {
        "id": 20, "name": "Red Velvet", "name_en": "Red Velvet", "agency": "SM 엔터테인먼트", "debut_year": 2014,
        "photo_url": "https://images.unsplash.com/photo-1470225620780-dba8ba36b745?auto=format&fit=crop&w=800&q=80",
        "avatar_url": "https://api.dicebear.com/7.x/bottts/svg?seed=RedVelvet&backgroundColor=fecdd3",
        "fandom_name": "러비 (ReVeluv)", "signature_quote": "강렬하고 클래식한 레드와 벨벳의 완벽한 조화!",
        "tags": ["#콘셉트퀸", "#Psycho", "#서머퀸"],
        "is_verified": True, "generation": "3세대",
        "stats": {"music_stream": 88.0, "album_sales": 87.5, "youtube_views": 91.0, "sns_growth": 88.0, "google_buzz": 87.0, "fandom_power": 89.5}
    },
    {
        "id": 21, "name": "EXO", "name_en": "EXO", "agency": "SM 엔터테인먼트", "debut_year": 2012,
        "photo_url": "https://images.unsplash.com/photo-1501386761578-eac5c94b800a?auto=format&fit=crop&w=800&q=80",
        "avatar_url": "https://api.dicebear.com/7.x/bottts/svg?seed=EXO&backgroundColor=e2e8f0",
        "fandom_name": "엑소엘 (EXO-L)", "signature_quote": "WE ARE ONE! 엑소 사랑하자!",
        "tags": ["#KPOP킹", "#밀리언셀러신화", "#세계관시초"],
        "is_verified": True, "generation": "3세대",
        "stats": {"music_stream": 87.5, "album_sales": 94.0, "youtube_views": 90.5, "sns_growth": 86.5, "google_buzz": 88.0, "fandom_power": 95.5}
    },
    {
        "id": 22, "name": "아이유", "name_en": "IU", "agency": "EDAM 엔터테인먼트", "debut_year": 2008,
        "photo_url": "https://images.unsplash.com/photo-1516450360452-9312f5e86fc7?auto=format&fit=crop&w=800&q=80",
        "avatar_url": "https://api.dicebear.com/7.x/bottts/svg?seed=IU&backgroundColor=d8b4fe",
        "fandom_name": "유애나 (UAENA)", "signature_quote": "음악으로 전하는 진심과 위로, 독보적인 싱어송라이터!",
        "tags": ["#음원퀸", "#국민가수", "#상암벌월드투어"],
        "is_verified": True, "generation": "2세대",
        "stats": {"music_stream": 99.0, "album_sales": 92.5, "youtube_views": 95.0, "sns_growth": 94.0, "google_buzz": 98.0, "fandom_power": 97.0}
    },
    {
        "id": 23, "name": "태연", "name_en": "TAEYEON", "agency": "SM 엔터테인먼트", "debut_year": 2007,
        "photo_url": "https://images.unsplash.com/photo-1469488865564-c2de10f69f96?auto=format&fit=crop&w=800&q=80",
        "avatar_url": "https://api.dicebear.com/7.x/bottts/svg?seed=TAEYEON&backgroundColor=fae8ff",
        "fandom_name": "소원 (SONE)", "signature_quote": "믿고 듣는 태연, 보컬퀸의 장르를 초월한 울림!",
        "tags": ["#믿듣탱", "#독보적보컬퀸", "#음원강자"],
        "is_verified": True, "generation": "2세대",
        "stats": {"music_stream": 93.0, "album_sales": 88.0, "youtube_views": 89.5, "sns_growth": 91.0, "google_buzz": 90.0, "fandom_power": 92.0}
    },
    {
        "id": 24, "name": "DAY6", "name_en": "DAY6", "agency": "JYP 엔터테인먼트", "debut_year": 2015,
        "photo_url": "https://images.unsplash.com/photo-1526478806334-5fd488fcaabc?auto=format&fit=crop&w=800&q=80",
        "avatar_url": "https://api.dicebear.com/7.x/bottts/svg?seed=DAY6&backgroundColor=bae6fd",
        "fandom_name": "마이데이 (My Day)", "signature_quote": "모든 순간을 노래하는 K-밴드의 자존심!",
        "tags": ["#믿듣데", "#역주행신화", "#한페이지가될수있게"],
        "is_verified": True, "generation": "3세대",
        "stats": {"music_stream": 95.0, "album_sales": 88.5, "youtube_views": 90.0, "sns_growth": 90.0, "google_buzz": 94.0, "fandom_power": 94.5}
    },
    {
        "id": 25, "name": "QWER", "name_en": "QWER", "agency": "타마고 프로덕션", "debut_year": 2023,
        "photo_url": "https://images.unsplash.com/photo-1511671782779-c97d3d27a1d4?auto=format&fit=crop&w=800&q=80",
        "avatar_url": "https://api.dicebear.com/7.x/bottts/svg?seed=QWER&backgroundColor=a7f3d0",
        "fandom_name": "바위게 (BAWIGE)", "signature_quote": "서브컬처와 록 밴드의 만남, 고민중독 역주행!",
        "tags": ["#고민중독", "#걸밴드신화", "#음원차트상위권"],
        "is_verified": True, "generation": "5세대",
        "stats": {"music_stream": 94.0, "album_sales": 86.0, "youtube_views": 93.5, "sns_growth": 93.0, "google_buzz": 95.0, "fandom_power": 91.0}
    },
    {
        "id": 26, "name": "KISS OF LIFE", "name_en": "KISS OF LIFE", "agency": "S2 엔터테인먼트", "debut_year": 2023,
        "photo_url": "https://images.unsplash.com/photo-1514525253161-7a46d19cd819?auto=format&fit=crop&w=800&q=80",
        "avatar_url": "https://api.dicebear.com/7.x/bottts/svg?seed=KISSOFLIFE&backgroundColor=fef08a",
        "fandom_name": "키씨 (KISSY)", "signature_quote": "인공호흡처럼 K-POP 씬에 새로운 생명을 불어넣는다!",
        "tags": ["#핫걸라이브", "#Sticky", "#실력파5세대"],
        "is_verified": True, "generation": "5세대",
        "stats": {"music_stream": 91.5, "album_sales": 85.0, "youtube_views": 91.0, "sns_growth": 92.5, "google_buzz": 90.5, "fandom_power": 89.0}
    },
    {
        "id": 27, "name": "BOYNEXTDOOR", "name_en": "BOYNEXTDOOR", "agency": "하이브 / KOZ 엔터테인먼트", "debut_year": 2023,
        "photo_url": "https://images.unsplash.com/photo-1492684223066-81342ee5ff30?auto=format&fit=crop&w=800&q=80",
        "avatar_url": "https://api.dicebear.com/7.x/bottts/svg?seed=BOYNEXTDOOR&backgroundColor=fed7aa",
        "fandom_name": "원도어 (ONEDOOR)", "signature_quote": "옆집 소년들처럼 친근하고 위트 넘치는 에너지!",
        "tags": ["#지코프로듀싱", "#위트만점퍼포먼스", "#EarthDusty"],
        "is_verified": True, "generation": "5세대",
        "stats": {"music_stream": 88.0, "album_sales": 92.0, "youtube_views": 87.5, "sns_growth": 89.5, "google_buzz": 88.0, "fandom_power": 91.0}
    },
    {
        "id": 28, "name": "FIFTY FIFTY", "name_en": "FIFTY FIFTY", "agency": "어트랙트", "debut_year": 2022,
        "photo_url": "https://images.unsplash.com/photo-1470225620780-dba8ba36b745?auto=format&fit=crop&w=800&q=80",
        "avatar_url": "https://api.dicebear.com/7.x/bottts/svg?seed=FIFTYFIFTY&backgroundColor=d9f99d",
        "fandom_name": "트웨니 (TWENY)", "signature_quote": "Cupid 신화에서 재도약까지, 천상의 음색 보컬!",
        "tags": ["#Cupid", "#빌보드신화", "#음색요정"],
        "is_verified": True, "generation": "4세대",
        "stats": {"music_stream": 92.0, "album_sales": 84.0, "youtube_views": 92.5, "sns_growth": 88.0, "google_buzz": 89.0, "fandom_power": 86.0}
    },
    {
        "id": 29, "name": "NCT 127", "name_en": "NCT 127", "agency": "SM 엔터테인먼트", "debut_year": 2016,
        "photo_url": "https://images.unsplash.com/photo-1501386761578-eac5c94b800a?auto=format&fit=crop&w=800&q=80",
        "avatar_url": "https://api.dicebear.com/7.x/bottts/svg?seed=NCT127&backgroundColor=bef264",
        "fandom_name": "시즈니 (NCTzen)", "signature_quote": "서울을 기반으로 세계를 향해 나아가는 차원이 다른 네오!",
        "tags": ["#NEO", "#질주", "#독보적네오음악"],
        "is_verified": True, "generation": "3세대",
        "stats": {"music_stream": 87.0, "album_sales": 94.5, "youtube_views": 89.0, "sns_growth": 87.5, "google_buzz": 86.5, "fandom_power": 93.0}
    },
    {
        "id": 30, "name": "NCT DREAM", "name_en": "NCT DREAM", "agency": "SM 엔터테인먼트", "debut_year": 2016,
        "photo_url": "https://images.unsplash.com/photo-1516450360452-9312f5e86fc7?auto=format&fit=crop&w=800&q=80",
        "avatar_url": "https://api.dicebear.com/7.x/bottts/svg?seed=NCTDREAM&backgroundColor=fef08a",
        "fandom_name": "시즈니 (NCTzen)", "signature_quote": "7DREAM의 영원한 우정과 청춘 시너지!",
        "tags": ["#7DREAM", "#트리플밀리언셀러", "#청춘에너지"],
        "is_verified": True, "generation": "3세대",
        "stats": {"music_stream": 89.5, "album_sales": 96.0, "youtube_views": 88.5, "sns_growth": 89.0, "google_buzz": 88.5, "fandom_power": 94.0}
    },
    {
        "id": 31, "name": "샤이니", "name_en": "SHINee", "agency": "SM 엔터테인먼트", "debut_year": 2008,
        "photo_url": "https://images.unsplash.com/photo-1469488865564-c2de10f69f96?auto=format&fit=crop&w=800&q=80",
        "avatar_url": "https://api.dicebear.com/7.x/bottts/svg?seed=SHINee&backgroundColor=a5f3fc",
        "fandom_name": "샤이니월드 (SHINee World)", "signature_quote": "빛나는 샤이니입니다! 16년 차 현역 최정상 라이브!",
        "tags": ["#빛나는샤이니", "#라이브원탑", "#트렌드리더"],
        "is_verified": True, "generation": "2세대",
        "stats": {"music_stream": 86.5, "album_sales": 88.0, "youtube_views": 87.0, "sns_growth": 86.0, "google_buzz": 86.0, "fandom_power": 93.0}
    },
    {
        "id": 32, "name": "ITZY", "name_en": "ITZY", "agency": "JYP 엔터테인먼트", "debut_year": 2019,
        "photo_url": "https://images.unsplash.com/photo-1526478806334-5fd488fcaabc?auto=format&fit=crop&w=800&q=80",
        "avatar_url": "https://api.dicebear.com/7.x/bottts/svg?seed=ITZY&backgroundColor=fed7aa",
        "fandom_name": "믿지 (MIDZY)", "signature_quote": "EVERYTHING IN US! 당당함과 에너지의 퍼포먼스 퀸!",
        "tags": ["#달라달라", "#KPOP대표퍼포머", "#MIDZY"],
        "is_verified": True, "generation": "4세대",
        "stats": {"music_stream": 88.5, "album_sales": 89.0, "youtube_views": 91.5, "sns_growth": 88.0, "google_buzz": 87.5, "fandom_power": 89.0}
    },
    # 33 ~ 50: 18 Additional Production Artists
    {
        "id": 33, "name": "STAYC", "name_en": "STAYC", "agency": "하이업 엔터테인먼트", "debut_year": 2020,
        "photo_url": "https://images.unsplash.com/photo-1511671782779-c97d3d27a1d4?auto=format&fit=crop&w=800&q=80",
        "avatar_url": "https://api.dicebear.com/7.x/bottts/svg?seed=STAYC&backgroundColor=fce7f3",
        "fandom_name": "스윗 (SWITH)", "signature_quote": "Star To A Young Culture! 틴프레시의 대명사!",
        "tags": ["#틴프레시", "#ASAP", "#전원보컬재능"],
        "is_verified": True, "generation": "4세대",
        "stats": {"music_stream": 91.0, "album_sales": 87.0, "youtube_views": 90.0, "sns_growth": 89.0, "google_buzz": 89.5, "fandom_power": 88.0}
    },
    {
        "id": 34, "name": "TREASURE", "name_en": "TREASURE", "agency": "YG 엔터테인먼트", "debut_year": 2020,
        "photo_url": "https://images.unsplash.com/photo-1514525253161-7a46d19cd819?auto=format&fit=crop&w=800&q=80",
        "avatar_url": "https://api.dicebear.com/7.x/bottts/svg?seed=TREASURE&backgroundColor=bae6fd",
        "fandom_name": "트레저메이커 (TREASURE MAKER)", "signature_quote": "Find Your Treasure! 에너지 넘치는 무대 라이브!",
        "tags": ["#YG남돌", "#자체제작", "#아시아투어강자"],
        "is_verified": True, "generation": "4세대",
        "stats": {"music_stream": 87.5, "album_sales": 93.0, "youtube_views": 89.0, "sns_growth": 90.5, "google_buzz": 87.0, "fandom_power": 92.0}
    },
    {
        "id": 35, "name": "CRAVITY", "name_en": "CRAVITY", "agency": "스타쉽 엔터테인먼트", "debut_year": 2020,
        "photo_url": "https://images.unsplash.com/photo-1492684223066-81342ee5ff30?auto=format&fit=crop&w=800&q=80",
        "avatar_url": "https://api.dicebear.com/7.x/bottts/svg?seed=CRAVITY&backgroundColor=ddd6fe",
        "fandom_name": "러비티 (LUVITY)", "signature_quote": "독창적인 중력과 무한한 청춘 퍼포먼스!",
        "tags": ["#로드투킹덤우승", "#청춘에너지", "#퍼포먼스장인"],
        "is_verified": True, "generation": "4세대",
        "stats": {"music_stream": 85.0, "album_sales": 90.0, "youtube_views": 86.0, "sns_growth": 87.0, "google_buzz": 85.5, "fandom_power": 90.0}
    },
    {
        "id": 36, "name": "Kep1er", "name_en": "Kep1er", "agency": "웨이크원 / 클랩", "debut_year": 2022,
        "photo_url": "https://images.unsplash.com/photo-1470225620780-dba8ba36b745?auto=format&fit=crop&w=800&q=80",
        "avatar_url": "https://api.dicebear.com/7.x/bottts/svg?seed=Kep1er&backgroundColor=fed7aa",
        "fandom_name": "케플리안 (Kep1ian)", "signature_quote": "Catch your eye, Catch your mind! 하나로 빛나는 에너지!",
        "tags": ["#WADADA", "#글로벌걸그룹", "#칼군무퀸"],
        "is_verified": True, "generation": "4세대",
        "stats": {"music_stream": 87.0, "album_sales": 88.0, "youtube_views": 89.5, "sns_growth": 88.0, "google_buzz": 87.0, "fandom_power": 87.5}
    },
    {
        "id": 37, "name": "GOT7", "name_en": "GOT7", "agency": "워너뮤직 코리아", "debut_year": 2014,
        "photo_url": "https://images.unsplash.com/photo-1501386761578-eac5c94b800a?auto=format&fit=crop&w=800&q=80",
        "avatar_url": "https://api.dicebear.com/7.x/bottts/svg?seed=GOT7&backgroundColor=bbf7d0",
        "fandom_name": "아가새 (I GOT7)", "signature_quote": "GOT7 IS OUR NAME! 변치 않는 7명의 우정!",
        "tags": ["#마샬아츠트릭킹", "#글로벌투어", "#독립돌"],
        "is_verified": True, "generation": "3세대",
        "stats": {"music_stream": 86.0, "album_sales": 91.0, "youtube_views": 88.0, "sns_growth": 87.0, "google_buzz": 86.5, "fandom_power": 93.0}
    },
    {
        "id": 38, "name": "몬스타엑스", "name_en": "MONSTA X", "agency": "스타쉽 엔터테인먼트", "debut_year": 2015,
        "photo_url": "https://images.unsplash.com/photo-1516450360452-9312f5e86fc7?auto=format&fit=crop&w=800&q=80",
        "avatar_url": "https://api.dicebear.com/7.x/bottts/svg?seed=MONSTAX&backgroundColor=fef08a",
        "fandom_name": "몬베베 (MONBEBE)", "signature_quote": "HOO! MONSTA X! 피지컬과 짐승돌의 매력!",
        "tags": ["#피지컬원탑", "#짐승돌", "#빌보드200탑10"],
        "is_verified": True, "generation": "3세대",
        "stats": {"music_stream": 85.5, "album_sales": 91.5, "youtube_views": 87.0, "sns_growth": 86.0, "google_buzz": 86.0, "fandom_power": 92.5}
    },
    {
        "id": 39, "name": "BTOB", "name_en": "BTOB", "agency": "비투비 컴퍼니", "debut_year": 2012,
        "photo_url": "https://images.unsplash.com/photo-1469488865564-c2de10f69f96?auto=format&fit=crop&w=800&q=80",
        "avatar_url": "https://api.dicebear.com/7.x/bottts/svg?seed=BTOB&backgroundColor=bfdbfe",
        "fandom_name": "멜로디 (MELODY)", "signature_quote": "Born TO Beat! 하모니와 보컬의 감동!",
        "tags": ["#보컬천재돌", "#그리워하다", "#음원강자"],
        "is_verified": True, "generation": "2세대",
        "stats": {"music_stream": 90.0, "album_sales": 87.0, "youtube_views": 86.5, "sns_growth": 85.5, "google_buzz": 87.0, "fandom_power": 91.0}
    },
    {
        "id": 40, "name": "MAMAMOO", "name_en": "MAMAMOO", "agency": "RBW", "debut_year": 2014,
        "photo_url": "https://images.unsplash.com/photo-1526478806334-5fd488fcaabc?auto=format&fit=crop&w=800&q=80",
        "avatar_url": "https://api.dicebear.com/7.x/bottts/svg?seed=MAMAMOO&backgroundColor=fed7aa",
        "fandom_name": "무무 (MOOMOO)", "signature_quote": "믿고 듣는 마마무! 라이브 보컬의 전설!",
        "tags": ["#믿듣맘무", "#보컬퀸", "#HIP"],
        "is_verified": True, "generation": "3세대",
        "stats": {"music_stream": 91.0, "album_sales": 86.0, "youtube_views": 90.5, "sns_growth": 87.5, "google_buzz": 88.0, "fandom_power": 90.0}
    },
    {
        "id": 41, "name": "오마이걸", "name_en": "OH MY GIRL", "agency": "WM 엔터테인먼트", "debut_year": 2015,
        "photo_url": "https://images.unsplash.com/photo-1511671782779-c97d3d27a1d4?auto=format&fit=crop&w=800&q=80",
        "avatar_url": "https://api.dicebear.com/7.x/bottts/svg?seed=OHMYGIRL&backgroundColor=fce7f3",
        "fandom_name": "미라클 (MIRACLE)", "signature_quote": "살짝 설렜어! 기분 좋은 에너지와 콘셉트 요정!",
        "tags": ["#살짝설렜어", "#돌핀", "#콘셉트요정"],
        "is_verified": True, "generation": "3세대",
        "stats": {"music_stream": 90.5, "album_sales": 85.5, "youtube_views": 88.0, "sns_growth": 86.5, "google_buzz": 87.5, "fandom_power": 89.0}
    },
    {
        "id": 42, "name": "Dreamcatcher", "name_en": "Dreamcatcher", "agency": "드림캐쳐 컴퍼니", "debut_year": 2017,
        "photo_url": "https://images.unsplash.com/photo-1514525253161-7a46d19cd819?auto=format&fit=crop&w=800&q=80",
        "avatar_url": "https://api.dicebear.com/7.x/bottts/svg?seed=Dreamcatcher&backgroundColor=e2e8f0",
        "fandom_name": "인썸니아 (InSomnia)", "signature_quote": "락 메탈 댄스와 독보적인 다크 악몽 세계관!",
        "tags": ["#Kpop락메탈", "#해외콘서트강자", "#악몽세계관"],
        "is_verified": True, "generation": "3세대",
        "stats": {"music_stream": 85.0, "album_sales": 87.0, "youtube_views": 87.5, "sns_growth": 88.0, "google_buzz": 86.0, "fandom_power": 92.0}
    },
    {
        "id": 43, "name": "tripleS", "name_en": "tripleS", "agency": "모드하우스", "debut_year": 2023,
        "photo_url": "https://images.unsplash.com/photo-1492684223066-81342ee5ff30?auto=format&fit=crop&w=800&q=80",
        "avatar_url": "https://api.dicebear.com/7.x/bottts/svg?seed=tripleS&backgroundColor=a5f3fc",
        "fandom_name": "웨이브 (WAV)", "signature_quote": "모든 가능성의 아이돌, 24인 디멘션 시스템!",
        "tags": ["#24인걸그룹", "#GirlsNeverDie", "#팬참여프로듀싱"],
        "is_verified": True, "generation": "5세대",
        "stats": {"music_stream": 91.0, "album_sales": 89.5, "youtube_views": 88.5, "sns_growth": 91.0, "google_buzz": 90.0, "fandom_power": 89.5}
    },
    {
        "id": 44, "name": "KATSEYE", "name_en": "KATSEYE", "agency": "하이브 / 게펜 레코드", "debut_year": 2024,
        "photo_url": "https://images.unsplash.com/photo-1470225620780-dba8ba36b745?auto=format&fit=crop&w=800&q=80",
        "avatar_url": "https://api.dicebear.com/7.x/bottts/svg?seed=KATSEYE&backgroundColor=fecdd3",
        "fandom_name": "아이즈 (EYEKONS)", "signature_quote": "하이브의 글로벌 팝 걸그룹 프로젝트!",
        "tags": ["#Touch", "#글로벌팝", "#스포티파이바이럴"],
        "is_verified": True, "generation": "5세대",
        "stats": {"music_stream": 94.5, "album_sales": 82.0, "youtube_views": 92.0, "sns_growth": 95.0, "google_buzz": 94.0, "fandom_power": 87.0}
    },
    {
        "id": 45, "name": "MEOVV", "name_en": "MEOVV", "agency": "더블랙레이블", "debut_year": 2024,
        "photo_url": "https://images.unsplash.com/photo-1501386761578-eac5c94b800a?auto=format&fit=crop&w=800&q=80",
        "avatar_url": "https://api.dicebear.com/7.x/bottts/svg?seed=MEOVV&backgroundColor=e0e7ff",
        "fandom_name": "미야오 (MEOW)", "signature_quote": "테디 프로듀싱의 시크하고 강렬한 카리스마!",
        "tags": ["#MEOW", "#테디걸그룹", "#시크아우라"],
        "is_verified": True, "generation": "5세대",
        "stats": {"music_stream": 90.0, "album_sales": 85.0, "youtube_views": 93.0, "sns_growth": 93.0, "google_buzz": 92.0, "fandom_power": 87.5}
    },
    {
        "id": 46, "name": "AKMU", "name_en": "AKMU", "agency": "YG 엔터테인먼트", "debut_year": 2014,
        "photo_url": "https://images.unsplash.com/photo-1516450360452-9312f5e86fc7?auto=format&fit=crop&w=800&q=80",
        "avatar_url": "https://api.dicebear.com/7.x/bottts/svg?seed=AKMU&backgroundColor=d9f99d",
        "fandom_name": "악덕 (AKKA)", "signature_quote": "천재 남매의 위트 넘치는 독보적 음악 세계!",
        "tags": ["#음원연금", "#LoveLee", "#천재싱어송라이터"],
        "is_verified": True, "generation": "3세대",
        "stats": {"music_stream": 97.0, "album_sales": 83.0, "youtube_views": 92.0, "sns_growth": 89.0, "google_buzz": 94.0, "fandom_power": 90.0}
    },
    {
        "id": 47, "name": "선미", "name_en": "SUNMI", "agency": "어비스 컴퍼니", "debut_year": 2007,
        "photo_url": "https://images.unsplash.com/photo-1469488865564-c2de10f69f96?auto=format&fit=crop&w=800&q=80",
        "avatar_url": "https://api.dicebear.com/7.x/bottts/svg?seed=SUNMI&backgroundColor=fbcfe8",
        "fandom_name": "미야네 (Miya-ne)", "signature_quote": "선미팝이라는 독보적인 장르를 개척한 솔로퀸!",
        "tags": ["#선미팝", "#가시나", "#솔로퀸"],
        "is_verified": True, "generation": "2세대",
        "stats": {"music_stream": 90.0, "album_sales": 82.0, "youtube_views": 91.0, "sns_growth": 89.5, "google_buzz": 89.0, "fandom_power": 88.0}
    },
    {
        "id": 48, "name": "ASTRO", "name_en": "ASTRO", "agency": "판타지오", "debut_year": 2016,
        "photo_url": "https://images.unsplash.com/photo-1526478806334-5fd488fcaabc?auto=format&fit=crop&w=800&q=80",
        "avatar_url": "https://api.dicebear.com/7.x/bottts/svg?seed=ASTRO&backgroundColor=bae6fd",
        "fandom_name": "아로하 (AROHA)", "signature_quote": "Always You! 청량함과 감성의 별!",
        "tags": ["#청량돌", "#차은우", "#아로하"],
        "is_verified": True, "generation": "3세대",
        "stats": {"music_stream": 86.0, "album_sales": 90.0, "youtube_views": 88.0, "sns_growth": 91.0, "google_buzz": 92.0, "fandom_power": 90.5}
    },
    {
        "id": 49, "name": "KARD", "name_en": "KARD", "agency": "DSP 미디어", "debut_year": 2017,
        "photo_url": "https://images.unsplash.com/photo-1511671782779-c97d3d27a1d4?auto=format&fit=crop&w=800&q=80",
        "avatar_url": "https://api.dicebear.com/7.x/bottts/svg?seed=KARD&backgroundColor=fef08a",
        "fandom_name": "히든카드 (Hidden KARD)", "signature_quote": "혼성 그룹의 자존심, 남미 및 글로벌 열풍!",
        "tags": ["#혼성그룹원탑", "#남미강자", "#I_LOKE_IT"],
        "is_verified": True, "generation": "3세대",
        "stats": {"music_stream": 86.5, "album_sales": 81.0, "youtube_views": 89.0, "sns_growth": 88.5, "google_buzz": 86.0, "fandom_power": 88.0}
    },
    {
        "id": 50, "name": "TEMPEST", "name_en": "TEMPEST", "agency": "위에화 엔터테인먼트", "debut_year": 2022,
        "photo_url": "https://images.unsplash.com/photo-1514525253161-7a46d19cd819?auto=format&fit=crop&w=800&q=80",
        "avatar_url": "https://api.dicebear.com/7.x/bottts/svg?seed=TEMPEST&backgroundColor=bbf7d0",
        "fandom_name": "iE (아이)", "signature_quote": "거센 폭풍처럼 K-POP 씬을 사로잡는 강력한 에너제틱!",
        "tags": ["#폭풍돌", "#신인상수수상", "#에너제틱퍼포먼스"],
        "is_verified": True, "generation": "4세대",
        "stats": {"music_stream": 84.5, "album_sales": 88.0, "youtube_views": 86.0, "sns_growth": 86.5, "google_buzz": 85.0, "fandom_power": 88.5}
    }
]

seed_file = os.path.join(os.path.dirname(__file__), "seed_data.json")
with open(seed_file, "w", encoding="utf-8") as f:
    json.dump(artists, f, ensure_ascii=False, indent=2)

print(f"✓ Generated {len(artists)} artists into {seed_file}")

# Re-init DB with new schema & data
init_db()
print("✓ Database successfully re-seeded with 50 artists!")
