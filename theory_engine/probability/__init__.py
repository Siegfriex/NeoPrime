"""
합격 확률 계산 모듈

사용법:
    from theory_engine.probability import AdmissionProbabilityModel

    model = AdmissionProbabilityModel()
    result = model.calculate(student_score, cutoff_safe, cutoff_normal, cutoff_risk)
"""

from .admission_model import AdmissionProbabilityModel, ProbabilityResult

__all__ = ["AdmissionProbabilityModel", "ProbabilityResult"]
