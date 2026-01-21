# 🤖 Theory Engine v3 심층 구현 에이전트 프롬프트

> **생성일**: 2026-01-17
> **목표**: 미완성 5개 기능 100% 완성
> **예상 소요**: 3-4시간
> **검증 기준**: 실제 엑셀 파일 기반 E2E 테스트 통과

---

## 📋 현재 상태 요약

### 완료된 것 ✅
- `theory_engine/config.py` - 시트 설정, 버전 관리
- `theory_engine/constants.py` - Enum, 상수 정의
- `theory_engine/utils.py` - 유틸리티 함수
- `theory_engine/loader.py` - 엑셀 로드
- `theory_engine/model.py` - 데이터 모델
- `theory_engine/rules.py` - 기본 룰 엔진 (미완성 부분 있음)
- `tests/test_theory_engine.py` - 기본 테스트
- `run_theory_engine.py` - 실행 스크립트

### 미완성 기능 (이번 작업 대상) ⚠️

| 기능 | 현재 | 목표 | 파일 |
|------|------|------|------|
| INDEX 조회 | 50% | 95% | `optimizers/index_optimizer.py` |
| 탐구과목 조회 | 70% | 95% | `matchers/subject_matcher.py` |
| RESTRICT 체크 | 50% | 90% | `rules/disqualification_engine.py` |
| 확률 계산 | 30% | 90% | `probability/admission_model.py` |
| 커트라인 계산 | 0% | 85% | `cutoff/cutoff_extractor.py` |

---

## 🎯 에이전트 지침

### 작업 원칙
1. **파일 읽기 필수**: 수정 전 반드시 기존 코드 확인
2. **점진적 구현**: 한 기능씩 완성 후 테스트
3. **인코딩 주의**: 모든 파일 UTF-8로 저장
4. **로깅 활용**: 디버그 정보 충분히 출력
5. **테스트 우선**: 구현 후 즉시 검증

### 금지 사항
- 추측 기반 코드 작성 금지
- 한 번에 여러 파일 동시 수정 금지
- 테스트 없이 다음 단계 진행 금지

---

## 📁 최종 파일 구조

```
theory_engine/
├── __init__.py           # 패키지 초기화
├── config.py             # 설정 (기존)
├── constants.py          # 상수 (기존)
├── utils.py              # 유틸리티 (기존)
├── loader.py             # 로더 (수정)
├── model.py              # 모델 (기존)
├── rules.py              # 룰 엔진 (수정)
│
├── optimizers/           # [NEW] 최적화 모듈
│   ├── __init__.py
│   └── index_optimizer.py
│
├── matchers/             # [NEW] 매칭 모듈
│   ├── __init__.py
│   └── subject_matcher.py
│
├── disqualification/     # [NEW] 결격 체크
│   ├── __init__.py
│   └── disqualification_engine.py
│
├── probability/          # [NEW] 확률 계산
│   ├── __init__.py
│   └── admission_model.py
│
└── cutoff/               # [NEW] 커트라인
    ├── __init__.py
    └── cutoff_extractor.py
```

---

## 🔧 Phase 1: 탐구과목 매칭 (30분)

### 1.1 목표
- "물리학I" → "물리학 Ⅰ" 자동 변환
- 95% 이상 매칭 정확도

### 1.2 구현 파일

**파일**: `theory_engine/matchers/__init__.py`
```python
from .subject_matcher import SubjectMatcher

__all__ = ["SubjectMatcher"]
```

