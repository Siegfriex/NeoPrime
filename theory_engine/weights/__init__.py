"""
가중치/환산점수 모듈

엑셀에서 추출한 실제 환산점수 테이블을 사용합니다.
DEFAULT_WEIGHTS 같은 임의 폴백은 사용하지 않습니다.
"""

from .extracted_weights import (
    ExtractedWeightLoader,
    WeightNotFoundError,
    ConversionNotFoundError,
    get_weight_loader,
)

__all__ = [
    'ExtractedWeightLoader',
    'WeightNotFoundError',
    'ConversionNotFoundError',
    'get_weight_loader',
]
