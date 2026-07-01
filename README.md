# 📈 Hybrid Quant Equity Analyst

An institutional-grade, AI-driven financial research terminal. This application combines deterministic quantitative analysis, SEC legal fact-checking, and LLM synthesis to generate actionable stock insights.

## 🚀 Features
- **Dynamic Discovery Engine:** Parses thousands of news articles to dynamically identify trending tickers.
- **Hybrid Pipeline:** Combines `yfinance` technicals/fundamentals with AI news sentiment.
- **SEC Fact-Checking:** Scrapes official 10-Q/10-K filings from the SEC EDGAR database to extract legal risk factors.
- **Confidence Synthesis:** An LLM acts as an Investment Committee to cross-reference Quant, News, and Legal data into a final Conviction Score.

## 🛠️ Tech Stack
- **Frontend:** Streamlit
- **Data Sources:** NewsAPI, Yahoo Finance (`yfinance`), SEC EDGAR API
- **AI/LLM:** Ollama (Llama 3.1) running locally
- **Analysis:** `ta` (Technical Analysis), `BeautifulSoup4` (Web Scraping)

## ⚙️ Setup & Installation

1. Clone the repository:
   ```bash
   git clone [YOUR_REPO_URL]
   cd equity-analyst