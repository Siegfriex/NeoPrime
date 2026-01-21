"""
Theory Engine 설정 파일

- 시트별 로드 설정 (헤더, skiprows, 필수 여부)
- 버전 관리 (엔진 버전, 엑셀 버전)
- 타입 캐스팅 정책 (숫자 컬럼 패턴)
- 보간/조회 정책
"""

from typing import Dict, List, Optional, Set
from dataclasses import dataclass
from enum import Enum

# ============================================================
# 버전 관리
# ============================================================
ENGINE_VERSION = "3.0.0"
EXCEL_VERSION = "202511_가채점_20251114"
EXCEL_PATH = "202511고속성장분석기(가채점)20251114 (1).xlsx"

# ============================================================
# 시트별 로드 설정
# ============================================================
@dataclass
class SheetConfig:
    """시트 로드 설정"""
    header: Optional[int] = 0              # 헤더 행 번호
    skiprows: Optional[List[int]] = None   # 건너뛸 행
    skip: bool = False                     # 로드 제외 여부
    required: bool = True                  # 필수 시트 여부
    expected_columns: Optional[List[str]] = None  # 필수 컬럼 체크


# 실제 엑셀 구조 기반 설정
SHEET_CONFIG: Dict[str, SheetConfig] = {
    # 입력 시트 (optional)
    "INFO": SheetConfig(skip=True, required=False),
    "원점수입력": SheetConfig(header=2, skiprows=[0, 1], required=False),
    "수능입력": SheetConfig(header=2, skiprows=[0, 1], required=False),
    "내신입력": SheetConfig(header=1, skiprows=[0], required=False),
    "이과계열분석결과": SheetConfig(header=2, skiprows=[0, 1], required=False),
    "문과계열분석결과": SheetConfig(header=2, skiprows=[0, 1], required=False),
    "메모장": SheetConfig(skip=True, required=False),
    
    # 핵심 계산 시트 (required)
    "RAWSCORE": SheetConfig(
        header=0, 
        required=True,
        expected_columns=["영역", "과목명", "원점수"]
    ),
    "INDEX": SheetConfig(
        header=0, 
        required=True,
    ),
    "PERCENTAGE": SheetConfig(
        header=3,  # 3행(0-based)이 실제 헤더
        required=True,
    ),
    "RESTRICT": SheetConfig(
        header=0, 
        required=True,
        # 실제로는 카테고리별 컬럼: "□ 결격사유<수학,탐구>" 등
    ),
    "COMPUTE": SheetConfig(header=0, required=True),
    "SUBJECT1": SheetConfig(header=0, required=True),
    "SUBJECT2": SheetConfig(header=0, required=True),
    "SUBJECT3": SheetConfig(header=0, required=True),
}

# ============================================================
# 타입 캐스팅 설정
# ============================================================
# 패턴 매칭 (컬럼명에 포함되면 숫자로 변환)
NUMERIC_PATTERNS: List[str] = [
    "점수", "표준", "백분위", "등급", "누적", "누백",
    "적정", "예상", "소신", "환산", "원점수"
]

# 명시적 캐스팅 (정확한 컬럼명)
EXPLICIT_NUMERIC_COLUMNS: Set[str] = {
    "202511(가채점)", "Unnamed: 7", "Unnamed: 8", "Unnamed: 9",
    "수능점수", "내신점수", "수능+내신",
    "적정점수", "예상점수", "소신점수",
    "적정누백", "예상누백", "소신누백",
}

# 예외 (숫자로 변환 금지)
EXCLUDE_FROM_NUMERIC: Set[str] = {
    "INDEX", "과목명-원점수", "대학교", "전공", "모집단위", "영역", "과목명"
}

# ============================================================
# INDEX 시트 최적화 설정
# ============================================================
# MultiIndex 구성 컬럼 (실제 시트 확인 후 조정 필요)
INDEX_KEY_COLUMNS: List[str] = [
    "korean_std",  # 국어 표준점수
    "math_std",    # 수학 표준점수
    "inq1_std",    # 탐구1 표준점수
    "inq2_std",    # 탐구2 표준점수
    "track"        # 계열 (이과/문과)
]

# ============================================================
# 보간/조회 정책
# ============================================================
class InterpolationPolicy(Enum):
    """보간 정책"""
    NEAREST_LOWER = "nearest_lower"   # 가장 가까운 아래 값
    NEAREST_UPPER = "nearest_upper"   # 가장 가까운 위 값
    LINEAR = "linear"                 # 선형 보간
    NONE = "none"                     # 없으면 None


# 기본 정책
PERCENTAGE_INTERPOLATION_POLICY = InterpolationPolicy.NEAREST_LOWER
INDEX_NOT_FOUND_POLICY = "warn"  # "error" | "warn" | "silent"


if __name__ == "__main__":
    print(f"Engine Version: {ENGINE_VERSION}")
    print(f"Excel Version: {EXCEL_VERSION}")
    print(f"Required sheets: {[k for k, v in SHEET_CONFIG.items() if v.required]}")
