from eventregistry import *
import datetime
from collections import Counter
from flask import Flask, jsonify, request
import os
from dotenv import load_dotenv
from pytrends.request import TrendReq
from concurrent.futures import ThreadPoolExecutor, as_completed

load_dotenv()

app = Flask(__name__)

# Initialize Event Registry client
er = EventRegistry(apiKey=os.getenv('EVENT_REGISTRY_API_KEY'))

# Initialize Google Trends client
pytrends = TrendReq(hl='en-US', tz=360)

def get_google_trends():
    # Get trending searches for Indonesia
    trending_searches = pytrends.trending_searches(pn='indonesia')  # Ensure this is set to 'indonesia'
    return trending_searches.values.tolist()[:5]  # Return top 5 trending searches

def get_news_for_trend(trend, max_items=5):
    q = QueryArticlesIter(
        keywords=trend,
        lang="eng",
        dateStart=datetime.datetime.now() - datetime.timedelta(days=1),
        dateEnd=datetime.datetime.now(),
        dataType=["news", "blog"],
        sourceLocationUri=er.getLocationUri("Indonesia")
    )

    articles = []
    for article in q.execQuery(er, sortBy="date", maxItems=max_items):
        articles.append({
            "title": article["title"],
            "date": article["dateTime"],
            "source": article["source"]["title"],
            "url": article["url"],
            "summary": article.get("body", "")[:200] + "..." if article.get("body") else "Summary not available",
        })
    
    return articles

def get_dpr_ri_news(max_items=5):
    q = QueryArticlesIter(
        keywords="DPR RI",
        lang="ind",  # Changed to Indonesian
        dateStart=datetime.datetime.now() - datetime.timedelta(days=7),  # Last 7 days
        dateEnd=datetime.datetime.now(),
        dataType=["news"],
        sourceLocationUri=er.getLocationUri("Indonesia")
    )

    articles = []
    for article in q.execQuery(er, sortBy="date", maxItems=max_items):
        articles.append({
            "title": article["title"],
            "date": article["dateTime"],
            "source": article["source"]["title"],
            "url": article["url"],
            "summary": article.get("body", "")[:200] + "..." if article.get("body") else "Summary not available",
        })
    
    return articles

@app.route('/trending_news', methods=['GET'])
def trending_news():
    trends = get_google_trends()  # Fetch trending topics for Indonesia
    trending_news = []
    dpr_ri_news = get_dpr_ri_news()

    with ThreadPoolExecutor(max_workers=10) as executor:
        future_to_trend = {executor.submit(get_news_for_trend, trend): trend for trend in trends}
        for future in as_completed(future_to_trend):
            trend = future_to_trend[future]
            try:
                news = future.result()
                trending_news.append({
                    "trend": trend,
                    "news": news,
                    "url": f"https://news.google.com/search?q={trend}"  # Updated URL to news.google.com
                })
            except Exception as exc:
                print(f'{trend} generated an exception: {exc}')

    return jsonify({
        "trending_news": trending_news,
        "dpr_ri_news": dpr_ri_news,
        "count": len(trending_news) + 1  # +1 for DPR RI news
    })

if __name__ == "__main__":
    app.run(debug=True)