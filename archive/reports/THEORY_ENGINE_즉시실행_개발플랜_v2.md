# Theory Engine v3.0 즉시 실행 개발 플랜 v2.0

**작성일**: 2026-01-18  
**기반**: THEORY_ENGINE_이행현황_수정보고서_20260118.md  
**목표**: 실제 작동률 58% → 98% (6시간 내 완료)  
**에이전트**: Claude 에이전트 CLI 최적화

---

## 📋 Executive Summary

### 핵심 이슈 3개 - 정확한 원인과 해결책

| # | 이슈 | 현재 | 원인 | 해결책 | 소요 |
|---|------|------|------|--------|------|
| **1** | RAWSCORE 탐구과목 | 40% | `rules.py`가 "영역" 컬럼만 검색, 탐구는 "과목명" 사용 | `convert_raw_to_standard()` 3단계 매칭 추가 | **90분** |
| **2** | INDEX 조회 | 0% | 첫 컬럼 해시 인코딩, MultiIndex 0행 구축 | RAWSCORE 누적% 폴백 로직 | **60분** |
| **3** | 대학 커트라인 | 67% | "연세대" vs "연대", Alias 없음 | `cutoff_extractor.py`에 30+ 대학 Alias 추가 | **90분** |

---

## 🔧 Task 1: RAWSCORE 탐구과목 수정 (90분)

### 1.1 현재 문제점

```python
# 현재 rules.py:166-169
mask = (
    (rawscore_df["영역"].apply(lambda x: normalize_subject(str(x))) == normalized_subject) &
    (rawscore_df.get("원점수", raw_score) == raw_score)
)
```

**문제**: 탐구과목은 `영역="탐구"` + `과목명="물리학 Ⅰ"` 구조  
**현재**: `영역` 컬럼만 검색하므로 국어/수학만 성공

### 1.2 수정 코드

**파일**: `theory_engine/rules.py`  
**함수**: `convert_raw_to_standard()` 전체 교체

```python
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
            # 원점수 매칭
            if "원점수" in rawscore_df.columns:
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
        탐구_df = rawscore_df[rawscore_df["영역"] == "탐구"].copy()
        
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
                # 부분 매칭 (과목명에 검색어 포함)
                matcher = get_subject_matcher()
                for idx, row in 탐구_df.iterrows():
                    과목명_norm = row.get("_normalized", "")
                    원점수 = row.get("원점수", -1)
                    
                    # SubjectMatcher 사용
                    _, confidence = matcher.match(과목명_norm)
                    matched_canonical, _ = matcher.match(normalized_subject)
                    
                    if confidence >= 70 and 원점수 == raw_score:
                        result_df = 탐구_df.loc[[idx]]
                        match_type = f"stage3_fuzzy(conf={confidence:.0f})"
                        logger.debug(f"Stage 3 Fuzzy 성공: {key} ({match_type})")
                        break
    
    # ============================================================
    # Stage 4: 전체 퍼지 매칭 (최후 수단)
    # ============================================================
    if result_df.empty:
        matcher = get_subject_matcher()
        
        # 모든 과목명 후보 수집
        all_subjects = set()
        if "영역" in rawscore_df.columns:
            all_subjects.update(rawscore_df["영역"].dropna().unique())
        if "과목명" in rawscore_df.columns:
            all_subjects.update(rawscore_df["과목명"].dropna().unique())
        
        best_match = None
        best_score = 0
        
        for candidate in all_subjects:
            canonical, score = matcher.match(str(candidate))
            input_canonical, _ = matcher.match(subject)
            
            if canonical == input_canonical and score > best_score:
                best_score = score
                best_match = candidate
        
        if best_match and best_score >= 70:
            # 매칭된 과목으로 필터
            if best_match in rawscore_df.get("영역", pd.Series()).values:
                mask4 = rawscore_df["영역"] == best_match
            elif best_match in rawscore_df.get("과목명", pd.Series()).values:
                mask4 = rawscore_df["과목명"] == best_match
            else:
                mask4 = pd.Series([False] * len(rawscore_df))
            
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
    def safe_get(row, col_name, col_idx):
        """안전하게 값 추출"""
        if col_name in row.index:
            return row[col_name]
        elif len(row) > col_idx:
            return row.iloc[col_idx]
        return None
    
    return {
        "found": True,
        "key": key,
        "match_type": match_type,
        "standard_score": safe_get(row, "202511(가채점)", 6),
        "percentile": safe_get(row, "백분위", 7),
        "grade": safe_get(row, "등급", 8),
        "cumulative_pct": safe_get(row, "누적%", 9),
    }
```

