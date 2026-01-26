# ============================================================
# Score Calculator v3 - 가중택 대학 변형 컬럼 지원
# NEO GOD Ultra Framework v2.3
# ============================================================
"""
가중택 대학은 .1, .2 등 변형 컬럼에서 값을 가져옴
"""

import pandas as pd
import json
import re
from google.cloud import bigquery
from google.oauth2 import service_account


def load_data():
    """데이터 로드"""
    creds = service_account.Credentials.from_service_account_file('neoprime-loader-key.json')
    client = bigquery.Client(credentials=creds, project='neoprime0305', location='asia-northeast3')

    compute_numeric = client.query('''
        SELECT * FROM `neoprime0305.ds_neoprime_entrance.tb_raw_2026_COMPUTE`
        ORDER BY _row_id
    ''').to_dataframe()

    compute_string = pd.read_parquet('output/COMPUTE_chunk_0000.parquet')

    return compute_numeric, compute_string


def find_best_variant(univ_name, compute_string, compute_numeric):
    """
    대학의 가장 적합한 변형 컬럼 찾기

    1. 먼저 기본 컬럼 확인
    2. 기본 컬럼이 가중택이면 .1, .2 등에서 필수 컬럼 찾기
    3. 값이 있는 컬럼 우선
    """
    # 해당 대학의 모든 컬럼 찾기
    variants = []
    for col in compute_string.columns:
        if col == univ_name or col.startswith(f'{univ_name}.'):
            variants.append(col)

    if not variants:
        return None, None, None

    # 각 변형의 설정 및 값 확인
    best_variant = None
    best_score = -1
    best_config = None
    best_source = None

    for var in variants:
        # Row 63 (필수), 64 (선택), 65 (가중택) 확인
        row63 = compute_string.iloc[63].get(var)
        row64 = compute_string.iloc[64].get(var)
        row65 = compute_string.iloc[65].get(var)

        # 설정 문자열 찾기
        config_str = None
        source = None

        if row63 and isinstance(row63, str) and '국' in row63:
            config_str = row63
            source = '필수'
        elif row64 and isinstance(row64, str) and '국' in row64:
            config_str = row64
            source = '선택'
        elif row65 and isinstance(row65, str) and '국' in row65:
            config_str = row65
            source = '가중택'

        if not config_str:
            continue

        # Row 57 (국어환산) 값 확인
        row57_val = compute_string.iloc[57].get(var)
        has_korean = row57_val is not None and not pd.isna(row57_val) and row57_val != 0

        # 점수 계산: 필수 > 선택 > 가중택, 값 있음 우선
        score = 0
        if source == '필수':
            score += 100
        elif source == '선택':
            score += 50
        else:
            score += 10

        if has_korean:
            score += 1000  # 값이 있으면 최우선

        if score > best_score:
            best_score = score
            best_variant = var
            best_config = config_str
            best_source = source

    return best_variant, best_config, best_source


def get_scores_from_variant(variant_name, compute_string):
    """변형 컬럼에서 점수 추출"""
    if variant_name not in compute_string.columns:
        return None

    scores = {}

    # Row 57-61: 국어, 수학, 영어, 탐구1, 탐구2 환산점수
    row_map = {
        '국어': 57,
        '수학': 58,
        '영어': 59,
        '탐구1': 60,
        '탐구2': 61,
    }

    for name, row_idx in row_map.items():
        val = compute_string.iloc[row_idx].get(variant_name)
        if val is not None and not pd.isna(val):
            try:
                scores[name] = float(val)
            except:
                scores[name] = 0.0
        else:
            scores[name] = 0.0

    return scores


def parse_config(config_str):
    """반영영역 문자열 파싱"""
    if not config_str:
        return None

    config = {
        '국어': '국' in config_str,
        '수학': '수' in config_str,
        '영어': '영' in config_str,
        '탐구': 0,
        '한국사': '한' in config_str,
        '외국어': '외' in config_str,
    }

    # 탐구 과목 수
    match = re.search(r'탐\((\d)\)', config_str)
    if match:
        config['탐구'] = int(match.group(1))
    elif '탐' in config_str:
        config['탐구'] = 1

    return config