**파일**: `theory_engine/matchers/subject_matcher.py`
```python
"""
탐구과목 이름 퍼지 매칭

사용법:
    matcher = SubjectMatcher()
    canonical, score = matcher.match("물리학I")  # → ("물리학 Ⅰ", 95.0)
"""

import re
from typing import Dict, List, Optional, Tuple
import logging

logger = logging.getLogger(__name__)

class SubjectMatcher:
    """탐구과목 이름 퍼지 매칭"""
    
    # 표준 과목명 → 별칭 목록
    CANONICAL_SUBJECTS: Dict[str, List[str]] = {
        # === 국어 ===
        "국어(언매)": ["국어언매", "언어와매체", "언매", "국어 언매"],
        "국어(화작)": ["국어화작", "화법과작문", "화작", "국어 화작"],
        
        # === 수학 ===
        "수학(미적)": ["수학미적", "미적분", "미적", "수학 미적"],
        "수학(기하)": ["수학기하", "기하", "수학 기하"],
        "수학(확통)": ["수학확통", "확률과통계", "확통", "수학 확통"],
        
        # === 과학탐구 ===
        "물리학 Ⅰ": ["물리학1", "물리학I", "물리1", "물리Ⅰ", "물리 1", "물리학 1"],
        "물리학 Ⅱ": ["물리학2", "물리학II", "물리2", "물리Ⅱ", "물리 2", "물리학 2"],
        "화학 Ⅰ": ["화학1", "화학I", "화1", "화학Ⅰ", "화학 1"],
        "화학 Ⅱ": ["화학2", "화학II", "화2", "화학Ⅱ", "화학 2"],
        "생명과학 Ⅰ": ["생명과학1", "생명1", "생물1", "생명Ⅰ", "생명과학 1", "생과1"],
        "생명과학 Ⅱ": ["생명과학2", "생명2", "생물2", "생명Ⅱ", "생명과학 2", "생과2"],
        "지구과학 Ⅰ": ["지구과학1", "지구1", "지학1", "지구Ⅰ", "지구과학 1"],
        "지구과학 Ⅱ": ["지구과학2", "지구2", "지학2", "지구Ⅱ", "지구과학 2"],
        
        # === 사회탐구 ===
        "생활과 윤리": ["생윤", "생활윤리", "생활과윤리"],
        "윤리와 사상": ["윤사", "윤리사상", "윤리와사상"],
        "한국지리": ["한지"],
        "세계지리": ["세지"],
        "동아시아사": ["동아사", "동아시아"],
        "세계사": ["세사"],
        "경제": [],
        "정치와 법": ["정법", "정치와법"],
        "사회·문화": ["사문", "사회문화", "사회와문화"],
        
        # === 제2외국어 ===
        "한문 Ⅰ": ["한문1", "한문I"],
        "일본어 Ⅰ": ["일본어1", "일어1"],
        "중국어 Ⅰ": ["중국어1", "중어1"],
    }
    
    def __init__(self, threshold: int = 70):
        """
        Args:
            threshold: 매칭 임계값 (0-100)
        """
        self.threshold = threshold
        self._build_reverse_mapping()
        logger.info(f"SubjectMatcher 초기화: {len(self.alias_to_canonical)}개 매핑")
    
    def _build_reverse_mapping(self):
        """별칭 → 정규 이름 역매핑 구축"""
        self.alias_to_canonical: Dict[str, str] = {}
        
        for canonical, aliases in self.CANONICAL_SUBJECTS.items():
            # 정규 이름 자체도 매핑
            normalized = self._normalize(canonical)
            self.alias_to_canonical[normalized] = canonical
            
            # 모든 별칭 매핑
            for alias in aliases:
                normalized_alias = self._normalize(alias)
                self.alias_to_canonical[normalized_alias] = canonical
    
    def _normalize(self, name: str) -> str:
        """문자열 정규화"""
        if not name:
            return ""
        
        # 1. 공백 제거
        name = name.replace(" ", "")
        # 2. 로마자 통일 (Ⅰ→1, Ⅱ→2)
        name = name.replace("Ⅰ", "1").replace("Ⅱ", "2")
        name = name.replace("I", "1").replace("II", "2")
        # 3. 소문자 변환
        name = name.lower()
        # 4. 특수문자 제거 (·, (, ) 등)
        name = re.sub(r'[^\w가-힣0-9]', '', name)
        
        return name
    
    def match(self, input_name: str) -> Tuple[str, float]:
        """
        입력 과목명 → 정규 과목명 매칭
        
        Args:
            input_name: 입력 과목명
        
        Returns:
            (canonical_name, confidence_score)
            - canonical_name: 정규화된 과목명
            - confidence_score: 신뢰도 (0-100)
        """
        if not input_name:
            return input_name, 0.0
        
        normalized = self._normalize(input_name)
        
        # 1. 정확한 매칭
        if normalized in self.alias_to_canonical:
            canonical = self.alias_to_canonical[normalized]
            logger.debug(f"정확 매칭: '{input_name}' → '{canonical}'")
            return canonical, 100.0
        
        # 2. 부분 매칭 (포함 관계)
        for alias, canonical in self.alias_to_canonical.items():
            if normalized in alias or alias in normalized:
                score = len(normalized) / max(len(alias), len(normalized)) * 100
                if score >= self.threshold:
                    logger.debug(f"부분 매칭: '{input_name}' → '{canonical}' (score={score:.1f})")
                    return canonical, score
        
        # 3. 레벤슈타인 거리 기반 매칭 (간단 구현)
        best_match = None
        best_score = 0
        
        for alias, canonical in self.alias_to_canonical.items():
            score = self._similarity_score(normalized, alias)
            if score > best_score:
                best_score = score
                best_match = canonical
        
        if best_match and best_score >= self.threshold:
            logger.debug(f"유사 매칭: '{input_name}' → '{best_match}' (score={best_score:.1f})")
            return best_match, best_score
        
        # 4. 매칭 실패 - 원본 반환
        logger.warning(f"매칭 실패: '{input_name}'")
        return input_name, 0.0
    
    def _similarity_score(self, s1: str, s2: str) -> float:
        """두 문자열 유사도 (0-100)"""
        if not s1 or not s2:
            return 0.0
        
        # 공통 문자 비율
        common = set(s1) & set(s2)
        total = set(s1) | set(s2)
        
        if not total:
            return 0.0
        
        return len(common) / len(total) * 100
    
    def get_all_canonical_names(self) -> List[str]:
        """모든 정규 과목명 반환"""
        return list(self.CANONICAL_SUBJECTS.keys())
    
    def get_aliases(self, canonical_name: str) -> List[str]:
        """정규 과목명의 모든 별칭 반환"""
        return self.CANONICAL_SUBJECTS.get(canonical_name, [])


# 테스트 코드
if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    
    matcher = SubjectMatcher()
    
    test_cases = [
        "물리학I",
        "물리학 Ⅰ",
        "화학1",
        "생윤",
        "수학(미적)",
        "국어(언매)",
        "생명과학 Ⅰ",
        "지구과학2",
    ]
    
    print("\n=== 과목 매칭 테스트 ===")
    for name in test_cases:
        canonical, score = matcher.match(name)
        status = "✓" if score >= 70 else "✗"
        print(f"{status} '{name}' → '{canonical}' (score={score:.1f})")
```

### 1.3 테스트 명령어
```bash
cd C:\Neoprime
python -m theory_engine.matchers.subject_matcher
```

### 1.4 완료 기준
- [ ] 모든 테스트 케이스 통과
- [ ] 매칭 성공률 95% 이상
- [ ] 로깅 출력 정상

---

## 🔧 Phase 2: INDEX 최적화 (45분)

### 2.1 목표
- 20만 행 조회 1ms 이하
- 정확한 키 매칭 + 근사 검색

### 2.2 구현 파일

**파일**: `theory_engine/optimizers/__init__.py`
```python
from .index_optimizer import IndexOptimizer

__all__ = ["IndexOptimizer"]
```

