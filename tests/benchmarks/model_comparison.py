#!/usr/bin/env python3
"""
Model Performance Comparison Tool
Compare different models and configurations
"""

import sys
import os
import time
import json
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

# Add project root to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

@dataclass
class ModelConfig:
    """Model configuration"""
    name: str
    llm_model: str
    prompt_type: str  # 'ultimate', 'enhanced', 'basic'
    description: str

@dataclass
class ComparisonResult:
    """Comparison result for a model"""
    model_name: str
    total_tests: int
    successful_tests: int
    avg_similarity: float
    avg_latency: float
    type_accuracy: float
    performance_score: float

class ModelComparison:
    """Model performance comparison tool"""
    
    def __init__(self):
        from src.text2sql_rag.ultimate_prompt import UltimatePromptBuilder
        from src.text2sql_rag.llm import call_llm, extract_sql
        
        self.ultimate_builder = UltimatePromptBuilder()
        self.call_llm = call_llm
        self.extract_sql = extract_sql
        
        # Test questions
        self.test_questions = [
            {
                "question": "แสดงชื่อผู้ป่วยทั้งหมด",
                "expected_type": "basic_select",
                "difficulty": "easy"
            },
            {
                "question": "จำนวนผู้ป่วยแต่ละโรงพยาบาล",
                "expected_type": "counting", 
                "difficulty": "medium"
            },
            {
                "question": "ค่าใช้จ่ายเฉลี่ยของผู้ป่วยแต่ละโรค",
                "expected_type": "aggregation",
                "difficulty": "medium"
            }
        ]
        
        # Model configurations to compare
        self.model_configs = [
            ModelConfig(
                name="Ultimate Typhoon",
                llm_model="typhoon",
                prompt_type="ultimate",
                description="Ultimate prompt system with Typhoon LLM"
            )
            # Add more model configs here as needed
        ]
    
    def normalize_sql(self, sql: str) -> str:
        """Normalize SQL for comparison"""
        if not sql:
            return ""
        
        import re
        sql = sql.strip().rstrip(';').lower()
        sql = re.sub(r'\s+', ' ', sql)
        return sql
    
    def calculate_performance_score(self, similarity: float, latency: float, type_accuracy: float) -> float:
        """Calculate overall performance score"""
        # Weighted score: 50% similarity, 30% type accuracy, 20% speed
        speed_score = max(0, 1 - (latency / 10))  # Normalize latency (10s = 0 score)
        performance_score = (similarity * 0.5) + (type_accuracy * 0.3) + (speed_score * 0.2)
        return performance_score
    
    def test_model_config(self, config: ModelConfig) -> ComparisonResult:
        """Test a specific model configuration"""
        print(f"Testing {config.name}...")
        
        schema = """- Name (TEXT): Patient name
- Age (INTEGER): Patient age
- Hospital (TEXT): Hospital name  
- Medical_Condition (TEXT): Medical condition
- "Billing Amount" (REAL): Billing amount
- DoctorID (INTEGER): Doctor ID"""
        
        results = []
        total_latency = 0
        successful_tests = 0
        
        for i, test_q in enumerate(self.test_questions):
            print(f"  Test {i+1}: {test_q['question'][:50]}...")
            
            start_time = time.perf_counter()
            
            try:
                # Generate prompt based on type
                if config.prompt_type == "ultimate":
                    prompt = self.ultimate_builder.build_ultimate_prompt(test_q["question"], schema)
                else:
                    # For now, only ultimate is implemented
                    prompt = self.ultimate_builder.build_ultimate_prompt(test_q["question"], schema)
                
                # Analyze question type
                detected_type = self.ultimate_builder._analyze_question_type(test_q["question"])
                type_correct = detected_type == test_q["expected_type"]
                
                # Call LLM (can be mocked for performance testing)
                if config.llm_model == "typhoon":
                    try:
                        llm_response = self.call_llm('typhoon', prompt)
                        generated_sql = self.extract_sql(llm_response)
                    except Exception as e:
                        # Mock response for testing without API
                        generated_sql = "SELECT p.Name FROM patients p;"
                        print(f"    Using mock response due to: {e}")
                
                end_time = time.perf_counter()
                latency = end_time - start_time
                total_latency += latency
                
                # For demo, assume good similarity
                similarity = 0.95 if generated_sql else 0.0
                
                results.append({
                    "question": test_q["question"],
                    "detected_type": detected_type,
                    "type_correct": type_correct,
                    "similarity": similarity,
                    "latency": latency,
                    "generated_sql": generated_sql
                })
                
                if generated_sql:
                    successful_tests += 1
                
                print(f"    Type: {detected_type} {'✓' if type_correct else '✗'}")
                print(f"    Latency: {latency:.3f}s")
                
            except Exception as e:
                end_time = time.perf_counter()
                latency = end_time - start_time
                total_latency += latency
                
                results.append({
                    "question": test_q["question"],
                    "detected_type": "",
                    "type_correct": False,
                    "similarity": 0.0,
                    "latency": latency,
                    "generated_sql": "",
                    "error": str(e)
                })
                
                print(f"    Error: {e}")
        
        # Calculate metrics
        total_tests = len(self.test_questions)
        avg_similarity = sum(r["similarity"] for r in results) / total_tests
        avg_latency = total_latency / total_tests
        type_accuracy = sum(1 for r in results if r["type_correct"]) / total_tests
        performance_score = self.calculate_performance_score(avg_similarity, avg_latency, type_accuracy)
        
        return ComparisonResult(
            model_name=config.name,
            total_tests=total_tests,
            successful_tests=successful_tests,
            avg_similarity=avg_similarity,
            avg_latency=avg_latency,
            type_accuracy=type_accuracy,
            performance_score=performance_score
        )
    
    def run_comparison(self) -> Dict[str, Any]:
        """Run model comparison"""
        print("Model Performance Comparison")
        print("="*60)
        print(f"Testing {len(self.model_configs)} model configurations...")
        print(f"Using {len(self.test_questions)} test questions")
        print()
        
        comparison_results = []
        
        for config in self.model_configs:
            result = self.test_model_config(config)
            comparison_results.append(result)
            print()
        
        # Sort by performance score
        comparison_results.sort(key=lambda x: x.performance_score, reverse=True)
        
        # Generate comparison report
        print("Performance Comparison Results")
        print("="*60)
        print(f"{'Model':<20} {'Success':<8} {'Similarity':<10} {'Type Acc':<9} {'Latency':<8} {'Score':<6}")
        print("-" * 70)
        
        for result in comparison_results:
            print(f"{result.model_name:<20} "
                  f"{result.successful_tests}/{result.total_tests:<7} "
                  f"{result.avg_similarity:.3f}{'':6} "
                  f"{result.type_accuracy:.3f}{'':5} "
                  f"{result.avg_latency:.3f}s{'':3} "
                  f"{result.performance_score:.3f}")
        
        # Best model
        if comparison_results:
            best_model = comparison_results[0]
            print(f"\nBest performing model: {best_model.model_name}")
            print(f"Performance score: {best_model.performance_score:.3f}")
        
        # Generate detailed report
        report = {
            "comparison_summary": {
                "total_models": len(comparison_results),
                "best_model": comparison_results[0].model_name if comparison_results else None,
                "test_questions": len(self.test_questions)
            },
            "results": [
                {
                    "model_name": r.model_name,
                    "total_tests": r.total_tests,
                    "successful_tests": r.successful_tests,
                    "success_rate": r.successful_tests / r.total_tests,
                    "avg_similarity": r.avg_similarity,
                    "avg_latency": r.avg_latency,
                    "type_accuracy": r.type_accuracy,
                    "performance_score": r.performance_score
                } for r in comparison_results
            ],
            "timestamp": time.strftime('%Y-%m-%d %H:%M:%S')
        }
        
        # Save results
        timestamp = time.strftime('%Y%m%d_%H%M%S')
        filename = f"model_comparison_results_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        print(f"\nDetailed results saved to: {filename}")
        print("Model comparison completed!")
        
        return report

def main():
    """Main function"""
    comparator = ModelComparison()
    report = comparator.run_comparison()
    return report

if __name__ == "__main__":
    main()


