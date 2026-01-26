# ============================================================
# Score Calculator v4 - 대학명 매핑 + Row 구조 개선
# NEO GOD Ultra Framework v2.3
# ============================================================
"""
갭 1: 대학명 매핑 불일치 해결
  - 서울시립 → 시립대
  - 한국외대 → 외국어

갭 2: Row 구조 개선
  - Row 58 (수학환산) None일 때 대체 Row 탐색
  - Row 44 (점수계산) 활용
"""

import pandas as pd
import json
import re
from google.cloud import bigquery
from google.oauth2 import service_account


# 대학명 매핑 (검색명 → 실제 컬럼명)
UNIV_NAME_MAP = {
    '서울시립': '시립대',
    '한국외대': '외국어',
    '서울과기': '서울과',
    # 기본 대학들은 그대로
}


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


def get_actual_column_name(search_name, compute_string):
    """검색 대학명 → 실제 컬럼명 변환"""
    # 1. 매핑 테이블 확인
    if search_name in UNIV_NAME_MAP:
        actual = UNIV_NAME_MAP[search_name]
        if actual in compute_string.columns:
            return actual

    # 2. 직접 매칭
    if search_name in compute_string.columns:
        return search_name

    # 3. 부분 매칭 (시작)
    for col in compute_string.columns:
        if col.startswith(search_name):
            return col

    return None


def find_best_variant(base_name, compute_string):
    """
    대학의 가장 적합한 변형 컬럼 찾기

    우선순위:
    1. 필수(Row 63)에 설정이 있고 값이 있는 변형
    2. 선택(Row 64)에 설정이 있고 값이 있는 변형
    3. 가중택(Row 65)에 설정이 있는 변형
    """
    # 해당 대학의 모든 변형 찾기
    variants = []
    for col in compute_string.columns:
        if col == base_name or col.startswith(f'{base_name}.'):
            variants.append(col)

    if not variants:
        return None, None, None

    best_variant = None
    best_score = -1
    best_config = None
    best_source = None

    for var in variants:
        # Row 63 (필수), 64 (선택), 65 (가중택) 확인
        row63 = compute_string.iloc[63].get(var)
        row64 = compute_string.iloc[64].get(var)
        row65 = compute_string.iloc[65].get(var)

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
        has_value = row57_val is not None and not pd.isna(row57_val) and row57_val != 0

        # 점수: 필수 > 선택 > 가중택, 값 있음 우선
        score = 0
        if source == '필수':
            score += 100
        elif source == '선택':
            score += 50
        else:
            score += 10

        if has_value:
            score += 1000

        if score > best_score:
            best_score = score
            best_variant = var
            best_config = config_str
            best_source = source

    return best_variant, best_config, best_source