**파일**: `theory_engine/optimizers/index_optimizer.py`
```python
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
        self.raw_df = index_df
        self._cache: Dict[Tuple, Dict] = {}
        self._build_optimized_index()
    
    def _build_optimized_index(self):
        """MultiIndex 구축"""
        logger.info(f"INDEX 최적화 시작: {len(self.raw_df)}행")
        
        # 1. 컬럼명 매핑
        self.df = self.raw_df.copy()
        
        # 실제 컬럼명 확인
        logger.debug(f"원본 컬럼: {list(self.df.columns)}")
        
        # 매핑 적용
        rename_map = {}
        for old_name, new_name in self.COLUMN_MAPPING.items():
            if old_name in self.df.columns:
                rename_map[old_name] = new_name
        
        if rename_map:
            self.df = self.df.rename(columns=rename_map)
            logger.info(f"컬럼 매핑: {len(rename_map)}개")
        
        # 2. 필요한 컬럼 확인
        available_keys = [c for c in self.KEY_COLUMNS if c in self.df.columns]
        logger.info(f"사용 가능한 키: {available_keys}")
        
        if len(available_keys) < 2:
            logger.warning("키 컬럼 부족, 기본 인덱스 사용")
            self.use_multiindex = False
            return
        
        # 3. MultiIndex 설정
        try:
            # NaN 제거
            self.df = self.df.dropna(subset=available_keys)
            
            # 타입 변환 (숫자로)
            for col in available_keys[:-1]:  # track 제외
                if col in self.df.columns:
                    self.df[col] = pd.to_numeric(self.df[col], errors='coerce')
            
            # MultiIndex 설정
            self.df = self.df.set_index(available_keys)
            self.df = self.df.sort_index()
            self.use_multiindex = True
            
            logger.info(f"MultiIndex 구축 완료: {len(self.df)}행")
            
        except Exception as e:
            logger.error(f"MultiIndex 구축 실패: {e}")
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
        
        if not self.use_multiindex:
            # 기본 검색 (느림)
            result = self._basic_lookup(key, index_key)
        else:
            # MultiIndex 검색 (빠름)
            try:
                if key in self.df.index:
                    row = self.df.loc[key]
                    result = self._extract_result(row, index_key, exact=True)
                elif fuzzy:
                    result = self._fuzzy_lookup(key, index_key)
            except KeyError:
                if fuzzy:
                    result = self._fuzzy_lookup(key, index_key)
        
        self._cache[key] = result
        return result
    
    def _basic_lookup(self, key: Tuple, index_key: str) -> Dict[str, Any]:
        """기본 선형 검색"""
        korean, math, inq1, inq2, track = key
        
        mask = (
            (self.raw_df.iloc[:, 1] == korean) &
            (self.raw_df.iloc[:, 2] == math) &
            (self.raw_df.iloc[:, 3] == inq1) &
            (self.raw_df.iloc[:, 4] == inq2)
        )
        
        result_df = self.raw_df[mask]
        
        if result_df.empty:
            return {
                'found': False,
                'exact_match': False,
                'index_key': index_key,
                'percentile_sum': None,
                'national_rank': None,
                'cumulative_pct': None,
            }
        
        row = result_df.iloc[0]
        return self._extract_result(row, index_key, exact=True)
    
    def _extract_result(self, row, index_key: str, exact: bool) -> Dict[str, Any]:
        """결과 추출"""
        return {
            'found': True,
            'exact_match': exact,
            'index_key': index_key,
            'percentile_sum': row.get('percentile_sum', row.iloc[0] if len(row) > 0 else None),
            'national_rank': row.get('national_rank', row.iloc[1] if len(row) > 1 else None),
            'cumulative_pct': row.get('cumulative_pct', row.iloc[2] if len(row) > 2 else None),
        }
    
    def _fuzzy_lookup(self, key: Tuple, index_key: str) -> Dict[str, Any]:
        """근사 검색 (가장 가까운 키 찾기)"""
        korean, math, inq1, inq2, track = key
        
        # 계열 필터링
        if self.use_multiindex:
            try:
                track_df = self.df.xs(track, level='track', drop_level=False)
            except KeyError:
                track_df = self.df
        else:
            track_df = self.raw_df
        
        if track_df.empty:
            return {
                'found': False,
                'exact_match': False,
                'approximate': True,
                'index_key': index_key,
                'percentile_sum': None,
                'national_rank': None,
                'cumulative_pct': None,
            }
        
        # 거리 계산 (간단한 L1 거리)
        if self.use_multiindex:
            # MultiIndex에서 레벨 값 추출
            levels = track_df.index.to_frame()
            scores = levels[['korean_std', 'math_std', 'inq1_std', 'inq2_std']].values
        else:
            scores = track_df.iloc[:, 1:5].values
        
        target = np.array([korean, math, inq1, inq2])
        distances = np.abs(scores - target).sum(axis=1)
        
        nearest_idx = distances.argmin()
        row = track_df.iloc[nearest_idx]
        
        result = self._extract_result(row, index_key, exact=False)
        result['approximate'] = True
        result['distance'] = int(distances[nearest_idx])
        
        logger.debug(f"근사 매칭: distance={result['distance']}")
        return result
    
    def get_stats(self) -> Dict[str, Any]:
        """통계 정보"""
        return {
            'total_rows': len(self.raw_df),
            'indexed_rows': len(self.df) if self.use_multiindex else 0,
            'cache_size': len(self._cache),
            'use_multiindex': self.use_multiindex,
        }


# 테스트 코드
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # 테스트용 더미 데이터 생성
    print("=== INDEX 최적화 테스트 ===")
    
    # 실제 데이터로 테스트
    from theory_engine.loader import load_workbook
    from theory_engine.config import EXCEL_PATH
    
    print(f"엑셀 로드: {EXCEL_PATH}")
    data = load_workbook(EXCEL_PATH)
    
    if "INDEX" in data:
        optimizer = IndexOptimizer(data["INDEX"])
        print(f"통계: {optimizer.get_stats()}")
        
        # 테스트 조회
        result = optimizer.lookup(130, 135, 65, 62, "이과")
        print(f"조회 결과: {result}")
    else:
        print("INDEX 시트 없음")
```

### 2.3 테스트 명령어
```bash
cd C:\Neoprime
python -m theory_engine.optimizers.index_optimizer
```

### 2.4 완료 기준
- [ ] MultiIndex 구축 성공
- [ ] 조회 시간 10ms 이하
- [ ] 근사 검색 작동

---

## 🔧 Phase 3: 커트라인 추출 (45분)

### 3.1 목표
- PERCENTAGE 시트에서 80/50/20% 라인 자동 추출
- 대학/전공별 커트라인 계산

### 3.2 구현 파일

**파일**: `theory_engine/cutoff/__init__.py`
```python
from .cutoff_extractor import CutoffExtractor

__all__ = ["CutoffExtractor"]
```

