"""
Golden Case 통합 테스트

실제 사용 케이스 기반으로 전체 파이프라인을 테스트합니다.
"""

import pytest
import logging
from theory_engine.loader import load_workbook
from theory_engine.rules import compute_theory_result
from theory_engine.model import StudentProfile, ExamScore, TargetProgram
from theory_engine.constants import Track, LevelTheory

logger = logging.getLogger(__name__)


# Golden Case 정의
GOLDEN_CASES = [
    {
        "name": "이과_상위권_의대지망_미적분",
        "profile": StudentProfile(
            track=Track.SCIENCE,
            korean=ExamScore("국어(언매)", raw_total=85),
            math=ExamScore("수학(미적)", raw_total=82),  # 미적분 명시
            english_grade=2,
            history_grade=3,
            inquiry1=ExamScore("물리학 Ⅰ", raw_total=47),
            inquiry2=ExamScore("화학 Ⅰ", raw_total=45),
            targets=[
                TargetProgram("연세대", "의학"),  # 의예 → 의학 자동 매핑
                TargetProgram("가천", "의학"),
                TargetProgram("건국", "자연"),
            ]
        ),
        "expected": {
            "연세대의학": {
                "disqualified": False,
                "has_cutoff": True,
                "level_options": ["적정", "예상", "소신"],
            },
            "가천의학": {
                "disqualified": False,
                "has_cutoff": True,
                "level_options": ["적정", "예상"],
            },
            "건국자연": {
                "disqualified": False,
                "has_cutoff": True,
                "level_options": ["적정", "예상"],
            },
        }
    },
    {
        "name": "이과_중위권_기하",
        "profile": StudentProfile(
            track=Track.SCIENCE,
            korean=ExamScore("국어(화작)", raw_total=75),
            math=ExamScore("수학(기하)", raw_total=70),  # 기하 명시
            english_grade=2,
            history_grade=3,
            inquiry1=ExamScore("생명과학 Ⅰ", raw_total=42),
            inquiry2=ExamScore("지구과학 Ⅰ", raw_total=40),
            targets=[
                TargetProgram("한양대", "자연"),
                TargetProgram("경기대", "인문"),
            ]
        ),
        "expected": {
            "한양대자연": {
                "disqualified": False,
                "has_cutoff": True,
            },
            "경기대인문": {
                "disqualified": False,
                "has_cutoff": True,
            },
        }
    },
    {
        "name": "문과_확률과통계",
        "profile": StudentProfile(
            track=Track.LIBERAL,
            korean=ExamScore("국어(언매)", raw_total=80),
            math=ExamScore("수학(확통)", raw_total=78),  # 확통 명시
            english_grade=2,
            history_grade=3,
            inquiry1=ExamScore("생활과 윤리", raw_total=45),
            inquiry2=ExamScore("사회·문화", raw_total=43),
            targets=[
                TargetProgram("이화여대", "인문"),
                TargetProgram("숙명여대", "인문"),
            ]
        ),
        "expected": {
            "이화여대인문": {
                "disqualified": False,
            },
            "숙명여대인문": {
                "disqualified": False,
            },
        }
    },
    {
        "name": "이과_영어4등급_결격",
        "profile": StudentProfile(
            track=Track.SCIENCE,
            korean=ExamScore("국어(언매)", raw_total=90),
            math=ExamScore("수학(미적)", raw_total=88),
            english_grade=4,  # 결격 예상
            history_grade=3,
            inquiry1=ExamScore("물리학 Ⅰ", raw_total=48),
            inquiry2=ExamScore("화학 Ⅰ", raw_total=46),
            targets=[
                TargetProgram("서울대", "공대"),
                TargetProgram("가천", "의학"),
            ]
        ),
        "expected": {
            "서울대공대": {
                "disqualified": True,
                "reason_contains": "영어",
            },
            "가천의학": {
                "disqualified": True,
                "reason_contains": "영어",
            },
        }
    },
    {
        "name": "이과_확통_서울대_결격",
        "profile": StudentProfile(
            track=Track.SCIENCE,
            korean=ExamScore("국어(언매)", raw_total=92),
            math=ExamScore("수학(확통)", raw_total=90),  # 이과인데 확통 → 결격
            english_grade=1,
            history_grade=2,
            inquiry1=ExamScore("물리학 Ⅰ", raw_total=49),
            inquiry2=ExamScore("화학 Ⅰ", raw_total=48),
            targets=[
                TargetProgram("서울대", "공대"),
                TargetProgram("건국대", "자연"),  # 건국은 허용 가능
            ]
        ),
        "expected": {
            "서울대공대": {
                "disqualified": True,
                "reason_contains": "미적분",
            },
            "건국대자연": {
                "disqualified": False,  # 건국은 확통 허용 가능
            },
        }
    },
]


