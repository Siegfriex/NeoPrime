"""
매핑 리포트 생성: 엔진 함수 ↔ 엑셀 범위/수식 그룹 근거
"""

from pathlib import Path
import pandas as pd
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ReportGenerator:
    """리포트 생성기"""
    
    def __init__(self, outputs_dir: str = "outputs"):
        self.outputs_dir = Path(outputs_dir)
    
    def generate_mapping_report(self) -> str:
        """매핑 리포트 생성"""
        logger.info("매핑 리포트 생성 중...")
        
        report_lines = [
            "# Theory Engine 매핑 리포트",
            "",
            "이 리포트는 파이썬 시뮬레이션 엔진 함수가 어떤 엑셀 범위/수식 그룹을 담당하는지 보여줍니다.",
            "",
            "## 1. RAWSCORE 변환 함수",
            "",
            "**함수**: `convert_raw_to_standard()`",
            "",
            "**담당 엑셀 범위**:",
            "- 시트: RAWSCORE",
            "- 컬럼: 영역, 과목명, 원점수, 표준점수, 백분위, 등급, 누적%",
            "",
            "**수식 그룹**:",
            "- RAWSCORE 시트의 조회 수식 (VLOOKUP/INDEX-MATCH 등)",
            "",
            "## 2. INDEX 조회 함수",
            "",
            "**함수**: `lookup_index()`",
            "",
            "**담당 엑셀 범위**:",
            "- 시트: INDEX",
            "- 약 20만 행의 점수 조합 키 테이블",
            "",
            "## 3. PERCENTAGE 조회 함수",
            "",
            "**함수**: `lookup_percentage()`",
            "",
            "**담당 엑셀 범위**:",
            "- 시트: PERCENTAGE",
            "- 대학별 누적백분위 환산점수표 (1100+ 컬럼)",
            "",
            "## 4. 결격 체크 함수",
            "",
            "**함수**: `check_disqualification()`",
            "",
            "**담당 엑셀 범위**:",
            "- 시트: RESTRICT",
            "- 결격사유 룰 테이블",
            "",
            "## 5. 전체 계산 파이프라인",
            "",
            "**함수**: `compute_theory_result()`",
            "",
            "**데이터 플로우**:",
            "1. 원점수 입력 → RAWSCORE → 표준점수/백분위/등급",
            "2. 점수 조합 → INDEX → 누백/전국등수",
            "3. 대학/누백 → PERCENTAGE → 환산점수/커트라인",
            "4. RESTRICT → 결격 사유 체크",
            "5. 최종 합격 가능성/라인 판정",
            "",
        ]

        # 6) sheet flow graph TOP edges
        report_lines.extend([
            "## 6. 시트 플로우 그래프 (TOP 10 edges)",
            "",
        ])
        flow_path = self.outputs_dir / "sheet_flow_graph.json"
        if flow_path.exists():
            try:
                flow = json.loads(flow_path.read_text(encoding="utf-8"))
                edges = flow.get("edges", []) if isinstance(flow, dict) else []
                edges = sorted(edges, key=lambda e: e.get("weight", 0), reverse=True)
                for e in edges[:10]:
                    src = e.get("from")
                    dst = e.get("to")
                    w = e.get("weight")
                    report_lines.append(f"- {src} → {dst} (weight={w})")
                report_lines.append("")
            except Exception:
                report_lines.append("- (sheet_flow_graph.json 파싱 실패)")
                report_lines.append("")
        else:
            report_lines.append("- (sheet_flow_graph.json 없음)")
            report_lines.append("")

        # 7) rule candidates summary
        report_lines.extend([
            "## 7. 룰 후보 요약",
            "",
        ])
        rule_path = self.outputs_dir / "rule_candidates.csv"
        if rule_path.exists():
            try:
                df = pd.read_csv(rule_path)
                report_lines.append(f"- 총 룰 후보: {len(df):,}")
                if "source_type" in df.columns:
                    report_lines.append("- source_type 분포:")
                    for k, v in df["source_type"].value_counts().to_dict().items():
                        report_lines.append(f"  - {k}: {v:,}")
                report_lines.append("")
            except Exception:
                report_lines.append("- (rule_candidates.csv 파싱 실패)")
                report_lines.append("")
        else:
            report_lines.append("- (rule_candidates.csv 없음)")
            report_lines.append("")
        
        # 8) rule bundles TOP
        report_lines.extend([
            "## 8. 룰 번들 (TOP 10)",
            "",
        ])
        bundle_path = self.outputs_dir / "rule_bundles.csv"
        if bundle_path.exists():
            try:
                bundle_df = pd.read_csv(bundle_path)
                bundle_df = bundle_df.sort_values('rule_count', ascending=False)
                for idx, row in bundle_df.head(10).iterrows():
                    key = row.get('bundle_key', 'N/A')
                    count = row.get('rule_count', 0)
                    samples = row.get('sample_summaries', '')
                    report_lines.append(f"- **{key}**: {count}개 룰")
                    if samples:
                        report_lines.append(f"  - 샘플: {samples[:100]}...")
                report_lines.append("")
            except Exception:
                report_lines.append("- (rule_bundles.csv 파싱 실패)")
                report_lines.append("")
        else:
            report_lines.append("- (rule_bundles.csv 없음)")
            report_lines.append("")
        
        # 9) rule summaries sample
        report_lines.extend([
            "## 9. 룰 요약 샘플",
            "",
        ])
        summarized_path = self.outputs_dir / "rule_candidates_summarized.csv"
        if summarized_path.exists():
            try:
                summarized_df = pd.read_csv(summarized_path)
                if "summary_ko" in summarized_df.columns:
                    # source_type별 샘플
                    for source_type in summarized_df["source_type"].value_counts().head(5).index:
                        sample = summarized_df[summarized_df["source_type"] == source_type].iloc[0]
                        summary = sample.get("summary_ko", "")
                        location = sample.get("location", "")
                        if summary:
                            report_lines.append(f"- **{source_type}** ({location}): {summary[:150]}")
                    report_lines.append("")
            except Exception:
                report_lines.append("- (rule_candidates_summarized.csv 파싱 실패)")
                report_lines.append("")
        else:
            report_lines.append("- (rule_candidates_summarized.csv 없음)")
            report_lines.append("")

        # footer
        report_lines.extend([
            "---",
            "",
            "*이 리포트는 자동 생성되었습니다.*",
        ])
        
        report_text = "\n".join(report_lines)
        
        output_file = self.outputs_dir / "mapping_report.md"
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(report_text)
        
        logger.info(f"매핑 리포트 저장: {output_file}")
        return str(output_file)


def main():
    """메인 함수"""
    generator = ReportGenerator()
    generator.generate_mapping_report()
    print("매핑 리포트 생성 완료!")


if __name__ == "__main__":
    main()
