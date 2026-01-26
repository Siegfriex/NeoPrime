# ============================================================
# NEO GOD Ultra 통합 Stress Test 실행기
# Integration Stress Test Runner
# ============================================================

import sys
import json
import time
from pathlib import Path
from datetime import datetime

# Windows 인코딩 설정
if sys.platform == 'win32':
    try:
        if hasattr(sys.stdout, 'reconfigure'):
            sys.stdout.reconfigure(encoding='utf-8')
        if hasattr(sys.stderr, 'reconfigure'):
            sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

from stress_test_engine import StressTestEngine, TestScenario, run_stress_test


class IntegrationStressTestRunner:
    """통합 Stress Test 실행기"""

    def __init__(self, output_dir: str = './stress_test_output'):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.start_time = None
        self.results = {}

    def run_full_stress_test(self, cases_per_scenario: int = 50) -> dict:
        """전체 Stress Test 실행"""
        print("=" * 70)
        print("NEO GOD Ultra 통합 Stress Test")
        print("=" * 70)
        print(f"시작 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"케이스 수: {cases_per_scenario * 5} (시나리오당 {cases_per_scenario}개)")
        print()

        self.start_time = time.perf_counter()

        # Phase 1: Stress Test Engine 실행
        print("[Phase 1] Stress Test Engine 실행...")
        summary, report_files = run_stress_test(cases_per_scenario)
        self.results['stress_test'] = summary

        # Phase 2: 결과 분석
        print("\n[Phase 2] 결과 분석...")
        analysis = self._analyze_results(summary)
        self.results['analysis'] = analysis

        # Phase 3: 최종 리포트 생성
        print("\n[Phase 3] 최종 리포트 생성...")
        final_report = self._generate_final_report()

        # 리포트 저장
        final_report_path = self.output_dir / 'final_stress_test_report.json'
        with open(final_report_path, 'w', encoding='utf-8') as f:
            json.dump(final_report, f, ensure_ascii=False, indent=2, default=str)

        # 마크다운 리포트
        md_report = self._generate_markdown_report(final_report)
        md_report_path = self.output_dir / 'stress_test_report.md'
        with open(md_report_path, 'w', encoding='utf-8') as f:
            f.write(md_report)

        total_time = time.perf_counter() - self.start_time

        print("\n" + "=" * 70)
        print("STRESS TEST 완료")
        print("=" * 70)
        print(f"총 실행 시간: {total_time:.2f}초")
        print(f"리포트 위치: {self.output_dir}")
        print(f"  - {final_report_path}")
        print(f"  - {md_report_path}")

        return final_report

    def _analyze_results(self, summary: dict) -> dict:
        """결과 분석"""
        test_summary = summary.get('test_summary', {})

        # 시나리오별 상태 판정
        scenario_status = {}
        for scenario in TestScenario:
            key = f'scenario_{scenario.value}'
            if key in test_summary:
                result = test_summary[key]
                pass_rate = result.get('pass_rate', 0)

                if pass_rate >= 0.95:
                    status = 'EXCELLENT'
                elif pass_rate >= 0.9:
                    status = 'GOOD'
                elif pass_rate >= 0.8:
                    status = 'WARNING'
                else:
                    status = 'CRITICAL'

                scenario_status[scenario.name] = {
                    'pass_rate': pass_rate,
                    'status': status,
                    'details': result,
                }

        # 전체 상태 판정
        overall_pass_rate = test_summary.get('overall_pass_rate', 0)
        if overall_pass_rate >= 0.95:
            overall_status = 'EXCELLENT'
        elif overall_pass_rate >= 0.9:
            overall_status = 'GOOD'
        elif overall_pass_rate >= 0.8:
            overall_status = 'WARNING'
        else:
            overall_status = 'CRITICAL'

        return {
            'overall_status': overall_status,
            'overall_pass_rate': overall_pass_rate,
            'scenario_status': scenario_status,
            'recommendations': self._generate_recommendations(scenario_status),
        }

    def _generate_recommendations(self, scenario_status: dict) -> list:
        """개선 권장 사항 생성"""
        recommendations = []

        for scenario_name, status_info in scenario_status.items():
            if status_info['status'] in ['WARNING', 'CRITICAL']:
                if scenario_name == 'EDGE_CASES':
                    recommendations.append({
                        'scenario': scenario_name,
                        'issue': '경계값 처리 취약',
                        'recommendation': 'NULL, 빈 문자열, 극단값 처리 로직 강화 필요',
                    })
                elif scenario_name == 'MALFORMED_DATA':
                    recommendations.append({
                        'scenario': scenario_name,
                        'issue': '비정상 데이터 처리 취약',
                        'recommendation': 'Excel 에러 코드 및 잘못된 형식 데이터 처리 로직 개선 필요',
                    })
                elif scenario_name == 'HIGH_VOLUME':
                    recommendations.append({
                        'scenario': scenario_name,
                        'issue': '대용량 데이터 처리 성능 문제',
                        'recommendation': '청크 크기 최적화 및 메모리 관리 개선 필요',
                    })
                elif scenario_name == 'MIXED_TYPES':
                    recommendations.append({
                        'scenario': scenario_name,
                        'issue': '혼합 타입 데이터 처리 취약',
                        'recommendation': '타입 추론 로직 개선 및 강제 형변환 로직 추가 필요',
                    })

        if not recommendations:
            recommendations.append({
                'scenario': 'ALL',
                'issue': 'None',
                'recommendation': '모든 시나리오가 정상 작동 중입니다.',
            })

        return recommendations

    def _generate_final_report(self) -> dict:
        """최종 리포트 생성"""
        total_time = time.perf_counter() - self.start_time if self.start_time else 0

        return {
            'report_metadata': {
                'report_type': 'NEO GOD Ultra Stress Test Report',
                'generated_at': datetime.now().isoformat(),
                'execution_time_seconds': round(total_time, 2),
            },
            'test_summary': self.results.get('stress_test', {}).get('test_summary', {}),
            'analysis': self.results.get('analysis', {}),
            'conclusion': self._generate_conclusion(),
        }

    def _generate_conclusion(self) -> dict:
        """결론 생성"""
        analysis = self.results.get('analysis', {})
        overall_status = analysis.get('overall_status', 'UNKNOWN')
        overall_pass_rate = analysis.get('overall_pass_rate', 0)

        if overall_status == 'EXCELLENT':
            verdict = 'NEO GOD Ultra Framework는 모든 Stress Test를 우수하게 통과했습니다.'
            production_ready = True
        elif overall_status == 'GOOD':
            verdict = 'NEO GOD Ultra Framework는 대부분의 Stress Test를 통과했습니다. 일부 개선 권장.'
            production_ready = True
        elif overall_status == 'WARNING':
            verdict = 'NEO GOD Ultra Framework에 일부 취약점이 발견되었습니다. 수정 후 재테스트 권장.'
            production_ready = False
        else:
            verdict = 'NEO GOD Ultra Framework에 심각한 문제가 발견되었습니다. 즉시 수정 필요.'
            production_ready = False

        return {
            'overall_status': overall_status,
            'overall_pass_rate': f"{overall_pass_rate:.1%}",
            'verdict': verdict,
            'production_ready': production_ready,
        }

    def _generate_markdown_report(self, report: dict) -> str:
        """마크다운 리포트 생성"""
        md = []
        md.append("# NEO GOD Ultra Stress Test Report\n")
        md.append(f"**생성 시간**: {report['report_metadata']['generated_at']}\n")
        md.append(f"**실행 시간**: {report['report_metadata']['execution_time_seconds']}초\n")

        md.append("\n## 1. 테스트 요약\n")
        summary = report.get('test_summary', {})
        md.append(f"- **총 테스트 케이스**: {summary.get('total_cases', 0)}\n")
        md.append(f"- **통과**: {summary.get('total_passed', 0)}\n")
        md.append(f"- **실패**: {summary.get('total_failed', 0)}\n")
        md.append(f"- **전체 통과율**: {summary.get('overall_pass_rate', 0):.1%}\n")
        md.append(f"- **총 에러 수**: {summary.get('total_errors', 0)}\n")

        md.append("\n## 2. 시나리오별 결과\n")
        md.append("| 시나리오 | 총 케이스 | 통과 | 실패 | 통과율 | 상태 |\n")
        md.append("|----------|----------|------|------|--------|------|\n")

        analysis = report.get('analysis', {})
        scenario_status = analysis.get('scenario_status', {})

        for scenario in TestScenario:
            key = f'scenario_{scenario.value}'
            if key in summary:
                result = summary[key]
                status_info = scenario_status.get(scenario.name, {})
                status = status_info.get('status', 'UNKNOWN')

                status_emoji = {
                    'EXCELLENT': '✅',
                    'GOOD': '✅',
                    'WARNING': '⚠️',
                    'CRITICAL': '❌',
                }.get(status, '❓')

                md.append(f"| {scenario.name} | {result['total']} | {result['passed']} | "
                         f"{result['failed']} | {result['pass_rate']:.1%} | {status_emoji} {status} |\n")

        md.append("\n## 3. 분석 결과\n")
        md.append(f"**전체 상태**: {analysis.get('overall_status', 'UNKNOWN')}\n")

        recommendations = analysis.get('recommendations', [])
        if recommendations:
            md.append("\n### 권장 사항\n")
            for rec in recommendations:
                md.append(f"- **{rec['scenario']}**: {rec['issue']}\n")
                md.append(f"  - 권장: {rec['recommendation']}\n")

        md.append("\n## 4. 결론\n")
        conclusion = report.get('conclusion', {})
        md.append(f"**최종 판정**: {conclusion.get('overall_status', 'UNKNOWN')}\n")
        md.append(f"**통과율**: {conclusion.get('overall_pass_rate', '0%')}\n")
        md.append(f"**프로덕션 준비 상태**: {'✅ 준비 완료' if conclusion.get('production_ready') else '❌ 수정 필요'}\n")
        md.append(f"\n> {conclusion.get('verdict', '')}\n")

        return ''.join(md)


def main():
    """메인 실행"""
    import argparse

    parser = argparse.ArgumentParser(description='NEO GOD Ultra Integration Stress Test')
    parser.add_argument('--cases', type=int, default=50, help='Cases per scenario (default: 50)')
    parser.add_argument('--output', type=str, default='./stress_test_output', help='Output directory')

    args = parser.parse_args()

    runner = IntegrationStressTestRunner(output_dir=args.output)
    report = runner.run_full_stress_test(cases_per_scenario=args.cases)

    # 간단한 결과 출력
    print("\n" + "=" * 70)
    print("최종 결과")
    print("=" * 70)
    conclusion = report.get('conclusion', {})
    print(f"상태: {conclusion.get('overall_status', 'UNKNOWN')}")
    print(f"통과율: {conclusion.get('overall_pass_rate', '0%')}")
    print(f"프로덕션 준비: {'Yes' if conclusion.get('production_ready') else 'No'}")
    print(f"\n{conclusion.get('verdict', '')}")


if __name__ == '__main__':
    main()
