# 🏆 K-Rank (케이랭크) 사업 및 시스템 마스터 계획서 (Master Plan)

> **프로젝트명:** K-Rank (Global K-Pop & K-Celeb Fact Ranking Platform)  
> **문서 버전:** v1.0.0  
> **작성일:** 2026-11-11  
> **상태:** 기획 및 시스템 설계 단계 (MVP 개발 착수)  
> **저장 경로:** `01_Biz_Projects/krank/K_Rank_사업_및_시스템_마스터_계획서.md`  

---

## 1. 프로젝트 정의 & 서비스 비전 (Vision & Concept)

**K-Rank**는 주관적 감정이나 부정 투표에 휘둘리지 않고, **100% 글로벌 음원/영상/SNS/차트 팩트 데이터**에 기반하여 K-Pop 아티스트 및 K-셀럽의 종합 영향력 지수(**K-Score**)를 산출하고 실시간 랭킹 및 팬덤 커뮤니티를 제공하는 글로벌 데이터 & 엔터테인먼트 플랫폼입니다.

---

## 2. 해결하고자 하는 문제 (Problem Statement)

1. **투표 조작 및 팬덤 갈등**: 기존 K-Pop 인기투표 앱의 부정 투표, 유료 결제 유도, 주관성 시비로 인한 글로벌 팬덤 간 불신.
2. **파편화된 데이터**: Spotify 스트리밍, 빌보드, Circle Chart, YouTube 조회수, 인스타그램 팔로워가 분산되어 한눈에 종합 영향력을 파악하기 어려움.
3. **해외 팬덤의 한국 접근성 한계**: 해외 팬들이 한국 엔터 테크나 지하철/전광판 팬덤 광고에 참여하기 까다로운 구조.

---

## 3. 핵심 제공 가치 (Value Proposition)

- **100% 팩트 기반 K-Score 6대 정량 지표**: Spotify + YouTube + Circle Chart + Instagram/X + Google Trends + 팬덤 화력.
- **인터랙티브 3D 아바타 & 공식 실사진 플립(Flip)**: 최애 아티스트의 2D 캐리커쳐와 고화질 공식 사진 간 3D 플립 카드.
- **실시간 1클릭 하트 응원 & 팬덤 한줄 토론 배틀**: 1초 만에 최애에게 하트를 보내고 글로벌 팬들과 실시간 스탠스 토론.
- **글로벌 전광판/지하철 광고 펀딩 투표 연동**: K-Rank 1위 아티스트의 명동/타임스퀘어 팬덤 광고 펀딩 연동.

---

## 4. K-Score 6대 정량 지표 산출 알고리즘 (PoliRank 기반 확장)

$$\text{K-Score} = (0.30 \times S_{\text{음원}}) + (0.25 \times S_{\text{음반}}) + (0.20 \times S_{\text{영상}}) + (0.15 \times S_{\text{SNS}}) + (0.05 \times S_{\text{버즈}}) + (0.05 \times S_{\text{화력}})$$

| 지표명 | 가중치 | 데이터 출처 | 산출 방식 |
| :--- | :---: | :--- | :--- |
| **🎵 글로벌 음원 지수** | **30%** | Spotify Web API, Apple Music Chart | 일일/주간 글로벌 스트리밍 재생 수 정량화 |
| **💿 음반 판매 지수** | **25%** | Circle Chart (구 가온차트) API/Scraper | 주간/월간 앨범 초동 및 누적 판매량 정량화 |
| **📺 유튜브 영상 지수** | **20%** | YouTube Data API v3 | 공식 뮤직비디오 조회수, 좋아요, 댓글 수 |
| **📲 SNS 소셜 성장률** | **15%** | Instagram & X (Twitter) API | 주간 팔로워 증가량 및 언급 수 |
| **🔍 글로벌 검색 버즈** | **5%** | Google Trends API | 글로벌 구글/포털 검색 관심도 지수 |
| **🔥 팬덤 실시간 화력** | **5%** | K-Rank 플랫폼 자체 DB | 1클릭 실시간 하트 응원 수 |

---

## 5. 단계별 사업 & 개발 로드맵 (Roadmap)

### Phase 1: MVP 개발 (현 단계 - 1~2주 소요)
- **Top 32 주요 K-Pop 아티스트** 파일럿 데이터셋 구축 (`seed_data_krank.json`)
- FastAPI 백엔드 & TailwindCSS + Chart.js 프론트엔드 구축
- 6대 정량 지표 6축 레이더 차트 및 3D 아바타 카드 플립 구현
- SQLite 마스터 DB 및 1클릭 하트 응원 피드 연동

### Phase 2: 데이터 수집 자동화 & 확장 (2~4주 소요)
- Spotify API, YouTube API, Circle Chart 자동 ETL 파이프라인 구축 (`tools/krank_etl/`)
- GitHub Actions 주간 자동 데이터 동기화 워크플로우 적용
- 아티스트 라인업 100인 이상 확장

### Phase 3: 글로벌 바이럴 & 수익화 (1~2개월 소요)
- 영어/일어/한국어 다국어(i18n) 지원
- B2C 팬덤 광고 펀딩 투표권 시스템 및 역직구 굿즈 커머스 제휴 연동
