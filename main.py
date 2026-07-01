import fetch_news
from ai_brain import AIAnalyst

def format_articles_for_ai(articles):
    """
    Helper function to turn the list of article dictionaries 
    into a single, clean string that the AI can easily read.
    """
    formatted_text = ""
    for i, article in enumerate(articles):
        title = article.get('title', 'No Title')
        description = article.get('description', 'No description available.')
        formatted_text += f"Article {i+1}:\nTitle: {title}\nDescription: {description}\n\n"
    
    return formatted_text

def main():
    print("--- Starting Equity Analyst Pipeline ---\n")
    
    # 1. Fetch the data
    raw_data = fetch_news.fetch_tech_news()
    
    if not raw_data or raw_data.get("status") != "ok":
        print("Failed to fetch news. Aborting.")
        return

    articles = raw_data.get("articles", [])
    print(f"Successfully fetched {len(articles)} articles.\n")
    
    # 2. Format the data for the AI
    # (We only send the first 10 articles to keep the AI's context window happy and fast)
    articles_to_analyze = articles[:15] 
    text_for_ai = format_articles_for_ai(articles_to_analyze)
    
    # 3. Initialize the AI and run the analysis
    analyst = AIAnalyst()
    analysis_result = analyst.analyze_news(text_for_ai)
    
    # 4. Print the final structured result
    if analysis_result:
        print("\n--- AI ANALYSIS COMPLETE ---")
        print(f"Market Theme: {analysis_result.get('market_theme')}")
        print(f"Sentiment:    {analysis_result.get('overall_sentiment')}")
        print(f"Tickers:      {analysis_result.get('relevant_tickers')}")
        print(f"Key Takeaway: {analysis_result.get('key_takeaway')}")
        print("------------------------------\n")
    else:
        print("AI Analysis failed.")

if __name__ == "__main__":
    main()