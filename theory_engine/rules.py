"""
Theory Engine 룰 엔진 v3

- RAWSCORE 변환: convert_raw_to_standard()
- INDEX 조회: lookup_index() - MultiIndex + Fuzzy
- PERCENTAGE 조회: lookup_percentage()
- RESTRICT 체크: check_disqualification()
- 확률 계산: calculate_probability()
- 전체 파이프라인: compute_theory_result()

통합 모듈:
- SubjectMatcher: 탐구과목 Fuzzy 매칭
- IndexOptimizer: INDEX 200K 행 최적화 조회
- CutoffExtractor: PERCENTAGE → 커트라인 추출
- AdmissionProbabilityModel: 확률 계산
- DisqualificationEngine: 결격 룰 엔진
"""

import pandas as pd
import logging
import time
from typing import Dict, List, Optional, Any

from .config import (
    PERCENTAGE_INTERPOLATION_POLICY,
    INDEX_NOT_FOUND_POLICY,
    InterpolationPolicy,
)
from .constants import (
    LevelTheory,
    Track,
    DisqualificationCode,
)
from .model import (
    StudentProfile,
    TheoryResult,
    ProgramResult,
    DisqualificationInfo,
    ExplainabilityInfo,
    MappingInfo,
    CutoffSourceInfo,
    DisqualificationDetail,
    TargetProgram,
    ExamScore,
)

# 새 모듈 임포트
from .matchers import SubjectMatcher
from .optimizers import IndexOptimizer, get_index_fallback
from .cutoff import CutoffExtractor
from .probability import AdmissionProbabilityModel
from .disqualification import DisqualificationEngine

logger = logging.getLogger(__name__)

# 싱글톤 인스턴스 (재사용)
_subject_matcher: Optional[SubjectMatcher] = None
_index_optimizer: Optional[IndexOptimizer] = None
_cutoff_extractor: Optional[CutoffExtractor] = None
_probability_model: Optional[AdmissionProbabilityModel] = None
_disqualification_engine: Optional[DisqualificationEngine] = None


def get_subject_matcher() -> SubjectMatcher:
    """SubjectMatcher 싱글톤"""
    global _subject_matcher
    if _subject_matcher is None:
        _subject_matcher = SubjectMatcher()
    return _subject_matcher


def get_probability_model() -> AdmissionProbabilityModel:
    """AdmissionProbabilityModel 싱글톤"""
    global _probability_model
    if _probability_model is None:
        _probability_model = AdmissionProbabilityModel()
    return _probability_model


def get_disqualification_engine() -> DisqualificationEngine:
    """DisqualificationEngine 싱글톤"""
    global _disqualification_engine
    if _disqualification_engine is None:
        _disqualification_engine = DisqualificationEngine()
    return _disqualification_engine


def get_index_optimizer(index_df: pd.DataFrame) -> IndexOptimizer:
    """IndexOptimizer (DataFrame별 인스턴스)"""
    global _index_optimizer
    if _index_optimizer is None:
        _index_optimizer = IndexOptimizer(index_df)
    return _index_optimizer


def get_cutoff_extractor(percentage_df: pd.DataFrame) -> CutoffExtractor:
    """CutoffExtractor (DataFrame별 인스턴스)"""
    global _cutoff_extractor
    if _cutoff_extractor is None:
        _cutoff_extractor = CutoffExtractor(percentage_df)
    return _cutoff_extractor


# ============================================================
# 과목명 정규화 (SubjectMatcher 활용)
# ============================================================
def normalize_subject(subject: str) -> str:
    """
    과목명 정규화

    Args:
        subject: 입력 과목명 (예: "물리학1", "화학I")

    Returns:
        정규화된 과목명 (예: "물리학 Ⅰ", "화학 Ⅰ")
    """
    matcher = get_subject_matcher()
    canonical, confidence = matcher.match(subject)

    # SubjectMatcher.match()는 신뢰도를 0~100으로 반환합니다.
    if confidence >= 70.0:
        return canonical
    else:
        logger.warning(f"과목명 매칭 낮음: '{subject}' → '{canonical}' ({confidence:.2f})")
        return canonical


