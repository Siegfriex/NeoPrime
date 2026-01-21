"""
INDEX/COMPUTE 시트 계산 로직 (엑셀에서 추출)

엑셀의 COMPUTE 시트 Row 59 수식을 Python으로 변환:
=D46*IFERROR(FIND("국",D65)/FIND("국",D65),0)
+D47*IFERROR(FIND("수",D65)/FIND("수",D65),0)
+D48*IFERROR(FIND("영",D65)/FIND("영",D65),0)
+D51*IFERROR(FIND("탐",D65)/FIND("탐",D65),0)
+D57*(한국사 조건)
"""

import logging
from typing import Dict, Optional, List, Tuple
from dataclasses import dataclass

from ..weights import ExtractedWeightLoader, WeightNotFoundError, ConversionNotFoundError

logger = logging.getLogger(__name__)


@dataclass
class SubjectScore:
    """과목별 점수"""
    subject: str           # 과목명 (국어, 수학 등)
    raw_score: float       # 원점수/표준점수
    converted_score: float # 환산점수


@dataclass
class CalculationResult:
    """계산 결과"""
    total_score: float           # 최종 환산점수 합계
    subject_scores: List[SubjectScore]  # 과목별 점수
    required_subjects: str       # 필수과목 문자열 (예: "국수영탐(2)")
    calculation_method: str      # 계산 방식 (필수/선택/가산점형)
    parity_verified: bool        # Parity 검증 여부


class IndexCalculator:
    """INDEX/COMPUTE 시트 계산 로직

    엑셀 COMPUTE 시트의 계산 로직을 Python으로 재현합니다.
    """

    def __init__(self, weight_loader: ExtractedWeightLoader):
        """
        Args:
            weight_loader: 환산점수 테이블 로더
        """
        self.weights = weight_loader

    def calculate(
        self,
        university: str,
        department: str,
        korean_score: float,
        math_score: float,
        english_grade: int,
        inquiry1_score: float,
        inquiry2_score: float,
        history_grade: int,
        required_subjects: str = "국수영탐(2)"
    ) -> CalculationResult:
        """
        대학/학과별 수능 환산점수 계산

        Args:
            university: 대학명
            department: 학과명
            korean_score: 국어 표준점수
            math_score: 수학 표준점수
            english_grade: 영어 등급 (1-9)
            inquiry1_score: 탐구1 표준점수
            inquiry2_score: 탐구2 표준점수
            history_grade: 한국사 등급 (1-9)
            required_subjects: 필수과목 문자열 (예: "국수영탐(2)")

        Returns:
            CalculationResult: 계산 결과
        """
        subject_scores = []
        total = 0.0

        # 1. 국어 환산점수
        if "국" in required_subjects:
            try:
                korean_conv = self.weights.get_converted_score(
                    university, department, "국어", korean_score
                )
                subject_scores.append(SubjectScore("국어", korean_score, korean_conv))
                total += korean_conv
            except (WeightNotFoundError, ConversionNotFoundError) as e:
                logger.warning(f"국어 환산점수 조회 실패: {e}")

        # 2. 수학 환산점수
        if "수" in required_subjects:
            try:
                math_conv = self.weights.get_converted_score(
                    university, department, "수학", math_score
                )
                subject_scores.append(SubjectScore("수학", math_score, math_conv))
                total += math_conv
            except (WeightNotFoundError, ConversionNotFoundError) as e:
                logger.warning(f"수학 환산점수 조회 실패: {e}")

        # 3. 영어 환산점수 (등급 → 환산)
        if "영" in required_subjects:
            try:
                english_conv = self.weights.get_converted_score(
                    university, department, "영어", english_grade
                )
                subject_scores.append(SubjectScore("영어", english_grade, english_conv))
                total += english_conv
            except (WeightNotFoundError, ConversionNotFoundError):
                # 영어는 등급 기반이라 환산점수 없을 수 있음
                logger.debug(f"영어 환산점수 없음 (등급 기반): {english_grade}")

        # 4. 탐구 환산점수
        if "탐" in required_subjects:
            inquiry_count = self._parse_inquiry_count(required_subjects)
            inquiry_scores = sorted([inquiry1_score, inquiry2_score], reverse=True)

            for i, score in enumerate(inquiry_scores[:inquiry_count]):
                try:
                    # 탐구 과목명은 실제로 다양할 수 있음 (물리, 화학 등)
                    # 여기서는 일반화된 "탐구" 사용
                    inquiry_conv = self.weights.get_converted_score(
                        university, department, f"탐구{i+1}", score
                    )
                    subject_scores.append(SubjectScore(f"탐구{i+1}", score, inquiry_conv))
                    total += inquiry_conv
                except (WeightNotFoundError, ConversionNotFoundError):
                    logger.debug(f"탐구{i+1} 환산점수 없음")

        # 5. 한국사 (대부분 가산점 또는 감점)
        # 한국사는 복잡한 조건이 있어 별도 처리 필요

        return CalculationResult(
            total_score=total,
            subject_scores=subject_scores,
            required_subjects=required_subjects,
            calculation_method="필수",
            parity_verified=False
        )

    def _parse_inquiry_count(self, required_subjects: str) -> int:
        """필수과목 문자열에서 탐구 과목 수 추출

        예: "국수영탐(2)" → 2
        """
        import re
        match = re.search(r'\((\d)\)', required_subjects)
        if match:
            return int(match.group(1))
        return 2  # 기본값


class ComputeCalculator:
    """COMPUTE 시트 전체 계산 로직

    Row 3 = Row 58 + Row 59 + Row 60 + Row 61 + Row 62
    """

    def __init__(self, index_calculator: IndexCalculator):
        self.index_calc = index_calculator

    def calculate_final_score(
        self,
        university: str,
        department: str,
        korean_score: float,
        math_score: float,
        english_grade: int,
        inquiry1_score: float,
        inquiry2_score: float,
        history_grade: int,
        required_subjects: str = "국수영탐(2)"
    ) -> Dict:
        """
        COMPUTE Row 3 계산 (최종 환산점수)

        Row 3 = Row 58 (기본점수, 보통 0)
              + Row 59 (수능환산 필수)
              + Row 60 (수능환산 선택, 없으면 0)
              + Row 61 (수능환산 가산점형, 없으면 0)
              + Row 62 (추가점수, 없으면 0)
        """
        result = self.index_calc.calculate(
            university=university,
            department=department,
            korean_score=korean_score,
            math_score=math_score,
            english_grade=english_grade,
            inquiry1_score=inquiry1_score,
            inquiry2_score=inquiry2_score,
            history_grade=history_grade,
            required_subjects=required_subjects
        )

        return {
            "final_score": result.total_score,
            "row_58": 0.0,  # 기본점수
            "row_59": result.total_score,  # 필수 합계
            "row_60": None,  # 선택 (해당시)
            "row_61": None,  # 가산점형 (해당시)
            "row_62": None,  # 추가점수 (해당시)
            "subject_scores": [
                {"subject": s.subject, "raw": s.raw_score, "converted": s.converted_score}
                for s in result.subject_scores
            ],
            "required_subjects": result.required_subjects,
        }
