# endpoints/data/groupsentimen_endpoint.py
from flask import Blueprint, jsonify
from utils.data.utils_groupsentimen import get_news_classification as get_classification_data

groupsentimen_bp = Blueprint('groupsentimen', __name__)

@groupsentimen_bp.route('/news_classification', methods=['GET'])
def get_news_classification():
    sentiment_classification = get_classification_data()
    return jsonify(sentiment_classification)
