from flask import Flask, request, jsonify
import pandas as pd
import requests

app = Flask(__name__)

# Groq API Base URL and Authorization
GROQ_API_URL = "https://api.groq.com/v1/sentiment"
GROQ_API_KEY = "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"  # Replace with your actual API key

def call_groq_api(review_text):
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {"text": review_text}
    
    try:
        response = requests.post(GROQ_API_URL, json=data, headers=headers)
        response.raise_for_status()
        result = response.json()
        return result.get("sentiment", {})
    except requests.exceptions.RequestException as e:
        print(f"Error calling Groq API: {e}")
        return None

def analyze_sentiments(reviews):
    sentiments = {"positive": 0, "negative": 0, "neutral": 0}
    total_reviews = len(reviews)
    
    for review in reviews:
        sentiment_result = call_groq_api(review)
        
        if sentiment_result:
            sentiments["positive"] += sentiment_result.get("positive", 0)
            sentiments["negative"] += sentiment_result.get("negative", 0)
            sentiments["neutral"] += sentiment_result.get("neutral", 0)

    # Average the scores
    sentiments = {key: round(value / total_reviews, 2) for key, value in sentiments.items()}
    return sentiments

def process_file(file):
    if file.filename.endswith('.csv'):
        df = pd.read_csv(file)
    elif file.filename.endswith('.xlsx'):
        df = pd.read_excel(file)
    else:
        return None, "Invalid file format. Only CSV and XLSX are supported."

    if 'review' not in df.columns:
        return None, "Input file must contain a 'review' column."

    reviews = df['review'].dropna().tolist()
    return reviews, None

@app.route('/analyze', methods=['POST'])
def analyze():
    if 'file' not in request.files:
        return jsonify({"error": "No file provided"}), 400
    
    file = request.files['file']
    reviews, error = process_file(file)
    
    if error:
        return jsonify({"error": error}), 400
    
    sentiments = analyze_sentiments(reviews)
    return jsonify(sentiments)

# Exporting the Vercel handler
def handler(event, context):
    from flask import Flask, Response
    return app(environ=event, start_response=context)
