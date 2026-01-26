#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
neoprime-admin-key.json 파일 상태 확인 스크립트
"""

import os
import json

def check_json_file():
    """JSON 파일 상세 확인"""
    key_file = "neoprime-admin-key.json"
    
    print("=" * 60)
    print("JSON 파일 상세 확인")
    print("=" * 60)
    
    # 파일 존재 확인
    if not os.path.exists(key_file):
        print(f"❌ 파일이 존재하지 않습니다: {key_file}")
        return False
    
    print(f"✅ 파일 존재: {key_file}")
    
    # 파일 크기 확인
    file_size = os.path.getsize(key_file)
    print(f"📏 파일 크기: {file_size} bytes")
    
    if file_size == 0:
        print("❌ 파일이 비어있습니다!")
        return False
    
    # 파일 내용 읽기 시도 (여러 인코딩)
    print("\n인코딩별 읽기 시도:")
    print("-" * 60)
    
    encodings = ['utf-8', 'utf-8-sig', 'latin-1', 'cp949']
    
    for encoding in encodings:
        try:
            with open(key_file, 'r', encoding=encoding) as f:
                content = f.read()
            
            print(f"\n[{encoding}]")
            print(f"  읽은 길이: {len(content)} 문자")
            
            if not content.strip():
                print("  ⚠️ 내용이 비어있습니다")
                continue
            
            # 첫 100자 출력
            preview = content[:100].replace('\n', '\\n')
            print(f"  시작 부분: {preview}...")
            
            # JSON 파싱 시도
            try:
                key_data = json.loads(content)
                print(f"  ✅ JSON 파싱 성공!")
                print(f"  프로젝트 ID: {key_data.get('project_id', 'N/A')}")
                print(f"  서비스 계정: {key_data.get('client_email', 'N/A')}")
                return True
            except json.JSONDecodeError as e:
                print(f"  ❌ JSON 파싱 실패: {str(e)}")
                print(f"  오류 위치: line {e.lineno}, column {e.colno}")
                
        except UnicodeDecodeError as e:
            print(f"\n[{encoding}]")
            print(f"  ❌ 인코딩 오류: {str(e)}")
        except Exception as e:
            print(f"\n[{encoding}]")
            print(f"  ❌ 예상치 못한 오류: {str(e)}")
    
    # 바이너리 모드로 확인
    print("\n" + "-" * 60)
    print("바이너리 모드 확인:")
    try:
        with open(key_file, 'rb') as f:
            raw_content = f.read(200)
        print(f"  처음 200바이트 (hex): {raw_content.hex()[:100]}...")
        print(f"  처음 200바이트 (repr): {repr(raw_content[:100])}")
        
        # BOM 확인
        if raw_content.startswith(b'\xef\xbb\xbf'):
            print("  ⚠️ UTF-8 BOM 발견")
        elif raw_content.startswith(b'\xff\xfe'):
            print("  ⚠️ UTF-16 LE BOM 발견")
        elif raw_content.startswith(b'\xfe\xff'):
            print("  ⚠️ UTF-16 BE BOM 발견")
    except Exception as e:
        print(f"  ❌ 바이너리 읽기 실패: {str(e)}")
    
    return False

if __name__ == '__main__':
    result = check_json_file()
    print("\n" + "=" * 60)
    if result:
        print("✅ JSON 파일이 정상입니다!")
    else:
        print("❌ JSON 파일에 문제가 있습니다.")
        print("\n해결 방법:")
        print("1. 파일이 손상되었을 수 있습니다.")
        print("2. 파일을 다시 다운로드하거나 복사하세요.")
        print("3. 파일 인코딩이 UTF-8인지 확인하세요.")
    print("=" * 60)
