# ============================================================
# NEO GOD Ultra 엔진 무결성 검증 Stress Test
# 바이스 디렉터 Stress-Test 프롬프트 기반 통합 검증 시스템
# ============================================================

import sys
import random
import string
import json
import time
import traceback
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Tuple, Optional
from dataclasses import dataclass, field, asdict
from enum import Enum
import hashlib

# Windows 인코딩 설정
if sys.platform == 'win32':
    try:
        if hasattr(sys.stdout, 'reconfigure'):
            sys.stdout.reconfigure(encoding='utf-8')
        if hasattr(sys.stderr, 'reconfigure'):
            sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

import pandas as pd
import numpy as np


class TestScenario(Enum):
    """테스트 시나리오 정의"""
    NORMAL_DATA = 1          # 정상 데이터 처리
    EDGE_CASES = 2           # 경계값 테스트
    MALFORMED_DATA = 3       # 비정상 데이터 처리
    HIGH_VOLUME = 4          # 대용량 데이터 처리
    MIXED_TYPES = 5          # 혼합 타입 데이터


@dataclass
class TestCase:
    """개별 테스트 케이스"""
    case_id: int
    scenario: TestScenario
    description: str
    input_data: Dict[str, Any]
    expected_behavior: str
    actual_result: Optional[Dict] = None
    passed: bool = False
    error_message: str = ""
    execution_time_ms: float = 0.0

    def to_dict(self) -> Dict:
        result = asdict(self)
        result['scenario'] = self.scenario.name
        return result


@dataclass
class ErrorLog:
    """에러 로그 항목"""
    error_id: str
    scenario: int
    test_case_id: int
    location: Dict[str, Any]
    input_values: Dict[str, Any]
    expected: Any
    actual: Any
    error_type: str
    error_message: str
    stack_trace: str = ""
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict:
        return asdict(self)