# ============================================================
# RAWSCORE 변환 (v2: 다단계 매칭)
# ============================================================
def convert_raw_to_standard(
    rawscore_df: pd.DataFrame,
    subject: str,
    raw_score: int,
    raw_common: Optional[int] = None,
    raw_select: Optional[int] = None
) -> Dict[str, Any]:
    """
    원점수 → 표준점수/백분위/등급 변환 (v2: 다단계 매칭)

    변경사항:
    - Stage 1: 영역 컬럼 직접 매칭 (국어, 수학)
    - Stage 2: 과목명 컬럼 직접 매칭 (탐구과목)
    - Stage 3: 영역="탐구" + 과목명 퍼지 매칭
    - Stage 4: 전체 퍼지 매칭 (최후 수단)

    Args:
        rawscore_df: RAWSCORE 시트 DataFrame
        subject: 과목명 (예: "국어", "수학", "물리학 Ⅰ")
        raw_score: 총 원점수
        raw_common: 공통 원점수 (optional)
        raw_select: 선택 원점수 (optional)

    Returns:
        {
            "found": bool,
            "key": str,
            "match_type": str,  # stage1_영역, stage2_과목명, stage3_탐구영역, stage4_fuzzy
            "standard_score": int,
            "percentile": float,
            "grade": int,
            "cumulative_pct": float,
        }
    """
    # 과목명 정규화
    normalized_subject = normalize_subject(subject)

    # 조회 키 생성
    if raw_common is not None and raw_select is not None:
        key = f"{normalized_subject}-{raw_common}-{raw_select}"
    else:
        key = f"{normalized_subject}-{raw_score}"

    result_df = pd.DataFrame()
    match_type = None

    # ============================================================
    # Stage 1: 영역 컬럼 직접 매칭 (국어, 수학)
    # ============================================================
    if "영역" in rawscore_df.columns:
        # 정규화된 과목명으로 매칭
        mask1 = rawscore_df["영역"].apply(
            lambda x: normalize_subject(str(x)) if pd.notna(x) else ""
        ) == normalized_subject

        if mask1.any():
            # 원점수 매칭 (공통/선택 or 단일)
            if raw_common is not None and raw_select is not None:
                if "공통원점수" in rawscore_df.columns and "선택원점수" in rawscore_df.columns:
                    mask1 = mask1 & (rawscore_df["공통원점수"] == raw_common) & (rawscore_df["선택원점수"] == raw_select)
            elif "원점수" in rawscore_df.columns:
                mask1 = mask1 & (rawscore_df["원점수"] == raw_score)

            result_df = rawscore_df[mask1]
            if not result_df.empty:
                match_type = "stage1_영역"
                logger.debug(f"Stage 1 성공: {key} ({match_type})")

    # ============================================================
    # Stage 2: 과목명 컬럼 직접 매칭 (탐구과목)
    # ============================================================
    if result_df.empty and "과목명" in rawscore_df.columns:
        # 과목명 정규화 매칭
        mask2 = rawscore_df["과목명"].apply(
            lambda x: normalize_subject(str(x)) if pd.notna(x) else ""
        ) == normalized_subject

        if mask2.any():
            # 원점수 매칭
            if "원점수" in rawscore_df.columns:
                mask2 = mask2 & (rawscore_df["원점수"] == raw_score)
            result_df = rawscore_df[mask2]
            if not result_df.empty:
                match_type = "stage2_과목명"
                logger.debug(f"Stage 2 성공: {key} ({match_type})")

    # ============================================================
    # Stage 3: 영역="탐구" + 과목명 퍼지 매칭
    # ============================================================
    if result_df.empty and "영역" in rawscore_df.columns and "과목명" in rawscore_df.columns:
        # 탐구 영역 필터
        탐구_mask = rawscore_df["영역"].apply(
            lambda x: str(x).strip() if pd.notna(x) else ""
        ) == "탐구"
        탐구_df = rawscore_df[탐구_mask].copy()

        if not 탐구_df.empty:
            # 과목명 정규화 후 매칭
            탐구_df["_normalized"] = 탐구_df["과목명"].apply(
                lambda x: normalize_subject(str(x)) if pd.notna(x) else ""
            )

            # 완전 매칭
            mask3 = 탐구_df["_normalized"] == normalized_subject
            if mask3.any() and "원점수" in 탐구_df.columns:
                mask3 = mask3 & (탐구_df["원점수"] == raw_score)
            result_df = 탐구_df[mask3]

            if not result_df.empty:
                match_type = "stage3_탐구영역"
                logger.debug(f"Stage 3 성공: {key} ({match_type})")
            else:
                # 부분 매칭 - SubjectMatcher 활용
                matcher = get_subject_matcher()
                input_canonical, _ = matcher.match(normalized_subject)

                for idx, row in 탐구_df.iterrows():
                    과목명_raw = row.get("과목명", "")
                    if pd.isna(과목명_raw):
                        continue
                    과목명_canonical, confidence = matcher.match(str(과목명_raw))
                    원점수 = row.get("원점수", -1)

                    if 과목명_canonical == input_canonical and 원점수 == raw_score:
                        result_df = 탐구_df.loc[[idx]]
                        match_type = f"stage3_fuzzy(conf={confidence:.0f})"
                        logger.debug(f"Stage 3 Fuzzy 성공: {key} ({match_type})")
                        break

    # ============================================================
    # Stage 4: 전체 퍼지 매칭 (최후 수단)
    # ============================================================
    if result_df.empty:
        matcher = get_subject_matcher()
        input_canonical, _ = matcher.match(subject)

        # 모든 과목명 후보 수집 (영역 + 과목명 컬럼)
        all_subjects = []
        if "영역" in rawscore_df.columns:
            all_subjects.extend(rawscore_df["영역"].dropna().unique().tolist())
        if "과목명" in rawscore_df.columns:
            all_subjects.extend(rawscore_df["과목명"].dropna().unique().tolist())

        best_match = None
        best_score = 0

        for candidate in all_subjects:
            canonical, score = matcher.match(str(candidate))
            if canonical == input_canonical and score > best_score:
                best_score = score
                best_match = candidate

        if best_match and best_score >= 70:
            # 매칭된 과목으로 필터
            mask4 = pd.Series([False] * len(rawscore_df))
            if "영역" in rawscore_df.columns:
                mask4 = mask4 | (rawscore_df["영역"] == best_match)
            if "과목명" in rawscore_df.columns:
                mask4 = mask4 | (rawscore_df["과목명"] == best_match)

            if mask4.any() and "원점수" in rawscore_df.columns:
                mask4 = mask4 & (rawscore_df["원점수"] == raw_score)

            result_df = rawscore_df[mask4]
            if not result_df.empty:
                match_type = f"stage4_global_fuzzy(score={best_score:.0f})"
                logger.debug(f"Stage 4 성공: {key} ({match_type})")

    # ============================================================
    # 결과 처리
    # ============================================================
    if result_df.empty:
        logger.warning(f"RAWSCORE 조회 실패: {key} (all 4 stages failed)")
        return {
            "found": False,
            "key": key,
            "match_type": None,
            "standard_score": None,
            "percentile": None,
            "grade": None,
            "cumulative_pct": None,
        }

    # 첫 번째 매칭 행 사용
    row = result_df.iloc[0]

    # 컬럼명 또는 인덱스로 값 추출
    def safe_get(row, col_names, col_idx):
        """안전하게 값 추출 - 여러 컬럼명 후보 지원"""
        if isinstance(col_names, str):
            col_names = [col_names]
        for col_name in col_names:
            if col_name in row.index:
                val = row[col_name]
                if pd.notna(val):
                    return val
        if len(row) > col_idx:
            return row.iloc[col_idx]
        return None

    return {
        "found": True,
        "key": key,
        "match_type": match_type,
        "standard_score": safe_get(row, ["202511(가채점)", "표준점수", "standard_score"], 6),
        "percentile": safe_get(row, ["백분위", "percentile"], 7),
        "grade": safe_get(row, ["등급", "grade"], 8),
        "cumulative_pct": safe_get(row, ["누적%", "cumulative_pct", "누적"], 9),
    }


