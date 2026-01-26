# ============================================================
# Excel Value Converter v3 - Late Binding
# ============================================================

import os
import time
from datetime import datetime

def convert_excel():
    """Excel 수식을 값으로 변환 (Late Binding)"""
    import win32com.client
    import pythoncom

    pythoncom.CoInitialize()

    source_file = r"Y:\0126\0126\202511고속성장분석기(가채점)20251114.xlsx"

    print("=" * 60)
    print("Excel 값 변환 v3 (Late Binding)")
    print("=" * 60)

    excel = None
    wb = None

    try:
        # Late binding 사용
        print("Excel 시작 중...")
        excel = win32com.client.Dispatch("Excel.Application")
        excel.Visible = True  # 화면에 표시
        excel.DisplayAlerts = False

        time.sleep(3)

        print(f"파일 열기: {source_file}")
        wb = excel.Workbooks.Open(source_file)
        time.sleep(5)

        print(f"시트 수: {wb.Sheets.Count}")

        # 1. 테스트 데이터 입력
        print("\n[1] 테스트 데이터 입력")
        try:
            sheet = wb.Sheets("수능입력")
            sheet.Range("C8").Value = 131   # 국어 화작
            sheet.Range("C9").Value = 134   # 국어 언매
            sheet.Range("C11").Value = 140  # 수학
            sheet.Range("C13").Value = 1    # 영어
            sheet.Range("C15").Value = 68   # 탐구1
            sheet.Range("C16").Value = 65   # 탐구2
            sheet.Range("C18").Value = 1    # 한국사
            print("  완료")
        except Exception as e:
            print(f"  경고: {e}")

        time.sleep(3)

        # 2. 수식 재계산
        print("\n[2] 수식 재계산")
        excel.Calculate()
        time.sleep(10)  # 대규모 계산 대기
        print("  완료")

        # 3. 값으로 변환
        print("\n[3] 값으로 변환")
        targets = ['COMPUTE', '이과계열분석결과', '문과계열분석결과']

        for name in targets:
            try:
                sheet = wb.Sheets(name)
                used = sheet.UsedRange
                rows = used.Rows.Count
                cols = used.Columns.Count

                # 선택하고 복사
                used.Select()
                time.sleep(1)
                used.Copy()
                time.sleep(1)

                # 값으로 붙여넣기
                sheet.Range("A1").PasteSpecial(Paste=-4163)
                time.sleep(1)

                print(f"  ✓ {name}: {rows:,}행")
            except Exception as e:
                print(f"  ✗ {name}: {e}")

        # 4. 저장
        print("\n[4] 저장")
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        new_file = f"Y:\\0126\\0126\\분석기_값변환_{timestamp}.xlsx"
        wb.SaveAs(new_file, FileFormat=51)
        print(f"  {new_file}")

        return new_file

    except Exception as e:
        print(f"\n오류: {e}")
        import traceback
        traceback.print_exc()
        return None

    finally:
        try:
            if wb:
                wb.Close(False)
            if excel:
                excel.Quit()
        except:
            pass
        pythoncom.CoUninitialize()


if __name__ == '__main__':
    result = convert_excel()
    print(f"\n결과: {result}")
