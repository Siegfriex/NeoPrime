# ============================================================
# NEO GOD Ultra 경계값 부동소수점 정밀도 테스트
# test_boundary_precision.py
# 경계값에서의 부동소수점 정밀도 및 데이터 타입 검증
# ============================================================

import sys
import unittest
import math
from decimal import Decimal, ROUND_HALF_UP, ROUND_HALF_EVEN
from typing import Optional, Any

# Windows 인코딩 설정
if sys.platform == 'win32':
    try:
        if hasattr(sys.stdout, 'reconfigure'):
            sys.stdout.reconfigure(encoding='utf-8')
        if hasattr(sys.stderr, 'reconfigure'):
            sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass


class FloatingPointPrecisionTest(unittest.TestCase):
    """부동소수점 정밀도 테스트"""

    def test_01_classic_floating_point_error(self):
        """클래식 부동소수점 오류 (0.1 + 0.2)"""
        result = 0.1 + 0.2
        expected = 0.3

        print(f"\n[TEST] 0.1 + 0.2")
        print(f"  결과: {result}")
        print(f"  기대값: {expected}")
        print(f"  차이: {result - expected}")
        print(f"  동등: {result == expected}")

        # 직접 비교는 실패
        self.assertNotEqual(result, expected, "부동소수점 오류 없음 (예상과 다름)")

        # epsilon 비교는 성공
        epsilon = 1e-10
        self.assertLess(abs(result - expected), epsilon)

    def test_02_score_boundary_comparison(self):
        """점수 경계값 비교"""
        test_cases = [
            # (current, threshold, expected_result)
            (69.99999999999999, 70.0, "미만"),
            (70.0, 70.0, "이상"),
            (70.00000000000001, 70.0, "이상"),
            (59.99999999999999, 60.0, "미만"),
            (60.0, 60.0, "이상"),
        ]

        print("\n[TEST] 점수 경계값 비교")
        for current, threshold, expected in test_cases:
            actual = "이상" if current >= threshold else "미만"
            match = "OK" if actual == expected else "MISMATCH"
            print(f"  {current} >= {threshold}: {actual} [{match}]")

    def test_03_excel_date_serial_precision(self):
        """Excel 날짜 시리얼 정밀도"""
        import datetime

        # Excel 기준점
        excel_epoch = datetime.date(1899, 12, 30)

        test_serials = [
            (45000, "2023-03-15"),
            (45000.5, "2023-03-15 12:00:00"),  # 0.5 = 12시간
            (45000.25, "2023-03-15 06:00:00"),  # 0.25 = 6시간
            (45000.041666667, "2023-03-15 01:00:00"),  # 1/24 = 1시간
        ]

        print("\n[TEST] Excel 날짜 시리얼 정밀도")
        for serial, expected_str in test_serials:
            days = int(serial)
            time_fraction = serial - days
            date_part = excel_epoch + datetime.timedelta(days=days)
            time_part = datetime.timedelta(days=time_fraction)
            full_datetime = datetime.datetime.combine(date_part, datetime.time()) + time_part

            print(f"  시리얼 {serial}: {full_datetime}")

    def test_04_integer_vs_float_comparison(self):
        """정수 vs 부동소수점 비교"""
        test_cases = [
            (70, 70.0, True),
            (70, 69.99999999999999, False),
            (70, 70.00000000000001, False),
        ]

        print("\n[TEST] 정수 vs 부동소수점 비교")
        for int_val, float_val, expected_equal in test_cases:
            actual_equal = int_val == float_val
            match = "OK" if actual_equal == expected_equal else "UNEXPECTED"
            print(f"  {int_val} == {float_val}: {actual_equal} [{match}]")

    def test_05_decimal_precision(self):
        """Decimal 고정밀 연산"""
        # float 연산
        float_result = 0.1 + 0.2

        # Decimal 연산
        decimal_result = Decimal('0.1') + Decimal('0.2')

        print("\n[TEST] Decimal 고정밀 연산")
        print(f"  float: 0.1 + 0.2 = {float_result}")
        print(f"  Decimal: 0.1 + 0.2 = {decimal_result}")
        print(f"  Decimal == 0.3: {decimal_result == Decimal('0.3')}")

        self.assertEqual(decimal_result, Decimal('0.3'))


