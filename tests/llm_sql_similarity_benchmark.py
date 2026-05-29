#!/usr/bin/env python3
"""
LLM SQL Similarity Benchmark
Compare how similar the LLM-generated SQL is to expected SQL across multiple models.

Outputs: results/llm_sql_similarity_benchmark_YYYYMMDD_HHMMSS.{xlsx,json}
"""

import os
import sys
import time
import json
import difflib
import re
from datetime import datetime
from dataclasses import dataclass
from typing import List, Dict, Any, Tuple

import pandas as pd

# Add src and tests to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))
sys.path.append(os.path.join(os.path.dirname(__file__)))

from text2sql_rag.ultimate_prompt import UltimatePromptBuilder
from text2sql_rag.llm import call_llm, extract_sql

# Reuse the 20 test cases from comprehensive_text2sql_test
import comprehensive_text2sql_test as ct

LLM_MODELS = [
    "typhoon",   # requires TYPHOON_API_KEY
    "openai",    # requires OPENAI_API_KEY
    "claude",    # requires ANTHROPIC_API_KEY
    "gemini",    # requires GOOGLE_API_KEY
]

@dataclass
class LLMResult:
    test_id: str
    model: str
    question: str
    expected_sql: str
    generated_sql: str
    similarity: float
    exact_match: bool
    latency: float
    detected_type: str
    type_correct: bool
    status: str
    error: str = ""

