---
name: Theory Engine v3 최종
overview: 모든 피드백(시트 존재 체크, 명시적 캐스팅 컬럼, level_theory enum, raw_components 키 필수화, 보간 정책 config 분리, disqual_rules_triggered, 실패 케이스 테스트, 버전 검증)을 반영한 최종 Theory Engine 설계입니다.
todos:
  - id: config
    content: config.py - SheetConfig, 버전, 보간 정책, 캐스팅 설정
    status: in_progress
  - id: constants
    content: constants.py - LevelTheory enum, DisqualificationCode, 필수 키 정의
    status: pending
  - id: utils
    content: utils.py - validate_sheets, validate_columns, cast_numeric_columns
    status: pending
    dependencies:
      - config
  - id: loader
    content: loader.py - 엑셀 로더 (검증 + INDEX 최적화 + PERCENTAGE 정규화)
    status: pending
    dependencies:
      - utils
  - id: model
    content: model.py - StudentProfile, TheoryResult, DisqualificationInfo (raw_components 필수 키)
    status: pending
    dependencies:
      - constants
  - id: rules-rawscore
    content: rules.py - convert_raw_to_standard() + rawscore_keys 저장
    status: pending
    dependencies:
      - loader
      - model
  - id: rules-index
    content: rules.py - lookup_index() + index_key/index_found 저장
    status: pending
    dependencies:
      - rules-rawscore
  - id: rules-percentage
    content: rules.py - lookup_percentage() + 보간 정책 적용
    status: pending
    dependencies:
      - rules-index
  - id: rules-restrict
    content: rules.py - check_disqualification() + rules_triggered 리스트
    status: pending
    dependencies:
      - rules-percentage
  - id: rules-compute
    content: rules.py - compute_theory_result() + 디버그 모드
    status: pending
    dependencies:
      - rules-restrict
  - id: golden-data
    content: tests/data/golden_cases.xlsx - 성공 + 실패 + 경계 케이스
    status: pending
    dependencies:
      - rules-compute
  - id: tests
    content: test_theory_engine.py - 버전 검증 + 골든 레코드 + raw_components 키 검증
    status: pending
    dependencies:
      - golden-data
---

# NeoPrime Theory Engine v3 - 최종 완성 설계

## 프로젝트 구조

```
C:\Neoprime\
├── theory_engine/
│   ├── __init__.py
│   ├── config.py       # 시트 설정, 버전, 정책, 상수
│   ├── constants.py    # NEW: level_theory enum, 상수 정의
│   ├── loader.py       # 엑셀 로더
│   ├── model.py        # 입출력 모델
│   ├── rules.py        # 룰 엔진
│   └── utils.py        # 유틸리티
├── tests/
│   ├── data/
│   │   └── golden_cases.xlsx  # 성공 + 실패 케이스 포함
│   └── test_theory_engine.py
└── 202511고속성장분석기(가채점)20251114 (1).xlsx
```

---

## 1. config.py - 설정 및 정책 관리

[`theory_engine/config.py`](C:\Neoprime\theory_engine\config.py)

