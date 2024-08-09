import pandas as pd
from analysis.berita.analysis_news import get_anlysis


def pie_chart():
    document = get_anlysis()

    data = document['data'] if document else []
    # Convert to DataFrame
    df = pd.DataFrame(data)

    # Calculate the percentage of 'positif' and 'negatif'
    sentiment_counts = df['sentimen'].value_counts(normalize=True) * 100

    # Prepare the pie chart data
    pie_chart_data = {
        "labels": sentiment_counts.index.tolist(),
        "values": sentiment_counts.values.tolist()
    }

    return pie_chart_data
