# Python 사용 가이드

## 문제 상황
PowerShell에서 `python` 명령어를 인식하지 못하는 경우

## 해결 방법

### 방법 1: run_system.bat 실행 (권장)

**PowerShell에서 실행**:
```powershell
# run_system.bat 실행
cd Y:\0126
.\run_system.bat
```

**또는 직접 경로 지정**:
```powershell
Y:\0126\run_system.bat
```

이렇게 하면 Python 경로가 자동으로 설정됩니다.

### 방법 2: 전체 경로 사용

**Python 전체 경로로 실행**:
```powershell
# pandas 확인
Y:\0126\python_env.env\python.exe -c "import pandas; print(f'pandas 버전: {pandas.__version__}')"

# 체크 스크립트 실행
Y:\0126\python_env.env\python.exe check_pandas.py

# uploader.py 실행
Y:\0126\python_env.env\python.exe uploader.py data.xlsx --table entrance_data --project neoprime0305
```

### 방법 3: PowerShell에서 PATH 임시 설정

**현재 세션에서만 PATH 설정**:
```powershell
# PATH에 Python 추가
$env:PATH = "Y:\0126\python_env.env;Y:\0126\python_env.env\Scripts;" + $env:PATH

# 이제 python 명령어 사용 가능
python --version
python check_pandas.py
```

### 방법 4: PowerShell 별칭(Alias) 생성

**현재 세션에서 별칭 생성**:
```powershell
# python 별칭 생성
Set-Alias python "Y:\0126\python_env.env\python.exe"

# 확인
python --version
python check_pandas.py
```

## 권장 워크플로우

### 1단계: run_system.bat 실행
```powershell
cd Y:\0126
.\run_system.bat
```

### 2단계: 새로 열린 명령 프롬프트에서 작업
- run_system.bat이 새로운 cmd 창을 열면 그 창에서 작업
- Python, Node.js, Git 등 모든 도구가 PATH에 설정됨

### 3단계: pandas 확인
```cmd
python check_pandas.py
```

### 4단계: 업로더 실행
```cmd
python uploader.py <엑셀파일> --table entrance_data --project neoprime0305
```

## 빠른 참조

### Python 경로
- **실행 파일**: `Y:\0126\python_env.env\python.exe`
- **버전**: Python 3.14.2

### 주요 명령어
```powershell
# 전체 경로 사용
Y:\0126\python_env.env\python.exe --version
Y:\0126\python_env.env\python.exe check_pandas.py
Y:\0126\python_env.env\python.exe uploader.py --help
```

### pip 사용
```powershell
# 전체 경로로 pip 실행
Y:\0126\python_env.env\Scripts\pip.exe list
Y:\0126\python_env.env\Scripts\pip.exe install -r requirements.txt
```
