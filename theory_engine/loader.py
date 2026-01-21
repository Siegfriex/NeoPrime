"""
Theory Engine 데이터 로더

- 엑셀 파일 로드
- 시트별 전처리
- INDEX 시트 최적화 (MultiIndex)
- PERCENTAGE 시트 정규화 (Wide → Long)
"""

import pandas as pd
import logging
import os
from typing import Dict, Optional, Tuple
from pathlib import Path

from .config import (
    EXCEL_PATH,
    SHEET_CONFIG,
    INDEX_KEY_COLUMNS,
)
from .utils import (
    validate_sheets,
    validate_columns,
    cast_numeric_columns,
    log_dtypes,
    check_data_quality,
)

logger = logging.getLogger(__name__)

# ============================================================
# 워크북 캐시 (mtime 기반)
# ============================================================
_workbook_cache: Dict[Tuple[str, bool], Dict[str, pd.DataFrame]] = {}
_workbook_mtime: Dict[Tuple[str, bool], float] = {}


def clear_workbook_cache() -> None:
    """워크북 캐시 초기화 (테스트/개발용)"""
    _workbook_cache.clear()
    _workbook_mtime.clear()


# ============================================================
# 전체 워크북 로드
# ============================================================
def load_workbook(
    path: Optional[str] = None,
    strict: bool = False,
    use_cache: bool = True
) -> Dict[str, pd.DataFrame]:
    """
    엑셀 파일 전체 로드
    
    Args:
        path: 엑셀 파일 경로 (None이면 config.EXCEL_PATH 사용)
        strict: 필수 시트 누락 시 에러 발생 여부
    
    Returns:
        {시트명: DataFrame} dict
    """
    if path is None:
        path = EXCEL_PATH

    path_obj = Path(path).resolve()

    # 파일 존재 확인
    if not path_obj.exists():
        raise FileNotFoundError(f"엑셀 파일 없음: {path}")

    # 캐시 히트 검사 (mtime 기반)
    cache_key = (str(path_obj), bool(strict))
    current_mtime = os.path.getmtime(path_obj)
    if use_cache and cache_key in _workbook_cache:
        if _workbook_mtime.get(cache_key) == current_mtime:
            logger.debug(f"엑셀 워크북 캐시 히트: {path_obj}")
            # dict는 얕은 복사(키 추가/삭제 방지), DataFrame은 공유(읽기 전제)
            return dict(_workbook_cache[cache_key])
        else:
            logger.debug(f"엑셀 워크북 캐시 무효화(mtime 변경): {path_obj}")

    logger.info(f"엑셀 파일 로드 시작: {path_obj}")
    
    # ExcelFile 객체 생성
    xlsx = pd.ExcelFile(str(path_obj))
    
    # 시트 검증
    sheet_status = validate_sheets(xlsx, strict=strict)
    
    # 시트별 로드
    sheets = {}
    for sheet_name, config in SHEET_CONFIG.items():
        if config.skip:
            logger.debug(f"[{sheet_name}] 건너뜀 (skip=True)")
            continue
        
        if not sheet_status.get(sheet_name, False):
            if config.required:
                logger.error(f"[{sheet_name}] 필수 시트 없음!")
            else:
                logger.debug(f"[{sheet_name}] 선택 시트 없음, 건너뜀")
            continue
        
        try:
            # 시트 로드
            df = pd.read_excel(
                xlsx,
                sheet_name=sheet_name,
                header=config.header,
                skiprows=config.skiprows
            )
            
            # 컬럼 검증
            missing = validate_columns(df, sheet_name)
            if missing and strict:
                raise ValueError(f"[{sheet_name}] 필수 컬럼 누락: {missing}")
            
            # 타입 캐스팅
            df = cast_numeric_columns(df, sheet_name)
            
            # 데이터 품질 체크
            quality = check_data_quality(df, sheet_name)
            
            # 로깅
            log_dtypes(df, sheet_name)
            
            sheets[sheet_name] = df
            logger.info(f"[{sheet_name}] 로드 완료: {df.shape}")
            
        except Exception as e:
            logger.error(f"[{sheet_name}] 로드 실패: {e}")
            if strict:
                raise
    
    logger.info(f"엑셀 로드 완료: {len(sheets)}개 시트")

    # 캐시 저장
    if use_cache:
        _workbook_cache[cache_key] = sheets
        _workbook_mtime[cache_key] = current_mtime

    return sheets


# ============================================================
# RAWSCORE 시트 로드
# ============================================================
def load_rawscore(
    path: Optional[str] = None
) -> pd.DataFrame:
    """
    RAWSCORE 시트 로드
    
    컬럼:
    - 영역 (국어/수학/영어/탐구1/탐구2)
    - 과목명
    - 원점수 (또는 공통+선택)
    - 표준점수
    - 백분위
    - 등급
    - 누적%
    
    Returns:
        RAWSCORE DataFrame
    """
    sheets = load_workbook(path)
    df = sheets.get("RAWSCORE")
    
    if df is None:
        raise ValueError("RAWSCORE 시트가 없습니다")
    
    # 필수 컬럼 확인
    required = ["영역", "과목명"]
    missing = [col for col in required if col not in df.columns]
    if missing:
        logger.warning(f"RAWSCORE 일부 필수 컬럼 누락: {missing}")
        logger.info(f"실제 컬럼: {list(df.columns)[:10]}")
    
    logger.info(f"RAWSCORE 로드: {len(df)}행")
    return df


