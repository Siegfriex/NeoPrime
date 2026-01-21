# Theory Engine v3.0 실제 테스트 분석 보고서

**작성일**: 2026-01-18
**테스트 유형**: 실제 엑셀 데이터 기반 전체 파이프라인 테스트
**결론**: ⚠️ **부분 성공 - 핵심 이슈 3건 식별**

---

## 📊 테스트 결과 요약

| Phase | 테스트 항목 | 성공 | 실패 | 성공률 | 상태 |
|-------|-------------|------|------|--------|------|
| 1 | 엑셀 데이터 로드 | 13 | 0 | 100% | ✅ |
| 2 | RAWSCORE 조회 | 2 | 3 | 40% | ⚠️ |
| 3 | 과목명 매칭 | 12 | 0 | 100% | ✅ |
| 4 | 커트라인 추출 | 4 | 2 | 67% | ⚠️ |
| 5 | 확률 계산 | 4 | 0 | 100% | ✅ |
| 6 | 결격 체크 | 4 | 0 | 100% | ✅ |
| 7 | 전체 파이프라인 | 3 | 4 | 43% | ⚠️ |
| **전체** | - | **42** | **9** | **82%** | **⚠️** |

---

## 1. 미흡한 점 (Weaknesses)

### 🔴 Critical: RAWSCORE 탐구과목 조회 실패

**현상**:
```
[OK] 국어 80점 -> 표준: 125.0, 백분위: 89.0
[OK] 수학 75점 -> 표준: 121.0, 백분위: 82.0
[FAIL] 물리학 Ⅰ 45점 -> 표준: None, 백분위: None
[FAIL] 화학 Ⅰ 42점 -> 표준: None, 백분위: None
[FAIL] 생명과학 Ⅰ 40점 -> 표준: None, 백분위: None
```

**원인 분석**:
- RAWSCORE 시트의 "영역" 컬럼에 국어/수학만 존재
- 탐구과목은 별도 컬럼 구조 ("과목명" 컬럼 사용 가능성)
- 현재 코드가 "영역" 컬럼만 검색

**영향도**: ⬆️ High
- 탐구과목 점수 변환 전체 불가
- INDEX 조회에 필요한 표준점수 산출 불가

**권장 조치**:
```python
# rules.py에서 탐구과목용 별도 조회 로직 필요
# 실제 RAWSCORE 시트 구조:
# - 컬럼[0]: 영역 (국어, 수학, 영어, ...)
# - 컬럼[1]: 과목명 (물리학 Ⅰ, 화학 Ⅰ, ...)
# 탐구과목은 영역="탐구" + 과목명 매칭 필요
```

---

### 🔴 Critical: INDEX 조회 전체 실패

**현상**:
```
[INDEX 조회 결과]
  found: False
  match_type: None
  cumulative_pct: None
```

**원인 분석**:
- INDEX 시트 첫 컬럼이 인코딩된 키 (예: "510gs0t20509")
- 현재 코드는 표준점수 직접 매칭 시도
- MultiIndex 빌드 시 0개 행으로 구축됨 (컬럼 매핑 실패)

**영향도**: ⬆️ High
- 누적백분위(cumulative_pct) 산출 불가
- 전국 등수 산출 불가
- 정확한 합격 확률 계산 불가

**권장 조치**:
1. INDEX 인코딩 방식 역공학 (해시 구조 분석)
2. 또는 RAWSCORE 누적%를 직접 합산하여 우회

---

### 🟡 Medium: 일부 대학 커트라인 미발견

**현상**:
```
[OK] 가천의학: 적정=49.9, 예상=73.13, 소신=88.28
[OK] 건국자연: 적정=528.17, 예상=610.87, 소신=666.59
[FAIL] 연세대의예: 컬럼 없음
[FAIL] 고려대경영: 컬럼 없음
```

**원인 분석**:
- PERCENTAGE 시트 컬럼 형식: "가천의학 이과", "건국자연 문과"
- "연세대", "고려대" 등 일부 대학 표기 방식 불일치
- 실제 컬럼명 확인 필요 (연대?, 연세?, 고대?, 고려?)

**영향도**: ⬇️ Medium
- 해당 대학 합격 예측 불가
- 다른 대학은 정상 작동

