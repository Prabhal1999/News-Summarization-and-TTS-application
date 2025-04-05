import os
import requests
from bs4 import BeautifulSoup
from transformers import pipeline
from keybert import KeyBERT
import gtts
from collections import Counter
from deep_translator import GoogleTranslator
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
sentiment_analyzer = pipeline("sentiment-analysis", model="cardiffnlp/twitter-roberta-base-sentiment")
kb = KeyBERT()
translator = GoogleTranslator(source='en', target='hi')

NEWS_API_KEY = os.getenv("NEWS_API_KEY") 

# This function, with company name as parameter, extract news articles & returns articles in dictionary format
def extract_news(company):
    """
    Extract news articles from NewsAPI
    """
    if not NEWS_API_KEY:
        raise ValueError("NEWS_API_KEY not set in the environment.")

    url = f"https://newsapi.org/v2/everything?q={company}&from=2025-03-05&sortBy=publishedAt&apiKey={NEWS_API_KEY}"


    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        
        if data["status"] != "ok":
            raise Exception("NewsAPI error")
        
        articles = []
        for a in data["articles"]:
            if len(articles) >= 10:
                break
            title = a.get("title", "No title available")
            link = a.get("url")
            description = a.get("description", "No description available")
            newsapi_content = a.get("content", "No News content")
            
            content = newsapi_content if newsapi_content else description
            if link:
                try:
                    response = requests.get(link, timeout = 10)
                    response.raise_for_status()
                    soup = BeautifulSoup(response.content, "html.parser", from_encoding="utf-8")
                    text = soup.get_text(strip=True)[:1000]

                    # Heuristic for JS detection
                    paragraphs = soup.find_all("p")
                    total_text_length = len(text)
                    paragraph_count = len(paragraphs)
                    if total_text_length < 200 and paragraph_count < 2:
                        logger.info(f"Skipping {title}: Likely a JS-based website")
                        content = newsapi_content if newsapi_content else description
                    else:
                        content = text

                except requests.RequestException as e:
                    logger.warning(f"Failed to extract content from {link}: {e}")
                    content = newsapi_content if newsapi_content else description
            
            if not content:
                content = "No content available"
            
            articles.append({
                "title": title, 
                "content": content
            })
        
        if len(articles) < 10:
            logger.warning(f"Found only {len(articles)} articles for {company}")
        
        return articles
    
    except requests.RequestException as e:
        raise Exception(f"Failed to fetch articles from NewsAPI: {e}")

# This function summarizes the text input
def summarize_text(text):
    """
    Generates a polished summary
    """
    if not text or len(text) < 50:
        return "No content available to summarize"
    
    try:
        summary = summarizer(
            text,
            max_length=50,
            min_length=25,
            do_sample=False,
            truncation=True,
            clean_up_tokenization_spaces=True
        )[0]['summary_text']
        
        summary = summary.strip().capitalize()
        if not summary.endswith('.'):
            summary += '.'
        return summary
    except Exception as e:
        logger.error(f"Summarization failed: {e}")
        return text[:50].strip().capitalize() if text else "No content available"

# This function is used to analyze the sentiment of the text whether it's Positive, Negative or may be Neutral
def analyze_sentiment(text):
    """
    Analyze the sentiment
    """
    if not text:
        return "Neutral", 0
    try:
        result = sentiment_analyzer(text)[0]
        label = result['label']
        score = result['score']
        if label == "LABEL_0":  
            return "Negative", score
        elif label == "LABEL_1":  
            return "Neutral", score
        elif label == "LABEL_2":  
            return "Positive", score
        return "Neutral", score
    except Exception as e:
        logger.error(f"Sentiment analysis failed: {e}")
        return "Neutral", 0

# This function is used to extract keywords from all the articles
def extract_topics(text):
    """
    Extract important keywords 
    """
    if not text:
        return ["No topics found"]
    keywords = kb.extract_keywords(
        text, 
        keyphrase_ngram_range=(1, 2), 
        stop_words='english', 
        top_n=3
    )
    keywords = [k[0].replace('_', ' ').strip() for k in keywords]
    return keywords or ["No topics"]

