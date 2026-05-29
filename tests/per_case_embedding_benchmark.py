#!/usr/bin/env python3
"""
Per-Test-Case Embedding Benchmark (HF API)
Evaluate selected Hugging Face API embedders for each Text2SQL test case.

Outputs: results/per_case_embedding_benchmark_YYYYMMDD_HHMMSS.{xlsx,json}
"""

import os
import sys
import time
import json
from datetime import datetime
from dataclasses import dataclass
from typing import List, Dict, Any, Tuple

import numpy as np
import pandas as pd

# Add src and tests to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))
sys.path.append(os.path.join(os.path.dirname(__file__)))

from text2sql_rag.embedding import Embedder

try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))
    load_dotenv()
except Exception:
    pass

# Import test cases from comprehensive test
try:
    import comprehensive_text2sql_test as ct
except Exception as e:
    print(f"Warning: could not import comprehensive_text2sql_test: {e}")
    ct = None

# Embedding models to test (HF API)
EMBEDDERS = [
    "BAAI/bge-base-en-v1.5",
    "intfloat/e5-large-v2",
    "intfloat/multilingual-e5-large",
    "mixedbread-ai/mxbai-embed-large-v1",
    "BAAI/bge-small-en-v1.5",
]

@dataclass
class PerCaseResult:
    test_id: str
    question: str
    expected_sql: str
    model: str
    embed_time: float
    question_dim: int
    retrieval_quality: float
    status: str
    error: str = ""

class PerCaseBenchmark:
    def __init__(self):
        self.results: List[PerCaseResult] = []
        self.api_key_ok = bool(os.getenv("HUGGINGFACE_API_KEY") or os.getenv("HUGGINGFACE_API_TOKEN"))
        # Prepare test cases
        if ct is not None:
            gen = ct.ComprehensiveText2SQLTester()
            self.test_cases = gen.test_cases
        else:
            # Fallback minimal cases
            self.test_cases = [
                ct.Text2SQLTestCase(id="T001", thai_question="แสดงชื่อผู้ป่วยทั้งหมด", expected_sql="SELECT p.Name FROM patients p;", query_type="basic_select", difficulty="easy", description="Basic"),
            ] if ct else []

    def _cosine_similarity(self, a: np.ndarray, b: np.ndarray) -> float:
        try:
            dot = float(np.dot(a, b))
            na = float(np.linalg.norm(a))
            nb = float(np.linalg.norm(b))
            if na == 0 or nb == 0:
                return 0.0
            return dot / (na * nb)
        except Exception:
            return 0.0

    def _retrieval_quality(self, embedder: Embedder, question: str) -> float:
        # Use simple schema-related texts as proxies
        schema_texts = [
            "patients table contains name age hospital medical_condition billing_amount",
            "database schema for healthcare patient data",
            "patient information includes demographics and billing",
        ]
        try:
            qv = embedder.embed_texts(question)
            qv = np.atleast_2d(qv)[0]
            sv = embedder.embed_texts(schema_texts)
            sims = []
            for row in np.atleast_2d(sv):
                sims.append(self._cosine_similarity(qv, row))
            return float(np.mean(sims)) if sims else 0.0
        except Exception:
            return 0.0

    def run(self) -> bool:
        if not self.api_key_ok:
            print("HUGGINGFACE_API_KEY/TOKEN not set in environment")
            return False
        if not self.test_cases:
            print("No test cases available")
            return False

        print("Per-Test-Case Embedding Benchmark (HF API)")
        print(f"Models: {len(EMBEDDERS)} | Test cases: {len(self.test_cases)}")
        print("=" * 70)

        for i, tc in enumerate(self.test_cases, 1):
            print(f"[{i}/{len(self.test_cases)}] {tc.id}: {tc.thai_question}")
            for model in EMBEDDERS:
                try:
                    emb = Embedder(model)
                    t0 = time.time()
                    qvec = emb.embed_texts(tc.thai_question)
                    dt = time.time() - t0
                    dim = int(np.atleast_2d(qvec).shape[-1])
                    rq = self._retrieval_quality(emb, tc.thai_question)
                    self.results.append(PerCaseResult(
                        test_id=tc.id,
                        question=tc.thai_question,
                        expected_sql=tc.expected_sql,
                        model=model,
                        embed_time=dt,
                        question_dim=dim,
                        retrieval_quality=rq,
                        status="success",
                    ))
                    print(f"  - {model}: time {dt:.3f}s | dim {dim} | rq {rq:.3f}")
                except Exception as e:
                    self.results.append(PerCaseResult(
                        test_id=tc.id,
                        question=tc.thai_question,
                        expected_sql=tc.expected_sql,
                        model=model,
                        embed_time=999.0,
                        question_dim=0,
                        retrieval_quality=0.0,
                        status="failed",
                        error=str(e),
                    ))
                    print(f"  - {model}: FAILED ({e})")
            print()
        return True

    def export(self) -> Tuple[str, str]:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        os.makedirs("results", exist_ok=True)
        excel_path = f"results/per_case_embedding_benchmark_{timestamp}.xlsx"
        json_path = f"results/per_case_embedding_benchmark_{timestamp}.json"

        rows: List[Dict[str, Any]] = []
        for r in self.results:
            rows.append({
                'Test ID': r.test_id,
                'Question': r.question,
                'Expected SQL': r.expected_sql,
                'Model': r.model,
                'Embed Time (s)': float(r.embed_time),
                'Dimension': int(r.question_dim),
                'Retrieval Quality': float(r.retrieval_quality),
                'Status': r.status,
                'Error': r.error,
            })
        df = pd.DataFrame(rows)

        with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='All Results', index=False)
            if not df.empty:
                # Per-test pivot
                pivot_by_test = pd.pivot_table(
                    df[df['Status'] == 'success'],
                    index=['Test ID', 'Question'],
                    columns='Model',
                    values='Retrieval Quality',
                    aggfunc='mean'
                )
                pivot_by_test.to_excel(writer, sheet_name='RQ by TestCase')

                # Per-model summary
                summary = df.groupby('Model').agg({
                    'Retrieval Quality': 'mean',
                    'Embed Time (s)': 'mean',
                    'Dimension': 'max',
                }).round(3)
                summary.to_excel(writer, sheet_name='Model Summary')

        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump({'timestamp': datetime.now().isoformat(), 'results': rows}, f, ensure_ascii=False, indent=2)

        return excel_path, json_path


def main():
    bench = PerCaseBenchmark()
    ok = bench.run()
    if not ok:
        return
    xlsx, jsn = bench.export()
    print("Exported:")
    print(f"- Excel: {xlsx}")
    print(f"- JSON:  {jsn}")


if __name__ == '__main__':
    main()


