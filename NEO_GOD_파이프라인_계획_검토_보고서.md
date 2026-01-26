# NEO GOD 통합 파이프라인 계획 검토 보고서

**검토 일시**: 2026-01-26  
**검토자**: AI Assistant  
**계획 버전**: 최종 계획 v1.0

---

## ✅ 계획 강점

1. **명확한 단계 구분**: Phase A(즉시 실행)와 Phase B(고도화)로 구분하여 우선순위가 명확함
2. **구체적인 수정 위치**: 파일명과 라인 번호까지 명시되어 실행 가능성 높음
3. **검증 지표 명확**: BigQuery 테이블 수, 행 수 등 측정 가능한 지표 제시
4. **리스크 완화 방안**: 각 리스크에 대한 대응책 제시

---

## ⚠️ 발견된 이슈 및 개선 사항

### 1. **Phase A-1: `has_data` 필드 확인 필요**

**현재 계획**:
```python
target_sheets = [
    s['name'] for s in self.results['phase1']['sheets'] 
    if s['target_type'] in ['heavy', 'medium', 'light']
    and s.get('has_data', True)
]
```

**이슈**: `phase1_scouting.py`에서 `has_data` 필드를 실제로 반환하는지 확인 필요

**개선안**:
```python
target_sheets = [
    s['name'] for s in self.results['phase1']['sheets'] 
    if s['target_type'] in ['heavy', 'medium', 'light']
    and s.get('row_count', 0) > 0  # 실제 행 수로 확인
]
```

---

### 2. **Phase A-2: config.yaml 구조 확인**

**현재 계획**:
```yaml
sheet_processing:
  include_all: true
  exclude_sheets:
    - 메모장
```

**이슈**: `master_pipeline.py`에서 이 설정을 실제로 읽어서 사용하는지 확인 필요

**개선안**: 
- `master_pipeline.py`에 `sheet_processing` 설정 읽기 로직 추가
- 또는 `target_sheets` 필터링 로직에 직접 하드코딩

---

### 3. **Phase B-1: 검증 모드 구현 시 주의사항**

**현재 계획**: `validation_mode` 파라미터 추가

**개선 제안**:
- `warn_and_continue` 모드에서도 로그에 명확히 기록
- `preserve_staging` 모드에서 staging 테이블명에 타임스탬프 추가 (중복 방지)

```python
# 개선안
if validation_mode == 'preserve_staging':
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    preserved_table = f"{staging_table}_preserved_{timestamp}"
    self._copy_table(staging_table, preserved_table)
    logger.warning(f"검증 실패로 인해 staging 테이블 보존: {preserved_table}")
```

---

### 4. **Phase B-2: 시트별 임계값 하드코딩 vs 설정 파일**

**현재 계획**: `phase4_load.py`에 딕셔너리로 하드코딩

**개선안**: `config.yaml`에서 관리하도록 변경

```yaml
validation:
  sheet_specific_thresholds:
    INDEX: 0.95
    SUBJECT1: 0.95
    RAWSCORE: 0.10
    SUBJECT3: 0.10
    default: 0.95
```

그리고 `phase4_load.py`에서:
```python
def _get_null_threshold(self, sheet_name: str, default_threshold: float) -> float:
    """시트별 NULL 임계값 반환"""
    sheet_thresholds = self.config.get('validation', {}).get('sheet_specific_thresholds', {})
    return sheet_thresholds.get(sheet_name, sheet_thresholds.get('default', default_threshold))
```

---

### 5. **Phase B-3: 수식 메타데이터 경로 자동 감지**

**현재 상태 확인**: ✅ `output` 폴더에 이미 `{시트명}_formula_metadata.json` 파일들이 존재함

**개선안**: 수동 경로 지정 대신 자동 감지

```python
def normalize_dataframe(
    self,
    df: pd.DataFrame,
    sheet_name: str,  # 신규 추가
    # ... 기존 파라미터 ...
    formula_metadata_path: Optional[str] = None,
    preserve_formula_targets: bool = True
):
    # 자동 경로 감지
    if formula_metadata_path is None:
        default_path = Path(output_dir) / f"{sheet_name}_formula_metadata.json"
        if default_path.exists():
            formula_metadata_path = str(default_path)
```

---

### 6. **롤백 전략 보완**

**현재 계획**: "config.yaml만 이전 버전으로 복원"

