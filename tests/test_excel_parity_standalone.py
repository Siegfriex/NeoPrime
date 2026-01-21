"""
Excel Parity Test (Standalone) - xlwings 없이 실행 가능

Ground Truth JSON 기반으로 Python 계산 결과를 검증합니다.

사용법:
    pytest tests/test_excel_parity_standalone.py -v

전제 조건:
    - tests/fixtures/ground_truth.json 존재 (collect_ground_truth.py로 생성)
    - theory_engine/weights/subject3_conversions_full.json 존재

SSOT 문서 기준:
    - 절대 오차: 1e-6 이하
    - 상대 오차: 1e-9 이하 (둘 다 만족해야 함)
    - 성공 기준: 90% 이상 통과
"""

import sys
import os
import json
import pytest
from pathlib import Path
from typing import Dict, List, Tuple, Optional

# 프로젝트 루트를 path에 추가
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


# 상수 정의
ABS_TOLERANCE = 1e-6  # 절대 오차 허용치
REL_TOLERANCE = 1e-9  # 상대 오차 허용치
PASS_RATE_THRESHOLD = 0.90  # 90% 통과율 기준

GROUND_TRUTH_PATH = PROJECT_ROOT / "tests" / "fixtures" / "ground_truth.json"
CONVERSIONS_PATH = PROJECT_ROOT / "theory_engine" / "weights" / "subject3_conversions_full.json"


def is_strict_parity(expected: float, calculated: float) -> Tuple[bool, Dict]:
    """
    엄격한 Parity 검증: abs + rel 동시 만족 필요

    Returns:
        (passed: bool, metrics: dict)
    """
    if expected is None or calculated is None:
        return False, {"error": "None value", "passed": False}

    abs_err = abs(expected - calculated)
    denominator = max(abs(expected), abs(calculated), 1e-15)
    rel_err = abs_err / denominator

    passed = (abs_err < ABS_TOLERANCE) and (rel_err < REL_TOLERANCE)

    return passed, {
        "abs_error": abs_err,
        "rel_error": rel_err,
        "abs_threshold": ABS_TOLERANCE,
        "rel_threshold": REL_TOLERANCE,
        "passed": passed
    }


