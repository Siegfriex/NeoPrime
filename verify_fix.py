#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
파일 복구 확인 스크립트
"""

import os
import json

def verify_file():
    """파일 복구 확인"""
    key_file = "neoprime-admin-key.json"
    
    print("=" * 60)
    print("파일 복구 확인")
    print("=" * 60)
    
    # 파일 존재 및 크기 확인
    if not os.path.exists(key_file):
        print(f"❌ 파일이 존재하지 않습니다: {key_file}")
        return False
    
    file_size = os.path.getsize(key_file)
    print(f"✅ 파일 존재: {key_file}")
    print(f"📏 파일 크기: {file_size} bytes")
    
    if file_size == 0:
        print("❌ 파일이 여전히 비어있습니다!")
        return False
    
    # JSON 파싱 테스트
    try:
        with open(key_file, 'r', encoding='utf-8') as f:
            key_data = json.load(f)
        
        print("\n✅ JSON 파싱 성공!")
        print(f"   프로젝트 ID: {key_data.get('project_id', 'N/A')}")
        print(f"   서비스 계정: {key_data.get('client_email', 'N/A')}")
        print(f"   타입: {key_data.get('type', 'N/A')}")
        
        # BigQuery 클라이언트 생성 테스트
        print("\n" + "-" * 60)
        print("BigQuery 클라이언트 생성 테스트")
        print("-" * 60)
        
        from google.cloud import bigquery
        from google.oauth2 import service_account
        
        credentials = service_account.Credentials.from_service_account_file(
            key_file,
            scopes=["https://www.googleapis.com/auth/bigquery"]
        )
        client = bigquery.Client(
            project=key_data.get('project_id'),
            credentials=credentials
        )
        
        print(f"✅ BigQuery 클라이언트 생성 성공!")
        print(f"   프로젝트: {client.project}")
        
        return True
        
    except json.JSONDecodeError as e:
        print(f"\n❌ JSON 파싱 실패: {str(e)}")
        return False
    except Exception as e:
        print(f"\n❌ 오류 발생: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return False

if __name__ == '__main__':
    result = verify_file()
    print("\n" + "=" * 60)
    if result:
        print("✅ 모든 테스트 통과!")
        print("✅ neoprime-admin-key.json 파일이 정상적으로 복구되었습니다!")
        print("✅ uploader.py를 바로 사용할 수 있습니다!")
    else:
        print("❌ 파일에 여전히 문제가 있습니다.")
    print("=" * 60)
