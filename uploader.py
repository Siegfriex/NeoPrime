#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BigQuery Excel Data Uploader
20만 건의 엑셀 데이터를 GCP BigQuery entrance_exam 데이터셋에 업로드하는 스크립트

기본 인증: neoprime-admin-key.json (스크립트와 같은 디렉토리)

사용법:
    python uploader.py <엑셀파일경로> [--table 테이블명] [--project 프로젝트ID]

예시:
    python uploader.py data.xlsx --table entrance_data --project neoprime0305
"""

import os
import sys
import argparse
import logging
from pathlib import Path
from typing import Optional, List
import pandas as pd
from google.cloud import bigquery
from google.cloud.exceptions import NotFound
from google.oauth2 import service_account
import time

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('uploader.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class BigQueryUploader:
    """BigQuery 데이터 업로드 클래스"""
    
    def __init__(self, project_id: str, dataset_id: str = 'entrance_exam', 
                 credentials_path: Optional[str] = None):
        """
        초기화
        
        Args:
            project_id: GCP 프로젝트 ID
            dataset_id: BigQuery 데이터셋 ID (기본값: entrance_exam)
            credentials_path: 서비스 계정 키 파일 경로 (None이면 neoprime-admin-key.json 사용)
        """
        self.project_id = project_id
        self.dataset_id = dataset_id
        
        # 기본 서비스 계정 키 파일 경로 (스크립트와 같은 디렉토리)
        if credentials_path is None:
            script_dir = Path(__file__).parent
            default_credentials = script_dir / 'neoprime-admin-key.json'
            if default_credentials.exists():
                credentials_path = str(default_credentials)
                logger.info(f"기본 서비스 계정 키 파일 자동 감지: {credentials_path}")
        
        # 인증 설정
        if credentials_path and os.path.exists(credentials_path):
            credentials = service_account.Credentials.from_service_account_file(
                credentials_path,
                scopes=["https://www.googleapis.com/auth/bigquery"]
            )
            self.client = bigquery.Client(
                project=project_id,
                credentials=credentials
            )
            logger.info(f"서비스 계정 인증 사용: {credentials_path}")
        else:
            self.client = bigquery.Client(project=project_id)
            logger.warning("서비스 계정 키 파일을 찾을 수 없어 기본 인증을 사용합니다.")
            logger.warning("(gcloud auth application-default login 필요 또는 --credentials 옵션 사용)")
        
        # 데이터셋 확인 및 생성
        self._ensure_dataset_exists()
    
    def _ensure_dataset_exists(self):
        """데이터셋이 존재하는지 확인하고 없으면 생성"""
        dataset_ref = self.client.dataset(self.dataset_id)
        try:
            self.client.get_dataset(dataset_ref)
            logger.info(f"데이터셋 '{self.dataset_id}' 존재 확인")
        except NotFound:
            logger.info(f"데이터셋 '{self.dataset_id}' 생성 중...")
            dataset = bigquery.Dataset(dataset_ref)
            dataset.location = "asia-northeast3"  # 서울 리전
            dataset = self.client.create_dataset(dataset, exists_ok=True)
            logger.info(f"데이터셋 '{self.dataset_id}' 생성 완료")
    
    def read_excel(self, file_path: str, sheet_name: Optional[str] = None,
                   chunk_size: int = 10000) -> List[pd.DataFrame]:
        """
        엑셀 파일을 청크 단위로 읽기 (대용량 파일 처리)
        
        Args:
            file_path: 엑셀 파일 경로
            sheet_name: 시트 이름 (None이면 첫 번째 시트)
            chunk_size: 청크 크기 (행 수)
        
        Returns:
            DataFrame 리스트
        """
        logger.info(f"엑셀 파일 읽기 시작: {file_path}")
        
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"파일을 찾을 수 없습니다: {file_path}")
        
        # 파일 크기 확인
        file_size = os.path.getsize(file_path) / (1024 * 1024)  # MB
        logger.info(f"파일 크기: {file_size:.2f} MB")
        
        try:
            # 엑셀 파일 읽기
            excel_file = pd.ExcelFile(file_path)
            
            if sheet_name is None:
                sheet_name = excel_file.sheet_names[0]
                logger.info(f"시트 자동 선택: {sheet_name}")
            
            # 전체 데이터 읽기
            df = pd.read_excel(excel_file, sheet_name=sheet_name)
            total_rows = len(df)
            logger.info(f"총 행 수: {total_rows:,}개")
            
            # 청크로 분할
            chunks = []
            for i in range(0, total_rows, chunk_size):
                chunk = df.iloc[i:i + chunk_size]
                chunks.append(chunk)
                logger.info(f"청크 {len(chunks)}: {i+1:,} ~ {min(i+chunk_size, total_rows):,}행")
            
            return chunks
            
        except Exception as e:
            logger.error(f"엑셀 파일 읽기 실패: {str(e)}")
            raise
    
    def infer_schema(self, df: pd.DataFrame) -> List[bigquery.SchemaField]:
        """
        DataFrame에서 BigQuery 스키마 추론
        
        Args:
            df: DataFrame
        
        Returns:
            BigQuery 스키마 필드 리스트
        """
        schema = []
        
        for col_name, dtype in df.dtypes.items():
            # Pandas 타입을 BigQuery 타입으로 변환
            if pd.api.types.is_integer_dtype(dtype):
                bq_type = 'INTEGER'
            elif pd.api.types.is_float_dtype(dtype):
                bq_type = 'FLOAT'
            elif pd.api.types.is_bool_dtype(dtype):
                bq_type = 'BOOLEAN'
            elif pd.api.types.is_datetime64_any_dtype(dtype):
                bq_type = 'TIMESTAMP'
            else:
                bq_type = 'STRING'
            
            # 필드 모드 결정 (NULL 값이 있으면 NULLABLE)
            mode = 'NULLABLE' if df[col_name].isna().any() else 'REQUIRED'
            
            schema.append(bigquery.SchemaField(
                name=str(col_name),
                field_type=bq_type,
                mode=mode
            ))
        
        return schema
    
    def create_table_if_not_exists(self, table_id: str, schema: List[bigquery.SchemaField],
                                   write_disposition: str = 'WRITE_APPEND'):
        """
        테이블이 없으면 생성, 있으면 스키마 확인
        
        Args:
            table_id: 테이블 ID
            schema: BigQuery 스키마
            write_disposition: 쓰기 모드 (WRITE_APPEND, WRITE_TRUNCATE, WRITE_EMPTY)
        """
        table_ref = self.client.dataset(self.dataset_id).table(table_id)
        
        try:
            table = self.client.get_table(table_ref)
            logger.info(f"테이블 '{table_id}' 존재 확인 (행 수: {table.num_rows:,})")
            
            if write_disposition == 'WRITE_TRUNCATE':
                logger.warning(f"WRITE_TRUNCATE 모드: 기존 데이터가 삭제됩니다!")
                
        except NotFound:
            logger.info(f"테이블 '{table_id}' 생성 중...")
            table = bigquery.Table(table_ref, schema=schema)
            table = self.client.create_table(table)
            logger.info(f"테이블 '{table_id}' 생성 완료")
    
    def upload_dataframe(self, df: pd.DataFrame, table_id: str,
                        write_disposition: str = 'WRITE_APPEND') -> int:
        """
        DataFrame을 BigQuery에 업로드
        
        Args:
            df: 업로드할 DataFrame
            table_id: 테이블 ID
            write_disposition: 쓰기 모드
        
        Returns:
            업로드된 행 수
        """
        table_ref = self.client.dataset(self.dataset_id).table(table_id)
        
        # 스키마 추론
        schema = self.infer_schema(df)
        
        # 테이블 생성/확인
        self.create_table_if_not_exists(table_id, schema, write_disposition)
        
        # 데이터 타입 변환 (BigQuery 호환성)
        df_clean = df.copy()
        
        # NaN 값을 None으로 변환
        df_clean = df_clean.where(pd.notnull(df_clean), None)
        
        # 업로드 설정
        job_config = bigquery.LoadJobConfig(
            schema=schema,
            write_disposition=write_disposition,
            source_format=bigquery.SourceFormat.PARQUET,  # Parquet 형식 사용 (더 빠름)
        )
        
        # Parquet 형식으로 변환 후 업로드
        logger.info(f"데이터 업로드 시작: {len(df_clean):,}행")
        start_time = time.time()
        
        try:
            # 임시 Parquet 파일로 저장
            temp_parquet = f"temp_{table_id}_{int(time.time())}.parquet"
            df_clean.to_parquet(temp_parquet, index=False, engine='pyarrow')
            
            # BigQuery에 업로드
            with open(temp_parquet, 'rb') as source_file:
                job = self.client.load_table_from_file(
                    source_file,
                    table_ref,
                    job_config=job_config
                )
            
            # 작업 완료 대기
            job.result()
            
            # 임시 파일 삭제
            os.remove(temp_parquet)
            
            elapsed_time = time.time() - start_time
            logger.info(f"업로드 완료: {len(df_clean):,}행 ({elapsed_time:.2f}초)")
            
            return len(df_clean)
            
        except Exception as e:
            # 에러 발생 시 임시 파일 정리
            if os.path.exists(temp_parquet):
                os.remove(temp_parquet)
            logger.error(f"업로드 실패: {str(e)}")
            raise
    
    def upload_excel(self, excel_path: str, table_id: str,
                    sheet_name: Optional[str] = None,
                    write_disposition: str = 'WRITE_APPEND',
                    chunk_size: int = 10000) -> int:
        """
        엑셀 파일을 BigQuery에 업로드 (전체 프로세스)
        
        Args:
            excel_path: 엑셀 파일 경로
            table_id: 테이블 ID
            sheet_name: 시트 이름
            write_disposition: 쓰기 모드
            chunk_size: 청크 크기
        
        Returns:
            총 업로드된 행 수
        """
        logger.info("=" * 60)
        logger.info("BigQuery 엑셀 데이터 업로드 시작")
        logger.info("=" * 60)
        logger.info(f"프로젝트: {self.project_id}")
        logger.info(f"데이터셋: {self.dataset_id}")
        logger.info(f"테이블: {table_id}")
        logger.info(f"엑셀 파일: {excel_path}")
        logger.info("=" * 60)
        
        total_uploaded = 0
        
        try:
            # 엑셀 파일 읽기
            chunks = self.read_excel(excel_path, sheet_name, chunk_size)
            
            # 첫 번째 청크로 스키마 추론 및 테이블 생성
            if chunks:
                schema = self.infer_schema(chunks[0])
                self.create_table_if_not_exists(table_id, schema, write_disposition)
                
                # 각 청크 업로드
                for i, chunk in enumerate(chunks, 1):
                    logger.info(f"\n[청크 {i}/{len(chunks)}] 처리 중...")
                    
                    # 첫 번째 청크는 지정된 write_disposition 사용
                    # 이후 청크는 항상 APPEND
                    current_disposition = write_disposition if i == 1 else 'WRITE_APPEND'
                    
                    uploaded = self.upload_dataframe(chunk, table_id, current_disposition)
                    total_uploaded += uploaded
                    
                    logger.info(f"진행률: {total_uploaded:,}행 업로드 완료")
            
            logger.info("=" * 60)
            logger.info(f"전체 업로드 완료: 총 {total_uploaded:,}행")
            logger.info("=" * 60)
            
            return total_uploaded
            
        except Exception as e:
            logger.error(f"업로드 프로세스 실패: {str(e)}")
            raise


def main():
    """메인 함수"""
    parser = argparse.ArgumentParser(
        description='엑셀 데이터를 BigQuery에 업로드',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
예시:
  # 기본 사용 (neoprime-admin-key.json 자동 사용)
  python uploader.py data.xlsx --table entrance_data --project neoprime0305
  
  # 특정 시트 지정
  python uploader.py data.xlsx --table entrance_data --project neoprime0305 --sheet "Sheet1"
  
  # 기존 테이블 덮어쓰기
  python uploader.py data.xlsx --table entrance_data --project neoprime0305 --mode truncate
  
  # 다른 서비스 계정 키 사용 (기본값 무시)
  python uploader.py data.xlsx --table entrance_data --project neoprime0305 --credentials other-key.json
        """
    )
    
    parser.add_argument('excel_file', help='업로드할 엑셀 파일 경로')
    parser.add_argument('--project', default='neoprime0305',
                       help='GCP 프로젝트 ID (기본값: neoprime0305)')
    parser.add_argument('--dataset', default='entrance_exam',
                       help='BigQuery 데이터셋 ID (기본값: entrance_exam)')
    parser.add_argument('--table', required=True,
                       help='BigQuery 테이블 ID (필수)')
    parser.add_argument('--sheet', default=None,
                       help='엑셀 시트 이름 (기본값: 첫 번째 시트)')
    parser.add_argument('--mode', choices=['append', 'truncate', 'empty'],
                       default='append',
                       help='쓰기 모드: append(추가), truncate(덮어쓰기), empty(비어있을 때만)')
    parser.add_argument('--credentials', default=None,
                       help='서비스 계정 키 파일 경로 (기본값: neoprime-admin-key.json 자동 사용)')
    parser.add_argument('--chunk-size', type=int, default=10000,
                       help='청크 크기 (기본값: 10000)')
    
    args = parser.parse_args()
    
    # 쓰기 모드 변환
    mode_map = {
        'append': 'WRITE_APPEND',
        'truncate': 'WRITE_TRUNCATE',
        'empty': 'WRITE_EMPTY'
    }
    write_disposition = mode_map[args.mode]
    
    try:
        # 업로더 생성
        uploader = BigQueryUploader(
            project_id=args.project,
            dataset_id=args.dataset,
            credentials_path=args.credentials
        )
        
        # 업로드 실행
        total_rows = uploader.upload_excel(
            excel_path=args.excel_file,
            table_id=args.table,
            sheet_name=args.sheet,
            write_disposition=write_disposition,
            chunk_size=args.chunk_size
        )
        
        logger.info(f"\n✅ 성공: {total_rows:,}행이 '{args.dataset}.{args.table}' 테이블에 업로드되었습니다.")
        sys.exit(0)
        
    except KeyboardInterrupt:
        logger.warning("\n⚠️ 사용자에 의해 중단되었습니다.")
        sys.exit(1)
    except Exception as e:
        logger.error(f"\n❌ 오류 발생: {str(e)}")
        sys.exit(1)


if __name__ == '__main__':
    main()