```python
from typing import Dict, List, Optional, Set
from dataclasses import dataclass
from enum import Enum

# ============================================================
# 버전 관리
# ============================================================
ENGINE_VERSION = "3.0.0"
EXCEL_VERSION = "202511_가채점_20251114"

# ============================================================
# 시트별 설정 (존재 체크 포함)
# ============================================================
@dataclass
class SheetConfig:
    header: Optional[int] = 0
    skiprows: Optional[List[int]] = None
    skip: bool = False                    # True면 로드 제외
    required: bool = True                 # NEW: 필수 시트 여부
    expected_columns: Optional[List[str]] = None  # NEW: 필수 컬럼 체크

SHEET_CONFIG: Dict[str, SheetConfig] = {
    "INFO": SheetConfig(skip=True, required=False),
    "원점수입력": SheetConfig(header=2, skiprows=[0, 1], required=False),
    "수능입력": SheetConfig(header=2, skiprows=[0, 1], required=False),
    "내신입력": SheetConfig(header=1, skiprows=[0], required=False),
    "이과계열분석결과": SheetConfig(header=2, skiprows=[0, 1], required=False),
    "문과계열분석결과": SheetConfig(header=2, skiprows=[0, 1], required=False),
    "COMPUTE": SheetConfig(header=0, required=True),
    "RESTRICT": SheetConfig(header=0, required=True,
                           expected_columns=["결격사유"]),
    "SUBJECT1": SheetConfig(header=0, required=True),
    "SUBJECT2": SheetConfig(header=0, required=True),
    "SUBJECT3": SheetConfig(header=0, required=True),
    "PERCENTAGE": SheetConfig(header=1, skiprows=[0], required=True),
    "INDEX": SheetConfig(header=0, required=True),
    "RAWSCORE": SheetConfig(header=0, required=True,
                           expected_columns=["영역", "과목명", "원점수"]),
    "메모장": SheetConfig(skip=True, required=False),
}

# ============================================================
# 타입 캐스팅 설정
# ============================================================
# 패턴 기반 (포함 여부)
NUMERIC_PATTERNS: List[str] = [
    "점수", "표준", "백분위", "등급", "누적", "누백",
    "적정", "예상", "소신", "환산", "원점수"
]

# NEW: 명시적 캐스팅 컬럼 (정확한 컬럼명)
EXPLICIT_NUMERIC_COLUMNS: Set[str] = {
    # RAWSCORE
    "202511(가채점)", "Unnamed: 7", "Unnamed: 8", "Unnamed: 9",
    # 분석결과 시트
    "수능점수", "내신점수", "수능+내신",
    "적정점수", "예상점수", "소신점수",
    "적정누백", "예상누백", "소신누백",
}

# NEW: 숫자로 변환하면 안 되는 컬럼 (예외)
EXCLUDE_FROM_NUMERIC: Set[str] = {
    "INDEX", "과목명-원점수", "대학교", "전공", "모집단위"
}

# ============================================================
# INDEX 시트 멀티인덱스 설정
# ============================================================
INDEX_KEY_COLUMNS: List[str] = [
    "korean_std", "math_std", "inq1_std", "inq2_std", "track"
]

# ============================================================
# NEW: 보간/조회 정책 (rules.py에서 사용)
# ============================================================
class InterpolationPolicy(Enum):
    NEAREST_LOWER = "nearest_lower"   # 없으면 가장 가까운 아래 값
    NEAREST_UPPER = "nearest_upper"   # 없으면 가장 가까운 위 값
    LINEAR = "linear"                 # 선형 보간
    NONE = "none"                     # 없으면 None 반환

# 기본 보간 정책
PERCENTAGE_INTERPOLATION_POLICY = InterpolationPolicy.NEAREST_LOWER
INDEX_NOT_FOUND_POLICY = "warn"  # "error" | "warn" | "silent"
```

---

## 2. constants.py - 상수 및 Enum 정의

[`theory_engine/constants.py`](C:\Neoprime\theory_engine\constants.py)

```python
from enum import Enum

# ============================================================
# NEW: 합격 라인 레벨 (상수화)
# ============================================================
class LevelTheory(str, Enum):
    """합격 가능성 라인 상수"""
    SAFE = "적정"           # 합격률 80% 이상
    NORMAL = "예상"         # 합격률 50% 이상
    RISK = "소신"           # 합격률 20% 이상
    REACH = "상향"          # 합격률 20% 미만
    
    # 에러/예외 상태
    DISQUALIFIED = "불가"   # 결격 사유
    INPUT_ERROR = "입력오류"
    NO_DATA = "데이터없음"
    UNKNOWN = "알수없음"

# ============================================================
# 계열 상수
# ============================================================
class Track(str, Enum):
    SCIENCE = "이과"        # 미적/기하 + 과탐
    LIBERAL = "문과"        # 확통 + 사탐

# ============================================================
# 결격 사유 코드
# ============================================================
class DisqualificationCode(str, Enum):
    MATH_SUBJECT = "수학선택과목제한"
    INQUIRY_SUBJECT = "탐구과목제한"
    INQUIRY_COMBINATION = "탐구조합제한"
    ENGLISH_GRADE = "영어등급미달"
    HISTORY_GRADE = "한국사등급미달"
    SECOND_FOREIGN = "제2외국어제한"

# ============================================================
# raw_components 필수 키 (A/B 갭 분석용)
# ============================================================
REQUIRED_RAW_COMPONENT_KEYS = [
    # 점수 변환 결과
    "korean_standard",
    "korean_percentile",
    "korean_grade",
    "math_standard",
    "math_percentile",
    "math_grade",
    "inquiry1_standard",
    "inquiry2_standard",
    
    # INDEX 조회 키
    "index_key",
    "index_found",
    
    # RAWSCORE 조회 키
    "rawscore_keys",
    
    # 누백/전국등수
    "percentile_sum",
    "national_rank",
    "cumulative_pct",
]
```

