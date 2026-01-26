# ============================================================
# 실제 점수 계산 테스트
# NEO GOD Ultra Framework v2.3
# ============================================================
"""
BigQuery COMPUTE 테이블에서 데이터를 가져와
대학별 환산점수를 계산합니다.
"""

import sys
from pathlib import Path
from google.cloud import bigquery
from google.oauth2 import service_account
import pandas as pd

# 출력 디렉토리를 path에 추가
sys.path.insert(0, str(Path(__file__).parent / 'output'))


def load_compute_data():
    """BigQuery에서 COMPUTE 테이블 로드"""
    creds_path = "neoprime-loader-key.json"
    project_id = "neoprime0305"
    dataset_id = "ds_neoprime_entrance"

    credentials = service_account.Credentials.from_service_account_file(creds_path)
    client = bigquery.Client(
        credentials=credentials,
        project=project_id,
        location="asia-northeast3"
    )

    # COMPUTE 테이블 전체 로드
    query = f"""
    SELECT *
    FROM `{project_id}.{dataset_id}.tb_raw_2026_COMPUTE`
    ORDER BY _row_id
    """

    print("BigQuery에서 COMPUTE 테이블 로드 중...")
    df = client.query(query).to_dataframe()
    print(f"  - 로드 완료: {len(df)}행 x {len(df.columns)}열")

    return df


def convert_to_row_dict(df: pd.DataFrame, row_index: int) -> dict:
    """
    DataFrame의 특정 행을 엔진에서 사용할 수 있는 dict로 변환

    BigQuery 컬럼명 (column_0, column_1, ...) → Excel 컬럼 참조 (F58, F59, ...)
    """
    row_dict = {}

    # column_N → Excel 컬럼 문자로 변환 (0=A, 1=B, ..., 25=Z, 26=AA, ...)
    def idx_to_col(idx):
        result = ""
        while idx >= 0:
            result = chr(idx % 26 + ord('A')) + result
            idx = idx // 26 - 1
        return result

    # 각 컬럼을 Excel 참조 형식으로 변환
    for col in df.columns:
        if col.startswith('column_'):
            try:
                col_idx = int(col.replace('column_', ''))
                excel_col = idx_to_col(col_idx)
                # 행 번호는 row_index + 1 (Excel은 1부터 시작)
                # COMPUTE 테이블의 구조: 행 58~70이 점수 데이터
                # BigQuery row_index 0 = Excel row 1
                # 하지만 COMPUTE 테이블은 row 58부터 시작
                for excel_row in range(1, 72):  # 1~71행
                    row_dict[f'{excel_col}{excel_row}'] = None

                # 실제 값은 해당 row_index의 값
                # Excel row = row_index + 1 (헤더 제외)
                excel_row = row_index + 1
                row_dict[f'{excel_col}{excel_row}'] = df.iloc[row_index][col]
            except:
                pass

    return row_dict


def create_compute_dict(df: pd.DataFrame) -> dict:
    """
    전체 COMPUTE DataFrame을 Excel 셀 참조 dict로 변환
    row_dict['F58'] = COMPUTE의 F열, 58행 값
    """
    row_dict = {}

    def idx_to_col(idx):
        """0=A, 1=B, ..., 25=Z, 26=AA, ..."""
        result = ""
        idx_copy = idx
        while idx_copy >= 0:
            result = chr(idx_copy % 26 + ord('A')) + result
            idx_copy = idx_copy // 26 - 1
        return result

    # COMPUTE 테이블 구조: 70행, 563개 컬럼
    # 행 번호는 1부터 (Excel 기준), 하지만 헤더 포함 여부에 따라 조정 필요
    # 실제 데이터는 row 58부터 점수 데이터가 있음

    for col in df.columns:
        if col.startswith('column_'):
            try:
                col_idx = int(col.replace('column_', ''))
                excel_col = idx_to_col(col_idx)

                # 각 행에 대해 셀 참조 생성
                for row_idx in range(len(df)):
                    # BigQuery row 0 = Excel row 1 (헤더 제외 시)
                    # 하지만 원본 Excel에서 COMPUTE는 헤더 포함 70행
                    # 실제 점수는 row 58~70에 위치
                    excel_row = row_idx + 1  # 1-indexed
                    cell_ref = f'{excel_col}{excel_row}'
                    value = df.iloc[row_idx][col]
                    row_dict[cell_ref] = value
            except:
                pass

    return row_dict


