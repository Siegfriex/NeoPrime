# Excel "값으로 붙여넣기" 재적재 로드맵

**목적**: COMPUTE 테이블의 수식을 실제 계산된 값으로 변환하여 BigQuery에 재적재

---

## 1. 현재 문제 분석

### 1.1 현상
```
COMPUTE 테이블 조회 결과:
┌─────────────┬─────────┬─────────┬─────────┐
│ column_271  │ row 58  │ row 59  │ row 60  │
│ (서울대)    │ (국어)  │ (수학)  │ (영어)  │
├─────────────┼─────────┼─────────┼─────────┤
│ 값          │ 0.0     │ NaN     │ 0.0     │
└─────────────┴─────────┴─────────┴─────────┘
```

### 1.2 원인
```
[Excel 파일 구조]
┌─────────────────────────────────────────┐
│ COMPUTE 시트                            │
├─────────────────────────────────────────┤
│ 셀 JL58 = "=RAWSCORE!B58*가중치..."     │ ← 수식 (문자열)
│ 셀 JL59 = "=RAWSCORE!B59*가중치..."     │
│ ...                                     │
└─────────────────────────────────────────┘
         ↓ openpyxl로 추출 시
┌─────────────────────────────────────────┐
│ data_only=False: 수식 문자열 추출       │
│ data_only=True:  캐시된 값 (없으면 None)│
└─────────────────────────────────────────┘
```

**핵심 원인**: Excel 파일이 마지막으로 저장될 때 수식이 평가되지 않았거나, 입력 데이터가 없는 상태에서 저장됨

---

## 2. 솔루션 개요

### 2.1 방법 A: 수동 변환 (권장 - 가장 확실)
```
Excel에서 직접 "값으로 붙여넣기" 실행 후 저장
```

### 2.2 방법 B: Python 자동화 (win32com 사용)
```
Python으로 Excel 열기 → 수식 계산 → 값으로 변환 → 저장
```

### 2.3 방법 C: 하이브리드
```
테스트 데이터 입력 → Excel 저장 → Python 재적재
```

---

## 3. 방법 A: 수동 변환 로드맵

### Step 1: Excel 파일 백업
```powershell
# 원본 백업
copy "Y:\0126\0126\202511고속성장분석기(가채점)20251114.xlsx" `
     "Y:\0126\0126\backup\202511고속성장분석기_원본_backup.xlsx"
```

### Step 2: Excel에서 테스트 데이터 입력
```
[수능입력 시트]
┌─────────┬─────────┬─────────┐
│ 영역    │ 과목    │ 점수    │
├─────────┼─────────┼─────────┤
│ 국어    │ 화작    │ 131     │ ← 입력
│ 국어    │ 언매    │ 134     │ ← 입력
│ 수학    │ 미적분  │ 140     │ ← 입력
│ 영어    │ -       │ 1       │ ← 등급 입력
│ 탐구1   │ 물리1   │ 68      │ ← 입력
│ 탐구2   │ 화학1   │ 65      │ ← 입력
│ 한국사  │ -       │ 1       │ ← 등급 입력
└─────────┴─────────┴─────────┘
```

### Step 3: 수식 계산 확인
```
1. COMPUTE 시트 이동
2. 수식 재계산: Ctrl + Shift + F9
3. 값이 0이 아닌 숫자로 변경되었는지 확인
```

### Step 4: 값으로 붙여넣기 (핵심)
```
[COMPUTE 시트에서]
1. Ctrl + A (전체 선택)
2. Ctrl + C (복사)
3. 마우스 우클릭 → 선택하여 붙여넣기 → "값" (V)
   또는: Ctrl + Alt + V → "값" 선택 → 확인

[이과계열분석결과 시트에서]
1. 동일하게 반복

[문과계열분석결과 시트에서]
1. 동일하게 반복
```

### Step 5: 새 파일로 저장
```
파일 → 다른 이름으로 저장
파일명: 202511고속성장분석기_값변환_20260126.xlsx
```

### Step 6: 파이프라인 재실행
```powershell
cd Y:\0126\0126

# config.yaml 수정 (새 파일 경로)
# source_file: "Y:\\0126\\0126\\202511고속성장분석기_값변환_20260126.xlsx"