class ParityTestRunner:
    """독립 Parity Test 실행기"""

    def __init__(self):
        self.ground_truth = None
        self.conversions = None
        self.results = []

    def load_ground_truth(self) -> bool:
        """Ground Truth JSON 로드"""
        if not GROUND_TRUTH_PATH.exists():
            print(f"WARNING: Ground Truth 파일 없음: {GROUND_TRUTH_PATH}")
            print("해결 방법: python tools/collect_ground_truth.py 실행")
            return False

        with open(GROUND_TRUTH_PATH, 'r', encoding='utf-8') as f:
            self.ground_truth = json.load(f)

        print(f"Ground Truth 로드: {len(self.ground_truth.get('ground_truth', []))}개 케이스")
        return True

    def load_conversions(self) -> bool:
        """환산점수 테이블 로드"""
        # subject3_conversions_full.json 우선, 없으면 기존 파일 사용
        if CONVERSIONS_PATH.exists():
            path = CONVERSIONS_PATH
        else:
            path = PROJECT_ROOT / "theory_engine" / "weights" / "subject3_conversions.json"
            if not path.exists():
                print(f"WARNING: 환산점수 테이블 없음")
                return False

        with open(path, 'r', encoding='utf-8') as f:
            self.conversions = json.load(f)

        print(f"환산점수 테이블 로드: {len(self.conversions.get('conversion_table', {}))}개 대학")
        return True

    def calculate_python_result(self, case: Dict) -> Optional[float]:
        """
        Python으로 환산점수 계산 (JSON 테이블 기반)

        Ground Truth 케이스에서 입력값과 대학/학과를 받아서
        환산점수를 조회하고 합산합니다.
        """
        university = case.get("university", "")
        department = case.get("department", "")
        input_data = case.get("input", {})
        expected = case.get("expected", {})
        required_subjects = expected.get("required_subjects", "국수영탐(2)")

        # 대학/학과 키
        key = f"{university}_{department}"
        if key not in self.conversions.get("conversion_table", {}):
            return None

        table = self.conversions["conversion_table"][key]
        conversions = table.get("conversions", {})

        total = 0.0

        # 국어
        if "국" in required_subjects:
            score_key = f"국어-{int(input_data.get('korean', 0))}"
            if score_key in conversions:
                total += float(conversions[score_key])

        # 수학
        if "수" in required_subjects:
            score_key = f"수학-{int(input_data.get('math', 0))}"
            if score_key in conversions:
                total += float(conversions[score_key])

        # 영어
        if "영" in required_subjects:
            score_key = f"영어-{int(input_data.get('english_grade', 1))}"
            if score_key in conversions:
                total += float(conversions[score_key])

        # 탐구 (실제 과목명 또는 일반 키)
        if "탐" in required_subjects:
            inquiry1_subj = input_data.get("inquiry1_subject", "탐구1")
            inquiry2_subj = input_data.get("inquiry2_subject", "탐구2")
            inquiry1_score = input_data.get("inquiry1", 0)
            inquiry2_score = input_data.get("inquiry2", 0)

            # 탐구1
            score_key = f"{inquiry1_subj}-{int(inquiry1_score)}"
            if score_key in conversions:
                total += float(conversions[score_key])
            else:
                # 일반 키로 시도
                score_key = f"탐구1-{int(inquiry1_score)}"
                if score_key in conversions:
                    total += float(conversions[score_key])

            # 탐구2 (2과목 필요시)
            if "(2)" in required_subjects or "탐(2)" in required_subjects:
                score_key = f"{inquiry2_subj}-{int(inquiry2_score)}"
                if score_key in conversions:
                    total += float(conversions[score_key])
                else:
                    score_key = f"탐구2-{int(inquiry2_score)}"
                    if score_key in conversions:
                        total += float(conversions[score_key])

        return total

    def run_all_tests(self) -> Dict:
        """전체 Parity Test 실행"""
        if not self.ground_truth:
            return {"error": "Ground Truth 미로드"}
        if not self.conversions:
            return {"error": "환산점수 테이블 미로드"}

        passed_count = 0
        failed_count = 0
        skipped_count = 0
        details = []

        for case in self.ground_truth.get("ground_truth", []):
            # Python 계산
            python_result = self.calculate_python_result(case)

            # Excel 기대값
            excel_result = case.get("expected", {}).get("row59_total")

            if python_result is None or excel_result is None:
                skipped_count += 1
                details.append({
                    "case_name": case.get("case_name"),
                    "university": case.get("university"),
                    "department": case.get("department"),
                    "status": "SKIP",
                    "reason": "Missing data"
                })
                continue

            # Parity 검증
            passed, metrics = is_strict_parity(excel_result, python_result)

            if passed:
                passed_count += 1
                status = "PASS"
            else:
                failed_count += 1
                status = "FAIL"

            details.append({
                "case_name": case.get("case_name"),
                "university": case.get("university"),
                "department": case.get("department"),
                "excel_result": excel_result,
                "python_result": python_result,
                "status": status,
                "metrics": metrics
            })

        total = passed_count + failed_count
        pass_rate = passed_count / total if total > 0 else 0

        return {
            "passed": passed_count,
            "failed": failed_count,
            "skipped": skipped_count,
            "total": total,
            "pass_rate": pass_rate,
            "threshold_met": pass_rate >= PASS_RATE_THRESHOLD,
            "details": details
        }


# Pytest 테스트 함수들

@pytest.fixture(scope="module")
def parity_runner():
    """Parity Test Runner fixture"""
    runner = ParityTestRunner()
    return runner


@pytest.fixture(scope="module")
def ground_truth_loaded(parity_runner):
    """Ground Truth 로드 fixture"""
    return parity_runner.load_ground_truth()


@pytest.fixture(scope="module")
def conversions_loaded(parity_runner):
    """환산점수 테이블 로드 fixture"""
    return parity_runner.load_conversions()


