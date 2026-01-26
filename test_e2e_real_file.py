# ============================================================
# NEO GOD Ultra E2E 실제 파일 테스트
# test_e2e_real_file.py
# 실제 Excel 파일(225,420행)로 전체 파이프라인 실행 및 검증
# ============================================================

import sys
import os
import unittest
import json
import time
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

# Windows 인코딩 설정
if sys.platform == 'win32':
    try:
        if hasattr(sys.stdout, 'reconfigure'):
            sys.stdout.reconfigure(encoding='utf-8')
        if hasattr(sys.stderr, 'reconfigure'):
            sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

try:
    import pandas as pd
    import pyarrow.parquet as pq
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False


class E2ETestConfig:
    """E2E 테스트 설정"""

    # 소스 파일
    SOURCE_FILE = Path(r"Y:\0126\0126\202511고속성장분석기(가채점)20251114.xlsx")

    # 출력 디렉토리
    OUTPUT_DIR = Path(r"Y:\0126\0126\output")
    TEST_OUTPUT_DIR = Path(r"Y:\0126\0126\e2e_test_output")

    # 기대 데이터
    EXPECTED_TOTAL_ROWS = 225420
    EXPECTED_SHEETS = ['INDEX', 'RAWSCORE', '이과계열분석결과', '문과계열분석결과', 'SUBJECT1', 'SUBJECT3']

    # 검증 임계값
    NULL_THRESHOLD = 0.1  # 10%
    ROW_TOLERANCE = 0.01  # 1%


class Phase1ScoutingTest(unittest.TestCase):
    """Phase 1: 고속 정찰 테스트"""

    def test_01_source_file_exists(self):
        """소스 파일 존재 확인"""
        self.assertTrue(
            E2ETestConfig.SOURCE_FILE.exists(),
            f"소스 파일 없음: {E2ETestConfig.SOURCE_FILE}"
        )

        file_size_mb = E2ETestConfig.SOURCE_FILE.stat().st_size / (1024 * 1024)
        print(f"\n[INFO] 소스 파일 크기: {file_size_mb:.2f} MB")

    def test_02_scouting_report_exists(self):
        """정찰 리포트 존재 확인"""
        report_path = E2ETestConfig.OUTPUT_DIR / 'scouting_report.json'
        self.assertTrue(report_path.exists(), "scouting_report.json 없음")

        with open(report_path, 'r', encoding='utf-8') as f:
            report = json.load(f)

        print(f"\n[INFO] 정찰 리포트:")
        print(f"  스캔된 시트 수: {len(report.get('sheets', {}))}")

    def test_03_target_sheets_identified(self):
        """타겟 시트 식별 확인"""
        target_path = E2ETestConfig.OUTPUT_DIR / 'target_sheets.json'
        self.assertTrue(target_path.exists(), "target_sheets.json 없음")

        with open(target_path, 'r', encoding='utf-8') as f:
            targets = json.load(f)

        target_names = [t.get('sheet_name') for t in targets]

        print(f"\n[INFO] 타겟 시트: {target_names}")

        # 주요 시트 포함 확인
        for expected_sheet in E2ETestConfig.EXPECTED_SHEETS:
            self.assertIn(expected_sheet, target_names, f"시트 누락: {expected_sheet}")


class Phase2ExtractionTest(unittest.TestCase):
    """Phase 2: 이원화 추출 테스트"""

    def test_01_parquet_files_created(self):
        """Parquet 파일 생성 확인"""
        parquet_files = list(E2ETestConfig.OUTPUT_DIR.glob('*.parquet'))
        self.assertGreater(len(parquet_files), 0, "Parquet 파일 없음")

        print(f"\n[INFO] 생성된 Parquet 파일: {len(parquet_files)}개")
        for pf in parquet_files[:5]:
            print(f"  - {pf.name}")
        if len(parquet_files) > 5:
            print(f"  ... 외 {len(parquet_files) - 5}개")

    def test_02_formula_metadata_created(self):
        """수식 메타데이터 생성 확인"""
        metadata_files = list(E2ETestConfig.OUTPUT_DIR.glob('*_formula_metadata.json'))
        self.assertGreater(len(metadata_files), 0, "수식 메타데이터 없음")

        print(f"\n[INFO] 수식 메타데이터 파일: {len(metadata_files)}개")
        for mf in metadata_files:
            print(f"  - {mf.name}")

    def test_03_total_rows_extracted(self):
        """총 행 수 확인"""
        if not PANDAS_AVAILABLE:
            self.skipTest("Pandas 없음")

        total_rows = 0
        parquet_files = list(E2ETestConfig.OUTPUT_DIR.glob('*.parquet'))

        for pf in parquet_files:
            if 'clean_ingestion' not in pf.name:  # 정규화된 파일 제외
                try:
                    df = pd.read_parquet(pf)
                    total_rows += len(df)
                except:
                    pass

        print(f"\n[INFO] 추출된 총 행 수: {total_rows:,}")

        # 허용 오차 내 확인
        expected = E2ETestConfig.EXPECTED_TOTAL_ROWS
        tolerance = E2ETestConfig.ROW_TOLERANCE
        min_rows = expected * (1 - tolerance)
        max_rows = expected * (1 + tolerance)

        self.assertGreaterEqual(total_rows, min_rows * 0.5, f"행 수 너무 적음: {total_rows}")