# ============================================================
# INDEX 조회 (IndexOptimizer 활용)
# ============================================================
def lookup_index(
    index_df: pd.DataFrame,
    korean_std: int,
    math_std: int,
    inq1_std: int,
    inq2_std: int,
    track: str,
    policy: str = INDEX_NOT_FOUND_POLICY
) -> Optional[Dict[str, Any]]:
    """
    점수 조합으로 INDEX 행 찾기 (MultiIndex + Fuzzy)

    Args:
        index_df: INDEX 시트 DataFrame
        korean_std: 국어 표준점수
        math_std: 수학 표준점수
        inq1_std: 탐구1 표준점수
        inq2_std: 탐구2 표준점수
        track: 계열 (이과/문과)
        policy: "error" | "warn" | "silent"

    Returns:
        {
            "found": bool,
            "index_key": str,
            "percentile_sum": float,
            "national_rank": int,
            "cumulative_pct": float,
            "match_type": str,  # "exact" | "fuzzy"
            ...
        }
    """
    optimizer = get_index_optimizer(index_df)

    # 조회 시도 (fuzzy=True로 근사 매칭 허용)
    result = optimizer.lookup(korean_std, math_std, inq1_std, inq2_std, track, fuzzy=True)

    if not result.get("found", False):
        index_key = f"{korean_std}-{math_std}-{inq1_std}-{inq2_std}-{track}"
        msg = f"INDEX 조회 실패: {index_key}"
        if policy == "error":
            raise ValueError(msg)
        elif policy == "warn":
            logger.warning(msg)

        return {
            "found": False,
            "index_key": index_key,
            "percentile_sum": None,
            "national_rank": None,
            "cumulative_pct": None,
            "match_type": None,
        }

    return result


