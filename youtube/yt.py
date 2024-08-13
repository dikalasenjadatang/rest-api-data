from flask import Flask, request, jsonify
from flask_cors import CORS
from googleapiclient.discovery import build
import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from dotenv import load_dotenv
import os

app = Flask(__name__)
CORS(app)

load_dotenv()

# Load the API key from the .env file
api_key = os.getenv('YOUTUBE_API_KEY')
youtube = build('youtube', 'v3', developerKey=api_key)
latest_results = {}

def get_recent_comments(video_id, max_results=5):
    two_months_ago = datetime.datetime.now(datetime.UTC) - datetime.timedelta(days=60)
    comments = []
    
    try:
        comments_response = youtube.commentThreads().list(
            part='snippet',
            videoId=video_id,
            maxResults=max_results,
            order='time'
        ).execute()
        
        for comment in comments_response.get('items', []):
            comment_snippet = comment['snippet']['topLevelComment']['snippet']
            published_at = datetime.datetime.fromisoformat(comment_snippet['publishedAt'].replace('Z', '+00:00'))
            
            if published_at >= two_months_ago:
                comments.append({
                    'text': comment_snippet['textDisplay'],
                    'author': comment_snippet['authorDisplayName'],
                    'author_profile_image': comment_snippet['authorProfileImageUrl'],
                    'published_at': comment_snippet['publishedAt']
                })
            
            if len(comments) >= max_results:
                break
    except Exception as e:
        print(f"Error fetching comments for video {video_id}: {str(e)}")
    
    return comments

def update_search():
    global latest_results
    
    keywords = list(latest_results.keys())
    
    for keyword in keywords:
        now = datetime.datetime.now(datetime.UTC)
        one_minute_ago = now - datetime.timedelta(minutes=1)
        search_params = {
            'part': 'id,snippet',
            'type': 'video',
            'maxResults': 20,
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
                comments = get_recent_comments(video_id)

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
            'maxResults': 20,
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
            comments = get_recent_comments(video_id)

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

        result = {
            'videos': videos,
            'count': len(videos)
        }
        if update_mode:
            return jsonify(latest_results)

        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)