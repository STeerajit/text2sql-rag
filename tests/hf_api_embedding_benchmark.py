#!/usr/bin/env python3
"""
HF API Embedding Models Benchmark
Compare 5 embedding models via Hugging Face Inference API with standardized metrics.

Metrics:
- Initialization time
- Avg embedding time (per text)
- Embedding dimension
- Retrieval quality (within vs cross-category cosine similarity)
- Total score (0-10)

Exports: results/hf_api_embedding_benchmark_YYYYMMDD_HHMMSS.{xlsx,json}
Usage:
  1) export HUGGINGFACE_API_KEY=your_token
  2) python tests/hf_api_embedding_benchmark.py
"""

import os
import sys
import time
import json
import math
import pandas as pd
from datetime import datetime
from typing import List, Dict, Any, Tuple
from dataclasses import dataclass
import numpy as np

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from text2sql_rag.embedding import Embedder
try:
    from dotenv import load_dotenv
    # Load from repo root
    load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))
    load_dotenv()  # fallback
except Exception:
    pass

BENCHMARK_MODELS = [
    # 5 API models (commonly available, good quality)
    "intfloat/multilingual-e5-large",  # multilingual large
    "intfloat/e5-large-v2",            # strong general
    "BAAI/bge-base-en-v1.5",           # balanced baseline
    "BAAI/bge-m3",                     # multilingual multi-function encoder
    "mixedbread-ai/mxbai-embed-large-v1",  # high-dim strong quality
]

TEST_TEXTS = [
    # Thai questions
    "แสดงชื่อผู้ป่วยทั้งหมด",
    "จำนวนผู้ป่วยแต่ละโรงพยาบาล",
    "ค่าใช้จ่ายเฉลี่ยของผู้ป่วยแต่ละโรค",
    "ผู้ป่วยที่มีอายุมากกว่า 50 ปี",
    # English questions
    "Show all patient names",
    "Count patients by hospital",
    # SQL queries
    "SELECT name FROM patients",
    "SELECT hospital, COUNT(*) FROM patients GROUP BY hospital",
    # Schema descriptions
    "patients table contains name age hospital medical_condition billing_amount",
]

@dataclass
class ModelResult:
    model_name: str
    init_time: float
    avg_embed_time: float
    dimension: int
    retrieval_quality: float
    total_score: float
    status: str
    error: str = ""

