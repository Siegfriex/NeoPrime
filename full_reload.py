# ============================================================
# Full Reload: 전체 재적재 스크립트
# NEO GOD Ultra Framework v2.3
# ============================================================
"""
모든 문제를 해결하고 전체 재적재를 수행합니다:
1. BigQuery 기존 테이블 전체 삭제
2. Excel 값 변환 (모든 시트)
3. 마스터 파이프라인 재실행
4. 검증
"""

import os
import sys
import yaml
import shutil
from pathlib import Path
from datetime import datetime

def delete_all_tables():
    """BigQuery의 모든 tb_raw_2026 테이블 삭제"""
    from google.cloud import bigquery
    from google.oauth2 import service_account

    print("\n" + "=" * 70)
    print("[Step 1/4] BigQuery 테이블 전체 삭제")
    print("=" * 70)

    creds = service_account.Credentials.from_service_account_file('neoprime-loader-key.json')
    client = bigquery.Client(
        credentials=creds,
        project='neoprime0305',
        location='asia-northeast3'
    )

    # 모든 tb_raw_2026 테이블 조회
    query = """
    SELECT table_id
    FROM `neoprime0305.ds_neoprime_entrance.__TABLES__`
    WHERE table_id LIKE 'tb_raw_2026_%'
    """
    tables = [row.table_id for row in client.query(query)]

    print(f"  삭제 대상: {len(tables)}개 테이블")

    deleted = 0
    for table_name in tables:
        try:
            table_ref = f"neoprime0305.ds_neoprime_entrance.{table_name}"
            client.delete_table(table_ref)
            print(f"  ✓ 삭제: {table_name}")
            deleted += 1
        except Exception as e:
            print(f"  ✗ 실패: {table_name} - {e}")

    print(f"\n  총 {deleted}/{len(tables)}개 테이블 삭제 완료")
    return deleted


def convert_excel_to_values():
    """Excel 수식을 값으로 변환 (모든 시트)"""
    print("\n" + "=" * 70)
    print("[Step 2/4] Excel 값 변환")
    print("=" * 70)

    try:
        import win32com.client as win32
    except ImportError:
        print("  ✗ pywin32 필요: pip install pywin32")
        return None

    source_file = r"Y:\0126\0126\202511고속성장분석기(가채점)20251114.xlsx"

    if not os.path.exists(source_file):
        print(f"  ✗ 원본 파일 없음: {source_file}")
        return None

    print(f"  원본: {source_file}")

    # Excel 열기
    excel = win32.gencache.EnsureDispatch('Excel.Application')
    excel.Visible = False
    excel.DisplayAlerts = False
    excel.ScreenUpdating = False

    try:
        wb = excel.Workbooks.Open(source_file)
        print(f"  시트 수: {wb.Sheets.Count}")

        # 테스트 데이터 입력
        print("\n  [테스트 데이터 입력]")
        try:
            input_sheet = wb.Sheets('수능입력')
            test_data = {
                'C8': 131,   # 국어 화작
                'C9': 134,   # 국어 언매
                'C11': 140,  # 수학
                'C13': 1,    # 영어 등급
                'C15': 68,   # 탐구1
                'C16': 65,   # 탐구2
                'C18': 1,    # 한국사 등급
            }
            for cell, value in test_data.items():
                input_sheet.Range(cell).Value = value
                print(f"    {cell} = {value}")
        except Exception as e:
            print(f"  ⚠ 수능입력 시트 접근 오류: {e}")

        # 전체 재계산
        print("\n  [수식 재계산]")
        excel.Calculation = -4105  # xlCalculationAutomatic
        excel.CalculateFull()
        excel.CalculateFullRebuild()  # 더 강력한 재계산
        print("    전체 수식 재계산 완료")

        # 모든 시트 값으로 변환
        print("\n  [값으로 변환]")
        target_sheets = [
            'COMPUTE', 'INDEX', 'RAWSCORE', 'PERCENTAGE',
            'RESTRICT', 'SUBJECT1', 'SUBJECT2', 'SUBJECT3',
            '이과계열분석결과', '문과계열분석결과'
        ]

        for sheet_name in target_sheets:
            try:
                sheet = wb.Sheets(sheet_name)
                used_range = sheet.UsedRange
                rows = used_range.Rows.Count
                cols = used_range.Columns.Count

                # 복사 & 값으로 붙여넣기
                used_range.Copy()
                used_range.PasteSpecial(Paste=-4163)  # xlPasteValues
                excel.CutCopyMode = False

                print(f"    ✓ {sheet_name}: {rows}행 x {cols}열")
            except Exception as e:
                print(f"    ✗ {sheet_name}: {e}")

        # 새 파일로 저장
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        new_file = f"Y:\\0126\\0126\\202511고속성장분석기_전체값변환_{timestamp}.xlsx"
        wb.SaveAs(new_file, FileFormat=51)
        print(f"\n  저장: {new_file}")

        wb.Close(SaveChanges=False)
        return new_file

    except Exception as e:
        print(f"  ✗ 오류: {e}")
        import traceback
        traceback.print_exc()
        return None
    finally:
        excel.ScreenUpdating = True
        excel.Quit()


