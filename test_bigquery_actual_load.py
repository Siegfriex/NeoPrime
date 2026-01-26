# ============================================================
# NEO GOD Ultra BigQuery 실제 적재 테스트
# test_bigquery_actual_load.py
# BigQuery 실제 연결 및 소규모 데이터 적재 테스트
# ============================================================

import sys
import os
import unittest
import json
import tempfile
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional

# Windows 인코딩 설정
if sys.platform == 'win32':
    try:
        if hasattr(sys.stdout, 'reconfigure'):
            sys.stdout.reconfigure(encoding='utf-8')
        if hasattr(sys.stderr, 'reconfigure'):
            sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

# BigQuery 관련 임포트
try:
    from google.cloud import bigquery
    from google.oauth2 import service_account
    BIGQUERY_AVAILABLE = True
except ImportError:
    BIGQUERY_AVAILABLE = False
    print("[WARNING] google-cloud-bigquery not installed")

try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False


class BigQueryTestConfig:
    """BigQuery 테스트 설정"""

    # 기존 설정 파일 경로
    CONFIG_PATH = Path(__file__).parent / 'config.yaml'

    # 서비스 계정 키 파일 (기존 것 사용)
    LOADER_KEY_PATH = Path(__file__).parent / 'neoprime-loader-key.json'
    ADMIN_KEY_PATH = Path(__file__).parent / 'neoprime-admin-key.json'

    # BigQuery 설정 (config.yaml에서 로드)
    PROJECT_ID = 'neoprime0305'
    DATASET_ID = 'ds_neoprime_entrance'
    TABLE_ID = 'tb_raw_2026'
    LOCATION = 'asia-northeast3'  # 서울

    # 테스트용 테이블 (기존 데이터에 영향 없음)
    TEST_TABLE_ID = 'tb_test_load_validation'

    @classmethod
    def load_config(cls) -> Dict:
        """config.yaml 로드"""
        try:
            import yaml
            with open(cls.CONFIG_PATH, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except Exception as e:
            print(f"[WARNING] config.yaml 로드 실패: {e}")
            return {}

    @classmethod
    def get_credentials(cls, use_loader: bool = True) -> Optional[Any]:
        """서비스 계정 인증 정보 로드"""
        if not BIGQUERY_AVAILABLE:
            return None

        key_path = cls.LOADER_KEY_PATH if use_loader else cls.ADMIN_KEY_PATH

        if not key_path.exists():
            print(f"[WARNING] 키 파일 없음: {key_path}")
            return None

        try:
            credentials = service_account.Credentials.from_service_account_file(
                str(key_path),
                scopes=['https://www.googleapis.com/auth/bigquery']
            )
            return credentials
        except Exception as e:
            print(f"[ERROR] 인증 정보 로드 실패: {e}")
            return None


class BigQueryConnectionTest(unittest.TestCase):
    """BigQuery 연결 테스트"""

    @classmethod
    def setUpClass(cls):
        """테스트 클래스 초기화"""
        cls.config = BigQueryTestConfig()
        cls.credentials = cls.config.get_credentials(use_loader=True)
        cls.client = None

        if BIGQUERY_AVAILABLE and cls.credentials:
            try:
                cls.client = bigquery.Client(
                    project=cls.config.PROJECT_ID,
                    credentials=cls.credentials,
                    location=cls.config.LOCATION
                )
            except Exception as e:
                print(f"[ERROR] BigQuery 클라이언트 생성 실패: {e}")

    def test_01_bigquery_available(self):
        """BigQuery 라이브러리 설치 확인"""
        self.assertTrue(BIGQUERY_AVAILABLE, "google-cloud-bigquery 설치 필요")

    def test_02_credentials_loaded(self):
        """서비스 계정 인증 정보 로드 확인"""
        if not BIGQUERY_AVAILABLE:
            self.skipTest("BigQuery 라이브러리 없음")
        self.assertIsNotNone(self.credentials, "서비스 계정 인증 정보 로드 실패")

    def test_03_client_created(self):
        """BigQuery 클라이언트 생성 확인"""
        if not BIGQUERY_AVAILABLE:
            self.skipTest("BigQuery 라이브러리 없음")
        if not self.credentials:
            self.skipTest("인증 정보 없음")
        self.assertIsNotNone(self.client, "BigQuery 클라이언트 생성 실패")

    def test_04_project_accessible(self):
        """프로젝트 접근 가능 확인"""
        if not self.client:
            self.skipTest("클라이언트 없음")

        try:
            # 간단한 쿼리로 연결 테스트
            query = "SELECT 1 as test"
            result = self.client.query(query).result()
            rows = list(result)
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0].test, 1)
            print(f"\n[SUCCESS] 프로젝트 {self.config.PROJECT_ID} 접근 성공")
        except Exception as e:
            self.fail(f"프로젝트 접근 실패: {e}")

    def test_05_dataset_exists(self):
        """데이터셋 존재 확인"""
        if not self.client:
            self.skipTest("클라이언트 없음")

        try:
            dataset_ref = f"{self.config.PROJECT_ID}.{self.config.DATASET_ID}"
            dataset = self.client.get_dataset(dataset_ref)
            self.assertEqual(dataset.dataset_id, self.config.DATASET_ID)
            print(f"\n[SUCCESS] 데이터셋 {self.config.DATASET_ID} 존재 확인")
            print(f"  위치: {dataset.location}")
            print(f"  생성일: {dataset.created}")
        except Exception as e:
            self.fail(f"데이터셋 접근 실패: {e}")


