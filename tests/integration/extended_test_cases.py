#!/usr/bin/env python3
"""
Extended Test Cases for More Comprehensive Testing
"""

import sys
import os
from dataclasses import dataclass
from typing import List

# Add project root to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

@dataclass
class ExtendedTestCase:
    """Extended test case with more complexity"""
    id: str
    question: str
    expected_sql: str
    query_type: str
    difficulty: str
    description: str

class ExtendedTestCaseGenerator:
    """Generate extended test cases for comprehensive testing"""
    
    def __init__(self):
        self.test_cases = self._generate_extended_cases()
    
    def _generate_extended_cases(self) -> List[ExtendedTestCase]:
        """Generate extended test cases"""
        cases = []
        
        # Complex JOIN scenarios
        cases.extend([
            ExtendedTestCase(
                id="EXT001",
                question="แสดงชื่อผู้ป่วยและชื่อแพทย์ที่รักษา",
                expected_sql="SELECT p.Name, d.DoctorName FROM patients p JOIN doctors d ON p.DoctorID = d.DoctorID;",
                query_type="join",
                difficulty="hard",
                description="JOIN between patients and doctors table"
            ),
            ExtendedTestCase(
                id="EXT002",
                question="โรงพยาบาลไหนมีผู้ป่วยโรคเบาหวานมากที่สุด",
                expected_sql="SELECT p.Hospital FROM patients p WHERE p.Medical_Condition = 'Diabetes' GROUP BY p.Hospital ORDER BY COUNT(*) DESC LIMIT 1;",
                query_type="complex_aggregation",
                difficulty="hard",
                description="Complex aggregation with ordering and limit"
            )
        ])
        
        # Subquery scenarios
        cases.extend([
            ExtendedTestCase(
                id="EXT003",
                question="ผู้ป่วยที่มีค่าใช้จ่ายมากกว่าค่าเฉลี่ย",
                expected_sql="SELECT p.Name, p.\"Billing Amount\" FROM patients p WHERE p.\"Billing Amount\" > (SELECT AVG(\"Billing Amount\") FROM patients);",
                query_type="subquery",
                difficulty="expert",
                description="Subquery with aggregation"
            ),
            ExtendedTestCase(
                id="EXT004",
                question="โรงพยาบาลที่มีผู้ป่วยมากกว่า 2 คน",
                expected_sql="SELECT p.Hospital FROM patients p GROUP BY p.Hospital HAVING COUNT(*) > 2;",
                query_type="having",
                difficulty="hard",
                description="GROUP BY with HAVING clause"
            )
        ])
        
        # Date/Time scenarios (if we had date columns)
        cases.extend([
            ExtendedTestCase(
                id="EXT005",
                question="ผู้ป่วยที่มีอายุระหว่าง 30-60 ปี",
                expected_sql="SELECT p.Name, p.Age FROM patients p WHERE p.Age BETWEEN 30 AND 60;",
                query_type="range",
                difficulty="medium",
                description="BETWEEN operator usage"
            ),
            ExtendedTestCase(
                id="EXT006",
                question="ผู้ป่วยที่ไม่มีโรคเบาหวาน",
                expected_sql="SELECT p.Name FROM patients p WHERE p.Medical_Condition != 'Diabetes';",
                query_type="negation",
                difficulty="medium",
                description="Negation with NOT EQUAL"
            )
        ])
        
        # Advanced aggregations
        cases.extend([
            ExtendedTestCase(
                id="EXT007",
                question="แสดงโรคและจำนวนผู้ป่วย เรียงตามจำนวนมากที่สุด",
                expected_sql="SELECT p.Medical_Condition, COUNT(*) as PatientCount FROM patients p GROUP BY p.Medical_Condition ORDER BY COUNT(*) DESC;",
                query_type="aggregation_with_ordering",
                difficulty="hard",
                description="Aggregation with custom ordering"
            ),
            ExtendedTestCase(
                id="EXT008",
                question="ค่าใช้จ่ายรวมของแต่ละโรงพยาบาล เฉพาะที่มากกว่า 5000 บาท",
                expected_sql="SELECT p.Hospital, SUM(p.\"Billing Amount\") FROM patients p GROUP BY p.Hospital HAVING SUM(p.\"Billing Amount\") > 5000;",
                query_type="aggregation_with_having",
                difficulty="expert",
                description="SUM with HAVING clause"
            )
        ])
        
        # Multi-condition scenarios
        cases.extend([
            ExtendedTestCase(
                id="EXT009",
                question="ผู้ป่วยที่มีอายุมากกว่า 40 ปี หรือ ค่าใช้จ่ายมากกว่า 2000 บาท",
                expected_sql="SELECT p.Name, p.Age, p.\"Billing Amount\" FROM patients p WHERE p.Age > 40 OR p.\"Billing Amount\" > 2000;",
                query_type="multi_condition_or",
                difficulty="hard",
                description="Multiple conditions with OR"
            ),
            ExtendedTestCase(
                id="EXT010",
                question="จำนวนผู้ป่วยแต่ละโรคในแต่ละโรงพยาบาล",
                expected_sql="SELECT p.Hospital, p.Medical_Condition, COUNT(*) FROM patients p GROUP BY p.Hospital, p.Medical_Condition;",
                query_type="multi_column_grouping",
                difficulty="expert",
                description="GROUP BY multiple columns"
            )
        ])
        
        return cases
    
    def get_test_cases(self) -> List[ExtendedTestCase]:
        """Get all extended test cases"""
        return self.test_cases
    
    def get_cases_by_difficulty(self, difficulty: str) -> List[ExtendedTestCase]:
        """Get test cases by difficulty level"""
        return [case for case in self.test_cases if case.difficulty == difficulty]
    
    def get_cases_by_type(self, query_type: str) -> List[ExtendedTestCase]:
        """Get test cases by query type"""
        return [case for case in self.test_cases if case.query_type == query_type]

def main():
    """Main function to display extended test cases"""
    generator = ExtendedTestCaseGenerator()
    cases = generator.get_test_cases()
    
    print("Extended Test Cases for Text2SQL RAG System")
    print("="*60)
    print(f"Total cases: {len(cases)}")
    print()
    
    # Group by difficulty
    difficulties = ["medium", "hard", "expert"]
    for difficulty in difficulties:
        difficulty_cases = generator.get_cases_by_difficulty(difficulty)
        if difficulty_cases:
            print(f"{difficulty.upper()} Level ({len(difficulty_cases)} cases):")
            for case in difficulty_cases:
                print(f"  {case.id}: {case.question}")
                print(f"       Type: {case.query_type}")
                print(f"       SQL: {case.expected_sql}")
                print()
    
    return cases

if __name__ == "__main__":
    main()


