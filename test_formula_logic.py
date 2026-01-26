# ============================================================
# NEO GOD Ultra 비즈니스 로직 검증 테스트
# test_formula_logic.py
# 적정점수 판정 로직, COMPUTE/RESTRICT 조회 로직, 평균 점수 계산 로직 검증
# ============================================================

import sys
import unittest
from pathlib import Path
from typing import Optional, Tuple

# Windows 인코딩 설정
if sys.platform == 'win32':
    try:
        if hasattr(sys.stdout, 'reconfigure'):
            sys.stdout.reconfigure(encoding='utf-8')
        if hasattr(sys.stderr, 'reconfigure'):
            sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass


class ScoreJudgmentLogic:
    """적정점수 판정 로직 구현 (Excel 수식 -> Python)"""

    # 판정 결과 상수
    RESULT_ERROR = "오류(영어국사)"
    RESULT_EXCLUDE = "제외(수탐)"
    RESULT_OPTIMAL = "적정점수 이상"
    RESULT_EXPECTED = "예상점수 이상"
    RESULT_CONSERVATIVE = "소신점수 이상"
    RESULT_BELOW = "소신점수 미만"

    @staticmethod
    def validate_grade(grade: Optional[float]) -> bool:
        """영어/국사 등급 검증 (1-9 사이 유효)"""
        if grade is None or grade == "":
            return False
        try:
            grade_val = float(grade)
            if grade_val == 0 or grade_val > 9:
                return False
            return True
        except (ValueError, TypeError):
            return False

    @staticmethod
    def judge_score(
        current_score: float,
        optimal_score: float,
        expected_score: float,
        conservative_score: float,
        english_grade: Optional[float] = 1,
        history_grade: Optional[float] = 1,
        restrict_result: Optional[str] = None
    ) -> str:
        """
        적정점수 판정 로직

        Excel 수식:
        =IF(OR(수능입력!$C$18="",수능입력!$C$18=0,수능입력!$C$18>9,...),
            "오류(영어국사)",
            IFERROR(VLOOKUP(...RESTRICT...),
                IF($G6=0,"제외(수탐)",
                    IF($G6*1>=$J6*1,"적정점수 이상",
                        IF($G6*1>=$K6*1,"예상점수 이상",
                            IF($G6*1>=$L6*1,"소신점수 이상",
                                IF($G6*1<$L6*1,"소신점수 미만",0/0)))))))
        """
        # Step 1: 영어/국사 등급 검증
        if not ScoreJudgmentLogic.validate_grade(english_grade) or \
           not ScoreJudgmentLogic.validate_grade(history_grade):
            return ScoreJudgmentLogic.RESULT_ERROR

        # Step 2: RESTRICT 테이블 조회 결과가 있으면 그대로 반환
        if restrict_result:
            return restrict_result

        # Step 3: 현재 점수가 0이면 제외
        if current_score == 0:
            return ScoreJudgmentLogic.RESULT_EXCLUDE

        # Step 4: 점수 비교 판정
        if current_score >= optimal_score:
            return ScoreJudgmentLogic.RESULT_OPTIMAL
        elif current_score >= expected_score:
            return ScoreJudgmentLogic.RESULT_EXPECTED
        elif current_score >= conservative_score:
            return ScoreJudgmentLogic.RESULT_CONSERVATIVE
        else:
            return ScoreJudgmentLogic.RESULT_BELOW