@pytest.fixture(scope="module")
def excel_data():
    """엑셀 데이터 로드 (모듈 단위 캐싱)"""
    return load_workbook()


class TestGoldenCases:
    """Golden Case 통합 테스트"""
    
    @pytest.mark.parametrize("case", GOLDEN_CASES, ids=lambda c: c["name"])
    def test_golden_case_pipeline(self, excel_data, case):
        """전체 파이프라인 Golden Case 테스트"""
        profile = case["profile"]
        expected = case["expected"]
        
        # 전체 파이프라인 실행
        result = compute_theory_result(excel_data, profile)
        
        # 버전 확인
        assert result.engine_version == "3.0.0"
        assert result.excel_version == "202511_가채점_20251114"
        
        # INDEX 폴백 확인
        if result.raw_components.get("index_found") is False:
            # INDEX 조회 실패 시 폴백 사용 확인
            assert result.raw_components.get("index_match_type") == "fallback_rawscore_weighted", \
                "INDEX 실패 시 폴백 로직 미사용"

        # Explainability(설명 가능성) 최소 필드 검증
        for prog in result.program_results:
            assert prog.explainability is not None
            assert prog.explainability.university_mapping is not None
            assert prog.explainability.major_mapping is not None
            assert prog.explainability.university_mapping.method in ("exact", "alias", "fuzzy")
            assert prog.explainability.major_mapping.method in ("exact", "alias", "fuzzy")

            if prog.disqualification.is_disqualified:
                # 결격이면 트리거 정보가 있어야 함
                assert len(prog.explainability.disqualification_details) > 0
            else:
                # 비결격이면 커트라인 소스(조회 근거)가 있어야 함
                assert prog.explainability.cutoff_source is not None
                assert prog.explainability.cutoff_source.sheet in ("PERCENTAGE", "INDEX")
        
        # 대학별 결과 검증
        for prog_result in result.program_results:
            target_key = f"{prog_result.target.university}{prog_result.target.major}"
            
            if target_key not in expected:
                continue
            
            exp = expected[target_key]
            
            # 결격 여부 확인
            if "disqualified" in exp:
                assert prog_result.disqualification.is_disqualified == exp["disqualified"], \
                    f"{target_key}: 결격 여부 불일치 (예상={exp['disqualified']}, 실제={prog_result.disqualification.is_disqualified})"
                
                if exp["disqualified"] and "reason_contains" in exp:
                    reason = prog_result.disqualification.reason or ""
                    assert exp["reason_contains"] in reason, \
                        f"{target_key}: 결격 사유에 '{exp['reason_contains']}' 포함 필요 (실제={reason})"
            
            # 결격이 아닌 경우에만 커트라인 확인
            if not prog_result.disqualification.is_disqualified:
                if exp.get("has_cutoff"):
                    assert prog_result.cutoff_normal is not None, \
                        f"{target_key}: 커트라인(50%) 없음"
                
                if "level_options" in exp:
                    assert prog_result.level_theory.value in exp["level_options"], \
                        f"{target_key}: 레벨 불일치 (예상={exp['level_options']}, 실제={prog_result.level_theory.value})"
    
    def test_case_coverage(self):
        """Golden Case 커버리지 확인"""
        # 최소 5개 케이스
        assert len(GOLDEN_CASES) >= 5, "Golden Case 최소 5개 필요"
        
        # 계열 분포 확인
        science_count = sum(1 for c in GOLDEN_CASES if c["profile"].track == Track.SCIENCE)
        liberal_count = sum(1 for c in GOLDEN_CASES if c["profile"].track == Track.LIBERAL)
        
        assert science_count >= 3, "이과 케이스 최소 3개 필요"
        assert liberal_count >= 1, "문과 케이스 최소 1개 필요"
        
        # 결격 케이스 확인
        disqual_cases = []
        for c in GOLDEN_CASES:
            for target_key, exp in c["expected"].items():
                if exp.get("disqualified"):
                    disqual_cases.append(target_key)
        
        assert len(disqual_cases) >= 2, "결격 케이스 최소 2개 필요"


