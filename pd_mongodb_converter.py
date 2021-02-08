from pymongo import MongoClient
import pandas as pd
import os

df1_100 = pd.read_json(open('output' + os.sep + 'flickr_monkey_wild_df_100.json', "r", encoding="utf-8-sig"))
df2_100 = pd.read_json(open('output' + os.sep + 'flickr_monkey_cage_df_100.json', "r", encoding="utf-8-sig"))

df1 = pd.read_json(open('output' + os.sep + 'flickr_monkey_wild_df.json', "r", encoding="utf-8-sig"))
df2 = pd.read_json(open('output' + os.sep + 'flickr_monkey_cage_df.json', "r", encoding="utf-8-sig"))

df_100 = pd.concat([df1_100, df2_100], ignore_index=True)
df = pd.concat([df1, df2], ignore_index=True)

# TODO: NEED to Encrypting sensitive data in df then deleting df1 and df2 from the storage (comment out the delete step)
# TODO: Save df_100 and df to disk

fn = 'df_100.json'
df.to_json(fn)
print('All dataframes combined and saved in:' + fn)



# Insert a Pandas dataframe to MongoDB
myclient = MongoClient()  # Remember your uri string should be something like: "mongodb://localhost:27017/"
mydb = myclient["mydatabase"]

mongo_data = df.to_dict(orient='records')  # Here's our added param..

mydb.insert_many(mongo_data)