**파일**: `theory_engine/cutoff/cutoff_extractor.py`
```python
"""
커트라인 자동 추출기

PERCENTAGE 시트에서 대학/전공별 커트라인(80%/50%/20%) 추출
"""

import pandas as pd
import numpy as np
import logging
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

class CutoffExtractor:
    """커트라인 자동 추출기"""
    
    # 기준 확률 라인
    CUTOFF_PERCENTILES = {
        "적정": 80.0,   # 상위 20% → 누백 80%
        "예상": 50.0,   # 상위 50% → 누백 50%
        "소신": 20.0,   # 상위 80% → 누백 20%
    }
    
    def __init__(self, percentage_df: pd.DataFrame):
        """
        Args:
            percentage_df: PERCENTAGE 시트 DataFrame
        """
        self.df = percentage_df
        self._cache: Dict[str, Dict] = {}
        self._analyze_structure()
    
    def _analyze_structure(self):
        """시트 구조 분석"""
        logger.info(f"PERCENTAGE 시트 분석: {self.df.shape}")
        
        # 첫 컬럼 (누백/%) 확인
        self.percentile_col = self.df.columns[0]
        logger.info(f"누백 컬럼: '{self.percentile_col}'")
        
        # 대학/전공 컬럼 목록
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
            university: 대학명 (예: "서울대", "연세대")
            major: 전공명 (예: "의예", "공대")
            track: 계열 (선택, "이과" | "문과")
        
        Returns:
            {
                'found': True,
                'column': '서울대의예 이과',
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
            }
            self._cache[cache_key] = result
            return result
        
        # 커트라인 계산
        result = self._calculate_cutoffs(program_col)
        result['found'] = True
        result['column'] = program_col
        
        self._cache[cache_key] = result
        return result
    
    def _find_program_column(
        self,
        university: str,
        major: str,
        track: str = ""
    ) -> Optional[str]:
        """대학/전공에 해당하는 컬럼 찾기"""
        
        # 패턴 생성
        patterns = [
            f"{university}{major}",           # "서울대의예"
            f"{university} {major}",          # "서울대 의예"
            f"{university}{major} {track}" if track else None,  # "서울대의예 이과"
        ]
        patterns = [p for p in patterns if p]
        
        # 정확한 매칭
        for col in self.df.columns:
            col_str = str(col)
            for pattern in patterns:
                if pattern in col_str:
                    logger.debug(f"컬럼 매칭: '{pattern}' → '{col_str}'")
                    return col
        
        # 부분 매칭
        for col in self.df.columns:
            col_str = str(col)
            if university in col_str and major in col_str:
                logger.debug(f"부분 매칭: '{university}+{major}' → '{col_str}'")
                return col
        
        # 대학만 매칭
        for col in self.df.columns:
            col_str = str(col)
            if university in col_str:
                logger.debug(f"대학 매칭: '{university}' → '{col_str}'")
                return col
        
        logger.warning(f"컬럼 없음: {university}{major}")
        return None
    
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
        percentile: float
    ) -> Optional[float]:
        """특정 누백에서의 환산점수 조회"""
        
        program_col = self._find_program_column(university, major)
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
            score = np.interp(
                percentile,
                df_subset['pct'].values,
                df_subset['score'].values
            )
            return round(float(score), 2)
        except:
            return None
    
    def list_available_programs(self) -> List[str]:
        """사용 가능한 대학/전공 목록"""
        return self.program_columns
    
    def get_stats(self) -> Dict:
        """통계 정보"""
        return {
            'total_programs': len(self.program_columns),
            'percentile_range': (
                self.df[self.percentile_col].min(),
                self.df[self.percentile_col].max()
            ),
            'cache_size': len(self._cache),
        }


# 테스트 코드
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    from theory_engine.loader import load_workbook
    from theory_engine.config import EXCEL_PATH
    
    print("=== 커트라인 추출 테스트 ===")
    print(f"엑셀 로드: {EXCEL_PATH}")
    
    data = load_workbook(EXCEL_PATH)
    
    if "PERCENTAGE" in data:
        extractor = CutoffExtractor(data["PERCENTAGE"])
        print(f"통계: {extractor.get_stats()}")
        
        # 사용 가능한 프로그램 목록
        programs = extractor.list_available_programs()
        print(f"\n사용 가능한 대학/전공: {len(programs)}개")
        if programs:
            print(f"샘플: {programs[:10]}")
        
        # 커트라인 추출 테스트
        test_cases = [
            ("가천", "의학"),
            ("건국", "자연"),
            ("서울대", "공대"),
        ]
        
        print("\n=== 커트라인 추출 ===")
        for univ, major in test_cases:
            result = extractor.extract_cutoffs(univ, major)
            if result['found']:
                print(f"✓ {univ}{major}: 적정={result['cutoff_safe']}, "
                      f"예상={result['cutoff_normal']}, 소신={result['cutoff_risk']}")
            else:
                print(f"✗ {univ}{major}: 데이터 없음")
    else:
        print("PERCENTAGE 시트 없음")
```

### 3.3 테스트 명령어
```bash
cd C:\Neoprime
python -m theory_engine.cutoff.cutoff_extractor
```

---

## 🔧 Phase 4: 확률 계산 모델 (45분)

### 4.1 구현 파일

**파일**: `theory_engine/probability/__init__.py`
```python
from .admission_model import AdmissionProbabilityModel

__all__ = ["AdmissionProbabilityModel"]
```

**파일**: `theory_engine/probability/admission_model.py`
```python
"""
합격 확률 계산 모델

학생 점수와 커트라인 기반 합격 확률 계산
"""

import logging
from typing import Dict, Optional, Tuple
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class ProbabilityResult:
    """확률 계산 결과"""
    probability: float
    level: str
    confidence_low: float
    confidence_high: float


class AdmissionProbabilityModel:
    """합격 확률 계산 모델"""
    
    # 라인별 기본 확률 범위
    LEVEL_RANGES = {
        "적정": (0.80, 1.00),
        "예상": (0.50, 0.80),
        "소신": (0.20, 0.50),
        "상향": (0.00, 0.20),
    }
    
    def __init__(self, uncertainty: float = 0.10):
        """
        Args:
            uncertainty: 기본 불확실성 (표준편차)
        """
        self.uncertainty = uncertainty
    
    def calculate(
        self,
        student_score: float,
        cutoff_safe: Optional[float],
        cutoff_normal: Optional[float],
        cutoff_risk: Optional[float]
    ) -> ProbabilityResult:
        """
        합격 확률 계산
        
        Args:
            student_score: 학생의 환산점수
            cutoff_safe: 적정 커트라인 (80%)
            cutoff_normal: 예상 커트라인 (50%)
            cutoff_risk: 소신 커트라인 (20%)
        
        Returns:
            ProbabilityResult
        """
        # 커트라인 없으면 기본값
        if cutoff_normal is None:
            return ProbabilityResult(
                probability=0.50,
                level="알수없음",
                confidence_low=0.30,
                confidence_high=0.70
            )
        
        # 점수 위치 판정
        if cutoff_safe and student_score >= cutoff_safe:
            # 적정 이상
            prob = self._calc_prob_above(student_score, cutoff_safe, 0.80, 1.00)
            level = "적정"
            
        elif student_score >= cutoff_normal:
            # 예상 범위
            if cutoff_safe:
                ratio = (student_score - cutoff_normal) / (cutoff_safe - cutoff_normal)
            else:
                ratio = 0.5
            prob = 0.50 + ratio * 0.30
            level = "예상"
            
        elif cutoff_risk and student_score >= cutoff_risk:
            # 소신 범위
            ratio = (student_score - cutoff_risk) / (cutoff_normal - cutoff_risk)
            prob = 0.20 + ratio * 0.30
            level = "소신"
            
        else:
            # 상향 범위
            if cutoff_risk:
                ratio = max(0, student_score / cutoff_risk)
                prob = ratio * 0.20
            else:
                prob = 0.10
            level = "상향"
        
        # 확률 범위 제한
        prob = max(0.01, min(0.99, prob))
        
        # 신뢰구간
        ci_low = max(0.00, prob - 1.96 * self.uncertainty)
        ci_high = min(1.00, prob + 1.96 * self.uncertainty)
        
        return ProbabilityResult(
            probability=round(prob, 4),
            level=level,
            confidence_low=round(ci_low, 4),
            confidence_high=round(ci_high, 4)
        )
    
    def _calc_prob_above(
        self,
        score: float,
        cutoff: float,
        base_prob: float,
        max_prob: float
    ) -> float:
        """커트라인 이상일 때 확률 계산"""
        excess = score - cutoff
        range_above = cutoff * 0.05  # 5% 여유
        
        if range_above <= 0:
            return base_prob
        
        normalized = min(1.0, excess / range_above)
        return base_prob + normalized * (max_prob - base_prob)
    
    def determine_level(
        self,
        student_score: float,
        cutoff_safe: Optional[float],
        cutoff_normal: Optional[float],
        cutoff_risk: Optional[float]
    ) -> str:
        """합격 라인만 판정"""
        result = self.calculate(student_score, cutoff_safe, cutoff_normal, cutoff_risk)
        return result.level


# 테스트 코드
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    model = AdmissionProbabilityModel()
    
    print("=== 확률 계산 테스트 ===\n")
    
    # 테스트 케이스
    test_cases = [
        # (student_score, cutoff_safe, cutoff_normal, cutoff_risk, expected_level)
        (98.0, 95.0, 90.0, 85.0, "적정"),
        (92.0, 95.0, 90.0, 85.0, "예상"),
        (87.0, 95.0, 90.0, 85.0, "소신"),
        (80.0, 95.0, 90.0, 85.0, "상향"),
        (70.0, None, None, None, "알수없음"),
    ]
    
    for score, safe, normal, risk, expected in test_cases:
        result = model.calculate(score, safe, normal, risk)
        status = "✓" if result.level == expected else "✗"
        print(f"{status} score={score}, level={result.level} (expected={expected})")
        print(f"   prob={result.probability:.2%}, CI=[{result.confidence_low:.2%}, {result.confidence_high:.2%}]")
```

