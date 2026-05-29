#!/usr/bin/env python3
"""
Local Embedding Models Performance Test
ทดสอบ embedding models ที่ใช้งานได้โดยไม่ต้องใช้ API key
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

@dataclass
class LocalEmbeddingResult:
    """ผลการทดสอบ local embedding model"""
    model_name: str
    initialization_time: float
    avg_embedding_time: float
    embedding_dimension: int
    retrieval_quality: float
    memory_usage: float
    total_score: float
    status: str
    error: str = ""

class LocalEmbeddingTester:
    """ทดสอบ Local Embedding Models"""
    
    def __init__(self):
        # Local models that should work without API keys
        self.local_models = [
            "sentence-transformers/all-MiniLM-L6-v2",
            "sentence-transformers/paraphrase-MiniLM-L6-v2",
            "sentence-transformers/distiluse-base-multilingual-cased",
        ]
        
        # Test texts in multiple languages including Thai
        self.test_texts = [
            # Thai questions
            "แสดงชื่อผู้ป่วยทั้งหมด",
            "จำนวนผู้ป่วยแต่ละโรงพยาบาล", 
            "ค่าใช้จ่ายเฉลี่ยของผู้ป่วยแต่ละโรค",
            "ผู้ป่วยที่มีอายุมากกว่า 50 ปี",
            
            # English questions
            "Show all patient names",
            "Count patients by hospital",
            "Average cost per disease", 
            "Patients older than 50",
            
            # SQL queries
            "SELECT name FROM patients",
            "SELECT hospital, COUNT(*) FROM patients GROUP BY hospital",
            "SELECT medical_condition, AVG(billing_amount) FROM patients GROUP BY medical_condition",
            "SELECT * FROM patients WHERE age > 50",
            
            # Schema descriptions
            "patients table contains name age hospital medical_condition billing_amount",
            "database schema for healthcare patient data"
        ]
        
        self.results = []
    
    def test_single_model(self, model_name: str) -> LocalEmbeddingResult:
        """ทดสอบ model เดียว"""
        print(f"\n{'='*60}")
        print(f"ทดสอบ: {model_name}")
        print(f"{'='*60}")
        
        try:
            # 1. Test initialization
            print("1. ทดสอบการเริ่มต้น...")
            start_time = time.time()
            embedder = Embedder(model_name)
            init_time = time.time() - start_time
            print(f"   เวลาเริ่มต้น: {init_time:.3f}s")
            
            # Check if model was actually loaded
            if embedder.model is None:
                return LocalEmbeddingResult(
                    model_name=model_name,
                    initialization_time=init_time,
                    avg_embedding_time=0.0,
                    embedding_dimension=0,
                    retrieval_quality=0.0,
                    memory_usage=0.0,
                    total_score=0.0,
                    status="failed",
                    error="Model not initialized"
                )
            
            # 2. Test embedding speed and dimension
            print("2. ทดสอบความเร็วและ dimension...")
            embedding_times = []
            dimensions = []
            
            for i, text in enumerate(self.test_texts[:8]):  # Test 8 texts
                start_time = time.time()
                embeddings = embedder.embed_texts([text])
                embed_time = time.time() - start_time
                embedding_times.append(embed_time)
                
                if len(embeddings) > 0 and len(embeddings[0]) > 0:
                    dimensions.append(len(embeddings[0]))
                
                print(f"   Text {i+1}: {embed_time:.3f}s")
            
            if not embedding_times:
                raise Exception("No embeddings generated")
            
            avg_embedding_time = np.mean(embedding_times)
            embedding_dimension = max(dimensions) if dimensions else 0
            
            print(f"   เวลาเฉลี่ย: {avg_embedding_time:.3f}s")
            print(f"   Dimension: {embedding_dimension}")
            
            # 3. Test retrieval quality
            print("3. ทดสอบคุณภาพการดึงข้อมูล...")
            retrieval_quality = self._test_retrieval_quality(embedder)
            print(f"   Retrieval Quality: {retrieval_quality:.3f}")
            
            # 4. Estimate memory usage
            memory_usage = self._estimate_memory_usage(embedding_dimension)
            print(f"   Memory Usage (estimate): {memory_usage:.2f} MB")
            
            # 5. Calculate total score
            total_score = self._calculate_total_score(
                init_time, avg_embedding_time, retrieval_quality, embedding_dimension
            )
            print(f"   Total Score: {total_score:.3f}/10.0")
            
            return LocalEmbeddingResult(
                model_name=model_name,
                initialization_time=init_time,
                avg_embedding_time=avg_embedding_time,
                embedding_dimension=embedding_dimension,
                retrieval_quality=retrieval_quality,
                memory_usage=memory_usage,
                total_score=total_score,
                status="success"
            )
            
        except Exception as e:
            error_msg = str(e)
            print(f"   ❌ Error: {error_msg}")
            
            return LocalEmbeddingResult(
                model_name=model_name,
                initialization_time=999.0,
                avg_embedding_time=999.0,
                embedding_dimension=0,
                retrieval_quality=0.0,
                memory_usage=0.0,
                total_score=0.0,
                status="failed",
                error=error_msg
            )
    
    def _test_retrieval_quality(self, embedder: Embedder) -> float:
        """ทดสอบคุณภาพการดึงข้อมูล"""
        try:
            # Group similar texts
            thai_texts = [t for t in self.test_texts if any(c in 'กขคงจฉชซฌญฎฏฐฑฒณดต' for c in t)]
            english_texts = [t for t in self.test_texts if t.startswith(('Show', 'Count', 'Average', 'Patients'))]
            sql_texts = [t for t in self.test_texts if t.startswith('SELECT')]
            
            if len(thai_texts) < 2 or len(english_texts) < 2 or len(sql_texts) < 2:
                return 0.5  # Default if not enough variety
            
            # Embed different categories
            thai_embeddings = embedder.embed_texts(thai_texts[:2])
            english_embeddings = embedder.embed_texts(english_texts[:2])
            sql_embeddings = embedder.embed_texts(sql_texts[:2])
            
            # Calculate within-category similarities (should be higher)
            thai_sim = self._cosine_similarity(thai_embeddings[0], thai_embeddings[1])
            english_sim = self._cosine_similarity(english_embeddings[0], english_embeddings[1])
            sql_sim = self._cosine_similarity(sql_embeddings[0], sql_embeddings[1])
            
            # Calculate cross-category similarities (should be lower)
            cross_sim1 = self._cosine_similarity(thai_embeddings[0], sql_embeddings[0])
            cross_sim2 = self._cosine_similarity(english_embeddings[0], sql_embeddings[0])
            
            # Good quality = high within-category, lower cross-category
            within_avg = (thai_sim + english_sim + sql_sim) / 3.0
            cross_avg = (cross_sim1 + cross_sim2) / 2.0
            
            # Quality score based on the difference
            quality_score = within_avg - (cross_avg * 0.5)
            
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
            
            similarity = dot_product / (norm1 * norm2)
            return float(similarity)
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
                             retrieval_qual: float, dimension: int) -> float:
        """คำนวณคะแนนรวม (0-10)"""
        # Speed score (faster = better)
        init_score = max(0, 2.0 - min(2.0, init_time * 0.5))  # Max 2 points
        speed_score = max(0, 2.0 - min(2.0, embed_time * 20))  # Max 2 points
        
        # Quality score
        quality_score = retrieval_qual * 3.0  # Max 3 points
        
        # Dimension score (higher dimension often = better quality)
        dim_score = min(3.0, dimension / 384.0 * 3.0)  # Max 3 points
        
        total = init_score + speed_score + quality_score + dim_score
        return min(10.0, total)
    
    def run_all_tests(self) -> List[LocalEmbeddingResult]:
        """รันการทดสอบทั้งหมด"""
        print("Local Embedding Models Performance Test")
        print("ทดสอบประสิทธิภาพ Local Embedding Models")
        print(f"จำนวนโมเดลที่จะทดสอบ: {len(self.local_models)}")
        print(f"จำนวนข้อความทดสอบ: {len(self.test_texts)}")
        
        for i, model_name in enumerate(self.local_models, 1):
            print(f"\n[{i}/{len(self.local_models)}] ทดสอบ: {model_name}")
            
            result = self.test_single_model(model_name)
            self.results.append(result)
            
            # Small delay between tests
            time.sleep(1)
        
        return self.results
    
    def generate_report(self) -> str:
        """สร้างรายงานผลการทดสอบ"""
        if not self.results:
            return "ไม่มีผลการทดสอบ"
        
        successful_results = [r for r in self.results if r.status == "success"]
        failed_results = [r for r in self.results if r.status == "failed"]
        
        report = f"""
{'='*80}
รายงานผลการทดสอบ Local Embedding Models
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
   • Error: {result.error}
