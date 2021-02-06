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
