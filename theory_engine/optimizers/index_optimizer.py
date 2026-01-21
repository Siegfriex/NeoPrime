"""
INDEX 시트 조회 최적화

20만 행을 O(1)에 조회하기 위한 MultiIndex 기반 최적화
"""

import pandas as pd
import numpy as np
import logging
from typing import Dict, Optional, Tuple, Any

logger = logging.getLogger(__name__)


class IndexOptimizer:
    """INDEX 시트 조회 최적화 (20만 행 대응)"""

    # 컬럼명 매핑 (실제 INDEX 시트 구조 기반)
    COLUMN_MAPPING = {
        'Unnamed: 1': 'korean_std',
        'Unnamed: 2': 'math_std',
        'Unnamed: 3': 'inq1_std',
        'Unnamed: 4': 'inq2_std',
        'Unnamed: 5': 'track',
        'Unnamed: 6': 'percentile_sum',
        'Unnamed: 7': 'national_rank',
        'Unnamed: 8': 'cumulative_pct',
    }

    KEY_COLUMNS = ['korean_std', 'math_std', 'inq1_std', 'inq2_std', 'track']
    VALUE_COLUMNS = ['percentile_sum', 'national_rank', 'cumulative_pct']

    def __init__(self, index_df: pd.DataFrame):
        """
        Args:
            index_df: INDEX 시트 원본 DataFrame
        """
        self.raw_df = index_df.copy()
        self._cache: Dict[Tuple, Dict] = {}
        self.use_multiindex = False
        self._build_optimized_index()

    def _build_optimized_index(self):
        """MultiIndex 구축"""
        logger.info(f"INDEX 최적화 시작: {len(self.raw_df)}행")

        # 1. 컬럼명 매핑
        self.df = self.raw_df.copy()

        # 실제 컬럼명 확인
        logger.debug(f"원본 컬럼: {list(self.df.columns)[:15]}")

        # 매핑 적용
        rename_map = {}
        for old_name, new_name in self.COLUMN_MAPPING.items():
            if old_name in self.df.columns:
                rename_map[old_name] = new_name

        if rename_map:
            self.df = self.df.rename(columns=rename_map)
            logger.info(f"컬럼 매핑: {len(rename_map)}개")

        # 첫 번째 컬럼이 INDEX면 그대로 사용
        if 'INDEX' in self.df.columns:
            logger.info("INDEX 컬럼 발견 - 기존 인코딩 사용")
            self.index_col = 'INDEX'
        else:
            self.index_col = None

        # 2. 필요한 컬럼 확인
        available_keys = [c for c in self.KEY_COLUMNS if c in self.df.columns]
        logger.info(f"사용 가능한 키: {available_keys}")

        if len(available_keys) >= 4:
            # MultiIndex 구축 시도
            try:
                # NaN 제거
                self.df = self.df.dropna(subset=available_keys)

                # 타입 변환 (숫자로)
                for col in available_keys:
                    if col in self.df.columns and col != 'track':
                        self.df[col] = pd.to_numeric(self.df[col], errors='coerce')

                # MultiIndex 설정
                self.indexed_df = self.df.set_index(available_keys)
                self.indexed_df = self.indexed_df.sort_index()
                self.use_multiindex = True

                logger.info(f"MultiIndex 구축 완료: {len(self.indexed_df)}행")

            except Exception as e:
                logger.warning(f"MultiIndex 구축 실패: {e}")
                self.use_multiindex = False
        else:
            logger.warning(f"키 컬럼 부족 ({len(available_keys)}개), 기본 인덱스 사용")
            self.use_multiindex = False

    def lookup(
        self,
        korean_std: int,
        math_std: int,
        inq1_std: int,
        inq2_std: int,
        track: str,
        fuzzy: bool = True
    ) -> Dict[str, Any]:
        """
        점수 조합으로 INDEX 행 조회

        Args:
            korean_std: 국어 표준점수
            math_std: 수학 표준점수
            inq1_std: 탐구1 표준점수
            inq2_std: 탐구2 표준점수
            track: 계열 ("이과" | "문과")
            fuzzy: True면 근사 검색 허용

        Returns:
            {
                'found': True,
                'exact_match': True,
                'index_key': '130-135-65-62-이과',
                'percentile_sum': 390.5,
                'national_rank': 1234,
                'cumulative_pct': 98.5
            }
        """
        key = (korean_std, math_std, inq1_std, inq2_std, track)
        index_key = f"{korean_std}-{math_std}-{inq1_std}-{inq2_std}-{track}"

        # 캐시 확인
        if key in self._cache:
            return self._cache[key]

        result = {
            'found': False,
            'exact_match': False,
            'index_key': index_key,
            'percentile_sum': None,
            'national_rank': None,
            'cumulative_pct': None,
        }

        if self.use_multiindex:
            # MultiIndex 검색 (빠름)
            try:
                if key in self.indexed_df.index:
                    row = self.indexed_df.loc[key]
                    result = self._extract_result(row, index_key, exact=True)
                elif fuzzy:
                    result = self._fuzzy_lookup(key, index_key)
            except KeyError:
                if fuzzy:
                    result = self._fuzzy_lookup(key, index_key)
        else:
            # 기본 검색 (느림)
            result = self._basic_lookup(key, index_key)
            if not result['found'] and fuzzy:
                result = self._fuzzy_lookup_basic(key, index_key)

        self._cache[key] = result
        return result

    def _basic_lookup(self, key: Tuple, index_key: str) -> Dict[str, Any]:
        """기본 선형 검색"""
        korean, math, inq1, inq2, track = key

        # 컬럼이 있는지 확인
        if not all(col in self.df.columns for col in self.KEY_COLUMNS[:4]):
            # 숫자 컬럼으로 시도
            try:
                mask = (
                    (self.df.iloc[:, 1] == korean) &
                    (self.df.iloc[:, 2] == math) &
                    (self.df.iloc[:, 3] == inq1) &
                    (self.df.iloc[:, 4] == inq2)
                )
                result_df = self.df[mask]
            except Exception:
                return self._empty_result(index_key)
        else:
            mask = (
                (self.df['korean_std'] == korean) &
                (self.df['math_std'] == math) &
                (self.df['inq1_std'] == inq1) &
                (self.df['inq2_std'] == inq2)
            )
            result_df = self.df[mask]

        if result_df.empty:
            return self._empty_result(index_key)

        row = result_df.iloc[0]
        return self._extract_result(row, index_key, exact=True)

    def _extract_result(self, row, index_key: str, exact: bool) -> Dict[str, Any]:
        """결과 추출"""
        if isinstance(row, pd.Series):
            percentile_sum = row.get('percentile_sum', None)
            national_rank = row.get('national_rank', None)
            cumulative_pct = row.get('cumulative_pct', None)

            # 컬럼명이 없으면 인덱스로 접근
            if percentile_sum is None and len(row) > 0:
                try:
                    percentile_sum = row.iloc[0] if len(row) > 0 else None
                    national_rank = row.iloc[1] if len(row) > 1 else None
                    cumulative_pct = row.iloc[2] if len(row) > 2 else None
                except Exception:
                    pass
        else:
            percentile_sum = None
            national_rank = None
            cumulative_pct = None

        return {
            'found': True,
            'exact_match': exact,
            'index_key': index_key,
            'percentile_sum': float(percentile_sum) if pd.notna(percentile_sum) else None,
            'national_rank': int(national_rank) if pd.notna(national_rank) else None,
            'cumulative_pct': float(cumulative_pct) if pd.notna(cumulative_pct) else None,
        }

    def _empty_result(self, index_key: str) -> Dict[str, Any]:
        """빈 결과"""
        return {
            'found': False,
            'exact_match': False,
            'index_key': index_key,
            'percentile_sum': None,
            'national_rank': None,
            'cumulative_pct': None,
        }

    def _fuzzy_lookup(self, key: Tuple, index_key: str) -> Dict[str, Any]:
        """근사 검색 (MultiIndex 버전)"""
        korean, math, inq1, inq2, track = key

        try:
            # 계열 필터링
            track_df = self.indexed_df.xs(track, level='track', drop_level=False) if 'track' in self.indexed_df.index.names else self.indexed_df
        except KeyError:
            track_df = self.indexed_df

        if track_df.empty:
            result = self._empty_result(index_key)
            result['approximate'] = True
            return result

        # 거리 계산 (간단한 L1 거리)
        levels = track_df.index.to_frame()
        score_cols = ['korean_std', 'math_std', 'inq1_std', 'inq2_std']
        available_cols = [c for c in score_cols if c in levels.columns]

        if len(available_cols) < 4:
            result = self._empty_result(index_key)
            result['approximate'] = True
            return result

        scores = levels[available_cols].values.astype(float)
        target = np.array([korean, math, inq1, inq2][:len(available_cols)], dtype=float)
        distances = np.abs(scores - target).sum(axis=1)

        nearest_idx = distances.argmin()
        row = track_df.iloc[nearest_idx]

        result = self._extract_result(row, index_key, exact=False)
        result['approximate'] = True
        result['distance'] = int(distances[nearest_idx])

        logger.debug(f"근사 매칭: distance={result['distance']}")
        return result

    def _fuzzy_lookup_basic(self, key: Tuple, index_key: str) -> Dict[str, Any]:
        """근사 검색 (기본 버전)"""
        korean, math, inq1, inq2, track = key

        # 숫자 컬럼 추출
        try:
            if all(col in self.df.columns for col in self.KEY_COLUMNS[:4]):
                scores = self.df[self.KEY_COLUMNS[:4]].values.astype(float)
            else:
                scores = self.df.iloc[:, 1:5].values.astype(float)
        except Exception:
            result = self._empty_result(index_key)
            result['approximate'] = True
            return result

        target = np.array([korean, math, inq1, inq2], dtype=float)

        # NaN 제거
        valid_mask = ~np.isnan(scores).any(axis=1)
        if not valid_mask.any():
            result = self._empty_result(index_key)
            result['approximate'] = True
            return result

        valid_scores = scores[valid_mask]
        valid_indices = np.where(valid_mask)[0]

        distances = np.abs(valid_scores - target).sum(axis=1)
        nearest_local_idx = distances.argmin()
        nearest_idx = valid_indices[nearest_local_idx]

        row = self.df.iloc[nearest_idx]
        result = self._extract_result(row, index_key, exact=False)
        result['approximate'] = True
        result['distance'] = int(distances[nearest_local_idx])

        return result

    def get_percentile_from_rawscore(
        self,
        korean_percentile: float,
        math_percentile: float,
        inq1_percentile: float,
        inq2_percentile: float
    ) -> float:
        """
        개별 백분위로부터 누적백분위 계산 (간단 버전)

        Note:
            INDEX 조회가 실패할 경우의 대안
        """
        total = korean_percentile + math_percentile + inq1_percentile + inq2_percentile
        return total

    def get_stats(self) -> Dict[str, Any]:
        """통계 정보"""
        return {
            'total_rows': len(self.raw_df),
            'indexed_rows': len(self.indexed_df) if self.use_multiindex else 0,
            'cache_size': len(self._cache),
            'use_multiindex': self.use_multiindex,
        }


