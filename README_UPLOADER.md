# BigQuery Excel Uploader

20만 건의 엑셀 데이터를 GCP BigQuery `entrance_exam` 데이터셋에 업로드하는 Python 스크립트입니다.

## 사전 요구사항

### 1. Python 환경
- Python 3.8 이상
- 가상환경 권장 (Y:\0126\python_env.env)

### 2. GCP 인증 설정

**기본 설정**: 스크립트는 자동으로 `neoprime-admin-key.json` 파일을 사용합니다.
- 파일이 스크립트와 같은 디렉토리에 있으면 자동으로 감지됩니다.
- 별도의 인증 설정 없이 바로 사용 가능합니다.

**다른 서비스 계정 키 사용**:
```bash
python uploader.py data.xlsx --table entrance_data --credentials other-key.json
```

**참고**: 기본 인증이 실패할 경우에만 다음 방법을 사용하세요:
```bash
gcloud auth application-default login
```

### 3. Python 패키지 설치
```bash
pip install -r requirements.txt
```

## 사용법

### 기본 사용
```bash
python uploader.py <엑셀파일경로> --table <테이블명> --project neoprime0305
```

### 예시
```bash
# 기본 업로드 (neoprime-admin-key.json 자동 사용)
python uploader.py data.xlsx --table entrance_data --project neoprime0305

# 특정 시트 지정
python uploader.py data.xlsx --table entrance_data --project neoprime0305 --sheet "Sheet1"

# 기존 테이블 덮어쓰기
python uploader.py data.xlsx --table entrance_data --project neoprime0305 --mode truncate

# 다른 서비스 계정 키 사용 (기본값 무시)
python uploader.py data.xlsx --table entrance_data --project neoprime0305 --credentials other-key.json

# 청크 크기 조정 (대용량 파일)
python uploader.py data.xlsx --table entrance_data --project neoprime0305 --chunk-size 50000
```

## 명령줄 옵션

| 옵션 | 설명 | 기본값 |
|------|------|--------|
| `--project` | GCP 프로젝트 ID | `neoprime0305` |
| `--dataset` | BigQuery 데이터셋 ID | `entrance_exam` |
| `--table` | BigQuery 테이블 ID | (필수) |
| `--sheet` | 엑셀 시트 이름 | 첫 번째 시트 |
| `--mode` | 쓰기 모드 (`append`, `truncate`, `empty`) | `append` |
| `--credentials` | 서비스 계정 키 파일 경로 | `neoprime-admin-key.json` (자동) |
| `--chunk-size` | 청크 크기 (행 수) | `10000` |

## 기능

- ✅ 대용량 엑셀 파일 처리 (청크 단위 업로드)
- ✅ 자동 스키마 추론
- ✅ 데이터 타입 자동 변환
- ✅ 진행 상황 로깅
- ✅ 에러 처리 및 복구
- ✅ Parquet 형식 사용으로 빠른 업로드
- ✅ UTF-8 인코딩 지원 (한글 데이터 처리)

## 로그 파일

업로드 과정은 `uploader.log` 파일에 기록됩니다.

## 주의사항

1. **WRITE_TRUNCATE 모드**: 기존 테이블의 모든 데이터가 삭제됩니다.
2. **청크 크기**: 메모리와 네트워크 상황에 따라 조정하세요.
3. **인증**: GCP 프로젝트에 BigQuery 권한이 필요합니다.
4. **데이터 타입**: 자동 추론되지만 필요시 수동 스키마 지정 가능합니다.

## 문제 해결

### 인증 오류
1. `neoprime-admin-key.json` 파일이 스크립트와 같은 디렉토리에 있는지 확인
2. 서비스 계정에 BigQuery 권한이 있는지 확인
3. 필요시 다른 서비스 계정 키 사용:
   ```bash
   python uploader.py data.xlsx --table entrance_data --credentials key.json
   ```
4. 마지막 수단으로 기본 인증 사용:
   ```bash
   gcloud auth application-default login
   ```

### 패키지 설치 오류
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 메모리 부족
`--chunk-size` 값을 줄이세요 (예: 5000)
