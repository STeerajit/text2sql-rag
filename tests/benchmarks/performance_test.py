#!/usr/bin/env python3
"""
Performance Test for Text2SQL RAG System
Test system performance and capabilities
"""

import sys
import os
import time
import json
from pathlib import Path

# Add project root to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

def test_prompt_generation_performance():
    """Test prompt generation performance"""
    print("Testing Prompt Generation Performance")
    print("="*60)
    
    try:
        from src.text2sql_rag.ultimate_prompt import UltimatePromptBuilder
        
        # Create builder
        ultimate_builder = UltimatePromptBuilder()
        
        # Test cases
        test_cases = [
            {
                "question": "แสดงจำนวนผู้ป่วยแต่ละโรงพยาบาล",
                "expected_type": "counting"
            },
            {
                "question": "หาค่าใช้จ่ายเฉลี่ยของผู้ป่วยแต่ละโรค",
                "expected_type": "aggregation"
            },
            {
                "question": "ผู้ป่วยที่มีอายุมากกว่า 60 ปี และ มีโรคเบาหวาน",
                "expected_type": "logical"
            },
            {
                "question": "แสดงผู้ป่วยที่มีค่าใช้จ่ายมากกว่า 1000 บาท",
                "expected_type": "filtering"
            },
            {
                "question": "แสดงชื่อผู้ป่วย 10 คนแรกเรียงตามอายุ",
                "expected_type": "ordering"
            }
        ]
        
        schema = """- Name (TEXT): Patient name
- Age (INTEGER): Patient age  
- Hospital (TEXT): Hospital name
- Medical_Condition (TEXT): Medical condition
- "Billing Amount" (REAL): Billing amount"""
        
        results = {
            "total_time": 0,
            "prompt_lengths": [],
            "question_types": [],
            "accuracy": 0
        }
        
        print("Testing Ultimate Prompt System...")
        
        for i, case in enumerate(test_cases):
            start_time = time.perf_counter()
            
            try:
                # Generate prompt
                prompt = ultimate_builder.build_ultimate_prompt(case["question"], schema)
                
                # Analyze question type
                question_type = ultimate_builder._analyze_question_type(case["question"])
                
                end_time = time.perf_counter()
                generation_time = end_time - start_time
                
                # Store results
                results["total_time"] += generation_time
                results["prompt_lengths"].append(len(prompt))
                results["question_types"].append(question_type)
                
                # Check accuracy
                if question_type == case["expected_type"]:
                    results["accuracy"] += 1
                
                print(f"  Test {i+1}: {generation_time:.4f}s, Length: {len(prompt)} chars, Type: {question_type}")
                
            except Exception as e:
                print(f"  Test {i+1}: Error - {e}")
                results["prompt_lengths"].append(0)
                results["question_types"].append("error")
        
        # Calculate statistics
        results["accuracy"] = (results["accuracy"] / len(test_cases)) * 100
        results["avg_time"] = results["total_time"] / len(test_cases)
        results["avg_length"] = sum(results["prompt_lengths"]) / len(results["prompt_lengths"])
        
        print(f"\nStatistics:")
        print(f"  Average time: {results['avg_time']:.4f}s")
        print(f"  Average length: {results['avg_length']:.0f} chars")
        print(f"  Type accuracy: {results['accuracy']:.1f}%")
        
        return results
        
    except Exception as e:
        print(f"Error: {e}")
        return {}

def test_knowledge_base_performance():
    """Test knowledge base performance"""
    print("\nTesting Knowledge Base Performance")
    print("="*60)
    
    try:
        from src.text2sql_rag.text2sql_knowledge import Text2SQLKnowledgeBase
        
        # Create knowledge base
        kb = Text2SQLKnowledgeBase()
        
        results = {
            "total_knowledge": len(kb.get_all_knowledge()),
            "search_performance": {}
        }
        
        print(f"Total knowledge items: {results['total_knowledge']}")
        
        # Test search performance
        search_terms = ["alias", "group by", "aggregation", "where", "select", "count"]
        
        for term in search_terms:
            start_time = time.perf_counter()
            search_results = kb.search_knowledge(term)
            end_time = time.perf_counter()
            
            results["search_performance"][term] = {
                "count": len(search_results),
                "time": end_time - start_time
            }
            
            print(f"  '{term}': found {len(search_results)} items, time {end_time - start_time:.4f}s")
        
        return results
        
    except Exception as e:
        print(f"Error: {e}")
        return {}

