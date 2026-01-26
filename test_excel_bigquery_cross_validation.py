# ============================================================
# NEO GOD Ultra Excel vs BigQuery 교차 검증 테스트
# test_excel_bigquery_cross_validation.py
# Excel 수식 계산 vs BigQuery SQL 변환 결과 비교
# ============================================================

import sys
import unittest
from pathlib import Path
from typing import Dict, List, Any, Optional
from decimal import Decimal, ROUND_HALF_UP
import json

# Windows 인코딩 설정
if sys.platform == 'win32':
    try:
        if hasattr(sys.stdout, 'reconfigure'):
            sys.stdout.reconfigure(encoding='utf-8')
        if hasattr(sys.stderr, 'reconfigure'):
            sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass


class ExcelFormulaEmulator:
    """Excel 수식 에뮬레이터 (Python 구현)"""

    @staticmethod
    def excel_round(value: float, decimals: int = 0) -> float:
        """Excel ROUND 함수 (사사오입)"""
        if value is None:
            return None
        d = Decimal(str(value))
        if decimals == 0:
            return float(d.quantize(Decimal('1'), rounding=ROUND_HALF_UP))
        else:
            pattern = Decimal(10) ** -decimals
            return float(d.quantize(pattern, rounding=ROUND_HALF_UP))

    @staticmethod
    def excel_if(condition: bool, true_val: Any, false_val: Any) -> Any:
        """Excel IF 함수"""
        return true_val if condition else false_val

    @staticmethod
    def excel_or(*conditions: bool) -> bool:
        """Excel OR 함수"""
        return any(conditions)

    @staticmethod
    def excel_and(*conditions: bool) -> bool:
        """Excel AND 함수"""
        return all(conditions)

    @staticmethod
    def excel_iferror(value: Any, error_val: Any) -> Any:
        """Excel IFERROR 함수"""
        try:
            if value is None or (isinstance(value, float) and str(value) == 'nan'):
                return error_val
            return value
        except:
            return error_val

    @staticmethod
    def excel_vlookup(
        lookup_value: Any,
        table: List[List[Any]],
        col_index: int,
        range_lookup: bool = False
    ) -> Optional[Any]:
        """Excel VLOOKUP 함수"""
        if not table:
            return None

        for row in table:
            if len(row) >= col_index and row[0] == lookup_value:
                return row[col_index - 1]

        return None

    @staticmethod
    def excel_index_match(
        data_range: List[List[Any]],
        row_lookup: Any,
        row_range: List[Any],
        col_lookup: Any,
        col_range: List[Any]
    ) -> Optional[Any]:
        """Excel INDEX/MATCH 함수 조합"""
        try:
            row_idx = row_range.index(row_lookup)
            col_idx = col_range.index(col_lookup)
            return data_range[row_idx][col_idx]
        except (ValueError, IndexError):
            return None

    @staticmethod
    def excel_sum(*values) -> float:
        """Excel SUM 함수"""
        total = 0
        for v in values:
            if v is not None and v != "":
                try:
                    total += float(v)
                except (ValueError, TypeError):
                    pass
        return total

    @staticmethod
    def excel_average(*values) -> Optional[float]:
        """Excel AVERAGE 함수"""
        valid = []
        for v in values:
            if v is not None and v != "":
                try:
                    valid.append(float(v))
                except (ValueError, TypeError):
                    pass
        if not valid:
            return None
        return sum(valid) / len(valid)

    @staticmethod
    def excel_max(*values) -> float:
        """Excel MAX 함수"""
        valid = []
        for v in values:
            if v is not None and v != "":
                try:
                    valid.append(float(v))
                except (ValueError, TypeError):
                    pass
        return max(valid) if valid else 0


class BigQuerySQLEmulator:
    """BigQuery SQL 에뮬레이터 (Python 구현)"""

    @staticmethod
    def bq_round(value: float, decimals: int = 0) -> float:
        """BigQuery ROUND 함수"""
        if value is None:
            return None
        return round(value, decimals)

    @staticmethod
    def bq_if(condition: bool, true_val: Any, false_val: Any) -> Any:
        """BigQuery IF 함수"""
        return true_val if condition else false_val

    @staticmethod
    def bq_case_when(conditions: List[tuple]) -> Any:
        """BigQuery CASE WHEN 구문"""
        for condition, value in conditions:
            if condition:
                return value
        return None

    @staticmethod
    def bq_coalesce(*values) -> Any:
        """BigQuery COALESCE 함수"""
        for v in values:
            if v is not None:
                return v
        return None

    @staticmethod
    def bq_ifnull(value: Any, default: Any) -> Any:
        """BigQuery IFNULL 함수"""
        return value if value is not None else default

    @staticmethod
    def bq_nullif(value: Any, compare: Any) -> Any:
        """BigQuery NULLIF 함수"""
        return None if value == compare else value

    @staticmethod
    def bq_sum(values: List) -> float:
        """BigQuery SUM 집계"""
        total = 0
        for v in values:
            if v is not None:
                total += v
        return total

    @staticmethod
    def bq_avg(values: List) -> Optional[float]:
        """BigQuery AVG 집계"""
        valid = [v for v in values if v is not None]
        if not valid:
            return None
        return sum(valid) / len(valid)

    @staticmethod
    def bq_greatest(*values) -> float:
        """BigQuery GREATEST 함수"""
        valid = [v for v in values if v is not None]
        return max(valid) if valid else None


