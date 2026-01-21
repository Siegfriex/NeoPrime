"""
Theory Engine v3 E2E 통합 테스트

전체 파이프라인 테스트:
1. 과목명 매칭 (SubjectMatcher)
2. INDEX 조회 (IndexOptimizer)
3. 커트라인 추출 (CutoffExtractor)
4. 확률 계산 (AdmissionProbabilityModel)
5. 결격 체크 (DisqualificationEngine)
6. 전체 파이프라인 (compute_theory_result)
"""

import pytest
import sys
from pathlib import Path

# 프로젝트 루트 추가
sys.path.insert(0, str(Path(__file__).parent.parent))

from theory_engine.matchers import SubjectMatcher
from theory_engine.optimizers import IndexOptimizer
from theory_engine.cutoff import CutoffExtractor
from theory_engine.probability import AdmissionProbabilityModel
from theory_engine.disqualification import DisqualificationEngine
from theory_engine.model import StudentProfile, TargetProgram, ExamScore
from theory_engine.constants import Track, LevelTheory


class TestSubjectMatcher:
    """과목명 매칭 테스트"""

    def setup_method(self):
        self.matcher = SubjectMatcher()

    def test_exact_match(self):
        """정확한 과목명 매칭"""
        name, conf = self.matcher.match("물리학 Ⅰ")
        assert name == "물리학 Ⅰ"
        assert conf >= 90.0  # 백분율 스케일 (0-100)

    def test_roman_numeral_normalization(self):
        """로마숫자 정규화 매칭"""
        test_cases = [
            ("물리학I", "물리학 Ⅰ"),
            ("물리학1", "물리학 Ⅰ"),
            ("화학II", "화학 Ⅱ"),
            ("화학2", "화학 Ⅱ"),
        ]
        for input_name, expected in test_cases:
            name, conf = self.matcher.match(input_name)
            assert name == expected, f"{input_name} → {name} (expected {expected})"
            assert conf >= 90.0  # 백분율 스케일

    def test_korean_subject_variants(self):
        """국어/수학 선택과목 매칭"""
        test_cases = [
            # 실제 canonical 이름과 매칭
            ("국어(언매)", "국어(언매)"),  # 줄임말 그대로 유지
            ("국어(화작)", "국어(화작)"),
            ("수학(미적)", "수학(미적)"),
            ("수학(기하)", "수학(기하)"),
        ]
        for input_name, expected in test_cases:
            name, conf = self.matcher.match(input_name)
            assert name == expected, f"{input_name} → {name} (expected {expected})"
            assert conf >= 90.0  # 백분율 스케일

    def test_social_studies_subjects(self):
        """사회탐구 과목 매칭"""
        test_cases = [
            ("생윤", "생활과 윤리"),
            ("사문", "사회·문화"),
            ("한지", "한국지리"),
        ]
        for input_name, expected in test_cases:
            name, conf = self.matcher.match(input_name)
            assert name == expected, f"{input_name} → {name} (expected {expected})"

    def test_unknown_subject(self):
        """알 수 없는 과목 처리"""
        name, conf = self.matcher.match("알수없는과목")
        assert conf < 0.5  # 낮은 신뢰도


class TestAdmissionProbabilityModel:
    """확률 계산 모델 테스트"""

    def setup_method(self):
        self.model = AdmissionProbabilityModel()

    def test_safe_level(self):
        """적정 라인 테스트"""
        result = self.model.calculate(98.0, 95.0, 90.0, 85.0)
        assert result.level == "적정"
        assert result.probability >= 0.80

    def test_normal_level(self):
        """예상 라인 테스트"""
        result = self.model.calculate(92.0, 95.0, 90.0, 85.0)
        assert result.level == "예상"
        assert 0.50 <= result.probability < 0.80

    def test_risk_level(self):
        """소신 라인 테스트"""
        result = self.model.calculate(87.0, 95.0, 90.0, 85.0)
        assert result.level == "소신"
        assert 0.20 <= result.probability < 0.50

    def test_reach_level(self):
        """상향 라인 테스트"""
        result = self.model.calculate(80.0, 95.0, 90.0, 85.0)
        assert result.level == "상향"
        assert result.probability < 0.20

    def test_no_cutoff(self):
        """커트라인 없음"""
        result = self.model.calculate(70.0, None, None, None)
        assert result.level == "알수없음"

    def test_confidence_interval(self):
        """신뢰구간 검증"""
        result = self.model.calculate(92.0, 95.0, 90.0, 85.0)
        assert result.confidence_low <= result.probability
        assert result.probability <= result.confidence_high


