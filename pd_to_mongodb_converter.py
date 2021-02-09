import os
from pymongo import MongoClient
import pandas as pd
from cryptography.fernet import Fernet

# Reading previously saved Pandas DataFrames
fn = 'output' + os.sep + 'df_100_per_search_with_PREDS.json'
df_100_per_search_with_PREDS = pd.read_json(open(fn, "r", encoding="utf-8-sig"))

fn = 'output' + os.sep + 'df_all.json'
df_all = pd.read_json(open(fn, "r", encoding="utf-8-sig"))

# Moving filename column as the 1st column if it is not already the 1st column
df_100_per_search_with_PREDS.set_index("filename", inplace=True)
df_100_per_search_with_PREDS.reset_index(inplace=True)
df_all.set_index("filename", inplace=True)
df_all.reset_index(inplace=True)

# Encrypt sensitive fields: 'owner name', 'path alias', 'owner', 'exif data'
key = Fernet.generate_key()  # store in a secure location. You will needed when you decrypt the DB
print("Key:", key.decode())
with open('KEY_DB.txt', 'w') as file:
    file.write(key.decode())

# Read the key from the stored key file
with open('KEY_DB.txt', 'r') as file:
    key = file.read().encode()
print("Key:", key.decode())

def encrypt(message: bytes, key: bytes) -> bytes:
    return Fernet(key).encrypt(message)


def decrypt(token: bytes, key: bytes) -> bytes:
    return Fernet(key).decrypt(token)


message = 'John Doe'
token = encrypt(message.encode(), key)
print(token)

message = decrypt(token, key).decode()
print(message)

pass
# Insert a Pandas dataframe to MongoDB
myclient = MongoClient("mongodb://localhost:27017/")
mydb_100 = myclient["scraped_data_100"]
mydb_all = myclient["scraped_data_all"]

mongo_data_100 = df_100_per_search_with_PREDS.to_dict(orient='records')
mongo_data_all = df_all.to_dict(orient='records')

mycol_100 = mydb_100["scraped_metadata_100_per_search_with_PREDS"]
mycol_100.insert_many(mongo_data_100)

mycol_all = mydb_all["scraped_data_all"]
mycol_all.insert_many(mongo_data_all)