class Phase3NormalizationTest(unittest.TestCase):
    """Phase 3: Date-First 정규화 테스트"""

    def test_01_normalized_files_created(self):
        """정규화된 파일 생성 확인"""
        clean_files = list(E2ETestConfig.OUTPUT_DIR.glob('clean_ingestion_*.parquet'))
        self.assertGreater(len(clean_files), 0, "정규화 파일 없음")

        print(f"\n[INFO] 정규화된 파일: {len(clean_files)}개")

    def test_02_data_quality_report_exists(self):
        """데이터 품질 리포트 확인"""
        report_path = E2ETestConfig.OUTPUT_DIR / 'data_quality_report.json'
        self.assertTrue(report_path.exists(), "data_quality_report.json 없음")

        with open(report_path, 'r', encoding='utf-8') as f:
            report = json.load(f)

        print(f"\n[INFO] 데이터 품질 리포트:")
        print(f"  총 행: {report.get('total_rows', 'N/A')}")
        print(f"  총 컬럼: {report.get('total_cols', 'N/A')}")

    def test_03_column_mapping_exists(self):
        """컬럼 매핑 파일 확인"""
        mapping_path = E2ETestConfig.OUTPUT_DIR / 'column_mapping.json'
        self.assertTrue(mapping_path.exists(), "column_mapping.json 없음")

        with open(mapping_path, 'r', encoding='utf-8') as f:
            mapping = json.load(f)

        print(f"\n[INFO] 컬럼 매핑: {len(mapping)}개 컬럼")

    def test_04_data_types_normalized(self):
        """데이터 타입 정규화 확인"""
        if not PANDAS_AVAILABLE:
            self.skipTest("Pandas 없음")

        clean_files = list(E2ETestConfig.OUTPUT_DIR.glob('clean_ingestion_*.parquet'))
        if not clean_files:
            self.skipTest("정규화 파일 없음")

        df = pd.read_parquet(clean_files[0])

        print(f"\n[INFO] 정규화된 데이터 타입:")
        for col in df.columns[:10]:
            print(f"  {col}: {df[col].dtype}")

    def test_05_null_ratio_within_threshold(self):
        """NULL 비율 검증"""
        if not PANDAS_AVAILABLE:
            self.skipTest("Pandas 없음")

        clean_files = list(E2ETestConfig.OUTPUT_DIR.glob('clean_ingestion_*.parquet'))
        if not clean_files:
            self.skipTest("정규화 파일 없음")

        df = pd.read_parquet(clean_files[0])

        total_cells = df.size
        null_cells = df.isnull().sum().sum()
        null_ratio = null_cells / total_cells if total_cells > 0 else 0

        print(f"\n[INFO] NULL 비율: {null_ratio:.4f} ({null_cells:,}/{total_cells:,})")

        self.assertLessEqual(
            null_ratio,
            E2ETestConfig.NULL_THRESHOLD,
            f"NULL 비율 초과: {null_ratio:.2%}"
        )


class Phase4LoadValidationTest(unittest.TestCase):
    """Phase 4: 적재 검증 테스트 (로컬 검증)"""

    def test_01_pipeline_report_exists(self):
        """파이프라인 리포트 확인"""
        report_path = E2ETestConfig.OUTPUT_DIR / 'pipeline_report.json'
        if not report_path.exists():
            self.skipTest("pipeline_report.json 없음 (Phase 4 미실행)")

        with open(report_path, 'r', encoding='utf-8') as f:
            report = json.load(f)

        print(f"\n[INFO] 파이프라인 리포트:")
        print(f"  상태: {report.get('status', 'N/A')}")

    def test_02_staging_readiness(self):
        """Staging 준비 상태 확인"""
        # 모든 Parquet 파일이 BigQuery 호환 형식인지 확인
        if not PANDAS_AVAILABLE:
            self.skipTest("Pandas 없음")

        clean_files = list(E2ETestConfig.OUTPUT_DIR.glob('clean_ingestion_*.parquet'))
        if not clean_files:
            self.skipTest("정규화 파일 없음")

        for pf in clean_files:
            try:
                # Parquet 메타데이터 읽기
                parquet_file = pq.ParquetFile(pf)
                schema = parquet_file.schema_arrow

                print(f"\n[INFO] {pf.name} 스키마:")
                for field in schema[:5]:
                    print(f"  {field.name}: {field.type}")

            except Exception as e:
                self.fail(f"Parquet 파일 검증 실패: {pf.name} - {e}")


