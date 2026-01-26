# ============================================================
# Score Calculator v6 - 가중택 대학 총점 Row 사용
# NEO GOD Ultra Framework v2.3
# ============================================================
"""
갭 11 수정: 가중택 대학은 Row 59 (가중택총점) 사용
- 필수 대학: 개별과목 합산 (Row 9, 13, 16)
- 가중택 대학: Row 59 (가중택총점) 또는 Row 57+59 합산
"""

import pandas as pd
import re
from google.cloud import bigquery
from google.oauth2 import service_account


UNIV_NAME_MAP = {
    '서울시립': '시립대',
    '한국외대': '외국어',
    '카이스트': '과기원',
}

ROW_MAP = {
    '국어': 9, '수학': 13, '영어': 16,
    '필수총점': 57, '선택총점': 58, '가중택총점': 59,
    '필수설정': 63, '선택설정': 64, '가중택설정': 65,
}


def load_data():
    compute_string = pd.read_parquet('output/COMPUTE_chunk_0000.parquet')
    return compute_string


def get_actual_column_name(search_name, df):
    if search_name in UNIV_NAME_MAP:
        actual = UNIV_NAME_MAP[search_name]
        if actual in df.columns:
            return actual
    if search_name in df.columns:
        return search_name
    for col in df.columns:
        if col.startswith(search_name):
            return col
    return None


def find_best_variant(base_name, df):
    """
    변형 선택 (v6.1: 설정 완전성 고려)

    우선순위:
    1. 값이 있는 변형 (필수총점 또는 가중택총점 > 0)
    2. 설정 완전성 (국수영탐 > 국수영 > 국영 > 영)
    3. 필수 > 선택 > 가중택
    """
    variants = [c for c in df.columns if c == base_name or c.startswith(f'{base_name}.')]
    if not variants:
        return None, None, None

    best = {'var': None, 'score': -1, 'config': None, 'source': None}

    for var in variants:
        r63 = df.iloc[ROW_MAP['필수설정']].get(var)
        r64 = df.iloc[ROW_MAP['선택설정']].get(var)
        r65 = df.iloc[ROW_MAP['가중택설정']].get(var)

        config_str, source = None, None
        if r63 and isinstance(r63, str) and ('국' in r63 or '영' in r63):
            config_str, source = r63, '필수'
        elif r64 and isinstance(r64, str) and ('국' in r64 or '영' in r64):
            config_str, source = r64, '선택'
        elif r65 and isinstance(r65, str) and ('국' in r65 or '영' in r65):
            config_str, source = r65, '가중택'

        if not config_str:
            continue

        # 설정 완전성 점수 (갭 13, 14 수정)
        completeness = 0
        if '국' in config_str:
            completeness += 100
        if '수' in config_str:
            completeness += 100
        if '영' in config_str:
            completeness += 50
        if '탐' in config_str:
            completeness += 50

        # 값 유무 확인
        has_value = False
        value_amount = 0
        if source == '가중택':
            val = df.iloc[ROW_MAP['가중택총점']].get(var)
            if val is not None and not pd.isna(val) and val != 0:
                has_value = True
                value_amount = float(val)
        else:
            val = df.iloc[ROW_MAP['필수총점']].get(var)
            if val is not None and not pd.isna(val) and val != 0:
                has_value = True
                value_amount = float(val)

        # 점수 계산: 값 > 완전성 > 유형
        score = 0
        if has_value:
            score += 10000 + value_amount  # 값이 클수록 우선
        score += completeness  # 설정 완전성
        score += {'필수': 10, '선택': 5, '가중택': 1}.get(source, 0)

        if score > best['score']:
            best = {'var': var, 'score': score, 'config': config_str, 'source': source}

    return best['var'], best['config'], best['source']


def safe_float(val):
    if val is None or pd.isna(val):
        return 0.0
    try:
        return float(val)
    except:
        return 0.0


def get_scores(variant, df, source):
    """
    점수 추출 (v6: 유형별 다른 로직)

    - 필수 대학: 개별과목 Row 사용
    - 가중택 대학: Row 59 (가중택총점) 사용
    - 혼합 대학 (서강대): Row 57 + Row 59 합산
    """
    scores = {
        '국어': safe_float(df.iloc[ROW_MAP['국어']].get(variant)),
        '수학': safe_float(df.iloc[ROW_MAP['수학']].get(variant)),
        '영어': safe_float(df.iloc[ROW_MAP['영어']].get(variant)),
        '탐구1': 0.0,
        '탐구2': 0.0,
        '필수총점': safe_float(df.iloc[ROW_MAP['필수총점']].get(variant)),
        '가중택총점': safe_float(df.iloc[ROW_MAP['가중택총점']].get(variant)),
    }

    # 탐구 점수 (Row 18-34 중 상위 2개)
    tamgu_rows = list(range(18, 35))
    tamgu_vals = [(i, safe_float(df.iloc[i].get(variant))) for i in tamgu_rows]
    tamgu_vals = [(i, v) for i, v in tamgu_vals if v != 0]
    tamgu_vals.sort(key=lambda x: x[1], reverse=True)
    if len(tamgu_vals) >= 1:
        scores['탐구1'] = tamgu_vals[0][1]
    if len(tamgu_vals) >= 2:
        scores['탐구2'] = tamgu_vals[1][1]

    return scores


