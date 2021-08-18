import numpy as np
import sqlite3
from sentence_transformers import SentenceTransformer
import io
import os

db_old          = "./databases/deneme3.db"

db_old_splitted = db_old.split(".db")[0]
db_new          = db_old_splitted + "_with_bert.db"

if os.path.isfile(db_new):
    print(f"The {db_new} is already exists.")
    if input("Would you want to delete and write again? (Y/N) ").lower() == "y":
        os.remove(db_new)
    else:
        print("Database is NOT deleted.")


con_old = sqlite3.connect(db_old)
cursor_old = con_old.cursor()

query = "SELECT * FROM google_responses_raw"
cursor_old.execute(query)
datas_from_db = cursor_old.fetchall()

cursor_old.close()

conn   = sqlite3.connect(db_new)
cursor = conn.cursor()

model = SentenceTransformer('dbmdz/bert-base-turkish-cased')

# Create TABLE if not exists
cursor.execute("CREATE TABLE if not exists google_responses_raw(filename text, \
                    video_id text, response text, Bert_Vector text NOT_NULL)")

for i, data in enumerate(datas_from_db):
    file_path = data[0]
    vid_id = data[1]
    

    response = data[2].encode().decode('unicode-escape').encode('latin1').decode('utf-8')
    if len(response) == 0:
        continue
    sentence = response.split("transcript:")[-1].split("\n")[0].strip().replace('"', "")
    sentence_embeddings = model.encode(sentence)
    cursor.execute("INSERT INTO google_responses_raw VALUES (?,?,?,?)", \
        (file_path, vid_id, response, str(np.array(sentence_embeddings)), ))
    print(f"inserted data: {i+1} ", end="\r")


conn.commit()
conn.close()

