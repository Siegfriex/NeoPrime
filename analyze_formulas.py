# ============================================================
# 수식 메타데이터 분석 스크립트
# NEO GOD 엔진 리버스 엔지니어링 지원
# ============================================================

import sys
import io
import json
from pathlib import Path
from typing import Dict, List, Any
import pandas as pd

# Windows 인코딩 설정
if sys.platform == 'win32':
    try:
        if hasattr(sys.stdout, 'reconfigure'):
            sys.stdout.reconfigure(encoding='utf-8')
        if hasattr(sys.stderr, 'reconfigure'):
            sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass


def load_all_formula_metadata(output_dir: str = './output') -> Dict[str, Any]:
    """모든 수식 메타데이터 파일 로드"""
    output_path = Path(output_dir)
    metadata_files = list(output_path.glob('*_formula_metadata.json'))
    
    all_metadata = {}
    for file_path in metadata_files:
        sheet_name = file_path.stem.replace('_formula_metadata', '')
        with open(file_path, 'r', encoding='utf-8') as f:
            all_metadata[sheet_name] = json.load(f)
    
    return all_metadata


def analyze_formula_dependencies(metadata: Dict[str, Any]) -> Dict[str, List[str]]:
    """수식 의존성 분석 (시트 간 참조 추출)"""
    dependencies = {}
    
    for sheet_name, data in metadata.items():
        sheet_deps = set()
        
        for col_name, formula_info in data.get('formula_samples', {}).items():
            formula = formula_info.get('formula', '')
            deps = formula_info.get('dependencies', [])
            
            # 시트 참조 추출 (예: "COMPUTE!", "RESTRICT!", "수능입력!")
            for dep in deps:
                if '!' in str(dep):
                    # "COMPUTEA1" -> "COMPUTE"
                    sheet_ref = str(dep).split('!')[0].replace('=', '').upper()
                    if sheet_ref and sheet_ref not in ['IF', 'IFERROR', 'INDEX', 'MATCH', 'VLOOKUP', 'HLOOKUP']:
                        sheet_deps.add(sheet_ref)
                elif any(keyword in str(dep).upper() for keyword in ['COMPUTE', 'RESTRICT', 'SUBJECT', '수능', 'INFO']):
                    # 키워드 기반 추출
                    for keyword in ['COMPUTE', 'RESTRICT', 'SUBJECT', '수능', 'INFO']:
                        if keyword in str(dep).upper():
                            sheet_deps.add(keyword)
        
        if sheet_deps:
            dependencies[sheet_name] = sorted(list(sheet_deps))
    
    return dependencies


def extract_formula_patterns(metadata: Dict[str, Any]) -> Dict[str, Any]:
    """수식 패턴 분석"""
    patterns = {
        'conditional': [],
        'index_match': [],
        'aggregation_sum': [],
        'aggregation_avg': [],
        'lookup': [],
        'other': []
    }
    
    for sheet_name, data in metadata.items():
        for col_name, formula_info in data.get('formula_samples', {}).items():
            pattern = data.get('formula_patterns', {}).get(col_name, 'other')
            formula = formula_info.get('formula', '')
            
            patterns[pattern].append({
                'sheet': sheet_name,
                'column': col_name,
                'formula': formula,
                'sample_row': formula_info.get('sample_row', 0)
            })
    
    return patterns