class ComputeLookupLogic:
    """COMPUTE 시트 기반 점수 변환 로직 (INDEX/MATCH)"""

    def __init__(self, compute_data: dict = None):
        """
        compute_data: {
            'headers': {'row': [...], 'col': [...]},
            'values': [[...], [...], ...]  # 2D array
        }
        """
        self.compute_data = compute_data or {}

    def index_match(
        self,
        row_key: str,
        col_key: str,
        default: float = 0
    ) -> float:
        """
        INDEX/MATCH 로직 구현

        Excel 수식:
        =IFERROR(INDEX(COMPUTE!$A$1:$UG$72,
            MATCH(E$5,COMPUTE!$B$1:$B$72,0),
            MATCH($AK6,COMPUTE!$A$2:$UG$2,0)),0)
        """
        if not self.compute_data:
            return default

        try:
            row_headers = self.compute_data.get('headers', {}).get('row', [])
            col_headers = self.compute_data.get('headers', {}).get('col', [])
            values = self.compute_data.get('values', [])

            # MATCH row_key in row headers
            if row_key not in row_headers:
                return default
            row_idx = row_headers.index(row_key)

            # MATCH col_key in col headers
            if col_key not in col_headers:
                return default
            col_idx = col_headers.index(col_key)

            # INDEX value
            return values[row_idx][col_idx]

        except (IndexError, KeyError, TypeError):
            return default

    def hlookup(
        self,
        lookup_key: str,
        row_index: int,
        default: float = None
    ) -> Optional[float]:
        """
        HLOOKUP 로직 구현

        Excel 수식:
        =HLOOKUP($AK6,COMPUTE!$2:$8,4,FALSE)
        """
        if not self.compute_data:
            return default

        try:
            col_headers = self.compute_data.get('headers', {}).get('col', [])
            values = self.compute_data.get('values', [])

            if lookup_key not in col_headers:
                return default
            col_idx = col_headers.index(lookup_key)

            # row_index is 1-based (Excel style)
            return values[row_index - 1][col_idx]

        except (IndexError, KeyError, TypeError):
            return default


class AverageScoreLogic:
    """평균 점수 계산 로직"""

    @staticmethod
    def calculate_average(
        current_score: float,
        value1: Optional[float],
        value2: Optional[float],
        min_value: float = 0.00001
    ) -> Optional[float]:
        """
        평균 점수 계산 로직

        Excel 수식:
        =IF($G6=0,"",
            IF(AND(IFERROR(HLOOKUP(...),\"")=\"",IFERROR(HLOOKUP(...),\"\")=\"\"),
                "",
                MAX(0.00001,AVERAGE(HLOOKUP(...),HLOOKUP(...)))))
        """
        # G6=0이면 빈 문자열 (None)
        if current_score == 0:
            return None

        # 둘 다 없으면 빈 문자열 (None)
        if (value1 is None or value1 == "") and (value2 is None or value2 == ""):
            return None

        # AVERAGE 계산 (None 제외)
        valid_values = []
        if value1 is not None and value1 != "":
            valid_values.append(float(value1))
        if value2 is not None and value2 != "":
            valid_values.append(float(value2))

        if not valid_values:
            return None

        avg = sum(valid_values) / len(valid_values)

        # MAX(0.00001, average)
        return max(min_value, avg)


