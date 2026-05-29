import argparse
import pandas as pd
from text2sql_rag.retrieval import Retriever # Load schema from CSV
df = pd.read_csv("data/healthcare_dataset_with_id.csv") column_desc = { "id": "รหัสผู้ป่วย", "Name": "ชื่อผู้ป่วย", "Age": "อายุ", "Gender": "เพศ", "Blood Type": "กรุ๊ปเลือด", "Medical Condition": "โรคหรืออาการ", "Date of Admission": "วันที่เข้ารักษา", "Doctor": "แพทย์ผู้ดูแล", "Hospital": "โรงพยาบาล", "Insurance Provider": "บริษัทประกัน", "Billing Amount": "ค่าใช้จ่าย", "Room Number": "หมายเลขห้อง", "Admission Type": "ประเภทการรับเข้า", "Discharge Date": "วันที่ออกจากโรงพยาบาล", "Medication": "ยาที่ได้รับ", "Test Results": "ผลตรวจ"
} #mapping
column_mapping = [f"{col} = {column_desc.get(col, col)}" for col in df.columns] #sample row
sample_row = df.iloc[0]
sample_row_text = "ตัวอย่างข้อมูล: " + ", ".join([f"{col}={sample_row[col]}" for col in df.columns]) schema_lines = [f"คอลัมน์: {col} ({str(dtype)}) - {column_desc.get(col, '')}" for col, dtype in zip(df.columns, df.dtypes)]
schema_text = ["ตาราง: patients"] + schema_lines + ["\nMapping ชื่อคอลัมน์:"] + column_mapping + ["\n" + sample_row_text] def main(): parser = argparse.ArgumentParser(description="สร้างเวกเตอร์สโตร์ของ schema สำหรับ embedder ที่ระบุ") parser.add_argument("--embedder", type=str, default=None, help="ชื่อโมเดลฝังตัว (เช่น sentence-transformers/all-MiniLM-L6-v2)") args = parser.parse_args() retriever = Retriever(embedder_model=args.embedder) retriever.add_schema(schema_text) print(f"complete (embedder={retriever.embedder.model_name})") if __name__ == "__main__": main()
