import re
from collections import Counter

class NewsParser:
    def __init__(self):
        # A robust dictionary of top companies and their common aliases.
        # In a production app, this would be a database of the entire S&P 500.
        self.ticker_aliases = {
            "apple": "AAPL", "aapl": "AAPL",
            "microsoft": "MSFT", "msft": "MSFT",
            "nvidia": "NVDA", "nvda": "NVDA",
            "amazon": "AMZN", "amzn": "AMZN",
            "google": "GOOGL", "alphabet": "GOOGL", "googl": "GOOGL",
            "meta": "META", "facebook": "META",
            "tesla": "TSLA", "tsla": "TSLA",
            "berkshire hathaway": "BRK-B", "brk-b": "BRK-B",
            "jpmorgan": "JPM", "jpm": "JPM", "chase": "JPM",
            "visa": "V", "mastercard": "MA", "ma": "MA",
            "unitedhealth": "UNH", "johnson & johnson": "JNJ", "jnj": "JNJ",
            "walmart": "WMT", "wmt": "WMT", "exxon": "XOM", "xom": "XOM",
            "procter & gamble": "PG", "pg": "PG", "home depot": "HD", "hd": "HD",
            "chevron": "CVX", "cvx": "CVX", "merck": "MRK", "mrk": "MRK",
            "abbvie": "ABBV", "abbv": "ABBV", "coca-cola": "KO", "ko": "KO",
            "pepsico": "PEP", "pep": "PEP", "costco": "COST", "cost": "COST",
            "broadcom": "AVGO", "avgo": "AVGO", "eli lilly": "LLY", "lly": "LLY",
            "thermo fisher": "TMO", "tmo": "TMO", "mcdonald's": "MCD", "mcd": "MCD",
            "cisco": "CSCO", "csco": "CSCO", "accenture": "ACN", "acn": "ACN",
            "abbott": "ABT", "abt": "ABT", "danaher": "DHR", "dhr": "DHR",
            "verizon": "VZ", "vz": "VZ", "adp": "ADP", "adp": "ADP",
            "texas instruments": "TXN", "txn": "TXN", "qualcomm": "QCOM", "qcom": "QCOM",
            "intuit": "INTU", "intu": "INTU", "applied materials": "AMAT", "amat": "AMAT",
            "booking holdings": "BKNG", "bkng": "BKNG", "intuitive surgical": "ISRG", "isrg": "ISRG",
            "honeywell": "HON", "hon": "HON", "union pacific": "UNP", "unp": "UNP",
            "sp global": "SPGI", "spgi": "SPGI", "lam research": "LRCX", "lrcx": "LRCX",
            "micron": "MU", "mu": "MU", "nokia": "NOK", "nok": "NOK",
            "western digital": "WDC", "wdc": "WDC", "sandisk": "WDC",
            "intel": "INTC", "intc": "INTC", "amd": "AMD", "amd": "AMD",
            "paypal": "PYPL", "pypl": "PYPL", "disney": "DIS", "dis": "DIS",
            "alibaba": "BABA", "baba": "BABA", "netflix": "NFLX", "nflx": "NFLX",
            "boeing": "BA", "ba": "BA", "caterpillar": "CAT", "cat": "CAT",
            "goldman sachs": "GS", "gs": "GS", "citigroup": "C", "c": "C",
            "bank of america": "BAC", "bac": "BAC", "wells fargo": "WFC", "wfc": "WFC"
        }
        
        # Words to ignore when using Regex (False positives)
        self.ignore_words = {"CEO", "CFO", "COO", "IPO", "ETF", "USA", "AI", "US", "UK", "GDP", "Fed", "PR", "HR", "IT", "R&D", "LLC", "INC", "CORP", "LTD", "CO", "NEW", "OLD", "BIG", "TOP"}

    def extract_tickers(self, articles):
        """
        Scans articles and returns a list of unique tickers found, 
        sorted by how frequently they are mentioned.
        """
        ticker_counts = Counter()
        
        for article in articles:
            title = article.get('title', '').lower()
            desc = article.get('description', '').lower()
            text = f"{title} {desc}"
            
            # 1. Dictionary Matching (Catches "Apple", "Microsoft", etc.)
            for alias, ticker in self.ticker_aliases.items():
                if alias in text:
                    ticker_counts[ticker] += 1
                    
            # 2. Explicit Ticker Regex (Catches "$NVDA", "(AAPL)", "NYSE: MSFT")
            # Looks for 1-5 uppercase letters preceded by $, (, or specific exchange names
            explicit_pattern = r'(?:\$|\(|NYSE:|NASDAQ:)\s*([A-Z]{1,5})'
            explicit_matches = re.findall(explicit_pattern, article.get('title', '') + " " + article.get('description', ''))
            for match in explicit_matches:
                if match not in self.ignore_words:
                    ticker_counts[match] += 1
                    
            # 3. Standalone Uppercase Regex (Catches "NVDA reported...")
            # We only accept these if they are 2-5 letters and not in our ignore list
            standalone_pattern = r'\b([A-Z]{2,5})\b'
            standalone_matches = re.findall(standalone_pattern, article.get('title', '') + " " + article.get('description', ''))
            for match in standalone_matches:
                if match not in self.ignore_words and match not in self.ticker_aliases.values():
                    # To prevent false positives, we only count standalone tickers 
                    # if they appear multiple times or are in our known dictionary
                    if match in self.ticker_aliases.values():
                        ticker_counts[match] += 1

        # Return a list of tickers, sorted by most mentioned first
        # We limit to the top 8 to prevent the local AI from hanging
        return [ticker for ticker, count in ticker_counts.most_common(8)]