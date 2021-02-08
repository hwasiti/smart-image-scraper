from pymongo import MongoClient


fn = 'df_100.json'
df.to_json(fn)
print('All dataframes combined and saved in:' + fn)



# Insert a Pandas dataframe to MongoDB
myclient = MongoClient()  # Remember your uri string should be something like: "mongodb://localhost:27017/"
mydb = myclient["mydatabase"]

mongo_data = df.to_dict(orient='records')  # Here's our added param..

mydb.insert_many(mongo_data)
