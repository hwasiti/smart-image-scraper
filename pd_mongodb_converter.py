from pymongo import MongoClient
import pandas as pd

df1 = pd.read_json('flickr_monkey_wild_df_100.json')
df2 = pd.read_json('flickr_monkey_cage_df_100.json')

df = pd.concat([df1, df2], ignore_index=True)

fn = 'df_all.json'
df.to_json(fn)
print('All dataframes combined and saved in:' + fn)

# Insert a Pandas dataframe to MongoDB
myclient = MongoClient()  # Remember your uri string like: "mongodb://localhost:27017/"
mydb = myclient["mydatabase"]

mongo_data = df.to_dict(orient='records')  # Here's our added param..

mydb.insert_many(mongo_data)
