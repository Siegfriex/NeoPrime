"""커트라인 불일치 분석"""
import logging
logging.basicConfig(level=logging.WARNING)

from theory_engine.loader import load_workbook
from theory_engine.cutoff import CutoffExtractor
from theory_engine.rules import lookup_percentage, check_disqualification
from theory_engine.model import StudentProfile, ExamScore, TargetProgram
from theory_engine.constants import Track

excel_data = load_workbook()
extractor = CutoffExtractor(excel_data["PERCENTAGE"])

print("="*70)
print("불일치 분석: 개별 테스트 vs 전체 파이프라인")
print("="*70)

# 개별 테스트 (에이전트가 테스트한 방식)
print("\n[1] 개별 extract_cutoffs 호출 (에이전트 테스트 방식)")
cases = [
    ("연세대", "의예", "이과"),
    ("고려대", "의예", "이과"),
    ("가천", "의학", "이과"),
]

for univ, major, track in cases:
    result = extractor.extract_cutoffs(univ, major, track)
    found = result["found"]
    column = result.get("column", "N/A")
    cutoff = result.get("cutoff_normal", "N/A")
    print(f"  {univ}{major}: found={found}, column={column}, cutoff_50%={cutoff}")

# 전체 파이프라인에서 사용하는 방식 (rules.py lookup_percentage)
print("\n[2] 전체 파이프라인 lookup_percentage 호출")
for univ, major, track in cases:
    result = lookup_percentage(excel_data["PERCENTAGE"], univ, major, 50.0, track)
    found = result["found"]
    column = result.get("column", "N/A")
    cutoff = result.get("cutoff_normal", "N/A")
    print(f"  {univ}{major}: found={found}, column={column}, cutoff_50%={cutoff}")

# 결격 체크 확인
print("\n[3] 결격 체크 (DisqualificationEngine)")
profile = StudentProfile(
    track=Track.SCIENCE,
    korean=ExamScore("국어", raw_total=85),
    math=ExamScore("수학", raw_total=82),
    english_grade=2,
    history_grade=3,
    inquiry1=ExamScore("물리학 Ⅰ", raw_total=47),
    inquiry2=ExamScore("화학 Ⅰ", raw_total=45),
    targets=[]
)

import pandas as pd
restrict_df = excel_data.get("RESTRICT", pd.DataFrame())

for univ, major, track in cases:
    target = TargetProgram(univ, major)
    disqual = check_disqualification(restrict_df, profile, target)
    print(f"  {univ}{major}: is_disqualified={disqual.is_disqualified}, reason={disqual.reason}")

# 근본 원인 분석
print("\n[4] 근본 원인 분석")
print("="*70)

# extractor 캐시 확인
print(f"\nCutoffExtractor 캐시: {len(extractor._cache)}개")
for key, val in list(extractor._cache.items())[:5]:
    print(f"  {key}: found={val['found']}, column={val.get('column')}")

# PERCENTAGE 컬럼 검색
print("\n연세대 관련 컬럼 검색:")
for col in excel_data["PERCENTAGE"].columns:
    if "연" in str(col):
        print(f"  - {col}")

print("\n고려대 관련 컬럼 검색:")
for col in excel_data["PERCENTAGE"].columns:
    if "고" in str(col):
        print(f"  - {col}")[:10]
