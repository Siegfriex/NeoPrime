---
name: NEO_GOD_비즈니스_로직_검증_및_프로덕션_준비_플랜
overview: 비즈니스 로직 검증, Excel vs BigQuery 교차 검증, BigQuery 실제 적재 테스트, 실제 파일 E2E 테스트를 포함한 프로덕션 배포 전 필수 검증 작업을 수행합니다.
todos:
  - id: create-formula-logic-test
    content: "test_formula_logic.py 개발: 적정점수 판정 로직, COMPUTE/RESTRICT 조회 로직, 평균 점수 계산 로직 검증"
    status: pending
  - id: create-cross-validation-test
    content: "test_excel_bigquery_cross_validation.py 개발: Excel 수식 계산 vs BigQuery SQL 변환 결과 비교"
    status: pending
  - id: create-bigquery-load-test
    content: "test_bigquery_actual_load.py 개발: BigQuery 실제 연결 및 소규모 데이터 적재 테스트"
    status: pending
  - id: create-e2e-test
    content: "test_e2e_real_file.py 개발: 실제 Excel 파일(225,420행)로 전체 파이프라인 실행 및 검증"
    status: pending
  - id: create-calamine-performance-test
    content: "test_calamine_performance.py 개발: Calamine 엔진 설치 및 성능 비교 테스트"
    status: pending
  - id: create-boundary-precision-test
    content: "test_boundary_precision.py 개발: 경계값 부동소수점 오차 테스트 (Excel vs Python vs BigQuery)"
    status: pending
  - id: create-final-report-generator
    content: "generate_final_validation_report.py 개발: 모든 검증 결과를 통합한 최종 리포트 생성"
    status: pending
isProject: false
---

# NEO GOD Ultra v2.0 비즈니스 로직 검증 및 프로덕션 준비 플랜

## 목표

프로덕션 배포 전 필수 검증 작업을 완료하여 시스템의 신뢰도를 99.9%로 향상시킵니다.

## 현재 상태

- 데이터 파이프라인 (Phase 1-3): 검증 완료
- Stress Test: 140/140 통과 (100%)
- 비즈니스 로직 검증: 미검증 (Critical Gap)
- BigQuery 실제 적재: 미검증 (Critical Gap)
- Excel vs BigQuery 교차 검증: 미검증 (Critical Gap)

## 작업 단계

### Task 1: 비즈니스 로직 검증 스크립트 개발

**파일**: `test_formula_logic.py`

**목표**: 적정점수 판정 로직, COMPUTE/RESTRICT 시트 조회 로직 검증

**구현 내용**:

1. **적정점수 판정 로직 테스트**

- 수식: `output/formula_analysis_report.json`의 `col_3` 수식 사용
- 테스트 케이스:
- 영어/국사 등급 검증 (C18, C19)
- RESTRICT 시트 3단계 폴백 메커니즘
- 경계값 판정 (`G6 >= J6`, `G6 >= K6`, `G6 >= L6`)
- `0/0` 에러 처리

2. **COMPUTE 시트 조회 로직 테스트**

- 수식: `col_4`, `col_5` INDEX/MATCH 조회
- 테스트 케이스:
- 존재하는 대학 코드 조회
- 존재하지 않는 대학 코드 조회 (IFERROR 처리)
- 행 헤더 불일치 케이스

3. **평균 점수 계산 로직 테스트**

- 수식: `col_7` HLOOKUP + AVERAGE
- 테스트 케이스:
- `MAX(0.00001, ...)` 최소값 보정
- 이과/문과 계열별 행 번호 차이 (4-5행 vs 6-7행)

**참고 파일**:

- `output/formula_analysis_report.json`: 수식 메타데이터
- `NEO_GOD_엔진_상세_명세서.md`: 수식 해석
- `phase2_extraction.py`: 수식 추출 로직

**예상 출력**:

- 테스트 결과 리포트 (JSON)
- 실패 케이스 상세 분석
- 경계값 오차 리포트

---

### Task 2: Excel 원본 vs BigQuery 교차 검증

**파일**: `test_excel_bigquery_cross_validation.py`

