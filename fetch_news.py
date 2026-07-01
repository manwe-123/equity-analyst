import os
import requests
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("NEWS_API_KEY")

def fetch_news_by_sector(sector="technology"):
    """
    Fetches a broad range of news using the 'everything' endpoint.
    """
    url = "https://newsapi.org/v2/everything"
    
    # Map our sectors to robust search queries to ensure we get relevant, broad data
    query_map = {
        "technology": "technology OR tech OR software OR hardware OR AI OR semiconductor",
        "business": "business OR finance OR markets OR economy OR stocks",
        "health": "healthcare OR biotech OR pharma OR medical OR health",
        "science": "science OR research OR discovery OR space OR energy",
        "general": "world news OR markets OR economy"
    }
    
    params = {
        "q": query_map.get(sector, sector),
        "sortBy": "publishedAt", # Get the absolute newest articles
        "language": "en",
        "apiKey": api_key
    }
    
    print(f"Fetching broad {sector} news from API...")
    
    try:
        response = requests.get(url, params=params, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            # The 'everything' endpoint returns 'totalResults'. Let's print it to see the volume!
            print(f"✅ Found {data.get('totalResults', 0)} total articles. Now processing...")
            return data
        else:
            print(f" API FAILED with status code {response.status_code}")
            print(f"👇 RAW API ERROR MESSAGE BELOW 👇")
            print(response.text) 
            print(f"👆 END OF ERROR MESSAGE 👆")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f" NETWORK ERROR: {e}")
        return None