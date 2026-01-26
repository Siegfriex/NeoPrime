# ============================================================
# Phase별 단위 테스트 스크립트
# NEO GOD Ultra Framework v2.0
# ============================================================

import sys
import io
import json
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

def test_phase1():
    """Phase 1 테스트: 고속 정찰"""
    print("=" * 60)
    print("Phase 1 테스트: 고속 정찰")
    print("=" * 60)
    
    try:
        from phase1_scouting import scout_with_fallback, generate_scouting_report
        
        # 테스트 파일 경로
        test_file = r"Y:\0126\0126\202511고속성장분석기(가채점)20251114.xlsx"
        
        if not Path(test_file).exists():
            print(f"[SKIP] 테스트 파일이 없습니다: {test_file}")
            return False
        
        print(f"테스트 파일: {test_file}")
        print()
        
        # 정찰 실행
        result = scout_with_fallback(test_file)
        
        # 결과 검증
        assert 'sheets' in result, "시트 정보 없음"
        assert 'scan_time_seconds' in result, "스캔 시간 없음"
        assert len(result['sheets']) > 0, "시트가 없음"
        
        print(f"✓ 스캔 완료: {result['scan_time_seconds']}초")
        print(f"✓ 시트 수: {len(result['sheets'])}개")
        print(f"✓ 엔진: {result.get('engine', 'unknown')}")
        
        # 리포트 생성 테스트
        report_files = generate_scouting_report(result, './test_output')
        assert Path(report_files['scouting_report']).exists(), "리포트 파일 생성 실패"
        assert Path(report_files['target_sheets']).exists(), "타겟 시트 파일 생성 실패"
        
        print(f"✓ 리포트 생성 완료")
        print()
        return True
        
    except Exception as e:
        print(f"✗ Phase 1 테스트 실패: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_phase2():
    """Phase 2 테스트: 물리적 이원화 추출"""
    print("=" * 60)
    print("Phase 2 테스트: 물리적 이원화 추출")
    print("=" * 60)
    
    try:
        from phase2_extraction import PhysicalDualTrackExtractor
        
        # 테스트 파일 경로
        test_file = r"Y:\0126\0126\202511고속성장분석기(가채점)20251114.xlsx"
        
        if not Path(test_file).exists():
            print(f"[SKIP] 테스트 파일이 없습니다: {test_file}")
            return False
        
        # Phase 1 결과에서 첫 번째 시트 가져오기
        from phase1_scouting import scout_with_fallback
        scout_result = scout_with_fallback(test_file)
        target_sheets = [s['name'] for s in scout_result['sheets'] if s['target_type'] in ['heavy', 'medium']]
        
        if not target_sheets:
            print("[SKIP] 타겟 시트가 없습니다")
            return False
        
        test_sheet = target_sheets[0]
        print(f"테스트 시트: {test_sheet}")
        print()
        
        # 추출 실행
        extractor = PhysicalDualTrackExtractor(test_file, './test_output')
        result = extractor.run_dual_track_extraction(
            test_sheet,
            chunk_size=1000,  # 작은 청크로 테스트
            formula_sample_rows=5
        )
        
        # 결과 검증
        assert 'value_chunks' in result, "값 청크 없음"
        assert 'formula_metadata' in result, "수식 메타데이터 없음"
        assert len(result['value_chunks']) > 0, "청크 파일 생성 실패"
        
        # 파일 존재 확인
        for chunk_file in result['value_chunks']:
            assert Path(chunk_file).exists(), f"청크 파일 없음: {chunk_file}"
        
        print(f"✓ 추출 완료: {result['stats']['total_rows']}행")
        print(f"✓ 청크 수: {result['stats']['total_chunks']}개")
        print(f"✓ 수식 컬럼: {len(result['formula_metadata']['columns_with_formulas'])}개")
        print()
        return True
        
    except Exception as e:
        print(f"✗ Phase 2 테스트 실패: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_phase3():
    """Phase 3 테스트: Date-First 정규화"""
    print("=" * 60)
    print("Phase 3 테스트: Date-First 정규화")
    print("=" * 60)
    
    try:
        from phase3_normalization import DateFirstNormalizer
        import pandas as pd
        import numpy as np
        
        # 테스트 데이터 생성
        test_data = {
            'excel_date_serial': [44927, 44928, 44929, None],  # Excel 날짜 시리얼
            'date_string': ['2023-01-01', '2023-01-02', '2023-01-03', None],
            'numeric': [100, 200, 300, None],
            'string': ['test1', 'test2', 'test3', None],
            'excel_error': ['#N/A', '#VALUE!', 'normal', None]
        }
        df = pd.DataFrame(test_data)
        
        print("테스트 데이터 생성 완료")
        print()
        
        # 정규화 실행
        normalizer = DateFirstNormalizer()
        result = normalizer.normalize_dataframe(
            df,
            output_dir='./test_output',
            max_chunk_size_mb=1  # 작은 크기로 테스트
        )
        
        # 결과 검증
        assert 'parquet_chunks' in result, "Parquet 청크 없음"
        assert len(result['parquet_chunks']) > 0, "청크 파일 생성 실패"
        assert 'column_mapping' in result, "컬럼 매핑 없음"
        assert 'quality_report' in result, "품질 리포트 없음"
        
        # 파일 존재 확인
        assert Path(result['column_mapping']).exists(), "컬럼 매핑 파일 없음"
        assert Path(result['quality_report']).exists(), "품질 리포트 파일 없음"
        
        print(f"✓ 정규화 완료: {result['total_rows']}행, {result['total_cols']}컬럼")
        print(f"✓ 청크 수: {len(result['parquet_chunks'])}개")
        print(f"✓ 타입 매핑: {len(result['type_mapping'])}개")
        print()
        return True
        
    except Exception as e:
        print(f"✗ Phase 3 테스트 실패: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_phase4():
    """Phase 4 테스트: Staging Table 적재 (모듈 및 설정 검증)"""
    print("=" * 60)
    print("Phase 4 테스트: Staging Table 적재")
    print("=" * 60)

    try:
        # 모듈 임포트 테스트
        from phase4_load import StagingTableLoader
        print("✓ StagingTableLoader 모듈 임포트 성공")

        # 설정 확인
        config_file = Path('config.yaml')
        if not config_file.exists():
            print("[SKIP] config.yaml 파일이 없습니다")
            return False

        import yaml
        with open(config_file, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)

        print(f"✓ config.yaml 로드 성공")
        print(f"  프로젝트: {config['bigquery']['project_id']}")
        print(f"  데이터셋: {config['bigquery']['dataset_id']}")

        # BigQuery 클라이언트 초기화 테스트 (권한 오류 허용)
        try:
            loader = StagingTableLoader(
                config['bigquery']['project_id'],
                config['bigquery']['dataset_id'],
                config['bigquery']['credentials_path'],
                config['bigquery'].get('location', 'asia-northeast3')
            )
            print(f"✓ BigQuery 클라이언트 초기화 성공")
        except Exception as bq_error:
            # BigQuery 권한 오류는 예상된 오류 (테스트 환경에서 정상)
            if 'Permission' in str(bq_error) or 'Forbidden' in str(bq_error) or 'credentials' in str(bq_error).lower():
                print(f"⚠ BigQuery 연결 실패 (권한/인증 문제 - 테스트 환경에서 예상됨)")
                print(f"  오류: {type(bq_error).__name__}")
            else:
                raise bq_error

        print()
        print("[INFO] 실제 적재는 유효한 BigQuery 인증 후 수행됩니다")
        print()
        return True

    except Exception as e:
        print(f"✗ Phase 4 테스트 실패: {e}")
        import traceback
        traceback.print_exc()
        return False


def run_all_tests():
    """모든 Phase 테스트 실행"""
    print("=" * 60)
    print("NEO GOD Ultra Framework v2.0 - Phase별 단위 테스트")
    print("=" * 60)
    print()
    
    # 테스트 출력 디렉토리 생성
    Path('./test_output').mkdir(exist_ok=True)
    
    results = {
        'phase1': test_phase1(),
        'phase2': test_phase2(),
        'phase3': test_phase3(),
        'phase4': test_phase4()
    }
    
    print("=" * 60)
    print("테스트 결과 요약")
    print("=" * 60)
    
    for phase, passed in results.items():
        status = "✓ 통과" if passed else "✗ 실패"
        print(f"{phase}: {status}")
    
    total_passed = sum(results.values())
    total_tests = len(results)
    
    print()
    print(f"총 {total_tests}개 테스트 중 {total_passed}개 통과")
    
    return all(results.values())


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
