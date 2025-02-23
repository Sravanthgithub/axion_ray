import pandas as pd
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from collections import Counter
import matplotlib.pyplot as plt
import seaborn as sns

# Download required NLTK data
nltk.download('punkt_tab')
nltk.download('vader_lexicon')
nltk.download('punkt')
nltk.download('stopwords')

def analyze_reviews(file_path):
    # Read the CSV file
    df = pd.read_csv(file_path)
    
    # Initialize the NLTK sentiment analyzer
    sia = SentimentIntensityAnalyzer()
    
    # Function to get sentiment scores
    def get_sentiment(text):
        return sia.polarity_scores(text)
    
    # Calculate sentiment scores for each review
    sentiments = df['review_text'].apply(get_sentiment)
    
    # Extract sentiment scores into separate columns
    df['compound'] = sentiments.apply(lambda x: x['compound'])
    df['positive'] = sentiments.apply(lambda x: x['pos'])
    df['negative'] = sentiments.apply(lambda x: x['neg'])
    df['neutral'] = sentiments.apply(lambda x: x['neu'])
    
    # Classify overall sentiment
    df['sentiment'] = df['compound'].apply(lambda x: 'Positive' if x > 0.05 
                                         else ('Negative' if x < -0.05 else 'Neutral'))
    
    # Get most common words (excluding stopwords)
    stop_words = set(stopwords.words('english'))
    all_words = ' '.join(df['review_text']).lower()
    word_tokens = word_tokenize(all_words)
    filtered_words = [word for word in word_tokens 
                     if word.isalnum() and word not in stop_words]
    word_freq = Counter(filtered_words).most_common(10)
    
    # Calculate average sentiment scores
    avg_scores = {
        'Average Compound Score': df['compound'].mean(),
        'Average Positive Score': df['positive'].mean(),
        'Average Negative Score': df['negative'].mean(),
        'Average Neutral Score': df['neutral'].mean()
    }
    
    # Calculate sentiment distribution
    sentiment_dist = df['sentiment'].value_counts()
    
    # Generate summary statistics
    summary = {
        'Total Reviews': len(df),
        'Average Sentiment Score': df['compound'].mean(),
        'Positive Reviews': sentiment_dist.get('Positive', 0),
        'Neutral Reviews': sentiment_dist.get('Neutral', 0),
        'Negative Reviews': sentiment_dist.get('Negative', 0),
        'Most Common Words': dict(word_freq),
        'Average Scores': avg_scores
    }
    
    return df, summary

def plot_sentiment_distribution(df):
    plt.figure(figsize=(10, 6))
    sns.histplot(data=df, x='compound', bins=20)
    plt.title('Distribution of Sentiment Scores')
    plt.xlabel('Compound Sentiment Score')
    plt.ylabel('Count')
    plt.savefig('sentiment_distribution.png')
    plt.close()

def plot_sentiment_categories(df):
    plt.figure(figsize=(8, 6))
    df['sentiment'].value_counts().plot(kind='bar')
    plt.title('Distribution of Sentiment Categories')
    plt.xlabel('Sentiment')
    plt.ylabel('Count')
    plt.savefig('sentiment_categories.png')
    plt.close()

if __name__ == "__main__":
    # Analyze reviews
    df, summary = analyze_reviews('/home/sravanth/Documents/axion_ray/reviews.csv')
    
    # Print summary
    print("\n=== Sentiment Analysis Summary ===")
    print(f"Total Reviews Analyzed: {summary['Total Reviews']}")
    print(f"Average Sentiment Score: {summary['Average Sentiment Score']:.3f}")
    print("\nSentiment Distribution:")
    print(f"Positive Reviews: {summary['Positive Reviews']}")
    print(f"Neutral Reviews: {summary['Neutral Reviews']}")
    print(f"Negative Reviews: {summary['Negative Reviews']}")
    
    print("\nAverage Scores:")
    for metric, score in summary['Average Scores'].items():
        print(f"{metric}: {score:.3f}")
    
    print("\nTop 10 Most Common Words:")
    for word, count in summary['Most Common Words'].items():
        print(f"{word}: {count}")
    
    # Generate plots
    plot_sentiment_distribution(df)
    plot_sentiment_categories(df)
    
    # Export detailed results to CSV
    df[['review_text', 'compound', 'positive', 'negative', 'neutral', 'sentiment']].to_csv(
        'sentiment_analysis_results.csv', index=False)