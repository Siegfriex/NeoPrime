# BigQuery 적재 최종 보고서

**작성일**: 2026-01-26
**프로젝트**: NEO GOD Ultra Framework v2.0
**파이프라인 버전**: 2.0

---

## 1. 실행 요약

| 항목 | 값 |
|------|-----|
| 총 실행 시간 | 69.15초 |
| 소스 파일 | `202511고속성장분석기(가채점)20251114.xlsx` (23.36 MB) |
| 대상 시트 | 6개 |
| 추출 청크 | 9개 |
| 최종 상태 | **Partial Success** |

---

## 2. 파이프라인 단계별 결과

### Phase 1: 고속 정찰 (Scouting)
- **상태**: Completed
- **스캔 시간**: 0.26초
- **엔진**: openpyxl_fallback (Calamine 미설치)
- **식별 시트**: 6개 (medium/heavy)

### Phase 2: 물리적 이원화 추출
- **상태**: Completed
- **생성 청크**: 9개
- **총 행 수**: 225,420행

### Phase 3: Date-First 정규화
- **상태**: Completed
- **처리 청크**: 9개
- **컬럼명 정규화**: BigQuery 호환 형식 적용

### Phase 4: Staging Table 적재
- **상태**: Partial (2/6 성공)
- **적재 성공**: 12,830행
- **검증 실패**: 4개 시트 (NULL 비율 초과)

---

## 3. BigQuery 테이블 현황

### 3.1 성공적으로 적재된 테이블

| 테이블명 | 행 수 | 컬럼 수 | NULL 비율 | 상태 |
|----------|-------|---------|-----------|------|
| `tb_raw_2026_SUBJECT3` | 1,464 | 560 | 0.2% | **Success** |
| `tb_raw_2026_RAWSCORE` | 11,366 | 10 | 0.01% | **Success** |
| **합계** | **12,830** | - | - | - |

### 3.2 검증 실패 시트

| 시트명 | 행 수 | 실패 사유 | 문제 컬럼 |
|--------|-------|-----------|-----------|
| 이과계열분석결과 | 5,833 | NULL > 10% | unnamed_7 (92.5%), unnamed_8 (92.5%) |
| 문과계열분석결과 | 5,833 | NULL > 10% | unnamed_7 (92.5%), unnamed_8 (92.5%) |
| SUBJECT1 | 1,004 | NULL > 10% | column_0~unnamed_7 (96.1%) |
| INDEX | 199,920 | NULL > 10% | unnamed_1,4~9 (100%) |

---

## 4. 데이터 품질 분석

### 4.1 NULL 비율 검증 결과

검증 기준: **NULL 비율 10% 이하**

```
SUBJECT3:   0.2%  ✓ Pass
RAWSCORE:   0.01% ✓ Pass
이과계열:    92.5% ✗ Fail (unnamed_7, unnamed_8)
문과계열:    92.5% ✗ Fail (unnamed_7, unnamed_8)
SUBJECT1:   96.1% ✗ Fail (8개 컬럼)
INDEX:     100.0% ✗ Fail (7개 컬럼)
```

### 4.2 스키마 분석

원본 Excel 시트들의 스키마가 서로 상이하여 개별 테이블로 분리 적재:

| 시트 | 컬럼 수 | 특징 |
|------|---------|------|
| INDEX | 27 | 대용량 (20만행), 대부분 빈 컬럼 |
| SUBJECT3 | 560 | 다양한 수식 결과 |
| 분석결과 | 59 | 계열별 분석 데이터 |
| SUBJECT1 | 45 | 헤더 영역에 빈 셀 다수 |
| RAWSCORE | 10 | 깨끗한 데이터 |

---

## 5. GCP 환경 정보

| 항목 | 값 |
|------|-----|
| 프로젝트 ID | `neoprime0305` |
| 데이터셋 | `ds_neoprime_entrance` |
| 서비스 계정 | `sa-bq-loader@neoprime0305.iam.gserviceaccount.com` |
| 위치 | `asia-northeast3` |
| 인증 파일 | `neoprime-loader-key.json` |

---

## 6. 발견된 이슈 및 해결

### 6.1 해결된 이슈

| 이슈 | 원인 | 해결 방법 |
|------|------|-----------|
| 동일 파일 중복 업로드 | Phase3에서 청크별 고유 파일명 미생성 | `file_prefix` 파라미터 추가로 고유 파일명 생성 |
| 스키마 불일치 오류 | 기존 스테이징 테이블 스키마 충돌 | Step 0에서 기존 스테이징 테이블 삭제 |
| SQL 예약어 오류 | 컬럼명 `and`, `or`이 SQL 예약어 | 백틱으로 컬럼명 이스케이프 |
| 리포트 구조 오류 | 멀티 시트 결과 구조 미지원 | `generate_upload_report` 함수 멀티 시트 대응 |

### 6.2 미해결 이슈

| 이슈 | 원인 | 권장 해결 방법 |
|------|------|----------------|
| 4개 시트 적재 실패 | 원본 Excel에 빈 컬럼 다수 존재 | ① NULL 임계값 상향 (95%) 또는 ② 빈 컬럼 제외 추출 |

---

## 7. 권장 사항

### 7.1 즉시 조치 (데이터 완전 적재 필요 시)

**옵션 A**: NULL 임계값 상향
```yaml
# config.yaml
validation:
  null_threshold: 0.95  # 현재 0.1 → 0.95로 상향
```

**옵션 B**: 빈 컬럼 제외 후 재적재
- Phase 2/3에서 NULL 비율 100% 컬럼 자동 제외 로직 추가
- INDEX 시트의 유효 컬럼(3개)만 추출하여 적재

### 7.2 장기 개선

1. **데이터 프로파일링 자동화**: 추출 전 컬럼별 NULL 비율 사전 분석
2. **스키마 통합 전략**: 유사 스키마 시트 자동 병합 로직
3. **Calamine 설치**: 고속 추출 성능 향상 (현재 openpyxl fallback)

---

## 8. 파일 아티팩트

| 파일 | 설명 |
|------|------|
| `output/pipeline_report.json` | 파이프라인 실행 결과 |
| `output/upload_report.json` | BigQuery 업로드 상세 결과 |
| `output/scouting_report.json` | 시트 정찰 결과 |
| `output/data_quality_report.json` | 데이터 품질 분석 |
| `output/column_mapping.json` | 컬럼명 매핑 정보 |
| `output/normalized_*_part_*.parquet` | 정규화된 Parquet 파일 (9개) |

---

## 9. 결론

### 적재 결과 요약

- **총 추출 행**: 225,420행 (6개 시트)
- **성공 적재**: 12,830행 (2개 테이블) - **5.7%**
- **검증 실패**: 212,590행 (4개 시트) - **94.3%**

### 핵심 원인

원본 Excel 파일의 데이터 품질 문제:
- 다수의 빈 컬럼 (unnamed_X) 존재
- 특히 INDEX 시트는 27개 중 24개 컬럼이 100% NULL
- 이는 Excel 수식/참조 영역의 빈 셀이 추출된 결과

### 최종 판정

| 기준 | 결과 | 비고 |
|------|------|------|
| 행 수 검증 | **Partial** | 성공 시트만 행 수 일치 |
| NULL 비율 (<10%) | **2/6 Pass** | SUBJECT3, RAWSCORE만 통과 |
| 스키마 무결성 | **Pass** | 시트별 분리로 스키마 충돌 해결 |
| 데이터 타입 보존 | **Pass** | Date-First 정규화 정상 작동 |

---

**작성**: NEO GOD Ultra Framework v2.0
**검토**: Claude Opus 4.5
