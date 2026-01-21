"""
Excel에서 추출한 실제 환산점수 테이블 로더

중요: DEFAULT_WEIGHTS 같은 임의 폴백 사용 금지!
환산점수가 없으면 명시적으로 WeightNotFoundError 발생

Phase 2 추가:
- 탐구 과목명 정규화 기능 (_normalize_inquiry_subject)
- "물리학1" → "물리학 Ⅰ" 등 별칭 매핑
"""

import json
import logging
import re
from pathlib import Path
from typing import Dict, Optional, Any, List

logger = logging.getLogger(__name__)


# 탐구 과목명 정규화 매핑 (Phase 2)
# key: 정규화된 이름, value: 별칭 리스트
INQUIRY_SUBJECT_ALIASES: Dict[str, List[str]] = {
    # 과학탐구
    "물리학 Ⅰ": ["물리학1", "물리1", "물리 I", "물리학I", "물리Ⅰ", "물리 1", "Physics I"],
    "물리학 Ⅱ": ["물리학2", "물리2", "물리 II", "물리학II", "물리Ⅱ", "물리 2", "Physics II"],
    "화학 Ⅰ": ["화학1", "화학 I", "화학I", "화학Ⅰ", "화학 1", "Chemistry I"],
    "화학 Ⅱ": ["화학2", "화학 II", "화학II", "화학Ⅱ", "화학 2", "Chemistry II"],
    "생명과학 Ⅰ": ["생명과학1", "생명1", "생명 I", "생명과학I", "생명Ⅰ", "생명 1", "Biology I"],
    "생명과학 Ⅱ": ["생명과학2", "생명2", "생명 II", "생명과학II", "생명Ⅱ", "생명 2", "Biology II"],
    "지구과학 Ⅰ": ["지구과학1", "지구1", "지구 I", "지구과학I", "지구Ⅰ", "지구 1", "Earth Science I"],
    "지구과학 Ⅱ": ["지구과학2", "지구2", "지구 II", "지구과학II", "지구Ⅱ", "지구 2", "Earth Science II"],

    # 사회탐구
    "생활과 윤리": ["생활과윤리", "생윤", "생활윤리"],
    "윤리와 사상": ["윤리와사상", "윤사", "윤리사상"],
    "한국지리": ["한국 지리", "한지"],
    "세계지리": ["세계 지리", "세지"],
    "동아시아사": ["동아시아 사", "동아사"],
    "세계사": ["세계 사"],
    "경제": [],
    "정치와 법": ["정치와법", "정법", "정치법"],
    "사회문화": ["사회 문화", "사문", "사회·문화"],

    # 제2외국어/한문
    "한문 Ⅰ": ["한문1", "한문I", "한문 I"],
}

# 역방향 매핑 (별칭 → 정규화된 이름) - 런타임에 빌드
_ALIAS_TO_NORMALIZED: Dict[str, str] = {}


def _build_alias_map():
    """별칭 → 정규화된 이름 역방향 매핑 빌드"""
    global _ALIAS_TO_NORMALIZED
    if _ALIAS_TO_NORMALIZED:
        return

    for normalized, aliases in INQUIRY_SUBJECT_ALIASES.items():
        _ALIAS_TO_NORMALIZED[normalized] = normalized  # 정규화된 이름 자체도 매핑
        _ALIAS_TO_NORMALIZED[normalized.replace(" ", "")] = normalized  # 공백 제거 버전
        for alias in aliases:
            _ALIAS_TO_NORMALIZED[alias] = normalized
            _ALIAS_TO_NORMALIZED[alias.replace(" ", "")] = normalized


def normalize_inquiry_subject(subject: str) -> str:
    """탐구 과목명 정규화

    Args:
        subject: 원본 과목명 (예: "물리학1", "물리 I", "물리학 Ⅰ")

    Returns:
        정규화된 과목명 (예: "물리학 Ⅰ")
    """
    _build_alias_map()

    # 1. 직접 매핑 확인
    if subject in _ALIAS_TO_NORMALIZED:
        return _ALIAS_TO_NORMALIZED[subject]

    # 2. 공백 제거 후 확인
    subject_no_space = subject.replace(" ", "")
    if subject_no_space in _ALIAS_TO_NORMALIZED:
        return _ALIAS_TO_NORMALIZED[subject_no_space]

    # 3. 아라비아 숫자 → 로마 숫자 변환 시도
    subject_roman = _convert_arabic_to_roman(subject)
    if subject_roman in _ALIAS_TO_NORMALIZED:
        return _ALIAS_TO_NORMALIZED[subject_roman]

    # 4. 매핑 실패 - 원본 반환 (경고 로그)
    logger.warning(f"탐구 과목명 정규화 실패: '{subject}' - 원본 사용")
    return subject


def _convert_arabic_to_roman(text: str) -> str:
    """아라비아 숫자 → 로마 숫자 변환

    예: "물리학1" → "물리학 Ⅰ", "화학2" → "화학 Ⅱ"
    """
    # 숫자 1,2 → 로마 숫자 변환
    text = re.sub(r'(\S)1$', r'\1 Ⅰ', text)
    text = re.sub(r'(\S)2$', r'\1 Ⅱ', text)
    text = re.sub(r'(\S) 1$', r'\1 Ⅰ', text)
    text = re.sub(r'(\S) 2$', r'\1 Ⅱ', text)
    return text


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
        raw_score: float,
        normalize_inquiry: bool = True
    ) -> float:
        """대학/학과별 환산점수 조회

        Args:
            university: 대학명 (예: "가천대학교")
            department: 학과명 (예: "가천대학교")
            subject: 과목명 (예: "국어", "물리학1", "물리학 Ⅰ")
            raw_score: 원점수/표준점수 (예: 124)
            normalize_inquiry: 탐구 과목명 정규화 여부 (기본 True)

        Returns:
            환산점수 (예: 88.0)

        Raises:
            WeightNotFoundError: 해당 대학/학과가 등록되지 않은 경우
            ConversionNotFoundError: 해당 과목/점수 조합이 없는 경우

        Phase 2 추가:
            - 탐구 과목명 정규화 지원 ("물리학1" → "물리학 Ⅰ")
            - 정규화 실패 시 원본 이름으로 조회 시도
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

        # Phase 2: 탐구 과목명 정규화 시도
        original_subject = subject
        if normalize_inquiry and subject not in ["국어", "수학", "영어", "한국사"]:
            subject = normalize_inquiry_subject(subject)

        # 과목-점수 키 생성 (예: "국어-124", "물리학 Ⅰ-65")
        score_key = f"{subject}-{int(raw_score)}"

        if score_key not in conversions:
            # 정규화된 이름으로 못 찾으면 원본으로 재시도
            if subject != original_subject:
                original_key = f"{original_subject}-{int(raw_score)}"
                if original_key in conversions:
                    return float(conversions[original_key])

            raise ConversionNotFoundError(
                f"환산점수 없음: {score_key} (대학: {key})\n"
                f"원본 과목명: {original_subject}, 정규화: {subject}\n"
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
