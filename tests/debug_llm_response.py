# !/usr/bin/env python3
"""
ทดสอบเพื่อดู LLM response ที่แท้จริง
""" import os
import sys
import requests
import json
from dotenv import load_dotenv # โหลด environment variables จาก .env
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env')) def call_typhoon_direct(prompt: str) -> str: """เรียกใช้ Typhoon API โดยตรง""" TYPHOON_ENDPOINT = "https://api.opentyphoon.ai/v1/chat/completions" TYPHOON_API_KEY = os.getenv("TYPHOON_API_KEY") if not TYPHOON_API_KEY: print(" กรุณาตั้งค่า TYPHOON_API_KEY ใน .env") return "" headers = { "Authorization": f"Bearer {TYPHOON_API_KEY}", "Content-Type": "application/json" } data = { "model": "typhoon-v2.1-12b-instruct", "messages": [{"role": "user", "content": prompt}], "max_tokens": 2000, "temperature": 0.0 } print(" ส่ง request ไปยัง Typhoon API...") response = requests.post(TYPHOON_ENDPOINT, headers=headers, json=data) if response.status_code == 200: result = response.json() content = result["choices"][0]["message"]["content"] print(" ได้ response จาก Typhoon API") return content else: print(f" Typhoon API error: {response.status_code}") print(f"Response: {response.text}") return "" def test_comprehensive_prompt(): """ทดสอบ Comprehensive Prompt""" print(" ทดสอบ Comprehensive Prompt เพื่อดู LLM Response") print("="*70) # Comprehensive Prompt ที่ใช้จริง prompt = """ คุณเป็น SQL Expert ที่ต้องสร้าง SQL ที่ถูกต้องและสมบูรณ์ที่สุด! กฎที่ต้องปฏิบัติอย่างเคร่งครัด (VIOLATION = FAILURE): 1. ใช้ alias 'p.' ในทุกคอลัมน์และเงื่อนไข (บังคับ!)
2. ระบุคอลัมน์ที่ต้องการแทนการใช้ SELECT * (บังคับ!)
3. ใช้เงื่อนไขที่เหมาะสมกับคำถาม (บังคับ!)
4. ตรวจสอบ syntax และความถูกต้องของ SQL (บังคับ!)
5. ใช้ semicolon (;) ที่ท้าย SQL statement (บังคับ!)
6. ใช้ quotes (') รอบ string values (บังคับ!) ประเภทคำถาม: counting ตัวอย่างการใช้งาน alias ที่ถูกต้อง (COPY EXACTLY): ถูก: SELECT p.Name, p.Age, p.Hospital FROM patients p WHERE p.Medical_Condition = 'Diabetes'; ผิด: SELECT Name, Age, Hospital FROM patients WHERE Medical_Condition = Diabetes ตัวอย่าง SQL ที่ถูกต้องตามประเภทคำถาม: **Counting:**
- SELECT p.Hospital, COUNT(*) FROM patients p GROUP BY p.Hospital; กรุณาสร้าง SQL ที่ถูกต้องและสมบูรณ์ (COPY FORMAT ABOVE): **โครงสร้างฐานข้อมูล (patients table):**
- Name (TEXT): ชื่อผู้ป่วย
- Age (INTEGER): อายุ
- Hospital (TEXT): โรงพยาบาล
- Medical_Condition (TEXT): อาการป่วย
- "Billing Amount" (REAL): ค่าใช้จ่าย
- DoctorID (INTEGER): รหัสแพทย์ **คำถาม:** แสดงจำนวนผู้ป่วยแต่ละโรงพยาบาล **คำตอบ:** กรุณาสร้าง SQL ที่สมบูรณ์และถูกต้องตามตัวอย่างข้างต้น: **โครงสร้างตาราง patients:**
```sql
CREATE TABLE patients ( Name TEXT, Age INTEGER, Hospital TEXT, Medical_Condition TEXT, "Billing Amount" REAL, DoctorID INTEGER
);
``` **กรุณาตอบด้วย SQL ที่สมบูรณ์เท่านั้น:**""" print(f" Prompt Length: {len(prompt)} characters") print("-" * 70) response = call_typhoon_direct(prompt) if response: print(" LLM Response (Raw):") print("=" * 50) print(response) print("=" * 50) print(f"\n Length: {len(response)}") print(f" Contains SELECT: {'SELECT' in response.upper()}") print(f" Contains FROM: {'FROM' in response.upper()}") print(f" Contains GROUP BY: {'GROUP BY' in response.upper()}") print(f" Contains alias p.: {'p.' in response}") print(f" Contains semicolon: {';' in response}") # ทดสอบ extract_sql_from_response print("\n ทดสอบ extract_sql_from_response:") sql = extract_sql_from_response(response) print(f"Extracted SQL: '{sql}'") print(f"SQL Length: {len(sql)}") else: print(" ไม่ได้ response จาก LLM") def extract_sql_from_response(response: str) -> str: """สกัด SQL จากการตอบของ LLM""" if not response: return "" # หา SQL block import re sql_patterns = [ r'```sql\s*(.*?)\s*```', r'```\s*(SELECT.*?);?\s*```', r'(SELECT.*?);?' ] for pattern in sql_patterns: matches = re.findall(pattern, response, re.DOTALL | re.IGNORECASE) if matches: sql = matches[0].strip() # เก็บ semicolon ท้าย (ไม่ลบออก) return sql return "" if __name__ == "__main__": test_comprehensive_prompt()