### 4.2 테스트 명령어
```bash
cd C:\Neoprime
python -m theory_engine.probability.admission_model
```

---

## 🔧 Phase 5: 결격 체크 엔진 (45분)

### 5.1 구현 파일

**파일**: `theory_engine/disqualification/__init__.py`
```python
from .disqualification_engine import DisqualificationEngine

__all__ = ["DisqualificationEngine"]
```

**파일**: `theory_engine/disqualification/disqualification_engine.py`
```python
"""
결격 사유 체크 엔진

RESTRICT 시트 기반 결격 룰 적용
"""

import re
import logging
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass, field

from ..constants import DisqualificationCode
from ..model import StudentProfile, TargetProgram, DisqualificationInfo

logger = logging.getLogger(__name__)

@dataclass
class DisqualificationRule:
    """결격 사유 룰"""
    rule_id: str
    description: str
    university_pattern: str  # 대학명 패턴 (regex)
    check_func: Callable[[Any, Any], bool]  # (profile, target) → bool
    code: DisqualificationCode
    message_template: str
    severity: int = 1  # 1=경고, 2=심각


class DisqualificationEngine:
    """결격 사유 체크 엔진"""
    
    # 과학탐구 과목 목록
    SCIENCE_SUBJECTS = ["물리학", "화학", "생명과학", "지구과학"]
    
    # 사회탐구 과목 목록
    SOCIAL_SUBJECTS = ["생활과 윤리", "윤리와 사상", "한국지리", "세계지리", 
                       "동아시아사", "세계사", "경제", "정치와 법", "사회·문화"]
    
    def __init__(self):
        """엔진 초기화 및 룰 로드"""
        self.rules: List[DisqualificationRule] = []
        self._load_rules()
        logger.info(f"결격 체크 엔진 초기화: {len(self.rules)}개 룰")
    
    def _load_rules(self):
        """결격 룰 로드"""
        
        # ===== 영어 등급 제한 =====
        self.rules.append(DisqualificationRule(
            rule_id="ENG_GRADE_001",
            description="영어 3등급 초과 제한 (일반)",
            university_pattern=r".*",
            check_func=lambda p, t: p.english_grade > 3,
            code=DisqualificationCode.ENGLISH_GRADE,
            message_template="영어 {grade}등급: 대부분 대학은 3등급 이내 필수",
            severity=2
        ))
        
        self.rules.append(DisqualificationRule(
            rule_id="ENG_GRADE_002",
            description="영어 2등급 초과 제한 (상위권)",
            university_pattern=r"서울대|연세대|고려대|성균관|한양대|중앙대|경희대|이화여대",
            check_func=lambda p, t: p.english_grade > 2,
            code=DisqualificationCode.ENGLISH_GRADE,
            message_template="영어 {grade}등급: {university}는 2등급 이내 권장",
            severity=1
        ))
        
        # ===== 한국사 등급 제한 =====
        self.rules.append(DisqualificationRule(
            rule_id="HIST_GRADE_001",
            description="한국사 4등급 초과 제한",
            university_pattern=r".*",
            check_func=lambda p, t: p.history_grade > 4,
            code=DisqualificationCode.HISTORY_GRADE,
            message_template="한국사 {grade}등급: 대부분 대학은 4등급 이내 필수",
            severity=2
        ))
        
        # ===== 수학 선택과목 제한 =====
        self.rules.append(DisqualificationRule(
            rule_id="MATH_SUBJ_001",
            description="이과 미적분/기하 필수",
            university_pattern=r"서울대|연세대|고려대|성균관|한양대|KAIST|포항공대",
            check_func=lambda p, t: (
                p.track.value == "이과" and 
                p.math.subject not in ["수학(미적)", "수학(기하)", "미적분", "기하"]
            ),
            code=DisqualificationCode.MATH_SUBJECT,
            message_template="{university} 이과: 미적분/기하 필수",
            severity=2
        ))
        
        # ===== 탐구과목 제한 (의대) =====
        self.rules.append(DisqualificationRule(
            rule_id="INQ_SUBJ_001",
            description="의대 과탐 2과목 필수",
            university_pattern=r"의대|의학|의예|치의|한의|약학",
            check_func=lambda p, t: (
                "의" in t.major or "약" in t.major
            ) and (
                not self._is_science(p.inquiry1.subject) or
                not self._is_science(p.inquiry2.subject)
            ),
            code=DisqualificationCode.INQUIRY_SUBJECT,
            message_template="{university} {major}: 과학탐구 2과목 필수",
            severity=2
        ))
        
        # ===== 탐구 조합 제한 (서울대) =====
        self.rules.append(DisqualificationRule(
            rule_id="INQ_COMBO_001",
            description="서울대 동일과목군 I+I 불가",
            university_pattern=r"서울대",
            check_func=lambda p, t: (
                self._get_subject_category(p.inquiry1.subject) ==
                self._get_subject_category(p.inquiry2.subject) and
                "Ⅰ" in p.inquiry1.subject and "Ⅰ" in p.inquiry2.subject
            ),
            code=DisqualificationCode.INQUIRY_COMBINATION,
            message_template="서울대: 동일 과목군 Ⅰ+Ⅰ 조합 불가",
            severity=2
        ))
    
    def _is_science(self, subject: str) -> bool:
        """과학탐구 과목 여부"""
        return any(s in subject for s in self.SCIENCE_SUBJECTS)
    
    def _get_subject_category(self, subject: str) -> str:
        """탐구 과목 카테고리"""
        for cat in self.SCIENCE_SUBJECTS + self.SOCIAL_SUBJECTS:
            if cat in subject:
                return cat.split()[0]  # "물리학", "화학" 등
        return "기타"
    
    def check(
        self,
        profile: StudentProfile,
        target: TargetProgram,
        severity_threshold: int = 1
    ) -> DisqualificationInfo:
        """
        결격 사유 체크
        
        Args:
            profile: 학생 프로필
            target: 지원 대학/전형
            severity_threshold: 이 심각도 이상만 결격 처리 (1=경고 포함, 2=심각만)
        
        Returns:
            DisqualificationInfo
        """
        triggered_rules: List[DisqualificationRule] = []
        
        for rule in self.rules:
            # 대학 패턴 매칭
            if not re.search(rule.university_pattern, target.university, re.IGNORECASE):
                if not re.search(rule.university_pattern, target.major, re.IGNORECASE):
                    continue
            
            # 조건 체크
            try:
                if rule.check_func(profile, target):
                    if rule.severity >= severity_threshold:
                        triggered_rules.append(rule)
                        logger.debug(f"룰 트리거: {rule.rule_id} - {rule.description}")
            except Exception as e:
                logger.warning(f"룰 {rule.rule_id} 평가 실패: {e}")
        
        if triggered_rules:
            # 가장 심각한 룰 선택
            triggered_rules.sort(key=lambda r: r.severity, reverse=True)
            primary = triggered_rules[0]
            
            message = primary.message_template.format(
                university=target.university,
                major=target.major,
                grade=profile.english_grade,
            )
            
            return DisqualificationInfo(
                is_disqualified=True,
                reason=message,
                code=primary.code,
                rules_triggered=[r.rule_id for r in triggered_rules]
            )
        
        return DisqualificationInfo(is_disqualified=False)
    
    def get_all_rules(self) -> List[Dict]:
        """모든 룰 목록"""
        return [
            {
                "rule_id": r.rule_id,
                "description": r.description,
                "severity": r.severity,
                "code": r.code.value,
            }
            for r in self.rules
        ]


# 테스트 코드
if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    
    from ..model import ExamScore, StudentProfile, TargetProgram
    from ..constants import Track
    
    print("=== 결격 체크 테스트 ===\n")
    
    engine = DisqualificationEngine()
    print(f"로드된 룰: {len(engine.rules)}개\n")
    
    # 테스트 프로필
    profile = StudentProfile(
        track=Track.SCIENCE,
        korean=ExamScore("국어(언매)", raw_total=80),
        math=ExamScore("수학(미적)", raw_total=75),
        english_grade=2,
        history_grade=3,
        inquiry1=ExamScore("물리학 Ⅰ", raw_total=50),
        inquiry2=ExamScore("화학 Ⅰ", raw_total=48),
    )
    
    # 테스트 케이스
    targets = [
        TargetProgram("서울대", "공대"),
        TargetProgram("연세대", "의예"),
        TargetProgram("고려대", "경영"),
    ]
    
    for target in targets:
        result = engine.check(profile, target)
        status = "✗ 결격" if result.is_disqualified else "✓ 통과"
        print(f"{status}: {target.university} {target.major}")
        if result.is_disqualified:
            print(f"   사유: {result.reason}")
            print(f"   룰: {result.rules_triggered}")
        print()
```

