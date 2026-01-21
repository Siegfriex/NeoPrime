"""P0 수정 검증 스크립트"""

import logging
logging.basicConfig(level=logging.WARNING)

from theory_engine.loader import load_workbook
from theory_engine.rules import convert_raw_to_standard, compute_theory_result
from theory_engine.cutoff import CutoffExtractor
from theory_engine.optimizers import get_index_fallback
from theory_engine.model import StudentProfile, ExamScore, TargetProgram
from theory_engine.constants import Track

print("=" * 70)
print("P0 수정 검증 보고서")
print("=" * 70)

# 엑셀 로드
excel_data = load_workbook()
print(f"\n로드된 시트: {list(excel_data.keys())}")

# ============================================================
# 검증 1: RAWSCORE 탐구과목
# ============================================================
print("\n" + "=" * 70)
print("[검증 1] RAWSCORE 탐구과목 변환")
print("=" * 70)

test_cases = [
    ("국어", 80),
    ("수학", 75),
    ("물리학 Ⅰ", 45),
    ("화학 Ⅰ", 42),
    ("생명과학 Ⅰ", 40),
    ("지구과학 Ⅰ", 38),
    ("생활과 윤리", 35),
]

rawscore_success = 0
rawscore_results = []

for subject, score in test_cases:
    result = convert_raw_to_standard(excel_data["RAWSCORE"], subject, score)
    status = "OK" if result["found"] else "FAIL"
    if result["found"]:
        rawscore_success += 1
    
    std_score = result.get("standard_score", "N/A")
    match_type = result.get("match_type", "N/A")
    print(f"  [{status}] {subject} {score}점 → 표준={std_score}, 타입={match_type}")
    rawscore_results.append((subject, result["found"], match_type))

print(f"\n  >> 성공률: {rawscore_success}/{len(test_cases)} ({rawscore_success/len(test_cases)*100:.0f}%)")

# ============================================================
# 검증 2: INDEX 폴백
# ============================================================
print("\n" + "=" * 70)
print("[검증 2] INDEX 폴백 로직")
print("=" * 70)

# 개별 과목 변환
korean_conv = convert_raw_to_standard(excel_data["RAWSCORE"], "국어", 85)
math_conv = convert_raw_to_standard(excel_data["RAWSCORE"], "수학", 82)
inq1_conv = convert_raw_to_standard(excel_data["RAWSCORE"], "물리학 Ⅰ", 47)
inq2_conv = convert_raw_to_standard(excel_data["RAWSCORE"], "화학 Ⅰ", 45)

print(f"  국어 변환: found={korean_conv['found']}, 누적%={korean_conv.get('cumulative_pct')}")
print(f"  수학 변환: found={math_conv['found']}, 누적%={math_conv.get('cumulative_pct')}")
print(f"  탐구1 변환: found={inq1_conv['found']}, 누적%={inq1_conv.get('cumulative_pct')}")
print(f"  탐구2 변환: found={inq2_conv['found']}, 누적%={inq2_conv.get('cumulative_pct')}")

# 폴백 계산
fallback = get_index_fallback()
fallback_result = fallback.calculate_from_rawscore(
    korean_conv, math_conv, inq1_conv, inq2_conv,
    english_grade=2
)

print(f"\n  폴백 결과:")
print(f"    found: {fallback_result['found']}")
print(f"    match_type: {fallback_result['match_type']}")
print(f"    cumulative_pct: {fallback_result['cumulative_pct']}")
print(f"    national_rank: {fallback_result['national_rank']}")
print(f"    subjects_used: {fallback_result['subjects_used']}")
print(f"    confidence: {fallback_result['confidence']}")

index_fallback_ok = fallback_result["found"] and fallback_result["cumulative_pct"] is not None

# ============================================================
# 검증 3: 대학 커트라인 Alias
# ============================================================
print("\n" + "=" * 70)
print("[검증 3] 대학 커트라인 Alias")
print("=" * 70)

cutoff_extractor = CutoffExtractor(excel_data["PERCENTAGE"])

# 에이전트 주장 테스트 케이스
cutoff_cases = [
    ("연세대", "의예", "이과"),
    ("고려대", "의예", "이과"),
    ("가천", "의학", "이과"),
    ("건국", "자연", "이과"),
]

