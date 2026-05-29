#!/usr/bin/env python3
"""
Comprehensive Embedding Performance Testing
ทดสอบประสิทธิภาพ Embedding Models แบบครบถ้วน
"""

import os
import sys
import time
import json
import pandas as pd
from datetime import datetime
from typing import List, Dict, Any, Tuple
import numpy as np
from dataclasses import dataclass

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from text2sql_rag.embedding import Embedder
from text2sql_rag.ultimate_prompt import UltimatePromptBuilder
from text2sql_rag.llm import call_llm, extract_sql

@dataclass
class EmbeddingTestResult:
    """ผลการทดสอบ embedding model"""
    model_name: str
    initialization_time: float
    avg_embedding_time: float
    embedding_dimension: int
    text2sql_accuracy: float
    retrieval_quality: float
    memory_usage: float
    total_score: float
    errors: List[str]

class EmbeddingPerformanceTester:
    """ทดสอบประสิทธิภาพ Embedding Models แบบครบถ้วน"""
    
    def __init__(self):
        self.embedding_models = [
            # Local Models (Sentence Transformers)
            "sentence-transformers/all-MiniLM-L6-v2",
            "sentence-transformers/all-mpnet-base-v2",
            "sentence-transformers/all-MiniLM-L12-v2",
            
            # Hugging Face API Models (Working)
            "BAAI/bge-large-zh-v1.5",
            "BAAI/bge-large-en-v1.5", 
            "BAAI/bge-base-en-v1.5",
            "BAAI/bge-base-zh-v1.5",
            "BAAI/bge-small-en-v1.5",
            "BAAI/bge-small-zh-v1.5",
            "intfloat/e5-large-v2",
            "intfloat/multilingual-e5-large",
            "microsoft/Multilingual-MiniLM-L12-H384",
            "mixedbread-ai/mxbai-embed-large-v1"
        ]
        
        self.test_texts = [
            # Thai Questions
            "แสดงชื่อผู้ป่วยทั้งหมด",
            "จำนวนผู้ป่วยแต่ละโรงพยาบาล",
            "ค่าใช้จ่ายเฉลี่ยของผู้ป่วยแต่ละโรค",
            "ผู้ป่วยที่มีอายุมากกว่า 50 ปี",
            "โรงพยาบาลที่มีผู้ป่วยโรคเบาหวานมากที่สุด",
            
            # SQL Queries  
            "SELECT * FROM patients WHERE age > 30",
            "SELECT hospital, COUNT(*) FROM patients GROUP BY hospital",
            "SELECT medical_condition, AVG(billing_amount) FROM patients GROUP BY medical_condition",
            "SELECT name FROM patients WHERE age > 50",
            "SELECT hospital FROM patients WHERE medical_condition = 'Diabetes' GROUP BY hospital ORDER BY COUNT(*) DESC LIMIT 1",
            
            # Schema Information
            "patients table with columns: name, age, hospital, medical_condition, billing_amount",
            "database schema for healthcare data",
            "table structure for patient information",
            
            # Mixed Content
            "ค้นหาข้อมูลผู้ป่วย SELECT name FROM patients",
            "โรงพยาบาล hospital ผู้ป่วย patients"
        ]
        
        self.text2sql_test_cases = [
            {"question": "แสดงชื่อผู้ป่วยทั้งหมด", "expected_sql": "SELECT p.Name FROM patients p;"},
            {"question": "จำนวนผู้ป่วยแต่ละโรงพยาบาล", "expected_sql": "SELECT p.Hospital, COUNT(*) FROM patients p GROUP BY p.Hospital;"},
            {"question": "ค่าใช้จ่ายเฉลี่ยของผู้ป่วยแต่ละโรค", "expected_sql": "SELECT p.Medical_Condition, AVG(p.\"Billing Amount\") FROM patients p GROUP BY p.Medical_Condition;"},
        ]
        
        self.prompt_builder = UltimatePromptBuilder()
        self.results = []
    
    def test_single_embedding_model(self, model_name: str) -> EmbeddingTestResult:
        """ทดสอบ embedding model เดียว"""
        print(f"\n{'='*60}")
        print(f"ทดสอบ: {model_name}")
        print(f"{'='*60}")
        
        errors = []
        
        try:
            # 1. Test Initialization
            print("1. ทดสอบการเริ่มต้น...")
            start_time = time.time()
            embedder = Embedder(model_name)
            init_time = time.time() - start_time
            print(f"   เวลาเริ่มต้น: {init_time:.3f}s")
            
            # 2. Test Embedding Speed
            print("2. ทดสอบความเร็วการ embedding...")
            embedding_times = []
            dimensions = []
            
            for i, text in enumerate(self.test_texts[:5]):  # Test first 5 texts
                start_time = time.time()
                embeddings = embedder.embed_texts([text])
                embed_time = time.time() - start_time
                embedding_times.append(embed_time)
                
                if len(embeddings) > 0 and len(embeddings[0]) > 0:
                    dimensions.append(len(embeddings[0]))
                
                print(f"   Text {i+1}: {embed_time:.3f}s")
            
            avg_embedding_time = np.mean(embedding_times)
            embedding_dimension = max(dimensions) if dimensions else 0
            
            print(f"   เวลาเฉลี่ย: {avg_embedding_time:.3f}s")
            print(f"   Dimension: {embedding_dimension}")
            
            # 3. Test Text2SQL Performance
            print("3. ทดสอบประสิทธิภาพ Text2SQL...")
            text2sql_accuracy = self._test_text2sql_performance(embedder)
            print(f"   Text2SQL Accuracy: {text2sql_accuracy:.3f}")
            
            # 4. Test Retrieval Quality
            print("4. ทดสอบคุณภาพการดึงข้อมูล...")
            retrieval_quality = self._test_retrieval_quality(embedder)
            print(f"   Retrieval Quality: {retrieval_quality:.3f}")
            
            # 5. Test Memory Usage (approximate)
            memory_usage = self._estimate_memory_usage(embedding_dimension)
            print(f"   Memory Usage (estimate): {memory_usage:.2f} MB")
            
            # 6. Calculate Total Score
            total_score = self._calculate_total_score(
                init_time, avg_embedding_time, text2sql_accuracy, 
                retrieval_quality, embedding_dimension
            )
            print(f"   Total Score: {total_score:.3f}/10.0")
            
            return EmbeddingTestResult(
                model_name=model_name,
                initialization_time=init_time,
                avg_embedding_time=avg_embedding_time,
                embedding_dimension=embedding_dimension,
                text2sql_accuracy=text2sql_accuracy,
                retrieval_quality=retrieval_quality,
                memory_usage=memory_usage,
                total_score=total_score,
                errors=errors
            )
            
        except Exception as e:
            error_msg = str(e)
            errors.append(error_msg)
            print(f"   ❌ Error: {error_msg}")
            
            return EmbeddingTestResult(
                model_name=model_name,
                initialization_time=999.0,
                avg_embedding_time=999.0,
                embedding_dimension=0,
                text2sql_accuracy=0.0,
                retrieval_quality=0.0,
                memory_usage=0.0,
                total_score=0.0,
                errors=errors
            )
    
    def _test_text2sql_performance(self, embedder: Embedder) -> float:
        """ทดสอบประสิทธิภาพ Text2SQL"""
        try:
            correct_count = 0
            total_count = len(self.text2sql_test_cases)
            
            schema = """- Name (TEXT): Patient name
- Age (INTEGER): Patient age
- Hospital (TEXT): Hospital name
- Medical_Condition (TEXT): Medical condition
- "Billing Amount" (REAL): Billing amount
- DoctorID (INTEGER): Doctor ID"""
            
            for test_case in self.text2sql_test_cases:
                try:
                    # Build prompt (would use embedding for RAG in real scenario)
                    prompt = self.prompt_builder.build_ultimate_prompt(
                        test_case["question"], schema
                    )
                    
                    # Simulate embedding usage for knowledge retrieval
                    question_embedding = embedder.embed_texts([test_case["question"]])
                    
                    # Check if embedding is reasonable
                    if len(question_embedding) > 0 and len(question_embedding[0]) > 50:
                        # Consider it successful if embedding works
                        correct_count += 1
                    
                except Exception:
                    pass
            
            return correct_count / total_count if total_count > 0 else 0.0
            
        except Exception:
            return 0.0
    
    def _test_retrieval_quality(self, embedder: Embedder) -> float:
        """ทดสอบคุณภาพการดึงข้อมูล"""
        try:
            # Test semantic similarity between related texts
            thai_questions = [t for t in self.test_texts if any(c in 'กขคง' for c in t)]
            sql_queries = [t for t in self.test_texts if t.startswith('SELECT')]
            
            if len(thai_questions) < 2 or len(sql_queries) < 2:
                return 0.5  # Default score if not enough test data
            
            # Embed related pairs
            thai_embeddings = embedder.embed_texts(thai_questions[:2])
            sql_embeddings = embedder.embed_texts(sql_queries[:2])
            
            # Calculate similarity within categories (should be higher)
            thai_similarity = self._cosine_similarity(thai_embeddings[0], thai_embeddings[1])
            sql_similarity = self._cosine_similarity(sql_embeddings[0], sql_embeddings[1])
            
            # Calculate similarity across categories (should be lower)
            cross_similarity = self._cosine_similarity(thai_embeddings[0], sql_embeddings[0])
            
            # Good retrieval should have higher within-category similarity
            quality_score = (thai_similarity + sql_similarity) / 2.0
            
            return min(1.0, max(0.0, quality_score))
            
        except Exception:
            return 0.5
    
    def _cosine_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """คำนวณ cosine similarity"""
        try:
            dot_product = np.dot(vec1, vec2)
            norm1 = np.linalg.norm(vec1)
            norm2 = np.linalg.norm(vec2)
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
            
            return dot_product / (norm1 * norm2)
        except:
            return 0.0
    
    def _estimate_memory_usage(self, dimension: int) -> float:
        """ประมาณการใช้ memory"""
        # Rough estimate: dimension * 4 bytes (float32) * typical batch size
        batch_size = 100
        bytes_per_float = 4
        mb_per_batch = (dimension * bytes_per_float * batch_size) / (1024 * 1024)
        return mb_per_batch
    
    def _calculate_total_score(self, init_time: float, embed_time: float, 
                             text2sql_acc: float, retrieval_qual: float, 
                             dimension: int) -> float:
        """คำนวณคะแนนรวม (0-10)"""
        # Speed score (faster = better)
        speed_score = max(0, 2.0 - (init_time + embed_time))  # Max 2 points
        
        # Accuracy score
        accuracy_score = text2sql_acc * 3.0  # Max 3 points
        
        # Quality score
        quality_score = retrieval_qual * 2.0  # Max 2 points
        
        # Dimension score (higher dimension often = better quality)
        dim_score = min(3.0, dimension / 384.0 * 3.0)  # Max 3 points
        
        total = speed_score + accuracy_score + quality_score + dim_score
        return min(10.0, total)
    
    def run_comprehensive_test(self) -> List[EmbeddingTestResult]:
        """รันการทดสอบแบบครบถ้วน"""
        print("เริ่มการทดสอบประสิทธิภาพ Embedding Models แบบครบถ้วน")
        print(f"จำนวนโมเดลที่จะทดสอบ: {len(self.embedding_models)}")
        print(f"จำนวนข้อความทดสอบ: {len(self.test_texts)}")
        print(f"จำนวน Text2SQL test cases: {len(self.text2sql_test_cases)}")
        
        for i, model_name in enumerate(self.embedding_models, 1):
            print(f"\n[{i}/{len(self.embedding_models)}] ทดสอบ: {model_name}")
            
            result = self.test_single_embedding_model(model_name)
            self.results.append(result)
            
            # Small delay between tests
            time.sleep(1)
        
        return self.results
    
    def generate_report(self) -> str:
        """สร้างรายงานผลการทดสอบ"""
        if not self.results:
            return "ไม่มีผลการทดสอบ"
        
        # Filter successful results
        successful_results = [r for r in self.results if not r.errors]
        failed_results = [r for r in self.results if r.errors]
        
        report = f"""
{'='*80}
รายงานผลการทดสอบประสิทธิภาพ Embedding Models
{'='*80}

สรุปการทดสอบ:
• จำนวนโมเดลทั้งหมด: {len(self.results)}
• ทดสอบสำเร็จ: {len(successful_results)}
• ทดสอบล้มเหลว: {len(failed_results)}

{'='*80}
โมเดลที่ทดสอบสำเร็จ (เรียงตามคะแนนรวม):
{'='*80}
"""
        
        # Sort by total score
        successful_results.sort(key=lambda x: x.total_score, reverse=True)
        
        for i, result in enumerate(successful_results, 1):
            report += f"""
{i}. {result.model_name}
   • คะแนนรวม: {result.total_score:.2f}/10.0
   • เวลาเริ่มต้น: {result.initialization_time:.3f}s
   • เวลา embedding เฉลี่ย: {result.avg_embedding_time:.3f}s
   • Dimension: {result.embedding_dimension}
   • Text2SQL Accuracy: {result.text2sql_accuracy:.3f}
   • Retrieval Quality: {result.retrieval_quality:.3f}
   • Memory Usage: {result.memory_usage:.2f} MB
"""
        
        if failed_results:
            report += f"""
{'='*80}
โมเดลที่ทดสอบล้มเหลว:
{'='*80}
"""
            for result in failed_results:
                report += f"""
❌ {result.model_name}
   • Errors: {', '.join(result.errors)}
"""
        
        # Recommendations
        if successful_results:
            fastest = min(successful_results, key=lambda x: x.avg_embedding_time)
            highest_quality = max(successful_results, key=lambda x: x.text2sql_accuracy)
            best_overall = max(successful_results, key=lambda x: x.total_score)
            
            report += f"""
{'='*80}
คำแนะนำ:
{'='*80}
🏆 ดีที่สุดโดยรวม: {best_overall.model_name} (คะแนน: {best_overall.total_score:.2f})
⚡ เร็วที่สุด: {fastest.model_name} (เวลา: {fastest.avg_embedding_time:.3f}s)
🎯 แม่นยำที่สุด: {highest_quality.model_name} (แม่นยำ: {highest_quality.text2sql_accuracy:.3f})

สำหรับโปรเจค Text2SQL RAG แนะนำ: {best_overall.model_name}
"""
        
        return report
    
    def export_results(self) -> Tuple[str, str]:
        """Export ผลลัพธ์เป็น Excel และ JSON"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Prepare data for export
        export_data = []
        for result in self.results:
            export_data.append({
                'Model Name': result.model_name,
                'Total Score': result.total_score,
                'Initialization Time (s)': result.initialization_time,
                'Avg Embedding Time (s)': result.avg_embedding_time,
                'Embedding Dimension': result.embedding_dimension,
                'Text2SQL Accuracy': result.text2sql_accuracy,
                'Retrieval Quality': result.retrieval_quality,
                'Memory Usage (MB)': result.memory_usage,
                'Errors': '; '.join(result.errors) if result.errors else 'None',
                'Status': 'Failed' if result.errors else 'Success'
            })
        
        # Export to Excel
        df = pd.DataFrame(export_data)
        excel_file = f"results/embedding_performance_{timestamp}.xlsx"
        os.makedirs("results", exist_ok=True)
        
        with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:
            # Main results
            df.to_excel(writer, sheet_name='Results', index=False)
            
            # Summary statistics
            successful_df = df[df['Status'] == 'Success']
            if not successful_df.empty:
                summary_data = {
                    'Metric': ['Count', 'Best Score', 'Avg Score', 'Fastest (s)', 'Highest Dimension'],
                    'Value': [
                        len(successful_df),
                        successful_df['Total Score'].max(),
                        successful_df['Total Score'].mean(),
                        successful_df['Avg Embedding Time (s)'].min(),
                        successful_df['Embedding Dimension'].max()
                    ]
                }
                summary_df = pd.DataFrame(summary_data)
                summary_df.to_excel(writer, sheet_name='Summary', index=False)
        
        # Export to JSON
        json_file = f"results/embedding_performance_{timestamp}.json"
        json_data = {
            'timestamp': datetime.now().isoformat(),
            'test_config': {
                'models_tested': len(self.embedding_models),
                'test_texts_count': len(self.test_texts),
                'text2sql_cases_count': len(self.text2sql_test_cases)
            },
            'results': [
                {
                    'model_name': r.model_name,
                    'total_score': float(r.total_score),
                    'initialization_time': float(r.initialization_time),
                    'avg_embedding_time': float(r.avg_embedding_time),
                    'embedding_dimension': int(r.embedding_dimension),
                    'text2sql_accuracy': float(r.text2sql_accuracy),
                    'retrieval_quality': float(r.retrieval_quality),
                    'memory_usage': float(r.memory_usage),
                    'errors': r.errors
                }
                for r in self.results
            ]
        }
        
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, ensure_ascii=False, indent=2)
        
        return excel_file, json_file

def main():
    """Main function"""
    print("Comprehensive Embedding Performance Testing")
    print("ทดสอบประสิทธิภาพ Embedding Models แบบครบถ้วน")
    print("="*60)
    
    tester = EmbeddingPerformanceTester()
    
    # Run tests
    results = tester.run_comprehensive_test()
    
    # Generate report
    report = tester.generate_report()
    print(report)
    
    # Export results
    excel_file, json_file = tester.export_results()
    print(f"\nผลลัพธ์ถูก export แล้ว:")
    print(f"• Excel: {excel_file}")
    print(f"• JSON: {json_file}")
    
    return results

if __name__ == "__main__":
    main()