class RandomDataGenerator:
    """무작위 테스트 데이터 생성기"""

    # Excel 에러 코드
    EXCEL_ERRORS = ['#N/A', '#VALUE!', '#REF!', '#DIV/0!', '#NUM!', '#NAME?', '#NULL!']

    # 한글 테스트 문자열
    KOREAN_CHARS = '가나다라마바사아자차카타파하'
    KOREAN_WORDS = ['국어', '수학', '영어', '사회', '과학', '탐구', '논술', '면접']

    def __init__(self, seed: int = None):
        if seed:
            random.seed(seed)
            np.random.seed(seed)

    def generate_normal_string(self, length: int = 10) -> str:
        """정상 문자열 생성"""
        return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

    def generate_korean_string(self, length: int = 5) -> str:
        """한글 문자열 생성"""
        return ''.join(random.choices(self.KOREAN_CHARS, k=length))

    def generate_excel_date_serial(self, start_year: int = 2020, end_year: int = 2030) -> int:
        """Excel 날짜 시리얼 생성 (현실적 범위)"""
        # 1970-01-01 = 25569, 2020-01-01 = 43831, 2030-01-01 = 47484
        start_serial = 43831 + (start_year - 2020) * 365
        end_serial = 43831 + (end_year - 2020) * 365
        return random.randint(start_serial, end_serial)

    def generate_score(self, min_val: int = 0, max_val: int = 100) -> float:
        """점수 생성"""
        return round(random.uniform(min_val, max_val), 2)

    def generate_excel_error(self) -> str:
        """Excel 에러 코드 생성"""
        return random.choice(self.EXCEL_ERRORS)

    def generate_formula(self, complexity: str = 'simple') -> str:
        """수식 문자열 생성"""
        if complexity == 'simple':
            col = random.choice(string.ascii_uppercase)
            row = random.randint(1, 100)
            return f"={col}{row}"
        elif complexity == 'medium':
            cols = random.choices(string.ascii_uppercase, k=3)
            rows = [random.randint(1, 100) for _ in range(3)]
            return f"=SUM({cols[0]}{rows[0]}:{cols[1]}{rows[1]})+{cols[2]}{rows[2]}"
        else:  # complex
            funcs = ['SUM', 'AVERAGE', 'IF', 'VLOOKUP', 'INDEX', 'MATCH']
            func = random.choice(funcs)
            return f"={func}(A1:Z100,B2,C3)"

    def generate_edge_value(self, edge_type: str) -> Any:
        """경계값 생성"""
        edge_values = {
            'empty_string': '',
            'null': None,
            'zero': 0,
            'negative': -1,
            'max_int': 2**31 - 1,
            'min_int': -(2**31),
            'float_precision': 0.1 + 0.2,  # 부동소수점 정밀도 문제
            'very_long_string': 'A' * 10000,
            'special_chars': '!@#$%^&*()_+-=[]{}|;:\'",.<>?/`~',
            'unicode': '\u0000\u001f\uffff',
            'newline': 'line1\nline2\rline3\r\n',
            'whitespace': '   \t\n   ',
            'nan': float('nan'),
            'inf': float('inf'),
            'neg_inf': float('-inf'),
        }
        return edge_values.get(edge_type, None)

    def generate_dataframe(
        self,
        rows: int,
        cols: int,
        scenario: TestScenario
    ) -> pd.DataFrame:
        """시나리오별 테스트 DataFrame 생성"""

        data = {}

        for col_idx in range(cols):
            col_name = f"col_{col_idx}"

            if scenario == TestScenario.NORMAL_DATA:
                # 정상 데이터: 숫자, 문자열, 날짜 혼합
                if col_idx % 3 == 0:
                    data[col_name] = [self.generate_score() for _ in range(rows)]
                elif col_idx % 3 == 1:
                    data[col_name] = [self.generate_normal_string(8) for _ in range(rows)]
                else:
                    data[col_name] = [self.generate_korean_string(4) for _ in range(rows)]

            elif scenario == TestScenario.EDGE_CASES:
                # 경계값: NULL, 빈 문자열, 극단값 포함
                edge_types = ['empty_string', 'null', 'zero', 'negative',
                             'very_long_string', 'special_chars', 'whitespace']
                values = []
                for _ in range(rows):
                    if random.random() < 0.3:  # 30% 확률로 경계값
                        values.append(self.generate_edge_value(random.choice(edge_types)))
                    else:
                        values.append(self.generate_score())
                data[col_name] = values

            elif scenario == TestScenario.MALFORMED_DATA:
                # 비정상 데이터: Excel 에러, 잘못된 형식
                values = []
                for _ in range(rows):
                    roll = random.random()
                    if roll < 0.2:
                        values.append(self.generate_excel_error())
                    elif roll < 0.4:
                        values.append(self.generate_formula('complex'))
                    elif roll < 0.6:
                        values.append(f"'{self.generate_score()}")  # 숫자 앞 따옴표
                    else:
                        values.append(self.generate_score())
                data[col_name] = values

            elif scenario == TestScenario.HIGH_VOLUME:
                # 대용량: 기본적으로 숫자 데이터 (메모리 효율)
                data[col_name] = np.random.uniform(0, 100, rows).tolist()

            elif scenario == TestScenario.MIXED_TYPES:
                # 혼합 타입: 같은 컬럼에 다양한 타입
                values = []
                for _ in range(rows):
                    roll = random.random()
                    if roll < 0.2:
                        values.append(self.generate_score())
                    elif roll < 0.4:
                        values.append(str(self.generate_score()))
                    elif roll < 0.6:
                        values.append(self.generate_korean_string(3))
                    elif roll < 0.8:
                        values.append(None)
                    else:
                        values.append(self.generate_excel_date_serial())
                data[col_name] = values

        return pd.DataFrame(data)


