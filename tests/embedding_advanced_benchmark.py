#!/usr/bin/env python3
"""
Advanced Embedding Benchmark (HF API)
- Retrieval/Search: Recall@k, MRR, nDCG (binary relevance from expected SQL references)
- Embedding Quality: STS correlation (cosine vs label), Clustering accuracy (nearest-centroid by query type)
- Efficiency: Throughput, Latency, Memory footprint estimate

Outputs: results/embedding_advanced_benchmark_YYYYMMDD_HHMMSS.{xlsx,json}
"""

import os
import sys
import time
import json
import math
from datetime import datetime
from dataclasses import dataclass
from typing import List, Dict, Any, Tuple

import numpy as np
import pandas as pd

# Add src and tests
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))
sys.path.append(os.path.join(os.path.dirname(__file__)))

from text2sql_rag.embedding import Embedder
import comprehensive_text2sql_test as ct

try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))
    load_dotenv()
except Exception:
    pass

EMBEDDERS = [
    "BAAI/bge-base-en-v1.5",
    "intfloat/e5-large-v2",
    "intfloat/multilingual-e5-large",
    "mixedbread-ai/mxbai-embed-large-v1",
    "BAAI/bge-small-en-v1.5",
]

SCHEMA_COLUMNS = [
    'Name', 'Age', 'Hospital', 'Medical_Condition', 'Billing Amount', 'DoctorID'
]

DOC_CORPUS = [
    "Column: Name - patient full name",
    "Column: Age - patient age",
    "Column: Hospital - hospital name",
    "Column: Medical_Condition - disease condition",
    "Column: Billing Amount - medical billing amount",
    "Column: DoctorID - doctor identifier",
    # table docs
    "Table: patients - patient records table with demographics and billing",
]

@dataclass
class RetrievalMetrics:
    recall_at_10: float
    recall_at_50: float
    mrr: float
    ndcg: float

@dataclass
class QualityMetrics:
    sts_corr: float
    clustering_acc: float

@dataclass
class EfficiencyMetrics:
    throughput: float
    latency: float
    dimension: int
    memory_mb_batch100: float

