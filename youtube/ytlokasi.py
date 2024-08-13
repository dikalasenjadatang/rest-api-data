from flask import Flask, request, jsonify, render_template
from googleapiclient.discovery import build
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderUnavailable
from geopy.distance import geodesic
import folium
import os
import html

app = Flask(__name__)

# Ganti dengan API Key Anda
API_KEY = 'AIzaSyAjNsxll9S2776nHd0RkuowzwALeUFAlLE'

# Membuat service YouTube
youtube = build('youtube', 'v3', developerKey=API_KEY)

# Initialize Nominatim geolocator
geolocator = Nominatim(user_agent="ytlokasi_app")

def search_youtube_videos(query, location, radius, max_results=10):
    # Get coordinates for the location
    try:
        location_info = geolocator.geocode(location)
        if location_info:
            lat, lng = location_info.latitude, location_info.longitude
            location_string = f"{lat},{lng}"
        else:
            location_string = None
    except (GeocoderTimedOut, GeocoderUnavailable):
        location_string = None

    request = youtube.search().list(
        q=query,
        part='snippet,id',
        type='video',
        maxResults=max_results,
        order='relevance',
        location=location_string,
        locationRadius=f"{radius}km" if location_string else None
    ) 
    response = request.execute()
    
    videos = []
    for item in response.get('items', []):
        video_id = item['id']['videoId']
        video_response = youtube.videos().list(
            part='recordingDetails,snippet',
            id=video_id
        ).execute()
        
        video_snippet = video_response['items'][0]['snippet']
        recording_details = video_response['items'][0].get('recordingDetails', {})
        video_location = recording_details.get('location', {})
        
        if video_location:
            video_lat, video_lng = video_location.get('latitude'), video_location.get('longitude')
            distance = geodesic((lat, lng), (video_lat, video_lng)).kilometers if location_info else None
        else:
            video_lat, video_lng, distance = None, None, None
        
        video = {
            'title': video_snippet['title'],
            'description': video_snippet['description'],
            'publish_time': video_snippet['publishedAt'],
            'video_url': f"https://www.youtube.com/watch?v={video_id}",
            'latitude': video_lat,
            'longitude': video_lng,
            'distance': round(distance, 2) if distance else None,
            'channel_name': video_snippet['channelTitle'],
            'thumbnail_url': video_snippet['thumbnails']['default']['url']
        }
        videos.append(video)
    
    return videos, location_info

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('q', default='Jakarta', type=str)
    location = request.args.get('location', default='Jakarta', type=str)
    max_results = request.args.get('max_results', default=10, type=int)
    radius = request.args.get('radius', default=100, type=int)
    
    videos, location_info = search_youtube_videos(query, location, radius, max_results)
    
    # Create a map centered on the search location
    if location_info:
        m = folium.Map(location=[location_info.latitude, location_info.longitude], zoom_start=10)
        folium.Marker(
            [location_info.latitude, location_info.longitude],
            popup="Search Location",
            icon=folium.Icon(color='red', icon='info-sign')
        ).add_to(m)
        
        # Add markers for each video with location data
        for video in videos:
            if video['latitude'] and video['longitude']:
                popup_html = f"""
                <div style="width:200px">
                    <img src="{video['thumbnail_url']}" alt="Video Thumbnail" style="width:100%"><br>
                    <strong>{html.escape(video['title'])}</strong><br>
                    Channel: {html.escape(video['channel_name'])}<br>
                    <a href="{video['video_url']}" target="_blank">Watch Video</a>
                </div>
                """
                folium.Marker(
                    [video['latitude'], video['longitude']],
                    popup=folium.Popup(popup_html, max_width=300),
                    icon=folium.Icon(color='blue', icon='video-camera')
                ).add_to(m)
        
        map_html = m._repr_html_()
    else:
        map_html = "<p>Unable to generate map. Location not found.</p>"
    
    response = {
        'search_location': {
            'address': location_info.address if location_info else None,
            'latitude': location_info.latitude if location_info else None,
            'longitude': location_info.longitude if location_info else None
        },
        'videos': videos,
        'map_html': map_html  # Tambahkan ini
    }
    
    return jsonify(response)

if __name__ == "__main__":
    app.run(debug=True)