class TestDisqualificationEngine:
    """결격 체크 엔진 테스트"""

    def setup_method(self):
        self.engine = DisqualificationEngine()

    def test_normal_profile_passes(self):
        """정상 프로필 통과"""
        profile = StudentProfile(
            track=Track.SCIENCE,
            korean=ExamScore(subject="국어(언매)", raw_total=80),
            math=ExamScore(subject="수학(미적)", raw_total=75),
            english_grade=2,
            history_grade=3,
            inquiry1=ExamScore(subject="물리학 Ⅰ", raw_total=50),
            inquiry2=ExamScore(subject="화학 Ⅰ", raw_total=48),
        )
        target = TargetProgram("서울대", "공대")

        result = self.engine.check(profile, target, severity_threshold=2)
        assert not result.is_disqualified

    def test_english_grade_disqualification(self):
        """영어 등급 결격"""
        profile = StudentProfile(
            track=Track.SCIENCE,
            korean=ExamScore(subject="국어", raw_total=80),
            math=ExamScore(subject="수학", raw_total=75),
            english_grade=4,  # 4등급 = 결격
            history_grade=3,
            inquiry1=ExamScore(subject="물리학 Ⅰ", raw_total=50),
            inquiry2=ExamScore(subject="화학 Ⅰ", raw_total=48),
        )
        target = TargetProgram("서울대", "공대")

        result = self.engine.check(profile, target, severity_threshold=2)
        assert result.is_disqualified
        assert "영어" in result.reason

    def test_history_grade_disqualification(self):
        """한국사 등급 결격"""
        profile = StudentProfile(
            track=Track.SCIENCE,
            korean=ExamScore(subject="국어", raw_total=80),
            math=ExamScore(subject="수학", raw_total=75),
            english_grade=2,
            history_grade=5,  # 5등급 = 결격
            inquiry1=ExamScore(subject="물리학 Ⅰ", raw_total=50),
            inquiry2=ExamScore(subject="화학 Ⅰ", raw_total=48),
        )
        target = TargetProgram("서울대", "공대")

        result = self.engine.check(profile, target, severity_threshold=2)
        assert result.is_disqualified
        assert "한국사" in result.reason

    def test_severity_threshold(self):
        """심각도 임계값 테스트"""
        profile = StudentProfile(
            track=Track.SCIENCE,
            korean=ExamScore(subject="국어", raw_total=80),
            math=ExamScore(subject="수학(미적)", raw_total=75),  # 이과는 미적분 필수
            english_grade=3,  # 3등급 = 상위권 대학에서는 경고
            history_grade=3,
            inquiry1=ExamScore(subject="물리학 Ⅰ", raw_total=50),
            inquiry2=ExamScore(subject="화학 Ⅰ", raw_total=48),
        )
        target = TargetProgram("서울대", "공대")

        # severity=2 (심각만) → 통과
        result_high = self.engine.check(profile, target, severity_threshold=2)
        assert not result_high.is_disqualified

        # severity=1 (경고 포함) → 결격
        result_low = self.engine.check(profile, target, severity_threshold=1)
        assert result_low.is_disqualified

    def test_university_alias_recognition(self):
        """대학명 별칭(연대/고대 등)에서도 결격 룰이 동일 적용되는지"""
        profile = StudentProfile(
            track=Track.SCIENCE,
            korean=ExamScore(subject="국어(언매)", raw_total=80),
            math=ExamScore(subject="수학(확통)", raw_total=75),  # 이과 상위권 대학에서 결격 대상
            english_grade=1,
            history_grade=1,
            inquiry1=ExamScore(subject="물리학 Ⅰ", raw_total=50),
            inquiry2=ExamScore(subject="화학 Ⅰ", raw_total=48),
        )

        # "연대"는 "연세대"로 alias 해소되어 MATH_SUBJ_001 룰이 적용되어야 함
        target_alias = TargetProgram("연대", "공대")
        result = self.engine.check(profile, target_alias, severity_threshold=2)
        assert result.is_disqualified
        assert "미적분/기하" in (result.reason or "")

    def test_medical_major_keywords(self):
        """의료계열 판정이 '의' 단일 포함으로 오탐되지 않는지"""
        profile = StudentProfile(
            track=Track.SCIENCE,
            korean=ExamScore(subject="국어(언매)", raw_total=80),
            math=ExamScore(subject="수학(미적)", raw_total=75),
            english_grade=1,
            history_grade=1,
            # 의대 과탐2과목 필수 룰 검증을 위해 사회탐구로 구성(미충족)
            inquiry1=ExamScore(subject="생활과 윤리", raw_total=45),
            inquiry2=ExamScore(subject="사회·문화", raw_total=43),
        )

        # 의료계열(True) → 과탐2 미충족으로 결격
        target_medical = TargetProgram("서울대", "의예")
        result_med = self.engine.check(profile, target_medical, severity_threshold=2)
        assert result_med.is_disqualified
        assert "과학탐구" in (result_med.reason or "")

        # 비의료계열(False) → 결격 아님 ("의류학" 오탐 방지)
        target_non_med = TargetProgram("서울대", "의류학")
        result_non = self.engine.check(profile, target_non_med, severity_threshold=2)
        assert not result_non.is_disqualified


