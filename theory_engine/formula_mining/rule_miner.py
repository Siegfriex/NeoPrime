"""
룰 후보 추출: IF/조건부서식/데이터검증 기반
"""

import pandas as pd
import re
from pathlib import Path
from typing import List, Dict
import logging
import json
import hashlib

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RuleMiner:
    """룰 마이너"""
    
    def __init__(self, formula_catalog_path: str = "outputs/formula_catalog.csv"):
        self.catalog_path = formula_catalog_path
        self.df: pd.DataFrame = None
        self.rules: List[Dict] = []
    
    def load_catalog(self):
        """카탈로그 로드"""
        self.df = pd.read_csv(self.catalog_path)
    
    def mine_rules(self) -> pd.DataFrame:
        """룰 후보 추출"""
        if self.df is None:
            self.load_catalog()
        
        logger.info("룰 후보 추출 중...")
        
        formula_col = 'effective_formula' if 'effective_formula' in self.df.columns else 'formula'
        
        for idx, row in self.df.iterrows():
            formula = row[formula_col]
            if pd.isna(formula):
                continue
            
            # IF/IFS/SWITCH 수식에서 룰 추출
            f = str(formula)
            f_upper = f.upper()
            # 순서 중요: IFS/SWITCH를 먼저 체크 (IF가 포함되어 있으므로)
            if 'IFS' in f_upper and 'IFS(' in f_upper:
                rules = self._extract_ifs_rules(row, f)
                if rules:
                    self.rules.extend(rules)
            elif 'SWITCH' in f_upper and 'SWITCH(' in f_upper:
                rules = self._extract_switch_rules(row, f)
                if rules:
                    self.rules.extend(rules)
            elif 'IF' in f_upper and 'IF(' in f_upper:
                rules = self._extract_if_rules(row, f)
                if rules:
                    self.rules.extend(rules)

        # 조건부서식/데이터검증 룰 후보 합치기 (있으면)
        self._append_cf_dv_rules()
        
        rule_df = pd.DataFrame(self.rules)
        logger.info(f"룰 후보 {len(rule_df)}개 추출")
        return rule_df
    
    def _extract_if_rules(self, row: pd.Series, formula: str) -> List[Dict]:
        """
        IF 수식에서 룰 후보 추출

        기존 regex 방식은 중첩 IF / 함수 인자 내부의 콤마 때문에 깨짐.
        여기서는 문자열/괄호 깊이를 추적해서 IF(...)의 3개 인자를 안전하게 분리한다.
        """
        out: List[Dict] = []
        for if_idx, condition, true_val, false_val in self._iter_if_calls(formula):
            rid = f"R{len(self.rules) + len(out) + 1:04d}"
            loc = f"{row['sheet_name']}!{row['cell_ref']}"
            rule_data = {
                "rule_id": rid,
                "source_type": "formula_if",
                "location": loc,
                "if_index": if_idx,
                "condition": condition,
                "true_value": true_val,
                "false_value": false_val,
                "human_hint": f"IF {condition} THEN {true_val} ELSE {false_val}",
                "confidence": "high" if condition and true_val else "low",
            }
            rule_data["rule_uid"] = self._generate_rule_uid(rule_data)
            out.append(rule_data)
        return out

    def _extract_ifs_rules(self, row: pd.Series, formula: str) -> List[Dict]:
        """IFS(condition1,val1, condition2,val2, ..., [default]) 룰 후보 추출"""
        out: List[Dict] = []
        for call_idx, cond_val_pairs, default_val in self._iter_ifs_calls(formula):
            loc = f"{row['sheet_name']}!{row['cell_ref']}"
            for branch_i, (cond, val) in enumerate(cond_val_pairs):
                rid = f"R{len(self.rules) + len(out) + 1:04d}"
                rule_data = {
                    "rule_id": rid,
                    "source_type": "formula_ifs",
                    "location": loc,
                    "if_index": call_idx,
                    "condition": cond,
                    "true_value": val,
                    "false_value": default_val if branch_i == len(cond_val_pairs) - 1 else "",
                    "human_hint": f"IFS branch {branch_i}: IF {cond} THEN {val}" + (f" ELSE {default_val}" if default_val and branch_i == len(cond_val_pairs) - 1 else ""),
                    "confidence": "medium" if cond and val else "low",
                }
                rule_data["rule_uid"] = self._generate_rule_uid(rule_data)
                out.append(rule_data)
        return out
    
    def _extract_switch_rules(self, row: pd.Series, formula: str) -> List[Dict]:
        """SWITCH(expr, value1, result1, value2, result2, ..., [default]) 룰 후보 추출"""
        out: List[Dict] = []
        for call_idx, expr, value_result_pairs, default_val in self._iter_switch_calls(formula):
            loc = f"{row['sheet_name']}!{row['cell_ref']}"
            for branch_i, (val, result) in enumerate(value_result_pairs):
                rid = f"R{len(self.rules) + len(out) + 1:04d}"
                condition = f"{expr}=={val}"
                rule_data = {
                    "rule_id": rid,
                    "source_type": "formula_switch",
                    "location": loc,
                    "if_index": call_idx,
                    "condition": condition,
                    "true_value": result,
                    "false_value": default_val if branch_i == len(value_result_pairs) - 1 else "",
                    "human_hint": f"SWITCH branch {branch_i}: IF {expr}=={val} THEN {result}" + (f" ELSE {default_val}" if default_val and branch_i == len(value_result_pairs) - 1 else ""),
                    "confidence": "medium" if expr and val and result else "low",
                }
                rule_data["rule_uid"] = self._generate_rule_uid(rule_data)
                out.append(rule_data)
        return out
    
    def _generate_rule_uid(self, rule_data: Dict) -> str:
        """결정적 rule_uid 생성 (sha1 기반)"""
        key_parts = [
            rule_data.get("source_type", ""),
            rule_data.get("location", ""),
            rule_data.get("condition", ""),
            rule_data.get("true_value", ""),
            rule_data.get("false_value", ""),
        ]
        key_str = "|".join(str(p) for p in key_parts)
        return hashlib.sha1(key_str.encode('utf-8')).hexdigest()[:16]

    def _iter_ifs_calls(self, formula: str):
        """formula 문자열에서 IFS( ... ) 호출들을 순회하며 (idx, [(cond,val),...], default) 반환"""
        s = formula.strip()
        if s.startswith("="):
            s = s[1:]
        s_upper = s.upper()

        i = 0
        while i < len(s):
            idx = s_upper.find("IFS", i)
            if idx < 0:
                break

            # 단어 경계 체크
            if idx > 0 and (s_upper[idx - 1].isalnum() or s_upper[idx - 1] in {"_", "."}):
                i = idx + 3
                continue

            j = idx + 3
            while j < len(s) and s[j].isspace():
                j += 1
            if j >= len(s) or s[j] != "(":
                i = idx + 3
                continue

            content, end_pos = self._extract_paren_content(s, j)
            if content is None:
                i = j + 1
                continue

            args = self._split_top_level_args(content)
            pairs = []
            default_val = ""
            
            # 짝수 개면 모두 (cond,val) 쌍, 홀수 개면 마지막이 default
            if len(args) % 2 == 1:
                default_val = args[-1].strip()
                args = args[:-1]
            
            for k in range(0, len(args) - 1, 2):
                cond = args[k].strip()
                val = args[k + 1].strip()
                if cond or val:
                    pairs.append((cond, val))
            
            if pairs:
                yield idx, pairs, default_val

            i = end_pos + 1
    
    def _iter_switch_calls(self, formula: str):
        """formula 문자열에서 SWITCH(expr, val1, res1, val2, res2, ..., [default]) 호출들을 순회하며 (idx, expr, [(val,res),...], default) 반환"""
        s = formula.strip()
        if s.startswith("="):
            s = s[1:]
        s_upper = s.upper()

        i = 0
        while i < len(s):
            idx = s_upper.find("SWITCH", i)
            if idx < 0:
                break

            # 단어 경계 체크
            if idx > 0 and (s_upper[idx - 1].isalnum() or s_upper[idx - 1] in {"_", "."}):
                i = idx + 6
                continue

            j = idx + 6
            while j < len(s) and s[j].isspace():
                j += 1
            if j >= len(s) or s[j] != "(":
                i = idx + 6
                continue

            content, end_pos = self._extract_paren_content(s, j)
            if content is None:
                i = j + 1
                continue

            args = self._split_top_level_args(content)
            if len(args) < 3:  # 최소: expr, val1, res1
                i = end_pos + 1
                continue
            
            expr = args[0].strip()
            value_result_pairs = []
            default_val = ""
            
            # 나머지 인자: (val1, res1, val2, res2, ...) 또는 (..., default)
            remaining = args[1:]
            if len(remaining) % 2 == 1:
                default_val = remaining[-1].strip()
                remaining = remaining[:-1]
            
            for k in range(0, len(remaining) - 1, 2):
                val = remaining[k].strip()
                res = remaining[k + 1].strip()
                if val or res:
                    value_result_pairs.append((val, res))
            
            if expr and value_result_pairs:
                yield idx, expr, value_result_pairs, default_val

            i = end_pos + 1

    def _append_cf_dv_rules(self):
        """outputs/*.json에서 CF/DV 룰을 읽어 rule_candidates에 합친다."""
        # 파일이 없으면 스킵
        cf_path = Path("outputs/conditional_formats.json")
        dv_path = Path("outputs/data_validations.json")

        base_n = len(self.rules)

        def _next_id(n):
            return f"R{n + 1:04d}"

        # Conditional Formats
        if cf_path.exists():
            try:
                cf_data = json.loads(cf_path.read_text(encoding="utf-8"))
                if isinstance(cf_data, list):
                    for item in cf_data:
                        sheet = item.get("sheet")
                        sqref = item.get("sqref") or item.get("range")
                        loc = f"{sheet}!{sqref}" if sheet and sqref else (sheet or "")
                        formulas = item.get("formulas") or []
                        cond = " ; ".join(formulas) if formulas else f"type={item.get('type')} operator={item.get('operator')}"
                        rid = _next_id(base_n + len(self.rules) - base_n)
                        rule_data = {
                            "rule_id": rid,
                            "source_type": "conditional_format",
                            "location": loc,
                            "if_index": None,
                            "condition": cond,
                            "true_value": "",
                            "false_value": "",
                            "human_hint": f"CF on {loc}: {cond}",
                            "confidence": "low",
                        }
                        rule_data["rule_uid"] = self._generate_rule_uid(rule_data)
                        self.rules.append(rule_data)
            except Exception:
                pass

        # Data Validations
        if dv_path.exists():
            try:
                dv_data = json.loads(dv_path.read_text(encoding="utf-8"))
                if isinstance(dv_data, list):
                    for item in dv_data:
                        sheet = item.get("sheet")
                        sqref = item.get("sqref") or item.get("range")
                        loc = f"{sheet}!{sqref}" if sheet and sqref else (sheet or "")
                        f1 = item.get("formula1")
                        f2 = item.get("formula2")
                        cond_parts = [f"type={item.get('type')}", f"op={item.get('operator')}"]
                        if f1:
                            cond_parts.append(f"f1={f1}")
                        if f2:
                            cond_parts.append(f"f2={f2}")
                        cond = " ".join([p for p in cond_parts if p and p != "None"])
                        rid = _next_id(base_n + len(self.rules) - base_n)
                        rule_data = {
                            "rule_id": rid,
                            "source_type": "data_validation",
                            "location": loc,
                            "if_index": None,
                            "condition": cond,
                            "true_value": "",
                            "false_value": "",
                            "human_hint": f"DV on {loc}: {cond}",
                            "confidence": "low",
                        }
                        rule_data["rule_uid"] = self._generate_rule_uid(rule_data)
                        self.rules.append(rule_data)
            except Exception:
                pass

    def _iter_if_calls(self, formula: str):
        """formula 문자열에서 IF( ... ) 호출들을 순회하며 (idx, cond, t, f) 반환"""
        s = formula.strip()
        if s.startswith("="):
            s = s[1:]
        s_upper = s.upper()

        i = 0
        while i < len(s):
            idx = s_upper.find("IF", i)
            if idx < 0:
                break

            # 단어 경계 체크 (DIFF 같은 오탐 방지)
            if idx > 0 and (s_upper[idx - 1].isalnum() or s_upper[idx - 1] in {"_", "."}):
                i = idx + 2
                continue

            j = idx + 2
            while j < len(s) and s[j].isspace():
                j += 1
            if j >= len(s) or s[j] != "(":
                i = idx + 2
                continue

            content, end_pos = self._extract_paren_content(s, j)
            if content is None:
                i = j + 1
                continue

            args = self._split_top_level_args(content)
            if len(args) >= 2:
                cond = args[0].strip()
                tval = args[1].strip()
                fval = args[2].strip() if len(args) >= 3 else ""
                yield idx, cond, tval, fval

            i = end_pos + 1

    def _extract_paren_content(self, s: str, open_paren_idx: int):
        """s[open_paren_idx]=='(' 일 때, 대응되는 ')'까지의 내부 문자열과 닫는 위치를 반환"""
        depth = 0
        in_str = False
        i = open_paren_idx + 1
        while i < len(s):
            ch = s[i]
            if in_str:
                if ch == '"':
                    # Excel 문자열 escape: "" -> "
                    if i + 1 < len(s) and s[i + 1] == '"':
                        i += 2
                        continue
                    in_str = False
                i += 1
                continue

            if ch == '"':
                in_str = True
                i += 1
                continue
            if ch == "(":
                depth += 1
            elif ch == ")":
                if depth == 0:
                    return s[open_paren_idx + 1:i], i
                depth -= 1
            i += 1
        return None, None

    def _split_top_level_args(self, content: str) -> List[str]:
        """IF 인자 문자열을 최상위 레벨(괄호 depth=0) 기준으로 ,/; 분리"""
        args: List[str] = []
        buf: List[str] = []
        depth = 0
        in_str = False
        i = 0
        while i < len(content):
            ch = content[i]
            if in_str:
                buf.append(ch)
                if ch == '"':
                    if i + 1 < len(content) and content[i + 1] == '"':
                        buf.append('"')
                        i += 2
                        continue
                    in_str = False
                i += 1
                continue

            if ch == '"':
                in_str = True
                buf.append(ch)
                i += 1
                continue
            if ch == "(":
                depth += 1
            elif ch == ")":
                if depth > 0:
                    depth -= 1

            if depth == 0 and ch in {",", ";"}:
                args.append("".join(buf).strip())
                buf = []
                i += 1
                continue

            buf.append(ch)
            i += 1

        tail = "".join(buf).strip()
        if tail or content.strip():
            args.append(tail)
        return args
    
    def save_rules(self, output_path: str = "outputs/rule_candidates.csv"):
        """룰 후보 저장"""
        rule_df = self.mine_rules()
        output_file = Path(output_path)
        rule_df.to_csv(output_file, index=False, encoding='utf-8-sig')
        logger.info(f"룰 후보 저장: {output_file}")
        return output_file


def main():
    """메인 함수"""
    miner = RuleMiner()
    miner.save_rules()
    print("룰 후보 추출 완료!")


if __name__ == "__main__":
    main()