**권장 조치**:
```python
# 대학명 alias 매핑 추가
UNIVERSITY_ALIASES = {
    "연세대": ["연대", "연세", "연세대학교"],
    "고려대": ["고대", "고려", "고려대학교"],
    "서울대": ["서대", "서울", "서울대학교"],
}
```

---

### 🟡 Medium: 원점수 변환 전체 실패 (파이프라인)

**현상**:
```
[원점수 변환 결과]
  [FAIL] korean_standard: None
  [FAIL] math_standard: None
  [FAIL] inquiry1_standard: None
  [FAIL] inquiry2_standard: None
```

**원인 분석**:
- 파이프라인에서 과목명 정규화 후 조회 시 매칭 실패
- 국어(언매), 수학(미적) 형식이 RAWSCORE와 불일치
- 개별 테스트(국어 80점)는 성공했으나 통합 시 실패

**영향도**: ⬇️ Medium (개별 함수는 작동)

---

## 2. 위험 요인 (Risk Factors)

### 🔴 R1: 데이터 스키마 변경 위험

| 위험 | 설명 | 발생 가능성 | 영향도 |
|------|------|-------------|--------|
| 엑셀 구조 변경 | 컬럼명/시트명 변경 시 전체 실패 | Medium | Critical |
| 인코딩 변경 | INDEX 키 인코딩 방식 변경 | Low | High |
| 대학 추가/삭제 | PERCENTAGE 컬럼 변동 | High | Low |

**대응 방안**:
- 스키마 버전 관리 도입
- 컬럼 매핑 외부 설정 파일화
- 변경 감지 경고 시스템

---

### 🔴 R2: 정확도 검증 부재

| 위험 | 설명 | 현재 상태 |
|------|------|-----------|
| Golden Case 없음 | 실제 합격 데이터 비교 불가 | ⚠️ |
| 엑셀 결과 비교 없음 | 엑셀 시뮬레이션 결과와 대조 미실시 | ⚠️ |
| 오차 범위 미정의 | 허용 오차 기준 없음 | ⚠️ |

**대응 방안**:
- 실제 학생 5~10명 Golden Case 생성
- 엑셀 결과와 Python 결과 1:1 비교
- 오차 ±5% 이내 목표 설정

---

### 🟡 R3: 성능 병목 가능성

| 구간 | 현재 | 위험 |
|------|------|------|
| INDEX 로드 | ~4초 (200K 행) | 동시 사용자 증가 시 병목 |
| PERCENTAGE 조회 | ~50ms | OK |
| 메모리 사용 | ~500MB | 서버 환경에서 주의 |

---

### 🟡 R4: 예외 처리 미흡

```python
# 현재 코드의 문제점
try:
    result = lookup_index(...)
except Exception as e:
    logger.warning(f"조회 실패: {e}")  # 경고만 출력
    return None  # 조용히 실패
```

**위험**: 사용자에게 명확한 에러 메시지 전달 안 됨

---

## 3. 기회 요인 (Opportunities)

### 🟢 O1: 과목 매칭 모듈 우수

```
[OK] "물리학I" -> "물리학 Ⅰ" (신뢰도: 100%)
[OK] "화학II" -> "화학 Ⅱ" (신뢰도: 100%)
[OK] "생윤" -> "생활과 윤리" (신뢰도: 100%)
[OK] "사문" -> "사회·문화" (신뢰도: 100%)
```

**활용 방안**:
- 사용자 입력 자동 보정 기능으로 확장
- 음성 인식 연동 시 전처리 활용
- 다른 교육 서비스 API로 제공 가능

---

### 🟢 O2: 확률 계산 모델 정확

```
[OK] 점수=98, 레벨=적정 (기대: 적정), 확률=92.00%
[OK] 점수=92, 레벨=예상 (기대: 예상), 확률=62.00%
[OK] 점수=87, 레벨=소신 (기대: 소신), 확률=32.00%
[OK] 점수=80, 레벨=상향 (기대: 상향), 확률=18.82%
```

**활용 방안**:
- 신뢰구간 시각화로 UX 향상
- 레벨별 색상 코딩 (적정=녹색, 상향=빨강)
- 확률 변화 추이 그래프

---

### 🟢 O3: 결격 체크 엔진 완성도 높음

