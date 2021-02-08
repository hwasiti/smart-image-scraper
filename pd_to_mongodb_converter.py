import os
from pymongo import MongoClient
import pandas as pd

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

# TODO: Here or in prev Script: NEED to Encrypting sensitive data in df then deleting df1 and df2 from the storage (comment out the delete step)

# Insert a Pandas dataframe to MongoDB
myclient = MongoClient("mongodb://localhost:27017/")
mydb = myclient["mydatabase"]

mongo_data = df_100_per_search_with_PREDS.to_dict(orient='records')  # Here's our added param..

mycol = mydb["scraped_metadata"]

mycol.insert_many(mongo_data)