def calculate_total(scores, config):
    """총점 계산"""
    total = 0

    if config['국어']:
        total += scores.get('국어', 0)
    if config['수학']:
        total += scores.get('수학', 0)
    if config['영어']:
        total += scores.get('영어', 0)
    if config['탐구'] >= 1:
        total += scores.get('탐구1', 0)
    if config['탐구'] >= 2:
        total += scores.get('탐구2', 0)

    return total


def main():
    print('=' * 80)
    print('NEO GOD v3 - 가중택 대학 변형 컬럼 지원')
    print('=' * 80)

    # 데이터 로드
    print('\n[1] 데이터 로드')
    compute_numeric, compute_string = load_data()

    # 주요 대학
    major_univs = [
        '서울대', '연세대', '고려대', '성균관', '서강대', '한양대',
        '중앙대', '경희대', '이화여', '건국대', '동국대', '홍익대',
        '숙명여', '국민대', '숭실대', '세종대', '아주대', '인하대',
        '서울시립', '한국외대', '포항공', '카이스트'
    ]

    # 결과 저장
    results = []

    print('\n[2] 대학별 점수 계산')
    print('-' * 90)
    print(f"{'대학':<10} {'변형':<12} {'유형':<6} {'국어':>8} {'수학':>8} {'영어':>8} {'탐구1':>8} {'탐구2':>8} {'총점':>10}")
    print('-' * 90)

    for univ in major_univs:
        # 최적 변형 찾기
        variant, config_str, source = find_best_variant(univ, compute_string, compute_numeric)

        if not variant:
            print(f"{univ:<10} {'N/A':<12} {'N/A':<6} {0:>8} {0:>8} {0:>8} {0:>8} {0:>8} {0:>10}")
            continue

        # 점수 추출
        scores = get_scores_from_variant(variant, compute_string)
        config = parse_config(config_str)

        if not scores or not config:
            continue

        # 총점 계산
        total = calculate_total(scores, config)

        # 변형 표시
        variant_display = variant if variant != univ else '-'

        results.append({
            'university': univ,
            'variant': variant,
            'source': source,
            'config': config,
            'config_str': config_str,
            'scores': scores,
            'total': total
        })

        print(f"{univ:<10} {variant_display:<12} {source:<6} "
              f"{scores['국어']:>8.1f} {scores['수학']:>8.1f} {scores['영어']:>8.1f} "
              f"{scores['탐구1']:>8.1f} {scores['탐구2']:>8.1f} {total:>10.1f}")

    # 순위
    print('\n[3] 총점 순위')
    print('-' * 80)

    sorted_results = sorted(results, key=lambda x: x['total'], reverse=True)

    for i, r in enumerate(sorted_results, 1):
        variant_mark = f"({r['variant']})" if r['variant'] != r['university'] else ""
        source_mark = '⭐' if r['source'] == '가중택' else '  '
        print(f"  {i:2}. {source_mark} {r['university']:<10} {variant_mark:<15} ({r['source']:<4}): {r['total']:>10.1f}점")

    # 가중택 대학 상세
    print('\n[4] 가중택→필수 변환 상세')
    print('-' * 80)

    weighted_univs = ['서울대', '성균관', '이화여', '인하대', '서강대']
    for univ in weighted_univs:
        result = next((r for r in results if r['university'] == univ), None)
        if result:
            print(f"\n{univ}:")
            print(f"  - 사용 변형: {result['variant']}")
            print(f"  - 유형: {result['source']}")
            print(f"  - 설정: {result['config_str']}")
            print(f"  - 점수: 국어={result['scores']['국어']:.1f}, 수학={result['scores']['수학']:.1f}, "
                  f"영어={result['scores']['영어']:.1f}, 탐구={result['scores']['탐구1']:.1f}+{result['scores']['탐구2']:.1f}")
            print(f"  - 총점: {result['total']:.1f}")

    return results


if __name__ == '__main__':
    main()
