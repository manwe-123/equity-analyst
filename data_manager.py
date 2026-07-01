import pandas as pd
from datetime import datetime
import os

class DataManager:
    def __init__(self, filename="market_history.csv"):
        """
        Initialize the Data Manager with a filename.
        """
        self.filepath = filename

    def save_daily_analysis(self, analysis_data, sector="general"):
        """
        Takes the AI analysis dictionary and appends it as a new row to our CSV history.
        """
        # 1. Get today's date
        today = datetime.now().strftime("%Y-%m-%d")
        
        # 2. Extract data from the AI's JSON response
        raw_sentiment = analysis_data.get('overall_sentiment', 'Neutral')
        if 'Bullish' in raw_sentiment:
            sentiment = 'Bullish'
        elif 'Bearish' in raw_sentiment:
            sentiment = 'Bearish'
        else:
            sentiment = 'Neutral'        
        theme = analysis_data.get('market_theme', 'No theme')
        tickers_list = analysis_data.get('relevant_tickers', [])
        tickers_string = ", ".join(tickers_list) if tickers_list else "None"
        takeaway = analysis_data.get('key_takeaway', 'No takeaway')
        # 3. Create a new row of data
        new_row = {
            "date": today,
            "sector": sector.upper(),
            "sentiment": sentiment, # <-- ADDED THIS BACK IN!
            "dominant_theme": theme,
            "relevant_tickers": tickers_string,
            "key_takeaway": takeaway
        }

        # 4. Save to CSV
        file_exists = os.path.isfile(self.filepath)
        
        df = pd.DataFrame([new_row])
        df.to_csv(self.filepath, mode='a', header=not file_exists, index=False)
        
        # Notice how this print statement is indented exactly 8 spaces? 
        # That puts it inside the method, so 'self' is perfectly valid!
        print(f"✅ Data successfully saved to {self.filepath}")

    def get_history(self):
        """
        Reads the CSV file and returns it as a Pandas DataFrame.
        If the file doesn't exist yet, returns an empty DataFrame.
        """
        if os.path.isfile(self.filepath):
            return pd.read_csv(self.filepath)
        else:
            return pd.DataFrame() 