class BigQuerySmallDataLoadTest(unittest.TestCase):
    """소규모 데이터 적재 테스트"""

    @classmethod
    def setUpClass(cls):
        """테스트 클래스 초기화"""
        cls.config = BigQueryTestConfig()
        cls.credentials = cls.config.get_credentials(use_loader=True)
        cls.client = None
        cls.test_table_created = False

        if BIGQUERY_AVAILABLE and cls.credentials:
            try:
                cls.client = bigquery.Client(
                    project=cls.config.PROJECT_ID,
                    credentials=cls.credentials,
                    location=cls.config.LOCATION
                )
            except Exception as e:
                print(f"[ERROR] BigQuery 클라이언트 생성 실패: {e}")

    @classmethod
    def tearDownClass(cls):
        """테스트 클래스 정리 - 테스트 테이블 삭제"""
        if cls.client and cls.test_table_created:
            try:
                table_ref = f"{cls.config.PROJECT_ID}.{cls.config.DATASET_ID}.{cls.config.TEST_TABLE_ID}"
                cls.client.delete_table(table_ref, not_found_ok=True)
                print(f"\n[CLEANUP] 테스트 테이블 삭제: {cls.config.TEST_TABLE_ID}")
            except Exception as e:
                print(f"[WARNING] 테스트 테이블 삭제 실패: {e}")

    def test_01_create_test_table(self):
        """테스트 테이블 생성"""
        if not self.client:
            self.skipTest("클라이언트 없음")

        try:
            table_ref = f"{self.config.PROJECT_ID}.{self.config.DATASET_ID}.{self.config.TEST_TABLE_ID}"

            # 기존 테이블 삭제 (있으면)
            self.client.delete_table(table_ref, not_found_ok=True)

            # 스키마 정의
            schema = [
                bigquery.SchemaField("id", "INTEGER", mode="REQUIRED"),
                bigquery.SchemaField("name", "STRING"),
                bigquery.SchemaField("score", "FLOAT64"),
                bigquery.SchemaField("grade", "STRING"),
                bigquery.SchemaField("created_at", "TIMESTAMP"),
            ]

            table = bigquery.Table(table_ref, schema=schema)
            table = self.client.create_table(table)

            self.__class__.test_table_created = True

            self.assertEqual(table.table_id, self.config.TEST_TABLE_ID)
            print(f"\n[SUCCESS] 테스트 테이블 생성: {table.table_id}")

        except Exception as e:
            self.fail(f"테스트 테이블 생성 실패: {e}")

    def test_02_insert_test_data(self):
        """테스트 데이터 삽입"""
        if not self.client:
            self.skipTest("클라이언트 없음")
        if not self.__class__.test_table_created:
            self.skipTest("테스트 테이블 없음")

        try:
            table_ref = f"{self.config.PROJECT_ID}.{self.config.DATASET_ID}.{self.config.TEST_TABLE_ID}"

            # 테스트 데이터 (10행)
            rows_to_insert = [
                {"id": 1, "name": "홍길동", "score": 95.5, "grade": "A", "created_at": datetime.now().isoformat()},
                {"id": 2, "name": "김철수", "score": 88.0, "grade": "B", "created_at": datetime.now().isoformat()},
                {"id": 3, "name": "이영희", "score": 92.3, "grade": "A", "created_at": datetime.now().isoformat()},
                {"id": 4, "name": "박민수", "score": 78.5, "grade": "C", "created_at": datetime.now().isoformat()},
                {"id": 5, "name": "정수연", "score": 85.0, "grade": "B", "created_at": datetime.now().isoformat()},
                {"id": 6, "name": "서울대", "score": 100.0, "grade": "A+", "created_at": datetime.now().isoformat()},
                {"id": 7, "name": "연세대", "score": 98.5, "grade": "A", "created_at": datetime.now().isoformat()},
                {"id": 8, "name": "고려대", "score": 97.0, "grade": "A", "created_at": datetime.now().isoformat()},
                {"id": 9, "name": "성균관대", "score": 95.0, "grade": "A", "created_at": datetime.now().isoformat()},
                {"id": 10, "name": "한양대", "score": 93.5, "grade": "A", "created_at": datetime.now().isoformat()},
            ]

            errors = self.client.insert_rows_json(table_ref, rows_to_insert)

            if errors:
                self.fail(f"데이터 삽입 에러: {errors}")

            print(f"\n[SUCCESS] {len(rows_to_insert)}행 삽입 완료")

        except Exception as e:
            self.fail(f"데이터 삽입 실패: {e}")

    def test_03_query_test_data(self):
        """테스트 데이터 조회"""
        if not self.client:
            self.skipTest("클라이언트 없음")
        if not self.__class__.test_table_created:
            self.skipTest("테스트 테이블 없음")

        try:
            query = f"""
            SELECT COUNT(*) as cnt, AVG(score) as avg_score
            FROM `{self.config.PROJECT_ID}.{self.config.DATASET_ID}.{self.config.TEST_TABLE_ID}`
            """

            result = self.client.query(query).result()
            rows = list(result)

            self.assertEqual(len(rows), 1)
            print(f"\n[SUCCESS] 데이터 조회 완료")
            print(f"  행 수: {rows[0].cnt}")
            print(f"  평균 점수: {rows[0].avg_score:.2f}")

        except Exception as e:
            self.fail(f"데이터 조회 실패: {e}")

    def test_04_null_validation_query(self):
        """NULL 검증 쿼리 테스트 (Phase 4 로직)"""
        if not self.client:
            self.skipTest("클라이언트 없음")
        if not self.__class__.test_table_created:
            self.skipTest("테스트 테이블 없음")

        try:
            # Phase 4의 NULL 검증 쿼리 패턴
            query = f"""
            SELECT
                'name' as column_name,
                COUNTIF(name IS NULL) as null_count,
                COUNT(*) as total_count,
                SAFE_DIVIDE(COUNTIF(name IS NULL), COUNT(*)) as null_ratio
            FROM `{self.config.PROJECT_ID}.{self.config.DATASET_ID}.{self.config.TEST_TABLE_ID}`
            UNION ALL
            SELECT
                'score' as column_name,
                COUNTIF(score IS NULL) as null_count,
                COUNT(*) as total_count,
                SAFE_DIVIDE(COUNTIF(score IS NULL), COUNT(*)) as null_ratio
            FROM `{self.config.PROJECT_ID}.{self.config.DATASET_ID}.{self.config.TEST_TABLE_ID}`
            """

            result = self.client.query(query).result()
            rows = list(result)

            print(f"\n[SUCCESS] NULL 검증 쿼리 실행 완료")
            for row in rows:
                print(f"  {row.column_name}: NULL {row.null_count}/{row.total_count} ({row.null_ratio:.2%})")

            # 테스트 데이터에 NULL이 없어야 함
            for row in rows:
                self.assertEqual(row.null_count, 0)

        except Exception as e:
            self.fail(f"NULL 검증 쿼리 실패: {e}")