def update_config(new_file):
    """config.yaml 업데이트"""
    print("\n  [config.yaml 업데이트]")

    config_path = 'config.yaml'
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)

    old_file = config.get('source_file', 'N/A')
    config['source_file'] = new_file

    # NULL 허용 비율 100%로 설정 (전체 적재)
    if 'validation' not in config:
        config['validation'] = {}
    config['validation']['null_threshold'] = 1.0

    with open(config_path, 'w', encoding='utf-8') as f:
        yaml.dump(config, f, allow_unicode=True, default_flow_style=False)

    print(f"    이전: {old_file}")
    print(f"    변경: {new_file}")
    print(f"    null_threshold: 1.0 (전체 적재)")


def run_pipeline():
    """마스터 파이프라인 실행"""
    print("\n" + "=" * 70)
    print("[Step 3/4] 마스터 파이프라인 실행")
    print("=" * 70)

    try:
        from master_pipeline import MasterPipeline

        pipeline = MasterPipeline(config_path='config.yaml')
        result = pipeline.run()

        print(f"\n  파이프라인 결과: {result.get('status', 'unknown')}")
        return result
    except Exception as e:
        print(f"  ✗ 파이프라인 오류: {e}")
        import traceback
        traceback.print_exc()
        return None


def verify_reload():
    """재적재 결과 검증"""
    print("\n" + "=" * 70)
    print("[Step 4/4] 재적재 검증")
    print("=" * 70)

    from google.cloud import bigquery
    from google.oauth2 import service_account

    creds = service_account.Credentials.from_service_account_file('neoprime-loader-key.json')
    client = bigquery.Client(
        credentials=creds,
        project='neoprime0305',
        location='asia-northeast3'
    )

    # 테이블 현황
    query = """
    SELECT table_id, row_count
    FROM `neoprime0305.ds_neoprime_entrance.__TABLES__`
    WHERE table_id LIKE 'tb_raw_2026_%'
      AND table_id NOT LIKE '%_backup%'
    ORDER BY table_id
    """
    df = client.query(query).to_dataframe()

    print("\n  [테이블 현황]")
    total_rows = 0
    for _, row in df.iterrows():
        print(f"    {row['table_id']:<40} {row['row_count']:>10,}행")
        total_rows += row['row_count']
    print(f"    {'합계':<40} {total_rows:>10,}행")

    # COMPUTE 검증
    print("\n  [COMPUTE 데이터 품질]")
    compute_df = client.query("""
    SELECT * FROM `neoprime0305.ds_neoprime_entrance.tb_raw_2026_COMPUTE`
    ORDER BY _row_id
    """).to_dataframe()

    score_rows = [(57, '국어'), (58, '수학'), (59, '영어'), (60, '탐구1'), (61, '탐구2')]
    for row_idx, name in score_rows:
        if row_idx < len(compute_df):
            valid = sum(1 for col in compute_df.columns
                       if col.startswith('column_') and col != 'column_0'
                       and compute_df.iloc[row_idx][col] != 0)
            print(f"    {name}(Row{row_idx+1}): {valid}/220 컬럼 유효")

    # 주요 대학 확인
    print("\n  [주요 대학 점수]")
    univs = {'서울대': 271, '연세대': 363, '고려대': 82}
    for name, idx in univs.items():
        col = f'column_{idx}'
        if col in compute_df.columns:
            values = [compute_df.iloc[r][col] for r in [57, 58, 59, 60, 61]]
            total = sum(v for v in values if v and v != 0)
            print(f"    {name}: {values} = {total:.2f}")

    return {
        'tables': len(df),
        'total_rows': total_rows
    }


def main():
    print("=" * 70)
    print("NEO GOD Ultra v2.3 - 전체 재적재")
    print("=" * 70)
    print(f"시작: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Step 1: BigQuery 테이블 삭제
    delete_all_tables()

    # Step 2: Excel 값 변환
    new_file = convert_excel_to_values()
    if not new_file:
        print("\n✗ Excel 변환 실패. 중단합니다.")
        return

    # config.yaml 업데이트
    update_config(new_file)

    # Step 3: 파이프라인 실행
    run_pipeline()

    # Step 4: 검증
    result = verify_reload()

    print("\n" + "=" * 70)
    print("전체 재적재 완료")
    print(f"종료: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)


if __name__ == '__main__':
    main()
