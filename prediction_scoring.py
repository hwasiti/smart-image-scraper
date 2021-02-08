import pandas as pd
import os
import json
from visionAPI import vision

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
### fn = 'output' + os.sep + 'df_100_per_search.json'
### df_100.to_json(fn)
### print('Pandas DataFrame of the 1st 100 images from each search term has been saved in: ' + fn)

### fn = 'output' + os.sep + 'df_all.json'
### df.to_json(fn)
### print('Pandas DataFrame of ALL images of all search term has been saved in: '  + fn)

# Make DL predictions using Google Cloud Vision API.
# Try the API: https://cloud.google.com/vision/docs/drag-and-drop
# To work within the free tier of Google Cloud Vision API: we will predict
# only for df_100.json (the 1st 100 images from each search term).
# Maximum supported image file size is 20 MB. # So we should repeat predictions of those images after down-sizing
# those downloaded images.
# Also, Note that the Vision API imposes a 10MB JSON request size limit;
# larger files should be hosted on Cloud Storage or on the web, rather than being passed as base64-encoded content in
# the JSON itself.

# Steps from: https://github.com/philipperemy/vision-api
# 1. Browse here: https://cloud.google.com/vision/
# 2. Create a Google account. You might be lucky and get $300 of free usage.
# 3. Activate the Vision API with the free trial.
# 4. Browse here: https://console.cloud.google.com/apis/credentials
# 5. Go to credentials tab and create a new one. Create Credentials > API Key.
# 6. save the KEY in the credentials.json file
# example: {"FLICKER_KEY":"YOUR_API_KEY", "FLICKER_SECRET":"YOUR_API_SECRET", "GOOGLE_VISION_KEY":"YOUR_API_KEY"}

resp = vision.request_vision_api('images' + os.sep + 'flickr_monkey_cage-0.jpg', b64=False)
dict_google_response = json.loads(resp.content)
str_to_write = json.dumps(dict_google_response, indent=4)

for item in dict_google_response['responses'][0]['labelAnnotations']:
    print(item['description'] + ": " + str(item['score']))

print(str_to_write)




# Save prediction scores in dataframes





# TODO: NEED to Encrypting sensitive data in df then deleting df1 and df2 from the storage (comment out the delete step)
# TODO: Save df_100 and df to disk
