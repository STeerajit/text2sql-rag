import pandas as pd
import sqlite3 df = pd.read_csv("data/healthcare_dataset_with_id.csv")
conn = sqlite3.connect("data/healthcare.db")
df.to_sql("patients", conn, if_exists="replace", index=False)
conn.close()