# This function translates the text into hindi and generates text-to-speech output in mp3 format
def generate_hindi_tts(text, filename="output.mp3"):
    """
    Translates into Hindi and generates text-to-speech output
    """
    if not text:
        return None
    try:
        hindi_text = translator.translate(text)
        tts = gtts.gTTS(text=hindi_text, lang='hi', slow=False)  # Changed slow=True to False for natural speed
        tts.save(filename)
        return filename
    except Exception as e:
        logger.error(f"TTS generation failed: {e}")
        return None

# This function generates the entire report about the company
def generate_report(articles, company):
    """
    Process articles and generate a detailed report
    """
    report = {
        "Company": company,
        "Articles": []
    }
    sentiments = {"Positive": 0, "Negative": 0, "Neutral": 0}
    sentiment_scores = {"Positive": [], "Negative": [], "Neutral": []}
    all_topics = []
    article_topics = []
    
    for item in articles:
        summary = summarize_text(item["content"])
        sentiment, score = analyze_sentiment(item["content"])
        topics = extract_topics(item["content"])
        
        report["Articles"].append({
            "Title": item["title"],
            "Summary": summary,
            "Sentiment": sentiment,
            "Topics": topics
        })
        sentiments[sentiment] += 1
        sentiment_scores[sentiment].append(score)
        all_topics.extend(topics)
        article_topics.append((item["title"], topics))
    
    topic_counts = Counter(all_topics)
    topic_overlap = [topic for topic, count in topic_counts.items() if count > 1]
    
    coverage_differences = []
    for i, (title1, topics1) in enumerate(article_topics):
        for j, (title2, topics2) in enumerate(article_topics[i+1:], start=i+1):
            unique_to_article1 = set(topics1) - set(topics2)
            unique_to_article2 = set(topics2) - set(topics1)
            if unique_to_article1 or unique_to_article2:
                coverage_differences.append({
                    "Comparison": f"Article {i+1} vs Article {j+1}",
                    "Impact": (
                        f"Article {i+1} focuses on: {list(unique_to_article1) if unique_to_article1 else 'no unique topics'}, "
                        f"while Article {j+1} discusses: {list(unique_to_article2) if unique_to_article2 else 'no unique topics'}."
                    )
                })
    
    topic_overview = {
        "Topic Overlap": topic_overlap if topic_overlap else ["No overlap"],
        "Unique Topics per Article": {
            f"Article {i+1}": list(set(topics) - set(topic_overlap))
            for i, (_, topics) in enumerate(article_topics)
        }
    }
    
    report["Comparative Sentiment Score"] = {
        "Sentiment Distribution": sentiments,
        "Topic Overlap": topic_overlap if topic_overlap else ["No overlap"],
        "Coverage Differences": coverage_differences if coverage_differences else [{
            "Comparison": "Not Available", 
            "Impact": "No significant coverage difference is found"
        }],
        "Topic Overview": topic_overview
    }
    
    # Final Sentiment Analysis
    max_sentiment = max(sentiments, key=sentiments.get)
    avg_score = sum(sentiment_scores[max_sentiment]) / len(sentiment_scores[max_sentiment]) if sentiment_scores[max_sentiment] else 0
    sentiment_strength = "strong" if avg_score > 0.75 else "moderate" if avg_score > 0.5 else "weak"
    
    sentiment_explanation = (
        f"The overall sentiment towards {company} is {max_sentiment.lower()} with a {sentiment_strength} confidence "
        f"(average score: {avg_score:.2f}). "
    )
    if max_sentiment == "Positive":
        sentiment_explanation += f"This suggests favorable news coverage, likely driven by {topic_overlap[0] if topic_overlap else 'recent developments'}."
    elif max_sentiment == "Negative":
        sentiment_explanation += f"This indicates unfavorable news coverage, possibly due to {topic_overlap[0] if topic_overlap else 'recent challenges'}."
    else:
        sentiment_explanation += "This suggests a balanced view."
    
    report["Final Sentiment Analysis"] = sentiment_explanation
    
    # Audio summary
    tts_summary = (
        f"Analysis of {len(articles)} articles gives {sentiments['Positive']} positive, "
        f"{sentiments['Negative']} negative, and {sentiments['Neutral']} neutral sentiments."
    )
    report["Audio"] = generate_hindi_tts(tts_summary)
    
    return report