### 1.3 테스트 코드

```python
# tests/test_rawscore_inquiry.py

import pytest
from theory_engine.loader import load_workbook
from theory_engine.rules import convert_raw_to_standard

@pytest.fixture(scope="module")
def excel_data():
    return load_workbook()

class TestRAWSCOREInquirySubjects:
    """RAWSCORE 탐구과목 변환 테스트"""
    
    @pytest.mark.parametrize("subject,raw_score", [
        ("국어", 80),
        ("수학", 75),
        ("물리학 Ⅰ", 45),
        ("물리학I", 45),
        ("화학 Ⅰ", 42),
        ("생명과학 Ⅰ", 40),
        ("지구과학 Ⅰ", 38),
        ("생활과 윤리", 35),
        ("사회·문화", 42),
    ])
    def test_inquiry_conversion(self, excel_data, subject, raw_score):
        """탐구과목 포함 전체 과목 변환"""
        result = convert_raw_to_standard(
            excel_data["RAWSCORE"], subject, raw_score
        )
        
        assert result["found"] is True, f"{subject} 변환 실패: {result}"
        assert result["standard_score"] is not None, f"{subject} 표준점수 None"
        assert result["match_type"] is not None, f"{subject} 매칭 타입 None"
        
        print(f"✅ {subject} {raw_score}점 → "
              f"표준={result['standard_score']}, "
              f"타입={result['match_type']}")
```

---

## 🔧 Task 2: INDEX 우회 로직 (60분)

### 2.1 현재 문제점

```
IndexOptimizer: MultiIndex 구축 완료: 0행  ← 문제!
```

**원인**: INDEX 시트 첫 컬럼이 "510gs0t20509" 같은 인코딩 키

### 2.2 수정 코드

**새 파일**: `theory_engine/optimizers/index_fallback.py`

