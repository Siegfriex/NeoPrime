"""
Excel 오라클: xlwings/COM 기반 실계산으로 golden case 생성 (옵션)

Windows + Excel 설치 환경에서만 동작합니다.
"""

import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    """메인 함수"""
    logger.info("Excel 오라클은 옵션 기능입니다.")
    logger.info("Windows + Excel 환경에서 xlwings를 사용하여 구현할 수 있습니다.")
    logger.info("현재는 스켈레톤만 제공됩니다.")


if __name__ == "__main__":
    main()
