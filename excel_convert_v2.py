# ============================================================
# Excel Value Converter v2 - 안정화 버전
# ============================================================

import os
import time
from datetime import datetime

def convert_excel():
    """Excel 수식을 값으로 변환 (안정화)"""
    import win32com.client as win32
    import pythoncom

    pythoncom.CoInitialize()

    source_file = r"Y:\0126\0126\202511고속성장분석기(가채점)20251114.xlsx"

    print("=" * 60)
    print("Excel 값 변환 시작")
    print("=" * 60)
    print(f"원본: {source_file}")

    excel = None
    wb = None

    try:
        # Excel 시작
        excel = win32.DispatchEx('Excel.Application')  # 새 인스턴스
        excel.Visible = False
        excel.DisplayAlerts = False

        print("\nExcel 열기 중...")
        time.sleep(2)

        # 파일 열기
        wb = excel.Workbooks.Open(source_file)
        print(f"시트 수: {wb.Sheets.Count}")

        time.sleep(3)  # 파일 로드 대기

        # 1. 테스트 데이터 입력
        print("\n[1] 테스트 데이터 입력")
        try:
            sheet = wb.Worksheets('수능입력')
            test_data = [
                ('C8', 131),   # 국어 화작
                ('C9', 134),   # 국어 언매
                ('C11', 140),  # 수학
                ('C13', 1),    # 영어 등급
                ('C15', 68),   # 탐구1
                ('C16', 65),   # 탐구2
                ('C18', 1),    # 한국사 등급
            ]
            for cell, value in test_data:
                sheet.Range(cell).Value = value
                print(f"  {cell} = {value}")
                time.sleep(0.1)
        except Exception as e:
            print(f"  경고: {e}")

        time.sleep(2)

        # 2. 수식 재계산
        print("\n[2] 수식 재계산")
        try:
            excel.CalculateFull()
            print("  CalculateFull 완료")
            time.sleep(5)  # 계산 대기
        except Exception as e:
            print(f"  계산 오류: {e}")

        # 3. 값으로 변환
        print("\n[3] 값으로 변환")
        target_sheets = [
            'COMPUTE',
            'INDEX',
            'RAWSCORE',
            'PERCENTAGE',
            'RESTRICT',
            'SUBJECT1',
            'SUBJECT2',
            'SUBJECT3',
            '이과계열분석결과',
            '문과계열분석결과'
        ]

        for sheet_name in target_sheets:
            try:
                sheet = wb.Worksheets(sheet_name)
                used = sheet.UsedRange
                rows = used.Rows.Count
                cols = used.Columns.Count

                # 값으로 복사
                used.Copy()
                time.sleep(0.5)
                used.PasteSpecial(Paste=-4163)  # xlPasteValues
                excel.CutCopyMode = False
                time.sleep(0.5)

                print(f"  ✓ {sheet_name}: {rows:,}행 x {cols}열")
            except Exception as e:
                print(f"  ✗ {sheet_name}: {e}")

        # 4. 저장
        print("\n[4] 새 파일 저장")
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        new_file = f"Y:\\0126\\0126\\분석기_값변환_{timestamp}.xlsx"

        wb.SaveAs(new_file, FileFormat=51)
        print(f"  저장 완료: {new_file}")

        return new_file

    except Exception as e:
        print(f"\n오류 발생: {e}")
        import traceback
        traceback.print_exc()
        return None

    finally:
        try:
            if wb:
                wb.Close(SaveChanges=False)
            if excel:
                excel.Quit()
        except:
            pass
        pythoncom.CoUninitialize()


if __name__ == '__main__':
    result = convert_excel()
    if result:
        print(f"\n성공: {result}")
    else:
        print("\n실패")
