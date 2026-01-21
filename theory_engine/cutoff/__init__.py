"""
커트라인 추출 모듈

사용법:
    from theory_engine.cutoff import CutoffExtractor

    extractor = CutoffExtractor(percentage_df)
    cutoffs = extractor.extract_cutoffs("가천", "의학", "이과")
"""

from .cutoff_extractor import CutoffExtractor

__all__ = ["CutoffExtractor"]
