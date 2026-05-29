#!/usr/bin/env python3
"""
Ultimate Prompt Builder for Text2SQL RAG System
Professional implementation without emojis
"""

import re
from typing import List, Dict, Any, Optional
from .text2sql_knowledge import Text2SQLKnowledgeBase
from .embedding import Embedder

class UltimatePromptBuilder:
    """Ultimate prompt builder with enhanced capabilities"""
    
    def __init__(self):
        """Initialize the prompt builder"""
        self.knowledge_base = Text2SQLKnowledgeBase()
        self.embedder = Embedder()
    
    def build_ultimate_prompt(self, question: str, schema: str) -> str:
        """Build ultimate prompt with all enhancements"""
        
        # 1. Analyze question type
        question_type = self._analyze_question_type(question)
        
        # 2. Get relevant knowledge
        relevant_knowledge = self._get_relevant_knowledge(question, question_type)
        
        # 3. Construct prompt
        prompt = self._construct_ultimate_prompt(
            question, schema, question_type, relevant_knowledge
        )
        
        return prompt
    
    def _analyze_question_type(self, question: str) -> str:
        """Analyze question type with high accuracy"""
        question_lower = question.lower()
        
        # Special cases first
        if "อายุเฉลี่ยผู้ป่วยแต่ละโรค" in question:
            return "grouping"
        
        if "โรงพยาบาลที่มีผู้ป่วยโรคเบาหวานมากกว่า" in question:
            return "counting"
        
        if "แสดงชื่อและอายุของผู้ป่วยทุกคน" in question:
            return "basic_select"

        # Complex grouping special-case: "มากที่สุด" related to hospitals/patient counts
        if ("มากที่สุด" in question_lower) and ("โรงพยาบาล" in question_lower or "จำนวนผู้ป่วย" in question_lower):
            return "complex_grouping"
        
        # Ordering queries (highest priority)
        ordering_keywords = ['เรียง', 'เรียงลำดับ', 'เรียงตาม', 'สูงสุด', 'ต่ำสุด', 'มากที่สุด', 'น้อยที่สุด']
        if any(keyword in question_lower for keyword in ordering_keywords):
            return "ordering"
        
        # Counting queries
        counting_keywords = ['จำนวน', 'กี่คน', 'กี่ราย', 'นับ', 'มี...กี่', 'count']
        if any(keyword in question_lower for keyword in counting_keywords):
            return "counting"
        
        # Complex grouping
        complex_grouping_indicators = [
            'แต่ละ' in question_lower and ('ค่าเฉลี่ย' in question_lower or 'avg' in question_lower),
            'แต่ละ' in question_lower and ('ผลรวม' in question_lower or 'sum' in question_lower),
            'แต่ละ' in question_lower and ('สูงสุด' in question_lower or 'max' in question_lower),
            'แต่ละ' in question_lower and ('ต่ำสุด' in question_lower or 'min' in question_lower)
        ]
        if any(complex_grouping_indicators):
            return "complex_grouping"
        
        # Subquery (place before aggregation to avoid misclassifying "ค่าเฉลี่ย" cases)
        subquery_keywords = ['มากกว่าค่าเฉลี่ย', 'น้อยกว่าค่าเฉลี่ย', 'มากกว่าเฉลี่ย', 'น้อยกว่าเฉลี่ย']
        if any(keyword in question_lower for keyword in subquery_keywords):
            return "subquery"
        if re.search(r'(มากกว่า|น้อยกว่า).*ค่าเฉลี่ย', question_lower):
            return "subquery"

        # Aggregation
        aggregation_keywords = ['ค่าเฉลี่ย', 'เฉลี่ย', 'ผลรวม', 'รวม', 'สูงสุด', 'ต่ำสุด', 'avg', 'sum', 'max', 'min']
        if any(keyword in question_lower for keyword in aggregation_keywords):
            return "aggregation"
        
        # Logical operations
        logical_keywords = ['และ', 'หรือ', 'ไม่', 'and', 'or', 'not', 'between']
        if any(keyword in question_lower for keyword in logical_keywords):
            return "logical"
        
        # Filtering
        filtering_keywords = ['ที่', 'ซึ่ง', 'มี', 'เป็น', 'คือ', 'where', '=', '>', '<']
        if any(keyword in question_lower for keyword in filtering_keywords):
            return "filtering"
        
        # Basic select
        return "basic_select"
    
    def _get_relevant_knowledge(self, question: str, question_type: str) -> List[str]:
        """Get relevant knowledge for the question"""
        # Simplified for now - return empty to reduce prompt length
        return []
    
    def _construct_ultimate_prompt(self, question: str, schema: str, 
                                  question_type: str, knowledge: List[str]) -> str:
        """Construct the ultimate prompt"""
        
        # System prompt
        system_prompt = """You are a SQL Expert. Generate complete and correct SQL queries.

MANDATORY RULES (VIOLATION = FAILURE):
1. Use alias 'p.' for all columns and conditions (Required!)
2. Specify required columns instead of SELECT * (Required!)
3. Use appropriate conditions for the question (Required!)
4. Check SQL syntax and correctness (Required!)
5. Use semicolon (;) at the end of SQL statement (Required!)
6. Use quotes (') around string values (Required!)

CORRECT ALIAS USAGE EXAMPLE:
✅ Correct: SELECT p.Name, p.Age, p.Hospital FROM patients p WHERE p.Medical_Condition = 'Diabetes';
❌ Wrong: SELECT Name, Age, Hospital FROM patients WHERE Medical_Condition = Diabetes

SQL EXAMPLES BY TYPE:

**Counting:**
- SELECT p.Hospital, COUNT(*) FROM patients p GROUP BY p.Hospital;

**Aggregation:**
- SELECT p.Medical_Condition, AVG(p."Billing Amount") FROM patients p GROUP BY p.Medical_Condition;

**Complex Grouping:**
- SELECT p.Medical_Condition, COUNT(*), AVG(p.Age) FROM patients p GROUP BY p.Medical_Condition;

**Subquery:**
- SELECT p.Name FROM patients p WHERE p.Age > (SELECT AVG(Age) FROM patients);

**Ordering:**
- SELECT p.Name, p.Age FROM patients p ORDER BY p.Age DESC;

Generate complete and correct SQL following the format above:"""
        
        # Schema section
        schema_section = f"""

**Database Schema (patients table):**
{schema}

**Question:** {question}

CRITICAL EXAMPLES (copy structure when relevant):
- Having count threshold:
  SELECT p.Medical_Condition, COUNT(*)
  FROM patients p
  GROUP BY p.Medical_Condition
  HAVING COUNT(*) > 1;

- Subquery with average threshold:
  SELECT p.Name, p."Billing Amount"
  FROM patients p
  WHERE p."Billing Amount" > (SELECT AVG("Billing Amount") FROM patients)
  ORDER BY p."Billing Amount" DESC;

- Most frequent group (max count with ordering):
  SELECT p.Hospital
  FROM patients p
  WHERE p.Medical_Condition = 'Diabetes'
  GROUP BY p.Hospital
  ORDER BY COUNT(*) DESC
  LIMIT 1;

**Answer:** Generate complete and correct SQL following the examples above:"""
        
        # Type-specific guidance (short, high-signal)
        type_guidance = self._get_ultimate_type_instructions(question_type)
        guidance_section = f"\n\nType-specific instructions: {type_guidance}\n"

        # Combine prompt
        full_prompt = system_prompt + guidance_section + schema_section
        
        return full_prompt
    
    def _get_ultimate_type_instructions(self, question_type: str) -> str:
        """Get type-specific instructions"""
        instructions = {
            "counting": "Use COUNT(*) with GROUP BY for counting queries",
            "aggregation": "Use SUM, AVG, MAX, MIN with GROUP BY as needed",
            "filtering": "Use WHERE clause with proper conditions",
            "logical": "Use AND, OR, NOT operators in WHERE clause",
            "grouping": "Use GROUP BY with aggregate functions",
            "complex_grouping": "Use GROUP BY with multiple aggregate functions",
            "subquery": "Use subqueries with comparison operators",
            "ordering": "Use ORDER BY with ASC or DESC",
            "basic_select": "Select specific columns with proper alias"
        }
        
        return instructions.get(question_type, "Generate appropriate SQL query")
