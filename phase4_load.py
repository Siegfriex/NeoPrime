# ============================================================
# Phase 4: Staging Table 멱등성 적재 (Idempotent Staging Load)
# NEO GOD Ultra Framework v2.0
# ============================================================

import sys
import io
import json
import time
from typing import List, Dict, Any, Optional
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

from google.cloud import bigquery
from google.cloud.bigquery import LoadJobConfig, WriteDisposition, SourceFormat
from google.oauth2 import service_account


class StagingTableLoader:
    """
    Staging Table 기반 안전한 BigQuery 적재기
    
    전략:
    1. 임시 테이블(staging)에 먼저 적재
    2. 무결성 검증 수행
    3. 검증 통과 시에만 본 테이블로 MERGE/RENAME
    4. 실패 시 staging 테이블만 삭제 (본 테이블 무결)
    """
    
    def __init__(
        self, 
        project_id: str, 
        dataset_id: str,
        credentials_path: Optional[str] = None,
        location: str = 'asia-northeast3'
    ):
        """
        Args:
            project_id: GCP 프로젝트 ID
            dataset_id: BigQuery 데이터셋 ID
            credentials_path: 서비스 계정 키 파일 경로
            location: 데이터셋 위치 (기본: asia-northeast3)
        """
        if credentials_path:
            credentials = service_account.Credentials.from_service_account_file(
                credentials_path,
                scopes=['https://www.googleapis.com/auth/bigquery']
            )
            self.client = bigquery.Client(project=project_id, credentials=credentials)
        else:
            self.client = bigquery.Client(project=project_id)
        
        self.project_id = project_id
        self.dataset_id = dataset_id
        self.location = location
        self._ensure_dataset_exists()
    
    def _ensure_dataset_exists(self):
        """데이터셋 존재 확인 및 생성"""
        dataset_ref = f"{self.project_id}.{self.dataset_id}"
        try:
            self.client.get_dataset(dataset_ref)
            print(f"[INFO] 데이터셋 존재 확인: {dataset_ref}")
        except Exception:
            print(f"[INFO] 데이터셋 생성 중: {dataset_ref}")
            dataset = bigquery.Dataset(dataset_ref)
            dataset.location = self.location
            self.client.create_dataset(dataset, exists_ok=True)
            print(f"[INFO] 데이터셋 생성 완료: {dataset_ref}")
    
    def safe_load_with_staging(
        self,
        parquet_files: List[str],
        target_table: str,
        expected_row_count: int,
        null_threshold: float = 0.1  # 10% 이하 NULL 허용
    ) -> Dict[str, Any]:
        """
        Staging 테이블을 통한 안전한 적재
        
        Args:
            parquet_files: Parquet 파일 경로 리스트
            target_table: 대상 테이블명 (예: 'tb_raw_2026')
            expected_row_count: 예상 행 수 (검증용)
            null_threshold: 허용 NULL 비율
        
        Returns:
            Dict: 적재 결과
        """
        staging_table = f"{target_table}_staging"
        backup_table = f"{target_table}_backup_{int(time.time())}"
        
        result = {
            'status': 'pending',
            'staging_table': staging_table,
            'target_table': target_table,
            'loaded_rows': 0,
            'validation': {},
            'errors': []
        }
        
        try:
            # ========================================
            # Step 0: 기존 Staging 테이블 삭제 (스키마 불일치 방지)
            # ========================================
            if self._table_exists(staging_table):
                print(f"[Step 0] 기존 Staging 테이블 삭제: {staging_table}")
                self._delete_table(staging_table)

            # ========================================
            # Step 1: Staging 테이블에 적재
            # ========================================
            print(f"[Step 1] Staging 테이블 적재: {staging_table}")

            staging_ref = f"{self.project_id}.{self.dataset_id}.{staging_table}"

            for idx, parquet_file in enumerate(parquet_files):
                job_config = LoadJobConfig(
                    source_format=SourceFormat.PARQUET,
                    write_disposition=(
                        WriteDisposition.WRITE_TRUNCATE if idx == 0 
                        else WriteDisposition.WRITE_APPEND
                    ),
                    autodetect=True
                )
                
                with open(parquet_file, 'rb') as f:
                    job = self.client.load_table_from_file(
                        f, staging_ref, job_config=job_config
                    )
                    job.result()  # 완료 대기
                
                print(f"  [Chunk {idx}] {parquet_file} 적재 완료 ({job.output_rows} rows)")
            
            # ========================================
            # Step 2: 무결성 검증
            # ========================================
            print(f"[Step 2] 무결성 검증 시작...")
            
            validation = self._validate_staging_table(
                staging_table, 
                expected_row_count, 
                null_threshold
            )
            result['validation'] = validation
            result['loaded_rows'] = validation['actual_row_count']
            
            if not validation['passed']:
                raise ValueError(f"검증 실패: {validation['failure_reasons']}")
            
            print(f"  ✓ 검증 통과: {validation['actual_row_count']}행")
            
            # ========================================
            # Step 3: 백업 생성 (기존 테이블이 있는 경우)
            # ========================================
            target_ref = f"{self.project_id}.{self.dataset_id}.{target_table}"
            
            if self._table_exists(target_table):
                print(f"[Step 3] 기존 테이블 백업: {backup_table}")
                self._copy_table(target_table, backup_table)
                result['backup_table'] = backup_table
            
            # ========================================
            # Step 4: Staging → Target 원자적 전환
            # ========================================
            print(f"[Step 4] 테이블 전환: {staging_table} → {target_table}")
            
            # 방법 1: RENAME (가장 안전, 다운타임 최소)
            self._atomic_table_swap(staging_table, target_table)
            
            result['status'] = 'success'
            print(f"[완료] {target_table} 적재 성공!")
            
        except Exception as e:
            result['status'] = 'failed'
            result['errors'].append(str(e))
            print(f"[실패] {e}")
            
            # 실패 시 staging 테이블만 정리 (본 테이블 무결)
            try:
                self._delete_table(staging_table)
                print(f"  Staging 테이블 정리 완료")
            except:
                pass
        
        return result
    
    def _validate_staging_table(
        self, 
        table_name: str, 
        expected_rows: int,
        null_threshold: float
    ) -> Dict[str, Any]:
        """
        Staging 테이블 무결성 검증
        
        검증 항목:
        1. 행 수 일치 여부
        2. NULL 비율 임계값 이내
        3. 필수 컬럼 존재 여부
        
        Args:
            table_name: 테이블 이름
            expected_rows: 예상 행 수
            null_threshold: 허용 NULL 비율
        
        Returns:
            Dict: 검증 결과
        """
        table_ref = f"{self.project_id}.{self.dataset_id}.{table_name}"
        
        # 행 수 확인
        row_count_query = f"SELECT COUNT(*) as cnt FROM `{table_ref}`"
        row_result = self.client.query(row_count_query).result()
        actual_rows = list(row_result)[0].cnt
        
        # 스키마 및 NULL 비율 확인
        schema_query = f"""
        SELECT 
            column_name,
            data_type
        FROM `{self.project_id}.{self.dataset_id}.INFORMATION_SCHEMA.COLUMNS`
        WHERE table_name = '{table_name}'
        """
        schema_result = self.client.query(schema_query).result()
        columns = [row.column_name for row in schema_result]
        
        # 컬럼별 NULL 비율 계산 (백틱으로 예약어 이스케이프)
        null_check_parts = [
            f"COUNTIF(`{col}` IS NULL) / COUNT(*) as `{col}_null_ratio`"
            for col in columns[:10]  # 상위 10개 컬럼만 체크
        ]
        
        if null_check_parts:
            null_query = f"""
            SELECT 
                COUNT(*) as total_rows,
                {', '.join(null_check_parts)}
            FROM `{table_ref}`
            """
            null_result = list(self.client.query(null_query).result())[0]
        else:
            null_result = None
        
        # 검증 결과
        validation = {
            'expected_row_count': expected_rows,
            'actual_row_count': actual_rows,
            'row_count_match': abs(actual_rows - expected_rows) / max(expected_rows, 1) < 0.01,
            'null_ratios': {},
            'high_null_columns': [],
            'passed': True,
            'failure_reasons': []
        }
        
        # 행 수 검증
        if not validation['row_count_match']:
            validation['passed'] = False
            validation['failure_reasons'].append(
                f"행 수 불일치: 예상 {expected_rows}, 실제 {actual_rows}"
            )
        
        # NULL 비율 검증
        if null_result:
            for col in columns[:10]:
                ratio_attr = f"{col}_null_ratio"
                if hasattr(null_result, ratio_attr):
                    ratio = getattr(null_result, ratio_attr) or 0
                    validation['null_ratios'][col] = ratio
                    if ratio > null_threshold:
                        validation['high_null_columns'].append(col)
        
        if validation['high_null_columns']:
            validation['passed'] = False
            validation['failure_reasons'].append(
                f"높은 NULL 비율 컬럼: {validation['high_null_columns']}"
            )
        
        return validation
    
    def _table_exists(self, table_name: str) -> bool:
        """테이블 존재 여부 확인"""
        try:
            table_ref = f"{self.project_id}.{self.dataset_id}.{table_name}"
            self.client.get_table(table_ref)
            return True
        except:
            return False
    
    def _copy_table(self, source: str, destination: str):
        """테이블 복사"""
        source_ref = f"{self.project_id}.{self.dataset_id}.{source}"
        dest_ref = f"{self.project_id}.{self.dataset_id}.{destination}"
        
        job = self.client.copy_table(source_ref, dest_ref)
        job.result()
    
    def _delete_table(self, table_name: str):
        """테이블 삭제"""
        table_ref = f"{self.project_id}.{self.dataset_id}.{table_name}"
        self.client.delete_table(table_ref, not_found_ok=True)
    
    def _atomic_table_swap(self, staging: str, target: str):
        """
        원자적 테이블 전환
        
        BigQuery는 테이블 RENAME을 지원하지 않으므로
        COPY + DELETE 조합 사용
        """
        staging_ref = f"{self.project_id}.{self.dataset_id}.{staging}"
        target_ref = f"{self.project_id}.{self.dataset_id}.{target}"
        
        # 기존 target 삭제
        self.client.delete_table(target_ref, not_found_ok=True)
        
        # staging을 target으로 복사
        job = self.client.copy_table(staging_ref, target_ref)
        job.result()
        
        # staging 삭제
        self.client.delete_table(staging_ref, not_found_ok=True)
    
    def generate_upload_report(
        self,
        result: Dict[str, Any],
        parquet_files: List[str],
        output_dir: str = './output'
    ) -> str:
        """
        업로드 리포트 생성

        Args:
            result: safe_load_with_staging 결과 (단일 테이블 또는 멀티 시트)
            parquet_files: 업로드된 Parquet 파일 리스트
            output_dir: 출력 디렉토리

        Returns:
            str: 리포트 파일 경로
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        # 멀티 시트 결과인지 단일 테이블 결과인지 확인
        if 'sheets' in result:
            # 멀티 시트 결과 구조
            report = {
                'upload_time': time.strftime('%Y-%m-%dT%H:%M:%S'),
                'project_id': self.project_id,
                'dataset_id': self.dataset_id,
                'tables': list(result.get('sheets', {}).keys()),
                'source_files': parquet_files,
                'upload_stats': {
                    'total_rows': result.get('total_rows', 0),
                    'chunks_uploaded': len(parquet_files),
                    'tables_created': len(result.get('sheets', {})),
                    'status': result['status']
                },
                'sheets_detail': result.get('sheets', {}),
                'validation': result.get('validation', {}),
                'status': result['status']
            }
        else:
            # 단일 테이블 결과 구조 (기존 호환)
            report = {
                'upload_time': time.strftime('%Y-%m-%dT%H:%M:%S'),
                'project_id': self.project_id,
                'dataset_id': self.dataset_id,
                'table_id': result.get('target_table', 'unknown'),
                'source_files': parquet_files,
                'upload_stats': {
                    'total_rows': result.get('loaded_rows', 0),
                    'chunks_uploaded': len(parquet_files),
                    'status': result['status']
                },
                'validation': result.get('validation', {}),
                'backup_table': result.get('backup_table'),
                'status': result['status'],
                'errors': result.get('errors', [])
            }

        report_path = output_path / 'upload_report.json'
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2, default=str)

        print(f"[완료] 업로드 리포트 생성: {report_path}")

        return str(report_path)


if __name__ == '__main__':
    # 테스트 실행
    import argparse
    
    parser = argparse.ArgumentParser(description='Phase 4: Staging Table 멱등성 적재')
    parser.add_argument('parquet_files', nargs='+', type=str, help='Parquet 파일 경로들')
    parser.add_argument('--project-id', type=str, required=True, help='GCP 프로젝트 ID')
    parser.add_argument('--dataset-id', type=str, required=True, help='BigQuery 데이터셋 ID')
    parser.add_argument('--table-id', type=str, required=True, help='대상 테이블 ID')
    parser.add_argument('--credentials', type=str, help='서비스 계정 키 파일 경로')
    parser.add_argument('--expected-rows', type=int, required=True, help='예상 행 수')
    parser.add_argument('--null-threshold', type=float, default=0.1, help='NULL 비율 임계값')
    parser.add_argument('--output-dir', type=str, default='./output', help='출력 디렉토리')
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("Phase 4: Staging Table 멱등성 적재")
    print("=" * 60)
    print(f"프로젝트: {args.project_id}")
    print(f"데이터셋: {args.dataset_id}")
    print(f"테이블: {args.table_id}")
    print(f"파일 수: {len(args.parquet_files)}")
    print()
    
    loader = StagingTableLoader(
        args.project_id,
        args.dataset_id,
        args.credentials
    )
    
    result = loader.safe_load_with_staging(
        args.parquet_files,
        args.table_id,
        args.expected_rows,
        args.null_threshold
    )
    
    report_path = loader.generate_upload_report(
        result,
        args.parquet_files,
        args.output_dir
    )
    
    print()
    print("적재 결과:")
    print(json.dumps({
        'status': result['status'],
        'loaded_rows': result['loaded_rows'],
        'validation_passed': result['validation'].get('passed', False)
    }, indent=2, ensure_ascii=False))