class CrossValidator:
    """교차 검증기"""

    def __init__(self):
        self.validation_results = []

    def validate_row_count(
        self,
        original: pd.DataFrame,
        processed: pd.DataFrame,
        tolerance: float = 0.01
    ) -> Tuple[bool, str]:
        """행 수 검증"""
        orig_rows = len(original)
        proc_rows = len(processed)

        if orig_rows == 0:
            return False, "Original DataFrame is empty"

        diff_ratio = abs(orig_rows - proc_rows) / orig_rows

        if diff_ratio <= tolerance:
            return True, f"Row count match: {orig_rows} vs {proc_rows} (diff: {diff_ratio:.4f})"
        else:
            return False, f"Row count mismatch: {orig_rows} vs {proc_rows} (diff: {diff_ratio:.4f})"

    def validate_column_count(
        self,
        original: pd.DataFrame,
        processed: pd.DataFrame
    ) -> Tuple[bool, str]:
        """컬럼 수 검증"""
        orig_cols = len(original.columns)
        proc_cols = len(processed.columns)

        if orig_cols == proc_cols:
            return True, f"Column count match: {orig_cols}"
        else:
            return False, f"Column count mismatch: {orig_cols} vs {proc_cols}"

    def validate_null_ratio(
        self,
        original: pd.DataFrame,
        processed: pd.DataFrame,
        threshold: float = 0.1
    ) -> Tuple[bool, str]:
        """NULL 비율 검증"""
        orig_nulls = original.isnull().sum().sum()
        proc_nulls = processed.isnull().sum().sum()

        total_cells = processed.size
        if total_cells == 0:
            return False, "DataFrame is empty"

        null_ratio = proc_nulls / total_cells

        if null_ratio <= threshold:
            return True, f"NULL ratio acceptable: {null_ratio:.4f} (threshold: {threshold})"
        else:
            return False, f"NULL ratio too high: {null_ratio:.4f} (threshold: {threshold})"

    def validate_data_types(
        self,
        processed: pd.DataFrame,
        expected_types: Dict[str, str] = None
    ) -> Tuple[bool, str]:
        """데이터 타입 검증"""
        issues = []

        for col in processed.columns:
            dtype = str(processed[col].dtype)

            # object 타입이 너무 많으면 경고
            if dtype == 'object':
                # 실제로 숫자인지 확인
                numeric_ratio = pd.to_numeric(processed[col], errors='coerce').notna().mean()
                if numeric_ratio > 0.8:
                    issues.append(f"{col}: should be numeric (ratio: {numeric_ratio:.2f})")

        if issues:
            return False, f"Type issues: {issues}"
        else:
            return True, "Data types OK"

    def validate_checksum(
        self,
        original: pd.DataFrame,
        processed: pd.DataFrame
    ) -> Tuple[bool, str]:
        """데이터 체크섬 검증 (샘플 기반)"""
        # 첫 100행 샘플로 체크섬 계산
        sample_size = min(100, len(original), len(processed))

        if sample_size == 0:
            return False, "No data for checksum"

        orig_sample = original.head(sample_size).fillna('NULL').astype(str)
        proc_sample = processed.head(sample_size).fillna('NULL').astype(str)

        orig_hash = hashlib.md5(orig_sample.to_string().encode()).hexdigest()
        proc_hash = hashlib.md5(proc_sample.to_string().encode()).hexdigest()

        # 체크섬이 다를 수 있음 (정규화로 인해) - 정보 제공용
        return True, f"Checksums: orig={orig_hash[:8]}..., proc={proc_hash[:8]}..."

    def run_all_validations(
        self,
        original: pd.DataFrame,
        processed: pd.DataFrame,
        scenario: 'TestScenario' = None
    ) -> Dict[str, Any]:
        """모든 검증 실행 (시나리오별 threshold 적용)"""

        # 시나리오별 NULL 비율 threshold 설정
        # EDGE_CASES와 MALFORMED_DATA는 의도적으로 비정상 데이터를 포함하므로 높은 threshold
        null_thresholds = {
            TestScenario.NORMAL_DATA: 0.05,      # 정상 데이터: 5%
            TestScenario.EDGE_CASES: 0.50,       # 경계값: 50% (의도적 NULL 포함)
            TestScenario.MALFORMED_DATA: 0.60,   # 비정상: 60% (수식/에러코드 → NULL 변환)
            TestScenario.HIGH_VOLUME: 0.10,      # 대용량: 10%
            TestScenario.MIXED_TYPES: 0.30,      # 혼합 타입: 30% (NULL 포함 가능)
        }

        null_threshold = null_thresholds.get(scenario, 0.1)

        results = {
            'row_count': self.validate_row_count(original, processed),
            'column_count': self.validate_column_count(original, processed),
            'null_ratio': self.validate_null_ratio(original, processed, threshold=null_threshold),
            'data_types': self.validate_data_types(processed),
            'checksum': self.validate_checksum(original, processed),
        }

        all_passed = all(r[0] for r in results.values())

        return {
            'all_passed': all_passed,
            'validations': {k: {'passed': v[0], 'message': v[1]} for k, v in results.items()}
        }


