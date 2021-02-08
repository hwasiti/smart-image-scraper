import pandas as pd
import os
import json
from visionAPI import vision
import warnings
warnings.filterwarnings("ignore")

# Merging DatFrames of your previously scraped search terms
# You should change the file names of df1_100, df2_100, df1 and df2
# And you can add more if you have more than 2 search scraping
df1_100 = pd.read_json(open('output' + os.sep + 'flickr_monkey_wild_df_100.json', "r", encoding="utf-8-sig"))
df2_100 = pd.read_json(open('output' + os.sep + 'flickr_monkey_cage_df_100.json', "r", encoding="utf-8-sig"))

df1 = pd.read_json(open('output' + os.sep + 'flickr_monkey_wild_df.json', "r", encoding="utf-8-sig"))
df2 = pd.read_json(open('output' + os.sep + 'flickr_monkey_cage_df.json', "r", encoding="utf-8-sig"))

df_100 = pd.concat([df1_100, df2_100], ignore_index=True)
df = pd.concat([df1, df2], ignore_index=True)

# Saving merged DatFrames
fn = 'output' + os.sep + 'df_100_per_search.json'
df_100.to_json(fn)
print('Pandas DataFrame of the 1st 100 images from each search term has been saved in: ' + fn)

fn = 'output' + os.sep + 'df_all.json'
df.to_json(fn)
print('Pandas DataFrame of ALL images of all search term has been saved in: '  + fn)

# Make DL predictions using Google Cloud Vision API.
# Try the API: https://cloud.google.com/vision/docs/drag-and-drop
# To work within the free tier of Google Cloud Vision API: we will predict
# only for df_100 DataFrame items (the 1st 100 images from each search term).

# Steps from: https://github.com/philipperemy/vision-api
# 1. Browse here: https://cloud.google.com/vision/
# 2. Create a Google account. You might be lucky and get $300 of free usage.
# 3. Activate the Vision API with the free trial.
# 4. Browse here: https://console.cloud.google.com/apis/credentials
# 5. Go to credentials tab and create a new one. Create Credentials > API Key.
# 6. save the KEY in the credentials.json file
# example: {"FLICKER_KEY":"YOUR_API_KEY", "FLICKER_SECRET":"YOUR_API_SECRET", "GOOGLE_VISION_KEY":"YOUR_API_KEY"}

# ApI response will be with all labels with score_threshold above 0.5
# There seems no way to decrease this threshold:
# https://cloud.google.com/vision/docs/reference/rest/v1/AnnotateImageRequest

labels_related = {'monkey': ['monkey', 'macaque', 'primate', 'mandrill', 'gibbon',
                             'colobines', 'titi', 'langur'],
                  'cage': ['cage', 'fence', 'fencing', 'mesh', 'shelter', 'net']}


df_100.set_index("filename", inplace=True)

for index, row in df_100.iterrows(): # check images one by one
    resp = vision.request_vision_api('images' + os.sep + row.name , b64=False)  # row.name is the filename
    dict_google_response = json.loads(resp.content)

    label_found = False
    print()
    print('Searching the label MONKEY or any related label for the image: ' + row.name)
    for item in dict_google_response['responses'][0]['labelAnnotations']: # check Google api responded labels
        print(item['description'] + ": " + str(item['score']))
        if len([i for i in labels_related['monkey'] if
                item['description'].lower() in i or i in item['description'].lower()]) > 0: # found a monkey label
            print('FOUND ' + item['description'].lower() + ": " + str(item['score']))
            df_100.loc[row.name, 'species prediction score'] = item['score']
            label_found = True
            break
    if not label_found:
        df_100.loc[row.name, 'species prediction score'] = 0.49  # Google vision will not return scores < 0.5
        print('NOT FOUND any label. Setting the score to 0.49 (below the Google Vision minimum score)')

    label_found = False
    print()
    print('Searching the label CAGE or any related label for the image: ' + row.name)
    for item in dict_google_response['responses'][0]['labelAnnotations']:
        print(item['description'] + ": " + str(item['score']))
        if len([i for i in labels_related['cage'] if
                item['description'].lower() in i or i in item['description'].lower()]) > 0:  # found a cage label
            print('FOUND ' + item['description'].lower() + ": " + str(item['score']))
            df_100.loc[row.name, 'cage prediction score'] = item['score']
            label_found = True
            break
    if not label_found:
        df_100.loc[row.name, 'cage prediction score'] = 0.49  # Google vision will not return scores < 0.5
        print('NOT FOUND any label. Setting the score to 0.49 (below the Google Vision minimum score)')

df_100.reset_index(inplace=True)

# Saving merged DatFrames
fn = 'output' + os.sep + 'df_100_per_search.json'
df_100.to_json(fn)
print('Pandas DataFrame of the 1st 100 images from each search term has been saved in: ' + fn)

fn = 'output' + os.sep + 'df_all.json'
df.to_json(fn)
print('Pandas DataFrame of ALL images of all search term has been saved in: '  + fn)

# Save prediction scores in dataframes
fn = 'output' + os.sep + 'df_100_per_search_with_PREDS.json'
df_100.to_json(fn)
print('Pandas DataFrame of the 1st 100 images from each search term WITH GOOGLE DL predictions has been saved in: ' + fn)