# ============================================================
# PERCENTAGE 조회 (CutoffExtractor 활용)
# ============================================================
def lookup_percentage(
    percentage_df: pd.DataFrame,
    university: str,
    major: str,
    percentile: float,
    track: str = "",
    policy: InterpolationPolicy = PERCENTAGE_INTERPOLATION_POLICY
) -> Dict[str, Optional[float]]:
    """
    대학/전공/누백으로 환산점수 및 커트라인 조회

    Args:
        percentage_df: PERCENTAGE 시트 DataFrame
        university: 대학명
        major: 전공명
        percentile: 누적백분위
        track: 계열 (optional)
        policy: 보간 정책

    Returns:
        {
            "found": bool,
            "score": float,
            "cutoff_safe": float,   # 20% 라인 (상위 20%, 적정)
            "cutoff_normal": float, # 50% 라인
            "cutoff_risk": float,   # 80% 라인 (상위 80%, 소신)
            "column": str,
            "match_info": dict,
            "interpolated": bool,
            "interpolation_method": str,
        }
    """
    extractor = get_cutoff_extractor(percentage_df)

    # 커트라인 추출
    cutoff_result = extractor.extract_cutoffs(university, major, track)

    if not cutoff_result.get("found", False):
        logger.warning(f"PERCENTAGE에서 {university}{major} 찾을 수 없음")
        return {
            "found": False,
            "score": None,
            "cutoff_safe": None,
            "cutoff_normal": None,
            "cutoff_risk": None,
            "column": None,
            "match_info": cutoff_result.get("match_info", {}) if cutoff_result else {},
            "interpolated": None,
            "interpolation_method": None,
        }

    # 해당 누백에서의 점수 조회
    score = extractor.get_score_at_percentile(university, major, percentile, track)
    score_lookup = getattr(extractor, "_last_score_lookup", {}) or {}

    return {
        "found": True,
        "score": score,
        "cutoff_safe": cutoff_result.get("cutoff_safe"),
        "cutoff_normal": cutoff_result.get("cutoff_normal"),
        "cutoff_risk": cutoff_result.get("cutoff_risk"),
        "column": cutoff_result.get("column"),
        "match_info": cutoff_result.get("match_info", {}),
        "interpolated": score_lookup.get("interpolated"),
        "interpolation_method": score_lookup.get("interpolation_method"),
    }


