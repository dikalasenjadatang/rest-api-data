import eventregistry
from eventregistry import *
import datetime
import json
from flask import Flask, request, jsonify
from flask_apscheduler import APScheduler
from dotenv import load_dotenv
import os
from news import get_latest_articles  # Import the function from news.py
import re

# Initialize the Event Registry API client
# Load environment variables from .env file
load_dotenv()

# Initialize the Event Registry API client
er = EventRegistry(apiKey=os.getenv("EVENT_REGISTRY_API_KEY"))
app = Flask(__name__)
scheduler = APScheduler()
scheduler.init_app(app)
scheduler.start()

# Global variable to store the latest articles
latest_articles = []
current_keyword = ""

# Add this list of Indonesian provinces
indonesian_provinces = [
    "Aceh", "Sumatera Utara", "Sumatera Barat", "Riau", "Kepulauan Riau", "Jambi", "Sumatera Selatan",
    "Bangka Belitung", "Bengkulu", "Lampung", "DKI Jakarta", "Banten", "Jawa Barat", "Jawa Tengah",
    "DI Yogyakarta", "Jawa Timur", "Bali", "Nusa Tenggara Barat", "Nusa Tenggara Timur", "Kalimantan Barat",
    "Kalimantan Tengah", "Kalimantan Selatan", "Kalimantan Timur", "Kalimantan Utara", "Sulawesi Utara",
    "Gorontalo", "Sulawesi Tengah", "Sulawesi Barat", "Sulawesi Selatan", "Sulawesi Tenggara", "Maluku",
    "Maluku Utara", "Papua Barat", "Papua"
]

def extract_provinces(text):
    found_provinces = []
    for province in indonesian_provinces:
        if re.search(r'\b' + re.escape(province) + r'\b', text, re.IGNORECASE):
            found_provinces.append(province)
    return found_provinces

def get_latest_articles(keyword):
    allowed_sources = [
        "detik.com", "antaranews.com", "viva.co.id", "republika.co.id",
        "cnnindonesia.com", "liputan6.com", "tribunnews.com", "kumparan.com",
        "kompas.com", "tempo.co", "suara.com", "rmol.id", "okezone.com", 
        "mediaindonesia.com", "merdeka.com", "thejakartapost.com", "suara.com"
    ]
    
    q = QueryArticlesIter(
        keywords=keyword,
        lang=["eng", "ind"],
        dateStart=datetime.datetime.now() - datetime.timedelta(days=30),  # Changed to last hour
        dateEnd=datetime.datetime.now(),
        dataType=["news", "blog"],
        sourceLocationUri=er.getLocationUri("Indonesia"),
        sourceUri=QueryItems.OR(allowed_sources)
    )

    articles = []
    for article in q.execQuery(er, sortBy="date", maxItems=500):
        content = article.get("body", "")
        provinces = extract_provinces(content)
        
        articles.append({
            "judul": article["title"],
            "tanggal": article["dateTime"],
            "sumber": article["source"]["title"],
            "url": article["url"],
            "ringkasan": content[:200] + "..." if content else "Ringkasan tidak tersedia",
            "isi": content,
            "penulis": article.get("authors", []),
            "editor": article.get("editors", []),
            "thumbnail": article.get("image", None),
            "provinsi": provinces  # Add the extracted provinces
        })
    
    return articles

@app.route('/search', methods=['GET'])
def search_articles():
    global current_keyword
    keyword = request.args.get('keyword', type=str)
    current_keyword = keyword
    latest_articles = get_latest_articles(keyword)
    return jsonify({"articles": latest_articles, "count": len(latest_articles)})

def update_articles():
    global latest_articles, current_keyword
    if current_keyword:
        latest_articles = get_latest_articles(current_keyword)

def update_news_articles():
    global latest_articles
    news_articles = get_latest_articles()
    latest_articles.extend(news_articles)

@scheduler.task('interval', id='update_articles_job', seconds=60, misfire_grace_time=900)
def scheduled_update():
    with app.app_context():
        update_articles()
        update_news_articles()

if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)

# Remove the print statement as it's not needed in a web application