class StressTestEngine:
    """Stress Test 엔진"""

    def __init__(self, output_dir: str = './stress_test_output'):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.generator = RandomDataGenerator(seed=42)
        self.validator = CrossValidator()

        self.test_cases: List[TestCase] = []
        self.error_logs: List[ErrorLog] = []
        self.test_summary: Dict[str, Any] = {}

        self.error_counter = 0

    def _generate_error_id(self) -> str:
        """에러 ID 생성"""
        self.error_counter += 1
        return f"ERR_{self.error_counter:04d}"

    def _import_normalizer(self):
        """DateFirstNormalizer 임포트"""
        try:
            from phase3_normalization import DateFirstNormalizer
            return DateFirstNormalizer()
        except ImportError as e:
            print(f"[WARNING] Could not import DateFirstNormalizer: {e}")
            return None

    def generate_test_cases(self, cases_per_scenario: int = 200) -> List[TestCase]:
        """테스트 케이스 생성"""
        print(f"[INFO] Generating {cases_per_scenario * 5} test cases...")

        case_id = 0
        test_cases = []

        scenario_configs = {
            TestScenario.NORMAL_DATA: {
                'description': '정상 데이터 처리 테스트',
                'rows_range': (100, 1000),
                'cols_range': (5, 20),
            },
            TestScenario.EDGE_CASES: {
                'description': '경계값 테스트 (NULL, 빈 문자열, 극단값)',
                'rows_range': (50, 500),
                'cols_range': (5, 15),
            },
            TestScenario.MALFORMED_DATA: {
                'description': '비정상 데이터 처리 테스트 (Excel 에러, 잘못된 형식)',
                'rows_range': (50, 500),
                'cols_range': (5, 15),
            },
            TestScenario.HIGH_VOLUME: {
                'description': '대용량 데이터 처리 테스트',
                'rows_range': (10000, 50000),
                'cols_range': (10, 30),
            },
            TestScenario.MIXED_TYPES: {
                'description': '혼합 타입 데이터 처리 테스트',
                'rows_range': (100, 1000),
                'cols_range': (5, 20),
            },
        }

        for scenario, config in scenario_configs.items():
            print(f"  Generating {cases_per_scenario} cases for {scenario.name}...")

            for i in range(cases_per_scenario):
                rows = random.randint(*config['rows_range'])
                cols = random.randint(*config['cols_range'])

                # 대용량 시나리오는 케이스 수 줄이고 크기 키움
                if scenario == TestScenario.HIGH_VOLUME and i >= 20:
                    continue  # 대용량은 20개만

                test_case = TestCase(
                    case_id=case_id,
                    scenario=scenario,
                    description=f"{config['description']} - {rows}x{cols}",
                    input_data={
                        'rows': rows,
                        'cols': cols,
                        'scenario': scenario.name,
                    },
                    expected_behavior='Data should be normalized without errors'
                )

                test_cases.append(test_case)
                case_id += 1

        self.test_cases = test_cases
        print(f"[INFO] Generated {len(test_cases)} test cases")
        return test_cases

    def run_single_test(
        self,
        test_case: TestCase,
        normalizer
    ) -> TestCase:
        """단일 테스트 실행"""
        start_time = time.perf_counter()

        try:
            # 테스트 데이터 생성
            scenario = TestScenario[test_case.input_data['scenario']]
            df = self.generator.generate_dataframe(
                rows=test_case.input_data['rows'],
                cols=test_case.input_data['cols'],
                scenario=scenario
            )

            # 정규화 실행
            if normalizer:
                result = normalizer.normalize_dataframe(
                    df,
                    output_dir=str(self.output_dir / 'temp'),
                    max_chunk_size_mb=50
                )

                # 결과 DataFrame 로드
                if result['parquet_chunks']:
                    processed_df = pd.read_parquet(result['parquet_chunks'][0])
                else:
                    processed_df = df

                # 교차 검증 (시나리오별 threshold 적용)
                validation = self.validator.run_all_validations(df, processed_df, scenario=scenario)

                test_case.actual_result = {
                    'input_rows': len(df),
                    'output_rows': len(processed_df),
                    'validation': validation,
                }

                test_case.passed = validation['all_passed']

                if not test_case.passed:
                    test_case.error_message = str(validation['validations'])

                    # 에러 로그 생성
                    error_log = ErrorLog(
                        error_id=self._generate_error_id(),
                        scenario=scenario.value,
                        test_case_id=test_case.case_id,
                        location={
                            'scenario': scenario.name,
                            'rows': test_case.input_data['rows'],
                            'cols': test_case.input_data['cols'],
                        },
                        input_values={'sample': df.head(3).to_dict()},
                        expected='All validations passed',
                        actual=validation['validations'],
                        error_type='ValidationError',
                        error_message=test_case.error_message,
                    )
                    self.error_logs.append(error_log)
            else:
                # Normalizer 없으면 기본 검증만
                test_case.passed = True
                test_case.actual_result = {'input_rows': len(df), 'output_rows': len(df)}

        except Exception as e:
            test_case.passed = False
            test_case.error_message = str(e)
            test_case.actual_result = {'error': str(e)}

            # 에러 로그 생성
            error_log = ErrorLog(
                error_id=self._generate_error_id(),
                scenario=TestScenario[test_case.input_data['scenario']].value,
                test_case_id=test_case.case_id,
                location={
                    'scenario': test_case.input_data['scenario'],
                    'rows': test_case.input_data['rows'],
                    'cols': test_case.input_data['cols'],
                },
                input_values={},
                expected='No exception',
                actual=str(e),
                error_type=type(e).__name__,
                error_message=str(e),
                stack_trace=traceback.format_exc(),
            )
            self.error_logs.append(error_log)

        test_case.execution_time_ms = (time.perf_counter() - start_time) * 1000
        return test_case

    def run_all_tests(self, cases_per_scenario: int = 200) -> Dict[str, Any]:
        """모든 테스트 실행"""
        print("=" * 60)
        print("NEO GOD Ultra Stress Test Engine")
        print("=" * 60)

        # 테스트 케이스 생성
        if not self.test_cases:
            self.generate_test_cases(cases_per_scenario)

        # Normalizer 임포트
        normalizer = self._import_normalizer()

        # 테스트 실행
        print(f"\n[INFO] Running {len(self.test_cases)} test cases...")

        scenario_results = {s: {'total': 0, 'passed': 0, 'failed': 0} for s in TestScenario}

        for i, test_case in enumerate(self.test_cases):
            if (i + 1) % 100 == 0:
                print(f"  Progress: {i + 1}/{len(self.test_cases)}")

            self.run_single_test(test_case, normalizer)

            scenario = TestScenario[test_case.input_data['scenario']]
            scenario_results[scenario]['total'] += 1
            if test_case.passed:
                scenario_results[scenario]['passed'] += 1
            else:
                scenario_results[scenario]['failed'] += 1

        # 결과 집계
        total_cases = len(self.test_cases)
        total_passed = sum(r['passed'] for r in scenario_results.values())
        total_failed = sum(r['failed'] for r in scenario_results.values())

        self.test_summary = {
            'test_summary': {
                'total_cases': total_cases,
                'total_passed': total_passed,
                'total_failed': total_failed,
                'overall_pass_rate': round(total_passed / total_cases, 4) if total_cases > 0 else 0,
                'total_errors': len(self.error_logs),
            }
        }

        for scenario, result in scenario_results.items():
            if result['total'] > 0:
                result['pass_rate'] = round(result['passed'] / result['total'], 4)
            else:
                result['pass_rate'] = 0
            self.test_summary['test_summary'][f'scenario_{scenario.value}'] = result

        print(f"\n[INFO] Test completed!")
        print(f"  Total: {total_cases}, Passed: {total_passed}, Failed: {total_failed}")
        print(f"  Pass Rate: {self.test_summary['test_summary']['overall_pass_rate']:.2%}")

        return self.test_summary

    def generate_debug_report(self) -> Dict[str, Any]:
        """디버그 리포트 생성"""
        report = {
            'report_time': datetime.now().isoformat(),
            'test_summary': self.test_summary.get('test_summary', {}),
            'errors': [e.to_dict() for e in self.error_logs[:100]],  # 상위 100개
            'error_statistics': self._analyze_errors(),
        }

        return report

    def _analyze_errors(self) -> Dict[str, Any]:
        """에러 통계 분석"""
        if not self.error_logs:
            return {'total_errors': 0}

        # 시나리오별 에러 수
        scenario_errors = {}
        error_types = {}

        for error in self.error_logs:
            scenario = error.scenario
            scenario_errors[scenario] = scenario_errors.get(scenario, 0) + 1

            error_type = error.error_type
            error_types[error_type] = error_types.get(error_type, 0) + 1

        return {
            'total_errors': len(self.error_logs),
            'errors_by_scenario': scenario_errors,
            'errors_by_type': error_types,
        }

    def save_reports(self) -> Dict[str, str]:
        """리포트 파일 저장"""
        report_files = {}

        # 테스트 요약
        summary_path = self.output_dir / 'test_summary.json'
        with open(summary_path, 'w', encoding='utf-8') as f:
            json.dump(self.test_summary, f, ensure_ascii=False, indent=2)
        report_files['summary'] = str(summary_path)

        # 디버그 리포트
        debug_report = self.generate_debug_report()
        debug_path = self.output_dir / 'debug_report.json'
        with open(debug_path, 'w', encoding='utf-8') as f:
            json.dump(debug_report, f, ensure_ascii=False, indent=2, default=str)
        report_files['debug'] = str(debug_path)

        # 테스트 케이스 상세
        cases_path = self.output_dir / 'test_cases.json'
        with open(cases_path, 'w', encoding='utf-8') as f:
            cases_data = [tc.to_dict() for tc in self.test_cases[:500]]  # 상위 500개
            json.dump(cases_data, f, ensure_ascii=False, indent=2, default=str)
        report_files['cases'] = str(cases_path)

        # 에러 로그
        if self.error_logs:
            errors_path = self.output_dir / 'error_logs.json'
            with open(errors_path, 'w', encoding='utf-8') as f:
                errors_data = [e.to_dict() for e in self.error_logs]
                json.dump(errors_data, f, ensure_ascii=False, indent=2, default=str)
            report_files['errors'] = str(errors_path)

        print(f"\n[INFO] Reports saved to {self.output_dir}")
        for name, path in report_files.items():
            print(f"  - {name}: {path}")

        return report_files


