import eventregistry
from eventregistry import *
import datetime
import json
from flask import Flask, request, jsonify
from flask_apscheduler import APScheduler
from dotenv import load_dotenv
import os
import logging
from flask_cors import CORS


# Initialize the Event Registry API client
# Load environment variables from .env file
load_dotenv()

# Initialize the Event Registry API client
er = EventRegistry(apiKey=os.getenv("EVENT_REGISTRY_API_KEY"))
app = Flask(__name__)
CORS(app)
scheduler = APScheduler()
scheduler.init_app(app)
scheduler.start()

# Global variable to store the latest articles
latest_articles = []
current_keyword = ""

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_latest_articles(keyword):
    q = QueryArticlesIter(
        keywords=keyword,
        lang=["eng", "id"],  # Changed to English only for global news
        dateStart=datetime.datetime.now() - datetime.timedelta(days=7),  # Berita dari 1 minggu yang lalu
        dateEnd=datetime.datetime.now(),  # Sampai hari ini
        dataType=["news"],
        # Removed sourceLocationUri parameter
    )

    articles = []
    for i, article in enumerate(q.execQuery(er, sortBy="date", maxItems=100), 1):
        articles.append({
            "judul": article["title"],
            "tanggal": article["dateTime"],
            "sumber": article["source"]["title"],
            "url": article["url"],
            "ringkasan": article.get("body", "")[:200] + "..." if article.get("body") else "Ringkasan tidak tersedia"
        })
        logger.info(f"Artikel ke-{i} berhasil ditarik: {article['title']}")
    
    logger.info(f"Total {len(articles)} artikel berhasil ditarik untuk keyword: {keyword}")
    return articles

def get_articles_from_specific_sources(keyword):
    # List of specific news sources to query
    specific_sources = [
        "detik.com", "antaranews.com", "viva.co.id", "republika.co.id",
        "cnnindonesia.com", "liputan6.com", "tribunnews.com", "kumparan.com",
        "kompas.com", "tempo.co", "suara.com", "rmol.id"
    ]
    
    # Set up the query parameters
    q = QueryArticlesIter(
        keywords=keyword,
        lang=["eng", "id"],  # English language articles only
        dateStart=datetime.datetime.now() - datetime.timedelta(days=7),  # Berita dari 1 minggu yang lalu
        dateEnd=datetime.datetime.now(),  # Sampai hari ini
        dataType=["news"],
        sourceUri=QueryItems.OR(specific_sources)  # Only articles from the specified sources
    )

    article = []
    # Execute the query and process the results
    for article in q.execQuery(er, sortBy="date", maxItems=100):
        source_domain = article["source"]["uri"]
        if any(source in source_domain for source in specific_sources):
            # Extract relevant information from the article
            article.append({
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
            logger.info(f"Artikel dari {source_domain} berhasil ditarik: {article['title']}")
    
    logger.info(f"Total {len(article)} artikel dari sumber spesifik berhasil ditarik untuk keyword: {keyword}")
    return article

@app.route('/search', methods=['GET'])
def search_articles():
    global current_keyword
    keyword = request.args.get('keyword', type=str)
    current_keyword = keyword
    specific_articles = get_articles_from_specific_sources(keyword)
    return jsonify({
        "articles": specific_articles,
        "count": len(specific_articles)
    })

def update_articles():
    global latest_articles, current_keyword
    if current_keyword:
        latest_articles = get_latest_articles(current_keyword)

@scheduler.task('interval', id='update_articles_job', seconds=60, misfire_grace_time=900)
def scheduled_update():
    with app.app_context():
        update_articles()

if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)