# ============================================================
# Phase 3: Date-First 정규화 (Date-First Normalization)
# NEO GOD Ultra Framework v2.0
# ============================================================

import sys
import io
import json
import re
from typing import Any, Optional, Tuple, List, Dict
from pathlib import Path

# Windows 인코딩 설정 (안전한 방식)
if sys.platform == 'win32':
    try:
        if hasattr(sys.stdout, 'reconfigure'):
            sys.stdout.reconfigure(encoding='utf-8')
        if hasattr(sys.stderr, 'reconfigure'):
            sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

import pandas as pd
import numpy as np
import pyarrow as pa
import pyarrow.parquet as pq


class DateFirstNormalizer:
    """
    Date-First 우선순위 정규화기
    
    변환 순서:
    1. Excel 날짜 시리얼 감지 및 변환
    2. 표준 날짜 문자열 변환
    3. 숫자형 변환
    4. 문자열 정리
    """
    
    # Excel 에러 코드
    EXCEL_ERROR_CODES = {
        '#N/A', '#VALUE!', '#REF!', '#DIV/0!', '#NUM!', '#NAME?', '#NULL!'
    }
    
    # Excel 날짜 시리얼 범위 (1900-01-01 ~ 2100-12-31)
    EXCEL_SERIAL_MIN = 1       # 1900-01-01
    EXCEL_SERIAL_MAX = 73415   # 2100-12-31
    
    def normalize_column(self, series: pd.Series) -> Tuple[pd.Series, str]:
        """
        컬럼 정규화 (Date-First 우선순위)
        
        Args:
            series: 원본 시리즈
        
        Returns:
            Tuple[pd.Series, str]: (정규화된 시리즈, 추론된 타입)
        """
        # 1. Excel 에러 코드 처리
        series = self._handle_excel_errors(series)
        
        # 2. 빈 값 확인
        non_null_values = series.dropna()
        if len(non_null_values) == 0:
            return series, 'empty'
        
        # 3. Date-First: Excel 날짜 시리얼 감지 (숫자보다 먼저!)
        if self._is_excel_date_serial(series):
            converted = self._convert_excel_serial_to_date(series)
            if converted is not None:
                return converted, 'datetime_from_serial'
        
        # 4. 표준 날짜 문자열 감지
        if self._is_date_string(series):
            converted = self._convert_date_string(series)
            if converted is not None:
                return converted, 'datetime_from_string'
        
        # 5. 숫자형 변환 시도 (날짜 판단 후에!)
        if self._is_numeric(series):
            converted = pd.to_numeric(series, errors='coerce')
            if converted.notna().sum() / len(converted) > 0.8:  # 80% 이상 변환 성공
                return converted, 'numeric'
        
        # 6. 문자열 정리
        return self._clean_string(series), 'string'
    
    def _handle_excel_errors(self, series: pd.Series) -> pd.Series:
        """Excel 에러 코드를 None으로 변환"""
        return series.replace(self.EXCEL_ERROR_CODES, None)
    
    def _is_excel_date_serial(self, series: pd.Series) -> bool:
        """
        Excel 날짜 시리얼인지 감지 (보수적 판단)

        일반 점수(0-100)와 구별하기 위해 최소 임계값을 높게 설정:
        - EXCEL_SERIAL_REALISTIC_MIN = 25569 (1970-01-01)
        - EXCEL_SERIAL_REALISTIC_MAX = 55153 (2050-12-31)
        """
        non_null = series.dropna()
        if len(non_null) == 0:
            return False

        # 숫자형으로 변환 가능한지 확인
        try:
            numeric = pd.to_numeric(non_null, errors='coerce')
            valid_numeric = numeric.dropna()

            if len(valid_numeric) == 0:
                return False

            # 현실적인 날짜 범위 (1970-2050)
            REALISTIC_MIN = 25569  # 1970-01-01
            REALISTIC_MAX = 55153  # 2050-12-31

            # 90% 이상이 현실적인 날짜 범위 내에 있는지 확인
            in_range = (valid_numeric >= REALISTIC_MIN) & \
                       (valid_numeric <= REALISTIC_MAX)

            # 또한 값들의 최소값이 1000 이상이어야 함 (점수 0-100과 구별)
            if valid_numeric.min() < 1000:
                return False

            return in_range.sum() / len(valid_numeric) > 0.9
        except:
            return False
    
    def _convert_excel_serial_to_date(self, series: pd.Series) -> Optional[pd.Series]:
        """
        Excel 시리얼 번호를 datetime으로 변환
        
        Excel epoch: 1899-12-30 (Excel의 윤년 버그 보정 포함)
        """
        try:
            numeric = pd.to_numeric(series, errors='coerce')
            
            # Excel epoch 기준 변환
            converted = pd.to_datetime(
                numeric, 
                origin='1899-12-30',  # Excel epoch
                unit='D',             # 일 단위
                errors='coerce'
            )
            
            # 유효한 날짜 범위 확인 (1900-2100)
            valid_dates = converted.notna() & \
                         (converted >= '1900-01-01') & \
                         (converted <= '2100-12-31')
            
            if valid_dates.sum() / len(converted.dropna()) > 0.8:
                return converted
            return None
        except:
            return None
    
    def _is_date_string(self, series: pd.Series) -> bool:
        """날짜 문자열인지 감지"""
        non_null = series.dropna().astype(str)
        if len(non_null) == 0:
            return False
        
        # 일반적인 날짜 패턴
        date_patterns = [
            r'\d{4}-\d{2}-\d{2}',      # 2023-01-01
            r'\d{2}/\d{2}/\d{4}',      # 01/01/2023
            r'\d{4}/\d{2}/\d{2}',      # 2023/01/01
            r'\d{2}-\d{2}-\d{4}',      # 01-01-2023
        ]
        
        pattern = '|'.join(date_patterns)
        matches = non_null.str.match(pattern, na=False)
        
        return matches.sum() / len(non_null) > 0.5
    
    def _convert_date_string(self, series: pd.Series) -> Optional[pd.Series]:
        """날짜 문자열을 datetime으로 변환"""
        try:
            converted = pd.to_datetime(series, errors='coerce', infer_datetime_format=True)
            if converted.notna().sum() / len(converted) > 0.5:
                return converted
            return None
        except:
            return None
    
    def _is_numeric(self, series: pd.Series) -> bool:
        """숫자형인지 감지"""
        non_null = series.dropna()
        if len(non_null) == 0:
            return False
        
        try:
            numeric = pd.to_numeric(non_null, errors='coerce')
            return numeric.notna().sum() / len(non_null) > 0.8
        except:
            return False
    
    def _clean_string(self, series: pd.Series) -> pd.Series:
        """문자열 정리"""
        return series.astype(str).str.strip()
    
    # ========================
    # 컬럼명 정규화
    # ========================
    
    def normalize_column_names(
        self, 
        columns: list, 
        korean_mapping: dict = None
    ) -> list:
        """
        BigQuery 호환 컬럼명으로 정규화
        
        Args:
            columns: 원본 컬럼명 리스트
            korean_mapping: 한글→영어 매핑 딕셔너리 (선택)
        
        Returns:
            정규화된 컬럼명 리스트
        """
        normalized = []
        used_names = set()
        
        for i, col in enumerate(columns):
            if col is None or str(col).strip() == '':
                new_name = f'column_{i}'
            else:
                new_name = str(col)
                
                # 한글 매핑 적용
                if korean_mapping and new_name in korean_mapping:
                    new_name = korean_mapping[new_name]
                
                # BigQuery 호환 정규화
                new_name = re.sub(r'[^a-zA-Z0-9_]', '_', new_name)  # 특수문자 → _
                new_name = re.sub(r'^(\d)', r'col_\1', new_name)    # 숫자로 시작 방지
                new_name = re.sub(r'_+', '_', new_name)             # 연속 _ 제거
                new_name = new_name.strip('_').lower()
                
                if not new_name:
                    new_name = f'column_{i}'
            
            # 중복 처리
            base_name = new_name
            counter = 1
            while new_name in used_names:
                new_name = f'{base_name}_{counter}'
                counter += 1
            
            used_names.add(new_name)
            normalized.append(new_name)
        
        return normalized
    
    # ========================
    # 병합 셀 처리
    # ========================
    
    def handle_merged_cells(self, df: pd.DataFrame) -> pd.DataFrame:
        """병합 셀로 인한 NaN을 ffill로 처리"""
        for col in df.columns:
            dtype = df[col].dtype
            
            if dtype in [np.int64, np.float64]:
                df[col] = df[col].ffill().fillna(0)
            elif dtype == 'object':
                df[col] = df[col].ffill().fillna('')
            elif 'datetime' in str(dtype):
                df[col] = df[col].ffill()
        
        return df
    
    # ========================
    # 데이터 품질 리포트
    # ========================
    
    def generate_quality_report(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        데이터 품질 리포트 생성
        
        Args:
            df: 데이터프레임
        
        Returns:
            Dict: 품질 리포트
        """
        report = {
            'total_rows': len(df),
            'total_cols': len(df.columns),
            'columns': {}
        }
        
        for col in df.columns:
            null_count = df[col].isnull().sum()
            null_ratio = null_count / len(df)
            
            col_info = {
                'dtype': str(df[col].dtype),
                'null_count': int(null_count),
                'null_ratio': float(null_ratio),
                'unique_count': int(df[col].nunique()),
                'sample_values': df[col].dropna().head(5).tolist()
            }
            
            # 숫자형 통계
            if df[col].dtype in [np.int64, np.float64]:
                col_info['stats'] = {
                    'mean': float(df[col].mean()) if not df[col].isna().all() else None,
                    'std': float(df[col].std()) if not df[col].isna().all() else None,
                    'min': float(df[col].min()) if not df[col].isna().all() else None,
                    'max': float(df[col].max()) if not df[col].isna().all() else None
                }
            
            report['columns'][col] = col_info
        
        return report
    
    # ========================
    # 통합 정규화 프로세스
    # ========================
    
    def normalize_dataframe(
        self,
        df: pd.DataFrame,
        korean_mapping: dict = None,
        output_dir: str = './output',
        max_chunk_size_mb: int = 50,
        file_prefix: str = 'clean_ingestion'
    ) -> Dict[str, Any]:
        """
        데이터프레임 전체 정규화

        Args:
            df: 원본 데이터프레임
            korean_mapping: 한글 컬럼명 매핑
            output_dir: 출력 디렉토리
            max_chunk_size_mb: 최대 청크 크기 (MB)
            file_prefix: 출력 파일 접두사 (고유 식별자)

        Returns:
            Dict: 정규화 결과
        """
        self._current_file_prefix = file_prefix
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        print("[Step 1] Excel 에러 코드 처리...")
        # 에러 코드는 normalize_column에서 처리됨
        
        print("[Step 2] 병합 셀 처리 (ffill)...")
        df = self.handle_merged_cells(df)
        
        print("[Step 3] 컬럼명 정규화...")
        original_columns = df.columns.tolist()
        normalized_columns = self.normalize_column_names(original_columns, korean_mapping)
        df.columns = normalized_columns
        
        # 컬럼 매핑 저장
        column_mapping = dict(zip(original_columns, normalized_columns))
        mapping_path = output_path / 'column_mapping.json'
        with open(mapping_path, 'w', encoding='utf-8') as f:
            json.dump(column_mapping, f, ensure_ascii=False, indent=2)
        
        print("[Step 4] Date-First 타입 변환...")
        type_mapping = {}
        for col in df.columns:
            df[col], inferred_type = self.normalize_column(df[col])
            type_mapping[col] = inferred_type
        
        print("[Step 5] 데이터 품질 리포트 생성...")
        quality_report = self.generate_quality_report(df)
        quality_path = output_path / 'data_quality_report.json'
        with open(quality_path, 'w', encoding='utf-8') as f:
            json.dump(quality_report, f, ensure_ascii=False, indent=2, default=str)
        
        print("[Step 6] Parquet 파일 분할 저장...")
        chunk_files = self._save_parquet_chunks(df, output_path, max_chunk_size_mb, file_prefix)
        
        return {
            'column_mapping': str(mapping_path),
            'quality_report': str(quality_path),
            'parquet_chunks': chunk_files,
            'type_mapping': type_mapping,
            'total_rows': len(df),
            'total_cols': len(df.columns)
        }
    
    def _save_parquet_chunks(
        self,
        df: pd.DataFrame,
        output_path: Path,
        max_size_mb: int = 50,
        file_prefix: str = 'clean_ingestion'
    ) -> List[str]:
        """
        Parquet 파일을 지정된 크기 이하로 분할 저장

        Args:
            df: 데이터프레임
            output_path: 출력 디렉토리
            max_size_mb: 최대 파일 크기 (MB)
            file_prefix: 출력 파일 접두사

        Returns:
            List[str]: 생성된 파일 경로 리스트
        """
        chunk_files = []
        chunk_size = 50000  # 초기 청크 크기
        chunk_num = 0

        for i in range(0, len(df), chunk_size):
            chunk = df.iloc[i:i+chunk_size]

            # 임시 파일로 저장하여 크기 확인
            temp_path = output_path / f'temp_chunk_{file_prefix}_{chunk_num}.parquet'
            chunk.to_parquet(temp_path, index=False, compression='snappy', engine='pyarrow')

            file_size_mb = temp_path.stat().st_size / (1024 * 1024)

            if file_size_mb > max_size_mb:
                # 청크 크기 축소
                smaller_chunk_size = int(chunk_size * (max_size_mb / file_size_mb))
                chunk = df.iloc[i:i+smaller_chunk_size]
                temp_path.unlink()
                chunk.to_parquet(temp_path, index=False, compression='snappy', engine='pyarrow')

            # 최종 파일명 (고유 접두사 사용)
            final_path = output_path / f'{file_prefix}_part_{chunk_num:03d}.parquet'
            temp_path.replace(final_path)

            chunk_files.append(str(final_path))
            chunk_num += 1

        return chunk_files


if __name__ == '__main__':
    # 테스트 실행
    import argparse
    
    parser = argparse.ArgumentParser(description='Phase 3: Date-First 정규화')
    parser.add_argument('input_file', type=str, help='입력 Parquet 파일 경로')
    parser.add_argument('--output-dir', type=str, default='./output', help='출력 디렉토리')
    parser.add_argument('--max-chunk-size-mb', type=int, default=50, help='최대 청크 크기 (MB)')
    parser.add_argument('--korean-mapping', type=str, help='한글 매핑 JSON 파일 경로')
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("Phase 3: Date-First 정규화 (Date-First Normalization)")
    print("=" * 60)
    print(f"입력 파일: {args.input_file}")
    print()
    
    # 데이터 로드
    df = pd.read_parquet(args.input_file)
    
    # 한글 매핑 로드
    korean_mapping = None
    if args.korean_mapping:
        with open(args.korean_mapping, 'r', encoding='utf-8') as f:
            korean_mapping = json.load(f)
    
    # 정규화 실행
    normalizer = DateFirstNormalizer()
    result = normalizer.normalize_dataframe(
        df,
        korean_mapping=korean_mapping,
        output_dir=args.output_dir,
        max_chunk_size_mb=args.max_chunk_size_mb
    )
    
    print()
    print("정규화 결과:")
    print(json.dumps({
        'total_rows': result['total_rows'],
        'total_cols': result['total_cols'],
        'parquet_chunks': len(result['parquet_chunks'])
    }, indent=2, ensure_ascii=False))