@pytest.mark.skipif(
    not GROUND_TRUTH_PATH.exists(),
    reason="Ground Truth 파일 없음 - collect_ground_truth.py 실행 필요"
)
def test_ground_truth_exists():
    """Ground Truth 파일 존재 확인"""
    assert GROUND_TRUTH_PATH.exists()


def test_conversions_table_exists():
    """환산점수 테이블 존재 확인"""
    base_path = PROJECT_ROOT / "theory_engine" / "weights" / "subject3_conversions.json"
    assert base_path.exists() or CONVERSIONS_PATH.exists()


@pytest.mark.skipif(
    not GROUND_TRUTH_PATH.exists(),
    reason="Ground Truth 파일 없음"
)
def test_parity_pass_rate(parity_runner, ground_truth_loaded, conversions_loaded):
    """
    Parity Test 통과율 검증

    성공 기준: 90% 이상 통과
    """
    if not ground_truth_loaded or not conversions_loaded:
        pytest.skip("데이터 로드 실패")

    results = parity_runner.run_all_tests()

    if "error" in results:
        pytest.skip(results["error"])

    print(f"\n=== Parity Test 결과 ===")
    print(f"PASSED: {results['passed']}")
    print(f"FAILED: {results['failed']}")
    print(f"SKIPPED: {results['skipped']}")
    print(f"통과율: {results['pass_rate']:.2%}")
    print(f"기준: {PASS_RATE_THRESHOLD:.0%}")

    # 실패 케이스 상세 출력
    if results['failed'] > 0:
        print(f"\n=== 실패 케이스 ===")
        for detail in results['details']:
            if detail.get('status') == 'FAIL':
                print(f"  {detail['university']}/{detail['department']}")
                print(f"    Excel: {detail.get('excel_result')}")
                print(f"    Python: {detail.get('python_result')}")
                metrics = detail.get('metrics', {})
                print(f"    abs_err: {metrics.get('abs_error', 0):.2e}")

    # 90% 이상 통과 확인
    assert results['pass_rate'] >= PASS_RATE_THRESHOLD, \
        f"통과율 {results['pass_rate']:.2%}가 기준 {PASS_RATE_THRESHOLD:.0%} 미달"


def test_strict_parity_function():
    """is_strict_parity 함수 테스트"""
    # 동일한 값
    passed, metrics = is_strict_parity(100.0, 100.0)
    assert passed
    assert metrics['abs_error'] == 0

    # 허용 범위 내 오차
    passed, metrics = is_strict_parity(100.0, 100.0 + 1e-7)
    assert passed

    # 허용 범위 초과
    passed, metrics = is_strict_parity(100.0, 100.1)
    assert not passed

    # None 값
    passed, metrics = is_strict_parity(None, 100.0)
    assert not passed


if __name__ == "__main__":
    """직접 실행 시 테스트 결과 출력"""
    runner = ParityTestRunner()

    if not runner.load_ground_truth():
        print("\nGround Truth 파일이 없습니다.")
        print("먼저 실행: python tools/collect_ground_truth.py")
        sys.exit(1)

    if not runner.load_conversions():
        print("\n환산점수 테이블이 없습니다.")
        sys.exit(1)

    results = runner.run_all_tests()

    print("\n" + "=" * 60)
    print("Standalone Parity Test 결과")
    print("=" * 60)
    print(f"PASSED: {results['passed']}")
    print(f"FAILED: {results['failed']}")
    print(f"SKIPPED: {results['skipped']}")
    print(f"통과율: {results['pass_rate']:.2%}")
    print(f"기준 충족: {'YES' if results['threshold_met'] else 'NO'}")
    print("=" * 60)

    if results['failed'] > 0:
        print("\n실패 케이스:")
        for detail in results['details']:
            if detail.get('status') == 'FAIL':
                print(f"  - {detail['case_name']}: {detail['university']}/{detail['department']}")

    sys.exit(0 if results['threshold_met'] else 1)
