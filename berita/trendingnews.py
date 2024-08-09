from serpapi import GoogleSearch
import os
   
SERPAPI_API_KEY = os.environ['SERPAPI_API_KEY'] = 'f7fe28cca82df25849028abd7d5ab97ffcf33bf350434dce1b4c8afec4b544a3'

# Inisialisasi GoogleSearch dengan API key dan query

# Eksekusi pencarian
def get_trending_news(query="trending DPR RI", num_results=5):
    # Inisialisasi GoogleSearch dengan API key dan query
    search = GoogleSearch({"q": query, "SERPAPI_API_KEY": SERPAPI_API_KEY, "num": num_results})

    # Eksekusi pencarian
    results = search.get_dict()

    # Menampilkan berita trending
    if 'news_results' in results:
        for news in results['news_results']:
            print("Title:", news.get('title'))
            print("URL:", news.get('link'))
            print("Source:", news.get('source'))
            print("Date:", news.get('date'))
            print("-" * 40)
    else:
        print("No trending news found.")

if __name__ == "__main__":
    if not SERPAPI_API_KEY:
        print("Please set the SERPAPI_API_KEY environment variable.")
    else:
        get_trending_news()