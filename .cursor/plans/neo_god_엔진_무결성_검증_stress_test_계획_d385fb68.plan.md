---
name: NEO_GOD_엔진_무결성_검증_Stress_Test_계획
overview: 바이스 디렉터의 Stress-Test 프롬프트를 기반으로, 무작위 데이터 생성, 교차 검증, 디버깅 리포트를 포함한 통합 무결성 검증 시스템을 구축합니다.
todos:
  - id: create-synthetic-generator
    content: "test_synthetic_data_generator.py 작성: 5가지 시나리오별 가상 데이터 1,000건 생성기 구현"
    status: pending
  - id: create-cross-validation
    content: "test_cross_validation.py 작성: Excel 원본 vs BigQuery 이식 엔진 교차 검증 로직 구현"
    status: pending
  - id: create-formula-replicator
    content: "test_formula_replicator.py 작성: 핵심 수식 재현 로직 (적정점수 판정, COMPUTE 조회, RESTRICT 폴백) 구현"
    status: pending
  - id: create-debug-report
    content: "test_debug_report.py 작성: 디버깅 리포트 생성기 (테스트 요약, 오류 분류, 제언) 구현"
    status: pending
  - id: create-boundary-analyzer
    content: "test_boundary_analyzer.py 작성: 경계값 분석기 (부동 소수점 오차 검증) 구현"
    status: pending
  - id: create-exception-handler
    content: "test_exception_handler.py 작성: 예외 처리 검증기 (0/0, NULL, 타입 오류) 구현"
    status: pending
  - id: create-integration-stress
    content: "test_integration_stress.py 작성: 통합 테스트 실행기 (전체 파이프라인 오케스트레이션) 구현"
    status: pending
  - id: create-final-recommendations
    content: "stress_test_final_recommendations.md 템플릿 작성: 최종 제언 리포트 형식 정의"
    status: pending
isProject: false
---

# NEO GOD 엔진 무결성 검증 Stress-Test 계획

## 목표

바이스 디렉터의 전략적 품질 보증 프롬프트를 기반으로, 실제 데이터가 엔진을 통과했을 때 설계된 대로 결과가 나오는지를 검증하는 **무작위 시뮬레이션 테스트 시스템**을 구축합니다.

## 핵심 원칙

1. **블랙박스 테스팅**: 결과 비교 (Excel 원본 vs BigQuery 이식)
2. **화이트박스 테스팅**: 로직 검증 (수식 해석, 타입 변환, 경계값)
3. **Stress-Test**: 시스템 한계치 및 논리적 오류 식별
4. **교차 검증**: 오차 0.000001 이상 시 Logic Error 식별

## 구현 구조

### Phase 1: 가상 데이터 생성기 (Synthetic Data Generator)

**파일**: `test_synthetic_data_generator.py`

**기능**:

- 5가지 시나리오별 가상 학생 데이터 1,000건 생성
- Excel 호환 형식으로 저장
- 메타데이터 (시나리오 타입, 예상 결과) 포함

**시나리오별 생성 규칙**:

#### 시나리오 1: 만점자/최상위권

```python
{
    "원점수": 100.0,  # 모든 과목 만점
    "영어등급": 1,
    "국사등급": 1,
    "예상결과": "적정점수 이상"  # 모든 판정 통과
}
```

#### 시나리오 2: 경계선 (Boundary)

```python
{
    "원점수": 적정점수 ± 0.01,  # 정확히 컷라인
    "영어등급": 1-9,
    "국사등급": 1-9,
    "예상결과": "적정점수 이상" 또는 "예상점수 이상"  # 경계값 테스트
}
```

#### 시나리오 3: 결측치 (Null)

```python
{
    "원점수": None,  # 또는 ""
    "영어등급": None,  # 또는 0 또는 ""
    "국사등급": None,
    "예상결과": "오류(영어국사)" 또는 "제외(수탐)"
}
```

#### 시나리오 4: 데이터 오염 (Dirty)

```python
{
    "원점수": "100점",  # 문자열
    "영어등급": -1,  # 음수
    "국사등급": 10,  # 범위 초과
    "예상결과": 에러 처리 또는 타입 변환
}
```

#### 시나리오 5: 복합 가중치

```python
{
    "대학코드": "510gs0t20509",
    "수학가중치": 200,  # 극단적 높음
    "수학가중치": 0,  # 극단적 낮음
    "예상결과": 가중치 적용 후 점수 변화 확인
}
```

### Phase 2: 교차 검증 엔진 (Cross-Validation Engine)

**파일**: `test_cross_validation.py`

**기능**:

1. **Excel 원본 엔진 실행**

   - 생성된 가상 데이터를 원본 Excel 파일에 주입
   - OpenPyXL로 수식 계산 실행
   - 결과값 추출

2. **BigQuery 이식 엔진 실행**

   - Phase 1-3 파이프라인 실행
   - BigQuery SQL로 수식 재현 (또는 Python으로 수식 계산)
   - 결과값 추출