class TestCutoffExtractor:
    """커트라인 추출 테스트 (Mock 데이터)"""

    def test_cutoff_levels(self):
        """커트라인 레벨 상수 확인"""
        # PERCENTAGE(%) 축은 0에 가까울수록 상위권(점수↑), 값이 커질수록 하위권(점수↓)
        # 따라서 적정/예상/소신은 상위% 기준 20/50/80 사용
        assert CutoffExtractor.CUTOFF_PERCENTILES["적정"] == 20.0
        assert CutoffExtractor.CUTOFF_PERCENTILES["예상"] == 50.0
        assert CutoffExtractor.CUTOFF_PERCENTILES["소신"] == 80.0

    def test_cutoff_ordering_sanity(self):
        """커트라인 점수 방향(적정≥예상≥소신) sanity 체크"""
        import pandas as pd

        df = pd.DataFrame(
            {
                "%": [0.0, 20.0, 50.0, 80.0, 94.0],
                "가천의학 이과": [100.0, 90.0, 70.0, 50.0, 30.0],
            }
        )

        extractor = CutoffExtractor(df)
        res = extractor.extract_cutoffs("가천", "의학", "이과")

        assert res["found"] is True
        assert res["cutoff_safe"] is not None
        assert res["cutoff_normal"] is not None
        assert res["cutoff_risk"] is not None
        assert res["cutoff_safe"] >= res["cutoff_normal"] >= res["cutoff_risk"]

    def test_university_alias_no_overmatch(self):
        """대학 Alias가 과도한 부분 매칭으로 오매핑되지 않는지 확인"""
        import pandas as pd

        df = pd.DataFrame(
            {
                "%": [0.0, 50.0, 94.0],
                "서울대공대 이과": [100.0, 70.0, 30.0],
            }
        )
        extractor = CutoffExtractor(df)

        # '서울과기대' 같은 미등록 대학이 '서울대'로 강제 매핑되면 안 됨
        assert extractor._get_official_university("서울과기대") == "서울과기대"

        # 괄호/특수문자 포함 대학도 정규화 후 정확 매핑되어야 함
        assert extractor._get_official_university("연세대(원주)") == "연세대(원주)"


