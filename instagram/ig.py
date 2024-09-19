from collections import Counter
from apify_client import ApifyClient
from flask import Flask, jsonify
from flask_restful import Api, request, Resource
from dotenv import load_dotenv
import os

app = Flask(__name__)
api = Api(app)

load_dotenv()

# Initialize the ApifyClient with your API token
client = ApifyClient(os.getenv("APIFY_API_TOKEN"))

def run_first_actor(search):
    run_input = {
        "addParentData": False,
        "enhanceUserSearchWithFacebookPage": False,
        "isUserReelFeedURL": False,
        "isUserTaggedFeedURL": False,
        "resultsLimit": 100,
        "resultsType": "comments",
        "search": search,
        "searchLimit": 100,
        "searchType": "hashtag"
    }
    run = client.actor("shu8hvrXbJbY3Eb9W").call(run_input=run_input)
    dataset = client.dataset(run["defaultDatasetId"])
    
    # Ambil hasil sebagai list
    items = list(dataset.iterate_items())
    return items

def run_second_actor(direct_urls):
    run_input = {
        "directUrls": direct_urls,
        "resultsLimit": 100,
    }
    run = client.actor("SbK00X0JYCPblD2wp").call(run_input=run_input)
    dataset = client.dataset(run["defaultDatasetId"])
    
    # Ambil hasil sebagai list
    items = list(dataset.iterate_items())
    return items

@app.route('/instagram', methods=['GET'])
def run_actors():
    search = request.args.get('search')
    
    if not search:
        return jsonify({"error": "Parameter 'search' is required."}), 400
    
    try:
        # Run the first actor and get results
        first_actor_results = run_first_actor(search)

        # Extract direct URLs from the results of the first actor
        direct_urls = set()  # Menggunakan set untuk menghindari duplikat
        for item in first_actor_results:
            # Ambil URL dari topPosts jika ada
            if 'topPosts' in item:
                for post in item['topPosts']:
                    direct_urls.add(post['url'])

        # Cek jika direct_urls kosong
        if not direct_urls:
            return jsonify({"error": "No direct URLs found from the first actor."}), 400
        
        # Konversi kembali ke list
        unique_direct_urls = list(direct_urls)

        # Run the second actor with the obtained direct URLs
        second_actor_results = run_second_actor(unique_direct_urls)

        return jsonify({
            "first_actor_results": first_actor_results,
            "second_actor_results": second_actor_results
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(port=31337, debug=True)