3. **오차 분석**

   - 두 결과값 비교
   - 오차 > 0.000001 시 Logic Error 식별
   - 부동 소수점 오차 vs 로직 오류 구분

**핵심 수식 재현**:

#### 적정점수 판정 로직 (SQL)

```sql
CASE
    WHEN 영어등급 IS NULL OR 영어등급 = 0 OR 영어등급 > 9 
         OR 국사등급 IS NULL OR 국사등급 = 0 OR 국사등급 > 9
    THEN '오류(영어국사)'
    WHEN 현재점수 >= 적정점수 THEN '적정점수 이상'
    WHEN 현재점수 >= 예상점수 THEN '예상점수 이상'
    WHEN 현재점수 >= 소신점수 THEN '소신점수 이상'
    ELSE '소신점수 미만'
END
```

#### COMPUTE 시트 조회 (Python)

```python
def lookup_compute(row_header: str, col_header: str, compute_df: pd.DataFrame) -> float:
    """COMPUTE 시트 INDEX/MATCH 재현"""
    row_idx = compute_df[compute_df['B'] == row_header].index[0]
    col_idx = compute_df.columns.get_loc(col_header)
    return compute_df.iloc[row_idx, col_idx]
```

### Phase 3: 디버깅 리포트 생성기 (Debug Report Generator)

**파일**: `test_debug_report.py`

**출력 형식**:

#### 테스트 요약

```json
{
    "test_summary": {
        "total_cases": 1000,
        "scenario_1": {"total": 200, "passed": 198, "failed": 2, "pass_rate": 0.99},
        "scenario_2": {"total": 200, "passed": 195, "failed": 5, "pass_rate": 0.975},
        "scenario_3": {"total": 200, "passed": 200, "failed": 0, "pass_rate": 1.0},
        "scenario_4": {"total": 200, "passed": 180, "failed": 20, "pass_rate": 0.9},
        "scenario_5": {"total": 200, "passed": 190, "failed": 10, "pass_rate": 0.95},
        "overall_pass_rate": 0.963,
        "total_errors": 37
    }
}
```

#### 디버그 로그

```json
{
    "errors": [
        {
            "error_id": "ERR_001",
            "scenario": 2,
            "test_case_id": 145,
            "location": {
                "sheet": "이과계열분석결과",
                "column": "col_3",
                "row": 145,
                "formula_pattern": "conditional"
            },
            "input_values": {
                "G6": 85.0,
                "J6": 85.0,
                "K6": 80.0,
                "L6": 75.0
            },
            "expected_result": "적정점수 이상",
            "actual_result_excel": "적정점수 이상",
            "actual_result_bq": "예상점수 이상",
            "difference": 0.0,
            "error_type": "Logic Branch Fail",
            "root_cause": "부동 소수점 오차로 인한 경계값 판정 오류",
            "suggested_fix": "ROUND() 함수 적용 또는 >= 대신 > 사용"
        }
    ]
}
```

#### 오류 분류

- **Precision Loss**: 소수점 8자리 이하 불일치
- **Logic Branch Fail**: IF 중첩 구조 조건 누락
- **Mapping Error**: COMPUTE 시트 조회 실패
- **Type Mismatch**: 데이터 타입 불일치
- **Performance Lag**: 응답 속도 저하

### Phase 4: 통합 테스트 실행기 (Integration Test Runner)

**파일**: `test_integration_stress.py`

**실행 흐름**:

1. 가상 데이터 생성 (1,000건)
2. Excel 원본 엔진 실행
3. BigQuery 이식 엔진 실행
4. 교차 검증
5. 디버깅 리포트 생성
6. 최종 제언 리포트 생성

**성능 지표 측정**:

- 실행 시간 (각 Phase별)
- 메모리 사용량
- 오류 발생률
- 처리 속도 (행/초)

## 주요 테스트 시나리오 상세

### A. 경계값 분석 (Boundary Value Analysis)

**검증 대상**: `$G_6 \geq J_6` 등 판정 로직

**테스트 케이스**:

- `G6 = J6 - 0.000001` → "예상점수 이상" 기대
- `G6 = J6` → "적정점수 이상" 기대
- `G6 = J6 + 0.000001` → "적정점수 이상" 기대

**식별 리스크**: 부동 소수점 오차로 인한 합격권 점수가 불합격으로 처리

**대응 전략**: ROUND() 함수 위치 재조정 또는 경계값 ±0.01 범위 허용

### B. 논리적 예외 처리 (Exception Handling)

**검증 대상**: 의도적 에러 생성 로직 (`0/0`)

**테스트 케이스**:

- 조건 불만족 시 `0/0` 생성
- Excel: `#DIV/0!` 에러
- BigQuery: NULL 또는 에러 처리 확인

**식별 리스크**: 시스템이 에러를 뱉지 않고 억지로 계산하여 잘못된 숫자 산출

**대응 전략**: CASE WHEN 구문의 ELSE 처리 강화, NULL 명시적 처리

