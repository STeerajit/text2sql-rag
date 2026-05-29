#!/usr/bin/env python3
"""
Text2SQL RAG System - Main Application
Professional Text-to-SQL system using Retrieval-Augmented Generation
"""

import os
import sys
import argparse
import json
from typing import Dict, Any, Optional
from pathlib import Path

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from text2sql_rag.ultimate_prompt import UltimatePromptBuilder
from text2sql_rag.llm import call_llm, extract_sql
from text2sql_rag.embedding import Embedder
from text2sql_rag.text2sql_knowledge import Text2SQLKnowledgeBase

class Text2SQLRAGSystem:
    """Main Text2SQL RAG System"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the system"""
        self.config = config or self._load_default_config()
        
        # Initialize components
        self.prompt_builder = UltimatePromptBuilder()
        self.embedder = Embedder()
        self.knowledge_base = Text2SQLKnowledgeBase()
        
        print("Text2SQL RAG System initialized successfully")
        print(f"LLM Model: {self.config.get('llm_model', 'Typhoon')}")
        print(f"Embedding Model: {self.config.get('embedder_model', 'all-MiniLM-L6-v2')}")
    
    def _load_default_config(self) -> Dict[str, Any]:
        """Load default configuration"""
        return {
            'llm_model': 'typhoon',
            'embedder_model': 'all-MiniLM-L6-v2',
            'max_tokens': 2000,
            'temperature': 0.0,
            'enable_knowledge_retrieval': True,
            'knowledge_top_k': 5
        }
    
    def process_question(self, question: str, schema: str = None) -> Dict[str, Any]:
        """Process question and generate SQL"""
        try:
            print(f"Processing question: {question}")
            
            # 1. Analyze question type
            question_type = self.prompt_builder._analyze_question_type(question)
            print(f"Question type: {question_type}")
            
            # 2. Build prompt
            if schema:
                prompt = self.prompt_builder.build_ultimate_prompt(question, schema)
            else:
                # Use default schema
                default_schema = """- Name (TEXT): Patient name
- Age (INTEGER): Patient age
- Hospital (TEXT): Hospital name
- Medical_Condition (TEXT): Medical condition
- "Billing Amount" (REAL): Billing amount
- DoctorID (INTEGER): Doctor ID"""
                prompt = self.prompt_builder.build_ultimate_prompt(question, default_schema)
            
            print(f"Prompt length: {len(prompt)} characters")
            
            # 3. Call LLM
            print("Calling LLM...")
            llm_response = call_llm('typhoon', prompt)
            
            # 4. Extract SQL
            generated_sql = extract_sql(llm_response)
            
            # 5. Post-process SQL
            final_sql = self._post_process_sql(generated_sql, question, question_type)
            
            # 6. Create result
            result = {
                'question': question,
                'question_type': question_type,
                'generated_sql': final_sql,
                'llm_response': llm_response,
                'prompt_length': len(prompt),
                'status': 'success'
            }
            
            print(f"SQL generated successfully: {final_sql}")
            return result
            
        except Exception as e:
            print(f"Error: {e}")
            return {
                'question': question,
                'status': 'error',
                'error': str(e)
            }
    
    def _post_process_sql(self, sql: str, question: str, question_type: str) -> str:
        """Post-process generated SQL"""
        if not sql:
            return sql
        
        # Add semicolon if missing
        if not sql.strip().endswith(';'):
            sql = sql.strip() + ';'
        
        # Add alias if missing
        if 'patients' in sql.lower() and 'p.' not in sql:
            sql = self._add_alias_to_sql(sql)
        
        # Fix string quotes
        sql = self._fix_string_quotes(sql)
        
        return sql
    
    def _add_alias_to_sql(self, sql: str) -> str:
        """Add alias to SQL"""
        import re
        
        replacements = {
            'Name': 'p.Name',
            'Age': 'p.Age',
            'Hospital': 'p.Hospital',
            'Medical_Condition': 'p.Medical_Condition',
            '"Billing Amount"': 'p."Billing Amount"',
            'DoctorID': 'p.DoctorID'
        }
        
        for old, new in replacements.items():
            if old in sql:
                sql = re.sub(rf'\b{re.escape(old)}\b', new, sql)
        
        return sql
    
    def _fix_string_quotes(self, sql: str) -> str:
        """Fix string quotes in SQL"""
        import re
        
        string_values = ['Diabetes', 'Hypertension', 'Asthma']
        
        for value in string_values:
            pattern = rf'(?<==)\s*{re.escape(value)}(?=\s|;|$)'
            replacement = f" '{value}'"
            sql = re.sub(pattern, replacement, sql, flags=re.IGNORECASE)
        
        return sql
    
    def batch_process(self, questions: list, schema: str = None) -> list:
        """Process multiple questions"""
        results = []
        
        print(f"Starting batch processing of {len(questions)} questions...")
        
        for i, question in enumerate(questions, 1):
            print(f"\nQuestion {i}/{len(questions)}")
            result = self.process_question(question, schema)
            results.append(result)
        
        print(f"\nCompleted processing {len(results)} questions")
        return results
    
    def save_results(self, results: list, filename: str = None):
        """Save results to file"""
        if not filename:
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"text2sql_results_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        print(f"Results saved to: {filename}")

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='Text2SQL RAG System')
    parser.add_argument('--question', '-q', help='Question to convert to SQL')
    parser.add_argument('--schema', '-s', help='Database schema')
    parser.add_argument('--file', '-f', help='File with multiple questions (JSON)')
    parser.add_argument('--output', '-o', help='Output file')
    parser.add_argument('--interactive', '-i', action='store_true', help='Interactive mode')
    
    args = parser.parse_args()
    
    # Initialize system
    system = Text2SQLRAGSystem()
    
    if args.interactive:
        # Interactive mode
        print("\nInteractive Mode - Type 'quit' to exit")
        print("="*50)
        
        while True:
            try:
                question = input("\nQuestion: ").strip()
                
                if question.lower() in ['quit', 'exit']:
                    print("Exiting system")
                    break
                
                if not question:
                    continue
                
                # Process question
                result = system.process_question(question, args.schema)
                
                if result['status'] == 'success':
                    print(f"\nResult:")
                    print(f"   Type: {result['question_type']}")
                    print(f"   SQL: {result['generated_sql']}")
                else:
                    print(f"Error occurred: {result.get('error', 'Unknown error')}")
                    
            except KeyboardInterrupt:
                print("\nExiting system")
                break
            except Exception as e:
                print(f"Error: {e}")
    
    elif args.question:
        # Single question
        result = system.process_question(args.question, args.schema)
        
        if result['status'] == 'success':
            print(f"\nResult:")
            print(f"   Question: {result['question']}")
            print(f"   Type: {result['question_type']}")
            print(f"   SQL: {result['generated_sql']}")
        else:
            print(f"Error occurred: {result.get('error', 'Unknown error')}")
    
    elif args.file:
        # Batch processing
        try:
            with open(args.file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if isinstance(data, list):
                questions = data
            elif isinstance(data, dict) and 'questions' in data:
                questions = data['questions']
            else:
                print("Invalid file format")
                return
            
            results = system.batch_process(questions, args.schema)
            system.save_results(results, args.output)
            
        except Exception as e:
            print(f"Error reading file: {e}")
    
    else:
        # Show help
        parser.print_help()
        print("\nUsage examples:")
        print("  python main.py -q 'Show patient count by hospital'")
        print("  python main.py -i  # Interactive mode")
        print("  python main.py -f questions.json -o results.json")

if __name__ == "__main__":
    main()
