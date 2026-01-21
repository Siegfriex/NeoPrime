"""
탐구과목 이름 퍼지 매칭

사용법:
    matcher = SubjectMatcher()
    canonical, score = matcher.match("물리학I")  # → ("물리학 Ⅰ", 95.0)
"""

import re
from typing import Dict, List, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


class SubjectMatcher:
    """탐구과목 이름 퍼지 매칭"""

    # 표준 과목명 → 별칭 목록
    CANONICAL_SUBJECTS: Dict[str, List[str]] = {
        # === 국어 ===
        "국어(언매)": ["국어언매", "언어와매체", "언매", "국어 언매"],
        "국어(화작)": ["국어화작", "화법과작문", "화작", "국어 화작"],

        # === 수학 ===
        "수학(미적)": ["수학미적", "미적분", "미적", "수학 미적"],
        "수학(기하)": ["수학기하", "기하", "수학 기하"],
        "수학(확통)": ["수학확통", "확률과통계", "확통", "수학 확통"],

        # === 과학탐구 ===
        "물리학 Ⅰ": ["물리학1", "물리학I", "물리1", "물리Ⅰ", "물리 1", "물리학 1", "물리학Ⅰ"],
        "물리학 Ⅱ": ["물리학2", "물리학II", "물리2", "물리Ⅱ", "물리 2", "물리학 2", "물리학Ⅱ"],
        "화학 Ⅰ": ["화학1", "화학I", "화1", "화학Ⅰ", "화학 1"],
        "화학 Ⅱ": ["화학2", "화학II", "화2", "화학Ⅱ", "화학 2"],
        "생명과학 Ⅰ": ["생명과학1", "생명1", "생물1", "생명Ⅰ", "생명과학 1", "생과1", "생명과학Ⅰ"],
        "생명과학 Ⅱ": ["생명과학2", "생명2", "생물2", "생명Ⅱ", "생명과학 2", "생과2", "생명과학Ⅱ"],
        "지구과학 Ⅰ": ["지구과학1", "지구1", "지학1", "지구Ⅰ", "지구과학 1", "지과1", "지구과학Ⅰ"],
        "지구과학 Ⅱ": ["지구과학2", "지구2", "지학2", "지구Ⅱ", "지구과학 2", "지과2", "지구과학Ⅱ"],

        # === 사회탐구 ===
        "생활과 윤리": ["생윤", "생활윤리", "생활과윤리"],
        "윤리와 사상": ["윤사", "윤리사상", "윤리와사상"],
        "한국지리": ["한지"],
        "세계지리": ["세지"],
        "동아시아사": ["동아사", "동아시아"],
        "세계사": ["세사"],
        "경제": [],
        "정치와 법": ["정법", "정치와법"],
        "사회·문화": ["사문", "사회문화", "사회와문화", "사회·문화"],

        # === 제2외국어 ===
        "한문 Ⅰ": ["한문1", "한문I"],
        "일본어 Ⅰ": ["일본어1", "일어1", "일본어I"],
        "일본어 Ⅱ": ["일본어2", "일어2", "일본어II"],
        "중국어 Ⅰ": ["중국어1", "중어1", "중국어I"],
        "중국어 Ⅱ": ["중국어2", "중어2", "중국어II"],
        "프랑스어 Ⅰ": ["프랑스어1", "프랑스어I", "불어1", "불어I"],
        "프랑스어 Ⅱ": ["프랑스어2", "프랑스어II", "불어2", "불어II"],
        "독일어 Ⅰ": ["독일어1", "독일어I", "독어1"],
        "독일어 Ⅱ": ["독일어2", "독일어II", "독어2"],
        "스페인어 Ⅰ": ["스페인어1", "스페인어I", "서반아어1"],
        "스페인어 Ⅱ": ["스페인어2", "스페인어II", "서반아어2"],
        "러시아어 Ⅰ": ["러시아어1", "러시아어I", "노어1"],
        "러시아어 Ⅱ": ["러시아어2", "러시아어II", "노어2"],
        "아랍어 Ⅰ": ["아랍어1", "아랍어I"],
        "아랍어 Ⅱ": ["아랍어2", "아랍어II"],
        "베트남어 Ⅰ": ["베트남어1", "베트남어I", "월남어1"],
        "베트남어 Ⅱ": ["베트남어2", "베트남어II", "월남어2"],
    }

    def __init__(self, threshold: int = 70):
        """
        Args:
            threshold: 매칭 임계값 (0-100)
        """
        self.threshold = threshold
        self._build_reverse_mapping()
        logger.info(f"SubjectMatcher 초기화: {len(self.alias_to_canonical)}개 매핑")

    def _build_reverse_mapping(self):
        """별칭 → 정규 이름 역매핑 구축"""
        self.alias_to_canonical: Dict[str, str] = {}

        for canonical, aliases in self.CANONICAL_SUBJECTS.items():
            # 정규 이름 자체도 매핑
            normalized = self._normalize(canonical)
            self.alias_to_canonical[normalized] = canonical

            # 모든 별칭 매핑
            for alias in aliases:
                normalized_alias = self._normalize(alias)
                self.alias_to_canonical[normalized_alias] = canonical

    def _normalize(self, name: str) -> str:
        """문자열 정규화"""
        if not name:
            return ""

        # 1. 공백 제거
        name = name.replace(" ", "")
        # 2. 로마자 통일 (Ⅰ→1, Ⅱ→2)
        name = name.replace("Ⅰ", "1").replace("Ⅱ", "2")
        name = name.replace("I", "1").replace("II", "2")
        # 3. 소문자 변환
        name = name.lower()
        # 4. 특수문자 제거 (·, (, ) 등)
        name = re.sub(r'[^\w가-힣0-9]', '', name)

        return name

    def match(self, input_name: str) -> Tuple[str, float]:
        """
        입력 과목명 → 정규 과목명 매칭

        Args:
            input_name: 입력 과목명

        Returns:
            (canonical_name, confidence_score)
            - canonical_name: 정규화된 과목명
            - confidence_score: 신뢰도 (0-100)
        """
        if not input_name:
            return input_name, 0.0

        normalized = self._normalize(input_name)

        # 1. 정확한 매칭
        if normalized in self.alias_to_canonical:
            canonical = self.alias_to_canonical[normalized]
            logger.debug(f"정확 매칭: '{input_name}' → '{canonical}'")
            return canonical, 100.0

        # 2. 부분 매칭 (포함 관계)
        for alias, canonical in self.alias_to_canonical.items():
            if normalized in alias or alias in normalized:
                score = len(normalized) / max(len(alias), len(normalized)) * 100
                if score >= self.threshold:
                    logger.debug(f"부분 매칭: '{input_name}' → '{canonical}' (score={score:.1f})")
                    return canonical, score

        # 3. 레벤슈타인 거리 기반 매칭 (간단 구현)
        best_match = None
        best_score = 0.0

        for alias, canonical in self.alias_to_canonical.items():
            score = self._similarity_score(normalized, alias)
            if score > best_score:
                best_score = score
                best_match = canonical

        if best_match and best_score >= self.threshold:
            logger.debug(f"유사 매칭: '{input_name}' → '{best_match}' (score={best_score:.1f})")
            return best_match, best_score

        # 4. 매칭 실패 - 원본 반환
        logger.debug(f"매칭 실패: '{input_name}'")
        return input_name, 0.0

    def _similarity_score(self, s1: str, s2: str) -> float:
        """두 문자열 유사도 (0-100)"""
        if not s1 or not s2:
            return 0.0

        # 공통 문자 비율
        common = set(s1) & set(s2)
        total = set(s1) | set(s2)

        if not total:
            return 0.0

        return len(common) / len(total) * 100

    def get_all_canonical_names(self) -> List[str]:
        """모든 정규 과목명 반환"""
        return list(self.CANONICAL_SUBJECTS.keys())

    def get_aliases(self, canonical_name: str) -> List[str]:
        """정규 과목명의 모든 별칭 반환"""
        return self.CANONICAL_SUBJECTS.get(canonical_name, [])


# 테스트 코드
if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)

    matcher = SubjectMatcher()

    test_cases = [
        ("물리학I", "물리학 Ⅰ"),
        ("물리학 Ⅰ", "물리학 Ⅰ"),
        ("화학1", "화학 Ⅰ"),
        ("생윤", "생활과 윤리"),
        ("수학(미적)", "수학(미적)"),
        ("국어(언매)", "국어(언매)"),
        ("생명과학 Ⅰ", "생명과학 Ⅰ"),
        ("지구과학2", "지구과학 Ⅱ"),
        ("사문", "사회·문화"),
        ("윤사", "윤리와 사상"),
    ]

    print("\n" + "="*60)
    print("과목 매칭 테스트")
    print("="*60)

    passed = 0
    for input_name, expected in test_cases:
        canonical, score = matcher.match(input_name)
        is_match = canonical == expected
        status = "PASS" if is_match else "FAIL"
        if is_match:
            passed += 1
        print(f"  {status}: '{input_name}' → '{canonical}' (expected: '{expected}', score={score:.1f})")

    print(f"\n결과: {passed}/{len(test_cases)} 통과 ({passed/len(test_cases)*100:.0f}%)")
