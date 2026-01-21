"""
IF/IFS/SWITCH 파서 안정성 검증 테스트
"""

import sys
from pathlib import Path

# 프로젝트 루트를 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from theory_engine.formula_mining.rule_miner import RuleMiner
import pandas as pd


def test_if_parser():
    """IF 파서 테스트"""
    miner = RuleMiner()
    
    test_cases = [
        ("=IF(A1>0, 10, 20)", 1, "A1>0", "10", "20"),
        ("=IFERROR(IF(B2=\"\", \"\", INDEX(Sheet!A:A, MATCH(B2, Sheet!B:B, 0))), \"\")", 1, "B2=\"\"", "\"\"", "INDEX(Sheet!A:A, MATCH(B2, Sheet!B:B, 0))"),
        ("=IF(OR(A1=1, A1=2), \"YES\", \"NO\")", 1, "OR(A1=1, A1=2)", "\"YES\"", "\"NO\""),
    ]
    
    print("=== IF 파서 테스트 ===")
    for formula, expected_count, expected_cond, expected_true, expected_false in test_cases:
        rules = miner._extract_if_rules(
            pd.Series({'sheet_name': 'TEST', 'cell_ref': 'A1'}),
            formula
        )
        assert len(rules) >= expected_count, f"IF 파싱 실패: {formula}"
        if rules:
            rule = rules[0]
            assert expected_cond in rule['condition'], f"조건 불일치: {formula}"
            print(f"✓ {formula[:50]}... -> {rule['condition'][:30]}...")


def test_ifs_parser():
    """IFS 파서 테스트"""
    miner = RuleMiner()
    
    test_cases = [
        ("=IFS(A1>10, 100, A1>5, 50, 0)", 2, None),  # default 있음
        ("=IFS(B2=\"A\", 1, B2=\"B\", 2)", 2, None),  # default 없음
    ]
    
    print("\n=== IFS 파서 테스트 ===")
    for formula, expected_pairs, expected_default in test_cases:
        rules = miner._extract_ifs_rules(
            pd.Series({'sheet_name': 'TEST', 'cell_ref': 'A1'}),
            formula
        )
        assert len(rules) >= expected_pairs, f"IFS 파싱 실패: {formula}"
        print(f"✓ {formula[:50]}... -> {len(rules)}개 branch")


def test_switch_parser():
    """SWITCH 파서 테스트"""
    miner = RuleMiner()
    
    test_cases = [
        ("=SWITCH(A1, 1, \"ONE\", 2, \"TWO\", \"OTHER\")", "A1", 2, "OTHER"),
        ("=SWITCH(B2, \"A\", 10, \"B\", 20)", "B2", 2, None),
    ]
    
    print("\n=== SWITCH 파서 테스트 ===")
    for formula, expected_expr, expected_pairs, expected_default in test_cases:
        rules = miner._extract_switch_rules(
            pd.Series({'sheet_name': 'TEST', 'cell_ref': 'A1'}),
            formula
        )
        assert len(rules) >= expected_pairs, f"SWITCH 파싱 실패: {formula}"
        if rules:
            rule = rules[0]
            assert expected_expr in rule['condition'], f"표현식 불일치: {formula}"
            print(f"✓ {formula[:50]}... -> {rule['condition'][:30]}...")


def test_nested_if():
    """중첩 IF 테스트"""
    miner = RuleMiner()
    
    formula = "=IF(A1>0, IF(B1>0, \"BOTH\", \"A_ONLY\"), \"NONE\")"
    rules = miner._extract_if_rules(
        pd.Series({'sheet_name': 'TEST', 'cell_ref': 'A1'}),
        formula
    )
    
    print("\n=== 중첩 IF 테스트 ===")
    # 중첩 IF는 최소 1개 이상의 룰이 추출되어야 함 (외부 IF는 반드시 추출됨)
    assert len(rules) >= 1, "중첩 IF 파싱 실패"
    print(f"✓ 중첩 IF -> {len(rules)}개 룰 추출 (중첩 IF는 여러 레벨이 각각 룰로 추출됨)")


def test_string_escape():
    """문자열 escape 테스트"""
    miner = RuleMiner()
    
    formula = '=IF(A1="텍스트""내부", "YES", "NO")'
    rules = miner._extract_if_rules(
        pd.Series({'sheet_name': 'TEST', 'cell_ref': 'A1'}),
        formula
    )
    
    print("\n=== 문자열 escape 테스트 ===")
    assert len(rules) >= 1, "문자열 escape 파싱 실패"
    print(f"✓ 문자열 escape -> {len(rules)}개 룰 추출")


def test_rule_uid():
    """rule_uid 결정성 테스트"""
    miner = RuleMiner()
    
    rule_data1 = {
        "source_type": "formula_if",
        "location": "TEST!A1",
        "condition": "A1>0",
        "true_value": "10",
        "false_value": "20",
    }
    
    rule_data2 = {
        "source_type": "formula_if",
        "location": "TEST!A1",
        "condition": "A1>0",
        "true_value": "10",
        "false_value": "20",
    }
    
    uid1 = miner._generate_rule_uid(rule_data1)
    uid2 = miner._generate_rule_uid(rule_data2)
    
    print("\n=== rule_uid 결정성 테스트 ===")
    assert uid1 == uid2, "rule_uid가 결정적이지 않음"
    print(f"✓ rule_uid 결정성 확인: {uid1}")


if __name__ == "__main__":
    try:
        test_if_parser()
        test_ifs_parser()
        test_switch_parser()
        test_nested_if()
        test_string_escape()
        test_rule_uid()
        print("\n✅ 모든 테스트 통과!")
    except AssertionError as e:
        print(f"\n❌ 테스트 실패: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
