"""
Theory Engine 데이터 모델

- 입력 구조 (StudentProfile, ExamScore, TargetProgram)
- 출력 구조 (TheoryResult, ProgramResult)
- 결격 정보 (DisqualificationInfo)
"""

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
    subject: str                      # 과목명 (예: "국어", "수학")
    subject_code: Optional[str] = None  # 과목 코드
    
    # 원점수
    raw_common: Optional[int] = None   # 공통 원점수
    raw_select: Optional[int] = None   # 선택 원점수
    raw_total: Optional[int] = None    # 총 원점수
    
    # 변환 점수
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
    track: Track                      # 계열 (이과/문과)
    
    # 수능 점수
    korean: ExamScore
    math: ExamScore
    english_grade: int                # 영어 등급
    history_grade: int                # 한국사 등급
    inquiry1: ExamScore
    inquiry2: ExamScore
    
    # 내신
    gpa_score: Optional[float] = None
    
    # 지원 대학
    targets: List[TargetProgram] = field(default_factory=list)


# ============================================================
# 출력 구조
# ============================================================
@dataclass
class DisqualificationInfo:
    """결격 상세 정보"""
    is_disqualified: bool = False
    reason: Optional[str] = None
    code: Optional[DisqualificationCode] = None
    rules_triggered: List[str] = field(default_factory=list)  # 적용된 룰 ID


# ============================================================
# 설명 가능성 (Explainability) - 최소 구현
# ============================================================
@dataclass
class MappingInfo:
    """입력 → 매칭 결과 및 근거"""
    input: str                          # 원본 입력
    matched: str                        # 매칭된 결과
    method: str                         # 'exact' | 'alias' | 'fuzzy'
    confidence: float = 1.0             # 0.0 ~ 1.0
    fuzzy_score: Optional[float] = None # 0~100 (rapidfuzz 등)
    alias_chain: List[str] = field(default_factory=list)  # 예: ["의예", "의학"]


@dataclass
class CutoffSourceInfo:
    """커트라인/점수 소스 정보"""
    sheet: str                          # 'INDEX' | 'PERCENTAGE'
    column_name: Optional[str] = None   # 실제 사용된 컬럼명
    percentile: Optional[float] = None  # 적용된 백분위(학생 누백 등)
    interpolated: bool = False          # 보간 여부
    interpolation_method: Optional[str] = None  # 'linear' | 'nearest' | None


@dataclass
class DisqualificationDetail:
    """결격 상세(설명가능성용)"""
    rule_id: str
    reason: str
    triggered_value: Optional[str] = None


@dataclass
class ExplainabilityInfo:
    """설명 가능성 정보(최소)"""
    university_mapping: Optional[MappingInfo] = None
    major_mapping: Optional[MappingInfo] = None
    cutoff_source: Optional[CutoffSourceInfo] = None
    disqualification_details: List[DisqualificationDetail] = field(default_factory=list)
    performance_ms: Optional[float] = None  # 처리 시간(선택)


@dataclass
class ProgramResult:
    """개별 대학/전형 결과"""
    target: TargetProgram
    
    # 합격 예측
    p_theory: Optional[float] = None   # 합격 확률
    score_theory: Optional[float] = None  # 환산 점수
    level_theory: LevelTheory = LevelTheory.UNKNOWN  # 합격 라인 레벨
    
    # 커트라인 상세
    cutoff_safe: Optional[float] = None     # 적정 (80%)
    cutoff_normal: Optional[float] = None   # 예상 (50%)
    cutoff_risk: Optional[float] = None     # 소신 (20%)
    
    # 결격 정보
    disqualification: DisqualificationInfo = field(
        default_factory=DisqualificationInfo
    )

    # 설명 가능성(근거) 정보
    explainability: ExplainabilityInfo = field(default_factory=ExplainabilityInfo)


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
    
    # 중간 계산 결과 (디버그/A-B 갭 분석용)
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
        
        # INDEX 조회 키
        "index_key": None,
        "index_found": False,
        
        # RAWSCORE 조회 키
        "rawscore_keys": [],
        
        # 누백/전국등수
        "percentile_sum": None,
        "national_rank": None,
        "cumulative_pct": None,
    })


if __name__ == "__main__":
    # 예제 데이터 생성
    korean = ExamScore(
        subject="국어",
        raw_common=45,
        raw_select=20,
        raw_total=65
    )
    
    math = ExamScore(
        subject="수학",
        raw_common=40,
        raw_select=18,
        raw_total=58
    )
    
    inquiry1 = ExamScore(subject="물리학I", raw_total=50)
    inquiry2 = ExamScore(subject="화학I", raw_total=48)
    
    target = TargetProgram(university="서울대", major="공대")
    
    profile = StudentProfile(
        track=Track.SCIENCE,
        korean=korean,
        math=math,
        english_grade=2,
        history_grade=3,
        inquiry1=inquiry1,
        inquiry2=inquiry2,
        targets=[target]
    )
    
    print("StudentProfile 예제:")
    print(f"  계열: {profile.track.value}")
    print(f"  국어: {profile.korean.raw_total}점")
    print(f"  수학: {profile.math.raw_total}점")
    print(f"  목표: {profile.targets[0].university} {profile.targets[0].major}")
    
    result = TheoryResult()
    print(f"\nTheoryResult 예제:")
    print(f"  Engine: {result.engine_version}")
    print(f"  Excel: {result.excel_version}")