**목표**: Excel 수식 계산 결과와 BigQuery SQL 변환 결과 비교

**구현 내용**:

1. **Excel 수식 계산 엔진**

- OpenPyXL `data_only=False`로 수식 추출
- 실제 Excel 파일에서 샘플 데이터 추출 (100-200행)
- 수식 계산 실행 및 결과 저장

2. **BigQuery SQL 변환 로직**

- 적정점수 판정 로직을 SQL CASE WHEN으로 변환
- COMPUTE 시트 조회를 JOIN으로 변환
- RESTRICT 시트 폴백을 UNION ALL로 변환

3. **교차 검증**

- Excel 결과 vs BigQuery 결과 비교
- 오차 0.000001 이하 검증
- 불일치 케이스 상세 분석

**참고 파일**:

- `output/formula_analysis_report.json`: 수식 메타데이터
- `phase2_extraction.py`: 수식 추출 로직
- `phase4_load.py`: BigQuery 적재 로직

**예상 출력**:

- 교차 검증 리포트 (JSON)
- 불일치 케이스 리포트
- SQL 변환 로직 문서

---

### Task 3: BigQuery 실제 적재 테스트

**파일**: `test_bigquery_actual_load.py`

**목표**: 실제 BigQuery 연결 및 적재 검증

**구현 내용**:

1. **인증 확인**

- `neoprime-admin-key.json` 파일 존재 확인
- BigQuery 클라이언트 초기화 테스트
- 권한 확인 (데이터셋 읽기/쓰기)

2. **소규모 테스트 적재**

- 100행 샘플 데이터 생성
- Staging Table에 적재
- 스키마 자동 감지 검증
- NULL 처리 검증
- 행 수 일치 확인

3. **검증 리포트 생성**

- 적재 성공/실패 여부
- 스키마 정보
- 데이터 품질 리포트

**참고 파일**:

- `phase4_load.py`: StagingTableLoader 클래스
- `config.yaml`: BigQuery 설정
- `neoprime-admin-key.json`: 인증 파일

**예상 출력**:

- BigQuery 적재 테스트 리포트 (JSON)
- 스키마 검증 리포트
- 권한 확인 리포트

---

### Task 4: 실제 파일 E2E 테스트

**파일**: `test_e2e_real_file.py`

**목표**: 225,420행 실제 Excel 파일로 전체 파이프라인 실행

**구현 내용**:

1. **전체 파이프라인 실행**

- `master_pipeline.py` 호출
- Phase 1-4 순차 실행
- 각 Phase별 실행 시간 측정

2. **메모리 모니터링**

- `psutil`로 메모리 사용량 추적
- 피크 메모리 사용량 기록
- 메모리 누수 검증

3. **결과 무결성 검증**

- 행 수 일치 확인
- 컬럼 수 일치 확인
- 샘플 데이터 검증

**참고 파일**:

- `master_pipeline.py`: 파이프라인 오케스트레이션
- `config.yaml`: 설정 파일
- `202511고속성장분석기(가채점)20251114.xlsx`: 실제 Excel 파일

**예상 출력**:

- E2E 테스트 리포트 (JSON)
- 성능 리포트 (실행 시간, 메모리 사용량)
- 무결성 검증 리포트

---

### Task 5: python-calamine 설치 및 성능 검증

**파일**: `test_calamine_performance.py`

**목표**: Calamine 엔진 성능 검증

**구현 내용**:

1. **Calamine 설치 확인**

- `pip install python-calamine` 실행
- 설치 확인 테스트

2. **성능 비교 테스트**

- OpenPyXL로 Phase 1 실행 (시간 측정)
- Calamine으로 Phase 1 실행 (시간 측정)
- 성능 향상률 계산

3. **메모리 사용량 비교**

- 각 엔진별 메모리 사용량 측정
- 비교 리포트 생성

**참고 파일**:

- `phase1_scouting.py`: Scouting 로직
- `requirements.txt`: 패키지 목록

**예상 출력**:

- 성능 비교 리포트 (JSON)
- 메모리 사용량 비교 리포트

---

### Task 6: 경계값 부동소수점 오차 테스트

