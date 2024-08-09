from flask import Blueprint, jsonify
from utils.data.utils_pie import pie_chart

pie_bp = Blueprint('pie', __name__)

@pie_bp.route('/portal_persen', methods=['GET'])
def get_news_data():
    pie_chart_data = pie_chart()
    return jsonify(pie_chart_data)
