"""
Excel에서 추출한 실제 환산점수 테이블 로더

중요: DEFAULT_WEIGHTS 같은 임의 폴백 사용 금지!
환산점수가 없으면 명시적으로 WeightNotFoundError 발생
"""

import json
import logging
from pathlib import Path
from typing import Dict, Optional, Any

logger = logging.getLogger(__name__)


class WeightNotFoundError(Exception):
    """환산점수 미등록 오류 - Fallback 사용 금지, 명시적 오류 발생"""
    pass


class ConversionNotFoundError(Exception):
    """환산점수 조회 실패 - 해당 과목/점수 조합이 테이블에 없음"""
    pass


class ExtractedWeightLoader:
    """엑셀 SUBJECT3에서 추출한 실제 환산점수 테이블 로더

    중요:
    - DEFAULT_WEIGHTS 같은 임의 폴백 사용 금지!
    - 환산점수가 없으면 명시적으로 에러 발생
    - 모든 값은 엑셀에서 직접 추출된 것만 사용
    """

    def __init__(self, conversion_file: Optional[str] = None):
        """
        Args:
            conversion_file: subject3_conversions.json 경로
                           None이면 기본 경로 사용
        """
        if conversion_file is None:
            conversion_file = Path(__file__).parent / "subject3_conversions.json"

        self._load_conversions(conversion_file)

    def _load_conversions(self, file_path: str):
        """환산점수 테이블 로드"""
        file_path = Path(file_path)

        if not file_path.exists():
            raise FileNotFoundError(
                f"환산점수 테이블 파일 없음: {file_path}\n"
                f"해결 방법: 엑셀에서 SUBJECT3 테이블 추출 필요"
            )

        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        self._metadata = data.get('metadata', {})
        self._university_mapping = data.get('university_mapping', {})
        self._conversion_table = data.get('conversion_table', {})

        logger.info(
            f"환산점수 테이블 로드: {len(self._conversion_table)}개 대학/학과, "
            f"출처: {self._metadata.get('source_excel', 'unknown')}"
        )

    def get_converted_score(
        self,
        university: str,
        department: str,
        subject: str,
        raw_score: float
    ) -> float:
        """대학/학과별 환산점수 조회

        Args:
            university: 대학명 (예: "가천대학교")
            department: 학과명 (예: "가천대학교")
            subject: 과목명 (예: "국어")
            raw_score: 원점수/표준점수 (예: 124)

        Returns:
            환산점수 (예: 88.0)

        Raises:
            WeightNotFoundError: 해당 대학/학과가 등록되지 않은 경우
            ConversionNotFoundError: 해당 과목/점수 조합이 없는 경우
        """
        # 대학/학과 키 생성
        key = f"{university}_{department}"

        if key not in self._conversion_table:
            raise WeightNotFoundError(
                f"대학/학과 미등록: {key}\n"
                f"등록된 대학/학과: {list(self._conversion_table.keys())[:10]}...\n"
                f"해결 방법: 엑셀에서 해당 대학 환산점수 추출 필요"
            )

        table = self._conversion_table[key]
        conversions = table.get('conversions', {})

        # 과목-점수 키 생성 (예: "국어-124")
        score_key = f"{subject}-{int(raw_score)}"

        if score_key not in conversions:
            raise ConversionNotFoundError(
                f"환산점수 없음: {score_key} (대학: {key})\n"
                f"해결 방법: SUBJECT3 테이블에서 해당 과목/점수 확인 필요"
            )

        return float(conversions[score_key])

    def get_university_info(self, university: str, department: str) -> Dict[str, Any]:
        """대학/학과 정보 조회"""
        key = f"{university}_{department}"

        if key not in self._conversion_table:
            raise WeightNotFoundError(f"대학/학과 미등록: {key}")

        return self._conversion_table[key]

    def list_available_programs(self) -> list:
        """등록된 대학/학과 목록 반환"""
        return list(self._conversion_table.keys())

    def get_metadata(self) -> dict:
        """추출 메타데이터 반환 (출처, 날짜 등)"""
        return self._metadata


# 싱글톤
_weight_loader: Optional[ExtractedWeightLoader] = None


def get_weight_loader() -> ExtractedWeightLoader:
    """ExtractedWeightLoader 싱글톤"""
    global _weight_loader
    if _weight_loader is None:
        _weight_loader = ExtractedWeightLoader()
    return _weight_loader
