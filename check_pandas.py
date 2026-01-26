#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
pandas 및 필수 패키지 설치 여부 확인 스크립트
"""

import sys

def check_package(package_name, import_name=None):
    """패키지 설치 여부 확인"""
    if import_name is None:
        import_name = package_name
    
    try:
        module = __import__(import_name)
        version = getattr(module, '__version__', '버전 정보 없음')
        print(f"✅ {package_name}: 설치됨 (버전: {version})")
        return True
    except ImportError:
        print(f"❌ {package_name}: 설치되지 않음")
        return False

def main():
    print("=" * 60)
    print("필수 패키지 설치 여부 확인")
    print("=" * 60)
    print(f"Python 버전: {sys.version}")
    print(f"Python 경로: {sys.executable}")
    print("=" * 60)
    print()
    
    packages = [
        ('pandas', 'pandas'),
        ('openpyxl', 'openpyxl'),
        ('pyarrow', 'pyarrow'),
        ('google-cloud-bigquery', 'google.cloud.bigquery'),
        ('google-auth', 'google.auth'),
    ]
    
    results = []
    for package_name, import_name in packages:
        result = check_package(package_name, import_name)
        results.append(result)
    
    print()
    print("=" * 60)
    if all(results):
        print("✅ 모든 필수 패키지가 설치되어 있습니다!")
        print("uploader.py를 바로 사용할 수 있습니다.")
    else:
        print("❌ 일부 패키지가 설치되지 않았습니다.")
        print()
        print("설치 방법:")
        print("  pip install -r requirements.txt")
        print()
        print("또는 개별 설치:")
        missing = [pkg[0] for pkg, result in zip(packages, results) if not result]
        print(f"  pip install {' '.join(missing)}")
    print("=" * 60)

if __name__ == '__main__':
    main()
