#!/usr/bin/env python3
"""
Text2SQL Knowledge Base
Professional implementation for storing and retrieving SQL knowledge
"""

from typing import List, Dict, Any

class Text2SQLKnowledgeBase:
    """Knowledge base for Text2SQL operations"""
    
    def __init__(self):
        """Initialize the knowledge base"""
        self.knowledge = self._initialize_knowledge()
    
    def _initialize_knowledge(self) -> List[str]:
        """Initialize the knowledge base with SQL concepts"""
        knowledge = []
        
        # Basic SQL knowledge
        knowledge.extend([
            "Text-to-SQL converts natural language questions to SQL queries",
            "SELECT statement structure: SELECT columns FROM table WHERE conditions",
            "Always use table aliases for better readability",
            "Use semicolon at the end of SQL statements",
            "Use single quotes for string values in SQL"
        ])
        
        # Column and table knowledge
        knowledge.extend([
            "Use alias 'p.' for patients table columns",
            "patients table contains: Name, Age, Hospital, Medical_Condition, Billing Amount, DoctorID",
            "Medical_Condition stores disease information",
            "Hospital stores hospital names",
            "Billing Amount should be quoted due to space in name"
        ])
        
        # Aggregation knowledge
        knowledge.extend([
            "COUNT(*) counts all rows in a group",
            "AVG() calculates average values",
            "SUM() calculates total values", 
            "MAX() finds maximum values",
            "MIN() finds minimum values",
            "GROUP BY groups rows with same values"
        ])
        
        # Filtering knowledge
        knowledge.extend([
            "WHERE clause filters rows based on conditions",
            "Use = for exact matches",
            "Use > and < for numerical comparisons",
            "Use LIKE for pattern matching",
            "Combine conditions with AND, OR, NOT"
        ])
        
        # Ordering knowledge
        knowledge.extend([
            "ORDER BY sorts query results",
            "ASC sorts in ascending order (default)",
            "DESC sorts in descending order",
            "Can order by multiple columns"
        ])
        
        return knowledge
    
    def get_all_knowledge(self) -> List[str]:
        """Get all knowledge statements"""
        return self.knowledge
    
    def search_knowledge(self, query: str, top_k: int = 5) -> List[str]:
        """Search for relevant knowledge"""
        # Simple keyword-based search
        query_lower = query.lower()
        relevant = []
        
        for knowledge_item in self.knowledge:
            if any(word in knowledge_item.lower() for word in query_lower.split()):
                relevant.append(knowledge_item)
        
        return relevant[:top_k]
    
    def get_knowledge_by_type(self, knowledge_type: str) -> List[str]:
        """Get knowledge by type"""
        type_keywords = {
            "basic": ["SELECT", "FROM", "WHERE"],
            "aggregation": ["COUNT", "AVG", "SUM", "MAX", "MIN", "GROUP BY"],
            "filtering": ["WHERE", "conditions", "=", ">", "<"],
            "ordering": ["ORDER BY", "ASC", "DESC", "sort"],
            "tables": ["patients", "table", "column", "alias"]
        }
        
        keywords = type_keywords.get(knowledge_type.lower(), [])
        if not keywords:
            return []
        
        relevant = []
        for knowledge_item in self.knowledge:
            if any(keyword.lower() in knowledge_item.lower() for keyword in keywords):
                relevant.append(knowledge_item)
        
        return relevant