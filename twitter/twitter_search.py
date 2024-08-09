from apify_client import ApifyClient
from flask import Flask, request, jsonify
from dotenv import load_dotenv
import os
app = Flask(__name__)

load_dotenv()

# Initialize the ApifyClient with your API token
client = ApifyClient(os.getenv("APIFY_API_TOKEN"))

@app.route('/search_tweets', methods=['GET'])
def search_tweets():
    keyword = request.args.get('keyword')
    
    if not keyword:
        return jsonify({"error": "Keyword is required"}), 400

    # Prepare the Actor input
    run_input = {
        "searchTerms": [keyword],  # Wrap keyword in a list
        "searchMode": "live",
        "maxTweets": 200,
        "maxTweetsPerQuery": 200,
        "maxRequestRetries": 6,
        "addUserInfo": True,
        "scrapeTweetReplies": True,
        "handle": ["indonesia"],
        "urls": ["https://twitter.com/search?q=gpt&src=typed_query&f=live"],
    }

    try:
        # Run the Actor and wait for it to finish
        run = client.actor("heLL6fUofdPgRXZie").call(run_input=run_input)
        
        # Fetch Actor results from the run's dataset (if there are any)
        results = []
        total_likes = 0
        followers_count = 0  # Initialize total followers count

        for item in client.dataset(run["defaultDatasetId"]).iterate_items():
            results.append(item)
            total_likes += item.get('likes', 0)
            if 'user' in item and 'followersCount' in item['user']:
                user_followers_count = item['user']['followersCount']
                followers_count += user_followers_count  # Add to total followers count

        response = {
            "results": results,
            "total_likes": total_likes,
            "followers_count": followers_count,  # Total followers count
            "total_posts": len(results),  # Number of posts
        }

        return jsonify(response)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)