class BigQueryParquetLoadTest(unittest.TestCase):
    """Parquet 파일 적재 테스트"""

    @classmethod
    def setUpClass(cls):
        """테스트 클래스 초기화"""
        cls.config = BigQueryTestConfig()
        cls.credentials = cls.config.get_credentials(use_loader=True)
        cls.client = None
        cls.parquet_table_id = 'tb_test_parquet_load'
        cls.test_table_created = False

        if BIGQUERY_AVAILABLE and cls.credentials:
            try:
                cls.client = bigquery.Client(
                    project=cls.config.PROJECT_ID,
                    credentials=cls.credentials,
                    location=cls.config.LOCATION
                )
            except Exception as e:
                print(f"[ERROR] BigQuery 클라이언트 생성 실패: {e}")

    @classmethod
    def tearDownClass(cls):
        """테스트 테이블 정리"""
        if cls.client and cls.test_table_created:
            try:
                table_ref = f"{cls.config.PROJECT_ID}.{cls.config.DATASET_ID}.{cls.parquet_table_id}"
                cls.client.delete_table(table_ref, not_found_ok=True)
                print(f"\n[CLEANUP] Parquet 테스트 테이블 삭제")
            except:
                pass

    def test_01_load_parquet_from_local(self):
        """로컬 Parquet 파일에서 BigQuery 로드"""
        if not self.client:
            self.skipTest("클라이언트 없음")
        if not PANDAS_AVAILABLE:
            self.skipTest("Pandas 없음")

        try:
            # 테스트용 Parquet 파일 생성
            test_df = pd.DataFrame({
                'id': range(1, 101),
                'name': [f'Student_{i}' for i in range(1, 101)],
                'score': [50 + (i % 50) for i in range(1, 101)],
                'subject': ['국어', '수학', '영어', '탐구', '논술'] * 20,
            })

            # 임시 Parquet 파일 생성
            with tempfile.NamedTemporaryFile(suffix='.parquet', delete=False) as tmp:
                tmp_path = tmp.name
                test_df.to_parquet(tmp_path, index=False)

            # BigQuery에 로드
            table_ref = f"{self.config.PROJECT_ID}.{self.config.DATASET_ID}.{self.parquet_table_id}"

            # 기존 테이블 삭제
            self.client.delete_table(table_ref, not_found_ok=True)

            job_config = bigquery.LoadJobConfig(
                source_format=bigquery.SourceFormat.PARQUET,
                write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
            )

            with open(tmp_path, 'rb') as source_file:
                job = self.client.load_table_from_file(
                    source_file,
                    table_ref,
                    job_config=job_config
                )

            job.result()  # 완료 대기

            self.__class__.test_table_created = True

            # 로드 결과 확인
            table = self.client.get_table(table_ref)
            self.assertEqual(table.num_rows, 100)

            print(f"\n[SUCCESS] Parquet 로드 완료")
            print(f"  행 수: {table.num_rows}")
            print(f"  스키마: {[f.name for f in table.schema]}")

            # 임시 파일 삭제
            os.unlink(tmp_path)

        except Exception as e:
            self.fail(f"Parquet 로드 실패: {e}")


