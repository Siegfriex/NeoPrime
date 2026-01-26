# ============================================================
# Score Calculator v2 - 가중택 대학 지원
# NEO GOD Ultra Framework v2.3
# ============================================================
"""
필수 + 가중택 대학 모두 계산 지원
- Row 63: 필수 영역 (국수영탐(2) 등)
- Row 65: 가중택 영역 (국수영탐(2)中가중택4 등)
"""

import pandas as pd
import json
import re
from google.cloud import bigquery
from google.oauth2 import service_account


def load_data():
    """BigQuery에서 COMPUTE 데이터 로드 + 원본 Parquet에서 문자열 데이터 로드"""

    # BigQuery 연결
    creds = service_account.Credentials.from_service_account_file('neoprime-loader-key.json')
    client = bigquery.Client(credentials=creds, project='neoprime0305', location='asia-northeast3')

    # 숫자 데이터 (BigQuery)
    compute_numeric = client.query('''
        SELECT * FROM `neoprime0305.ds_neoprime_entrance.tb_raw_2026_COMPUTE`
        ORDER BY _row_id
    ''').to_dataframe()

    # 문자열 데이터 (원본 Parquet)
    compute_string = pd.read_parquet('output/COMPUTE_chunk_0000.parquet')

    return compute_numeric, compute_string


def get_subject_config(row63_val, row64_val, row65_val):
    """
    반영영역 문자열에서 과목 설정 추출

    예: "국수영탐(2)" → {'국어': True, '수학': True, '영어': True, '탐구': 2}
    예: "국수영탐(2)中가중택4" → {'국어': True, '수학': True, '영어': True, '탐구': 2, '가중택': 4}
    """
    # 우선순위: Row 63 (필수) > Row 64 (선택) > Row 65 (가중택)
    val = None
    source = None

    if row63_val and isinstance(row63_val, str) and '국' in row63_val:
        val = row63_val
        source = '필수'
    elif row64_val and isinstance(row64_val, str) and '국' in row64_val:
        val = row64_val
        source = '선택'
    elif row65_val and isinstance(row65_val, str) and '국' in row65_val:
        val = row65_val
        source = '가중택'

    if not val:
        return None, None

    config = {
        '국어': '국' in val,
        '수학': '수' in val,
        '영어': '영' in val,
        '탐구': 0,
        '한국사': '한' in val,
        '외국어': '외' in val,
        '가중택': 0
    }

    # 탐구 과목 수 추출: 탐(2), 탐(1)
    match = re.search(r'탐\((\d)\)', val)
    if match:
        config['탐구'] = int(match.group(1))
    elif '탐' in val:
        config['탐구'] = 1  # 기본 1과목

    # 가중택 수 추출
    match = re.search(r'가중택(\d)', val)
    if match:
        config['가중택'] = int(match.group(1))

    return config, source


def calculate_university_score(univ_name, col_idx, compute_numeric, compute_string, col_name_in_string):
    """
    대학별 환산점수 계산

    BigQuery Row 매핑:
    - Row 57 (BQ) = 국어환산
    - Row 58 (BQ) = 수학환산
    - Row 59 (BQ) = 영어환산
    - Row 60 (BQ) = 탐구1환산
    - Row 61 (BQ) = 탐구2환산
    """
    result = {
        'university': univ_name,
        'column': col_idx,
        'source': None,
        'config': None,
        'scores': {},
        'total': 0,
        'status': 'unknown'
    }

    # 컬럼명
    bq_col = f'column_{col_idx}'

    if bq_col not in compute_numeric.columns:
        result['status'] = 'column_not_found'
        return result

    # 반영영역 설정 가져오기 (Row 63, 64, 65)
    row63_val = compute_string.iloc[63].get(col_name_in_string) if col_name_in_string in compute_string.columns else None
    row64_val = compute_string.iloc[64].get(col_name_in_string) if col_name_in_string in compute_string.columns else None
    row65_val = compute_string.iloc[65].get(col_name_in_string) if col_name_in_string in compute_string.columns else None

    config, source = get_subject_config(row63_val, row64_val, row65_val)

    if not config:
        result['status'] = 'no_config'
        return result

    result['config'] = config
    result['source'] = source

    # 점수 추출 (BigQuery Row 기준)
    scores = {
        '국어': float(compute_numeric.iloc[57][bq_col]) if not pd.isna(compute_numeric.iloc[57][bq_col]) else 0,
        '수학': float(compute_numeric.iloc[58][bq_col]) if not pd.isna(compute_numeric.iloc[58][bq_col]) else 0,
        '영어': float(compute_numeric.iloc[59][bq_col]) if not pd.isna(compute_numeric.iloc[59][bq_col]) else 0,
        '탐구1': float(compute_numeric.iloc[60][bq_col]) if not pd.isna(compute_numeric.iloc[60][bq_col]) else 0,
        '탐구2': float(compute_numeric.iloc[61][bq_col]) if not pd.isna(compute_numeric.iloc[61][bq_col]) else 0,
    }

    result['scores'] = scores

    # 총점 계산 (반영영역에 따라)
    total = 0

    if config['국어']:
        total += scores['국어']
    if config['수학']:
        total += scores['수학']
    if config['영어']:
        total += scores['영어']

    # 탐구 과목 수에 따라
    if config['탐구'] >= 1:
        total += scores['탐구1']
    if config['탐구'] >= 2:
        total += scores['탐구2']

    result['total'] = total
    result['status'] = 'calculated'

    return result


