from pymongo import MongoClient
import pandas as pd
from datetime import datetime
import os
from user_manage.user_data import username
TOPIK = username()

MONGO_URI = 'mongodb://localhost:27017/'  # Update with your MongoDB URI
DATABASE_NAME = 'E2E_TESTING'
DATA_COLLECTION_NAME = 'data_scrape'

# Create MongoDB client
client_db = MongoClient(MONGO_URI)
db = client_db[DATABASE_NAME]
topik_collection = db[TOPIK]

def news_endpoint():
    document = topik_collection.find_one({'_id': 'news'})

    data = document['data'] if document else []
    # Convert to DataFrame
    df = pd.DataFrame(data)
    sentiment_counts = df['sentimen'].value_counts(normalize=True) * 100
    pie_sentiment = {
        "labels": sentiment_counts.index.tolist(),
        "values": sentiment_counts.values.tolist()
    }

    df_pie = pd.DataFrame(pie_sentiment)
    df_pie['keyword'] = TOPIK
    df_pie['createdAt'] = datetime.today().strftime('%Y-%m-%d')

    buzzer_counts = df['buzzer'].value_counts(normalize=True) * 100
    pie_buzz = {
        "labels": buzzer_counts.index.tolist(),
        "values": buzzer_counts.values.tolist()
    }

    df_piebuz = pd.DataFrame(pie_buzz)
    df_piebuz['keyword'] = TOPIK
    df_piebuz['createdAt'] = datetime.today().strftime('%Y-%m-%d')


    result = {'pie_sentiment' : df_pie.to_dict('records'),
            'pie_buzz' : df_piebuz.to_dict('records')}
    
    return result