---

## 3. utils.py - 유틸리티 (시트 체크 포함)

[`theory_engine/utils.py`](C:\Neoprime\theory_engine\utils.py)

```python
import logging
from typing import Dict, List, Optional, Set
import pandas as pd

from .config import (
    SHEET_CONFIG, NUMERIC_PATTERNS, 
    EXPLICIT_NUMERIC_COLUMNS, EXCLUDE_FROM_NUMERIC
)

logger = logging.getLogger(__name__)

# ============================================================
# NEW: 시트 존재 여부 체크
# ============================================================
def validate_sheets(
    xlsx: pd.ExcelFile,
    strict: bool = False
) -> Dict[str, bool]:
    """
    엑셀 파일의 시트 존재 여부 검증
    
    Returns: {시트명: 존재여부}
    Raises: ValueError if strict=True and required sheet missing
    """
    available = set(xlsx.sheet_names)
    result = {}
    
    for sheet_name, config in SHEET_CONFIG.items():
        exists = sheet_name in available
        result[sheet_name] = exists
        
        if not exists:
            if config.required:
                msg = f"필수 시트 누락: {sheet_name}"
                if strict:
                    raise ValueError(msg)
                else:
                    logger.warning(msg)
            else:
                logger.info(f"선택 시트 없음 (무시): {sheet_name}")
    
    # 예상치 못한 시트 경고
    expected = set(SHEET_CONFIG.keys())
    unexpected = available - expected
    if unexpected:
        logger.warning(f"알 수 없는 시트 발견: {unexpected}")
    
    return result

# ============================================================
# NEW: 필수 컬럼 체크
# ============================================================
def validate_columns(
    df: pd.DataFrame,
    sheet_name: str
) -> List[str]:
    """
    시트의 필수 컬럼 존재 여부 검증
    
    Returns: 누락된 컬럼 리스트
    """
    config = SHEET_CONFIG.get(sheet_name)
    if not config or not config.expected_columns:
        return []
    
    missing = []
    for col in config.expected_columns:
        if col not in df.columns:
            missing.append(col)
            logger.warning(f"[{sheet_name}] 필수 컬럼 누락: {col}")
    
    return missing

# ============================================================
# 타입 캐스팅 (개선)
# ============================================================
def cast_numeric_columns(
    df: pd.DataFrame,
    sheet_name: str = ""
) -> pd.DataFrame:
    """
    숫자 컬럼 강제 변환
    
    1. EXPLICIT_NUMERIC_COLUMNS에 있으면 무조건 변환
    2. EXCLUDE_FROM_NUMERIC에 있으면 제외
    3. NUMERIC_PATTERNS에 매칭되면 변환
    """
    df = df.copy()
    converted = []
    
    for col in df.columns:
        # 제외 대상
        if col in EXCLUDE_FROM_NUMERIC:
            continue
        
        should_convert = False
        
        # 명시적 지정
        if col in EXPLICIT_NUMERIC_COLUMNS:
            should_convert = True
        # 패턴 매칭
        elif any(pattern in str(col) for pattern in NUMERIC_PATTERNS):
            should_convert = True
        
        if should_convert:
            original_dtype = df[col].dtype
            df[col] = pd.to_numeric(df[col], errors='coerce')
            if df[col].dtype != original_dtype:
                converted.append(col)
    
    if converted:
        logger.debug(f"[{sheet_name}] 숫자 변환: {converted}")
    
    return df

def log_dtypes(df: pd.DataFrame, sheet_name: str) -> None:
    """dtype 추론 결과 로깅"""
    logger.info(f"[{sheet_name}] shape={df.shape}")
    logger.debug(f"[{sheet_name}] dtypes:\n{df.dtypes}")
```

