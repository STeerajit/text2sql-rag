# !/usr/bin/env python3
"""
ทดสอบเพื่อดู Prompt ที่ใช้จริงใน Comprehensive Test
""" import os
import sys
from dotenv import load_dotenv # โหลด environment variables จาก .env
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env')) # เพิ่ม path สำหรับ import
sys.path.append(os.path.join(os.path.dirname(__file__), '..')) from comprehensive_test_cases import ComprehensiveTestCaseGenerator
from text2sql_rag.ultimate_prompt import UltimatePromptBuilder
from text2sql_rag.enhanced_prompt import EnhancedPromptBuilder def test_comprehensive_prompt_generation(): """ทดสอบการสร้าง Prompt ใน Comprehensive Test""" print(" ทดสอบการสร้าง Prompt ใน Comprehensive Test") print("="*70) try: # สร้าง builders และ test cases ultimate_builder = UltimatePromptBuilder() enhanced_builder = EnhancedPromptBuilder() generator = ComprehensiveTestCaseGenerator() test_cases = generator.get_test_cases() # Schema ตัวอย่าง schema = """ patients table: - Name (TEXT): ชื่อผู้ป่วย - Age (INTEGER): อายุ - Hospital (TEXT): โรงพยาบาล - Medical_Condition (TEXT): อาการป่วย - "Billing Amount" (REAL): ค่าใช้จ่าย - DoctorID (INTEGER): รหัสแพทย์ """ # ทดสอบข้อแรก case = test_cases[0] print(f" Test: {case.id}") print(f" คำถาม: {case.thai_question}") print(f" ประเภทที่คาดหวัง: {case.query_type.value}") # สร้าง Ultimate Prompt ultimate_prompt = ultimate_builder.build_ultimate_prompt(case.thai_question, schema) print(f"\n Ultimate Prompt (Length: {len(ultimate_prompt)}):") print("="*70) print(ultimate_prompt) print("="*70) # วิเคราะห์ประเภทคำถาม detected_type = ultimate_builder._analyze_question_type(case.thai_question) print(f"\n ประเภทที่ตรวจจับได้: {detected_type}") print(f" ถูกต้อง: {'' if detected_type == case.query_type.value else ''}") except Exception as e: print(f" เกิดข้อผิดพลาด: {e}") import traceback traceback.print_exc() if __name__ == "__main__": test_comprehensive_prompt_generation()