def run_bigquery_tests():
    """BigQuery 테스트 실행"""
    print("=" * 70)
    print("NEO GOD Ultra BigQuery 실제 적재 테스트")
    print("=" * 70)

    # 환경 확인
    print("\n[환경 확인]")
    print(f"  google-cloud-bigquery: {'설치됨' if BIGQUERY_AVAILABLE else '미설치'}")
    print(f"  pandas: {'설치됨' if PANDAS_AVAILABLE else '미설치'}")

    config = BigQueryTestConfig()
    print(f"  프로젝트: {config.PROJECT_ID}")
    print(f"  데이터셋: {config.DATASET_ID}")
    print(f"  키 파일 (loader): {'존재' if config.LOADER_KEY_PATH.exists() else '없음'}")
    print(f"  키 파일 (admin): {'존재' if config.ADMIN_KEY_PATH.exists() else '없음'}")

    # 테스트 스위트 생성
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    suite.addTests(loader.loadTestsFromTestCase(BigQueryConnectionTest))
    suite.addTests(loader.loadTestsFromTestCase(BigQuerySmallDataLoadTest))
    suite.addTests(loader.loadTestsFromTestCase(BigQueryParquetLoadTest))

    # 테스트 실행
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # 결과 요약
    print("\n" + "=" * 70)
    print("테스트 결과 요약")
    print("=" * 70)
    print(f"실행: {result.testsRun}")
    print(f"성공: {result.testsRun - len(result.failures) - len(result.errors) - len(result.skipped)}")
    print(f"실패: {len(result.failures)}")
    print(f"에러: {len(result.errors)}")
    print(f"스킵: {len(result.skipped)}")

    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_bigquery_tests()
    sys.exit(0 if success else 1)