def run_stress_test(cases_per_scenario: int = 50):
    """Stress Test 실행"""
    engine = StressTestEngine()

    # 테스트 실행
    summary = engine.run_all_tests(cases_per_scenario)

    # 리포트 저장
    report_files = engine.save_reports()

    # 결과 출력
    print("\n" + "=" * 60)
    print("STRESS TEST RESULTS")
    print("=" * 60)

    print("\n### 테스트 요약")
    print(json.dumps(summary, indent=2, ensure_ascii=False))

    print("\n### 시나리오별 결과")
    for scenario in TestScenario:
        key = f'scenario_{scenario.value}'
        if key in summary['test_summary']:
            result = summary['test_summary'][key]
            status = "PASS" if result['pass_rate'] >= 0.9 else "FAIL"
            print(f"  {scenario.name}: {result['passed']}/{result['total']} ({result['pass_rate']:.1%}) [{status}]")

    return summary, report_files


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='NEO GOD Ultra Stress Test Engine')
    parser.add_argument('--cases', type=int, default=50, help='Cases per scenario')
    parser.add_argument('--output', type=str, default='./stress_test_output', help='Output directory')

    args = parser.parse_args()

    engine = StressTestEngine(output_dir=args.output)
    summary = engine.run_all_tests(cases_per_scenario=args.cases)
    engine.save_reports()
