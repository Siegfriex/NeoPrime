"""
Theory Engine 유틸리티

- 시트 존재 여부 검증
- 필수 컬럼 검증
- 타입 캐스팅
- 데이터 품질 체크
"""

import logging
from typing import Dict, List, Optional, Any
import pandas as pd

from .config import (
    SHEET_CONFIG,
    NUMERIC_PATTERNS,
    EXPLICIT_NUMERIC_COLUMNS,
    EXCLUDE_FROM_NUMERIC
)

logger = logging.getLogger(__name__)

# ============================================================
# 시트 검증
# ============================================================
def validate_sheets(
    xlsx: pd.ExcelFile,
    strict: bool = False
) -> Dict[str, bool]:
    """
    엑셀 파일의 시트 존재 여부 검증
    
    Args:
        xlsx: pd.ExcelFile 객체
        strict: True면 필수 시트 누락 시 에러 발생
    
    Returns:
        {시트명: 존재여부} dict
    
    Raises:
        ValueError: strict=True이고 필수 시트 누락 시
    """
    available = set(xlsx.sheet_names)
    result = {}
    
    for sheet_name, config in SHEET_CONFIG.items():
        exists = sheet_name in available
        result[sheet_name] = exists
        
        if not exists:
            if config.required:
                msg = f"[ERROR] 필수 시트 누락: {sheet_name}"
                if strict:
                    raise ValueError(msg)
                else:
                    logger.warning(msg)
            else:
                logger.debug(f"[INFO] 선택 시트 없음 (무시): {sheet_name}")
    
    # 예상치 못한 시트 경고
    expected = set(SHEET_CONFIG.keys())
    unexpected = available - expected
    if unexpected:
        logger.warning(f"[WARN] 알 수 없는 시트 발견: {unexpected}")
    
    return result


def validate_columns(
    df: pd.DataFrame,
    sheet_name: str
) -> List[str]:
    """
    시트의 필수 컬럼 존재 여부 검증
    
    Args:
        df: DataFrame
        sheet_name: 시트명
    
    Returns:
        누락된 컬럼 리스트
    """
    config = SHEET_CONFIG.get(sheet_name)
    if not config or not config.expected_columns:
        return []
    
    missing = []
    for col in config.expected_columns:
        if col not in df.columns:
            missing.append(col)
            logger.warning(f"[{sheet_name}] 필수 컬럼 누락: {col}")
    
    return missing


# ============================================================
# 타입 캐스팅
# ============================================================
def cast_numeric_columns(
    df: pd.DataFrame,
    sheet_name: str = ""
) -> pd.DataFrame:
    """
    숫자 컬럼 강제 변환
    
    로직:
    1. EXPLICIT_NUMERIC_COLUMNS에 있으면 무조건 변환
    2. EXCLUDE_FROM_NUMERIC에 있으면 제외
    3. NUMERIC_PATTERNS에 매칭되면 변환
    
    Args:
        df: DataFrame
        sheet_name: 시트명 (로깅용)
    
    Returns:
        타입 변환된 DataFrame (원본 수정 안 함)
    """
    df = df.copy()
    converted = []
    
    for col in df.columns:
        # 제외 대상
        if col in EXCLUDE_FROM_NUMERIC:
            continue
        
        should_convert = False
        
        # 명시적 지정
        if col in EXPLICIT_NUMERIC_COLUMNS:
            should_convert = True
        # 패턴 매칭
        elif any(pattern in str(col) for pattern in NUMERIC_PATTERNS):
            should_convert = True
        
        if should_convert:
            original_dtype = df[col].dtype
            df[col] = pd.to_numeric(df[col], errors='coerce')
            if df[col].dtype != original_dtype:
                converted.append(col)
    
    if converted:
        logger.info(f"[{sheet_name}] 숫자 변환: {len(converted)}개 컬럼")
        logger.debug(f"[{sheet_name}] 변환 컬럼: {converted[:10]}...")
    
    return df


def log_dtypes(df: pd.DataFrame, sheet_name: str) -> None:
    """dtype 추론 결과 로깅"""
    logger.info(f"[{sheet_name}] shape={df.shape}")
    logger.debug(f"[{sheet_name}] columns={list(df.columns)[:10]}...")
    logger.debug(f"[{sheet_name}] dtypes 샘플:\n{df.dtypes.head(10)}")


def check_data_quality(df: pd.DataFrame, sheet_name: str) -> Dict[str, Any]:
    """
    데이터 품질 체크
    
    Args:
        df: DataFrame
        sheet_name: 시트명
    
    Returns:
        {
            "null_count": {컬럼: null_개수},
            "duplicate_count": 중복_행_개수,
            "row_count": 총_행_개수
        }
    """
    null_count = df.isnull().sum().to_dict()
    null_count = {k: v for k, v in null_count.items() if v > 0}
    
    duplicate_count = df.duplicated().sum()
    
    quality = {
        "null_count": null_count,
        "duplicate_count": int(duplicate_count),
        "row_count": len(df)
    }
    
    if null_count and len(null_count) <= 5:
        logger.warning(f"[{sheet_name}] NULL 값 발견: {null_count}")
    elif null_count:
        logger.warning(f"[{sheet_name}] NULL 값 발견: {len(null_count)}개 컬럼")
    
    if duplicate_count > 0:
        logger.warning(f"[{sheet_name}] 중복 행 {duplicate_count}개")
    
    return quality


if __name__ == "__main__":
    # 간단한 테스트
    test_df = pd.DataFrame({
        "점수": ["100", "90", "80"],
        "이름": ["A", "B", "C"],
        "등급": ["1", "2", "3"]
    })
    
    result = cast_numeric_columns(test_df, "TEST")
    print("Original dtypes:")
    print(test_df.dtypes)
    print("\nConverted dtypes:")
    print(result.dtypes)