python master_pipeline.py --config config.yaml
```

---

## 4. 방법 B: Python 자동화 파이프라인

### 4.1 전체 흐름도
```
┌─────────────────────────────────────────────────────────────┐
│                  자동화 파이프라인                           │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  [Phase 0] 원본 백업                                        │
│      │                                                      │
│      ▼                                                      │
│  [Phase 1] Excel 열기 (win32com)                            │
│      │                                                      │
│      ▼                                                      │
│  [Phase 2] 테스트 데이터 입력 (선택)                         │
│      │                                                      │
│      ▼                                                      │
│  [Phase 3] 수식 강제 재계산                                  │
│      │     Application.CalculateFull()                      │
│      ▼                                                      │
│  [Phase 4] 대상 시트 "값으로 붙여넣기"                       │
│      │     - COMPUTE                                        │
│      │     - 이과계열분석결과                                │
│      │     - 문과계열분석결과                                │
│      ▼                                                      │
│  [Phase 5] 새 파일 저장                                      │
│      │                                                      │
│      ▼                                                      │
│  [Phase 6] 기존 파이프라인 실행                              │
│      │     master_pipeline.py                               │
│      ▼                                                      │
│  [Phase 7] BigQuery 적재 검증                                │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 4.2 구현 코드

```python
# excel_value_converter.py
"""
Excel 수식 → 값 변환 자동화 스크립트
Windows 전용 (win32com 필요)
"""

import os
import shutil
from datetime import datetime
from pathlib import Path

# Windows COM 인터페이스
import win32com.client as win32
from win32com.client import constants


class ExcelValueConverter:
    """Excel 수식을 값으로 변환"""

    def __init__(self, source_path: str, output_dir: str = './output'):
        self.source_path = Path(source_path).resolve()
        self.output_dir = Path(output_dir)
        self.excel = None
        self.workbook = None

        # 변환 대상 시트
        self.target_sheets = [
            'COMPUTE',
            '이과계열분석결과',
            '문과계열분석결과',
        ]

    def run(self, test_data: dict = None) -> str:
        """
        전체 변환 프로세스 실행

        Args:
            test_data: 테스트 점수 데이터 (선택)

        Returns:
            새 파일 경로
        """
        print("=" * 60)
        print("Excel 값 변환 파이프라인")
        print("=" * 60)

        try:
            # Phase 0: 백업
            self._backup_original()

            # Phase 1: Excel 열기
            self._open_excel()

            # Phase 2: 테스트 데이터 입력 (선택)
            if test_data:
                self._input_test_data(test_data)

            # Phase 3: 수식 재계산
            self._recalculate()

            # Phase 4: 값으로 붙여넣기
            self._convert_to_values()

            # Phase 5: 새 파일 저장
            new_path = self._save_as_new()

            # Phase 6: 정리
            self._cleanup()

            print("\n" + "=" * 60)
            print(f"[완료] 새 파일: {new_path}")
            print("=" * 60)

            return new_path

        except Exception as e:
            print(f"\n[오류] {e}")
            self._cleanup()
            raise

    def _backup_original(self):
        """원본 파일 백업"""
        print("\n[Phase 0] 원본 백업...")

        backup_dir = self.source_path.parent / 'backup'
        backup_dir.mkdir(exist_ok=True)

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_name = f"{self.source_path.stem}_backup_{timestamp}.xlsx"
        backup_path = backup_dir / backup_name

        shutil.copy2(self.source_path, backup_path)
        print(f"  - 백업 완료: {backup_path}")

    def _open_excel(self):
        """Excel 애플리케이션 열기"""
        print("\n[Phase 1] Excel 열기...")

        self.excel = win32.gencache.EnsureDispatch('Excel.Application')
        self.excel.Visible = False  # 백그라운드 실행
        self.excel.DisplayAlerts = False

        self.workbook = self.excel.Workbooks.Open(str(self.source_path))
        print(f"  - 파일 열림: {self.source_path.name}")
        print(f"  - 시트 수: {self.workbook.Sheets.Count}")

    def _input_test_data(self, test_data: dict):
        """테스트 데이터 입력"""
        print("\n[Phase 2] 테스트 데이터 입력...")

        sheet = self.workbook.Sheets('수능입력')

        # 테스트 데이터 매핑 (셀 주소: 값)
        # 실제 셀 주소는 시트 구조에 따라 조정 필요
        cell_mapping = {
            'C8': test_data.get('국어_화작', 131),
            'C9': test_data.get('국어_언매', 134),
            'C11': test_data.get('수학', 140),
            'C13': test_data.get('영어', 1),
            'C15': test_data.get('탐구1', 68),
            'C16': test_data.get('탐구2', 65),
            'C18': test_data.get('한국사', 1),
        }

        for cell, value in cell_mapping.items():
            sheet.Range(cell).Value = value
            print(f"  - {cell} = {value}")

    def _recalculate(self):
        """수식 강제 재계산"""
        print("\n[Phase 3] 수식 재계산...")

        self.excel.CalculateFull()
        print("  - 전체 수식 재계산 완료")

    def _convert_to_values(self):
        """대상 시트를 값으로 변환"""
        print("\n[Phase 4] 값으로 붙여넣기...")

        for sheet_name in self.target_sheets:
            try:
                sheet = self.workbook.Sheets(sheet_name)
                used_range = sheet.UsedRange

                # 복사
                used_range.Copy()

                # 값으로 붙여넣기
                used_range.PasteSpecial(Paste=constants.xlPasteValues)

                # 클립보드 정리
                self.excel.CutCopyMode = False

                print(f"  - {sheet_name}: 변환 완료")
                print(f"    범위: {used_range.Address}")

            except Exception as e:
                print(f"  - {sheet_name}: 오류 - {e}")

    def _save_as_new(self) -> str:
        """새 파일로 저장"""
        print("\n[Phase 5] 새 파일 저장...")

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        new_name = f"{self.source_path.stem}_값변환_{timestamp}.xlsx"
        new_path = self.source_path.parent / new_name

        self.workbook.SaveAs(str(new_path))
        print(f"  - 저장 완료: {new_path}")

        return str(new_path)

    def _cleanup(self):
        """리소스 정리"""
        print("\n[Phase 6] 정리...")

        if self.workbook:
            self.workbook.Close(SaveChanges=False)
        if self.excel:
            self.excel.Quit()

        print("  - Excel 종료")


def main():
    """메인 실행"""
    source_file = r"Y:\0126\0126\202511고속성장분석기(가채점)20251114.xlsx"

    # 테스트 데이터 (상위권 학생 예시)
    test_data = {
        '국어_화작': 131,
        '국어_언매': 134,
        '수학': 140,
        '영어': 1,
        '탐구1': 68,
        '탐구2': 65,
        '한국사': 1,
    }

    converter = ExcelValueConverter(source_file)
    new_file = converter.run(test_data=test_data)

    print(f"\n다음 단계:")
    print(f"1. config.yaml의 source_file을 '{new_file}'로 변경")
    print(f"2. python master_pipeline.py 실행")


if __name__ == '__main__':
    main()
```