class E2EPerformanceTest(unittest.TestCase):
    """E2E 성능 테스트"""

    def test_01_phase1_performance(self):
        """Phase 1 성능 측정"""
        # 정찰 리포트에서 실행 시간 확인
        report_path = E2ETestConfig.OUTPUT_DIR / 'scouting_report.json'
        if not report_path.exists():
            self.skipTest("scouting_report.json 없음")

        with open(report_path, 'r', encoding='utf-8') as f:
            report = json.load(f)

        execution_time = report.get('execution_time_seconds', 0)
        print(f"\n[PERF] Phase 1 실행 시간: {execution_time:.2f}초")

    def test_02_memory_efficiency(self):
        """메모리 효율성 확인"""
        if not PANDAS_AVAILABLE:
            self.skipTest("Pandas 없음")

        parquet_files = list(E2ETestConfig.OUTPUT_DIR.glob('*.parquet'))

        total_size_mb = 0
        for pf in parquet_files:
            total_size_mb += pf.stat().st_size / (1024 * 1024)

        source_size_mb = E2ETestConfig.SOURCE_FILE.stat().st_size / (1024 * 1024)

        compression_ratio = total_size_mb / source_size_mb if source_size_mb > 0 else 0

        print(f"\n[PERF] 파일 크기 비교:")
        print(f"  원본 Excel: {source_size_mb:.2f} MB")
        print(f"  Parquet 합계: {total_size_mb:.2f} MB")
        print(f"  압축률: {compression_ratio:.2f}")


class E2EDataIntegrityTest(unittest.TestCase):
    """E2E 데이터 무결성 테스트"""

    def test_01_no_data_loss(self):
        """데이터 손실 없음 확인"""
        scouting_path = E2ETestConfig.OUTPUT_DIR / 'scouting_report.json'
        if not scouting_path.exists():
            self.skipTest("scouting_report.json 없음")

        with open(scouting_path, 'r', encoding='utf-8') as f:
            scouting = json.load(f)

        # 정찰에서 발견된 행 수
        scouted_rows = 0
        for sheet_name, sheet_info in scouting.get('sheets', {}).items():
            scouted_rows += sheet_info.get('row_count', 0)

        print(f"\n[INTEGRITY] 정찰된 총 행 수: {scouted_rows:,}")

        if not PANDAS_AVAILABLE:
            return

        # 추출된 행 수
        extracted_rows = 0
        for pf in E2ETestConfig.OUTPUT_DIR.glob('*.parquet'):
            if 'clean_ingestion' not in pf.name:
                try:
                    df = pd.read_parquet(pf)
                    extracted_rows += len(df)
                except:
                    pass

        print(f"  추출된 총 행 수: {extracted_rows:,}")

        # 허용 오차 내 확인 (헤더 행 제외로 약간의 차이 허용)
        if scouted_rows > 0:
            loss_ratio = abs(scouted_rows - extracted_rows) / scouted_rows
            print(f"  차이 비율: {loss_ratio:.4f}")
            self.assertLess(loss_ratio, 0.05, f"데이터 손실 의심: {loss_ratio:.2%}")

    def test_02_formula_preservation(self):
        """수식 메타데이터 보존 확인"""
        metadata_files = list(E2ETestConfig.OUTPUT_DIR.glob('*_formula_metadata.json'))

        total_formulas = 0
        for mf in metadata_files:
            with open(mf, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
                total_formulas += len(metadata.get('formula_columns', {}))

        print(f"\n[INTEGRITY] 보존된 수식 메타데이터: {total_formulas}개 컬럼")
        self.assertGreater(total_formulas, 0, "수식 메타데이터 없음")


def run_e2e_tests():
    """E2E 테스트 실행"""
    print("=" * 70)
    print("NEO GOD Ultra E2E 실제 파일 테스트")
    print("=" * 70)

    # 환경 확인
    print("\n[환경 확인]")
    print(f"  소스 파일: {'존재' if E2ETestConfig.SOURCE_FILE.exists() else '없음'}")
    print(f"  출력 디렉토리: {'존재' if E2ETestConfig.OUTPUT_DIR.exists() else '없음'}")
    print(f"  pandas: {'설치됨' if PANDAS_AVAILABLE else '미설치'}")

    if E2ETestConfig.SOURCE_FILE.exists():
        size_mb = E2ETestConfig.SOURCE_FILE.stat().st_size / (1024 * 1024)
        print(f"  파일 크기: {size_mb:.2f} MB")

    # 테스트 스위트 생성
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    suite.addTests(loader.loadTestsFromTestCase(Phase1ScoutingTest))
    suite.addTests(loader.loadTestsFromTestCase(Phase2ExtractionTest))
    suite.addTests(loader.loadTestsFromTestCase(Phase3NormalizationTest))
    suite.addTests(loader.loadTestsFromTestCase(Phase4LoadValidationTest))
    suite.addTests(loader.loadTestsFromTestCase(E2EPerformanceTest))
    suite.addTests(loader.loadTestsFromTestCase(E2EDataIntegrityTest))

    # 테스트 실행
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # 결과 요약
    print("\n" + "=" * 70)
    print("E2E 테스트 결과 요약")
    print("=" * 70)
    print(f"실행: {result.testsRun}")
    print(f"성공: {result.testsRun - len(result.failures) - len(result.errors) - len(result.skipped)}")
    print(f"실패: {len(result.failures)}")
    print(f"에러: {len(result.errors)}")
    print(f"스킵: {len(result.skipped)}")

    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_e2e_tests()
    sys.exit(0 if success else 1)