**파일**: `test_boundary_precision.py`

**목표**: 경계값 판정 로직의 부동소수점 오차 검증

**구현 내용**:

1. **경계값 테스트 케이스 생성**

- `G6 = J6 ± 0.000001` 케이스
- `G6 = K6 ± 0.000001` 케이스
- `G6 = L6 ± 0.000001` 케이스

2. **Excel vs Python vs BigQuery 비교**

- Excel에서 계산된 결과
- Python에서 계산된 결과
- BigQuery SQL에서 계산된 결과
- 세 결과 비교

3. **ROUND() 함수 적용 검증**

- ROUND() 함수 적용 위치 검증
- 정밀도 손실 분석

**참고 파일**:

- `output/formula_analysis_report.json`: 수식 메타데이터
- `phase3_normalization.py`: 정규화 로직

**예상 출력**:

- 경계값 테스트 리포트 (JSON)
- 부동소수점 오차 분석 리포트
- ROUND() 함수 적용 권장 사항

---

## 실행 순서

### Phase 1: Critical 작업 (Week 1)

**Day 1-2**: Task 1 (비즈니스 로직 검증)

- `test_formula_logic.py` 개발
- 적정점수 판정 로직 테스트
- COMPUTE/RESTRICT 조회 테스트

**Day 3-4**: Task 2 (Excel vs BigQuery 교차 검증)

- `test_excel_bigquery_cross_validation.py` 개발
- 수식 → SQL 변환 로직 구현
- 결과 비교 및 오차 분석

**Day 5**: Task 3 (BigQuery 실제 적재) + Task 4 (E2E 테스트)

- BigQuery 인증 확인
- 소규모 테스트 적재
- 실제 파일 E2E 테스트 실행

### Phase 2: High 작업 (Week 2)

**Day 1**: Task 5 (Calamine 성능 검증)

- Calamine 설치
- 성능 비교 테스트

**Day 2**: Task 6 (경계값 부동소수점 오차)

- 경계값 테스트 케이스 생성
- Excel vs Python vs BigQuery 비교

---

## 통합 리포트 생성

**파일**: `generate_final_validation_report.py`

**목표**: 모든 검증 결과를 통합한 최종 리포트 생성

**구현 내용**:

- 모든 테스트 결과 수집
- 통합 리포트 생성 (Markdown)
- 프로덕션 준비 상태 평가
- 남은 작업 목록 생성

---

## 검증 완료 기준

- [ ] 비즈니스 로직 검증 통과율 > 95%
- [ ] Excel vs BigQuery 교차 검증 오차 < 0.000001
- [ ] BigQuery 실제 적재 성공
- [ ] 실제 파일 E2E 테스트 통과
- [ ] Calamine 성능 향상 확인 (선택)
- [ ] 경계값 부동소수점 오차 해결

---

## 예상 산출물

1. `test_formula_logic.py` - 비즈니스 로직 검증 스크립트
2. `test_excel_bigquery_cross_validation.py` - 교차 검증 스크립트
3. `test_bigquery_actual_load.py` - BigQuery 적재 테스트 스크립트
4. `test_e2e_real_file.py` - E2E 테스트 스크립트
5. `test_calamine_performance.py` - Calamine 성능 검증 스크립트
6. `test_boundary_precision.py` - 경계값 부동소수점 오차 테스트 스크립트
7. `generate_final_validation_report.py` - 통합 리포트 생성 스크립트
8. `validation_reports/` - 모든 검증 리포트 디렉토리
9. `최종_검증_보고서.md` - 통합 최종 리포트

---

## 참고 문서

- [NEO_GOD_엔진_상세_명세서.md](y:\0126\0126\NEO_GOD_엔진_상세_명세서.md): 수식 해석
- [output/formula_analysis_report.json](y:\0126\0126\output\formula_analysis_report.json): 수식 메타데이터
- [phase2_extraction.py](y:\0126\0126\phase2_extraction.py): 수식 추출 로직
- [phase4_load.py](y:\0126\0126\phase4_load.py): BigQuery 적재 로직
- [config.yaml](y:\0126\0126\config.yaml): 설정 파일