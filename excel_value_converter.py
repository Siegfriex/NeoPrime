# ============================================================
# Excel Value Converter: 수식 → 값 변환 자동화
# NEO GOD Ultra Framework v2.3
# ============================================================
"""
Excel 파일의 수식을 실제 계산된 값으로 변환하여 저장합니다.
Windows 전용 (win32com 필요)

사용법:
    python excel_value_converter.py [--input 파일경로] [--with-test-data]
"""

import os
import sys
import shutil
import argparse
from datetime import datetime
from pathlib import Path

try:
    import win32com.client as win32
    from win32com.client import constants
    HAS_WIN32COM = True
except ImportError:
    HAS_WIN32COM = False
    print("[경고] pywin32가 설치되지 않았습니다.")
    print("설치: pip install pywin32")


class ExcelValueConverter:
    """Excel 수식을 값으로 변환"""

    # 변환 대상 시트
    TARGET_SHEETS = [
        'COMPUTE',
        '이과계열분석결과',
        '문과계열분석결과',
    ]

    # 테스트 데이터 (상위권 학생 예시 점수)
    DEFAULT_TEST_DATA = {
        '국어_화작': 131,      # 표준점수
        '국어_언매': 134,      # 표준점수
        '수학': 140,           # 표준점수
        '영어': 1,             # 등급
        '탐구1': 68,           # 표준점수
        '탐구2': 65,           # 표준점수
        '한국사': 1,           # 등급
    }

    def __init__(self, source_path: str, output_dir: str = None):
        """
        Args:
            source_path: 원본 Excel 파일 경로
            output_dir: 출력 디렉토리 (기본: 원본과 같은 위치)
        """
        self.source_path = Path(source_path).resolve()
        self.output_dir = Path(output_dir) if output_dir else self.source_path.parent

        if not self.source_path.exists():
            raise FileNotFoundError(f"파일을 찾을 수 없습니다: {self.source_path}")

        self.excel = None
        self.workbook = None
        self.new_file_path = None

    def run(self, test_data: dict = None, verbose: bool = True) -> str:
        """
        전체 변환 프로세스 실행

        Args:
            test_data: 테스트 점수 데이터 (None이면 입력하지 않음)
            verbose: 상세 출력 여부

        Returns:
            새 파일 경로
        """
        if not HAS_WIN32COM:
            raise RuntimeError("pywin32가 필요합니다. pip install pywin32")

        self._log("=" * 60, verbose)
        self._log("Excel 값 변환 파이프라인 시작", verbose)
        self._log("=" * 60, verbose)

        try:
            # Phase 0: 백업
            self._backup_original(verbose)

            # Phase 1: Excel 열기
            self._open_excel(verbose)

            # Phase 2: 테스트 데이터 입력 (선택)
            if test_data:
                self._input_test_data(test_data, verbose)

            # Phase 3: 수식 재계산
            self._recalculate(verbose)

            # Phase 4: 값으로 붙여넣기
            self._convert_to_values(verbose)

            # Phase 5: 새 파일 저장
            self.new_file_path = self._save_as_new(verbose)

            self._log("\n" + "=" * 60, verbose)
            self._log(f"[완료] 새 파일: {self.new_file_path}", verbose)
            self._log("=" * 60, verbose)

            return self.new_file_path

        except Exception as e:
            self._log(f"\n[오류] {e}", verbose)
            raise

        finally:
            self._cleanup(verbose)

    def _log(self, message: str, verbose: bool):
        """로그 출력"""
        if verbose:
            print(message)

    def _backup_original(self, verbose: bool):
        """원본 파일 백업"""
        self._log("\n[Phase 0] 원본 백업...", verbose)

        backup_dir = self.source_path.parent / 'backup'
        backup_dir.mkdir(exist_ok=True)

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_name = f"{self.source_path.stem}_backup_{timestamp}.xlsx"
        backup_path = backup_dir / backup_name

        shutil.copy2(self.source_path, backup_path)
        self._log(f"  - 백업 완료: {backup_path}", verbose)

    def _open_excel(self, verbose: bool):
        """Excel 애플리케이션 열기"""
        self._log("\n[Phase 1] Excel 열기...", verbose)

        # Excel COM 객체 생성
        self.excel = win32.gencache.EnsureDispatch('Excel.Application')
        self.excel.Visible = False  # 백그라운드 실행
        self.excel.DisplayAlerts = False
        self.excel.ScreenUpdating = False

        # 워크북 열기
        self.workbook = self.excel.Workbooks.Open(str(self.source_path))

        self._log(f"  - 파일 열림: {self.source_path.name}", verbose)
        self._log(f"  - 시트 수: {self.workbook.Sheets.Count}", verbose)

        # 시트 목록 출력
        sheets = [self.workbook.Sheets(i).Name for i in range(1, self.workbook.Sheets.Count + 1)]
        self._log(f"  - 시트: {sheets}", verbose)

    def _input_test_data(self, test_data: dict, verbose: bool):
        """테스트 데이터 입력"""
        self._log("\n[Phase 2] 테스트 데이터 입력...", verbose)

        try:
            sheet = self.workbook.Sheets('수능입력')
        except:
            self._log("  - [경고] '수능입력' 시트를 찾을 수 없습니다.", verbose)
            return

        # 테스트 데이터 매핑 (셀 주소는 실제 시트 구조에 따라 조정 필요)
        # 이 매핑은 예시이며, 실제 파일의 셀 위치에 맞게 수정해야 합니다
        cell_mapping = {
            # '셀주소': (데이터키, 기본값)
            'C8': ('국어_화작', 131),
            'C9': ('국어_언매', 134),
            'C11': ('수학', 140),
            'C13': ('영어', 1),
            'C15': ('탐구1', 68),
            'C16': ('탐구2', 65),
            'C18': ('한국사', 1),
        }

        for cell, (key, default) in cell_mapping.items():
            value = test_data.get(key, default)
            try:
                sheet.Range(cell).Value = value
                self._log(f"  - {cell} ({key}) = {value}", verbose)
            except Exception as e:
                self._log(f"  - {cell}: 입력 실패 - {e}", verbose)

    def _recalculate(self, verbose: bool):
        """수식 강제 재계산"""
        self._log("\n[Phase 3] 수식 재계산...", verbose)

        # 자동 계산 모드 활성화
        self.excel.Calculation = -4105  # xlCalculationAutomatic

        # 전체 워크북 재계산
        self.excel.CalculateFull()

        self._log("  - 전체 수식 재계산 완료", verbose)

    def _convert_to_values(self, verbose: bool):
        """대상 시트를 값으로 변환"""
        self._log("\n[Phase 4] 값으로 붙여넣기...", verbose)

        converted_count = 0

        for sheet_name in self.TARGET_SHEETS:
            try:
                sheet = self.workbook.Sheets(sheet_name)
                used_range = sheet.UsedRange

                # 사용된 범위 정보
                row_count = used_range.Rows.Count
                col_count = used_range.Columns.Count

                self._log(f"\n  [{sheet_name}]", verbose)
                self._log(f"    범위: {used_range.Address} ({row_count}행 x {col_count}열)", verbose)

                # 복사
                used_range.Copy()

                # 값으로 붙여넣기 (xlPasteValues = -4163)
                used_range.PasteSpecial(Paste=-4163)

                # 클립보드 정리
                self.excel.CutCopyMode = False

                self._log(f"    상태: ✅ 변환 완료", verbose)
                converted_count += 1

            except Exception as e:
                self._log(f"  [{sheet_name}]: ❌ 오류 - {e}", verbose)

        self._log(f"\n  총 {converted_count}/{len(self.TARGET_SHEETS)} 시트 변환됨", verbose)

    def _save_as_new(self, verbose: bool) -> str:
        """새 파일로 저장"""
        self._log("\n[Phase 5] 새 파일 저장...", verbose)

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        new_name = f"{self.source_path.stem}_값변환_{timestamp}.xlsx"
        new_path = self.output_dir / new_name

        # xlsx 형식으로 저장 (xlOpenXMLWorkbook = 51)
        self.workbook.SaveAs(str(new_path), FileFormat=51)

        self._log(f"  - 저장 완료: {new_path}", verbose)

        return str(new_path)

    def _cleanup(self, verbose: bool):
        """리소스 정리"""
        self._log("\n[Phase 6] 정리...", verbose)

        try:
            if self.workbook:
                self.workbook.Close(SaveChanges=False)
            if self.excel:
                self.excel.ScreenUpdating = True
                self.excel.Quit()

            # COM 객체 해제
            self.workbook = None
            self.excel = None

            self._log("  - Excel 종료 완료", verbose)

        except Exception as e:
            self._log(f"  - 정리 중 오류: {e}", verbose)


