# ============================================================
# 통합 테스트 스크립트
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


def test_integration():
    """전체 파이프라인 통합 테스트"""
    print("=" * 60)
    print("NEO GOD Ultra Framework v2.0 - 통합 테스트")
    print("=" * 60)
    print()
    
    try:
        # 설정 파일 확인
        config_file = Path('config.yaml')
        if not config_file.exists():
            print("[ERROR] config.yaml 파일이 없습니다")
            return False
        
        # 소스 파일 확인
        import yaml
        with open(config_file, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        source_file = Path(config['source_file'])
        if not source_file.exists():
            print(f"[ERROR] 소스 파일이 없습니다: {source_file}")
            return False
        
        print(f"설정 파일: {config_file}")
        print(f"소스 파일: {source_file}")
        print()
        
        # Master Pipeline 임포트 테스트
        print("[1/4] Master Pipeline 임포트 테스트...")
        from master_pipeline import NeoGodUltraPipeline
        print("✓ Master Pipeline 임포트 성공")
        print()
        
        # Pipeline 초기화 테스트
        print("[2/4] Pipeline 초기화 테스트...")
        pipeline = NeoGodUltraPipeline(str(config_file))
        print("✓ Pipeline 초기화 성공")
        print()
        
        # 각 Phase 모듈 임포트 테스트
        print("[3/4] Phase 모듈 임포트 테스트...")
        from phase1_scouting import scout_with_fallback
        from phase2_extraction import PhysicalDualTrackExtractor
        from phase3_normalization import DateFirstNormalizer
        from phase4_load import StagingTableLoader
        print("✓ 모든 Phase 모듈 임포트 성공")
        print()
        
        # 실제 실행 여부 확인
        print("[4/4] 실행 준비 확인...")
        print("⚠ 실제 파이프라인 실행은 다음 명령으로 수행하세요:")
        print("   python master_pipeline.py --config config.yaml")
        print()
        print("⚠ 주의: 실제 실행 시 BigQuery에 데이터가 적재됩니다!")
        print()
        
        # 검증 체크리스트
        print("=" * 60)
        print("검증 체크리스트")
        print("=" * 60)
        
        checks = {
            'config.yaml 존재': config_file.exists(),
            '소스 파일 존재': source_file.exists(),
            'Phase 1 모듈': True,  # 이미 임포트 성공
            'Phase 2 모듈': True,
            'Phase 3 모듈': True,
            'Phase 4 모듈': True,
            'Master Pipeline 모듈': True,
        }
        
        for check, status in checks.items():
            status_str = "✓" if status else "✗"
            print(f"{status_str} {check}")
        
        all_passed = all(checks.values())
        
        print()
        if all_passed:
            print("✓ 모든 검증 통과!")
            print()
            print("다음 단계:")
            print("1. requirements.txt의 패키지 설치 확인")
            print("2. BigQuery 인증 파일 확인 (neoprime-admin-key.json)")
            print("3. python master_pipeline.py --config config.yaml 실행")
        else:
            print("✗ 일부 검증 실패")
        
        return all_passed
        
    except Exception as e:
        print(f"✗ 통합 테스트 실패: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_dependencies():
    """의존성 패키지 확인"""
    print("=" * 60)
    print("의존성 패키지 확인")
    print("=" * 60)
    print()

    # 필수 패키지
    required_packages = {
        'pandas': 'pandas>=2.2.0',
        'openpyxl': 'openpyxl>=3.1.0',
        'pyarrow': 'pyarrow>=14.0.0',
        'psutil': 'psutil>=5.9.0',
        'yaml': 'pyyaml>=6.0',
        'google.cloud.bigquery': 'google-cloud-bigquery>=3.11.0',
    }

    # 선택적 패키지 (폴백 있음)
    optional_packages = {
        'python_calamine': 'python-calamine>=0.6.0'
    }

    results = {}

    # 필수 패키지 확인
    print("[필수 패키지]")
    for module_name, package_name in required_packages.items():
        try:
            if module_name == 'yaml':
                import yaml
            elif module_name == 'google.cloud.bigquery':
                from google.cloud import bigquery
            else:
                __import__(module_name)

            # 버전 확인
            if module_name == 'pandas':
                import pandas
                version = pandas.__version__
            elif module_name == 'yaml':
                import yaml
                version = getattr(yaml, '__version__', 'unknown')
            else:
                mod = __import__(module_name)
                version = getattr(mod, '__version__', 'unknown')

            results[package_name] = {'installed': True, 'version': version, 'required': True}
            print(f"✓ {package_name}: {version}")

        except ImportError:
            results[package_name] = {'installed': False, 'version': None, 'required': True}
            print(f"✗ {package_name}: 설치되지 않음")

    # 선택적 패키지 확인
    print()
    print("[선택적 패키지 (폴백 있음)]")
    for module_name, package_name in optional_packages.items():
        try:
            if module_name == 'python_calamine':
                from python_calamine import CalamineWorkbook
                version = 'installed'
            else:
                mod = __import__(module_name)
                version = getattr(mod, '__version__', 'unknown')

            results[package_name] = {'installed': True, 'version': version, 'required': False}
            print(f"✓ {package_name}: {version}")

        except ImportError:
            results[package_name] = {'installed': False, 'version': None, 'required': False}
            print(f"⚠ {package_name}: 미설치 (openpyxl 폴백 사용)")

    print()

    # 필수 패키지만 확인
    required_installed = all(r['installed'] for r in results.values() if r.get('required', True))

    if not required_installed:
        print("설치되지 않은 필수 패키지:")
        for pkg, info in results.items():
            if not info['installed'] and info.get('required', True):
                print(f"  - {pkg}")
        print()
        print("다음 명령으로 설치하세요:")
        print("  pip install -r requirements.txt")

    return required_installed


if __name__ == '__main__':
    print()
    
    # 의존성 확인
    deps_ok = test_dependencies()
    print()
    
    # 통합 테스트
    integration_ok = test_integration()
    print()
    
    # 최종 결과
    print("=" * 60)
    print("최종 결과")
    print("=" * 60)
    
    if deps_ok and integration_ok:
        print("✓ 모든 테스트 통과!")
        sys.exit(0)
    else:
        print("✗ 일부 테스트 실패")
        if not deps_ok:
            print("  - 의존성 패키지 설치 필요")
        if not integration_ok:
            print("  - 통합 테스트 실패")
        sys.exit(1)
