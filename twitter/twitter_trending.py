from collections import Counter
from apify_client import ApifyClient
from flask import Flask
from flask_restful import Api, Resource
from dotenv import load_dotenv
import os

app = Flask(__name__)
api = Api(app)

load_dotenv()

# Initialize the ApifyClient with your API token
client = ApifyClient(os.getenv("APIFY_API_TOKEN"))

class TrendingTweets(Resource):
    def get(self):
        # Prepare the Actor input for trending topics related to DPR RI
        run_input = {
            "searchTerms": ["DPR RI"],
            "searchMode": "top",
            "maxTweets": 10,  # Increased to get more tweets
            "maxTweetsPerQuery": 10,
            "maxRequestRetries": 6,
            "addUserInfo": True,
            "scrapeTweetReplies": False,
            "handle": ["indonesia"],
            "urls": ["https://twitter.com/search?q=DPR%20RI&src=typed_query&f=top"],
        }

        # Run the Actor and wait for it to finish
        run = client.actor("heLL6fUofdPgRXZie").call(run_input=run_input)

        # Fetch Actor results from the run's dataset
        all_hashtags = []
        for item in client.dataset(run["defaultDatasetId"]).iterate_items():
            hashtags = [tag["text"] for tag in item.get("entities", {}).get("hashtags", [])]
            all_hashtags.extend(hashtags)

        # Count hashtag occurrences
        hashtag_counts = Counter(all_hashtags)

        # Get the top 10 trending hashtags
        top_trending_hashtags = hashtag_counts.most_common(10)

        # Format the result
        trending_results = [
            {
                "hashtag": f"#{hashtag}",
                "count": count
            }
            for hashtag, count in top_trending_hashtags
        ]

        return trending_results

api.add_resource(TrendingTweets, '/api/trending_tweets')

if __name__ == '__main__':
    app.run(debug=True)