class FormulaTranslator:
    """Excel 수식 -> BigQuery SQL 변환기"""

    @staticmethod
    def translate_score_judgment(
        current_score: str,
        optimal_score: str,
        expected_score: str,
        conservative_score: str
    ) -> str:
        """
        적정점수 판정 로직의 BigQuery SQL 변환

        Excel:
        =IF($G6*1>=$J6*1,"적정점수 이상",
            IF($G6*1>=$K6*1,"예상점수 이상",
                IF($G6*1>=$L6*1,"소신점수 이상",
                    IF($G6*1<$L6*1,"소신점수 미만",NULL))))

        BigQuery SQL:
        CASE
            WHEN current_score >= optimal_score THEN '적정점수 이상'
            WHEN current_score >= expected_score THEN '예상점수 이상'
            WHEN current_score >= conservative_score THEN '소신점수 이상'
            WHEN current_score < conservative_score THEN '소신점수 미만'
            ELSE NULL
        END
        """
        return f"""
CASE
    WHEN {current_score} >= {optimal_score} THEN '적정점수 이상'
    WHEN {current_score} >= {expected_score} THEN '예상점수 이상'
    WHEN {current_score} >= {conservative_score} THEN '소신점수 이상'
    WHEN {current_score} < {conservative_score} THEN '소신점수 미만'
    ELSE NULL
END
""".strip()

    @staticmethod
    def translate_sum(col1: str, col2: str) -> str:
        """
        SUM 수식의 BigQuery SQL 변환

        Excel: =SUM(E6,F6)
        BigQuery: COALESCE(E6, 0) + COALESCE(F6, 0)
        """
        return f"COALESCE({col1}, 0) + COALESCE({col2}, 0)"

    @staticmethod
    def translate_average_with_min(col1: str, col2: str, min_val: float = 0.00001) -> str:
        """
        MIN 보정 AVERAGE의 BigQuery SQL 변환

        Excel: =MAX(0.00001, AVERAGE(H1, H2))
        BigQuery: GREATEST(0.00001, (COALESCE(H1, 0) + COALESCE(H2, 0)) / 2)
        """
        return f"GREATEST({min_val}, (COALESCE({col1}, 0) + COALESCE({col2}, 0)) / 2)"

    @staticmethod
    def translate_round(value: str, decimals: int = 0) -> str:
        """
        ROUND 수식의 BigQuery SQL 변환

        Excel: =ROUND(value, 0)
        BigQuery: ROUND(value, 0)
        """
        return f"ROUND({value}, {decimals})"