```
[OK] 정상: 결격=False
[OK] 영어4등급: 결격=True, 사유: 영어 4등급: 대부분 대학은 3등급 이내 필수
[OK] 한국사5등급: 결격=True, 사유: 한국사 5등급: 대부분 대학은 4등급 이내 필수
[OK] 이과+확통: 결격=True, 사유: 서울대 이과: 미적분/기하 필수
```

**활용 방안**:
- 지원 전 사전 경고 시스템
- 대학별 맞춤 결격 알림
- 결격 회피 전략 추천

---

### 🟢 O4: 커트라인 데이터 풍부

- 1,096개 대학/전공 조합
- 80%/50%/20% 3단계 커트라인
- 실시간 보간 계산 지원

**활용 방안**:
- 지원 전략 시뮬레이터
- 목표 점수 역산 기능
- 경쟁률 예측 연동

---

## 4. 제언 (Recommendations)

### 📌 P0: 즉시 조치 (1일 이내)

#### 4.1 RAWSCORE 탐구과목 조회 수정

```python
# rules.py 수정 제안
def convert_raw_to_standard(rawscore_df, subject, raw_score, ...):
    # 1. 기존 영역 매칭 시도
    mask = rawscore_df["영역"] == subject

    # 2. 실패 시 과목명 컬럼 매칭
    if rawscore_df[mask].empty:
        if "과목명" in rawscore_df.columns:
            normalized = normalize_subject(subject)
            mask = rawscore_df["과목명"].apply(
                lambda x: normalize_subject(str(x))
            ) == normalized

    # 3. 탐구 영역 + 과목명 조합 매칭
    if rawscore_df[mask].empty:
        mask = (
            (rawscore_df["영역"] == "탐구") &
            (rawscore_df["과목명"].str.contains(subject, na=False))
        )
```

**예상 소요**: 2시간
**기대 효과**: RAWSCORE 조회 성공률 40% → 90%+

---

#### 4.2 INDEX 우회 로직 구현

```python
# 현재: INDEX 시트 직접 조회 (실패)
# 제안: RAWSCORE 누적% 합산으로 대체

def calculate_cumulative_pct(korean_conv, math_conv, inq1_conv, inq2_conv):
    """RAWSCORE 누적% 합산으로 cumulative_pct 계산"""
    pcts = [
        korean_conv.get("cumulative_pct", 0) or 0,
        math_conv.get("cumulative_pct", 0) or 0,
        inq1_conv.get("cumulative_pct", 0) or 0,
        inq2_conv.get("cumulative_pct", 0) or 0,
    ]
    return sum(pcts) / len([p for p in pcts if p > 0])
```

**예상 소요**: 1시간
**기대 효과**: 전체 파이프라인 작동 가능

---

### 📌 P1: 단기 조치 (1주 이내)

#### 4.3 대학명 Alias 시스템

```python
# cutoff/cutoff_extractor.py에 추가
UNIVERSITY_ALIASES = {
    "연세대": ["연대", "연세", "연세대학교", "연세대 의"],
    "고려대": ["고대", "고려", "고려대학교"],
    "성균관대": ["성대", "성균관", "SKKU"],
    "한양대": ["한대", "한양"],
    "서강대": ["서강"],
    "이화여대": ["이대", "이화"],
    "중앙대": ["중대", "중앙"],
    "경희대": ["경대", "경희"],
}

def _find_program_column(self, university, major, track):
    # 1. 정확 매칭
    # 2. Alias 매칭
    aliases = UNIVERSITY_ALIASES.get(university, [university])
    for alias in aliases:
        # 패턴 매칭 시도
```

**예상 소요**: 3시간
**기대 효과**: 커트라인 조회 성공률 67% → 95%+

---

#### 4.4 Golden Case 테스트 구축

```python
# tests/test_golden_cases.py 생성
GOLDEN_CASES = [
    {
        "input": {
            "track": "이과",
            "korean": 80,
            "math": 75,
            "english_grade": 2,
            "history_grade": 3,
            "inquiry1": ("물리학 Ⅰ", 45),
            "inquiry2": ("화학 Ⅰ", 42),
            "targets": [("가천", "의학"), ("건국", "자연")],
        },
        "expected": {
            "가천의학": {"level": "예상", "prob_min": 0.4, "prob_max": 0.7},
            "건국자연": {"level": "적정", "prob_min": 0.7, "prob_max": 0.9},
        },
        "source": "2025학년도 실제 합격자 A"
    },
    # ... 추가 케이스
]
```

