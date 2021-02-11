import os
from pymongo import MongoClient
import pandas as pd
from pandas._testing import assert_frame_equal
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

# Run this only once to generate your encryption key file which will be stored in the project directory as
# 'KEY_DB.txt'
# Store it in a secure location. You will need it when you will decrypt the DB
# key = Fernet.generate_key()
# print("Key:", key.decode())
# with open('KEY_DB.txt', 'w') as file:
#     file.write(key.decode())

# Read the encryption key from the stored key file
try:
    with open('KEY_DB.txt', 'r') as file:
        key = file.read().encode()
except FileNotFoundError:
    print("You should create a file <KEY_DB.txt> contains the encryption key. Please re-run this script after "
          "uncommenting generating the encryption key and saving this file.")
# print("Key:", key.decode())

def encrypt(message: bytes, key: bytes) -> bytes:
    return Fernet(key).encrypt(message)


def decrypt(token: bytes, key: bytes) -> bytes:
    return Fernet(key).decrypt(token)


# Encrypt columns
df_100_per_search_with_PREDS_encrypted = df_100_per_search_with_PREDS.copy()
df_all_encrypted = df_all.copy()
cols_to_encrypt = ['owner name', 'path alias', 'owner', 'exif data']

for index, row in df_100_per_search_with_PREDS_encrypted.iterrows():
    for col in cols_to_encrypt:
        data = df_100_per_search_with_PREDS_encrypted.loc[row.name, col]
        df_100_per_search_with_PREDS_encrypted.loc[row.name, col] = encrypt(data.encode(), key).decode()

for index, row in df_all_encrypted.iterrows():
    for col in cols_to_encrypt:
        data = df_all_encrypted.loc[row.name, col]
        df_all_encrypted.loc[row.name, col] = encrypt(data.encode(), key).decode()

# Decrypt columns to check nothing lost on the way
df_100_per_search_with_PREDS_decrypted = df_100_per_search_with_PREDS_encrypted.copy()
df_all_decrypted = df_all_encrypted.copy()
cols_to_decrypted = ['owner name', 'path alias', 'owner', 'exif data']

for index, row in df_100_per_search_with_PREDS_decrypted.iterrows():
    for col in cols_to_decrypted:
        data = df_100_per_search_with_PREDS_decrypted.loc[row.name, col]
        df_100_per_search_with_PREDS_decrypted.loc[row.name, col] = decrypt(data.encode(), key).decode()

for index, row in df_all_decrypted.iterrows():
    for col in cols_to_decrypted:
        data = df_all_decrypted.loc[row.name, col]
        df_all_decrypted.loc[row.name, col] = decrypt(data.encode(), key).decode()

assert_frame_equal(df_100_per_search_with_PREDS, df_100_per_search_with_PREDS_decrypted)
assert_frame_equal(df_all, df_all_decrypted)

# Insert the Pandas dataframes to MongoDB
myclient = MongoClient("mongodb://localhost:27017/")
mydb_100_encrypted = myclient["scraped_data_100_encrypted"]
mydb_all_encrypted = myclient["scraped_data_all_encrypted"]

mongo_data_100_encrypted = df_100_per_search_with_PREDS_encrypted.to_dict(orient='records')
mongo_data_all_encrypted = df_all_encrypted.to_dict(orient='records')

mycol_100_encrypted = mydb_100_encrypted["scraped_metadata_100_per_search_with_PREDS_encrypted"]
mycol_100_encrypted.insert_many(mongo_data_100_encrypted)

mycol_all_encrypted = mydb_all_encrypted["scraped_data_all_encrypted"]
mycol_all_encrypted.insert_many(mongo_data_all_encrypted)

# Repeat the above to store not encrypted MongoDB files (just for demonstration purposes)
# Later on for security reasons, any files that did not encrypt sensitive info should be deleted
mydb_100 = myclient["scraped_data_100"]
mydb_all = myclient["scraped_data_all"]

mongo_data_100 = df_100_per_search_with_PREDS.to_dict(orient='records')
mongo_data_all = df_all.to_dict(orient='records')

mycol_100 = mydb_100["scraped_metadata_100_per_search_with_PREDS"]
mycol_100.insert_many(mongo_data_100)

mycol_all = mydb_all["scraped_data_all"]
mycol_all.insert_many(mongo_data_all)

print('Finished saving MongoDB files.')