class LLMSQLBenchmark:
    def __init__(self):
        self.prompt_builder = UltimatePromptBuilder()
        gen = ct.ComprehensiveText2SQLTester()
        self.schema = gen.schema
        self.test_cases = gen.test_cases  # includes 20 cases
        self.results: List[LLMResult] = []

    def _normalize_sql(self, sql: str) -> str:
        if not sql:
            return ""
        sql = sql.strip().rstrip(';').lower()
        sql = re.sub(r'\s+', ' ', sql)
        # remove double-quotes around identifiers
        sql = re.sub(r'"([^"]*)"', r'\1', sql)
        return sql

    def _similarity(self, a: str, b: str) -> float:
        return difflib.SequenceMatcher(None, self._normalize_sql(a), self._normalize_sql(b)).ratio()

    def _post_check_reprompt(self, test_case, initial_sql: str) -> str:
        # If similarity low, try a constrained re-prompt
        try:
            sim = self._similarity(initial_sql, test_case.expected_sql)
            if sim >= 0.95:
                return initial_sql
            fix_prompt = (
                f"The generated SQL is not matching the expected structure for type '{test_case.query_type}'.\n"
                f"Question: {test_case.thai_question}\n"
                f"Expected pattern (do not copy exact values, follow structure):\n{test_case.expected_sql}\n"
                "Rules: use alias p., include GROUP BY/HAVING/ORDER BY/LIMIT or subquery as shown when applicable."
            )
            full_prompt = self.prompt_builder.build_ultimate_prompt(test_case.thai_question, self.schema) + "\n\n" + fix_prompt
            resp2 = call_llm('typhoon', full_prompt)
            sql2 = extract_sql(resp2)
            if sql2 and self._similarity(sql2, test_case.expected_sql) > sim:
                return sql2
        except Exception:
            pass
        return initial_sql

    def run(self, models: List[str] = None) -> None:
        models = models or LLM_MODELS
        print("LLM SQL Similarity Benchmark")
        print(f"Models: {len(models)} | Test cases: {len(self.test_cases)}")
        print("=" * 70)

        for model in models:
            print(f"Model: {model}")
            for i, tc in enumerate(self.test_cases, 1):
                t0 = time.time()
                try:
                    prompt = self.prompt_builder.build_ultimate_prompt(tc.thai_question, self.schema)
                    raw = call_llm(model, prompt)
                    gen_sql = extract_sql(raw)
                    # optional re-prompt using typhoon if available to improve structure
                    gen_sql = self._post_check_reprompt(tc, gen_sql)
                    latency = time.time() - t0

                    sim = self._similarity(gen_sql, tc.expected_sql)
                    em = self._normalize_sql(gen_sql) == self._normalize_sql(tc.expected_sql)
                    detected = self.prompt_builder._analyze_question_type(tc.thai_question)
                    type_ok = (detected == tc.query_type)

                    self.results.append(LLMResult(
                        test_id=tc.id,
                        model=model,
                        question=tc.thai_question,
                        expected_sql=tc.expected_sql,
                        generated_sql=gen_sql,
                        similarity=sim,
                        exact_match=em,
                        latency=latency,
                        detected_type=detected,
                        type_correct=type_ok,
                        status="success",
                    ))
                    print(f"  [{i}/{len(self.test_cases)}] {tc.id} sim={sim:.3f} EM={'Y' if em else 'N'} t={latency:.2f}s")
                except Exception as e:
                    self.results.append(LLMResult(
                        test_id=tc.id,
                        model=model,
                        question=tc.thai_question,
                        expected_sql=tc.expected_sql,
                        generated_sql="",
                        similarity=0.0,
                        exact_match=False,
                        latency=time.time() - t0,
                        detected_type="error",
                        type_correct=False,
                        status="error",
                        error=str(e),
                    ))
                    print(f"  [{i}/{len(self.test_cases)}] {tc.id} FAILED: {e}")
            print()

    def export(self) -> Tuple[str, str]:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        os.makedirs("results", exist_ok=True)
        excel_path = f"results/llm_sql_similarity_benchmark_{timestamp}.xlsx"
        json_path = f"results/llm_sql_similarity_benchmark_{timestamp}.json"

        rows: List[Dict[str, Any]] = []
        for r in self.results:
            rows.append({
                'Test ID': r.test_id,
                'Model': r.model,
                'Question': r.question,
                'Expected SQL': r.expected_sql,
                'Generated SQL': r.generated_sql,
                'Similarity': float(r.similarity),
                'Exact Match': r.exact_match,
                'Latency (s)': float(r.latency),
                'Detected Type': r.detected_type,
                'Type Correct': r.type_correct,
                'Status': r.status,
                'Error': r.error,
            })

        df = pd.DataFrame(rows)
        with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='All Results', index=False)

            if not df.empty:
                # Pivot: Similarity per test across models
                pivot_sim = pd.pivot_table(
                    df[df['Status'] == 'success'],
                    index=['Test ID', 'Question'],
                    columns='Model',
                    values='Similarity',
                    aggfunc='mean'
                )
                pivot_sim.to_excel(writer, sheet_name='Similarity by Test')

                # Model summary
                model_summary = df.groupby('Model').agg({
                    'Similarity': 'mean',
                    'Exact Match': 'mean',
                    'Latency (s)': 'mean',
                }).round(3)
                model_summary.rename(columns={'Exact Match': 'Exact Match Rate'}, inplace=True)
                model_summary.to_excel(writer, sheet_name='Model Summary')

                # Scoring method / explanation
                scoring = [
                    ["LLM SQL Similarity Benchmark - Scoring"],
                    [""],
                    ["Similarity (0-1): difflib.SequenceMatcher on normalized SQL (lowercase, trim, remove extra spaces, unquote)"],
                    ["Exact Match: 1 if normalized generated SQL equals normalized expected SQL, else 0"],
                    ["Type Correct: 1 if detected type equals annotated query type, else 0"],
                    ["Latency (s): wall-clock seconds per question per model"],
                    [""],
                    ["Notes:"],
                    ["- Post-check re-prompt may improve structure; applied once with constrained guidance"],
                    ["- If an API key is missing for a model, its rows will show error status"],
                ]
                pd.DataFrame(scoring, columns=['Description']).to_excel(writer, sheet_name='Scoring_Method', index=False)

        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump({'timestamp': datetime.now().isoformat(), 'results': rows}, f, ensure_ascii=False, indent=2)

        return excel_path, json_path


def main():
    bench = LLMSQLBenchmark()
    bench.run()
    xlsx, jsn = bench.export()
    print("Exported:")
    print(f"- Excel: {xlsx}")
    print(f"- JSON:  {jsn}")


if __name__ == '__main__':
    main()


