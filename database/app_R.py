from flask import Flask, jsonify
from flask import request
from pymongo import MongoClient
import pandas as pd
from scraping.berita.get_news import get_news_data
from analysis.berita.analysis_news import get_anlysis_news, update_sentiment

# save mongo
from utils.mongoSaveLoad.save_news_db import save_scrape_news, save_analyze_news
from utils.mongoSaveLoad.save_endpoint_mdb import save_endpoint_MDB

# generate endpoint
from endpoints.data.news_ep import news_endpoint

from user_manage.user_data import username
TOPIK = username()


app = Flask(__name__)

# MongoDB configuration
MONGO_URI = 'mongodb://localhost:27017/'  # Update with your MongoDB URI
DATABASE_NAME = 'E2E_TESTING'
#TOPIK = 'INSTANSIB'
DATA_COLLECTION_NAME = 'data_scrape'
#PIE_CHART_COLLECTION_NAME = 'analisis-result'

# Create MongoDB client
client_db = MongoClient(MONGO_URI)
db = client_db[DATABASE_NAME]
data_collection = db[DATA_COLLECTION_NAME]
#pie_chart_collection = db[PIE_CHART_COLLECTION_NAME]

# ======== Srape and Saved to MongoDB =================
# ---------- NEWS -----------------
@app.route('/data', methods=['GET'])
def get_and_save_news():
    data_json = get_news_data()
    #print(pd.DataFrame(data_json))

    save_scrape_news(data_json, DATA_COLLECTION_NAME)
    return jsonify(data_json)


# ======== Analyze and Saved to MongoDB =================
@app.route('/analyze', methods=['POST'])
def analyze_news():
    """Compute pie chart data, save it to MongoDB, and return it."""
    
    # Terima data yang akan diubah dari request POST
    data_to_update = request.json
    
    # Ambil data sebelum update
    pre_update_data = get_anlysis_news()
    
    # Update data berdasarkan input
    for item in data_to_update:
        if 'id' in item and 'sentiment' in item:
            update_sentiment(item['id'], item['sentiment'], TOPIK)
        else:
            print(f"Warning: Skipping item due to missing 'id' or 'sentiment': {item}")
    
    # Ambil data setelah update
    post_update_data = get_anlysis_news()
    
    # Bandingkan data sebelum dan sesudah update
    changes = compare_data(pre_update_data, post_update_data)
    
    # Proses selanjutnya
    save_analyze_news(post_update_data, TOPIK)
    
    data_json_ep = news_endpoint()
    save_endpoint_MDB(data_json_ep, TOPIK)
    
    # Tambahkan informasi perubahan ke dalam respons
    data_json_ep['sentiment_changes'] = changes
    return jsonify(data_json_ep)

def compare_data(pre_data, post_data):
    changes = {
        'total_changes': 0,
        'changed_items': []
    }
    for pre, post in zip(pre_data, post_data):
        # Check if both 'id' and 'sentiment' keys exist in both pre and post
        if 'id' in pre and 'id' in post and 'sentiment' in pre and 'sentiment' in post:
            if pre['sentiment'] != post['sentiment']:
                changes['total_changes'] += 1
                changes['changed_items'].append({
                    'id': post['id'],
                    'old_sentiment': pre['sentiment'],
                    'new_sentiment': post['sentiment']
                })
        else:
            print(f"Warning: Skipping comparison due to missing 'id' or 'sentiment' key in item.")
    return changes

# ======= CALL ENDPOINT =========
@app.route('/call_endpoint_pieSentiment', methods=['GET'])
def call_endpoint_pieSentiment():
    topik_collection = db[TOPIK]
    document = topik_collection.find_one({'_id': 'news_ep'})
    data_json = document['pie_sentiment']

    return jsonify(data_json)

@app.route('/call_endpoint_pieBuzzer', methods=['GET'])
def call_endpoint_pieBuzzer():
    topik_collection = db[TOPIK]
    document = topik_collection.find_one({'_id': 'news_ep'})
    data_json = document['pie_buzz']

    return jsonify(data_json)


if __name__ == '__main__':
    app.run(debug=True)
