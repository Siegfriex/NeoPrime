# NeoPrime - 다음 단계 실행 가이드

**생성 날짜**: 2026-01-21  
**현재 상태**: Frontend 100% 완료 ✅ / Backend 연동 필요 ⏳

---

## 🎯 즉시 실행 (이번 주)

### 1. 프론트엔드 로컬 실행 테스트

```bash
cd C:\Neoprime\frontend\neoprime

# 환경 변수 설정
echo "VITE_GEMINI_API_KEY=your_api_key_here" > .env.local

# 개발 서버 실행
npm run dev

# 브라우저에서 확인
# http://localhost:5173
```

**확인 사항**:
- [ ] Dashboard 로딩 확인
- [ ] 학생 목록 Scatter Plot 확인
- [ ] AI 챗봇 작동 확인 (API 키 필요)
- [ ] 시뮬레이터 차트 확인

---

### 2. Backend 디렉토리 생성

```bash
cd C:\Neoprime

# Backend 디렉토리 생성
mkdir backend
cd backend

# FastAPI 프로젝트 초기화
mkdir api models routers schemas middleware

# 가상 환경 생성
python -m venv venv
venv\Scripts\activate

# 의존성 설치
pip install fastapi uvicorn sqlalchemy psycopg2-binary python-jose[cryptography] passlib[bcrypt] python-multipart
pip install python-dotenv pydantic-settings

# requirements.txt 생성
pip freeze > requirements.txt
```

---

### 3. Theory Engine API 래핑

**파일**: `backend/routers/prediction.py`

```python
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import sys
sys.path.append('../../theory_engine')  # Theory Engine 경로

from theory_engine.model import TheoryEngine

router = APIRouter(prefix="/api/prediction", tags=["prediction"])

class StudentData(BaseModel):
    korean: int
    math: int
    english: int
    social1: int
    social2: int
    target_university: str
    major: str

class AdmissionPrediction(BaseModel):
    probability: float
    line: str  # TOP/HIGH/MID/LOW
    similar_cases: list

@router.post("/admission", response_model=AdmissionPrediction)
async def predict_admission(data: StudentData):
    try:
        engine = TheoryEngine()
        # Theory Engine v3 호출
        result = engine.predict(
            korean=data.korean,
            math=data.math,
            # ... 나머지 매개변수
        )
        
        return {
            "probability": result['probability'],
            "line": result['line'],
            "similar_cases": result.get('cases', [])
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

---

### 4. Gemini AI API 래핑

**파일**: `backend/routers/ai.py`

```python
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import os
from google import genai

router = APIRouter(prefix="/api/ai", tags=["ai"])

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=GEMINI_API_KEY)

class FeedbackRequest(BaseModel):
    student_name: str
    scores: dict
    notes: str
    use_thinking: bool = False

@router.post("/feedback")
async def generate_feedback(req: FeedbackRequest):
    # geminiService.ts의 generateAIFeedback() 로직 Python으로 포팅
    prompt = f"""
    학생: {req.student_name}
    점수: {req.scores}
    노트: {req.notes}
    
    피드백을 생성하세요.
    """
    
    model = 'gemini-3-pro-preview' if req.use_thinking else 'gemini-3-flash-preview'
    
    response = client.models.generate_content(
        model=model,
        contents=prompt,
        config={
            'response_mime_type': 'application/json',
            'response_schema': {...}
        }
    )
    
    return response.json()
```

---

## 🗓️ 4주 개발 로드맵

### Week 1: Backend Core
- [x] 프론트엔드 통합 완료 ✅
- [ ] FastAPI 프로젝트 초기화
- [ ] PostgreSQL 스키마 설계
- [ ] SQLAlchemy 모델 정의
- [ ] Alembic 마이그레이션 설정
- [ ] Theory Engine API 래핑
- [ ] Gemini API 래핑

### Week 2: API 개발
- [ ] 인증 API (JWT)
- [ ] 학생 관리 API (CRUD)
- [ ] 평가 관리 API
- [ ] 합격 예측 API
- [ ] AI 피드백 API
- [ ] 챗봇 API (WebSocket or SSE)

### Week 3: Frontend-Backend 연동
- [ ] Axios/Fetch 클라이언트 작성
- [ ] API 호출 서비스 레이어
- [ ] 에러 핸들링 (try-catch, toast)
- [ ] 로딩 상태 (Skeleton, Spinner)
- [ ] Mock 데이터 제거
- [ ] E2E 테스트 (Playwright)

### Week 4: GCP 배포 & 파일럿
- [ ] Cloud Run (Frontend)
- [ ] Cloud Functions (Backend)
- [ ] Cloud SQL (PostgreSQL)
- [ ] Vertex AI 모델 훈련
- [ ] CI/CD (GitHub Actions)
- [ ] 네오캣 파일럿 시작

---

## 🧪 테스트 체크리스트

### Frontend 테스트
```bash
cd frontend/neoprime