def get_scores_from_variant(variant_name, compute_string):
    """
    변형 컬럼에서 점수 추출 (갭 2: 다중 Row 탐색)

    Row 매핑:
    - Row 57: 국어환산
    - Row 58: 수학환산 (None이면 대체 탐색)
    - Row 59: 영어환산 (None이면 대체 탐색)
    - Row 60: 탐구1환산
    - Row 61: 탐구2환산

    대체 Row:
    - Row 44: 점수계산 (총점 또는 주요 점수)
    - Row 46-47: 추가 점수
    """
    if variant_name not in compute_string.columns:
        return None

    scores = {}

    # 기본 Row 매핑
    primary_rows = {
        '국어': 57,
        '수학': 58,
        '영어': 59,
        '탐구1': 60,
        '탐구2': 61,
    }

    # 대체 Row 매핑 (기본 Row가 None일 때)
    fallback_rows = {
        '수학': [46, 47, 44],  # Row 58이 None이면 46, 47, 44 순으로 탐색
        '영어': [47, 46, 44],
    }

    for name, row_idx in primary_rows.items():
        val = compute_string.iloc[row_idx].get(variant_name)

        # 값이 없으면 대체 Row 탐색
        if (val is None or pd.isna(val)) and name in fallback_rows:
            for fallback_row in fallback_rows[name]:
                fallback_val = compute_string.iloc[fallback_row].get(variant_name)
                if fallback_val is not None and not pd.isna(fallback_val) and fallback_val != 0:
                    val = fallback_val
                    break

        # 최종 값 설정
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
    print('=' * 90)
    print('NEO GOD v4 - 대학명 매핑 + Row 구조 개선')
    print('=' * 90)

    # 데이터 로드
    print('\n[1] 데이터 로드')
    compute_numeric, compute_string = load_data()

    # 주요 대학 (갭 1: 매핑 적용)
    major_univs = [
        '서울대', '연세대', '고려대', '성균관', '서강대', '한양대',
        '중앙대', '경희대', '이화여', '건국대', '동국대', '홍익대',
        '숙명여', '국민대', '숭실대', '세종대', '아주대', '인하대',
        '서울시립', '한국외대',  # 갭 1: 매핑 필요 대학
        '포항공', '카이스트'
    ]

    results = []

    print('\n[2] 대학별 점수 계산')
    print('-' * 100)
    print(f"{'대학':<10} {'실제컬럼':<12} {'변형':<12} {'유형':<6} {'국어':>8} {'수학':>8} {'영어':>8} {'탐구1':>8} {'탐구2':>8} {'총점':>10}")
    print('-' * 100)

    for search_name in major_univs:
        # 갭 1: 대학명 매핑
        actual_name = get_actual_column_name(search_name, compute_string)

        if not actual_name:
            print(f"{search_name:<10} {'N/A':<12} {'-':<12} {'-':<6} {0:>8} {0:>8} {0:>8} {0:>8} {0:>8} {0:>10}")
            continue

        # 최적 변형 찾기
        variant, config_str, source = find_best_variant(actual_name, compute_string)

        if not variant:
            print(f"{search_name:<10} {actual_name:<12} {'N/A':<12} {'N/A':<6} {0:>8} {0:>8} {0:>8} {0:>8} {0:>8} {0:>10}")
            continue

        # 갭 2: 점수 추출 (다중 Row 탐색)
        scores = get_scores_from_variant(variant, compute_string)
        config = parse_config(config_str)

        if not scores or not config:
            continue

        total = calculate_total(scores, config)

        variant_display = variant if variant != actual_name else '-'
        actual_display = actual_name if actual_name != search_name else '-'

        results.append({
            'search_name': search_name,
            'actual_name': actual_name,
            'variant': variant,
            'source': source,
            'config': config,
            'config_str': config_str,
            'scores': scores,
            'total': total
        })

        print(f"{search_name:<10} {actual_display:<12} {variant_display:<12} {source:<6} "
              f"{scores['국어']:>8.1f} {scores['수학']:>8.1f} {scores['영어']:>8.1f} "
              f"{scores['탐구1']:>8.1f} {scores['탐구2']:>8.1f} {total:>10.1f}")

    # 순위
    print('\n[3] 총점 순위')
    print('-' * 80)

    sorted_results = sorted(results, key=lambda x: x['total'], reverse=True)

    for i, r in enumerate(sorted_results, 1):
        mapping_mark = '🔗' if r['actual_name'] != r['search_name'] else '  '
        variant_mark = f"({r['variant']})" if r['variant'] != r['actual_name'] else ""
        source_mark = '⭐' if r['source'] == '가중택' else '  '
        print(f"  {i:2}. {mapping_mark}{source_mark} {r['search_name']:<10} {variant_mark:<15} ({r['source']:<4}): {r['total']:>10.1f}점")

    # 갭 수정 결과 요약
    print('\n[4] 갭 수정 결과')
    print('-' * 80)

    print('\n  [갭 1] 대학명 매핑:')
    mapped = [r for r in results if r['actual_name'] != r['search_name']]
    for r in mapped:
        print(f"    ✓ {r['search_name']} → {r['actual_name']} (국어={r['scores']['국어']:.1f})")

    print('\n  [갭 2] 수학환산 대체 Row 적용:')
    math_found = [r for r in results if r['scores']['수학'] > 0]
    if math_found:
        for r in math_found:
            print(f"    ✓ {r['search_name']}: 수학={r['scores']['수학']:.1f}")
    else:
        print("    - 수학 점수 입력 데이터 없음 (원본 Excel에 수학 점수 미입력)")

    return results


if __name__ == '__main__':
    main()