class RoundingBehaviorTest(unittest.TestCase):
    """반올림 동작 테스트"""

    def test_01_python_round_bankers(self):
        """Python round() - Banker's Rounding"""
        test_cases = [
            (2.5, 2),   # 가장 가까운 짝수 = 2
            (3.5, 4),   # 가장 가까운 짝수 = 4
            (4.5, 4),   # 가장 가까운 짝수 = 4
            (5.5, 6),   # 가장 가까운 짝수 = 6
            (2.4, 2),
            (2.6, 3),
        ]

        print("\n[TEST] Python round() - Banker's Rounding")
        for value, expected in test_cases:
            result = round(value)
            match = "OK" if result == expected else "DIFF"
            print(f"  round({value}) = {result} (기대: {expected}) [{match}]")
            self.assertEqual(result, expected)

    def test_02_excel_round_half_up(self):
        """Excel ROUND - 사사오입 (Half Up)"""
        def excel_round(value: float, decimals: int = 0) -> float:
            d = Decimal(str(value))
            if decimals == 0:
                return float(d.quantize(Decimal('1'), rounding=ROUND_HALF_UP))
            else:
                pattern = Decimal(10) ** -decimals
                return float(d.quantize(pattern, rounding=ROUND_HALF_UP))

        test_cases = [
            (2.5, 0, 3),   # Excel: 3 (항상 올림)
            (3.5, 0, 4),   # Excel: 4
            (4.5, 0, 5),   # Excel: 5
            (5.5, 0, 6),   # Excel: 6
            (-2.5, 0, -3), # Excel: -3 (음수도 올림)
            (2.55, 1, 2.6),
        ]

        print("\n[TEST] Excel ROUND - 사사오입 (Half Up)")
        for value, decimals, expected in test_cases:
            result = excel_round(value, decimals)
            match = "OK" if result == expected else "DIFF"
            print(f"  excel_round({value}, {decimals}) = {result} (기대: {expected}) [{match}]")
            self.assertEqual(result, expected)

    def test_03_bigquery_round_half_even(self):
        """BigQuery ROUND - Banker's Rounding (Half Even)"""
        def bq_round(value: float, decimals: int = 0) -> float:
            d = Decimal(str(value))
            if decimals == 0:
                return float(d.quantize(Decimal('1'), rounding=ROUND_HALF_EVEN))
            else:
                pattern = Decimal(10) ** -decimals
                return float(d.quantize(pattern, rounding=ROUND_HALF_EVEN))

        test_cases = [
            (2.5, 0, 2),   # BigQuery: 2 (짝수로)
            (3.5, 0, 4),   # BigQuery: 4
            (4.5, 0, 4),   # BigQuery: 4 (짝수로)
            (5.5, 0, 6),   # BigQuery: 6
        ]

        print("\n[TEST] BigQuery ROUND - Banker's Rounding")
        for value, decimals, expected in test_cases:
            result = bq_round(value, decimals)
            match = "OK" if result == expected else "DIFF"
            print(f"  bq_round({value}, {decimals}) = {result} (기대: {expected}) [{match}]")
            self.assertEqual(result, expected)

    def test_04_rounding_discrepancy(self):
        """Excel vs BigQuery 반올림 차이"""
        def excel_round(v):
            return float(Decimal(str(v)).quantize(Decimal('1'), rounding=ROUND_HALF_UP))
        def bq_round(v):
            return float(Decimal(str(v)).quantize(Decimal('1'), rounding=ROUND_HALF_EVEN))

        # 차이가 발생하는 케이스
        discrepancy_cases = [2.5, 4.5, 6.5, 8.5, -2.5, -4.5]

        print("\n[TEST] Excel vs BigQuery 반올림 차이")
        print("  Value     Excel   BigQuery  차이")
        print("  " + "-" * 35)

        for value in discrepancy_cases:
            excel_result = excel_round(value)
            bq_result = bq_round(value)
            diff = "YES" if excel_result != bq_result else "NO"
            print(f"  {value:7.1f}   {excel_result:5.0f}   {bq_result:8.0f}   {diff}")


class DataTypeEdgeCaseTest(unittest.TestCase):
    """데이터 타입 엣지 케이스 테스트"""

    def test_01_nan_handling(self):
        """NaN 처리"""
        nan = float('nan')

        print("\n[TEST] NaN 처리")
        print(f"  nan == nan: {nan == nan}")  # False
        print(f"  math.isnan(nan): {math.isnan(nan)}")  # True

        self.assertFalse(nan == nan, "NaN은 자기 자신과도 같지 않음")
        self.assertTrue(math.isnan(nan))

    def test_02_infinity_handling(self):
        """Infinity 처리"""
        pos_inf = float('inf')
        neg_inf = float('-inf')

        print("\n[TEST] Infinity 처리")
        print(f"  inf > 1e308: {pos_inf > 1e308}")
        print(f"  -inf < -1e308: {neg_inf < -1e308}")
        print(f"  math.isinf(inf): {math.isinf(pos_inf)}")

        self.assertTrue(pos_inf > 1e308)
        self.assertTrue(math.isinf(pos_inf))

    def test_03_zero_division(self):
        """0으로 나누기"""
        print("\n[TEST] 0으로 나누기")

        # 정수 나누기
        try:
            result = 1 / 0
            print(f"  1 / 0 = {result}")
        except ZeroDivisionError:
            print("  1 / 0 = ZeroDivisionError")

        # float 나누기 (inf 반환)
        result = 1.0 / 1e-400  # 매우 작은 수
        print(f"  1.0 / 1e-400 = {result}")

    def test_04_string_to_number_edge_cases(self):
        """문자열 -> 숫자 변환 엣지 케이스"""
        test_cases = [
            ("70", 70.0),
            ("70.5", 70.5),
            (" 70 ", 70.0),      # 공백 포함
            ("70.0", 70.0),
            ("1e10", 1e10),      # 과학적 표기법
            ("-70", -70.0),
        ]

        print("\n[TEST] 문자열 -> 숫자 변환")
        for string_val, expected in test_cases:
            try:
                result = float(string_val)
                match = "OK" if result == expected else "DIFF"
                print(f"  float('{string_val}') = {result} [{match}]")
                self.assertEqual(result, expected)
            except ValueError as e:
                print(f"  float('{string_val}') = Error: {e}")

    def test_05_null_empty_handling(self):
        """NULL/빈 값 처리"""
        test_values = [
            (None, "None"),
            ("", "empty string"),
            (0, "zero"),
            (0.0, "zero float"),
            (False, "False"),
        ]

        print("\n[TEST] NULL/빈 값의 truthiness")
        for value, desc in test_values:
            is_truthy = bool(value)
            is_none = value is None
            print(f"  {desc}: bool={is_truthy}, is_none={is_none}")


