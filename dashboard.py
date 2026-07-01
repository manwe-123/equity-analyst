from news_parser import NewsParser
from quant_engine import QuantEngine
from sec_scraper import SECScraper
import streamlit as st
import pandas as pd
from collections import Counter
import fetch_news
from ai_brain import AIAnalyst
from market_data import MarketData
from data_manager import DataManager
from hardware_bridge import ArduinoBridge

# 1. Page Configuration
st.set_page_config(page_title="Hybrid Quant Analyst", layout="wide", page_icon="📈")

def main():
    # ==========================================
    # SIDEBAR: Controls
    # ==========================================
    with st.sidebar:
        st.title("⚙️ Control Panel")
        st.markdown("Configure your market analysis parameters.")
        st.divider()

        sector_map = {
            "Technology": "technology",
            "Business": "business",
            "Healthcare": "health",
            "Science": "science",
            "General Market": "general"
        }
        
        selected_pretty_sector = st.selectbox(
            "Target Sector", 
            options=list(sector_map.keys()),
            index=0
        )
        api_sector = sector_map[selected_pretty_sector]
        
        st.divider()
        st.subheader(" Search & Discovery")
        
        # 1. Targeted Search
        search_ticker = st.text_input("Analyze Specific Ticker", placeholder="e.g., TSLA, AAPL").upper()
        
        # 2. Auto-Discovery Toggle
        auto_discover = st.checkbox("Auto-Discover Top 5 Tickers from News", value=True)
        
        st.divider()
        run_button = st.button(f"🚀 Run Hybrid Analysis", type="primary", use_container_width=True)
        
        st.divider()
        st.caption("Powered by Local LLM (Llama 3.1) & yfinance")

    # ==========================================
    # MAIN CANVAS: The Dashboard
    # ==========================================
    st.title(f" {selected_pretty_sector} Hybrid Quant Analyst")
    st.markdown("Mathematical upside screening combined with AI news catalyst analysis.")
    st.divider()

    if run_button:
        # 1. Fetch Data
        with st.spinner(f"Fetching latest {selected_pretty_sector} news..."):
            raw_data = fetch_news.fetch_news_by_sector(sector=api_sector)
            
        if raw_data and raw_data.get("status") == "ok":
            # CRITICAL FIX: Define articles RIGHT HERE, before the loop!
            articles = raw_data.get("articles", [])[:30] 
            st.session_state['raw_articles'] = articles
            
            # 2. DYNAMIC DISCOVERY: Parse the news to find relevant companies
            print(f"🔍 [Discovery Engine] Scanning {len(articles)} articles for company mentions...")
            news_parser = NewsParser()
            watchlist = news_parser.extract_tickers(articles)
            
            if not watchlist:
                st.warning("No specific companies were found in today's news. Falling back to default watchlist.")
                watchlist = ["AAPL", "MSFT", "NVDA", "AMZN", "GOOGL", "META", "TSLA", "JPM"]
                
            print(f"🎯 [Discovery Engine] Found {len(watchlist)} relevant tickers: {watchlist}")
            
            # 3. Initialize the progress bar explicitly
            progress_bar = st.progress(0, text="Initializing engines...")
            
            quant_engine = QuantEngine()
            sec_scraper = SECScraper()
            analyst = AIAnalyst()
            
            stock_data = []
            total_stocks = len(watchlist)
            
            # 4. The Synthesis Loop
            for i, ticker in enumerate(watchlist):
                progress_bar.progress((i + 1) / total_stocks, text=f"Analyzing {ticker}...")
                
                # A. Get Quant Data
                metrics = quant_engine.get_deep_analysis(ticker)
                if not metrics:
                    continue
                    
                # B. Filter News
                relevant_articles = []
                for article in articles:
                    title = (article.get('title') or '').upper()
                    desc = (article.get('description') or '').upper()
                    if ticker in title or ticker in desc:
                        relevant_articles.append(article)
                
                # C. Get News Brief
                brief_text = "No recent news found."
                if relevant_articles:
                    brief_text = "\n".join([f"- {art.get('title')}" for art in relevant_articles[:3]])
                    brief_text = analyst.generate_quick_brief(ticker, brief_text)
                    
                # D. Get SEC Risk Factors
                sec_risks = sec_scraper.get_risk_factors(ticker)
                
                # E. Generate Confidence Score (The Synthesis)
                confidence_data = analyst.generate_confidence_score(ticker, metrics, sec_risks, brief_text)
                
                stock_data.append({
                    "metrics": metrics,
                    "brief": brief_text,
                    "sec_risks": sec_risks,
                    "confidence": confidence_data,
                    "article_count": len(relevant_articles)
                })

            # 5. Sort by Confidence Score (Highest first)
            stock_data.sort(key=lambda x: x['confidence'].get('confidence_score', 0), reverse=True)
            st.session_state['stock_data'] = stock_data
            st.toast("Synthesis Complete!", icon="🏆")
        else:
            st.error("Failed to fetch news. Check terminal for API errors.")

    # 2. Render the UI (If we have data)
    if 'stock_data' in st.session_state and st.session_state['stock_data']:
        stock_data = st.session_state['stock_data']
        articles = st.session_state.get('raw_articles', [])

        tab1, tab2 = st.tabs(["🚀 High Upside Screener", "📰 Raw News Feed"])

        with tab1:
            st.subheader("🚀 High Upside / Turnaround Screener")
            st.markdown("Stocks mathematically far from their 52-week highs, filtered for recent news catalysts.")
            
            for stock in stock_data:
                m = stock['metrics']
                conf = stock['confidence']
                
                # Determine UI colors based on verdict
                verdict = conf.get('verdict', 'Hold')
                if 'Strong Buy' in verdict: color = "🟢"
                elif 'Buy' in verdict: color = "🟢"
                elif 'Sell' in verdict: color = ""
                else: color = "⚪️"
                    
                with st.container(border=True):
                    # Header Row
                    col_header1, col_header2 = st.columns([3, 1])
                    with col_header1:
                        st.markdown(f"### {color} ${m['symbol']} - {verdict}")
                    with col_header2:
                        score = conf.get('confidence_score', 0)
                        st.metric("Confidence", f"{score}/100")
                        
                    st.divider()
                    
                    # Top Line Catalyst & Risk
                    col_catalyst, col_risk = st.columns(2)
                    with col_catalyst:
                        st.markdown(f"**🚀 Primary Catalyst:** {conf.get('primary_catalyst', 'N/A')}")
                    with col_risk:
                        st.markdown(f"**⚠️ Dealbreaker Risk:** {conf.get('dealbreaker_risk', 'None')}")
                        
                    st.divider()
                    
                    # THE DEEP DIVE EXPANDER
                    with st.expander(" View Advanced Technical & Fundamental Analysis"):
                        
                        # 3-Column Grid for Core Data
                        col_quant, col_fund, col_tech = st.columns(3)
                        
                        with col_quant:
                            st.markdown("**📊 Valuation**")
                            st.caption(f"Price: ${m['current_price']}")
                            st.caption(f"P/E Ratio: {m['pe_ratio']}")
                            st.caption(f"PEG Ratio: {m['peg_ratio']}")
                            st.caption(f"Debt/Equity: {m['debt_to_equity']}")
                            
                        with col_fund:
                            st.markdown("** Fundamentals**")
                            st.caption(f"Free Cash Flow: {m['fcf']}")
                            st.caption(f"Return on Equity: {m['roe']}")
                            st.caption(f"Revenue Growth: {m['revenue_growth']}")
                            st.caption(f"SEC Risk: {stock['sec_risks'][:100]}...")
                            
                        with col_tech:
                            st.markdown("**📈 Technicals**")
                            st.caption(f"Trend (50/200 SMA): {m['trend']}")
                            st.caption(f"RSI (14): {m['rsi_14']}")
                            st.caption(f"MACD Histogram: {m['macd_histogram']}")
                            st.caption(f"Bollinger Width: {m['bb_width']}%")

        with tab2:
            st.subheader("Source Material")
            st.caption(f"The top {len(articles)} raw articles fed into the pipeline.")
            for i, article in enumerate(articles):
                with st.container(border=True):
                    st.markdown(f"**{i+1}. [{article.get('source', {}).get('name', 'Unknown')}] {article.get('title')}**")
                    st.caption(article.get('description', 'No description.'))
                    if article.get('url'):
                        st.markdown(f"[Read full article ↗]({article.get('url')})")

    else:
        st.info("👈 Select a sector in the sidebar and click **Run Hybrid Analysis** to begin.")

if __name__ == "__main__":
    main()