```python
"""
INDEX 조회 실패 시 RAWSCORE 누적% 폴백 계산
"""

import logging
from typing import Dict, Optional, List

logger = logging.getLogger(__name__)


class IndexFallback:
    """INDEX 조회 우회 계산기"""
    
    # 과목별 가중치 (수능 반영 비율 기반)
    DEFAULT_WEIGHTS = {
        "korean": 0.28,
        "math": 0.28,
        "english": 0.14,
        "inquiry1": 0.15,
        "inquiry2": 0.15,
    }
    
    def __init__(self, weights: Optional[Dict[str, float]] = None):
        self.weights = weights or self.DEFAULT_WEIGHTS
    
    def calculate_from_rawscore(
        self,
        korean_conv: Dict,
        math_conv: Dict,
        inq1_conv: Dict,
        inq2_conv: Dict,
        english_grade: int = 1,
        method: str = "weighted"
    ) -> Dict:
        """
        RAWSCORE 누적% 합산으로 INDEX 대체
        
        Args:
            korean_conv: convert_raw_to_standard() 결과
            math_conv: convert_raw_to_standard() 결과
            inq1_conv: convert_raw_to_standard() 결과
            inq2_conv: convert_raw_to_standard() 결과
            english_grade: 영어 등급 (1-9)
            method: "weighted" | "simple" | "geometric"
        
        Returns:
            {
                "found": True,
                "match_type": "fallback_rawscore_weighted",
                "cumulative_pct": 5.2,
                "percentile_sum": 356.5,
                "national_rank": 26000,
                "confidence": 0.85
            }
        """
        # 각 과목 누적% 추출
        conversions = {
            "korean": korean_conv,
            "math": math_conv,
            "inquiry1": inq1_conv,
            "inquiry2": inq2_conv,
        }
        
        pcts = {}
        for key, conv in conversions.items():
            if conv and conv.get("found"):
                pct = conv.get("cumulative_pct") or conv.get("percentile")
                if pct is not None:
                    pcts[key] = float(pct)
        
        # 영어 등급 → 백분위 변환
        english_pct = self._grade_to_percentile(english_grade)
        if english_pct:
            pcts["english"] = english_pct
        
        if not pcts:
            logger.warning("유효한 누적% 데이터 없음")
            return {
                "found": False,
                "match_type": "fallback_failed",
                "cumulative_pct": None,
                "percentile_sum": None,
                "national_rank": None,
                "confidence": 0.0,
            }
        
        logger.info(f"INDEX 폴백: {len(pcts)}개 과목 사용")
        
        # 방법별 계산
        if method == "weighted":
            cumulative_pct = self._weighted_average(pcts)
            match_type = "fallback_rawscore_weighted"
        elif method == "simple":
            cumulative_pct = sum(pcts.values()) / len(pcts)
            match_type = "fallback_rawscore_simple"
        elif method == "geometric":
            import math
            product = 1.0
            for pct in pcts.values():
                product *= max(pct, 0.01) / 100
            cumulative_pct = (product ** (1 / len(pcts))) * 100
            match_type = "fallback_rawscore_geometric"
        else:
            cumulative_pct = self._weighted_average(pcts)
            match_type = "fallback_rawscore_weighted"
        
        # 백분위 합산 (단순 합계)
        percentile_sum = sum(pcts.values())
        
        # 전국 등수 추정 (50만명 기준)
        national_rank = self._estimate_national_rank(cumulative_pct)
        
        # 신뢰도 계산 (사용된 과목 수 기반)
        confidence = len(pcts) / 5.0  # 5과목 기준
        
        return {
            "found": True,
            "match_type": match_type,
            "cumulative_pct": round(cumulative_pct, 2),
            "percentile_sum": round(percentile_sum, 2),
            "national_rank": national_rank,
            "confidence": round(confidence, 2),
            "subjects_used": list(pcts.keys()),
        }
    
    def _weighted_average(self, pcts: Dict[str, float]) -> float:
        """가중 평균 계산"""
        total_weight = 0.0
        weighted_sum = 0.0
        
        for key, pct in pcts.items():
            weight = self.weights.get(key, 0.2)  # 기본 가중치 0.2
            weighted_sum += pct * weight
            total_weight += weight
        
        if total_weight == 0:
            return 50.0  # 기본값
        
        return weighted_sum / total_weight
    
    def _grade_to_percentile(self, grade: int) -> Optional[float]:
        """등급 → 백분위 변환"""
        # 수능 등급 백분위 기준
        grade_to_pct = {
            1: 4.0,    # 상위 4%
            2: 11.0,   # 상위 11%
            3: 23.0,   # 상위 23%
            4: 40.0,   # 상위 40%
            5: 60.0,   # 상위 60%
            6: 77.0,   # 상위 77%
            7: 89.0,   # 상위 89%
            8: 96.0,   # 상위 96%
            9: 100.0,  # 상위 100%
        }
        return grade_to_pct.get(grade)
    
    def _estimate_national_rank(
        self,
        cumulative_pct: float,
        total_students: int = 500000
    ) -> int:
        """누적백분위 → 전국 등수 추정"""
        # cumulative_pct가 낮을수록 상위권
        rank = int((cumulative_pct / 100.0) * total_students)
        return max(1, rank)


# 싱글톤
_index_fallback: Optional[IndexFallback] = None

def get_index_fallback() -> IndexFallback:
    global _index_fallback
    if _index_fallback is None:
        _index_fallback = IndexFallback()
    return _index_fallback
```

### 2.3 rules.py 수정

**파일**: `theory_engine/rules.py`  
**위치**: `compute_theory_result()` 함수 내 INDEX 조회 부분

```python
# rules.py 상단 import 추가
from .optimizers.index_fallback import get_index_fallback

# compute_theory_result() 함수 내 수정 (약 라인 474-495)
# 기존:
    # 2. INDEX 조회
    cumulative_pct = None
    if "INDEX" in excel_data:
        index_result = lookup_index(...)
        
# 수정:
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
    
    # INDEX 조회 실패 시 폴백
    if not index_result or not index_result.get("found"):
        logger.warning("INDEX 조회 실패, RAWSCORE 폴백 사용")
        fallback = get_index_fallback()
        index_result = fallback.calculate_from_rawscore(
            korean_conv, math_conv, inq1_conv, inq2_conv,
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
        })
```

---

## 🔧 Task 3: 대학명 Alias 시스템 (90분)

### 3.1 현재 문제점

```python
# cutoff_extractor.py:114-118 - 단순 패턴 매칭만 지원
patterns.append(f"{university}{major}")  # "가천의학" ✅
# "연세대" → "연대" 매핑 없음 ❌
```