# 테스트 코드
if __name__ == "__main__":
    import sys
    from pathlib import Path

    # 프로젝트 루트 추가
    sys.path.insert(0, str(Path(__file__).parent.parent.parent))

    logging.basicConfig(level=logging.INFO)

    print("=" * 60)
    print("INDEX 최적화 테스트")
    print("=" * 60)

    try:
        from theory_engine.loader import load_workbook
        from theory_engine.config import EXCEL_PATH

        print(f"\n엑셀 로드: {EXCEL_PATH}")
        data = load_workbook(EXCEL_PATH)

        if "INDEX" in data:
            print(f"INDEX 시트: {data['INDEX'].shape}")

            optimizer = IndexOptimizer(data["INDEX"])
            print(f"\n통계: {optimizer.get_stats()}")

            # 테스트 조회
            import time

            test_cases = [
                (130, 135, 65, 62, "이과"),
                (140, 145, 70, 68, "이과"),
                (120, 125, 60, 58, "문과"),
            ]

            print("\n테스트 조회:")
            for korean, math, inq1, inq2, track in test_cases:
                start = time.time()
                result = optimizer.lookup(korean, math, inq1, inq2, track)
                elapsed = (time.time() - start) * 1000

                status = "FOUND" if result['found'] else "NOT_FOUND"
                approx = " (근사)" if result.get('approximate') else ""
                print(f"  {status}{approx}: ({korean},{math},{inq1},{inq2},{track}) "
                      f"→ percentile_sum={result['percentile_sum']}, "
                      f"time={elapsed:.2f}ms")
        else:
            print("INDEX 시트 없음")

    except Exception as e:
        print(f"테스트 실패: {e}")
        import traceback
        traceback.print_exc()