# ============================================================
# RESTRICT 결격 체크 (DisqualificationEngine 활용)
# ============================================================
def check_disqualification(
    restrict_df: pd.DataFrame,
    profile: StudentProfile,
    target: TargetProgram,
    severity_threshold: int = 2
) -> DisqualificationInfo:
    """
    결격 사유 확인 (DisqualificationEngine 활용)

    Args:
        restrict_df: RESTRICT 시트 DataFrame (현재 미사용, 향후 동적 룰 로딩용)
        profile: 학생 프로필
        target: 지원 대학/전형
        severity_threshold: 심각도 임계값 (2=심각한 것만)

    Returns:
        DisqualificationInfo
    """
    engine = get_disqualification_engine()
    return engine.check(profile, target, severity_threshold)


# ============================================================
# 확률 계산 (AdmissionProbabilityModel 활용)
# ============================================================
def calculate_probability(
    student_score: float,
    cutoff_safe: Optional[float],
    cutoff_normal: Optional[float],
    cutoff_risk: Optional[float]
) -> Dict[str, Any]:
    """
    합격 확률 계산

    Args:
        student_score: 학생의 환산점수
        cutoff_safe: 적정 커트라인 (80%)
        cutoff_normal: 예상 커트라인 (50%)
        cutoff_risk: 소신 커트라인 (20%)

    Returns:
        {
            "probability": float,
            "level": str,  # 적정/예상/소신/상향
            "confidence_low": float,
            "confidence_high": float,
        }
    """
    model = get_probability_model()
    result = model.calculate(student_score, cutoff_safe, cutoff_normal, cutoff_risk)

    return {
        "probability": result.probability,
        "level": result.level,
        "confidence_low": result.confidence_low,
        "confidence_high": result.confidence_high,
    }


def level_to_theory(level: str) -> LevelTheory:
    """확률 레벨을 LevelTheory enum으로 변환"""
    mapping = {
        "적정": LevelTheory.SAFE,
        "예상": LevelTheory.NORMAL,
        "소신": LevelTheory.RISK,
        "상향": LevelTheory.REACH,
        "알수없음": LevelTheory.NO_DATA,
    }
    return mapping.get(level, LevelTheory.NO_DATA)


