# Smart Image Scraper

## Installation

1. Clone the repo
2. Create an Anaconda-environment 
````python
   conda create --name YOUR_ENV_NAME python=3.7
````
or alternatively a virtual-environment

3. Install requirements
````python
pip install -r requirements.txt
````

## Usage

1. Create a Flicker account or sign-in
2. Get an API Key from: https://www.flickr.com/services/apps/create/apply
3. Create a file in the project directory named `credentials.json` and write your API key and Secret inside the file as:
```python
{"KEY":"YOUR_API_KEY", "SECRET":"YOUR_API_SECRET"}
```

## Geographical bounding box
**bbox (Optional)**

A comma-delimited list of 4 values defining the Bounding Box of the area that will be searched.

The 4 values represent the bottom-left corner of the box and the top-right corner, minimum_longitude, minimum_latitude, maximum_longitude, maximum_latitude.

Longitude has a range of -180 to 180 , latitude of -90 to 90. Defaults to -180, -90, 180, 90 if not specified.

bbox should be: _minimum_longitude, minimum_latitude, maximum_longitude, maximum_latitude_

**Please note that not all images has been uploaded with longitude and latitude metada in Flicker.** Images that has no such information are tagged with long:0 lat:0. 

Also note that this is a square bounding box which not necessarily confined to a certain country if its landscape is quite different from a square.

Converting N,S,E,W into range of -180 to 180 , latitude of -90 to 90:

N latitude = positive

N latitude = negative

E longitude = positive

W longitude = negative

**For example:**

Philippines is located between 116° 40', and 126° 34' E longitude and 4° 40' and 21° 10' N latitude

So, in order to download 10 images taken in this bounding box location use:
````python
python flicker_scraper.py -s "monkey wild" -n 10 -d True -b "116 4 127 22"
````
