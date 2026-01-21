"""
Excel Parity Test (Legacy) - 엑셀 결과와 Python 결과 100% 일치 검증

SSOT 문서 기준:
- 절대 오차: 1e-6 이하
- 상대 오차: 1e-9 이하 (둘 다 만족해야 함)

Phase 2 주의사항:
- 이 파일은 xlwings를 사용하여 Excel COM 연결이 필요합니다.
- 런타임에 xlwings 없이 테스트하려면 test_excel_parity_standalone.py 사용
- 이 테스트는 Excel 환산점수 값을 직접 읽어서 합산하는 방식입니다.
- Python이 JSON 테이블에서 환산점수를 조회하는 방식은 standalone 테스트 참조.

xlwings 없이 실행:
    pytest tests/test_excel_parity_standalone.py -v
"""

import sys
import os

# 프로젝트 루트를 path에 추가
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import xlwings as xw
from typing import Dict, List, Tuple


def is_strict_parity(expected: float, calculated: float) -> Tuple[bool, Dict]:
    """
    엄격한 Parity 검증: abs + rel 동시 만족 필요

    기준:
    - 절대 오차: 1e-6 이하
    - 상대 오차: 1e-9 이하
    """
    if expected is None or calculated is None:
        return False, {"error": "None value"}

    abs_err = abs(expected - calculated)
    denominator = max(abs(expected), abs(calculated), 1e-15)
    rel_err = abs_err / denominator

    ABS_TOLERANCE = 1e-6
    REL_TOLERANCE = 1e-9

    passed = (abs_err < ABS_TOLERANCE) and (rel_err < REL_TOLERANCE)

    return passed, {
        "abs_error": abs_err,
        "rel_error": rel_err,
        "abs_threshold": ABS_TOLERANCE,
        "rel_threshold": REL_TOLERANCE,
        "passed": passed
    }


def run_parity_test(excel_path: str, test_columns: List[str] = None):
    """
    여러 대학 컬럼에 대해 Parity Test 수행

    Args:
        excel_path: 엑셀 파일 경로
        test_columns: 테스트할 컬럼 목록 (예: ['D', 'E', 'F', 'G'])
    """
    if test_columns is None:
        test_columns = ['D', 'E', 'F', 'G', 'H', 'I', 'J']

    print("=" * 60)
    print("Excel Parity Test")
    print("=" * 60)

    app = xw.App(visible=False)
    app.display_alerts = False
    app.screen_updating = False

    results = {
        "passed": 0,
        "failed": 0,
        "details": []
    }

    try:
        wb = app.books.open(excel_path)
        ws_compute = wb.sheets['COMPUTE']
        ws_input = wb.sheets[2]  # 수능입력

        # 입력값 읽기
        print("\n=== Input Scores ===")
        korean = ws_input.range('C11').value
        math = ws_input.range('C15').value
        english = ws_input.range('C18').value
        inquiry1 = ws_input.range('C29').value
        inquiry2 = ws_input.range('C32').value
        history = ws_input.range('C19').value

        print(f"Korean: {korean}")
        print(f"Math: {math}")
        print(f"English grade: {english}")
        print(f"Inquiry1: {inquiry1}")
        print(f"Inquiry2: {inquiry2}")
        print(f"History grade: {history}")

        print("\n=== Parity Test Results ===")

        for col in test_columns:
            # 대학명/학과명
            univ = ws_compute.range(f'{col}1').value
            dept = ws_compute.range(f'{col}2').value

            # Excel 환산점수
            excel_korean = ws_compute.range(f'{col}46').value
            excel_math = ws_compute.range(f'{col}47').value
            excel_english = ws_compute.range(f'{col}48').value
            excel_inquiry = ws_compute.range(f'{col}51').value
            excel_history = ws_compute.range(f'{col}57').value

            # Excel 최종 점수
            excel_row59 = ws_compute.range(f'{col}59').value
            excel_row3 = ws_compute.range(f'{col}3').value

            # 필수과목 문자열
            required = ws_compute.range(f'{col}65').value

            # Python 계산 (단순 합산으로 검증)
            python_row59 = 0.0
            if required:
                if "국" in str(required) and excel_korean:
                    python_row59 += excel_korean
                if "수" in str(required) and excel_math:
                    python_row59 += excel_math
                if "영" in str(required) and excel_english:
                    python_row59 += excel_english
                if "탐" in str(required) and excel_inquiry:
                    python_row59 += excel_inquiry
                # 한국사는 복잡한 조건이라 일단 제외

            # Parity 검증
            passed, metrics = is_strict_parity(
                excel_row59 if excel_row59 else 0,
                python_row59
            )

            status = "PASS" if passed else "FAIL"
            results["passed" if passed else "failed"] += 1

            print(f"\n{col}: {univ} / {dept}")
            print(f"  Required: {required}")
            print(f"  Korean: {korean} -> {excel_korean}")
            print(f"  Math: {math} -> {excel_math}")
            print(f"  English: {english} -> {excel_english}")
            print(f"  Inquiry: -> {excel_inquiry}")
            print(f"  Excel Row59: {excel_row59}")
            print(f"  Python Row59: {python_row59}")
            print(f"  Excel Row3: {excel_row3}")
            print(f"  [{status}] abs_err={metrics.get('abs_error', 0):.2e}, "
                  f"rel_err={metrics.get('rel_error', 0):.2e}")

            results["details"].append({
                "column": col,
                "university": univ,
                "department": dept,
                "excel_row59": excel_row59,
                "python_row59": python_row59,
                "passed": passed,
                "metrics": metrics
            })

        print("\n" + "=" * 60)
        print(f"TOTAL: {results['passed']} PASSED, {results['failed']} FAILED")
        print("=" * 60)

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

    finally:
        try:
            wb.close()
        except:
            pass
        app.quit()
        print("\nExcel closed.")

    return results


if __name__ == "__main__":
    excel_path = r"C:\Neoprime\202511고속성장분석기(가채점)20251114 (1).xlsx"
    run_parity_test(excel_path, test_columns=['D', 'E', 'F', 'G', 'H', 'I', 'J'])
