"""
결격 사유 체크 엔진

RESTRICT 시트 기반 결격 룰 적용
"""

import re
import logging
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass, field

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from theory_engine.constants import DisqualificationCode
from theory_engine.model import StudentProfile, TargetProgram, DisqualificationInfo
from theory_engine.cutoff import CutoffExtractor

logger = logging.getLogger(__name__)


@dataclass
class DisqualificationRule:
    """결격 사유 룰"""
    rule_id: str
    description: str
    university_pattern: str  # 대학명 패턴 (regex)
    check_func: Callable[[Any, Any], bool]  # (profile, target) → bool
    code: DisqualificationCode
    message_template: str
    severity: int = 1  # 1=경고, 2=심각


class DisqualificationEngine:
    """결격 사유 체크 엔진"""

    # 과학탐구 과목 목록
    SCIENCE_SUBJECTS = ["물리학", "화학", "생명과학", "지구과학"]

    # 사회탐구 과목 목록
    SOCIAL_SUBJECTS = ["생활과 윤리", "윤리와 사상", "한국지리", "세계지리",
                       "동아시아사", "세계사", "경제", "정치와 법", "사회·문화"]

    # 의료계열 키워드 (⚠️ "의" 단일 포함 금지)
    # - 정규화(공백/특수문자 제거 + 소문자) 후 정확/접두사 매칭만 허용
    MEDICAL_MAJOR_KEYWORDS = {
        # 의대
        "의예", "의예과", "의학", "의대",
        # 약대
        "약학", "약대",
        # 치대
        "치의예", "치의예과", "치의학", "치대",
        # 한의대
        "한의예", "한의예과", "한의학", "한의대",
        # 수의대
        "수의예", "수의예과", "수의학", "수의대",
        # 간호
        "간호", "간호학", "간호학과",
    }

    def __init__(self):
        """엔진 초기화 및 룰 로드"""
        # 대학 Alias 역매핑 구축 (CutoffExtractor의 정적 데이터 재사용)
        CutoffExtractor._build_alias_reverse_map()
        self.rules: List[DisqualificationRule] = []
        self._load_rules()
        logger.info(f"결격 체크 엔진 초기화: {len(self.rules)}개 룰")

    def _normalize_university(self, name: str) -> str:
        """CutoffExtractor의 대학명 정규화 로직 재사용"""
        return CutoffExtractor._normalize_university(name)

    def _get_official_university(self, name: str) -> str:
        """별칭 → 공식 대학명 변환 (부분매칭 금지: 오매핑 방지)"""
        normalized = self._normalize_university(name)
        return CutoffExtractor.ALIAS_TO_OFFICIAL.get(normalized, name)

    @staticmethod
    def _normalize_major(major: str) -> str:
        """전공명 정규화 (공백/특수문자 제거)"""
        if not major:
            return ""
        major = str(major).strip()
        major = re.sub(r"\s+", "", major)
        major = re.sub(r"[·\-_()]", "", major)
        return major.lower()

    def _is_medical_major(self, major: str) -> bool:
        """
        의료계열 전공 판정 (정확/접두사 매칭)

        ⚠️ HIGH 갭 대응:
        - 기존: "의" 단일 포함 → "의류학" 등 오탐 가능
        - 수정: 명시 키워드만 허용 + 전공 Alias 체인 적용
        """
        major_raw = str(major or "").strip()
        if not major_raw:
            return False

        major_compact = re.sub(r"\s+", "", major_raw)

        # 전공 Alias 체인 적용 (의예 → 의학 등)
        aliases = (
            CutoffExtractor.MAJOR_ALIASES.get(major_raw)
            or CutoffExtractor.MAJOR_ALIASES.get(major_compact)
            or []
        )

        candidates = [major_raw, major_compact] + list(aliases)
        normalized_candidates = [self._normalize_major(c) for c in candidates if c]

        for cand in normalized_candidates:
            for kw in self.MEDICAL_MAJOR_KEYWORDS:
                kw_norm = self._normalize_major(kw)
                if cand == kw_norm or cand.startswith(kw_norm):
                    return True

        return False

    def _load_rules(self):
        """결격 룰 로드"""

        # ===== 영어 등급 제한 =====
        self.rules.append(DisqualificationRule(
            rule_id="ENG_GRADE_001",
            description="영어 3등급 초과 제한 (일반)",
            university_pattern=r".*",
            check_func=lambda p, t: p.english_grade > 3,
            code=DisqualificationCode.ENGLISH_GRADE,
            message_template="영어 {grade}등급: 대부분 대학은 3등급 이내 필수",
            severity=2
        ))

        self.rules.append(DisqualificationRule(
            rule_id="ENG_GRADE_002",
            description="영어 2등급 초과 제한 (상위권)",
            university_pattern=r"서울대|연세대|고려대|성균관|한양대|중앙대|경희대|이화여대",
            check_func=lambda p, t: p.english_grade > 2,
            code=DisqualificationCode.ENGLISH_GRADE,
            message_template="영어 {grade}등급: {university}는 2등급 이내 권장",
            severity=1
        ))

        # ===== 한국사 등급 제한 =====
        self.rules.append(DisqualificationRule(
            rule_id="HIST_GRADE_001",
            description="한국사 4등급 초과 제한",
            university_pattern=r".*",
            check_func=lambda p, t: p.history_grade > 4,
            code=DisqualificationCode.HISTORY_GRADE,
            message_template="한국사 {history_grade}등급: 대부분 대학은 4등급 이내 필수",
            severity=2
        ))

        # ===== 수학 선택과목 제한 =====
        self.rules.append(DisqualificationRule(
            rule_id="MATH_SUBJ_001",
            description="이과 미적분/기하 필수",
            university_pattern=r"서울대|연세대|고려대|성균관|한양대|KAIST|포항공대",
            check_func=lambda p, t: (
                p.track.value == "이과" and
                p.math.subject not in ["수학(미적)", "수학(기하)", "미적분", "기하"]
            ),
            code=DisqualificationCode.MATH_SUBJECT,
            message_template="{university} 이과: 미적분/기하 필수",
            severity=2
        ))

        # ===== 탐구과목 제한 (의대) =====
        self.rules.append(DisqualificationRule(
            rule_id="INQ_SUBJ_001",
            description="의대 과탐 2과목 필수",
            university_pattern=r".*",
            check_func=lambda p, t: self._check_medical_inquiry(p, t),
            code=DisqualificationCode.INQUIRY_SUBJECT,
            message_template="{university} {major}: 과학탐구 2과목 필수",
            severity=2
        ))

        # ===== 탐구 조합 제한 (서울대) =====
        self.rules.append(DisqualificationRule(
            rule_id="INQ_COMBO_001",
            description="서울대 동일과목군 I+I 불가",
            university_pattern=r"서울대",
            check_func=lambda p, t: self._check_same_subject_combo(p),
            code=DisqualificationCode.INQUIRY_COMBINATION,
            message_template="서울대: 동일 과목군 Ⅰ+Ⅰ 조합 불가",
            severity=2
        ))

    def _check_medical_inquiry(self, profile: StudentProfile, target: TargetProgram) -> bool:
        """의대/약대 과탐 2과목 필수 체크"""
        if not self._is_medical_major(target.major):
            return False

        inq1 = profile.inquiry1.subject if profile.inquiry1 else ""
        inq2 = profile.inquiry2.subject if profile.inquiry2 else ""

        is_science1 = any(s in inq1 for s in self.SCIENCE_SUBJECTS)
        is_science2 = any(s in inq2 for s in self.SCIENCE_SUBJECTS)

        return not (is_science1 and is_science2)

    def _check_same_subject_combo(self, profile: StudentProfile) -> bool:
        """동일 과목군 I+I 조합 체크"""
        inq1 = profile.inquiry1.subject if profile.inquiry1 else ""
        inq2 = profile.inquiry2.subject if profile.inquiry2 else ""

        cat1 = self._get_subject_category(inq1)
        cat2 = self._get_subject_category(inq2)

        has_level1_1 = "Ⅰ" in inq1 or "1" in inq1 or "I" in inq1
        has_level1_2 = "Ⅱ" not in inq2 and ("Ⅰ" in inq2 or "1" in inq2 or "I" in inq2)

        return cat1 == cat2 and has_level1_1 and has_level1_2

    def _is_science(self, subject: str) -> bool:
        """과학탐구 과목 여부"""
        return any(s in subject for s in self.SCIENCE_SUBJECTS)

    def _get_subject_category(self, subject: str) -> str:
        """탐구 과목 카테고리"""
        for cat in self.SCIENCE_SUBJECTS + self.SOCIAL_SUBJECTS:
            if cat in subject:
                return cat.split()[0]  # "물리학", "화학" 등
        return "기타"

    def check(
        self,
        profile: StudentProfile,
        target: TargetProgram,
        severity_threshold: int = 1
    ) -> DisqualificationInfo:
        """
        결격 사유 체크

        Args:
            profile: 학생 프로필
            target: 지원 대학/전형
            severity_threshold: 이 심각도 이상만 결격 처리 (1=경고 포함, 2=심각만)

        Returns:
            DisqualificationInfo
        """
        triggered_rules: List[DisqualificationRule] = []
        official_university = self._get_official_university(target.university)

        for rule in self.rules:
            # 대학 패턴 매칭
            if not re.search(rule.university_pattern, official_university, re.IGNORECASE):
                if not re.search(rule.university_pattern, target.major, re.IGNORECASE):
                    if rule.university_pattern != r".*":
                        continue

            # 조건 체크
            try:
                if rule.check_func(profile, target):
                    if rule.severity >= severity_threshold:
                        triggered_rules.append(rule)
                        logger.debug(f"룰 트리거: {rule.rule_id} - {rule.description}")
            except Exception as e:
                logger.warning(f"룰 {rule.rule_id} 평가 실패: {e}")

        if triggered_rules:
            # 가장 심각한 룰 선택
            triggered_rules.sort(key=lambda r: r.severity, reverse=True)
            primary = triggered_rules[0]

            message = primary.message_template.format(
                university=official_university,
                major=target.major,
                grade=profile.english_grade,
                history_grade=profile.history_grade,
            )

            return DisqualificationInfo(
                is_disqualified=True,
                reason=message,
                code=primary.code,
                rules_triggered=[r.rule_id for r in triggered_rules]
            )

        return DisqualificationInfo(is_disqualified=False)

    def get_all_rules(self) -> List[Dict]:
        """모든 룰 목록"""
        return [
            {
                "rule_id": r.rule_id,
                "description": r.description,
                "severity": r.severity,
                "code": r.code.value,
            }
            for r in self.rules
        ]


