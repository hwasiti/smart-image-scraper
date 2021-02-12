import os
import streamlit as st
import pymongo
import pandas as pd
from cryptography.fernet import Fernet
from PIL import Image
from math import floor, ceil


def decrypt(token: bytes, key: bytes) -> bytes:
    return Fernet(key).decrypt(token)


def read_encrypt_key():
    # Read the encryption key from the stored key file
    try:
        with open('KEY_DB.txt', 'r') as file:
            key = file.read().encode()
    except FileNotFoundError:
        print("You should create a file <KEY_DB.txt> contains the encryption key. Please re-run this script after "
              "copying the encryption key and saving this file in the project root directory.")
        exit()
    return key

def read_db_password():
    # Read the password of the online Mongo Atlas DB from the stored password file
    try:
        with open('PASSW_DB.txt', 'r') as file:
            passw = file.read().replace('\n', '')
    except FileNotFoundError:
        print(
            "You should create a file <PASSW_DB.txt> contains the password to access the online Mongo Atlas DB. Please "
            "re-run this script after saving this file in the project root directory.")
        exit()
    return passw


def load_db(passw, key):
    # Read from MongoDB to Pandas
    lnk = "mongodb+srv://hwasiti:" + passw + "@cluster0.pxlzj.mongodb.net/scraped_data_100_encrypted?retryWrites=true&w=majority"
    client = pymongo.MongoClient(lnk)
    db = client.scraped_data_100_encrypted
    collection = db.scraped_metadata_100_per_search_with_PREDS_encrypted
    df = pd.DataFrame(list(collection.find()))

    print('Database read successfully...')

    # Decrypt columns with the sensitive info
    df_decrypted = df.copy()
    cols_to_decrypt = ['owner name', 'path alias', 'owner', 'exif data']

    for index, row in df_decrypted.iterrows():
        for col in cols_to_decrypt:
            data = df_decrypted.loc[row.name, col]
            df_decrypted.loc[row.name, col] = decrypt(data.encode(), key).decode()
    return df_decrypted

def load_db_from_pd():
    df_decrypted = pd.read_json(open('output' + os.sep + 'df_100_per_search.json'))
    return df_decrypted

def show_images(df_filtered, grid_size, page, captions):

    n_grid_images = grid_size * grid_size  # number of images in a page
    if page * n_grid_images <= len(df_filtered):  # if this page will NOT exceed the number of possible images to be shown
        # first_image_n = n_grid_images * (page - 1)
        # last_img_n = n_grid_images * page
        last_y = ceil(n_grid_images / grid_size)
        n_images_to_show = n_grid_images
    else:
        # first_image_n = n_grid_images * (page - 1)
        last_img_n = len(df_filtered)
        last_y = ceil((last_img_n - (page-1) * n_grid_images) / grid_size)
        n_images_to_show = last_img_n - (page - 1) * n_grid_images

    for y in range(last_y):
        cols = st.beta_columns(grid_size)
        last_x = n_images_to_show - (last_y - 1) * grid_size
        for x in range(last_x):
            img_name = df_filtered.filename[(page-1) * n_grid_images + y * grid_size + x]
            fn = "images_100" + os.sep + img_name
            image = Image.open(fn)
            if image.mode in ("RGBA", "P"):
                image = image.convert('RGB')  # discard the alpha channel
            cols[x].image(image, use_column_width=True)
            for item in captions:
                cols[x].markdown('**' + item + '**: ' + df_filtered[(df_filtered.filename == img_name)][item].to_string(index=False))
            cols[x].dataframe(df_filtered[(df_filtered.filename == img_name)])



def main():
    """Main function. Run this to run the app"""
    st.set_page_config(
        page_title="Smart Image Scraper",
        page_icon="🧊",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    st.title("Smart Image Scraper Results")
    st.write("")

    st.sidebar.title("Settings")
    st.sidebar.header("Grid size")
    grid_size = st.sidebar.slider('', 1, 8, 2)

    columns = ['search term', 'date of download', 'time of download', 'filename', 'link',
                'title', 'description', 'date taken', 'owner name', 'path alias', 'owner',
                'latitude', 'longitude', 'country', 'city', 'machine tags', 'views', 'tags',
                'exif data', 'species prediction score', 'cage prediction score']

    st.sidebar.header("Search term")
    terms_selected = st.sidebar.multiselect('', ['monkey wild', 'monkey cage'], ['monkey wild', 'monkey cage'])

    st.sidebar.header("Metadata")

    captions = st.sidebar.multiselect(
        'Select what to show below images. Other info will be shown as a table below. For long data, just hover the '
        'mouse over it, a tool-tip will show all the cell content.',
        columns)  # , ['search term', 'species prediction score', 'cage prediction score']) # defaults

    st.sidebar.header("DL prediction of Monkey")
    pred_thr_monkey_low, pred_thr_monkey_high = st.sidebar.slider("1.0 = Highly confident", 0.0, 1.0, (0.45, 1.0), 0.05,
                                                                  key='11') # any rand unique key

    st.sidebar.header("DL prediction of Cage")
    pred_thr_cage_low, pred_thr_cage_high = st.sidebar.slider("", 0.0, 1.0, (0.45, 1.0), 0.05,
                                                               key='12')

    df_decrypted = load_db_from_pd()

    st.sidebar.header("Country")
    countries = df_decrypted.country.unique().tolist()

    countries_selected = st.sidebar.multiselect('', countries, countries)
    view_max = df_decrypted.views.max().astype(int).item()
    view_min = df_decrypted.views.min().astype(int).item()
    st.sidebar.header("View Count")

    view_low, view_high = st.sidebar.slider("", view_min, view_max, (view_min, view_max))

    # filtering the DB
    df_filtered = df_decrypted.loc[(df_decrypted['species prediction score'] >= pred_thr_monkey_low)
                                   & (df_decrypted['cage prediction score'] >= pred_thr_cage_low)
                                   & (df_decrypted['species prediction score'] <= pred_thr_monkey_high)
                                   & (df_decrypted['cage prediction score'] <= pred_thr_cage_high)
                                   & (df_decrypted['views'].astype(int) <= view_high)
                                   & (df_decrypted['views'].astype(int) >= view_low)
                                   & (df_decrypted['search term'].isin(terms_selected))
                                   & (df_decrypted['country'].isin(countries_selected))
                                   ]

    df_filtered.reset_index(drop=True, inplace=True)

    st.markdown('**Total images = ** ' + str(len(df_filtered)))

    col1, col2, col3, col4, col5, col6, col7, col8, col9, col10, col11, col12, col13 = st.beta_columns((1, 1, 1, 1, 1, 1, 3, 1, 1, 1, 1, 1, 1))
    total_pages = ceil(len(df_filtered)/(grid_size*grid_size))
    if total_pages == 0:
        total_pages = 1
    pages = ['Page '+str(i+1) for i in range(total_pages)]  # number of pages of the gallery

    page = col7.selectbox('', pages)
    current_page = int(page[5:])

    if df_filtered is None:
        st.write("No results to show")
    elif len(df_filtered) == 0:
        st.write("No results to show")
    else:
        show_images(df_filtered, grid_size, current_page, captions)

    # with st.beta_container():
    #     st.image(image1, width = 500)
    #
    # with st.beta_container():
    #     st.image(image2, width = 500)
    #
    # with st.beta_container():
    #     st.image(image3, width=500)
    #
    # with st.beta_container():
    #     st.image(image4, width=500)






    # key = read_encrypt_key()
    # passw = read_db_password()
    # df_decrypted = load_db(passw, key)


main()

print()