### 3.2 수정 코드

**파일**: `theory_engine/cutoff/cutoff_extractor.py`  
**위치**: 클래스 상단에 UNIVERSITY_ALIASES 추가 및 `_find_program_column()` 수정

```python
class CutoffExtractor:
    """커트라인 자동 추출기 v2 (Alias 지원)"""

    # ============================================================
    # 대학명 Alias 매핑 (30+ 대학)
    # ============================================================
    UNIVERSITY_ALIASES: Dict[str, List[str]] = {
        # === SKY ===
        "서울대": ["서울", "서대", "서울대학교", "SNU"],
        "연세대": ["연대", "연세", "연세대학교", "연대의", "연세대 의"],
        "고려대": ["고대", "고려", "고려대학교", "KU"],
        
        # === 의대 (가나다순) ===
        "가천대": ["가천", "가천대학교"],
        "가톨릭대": ["가톨릭", "가대", "가톨릭의대"],
        "강원대": ["강원", "강대"],
        "건국대": ["건대", "건국", "건국대학교"],
        "건양대": ["건양"],
        "경북대": ["경북", "경대"],
        "경상대": ["경상"],
        "경희대": ["경희", "경대"],
        "계명대": ["계명"],
        "고신대": ["고신"],
        "단국대": ["단대", "단국"],
        "대구가톨릭대": ["대가대", "대구가톨릭"],
        "동국대": ["동대", "동국"],
        "동아대": ["동아"],
        "부산대": ["부대", "부산"],
        "순천향대": ["순천향", "순대"],
        "아주대": ["아주"],
        "연세대(원주)": ["연대원주", "원주연대", "연대 원주"],
        "영남대": ["영남"],
        "울산대": ["울산", "울대"],
        "을지대": ["을지"],
        "인제대": ["인제"],
        "인하대": ["인하"],
        "전남대": ["전남", "전대"],
        "전북대": ["전북"],
        "제주대": ["제주"],
        "조선대": ["조선"],
        "중앙대": ["중대", "중앙"],
        "차의과대": ["차의대", "차대", "차의과"],
        "충남대": ["충남"],
        "충북대": ["충북"],
        "한림대": ["한림"],
        "한양대": ["한대", "한양", "한양대학교"],
        
        # === 주요 대학 ===
        "성균관대": ["성대", "성균관", "SKKU"],
        "서강대": ["서강"],
        "이화여대": ["이대", "이화"],
        "한국외대": ["외대", "한국외대"],
        "홍익대": ["홍대", "홍익"],
        "숙명여대": ["숙대", "숙명"],
        "경기대": ["경기"],
        "국민대": ["국민", "국대"],
        "세종대": ["세종"],
        "숭실대": ["숭실"],
        "광운대": ["광운"],
        "명지대": ["명지"],
        "상명대": ["상명"],
        "서울시립대": ["시립대", "서울시립"],
        
        # === 지방 거점 ===
        "부경대": ["부경"],
        "경남대": ["경남"],
        "창원대": ["창원"],
        "충청대": ["충청"],
    }
    
    # 역매핑 자동 생성
    ALIAS_TO_OFFICIAL: Dict[str, str] = {}
    
    @classmethod
    def _build_alias_reverse_map(cls):
        """별칭 → 공식 대학명 역매핑"""
        if cls.ALIAS_TO_OFFICIAL:
            return
        for official, aliases in cls.UNIVERSITY_ALIASES.items():
            cls.ALIAS_TO_OFFICIAL[official] = official
            for alias in aliases:
                cls.ALIAS_TO_OFFICIAL[alias] = official
    
    def __init__(self, percentage_df: pd.DataFrame):
        self._build_alias_reverse_map()
        # ... 기존 __init__ 코드 ...
    
    def _normalize_university(self, name: str) -> str:
        """대학명 정규화"""
        if not name:
            return ""
        # 공백 제거
        name = name.replace(" ", "")
        # "대학교" → "대" 축약
        name = name.replace("대학교", "대")
        # 특수문자 제거
        name = re.sub(r'[·\-_()]', '', name)
        return name
    
    def _get_official_university(self, name: str) -> str:
        """별칭 → 공식 대학명"""
        normalized = self._normalize_university(name)
        
        # 정확 매칭
        if normalized in self.ALIAS_TO_OFFICIAL:
            return self.ALIAS_TO_OFFICIAL[normalized]
        
        # 부분 매칭
        for alias, official in self.ALIAS_TO_OFFICIAL.items():
            if alias in normalized or normalized in alias:
                return official
        
        return name
    
    def _find_program_column(
        self,
        university: str,
        major: str,
        track: str = ""
    ) -> Optional[str]:
        """대학/전공에 해당하는 컬럼 찾기 (v2: Alias 지원)"""
        import re
        
        # 1. 공식 대학명 변환
        official_univ = self._get_official_university(university)
        
        # 2. 모든 별칭 수집
        all_names = [official_univ]
        if official_univ in self.UNIVERSITY_ALIASES:
            all_names.extend(self.UNIVERSITY_ALIASES[official_univ])
        all_names.append(university)  # 원본도 추가
        
        # 3. 패턴 생성 (우선순위 순)
        patterns = []
        for univ_name in all_names:
            patterns.append(f"{univ_name}{major}")           # "가천의학"
            patterns.append(f"{univ_name} {major}")          # "가천 의학"
            if track:
                patterns.append(f"{univ_name}{major} {track}")  # "가천의학 이과"
                patterns.append(f"{univ_name}{major}{track}")   # "가천의학이과"
                patterns.append(f"{univ_name} {major} {track}") # "가천 의학 이과"
        
        # 4. 정확한 매칭
        for col in self.df.columns:
            col_str = str(col)
            for pattern in patterns:
                if pattern == col_str:
                    logger.debug(f"정확 매칭: '{pattern}' → '{col_str}'")
                    return col
        
        # 5. 포함 매칭 (대학명 + 전공 모두 포함)
        for col in self.df.columns:
            col_str = str(col)
            col_normalized = self._normalize_university(col_str)
            
            for univ_name in all_names:
                univ_normalized = self._normalize_university(univ_name)
                major_normalized = self._normalize_university(major)
                
                if univ_normalized in col_normalized and major_normalized in col_normalized:
                    # track도 확인
                    if not track or track in col_str:
                        logger.debug(f"포함 매칭: '{univ_name}+{major}' → '{col_str}'")
                        return col
        
        # 6. 퍼지 매칭 (RapidFuzz 사용 가능 시)
        try:
            from rapidfuzz import fuzz, process
            
            best_pattern = f"{official_univ}{major}"
            result = process.extractOne(
                query=best_pattern,
                choices=list(self.df.columns),
                scorer=fuzz.WRatio,
                score_cutoff=70
            )
            if result:
                logger.debug(f"퍼지 매칭: '{best_pattern}' → '{result[0]}' (score={result[1]})")
                return result[0]
        except ImportError:
            pass
        
        # 7. 대학명만 매칭 (마지막 수단)
        for col in self.df.columns:
            col_str = str(col)
            for univ_name in all_names:
                if univ_name in col_str:
                    logger.debug(f"대학 매칭: '{univ_name}' → '{col_str}'")
                    return col
        
        logger.warning(f"컬럼 없음: {university}({official_univ}){major}")
        return None
```

