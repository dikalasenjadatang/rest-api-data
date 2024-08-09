import eventregistry
from eventregistry import *
import datetime
import json
from flask import Flask, request, jsonify
from flask_apscheduler import APScheduler
from dotenv import load_dotenv
import os
from news import get_news_articles  # Import the function from news.py

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
        articles.append({
            "judul": article["title"],
            "tanggal": article["dateTime"],
            "sumber": article["source"]["title"],
            "url": article["url"],
            "ringkasan": article.get("body", "")[:200] + "..." if article.get("body") else "Ringkasan tidak tersedia",
            "isi": article.get("body", "Konten tidak tersedia"),  # Full article content
            "penulis": article.get("authors", []),  # Author information
            "editor": article.get("editors", []),  # Editor information
            "thumbnail": article.get("image", None)  # Thumbnail URL
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
    news_articles = get_news_articles()
    latest_articles.extend(news_articles)

@scheduler.task('interval', id='update_articles_job', seconds=60, misfire_grace_time=900)
def scheduled_update():
    with app.app_context():
        update_articles()
        update_news_articles()

if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)

# Remove the print statement as it's not needed in a web application