---

## 5. 전체 통합 파이프라인

### 5.1 파이프라인 스크립트

```python
# reload_pipeline.py
"""
전체 재적재 파이프라인
1. Excel 값 변환
2. BigQuery 기존 테이블 삭제
3. 파이프라인 재실행
4. 검증
"""

import os
import sys
import yaml
from pathlib import Path


def run_full_reload():
    """전체 재적재 실행"""

    print("=" * 70)
    print("NEO GOD Ultra v2.3 - 전체 재적재 파이프라인")
    print("=" * 70)

    # Step 1: Excel 값 변환
    print("\n[Step 1/4] Excel 값 변환...")
    from excel_value_converter import ExcelValueConverter

    source_file = r"Y:\0126\0126\202511고속성장분석기(가채점)20251114.xlsx"
    converter = ExcelValueConverter(source_file)

    test_data = {
        '국어_화작': 131,
        '국어_언매': 134,
        '수학': 140,
        '영어': 1,
        '탐구1': 68,
        '탐구2': 65,
        '한국사': 1,
    }

    new_file = converter.run(test_data=test_data)

    # Step 2: config.yaml 업데이트
    print("\n[Step 2/4] config.yaml 업데이트...")
    config_path = Path('config.yaml')
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)

    config['source_file'] = new_file

    with open(config_path, 'w', encoding='utf-8') as f:
        yaml.dump(config, f, allow_unicode=True, default_flow_style=False)

    print(f"  - source_file 업데이트: {new_file}")

    # Step 3: BigQuery 기존 테이블 삭제 (선택)
    print("\n[Step 3/4] BigQuery 테이블 정리...")
    # 기존 테이블 유지 또는 삭제 선택

    # Step 4: 파이프라인 재실행
    print("\n[Step 4/4] 마스터 파이프라인 실행...")
    from master_pipeline import MasterPipeline

    pipeline = MasterPipeline(config_path='config.yaml')
    result = pipeline.run()

    # 결과 출력
    print("\n" + "=" * 70)
    print("재적재 완료")
    print("=" * 70)
    print(f"  - 적재된 행: {result.get('total_rows', 'N/A')}")
    print(f"  - 테이블 수: {result.get('tables', 'N/A')}")

    return result


if __name__ == '__main__':
    run_full_reload()
```

---

## 6. 검증 쿼리

### 6.1 BigQuery 검증

