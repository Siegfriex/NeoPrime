# NeoPrime - 데이터 드리븐 예체능 입시 인텔리전스 플랫폼

**Version**: 3.1  
**Last Updated**: 2026-01-21  
**Status**: Frontend Complete / Backend In Progress

---

## 🎯 프로젝트 개요

NeoPrime은 예체능 입시 학원 원장의 20년 암묵지를 데이터로 증명하는 AI 엔진입니다.

### 핵심 가치
- 원장의 A~F 평가 × 20만 건 합격 데이터 = 숫자로 증명된 예측
- 감이 아닌 데이터로 합격 확률 제시
- 강사 평가 표준화 및 품질 관리

---

## 📁 프로젝트 구조

```
C:\Neoprime\
├── frontend/                    # 프론트엔드 (React + TypeScript)
│   └── neoprime/               # 웹 대시보드 (원장/강사용)
│       ├── components/         # 공통 컴포넌트 (4개)
│       ├── pages/              # 페이지 (11개)
│       ├── services/           # 비즈니스 로직 (3개)
│       └── package.json        # 의존성 관리
│
├── theory_engine/              # Theory Engine v3 (Python)
│   ├── formulas/               # 5단계 파이프라인
│   ├── formula_mining/         # 데이터 마이닝
│   └── tests/                  # 테스트 (9/9 통과)
│
├── docs/                       # 문서
│   ├── NeoPrime_PRD_Final.md              # PRD 기본 문서
│   ├── PRD_프론트엔드구현_업데이트_v3.1.md  # 프론트엔드 반영 업데이트
│   ├── Frontend_구현현황_v1.md            # 프론트엔드 상세 분석
│   ├── Frontend_IA_실제구현_v2.md         # IA (실제 구현 기준)
│   ├── NeoPrime_IA_서비스정보구조.md      # IA 기본 문서
│   ├── Theory_Engine_기능명세서_v3.0.md   # Theory Engine 명세
│   └── NeoPrime_기능명세서_v1.md          # 전체 기능 명세
│
├── ppt/                        # IR Deck
│   ├── neoprime/               # NeoPrime IR (B2B)
│   │   ├── index.html
│   │   ├── NeoPrime_IR_Deck_Content.md
│   │   └── WCAG_DESIGN_IMPROVEMENTS.md
│   └── designmate/             # DesignMate IR (B2C)
│       ├── index.html
│       └── WCAG_DESIGN_IMPROVEMENTS.md
│
└── README.md                   # 이 파일
```

---

## 🚀 빠른 시작

### Frontend (웹 대시보드)

```bash
cd frontend/neoprime
npm install
npm run dev
```

**URL**: http://localhost:5173

**환경 변수**: `.env.local` 생성 필요
```env
VITE_GEMINI_API_KEY=your_gemini_api_key_here
```

### Backend (Theory Engine)

```bash
pip install -r requirements.txt
python run_theory_engine.py
```

---

## 📊 구현 현황

### Frontend (100% ✅)
- ✅ 11개 페이지 구현 완료
- ✅ Gemini AI 완전 통합
- ✅ 6가지 고급 차트
- ✅ 빌드 성공 (51ms, 0 vulnerabilities)

**주요 페이지**:
1. Dashboard - 대시보드 (KPI, 리스크, 트렌드)
2. StudentList - 학생 목록 & 상대적 위치 분석
3. StudentDetail - 학생 상세 프로필
4. EvaluationEntry - AI 피드백 생성
5. Analytics - Analysis Lab (고급 분석)
6. AdmissionSimulator - 입시 시뮬레이터
7. Login/Signup - 인증
8. Settings/Profile - 설정

### Backend (진행 중 🟡)
- ✅ Theory Engine v3 (5단계 파이프라인)
- ✅ 226,695행 데이터 로드
- ✅ 9/9 테스트 통과
- ⏳ FastAPI 서버 구축 필요
- ⏳ GCP 배포 필요

---

## 🧪 기술 스택

### Frontend
- **Framework**: React 19.2.3
- **Language**: TypeScript 5.8.2
- **Build**: Vite 6.2.0
- **Router**: React Router v7.12.0
- **Charts**: Recharts 3.6.0
- **AI**: @google/genai 1.37.0
- **Icons**: Lucide React 0.562.0

### Backend
- **Language**: Python 3.11+
- **Framework**: FastAPI (예정)
- **DB**: PostgreSQL (예정)
- **ML**: Vertex AI (예정)
- **Engine**: Theory Engine v3 ✅

### Infrastructure
- **Cloud**: GCP
- **CI/CD**: GitHub Actions (예정)
- **Monitoring**: Cloud Logging (예정)

---

## 📖 주요 문서

### 비즈니스
- `NeoPrime_PRD_Final.md` - 전체 PRD (2,536줄)
- `PRD_프론트엔드구현_업데이트_v3.1.md` - 구현 상태 업데이트

### 기술
- `Theory_Engine_기능명세서_v3.0.md` - Theory Engine 상세
- `Frontend_구현현황_v1.md` - 프론트엔드 분석
- `Frontend_IA_실제구현_v2.md` - IA (실제 구현)

### IR Deck
- `ppt/neoprime/index.html` - NeoPrime IR Deck (B2B)
- `ppt/designmate/index.html` - DesignMate IR Deck (B2C)
- WCAG 2.1 AA 준수 (99%)

---

## 🎯 로드맵

### Q1 2026 (현재)
- ✅ Frontend 100% 완성
- ✅ Theory Engine v3 완성
- ⏳ Backend API 개발
- ⏳ GCP 배포

### Q2 2026
- ⏳ 네오캣 파일럿 (4개월)
- ⏳ Elite 파트너 10곳 확보
- ⏳ 월 매출 5억원 달성

### Q3-Q4 2026
- ⏳ Elite 15곳 + Standard 30곳
- ⏳ 월 매출 20억원
- ⏳ Series A 준비

---

## 👥 팀 (필요)

### 필수 (P0)
- CEO / PM: 에듀테크 창업 경험
- CTO: AI/ML 프로덕트 리드
- ML Lead: Vertex AI 경험

### 우선 (P1)
- Domain Expert: 미대입시 10년+

---

## 💰 투자 요청

- **시드 라운드**: 3~5억원
- **용도**: 팀 구성, 인프라, 마케팅
- **목표**: 6개월 내 Elite 10곳 확보

---

## 📞 Contact

- **GitHub**: https://github.com/Siegfriex/NeoPrime
- **Email**: TBD
- **Website**: TBD

---

**Copyright © 2026 NeoPrime. All rights reserved.**
