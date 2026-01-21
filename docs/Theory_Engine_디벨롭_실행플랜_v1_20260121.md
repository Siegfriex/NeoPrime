# Theory Engine v3.0 디벨롭 실행플랜 (v1.0)

- **기준 문서(입력)**  
  - `docs/Theory_Engine_기능명세서_v3.0.md` (기능명세/AC)  
  - `docs/Theory_Engine_기능명세_검증보고서_v1.md` (식별 갭)  
  - `docs/Theory_Engine_명세vs실제_최종비교표.md` (종합 비교/권장사항)
- **범위**: Theory Engine(`theory_engine/`) 한정
- **버전**: v1.0
- **작성일**: 2026-01-21
- **검증 상태**: ✅ 1차 검증 완료(테스트/실데이터 축/갭 반영)

---

## 1) 현재 상태 스냅샷(사실 기반)

- **테스트**: `pytest` 전체 통과(총 51개)  
- **CRITICAL 갭(문서 기준)**  
  - **PERCENTAGE 축 방향/레벨 매핑**: ✅ 수정 완료 + 테스트로 고정  
  - **Alias 오매핑(역매핑 키 정규화/부분매칭 제거)**: ✅ 수정 완료 + 테스트로 고정

> 현재 “정확도·설명가능성·성능” 관점에서 남은 P0/P1 항목은 아래 2~3절.

---

## 2) 남은 갭 요약(문서 기반 우선순위)

### P0(오늘) — 품질/신뢰도 즉시 영향

- **GAP-H01**: 의료계열 판정 과도(“의” 단일 포함 → 오탐 가능)  
- **GAP-H02**: 결격 룰 대학명 별칭 미인식(연대/고대 등) → 결격 누락 가능  
- **GAP-H03**: 설명 가능성 플래그 부재(어떤 매칭/폴백이 발생했는지 결과에 없음)

### P1(이번 주) — 운영가능성/확장

- **GAP-H04**: 성능(단일 예측 4.4초/케이스) → 캐싱/인덱싱 필요  
- **GAP-M01**: Golden Case 10+ / Sanity 5+ 목표 대비 부족(회귀 방지/신뢰도)

---

## 3) 무엇을 / 어떻게 디벨롭할 것인가 (실행 단위)

### P0-1. 결격 룰에 “대학명 정규화” 적용 (GAP-H02)

- **목표**: 입력이 `"연대"`, `"고대"`여도 `"연세대"`, `"고려대"`와 동일하게 결격 룰이 적용되도록 보장
- **구현 방향**
  - **단일 진실원(SSOT)**: 대학명 정규화 로직을 한 곳으로 모으기
    - 옵션 A(권장): `theory_engine/alias.py` 같은 공용 모듈 신설  
      - `normalize_university(text) -> str`  
      - `resolve_university_alias(text) -> official`
    - 옵션 B: `CutoffExtractor`의 alias를 “서비스”로 분리(순환 의존성 주의)
  - `DisqualificationEngine.check()`에서 룰 매칭 전에:
    - `official = resolve_university_alias(target.university)`
    - 룰 매칭은 `official` 기준으로 수행
- **수용 기준(AC)**
  - `"연대"` 입력과 `"연세대"` 입력이 **동일한 결격 결과**를 만든다.
- **테스트**
  - `test_restrict_university_alias()` 추가  
    - 입력: `TargetProgram("연대", "...")`  
    - 기대: `TargetProgram("연세대", "...")`와 동일 트리거

---

### P0-2. 의료계열 판정 키워드 정교화 (GAP-H01)

- **문제**: 현 구현은 `"의"` 단일 포함으로 의료계열로 판정될 수 있음(예: “의류학”)
- **구현 방향**
  - `_is_medical_major(major: str) -> bool`를 **명시 키워드 기반**으로 재정의
  - 정규화 후 **정확/시작 매칭**만 허용:
    - 키워드 예: `의예`, `의학`, `약학`, `치의예`, `치의학`, `한의예`, `한의학`, `수의예`, `수의학`, `간호학`
  - 전공 Alias 체인(예: 의예→의학)을 결격에서도 동일하게 적용(SSOT)
