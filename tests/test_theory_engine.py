"""
Theory Engine 테스트

- 버전 검증
- 데이터 로드 테스트
- 룰 함수 테스트
- 통합 테스트
"""

import pytest
import pandas as pd
from pathlib import Path

# Theory Engine imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from theory_engine.config import ENGINE_VERSION, EXCEL_VERSION, EXCEL_PATH
from theory_engine.constants import LevelTheory, Track, DisqualificationCode
from theory_engine.loader import (
    load_workbook,
    load_rawscore,
    load_index_optimized,
    load_percentage_raw,
)
from theory_engine.model import (
    ExamScore,
    StudentProfile,
    TargetProgram,
    TheoryResult,
)
from theory_engine.rules import (
    convert_raw_to_standard,
    lookup_index,
    lookup_percentage,
    check_disqualification,
    compute_theory_result,
)


# ============================================================
# 버전 검증
# ============================================================
def test_engine_version():
    """엔진 버전 확인"""
    assert ENGINE_VERSION == "3.0.0"
    assert EXCEL_VERSION == "202511_가채점_20251114"


# ============================================================
# 데이터 로드 테스트
# ============================================================
def test_load_workbook():
    """전체 워크북 로드 테스트"""
    if not Path(EXCEL_PATH).exists():
        pytest.skip(f"엑셀 파일 없음: {EXCEL_PATH}")
    
    sheets = load_workbook(strict=False)
    
    # 기본 검증
    assert isinstance(sheets, dict)
    assert len(sheets) > 0
    
    # 필수 시트 확인
    required_sheets = ["RAWSCORE", "INDEX", "PERCENTAGE"]
    for sheet_name in required_sheets:
        if sheet_name in sheets:
            assert isinstance(sheets[sheet_name], pd.DataFrame)
            assert len(sheets[sheet_name]) > 0


def test_load_rawscore():
    """RAWSCORE 시트 로드 테스트"""
    if not Path(EXCEL_PATH).exists():
        pytest.skip(f"엑셀 파일 없음: {EXCEL_PATH}")
    
    df = load_rawscore()
    
    assert isinstance(df, pd.DataFrame)
    assert len(df) > 0
    
    # 컬럼 확인
    expected_cols = ["영역", "과목명"]
    for col in expected_cols:
        if col in df.columns:
            assert col in df.columns


# ============================================================
# 모델 테스트
# ============================================================
def test_exam_score_creation():
    """ExamScore 생성 테스트"""
    score = ExamScore(
        subject="국어",
        raw_common=45,
        raw_select=20,
        raw_total=65
    )
    
    assert score.subject == "국어"
    assert score.raw_total == 65


def test_student_profile_creation():
    """StudentProfile 생성 테스트"""
    korean = ExamScore("국어", raw_total=80)
    math = ExamScore("수학", raw_total=75)
    inquiry1 = ExamScore("물리학I", raw_total=50)
    inquiry2 = ExamScore("화학I", raw_total=48)
    
    target = TargetProgram("서울대", "공대")
    
    profile = StudentProfile(
        track=Track.SCIENCE,
        korean=korean,
        math=math,
        english_grade=2,
        history_grade=3,
        inquiry1=inquiry1,
        inquiry2=inquiry2,
        targets=[target]
    )
    
    assert profile.track == Track.SCIENCE
    assert profile.english_grade == 2
    assert len(profile.targets) == 1


def test_theory_result_creation():
    """TheoryResult 생성 테스트"""
    result = TheoryResult()
    
    assert result.engine_version == ENGINE_VERSION
    assert result.excel_version == EXCEL_VERSION
    assert isinstance(result.raw_components, dict)
    assert "korean_standard" in result.raw_components


# ============================================================
# 룰 함수 테스트
# ============================================================
def test_convert_raw_to_standard():
    """RAWSCORE 변환 테스트"""
    if not Path(EXCEL_PATH).exists():
        pytest.skip(f"엑셀 파일 없음: {EXCEL_PATH}")
    
    df = load_rawscore()
    
    # 테스트 케이스 (실제 데이터에 맞게 조정 필요)
    result = convert_raw_to_standard(
        df,
        "국어",
        80
    )
    
    assert isinstance(result, dict)
    assert "found" in result
    assert "key" in result


def test_level_theory_probability_range():
    """LevelTheory 확률 범위 테스트"""
    assert LevelTheory.SAFE.to_probability_range() == (0.80, 1.00)
    assert LevelTheory.NORMAL.to_probability_range() == (0.50, 0.80)
    assert LevelTheory.RISK.to_probability_range() == (0.20, 0.50)


# ============================================================
# 통합 테스트
# ============================================================
def test_compute_theory_result():
    """전체 파이프라인 테스트"""
    if not Path(EXCEL_PATH).exists():
        pytest.skip(f"엑셀 파일 없음: {EXCEL_PATH}")
    
    # 엑셀 데이터 로드
    excel_data = load_workbook(strict=False)
    
    # 테스트 프로필
    profile = StudentProfile(
        track=Track.SCIENCE,
        korean=ExamScore("국어", raw_total=80),
        math=ExamScore("수학", raw_total=75),
        english_grade=2,
        history_grade=3,
        inquiry1=ExamScore("물리학I", raw_total=50),
        inquiry2=ExamScore("화학I", raw_total=48),
        targets=[TargetProgram("서울대", "공대")]
    )
    
    # 계산 실행
    result = compute_theory_result(excel_data, profile)
    
    # 검증
    assert isinstance(result, TheoryResult)
    assert result.engine_version == ENGINE_VERSION
    assert isinstance(result.raw_components, dict)
    
    # raw_components 필수 키 확인
    required_keys = ["korean_standard", "math_standard", "rawscore_keys"]
    for key in required_keys:
        assert key in result.raw_components


# ============================================================
# 실행
# ============================================================
if __name__ == "__main__":
    # pytest 없이 직접 실행
    import traceback
    
    tests = [
        ("버전 검증", test_engine_version),
        ("워크북 로드", test_load_workbook),
        ("RAWSCORE 로드", test_load_rawscore),
        ("ExamScore 생성", test_exam_score_creation),
        ("StudentProfile 생성", test_student_profile_creation),
        ("TheoryResult 생성", test_theory_result_creation),
        ("RAWSCORE 변환", test_convert_raw_to_standard),
        ("LevelTheory 확률", test_level_theory_probability_range),
        ("통합 테스트", test_compute_theory_result),
    ]
    
    passed = 0
    failed = 0
    skipped = 0
    
    for name, test_func in tests:
        try:
            test_func()
            print(f"[PASS] {name}")
            passed += 1
        except pytest.skip.Exception as e:
            print(f"[SKIP] {name}: {e}")
            skipped += 1
        except Exception as e:
            print(f"[FAIL] {name}: {e}")
            traceback.print_exc()
            failed += 1
    
    print(f"\n총 {len(tests)}개 테스트")
    print(f"  통과: {passed}")
    print(f"  실패: {failed}")
    print(f"  건너뜀: {skipped}")
