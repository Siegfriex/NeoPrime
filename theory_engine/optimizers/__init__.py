"""
INDEX 시트 조회 최적화 모듈

사용법:
    from theory_engine.optimizers import IndexOptimizer, IndexFallback, get_index_fallback

    # 일반 조회
    optimizer = IndexOptimizer(index_df)
    result = optimizer.lookup(130, 135, 65, 62, "이과")

    # 폴백 조회 (INDEX 실패 시)
    fallback = get_index_fallback()
    result = fallback.calculate_from_rawscore(korean_conv, math_conv, inq1_conv, inq2_conv)
"""

from .index_optimizer import IndexOptimizer
from .index_fallback import IndexFallback, get_index_fallback

__all__ = ["IndexOptimizer", "IndexFallback", "get_index_fallback"]