class TestIndexOptimizer:
    """INDEX 최적화 테스트 (Mock 데이터)"""

    def test_key_columns(self):
        """키 컬럼 확인"""
        assert "korean_std" in IndexOptimizer.KEY_COLUMNS
        assert "math_std" in IndexOptimizer.KEY_COLUMNS
        assert "track" in IndexOptimizer.KEY_COLUMNS


class TestIntegration:
    """전체 통합 테스트"""

    @pytest.fixture
    def sample_profile(self):
        """테스트용 프로필"""
        return StudentProfile(
            track=Track.SCIENCE,
            korean=ExamScore(subject="국어(언매)", raw_total=80),
            math=ExamScore(subject="수학(미적)", raw_total=75),
            english_grade=2,
            history_grade=3,
            inquiry1=ExamScore(subject="물리학I", raw_total=50),
            inquiry2=ExamScore(subject="화학I", raw_total=48),
            targets=[
                TargetProgram("가천", "의학"),
                TargetProgram("서울대", "공대"),
            ]
        )

    def test_subject_normalization_in_profile(self, sample_profile):
        """프로필 내 과목명 정규화"""
        matcher = SubjectMatcher()

        # 탐구과목 정규화
        inq1_name, _ = matcher.match(sample_profile.inquiry1.subject)
        inq2_name, _ = matcher.match(sample_profile.inquiry2.subject)

        assert inq1_name == "물리학 Ⅰ"
        assert inq2_name == "화학 Ⅰ"

    def test_disqualification_check(self, sample_profile):
        """결격 체크"""
        engine = DisqualificationEngine()

        for target in sample_profile.targets:
            result = engine.check(sample_profile, target, severity_threshold=2)
            assert not result.is_disqualified, f"{target.university} 결격 처리됨"

    def test_probability_calculation_workflow(self):
        """확률 계산 워크플로우"""
        model = AdmissionProbabilityModel()

        # 가상 시나리오: 학생 점수 92, 커트라인 (95, 90, 85)
        student_score = 92.0
        result = model.calculate(
            student_score,
            cutoff_safe=95.0,
            cutoff_normal=90.0,
            cutoff_risk=85.0
        )

        assert result.level == "예상"
        assert 0.50 <= result.probability < 0.80


class TestEdgeCases:
    """경계 케이스 테스트"""

    def test_empty_targets(self):
        """빈 지원 목록"""
        profile = StudentProfile(
            track=Track.SCIENCE,
            korean=ExamScore(subject="국어", raw_total=80),
            math=ExamScore(subject="수학", raw_total=75),
            english_grade=2,
            history_grade=3,
            inquiry1=ExamScore(subject="물리학 Ⅰ", raw_total=50),
            inquiry2=ExamScore(subject="화학 Ⅰ", raw_total=48),
            targets=[]
        )
        assert len(profile.targets) == 0

    def test_multiple_disqualifications(self):
        """복수 결격 사유"""
        engine = DisqualificationEngine()
        profile = StudentProfile(
            track=Track.SCIENCE,
            korean=ExamScore(subject="국어", raw_total=80),
            math=ExamScore(subject="수학", raw_total=75),
            english_grade=5,  # 결격
            history_grade=6,  # 결격
            inquiry1=ExamScore(subject="물리학 Ⅰ", raw_total=50),
            inquiry2=ExamScore(subject="화학 Ⅰ", raw_total=48),
        )
        target = TargetProgram("서울대", "공대")

        result = engine.check(profile, target, severity_threshold=2)
        assert result.is_disqualified
        assert len(result.rules_triggered) >= 1

    def test_boundary_probability(self):
        """경계값 확률"""
        model = AdmissionProbabilityModel()

        # 정확히 커트라인과 동일
        result_at_safe = model.calculate(95.0, 95.0, 90.0, 85.0)
        assert result_at_safe.probability >= 0.80

        result_at_normal = model.calculate(90.0, 95.0, 90.0, 85.0)
        assert 0.50 <= result_at_normal.probability < 0.80

        result_at_risk = model.calculate(85.0, 95.0, 90.0, 85.0)
        assert 0.20 <= result_at_risk.probability < 0.50


# 실행
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