class TestScoreJudgmentLogic(unittest.TestCase):
    """적정점수 판정 로직 테스트"""

    def test_grade_validation_valid(self):
        """유효한 등급 검증"""
        self.assertTrue(ScoreJudgmentLogic.validate_grade(1))
        self.assertTrue(ScoreJudgmentLogic.validate_grade(5))
        self.assertTrue(ScoreJudgmentLogic.validate_grade(9))
        self.assertTrue(ScoreJudgmentLogic.validate_grade(1.5))

    def test_grade_validation_invalid(self):
        """무효한 등급 검증"""
        self.assertFalse(ScoreJudgmentLogic.validate_grade(None))
        self.assertFalse(ScoreJudgmentLogic.validate_grade(""))
        self.assertFalse(ScoreJudgmentLogic.validate_grade(0))
        self.assertFalse(ScoreJudgmentLogic.validate_grade(10))
        self.assertFalse(ScoreJudgmentLogic.validate_grade(100))

    def test_judge_score_error_invalid_grade(self):
        """무효한 등급 -> 오류(영어국사)"""
        result = ScoreJudgmentLogic.judge_score(
            current_score=80,
            optimal_score=70,
            expected_score=60,
            conservative_score=50,
            english_grade=0,  # 무효
            history_grade=1
        )
        self.assertEqual(result, ScoreJudgmentLogic.RESULT_ERROR)

    def test_judge_score_exclude_zero_score(self):
        """점수 0 -> 제외(수탐)"""
        result = ScoreJudgmentLogic.judge_score(
            current_score=0,
            optimal_score=70,
            expected_score=60,
            conservative_score=50,
            english_grade=1,
            history_grade=1
        )
        self.assertEqual(result, ScoreJudgmentLogic.RESULT_EXCLUDE)

    def test_judge_score_optimal(self):
        """적정점수 이상"""
        result = ScoreJudgmentLogic.judge_score(
            current_score=80,
            optimal_score=70,
            expected_score=60,
            conservative_score=50,
            english_grade=1,
            history_grade=1
        )
        self.assertEqual(result, ScoreJudgmentLogic.RESULT_OPTIMAL)

    def test_judge_score_expected(self):
        """예상점수 이상"""
        result = ScoreJudgmentLogic.judge_score(
            current_score=65,
            optimal_score=70,
            expected_score=60,
            conservative_score=50,
            english_grade=1,
            history_grade=1
        )
        self.assertEqual(result, ScoreJudgmentLogic.RESULT_EXPECTED)

    def test_judge_score_conservative(self):
        """소신점수 이상"""
        result = ScoreJudgmentLogic.judge_score(
            current_score=55,
            optimal_score=70,
            expected_score=60,
            conservative_score=50,
            english_grade=1,
            history_grade=1
        )
        self.assertEqual(result, ScoreJudgmentLogic.RESULT_CONSERVATIVE)

    def test_judge_score_below(self):
        """소신점수 미만"""
        result = ScoreJudgmentLogic.judge_score(
            current_score=45,
            optimal_score=70,
            expected_score=60,
            conservative_score=50,
            english_grade=1,
            history_grade=1
        )
        self.assertEqual(result, ScoreJudgmentLogic.RESULT_BELOW)

    def test_judge_score_boundary_optimal(self):
        """경계값 테스트 - 정확히 적정점수"""
        result = ScoreJudgmentLogic.judge_score(
            current_score=70,
            optimal_score=70,
            expected_score=60,
            conservative_score=50,
            english_grade=1,
            history_grade=1
        )
        self.assertEqual(result, ScoreJudgmentLogic.RESULT_OPTIMAL)

    def test_judge_score_boundary_expected(self):
        """경계값 테스트 - 정확히 예상점수"""
        result = ScoreJudgmentLogic.judge_score(
            current_score=60,
            optimal_score=70,
            expected_score=60,
            conservative_score=50,
            english_grade=1,
            history_grade=1
        )
        self.assertEqual(result, ScoreJudgmentLogic.RESULT_EXPECTED)

    def test_judge_score_restrict_override(self):
        """RESTRICT 테이블 결과 우선"""
        result = ScoreJudgmentLogic.judge_score(
            current_score=80,
            optimal_score=70,
            expected_score=60,
            conservative_score=50,
            english_grade=1,
            history_grade=1,
            restrict_result="특별 제한"
        )
        self.assertEqual(result, "특별 제한")


class TestComputeLookupLogic(unittest.TestCase):
    """COMPUTE 조회 로직 테스트"""

    def setUp(self):
        """테스트 데이터 설정"""
        self.compute_data = {
            'headers': {
                'row': ['국어', '수학', '영어', '탐구1', '탐구2'],
                'col': ['서울대', '연세대', '고려대', '성균관대', 'KAIST']
            },
            'values': [
                [100, 98, 97, 95, 99],  # 국어
                [100, 99, 98, 96, 100], # 수학
                [95, 94, 93, 92, 91],   # 영어
                [90, 88, 87, 85, 89],   # 탐구1
                [85, 83, 82, 80, 84],   # 탐구2
            ]
        }
        self.lookup = ComputeLookupLogic(self.compute_data)

    def test_index_match_valid(self):
        """유효한 INDEX/MATCH"""
        result = self.lookup.index_match('수학', '서울대')
        self.assertEqual(result, 100)

        result = self.lookup.index_match('국어', '연세대')
        self.assertEqual(result, 98)

    def test_index_match_invalid_row(self):
        """무효한 행 키"""
        result = self.lookup.index_match('물리', '서울대', default=0)
        self.assertEqual(result, 0)

    def test_index_match_invalid_col(self):
        """무효한 열 키"""
        result = self.lookup.index_match('수학', '하버드', default=0)
        self.assertEqual(result, 0)

    def test_hlookup_valid(self):
        """유효한 HLOOKUP"""
        # row_index 1 = 첫 번째 행 (국어)
        result = self.lookup.hlookup('서울대', 1)
        self.assertEqual(result, 100)

        # row_index 2 = 두 번째 행 (수학)
        result = self.lookup.hlookup('연세대', 2)
        self.assertEqual(result, 99)

    def test_hlookup_invalid_key(self):
        """무효한 키"""
        result = self.lookup.hlookup('MIT', 1, default=None)
        self.assertIsNone(result)


