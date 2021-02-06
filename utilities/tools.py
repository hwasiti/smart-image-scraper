import os
import requests
from PIL import Image
from pathlib import Path


def download_img(uri, filename):

    with open(filename, 'wb') as file:
        file.write(requests.get(uri, timeout=10).content)

    # Add suffix
        if Path(filename).suffix == '':
            filename_old = filename
            filename += '.' + Image.open(filename).format.lower()
            os.rename(filename_old, filename)