### 5.2 테스트 명령어
```bash
cd C:\Neoprime
python -m theory_engine.disqualification.disqualification_engine
```

---

## 🔧 Phase 6: 통합 및 rules.py 업데이트 (30분)

### 6.1 목표
- 새 모듈들을 rules.py에 통합
- compute_theory_result() 완전 구현

### 6.2 rules.py 수정 내용

기존 `rules.py`의 `compute_theory_result()` 함수를 다음과 같이 수정:

```python
# rules.py 상단에 import 추가
from .matchers.subject_matcher import SubjectMatcher
from .optimizers.index_optimizer import IndexOptimizer
from .cutoff.cutoff_extractor import CutoffExtractor
from .probability.admission_model import AdmissionProbabilityModel
from .disqualification.disqualification_engine import DisqualificationEngine

# 전역 인스턴스 (lazy initialization)
_subject_matcher = None
_probability_model = None
_disqualification_engine = None

def get_subject_matcher():
    global _subject_matcher
    if _subject_matcher is None:
        _subject_matcher = SubjectMatcher()
    return _subject_matcher

def get_probability_model():
    global _probability_model
    if _probability_model is None:
        _probability_model = AdmissionProbabilityModel()
    return _probability_model

def get_disqualification_engine():
    global _disqualification_engine
    if _disqualification_engine is None:
        _disqualification_engine = DisqualificationEngine()
    return _disqualification_engine
```

### 6.3 테스트 명령어
```bash
cd C:\Neoprime
python run_theory_engine.py
```

---

## 🧪 Phase 7: E2E 테스트 및 검증 (30분)

### 7.1 통합 테스트 스크립트

