<div align="center">

# Thai Text-to-SQL with RAG and LoRA

**Undergraduate Thesis — B.Eng. Computer Engineering, CDTI**

*Presented at ECTI National Conference 2025*

[![Python](https://img.shields.io/badge/Python-3.x-3776AB?style=flat&logo=python&logoColor=white)](https://python.org)
[![HuggingFace](https://img.shields.io/badge/HuggingFace-Transformers-FFD21E?style=flat&logo=huggingface&logoColor=black)](https://huggingface.co)
[![LangChain](https://img.shields.io/badge/LangChain-RAG-1C3C3C?style=flat)](https://langchain.com)
[![License](https://img.shields.io/badge/License-MIT-green?style=flat)](LICENSE)

</div>

---

## Overview

A Thai-language Text-to-SQL system that allows non-technical users to query databases using natural language. The system combines **Retrieval-Augmented Generation (RAG)** for schema-aware context retrieval and **LoRA fine-tuning** to adapt LLMs for domain-specific SQL generation.

**Problem:** Non-technical users cannot access complex databases without SQL knowledge.  
**Solution:** RAG pipeline + LoRA fine-tuned LLMs to bridge Thai natural language and SQL.

---

## Results

### Best Configuration: E5-base-v2 + Typhoon v2.1 12B + LoRA

| Metric | Before Fine-tuning | After LoRA Fine-tuning |
|--------|:-----------------:|:---------------------:|
| Exact Match (EM) | 0.76 | **0.80** ↑ |
| Structural Match (SMT) | 0.79 | **0.82** ↑ |
| Abstract Syntax Tree (AST) | 0.78 | **0.81** ↑ |
| Execution Accuracy (EA) | 0.80 | **0.84** ↑ |
| F1 Score | 0.79 | **0.82** ↑ |

### Retrieval Performance (E5-base-v2, k=10)

| Recall@10 | MRR@10 | nDCG@10 |
|:---------:|:------:|:-------:|
| **0.89** | **0.69** | **0.86** |

---

## System Architecture

```
Thai Question → Embedding Model → Vector Similarity Search
                                         ↓
                              Schema Linking + SQL Examples
                                         ↓
                              RAG Prompt + LLM → SQL Query
```

**3-stage pipeline:**
1. **Input** — User inputs Thai natural language question
2. **Retrieval** — Embed question → Cosine similarity search → Schema linking + top-k SQL examples
3. **Generation** — Augmented prompt sent to LLM for SQL generation

---

## Models Evaluated

**Embedding Models:** E5-base-v2 · All-MiniLM-L6-v2 · BGE-base-en-v1.5

**LLMs:** Typhoon v2.1 12B Instruct · OpenThaiGPT 14B 1.5 Instruct · Qwen3-VL-8B-Instruct

---

## Dataset

- **Database:** Northwind Sample Database
- **RAG evaluation:** 300 samples (Easy / Medium / Hard difficulty)
- **RAG + LoRA evaluation:** 100 samples
- **Difficulty levels:** Simple SELECT → Multi-JOIN → CTE (Common Table Expression)

---

## Installation

```bash
git clone https://github.com/STeerajit/text2sql-rag.git
cd text2sql-rag
pip install -r requirements.txt
cp .env.example .env  # Add your API keys
make setup-data
```

## Usage

```bash
# Single question
python main.py -q "รายชื่อนักเรียนที่สมัครเรียนปีการศึกษา 2569"

# Interactive mode
python main.py -i

# Batch processing
python main.py -f questions.json -o results.json
```

## Evaluation

```bash
make eval        # Full evaluation
make eval-simple # Quick evaluation
```

---

## Authors

**ธีรชิต โกมลภิส** · ปัณณวัฒน์ นนทิวัฒน์วณิช · ธีระเดช มานุ · ธนกร รักคำ · วรัญญู วงษ์เสรี

B.Eng. Computer Engineering, Faculty of Digital Technology, CDTI

---

<div align="center">

*If this project helped you, please consider giving it a ⭐*

</div>