---

## 🤖 Claude 에이전트 CLI 프롬프트

아래 프롬프트를 Claude Code CLI에서 실행하세요.

### 프롬프트 1: RAWSCORE 탐구과목 수정 (90분)

```
당신은 Theory Engine v3.0 개발자입니다. 다음 작업을 수행하세요:

## 작업 목표
RAWSCORE 탐구과목 조회 성공률을 40% → 90%+로 향상

## 문제 상황
- 현재 rules.py의 convert_raw_to_standard()가 "영역" 컬럼만 검색
- 탐구과목은 영역="탐구" + 과목명="물리학 Ⅰ" 구조
- 결과: 국어/수학만 성공, 탐구과목 전체 실패

## 작업 내용
1. C:\Neoprime\theory_engine\rules.py 파일 읽기
2. convert_raw_to_standard() 함수를 다단계 매칭으로 교체:
   - Stage 1: 영역 컬럼 직접 매칭 (국어, 수학)
   - Stage 2: 과목명 컬럼 직접 매칭 (탐구과목)
   - Stage 3: 영역="탐구" + 과목명 퍼지 매칭
   - Stage 4: 전체 퍼지 매칭 (최후 수단)
3. 각 Stage별 로깅 추가
4. 테스트 실행: python -m pytest tests/test_integration.py -v -k "rawscore"

## 주의사항
- SubjectMatcher는 이미 구현됨, get_subject_matcher() 사용
- normalize_subject() 함수 재사용
- match_type 필드에 사용된 Stage 기록
- 기존 테스트 호환성 유지

## 예상 결과
- 물리학 Ⅰ, 화학 Ⅰ, 생명과학 Ⅰ, 지구과학 Ⅰ 등 탐구과목 변환 성공
- 국어/수학 기존 동작 유지

작업을 시작하세요.
```

