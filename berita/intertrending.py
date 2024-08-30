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
    trending_searches_indonesia = pytrends.trending_searches(pn='indonesia')
    # Get trending searches for the world
    trending_searches_world = pytrends.trending_searches(pn='united_states')  # Example for international trends
    return {
        "indonesia": trending_searches_indonesia.values.tolist()[:5],  # Top 5 trending searches in Indonesia
        "world": trending_searches_world.values.tolist()[:5]  # Top 5 trending searches internationally
    }

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
    trends = get_google_trends()
    trending_news_indonesia = []
    trending_news_world = []
    dpr_ri_news = get_dpr_ri_news()

    with ThreadPoolExecutor(max_workers=10) as executor:
        future_to_trend_indonesia = {executor.submit(get_news_for_trend, trend): trend for trend in trends["indonesia"]}
        future_to_trend_world = {executor.submit(get_news_for_trend, trend): trend for trend in trends["world"]}
        
        for future in as_completed(future_to_trend_indonesia):
            trend = future_to_trend_indonesia[future]
            try:
                news = future.result()
                trending_news_indonesia.append({
                    "trend": trend,
                    "news": news,
                    "url": f"https://trends.google.com/trends/explore?geo=ID&q={trend}"  # Added URL
                })
            except Exception as exc:
                print(f'{trend} generated an exception: {exc}')
        
        for future in as_completed(future_to_trend_world):
            trend = future_to_trend_world[future]
            try:
                news = future.result()
                trending_news_world.append({
                    "trend": trend,
                    "news": news,
                    "url": f"https://trends.google.com/trends/explore?geo=US&q={trend}"  # Added URL
                })
            except Exception as exc:
                print(f'{trend} generated an exception: {exc}')

    return jsonify({
        "trending_news_indonesia": trending_news_indonesia,
        "trending_news_world": trending_news_world,
        "dpr_ri_news": dpr_ri_news,
        "count": len(trending_news_indonesia) + len(trending_news_world) + 1  # +1 for DPR RI news
    })

if __name__ == "__main__":
    app.run(debug=True)