---

## 4. model.py - 입출력 모델 (최종)

[`theory_engine/model.py`](C:\Neoprime\theory_engine\model.py)

```python
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional

from .config import ENGINE_VERSION, EXCEL_VERSION
from .constants import LevelTheory, Track, DisqualificationCode

# ============================================================
# 입력 구조
# ============================================================
@dataclass
class ExamScore:
    """개별 과목 점수"""
    subject: str
    subject_code: Optional[str] = None
    raw_common: Optional[int] = None      # 공통 원점수
    raw_select: Optional[int] = None      # 선택 원점수
    raw_total: Optional[int] = None       # 총 원점수
    standard_score: Optional[int] = None
    percentile: Optional[float] = None
    grade: Optional[int] = None

@dataclass
class TargetProgram:
    """지원 대학/전형 정보"""
    university: str
    major: str
    admission_type: str = "수능위주"
    suneung_ratio: float = 1.0
    inquiry_combination_code: Optional[str] = None

@dataclass
class StudentProfile:
    """학생 입력 프로필"""
    track: Track
    korean: ExamScore
    math: ExamScore
    english_grade: int
    history_grade: int
    inquiry1: ExamScore
    inquiry2: ExamScore
    gpa_score: Optional[float] = None
    targets: List[TargetProgram] = field(default_factory=list)

# ============================================================
# 출력 구조
# ============================================================
@dataclass
class DisqualificationInfo:
    """NEW: 결격 상세 정보"""
    is_disqualified: bool = False
    reason: Optional[str] = None
    code: Optional[DisqualificationCode] = None
    rules_triggered: List[str] = field(default_factory=list)  # NEW

@dataclass
class ProgramResult:
    """개별 대학/전형 결과"""
    target: TargetProgram
    p_theory: Optional[float]
    score_theory: Optional[float]
    level_theory: LevelTheory              # NEW: Enum 사용
    
    # 커트라인 상세
    cutoff_safe: Optional[float] = None    # 적정 (80%)
    cutoff_normal: Optional[float] = None  # 예상 (50%)
    cutoff_risk: Optional[float] = None    # 소신 (20%)
    
    # 결격 정보
    disqualification: DisqualificationInfo = field(
        default_factory=DisqualificationInfo
    )

@dataclass
class TheoryResult:
    """이론 시뮬레이션 결과"""
    # 버전 태깅
    engine_version: str = ENGINE_VERSION
    excel_version: str = EXCEL_VERSION
    computed_at: str = field(
        default_factory=lambda: datetime.now().isoformat()
    )
    
    # 다중 대학 결과
    program_results: List[ProgramResult] = field(default_factory=list)
    
    # NEW: 중간 계산 결과 (필수 키 포함)
    raw_components: Dict[str, Any] = field(default_factory=lambda: {
        # 점수 변환 결과
        "korean_standard": None,
        "korean_percentile": None,
        "korean_grade": None,
        "math_standard": None,
        "math_percentile": None,
        "math_grade": None,
        "inquiry1_standard": None,
        "inquiry2_standard": None,
        
        # INDEX 조회 키 (A/B 갭 분석용)
        "index_key": None,
        "index_found": False,
        
        # RAWSCORE 조회 키
        "rawscore_keys": [],
        
        # 누백/전국등수
        "percentile_sum": None,
        "national_rank": None,
        "cumulative_pct": None,
    })
```

---

## 5. rules.py - 룰 엔진 (최종)

[`theory_engine/rules.py`](C:\Neoprime\theory_engine\rules.py)

### 핵심 함수 시그니처