class TestExcelBigQueryComparison(unittest.TestCase):
    """Excel vs BigQuery 계산 결과 비교 테스트"""

    def test_round_comparison_positive(self):
        """ROUND 함수 비교 - 양수"""
        excel = ExcelFormulaEmulator.excel_round
        bq = BigQuerySQLEmulator.bq_round

        test_cases = [
            (2.5, 0),   # Excel: 3, BQ: 2 (banker's rounding) - 차이 발생!
            (3.5, 0),   # Excel: 4, BQ: 4
            (2.4, 0),   # 둘 다 2
            (2.6, 0),   # 둘 다 3
            (2.55, 1),  # 소수점 1자리
        ]

        print("\n[ROUND 함수 비교]")
        for value, decimals in test_cases:
            excel_result = excel(value, decimals)
            bq_result = bq(value, decimals)
            match = "MATCH" if excel_result == bq_result else "DIFF"
            print(f"  ROUND({value}, {decimals}): Excel={excel_result}, BQ={bq_result} [{match}]")

    def test_round_comparison_negative(self):
        """ROUND 함수 비교 - 음수"""
        excel = ExcelFormulaEmulator.excel_round
        bq = BigQuerySQLEmulator.bq_round

        test_cases = [
            (-2.5, 0),  # Excel: -3 (사사오입), BQ: -2
            (-3.5, 0),
            (-2.4, 0),
            (-2.6, 0),
        ]

        print("\n[ROUND 함수 비교 - 음수]")
        for value, decimals in test_cases:
            excel_result = excel(value, decimals)
            bq_result = bq(value, decimals)
            match = "MATCH" if excel_result == bq_result else "DIFF"
            print(f"  ROUND({value}, {decimals}): Excel={excel_result}, BQ={bq_result} [{match}]")

    def test_sum_comparison(self):
        """SUM 함수 비교"""
        excel = ExcelFormulaEmulator.excel_sum
        bq = BigQuerySQLEmulator.bq_sum

        test_cases = [
            ([10, 20, 30],),
            ([10, None, 30],),
            ([None, None, None],),
            ([0, 0, 0],),
            ([0.1, 0.2, 0.3],),  # 부동소수점
        ]

        print("\n[SUM 함수 비교]")
        for values in test_cases:
            excel_result = excel(*values[0])
            bq_result = bq(values[0])
            match = "MATCH" if abs(excel_result - bq_result) < 1e-10 else "DIFF"
            print(f"  SUM({values[0]}): Excel={excel_result}, BQ={bq_result} [{match}]")
            self.assertAlmostEqual(excel_result, bq_result, places=10)

    def test_average_comparison(self):
        """AVERAGE 함수 비교"""
        excel = ExcelFormulaEmulator.excel_average
        bq = BigQuerySQLEmulator.bq_avg

        test_cases = [
            [10, 20, 30],
            [10, None, 30],
            [None, None, None],
        ]

        print("\n[AVERAGE 함수 비교]")
        for values in test_cases:
            excel_result = excel(*values)
            bq_result = bq(values)
            if excel_result is None and bq_result is None:
                match = "MATCH"
            elif excel_result is None or bq_result is None:
                match = "DIFF"
            else:
                match = "MATCH" if abs(excel_result - bq_result) < 1e-10 else "DIFF"
            print(f"  AVG({values}): Excel={excel_result}, BQ={bq_result} [{match}]")

    def test_score_judgment_comparison(self):
        """적정점수 판정 로직 비교"""
        test_cases = [
            # (current, optimal, expected, conservative, expected_result)
            (80, 70, 60, 50, "적정점수 이상"),
            (65, 70, 60, 50, "예상점수 이상"),
            (55, 70, 60, 50, "소신점수 이상"),
            (45, 70, 60, 50, "소신점수 미만"),
            (70, 70, 60, 50, "적정점수 이상"),  # 경계값
            (60, 70, 60, 50, "예상점수 이상"),  # 경계값
            (50, 70, 60, 50, "소신점수 이상"),  # 경계값
        ]

        print("\n[적정점수 판정 로직 비교]")
        for current, optimal, expected, conservative, exp_result in test_cases:
            # Excel 에뮬레이션
            if current >= optimal:
                excel_result = "적정점수 이상"
            elif current >= expected:
                excel_result = "예상점수 이상"
            elif current >= conservative:
                excel_result = "소신점수 이상"
            else:
                excel_result = "소신점수 미만"

            # BigQuery CASE WHEN 에뮬레이션
            bq_result = BigQuerySQLEmulator.bq_case_when([
                (current >= optimal, "적정점수 이상"),
                (current >= expected, "예상점수 이상"),
                (current >= conservative, "소신점수 이상"),
                (current < conservative, "소신점수 미만"),
            ])

            match = "MATCH" if excel_result == bq_result == exp_result else "DIFF"
            print(f"  Score({current}): Excel={excel_result}, BQ={bq_result} [{match}]")
            self.assertEqual(excel_result, bq_result)
            self.assertEqual(excel_result, exp_result)


class TestSQLGeneration(unittest.TestCase):
    """BigQuery SQL 생성 테스트"""

    def test_generate_score_judgment_sql(self):
        """적정점수 판정 SQL 생성"""
        sql = FormulaTranslator.translate_score_judgment(
            'current_score', 'optimal_score', 'expected_score', 'conservative_score'
        )

        expected_keywords = [
            'CASE', 'WHEN', 'THEN', 'ELSE', 'END',
            '적정점수 이상', '예상점수 이상', '소신점수 이상', '소신점수 미만'
        ]

        for keyword in expected_keywords:
            self.assertIn(keyword, sql)

        print("\n[생성된 적정점수 판정 SQL]")
        print(sql)

    def test_generate_sum_sql(self):
        """SUM SQL 생성"""
        sql = FormulaTranslator.translate_sum('col_e', 'col_f')

        self.assertIn('COALESCE', sql)
        self.assertIn('col_e', sql)
        self.assertIn('col_f', sql)

        print("\n[생성된 SUM SQL]")
        print(sql)

    def test_generate_average_sql(self):
        """AVERAGE SQL 생성"""
        sql = FormulaTranslator.translate_average_with_min('col_h1', 'col_h2')

        self.assertIn('GREATEST', sql)
        self.assertIn('0.00001', sql)
        self.assertIn('COALESCE', sql)

        print("\n[생성된 AVERAGE SQL]")
        print(sql)


