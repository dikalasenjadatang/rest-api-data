# scraping/berita/get_news.py
import pandas as pd
from pymongo import MongoClient
import os
import json
from datetime import datetime
from user_manage.user_data import username
TOPIK = username()

#client_DB = MongoClient('mongodb://localhost:27017/')  # Ganti dengan URI MongoDB Anda
#db = client_DB['END2END_TESTING']  # Ganti dengan nama database Anda
 # Ganti dengan nama koleksi Anda
def get_news_data():
    path_folder = r'C:\laragon\www\DPR-NEW\database\datacrawl'
    datas = os.listdir(path_folder)
    path_news = os.path.join(path_folder, datas[0])

    with open(path_news, 'r') as f:
        news_dat = json.load(f)

    news_df = pd.DataFrame(news_dat['articles'])

    news_df['label_owner'] = TOPIK
    news_df['label_timestamp'] = datetime.now().isoformat()
    data_dict = news_df.to_dict("records")

    # Fetch existing data from 'news' document
    
    
    return data_dict
