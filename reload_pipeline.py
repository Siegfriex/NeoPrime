# ============================================================
# Reload Pipeline: 전체 재적재 통합 파이프라인
# NEO GOD Ultra Framework v2.3
# ============================================================
"""
전체 재적재 프로세스를 한 번에 실행합니다:
1. Excel 값 변환
2. config.yaml 업데이트
3. BigQuery 기존 테이블 삭제 (선택)
4. 마스터 파이프라인 재실행
5. 검증

사용법:
    python reload_pipeline.py [--clean] [--with-test-data]
"""

import os
import sys
import yaml
import argparse
from pathlib import Path
from datetime import datetime


def update_config(config_path: str, new_source_file: str) -> dict:
    """config.yaml 업데이트"""
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)

    old_source = config.get('source_file', 'N/A')
    config['source_file'] = new_source_file

    with open(config_path, 'w', encoding='utf-8') as f:
        yaml.dump(config, f, allow_unicode=True, default_flow_style=False)

    print(f"  - 이전: {old_source}")
    print(f"  - 변경: {new_source_file}")

    return config


def delete_existing_tables(config: dict, confirm: bool = True) -> int:
    """BigQuery 기존 테이블 삭제"""
    from google.cloud import bigquery
    from google.oauth2 import service_account

    project_id = config['bigquery']['project_id']
    dataset_id = config['bigquery']['dataset_id']
    creds_path = config['bigquery']['credentials_path']

    credentials = service_account.Credentials.from_service_account_file(creds_path)
    client = bigquery.Client(
        credentials=credentials,
        project=project_id,
        location=config['bigquery'].get('location', 'asia-northeast3')
    )

    # 기존 테이블 목록 조회
    query = f"""
    SELECT table_name
    FROM `{project_id}.{dataset_id}.INFORMATION_SCHEMA.TABLES`
    WHERE table_name LIKE 'tb_raw_2026_%'
      AND table_name NOT LIKE '%_backup%'
    """
    tables = [row.table_name for row in client.query(query)]

    if not tables:
        print("  - 삭제할 테이블이 없습니다.")
        return 0

    print(f"  - 삭제 대상: {len(tables)}개 테이블")
    for t in tables:
        print(f"    • {t}")

    if confirm:
        response = input("\n  삭제하시겠습니까? (y/N): ")
        if response.lower() != 'y':
            print("  - 삭제 취소됨")
            return 0

    # 테이블 삭제
    deleted = 0
    for table_name in tables:
        table_ref = f"{project_id}.{dataset_id}.{table_name}"
        try:
            client.delete_table(table_ref)
            print(f"  - 삭제됨: {table_name}")
            deleted += 1
        except Exception as e:
            print(f"  - 삭제 실패: {table_name} - {e}")

    return deleted


def verify_reload(config: dict) -> dict:
    """재적재 결과 검증"""
    from google.cloud import bigquery
    from google.oauth2 import service_account

    project_id = config['bigquery']['project_id']
    dataset_id = config['bigquery']['dataset_id']
    creds_path = config['bigquery']['credentials_path']

    credentials = service_account.Credentials.from_service_account_file(creds_path)
    client = bigquery.Client(
        credentials=credentials,
        project=project_id,
        location=config['bigquery'].get('location', 'asia-northeast3')
    )

    results = {}

    # 테이블 수 및 행 수 확인
    query = f"""
    SELECT
        table_name,
        row_count
    FROM `{project_id}.{dataset_id}.__TABLES__`
    WHERE table_id LIKE 'tb_raw_2026_%'
      AND table_id NOT LIKE '%_backup%'
    ORDER BY table_id
    """

    try:
        df = client.query(query).to_dataframe()
        results['tables'] = len(df)
        results['total_rows'] = df['row_count'].sum()
        results['table_details'] = df.to_dict('records')
    except Exception as e:
        results['error'] = str(e)

    # COMPUTE 테이블 값 샘플
    try:
        sample_query = f"""
        SELECT column_271, column_272, column_273
        FROM `{project_id}.{dataset_id}.tb_raw_2026_COMPUTE`
        LIMIT 5 OFFSET 55
        """
        sample_df = client.query(sample_query).to_dataframe()
        results['compute_sample'] = sample_df.to_dict('records')

        # NULL/0 비율 계산
        null_count = sample_df.isna().sum().sum() + (sample_df == 0).sum().sum()
        total_cells = sample_df.size
        results['valid_data_pct'] = round((total_cells - null_count) / total_cells * 100, 1)
    except Exception as e:
        results['compute_sample_error'] = str(e)

    return results


