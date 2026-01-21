"""
커트라인 자동 추출기 v2 (대학명 Alias 지원)

PERCENTAGE 시트에서 대학/전공별 커트라인(80%/50%/20%) 추출
대학명 별칭(Alias) 시스템으로 다양한 표기 방식 지원
"""

import re
import pandas as pd
import numpy as np
import logging
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


class CutoffExtractor:
    """커트라인 자동 추출기 v2 (Alias 지원)"""

    # 기준 확률 라인
    CUTOFF_PERCENTILES = {
        # NOTE:
        # - PERCENTAGE 시트 첫 컬럼(%)은 0에 가까울수록 상위권(점수↑), 값이 커질수록 하위권(점수↓)입니다.
        # - 따라서 "적정/예상/소신" 커트라인은 상위% 기준 20/50/80을 사용합니다.
        "적정": 20.0,   # 상위 20%
        "예상": 50.0,   # 상위 50%
        "소신": 80.0,   # 상위 80%
    }

    # ============================================================
    # 대학명 Alias 매핑 (30+ 대학)
    # ============================================================
    UNIVERSITY_ALIASES: Dict[str, List[str]] = {
        # === SKY ===
        "서울대": ["서울", "서대", "서울대학교", "SNU", "서울대학"],
        "연세대": ["연대", "연세", "연세대학교", "연대의", "연세대 의", "연세대학"],
        "고려대": ["고대", "고려", "고려대학교", "KU", "고려대학"],

        # === 의대 (가나다순) ===
        "가천대": ["가천", "가천대학교", "가천의"],
        "가톨릭대": ["가톨릭", "가대", "가톨릭의대", "가톨릭대학교"],
        "강원대": ["강원", "강대", "강원대학교"],
        "건국대": ["건대", "건국", "건국대학교"],
        "건양대": ["건양", "건양대학교"],
        "경북대": ["경북", "경대", "경북대학교"],
        "경상대": ["경상", "경상대학교", "경상국립대"],
        "경희대": ["경희", "경희대학교"],
        "계명대": ["계명", "계명대학교"],
        "고신대": ["고신", "고신대학교"],
        "단국대": ["단대", "단국", "단국대학교"],
        "대구가톨릭대": ["대가대", "대구가톨릭", "대구가톨릭대학교"],
        "동국대": ["동대", "동국", "동국대학교"],
        "동아대": ["동아", "동아대학교"],
        "부산대": ["부대", "부산", "부산대학교"],
        "순천향대": ["순천향", "순대", "순천향대학교"],
        "아주대": ["아주", "아주대학교"],
        "연세대(원주)": ["연대원주", "원주연대", "연대 원주", "연세원주"],
        "영남대": ["영남", "영남대학교"],
        "울산대": ["울산", "울대", "울산대학교"],
        "을지대": ["을지", "을지대학교"],
        "인제대": ["인제", "인제대학교"],
        "인하대": ["인하", "인하대학교"],
        "전남대": ["전남", "전대", "전남대학교"],
        "전북대": ["전북", "전북대학교"],
        "제주대": ["제주", "제주대학교"],
        "조선대": ["조선", "조선대학교"],
        "중앙대": ["중대", "중앙", "중앙대학교"],
        "차의과대": ["차의대", "차대", "차의과", "차의과학대학교"],
        "충남대": ["충남", "충남대학교"],
        "충북대": ["충북", "충북대학교"],
        "한림대": ["한림", "한림대학교"],
        "한양대": ["한대", "한양", "한양대학교"],

        # === 주요 대학 ===
        "성균관대": ["성대", "성균관", "SKKU", "성균관대학교"],
        "서강대": ["서강", "서강대학교"],
        "이화여대": ["이대", "이화", "이화여자대학교"],
        "한국외대": ["외대", "한국외대", "한국외국어대학교"],
        "홍익대": ["홍대", "홍익", "홍익대학교"],
        "숙명여대": ["숙대", "숙명", "숙명여자대학교"],
        "경기대": ["경기", "경기대학교"],
        "국민대": ["국민", "국대", "국민대학교"],
        "세종대": ["세종", "세종대학교"],
        "숭실대": ["숭실", "숭실대학교"],
        "광운대": ["광운", "광운대학교"],
        "명지대": ["명지", "명지대학교"],
        "상명대": ["상명", "상명대학교"],
        "서울시립대": ["시립대", "서울시립", "서울시립대학교"],

        # === 지방 거점 ===
        "부경대": ["부경", "부경대학교"],
        "경남대": ["경남", "경남대학교"],
        "창원대": ["창원", "창원대학교"],
    }

    # 역매핑 (별칭 → 공식 대학명) - 클래스 변수로 초기화
    ALIAS_TO_OFFICIAL: Dict[str, str] = {}
    
    # ============================================================
    # 전공명 Alias 매핑
    # ============================================================
    MAJOR_ALIASES: Dict[str, List[str]] = {
        "의예": ["의학", "의대", "의예과"],
        "의학": ["의예", "의대", "의예과"],
        "치의예": ["치의학", "치대", "치의예과"],
        "치의학": ["치의예", "치대", "치의예과"],
        "한의예": ["한의학", "한의대", "한의예과"],
        "한의학": ["한의예", "한의대", "한의예과"],
        "약학": ["약대", "약학과"],
        "수의예": ["수의학", "수의대", "수의예과"],
        "수의학": ["수의예", "수의대", "수의예과"],
        "간호": ["간호학", "간호대", "간호학과"],
        "공대": ["공학", "공과대", "공학부"],
        "자연": ["자연과학", "이과", "자연계"],
        "인문": ["인문과학", "문과", "인문계"],
        "사범": ["사범대", "교육"],
        "경영": ["경영학", "상경", "경영학과"],
        "경제": ["경제학", "경제학과"],
        "법대": ["법학", "법학과"],
        "공공": ["공공정책", "행정"],
    }

    @classmethod
    def _build_alias_reverse_map(cls):
        """별칭 → 공식 대학명 역매핑 구축"""
        if cls.ALIAS_TO_OFFICIAL:
            return  # 이미 구축됨

        for official, aliases in cls.UNIVERSITY_ALIASES.items():
            # 공식 대학명 자체도 매핑
            cls.ALIAS_TO_OFFICIAL[cls._normalize_university(official)] = official
            cls.ALIAS_TO_OFFICIAL[cls._normalize_university(official.replace("대", ""))] = official  # "서울" → "서울대"

            # 모든 별칭 매핑
            for alias in aliases:
                cls.ALIAS_TO_OFFICIAL[cls._normalize_university(alias)] = official

        logger.debug(f"대학 Alias 역매핑 구축: {len(cls.ALIAS_TO_OFFICIAL)}개")

    def __init__(self, percentage_df: pd.DataFrame):
        """
        Args:
            percentage_df: PERCENTAGE 시트 DataFrame
        """
        # Alias 역매핑 구축
        self._build_alias_reverse_map()

        self.df = percentage_df.copy()
        self._cache: Dict[str, Dict] = {}
        # 마지막 매칭/보간 정보 (Explainability/디버깅용)
        self._last_match_info: Dict[str, Any] = {}
        self._last_score_lookup: Dict[str, Any] = {}
        self._analyze_structure()

    @staticmethod
    def _normalize_university(name: str) -> str:
        """대학명 정규화"""
        if not name:
            return ""
        # 공백 제거
        name = str(name).strip().replace(" ", "")
        # "대학교" → "대" 축약
        name = name.replace("대학교", "대")
        # 특수문자 제거
        name = re.sub(r'[·\-_()]', '', name)
        # 영문 소문자 통일 (SNU, KU 등)
        return name.lower()

    def _get_official_university(self, name: str) -> str:
        """별칭 → 공식 대학명 변환"""
        if not name:
            return name

        normalized = self._normalize_university(name)

        # 정확 매칭
        if normalized in self.ALIAS_TO_OFFICIAL:
            return self.ALIAS_TO_OFFICIAL[normalized]

        # 매칭 실패 시 원본 반환 (과도한 부분매칭은 오매핑 위험)
        return name

    def _analyze_structure(self):
        """시트 구조 분석"""
        logger.info(f"PERCENTAGE 시트 분석: {self.df.shape}")

        # 첫 컬럼 (누백/%) 확인
        self.percentile_col = self.df.columns[0]
        logger.info(f"누백 컬럼: '{self.percentile_col}'")

        # 대학/전공 컬럼 목록 (★, Unnamed 제외)
        self.program_columns = [
            col for col in self.df.columns[1:]
            if not str(col).startswith('Unnamed') and not str(col).startswith('★')
        ]
        logger.info(f"대학/전공 컬럼: {len(self.program_columns)}개")

        # 샘플 출력
        if self.program_columns:
            logger.debug(f"샘플 컬럼: {self.program_columns[:5]}")

    def extract_cutoffs(
        self,
        university: str,
        major: str,
        track: str = ""
    ) -> Dict[str, Optional[float]]:
        """
        대학/전공의 커트라인 추출

        Args:
            university: 대학명 (예: "서울대", "연세대", "가천")
            major: 전공명 (예: "의예", "공대", "의학")
            track: 계열 (선택, "이과" | "문과")

        Returns:
            {
                'found': True,
                'column': '가천의학 이과',
                'cutoff_safe': 97.5,    # 적정 (80%)
                'cutoff_normal': 95.0,  # 예상 (50%)
                'cutoff_risk': 92.0,    # 소신 (20%)
            }
        """
        cache_key = f"{university}_{major}_{track}"
        if cache_key in self._cache:
            return self._cache[cache_key]

        # 컬럼 찾기
        program_col = self._find_program_column(university, major, track)

        if program_col is None:
            result = {
                'found': False,
                'column': None,
                'cutoff_safe': None,
                'cutoff_normal': None,
                'cutoff_risk': None,
                'match_info': dict(self._last_match_info) if self._last_match_info else {},
            }
            self._cache[cache_key] = result
            return result

        # 커트라인 계산
        result = self._calculate_cutoffs(program_col)
        result['found'] = True
        result['column'] = program_col
        result['match_info'] = dict(self._last_match_info) if self._last_match_info else {}

        self._cache[cache_key] = result
        return result

    def _find_program_column(
        self,
        university: str,
        major: str,
        track: str = ""
    ) -> Optional[str]:
        """대학/전공에 해당하는 컬럼 찾기 (v2: Alias 지원)"""

        # 1. 공식 대학명 변환
        official_univ = self._get_official_university(university)

        # 매칭 메타 (Explainability)
        match_info: Dict[str, Any] = {
            "university_input": university,
            "university_official": official_univ,
            "university_method": "alias" if official_univ != university else "exact",
            "major_input": major,
            "major_used": major,
            "major_method": "exact",
            "alias_chain": [],
            "track": track,
            "match_stage": None,
            "fuzzy_score": None,
            "column": None,
        }

        # 2. 모든 별칭 수집
        all_univ_names = [official_univ]
        if official_univ in self.UNIVERSITY_ALIASES:
            all_univ_names.extend(self.UNIVERSITY_ALIASES[official_univ])
        if university not in all_univ_names:
            all_univ_names.append(university)  # 원본도 추가

        # 3. 패턴 생성 (우선순위 순)
        patterns = []
        for univ_name in all_univ_names:
            patterns.append(f"{univ_name}{major}")              # "가천의학"
            patterns.append(f"{univ_name} {major}")             # "가천 의학"
            if track:
                patterns.append(f"{univ_name}{major} {track}")  # "가천의학 이과"
                patterns.append(f"{univ_name}{major}{track}")   # "가천의학이과"
                patterns.append(f"{univ_name} {major} {track}") # "가천 의학 이과"

        # 4. 정확한 매칭 (우선순위 최고)
        for col in self.df.columns:
            col_str = str(col)
            for pattern in patterns:
                if pattern == col_str:
                    logger.debug(f"정확 매칭: '{pattern}' → '{col_str}'")
                    match_info["match_stage"] = "exact"
                    match_info["column"] = col_str
                    self._last_match_info = match_info
                    return col

        # 5. 포함 매칭 (대학명 + 전공 모두 포함)
        for col in self.df.columns:
            col_str = str(col)
            col_normalized = self._normalize_university(col_str)

            for univ_name in all_univ_names:
                univ_normalized = self._normalize_university(univ_name)
                major_normalized = self._normalize_university(major)

                if univ_normalized in col_normalized and major_normalized in col_normalized:
                    # track도 확인 (있으면)
                    if not track or track in col_str:
                        logger.debug(f"포함 매칭: '{univ_name}+{major}' → '{col_str}'")
                        match_info["match_stage"] = "contains"
                        match_info["column"] = col_str
                        self._last_match_info = match_info
                        return col

        # 6. 전공 Alias 확장 매칭
        # "의예" → "의학", "의대" 등 유사 전공명으로 재시도
        major_aliases = self._get_major_aliases(major)
        for major_alias in major_aliases:
            for col in self.df.columns:
                col_str = str(col)
                col_normalized = self._normalize_university(col_str)
                major_alias_normalized = self._normalize_university(major_alias)
                for univ_name in all_univ_names:
                    univ_normalized = self._normalize_university(univ_name)
                    if univ_normalized in col_normalized and major_alias_normalized in col_normalized:
                        if not track or track in col_str:
                            logger.info(f"전공Alias 매칭: '{major}' → '{major_alias}' (컬럼: '{col_str}')")
                            match_info["match_stage"] = "major_alias"
                            match_info["major_used"] = major_alias
                            match_info["major_method"] = "alias"
                            match_info["alias_chain"] = [major, major_alias]
                            match_info["column"] = col_str
                            self._last_match_info = match_info
                            return col

        # 7. 퍼지 매칭 (rapidfuzz 사용 가능 시) - 마지막 보조 수단
        try:
            from rapidfuzz import fuzz, process

            best_pattern = f"{official_univ}{major}"
            if track:
                best_pattern = f"{best_pattern} {track}"

            result = process.extractOne(
                query=best_pattern,
                choices=[str(c) for c in self.program_columns],
                scorer=fuzz.WRatio,
                score_cutoff=80
            )
            if result:
                candidate = result[0]
                candidate_norm = self._normalize_university(candidate)
                if (
                    self._normalize_university(official_univ) in candidate_norm
                    and (not track or track in candidate)
                ):
                    logger.debug(f"퍼지 매칭: '{best_pattern}' → '{candidate}' (score={result[1]})")
                    for col in self.df.columns:
                        if str(col) == candidate:
                            match_info["match_stage"] = "fuzzy"
                            match_info["fuzzy_score"] = float(result[1])
                            match_info["column"] = candidate
                            self._last_match_info = match_info
                            return col
        except ImportError:
            pass  # rapidfuzz 없으면 스킵

        # 8. 대학+전공 원본 텍스트 매칭 (최후 수단)
        # 주의: 대학명만 매칭하면 오매칭 위험 ("연세대의예" → "연세간호" 방지)
        major_normalized = self._normalize_university(major)
        for col in self.df.columns:
            col_str = str(col)
            col_normalized = self._normalize_university(col_str)
            for univ_name in all_univ_names:
                univ_normalized = self._normalize_university(univ_name)
                if univ_normalized in col_normalized and major_normalized in col_normalized:
                    if not track or track in col_str:
                        logger.debug(f"대학+전공 매칭: '{univ_name}+{major}' → '{col_str}'")
                        match_info["match_stage"] = "raw_contains"
                        match_info["column"] = col_str
                        self._last_match_info = match_info
                        return col

        # 찾지 못함 - 반드시 대학+전공 조합 필요
        logger.warning(f"컬럼 없음: {university}({official_univ})+{major} (전공명 필수)")
        match_info["match_stage"] = "not_found"
        self._last_match_info = match_info
        return None

    def _get_major_aliases(self, major: str) -> List[str]:
        """전공명 별칭 반환"""
        return self.MAJOR_ALIASES.get(major, [])

    def _calculate_cutoffs(self, program_col: str) -> Dict[str, Optional[float]]:
        """커트라인 계산"""

        # 데이터 추출
        df_subset = self.df[[self.percentile_col, program_col]].copy()
        df_subset.columns = ['percentile', 'score']

        # NaN 제거 및 정렬
        df_subset = df_subset.dropna()
        df_subset['percentile'] = pd.to_numeric(df_subset['percentile'], errors='coerce')
        df_subset['score'] = pd.to_numeric(df_subset['score'], errors='coerce')
        df_subset = df_subset.dropna()
        df_subset = df_subset.sort_values('percentile')

        if len(df_subset) < 2:
            return {
                'cutoff_safe': None,
                'cutoff_normal': None,
                'cutoff_risk': None,
            }

        result = {}

        for name, pct in self.CUTOFF_PERCENTILES.items():
            try:
                # 보간으로 커트라인 계산
                score = np.interp(
                    pct,
                    df_subset['percentile'].values,
                    df_subset['score'].values
                )
                result[f'cutoff_{name}'] = round(float(score), 2)
            except Exception as e:
                logger.warning(f"커트라인 계산 실패 ({name}): {e}")
                result[f'cutoff_{name}'] = None

        # 키 이름 변환
        return {
            'cutoff_safe': result.get('cutoff_적정'),
            'cutoff_normal': result.get('cutoff_예상'),
            'cutoff_risk': result.get('cutoff_소신'),
        }

    def get_score_at_percentile(
        self,
        university: str,
        major: str,
        percentile: float,
        track: str = ""
    ) -> Optional[float]:
        """특정 누백에서의 환산점수 조회"""

        program_col = self._find_program_column(university, major, track)
        if program_col is None:
            return None

        df_subset = self.df[[self.percentile_col, program_col]].copy()
        df_subset.columns = ['pct', 'score']
        df_subset = df_subset.dropna()
        df_subset['pct'] = pd.to_numeric(df_subset['pct'], errors='coerce')
        df_subset['score'] = pd.to_numeric(df_subset['score'], errors='coerce')
        df_subset = df_subset.dropna().sort_values('pct')

        if len(df_subset) < 2:
            return None

        try:
            pct_value = float(percentile)
            pct_arr = df_subset['pct'].values
            score_arr = df_subset['score'].values

            # 정확 값 존재 여부 (float 오차 고려)
            exact_mask = np.isclose(pct_arr, pct_value, atol=1e-9)
            if exact_mask.any():
                score = score_arr[exact_mask.argmax()]
                interpolated = False
            else:
                score = np.interp(pct_value, pct_arr, score_arr)
                interpolated = True

            self._last_score_lookup = {
                "column": str(program_col),
                "percentile": pct_value,
                "interpolated": interpolated,
                "interpolation_method": "linear",
            }
            return round(float(score), 2)
        except Exception:
            return None

    def list_available_programs(self) -> List[str]:
        """사용 가능한 대학/전공 목록"""
        return self.program_columns

    def search_programs(self, keyword: str) -> List[str]:
        """키워드로 대학/전공 검색"""
        return [col for col in self.program_columns if keyword in str(col)]

    def get_stats(self) -> Dict:
        """통계 정보"""
        pct_col = self.df[self.percentile_col]
        pct_min = pct_col.min() if len(pct_col) > 0 else None
        pct_max = pct_col.max() if len(pct_col) > 0 else None

        return {
            'total_programs': len(self.program_columns),
            'percentile_range': (pct_min, pct_max),
            'total_rows': len(self.df),
            'cache_size': len(self._cache),
        }


