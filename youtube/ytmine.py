from flask import Flask, request, jsonify
from flask_cors import CORS
from googleapiclient.discovery import build
import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from dotenv import load_dotenv
import os
from collections import Counter
import re

app = Flask(__name__)
CORS(app)

load_dotenv()

# Load the API key from the .env file
api_key = os.getenv('YOUTUBE_API_KEY')
youtube = build('youtube', 'v3', developerKey=api_key)
latest_results = {}

def update_search():
    global latest_results
    
    keywords = list(latest_results.keys())
    
    for keyword in keywords:
        now = datetime.datetime.now(datetime.UTC)
        one_minute_ago = now - datetime.timedelta(minutes=1)
        search_params = {
            'part': 'id,snippet',
            'type': 'video',
            'maxResults': 100,
            'q': keyword,
            'order': 'date',
            'publishedAfter': one_minute_ago.replace(microsecond=0).isoformat() + 'Z'
        }
        
        try:
            response = youtube.search().list(**search_params).execute()
            videos = []
            
            for item in response.get('items', []):
                video_id = item['id']['videoId']
                snippet = item['snippet']

                # Fetch video details
                video_response = youtube.videos().list(
                    part='statistics',
                    id=video_id
                ).execute()
                video_details = video_response['items'][0]
                statistics = video_details['statistics']

                # Fetch channel details
                channel_id = snippet['channelId']
                channel_response = youtube.channels().list(
                    part='snippet',
                    id=channel_id
                ).execute()
                channel_info = channel_response['items'][0]['snippet']

                # Fetch video comments
                comments_response = youtube.commentThreads().list(
                    part='snippet',
                    videoId=video_id,
                    maxResults=5
                ).execute()
                comments = [{
                    'text': comment['snippet']['topLevelComment']['snippet']['textDisplay'],
                    'author': comment['snippet']['topLevelComment']['snippet']['authorDisplayName'],
                    'author_profile_image': comment['snippet']['topLevelComment']['snippet']['authorProfileImageUrl'],
                    'published_at': comment['snippet']['topLevelComment']['snippet']['publishedAt']
                } for comment in comments_response.get('items', [])]

                video_data = {
                    'title': snippet['title'],
                    'channel': snippet['channelTitle'],
                    'channel_location': channel_info.get('country', 'Not specified'),
                    'published_at': snippet['publishedAt'],
                    'thumbnail': snippet['thumbnails']['default']['url'],
                    'view_count': statistics.get('viewCount', 0),
                    'likes': statistics.get('likeCount', 0),
                    'comment_count': statistics.get('commentCount', 0),
                    'comments': comments  # Add comments to video data
                }
                videos.append(video_data)

            latest_results[keyword] = {
                'videos': videos,
                'count': len(videos),
                'last_updated': now.isoformat()
            }
        except Exception as e:
            print(f"Error updating search for keyword '{keyword}': {str(e)}")

    print("Search results updated successfully")

scheduler = BackgroundScheduler()
scheduler.add_job(func=update_search, trigger="interval", minutes=1)
scheduler.start()

@app.route('/youtube_search', methods=['GET'])
def youtube_search():
    try:
        keyword = request.args.get('q', '')
        order = request.args.get('order', 'relevance')
        published_after = request.args.get('published_after', '')
        published_before = request.args.get('published_before', '')
        update_mode = request.args.get('update', 'false').lower() == 'true'

        if not keyword:
            return jsonify({'error': 'Keyword is required'}), 400

        # Add the keyword to latest_results if it's not already there
        if keyword not in latest_results:
            latest_results[keyword] = {
                'videos': [],
                'count': 0,
                'last_updated': None
            }

        search_params = {
            'part': 'id,snippet',
            'type': 'video',
            'maxResults': 100,
            'q': keyword
        }

        if update_mode:
            now = datetime.datetime.now(datetime.UTC)
            yesterday = now - datetime.timedelta(days=1)
            search_params['order'] = 'date'
            search_params['publishedAfter'] = yesterday.isoformat() + 'Z'
        else:
            search_params['order'] = order
            if published_after:
                search_params['publishedAfter'] = published_after
            if published_before:
                search_params['publishedBefore'] = published_before

        response = youtube.search().list(**search_params).execute()

        videos = []
        person_mentions = Counter()
        channel_mentions = Counter()

        for item in response.get('items', []):
            video_id = item['id']['videoId']
            snippet = item['snippet']

            # Fetch video details
            video_response = youtube.videos().list(
                part='statistics',
                id=video_id
            ).execute()
            video_details = video_response['items'][0]
            statistics = video_details['statistics']

            # Fetch channel details
            channel_id = snippet['channelId']
            channel_response = youtube.channels().list(
                part='snippet',
                id=channel_id
            ).execute()
            channel_info = channel_response['items'][0]['snippet']

            # Fetch video comments
            comments_response = youtube.commentThreads().list(
                part='snippet',
                videoId=video_id,
                maxResults=5
            ).execute()
            comments = [{
                'text': comment['snippet']['topLevelComment']['snippet']['textDisplay'],
                'author': comment['snippet']['topLevelComment']['snippet']['authorDisplayName'],
                'author_profile_image': comment['snippet']['topLevelComment']['snippet']['authorProfileImageUrl'],
                'published_at': comment['snippet']['topLevelComment']['snippet']['publishedAt']
            } for comment in comments_response.get('items', [])]

            video_data = {
                'title': snippet['title'],
                'channel': snippet['channelTitle'],
                'channel_location': channel_info.get('country', 'Not specified'),
                'published_at': snippet['publishedAt'],
                'thumbnail': snippet['thumbnails']['default']['url'],
                'view_count': statistics.get('viewCount', 0),
                'likes': statistics.get('likeCount', 0),
                'comment_count': statistics.get('commentCount', 0),
                'comments': comments
            }

            # Count person mentions in video title
            title_mentions = extract_names(video_data['title'])
            person_mentions.update(title_mentions)
            if title_mentions:
                channel_mentions[video_data['channel']] += 1

            # Count person mentions in comments
            for comment in comments:
                comment_mentions = extract_names(comment['text'])
                person_mentions.update(comment_mentions)
                if comment_mentions:
                    channel_mentions[video_data['channel']] += 1

            videos.append(video_data)

        result = {
            'videos': videos,
            'count': len(videos),
            'top_inffluencers': dict(person_mentions.most_common(10)),  # Top 10 mentioned persons
            'top_channels': dict(channel_mentions.most_common(5))  # Top 5 channels mentioning persons
        }
        if update_mode:
            return jsonify(latest_results)

        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def extract_names(text):
    # Simple name extraction (can be improved with NLP libraries)
    words = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', text)
    return [word for word in words if len(word.split()) > 1]  # Only consider multi-word names


if __name__ == '__main__':
    app.run(debug=True)