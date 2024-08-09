import os
import numpy as np
import pandas as pd
from pymongo import MongoClient
import json
from datetime import datetime

def save_data_to_mongo(data_json, database_name, collection_name, mongo_url='mongodb://localhost:27017/', document_id='news'):
    """
    Save data to MongoDB collection, avoiding duplicates based on the 'url' field.
    If 'url' exists but with a new 'label_owner', add the new 'label_owner' to the list.

    :param data_json: List of dictionaries containing the data to be saved.
    :param mongo_uri: MongoDB URI.
    :param database_name: Name of the database.
    :param collection_name: Name of the collection.
    :param document_id: The document ID to update or insert data.
    """
    client_db = MongoClient(mongo_url)
    db = client_db[database_name]
    data_collection = db[collection_name]

    existing_document = data_collection.find_one({'_id': document_id})

    if existing_document and 'data' in existing_document:
        existing_data = existing_document['data']
        existing_urls = {item['url'] for item in existing_data}

        for new_item in data_json:
            if new_item['url'] in existing_urls:
                for existing_item in existing_data:
                    if existing_item['url'] == new_item['url']:
                        if new_item['label_owner'] not in existing_item['label_owner']:
                            existing_item['label_owner'].append(new_item['label_owner'])
                        existing_item['label_timestamp'].append(new_item['label_timestamp'])
                        break
            else:
                new_item['label_owner'] = [new_item['label_owner']]
                new_item['label_timestamp'] = [new_item['label_timestamp']]
                existing_data.append(new_item)

        data_collection.update_one(
            {'_id': document_id},
            {'$set': {'data': existing_data}}
        )
    else:
        for new_item in data_json:
            new_item['label_owner'] = [new_item['label_owner']]
            new_item['label_timestamp'] = [new_item['label_timestamp']]
        data_collection.update_one(
            {'_id': document_id},
            {'$set': {'data': data_json}},
            upsert=True
        )

    print("Data News Saved!")

MONGO_URI = 'mongodb://localhost:27017/'  # Update with your MongoDB URI
DATABASE_NAME = 'E2E'
DATA_COLLECTION_NAME = 'data_scrape'

# Create MongoDB client
client_db = MongoClient(MONGO_URI)
db = client_db[DATABASE_NAME]
data_collect = db[DATA_COLLECTION_NAME]

TOPIK = 'instansi A'

path_folder = r'C:\Users\Win10\End-to-End-Testing-main\datacrawl'
datas = os.listdir(path_folder)
path_news = os.path.join(path_folder, datas[0])

with open(path_news, 'r') as f:
    news_dat = json.load(f)

news_df = pd.DataFrame(news_dat['articles']).head(3)

news_df['label_owner'] = TOPIK
news_df['label_timestamp'] = datetime.now().isoformat()
data_dict = news_df.to_dict("records")

save_data_to_mongo(data_dict, DATABASE_NAME, DATA_COLLECTION_NAME)