```python
from .config import (
    InterpolationPolicy, 
    PERCENTAGE_INTERPOLATION_POLICY,
    INDEX_NOT_FOUND_POLICY
)
from .constants import LevelTheory, DisqualificationCode
from .model import (
    StudentProfile, TheoryResult, ProgramResult,
    DisqualificationInfo, TargetProgram
)

# ============================================================
# RAWSCORE 변환
# ============================================================
def convert_raw_to_standard(
    rawscore_df: pd.DataFrame,
    subject: str,
    raw_common: int,
    raw_select: int
) -> Dict[str, Any]:
    """
    원점수 → 표준점수/백분위/등급/누적% 변환
    
    조회 키: f"{subject}-{raw_common}-{raw_select}"
    키를 raw_components["rawscore_keys"]에 추가
    """

# ============================================================
# INDEX 조회 (MultiIndex)
# ============================================================
def lookup_index(
    index_df: pd.DataFrame,
    korean_std: int,
    math_std: int,
    inq1_std: int,
    inq2_std: int,
    track: str,
    policy: str = INDEX_NOT_FOUND_POLICY
) -> Optional[pd.Series]:
    """
    점수 조합으로 INDEX 행 찾기
    
    policy:
    - "error": 없으면 예외 발생
    - "warn": 없으면 경고 + None 반환
    - "silent": 없으면 None 반환
    
    index_key를 raw_components["index_key"]에 저장
    """

# ============================================================
# PERCENTAGE 조회 (보간 정책 분리)
# ============================================================
def lookup_percentage(
    percentage_df: pd.DataFrame,
    university: str,
    major: str,
    percentile: float,
    policy: InterpolationPolicy = PERCENTAGE_INTERPOLATION_POLICY
) -> Dict[str, Optional[float]]:
    """
    대학/전공/누백으로 환산점수 조회
    
    NEW: 보간 정책 config에서 분리
    - NEAREST_LOWER: 없으면 가장 가까운 아래 값
    - NEAREST_UPPER: 없으면 가장 가까운 위 값
    - LINEAR: 선형 보간
    - NONE: 없으면 None
    """

# ============================================================
# RESTRICT 결격 체크 (상세 정보 반환)
# ============================================================
def check_disqualification(
    restrict_df: pd.DataFrame,
    profile: StudentProfile,
    target: TargetProgram
) -> DisqualificationInfo:
    """
    결격 사유 확인
    
    NEW: DisqualificationInfo 반환
    - rules_triggered: 적용된 룰 리스트
      예: ["수학_확통_의대불가", "영어_3등급_초과"]
    - LLM이 "왜 불가인지" 설명할 때 바로 사용 가능
    """

# ============================================================
# 최상위 계산 함수
# ============================================================
def compute_theory_result(
    excel_data: Dict[str, pd.DataFrame],
    profile: StudentProfile,
    debug: bool = False
) -> TheoryResult:
    """
    전체 이론 계산 파이프라인
    
    계산 순서:
    1. 원점수 → RAWSCORE → 표준점수/백분위/등급
       → raw_components에 키/결과 저장
    2. 점수 조합 → INDEX → 누백/전국등수
       → raw_components["index_key"], ["index_found"] 저장
    3. 각 target에 대해:
       a. RESTRICT → 결격 체크
          → rules_triggered 리스트 저장
       b. PERCENTAGE → 환산점수/커트라인
       c. 합격 가능성/라인 판정 (LevelTheory enum)
    
    예외 처리:
    - 점수 누락: LevelTheory.INPUT_ERROR
    - 대학 데이터 없음: LevelTheory.NO_DATA
    - 결격: LevelTheory.DISQUALIFIED
    
    debug=True:
    - 모든 중간 결과를 raw_components에 상세 저장
    """
```

---

## 6. 테스트 구조 (최종)

[`tests/test_theory_engine.py`](C:\Neoprime\tests\test_theory_engine.py)

### golden_cases.xlsx 구조

| case_id | type | korean_raw | math_raw | ... | expected_level | expected_score | expected_disqual | disqual_reason |

|---------|------|------------|----------|-----|----------------|----------------|------------------|----------------|

| TC001 | success | 90 | 95 | ... | 적정 | 98.5 | false | |

| TC002 | success | 100 | 100 | ... | 적정 | 99.9 | false | |

| TC003 | **failure** | 80 | 85 | ... | **불가** | | **true** | 수학선택과목제한 |

| TC004 | **failure** | 90 | 95 | ... | **데이터없음** | | false | |

| TC005 | boundary | 89 | 90 | ... | 적정 | 97.5 | false | |

| TC006 | boundary | 88 | 90 | ... | 예상 | 97.4 | false | |

### 테스트 코드