def main():
    print('=' * 80)
    print('NEO GOD v2.3 - 가중택 대학 포함 점수 계산')
    print('=' * 80)

    # 데이터 로드
    print('\n[1] 데이터 로드')
    compute_numeric, compute_string = load_data()
    print(f'  - BigQuery: {len(compute_numeric)}행')
    print(f'  - Parquet: {len(compute_string)}행, {len(compute_string.columns)}열')

    # 대학명 매핑
    with open('output/column_mapping_v2.json', 'r', encoding='utf-8') as f:
        mapping = json.load(f)
    univ_map = mapping.get('university_column_map', {})

    def col_to_idx(col):
        result = 0
        for i, c in enumerate(reversed(col)):
            result += (ord(c) - ord('A') + 1) * (26 ** i)
        return result - 1

    # 주요 대학 계산
    print('\n[2] 주요 대학 점수 계산')
    print('-' * 80)

    major_univs = [
        '서울대', '연세대', '고려대', '성균관', '서강대', '한양대',
        '중앙대', '경희대', '이화여', '건국대', '동국대', '홍익대',
        '숙명여', '국민대', '숭실대', '세종대', '아주대', '인하대'
    ]

    results = []

    print(f"\n{'대학':<10} {'유형':<6} {'국어':>8} {'수학':>8} {'영어':>8} {'탐구1':>8} {'탐구2':>8} {'총점':>10}")
    print('-' * 80)

    for univ in major_univs:
        if univ not in univ_map:
            continue

        col_letter = univ_map[univ]
        col_idx = col_to_idx(col_letter)

        # 문자열 컬럼명 찾기
        col_name_in_string = univ  # 기본
        if univ not in compute_string.columns:
            # 유사한 이름 찾기
            for c in compute_string.columns:
                if c.startswith(univ) and '.' not in c:
                    col_name_in_string = c
                    break

        result = calculate_university_score(
            univ, col_idx, compute_numeric, compute_string, col_name_in_string
        )
        results.append(result)

        scores = result['scores']
        source = result['source'] or 'N/A'

        print(f"{univ:<10} {source:<6} {scores.get('국어',0):>8.1f} {scores.get('수학',0):>8.1f} "
              f"{scores.get('영어',0):>8.1f} {scores.get('탐구1',0):>8.1f} {scores.get('탐구2',0):>8.1f} "
              f"{result['total']:>10.1f}")

    # 가중택 대학 상세 분석
    print('\n[3] 가중택 대학 상세 분석')
    print('-' * 80)

    weighted_univs = [r for r in results if r['source'] == '가중택']

    for r in weighted_univs:
        print(f"\n{r['university']}:")
        print(f"  - 유형: {r['source']}")
        print(f"  - 설정: {r['config']}")
        print(f"  - 점수: {r['scores']}")
        print(f"  - 총점: {r['total']:.1f}")

    # 총점 순위
    print('\n[4] 총점 순위 (상위 15개)')
    print('-' * 80)

    sorted_results = sorted(results, key=lambda x: x['total'], reverse=True)
    for i, r in enumerate(sorted_results[:15], 1):
        source_mark = '⭐' if r['source'] == '가중택' else '  '
        print(f"  {i:2}. {source_mark} {r['university']:<10} ({r['source']:<4}): {r['total']:>10.1f}점")

    return results


if __name__ == '__main__':
    main()
