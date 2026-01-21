"""
INDEX 조회 실패 시 RAWSCORE 누적% 폴백 계산

INDEX 시트가 인코딩된 해시 키를 사용하여 직접 조회가 불가능할 때,
RAWSCORE에서 추출한 누적%를 가중 평균하여 대체 누적백분위를 계산합니다.

[2026-01-21 수정] DEFAULT_WEIGHTS 제거
- SSOT 문서(AGENT_PROMPT_엑셀_가중치_추출.md)에 따라 하드코딩된 가중치 제거
- 임의 가중치 사용 금지 → 엑셀에서 추출한 실제 값만 사용
- 가중치가 필요하면 ExtractedWeightLoader 사용
"""

import logging
from typing import Dict, Optional, List

logger = logging.getLogger(__name__)


class WeightNotProvidedError(Exception):
    """가중치 미제공 오류 - 하드코딩된 DEFAULT_WEIGHTS 사용 금지"""
    pass


class IndexFallback:
    """INDEX 조회 우회 계산기

    [주의] DEFAULT_WEIGHTS가 제거되었습니다.
    가중치가 필요한 경우 반드시 weights 파라미터로 명시적으로 전달해야 합니다.
    엑셀에서 추출한 실제 가중치를 사용하려면 ExtractedWeightLoader를 사용하세요.
    """

    # [제거됨] 하드코딩된 가중치는 사용하지 않습니다.
    # DEFAULT_WEIGHTS = {...}  # SSOT 문서에 따라 제거됨

    # 영어 등급 → 백분위 변환 테이블
    GRADE_TO_PERCENTILE = {
        1: 4.0,    # 상위 4%
        2: 11.0,   # 상위 11%
        3: 23.0,   # 상위 23%
        4: 40.0,   # 상위 40%
        5: 60.0,   # 상위 60%
        6: 77.0,   # 상위 77%
        7: 89.0,   # 상위 89%
        8: 96.0,   # 상위 96%
        9: 100.0,  # 상위 100%
    }

    def __init__(self, weights: Optional[Dict[str, float]] = None):
        """
        Args:
            weights: 과목별 가중치 딕셔너리 (필수)
                    예: {"korean": 0.28, "math": 0.28, ...}

        Raises:
            WeightNotProvidedError: 가중치가 제공되지 않은 경우
        """
        if weights is None:
            raise WeightNotProvidedError(
                "가중치가 제공되지 않았습니다.\n"
                "해결 방법:\n"
                "  1. weights 파라미터에 명시적으로 가중치 전달\n"
                "  2. ExtractedWeightLoader를 사용하여 엑셀에서 추출한 가중치 사용\n"
                "  3. 임의 가중치(DEFAULT_WEIGHTS) 사용 금지 - SSOT 정책"
            )
        self.weights = weights

    def calculate_from_rawscore(
        self,
        korean_conv: Dict,
        math_conv: Dict,
        inq1_conv: Dict,
        inq2_conv: Dict,
        english_grade: int = 1,
        method: str = "weighted"
    ) -> Dict:
        """
        RAWSCORE 누적% 합산으로 INDEX 대체

        Args:
            korean_conv: convert_raw_to_standard() 결과
            math_conv: convert_raw_to_standard() 결과
            inq1_conv: convert_raw_to_standard() 결과
            inq2_conv: convert_raw_to_standard() 결과
            english_grade: 영어 등급 (1-9)
            method: "weighted" | "simple" | "geometric"

        Returns:
            {
                "found": True,
                "match_type": "fallback_rawscore_weighted",
                "cumulative_pct": 5.2,
                "percentile_sum": 356.5,
                "national_rank": 26000,
                "confidence": 0.85,
                "subjects_used": ["korean", "math", ...]
            }
        """
        # 각 과목 누적%/백분위 추출
        conversions = {
            "korean": korean_conv,
            "math": math_conv,
            "inquiry1": inq1_conv,
            "inquiry2": inq2_conv,
        }

        pcts = {}
        for key, conv in conversions.items():
            if conv and conv.get("found"):
                # 누적% 우선, 없으면 백분위 사용
                pct = conv.get("cumulative_pct")
                if pct is None:
                    pct = conv.get("percentile")
                if pct is not None:
                    try:
                        pcts[key] = float(pct)
                    except (ValueError, TypeError):
                        pass

        # 영어 등급 → 백분위 변환
        english_pct = self._grade_to_percentile(english_grade)
        if english_pct is not None:
            pcts["english"] = english_pct

        if not pcts:
            logger.warning("유효한 누적% 데이터 없음")
            return {
                "found": False,
                "match_type": "fallback_failed",
                "cumulative_pct": None,
                "percentile_sum": None,
                "national_rank": None,
                "confidence": 0.0,
                "subjects_used": [],
            }

        logger.info(f"INDEX 폴백: {len(pcts)}개 과목 사용 - {list(pcts.keys())}")

        # 방법별 계산
        if method == "weighted":
            cumulative_pct = self._weighted_average(pcts)
            match_type = "fallback_rawscore_weighted"
        elif method == "simple":
            cumulative_pct = sum(pcts.values()) / len(pcts)
            match_type = "fallback_rawscore_simple"
        elif method == "geometric":
            import math
            product = 1.0
            for pct in pcts.values():
                product *= max(pct, 0.01) / 100
            cumulative_pct = (product ** (1 / len(pcts))) * 100
            match_type = "fallback_rawscore_geometric"
        else:
            cumulative_pct = self._weighted_average(pcts)
            match_type = "fallback_rawscore_weighted"

        # 백분위 합산 (단순 합계 - 참고용)
        percentile_sum = sum(pcts.values())

        # 전국 등수 추정 (50만명 기준)
        national_rank = self._estimate_national_rank(cumulative_pct)

        # 신뢰도 계산 (사용된 과목 수 기반)
        confidence = len(pcts) / 5.0  # 5과목 기준

        return {
            "found": True,
            "match_type": match_type,
            "cumulative_pct": round(cumulative_pct, 2),
            "percentile_sum": round(percentile_sum, 2),
            "national_rank": national_rank,
            "confidence": round(confidence, 2),
            "subjects_used": list(pcts.keys()),
        }

    def _weighted_average(self, pcts: Dict[str, float]) -> float:
        """가중 평균 계산

        Raises:
            KeyError: 가중치 키가 등록되지 않은 경우
            ValueError: 유효한 과목 가중치가 없는 경우 (total_weight=0)
        """
        total_weight = 0.0
        weighted_sum = 0.0

        for key, pct in pcts.items():
            # Phase 2: 숨은 기본값 제거 - 명시적 예외 발생
            if key not in self.weights:
                raise KeyError(
                    f"가중치 키 '{key}' 미등록. 등록된 키: {list(self.weights.keys())}"
                )
            weight = self.weights[key]
            weighted_sum += pct * weight
            total_weight += weight

        if total_weight == 0:
            # Phase 2: 숨은 폴백값 제거 - 명시적 예외 발생
            raise ValueError("total_weight=0: 유효한 과목 가중치가 없습니다")

        return weighted_sum / total_weight

    def _grade_to_percentile(self, grade: int) -> Optional[float]:
        """등급 → 백분위 변환"""
        return self.GRADE_TO_PERCENTILE.get(grade)

    def _estimate_national_rank(
        self,
        cumulative_pct: float,
        total_students: int = 500000
    ) -> int:
        """누적백분위 → 전국 등수 추정"""
        # cumulative_pct가 낮을수록 상위권
        rank = int((cumulative_pct / 100.0) * total_students)
        return max(1, rank)


# 싱글톤
_index_fallback: Optional[IndexFallback] = None


def get_index_fallback(weights: Optional[Dict[str, float]] = None) -> IndexFallback:
    """IndexFallback 싱글톤

    Args:
        weights: 과목별 가중치 딕셔너리 (첫 호출 시 필수)

    Raises:
        WeightNotProvidedError: 첫 호출 시 가중치가 제공되지 않은 경우

    Note:
        기존 코드가 get_index_fallback()을 가중치 없이 호출하면
        명시적으로 WeightNotProvidedError가 발생합니다.
        이는 SSOT 정책에 따른 의도된 동작입니다.
    """
    global _index_fallback
    if _index_fallback is None:
        _index_fallback = IndexFallback(weights=weights)
    return _index_fallback
