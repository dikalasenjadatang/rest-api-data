from flask import Flask, Blueprint
from berita.news import search_articles
from twitter.twitter_search import search_tweets
from youtube.yt import youtube_search
from berita.newspaper import scrape_newspaper
app = Flask(__name__)

# Create blueprints
news_bp = Blueprint('news', __name__)
twitter_bp = Blueprint('twitter', __name__)
youtube_bp = Blueprint('youtube', __name__)
newspaper_bp = Blueprint('newspaepr', __name__)
# Register routes with blueprints
news_bp.route('/')(search_articles)
twitter_bp.route('/')(search_tweets)
youtube_bp.route('/')(youtube_search)
newspaper_bp.route('/')(scrape_newspaper)

# Register blueprints with the app
app.register_blueprint(news_bp, url_prefix='/news')
app.register_blueprint(twitter_bp, url_prefix='/twitter')
app.register_blueprint(youtube_bp, url_prefix='/youtube')
app.register_blueprint(newspaper_bp, url_prefix='/newspaper')

if __name__ == '__main__':
    app.run(debug=True)