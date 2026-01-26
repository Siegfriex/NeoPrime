# ============================================================
# BigQuery 연동 테스트: University Score Engine
# NEO GOD Ultra Framework v2.3
# ============================================================
"""
BigQuery의 실제 데이터로 UniversityScoreEngine을 테스트합니다.
"""

import sys
import json
from pathlib import Path
from google.cloud import bigquery
from google.oauth2 import service_account

# 로컬 모듈 임포트
sys.path.insert(0, str(Path(__file__).parent / 'output'))
from university_score_engine import UniversityScoreEngine


def load_config():
    """config.yaml 로드"""
    import yaml
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


def get_table_schema(client, project_id, dataset_id, table_name):
    """테이블 스키마 조회"""
    table_ref = f"{project_id}.{dataset_id}.{table_name}"
    table = client.get_table(table_ref)
    return [(field.name, field.field_type) for field in table.schema]


def load_compute_sample(client, project_id, dataset_id, limit=5):
    """COMPUTE 테이블에서 샘플 데이터 로드"""
    query = f"""
    SELECT *
    FROM `{project_id}.{dataset_id}.tb_raw_2026_COMPUTE`
    LIMIT {limit}
    """
    result = client.query(query).to_dataframe()
    return result


def test_engine_with_bq_data():
    """BigQuery 데이터로 엔진 테스트"""
    print("=" * 60)
    print("BigQuery 연동 테스트: University Score Engine")
    print("=" * 60)

    # 1. 설정 로드
    print("\n[Step 1] 설정 로드...")
    config = load_config()
    project_id = config['bigquery']['project_id']
    dataset_id = config['bigquery']['dataset_id']
    print(f"  - Project: {project_id}")
    print(f"  - Dataset: {dataset_id}")

    # 2. BigQuery 연결
    print("\n[Step 2] BigQuery 연결...")
    client = get_bq_client(config)
    print("  - 연결 성공")

    # 3. 테이블 목록 조회
    print("\n[Step 3] 테이블 목록 조회...")
    tables_query = f"""
    SELECT table_name
    FROM `{project_id}.{dataset_id}.INFORMATION_SCHEMA.TABLES`
    WHERE table_name LIKE 'tb_raw_2026_%'
      AND table_name NOT LIKE '%_backup%'
      AND table_name NOT LIKE '%_quarantine%'
    ORDER BY table_name
    """
    tables_df = client.query(tables_query).to_dataframe()
    print(f"  - 발견된 테이블: {len(tables_df)}개")
    for _, row in tables_df.iterrows():
        print(f"    • {row['table_name']}")

    # 4. COMPUTE 테이블 스키마 확인
    print("\n[Step 4] COMPUTE 테이블 스키마 확인...")
    try:
        schema = get_table_schema(client, project_id, dataset_id, 'tb_raw_2026_COMPUTE')
        print(f"  - 컬럼 수: {len(schema)}개")
        # 대학명 컬럼 찾기 (예: 서울대, 연세대 등)
        univ_cols = [col for col, _ in schema if not col.startswith('col_') and not col.startswith('_')]
        print(f"  - 대학 관련 컬럼 예시: {univ_cols[:5]}...")
    except Exception as e:
        print(f"  - 스키마 조회 실패: {e}")
        return

    # 5. 샘플 데이터 로드
    print("\n[Step 5] COMPUTE 테이블 샘플 데이터 로드...")
    try:
        sample_df = load_compute_sample(client, project_id, dataset_id, limit=3)
        print(f"  - 로드된 행: {len(sample_df)}개")
        print(f"  - 컬럼 수: {len(sample_df.columns)}개")
    except Exception as e:
        print(f"  - 데이터 로드 실패: {e}")
        return

    # 6. 엔진 초기화 및 테스트
    print("\n[Step 6] UniversityScoreEngine 테스트...")

    # DataFrame을 sheets 딕셔너리로 변환
    sheets = {'COMPUTE': sample_df}
    engine = UniversityScoreEngine(sheets)

    # 첫 번째 행을 딕셔너리로 변환
    if len(sample_df) > 0:
        # 컬럼명에서 셀 참조 형태로 매핑 필요
        # COMPUTE 시트의 각 행은 특정 데이터 행에 해당
        # 엔진이 기대하는 row['JL58'] 형태와 실제 데이터 매핑 필요

        print("\n  [분석] 엔진이 기대하는 데이터 형식:")
        print("    - 엔진: row['JL58'] (서울대 수식의 국어 점수)")
        print("    - 실제: COMPUTE 테이블의 컬럼 구조 확인 필요")

        # 실제 컬럼명 출력
        print(f"\n  [실제 컬럼명 샘플]:")
        cols = list(sample_df.columns)[:20]
        for col in cols:
            print(f"    • {col}")

        # 매핑 분석
        print("\n  [결론]")
        print("    Excel 수식의 셀 참조(JL58)와 BigQuery 테이블 컬럼명(col_N) 사이에")
        print("    매핑 로직이 필요합니다.")
        print("\n    다음 단계:")
        print("    1. Excel 원본에서 컬럼 인덱스 ↔ 대학명 매핑 추출")
        print("    2. 행 번호(58, 59...) → 영역(국어, 수학...) 매핑 생성")
        print("    3. 엔진 수정: row['JL58'] → row['서울대_국어'] 형태로")

    print("\n" + "=" * 60)
    print("테스트 완료")
    print("=" * 60)


def analyze_column_mapping():
    """컬럼 매핑 분석"""
    print("\n" + "=" * 60)
    print("[추가 분석] Excel 컬럼 인덱스 → 대학명 매핑")
    print("=" * 60)

    # COMPUTE 메타데이터에서 대학명 추출
    metadata_path = Path('./output/COMPUTE_formula_metadata.json')
    if metadata_path.exists():
        with open(metadata_path, 'r', encoding='utf-8') as f:
            metadata = json.load(f)

        formula_samples = metadata.get('formula_samples', {})
        print(f"\n  대학 수: {len(formula_samples)}개")

        # 컬럼 인덱스 추출 (수식에서)
        print("\n  대학별 컬럼 인덱스 매핑:")
        import re
        mappings = []
        for univ_name, data in list(formula_samples.items())[:10]:
            formula = data.get('formula', '')
            # =F$58 에서 F 추출
            match = re.search(r'=([A-Z]+)\$', formula)
            if match:
                col_letter = match.group(1)
                mappings.append((univ_name, col_letter))
                print(f"    • {univ_name}: 컬럼 {col_letter}")

        return mappings
    return []


if __name__ == '__main__':
    test_engine_with_bq_data()
    analyze_column_mapping()