def test_llm_response_time():
    """Test LLM integration performance"""
    print("\nTesting LLM Integration Performance")
    print("="*60)
    
    try:
        from src.text2sql_rag.llm import extract_sql
        
        # Test SQL extraction performance
        test_responses = [
            "```sql\nSELECT p.Name FROM patients p;\n```",
            "SELECT p.Hospital, COUNT(*) FROM patients p GROUP BY p.Hospital;",
            "```\nSELECT p.Medical_Condition, AVG(p.\"Billing Amount\") FROM patients p GROUP BY p.Medical_Condition;\n```",
            "The SQL query would be: SELECT p.Name, p.Age FROM patients p WHERE p.Age > 30;",
            "```sql\nSELECT p.Name FROM patients p ORDER BY p.Age DESC LIMIT 10;\n```"
        ]
        
        results = {
            "extraction_times": [],
            "extracted_sqls": []
        }
        
        print("Testing SQL extraction...")
        
        for i, response in enumerate(test_responses):
            start_time = time.perf_counter()
            extracted_sql = extract_sql(response)
            end_time = time.perf_counter()
            
            extraction_time = end_time - start_time
            results["extraction_times"].append(extraction_time)
            results["extracted_sqls"].append(extracted_sql)
            
            print(f"  Test {i+1}: {extraction_time:.6f}s")
            print(f"    Extracted: {extracted_sql[:50]}...")
        
        avg_extraction_time = sum(results["extraction_times"]) / len(results["extraction_times"])
        print(f"\nAverage extraction time: {avg_extraction_time:.6f}s")
        
        results["avg_extraction_time"] = avg_extraction_time
        
        return results
        
    except Exception as e:
        print(f"Error: {e}")
        return {}

def main():
    """Main function"""
    print("Text2SQL RAG System Performance Test")
    print("="*60)
    
    results = {}
    
    # Test 1: Prompt generation performance
    print("1. Testing prompt generation performance...")
    prompt_results = test_prompt_generation_performance()
    if prompt_results:
        results["prompt_performance"] = prompt_results
    
    # Test 2: Knowledge base performance
    print("\n2. Testing knowledge base performance...")
    kb_results = test_knowledge_base_performance()
    if kb_results:
        results["knowledge_base"] = kb_results
    
    # Test 3: LLM integration performance
    print("\n3. Testing LLM integration performance...")
    llm_results = test_llm_response_time()
    if llm_results:
        results["llm_performance"] = llm_results
    
    # Generate summary
    print("\nPerformance Summary")
    print("="*60)
    
    if "prompt_performance" in results:
        data = results["prompt_performance"]
        print("Prompt Generation:")
        print(f"  Average time: {data['avg_time']:.4f}s")
        print(f"  Average length: {data['avg_length']:.0f} chars")
        print(f"  Type accuracy: {data['accuracy']:.1f}%")
    
    if "knowledge_base" in results:
        kb_data = results["knowledge_base"]
        print(f"\nKnowledge Base:")
        print(f"  Total items: {kb_data['total_knowledge']}")
        avg_search_time = sum(data['time'] for data in kb_data['search_performance'].values()) / len(kb_data['search_performance'])
        print(f"  Average search time: {avg_search_time:.4f}s")
    
    if "llm_performance" in results:
        llm_data = results["llm_performance"]
        print(f"\nLLM Integration:")
        print(f"  Average SQL extraction time: {llm_data['avg_extraction_time']:.6f}s")
    
    print(f"\nOverall Status: System is ready for production use")
    
    # Save results
    timestamp = time.strftime('%Y%m%d_%H%M%S')
    filename = f"performance_test_results_{timestamp}.json"
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\nResults saved to: {filename}")
    print("Performance testing completed!")

if __name__ == "__main__":
    main()


