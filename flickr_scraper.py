import os
import pandas as pd
from datetime import datetime
import time
import argparse
import json
from flickrapi import FlickrAPI
from utilities.tools import download_img, reverse_geocode

with open('credentials.json') as file:
    credentials = json.load(file)

KEY = credentials['KEY']
SECRET = credentials['SECRET']


def download_photos(search_query, n=30, download=False, bbox=None):
    t = time.time()
    fr = FlickrAPI(KEY, SECRET)

    if n < 500:
        per_page = n
    else:
        per_page = 500

    # bbox should be: minimum_longitude, minimum_latitude, maximum_longitude, maximum_latitude
    if bbox is not None and len(bbox) == 4:
        bbox = ','.join(bbox)

    # API library details: https://stuvel.eu/flickrapi-doc/7-util.html#walking-through-all-photos-in-a-set
    # http://www.flickr.com/services/api/flickr.photos.search.html
    # Explorer of search API: https://www.flickr.com/services/api/explore/?method=flickr.photos.search
    extras = 'description,date_upload,date_taken,owner_name,geo,tags,machine_tags,o_dims,views,media,path_alias,url_o'

    photos = fr.walk(text=search_query,
                     sort='relevance',
                     bbox=bbox,
                     extras=extras,
                     per_page=per_page)

    if download:
        # image save folder
        dir = os.getcwd() + os.sep + 'images' + os.sep
        if not os.path.exists(dir):
            os.makedirs(dir)

    filenames, date_of_downloads, time_of_downloads, search_terms, links, path_aliases, titles = [], [], [], [], [], [], []
    descriptions, dates_taken, owner_names, owners, latitudes, longitudes, countries, cities = [], [], [], [], [], [], [], []
    images_tags, images_machine_tags, images_views, images_exif = [], [], [], []

    for count, photo in enumerate(photos):
        if count < n:
            link = photo.get('url_o')  # photo with the original size

            # http://www.flickr.com/services/api/flickr.photos.search.html
            if link is None:
                link = 'https://farm%s.staticflickr.com/%s/%s_%s_b.jpg' % \
                       (photo.get('farm'), photo.get('server'), photo.get('id'), photo.get('secret'))

            if download:
                suffix = os.path.basename(link).split('.')[-1]
                filename = 'images' + os.sep + 'flickr_' + search_query.replace(' ', '_') + '-' + str(
                    count) + '.' + suffix
                exif = download_img(link, filename)

            # Convert coord to country and city
            country = ''
            city = ''
            lat = float(photo.get('latitude'))
            lon = float(photo.get('longitude'))
            if lat != 0 or lon != 0:
                # flickr coordinates are available
                coords = (lat, lon) , (lat, lon) # Duplicating as a workaround for the bug in reverse_geocode package:
                # TypeError: 'int' object is not iterable
                addr = reverse_geocode(coords)
                country = addr[0]['country']
                city = addr[0]['city']
                print(addr)

            now = datetime.now()

            filenames.append(filename.split(os.sep)[-1])  # only the base file name
            date_of_downloads.append(now.strftime("%d/%m/%Y"))
            time_of_downloads.append(now.strftime("%H:%M:%S"))
            search_terms.append(search_query)
            links.append(link)
            titles.append(photo.get('title'))
            descriptions.append(photo.find('description').text)  # 'description' is a nested XML and not an attr.
            dates_taken.append(photo.get('datetaken'))
            owner_names.append(photo.get('ownername'))
            path_aliases.append(photo.get('pathalias'))
            owners.append(photo.get('owner'))
            latitudes.append(photo.get('latitude'))
            longitudes.append(photo.get('longitude'))
            countries.append(country)
            cities.append(city)
            images_tags.append(photo.get('tags'))
            images_machine_tags.append(photo.get('machine_tags'))
            images_views.append(photo.get('views'))
            images_exif.append(str(exif))

            print(f'{count + 1}/{n}: {link}')
        else:
            break

    data = list(zip(search_terms, date_of_downloads, time_of_downloads, filenames, links,
                    titles, descriptions, dates_taken, owner_names, path_aliases, owners, latitudes,
                    longitudes, countries, cities, images_machine_tags, images_views, images_tags, images_exif,
                    [1.0] * len(search_terms), [1.0] * len(search_terms)))  # prediction score at the moment is 100%

    columns = ['search term', 'date of download', 'time of download', 'filename', 'link',
               'title', 'description', 'date taken', 'owner name', 'path alias', 'owner',
               'latitude', 'longitude', 'country', 'city', 'machine tags', 'views', 'tags',
               'exif data', 'species prediction score', 'cage prediction score']

    df = pd.DataFrame(data, columns=columns)

    print(f'Finished downloading in {time.time() - t} sec.')
    return df


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--search', '-s', dest='search', type=str, default='monkey cage', help='search term')
    parser.add_argument('--number', '-n', dest='n', type=int, default=1000, help='number of images to download')
    parser.add_argument('--download', '-d', dest='download', type=bool, default=True,
                        help='download images (True or False)')
    parser.add_argument('--bbox', '-b', dest='bbox', required=False,
                        help='Geographical bounding box to search in. Should be separated by spaces like: '
                             'minimum_longitude minimum_latitude maximum_longitude maximum_latitude. '
                             ' Longitude has a range of -180 to 180 , latitude of -90 to 90')
    args = parser.parse_args()

    # Check flickr API key available
    fr_key_help = 'https://www.flickr.com/services/apps/create/apply'
    assert KEY and SECRET, f'Get your Flickr API key and Secret. To apply visit {fr_key_help}. Save them in a file ' \
                           f'named: credentials.json as {"KEY":"YOUR_API_KEY", "SECRET":"YOUR_API_SECRET"}'
    try:
        bbox = args.bbox.split(' ')
    except Exception as e:
        bbox = None
        print('Geographical bounding box unidentified -> bbox will be ignored!')

    if bbox and len(bbox) != 4:
        bbox = None
        print('Geographical bounding box unidentified -> bbox will be ignored!')

    if bbox:
        print('Searching within the Geographical bounding box: min_long, min_lat, max_long, max_lat', bbox)

    pd_data = download_photos(search_query=args.search,  # search term
                              n=args.n,  # max number of images
                              download=args.download,  # download images
                              bbox=bbox)  # search within certain geographical limit

    # Saving the csv with special character separator like ζ works well with even non-english commonly used text
    print()
    fn = 'output' + os.sep + 'flickr_' + args.search.replace(' ', '_') + '_df.csv'
    pd_data.to_csv(fn, encoding='utf-8-sig', sep='ζ')
    print('Image data saved in: ' + fn)

    fn = 'output' + os.sep + 'flickr_' + args.search.replace(' ', '_') + '_df.json'
    pd_data.to_json(fn)
    print('Image data saved in: ' + fn)

    fn = 'output' + os.sep + 'flickr_' + args.search.replace(' ', '_') + '_df_100.json'
    pd_data.head(100).to_json(fn)
    print('First 100 Image data saved in: ' + fn)
