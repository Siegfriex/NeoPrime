# quick_all.ps1 사용 가이드

## 개요

`quick_all.ps1`은 모든 개발 도구 환경을 한 번에 설정하는 **유일한** PowerShell 스크립트입니다.

- ✅ Python 환경 설정
- ✅ Claude Code 설정
- ✅ Google Cloud SDK 설정
- ✅ Git 설정
- ✅ Node.js 설정
- ✅ Cursor IDE 설정

## 사용법

### 기본 사용

PowerShell에서 다음 명령어를 실행:

```powershell
cd Y:\0126\0126
.\quick_all.ps1
```

### 실행 후 사용 가능한 명령어

스크립트 실행 후 다음 명령어들을 바로 사용할 수 있습니다:

#### Python 관련
```powershell
python --version              # Python 버전 확인
python check_pandas.py       # 패키지 설치 확인
python test_uploader.py       # 전체 환경 테스트
python uploader.py ...        # BigQuery 업로더 실행
pip list                      # 설치된 패키지 목록
```

#### 기타 도구
```powershell
claude.cmd                    # Claude Code CLI 실행
gcloud                        # Google Cloud SDK
git                           # Git 버전 관리
node                          # Node.js 실행
```

## 주요 기능

### 1. 자동 환경 설정
- Python 경로 자동 설정
- 모든 도구의 PATH 자동 추가
- 작업 디렉토리 자동 이동

### 2. 환경 검증
스크립트 실행 시 다음을 자동으로 확인:
- Python 설치 여부 및 버전
- 필수 패키지(pandas) 설치 여부
- Claude Code 설치 여부
- Google Cloud SDK 설치 여부
- Git 설치 여부
- Node.js 설치 여부
- 서비스 계정 키 파일 존재 여부

### 3. 한글 지원
- UTF-8 인코딩 자동 설정
- 한글 데이터 처리 지원

## 주의사항

### 세션 제한
- 이 스크립트는 **현재 PowerShell 세션에서만** 유효합니다.
- 새 PowerShell 창을 열면 다시 실행해야 합니다.

### 대안
영구적으로 사용하려면:
- `run_system.bat` 실행 후 cmd 창에서 작업
- 또는 매번 `quick_all.ps1` 실행

## 빠른 시작

```powershell
# 1. 작업 디렉토리로 이동
cd Y:\0126\0126

# 2. 환경 설정 실행
.\quick_all.ps1

# 3. 환경 확인
python check_pandas.py

# 4. BigQuery 업로더 실행
python uploader.py data.xlsx --table entrance_data --project neoprime0305
```

## 문제 해결

### Python 명령어가 인식되지 않는 경우
- `quick_all.ps1`을 다시 실행하세요.
- 새 PowerShell 창을 열었는지 확인하세요.

### 패키지가 설치되지 않은 경우
```powershell
pip install -r requirements.txt
```

### 서비스 계정 키 파일이 없는 경우
- `neoprime-admin-key.json` 파일이 `Y:\0126\0126` 폴더에 있는지 확인하세요.

## 버전 정보

- **현재 버전**: 2.0
- **업데이트 내용**: Python 환경 통합 완료
- **이전 버전**: quick_python.ps1 사용 중단 (quick_all.ps1로 통합)

---

**중요**: `quick_python.ps1`은 더 이상 사용하지 마세요. `quick_all.ps1`만 사용하세요!