class HFEmbeddingBenchmark:
    def __init__(self, models: List[str]):
        self.models = models
        self.results: List[ModelResult] = []
        self.api_key = os.getenv("HUGGINGFACE_API_KEY") or os.getenv("HUGGINGFACE_API_TOKEN")

    def _check_api_key(self) -> bool:
        if not self.api_key:
            print("HUGGINGFACE_API_KEY not set. Please export it before running.")
            print("Example: export HUGGINGFACE_API_KEY=hf_xxx")
            return False
        return True

    def _connectivity_test(self, model: str) -> Tuple[bool, str]:
        try:
            embedder = Embedder(model)
            # Quick single call with retries
            ok = False
            last_err = ""
            for _ in range(3):
                try:
                    _ = embedder.embed_texts("ping")
                    ok = True
                    break
                except Exception as e:
                    last_err = str(e)
                    time.sleep(0.5)
            if not ok:
                raise RuntimeError(last_err)
            return True, "ok"
        except Exception as e:
            return False, str(e)

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

    def _retrieval_quality(self, embedder: Embedder) -> float:
        try:
            # Group by rough categories
            thai = [t for t in TEST_TEXTS if any(c in 'กขคงจฉชซฌญฎฏฐฑฒณดตถทธนบปผฝพฟภมยรลวศษสหฬอฮ' for c in t)]
            english = [t for t in TEST_TEXTS if t[0].isupper() and ' ' in t and not t.startswith('SELECT')]
            sqls = [t for t in TEST_TEXTS if t.startswith('SELECT')]

            if len(thai) < 2 or len(english) < 2 or len(sqls) < 2:
                return 0.5

            thai_emb = embedder.embed_texts(thai[:2])
            eng_emb = embedder.embed_texts(english[:2])
            sql_emb = embedder.embed_texts(sqls[:2])

            within = [
                self._cosine_similarity(thai_emb[0], thai_emb[1]),
                self._cosine_similarity(eng_emb[0], eng_emb[1]),
                self._cosine_similarity(sql_emb[0], sql_emb[1]),
            ]
            cross = [
                self._cosine_similarity(thai_emb[0], sql_emb[0]),
                self._cosine_similarity(eng_emb[0], sql_emb[1]),
            ]
            score = max(0.0, min(1.0, (sum(within) / len(within)) - 0.5 * (sum(cross) / len(cross))))
            return score
        except Exception:
            return 0.5

    def _calc_score(self, init_t: float, avg_t: float, dim: int, quality: float) -> float:
        # Speed (lower is better): map roughly to [0,2]
        init_score = max(0.0, 2.0 - min(2.0, init_t * 0.5))
        speed_score = max(0.0, 2.0 - min(2.0, avg_t * 15))
        # Quality [0,3]
        quality_score = max(0.0, min(3.0, quality * 3.0))
        # Dimension proxy [0,3]
        dim_score = max(0.0, min(3.0, dim / 768.0 * 3.0))
        total = init_score + speed_score + quality_score + dim_score
        return round(min(10.0, total), 3)

    def run(self):
        print("HF API Embedding Models Benchmark")
        print("Comparing 5 models via Hugging Face Inference API")
        print("=" * 70)
        
        if not self._check_api_key():
            return False

        for i, model in enumerate(self.models, 1):
            print(f"[{i}/{len(self.models)}] {model}")
            ok, err = self._connectivity_test(model)
            if not ok:
                print(f"  ❌ Connectivity failed: {err}")
                self.results.append(ModelResult(
                    model_name=model,
                    init_time=math.inf,
                    avg_embed_time=math.inf,
                    dimension=0,
                    retrieval_quality=0.0,
                    total_score=0.0,
                    status="failed",
                    error=err,
                ))
                continue

            try:
                # Initialization time (Embedder creation is light; measure first call instead)
                embedder = Embedder(model)
                t0 = time.time()
                v = embedder.embed_texts(TEST_TEXTS[0])
                init_time = time.time() - t0

                # Embedding times on a few texts (repeat N rounds then average)
                rounds = 3
                per_round_avg = []
                dims = []
                for _ in range(rounds):
                    round_times = []
                    for t in TEST_TEXTS[:5]:
                        t1 = time.time()
                        vec = embedder.embed_texts(t)
                        round_times.append(time.time() - t1)
                        # vec could be [1, D] or [D]
                        arr = np.atleast_2d(vec)
                        dims.append(arr.shape[-1])
                        time.sleep(0.15)
                    per_round_avg.append(np.mean(round_times))
                avg_time = float(np.mean(per_round_avg)) if per_round_avg else 0.0
                dimension = int(max(dims)) if dims else 0

                # Retrieval quality
                quality = float(self._retrieval_quality(embedder))

                # Total score
                score = self._calc_score(init_time, avg_time, dimension, quality)

                self.results.append(ModelResult(
                    model_name=model,
                    init_time=init_time,
                    avg_embed_time=avg_time,
                    dimension=dimension,
                    retrieval_quality=quality,
                    total_score=score,
                    status="success",
                ))
                print(f"  ✓ init {init_time:.3f}s | avg {avg_time:.3f}s | dim {dimension} | quality {quality:.3f} | score {score}")
            except Exception as e:
                err = str(e)
                self.results.append(ModelResult(
                    model_name=model,
                    init_time=math.inf,
                    avg_embed_time=math.inf,
                    dimension=0,
                    retrieval_quality=0.0,
                    total_score=0.0,
                    status="failed",
                    error=err,
                ))
                print(f"  ❌ Error: {err}")

        return True

    def export(self) -> Tuple[str, str]:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        os.makedirs("results", exist_ok=True)
        excel_path = f"results/hf_api_embedding_benchmark_{timestamp}.xlsx"
        json_path = f"results/hf_api_embedding_benchmark_{timestamp}.json"

        rows = [{
            "Model": r.model_name,
            "Status": r.status,
            "Init Time (s)": float(r.init_time) if math.isfinite(r.init_time) else None,
            "Avg Embedding Time (s)": float(r.avg_embed_time) if math.isfinite(r.avg_embed_time) else None,
            "Dimension": int(r.dimension),
            "Retrieval Quality": float(r.retrieval_quality),
            "Total Score": float(r.total_score),
            "Error": r.error,
        } for r in self.results]

        df = pd.DataFrame(rows)
        with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Results', index=False)
            if not df.empty:
                # Summary sheet
                success_df = df[df['Status'] == 'success']
                if not success_df.empty:
                    summary = {
                        'Best Score Model': [success_df.loc[success_df['Total Score'].idxmax(), 'Model']],
                        'Best Score': [success_df['Total Score'].max()],
                        'Fastest Model': [success_df.loc[success_df['Avg Embedding Time (s)'].idxmin(), 'Model']],
                        'Fastest Time (s)': [success_df['Avg Embedding Time (s)'].min()],
                        'Highest Dim Model': [success_df.loc[success_df['Dimension'].idxmax(), 'Model']],
                        'Highest Dim': [success_df['Dimension'].max()],
                    }
                    pd.DataFrame(summary).to_excel(writer, sheet_name='Summary', index=False)

                    # Weighted views
                    # Speed-heavy: 50% speed, 30% quality, 20% dim
                    speed_score = (
                        (1.0 / (1.0 + success_df['Avg Embedding Time (s)'])) * 0.5 +
                        (success_df['Retrieval Quality']) * 0.3 +
                        (success_df['Dimension'] / success_df['Dimension'].max()) * 0.2
                    )
                    # Quality-heavy: 60% quality, 20% speed, 20% dim
                    quality_score = (
                        (success_df['Retrieval Quality']) * 0.6 +
                        (1.0 / (1.0 + success_df['Avg Embedding Time (s)'])) * 0.2 +
                        (success_df['Dimension'] / success_df['Dimension'].max()) * 0.2
                    )
                    weighted = pd.DataFrame({
                        'Model': success_df['Model'],
                        'Speed-Heavy Score': speed_score.round(4),
                        'Quality-Heavy Score': quality_score.round(4),
                    }).sort_values(by='Quality-Heavy Score', ascending=False)
                    weighted.to_excel(writer, sheet_name='Weighted Views', index=False)

            # Scoring methodology sheet
            scoring_lines = [
                ["Scoring Methodology (HF API Embedding Benchmark)"],
                [""],
                ["Metrics (per model):"],
                ["- Init Time (s): time of first embedding call after model init (includes warm-up)"],
                ["- Avg Embedding Time (s): mean time over multiple rounds and texts"],
                ["- Dimension: embedding vector size (e.g., 768, 1024)"],
                ["- Retrieval Quality (RQ): within-category cosine similarity minus half of cross-category"],
                ["  • within = mean(sim(Thai1,Thai2), sim(Eng1,Eng2), sim(SQL1,SQL2))"],
                ["  • cross = mean(sim(Thai1,SQL1), sim(Eng1,SQL2))"],
                ["  • RQ = clip(0,1, within - 0.5*cross)"],
                [""],
                ["Total Score (0–10):"],
                ["- init_score = max(0, 2.0 - min(2.0, init_time * 0.5))"],
                ["- speed_score = max(0, 2.0 - min(2.0, avg_time * 15))"],
                ["- quality_score = min(3.0, RQ * 3.0)"],
                ["- dim_score = min(3.0, (dimension / 768.0) * 3.0)"],
                ["- total_score = init_score + speed_score + quality_score + dim_score (capped at 10.0)"],
                [""],
                ["Weighted Views:"],
                ["- Speed-heavy = 0.5*(1/(1+avg_time)) + 0.3*RQ + 0.2*(dim/max_dim)"],
                ["- Quality-heavy = 0.6*RQ + 0.2*(1/(1+avg_time)) + 0.2*(dim/max_dim)"],
                [""],
                ["Notes:"],
                ["- API warm-up may slow the first call; we average multiple rounds to stabilize."],
                ["- RQ here is a proxy metric; for production use Recall@k on real vector store."],
            ]
            pd.DataFrame(scoring_lines, columns=["Description"]).to_excel(writer, sheet_name='Scoring_Method', index=False)

        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'models': self.models,
                'results': rows,
            }, f, ensure_ascii=False, indent=2)

        return excel_path, json_path


def main():
    print("HF API Embedding Models Benchmark")

    bench = HFEmbeddingBenchmark(BENCHMARK_MODELS)
    ok = bench.run()
    if not ok:
        return

    xlsx, jsn = bench.export()
    print("\nExported:")
    print(f"- Excel: {xlsx}")
    print(f"- JSON:  {jsn}")


if __name__ == "__main__":
    main()