# 테스트 코드
if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)

    from theory_engine.model import ExamScore
    from theory_engine.constants import Track

    print("=" * 60)
    print("결격 체크 테스트")
    print("=" * 60)

    engine = DisqualificationEngine()
    print(f"\n로드된 룰: {len(engine.rules)}개")

    # 정상 프로필
    normal_profile = StudentProfile(
        track=Track.SCIENCE,
        korean=ExamScore(subject="국어(언매)", raw_total=80),
        math=ExamScore(subject="수학(미적)", raw_total=75),
        english_grade=2,
        history_grade=3,
        inquiry1=ExamScore(subject="물리학 Ⅰ", raw_total=50),
        inquiry2=ExamScore(subject="화학 Ⅰ", raw_total=48),
    )

    # 결격 프로필 (영어 4등급)
    disqualified_profile = StudentProfile(
        track=Track.SCIENCE,
        korean=ExamScore(subject="국어(언매)", raw_total=80),
        math=ExamScore(subject="수학(미적)", raw_total=75),
        english_grade=4,  # 결격!
        history_grade=3,
        inquiry1=ExamScore(subject="물리학 Ⅰ", raw_total=50),
        inquiry2=ExamScore(subject="화학 Ⅰ", raw_total=48),
    )

    # 테스트 케이스
    test_cases = [
        (normal_profile, TargetProgram("서울대", "공대"), False, "정상 프로필"),
        (disqualified_profile, TargetProgram("서울대", "공대"), True, "영어 4등급"),
    ]

    print("\n테스트 결과:")
    passed = 0
    for profile, target, expected_disqual, desc in test_cases:
        result = engine.check(profile, target, severity_threshold=2)
        is_pass = result.is_disqualified == expected_disqual
        status = "PASS" if is_pass else "FAIL"
        if is_pass:
            passed += 1

        disqual_status = "결격" if result.is_disqualified else "통과"
        print(f"  {status}: {desc} → {disqual_status}")
        if result.is_disqualified:
            print(f"       사유: {result.reason}")
            print(f"       룰: {result.rules_triggered}")

    print(f"\n결과: {passed}/{len(test_cases)} 통과")