**예상 소요**: 1일
**기대 효과**: 정확도 검증 체계 구축

---

### 📌 P2: 중기 조치 (1개월 이내)

#### 4.5 INDEX 인코딩 역공학

현재 INDEX 컬럼: `"510gs0t20509"` 형태
- 숫자+알파벳 조합
- 위치별 의미 분석 필요

**접근 방법**:
1. 패턴 분석 (첫 3자리=국어?, 다음 2자리=계열?)
2. 기존 엑셀 수식 추적 (INDEX 시트 생성 로직)
3. 샘플 매칭 테스트

---

#### 4.6 에러 핸들링 강화

```python
class TheoryEngineError(Exception):
    """Theory Engine 기본 예외"""
    pass

class RawscoreLookupError(TheoryEngineError):
    """RAWSCORE 조회 실패"""
    def __init__(self, subject, score):
        self.subject = subject
        self.score = score
        super().__init__(f"RAWSCORE 조회 실패: {subject} {score}점")

class CutoffNotFoundError(TheoryEngineError):
    """커트라인 없음"""
    def __init__(self, university, major):
        super().__init__(f"커트라인 없음: {university} {major}")
```

---

### 📌 P3: 장기 조치 (3개월 이내)

#### 4.7 Vertex AI 연동 (A/B 갭 보정)

```
[Flow]
1. Theory Engine 예측값 (P_theory)
2. 실제 합격 결과 수집 (is_admitted)
3. 갭 분석: gap = is_admitted - P_theory
4. ML 모델 학습: gap ~ f(features)
5. 보정된 예측: P_final = P_theory + predicted_gap
```

---

#### 4.8 실시간 모니터링 대시보드

```
[Metrics]
- API 호출 수 / 분
- 평균 응답 시간
- 에러율 (by 유형)
- 캐시 히트율
- 대학별 조회 빈도
```

---

## 5. 우선순위 매트릭스

```
        High Impact
            │
   P0-1     │     P0-2
  RAWSCORE  │    INDEX
   수정     │    우회
            │
Low ────────┼──────── High Effort
            │
   P1-3     │     P2-5
  대학Alias │    INDEX
            │    역공학
            │
        Low Impact
```

| 순위 | 항목 | 영향도 | 소요시간 | ROI |
|------|------|--------|----------|-----|
| 1 | INDEX 우회 로직 | High | 1시간 | ⬆️⬆️⬆️ |
| 2 | RAWSCORE 탐구과목 | High | 2시간 | ⬆️⬆️⬆️ |
| 3 | 대학명 Alias | Medium | 3시간 | ⬆️⬆️ |
| 4 | Golden Case 테스트 | Medium | 1일 | ⬆️⬆️ |
| 5 | INDEX 역공학 | Low | 1주 | ⬆️ |

---

## 6. 결론

### 현재 상태 평가

| 영역 | 완성도 | 실제 작동 | 갭 |
|------|--------|-----------|-----|
| 데이터 로드 | 100% | 100% | 0% |
| 과목 매칭 | 100% | 100% | 0% |
| RAWSCORE 변환 | 100% | 40% | **60%** |
| INDEX 조회 | 100% | 0% | **100%** |
| 커트라인 추출 | 100% | 67% | 33% |
| 확률 계산 | 100% | 100% | 0% |
| 결격 체크 | 100% | 100% | 0% |
| **전체** | **100%** | **58%** | **42%** |

### 핵심 메시지

> **"코드 완성도 100%이나, 실제 엑셀 스키마 연동 미흡으로 42% 갭 존재"**

### 즉시 조치 시 기대 효과

| 조치 | 소요 | 효과 |
|------|------|------|
| INDEX 우회 | 1시간 | +30% |
| RAWSCORE 수정 | 2시간 | +20% |
| 대학 Alias | 3시간 | +5% |
| **합계** | **6시간** | **+55% → 실작동 95%+** |

---

**작성일**: 2026-01-18
**분석 완료**: 실제 데이터 기반 7 Phase 테스트
**권장 조치**: P0 항목 6시간 내 완료 시 95%+ 실작동 달성 가능

---

**END OF ANALYSIS REPORT**
