#!/usr/bin/env python3
"""
Real LLM Evaluation for Text2SQL RAG System
Test with actual LLM API calls
"""

import sys
import os
import time
import json
from typing import List, Dict, Any
from dataclasses import dataclass

# Add project root to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

@dataclass
class TestCase:
    """Test case for real LLM evaluation"""
    id: str
    question: str
    expected_sql: str
    query_type: str
    difficulty: str = "medium"

class RealLLMEvaluator:
    """Evaluator using real LLM API calls"""
    
    def __init__(self):
        from src.text2sql_rag.ultimate_prompt import UltimatePromptBuilder
        from src.text2sql_rag.llm import call_llm, extract_sql
        
        self.ultimate_builder = UltimatePromptBuilder()
        self.call_llm = call_llm
        self.extract_sql = extract_sql
        
        # Test cases for real LLM evaluation
        self.test_cases = [
            TestCase(
                id="R001",
                question="แสดงชื่อผู้ป่วยทั้งหมด",
                expected_sql="SELECT p.Name FROM patients p;",
                query_type="basic_select",
                difficulty="easy"
            ),
            TestCase(
                id="R002", 
                question="จำนวนผู้ป่วยแต่ละโรงพยาบาล",
                expected_sql="SELECT p.Hospital, COUNT(*) FROM patients p GROUP BY p.Hospital;",
                query_type="counting",
                difficulty="medium"
            ),
            TestCase(
                id="R003",
                question="ค่าใช้จ่ายเฉลี่ยของผู้ป่วยแต่ละโรค",
                expected_sql="SELECT p.Medical_Condition, AVG(p.\"Billing Amount\") FROM patients p GROUP BY p.Medical_Condition;",
                query_type="aggregation",
                difficulty="medium"
            )
        ]
    
    def normalize_sql(self, sql: str) -> str:
        """Normalize SQL for comparison"""
        if not sql:
            return ""
        
        import re
        sql = sql.strip().rstrip(';').lower()
        sql = re.sub(r'\s+', ' ', sql)
        return sql
    
    def calculate_similarity(self, generated_sql: str, expected_sql: str) -> float:
        """Calculate SQL similarity"""
        import difflib
        
        gen_normalized = self.normalize_sql(generated_sql)
        exp_normalized = self.normalize_sql(expected_sql)
        
        similarity = difflib.SequenceMatcher(None, gen_normalized, exp_normalized).ratio()
        return similarity
    
    def evaluate_with_real_llm(self, test_case: TestCase) -> Dict[str, Any]:
        """Evaluate test case with real LLM"""
        print(f"Testing {test_case.id}: {test_case.question}")
        
        schema = """- Name (TEXT): Patient name
- Age (INTEGER): Patient age
- Hospital (TEXT): Hospital name  
- Medical_Condition (TEXT): Medical condition
- "Billing Amount" (REAL): Billing amount
- DoctorID (INTEGER): Doctor ID"""
        
        start_time = time.perf_counter()
        
        try:
            # Build prompt
            prompt = self.ultimate_builder.build_ultimate_prompt(test_case.question, schema)
            print(f"  Prompt length: {len(prompt)} characters")
            
            # Analyze question type
            detected_type = self.ultimate_builder._analyze_question_type(test_case.question)
            print(f"  Detected type: {detected_type}")
            
            # Call real LLM
            print("  Calling LLM...")
            llm_response = self.call_llm('typhoon', prompt)
            
            # Extract SQL
            generated_sql = self.extract_sql(llm_response)
            
            end_time = time.perf_counter()
            latency = end_time - start_time
            
            # Calculate metrics
            similarity = self.calculate_similarity(generated_sql, test_case.expected_sql)
            type_correct = detected_type == test_case.query_type
            
            result = {
                "test_id": test_case.id,
                "question": test_case.question,
                "expected_sql": test_case.expected_sql,
                "generated_sql": generated_sql,
                "llm_response": llm_response,
                "query_type": test_case.query_type,
                "detected_type": detected_type,
                "type_correct": type_correct,
                "similarity": similarity,
                "latency": latency,
                "difficulty": test_case.difficulty,
                "prompt_length": len(prompt),
                "status": "success"
            }
            
            print(f"  Generated SQL: {generated_sql}")
            print(f"  Similarity: {similarity:.3f}")
            print(f"  Type correct: {'Yes' if type_correct else 'No'}")
            print(f"  Latency: {latency:.3f}s")
            
            return result
            
        except Exception as e:
            end_time = time.perf_counter()
            latency = end_time - start_time
            
            print(f"  Error: {e}")
            
            result = {
                "test_id": test_case.id,
                "question": test_case.question,
                "expected_sql": test_case.expected_sql,
                "generated_sql": "",
                "llm_response": "",
                "query_type": test_case.query_type,
                "detected_type": "",
                "type_correct": False,
                "similarity": 0.0,
                "latency": latency,
                "difficulty": test_case.difficulty,
                "prompt_length": 0,
                "status": "error",
                "error": str(e)
            }
            
            return result
    
    def run_real_llm_evaluation(self) -> Dict[str, Any]:
        """Run evaluation with real LLM"""
        print("Real LLM Evaluation for Text2SQL RAG System")
        print("="*60)
        print(f"Testing {len(self.test_cases)} cases with actual LLM...")
        print()
        
        results = []
        
        for i, test_case in enumerate(self.test_cases, 1):
            print(f"Test {i}/{len(self.test_cases)}")
            result = self.evaluate_with_real_llm(test_case)
            results.append(result)
            print()
        
        # Calculate overall metrics
        successful_tests = len([r for r in results if r["status"] == "success"])
        total_tests = len(results)
        
        if successful_tests > 0:
            avg_similarity = sum(r["similarity"] for r in results if r["status"] == "success") / successful_tests
            avg_latency = sum(r["latency"] for r in results if r["status"] == "success") / successful_tests
            type_accuracy = sum(1 for r in results if r["type_correct"]) / total_tests
        else:
            avg_similarity = 0.0
            avg_latency = 0.0
            type_accuracy = 0.0
        
        # Generate report
        report = {
            "summary": {
                "total_tests": total_tests,
                "successful_tests": successful_tests,
                "failed_tests": total_tests - successful_tests,
                "success_rate": successful_tests / total_tests if total_tests > 0 else 0,
                "avg_similarity": avg_similarity,
                "avg_latency": avg_latency,
                "type_accuracy": type_accuracy
            },
            "results": results,
            "timestamp": time.strftime('%Y-%m-%d %H:%M:%S')
        }
        
        # Print summary
        print("Real LLM Evaluation Summary")
        print("="*60)
        print(f"Total tests: {total_tests}")
        print(f"Successful tests: {successful_tests}")
        print(f"Success rate: {successful_tests/total_tests:.1%}")
        
        if successful_tests > 0:
            print(f"Average similarity: {avg_similarity:.3f}")
            print(f"Type accuracy: {type_accuracy:.1%}")
            print(f"Average latency: {avg_latency:.3f}s")
        
        # Performance assessment
        if successful_tests == total_tests:
            print("\nPerformance: Excellent - All tests passed")
        elif successful_tests >= total_tests * 0.8:
            print("\nPerformance: Good - Most tests passed")
        elif successful_tests >= total_tests * 0.5:
            print("\nPerformance: Fair - Some issues detected")
        else:
            print("\nPerformance: Poor - Many tests failed")
        
        # Save results
        timestamp = time.strftime('%Y%m%d_%H%M%S')
        filename = f"real_llm_evaluation_results_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        print(f"\nResults saved to: {filename}")
        print("Real LLM evaluation completed!")
        
        return report

def main():
    """Main function"""
    evaluator = RealLLMEvaluator()
    
    print("Warning: This will make actual API calls to LLM service")
    print("Make sure you have valid API keys configured in .env file")
    
    try:
        report = evaluator.run_real_llm_evaluation()
        return report
    except Exception as e:
        print(f"Evaluation failed: {e}")
        print("Please check your API configuration and try again")
        return None

if __name__ == "__main__":
    main()


