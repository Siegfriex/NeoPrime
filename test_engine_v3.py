# ============================================================
# BigQuery 연동 테스트 v3: 원본 데이터로 점수 계산
# NEO GOD Ultra Framework v2.3
# ============================================================
"""
수능입력, 원점수입력 테이블의 실제 데이터를 사용하여
대학별 환산점수를 계산합니다.
"""

import sys
import json
import re
from pathlib import Path
from google.cloud import bigquery
from google.oauth2 import service_account
import yaml
import pandas as pd


def load_config():
    with open('config.yaml', 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def get_bq_client(config):
    creds_path = config['bigquery']['credentials_path']
    credentials = service_account.Credentials.from_service_account_file(creds_path)
    return bigquery.Client(
        credentials=credentials,
        project=config['bigquery']['project_id'],
        location=config['bigquery']['location']
    )


def analyze_source_tables():
    """원본 데이터 테이블 분석"""
    print("=" * 70)
    print("원본 데이터 테이블 분석")
    print("=" * 70)

    config = load_config()
    client = get_bq_client(config)
    project_id = config['bigquery']['project_id']
    dataset_id = config['bigquery']['dataset_id']

    # 주요 테이블 분석
    tables_to_analyze = [
        'tb_raw_2026_수능입력',
        'tb_raw_2026_원점수입력',
        'tb_raw_2026_내신입력',
        'tb_raw_2026_RAWSCORE',
        'tb_raw_2026_PERCENTAGE',
    ]

    for table_name in tables_to_analyze:
        print(f"\n{'─' * 70}")
        print(f"[{table_name}]")
        print('─' * 70)

        try:
            # 행 수 확인
            count_query = f"""
            SELECT COUNT(*) as cnt
            FROM `{project_id}.{dataset_id}.{table_name}`
            """
            count_df = client.query(count_query).to_dataframe()
            row_count = count_df['cnt'].iloc[0]

            # 컬럼 확인
            schema_query = f"""
            SELECT column_name, data_type
            FROM `{project_id}.{dataset_id}.INFORMATION_SCHEMA.COLUMNS`
            WHERE table_name = '{table_name}'
            ORDER BY ordinal_position
            LIMIT 30
            """
            schema_df = client.query(schema_query).to_dataframe()

            print(f"  행 수: {row_count:,}개")
            print(f"  컬럼 수: {len(schema_df)}개+")
            print(f"\n  주요 컬럼:")
            for _, row in schema_df.head(15).iterrows():
                print(f"    • {row['column_name']} ({row['data_type']})")

            # 샘플 데이터
            sample_query = f"""
            SELECT *
            FROM `{project_id}.{dataset_id}.{table_name}`
            LIMIT 5
            """
            sample_df = client.query(sample_query).to_dataframe()

            print(f"\n  샘플 데이터 (첫 5행, 첫 5컬럼):")
            cols = list(sample_df.columns)[:5]
            for i, row in sample_df.head(5).iterrows():
                vals = [str(row[c])[:15] for c in cols]
                print(f"    {i}: {vals}")

        except Exception as e:
            print(f"  [오류] {e}")

    # 수능입력 테이블 상세 분석
    print("\n" + "=" * 70)
    print("수능입력 테이블 상세 분석")
    print("=" * 70)

    try:
        query = f"""
        SELECT *
        FROM `{project_id}.{dataset_id}.tb_raw_2026_수능입력`
        LIMIT 20
        """
        df = client.query(query).to_dataframe()

        print(f"\n전체 컬럼: {list(df.columns)}")

        # 점수 관련 컬럼 찾기
        score_cols = [c for c in df.columns if any(kw in str(c) for kw in ['점수', '국어', '수학', '영어', '탐구', 'score'])]
        print(f"\n점수 관련 컬럼: {score_cols}")

        # 데이터 미리보기
        print("\n데이터 미리보기:")
        print(df.head(10).to_string())

    except Exception as e:
        print(f"[오류] {e}")

    # RAWSCORE 테이블 분석 (환산점수의 원본일 가능성)
    print("\n" + "=" * 70)
    print("RAWSCORE 테이블 상세 분석")
    print("=" * 70)

    try:
        query = f"""
        SELECT *
        FROM `{project_id}.{dataset_id}.tb_raw_2026_RAWSCORE`
        LIMIT 20
        """
        df = client.query(query).to_dataframe()

        print(f"\n전체 컬럼 수: {len(df.columns)}")
        print(f"컬럼 목록 (처음 20개): {list(df.columns)[:20]}")

        # 데이터 미리보기
        print("\n데이터 미리보기 (처음 5열):")
        print(df.iloc[:, :5].head(10).to_string())

    except Exception as e:
        print(f"[오류] {e}")

    return df


def test_score_calculation_flow():
    """점수 계산 플로우 테스트"""
    print("\n" + "=" * 70)
    print("점수 계산 플로우 분석")
    print("=" * 70)

    print("""
    [Excel 수식 분석]

    서울대 환산점수 수식: =JL$58+JL$59+JL$60+JL$61+JL$62

    이 수식이 참조하는 값들:
    - JL$58: COMPUTE 시트의 JL열 58행 (국어 환산점수)
    - JL$59: COMPUTE 시트의 JL열 59행 (수학 환산점수)
    - JL$60: COMPUTE 시트의 JL열 60행 (영어 환산점수)
    - JL$61: COMPUTE 시트의 JL열 61행 (탐구1 환산점수)
    - JL$62: COMPUTE 시트의 JL열 62행 (탐구2 환산점수)

    [문제]
    COMPUTE 시트의 JL58-62 값들도 또 다른 수식의 결과임!
    → 이 값들은 RAWSCORE, PERCENTAGE 등에서 가져와 가공된 것

    [해결 방안]
    1. 수식 체인 전체 추적 (COMPUTE → RAWSCORE → 원점수입력)
    2. 또는 Excel에서 "값만 복사"된 결과를 사용
    3. 현재 BigQuery의 COMPUTE 테이블에 이미 계산된 값이 있다면 그것을 사용

    [현재 상태]
    - BigQuery COMPUTE 테이블의 값이 대부분 0/NULL
    - 이는 Excel 수식이 아직 평가되지 않았거나,
    - 원본 데이터가 입력되지 않은 상태에서 추출되었기 때문

    [추천 접근법]
    1. Excel 파일을 "수식 → 값" 변환 후 재적재
    2. 또는 Python에서 전체 수식 체인을 구현
    """)


if __name__ == '__main__':
    analyze_source_tables()
    test_score_calculation_flow()
