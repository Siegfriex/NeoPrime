"""
NeoPrime Theory Engine

엑셀 기반 입시 예측 시뮬레이션 엔진을 파이썬으로 재구현
"""

from .config import ENGINE_VERSION, EXCEL_VERSION
from .constants import LevelTheory, Track, DisqualificationCode

__version__ = ENGINE_VERSION
__all__ = [
    "ENGINE_VERSION",
    "EXCEL_VERSION",
    "LevelTheory",
    "Track",
    "DisqualificationCode",
]
