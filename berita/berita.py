import datetime
import json
import re
import os
from flask import Flask, request, jsonify
from flask_apscheduler import APScheduler
from flask_caching import Cache
from dotenv import load_dotenv
from eventregistry import EventRegistry, QueryArticlesIter

# Load environment variables from .env file
load_dotenv()

# Initialize the Event Registry API client
er = EventRegistry(apiKey=os.getenv("EVENT_REGISTRY_API_KEY"))
app = Flask(__name__)

# Configure caching
app.config['CACHE_TYPE'] = 'simple'
app.config['CACHE_DEFAULT_TIMEOUT'] = 600  # Cache timeout in seconds (10 minutes)
cache = Cache(app)

scheduler = APScheduler()
scheduler.init_app(app)
scheduler.start()

# Global variable to store the current keyword
current_keyword = ""

# List of Indonesian provinces
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
        dateStart=datetime.datetime.now() - datetime.timedelta(days=30),
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
            "provinsi": provinces
        })
    
    return articles

@app.route('/search', methods=['GET'])
@cache.cached(query_string=True)  # Cache based on query string
def search_articles():
    global current_keyword
    keyword = request.args.get('keyword', type=str)
    current_keyword = keyword
    articles = get_latest_articles(keyword)
    return jsonify({"articles": articles, "count": len(articles)})

def update_articles():
    global current_keyword
    if current_keyword:
        cache.set(f'articles_{current_keyword}', get_latest_articles(current_keyword))

@scheduler.task('interval', id='update_articles_job', seconds=60, misfire_grace_time=900)
def scheduled_update():
    with app.app_context():
        if current_keyword:
            update_articles()

if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)
        
