"""
Ground Truth 수집 스크립트

xlwings COM으로 엑셀 실계산 결과를 수집하여 golden cases 생성

사용법:
    python tools/collect_ground_truth.py

출력:
    tests/fixtures/ground_truth.json

주의:
    - Windows + Excel 설치 환경에서만 동작
    - xlwings 필요
    - 1회 실행 후 JSON으로 보존 (런타임에는 JSON만 사용)
"""

import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple
import sys
import time

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 프로젝트 루트 추가
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


class GroundTruthCollector:
    """Excel 실계산 기반 Ground Truth 수집기

    다양한 입력 조합에 대해 Excel이 계산한 결과를 수집합니다.
    이 결과는 Python 엔진의 Parity Test에 사용됩니다.
    """

    # 테스트 입력 조합 (다양한 케이스 커버)
    TEST_CASES = [
        # 고득점 케이스
        {
            "name": "high_score_case1",
            "korean": 135,
            "math": 140,
            "english_grade": 1,
            "inquiry1": 68,
            "inquiry2": 65,
            "history_grade": 1,
            "inquiry1_subject": "물리학 Ⅰ",
            "inquiry2_subject": "화학 Ⅰ",
        },
        # 중간 점수 케이스
        {
            "name": "mid_score_case1",
            "korean": 120,
            "math": 125,
            "english_grade": 2,
            "inquiry1": 55,
            "inquiry2": 52,
            "history_grade": 2,
            "inquiry1_subject": "생명과학 Ⅰ",
            "inquiry2_subject": "지구과학 Ⅰ",
        },
        # 낮은 점수 케이스
        {
            "name": "low_score_case1",
            "korean": 100,
            "math": 105,
            "english_grade": 4,
            "inquiry1": 45,
            "inquiry2": 42,
            "history_grade": 4,
            "inquiry1_subject": "물리학 Ⅱ",
            "inquiry2_subject": "화학 Ⅱ",
        },
        # 문과형 (수학 낮음, 국어 높음)
        {
            "name": "liberal_arts_case1",
            "korean": 138,
            "math": 110,
            "english_grade": 1,
            "inquiry1": 60,
            "inquiry2": 58,
            "history_grade": 1,
            "inquiry1_subject": "생활과 윤리",
            "inquiry2_subject": "사회문화",
        },
        # 이과형 (수학 높음, 국어 낮음)
        {
            "name": "science_case1",
            "korean": 115,
            "math": 145,
            "english_grade": 2,
            "inquiry1": 70,
            "inquiry2": 68,
            "history_grade": 2,
            "inquiry1_subject": "물리학 Ⅰ",
            "inquiry2_subject": "화학 Ⅰ",
        },
        # 영어 낮은 케이스
        {
            "name": "low_english_case1",
            "korean": 130,
            "math": 130,
            "english_grade": 5,
            "inquiry1": 58,
            "inquiry2": 55,
            "history_grade": 2,
            "inquiry1_subject": "생명과학 Ⅰ",
            "inquiry2_subject": "지구과학 Ⅰ",
        },
        # 극단 케이스 (최고점)
        {
            "name": "max_score_case",
            "korean": 150,
            "math": 150,
            "english_grade": 1,
            "inquiry1": 75,
            "inquiry2": 75,
            "history_grade": 1,
            "inquiry1_subject": "물리학 Ⅰ",
            "inquiry2_subject": "화학 Ⅰ",
        },
        # 균형 케이스
        {
            "name": "balanced_case1",
            "korean": 125,
            "math": 125,
            "english_grade": 2,
            "inquiry1": 58,
            "inquiry2": 58,
            "history_grade": 2,
            "inquiry1_subject": "생명과학 Ⅰ",
            "inquiry2_subject": "화학 Ⅰ",
        },
    ]

    # 테스트할 대학 컬럼 (다양한 계산 방식 커버)
    TEST_UNIVERSITIES = [
        "D",   # 첫 번째 대학
        "E",
        "F",
        "G",
        "H",
        "I",
        "J",
        "K",
        "L",
        "M",   # 가천대 가천의학
        "N",   # 가천대 가천통합백
        "O",   # 가천대 가천통합표
        "Q",   # 가톨릭 간호
        "AP",  # 건국대 인문
    ]

    def __init__(self, excel_path: str):
        self.excel_path = Path(excel_path)
        self.results = []

    def collect_all(self) -> Dict:
        """전체 Ground Truth 수집

        Returns:
            ground_truth.json 형식의 데이터
        """
        try:
            import xlwings as xw
        except ImportError:
            logger.error("xlwings가 설치되지 않았습니다: pip install xlwings")
            raise

        logger.info(f"Ground Truth 수집 시작: {self.excel_path}")

        app = xw.App(visible=False)
        app.display_alerts = False
        app.screen_updating = False

        result = {
            "metadata": {
                "source_excel": str(self.excel_path.name),
                "collection_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "test_cases_count": len(self.TEST_CASES),
                "universities_count": len(self.TEST_UNIVERSITIES),
                "total_ground_truth": 0,
            },
            "test_cases": self.TEST_CASES,
            "ground_truth": [],
        }

        try:
            wb = app.books.open(str(self.excel_path))

            # 수능입력 시트
            ws_input = wb.sheets[2]  # 또는 이름으로 찾기
            # COMPUTE 시트
            ws_compute = wb.sheets['COMPUTE']

            # 각 테스트 케이스에 대해 수집
            for case in self.TEST_CASES:
                logger.info(f"케이스 처리 중: {case['name']}")

                # 1. 입력값 설정
                self._set_input_values(ws_input, case)

                # 2. 계산 대기 (엑셀 자동 계산)
                time.sleep(0.5)  # 계산 완료 대기

                # 3. 각 대학에 대해 결과 수집
                for col in self.TEST_UNIVERSITIES:
                    try:
                        gt = self._collect_university_result(
                            ws_compute, col, case
                        )
                        if gt:
                            result["ground_truth"].append(gt)
                    except Exception as e:
                        logger.warning(f"대학 {col} 수집 중 오류: {e}")
                        continue

            result["metadata"]["total_ground_truth"] = len(result["ground_truth"])

            logger.info(f"수집 완료: {len(result['ground_truth'])}개 케이스")

        except Exception as e:
            logger.error(f"수집 중 오류: {e}")
            import traceback
            traceback.print_exc()
            raise

        finally:
            try:
                wb.close()
            except:
                pass
            app.quit()

        return result

    def _set_input_values(self, ws_input, case: Dict):
        """입력 시트에 값 설정"""
        # 수능입력 시트 셀 위치 (엑셀 분석 기반)
        ws_input.range('C11').value = case["korean"]      # 국어 표준점수
        ws_input.range('C15').value = case["math"]        # 수학 표준점수
        ws_input.range('C18').value = case["english_grade"]  # 영어 등급
        ws_input.range('C29').value = case["inquiry1"]    # 탐구1 표준점수
        ws_input.range('C32').value = case["inquiry2"]    # 탐구2 표준점수
        ws_input.range('C19').value = case["history_grade"]  # 한국사 등급

        # 탐구 과목명 설정 (있다면)
        # ws_input.range('B29').value = case.get("inquiry1_subject", "")
        # ws_input.range('B32').value = case.get("inquiry2_subject", "")

    def _collect_university_result(
        self,
        ws_compute,
        col: str,
        case: Dict
    ) -> Dict:
        """특정 대학의 계산 결과 수집"""

        # 대학/학과 정보
        university = ws_compute.range(f'{col}1').value
        department = ws_compute.range(f'{col}2').value

        if not university or not department:
            return None

        # 환산점수 결과 수집
        korean_conv = ws_compute.range(f'{col}46').value
        math_conv = ws_compute.range(f'{col}47').value
        english_conv = ws_compute.range(f'{col}48').value
        inquiry_conv = ws_compute.range(f'{col}51').value
        history_conv = ws_compute.range(f'{col}57').value

        # 최종 점수
        row59_total = ws_compute.range(f'{col}59').value
        row3_final = ws_compute.range(f'{col}3').value

        # 필수과목 문자열
        required = ws_compute.range(f'{col}65').value

        return {
            "case_name": case["name"],
            "column": col,
            "university": str(university).strip(),
            "department": str(department).strip(),
            "input": {
                "korean": case["korean"],
                "math": case["math"],
                "english_grade": case["english_grade"],
                "inquiry1": case["inquiry1"],
                "inquiry2": case["inquiry2"],
                "history_grade": case["history_grade"],
                "inquiry1_subject": case.get("inquiry1_subject", ""),
                "inquiry2_subject": case.get("inquiry2_subject", ""),
            },
            "expected": {
                "korean_converted": korean_conv,
                "math_converted": math_conv,
                "english_converted": english_conv,
                "inquiry_converted": inquiry_conv,
                "history_converted": history_conv,
                "row59_total": row59_total,
                "row3_final": row3_final,
                "required_subjects": str(required).strip() if required else "",
            },
        }

    def save_result(self, result: Dict, output_path: str = None):
        """결과 저장"""
        if output_path is None:
            output_path = PROJECT_ROOT / "tests" / "fixtures" / "ground_truth.json"
        else:
            output_path = Path(output_path)

        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)

        logger.info(f"저장 완료: {output_path}")
        logger.info(f"  - 테스트 케이스: {result['metadata']['test_cases_count']}개")
        logger.info(f"  - 대학: {result['metadata']['universities_count']}개")
        logger.info(f"  - Ground Truth: {result['metadata']['total_ground_truth']}개")

        return output_path


def main():
    """메인 함수"""
    excel_path = PROJECT_ROOT / "202511고속성장분석기(가채점)20251114 (1).xlsx"

    if not excel_path.exists():
        logger.error(f"엑셀 파일을 찾을 수 없습니다: {excel_path}")
        return

    collector = GroundTruthCollector(str(excel_path))

    try:
        # Ground Truth 수집
        result = collector.collect_all()

        # 결과 저장
        output_path = collector.save_result(result)

        # 검증
        print("\n" + "=" * 60)
        print("Ground Truth 수집 완료")
        print("=" * 60)
        print(f"출력 파일: {output_path}")
        print(f"테스트 케이스: {result['metadata']['test_cases_count']}개")
        print(f"대학: {result['metadata']['universities_count']}개")
        print(f"Ground Truth: {result['metadata']['total_ground_truth']}개")

        # 샘플 출력
        if result["ground_truth"]:
            print("\n샘플 케이스:")
            sample = result["ground_truth"][0]
            print(f"  {sample['university']} / {sample['department']}")
            print(f"  입력: 국어={sample['input']['korean']}, 수학={sample['input']['math']}")
            print(f"  결과: row59={sample['expected']['row59_total']}")

    except Exception as e:
        logger.error(f"수집 실패: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