# Unit Tests (Vitest)
npm install -D vitest @testing-library/react
npm run test

# E2E Tests (Playwright)
npm install -D @playwright/test
npx playwright test
```

**테스트 케이스**:
- [ ] Dashboard KPI 카드 렌더링
- [ ] StudentList Scatter Plot 생성
- [ ] AdmissionSimulator 계산 정확도
- [ ] EvaluationEntry AI 피드백 생성 (Mock)
- [ ] ChatBot 메시지 전송/수신

### Backend 테스트
```bash
cd backend

# pytest
pip install pytest pytest-asyncio httpx
pytest tests/
```

**테스트 케이스**:
- [ ] Theory Engine 호출 성공
- [ ] JWT 토큰 생성/검증
- [ ] PostgreSQL CRUD
- [ ] Gemini API 응답 파싱

---

## 💾 데이터베이스 스키마 (예시)

### PostgreSQL Tables

```sql
-- 학생 테이블
CREATE TABLE students (
    id UUID PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    grade VARCHAR(20),
    school VARCHAR(200),
    target_university VARCHAR(200),
    major VARCHAR(100),
    current_level VARCHAR(10),
    instructor_id UUID,
    avatar_url TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 평가 테이블
CREATE TABLE evaluations (
    id UUID PRIMARY KEY,
    student_id UUID REFERENCES students(id),
    date DATE NOT NULL,
    composition DECIMAL(3,1),
    tone DECIMAL(3,1),
    idea DECIMAL(3,1),
    completeness DECIMAL(3,1),
    total_score DECIMAL(5,2),
    notes TEXT,
    ai_feedback JSONB,
    instructor_id UUID,
    created_at TIMESTAMP DEFAULT NOW()
);

-- 사용자 테이블
CREATE TABLE users (
    id UUID PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    role VARCHAR(20), -- 'principal', 'instructor'
    academy_name VARCHAR(200),
    created_at TIMESTAMP DEFAULT NOW()
);

-- 합격 예측 캐시
CREATE TABLE admission_predictions (
    id UUID PRIMARY KEY,
    student_id UUID REFERENCES students(id),
    university VARCHAR(200),
    major VARCHAR(100),
    probability DECIMAL(5,2),
    line VARCHAR(20), -- TOP/HIGH/MID/LOW
    calculated_at TIMESTAMP DEFAULT NOW()
);
```

---

## 🔧 환경 변수 템플릿

### Frontend (`.env.local`)
```env
# Gemini API
VITE_GEMINI_API_KEY=your_gemini_api_key_here

# Backend URL
VITE_API_BASE_URL=http://localhost:8000

# Environment
VITE_ENV=development
```

### Backend (`.env`)
```env
# Database
DATABASE_URL=postgresql://postgres:password@localhost:5432/neoprime

# Gemini API
GEMINI_API_KEY=your_gemini_api_key_here

# JWT
JWT_SECRET=your_jwt_secret_key_here
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=10080

# GCP (Optional)
GCP_PROJECT_ID=neoprime-prod
GCP_REGION=asia-northeast3

# Theory Engine
THEORY_ENGINE_DATA_PATH=../theory_engine/data/
```

---

## 📞 연락처 & 리소스

### GitHub
- **Frontend Repo**: https://github.com/Siegfriex/NeoPrime
- **Local Monorepo**: C:\Neoprime

### 문서
- **PRD**: `NeoPrime_PRD_Final.md`
- **IA**: `docs/Frontend_IA_실제구현_v2.md`
- **구현 현황**: `docs/Frontend_구현현황_v1.md`
- **업데이트**: `docs/PRD_프론트엔드구현_업데이트_v3.1.md`

### 참조
- Gemini API Docs: https://ai.google.dev/gemini-api/docs
- FastAPI Docs: https://fastapi.tiangolo.com
- GCP Cloud Run: https://cloud.google.com/run/docs

---

**준비 완료! Backend 개발을 시작하세요.** 🚀