```python
import pytest
from theory_engine.config import ENGINE_VERSION, EXCEL_VERSION
from theory_engine.constants import LevelTheory

# ============================================================
# NEW: 버전 검증 테스트
# ============================================================
def test_engine_version():
    """엔진 버전 확인"""
    assert ENGINE_VERSION == "3.0.0"

def test_excel_version_in_result():
    """결과에 엑셀 버전 포함 확인"""
    result = simulate_theory(excel_data, sample_profile)
    assert result.excel_version == EXCEL_VERSION
    assert result.engine_version == ENGINE_VERSION

# ============================================================
# 골든 레코드 테스트 (성공 + 실패)
# ============================================================
@pytest.fixture
def golden_cases():
    return pd.read_excel("tests/data/golden_cases.xlsx")

def test_success_cases(golden_cases):
    """성공 케이스 검증"""
    success_cases = golden_cases[golden_cases["type"] == "success"]
    for _, case in success_cases.iterrows():
        result = simulate_for_case(case)
        assert result.level_theory.value == case["expected_level"]
        assert abs(result.score_theory - case["expected_score"]) < 0.1

def test_failure_cases(golden_cases):
    """NEW: 실패 케이스 검증 (결격, 데이터없음)"""
    failure_cases = golden_cases[golden_cases["type"] == "failure"]
    for _, case in failure_cases.iterrows():
        result = simulate_for_case(case)
        assert result.level_theory.value == case["expected_level"]
        
        if case["expected_disqual"]:
            assert result.disqualification.is_disqualified
            assert case["disqual_reason"] in str(result.disqualification.rules_triggered)

# ============================================================
# 경계 케이스 테스트
# ============================================================
def test_boundary_cases(golden_cases):
    """커트라인 경계 테스트"""
    boundary_cases = golden_cases[golden_cases["type"] == "boundary"]
    for _, case in boundary_cases.iterrows():
        result = simulate_for_case(case)
        assert result.level_theory.value == case["expected_level"]

def test_perfect_score():
    """만점 케이스"""

def test_zero_score():
    """0점 케이스"""

def test_cutline_boundary_above():
    """커트라인 바로 위 (+0.1)"""

def test_cutline_boundary_below():
    """커트라인 바로 아래 (-0.1)"""

# ============================================================
# raw_components 필수 키 검증
# ============================================================
def test_raw_components_required_keys():
    """raw_components에 필수 키 포함 확인"""
    result = simulate_theory(excel_data, sample_profile, debug=True)
    
    required_keys = [
        "korean_standard", "math_standard",
        "index_key", "index_found",
        "rawscore_keys", "percentile_sum"
    ]
    for key in required_keys:
        assert key in result.raw_components

def test_disqual_rules_triggered():
    """NEW: 결격 시 rules_triggered 리스트 확인"""
    result = simulate_for_disqualified_case()
    assert result.disqualification.is_disqualified
    assert len(result.disqualification.rules_triggered) > 0
```

---

## 작업 순서 (최종)

| 순서 | 파일 | 작업 내용 |

|------|------|-----------|

| 1 | config.py | SheetConfig, 버전, 보간 정책, 캐스팅 설정 |

| 2 | constants.py | LevelTheory enum, DisqualificationCode, 필수 키 |

| 3 | utils.py | validate_sheets, validate_columns, cast_numeric |

| 4 | loader.py | 엑셀 로더 (검증 + 정규화) |

| 5 | model.py | dataclass 정의 (필수 키 포함) |

| 6 | rules.py | RAWSCORE/INDEX/PERCENTAGE/RESTRICT 룰 |

| 7 | tests/data/golden_cases.xlsx | 성공 + 실패 + 경계 케이스 |

| 8 | test_theory_engine.py | 버전 검증 + 골든 레코드 + 경계 테스트 |

---

## 복원 가능 범위 (최종)

| 항목 | 자동화율 | 방법 |

|------|----------|------|

| 점수 변환/환산 알고리즘 | 85% | RAWSCORE + 수식 매핑 |

| 대학별 커트라인 | 90% | PERCENTAGE 정규화 |

| 결격 사유 룰 | 90% | RESTRICT + rules_triggered |

| 데이터 플로우 | 80% | INDEX 키 + raw_components |

| 버전 추적 | 100% | engine_version, excel_version |

| **예외/정성 판단** | **25%** | **인터뷰/주석/config override** |