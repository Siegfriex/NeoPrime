#!/usr/bin/env python
"""
Theory Engine 실행 스크립트

엑셀 데이터를 로드하고 이론 시뮬레이션을 실행합니다.
"""

import logging
import sys
from pathlib import Path

# Theory Engine import
from theory_engine import loader, model, rules
from theory_engine.constants import Track
from theory_engine.config import EXCEL_PATH

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """메인 실행 함수"""
    
    # 1. 엑셀 파일 확인
    if not Path(EXCEL_PATH).exists():
        logger.error(f"엑셀 파일 없음: {EXCEL_PATH}")
        logger.info("프로젝트 루트에 엑셀 파일을 배치하세요.")
        return 1
    
    logger.info(f"엑셀 파일 발견: {EXCEL_PATH}")
    
    # 2. 엑셀 데이터 로드
    logger.info("엑셀 데이터 로드 중...")
    try:
        excel_data = loader.load_workbook(strict=False)
        logger.info(f"로드 완료: {len(excel_data)}개 시트")
        for name, df in excel_data.items():
            logger.info(f"  - {name}: {df.shape}")
    except Exception as e:
        logger.error(f"엑셀 로드 실패: {e}")
        return 1
    
    # 3. 테스트 학생 프로필 생성
    logger.info("\n테스트 학생 프로필 생성...")
    
    korean = model.ExamScore("국어", raw_total=80)
    math = model.ExamScore("수학", raw_total=75)
    inquiry1 = model.ExamScore("물리학I", raw_total=50)
    inquiry2 = model.ExamScore("화학I", raw_total=48)
    
    profile = model.StudentProfile(
        track=Track.SCIENCE,
        korean=korean,
        math=math,
        english_grade=2,
        history_grade=3,
        inquiry1=inquiry1,
        inquiry2=inquiry2,
        targets=[
            model.TargetProgram("가천", "의학"),
            model.TargetProgram("건국", "자연"),
            model.TargetProgram("경기", "인문"),
        ]
    )
    
    logger.info(f"  계열: {profile.track.value}")
    logger.info(f"  국어: {profile.korean.raw_total}점")
    logger.info(f"  수학: {profile.math.raw_total}점")
    logger.info(f"  영어: {profile.english_grade}등급")
    logger.info(f"  목표: {len(profile.targets)}개 대학")
    
    # 4. 시뮬레이션 실행
    logger.info("\n이론 시뮬레이션 실행 중...")
    try:
        result = rules.compute_theory_result(excel_data, profile, debug=True)
        logger.info("시뮬레이션 완료!")
    except Exception as e:
        logger.error(f"시뮬레이션 실패: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    # 5. 결과 출력
    logger.info(f"\n{'='*60}")
    logger.info("시뮬레이션 결과")
    logger.info(f"{'='*60}")
    
    logger.info(f"\n버전 정보:")
    logger.info(f"  Engine: {result.engine_version}")
    logger.info(f"  Excel: {result.excel_version}")
    logger.info(f"  계산 시각: {result.computed_at}")
    
    logger.info(f"\n중간 계산 결과 (raw_components):")
    for key, value in result.raw_components.items():
        if value is not None and key != "rawscore_keys":
            logger.info(f"  {key}: {value}")
    
    logger.info(f"\n대학별 예측 결과:")
    if result.program_results:
        for i, prog_result in enumerate(result.program_results, 1):
            logger.info(f"\n  [{i}] {prog_result.target.university} {prog_result.target.major}")
            logger.info(f"      라인: {prog_result.level_theory.value}")
            logger.info(f"      확률: {prog_result.p_theory}")
            logger.info(f"      환산점수: {prog_result.score_theory}")
            
            if prog_result.disqualification.is_disqualified:
                logger.info(f"      결격: {prog_result.disqualification.reason}")
    else:
        logger.warning("  예측 결과 없음")
    
    logger.info(f"\n{'='*60}")
    logger.info("실행 완료!")
    logger.info(f"{'='*60}\n")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