# ============================================================
# 최상위 계산 함수
# ============================================================
def compute_theory_result(
    excel_data: Dict[str, pd.DataFrame],
    profile: StudentProfile,
    debug: bool = False
) -> TheoryResult:
    """
    전체 이론 계산 파이프라인

    Args:
        excel_data: 엑셀 시트 dict (load_workbook 결과)
        profile: 학생 프로필
        debug: True면 raw_components에 상세 저장

    Returns:
        TheoryResult
    """
    result = TheoryResult()

    # 1. 원점수 → 표준점수 변환
    korean_conv = convert_raw_to_standard(
        excel_data["RAWSCORE"],
        profile.korean.subject,
        profile.korean.raw_total or 0,
        profile.korean.raw_common,
        profile.korean.raw_select
    )

    math_conv = convert_raw_to_standard(
        excel_data["RAWSCORE"],
        profile.math.subject,
        profile.math.raw_total or 0,
        profile.math.raw_common,
        profile.math.raw_select
    )

    # 탐구과목 정규화 후 변환
    inq1_subject = normalize_subject(profile.inquiry1.subject) if profile.inquiry1 else ""
    inq2_subject = normalize_subject(profile.inquiry2.subject) if profile.inquiry2 else ""

    inq1_conv = convert_raw_to_standard(
        excel_data["RAWSCORE"],
        inq1_subject,
        profile.inquiry1.raw_total or 0
    ) if profile.inquiry1 else {"found": False}

    inq2_conv = convert_raw_to_standard(
        excel_data["RAWSCORE"],
        inq2_subject,
        profile.inquiry2.raw_total or 0
    ) if profile.inquiry2 else {"found": False}

    # raw_components 저장
    result.raw_components.update({
        "korean_standard": korean_conv.get("standard_score"),
        "korean_percentile": korean_conv.get("percentile"),
        "korean_grade": korean_conv.get("grade"),
        "math_standard": math_conv.get("standard_score"),
        "math_percentile": math_conv.get("percentile"),
        "math_grade": math_conv.get("grade"),
        "inquiry1_subject": inq1_subject,
        "inquiry1_standard": inq1_conv.get("standard_score"),
        "inquiry2_subject": inq2_subject,
        "inquiry2_standard": inq2_conv.get("standard_score"),
        "rawscore_keys": [
            korean_conv.get("key"),
            math_conv.get("key"),
            inq1_conv.get("key"),
            inq2_conv.get("key"),
        ],
    })

    # 2. INDEX 조회 (+ 폴백 로직)
    cumulative_pct = None
    index_result = None

    if "INDEX" in excel_data:
        index_result = lookup_index(
            excel_data["INDEX"],
            korean_conv.get("standard_score") or 0,
            math_conv.get("standard_score") or 0,
            inq1_conv.get("standard_score") or 0,
            inq2_conv.get("standard_score") or 0,
            profile.track.value
        )

    # INDEX 조회 실패 시 폴백 사용
    if not index_result or not index_result.get("found"):
        logger.warning("INDEX 조회 실패, RAWSCORE 폴백 사용")
        fallback = get_index_fallback()
        index_result = fallback.calculate_from_rawscore(
            korean_conv,
            math_conv,
            inq1_conv,
            inq2_conv,
            english_grade=profile.english_grade,
            method="weighted"
        )

    if index_result:
        cumulative_pct = index_result.get("cumulative_pct")
        result.raw_components.update({
            "index_key": index_result.get("index_key"),
            "index_found": index_result.get("found"),
            "index_match_type": index_result.get("match_type"),
            "percentile_sum": index_result.get("percentile_sum"),
            "national_rank": index_result.get("national_rank"),
            "cumulative_pct": cumulative_pct,
            "fallback_subjects": index_result.get("subjects_used"),
            "fallback_confidence": index_result.get("confidence"),
        })

    # 3. 각 target에 대해 처리
    for target in profile.targets:
        _t0 = time.perf_counter()

        # Explainability 기본(대학/전공 매핑)
        try:
            # CutoffExtractor의 정적 alias 데이터 재사용
            CutoffExtractor._build_alias_reverse_map()
            _official_univ = CutoffExtractor.ALIAS_TO_OFFICIAL.get(
                CutoffExtractor._normalize_university(target.university),
                target.university
            )
        except Exception:
            _official_univ = target.university

        _univ_method = "alias" if _official_univ != target.university else "exact"
        explainability = ExplainabilityInfo(
            university_mapping=MappingInfo(
                input=target.university,
                matched=_official_univ,
                method=_univ_method,
                confidence=1.0,
                alias_chain=[target.university, _official_univ] if _univ_method == "alias" else [],
            ),
            major_mapping=MappingInfo(
                input=target.major,
                matched=target.major,
                method="exact",
                confidence=1.0,
            ),
        )

        # 결격 체크
        disqual = check_disqualification(
            excel_data.get("RESTRICT", pd.DataFrame()),
            profile,
            target,
            severity_threshold=2  # 심각한 결격만
        )

        if disqual.is_disqualified:
            # 결격 상세 (Explainability)
            for rid in (disqual.rules_triggered or []):
                explainability.disqualification_details.append(
                    DisqualificationDetail(
                        rule_id=rid,
                        reason=disqual.reason or ""
                    )
                )
            explainability.performance_ms = round((time.perf_counter() - _t0) * 1000.0, 2)

            prog_result = ProgramResult(
                target=target,
                level_theory=LevelTheory.DISQUALIFIED,
                disqualification=disqual,
                explainability=explainability,
            )
            result.program_results.append(prog_result)
            continue

        # PERCENTAGE 조회 및 확률 계산
        if "PERCENTAGE" in excel_data:
            # 학생의 누백 사용 (없으면 50.0)
            student_pct = cumulative_pct if cumulative_pct else 50.0

            perc_result = lookup_percentage(
                excel_data["PERCENTAGE"],
                target.university,
                target.major,
                student_pct,
                track=profile.track.value
            )

            if perc_result.get("found"):
                # Explainability: 매칭/소스 정보 채우기
                match_info = perc_result.get("match_info") or {}
                if match_info:
                    stage = match_info.get("match_stage")
                    fuzzy_score = match_info.get("fuzzy_score")

                    # 대학 매핑
                    univ_method = match_info.get("university_method", explainability.university_mapping.method)
                    if stage == "fuzzy":
                        univ_method = "fuzzy"

                    univ_conf = 1.0
                    if isinstance(fuzzy_score, (int, float)) and stage == "fuzzy":
                        univ_conf = max(0.0, min(1.0, float(fuzzy_score) / 100.0))

                    explainability.university_mapping = MappingInfo(
                        input=target.university,
                        matched=match_info.get("university_official", _official_univ),
                        method=univ_method,
                        confidence=univ_conf,
                        fuzzy_score=float(fuzzy_score) if isinstance(fuzzy_score, (int, float)) else None,
                    )

                    # 전공 매핑
                    major_method = match_info.get("major_method", explainability.major_mapping.method)
                    if stage == "fuzzy":
                        major_method = "fuzzy"

                    explainability.major_mapping = MappingInfo(
                        input=target.major,
                        matched=match_info.get("major_used", target.major),
                        method=major_method,
                        confidence=univ_conf if stage == "fuzzy" else 1.0,
                        fuzzy_score=float(fuzzy_score) if isinstance(fuzzy_score, (int, float)) else None,
                        alias_chain=list(match_info.get("alias_chain") or []),
                    )

                explainability.cutoff_source = CutoffSourceInfo(
                    sheet="PERCENTAGE",
                    column_name=str(perc_result.get("column")) if perc_result.get("column") is not None else None,
                    percentile=float(student_pct) if student_pct is not None else None,
                    interpolated=bool(perc_result.get("interpolated")) if perc_result.get("interpolated") is not None else False,
                    interpolation_method=perc_result.get("interpolation_method"),
                )

                # 확률 계산
                prob_result = calculate_probability(
                    perc_result.get("score") or 0,
                    perc_result.get("cutoff_safe"),
                    perc_result.get("cutoff_normal"),
                    perc_result.get("cutoff_risk")
                )

                level = level_to_theory(prob_result["level"])

                explainability.performance_ms = round((time.perf_counter() - _t0) * 1000.0, 2)
                prog_result = ProgramResult(
                    target=target,
                    p_theory=prob_result["probability"],
                    score_theory=perc_result.get("score"),
                    level_theory=level,
                    cutoff_safe=perc_result.get("cutoff_safe"),
                    cutoff_normal=perc_result.get("cutoff_normal"),
                    cutoff_risk=perc_result.get("cutoff_risk"),
                    disqualification=disqual,
                    explainability=explainability,
                )
            else:
                explainability.cutoff_source = CutoffSourceInfo(
                    sheet="PERCENTAGE",
                    column_name=None,
                    percentile=float(student_pct) if student_pct is not None else None,
                    interpolated=False,
                    interpolation_method=None,
                )
                explainability.performance_ms = round((time.perf_counter() - _t0) * 1000.0, 2)
                prog_result = ProgramResult(
                    target=target,
                    level_theory=LevelTheory.NO_DATA,
                    disqualification=disqual,
                    explainability=explainability,
                )

            result.program_results.append(prog_result)
        else:
            explainability.cutoff_source = CutoffSourceInfo(
                sheet="PERCENTAGE",
                column_name=None,
                percentile=None,
                interpolated=False,
                interpolation_method=None,
            )
            explainability.performance_ms = round((time.perf_counter() - _t0) * 1000.0, 2)
            prog_result = ProgramResult(
                target=target,
                level_theory=LevelTheory.NO_DATA,
                disqualification=disqual,
                explainability=explainability,
            )
            result.program_results.append(prog_result)

    return result


