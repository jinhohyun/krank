# 🛠️ K-Rank (케이랭크) 개발 로드맵 및 단계별 구현 가이드 (Step-by-Step Build)

> **프로젝트명:** K-Rank MVP 빌드  
> **담당 에이전트:** 풀스택 수석 개발자 서브 에이전트 (`fullstack_dev`)  
> **문서 버전:** v1.0.0  
> **작성일:** 2026-11-11  
> **저장 경로:** `01_Biz_Projects/krank/K_Rank_개발_로드맵_및_단계별_구현_가이드.md`  

---

## 🎯 개발 진행 원칙 (Full-Stack Dev Guidelines)
1. **Antigravity 대체 자율 수행**: `write_file`, `patch`, `read_file`, `terminal` 도구를 활용하여 풀스택 개발자 에이전트가 직접 개발 및 검증을 완수합니다.
2. **단계별 점진적 개발 (Step-by-Step)**: 한 번에 거대 코드를 작성하지 않고, **4개의 명확한 단계**로 잘게 나누어 한 단계씩 개발 및 실행 테스트를 진행합니다.
3. **디스코드 `#개발실` 실시간 공유**: 단계별 개발 완료 및 테스트 결과를 디스코드 `#개발실` 채널에 보고합니다.

---

## 📑 4단계 개발 세부 작업 분할 (WBS)

### 📌 Step 1: 프로젝트 디렉터리 & 스캐폴딩 및 데이터베이스 구축
- **작업 내용**:
  - `01_Biz_Projects/krank_mvp/` 디렉터리 및 필요 정적 폴더(`static/`) 생성
  - Top 32 K-Pop 아티스트 시드 데이터 파일 (`seed_data.json`) 생성 (BTS, 블랙핑크, 뉴진스, 스트레이키즈, 세븐틴, 에스파, 아이브, 트와이스 등)
  - `database.py`: SQLite `artists`, `cheer_logs`, `fan_discussions` 스키마 작성 및 DB 초기화 스크립트 작성
- **검증**: `python3 database.py` 실행 ➔ DB 테이블 생성 및 시드 데이터 시딩 정상 완료 검증

---

### 📌 Step 2: K-Score 6대 지표 산출 엔진 및 FastAPI 서버 구축
- **작업 내용**:
  - `scoring.py`: 6대 정량 지표 가중합 산출 알고리즘 및 S+ ~ C 등급 티어 매핑 함수 개발
  - `app.py`: FastAPI 메인 애플리케이션 및 RESTful API 엔드포인트 구현
    - `GET /api/artists`: 랭킹 순 정렬 조회
    - `POST /api/artists/{id}/cheer`: 실시간 하트 증가
    - `GET/POST /api/artists/{id}/discussions`: 한줄 토론 피드
  - `run.py`: Uvicorn 서버 실행기 작성
- **검증**: `python3 -m unittest` 또는 API 호출 테스트 ➔ HTTP 200 정상 응답 검증

---

### 📌 Step 3: 바이럴 프론트엔드 UI 구축 (TailwindCSS + Chart.js)
- **작업 내용**:
  - `static/index.html`: 반응형 헤더, K-Rank 상위 아티스트 포디엄(Podium 1, 2, 3위), 랭킹 카드 리스트, 실시간 하트 배틀 피드
  - `static/app.js`: 
    - Chart.js 기반 6축 K-Score 레이더 차트 수치 시각화
    - 3D 회전 카드 플립 (아바타 ↔ 국회/공식 고화질 사진)
    - 1클릭 하트 클릭 시 플로팅 파티클 애니메이션 및 DB 실시간 연동
- **검증**: 웹 브라우저 렌더링 및 UI 인터랙션 검증

---

### 📌 Step 4: 종합 통합 테스트 및 서버 구동 검증
- **작업 내용**:
  - `test_krank.py`: API 통합 테스트 스크립트 작성 및 실행
  - 포트 8000번 가동 테스트 및 README.md 개발 가이드 작성
- **검증**: 전체 단위/통합 테스트 100% 통과 확인 및 개발 완료 보고

---

🚀 **문서 작성 완료! 진호님의 지시에 따라 Step 1부터 순차적으로 풀스택 개발을 시작합니다.**
