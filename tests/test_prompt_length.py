# !/usr/bin/env python3
"""
ทดสอบความยาวของ prompt ที่แก้ไขแล้ว
""" import os
import sys # เพิ่ม path เพื่อ import modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..')) from text2sql_rag.ultimate_prompt import UltimatePromptBuilder def test_prompt_length(): """ทดสอบความยาวของ Ultimate Prompt ที่แก้ไขแล้ว""" print(" ทดสอบความยาวของ Ultimate Prompt หลังการแก้ไข") print("="*60) # สร้าง prompt builder ultimate_builder = UltimatePromptBuilder() # Schema สำหรับทดสอบ schema = """- Name (TEXT): ชื่อผู้ป่วย
- Age (INTEGER): อายุ
- Hospital (TEXT): โรงพยาบาล
- Medical_Condition (TEXT): อาการป่วย
- "Billing Amount" (REAL): ค่าใช้จ่าย
- DoctorID (INTEGER): รหัสแพทย์""" # คำถามทดสอบ test_question = "แสดงจำนวนผู้ป่วยแต่ละโรงพยาบาล" # สร้าง Ultimate Prompt ultimate_prompt = ultimate_builder.build_ultimate_prompt(test_question, schema) print(f" คำถาม: {test_question}") print(f" ความยาว Ultimate Prompt: {len(ultimate_prompt)} characters") print() print(" Ultimate Prompt:") print("-" * 60) print(ultimate_prompt) print("-" * 60) # วิเคราะห์ประเภทคำถาม detected_type = ultimate_builder._analyze_question_type(test_question) print(f"\n ประเภทคำถามที่ตรวจจับได้: {detected_type}") # แสดงส่วนประกอบของ prompt print(f"\n การวิเคราะห์ความยาว:") print(f" - Total length: {len(ultimate_prompt)} chars") lines_count = len(ultimate_prompt.split('\n')) print(f" - Lines: {lines_count} lines") # เปรียบเทียบกับความยาวเดิม (ประมาณ 3617 chars) old_length = 3617 reduction = old_length - len(ultimate_prompt) percentage = (reduction / old_length) * 100 print(f"\n การเปรียบเทียบ:") print(f" - ความยาวเดิม: ~{old_length} chars") print(f" - ความยาวใหม่: {len(ultimate_prompt)} chars") print(f" - ลดลง: {reduction} chars ({percentage:.1f}%)") if __name__ == "__main__": test_prompt_length()