class TestRealisticProfiles:
    """실제 사용 케이스 기반 파라미터 테스트"""
    
    @pytest.mark.parametrize("math_type,english,expected_disqual", [
        ("수학(미적)", 2, False),  # 정상
        ("수학(기하)", 1, False),  # 정상
        ("수학(확통)", 2, False),  # 문과는 정상 (이과 케이스는 Golden Case에서)
        ("수학(미적)", 4, True),   # 영어 4등급 결격
        ("수학", 1, False),        # 선택과목 미지정 (일부 대학 결격 가능)
    ])
    def test_math_english_combinations(
        self, 
        excel_data, 
        math_type, 
        english, 
        expected_disqual
    ):
        """수학 선택과목 + 영어 등급 조합 테스트"""
        profile = StudentProfile(
            track=Track.SCIENCE,
            korean=ExamScore("국어(언매)", raw_total=80),
            math=ExamScore(math_type, raw_total=75),
            english_grade=english,
            history_grade=3,
            inquiry1=ExamScore("물리학 Ⅰ", raw_total=45),
            inquiry2=ExamScore("화학 Ⅰ", raw_total=43),
            targets=[TargetProgram("가천", "의학")]
        )
        
        result = compute_theory_result(excel_data, profile)
        
        # 최소 1개 결과 존재
        assert len(result.program_results) > 0
        
        # 결격 여부 확인 (영어 4등급은 대부분 대학 결격)
        prog_result = result.program_results[0]
        if expected_disqual:
            assert prog_result.disqualification.is_disqualified, \
                f"{math_type} + 영어{english}등급: 결격 예상했으나 통과"


if __name__ == "__main__":
    # 직접 실행
    logging.basicConfig(level=logging.INFO)
    
    print("=" * 70)
    print("Golden Case 수동 테스트")
    print("=" * 70)
    
    excel_data = load_workbook()
    
    for i, case in enumerate(GOLDEN_CASES, 1):
        print(f"\n[Case {i}] {case['name']}")
        print("-" * 70)
        
        profile = case["profile"]
        result = compute_theory_result(excel_data, profile)
        
        print(f"  계열: {profile.track.value}")
        print(f"  수학: {profile.math.subject}")
        print(f"  영어: {profile.english_grade}등급")
        print(f"  INDEX: {result.raw_components.get('index_match_type')}")
        print(f"  누적%: {result.raw_components.get('cumulative_pct')}")
        
        print(f"\n  대학별 결과:")
        for prog in result.program_results:
            target_key = f"{prog.target.university}{prog.target.major}"
            status = "✅" if prog.cutoff_normal or prog.disqualification.is_disqualified else "❌"
            
            print(f"    {status} {target_key}")
            print(f"       레벨: {prog.level_theory.value}")
            if prog.disqualification.is_disqualified:
                print(f"       결격: {prog.disqualification.reason}")
            else:
                print(f"       커트라인(50%): {prog.cutoff_normal}")
                print(f"       확률: {prog.p_theory:.2%}" if prog.p_theory else "       확률: N/A")
        
        # 검증
        expected = case["expected"]
        passed = 0
        total = len(expected)
        
        for prog in result.program_results:
            target_key = f"{prog.target.university}{prog.target.major}"
            if target_key in expected:
                exp = expected[target_key]
                
                # 결격 확인
                if exp.get("disqualified") is not None:
                    if prog.disqualification.is_disqualified == exp["disqualified"]:
                        passed += 1
                
                # 커트라인 확인
                elif exp.get("has_cutoff"):
                    if prog.cutoff_normal is not None:
                        passed += 1
        
        print(f"\n  검증: {passed}/{total} 통과")
    
    print("\n" + "=" * 70)
    print(f"전체 {len(GOLDEN_CASES)}개 케이스 수동 실행 완료")
