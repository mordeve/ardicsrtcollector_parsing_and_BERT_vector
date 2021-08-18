import sqlite3
import numpy as np
import io

db_new = "./databases/deneme3_with_bert.db"

con = sqlite3.connect(db_new)
cur = con.cursor()

cur.execute("select Bert_Vector from google_responses_raw")
data = cur.fetchall()

print(f"Length of data: {len(data)}")

print("sample reading of bert_vector from google_responses_raw ->")
print()
for row in data:
    A=str(row[0])
    A=A.replace("[", "")
    A=A.replace("]", "")
    AA=np.fromstring(A, sep = ' ')
    print(AA)
    break