# 테스트 코드
if __name__ == "__main__":
    import sys
    from pathlib import Path

    # 프로젝트 루트 추가
    sys.path.insert(0, str(Path(__file__).parent.parent.parent))

    logging.basicConfig(level=logging.INFO)

    print("=" * 60)
    print("커트라인 추출 테스트")
    print("=" * 60)

    try:
        from theory_engine.loader import load_workbook
        from theory_engine.config import EXCEL_PATH

        print(f"\n엑셀 로드: {EXCEL_PATH}")
        data = load_workbook(EXCEL_PATH)

        if "PERCENTAGE" in data:
            print(f"PERCENTAGE 시트: {data['PERCENTAGE'].shape}")

            extractor = CutoffExtractor(data["PERCENTAGE"])
            print(f"\n통계: {extractor.get_stats()}")

            # 사용 가능한 프로그램 목록
            programs = extractor.list_available_programs()
            print(f"\n사용 가능한 대학/전공: {len(programs)}개")
            if programs:
                print(f"샘플: {programs[:10]}")

            # 키워드 검색 테스트
            print("\n키워드 검색 테스트:")
            for keyword in ["가천", "의학", "서울"]:
                matches = extractor.search_programs(keyword)
                print(f"  '{keyword}': {len(matches)}개 매칭")
                if matches:
                    print(f"    예시: {matches[:3]}")

            # 커트라인 추출 테스트
            test_cases = [
                ("가천", "의학", "이과"),
                ("건국", "자연", "이과"),
                ("경기", "인문", "문과"),
                ("서울대", "공대", "이과"),
            ]

            print("\n커트라인 추출:")
            for univ, major, track in test_cases:
                result = extractor.extract_cutoffs(univ, major, track)
                if result['found']:
                    print(f"  FOUND: {univ}{major} {track}")
                    print(f"    컬럼: {result['column']}")
                    print(f"    적정: {result['cutoff_safe']}")
                    print(f"    예상: {result['cutoff_normal']}")
                    print(f"    소신: {result['cutoff_risk']}")
                else:
                    print(f"  NOT_FOUND: {univ}{major} {track}")
        else:
            print("PERCENTAGE 시트 없음")

    except Exception as e:
        print(f"테스트 실패: {e}")
        import traceback
        traceback.print_exc()