def analyze_core_formulas(metadata: Dict[str, Any]) -> Dict[str, Any]:
    """핵심 수식 분석"""
    core_analysis = {}
    
    # 이과계열분석결과와 문과계열분석결과의 핵심 수식 분석
    for sheet_name in ['이과계열분석결과', '문과계열분석결과']:
        if sheet_name not in metadata:
            continue
        
        sheet_data = metadata[sheet_name]
        formulas = sheet_data.get('formula_samples', {})
        
        core_analysis[sheet_name] = {
            'col_3': {
                'description': '적정점수/예상점수/소신점수 판정 로직',
                'formula': formulas.get('col_3', {}).get('formula', ''),
                'pattern': 'conditional',
                'dependencies': formulas.get('col_3', {}).get('dependencies', []),
                'key_references': {
                    '수능입력': '영어/국사 등급 검증',
                    'RESTRICT': '제한 조건 테이블 (3개 영역)',
                    'G6': '현재 점수',
                    'J6': '적정점수 기준',
                    'K6': '예상점수 기준',
                    'L6': '소신점수 기준'
                }
            },
            'col_4': {
                'description': 'COMPUTE 시트 기반 점수 변환 (첫 번째 지표)',
                'formula': formulas.get('col_4', {}).get('formula', ''),
                'pattern': 'index_match',
                'dependencies': formulas.get('col_4', {}).get('dependencies', []),
                'key_references': {
                    'COMPUTE': '점수 변환표 (72행 × 553컬럼)',
                    'E$5': '행 헤더 (대학명 또는 지표명)',
                    'AK6': '열 헤더 (대학 코드)'
                }
            },
            'col_5': {
                'description': 'COMPUTE 시트 기반 점수 변환 (두 번째 지표)',
                'formula': formulas.get('col_5', {}).get('formula', ''),
                'pattern': 'index_match',
                'dependencies': formulas.get('col_5', {}).get('dependencies', []),
                'key_references': {
                    'COMPUTE': '점수 변환표',
                    'F$5': '행 헤더',
                    'AK6': '열 헤더'
                }
            },
            'col_6': {
                'description': '점수 합계',
                'formula': formulas.get('col_6', {}).get('formula', ''),
                'pattern': 'aggregation_sum',
                'dependencies': formulas.get('col_6', {}).get('dependencies', [])
            },
            'col_7': {
                'description': '평균 점수 계산 (HLOOKUP 기반)',
                'formula': formulas.get('col_7', {}).get('formula', ''),
                'pattern': 'aggregation_avg',
                'dependencies': formulas.get('col_7', {}).get('dependencies', []),
                'key_references': {
                    'COMPUTE': 'HLOOKUP으로 4행, 5행 (또는 6행, 7행) 조회',
                    'MAX(0.00001, ...)': '최소값 보정'
                }
            },
            'col_8': {
                'description': '조건부 포맷팅 및 VLOOKUP',
                'formula': formulas.get('col_8', {}).get('formula', ''),
                'pattern': 'conditional',
                'dependencies': formulas.get('col_8', {}).get('dependencies', []),
                'key_references': {
                    'SUBJECT1': '과목별 가중치 조회',
                    'HLOOKUP': 'COMPUTE 시트 조회',
                    'ROUND': '반올림 처리'
                }
            }
        }
    
    return core_analysis


def generate_analysis_report(output_dir: str = './output') -> Dict[str, Any]:
    """전체 분석 리포트 생성"""
    output_path = Path(output_dir)
    
    # 수식 메타데이터 로드
    all_metadata = load_all_formula_metadata(str(output_path))
    
    # 의존성 분석
    dependencies = analyze_formula_dependencies(all_metadata)
    
    # 패턴 분석
    patterns = extract_formula_patterns(all_metadata)
    
    # 핵심 수식 분석
    core_formulas = analyze_core_formulas(all_metadata)
    
    report = {
        'metadata_summary': {
            'total_sheets_with_formulas': len([s for s in all_metadata.values() if s.get('columns_with_formulas')]),
            'total_formula_columns': sum(len(s.get('columns_with_formulas', [])) for s in all_metadata.values())
        },
        'sheet_dependencies': dependencies,
        'formula_patterns': {
            pattern: len(formulas) for pattern, formulas in patterns.items()
        },
        'core_formulas': core_formulas,
        'detailed_patterns': patterns
    }
    
    # 리포트 저장
    report_path = output_path / 'formula_analysis_report.json'
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2, default=str)
    
    print(f"[완료] 수식 분석 리포트 생성: {report_path}")
    
    return report


if __name__ == '__main__':
    print("=" * 60)
    print("수식 메타데이터 분석")
    print("=" * 60)
    print()
    
    report = generate_analysis_report()
    
    print()
    print("분석 결과 요약:")
    print(f"  수식이 있는 시트: {report['metadata_summary']['total_sheets_with_formulas']}개")
    print(f"  총 수식 컬럼: {report['metadata_summary']['total_formula_columns']}개")
    print()
    print("수식 패턴 분포:")
    for pattern, count in report['formula_patterns'].items():
        print(f"  {pattern}: {count}개")
    print()
    print("시트 간 의존성:")
    for sheet, deps in report['sheet_dependencies'].items():
        print(f"  {sheet}: {', '.join(deps)}")
