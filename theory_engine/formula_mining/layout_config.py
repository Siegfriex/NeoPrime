"""
시트별 레이아웃 설정: 행/열 라벨 스캔 범위
"""

from typing import List, Dict


# 시트별 레이아웃 설정
SHEET_LAYOUT_CONFIG: Dict[str, Dict] = {
    "COMPUTE": {
        "row_label_scan_cols": ['A', 'B', 'C', 'D'],
        "col_header_scan_rows": list(range(1, 11)),  # 1~10행
        "note": "COMPUTE 시트: 대학/전형 정보는 A~D열, 헤더는 1~10행",
    },
    "RESTRICT": {
        "row_label_scan_cols": ['A', 'B', 'C', 'D'],
        "col_header_scan_rows": list(range(1, 11)),
        "note": "RESTRICT 시트: 결격사유 정보는 A~D열, 헤더는 1~10행",
    },
    # 기본값 (다른 시트)
    "default": {
        "row_label_scan_cols": ['A', 'B', 'C'],
        "col_header_scan_rows": list(range(1, 6)),
        "note": "기본 설정",
    },
}


def get_layout_config(sheet_name: str) -> Dict:
    """시트별 레이아웃 설정 반환"""
    return SHEET_LAYOUT_CONFIG.get(sheet_name, SHEET_LAYOUT_CONFIG["default"])