class AdvancedEmbeddingBenchmark:
    def __init__(self):
        gen = ct.ComprehensiveText2SQLTester()
        self.test_cases = gen.test_cases  # 20 cases
        self.results_rows: List[Dict[str, Any]] = []
        self.model_summaries: List[Dict[str, Any]] = []

    def _extract_relevant_docs(self, expected_sql: str) -> List[int]:
        sql = expected_sql.lower()
        relevant = []
        col_to_idx = {
            'name': 0,
            'age': 1,
            'hospital': 2,
            'medical_condition': 3,
            'billing amount': 4,
            'doctorid': 5,
        }
        for key, idx in col_to_idx.items():
            if key in sql:
                relevant.append(idx)
        # patients table relevance
        if ' from patients' in sql or '\nfrom patients' in sql:
            relevant.append(6)
        return sorted(set(relevant))

    def _rank_docs(self, embedder: Embedder, query: str, docs: List[str]) -> List[int]:
        q = embedder.embed_texts(query)
        q = np.atleast_2d(q)[0]
        D = embedder.embed_texts(docs)
        D = np.atleast_2d(D)
        sims = D @ q / (np.linalg.norm(D, axis=1) * (np.linalg.norm(q) + 1e-12) + 1e-12)
        ranked = np.argsort(-sims)
        return ranked.tolist()

    def _recall_at_k(self, ranked: List[int], relevant: List[int], k: int) -> float:
        if not relevant:
            return 0.0
        topk = set(ranked[:min(k, len(ranked))])
        hits = sum(1 for r in relevant if r in topk)
        return hits / len(relevant)

    def _mrr(self, ranked: List[int], relevant: List[int]) -> float:
        if not relevant:
            return 0.0
        for i, idx in enumerate(ranked, start=1):
            if idx in relevant:
                return 1.0 / i
        return 0.0

    def _ndcg(self, ranked: List[int], relevant: List[int]) -> float:
        if not relevant:
            return 0.0
        rel_set = set(relevant)
        dcg = 0.0
        for i, idx in enumerate(ranked[:len(ranked)], start=1):
            rel = 1.0 if idx in rel_set else 0.0
            dcg += rel / math.log2(i + 1)
        # ideal dcg
        ideal = 0.0
        for i in range(1, min(len(relevant), len(ranked)) + 1):
            ideal += 1.0 / math.log2(i + 1)
        return dcg / ideal if ideal > 0 else 0.0

    def _retrieval_metrics(self, embedder: Embedder, tc) -> RetrievalMetrics:
        ranked = self._rank_docs(embedder, tc.thai_question, DOC_CORPUS)
        relevant = self._extract_relevant_docs(tc.expected_sql)
        return RetrievalMetrics(
            recall_at_10=self._recall_at_k(ranked, relevant, 10),
            recall_at_50=self._recall_at_k(ranked, relevant, 50),
            mrr=self._mrr(ranked, relevant),
            ndcg=self._ndcg(ranked, relevant),
        )

    def _sts_correlation(self, embedder: Embedder) -> float:
        # Build pairs: same-type pairs labeled 1, different-type labeled 0
        questions = [tc.thai_question for tc in self.test_cases]
        types = [tc.query_type for tc in self.test_cases]
        # Sample up to 50 pairs
        pairs = []
        for i in range(len(questions)):
            for j in range(i + 1, len(questions)):
                label = 1.0 if types[i] == types[j] else 0.0
                pairs.append((questions[i], questions[j], label))
        if len(pairs) > 60:
            pairs = pairs[:60]
        # Compute similarities
        sims = []
        labels = []
        for a, b, lab in pairs:
            v = embedder.embed_texts([a, b])
            v = np.atleast_2d(v)
            sim = float(np.dot(v[0], v[1]) / (np.linalg.norm(v[0]) * np.linalg.norm(v[1]) + 1e-12))
            sims.append(sim)
            labels.append(lab)
        if not sims:
            return 0.0
        # Pearson correlation as proxy (no scipy)
        sims_arr = np.array(sims)
        labels_arr = np.array(labels)
        sims_norm = (sims_arr - sims_arr.mean()) / (sims_arr.std() + 1e-9)
        labels_norm = (labels_arr - labels_arr.mean()) / (labels_arr.std() + 1e-9)
        corr = float(np.mean(sims_norm * labels_norm))
        return corr

    def _clustering_accuracy(self, embedder: Embedder) -> float:
        # Nearest-centroid by query type (purity accuracy)
        type_set = sorted(set(tc.query_type for tc in self.test_cases))
        type_to_idx = {t: i for i, t in enumerate(type_set)}
        # compute centroids
        type_vecs: Dict[str, List[np.ndarray]] = {t: [] for t in type_set}
        for tc in self.test_cases:
            v = embedder.embed_texts(tc.thai_question)
            type_vecs[tc.query_type].append(np.atleast_2d(v)[0])
        centroids = {t: np.mean(np.stack(vs, axis=0), axis=0) for t, vs in type_vecs.items() if vs}
        # assign
        correct = 0
        for tc in self.test_cases:
            v = np.atleast_2d(embedder.embed_texts(tc.thai_question))[0]
            best_t = None
            best_sim = -1e9
            for t, c in centroids.items():
                sim = float(np.dot(v, c) / (np.linalg.norm(v) * np.linalg.norm(c) + 1e-12))
                if sim > best_sim:
                    best_sim = sim
                    best_t = t
            if best_t == tc.query_type:
                correct += 1
        return correct / len(self.test_cases)

    def _efficiency(self, embedder: Embedder) -> EfficiencyMetrics:
        # Warm-up
        _ = embedder.embed_texts("warm up")
        # Latency (median over 10 single calls)
        latencies = []
        for _ in range(10):
            t0 = time.time()
            _ = embedder.embed_texts("single test")
            latencies.append(time.time() - t0)
            time.sleep(0.05)
        latency = float(np.median(latencies))
        # Throughput over a batch of texts
        batch = [f"sample text {i}" for i in range(100)]
        t0 = time.time()
        _ = embedder.embed_texts(batch)
        elapsed = time.time() - t0
        throughput = 100.0 / elapsed if elapsed > 0 else 0.0
        # Dimension
        dim_vec = np.atleast_2d(embedder.embed_texts("dim probe")).shape[-1]
        dimension = int(dim_vec)
        memory_mb = (dimension * 4 * 100) / (1024 * 1024)  # batch 100, float32
        return EfficiencyMetrics(
            throughput=throughput,
            latency=latency,
            dimension=dimension,
            memory_mb_batch100=memory_mb,
        )

    def run(self) -> None:
        print("Advanced Embedding Benchmark")
        print(f"Models: {len(EMBEDDERS)} | Test cases: {len(self.test_cases)}")
        print("=" * 70)
        for model in EMBEDDERS:
            print(f"Model: {model}")
            try:
                emb = Embedder(model)
                # Aggregate metrics
                recalls_10 = []
                recalls_50 = []
                mrrs = []
                ndcgs = []
                for tc in self.test_cases:
                    rm = self._retrieval_metrics(emb, tc)
                    recalls_10.append(rm.recall_at_10)
                    recalls_50.append(rm.recall_at_50)
                    mrrs.append(rm.mrr)
                    ndcgs.append(rm.ndcg)
                    # Save per-test rows (optional)
                    self.results_rows.append({
                        'Model': model,
                        'Test ID': tc.id,
                        'Recall@10': rm.recall_at_10,
                        'Recall@50': rm.recall_at_50,
                        'MRR': rm.mrr,
                        'nDCG': rm.ndcg,
                    })
                sts = self._sts_correlation(emb)
                clus = self._clustering_accuracy(emb)
                eff = self._efficiency(emb)
                self.model_summaries.append({
                    'Model': model,
                    'Recall@10': float(np.mean(recalls_10)),
                    'Recall@50': float(np.mean(recalls_50)),
                    'MRR': float(np.mean(mrrs)),
                    'nDCG': float(np.mean(ndcgs)),
                    'STS_Corr': float(sts),
                    'Clustering_Acc': float(clus),
                    'Throughput (texts/s)': float(eff.throughput),
                    'Latency (s)': float(eff.latency),
                    'Dimension': int(eff.dimension),
                    'Memory_MB_Batch100': float(eff.memory_mb_batch100),
                })
                print(f"  Recall@10={np.mean(recalls_10):.3f} MRR={np.mean(mrrs):.3f} nDCG={np.mean(ndcgs):.3f} STS={sts:.3f} Clus={clus:.3f}")
            except Exception as e:
                self.model_summaries.append({
                    'Model': model,
                    'Error': str(e)
                })
                print(f"  FAILED: {e}")

    def export(self) -> Tuple[str, str]:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        os.makedirs("results", exist_ok=True)
        excel_path = f"results/embedding_advanced_benchmark_{timestamp}.xlsx"
        json_path = f"results/embedding_advanced_benchmark_{timestamp}.json"

        per_rows_df = pd.DataFrame(self.results_rows)
        summary_df = pd.DataFrame(self.model_summaries)

        with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
            if not per_rows_df.empty:
                per_rows_df.to_excel(writer, sheet_name='PerTest_Retrieval', index=False)
            summary_df.to_excel(writer, sheet_name='Model_Summary', index=False)

            scoring = [
                ["Advanced Embedding Benchmark - Scoring"],
                [""],
                ["Retrieval/Search"],
                ["- Recall@k: fraction of relevant docs (from expected SQL refs) appearing in top-k"],
                ["- MRR: 1 / rank of first relevant doc (averaged)"],
                ["- nDCG: sum(rel_i/log2(i+1)) normalized by ideal DCG (binary relevance)"],
                [""],
                ["Embedding Quality"],
                ["- STS correlation: Pearson correlation between cosine similarity and same-type label (1/0)"],
                ["- Clustering accuracy: nearest-centroid by query type (purity/accuracy)"],
                [""],
                ["Efficiency"],
                ["- Throughput: 100 texts / elapsed time"],
                ["- Latency: median time of 10 single-text embeddings after warm-up"],
                ["- Memory footprint: dimension*4 bytes * 100 / 1024^2 (MB estimate)"],
                [""],
                ["Notes:"],
                ["- Document corpus is schema-focused; relevance derived from columns/tables present in expected SQL"],
                ["- For production, replace with full vector store and human relevance labels"],
            ]
            pd.DataFrame(scoring, columns=['Description']).to_excel(writer, sheet_name='Scoring_Method', index=False)

        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'per_test': self.results_rows,
                'summary': self.model_summaries,
            }, f, ensure_ascii=False, indent=2)

        return excel_path, json_path


def main():
    bench = AdvancedEmbeddingBenchmark()
    bench.run()
    xlsx, jsn = bench.export()
    print("Exported:")
    print(f"- Excel: {xlsx}")
    print(f"- JSON:  {jsn}")


if __name__ == '__main__':
    main()


