# ============================================================
# BigQuery 스키마 호환성 검증 스크립트
# NEO GOD 엔진 리버스 엔지니어링 지원
# ============================================================

import sys
import json
from pathlib import Path
from typing import Dict, List, Any
import pandas as pd

# Windows 인코딩 설정
if sys.platform == 'win32':
    try:
        if hasattr(sys.stdout, 'reconfigure'):
            sys.stdout.reconfigure(encoding='utf-8')
        if hasattr(sys.stderr, 'reconfigure'):
            sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass


def check_bigquery_type_compatibility(dtype: str, sample_values: List[Any]) -> Dict[str, Any]:
    """BigQuery 타입 호환성 검증"""
    issues = []
    warnings = []
    
    # Pandas dtype → BigQuery 타입 매핑
    dtype_mapping = {
        'int64': 'INTEGER',
        'float64': 'FLOAT',
        'bool': 'BOOLEAN',
        'object': 'STRING',  # str 포함
        'string': 'STRING',
        'datetime64[ns]': 'TIMESTAMP',
        'date': 'DATE'
    }
    
    bq_type = dtype_mapping.get(dtype, 'STRING')
    
    # 타입별 검증
    if dtype == 'float64':
        # NaN 값 확인
        nan_count = sum(1 for v in sample_values if pd.isna(v))
        if nan_count > 0:
            warnings.append(f"NaN 값 {nan_count}개 발견 - BigQuery에서는 NULL로 처리됨")
        
        # 무한대 값 확인
        inf_count = sum(1 for v in sample_values if isinstance(v, float) and (v == float('inf') or v == float('-inf')))
        if inf_count > 0:
            issues.append(f"무한대 값 {inf_count}개 발견 - BigQuery에서 오류 발생 가능")
    
    elif dtype == 'object' or dtype == 'string':
        # 문자열 길이 확인
        max_length = max((len(str(v)) for v in sample_values if v is not None), default=0)
        if max_length > 262144:  # BigQuery STRING 최대 길이 (2MB)
            issues.append(f"최대 문자열 길이 {max_length} - BigQuery STRING 제한 초과")
        elif max_length > 8192:  # 권장 길이
            warnings.append(f"최대 문자열 길이 {max_length} - BigQuery 성능 저하 가능")
        
        # 숫자로 변환 가능한 문자열 확인
        numeric_strings = []
        for v in sample_values:
            if v is not None and isinstance(v, str):
                try:
                    float(v)
                    numeric_strings.append(v)
                except ValueError:
                    pass
        
        if len(numeric_strings) > len(sample_values) * 0.5:
            warnings.append(f"숫자로 변환 가능한 문자열 {len(numeric_strings)}개 - 타입 변환 필요 가능")
    
    elif dtype == 'int64':
        # 범위 확인
        valid_ints = [v for v in sample_values if v is not None]
        if valid_ints:
            min_val = min(valid_ints)
            max_val = max(valid_ints)
            if min_val < -9223372036854775808 or max_val > 9223372036854775807:
                issues.append(f"정수 범위 초과: {min_val} ~ {max_val}")
    
    return {
        'bigquery_type': bq_type,
        'issues': issues,
        'warnings': warnings,
        'compatible': len(issues) == 0
    }


def verify_sheet_compatibility(sheet_name: str, samples: Dict[str, Any]) -> Dict[str, Any]:
    """시트별 BigQuery 호환성 검증"""
    column_info = samples.get('column_info', {})
    
    results = {}
    total_issues = 0
    total_warnings = 0
    
    for col_name, col_info in column_info.items():
        dtype = col_info.get('dtype', 'unknown')
        sample_values = col_info.get('sample_values', [])
        
        compatibility = check_bigquery_type_compatibility(dtype, sample_values)
        
        results[col_name] = {
            'pandas_dtype': dtype,
            'bigquery_type': compatibility['bigquery_type'],
            'issues': compatibility['issues'],
            'warnings': compatibility['warnings'],
            'compatible': compatibility['compatible']
        }
        
        total_issues += len(compatibility['issues'])
        total_warnings += len(compatibility['warnings'])
    
    return {
        'sheet_name': sheet_name,
        'total_columns': len(column_info),
        'columns': results,
        'total_issues': total_issues,
        'total_warnings': total_warnings,
        'overall_compatible': total_issues == 0
    }


def generate_compatibility_report(output_dir: str = './output') -> str:
    """BigQuery 호환성 리포트 생성"""
    output_path = Path(output_dir)
    
    # 데이터 샘플 리포트 로드
    samples_path = output_path / 'data_samples_report.json'
    if not samples_path.exists():
        print(f"[오류] 데이터 샘플 리포트 없음: {samples_path}")
        return ""
    
    with open(samples_path, 'r', encoding='utf-8') as f:
        samples_data = json.load(f)
    
    # 주요 시트 검증
    target_sheets = ['INDEX', 'RAWSCORE', '이과계열분석결과', '문과계열분석결과']
    
    report = {
        'verification_date': pd.Timestamp.now().isoformat(),
        'sheets': {},
        'summary': {
            'total_sheets': 0,
            'compatible_sheets': 0,
            'total_issues': 0,
            'total_warnings': 0
        }
    }
    
    for sheet_name in target_sheets:
        if sheet_name not in samples_data:
            continue
        
        sheet_samples = samples_data[sheet_name]
        verification = verify_sheet_compatibility(sheet_name, sheet_samples)
        
        report['sheets'][sheet_name] = verification
        report['summary']['total_sheets'] += 1
        report['summary']['total_issues'] += verification['total_issues']
        report['summary']['total_warnings'] += verification['total_warnings']
        
        if verification['overall_compatible']:
            report['summary']['compatible_sheets'] += 1
    
    # 리포트 저장
    report_path = output_path / 'bigquery_compatibility_report.json'
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2, default=str)
    
    print(f"[완료] BigQuery 호환성 리포트 생성: {report_path}")
    
    # 요약 출력
    print()
    print("=" * 60)
    print("BigQuery 호환성 검증 요약")
    print("=" * 60)
    print(f"검증 시트: {report['summary']['total_sheets']}개")
    print(f"호환 가능: {report['summary']['compatible_sheets']}개")
    print(f"이슈: {report['summary']['total_issues']}개")
    print(f"경고: {report['summary']['total_warnings']}개")
    
    # 이슈 상세 출력
    if report['summary']['total_issues'] > 0:
        print()
        print("주요 이슈:")
        for sheet_name, sheet_data in report['sheets'].items():
            for col_name, col_data in sheet_data['columns'].items():
                if col_data['issues']:
                    print(f"  [{sheet_name}.{col_name}]: {', '.join(col_data['issues'])}")
    
    return str(report_path)


if __name__ == '__main__':
    print("=" * 60)
    print("BigQuery 스키마 호환성 검증")
    print("=" * 60)
    print()
    
    report_path = generate_compatibility_report()
    
    if report_path:
        print()
        print("검증 완료!")
