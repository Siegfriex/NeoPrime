"""
합격 확률 계산 모델

학생 점수와 커트라인 기반 합격 확률 계산
"""

import logging
from typing import Dict, Optional, Tuple
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class ProbabilityResult:
    """확률 계산 결과"""
    probability: float
    level: str
    confidence_low: float
    confidence_high: float


class AdmissionProbabilityModel:
    """합격 확률 계산 모델"""

    # 라인별 기본 확률 범위
    LEVEL_RANGES = {
        "적정": (0.80, 1.00),
        "예상": (0.50, 0.80),
        "소신": (0.20, 0.50),
        "상향": (0.00, 0.20),
    }

    def __init__(self, uncertainty: float = 0.10):
        """
        Args:
            uncertainty: 기본 불확실성 (표준편차)
        """
        self.uncertainty = uncertainty

    def calculate(
        self,
        student_score: float,
        cutoff_safe: Optional[float],
        cutoff_normal: Optional[float],
        cutoff_risk: Optional[float]
    ) -> ProbabilityResult:
        """
        합격 확률 계산

        Args:
            student_score: 학생의 환산점수
            cutoff_safe: 적정 커트라인 (80%)
            cutoff_normal: 예상 커트라인 (50%)
            cutoff_risk: 소신 커트라인 (20%)

        Returns:
            ProbabilityResult
        """
        # 커트라인 없으면 기본값
        if cutoff_normal is None:
            return ProbabilityResult(
                probability=0.50,
                level="알수없음",
                confidence_low=0.30,
                confidence_high=0.70
            )

        # 점수 위치 판정
        if cutoff_safe and student_score >= cutoff_safe:
            # 적정 이상
            prob = self._calc_prob_above(student_score, cutoff_safe, 0.80, 0.99)
            level = "적정"

        elif student_score >= cutoff_normal:
            # 예상 범위
            if cutoff_safe:
                ratio = (student_score - cutoff_normal) / (cutoff_safe - cutoff_normal)
                ratio = min(1.0, max(0.0, ratio))
            else:
                ratio = 0.5
            prob = 0.50 + ratio * 0.30
            level = "예상"

        elif cutoff_risk and student_score >= cutoff_risk:
            # 소신 범위
            ratio = (student_score - cutoff_risk) / (cutoff_normal - cutoff_risk)
            ratio = min(1.0, max(0.0, ratio))
            prob = 0.20 + ratio * 0.30
            level = "소신"

        else:
            # 상향 범위
            if cutoff_risk:
                ratio = max(0, student_score / cutoff_risk) if cutoff_risk > 0 else 0
                prob = ratio * 0.20
            else:
                prob = 0.10
            level = "상향"

        # 확률 범위 제한
        prob = max(0.01, min(0.99, prob))

        # 신뢰구간 (95%)
        ci_low = max(0.00, prob - 1.96 * self.uncertainty)
        ci_high = min(1.00, prob + 1.96 * self.uncertainty)

        return ProbabilityResult(
            probability=round(prob, 4),
            level=level,
            confidence_low=round(ci_low, 4),
            confidence_high=round(ci_high, 4)
        )

    def _calc_prob_above(
        self,
        score: float,
        cutoff: float,
        base_prob: float,
        max_prob: float
    ) -> float:
        """커트라인 이상일 때 확률 계산"""
        excess = score - cutoff
        range_above = cutoff * 0.05  # 5% 여유

        if range_above <= 0:
            return base_prob

        normalized = min(1.0, excess / range_above)
        return base_prob + normalized * (max_prob - base_prob)

    def determine_level(
        self,
        student_score: float,
        cutoff_safe: Optional[float],
        cutoff_normal: Optional[float],
        cutoff_risk: Optional[float]
    ) -> str:
        """합격 라인만 판정"""
        result = self.calculate(student_score, cutoff_safe, cutoff_normal, cutoff_risk)
        return result.level

    def calculate_from_percentile(
        self,
        student_percentile: float,
        target_cutoff_percentile: float = 50.0
    ) -> ProbabilityResult:
        """
        누백 기반 확률 계산 (간단 버전)

        Args:
            student_percentile: 학생의 누적백분위
            target_cutoff_percentile: 목표 커트라인 백분위

        Returns:
            ProbabilityResult
        """
        # 누백이 높을수록 합격 확률 높음
        diff = student_percentile - target_cutoff_percentile

        if diff >= 30:
            prob = 0.90
            level = "적정"
        elif diff >= 0:
            prob = 0.50 + (diff / 30) * 0.40
            level = "예상"
        elif diff >= -30:
            prob = 0.20 + ((diff + 30) / 30) * 0.30
            level = "소신"
        else:
            prob = max(0.05, 0.20 + (diff + 30) / 30 * 0.15)
            level = "상향"

        prob = max(0.01, min(0.99, prob))

        ci_low = max(0.00, prob - 1.96 * self.uncertainty)
        ci_high = min(1.00, prob + 1.96 * self.uncertainty)

        return ProbabilityResult(
            probability=round(prob, 4),
            level=level,
            confidence_low=round(ci_low, 4),
            confidence_high=round(ci_high, 4)
        )


# 테스트 코드
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    model = AdmissionProbabilityModel()

    print("=" * 60)
    print("확률 계산 테스트")
    print("=" * 60)

    # 테스트 케이스
    test_cases = [
        # (student_score, cutoff_safe, cutoff_normal, cutoff_risk, expected_level)
        (98.0, 95.0, 90.0, 85.0, "적정"),
        (92.0, 95.0, 90.0, 85.0, "예상"),
        (87.0, 95.0, 90.0, 85.0, "소신"),
        (80.0, 95.0, 90.0, 85.0, "상향"),
        (70.0, None, None, None, "알수없음"),
    ]

    print("\n점수 기반 확률 계산:")
    passed = 0
    for score, safe, normal, risk, expected in test_cases:
        result = model.calculate(score, safe, normal, risk)
        is_pass = result.level == expected
        status = "PASS" if is_pass else "FAIL"
        if is_pass:
            passed += 1
        print(f"  {status}: score={score}, level={result.level} (expected={expected})")
        print(f"       prob={result.probability:.2%}, CI=[{result.confidence_low:.2%}, {result.confidence_high:.2%}]")

    print(f"\n결과: {passed}/{len(test_cases)} 통과")

    # 누백 기반 테스트
    print("\n누백 기반 확률 계산:")
    percentile_cases = [
        (90.0, 50.0, "적정"),
        (60.0, 50.0, "예상"),
        (35.0, 50.0, "소신"),
        (10.0, 50.0, "상향"),
    ]

    for student_pct, target_pct, expected in percentile_cases:
        result = model.calculate_from_percentile(student_pct, target_pct)
        status = "PASS" if result.level == expected else "FAIL"
        print(f"  {status}: student={student_pct}%, target={target_pct}%, level={result.level} (expected={expected})")
        print(f"       prob={result.probability:.2%}")