def parse_config(config_str):
    if not config_str:
        return None
    config = {
        '국어': '국' in config_str,
        '수학': '수' in config_str,
        '영어': '영' in config_str,
        '탐구': 0,
    }
    match = re.search(r'탐\((\d)\)', config_str)
    if match:
        config['탐구'] = int(match.group(1))
    elif '탐' in config_str:
        config['탐구'] = 1
    return config


def calculate_total(scores, config, source, config_str):
    """
    총점 계산 (v6: 유형별 다른 로직)

    - 필수: 개별과목 합산
    - 가중택: Row 59 (가중택총점) 직접 사용
    - 혼합 (필수+가중택 둘 다): Row 57 + Row 59
    """
    # 가중택 대학: 가중택총점 사용
    if source == '가중택':
        # 가중택총점이 있으면 사용
        if scores['가중택총점'] > 0:
            return scores['가중택총점']

    # 혼합 대학 체크 (필수설정 + 가중택설정 둘 다 있는 경우)
    # 예: 서강대 - 필수=영탐(2), 가중택=국수(2)
    if scores['필수총점'] > 0 and scores['가중택총점'] > 0:
        return scores['필수총점'] + scores['가중택총점']

    # 필수 대학: 개별과목 합산
    total = 0
    if config['국어']:
        total += scores['국어']
    if config['수학']:
        total += scores['수학']
    if config['영어']:
        total += scores['영어']
    if config['탐구'] >= 1:
        total += scores['탐구1']
    if config['탐구'] >= 2:
        total += scores['탐구2']

    # 개별과목 합이 0이고 필수총점이 있으면 필수총점 사용
    if total == 0 and scores['필수총점'] > 0:
        return scores['필수총점']

    return total


def main():
    print('=' * 110)
    print('NEO GOD v6 - 가중택 대학 총점 Row 사용')
    print('=' * 110)

    df = load_data()

    univs = [
        '서울대', '연세대', '고려대', '성균관', '서강대', '한양대',
        '중앙대', '경희대', '이화여', '건국대', '동국대', '홍익대',
        '숙명여', '국민대', '숭실대', '세종대', '아주대', '인하대',
        '서울시립', '한국외대', '카이스트',
    ]

    results = []

    print('\n[1] 대학별 점수 (v6: 가중택=Row59 사용)')
    print('-' * 120)
    print(f"{'대학':<10} {'컬럼':<8} {'변형':<6} {'유형':<6} {'국어':>7} {'수학':>7} {'영어':>7} {'탐1':>6} {'탐2':>6} {'필수합':>8} {'가중합':>8} {'최종':>10}")
    print('-' * 120)

    for name in univs:
        actual = get_actual_column_name(name, df)
        if not actual:
            print(f"{name:<10} {'N/A':<8}")
            continue

        variant, config_str, source = find_best_variant(actual, df)
        if not variant:
            print(f"{name:<10} {actual:<8} {'N/A':<6}")
            continue

        scores = get_scores(variant, df, source)
        config = parse_config(config_str)
        total = calculate_total(scores, config, source, config_str)

        var_disp = variant.replace(actual, '') if variant != actual else '-'
        act_disp = actual if actual != name else '-'

        results.append({
            'name': name, 'actual': actual, 'variant': variant,
            'source': source, 'config_str': config_str,
            'scores': scores, 'total': total
        })

        print(f"{name:<10} {act_disp:<8} {var_disp:<6} {source:<6} "
              f"{scores['국어']:>7.1f} {scores['수학']:>7.1f} {scores['영어']:>7.1f} "
              f"{scores['탐구1']:>6.1f} {scores['탐구2']:>6.1f} "
              f"{scores['필수총점']:>8.1f} {scores['가중택총점']:>8.1f} {total:>10.1f}")

    # 순위
    print('\n[2] 총점 순위')
    print('-' * 80)
    sorted_r = sorted(results, key=lambda x: x['total'], reverse=True)
    for i, r in enumerate(sorted_r, 1):
        m1 = '🔗' if r['actual'] != r['name'] else '  '
        m2 = '⭐' if r['source'] == '가중택' else '  '
        v = f"(.{r['variant'].split('.')[-1]})" if '.' in r['variant'] else ""
        print(f"  {i:2}. {m1}{m2} {r['name']:<10} {v:<6} ({r['source']:<4}): {r['total']:>10.1f}점")

    # v5 vs v6 비교
    print('\n[3] 갭 11 수정 결과: 가중택 대학')
    print('-' * 80)
    for r in results:
        if r['source'] == '가중택':
            indiv = r['scores']['국어'] + r['scores']['수학'] + r['scores']['영어']
            print(f"  {r['name']}:")
            print(f"    개별합: {indiv:.1f}")
            print(f"    가중택총점(R59): {r['scores']['가중택총점']:.1f}")
            print(f"    v6 최종: {r['total']:.1f} ← Row 59 사용")

    # 혼합 대학 (필수+가중택)
    print('\n[4] 혼합 대학 (필수총점 + 가중택총점)')
    print('-' * 80)
    for r in results:
        if r['scores']['필수총점'] > 0 and r['scores']['가중택총점'] > 0:
            print(f"  {r['name']}: 필수({r['scores']['필수총점']:.1f}) + 가중택({r['scores']['가중택총점']:.1f}) = {r['total']:.1f}")

    return results


if __name__ == '__main__':
    main()
