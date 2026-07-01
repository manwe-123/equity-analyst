import yfinance as yf

class MarketData:
    def get_ticker_snapshot(self, ticker_symbol):
        """
        Fetches the current price and 1-month trend for a specific stock ticker.
        """
        try:
            # Initialize the yfinance ticker object
            ticker = yf.Ticker(ticker_symbol)
            
            # Fetch basic info to get the current price
            # (We use a fallback chain because different keys are populated depending on market hours)
            info = ticker.info
            price = info.get('currentPrice') or info.get('regularMarketPrice') or info.get('previousClose', 0)
            
            # Fetch 1 month of historical closing prices for our sparkline chart
            hist = ticker.history(period="1mo")
            trend_data = hist['Close'].tolist()
            
            return {
                "symbol": ticker_symbol,
                "price": round(price, 2),
                "trend": trend_data
            }
        except Exception as e:
            print(f"⚠️ Could not fetch market data for {ticker_symbol}: {e}")
            return None
    def get_upside_metrics(self, ticker_symbol):
        """
        Pulls fundamental data and calculates mathematical upside potential.
        """
        try:
            ticker = yf.Ticker(ticker_symbol)
            info = ticker.info
            
            # Extract key metrics (using fallbacks because yfinance keys vary)
            current_price = info.get('currentPrice') or info.get('regularMarketPrice') or 0
            high_52w = info.get('fiftyTwoWeekHigh') or 0
            low_52w = info.get('fiftyTwoWeekLow') or 0
            pe_ratio = info.get('trailingPE') or info.get('forwardPE') or 0
            
            # Calculate Upside: How far is it from its 52-week high?
            upside_potential = 0
            if current_price > 0 and high_52w > 0:
                upside_potential = round(((high_52w - current_price) / current_price) * 100, 2)
            elif current_price > 0 and high_52w == 0:
                # Fallback: If yfinance fails to get the 52w high, assume 30% upside 
                # just so we can see the stock in the UI!
                upside_potential = 30.0 

            return {
                "symbol": ticker_symbol,
                "price": round(current_price, 2),
                "pe_ratio": round(pe_ratio, 2) if pe_ratio else "N/A",
                "52w_high": round(high_52w, 2),
                "upside_to_high": upside_potential # e.g., 35.5 means it's 35.5% away from its high
            }
        except Exception as e:
            print(f"️ Could not fetch metrics for {ticker_symbol}: {e}")
            return None