- **수용 기준(AC)**
  - 의료계열은 과탐 2과목 룰이 적용되나, “의류학/의사소통” 등은 오탐 0
- **테스트**
  - `test_restrict_medical_keywords()` 추가  
    - True 케이스: `"의예"`, `"의학"`, `"치의예"`  
    - False 케이스: `"의류학"`, `"의사소통"`  

---

### P0-3. Explainability 필드(플래그/근거) 최소 구현 (GAP-H03)

- **목표**: “왜 이 결과가 나왔는지”를 **필드로 추적 가능**하게(디버그 가능/사용자 신뢰)
- **구현 방향(최소 스코프)**
  - `model.py`에 `ExplainabilityInfo`(또는 동등 구조)를 추가하고, 다음을 최소 포함:
    - `university_mapping`: input/matched/method(alias|exact|fuzzy)/fuzzy_score?/alias_used?
    - `major_mapping`: input/matched/method/alias_chain(“의예→의학”)
    - `cutoff_source`: sheet(INDEX|PERCENTAGE), column, percentile(20/50/80 또는 student_pct), interpolated 여부
    - `disqualification_triggers`: rule_id/reason/value
  - `compute_theory_result()`에서 ProgramResult 생성 시 함께 채움
    - (중요) **결격 결과**도 explainability에 “왜 결격인지” 포함
- **수용 기준(AC)**
  - 모든 결과에 explainability가 존재하고, method/alias_chain/cutoff_source가 채워진다.
- **테스트**
  - `test_explainability_fields()` / `test_explainability_alias_chain()` / `test_explainability_cutoff_source()` 추가

---

### P1-1. 성능 개선(캐싱/인덱싱/로그) (GAP-H04)

- **현상(문서 근거)**: 테스트 환경 기준 평균 4.4초/케이스  
- **핵심 원인 후보**
  - `loader.py`가 호출될 때마다 **엑셀 전체 로드 + 품질검사 + 로그 출력**을 수행
- **구현 방향**
  - 워크북 캐싱: `@lru_cache(maxsize=1)` 또는 mtime 기반 캐시
  - “검증/품질검사/로깅”을 실행 모드별로 분리:
    - 개발/검증: verbose + 품질검사 ON
    - 프로덕션: 기본 OFF(필수 최소만)
  - INDEX/컷오프 인덱싱:
    - INDEX는 `IndexOptimizer`에서 MultiIndex/해시 인덱스 빌드(로드 1회)
    - 컷오프는 컬럼명 정규화 인덱스(딕셔너리) 빌드(로드 1회)
- **완료 기준**
  - 초기 로드(캐시 미스) < 10초 허용
  - 캐시 히트 단일 예측 < 1초 목표(문서 권장)
- **테스트/측정**
  - `pytest-benchmark` 도입
  - 단일/배치(10/100) 성능 회귀 방지

---

### P1-2. Golden Case 10+ / Sanity 5+ 확장 (GAP-M01)

- **목표**: “당연한 규칙(축 방향/오매핑 방지/결격 별칭/의예→의학)”이 회귀하지 않도록 테스트로 고정
- **추가할 케이스 예시**
  - 대학 별칭: `"연대"`, `"고대"` 입력
  - 전공 별칭 체인: `"의예"` 입력 → `"의학"` 컬럼 선택
  - 결격 오탐 방지: `"의류학"`은 의료계열 아님
  - 제2외국어 관련(해당 룰 존재 시)
- **완료 기준**
  - Golden Case 10개 100% 통과
  - Sanity 5개 100% 통과

---

## 4) 즉시 실행 순서(추천)

- **오늘(P0)**: P0-1 → P0-2 → P0-3  
- **이번 주(P1)**: P1-1 → P1-2

---

## 5) 검증(재현 가능한 커맨드)

- 전체 테스트: `python -m pytest tests/ -q`
- 성능(추가 후): `pytest --benchmark-only` (도입 시)

---

## 6) 비고(범위 밖)

- A/B 갭 보정 모델(`s_final = s_theory + r(x, s_theory)`)은 데이터셋/백테스트가 필요하므로 P2~로 이관 권장