def main():
    """CLI 메인 함수"""
    parser = argparse.ArgumentParser(
        description='Excel 수식을 값으로 변환합니다.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
예시:
  python excel_value_converter.py
  python excel_value_converter.py --input "파일경로.xlsx"
  python excel_value_converter.py --with-test-data
        """
    )

    parser.add_argument(
        '--input', '-i',
        default=r"Y:\0126\0126\202511고속성장분석기(가채점)20251114.xlsx",
        help='입력 Excel 파일 경로'
    )

    parser.add_argument(
        '--output-dir', '-o',
        default=None,
        help='출력 디렉토리 (기본: 입력 파일과 같은 위치)'
    )

    parser.add_argument(
        '--with-test-data', '-t',
        action='store_true',
        help='테스트 데이터 입력 후 변환'
    )

    parser.add_argument(
        '--quiet', '-q',
        action='store_true',
        help='조용한 모드 (로그 최소화)'
    )

    args = parser.parse_args()

    # 변환 실행
    try:
        converter = ExcelValueConverter(
            source_path=args.input,
            output_dir=args.output_dir
        )

        test_data = ExcelValueConverter.DEFAULT_TEST_DATA if args.with_test_data else None

        new_file = converter.run(
            test_data=test_data,
            verbose=not args.quiet
        )

        print(f"\n{'=' * 60}")
        print("다음 단계:")
        print(f"1. config.yaml의 source_file을 아래 경로로 변경:")
        print(f"   {new_file}")
        print(f"2. 파이프라인 재실행:")
        print(f"   python master_pipeline.py")
        print(f"{'=' * 60}")

        return 0

    except Exception as e:
        print(f"\n오류 발생: {e}")
        return 1


if __name__ == '__main__':
    sys.exit(main())