**파일**: `tests/test_integration.py`
```python
"""
Theory Engine v3 통합 테스트

실제 엑셀 파일 기반 E2E 테스트
"""

import logging
import sys
import time
from pathlib import Path

# 프로젝트 루트 추가
sys.path.insert(0, str(Path(__file__).parent.parent))

from theory_engine.config import EXCEL_PATH, ENGINE_VERSION
from theory_engine.loader import load_workbook
from theory_engine.model import StudentProfile, ExamScore, TargetProgram
from theory_engine.constants import Track
from theory_engine.rules import compute_theory_result
from theory_engine.matchers import SubjectMatcher
from theory_engine.optimizers import IndexOptimizer
from theory_engine.cutoff import CutoffExtractor
from theory_engine.probability import AdmissionProbabilityModel
from theory_engine.disqualification import DisqualificationEngine

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def test_subject_matcher():
    """과목 매칭 테스트"""
    print("\n" + "="*60)
    print("1. 과목 매칭 테스트")
    print("="*60)
    
    matcher = SubjectMatcher()
    
    test_cases = [
        ("물리학I", "물리학 Ⅰ"),
        ("화학1", "화학 Ⅰ"),
        ("생윤", "생활과 윤리"),
        ("수학(미적)", "수학(미적)"),
        ("국어(언매)", "국어(언매)"),
    ]
    
    passed = 0
    for input_name, expected in test_cases:
        result, score = matcher.match(input_name)
        status = "PASS" if result == expected else "FAIL"
        if status == "PASS":
            passed += 1
        print(f"  {status}: '{input_name}' → '{result}' (expected: '{expected}', score={score:.1f})")
    
    print(f"\n  결과: {passed}/{len(test_cases)} 통과")
    return passed == len(test_cases)


def test_index_optimizer():
    """INDEX 최적화 테스트"""
    print("\n" + "="*60)
    print("2. INDEX 최적화 테스트")
    print("="*60)
    
    data = load_workbook(EXCEL_PATH)
    if "INDEX" not in data:
        print("  SKIP: INDEX 시트 없음")
        return True
    
    optimizer = IndexOptimizer(data["INDEX"])
    stats = optimizer.get_stats()
    print(f"  총 행: {stats['total_rows']}")
    print(f"  인덱싱: {stats['indexed_rows']}")
    print(f"  MultiIndex: {stats['use_multiindex']}")
    
    # 조회 성능 테스트
    start = time.time()
    for _ in range(100):
        optimizer.lookup(130, 135, 65, 62, "이과")
    elapsed = (time.time() - start) * 10  # ms per lookup
    
    print(f"  조회 시간: {elapsed:.2f}ms (100회 평균)")
    
    return elapsed < 100  # 100ms 이하면 성공


def test_cutoff_extractor():
    """커트라인 추출 테스트"""
    print("\n" + "="*60)
    print("3. 커트라인 추출 테스트")
    print("="*60)
    
    data = load_workbook(EXCEL_PATH)
    if "PERCENTAGE" not in data:
        print("  SKIP: PERCENTAGE 시트 없음")
        return True
    
    extractor = CutoffExtractor(data["PERCENTAGE"])
    stats = extractor.get_stats()
    print(f"  대학/전공: {stats['total_programs']}개")
    
    # 샘플 추출
    programs = extractor.list_available_programs()[:5]
    print(f"  샘플 프로그램: {programs}")
    
    # 커트라인 추출 테스트
    test_found = 0
    for prog in programs:
        # 대학명 추출 시도
        result = extractor.extract_cutoffs(prog[:2], prog[2:4])
        if result['found']:
            test_found += 1
            print(f"  ✓ {prog}: 적정={result['cutoff_safe']}, 예상={result['cutoff_normal']}")
    
    return test_found > 0


def test_probability_model():
    """확률 계산 테스트"""
    print("\n" + "="*60)
    print("4. 확률 계산 테스트")
    print("="*60)
    
    model = AdmissionProbabilityModel()
    
    test_cases = [
        (98.0, 95.0, 90.0, 85.0, "적정"),
        (92.0, 95.0, 90.0, 85.0, "예상"),
        (87.0, 95.0, 90.0, 85.0, "소신"),
        (80.0, 95.0, 90.0, 85.0, "상향"),
    ]
    
    passed = 0
    for score, safe, normal, risk, expected_level in test_cases:
        result = model.calculate(score, safe, normal, risk)
        status = "PASS" if result.level == expected_level else "FAIL"
        if status == "PASS":
            passed += 1
        print(f"  {status}: score={score} → {result.level} (expected={expected_level}), prob={result.probability:.2%}")
    
    print(f"\n  결과: {passed}/{len(test_cases)} 통과")
    return passed == len(test_cases)


def test_disqualification_engine():
    """결격 체크 테스트"""
    print("\n" + "="*60)
    print("5. 결격 체크 테스트")
    print("="*60)
    
    engine = DisqualificationEngine()
    print(f"  로드된 룰: {len(engine.rules)}개")
    
    # 정상 프로필
    normal_profile = StudentProfile(
        track=Track.SCIENCE,
        korean=ExamScore("국어(언매)", raw_total=80),
        math=ExamScore("수학(미적)", raw_total=75),
        english_grade=2,
        history_grade=3,
        inquiry1=ExamScore("물리학 Ⅰ", raw_total=50),
        inquiry2=ExamScore("화학 Ⅰ", raw_total=48),
    )
    
    # 결격 프로필 (영어 4등급)
    disqualified_profile = StudentProfile(
        track=Track.SCIENCE,
        korean=ExamScore("국어(언매)", raw_total=80),
        math=ExamScore("수학(미적)", raw_total=75),
        english_grade=4,  # 결격!
        history_grade=3,
        inquiry1=ExamScore("물리학 Ⅰ", raw_total=50),
        inquiry2=ExamScore("화학 Ⅰ", raw_total=48),
    )
    
    target = TargetProgram("서울대", "공대")
    
    # 정상 체크
    result1 = engine.check(normal_profile, target, severity_threshold=2)
    status1 = "PASS" if not result1.is_disqualified else "FAIL"
    print(f"  {status1}: 정상 프로필 → {'결격' if result1.is_disqualified else '통과'}")
    
    # 결격 체크
    result2 = engine.check(disqualified_profile, target, severity_threshold=2)
    status2 = "PASS" if result2.is_disqualified else "FAIL"
    print(f"  {status2}: 결격 프로필 → {'결격' if result2.is_disqualified else '통과'}")
    if result2.is_disqualified:
        print(f"       사유: {result2.reason}")
    
    return status1 == "PASS" and status2 == "PASS"


def test_e2e_pipeline():
    """전체 파이프라인 E2E 테스트"""
    print("\n" + "="*60)
    print("6. E2E 파이프라인 테스트")
    print("="*60)
    
    # 엑셀 로드
    print(f"  엑셀 로드: {EXCEL_PATH}")
    data = load_workbook(EXCEL_PATH)
    print(f"  로드된 시트: {len(data)}개")
    
    # 테스트 프로필
    profile = StudentProfile(
        track=Track.SCIENCE,
        korean=ExamScore("국어(언매)", raw_total=80, raw_common=55, raw_select=25),
        math=ExamScore("수학(미적)", raw_total=75, raw_common=50, raw_select=25),
        english_grade=2,
        history_grade=3,
        inquiry1=ExamScore("물리학 Ⅰ", raw_total=50),
        inquiry2=ExamScore("화학 Ⅰ", raw_total=48),
        targets=[
            TargetProgram("가천", "의학"),
            TargetProgram("건국", "자연"),
            TargetProgram("서울대", "공대"),
        ]
    )
    
    print(f"\n  학생 프로필:")
    print(f"    계열: {profile.track.value}")
    print(f"    국어: {profile.korean.raw_total}점")
    print(f"    수학: {profile.math.raw_total}점")
    print(f"    영어: {profile.english_grade}등급")
    print(f"    목표: {len(profile.targets)}개 대학")
    
    # 시뮬레이션 실행
    print(f"\n  시뮬레이션 실행 중...")
    start = time.time()
    result = compute_theory_result(data, profile, debug=True)
    elapsed = time.time() - start
    
    print(f"  실행 시간: {elapsed:.2f}초")
    print(f"  엔진 버전: {result.engine_version}")
    
    # 결과 출력
    print(f"\n  결과:")
    for prog in result.program_results:
        print(f"    {prog.target.university} {prog.target.major}:")
        print(f"      라인: {prog.level_theory.value}")
        print(f"      확률: {prog.p_theory}")
        print(f"      점수: {prog.score_theory}")
        if prog.disqualification.is_disqualified:
            print(f"      결격: {prog.disqualification.reason}")
    
    # 중간 결과
    print(f"\n  중간 계산 결과:")
    for key, value in list(result.raw_components.items())[:5]:
        print(f"    {key}: {value}")
    
    return len(result.program_results) > 0


def main():
    """메인 테스트 실행"""
    print("="*60)
    print(f"Theory Engine v{ENGINE_VERSION} 통합 테스트")
    print("="*60)
    
    results = {
        "과목 매칭": test_subject_matcher(),
        "INDEX 최적화": test_index_optimizer(),
        "커트라인 추출": test_cutoff_extractor(),
        "확률 계산": test_probability_model(),
        "결격 체크": test_disqualification_engine(),
        "E2E 파이프라인": test_e2e_pipeline(),
    }
    
    # 요약
    print("\n" + "="*60)
    print("테스트 결과 요약")
    print("="*60)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for name, result in results.items():
        status = "PASS" if result else "FAIL"
        print(f"  {status}: {name}")
    
    print(f"\n총 {passed}/{total} 통과")
    
    if passed == total:
        print("\n✅ 모든 테스트 통과!")
        return 0
    else:
        print("\n❌ 일부 테스트 실패")
        return 1


if __name__ == "__main__":
    sys.exit(main())
```