**개선안**: 더 구체적인 롤백 절차

```markdown
## 롤백 절차

1. **Phase A 롤백**:
   ```powershell
   git checkout HEAD -- master_pipeline.py config.yaml
   ```

2. **Phase B 롤백**:
   ```powershell
   git checkout HEAD -- phase4_load.py phase3_normalization.py config.yaml
   ```

3. **BigQuery 테이블 롤백**:
   - `backup_table`에서 원본으로 복원
   - 또는 `_atomic_table_swap` 이전 상태로 복원
```

---

## 📋 실행 전 체크리스트

### Phase A 실행 전

- [ ] `phase1_scouting.py`에서 `has_data` 또는 `row_count` 필드 확인
- [ ] 현재 BigQuery 테이블 목록 백업 (스냅샷)
- [ ] `output` 폴더 백업 (필요시)
- [ ] `config.yaml` 현재 버전 백업

### Phase B 실행 전

- [ ] Phase A 완료 확인 (15개 테이블 검증)
- [ ] `formula_metadata.json` 파일들 존재 확인 ✅ (이미 확인됨)
- [ ] `master_pipeline.py`에서 `sheet_name` 전달 경로 확인

---

## 🔧 추가 개선 제안

### 1. **에러 복구 자동화**

```python
# phase4_load.py에 추가
def recover_from_failure(self, table_name: str):
    """실패한 적재 복구 시도"""
    staging_table = f"{table_name}_staging"
    backup_table = f"{table_name}_backup"
    
    if self._table_exists(backup_table):
        # 백업에서 복원
        self._copy_table(backup_table, table_name)
        logger.info(f"백업에서 복원 완료: {table_name}")
    elif self._table_exists(staging_table):
        # Staging 테이블 재검증
        # ...
```

### 2. **진행 상황 모니터링**

```python
# master_pipeline.py에 추가
def _log_progress(self, phase: str, current: int, total: int):
    """진행 상황 로깅"""
    percentage = (current / total) * 100
    logger.info(f"[{phase}] 진행률: {current}/{total} ({percentage:.1f}%)")
```

### 3. **설정 검증 함수**

```python
# config.yaml 로드 후 검증
def validate_config(config: dict) -> List[str]:
    """설정 파일 검증"""
    errors = []
    
    if config['validation']['null_threshold'] > 1.0:
        errors.append("null_threshold는 1.0 이하여야 합니다")
    
    # ... 추가 검증
    
    return errors
```

---

## 📊 예상 실행 시간

| Phase | 작업 | 예상 시간 |
|-------|------|----------|
| A-1 | 코드 수정 | 5분 |
| A-2 | config.yaml 수정 | 3분 |
| A-3 | 파이프라인 재실행 | 30-60분 (데이터 크기에 따라) |
| A-4 | BigQuery 검증 | 5분 |
| **Phase A 총계** | | **45-75분** |
| B-1 | 검증 모드 구현 | 30분 |
| B-2 | 시트별 임계값 | 20분 |
| B-3 | 수식 메타데이터 활용 | 40분 |
| B-4 | config 고도화 | 15분 |
| **Phase B 총계** | | **105분 (약 1.75시간)** |

---

## ✅ 최종 평가

**전체 평가**: ⭐⭐⭐⭐☆ (4/5)

**강점**:
- 실행 가능한 구체적인 계획
- 명확한 단계 구분
- 검증 가능한 지표

**개선 필요**:
- 일부 필드 존재 여부 확인 필요
- 롤백 전략 구체화
- 설정 파일과 코드 간 연동 확인

**권장 사항**:
1. Phase A 실행 전에 `phase1_scouting.py`의 반환 구조 확인
2. Phase B는 Phase A 완료 후 실행
3. 각 단계마다 Git 커밋으로 상태 저장

---

## 🚀 실행 준비 완료 여부

- [x] 계획 명확성
- [x] 파일 경로 확인
- [ ] 코드 구조 검증 (실행 전)
- [x] 리스크 완화 방안
- [ ] 롤백 전략 구체화

**결론**: 계획은 매우 잘 구성되어 있으며, 위의 개선 사항을 반영하면 더욱 견고해집니다. **즉시 실행 가능**하지만, 실행 전에 `phase1_scouting.py`의 반환 구조를 한 번 더 확인하는 것을 권장합니다.
