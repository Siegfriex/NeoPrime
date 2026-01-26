# ============================================================
# Score Calculator v5 - 올바른 Row 구조 적용
# NEO GOD Ultra Framework v2.3
# ============================================================
"""
핵심 수정:
- Row 57-61은 영역별 총점/응시자격 (개별 과목 아님!)
- 개별 과목 환산: Row 9(국어), 13(수학), 16(영어), 18-34(탐구)

갭 수정:
- 갭 5: Row 9,13,16 사용 (개별 과목)
- 갭 6: 카이스트 = 과기원 매핑
- 갭 7: 수학/영어 분리
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
    '카이스트': '과기원',  # 갭 6: 추가
    'KAIST': '과기원',
}

# 올바른 Row 매핑
ROW_MAP = {
    # 개별 과목 환산 (Row 7-43)
    '국어_화작': 7,
    '국어_언매': 8,
    '국어': 9,
    '수학_미적': 10,
    '수학_기하': 11,
    '수학_확통': 12,
    '수학': 13,
    '수학_이과': 14,
    '수학_문과': 15,
    '영어': 16,
    '한국사': 17,
    # 탐구 (Row 18-43)
    '물리1': 18,
    '물리2': 19,
    '생명1': 20,
    '생명2': 21,
    '지구1': 22,
    '지구2': 23,
    '화학1': 24,
    '화학2': 25,
    # 사탐 (Row 26-34)
    '경제': 26,
    '동아시아사': 27,
    '사회문화': 28,
    '생활윤리': 29,
    '세계사': 30,
    '세계지리': 31,
    '윤리사상': 32,
    '정치법': 33,
    '한국지리': 34,

    # 영역별 총점 (Row 57-59)
    '필수총점': 57,
    '선택총점': 58,
    '가중택총점': 59,

    # 설정 (Row 63-65)
    '필수설정': 63,
    '선택설정': 64,
    '가중택설정': 65,

    # 점수계산 (Row 44)
    '점수계산': 44,
}


def load_data():
    """데이터 로드"""
    creds = service_account.Credentials.from_service_account_file('neoprime-loader-key.json')
    client = bigquery.Client(credentials=creds, project='neoprime0305', location='asia-northeast3')

    compute_string = pd.read_parquet('output/COMPUTE_chunk_0000.parquet')

    return compute_string


def get_actual_column_name(search_name, compute_string):
    """검색 대학명 → 실제 컬럼명 변환"""
    if search_name in UNIV_NAME_MAP:
        actual = UNIV_NAME_MAP[search_name]
        if actual in compute_string.columns:
            return actual

    if search_name in compute_string.columns:
        return search_name

    for col in compute_string.columns:
        if col.startswith(search_name):
            return col

    return None


def find_best_variant(base_name, compute_string):
    """대학의 가장 적합한 변형 컬럼 찾기"""
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
        row63 = compute_string.iloc[ROW_MAP['필수설정']].get(var)
        row64 = compute_string.iloc[ROW_MAP['선택설정']].get(var)
        row65 = compute_string.iloc[ROW_MAP['가중택설정']].get(var)

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

        # 국어 값 확인 (Row 9)
        korean_val = compute_string.iloc[ROW_MAP['국어']].get(var)
        has_value = korean_val is not None and not pd.isna(korean_val) and korean_val != 0

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
    변형 컬럼에서 개별 과목 점수 추출 (v5: 올바른 Row 사용)
    """
    if variant_name not in compute_string.columns:
        return None

    def safe_float(val):
        if val is None or pd.isna(val):
            return 0.0
        try:
            return float(val)
        except:
            return 0.0

    scores = {
        '국어': safe_float(compute_string.iloc[ROW_MAP['국어']].get(variant_name)),
        '수학': safe_float(compute_string.iloc[ROW_MAP['수학']].get(variant_name)),
        '영어': safe_float(compute_string.iloc[ROW_MAP['영어']].get(variant_name)),
    }

    # 탐구: 과탐 또는 사탐 중 값이 있는 것 사용
    tamgu_rows = [
        ('물리1', 18), ('물리2', 19), ('생명1', 20), ('생명2', 21),
        ('지구1', 22), ('지구2', 23), ('화학1', 24), ('화학2', 25),
        ('경제', 26), ('동아시아사', 27), ('사회문화', 28), ('생활윤리', 29),
        ('세계사', 30), ('세계지리', 31), ('윤리사상', 32), ('정치법', 33), ('한국지리', 34),
    ]

    tamgu_scores = []
    for name, row_idx in tamgu_rows:
        val = safe_float(compute_string.iloc[row_idx].get(variant_name))
        if val != 0:
            tamgu_scores.append((name, val))

    # 상위 2개 탐구
    tamgu_scores.sort(key=lambda x: x[1], reverse=True)
    scores['탐구1'] = tamgu_scores[0][1] if len(tamgu_scores) >= 1 else 0.0
    scores['탐구2'] = tamgu_scores[1][1] if len(tamgu_scores) >= 2 else 0.0
    scores['탐구1_과목'] = tamgu_scores[0][0] if len(tamgu_scores) >= 1 else '-'
    scores['탐구2_과목'] = tamgu_scores[1][0] if len(tamgu_scores) >= 2 else '-'

    # 영역별 총점 (참고)
    scores['필수총점'] = safe_float(compute_string.iloc[ROW_MAP['필수총점']].get(variant_name))
    scores['선택총점'] = safe_float(compute_string.iloc[ROW_MAP['선택총점']].get(variant_name))
    scores['가중택총점'] = safe_float(compute_string.iloc[ROW_MAP['가중택총점']].get(variant_name))

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
    }

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
    print('=' * 100)
    print('NEO GOD v5 - 올바른 Row 구조 (개별과목: Row 9,13,16)')
    print('=' * 100)

    compute_string = load_data()

    major_univs = [
        '서울대', '연세대', '고려대', '성균관', '서강대', '한양대',
        '중앙대', '경희대', '이화여', '건국대', '동국대', '홍익대',
        '숙명여', '국민대', '숭실대', '세종대', '아주대', '인하대',
        '서울시립', '한국외대', '카이스트',
    ]

    results = []

    print('\n[1] 대학별 점수 계산 (개별 과목 Row 사용)')
    print('-' * 110)
    print(f"{'대학':<10} {'실제컬럼':<10} {'변형':<10} {'유형':<6} {'국어':>8} {'수학':>8} {'영어':>8} {'탐구1':>8} {'탐구2':>8} {'합계':>10} {'필수총점':>10}")
    print('-' * 110)

    for search_name in major_univs:
        actual_name = get_actual_column_name(search_name, compute_string)

        if not actual_name:
            print(f"{search_name:<10} {'N/A':<10} {'-':<10} {'-':<6} {0:>8} {0:>8} {0:>8} {0:>8} {0:>8} {0:>10} {0:>10}")
            continue

        variant, config_str, source = find_best_variant(actual_name, compute_string)

        if not variant:
            print(f"{search_name:<10} {actual_name:<10} {'N/A':<10} {'N/A':<6} {0:>8} {0:>8} {0:>8} {0:>8} {0:>8} {0:>10} {0:>10}")
            continue

        scores = get_scores_from_variant(variant, compute_string)
        config = parse_config(config_str)

        if not scores or not config:
            continue

        total = calculate_total(scores, config)

        variant_display = variant.replace(actual_name, '') if variant != actual_name else '-'
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

        print(f"{search_name:<10} {actual_display:<10} {variant_display:<10} {source:<6} "
              f"{scores['국어']:>8.1f} {scores['수학']:>8.1f} {scores['영어']:>8.1f} "
              f"{scores['탐구1']:>8.1f} {scores['탐구2']:>8.1f} {total:>10.1f} {scores['필수총점']:>10.1f}")

    # 순위
    print('\n[2] 총점 순위')
    print('-' * 80)

    sorted_results = sorted(results, key=lambda x: x['total'], reverse=True)

    for i, r in enumerate(sorted_results, 1):
        mapping_mark = '🔗' if r['actual_name'] != r['search_name'] else '  '
        variant_mark = f"(.{r['variant'].split('.')[-1]})" if '.' in r['variant'] else ""
        source_mark = '⭐' if r['source'] == '가중택' else '  '
        print(f"  {i:2}. {mapping_mark}{source_mark} {r['search_name']:<10} {variant_mark:<6} ({r['source']:<4}): {r['total']:>10.1f}점")

    # v4 vs v5 비교
    print('\n[3] 갭 수정 결과')
    print('-' * 80)

    print('\n  [갭 5] 개별과목 Row 사용 (v4: Row57=총점 → v5: Row9,13,16=개별):')
    for r in results[:5]:
        print(f"    {r['search_name']}: 국어(R9)={r['scores']['국어']:.1f}, 수학(R13)={r['scores']['수학']:.1f}, 영어(R16)={r['scores']['영어']:.1f}")

    print('\n  [갭 6] 카이스트 매핑:')
    kaist = next((r for r in results if r['search_name'] == '카이스트'), None)
    if kaist:
        print(f"    ✓ 카이스트 → {kaist['actual_name']} (국어={kaist['scores']['국어']:.1f}, 총점={kaist['total']:.1f})")

    print('\n  [갭 7] 수학/영어 분리 (v4: Row46=47 동일 → v5: Row13/16 분리):')
    for r in results:
        if r['scores']['수학'] != r['scores']['영어'] and r['scores']['수학'] > 0:
            print(f"    ✓ {r['search_name']}: 수학={r['scores']['수학']:.1f}, 영어={r['scores']['영어']:.1f}")
            break

    # 데이터 품질 체크
    print('\n[4] 데이터 품질')
    print('-' * 80)
    zero_math = [r for r in results if r['scores']['수학'] == 0]
    zero_eng = [r for r in results if r['scores']['영어'] == 0]
    print(f'  수학=0: {len(zero_math)}개 대학 (원본 데이터에 수학 점수 미입력)')
    print(f'  영어=0: {len(zero_eng)}개 대학')

    return results


if __name__ == '__main__':
    main()
