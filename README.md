# News-Summarization-and-TTS-application
A web-based application that extracts news articles for a given company, performs sentiment analysis, conducts comparative sentiment analysis across the articles to derive insights on how the company's news coverage varies and generates a text-to-speech output in Hindi. The app is built using Python, Streamlit, and various NLP libraries, and is deployed on Streamlit Cloud.

# Overview
This application allows the users to: 
1. Input a company name.
2. Fetches news articles about that company.
3. Summarizes the articles.
4. Analyzes their sentiment (Positive, Negative, Neutral)
5. Compares the coverage across articles.
6. Generates a Hindi audio summary about the report.

# Setup Instructions

1. **Clone the Repository**
   ```bash
   git clone https://github.com/Prabhal1999/News-Summarization-and-TTS-application
   cd News-Summarization-and-TTS-application
   
2. **Install Dependencies**
   pip install -r requirements.txt

3. **Set Environment Variables**
   export NEWS_API_KEY="your-api-key"

4. **Run the Application**
   streamlit run streamlit_app.py

5. **Access the Application on your browser**
   http://localhost:8501
   
# Usage Instructions
1. Visit the deployed app on the Streamlit Cloud: https://news-summarization-and-tts-application.streamlit.app/
2. Enter a company name in the text input field.
3. Click "Generate Report" to fetch news articles and view the sentiment report.
4. Review the report which includes article summaries, sentiment scores, comparative analysis and a hindi audio.

**Dependencies**
1. beautifulsoup4
2. deep-translator
3. gtts
4. keybert
5. requests
6. streamlit
7. transformers

# Documentation

**Project Setup**
1. Clone the repository: git clone https://github.com/Prabhal1999/News-Summarization-and-TTS-application
2. Install dependencies: pip install -r requirements.txt
3. Set the NewsAPI key: export NEWS_API_KEY="your-api-key"
4. Run the app: streamlit run streamlit_app.py
5. Access at http://localhost:8501.

**Model Details**
1. **Summarization**: Uses "facebook/bart-large-cnn" from Hugging Face’s transformers library. It’s a pre-trained model for generating concise summaries from long text inputs.
2. **Sentiment Analysis**: Uses "cardiffnlp/twitter-roberta-base-sentiment", a RoBERTa-based model fine-tuned for sentiment classification (Positive, Negative, Neutral) on Twitter-like data.
3. **Text-to-Speech (TTS)**: Uses gtts (Google Text-to-Speech), an open-source library to convert text into Hindi audio and saved as an MP3 file.

**API Development**
 The original implementation used FastAPI to create an endpoint (/analyze/{company}) for communication between the frontend and backend.
 However, for Streamlit Cloud deployment, the backend logic was integrated directly into the Streamlit app since Streamlit Cloud does not support running a 
 separate FastAPI server.

**API Usage**
1. NewsAPI is used to fetch news articles on the basis of the name of the company.  
2. It provides article metadata such as title, description, URL and content which are essential for summarization, sentiment analysis and topic extraction.  
3. The `extract_news` function in `utils.py` sends a GET request to `https://newsapi.org/v2/everything` with the company name as a query parameter along with the additional parameters like `from` and `sortBy`. The response is parsed as JSON and the app extracts up to 10 articles for processing. If the article content is incomplete, the app attempts to scrape the full content from the article URL using BeautifulSoup.  
4. The API key is stored in the `NEWS_API_KEY` environment variable. For local development, it’s set using `export NEWS_API_KEY="your-api-key"`. For Streamlit Cloud deployment, the key is securely stored in Streamlit Secrets under `NEWS_API_KEY`.  
5. The app handles potential API errors by raising exceptions with descriptive messages, which are displayed to the user via Streamlit’s error component.

**Assumptions & Limitations**
**Assumptions**
1. NewsAPI provides sufficient articles for the given company.
2. Internet connectivity is available for fetching news articles and generating TTS.
**Limitations**
1. Some news websites may use javascript-based rendering, which BeautifulSoup cannot scrape effectively. In such cases, the app falls back to NewsAPI content.
2. The sentiment analysis model might miss complex emotions in news articles, as it’s trained on Twitter data. For example, it may struggle with sarcasm or mixed sentiments.
