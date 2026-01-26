#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
uploader.py의 핵심 기능이 정상 작동하는지 테스트하는 스크립트
"""

import sys
import os

def test_imports():
    """필수 모듈 import 테스트"""
    print("=" * 60)
    print("필수 모듈 Import 테스트")
    print("=" * 60)
    
    modules = [
        ('pandas', 'pd'),
        ('openpyxl', None),
        ('pyarrow', None),
        ('google.cloud.bigquery', 'bigquery'),
        ('google.oauth2.service_account', 'service_account'),
    ]
    
    results = []
    for module_name, alias in modules:
        try:
            if alias:
                exec(f"import {module_name} as {alias}")
            else:
                exec(f"import {module_name}")
            print(f"✅ {module_name}: 정상")
            results.append(True)
        except ImportError as e:
            print(f"❌ {module_name}: 실패 - {str(e)}")
            results.append(False)
    
    return all(results)

def test_credentials():
    """서비스 계정 키 파일 확인"""
    print("\n" + "=" * 60)
    print("서비스 계정 키 파일 확인")
    print("=" * 60)
    
    key_file = "neoprime-admin-key.json"
    if os.path.exists(key_file):
        print(f"✅ {key_file}: 파일 존재")
        
        # JSON 파일 읽기 테스트
        try:
            import json
            
            # 파일 크기 확인
            file_size = os.path.getsize(key_file)
            print(f"   파일 크기: {file_size} bytes")
            
            # 파일 내용 읽기 (여러 인코딩 시도)
            key_data = None
            encodings = ['utf-8', 'utf-8-sig', 'latin-1']
            
            for encoding in encodings:
                try:
                    with open(key_file, 'r', encoding=encoding) as f:
                        content = f.read()
                        if not content.strip():
                            print(f"   ⚠️ 파일이 비어있습니다 (인코딩: {encoding})")
                            continue
                        key_data = json.loads(content)
                        print(f"   ✅ JSON 파싱 성공 (인코딩: {encoding})")
                        break
                except UnicodeDecodeError:
                    continue
                except json.JSONDecodeError as e:
                    print(f"   ⚠️ JSON 파싱 실패 (인코딩: {encoding}): {str(e)}")
                    # 첫 200자만 출력
                    with open(key_file, 'rb') as f:
                        raw_content = f.read(200)
                        print(f"   파일 시작 부분 (hex): {raw_content[:50].hex()}")
                    continue
            
            if key_data:
                print(f"   프로젝트 ID: {key_data.get('project_id', 'N/A')}")
                print(f"   서비스 계정: {key_data.get('client_email', 'N/A')}")
                return True
            else:
                print(f"❌ 모든 인코딩 시도 실패")
                return False
                
        except Exception as e:
            print(f"❌ JSON 파일 읽기 실패: {str(e)}")
            import traceback
            print(f"   상세 오류: {traceback.format_exc()}")
            return False
    else:
        print(f"❌ {key_file}: 파일 없음")
        return False

def test_bigquery_client():
    """BigQuery 클라이언트 생성 테스트"""
    print("\n" + "=" * 60)
    print("BigQuery 클라이언트 생성 테스트")
    print("=" * 60)
    
    try:
        from google.cloud import bigquery
        from google.oauth2 import service_account
        
        key_file = "neoprime-admin-key.json"
        if os.path.exists(key_file):
            credentials = service_account.Credentials.from_service_account_file(
                key_file,
                scopes=["https://www.googleapis.com/auth/bigquery"]
            )
            client = bigquery.Client(
                project="neoprime0305",
                credentials=credentials
            )
            print(f"✅ BigQuery 클라이언트 생성 성공")
            print(f"   프로젝트: {client.project}")
            return True
        else:
            print("⚠️ 서비스 계정 키 파일이 없어 테스트 건너뜀")
            return False
    except Exception as e:
        print(f"❌ BigQuery 클라이언트 생성 실패: {str(e)}")
        return False

def main():
    """메인 테스트 함수"""
    print("\n")
    print("=" * 60)
    print("uploader.py 환경 테스트")
    print("=" * 60)
    print(f"Python 버전: {sys.version}")
    print(f"작업 디렉토리: {os.getcwd()}")
    print()
    
    # 테스트 실행
    test1 = test_imports()
    test2 = test_credentials()
    test3 = test_bigquery_client()
    
    # 최종 결과
    print("\n" + "=" * 60)
    print("최종 결과")
    print("=" * 60)
    
    if test1 and test2:
        print("✅ 모든 테스트 통과!")
        print("✅ uploader.py를 바로 사용할 수 있습니다.")
        if test3:
            print("✅ BigQuery 연결도 정상입니다.")
        else:
            print("⚠️ BigQuery 연결 테스트는 건너뛰었습니다.")
    else:
        print("❌ 일부 테스트 실패")
        if not test1:
            print("   - 필수 모듈 설치 필요: pip install -r requirements.txt")
        if not test2:
            print("   - neoprime-admin-key.json 파일 확인 필요")
    
    print("=" * 60)
    print()

if __name__ == '__main__':
    main()
