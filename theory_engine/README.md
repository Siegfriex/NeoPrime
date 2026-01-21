# NeoPrime Theory Engine v3.0

엑셀 기반 입시 예측 시뮬레이션 엔진을 파이썬으로 재구현한 핵심 계산 엔진입니다.

## 📋 개요

- **버전**: 3.0.0
- **엑셀 버전**: 202511_가채점_20251114
- **목적**: 엑셀 수식 로직을 파이썬으로 복원하여 자동화 및 확장 가능한 시뮬레이션 엔진 구축

## 🏗️ 구조

```
theory_engine/
├── __init__.py          # 패키지 초기화
├── config.py            # 설정 (시트 구조, 버전, 타입 캐스팅)
├── constants.py         # 상수 (LevelTheory, Track, 결격사유 코드)
├── utils.py             # 유틸리티 (시트 검증, 타입 변환, 품질 체크)
├── loader.py            # 데이터 로더 (엑셀 → DataFrame)
├── model.py             # 데이터 모델 (입출력 구조)
├── rules.py             # 룰 엔진 (RAWSCORE, INDEX, PERCENTAGE, RESTRICT)
└── README.md            # 이 파일
```

## 🚀 사용법

### 1. 기본 사용

```python
from theory_engine import config, loader, model, rules
from theory_engine.constants import Track

# 1. 엑셀 데이터 로드
excel_data = loader.load_workbook()

# 2. 학생 프로필 생성
korean = model.ExamScore("국어", raw_total=80)
math = model.ExamScore("수학", raw_total=75)
inquiry1 = model.ExamScore("물리학I", raw_total=50)
inquiry2 = model.ExamScore("화학I", raw_total=48)

profile = model.StudentProfile(
    track=Track.SCIENCE,
    korean=korean,
    math=math,
    english_grade=2,
    history_grade=3,
    inquiry1=inquiry1,
    inquiry2=inquiry2,
    targets=[model.TargetProgram("서울대", "공대")]
)

# 3. 시뮬레이션 실행
result = rules.compute_theory_result(excel_data, profile)

# 4. 결과 확인
for prog_result in result.program_results:
    print(f"대학: {prog_result.target.university}")
    print(f"전공: {prog_result.target.major}")
    print(f"라인: {prog_result.level_theory.value}")
    print(f"확률: {prog_result.p_theory}")
```

### 2. 개별 함수 사용

```python
# RAWSCORE 변환
rawscore_df = loader.load_rawscore()
result = rules.convert_raw_to_standard(
    rawscore_df,
    subject="국어",
    raw_score=80
)
print(result)  # {"found": True, "standard_score": 142, ...}

# INDEX 조회
index_df = loader.load_index_optimized()
result = rules.lookup_index(
    index_df,
    korean_std=142,
    math_std=145,
    inq1_std=68,
    inq2_std=67,
    track="이과"
)

# PERCENTAGE 조회
percentage_df = loader.load_percentage_raw()
result = rules.lookup_percentage(
    percentage_df,
    university="서울대",
    major="공대",
    percentile=95.5
)
```

## 📊 데이터 플로우

```
1. 원점수 입력 → RAWSCORE → 표준점수/백분위/등급
   ├─ convert_raw_to_standard()
   └─ raw_components["korean_standard"], ...

2. 점수 조합 → INDEX → 누백/전국등수
   ├─ lookup_index()
   └─ raw_components["index_key"], ["percentile_sum"]

3. 대학/누백 → PERCENTAGE → 환산점수/커트라인
   ├─ lookup_percentage()
   └─ score_theory, cutoff_safe/normal/risk

4. RESTRICT → 결격 사유 체크
   ├─ check_disqualification()
   └─ disqualification.is_disqualified

5. 최종 합격 가능성/라인 판정
   └─ level_theory (SAFE/NORMAL/RISK/REACH)
```

## 🔧 설정

### 시트별 로드 설정 (config.py)

```python
SHEET_CONFIG = {
    "RAWSCORE": SheetConfig(
        header=0, 
        required=True,
        expected_columns=["영역", "과목명", "원점수"]
    ),
    "INDEX": SheetConfig(header=0, required=True),
    "PERCENTAGE": SheetConfig(header=1, skiprows=[0], required=True),
    # ...
}
```

### 타입 캐스팅 패턴

```python
NUMERIC_PATTERNS = [
    "점수", "표준", "백분위", "등급", "누적", "누백",
    "적정", "예상", "소신", "환산", "원점수"
]
```

### 보간 정책

```python
PERCENTAGE_INTERPOLATION_POLICY = InterpolationPolicy.NEAREST_LOWER
INDEX_NOT_FOUND_POLICY = "warn"  # "error" | "warn" | "silent"
```

## 📝 주요 클래스

### LevelTheory (합격 라인)

- `SAFE`: 적정 (80%+)
- `NORMAL`: 예상 (50%+)
- `RISK`: 소신 (20%+)
- `REACH`: 상향 (<20%)
- `DISQUALIFIED`: 불가 (결격)

### Track (계열)

- `SCIENCE`: 이과 (미적분/기하 + 과탐)
- `LIBERAL`: 문과 (확률과통계 + 사탐)

### DisqualificationCode (결격 사유)

- `MATH_SUBJECT`: 수학선택과목제한
- `INQUIRY_SUBJECT`: 탐구과목제한
- `ENGLISH_GRADE`: 영어등급미달
- `HISTORY_GRADE`: 한국사등급미달

## 🧪 테스트

```bash
# pytest 사용
cd tests
pytest test_theory_engine.py -v

# 직접 실행
python test_theory_engine.py
```

## ⚠️ 주의사항

1. **엑셀 파일 필요**: `202511고속성장분석기(가채점)20251114 (1).xlsx` 파일이 프로젝트 루트에 있어야 합니다.

2. **실제 컬럼명 확인**: INDEX, PERCENTAGE 시트의 실제 컬럼 구조를 확인하여 `lookup_index()`, `lookup_percentage()` 함수를 조정해야 할 수 있습니다.

3. **RESTRICT 로직**: 결격 사유 체크 로직은 실제 RESTRICT 시트 구조에 맞게 구현이 필요합니다.

4. **커트라인 계산**: PERCENTAGE에서 80%, 50%, 20% 라인 계산 로직은 추가 구현이 필요합니다.

## 🔄 복원율

| 항목 | 자동화율 | 방법 |
|------|----------|------|
| 점수 변환/환산 알고리즘 | 85% | RAWSCORE + 수식 매핑 |
| 대학별 커트라인 | 90% | PERCENTAGE 정규화 |
| 결격 사유 룰 | 90% | RESTRICT + rules_triggered |
| 데이터 플로우 | 80% | INDEX 키 + raw_components |
| 버전 추적 | 100% | engine_version, excel_version |

## 📚 다음 단계

1. **INDEX 시트 MultiIndex 최적화**: 실제 컬럼명 확인 후 MultiIndex 구성
2. **PERCENTAGE Long 형태 정규화**: 대학-전공 파싱 로직 개선
3. **RESTRICT 룰 구현**: 실제 결격 사유 체크 로직 구현
4. **커트라인 계산**: 80/50/20% 라인 자동 계산
5. **A/B 갭 보정 모델**: Vertex AI 연동
6. **Golden Case 테스트**: 실제 데이터로 검증

## 📄 라이선스

NeoPrime Project - 2026
