# ============================================================
# 데이터 샘플 추출 스크립트
# NEO GOD 엔진 리버스 엔지니어링 지원
# ============================================================

import sys
import io
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


def extract_sample_data(output_dir: str = './output', sample_rows: int = 5) -> Dict[str, Any]:
    """주요 시트의 샘플 데이터 추출"""
    output_path = Path(output_dir)
    
    samples = {}
    
    # 주요 시트 목록
    target_sheets = [
        'INDEX',
        'RAWSCORE',
        '이과계열분석결과',
        '문과계열분석결과',
        'SUBJECT1',
        'SUBJECT3'
    ]
    
    for sheet_name in target_sheets:
        chunk_file = output_path / f'{sheet_name}_chunk_0000.parquet'
        
        if not chunk_file.exists():
            print(f"[SKIP] {sheet_name}: 청크 파일 없음")
            continue
        
        try:
            df = pd.read_parquet(chunk_file)
            
            # 샘플 데이터 추출
            sample_df = df.head(sample_rows)
            
            # 컬럼 정보
            column_info = {}
            for col in df.columns:
                dtype = str(df[col].dtype)
                non_null = df[col].dropna()
                
                col_info = {
                    'dtype': dtype,
                    'null_count': int(df[col].isnull().sum()),
                    'null_ratio': float(df[col].isnull().sum() / len(df)),
                    'unique_count': int(df[col].nunique()),
                    'sample_values': sample_df[col].head(3).tolist() if len(sample_df) > 0 else []
                }
                
                # 숫자형 통계
                if dtype in ['int64', 'float64']:
                    if len(non_null) > 0:
                        col_info['stats'] = {
                            'min': float(non_null.min()),
                            'max': float(non_null.max()),
                            'mean': float(non_null.mean()) if dtype == 'float64' else None
                        }
                
                column_info[col] = col_info
            
            samples[sheet_name] = {
                'total_rows': len(df),
                'total_columns': len(df.columns),
                'columns': list(df.columns),
                'column_info': column_info,
                'sample_data': sample_df.to_dict('records') if len(sample_df) > 0 else []
            }
            
            print(f"[완료] {sheet_name}: {len(df)}행, {len(df.columns)}컬럼")
            
        except Exception as e:
            print(f"[오류] {sheet_name}: {e}")
            samples[sheet_name] = {'error': str(e)}
    
    return samples


def generate_sample_report(output_dir: str = './output') -> str:
    """샘플 데이터 리포트 생성"""
    output_path = Path(output_dir)
    
    samples = extract_sample_data(str(output_path))
    
    # 리포트 저장
    report_path = output_path / 'data_samples_report.json'
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(samples, f, ensure_ascii=False, indent=2, default=str)
    
    print(f"[완료] 샘플 데이터 리포트 생성: {report_path}")
    
    return str(report_path)


if __name__ == '__main__':
    print("=" * 60)
    print("데이터 샘플 추출")
    print("=" * 60)
    print()
    
    report_path = generate_sample_report()
    
    print()
    print("추출 완료!")