def run_reload_pipeline(
    source_file: str = None,
    with_test_data: bool = False,
    clean_tables: bool = False,
    skip_excel: bool = False
):
    """전체 재적재 파이프라인 실행"""

    print("=" * 70)
    print("NEO GOD Ultra v2.3 - 전체 재적재 파이프라인")
    print("=" * 70)
    print(f"시작 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    config_path = 'config.yaml'

    # Step 1: Excel 값 변환
    if not skip_excel:
        print("\n" + "─" * 70)
        print("[Step 1/5] Excel 값 변환")
        print("─" * 70)

        try:
            from excel_value_converter import ExcelValueConverter

            if source_file is None:
                source_file = r"Y:\0126\0126\202511고속성장분석기(가채점)20251114.xlsx"

            converter = ExcelValueConverter(source_file)

            test_data = ExcelValueConverter.DEFAULT_TEST_DATA if with_test_data else None

            new_file = converter.run(test_data=test_data, verbose=True)

        except ImportError:
            print("[오류] excel_value_converter.py를 찾을 수 없습니다.")
            print("       수동으로 Excel에서 '값으로 붙여넣기'를 실행해주세요.")
            return
        except Exception as e:
            print(f"[오류] Excel 변환 실패: {e}")
            return
    else:
        print("\n[Step 1/5] Excel 변환 건너뜀 (--skip-excel)")
        new_file = source_file

    # Step 2: config.yaml 업데이트
    print("\n" + "─" * 70)
    print("[Step 2/5] config.yaml 업데이트")
    print("─" * 70)

    config = update_config(config_path, new_file)

    # Step 3: BigQuery 테이블 삭제 (선택)
    if clean_tables:
        print("\n" + "─" * 70)
        print("[Step 3/5] BigQuery 기존 테이블 삭제")
        print("─" * 70)

        deleted = delete_existing_tables(config, confirm=True)
        print(f"  - {deleted}개 테이블 삭제됨")
    else:
        print("\n[Step 3/5] 테이블 삭제 건너뜀 (--clean 옵션 없음)")

    # Step 4: 마스터 파이프라인 실행
    print("\n" + "─" * 70)
    print("[Step 4/5] 마스터 파이프라인 실행")
    print("─" * 70)

    try:
        from master_pipeline import MasterPipeline

        pipeline = MasterPipeline(config_path=config_path)
        result = pipeline.run()

        print(f"\n  파이프라인 결과:")
        print(f"  - 상태: {result.get('status', 'unknown')}")

    except Exception as e:
        print(f"[오류] 파이프라인 실행 실패: {e}")
        import traceback
        traceback.print_exc()

    # Step 5: 검증
    print("\n" + "─" * 70)
    print("[Step 5/5] 재적재 결과 검증")
    print("─" * 70)

    verify_result = verify_reload(config)

    print(f"\n  검증 결과:")
    print(f"  - 테이블 수: {verify_result.get('tables', 'N/A')}개")
    print(f"  - 총 행 수: {verify_result.get('total_rows', 'N/A'):,}행")
    print(f"  - COMPUTE 유효 데이터: {verify_result.get('valid_data_pct', 'N/A')}%")

    if 'compute_sample' in verify_result:
        print(f"\n  COMPUTE 테이블 샘플 (row 56-60):")
        for i, row in enumerate(verify_result['compute_sample']):
            print(f"    {i}: {row}")

    # 완료
    print("\n" + "=" * 70)
    print("재적재 완료")
    print(f"종료 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)

    return verify_result


def main():
    """CLI 메인"""
    parser = argparse.ArgumentParser(
        description='전체 재적재 파이프라인을 실행합니다.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
예시:
  python reload_pipeline.py                    # 기본 실행
  python reload_pipeline.py --with-test-data   # 테스트 데이터 포함
  python reload_pipeline.py --clean            # 기존 테이블 삭제 후 실행
  python reload_pipeline.py --skip-excel       # Excel 변환 건너뛰기
        """
    )

    parser.add_argument(
        '--input', '-i',
        default=None,
        help='입력 Excel 파일 경로'
    )

    parser.add_argument(
        '--with-test-data', '-t',
        action='store_true',
        help='테스트 데이터 입력 후 변환'
    )

    parser.add_argument(
        '--clean', '-c',
        action='store_true',
        help='기존 BigQuery 테이블 삭제'
    )

    parser.add_argument(
        '--skip-excel',
        action='store_true',
        help='Excel 변환 단계 건너뛰기'
    )

    args = parser.parse_args()

    run_reload_pipeline(
        source_file=args.input,
        with_test_data=args.with_test_data,
        clean_tables=args.clean,
        skip_excel=args.skip_excel
    )


if __name__ == '__main__':
    main()
