import os
import pandas as pd
from datetime import datetime
import time
import argparse
import json
from flickrapi import FlickrAPI
from utilities.tools import download_img

with open('credentials.json') as file:
    credentials = json.load(file)

KEY = credentials['KEY']
SECRET = credentials['SECRET']


def download_photos(search_query, n=10, download=False):
    t = time.time()
    license = ()  # https://www.flickr.com/services/api/explore/?method=flickr.photos.licenses.getInfo
    fr = FlickrAPI(KEY, SECRET)
    if n < 500:
        per_page = n
    else:
        per_page = 500

    # API library details:
    # https://stuvel.eu/flickrapi-doc/7-util.html#walking-through-all-photos-in-a-set
    photos = fr.walk(text=search_query,
                     extras='url_o',
                     per_page=per_page,  # 1-500
                     license=license,
                     sort='relevance')

    if download:
        # image save folder
        dir = os.getcwd() + os.sep + 'images' + os.sep
        if not os.path.exists(dir):
            os.makedirs(dir)

    filenames = []
    date_of_downloads = []
    time_of_downloads = []
    search_terms = []
    links = []
    for count, photo in enumerate(photos):
        if count < n:
            try:
                link = photo.get('url_o')  # photo with the original size
                if link is None:
                    link = 'https://farm%s.staticflickr.com/%s/%s_%s_b.jpg' % \
                           (photo.get('farm'), photo.get('server'), photo.get('id'), photo.get('secret'))

                if download:
                    suffix = os.path.basename(link).split('.')[-1]
                    filename = 'images' + os.sep + search_query.replace(' ', '_') + '-' + str(count) + '.' + suffix
                    download_img(link, filename)

                now = datetime.now()
                filenames.append(filename.split(os.sep)[-1])  # only the base file name
                date_of_downloads.append(now.strftime("%d/%m/%Y"))
                time_of_downloads.append(now.strftime("%H:%M:%S"))
                search_terms.append(search_query)
                links.append(link)
                print(f'{count + 1}/{n}: {link}')
            except Exception as e:
                print(f'error in downloading item {count + 1}/{n}: {e}: {link}')
        else:
            break

    data = list(zip(search_terms, date_of_downloads, time_of_downloads, filenames, links))
    df = pd.DataFrame(data, columns=['search term',
                                     'date of download',
                                     'time of download',
                                     'filename',
                                     'link'])

    print(f'Finished downloading in {time.time() - t} sec.')
    return df


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--search', type=str, default='monkey cage', help='search term')
    parser.add_argument('--n', type=int, default=10, help='number of images to download')
    parser.add_argument('--download', type=bool, default=True, help='download images')
    args = parser.parse_args()

    # Check Flicker API key available
    fr_key_help = 'https://www.flickr.com/services/apps/create/apply'
    assert KEY and SECRET, f'Get your Flickr API key and Secret. To apply visit {fr_key_help}. Save them in a file ' \
                           f'named: credentials.json as {"KEY":"YOUR_API_KEY", "SECRET":"YOUR_API_SECRET"}'

    pd_data = download_photos(search_query=args.search,  # search term
                              n=args.n,  # max number of images
                              download=args.download)  # download images

    pd_data.to_csv(args.search + "_df.csv")
