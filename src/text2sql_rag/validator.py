#!/usr/bin/env python3
"""
SQL Validator and Error Handler
Professional validation and error handling for SQL generation
"""

import re
import sqlite3
from typing import Tuple, List, Dict, Any, Optional
from dataclasses import dataclass

@dataclass
class ValidationResult:
    """Result of SQL validation"""
    is_valid: bool
    errors: List[str]
    warnings: List[str]
    suggestions: List[str]
    corrected_sql: Optional[str] = None

class SQLValidator:
    """SQL validation and error handling"""
    
    def __init__(self):
        self.required_keywords = ['select', 'from']
        self.optional_keywords = ['where', 'group by', 'order by', 'having', 'limit']
        self.aggregate_functions = ['count', 'sum', 'avg', 'max', 'min']
        
    def validate_sql(self, sql: str, schema_info: Dict[str, List[str]] = None) -> ValidationResult:
        """Comprehensive SQL validation"""
        errors = []
        warnings = []
        suggestions = []
        corrected_sql = None
        
        if not sql or not sql.strip():
            errors.append("Empty SQL query")
            return ValidationResult(False, errors, warnings, suggestions)
        
        sql_clean = sql.strip().rstrip(';')
        
        # 1. Syntax validation
        syntax_errors = self._check_syntax(sql_clean)
        errors.extend(syntax_errors)
        
        # 2. Structure validation
        structure_warnings = self._check_structure(sql_clean)
        warnings.extend(structure_warnings)
        
        # 3. Schema validation (if provided)
        if schema_info:
            schema_errors, schema_suggestions = self._check_schema_compliance(sql_clean, schema_info)
            errors.extend(schema_errors)
            suggestions.extend(schema_suggestions)
        
        # 4. Best practices check
        best_practice_suggestions = self._check_best_practices(sql_clean)
        suggestions.extend(best_practice_suggestions)
        
        # 5. Auto-correction attempt
        if errors:
            corrected_sql = self._attempt_correction(sql_clean, errors)
        
        is_valid = len(errors) == 0
        
        return ValidationResult(is_valid, errors, warnings, suggestions, corrected_sql)
    
    def _check_syntax(self, sql: str) -> List[str]:
        """Check basic SQL syntax"""
        errors = []
        sql_lower = sql.lower()
        
        # Check required keywords
        for keyword in self.required_keywords:
            if keyword not in sql_lower:
                errors.append(f"Missing required keyword: {keyword.upper()}")
        
        # Check parentheses balance
        if sql.count('(') != sql.count(')'):
            errors.append("Unbalanced parentheses")
        
        # Check quotes balance
        single_quotes = sql.count("'")
        double_quotes = sql.count('"')
        if single_quotes % 2 != 0:
            errors.append("Unbalanced single quotes")
        if double_quotes % 2 != 0:
            errors.append("Unbalanced double quotes")
        
        # Check for common syntax errors
        if re.search(r'\bselect\s*\bfrom\b', sql_lower):
            errors.append("Missing SELECT columns")
        
        if re.search(r'\bwhere\s*group\s+by\b', sql_lower):
            errors.append("Missing WHERE condition")
        
        return errors
    
    def _check_structure(self, sql: str) -> List[str]:
        """Check SQL structure and logic"""
        warnings = []
        sql_lower = sql.lower()
        
        # Check for SELECT *
        if re.search(r'\bselect\s+\*\b', sql_lower):
            warnings.append("Using SELECT * is not recommended - specify columns explicitly")
        
        # Check for missing aliases
        if 'from patients' in sql_lower and 'p.' not in sql:
            warnings.append("Consider using table aliases for better readability")
        
        # Check GROUP BY without aggregate functions
        if 'group by' in sql_lower:
            has_aggregate = any(func in sql_lower for func in self.aggregate_functions)
            if not has_aggregate:
                warnings.append("GROUP BY used without aggregate functions")
        
        # Check ORDER BY without LIMIT in potential large result sets
        if 'order by' in sql_lower and 'limit' not in sql_lower:
            warnings.append("Consider adding LIMIT when using ORDER BY")
        
        return warnings
    
    def _check_schema_compliance(self, sql: str, schema_info: Dict[str, List[str]]) -> Tuple[List[str], List[str]]:
        """Check compliance with database schema"""
        errors = []
        suggestions = []
        
        # Extract column references from SQL
        column_refs = self._extract_column_references(sql)
        
        # Check if referenced columns exist in schema
        available_columns = []
        for table, columns in schema_info.items():
            available_columns.extend(columns)
        
        for col_ref in column_refs:
            # Remove table alias prefix if present
            column_name = col_ref.split('.')[-1]
            if column_name not in available_columns:
                errors.append(f"Unknown column: {column_name}")
                
                # Suggest similar columns
                similar_cols = self._find_similar_columns(column_name, available_columns)
                if similar_cols:
                    suggestions.append(f"Did you mean: {', '.join(similar_cols)}?")
        
        return errors, suggestions
    
    def _check_best_practices(self, sql: str) -> List[str]:
        """Check for SQL best practices"""
        suggestions = []
        sql_lower = sql.lower()
        
        # Suggest using explicit JOINs instead of WHERE clause joins
        if re.search(r'\bwhere\b.*=.*\..*', sql_lower):
            suggestions.append("Consider using explicit JOIN syntax instead of WHERE clause joins")
        
        # Suggest using LIMIT for potentially large result sets
        if re.search(r'\bselect\b.*\bfrom\b.*(?!.*\blimit\b)', sql_lower):
            if not any(keyword in sql_lower for keyword in ['where', 'group by']):
                suggestions.append("Consider adding LIMIT to prevent large result sets")
        
        # Suggest using aliases for better readability
        if len(sql.split()) > 10 and '.' not in sql:
            suggestions.append("Consider using table aliases for complex queries")
        
        return suggestions
    
    def _extract_column_references(self, sql: str) -> List[str]:
        """Extract column references from SQL"""
        # Simple regex to find column references
        # This is a basic implementation - could be more sophisticated
        pattern = r'\b[a-zA-Z_][a-zA-Z0-9_]*\.[a-zA-Z_][a-zA-Z0-9_]*\b'
        matches = re.findall(pattern, sql)
        
        # Also look for unqualified column names in SELECT clause
        select_match = re.search(r'select\s+(.*?)\s+from', sql, re.IGNORECASE)
        if select_match:
            select_columns = select_match.group(1)
            # Extract column names (basic approach)
            cols = [col.strip() for col in select_columns.split(',')]
            matches.extend([col for col in cols if col not in ['*', 'count(*)']])
        
        return matches
    
    def _find_similar_columns(self, column_name: str, available_columns: List[str]) -> List[str]:
        """Find similar column names using simple string similarity"""
        similar = []
        column_lower = column_name.lower()
        
        for col in available_columns:
            col_lower = col.lower()
            if column_lower in col_lower or col_lower in column_lower:
                similar.append(col)
        
        return similar[:3]  # Return top 3 matches
    
    def _attempt_correction(self, sql: str, errors: List[str]) -> Optional[str]:
        """Attempt to auto-correct common SQL errors"""
        corrected = sql
        
        # Fix missing semicolon
        if not corrected.rstrip().endswith(';'):
            corrected = corrected.rstrip() + ';'
        
        # Fix missing SELECT
        if 'Missing required keyword: SELECT' in str(errors):
            if not corrected.lower().startswith('select'):
                corrected = 'SELECT * FROM patients;'
        
        # Fix missing FROM
        if 'Missing required keyword: FROM' in str(errors):
            if 'from' not in corrected.lower():
                corrected = corrected.replace('SELECT', 'SELECT * FROM patients WHERE')
        
        return corrected if corrected != sql else None
    
    def validate_execution(self, sql: str) -> ValidationResult:
        """Validate SQL by attempting execution on a test database"""
        errors = []
        warnings = []
        suggestions = []
        
        try:
            # Create a temporary in-memory database for testing
            conn = sqlite3.connect(':memory:')
            
            # Create a test schema
            conn.execute('''
                CREATE TABLE patients (
                    Name TEXT,
                    Age INTEGER,
                    Hospital TEXT,
                    Medical_Condition TEXT,
                    "Billing Amount" REAL,
                    DoctorID INTEGER
                )
            ''')
            
            # Insert test data
            conn.execute('''
                INSERT INTO patients VALUES 
                ('Test Patient', 30, 'Test Hospital', 'Test Condition', 1000.0, 1)
            ''')
            
            # Try to execute the SQL
            cursor = conn.execute(sql)
            result = cursor.fetchall()
            
            # Check result characteristics
            if len(result) == 0:
                warnings.append("Query returns no results")
            elif len(result) > 1000:
                warnings.append("Query returns large number of results - consider adding LIMIT")
            
            conn.close()
            
        except sqlite3.Error as e:
            errors.append(f"SQL execution error: {str(e)}")
            suggestions.append("Check SQL syntax and column names")
        
        except Exception as e:
            errors.append(f"Validation error: {str(e)}")
        
        is_valid = len(errors) == 0
        return ValidationResult(is_valid, errors, warnings, suggestions)

def main():
    """Test the SQL validator"""
    validator = SQLValidator()
    
    test_sqls = [
        "SELECT p.Name FROM patients p;",  # Valid
        "SELECT * FROM;",  # Missing table
        "SELECT Name FROM patients WHERE Age >",  # Incomplete WHERE
        "SELECT COUNT(*) FROM patients GROUP BY Hospital;",  # Valid aggregation
        "SELECT Name Age FROM patients",  # Missing comma
    ]
    
    print("SQL Validator Test")
    print("="*50)
    
    for i, sql in enumerate(test_sqls, 1):
        print(f"\nTest {i}: {sql}")
        result = validator.validate_sql(sql)
        
        print(f"Valid: {result.is_valid}")
        if result.errors:
            print(f"Errors: {result.errors}")
        if result.warnings:
            print(f"Warnings: {result.warnings}")
        if result.suggestions:
            print(f"Suggestions: {result.suggestions}")
        if result.corrected_sql:
            print(f"Corrected: {result.corrected_sql}")

if __name__ == "__main__":
    main()


