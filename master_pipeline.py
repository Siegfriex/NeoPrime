# ============================================================
# Master Pipeline: NEO GOD Ultra Framework v2.0
# 통합 실행, 에러 처리, 리포트
# ============================================================

import sys
import io
import yaml
import json
import logging
import time
from pathlib import Path
from typing import Dict, Any
from functools import wraps

# Windows 인코딩 설정 (안전한 방식)
if sys.platform == 'win32':
    try:
        if hasattr(sys.stdout, 'reconfigure'):
            sys.stdout.reconfigure(encoding='utf-8')
        if hasattr(sys.stderr, 'reconfigure'):
            sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler('pipeline.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def retry_on_failure(max_retries=3, delay=5):
    """재시도 데코레이터"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_retries - 1:
                        raise
                    logger.warning(f"시도 {attempt+1} 실패, {delay}초 후 재시도: {str(e)}")
                    time.sleep(delay)
        return wrapper
    return decorator


class NeoGodUltraPipeline:
    """NEO GOD Ultra 파이프라인 v2.0"""
    
    def __init__(self, config_path: str):
        """
        Args:
            config_path: 설정 파일 경로 (YAML)
        """
        self.config = self._load_config(config_path)
        self.results = {}
        self.start_time = None
        self.output_dir = Path(self.config.get('output', {}).get('directory', './output'))
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def _load_config(self, path: str) -> Dict[str, Any]:
        """설정 파일 로드"""
        with open(path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    @retry_on_failure(max_retries=3, delay=5)
    def execute(self) -> Dict[str, Any]:
        """전체 파이프라인 실행"""
        self.start_time = time.perf_counter()
        logger.info("=" * 60)
        logger.info("NEO GOD Ultra Pipeline v2.0 시작")
        logger.info("=" * 60)
        
        try:
            # Phase 1: 고속 정찰 (Calamine)
            logger.info("[Phase 1] 고속 정찰 시작...")
            from phase1_scouting import scout_with_fallback, generate_scouting_report
            self.results['phase1'] = scout_with_fallback(self.config['source_file'])
            generate_scouting_report(self.results['phase1'], str(self.output_dir))
            
            # 모든 시트 적재 (메모장 제외)
            target_sheets = [
                s['name'] for s in self.results['phase1']['sheets']
                if s['has_data'] and s['name'] != '메모장'
            ]
            logger.info(f"타겟 시트 식별: {len(target_sheets)}개")
            
            # Phase 2: 물리적 이원화 추출
            logger.info("[Phase 2] 물리적 이원화 추출 시작...")
            from phase2_extraction import PhysicalDualTrackExtractor
            
            extractor = PhysicalDualTrackExtractor(
                self.config['source_file'], 
                str(self.output_dir)
            )
            
            self.results['phase2'] = []
            all_value_chunks = []
            
            for sheet in target_sheets:
                logger.info(f"시트 추출 중: {sheet}")
                result = extractor.run_dual_track_extraction(
                    sheet, 
                    chunk_size=self.config['processing']['chunk_size'],
                    formula_sample_rows=self.config['processing']['formula_sample_rows']
                )
                self.results['phase2'].append(result)
                all_value_chunks.extend(result['value_chunks'])
            
            logger.info(f"Phase 2 완료: 총 {len(all_value_chunks)}개 청크 생성")
            
            # Phase 3: Date-First 정규화
            logger.info("[Phase 3] Date-First 정규화 시작...")
            from phase3_normalization import DateFirstNormalizer
            
            normalizer = DateFirstNormalizer()
            
            # 한글 매핑 로드
            korean_mapping = None
            mapping_file = self.config.get('column_mapping', {}).get('file')
            if mapping_file and Path(mapping_file).exists():
                with open(mapping_file, 'r', encoding='utf-8') as f:
                    korean_mapping = json.load(f)
            
            # 각 청크 파일 정규화
            self.results['phase3'] = []
            all_normalized_chunks = []
            import pandas as pd

            # 메타데이터 설정 (v2.3)
            metadata_cfg = self.config.get('metadata', {})
            add_system_cols = metadata_cfg.get('add_system_columns', False)
            source_fname = metadata_cfg.get('source_filename', None)

            for idx, chunk_file in enumerate(all_value_chunks):
                logger.info(f"청크 정규화 중: {chunk_file}")
                df = pd.read_parquet(chunk_file)

                # 원본 청크 파일명에서 고유 접두사 생성
                chunk_basename = Path(chunk_file).stem  # 예: INDEX_chunk_0000
                file_prefix = f'normalized_{chunk_basename}'

                result = normalizer.normalize_dataframe(
                    df,
                    korean_mapping=korean_mapping,
                    output_dir=str(self.output_dir),
                    max_chunk_size_mb=self.config['processing']['max_parquet_size_mb'],
                    file_prefix=file_prefix,
                    chunk_index=idx,
                    chunk_size=self.config['processing']['chunk_size'],
                    source_filename=source_fname,
                    add_system_columns=add_system_cols
                )
                self.results['phase3'].append(result)
                all_normalized_chunks.extend(result['parquet_chunks'])

            logger.info(f"Phase 3 완료: 총 {len(all_normalized_chunks)}개 정규화 청크 생성")

            # Phase 3.5: 기존 테이블 마이그레이션 (v2.3)
            if add_system_cols:
                logger.info("[Phase 3.5] 기존 테이블 마이그레이션...")
                self._migrate_existing_tables()

            # Phase 4: Staging Table 멱등성 적재 (시트별 테이블 분리)
            logger.info("[Phase 4] Staging Table 적재 시작...")
            from phase4_load import StagingTableLoader

            loader = StagingTableLoader(
                self.config['bigquery']['project_id'],
                self.config['bigquery']['dataset_id'],
                self.config['bigquery']['credentials_path'],
                self.config['bigquery'].get('location', 'asia-northeast3')
            )

            # 시트별로 청크 그룹화 (스키마가 다르므로 별도 테이블에 적재)
            import pandas as pd
            from collections import defaultdict

            sheet_chunks = defaultdict(list)
            sheet_rows = defaultdict(int)

            for chunk_file in all_normalized_chunks:
                # 파일명에서 시트명 추출: normalized_시트명_chunk_XXXX_part_XXX.parquet
                basename = Path(chunk_file).stem  # normalized_INDEX_chunk_0000_part_000
                parts = basename.split('_chunk_')
                sheet_name = parts[0].replace('normalized_', '')  # INDEX
                sheet_chunks[sheet_name].append(chunk_file)
                df = pd.read_parquet(chunk_file)
                sheet_rows[sheet_name] += len(df)

            self.results['phase4'] = {
                'status': 'success',
                'sheets': {},
                'total_rows': 0,
                'validation': {'passed': True, 'failure_reasons': []}
            }

            base_table = self.config['bigquery']['table_id']  # tb_raw_2026

            for sheet_name, chunks in sheet_chunks.items():
                # 시트별 테이블명: tb_raw_2026_INDEX, tb_raw_2026_RAWSCORE 등
                table_name = f"{base_table}_{sheet_name}"
                expected = sheet_rows[sheet_name]

                logger.info(f"[Phase 4] 시트 '{sheet_name}' → 테이블 '{table_name}' ({expected:,} rows)")

                try:
                    result = loader.safe_load_with_staging(
                        chunks,
                        table_name,
                        expected_row_count=expected,
                        null_threshold=self.config['validation']['null_threshold']
                    )
                    self.results['phase4']['sheets'][sheet_name] = result
                    self.results['phase4']['total_rows'] += result.get('loaded_rows', 0)

                    if result.get('status') != 'success':
                        self.results['phase4']['status'] = 'partial'
                        self.results['phase4']['validation']['failure_reasons'].append(
                            f"{sheet_name}: {result.get('errors', [])}"
                        )
                except Exception as e:
                    logger.error(f"시트 '{sheet_name}' 적재 실패: {e}")
                    self.results['phase4']['sheets'][sheet_name] = {'status': 'failed', 'error': str(e)}
                    self.results['phase4']['status'] = 'partial'

            # 전체 성공 여부 확인
            if all(r.get('status') == 'success' for r in self.results['phase4']['sheets'].values()):
                self.results['phase4']['status'] = 'success'
                self.results['phase4']['validation']['passed'] = True

            # 업로드 리포트 생성
            loader.generate_upload_report(
                self.results['phase4'],
                all_normalized_chunks,
                str(self.output_dir)
            )
            
            logger.info(f"Phase 4 완료: 상태={self.results['phase4']['status']}")
            
            # 최종 리포트 생성
            self._generate_final_report()
            
            return self.results
            
        except Exception as e:
            logger.error(f"파이프라인 실패: {e}", exc_info=True)
            self._generate_final_report()
            raise

    def _migrate_existing_tables(self):
        """기존 테이블에 메타데이터 컬럼 추가 (v2.3)"""
        from google.cloud import bigquery
        from google.oauth2 import service_account
        try:
            creds = service_account.Credentials.from_service_account_file(
                self.config['bigquery']['credentials_path'],
                scopes=['https://www.googleapis.com/auth/bigquery']
            )
            client = bigquery.Client(project=self.config['bigquery']['project_id'], credentials=creds)
            dataset_id = self.config['bigquery']['dataset_id']
            base_table = self.config['bigquery']['table_id']

            query = f"""
            SELECT table_name FROM `{self.config['bigquery']['project_id']}.{dataset_id}.INFORMATION_SCHEMA.TABLES`
            WHERE table_name LIKE '{base_table}_%'
            AND table_name NOT LIKE '%_staging' AND table_name NOT LIKE '%_backup_%' AND table_name NOT LIKE '%_quarantine_%'
            """
            tables = [row.table_name for row in client.query(query).result()]
            logger.info(f"  기존 테이블 {len(tables)}개 발견")

            for tbl in tables:
                col_query = f"""
                SELECT column_name FROM `{self.config['bigquery']['project_id']}.{dataset_id}.INFORMATION_SCHEMA.COLUMNS`
                WHERE table_name = '{tbl}' AND column_name IN ('_ingested_at', '_source_filename', '_row_id')
                """
                existing = [r.column_name for r in client.query(col_query).result()]
                if len(existing) == 3:
                    continue
                tbl_ref = f"`{self.config['bigquery']['project_id']}.{dataset_id}.{tbl}`"
                if '_ingested_at' not in existing:
                    client.query(f"ALTER TABLE {tbl_ref} ADD COLUMN IF NOT EXISTS _ingested_at STRING").result()
                if '_source_filename' not in existing:
                    client.query(f"ALTER TABLE {tbl_ref} ADD COLUMN IF NOT EXISTS _source_filename STRING").result()
                if '_row_id' not in existing:
                    client.query(f"ALTER TABLE {tbl_ref} ADD COLUMN IF NOT EXISTS _row_id INT64").result()
                logger.info(f"  {tbl}: 메타데이터 컬럼 추가 완료")
        except Exception as e:
            logger.warning(f"  기존 테이블 마이그레이션 스킵: {e}")

    def _generate_final_report(self):
        """최종 리포트 생성"""
        total_time = time.perf_counter() - self.start_time if self.start_time else 0
        
        report = {
            'pipeline_version': '2.0',
            'execution_time_seconds': round(total_time, 2),
            'phases': {
                'phase1': {
                    'status': 'completed' if 'phase1' in self.results else 'failed',
                    'scan_time_seconds': self.results.get('phase1', {}).get('scan_time_seconds', 0),
                    'target_sheets': len([
                        s for s in self.results.get('phase1', {}).get('sheets', [])
                        if s.get('target_type') in ['heavy', 'medium']
                    ])
                },
                'phase2': {
                    'status': 'completed' if 'phase2' in self.results else 'failed',
                    'total_chunks': sum(
                        len(r.get('value_chunks', []))
                        for r in self.results.get('phase2', [])
                    )
                },
                'phase3': {
                    'status': 'completed' if 'phase3' in self.results else 'failed',
                    'total_chunks': sum(
                        len(r.get('parquet_chunks', []))
                        for r in self.results.get('phase3', [])
                    )
                },
                'phase4': {
                    'status': self.results.get('phase4', {}).get('status', 'failed'),
                    'loaded_rows': self.results.get('phase4', {}).get('total_rows', 0),
                    'tables_created': len(self.results.get('phase4', {}).get('sheets', {})),
                    'validation_passed': self.results.get('phase4', {}).get('validation', {}).get('passed', False)
                }
            },
            'status': 'success' if self.results.get('phase4', {}).get('status') == 'success' else 'failed'
        }
        
        report_path = self.output_dir / 'pipeline_report.json'
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2, default=str)
        
        logger.info(f"[완료] 총 실행 시간: {total_time:.2f}초")
        logger.info(f"[완료] 최종 리포트: {report_path}")
        
        return str(report_path)


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='NEO GOD Ultra Pipeline v2.0')
    parser.add_argument('--config', type=str, default='config.yaml', help='설정 파일 경로')
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("NEO GOD Ultra Pipeline v2.0")
    print("=" * 60)
    print(f"설정 파일: {args.config}")
    print()
    
    pipeline = NeoGodUltraPipeline(args.config)
    result = pipeline.execute()
    
    print()
    print("파이프라인 실행 완료!")
    print(f"상태: {result.get('phase4', {}).get('status', 'unknown')}")
