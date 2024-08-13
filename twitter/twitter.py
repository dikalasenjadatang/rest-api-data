import requests

# Gantilah dengan URL API SocialData dan token API Anda
api_url = "https://api.socialdata.tools/twitter"
api_token = "589|gtynJweUrMzrd2HQFW48OI7WSq0zymwQKwQbM2We6fbf9c82"

def get_tweets_and_comments(query, count=10):
    headers = {
        "Authorization": f"Bearer {api_token}"
    }
    
    # Mengambil postingan
    tweet_response = requests.get(f"{api_url}/tweets", headers=headers, params={"query": query, "count": count})
    
    try:
        tweets = tweet_response.json()
    except requests.exceptions.JSONDecodeError:
        print(f"Error decoding JSON. Status code: {tweet_response.status_code}")
        print(f"Response content: {tweet_response.text}")
        return None

    # Mengambil komentar untuk setiap postingan
    for tweet in tweets.get('data', []):
        tweet_id = tweet['id']
        comment_response = requests.get(f"{api_url}/tweets/{tweet_id}/comments", headers=headers)
        
        try:
            comments = comment_response.json()
            tweet['comments'] = comments.get('data', [])
        except requests.exceptions.JSONDecodeError:
            print(f"Error decoding JSON for comments. Tweet ID: {tweet_id}")
            print(f"Response content: {comment_response.text}")
            tweet['comments'] = []
    
    return tweets

# Contoh penggunaan
tweets_and_comments = get_tweets_and_comments("Jokowi", count=5)
print(tweets_and_comments)