# ============================================================
# 편의 함수들
# ============================================================
def quick_check(
    excel_data: Dict[str, pd.DataFrame],
    track: str,
    korean_raw: int,
    math_raw: int,
    english_grade: int,
    history_grade: int,
    inq1_subject: str,
    inq1_raw: int,
    inq2_subject: str,
    inq2_raw: int,
    universities: List[str],
    majors: List[str]
) -> TheoryResult:
    """
    빠른 체크 (간편 인터페이스)

    Args:
        excel_data: 엑셀 데이터
        track: "이과" | "문과"
        korean_raw: 국어 원점수
        math_raw: 수학 원점수
        english_grade: 영어 등급
        history_grade: 한국사 등급
        inq1_subject: 탐구1 과목명
        inq1_raw: 탐구1 원점수
        inq2_subject: 탐구2 과목명
        inq2_raw: 탐구2 원점수
        universities: 대학명 리스트
        majors: 전공명 리스트 (universities와 1:1 매핑)

    Returns:
        TheoryResult
    """
    # 프로필 생성
    targets = [
        TargetProgram(university=u, major=m)
        for u, m in zip(universities, majors)
    ]

    profile = StudentProfile(
        track=Track(track),
        korean=ExamScore(subject="국어", raw_total=korean_raw),
        math=ExamScore(subject="수학", raw_total=math_raw),
        english_grade=english_grade,
        history_grade=history_grade,
        inquiry1=ExamScore(subject=inq1_subject, raw_total=inq1_raw),
        inquiry2=ExamScore(subject=inq2_subject, raw_total=inq2_raw),
        targets=targets
    )

    return compute_theory_result(excel_data, profile)


