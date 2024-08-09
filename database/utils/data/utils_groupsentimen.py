# utils/data/utils_groupsentimen.py
import pandas as pd
#from scraping.berita.get_news import get_news_data
from analysis.berita.analysis_news import get_anlysis

def get_news_classification():
    document = get_anlysis()

    data = document['data'] if document else []
    # Convert to DataFrame
    df = pd.DataFrame(data)
    
    # Create dictionaries for sentiment classification
    sentiment_classification = {
        "positif": df[df["sentimen"] == "positif"]["judul"].tolist(),
        "negatif": df[df["sentimen"] == "negatif"]["judul"].tolist()
    }
    
    return sentiment_classification
