"""
의존관계 그래프 생성: 셀/시트 레벨 데이터 플로우
"""

import pandas as pd
import json
from pathlib import Path
from typing import Dict, List, Set
from collections import defaultdict
import logging
import ast

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GraphBuilder:
    """그래프 빌더"""
    
    def __init__(self, formula_catalog_path: str = "outputs/formula_catalog.csv"):
        self.catalog_path = formula_catalog_path
        self.df: pd.DataFrame = None
    
    def load_catalog(self):
        """카탈로그 로드"""
        self.df = pd.read_csv(self.catalog_path)
    
    def build_dependency_graph(self) -> Dict:
        """셀 레벨 의존관계 그래프 생성"""
        if self.df is None:
            self.load_catalog()
        
        logger.info("의존관계 그래프 생성 중...")
        
        node_sample_limit = 1000
        edge_sample_limit = 1000
        nodes = []
        edges = []
        edge_count_total = 0
        
        # 노드 샘플만 구성 (전체는 너무 큼)
        for _, row in self.df.head(node_sample_limit).iterrows():
            node_id = f"{row['sheet_name']}!{row['cell_ref']}"
            nodes.append({
                "id": node_id,
                "sheet": row["sheet_name"],
                "cell": row["cell_ref"],
                "type": "formula",
            })
        
        # 엣지: 참조 관계
        for _, row in self.df.iterrows():
            source = f"{row['sheet_name']}!{row['cell_ref']}"
            
            refs = []
            for col in ("range_refs", "cell_refs"):
                v = row.get(col)
                if pd.isna(v):
                    continue
                if isinstance(v, list):
                    refs.extend(v)
                elif isinstance(v, str) and v.strip():
                    # formula_parse.py는 JSON 문자열로 저장함
                    try:
                        parsed = json.loads(v)
                        if isinstance(parsed, list):
                            refs.extend(parsed)
                        else:
                            refs.append(str(parsed))
                    except Exception:
                        # legacy: 파이썬 repr(list)인 경우도 처리
                        try:
                            parsed = ast.literal_eval(v)
                            if isinstance(parsed, list):
                                refs.extend(parsed)
                        except Exception:
                            continue

            for ref in set(refs):
                if not isinstance(ref, str) or not ref:
                    continue
                target = ref if "!" in ref else f"{row['sheet_name']}!{ref}"
                edge_count_total += 1
                if len(edges) < edge_sample_limit:
                    edges.append({
                        "from": source,
                        "to": target,
                        "type": "ref",
                    })
        
        graph = {
            "node_count_total": int(len(self.df)),
            "edge_count_total": int(edge_count_total),
            "nodes": nodes,
            "edges": edges,
        }
        
        logger.info(f"그래프 생성 완료: {len(self.df)}개 노드(샘플 {len(nodes)}), {edge_count_total}개 엣지(샘플 {len(edges)})")
        return graph
    
    def build_sheet_flow_graph(self) -> Dict:
        """시트 레벨 플로우 그래프"""
        if self.df is None:
            self.load_catalog()
        
        logger.info("시트 플로우 그래프 생성 중...")
        
        # 시트 간 참조 집계 (weight 포함)
        sheet_edge_counts = defaultdict(int)
        
        for _, row in self.df.iterrows():
            source_sheet = row['sheet_name']
            refs = []
            for col in ("range_refs", "cell_refs"):
                v = row.get(col)
                if pd.isna(v):
                    continue
                if isinstance(v, list):
                    refs.extend(v)
                elif isinstance(v, str) and v.strip():
                    try:
                        parsed = json.loads(v)
                        if isinstance(parsed, list):
                            refs.extend(parsed)
                    except Exception:
                        try:
                            parsed = ast.literal_eval(v)
                            if isinstance(parsed, list):
                                refs.extend(parsed)
                        except Exception:
                            continue

            for ref in refs:
                if not isinstance(ref, str) or "!" not in ref:
                    continue
                target_sheet = ref.split("!", 1)[0]
                if target_sheet and target_sheet != source_sheet:
                    sheet_edge_counts[(source_sheet, target_sheet)] += 1
        
        # 그래프 생성
        nodes = [{'id': sheet, 'type': 'sheet'} for sheet in self.df['sheet_name'].unique()]
        edges = []
        for (src, dst), w in sorted(sheet_edge_counts.items(), key=lambda x: x[1], reverse=True):
            edges.append({
                "from": src,
                "to": dst,
                "type": "sheet_ref",
                "weight": w,
            })
        
        graph = {
            'nodes': nodes,
            'edges': edges,
        }
        
        logger.info(f"시트 플로우 그래프 생성 완료: {len(nodes)}개 시트, {len(edges)}개 참조")
        return graph
    
    def save_graphs(self, output_dir: str = "outputs"):
        """그래프 저장"""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        dep_graph = self.build_dependency_graph()
        flow_graph = self.build_sheet_flow_graph()
        
        with open(output_path / "dependency_graph.json", 'w', encoding='utf-8') as f:
            json.dump(dep_graph, f, ensure_ascii=False, indent=2)
        
        with open(output_path / "sheet_flow_graph.json", 'w', encoding='utf-8') as f:
            json.dump(flow_graph, f, ensure_ascii=False, indent=2)
        
        logger.info("그래프 저장 완료")


def main():
    """메인 함수"""
    builder = GraphBuilder()
    builder.save_graphs()
    print("그래프 생성 완료!")


if __name__ == "__main__":
    main()