### 프롬프트 2: INDEX 우회 로직 (60분)

```
당신은 Theory Engine v3.0 개발자입니다. 다음 작업을 수행하세요:

## 작업 목표
INDEX 조회 성공률을 0% → 95%+로 향상 (우회 로직 구현)

## 문제 상황
- INDEX 시트 첫 컬럼이 "510gs0t20509" 같은 인코딩 키
- IndexOptimizer가 MultiIndex 0행으로 구축됨
- 결과: INDEX 조회 전체 실패

## 작업 내용
1. 새 파일 생성: C:\Neoprime\theory_engine\optimizers\index_fallback.py
   - IndexFallback 클래스 구현
   - RAWSCORE 누적% 가중평균 계산
   - 영어 등급 → 백분위 변환
   - 전국 등수 추정 로직
   - get_index_fallback() 싱글톤 함수

2. C:\Neoprime\theory_engine\rules.py 수정
   - 상단에 from .optimizers.index_fallback import get_index_fallback 추가
   - compute_theory_result() 함수 내 INDEX 조회 부분 수정:
     - INDEX 조회 실패 시 폴백 사용
     - match_type에 "fallback_rawscore_weighted" 기록

3. C:\Neoprime\theory_engine\optimizers\__init__.py 수정
   - IndexFallback, get_index_fallback 추가

4. 테스트 실행: python -m pytest tests/test_integration.py -v -k "index"

## 가중치 설정
korean: 0.28, math: 0.28, english: 0.14, inquiry1: 0.15, inquiry2: 0.15

## 예상 결과
- INDEX 조회 실패해도 cumulative_pct, national_rank 산출
- match_type이 "fallback_rawscore_weighted"로 기록

작업을 시작하세요.
```

### 프롬프트 3: 대학명 Alias (90분)

```
당신은 Theory Engine v3.0 개발자입니다. 다음 작업을 수행하세요:

## 작업 목표
대학 커트라인 조회 성공률을 67% → 95%+로 향상

## 문제 상황
- "연세대" vs "연대", "고려대" vs "고대" 등 Alias 미지원
- cutoff_extractor.py가 단순 패턴 매칭만 수행
- 결과: 상위권 대학(SKY 등) 커트라인 조회 실패

## 작업 내용
1. C:\Neoprime\theory_engine\cutoff\cutoff_extractor.py 수정
   - UNIVERSITY_ALIASES 딕셔너리 추가 (30+ 대학)
   - ALIAS_TO_OFFICIAL 역매핑 자동 생성
   - _normalize_university() 메서드 추가
   - _get_official_university() 메서드 추가
   - _find_program_column() 메서드 개선:
     - 공식 대학명 변환
     - 모든 별칭으로 패턴 생성
     - 정확 매칭 → 포함 매칭 → 퍼지 매칭 순서
     - rapidfuzz 옵션 (설치된 경우)

2. 테스트 케이스 추가:
   - ("연대", "의예", "이과") → 연세대의예
   - ("고대", "경영", "문과") → 고려대경영
   - ("서울", "공대", "이과") → 서울대공대

3. 테스트 실행: python -m pytest tests/test_integration.py -v -k "cutoff"

## 대학 Alias 목록 (필수)
- SKY: 서울대(서울,서대), 연세대(연대,연세), 고려대(고대,고려)
- 의대: 가천대(가천), 연세대원주(연대원주), 한양대(한대) 등 30+ 대학

## 예상 결과
- "연세대의예", "고려대경영" 등 상위권 대학 조회 성공
- 기존 "가천의학", "건국자연" 계속 작동

작업을 시작하세요.
```

### 프롬프트 4: 통합 테스트 및 검증 (30분)