"""
        
        # Recommendations
        if successful_results:
            fastest = min(successful_results, key=lambda x: x.avg_embedding_time)
            best_quality = max(successful_results, key=lambda x: x.retrieval_quality)
            best_overall = max(successful_results, key=lambda x: x.total_score)
            
            report += f"""
{'='*80}
คำแนะนำสำหรับ Text2SQL RAG:
{'='*80}
🏆 ดีที่สุดโดยรวม: {best_overall.model_name} (คะแนน: {best_overall.total_score:.2f})
⚡ เร็วที่สุด: {fastest.model_name} (เวลา: {fastest.avg_embedding_time:.3f}s)
🎯 คุณภาพสูงสุด: {best_quality.model_name} (คุณภาพ: {best_quality.retrieval_quality:.3f})

สำหรับการใช้งานจริง แนะนำ: {best_overall.model_name}
เหตุผล: มีประสิทธิภาพโดยรวมสูงสุด และใช้งานได้โดยไม่ต้องใช้ API key
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
                'Total Score': float(result.total_score),
                'Initialization Time (s)': float(result.initialization_time),
                'Avg Embedding Time (s)': float(result.avg_embedding_time),
                'Embedding Dimension': int(result.embedding_dimension),
                'Retrieval Quality': float(result.retrieval_quality),
                'Memory Usage (MB)': float(result.memory_usage),
                'Status': result.status,
                'Error': result.error if result.error else 'None'
            })
        
        # Export to Excel
        df = pd.DataFrame(export_data)
        excel_file = f"results/local_embedding_performance_{timestamp}.xlsx"
        os.makedirs("results", exist_ok=True)
        
        with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:
            # Main results
            df.to_excel(writer, sheet_name='Results', index=False)
            
            # Summary statistics
            successful_df = df[df['Status'] == 'success']
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
        json_file = f"results/local_embedding_performance_{timestamp}.json"
        json_data = {
            'timestamp': datetime.now().isoformat(),
            'test_config': {
                'models_tested': len(self.local_models),
                'test_texts_count': len(self.test_texts),
                'test_type': 'local_models_only'
            },
            'results': [
                {
                    'model_name': r.model_name,
                    'total_score': float(r.total_score),
                    'initialization_time': float(r.initialization_time),
                    'avg_embedding_time': float(r.avg_embedding_time),
                    'embedding_dimension': int(r.embedding_dimension),
                    'retrieval_quality': float(r.retrieval_quality),
                    'memory_usage': float(r.memory_usage),
                    'status': r.status,
                    'error': r.error
                }
                for r in self.results
            ]
        }
        
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, ensure_ascii=False, indent=2)
        
        return excel_file, json_file

def main():
    """Main function"""
    print("Local Embedding Models Performance Test")
    print("ทดสอบ Local Embedding Models (ไม่ต้องใช้ API Key)")
    print("="*60)
    
    tester = LocalEmbeddingTester()
    
    # Run tests
    results = tester.run_all_tests()
    
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


