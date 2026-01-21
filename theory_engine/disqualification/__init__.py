"""
결격 사유 체크 모듈

사용법:
    from theory_engine.disqualification import DisqualificationEngine

    engine = DisqualificationEngine()
    result = engine.check(profile, target)
"""

from .disqualification_engine import DisqualificationEngine, DisqualificationRule

__all__ = ["DisqualificationEngine", "DisqualificationRule"]
