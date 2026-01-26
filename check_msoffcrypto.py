#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
msoffcrypto-tool 설치 여부 확인 스크립트
"""

import sys
import os

# 출력 인코딩 설정
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

def main():
    print("=" * 60)
    print("msoffcrypto-tool 설치 여부 확인")
    print("=" * 60)
    
    try:
        import msoffcrypto
        version = getattr(msoffcrypto, '__version__', '버전 정보 없음')
        print(f"[OK] msoffcrypto-tool: 설치됨 (버전: {version})")
        print("=" * 60)
        return True
    except ImportError:
        print("[WARN] msoffcrypto-tool: 설치되지 않음")
        print()
        print("설치 방법:")
        print("  pip install msoffcrypto-tool")
        print()
        print("또는 requirements.txt에 추가 후:")
        print("  pip install -r requirements.txt")
        print("=" * 60)
        return False

if __name__ == '__main__':
    main()