# ============================================================
# INDEX 시트 로드 (최적화)
# ============================================================
def load_index_optimized(
    path: Optional[str] = None
) -> pd.DataFrame:
    """
    INDEX 시트 로드 (20만 행 최적화)
    
    MultiIndex 구성:
    - (korean_std, math_std, inq1_std, inq2_std, track)
    
    조회 예시:
    >>> df.loc[(142, 145, 68, 67, "이과")]
    
    Returns:
        INDEX DataFrame (또는 MultiIndex)
    
    Note:
        실제 컬럼명 확인 후 MultiIndex 설정 필요
    """
    sheets = load_workbook(path)
    df = sheets.get("INDEX")
    
    if df is None:
        raise ValueError("INDEX 시트가 없습니다")
    
    # 컬럼명 확인 (실제 엑셀 확인 필요)
    logger.info(f"INDEX 컬럼 샘플: {list(df.columns)[:20]}")
    
    # TODO: 실제 엑셀의 INDEX 컬럼명 확인 후 MultiIndex 설정
    # 현재는 기본 DataFrame으로 반환
    
    logger.info(f"INDEX 로드: {len(df)}행")
    return df


# ============================================================
# PERCENTAGE 시트 로드 (정규화)
# ============================================================
def load_percentage_normalized(
    path: Optional[str] = None
) -> pd.DataFrame:
    """
    PERCENTAGE 시트 로드 → Long 형태로 정규화
    
    원본 (Wide): 1100+ 컬럼
    | % | ★백분위합 이과 | 가천의학 이과 | ... |
    |---|--------------|-------------|-----|
    | 0 | 300          | 99.6        | ... |
    
    변환 (Long):
    | percentile | program        | score |
    |-----------|----------------|-------|
    | 0.0       | 가천의학 이과   | 99.6  |
    
    Returns:
        Long 형태 DataFrame
    """
    sheets = load_workbook(path)
    df = sheets.get("PERCENTAGE")
    
    if df is None:
        raise ValueError("PERCENTAGE 시트가 없습니다")
    
    logger.info(f"PERCENTAGE 원본: {df.shape}")
    
    # 첫 컬럼 이름 확인
    percentile_col = df.columns[0]
    logger.debug(f"PERCENTAGE 첫 컬럼: {percentile_col}")
    
    # Wide → Long 변환
    df_long = df.melt(
        id_vars=[percentile_col],
        var_name="program",
        value_name="score"
    )
    
    # 컬럼명 정규화
    df_long = df_long.rename(columns={percentile_col: "percentile"})
    
    # NaN 제거
    df_long = df_long.dropna(subset=["score"])
    
    # 대학명-전공-계열 파싱 시도
    # 패턴: "가천의학 이과", "서울대자연 이과" 등
    # 공백으로 계열 분리
    df_long[["university_major", "track"]] = df_long["program"].str.rsplit(" ", n=1, expand=True)
    
    logger.info(f"PERCENTAGE 정규화: {len(df_long)}행")
    return df_long


def load_percentage_raw(
    path: Optional[str] = None
) -> pd.DataFrame:
    """
    PERCENTAGE 시트 원본 그대로 로드 (Wide 형태)
    
    Returns:
        Wide 형태 DataFrame
    """
    sheets = load_workbook(path)
    df = sheets.get("PERCENTAGE")
    
    if df is None:
        raise ValueError("PERCENTAGE 시트가 없습니다")
    
    logger.info(f"PERCENTAGE 원본 로드: {df.shape}")
    return df


# ============================================================
# RESTRICT 시트 로드
# ============================================================
def load_restrict(
    path: Optional[str] = None
) -> pd.DataFrame:
    """RESTRICT 시트: 결격사유 룰"""
    sheets = load_workbook(path)
    df = sheets.get("RESTRICT")
    
    if df is None:
        raise ValueError("RESTRICT 시트가 없습니다")
    
    logger.info(f"RESTRICT 로드: {len(df)}행")
    return df


# ============================================================
# COMPUTE 시트 로드
# ============================================================
def load_compute(
    path: Optional[str] = None
) -> pd.DataFrame:
    """COMPUTE 시트: 대학별 환산공식"""
    sheets = load_workbook(path)
    df = sheets.get("COMPUTE")
    
    if df is None:
        raise ValueError("COMPUTE 시트가 없습니다")
    
    logger.info(f"COMPUTE 로드: {len(df)}행")
    return df


if __name__ == "__main__":
    # 로깅 설정
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # 전체 워크북 로드 테스트
    try:
        sheets = load_workbook()
        print(f"\n로드된 시트: {list(sheets.keys())}")
        for name, df in sheets.items():
            print(f"  {name}: {df.shape}")
    except Exception as e:
        print(f"로드 실패: {e}")