### C. 데이터 타입 유연성 (Type Flexibility)

**검증 대상**: 문자열 강제 숫자 변환 (`*1`)

**테스트 케이스**:

- `"100"` → `100.0` 변환 확인
- `"100점"` → 에러 처리 또는 숫자 추출
- `NULL` → NULL 유지

**식별 리스크**: BigQuery SQL에서 문자열 "100"과 숫자 100의 비교 연산 시 성능 저하

**대응 전략**: Phase 3에서 타입 명시적 변환, CAST() 함수 적용

### D. COMPUTE 시트 매핑 검증

**검증 대상**: INDEX/MATCH 조회 로직

**테스트 케이스**:

- 존재하는 대학 코드 조회
- 존재하지 않는 대학 코드 조회 (IFERROR 처리 확인)
- 행 헤더 불일치 케이스

**식별 리스크**: 대학 코드는 같으나 지표명이 달라 조회 실패

**대응 전략**: COMPUTE 시트의 INDEX/MATCH 키값 정규화, 대소문자 통일

### E. RESTRICT 시트 폴백 검증

**검증 대상**: 3단계 VLOOKUP 폴백 메커니즘

**테스트 케이스**:

- 영역 1 ($A:$C) 매칭 성공
- 영역 1 실패 → 영역 2 ($E:$G) 매칭 성공
- 영역 2 실패 → 영역 3 ($I:$L) 매칭 성공
- 모든 영역 실패 → 점수 비교 로직 동작

**식별 리스크**: 폴백 메커니즘이 정상 동작하지 않아 잘못된 판정

**대응 전략**: 각 폴백 단계별 로그 추가, 실패 케이스 추적

## 디버그 체크리스트

| 체크 항목 | 식별 방법 | 대응 전략 |

|----------|----------|----------|

| **Precision Loss** | 소수점 8자리 이하 불일치 | ROUND() 함수 위치 재조정 |

| **Logic Branch Fail** | IF 중첩 구조 조건 누락 | CASE WHEN 구문의 ELSE 처리 강화 |

| **Mapping Error** | 대학 코드는 같으나 지표명 불일치 | COMPUTE 시트 키값 정규화 |

| **Performance Lag** | 무작위 대량 쿼리 시 응답 속도 저하 | INDEX 컬럼 파티셔닝 및 클러스터링 |

| **Type Mismatch** | 문자열/숫자 타입 불일치 | Phase 3 타입 명시적 변환 |

| **Null Handling** | NULL 처리 불일치 | NULL 명시적 처리, COALESCE() 적용 |

## 최종 제언 리포트 형식

**파일**: `stress_test_final_recommendations.md`

**구조**:

1. **엔진 신뢰도 평가**

   - 현재 신뢰도: 85% → 목표: 99.9%
   - 발견된 취약점 요약

2. **로직 수정 제안**

   - Critical 수정 사항 (즉시 적용)
   - High 수정 사항 (단기 적용)
   - Medium 수정 사항 (중기 적용)

3. **성능 최적화 제안**

   - 병목 지점 분석
   - 최적화 방안

4. **모니터링 제안**

   - 프로덕션 환경 모니터링 지표
   - 알림 임계값 설정

## 구현 파일 목록

1. `test_synthetic_data_generator.py` - 가상 데이터 생성기
2. `test_cross_validation.py` - 교차 검증 엔진
3. `test_debug_report.py` - 디버깅 리포트 생성기
4. `test_integration_stress.py` - 통합 테스트 실행기
5. `test_formula_replicator.py` - 수식 재현 로직 (Excel → SQL/Python)
6. `test_boundary_analyzer.py` - 경계값 분석기
7. `test_exception_handler.py` - 예외 처리 검증기
8. `stress_test_final_recommendations.md` - 최종 제언 리포트

## 실행 방법

```bash
# 전체 Stress-Test 실행
python test_integration_stress.py --scenarios 1,2,3,4,5 --cases 1000 --output stress_test_report.json

# 특정 시나리오만 실행
python test_integration_stress.py --scenario 2 --cases 200 --output scenario_2_report.json

# 디버그 모드 실행
python test_integration_stress.py --scenarios 1,2,3,4,5 --cases 1000 --debug --verbose
```

## 검증 완료 기준

- ✅ 모든 시나리오 실행 완료
- ✅ 통과율 > 99% (목표: 99.9%)
- ✅ Critical 오류 0개
- ✅ High 오류 < 5개
- ✅ 성능 목표 달성 (전체 실행 시간 < 300초)
- ✅ 디버깅 리포트 생성 완료
- ✅ 최종 제언 리포트 생성 완료

## 참고 문서

- [NEO_GOD_엔진_상세_명세서.md](y:\0126\0126\NEO_GOD_엔진_상세_명세서.md)
- [전방위_검증_테스트_프롬프트.md](y:\0126\0126\전방위_검증_테스트_프롬프트.md)
- [output/formula_analysis_report.json](y:\0126\0126\output\formula_analysis_report.json)