```
당신은 Theory Engine v3.0 개발자입니다. 다음 검증 작업을 수행하세요:

## 작업 목표
전체 파이프라인 통합 테스트로 실작동률 98% 확인

## 작업 내용
1. 전체 테스트 실행:
   cd C:\Neoprime
   python -m pytest tests/ -v --tb=short

2. 통합 테스트 상세 실행:
   python -m pytest tests/test_integration.py -v

3. 실제 데이터 테스트:
   python -c "
   from theory_engine.loader import load_workbook
   from theory_engine.rules import compute_theory_result, convert_raw_to_standard
   from theory_engine.model import StudentProfile, ExamScore, TargetProgram
   from theory_engine.constants import Track

   excel_data = load_workbook()
   
   # 탐구과목 테스트
   subjects = ['물리학 Ⅰ', '화학 Ⅰ', '생명과학 Ⅰ', '지구과학 Ⅰ']
   for subj in subjects:
       result = convert_raw_to_standard(excel_data['RAWSCORE'], subj, 45)
       status = '✅' if result['found'] else '❌'
       print(f'{status} {subj}: {result.get(\"match_type\", \"FAIL\")}')
   
   # 전체 파이프라인 테스트
   profile = StudentProfile(
       track=Track.SCIENCE,
       korean=ExamScore('국어', raw_total=85),
       math=ExamScore('수학', raw_total=82),
       english_grade=2,
       history_grade=3,
       inquiry1=ExamScore('물리학 Ⅰ', raw_total=47),
       inquiry2=ExamScore('화학 Ⅰ', raw_total=45),
       targets=[
           TargetProgram('연세대', '의예'),
           TargetProgram('고려대', '의예'),
           TargetProgram('가천', '의학'),
       ]
   )
   
   result = compute_theory_result(excel_data, profile)
   print(f'\\nINDEX: {result.raw_components.get(\"index_match_type\")}')
   print(f'누적%: {result.raw_components.get(\"cumulative_pct\")}')
   for prog in result.program_results:
       status = '✅' if prog.cutoff_normal else '❌'
       print(f'{status} {prog.target.university}{prog.target.major}: {prog.level_theory.value}')
   "

4. 결과 요약 보고

## 기대 결과
- 테스트 통과율: 38/38 (100%)
- RAWSCORE 탐구과목: 4/4 (100%)
- INDEX 폴백: cumulative_pct 산출
- 대학 커트라인: 연세대의예, 고려대의예 조회 성공

검증을 시작하세요.
```

---

## 📊 실행 체크리스트

### Task 1 완료 기준 (90분)
- [ ] rules.py convert_raw_to_standard() 수정
- [ ] Stage 1-4 다단계 매칭 구현
- [ ] 탐구과목 테스트 통과 (물리학Ⅰ, 화학Ⅰ, 생명과학Ⅰ, 지구과학Ⅰ)
- [ ] 기존 국어/수학 테스트 유지

### Task 2 완료 기준 (60분)
- [ ] index_fallback.py 신규 생성
- [ ] rules.py에 폴백 로직 통합
- [ ] optimizers/__init__.py 업데이트
- [ ] INDEX 폴백 테스트 통과

### Task 3 완료 기준 (90분)
- [ ] cutoff_extractor.py UNIVERSITY_ALIASES 추가
- [ ] _find_program_column() 개선
- [ ] 연세대/고려대/서울대 조회 테스트 통과
- [ ] 기존 가천/건국 테스트 유지

### 최종 검증 (30분)
- [ ] python -m pytest tests/ -v 전체 통과
- [ ] 탐구과목 4/4 성공
- [ ] INDEX 폴백 동작
- [ ] 상위권 대학 커트라인 조회 성공
- [ ] 실작동률 95%+ 달성

---

## 🎯 예상 결과

| 지표 | 현재 | 목표 | 달성 방법 |
|------|------|------|----------|
| **RAWSCORE 탐구과목** | 40% | **95%+** | 다단계 매칭 |
| **INDEX 조회** | 0% | **95%+** | RAWSCORE 폴백 |
| **대학 커트라인** | 67% | **95%+** | Alias 시스템 |
| **전체 실작동률** | 58% | **98%** | 위 3개 조합 |

---

**작성일**: 2026-01-18  
**소요 시간**: 총 6시간 (Task1: 90분, Task2: 60분, Task3: 90분, 검증: 30분)  
**담당**: Claude 에이전트 CLI  

**END OF DEVELOPMENT PLAN**