class ScoreComparisonPrecisionTest(unittest.TestCase):
    """점수 비교 정밀도 테스트 (비즈니스 로직)"""

    def test_01_score_judgment_precision(self):
        """적정점수 판정 정밀도"""
        def judge_score(current: float, threshold: float, epsilon: float = 1e-9) -> str:
            """정밀 점수 판정"""
            if abs(current - threshold) < epsilon:
                return "경계값 (이상으로 처리)"
            elif current > threshold:
                return "이상"
            else:
                return "미만"

        test_cases = [
            (70.0, 70.0, "경계값 (이상으로 처리)"),
            (69.99999999999999, 70.0, "경계값 (이상으로 처리)"),  # 부동소수점 근사
            (70.00000000000001, 70.0, "경계값 (이상으로 처리)"),  # 부동소수점 근사
            (69.9, 70.0, "미만"),
            (70.1, 70.0, "이상"),
        ]

        print("\n[TEST] 적정점수 판정 정밀도")
        for current, threshold, expected in test_cases:
            result = judge_score(current, threshold)
            match = "OK" if result == expected else "DIFF"
            print(f"  judge({current}, {threshold}) = '{result}' [{match}]")

    def test_02_score_range_precision(self):
        """점수 범위 판정 정밀도"""
        def categorize_score(
            score: float,
            optimal: float,
            expected: float,
            conservative: float,
            epsilon: float = 1e-9
        ) -> str:
            """정밀 범위 판정"""
            if score >= optimal - epsilon:
                return "적정점수 이상"
            elif score >= expected - epsilon:
                return "예상점수 이상"
            elif score >= conservative - epsilon:
                return "소신점수 이상"
            else:
                return "소신점수 미만"

        # 경계값 테스트
        optimal, expected, conservative = 70.0, 60.0, 50.0

        boundary_scores = [
            70.0, 69.99999999999, 70.00000000001,
            60.0, 59.99999999999, 60.00000000001,
            50.0, 49.99999999999, 50.00000000001,
        ]

        print("\n[TEST] 점수 범위 판정 (경계값)")
        print(f"  기준: 적정={optimal}, 예상={expected}, 소신={conservative}")
        for score in boundary_scores:
            result = categorize_score(score, optimal, expected, conservative)
            print(f"  {score:.11f} -> {result}")


def run_precision_tests():
    """정밀도 테스트 실행"""
    print("=" * 70)
    print("NEO GOD Ultra 경계값 부동소수점 정밀도 테스트")
    print("=" * 70)

    # 테스트 스위트 생성
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    suite.addTests(loader.loadTestsFromTestCase(FloatingPointPrecisionTest))
    suite.addTests(loader.loadTestsFromTestCase(RoundingBehaviorTest))
    suite.addTests(loader.loadTestsFromTestCase(DataTypeEdgeCaseTest))
    suite.addTests(loader.loadTestsFromTestCase(ScoreComparisonPrecisionTest))

    # 테스트 실행
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # 결과 요약
    print("\n" + "=" * 70)
    print("정밀도 테스트 결과 요약")
    print("=" * 70)
    print(f"실행: {result.testsRun}")
    print(f"성공: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"실패: {len(result.failures)}")
    print(f"에러: {len(result.errors)}")

    # 주의 사항
    print("\n[주의] 프로덕션 코드 권장 사항:")
    print("  1. 점수 비교 시 epsilon(1e-9) 허용 오차 사용")
    print("  2. ROUND 함수는 Excel/BigQuery 차이 인지")
    print("  3. NaN/Infinity 값 사전 필터링")
    print("  4. 문자열 -> 숫자 변환 시 예외 처리")

    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_precision_tests()
    sys.exit(0 if success else 1)
