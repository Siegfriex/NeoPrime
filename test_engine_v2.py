# ============================================================
# BigQuery 연동 테스트 v2: 실제 데이터로 점수 계산
# NEO GOD Ultra Framework v2.3
# ============================================================
"""
BigQuery의 COMPUTE 테이블에서 실제 점수를 추출하고
대학별 환산점수를 검증합니다.
"""

import sys
import json
import re
from pathlib import Path
from google.cloud import bigquery
from google.oauth2 import service_account
import yaml

# 로컬 모듈
from column_mapper import ColumnMapper, excel_col_to_index


def load_config():
    """config.yaml 로드"""
    with open('config.yaml', 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def get_bq_client(config):
    """BigQuery 클라이언트 생성"""
    creds_path = config['bigquery']['credentials_path']
    credentials = service_account.Credentials.from_service_account_file(creds_path)
    return bigquery.Client(
        credentials=credentials,
        project=config['bigquery']['project_id'],
        location=config['bigquery']['location']
    )


def get_compute_row_data(client, project_id, dataset_id, row_offset: int) -> dict:
    """
    COMPUTE 테이블에서 특정 행의 데이터를 가져옴

    Args:
        row_offset: 0-based row offset (Excel 행 58 = offset 57 또는 데이터 시작 기준)

    Returns:
        {column_name: value} 딕셔너리
    """
    # 먼저 컬럼 목록 가져오기
    schema_query = f"""
    SELECT column_name
    FROM `{project_id}.{dataset_id}.INFORMATION_SCHEMA.COLUMNS`
    WHERE table_name = 'tb_raw_2026_COMPUTE'
    ORDER BY ordinal_position
    """
    columns_df = client.query(schema_query).to_dataframe()
    columns = columns_df['column_name'].tolist()

    # 특정 행 데이터 가져오기
    query = f"""
    SELECT *
    FROM `{project_id}.{dataset_id}.tb_raw_2026_COMPUTE`
    LIMIT 1 OFFSET {row_offset}
    """
    result_df = client.query(query).to_dataframe()

    if len(result_df) == 0:
        return {}

    row_data = result_df.iloc[0].to_dict()
    return row_data, columns


def test_university_score_calculation():
    """대학별 환산점수 계산 테스트"""
    print("=" * 70)
    print("BigQuery 연동 테스트 v2: 실제 데이터로 대학 점수 계산")
    print("=" * 70)

    # 1. 설정 및 연결
    print("\n[Step 1] BigQuery 연결...")
    config = load_config()
    client = get_bq_client(config)
    project_id = config['bigquery']['project_id']
    dataset_id = config['bigquery']['dataset_id']
    print("  - 연결 성공")

    # 2. Column Mapper 초기화
    print("\n[Step 2] 컬럼 매퍼 초기화...")
    mapper = ColumnMapper()

    # 3. COMPUTE 테이블 구조 분석
    print("\n[Step 3] COMPUTE 테이블 구조 분석...")

    # 첫 몇 행 가져오기
    query = f"""
    SELECT *
    FROM `{project_id}.{dataset_id}.tb_raw_2026_COMPUTE`
    LIMIT 70
    """
    df = client.query(query).to_dataframe()
    print(f"  - 로드된 행: {len(df)}개")
    print(f"  - 컬럼 수: {len(df.columns)}개")

    # 컬럼 목록
    columns = list(df.columns)

    # 4. 특정 행 분석 (행 58 = 국어 점수 행으로 가정)
    print("\n[Step 4] 데이터 구조 분석...")

    # Excel에서 행 58은 보통 데이터 영역
    # BigQuery에서는 0-indexed이므로 실제 위치 확인 필요

    # 첫 번째 컬럼의 값들을 확인하여 데이터 패턴 파악
    print("\n  [첫 번째 컬럼 데이터 샘플]:")
    first_col = columns[0]
    for i in range(min(10, len(df))):
        val = df.iloc[i][first_col]
        print(f"    행 {i}: {val}")

    # 5. 대학 컬럼 인덱스로 실제 값 추출 테스트
    print("\n[Step 5] 대학별 컬럼 인덱스 → 실제 값 매핑 테스트...")

    # 가천대 (컬럼 F = 인덱스 5)
    test_universities = [
        ('가천대', 'F', 5),
        ('가톨릭', 'J', 9),
        ('서울대', 'JL', 271),
    ]

    for univ_name, col_letter, col_idx in test_universities:
        print(f"\n  [{univ_name}] (Excel 컬럼 {col_letter}, 인덱스 {col_idx}):")

        if col_idx < len(columns):
            actual_col_name = columns[col_idx]
            print(f"    BigQuery 컬럼명: {actual_col_name}")

            # 행 58-62 (국어~탐구2) 값 추출 시도
            # Excel 행 번호와 BigQuery 행 인덱스 매핑 필요
            for row_label, row_offset in [('국어(행58)', 57), ('수학(행59)', 58), ('영어(행60)', 59)]:
                if row_offset < len(df):
                    val = df.iloc[row_offset][actual_col_name]
                    print(f"    {row_label}: {val}")
        else:
            print(f"    [오류] 컬럼 인덱스 {col_idx}가 범위를 벗어남 (최대: {len(columns)-1})")

    # 6. 실제 환산점수 계산 테스트
    print("\n[Step 6] 환산점수 계산 시뮬레이션...")

    # 가천대 수식: =F$58+F$59+F$60+F$61+F$62
    # 즉, 국어+수학+영어+탐구1+탐구2

    col_idx = 5  # 가천대 (F 컬럼)
    if col_idx < len(columns):
        actual_col = columns[col_idx]
        scores = []
        for row_idx in range(57, 62):  # 행 58-62 (0-indexed: 57-61)
            if row_idx < len(df):
                val = df.iloc[row_idx][actual_col]
                try:
                    scores.append(float(val) if val is not None else 0)
                except:
                    scores.append(0)

        print(f"\n  [가천대 환산점수 계산]")
        print(f"    컬럼: {actual_col}")
        print(f"    국어(행58): {scores[0] if len(scores)>0 else 'N/A'}")
        print(f"    수학(행59): {scores[1] if len(scores)>1 else 'N/A'}")
        print(f"    영어(행60): {scores[2] if len(scores)>2 else 'N/A'}")
        print(f"    탐구1(행61): {scores[3] if len(scores)>3 else 'N/A'}")
        print(f"    탐구2(행62): {scores[4] if len(scores)>4 else 'N/A'}")
        print(f"    ────────────")
        print(f"    합계: {sum(scores)}")

    print("\n" + "=" * 70)
    print("[결론]")
    print("=" * 70)
    print("""
    현재 BigQuery 테이블 구조와 Excel 수식 간의 매핑 이슈:

    1. Excel 수식 =F$58+F$59+... 은:
       - 컬럼 F (대학 가천대)의
       - 행 58-62 (국어~탐구2 점수)를 합산

    2. BigQuery 테이블은:
       - 컬럼명이 'column_0', 'unnamed_1' 등으로 저장됨
       - 행 순서가 Excel과 동일하다고 가정

    3. 해결 방안:
       a) Phase 2에서 컬럼명을 대학명으로 저장하도록 수정
       b) 또는 컬럼 인덱스 → 대학명 매핑 테이블 사용

    4. 현재 엔진 수정 필요:
       - row['JL58'] 대신 → row[columns[271]] 형태로
       - 또는 의미론적 접근: row['서울대']['국어']
    """)

    return df, columns


if __name__ == '__main__':
    df, columns = test_university_score_calculation()