### 7.2 테스트 실행
```bash
cd C:\Neoprime
python tests/test_integration.py
```

---

## 📊 Phase 8: 검증 및 리팩토링 (지속)

### 8.1 검증 체크리스트

실행 후 다음 항목 확인:

- [ ] 과목 매칭 95% 이상
- [ ] INDEX 조회 100ms 이하
- [ ] 커트라인 정상 추출
- [ ] 확률 계산 범위 정상 (0-1)
- [ ] 결격 체크 작동
- [ ] E2E 파이프라인 완료
- [ ] 메모리 사용량 적정
- [ ] 에러 로깅 정상

### 8.2 디버깅 명령어

```bash
# 상세 로그 출력
python -c "
import logging
logging.basicConfig(level=logging.DEBUG)
from theory_engine.loader import load_workbook
from theory_engine.config import EXCEL_PATH
data = load_workbook(EXCEL_PATH)
print('로드 완료:', list(data.keys()))
"

# 특정 시트 구조 확인
python -c "
import pandas as pd
df = pd.read_excel('202511고속성장분석기(가채점)20251114 (1).xlsx', sheet_name='INDEX', nrows=5)
print(df.columns.tolist())
print(df.head())
"

# 메모리 프로파일링
python -c "
import tracemalloc
tracemalloc.start()
from theory_engine.loader import load_workbook
data = load_workbook()
current, peak = tracemalloc.get_traced_memory()
print(f'현재 메모리: {current / 10**6:.1f}MB')
print(f'최대 메모리: {peak / 10**6:.1f}MB')
tracemalloc.stop()
"
```

### 8.3 리팩토링 지침

테스트 실패 시:

1. **과목 매칭 실패**
   - `CANONICAL_SUBJECTS`에 누락된 과목 추가
   - 정규화 로직 조정

2. **INDEX 조회 느림**
   - MultiIndex 컬럼 확인
   - 캐싱 효과 점검

3. **커트라인 추출 실패**
   - 컬럼명 패턴 확인
   - 누백 범위 확인

4. **확률 계산 이상**
   - 커트라인 값 확인
   - 보간 로직 점검

5. **결격 체크 오작동**
   - 룰 조건 확인
   - 대학 패턴 점검

---

## 📝 완료 기준

### 필수 달성 항목
- [ ] 5개 모듈 모두 구현 완료
- [ ] 통합 테스트 6/6 통과
- [ ] 실제 엑셀 파일 기반 시뮬레이션 성공
- [ ] 에러 없이 run_theory_engine.py 실행

### 품질 지표
| 항목 | 목표 | 측정 방법 |
|------|------|----------|
| 과목 매칭 | 95%+ | test_subject_matcher |
| INDEX 조회 | <100ms | test_index_optimizer |
| 커트라인 | 80%+ 추출 | test_cutoff_extractor |
| 확률 정확도 | 90%+ | test_probability_model |
| 결격 정확도 | 95%+ | test_disqualification_engine |
| E2E 성공 | 100% | test_e2e_pipeline |

---

## 🔄 작업 순서 요약

```
1. matchers/subject_matcher.py 생성 → 테스트 ✓
2. optimizers/index_optimizer.py 생성 → 테스트 ✓
3. cutoff/cutoff_extractor.py 생성 → 테스트 ✓
4. probability/admission_model.py 생성 → 테스트 ✓
5. disqualification/disqualification_engine.py 생성 → 테스트 ✓
6. rules.py 통합 수정 → 테스트 ✓
7. tests/test_integration.py 생성 → 전체 테스트 ✓
8. run_theory_engine.py 최종 검증 ✓
9. 디버깅/리팩토링 (필요시 반복)
```

---

**이 프롬프트를 에이전트에게 주입하고 순서대로 실행하세요.**
