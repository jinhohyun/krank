# K-Rank (케이랭크) 🏆
> **100% 팩트 데이터 기반 글로벌 K-Pop 정량 랭킹 & 팬덤 인터랙티브 MVP 플랫폼**

![K-Rank MVP](https://img.shields.io/badge/Version-v1.0%20MVP-pink?style=flat-square)
![Status](https://img.shields.io/badge/Status-Fully%20Tested%20%26%20Functional-emerald?style=flat-square)
![Stack](https://img.shields.io/badge/Backend-FastAPI%20%7C%20SQLite-black?style=flat-square)
![Frontend](https://img.shields.io/badge/Frontend-TailwindCSS%20%7C%20Chart.js%20(6--Axis%20Radar)-purple?style=flat-square)

---

## 1. 개요 (Overview)
**K-Rank**는 주관적 감정이나 부정 투표 없이 **글로벌 Spotify 스트리밍, Circle Chart 음반 판매량, YouTube 조회수, SNS 팔로워 성장률, 구글 검색 버즈, 실시간 팬덤 화력** 6대 팩트 데이터를 가중합한 **K-Score (100점 만점)** 정량 랭킹 플랫폼입니다.

---

## 2. 주요 제공 기능 (Key Features)

1. **🏆 글로벌 Top 3 포디엄 리더보드**: K-Score 상위 3팀 황금/은/동 뱃지 하이라이트
2. **📊 6대 정량 지표 6축 레이더 차트**: Chart.js 기반 6차원 지표 정밀 시각화 모달
3. **🖼️ 3D 카드 플립 애니메이션**: 2D 캐리커쳐 아바타 ↔ 고화질 공식 사진 간 3D 회전 전환
4. **💖 실시간 1클릭 하트 응원 & 파티클**: 클릭 시 통통 튀는 플로팅 하트 파티클 및 DB 실시간 연동
5. **💬 팬덤 한줄 토론 피드**: 아티스트별 실시간 응원/입덕/화력지원 한줄 소통 피드

---

## 3. 실행 방법 (Run Guide)

### 1) 서버 실행
```bash
python3 run.py
```
- **웹 서비스 접속**: `http://localhost:8000`
- **FastAPI 대화형 API 문서**: `http://localhost:8000/docs`

### 2) 통합 테스트 실행
```bash
python3 test_krank.py
```
> 결과: `Ran 3 tests in 0.037s / OK` (100% 통과)
