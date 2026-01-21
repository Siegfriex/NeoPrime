# Theory Engine 매핑 리포트

이 리포트는 파이썬 시뮬레이션 엔진 함수가 어떤 엑셀 범위/수식 그룹을 담당하는지 보여줍니다.

## 1. RAWSCORE 변환 함수

**함수**: `convert_raw_to_standard()`

**담당 엑셀 범위**:
- 시트: RAWSCORE
- 컬럼: 영역, 과목명, 원점수, 표준점수, 백분위, 등급, 누적%

**수식 그룹**:
- RAWSCORE 시트의 조회 수식 (VLOOKUP/INDEX-MATCH 등)

## 2. INDEX 조회 함수

**함수**: `lookup_index()`

**담당 엑셀 범위**:
- 시트: INDEX
- 약 20만 행의 점수 조합 키 테이블

## 3. PERCENTAGE 조회 함수

**함수**: `lookup_percentage()`

**담당 엑셀 범위**:
- 시트: PERCENTAGE
- 대학별 누적백분위 환산점수표 (1100+ 컬럼)

## 4. 결격 체크 함수

**함수**: `check_disqualification()`

**담당 엑셀 범위**:
- 시트: RESTRICT
- 결격사유 룰 테이블

## 5. 전체 계산 파이프라인

**함수**: `compute_theory_result()`

**데이터 플로우**:
1. 원점수 입력 → RAWSCORE → 표준점수/백분위/등급
2. 점수 조합 → INDEX → 누백/전국등수
3. 대학/누백 → PERCENTAGE → 환산점수/커트라인
4. RESTRICT → 결격 사유 체크
5. 최종 합격 가능성/라인 판정

## 6. 시트 플로우 그래프 (TOP 10 edges)

- 이과계열분석결과 → INFO (weight=199957)
- INDEX → SUBJECT3 (weight=61050)
- SUBJECT3 → COMPUTE (weight=46632)
- PERCENTAGE → COMPUTE (weight=46632)
- INDEX → 수능입력 (weight=40833)
- SUBJECT3 → RESTRICT (weight=17487)
- PERCENTAGE → RESTRICT (weight=17487)
- SUBJECT3 → 수능입력 (weight=11658)
- PERCENTAGE → 수능입력 (weight=11658)
- INDEX → PERCENTAGE (weight=8800)

## 7. 룰 후보 요약

- 총 룰 후보: 42,900
- source_type 분포:
  - formula_if: 42,883
  - conditional_format: 16
  - data_validation: 1

---

*이 리포트는 자동 생성되었습니다.*