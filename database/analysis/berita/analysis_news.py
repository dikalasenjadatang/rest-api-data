# scraping/berita/get_news.py
import pandas as pd
from pymongo import MongoClient
import os
import json
from datetime import datetime
import numpy as np
from utils.mongoSaveLoad.save_news_db import load_scrape_news


from user_manage.user_data import username
TOPIK = username()

MONGO_URI = 'mongodb://localhost:27017/'  # Update with your MongoDB URI
DATABASE_NAME = 'E2E_TESTING'
DATA_COLLECTION_NAME = 'data_scrape'

# Create MongoDB client
client_db = MongoClient(MONGO_URI)
db = client_db[DATABASE_NAME]
data_collect = db[DATA_COLLECTION_NAME]

def get_anlysis_news():
    #collection_news = db[name_collect]
    data = load_scrape_news(TOPIK)
    # Convert to DataFrame
    df = pd.DataFrame(data)
    # Nama kolom yang ingin dijatuhkan
    columns_to_drop = ['label_owner', 'label_timestamp']

    # Menjatuhkan kolom
    df = df.drop(columns=columns_to_drop)
    df['label_owner'] = TOPIK
    #df = df.query(f'label_owner == "{TOPIK}"')

    df['sentimen'] = np.random.choice(['positif', 'negatif'], size=len(df))
    df['buzzer'] = np.random.choice(['buzzer', 'not_buzzer'], size=len(df))

    data_dict = df.to_dict("records")

    return data_dict
    #return collection_news.find_one({'_id': 'news'})

def update_sentiment(data_id, new_sentiment, user):
    data = data_collect.find_one({"_id": data_id})
    if data:
        old_sentiment = data.get('sentimen', '')
        if old_sentiment != new_sentiment:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            edit_label = f"Edited by {user} {timestamp}"
            
            data_collect.update_one(
                {"_id": data_id},
                {
                    "$set": {
                        "sentimen": new_sentiment,
                        "sentiment_edit": edit_label
                    }
                }
            )
            return True
    return False