cutoff_success = 0
for univ, major, track in cutoff_cases:
    result = cutoff_extractor.extract_cutoffs(univ, major, track)
    status = "OK" if result["found"] else "FAIL"
    if result["found"]:
        cutoff_success += 1
    
    column = result.get("column", "N/A")
    cutoff_50 = result.get("cutoff_normal", "N/A")
    print(f"  [{status}] {univ}{major} → 컬럼={column}, 커트라인(50%)={cutoff_50}")

print(f"\n  >> 성공률: {cutoff_success}/{len(cutoff_cases)} ({cutoff_success/len(cutoff_cases)*100:.0f}%)")

# ============================================================
# 검증 4: 전체 파이프라인
# ============================================================
print("\n" + "=" * 70)
print("[검증 4] 전체 파이프라인 (compute_theory_result)")
print("=" * 70)

profile = StudentProfile(
    track=Track.SCIENCE,
    korean=ExamScore("국어", raw_total=85),
    math=ExamScore("수학", raw_total=82),
    english_grade=2,
    history_grade=3,
    inquiry1=ExamScore("물리학 Ⅰ", raw_total=47),
    inquiry2=ExamScore("화학 Ⅰ", raw_total=45),
    targets=[
        TargetProgram("연세대", "의예"),
        TargetProgram("고려대", "의예"),
        TargetProgram("가천", "의학"),
    ]
)

result = compute_theory_result(excel_data, profile)

print(f"  엔진 버전: {result.engine_version}")
print(f"  INDEX 매칭: {result.raw_components.get('index_match_type')}")
print(f"  누적%: {result.raw_components.get('cumulative_pct')}")
print(f"  전국등수: {result.raw_components.get('national_rank')}")

print(f"\n  대학별 결과:")
pipeline_success = 0
for prog in result.program_results:
    has_cutoff = prog.cutoff_normal is not None
    status = "OK" if has_cutoff else "FAIL"
    if has_cutoff:
        pipeline_success += 1
    print(f"    [{status}] {prog.target.university}{prog.target.major}: "
          f"레벨={prog.level_theory.value}, "
          f"커트라인(50%)={prog.cutoff_normal}")

print(f"\n  >> 성공률: {pipeline_success}/{len(result.program_results)} ({pipeline_success/len(result.program_results)*100:.0f}%)")

# ============================================================
# 최종 요약
# ============================================================
print("\n" + "=" * 70)
print("최종 검증 요약")
print("=" * 70)

print(f"""
┌───────────────────────┬────────────────────┬───────────┐
│         항목          │      결과          │   상태    │
├───────────────────────┼────────────────────┼───────────┤
│ RAWSCORE 탐구과목     │ {rawscore_success}/{len(test_cases)} ({rawscore_success/len(test_cases)*100:.0f}%)              │ {"✅ OK" if rawscore_success == len(test_cases) else "⚠️ 일부실패"} │
├───────────────────────┼────────────────────┼───────────┤
│ INDEX 폴백            │ found={str(fallback_result['found']):<14} │ {"✅ OK" if index_fallback_ok else "❌ FAIL"} │
├───────────────────────┼────────────────────┼───────────┤
│ 대학 커트라인 Alias   │ {cutoff_success}/{len(cutoff_cases)} ({cutoff_success/len(cutoff_cases)*100:.0f}%)              │ {"✅ OK" if cutoff_success == len(cutoff_cases) else "⚠️ 일부실패"} │
├───────────────────────┼────────────────────┼───────────┤
│ 전체 파이프라인       │ {pipeline_success}/{len(result.program_results)} ({pipeline_success/len(result.program_results)*100:.0f}%)              │ {"✅ OK" if pipeline_success == len(result.program_results) else "⚠️ 일부실패"} │
└───────────────────────┴────────────────────┴───────────┘
""")

# 전체 성공 여부
all_success = (
    rawscore_success == len(test_cases) and
    index_fallback_ok and
    cutoff_success == len(cutoff_cases) and
    pipeline_success == len(result.program_results)
)

if all_success:
    print("🎉 에이전트 주장 검증 완료: 모든 테스트 통과!")
else:
    print("⚠️ 일부 검증 실패 - 상세 확인 필요")

print("\n" + "=" * 70)
