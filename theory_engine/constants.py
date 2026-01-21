"""
Theory Engine 상수 정의

- LevelTheory: 합격 라인 레벨
- DisqualificationCode: 결격 사유 코드
- Track: 계열 구분
"""

from enum import Enum
from typing import List, Tuple

# ============================================================
# 합격 라인 레벨
# ============================================================
class LevelTheory(str, Enum):
    """합격 가능성 라인"""
    # 정상 라인
    SAFE = "적정"      # 합격률 80% 이상
    NORMAL = "예상"    # 합격률 50% 이상
    RISK = "소신"      # 합격률 20% 이상
    REACH = "상향"     # 합격률 20% 미만
    
    # 예외 상태
    DISQUALIFIED = "불가"      # 결격 사유
    INPUT_ERROR = "입력오류"
    NO_DATA = "데이터없음"
    UNKNOWN = "알수없음"
    
    def to_probability_range(self) -> Tuple[float, float]:
        """확률 범위 반환"""
        mapping = {
            self.SAFE: (0.80, 1.00),
            self.NORMAL: (0.50, 0.80),
            self.RISK: (0.20, 0.50),
            self.REACH: (0.00, 0.20),
            self.DISQUALIFIED: (0.00, 0.00),
        }
        return mapping.get(self, (0.00, 0.00))


# ============================================================
# 계열 구분
# ============================================================
class Track(str, Enum):
    """계열"""
    SCIENCE = "이과"    # 미적분/기하 + 과탐
    LIBERAL = "문과"    # 확률과통계 + 사탐


# ============================================================
# 결격 사유 코드
# ============================================================
class DisqualificationCode(str, Enum):
    """결격 사유 상세 코드"""
    MATH_SUBJECT = "수학선택과목제한"
    INQUIRY_SUBJECT = "탐구과목제한"
    INQUIRY_COMBINATION = "탐구조합제한"
    ENGLISH_GRADE = "영어등급미달"
    HISTORY_GRADE = "한국사등급미달"
    SECOND_FOREIGN = "제2외국어제한"
    ATTENDANCE = "출석미달"
    OTHER = "기타결격"


# ============================================================
# raw_components 필수 키 (A/B 갭 분석용)
# ============================================================
REQUIRED_RAW_COMPONENT_KEYS: List[str] = [
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


# ============================================================
# 과목 코드 매핑
# ============================================================
SUBJECT_CODES = {
    "국어": "KOR",
    "수학": "MATH",
    "영어": "ENG",
    "한국사": "HIST",
    "물리학I": "PHY1",
    "화학I": "CHEM1",
    "생명과학I": "BIO1",
    "지구과학I": "GEO1",
}


if __name__ == "__main__":
    print("LevelTheory values:")
    for level in LevelTheory:
        print(f"  {level.value}: {level.to_probability_range()}")
    
    print("\nTrack values:")
    for track in Track:
        print(f"  {track.value}")
