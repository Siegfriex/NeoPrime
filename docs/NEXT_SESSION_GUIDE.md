# NEO GOD Ultra Framework v2.3
## 다음 세션 진입 가이드

> 이 문서를 읽고 바로 개발에 진입하세요.

---

## 1. 프로젝트 현황 (2026-01-26 기준)

```
전체 진척도: 60%
├── Phase 1: Data Pipeline     ✅ 완료 (100%)
├── Phase 2: Score Calculator  🔄 진행중 (80%)
└── Phase 3: Ranking Engine    ⏳ 예정 (0%)
```

---

## 2. 핵심 파일 구조

```
Y:\0126\0126\
│
├── 🔧 파이프라인 (Phase 1)
│   ├── master_pipeline.py      # 전체 파이프라인 오케스트레이터
│   ├── phase1_scouting.py      # Excel 시트 스캔
│   ├── phase2_extraction.py    # 데이터 추출
│   ├── phase3_normalization.py # 정규화
│   └── phase4_load.py          # BigQuery 로드
│
├── 🧮 점수 계산 (Phase 2) ← 현재 작업 중
│   ├── score_calculator_v6.py  # ⭐ 최신 버전 (사용)
│   ├── score_calculator_v5.py  # Row 구조 정정
│   ├── score_calculator_v4.py  # 대학명 매핑
│   ├── score_calculator_v3.py  # 변형 컬럼
│   └── score_calculator_v2.py  # 가중택 지원
│
├── 📊 출력 데이터
│   └── output/
│       ├── COMPUTE_chunk_0000.parquet  # 핵심 계산 데이터
│       ├── column_mapping_v2.json      # 대학-컬럼 매핑
│       └── *.parquet                   # 기타 시트 데이터
│
├── 📝 문서
│   └── docs/
│       ├── NULL_VALUE_FIRST_PRINCIPLE.md    # 제1원칙
│       ├── INTERIM_DEVELOPMENT_REPORT_20260126.md  # 중간보고서
│       └── NEXT_SESSION_GUIDE.md            # 이 파일
│
└── ⚙️ 설정
    ├── config.yaml             # 파이프라인 설정
    └── neoprime-loader-key.json # BigQuery 인증키
```

---

## 3. BigQuery 테이블 현황

```sql
-- 데이터셋: neoprime0305.ds_neoprime_entrance

tb_raw_2026_COMPUTE          71 rows    ← 환산점수 핵심
tb_raw_2026_INDEX        199,920 rows   ← 대학별 상세
tb_raw_2026_RAWSCORE      11,366 rows   ← 원점수
tb_raw_2026_SUBJECT3       1,464 rows   ← 과목 정보
tb_computed_2026_SCORES       21 rows   ← 계산 결과 ⭐
... (총 15개 테이블)
```

---

## 4. 핵심 개념

### 4.1 Row 구조 (COMPUTE 시트)
```
Row 9:  국어 개별환산
Row 13: 수학 개별환산
Row 16: 영어 개별환산
Row 57: 필수총점 (영역 합계)
Row 59: 가중택총점
Row 63: 필수설정 ("국수영탐(2)")
Row 65: 가중택설정 ("국수영탐(2)中가중택4")
```

### 4.2 대학명 매핑
```python
UNIV_NAME_MAP = {
    '서울시립': '시립대',
    '한국외대': '외국어',
    '카이스트': '과기원',
}
```

### 4.3 제1원칙
> **"0이면 다른 곳에 정당한 값이 있다"**
> - 다른 이름으로 저장됨
> - 변형 컬럼(.1, .2)에 있음
> - 다른 Row에 있음

---

## 5. 빠른 시작

### 5.1 환경 확인
```powershell
cd Y:\0126\0126
python --version  # 3.x 확인
```

### 5.2 점수 계산 실행
```powershell
python score_calculator_v6.py
```

### 5.3 BigQuery 조회
```sql
SELECT * FROM `neoprime0305.ds_neoprime_entrance.tb_computed_2026_SCORES`
ORDER BY rank;
```

---

## 6. 다음 개발 TODO

### 우선순위 1 (이번 주)
- [ ] 실제 수능 점수 전체 입력 테스트 (수학/탐구 포함)
- [ ] 21개 → 전체 대학 확장
- [ ] 하드코딩된 매핑 → config.yaml 분리

### 우선순위 2 (다음 주)
- [ ] Phase 3: Ranking Engine 개발
- [ ] 합격 가능성 산출 로직
- [ ] API 인터페이스 설계

### 우선순위 3 (이후)
- [ ] 웹 UI 개발
- [ ] 모의지원 시뮬레이션

---

## 7. 주의사항

1. **score_calculator_v6.py 사용** - v2~v5는 히스토리용
2. **Parquet 파일 수정 금지** - 원본 데이터
3. **Row 번호 하드코딩 주의** - Excel 구조 변경 시 깨짐
4. **테스트 데이터 한계** - 현재 수학/탐구 미입력 상태

---

## 8. 문제 발생 시

### BigQuery 연결 오류
```powershell
# 인증키 확인
type neoprime-loader-key.json
```

### 점수 계산 이상
```python
# Row 구조 확인
import pandas as pd
df = pd.read_parquet('output/COMPUTE_chunk_0000.parquet')
print(df.iloc[63].get('연세대'))  # 필수설정 확인
```

### 대학 못 찾음
```python
# 컬럼 검색
[c for c in df.columns if '서울' in c]
```

---

## 9. 관련 문서

- [NULL 값 처리 제1원칙](./NULL_VALUE_FIRST_PRINCIPLE.md)
- [중간 개발 보고서](./INTERIM_DEVELOPMENT_REPORT_20260126.md)

---

*마지막 업데이트: 2026-01-26*