class TestAverageScoreLogic(unittest.TestCase):
    """평균 점수 계산 로직 테스트"""

    def test_calculate_average_normal(self):
        """정상적인 평균 계산"""
        result = AverageScoreLogic.calculate_average(
            current_score=80,
            value1=90,
            value2=80
        )
        self.assertEqual(result, 85.0)

    def test_calculate_average_zero_score(self):
        """점수 0 -> None"""
        result = AverageScoreLogic.calculate_average(
            current_score=0,
            value1=90,
            value2=80
        )
        self.assertIsNone(result)

    def test_calculate_average_both_empty(self):
        """둘 다 빈 값 -> None"""
        result = AverageScoreLogic.calculate_average(
            current_score=80,
            value1=None,
            value2=None
        )
        self.assertIsNone(result)

    def test_calculate_average_one_value(self):
        """하나의 값만 있는 경우"""
        result = AverageScoreLogic.calculate_average(
            current_score=80,
            value1=90,
            value2=None
        )
        self.assertEqual(result, 90.0)

    def test_calculate_average_min_value(self):
        """최소값 보정 (MAX 0.00001)"""
        result = AverageScoreLogic.calculate_average(
            current_score=80,
            value1=0.000001,
            value2=0.000001
        )
        self.assertEqual(result, 0.00001)

    def test_calculate_average_negative_values(self):
        """음수 값 처리"""
        result = AverageScoreLogic.calculate_average(
            current_score=80,
            value1=-10,
            value2=-5
        )
        # MAX(0.00001, -7.5) = 0.00001
        self.assertEqual(result, 0.00001)


class TestFloatingPointPrecision(unittest.TestCase):
    """부동소수점 정밀도 테스트"""

    def test_boundary_precision(self):
        """경계값에서의 부동소수점 정밀도"""
        # 0.1 + 0.2 != 0.3 (부동소수점 오차)
        score = 0.1 + 0.2
        threshold = 0.3

        # 부동소수점 비교는 epsilon 사용 권장
        epsilon = 1e-9
        self.assertTrue(abs(score - threshold) < epsilon)

    def test_score_comparison_precision(self):
        """점수 비교 시 정밀도"""
        current = 69.99999999999999
        optimal = 70.0

        # 직접 비교는 실패할 수 있음
        # self.assertTrue(current >= optimal)  # 실패 가능

        # 반올림 후 비교
        self.assertFalse(round(current, 10) >= optimal)

    def test_average_precision(self):
        """평균 계산 정밀도"""
        result = AverageScoreLogic.calculate_average(
            current_score=80,
            value1=0.1,
            value2=0.2
        )
        # 기대값: 0.15
        self.assertAlmostEqual(result, 0.15, places=10)


def run_formula_logic_tests():
    """전체 비즈니스 로직 테스트 실행"""
    print("=" * 70)
    print("NEO GOD Ultra 비즈니스 로직 검증 테스트")
    print("=" * 70)

    # 테스트 스위트 생성
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    suite.addTests(loader.loadTestsFromTestCase(TestScoreJudgmentLogic))
    suite.addTests(loader.loadTestsFromTestCase(TestComputeLookupLogic))
    suite.addTests(loader.loadTestsFromTestCase(TestAverageScoreLogic))
    suite.addTests(loader.loadTestsFromTestCase(TestFloatingPointPrecision))

    # 테스트 실행
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # 결과 요약
    print("\n" + "=" * 70)
    print("테스트 결과 요약")
    print("=" * 70)
    print(f"실행: {result.testsRun}")
    print(f"성공: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"실패: {len(result.failures)}")
    print(f"에러: {len(result.errors)}")

    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_formula_logic_tests()
    sys.exit(0 if success else 1)
