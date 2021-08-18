import sqlite3
import numpy as np
import io

db_new = "./databases/deneme3_with_bert.db"

def convert_array(text):
    out = io.BytesIO(text)
    out.seek(0)
    return np.load(out)

# Converts TEXT to np.array when selecting
sqlite3.register_converter("array", convert_array)

con = sqlite3.connect(db_new, detect_types=sqlite3.PARSE_DECLTYPES)
cur = con.cursor()

cur.execute("select bert_vector from google_responses_raw")
data = cur.fetchall()

print(f"Length of data: {len(data)}")

print("sample reading of bert_vector from google_responses_raw ->")
print()
for row in data:
    print(row)
    break
