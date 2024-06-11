
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import io
import base64
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
import os

def generate_wordcloud(docs, stop_words, max_words=35, width=1600, height=800):
    # Check if docs is a list of strings or a single string
    if isinstance(docs, list):
        # Join the list of documents into a single string
        text = ' '.join(docs)
    elif isinstance(docs, str):
        text = docs
    else:
        raise ValueError("docs should be either a list of strings or a single string")

    # Create a WordCloud object
    wordcloud = WordCloud(width=width, height=height,
                          background_color='#F2F7FF',
                          max_words=max_words,
                          stopwords=stop_words,
                          min_font_size=10).generate(text)

    # Plot the WordCloud image
    fig, ax = plt.subplots(figsize=(20, 10), facecolor='k')
    ax.imshow(wordcloud, interpolation='bilinear')
    ax.axis("off")
    plt.tight_layout(pad=0)

    return fig

def load_wordcloud(docs, stop_words):
    # Generate wordcloud
    fig = None
    if docs:
        try:
            fig = generate_wordcloud(docs, stop_words)
        except ValueError:
            # Handle the case where wordcloud generation fails
            print(f"Error generating word cloud: {e}")
            fig = None
    image_base64 = None
    if fig:
        buf = io.BytesIO()
        canvas = FigureCanvas(fig)
        canvas.print_png(buf)
        buf.seek(0)
        image_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
    return image_base64