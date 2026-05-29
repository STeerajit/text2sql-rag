"""
Enhanced Prompt System with Text-to-SQL Knowledge Base
ระบบ Prompt ที่ใช้ความรู้จาก RAG เพื่อเพิ่มประสิทธิภาพการสร้าง SQL
""" from typing import List, Dict, Any
from .text2sql_knowledge import Text2SQLKnowledgeBase
from .embedding import Embedder class EnhancedPromptBuilder: def __init__(self): self.knowledge_base = Text2SQLKnowledgeBase() def build_enhanced_prompt(self, question: str, schema: str, embedder: Embedder = None) -> str: """สร้าง enhanced prompt ที่รวมความรู้จาก Text-to-SQL""" # 1. วิเคราะห์ประเภทของคำถาม question_type = self._analyze_question_type(question) # 2. ดึงความรู้ที่เกี่ยวข้อง relevant_knowledge = self._get_relevant_knowledge(question, question_type) # 3. สร้าง enhanced prompt prompt = self._construct_enhanced_prompt(question, schema, relevant_knowledge, question_type) return prompt def _analyze_question_type(self, question: str) -> str: """วิเคราะห์ประเภทของคำถามให้แม่นยำขึ้น""" question_lower = question.lower() # 1. Counting queries - นับจำนวน counting_keywords = [ "จำนวน", "นับ", "กี่คน", "กี่ราย", "กี่โรค", "กี่โรงพยาบาล", "มีกี่", "ทั้งหมดกี่", "รวมกี่", "count", "นับจำนวน" ] if any(keyword in question_lower for keyword in counting_keywords): # ตรวจสอบว่าเป็น grouping ที่ซับซ้อนหรือไม่ if "แต่ละ" in question_lower and question_lower.count("แต่ละ") >= 2: return "grouping" return "counting" # 2. Subquery queries - คำถามที่ต้องใช้ subquery (ตรวจสอบก่อน aggregation) subquery_keywords = [ "มากกว่า", "น้อยกว่า", "เท่ากับ", "สูงกว่า", "ต่ำกว่า", "เกิน", "ไม่เกิน" ] if any(keyword in question_lower for keyword in subquery_keywords): # ตรวจสอบว่าเป็น subquery จริงหรือไม่ subquery_indicators = ["ค่าเฉลี่ย", "เฉลี่ย", "ผลรวม", "รวม", "จำนวน", "avg", "sum", "count"] if any(indicator in question_lower for indicator in subquery_indicators): return "subquery" # 3. Complex grouping - การจัดกลุ่มที่ซับซ้อน (ตรวจสอบก่อน aggregation) # ตรวจสอบ pattern ที่ชัดเจนก่อน explicit_complex_patterns = [ "มากที่สุดในแต่ละ", "สูงที่สุดในแต่ละ", "น้อยที่สุดในแต่ละ", "ต่ำที่สุดในแต่ละ", "สูงสุดในแต่ละ", "ต่ำสุดในแต่ละ", "มากสุดในแต่ละ", "น้อยสุดในแต่ละ" ] if any(pattern in question_lower for pattern in explicit_complex_patterns): return "complex_grouping" # ตรวจสอบ complex pattern อื่นๆ - ปรับปรุงให้แม่นยำขึ้น if any(word in question_lower for word in ["ที่มี", "ที่", "ชื่ออะไร", "อะไร", "ใคร"]): superlative_keywords = ["สูงที่สุด", "ต่ำที่สุด", "มากที่สุด", "น้อยที่สุด", "สูงสุด", "ต่ำสุด"] if any(keyword in question_lower for keyword in superlative_keywords): # ตรวจสอบว่าเป็น complex grouping จริงหรือไม่ if "ในแต่ละ" in question_lower or "ของแต่ละ" in question_lower: return "complex_grouping" # ตรวจสอบว่าเป็น "สูงสุด/ต่ำสุด" ที่มี "ของ" หรือไม่ if "ของ" in question_lower: return "complex_grouping" # ถ้าไม่มี "แต่ละ" หรือ "ของ" แต่มี "สูงสุด/ต่ำสุด" -> เป็น aggregation return "aggregation" # 4. Ordering queries - การเรียงลำดับ (ตรวจสอบก่อน filtering) ordering_patterns = [ "เรียงตาม", "ลำดับตาม", "จัดอันดับ", "5 อันดับแรก", "10 อันดับแรก", "อันดับแรก", "อันดับที่", "จากมากไปน้อย", "จากน้อยไปมาก" ] if any(pattern in question_lower for pattern in ordering_patterns): return "ordering" ordering_keywords = ["เรียง", "ลำดับ", "อันดับ", "order", "sort", "rank", "top", "first"] if any(keyword in question_lower for keyword in ordering_keywords): # ตรวจสอบว่าเป็น ordering จริงหรือไม่ if any(word in question_lower for word in ["เรียงตาม", "ลำดับตาม", "จัดอันดับ"]): return "ordering" # ตรวจสอบ top N pattern if any(word in question_lower for word in ["5 อันดับแรก", "10 อันดับแรก", "อันดับแรก", "อันดับที่", "อันดับ"]): return "ordering" # ตรวจสอบการเรียงลำดับ if any(word in question_lower for word in ["จากมากไปน้อย", "จากน้อยไปมาก", "มากไปน้อย", "น้อยไปมาก"]): return "ordering" # ตรวจสอบ pattern ที่ชัดเจนว่าเป็น ordering if "สูงสุด" in question_lower and ("5 อันดับแรก" in question_lower or "อันดับแรก" in question_lower): return "ordering" if "มากที่สุด" in question_lower and ("5 อันดับแรก" in question_lower or "อันดับแรก" in question_lower): return "ordering" # 5. Grouping queries - การจัดกลุ่มทั่วไป (ตรวจสอบก่อน aggregation) # ตรวจสอบการมี "แต่ละ" หลายครั้งหรือการจัดกลุ่มซับซ้อน grouping_patterns = [ "แต่ละโรคในแต่ละโรงพยาบาล", "แต่ละโรงพยาบาลในแต่ละโรค", "แต่ละกลุ่มในแต่ละประเภท", "แต่ละประเภทในแต่ละกลุ่ม", "แยกตาม", "แบ่งตาม", "จัดกลุ่มตาม" ] if any(pattern in question_lower for pattern in grouping_patterns): return "grouping" # ตรวจสอบการมี "แต่ละ" + aggregation function - ปรับปรุงให้แม่นยำขึ้น if "แต่ละ" in question_lower: # นับจำนวน "แต่ละ" ในคำถาม each_count = question_lower.count("แต่ละ") if each_count >= 2: return "grouping" elif each_count == 1: # ตรวจสอบว่ามี aggregation function หรือไม่ aggregation_funcs = ["ค่าเฉลี่ย", "เฉลี่ย", "ผลรวม", "รวม"] basic_aggregation = any(func in question_lower for func in aggregation_funcs) superlative_funcs = ["สูงสุด", "ต่ำสุด", "มากที่สุด", "น้อยที่สุด", "max", "min"] superlative_aggregation = any(func in question_lower for func in superlative_funcs) if superlative_aggregation: # ตรวจสอบว่าเป็น aggregation แบบธรรมดาหรือ complex grouping if "ในแต่ละ" in question_lower or "ของแต่ละ" in question_lower: return "complex_grouping" else: return "aggregation" elif basic_aggregation: # สำหรับ ค่าเฉลี่ย, ผลรวม ที่มี "แต่ละ" -> เป็น aggregation return "aggregation" else: # ถ้ามี "แต่ละ" แต่ไม่มี aggregation function -> เป็น grouping return "grouping" # 6. Aggregation queries - การคำนวณค่าเฉลี่ย, ผลรวม, สูงสุด, ต่ำสุด aggregation_keywords = [ "ค่าเฉลี่ย", "เฉลี่ย", "ผลรวม", "รวม", "สูงสุด", "ต่ำสุด", "มากที่สุด", "น้อยที่สุด", "avg", "average", "sum", "maximum", "minimum", "max", "min" ] if any(keyword in question_lower for keyword in aggregation_keywords): return "aggregation" # 7. Logical queries - คำถามที่มีเงื่อนไข AND, OR, NOT logical_keywords = [ "และ", "หรือ", "ไม่", "ทั้ง", "แต่", "however", "and", "or", "not" ] if any(keyword in question_lower for keyword in logical_keywords): # ตรวจสอบว่ามีเงื่อนไขหลายข้อหรือไม่ if question_lower.count("และ") > 0 or question_lower.count("หรือ") > 0: return "logical" # ตรวจสอบ "ไม่" ที่เป็น logical operator if "ไม่" in question_lower and any(word in question_lower for word in ["ไม่ใช่", "ไม่เท่ากับ", "ไม่เท่า"]): return "logical" # 8. Filtering queries - การกรองข้อมูล filtering_keywords = [ "ที่มี", "ที่", "ใน", "ของ", "จาก", "มากกว่า", "น้อยกว่า", "เท่ากับ", "สูงกว่า", "ต่ำกว่า", "เกิน", "ไม่เกิน", "ระหว่าง", "ตั้งแต่", "จนถึง" ] if any(keyword in question_lower for keyword in filtering_keywords): return "filtering" # 9. Basic select - การเลือกข้อมูลพื้นฐาน basic_select_keywords = [ "แสดง", "ดู", "หาข้อมูล", "ข้อมูล", "รายการ", "รายชื่อ" ] if any(keyword in question_lower for keyword in basic_select_keywords): return "basic_select" # 10. Join queries - การเชื่อมตาราง join_keywords = [ "เชื่อม", "รวม", "join", "เชื่อมต่อ", "รวมกัน", "พร้อมกัน" ] if any(keyword in question_lower for keyword in join_keywords): return "join" # Default case return "basic_select" def _get_relevant_knowledge(self, question: str, question_type: str) -> List[str]: """ดึงความรู้ที่เกี่ยวข้องกับคำถาม""" relevant_knowledge = [] # 1. ดึงความรู้ตามประเภทของคำถาม type_knowledge = self.knowledge_base.get_knowledge_for_sql_type(question_type) relevant_knowledge.extend(type_knowledge[:5]) # ใช้ 5 ข้อแรก # 2. ค้นหาความรู้ที่เกี่ยวข้องกับคำถาม question_keywords = self._extract_keywords(question) for keyword in question_keywords: keyword_knowledge = self.knowledge_base.search_knowledge(keyword) relevant_knowledge.extend(keyword_knowledge[:3]) # ใช้ 3 ข้อแรก # 3. ดึงความรู้พื้นฐานที่สำคัญ basic_knowledge = self.knowledge_base.get_knowledge_by_category("basic") relevant_knowledge.extend(basic_knowledge[:3]) # 4. ดึงความรู้เกี่ยวกับ best practices best_practices = self.knowledge_base.get_knowledge_by_category("best_practices") relevant_knowledge.extend(best_practices[:3]) # ลบความรู้ที่ซ้ำกัน unique_knowledge = list(dict.fromkeys(relevant_knowledge)) return unique_knowledge[:15] # จำกัดจำนวนความรู้ที่ใช้ def _extract_keywords(self, question: str) -> List[str]: """สกัดคำสำคัญจากคำถาม""" # คำสำคัญที่เกี่ยวข้องกับ SQL sql_keywords = [ "select", "from", "where", "group", "order", "limit", "count", "sum", "avg", "max", "min", "join", "alias", "having", "between", "like", "in", "null", "case" ] # คำสำคัญภาษาไทย thai_keywords = [ "จำนวน", "ค่าเฉลี่ย", "มากที่สุด", "น้อยที่สุด", "ผลรวม", "แต่ละ", "กลุ่ม", "เรียง", "ลำดับ", "มากกว่า", "น้อยกว่า", "เท่ากับ", "และ", "หรือ", "ไม่", "ในแต่ละ", "ของแต่ละ" ] keywords = [] question_lower = question.lower() # หาคำสำคัญภาษาอังกฤษ for keyword in sql_keywords: if keyword in question_lower: keywords.append(keyword) # หาคำสำคัญภาษาไทย for keyword in thai_keywords: if keyword in question: keywords.append(keyword) return keywords def _construct_enhanced_prompt(self, question: str, schema: str, knowledge: List[str], question_type: str) -> str: """สร้าง enhanced prompt""" # 1. System prompt ที่เข้มงวดขึ้น system_prompt = f""" คุณเป็น SQL Expert ที่ต้องสร้าง SQL ที่ถูกต้องและสมบูรณ์! กฎที่ต้องปฏิบัติอย่างเคร่งครัด: 1. ใช้ alias 'p.' ในทุกคอลัมน์และเงื่อนไข (บังคับ!)
2. ระบุคอลัมน์ที่ต้องการแทนการใช้ SELECT * (บังคับ!)
3. ใช้เงื่อนไขที่เหมาะสมกับคำถาม (บังคับ!)
4. ใช้ semicolon (;) ที่ท้าย SQL statement (บังคับ!)
5. ใช้ quotes (') รอบ string values (บังคับ!) ความรู้ที่เกี่ยวข้อง:
{self._format_knowledge(knowledge)} ประเภทคำถาม: {question_type}
{self._get_type_specific_instructions(question_type)} ตัวอย่างการใช้งาน alias ที่ถูกต้อง (COPY EXACTLY): ถูก: SELECT p.Name, p.Age, p.Hospital FROM patients p WHERE p.Medical_Condition = 'Diabetes' ผิด: SELECT Name, Age, Hospital FROM patients WHERE Medical_Condition = Diabetes กฎการสร้าง SQL:
- เริ่มต้นด้วย SELECT p.column_name
- ใช้ FROM patients p (ต้องมี alias)
- ใช้ WHERE p.column_name = 'value' (ต้องมี alias และ quotes)
- ใช้ GROUP BY p.column_name (ต้องมี alias)
- ใช้ ORDER BY p.column_name (ต้องมี alias) กรุณาสร้าง SQL ที่ถูกต้องและสมบูรณ์ (COPY FORMAT ABOVE):""" # 2. Schema information schema_section = f"""
**โครงสร้างฐานข้อมูล:**
{schema} **คำถาม:** {question} **คำตอบ:**""" # 3. รวม prompt full_prompt = system_prompt + schema_section return full_prompt def _format_knowledge(self, knowledge: List[str]) -> str: """จัดรูปแบบความรู้ให้อ่านง่าย""" if not knowledge: return "ไม่มีความรู้เฉพาะที่เกี่ยวข้อง" formatted = [] for i, item in enumerate(knowledge, 1): formatted.append(f"{i}. {item}") return "\n".join(formatted) def _get_type_specific_instructions(self, question_type: str) -> str: """คำแนะนำเฉพาะตามประเภทของคำถาม""" type_instructions = { "counting": """
**คำแนะนำสำหรับการนับจำนวน:**
- ใช้ COUNT(*) สำหรับนับจำนวนแถวทั้งหมด
- ใช้ COUNT(column) สำหรับนับจำนวนแถวที่ไม่ใช่ NULL
- ใช้ DISTINCT เมื่อต้องการนับจำนวนที่ไม่ซ้ำกัน
- ใช้ WHERE เพื่อกรองข้อมูลก่อนการนับ
- ใช้ alias เมื่อต้องการความชัดเจน: SELECT p.Hospital, COUNT(*) FROM patients p GROUP BY p.Hospital""", "aggregation": """
**คำแนะนำสำหรับการคำนวณค่าเฉลี่ย:**
- ใช้ AVG(column) สำหรับหาค่าเฉลี่ย
- ใช้ GROUP BY เมื่อต้องการค่าเฉลี่ยแต่ละกลุ่ม
- แสดงคอลัมน์ที่จัดกลุ่มและผลลัพธ์การคำนวณ
- ใช้ alias สำหรับผลลัพธ์การคำนวณ
- ตัวอย่าง: SELECT p.Hospital, AVG(p."Billing Amount") as avg_billing FROM patients p GROUP BY p.Hospital""", "max": """
**คำแนะนำสำหรับการหาค่าสูงสุด:**
- ใช้ MAX(column) สำหรับหาค่าสูงสุด
- ใช้ ORDER BY column DESC LIMIT 1 เมื่อต้องการข้อมูลเพิ่มเติม
- ใช้ subquery แบบ correlated เมื่อต้องการค่าสูงสุดในแต่ละกลุ่ม
- ระบุคอลัมน์ที่ต้องการแสดงผล
- ใช้ alias เมื่อจำเป็น: SELECT p1.Name, p1.Age FROM patients p1 WHERE p1.Age = (SELECT MAX(p2.Age) FROM patients p2)""", "min": """
**คำแนะนำสำหรับการหาค่าต่ำสุด:**
- ใช้ MIN(column) สำหรับหาค่าต่ำสุด
- ใช้ ORDER BY column ASC LIMIT 1 เมื่อต้องการข้อมูลเพิ่มเติม
- ใช้ subquery แบบ correlated เมื่อต้องการค่าต่ำสุดในแต่ละกลุ่ม
- ระบุคอลัมน์ที่ต้องการแสดงผล
- ใช้ alias เมื่อจำเป็น: SELECT p1.Name, p1.Age FROM patients p1 WHERE p1.Age = (SELECT MIN(p2.Age) FROM patients p2)""", "sum": """
**คำแนะนำสำหรับการหาผลรวม:**
- ใช้ SUM(column) สำหรับหาผลรวม
- ใช้ GROUP BY เมื่อต้องการผลรวมแต่ละกลุ่ม
- แสดงคอลัมน์ที่จัดกลุ่มและผลลัพธ์การคำนวณ
- ใช้ alias สำหรับผลลัพธ์การคำนวณ
- ตัวอย่าง: SELECT p.Hospital, SUM(p."Billing Amount") as total_billing FROM patients p GROUP BY p.Hospital""", "grouping": """
**คำแนะนำสำหรับการจัดกลุ่ม:**
- ใช้ GROUP BY เพื่อจัดกลุ่มข้อมูล
- แสดงคอลัมน์ที่จัดกลุ่มและผลลัพธ์การคำนวณ
- ใช้ HAVING เพื่อกรองข้อมูลที่จัดกลุ่มแล้ว
- ใช้ alias สำหรับผลลัพธ์การคำนวณ
- ใช้ alias ในทุกส่วน: SELECT p.Hospital, COUNT(*) FROM patients p GROUP BY p.Hospital""", "ordering": """
**คำแนะนำสำหรับการเรียงลำดับ:**
- ใช้ ORDER BY เพื่อเรียงลำดับข้อมูล
- ใช้ ASC (น้อยไปมาก) หรือ DESC (มากไปน้อย)
- สามารถเรียงตามหลายคอลัมน์ได้
- ใช้ LIMIT เพื่อจำกัดจำนวนผลลัพธ์
- ใช้ alias เมื่อจำเป็น: SELECT p.Name, p.Age FROM patients p ORDER BY p.Age DESC LIMIT 5""", "filtering": """
**คำแนะนำสำหรับการกรองข้อมูล:**
- ใช้ WHERE เพื่อกรองข้อมูลตามเงื่อนไข
- ใช้ =, !=, >, <, >=, <= สำหรับการเปรียบเทียบ
- ใช้ LIKE สำหรับการค้นหาข้อความ
- ใช้ IN สำหรับการตรวจสอบค่าหลายค่า
- ใช้ BETWEEN สำหรับการตรวจสอบช่วงค่า
- ใช้ alias เมื่อจำเป็น: SELECT p.Name, p.Age FROM patients p WHERE p.Age > 50""", "logical": """
**คำแนะนำสำหรับการใช้ Logical Operators:**
- ใช้ AND เพื่อรวมเงื่อนไขหลายข้อ
- ใช้ OR เพื่อเลือกเงื่อนไขใดเงื่อนไขหนึ่ง
- ใช้ NOT เพื่อกลับเงื่อนไข
- ใช้วงเล็บ () เพื่อจัดกลุ่มเงื่อนไข
- AND มีความสำคัญมากกว่า OR
- ใช้ alias เมื่อจำเป็น: SELECT p.Name, p.Age FROM patients p WHERE p.Age > 60 AND (p."Medical Condition" = 'Diabetes' OR p."Medical Condition" = 'Hypertension')""", "complex_grouping": """
**คำแนะนำสำหรับการจัดกลุ่มที่ซับซ้อน:**
- ใช้ subquery แบบ correlated สำหรับค่าสูงสุด/ต่ำสุดในแต่ละกลุ่ม
- ใช้ HAVING เพื่อกรองข้อมูลที่จัดกลุ่มแล้ว
- แสดงคอลัมน์ที่จัดกลุ่มและผลลัพธ์การคำนวณ
- ใช้ alias เพื่อความชัดเจน
- ระบุเงื่อนไขเพิ่มเติมใน WHERE หรือ HAVING
- ใช้ alias ในทุกส่วน: SELECT p1.Hospital, p1.Name, p1.Age FROM patients p1 WHERE p1.Age = (SELECT MAX(p2.Age) FROM patients p2 WHERE p2.Hospital = p1.Hospital)""", "basic_select": """
**คำแนะนำสำหรับการดึงข้อมูลพื้นฐาน:**
- ใช้ SELECT เพื่อระบุคอลัมน์ที่ต้องการ
- ใช้ FROM เพื่อระบุตาราง
- ใช้ WHERE เพื่อกรองข้อมูล
- ระบุคอลัมน์ที่ต้องการแทนการใช้ SELECT *
- ใช้ alias เมื่อต้องการความชัดเจน
- ใช้ alias ในทุกส่วน: SELECT p.Name, p.Age, p.Hospital FROM patients p WHERE p.Age > 50""" } return type_instructions.get(question_type, type_instructions["basic_select"]) # ตัวอย่างการใช้งาน
if __name__ == "__main__": builder = EnhancedPromptBuilder() # ตัวอย่างคำถาม test_questions = [ "แสดงจำนวนผู้ป่วยแต่ละโรงพยาบาล", "หาค่าใช้จ่ายเฉลี่ยของผู้ป่วยแต่ละโรค", "ผู้ป่วยที่มีอายุมากที่สุดในแต่ละโรงพยาบาลชื่ออะไร", "แสดงผู้ป่วยที่มีค่าใช้จ่ายมากกว่า 1000 บาท" ] for question in test_questions: print(f"\n{'='*60}") print(f"คำถาม: {question}") print(f"{'='*60}") # สร้าง enhanced prompt enhanced_prompt = builder.build_enhanced_prompt(question, "Schema information here...") # แสดง prompt (ตัดส่วนท้ายออกเพื่อความกระชับ) print(enhanced_prompt[:500] + "...") # แสดงประเภทของคำถาม question_type = builder._analyze_question_type(question) print(f"\nประเภทของคำถาม: {question_type}") # แสดงความรู้ที่เกี่ยวข้อง relevant_knowledge = builder._get_relevant_knowledge(question, question_type) print(f"\nความรู้ที่เกี่ยวข้อง: {len(relevant_knowledge)} ข้อ") for i, knowledge in enumerate(relevant_knowledge[:3], 1): print(f" {i}. {knowledge[:80]}...")