if __name__ == "__main__":
    # 통합 테스트
    logging.basicConfig(level=logging.INFO)

    from .loader import load_workbook
    from .config import EXCEL_PATH

    print("=" * 60)
    print("Theory Engine v3 통합 테스트")
    print("=" * 60)

    # 엑셀 로드 시도
    try:
        excel_data = load_workbook(EXCEL_PATH)
        print(f"로드된 시트: {list(excel_data.keys())}")

        # 테스트 프로필
        profile = StudentProfile(
            track=Track.SCIENCE,
            korean=ExamScore("국어(언매)", raw_total=80),
            math=ExamScore("수학(미적)", raw_total=75),
            english_grade=2,
            history_grade=3,
            inquiry1=ExamScore("물리학I", raw_total=50),
            inquiry2=ExamScore("화학I", raw_total=48),
            targets=[
                TargetProgram("가천", "의학"),
                TargetProgram("서울대", "공대"),
            ]
        )

        print(f"\n프로필:")
        print(f"  계열: {profile.track.value}")
        print(f"  영어: {profile.english_grade}등급")
        print(f"  한국사: {profile.history_grade}등급")
        print(f"  탐구: {profile.inquiry1.subject}, {profile.inquiry2.subject}")
        print(f"  지원: {[(t.university, t.major) for t in profile.targets]}")

        # 계산 실행
        result = compute_theory_result(excel_data, profile, debug=True)

        print(f"\n결과:")
        print(f"  Engine: {result.engine_version}")
        print(f"  Programs: {len(result.program_results)}")

        for prog in result.program_results:
            print(f"\n  [{prog.target.university} {prog.target.major}]")
            print(f"    Level: {prog.level_theory.value}")
            if prog.p_theory:
                print(f"    확률: {prog.p_theory:.2%}")
            if prog.score_theory:
                print(f"    환산점수: {prog.score_theory}")
            if prog.cutoff_normal:
                print(f"    커트라인(50%): {prog.cutoff_normal}")
            if prog.disqualification and prog.disqualification.is_disqualified:
                print(f"    결격: {prog.disqualification.reason}")

        print(f"\n원점수 변환:")
        for key in ["korean_standard", "math_standard", "inquiry1_standard", "inquiry2_standard"]:
            print(f"  {key}: {result.raw_components.get(key)}")

        print(f"\nINDEX 조회:")
        print(f"  found: {result.raw_components.get('index_found')}")
        print(f"  match_type: {result.raw_components.get('index_match_type')}")
        print(f"  cumulative_pct: {result.raw_components.get('cumulative_pct')}")

        print("\n테스트 완료!")

    except Exception as e:
        print(f"테스트 실패: {e}")
        import traceback
        traceback.print_exc()
