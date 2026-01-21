# Theory Engine v3.0 - 빠른 시작 가이드

**버전**: 3.0.0  
**업데이트**: 2026-01-17

---

## 🚀 빠른 실행

```bash
# 전체 파이프라인 실행
python run_theory_engine.py

# 테스트 실행
python tests/test_theory_engine.py
```

---

## 📂 주요 파일

| 파일 | 용도 |
|------|------|
| `run_theory_engine.py` | 전체 파이프라인 실행 스크립트 |
| `theory_engine/` | 핵심 엔진 모듈 (7개 파일) |
| `tests/test_theory_engine.py` | 테스트 코드 (10개 테스트) |

---

## 📚 문서

### 사용자용
- **theory_engine/README.md**: 상세 사용법 및 API

### 개발자용
1. **THEORY_ENGINE_구현_완료_보고서_20260117.md**: 구현 내역
2. **EXCEL_시트_구조_분석_20260117.md**: 엑셀 구조 분석
3. **THEORY_ENGINE_실행_결과_검증_20260117.md**: 실행 검증
4. **작업_최종_총결산_20260117.md**: 전체 작업 종합

---

## ✅ 검증 완료

- ✅ 10개 테스트 100% 통과
- ✅ 13개 시트 로드 성공
- ✅ 전체 파이프라인 실행 검증
- ✅ 복원율 83% (목표 85% 거의 달성)

---

## 🎯 주요 성과

**구현 완료**:
- config.py, constants.py, utils.py, loader.py, model.py, rules.py
- 총 2,200+ 라인 코드

**검증 완료**:
- 국어 80점 → 표준 125, 백분위 89
- 수학 75점 → 표준 121, 백분위 82
- 가천의학 환산점수 73.13 산출

**문서화 완료**:
- 4개 상세 보고서
- 1개 사용자 가이드

---

**프로젝트**: NeoPrime  
**엔진**: Theory Engine v3.0  
**상태**: ✅ 작업 완료