```sql
-- 1. COMPUTE 테이블 값 확인
SELECT
    column_271 as 서울대_국어,
    column_272 as 서울대_수학,
    column_273 as 서울대_영어
FROM `neoprime0305.ds_neoprime_entrance.tb_raw_2026_COMPUTE`
WHERE _row_id BETWEEN 58 AND 62;

-- 2. NULL이 아닌 값 비율 확인
SELECT
    COUNT(*) as total_rows,
    COUNTIF(column_271 IS NOT NULL AND column_271 != 0) as non_null_count,
    ROUND(COUNTIF(column_271 IS NOT NULL AND column_271 != 0) / COUNT(*) * 100, 2) as non_null_pct
FROM `neoprime0305.ds_neoprime_entrance.tb_raw_2026_COMPUTE`;

-- 3. 대학별 환산점수 합계 확인 (서울대 예시)
SELECT
    SUM(CAST(column_271 AS FLOAT64)) as 서울대_총점
FROM `neoprime0305.ds_neoprime_entrance.tb_raw_2026_COMPUTE`
WHERE _row_id BETWEEN 58 AND 62;
```

### 6.2 Python 검증

```python
# verify_reload.py
"""재적재 결과 검증"""

from google.cloud import bigquery
from google.oauth2 import service_account

def verify_compute_values():
    """COMPUTE 테이블 값 검증"""

    credentials = service_account.Credentials.from_service_account_file(
        'neoprime-loader-key.json'
    )
    client = bigquery.Client(
        credentials=credentials,
        project='neoprime0305'
    )

    # 서울대 컬럼 (인덱스 271) 값 확인
    query = """
    SELECT
        _row_id,
        column_271 as value
    FROM `neoprime0305.ds_neoprime_entrance.tb_raw_2026_COMPUTE`
    WHERE _row_id BETWEEN 58 AND 65
    ORDER BY _row_id
    """

    df = client.query(query).to_dataframe()

    print("서울대 환산점수 (row 58-65):")
    print(df)

    # NULL/0 비율 확인
    null_count = df['value'].isna().sum() + (df['value'] == 0).sum()
    total = len(df)

    print(f"\n유효 데이터 비율: {(total - null_count) / total * 100:.1f}%")

    if null_count == 0:
        print("✅ 모든 값이 유효합니다!")
        return True
    else:
        print(f"⚠️ {null_count}개의 NULL/0 값이 있습니다.")
        return False


if __name__ == '__main__':
    verify_compute_values()
```

---

## 7. 실행 체크리스트

### 7.1 수동 방법 체크리스트

- [ ] 원본 파일 백업 완료
- [ ] Excel에서 수능입력 시트에 테스트 점수 입력
- [ ] Ctrl + Shift + F9로 수식 재계산
- [ ] COMPUTE 시트 전체 선택 → 복사 → 값으로 붙여넣기
- [ ] 이과계열분석결과 시트 동일 작업
- [ ] 문과계열분석결과 시트 동일 작업
- [ ] 새 파일로 저장
- [ ] config.yaml의 source_file 경로 수정
- [ ] `python master_pipeline.py` 실행
- [ ] BigQuery 검증 쿼리 실행

### 7.2 자동화 방법 체크리스트

- [ ] `pip install pywin32` 설치 확인
- [ ] `excel_value_converter.py` 생성
- [ ] `reload_pipeline.py` 생성
- [ ] `python reload_pipeline.py` 실행
- [ ] BigQuery 검증 쿼리 실행

---

## 8. 예상 결과

### Before (현재)
```
COMPUTE 테이블:
┌─────────────┬─────────┐
│ 서울대_국어 │ 0.0     │
│ 서울대_수학 │ NaN     │
│ 서울대_영어 │ 0.0     │
│ 서울대_탐구1│ NaN     │
│ 서울대_탐구2│ 0.0     │
├─────────────┼─────────┤
│ 합계        │ 0.0     │
└─────────────┴─────────┘
```

### After (재적재 후)
```
COMPUTE 테이블:
┌─────────────┬─────────┐
│ 서울대_국어 │ 133.5   │
│ 서울대_수학 │ 140.0   │
│ 서울대_영어 │ 100.0   │
│ 서울대_탐구1│ 68.0    │
│ 서울대_탐구2│ 65.0    │
├─────────────┼─────────┤
│ 합계        │ 506.5   │
└─────────────┴─────────┘
```

---

## 9. 문제 해결

### Q1: win32com 설치 오류
```powershell
pip install pywin32
# 설치 후 아래 명령 실행
python -m pywin32_postinstall install
```

### Q2: Excel이 이미 열려 있음
```python
# 기존 Excel 프로세스 종료
import subprocess
subprocess.run(['taskkill', '/F', '/IM', 'EXCEL.EXE'], capture_output=True)
```

### Q3: 수식이 계산되지 않음
```python
# 수동 계산 모드 해제
self.excel.Calculation = constants.xlCalculationAutomatic
self.excel.CalculateFull()
```

---

**문서 끝**