def calculate_scores_manual(compute_dict: dict):
    """
    주요 대학 환산점수 수동 계산
    원본 수식 기반으로 직접 계산
    """
    results = {}

    # 대학별 수식 정의 (원본 엔진에서 추출)
    universities = {
        '가천대': ('F', '=F$58+F$59+F$60+F$61+F$62'),
        '가톨릭대': ('J', '=J$58+J$59+J$60+J$61+J$62'),
        '건국대': ('N', '=N$58+N$59+N$60+N$61+N$62'),
        '경희대': ('V', '=V$58+V$59+V$60+V$61+V$62'),
        '고려대': ('CE', '=CE$58+CE$59+CE$60+CE$61+CE$62'),
        '서울대': ('JL', '=JL$58+JL$59+JL$60+JL$61+JL$62'),
        '성균관대': ('KP', '=KP$58+KP$59+KP$60+KP$61+KP$62'),
        '연세대': ('MZ', '=MZ$58+MZ$59+MZ$60+MZ$61+MZ$62'),
        '이화여대': ('OF', '=OF$58+OF$59+OF$60+OF$61+OF$62'),
        '중앙대': ('PV', '=PV$58+PV$59+PV$60+PV$61+PV$62'),
        '한양대': ('SN', '=SN$58+SN$59+SN$60+SN$61+SN$62'),
    }

    for univ_name, (col, formula) in universities.items():
        try:
            # 점수 영역: 국어(58), 수학(59), 영어(60), 탐구1(61), 탐구2(62)
            scores = []
            for row in [58, 59, 60, 61, 62]:
                cell = f'{col}{row}'
                value = compute_dict.get(cell)
                if value is not None and not pd.isna(value):
                    try:
                        scores.append(float(value))
                    except:
                        scores.append(0)
                else:
                    scores.append(0)

            total = sum(scores)
            results[univ_name] = {
                'column': col,
                'scores': {
                    '국어': scores[0],
                    '수학': scores[1],
                    '영어': scores[2],
                    '탐구1': scores[3],
                    '탐구2': scores[4],
                },
                'total': total
            }
        except Exception as e:
            results[univ_name] = {'error': str(e)}

    return results


def main():
    print("=" * 70)
    print("NEO GOD Ultra v2.3 - 실제 점수 계산 테스트")
    print("=" * 70)

    # 1. COMPUTE 데이터 로드
    df = load_compute_data()

    # 2. 데이터 구조 분석
    print("\n" + "-" * 70)
    print("[데이터 구조 분석]")
    print("-" * 70)
    print(f"  - 행 수: {len(df)}")
    print(f"  - 열 수: {len(df.columns)}")

    # 주요 컬럼 확인 (column_271 = JL = 서울대)
    key_columns = {
        'column_5': 'F (가천대)',
        'column_9': 'J (가톨릭대)',
        'column_82': 'CE (고려대)',
        'column_271': 'JL (서울대)',
        'column_363': 'MZ (연세대)',
    }

    print("\n  [주요 컬럼 샘플 (row 57-61 = Excel row 58-62)]")
    for col, name in key_columns.items():
        if col in df.columns:
            values = df[col].iloc[57:62].tolist()
            print(f"    {name}: {values}")

    # 3. Excel 셀 참조 dict 생성
    print("\n" + "-" * 70)
    print("[Excel 셀 참조 변환]")
    print("-" * 70)

    compute_dict = create_compute_dict(df)
    print(f"  - 총 셀 참조 수: {len(compute_dict):,}")

    # 샘플 확인
    sample_cells = ['F58', 'F59', 'JL58', 'JL59', 'MZ58', 'MZ59']
    print(f"\n  [샘플 셀 값]")
    for cell in sample_cells:
        value = compute_dict.get(cell, 'N/A')
        print(f"    {cell}: {value}")

    # 4. 대학별 환산점수 계산
    print("\n" + "-" * 70)
    print("[대학별 환산점수 계산]")
    print("-" * 70)

    results = calculate_scores_manual(compute_dict)

    # 결과 출력
    print("\n  {:<12} {:>10} {:>10} {:>10} {:>10} {:>10} {:>12}".format(
        '대학명', '국어', '수학', '영어', '탐구1', '탐구2', '총점'
    ))
    print("  " + "-" * 76)

    for univ, data in sorted(results.items()):
        if 'error' in data:
            print(f"  {univ:<12} 오류: {data['error']}")
        else:
            scores = data['scores']
            print("  {:<12} {:>10.2f} {:>10.2f} {:>10.2f} {:>10.2f} {:>10.2f} {:>12.2f}".format(
                univ,
                scores['국어'],
                scores['수학'],
                scores['영어'],
                scores['탐구1'],
                scores['탐구2'],
                data['total']
            ))

    # 5. 입력 데이터 확인
    print("\n" + "-" * 70)
    print("[테스트 입력 데이터 (참고)]")
    print("-" * 70)
    print("  - 국어 화작: 131점 (표준점수)")
    print("  - 국어 언매: 134점 (표준점수)")
    print("  - 수학: 140점 (표준점수)")
    print("  - 영어: 1등급")
    print("  - 탐구1: 68점 (표준점수)")
    print("  - 탐구2: 65점 (표준점수)")
    print("  - 한국사: 1등급")

    print("\n" + "=" * 70)
    print("점수 계산 완료")
    print("=" * 70)

    return results


if __name__ == '__main__':
    main()