class TestNullHandling(unittest.TestCase):
    """NULL 처리 비교 테스트"""

    def test_excel_null_in_sum(self):
        """Excel: SUM에서 NULL/빈값 처리"""
        # Excel SUM은 빈 셀을 0으로 처리
        result = ExcelFormulaEmulator.excel_sum(10, None, "", 20)
        self.assertEqual(result, 30)

    def test_bq_null_in_sum(self):
        """BigQuery: SUM에서 NULL 처리"""
        # BigQuery SUM은 NULL을 무시
        result = BigQuerySQLEmulator.bq_sum([10, None, 20])
        self.assertEqual(result, 30)

    def test_excel_iferror(self):
        """Excel IFERROR 동작"""
        self.assertEqual(ExcelFormulaEmulator.excel_iferror(10, 0), 10)
        self.assertEqual(ExcelFormulaEmulator.excel_iferror(None, 0), 0)

    def test_bq_ifnull(self):
        """BigQuery IFNULL 동작"""
        self.assertEqual(BigQuerySQLEmulator.bq_ifnull(10, 0), 10)
        self.assertEqual(BigQuerySQLEmulator.bq_ifnull(None, 0), 0)

    def test_bq_coalesce(self):
        """BigQuery COALESCE 동작"""
        self.assertEqual(BigQuerySQLEmulator.bq_coalesce(None, None, 10), 10)
        self.assertEqual(BigQuerySQLEmulator.bq_coalesce(5, None, 10), 5)
        self.assertIsNone(BigQuerySQLEmulator.bq_coalesce(None, None, None))


class TestDataTypeConversion(unittest.TestCase):
    """데이터 타입 변환 테스트"""

    def test_string_to_number_excel(self):
        """Excel: 문자열 -> 숫자 변환 (*1 트릭)"""
        # Excel에서 "70" * 1 = 70
        value = "70"
        result = float(value) * 1
        self.assertEqual(result, 70.0)

    def test_string_to_number_bigquery(self):
        """BigQuery: CAST 또는 SAFE_CAST"""
        # BigQuery에서 SAFE_CAST('70' AS FLOAT64) = 70.0
        value = "70"
        try:
            result = float(value)
        except ValueError:
            result = None
        self.assertEqual(result, 70.0)

    def test_excel_date_serial(self):
        """Excel 날짜 시리얼 변환"""
        # Excel에서 45000 = 2023-03-15
        serial = 45000
        # Python에서 Excel 시리얼 변환
        import datetime
        excel_epoch = datetime.date(1899, 12, 30)
        result = excel_epoch + datetime.timedelta(days=serial)
        self.assertEqual(result.year, 2023)

    def test_bigquery_date_format(self):
        """BigQuery 날짜 형식"""
        # BigQuery에서 DATE('2023-03-15')
        import datetime
        date_str = '2023-03-15'
        result = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
        self.assertEqual(result.year, 2023)
        self.assertEqual(result.month, 3)
        self.assertEqual(result.day, 15)


def run_cross_validation_tests():
    """전체 교차 검증 테스트 실행"""
    print("=" * 70)
    print("NEO GOD Ultra Excel vs BigQuery 교차 검증 테스트")
    print("=" * 70)

    # 테스트 스위트 생성
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    suite.addTests(loader.loadTestsFromTestCase(TestExcelBigQueryComparison))
    suite.addTests(loader.loadTestsFromTestCase(TestSQLGeneration))
    suite.addTests(loader.loadTestsFromTestCase(TestNullHandling))
    suite.addTests(loader.loadTestsFromTestCase(TestDataTypeConversion))

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

    # 주의 사항 출력
    print("\n[주의] Excel vs BigQuery 차이점:")
    print("  1. ROUND: Excel은 사사오입, BigQuery는 banker's rounding")
    print("  2. NULL 처리: Excel은 빈 셀=0, BigQuery는 NULL 유지")
    print("  3. 문자열 비교: Excel은 대소문자 무시, BigQuery는 구분")

    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_cross_validation_tests()
    sys.exit(0 if success else 1)
